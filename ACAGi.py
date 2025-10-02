#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACAGi — unified single-file integration for the autonomous desktop stack.

This module is the authoritative integration point: the virtual desktop, chat,
memory, bridge, and safety subsystems previously maintained as separate scripts
are now embedded here unless a component is explicitly documented elsewhere.
Requirements: PySide6>=6.6, requests, Pillow (optional), local ollama, and
Windows 10+ for the bridge runtime.
"""

from __future__ import annotations

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt

import argparse
import ast
import atexit
import base64
import builtins
import copy
import ctypes
import configparser
import difflib
import hashlib
import importlib
import importlib.util
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
import tempfile
import threading
import time
import traceback
import uuid
import warnings
import zipfile
from collections import Counter, defaultdict, deque
from functools import lru_cache
from dataclasses import dataclass, field
from enum import Enum
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from types import ModuleType, TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Deque,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
)

# Optional dependencies are resolved via runtime checks instead of guarded imports
_REQUESTS_MODULE_NAME = "requests"
_PILLOW_MODULE_NAME = "PIL.Image"

if importlib.util.find_spec(_REQUESTS_MODULE_NAME):
    import requests  # type: ignore  # noqa: F401
else:
    requests = None  # type: ignore[assignment]

if importlib.util.find_spec(_PILLOW_MODULE_NAME):
    from PIL import Image  # type: ignore  # noqa: F401
else:
    Image = None  # type: ignore[assignment]

from PySide6.QtCore import (
    QRect,
    QRectF,
    QTimer,
    Signal,
    Slot,
    QSize,
    QEvent,
    QObject,
    QMimeData,
    QPoint,
    QUrl,
    QThread,
    QFileSystemWatcher,
)
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QColor,
    QCursor,
    QDesktopServices,
    QFont,
    QKeyEvent,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPalette,
    QBrush,
    QIcon,
    QImage,
    QPixmap,
    QTextCharFormat,
    QTextCursor,
    QMovie,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QComboBox,
    QSlider,
    QFormLayout,
    QGroupBox,
    QTabWidget,
    QScrollArea,
    QToolButton,
    QCheckBox,
    QSpinBox,
    QSpacerItem,
    QSizePolicy,
    QInputDialog,
    QMenu,
    QStyle,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QStatusBar,
)




# ============================================================================
# Dev Logic Roots
# ============================================================================

DEV_LOGIC_ROOT = Path(__file__).resolve().parent / "Dev_Logic"


# ============================================================================
# Token Budget Utilities (Inlined from Dev_Logic/token_budget.py)
# ============================================================================

_TIKTOKEN_MODULE_NAME = "tiktoken"

if importlib.util.find_spec(_TIKTOKEN_MODULE_NAME):
    import tiktoken  # type: ignore  # noqa: F401
else:
    tiktoken = None  # type: ignore[assignment]

_MODEL_TOKEN_LIMITS: Dict[str, int] = {
    "qwen3": 32768,
    "qwen2": 32768,
    "qwen": 32768,
    "llama3": 8192,
    "llama-3": 8192,
    "llama2": 4096,
    "llama-2": 4096,
    "mistral": 8192,
    "mixtral": 8192,
    "phi3": 4096,
    "phi-3": 4096,
    "phi2": 4096,
    "codellama": 16384,
    "deepseek": 16384,
    "gpt-4o": 128000,
    "gpt-4": 8192,
    "gpt-3.5": 4096,
}
_DEFAULT_MAX_TOKENS = 8192
_WORD_RE = re.compile(r"\S+")


@lru_cache(maxsize=32)
def _encoding_for_model(model: Optional[str]) -> Any:
    """Return a cached tokenizer for *model* when tiktoken is available."""

    if tiktoken is None:
        return None
    name = (model or "").strip() or "cl100k_base"
    try:
        return tiktoken.encoding_for_model(name)
    except Exception:
        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            return None


def get_model_token_limit(model: Optional[str]) -> int:
    """Return the maximum prompt tokens supported by *model*."""

    if not model:
        return _DEFAULT_MAX_TOKENS
    key = model.lower()
    for pattern, limit in _MODEL_TOKEN_LIMITS.items():
        if pattern in key:
            return limit
    return _DEFAULT_MAX_TOKENS


def prompt_token_budget(model: Optional[str], headroom_pct: int) -> int:
    """Compute the usable prompt budget given a headroom percentage."""

    limit = get_model_token_limit(model)
    pct = max(1, min(int(headroom_pct or 0), 100))
    return int(limit * (pct / 100.0))


def count_tokens(text: str, model: Optional[str] = None) -> int:
    """Count tokens for *text* using an optional tokenizer fallback."""

    if not text:
        return 0
    encoding = _encoding_for_model(model)
    if encoding is not None:
        try:
            return len(encoding.encode(text))
        except Exception:
            pass
    tokens = _WORD_RE.findall(text)
    if tokens:
        return len(tokens)
    return max(1, math.ceil(len(text) / 4))

# ============================================================================
# Safety Guardrails (Inlined from Dev_Logic/safety.py)
# ============================================================================


class SafetyViolation(RuntimeError):
    """Raised when a safety rule blocks an operation."""


class SafetyManager:
    """Coordinates safety guardrails for file writes and shell commands."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._protected_files: set[Path] = set()
        self._protected_dirs: set[Path] = set()
        self._notifiers: Dict[str, Callable[[str], None]] = {}
        self._confirmer: Optional[Callable[[str, Sequence[str]], bool]] = None
        self._original_open = builtins.open
        self._installed = False
        self._risk_patterns = (
            re.compile(r"\brm\b.*\b--no-preserve-root\b"),
            re.compile(r"\brm\b.*\b-\w*[rf]\w*\b.*\s/"),
            re.compile(r"\bsudo\s+rm\b"),
            re.compile(r"\bmkfs(\.\w+)?\b"),
            re.compile(r"\bformat\s+[A-Za-z]:"),
            re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*;\s*\}\s*;\s*:"),
        )
        self._operation_policies: Dict[str, "OperationPolicy"] = {}
        self._runtime_settings: Optional["RuntimeSettings"] = None

    def install_file_guard(self) -> None:
        """Monkey patch :func:`open` so destructive writes are intercepted."""

        with self._lock:
            if self._installed:
                return

            def _guarded_open(file, mode="r", *args, **kwargs):  # type: ignore[override]
                path = self._coerce_path(file)
                if path is not None and self._is_write_mode(mode):
                    self._enforce_protected(path, mode)
                return self._original_open(file, mode, *args, **kwargs)

            builtins.open = _guarded_open  # type: ignore[assignment]
            self._installed = True

    def add_protected_path(self, path: os.PathLike[str] | str) -> None:
        resolved = self._normalise(path)
        with self._lock:
            self._protected_files.add(resolved)

    def add_protected_directory(self, path: os.PathLike[str] | str) -> None:
        resolved = self._normalise(path)
        with self._lock:
            self._protected_dirs.add(resolved)

    def remove_protected_path(self, path: os.PathLike[str] | str) -> None:
        resolved = self._normalise(path)
        with self._lock:
            self._protected_files.discard(resolved)

    def remove_protected_directory(self, path: os.PathLike[str] | str) -> None:
        resolved = self._normalise(path)
        with self._lock:
            self._protected_dirs.discard(resolved)

    def clear_protected(self) -> None:
        with self._lock:
            self._protected_files.clear()
            self._protected_dirs.clear()

    def add_notifier(self, callback: Callable[[str], None]) -> str:
        token = uuid.uuid4().hex
        with self._lock:
            self._notifiers[token] = callback
        return token

    def remove_notifier(self, token: str) -> None:
        with self._lock:
            self._notifiers.pop(token, None)

    def clear_notifiers(self) -> None:
        with self._lock:
            self._notifiers.clear()

    def set_confirmer(
        self, callback: Optional[Callable[[str, Sequence[str]], bool]]
    ) -> None:
        with self._lock:
            self._confirmer = callback

    def set_operation_policies(
        self, policies: Mapping[str, "OperationPolicy"]
    ) -> None:
        with self._lock:
            self._operation_policies = {
                key.lower(): value for key, value in policies.items()
            }

    def set_runtime_settings(self, settings: "RuntimeSettings") -> None:
        with self._lock:
            self._runtime_settings = settings

    def ensure_command_allowed(
        self, cmd: Sequence[str], *, operation: Optional[str] = None
    ) -> None:
        if not cmd:
            return

        canonical = [str(part) for part in cmd]
        joined = shlex.join(canonical)
        lowered = joined.lower()

        if operation:
            self._enforce_operation_policy(operation, canonical)

        reason = self._match_risky(lowered, canonical)
        if not reason:
            return

        prompt = (
            f"[SAFETY] Confirmation required: {joined}"
            if reason == "confirm"
            else f"[SAFETY] {reason}: {joined}"
        )
        self._dispatch(prompt)

        allow = False
        callback = self._confirmer
        if callback is not None:
            try:
                allow = bool(callback(prompt, tuple(canonical)))
            except Exception as exc:  # pragma: no cover - defensive
                self._dispatch(f"[SAFETY] Confirmation handler failed: {exc}")
                allow = False

        if allow:
            self._dispatch(f"[SAFETY] Approved: {joined}")
            return

        message = f"[SAFETY] Blocked command: {joined}"
        self._dispatch(message)
        raise SafetyViolation(message)

    def _enforce_operation_policy(
        self, operation: str, canonical: Sequence[str]
    ) -> None:
        with self._lock:
            policy = self._operation_policies.get(operation.lower())
            runtime = self._runtime_settings

        if policy is None:
            return

        command_name = Path(canonical[0]).name.lower()
        if command_name in policy.deny_commands:
            message = (
                f"[POLICY] {operation} denylist violation: {shlex.join(canonical)}"
            )
            self._dispatch(message)
            raise SafetyViolation(message)

        reasons: List[str] = []
        if policy.allow_commands and command_name not in policy.allow_commands:
            reasons.append("command not allowlisted")

        if command_name in policy.approval_commands:
            reasons.append("command requires manual approval")

        if policy.sandbox_modes:
            current_mode = (runtime.sandbox if runtime else "trusted").lower()
            if current_mode not in policy.sandbox_modes:
                allowed = ", ".join(sorted(policy.sandbox_modes))
                reasons.append(
                    f"sandbox must be one of [{allowed}] (current={current_mode})"
                )

        if reasons:
            reason_text = "; ".join(reasons)
            self._request_policy_approval(operation, canonical, reason_text)

    def _request_policy_approval(
        self, operation: str, canonical: Sequence[str], reason: str
    ) -> None:
        joined = shlex.join(canonical)
        prompt = f"[POLICY] {operation}: {reason}: {joined}"
        self._dispatch(prompt)

        allow = False
        callback = self._confirmer
        if callback is not None:
            try:
                allow = bool(callback(prompt, tuple(canonical)))
            except Exception as exc:  # pragma: no cover - defensive
                self._dispatch(f"[POLICY] Approval handler failed: {exc}")
                allow = False

        if allow:
            self._dispatch(f"[POLICY] Approved: {joined}")
            return

        message = f"[POLICY] Blocked command: {joined}"
        self._dispatch(message)
        raise SafetyViolation(message)

    def _match_risky(self, lowered: str, tokens: Sequence[str]) -> Optional[str]:
        for pattern in self._risk_patterns:
            if pattern.search(lowered):
                return "confirm"

        if not tokens:
            return None

        lowered_tokens = [tok.lower() for tok in tokens]
        if "rm" in lowered_tokens or any(tok.endswith("rm") for tok in lowered_tokens):
            if self._has_flag(lowered_tokens, "r") and self._has_flag(lowered_tokens, "f"):
                if any(tok == "/" or tok.startswith("/") for tok in lowered_tokens):
                    return "confirm"
        return None

    @staticmethod
    def _has_flag(tokens: Sequence[str], flag: str) -> bool:
        return any(token.startswith("-") and flag in token for token in tokens)

    def _dispatch(self, message: str) -> None:
        with self._lock:
            callbacks = list(self._notifiers.values())
        for cb in callbacks:
            try:
                cb(message)
            except Exception:  # pragma: no cover - defensive
                continue

    def _enforce_protected(self, path: Path, mode: str) -> None:
        if not self._is_protected(path):
            return

        if "a" in mode and "w" not in mode:
            return

        message = f"[SAFETY] Blocked write to protected path: {path}"
        self._dispatch(message)
        raise SafetyViolation(message)

    def _is_protected(self, path: Path) -> bool:
        with self._lock:
            files = set(self._protected_files)
            dirs = set(self._protected_dirs)
        if path in files:
            return True
        for root in dirs:
            try:
                if path == root or path.is_relative_to(root):  # type: ignore[attr-defined]
                    return True
            except AttributeError:
                try:
                    path.resolve()
                    root.resolve()
                except Exception:
                    continue
                if str(path).startswith(str(root)):
                    return True
        return False

    @staticmethod
    def _is_write_mode(mode: str) -> bool:
        return any(token in mode for token in ("w", "a", "+", "x"))

    @staticmethod
    def _coerce_path(file: object) -> Optional[Path]:
        if isinstance(file, (str, bytes, os.PathLike)):
            return Path(file)
        return None

    @staticmethod
    def _normalise(path: os.PathLike[str] | str) -> Path:
        return Path(path).expanduser().resolve(strict=False)


safety_manager = SafetyManager()
safety_manager.install_file_guard()
safety_manager.add_protected_path(Path("AGENT.md"))
safety_manager.add_protected_directory(Path("errors"))


# ============================================================================
# Prompt Loader (Inlined from Dev_Logic/prompt_loader.py)
# ============================================================================


PROMPTS_DIR = DEV_LOGIC_ROOT / "prompts"


@dataclass(frozen=True)
class PromptDefinition:
    """Static metadata describing a prompt bundle."""

    slug: str
    title: str
    description: str
    default: str = ""

    @property
    def base_path(self) -> Path:
        return PROMPTS_DIR / f"{self.slug}.txt"

    @property
    def overlay_path(self) -> Path:
        return PROMPTS_DIR / f"{self.slug}.overlay.txt"


class PromptWatcher:
    """Caches prompt text and refreshes when the underlying files change."""

    def __init__(self, definition: PromptDefinition):
        self._definition = definition
        self._lock = RLock()
        self._cached_text: str = ""
        self._mtimes: tuple[Optional[float], Optional[float]] = (None, None)
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        self._load(initial=True)

    @property
    def definition(self) -> PromptDefinition:
        return self._definition

    @property
    def base_path(self) -> Path:
        return self._definition.base_path

    @property
    def overlay_path(self) -> Path:
        return self._definition.overlay_path

    def text(self) -> str:
        """Return the prompt text, reloading if files changed."""

        with self._lock:
            current = (self._stat(self.base_path), self._stat(self.overlay_path))
            if current != self._mtimes:
                self._load()
            return self._cached_text

    def reload(self) -> None:
        """Force a reload regardless of modification times."""

        with self._lock:
            self._load()

    def _load(self, initial: bool = False) -> None:
        base_text = self._read_file(self.base_path)
        if not base_text.strip():
            base_text = self._definition.default
            if initial and self._definition.default and not self.base_path.exists():
                self.base_path.parent.mkdir(parents=True, exist_ok=True)
                self.base_path.write_text(
                    self._definition.default + "\n", encoding="utf-8"
                )
                base_text = self._definition.default
        overlay_text = self._read_file(self.overlay_path)
        combined = base_text.strip()
        overlay_clean = overlay_text.strip()
        if overlay_clean:
            combined = f"{combined}\n\n{overlay_clean}" if combined else overlay_clean
        if not combined.strip():
            combined = self._definition.default
        self._cached_text = combined
        self._mtimes = (self._stat(self.base_path), self._stat(self.overlay_path))

    def _read_file(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""

    def _stat(self, path: Path) -> Optional[float]:
        try:
            return path.stat().st_mtime
        except FileNotFoundError:
            return None


_PROMPT_DEFINITIONS: Dict[str, PromptDefinition] = {
    "codex_system": PromptDefinition(
        slug="codex_system",
        title="Codex System Prompt",
        description="Core persona for the coding operator.",
        default=(
            "You are Codex-Local's coding operator. Work entirely within this local "
            "workspace without network access. Translate user goals into exact shell "
            "commands and code edits, think through each plan before running it, and "
            "narrate critical decisions. The Codex interpreter may automatically prompt "
            "you to continue executing work; resume only when the requested path is "
            "safe and justified. When the requested work is complete, announce "
            "completion and emit `STOP` on its own line so downstream tooling halts "
            "cleanly. Respect safety guardrails, request confirmation for destructive "
            "steps, and prefer deterministic, minimal changes that keep tests green."
        ),
    ),
    "chat_system": PromptDefinition(
        slug="chat_system",
        title="Chat System Prompt",
        description="Conversational analysis and planning persona.",
        default=(
            "You are Codex-Local's planning and explanation companion. Provide "
            "thorough analysis, cite relevant repository context, and propose "
            "actionable next steps. Keep guidance grounded in files that exist locally, "
            "flag assumptions or risks, and delegate execution details to the coding "
            "operator when commands must be run. Anticipate interpreter auto-continue "
            "loops by outlining the next safe action and reminding the operator to "
            "declare completion. When work is finished, ensure the response includes an "
            "explicit completion note plus a standalone `STOP` line."
        ),
    ),
    "codex_shell": PromptDefinition(
        slug="codex_shell",
        title="Codex Shell Prompt",
        description="Translator from natural language intent to shell commands.",
        default=(
            "You convert natural language intent into concrete shell commands for "
            "Codex-Local. Use POSIX-friendly syntax unless the session explicitly "
            "targets another shell. Compose small, deterministic command sequences, "
            "include safety flags, and never guess at paths that do not exist. Expect "
            "interpreter auto-continue prompts; prepare follow-up commands only when "
            "prior output requires them. When no further safe commands remain, state "
            "that execution is complete and output `STOP` on its own line so automation "
            "knows to halt. If a request is ambiguous, return a brief question instead "
            "of a risky command."
        ),
    ),
    "voice_system": PromptDefinition(
        slug="voice_system",
        title="Voice System Prompt",
        description="Speech transcription and routing persona.",
        default=(
            "You run Codex-Local's voice interface. Listen for wake phrases, "
            "transcribe speech accurately, and summarize intent in concise text. "
            "Never execute commands yourself; hand the cleaned request to the "
            "appropriate agent. Preserve privacy by keeping audio-derived data local "
            "and discarding snippets once they are processed.\n\n"
            "Interpreter awareness:\n"
            "- Flag when a spoken request will trigger the coding interpreter so the "
            "user knows auto-continue may occur.\n"
            "- Remind the operator that completion replies must include a clear stop "
            "sentence plus a standalone `STOP` line."
        ),
    ),
}

_PROMPT_CACHE: Dict[str, PromptWatcher] = {}
_PROMPT_CACHE_LOCK = RLock()


def get_prompt_watcher(slug: str) -> PromptWatcher:
    """Return (and cache) the watcher for *slug*."""

    with _PROMPT_CACHE_LOCK:
        watcher = _PROMPT_CACHE.get(slug)
        if watcher is None:
            definition = _PROMPT_DEFINITIONS.get(slug)
            if definition is None:
                raise KeyError(f"Unknown prompt slug: {slug}")
            watcher = PromptWatcher(definition)
            _PROMPT_CACHE[slug] = watcher
        return watcher


def prompt_text(slug: str) -> str:
    """Convenience wrapper returning the combined text for *slug*."""

    return get_prompt_watcher(slug).text()


def iter_prompt_definitions() -> Iterable[PromptDefinition]:
    """Iterate over known prompt definitions in a stable order."""

    for key in sorted(_PROMPT_DEFINITIONS.keys()):
        yield _PROMPT_DEFINITIONS[key]


# ============================================================================
# Image Pipeline (Inlined from Dev_Logic/image_pipeline.py)
# ============================================================================


_PYTESSERACT_MODULE_NAME = "pytesseract"

if importlib.util.find_spec(_PYTESSERACT_MODULE_NAME):
    import pytesseract  # type: ignore  # noqa: F401
else:
    pytesseract = None  # type: ignore[assignment]


class VisionClient(Protocol):
    """Minimal protocol for Ollama-like chat clients."""

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        images: Optional[List[str]] = None,
    ) -> Tuple[bool, str, str]:
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


_MARKDOWN_IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")


def _normalise_markdown(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    cleaned: List[str] = []
    blank = False
    for line in lines:
        stripped = line.strip()
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


def _encode_png_base64(path: Path) -> Optional[str]:
    if Image is None:
        try:
            data = path.read_bytes()
        except Exception:
            return None
        return base64.b64encode(data).decode("ascii")

    try:
        with Image.open(path) as img:
            buffer = io.BytesIO()
            img.convert("RGBA").save(buffer, format="PNG", optimize=True)
            return base64.b64encode(buffer.getvalue()).decode("ascii")
    except Exception:
        try:
            data = path.read_bytes()
        except Exception:
            return None
        return base64.b64encode(data).decode("ascii")


def perform_ocr(
    image_path: Path | str,
    *,
    engine: Optional[Any] = None,
    language: str = "eng",
) -> OCRResult:
    """Run OCR over *image_path* returning Markdown text or an error."""

    path = _ensure_image(Path(image_path))
    if path is None:
        return OCRResult("", "", error="Image not found")

    if Image is None:
        return OCRResult("", "", error="Pillow not installed")

    ocr_engine = engine or pytesseract
    if ocr_engine is None:
        return OCRResult("", "", error="pytesseract not installed")

    try:
        with Image.open(path) as img:
            greyscale = img.convert("L")
            text = ocr_engine.image_to_string(greyscale, lang=language)
    except Exception as exc:
        return OCRResult("", "", error=str(exc))

    text = text.strip()
    if not text:
        return OCRResult("", "", error="No text detected")

    markdown = _normalise_markdown(text)
    return OCRResult(text=text, markdown=markdown)


def analyze_image(
    image_path: Path | str,
    ocr_text: str,
    *,
    client: Optional[VisionClient],
    model: str,
    user_text: str = "",
) -> VisionResult:
    """Ask a vision-language model to describe *image_path*."""

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


# ============================================================================
# Repository Index (Inlined from Dev_Logic/memory_manager.py)
# ============================================================================


DATASETS_ROOT = DEV_LOGIC_ROOT / "datasets"

Vector = List[float]
TextEmbedder = Callable[[str], Sequence[float]]

_FALLBACK_EMBED_DIM = 16
_REPO_DEFAULT_EXCLUDE = {
    ".git",
    "__pycache__",
    "datasets",
    "errors",
    "memory",
    "Archived Conversations",
}
_MAX_INDEX_FILE_SIZE = 256_000
_WINDOW_SIZE = 60
_WINDOW_OVERLAP = 10


def _hash_embedding(data: bytes, dims: int = _FALLBACK_EMBED_DIM) -> Vector:
    if not data:
        return [0.0] * dims

    digest = hashlib.blake2b(data, digest_size=dims * 4).digest()
    ints = [
        int.from_bytes(digest[i : i + 4], "big", signed=False)
        for i in range(0, len(digest), 4)
    ]
    vec = [value / 4294967295.0 for value in ints]
    norm = math.sqrt(sum(component * component for component in vec))
    if norm == 0:
        return vec
    return [component / norm for component in vec]


def _fallback_repo_embedding(text: str) -> Vector:
    tokens = [
        token for token in re.findall(r"[A-Za-z0-9_]+", text.lower()) if token
    ]
    if not tokens:
        return _hash_embedding(text.encode("utf-8"))
    dims = _FALLBACK_EMBED_DIM
    vec = [0.0] * dims
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % dims
        vec[index] += 1.0
    norm = math.sqrt(sum(component * component for component in vec))
    if norm == 0:
        return vec
    return [component / norm for component in vec]


def _ensure_vector(value: Any) -> Vector:
    if isinstance(value, list):
        result: Vector = []
        for item in value:
            try:
                result.append(float(item))
            except (TypeError, ValueError):
                return []
        return result
    return []


def _cosine(a: Vector, b: Vector) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(y * y for y in b))
    if da == 0 or db == 0:
        return 0.0
    return dot / (da * db)


@dataclass(slots=True)
class _RepoSegment:
    path: Path
    start_line: int
    end_line: int
    text: str
    metadata: Dict[str, Any]


@dataclass(slots=True)
class _RepoIndexRecord:
    identifier: str
    path: str
    start_line: int
    end_line: int
    text: str
    embedding: Vector
    metadata: Dict[str, Any]
    timestamp: float

    def score(self, query_vec: Vector) -> float:
        if not self.embedding or not query_vec:
            return 0.0
        return _cosine(query_vec, self.embedding)


def _segment_identifier(path: str, start_line: int, end_line: int) -> str:
    payload = f"{path}:{start_line}:{end_line}".encode("utf-8", "ignore")
    return hashlib.blake2b(payload, digest_size=16).hexdigest()


