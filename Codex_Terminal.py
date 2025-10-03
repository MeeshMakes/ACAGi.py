#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Virtual Desktop — Codex-Terminal (All-in-One)
- Virtual Desktop canvas (bright blue), draggable chat/terminal card
- Local-first Chat (Ollama-only) + OCR/Vision pipeline
- Dataset persistence (JSONL + embeddings) + user-memory (lightweight)
- **Codex Rust CLI bridge for Windows**:
    • Download/verify/launch Codex CLI
    • Mirror CMD output (snapshots)
    • Inject text to CMD
    • **Press Enter reliably** (WriteConsoleInputW + SendInput fallback)
    • Start/Stop/Show/Hide controls
    • Tri-state LED (red/yellow/green) for bridge health

Requires: PySide6>=6.6, requests, Pillow (optional), local ollama, Windows 10+ for bridge.
"""

from __future__ import annotations

from tools.python_runtime import ensure_supported_python

ensure_supported_python()

# --- DPI policy MUST be set before QApplication is created ---
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt

# Reuse ACAGi's guarded DPI helper so standalone and bundled entry points
# respect the same idempotent guard and Qt instance detection logic.
from ACAGi import _ensure_high_dpi_rounding_policy

import argparse
import base64
import copy
import ctypes
import hashlib
import io
import json
import logging
import math
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import threading
import traceback
import time
import traceback
import uuid
import zipfile
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Deque, Dict, List, Optional, Sequence, Set, Tuple
import token_budget

# Optional deps
try:
    import requests  # type: ignore
except Exception:
    requests = None  # surfaced in UI

try:
    from PIL import Image  # type: ignore
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

from PySide6.QtCore import (
    QRect,
    QRectF,
    QTimer,
    Signal,
    Slot,
    QSize,
    QEvent,
    QMimeData,
    QPoint,
    QUrl,
    QFileSystemWatcher,
)
from PySide6.QtGui import (
    QAction, QCloseEvent, QColor, QCursor, QDesktopServices, QKeyEvent, QKeySequence,
    QPainter, QPalette, QLinearGradient, QPainterPath, QImage, QPixmap, QIcon,
    QTextCharFormat, QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QTextBrowser, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QComboBox,
    QSlider, QFormLayout, QGroupBox, QTabWidget, QScrollArea,
    QToolButton, QCheckBox, QSpinBox, QSpacerItem, QSizePolicy, QInputDialog,
    QMenu, QStyle, QListWidget, QListWidgetItem, QAbstractItemView,
)

from tasks import record_diff
from tasks.bus import publish, subscribe, Subscription
from tasks.drawer import TaskDrawer
from tasks.models import (
    Task,
    TaskEvent,
    append_event,
    append_run_log,
    append_run_output,
    append_task,
    update_task,
)
from error_console import ErrorConsole, StderrRedirector, log_exception
from safety import SafetyViolation, manager as safety_manager
from image_pipeline import analyze_image, perform_ocr
from prompt_loader import get_prompt_watcher, iter_prompt_definitions, prompt_text
from background import (
    BackgroundConfig,
    BackgroundFit,
    BackgroundManager,
    BackgroundMode,
    GifBg,
    GLViewportBg,
    StaticImageBg,
    VideoBg,
)
from repo_reference_helper import RepoReference, RepoReferenceHelper

VD_LOGGER_NAME = "VirtualDesktop"
VD_LOG_FILENAME = "vd_system.log"
VD_LOG_PATH = Path(__file__).resolve().with_name(VD_LOG_FILENAME)


def _shared_log_handler_attached(logger: logging.Logger) -> bool:
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            try:
                if Path(handler.baseFilename).resolve() == VD_LOG_PATH:
                    return True
            except Exception:
                continue
    return False


def configure_shared_logger() -> logging.Logger:
    """Return a logger that writes to the shared Virtual Desktop log file."""

    logger = logging.getLogger(VD_LOGGER_NAME)
    if not _shared_log_handler_attached(logger):
        VD_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(VD_LOG_PATH, mode="a", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(handler)
    if logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)
    return logger

# --------------------------------------------------------------------------------------
# Crash capture
# --------------------------------------------------------------------------------------

class ErrorPopup(QDialog):
    def __init__(self, title: str, message: str, details: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(900, 580)
        layout = QVBoxLayout(self)

        msg = QLabel(message, self); msg.setWordWrap(True)
        layout.addWidget(msg)

        self.details = QTextBrowser(self)
        self.details.setPlainText(details)
        self.details.setReadOnly(True)
        layout.addWidget(self.details, 1)

        btns = QHBoxLayout()
        copy_btn = QPushButton("Copy to Clipboard", self)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.details.toPlainText()))
        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.accept)
        btns.addStretch(1); btns.addWidget(copy_btn); btns.addWidget(close_btn)
        layout.addLayout(btns)

def install_global_exception_handler(logger: Optional[logging.Logger] = None):
    shared_logger = logger or configure_shared_logger()

    def _hook(exc_type, exc, tb):
        shared_logger.error(
            "Unhandled exception in Codex Terminal",
            exc_info=(exc_type, exc, tb),
        )
        for handler in shared_logger.handlers:
            try:
                handler.flush()
            except Exception:
                continue

        text = "".join(traceback.format_exception(exc_type, exc, tb))
        try:
            dlg = ErrorPopup("Unhandled Error", "An unexpected error occurred.", text)
            dlg.exec()
        except Exception:
            shared_logger.error(
                "Failed to display unhandled error dialog",
                exc_info=True,
            )

    sys.excepthook = _hook

# --------------------------------------------------------------------------------------
# Paths / constants
# --------------------------------------------------------------------------------------

APP_NAME = "Agent Virtual Desktop — Codex-Terminal"

def here() -> Path:
    return Path(os.path.abspath(os.path.dirname(__file__)))

def _resolve_directory(path: Path) -> Path:
    try:
        resolved = path.expanduser().resolve()
    except Exception:
        resolved = path.expanduser()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def base_dir() -> Path:
    env = os.environ.get("CODEX_WORKSPACE")
    if env:
        try:
            return _resolve_directory(Path(env))
        except Exception:
            pass
    fallback = Path(__file__).resolve().with_name("Agent_Codex_Standalone")
    return _resolve_directory(fallback)


def workspace_root() -> Path:
    return base_dir()


def agent_data_root() -> Path:
    """Root directory scoped to the workspace for Codex-managed assets."""

    root = workspace_root() / ".codex_agent"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _agent_subdir(name: str) -> Path:
    path = agent_data_root() / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def agent_images_dir() -> Path:
    return _agent_subdir("images")


def agent_sessions_dir() -> Path:
    return _agent_subdir("sessions")


def agent_logs_dir() -> Path:
    return _agent_subdir("logs")


def agent_archives_dir() -> Path:
    return _agent_subdir("archives")


def agent_data_dir() -> Path:
    return _agent_subdir("data")


def agent_lexicons_dir() -> Path:
    return _agent_subdir("lexicons")


for _name in ("images", "sessions", "logs", "archives", "data", "lexicons"):
    _agent_subdir(_name)


def _clamp_to_agent_subdir(raw: Optional[Path | str], *, subdir: Path) -> Path:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return subdir

    try:
        candidate = Path(raw).expanduser()
    except Exception:
        return subdir

    if not candidate.is_absolute():
        candidate = subdir / candidate

    try:
        resolved = candidate.resolve(strict=False)
    except Exception:
        resolved = candidate

    try:
        agent_root = agent_data_root().resolve(strict=False)
    except Exception:
        agent_root = agent_data_root()

    if resolved == agent_root or agent_root in resolved.parents:
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    target = subdir / resolved.name
    target.mkdir(parents=True, exist_ok=True)
    return target


def styles_path() -> Path:
    p = here() / "Styles"
    p.mkdir(parents=True, exist_ok=True)
    return p / "advanced_styles.json"

def _legacy_transit_candidates() -> list[Path]:
    return [here() / "Codex-Transit"]


def _migrate_legacy_transit(target: Path) -> None:
    for legacy in _legacy_transit_candidates():
        if not legacy.exists() or not legacy.is_dir():
            continue
        try:
            if legacy.resolve() == target.resolve():
                continue
        except Exception:
            pass

        if not target.exists():
            try:
                legacy.rename(target)
                return
            except OSError:
                pass

        target.mkdir(parents=True, exist_ok=True)

        for child in list(legacy.iterdir()):
            destination = target / child.name
            if destination.exists():
                continue
            try:
                child.rename(destination)
            except OSError:
                shutil.move(str(child), str(destination))

        try:
            legacy.rmdir()
        except OSError:
            pass


def transit_dir() -> Path:
    target = workspace_root() / "Terminal Desktop"
    _migrate_legacy_transit(target)
    target.mkdir(parents=True, exist_ok=True)
    return target


def terminal_desktop_dir() -> Path:
    """Location for the standalone terminal's desktop workspace."""
    return transit_dir()

def lexicons_dir() -> Path:
    return agent_lexicons_dir()

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

MEMORY_PATH = here() / "memory" / "codex_memory.json"
MEMORY_LOCK = threading.Lock()

def _read_codex_memory() -> Dict[str, Any]:
    if not MEMORY_PATH.exists():
        return {"sessions": [], "work_items": []}
    try:
        data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"sessions": [], "work_items": []}
    if not isinstance(data, dict):
        return {"sessions": [], "work_items": []}
    sessions = data.get("sessions")
    if not isinstance(sessions, list):
        sessions = []
    work_items = data.get("work_items")
    if not isinstance(work_items, list):
        work_items = []
    return {"sessions": sessions, "work_items": work_items}

def load_session_notes() -> List[Dict[str, str]]:
    data = _read_codex_memory()
    notes: List[Dict[str, str]] = []
    for entry in data.get("sessions", []):
        if isinstance(entry, dict):
            note = entry.get("notes", "")
            ts = entry.get("timestamp", "")
            if isinstance(note, str) and note.strip():
                notes.append({
                    "timestamp": str(ts) if isinstance(ts, str) else str(ts),
                    "notes": note.strip(),
                })
    return notes

def _utc_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def append_session_note(note: str) -> Dict[str, str]:
    entry = {"timestamp": _utc_iso(), "notes": note.strip()}
    with MEMORY_LOCK:
        data = _read_codex_memory()
        sessions = data.get("sessions", [])
        sessions.append(entry)
        data["sessions"] = sessions
        data.setdefault("work_items", [])
        MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return entry

def is_windows() -> bool:
    return os.name == "nt" or platform.system().lower().startswith("win")

# Ollama
DEFAULT_CHAT_MODEL = "qwen3:8b"
DEFAULT_VISION_MODEL = "llava-llama3:latest"
DEFAULT_VISION_OCR_MODEL = "benhaotang/Nanonets-OCR-s:latest"
DEFAULT_EMBED_MODEL = "snowflake-arctic-embed2:latest"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

# Codex portable transit
DEFAULT_CODEX_EXE = transit_dir() / "codex-x86_64-pc-windows-msvc.exe"
SETTINGS_JSON = transit_dir() / "settings.json"
INSTALL_MANIFEST = transit_dir() / "INSTALL_MANIFEST.md"

# Demo asset URL/signature (adjust if you use a different build)
RELEASE_TAG = "rust-v0.34.0"
ASSET_ZIP = "codex-x86_64-pc-windows-msvc.exe.zip"
ASSET_ZIP_SHA256 = "789563e58e6126de96329c8e154718409378831abcef3856c8b46527b20c08ac"
RELEASE_BASE = f"https://github.com/openai/codex/releases/download/{RELEASE_TAG}"
ASSET_URL = f"{RELEASE_BASE}/{ASSET_ZIP}"

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------
# Theme (bright blue desktop variant + high contrast)
# --------------------------------------------------------------------------------------

@dataclass
class Theme:
    desktop_top: str = "#0f58ff"
    desktop_mid: str = "#2f7cff"
    desktop_edge_glow: str = "#70c3ff"

    card_bg: str = "#0e1624"
    card_border: str = "#2B3B4C"
    card_radius: int = 12

    header_bg: str = "#111b2b"
    header_text: str = "#eaf2ff"

    user_bubble: str = "#0d3a84"
    user_text: str = "#eaf2ff"
    ai_bubble: str = "#0f1a2d"
    ai_text: str = "#ffffff"
    think_text: str = "#6fb2b2"
    model_name: str = "#00a7a7"

    accent: str = "#1E5AFF"
    accent_hover: str = "#2f72ff"
    muted: str = "#1c2a3b"

    live_ok: str = "#00d17a"    # green
    live_warn: str = "#ffb300"  # yellow
    live_err: str = "#ff3b30"   # red

    @classmethod
    def load(cls, path: str | Path) -> "Theme":
        p = Path(path)
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                base = cls()
                for k, v in data.items():
                    if hasattr(base, k):
                        setattr(base, k, v)
                return base
            except Exception:
                return cls()
        return cls()

# --------------------------------------------------------------------------------------
# Live pill + small LED
# --------------------------------------------------------------------------------------

class LivePill(QFrame):
    def __init__(self, theme: Theme, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = theme
        self._alpha = 1.0
        self.setFixedHeight(24)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)

    def _tick(self):
        t = time.time() * 2.0
        self._alpha = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t))
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(96, 24)

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(0, 0, -1, -1)

        bg = QColor(self.theme.muted); bg.setAlphaF(0.90)
        path = QPainterPath(); path.addRoundedRect(QRectF(rect), 12, 12)
        p.fillPath(path, bg)

        p.setPen(QColor("#bcd5ff"))
        font = p.font(); font.setPointSizeF(9.5); font.setBold(True); p.setFont(font)
        text = "LIVE"
        metrics = p.fontMetrics()
        tw = metrics.horizontalAdvance(text)
        margin = 10
        dot_d = 8
        p.drawText(QRect(margin, 0, tw + 2, rect.height()), Qt.AlignVCenter | Qt.AlignLeft, text)

        dot_x = rect.right() - margin - dot_d
        dot_y = rect.center().y() - dot_d // 2
        live = QColor(self.theme.live_ok)
        live.setAlphaF(self._alpha)
        p.setBrush(live); p.setPen(Qt.NoPen)
        p.drawEllipse(QRect(dot_x, dot_y, dot_d, dot_d))

