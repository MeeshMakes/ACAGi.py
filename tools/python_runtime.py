"""Shared helpers for enforcing the supported Python interpreter runtime.

This module provides a centralised place to describe the Python versions the
ACAGi toolchain supports and the optional interpreter override operators can
configure.  Entry points import :func:`ensure_supported_python` before touching
heavy dependencies so version checks and relaunch logic occur consistently.

Configuration hierarchy (highest precedence first):

* ``ACAGI_PYTHON_INTERPRETER`` environment variable – absolute path to the
  preferred interpreter.
* ``ACAGI_PYTHON_RUNTIME_CONFIG`` environment variable – path to a JSON file
  mirroring the default configuration schema.
* ``<workspace>/.codex_agent/config/python-runtime.json`` – persistent config
  co-located with other Codex agent assets; the file is optional.

The JSON schema accepts ``{"python_interpreter": "/path/to/python",
"min_version": "3.10", "max_version": "3.12"}``.  Missing entries fall back to
repository defaults.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Sequence, Tuple

LOGGER = logging.getLogger("acagi.python_runtime")

SUPPORTED_MIN_VERSION: Tuple[int, int, int] = (3, 10, 0)
SUPPORTED_MAX_VERSION: Tuple[int, int, int] = (3, 12, 99)
DEFAULT_CONFIG_FILENAME = "python-runtime.json"
CONFIG_RELATIVE_PATH = Path(".codex_agent") / "config" / DEFAULT_CONFIG_FILENAME
ENV_INTERPRETER = "ACAGI_PYTHON_INTERPRETER"
ENV_CONFIG_PATH = "ACAGI_PYTHON_RUNTIME_CONFIG"
ENV_RELAUNCHED = "ACAGI_RUNTIME_RELAUNCHED"


@dataclass(frozen=True, slots=True)
class PythonRuntimeConfig:
    """Resolved interpreter configuration for the active process."""

    min_version: Tuple[int, int, int]
    max_version: Tuple[int, int, int]
    interpreter_path: Optional[Path]

    def is_version_supported(self, version: Tuple[int, int, int]) -> bool:
        """Return ``True`` when ``version`` falls within the configured bounds."""

        return self.min_version <= version <= self.max_version


def ensure_supported_python(argv: Optional[Sequence[str]] = None) -> None:
    """Validate the running interpreter and relaunch if overrides dictate.

    The helper exits early when the active interpreter matches both the
    supported version range and the configured executable.  When a mismatch is
    detected, the function relaunches the process using :func:`os.execv` where
    possible or spawns a subprocess as a fallback.
    """

    config = _load_config()
    current_version = _version_tuple(sys.version_info)
    current_executable = Path(sys.executable).resolve()
    argv = tuple(sys.argv if argv is None else argv)

    if not config.is_version_supported(current_version):
        _handle_version_mismatch(config, current_version, current_executable, argv)

    if config.interpreter_path is None:
        return

    desired_executable = config.interpreter_path
    if _paths_equal(desired_executable, current_executable):
        return

    if _should_skip_relaunch(desired_executable):
        LOGGER.debug(
            "Detected relaunch loop guard for interpreter %s; continuing with %s",
            desired_executable,
            current_executable,
        )
        return

    _relaunch(desired_executable, argv)


def _handle_version_mismatch(
    config: PythonRuntimeConfig,
    version: Tuple[int, int, int],
    executable: Path,
    argv: Sequence[str],
) -> None:
    """React to a version mismatch according to the available overrides."""

    desired = config.interpreter_path
    version_repr = _format_version(version)
    supported_repr = (
        f"{config.min_version[0]}.{config.min_version[1]}"
        f"–{config.max_version[0]}.{config.max_version[1]}"
    )

    if desired is not None and not _paths_equal(desired, executable):
        LOGGER.warning(
            "Python %s falls outside the supported range %s; relaunching via %s",
            version_repr,
            supported_repr,
            desired,
        )
        _relaunch(desired, argv)

    message = (
        "ACAGi requires a Python interpreter within the supported range "
        f"{supported_repr}. Current runtime reports {version_repr} at "
        f"{executable}. Configure an override via {ENV_INTERPRETER} or the "
        "python-runtime.json configuration file."
    )
    raise RuntimeError(message)


def _load_config() -> PythonRuntimeConfig:
    """Resolve interpreter overrides from the environment and config files."""

    min_version = SUPPORTED_MIN_VERSION
    max_version = SUPPORTED_MAX_VERSION
    interpreter = _read_interpreter_override()

    config_path = _discover_config_path()
    payload: Mapping[str, object] = {}
    if config_path is not None and config_path.exists():
        try:
            payload = _read_json(config_path)
        except Exception:
            LOGGER.exception("Failed to parse python runtime config: %s", config_path)

    if payload:
        min_version = _coerce_version(payload.get("min_version"), fallback=min_version)
        max_version = _coerce_version(payload.get("max_version"), fallback=max_version)
        if interpreter is None:
            interpreter_value = payload.get("python_interpreter")
            interpreter = _coerce_path(interpreter_value)

    config = PythonRuntimeConfig(
        min_version=min_version,
        max_version=max_version,
        interpreter_path=interpreter,
    )

    return config


def _discover_config_path() -> Optional[Path]:
    """Return the config path described by environment variables or defaults."""

    explicit = os.environ.get(ENV_CONFIG_PATH, "").strip()
    if explicit:
        return Path(explicit).expanduser()

    workspace_override = os.environ.get("CODEX_WORKSPACE", "").strip()
    if workspace_override:
        workspace = Path(workspace_override).expanduser()
    else:
        workspace = _default_workspace()
    return workspace / CONFIG_RELATIVE_PATH


def _default_workspace() -> Path:
    """Mirror ACAGi's default workspace resolution for config discovery."""

    return _script_root() / "Agent_Codex_Standalone"


