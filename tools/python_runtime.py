"""Interpreter normalization helper for ACAGi entrypoints.

This module centralises the logic required to ensure each launcher runs under
an operator-configured Python runtime. Entry scripts import this helper before
performing heavyweight imports so they can re-exec themselves under the desired
interpreter when the active process does not match the declared expectations.

Configuration sources are intentionally flexible:

* Environment variables provide the highest priority override:
  - ``ACAGI_PYTHON_EXECUTABLE`` – absolute path to the preferred interpreter.
  - ``ACAGI_PYTHON_VERSION`` – dotted version string (e.g. ``3.11``).
* Configuration files can be stored inside the Codex workspace config folder.
  The helper searches for ``python_runtime.json`` (JSON object) or
  ``python_runtime.ini`` (``[python]`` section) beneath
  ``<workspace>/.codex_agent/config``. The workspace defaults to the
  repository's ``Agent_Codex_Standalone`` directory but respects the
  ``CODEX_WORKSPACE`` override used throughout the project.

When a mismatch is detected the helper relaunches the current script using the
preferred interpreter, forwarding ``sys.argv`` verbatim. A guard environment
flag prevents infinite recursion if the new interpreter still fails to satisfy
the requested constraints; in that scenario the helper emits a warning and
continues with the already-running runtime so operators can investigate.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple


LOGGER = logging.getLogger("acagi.python_runtime")
RELAUNCH_FLAG = "ACAGI_INTERPRETER_RELAUNCHED"
EXECUTABLE_ENV = "ACAGI_PYTHON_EXECUTABLE"
VERSION_ENV = "ACAGI_PYTHON_VERSION"
CONFIG_ENV = "ACAGI_PYTHON_CONFIG"
CONFIG_BASENAMES = ("python_runtime.json", "python_runtime.ini")


@dataclass(frozen=True)
class RuntimePreference:
    """Operator-declared interpreter requirements."""

    executable: Optional[Path]
    version: Optional[Tuple[int, ...]]

    def requested(self) -> bool:
        """Return ``True`` when any explicit preference has been provided."""

        return self.executable is not None or self.version is not None


def ensure_desired_interpreter(script_hint: Optional[str] = None) -> None:
    """Re-execute the current process under the configured interpreter.

    Parameters
    ----------
    script_hint:
        Optional path to the script performing the import. This improves
        logging context when multiple entrypoints coexist.
    """

    preference = _gather_preferences()
    if not preference.requested():
        LOGGER.debug("No interpreter preference declared; continuing in-place.")
        return

    mismatch = _describe_mismatch(preference)
    if not mismatch:
        LOGGER.debug("Interpreter already satisfies configured requirements.")
        return

    if os.environ.get(RELAUNCH_FLAG) == "1":
        LOGGER.warning(
            "Interpreter mismatch persists after relaunch attempt: %s", mismatch
        )
        return

    LOGGER.info(
        "Interpreter mismatch detected (%s). Relaunching %s under %s.",
        mismatch,
        script_hint or Path(sys.argv[0]).name,
        preference.executable or preference.version,
    )
    _relaunch(preference)


def _gather_preferences() -> RuntimePreference:
    """Collect interpreter expectations from environment and configuration."""

    executable = _executable_from_env()
    version = _version_from_env()

    config = _load_config_preferences()
    executable = executable or config.get("executable")
    version = version or config.get("version")

    return RuntimePreference(executable=executable, version=version)


def _executable_from_env() -> Optional[Path]:
    raw = os.environ.get(EXECUTABLE_ENV, "").strip()
    if not raw:
        return None
    candidate = Path(raw)
    if candidate.exists():
        return candidate
    LOGGER.warning(
        "Preferred interpreter %s from %s does not exist.", raw, EXECUTABLE_ENV
    )
    return None


def _version_from_env() -> Optional[Tuple[int, ...]]:
    raw = os.environ.get(VERSION_ENV, "").strip()
    return _parse_version(raw)


def _parse_version(value: str) -> Optional[Tuple[int, ...]]:
    if not value:
        return None
    parts = []
    for piece in value.split("."):
        piece = piece.strip()
        if not piece:
            continue
        if not piece.isdigit():
            LOGGER.warning("Ignoring non-numeric version component: %s", piece)
            return None
        parts.append(int(piece))
    if not parts:
        return None
    return tuple(parts)


def _load_config_preferences() -> dict[str, Optional[Path | Tuple[int, ...]]]:
    executable: Optional[Path] = None
    version: Optional[Tuple[int, ...]] = None

    for path in _config_candidates():
        if not path.exists():
            continue
        try:
            payload = _read_config_file(path)
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.warning("Failed to parse interpreter config %s: %s", path, exc)
            continue

        raw_exec = payload.get("executable") or payload.get("path")
        raw_version = payload.get("version") or payload.get("python_version")

        if raw_exec and not executable:
            candidate = Path(raw_exec)
            if candidate.exists():
                executable = candidate
            else:
                LOGGER.warning(
                    "Configured interpreter %s from %s does not exist.",
                    raw_exec,
                    path,
                )
        if raw_version and not version:
            parsed = _parse_version(str(raw_version))
            if parsed:
                version = parsed
        if executable and version:
            break

    return {"executable": executable, "version": version}


def _config_candidates() -> Iterable[Path]:
    """Yield plausible configuration file locations in priority order."""

    env_override = os.environ.get(CONFIG_ENV, "").strip()
    if env_override:
        yield Path(env_override)

    workspace = _workspace_root()
    config_root = workspace / ".codex_agent" / "config"
    for basename in CONFIG_BASENAMES:
        yield config_root / basename


def _workspace_root() -> Path:
    override = os.environ.get("CODEX_WORKSPACE", "").strip()
    if override:
        try:
            return Path(override).expanduser().resolve()
        except Exception:
            return Path(override).expanduser()
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "Agent_Codex_Standalone"


def _read_config_file(path: Path) -> dict[str, str]:
    """Parse ``path`` supporting JSON and INI payloads."""

    suffix = path.suffix.lower()
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
        raise ValueError("python_runtime.json must contain a JSON object")

    if suffix in {".ini", ".cfg"}:
        import configparser

        parser = configparser.ConfigParser()
        with path.open("r", encoding="utf-8") as handle:
            parser.read_file(handle)
        if parser.has_section("python"):
            return {key: parser.get("python", key) for key in parser["python"]}
        raise ValueError("python_runtime.ini missing [python] section")

    raise ValueError(f"Unsupported interpreter config format: {path}")


def _describe_mismatch(preference: RuntimePreference) -> str:
    """Return a human-readable mismatch description or empty string."""

    reasons: list[str] = []

    if preference.executable:
        current = Path(sys.executable)
        try:
            same_file = current.resolve() == preference.executable.resolve()
        except Exception:
            same_file = current == preference.executable
        if not same_file:
            reasons.append(
                f"expected executable {preference.executable}, got {current}"
            )

    if preference.version:
        actual = sys.version_info
        desired = preference.version
        actual_tuple = (actual.major, actual.minor, actual.micro)
        if not _version_matches(actual_tuple, desired):
            readable = ".".join(str(component) for component in desired)
            current_str = ".".join(str(part) for part in actual_tuple)
            reasons.append(f"expected version {readable}, got {current_str}")

    return "; ".join(reasons)


def _version_matches(actual: Sequence[int], desired: Sequence[int]) -> bool:
    for index, component in enumerate(desired):
        if index >= len(actual):
            return False
        if actual[index] != component:
            return False
    return True


def _relaunch(preference: RuntimePreference) -> None:
    executable = preference.executable
    if not executable and preference.version:
        executable = _locate_interpreter_for_version(preference.version)

    if not executable:
        LOGGER.warning(
            "Unable to identify interpreter matching requested version %s; "
            "continuing with current runtime.",
            preference.version,
        )
        return

    command = [str(executable), *sys.argv]
    env = os.environ.copy()
    env[RELAUNCH_FLAG] = "1"

    try:
        completed = subprocess.run(command, env=env, check=False)
    except OSError as exc:
        LOGGER.error("Failed to relaunch using %s: %s", executable, exc)
        return

    sys.exit(completed.returncode)


def _locate_interpreter_for_version(version: Sequence[int]) -> Optional[Path]:
    """Attempt to discover an interpreter that matches *version*."""

    candidates: list[str] = []
    if version:
        major = version[0]
        minor = version[1] if len(version) > 1 else None
        if minor is not None:
            candidates.append(f"python{major}.{minor}")
        candidates.append(f"python{major}")
    candidates.append("python3")
    candidates.append("python")

    for name in candidates:
        resolved = shutil.which(name)
        if not resolved:
            continue
        path = Path(resolved)
        interpreter_version = _probe_interpreter_version(path)
        if not interpreter_version:
            continue
        if _version_matches(interpreter_version, version):
            return path
    return None


def _probe_interpreter_version(executable: Path) -> Optional[Tuple[int, ...]]:
    """Query *executable* for its version information."""

    probe_script = (
        "import json, sys\n"
        "info = sys.version_info\n"
        "print(json.dumps({'major': info.major, 'minor': info.minor, "
        "'micro': info.micro}))"
    )
    try:
        completed = subprocess.run(
            [str(executable), "-c", probe_script],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError:
        return None

    if completed.returncode != 0:
        return None

    try:
        payload = json.loads(completed.stdout.strip())
    except json.JSONDecodeError:
        return None

    major = payload.get("major")
    minor = payload.get("minor")
    micro = payload.get("micro")
    if any(not isinstance(value, int) for value in (major, minor, micro)):
        return None

    return (major, minor, micro)


if __name__ == "__main__":  # pragma: no cover - manual smoke test helper
    ensure_desired_interpreter()