class BridgeLED(QWidget):
    def __init__(self, theme: Theme, tooltip: str = "Bridge", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = theme
        self._state = "red"  # red -> error/off, yellow -> starting/awaiting, green -> healthy
        self.setToolTip(tooltip)
        self.setFixedSize(14, 14)

    def set_state(self, state: str):
        self._state = state
        self.update()

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(1, 1, -1, -1)
        color = {
            "green": self.theme.live_ok,
            "yellow": self.theme.live_warn,
            "red": self.theme.live_err,
        }.get(self._state, self.theme.live_warn)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(rect)


class ToggleSwitch(QCheckBox):
    """High-contrast slider-style checkbox."""

    def __init__(self, theme: Theme, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = theme
        self.setCursor(Qt.PointingHandCursor)
        self.setTristate(False)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setAccessibleName("Interpreter automation toggle")

    def sizeHint(self) -> QSize:  # pragma: no cover - Qt provides layout sizing
        return QSize(56, 30)

    def paintEvent(self, event):  # pragma: no cover - visual styling only
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(1, 1, -1, -1)

        radius = rect.height() / 2
        active = self.isChecked()
        enabled = self.isEnabled()

        bg_color = QColor(self.theme.accent if active else self.theme.card_border)
        if not enabled:
            bg_color.setAlphaF(0.4)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, radius, radius)

        knob_diameter = rect.height() - 8
        knob_y = rect.top() + 4
        if active:
            knob_x = rect.right() - knob_diameter - 4
            knob_color = QColor("#ffffff")
        else:
            knob_x = rect.left() + 4
            knob_color = QColor(self.theme.header_text)
            if not enabled:
                knob_color.setAlphaF(0.4)
        painter.setBrush(knob_color)
        painter.drawEllipse(QRectF(knob_x, knob_y, knob_diameter, knob_diameter))

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

def run_checked(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    *,
    task: Optional[Task] = None,
    dataset_root: Optional[Path] = None,
    workspace: Optional[Path] = None,
    cancelled: bool = False,
) -> Tuple[int, str, str]:
    """Execute ``cmd`` and update task bookkeeping when provided."""

    stdout = ""
    stderr = ""
    return_code = 1

    header_logged = False
    if task is not None:
        try:
            command_display = shlex.join(cmd)
        except Exception:
            command_display = " ".join(cmd)
        suffix: List[str] = []
        if cwd:
            try:
                suffix.append(f"cwd={Path(cwd).resolve()}")
            except Exception:
                suffix.append(f"cwd={cwd}")
        header = f"{_utc_iso()} $ {command_display}"
        if suffix:
            header += f" ({', '.join(suffix)})"
        try:
            append_run_log(task, header, dataset_root, channel="action")
            header_logged = True
        except Exception as exc:
            log_exception("Task run-log header failed", exc)

    try:
        blocked = False
        try:
            safety_manager.ensure_command_allowed(cmd)
        except SafetyViolation as exc:
            blocked = True
            stderr = str(exc)

        if not blocked:
            try:
                cp = subprocess.run(
                    cmd,
                    cwd=str(cwd) if cwd else None,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                return_code = cp.returncode
                stdout = cp.stdout or ""
                stderr = cp.stderr or ""
            except Exception as exc:
                stderr = str(exc)
                log_exception("run_checked execution failed", exc)
    finally:
        if task is not None:
            try:
                if stdout or stderr:
                    append_run_output(
                        task,
                        stdout=stdout,
                        stderr=stderr,
                        dataset_root=dataset_root,
                    )
                if header_logged or stdout or stderr:
                    append_run_log(
                        task,
                        f"{_utc_iso()} exit {return_code}",
                        dataset_root,
                        channel="action",
                    )
            except Exception as log_exc:
                log_exception("Task run-log update failed", log_exc)

            workspace_path: Path
            try:
                if workspace is not None:
                    workspace_path = Path(workspace)
                elif cwd is not None:
                    workspace_path = Path(cwd)
                else:
                    workspace_path = Path.cwd()
            except Exception:
                workspace_path = Path.cwd()

            diff_snapshot = None
            try:
                diff_snapshot = record_diff(task.id, workspace_root=workspace_path)
            except Exception as diff_exc:
                log_exception("Task diff capture failed", diff_exc)

            next_status: Optional[str] = None
            if cancelled:
                next_status = "cancelled"
            elif return_code == 0:
                if diff_snapshot and (diff_snapshot.added > 0 or diff_snapshot.removed > 0):
                    next_status = "merged"
            else:
                next_status = "failed"

            if next_status:
                now = datetime.now(UTC).timestamp()
                source = task.source or "terminal"
                try:
                    updated_task = update_task(task.id, status=next_status, updated_ts=now)
                    event_payload: Dict[str, Any] = {
                        "exit_code": return_code,
                        "diff_added": updated_task.diffs.added,
                        "diff_removed": updated_task.diffs.removed,
                        "cancelled": bool(cancelled),
                    }
                    append_event(
                        TaskEvent(
                            ts=now,
                            task_id=task.id,
                            event="status",
                            by=source,
                            to=next_status,
                            data=event_payload,
                        )
                    )
                except Exception as status_exc:
                    log_exception("Task status auto-update failed", status_exc)
                else:
                    publish("task.status", {"id": updated_task.id, "status": updated_task.status})
                    publish("task.updated", updated_task.to_dict())

    return return_code, stdout, stderr

def slug(s: str) -> str:
    t = re.sub(r"[^A-Za-z0-9_.-]+", "-", s.strip())
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t or f"item-{uuid.uuid4().hex[:8]}"

# --------------------------------------------------------------------------------------
# Ollama client (local only)
# --------------------------------------------------------------------------------------

class OllamaClient:
    def __init__(self, host: str = OLLAMA_HOST):
        self.host = host.rstrip("/")

    def _http(self) -> bool:
        return requests is not None

    def health(self) -> Tuple[bool, str]:
        if not self._http():
            return False, "requests not installed"
        try:
            r = requests.get(self.host, timeout=3)
            return (r.ok, "OK" if r.ok else f"{r.status_code}")
        except Exception as e:
            return False, str(e)

    def list_models(self) -> Tuple[bool, List[str], str]:
        if self._http():
            try:
                r = requests.get(f"{self.host}/api/tags", timeout=5)
                if r.ok:
                    data = r.json()
                    names = [m.get("name") or m.get("model") for m in data.get("models", []) if m.get("name") or m.get("model")]
                    return True, sorted(set(n for n in names if n)), ""
            except Exception:
                pass
        rc, out, err = run_checked(["ollama", "list"])
        if rc != 0:
            return False, [], err or out or "Ollama Not found"
        try:
            lines = [ln.strip().split()[0] for ln in out.splitlines()[1:] if ln.strip()]
            return True, sorted(set(lines)), ""
        except Exception:
            return True, [], ""

    def embeddings(self, model: str, text: str) -> Tuple[bool, List[float], str]:
        if not self._http():
            return False, [], "requests not installed"
        try:
            payload = {"model": model, "input": text}
            r = requests.post(f"{self.host}/api/embeddings", json=payload, timeout=120)
            if not r.ok:
                return False, [], f"{r.status_code} {r.text[:200]}"
            obj = r.json()
            vec = obj.get("embedding") or (obj.get("data") or [{}])[0].get("embedding")
            if not isinstance(vec, list):
                return False, [], "bad embedding response"
            return True, vec, ""
        except Exception as e:
            return False, [], str(e)

    def chat(self, model: str, messages: List[Dict[str, Any]], images: Optional[List[str]] = None) -> Tuple[bool, str, str]:
        if not self._http():
            return False, "", "requests not installed"
        try:
            body: Dict[str, Any] = {"model": model, "messages": messages, "stream": False}
            if images:
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        msg["images"] = images
                        break
            r = requests.post(f"{self.host}/api/chat", json=body, timeout=600, headers={"Content-Type": "application/json"})
            if not r.ok:
                return False, "", f"{r.status_code} {r.text[:200]}"
            try:
                data = r.json()
            except Exception:
                txt = r.text.strip()
                last = txt.splitlines()[-1] if txt else "{}"
                data = json.loads(last)
            content = (data.get("message") or {}).get("content", "") or data.get("response", "")
            return True, content, ""
        except Exception as e:
            return False, "", str(e)

# --------------------------------------------------------------------------------------
# Lexicons (minimal)
# --------------------------------------------------------------------------------------

DEFAULT_LEXICONS: Dict[str, Dict[str, Any]] = {
    "lang/markdown": {"type": "language", "name": "markdown",
                      "snippets": [{"label": "image", "pattern": "![alt](path.png)"}],
                      "keywords": ["# ", "```", "[", "]", "(", ")"]},
    "shells/cmd": {"type": "shell", "name": "cmd",
                   "snippets": [{"label": "dir", "pattern": "dir"}],
                   "keywords": ["dir", "cd", "copy", "del"]},
}

class LexiconManager:
    def __init__(self, folder: Path):
        self.folder = folder
        self.data: Dict[str, Dict[str, Any]] = {}
        self.enabled: Dict[str, bool] = {}
        self.reload()

    def reload(self):
        self.data.clear()
        self.enabled.clear()
        for key, val in DEFAULT_LEXICONS.items():
            self.data[key] = val
            self.enabled[key] = True
        if self.folder.is_dir():
            for p in self.folder.glob("*.json"):
                try:
                    obj = json.loads(p.read_text(encoding="utf-8"))
                    if isinstance(obj, dict):
                        key = obj.get("id") or p.stem
                        self.data[key] = obj
                        self.enabled[key] = True
                except Exception:
                    continue

    def toggle(self, key: str, state: bool):
        if key in self.data:
            self.enabled[key] = state

    def list_keys(self) -> List[str]:
        return sorted(self.data.keys())

    def active_items(self) -> Dict[str, Dict[str, Any]]:
        return {k: v for k, v in self.data.items() if self.enabled.get(k, True)}

    def auto_tags(self, text: str) -> List[str]:
        tags: List[str] = []
        for key, node in self.active_items().items():
            kws = node.get("keywords") or []
            for kw in kws:
                if kw and kw.lower() in text.lower():
                    tags.append(key)
                    break
        return tags

# --------------------------------------------------------------------------------------
# Dataset + conversation persistence + user memory
# --------------------------------------------------------------------------------------

def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b): return 0.0
    num = sum(x*y for x, y in zip(a, b))
    da = math.sqrt(sum(x*x for x in a)); db = math.sqrt(sum(y*y for y in b))
    if da == 0 or db == 0: return 0.0
    return num / (da * db)

class DatasetManager:
    def __init__(self, session_dir: Path, embedder: str, ollama: OllamaClient, data_root: Optional[Path] = None, enable_semantic: bool = True):
        self.session_dir = ensure_dir(session_dir)
        self.dataset_path = self.session_dir / "dataset.jsonl"
        self.embedder = embedder
        self.ollama = ollama
        self.lock = threading.Lock()
        self.enable_semantic = enable_semantic
        self.data_root = ensure_dir(data_root) if data_root else self.session_dir.parent

    def add_entry(self, role: str, text: str, images: List[Path], tags: Optional[List[str]] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        entry: Dict[str, Any] = {
            "id": uuid.uuid4().hex, "ts": time.time(),
            "role": role, "text": text, "images": [ip.name for ip in images], "tags": tags or [], "embedding": [],
        }
        if extra: entry.update(extra)
        if self.enable_semantic and text.strip():
            ok, vec, _ = self.ollama.embeddings(self.embedder, text)
            if ok and isinstance(vec, list): entry["embedding"] = vec
        with self.lock:
            with self.dataset_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def _all_dataset_files(self) -> List[Path]:
        files: List[Path] = []
        for p in self.data_root.rglob("dataset.jsonl"):
            files.append(p)
        if self.dataset_path not in files and self.dataset_path.exists():
            files.append(self.dataset_path)
        return files

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self.enable_semantic:
            return []
        ok, qvec, _ = self.ollama.embeddings(self.embedder, query)
        if not ok: return []
        rows: List[Dict[str, Any]] = []
        for fp in self._all_dataset_files():
            try:
                with fp.open("r", encoding="utf-8") as f:
                    for ln in f:
                        rows.append(json.loads(ln))
            except Exception:
                continue
        scored = []
        for obj in rows:
            vec = obj.get("embedding") or []
            sc = cosine(qvec, vec) if isinstance(vec, list) and vec else 0.0
            scored.append((sc, obj))
        scored.sort(key=lambda t: t[0], reverse=True)
        return [o for _, o in scored[:k]]

@dataclass(slots=True)
class ConversationPaths:
    identifier: str
    root: Path
    jsonl_path: Path
    markdown_path: Path
    source: str
    meta_path: Optional[Path] = None


class ConversationIO:
    _DEFAULT_MAX_ENTRIES = 1_000
    _DEFAULT_MAX_BYTES = 1_048_576  # 1 MiB

    def __init__(
        self,
        session_dir: Path,
        embedder: str,
        ollama: OllamaClient,
        enable_embeddings: bool,
        *,
        session_token: Optional[str] = None,
        archive_root: Optional[Path] = None,
        max_entries: int = _DEFAULT_MAX_ENTRIES,
        max_bytes: int = _DEFAULT_MAX_BYTES,
    ):
        self.session_dir = ensure_dir(session_dir)
        self.md_path = self.session_dir / "conversation.md"
        self.jsonl_path = self.session_dir / "conversation.jsonl"
        self.vec_path = self.session_dir / "conversation.vec"
        self.session_meta_path = self.session_dir / "session.meta.json"
        self.embedder = embedder
        self.ollama = ollama
        self.enable_embeddings = enable_embeddings
        self.lock = threading.RLock()
        self.session_token = session_token or ""
        target_archive_root = archive_root or agent_archives_dir()
        self.archive_root = ensure_dir(target_archive_root)
        self.repo_archive_root = ensure_dir(here() / "Archived Conversations")
        self.max_entries = max(0, int(max_entries))
        self.max_bytes = max(0, int(max_bytes))
        self._entry_count = 0

        self._ensure_archive_placeholder(self.archive_root)
        self._ensure_archive_placeholder(self.repo_archive_root)
        self._prepare_session()

    def _prepare_session(self) -> None:
        stored_token = self._read_session_token()
        with self.lock:
            if stored_token and self.session_token and stored_token != self.session_token:
                self._archive_current_logs_locked("session-rollover", stored_token)
            elif not stored_token and self.session_token and self._has_existing_logs_locked():
                self._archive_current_logs_locked("session-rollover", None)

            if self.session_token:
                self._write_session_token_locked(self.session_token)
            elif stored_token:
                self.session_token = stored_token

            self._ensure_header_locked()
            self._entry_count = self._count_entries_locked()

    def _ensure_archive_placeholder(self, root: Path) -> None:
        gitkeep = root / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")

    def _mirror_archive_to_repo(self, archive_dir: Path) -> None:
        try:
            mirror_dir = ensure_dir(self.repo_archive_root / archive_dir.name)
        except Exception:
            logger.exception("Failed to prepare archive mirror directory")
            return

        for item in archive_dir.iterdir():
            if not item.is_file():
                continue
            dest = mirror_dir / item.name
            try:
                shutil.copy2(item, dest)
            except Exception:
                logger.exception("Failed to mirror archive file %s", item)

    def _write_session_token_locked(self, token: str) -> None:
        data = {"id": token, "updated": datetime.now(UTC).isoformat()}
        with self.session_meta_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    def _read_session_token(self) -> str:
        if not self.session_meta_path.exists():
            return ""
        try:
            data = json.loads(self.session_meta_path.read_text(encoding="utf-8"))
            token = data.get("id")
            return str(token) if isinstance(token, str) else ""
        except Exception:
            return ""

    def _has_existing_logs_locked(self) -> bool:
        for path in (self.md_path, self.jsonl_path, self.vec_path):
            if path.exists() and path.stat().st_size > 0:
                return True
        return False

    def _write_header_unlocked(self) -> None:
        self.md_path.write_text("# Conversation\n\n", encoding="utf-8")

    def _ensure_header_locked(self) -> None:
        if not self.md_path.exists():
            self._write_header_unlocked()

    def _count_entries_locked(self) -> int:
        if not self.jsonl_path.exists():
            return 0
        try:
            with self.jsonl_path.open("r", encoding="utf-8") as fh:
                return sum(1 for _ in fh)
        except Exception:
            return 0

    def _current_log_size_locked(self) -> int:
        size = 0
        for path in (self.md_path, self.jsonl_path, self.vec_path):
            if path.exists():
                try:
                    size += path.stat().st_size
                except OSError:
                    continue
        return size

    def _next_archive_dir_locked(self, base_label: str) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        label = slug(base_label or "session")
        candidate = self.archive_root / f"{timestamp}_{label}"
        counter = 1
        while candidate.exists():
            counter += 1
            candidate = self.archive_root / f"{timestamp}_{label}_{counter:02d}"
        candidate.mkdir(parents=True, exist_ok=False)
        return candidate

    def _archive_current_logs_locked(self, reason: str, previous_token: Optional[str]) -> Optional[Path]:
        if not self._has_existing_logs_locked():
            for path in (self.md_path, self.jsonl_path, self.vec_path):
                if path.exists():
                    path.unlink()
            self._entry_count = 0
            return None

        base_label = previous_token or self.session_token or self.session_dir.name
        archive_dir = self._next_archive_dir_locked(base_label)
        metadata = {
            "reason": reason,
            "archived_at": datetime.now(UTC).isoformat(),
            "session_token": previous_token or self.session_token,
            "source": str(self.session_dir),
            "entry_count": self._entry_count,
            "total_bytes": self._current_log_size_locked(),
        }

        for path in (self.md_path, self.jsonl_path, self.vec_path):
            if path.exists():
                shutil.move(str(path), archive_dir / path.name)

        (archive_dir / "meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        self._mirror_archive_to_repo(archive_dir)

        self._entry_count = 0
        self._write_header_unlocked()
        return archive_dir

    def _rollover_if_needed_locked(self, reason: str) -> None:
        trigger = False
        if self.max_entries and self._entry_count >= self.max_entries:
            trigger = True
        elif self.max_bytes and self._current_log_size_locked() >= self.max_bytes:
            trigger = True

        if trigger:
            self._archive_current_logs_locked(reason, self.session_token)
            if self.session_token:
                self._write_session_token_locked(self.session_token)

    def _write_header(self):
        with self.lock:
            self._write_header_unlocked()

    def append(
        self,
        role: str,
        text: str,
        images: List[Path],
        *,
        references: Optional[List[Dict[str, str]]] = None,
    ):
        ts = _utc_iso()
        rec: Dict[str, Any] = {"timestamp": ts, "role": role, "text": text}
        if references:
            rec["references"] = references
        with self.lock:
            self._rollover_if_needed_locked("length-threshold")
            self._ensure_header_locked()

            with self.md_path.open("a", encoding="utf-8") as f:
                lab = "User" if role == "user" else ("Assistant" if role == "assistant" else "System")
                f.write(f"\n**{lab}:**\n\n{text}\n\n")
                for ip in images:
                    f.write(f"![image](images/{ip.name})\n")

            with self.jsonl_path.open("a", encoding="utf-8") as jf:
                jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            self._entry_count += 1

            if self.enable_embeddings and text.strip():
                ok, vec, _ = self.ollama.embeddings(self.embedder, text)
                if ok and isinstance(vec, list):
                    with self.vec_path.open("a", encoding="utf-8") as vf:
                        vf.write(json.dumps(vec) + "\n")

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self.enable_embeddings or not self.jsonl_path.exists() or not self.vec_path.exists():
            return []
        ok, qvec, _ = self.ollama.embeddings(self.embedder, query)
        if not ok:
            return []
        entries: List[Tuple[Dict[str, Any], List[float]]] = []
        with self.jsonl_path.open("r", encoding="utf-8") as jf, self.vec_path.open("r", encoding="utf-8") as vf:
            for jline, vline in zip(jf, vf):
                try:
                    rec = json.loads(jline)
                    vec = json.loads(vline)
                    if isinstance(vec, list):
                        entries.append((rec, vec))
                except Exception:
                    continue
        scored = [(cosine(qvec, vec), rec) for rec, vec in entries]
        scored.sort(key=lambda t: t[0], reverse=True)
        return [rec for _, rec in scored[:k]]

    def resolve_conversation(self, identifier: str) -> Optional[ConversationPaths]:
        conv_id = (identifier or "").strip()
        if not conv_id:
            return None
        with self.lock:
            live_token = self.session_token or self._read_session_token()
        if live_token == conv_id:
            return ConversationPaths(
                identifier=conv_id,
                root=self.session_dir,
                jsonl_path=self.jsonl_path,
                markdown_path=self.md_path,
                source="live",
                meta_path=self.session_meta_path if self.session_meta_path.exists() else None,
            )

        slug_id = slug(conv_id)
        try:
            candidates = sorted((p for p in self.archive_root.iterdir() if p.is_dir()), reverse=True)
        except FileNotFoundError:
            return None

        for candidate in candidates:
            meta_path = candidate / "meta.json"
            token = ""
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    raw = meta.get("session_token") or meta.get("session_id") or meta.get("token")
                    if isinstance(raw, str):
                        token = raw.strip()
                except Exception:
                    token = ""
            if token == conv_id or (slug_id and slug_id in candidate.name):
                return ConversationPaths(
                    identifier=conv_id,
                    root=candidate,
                    jsonl_path=candidate / "conversation.jsonl",
                    markdown_path=candidate / "conversation.md",
                    source="archive",
                    meta_path=meta_path if meta_path.exists() else None,
                )
        return None

    def recent(self, k: int = 5) -> List[Dict[str, Any]]:
        if not self.jsonl_path.exists() or k <= 0:
            return []
        from collections import deque
        dq = deque(maxlen=k)
        with self.jsonl_path.open("r", encoding="utf-8") as jf:
            for line in jf:
                dq.append(line)
        recs: List[Dict[str, Any]] = []
        for line in dq:
            try:
                recs.append(json.loads(line))
            except Exception:
                continue
        return recs

# --------------------------------------------------------------------------------------
# Codex Bootstrap + Bridge (Windows)
# --------------------------------------------------------------------------------------

def sha256_file(p: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

DEFAULT_SETTINGS = {
    "default_launch_mode": "bridge",
    "working_folder": str(transit_dir()),
    "model": DEFAULT_CHAT_MODEL,
    "enable_interpreter": False,
    "reference_embed_contents": True,
    "reference_case_sensitive": False,
    "reference_token_guard": True,
    "reference_token_headroom": 80,
    "scan_roots": [],
    "terminal_desktop": {
        "width": 980,
        "height": 620,
        "x": -1,
        "y": -1,
        "icon_size": "medium",
        "sort_mode": "name",
        "icon_positions": {},
        "background": BackgroundConfig().to_state(),
    },
    "sandbox": {
        "level": "restricted",
        "approval_policy": "require_approval",
        "full_auto": False,
        "encryption_enabled": False,
        "access_control_enforced": False,
    },
}


def _merge_settings(defaults: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in defaults.items():
        if isinstance(value, dict):
            node = target.get(key)
            if isinstance(node, dict):
                _merge_settings(value, node)
            else:
                target[key] = copy.deepcopy(value)
        elif isinstance(value, list):
            existing = target.get(key)
            if not isinstance(existing, list):
                target[key] = list(value)
        else:
            target.setdefault(key, value)
    return target


def _is_transit_path(candidate: str) -> bool:
    if not candidate:
        return False
    try:
        path = Path(candidate).expanduser().resolve()
    except Exception:
        return False
    targets = [workspace_root() / "Terminal Desktop"] + _legacy_transit_candidates()
    for target in targets:
        try:
            if path == target.expanduser().resolve():
                return True
        except Exception:
            pass
        if str(path) == str(target):
            return True
    return False


def _normalize_scan_roots(raw: Any) -> List[str]:
    roots: List[str] = []
    if isinstance(raw, (list, tuple)):
        seen: Set[str] = set()
        for entry in raw:
            if not entry:
                continue
            try:
                normalized = str(Path(entry).expanduser().resolve())
            except Exception:
                normalized = str(entry)
            if normalized in seen:
                continue
            seen.add(normalized)
            roots.append(normalized)
    return roots


def load_codex_settings() -> dict:
    workspace = str(transit_dir())
    if SETTINGS_JSON.exists():
        migrated = False
        try:
            obj = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                if "enable_interpreter" not in obj and "codex_auto_continue" in obj:
                    obj["enable_interpreter"] = bool(obj.get("codex_auto_continue", False))
                obj.pop("codex_auto_continue", None)

                raw_wf = str(obj.get("working_folder") or "").strip()
                if not raw_wf or _is_transit_path(raw_wf):
                    obj["working_folder"] = workspace
                    migrated = True

                obj["scan_roots"] = _normalize_scan_roots(obj.get("scan_roots"))

                merged = _merge_settings(DEFAULT_SETTINGS, obj)
                if migrated:
                    SETTINGS_JSON.write_text(json.dumps(merged, indent=2), encoding="utf-8")
                return merged
        except Exception:
            pass
    DEFAULT_SETTINGS["working_folder"] = workspace
    DEFAULT_SETTINGS["scan_roots"] = []
    SETTINGS_JSON.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding="utf-8")
    return copy.deepcopy(DEFAULT_SETTINGS)

def save_codex_settings(d: dict) -> None:
    payload = dict(d)
    payload["scan_roots"] = _normalize_scan_roots(payload.get("scan_roots"))
    SETTINGS_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

_READY_PATTERNS = [
    r"You are using OpenAI Codex",
    r"/status\s+-\s+show current session configuration",
    r"Ctrl\+J newline",
]
def codex_ready_banner(text: str) -> bool:
    if not text: return False
    for pat in _READY_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

# ---- Windows console helpers ----
if is_windows():
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    # Find visible console window for PID (best-effort)
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    GetWindowThreadProcessId.restype  = wintypes.DWORD
    EnumWindows = user32.EnumWindows
    EnumWindows.argtypes = [ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM), wintypes.LPARAM]
    EnumWindows.restype  = wintypes.BOOL
    IsWindowVisible = user32.IsWindowVisible
    IsWindowVisible.argtypes = [wintypes.HWND]
    IsWindowVisible.restype  = wintypes.BOOL
    ShowWindow = user32.ShowWindow
    ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    SetForegroundWindow = user32.SetForegroundWindow
    SetForegroundWindow.argtypes = [wintypes.HWND]
    GetForegroundWindow = user32.GetForegroundWindow
    GetForegroundWindow.restype = wintypes.HWND
    GetWindowThreadProcessId.restype = wintypes.DWORD
    AttachThreadInput = user32.AttachThreadInput
    AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
    GetCurrentThreadId = kernel32.GetCurrentThreadId

    SW_MINIMIZE, SW_RESTORE = 6, 9

    # Console attach/io
    ATTACH_PARENT_PROCESS = ctypes.c_uint(-1).value
    AttachConsole = kernel32.AttachConsole
    AttachConsole.argtypes = [wintypes.DWORD]
    FreeConsole = kernel32.FreeConsole
    FreeConsole.argtypes = []

    CreateFileW = kernel32.CreateFileW
    CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    CreateFileW.restype  = wintypes.HANDLE

    GENERIC_READ, GENERIC_WRITE = 0x80000000, 0x40000000
    FILE_SHARE_READ, FILE_SHARE_WRITE = 0x1, 0x2
    OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL = 3, 0x80
    INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

    class COORD(ctypes.Structure):
        _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]
    class SMALL_RECT(ctypes.Structure):
        _fields_ = [("Left", wintypes.SHORT), ("Top", wintypes.SHORT), ("Right", wintypes.SHORT), ("Bottom", wintypes.SHORT)]
    class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
        _fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD), ("wAttributes", wintypes.WORD), ("srWindow", SMALL_RECT), ("dwMaximumWindowSize", COORD)]
    GetConsoleScreenBufferInfo = kernel32.GetConsoleScreenBufferInfo
    GetConsoleScreenBufferInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(CONSOLE_SCREEN_BUFFER_INFO)]
    ReadConsoleOutputCharacterW = kernel32.ReadConsoleOutputCharacterW
    ReadConsoleOutputCharacterW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, COORD, ctypes.POINTER(wintypes.DWORD)]
    CloseHandle = kernel32.CloseHandle

    KEY_EVENT = 0x0001
    VK_RETURN = 0x0D
    ENABLE_MOUSE_INPUT = 0x0010
    ENABLE_QUICK_EDIT_MODE = 0x0040
    ENABLE_EXTENDED_FLAGS = 0x0080
    GetConsoleMode = kernel32.GetConsoleMode
    GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    SetConsoleMode = kernel32.SetConsoleMode
    SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]

    class _CHAR_UNION(ctypes.Union):
        _fields_ = [("UnicodeChar", wintypes.WCHAR)]
    class KEY_EVENT_RECORD(ctypes.Structure):
        _fields_ = [("bKeyDown", wintypes.BOOL), ("wRepeatCount", wintypes.WORD),
                    ("wVirtualKeyCode", wintypes.WORD), ("wVirtualScanCode", wintypes.WORD),
                    ("uChar", _CHAR_UNION), ("dwControlKeyState", wintypes.DWORD)]
    class _EVENT_UNION(ctypes.Union):
        _fields_ = [("KeyEvent", KEY_EVENT_RECORD)]
    class INPUT_RECORD(ctypes.Structure):
        _fields_ = [("EventType", wintypes.WORD), ("Event", _EVENT_UNION)]
    WriteConsoleInputW = kernel32.WriteConsoleInputW
    WriteConsoleInputW.argtypes = [wintypes.HANDLE, ctypes.POINTER(INPUT_RECORD), wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]

    # SendInput fallback (foreground)
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_void_p)]
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_void_p)]
    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]
    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("ki", KEYBDINPUT)]
    SendInput = user32.SendInput
    SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002

    def _sendinput_vk(vk: int):
        arr = (INPUT * 2)(
            INPUT(INPUT_KEYBOARD, KEYBDINPUT(vk, 0, 0, 0, None)),
            INPUT(INPUT_KEYBOARD, KEYBDINPUT(vk, 0, KEYEVENTF_KEYUP, 0, None)),
        )
        SendInput(2, arr, ctypes.sizeof(INPUT))

    def _find_hwnd_by_pid(pid: int) -> int:
        res = {"hwnd": 0}
        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def cb(hwnd, _):
            if not IsWindowVisible(hwnd): return True
            p = wintypes.DWORD(0)
            GetWindowThreadProcessId(hwnd, ctypes.byref(p))
            if int(p.value) == int(pid):
                res["hwnd"] = hwnd
                return False
            return True
        EnumWindows(cb, 0)
        return int(res["hwnd"])

    def _attach(pid: int) -> bool:
        FreeConsole()
        if AttachConsole(int(pid)):
            return True
        time.sleep(0.05)
        return bool(AttachConsole(int(pid)))

    def _open_conout_read() -> int:
        return CreateFileW("CONOUT$", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)

    def _open_conin_write() -> int:
        return CreateFileW("CONIN$", GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)

    def read_console_snapshot(pid: int) -> str:
        if not _attach(pid): return ""
        try:
            h = _open_conout_read()
            if int(h) == INVALID_HANDLE_VALUE: return ""
            try:
                csbi = CONSOLE_SCREEN_BUFFER_INFO()
                if not GetConsoleScreenBufferInfo(h, ctypes.byref(csbi)): return ""
                width, height = int(csbi.dwSize.X), int(csbi.dwSize.Y)
                buf = []
                for y in range(height):
                    coord = COORD(0, y)
                    count = ctypes.wintypes.DWORD(0)
                    tmp = ctypes.create_unicode_buffer(width)
                    ok = ReadConsoleOutputCharacterW(h, tmp, width, coord, ctypes.byref(count))
                    if not ok: break
                    s = tmp.value.rstrip("\x00").rstrip()
                    if s:
                        buf.append(s)
                return ("\n".join(buf).rstrip() + "\n")
            finally:
                CloseHandle(h)
        finally:
            FreeConsole()

    def _records_for_text_only(text: str) -> list[INPUT_RECORD]:
        recs: list[INPUT_RECORD] = []
        def push_char(ch: str):
            # Try to include proper VK for letters/numbers? For simplicity, rely on UnicodeChar.
            ke_down = KEY_EVENT_RECORD(True, 1, ord(ch.upper()) if ch.isalpha() else 0, 0, _CHAR_UNION(ch), 0)
            ke_up   = KEY_EVENT_RECORD(False,1, ord(ch.upper()) if ch.isalpha() else 0, 0, _CHAR_UNION(ch), 0)
            r1 = INPUT_RECORD(KEY_EVENT, _EVENT_UNION()); r1.Event.KeyEvent = ke_down
            r2 = INPUT_RECORD(KEY_EVENT, _EVENT_UNION()); r2.Event.KeyEvent = ke_up
            recs.append(r1); recs.append(r2)
        for ch in text:
            push_char(ch)
        return recs

    def _records_for_enter() -> list[INPUT_RECORD]:
        down = KEY_EVENT_RECORD(True, 1, VK_RETURN, 0, _CHAR_UNION('\r'), 0)
        up   = KEY_EVENT_RECORD(False,1, VK_RETURN, 0, _CHAR_UNION('\r'), 0)
        r1 = INPUT_RECORD(KEY_EVENT, _EVENT_UNION()); r1.Event.KeyEvent = down
        r2 = INPUT_RECORD(KEY_EVENT, _EVENT_UNION()); r2.Event.KeyEvent = up
        return [r1, r2]

    def write_console_input_text(pid: int, text: str) -> bool:
        if not _attach(pid): return False
        try:
            h = _open_conin_write()
            if int(h) == INVALID_HANDLE_VALUE: return False
            try:
                mode = ctypes.wintypes.DWORD(0)
                if GetConsoleMode(h, ctypes.byref(mode)):
                    new_mode = mode.value
                    new_mode &= ~(ENABLE_QUICK_EDIT_MODE | ENABLE_MOUSE_INPUT)
                    new_mode |= ENABLE_EXTENDED_FLAGS
                    SetConsoleMode(h, new_mode)
                recs = _records_for_text_only(text)
                if not recs: return True
                arr = (INPUT_RECORD * len(recs))(*recs)
                written = ctypes.wintypes.DWORD(0)
                ok = WriteConsoleInputW(h, arr, len(recs), ctypes.byref(written))
                return bool(ok) and written.value == len(recs)
            finally:
                CloseHandle(h)
        finally:
            FreeConsole()

    def write_console_input_enter(pid: int) -> bool:
        if not _attach(pid): return False
        try:
            h = _open_conin_write()
            if int(h) == INVALID_HANDLE_VALUE: return False
            try:
                mode = ctypes.wintypes.DWORD(0)
                if GetConsoleMode(h, ctypes.byref(mode)):
                    new_mode = mode.value
                    new_mode &= ~(ENABLE_QUICK_EDIT_MODE | ENABLE_MOUSE_INPUT)
                    new_mode |= ENABLE_EXTENDED_FLAGS
                    SetConsoleMode(h, new_mode)
                recs = _records_for_enter()
                arr = (INPUT_RECORD * len(recs))(*recs)
                written = ctypes.wintypes.DWORD(0)
                ok = WriteConsoleInputW(h, arr, len(recs), ctypes.byref(written))
                return bool(ok) and written.value == len(recs)
            finally:
                CloseHandle(h)
        finally:
            FreeConsole()

    def foreground_enter_fallback(hwnd_cmd: int, hwnd_restore: int):
        """Briefly foreground CMD, send Enter, then restore focus."""
        if not hwnd_cmd:
            return
        tid_cmd = user32.GetWindowThreadProcessId(hwnd_cmd, None)
        cur_tid = GetCurrentThreadId()
        AttachThreadInput(cur_tid, tid_cmd, True)
        try:
            ShowWindow(hwnd_cmd, SW_RESTORE)
            SetForegroundWindow(hwnd_cmd)
            time.sleep(0.02)
            _sendinput_vk(VK_RETURN)
            time.sleep(0.02)
            if hwnd_restore:
                SetForegroundWindow(hwnd_restore)
        finally:
            AttachThreadInput(cur_tid, tid_cmd, False)

    def show_window_by_pid(pid: int, how: int):
        hwnd = _find_hwnd_by_pid(pid)
        if hwnd:
            ShowWindow(hwnd, how)
else:
    def read_console_snapshot(pid: int) -> str: return ""
    def write_console_input_text(pid: int, text: str) -> bool: return False
    def write_console_input_enter(pid: int) -> bool: return False
    def foreground_enter_fallback(hwnd_cmd: int, hwnd_restore: int): return
    def show_window_by_pid(pid: int, how: int): return
    def _find_hwnd_by_pid(pid: int) -> int: return 0

class CodexBootstrap:
    def __init__(self, ollama: OllamaClient):
        self.ollama = ollama

    def ensure_ollama(self) -> None:
        ok, _ = self.ollama.health()
        if ok: return
        raise RuntimeError("Ollama not reachable at http://127.0.0.1:11434")

    def download_with_progress(self, url: str, dest: Path, progress_cb=None, chunk: int = 128 * 1024) -> Path:
        from urllib import request
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with request.urlopen(req, timeout=60) as r, tmp.open("wb") as f:
            total = int(r.headers.get("Content-Length") or 0)
            read = 0
            while True:
                buf = r.read(chunk)
                if not buf: break
                f.write(buf)
                read += len(buf)
                if progress_cb and total:
                    progress_cb(int(read * 100 / total))
        tmp.replace(dest)
        return dest

    def extract_zip(self, zip_path: Path, out_dir: Path) -> Path:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(out_dir)
        for p in out_dir.iterdir():
            if p.suffix.lower() == ".exe" and "codex" in p.name.lower():
                return p
        raise FileNotFoundError("codex exe not found after extraction")

    def ensure_release(self, progress_cb=None) -> Path:
        if DEFAULT_CODEX_EXE.exists():
            return DEFAULT_CODEX_EXE
        root = transit_dir()
        zip_path = root / ASSET_ZIP
        self.download_with_progress(ASSET_URL, zip_path, progress_cb=progress_cb)
        digest = sha256_file(zip_path)
        if digest.lower() != ASSET_ZIP_SHA256.lower():
            raise RuntimeError("SHA-256 mismatch for downloaded zip.")
        exe = self.extract_zip(zip_path, root)
        return exe

    def codex_version(self, bin_path: Path) -> str:
        try:
            out = subprocess.run([str(bin_path), "--version"], capture_output=True, text=True, timeout=8)
            return (out.stdout or out.stderr or "").strip()
        except Exception as e:
            return f"(version check failed: {e})"

    def write_config_toml(self, model: str) -> Path:
        cfg_dir = Path.home() / ".codex"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        cfg = cfg_dir / "config.toml"
        txt = (
            f'model = "{model}"\n'
            f'model_provider = "ollama"\n\n'
            f'[model_providers.ollama]\n'
            f'name = "Ollama"\n'
            f'base_url = "http://127.0.0.1:11434/v1"\n'
            f'wire_api = "chat"\n'
        )
        cfg.write_text(txt, encoding="utf-8")
        return cfg

    def write_install_manifest(self, selected_model: str, exe_path: Path) -> Path:
        version = self.codex_version(exe_path)
        cfg = self.write_config_toml(selected_model)
        lines = [
            f"# Install Manifest and Integration Guide\n",
            f"**Generated:** {datetime.now().isoformat(sep=' ', timespec='seconds')}\n",
            f"**Transit:** `{transit_dir()}`\n",
            f"**Binary:** `{exe_path}`\n",
            f"**Config:** `{cfg}`\n",
            f"**Codex version:** `{version}`\n",
        ]
        out = INSTALL_MANIFEST
        out.write_text("\n".join(lines), encoding="utf-8")
        return out

    def launch_codex_cmd(self, exe: Path, model: str, cwd: Path) -> subprocess.Popen:
        title = f"CODEX_CMD_{int(time.time())}"
        # Launch a new console window running CMD, then codex
        proc = subprocess.Popen(["cmd", "/k", "title", title, "&&", str(exe), "--model", model],
                                cwd=str(cwd), creationflags=subprocess.CREATE_NEW_CONSOLE)
        return proc