class RepositoryIndex:
    """Build and query a lightweight repository text index."""

    def __init__(
        self,
        repo_root: Optional[Path | str] = None,
        data_root: Optional[Path | str] = None,
        *,
        text_embedder: Optional[TextEmbedder] = None,
        enable_embeddings: bool = True,
        include_extensions: Optional[Sequence[str]] = None,
        exclude_dirs: Optional[Sequence[str]] = None,
        extra_roots: Optional[Sequence[Path | str]] = None,
    ) -> None:
        base_repo = (
            Path(repo_root)
            if repo_root is not None
            else Path(__file__).resolve().parent
        )
        self.repo_root = base_repo.resolve()
        base_data = (
            Path(data_root)
            if data_root is not None
            else DATASETS_ROOT
        )
        self.data_root = base_data.resolve()
        self.index_dir = self.data_root / "repo_index"
        self.index_path = self.index_dir / "index.jsonl"
        self.manifest_path = self.index_dir / "manifest.json"
        self.enable_embeddings = enable_embeddings
        self._text_embedder = text_embedder or _fallback_repo_embedding
        self._include_extensions = (
            tuple(include_extensions) if include_extensions else None
        )
        self._exclude_dirs = set(exclude_dirs) if exclude_dirs else set(
            _REPO_DEFAULT_EXCLUDE
        )
        extras: List[Path] = []
        seen: Set[Path] = {self.repo_root}
        if extra_roots:
            for entry in extra_roots:
                try:
                    candidate = Path(entry).expanduser().resolve()
                except Exception:
                    continue
                if candidate in seen:
                    continue
                seen.add(candidate)
                extras.append(candidate)
        self._extra_roots: Tuple[Path, ...] = tuple(extras)
        self._roots: Tuple[Path, ...] = (self.repo_root, *self._extra_roots)
        self._records: List[_RepoIndexRecord] = []
        self._loaded = False
        self._lock = RLock()

    def rebuild(self) -> Dict[str, Any]:
        segments: List[Tuple[Path, _RepoSegment]] = []
        files_indexed = 0
        timestamp = time.time()

        for base_root, path in self._iter_repo_files():
            text = self._read_file_text(path)
            if text is None:
                continue
            files_indexed += 1
            for segment in self._segment_file(path, text):
                segments.append((base_root, segment))

        entries = []
        for base_root, segment in segments:
            rel_path = self._relative_path(segment.path, base_root)
            embedding: Vector = []
            if self.enable_embeddings and segment.text.strip():
                embedding = self._embed_text(segment.text)
            record_id = _segment_identifier(
                rel_path, segment.start_line, segment.end_line
            )
            metadata = dict(segment.metadata)
            metadata.setdefault("scan_root", str(base_root))
            entry = {
                "id": record_id,
                "path": rel_path,
                "start_line": segment.start_line,
                "end_line": segment.end_line,
                "text": segment.text,
                "embedding": embedding,
                "metadata": metadata,
                "ts": timestamp,
            }
            entries.append(entry)

        self.index_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = self._write_index(entries)
        tmp_path.replace(self.index_path)

        embed_dim = 0
        if entries and entries[0]["embedding"]:
            embed_dim = len(entries[0]["embedding"])

        manifest = {
            "timestamp": timestamp,
            "segments": len(entries),
            "files_indexed": files_indexed,
            "embedding_dim": embed_dim,
        }
        with self.manifest_path.open("w", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False, indent=2)

        records = [
            _RepoIndexRecord(
                identifier=entry["id"],
                path=str(entry["path"]),
                start_line=int(entry["start_line"]),
                end_line=int(entry["end_line"]),
                text=str(entry["text"]),
                embedding=_ensure_vector(entry.get("embedding")),
                metadata=dict(entry.get("metadata") or {}),
                timestamp=float(entry.get("ts") or timestamp),
            )
            for entry in entries
        ]

        with self._lock:
            self._records = records
            self._loaded = True

        return {
            "files_indexed": files_indexed,
            "segments": len(entries),
            "timestamp": timestamp,
            "index_path": self.index_path,
        }

    def load(self) -> None:
        with self._lock:
            if self._loaded:
                return
            self._load_locked()

    def iter_segments(self) -> Iterable[Dict[str, Any]]:
        self.load()
        with self._lock:
            for record in self._records:
                yield {
                    "id": record.identifier,
                    "path": record.path,
                    "start_line": record.start_line,
                    "end_line": record.end_line,
                    "text": record.text,
                    "metadata": dict(record.metadata),
                    "timestamp": record.timestamp,
                }

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        query_text = query.strip()
        if not query_text or k <= 0 or not self.enable_embeddings:
            return []

        query_vec = self._embed_text(query_text)
        if not query_vec:
            return []

        self.load()

        with self._lock:
            records = list(self._records)

        scored: List[Tuple[float, _RepoIndexRecord]] = []
        for record in records:
            score = record.score(query_vec)
            if score <= 0:
                continue
            scored.append((score, record))

        scored.sort(key=lambda item: item[0], reverse=True)

        results: List[Dict[str, Any]] = []
        for score, record in scored[:k]:
            results.append(
                {
                    "id": record.identifier,
                    "path": record.path,
                    "start_line": record.start_line,
                    "end_line": record.end_line,
                    "text": record.text,
                    "metadata": dict(record.metadata),
                    "score": score,
                    "timestamp": record.timestamp,
                }
            )
        return results

    def _embed_text(self, text: str) -> Vector:
        vec = self._text_embedder(text) if text else []
        return [float(value) for value in vec]

    def _iter_repo_files(self) -> Iterable[Tuple[Path, Path]]:
        for base_root in self._roots:
            if not base_root.exists():
                continue
            try:
                base_resolved = base_root.resolve()
            except Exception:
                base_resolved = base_root
            for root, dirs, files in os.walk(base_root):
                path_root = Path(root)
                try:
                    relative_parts = set(path_root.relative_to(base_resolved).parts)
                except ValueError:
                    relative_parts = set()
                if relative_parts & self._exclude_dirs:
                    dirs[:] = []
                    continue
                dirs[:] = [
                    name
                    for name in dirs
                    if name not in self._exclude_dirs and not name.endswith(".egg-info")
                ]
                for name in files:
                    candidate = path_root / name
                    if candidate.is_symlink():
                        continue
                    if (
                        self._include_extensions
                        and candidate.suffix not in self._include_extensions
                    ):
                        continue
                    yield base_resolved, candidate

    def _read_file_text(self, path: Path) -> Optional[str]:
        try:
            if path.stat().st_size > _MAX_INDEX_FILE_SIZE:
                return None
        except OSError:
            return None
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None
        except OSError:
            return None

    def _segment_file(self, path: Path, text: str) -> List[_RepoSegment]:
        suffix = path.suffix.lower()
        lines = text.splitlines()
        if suffix == ".py":
            segments = self._segment_python(path, lines)
            if segments:
                return segments
        if suffix in {".md", ".rst"}:
            segments = self._segment_markdown(path, lines)
            if segments:
                return segments
        return self._segment_generic(path, lines)

    def _segment_python(self, path: Path, lines: List[str]) -> List[_RepoSegment]:
        source = "\n".join(lines)
        try:
            module = ast.parse(source)
        except SyntaxError:
            return []

        segments: List[_RepoSegment] = []

        if module.body:
            first = module.body[0]
            if isinstance(first, ast.Expr) and isinstance(
                getattr(first, "value", None), ast.Constant
            ):
                constant = first.value
                if isinstance(constant.value, str):
                    start = getattr(first, "lineno", 1)
                    end = getattr(first, "end_lineno", start)
                    text_block = self._slice_lines(lines, start, end)
                    segment = self._make_segment(
                        path,
                        start,
                        end,
                        text_block,
                        {"language": "python", "kind": "docstring"},
                    )
                    if segment:
                        segments.append(segment)

        for node in module.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = getattr(node, "lineno", 1)
                end = getattr(node, "end_lineno", start)
                text_block = self._slice_lines(lines, start, end)
                segment = self._make_segment(
                    path,
                    start,
                    end,
                    text_block,
                    {
                        "language": "python",
                        "kind": "function",
                        "name": getattr(node, "name", ""),
                    },
                )
                if segment:
                    segments.append(segment)
            elif isinstance(node, ast.ClassDef):
                start = getattr(node, "lineno", 1)
                end = getattr(node, "end_lineno", start)
                text_block = self._slice_lines(lines, start, end)
                segment = self._make_segment(
                    path,
                    start,
                    end,
                    text_block,
                    {
                        "language": "python",
                        "kind": "class",
                        "name": getattr(node, "name", ""),
                    },
                )
                if segment:
                    segments.append(segment)

        if not segments:
            return []
        return segments

    def _segment_markdown(self, path: Path, lines: List[str]) -> List[_RepoSegment]:
        segments: List[_RepoSegment] = []
        total = len(lines)
        if total == 0:
            return segments
        current_start = 0
        for idx, line in enumerate(lines):
            if line.lstrip().startswith("#") and idx != current_start:
                text_block = self._slice_lines(lines, current_start + 1, idx)
                segment = self._make_segment(
                    path,
                    current_start + 1,
                    idx,
                    text_block,
                    {"language": "markdown", "kind": "section"},
                )
                if segment:
                    segments.append(segment)
                current_start = idx
        text_block = self._slice_lines(lines, current_start + 1, total)
        segment = self._make_segment(
            path,
            current_start + 1,
            total,
            text_block,
            {"language": "markdown", "kind": "section"},
        )
        if segment:
            segments.append(segment)
        return segments

    def _segment_generic(self, path: Path, lines: List[str]) -> List[_RepoSegment]:
        segments: List[_RepoSegment] = []
        window = max(_WINDOW_SIZE, 1)
        overlap = min(_WINDOW_OVERLAP, window - 1) if window > 1 else 0
        total = len(lines)
        if total == 0:
            return segments
        step = window - overlap if window > overlap else window
        start = 0
        while start < total:
            end = min(total, start + window)
            text_block = self._slice_lines(lines, start + 1, end)
            segment = self._make_segment(
                path,
                start + 1,
                end,
                text_block,
                {"language": self._guess_language(path), "kind": "block"},
            )
            if segment:
                segments.append(segment)
            if end == total:
                break
            start += step
        return segments

    def _make_segment(
        self,
        path: Path,
        start_line: int,
        end_line: int,
        text: str,
        metadata: Dict[str, Any],
    ) -> Optional[_RepoSegment]:
        cleaned = text.strip("\n")
        if not cleaned.strip():
            return None
        return _RepoSegment(
            path=path,
            start_line=start_line,
            end_line=end_line,
            text=cleaned,
            metadata=dict(metadata),
        )

    def _slice_lines(self, lines: List[str], start: int, end: int) -> str:
        start_index = max(start - 1, 0)
        end_index = max(start_index, min(end, len(lines)))
        return "\n".join(lines[start_index:end_index])

    def _guess_language(self, path: Path) -> str:
        suffix = path.suffix.lower().lstrip(".")
        if not suffix:
            return "text"
        return suffix

    def _relative_path(
        self, path: Path, base_root: Optional[Path] = None
    ) -> str:
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path
        roots: List[Path] = []
        if base_root is not None:
            roots.append(base_root)
        roots.append(self.repo_root)
        for root in roots:
            try:
                return resolved.relative_to(root).as_posix()
            except ValueError:
                continue
        return resolved.as_posix()

    def _write_index(self, entries: List[Dict[str, Any]]) -> Path:
        tmp_file = tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, dir=self.index_dir
        )
        try:
            for entry in entries:
                json.dump(entry, tmp_file, ensure_ascii=False)
                tmp_file.write("\n")
        finally:
            tmp_file.close()
        return Path(tmp_file.name)

    def _load_locked(self) -> None:
        records: List[_RepoIndexRecord] = []
        if not self.index_path.exists():
            self._records = []
            self._loaded = True
            return
        with self.index_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                payload = line.strip()
                if not payload:
                    continue
                try:
                    entry = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                record = _RepoIndexRecord(
                    identifier=str(entry.get("id") or ""),
                    path=str(entry.get("path") or ""),
                    start_line=int(entry.get("start_line") or 1),
                    end_line=int(entry.get("end_line") or 1),
                    text=str(entry.get("text") or ""),
                    embedding=_ensure_vector(entry.get("embedding")),
                    metadata=dict(entry.get("metadata") or {}),
                    timestamp=float(entry.get("ts") or 0.0),
                )
                records.append(record)
        self._records = records
        self._loaded = True

# ============================================================================
# Boot & Environment
# ============================================================================

APP_NAME = "Agent Virtual Desktop — Codex-Terminal"
VD_LOGGER_NAME = "VirtualDesktop"
VD_LOG_FILENAME = "vd_system.log"
VD_LOG_PATH: Path = Path()
MEMORY_SERVICES: MemoryServices | None = None
Excepthook = Callable[
    [type[BaseException], BaseException, Optional[TracebackType]],
    None,
]
_ORIGINAL_EXCEPTHOOK: Optional[Excepthook] = None


def _ensure_high_dpi_rounding_policy() -> None:
    """Apply pass-through DPI rounding before any QApplication is created."""

    if QGuiApplication.instance() is not None:
        return
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )


_ensure_high_dpi_rounding_policy()


def here() -> Path:
    """Return the directory containing this script."""

    return Path(__file__).resolve().parent


def _resolve_directory(path: Path) -> Path:
    """Expand, resolve, and create the provided directory path."""

    try:
        resolved = path.expanduser().resolve()
    except Exception:
        resolved = path.expanduser()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _default_workspace_path() -> Path:
    """Compute the fallback workspace root when no override is provided."""

    return here() / "Agent_Codex_Standalone"


def _legacy_transit_candidates() -> list[Path]:
    """Historical transit directories migrated into the current workspace."""

    return [here() / "Codex-Transit"]


def _migrate_legacy_transit(target: Path) -> None:
    """Fold any legacy transit directories into the target directory."""

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
                continue
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


def _shared_file_handler_attached(logger: logging.Logger, *, path: Path) -> bool:
    """Return ``True`` if the logger already writes to the requested path."""

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            try:
                if Path(handler.baseFilename).resolve() == path.resolve():
                    return True
            except Exception:
                continue
    return False


def configure_shared_logger(*, log_path: Optional[Path] = None) -> logging.Logger:
    """Attach a file handler targeting ``vd_system.log`` and return the logger."""

    logger = logging.getLogger(VD_LOGGER_NAME)
    target_path = log_path
    if target_path is None:
        default_path = _default_workspace_path() / VD_LOG_FILENAME
        target_path = VD_LOG_PATH if VD_LOG_PATH else default_path

    target_path.parent.mkdir(parents=True, exist_ok=True)

    if not _shared_file_handler_attached(logger, path=target_path):
        for handler in list(logger.handlers):
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
                try:
                    handler.close()
                except Exception:
                    pass
        file_handler = logging.FileHandler(target_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(file_handler)

    if logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)
    return logger


