#!/usr/bin/env python3
"""User Guided Notes card for Codex Virtual Desktop.

This module provides a high-level implementation of the User Guided Notes
card described in the specification that accompanies the Virtual Desktop.
It focuses on providing a structured, high-contrast interface for capturing
conversations, evidence, and exports while remaining self-contained so it
can run even when optional subsystems (Ollama, OCR, etc.) are unavailable.

The implementation intentionally leans on defensive fallbacks so the widget
can be instantiated both as an embedded Virtual Desktop card and as a
standalone window.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:  # Optional dependency for HTTP interactions with Ollama/OpenAI
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional
    requests = None  # type: ignore

from PySide6.QtCore import (
    QEvent,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTimer,
    Signal,
    QSignalBlocker,
    QUrl,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QDesktopServices,
    QGuiApplication,
    QIcon,
    QImage,
    QKeySequence,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from image_pipeline import perform_ocr, analyze_image, generate_thumbnail, OCRResult

# --------------------------------------------------------------------------------------
# Storage helpers
# --------------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent / "User_Guided_Notes"
SETTINGS_PATH = BASE_DIR / "settings.json"
PROMPTS_PATH = BASE_DIR / "prompts" / "index.json"
NOTES_ROOT = BASE_DIR / "notes"
DEFAULT_PROVIDER = "Ollama"
DEFAULT_MODEL = "qwen:latest"
DEFAULT_EMBED_MODEL = "nomic-embed-text"
DATASET_TOP_K = 5

DEFAULT_PANE_VISIBILITY: Dict[str, bool] = {
    "evidence": True,
    "conversation": True,
    "summary": True,
    "dataset": True,
    "attachments": True,
}

DEFAULT_THEME = "dark"
DEFAULT_FONT_POINT_ADJUST = 0.0
COMPACT_FONT_POINT_ADJUST = -2.0


@dataclass(frozen=True)
class ThemePalette:
    name: str
    window_bg: str
    window_fg: str
    border: str
    panel_bg: str
    panel_fg: str
    secondary_bg: str
    secondary_fg: str
    input_bg: str
    input_fg: str
    accent: str
    accent_hover: str
    accent_fg: str
    muted_bg: str
    muted_fg: str
    status_fg: str
    traffic_red: str
    traffic_yellow: str
    traffic_green: str


THEME_PALETTES: Dict[str, ThemePalette] = {
    "dark": ThemePalette(
        name="dark",
        window_bg="#010409",
        window_fg="#f6f8fa",
        border="#1e2a44",
        panel_bg="#050b15",
        panel_fg="#e8f1ff",
        secondary_bg="#0c111f",
        secondary_fg="#f0f6ff",
        input_bg="#0c111f",
        input_fg="#f0f6ff",
        accent="#1f6feb",
        accent_hover="#388bfd",
        accent_fg="#ffffff",
        muted_bg="#030712",
        muted_fg="#9ba7bd",
        status_fg="#9ba7bd",
        traffic_red="#ff5f57",
        traffic_yellow="#febb2e",
        traffic_green="#2ac840",
    ),
    "light": ThemePalette(
        name="light",
        window_bg="#f5f5f7",
        window_fg="#1f1f24",
        border="#d0d4da",
        panel_bg="#ffffff",
        panel_fg="#1f2933",
        secondary_bg="#eef1f7",
        secondary_fg="#273449",
        input_bg="#ffffff",
        input_fg="#1f2933",
        accent="#3478f6",
        accent_hover="#1d6ce5",
        accent_fg="#ffffff",
        muted_bg="#e8ebf5",
        muted_fg="#4a5467",
        status_fg="#4a5467",
        traffic_red="#ff5f57",
        traffic_yellow="#fcbc2f",
        traffic_green="#28c840",
    ),
}


@dataclass
class FontTarget:
    widget: QWidget
    point_size: float
    pixel_size: int


def _capture_font_target(widget: QWidget) -> FontTarget:
    font = widget.font()
    return FontTarget(widget=widget, point_size=font.pointSizeF(), pixel_size=font.pixelSize())


def _apply_font_targets(
    targets: Sequence[FontTarget],
    offset: float,
    *,
    min_point: float = 6.0,
    min_pixel: int = 9,
) -> None:
    point_to_pixel = 96.0 / 72.0
    for target in targets:
        font = target.widget.font()
        if target.point_size > 0:
            font.setPointSizeF(max(target.point_size + offset, min_point))
        elif target.pixel_size > 0:
            computed = int(round(target.pixel_size + offset * point_to_pixel))
            font.setPixelSize(max(computed, min_pixel))
        target.widget.setFont(font)


class ThemeHelper:
    @classmethod
    def palette(cls, name: str) -> ThemePalette:
        return THEME_PALETTES.get(name, THEME_PALETTES[DEFAULT_THEME])

    @classmethod
    def available(cls) -> Sequence[str]:
        return list(THEME_PALETTES.keys())

BASE_DIR.mkdir(parents=True, exist_ok=True)
(NOTES_ROOT).mkdir(parents=True, exist_ok=True)
(PROMPTS_PATH.parent).mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------------------------

def timestamp() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def slugify(text: str, *, max_length: int = 48) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in text.lower()).strip("-")
    cleaned = "-".join(filter(None, cleaned.split("-")))
    if not cleaned:
        cleaned = f"note-{int(time.time())}"
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[:max_length].rstrip("-")


def load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(path: Path, data: Any) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        # Best-effort persistence; surfaced via UI logs later if required.
        pass


if not SETTINGS_PATH.exists():
    save_json(
        SETTINGS_PATH,
        {
            "provider": DEFAULT_PROVIDER,
            "model": DEFAULT_MODEL,
            "embed_model": DEFAULT_EMBED_MODEL,
            "autosave_interval": 20.0,
            "last_note_slug": None,
            "theme": DEFAULT_THEME,
            "font_point_adjust": DEFAULT_FONT_POINT_ADJUST,
        },
    )

if not PROMPTS_PATH.exists():
    save_json(
        PROMPTS_PATH,
        {
            "prompts": [
                {
                    "name": "Editorial Default",
                    "enabled": True,
                    "text": (
                        "You are a senior editor-engineer. Convert each user problem into precise "
                        "implementation corrections for this repository."
                    ),
                }
            ]
        },
    )


# --------------------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------------------

@dataclass
class NotePaths:
    root: Path
    note_md: Path
    dataset_jsonl: Path
    embeddings_json: Path
    attachments_full: Path
    attachments_thumbs: Path
    exports_dir: Path
    logs_dir: Path


@dataclass
class NoteMeta:
    id: str
    name: str
    slug: str
    created_ts: str
    updated_ts: str
    paths: NotePaths
    settings: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["paths"] = {k: str(v) for k, v in payload["paths"].items()}
        return payload


@dataclass
class Message:
    role: str
    text: str
    images: List[str]
    ts: str

    def to_json(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "text": self.text,
            "images": self.images,
            "ts": self.ts,
        }


# --------------------------------------------------------------------------------------
# Embedding helpers (placeholder deterministic embedding)
# --------------------------------------------------------------------------------------

EMBED_DIM = 96


def _hash_bytes(text: str) -> bytes:
    import hashlib

    return hashlib.sha256(text.encode("utf-8", "ignore")).digest()


def compute_embedding(text: str, *, dim: int = EMBED_DIM) -> List[float]:
    if not text:
        return [0.0] * dim
    raw = _hash_bytes(text)
    values: List[float] = []
    for idx in range(dim):
        byte = raw[idx % len(raw)]
        values.append((byte - 127.5) / 127.5)
    return values


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(y * y for y in b) ** 0.5
    if mag_a <= 1e-9 or mag_b <= 1e-9:
        return 0.0
    return dot / (mag_a * mag_b)


# --------------------------------------------------------------------------------------
# Ollama helpers
# --------------------------------------------------------------------------------------

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")


def discover_ollama_models() -> List[str]:
    models: List[str] = []
    # Try HTTP API first.
    if requests is not None:
        try:
            resp = requests.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags", timeout=2)
            if resp.ok:
                payload = resp.json()
                for model in payload.get("models", []):
                    name = model.get("name")
                    if isinstance(name, str):
                        models.append(name)
        except Exception:
            models = []
    if models:
        return models
    # Fallback to CLI list --json
    exe = shutil.which("ollama")
    if exe:
        try:
            output = subprocess.check_output([exe, "list", "--json"], text=True, timeout=5)
            for line in output.splitlines():
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                name = row.get("name")
                if isinstance(name, str):
                    models.append(name)
        except Exception:
            models = []
    if models:
        return models
    return [DEFAULT_MODEL]


# --------------------------------------------------------------------------------------
# Persistence manager
# --------------------------------------------------------------------------------------


class NoteManager:
    """Manage creation and persistence of notes on disk."""

    def __init__(self) -> None:
        self.base = NOTES_ROOT
        self.base.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def list_notes(self) -> List[NoteMeta]:
        notes: List[NoteMeta] = []
        if not self.base.exists():
            return notes
        for meta_path in sorted(self.base.glob("*/note.meta.json")):
            meta = self._load_meta_from_path(meta_path)
            if meta is not None:
                notes.append(meta)
        notes.sort(key=self._timestamp_key, reverse=True)
        return notes

    # ------------------------------------------------------------------
    def load_note(self, slug: str) -> Optional[NoteMeta]:
        return self._load_meta_from_path(self.base / slug / "note.meta.json")

    # ------------------------------------------------------------------
    def _load_meta_from_path(self, meta_path: Path) -> Optional[NoteMeta]:
        if not meta_path.exists():
            return None
        try:
            raw = meta_path.read_text(encoding="utf-8")
        except Exception:
            return None
        try:
            payload = json.loads(raw)
        except Exception:
            return None
        if not isinstance(payload, dict):
            return None
        return self._deserialize_meta(meta_path, payload)

    # ------------------------------------------------------------------
    def _deserialize_meta(self, meta_path: Path, payload: Dict[str, Any]) -> Optional[NoteMeta]:
        root = meta_path.parent
        slug = str(payload.get("slug") or root.name)
        name = str(payload.get("name") or slug)
        created_ts = str(payload.get("created_ts") or timestamp())
        updated_ts = str(payload.get("updated_ts") or created_ts)
        note_id = str(payload.get("id") or uuid.uuid4())

        default_paths = self._default_paths(root)
        stored_paths = payload.get("paths")
        if isinstance(stored_paths, dict):
            default_paths = NotePaths(
                root=root,
                note_md=self._coerce_path(stored_paths.get("note_md"), default_paths.note_md, root),
                dataset_jsonl=self._coerce_path(
                    stored_paths.get("dataset_jsonl"), default_paths.dataset_jsonl, root
                ),
                embeddings_json=self._coerce_path(
                    stored_paths.get("embeddings_json"), default_paths.embeddings_json, root
                ),
                attachments_full=self._coerce_path(
                    stored_paths.get("attachments_full"), default_paths.attachments_full, root
                ),
                attachments_thumbs=self._coerce_path(
                    stored_paths.get("attachments_thumbs"), default_paths.attachments_thumbs, root
                ),
                exports_dir=self._coerce_path(
                    stored_paths.get("exports_dir"), default_paths.exports_dir, root
                ),
                logs_dir=self._coerce_path(stored_paths.get("logs_dir"), default_paths.logs_dir, root),
            )

        settings_raw = payload.get("settings")
        settings: Dict[str, Any]
        if isinstance(settings_raw, dict):
            settings = dict(settings_raw)
        else:
            settings = {}
        settings.setdefault("font_point_adjust", DEFAULT_FONT_POINT_ADJUST)

        return NoteMeta(
            id=note_id,
            name=name,
            slug=slug,
            created_ts=created_ts,
            updated_ts=updated_ts,
            paths=default_paths,
            settings=settings,
        )

    # ------------------------------------------------------------------
    def _coerce_path(self, value: Any, default: Path, root: Path) -> Path:
        if isinstance(value, str) and value:
            candidate = Path(value)
            if not candidate.is_absolute():
                candidate = root / candidate
            return candidate
        return default

    # ------------------------------------------------------------------
    def _default_paths(self, root: Path) -> NotePaths:
        return NotePaths(
            root=root,
            note_md=root / "note.md",
            dataset_jsonl=root / "note.dataset.jsonl",
            embeddings_json=root / "embeddings.json",
            attachments_full=root / "attachments" / "full",
            attachments_thumbs=root / "attachments" / "thumbs",
            exports_dir=root / "exports",
            logs_dir=root / "logs",
        )

    # ------------------------------------------------------------------
    def _timestamp_key(self, note: NoteMeta) -> float:
        for value in (note.updated_ts, note.created_ts):
            if isinstance(value, str) and value:
                try:
                    cleaned = value.replace("Z", "+00:00") if value.endswith("Z") else value
                    return datetime.fromisoformat(cleaned).timestamp()
                except Exception:
                    continue
        return 0.0

    def create_note(self, name: str) -> NoteMeta:
        slug = slugify(name)
        root = self.base / slug
        suffix = 1
        while root.exists():
            root = self.base / f"{slug}-{suffix}"
            suffix += 1
        root.mkdir(parents=True, exist_ok=True)
        paths = NotePaths(
            root=root,
            note_md=root / "note.md",
            dataset_jsonl=root / "note.dataset.jsonl",
            embeddings_json=root / "embeddings.json",
            attachments_full=root / "attachments" / "full",
            attachments_thumbs=root / "attachments" / "thumbs",
            exports_dir=root / "exports",
            logs_dir=root / "logs",
        )
        paths.attachments_full.mkdir(parents=True, exist_ok=True)
        paths.attachments_thumbs.mkdir(parents=True, exist_ok=True)
        paths.exports_dir.mkdir(parents=True, exist_ok=True)
        paths.logs_dir.mkdir(parents=True, exist_ok=True)

        meta = NoteMeta(
            id=str(uuid.uuid4()),
            name=name,
            slug=root.name,
            created_ts=timestamp(),
            updated_ts=timestamp(),
            paths=paths,
            settings={
                "provider": DEFAULT_PROVIDER,
                "model": DEFAULT_MODEL,
                "embed_model": DEFAULT_EMBED_MODEL,
                "pane_visibility": dict(DEFAULT_PANE_VISIBILITY),
                "font_point_adjust": DEFAULT_FONT_POINT_ADJUST,
            },
        )
        # Seed files
        if not paths.note_md.exists():
            paths.note_md.write_text(f"# {name}\n\n", encoding="utf-8")
        if not paths.dataset_jsonl.exists():
            paths.dataset_jsonl.write_text("", encoding="utf-8")
        if not paths.embeddings_json.exists():
            paths.embeddings_json.write_text("[]\n", encoding="utf-8")
        self._write_meta(meta)
        return meta

    def _meta_path(self, note: NoteMeta) -> Path:
        return note.paths.root / "note.meta.json"

    def _write_meta(self, note: NoteMeta) -> None:
        save_json(self._meta_path(note), note.as_dict())

    def update_meta(self, note: NoteMeta) -> None:
        note.updated_ts = timestamp()
        self._write_meta(note)

    def append_message(self, note: NoteMeta, message: Message) -> None:
        path = note.paths.dataset_jsonl
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(message.to_json(), ensure_ascii=False) + "\n")
        # Update embeddings file
        entry = {
            "doc_id": message.ts,
            "vec": compute_embedding(message.text),
            "meta": {
                "role": message.role,
            },
        }
        embeddings = load_json(note.paths.embeddings_json, [])
        embeddings.append(entry)
        save_json(note.paths.embeddings_json, embeddings)
        note.updated_ts = timestamp()
        self._write_meta(note)

    def iter_messages(self, note: NoteMeta) -> Iterable[Dict[str, Any]]:
        path = note.paths.dataset_jsonl
        if not path.exists():
            return
        try:
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            return


# --------------------------------------------------------------------------------------
# Worker threads for LLM interactions
# --------------------------------------------------------------------------------------


class ChatWorker(QObject):
    chunk_received = Signal(str)
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, provider: str, model: str, messages: List[Dict[str, str]]):
        super().__init__()
        self.provider = provider
        self.model = model
        self.messages = messages
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    # ------------------------------------------------------------------
    def _run(self) -> None:
        try:
            if self.provider.lower() == "openai":
                text = self._run_openai()
            else:
                text = self._run_ollama()
            self.finished.emit(text)
        except Exception as exc:
            self.failed.emit(str(exc))

    # ------------------------------------------------------------------
    def _run_ollama(self) -> str:
        if requests is None:
            raise RuntimeError("requests module unavailable")
        url = f"{OLLAMA_HOST.rstrip('/')}/api/chat"
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": False,
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        msg = data.get("message") or {}
        content = msg.get("content") or data.get("response")
        if not isinstance(content, str):
            raise RuntimeError("invalid Ollama response")
        return content.strip()

    # ------------------------------------------------------------------
    def _run_openai(self) -> str:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        if requests is None:
            raise RuntimeError("requests module unavailable")
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("no choices returned")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            raise RuntimeError("no content returned")
        return content.strip()


# --------------------------------------------------------------------------------------
# UI components
# --------------------------------------------------------------------------------------


class DatasetInspector(QWidget):
    """Simple list showing retrieved dataset entries."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        self.title = QLabel("Dataset Inspector", self)
        self.title.setStyleSheet("font-weight:600;")
        layout.addWidget(self.title)
        self.listing = QListWidget(self)
        layout.addWidget(self.listing, 1)
        self._font_targets = [
            _capture_font_target(self.title),
            _capture_font_target(self.listing),
        ]
        self._palette = ThemeHelper.palette(DEFAULT_THEME)

    def update_entries(self, entries: Sequence[Tuple[float, Dict[str, Any]]]) -> None:
        self.listing.clear()
        for score, row in entries:
            text = row.get("text") or row.get("markdown") or "(no text)"
            preview = text.strip().splitlines()[0] if text else "(empty)"
            item = QListWidgetItem(f"{score:.2f} — {preview[:80]}")
            item.setToolTip(text)
            self.listing.addItem(item)

    def apply_theme(self, palette: ThemePalette) -> None:
        self._palette = palette
        self.title.setStyleSheet(f"font-weight:600; color:{palette.window_fg};")
        self.listing.setStyleSheet(
            f"QListWidget {{ background:{palette.muted_bg}; color:{palette.window_fg}; border:1px solid {palette.border}; border-radius:6px; }}"
        )

    def apply_font_scale(self, offset: float) -> None:
        _apply_font_targets(self._font_targets, offset)


class AttachmentsPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        self.title = QLabel("Attachments", self)
        self.title.setStyleSheet("font-weight:600;")
        layout.addWidget(self.title)
        self.listing = QListWidget(self)
        layout.addWidget(self.listing, 1)
        self.open_btn = QPushButton("Open Folder", self)
        self.open_btn.clicked.connect(self._open_folder)
        layout.addWidget(self.open_btn)
        self._current_root: Optional[Path] = None
        self._font_targets = [
            _capture_font_target(self.title),
            _capture_font_target(self.listing),
            _capture_font_target(self.open_btn),
        ]
        self._palette = ThemeHelper.palette(DEFAULT_THEME)

    def set_root(self, root: Path) -> None:
        self._current_root = root

    def refresh(self, files: Sequence[Path]) -> None:
        self.listing.clear()
        for path in files:
            item = QListWidgetItem(path.name)
            item.setToolTip(str(path))
            self.listing.addItem(item)

    def _open_folder(self) -> None:
        if not self._current_root:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._current_root)))

    def apply_theme(self, palette: ThemePalette) -> None:
        self._palette = palette
        self.title.setStyleSheet(f"font-weight:600; color:{palette.window_fg};")
        self.listing.setStyleSheet(
            f"QListWidget {{ background:{palette.muted_bg}; color:{palette.window_fg}; border:1px solid {palette.border}; border-radius:6px; }}"
        )
        self.open_btn.setStyleSheet(
            (
                "QPushButton {"
                f" background:{palette.accent};"
                f" color:{palette.accent_fg};"
                f" border:1px solid {palette.accent};"
                " border-radius:6px; padding:6px 12px; }"
                "QPushButton:hover {"
                f" background:{palette.accent_hover};"
                " }"
            )
        )

    def apply_font_scale(self, offset: float) -> None:
        _apply_font_targets(self._font_targets, offset)


