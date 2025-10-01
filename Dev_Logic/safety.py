"""Runtime safety guardrails for the Codex Terminal."""

from __future__ import annotations

import builtins
import os
import re
import shlex
import threading
import uuid
from pathlib import Path
from typing import Callable, Dict, Optional, Sequence

__all__ = ["SafetyViolation", "SafetyManager", "manager"]


class SafetyViolation(RuntimeError):
    """Raised when a safety rule blocks an operation."""


class SafetyManager:
    """Coordinates safety guardrails for file writes and shell commands."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
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

    # ------------------------------------------------------------------
    def install_file_guard(self) -> None:
        """Monkey patch ``open`` so we can intercept destructive writes."""

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

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    def set_confirmer(self, callback: Optional[Callable[[str, Sequence[str]], bool]]) -> None:
        with self._lock:
            self._confirmer = callback

    # ------------------------------------------------------------------
    def ensure_command_allowed(self, cmd: Sequence[str]) -> None:
        if not cmd:
            return

        canonical = [str(part) for part in cmd]
        joined = shlex.join(canonical)
        lowered = joined.lower()

        reason = self._match_risky(lowered, canonical)
        if not reason:
            return

        prompt = f"[SAFETY] Confirmation required: {joined}" if reason == "confirm" else f"[SAFETY] {reason}: {joined}"
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

    # ------------------------------------------------------------------
    def _match_risky(self, lowered: str, tokens: Sequence[str]) -> Optional[str]:
        for pattern in self._risk_patterns:
            if pattern.search(lowered):
                return "confirm"

        # Additional heuristic for rm -rf style deletions.
        if not tokens:
            return None

        lowered_tokens = [t.lower() for t in tokens]
        if "rm" in lowered_tokens or any(tok.endswith("rm") for tok in lowered_tokens):
            if self._has_flag(lowered_tokens, "r") and self._has_flag(lowered_tokens, "f"):
                if any(tok == "/" or tok.startswith("/") for tok in lowered_tokens):
                    return "confirm"
        return None

    @staticmethod
    def _has_flag(tokens: Sequence[str], flag: str) -> bool:
        return any(token.startswith("-") and flag in token for token in tokens)

    # ------------------------------------------------------------------
    def _dispatch(self, message: str) -> None:
        with self._lock:
            callbacks = list(self._notifiers.values())
        for cb in callbacks:
            try:
                cb(message)
            except Exception:  # pragma: no cover - defensive
                continue

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
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


manager = SafetyManager()
manager.install_file_guard()
manager.add_protected_path(Path("Agent.md"))
manager.add_protected_directory(Path("errors"))