class BrainShellCrashDialog(QDialog):
    """High-contrast crash dialog surfaced when BrainShell hits a fatal error."""

    def __init__(
        self,
        details: str,
        *,
        log_path: Optional[Path] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("BrainShell — Crash Report")
        self.setModal(True)
        self.resize(960, 600)
        self.setObjectName("BrainShellCrashDialog")
        self.setStyleSheet(
            """
            QDialog#BrainShellCrashDialog {
                background-color: #0b1120;
                color: #f8fafc;
            }
            QLabel#CrashTitle {
                font-size: 20px;
                font-weight: 700;
            }
            QLabel#CrashSubtitle {
                color: #cbd5f5;
            }
            QTextBrowser {
                background-color: #020817;
                color: #e2e8f0;
                font-family: "Fira Code", "Source Code Pro", monospace;
                border: 1px solid #1e293b;
            }
            QPushButton {
                background-color: #1d4ed8;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            """
        )

        layout = QVBoxLayout(self)

        title = QLabel("BrainShell encountered an unrecoverable error.", self)
        title.setObjectName("CrashTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        subtitle_text = "A fatal exception was captured. Review the log and details below."
        if log_path:
            subtitle_text = f"A fatal exception was captured. System log: {log_path}"
        subtitle = QLabel(subtitle_text, self)
        subtitle.setObjectName("CrashSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.details = QTextBrowser(self)
        self.details.setPlainText(details)
        self.details.setReadOnly(True)
        layout.addWidget(self.details, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)

        copy_btn = QPushButton("Copy Details", self)
        copy_btn.clicked.connect(self._copy_details)  # type: ignore[arg-type]
        buttons.addWidget(copy_btn)

        close_btn = QPushButton("Exit BrainShell", self)
        close_btn.clicked.connect(self.accept)  # type: ignore[arg-type]
        buttons.addWidget(close_btn)

        layout.addLayout(buttons)

    def _copy_details(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        clipboard = app.clipboard()
        clipboard.setText(self.details.toPlainText())


def install_global_exception_handler(logger: logging.Logger, *, log_path: Optional[Path] = None) -> None:
    """Install a BrainShell-aligned crash handler capturing unhandled exceptions."""

    global _ORIGINAL_EXCEPTHOOK
    if _ORIGINAL_EXCEPTHOOK is None:
        _ORIGINAL_EXCEPTHOOK = sys.excepthook

    def _hook(exc_type: type[BaseException], exc: BaseException, tb: TracebackType | None) -> None:
        logger.error("Unhandled exception in ACAGi", exc_info=(exc_type, exc, tb))
        for handler in logger.handlers:
            try:
                handler.flush()
            except Exception:
                continue

        details = "".join(traceback.format_exception(exc_type, exc, tb))
        app = QApplication.instance()
        if app is None:
            try:
                stderr = sys.stderr
                stderr.write("Unhandled exception in ACAGi.\n")
                stderr.write(details)
                stderr.flush()
            except Exception:
                pass
        else:
            try:
                dialog = BrainShellCrashDialog(details, log_path=log_path)
                dialog.exec()
            except Exception:
                logger.error("Failed to display BrainShell crash dialog", exc_info=True)

        if _ORIGINAL_EXCEPTHOOK and _ORIGINAL_EXCEPTHOOK is not _hook:
            _ORIGINAL_EXCEPTHOOK(exc_type, exc, tb)

    sys.excepthook = _hook


class BootEnvironment:
    """Manage workspace, transit, logging, and crash capture bootstrapping."""

    def __init__(self) -> None:
        self.workspace: Path = Path()
        self.transit: Path = Path()
        self.agent_root: Path = Path()
        self.logs_root: Path = Path()
        self.log_path: Path = Path()
        self.logger: logging.Logger = logging.getLogger(VD_LOGGER_NAME)
        self.refresh()

    def refresh(self) -> logging.Logger:
        workspace = self._resolve_workspace()
        transit = self._resolve_transit(workspace)
        agent_root = workspace / ".codex_agent"
        agent_root.mkdir(parents=True, exist_ok=True)
        logs_root = agent_root / "logs"
        logs_root.mkdir(parents=True, exist_ok=True)
        log_path = logs_root / VD_LOG_FILENAME

        logger = configure_shared_logger(log_path=log_path)
        install_global_exception_handler(logger, log_path=log_path)

        self.workspace = workspace
        self.transit = transit
        self.agent_root = agent_root
        self.logs_root = logs_root
        self.log_path = log_path
        self.logger = logger

        global VD_LOG_PATH
        VD_LOG_PATH = log_path

        global MEMORY_SERVICES
        if MEMORY_SERVICES is not None:
            try:
                sessions_dir = self.agent_subdir("sessions")
                MEMORY_SERVICES.refresh(
                    lessons_path=MEMORY_PATH,
                    inbox_path=LOGIC_INBOX_PATH,
                    sessions_root=sessions_dir,
                )
            except Exception:
                logger.exception("Failed to refresh memory services during boot")

        return logger

    def agent_subdir(self, name: str) -> Path:
        subdir = self.agent_root / name
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir

    def _resolve_workspace(self) -> Path:
        override = os.environ.get("CODEX_WORKSPACE", "").strip()
        if override:
            return _resolve_directory(Path(override))
        return _resolve_directory(_default_workspace_path())

    def _resolve_transit(self, workspace: Path) -> Path:
        target = workspace / "Terminal Desktop"
        _migrate_legacy_transit(target)
        target.mkdir(parents=True, exist_ok=True)
        return target


BOOT_ENV = BootEnvironment()


def base_dir() -> Path:
    """Return the active workspace root for backwards compatibility."""

    return BOOT_ENV.workspace


def workspace_root() -> Path:
    """Expose the currently resolved workspace directory."""

    return BOOT_ENV.workspace


def agent_data_root() -> Path:
    """Directory scoped to Codex-managed assets inside the workspace."""

    return BOOT_ENV.agent_root


def agent_logs_dir() -> Path:
    """Location of the agent's persistent log directory."""

    return BOOT_ENV.logs_root


def transit_dir() -> Path:
    """Return the active transit directory used by the Terminal Desktop."""

    return BOOT_ENV.transit


def shared_logger() -> logging.Logger:
    """Retrieve the shared Virtual Desktop logger instance."""

    return BOOT_ENV.logger


def _agent_subdir(name: str) -> Path:
    return BOOT_ENV.agent_subdir(name)


def agent_images_dir() -> Path:
    return _agent_subdir("images")


# ============================================================================
# Settings loader
# ============================================================================

CONFIG_FILENAME = "acagi.ini"
CONFIG_PATH = BOOT_ENV.agent_subdir("config") / CONFIG_FILENAME

DEFAULT_RUNTIME_CONFIG = {
    "ui": {
        "status_variant": "detailed",
        "status_refresh_seconds": "15",
    },
    "mode": {
        "offline": "false",
        "sandbox": "restricted",
    },
    "limits": {
        "share_limit": "5",
        "event_rate_per_minute": "120",
    },
    "policy": {
        "sentinel": "strict",
        "auto_approve": "false",
    },
    "remote": {
        "event_bus": "",
        "sentinel": "",
    },
}


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    """Runtime configuration parsed from :mod:`acagi.ini`.

    Schema overview:
        ``[ui]``
            ``status_variant`` – ``minimal`` or ``detailed`` controls the status bar text.
            ``status_refresh_seconds`` – poll cadence for UI refresh helpers.
        ``[mode]``
            ``offline`` – boolean toggle gating remote integrations and telemetry.
            ``sandbox`` – sandbox profile (``isolated``, ``restricted``, ``trusted``).
        ``[limits]``
            ``share_limit`` – default context-sharing cap for reference sharing widgets.
            ``event_rate_per_minute`` – soft cap for remote event fan-out.
        ``[policy]``
            ``sentinel`` – label describing the active safety posture (``strict``/``monitor``).
            ``auto_approve`` – allow sentinel to auto-confirm risky commands in trusted mode.
        ``[remote]``
            ``event_bus`` – optional URL for remote event replication.
            ``sentinel`` – optional URL for a remote safety controller endpoint.
    """

    status_variant: str = "detailed"
    status_refresh_seconds: int = 15
    offline: bool = False
    sandbox: str = "restricted"
    share_limit: int = 5
    event_rate_per_minute: int = 120
    sentinel_policy: str = "strict"
    auto_approve: bool = False
    remote_event_bus: str = ""
    remote_sentinel: str = ""


POLICIES_FILENAME = "policies.json"

DEFAULT_POLICY_BUNDLE: Mapping[str, Any] = {
    "version": "0.1.0",
    "operations": {
        "coder": {
            "allow": [
                "python",
                "pip",
                "pip3",
                "pytest",
                "ruff",
                "black",
                "mypy",
                "npm",
                "yarn",
                "pnpm",
                "node",
                "cargo",
                "go",
                "mvn",
                "gradle",
                "make",
                "git",
            ],
            "deny": ["rm", "sudo", "chmod", "chown", "mkfs"],
            "approval": ["git"],
            "sandbox_modes": ["isolated", "restricted"],
            "notes": (
                "Coder operations must run in restricted sandboxes and prompt before "
                "mutating repositories."
            ),
        },
        "test": {
            "allow": [
                "python",
                "pytest",
                "tox",
                "npm",
                "yarn",
                "pnpm",
                "bun",
                "go",
                "cargo",
                "mvn",
                "gradle",
                "node",
                "make",
            ],
            "deny": ["rm", "sudo", "mkfs"],
            "approval": [],
            "sandbox_modes": ["isolated", "restricted", "trusted"],
            "notes": "Tests should stay non-destructive; blocked commands remain explicit.",
        },
    },
    "metadata": {"generated": "default"},
}


@dataclass(frozen=True, slots=True)
class OperationPolicy:
    """Allowlist, denylist, and sandbox requirements for an operation."""

    name: str
    allow_commands: frozenset[str] = field(default_factory=frozenset)
    deny_commands: frozenset[str] = field(default_factory=frozenset)
    approval_commands: frozenset[str] = field(default_factory=frozenset)
    sandbox_modes: frozenset[str] = field(default_factory=frozenset)
    notes: str = ""

    @classmethod
    def from_mapping(cls, name: str, payload: Mapping[str, Any]) -> "OperationPolicy":
        def _normalize(values: Any) -> frozenset[str]:
            if not isinstance(values, Iterable) or isinstance(values, (str, bytes)):
                return frozenset()
            cleaned = {
                str(value).strip().lower() for value in values if str(value).strip()
            }
            return frozenset(cleaned)

        allow = _normalize(payload.get("allow"))
        deny = _normalize(payload.get("deny"))
        approval = _normalize(payload.get("approval"))
        sandbox = _normalize(payload.get("sandbox_modes"))
        notes = str(payload.get("notes") or "").strip()
        return cls(
            name=name,
            allow_commands=allow,
            deny_commands=deny,
            approval_commands=approval,
            sandbox_modes=sandbox,
            notes=notes,
        )


@dataclass(frozen=True, slots=True)
class PolicyBundle:
    """Structured policies derived from ``policies.json``."""

    version: str
    operations: Dict[str, OperationPolicy]
    source_path: Optional[Path] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(
        cls, payload: Mapping[str, Any], *, source_path: Optional[Path] = None
    ) -> "PolicyBundle":
        version = str(payload.get("version") or "0.0.0").strip()
        operations_payload = payload.get("operations")
        operations: Dict[str, OperationPolicy] = {}
        if isinstance(operations_payload, Mapping):
            for name, op_payload in operations_payload.items():
                if not isinstance(op_payload, Mapping):
                    continue
                operations[name.lower()] = OperationPolicy.from_mapping(name, op_payload)

        metadata: Dict[str, Any] = {}
        extra_meta = payload.get("metadata")
        if isinstance(extra_meta, Mapping):
            metadata = dict(extra_meta)

        return cls(
            version=version,
            operations=operations,
            source_path=source_path,
            metadata=metadata,
        )

    def get(self, operation: str) -> Optional[OperationPolicy]:
        return self.operations.get(operation.lower())


class SettingsLoader:
    """Persist ACAGi runtime defaults while tolerating absent or corrupt files."""

    def __init__(
        self,
        path: Optional[Path] = None,
        defaults: Optional[Mapping[str, Mapping[str, str]]] = None,
        policy_path: Optional[Path] = None,
    ) -> None:
        self.path = path or CONFIG_PATH
        self.policies_path = policy_path or (self.path.parent / POLICIES_FILENAME)
        self.defaults: Mapping[str, Mapping[str, str]] = (
            defaults if defaults is not None else copy.deepcopy(DEFAULT_RUNTIME_CONFIG)
        )
        self._parser = configparser.ConfigParser()
        self._policies: Optional[PolicyBundle] = None

    # ------------------------------------------------------------------
    def load(self) -> RuntimeSettings:
        parser = configparser.ConfigParser()
        parser.read_dict(self.defaults)
        if self.path.exists():
            try:
                parser.read(self.path, encoding="utf-8")
            except (configparser.Error, OSError) as exc:
                logging.getLogger(__name__).warning(
                    "Failed to parse %s: %s – using defaults", self.path, exc
                )
        else:
            self._persist_defaults()
        self._parser = parser
        settings = self._coerce(parser)
        if not self.path.exists():
            self.save(settings)
        return settings

    # ------------------------------------------------------------------
    def load_policies(self) -> PolicyBundle:
        template = self._load_policy_template()
        payload: Mapping[str, Any] = template
        if self.policies_path.exists():
            try:
                raw = self.policies_path.read_text(encoding="utf-8")
                payload = json.loads(raw)
            except (OSError, json.JSONDecodeError) as exc:
                logging.getLogger(__name__).warning(
                    "Failed to parse %s: %s – using defaults",
                    self.policies_path,
                    exc,
                )
                payload = template
        else:
            self._persist_policies(template)

        bundle = PolicyBundle.from_mapping(payload, source_path=self.policies_path)
        self._policies = bundle
        if not self.policies_path.exists():
            self._persist_policies(template)
        return bundle

    # ------------------------------------------------------------------
    def save(self, settings: RuntimeSettings) -> None:
        payload = configparser.ConfigParser()
        payload.read_dict(DEFAULT_RUNTIME_CONFIG)
        payload["ui"]["status_variant"] = settings.status_variant
        payload["ui"]["status_refresh_seconds"] = str(settings.status_refresh_seconds)
        payload["mode"]["offline"] = str(settings.offline).lower()
        payload["mode"]["sandbox"] = settings.sandbox
        payload["limits"]["share_limit"] = str(settings.share_limit)
        payload["limits"]["event_rate_per_minute"] = str(settings.event_rate_per_minute)
        payload["policy"]["sentinel"] = settings.sentinel_policy
        payload["policy"]["auto_approve"] = str(settings.auto_approve).lower()
        payload["remote"]["event_bus"] = settings.remote_event_bus
        payload["remote"]["sentinel"] = settings.remote_sentinel
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            payload.write(fh)

    # ------------------------------------------------------------------
    def snapshot(self) -> Mapping[str, Mapping[str, str]]:
        parser = self._parser if self._parser.sections() else self._fresh_parser()
        data: Dict[str, Dict[str, str]] = {}
        for section in parser.sections():
            data[section] = {key: value for key, value in parser.items(section)}
        return data

    # ------------------------------------------------------------------
    def _coerce(self, parser: configparser.ConfigParser) -> RuntimeSettings:
        def get(section: str, option: str, fallback: str) -> str:
            try:
                return parser.get(section, option)
            except (configparser.Error, ValueError):
                return fallback

        def get_int(section: str, option: str, fallback: int) -> int:
            try:
                return int(parser.get(section, option))
            except (configparser.Error, ValueError, TypeError):
                return fallback

        def get_bool(section: str, option: str, fallback: bool) -> bool:
            try:
                return parser.getboolean(section, option)
            except (configparser.Error, ValueError, TypeError):
                return fallback

        status_variant = get("ui", "status_variant", "detailed").strip().lower()
        if status_variant not in {"minimal", "detailed"}:
            status_variant = "detailed"

        sandbox = get("mode", "sandbox", "restricted").strip().lower()
        if sandbox not in {"isolated", "restricted", "trusted"}:
            sandbox = "restricted"

        sentinel_policy = get("policy", "sentinel", "strict").strip().lower()
        if sentinel_policy not in {"strict", "monitor"}:
            sentinel_policy = "strict"

        remote_event_bus = get("remote", "event_bus", "").strip()
        remote_sentinel = get("remote", "sentinel", "").strip()

        return RuntimeSettings(
            status_variant=status_variant,
            status_refresh_seconds=max(1, get_int("ui", "status_refresh_seconds", 15)),
            offline=get_bool("mode", "offline", False),
            sandbox=sandbox,
            share_limit=max(1, get_int("limits", "share_limit", 5)),
            event_rate_per_minute=max(1, get_int("limits", "event_rate_per_minute", 120)),
            sentinel_policy=sentinel_policy,
            auto_approve=get_bool("policy", "auto_approve", False),
            remote_event_bus=remote_event_bus,
            remote_sentinel=remote_sentinel,
        )

    # ------------------------------------------------------------------
    def _load_policy_template(self) -> Mapping[str, Any]:
        template_path = here() / POLICIES_FILENAME
        if template_path.exists():
            try:
                return json.loads(template_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logging.getLogger(__name__).warning(
                    "Failed to parse policy template %s: %s – falling back to built-in",
                    template_path,
                    exc,
                )
        return copy.deepcopy(DEFAULT_POLICY_BUNDLE)

    # ------------------------------------------------------------------
    def _persist_policies(self, payload: Mapping[str, Any]) -> None:
        self.policies_path.parent.mkdir(parents=True, exist_ok=True)
        with self.policies_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")

    # ------------------------------------------------------------------
    def _persist_defaults(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        parser = configparser.ConfigParser()
        parser.read_dict(DEFAULT_RUNTIME_CONFIG)
        with self.path.open("w", encoding="utf-8") as fh:
            parser.write(fh)

    # ------------------------------------------------------------------
    def _fresh_parser(self) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        parser.read_dict(DEFAULT_RUNTIME_CONFIG)
        return parser


SETTINGS_LOADER = SettingsLoader()
RUNTIME_SETTINGS = SETTINGS_LOADER.load()
safety_manager.set_runtime_settings(RUNTIME_SETTINGS)
POLICY_BUNDLE = SETTINGS_LOADER.load_policies()
safety_manager.set_operation_policies(POLICY_BUNDLE.operations)
_SENTINEL_LOGGER = logging.getLogger("sentinel")
_SENTINEL_NOTIFIER_TOKEN: Optional[str] = None


def configure_safety_sentinel(settings: RuntimeSettings) -> None:
    """Align the safety manager with sandbox and policy runtime toggles."""

    global _SENTINEL_NOTIFIER_TOKEN

    try:
        safety_manager.set_runtime_settings(settings)
    except Exception:
        _SENTINEL_LOGGER.debug(
            "Failed to refresh runtime settings on safety manager", exc_info=True
        )

    try:
        safety_manager.install_file_guard()
    except Exception:
        _SENTINEL_LOGGER.exception("Failed to install file guard")

    if hasattr(safety_manager, "clear_protected"):
        try:
            safety_manager.clear_protected()
        except Exception:
            _SENTINEL_LOGGER.debug("Unable to clear protected paths", exc_info=True)

    protected_roots: List[Path] = []
    if settings.sandbox == "isolated":
        protected_roots = [workspace_root(), Path.home()]
    elif settings.sandbox == "restricted":
        protected_roots = [workspace_root()]

    for root in protected_roots:
        if not hasattr(safety_manager, "add_protected_directory"):
            break
        try:
            safety_manager.add_protected_directory(root)
        except Exception:
            _SENTINEL_LOGGER.debug("Failed to protect directory: %s", root, exc_info=True)

    if _SENTINEL_NOTIFIER_TOKEN and hasattr(safety_manager, "remove_notifier"):
        try:
            safety_manager.remove_notifier(_SENTINEL_NOTIFIER_TOKEN)
        except Exception:
            _SENTINEL_LOGGER.debug("Could not detach sentinel notifier", exc_info=True)
        _SENTINEL_NOTIFIER_TOKEN = None

    if hasattr(safety_manager, "add_notifier"):

        def _dispatch(message: str) -> None:
            _SENTINEL_LOGGER.info("%s", message)
            try:
                publish(
                    "system.metrics",
                    {
                        "kind": "sentinel",
                        "message": message,
                        "meta": {"policy": settings.sentinel_policy},
                    },
                )
            except Exception:
                _SENTINEL_LOGGER.debug("Unable to emit sentinel event", exc_info=True)

        try:
            _SENTINEL_NOTIFIER_TOKEN = safety_manager.add_notifier(_dispatch)
        except Exception:
            _SENTINEL_LOGGER.debug("Failed to attach sentinel notifier", exc_info=True)

    try:
        _ensure_sentinel_monitors(settings)
    except Exception:
        _SENTINEL_LOGGER.debug(
            "Unable to refresh sentinel monitors", exc_info=True
        )


def agent_sessions_dir() -> Path:
    return _agent_subdir("sessions")


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


def terminal_desktop_dir() -> Path:
    """Location for the standalone terminal's desktop workspace."""

    return transit_dir()


def lexicons_dir() -> Path:
    return agent_lexicons_dir()


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


_DEPENDENCY_LABELS: Dict[str, str] = {
    _REQUESTS_MODULE_NAME: "requests",
    _PILLOW_MODULE_NAME: "Pillow",
}
_DEPENDENCY_WARNINGS_EMITTED: Set[str] = set()


class OptionalDependencyError(RuntimeError):
    """Raised when an optional module required for a feature is unavailable."""

    def __init__(self, module_name: str, feature: str):
        self.module_name = module_name
        self.feature = feature
        dependency = _DEPENDENCY_LABELS.get(module_name, module_name)
        message = f"{dependency} not installed"
        if feature:
            message = f"{dependency} not installed — required for {feature}"
        super().__init__(message)
        self.dependency = dependency

    @property
    def user_message(self) -> str:
        """Return the human-readable notification for UI surfaces."""

        return str(self)


@lru_cache(maxsize=None)
def _load_optional_dependency(module_name: str) -> Optional[ModuleType]:
    """Attempt to import a module, caching the result to avoid repeated probes."""

    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def dependency_available(module_name: str) -> bool:
    """Return ``True`` when the optional dependency can be imported."""

    return _load_optional_dependency(module_name) is not None


def ensure_dependency(module_name: str, feature: str) -> ModuleType:
    """Return the imported module or raise :class:`OptionalDependencyError`."""

    module = _load_optional_dependency(module_name)
    if module is None:
        raise OptionalDependencyError(module_name, feature)
    return module


def requests_available() -> bool:
    """Check whether the ``requests`` HTTP client is usable."""

    return dependency_available(_REQUESTS_MODULE_NAME)


def ensure_requests(feature: str) -> ModuleType:
    """Return the ``requests`` module or raise for the given feature context."""

    return ensure_dependency(_REQUESTS_MODULE_NAME, feature)


# ============================================================================
# Task Persistence and Eventing (Inlined from Dev_Logic/tasks)
# ============================================================================
"""Task data models, event bus, diff capture, and UI integration."""


TASKS_DATA_ROOT = Path(__file__).resolve().parent / "Dev_Logic" / "datasets"
TASKS_FILE = TASKS_DATA_ROOT / "tasks.jsonl"
EVENTS_FILE = TASKS_DATA_ROOT / "task_events.jsonl"
DIFFS_FILE = TASKS_DATA_ROOT / "diffs.jsonl"
ERRORS_FILE = TASKS_DATA_ROOT / "errors.jsonl"
_RUNS_SUBDIR = "runs"
_RUN_LOG_FILENAME = "run.log"


@dataclass(slots=True)
class TaskDiffSummary:
    """Summary of cumulative diff counts attached to a task."""

    added: int = 0
    removed: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {"added": int(self.added), "removed": int(self.removed)}


@dataclass(slots=True)
class Task:
    """Representation of a tracked task entry."""

    id: str
    title: str
    status: str
    created_ts: float
    updated_ts: float
    session_id: str
    source: str
    labels: List[str] = field(default_factory=list)
    diffs: TaskDiffSummary = field(default_factory=TaskDiffSummary)
    files: List[str] = field(default_factory=list)
    run_log_path: Optional[str] = None
    codex_conversation_id: Optional[str] = None
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
            "session_id": self.session_id,
            "source": self.source,
            "labels": list(self.labels),
            "diffs": self.diffs.to_dict(),
            "files": list(self.files),
            "run_log_path": self.run_log_path,
            "codex_conversation_id": self.codex_conversation_id,
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Task":
        diffs_payload = payload.get("diffs") or {}
        summary = TaskDiffSummary(
            added=int(diffs_payload.get("added", 0)),
            removed=int(diffs_payload.get("removed", 0)),
        )
        return cls(
            id=str(payload["id"]),
            title=str(payload["title"]),
            status=str(payload["status"]),
            created_ts=float(payload["created_ts"]),
            updated_ts=float(payload["updated_ts"]),
            session_id=str(payload["session_id"]),
            source=str(payload["source"]),
            labels=list(payload.get("labels", [])),
            diffs=summary,
            files=list(payload.get("files", [])),
            run_log_path=payload.get("run_log_path"),
            codex_conversation_id=payload.get("codex_conversation_id"),
            parent_id=payload.get("parent_id"),
        )


@dataclass(slots=True)
class TaskEvent:
    """Immutable event describing a change to a task."""

    ts: float
    task_id: str
    event: str
    by: Optional[str] = None
    to: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "ts": self.ts,
            "task_id": self.task_id,
            "event": self.event,
        }
        if self.by is not None:
            payload["by"] = self.by
        if self.to is not None:
            payload["to"] = self.to
        if self.data is not None:
            payload["data"] = self.data
        return payload


@dataclass(slots=True)
class DiffSnapshot:
    """Snapshot of diff statistics emitted during a task run."""

    ts: float
    task_id: str
    added: int
    removed: int
    files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts,
            "task_id": self.task_id,
            "added": int(self.added),
            "removed": int(self.removed),
            "files": list(self.files),
        }


@dataclass(slots=True)
class ErrorRecord:
    """Structured record describing a captured error event."""

    ts: float
    level: str
    kind: str
    msg: str
    path: Optional[str] = None
    task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "ts": float(self.ts),
            "level": str(self.level),
            "kind": str(self.kind),
            "msg": str(self.msg),
        }
        if self.path is not None:
            payload["path"] = self.path
        if self.task_id is not None:
            payload["task_id"] = self.task_id
        return payload


def _ensure_datasets_dir() -> None:
    TASKS_DATA_ROOT.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_datasets_dir()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    items: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def _write_jsonl_atomic(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    _ensure_datasets_dir()
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    os.replace(tmp_path, path)


def _dataset_root(candidate: Optional[Path]) -> Path:
    return Path(candidate) if candidate else TASKS_DATA_ROOT


def append_error_record(record: ErrorRecord) -> None:
    """Persist ``record`` to the shared ``errors.jsonl`` dataset."""

    _append_jsonl(ERRORS_FILE, record.to_dict())


def resolve_run_log_path(task: Task, dataset_root: Optional[Path] = None) -> Tuple[Path, str]:
    """Return absolute and relative run-log paths for ``task``."""

    root = _dataset_root(dataset_root)
    if task.run_log_path:
        raw = Path(task.run_log_path)
    else:
        raw = Path(_RUNS_SUBDIR) / task.id / _RUN_LOG_FILENAME
    absolute = raw if raw.is_absolute() else root / raw
    relative = raw.as_posix()
    return absolute, relative


def append_run_log(
    task: Task,
    lines: Iterable[str] | str,
    dataset_root: Optional[Path] = None,
    *,
    channel: Optional[str] = None,
) -> Tuple[Path, str, bool]:
    """Append ``lines`` to the task run log, creating directories as needed."""

    absolute, relative = resolve_run_log_path(task, dataset_root)
    absolute.parent.mkdir(parents=True, exist_ok=True)

    created = task.run_log_path is None

    if isinstance(lines, str):
        entries = [lines]
    else:
        entries = [str(line) for line in lines]

    if entries:
        prefix = f"[{channel}]" if channel else ""
        with absolute.open("a", encoding="utf-8") as fh:
            for entry in entries:
                text = entry.rstrip("\n")
                if prefix:
                    text = f"{prefix} {text}" if text else prefix
                fh.write((text + "\n") if text else "\n")
    else:
        absolute.touch(exist_ok=True)

    if task.run_log_path is None:
        task.run_log_path = relative

    return absolute, relative, created


def append_run_output(
    task: Task,
    *,
    stdout: str = "",
    stderr: str = "",
    dataset_root: Optional[Path] = None,
) -> Tuple[Path, str, bool]:
    """Append captured stdout/stderr streams to the task run log."""

    created = False
    path: Optional[Path] = None
    relative: Optional[str] = None

    if stdout:
        path, relative, created_stdout = append_run_log(
            task,
            stdout.splitlines(),
            dataset_root,
            channel="stdout",
        )
        created = created or created_stdout

    if stderr:
        path, relative, created_stderr = append_run_log(
            task,
            stderr.splitlines(),
            dataset_root,
            channel="stderr",
        )
        created = created or created_stderr

    if path is None or relative is None:
        path, relative = resolve_run_log_path(task, dataset_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        if task.run_log_path is None:
            task.run_log_path = relative
            created = True

    return path, relative, created


def load_run_log_tail(
    task: Task,
    dataset_root: Optional[Path] = None,
    *,
    max_lines: int = 200,
) -> List[str]:
    """Return the last ``max_lines`` entries from the task run log."""

    if max_lines <= 0:
        return []
    if not task.run_log_path:
        return []

    absolute, _ = resolve_run_log_path(task, dataset_root)
    if not absolute.exists():
        return []

    tail: Deque[str] = deque(maxlen=int(max_lines))
    with absolute.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            tail.append(line.rstrip("\n"))
    return list(tail)


def append_task(task: Task) -> None:
    """Append a task entry to ``tasks.jsonl``."""

    _append_jsonl(TASKS_FILE, task.to_dict())


def update_task(task_id: str, **changes: Any) -> Task:
    """Apply updates to a task entry and rewrite the dataset atomically."""

    records = _read_jsonl(TASKS_FILE)
    updated_record: Optional[Dict[str, Any]] = None
    for record in records:
        if record.get("id") == task_id:
            record.update(changes)
            updated_record = record
            break
    if updated_record is None:
        raise ValueError(f"Task '{task_id}' does not exist")
    _write_jsonl_atomic(TASKS_FILE, records)
    return Task.from_dict(updated_record)


def append_event(event: TaskEvent) -> None:
    """Append a task event to ``task_events.jsonl``."""

    _append_jsonl(EVENTS_FILE, event.to_dict())


# -- Event dispatcher -------------------------------------------------------

Subscriber = Callable[[dict], None]

DEFAULT_EVENT_TOPICS: Set[str] = {
    # Human-facing streams sourced from observations, annotations, and tasks.
    "observation",
    "observation.delta",
    "note",
    "note.appended",
    "task",
    "task.created",
    "task.updated",
    "task.status",
    "task.diff",
    "task.deleted",
    "task.conversation",
    # System coordination and metrics feeds.
    "system.metrics",
    "system.process",
    "system.immune",
}
_WILDCARD_TOPIC = "task.*"


class _SubscriptionState:
    """Runtime state for a single subscriber including queue backpressure."""

    __slots__ = (
        "callback",
        "max_pending",
        "queue",
        "lock",
        "delivering",
        "dropped",
    )

    def __init__(self, callback: Subscriber, *, max_pending: int) -> None:
        self.callback = callback
        self.max_pending = max_pending
        self.queue: Deque[dict] = deque()
        self.lock = RLock()
        self.delivering = False
        self.dropped = 0

    def enqueue(self, topic: str, payload: dict, *, logger: logging.Logger) -> bool:
        """Add ``payload`` and return ``True`` when the queue should be drained."""

        with self.lock:
            if len(self.queue) >= self.max_pending:
                self.dropped += 1
                logger.warning(
                    "Backpressure drop topic=%s callback=%r dropped=%s",
                    topic,
                    self.callback,
                    self.dropped,
                )
                return False
            self.queue.append(payload)
            should_start = not self.delivering
            # Mark as delivering so concurrent publishers avoid double drains.
            if should_start:
                self.delivering = True
            return should_start

    def start_delivery(self) -> Optional[dict]:
        """Pop the next payload or release the delivery flag when empty."""

        with self.lock:
            if not self.queue:
                self.delivering = False
                return None
            return self.queue.popleft()

    def finish_delivery(self) -> bool:
        """Return ``True`` when more payloads remain queued."""

        with self.lock:
            if self.queue:
                return True
            self.delivering = False
            return False


class Subscription:
    """Handle returned from :func:`subscribe` that can detach a listener."""

    __slots__ = ("_dispatcher", "_topic", "_state", "_active")

    def __init__(self, dispatcher: "EventDispatcher", topic: str, state: _SubscriptionState) -> None:
        self._dispatcher = dispatcher
        self._topic = topic
        self._state = state
        self._active = True

    @property
    def active(self) -> bool:
        return self._active

    def unsubscribe(self) -> None:
        if not self._active:
            return
        self._dispatcher._detach(self._topic, self._state)
        self._active = False

    def __call__(self) -> None:  # pragma: no cover - sugar
        self.unsubscribe()


class EventDispatcher:
    """Centralized pub/sub dispatcher with bounded subscriber queues."""

    def __init__(
        self,
        *,
        topics: Iterable[str],
        wildcard_topic: str,
        logger: Optional[logging.Logger] = None,
        rate_window: float = 60.0,
    ) -> None:
        self._topics: Set[str] = set(topics)
        self._wildcard = wildcard_topic
        self._subscribers: MutableMapping[str, List[_SubscriptionState]] = defaultdict(list)
        self._lock = RLock()
        self._logger = logger or logging.getLogger(f"{VD_LOGGER_NAME}.events")
        self._rate_window = rate_window
        self._remote_history: Deque[float] = deque()
        self._remote_url = RUNTIME_SETTINGS.remote_event_bus
        self._rate_limit = max(1, RUNTIME_SETTINGS.event_rate_per_minute)

    # ------------------------------------------------------------------
    def register_topic(self, topic: str) -> None:
        """Register ``topic`` to allow future subscriptions."""

        if not topic:
            raise ValueError("topic must be a non-empty string")
        with self._lock:
            self._topics.add(topic)

    # ------------------------------------------------------------------
    def subscribe(
        self,
        topic: str,
        callback: Subscriber,
        *,
        max_pending: int = 32,
    ) -> Subscription:
        """Register ``callback`` for ``topic`` with bounded queue backpressure."""

        if not callable(callback):
            raise TypeError("callback must be callable")

        if topic != self._wildcard and topic not in self._topics:
            raise ValueError(f"Unsupported topic: {topic!r}")

        if max_pending < 1:
            raise ValueError("max_pending must be >= 1")

        state = _SubscriptionState(callback, max_pending=max_pending)
        with self._lock:
            self._subscribers[topic].append(state)

        self._logger.debug(
            "Subscribed callback=%r topic=%s max_pending=%s", callback, topic, max_pending
        )
        return Subscription(self, topic, state)

    # ------------------------------------------------------------------
    def publish(self, topic: str, payload: dict) -> None:
        """Broadcast ``payload`` to subscribers registered for ``topic``."""

        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary")

        if topic not in self._topics:
            raise ValueError(f"Unsupported topic: {topic!r}")

        enriched_payload = dict(payload)
        meta = dict(enriched_payload.get("meta", {}))
        meta.setdefault("offline", RUNTIME_SETTINGS.offline)
        meta.setdefault("sandbox", RUNTIME_SETTINGS.sandbox)
        meta.setdefault("share_limit", RUNTIME_SETTINGS.share_limit)
        meta.setdefault("sentinel_policy", RUNTIME_SETTINGS.sentinel_policy)
        enriched_payload["meta"] = meta

        deliveries: List[_SubscriptionState] = []
        with self._lock:
            listeners = list(self._subscribers.get(topic, ()))
            wildcard_listeners = list(self._subscribers.get(self._wildcard, ()))

        for state in (*listeners, *wildcard_listeners):
            should_start = state.enqueue(topic, enriched_payload, logger=self._logger)
            if should_start:
                deliveries.append(state)

        subscriber_count = len(listeners) + len(wildcard_listeners)
        self._logger.info(
            "Event published topic=%s subscribers=%s keys=%s",
            topic,
            subscriber_count,
            list(enriched_payload.keys()),
        )

        for state in deliveries:
            self._drain(state, topic)

        self._fan_out_remote(topic, enriched_payload)

    # ------------------------------------------------------------------
    def _detach(self, topic: str, state: _SubscriptionState) -> None:
        with self._lock:
            listeners = self._subscribers.get(topic)
            if not listeners:
                return
            try:
                listeners.remove(state)
            except ValueError:
                return
            if not listeners:
                self._subscribers.pop(topic, None)
        self._logger.debug("Unsubscribed callback=%r topic=%s", state.callback, topic)

    # ------------------------------------------------------------------
    def _drain(self, state: _SubscriptionState, topic: str) -> None:
        while True:
            payload = state.start_delivery()
            if payload is None:
                return
            try:
                state.callback(payload)
            except Exception:  # pragma: no cover - defensive logging
                self._logger.exception("Error dispatching %s to %r", topic, state.callback)
            finally:
                if not state.finish_delivery():
                    return

    # ------------------------------------------------------------------
    def _fan_out_remote(self, topic: str, payload: dict) -> None:
        if not self._remote_url or RUNTIME_SETTINGS.offline:
            return

        now = time.monotonic()
        with self._lock:
            while self._remote_history and now - self._remote_history[0] > self._rate_window:
                self._remote_history.popleft()
            if len(self._remote_history) >= self._rate_limit:
                self._logger.warning(
                    "Remote event bus limit reached (%s/min) – dropping %s", self._rate_limit, topic
                )
                return
            self._remote_history.append(now)

        self._logger.debug(
            "Remote fan-out to %s topic=%s payload_keys=%s",
            self._remote_url,
            topic,
            list(payload.keys()),
        )


EVENT_DISPATCHER = EventDispatcher(
    topics=DEFAULT_EVENT_TOPICS,
    wildcard_topic=_WILDCARD_TOPIC,
    logger=logging.getLogger(f"{VD_LOGGER_NAME}.events"),
)


def register_topic(topic: str) -> None:
    """Expose ``topic`` for future subscriptions."""

    EVENT_DISPATCHER.register_topic(topic)


def subscribe(topic: str, callback: Subscriber, *, max_pending: int = 32) -> Subscription:
    """Register ``callback`` for ``topic`` and return an unsubscribe handle."""

    return EVENT_DISPATCHER.subscribe(topic, callback, max_pending=max_pending)


def publish(topic: str, payload: dict) -> None:
    """Broadcast ``payload`` to subscribers registered for ``topic``."""

    EVENT_DISPATCHER.publish(topic, payload)


class ImmuneResponse(Enum):
    """Enumerate sentinel immune response strategies."""

    COOLDOWN = "cooldown"
    QUARANTINE = "quarantine"
    ROLLBACK = "rollback"


@dataclass(slots=True)
class SentinelIncident:
    """Container describing a sentinel-triggered immune response."""

    task_id: str
    response: ImmuneResponse
    reason: str
    notes: str
    timestamp: float

    def to_payload(self, *, sandbox: str, policy: str) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "response": self.response.value,
            "reason": self.reason,
            "notes": self.notes,
            "timestamp": datetime.fromtimestamp(self.timestamp, UTC).isoformat(),
            "sandbox": sandbox,
            "policy": policy,
        }


class SentinelMonitorHub:
    """Subscribe to event bus topics and emit immune responses."""

    _SUCCESS_STATES = {
        "done",
        "complete",
        "completed",
        "merged",
        "passed",
        "resolved",
        "success",
    }

    def __init__(self, dispatcher: EventDispatcher, settings: RuntimeSettings) -> None:
        self._dispatcher = dispatcher
        self._logger = logging.getLogger(f"{VD_LOGGER_NAME}.sentinel.monitor")
        self._lock = RLock()
        self._settings = settings
        self._status_history: Dict[str, Deque[Tuple[str, float]]] = defaultdict(
            lambda: deque(maxlen=8)
        )
        self._last_progress: Dict[str, float] = {}
        self._response_backoff: Dict[Tuple[str, ImmuneResponse], float] = {}
        self._loop_window = 240.0
        self._stall_threshold = 600.0
        self._stall_interval = 60.0
        self._backoff_seconds = 300.0
        self._stop = threading.Event()
        self._subscriptions: List[Subscription] = []
        self._thread: Optional[threading.Thread] = None
        self.configure(settings)
        self._install_subscriptions()
        self._start_watcher()
        atexit.register(self.shutdown)

    # ------------------------------------------------------------------
    def configure(self, settings: RuntimeSettings) -> None:
        with self._lock:
            self._settings = settings
            if settings.sentinel_policy == "monitor":
                self._backoff_seconds = 180.0
                self._stall_threshold = 900.0
            else:
                self._backoff_seconds = 300.0
                self._stall_threshold = 600.0

    # ------------------------------------------------------------------
    def trigger_manual(
        self,
        task_id: str,
        response: ImmuneResponse,
        reason: str,
        notes: str,
    ) -> None:
        self._emit_response(task_id, response, reason, notes, force=True)

    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        self._stop.set()
        for sub in list(self._subscriptions):
            try:
                sub.unsubscribe()
            except Exception:
                self._logger.debug("Unable to detach sentinel subscription", exc_info=True)
        self._subscriptions.clear()
        thread = self._thread
        if thread and thread.is_alive() and threading.current_thread() is not thread:
            thread.join(timeout=1.0)

    # ------------------------------------------------------------------
    def _start_watcher(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._watch_stalls,
            name="SentinelStallWatcher",
            daemon=True,
        )
        self._thread.start()

    # ------------------------------------------------------------------
    def _install_subscriptions(self) -> None:
        self._subscriptions.append(subscribe("task.status", self._on_task_status))
        self._subscriptions.append(subscribe("task.diff", self._on_task_diff))
        self._subscriptions.append(subscribe("task.updated", self._on_task_updated))

    # ------------------------------------------------------------------
    def _on_task_status(self, payload: Mapping[str, Any]) -> None:
        task_id = str(payload.get("id") or payload.get("task_id") or "").strip()
        status = payload.get("status") or payload.get("to")
        if not task_id or not status:
            return
        normalized = str(status).strip().lower()
        if not normalized:
            return

        now = time.time()
        with self._lock:
            history = self._status_history[task_id]
            if history and history[-1][0] == normalized:
                self._last_progress[task_id] = now
                return
            history.append((normalized, now))
            self._last_progress[task_id] = now

        self._detect_loop(task_id)
        self._detect_regression(task_id)

    # ------------------------------------------------------------------
    def _on_task_diff(self, payload: Mapping[str, Any]) -> None:
        task_id = str(payload.get("id") or payload.get("task_id") or "").strip()
        if not task_id:
            return
        with self._lock:
            self._last_progress[task_id] = time.time()

    # ------------------------------------------------------------------
    def _on_task_updated(self, payload: Mapping[str, Any]) -> None:
        task_id = str(payload.get("id") or payload.get("task_id") or "").strip()
        if not task_id:
            return
        with self._lock:
            self._last_progress[task_id] = time.time()

    # ------------------------------------------------------------------
    def _detect_loop(self, task_id: str) -> None:
        with self._lock:
            history = list(self._status_history.get(task_id, ()))

        if len(history) < 4:
            return

        recent = history[-4:]
        statuses = [status for status, _ in recent]
        unique = {status for status in statuses}
        if len(unique) > 2:
            return

        first, second, third, fourth = statuses
        if first == second:
            return
        if first == third and second == fourth:
            window = recent[-1][1] - recent[0][1]
            if window <= self._loop_window:
                notes = (
                    f"Status loop {first}->{second} repeated within {int(window)}s"
                )
                self._emit_response(
                    task_id,
                    ImmuneResponse.COOLDOWN,
                    "loop",
                    notes,
                )

    # ------------------------------------------------------------------
    def _detect_regression(self, task_id: str) -> None:
        with self._lock:
            history = list(self._status_history.get(task_id, ()))

        if len(history) < 2:
            return

        prev_status, prev_ts = history[-2]
        current_status, current_ts = history[-1]
        if prev_status in self._SUCCESS_STATES and current_status not in self._SUCCESS_STATES:
            delta = max(0, int(current_ts - prev_ts))
            notes = (
                f"Regressed from {prev_status} to {current_status} after {delta}s"
            )
            self._emit_response(
                task_id,
                ImmuneResponse.ROLLBACK,
                "regression",
                notes,
            )

    # ------------------------------------------------------------------
    def _watch_stalls(self) -> None:
        while not self._stop.wait(self._stall_interval):
            now = time.time()
            with self._lock:
                items = list(self._last_progress.items())
            for task_id, last_ts in items:
                if now - last_ts >= self._stall_threshold:
                    notes = f"No progress for {int(now - last_ts)}s"
                    self._emit_response(
                        task_id,
                        ImmuneResponse.QUARANTINE,
                        "stall",
                        notes,
                    )

    # ------------------------------------------------------------------
    def _emit_response(
        self,
        task_id: str,
        response: ImmuneResponse,
        reason: str,
        notes: str,
        *,
        force: bool = False,
    ) -> None:
        now = time.time()
        with self._lock:
            sandbox = getattr(self._settings, "sandbox", "unknown")
            policy = getattr(self._settings, "sentinel_policy", "unknown")
            if not force and not self._update_backoff_locked(task_id, response, now):
                return
            if force:
                self._response_backoff[(task_id, response)] = now

        incident = SentinelIncident(
            task_id=task_id,
            response=response,
            reason=reason,
            notes=notes,
            timestamp=now,
        )
        payload = incident.to_payload(sandbox=sandbox, policy=policy)
        try:
            publish("system.immune", payload)
        except Exception:
            self._logger.debug("Unable to publish immune response", exc_info=True)
        self._logger.warning(
            "Sentinel immune response=%s task=%s reason=%s notes=%s",
            response.value,
            task_id,
            reason,
            notes,
        )

    # ------------------------------------------------------------------
    def _update_backoff_locked(
        self, task_id: str, response: ImmuneResponse, now: float
    ) -> bool:
        key = (task_id, response)
        last = self._response_backoff.get(key)
        if last is not None and now - last < self._backoff_seconds:
            return False
        self._response_backoff[key] = now
        return True


_SENTINEL_MONITOR_HUB: Optional[SentinelMonitorHub] = None


def _ensure_sentinel_monitors(settings: RuntimeSettings) -> SentinelMonitorHub:
    global _SENTINEL_MONITOR_HUB
    if _SENTINEL_MONITOR_HUB is None:
        _SENTINEL_MONITOR_HUB = SentinelMonitorHub(EVENT_DISPATCHER, settings)
    else:
        _SENTINEL_MONITOR_HUB.configure(settings)
    return _SENTINEL_MONITOR_HUB


def trigger_manual_immune_response(
    task_id: str, response: ImmuneResponse, reason: str, notes: str
) -> None:
    hub = _ensure_sentinel_monitors(RUNTIME_SETTINGS)
    hub.trigger_manual(task_id, response, reason, notes)


configure_safety_sentinel(RUNTIME_SETTINGS)


# -- Diff capture -----------------------------------------------------------

_SNAPSHOT_ROOT = TASKS_DATA_ROOT / _RUNS_SUBDIR


@dataclass(slots=True)
class _Target:
    """Normalized representation of a candidate file path."""

    abs_path: Path
    rel_workspace: str
    rel_repo: Optional[str] = None


def record_diff(
    task_id: str,
    files: Optional[Iterable[str]] = None,
    workspace_root: str | Path | None = None,
    timestamp: float | None = None,
) -> Optional[DiffSnapshot]:
    """Capture diff statistics for ``task_id`` and persist the results."""

    if not task_id:
        raise ValueError("task_id is required")

    workspace = Path(workspace_root or Path.cwd()).resolve()
    ts = float(timestamp) if timestamp is not None else time.time()

    targets = _normalize_targets(files, workspace)

    repo_root = _detect_git_repo(workspace)
    if repo_root:
        for target in targets.values():
            try:
                rel_repo = target.abs_path.resolve().relative_to(repo_root)
            except ValueError:
                continue
            target.rel_repo = rel_repo.as_posix()

    git_added = git_removed = 0
    git_files: List[str] = []
    git_handled: Set[Path] = set()
    if repo_root:
        git_added, git_removed, git_files, git_handled = _git_numstat(
            repo_root, workspace, targets
        )

    snapshot_added = snapshot_removed = 0
    snapshot_files: List[str] = []
    if targets:
        snapshot_added, snapshot_removed, snapshot_files = _snapshot_diff(
            task_id, targets, git_handled
        )

    total_added = git_added + snapshot_added
    total_removed = git_removed + snapshot_removed
    all_files = _unique(git_files + snapshot_files)

    if (
        not all_files
        and not targets
        and total_added == 0
        and total_removed == 0
    ):
        return None

    updated = update_task(
        task_id,
        diffs=TaskDiffSummary(added=total_added, removed=total_removed).to_dict(),
        updated_ts=ts,
    )

    snapshot = DiffSnapshot(
        ts=ts,
        task_id=task_id,
        added=total_added,
        removed=total_removed,
        files=all_files,
    )
    _append_diff_snapshot(snapshot)

    publish(
        "task.diff",
        {
            "id": updated.id,
            "added": total_added,
            "removed": total_removed,
            "files": list(all_files),
        },
    )
    return snapshot


def _normalize_targets(files: Optional[Iterable[str]], workspace: Path) -> Dict[Path, _Target]:
    if not files:
        return {}

    targets: Dict[Path, _Target] = {}
    for entry in files:
        if not entry:
            continue
        candidate = Path(entry)
        abs_path = candidate if candidate.is_absolute() else (workspace / candidate)
        abs_path = abs_path.resolve()
        rel_workspace = _relative_to_workspace(abs_path, workspace)
        targets[abs_path] = _Target(abs_path=abs_path, rel_workspace=rel_workspace)
    return targets


def _relative_to_workspace(path: Path, workspace: Path) -> str:
    try:
        rel = path.relative_to(workspace)
        return rel.as_posix()
    except ValueError:
        return path.as_posix()


def _detect_git_repo(start: Path) -> Optional[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    top = result.stdout.strip()
    if not top:
        return None
    return Path(top).resolve()


def _git_numstat(
    repo_root: Path,
    workspace: Path,
    targets: Dict[Path, _Target],
) -> Tuple[int, int, List[str], Set[Path]]:
    paths = sorted({target.rel_repo for target in targets.values() if target.rel_repo})

    cmd: List[str] = [
        "git",
        "-C",
        str(repo_root),
        "--no-optional-locks",
        "diff",
        "--numstat",
    ]
    if paths:
        cmd.append("--")
        cmd.extend(paths)

    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return 0, 0, [], set()
    if result.returncode != 0:
        return 0, 0, [], set()

    added_total = removed_total = 0
    files: List[str] = []
    handled: Set[Path] = set()

    for line in result.stdout.splitlines():
        parsed = _parse_numstat_line(line)
        if not parsed:
            continue
        added, removed, rel_path = parsed
        abs_path = (repo_root / rel_path).resolve()
        files.append(_relative_to_workspace(abs_path, workspace))
        added_total += added
        removed_total += removed
        if abs_path in targets:
            handled.add(abs_path)
    return added_total, removed_total, _unique(files), handled


def _parse_numstat_line(line: str) -> Optional[Tuple[int, int, str]]:
    parts = line.strip().split("\t", 2)
    if len(parts) != 3:
        return None
    added_str, removed_str, path_field = parts
    added = _parse_int(added_str)
    removed = _parse_int(removed_str)
    normalized = _normalize_numstat_path(path_field)
    if not normalized:
        return None
    return added, removed, normalized


def _parse_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def _normalize_numstat_path(field: str) -> str:
    field = field.strip()
    if not field:
        return ""
    if " => " in field:
        return _normalize_rename(field, " => ")
    if "->" in field:
        return _normalize_rename(field, "->")
    return field


def _normalize_rename(field: str, token: str) -> str:
    cleaned = field.replace("{", "").replace("}", "")
    parts = cleaned.split(token, 1)
    if len(parts) != 2:
        return cleaned.strip()
    left, right = parts[0].strip(), parts[1].strip()
    if "/" in left:
        prefix = left.rsplit("/", 1)[0]
        if prefix:
            if right.startswith(prefix):
                return right
            return f"{prefix}/{right}"
    return right


def _snapshot_diff(
    task_id: str,
    targets: Dict[Path, _Target],
    skip: Set[Path],
) -> Tuple[int, int, List[str]]:
    added_total = removed_total = 0
    files: List[str] = []
    for abs_path, target in targets.items():
        if abs_path in skip:
            continue
        added, removed = _compute_snapshot_counts(task_id, abs_path, target.rel_workspace)
        if added or removed:
            files.append(target.rel_workspace)
        added_total += added
        removed_total += removed
    return added_total, removed_total, _unique(files)


def _compute_snapshot_counts(task_id: str, abs_path: Path, rel_path: str) -> Tuple[int, int]:
    snapshot_file = _snapshot_file(task_id, rel_path)

    previous_lines: List[str] = []
    if snapshot_file.exists():
        previous_lines = snapshot_file.read_text(encoding="utf-8", errors="ignore").splitlines()

    current_lines: List[str] = []
    file_exists = abs_path.exists()
    if file_exists:
        current_lines = abs_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    added = removed = 0
    for line in difflib.ndiff(previous_lines, current_lines):
        if line.startswith("+ "):
            added += 1
        elif line.startswith("- "):
            removed += 1

    if file_exists:
        snapshot_file.parent.mkdir(parents=True, exist_ok=True)
        snapshot_file.write_text(
            "\n".join(current_lines),
            encoding="utf-8",
        )
    elif snapshot_file.exists():
        snapshot_file.unlink()

    return added, removed


def _snapshot_file(task_id: str, rel_path: str) -> Path:
    safe_parts = [part for part in Path(rel_path).parts if part not in ("", ".", "..")] 
    snapshot_root = _SNAPSHOT_ROOT / task_id / "snapshot"
    return (snapshot_root / Path(*safe_parts)).resolve()


def _append_diff_snapshot(snapshot: DiffSnapshot) -> None:
    DIFFS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DIFFS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(snapshot.to_dict(), ensure_ascii=False) + "\n")


def _unique(values: Sequence[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


# -- Task panel and drawer --------------------------------------------------


STATUS_ORDER = [
    "all",
    "open",
    "merged",
    "closed",
    "cancelled",
    "failed",
    "deleted",
]


@dataclass(slots=True)
class _TaskRowData:
    task: Task
    matches_filter: bool = True


class _StatusPill(QLabel):
    """High-contrast badge representing a task status."""

    _PILL_STYLES = {
        "open": ("#1b8a5a", "#ffffff"),
        "merged": ("#6f42c1", "#ffffff"),
        "closed": ("#c0392b", "#ffffff"),
        "cancelled": ("#475061", "#ffffff"),
    }

    _TEXT_STYLES = {
        "failed": "#ff6b6b",
        "deleted": "#96a3bb",
    }

    def __init__(self, status: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        status_key = status.lower()
        font = QFont("Segoe UI", 9)
        font.setBold(True)
        self.setFont(font)
        if status_key in self._PILL_STYLES:
            bg, fg = self._PILL_STYLES[status_key]
            self.setText(status.capitalize())
            self.setStyleSheet(
                (
                    "QLabel{{padding:2px 8px;border-radius:8px;font-weight:600;"
                    "background:{bg};color:{fg};border:1px solid #0b1524;}}"
                ).format(bg=bg, fg=fg)
            )
        else:
            color = self._TEXT_STYLES.get(status_key, "#e9f3ff")
            self.setText(status.capitalize())
            self.setStyleSheet(
                (
                    "QLabel{{padding:0px;font-weight:600;"
                    "color:{color};background:transparent;}}"
                ).format(color=color)
            )


class _TaskRowWidget(QWidget):
    """Widget rendered inside the list view for each task."""

    def __init__(self, task: Task, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.task = task
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        self.pill = _StatusPill(task.status, self)
        layout.addWidget(self.pill)

        self.title = QLabel(task.title, self)
        self.title.setStyleSheet("color:#e9f3ff;font:600 10pt 'Segoe UI';")
        self.title.setWordWrap(True)
        layout.addWidget(self.title, 1)

        diff_text = _format_diff(task)
        self.diff = QLabel(diff_text, self)
        self.diff.setStyleSheet("color:#bcd5ff;font:500 9pt 'Segoe UI';")
        layout.addWidget(self.diff)

        ts_label = QLabel(_format_timestamp(task.updated_ts), self)
        ts_label.setStyleSheet("color:#8ea4c9;font:500 9pt 'Segoe UI';")
        layout.addWidget(ts_label)

        self.setAutoFillBackground(True)
        palette = self.palette()
        bg = QColor("#0c1320")
        palette.setColor(QPalette.Window, bg)
        self.setPalette(palette)


def _format_diff(task: Task) -> str:
    added = task.diffs.added if task.diffs else 0
    removed = task.diffs.removed if task.diffs else 0
    return f"+{added} \u2212{removed}"


def _format_timestamp(ts: float) -> str:
    try:
        dt_obj = datetime.fromtimestamp(float(ts))
    except (TypeError, ValueError, OSError):
        return "--"
    return dt_obj.strftime("%Y-%m-%d %H:%M")


class TaskPanel(QDockWidget):
    """Dockable Tasks panel shared by Terminal and Virtual Desktop."""

    task_selected = Signal(str)
    new_taskRequested = Signal(str)
    status_changed = Signal(str, str)
    load_conversationRequested = Signal(str, str)

    def __init__(
        self,
        dataset_path: str | Path | None = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__("Tasks", parent)
        self.setObjectName("TaskPanelDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.dataset_path = Path(dataset_path) if dataset_path else TASKS_FILE
        self._dataset_root = self.dataset_path.parent
        self._tasks: List[_TaskRowData] = []
        self._selected_task: Optional[Task] = None
        self._log_placeholder = "No run log entries yet."
        self._active_conversation_id: Optional[str] = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        container = QWidget(self)
        container.setObjectName("TaskPanelContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(8)
        self.filter_combo = QComboBox(container)
        self.filter_combo.addItems([status.capitalize() for status in STATUS_ORDER])
        self.filter_combo.currentIndexChanged.connect(self._apply_filters)
        self.filter_combo.setStyleSheet(
            "QComboBox{background:#0a111e;color:#eaf2ff;border:1px solid #1d2b3c;"
            "border-radius:6px;padding:4px 8px;}"
            "QComboBox QAbstractItemView{background:#0b1624;color:#eaf2ff;}"
        )
        header.addWidget(self.filter_combo)

        self.search_edit = QLineEdit(container)
        self.search_edit.setPlaceholderText("Search tasks…")
        self.search_edit.textChanged.connect(self._apply_filters)
        self.search_edit.setStyleSheet(
            "QLineEdit{background:#0b1624;color:#e9f3ff;border:1px solid #203040;"
            "border-radius:6px;padding:6px 10px;font:10pt 'Segoe UI';}"
            "QLineEdit:focus{border:1px solid #2f72ff;}"
        )
        header.addWidget(self.search_edit, 1)

        layout.addLayout(header)

        self.list = QListWidget(container)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.itemSelectionChanged.connect(self._on_item_selected)
        self.list.setUniformItemSizes(False)
        self.list.setSpacing(4)
        self.list.setStyleSheet(
            "QListWidget{background:#0c1320;color:#e9f3ff;border:1px solid #1f2b3a;"
            "border-radius:8px;padding:4px;}"
            "QListWidget::item{margin:2px;padding:2px;border-radius:6px;}"
            "QListWidget::item:selected{background:#1f3a5b;}"
        )
        layout.addWidget(self.list, 1)

        self.detail = QFrame(container)
        self.detail.setFrameShape(QFrame.StyledPanel)
        self.detail.setObjectName("TaskDetailPopover")
        self.detail.setStyleSheet(
            "QFrame#TaskDetailPopover{background:#0b1624;border:1px solid #25405f;"
            "border-radius:10px;}"
        )
        detail_layout = QVBoxLayout(self.detail)
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(8)

        self.detail_title = QLabel("Select a task to view details", self.detail)
        self.detail_title.setStyleSheet("color:#eaf2ff;font:600 11pt 'Segoe UI';")
        self.detail_title.setWordWrap(True)
        detail_layout.addWidget(self.detail_title)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        status_label = QLabel("Status:", self.detail)
        status_label.setStyleSheet("color:#bcd5ff;font:500 9pt 'Segoe UI';")
        status_row.addWidget(status_label)

        self.status_combo = QComboBox(self.detail)
        for status in STATUS_ORDER[1:]:
            self.status_combo.addItem(status.capitalize(), status)
        self.status_combo.setStyleSheet(
            "QComboBox{background:#0a111e;color:#eaf2ff;border:1px solid #1d2b3c;"
            "border-radius:6px;padding:4px 8px;}"
            "QComboBox QAbstractItemView{background:#0b1624;color:#eaf2ff;}"
        )
        status_row.addWidget(self.status_combo, 1)

        self.status_apply = QPushButton("Update", self.detail)
        self.status_apply.clicked.connect(self._emit_status_change)
        self.status_apply.setStyleSheet(
            "QPushButton{background:#1E5AFF;color:#ffffff;border-radius:6px;"
            "padding:6px 12px;border:1px solid #1b3b73;font-weight:600;}"
            "QPushButton:hover{background:#2f72ff;}"
        )
        status_row.addWidget(self.status_apply)
        detail_layout.addLayout(status_row)

        self.detail_diff = QLabel("+0 \u22120", self.detail)
        self.detail_diff.setStyleSheet("color:#bcd5ff;font:500 9pt 'Segoe UI';")
        detail_layout.addWidget(self.detail_diff)

        self.detail_timestamps = QLabel("--", self.detail)
        self.detail_timestamps.setStyleSheet("color:#8ea4c9;font:500 9pt 'Segoe UI';")
        self.detail_timestamps.setWordWrap(True)
        detail_layout.addWidget(self.detail_timestamps)

        self.detail_labels = QLabel("", self.detail)
        self.detail_labels.setStyleSheet("color:#8ea4c9;font:500 9pt 'Segoe UI';")
        self.detail_labels.setWordWrap(True)
        detail_layout.addWidget(self.detail_labels)

        self.detail_log_label = QLabel("Run log", self.detail)
        self.detail_log_label.setStyleSheet("color:#bcd5ff;font:600 9pt 'Segoe UI';")
        detail_layout.addWidget(self.detail_log_label)

        self.detail_log = QPlainTextEdit(self.detail)
        self.detail_log.setReadOnly(True)
        self.detail_log.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.detail_log.setFont(QFont("Consolas", 9))
        self.detail_log.setStyleSheet(
            "QPlainTextEdit{background:#07101c;color:#e9f3ff;border:1px solid #203040;"
            "border-radius:6px;padding:8px;}"
        )
        self.detail_log.setFixedHeight(160)
        self.detail_log.setPlainText(self._log_placeholder)
        detail_layout.addWidget(self.detail_log)

        self.load_conversation_btn = QPushButton("Load Conversation", self.detail)
        self.load_conversation_btn.setEnabled(False)
        self.load_conversation_btn.setStyleSheet(
            "QPushButton{background:#1E5AFF;color:#ffffff;border-radius:6px;"
            "padding:6px 12px;border:1px solid #1b3b73;font-weight:600;}"
            "QPushButton:hover{background:#2f72ff;}"
            "QPushButton:disabled{background:#1b2c44;color:#6c7a96;border:1px solid #1b2c44;}"
        )
        self.load_conversation_btn.clicked.connect(self._emit_load_conversation)
        detail_layout.addWidget(self.load_conversation_btn, 0, Qt.AlignLeft)

        layout.addWidget(self.detail)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        self.new_task_input = QLineEdit(container)
        self.new_task_input.setPlaceholderText("Create new task…")
        self.new_task_input.returnPressed.connect(self._on_new_task_requested)
        self.new_task_input.setStyleSheet(
            "QLineEdit{background:#0b1624;color:#e9f3ff;border:1px solid #203040;"
            "border-radius:6px;padding:6px 10px;font:10pt 'Segoe UI';}"
            "QLineEdit:focus{border:1px solid #2f72ff;}"
        )
        footer.addWidget(self.new_task_input, 1)
        footer.addItem(QSpacerItem(12, 1, QSizePolicy.Fixed, QSizePolicy.Minimum))
        layout.addLayout(footer)

        container.setLayout(layout)
        self.setWidget(container)

        apply_palette(container)
        apply_palette(self.list)
        apply_palette(self.detail)
        apply_palette(self.new_task_input)
        apply_palette(self.search_edit)

    def refresh(self) -> None:
        if not self.dataset_path.exists():
            self._tasks = []
            self._apply_filters()
            return
        records: List[Task] = []
        with self.dataset_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    records.append(Task.from_dict(payload))
                except json.JSONDecodeError:
                    continue
        self.set_tasks(records)

    def set_tasks(self, tasks: Iterable[Task]) -> None:
        self._tasks = [_TaskRowData(task=task) for task in tasks]
        self._apply_filters()

    def update_task(self, task: Task) -> None:
        for row in self._tasks:
            if row.task.id == task.id:
                row.task = task
                break
        else:
            self._tasks.append(_TaskRowData(task=task))
        self._apply_filters(preserve_selection=True)

    def _apply_filters(self, preserve_selection: bool = False) -> None:
        search_text = self.search_edit.text().strip().lower()
        status_filter = STATUS_ORDER[self.filter_combo.currentIndex()]
        selected_id = self._selected_task.id if (preserve_selection and self._selected_task) else None

        self.list.blockSignals(True)
        self.list.clear()
        matched_task: Optional[Task] = None

        for row in self._tasks:
            task = row.task
            matches_status = status_filter == "all" or task.status.lower() == status_filter
            matches_search = not search_text or (
                search_text in task.title.lower()
                or search_text in task.id.lower()
                or any(search_text in label.lower() for label in task.labels)
            )
            row.matches_filter = matches_status and matches_search
            if not row.matches_filter:
                continue
            item = QListWidgetItem(self.list)
            item.setData(Qt.UserRole, task.id)
            widget = _TaskRowWidget(task, self.list)
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)
            if selected_id and task.id == selected_id:
                item.setSelected(True)
                matched_task = task

        self.list.blockSignals(False)
        if not preserve_selection or not matched_task:
            self._selected_task = None
            self.detail_title.setText("Select a task to view details")
            self.status_combo.blockSignals(True)
            self.status_combo.setCurrentIndex(0)
            self.status_combo.blockSignals(False)
            self.detail_diff.setText("+0 \u22120")
            self.detail_timestamps.setText("--")
            self.detail_labels.setText("")
            self._update_log_view(None)
            self._update_conversation_button(None)
        else:
            self._selected_task = matched_task
            self._populate_detail(matched_task)

    def _on_item_selected(self) -> None:
        items = self.list.selectedItems()
        if not items:
            self._selected_task = None
            self._apply_filters()
            return
        task_id = items[0].data(Qt.UserRole)
        for row in self._tasks:
            if row.task.id == task_id:
                self._selected_task = row.task
                self._populate_detail(row.task)
                self.task_selected.emit(row.task.id)
                break

    def _populate_detail(self, task: Task) -> None:
        self.detail_title.setText(task.title)
        status_index = self.status_combo.findData(task.status)
        self.status_combo.blockSignals(True)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
        else:
            self.status_combo.setCurrentIndex(0)
        self.status_combo.blockSignals(False)
        self.detail_diff.setText(_format_diff(task))
        created = _format_timestamp(task.created_ts)
        updated = _format_timestamp(task.updated_ts)
        self.detail_timestamps.setText(f"Created: {created}\nUpdated: {updated}")
        if task.labels:
            labels = ", ".join(task.labels)
            self.detail_labels.setText(f"Labels: {labels}")
        else:
            self.detail_labels.setText("")
        self._update_log_view(task)
        self._update_conversation_button(task)

    def _emit_status_change(self) -> None:
        if not self._selected_task:
            return
        status = self.status_combo.currentData()
        if not status or status == self._selected_task.status:
            return
        self.status_changed.emit(self._selected_task.id, status)

    def _on_new_task_requested(self) -> None:
        text = self.new_task_input.text().strip()
        if not text:
            return
        self.new_taskRequested.emit(text)
        self.new_task_input.clear()

    def _update_log_view(self, task: Optional[Task]) -> None:
        if task is None:
            self.detail_log.setPlainText(self._log_placeholder)
            return
        lines = load_run_log_tail(task, self._dataset_root, max_lines=200)
        self.detail_log.setPlainText("\n".join(lines) if lines else self._log_placeholder)
        scrollbar = self.detail_log.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def _update_conversation_button(self, task: Optional[Task]) -> None:
        identifier: Optional[str] = None
        if task is not None:
            cid = (task.codex_conversation_id or "").strip()
            identifier = cid or (task.session_id or "").strip()
        self._active_conversation_id = identifier or None
        if identifier:
            self.load_conversation_btn.setEnabled(True)
            self.load_conversation_btn.setToolTip("Load the linked Codex transcript into the chat window.")
        else:
            self.load_conversation_btn.setEnabled(False)
            self.load_conversation_btn.setToolTip("No linked Codex conversation for this task.")

    def _emit_load_conversation(self) -> None:
        if not self._selected_task or not self._active_conversation_id:
            return
        self.load_conversationRequested.emit(self._selected_task.id, self._active_conversation_id)


def apply_palette(widget: QWidget) -> None:
    """Apply the high-contrast palette to the given widget."""

    palette = widget.palette()
    bg = QColor("#0c1320")
    fg = QColor("#e9f3ff")
    for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        palette.setColor(group, QPalette.Window, bg)
        palette.setColor(group, QPalette.WindowText, fg)
        palette.setColor(group, QPalette.Base, QColor("#0b1624"))
        palette.setColor(group, QPalette.Text, fg)
        palette.setColor(group, QPalette.Button, QColor("#1E5AFF"))
        palette.setColor(group, QPalette.ButtonText, QColor("#ffffff"))
        palette.setColor(group, QPalette.Highlight, QColor("#1f3a5b"))
        palette.setColor(group, QPalette.HighlightedText, QColor("#ffffff"))
    widget.setPalette(palette)


class TaskDrawer(QFrame):
    """Right-aligned container that hosts the shared :class:`TaskPanel` UI."""

    def __init__(
        self,
        session_id: str,
        dataset_path: Optional[Path] = None,
        source: str = "terminal",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("TaskDrawer")
        self.setFocusPolicy(Qt.NoFocus)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setStyleSheet(
            "QFrame#TaskDrawer{background:#0a111e;border-left:1px solid #1d2b3c;}"
        )

        self._session_id = session_id or "terminal"
        self._source = source or "terminal"
        self._dataset_path = Path(dataset_path) if dataset_path else TASKS_FILE

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.panel = TaskPanel(self._dataset_path, self)
        self.panel.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.panel.setTitleBarWidget(QWidget(self.panel))
        layout.addWidget(self.panel)

        width_hint = max(360, self.panel.sizeHint().width())
        self.setFixedWidth(width_hint)

        self.panel.new_taskRequested.connect(self._create_task)
        self.panel.status_changed.connect(self._apply_status_change)
        self.panel.load_conversationRequested.connect(self._publish_conversation_request)

        self._subscriptions: List[Subscription] = [
            subscribe("task.created", self._on_task_payload),
            subscribe("task.updated", self._on_task_payload),
        ]
        self.destroyed.connect(lambda *_: self._teardown())

    def refresh(self) -> None:
        self.panel.refresh()

    def _teardown(self) -> None:
        for handle in self._subscriptions:
            try:
                handle.unsubscribe()
            except Exception:  # pragma: no cover - defensive cleanup
                logging.getLogger(__name__).exception(
                    "Failed to unsubscribe task drawer handle"
                )
        self._subscriptions.clear()

    def _create_task(self, title: str) -> None:
        title = (title or "").strip()
        if not title:
            return
        now = datetime.now(UTC).timestamp()
        task_id = self._generate_task_id()
        task = Task(
            id=task_id,
            title=title,
            status="open",
            created_ts=now,
            updated_ts=now,
            session_id=self._session_id,
            source=self._source,
            codex_conversation_id=self._session_id,
        )
        try:
            append_task(task)
            append_event(
                TaskEvent(
                    ts=now,
                    task_id=task_id,
                    event="created",
                    by=self._source,
                )
            )
        except Exception:
            logging.getLogger(__name__).exception(
                "Failed to persist new task: %s", task_id
            )
            return

        publish("task.created", task.to_dict())
        publish("task.updated", task.to_dict())
        self.panel.update_task(task)

    def _publish_conversation_request(self, task_id: str, conversation_id: str) -> None:
        conv = (conversation_id or "").strip()
        if not conv:
            return
        payload = {
            "id": task_id,
            "conversation_id": conv,
            "session_id": self._session_id,
            "source": self._source,
        }
        try:
            publish("task.conversation", payload)
        except Exception:  # pragma: no cover - defensive guard
            logging.getLogger(__name__).exception(
                "Failed to publish task conversation request"
            )

    def _apply_status_change(self, task_id: str, status: str) -> None:
        if not task_id or not status:
            return
        now = datetime.now(UTC).timestamp()
        try:
            updated = update_task(task_id, status=status, updated_ts=now)
            append_event(
                TaskEvent(
                    ts=now,
                    task_id=task_id,
                    event="status",
                    by=self._source,
                    to=status,
                )
            )
        except ValueError:
            logging.getLogger(__name__).warning(
                "Task %s not found when applying status", task_id
            )
            self.panel.refresh()
            return
        except Exception:
            logging.getLogger(__name__).exception(
                "Failed to update task status for %s", task_id
            )
            return

        publish("task.status", {"id": updated.id, "status": updated.status})
        publish("task.updated", updated.to_dict())
        self.panel.update_task(updated)

    def _on_task_payload(self, payload: dict) -> None:
        if not isinstance(payload, dict):
            return
        try:
            task = Task.from_dict(payload)
        except Exception:
            logging.getLogger(__name__).debug(
                "Skipping malformed task payload: %r", payload
            )
            self.panel.refresh()
            return
        self.panel.update_task(task)

    def _generate_task_id(self) -> str:
        stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"tsk_{stamp}_{uuid.uuid4().hex[:6]}"


# ============================================================================
# Error Console (Inlined from Dev_Logic/error_console.py)
# ============================================================================
"""Dockable error log surface and stderr redirector."""


class ErrorConsole(QDockWidget):
    """Dockable console to display and persist error messages."""

    def __init__(
        self,
        errors_dir: Path | str = "errors",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__("Errors", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self._text = QTextEdit(self)
        self._text.setReadOnly(True)
        self.setWidget(self._text)
        self.errors_dir = Path(errors_dir)
        self.errors_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str) -> None:
        """Append message to console and persist to timestamped file."""

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._text.append(f"[{ts}] {message}")
        fname = self.errors_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        with fname.open("a", encoding="utf-8") as fh:
            if message.endswith("\n"):
                fh.write(message)
            else:
                fh.write(f"{message}\n")
        self.show()
        self.raise_()


class StderrRedirector(io.TextIOBase):
    """File-like object that sends writes to the :class:`ErrorConsole`."""

    def __init__(self, console: ErrorConsole, original: io.TextIOBase) -> None:
        self.console = console
        self.original = original
        self._buffer = ""

    def write(self, text: str) -> int:  # type: ignore[override]
        self.original.write(text)
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                self.console.log(line)
        return len(text)

    def flush(self) -> None:  # type: ignore[override]
        if self._buffer.strip():
            self.console.log(self._buffer)
            self._buffer = ""
        self.original.flush()


def log_exception(console: ErrorConsole, exc_type, exc, tb) -> None:
    """Format and log an exception using the provided console."""

    text = "".join(traceback.format_exception(exc_type, exc, tb))
    console.log(text)


class DatasetIngestWorker(QObject):
    """Background worker that performs Hippocampus ingest operations."""

    progress = Signal(str)
    finished = Signal(list)
    failed = Signal(str)

    def __init__(
        self,
        client: HippocampusClient,
        paths: Sequence[Path],
        tags: Sequence[str],
        note: str,
    ) -> None:
        super().__init__()
        self._client = client
        self._paths = list(paths)
        self._tags = list(tags)
        self._note = note

    @Slot()
    def run(self) -> None:
        try:
            results = self._client.ingest_assets(
                self._paths,
                self._tags,
                self._note,
                progress=lambda msg: self.progress.emit(str(msg)),
            )
        except Exception:
            self.failed.emit(traceback.format_exc())
            return
        self.finished.emit(results)


class DatasetManagerDock(QDockWidget):
    """Qt dock widget exposing the Hippocampus dataset ingestion flow."""

    def __init__(
        self,
        chat_card: Optional["ChatCard"],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__("Dataset Manager", parent)
        self.setObjectName("DatasetManagerDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.toggleViewAction().setText("Dataset Manager")

        self._chat: Optional["ChatCard"] = None
        self._selected: List[Path] = []
        self._thread: Optional[QThread] = None
        self._worker: Optional[DatasetIngestWorker] = None

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        intro = QLabel(
            "Select files or folders to ingest into Hippocampus. "
            "Entries trigger OCR, embedding, and graph registration.",
            container,
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        tag_row = QHBoxLayout()
        tag_row.setSpacing(6)
        self.tag_input = QLineEdit(container)
        self.tag_input.setPlaceholderText("Comma-separated tags (e.g. design,log)")
        tag_row.addWidget(self.tag_input, 1)
        self.note_input = QLineEdit(container)
        self.note_input.setPlaceholderText("Operator note / rationale (optional)")
        tag_row.addWidget(self.note_input, 1)
        layout.addLayout(tag_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self.btn_add_files = QPushButton("Add Files…", container)
        self.btn_add_files.clicked.connect(self._add_files)
        btn_row.addWidget(self.btn_add_files)
        self.btn_add_dir = QPushButton("Add Directory…", container)
        self.btn_add_dir.clicked.connect(self._add_directory)
        btn_row.addWidget(self.btn_add_dir)
        self.btn_clear = QPushButton("Clear Selection", container)
        self.btn_clear.clicked.connect(self._clear_selection)
        btn_row.addWidget(self.btn_clear)
        layout.addLayout(btn_row)

        self.path_list = QListWidget(container)
        self.path_list.setSelectionMode(QAbstractItemView.NoSelection)
        layout.addWidget(self.path_list, 1)

        self.ingest_button = QPushButton("Ingest Selection", container)
        self.ingest_button.clicked.connect(self._start_ingest)
        layout.addWidget(self.ingest_button)

        self.log = QPlainTextEdit(container)
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(160)
        layout.addWidget(self.log, 1)

        self.setWidget(container)
        self.set_chat_card(chat_card)

    # ------------------------------------------------------------------
    def set_chat_card(self, chat_card: Optional["ChatCard"]) -> None:
        """Attach the active chat card so we can reach Hippocampus services."""

        self._chat = chat_card
        self._append_log(
            "Hippocampus client ready." if chat_card else "No chat context bound."
        )

    def _hippocampus(self) -> Optional[HippocampusClient]:
        if self._chat and hasattr(self._chat, "hippocampus_client"):
            return self._chat.hippocampus_client()
        return None

    def _add_files(self) -> None:
        base = self._default_directory()
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select files",
            str(base),
        )
        self._add_paths(files)

    def _add_directory(self) -> None:
        base = self._default_directory()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select directory",
            str(base),
        )
        if directory:
            self._add_paths([directory])

    def _add_paths(self, raw_paths: Sequence[str]) -> None:
        added = 0
        for raw in raw_paths:
            candidate = Path(raw).expanduser()
            if candidate in self._selected:
                continue
            if candidate.exists():
                self._selected.append(candidate)
                added += 1
        if added:
            self._selected.sort(key=lambda p: p.as_posix())
            self._refresh_list()
            self._append_log(f"Added {added} path(s) to ingest queue.")

    def _clear_selection(self) -> None:
        if not self._selected:
            return
        self._selected.clear()
        self._refresh_list()
        self._append_log("Selection cleared.")

    def _refresh_list(self) -> None:
        self.path_list.clear()
        for path in self._selected:
            item = QListWidgetItem(path.as_posix(), self.path_list)
            item.setToolTip(path.as_posix())

    def _start_ingest(self) -> None:
        client = self._hippocampus()
        if client is None:
            QMessageBox.warning(
                self,
                "Hippocampus unavailable",
                "Chat context is not ready; reopen after chat initialises.",
            )
            return
        if not self._selected:
            QMessageBox.information(
                self,
                "No paths selected",
                "Add at least one file or directory before ingesting.",
            )
            return
        tags = [tag.strip() for tag in self.tag_input.text().split(",") if tag.strip()]
        note = self.note_input.text().strip()
        self._set_busy(True)
        self._append_log(
            f"Starting ingest for {len(self._selected)} path(s) with tags {tags}."
        )
        self._thread = QThread(self)
        self._worker = DatasetIngestWorker(client, list(self._selected), tags, note)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._append_log)
        self._worker.finished.connect(self._on_ingest_finished)
        self._worker.failed.connect(self._on_ingest_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.failed.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.start()

    def _on_ingest_finished(self, records: List[HippocampusNodeRecord]) -> None:
        self._set_busy(False)
        if not records:
            self._append_log("Ingest completed with no nodes registered.")
            return
        self._append_log(f"Ingest complete: {len(records)} node(s) registered.")
        for record in records:
            summary = record.summary
            if len(summary) > 160:
                summary = summary[:157] + "…"
            self._append_log(
                f"• {record.label} → {summary} [tags: {', '.join(record.tags)}]"
            )

    def _on_ingest_failed(self, error: str) -> None:
        self._set_busy(False)
        self._append_log(f"Ingest failed:\n{error}")
        QMessageBox.critical(
            self,
            "Hippocampus ingest failed",
            "Review the dataset log for full details.",
        )

    def _cleanup_thread(self) -> None:
        if self._thread:
            self._thread.deleteLater()
            self._thread = None
        self._worker = None

    def _set_busy(self, busy: bool) -> None:
        self.btn_add_files.setEnabled(not busy)
        self.btn_add_dir.setEnabled(not busy)
        self.btn_clear.setEnabled(not busy)
        self.ingest_button.setEnabled(not busy)

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.appendPlainText(f"[{timestamp}] {message}")
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _default_directory(self) -> Path:
        if self._chat and hasattr(self._chat, "data_root"):
            try:
                return Path(getattr(self._chat, "data_root")).expanduser()
            except Exception:
                return agent_data_dir()
        return agent_data_dir()

# ============================================================================
# Virtual Desktop Dock (new consolidated UI shell)
# ============================================================================


class VirtualDesktopDock(QDockWidget):
    """Dockable Virtual Desktop with consoles, Dev Space, and OCR overlays."""

    def __init__(
        self,
        chat_card: Optional["ChatCard"],
        parent: Optional[QWidget] = None,
        *,
        dataset_root: Optional[Path] = None,
    ) -> None:
        super().__init__("Virtual Desktop", parent)
        self.setObjectName("VirtualDesktopDock")
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea
            | Qt.RightDockWidgetArea
            | Qt.BottomDockWidgetArea
        )
        self.toggleViewAction().setText("Virtual Desktop")

        self._logger = logging.getLogger(f"{VD_LOGGER_NAME}.virtual_desktop")
        self._chat: Optional["ChatCard"] = None
        self._dataset_root = _dataset_root(dataset_root)
        self._tasks: Dict[str, Task] = {}
        self._run_logs: Dict[str, List[str]] = {}
        self._latest_diff: Optional[Dict[str, Any]] = None
        self._log_buffer: Deque[str] = deque(maxlen=400)
        self._metrics_snapshot: Dict[str, Any] = {}
        self._dataset_snapshot: Dict[str, int] = {}
        self._ocr_history: List[Dict[str, str]] = []
        self._subscriptions: List[Tuple[str, Subscription]] = []
        self._console_view: Optional[QPlainTextEdit] = None
        self._devspace_tabs: Optional[QTabWidget] = None
        self._stats_view: Optional[QTextBrowser] = None
        self._dev_logs_view: Optional[QPlainTextEdit] = None
        self._data_view: Optional[QTextBrowser] = None
        self._code_view: Optional[QTextBrowser] = None
        self._graph_view: Optional[QPlainTextEdit] = None
        self._ocr_path: Optional[QLineEdit] = None
        self._ocr_output: Optional[QTextBrowser] = None
        self._ocr_history_list: Optional[QListWidget] = None
        self._ocr_status: Optional[QLabel] = None
        self._last_update_ts: Optional[float] = None

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        intro = QLabel(
            "Virtual Desktop components load on demand to preserve startup "
            "performance while keeping consoles, Dev Space tabs, and OCR "
            "overlays within reach.",
            container,
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self._main_tabs = QTabWidget(container)
        self._console_tab = QWidget(self._main_tabs)
        self._devspace_tab = QWidget(self._main_tabs)
        self._ocr_tab = QWidget(self._main_tabs)
        self._main_tabs.addTab(self._console_tab, "Consoles")
        self._main_tabs.addTab(self._devspace_tab, "Dev Space")
        self._main_tabs.addTab(self._ocr_tab, "OCR Overlay")
        self._main_tabs.currentChanged.connect(self._ensure_tab_initialized)
        layout.addWidget(self._main_tabs, 1)

        self._status_label = QLabel("Awaiting event stream…", container)
        layout.addWidget(self._status_label)

        self.setWidget(container)
        self.visibilityChanged.connect(self._on_visibility_changed)

        self.set_chat_card(chat_card)
        self._install_subscriptions()
        self._refresh_dataset_snapshot()

    # ------------------------------------------------------------------
    def set_chat_card(self, chat_card: Optional["ChatCard"]) -> None:
        """Store the active chat card for future integrations."""

        self._chat = chat_card

    # ------------------------------------------------------------------
    def _install_subscriptions(self) -> None:
        topics = (
            "task.created",
            "task.updated",
            "task.status",
            "task.deleted",
            "task.diff",
            "system.metrics",
        )
        for topic in topics:
            try:
                handle = subscribe(topic, self._make_callback(topic))
            except Exception:
                self._logger.exception("Failed to subscribe to %s", topic)
                continue
            self._subscriptions.append((topic, handle))
        self.destroyed.connect(lambda *_: self._teardown())

    # ------------------------------------------------------------------
    def _on_visibility_changed(self, visible: bool) -> None:
        if visible:
            self._ensure_tab_initialized(self._main_tabs.currentIndex())

    # ------------------------------------------------------------------
    def _ensure_tab_initialized(self, index: int) -> None:
        widget = self._main_tabs.widget(index)
        if widget is self._console_tab:
            self._ensure_console_panel()
        elif widget is self._devspace_tab:
            self._ensure_devspace_panel()
        elif widget is self._ocr_tab:
            self._ensure_ocr_panel()

    # ------------------------------------------------------------------
    def _ensure_console_panel(self) -> None:
        if self._console_view is not None:
            return
        layout = QVBoxLayout(self._console_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._console_view = QPlainTextEdit(self._console_tab)
        self._console_view.setObjectName("VirtualDesktopConsoleView")
        self._console_view.setReadOnly(True)
        layout.addWidget(self._console_view, 1)

        refresh_btn = QPushButton("Refresh from run logs", self._console_tab)
        refresh_btn.clicked.connect(self._refresh_console_from_logs)
        layout.addWidget(refresh_btn, 0, Qt.AlignRight)

        self._update_console_view()

    # ------------------------------------------------------------------
    def _ensure_devspace_panel(self) -> None:
        if self._devspace_tabs is not None:
            return
        layout = QVBoxLayout(self._devspace_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._devspace_tabs = QTabWidget(self._devspace_tab)
        layout.addWidget(self._devspace_tabs, 1)

        stats_widget = QWidget(self._devspace_tabs)
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(4)
        self._stats_view = QTextBrowser(stats_widget)
        self._stats_view.setObjectName("VirtualDesktopStats")
        self._stats_view.setOpenExternalLinks(False)
        stats_layout.addWidget(self._stats_view, 1)
        self._devspace_tabs.addTab(stats_widget, "Stats")

        logs_widget = QWidget(self._devspace_tabs)
        logs_layout = QVBoxLayout(logs_widget)
        logs_layout.setContentsMargins(0, 0, 0, 0)
        logs_layout.setSpacing(4)
        self._dev_logs_view = QPlainTextEdit(logs_widget)
        self._dev_logs_view.setObjectName("VirtualDesktopLogs")
        self._dev_logs_view.setReadOnly(True)
        logs_layout.addWidget(self._dev_logs_view, 1)
        self._devspace_tabs.addTab(logs_widget, "Logs")

        data_widget = QWidget(self._devspace_tabs)
        data_layout = QVBoxLayout(data_widget)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(4)
        refresh_btn = QPushButton("Refresh dataset snapshot", data_widget)
        refresh_btn.clicked.connect(self._refresh_dataset_snapshot)
        data_layout.addWidget(refresh_btn, 0, Qt.AlignRight)
        self._data_view = QTextBrowser(data_widget)
        self._data_view.setObjectName("VirtualDesktopData")
        data_layout.addWidget(self._data_view, 1)
        self._devspace_tabs.addTab(data_widget, "Data")

        code_widget = QWidget(self._devspace_tabs)
        code_layout = QVBoxLayout(code_widget)
        code_layout.setContentsMargins(0, 0, 0, 0)
        code_layout.setSpacing(4)
        self._code_view = QTextBrowser(code_widget)
        self._code_view.setObjectName("VirtualDesktopCode")
        mono = QFont(self._code_view.font())
        mono.setStyleHint(QFont.TypeWriter)
        self._code_view.setFont(mono)
        code_layout.addWidget(self._code_view, 1)
        self._devspace_tabs.addTab(code_widget, "Code")

        graph_widget = QWidget(self._devspace_tabs)
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        graph_layout.setSpacing(4)
        self._graph_view = QPlainTextEdit(graph_widget)
        self._graph_view.setObjectName("VirtualDesktopGraph")
        self._graph_view.setReadOnly(True)
        graph_font = QFont(self._graph_view.font())
        graph_font.setStyleHint(QFont.TypeWriter)
        self._graph_view.setFont(graph_font)
        graph_layout.addWidget(self._graph_view, 1)
        self._devspace_tabs.addTab(graph_widget, "Graph")

        self._update_devspace_views()

    # ------------------------------------------------------------------
    def _ensure_ocr_panel(self) -> None:
        if self._ocr_output is not None:
            return
        layout = QVBoxLayout(self._ocr_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        intro = QLabel(
            "Select a capture to extract OCR Markdown and persist the output "
            "for later review.",
            self._ocr_tab,
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        path_row = QHBoxLayout()
        path_row.setSpacing(6)
        self._ocr_path = QLineEdit(self._ocr_tab)
        self._ocr_path.setPlaceholderText("Image path within the workspace…")
        path_row.addWidget(self._ocr_path, 1)
        browse = QPushButton("Browse…", self._ocr_tab)
        browse.clicked.connect(self._browse_ocr_file)
        path_row.addWidget(browse)
        layout.addLayout(path_row)

        action_row = QHBoxLayout()
        action_row.setSpacing(6)
        run_btn = QPushButton("Run OCR", self._ocr_tab)
        run_btn.clicked.connect(self._trigger_ocr)
        action_row.addWidget(run_btn, 0)
        self._ocr_status = QLabel("", self._ocr_tab)
        self._ocr_status.setWordWrap(True)
        action_row.addWidget(self._ocr_status, 1)
        layout.addLayout(action_row)

        self._ocr_output = QTextBrowser(self._ocr_tab)
        self._ocr_output.setObjectName("VirtualDesktopOCROutput")
        layout.addWidget(self._ocr_output, 2)

        history_label = QLabel("Recent OCR runs", self._ocr_tab)
        layout.addWidget(history_label)
        self._ocr_history_list = QListWidget(self._ocr_tab)
        self._ocr_history_list.setObjectName("VirtualDesktopOCRHistory")
        self._ocr_history_list.itemSelectionChanged.connect(
            self._load_history_item
        )
        layout.addWidget(self._ocr_history_list, 1)

    # ------------------------------------------------------------------
    def _make_callback(self, topic: str) -> Callable[[dict], None]:
        def _callback(payload: dict) -> None:
            snapshot = dict(payload)
            QTimer.singleShot(
                0,
                lambda: self._handle_event(topic, snapshot),
            )

        return _callback

    # ------------------------------------------------------------------
    def _handle_event(self, topic: str, payload: Dict[str, Any]) -> None:
        self._append_log_line(topic, payload)
        if topic in {"task.created", "task.updated"}:
            self._apply_task_payload(payload)
            self._refresh_dataset_snapshot()
        elif topic == "task.status":
            self._apply_task_status(payload)
        elif topic == "task.deleted":
            self._apply_task_deleted(payload)
        elif topic == "task.diff":
            self._apply_diff_payload(payload)
        elif topic == "system.metrics":
            self._metrics_snapshot = dict(payload)
        self._update_run_logs()
        self._refresh_views()

    # ------------------------------------------------------------------
    def _apply_task_payload(self, payload: Mapping[str, Any]) -> None:
        try:
            task = Task.from_dict(dict(payload))
        except Exception:
            self._logger.debug("Invalid task payload: keys=%s", payload.keys())
            return
        self._tasks[task.id] = task

    # ------------------------------------------------------------------
    def _apply_task_status(self, payload: Mapping[str, Any]) -> None:
        task_id = str(payload.get("id") or payload.get("task_id") or "").strip()
        if not task_id:
            return
        status = payload.get("status") or payload.get("to")
        if not status:
            return
        task = self._tasks.get(task_id)
        if task:
            task.status = str(status)
            task.updated_ts = time.time()

    # ------------------------------------------------------------------
    def _apply_task_deleted(self, payload: Mapping[str, Any]) -> None:
        task_id = str(payload.get("id") or payload.get("task_id") or "").strip()
        if not task_id:
            return
        self._tasks.pop(task_id, None)
        self._run_logs.pop(task_id, None)

    # ------------------------------------------------------------------
    def _apply_diff_payload(self, payload: Mapping[str, Any]) -> None:
        self._latest_diff = {
            "added": int(payload.get("added", 0)),
            "removed": int(payload.get("removed", 0)),
            "files": list(payload.get("files", [])),
            "timestamp": time.time(),
        }

    # ------------------------------------------------------------------
    def _append_log_line(self, topic: str, payload: Mapping[str, Any]) -> None:
        when = datetime.now().strftime("%H:%M:%S")
        summary = self._summarise_payload(topic, payload)
        self._log_buffer.append(f"[{when}] {topic}: {summary}")
        self._last_update_ts = time.time()

    # ------------------------------------------------------------------
    def _summarise_payload(self, topic: str, payload: Mapping[str, Any]) -> str:
        if topic.startswith("task"):
            title = str(payload.get("title") or payload.get("id") or "").strip()
            status = payload.get("status") or payload.get("to")
            if status:
                return f"{title} → {status}"
            return title or "(task event)"
        if topic == "system.metrics":
            keys = [key for key in payload.keys() if key != "meta"]
            return f"metrics fields={', '.join(keys) or 'none'}"
        snippet = json.dumps(payload, ensure_ascii=False)
        return snippet[:160]

    # ------------------------------------------------------------------
    def _update_run_logs(self) -> None:
        for task in self._tasks.values():
            tail = load_run_log_tail(task, self._dataset_root, max_lines=80)
            if tail:
                self._run_logs[task.id] = tail

    # ------------------------------------------------------------------
    def _refresh_views(self) -> None:
        self._update_console_view()
        self._update_devspace_views()
        self._refresh_status_text()

    # ------------------------------------------------------------------
    def _update_console_view(self) -> None:
        if not self._console_view:
            return
        text = "\n".join(self._log_buffer)
        self._console_view.setPlainText(text or "Event stream idle.")
        bar = self._console_view.verticalScrollBar()
        if bar:
            bar.setValue(bar.maximum())

    # ------------------------------------------------------------------
    def _update_devspace_views(self) -> None:
        self._update_stats_view()
        self._update_logs_view()
        self._update_data_view()
        self._update_code_view()
        self._update_graph_view()

    # ------------------------------------------------------------------
    def _update_stats_view(self) -> None:
        if not self._stats_view:
            return
        statuses = Counter(task.status for task in self._tasks.values())
        lines = [f"Total tasks: {len(self._tasks)}"]
        if statuses:
            parts = [f"{name}: {count}" for name, count in statuses.items()]
            lines.append("Status mix: " + ", ".join(sorted(parts)))
        if self._metrics_snapshot:
            cpu = self._metrics_snapshot.get("cpu", "?")
            mem = self._metrics_snapshot.get("memory", "?")
            lines.append(f"Metrics • CPU: {cpu} • Memory: {mem}")
        self._stats_view.setPlainText("\n".join(lines))

    # ------------------------------------------------------------------
    def _update_logs_view(self) -> None:
        if not self._dev_logs_view:
            return
        rows: List[str] = []
        tasks = sorted(
            self._tasks.values(), key=lambda item: item.updated_ts, reverse=True
        )
        for task in tasks:
            tail = self._run_logs.get(task.id)
            if not tail:
                continue
            rows.append(f"▶ {task.title} [{task.status}]")
            rows.extend(tail[-12:])
            rows.append("")
        text = "\n".join(rows).strip()
        self._dev_logs_view.setPlainText(text or "No run logs captured yet.")
        bar = self._dev_logs_view.verticalScrollBar()
        if bar:
            bar.setValue(bar.maximum())

    # ------------------------------------------------------------------
    def _update_data_view(self) -> None:
        if not self._data_view:
            return
        if not self._dataset_snapshot:
            self._data_view.setPlainText("No dataset files discovered yet.")
            return
        lines = ["Dataset entries:"]
        for name, count in sorted(self._dataset_snapshot.items()):
            lines.append(f"• {name}: {count}")
        self._data_view.setPlainText("\n".join(lines))

    # ------------------------------------------------------------------
    def _update_code_view(self) -> None:
        if not self._code_view:
            return
        if not self._latest_diff:
            self._code_view.setPlainText("No diffs recorded yet.")
            return
        added = self._latest_diff.get("added", 0)
        removed = self._latest_diff.get("removed", 0)
        files = self._latest_diff.get("files", [])
        when = self._latest_diff.get("timestamp")
        timestamp = "unknown"
        if isinstance(when, float):
            timestamp = datetime.fromtimestamp(when).strftime("%H:%M:%S")
        lines = [
            f"Last diff observed at {timestamp}",
            f"Added lines: {added}",
            f"Removed lines: {removed}",
            "Files:",
        ]
        lines.extend(f"  - {path}" for path in files or ["(none)"])
        self._code_view.setPlainText("\n".join(lines))

    # ------------------------------------------------------------------
    def _update_graph_view(self) -> None:
        if not self._graph_view:
            return
        if not self._tasks:
            self._graph_view.setPlainText("Graph requires at least one task.")
            return
        rows = ["Task lineage graph:"]
        for task in sorted(self._tasks.values(), key=lambda t: t.created_ts):
            parent = task.parent_id or "—"
            rows.append(f"{task.id} ← {parent} :: {task.title}")
        self._graph_view.setPlainText("\n".join(rows))

    # ------------------------------------------------------------------
    def _refresh_console_from_logs(self) -> None:
        if not self._console_view:
            return
        rows: List[str] = []
        for task in sorted(
            self._tasks.values(), key=lambda item: item.updated_ts, reverse=True
        ):
            tail = self._run_logs.get(task.id)
            if not tail:
                continue
            rows.append(f"▶ {task.title} [{task.status}]")
            rows.extend(tail[-10:])
            rows.append("")
        text = "\n".join(rows).strip()
        if text:
            self._console_view.setPlainText(text)
        else:
            self._console_view.setPlainText(
                "No run log output located for tracked tasks."
            )

    # ------------------------------------------------------------------
    def _refresh_dataset_snapshot(self) -> None:
        snapshot: Dict[str, int] = {}
        root = self._dataset_root
        if root.exists():
            for idx, path in enumerate(sorted(root.glob("*.jsonl"))):
                if idx >= 10:
                    break
                try:
                    with path.open("r", encoding="utf-8") as fh:
                        count = sum(1 for line in fh if line.strip())
                except Exception:
                    self._logger.debug("Failed to read dataset file %s", path)
                    continue
                snapshot[path.name] = count
        self._dataset_snapshot = snapshot
        self._update_data_view()
        self._refresh_status_text()

    # ------------------------------------------------------------------
    def _refresh_status_text(self) -> None:
        parts = [f"Tasks: {len(self._tasks)}", f"Events cached: {len(self._log_buffer)}"]
        if self._dataset_snapshot:
            parts.append(f"Datasets tracked: {len(self._dataset_snapshot)}")
        if self._last_update_ts:
            stamp = datetime.fromtimestamp(self._last_update_ts).strftime("%H:%M:%S")
            parts.append(f"Last update {stamp}")
        self._status_label.setText(" • ".join(parts))

    # ------------------------------------------------------------------
    def _browse_ocr_file(self) -> None:
        if not self._ocr_path:
            return
        base = agent_data_dir()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select image for OCR",
            str(base),
        )
        if file_path:
            self._ocr_path.setText(file_path)

    # ------------------------------------------------------------------
    def _trigger_ocr(self) -> None:
        if not self._ocr_path or not self._ocr_output:
            return
        raw_path = self._ocr_path.text().strip()
        if not raw_path:
            self._set_ocr_status("Select an image before running OCR.")
            return
        path = Path(raw_path).expanduser()
        if not path.exists():
            self._set_ocr_status(f"Image not found: {path}")
            return
        result = perform_ocr(path)
        if result.error:
            self._set_ocr_status(f"OCR failed: {result.error}")
            self._ocr_output.setPlainText("")
        else:
            self._set_ocr_status("OCR completed successfully.")
            content = (
                f"## Markdown\n{result.markdown}\n\n## Raw Text\n{result.text}"
            )
            self._ocr_output.setPlainText(content)
            entry = {
                "path": path.as_posix(),
                "markdown": result.markdown,
                "text": result.text,
            }
            self._ocr_history.append(entry)
            self._update_ocr_history()

    # ------------------------------------------------------------------
    def _set_ocr_status(self, message: str) -> None:
        if self._ocr_status:
            self._ocr_status.setText(message)

    # ------------------------------------------------------------------
    def _update_ocr_history(self) -> None:
        if not self._ocr_history_list:
            return
        self._ocr_history_list.blockSignals(True)
        self._ocr_history_list.clear()
        for entry in reversed(self._ocr_history[-20:]):
            item = QListWidgetItem(entry["path"])
            item.setData(Qt.UserRole, entry)
            self._ocr_history_list.addItem(item)
        self._ocr_history_list.blockSignals(False)

    # ------------------------------------------------------------------
    def _load_history_item(self) -> None:
        if not self._ocr_history_list or not self._ocr_output:
            return
        items = self._ocr_history_list.selectedItems()
        if not items:
            return
        entry = items[0].data(Qt.UserRole) or {}
        markdown = entry.get("markdown", "")
        text = entry.get("text", "")
        content = f"## Markdown\n{markdown}\n\n## Raw Text\n{text}"
        self._ocr_output.setPlainText(content)
        if self._ocr_path:
            self._ocr_path.setText(entry.get("path", ""))

    # ------------------------------------------------------------------
    def _teardown(self) -> None:
        for topic, handle in self._subscriptions:
            try:
                handle.unsubscribe()
            except Exception:
                self._logger.debug(
                    "Failed to unsubscribe %s", topic, exc_info=True
                )
        self._subscriptions.clear()


# ============================================================================
# Virtual Desktop Backgrounds (Inlined from Dev_Logic/background)
# ============================================================================
"""Background configuration, rendering layers, and live scripting viewport."""


class BackgroundMode(str, Enum):
    """Supported background layer types."""

    SOLID = "solid"
    STATIC = "image"
    GIF = "gif"
    VIDEO = "video"
    GL = "gl"


class BackgroundFit(str, Enum):
    """Scaling strategies for image-backed backgrounds."""

    FILL = "fill"
    FIT = "fit"
    CENTER = "center"
    TILE = "tile"


@dataclass
class BackgroundConfig:
    """Runtime configuration for a background layer."""

    mode: BackgroundMode = BackgroundMode.SOLID
    source: str = ""
    fit: BackgroundFit = BackgroundFit.FILL
    loop: bool = True
    mute: bool = True
    playback_rate: float = 1.0

    @classmethod
    def from_state(cls, raw: object) -> "BackgroundConfig":
        if isinstance(raw, dict):
            mode = raw.get("mode", BackgroundMode.SOLID)
            source = raw.get("source", "")
            fit = raw.get("fit", BackgroundFit.FILL)
            loop = bool(raw.get("loop", True))
            mute = bool(raw.get("mute", True))
            try:
                playback_rate = float(raw.get("playback_rate", 1.0))
            except Exception:
                playback_rate = 1.0
        elif isinstance(raw, str) and raw:
            mode = BackgroundMode.STATIC
            source = raw
            fit = BackgroundFit.FILL
            loop = True
            mute = True
            playback_rate = 1.0
        else:
            mode = BackgroundMode.SOLID
            source = ""
            fit = BackgroundFit.FILL
            loop = True
            mute = True
            playback_rate = 1.0

        try:
            mode = BackgroundMode(mode)
        except Exception:
            mode = BackgroundMode.SOLID
        try:
            fit = BackgroundFit(fit)
        except Exception:
            fit = BackgroundFit.FILL
        return cls(mode=mode, source=source, fit=fit, loop=loop, mute=mute, playback_rate=playback_rate)

    def to_state(self) -> Dict[str, object]:
        return {
            "mode": self.mode.value,
            "source": self.source,
            "fit": self.fit.value,
            "loop": bool(self.loop),
            "mute": bool(self.mute),
            "playback_rate": float(self.playback_rate),
        }


class BackgroundLayer(QObject):
    """Interface implemented by background layer engines."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas

    def start(self, config: BackgroundConfig) -> None:
        """Activate the background using the provided configuration."""

    def stop(self) -> None:
        """Deactivate the background and release resources."""

    def paint(self, painter: QPainter, rect) -> bool:  # pragma: no cover - thin wrapper
        return False

    def resize(self, size: QSize) -> None:
        """Resize hook used by the canvas when it changes dimensions."""


class BackgroundManager(QObject):
    """Lifecycle coordinator for desktop background layers."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self._factories: Dict[BackgroundMode, Callable[[object], BackgroundLayer]] = {}
        self._instances: Dict[BackgroundMode, BackgroundLayer] = {}
        self._active: Optional[BackgroundLayer] = None
        self._active_mode: Optional[BackgroundMode] = None

    def register(self, mode: BackgroundMode, factory: Callable[[object], BackgroundLayer]) -> None:
        self._factories[mode] = factory

    def apply(self, config: Optional[BackgroundConfig]) -> None:
        if config is None:
            self.clear()
            return
        if self._active and self._active_mode != config.mode:
            self._active.stop()
            self._active = None
            self._active_mode = None
        factory = self._factories.get(config.mode)
        if factory is None:
            self.clear()
            return
        layer = self._instances.get(config.mode)
        if layer is None:
            layer = factory(self.canvas)
            self._instances[config.mode] = layer
        self._active = layer
        self._active_mode = config.mode
        layer.start(config)
        layer.resize(self.canvas.size())
        self.canvas.update()

    def clear(self) -> None:
        if self._active:
            self._active.stop()
        self._active = None
        self._active_mode = None
        self.canvas.update()

    def paint(self, painter: QPainter, rect) -> bool:
        if self._active:
            return bool(self._active.paint(painter, rect))
        return False

    def resize(self, size: QSize) -> None:
        if self._active:
            self._active.resize(size)

    @property
    def active_mode(self) -> Optional[BackgroundMode]:
        return self._active_mode


class StaticImageBg(BackgroundLayer):
    """Render a still image as the desktop background."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._pixmap: Optional[QPixmap] = None
        self._config: Optional[BackgroundConfig] = None

    def start(self, config: BackgroundConfig) -> None:
        self._config = config
        if config.source and os.path.isfile(config.source):
            pixmap = QPixmap(config.source)
            self._pixmap = pixmap if not pixmap.isNull() else None
        else:
            self._pixmap = None

    def stop(self) -> None:
        self._pixmap = None

    def paint(self, painter: QPainter, rect: QRect) -> bool:
        if not self._pixmap or not self._config:
            return False
        fit = self._config.fit
        if fit == BackgroundFit.TILE:
            brush = QBrush(self._pixmap)
            painter.fillRect(rect, brush)
            return True
        if fit == BackgroundFit.CENTER:
            target = self._pixmap.rect()
            target.moveCenter(rect.center())
            painter.drawPixmap(target, self._pixmap)
            return True
        mode = Qt.KeepAspectRatio
        if fit == BackgroundFit.FILL:
            mode = Qt.KeepAspectRatioByExpanding
        scaled = self._pixmap.scaled(rect.size(), mode, Qt.SmoothTransformation)
        painter.drawPixmap(rect, scaled)
        return True


class GifBg(BackgroundLayer):
    """Display an animated GIF behind desktop icons."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._label = QLabel(canvas)
        self._label.setObjectName("DesktopGifBackground")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._label.hide()
        self._movie: Optional[QMovie] = None
        self._config: Optional[BackgroundConfig] = None

    def start(self, config: BackgroundConfig) -> None:
        self._config = config
        if self._movie:
            self._movie.stop()
        if not (config.source and os.path.isfile(config.source)):
            self.stop()
            return
        movie = QMovie(config.source)
        if not movie.isValid():
            self.stop()
            return
        self._movie = movie
        self._label.setMovie(movie)
        self._label.show()
        self._label.lower()
        self.resize(self.canvas.size())
        movie.start()

    def stop(self) -> None:
        if self._movie:
            self._movie.stop()
        self._movie = None
        self._label.clear()
        self._label.hide()

    def resize(self, size: QSize) -> None:
        self._label.setGeometry(0, 0, size.width(), size.height())
        if not self._movie or not self._config:
            return
        fit = self._config.fit
        if fit == BackgroundFit.CENTER:
            self._label.setScaledContents(False)
            self._label.setAlignment(Qt.AlignCenter)
        else:
            self._label.setScaledContents(True)
            self._label.setAlignment(Qt.AlignCenter)
            self._movie.setScaledSize(size)

    def paint(self, *_args) -> bool:
        return bool(self._movie)


try:  # Multimedia stack is optional
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
    from PySide6.QtMultimediaWidgets import QVideoWidget
except Exception:  # pragma: no cover - optional dependency guard
    QAudioOutput = None  # type: ignore
    QMediaPlayer = None  # type: ignore
    QVideoWidget = None  # type: ignore


class VideoBg(BackgroundLayer):
    """Loop a muted video behind the desktop icons."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._player = None
        self._audio = None
        self._widget = None
        self._config: Optional[BackgroundConfig] = None

    def _ensure_stack(self) -> bool:
        if QMediaPlayer is None or QVideoWidget is None or QAudioOutput is None:
            return False
        if self._player is None:
            self._player = QMediaPlayer(self.canvas)
            self._audio = QAudioOutput(self.canvas)
            self._player.setAudioOutput(self._audio)
            self._widget = QVideoWidget(self.canvas)
            self._widget.setObjectName("DesktopVideoBackground")
            self._widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self._widget.hide()
            self._player.mediaStatusChanged.connect(self._handle_status)
        return True

    def start(self, config: BackgroundConfig) -> None:
        self._config = config
        if not (config.source and os.path.isfile(config.source)):
            self.stop()
            return
        if not self._ensure_stack():
            self.stop()
            return
        assert self._player and self._widget and self._audio
        self._player.stop()
        self._player.setSource(QUrl.fromLocalFile(config.source))
        try:
            loops = -1 if config.loop else 1
            self._player.setLoops(loops)
        except Exception:
            pass
        self._audio.setMuted(bool(config.mute))
        self._player.setPlaybackRate(config.playback_rate or 1.0)
        self._widget.show()
        self._widget.lower()
        self.resize(self.canvas.size())
        self._player.play()

    def stop(self) -> None:
        if self._player:
            self._player.stop()
        if self._widget:
            self._widget.hide()
        self._config = None

    def resize(self, size: QSize) -> None:
        if self._widget:
            self._widget.setGeometry(0, 0, size.width(), size.height())

    def paint(self, *_args) -> bool:
        return bool(self._widget and self._widget.isVisible())

    def _handle_status(self, status) -> None:  # pragma: no cover - signal callback
        if not self._player or not self._config or QMediaPlayer is None:
            return
        try:
            end_status = QMediaPlayer.MediaStatus.EndOfMedia
        except Exception:
            end_status = getattr(QMediaPlayer, "EndOfMedia", None)
        if getattr(self._config, "loop", True) and status == end_status:
            self._player.setPosition(0)
            self._player.play()


LOGGER_GL = logging.getLogger("VirtualDesktop.GLBackground")


class GLViewportBg(BackgroundLayer):
    """Host a programmable OpenGL viewport as the background."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._viewport: Optional["LiveScriptViewport"] = None
        self._config: Optional[BackgroundConfig] = None

    def _ensure_viewport(self) -> bool:
        if LiveScriptViewport is None:
            LOGGER_GL.warning("Qt OpenGL widgets unavailable; GL background disabled")
            return False
        if self._viewport is None:
            self._viewport = LiveScriptViewport(self.canvas)
            self._viewport.setObjectName("DesktopGLViewport")
            self._viewport.hide()
        checker = self._resolve_heavy_checker()
        if checker:
            self._viewport.set_heavy_process_checker(checker)
        return True

    def start(self, config: BackgroundConfig) -> None:
        self._config = config
        if not (config.source and self._ensure_viewport()):
            self.stop()
            return
        assert self._viewport is not None
        try:
            base_fps = LiveScriptViewport.DEFAULT_FPS if LiveScriptViewport else 60.0
            playback = float(config.playback_rate or 1.0)
            fps = max(
                LiveScriptViewport.MIN_FPS,
                min(LiveScriptViewport.MAX_FPS, base_fps * playback),
            )
        except Exception:
            fps = LiveScriptViewport.DEFAULT_FPS if LiveScriptViewport else 60.0
        self._viewport.set_fps_cap(fps)
        self._viewport.set_script(config.source)
        checker = self._resolve_heavy_checker()
        if checker:
            self._viewport.set_heavy_process_checker(checker)
        self._viewport.show()
        self._viewport.lower()
        self.resize(self.canvas.size())
        self._viewport.start()

    def stop(self) -> None:
        if self._viewport:
            self._viewport.stop()
            self._viewport.hide()
        self._config = None

    def resize(self, size: QSize) -> None:
        if self._viewport:
            self._viewport.setGeometry(0, 0, size.width(), size.height())

    def paint(self, *_args) -> bool:
        return bool(self._viewport and self._viewport.isVisible())

    def _resolve_heavy_checker(self) -> Optional[Callable[[], bool]]:
        if self.canvas is None or self.canvas.window() is None:
            return None
        window = self.canvas.window()
        checker = getattr(window, "is_heavy_process_active", None)
        if callable(checker):
            return lambda: bool(checker())
        return None


@dataclass
class ScriptHooks:
    """Bundle of lifecycle hooks exposed by a background script."""

    module: ModuleType
    path: str
    mtime: float

    def invoke(self, name: str, *args) -> None:
        func = getattr(self.module, name, None)
        if callable(func):
            func(*args)


class LiveScriptController(QObject):
    """Manage loading and hot-reloading of a background script module."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._hooks: Optional[ScriptHooks] = None
        self._script_path: Optional[str] = None
        self._missing_warned = False

    @property
    def module(self) -> Optional[ModuleType]:
        return self._hooks.module if self._hooks else None

    @property
    def script_path(self) -> str:
        return self._script_path or ""

    def set_script(self, path: Optional[str]) -> None:
        self._script_path = path or ""
        self._missing_warned = False
        if not self._script_path:
            self._hooks = None
            return
        self._load(force=True)

    def reload_if_changed(self) -> bool:
        if not self._script_path:
            return False
        try:
            mtime = os.path.getmtime(self._script_path)
        except OSError:
            if not self._missing_warned:
                logging.getLogger("VirtualDesktop.LiveEngine").warning(
                    "Live background script missing: %s", self._script_path
                )
                self._missing_warned = True
            self._hooks = None
            return False
        if not self._hooks:
            self._load(force=True)
            return self._hooks is not None
        if mtime <= self._hooks.mtime:
            return False
        self._load(force=True)
        return self._hooks is not None and self._hooks.mtime == mtime

    def _load(self, force: bool = False) -> None:
        path = self._script_path
        if not path:
            self._hooks = None
            return
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            if not self._missing_warned:
                logging.getLogger("VirtualDesktop.LiveEngine").warning(
                    "Live background script not found: %s", path
                )
                self._missing_warned = True
            self._hooks = None
            return
        if not force and self._hooks and mtime <= self._hooks.mtime:
            return
        spec = importlib.util.spec_from_file_location("vdsk_live_background", path)
        if not spec or not spec.loader:
            logging.getLogger("VirtualDesktop.LiveEngine").error(
                "Unable to create spec for live background script: %s", path
            )
            self._hooks = None
            return
        module = importlib.util.module_from_spec(spec)
        try:
            loader = spec.loader
            assert loader is not None
            loader.exec_module(module)  # type: ignore[union-attr]
        except Exception:
            logging.getLogger("VirtualDesktop.LiveEngine").exception(
                "Live background script import failed"
            )
            self._hooks = None
            return
        sys.modules[spec.name] = module
        self._hooks = ScriptHooks(module=module, path=path, mtime=mtime)
        self._missing_warned = False

    def call(self, name: str, *args) -> None:
        if not self._hooks:
            return
        try:
            self._hooks.invoke(name, *args)
        except Exception:
            logging.getLogger("VirtualDesktop.LiveEngine").exception(
                "Live background script %s() failed", name
            )


try:  # Optional dependencies for OpenGL/psutil
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
except Exception:  # pragma: no cover - optional dependency guard
    QOpenGLWidget = None  # type: ignore

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency guard
    psutil = None  # type: ignore


if QOpenGLWidget is None:  # pragma: no cover - executed when OpenGL widget missing
    LiveScriptViewport = None  # type: ignore
else:

    class LiveScriptViewport(QOpenGLWidget):  # pragma: no cover - requires OpenGL context
        """OpenGL viewport that executes scripted hooks at a capped frame rate."""

        DEFAULT_FPS = 60.0
        MIN_FPS = 5.0
        MAX_FPS = 120.0
        RESOURCE_POLL_INTERVAL = 1.0
        CPU_THRESHOLD = 85.0
        MEMORY_THRESHOLD = 90.0

        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.setUpdateBehavior(QOpenGLWidget.PartialUpdate)
            self._controller = LiveScriptController(self)
            self._timer = QTimer(self)
            self._timer.setTimerType(Qt.PreciseTimer)
            self._timer.timeout.connect(self._tick)
            self._fps_cap = self.DEFAULT_FPS
            self._pending_dt = 0.0
            self._last_frame_time: Optional[float] = None
            self._needs_init = False
            self._heavy_checker: Optional[Callable[[], bool]] = None
            self._resource_flag = False
            self._last_resource_poll = 0.0

        def set_script(self, path: Optional[str]) -> None:
            self._controller.set_script(path)
            self._needs_init = True
            self._last_frame_time = None
            if path:
                self._ensure_running()
            else:
                self.stop()

        def set_fps_cap(self, fps: float) -> None:
            fps = max(self.MIN_FPS, min(self.MAX_FPS, float(fps) if fps else self.DEFAULT_FPS))
            self._fps_cap = fps
            if self._timer.isActive():
                self._ensure_running()

        def set_heavy_process_checker(self, checker: Optional[Callable[[], bool]]) -> None:
            self._heavy_checker = checker

        def start(self) -> None:
            if not self._timer.isActive():
                self._ensure_running()

        def stop(self) -> None:
            self._timer.stop()

        def initializeGL(self) -> None:
            self._needs_init = True
            self._last_frame_time = time.monotonic()

        def resizeGL(self, w: int, h: int) -> None:
            self._controller.call("resize", w, h)

        def paintGL(self) -> None:
            module = self._controller.module
            if module is None:
                return
            if self._needs_init and self.isValid():
                self._controller.call("init", self)
                self._needs_init = False
            dt = self._pending_dt
            if dt < 0:
                dt = 0.0
            self._controller.call("update", dt)
            self._controller.call("render", self)

        def showEvent(self, event):  # pragma: no cover - thin Qt wrapper
            super().showEvent(event)
            self._ensure_running()

        def hideEvent(self, event):  # pragma: no cover - thin Qt wrapper
            super().hideEvent(event)
            self.stop()

        def _ensure_running(self) -> None:
            if not self._controller.module and not self._controller.script_path:
                return
            interval_ms = int(max(1.0, 1000.0 / self._fps_cap))
            self._timer.start(interval_ms)

        def _tick(self) -> None:
            changed = self._controller.reload_if_changed()
            if self._controller.module is None:
                return
            if changed:
                self._needs_init = True
            if not self._should_render():
                self._last_frame_time = None
                return
            now = time.monotonic()
            if self._last_frame_time is None:
                self._pending_dt = 0.0
            else:
                self._pending_dt = max(0.0, now - self._last_frame_time)
            self._last_frame_time = now
            self.update()

        def _should_render(self) -> bool:
            if not self.isVisible():
                return False
            window = self.window()
            if window is not None:
                if hasattr(window, "isMinimized") and window.isMinimized():
                    return False
                if not window.isVisible():
                    return False
            if self._heavy_checker and self._heavy_checker():
                return False
            now = time.monotonic()
            if now - self._last_resource_poll >= self.RESOURCE_POLL_INTERVAL:
                self._resource_flag = self._system_is_heavy()
                self._last_resource_poll = now
            if self._resource_flag:
                return False
            return True

        def _system_is_heavy(self) -> bool:
            if psutil is None:
                return False
            try:
                cpu = psutil.cpu_percent(interval=None)
                if cpu >= self.CPU_THRESHOLD:
                    return True
                mem = psutil.virtual_memory().percent
                return mem >= self.MEMORY_THRESHOLD
            except Exception:
                return False


# ============================================================================
# Repository Reference Helper (Inlined from Dev_Logic/repo_reference_helper.py)
# ============================================================================
"""Repository indexing, suggestion APIs, and Qt-aware helper."""


def _normalize_extra_roots(repo_root: Path, roots: Optional[Sequence[Path | str]]) -> List[Path]:
    extras: List[Path] = []
    if not roots:
        return extras
    try:
        base = repo_root.resolve()
    except Exception:
        base = repo_root
    seen: Set[Path] = {base}
    for entry in roots:
        if not entry:
            continue
        try:
            candidate = Path(entry).expanduser().resolve()
        except Exception:
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        extras.append(candidate)
    return extras


@dataclass(frozen=True)
class RepoReference:
    """Lightweight reference describing a repository file or directory."""

    absolute_path: Path
    relative_path: str
    kind: str  # "file" or "directory"

    def display_label(self) -> str:
        suffix = "/" if self.kind == "directory" else ""
        return f"{self.relative_path}{suffix}"


class RepoReferenceIndex:
    """Maintain an in-memory list of repository file and directory references."""

    def __init__(
        self,
        repo_root: Path,
        *,
        repository_index: Optional[RepositoryIndex] = None,
        extra_roots: Optional[Sequence[Path | str]] = None,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self._extra_roots = _normalize_extra_roots(self.repo_root, extra_roots)
        self._allowed_roots: List[Path] = [self.repo_root] + self._extra_roots
        self.repository_index = repository_index or RepositoryIndex(
            repo_root=self.repo_root,
            extra_roots=self._extra_roots,
        )
        self._references: List[RepoReference] = []

    def refresh(self) -> None:
        references: List[RepoReference] = []
        file_paths = self._gather_file_paths()
        seen_dirs: Dict[Path, None] = {}

        for file_path in sorted(file_paths):
            rel = self._to_relative(file_path)
            references.append(
                RepoReference(absolute_path=file_path, relative_path=rel, kind="file")
            )
            for parent in file_path.parents:
                if parent == self.repo_root:
                    break
                if parent in seen_dirs:
                    continue
                seen_dirs[parent] = None
                references.append(
                    RepoReference(
                        absolute_path=parent,
                        relative_path=self._to_relative(parent),
                        kind="directory",
                    )
                )

        references.sort(key=lambda ref: (0 if ref.kind == "file" else 1, ref.relative_path.lower()))
        self._references = references

    def suggestions(self, query: str, limit: int = 5) -> List[RepoReference]:
        text = (query or "").strip().lower()
        if not text:
            return []

        matches: List[tuple[int, int, RepoReference]] = []
        for ref in self._references:
            rel_lower = ref.relative_path.lower()
            name_lower = ref.absolute_path.name.lower()
            if text in rel_lower or text in name_lower:
                prefix_match = 0 if rel_lower.startswith(text) or name_lower.startswith(text) else 1
                matches.append((prefix_match, len(rel_lower), ref))

        matches.sort()
        return [ref for _, _, ref in matches[:limit]]

    def entries(self) -> List[RepoReference]:
        return list(self._references)

    def _to_relative(self, path: Path) -> str:
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path
        for root in self._allowed_roots:
            try:
                rel = resolved.relative_to(root)
            except ValueError:
                continue
            rel_text = rel.as_posix()
            if root == self.repo_root:
                return rel_text
            prefix = root.name or root.as_posix()
            return f"{prefix}/{rel_text}" if rel_text else prefix
        return resolved.as_posix()

    def _match_allowed_root(self, value: object) -> Optional[Path]:
        if not value:
            return None
        try:
            candidate = Path(str(value)).expanduser().resolve()
        except Exception:
            return None
        for root in self._allowed_roots:
            if candidate == root:
                return root
        return None

    def _resolve_segment_path(self, base_root: Path, relative_path: str) -> Optional[Path]:
        try:
            candidate = Path(relative_path)
        except Exception:
            return None
        try:
            if candidate.is_absolute():
                resolved = candidate.resolve()
            else:
                resolved = (base_root / candidate).resolve()
        except Exception:
            return None
        try:
            resolved.relative_to(base_root)
        except ValueError:
            return None
        return resolved

    def _gather_file_paths(self) -> List[Path]:
        paths: Set[Path] = set()
        segments: Iterable[Dict[str, object]] = []

        try:
            self.repository_index.load()
            segments = list(self.repository_index.iter_segments())
        except Exception:
            segments = []

        if not segments:
            try:
                self.repository_index.rebuild()
                self.repository_index.load()
                segments = list(self.repository_index.iter_segments())
            except Exception as exc:  # pragma: no cover - logged for visibility
                logging.getLogger(__name__).debug(
                    "RepoReferenceIndex rebuild failed: %s", exc
                )
                segments = []

        allowed_set = {root for root in self._allowed_roots}
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            path_str = str(segment.get("path") or "")
            if not path_str:
                continue
            metadata = segment.get("metadata")
            base_root = None
            if isinstance(metadata, dict):
                base_root = self._match_allowed_root(metadata.get("scan_root"))
            if base_root is None:
                base_root = self.repo_root
            if base_root not in allowed_set:
                continue
            resolved = self._resolve_segment_path(base_root, path_str)
            if resolved is None:
                continue
            if resolved.is_file():
                paths.add(resolved)

        if not paths:
            for root in self._allowed_roots:
                if not root.exists():
                    continue
                for file_path in root.rglob("*"):
                    if file_path.is_file():
                        try:
                            resolved = file_path.resolve()
                        except Exception:
                            continue
                        paths.add(resolved)

        return list(paths)


class RepoReferenceHelper(QObject):
    """Qt-aware helper that refreshes repository references as the workspace changes."""

    refreshed = Signal()

    def __init__(
        self,
        repo_root: Path,
        *,
        parent: Optional[QObject] = None,
        repository_index: Optional[RepositoryIndex] = None,
        embed_contents: bool = True,
        case_sensitive: bool = False,
        token_guard: bool = True,
        extra_roots: Optional[Sequence[Path | str]] = None,
    ) -> None:
        super().__init__(parent)
        self.repo_root = Path(repo_root).resolve()
        self._extra_roots = _normalize_extra_roots(self.repo_root, extra_roots)
        self.index = RepoReferenceIndex(
            self.repo_root,
            repository_index=repository_index,
            extra_roots=self._extra_roots,
        )
        self.index.refresh()

        self.embed_contents = bool(embed_contents)
        self.case_sensitive = bool(case_sensitive)
        self.token_guard = bool(token_guard)

        self._watcher = QFileSystemWatcher(self)
        self._watcher.directoryChanged.connect(self._schedule_refresh)
        self._watcher.fileChanged.connect(self._schedule_refresh)

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)
        self._debounce.timeout.connect(self.refresh)

        self._register_watch_paths()

    def refresh(self) -> None:
        self.index.refresh()
        self.refreshed.emit()

    def suggestions(self, query: str, limit: int = 5) -> List[RepoReference]:
        return self.index.suggestions(query, limit)

    def _register_watch_paths(self) -> None:
        for root in [self.repo_root] + self._extra_roots:
            if not root.exists():
                continue
            try:
                self._watcher.addPath(str(root))
            except Exception as exc:  # pragma: no cover - watcher limitations
                logging.getLogger(__name__).debug(
                    "Failed to watch repo root %s: %s", root, exc
                )

        index_path = getattr(self.index.repository_index, "index_path", None)
        if index_path:
            path_obj = Path(index_path)
            if path_obj.exists():
                try:
                    self._watcher.addPath(str(path_obj))
                except Exception as exc:  # pragma: no cover - watcher limitations
                    logging.getLogger(__name__).debug(
                        "Failed to watch index %s: %s", path_obj, exc
                    )

    def _schedule_refresh(self, _path: str) -> None:
        self._debounce.start()


def pillow_available() -> bool:
    """Check whether Pillow image utilities are usable."""

    return dependency_available(_PILLOW_MODULE_NAME)


def ensure_pillow(feature: str) -> ModuleType:
    """Return the ``PIL.Image`` module or raise for the given feature context."""

    return ensure_dependency(_PILLOW_MODULE_NAME, feature)


def notify_dependency_missing(error: OptionalDependencyError) -> None:
    """Log and warn when an optional module is unavailable for a feature."""

    if error.module_name in _DEPENDENCY_WARNINGS_EMITTED:
        return
    logger = logging.getLogger(VD_LOGGER_NAME)
    logger.warning(error.user_message)
    warnings.warn(error.user_message, RuntimeWarning, stacklevel=3)
    _DEPENDENCY_WARNINGS_EMITTED.add(error.module_name)
MEMORY_PATH = here() / "memory" / "codex_memory.json"
LOGIC_INBOX_PATH = here() / "memory" / "logic_inbox.jsonl"
MEMORY_LOCK = threading.Lock()

@dataclass(slots=True)
class DurableLesson:
    """Structured representation of a long-lived repository lesson."""

    anchor: str
    title: str
    summary: str
    applies_to: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class InstructionItem:
    """Item stored in the logic inbox awaiting implementation."""

    id: str
    title: str
    status: str
    notes: str
    created_at: float | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "notes": self.notes,
        }
        if self.created_at is not None:
            payload["created_at"] = self.created_at
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


@dataclass(slots=True)
class SessionTail:
    """Tail view of a session conversation JSONL file."""

    session_id: str
    path: Path
    entries: List[Dict[str, Any]]
    updated_at: float


class DurableMemoryStore:
    """Manage durable lessons and session notes persisted in codex_memory.json."""

    _DEFAULT_PAYLOAD: Dict[str, Any] = {
        "version": "0.0.0",
        "stable_lessons": [],
        "sessions": [],
        "work_items": [],
    }

    def __init__(
        self,
        path: Path,
        *,
        lock: threading.Lock | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.path = path
        self._lock = lock or threading.Lock()
        self._logger = logger or logging.getLogger(VD_LOGGER_NAME)
        self._payload: Dict[str, Any] = {}
        self.lessons: Dict[str, DurableLesson] = {}
        self.session_entries: List[Dict[str, Any]] = []
        self.refresh()

    def refresh(self) -> None:
        """Reload lessons and session entries from disk."""

        payload = self._read()
        lessons_payload = payload.get("stable_lessons", [])
        lessons: Dict[str, DurableLesson] = {}
        for index, item in enumerate(lessons_payload):
            if not isinstance(item, Mapping):
                continue
            title = str(item.get("title", "")).strip()
            summary = str(item.get("summary", "")).strip()
            applies_to = str(item.get("applies_to", "")).strip()
            anchor = self._derive_anchor(item.get("id"), title, index)
            metadata = dict(item.get("metadata") or {})
            lessons[anchor] = DurableLesson(
                anchor=anchor,
                title=title,
                summary=summary,
                applies_to=applies_to,
                metadata=metadata,
            )
        self.lessons = lessons

        sessions_payload = payload.get("sessions", [])
        entries: List[Dict[str, str]] = []
        for item in sessions_payload:
            if not isinstance(item, Mapping):
                continue
            ts = item.get("timestamp")
            note = item.get("notes")
            if isinstance(note, str) and note.strip():
                entries.append(
                    {
                        "timestamp": str(ts) if isinstance(ts, str) else str(ts or ""),
                        "notes": note.strip(),
                    }
                )
        self.session_entries = entries
        self._payload = payload

    def list_lessons(self) -> List[DurableLesson]:
        """Return the loaded stable lessons in deterministic order."""

        return [self.lessons[key] for key in sorted(self.lessons.keys())]

    def get_lesson(self, anchor: str) -> DurableLesson | None:
        """Retrieve a single lesson by anchor."""

        return self.lessons.get(anchor)

    def upsert_lesson(
        self,
        *,
        title: str,
        summary: str,
        applies_to: str,
        anchor: str | None = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> DurableLesson:
        """Create or update a durable lesson entry."""

        anchor_value = anchor or self._derive_anchor(None, title, len(self.lessons))
        record = DurableLesson(
            anchor=anchor_value,
            title=title.strip(),
            summary=summary.strip(),
            applies_to=applies_to.strip(),
            metadata=dict(metadata or {}),
        )
        with self._lock:
            self.lessons[anchor_value] = record
            self._persist()
        return record

    def delete_lesson(self, anchor: str) -> bool:
        """Remove a lesson by anchor, returning ``True`` when deleted."""

        with self._lock:
            if anchor not in self.lessons:
                return False
            self.lessons.pop(anchor)
            self._persist()
        return True

    def list_session_notes(self) -> List[Dict[str, str]]:
        """Return the stored session note entries."""

        return list(self.session_entries)

    def append_session_note(self, note: str) -> Dict[str, str]:
        """Append a session note and persist it to disk."""

        entry = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "notes": note.strip(),
        }
        with self._lock:
            self.session_entries.append(entry)
            self._persist()
        return entry

    def _derive_anchor(
        self,
        candidate: Any,
        title: str,
        index: int,
    ) -> str:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
        base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if not base:
            base = f"lesson-{index + 1}"
        anchor = base
        counter = 1
        while anchor in self.lessons and self.lessons[anchor].title != title:
            counter += 1
            anchor = f"{base}-{counter}"
        return anchor

    def _read(self) -> Dict[str, Any]:
        if not self.path.exists():
            return dict(self._DEFAULT_PAYLOAD)
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            self._logger.exception("Failed to read codex memory")
        return dict(self._DEFAULT_PAYLOAD)

    def _persist(self) -> None:
        payload = dict(self._payload)
        payload.setdefault("version", self._DEFAULT_PAYLOAD["version"])
        payload["stable_lessons"] = [
            {
                "id": lesson.anchor,
                "title": lesson.title,
                "summary": lesson.summary,
                "applies_to": lesson.applies_to,
                **({"metadata": lesson.metadata} if lesson.metadata else {}),
            }
            for lesson in self.lessons.values()
        ]
        payload["sessions"] = list(self.session_entries)
        payload.setdefault("work_items", self._payload.get("work_items", []))

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, self.path)
        self._payload = payload


class InstructionInboxStore:
    """Manage instruction inbox entries persisted as JSONL."""

    def __init__(
        self,
        path: Path,
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self.path = path
        self._logger = logger or logging.getLogger(VD_LOGGER_NAME)
        self.items: Dict[str, InstructionItem] = {}
        self._order: List[str] = []
        self.refresh()

    def refresh(self) -> None:
        """Reload inbox items from disk."""

        self.items.clear()
        self._order.clear()
        if not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                for raw_line in fh:
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        self._logger.debug(
                            "Skipping malformed inbox entry: %s", line, exc_info=True
                        )
                        continue
                    item = self._coerce(payload)
                    self.items[item.id] = item
                    self._order.append(item.id)
        except Exception:
            self._logger.exception("Failed to refresh instruction inbox")

    def list_items(self) -> List[InstructionItem]:
        """Return inbox items preserving their file order."""

        return [self.items[item_id] for item_id in self._order if item_id in self.items]

    def get_item(self, item_id: str) -> InstructionItem | None:
        return self.items.get(item_id)

    def upsert(
        self,
        *,
        item_id: str,
        title: str,
        status: str,
        notes: str,
        created_at: float | None = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> InstructionItem:
        """Insert or update an instruction inbox record."""

        record = InstructionItem(
            id=item_id,
            title=title.strip(),
            status=status.strip(),
            notes=notes.strip(),
            created_at=created_at,
            metadata=dict(metadata or {}),
        )
        if item_id not in self.items:
            self._order.append(item_id)
        self.items[item_id] = record
        self._flush()
        return record

    def mark_status(self, item_id: str, status: str) -> InstructionItem | None:
        record = self.items.get(item_id)
        if not record:
            return None
        updated = InstructionItem(
            id=record.id,
            title=record.title,
            status=status.strip(),
            notes=record.notes,
            created_at=record.created_at,
            metadata=dict(record.metadata),
        )
        self.items[item_id] = updated
        self._flush()
        return updated

    def delete(self, item_id: str) -> bool:
        if item_id not in self.items:
            return False
        self.items.pop(item_id)
        self._order = [existing for existing in self._order if existing != item_id]
        self._flush()
        return True

    def _coerce(self, payload: Mapping[str, Any]) -> InstructionItem:
        item_id = str(payload.get("id") or uuid.uuid4().hex)
        title = str(payload.get("title", "")).strip()
        status = str(payload.get("status", "pending")).strip()
        notes = str(payload.get("notes", "")).strip()
        created_at_raw = payload.get("created_at")
        created_at = float(created_at_raw) if isinstance(created_at_raw, (int, float)) else None
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), Mapping) else {}
        return InstructionItem(
            id=item_id,
            title=title,
            status=status or "pending",
            notes=notes,
            created_at=created_at,
            metadata=dict(metadata),
        )

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            for item_id in self._order:
                item = self.items.get(item_id)
                if not item:
                    continue
                tmp.write(json.dumps(item.to_payload(), ensure_ascii=False) + "\n")
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, self.path)


class SessionTailStore:
    """Load session conversation tails and expose CRUD helpers."""

    def __init__(
        self,
        sessions_root: Path,
        *,
        tail_lines: int = 50,
        logger: logging.Logger | None = None,
    ) -> None:
        self.sessions_root = sessions_root
        self.tail_lines = max(1, tail_lines)
        self._logger = logger or logging.getLogger(VD_LOGGER_NAME)
        self._tails: Dict[str, SessionTail] = {}
        self.refresh()

    def refresh(self, sessions_root: Optional[Path] = None) -> None:
        """Reload session tails from disk."""

        if sessions_root is not None:
            self.sessions_root = sessions_root
        self.sessions_root.mkdir(parents=True, exist_ok=True)
        tails: Dict[str, SessionTail] = {}
        for session_dir in self.sessions_root.iterdir():
            if not session_dir.is_dir():
                continue
            jsonl_path = session_dir / "conversation.jsonl"
            if not jsonl_path.exists():
                continue
            tail_entries = self._read_tail(jsonl_path)
            updated_at = jsonl_path.stat().st_mtime
            tails[session_dir.name] = SessionTail(
                session_id=session_dir.name,
                path=jsonl_path,
                entries=tail_entries,
                updated_at=updated_at,
            )
        self._tails = tails

    def list_tails(self) -> List[SessionTail]:
        """Return session tails sorted by modification time (desc)."""

        return sorted(
            self._tails.values(),
            key=lambda tail: tail.updated_at,
            reverse=True,
        )

    def get_tail(self, session_id: str) -> SessionTail | None:
        return self._tails.get(session_id)

    def append_entry(self, session_id: str, entry: Mapping[str, Any]) -> SessionTail:
        """Append a JSONL entry to the session log and refresh its tail."""

        jsonl_path = self._ensure_session_path(session_id)
        with jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return self._refresh_single(session_id)

    def overwrite_entries(
        self,
        session_id: str,
        entries: Iterable[Mapping[str, Any]],
    ) -> SessionTail:
        """Rewrite the JSONL file for a session with the provided entries."""

        jsonl_path = self._ensure_session_path(session_id)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            for entry in entries:
                tmp.write(json.dumps(entry, ensure_ascii=False) + "\n")
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, jsonl_path)
        return self._refresh_single(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete the JSONL file for the given session."""

        tail = self._tails.get(session_id)
        if not tail:
            return False
        try:
            tail.path.unlink(missing_ok=True)
        except Exception:
            self._logger.exception("Failed to delete session jsonl", exc_info=True)
            return False
        self._tails.pop(session_id, None)
        return True

    def _ensure_session_path(self, session_id: str) -> Path:
        session_dir = self.sessions_root / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = session_dir / "conversation.jsonl"
        if not jsonl_path.exists():
            jsonl_path.write_text("", encoding="utf-8")
        return jsonl_path

    def _refresh_single(self, session_id: str) -> SessionTail:
        jsonl_path = self._ensure_session_path(session_id)
        entries = self._read_tail(jsonl_path)
        tail = SessionTail(
            session_id=session_id,
            path=jsonl_path,
            entries=entries,
            updated_at=jsonl_path.stat().st_mtime,
        )
        self._tails[session_id] = tail
        return tail

    def _read_tail(self, path: Path) -> List[Dict[str, Any]]:
        rows: Deque[str] = deque(maxlen=self.tail_lines)
        try:
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    stripped = line.strip()
                    if stripped:
                        rows.append(stripped)
        except Exception:
            self._logger.exception("Failed to read session tail", exc_info=True)
            return []
        entries: List[Dict[str, Any]] = []
        for raw in rows:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                entries.append(data)
        return entries


class MemoryServices:
    """Aggregate durable lessons, inbox items, and session tails."""

    def __init__(
        self,
        *,
        lessons_path: Path,
        inbox_path: Path,
        sessions_root: Path,
        logger: logging.Logger | None = None,
    ) -> None:
        self.logger = logger or logging.getLogger(VD_LOGGER_NAME)
        self.lessons = DurableMemoryStore(lessons_path, lock=MEMORY_LOCK, logger=self.logger)
        self.inbox = InstructionInboxStore(inbox_path, logger=self.logger)
        self.sessions = SessionTailStore(sessions_root, logger=self.logger)

    def refresh(
        self,
        *,
        lessons_path: Optional[Path] = None,
        inbox_path: Optional[Path] = None,
        sessions_root: Optional[Path] = None,
    ) -> None:
        """Reload stores, updating paths when provided."""

        if lessons_path is not None and lessons_path != self.lessons.path:
            self.lessons.path = lessons_path
        if inbox_path is not None and inbox_path != self.inbox.path:
            self.inbox.path = inbox_path
        if sessions_root is not None:
            self.sessions.refresh(sessions_root=sessions_root)
        else:
            self.sessions.refresh()
        self.lessons.refresh()
        self.inbox.refresh()

    def load_session_notes(self) -> List[Dict[str, str]]:
        return self.lessons.list_session_notes()

    def append_session_note(self, note: str) -> Dict[str, str]:
        return self.lessons.append_session_note(note)


def memory_services() -> MemoryServices:
    """Return the shared memory services singleton, creating it if needed."""

    global MEMORY_SERVICES
    if MEMORY_SERVICES is None:
        MEMORY_SERVICES = MemoryServices(
            lessons_path=MEMORY_PATH,
            inbox_path=LOGIC_INBOX_PATH,
            sessions_root=agent_sessions_dir(),
            logger=logging.getLogger(VD_LOGGER_NAME),
        )
    return MEMORY_SERVICES


def load_session_notes() -> List[Dict[str, str]]:
    """Proxy to the session note list maintained by :class:`MemoryServices`."""

    return memory_services().load_session_notes()


def append_session_note(note: str) -> Dict[str, str]:
    """Append a session note via the shared memory services."""

    return memory_services().append_session_note(note)


MEMORY_SERVICES = memory_services()


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
    operation: Optional[str] = None,
) -> Tuple[int, str, str]:
    """Execute ``cmd`` and update task bookkeeping when provided.

    ``operation`` designates high-level flows such as ``"coder"`` or ``"test"`` so
    safety policies can enforce allowlists, denylists, and sandbox expectations.
    """

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
            safety_manager.ensure_command_allowed(cmd, operation=operation)
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


def run_coder_command(
    cmd: List[str],
    *,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    task: Optional[Task] = None,
    dataset_root: Optional[Path] = None,
    workspace: Optional[Path] = None,
    cancelled: bool = False,
) -> Tuple[int, str, str]:
    """Execute a command under the coder operation policy."""

    return run_checked(
        cmd,
        cwd=cwd,
        env=env,
        timeout=timeout,
        task=task,
        dataset_root=dataset_root,
        workspace=workspace,
        cancelled=cancelled,
        operation="coder",
    )


def run_test_command(
    cmd: List[str],
    *,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    task: Optional[Task] = None,
    dataset_root: Optional[Path] = None,
    workspace: Optional[Path] = None,
    cancelled: bool = False,
) -> Tuple[int, str, str]:
    """Execute a command under the tester operation policy."""

    return run_checked(
        cmd,
        cwd=cwd,
        env=env,
        timeout=timeout,
        task=task,
        dataset_root=dataset_root,
        workspace=workspace,
        cancelled=cancelled,
        operation="test",
    )

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
        return requests_available()

    def health(self) -> Tuple[bool, str]:
        try:
            http = ensure_requests("Ollama HTTP health check")
        except OptionalDependencyError as exc:
            notify_dependency_missing(exc)
            return False, exc.user_message
        try:
            r = http.get(self.host, timeout=3)
            return (r.ok, "OK" if r.ok else f"{r.status_code}")
        except Exception as e:
            return False, str(e)

    def list_models(self) -> Tuple[bool, List[str], str]:
        try:
            http = ensure_requests("Ollama model listing")
        except OptionalDependencyError as exc:
            notify_dependency_missing(exc)
        else:
            try:
                r = http.get(f"{self.host}/api/tags", timeout=5)
                if r.ok:
                    data = r.json()
                    names = [
                        m.get("name") or m.get("model")
                        for m in data.get("models", [])
                        if m.get("name") or m.get("model")
                    ]
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
        try:
            http = ensure_requests("Ollama embeddings API")
        except OptionalDependencyError as exc:
            notify_dependency_missing(exc)
            return False, [], exc.user_message
        try:
            payload = {"model": model, "input": text}
            r = http.post(
                f"{self.host}/api/embeddings", json=payload, timeout=120
            )
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
        try:
            http = ensure_requests("Ollama chat API")
        except OptionalDependencyError as exc:
            notify_dependency_missing(exc)
            return False, "", exc.user_message
        try:
            body: Dict[str, Any] = {"model": model, "messages": messages, "stream": False}
            if images:
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        msg["images"] = images
                        break
            r = http.post(
                f"{self.host}/api/chat",
                json=body,
                timeout=600,
                headers={"Content-Type": "application/json"},
            )
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


@dataclass(slots=True)
class DatasetNode:
    """Representation of a persisted dataset node and its sidecars."""

    anchor: str
    core: Dict[str, Any]
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    vector_path: Optional[Path] = None
    thumbnail_paths: List[Path] = field(default_factory=list)
    meta_path: Optional[Path] = None


class DatasetNodePersistence:
    """Manage dataset JSONL cores with sidecar metadata and vectors."""

    SIDECAR_DIRNAME = "dataset_nodes"
    VECTOR_SUFFIX = ".vec.json"
    META_SUFFIX = ".meta.json"
    THUMBNAIL_DIRNAME = "thumbnails"

    def __init__(
        self,
        dataset_path: Path,
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self.dataset_path = dataset_path
        self.logger = logger or logging.getLogger(VD_LOGGER_NAME)
        base_dir = ensure_dir(self.dataset_path.parent)
        self.sidecar_root = ensure_dir(base_dir / self.SIDECAR_DIRNAME)
        self.thumbnail_root = ensure_dir(self.sidecar_root / self.THUMBNAIL_DIRNAME)
        self._ensure_gitignore(self.sidecar_root)
        self._ensure_gitignore(self.thumbnail_root)

    def append(
        self,
        core: Mapping[str, Any],
        *,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        thumbnails: Optional[Iterable[Path]] = None,
    ) -> DatasetNode:
        anchor = str(core.get("anchor") or core.get("id") or uuid.uuid4().hex)
        sanitized = self._sanitize_core(core, anchor)
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        with self.dataset_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(sanitized, ensure_ascii=False) + "\n")

        vector_path = self._write_embedding(anchor, embedding)
        meta_path = self._write_metadata(anchor, metadata)
        thumb_paths = self._register_thumbnails(anchor, thumbnails)
        metadata_payload = self._read_metadata(anchor)
        embedding_payload = list(embedding or self._read_embedding(anchor))
        return DatasetNode(
            anchor=anchor,
            core=sanitized,
            embedding=embedding_payload,
            metadata=metadata_payload,
            vector_path=vector_path,
            thumbnail_paths=thumb_paths,
            meta_path=meta_path,
        )

    def iter_nodes(self) -> Iterable[DatasetNode]:
        for record in self._core_records():
            anchor = str(record.get("anchor") or record.get("id") or "").strip()
            if not anchor:
                continue
            raw_embedding = record.get("embedding")
            sanitized = self._sanitize_core(record, anchor)
            embedding = self._read_embedding(anchor)
            if not embedding and isinstance(raw_embedding, list):
                embedding = self._coerce_vector(raw_embedding)
            metadata_payload = self._read_metadata(anchor)
            thumbs = self._list_thumbnails(anchor)
            yield DatasetNode(
                anchor=anchor,
                core=sanitized,
                embedding=embedding,
                metadata=metadata_payload,
                vector_path=self._embedding_path(anchor) if embedding else None,
                thumbnail_paths=thumbs,
                meta_path=self._metadata_path(anchor) if metadata_payload else None,
            )

    def load(self, anchor: str) -> DatasetNode | None:
        for node in self.iter_nodes():
            if node.anchor == anchor:
                return node
        return None

    def update(
        self,
        anchor: str,
        *,
        core_updates: Optional[Mapping[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        thumbnails: Optional[Iterable[Path]] = None,
    ) -> DatasetNode | None:
        records = self._core_records()
        updated = None
        rewritten: List[Dict[str, Any]] = []
        for record in records:
            record_anchor = str(record.get("anchor") or record.get("id") or "").strip()
            if not record_anchor:
                continue
            if record_anchor == anchor:
                merged = dict(record)
                for key, value in (core_updates or {}).items():
                    if key in {"embedding", "metadata", "thumbnails"}:
                        continue
                    merged[key] = value
                sanitized = self._sanitize_core(merged, anchor)
                rewritten.append(sanitized)
                updated = sanitized
            else:
                rewritten.append(self._sanitize_core(record, record_anchor))

        if updated is None:
            return None

        self._write_core_records(rewritten)
        vector_path = self._write_embedding(anchor, embedding)
        meta_path = self._write_metadata(anchor, metadata)
        thumb_paths = self._register_thumbnails(anchor, thumbnails)
        metadata_payload = self._read_metadata(anchor)
        embedding_payload = list(embedding or self._read_embedding(anchor))
        if not thumb_paths:
            thumb_paths = self._list_thumbnails(anchor)
        return DatasetNode(
            anchor=anchor,
            core=updated,
            embedding=embedding_payload,
            metadata=metadata_payload,
            vector_path=vector_path,
            thumbnail_paths=thumb_paths,
            meta_path=meta_path,
        )

    def delete(self, anchor: str) -> bool:
        records = self._core_records()
        changed = False
        rewritten: List[Dict[str, Any]] = []
        for record in records:
            record_anchor = str(record.get("anchor") or record.get("id") or "").strip()
            if record_anchor == anchor:
                changed = True
                continue
            rewritten.append(self._sanitize_core(record, record_anchor))
        if not changed:
            return False
        self._write_core_records(rewritten)
        self._cleanup_sidecars(anchor)
        return True

    def thumbnail_dir(self, anchor: str, *, ensure: bool = True) -> Path:
        directory = self.thumbnail_root / anchor
        if ensure:
            directory.mkdir(parents=True, exist_ok=True)
            self._ensure_gitignore(directory)
        return directory

    # ------------------------------------------------------------------
    def _sanitize_core(self, core: Mapping[str, Any], anchor: str) -> Dict[str, Any]:
        record = dict(core)
        record["anchor"] = anchor
        record.pop("embedding", None)
        record.pop("metadata", None)
        record.pop("thumbnails", None)
        return record

    def _core_records(self) -> List[Dict[str, Any]]:
        if not self.dataset_path.exists():
            return []
        records: List[Dict[str, Any]] = []
        with self.dataset_path.open("r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    records.append(payload)
        return records

    def _write_core_records(self, records: Iterable[Mapping[str, Any]]) -> None:
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
            for record in records:
                tmp.write(json.dumps(record, ensure_ascii=False) + "\n")
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, self.dataset_path)

    def _write_embedding(
        self, anchor: str, embedding: Optional[List[float]]
    ) -> Optional[Path]:
        path = self._embedding_path(anchor)
        if embedding is None:
            return path if path.exists() else None
        vector = self._coerce_vector(embedding)
        if not vector:
            if path.exists():
                path.unlink(missing_ok=True)
            return None
        with path.open("w", encoding="utf-8") as fh:
            json.dump({"embedding": vector}, fh, ensure_ascii=False)
        return path

    def _read_embedding(self, anchor: str) -> List[float]:
        path = self._embedding_path(anchor)
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                payload = payload.get("embedding")
            if isinstance(payload, list):
                return self._coerce_vector(payload)
        except Exception:
            self.logger.debug("Failed to read embedding for %s", anchor, exc_info=True)
        return []

    def _write_metadata(
        self, anchor: str, metadata: Optional[Mapping[str, Any]]
    ) -> Path:
        path = self._metadata_path(anchor)
        if metadata is None and path.exists():
            return path
        payload = {
            "anchor": anchor,
            "stored_at": datetime.now(UTC).isoformat(),
            "metadata": dict(metadata or self._read_metadata(anchor)),
        }
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        return path

    def _read_metadata(self, anchor: str) -> Dict[str, Any]:
        path = self._metadata_path(anchor)
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            self.logger.debug("Failed to read metadata for %s", anchor, exc_info=True)
            return {}
        data = payload.get("metadata") if isinstance(payload, dict) else {}
        result = dict(data) if isinstance(data, Mapping) else {}
        stored_at = payload.get("stored_at") if isinstance(payload, dict) else None
        if isinstance(stored_at, str) and stored_at.strip():
            result.setdefault("stored_at", stored_at)
        return result

    def _register_thumbnails(
        self, anchor: str, thumbnails: Optional[Iterable[Path]]
    ) -> List[Path]:
        if not thumbnails:
            return self._list_thumbnails(anchor)
        dest_dir = self.thumbnail_dir(anchor)
        results: List[Path] = []
        for thumb in thumbnails:
            try:
                source = Path(thumb)
            except Exception:
                continue
            if not source.exists():
                continue
            target = dest_dir / source.name
            if source.resolve() != target.resolve():
                try:
                    shutil.copy2(source, target)
                except Exception:
                    self.logger.debug(
                        "Failed to stage thumbnail %s", source, exc_info=True
                    )
                    continue
            else:
                target = source
            results.append(target)
        return results or self._list_thumbnails(anchor)

    def _list_thumbnails(self, anchor: str) -> List[Path]:
        directory = self.thumbnail_dir(anchor, ensure=False)
        if not directory.exists():
            return []
        return sorted(p for p in directory.iterdir() if p.is_file())

    def _cleanup_sidecars(self, anchor: str) -> None:
        self._embedding_path(anchor).unlink(missing_ok=True)
        self._metadata_path(anchor).unlink(missing_ok=True)
        directory = self.thumbnail_dir(anchor, ensure=False)
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)

    def _embedding_path(self, anchor: str) -> Path:
        return self.sidecar_root / f"{anchor}{self.VECTOR_SUFFIX}"

    def _metadata_path(self, anchor: str) -> Path:
        return self.sidecar_root / f"{anchor}{self.META_SUFFIX}"

    def _ensure_gitignore(self, root: Path) -> None:
        gitignore = root / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n!.gitignore\n", encoding="utf-8")

    @staticmethod
    def _coerce_vector(raw: Iterable[Any]) -> List[float]:
        vector: List[float] = []
        for value in raw:
            if isinstance(value, (int, float)):
                vector.append(float(value))
        return vector

class DatasetManager:
    """Persist dataset entries with Git-friendly cores and sidecars."""

    def __init__(
        self,
        session_dir: Path,
        embedder: str,
        ollama: OllamaClient,
        data_root: Optional[Path] = None,
        enable_semantic: bool = True,
    ) -> None:
        self.session_dir = ensure_dir(session_dir)
        self.dataset_path = self.session_dir / "dataset.jsonl"
        self.embedder = embedder
        self.ollama = ollama
        self.lock = threading.Lock()
        self.enable_semantic = enable_semantic
        self.data_root = ensure_dir(data_root) if data_root else self.session_dir.parent
        self.persistence = DatasetNodePersistence(
            self.dataset_path,
            logger=logging.getLogger(VD_LOGGER_NAME),
        )

    def add_entry(
        self,
        role: str,
        text: str,
        images: List[Path],
        tags: Optional[List[str]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        anchor = uuid.uuid4().hex
        core: Dict[str, Any] = {
            "id": anchor,
            "anchor": anchor,
            "ts": time.time(),
            "role": role,
            "text": text,
            "images": [img.name for img in images],
            "tags": list(tags or []),
        }
        if extra:
            for key, value in extra.items():
                if key in {"embedding", "metadata", "thumbnails"}:
                    continue
                core[key] = value

        embedding_vec: List[float] = []
        if self.enable_semantic and text.strip():
            ok, vec, _ = self.ollama.embeddings(self.embedder, text)
            if ok and isinstance(vec, list):
                embedding_vec = DatasetNodePersistence._coerce_vector(vec)

        metadata: Dict[str, Any] = {
            "images": [str(path) for path in images],
            "tags": list(tags or []),
        }
        if extra:
            metadata["extra"] = extra

        thumbnails = self._generate_thumbnails(anchor, images)

        with self.lock:
            node = self.persistence.append(
                core,
                embedding=embedding_vec or None,
                metadata=metadata,
                thumbnails=thumbnails,
            )

        if embedding_vec:
            node.embedding = embedding_vec
        if thumbnails:
            node.thumbnail_paths = thumbnails

        payload = dict(node.core)
        payload["embedding"] = node.embedding
        if node.metadata:
            payload["metadata"] = node.metadata
        if node.thumbnail_paths:
            payload["thumbnails"] = [p.as_posix() for p in node.thumbnail_paths]
        return payload

    def _generate_thumbnails(self, anchor: str, images: List[Path]) -> List[Path]:
        if not images or Image is None:
            return []
        thumb_dir = self.persistence.thumbnail_dir(anchor)
        generated: List[Path] = []
        for index, image_path in enumerate(images):
            try:
                source = Path(image_path)
            except Exception:
                continue
            if not source.exists():
                continue
            try:
                with Image.open(source) as handle:  # type: ignore[attr-defined]
                    handle.thumbnail((320, 320))
                    dest = thumb_dir / f"{index:02d}_{source.stem}.png"
                    handle.save(dest)
                    generated.append(dest)
            except Exception:
                logging.getLogger(VD_LOGGER_NAME).debug(
                    "Failed to generate thumbnail for %s",
                    source,
                    exc_info=True,
                )
        return generated

    def _all_dataset_files(self) -> List[Path]:
        files: List[Path] = []
        for path in self.data_root.rglob("dataset.jsonl"):
            files.append(path)
        if self.dataset_path not in files and self.dataset_path.exists():
            files.append(self.dataset_path)
        return files

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if not self.enable_semantic or k <= 0:
            return []
        ok, vector, _ = self.ollama.embeddings(self.embedder, query)
        if not ok or not isinstance(vector, list):
            return []
        query_vec = DatasetNodePersistence._coerce_vector(vector)
        if not query_vec:
            return []

        scored: List[Tuple[float, DatasetNode]] = []
        for dataset_file in self._all_dataset_files():
            persistence = DatasetNodePersistence(
                dataset_file,
                logger=logging.getLogger(VD_LOGGER_NAME),
            )
            for node in persistence.iter_nodes():
                embedding = node.embedding
                if not embedding and isinstance(node.core.get("embedding"), list):
                    embedding = DatasetNodePersistence._coerce_vector(
                        node.core.get("embedding")  # type: ignore[arg-type]
                    )
                if not embedding:
                    continue
                score = cosine(query_vec, embedding)
                scored.append((score, node))

        scored.sort(key=lambda item: item[0], reverse=True)
        results: List[Dict[str, Any]] = []
        for score, node in scored[:k]:
            payload = dict(node.core)
            payload["embedding"] = node.embedding
            if node.metadata:
                payload["metadata"] = node.metadata
            if node.thumbnail_paths:
                payload["thumbnails"] = [p.as_posix() for p in node.thumbnail_paths]
            payload["similarity"] = score
            results.append(payload)
        return results


@dataclass(slots=True)
class HippocampusNodeRecord:
    """In-memory representation of a node persisted by Hippocampus."""

    anchor: str
    label: str
    source_path: str
    tags: List[str]
    summary: str
    embedding: List[float]
    metadata: Dict[str, Any]

    def as_payload(self) -> Dict[str, Any]:
        """Return a serialisable payload for UI loggers or telemetry."""

        return {
            "anchor": self.anchor,
            "label": self.label,
            "source_path": self.source_path,
            "tags": list(self.tags),
            "summary": self.summary,
            "embedding": list(self.embedding),
            "metadata": self.metadata,
        }


class BrainMapRegistry:
    """Durable store backing the 3D brain map visualisation."""

    def __init__(
        self,
        storage_path: Path,
        *,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.storage_path = storage_path
        self.logger = logger or logging.getLogger(VD_LOGGER_NAME)
        self._lock = threading.RLock()
        self._state: Dict[str, Any] = {"nodes": {}, "edges": []}
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.logger.warning(
                "Failed to load brain map registry: %s", exc, exc_info=True
            )
            return
        if not isinstance(data, dict):
            return
        nodes = data.get("nodes")
        edges = data.get("edges")
        if isinstance(nodes, dict) and isinstance(edges, list):
            with self._lock:
                self._state["nodes"] = nodes
                self._state["edges"] = edges

    def _persist(self) -> None:
        ensure_dir(self.storage_path.parent)
        try:
            self.storage_path.write_text(
                json.dumps(self._state, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        except Exception as exc:
            self.logger.warning(
                "Failed to persist brain map registry: %s", exc, exc_info=True
            )

    def register_node(self, node_id: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._state.setdefault("nodes", {})[node_id] = payload
            self._persist()
        self.logger.debug("Brain map node registered: %s", node_id)

    def register_edge(self, source: str, target: str, relation: str) -> None:
        edge = {"source": source, "target": target, "relation": relation}
        with self._lock:
            edges: List[Dict[str, str]] = self._state.setdefault("edges", [])
            edges.append(edge)
            self._persist()
        self.logger.debug(
            "Brain map edge registered: %s -> %s (%s)",
            source,
            target,
            relation,
        )

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._state))


class HippocampusClient:
    """Bridge datasets into Hippocampus nodes plus brain map edges."""

    _IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}
    _MAX_TEXT_BYTES = 131_072
    _MAX_DIRECTORY_DEPTH = 4
    _MAX_DIRECTORY_LISTING = 64

    def __init__(
        self,
        dataset: DatasetManager,
        brain_map: BrainMapRegistry,
        ollama: OllamaClient,
        settings: Mapping[str, Any],
        *,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.dataset = dataset
        self.brain_map = brain_map
        self.ollama = ollama
        self.settings = settings
        self.logger = logger or logging.getLogger(VD_LOGGER_NAME)
        self.enable_vision = bool(settings.get("enable_vision", True))
        self.summary_model = str(
            settings.get("chat_model", DEFAULT_CHAT_MODEL)
        ).strip()
        self.vision_model = str(
            settings.get("vision_model", DEFAULT_VISION_MODEL)
        ).strip()

    def ingest_assets(
        self,
        paths: Sequence[Path],
        tags: Sequence[str],
        note: str,
        *,
        progress: Optional[Callable[[str], None]] = None,
    ) -> List[HippocampusNodeRecord]:
        records: List[HippocampusNodeRecord] = []
        for path in paths:
            if progress:
                progress(f"Ingesting {path}")
            try:
                resolved = path.expanduser().resolve()
            except Exception:
                resolved = path
            records.extend(
                self._ingest_path(resolved, list(tags), note, 0, progress)
            )
        return records

    def _ingest_path(
        self,
        path: Path,
        tags: List[str],
        note: str,
        depth: int,
        progress: Optional[Callable[[str], None]],
    ) -> List[HippocampusNodeRecord]:
        if depth > self._MAX_DIRECTORY_DEPTH:
            summary = (
                f"Depth limit reached while scanning {path}. Captured metadata "
                "only."
            )
            payload = self.dataset.add_entry(
                "system",
                summary,
                [],
                tags=tags + ["hippocampus_depth_limit"],
                extra={"source_path": str(path)},
            )
            record = self._register_node(path, summary, tags, payload)
            return [record]

        if path.is_dir():
            return self._ingest_directory(path, tags, note, depth, progress)
        return [self._ingest_file(path, tags, note, progress)]

    def _ingest_directory(
        self,
        directory: Path,
        tags: List[str],
        note: str,
        depth: int,
        progress: Optional[Callable[[str], None]],
    ) -> List[HippocampusNodeRecord]:
        try:
            entries = sorted(directory.iterdir(), key=lambda p: p.name.lower())
        except Exception as exc:
            summary = f"Unable to enumerate {directory}: {exc}"
            payload = self.dataset.add_entry(
                "system",
                summary,
                [],
                tags=tags + ["hippocampus_error"],
                extra={"source_path": str(directory)},
            )
            record = self._register_node(directory, summary, tags, payload)
            return [record]

        limited = entries[: self._MAX_DIRECTORY_LISTING]
        overflow = len(entries) - len(limited)
        child_records: List[HippocampusNodeRecord] = []
        for child in limited:
            if progress:
                progress(f"Processing {child}")
            child_records.extend(
                self._ingest_path(child, tags, note, depth + 1, progress)
            )
        child_labels = ", ".join(rec.label for rec in child_records[:6])
        if overflow > 0:
            child_labels += f" … (+{overflow} more)"
        summary_parts = [
            f"Directory ingest for {directory.name}",
            f"Tags: {', '.join(tags) or '(none)'}",
        ]
        if note.strip():
            summary_parts.append(f"Operator note: {note.strip()}")
        if child_labels:
            summary_parts.append(f"Children: {child_labels}")
        summary = "\n".join(summary_parts)
        payload = self.dataset.add_entry(
            "system",
            summary,
            [],
            tags=tags + ["hippocampus_directory"],
            extra={
                "source_path": str(directory),
                "children": [rec.anchor for rec in child_records],
            },
        )
        record = self._register_node(directory, summary, tags, payload)
        for child in child_records:
            self.brain_map.register_edge(record.anchor, child.anchor, "contains")
        return [record] + child_records

    def _ingest_file(
        self,
        path: Path,
        tags: List[str],
        note: str,
        progress: Optional[Callable[[str], None]],
    ) -> HippocampusNodeRecord:
        suffix = path.suffix.lower()
        if suffix in self._IMAGE_SUFFIXES:
            return self._ingest_image(path, tags, note)
        snippet, is_text = self._extract_text_snippet(path)
        if is_text and snippet.strip():
            return self._ingest_text_file(path, tags, note, snippet)
        return self._ingest_binary_file(path, tags)

    def _ingest_image(
        self,
        path: Path,
        tags: List[str],
        note: str,
    ) -> HippocampusNodeRecord:
        ocr_res = perform_ocr(path)
        vision_summary = ""
        if self.enable_vision:
            vision = analyze_image(
                path,
                ocr_res.markdown if ocr_res.ok else "",
                client=self.ollama,
                model=self.vision_model or DEFAULT_VISION_MODEL,
                user_text=note,
            )
            if vision.ok:
                vision_summary = vision.summary
        combined_source = []
        if ocr_res.ok:
            combined_source.append(f"OCR Markdown:\n{ocr_res.markdown}")
        elif ocr_res.error:
            combined_source.append(f"OCR error: {ocr_res.error}")
        if vision_summary:
            combined_source.append(f"Vision summary:\n{vision_summary}")
        source_text = "\n\n".join(combined_source)
        summary = self._summarise_asset(path, tags, note, source_text)
        payload = self.dataset.add_entry(
            "assistant",
            summary,
            [path],
            tags=tags + ["hippocampus_image"],
            extra={
                "source_path": str(path),
                "ocr": ocr_res.markdown if ocr_res.ok else None,
                "vision": vision_summary or None,
            },
        )
        return self._register_node(path, summary, tags, payload)

    def _ingest_text_file(
        self,
        path: Path,
        tags: List[str],
        note: str,
        snippet: str,
    ) -> HippocampusNodeRecord:
        summary = self._summarise_asset(path, tags, note, snippet)
        payload = self.dataset.add_entry(
            "system",
            summary,
            [],
            tags=tags + ["hippocampus_text"],
            extra={
                "source_path": str(path),
                "preview": snippet[:1024],
            },
        )
        return self._register_node(path, summary, tags, payload)

    def _ingest_binary_file(
        self,
        path: Path,
        tags: List[str],
    ) -> HippocampusNodeRecord:
        try:
            size = path.stat().st_size
        except Exception:
            size = 0
        summary = (
            f"Binary asset captured: {path.name} ({size} bytes). Tags: "
            f"{', '.join(tags) or '(none)'}"
        )
        payload = self.dataset.add_entry(
            "system",
            summary,
            [],
            tags=tags + ["hippocampus_binary"],
            extra={"source_path": str(path), "size": size},
        )
        return self._register_node(path, summary, tags, payload)

    def _extract_text_snippet(self, path: Path) -> Tuple[str, bool]:
        try:
            data = path.read_bytes()
        except Exception as exc:
            self.logger.debug("Failed to read %s: %s", path, exc)
            return "", False
        sample = data[: self._MAX_TEXT_BYTES]
        text = sample.decode("utf-8", errors="ignore")
        if not text:
            return "", False
        printable = sum(1 for ch in text if ch.isprintable() or ch in "\n\r\t")
        ratio = printable / max(1, len(text))
        return text[: self._MAX_TEXT_BYTES], ratio > 0.75

    def _summarise_asset(
        self,
        path: Path,
        tags: Sequence[str],
        note: str,
        source_text: str,
    ) -> str:
        cleaned = source_text.strip()
        if cleaned:
            prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are Hippocampus, the semantic memory graft. "
                        "Produce a concise summary highlighting entities, "
                        "relationships, and potential follow-up questions."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Asset: {path.name}\nTags: {', '.join(tags) or '(none)'}\n"
                        f"Operator note: {note or '(none)'}\n\n"
                        f"Content snippet:\n{cleaned[:4000]}"
                    ),
                },
            ]
            ok, summary, err = self.ollama.chat(
                self.summary_model or DEFAULT_CHAT_MODEL,
                prompt,
            )
            if ok and summary.strip():
                return summary.strip()
            self.logger.debug(
                "Summary fallback for %s due to Ollama error: %s",
                path,
                err,
            )
        fallback = cleaned[:512] if cleaned else ""
        if fallback:
            return fallback.strip()
        return (
            f"Asset {path.name} ingested with tags {', '.join(tags) or '(none)'}."
        )

    def _register_node(
        self,
        path: Path,
        summary: str,
        tags: Sequence[str],
        payload: Dict[str, Any],
    ) -> HippocampusNodeRecord:
        anchor = str(payload.get("anchor") or payload.get("id") or uuid.uuid4().hex)
        metadata = payload.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}
        metadata.setdefault("source_path", str(path))
        record = HippocampusNodeRecord(
            anchor=anchor,
            label=path.name,
            source_path=str(path),
            tags=list(tags),
            summary=summary,
            embedding=payload.get("embedding") or [],
            metadata=metadata,
        )
        brain_payload = record.as_payload()
        brain_payload["core"] = payload
        self.brain_map.register_node(anchor, brain_payload)
        return record

    @staticmethod
    def _shorten_snippet(text: str, limit: int = 240) -> str:
        """Return a compact single-line snippet suitable for status messages."""

        normalized = " ".join(text.split())
        if len(normalized) <= limit:
            return normalized
        return normalized[: limit - 1] + "…"

    def record_transcript_tap(
        self,
        *,
        session_id: str,
        role: str,
        text: str,
    ) -> Dict[str, Any]:
        """Persist a transcript tap via the dataset service and emit metadata.

        The tap stores the raw text inside the Hippocampus dataset with tags that
        capture the originating role and session id. A shortened snippet is
        returned so the caller can display an inline confirmation while keeping
        the full text available through the dataset anchor.
        """

        trimmed = (text or "").strip()
        if not trimmed:
            raise ValueError("Transcript tap requires non-empty text")

        role_label = (role or "unknown").strip().lower() or "unknown"
        tags = ["transcript_tap", f"tap_role:{role_label}"]
        extra = {
            "event": "transcript_tap",
            "session_id": session_id,
            "tap_role": role_label,
            "captured_at": datetime.now(UTC).isoformat(),
        }

        payload = self.dataset.add_entry("system", trimmed, [], tags=tags, extra=extra)
        anchor = str(payload.get("anchor") or payload.get("id") or "")
        snippet = self._shorten_snippet(trimmed)

        self.logger.info(
            "Transcript tap stored",
            extra={
                "event": "transcript_tap",
                "anchor": anchor,
                "session_id": session_id,
                "role": role_label,
            },
        )

        return {
            "anchor": anchor,
            "snippet": snippet,
            "payload": payload,
        }

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


class TerminalHealthState(Enum):
    """Enumerate terminal bridge health states for LED + status handling."""

    OFFLINE = "offline"
    PROBING = "probing"
    READY = "ready"
    FAULT = "fault"


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
    """Renderable chat bubble that also emits taps for memory capture."""

    tapped = Signal(str, str)  # role, raw text snapshot

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
        raw_text: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        self.theme = theme
        self.role = role
        self._raw_text = raw_text if raw_text is not None else text
        self._press_pos: Optional[QPoint] = None
        self.setObjectName("ChatBubbleWidget")
        self.setCursor(Qt.PointingHandCursor)
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

    def mousePressEvent(self, event):  # pragma: no cover - UI interaction
        if event.button() == Qt.LeftButton:
            self._press_pos = event.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):  # pragma: no cover - UI interaction
        try:
            if event.button() == Qt.LeftButton and self._press_pos is not None:
                if (event.pos() - self._press_pos).manhattanLength() <= 4:
                    text = self._raw_text.strip()
                    if text:
                        self.tapped.emit(self.role, text)
        finally:
            self._press_pos = None
            super().mouseReleaseEvent(event)


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
        raw_text: Optional[str] = None,
    ) -> ChatBubbleWidget:
        bubble = ChatBubbleWidget(
            self.theme,
            role,
            text,
            model_name=model_name,
            thinks=thinks,
            images=images,
            raw_text=raw_text,
        )
        self._append_row(role, bubble)
        self._refresh_bubble_styles()
        QTimer.singleShot(0, self._scroll_to_bottom)
        return bubble

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
            if img:
                name = f"paste_{int(time.time())}_{uuid.uuid4().hex[:6]}.png"
                out = agent_images_dir() / name
                ensure_dir(out.parent)
                try:
                    image_module = ensure_pillow("clipboard image paste")
                except OptionalDependencyError as exc:
                    notify_dependency_missing(exc)
                    QMessageBox.warning(self, "Paste Image", exc.user_message)
                else:
                    try:
                        if isinstance(img, QImage):
                            buf = QImage(img).convertToFormat(QImage.Format_RGBA8888)
                            ptr = buf.constBits()
                            ptr.setsize(buf.sizeInBytes())
                            pil_image = image_module.frombytes(
                                "RGBA", (buf.width(), buf.height()), bytes(ptr)
                            )
                        else:
                            raise RuntimeError("Unsupported image type from clipboard")
                        pil_image = pil_image.convert("RGBA")
                        pil_image.save(out, "PNG", optimize=True)
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
        hippocampus_root = ensure_dir(self.session_dir / "hippocampus")
        self.brain_map = BrainMapRegistry(
            hippocampus_root / "brain_map.json",
            logger=logging.getLogger(f"{VD_LOGGER_NAME}.hippocampus"),
        )
        self.hippocampus = HippocampusClient(
            self.dataset,
            self.brain_map,
            self.ollama,
            self.settings,
            logger=logging.getLogger(f"{VD_LOGGER_NAME}.hippocampus"),
        )
        self.pending_images: List[Path] = []
        self.session_notes: List[Dict[str, str]] = self._load_session_notes()
        self._safety_notifier_id: str = ""
        self._approval_widgets: List[ApprovalPromptWidget] = []
        self._task_bus_handles: List[Subscription] = []
        self._loaded_conversation_id: Optional[str] = None
        self._recent_input_references: Deque[Dict[str, str]] = deque(maxlen=10)
        self._logger = logging.getLogger(f"{VD_LOGGER_NAME}.chat")
        self._health_state = TerminalHealthState.OFFLINE
        self._ready_banner_seen = False

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
        self.led.setToolTip(self._health_state_tooltip(self._health_state))
        self.led.set_state(self._LED_COLOR_BY_STATE[self._health_state])
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

    _LED_COLOR_BY_STATE: Dict[TerminalHealthState, str] = {
        TerminalHealthState.OFFLINE: "red",
        TerminalHealthState.PROBING: "yellow",
        TerminalHealthState.READY: "green",
        TerminalHealthState.FAULT: "red",
    }

    def _add_shortcut(self, key: str, fn):
        act = QAction(self); act.setShortcut(QKeySequence(key)); act.triggered.connect(fn); self.addAction(act)

    def _health_state_tooltip(self, state: TerminalHealthState) -> str:
        mapping = {
            TerminalHealthState.OFFLINE: "Bridge offline",
            TerminalHealthState.PROBING: "Bridge running — waiting for ready banner",
            TerminalHealthState.READY: "Bridge ready",
            TerminalHealthState.FAULT: "Bridge reported an error",
        }
        return mapping.get(state, "Bridge status unknown")

    def _interpret_led_state(self, color: str) -> TerminalHealthState:
        normalized = (color or "").strip().lower()
        if normalized == "green":
            return TerminalHealthState.READY
        if normalized == "yellow":
            return TerminalHealthState.PROBING
        return (
            TerminalHealthState.FAULT
            if self.bridge.running()
            else TerminalHealthState.OFFLINE
        )

    def _set_health_state(self, state: TerminalHealthState) -> None:
        if state == self._health_state:
            return

        previous = self._health_state
        self._health_state = state
        self._led_state = self._LED_COLOR_BY_STATE.get(state, "red")
        self.led.set_state(self._led_state)
        self.led.setToolTip(self._health_state_tooltip(state))
        self._refresh_interpreter_toggle_enabled()

        if state == TerminalHealthState.PROBING and previous in {
            TerminalHealthState.OFFLINE,
            TerminalHealthState.FAULT,
        }:
            self._emit_system_notice(
                "[Codex] Bridge warming up — waiting for ready banner."
            )
        elif state == TerminalHealthState.READY:
            if not self._ready_banner_seen:
                self._ready_banner_seen = True
                self._emit_system_notice("[Codex] Ready banner detected. Bridge live.")
        elif state == TerminalHealthState.FAULT and previous != TerminalHealthState.FAULT:
            self._emit_system_notice(
                "[Codex] Bridge error detected. Inspect the console window."
            )
        elif state == TerminalHealthState.OFFLINE:
            self._ready_banner_seen = False

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
        self._set_health_state(self._interpret_led_state(state))

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

    @Slot(str, str)
    def _handle_transcript_tap(self, role: str, text: str) -> None:
        """Persist tapped transcript text through Hippocampus and log a notice."""

        trimmed = (text or "").strip()
        if not trimmed:
            return
        if not hasattr(self, "hippocampus") or not self.hippocampus:
            self._emit_system_notice("[Memory] Hippocampus unavailable; tap ignored.")
            return

        try:
            record = self.hippocampus.record_transcript_tap(
                session_id=self.session_id,
                role=role,
                text=trimmed,
            )
        except Exception as exc:
            self._logger.exception("Transcript tap failed")
            self._emit_system_notice(f"[Memory] Transcript tap failed: {exc}")
            return

        anchor = str(record.get("anchor") or "").strip()
        snippet = record.get("snippet") or trimmed
        references: Optional[List[Dict[str, str]]] = None
        if anchor:
            references = [
                {
                    "type": "hippocampus",
                    "anchor": anchor,
                    "session": self.session_id,
                    "source_role": role,
                }
            ]

        note_lines = [
            f"[Memory] Saved {role} message to Hippocampus.",
        ]
        if anchor:
            note_lines.append(f"Anchor: {anchor[:8]}…")
        note_lines.append("")
        note_lines.append(snippet)
        message = "\n".join(note_lines).strip()

        self._record_message("system", message, [], references=references)
        self.append_signal.emit(ChatMessage("system", message, []))

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
        try:
            image_module = ensure_pillow("image conversion")
        except OptionalDependencyError as exc:
            notify_dependency_missing(exc)
            shutil.copy2(p, out)
        else:
            with image_module.open(p) as im:
                im = im.convert("RGBA")
                im.save(out, "PNG", optimize=True)
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

    def hippocampus_client(self) -> HippocampusClient:
        """Expose the active Hippocampus client for auxiliary widgets."""

        return self.hippocampus

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
        budget = prompt_token_budget(model, headroom_pct) if guard_enabled else 0
        message_tokens = count_tokens(text, model)

        context_entries: List[Tuple[str, int]] = []
        for line in context_lines:
            context_entries.append((line, count_tokens(line, model)))

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
                tokens = count_tokens(payload, model)
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
            self._ready_banner_seen = False
            self._set_health_state(TerminalHealthState.PROBING)
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
            self._set_health_state(TerminalHealthState.OFFLINE)
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
        bubble = self.view.append_message(
            msg.role,
            text,
            model_name=model_name,
            thinks=think_lines,
            images=msg.images,
            raw_text=text,
        )
        bubble.tapped.connect(self._handle_transcript_tap)

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
        self._create_text_file("New PowerShell Script", ".ps1", "Write-Host 'Hello from ACAGi'\n")

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
        "share_limit": RUNTIME_SETTINGS.share_limit,
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
        self.feature_flags = RUNTIME_SETTINGS
        configure_safety_sentinel(self.feature_flags)

        self.settings = _default_settings()
        self.settings.setdefault("share_limit", self.feature_flags.share_limit)
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
        self.setCentralWidget(self.chat)
        self.dataset_dock = DatasetManagerDock(self.chat, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dataset_dock)
        self.dataset_dock.hide()
        self.virtual_desktop_dock = VirtualDesktopDock(
            self.chat,
            self,
            dataset_root=TASKS_DATA_ROOT,
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self.virtual_desktop_dock)
        self.virtual_desktop_dock.hide()
        self.tabifyDockWidget(self.dataset_dock, self.virtual_desktop_dock)
        safety_manager.set_confirmer(self._confirm_risky_command)
        self.status_indicator: QStatusBar = self.statusBar()
        self._refresh_status_bar()

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
        view_menu.addAction(self.dataset_dock.toggleViewAction())
        view_menu.addAction(self.virtual_desktop_dock.toggleViewAction())

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
        if self.feature_flags.auto_approve and self.feature_flags.sandbox == "trusted":
            shared_logger().info(
                "Sentinel auto-approved command under trusted sandbox: %s",
                shlex.join(command),
            )
            return True

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

    def _refresh_status_bar(self) -> None:
        if not hasattr(self, "status_indicator"):
            return
        offline_state = "Offline" if self.feature_flags.offline else "Online"
        sandbox_state = self.feature_flags.sandbox.capitalize()
        limit = self.settings.get("share_limit", self.feature_flags.share_limit)
        policy = self.feature_flags.sentinel_policy.capitalize()
        remote_flag = "Remote bus linked" if self.feature_flags.remote_event_bus else "Local events"
        summary = " • ".join(
            [
                offline_state,
                f"Sandbox: {sandbox_state}",
                f"Share limit: {limit}",
                f"Policy: {policy}",
                remote_flag,
            ]
        )
        self.status_indicator.showMessage(summary)

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
        if hasattr(self, "dataset_dock"):
            self.dataset_dock.set_chat_card(self.chat)

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
            self.desktop = None
            self.setCentralWidget(self.chat)
            if hasattr(self, "dataset_dock"):
                self.dataset_dock.set_chat_card(self.chat)
            if hasattr(self, "virtual_desktop_dock"):
                self.virtual_desktop_dock.set_chat_card(self.chat)
            configure_safety_sentinel(self.feature_flags)
            self._refresh_status_bar()

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
    logger = shared_logger()
    logger.info("ACAGi starting up (pid=%s)", os.getpid())
    for handler in logger.handlers:
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
        logger = BOOT_ENV.refresh()
        logger.info("Workspace override applied: %s", candidate)
        for handler in logger.handlers:
            try:
                handler.flush()
            except Exception:
                continue
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

    _ensure_high_dpi_rounding_policy()

    sys.argv = [sys.argv[0]] + qt_args
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    widget, _ = build_widget()
    widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