class DragHandle(QPushButton):
    drag_started = Signal(QPoint)
    drag_moved = Signal(QPoint)
    drag_finished = Signal()

    def __init__(self, color: str, tooltip: str, cursor: Qt.CursorShape, parent: Optional[QWidget] = None) -> None:
        super().__init__("", parent)
        self._dragging = False
        self._press_pos = QPoint()
        self.setToolTip(tooltip)
        self.setCursor(cursor)
        self.setFixedSize(28, 28)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet(
            (
                "QPushButton {"
                " border-radius:14px;"
                f" background:{color};"
                " border:1px solid rgba(0,0,0,0.3);"
                " }"
            )
        )

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._press_pos = event.globalPosition().toPoint()
            self.drag_started.emit(self._press_pos)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._dragging:
            self.drag_moved.emit(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if self._dragging and event.button() == Qt.LeftButton:
            self._dragging = False
            self.drag_finished.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class SnippingOverlay(QWidget):
    captured = Signal(Path)
    canceled = Signal()

    MIN_WIDTH = 120
    MIN_HEIGHT = 90

    def __init__(self, attachments_dir: Path, parent: Optional[QWidget] = None) -> None:
        super().__init__(None)
        self.attachments_dir = attachments_dir
        self._screen = self._resolve_screen(parent)
        screen = self._screen or QGuiApplication.primaryScreen()
        if screen is None:
            raise RuntimeError("No available screen for snipping overlay")
        self._screen_geometry = screen.geometry()

        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.Tool, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowModality(Qt.ApplicationModal)
        self.setGeometry(self._screen_geometry)
        self._selection_rect = QRect(0, 0, 480, 320)
        self._selection_rect.moveCenter(self.rect().center())
        self._press_anchor = QPoint()
        self._initial_rect = QRect()

        self.move_handle = DragHandle("#ffffff", "Move selection", Qt.SizeAllCursor, self)
        self.move_handle.drag_started.connect(self._begin_move)
        self.move_handle.drag_moved.connect(self._update_move)
        self.move_handle.drag_finished.connect(self._end_drag)

        self.resize_handle = DragHandle("#388bfd", "Resize selection", Qt.SizeFDiagCursor, self)
        self.resize_handle.drag_started.connect(self._begin_resize)
        self.resize_handle.drag_moved.connect(self._update_resize)
        self.resize_handle.drag_finished.connect(self._end_drag)

        self.capture_btn = QPushButton("", self)
        self.capture_btn.setFixedSize(28, 28)
        self.capture_btn.setCursor(Qt.PointingHandCursor)
        self.capture_btn.setToolTip("Capture selection")
        self.capture_btn.setStyleSheet(
            "QPushButton { border-radius:14px; background:#2ac840; border:1px solid rgba(0,0,0,0.3); }"
        )
        self.capture_btn.clicked.connect(self._capture_selection)

        self.close_btn = QPushButton("", self)
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip("Cancel capture")
        self.close_btn.setStyleSheet(
            "QPushButton { border-radius:14px; background:#ff5f57; border:1px solid rgba(0,0,0,0.3); }"
        )
        self.close_btn.clicked.connect(self._cancel)

        self._update_controls()

    def _resolve_screen(self, widget: Optional[QWidget]):
        if widget is None:
            return QGuiApplication.primaryScreen()
        window = widget.window()
        if window is None:
            return QGuiApplication.primaryScreen()
        handle = window.windowHandle()
        if handle is None:
            return QGuiApplication.primaryScreen()
        return handle.screen()

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        QTimer.singleShot(0, self.activateWindow)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(1, 4, 9, 160))
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(self._selection_rect, Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        pen = QPen(QColor("#1f6feb"), 2)
        painter.setPen(pen)
        painter.drawRect(self._selection_rect)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key_Escape:
            self._cancel()
            event.accept()
            return
        super().keyPressEvent(event)

    def _begin_move(self, global_pos: QPoint) -> None:
        self._press_anchor = global_pos
        self._initial_rect = QRect(self._selection_rect)

    def _begin_resize(self, global_pos: QPoint) -> None:
        self._press_anchor = global_pos
        self._initial_rect = QRect(self._selection_rect)

    def _update_move(self, global_pos: QPoint) -> None:
        delta = global_pos - self._press_anchor
        rect = QRect(self._initial_rect)
        rect.moveTo(rect.topLeft() + delta)
        self._set_selection_rect(rect)

    def _update_resize(self, global_pos: QPoint) -> None:
        delta = global_pos - self._press_anchor
        rect = QRect(self._initial_rect)
        rect.setWidth(max(self.MIN_WIDTH, rect.width() + delta.x()))
        rect.setHeight(max(self.MIN_HEIGHT, rect.height() + delta.y()))
        self._set_selection_rect(rect)

    def _end_drag(self) -> None:
        self._initial_rect = QRect(self._selection_rect)

    def _set_selection_rect(self, rect: QRect) -> None:
        bounded = QRect(rect)
        bounded.setWidth(min(bounded.width(), self.width()))
        bounded.setHeight(min(bounded.height(), self.height()))
        if bounded.left() < 0:
            bounded.moveLeft(0)
        if bounded.top() < 0:
            bounded.moveTop(0)
        if bounded.right() > self.width():
            bounded.moveRight(self.width())
        if bounded.bottom() > self.height():
            bounded.moveBottom(self.height())
        if bounded.width() < self.MIN_WIDTH:
            bounded.setWidth(self.MIN_WIDTH)
        if bounded.height() < self.MIN_HEIGHT:
            bounded.setHeight(self.MIN_HEIGHT)
        self._selection_rect = bounded
        self._update_controls()
        self.update()

    def _update_controls(self) -> None:
        top_left = self._selection_rect.topLeft()
        spacing = 10
        base = QPoint(top_left.x() + spacing, top_left.y() + spacing)
        offset = self.move_handle.width() + 6
        self.move_handle.move(base)
        self.resize_handle.move(base + QPoint(offset, 0))
        self.capture_btn.move(base + QPoint(offset * 2, 0))
        self.close_btn.move(base + QPoint(offset * 3, 0))

    def _capture_selection(self) -> None:
        screen = self._screen or QGuiApplication.primaryScreen()
        if screen is None:
            self._cancel()
            return
        capture_rect = QRect(self._selection_rect)
        global_top_left = self._screen_geometry.topLeft() + capture_rect.topLeft()
        self.hide()
        QApplication.processEvents()
        pixmap = screen.grabWindow(
            0,
            global_top_left.x(),
            global_top_left.y(),
            capture_rect.width(),
            capture_rect.height(),
        )
        if pixmap.isNull():
            self.show()
            QMessageBox.critical(self, "Capture failed", "Unable to capture the selected region.")
            return
        self.attachments_dir.mkdir(parents=True, exist_ok=True)
        dest = self.attachments_dir / f"{timestamp()}_snip.png"
        pixmap.save(str(dest), "PNG")
        self.captured.emit(dest)
        self.close()

    def _cancel(self) -> None:
        self.canceled.emit()
        self.close()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        super().closeEvent(event)
        QTimer.singleShot(0, self.deleteLater)

class EvidencePanel(QGroupBox):
    ocr_ready = Signal(str)
    vision_ready = Signal(str)

    def __init__(self, note: NoteMeta, parent: Optional[QWidget] = None) -> None:
        super().__init__("Evidence", parent)
        self.note = note
        self.setLayout(QVBoxLayout())
        layout: QVBoxLayout = self.layout()  # type: ignore[assignment]
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self._palette = ThemeHelper.palette(DEFAULT_THEME)
        self._font_targets: List[FontTarget] = []
        self._active_overlay: Optional[SnippingOverlay] = None

        btn_row = QHBoxLayout()
        self.add_snapshot_btn = QPushButton("Add Snapshot", self)
        self.add_snapshot_btn.clicked.connect(self._capture_snapshot)
        btn_row.addWidget(self.add_snapshot_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        self.thumb_strip = QListWidget(self)
        self.thumb_strip.setViewMode(QListWidget.IconMode)
        self.thumb_strip.setIconSize(QSize(96, 96))
        self.thumb_strip.setResizeMode(QListWidget.Adjust)
        self.thumb_strip.setMovement(QListWidget.Static)
        self.thumb_strip.setSpacing(6)
        layout.addWidget(self.thumb_strip, 1)

        self.ocr_box = QTextBrowser(self)
        self.ocr_box.setPlaceholderText("OCR Markdown will appear here")
        layout.addWidget(self.ocr_box, 1)

        self.vision_box = QTextBrowser(self)
        self.vision_box.setPlaceholderText("Vision summary will appear here")
        layout.addWidget(self.vision_box, 1)

        self._thumbnails: List[Path] = []
        self._font_targets.extend(
            [
                _capture_font_target(self),
                _capture_font_target(self.add_snapshot_btn),
                _capture_font_target(self.thumb_strip),
                _capture_font_target(self.ocr_box),
                _capture_font_target(self.vision_box),
            ]
        )

    # ------------------------------------------------------------------
    def _capture_snapshot(self) -> None:
        box = QMessageBox(self)
        box.setWindowTitle("Add Snapshot")
        box.setIcon(QMessageBox.Question)
        box.setText("How would you like to add evidence?")
        browse_btn = box.addButton("Browse…", QMessageBox.AcceptRole)
        paste_btn = box.addButton("Paste from Clipboard", QMessageBox.ActionRole)
        capture_btn = box.addButton("Capture with Wireframe", QMessageBox.ActionRole)
        box.addButton(QMessageBox.Cancel)
        box.exec()
        clicked = box.clickedButton()
        if clicked is browse_btn:
            self._import_from_dialog()
        elif clicked is paste_btn:
            self._import_from_clipboard()
        elif clicked is capture_btn:
            self._launch_snipping_overlay()

    def _ensure_attachment_dirs(self) -> None:
        self.note.paths.attachments_full.mkdir(parents=True, exist_ok=True)
        self.note.paths.attachments_thumbs.mkdir(parents=True, exist_ok=True)

    def _ingest_snapshot(self, dest: Path) -> None:
        if not dest.exists():
            QMessageBox.warning(self, "Missing file", f"Captured file was not found: {dest}")
            return
        self._ensure_attachment_dirs()
        thumb_path = generate_thumbnail(dest)
        thumb_display: Path
        if thumb_path:
            thumb_dest = self.note.paths.attachments_thumbs / Path(thumb_path).name
            try:
                thumb_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(thumb_path, thumb_dest)
                thumb_display = thumb_dest
            except Exception:
                thumb_display = dest
        else:
            thumb_display = dest
        item = QListWidgetItem(QIcon(str(thumb_display)), dest.name)
        item.setToolTip(str(dest))
        self.thumb_strip.addItem(item)
        self._thumbnails.append(dest)
        self._run_ocr(dest)

    def _import_from_dialog(self) -> None:
        start_dir = str(self.note.paths.attachments_full)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            start_dir,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not file_path:
            return
        src = Path(file_path)
        dest = self.note.paths.attachments_full / f"{timestamp()}_{src.name}"
        try:
            self._ensure_attachment_dirs()
            shutil.copy2(src, dest)
        except Exception as exc:
            QMessageBox.critical(self, "Copy failed", f"Failed to copy image: {exc}")
            return
        self._ingest_snapshot(dest)

    def _import_from_clipboard(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "Clipboard unavailable", "Cannot access the system clipboard.")
            return
        image: QImage = clipboard.image()
        if image.isNull():
            pixmap = clipboard.pixmap()
            if not pixmap.isNull():
                image = pixmap.toImage()
        if image.isNull():
            QMessageBox.information(self, "No image found", "Clipboard does not contain image data.")
            return
        self._ensure_attachment_dirs()
        dest = self.note.paths.attachments_full / f"{timestamp()}_clipboard.png"
        if not image.save(str(dest), "PNG"):
            QMessageBox.critical(self, "Save failed", "Unable to write clipboard image to disk.")
            return
        self._ingest_snapshot(dest)

    def _launch_snipping_overlay(self) -> None:
        if self._active_overlay is not None:
            return
        try:
            overlay = SnippingOverlay(self.note.paths.attachments_full, self)
        except RuntimeError as exc:
            QMessageBox.critical(self, "Capture unavailable", str(exc))
            return
        self._active_overlay = overlay
        overlay.captured.connect(self._handle_snip_captured)
        overlay.canceled.connect(self._overlay_closed)
        overlay.destroyed.connect(lambda *_: self._overlay_closed())
        overlay.show()

    def _handle_snip_captured(self, dest: Path) -> None:
        self._active_overlay = None
        self._ingest_snapshot(dest)

    def _overlay_closed(self) -> None:
        self._active_overlay = None

    # ------------------------------------------------------------------
    def _run_ocr(self, path: Path) -> None:
        result: OCRResult = perform_ocr(path)
        if result.ok:
            self.ocr_box.append(f"### {path.name}\n\n{result.markdown}\n")
            self.ocr_ready.emit(result.markdown)
        else:
            self.ocr_box.append(f"### {path.name}\n\n*(OCR failed: {result.error})*\n")
        vision = analyze_image(path, result.markdown, client=None, model="", user_text="")
        if vision.ok:
            self.vision_box.append(f"### {path.name}\n\n{vision.summary}\n")
            self.vision_ready.emit(vision.summary)
        elif vision.error:
            self.vision_box.append(f"### {path.name}\n\n*(Vision unavailable: {vision.error})*\n")

    def apply_theme(self, palette: ThemePalette) -> None:
        self._palette = palette
        self.setStyleSheet(
            (
                "QGroupBox {"
                f" background:{palette.panel_bg};"
                f" color:{palette.panel_fg};"
                f" border:1px solid {palette.border};"
                " border-radius:8px; margin-top:12px; }"
                "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding:0 6px; }"
            )
        )
        button_style = (
            "QPushButton {"
            f" background:{palette.accent};"
            f" color:{palette.accent_fg};"
            f" border:1px solid {palette.accent};"
            " border-radius:6px; padding:6px 12px; }"
            "QPushButton:hover {"
            f" background:{palette.accent_hover};"
            " }"
        )
        self.add_snapshot_btn.setStyleSheet(button_style)
        self.thumb_strip.setStyleSheet(
            f"QListWidget {{ background:{palette.muted_bg}; color:{palette.panel_fg}; border:1px solid {palette.border}; border-radius:6px; }}"
        )
        browser_style = (
            "QTextBrowser {"
            f" background:{palette.secondary_bg};"
            f" color:{palette.secondary_fg};"
            f" border:1px solid {palette.border};"
            " border-radius:6px; }"
        )
        self.ocr_box.setStyleSheet(browser_style)
        self.vision_box.setStyleSheet(browser_style)

    def apply_font_scale(self, offset: float) -> None:
        _apply_font_targets(self._font_targets, offset)


class ConversationWidget(QWidget):
    message_submitted = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._palette = ThemeHelper.palette(DEFAULT_THEME)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.view = QTextBrowser(self)
        layout.addWidget(self.view, 1)
        input_row = QHBoxLayout()
        self.input = QPlainTextEdit(self)
        self.input.setPlaceholderText("Describe the problem or next step…")
        self.input.installEventFilter(self)
        input_row.addWidget(self.input, 1)
        self.send_btn = QPushButton("Send", self)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self._emit_message)
        input_row.addWidget(self.send_btn)
        layout.addLayout(input_row)
        self._font_targets = [
            _capture_font_target(self.view),
            _capture_font_target(self.input),
            _capture_font_target(self.send_btn),
        ]

    def append_message(self, role: str, text: str) -> None:
        palette = self._palette
        if role == "assistant":
            colour = palette.accent
        elif role == "system":
            colour = palette.traffic_yellow
        else:
            colour = palette.traffic_green
        safe_text = text.replace("<", "&lt;").replace(">", "&gt;")
        self.view.append(f"<p style='color:{colour};'><b>{role.title()}:</b> {safe_text}</p>")

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self.input and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ControlModifier:
                self._emit_message()
                return True
        return super().eventFilter(obj, event)

    def _emit_message(self) -> None:
        text = self.input.toPlainText().strip()
        if not text:
            return
        self.message_submitted.emit(text)
        self.input.clear()

    def apply_theme(self, palette: ThemePalette) -> None:
        self._palette = palette
        self.view.setStyleSheet(
            (
                "QTextBrowser {"
                f" background:{palette.panel_bg};"
                f" color:{palette.panel_fg};"
                f" border:1px solid {palette.border};"
                " border-radius:6px; }"
            )
        )
        self.input.setStyleSheet(
            (
                "QPlainTextEdit {"
                f" background:{palette.secondary_bg};"
                f" color:{palette.secondary_fg};"
                f" border:1px solid {palette.border};"
                " border-radius:6px; }"
            )
        )
        self.send_btn.setStyleSheet(
            (
                "QPushButton {"
                f" background:{palette.accent};"
                f" color:{palette.accent_fg};"
                f" border:1px solid {palette.accent};"
                " border-radius:6px; padding:6px 12px; }"
                "QPushButton:hover {"
                f" background:{palette.accent_hover};"
                " }"
            )
        )

    def apply_font_scale(self, offset: float) -> None:
        _apply_font_targets(self._font_targets, offset)


class NoteTab(QWidget):
    request_chat = Signal(str)
    export_requested = Signal()

    def __init__(
        self,
        manager: NoteManager,
        meta: NoteMeta,
        theme: str,
        font_offset: float,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.manager = manager
        self.meta = meta
        self.meta.settings.setdefault("font_point_adjust", font_offset)
        self._theme_name = theme
        self._font_offset = font_offset
        self._palette = ThemeHelper.palette(theme)
        self.retrieval_cache: List[Tuple[float, Dict[str, Any]]] = []
        self._font_targets: List[FontTarget] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        header_row = QHBoxLayout()
        self.header_label = QLabel("Problem title", self)
        header_row.addWidget(self.header_label)
        self.title_edit = QLineEdit(meta.name, self)
        self.title_edit.editingFinished.connect(self._save_title)
        header_row.addWidget(self.title_edit, 1)
        root.addLayout(header_row)

        self.splitter = QSplitter(Qt.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(6)
        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 3)
        root.addWidget(self.splitter, 1)

        left = QWidget(self.splitter)
        self.left_container = left
        self.left_container.setMinimumWidth(320)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.evidence = EvidencePanel(meta, left)
        self.evidence.setMinimumHeight(220)
        self.evidence.ocr_ready.connect(self._handle_ocr)
        self.evidence.vision_ready.connect(self._handle_vision)
        left_layout.addWidget(self.evidence, 2)

        self.conversation = ConversationWidget(left)
        self.conversation.setMinimumHeight(200)
        self.conversation.message_submitted.connect(self._handle_user_message)
        left_layout.addWidget(self.conversation, 4)

        summary_box = QGroupBox("Note summary", left)
        summary_box.setMinimumHeight(140)
        self.summary_box = summary_box
        summary_layout = QVBoxLayout(summary_box)
        self.summary_edit = QTextEdit(summary_box)
        self.summary_edit.setPlaceholderText("Running summary will appear here")
        self.summary_edit.textChanged.connect(self._save_summary)
        self.summary_edit.setMinimumHeight(120)
        summary_layout.addWidget(self.summary_edit)
        left_layout.addWidget(summary_box, 1)

        right = QWidget(self.splitter)
        self.right_container = right
        self.right_container.setMinimumWidth(240)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        self.dataset_inspector = DatasetInspector(right)
        self.dataset_inspector.setMinimumHeight(160)
        right_layout.addWidget(self.dataset_inspector, 3)
        self.attachments_panel = AttachmentsPanel(right)
        self.attachments_panel.setMinimumHeight(140)
        self.attachments_panel.set_root(meta.paths.attachments_full)
        right_layout.addWidget(self.attachments_panel, 2)
        self._default_split_sizes = [560, 280]
        self.splitter.setSizes(self._default_split_sizes)
        self._pane_widgets: Dict[str, QWidget] = {
            "evidence": self.evidence,
            "conversation": self.conversation,
            "summary": self.summary_box,
            "dataset": self.dataset_inspector,
            "attachments": self.attachments_panel,
        }

        self._font_targets.extend(
            [
                _capture_font_target(self),
                _capture_font_target(self.header_label),
                _capture_font_target(self.title_edit),
                _capture_font_target(self.summary_box),
                _capture_font_target(self.summary_edit),
            ]
        )

        self._initialize_pane_visibility()
        self.apply_theme(self._palette)
        self.apply_font_scale(self._font_offset)

        self._load_existing()

    # ------------------------------------------------------------------
    def _load_existing(self) -> None:
        attachments = sorted(self.meta.paths.attachments_full.glob("*"))
        self.attachments_panel.refresh(attachments)
        if self.meta.paths.note_md.exists():
            try:
                raw = self.meta.paths.note_md.read_text(encoding="utf-8")
            except Exception:
                raw = ""
            lines = raw.splitlines()
            if lines and lines[0].lstrip().startswith("#"):
                lines = lines[1:]
                if lines and not lines[0].strip():
                    lines = lines[1:]
            text = "\n".join(lines)
            self.summary_edit.blockSignals(True)
            self.summary_edit.setPlainText(text)
            self.summary_edit.blockSignals(False)
        for row in self.manager.iter_messages(self.meta):
            role = row.get("role", "user")
            text = row.get("text", "")
            self.conversation.append_message(role, text)
        self._update_retrieval("")

    def apply_theme(self, palette: ThemePalette) -> None:
        self._palette = palette
        self._theme_name = palette.name
        base_style = (
            "QWidget {"
            f" background:{palette.window_bg};"
            f" color:{palette.window_fg};"
            " }"
            "QLabel {"
            f" color:{palette.window_fg};"
            " }"
            "QLineEdit, QPlainTextEdit, QTextEdit {"
            f" background:{palette.input_bg};"
            f" color:{palette.input_fg};"
            f" border:1px solid {palette.border};"
            " border-radius:6px; padding:4px; }"
            "QSplitter::handle {"
            f" background:{palette.border};"
            " }"
            "QGroupBox {"
            f" background:{palette.panel_bg};"
            f" color:{palette.panel_fg};"
            f" border:1px solid {palette.border};"
            " border-radius:8px; margin-top:12px; }"
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding:0 6px; }"
        )
        self.setStyleSheet(base_style)
        self.evidence.apply_theme(palette)
        self.conversation.apply_theme(palette)
        self.dataset_inspector.apply_theme(palette)
        self.attachments_panel.apply_theme(palette)

    def apply_font_scale(self, offset: float, *, persist: bool = False) -> None:
        self._font_offset = offset
        _apply_font_targets(self._font_targets, offset)
        self.evidence.apply_font_scale(offset)
        self.conversation.apply_font_scale(offset)
        self.dataset_inspector.apply_font_scale(offset)
        self.attachments_panel.apply_font_scale(offset)
        if persist:
            if self.meta.settings.get("font_point_adjust") != offset:
                self.meta.settings["font_point_adjust"] = offset
                self.manager.update_meta(self.meta)

    def update_theme(self, theme: str) -> None:
        self.apply_theme(ThemeHelper.palette(theme))

    def font_offset(self) -> float:
        return self._font_offset

    # ------------------------------------------------------------------
    def pane_visibility(self) -> Dict[str, bool]:
        return {name: widget.isVisible() for name, widget in self._pane_widgets.items()}

    # ------------------------------------------------------------------
    def apply_pane_visibility(self, panes: Dict[str, bool], *, persist: bool = True) -> None:
        for name, widget in self._pane_widgets.items():
            widget.setVisible(bool(panes.get(name, True)))
        self._apply_splitter_policy()
        if persist:
            self._persist_pane_settings()

    # ------------------------------------------------------------------
    def set_pane_visible(self, pane: str, visible: bool) -> None:
        widget = self._pane_widgets.get(pane)
        if widget is None:
            return
        current = widget.isVisible()
        if current == bool(visible):
            return
        widget.setVisible(bool(visible))
        self._apply_splitter_policy()
        self._persist_pane_settings()

    # ------------------------------------------------------------------
    def _initialize_pane_visibility(self) -> None:
        stored = self.meta.settings.get("pane_visibility")
        defaults = self._default_pane_states()
        stored_dict = stored if isinstance(stored, dict) else {}
        normalized = {name: bool(stored_dict.get(name, defaults[name])) for name in defaults}
        missing_defaults = not isinstance(stored, dict) or any(name not in stored_dict for name in defaults)
        non_bool_values = any(not isinstance(stored_dict.get(name), bool) for name in defaults if name in stored_dict)
        self.meta.settings["pane_visibility"] = dict(normalized)
        self.apply_pane_visibility(normalized, persist=False)
        if missing_defaults or non_bool_values:
            self.manager.update_meta(self.meta)

    # ------------------------------------------------------------------
    def _default_pane_states(self) -> Dict[str, bool]:
        return dict(DEFAULT_PANE_VISIBILITY)

    # ------------------------------------------------------------------
    def _apply_splitter_policy(self) -> None:
        right_visible = any(
            self._pane_widgets[name].isVisible() for name in ("dataset", "attachments")
        )
        self.right_container.setVisible(right_visible)
        total = sum(self.splitter.sizes())
        if not total:
            total = sum(self._default_split_sizes)
        if not right_visible:
            self.splitter.setSizes([total, 0])
            return
        sizes = self.splitter.sizes()
        if sizes[1] == 0:
            left = int(total * 0.65)
            right = total - left
            if right <= 0:
                right = max(int(total * 0.35), 1)
                left = total - right
            self.splitter.setSizes([left, right])

    # ------------------------------------------------------------------
    def _persist_pane_settings(self) -> None:
        states = self.pane_visibility()
        stored = self.meta.settings.get("pane_visibility")
        if not isinstance(stored, dict) or stored != states:
            self.meta.settings["pane_visibility"] = dict(states)
            self.manager.update_meta(self.meta)

    # ------------------------------------------------------------------
    def _handle_user_message(self, text: str) -> None:
        self.conversation.append_message("user", text)
        msg = Message(role="user", text=text, images=[], ts=timestamp())
        self.manager.append_message(self.meta, msg)
        self._update_retrieval(text)
        self.request_chat.emit(text)

    # ------------------------------------------------------------------
    def append_assistant_message(self, text: str) -> None:
        self.conversation.append_message("assistant", text)
        msg = Message(role="assistant", text=text, images=[], ts=timestamp())
        self.manager.append_message(self.meta, msg)
        self.summary_edit.setPlainText(text if not self.summary_edit.toPlainText() else self.summary_edit.toPlainText() + "\n" + text)
        self._update_retrieval(text)

    # ------------------------------------------------------------------
    def _handle_ocr(self, markdown: str) -> None:
        msg = Message(role="system", text=f"OCR:\n{markdown}", images=[], ts=timestamp())
        self.manager.append_message(self.meta, msg)
        self._update_retrieval(markdown)
        attachments = sorted(self.meta.paths.attachments_full.glob("*"))
        self.attachments_panel.refresh(attachments)

    # ------------------------------------------------------------------
    def _handle_vision(self, summary: str) -> None:
        if not summary:
            return
        msg = Message(role="system", text=f"Vision:\n{summary}", images=[], ts=timestamp())
        self.manager.append_message(self.meta, msg)
        self._update_retrieval(summary)

    # ------------------------------------------------------------------
    def _update_retrieval(self, query: str) -> None:
        query_vec = compute_embedding(query)
        rows: List[Tuple[float, Dict[str, Any]]] = []
        for row in self.manager.iter_messages(self.meta):
            vec = compute_embedding(row.get("text", ""))
            score = cosine_similarity(query_vec, vec)
            rows.append((score, row))
        rows.sort(key=lambda pair: pair[0], reverse=True)
        self.retrieval_cache = rows[:DATASET_TOP_K]
        self.dataset_inspector.update_entries(self.retrieval_cache)

    # ------------------------------------------------------------------
    def export_documents(self) -> None:
        self.export_requested.emit()

    # ------------------------------------------------------------------
    def _save_summary(self) -> None:
        text = self.summary_edit.toPlainText().rstrip()
        title = self.title_edit.text().strip() or "Untitled note"
        content = f"# {title}\n\n{text}\n" if text else f"# {title}\n"
        try:
            self.meta.paths.note_md.write_text(content, encoding="utf-8")
        except Exception:
            pass
        else:
            self.manager.update_meta(self.meta)

    # ------------------------------------------------------------------
    def _save_title(self) -> None:
        title = self.title_edit.text().strip() or "Untitled note"
        if title != self.meta.name:
            self.meta.name = title
            self.manager.update_meta(self.meta)
            self._save_summary()


# --------------------------------------------------------------------------------------
# Main widget
# --------------------------------------------------------------------------------------


class TopStrip(QWidget):
    provider_changed = Signal(str)
    model_changed = Signal(str)
    mic_changed = Signal(str)
    mic_toggled = Signal(bool)
    new_tab_requested = Signal()
    export_requested = Signal()
    pane_visibility_changed = Signal(str, bool)
    detach_requested = Signal(bool)
    theme_changed = Signal(str)
    font_scale_changed = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("TopStrip")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(8)

        self._font_targets: List[FontTarget] = []
        self._pane_buttons: Dict[str, QToolButton] = {}
        self._traffic_lights: List[QLabel] = []
        self._font_scale_labels: Dict[float, str] = {
            DEFAULT_FONT_POINT_ADJUST: "Default",
            COMPACT_FONT_POINT_ADJUST: "Compact (-2pt)",
        }
        self._font_scale_lookup: Dict[str, float] = {
            label: value for value, label in self._font_scale_labels.items()
        }

        traffic_container = QWidget(self)
        traffic_layout = QHBoxLayout(traffic_container)
        traffic_layout.setContentsMargins(0, 0, 0, 0)
        traffic_layout.setSpacing(4)
        for colour_key in ("traffic_red", "traffic_yellow", "traffic_green"):
            dot = QLabel(traffic_container)
            dot.setFixedSize(12, 12)
            traffic_layout.addWidget(dot)
            self._traffic_lights.append(dot)
        layout.addWidget(traffic_container)
        layout.addSpacing(8)

        self.provider_label = QLabel("Provider", self)
        self.provider_combo = QComboBox(self)
        self.provider_combo.addItems(["Ollama", "OpenAI"])
        self.provider_combo.currentTextChanged.connect(self.provider_changed.emit)
        layout.addWidget(self.provider_label)
        layout.addWidget(self.provider_combo)

        self.model_label = QLabel("Model", self)
        self.model_combo = QComboBox(self)
        self.model_combo.setEditable(True)
        self.model_combo.currentTextChanged.connect(self.model_changed.emit)
        layout.addWidget(self.model_label)
        layout.addWidget(self.model_combo, 1)

        self.mic_label = QLabel("Microphone", self)
        self.mic_combo = QComboBox(self)
        self.mic_combo.currentTextChanged.connect(self.mic_changed.emit)
        layout.addWidget(self.mic_label)
        layout.addWidget(self.mic_combo)

        self.refresh_mics_btn = QToolButton(self)
        self.refresh_mics_btn.setText("↻")
        self.refresh_mics_btn.setToolTip("Refresh available microphones")
        self.refresh_mics_btn.clicked.connect(self._populate_mics)
        layout.addWidget(self.refresh_mics_btn)

        self.mic_toggle = QToolButton(self)
        self.mic_toggle.setText("🎙")
        self.mic_toggle.setCheckable(True)
        self.mic_toggle.setToolTip("Toggle microphone (F9)")
        self.mic_toggle.clicked.connect(self.mic_toggled.emit)
        layout.addWidget(self.mic_toggle)

        self.theme_label = QLabel("Theme", self)
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self._emit_theme_changed)
        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_combo)

        self.font_label = QLabel("Font", self)
        self.font_scale_combo = QComboBox(self)
        for label in self._font_scale_labels.values():
            self.font_scale_combo.addItem(label)
        self.font_scale_combo.currentTextChanged.connect(self._emit_font_scale_changed)
        layout.addWidget(self.font_label)
        layout.addWidget(self.font_scale_combo)

        self.new_tab_btn = QPushButton("New Tab", self)
        self.new_tab_btn.clicked.connect(self.new_tab_requested.emit)
        layout.addWidget(self.new_tab_btn)

        self.export_btn = QPushButton("Export", self)
        self.export_btn.clicked.connect(self.export_requested.emit)
        layout.addWidget(self.export_btn)

        self.detach_btn = QToolButton(self)
        self.detach_btn.setCheckable(True)
        self.detach_btn.setCursor(Qt.PointingHandCursor)
        self.detach_btn.setToolTip("Pop the notes out into a standalone window")
        self.detach_btn.setAccessibleName("Pop out User Guided Notes")
        self.detach_btn.setText("Pop Out")
        self.detach_btn.toggled.connect(self._on_detach_toggled)
        layout.addWidget(self.detach_btn)

        pane_layout = QHBoxLayout()
        pane_layout.setContentsMargins(0, 0, 0, 0)
        pane_layout.setSpacing(4)
        pane_specs = [
            ("evidence", "Evidence", "Show or hide the evidence panel"),
            ("conversation", "Conversation", "Show or hide the conversation log"),
            ("summary", "Summary", "Show or hide the summary editor"),
            ("dataset", "Dataset", "Show or hide the dataset inspector"),
            ("attachments", "Attachments", "Show or hide the attachments list"),
        ]
        for key, label, tip in pane_specs:
            btn = QToolButton(self)
            btn.setText(label)
            btn.setCheckable(True)
            btn.setChecked(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tip)
            btn.setAccessibleName(f"Toggle {label} visibility")
            btn.toggled.connect(lambda checked, name=key: self.pane_visibility_changed.emit(name, checked))
            pane_layout.addWidget(btn)
            self._pane_buttons[key] = btn
        layout.addLayout(pane_layout)
        layout.addStretch(1)

        self.status_label = QLabel("Ready", self)
        layout.addWidget(self.status_label)

        self._populate_mics()

        self._font_targets.extend(
            [
                _capture_font_target(self.provider_label),
                _capture_font_target(self.provider_combo),
                _capture_font_target(self.model_label),
                _capture_font_target(self.model_combo),
                _capture_font_target(self.mic_label),
                _capture_font_target(self.mic_combo),
                _capture_font_target(self.refresh_mics_btn),
                _capture_font_target(self.mic_toggle),
                _capture_font_target(self.theme_label),
                _capture_font_target(self.theme_combo),
                _capture_font_target(self.font_label),
                _capture_font_target(self.font_scale_combo),
                _capture_font_target(self.new_tab_btn),
                _capture_font_target(self.export_btn),
                _capture_font_target(self.detach_btn),
                _capture_font_target(self.status_label),
            ]
        )

    def set_models(self, models: Sequence[str]) -> None:
        current = self.model_combo.currentText()
        self.model_combo.clear()
        for model in models:
            self.model_combo.addItem(model)
        if current:
            idx = self.model_combo.findText(current)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.setCurrentIndex(0)

    def _populate_mics(self) -> None:
        try:
            from PySide6.QtMultimedia import QMediaDevices  # type: ignore
        except Exception:
            QTimer.singleShot(0, lambda: self.status_label.setText("Audio unavailable"))
            return
        devices = QMediaDevices.audioInputs()
        self.mic_combo.clear()
        for dev in devices:
            self.mic_combo.addItem(dev.description())
        if not devices:
            self.mic_combo.addItem("No devices")

    def set_theme_name(self, theme: str) -> None:
        display = "Light" if theme.lower() == "light" else "Dark"
        blocker = QSignalBlocker(self.theme_combo)
        self.theme_combo.setCurrentText(display)

    def set_font_offset(self, offset: float) -> None:
        label = None
        for value, name in self._font_scale_labels.items():
            if abs(value - offset) <= 0.1:
                label = name
                break
        if label is None:
            label = self._font_scale_labels[DEFAULT_FONT_POINT_ADJUST]
        blocker = QSignalBlocker(self.font_scale_combo)
        self.font_scale_combo.setCurrentText(label)

    def apply_theme(self, palette: ThemePalette) -> None:
        combo_style = (
            "QComboBox {"
            f" background:{palette.input_bg};"
            f" color:{palette.input_fg};"
            f" border:1px solid {palette.border};"
            " border-radius:6px; padding:2px 6px; }"
            "QComboBox::drop-down { border: none; }"
            "QComboBox QAbstractItemView {"
            f" background:{palette.input_bg};"
            f" color:{palette.input_fg};"
            f" border:1px solid {palette.border};"
            " }"
        )
        self.setStyleSheet(
            f"#TopStrip {{ background:{palette.secondary_bg}; border-bottom:1px solid {palette.border}; }}"
            f"#TopStrip QLabel {{ color:{palette.window_fg}; }}"
            + combo_style
        )
        button_style = (
            "QPushButton {"
            f" background:{palette.accent};"
            f" color:{palette.accent_fg};"
            f" border:1px solid {palette.accent};"
            " border-radius:6px; padding:6px 12px; }"
            "QPushButton:hover {"
            f" background:{palette.accent_hover};"
            " }"
        )
        for btn in (self.new_tab_btn, self.export_btn):
            btn.setStyleSheet(button_style)
        tool_style = (
            "QToolButton {"
            f" background:{palette.muted_bg};"
            f" color:{palette.window_fg};"
            f" border:1px solid {palette.border};"
            " border-radius:6px; padding:4px 8px; }"
            "QToolButton:hover {"
            f" background:{palette.accent};"
            f" color:{palette.accent_fg};"
            " }"
            "QToolButton:checked {"
            f" background:{palette.accent};"
            f" color:{palette.accent_fg};"
            " }"
        )
        for widget in (self.refresh_mics_btn, self.mic_toggle, self.detach_btn):
            widget.setStyleSheet(tool_style)
        for btn in self._pane_buttons.values():
            btn.setStyleSheet(tool_style)
        self.status_label.setStyleSheet(f"color:{palette.status_fg};")
        colours = [palette.traffic_red, palette.traffic_yellow, palette.traffic_green]
        for dot, colour in zip(self._traffic_lights, colours):
            dot.setStyleSheet(
                f"background:{colour}; border-radius:6px; border:1px solid {palette.border};"
            )

    def apply_font_scale(self, offset: float) -> None:
        _apply_font_targets(self._font_targets, offset)

    def _emit_theme_changed(self, text: str) -> None:
        self.theme_changed.emit(text.lower())

    def _emit_font_scale_changed(self, text: str) -> None:
        value = self._font_scale_lookup.get(text, DEFAULT_FONT_POINT_ADJUST)
        self.font_scale_changed.emit(value)

    def apply_pane_states(self, states: Dict[str, bool]) -> None:
        for name, button in self._pane_buttons.items():
            desired = bool(states.get(name, True))
            if button.isChecked() != desired:
                blocker = QSignalBlocker(button)
                button.setChecked(desired)

    def _on_detach_toggled(self, detached: bool) -> None:
        self._apply_detach_label(detached)
        self.detach_requested.emit(detached)

    def _apply_detach_label(self, detached: bool) -> None:
        if detached:
            self.detach_btn.setText("Dock")
            self.detach_btn.setToolTip("Return the notes to the desktop card")
            self.detach_btn.setAccessibleName("Dock User Guided Notes")
        else:
            self.detach_btn.setText("Pop Out")
            self.detach_btn.setToolTip("Pop the notes out into a standalone window")
            self.detach_btn.setAccessibleName("Pop out User Guided Notes")

    def set_detach_state(self, detached: bool) -> None:
        if self.detach_btn.isChecked() == detached:
            self._apply_detach_label(detached)
            return
        blocker = QSignalBlocker(self.detach_btn)
        self.detach_btn.setChecked(detached)
        self._apply_detach_label(detached)