class CodexBridge:
    """Mirrors Codex CMD, injects text and **presses Enter**."""

    def __init__(self, status_append_fn, led_setter_fn, output_append_fn):
        self._pid: Optional[int] = None
        self._running = False
        self._stop_evt = threading.Event()
        self._busy_evt = threading.Event()
        self._last_hash = ""
        self._last_snapshot = ""
        self._last_injected: Optional[str] = None
        self._status = status_append_fn       # callable(str)
        self._set_led = led_setter_fn         # callable(str)
        self._output = output_append_fn       # callable(str)
        self._ready_seen = False

    @property
    def pid(self) -> Optional[int]: return self._pid
    def running(self) -> bool: return self._running

    def attach(self, pid: int):
        self._pid = int(pid)

    def start(self):
        if not self._pid: return
        self._stop_evt.clear()
        self._running = True
        self._set_led("yellow")
        threading.Thread(target=self._idle_loop, daemon=True).start()

    def stop(self):
        self._stop_evt.set()
        self._running = False
        self._set_led("red")
        self._last_injected = None

    def show(self): 
        if self._pid: show_window_by_pid(self._pid, SW_RESTORE if is_windows() else 9)
    def hide(self): 
        if self._pid: show_window_by_pid(self._pid, SW_MINIMIZE if is_windows() else 6)

    # --- text then Enter (two steps) ---
    def send_text(self, text: str) -> bool:
        if not self._pid: return False
        ok = write_console_input_text(self._pid, text)
        if ok:
            self._busy_evt.set()
            self._last_injected = text
            self._status("[Codex] Text injected.")
        else:
            self._last_injected = None
            self._status("[Codex] Text injection failed.")
            self._set_led("red")
        return ok

    def press_enter_async(self, hwnd_ui: int):
        if not self._pid: return
        threading.Thread(target=self._press_enter_sequence, args=(hwnd_ui,), daemon=True).start()

    def busy(self) -> bool:
        return self._busy_evt.is_set()

    def _press_enter_sequence(self, hwnd_ui: int):
        # Try primary (console input)
        ok = write_console_input_enter(self._pid)
        if not ok:
            # Fallback: brief foreground hop
            hwnd_cmd = _find_hwnd_by_pid(self._pid) if is_windows() else 0
            foreground_enter_fallback(hwnd_cmd, hwnd_ui)
        self._status("[Codex] Enter sent.")
        threading.Thread(target=self._settle_loop, daemon=True).start()

    # --- loops ---
    def _idle_loop(self):
        while not self._stop_evt.is_set():
            if self._busy_evt.is_set():
                time.sleep(0.2); continue
            snap = read_console_snapshot(self._pid)
            if snap:
                if snap != self._last_snapshot:
                    old_lines = self._last_snapshot.splitlines()
                    new_lines = snap.splitlines()
                    if len(new_lines) > len(old_lines):
                        delta = "\n".join(new_lines[len(old_lines):])
                        if delta:
                            if self._last_injected:
                                injected = self._last_injected.strip().lower()
                                if delta.strip().lower() == injected:
                                    self._last_injected = None
                                    delta = ""
                            if delta:
                                self._output(delta)
                                self._last_injected = None
                    self._last_snapshot = snap
                digest = hashlib.sha256(snap.encode("utf-8", "replace")).hexdigest()
                if digest != self._last_hash:
                    self._last_hash = digest
                    if codex_ready_banner(snap) and not self._ready_seen:
                        self._ready_seen = True
                        self._set_led("green")
                        self._status("[Codex] Ready.")
            time.sleep(0.9)

    def _settle_loop(self):
        last = ""
        last_change = time.time()
        while not self._stop_evt.is_set():
            snap = read_console_snapshot(self._pid)
            if snap != last:
                last = snap; last_change = time.time()
            if time.time() - last_change > 1.2:
                self._busy_evt.clear()
                if codex_ready_banner(last):
                    self._set_led("green")
                return
            time.sleep(0.16)

# --------------------------------------------------------------------------------------
# Settings dialog (models + codex quick defaults)
# --------------------------------------------------------------------------------------

