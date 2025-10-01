"""Utilities for summarizing architecture logic documents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Protocol, Sequence, Tuple
import re

DEFAULT_SUMMARY_MODEL = "qwen3:8b"
_DEFAULT_SYSTEM_PROMPT = (
    "You summarize internal architecture documentation. "
    "Capture responsibilities, data flows, and integration notes for each section. "
    "Return 2-3 bullet points per section, using concise language and avoiding repetition."
)


class ChatClient(Protocol):
    """Protocol describing the subset of Ollama-style chat client we require."""

    def chat(
        self,
        model: str,
        messages: Sequence[dict],
        images: Optional[Sequence[str]] = None,
    ) -> Tuple[bool, str, str]:
        ...


@dataclass
class Segment:
    """Represents a logical section within a document."""

    title: str
    start_line: int
    end_line: int
    content: str

    @property
    def span_label(self) -> str:
        if self.start_line == self.end_line:
            return f"Line {self.start_line}"
        return f"Lines {self.start_line}-{self.end_line}"


@dataclass
class SegmentSummary:
    """Holds the LLM-generated summary (or an error) for a segment."""

    segment: Segment
    summary: str
    error: Optional[str] = None


_IGNORED_TOKENS = {"GitHub", "Copy"}
_slug_pattern = re.compile(r"[^a-z0-9]+")


def _looks_like_heading(lines: List[str], index: int, stripped: str) -> bool:
    if not stripped:
        return False
    if stripped in _IGNORED_TOKENS:
        return False
    if stripped.startswith(('#', '*', '-', '>')):
        return stripped.startswith('#')
    prev_blank = index == 0 or not lines[index - 1].strip()
    next_blank = index == len(lines) - 1 or not lines[index + 1].strip()
    if not (prev_blank and next_blank):
        return False
    if ':' in stripped and not stripped.endswith(':'):
        return False
    if any(ch in stripped for ch in '.?!;') and not stripped.endswith(':'):
        return False
    return True


def parse_segments(text: str, *, fallback_title: str = "Document") -> List[Segment]:
    """Split *text* into logical segments using simple heading heuristics."""

    lines = text.splitlines()
    headings: List[Tuple[int, str]] = []
    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped.startswith('#'):
            title = stripped.lstrip('#').strip() or fallback_title
            headings.append((idx, title))
            continue
        if _looks_like_heading(lines, idx, stripped):
            title = stripped.rstrip(':').strip()
            headings.append((idx, title or fallback_title))
    segments: List[Segment] = []
    if not headings:
        end_line = len(lines) or 1
        segments.append(
            Segment(
                title=fallback_title,
                start_line=1,
                end_line=end_line,
                content=text.strip(),
            )
        )
        return segments
    for pos, (line_no, title) in enumerate(headings):
        body_start = line_no + 1
        body_end = headings[pos + 1][0] if pos + 1 < len(headings) else len(lines)
        if body_end < body_start:
            body_end = body_start
        content = "\n".join(lines[body_start:body_end]).strip()
        segments.append(
            Segment(
                title=title,
                start_line=line_no + 1,
                end_line=body_end if body_end > body_start else line_no + 1,
                content=content,
            )
        )
    return segments


def load_segments(path: Path) -> List[Segment]:
    """Load the file at *path* and return detected segments."""

    data = path.read_text(encoding="utf-8")
    return parse_segments(data, fallback_title=path.name)


def _build_messages(segment: Segment, instructions: Optional[str]) -> List[dict]:
    user_prompt = (
        f"Summarize the following section from the Codex architecture reference.\n"
        f"Section: {segment.title}\n"
        f"Location: {segment.span_label}\n\n"
        f"{segment.content.strip()}"
    ).strip()
    system_prompt = instructions or _DEFAULT_SYSTEM_PROMPT
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def summarize_segments(
    segments: Iterable[Segment],
    *,
    client: Optional[ChatClient],
    model: str = DEFAULT_SUMMARY_MODEL,
    instructions: Optional[str] = None,
) -> List[SegmentSummary]:
    """Call *client* to summarize each segment and return structured results."""

    results: List[SegmentSummary] = []
    for segment in segments:
        if client is None:
            results.append(
                SegmentSummary(
                    segment=segment,
                    summary="",
                    error="LLM client unavailable",
                )
            )
            continue
        try:
            messages = _build_messages(segment, instructions)
            ok, content, err = client.chat(model, messages)
        except Exception as exc:  # pragma: no cover - defensive
            results.append(
                SegmentSummary(segment=segment, summary="", error=str(exc))
            )
            continue
        if not ok:
            results.append(
                SegmentSummary(segment=segment, summary="", error=err or "unknown error")
            )
        else:
            results.append(
                SegmentSummary(segment=segment, summary=content.strip(), error=None)
            )
    return results


def _slugify(title: str) -> str:
    slug = _slug_pattern.sub('-', title.lower()).strip('-')
    return slug or "section"


def segment_anchor(segment: Segment, source: Optional[Path]) -> str:
    """Return a markdown-friendly anchor for *segment*."""

    if source is not None:
        return f"editor://{source.name}?line={segment.start_line}"
    return f"#{_slugify(segment.title)}"


def build_summary_markdown(
    summaries: Sequence[SegmentSummary],
    *,
    source: Optional[Path] = None,
) -> str:
    """Render a markdown report for the supplied segment *summaries*."""

    timestamp = datetime.now(timezone.utc).isoformat()
    header = [
        "# Logic Document Review",
        "",
        f"- Source: {source.as_posix() if source else 'unsaved buffer'}",
        f"- Generated: {timestamp}",
        "",
    ]
    toc = ["## Table of Contents"]
    for summary in summaries:
        suffix = " (error)" if summary.error else ""
        toc.append(
            f"- [{summary.segment.title}{suffix}]({segment_anchor(summary.segment, source)})"
        )
    toc.append("")
    body: List[str] = []
    for summary in summaries:
        body.append(f"## {summary.segment.title}")
        body.append(f"*{summary.segment.span_label}*")
        if summary.error:
            body.append(f"> ❌ Summary failed: {summary.error}")
        else:
            text = summary.summary.strip()
            body.append(text or "_No summary produced._")
        body.append("")
    return "\n".join(header + toc + body).rstrip() + "\n"


def write_report(source: Optional[Path], content: str) -> Optional[Path]:
    """Persist *content* alongside *source* and return the report path."""

    if source is None:
        return None
    base = source.stem or source.name
    target = source.with_name(f"{base}.logic-summary.md")
    target.write_text(content, encoding="utf-8")
    return target