class UserGuidedNotesWidget(QWidget):
    request_detach = Signal(object)
    request_redock = Signal(object)

    def __init__(self, embedded: bool = True, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.embedded = embedded
        self.manager = NoteManager()
        raw_settings = load_json(SETTINGS_PATH, {})
        self.settings = raw_settings if isinstance(raw_settings, dict) else {}
        self.settings.setdefault("last_note_slug", None)
        self.settings.setdefault("theme", DEFAULT_THEME)
        self.settings.setdefault("font_point_adjust", DEFAULT_FONT_POINT_ADJUST)
        self._workers: List[ChatWorker] = []
        self._theme_name = str(self.settings.get("theme") or DEFAULT_THEME)
        try:
            self._font_offset = float(self.settings.get("font_point_adjust", DEFAULT_FONT_POINT_ADJUST))
        except (TypeError, ValueError):
            self._font_offset = DEFAULT_FONT_POINT_ADJUST
        self.setWindowTitle("User Guided Notes")
        self.setMinimumSize(520, 360)
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.setMovable(True)
        self.tabs.tabBarDoubleClicked.connect(self._rename_tab)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.menu_bar = QMenuBar(self)
        root.addWidget(self.menu_bar)
        self._build_menus()

        self.top_strip = TopStrip(self)
        root.addWidget(self.top_strip)

        root.addWidget(self.tabs, 1)

        self.top_strip.set_detach_state(not self.embedded)
        self.top_strip.provider_changed.connect(self._handle_provider_change)
        self.top_strip.new_tab_requested.connect(self._create_note_tab)
        self.top_strip.export_requested.connect(self._export_active_note)
        self.top_strip.pane_visibility_changed.connect(self._handle_pane_visibility_change)
        self.top_strip.detach_requested.connect(self._handle_detach_toggle)
        self.top_strip.theme_changed.connect(self._handle_theme_change)
        self.top_strip.font_scale_changed.connect(self._handle_font_scale_change)
        self.tabs.currentChanged.connect(self._handle_tab_changed)

        self.models = discover_ollama_models()
        self.top_strip.set_models(self.models)

        palette = ThemeHelper.palette(self._theme_name)
        self.top_strip.apply_theme(palette)
        self.top_strip.set_theme_name(self._theme_name)
        self.top_strip.set_font_offset(self._font_offset)
        self.top_strip.apply_font_scale(self._font_offset)

        self._initialize_tabs()

    # ------------------------------------------------------------------
    def apply_embedded_state(self, embedded: bool) -> None:
        if self.embedded == embedded:
            self.top_strip.set_detach_state(not embedded)
            return
        self.embedded = embedded
        self.top_strip.set_detach_state(not embedded)

    # ------------------------------------------------------------------
    def _handle_detach_toggle(self, detached: bool) -> None:
        if detached:
            if self.embedded:
                self.request_detach.emit(self)
            else:
                self.top_strip.set_detach_state(True)
        else:
            if not self.embedded:
                self.request_redock.emit(self)
            else:
                self.top_strip.set_detach_state(False)

    # ------------------------------------------------------------------
    def _handle_theme_change(self, theme: str) -> None:
        normalized = theme.lower()
        if normalized not in ThemeHelper.available():
            normalized = DEFAULT_THEME
        if normalized == self._theme_name:
            self.top_strip.set_theme_name(normalized)
            return
        self._theme_name = normalized
        self.settings["theme"] = normalized
        self._save_settings()
        palette = ThemeHelper.palette(normalized)
        self.top_strip.apply_theme(palette)
        self.top_strip.set_theme_name(normalized)
        self.top_strip.apply_font_scale(self._font_offset)
        for idx in range(self.tabs.count()):
            widget = self.tabs.widget(idx)
            if isinstance(widget, NoteTab):
                widget.update_theme(normalized)

    # ------------------------------------------------------------------
    def _handle_font_scale_change(self, offset: float) -> None:
        try:
            normalized = float(offset)
        except (TypeError, ValueError):
            normalized = DEFAULT_FONT_POINT_ADJUST
        if abs(self._font_offset - normalized) <= 1e-6:
            return
        self._font_offset = normalized
        self.settings["font_point_adjust"] = normalized
        self._save_settings()
        self.top_strip.set_font_offset(normalized)
        self.top_strip.apply_font_scale(normalized)
        for idx in range(self.tabs.count()):
            widget = self.tabs.widget(idx)
            if isinstance(widget, NoteTab):
                widget.apply_font_scale(normalized, persist=True)

    # ------------------------------------------------------------------
    def _build_menus(self) -> None:
        file_menu = self.menu_bar.addMenu("File")
        new_action = QAction("New Note", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._create_note_tab)
        file_menu.addAction(new_action)

        export_action = QAction("Export", self)
        export_action.triggered.connect(self._export_active_note)
        file_menu.addAction(export_action)

        open_root = QAction("Open Notes Folder", self)
        open_root.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(NOTES_ROOT)))
        )
        file_menu.addAction(open_root)

        settings_menu = self.menu_bar.addMenu("Settings")
        refresh_models = QAction("Refresh Models", self)
        refresh_models.triggered.connect(self._refresh_models)
        settings_menu.addAction(refresh_models)

    # ------------------------------------------------------------------
    def _refresh_models(self) -> None:
        self.models = discover_ollama_models()
        self.top_strip.set_models(self.models)

    # ------------------------------------------------------------------
    def _handle_pane_visibility_change(self, pane: str, visible: bool) -> None:
        widget = self.tabs.currentWidget()
        if isinstance(widget, NoteTab):
            widget.set_pane_visible(pane, visible)
            self._sync_top_strip_with_tab(widget)

    # ------------------------------------------------------------------
    def _handle_tab_changed(self, index: int) -> None:
        widget = self.tabs.widget(index)
        if isinstance(widget, NoteTab):
            self._sync_top_strip_with_tab(widget)
            self._remember_last_note(widget.meta)
        else:
            self.top_strip.apply_pane_states(DEFAULT_PANE_VISIBILITY)
            self.top_strip.set_font_offset(self._font_offset)
            self.top_strip.set_theme_name(self._theme_name)
            self.top_strip.apply_font_scale(self._font_offset)

    # ------------------------------------------------------------------
    def _sync_top_strip_with_tab(self, tab: NoteTab) -> None:
        self._font_offset = tab.font_offset()
        self.top_strip.apply_pane_states(tab.pane_visibility())
        self.top_strip.set_font_offset(self._font_offset)
        self.top_strip.apply_font_scale(self._font_offset)
        self.top_strip.set_theme_name(self._theme_name)

    # ------------------------------------------------------------------
    def _initialize_tabs(self) -> None:
        notes = self.manager.list_notes()
        target: Optional[NoteMeta] = None
        last_slug = self.settings.get("last_note_slug")
        if isinstance(last_slug, str) and last_slug:
            for note in notes:
                if note.slug == last_slug:
                    target = note
                    break
        if target is None and notes:
            target = notes[0]
        if target is not None:
            self._open_note_tab(target)
        else:
            self._create_note_tab()

    # ------------------------------------------------------------------
    def _save_settings(self) -> None:
        save_json(SETTINGS_PATH, self.settings)

    # ------------------------------------------------------------------
    def _remember_last_note(self, meta: NoteMeta) -> None:
        slug = meta.slug
        if not slug:
            return
        if self.settings.get("last_note_slug") == slug:
            return
        self.settings["last_note_slug"] = slug
        self._save_settings()

    # ------------------------------------------------------------------
    def _open_note_tab(self, meta: NoteMeta, *, make_current: bool = True) -> NoteTab:
        offset_raw = meta.settings.get("font_point_adjust")
        try:
            note_offset = float(offset_raw)
        except (TypeError, ValueError):
            note_offset = self._font_offset
        tab = NoteTab(self.manager, meta, self._theme_name, note_offset, self)
        tab.request_chat.connect(lambda text, t=tab: self._invoke_chat(t, text))
        tab.export_requested.connect(lambda t=tab: self._export_note(t))
        idx = self.tabs.addTab(tab, meta.name)
        if make_current:
            self.tabs.setCurrentIndex(idx)
            self._sync_top_strip_with_tab(tab)
            self._remember_last_note(meta)
        return tab

    # ------------------------------------------------------------------
    def _select_existing_note(self, exclude_slug: Optional[str]) -> Optional[NoteMeta]:
        notes = self.manager.list_notes()
        if not notes:
            return None
        if exclude_slug:
            for note in notes:
                if note.slug != exclude_slug:
                    return note
        return notes[0]

    # ------------------------------------------------------------------
    def _update_last_note_setting(self) -> None:
        widget = self.tabs.currentWidget()
        if isinstance(widget, NoteTab):
            self._remember_last_note(widget.meta)

    # ------------------------------------------------------------------
    def _create_note_tab(self) -> None:
        name, ok = self._prompt("New note", "Enter note title:")
        if not ok and self.tabs.count() > 0:
            return
        meta = self.manager.create_note(name or "Untitled note")
        if meta.settings.get("font_point_adjust") != self._font_offset:
            meta.settings["font_point_adjust"] = self._font_offset
            self.manager.update_meta(meta)
        self._open_note_tab(meta)

    # ------------------------------------------------------------------
    def _prompt(self, title: str, text: str) -> Tuple[str, bool]:
        dialog = QInputDialog(self)
        dialog.setWindowTitle(title)
        dialog.setLabelText(text)
        dialog.setTextValue("Untitled note")
        dialog.resize(380, 120)
        ok = dialog.exec() == QDialog.Accepted
        return dialog.textValue(), ok

    # ------------------------------------------------------------------
    def _invoke_chat(self, tab: NoteTab, text: str) -> None:
        provider = self.top_strip.provider_combo.currentText()
        model = self.top_strip.model_combo.currentText() or DEFAULT_MODEL
        system_prompt = self._build_system_prompt(tab)
        messages = [{"role": "system", "content": system_prompt}]
        for row in tab.retrieval_cache:
            entry = row[1]
            if entry.get("role") == "assistant":
                messages.append({"role": "assistant", "content": entry.get("text", "")})
            else:
                messages.append({"role": "user", "content": entry.get("text", "")})
        messages.append({"role": "user", "content": text})

        worker = ChatWorker(provider, model, messages)

        def _cleanup(worker_ref: ChatWorker) -> None:
            try:
                self._workers.remove(worker_ref)
            except ValueError:
                pass

        def _finished(reply: str, *, worker_ref: ChatWorker = worker, target: NoteTab = tab) -> None:
            _cleanup(worker_ref)
            target.append_assistant_message(reply)

        def _failed(err: str, *, worker_ref: ChatWorker = worker, target: NoteTab = tab) -> None:
            _cleanup(worker_ref)
            target.append_assistant_message(f"(LLM error: {err})")

        worker.finished.connect(_finished)
        worker.failed.connect(_failed)
        self._workers.append(worker)
        worker.start()

    # ------------------------------------------------------------------
    def _build_system_prompt(self, tab: NoteTab) -> str:
        return (
            "You are a senior editor-engineer. Convert each user problem into precise implementation "
            "corrections. Provide actionable bullet points."
        )

    # ------------------------------------------------------------------
    def _export_active_note(self) -> None:
        widget = self.tabs.currentWidget()
        if isinstance(widget, NoteTab):
            self._export_note(widget)

    # ------------------------------------------------------------------
    def _export_note(self, tab: NoteTab) -> None:
        narrative = tab.summary_edit.toPlainText().strip()
        convo_lines = []
        for row in self.manager.iter_messages(tab.meta):
            role = row.get("role", "user")
            text = row.get("text", "")
            convo_lines.append(f"### {role}\n\n{text}\n")
        context_doc = "\n".join(convo_lines)
        impl_plan = [
            "# Implementation Tasklist",
            "",
            f"Generated: {timestamp()}",
            "",
            "## Summary",
            narrative or "(No summary)",
        ]
        task_path = tab.meta.paths.exports_dir / "Implementation_Tasklist.md"
        task_path.write_text("\n".join(impl_plan), encoding="utf-8")

        context_path = tab.meta.paths.exports_dir / "Note_Context.md"
        context_doc = "# Note Context\n\n" + context_doc
        context_path.write_text(context_doc, encoding="utf-8")
        QMessageBox.information(self, "Export complete", f"Exports saved to {tab.meta.paths.exports_dir}")

    # ------------------------------------------------------------------
    def _rename_tab(self, index: int) -> None:
        if index < 0:
            return
        widget = self.tabs.widget(index)
        if not isinstance(widget, NoteTab):
            return
        title, ok = self._prompt("Rename note", "New title:")
        if ok and title:
            widget.meta.name = title
            widget.manager.update_meta(widget.meta)
            self.tabs.setTabText(index, title)

    # ------------------------------------------------------------------
    def _close_tab(self, index: int) -> None:
        widget = self.tabs.widget(index)
        if widget is None:
            return
        closed_slug = widget.meta.slug if isinstance(widget, NoteTab) else None
        widget.deleteLater()
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            fallback = self._select_existing_note(closed_slug)
            if fallback is not None:
                self._open_note_tab(fallback)
            else:
                self._create_note_tab()
        else:
            self._update_last_note_setting()

    # ------------------------------------------------------------------
    def _handle_provider_change(self, provider: str) -> None:
        if provider.lower() == "ollama":
            self._refresh_models()
        else:
            # Provide OpenAI defaults
            self.top_strip.set_models(["gpt-4o-mini", "gpt-4.1"])