class SettingsDialog(QDialog):
    def __init__(self, theme: Theme, parent: Optional[QWidget], ollama: OllamaClient, lex_mgr: LexiconManager):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(920, 680)
        self.theme = theme
        self.ollama = ollama
        self.lex_mgr = lex_mgr

        layout = QVBoxLayout(self)

        # Models
        models_box = QGroupBox("Models (Local Ollama only)")
        self.chat_model = QComboBox(models_box)
        self.vision_ocr_model = QComboBox(models_box)
        self.vision_model = QComboBox(models_box)
        self.embed_model = QComboBox(models_box)
        self.context_pairs = QSlider(Qt.Horizontal, models_box)
        self.context_pairs.setMinimum(1); self.context_pairs.setMaximum(100); self.context_pairs.setValue(25)
        self.context_val = QLabel("25", models_box)
        self.share_context = QCheckBox("Share conversation context", models_box)
        self.share_limit = QSpinBox(models_box); self.share_limit.setRange(1, 50); self.share_limit.setValue(5)
        self.enable_embeddings = QCheckBox("Enable embeddings", models_box)
        self.enable_vision = QCheckBox("Enable vision (OCR + summary)", models_box)
        mform = QFormLayout(models_box)
        mform.addRow("Chat", self.chat_model)
        mform.addRow("Vision-OCR (markdown)", self.vision_ocr_model)
        mform.addRow("Vision (creative)", self.vision_model)
        mform.addRow("Embeddings", self.embed_model)
        mform.addRow("History depth", self.context_pairs)
        mform.addRow("", self.context_val)
        mform.addRow(self.share_context)
        mform.addRow("Context limit", self.share_limit)
        mform.addRow(self.enable_embeddings)
        mform.addRow(self.enable_vision)

        # Shells
        shells_box = QGroupBox("Shells")
        self.chk_cmd = QCheckBox("CMD", shells_box)
        self.chk_powershell = QCheckBox("PowerShell", shells_box)
        self.chk_bash = QCheckBox("Bash", shells_box)
        self.chk_zsh = QCheckBox("Zsh", shells_box)
        self.chk_wsl = QCheckBox("WSL Ubuntu", shells_box)
        slyt = QVBoxLayout(shells_box)
        for w in (self.chk_cmd, self.chk_powershell, self.chk_bash, self.chk_zsh, self.chk_wsl):
            slyt.addWidget(w)

        # Data
        data_box = QGroupBox("Data")
        self.data_root_edit = QLineEdit(str(agent_data_dir()), data_box)
        self.data_root_btn = QPushButton("Browse…", data_box)
        dform = QFormLayout(data_box)
        dform.addRow("Data Root", self._row(self.data_root_edit, self.data_root_btn))

        def _browse_data_root():
            p = QFileDialog.getExistingDirectory(self, "Pick data root", str(agent_data_dir()))
            if p: self.data_root_edit.setText(p)
        self.data_root_btn.clicked.connect(_browse_data_root)

        # Codex defaults
        codex_box = QGroupBox("Codex Defaults")
        codex_box.setObjectName("CodexDefaultsBox")
        self.codex_mode_bridge = QCheckBox("Default launch: Codex + Bridge", codex_box); self.codex_mode_bridge.setChecked(True)
        self.codex_working = QLineEdit(str(workspace_root()), codex_box)
        browse = QPushButton("Browse…", codex_box)
        self.enable_interpreter = ToggleSwitch(theme, codex_box)
        self.enable_interpreter.setObjectName("InterpreterSwitch")
        self.enable_interpreter.setToolTip(
            "When enabled, Codex automatically sends follow-up commands whenever the interpreter detects"
            " a continuation or actionable plan in the bridge output."
        )
        self.reference_embed_contents = QCheckBox(
            "Embed reference contents in chat", codex_box
        )
        self.reference_embed_contents.setToolTip(
            "Automatically attach referenced file contents when inserting workspace references."
        )
        self.reference_case_sensitive = QCheckBox(
            "Match references with case sensitivity", codex_box
        )
        self.reference_case_sensitive.setToolTip(
            "Only surface reference suggestions that respect the exact casing of your query."
        )
        self.reference_token_guard = QCheckBox(
            "Guard reference inserts with token safety", codex_box
        )
        self.reference_token_guard.setToolTip(
            "Prevents oversized reference payloads from being inserted when token budgets are tight."
        )
        self.reference_token_headroom = QSpinBox(codex_box)
        self.reference_token_headroom.setRange(10, 100)
        self.reference_token_headroom.setValue(
            DEFAULT_SETTINGS.get("reference_token_headroom", 80)
        )
        self.reference_token_headroom.setSuffix("%")
        self.reference_token_headroom.setToolTip(
            "Percentage of the model's context window available for prompts before attaching reference contents."
        )

        def _pick():
            p = QFileDialog.getExistingDirectory(self, "Pick working folder", str(workspace_root()))
            if p:
                self.codex_working.setText(p)

        browse.clicked.connect(_pick)

        codex_layout = QVBoxLayout(codex_box)
        codex_layout.setContentsMargins(12, 12, 12, 12)
        codex_layout.setSpacing(12)

        cf = QFormLayout()
        cf.addRow(self.codex_mode_bridge)
        interpreter_row = QWidget(codex_box)
        interpreter_layout = QHBoxLayout(interpreter_row)
        interpreter_layout.setContentsMargins(0, 0, 0, 0)
        interpreter_layout.setSpacing(6)
        interpreter_layout.addWidget(self.enable_interpreter, 0, Qt.AlignLeft)
        interpreter_layout.addStretch(1)
        cf.addRow("Interpreter automation", interpreter_row)
        roww = QWidget()
        rw = QHBoxLayout(roww)
        rw.setContentsMargins(0, 0, 0, 0)
        rw.addWidget(self.codex_working, 1)
        rw.addWidget(browse)
        cf.addRow("Working folder:", roww)

        scan_widget = QWidget(codex_box)
        scan_layout = QVBoxLayout(scan_widget)
        scan_layout.setContentsMargins(0, 0, 0, 0)
        scan_layout.setSpacing(6)
        self.scan_roots_list = QListWidget(scan_widget)
        self.scan_roots_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        scan_layout.addWidget(self.scan_roots_list)

        scan_btns = QHBoxLayout()
        scan_btns.setContentsMargins(0, 0, 0, 0)
        scan_btns.setSpacing(6)
        self.scan_root_add = QPushButton("Add…", scan_widget)
        self.scan_root_remove = QPushButton("Remove", scan_widget)
        self.scan_root_remove.setEnabled(False)
        scan_btns.addWidget(self.scan_root_add)
        scan_btns.addWidget(self.scan_root_remove)
        scan_btns.addStretch(1)
        scan_layout.addLayout(scan_btns)

        self.scan_root_add.clicked.connect(self._on_add_scan_root)
        self.scan_root_remove.clicked.connect(self._on_remove_selected_scan_roots)
        self.scan_roots_list.itemSelectionChanged.connect(self._update_scan_root_remove_enabled)

        cf.addRow("Additional scan roots", scan_widget)
        cf.addRow(self.reference_embed_contents)
        cf.addRow(self.reference_case_sensitive)
        cf.addRow(self.reference_token_guard)
        cf.addRow("Reference token headroom", self.reference_token_headroom)
        codex_layout.addLayout(cf)

        sandbox_box = QGroupBox("Sandbox")
        sandbox_box.setObjectName("SandboxBox")
        sb_layout = QVBoxLayout(sandbox_box)
        sb_layout.setContentsMargins(12, 12, 12, 12)
        sb_layout.setSpacing(10)

        self.sandbox_level = QComboBox(sandbox_box)
        self.sandbox_level.addItem("Isolated (maximum containment)", "isolated")
        self.sandbox_level.addItem("Restricted (balanced)", "restricted")
        self.sandbox_level.addItem("Trusted (broad access)", "trusted")

        self.sandbox_policy = QComboBox(sandbox_box)
        self.sandbox_policy.addItem("Require approval for all actions", "require_approval")
        self.sandbox_policy.addItem("Auto-approve safe actions", "auto_safe")
        self.sandbox_policy.addItem("Auto-approve trusted workflows", "auto_trust")

        self.sandbox_full_auto = QCheckBox("Enable full auto mode", sandbox_box)
        self.sandbox_level.currentIndexChanged.connect(self._update_scan_roots_enabled)

        sandbox_form = QFormLayout()
        sandbox_form.addRow("Level", self.sandbox_level)
        sandbox_form.addRow("Approval policy", self.sandbox_policy)
        sandbox_form.addRow(self.sandbox_full_auto)
        sb_layout.addLayout(sandbox_form)

        status_header = QLabel("Safety status", sandbox_box)
        status_header.setObjectName("SandboxStatusHeader")
        sb_layout.addWidget(status_header)

        status_form = QFormLayout()
        self.sandbox_ollama_status = QLabel("", sandbox_box)
        self.sandbox_encryption_status = QLabel("", sandbox_box)
        self.sandbox_access_status = QLabel("", sandbox_box)
        for label in (self.sandbox_ollama_status, self.sandbox_encryption_status, self.sandbox_access_status):
            label.setObjectName("SandboxStatusValue")
            label.setWordWrap(True)
        status_form.addRow("Ollama connection", self.sandbox_ollama_status)
        status_form.addRow("Encryption", self.sandbox_encryption_status)
        status_form.addRow("Access control", self.sandbox_access_status)
        sb_layout.addLayout(status_form)
        sb_layout.addStretch(1)

        sandbox_box.setStyleSheet(
            f"""
            QGroupBox#SandboxBox {{
                background-color: {self.theme.card_bg};
                border: 1px solid {self.theme.card_border};
                border-radius: {self.theme.card_radius}px;
                margin-top: 4px;
                padding-top: 18px;
            }}
            QGroupBox#SandboxBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 12px;
                color: {self.theme.header_text};
                font-weight: 600;
            }}
            QLabel#SandboxStatusHeader {{
                color: {self.theme.think_text};
                font-weight: 600;
            }}
            QLabel#SandboxStatusValue {{
                font-weight: 600;
            }}
            """
        )

        self._sandbox_encryption_enabled = False
        self._sandbox_access_control_enforced = False
        codex_layout.addWidget(sandbox_box)
        codex_layout.addStretch(1)

        self.update_sandbox_status(
            ollama_ok=False,
            ollama_detail="Status unknown",
            encryption_enabled=False,
            access_control_enabled=False,
        )

        self._update_scan_roots_enabled()

        prompts_box = QWidget(self)
        pb_layout = QVBoxLayout(prompts_box)
        pb_layout.setContentsMargins(12, 12, 12, 12)
        pb_layout.setSpacing(12)
        intro = QLabel(
            "Prompt files live in the prompts/ directory. Base text defines the persona and "
            "overlay files append additional guidance without editing the default instructions.",
            prompts_box,
        )
        intro.setWordWrap(True)
        pb_layout.addWidget(intro)

        for definition in iter_prompt_definitions():
            row = QFrame(prompts_box)
            row.setObjectName("PromptRow")
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(12, 12, 12, 12)
            row_layout.setSpacing(6)

            title = QLabel(definition.title, row)
            title.setObjectName("PromptTitle")
            title.setWordWrap(True)
            desc = QLabel(definition.description, row)
            desc.setObjectName("PromptDesc")
            desc.setWordWrap(True)

            btn_row = QHBoxLayout()
            base_btn = QPushButton("Open Base", row)
            base_btn.setToolTip(str(definition.base_path))
            base_btn.clicked.connect(lambda _=False, p=definition.base_path: self._open_prompt_path(p, ensure_exists=True))
            overlay_btn = QPushButton("Open Overlay", row)
            overlay_btn.setToolTip(str(definition.overlay_path))
            overlay_btn.clicked.connect(lambda _=False, p=definition.overlay_path: self._open_prompt_path(p, ensure_exists=True))
            btn_row.addWidget(base_btn)
            btn_row.addWidget(overlay_btn)
            btn_row.addStretch(1)

            row_layout.addWidget(title)
            row_layout.addWidget(desc)
            row_layout.addLayout(btn_row)

            row.setStyleSheet(
                """
                QFrame#PromptRow {
                    background-color: %s;
                    border: 1px solid %s;
                    border-radius: 10px;
                }
                QFrame#PromptRow QLabel {
                    color: %s;
                }
                QFrame#PromptRow QLabel#PromptDesc {
                    color: %s;
                    font-size: 10pt;
                }
                QFrame#PromptRow QPushButton {
                    padding: 6px 12px;
                }
                """
                % (self.theme.card_bg, self.theme.card_border, self.theme.ai_text, self.theme.think_text)
            )

            pb_layout.addWidget(row)

        pb_layout.addStretch(1)

        tabs = QTabWidget(self)
        tabs.addTab(models_box, "Models")
        tabs.addTab(shells_box, "Shells")
        tabs.addTab(data_box, "Data")
        tabs.addTab(codex_box, "Codex")
        tabs.addTab(prompts_box, "Prompts")
        layout.addWidget(tabs)

        btns = QHBoxLayout()
        btns.addStretch(1)
        okb = QPushButton("OK", self); cb = QPushButton("Cancel", self)
        btns.addWidget(okb); btns.addWidget(cb)
        layout.addLayout(btns)

        self.populate_models()
        self.context_pairs.valueChanged.connect(lambda v: self.context_val.setText(str(v)))
        okb.clicked.connect(self.accept); cb.clicked.connect(self.reject)

        self.setStyleSheet(f"""
        QDialog, QWidget {{ background:{theme.card_bg}; color:{theme.header_text}; }}
        QTabWidget::pane {{ background:{theme.card_bg}; border:1px solid {theme.card_border}; }}
        QTabBar::tab {{
            background:{theme.card_bg};
            color:{theme.muted};
            padding:6px 12px;
            border:1px solid {theme.card_border};
            border-bottom:0px;
            border-top-left-radius:6px;
            border-top-right-radius:6px;
            margin-right:2px;
        }}
        QTabBar::tab:hover {{
            background:{theme.card_border};
            color:{theme.header_text};
        }}
        QTabBar::tab:selected {{
            background:{theme.accent};
            color:#ffffff;
        }}
        QGroupBox {{ border:1px solid {theme.card_border}; border-radius:8px; margin-top:14px; padding-top:10px; color:{theme.header_text}; }}
        QGroupBox::title {{ color:{theme.header_text}; }}
        QComboBox, QTextEdit, QLineEdit {{
            background:#0d1a2b; color:#eaf2ff; border:1px solid {theme.card_border}; border-radius:6px; padding:6px;
        }}
        QSlider::groove:horizontal {{ background:#263a50; height:6px; border-radius:3px; }}
        QSlider::handle:horizontal {{ background:{theme.accent}; width:14px; border-radius:7px; }}
        QPushButton {{ color:#ffffff; background:{theme.accent}; border:1px solid {theme.card_border}; border-radius:6px; padding:6px 10px; }}
        QPushButton:hover {{ background:{theme.accent_hover}; }}
        QLabel {{ color:{theme.header_text}; }}
        QCheckBox {{ color:#eaf2ff; }}
        """)

    def apply_sandbox_settings(self, sandbox: Dict[str, Any]) -> None:
        defaults = DEFAULT_SETTINGS.get("sandbox", {})
        sandbox = sandbox if isinstance(sandbox, dict) else {}

        level_value = sandbox.get("level", defaults.get("level", "restricted"))
        level_idx = self.sandbox_level.findData(level_value)
        if level_idx < 0:
            level_idx = self.sandbox_level.findData(defaults.get("level", "restricted"))
        if level_idx < 0:
            level_idx = 0
        self.sandbox_level.setCurrentIndex(level_idx)

        policy_value = sandbox.get("approval_policy", defaults.get("approval_policy", "require_approval"))
        policy_idx = self.sandbox_policy.findData(policy_value)
        if policy_idx < 0:
            policy_idx = self.sandbox_policy.findData(defaults.get("approval_policy", "require_approval"))
        if policy_idx < 0:
            policy_idx = 0
        self.sandbox_policy.setCurrentIndex(policy_idx)

        self.sandbox_full_auto.setChecked(bool(sandbox.get("full_auto", defaults.get("full_auto", False))))

        encryption_enabled = bool(sandbox.get("encryption_enabled", defaults.get("encryption_enabled", False)))
        access_enforced = bool(
            sandbox.get("access_control_enforced", defaults.get("access_control_enforced", False))
            or sandbox.get("access_control", False)
        )

        try:
            healthy, detail = self.ollama.health()
        except Exception:
            healthy, detail = False, "unavailable"

        self.update_sandbox_status(
            ollama_ok=healthy,
            ollama_detail=detail,
            encryption_enabled=encryption_enabled,
            access_control_enabled=access_enforced,
        )
        self._update_scan_roots_enabled()

    def update_sandbox_status(
        self,
        *,
        ollama_ok: bool,
        ollama_detail: str,
        encryption_enabled: bool,
        access_control_enabled: bool,
    ) -> None:
        detail = (ollama_detail or "").strip()
        if ollama_ok:
            text = "Connected"
            if detail and detail.upper() not in {"OK", "200"}:
                text = f"Connected ({detail})"
            self._set_status_label(self.sandbox_ollama_status, text, self.theme.live_ok)
        else:
            offline_text = "Offline" if not detail else f"Offline ({detail})"
            self._set_status_label(self.sandbox_ollama_status, offline_text, self.theme.live_err)

        encryption_text = "Enabled" if encryption_enabled else "Disabled"
        encryption_color = self.theme.live_ok if encryption_enabled else self.theme.live_warn
        self._set_status_label(self.sandbox_encryption_status, encryption_text, encryption_color)

        access_text = "Enforced" if access_control_enabled else "Open"
        access_color = self.theme.live_ok if access_control_enabled else self.theme.live_warn
        self._set_status_label(self.sandbox_access_status, access_text, access_color)

        self._sandbox_encryption_enabled = encryption_enabled
        self._sandbox_access_control_enforced = access_control_enabled

    def _set_status_label(self, label: QLabel, text: str, color: str) -> None:
        label.setText(text)
        label.setStyleSheet(f"color: {color}; font-weight: 600;")

    def populate_models(self):
        ok, names, _ = OllamaClient().list_models()
        names = sorted(names) if ok else []
        def fill(box: QComboBox, default_name: str):
            box.clear()
            if names:
                box.addItems(names)
                idx = box.findText(default_name)
                if idx >= 0: box.setCurrentIndex(idx)
                else:
                    box.insertItem(0, default_name); box.setCurrentIndex(0)
            else:
                box.addItem(default_name)
        fill(self.chat_model, DEFAULT_CHAT_MODEL)
        fill(self.vision_ocr_model, DEFAULT_VISION_OCR_MODEL)
        fill(self.vision_model, DEFAULT_VISION_MODEL)
        fill(self.embed_model, DEFAULT_EMBED_MODEL)

    def values(self) -> Dict[str, Any]:
        level_value = self.sandbox_level.currentData()
        if not level_value:
            level_text = self.sandbox_level.currentText().strip().lower()
            level_value = level_text.split()[0] if level_text else DEFAULT_SETTINGS["sandbox"]["level"]

        policy_value = self.sandbox_policy.currentData()
        if not policy_value:
            policy_text = self.sandbox_policy.currentText().strip().lower()
            policy_value = policy_text.split()[0] if policy_text else DEFAULT_SETTINGS["sandbox"]["approval_policy"]

        embed_contents = self.reference_embed_contents.isChecked()
        case_sensitive = self.reference_case_sensitive.isChecked()
        token_guard = self.reference_token_guard.isChecked()
        headroom = int(self.reference_token_headroom.value())

        scan_roots: List[str] = []
        if level_value == "trusted":
            scan_roots = _normalize_scan_roots(self._collect_scan_roots())

        return {
            "chat_model": self.chat_model.currentText().strip(),
            "vision_ocr_model": self.vision_ocr_model.currentText().strip(),
            "vision_model": self.vision_model.currentText().strip(),
            "embed_model": self.embed_model.currentText().strip(),
            "context_pairs": int(self.context_pairs.value()),
            "share_context": self.share_context.isChecked(),
            "share_limit": int(self.share_limit.value()),
            "enable_semantic": self.enable_embeddings.isChecked(),
            "enable_vision": self.enable_vision.isChecked(),
            "enable_interpreter": self.enable_interpreter.isChecked(),
            "reference_embed_contents": embed_contents,
            "reference_case_sensitive": case_sensitive,
            "reference_token_guard": token_guard,
            "reference_token_headroom": headroom,
            "data_root": _clamp_to_agent_subdir(self.data_root_edit.text().strip(), subdir=agent_data_dir()),
            "scan_roots": scan_roots,
            "shells": {
                "cmd": self.chk_cmd.isChecked(),
                "powershell": self.chk_powershell.isChecked(),
                "bash": self.chk_bash.isChecked(),
                "zsh": self.chk_zsh.isChecked(),
                "wsl": self.chk_wsl.isChecked(),
            },
            "codex": {
                "default_launch_mode": "bridge" if self.codex_mode_bridge.isChecked() else "normal",
                "working_folder": self.codex_working.text().strip() or str(workspace_root()),
                "sandbox": {
                    "level": level_value,
                    "approval_policy": policy_value,
                    "full_auto": self.sandbox_full_auto.isChecked(),
                    "encryption_enabled": self._sandbox_encryption_enabled,
                    "access_control_enforced": self._sandbox_access_control_enforced,
                },
                "reference_embed_contents": embed_contents,
                "reference_case_sensitive": case_sensitive,
                "reference_token_guard": token_guard,
                "reference_token_headroom": headroom,
                "scan_roots": scan_roots,
            }
        }

    def set_scan_roots(self, roots: Sequence[str]) -> None:
        self.scan_roots_list.clear()
        for root in _normalize_scan_roots(roots):
            self.scan_roots_list.addItem(root)
        self._update_scan_root_remove_enabled()
        self._update_scan_roots_enabled()

    def _collect_scan_roots(self) -> List[str]:
        values: List[str] = []
        for index in range(self.scan_roots_list.count()):
            item = self.scan_roots_list.item(index)
            if not item:
                continue
            text = item.text().strip()
            if text:
                values.append(text)
        return values

    def _on_add_scan_root(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select additional scan root",
            self.codex_working.text().strip() or str(workspace_root()),
        )
        if not directory:
            return
        normalized = _normalize_scan_roots([directory])
        if not normalized:
            return
        new_root = normalized[0]
        existing = {
            self.scan_roots_list.item(i).text()
            for i in range(self.scan_roots_list.count())
        }
        if new_root in existing:
            return
        self.scan_roots_list.addItem(new_root)
        self._update_scan_root_remove_enabled()

    def _on_remove_selected_scan_roots(self) -> None:
        for item in list(self.scan_roots_list.selectedItems()):
            row = self.scan_roots_list.row(item)
            self.scan_roots_list.takeItem(row)
        self._update_scan_root_remove_enabled()

    def _update_scan_root_remove_enabled(self) -> None:
        enabled = self.scan_roots_list.isEnabled() and bool(self.scan_roots_list.selectedItems())
        self.scan_root_remove.setEnabled(enabled)

    def _update_scan_roots_enabled(self, *_args) -> None:
        trusted = (self.sandbox_level.currentData() == "trusted")
        self.scan_roots_list.setEnabled(trusted)
        self.scan_root_add.setEnabled(trusted)
        if not trusted:
            self.scan_roots_list.clearSelection()
        self._update_scan_root_remove_enabled()

    def _row(self, *widgets: QWidget) -> QWidget:
        w = QWidget(self); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0)
        for wd in widgets: h.addWidget(wd)
        return w

    def _open_prompt_path(self, path: Path, ensure_exists: bool = False) -> None:
        path = Path(path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if ensure_exists and not path.exists():
                path.touch()
        except Exception as exc:  # pragma: no cover - UI feedback only
            QMessageBox.warning(self, "Open Prompt", f"Failed to prepare prompt file:\n{exc}")
            return
        opened = QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        if not opened:  # pragma: no cover - depends on host OS handlers
            QMessageBox.information(
                self,
                "Open Prompt",
                f"Prompt file located at:\n{path}\nOpen it manually to edit the persona.",
            )

# --------------------------------------------------------------------------------------
# Chat UI + vision pipeline
# --------------------------------------------------------------------------------------

class ChatMessage:
    def __init__(
        self,
        role: str,
        text: str,
        images: Optional[List[Path]] = None,
        model_name: str = "",
        *,
        kind: str = "text",
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.role = role
        self.text = text
        self.images = images or []
        self.model_name = model_name
        self.kind = kind
        self.meta = meta or {}


@dataclass
class ApprovalPrompt:
    header: str
    body: str
    options: Dict[str, str]

    def as_text(self) -> str:
        body = self.body.strip()
        if body:
            return f"{self.header}\n{body}"
        return self.header


@dataclass
class ParsedCodexEvent:
    kind: str  # "text" | "prompt" | "dismissal"
    payload: Any


class CodexInterpreter:
    """Auto-respond to Codex prompts when enabled."""

    _CONTINUE_PATTERNS: Tuple[re.Pattern[str], ...] = (
        re.compile(r"would you like me to continue", re.IGNORECASE),
        re.compile(r"should i keep going", re.IGNORECASE),
        re.compile(r"do you want me to continue", re.IGNORECASE),
        re.compile(r"can i continue", re.IGNORECASE),
    )
    _PLAN_PATTERN = re.compile(r"(?:^|\n)\s*(?:plan|next steps|todo)[:?]", re.IGNORECASE)
    _PLAN_BULLET_PATTERN = re.compile(r"^\s*(?:[-*]|\d+\.)", re.MULTILINE)
    _COMPLETION_PATTERNS: Tuple[re.Pattern[str], ...] = (
        re.compile(r"completed .*file", re.IGNORECASE),
        re.compile(r"finished .*file", re.IGNORECASE),
        re.compile(r"all changes (?:have been )?(?:applied|completed)", re.IGNORECASE),
        re.compile(r"no further (?:changes|actions) required", re.IGNORECASE),
    )
    _MAX_PLAN_CHARS = 400

    def __init__(
        self,
        *,
        bridge: CodexBridge,
        get_busy: Callable[[], bool],
        get_hwnd: Callable[[], int],
        on_auto: Optional[Callable[[str], None]] = None,
        send_command: Optional[Callable[[str], bool]] = None,
        enabled: bool = True,
    ) -> None:
        self.bridge = bridge
        self.enabled = enabled
        self._get_busy = get_busy
        self._get_hwnd = get_hwnd
        self._on_auto = on_auto or (lambda command: None)
        self._send_command = send_command
        self._last_user_instruction: str = ""
        self._last_auto_command: Optional[str] = None
        self._recent_plan: Deque[str] = deque(maxlen=2)
        self._auto_active = False
        self._auto_completed = False

    def observe_user(self, text: str) -> None:
        if text:
            self._last_user_instruction = self._trim(text)
        else:
            self._last_user_instruction = ""
        self._last_auto_command = None
        self._recent_plan.clear()
        self._auto_active = False
        self._auto_completed = False

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)
        if not self.enabled:
            self._recent_plan.clear()
            self._auto_active = False
            self._auto_completed = False
            self._last_auto_command = None

    def observe_codex_output(self, text: str) -> None:
        if not self.enabled:
            return
        snippet = (text or "").strip()
        if not snippet:
            return
        if self._matches(snippet, self._COMPLETION_PATTERNS):
            self._handle_completion()
            return
        if self._auto_completed or self._auto_active:
            return
        if not self._ready():
            return
        if self._matches(snippet, self._CONTINUE_PATTERNS):
            self._schedule_follow_up(self._build_follow_up())
            return
        if self._looks_like_plan(snippet):
            key = self._normalize_plan(snippet)
            if key:
                self._recent_plan.append(key)
                if len(self._recent_plan) == self._recent_plan.maxlen and len(set(self._recent_plan)) == 1:
                    self._schedule_follow_up(self._build_follow_up())
                    self._recent_plan.clear()
                    return
        else:
            self._recent_plan.clear()

    def _schedule_follow_up(self, command: Optional[str]) -> None:
        if not command:
            return
        message = command.strip()
        if not message:
            return
        if self._auto_completed:
            return
        if self._auto_active and message == self._last_auto_command:
            return

        if not self._ready():
            return
        sender = self._send_command
        if sender:
            ok = sender(message)
            if not ok:
                return
        else:
            ok = self.bridge.send_text(message)
            if not ok:
                return
            self.bridge.press_enter_async(self._get_hwnd())
        self._last_auto_command = message
        self._auto_active = True
        self._on_auto(message)

    def _ready(self) -> bool:
        if not self.bridge or not self.bridge.running():
            return False
        try:
            if self.bridge.busy():
                return False
        except Exception:
            pass
        try:
            if self._get_busy():
                return False
        except Exception:
            return False
        return True

    def _build_follow_up(self) -> str:
        base = self._last_user_instruction.strip()
        if not base:
            return "continue"
        if len(base) > 160:
            base = base[:157].rstrip() + "..."
        return f"continue, focusing on {base}"

    @staticmethod
    def _trim(text: str) -> str:
        collapsed = " ".join(text.split())
        return collapsed.strip()

    @staticmethod
    def _normalize_plan(text: str) -> str:
        return " ".join(text.lower().split())

    @staticmethod
    def _matches(snippet: str, patterns: Sequence[re.Pattern[str]]) -> bool:
        return any(p.search(snippet) for p in patterns)

    def _looks_like_plan(self, text: str) -> bool:
        if len(text) > self._MAX_PLAN_CHARS:
            return False
        if self._PLAN_PATTERN.search(text):
            return True
        if self._PLAN_BULLET_PATTERN.search(text):
            return True
        return False

    def _handle_completion(self) -> None:
        if self._auto_active:
            self._auto_completed = True
        self._auto_active = False
        self._last_auto_command = None
        self._recent_plan.clear()

DEFAULT_APPROVAL_TOKENS: Dict[str, str] = {
    "yes": "y",
    "always": "always",
    "no": "n",
    "feedback": "feedback",
}

_APPROVAL_TOKEN_STRINGS: Set[str] = (
    {action.lower() for action in DEFAULT_APPROVAL_TOKENS.keys()}
    | {token.lower() for token in DEFAULT_APPROVAL_TOKENS.values()}
)

APPROVAL_ACTION_TITLES: Dict[str, str] = {
    "yes": "Yes",
    "always": "Always",
    "no": "No",
    "feedback": "Provide feedback",
}

_APPROVAL_ACTION_ALIASES: Dict[str, Tuple[str, ...]] = {
    "yes": ("yes", "y", "approve", "allow", "run", "execute"),
    "always": ("always", "a", "always allow", "always approve"),
    "no": ("no", "n", "deny", "don't", "cancel", "abort"),
    "feedback": ("feedback", "f", "provide feedback", "report", "complaint"),
}

_APPROVAL_HEADER_RE = re.compile(
    r"^\s*(?:allow|approve|authorization|authorize)\b.*(?:\?|:).*$",
    re.IGNORECASE,
)
_APPROVAL_HEADER_PREFIXES: Tuple[str, ...] = (
    "select",
    "choose",
    "pick",
    "make a selection",
    "action required",
    "selection required",
)
_APPROVAL_DISMISS_RE = re.compile(r"(prompt|approval).*(dismissed|cancell?ed|aborted)", re.IGNORECASE)


def _normalize_display_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


class ChatBubbleWidget(QFrame):
    def __init__(
        self,
        theme: Theme,
        role: str,
        text: str,
        *,
        model_name: str = "",
        thinks: Optional[Sequence[str]] = None,
        images: Optional[Sequence[Path]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.theme = theme
        self.role = role
        self.setObjectName("ChatBubbleWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if role in ("user", "assistant"):
            name = "You" if role == "user" else "Codex"
            name_label = QLabel(name, self)
            name_label.setObjectName("MessageName")
            name_label.setProperty("role", role)
            align = Qt.AlignRight if role == "user" else Qt.AlignLeft
            name_label.setAlignment(align)
            layout.addWidget(name_label, 0, align)

        bubble = QFrame(self)
        bubble.setObjectName("MessageBubble")
        bubble.setProperty("role", role)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(14, 10, 14, 12)
        bubble_layout.setSpacing(8)
        bubble.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        bubble.setMaximumWidth(720)

        if role == "assistant" and model_name:
            model_label = QLabel(model_name, bubble)
            model_label.setObjectName("ModelNameLabel")
            model_label.setAlignment(Qt.AlignLeft)
            bubble_layout.addWidget(model_label)

        if role == "assistant":
            for raw_think in thinks or []:
                think_text = _normalize_display_text(raw_think).strip()
                if not think_text:
                    continue
                think_label = QLabel(think_text, bubble)
                think_label.setObjectName("ThinkText")
                think_label.setProperty("role", role)
                think_label.setTextFormat(Qt.PlainText)
                think_label.setWordWrap(True)
                think_label.setAlignment(Qt.AlignLeft)
                think_label.setTextInteractionFlags(
                    Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
                )
                bubble_layout.addWidget(think_label)

        body_text = _normalize_display_text(text)
        body_label = QLabel(body_text if body_text else "", bubble)
        body_label.setObjectName("MessageText")
        body_label.setProperty("role", role)
        body_label.setTextFormat(Qt.PlainText)
        body_label.setWordWrap(True)
        body_label.setAlignment(Qt.AlignLeft)
        body_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.LinksAccessibleByMouse
        )
        bubble_layout.addWidget(body_label)

        for img_path in images or []:
            caption = QLabel(img_path.name, bubble)
            caption.setObjectName("AttachmentLabel")
            caption.setAlignment(Qt.AlignLeft)
            caption.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            bubble_layout.addWidget(caption)

            img_label = QLabel(bubble)
            img_label.setObjectName("AttachmentImage")
            pixmap = QPixmap(str(img_path)) if img_path.exists() else QPixmap()
            if not pixmap.isNull():
                if pixmap.width() > 320:
                    pixmap = pixmap.scaledToWidth(320, Qt.SmoothTransformation)
                img_label.setPixmap(pixmap)
            else:
                img_label.setText("(image unavailable)")
                img_label.setTextFormat(Qt.PlainText)
            img_label.setAlignment(Qt.AlignLeft)
            bubble_layout.addWidget(img_label)

        layout.addWidget(bubble)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


class ConversationView(QFrame):
    def __init__(self, theme: Theme, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.theme = theme
        self.setObjectName("ConversationView")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll = QScrollArea(self)
        self.scroll.setObjectName("ConversationScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.scroll)

        self.container = QWidget(self.scroll)
        self.container.setObjectName("ConversationContainer")
        self.scroll.setWidget(self.container)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 12, 12, 12)
        self.container_layout.setSpacing(12)
        self._spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.container_layout.addItem(self._spacer)

    def clear(self) -> None:
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def append_message(
        self,
        role: str,
        text: str,
        *,
        model_name: str = "",
        thinks: Optional[Sequence[str]] = None,
        images: Optional[Sequence[Path]] = None,
    ) -> None:
        bubble = ChatBubbleWidget(
            self.theme,
            role,
            text,
            model_name=model_name,
            thinks=thinks,
            images=images,
        )
        self._append_row(role, bubble)
        self._refresh_bubble_styles()
        QTimer.singleShot(0, self._scroll_to_bottom)

    def append_widget(
        self,
        widget: QWidget,
        *,
        role: str = "assistant",
        alignment: Optional[Qt.AlignmentFlag] = None,
    ) -> None:
        self._append_row(role, widget, alignment)
        QTimer.singleShot(0, self._scroll_to_bottom)

    def _append_row(
        self,
        role: str,
        widget: QWidget,
        alignment: Optional[Qt.AlignmentFlag] = None,
    ) -> None:
        row = QFrame(self.container)
        row.setObjectName("MessageRow")
        hbox = QHBoxLayout(row)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        align = alignment if alignment is not None else (Qt.AlignRight if role == "user" else Qt.AlignLeft)
        if align == Qt.AlignRight:
            hbox.addStretch(1)
            hbox.addWidget(widget, 0, Qt.AlignRight)
        elif align == Qt.AlignCenter:
            hbox.addStretch(1)
            hbox.addWidget(widget, 0, Qt.AlignCenter)
            hbox.addStretch(1)
        else:
            hbox.addWidget(widget, 0, Qt.AlignLeft)
            hbox.addStretch(1)

        insert_at = max(0, self.container_layout.count() - 1)
        self.container_layout.insertWidget(insert_at, row)

    def _refresh_bubble_styles(self) -> None:
        for index in range(self.container_layout.count() - 1):
            item = self.container_layout.itemAt(index)
            row = item.widget()
            if not row:
                continue
            bubble = row.findChild(ChatBubbleWidget)
            if not bubble:
                continue
            bubble.style().unpolish(bubble)
            bubble.style().polish(bubble)
            for label in bubble.findChildren(QLabel):
                label.style().unpolish(label)
                label.style().polish(label)

    def _scroll_to_bottom(self) -> None:
        bar = self.scroll.verticalScrollBar()
        if bar:
            bar.setValue(bar.maximum())


class ApprovalPromptWidget(QFrame):
    def __init__(
        self,
        theme: Theme,
        prompt: ApprovalPrompt,
        on_decision,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.theme = theme
        self.prompt = prompt
        self._on_decision = on_decision
        self._buttons: Dict[str, QPushButton] = {}
        self._state: str = "pending"
        self._pending_action: str = ""
        self.setObjectName("ApprovalPrompt")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QLabel(prompt.header, self)
        header.setObjectName("ApprovalHeader")
        header.setWordWrap(True)
        header.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        layout.addWidget(header)

        body_text = prompt.body.strip()
        if body_text:
            body = QLabel(body_text, self)
            body.setObjectName("ApprovalBody")
            body.setWordWrap(True)
            body.setTextInteractionFlags(
                Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.LinksAccessibleByMouse
            )
            layout.addWidget(body)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(btn_row)

        for action, title in APPROVAL_ACTION_TITLES.items():
            btn = QPushButton(title, self)
            btn.setObjectName("ApprovalButton")
            btn.setProperty("approvalAction", action)
            btn.clicked.connect(lambda _=False, a=action: self._handle_click(a))
            self._buttons[action] = btn
            btn_row.addWidget(btn)

        btn_row.addStretch(1)

        self._status = QLabel("", self)
        self._status.setObjectName("ApprovalStatus")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

    def _handle_click(self, action: str) -> None:
        if self._state not in {"pending"}:
            return
        token = self.prompt.options.get(action) or DEFAULT_APPROVAL_TOKENS.get(action, action)
        self._pending_action = action
        self._state = "responding"
        self._set_buttons_enabled(False)
        try:
            self._on_decision(self, action, token)
        except Exception:
            self._state = "pending"
            self._set_buttons_enabled(True)
            self._pending_action = ""
            raise

    def mark_submitted(self, action: Optional[str] = None) -> None:
        action = action or self._pending_action
        title = APPROVAL_ACTION_TITLES.get(action, action.title())
        self._status.setText(f"Sent: {title}")
        self._state = "submitted"
        self._pending_action = ""
        self._set_buttons_enabled(False)

    def mark_failed(self, reason: str) -> None:
        self._status.setText(f"Send failed: {reason}")
        self._state = "pending"
        self._pending_action = ""
        self._set_buttons_enabled(True)

    def mark_dismissed(self, reason: str) -> None:
        note = reason.strip() if reason else "Approval dismissed."
        self._status.setText(note)
        self._state = "dismissed"
        self._pending_action = ""
        self._set_buttons_enabled(False)

    def is_active(self) -> bool:
        return self._state in {"pending", "responding"}

    def _set_buttons_enabled(self, enabled: bool) -> None:
        for btn in self._buttons.values():
            btn.setEnabled(enabled)

class ChatInput(QTextEdit):
    imagesReady = Signal(list)
    referenceAccepted = Signal(dict)

    _TOKEN_BREAKS = " \n\t\r\f\v'\"()[]{}<>:,"

    def __init__(self, parent_card: "ChatCard", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card = parent_card
        self.setAcceptDrops(True)
        self.setLayoutDirection(Qt.LeftToRight)

        ref_settings = parent_card.settings if isinstance(parent_card.settings, dict) else {}
        embed_contents = bool(
            ref_settings.get(
                "reference_embed_contents",
                DEFAULT_SETTINGS.get("reference_embed_contents", True),
            )
        )
        case_sensitive = bool(
            ref_settings.get(
                "reference_case_sensitive",
                DEFAULT_SETTINGS.get("reference_case_sensitive", False),
            )
        )
        token_guard = bool(
            ref_settings.get(
                "reference_token_guard",
                DEFAULT_SETTINGS.get("reference_token_guard", True),
            )
        )

        self._repo_helper = RepoReferenceHelper(
            parent_card.workspace,
            parent=self,
            embed_contents=embed_contents,
            case_sensitive=case_sensitive,
            token_guard=token_guard,
            extra_roots=parent_card.scan_roots,
        )
        self._repo_helper.refreshed.connect(self._handle_repo_refresh)

        self._suggestion_popup = QListWidget(self)
        self._suggestion_popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self._suggestion_popup.setFocusPolicy(Qt.NoFocus)
        self._suggestion_popup.setUniformItemSizes(True)
        self._suggestion_popup.hide()
        self._suggestion_popup.itemClicked.connect(self._handle_item_clicked)

        self._accepted_references: List[Dict[str, str]] = []

        self.textChanged.connect(self._handle_text_changed)

    # ----- clipboard & drag/drop -----
    def canInsertFromMimeData(self, source: QMimeData) -> bool:
        if source.hasImage() or source.hasUrls():
            return True
        return super().canInsertFromMimeData(source)

    def insertFromMimeData(self, source: QMimeData):
        if source.hasImage():
            img = source.imageData()
            if PIL_AVAILABLE and img:
                name = f"paste_{int(time.time())}_{uuid.uuid4().hex[:6]}.png"
                out = agent_images_dir() / name
                ensure_dir(out.parent)
                try:
                    if isinstance(img, QImage):
                        buf = QImage(img).convertToFormat(QImage.Format_RGBA8888)
                        ptr = buf.constBits()
                        ptr.setsize(buf.sizeInBytes())
                        pil = Image.frombytes("RGBA", (buf.width(), buf.height()), bytes(ptr))
                    else:
                        raise RuntimeError("Unsupported image type from clipboard")
                    pil = pil.convert("RGBA")
                    pil.save(out, "PNG", optimize=True)
                    self.imagesReady.emit([out])
                    return
                except Exception as e:
                    QMessageBox.warning(self, "Paste Image", f"Failed to paste image: {e}")
        if source.hasUrls():
            imgs: List[Path] = []
            for url in source.urls():
                p = Path(url.toLocalFile())
                if p.is_file():
                    try:
                        imgs.append(self.card._convert_to_png(p))
                    except Exception:
                        pass
            if imgs:
                self.imagesReady.emit(imgs)
                return
        super().insertFromMimeData(source)

    def dragEnterEvent(self, e):
        if e.mimeData().hasImage() or e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dropEvent(self, e):
        md = e.mimeData()
        imgs: List[Path] = []
        if md.hasUrls():
            for url in md.urls():
                p = Path(url.toLocalFile())
                if p.is_file():
                    try:
                        imgs.append(self.card._convert_to_png(p))
                    except Exception:
                        pass
        if imgs:
            self.imagesReady.emit(imgs)
            e.acceptProposedAction()
            return
        super().dropEvent(e)

    # ----- repository suggestions -----
    def clear(self) -> None:  # type: ignore[override]
        self._accepted_references.clear()
        self._hide_suggestions()
        super().clear()

    def consume_references(self) -> List[Dict[str, str]]:
        refs = [
            {"path": ref["path"], "type": ref["type"]}
            for ref in self._accepted_references
        ]
        self._accepted_references.clear()
        return refs

    def keyPressEvent(self, event: QKeyEvent) -> None:  # type: ignore[override]
        if self._suggestion_popup.isVisible():
            if event.key() in (Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter):
                event.accept()
                self._accept_current_suggestion()
                return
            if event.key() == Qt.Key_Down and self._suggestion_popup.count():
                event.accept()
                row = (self._suggestion_popup.currentRow() + 1) % self._suggestion_popup.count()
                self._suggestion_popup.setCurrentRow(row)
                return
            if event.key() == Qt.Key_Up and self._suggestion_popup.count():
                event.accept()
                row = self._suggestion_popup.currentRow() - 1
                if row < 0:
                    row = self._suggestion_popup.count() - 1
                self._suggestion_popup.setCurrentRow(row)
                return
            if event.key() == Qt.Key_Escape:
                event.accept()
                self._hide_suggestions()
                return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):  # type: ignore[override]
        self._hide_suggestions()
        super().focusOutEvent(event)

    def _handle_repo_refresh(self) -> None:
        self._update_suggestions()

    def _handle_item_clicked(self, item: QListWidgetItem) -> None:
        ref = item.data(Qt.UserRole)
        if isinstance(ref, RepoReference):
            self._apply_reference(ref)

    def _handle_text_changed(self) -> None:
        if not self.toPlainText().strip():
            self._accepted_references.clear()
        self._update_suggestions()

    def _token_info(self) -> tuple[str, int, int]:
        text = self.toPlainText()
        cursor = self.textCursor()
        pos = cursor.position()
        start = pos
        while start > 0 and text[start - 1] not in self._TOKEN_BREAKS:
            start -= 1
        return text[start:pos], start, pos

    def _update_suggestions(self) -> None:
        token, _, _ = self._token_info()
        if len(token.strip()) < 2:
            self._hide_suggestions()
            return

        matches = self._repo_helper.suggestions(token, limit=6)
        if not matches:
            self._hide_suggestions()
            return

        self._suggestion_popup.clear()
        for ref in matches:
            item = QListWidgetItem(ref.display_label())
            item.setData(Qt.UserRole, ref)
            item.setToolTip(ref.absolute_path.as_posix())
            self._suggestion_popup.addItem(item)
        self._suggestion_popup.setCurrentRow(0)

        rect = self.cursorRect()
        popup_width = max(260, rect.width() * 3)
        popup_height = self._suggestion_popup.sizeHintForRow(0) * min(6, self._suggestion_popup.count()) + 8
        global_pos = self.mapToGlobal(rect.bottomLeft())
        self._suggestion_popup.setFixedSize(popup_width, popup_height)
        self._suggestion_popup.move(global_pos)
        self._suggestion_popup.show()

    def _hide_suggestions(self) -> None:
        self._suggestion_popup.hide()

    def _accept_current_suggestion(self) -> None:
        item = self._suggestion_popup.currentItem()
        if item is None and self._suggestion_popup.count():
            item = self._suggestion_popup.item(0)
        if not item:
            return
        ref = item.data(Qt.UserRole)
        if isinstance(ref, RepoReference):
            self._apply_reference(ref)

    def _apply_reference(self, ref: "RepoReference") -> None:
        token, start, end = self._token_info()
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(ref.relative_path)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

        highlight = self.textCursor()
        highlight.setPosition(cursor.position() - len(ref.relative_path))
        highlight.setPosition(cursor.position(), QTextCursor.KeepAnchor)
        fmt = QTextCharFormat()
        fmt.setBackground(self.palette().alternateBase())
        highlight.mergeCharFormat(fmt)

        payload = {"path": ref.relative_path, "type": ref.kind, "token": ref.relative_path}
        self._accepted_references.append(payload)
        self.referenceAccepted.emit({"path": ref.relative_path, "type": ref.kind})
        self._hide_suggestions()

class ChatCard(QFrame):
    append_signal = Signal(ChatMessage)
    state_signal = Signal(bool)
    codex_status_signal = Signal(str)     # status text
    codex_led_signal = Signal(str)        # "red"/"yellow"/"green"
    codex_output_signal = Signal(str)     # new Codex output
    error_signal = Signal(str)

    _TASK_STATUSES = {"open", "merged", "closed", "cancelled", "failed", "deleted"}

    def __init__(self, theme: Theme, ollama: OllamaClient, settings: Dict[str, Any], lex_mgr: LexiconManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = theme; self.ollama = ollama; self.settings = settings; self.lex = lex_mgr
        self._chat_prompt = get_prompt_watcher("chat_system")
        self.setObjectName("ChatCard"); self.setStyleSheet(self._qss(theme)); self.setLayoutDirection(Qt.LeftToRight)
        self.busy = False; self.messages: List[ChatMessage] = []; self.context_pairs = int(settings.get("context_pairs", 25))
        self.share_context = bool(settings.get("share_context", True))
        self.share_limit = int(settings.get("share_limit", 5))
        self.workspace: Path = Path(settings.get("workspace") or workspace_root())
        sandbox_cfg = settings.get("sandbox")
        if not isinstance(sandbox_cfg, dict):
            sandbox_cfg = copy.deepcopy(DEFAULT_SETTINGS.get("sandbox", {}))
        self.settings["sandbox"] = sandbox_cfg
        raw_scan_roots = settings.get("scan_roots")
        normalized_scan_roots = _normalize_scan_roots(
            raw_scan_roots if isinstance(raw_scan_roots, (list, tuple)) else []
        )
        self.settings["scan_roots"] = normalized_scan_roots
        self._sandbox_level = str(
            sandbox_cfg.get("level", DEFAULT_SETTINGS.get("sandbox", {}).get("level", "restricted"))
        ).strip().lower()
        allowed_scan_roots: List[Path] = []
        if self._sandbox_level == "trusted":
            seen_paths: Set[Path] = set()
            try:
                workspace_resolved = self.workspace.resolve()
            except Exception:
                workspace_resolved = self.workspace
            for root_text in normalized_scan_roots:
                try:
                    candidate = Path(root_text).expanduser().resolve()
                except Exception:
                    continue
                if candidate in seen_paths or candidate == workspace_resolved:
                    continue
                if not candidate.exists() or not candidate.is_dir():
                    continue
                seen_paths.add(candidate)
                allowed_scan_roots.append(candidate)
        self.scan_roots = allowed_scan_roots
        self.session_id = f"term_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.session_dir = ensure_dir(agent_sessions_dir() / self.session_id)
        self.data_root: Path = _clamp_to_agent_subdir(settings.get("data_root"), subdir=agent_data_dir())
        self.settings["data_root"] = str(self.data_root)
        interpreter_default = bool(settings.get("enable_interpreter", settings.get("codex_auto_continue", False)))
        self.settings["enable_interpreter"] = interpreter_default
        self._interpreter_tooltip = (
            "When enabled, Codex automatically sends follow-up commands whenever the interpreter detects"
            " a continuation prompt or actionable plan in the bridge output."
        )
        self._led_state = "red"

        embed_model = settings.get("embed_model", DEFAULT_EMBED_MODEL)
        enable_embed = settings.get("enable_semantic", True)
        self.conv = ConversationIO(
            self.session_dir,
            embed_model,
            self.ollama,
            enable_embed,
            session_token=self.session_id,
            archive_root=agent_archives_dir(),
        )
        self.dataset = DatasetManager(self.session_dir, embed_model, self.ollama, data_root=self.data_root, enable_semantic=enable_embed)
        self.pending_images: List[Path] = []
        self.session_notes: List[Dict[str, str]] = self._load_session_notes()
        self._safety_notifier_id: str = ""
        self._approval_widgets: List[ApprovalPromptWidget] = []
        self._task_bus_handles: List[Subscription] = []
        self._loaded_conversation_id: Optional[str] = None
        self._recent_input_references: Deque[Dict[str, str]] = deque(maxlen=10)

        self.codex = CodexBootstrap(self.ollama)
        self.bridge = CodexBridge(
            status_append_fn=self._codex_status,
            led_setter_fn=lambda s: self.codex_led_signal.emit(s),
            output_append_fn=lambda t: self.codex_output_signal.emit(t),
        )
        self.codex_interpreter = CodexInterpreter(
            bridge=self.bridge,
            get_busy=lambda: self.busy or self.bridge.busy(),
            get_hwnd=self._ui_hwnd,
            on_auto=self._handle_auto_follow_up,
            send_command=self._send_codex_auto,
            enabled=interpreter_default,
        )

        self.error_signal.connect(self._log_error_center)
        self.error_signal.connect(self._handle_error_notice)
        self._safety_notifier_id = safety_manager.add_notifier(self.error_signal.emit)

        # UI
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        main_frame = QFrame(self)
        main_frame.setObjectName("ChatMainColumn")
        root = QVBoxLayout(main_frame)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame(main_frame)
        header.setObjectName("Header")
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(12, 8, 12, 8)
        hbox.setSpacing(8)
        self.title = QLabel("Terminal", header)
        self.title.setObjectName("Title")
        hbox.addWidget(self.title)

        self.drawer_toggle = QToolButton(header)
        self.drawer_toggle.setObjectName("TaskDrawerToggle")
        self.drawer_toggle.setArrowType(Qt.RightArrow)
        self.drawer_toggle.setAutoRaise(True)
        self.drawer_toggle.setFocusPolicy(Qt.NoFocus)
        self.drawer_toggle.setToolTip("Show Tasks (Alt+T)")
        self.drawer_toggle.clicked.connect(self._toggle_task_drawer)
        hbox.addWidget(self.drawer_toggle)

        hbox.addStretch(1)

        self.led = BridgeLED(self.theme, tooltip="Codex Bridge")
        hbox.addWidget(self.led, 0, Qt.AlignVCenter)
        self.interpreter_caption = QLabel("Interpreter: On" if interpreter_default else "Interpreter: Off", header)
        self.interpreter_caption.setObjectName("InterpreterCaption")
        hbox.addWidget(self.interpreter_caption, 0, Qt.AlignVCenter)
        self.interpreter_toggle = ToggleSwitch(self.theme, header)
        self.interpreter_toggle.setObjectName("InterpreterToggle")
        self.interpreter_toggle.setChecked(interpreter_default)
        self.interpreter_toggle.setToolTip(self._interpreter_tooltip)
        self.interpreter_toggle.toggled.connect(self._on_interpreter_toggled)
        hbox.addWidget(self.interpreter_toggle, 0, Qt.AlignVCenter)
        self.model_label = QLabel(self._model_label_text(), header)
        self.model_label.setObjectName("ModelLabel")
        hbox.addWidget(self.model_label)

        self.btn_codex_start = QPushButton("Start Codex + Bridge", header)
        self.btn_codex_start.setObjectName("AccentBtn")
        self.btn_codex_start.clicked.connect(self._start_codex_bridge)
        hbox.addWidget(self.btn_codex_start)

        self.btn_codex_stop = QPushButton("Stop", header)
        self.btn_codex_stop.setObjectName("AccentBtn")
        self.btn_codex_stop.clicked.connect(self._stop_codex_bridge)
        self.btn_codex_stop.setEnabled(False)
        hbox.addWidget(self.btn_codex_stop)

        self.btn_show = QPushButton("Show CMD", header)
        self.btn_show.clicked.connect(lambda: self.bridge.show())
        hbox.addWidget(self.btn_show)
        self.btn_hide = QPushButton("Hide CMD", header)
        self.btn_hide.clicked.connect(lambda: self.bridge.hide())
        hbox.addWidget(self.btn_hide)

        self.attach_btn = QPushButton("Attach Image", header)
        self.attach_btn.setObjectName("AccentBtn")
        self.attach_btn.clicked.connect(self._attach_image)
        hbox.addWidget(self.attach_btn)
        root.addWidget(header)

        self.view = ConversationView(self.theme, main_frame)
        root.addWidget(self.view, 1)
        self.view.append_message("system", self._intro_message())

        ibar = QFrame(main_frame)
        ibar.setObjectName("InputBar")
        ibox = QHBoxLayout(ibar)
        ibox.setContentsMargins(10, 8, 10, 10)
        ibox.setSpacing(8)
        self.input = ChatInput(self, ibar)
        self.input.setObjectName("InputMulti")
        self.input.setPlaceholderText("Type a message…  (Ctrl+Enter → Codex • Alt+Enter local reply)")
        self.input.setFixedHeight(4 * self.input.fontMetrics().lineSpacing())
        self.input.imagesReady.connect(self._on_images_from_editor)
        self.input.referenceAccepted.connect(self._on_reference_accepted)
        ibox.addWidget(self.input, 1)
        self.send_codex_btn = QPushButton("Send → Codex", ibar)
        self.send_codex_btn.clicked.connect(self._send_to_codex)
        ibox.addWidget(self.send_codex_btn)
        self.send_btn = QPushButton("Local Reply", ibar)
        self.send_btn.setObjectName("AccentBtn")
        self.send_btn.clicked.connect(self._on_send_local)
        ibox.addWidget(self.send_btn)
        root.addWidget(ibar)

        outer.addWidget(main_frame, 1)
        self.task_drawer = TaskDrawer(session_id=self.session_id, parent=self)
        self.task_drawer.hide()
        outer.addWidget(self.task_drawer, 0)
        self._drawer_width = self.task_drawer.width()

        self._base_min_width = 980
        self._base_min_height = 600
        self.setMinimumSize(self._base_min_width, self._base_min_height)
        self._update_drawer_toggle(False)
        QTimer.singleShot(0, self._propagate_minimums)

        # Signals
        self.append_signal.connect(self._render_message)
        self.state_signal.connect(self._set_busy)
        self.codex_status_signal.connect(self._on_codex_status)
        self.codex_led_signal.connect(self._handle_led_state)
        self.codex_output_signal.connect(self._on_codex_output)

        try:
            self._task_bus_handles.append(subscribe("task.conversation", self._handle_task_conversation))
        except Exception:
            logger.exception("Failed to subscribe to task conversation events")
        self.destroyed.connect(lambda *_: self._teardown_task_bus())

        # Shortcuts
        self._add_shortcut("Ctrl+Return", self._send_to_codex)  # primary to Codex
        self._add_shortcut("Alt+Return", self._on_send_local)
        self._add_shortcut("Alt+T", self._toggle_task_drawer)
        self._refresh_interpreter_toggle_enabled()

    # ----- helpers -----
    def _ui_hwnd(self) -> int:
        try:
            wh = self.window().windowHandle()
            return int(wh.winId()) if wh else 0
        except Exception:
            return 0

    def _add_shortcut(self, key: str, fn):
        act = QAction(self); act.setShortcut(QKeySequence(key)); act.triggered.connect(fn); self.addAction(act)

    def _update_interpreter_caption(self, enabled: bool) -> None:
        if hasattr(self, "interpreter_caption"):
            text = "Interpreter: On" if enabled else "Interpreter: Off"
            self.interpreter_caption.setText(text)

    def _refresh_interpreter_toggle_enabled(self) -> None:
        if not hasattr(self, "interpreter_toggle"):
            return
        allow = self.bridge.running() and self._led_state in {"yellow", "green"}
        self.interpreter_toggle.setEnabled(allow)
        tooltip = self._interpreter_tooltip
        if not allow:
            tooltip = (
                f"{self._interpreter_tooltip}\nBridge offline — start Codex to change automation."
            )
        self.interpreter_toggle.setToolTip(tooltip)
        self._update_interpreter_caption(self.interpreter_toggle.isChecked())

    def _current_min_width(self, opened: Optional[bool] = None) -> int:
        if opened is None:
            opened = self.task_drawer.isVisible()
        extra = self._drawer_width if opened else 0
        return self._base_min_width + extra

    def _propagate_minimums(self, opened: Optional[bool] = None) -> None:
        min_width = self._current_min_width(opened)
        min_height = self._base_min_height
        self.setMinimumSize(min_width, min_height)
        parent = self.parentWidget()
        handled = False
        while parent is not None:
            if hasattr(parent, "set_content_min_size"):
                parent.set_content_min_size(min_width, min_height)
                handled = True
                break
            if hasattr(parent, "setMinimumSize"):
                parent.setMinimumSize(max(parent.minimumWidth(), min_width), max(parent.minimumHeight(), min_height))
            if hasattr(parent, "resize"):
                parent.resize(max(parent.width(), min_width), max(parent.height(), min_height))
            parent = parent.parentWidget()
        if not handled:
            parent = self.parentWidget()
            if parent and hasattr(parent, "setMinimumSize"):
                parent.setMinimumSize(max(parent.minimumWidth(), min_width), max(parent.minimumHeight(), min_height))

    def _update_drawer_toggle(self, opened: bool) -> None:
        arrow = Qt.LeftArrow if opened else Qt.RightArrow
        self.drawer_toggle.setArrowType(arrow)
        tooltip = "Hide Tasks (Alt+T)" if opened else "Show Tasks (Alt+T)"
        self.drawer_toggle.setToolTip(tooltip)

    def _toggle_task_drawer(self):
        focus_before = QApplication.focusWidget()
        visible = self.task_drawer.isVisible()
        if visible:
            self.task_drawer.hide()
            self._propagate_minimums(False)
        else:
            self.task_drawer.refresh()
            self.task_drawer.show()
            self._drawer_width = max(self._drawer_width, self.task_drawer.width())
            self._propagate_minimums(True)
        self._update_drawer_toggle(not visible)
        if (
            focus_before
            and focus_before is not self.drawer_toggle
            and not self.task_drawer.isAncestorOf(focus_before)
        ):
            QTimer.singleShot(0, lambda w=focus_before: w.setFocus(Qt.ShortcutFocusReason))

    def _codex_status(self, msg: str):
        self.codex_status_signal.emit(msg)

    @Slot(str)
    def _on_codex_status(self, message: str) -> None:
        self.view.append_message("system", message)

    @Slot(str)
    def _handle_led_state(self, state: str) -> None:
        self._led_state = state or "red"
        self.led.set_state(state)
        self._refresh_interpreter_toggle_enabled()

    def _on_interpreter_toggled(self, checked: bool) -> None:
        enabled = bool(checked)
        self.settings["enable_interpreter"] = enabled
        self._update_interpreter_caption(enabled)
        if hasattr(self, "codex_interpreter"):
            self.codex_interpreter.set_enabled(enabled)
        settings = load_codex_settings()
        settings["enable_interpreter"] = enabled
        save_codex_settings(settings)
        self._refresh_interpreter_toggle_enabled()

    def _load_session_notes(self) -> List[Dict[str, str]]:
        try:
            return load_session_notes()
        except Exception:
            return []

    def _memory_messages(self) -> List[Dict[str, str]]:
        if not self.session_notes:
            return []
        recent = self.session_notes[-5:]
        lines = [f"- {entry.get('notes', '')}" for entry in recent if entry.get("notes")]
        payload = "\n".join(lines).strip()
        if not payload:
            return []
        return [{"role": "system", "content": f"Prior session notes:\n{payload}"}]

    def _summarize_memory_note(self, text: str, images: List[Path]) -> Optional[str]:
        base = text.strip()
        if not base:
            if images:
                names = ", ".join(ip.name for ip in images)
                base = f"User shared images: {names}"
            else:
                return None
        if len(base) > 240:
            base = base[:237].rstrip() + "..."
        return base

    def _store_session_note(self, text: str, images: List[Path]) -> None:
        summary = self._summarize_memory_note(text, images)
        if not summary:
            return
        entry = append_session_note(summary)
        self.session_notes.append(entry)

    @staticmethod
    def _parse_codex_approval_events(delta: str) -> List[ParsedCodexEvent]:
        if not delta:
            return []

        def strip_prompt_leader(value: str) -> str:
            if not value:
                return value
            idx = 0
            saw_prompt = False
            length = len(value)
            while idx < length:
                ch = value[idx]
                if ch.isspace():
                    idx += 1
                    continue
                code_point = ord(ch)
                if 0x2500 <= code_point <= 0x259F:
                    saw_prompt = True
                    idx += 1
                    continue
                break
            if saw_prompt:
                while idx < length and value[idx].isspace():
                    idx += 1
                return value[idx:]
            return value

        lines = [strip_prompt_leader(line) for line in delta.splitlines()]
        events: List[ParsedCodexEvent] = []
        buffer: List[str] = []
        pending_actions: List[str] = []

        def flush_buffer() -> None:
            if not buffer:
                return
            text = "\n".join(buffer).strip("\n")
            if text.strip():
                events.append(ParsedCodexEvent("text", text))
            buffer.clear()

        def is_header(line: str) -> bool:
            normalized = strip_prompt_leader(line)
            stripped = normalized.strip()
            if not stripped:
                return False
            if _APPROVAL_HEADER_RE.match(stripped):
                return True
            lowered = stripped.lower()
            if ":" in stripped:
                prefix = stripped.split(":", 1)[0].strip().lower()
                if any(prefix.startswith(p) for p in _APPROVAL_HEADER_PREFIXES):
                    return True
            if any(lowered.startswith(p) for p in _APPROVAL_HEADER_PREFIXES):
                if "?" in stripped or "option" in lowered or "action" in lowered or "selection" in lowered:
                    return True
            if any(phrase in lowered for phrase in ("select an option", "choose an option", "make a selection")):
                return True
            return False

        def is_dismissal(line: str) -> bool:
            return bool(_APPROVAL_DISMISS_RE.search(line))

        def line_is_prompt_content(line: str) -> bool:
            normalized_line = strip_prompt_leader(line)
            stripped = normalized_line.strip()
            if not stripped:
                return False
            if stripped.startswith((">", "-", "•")):
                return True
            if normalized_line.startswith(" "):
                return True
            if re.match(r"^[\[(<].+[\])>]", stripped):
                return True
            if re.match(r"^\d+\s*[\).:-]", stripped):
                return True
            lowered = stripped.lower()
            for aliases in _APPROVAL_ACTION_ALIASES.values():
                if any(alias in lowered for alias in aliases):
                    return True
            if any(keyword in lowered for keyword in ("allow", "approve", "command", "run")):
                return True
            return False

        def _split_option_columns(text: str) -> List[str]:
            parts = re.split(r"\s{2,}", text.strip())
            return [part.strip() for part in parts if part.strip()]

        def _clean_token(value: str) -> str:
            return value.strip().strip("[](){}<>")

        def parse_option_line(line: str) -> Tuple[List[Tuple[str, str]], bool]:
            nonlocal pending_actions
            stripped = strip_prompt_leader(line).strip()
            if not stripped:
                pending_actions = []
                return [], False

            match = re.match(r"^[\s>*-]*[\[(<]\s*([^\])>]+)\s*[\])>]\s*(.+)$", stripped)
            if match:
                return [(match.group(1).strip(), match.group(2).strip())], True
            match = re.match(r"^[\s>*-]*([A-Za-z0-9]+)\s*[:\).\-]\s*(.+)$", stripped)
            if match:
                return [(match.group(1).strip(), match.group(2).strip())], True
            match = re.match(r"^(.+?)\s*[\[(<]\s*([^\])>]+)\s*[\])>]\s*$", stripped)
            if match:
                label = match.group(1).strip()
                token = match.group(2).strip()
                return [(token, label)], True

            columns = _split_option_columns(stripped)

            if pending_actions:
                if not columns and pending_actions:
                    columns = stripped.split()
                if columns:
                    if len(columns) >= len(pending_actions):
                        tokens: List[Tuple[str, str]] = []
                        for label, token in zip(pending_actions, columns):
                            cleaned = _clean_token(token)
                            if cleaned:
                                tokens.append((cleaned, label))
                        pending_actions = []
                        return tokens, True
                    pending_actions = []
                    return [], True
                pending_actions = []
                return [], False

            if len(columns) >= 2:
                recognized_labels: List[str] = []
                for column in columns:
                    if not canonical_action(column):
                        recognized_labels = []
                        break
                    recognized_labels.append(column)
                if len(recognized_labels) >= 2:
                    pending_actions = recognized_labels
                    return [], True

            return [], False

        def canonical_action(text: str) -> Optional[str]:
            lowered = text.lower()
            for action, aliases in _APPROVAL_ACTION_ALIASES.items():
                if any(alias in lowered for alias in aliases):
                    return action
            return None

        def build_prompt(block_lines: List[str]) -> Optional[ApprovalPrompt]:
            if not block_lines:
                return None
            header = block_lines[0].strip()
            body_lines: List[str] = []
            tokens: Dict[str, str] = {}
            for raw in block_lines[1:]:
                if is_dismissal(raw):
                    continue
                options, consumed = parse_option_line(raw)
                if options:
                    for token, label in options:
                        action = canonical_action(label)
                        if action:
                            tokens[action] = token.strip()
                    continue
                if consumed:
                    continue
                body_lines.append(raw)

            while body_lines and not body_lines[0].strip():
                body_lines.pop(0)
            while body_lines and not body_lines[-1].strip():
                body_lines.pop()

            body = "\n".join(body_lines)
            options = DEFAULT_APPROVAL_TOKENS.copy()
            for action, token in tokens.items():
                if token:
                    options[action] = token
            return ApprovalPrompt(header=header, body=body, options=options)

        def collect_block(start: int) -> Tuple[List[str], int, Optional[str]]:
            block = [lines[start]]
            idx = start + 1
            dismissal: Optional[str] = None
            while idx < len(lines):
                current = lines[idx]
                if is_header(current):
                    break
                if is_dismissal(current):
                    dismissal = current.strip()
                    block.append(current)
                    idx += 1
                    break
                block.append(current)
                if not current.strip():
                    lookahead = idx + 1
                    while lookahead < len(lines) and not lines[lookahead].strip():
                        block.append(lines[lookahead])
                        lookahead += 1
                    if lookahead >= len(lines):
                        idx = lookahead
                        break
                    if not line_is_prompt_content(lines[lookahead]):
                        idx = lookahead
                        break
                    idx = lookahead
                    continue
                idx += 1
            return block, idx, dismissal

        i = 0
        while i < len(lines):
            line = lines[i]
            if is_dismissal(line):
                flush_buffer()
                events.append(ParsedCodexEvent("dismissal", line.strip()))
                i += 1
                continue
            if is_header(line):
                flush_buffer()
                block, i, dismissal = collect_block(i)
                prompt = build_prompt(block)
                if prompt:
                    events.append(ParsedCodexEvent("prompt", prompt))
                else:
                    text = "\n".join(block).strip("\n")
                    if text.strip():
                        events.append(ParsedCodexEvent("text", text))
                if dismissal:
                    events.append(ParsedCodexEvent("dismissal", dismissal))
                continue
            buffer.append(line)
            i += 1

        flush_buffer()
        return events

    def _dismiss_active_approvals(self, reason: str) -> None:
        note = reason.strip() if reason else "Approval dismissed."
        for widget in self._approval_widgets:
            if widget.is_active():
                widget.mark_dismissed(note)

    def _handle_approval_decision(
        self,
        widget: ApprovalPromptWidget,
        action: str,
        token: str,
    ) -> None:
        if not self.bridge.running() or not self.bridge.pid:
            widget.mark_failed("Bridge inactive")
            self.view.append_message("system", "[Codex] Bridge not active. Unable to send approval.")
            return
        ok = self.bridge.send_text(token)
        if not ok:
            widget.mark_failed("Send failed")
            self._codex_status("[Codex] Approval send failed.")
            self.codex_led_signal.emit("red")
            return
        widget.mark_submitted(action)
        label = APPROVAL_ACTION_TITLES.get(action, action.title())
        self._codex_status(f"[Codex] Approval → {label}")
        self.codex_led_signal.emit("yellow")
        self.bridge.press_enter_async(self._ui_hwnd())

    @Slot(str)
    def _on_codex_output(self, reply_text: str):
        trimmed = reply_text.strip()
        if not trimmed:
            return
        if trimmed.lower() in _APPROVAL_TOKEN_STRINGS:
            return
        self._record_message("assistant", reply_text, [])
        events = self._parse_codex_approval_events(reply_text)
        if hasattr(self, "codex_interpreter"):
            self.codex_interpreter.observe_codex_output(reply_text)
        if not events:
            self.append_signal.emit(ChatMessage("assistant", reply_text, []))
            return

        for event in events:
            if event.kind == "text":
                text = str(event.payload)
                if text.strip():
                    self.append_signal.emit(ChatMessage("assistant", text, []))
            elif event.kind == "prompt":
                prompt = event.payload
                if isinstance(prompt, ApprovalPrompt):
                    self.append_signal.emit(
                        ChatMessage(
                            "assistant",
                            prompt.as_text(),
                            [],
                            kind="approval",
                            meta={"prompt": prompt},
                        )
                    )
                else:
                    text = str(prompt)
                    if text.strip():
                        self.append_signal.emit(ChatMessage("assistant", text, []))
            elif event.kind == "dismissal":
                reason = str(event.payload)
                self._dismiss_active_approvals(reason)
                if reason.strip():
                    self.append_signal.emit(ChatMessage("system", reason, []))

    def _model_label_text(self) -> str:
        return "Model: " f"<span style='color:{self.theme.model_name};font-weight:600'>{self.settings.get('chat_model', DEFAULT_CHAT_MODEL)}</span>"

    def _intro_message(self) -> str:
        return (
            f"{self.settings.get('chat_model', DEFAULT_CHAT_MODEL)} ready. "
            f"Local Ollama only (OCR/vision/embeddings). Context={self.context_pairs} pairs.\n"
            f"Vision-OCR={self.settings.get('vision_ocr_model', DEFAULT_VISION_OCR_MODEL)}. "
            f"Vision={self.settings.get('vision_model', DEFAULT_VISION_MODEL)}. "
            f"Embedder={self.settings.get('embed_model', DEFAULT_EMBED_MODEL)}.\n"
            "Codex-first terminal: Send → Codex (Ctrl+Enter). LED shows bridge health."
            " Type a file or folder fragment and press Tab to insert a workspace reference."
        )

    # ----- images -----
    @Slot(list)
    def _on_images_from_editor(self, paths: List[Path]):
        if not paths: return
        attached: List[Path] = []
        for p in paths:
            try:
                if p.suffix.lower() != ".png": p = self._convert_to_png(p)
                attached.append(p)
            except Exception: pass
        if attached:
            self.pending_images.extend(attached)
            lines = [f"Attached: {a.name}" for a in attached]
            if self.settings.get("enable_vision", True):
                lines.append("Images will be summarized on your next message.")
            self.view.append_message("system", "\n".join(lines))
            for a in attached:
                self.input.append(f'view_image "{a.as_posix()}"')

    @Slot(dict)
    def _on_reference_accepted(self, payload: Dict[str, str]) -> None:
        if not isinstance(payload, dict):
            return
        path = str(payload.get("path") or "").strip()
        if not path:
            return
        kind = str(payload.get("type") or "file")
        self._recent_input_references.append({"path": path, "type": kind})

    @Slot()
    def _attach_image(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Attach image(s)",
            str(agent_images_dir()),
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)",
        )
        if not paths: return
        attached: List[Path] = []
        for sp in paths:
            p = Path(sp)
            try:
                out = self._convert_to_png(p); attached.append(out)
            except Exception as e:
                self.view.append_message("assistant", f"Image attach failed: {e}")
        if attached:
            self.pending_images.extend(attached)
            lines = [f"Attached: {a.name}" for a in attached]
            if self.settings.get("enable_vision", True):
                lines.append("Images will be summarized on your next message.")
            self.view.append_message("system", "\n".join(lines))
            for a in attached:
                self.input.append(f'view_image "{a.as_posix()}"')

    def _convert_to_png(self, p: Path) -> Path:
        out = agent_images_dir() / (slug(p.stem) + ".png")
        ensure_dir(out.parent)
        if PIL_AVAILABLE:
            with Image.open(p) as im:
                im = im.convert("RGBA"); im.save(out, "PNG", optimize=True)
        else:
            shutil.copy2(p, out)
        return out

    # ----- local reply flow -----
    @Slot()
    def _on_send_local(self):
        if self.busy: return
        text = self.input.toPlainText().strip()
        images = self.pending_images
        if not text and not images:
            return
        references = self.input.consume_references()
        if text.startswith("/"):
            if images:
                self.pending_images = []
                self._emit_system_notice("Commands cannot include attached images.")
                self.input.clear()
                return
            handled = self._handle_command(text, references)
            if handled:
                self.pending_images = []
                self.input.clear()
                return
        self.pending_images = []
        self._record_message("user", text or "(image)", images, references=references)
        self.append_signal.emit(ChatMessage("user", text or "(image)", images))
        self.input.clear()
        threading.Thread(target=self._infer_thread, args=(text, images), daemon=True).start()

    def _handle_command(self, text: str, references: List[Dict[str, str]]) -> bool:
        try:
            tokens = shlex.split(text)
        except ValueError as exc:
            self._record_message("user", text, [], references=references)
            self.append_signal.emit(ChatMessage("user", text, []))
            self._emit_system_notice(f"Command parse error: {exc}")
            return True
        if not tokens:
            return False
        cmd = tokens[0].lower()
        if cmd == "/tasks":
            self._record_message("user", text, [], references=references)
            self.append_signal.emit(ChatMessage("user", text, []))
            self._command_tasks_list()
            return True
        if cmd != "/task":
            return False

        if len(tokens) < 2:
            self._record_message("user", text, [], references=references)
            self.append_signal.emit(ChatMessage("user", text, []))
            self._emit_system_notice(
                "Usage: /task \"title\" | /task <id> status <state> | /task <id> note <text>"
            )
            return True

        subject = tokens[1]
        is_task_id = self._looks_like_task_id(subject)

        if is_task_id and len(tokens) >= 3:
            action = tokens[2].lower()
            self._record_message("user", text, [], references=references)
            self.append_signal.emit(ChatMessage("user", text, []))
            if action == "status":
                status = tokens[3].lower() if len(tokens) >= 4 else ""
                self._command_task_status(subject, status)
                return True
            if action == "note":
                note_text = " ".join(tokens[3:]).strip()
                self._command_task_note(subject, note_text)
                return True
            self._emit_system_notice(
                "Usage: /task <id> status <state> | /task <id> note <text>"
            )
            return True

        title = " ".join(tokens[1:]).strip()
        self._record_message("user", text, [], references=references)
        self.append_signal.emit(ChatMessage("user", text, []))
        if not title:
            self._emit_system_notice("Task title required.")
        else:
            self._command_task_create(title)
        return True

    def _command_task_create(self, title: str) -> None:
        now = datetime.now(UTC).timestamp()
        task_id = f"tsk_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        task = Task(
            id=task_id,
            title=title,
            status="open",
            created_ts=now,
            updated_ts=now,
            session_id=self.session_id,
            source="terminal",
            codex_conversation_id=self.session_id,
        )
        try:
            append_task(task)
            append_event(TaskEvent(ts=now, task_id=task_id, event="created", by="terminal"))
        except Exception as exc:
            log_exception("Task creation failed", exc)
            self._emit_system_notice(f"Failed to create task: {exc}")
            return

        publish("task.created", task.to_dict())
        publish("task.updated", task.to_dict())
        self._emit_system_notice(f"Task created [{task_id}]: {title}")

    def _command_task_status(self, task_id: str, status: str) -> None:
        status_key = status.lower().strip()
        if status_key not in self._TASK_STATUSES:
            allowed = ", ".join(sorted(self._TASK_STATUSES))
            self._emit_system_notice(f"Unknown status '{status}'. Allowed: {allowed}.")
            return
        now = datetime.now(UTC).timestamp()
        try:
            updated = update_task(task_id, status=status_key, updated_ts=now)
            append_event(
                TaskEvent(
                    ts=now,
                    task_id=task_id,
                    event="status",
                    by="terminal",
                    to=status_key,
                )
            )
        except ValueError:
            self._emit_system_notice(f"Task not found: {task_id}")
            return
        except Exception as exc:
            log_exception("Task status update failed", exc)
            self._emit_system_notice(f"Failed to update task {task_id}: {exc}")
            return

        publish("task.status", {"id": updated.id, "status": updated.status})
        publish("task.updated", updated.to_dict())
        if status_key == "deleted":
            publish("task.deleted", {"id": updated.id})
        self._emit_system_notice(f"Task {task_id} status → {status_key}")

    def _command_task_note(self, task_id: str, note_text: str) -> None:
        note = note_text.strip()
        if not note:
            self._emit_system_notice("Task note cannot be empty.")
            return
        task = self._load_task(task_id)
        if task is None:
            self._emit_system_notice(f"Task not found: {task_id}")
            return

        dataset_dir = self.task_drawer.panel.dataset_path.parent
        try:
            _, relative, created = append_run_log(
                task,
                f"[{_utc_iso()}] {note}",
                dataset_dir,
            )
        except Exception as exc:
            log_exception("Task run-log write failed", exc)
            self._emit_system_notice(f"Failed to record note for {task_id}: {exc}")
            return

        now = datetime.now(UTC).timestamp()
        changes: Dict[str, Any] = {"updated_ts": now}
        if not task.run_log_path or created:
            changes["run_log_path"] = relative
        try:
            updated = update_task(task_id, **changes)
            append_event(
                TaskEvent(
                    ts=now,
                    task_id=task_id,
                    event="note",
                    by="terminal",
                    data={"text": note},
                )
            )
        except ValueError:
            self._emit_system_notice(f"Task not found: {task_id}")
            return
        except Exception as exc:
            log_exception("Task dataset update failed", exc)
            self._emit_system_notice(f"Failed to update task {task_id}: {exc}")
            return

        publish("task.updated", {**updated.to_dict(), "last_note": note})
        self._emit_system_notice(f"Task {task_id} note recorded.")

    def _command_tasks_list(self) -> None:
        self.task_drawer.refresh()
        tasks = [task for task in self._load_tasks() if task.session_id == self.session_id]
        if not tasks:
            self._emit_system_notice("No tasks recorded for this session yet.")
            return
        tasks.sort(key=lambda t: t.updated_ts, reverse=True)
        lines = []
        for task in tasks:
            added = task.diffs.added if task.diffs else 0
            removed = task.diffs.removed if task.diffs else 0
            timestamp = self._format_timestamp(task.updated_ts)
            lines.append(
                f"- [{task.status}] {task.id}: {task.title} (+{added} −{removed}) @ {timestamp}"
            )
        body = "Tasks for this session:\n" + "\n".join(lines)
        self._emit_system_notice(body)

    def _load_tasks(self) -> List[Task]:
        path = self.task_drawer.panel.dataset_path
        if not path.exists():
            return []
        records: List[Task] = []
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    records.append(Task.from_dict(payload))
                except Exception:
                    continue
        return records

    @staticmethod
    def _looks_like_task_id(candidate: str) -> bool:
        return bool(candidate) and bool(re.match(r"^tsk_[\w-]+", candidate))

    @staticmethod
    def _format_timestamp(ts: float) -> str:
        try:
            dt = datetime.fromtimestamp(float(ts))
        except Exception:
            return "--"
        return dt.strftime("%H:%M:%S")

    def _emit_system_notice(self, message: str) -> None:
        self._record_message("system", message, [])
        self.append_signal.emit(ChatMessage("system", message, []))

    def _error_console(self) -> Optional[ErrorConsole]:
        window = self.window()
        if window and hasattr(window, "error_console"):
            console = getattr(window, "error_console")
            if isinstance(console, ErrorConsole):
                return console
        return None

    @Slot(str)
    def _log_error_center(self, message: str) -> None:
        console = self._error_console()
        if console:
            console.log(message)

    @Slot(str)
    def _handle_error_notice(self, message: str) -> None:
        self._emit_system_notice(message)

    def detach_safety_notifier(self) -> None:
        if self._safety_notifier_id:
            safety_manager.remove_notifier(self._safety_notifier_id)
            self._safety_notifier_id = ""

    # ----- send to Codex -----
    @Slot()
    def _send_to_codex(self):
        txt = self.input.toPlainText().strip()
        if not txt:
            return
        if not self.bridge.running() or not self.bridge.pid:
            self.view.append_message("system", "[Codex] Bridge not active. Use Start Codex + Bridge.")
            return

        snapshot_refs: List[Dict[str, str]] = list(getattr(self.input, "_accepted_references", []))
        send_txt, notices = self._build_codex_prompt(txt, snapshot_refs, include_context=True)
        if not send_txt:
            self.view.append_message("system", f"→ Codex: {txt} ✗")
            return

        ok = self.bridge.send_text(send_txt)
        if ok:
            references = self.input.consume_references()
            self._record_message("user", txt, [], references=references)
            if hasattr(self, "codex_interpreter"):
                self.codex_interpreter.observe_user(txt)
            self.view.append_message("system", f"→ Codex: {txt} ✓")
            self.input.clear()
            # Immediately press Enter (non-blocking) and bring focus back
            self.bridge.press_enter_async(self._ui_hwnd())
            for note in notices:
                self._emit_system_notice(note)
        else:
            self.view.append_message("system", f"→ Codex: {txt} ✗")

    def _send_codex_auto(self, text: str) -> bool:
        payload, notices = self._build_codex_prompt(text.strip(), [], include_context=False)
        if not payload:
            return False
        ok = self.bridge.send_text(payload)
        if not ok:
            return False
        self.bridge.press_enter_async(self._ui_hwnd())
        for note in notices:
            self._emit_system_notice(note)
        return True

    def _handle_auto_follow_up(self, command: str) -> None:
        message = command.strip()
        if not message:
            return
        note = f"[Codex] Auto-continue → {message}"
        self._record_message("system", note, [])
        self.messages.append(ChatMessage("system", note, []))
        self.view.append_message("system", note)

    def _build_codex_prompt(
        self,
        text: str,
        references: Optional[List[Dict[str, str]]],
        *,
        include_context: bool,
    ) -> Tuple[str, List[str]]:
        references = references or []
        context_lines: List[str] = []
        if include_context and self.share_context:
            k = max(1, self.share_limit)
            if self.settings.get("enable_semantic", True):
                recs = self.conv.retrieve(text, k=k)
            else:
                recs = self.conv.recent(k)
            context_lines = [f"{r.get('role', 'user')}: {r.get('text', '')}" for r in recs]

        model = str(self.settings.get("chat_model", DEFAULT_CHAT_MODEL))
        guard_enabled = bool(
            self.settings.get(
                "reference_token_guard",
                DEFAULT_SETTINGS.get("reference_token_guard", True),
            )
        )
        headroom_pct = int(
            self.settings.get(
                "reference_token_headroom",
                DEFAULT_SETTINGS.get("reference_token_headroom", 80),
            )
        )
        budget = token_budget.prompt_token_budget(model, headroom_pct) if guard_enabled else 0
        message_tokens = token_budget.count_tokens(text, model)

        context_entries: List[Tuple[str, int]] = []
        for line in context_lines:
            context_entries.append((line, token_budget.count_tokens(line, model)))

        base_tokens = message_tokens + sum(tokens for _, tokens in context_entries)
        notices: List[str] = []

        if guard_enabled and budget > 0:
            dropped = 0
            while context_entries and base_tokens > budget:
                _, tokens = context_entries.pop(0)
                base_tokens -= tokens
                dropped += 1
            if dropped:
                plural = "s" if dropped != 1 else ""
                notices.append(
                    f"[Codex] Dropped {dropped} context item{plural} to fit the token budget."
                )
            if base_tokens > budget:
                notices.append(
                    "[Codex] Message exceeds the available token budget; reference contents skipped."
                )
                base_tokens = message_tokens
                context_entries.clear()

        context_lines = [line for line, _ in context_entries]
        payloads, payload_notices = self._reference_payloads(references)
        notices.extend(payload_notices)

        if guard_enabled and budget > 0:
            available = max(0, budget - base_tokens)
            included: List[str] = []
            skipped = 0
            for payload in payloads:
                tokens = token_budget.count_tokens(payload, model)
                if tokens <= available:
                    included.append(payload)
                    available -= tokens
                else:
                    skipped += 1
            if skipped:
                plural = "s" if skipped != 1 else ""
                notices.append(
                    f"[Codex] Skipped {skipped} reference payload{plural} due to token limits."
                )
            payloads = included

        base_section = "\n".join(context_lines + [text]) if context_lines else text
        parts: List[str] = []
        if base_section.strip():
            parts.append(base_section.strip())
        for payload in payloads:
            segment = payload.strip()
            if segment:
                parts.append(segment)
        return "\n\n".join(parts), notices

    def _reference_payloads(
        self, references: List[Dict[str, str]]
    ) -> Tuple[List[str], List[str]]:
        payloads: List[str] = []
        notices: List[str] = []
        embed_contents = bool(
            self.settings.get(
                "reference_embed_contents",
                DEFAULT_SETTINGS.get("reference_embed_contents", True),
            )
        )
        if not embed_contents:
            return payloads, notices

        for ref in references:
            path = str(ref.get("path") or "").strip()
            if not path:
                continue
            display = path
            candidate = Path(path)
            if not candidate.is_absolute():
                candidate = (self.workspace / path).resolve()
            else:
                candidate = candidate.resolve()

            if not candidate.exists():
                notices.append(f"[Codex] Reference missing: {display}")
                continue

            if candidate.is_dir():
                try:
                    entries = sorted(p.name for p in candidate.iterdir())
                except Exception as exc:
                    notices.append(f"[Codex] Could not read directory {display}: {exc}")
                    continue
                listing = "\n".join(entries[:50])
                payloads.append(f"# Directory: {display}\n{listing}")
                continue

            try:
                content = candidate.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:
                notices.append(f"[Codex] Could not read {display}: {exc}")
                continue

            body = content.rstrip()
            if body:
                payloads.append(f"# Reference: {display}\n```\n{body}\n```")
            else:
                payloads.append(f"# Reference: {display}\n(Empty file.)")

        return payloads, notices

    def _teardown_task_bus(self) -> None:
        if not getattr(self, "_task_bus_handles", None):
            return
        for handle in self._task_bus_handles:
            try:
                handle.unsubscribe()
            except Exception:
                logger.exception("Failed to unsubscribe task conversation handle")
        self._task_bus_handles.clear()

    def _handle_task_conversation(self, payload: dict) -> None:
        if not isinstance(payload, dict):
            return
        conv = str(payload.get("conversation_id") or payload.get("session_id") or "").strip()
        if not conv:
            return
        label = str(payload.get("id") or conv)
        self._load_conversation_transcript(conv, label=label)

    def _load_conversation_transcript(self, conversation_id: str, *, label: str = "") -> None:
        record = self.conv.resolve_conversation(conversation_id)
        if record is None:
            self.view.append_message("system", f"[Tasks] Conversation not found: {conversation_id}")
            return
        entries: List[ChatMessage] = []
        if record.jsonl_path.exists():
            try:
                with record.jsonl_path.open("r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        role = str(data.get("role") or "").strip()
                        text = data.get("text")
                        if not role or text is None:
                            continue
                        entries.append(ChatMessage(role, str(text), []))
            except Exception as exc:
                self.view.append_message("system", f"[Tasks] Failed to read conversation: {exc}")
                return
        elif record.markdown_path.exists():
            try:
                md_text = record.markdown_path.read_text(encoding="utf-8").strip()
            except Exception as exc:
                self.view.append_message("system", f"[Tasks] Failed to read conversation markdown: {exc}")
                return
            if md_text:
                entries.append(ChatMessage("system", md_text, []))

        self.messages = []
        self.view.clear()

        if entries:
            for msg in entries:
                self.messages.append(msg)
                self.view.append_message(msg.role, msg.text)
        else:
            empty_msg = ChatMessage("system", "[Tasks] Conversation log is empty.", [])
            self.messages.append(empty_msg)
            self.view.append_message(empty_msg.role, empty_msg.text)

        self._loaded_conversation_id = conversation_id
        origin = "archive" if record.source == "archive" else "session"
        note_label = label or conversation_id
        notice = ChatMessage("system", f"[Tasks] Conversation loaded ({origin}): {note_label}", [])
        self.messages.append(notice)
        self.view.append_message(notice.role, notice.text)

        if hasattr(self, "codex_interpreter") and self.codex_interpreter:
            last_user = next((m.text for m in reversed(self.messages) if m.role == "user"), "")
            if last_user:
                self.codex_interpreter.observe_user(last_user)

    # ----- Codex controls -----
    @Slot()
    def _start_codex_bridge(self):
        try:
            self.codex.ensure_ollama()
            exe = self.codex.ensure_release()
            s = load_codex_settings()
            model = s.get("model") or self.settings.get("chat_model", DEFAULT_CHAT_MODEL)

            raw_folder = str(s.get("working_folder") or "").strip()
            working_dir: Path = transit_dir()
            fallback_reason: Optional[str] = None
            candidate: Optional[Path] = None
            if raw_folder:
                try:
                    candidate = Path(raw_folder).expanduser()
                except Exception as exc:
                    fallback_reason = f"Working folder '{raw_folder}' is invalid ({exc})"
                else:
                    try:
                        if candidate.exists() and candidate.is_dir():
                            working_dir = candidate
                        elif candidate.exists():
                            fallback_reason = f"Working folder '{candidate}' is not a directory"
                        else:
                            fallback_reason = f"Working folder '{candidate}' does not exist"
                    except OSError as exc:
                        fallback_reason = f"Working folder '{candidate}' cannot be accessed ({exc})"
            else:
                fallback_reason = "Working folder not set"

            if fallback_reason:
                self.view.append_message(
                    "system",
                    (
                        f"[Codex] {fallback_reason}. Using default transit folder: "
                        f"{transit_dir()}"
                    ),
                )

            self.codex.write_config_toml(model)
            proc = self.codex.launch_codex_cmd(exe, model, working_dir)
            self.view.append_message("system", f"[Codex] Launched. PID={proc.pid}")
            self.bridge.attach(proc.pid)
            self.bridge.start()
            self.codex_led_signal.emit("yellow")
            self.btn_codex_start.setEnabled(False)
            self.btn_codex_stop.setEnabled(True)
            self._refresh_interpreter_toggle_enabled()
        except Exception as e:
            self.codex_led_signal.emit("red")
            self.view.append_message("system", f"[Codex Error] {e}")

    @Slot()
    def _stop_codex_bridge(self):
        try:
            self.bridge.stop()
            self.btn_codex_start.setEnabled(True)
            self.btn_codex_stop.setEnabled(False)
            self.view.append_message("system", "[Codex] Bridge stopped.")
            self._refresh_interpreter_toggle_enabled()
        except Exception as e:
            self.view.append_message("system", f"[Codex Error] {e}")

    # ----- core inference -----
    def _system_prompt(self) -> str:
        if hasattr(self, "_chat_prompt"):
            return self._chat_prompt.text()
        return prompt_text("chat_system")

    def _summarize_images_dual(self, images: List[Path], user_text: str) -> Tuple[List[str], List[str], str]:
        if not images:
            return [], [], ""

        ocr_list: List[str] = []
        vis_list: List[str] = []
        combined_parts: List[str] = []

        for original in images:
            path = original
            if path.suffix.lower() != ".png":
                try:
                    path = self._convert_to_png(path)
                except Exception as exc:
                    err = f"Image conversion failed for {original.name}: {exc}"
                    self.error_signal.emit(err)
                    ocr_list.append(f"[ocr-error] {err}")
                    vis_list.append("[vision-error] skipped — conversion failed")
                    continue

            ocr_res = perform_ocr(path)
            if not ocr_res.ok:
                err = f"OCR failed for {path.name}: {ocr_res.error}"
                self.error_signal.emit(err)
                ocr_md = f"[ocr-error] {ocr_res.error}"
            else:
                ocr_md = ocr_res.markdown

            try:
                ocr_path = path.with_suffix(path.suffix + ".ocr.md")
                ensure_dir(ocr_path.parent)
                ocr_path.write_text(ocr_md, encoding="utf-8")
            except Exception as exc:
                self.error_signal.emit(f"Failed to write OCR markdown for {path.name}: {exc}")

            ocr_list.append(ocr_md)

            vision_res = analyze_image(
                path,
                ocr_res.markdown if ocr_res.ok else "",
                client=self.ollama,
                model=self.settings.get("vision_model", DEFAULT_VISION_MODEL),
                user_text=user_text,
            )
            if not vision_res.ok:
                err = f"Vision summary failed for {path.name}: {vision_res.error}"
                self.error_signal.emit(err)
                vis_txt = f"[vision-error] {vision_res.error}"
            else:
                vis_txt = vision_res.summary

            try:
                vis_path = path.with_suffix(path.suffix + ".vision.md")
                ensure_dir(vis_path.parent)
                vis_path.write_text(vis_txt, encoding="utf-8")
            except Exception as exc:
                self.error_signal.emit(f"Failed to write vision markdown for {path.name}: {exc}")

            vis_list.append(vis_txt)
            combined_parts.append(f"## OCR (Markdown)\n{ocr_md}\n\n## Vision Interpretation\n{vis_txt}")

        combined = "\n\n".join(combined_parts)
        return ocr_list, vis_list, combined

    def _conversation_context(self, query: str) -> List[Dict[str, str]]:
        if not self.share_context:
            return []
        k = max(1, self.share_limit)
        if self.settings.get("enable_semantic", True):
            recs = self.conv.retrieve(query, k=k)
        else:
            recs = self.conv.recent(k)
        return [{"role": r.get("role", "user"), "content": r.get("text", "")} for r in recs]

    def _gather_context(self, query: str) -> List[Dict[str, str]]:
        memory_msgs = self._memory_messages()
        ctx = self._conversation_context(query)
        window = [{"role": m.role, "content": m.text} for m in self.messages[-2 * self.context_pairs:]]
        return memory_msgs + ctx + window

    def _record_message(
        self,
        role: str,
        text: str,
        images: List[Path],
        *,
        references: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        refs: List[Dict[str, str]] = []
        if references:
            for item in references:
                if not isinstance(item, dict):
                    continue
                path = str(item.get("path") or "").strip()
                if not path:
                    continue
                kind = str(item.get("type") or "file")
                refs.append({"path": path, "type": kind})

        self.conv.append(role, text, images, references=refs or None)
        tags = self.lex.auto_tags(text)
        extra = {"references": refs} if refs else None
        self.dataset.add_entry(role, text, images, tags=tags, extra=extra)
        if role == "user":
            self._store_session_note(text, images)

    def _infer_thread(self, text: str, images: List[Path]):
        self.state_signal.emit(True)
        try:
            chat_model = self.settings.get("chat_model", DEFAULT_CHAT_MODEL)
            msgs: List[Dict[str, Any]] = [{"role": "system", "content": self._system_prompt()}]
            msgs += self._gather_context(text)
            if images and self.settings.get("enable_vision", True):
                ocr_list, vis_list, combo = self._summarize_images_dual(images, text)
                for ocr_md in ocr_list:
                    self.dataset.add_entry("assistant", ocr_md, images, tags=["vision_ocr"])
                    self.append_signal.emit(ChatMessage("assistant", f"## OCR (Markdown)\n{ocr_md}", []))
                for vis_txt in vis_list:
                    self.dataset.add_entry("assistant", vis_txt, images, tags=["vision_interpret"])
                    self.append_signal.emit(ChatMessage("assistant", f"## Vision Interpretation\n{vis_txt}", []))
                if combo:
                    self.dataset.add_entry("assistant", combo, images, tags=["vision_summary"])
                    self.conv.append("system", "_Image(s) summarized via OCR + Vision. Injected into context._", [])
                    msgs.append({"role": "system", "content": f"Image context:\n{combo}"})
            user_msg = {"role": "user", "content": text or "(image)"}
            ok, content, err = self.ollama.chat(model=chat_model, messages=msgs + [user_msg])
            if not ok: content = f"[Error] Ollama: {err or 'Unknown error'}"
            self.dataset.add_entry("assistant", content, [], tags=self.lex.auto_tags(content))
            self._record_message("assistant", content, [])
            self.append_signal.emit(ChatMessage("assistant", content, [], chat_model))
        except Exception as e:
            err = f"[Error] {e}"
            self.dataset.add_entry("assistant", err, [], tags=["error"])
            self._record_message("assistant", err, [])
            self.append_signal.emit(ChatMessage("assistant", err, []))
        finally:
            self.state_signal.emit(False)

    @Slot(ChatMessage)
    def _render_message(self, msg: ChatMessage):
        self.messages.append(msg)
        if msg.kind == "approval":
            prompt = msg.meta.get("prompt")
            if isinstance(prompt, ApprovalPrompt):
                widget = ApprovalPromptWidget(self.theme, prompt, self._handle_approval_decision)
                self._approval_widgets.append(widget)
                self.view.append_widget(widget, role="assistant", alignment=Qt.AlignLeft)
                return
        text = msg.text
        thinks = re.findall(r"<think>(.*?)</think>", text, flags=re.DOTALL)
        text = re.sub(r"<think>(.*?)</think>", "", text, flags=re.DOTALL)
        think_lines = [t.strip() for t in thinks if t.strip()] if msg.role == "assistant" else []
        model_name = msg.model_name if msg.role == "assistant" else ""
        self.view.append_message(
            msg.role,
            text,
            model_name=model_name,
            thinks=think_lines,
            images=msg.images,
        )

    @Slot(bool)
    def _set_busy(self, state: bool):
        self.busy = state
        enabled = not state
        self.send_btn.setEnabled(enabled)
        self.attach_btn.setEnabled(enabled)
        self.send_codex_btn.setEnabled(True if self.bridge.running() else True)

    @staticmethod
    def _qss(t: Theme) -> str:
        return f"""
        QFrame#ChatCard {{
            background-color: {t.card_bg};
            border: 1px solid {t.card_border};
            border-radius: {t.card_radius}px;
        }}
        QFrame#Header {{
            background-color: {t.header_bg};
            border-top-left-radius: {t.card_radius}px;
            border-top-right-radius: {t.card_radius}px;
        }}
        QLabel#Title {{ color: {t.header_text}; font-weight: 600; letter-spacing: 0.5px; }}
        QLabel#ModelLabel {{ color: {t.header_text}; }}
        QLabel#InterpreterCaption {{ color: {t.header_text}; font-weight: 600; }}
        QFrame#ConversationView {{
            background: {t.card_bg};
            border-top: 1px solid {t.card_border};
            border-bottom: 1px solid {t.card_border};
        }}
        QScrollArea#ConversationScroll {{
            background: transparent;
            border: none;
        }}
        QWidget#ConversationContainer {{
            background: {t.card_bg};
        }}
        QFrame#MessageRow {{
            background: transparent;
        }}
        QFrame#MessageBubble[role="user"] {{
            background: {t.user_bubble};
            color: {t.user_text};
            border: 1px solid {t.card_border};
            border-radius: 10px;
        }}
        QFrame#MessageBubble[role="assistant"] {{
            background: {t.ai_bubble};
            color: {t.ai_text};
            border: 1px solid {t.card_border};
            border-radius: 10px;
        }}
        QFrame#MessageBubble[role="system"] {{
            background: {t.muted};
            color: {t.ai_text};
            border: 1px solid {t.card_border};
            border-radius: 10px;
        }}
        QLabel#MessageName[role="user"] {{
            color: {t.user_text};
            font-weight: 600;
        }}
        QLabel#MessageName[role="assistant"] {{
            color: {t.model_name};
            font-weight: 600;
        }}
        QLabel#ModelNameLabel {{
            color: {t.model_name};
            font-weight: 600;
        }}
        QLabel#ThinkText {{
            color: {t.think_text};
            font-style: italic;
            font-size: 11pt;
        }}
        QLabel#MessageText {{
            font-size: 12.5pt;
        }}
        QLabel#MessageText[role="assistant"] {{
            color: {t.ai_text};
        }}
        QLabel#MessageText[role="user"] {{
            color: {t.user_text};
        }}
        QFrame#ApprovalPrompt {{
            background: {t.ai_bubble};
            border: 1px solid {t.card_border};
            border-radius: 10px;
        }}
        QLabel#ApprovalHeader {{
            color: {t.model_name};
            font-weight: 600;
        }}
        QLabel#ApprovalBody {{
            color: {t.ai_text};
            font-size: 12.5pt;
        }}
        QLabel#ApprovalStatus {{
            color: {t.think_text};
            font-style: italic;
        }}
        QPushButton#ApprovalButton {{
            background: {t.accent};
            color: #ffffff;
            border: 1px solid {t.card_border};
            border-radius: 6px;
            padding: 6px 10px;
            font-weight: 600;
        }}
        QPushButton#ApprovalButton:disabled {{
            background: #1f2d42;
            color: #8aa4c2;
            border-color: {t.card_border};
        }}
        QLabel#AttachmentLabel {{
            color: {t.header_text};
            font-family: "Cascadia Code", "Fira Code", monospace;
        }}
        QFrame#InputBar {{
            background-color: {t.card_bg};
            border-bottom-left-radius: {t.card_radius}px;
            border-bottom-right-radius: {t.card_radius}px;
        }}
        QTextEdit#InputMulti {{
            background: #0c1524;
            color: {t.ai_text};
            border: 1px solid {t.card_border};
            border-radius: 6px;
            padding: 8px 10px;
            selection-background-color: {t.accent};
            selection-color: #ffffff;
        }}
        QPushButton {{
            color: #ffffff;
            background-color: {t.accent};
            border: 1px solid {t.card_border};
            border-radius: 6px;
            padding: 6px 12px;
        }}
        QPushButton:hover {{ background-color: {t.accent_hover}; }}
        QPushButton:disabled {{ background-color: #2a3a59; color: #9fb3d4; }}
        """

# --------------------------------------------------------------------------------------
# Virtual desktop (canvas + draggable card)
# --------------------------------------------------------------------------------------

class VirtualCanvas(QWidget):
    def __init__(self, theme: Theme, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = theme
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setAutoFillBackground(False)
        self._bg_manager = BackgroundManager(self)
        self._bg_manager.register(BackgroundMode.STATIC, lambda canvas: StaticImageBg(canvas))
        self._bg_manager.register(BackgroundMode.GIF, lambda canvas: GifBg(canvas))
        self._bg_manager.register(BackgroundMode.VIDEO, lambda canvas: VideoBg(canvas))
        self._bg_manager.register(BackgroundMode.GL, lambda canvas: GLViewportBg(canvas))
        self._bg_config = BackgroundConfig()

    def ensure_minimum(self, viewport_size: QSize):
        screen = self.window().windowHandle().screen() if self.window() and self.window().windowHandle() else None
        geo = (screen.availableGeometry() if screen else QGuiApplication.primaryScreen().availableGeometry())
        min_w = max(viewport_size.width(), geo.width())
        min_h = max(viewport_size.height(), geo.height())
        if self.width() != min_w or self.height() != min_h:
            self.resize(min_w, min_h)

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        painted = self._bg_manager.paint(p, rect)
        if not painted:
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0.0, QColor(self.theme.desktop_top))
            grad.setColorAt(0.55, QColor(self.theme.desktop_mid))
            grad.setColorAt(1.0, QColor(self.theme.desktop_top))
            p.fillRect(rect, grad)
        glow = QColor(self.theme.desktop_edge_glow); glow.setAlphaF(0.18); p.setPen(glow)
        for i in range(20):
            r = rect.adjusted(10 + i, 10 + i, -10 - i, -10 - i); p.drawRoundedRect(r, 18, 18)
        vignette = QColor(0, 0, 0, 120); p.setPen(Qt.NoPen); p.setBrush(vignette)
        path = QPainterPath(); path.addRect(rect)
        inner = rect.adjusted(30, 30, -30, -30); inner_path = QPainterPath(); inner_path.addRoundedRect(QRectF(inner), 26, 26)
        path = path.subtracted(inner_path); p.drawPath(path)

    def resizeEvent(self, event):  # pragma: no cover - Qt plumbing
        super().resizeEvent(event)
        self._bg_manager.resize(event.size())

    def background_config(self) -> BackgroundConfig:
        return BackgroundConfig.from_state(self._bg_config.to_state())

    def set_background_config(self, config: BackgroundConfig) -> None:
        self._apply_background_config(config)

    def _apply_background_config(self, config: BackgroundConfig) -> None:
        self._bg_config = BackgroundConfig.from_state(config.to_state())
        mode = self._bg_config.mode
        source = self._bg_config.source
        if mode == BackgroundMode.SOLID or not source:
            self._bg_manager.clear()
            self.update()
            return
        src_path = Path(source)
        if not src_path.exists():
            self._bg_manager.clear()
            self.update()
            return
        self._bg_manager.apply(self._bg_config)
        self.update()

class CameraView(QScrollArea):
    def __init__(self, canvas: VirtualCanvas, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setWidgetResizable(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(canvas)
        self.canvas = canvas

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.canvas.ensure_minimum(self.viewport().size())


class TerminalDesktopIcon(QToolButton):
    def __init__(
        self,
        theme: Theme,
        path: str,
        parent: QWidget,
        grid_size: Tuple[int, int],
        size_mode: str,
    ):
        super().__init__(parent)
        self.theme = theme
        self.path = path
        self._grid_size = grid_size
        self._size_mode = size_mode
        self._drag_active = False
        self._press_pos = QPoint()
        self._moved = False
        self.setAcceptDrops(False)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setCursor(Qt.OpenHandCursor)
        base = os.path.basename(path)
        self.setText(os.path.splitext(base)[0] if os.path.isfile(path) else base)
        self._apply_size_mode()
        self._pick_icon()
        self.setStyleSheet("QToolButton{color:#eaf2ff;}")

    # ------------------------------------------------------------------
    def set_size_mode(self, mode: str) -> None:
        mode = mode if mode in {"small", "medium", "large"} else "medium"
        if mode == self._size_mode:
            return
        self._size_mode = mode
        self._apply_size_mode()

    def _apply_size_mode(self) -> None:
        if self._size_mode == "small":
            self.setIconSize(QSize(32, 32))
        elif self._size_mode == "large":
            self.setIconSize(QSize(64, 64))
        else:
            self.setIconSize(QSize(48, 48))

    def _pick_icon(self) -> None:
        p = Path(self.path)
        style = QApplication.style()
        if p.is_dir():
            self.setIcon(style.standardIcon(QStyle.SP_DirIcon))
            return
        ext = p.suffix.lower()
        if ext in {".txt", ".md", ".log", ".ini", ".cfg", ".json"}:
            icon = QIcon.fromTheme("text-x-generic") or style.standardIcon(QStyle.SP_FileIcon)
        elif ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}:
            icon = QIcon.fromTheme("image-x-generic") or style.standardIcon(QStyle.SP_FileIcon)
        elif ext == ".py":
            icon = QIcon.fromTheme("text-x-python") or style.standardIcon(QStyle.SP_FileIcon)
        else:
            icon = style.standardIcon(QStyle.SP_FileIcon)
        self.setIcon(icon)

    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self._drag_active = True
            self._press_pos = event.position().toPoint()
            self._moved = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active:
            delta = event.position().toPoint() - self._press_pos
            if delta.manhattanLength() > 4:
                self._moved = True
                new_pos = self.pos() + delta
                parent_rect = self.parentWidget().rect()
                new_pos.setX(max(6, min(new_pos.x(), parent_rect.width() - self.width() - 6)))
                new_pos.setY(max(30, min(new_pos.y(), parent_rect.height() - self.height() - 30)))
                self.move(new_pos)
                self._press_pos = event.position().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_active:
            self.setCursor(Qt.OpenHandCursor)
            moved = self._moved
            self._drag_active = False
            self._moved = False
            canvas: Optional[TerminalDesktopCanvas] = self.parentWidget()  # type: ignore
            if moved and isinstance(canvas, TerminalDesktopCanvas):
                grid_w, grid_h = self._grid_size
                x = round(self.x() / grid_w) * grid_w
                y = round(self.y() / grid_h) * grid_h
                self.move(x, y)
                for sibling in canvas.findChildren(TerminalDesktopIcon):
                    if (
                        sibling is not self
                        and sibling.geometry().contains(
                            self.mapToParent(QPoint(0, 0)) + self.rect().center()
                        )
                        and os.path.isdir(sibling.path)
                    ):
                        canvas._move_file_to_folder(self.path, sibling.path)
                        break
                canvas.save_icon_position(self.path, self.pos())
            elif isinstance(canvas, TerminalDesktopCanvas):
                canvas.open_path(self.path)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            canvas: Optional[TerminalDesktopCanvas] = self.parentWidget()  # type: ignore
            if isinstance(canvas, TerminalDesktopCanvas):
                canvas.open_path(self.path)
        super().mouseDoubleClickEvent(event)

    # ------------------------------------------------------------------
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        act_open = menu.addAction("Open")
        act_rename = menu.addAction("Rename")
        act_delete = menu.addAction("Delete")
        act_props = menu.addAction("Properties")
        chosen = menu.exec(event.globalPos())
        canvas: Optional[TerminalDesktopCanvas] = self.parentWidget()  # type: ignore
        if not isinstance(canvas, TerminalDesktopCanvas):
            return
        if chosen == act_open:
            canvas.open_path(self.path)
        elif chosen == act_rename:
            new_name, ok = QInputDialog.getText(
                self,
                "Rename",
                "New name (extensions allowed):",
                text=os.path.basename(self.path),
            )
            if ok and new_name:
                new_name = new_name.strip()
                if not new_name:
                    return
                dst = os.path.join(os.path.dirname(self.path), new_name)
                try:
                    os.rename(self.path, dst)
                    owner = canvas.parent_desktop()
                    if owner:
                        owner.forget_icon_position(self.path)
                except Exception as exc:  # pragma: no cover - UI feedback path
                    QMessageBox.warning(self, "Rename", f"Rename failed: {exc}")
                finally:
                    canvas._refresh_icons()
        elif chosen == act_delete:
            try:
                if os.path.isdir(self.path):
                    shutil.rmtree(self.path)
                else:
                    os.remove(self.path)
                owner = canvas.parent_desktop()
                if owner:
                    owner.forget_icon_position(self.path)
            except Exception as exc:  # pragma: no cover - UI feedback path
                QMessageBox.warning(self, "Delete", f"Delete failed: {exc}")
            finally:
                canvas._refresh_icons()
        elif chosen == act_props:
            size = 0
            try:
                if os.path.isdir(self.path):
                    for entry in Path(self.path).rglob("*"):
                        if entry.is_file():
                            size += entry.stat().st_size
                else:
                    size = os.path.getsize(self.path)
            except Exception:
                size = 0
            QMessageBox.information(
                self,
                "Properties",
                f"Path: {self.path}\nSize: {size} bytes",
            )


class TerminalDesktopCanvas(VirtualCanvas):
    def __init__(self, theme: Theme, parent: Optional[QWidget] = None):
        super().__init__(theme, parent)
        ensure_dir(terminal_desktop_dir())
        self._icons: Dict[str, TerminalDesktopIcon] = {}
        self._grid_size = (92, 90)
        self._last_sorted_paths: List[str] = []
        self._watcher = QFileSystemWatcher(self)
        try:
            self._watcher.addPath(str(terminal_desktop_dir()))
        except Exception:
            pass
        self._watcher.directoryChanged.connect(lambda _path: self._refresh_icons())
        self._watcher.fileChanged.connect(lambda _path: self._refresh_icons())
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._desktop_context)
        QTimer.singleShot(0, self._refresh_icons)

    # ------------------------------------------------------------------
    def parent_desktop(self) -> Optional["TerminalDesktop"]:
        parent = self.parentWidget()
        return parent if isinstance(parent, TerminalDesktop) else None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._arrange_icons()

    def _refresh_icons(self) -> None:
        ensure_dir(terminal_desktop_dir())
        entries = self._sorted_workspace_entries()
        want_paths = [str(p) for p in entries]
        want_set = set(want_paths)
        current_paths = set(self._icons.keys())
        removed = current_paths - want_set
        parent = self.parent_desktop()
        for path in list(removed):
            icon = self._icons.pop(path, None)
            if icon:
                icon.setParent(None)
                icon.deleteLater()
            if parent:
                parent.forget_icon_position(path)
        for idx, path in enumerate(want_paths):
            icon = self._icons.get(path)
            if not icon:
                icon = TerminalDesktopIcon(
                    self.theme,
                    path,
                    self,
                    self._grid_size,
                    self._current_icon_size(),
                )
                icon.show()
                self._icons[path] = icon
                stored = self.restore_icon_position(path)
                if stored is not None:
                    icon.move(stored)
                else:
                    self._position_icon(icon, idx)
            else:
                icon.path = path
                icon.set_size_mode(self._current_icon_size())
        self._last_sorted_paths = want_paths
        self._arrange_icons_if_needed()
        QApplication.processEvents()

    def _position_icon(self, icon: TerminalDesktopIcon, index: int) -> None:
        cols = max(1, int((self.width() - 60) / self._grid_size[0]))
        row, col = divmod(index, cols)
        pos = QPoint(30 + col * self._grid_size[0], 40 + row * self._grid_size[1])
        icon.move(pos)
        self.save_icon_position(icon.path, pos)

    def _arrange_icons(self) -> None:
        if not self._icons:
            return
        if self.parent_desktop() and self.parent_desktop().sort_mode() in {"type", "date"}:
            self._arrange_icons_if_needed(force=True)

    def _arrange_icons_if_needed(self, force: bool = False) -> None:
        parent = self.parent_desktop()
        if not parent:
            return
        if not force and parent.sort_mode() not in {"type", "date"}:
            return
        paths = self._last_sorted_paths or [str(p) for p in self._sorted_workspace_entries()]
        cols = max(1, int((self.width() - 60) / self._grid_size[0]))
        for idx, path in enumerate(paths):
            icon = self._icons.get(path)
            if not icon:
                continue
            row, col = divmod(idx, cols)
            pos = QPoint(30 + col * self._grid_size[0], 40 + row * self._grid_size[1])
            icon.move(pos)
            self.save_icon_position(path, pos)

    def _sorted_workspace_entries(self) -> List[Path]:
        root = terminal_desktop_dir()
        try:
            entries = list(root.iterdir())
        except Exception:
            return []
        mode = self.parent_desktop().sort_mode() if self.parent_desktop() else "name"
        mode = mode if mode in {"name", "type", "date"} else "name"

        def base_key(path: Path) -> int:
            return 0 if path.is_dir() else 1

        if mode == "type":
            entries.sort(key=lambda p: (base_key(p), p.suffix.lower(), p.name.lower()))
        elif mode == "date":
            def mtime(path: Path) -> float:
                try:
                    return float(path.stat().st_mtime)
                except Exception:
                    return 0.0

            entries.sort(key=lambda p: (base_key(p), -mtime(p), p.name.lower()))
        else:
            entries.sort(key=lambda p: (base_key(p), p.name.lower()))
        return entries

    # ------------------------------------------------------------------
    def _current_icon_size(self) -> str:
        parent = self.parent_desktop()
        return parent.icon_size() if parent else "medium"

    def _current_background_config(self) -> BackgroundConfig:
        parent = self.parent_desktop()
        return parent.background_config() if parent else BackgroundConfig()

    def save_icon_position(self, path: str, pos: QPoint) -> None:
        parent = self.parent_desktop()
        if parent:
            parent.save_icon_position(path, pos)

    def restore_icon_position(self, path: str) -> Optional[QPoint]:
        parent = self.parent_desktop()
        return parent.restore_icon_position(path) if parent else None

    # ------------------------------------------------------------------
    def _set_icon_size(self, mode: str) -> None:
        parent = self.parent_desktop()
        if parent:
            parent.set_icon_size(mode)
        for icon in self._icons.values():
            icon.set_size_mode(self._current_icon_size())

    def _set_sort_mode(self, mode: str) -> None:
        parent = self.parent_desktop()
        if parent:
            parent.set_sort_mode(mode)
        self._refresh_icons()

    def _set_background_fit(self, fit: BackgroundFit) -> None:
        parent = self.parent_desktop()
        if not parent:
            return
        config = parent.background_config()
        config.fit = fit
        parent.set_background_config(config)

    def _select_background(self, mode: BackgroundMode) -> None:
        parent = self.parent_desktop()
        if not parent:
            return
        config = parent.background_config()
        config.mode = mode
        if mode == BackgroundMode.SOLID:
            config.source = ""
            parent.set_background_config(config)
            return
        path = self._prompt_background_path(mode)
        if not path:
            return
        config.source = path
        if mode in (BackgroundMode.STATIC, BackgroundMode.GIF) and not isinstance(config.fit, BackgroundFit):
            config.fit = BackgroundFit.FILL
        if mode == BackgroundMode.VIDEO:
            config.loop = True
            config.mute = True
        parent.set_background_config(config)

    def _background_prompt_details(self, mode: BackgroundMode) -> Tuple[str, str]:
        filters = {
            BackgroundMode.STATIC: "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
            BackgroundMode.GIF: "GIF images (*.gif)",
            BackgroundMode.VIDEO: "Videos (*.mp4 *.mov *.mkv *.avi *.webm)",
            BackgroundMode.GL: "Python Scripts (*.py)",
        }
        captions = {
            BackgroundMode.STATIC: "Choose Background Image",
            BackgroundMode.GIF: "Choose Animated GIF",
            BackgroundMode.VIDEO: "Choose Background Video",
            BackgroundMode.GL: "Choose GL Background Script",
        }
        return filters.get(mode, "*"), captions.get(mode, "Choose Background")

    def _prompt_background_path(self, mode: BackgroundMode) -> Optional[str]:
        filt, caption = self._background_prompt_details(mode)
        path, _ = QFileDialog.getOpenFileName(self, caption, str(terminal_desktop_dir()), filt)
        if not path or not os.path.isfile(path):
            return None
        return path

    # ------------------------------------------------------------------
    def _desktop_context(self, pos: QPoint) -> None:
        menu = QMenu(self)
        view_menu = menu.addMenu("View")
        size_mode = self._current_icon_size()
        size_actions = {
            "large": view_menu.addAction("Large icons"),
            "medium": view_menu.addAction("Medium icons"),
            "small": view_menu.addAction("Small icons"),
        }
        for key, action in size_actions.items():
            action.setCheckable(True)
            action.setChecked(size_mode == key)
            action.triggered.connect(lambda _checked, mode=key: self._set_icon_size(mode))

        sort_menu = menu.addMenu("Sort by")
        current_sort = self.parent_desktop().sort_mode() if self.parent_desktop() else "name"
        for key, label in (("name", "Name"), ("type", "Type"), ("date", "Date modified")):
            action = sort_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(current_sort == key)
            action.triggered.connect(lambda _checked, mode=key: self._set_sort_mode(mode))

        menu.addAction("Refresh", self._refresh_icons)
        menu.addSeparator()
        new_menu = menu.addMenu("New")
        new_menu.addAction("Folder", self._new_folder_desktop)
        new_menu.addAction("Text File", self._new_text_desktop)
        new_menu.addAction("Markdown File", self._new_markdown_desktop)
        new_menu.addAction("JSON File", self._new_json_desktop)
        new_menu.addAction("Python File", self._new_python_desktop)
        new_menu.addAction("PowerShell Script", self._new_powershell_desktop)
        new_menu.addAction("ZIP Archive", self._new_zip_desktop)
        new_menu.addAction("Shortcut", self._new_shortcut_desktop)
        menu.addSeparator()
        personalize = menu.addMenu("Personalize")
        personalize.addAction("Solid color", lambda: self._select_background(BackgroundMode.SOLID))
        personalize.addAction("Image…", lambda: self._select_background(BackgroundMode.STATIC))
        personalize.addAction("Animated GIF…", lambda: self._select_background(BackgroundMode.GIF))
        personalize.addAction("Video…", lambda: self._select_background(BackgroundMode.VIDEO))
        personalize.addAction("Live GL viewport…", lambda: self._select_background(BackgroundMode.GL))
        fit_menu = personalize.addMenu("Image fit")
        cfg = self._current_background_config()
        fit_menu.setEnabled(cfg.mode in (BackgroundMode.STATIC, BackgroundMode.GIF))
        for fit, label in (
            (BackgroundFit.FILL, "Fill"),
            (BackgroundFit.FIT, "Fit"),
            (BackgroundFit.CENTER, "Center"),
            (BackgroundFit.TILE, "Tile"),
        ):
            action = fit_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(cfg.fit == fit)
            action.triggered.connect(lambda _checked, f=fit: self._set_background_fit(f))
        menu.exec(self.mapToGlobal(pos))

    # ------------------------------------------------------------------
    def _unique_path(self, base_name: str, extension: str = "") -> Path:
        root = terminal_desktop_dir()
        candidate = root / f"{base_name}{extension}"
        if not candidate.exists():
            return candidate
        idx = 1
        while True:
            alt = root / f"{base_name} ({idx}){extension}"
            if not alt.exists():
                return alt
            idx += 1

    def _create_text_file(self, base_name: str, extension: str, contents: str = "") -> None:
        try:
            path = self._unique_path(base_name, extension)
            path.write_text(contents, encoding="utf-8")
            self._refresh_icons()
        except Exception as exc:  # pragma: no cover - log only path
            logger.warning("terminal desktop new file failed: %s", exc)

    def _new_folder_desktop(self) -> None:
        try:
            path = self._unique_path("New Folder")
            path.mkdir()
            self._refresh_icons()
        except Exception as exc:  # pragma: no cover - log only path
            logger.warning("terminal desktop new folder failed: %s", exc)

    def _new_text_desktop(self) -> None:
        self._create_text_file("New Text File", ".txt")

    def _new_markdown_desktop(self) -> None:
        self._create_text_file("New Markdown File", ".md", "# New Markdown File\n\n")

    def _new_json_desktop(self) -> None:
        self._create_text_file("New JSON File", ".json", "{\n\n}\n")

    def _new_python_desktop(self) -> None:
        self._create_text_file("New Python File", ".py", "#!/usr/bin/env python3\n\n\"\"\"New script.\"\"\"\n\n")

    def _new_powershell_desktop(self) -> None:
        self._create_text_file("New PowerShell Script", ".ps1", "Write-Host 'Hello from Codex Terminal'\n")

    def _new_zip_desktop(self) -> None:
        try:
            path = self._unique_path("New Archive", ".zip")
            with zipfile.ZipFile(path, "w"):
                pass
            self._refresh_icons()
        except Exception as exc:  # pragma: no cover - log only path
            logger.warning("terminal desktop new zip failed: %s", exc)

    def _new_shortcut_desktop(self) -> None:
        try:
            path = self._unique_path("New Shortcut", ".shortcut.json")
            payload = {"target": "", "args": [], "working_dir": ""}
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            self._refresh_icons()
        except Exception as exc:  # pragma: no cover - log only path
            logger.warning("terminal desktop new shortcut failed: %s", exc)

    # ------------------------------------------------------------------
    def _move_file_to_folder(self, src: str, dst_folder: str) -> None:
        try:
            shutil.move(src, dst_folder)
            self._refresh_icons()
        except Exception as exc:  # pragma: no cover - log only path
            logger.warning("terminal desktop move failed: %s", exc)

    def open_path(self, path: str) -> None:
        target = Path(path)
        if not target.exists():
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(target))):
            QMessageBox.information(
                self,
                "Open",
                f"Unable to open {target}. Open it manually if needed.",
            )

class DraggableProxy(QFrame):
    geometry_changed = Signal(QRect)

    _EDGE_MARGIN = 12
    _LEFT = 0x01
    _RIGHT = 0x02
    _TOP = 0x04
    _BOTTOM = 0x08

    def __init__(self, inner: QWidget, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(inner)
        self.inner = inner
        self._drag_active = False
        self._mode: Optional[str] = None
        self._resize_edges = 0
        self._press_pos = QPoint(0, 0)
        self._start_geom = QRect()
        self._user_min = QSize(980, 600)
        self._cursor_edges = 0

    # ----- sizing helpers -----
    def _effective_min_width(self) -> int:
        inner_hint = self.inner.minimumSizeHint().width()
        inner_min = self.inner.minimumWidth()
        return max(self._user_min.width(), inner_hint, inner_min)

    def _effective_min_height(self) -> int:
        inner_hint = self.inner.minimumSizeHint().height()
        inner_min = self.inner.minimumHeight()
        return max(self._user_min.height(), inner_hint, inner_min)

    def minimum_size(self) -> QSize:
        return QSize(self._effective_min_width(), self._effective_min_height())

    def set_content_min_size(self, width: int, height: int) -> None:
        width = max(width, 0)
        height = max(height, 0)
        new_min = QSize(width, height)
        if new_min != self._user_min:
            self._user_min = new_min
        target_w = max(self.width(), self._effective_min_width())
        target_h = max(self.height(), self._effective_min_height())
        if target_w != self.width() or target_h != self.height():
            self.resize(target_w, target_h)
            self._keep_within_parent()
            self._emit_geometry()

    # ----- cursor helpers -----
    def _hit_edges(self, pos: QPoint) -> int:
        rect = self.rect()
        edges = 0
        if pos.x() <= self._EDGE_MARGIN:
            edges |= self._LEFT
        elif pos.x() >= rect.width() - self._EDGE_MARGIN:
            edges |= self._RIGHT
        if pos.y() <= self._EDGE_MARGIN:
            edges |= self._TOP
        elif pos.y() >= rect.height() - self._EDGE_MARGIN:
            edges |= self._BOTTOM
        return edges

    def _cursor_for_edges(self, edges: int) -> Qt.CursorShape:
        if edges & self._LEFT and edges & self._TOP:
            return Qt.SizeFDiagCursor
        if edges & self._RIGHT and edges & self._BOTTOM:
            return Qt.SizeFDiagCursor
        if edges & self._RIGHT and edges & self._TOP:
            return Qt.SizeBDiagCursor
        if edges & self._LEFT and edges & self._BOTTOM:
            return Qt.SizeBDiagCursor
        if edges & (self._LEFT | self._RIGHT):
            return Qt.SizeHorCursor
        if edges & (self._TOP | self._BOTTOM):
            return Qt.SizeVerCursor
        return Qt.ArrowCursor

    def _update_cursor(self, edges: int) -> None:
        if edges == self._cursor_edges:
            return
        self._cursor_edges = edges
        self.setCursor(QCursor(self._cursor_for_edges(edges)))

    # ----- geometry helpers -----
    def _keep_within_parent(self) -> None:
        parent = self.parentWidget()
        if not parent:
            return
        max_x = max(0, parent.width() - self.width())
        max_y = max(0, parent.height() - self.height())
        new_x = min(max(self.x(), 0), max_x)
        new_y = min(max(self.y(), 0), max_y)
        if new_x != self.x() or new_y != self.y():
            self.move(new_x, new_y)

    def ensure_within_parent(self) -> None:
        self._keep_within_parent()

    def _emit_geometry(self) -> None:
        self.geometry_changed.emit(self.geometry())

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            e.ignore()
            return
        edges = self._hit_edges(e.position().toPoint())
        self._drag_active = True
        self._resize_edges = edges
        self._mode = "resize" if edges else "move"
        self._press_pos = e.position().toPoint()
        self._start_geom = self.geometry()
        e.accept()

    def mouseMoveEvent(self, e):
        if not self._drag_active:
            self._update_cursor(self._hit_edges(e.position().toPoint()))
            e.ignore()
            return
        if self._mode == "move":
            self._move_proxy(e)
        else:
            self._resize_proxy(e)

    def mouseReleaseEvent(self, e):
        if not self._drag_active:
            e.ignore()
            return
        self._drag_active = False
        self._mode = None
        self._resize_edges = 0
        self._update_cursor(self._hit_edges(e.position().toPoint()))
        self._emit_geometry()
        e.accept()

    def leaveEvent(self, _e):
        if not self._drag_active:
            self._update_cursor(0)

    # ----- internal actions -----
    def _move_proxy(self, e) -> None:
        parent = self.parentWidget()
        if not parent:
            e.ignore()
            return
        delta = e.position().toPoint() - self._press_pos
        new_pos = self._start_geom.topLeft() + delta
        nx = max(0, min(new_pos.x(), parent.width() - self.width()))
        ny = max(0, min(new_pos.y(), parent.height() - self.height()))
        self.move(nx, ny)
        e.accept()

    def _resize_proxy(self, e) -> None:
        parent = self.parentWidget()
        delta = e.position().toPoint() - self._press_pos
        geom = QRect(self._start_geom)
        x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()
        min_w = self._effective_min_width()
        min_h = self._effective_min_height()

        if self._resize_edges & self._LEFT:
            new_x = x + delta.x()
            max_x = x + w - min_w
            new_x = max(0, min(new_x, max_x))
            w = w + (x - new_x)
            x = new_x
        elif self._resize_edges & self._RIGHT:
            new_w = w + delta.x()
            max_w = parent.width() - x if parent else new_w
            w = max(min_w, min(new_w, max_w))

        if self._resize_edges & self._TOP:
            new_y = y + delta.y()
            max_y = y + h - min_h
            new_y = max(0, min(new_y, max_y))
            h = h + (y - new_y)
            y = new_y
        elif self._resize_edges & self._BOTTOM:
            new_h = h + delta.y()
            max_h = parent.height() - y if parent else new_h
            h = max(min_h, min(new_h, max_h))

        if parent:
            w = min(w, max(1, parent.width() - x))
            h = min(h, max(1, parent.height() - y))

        if w < min_w:
            w = min_w
        if h < min_h:
            h = min_h

        self.setGeometry(QRect(x, y, w, h))
        self._keep_within_parent()
        e.accept()

class TerminalDesktop(QFrame):
    def __init__(self, theme: Theme, chat_card: ChatCard, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = theme
        self.setObjectName("TerminalDesktop")
        self.setAutoFillBackground(False)
        self.setContentsMargins(0, 0, 0, 0)

        ensure_dir(terminal_desktop_dir())
        self.canvas = TerminalDesktopCanvas(theme, self)
        self.camera = CameraView(self.canvas, self)

        self._codex_settings = load_codex_settings()
        self.canvas.set_background_config(self.background_config())
        self.proxy = DraggableProxy(chat_card, self.canvas)
        base_height = max(540, chat_card.sizeHint().height())
        self.proxy.resize(980, base_height)
        self.proxy.set_content_min_size(980, base_height)
        self.proxy.geometry_changed.connect(self._on_proxy_geometry_changed)
        self.proxy.move(max(0, self.canvas.width() // 2 - self.proxy.width() // 2),
                        max(0, self.canvas.height() // 2 - self.proxy.height() // 2))
        QTimer.singleShot(0, self._apply_saved_geometry)

        live_row = QHBoxLayout(); live_row.setContentsMargins(0,0,6,6); live_row.addStretch(1)
        self.live = LivePill(theme, self); self.live.setFixedWidth(96); live_row.addWidget(self.live, 0, Qt.AlignRight | Qt.AlignBottom)

        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(self.camera, 1)
        overlay = QFrame(self); overlay.setLayout(live_row); overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        root.addWidget(overlay, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.proxy.ensure_within_parent()

    def _apply_saved_geometry(self) -> None:
        geom = self._codex_settings.get("terminal_desktop", {})
        if not isinstance(geom, dict):
            geom = {}
        min_size = self.proxy.minimum_size()
        width = int(geom.get("width", self.proxy.width()))
        height = int(geom.get("height", self.proxy.height()))
        width = max(min_size.width(), width)
        height = max(min_size.height(), height)

        canvas_w = self.canvas.width()
        canvas_h = self.canvas.height()
        if canvas_w == 0 or canvas_h == 0:
            QTimer.singleShot(0, self._apply_saved_geometry)
            return
        width = min(width, canvas_w)
        height = min(height, canvas_h)

        x = geom.get("x", -1)
        y = geom.get("y", -1)
        max_x = max(0, canvas_w - width)
        max_y = max(0, canvas_h - height)
        default_x = max(0, (canvas_w - width) // 2)
        default_y = max(0, (canvas_h - height) // 2)
        if not isinstance(x, int) or x < 0 or x > max_x:
            x = default_x
        if not isinstance(y, int) or y < 0 or y > max_y:
            y = default_y

        self.proxy.setGeometry(QRect(x, y, width, height))
        self.proxy.ensure_within_parent()
        self._persist_proxy_geometry()

    def _on_proxy_geometry_changed(self, rect: QRect) -> None:
        self._persist_proxy_geometry(rect)

    def _persist_proxy_geometry(self, rect: Optional[QRect] = None) -> None:
        current = rect or self.proxy.geometry()
        settings = load_codex_settings()
        node = settings.get("terminal_desktop")
        if not isinstance(node, dict):
            node = {}
        node.update({
            "width": current.width(),
            "height": current.height(),
            "x": current.x(),
            "y": current.y(),
        })
        settings["terminal_desktop"] = node
        save_codex_settings(settings)
        self._codex_settings = settings

    # ------------------------------------------------------------------
    def _terminal_state(self) -> Dict[str, Any]:
        node = self._codex_settings.get("terminal_desktop")
        if not isinstance(node, dict):
            node = {}
            self._codex_settings["terminal_desktop"] = node
        node.setdefault("icon_size", "medium")
        node.setdefault("sort_mode", "name")
        node.setdefault("icon_positions", {})
        node.setdefault("background", BackgroundConfig().to_state())
        return node

    def _update_terminal_state(self, mutator) -> None:
        settings = load_codex_settings()
        node = settings.get("terminal_desktop")
        if not isinstance(node, dict):
            node = {}
        node.setdefault("icon_size", "medium")
        node.setdefault("sort_mode", "name")
        node.setdefault("icon_positions", {})
        node.setdefault("background", BackgroundConfig().to_state())
        mutator(node)
        settings["terminal_desktop"] = node
        save_codex_settings(settings)
        self._codex_settings = settings

    def icon_size(self) -> str:
        mode = str(self._terminal_state().get("icon_size", "medium"))
        return mode if mode in {"small", "medium", "large"} else "medium"

    def set_icon_size(self, mode: str) -> None:
        if mode not in {"small", "medium", "large"}:
            mode = "medium"

        def mutate(node: Dict[str, Any]) -> None:
            node["icon_size"] = mode

        self._update_terminal_state(mutate)

    def sort_mode(self) -> str:
        mode = str(self._terminal_state().get("sort_mode", "name"))
        return mode if mode in {"name", "type", "date"} else "name"

    def set_sort_mode(self, mode: str) -> None:
        if mode not in {"name", "type", "date"}:
            mode = "name"

        def mutate(node: Dict[str, Any]) -> None:
            node["sort_mode"] = mode

        self._update_terminal_state(mutate)

    def save_icon_position(self, path: str, pos: QPoint) -> None:

        def mutate(node: Dict[str, Any]) -> None:
            positions = node.setdefault("icon_positions", {})
            positions[path] = [int(pos.x()), int(pos.y())]

        self._update_terminal_state(mutate)

    def restore_icon_position(self, path: str) -> Optional[QPoint]:
        positions = self._terminal_state().get("icon_positions", {})
        coords = positions.get(path)
        if not isinstance(coords, (list, tuple)) or len(coords) != 2:
            return None
        try:
            return QPoint(int(coords[0]), int(coords[1]))
        except Exception:
            return None

    def forget_icon_position(self, path: str) -> None:

        def mutate(node: Dict[str, Any]) -> None:
            positions = node.setdefault("icon_positions", {})
            positions.pop(path, None)

        self._update_terminal_state(mutate)

    def background_config(self) -> BackgroundConfig:
        state = self._terminal_state()
        return BackgroundConfig.from_state(state.get("background"))

    def set_background_config(self, config: BackgroundConfig) -> None:
        normalized = BackgroundConfig.from_state(config.to_state())
        self.canvas.set_background_config(normalized)

        def mutate(node: Dict[str, Any]) -> None:
            node["background"] = normalized.to_state()

        self._update_terminal_state(mutate)

# --------------------------------------------------------------------------------------
# Main window
# --------------------------------------------------------------------------------------

def _default_settings() -> Dict[str, Any]:
    root = transit_dir()
    data_root = agent_data_dir()
    return {
        "chat_model": DEFAULT_CHAT_MODEL,
        "vision_ocr_model": DEFAULT_VISION_OCR_MODEL,
        "vision_model": DEFAULT_VISION_MODEL,
        "embed_model": DEFAULT_EMBED_MODEL,
        "context_pairs": 25,
        "workspace": root,
        "data_root": data_root,
        "enable_semantic": True,
        "enable_vision": True,
        "enable_interpreter": False,
        "reference_embed_contents": DEFAULT_SETTINGS.get("reference_embed_contents", True),
        "reference_case_sensitive": DEFAULT_SETTINGS.get("reference_case_sensitive", False),
        "reference_token_guard": DEFAULT_SETTINGS.get("reference_token_guard", True),
        "reference_token_headroom": DEFAULT_SETTINGS.get("reference_token_headroom", 80),
        "scan_roots": [],
        "shells": {
            "cmd": True,
            "powershell": False,
            "bash": False,
            "zsh": False,
            "wsl": False,
        },
    }


class MainWindow(QMainWindow):
    def __init__(self, theme: Theme, parent: Optional[QWidget] = None, *, embedded: bool = False):
        super().__init__(parent)
        self.theme = theme
        self._embedded = embedded
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 800)
        self.setContentsMargins(0, 0, 0, 0)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#0a1430"))
        pal.setColor(QPalette.Base, QColor("#0a1430"))
        pal.setColor(QPalette.Text, QColor("#e6f0ff"))
        pal.setColor(QPalette.WindowText, QColor("#e6f0ff"))
        self.setPalette(pal)

        self.ollama = OllamaClient()
        self.lex_mgr = LexiconManager(lexicons_dir())

        self.settings = _default_settings()
        saved_codex = load_codex_settings()
        if isinstance(saved_codex, dict):
            self.settings["enable_interpreter"] = bool(
                saved_codex.get("enable_interpreter", saved_codex.get("codex_auto_continue", False))
            )
            self.settings["reference_embed_contents"] = bool(
                saved_codex.get(
                    "reference_embed_contents",
                    DEFAULT_SETTINGS.get("reference_embed_contents", True),
                )
            )
            self.settings["reference_case_sensitive"] = bool(
                saved_codex.get(
                    "reference_case_sensitive",
                    DEFAULT_SETTINGS.get("reference_case_sensitive", False),
                )
            )
            self.settings["reference_token_guard"] = bool(
                saved_codex.get(
                    "reference_token_guard",
                    DEFAULT_SETTINGS.get("reference_token_guard", True),
                )
            )
            self.settings["reference_token_headroom"] = int(
                saved_codex.get(
                    "reference_token_headroom",
                    DEFAULT_SETTINGS.get("reference_token_headroom", 80),
                )
            )
            self.settings["scan_roots"] = _normalize_scan_roots(saved_codex.get("scan_roots", []))
            sandbox_cfg = saved_codex.get("sandbox")
            if isinstance(sandbox_cfg, dict):
                self.settings["sandbox"] = copy.deepcopy(sandbox_cfg)
            else:
                self.settings["sandbox"] = copy.deepcopy(DEFAULT_SETTINGS.get("sandbox", {}))
        else:
            self.settings["sandbox"] = copy.deepcopy(DEFAULT_SETTINGS.get("sandbox", {}))
            self.settings["scan_roots"] = []

        # Error console setup
        self.error_console = ErrorConsole(parent=self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.error_console)
        self.error_console.hide()
        self._orig_stderr = None
        self._orig_excepthook = None
        if not self._embedded:
            ensure_dir(terminal_desktop_dir())
            self._orig_stderr = sys.stderr
            sys.stderr = StderrRedirector(self.error_console, sys.stderr)
            self._orig_excepthook = sys.excepthook
            sys.excepthook = self._handle_exception

        self.desktop: Optional[TerminalDesktop] = None
        self.chat = ChatCard(self.theme, self.ollama, self.settings, self.lex_mgr, self)
        if self._embedded:
            self.setCentralWidget(self.chat)
        else:
            self.desktop = TerminalDesktop(theme, self.chat, self)
            self.setCentralWidget(self.desktop)
        safety_manager.set_confirmer(self._confirm_risky_command)

        self._init_menu()
        self._init_shortcuts()
        self._check_ollama()

    def _init_menu(self):
        bar = self.menuBar()

        file_menu = bar.addMenu("&File")
        open_styles = QAction("Load Styles JSON…", self)
        open_styles.triggered.connect(self._load_styles_json)
        file_menu.addAction(open_styles)
        file_menu.addSeparator()
        quit_act = QAction("Quit", self)
        quit_act.setShortcut(QKeySequence.Quit)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        tools_menu = bar.addMenu("&Settings")
        settings_act = QAction("Preferences…", self)
        settings_act.triggered.connect(self._open_settings)
        tools_menu.addAction(settings_act)

        view_menu = bar.addMenu("&View")
        self.fullscreen_act = QAction("Toggle Fullscreen (Alt+Enter)", self)
        self.fullscreen_act.setShortcut("Alt+Return")
        self.fullscreen_act.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(self.fullscreen_act)

    def _init_shortcuts(self):
        focus_input = QAction(self); focus_input.setShortcut(QKeySequence("Ctrl+`"))
        focus_input.triggered.connect(lambda: self.chat.input.setFocus(Qt.ShortcutFocusReason)); self.addAction(focus_input)

        send_codex = QAction(self); send_codex.setShortcut(QKeySequence("Ctrl+Return"))
        send_codex.triggered.connect(self.chat._send_to_codex); self.addAction(send_codex)

        send_local = QAction(self); send_local.setShortcut(QKeySequence("Alt+Return"))
        send_local.triggered.connect(self.chat._on_send_local); self.addAction(send_local)

    def _check_ollama(self):
        ok, msg = self.ollama.health()
        if not ok:
            QMessageBox.warning(self, "Ollama", f"Ollama Not found: {msg}")

    def _confirm_risky_command(self, prompt: str, command: Sequence[str]) -> bool:
        if QApplication.instance() is None:
            return False
        joined = shlex.join(command)
        message = (
            f"{prompt}\n\n"
            f"Command:\n{joined}\n\nProceed with execution?"
        )
        result = QMessageBox.warning(
            self,
            "Safety Confirmation",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return result == QMessageBox.Yes

    # ------------------------------------------------------------------
    def _handle_exception(self, exc_type, exc, tb) -> None:
        """Log uncaught exceptions without terminating the app."""
        log_exception(self.error_console, exc_type, exc, tb)

    @Slot()
    def _toggle_fullscreen(self):
        if self.isFullScreen(): self.showNormal()
        else: self.showFullScreen()

    @Slot()
    def _load_styles_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Styles JSON", str(styles_path().parent), "JSON Files (*.json)")
        if not path: return
        new_theme = Theme.load(path)
        self.theme = new_theme
        old_chat = getattr(self, "chat", None)
        self.setCentralWidget(None)
        if hasattr(old_chat, "detach_safety_notifier"):
            old_chat.detach_safety_notifier()
        self.chat = ChatCard(self.theme, self.ollama, self.settings, self.lex_mgr, self)
        if self._embedded:
            self.desktop = None
            self.setCentralWidget(self.chat)
        else:
            self.desktop = TerminalDesktop(self.theme, self.chat, self)
            self.setCentralWidget(self.desktop)

    @Slot()
    def _open_settings(self):
        dlg = SettingsDialog(self.theme, self, self.ollama, self.lex_mgr)
        dlg.context_pairs.setValue(int(self.settings.get("context_pairs", 25)))
        dlg.share_context.setChecked(self.settings.get("share_context", True))
        dlg.share_limit.setValue(int(self.settings.get("share_limit", 5)))
        dlg.enable_embeddings.setChecked(self.settings.get("enable_semantic", True))
        dlg.enable_vision.setChecked(self.settings.get("enable_vision", True))
        current_data_root = _clamp_to_agent_subdir(self.settings.get("data_root"), subdir=agent_data_dir())
        dlg.data_root_edit.setText(str(current_data_root))
        shells = self.settings.get("shells", {})
        dlg.chk_cmd.setChecked(shells.get("cmd", True))
        dlg.chk_powershell.setChecked(shells.get("powershell", False))
        dlg.chk_bash.setChecked(shells.get("bash", False))
        dlg.chk_zsh.setChecked(shells.get("zsh", False))
        dlg.chk_wsl.setChecked(shells.get("wsl", False))
        s = load_codex_settings()
        dlg.codex_mode_bridge.setChecked(s.get("default_launch_mode","bridge") == "bridge")
        dlg.codex_working.setText(s.get("working_folder", str(workspace_root())))
        dlg.enable_interpreter.setChecked(
            bool(self.settings.get("enable_interpreter", s.get("enable_interpreter", False)))
        )
        dlg.reference_embed_contents.setChecked(
            bool(
                self.settings.get(
                    "reference_embed_contents",
                    s.get(
                        "reference_embed_contents",
                        DEFAULT_SETTINGS.get("reference_embed_contents", True),
                    ),
                )
            )
        )
        dlg.reference_case_sensitive.setChecked(
            bool(
                self.settings.get(
                    "reference_case_sensitive",
                    s.get(
                        "reference_case_sensitive",
                        DEFAULT_SETTINGS.get("reference_case_sensitive", False),
                    ),
                )
            )
        )
        dlg.reference_token_guard.setChecked(
            bool(
                self.settings.get(
                    "reference_token_guard",
                    s.get(
                        "reference_token_guard",
                        DEFAULT_SETTINGS.get("reference_token_guard", True),
                    ),
                )
            )
        )
        dlg.reference_token_headroom.setValue(
            int(
                self.settings.get(
                    "reference_token_headroom",
                    s.get(
                        "reference_token_headroom",
                        DEFAULT_SETTINGS.get("reference_token_headroom", 80),
                    ),
                )
            )
        )
        dlg.set_scan_roots(s.get("scan_roots", []))
        dlg.apply_sandbox_settings(s.get("sandbox", {}))

        if dlg.exec() == QDialog.Accepted:
            vals = dlg.values()
            self.settings.update({
                "chat_model": vals["chat_model"],
                "vision_ocr_model": vals["vision_ocr_model"],
                "vision_model": vals["vision_model"],
                "embed_model": vals["embed_model"],
                "context_pairs": vals["context_pairs"],
                "share_context": vals["share_context"],
                "share_limit": vals["share_limit"],
                "enable_semantic": vals["enable_semantic"],
                "enable_vision": vals["enable_vision"],
                "enable_interpreter": vals["enable_interpreter"],
                "reference_embed_contents": vals["reference_embed_contents"],
                "reference_case_sensitive": vals["reference_case_sensitive"],
                "reference_token_guard": vals["reference_token_guard"],
                "reference_token_headroom": vals["reference_token_headroom"],
                "data_root": vals["data_root"],
                "scan_roots": vals["scan_roots"],
                "shells": vals["shells"],
            })
            self.settings["sandbox"] = vals["codex"]["sandbox"]
            self.settings["scan_roots"] = vals["codex"]["scan_roots"]
            codex_settings = load_codex_settings()
            codex_settings.update({
                "default_launch_mode": vals["codex"]["default_launch_mode"],
                "working_folder": vals["codex"]["working_folder"],
                "model": self.settings["chat_model"],
                "sandbox": vals["codex"]["sandbox"],
                "enable_interpreter": vals["enable_interpreter"],
                "reference_embed_contents": vals["reference_embed_contents"],
                "reference_case_sensitive": vals["reference_case_sensitive"],
                "reference_token_guard": vals["reference_token_guard"],
                "reference_token_headroom": vals["reference_token_headroom"],
                "scan_roots": vals["codex"]["scan_roots"],
            })
            save_codex_settings(codex_settings)
            old_chat = self.chat
            self.setCentralWidget(None)
            if hasattr(old_chat, "detach_safety_notifier"):
                old_chat.detach_safety_notifier()
            self.chat = ChatCard(self.theme, self.ollama, self.settings, self.lex_mgr, self)
            if self._embedded:
                self.desktop = None
                self.setCentralWidget(self.chat)
            else:
                self.desktop = TerminalDesktop(self.theme, self.chat, self)
                self.setCentralWidget(self.desktop)

    def closeEvent(self, event: QCloseEvent) -> None:
        if hasattr(self, "chat") and hasattr(self.chat, "detach_safety_notifier"):
            self.chat.detach_safety_notifier()
        if self._orig_stderr is not None:
            sys.stderr = self._orig_stderr
            self._orig_stderr = None
        if self._orig_excepthook is not None:
            sys.excepthook = self._orig_excepthook
            self._orig_excepthook = None
        super().closeEvent(event)

# --------------------------------------------------------------------------------------
# Embeddable factory
# --------------------------------------------------------------------------------------

def build_widget(parent: Optional[QWidget] = None, embedded: bool = False) -> Tuple[QWidget, str]:
    """Create the Codex Terminal widget for embedding or standalone usage."""
    theme_json = locate_styles_json()
    theme = Theme.load(theme_json) if theme_json else Theme()
    window = MainWindow(theme, parent=parent, embedded=embedded)
    return window, APP_NAME


# --------------------------------------------------------------------------------------
# Entry
# --------------------------------------------------------------------------------------

def locate_styles_json() -> str:
    p = styles_path()
    return str(p) if p.is_file() else ""

def main():
    shared_logger = configure_shared_logger()
    install_global_exception_handler(shared_logger)
    shared_logger.info("Codex Terminal starting up (pid=%s)", os.getpid())
    for handler in shared_logger.handlers:
        try:
            handler.flush()
        except Exception:
            continue

    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument(
        "--workspace",
        metavar="PATH",
        help="Path to use for CODEX_WORKSPACE before launching the UI.",
    )
    args, qt_args = parser.parse_known_args()
    if args.workspace:
        candidate = os.path.abspath(os.path.expanduser(args.workspace))
        os.environ["CODEX_WORKSPACE"] = candidate
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

    sys.argv = [sys.argv[0]] + qt_args
    # Apply the shared DPI rounding guard immediately before constructing
    # QApplication so we never touch Qt after an instance already exists.
    _ensure_high_dpi_rounding_policy()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    widget, _ = build_widget()
    widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
