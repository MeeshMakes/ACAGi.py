"""Utilities for loading disk-backed prompt files with overlay support."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Dict, Iterable, Optional

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


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

    # ----- internal helpers -----
    def _load(self, initial: bool = False) -> None:
        base_text = self._read_file(self.base_path)
        if not base_text.strip():
            base_text = self._definition.default
            if initial and self._definition.default and not self.base_path.exists():
                self.base_path.parent.mkdir(parents=True, exist_ok=True)
                self.base_path.write_text(self._definition.default + "\n", encoding="utf-8")
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
_CACHE_LOCK = RLock()


def get_prompt_watcher(slug: str) -> PromptWatcher:
    """Return (and cache) the watcher for *slug*."""

    with _CACHE_LOCK:
        watcher = _PROMPT_CACHE.get(slug)
        if watcher is None:
            definition = _PROMPT_DEFINITIONS.get(slug)
            if definition is None:
                raise KeyError(f"Unknown prompt slug: {slug}")
            watcher = PromptWatcher(definition)
            _PROMPT_CACHE[slug] = watcher
        return watcher


def prompt_text(slug: str) -> str:
    """Convenience wrapper that returns the combined text for *slug*."""

    return get_prompt_watcher(slug).text()


def iter_prompt_definitions() -> Iterable[PromptDefinition]:
    """Iterate over known prompt definitions in a stable order."""

    for slug in sorted(_PROMPT_DEFINITIONS.keys()):
        yield _PROMPT_DEFINITIONS[slug]
