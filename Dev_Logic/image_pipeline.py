"""Image processing helpers for Codex-Local.

This module keeps the OCR + vision summarisation logic reusable so that
both the terminal chat and future editor chat panes can import the same
helpers.  The functions are intentionally defensive because local OCR
and VLM pipelines may be unavailable on some machines.
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

try:  # Optional dependency – we can still provide structured errors.
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - exercised via error path tests
    Image = None  # type: ignore

try:  # Optional dependency – pytesseract may not be installed yet.
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover - exercised via error path tests
    pytesseract = None  # type: ignore


class VisionClient(Protocol):
    """Minimal protocol for Ollama-like chat clients."""

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        images: Optional[List[str]] = None,
    ) -> tuple[bool, str, str]:
        ...


@dataclass
class OCRResult:
    """Structured result returned by :func:`perform_ocr`."""

    text: str
    markdown: str
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class VisionResult:
    """Structured result returned by :func:`analyze_image`."""

    summary: str
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class ThumbnailUpdate:
    """Record describing a thumbnail replacement inside a Markdown log."""

    original_path: Path
    thumbnail_path: Path
    markdown_original: str
    markdown_thumbnail: str


_MARKDOWN_IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")


def _normalise_markdown(text: str) -> str:
    """Collapse whitespace and return Markdown-friendly text."""

    lines = [ln.rstrip() for ln in text.splitlines()]
    cleaned: list[str] = []
    blank = False
    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            if not blank and cleaned:
                cleaned.append("")
            blank = True
            continue
        blank = False
        cleaned.append(stripped)
    return "\n".join(cleaned).strip()


def _ensure_image(path: Path) -> Optional[Path]:
    if path.exists():
        return path
    return None


def _thumbnail_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}_thumb.png")


def _resolve_markdown_path(base: Path, ref: str) -> Path:
    ref_path = Path(ref.strip())
    if ref_path.is_absolute():
        return ref_path
    return (base.parent / ref_path).resolve(strict=False)


def _markdown_path(base: Path, path: Path) -> str:
    resolved = path.resolve(strict=False)
    try:
        rel = resolved.relative_to(base.parent)
        return rel.as_posix()
    except ValueError:
        return resolved.as_posix()


def generate_thumbnail(
    image_path: Path | str,
    *,
    max_size: tuple[int, int] = (160, 160),
) -> Optional[Path]:
    """Create or reuse a ``*_thumb.png`` for ``image_path``."""

    path = _ensure_image(Path(image_path))
    if path is None:
        return None

    thumb_path = _thumbnail_path(path)

    if Image is None:
        if thumb_path.exists():
            return thumb_path
        return None

    try:
        thumb_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:  # pragma: no cover - filesystem permissions
        return None

    try:
        src_mtime = path.stat().st_mtime
        if thumb_path.exists() and thumb_path.stat().st_mtime >= src_mtime:
            return thumb_path
    except Exception:  # pragma: no cover - unable to stat reliably
        pass

    try:
        with Image.open(path) as im:
            img = im.convert("RGBA")
            if hasattr(Image, "Resampling"):
                resample = Image.Resampling.LANCZOS
            else:  # pragma: no cover - Pillow < 9
                resample = Image.LANCZOS  # type: ignore[attr-defined]
            img.thumbnail(max_size, resample=resample)
            img.save(thumb_path, format="PNG", optimize=True)
    except Exception:  # pragma: no cover - corrupted image path
        return None

    return thumb_path


def _replace_markdown_paths(text: str, old: str, new: str) -> tuple[str, bool]:
    replaced = False

    def _sub(match: re.Match[str]) -> str:
        nonlocal replaced
        current = match.group("path").strip()
        if current == old:
            replaced = True
            alt = match.group("alt")
            return f"![{alt}]({new})"
        return match.group(0)

    return _MARKDOWN_IMAGE_RE.sub(_sub, text), replaced


def thumbnailize_conversation_markdown(
    conversation_path: Path | str,
    *,
    keep_recent: int = 10,
    max_size: tuple[int, int] = (160, 160),
) -> List[ThumbnailUpdate]:
    """Replace older Markdown image links with thumbnail variants."""

    conv_path = Path(conversation_path)
    if not conv_path.exists():
        return []

    try:
        text = conv_path.read_text(encoding="utf-8")
    except Exception:  # pragma: no cover - encoding error paths
        return []

    matches = list(_MARKDOWN_IMAGE_RE.finditer(text))
    if keep_recent < 0:
        keep_recent = 0
    cutoff = max(0, len(matches) - keep_recent)

    updates: List[ThumbnailUpdate] = []
    new_text_parts: List[str] = []
    last_end = 0

    for idx, match in enumerate(matches):
        new_text_parts.append(text[last_end : match.start()])
        alt = match.group("alt")
        original_ref = match.group("path").strip()
        replacement_ref = original_ref

        if idx < cutoff and not original_ref.endswith("_thumb.png"):
            resolved = _resolve_markdown_path(conv_path, original_ref)
            thumb_path = generate_thumbnail(resolved, max_size=max_size)
            if thumb_path is not None and thumb_path.exists():
                thumb_ref = _markdown_path(conv_path, thumb_path)
                orig_ref_norm = _markdown_path(conv_path, resolved)
                if thumb_ref != original_ref:
                    replacement_ref = thumb_ref
                    updates.append(
                        ThumbnailUpdate(
                            original_path=resolved,
                            thumbnail_path=thumb_path,
                            markdown_original=orig_ref_norm,
                            markdown_thumbnail=thumb_ref,
                        )
                    )

        new_text_parts.append(f"![{alt}]({replacement_ref})")
        last_end = match.end()

    new_text_parts.append(text[last_end:])
    new_text = "".join(new_text_parts)

    if new_text != text:
        conv_path.write_text(new_text, encoding="utf-8")

    return updates


def restore_conversation_image(
    conversation_path: Path | str,
    image_path: Path | str,
) -> bool:
    """Restore the original Markdown link for ``image_path`` if thumbnailed."""

    conv_path = Path(conversation_path)
    if not conv_path.exists():
        return False

    resolved = _resolve_markdown_path(conv_path, str(image_path))
    original_ref = _markdown_path(conv_path, resolved)
    thumb_ref = _markdown_path(conv_path, _thumbnail_path(resolved))

    try:
        text = conv_path.read_text(encoding="utf-8")
    except Exception:  # pragma: no cover - encoding error
        return False

    updated_text, changed = _replace_markdown_paths(text, thumb_ref, original_ref)
    if changed:
        conv_path.write_text(updated_text, encoding="utf-8")
    return changed


def perform_ocr(
    image_path: Path | str,
    *,
    engine: Optional[Any] = None,
    language: str = "eng",
) -> OCRResult:
    """Run OCR over ``image_path`` returning Markdown text or an error.

    Parameters
    ----------
    image_path:
        Location of the image to process.
    engine:
        Optional pytesseract-like module.  When omitted the function will
        use the globally imported :mod:`pytesseract` instance.
    language:
        Language hint forwarded to the OCR engine.
    """

    path = _ensure_image(Path(image_path))
    if path is None:
        return OCRResult("", "", error="Image not found")

    if Image is None:
        return OCRResult("", "", error="Pillow not installed")

    ocr_engine = engine or pytesseract
    if ocr_engine is None:
        return OCRResult("", "", error="pytesseract not installed")

    try:
        with Image.open(path) as im:
            img = im.convert("L")  # greyscale improves OCR quality
            text = ocr_engine.image_to_string(img, lang=language)
    except Exception as exc:  # pragma: no cover - hard to force reliably
        return OCRResult("", "", error=str(exc))

    text = text.strip()
    if not text:
        return OCRResult("", "", error="No text detected")

    markdown = _normalise_markdown(text)
    return OCRResult(text=text, markdown=markdown)


def _encode_png_base64(path: Path) -> Optional[str]:
    if Image is None:
        try:
            data = path.read_bytes()
        except Exception:  # pragma: no cover - filesystem error path
            return None
        return base64.b64encode(data).decode("ascii")

    try:
        with Image.open(path) as im:
            buf = io.BytesIO()
            im.convert("RGBA").save(buf, format="PNG", optimize=True)
            return base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:  # pragma: no cover - corrupted image path
        try:
            data = path.read_bytes()
        except Exception:
            return None
        return base64.b64encode(data).decode("ascii")


def analyze_image(
    image_path: Path | str,
    ocr_text: str,
    *,
    client: Optional[VisionClient],
    model: str,
    user_text: str = "",
) -> VisionResult:
    """Ask a vision-language model to describe ``image_path``.

    The ``ocr_text`` extracted via :func:`perform_ocr` is supplied to the
    model as grounding context.
    """

    path = _ensure_image(Path(image_path))
    if path is None:
        return VisionResult("", error="Image not found")

    if client is None:
        return VisionResult("", error="No vision client configured")

    b64 = _encode_png_base64(path)
    if not b64:
        return VisionResult("", error="Unable to encode image")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a meticulous vision assistant. Use the provided OCR "
                "Markdown as factual ground truth and summarise UI elements, "
                "notable numbers, and potential actions succinctly."
            ),
        },
        {
            "role": "user",
            "content": (
                f"User request: {user_text or '(none)'}\n\nOCR Markdown:\n{ocr_text or '(empty)'}"
            ),
        },
    ]

    ok, summary, err = client.chat(model=model, messages=messages, images=[b64])
    if not ok:
        return VisionResult("", error=err or "Vision model error")

    summary = summary.strip()
    if not summary:
        return VisionResult("", error="Vision model returned no text")

    return VisionResult(summary=summary)


__all__ = [
    "OCRResult",
    "VisionResult",
    "perform_ocr",
    "analyze_image",
    "ThumbnailUpdate",
    "generate_thumbnail",
    "thumbnailize_conversation_markdown",
    "restore_conversation_image",
]