def _script_root() -> Path:
    """Directory containing repository entry points (ACAGi.py, Codex_Terminal.py)."""

    return Path(__file__).resolve().parent.parent


def _read_interpreter_override() -> Optional[Path]:
    """Extract the interpreter override path from the environment."""

    candidate = os.environ.get(ENV_INTERPRETER, "").strip()
    if not candidate:
        return None
    return _coerce_path(candidate)


def _coerce_path(value: object) -> Optional[Path]:
    """Convert ``value`` into a resolved :class:`Path` when possible."""

    if isinstance(value, (str, Path)):
        try:
            return Path(value).expanduser().resolve()
        except OSError:
            return Path(value).expanduser()
    return None


def _coerce_version(value: object, *, fallback: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Normalise version inputs like ``"3.10"`` or ``[3, 11, 2]`` into tuples."""

    if isinstance(value, str):
        parts = value.split(".")
    elif isinstance(value, Sequence):
        parts = [str(item) for item in value]
    else:
        return fallback

    numbers: list[int] = []
    for part in parts:
        if not part:
            continue
        try:
            numbers.append(int(part))
        except ValueError:
            return fallback
        if len(numbers) == 3:
            break

    if not numbers:
        return fallback

    while len(numbers) < 3:
        numbers.append(0)

    return tuple(numbers[:3])  # type: ignore[return-value]


def _read_json(path: Path) -> Mapping[str, object]:
    """Load JSON payload from ``path`` with informative logging."""

    with path.open("r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:
            LOGGER.warning("Invalid JSON in %s: %s", path, exc)
            return {}
    if not isinstance(data, Mapping):
        LOGGER.warning("Python runtime config %s did not contain a mapping", path)
        return {}
    return data


def _version_tuple(info: sys.version_info) -> Tuple[int, int, int]:
    """Normalise :data:`sys.version_info` for tuple comparisons."""

    return info.major, info.minor, info.micro


def _format_version(version: Tuple[int, int, int]) -> str:
    """Render a human-readable version string."""

    major, minor, micro = version
    return f"{major}.{minor}.{micro}"


def _paths_equal(first: Path, second: Path) -> bool:
    """Return ``True`` when two filesystem paths reference the same target."""

    try:
        return first.resolve() == second.resolve()
    except OSError:
        return first == second


def _should_skip_relaunch(desired: Path) -> bool:
    """Guard against relaunch loops when the target interpreter re-invokes us."""

    recorded = os.environ.get(ENV_RELAUNCHED)
    if not recorded:
        return False
    try:
        recorded_path = Path(recorded).resolve()
    except OSError:
        recorded_path = Path(recorded)
    try:
        desired_path = desired.resolve()
    except OSError:
        desired_path = desired
    return recorded_path == desired_path


def _relaunch(executable: Path, argv: Sequence[str]) -> None:
    """Replace the current process with ``executable`` preserving arguments."""

    os.environ[ENV_RELAUNCHED] = str(executable)
    command = [str(executable), *argv]
    LOGGER.info("Relaunching process via %s", executable)
    try:
        os.execv(str(executable), command)
    except OSError:
        LOGGER.debug("os.execv failed; falling back to subprocess", exc_info=True)
        env: MutableMapping[str, str] = dict(os.environ)
        result = subprocess.call(command, env=env)
        raise SystemExit(result)
    raise SystemExit(0)