class UserGuidedNotesWindow(QMainWindow):
    def __init__(self, widget: Optional[UserGuidedNotesWidget] = None) -> None:
        super().__init__()
        if widget is None:
            widget = UserGuidedNotesWidget(embedded=False)
        else:
            widget.apply_embedded_state(False)
        self.widget = widget
        self.setCentralWidget(self.widget)
        self.setWindowTitle("User Guided Notes")
        self.setFont(self.widget.font())
        self.resize(1100, 700)


# --------------------------------------------------------------------------------------
# Factory / entry points
# --------------------------------------------------------------------------------------


def create_card(parent: Optional[QWidget] = None, embedded: bool = True):
    widget = UserGuidedNotesWidget(embedded=embedded, parent=parent)
    meta = {
        "title": "User Guided Notes",
        "persist_tag": "user_guided_notes",
        "task_profile": "notes",
        "task_tooltip": "User Guided Notes",
    }
    return widget, meta


def build_widget(parent: Optional[QWidget] = None, embedded: bool = True):
    return create_card(parent=parent, embedded=embedded)


def main() -> None:
    app = QApplication.instance()
    owns_app = False
    if app is None:
        app = QApplication(sys.argv)
        owns_app = True
    window = UserGuidedNotesWindow()
    window.show()
    if owns_app:
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
