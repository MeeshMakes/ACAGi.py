"""Validate Windows elevation relaunch argument handling."""

from __future__ import annotations

import ast
import ctypes
import logging
import os
import subprocess
import sys
import types
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    # Pytest can change the working directory during collection; explicitly
    # insert the repository root so ``import ACAGi`` resolves the monolithic
    # entrypoint when tests run from nested paths.
    sys.path.insert(0, str(REPO_ROOT))

ACAGI_SOURCE = (REPO_ROOT / "ACAGi.py").read_text(encoding="utf-8")


def _load_ensure_windows_elevation() -> Callable[[logging.Logger | None], None]:
    """Compile `_ensure_windows_elevation` in isolation for targeted testing."""

    module_ast = ast.parse(ACAGI_SOURCE)
    for node in module_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_ensure_windows_elevation":
            isolated_module = ast.Module(body=[node], type_ignores=[])
            compiled = compile(isolated_module, filename=str(REPO_ROOT / "ACAGi.py"), mode="exec")
            namespace: Dict[str, Any] = {
                "__name__": "test_windows_elevation",
                "ctypes": ctypes,
                "logging": logging,
                "os": os,
                "subprocess": subprocess,
                "sys": sys,
            }
            exec(compiled, namespace)
            return namespace["_ensure_windows_elevation"]

    raise AssertionError("_ensure_windows_elevation function not found")


pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("win"),
    reason="Windows-only behaviour",
)


def _capture_shell32_invocation() -> Tuple[types.SimpleNamespace, Dict[str, Any]]:
    """Create a fake ``shell32`` implementation that records relaunch calls."""

    captured: Dict[str, Any] = {}

    def _is_user_an_admin() -> int:
        """Return ``0`` so the elevation branch executes during the test."""

        return 0

    def _shell_execute(
        hwnd: Any,
        operation: str,
        executable: str,
        parameters: str,
        directory: Any,
        show_cmd: int,
    ) -> int:
        """Record the invocation and emulate a successful relaunch result."""

        captured["args"] = (
            hwnd,
            operation,
            executable,
            parameters,
            directory,
            show_cmd,
        )
        captured["params"] = parameters
        return 33

    fake_shell32 = types.SimpleNamespace(
        IsUserAnAdmin=_is_user_an_admin,
        ShellExecuteW=_shell_execute,
    )
    return fake_shell32, captured


def test_elevation_relaunch_preserves_spaced_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the relaunch command keeps spaced arguments quoted on Windows."""

    fake_shell32, captured = _capture_shell32_invocation()
    monkeypatch.setattr(
        ctypes,
        "windll",
        types.SimpleNamespace(shell32=fake_shell32),
        raising=False,
    )
    monkeypatch.delenv("ACAGI_ELEVATED", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ACAGi.py",
            "--workspace",
            r"C:\\Program Files\\ACAGi Data",
        ],
    )

    logger = logging.getLogger("test.elevation")
    ensure_windows_elevation = _load_ensure_windows_elevation()

    with pytest.raises(SystemExit) as excinfo:
        ensure_windows_elevation(logger)

    assert excinfo.value.code == 0
    expected_params = subprocess.list2cmdline(
        ["--workspace", r"C:\\Program Files\\ACAGi Data"]
    )
    assert captured["params"] == expected_params
    assert captured["args"][1] == "runas"
