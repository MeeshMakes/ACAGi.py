import os
import shutil
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from Virtual_Desktop import (
    _fallback_icon_for_path,
    _icon_for_path,
    Card,
    Taskbar,
    Theme,
)


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific icon extraction")
def test_windows_executable_icon_native():
    _ensure_app()
    source = Path(sys.executable)
    if not source.exists():
        pytest.skip("Python executable unavailable")
    workspace = Path(os.environ["CODEX_WORKSPACE"]) / "icon_tests"
    workspace.mkdir(parents=True, exist_ok=True)
    exe_path = workspace / "sample_launch.exe"
    shutil.copyfile(source, exe_path)
    try:
        icon, native = _icon_for_path(exe_path)
        assert native is True
        assert icon is not None and not icon.isNull()
    finally:
        exe_path.unlink(missing_ok=True)


def test_shortcut_icon_fallback():
    _ensure_app()
    workspace = Path(os.environ["CODEX_WORKSPACE"]) / "icon_tests"
    workspace.mkdir(parents=True, exist_ok=True)
    shortcut = workspace / "workspace_link.lnk"
    shortcut.write_bytes(b"dummy shortcut payload")
    try:
        icon, native = _icon_for_path(shortcut)
        assert icon is not None and not icon.isNull()
        if sys.platform != "win32":
            fallback = _fallback_icon_for_path(shortcut)
            assert icon.cacheKey() == fallback.cacheKey()
            assert native is False
    finally:
        shortcut.unlink(missing_ok=True)


def test_taskbar_uses_card_icon_metadata():
    _ensure_app()
    theme = Theme()
    card = Card(theme, "Process")
    icon, _ = _icon_for_path(Path(__file__))
    card.set_task_metadata("process-card", icon, "Process card")
    taskbar = Taskbar(theme)
    try:
        taskbar.add_task(card)
        group = taskbar._groups.get("process-card")
        assert group is not None
        btn_icon = group.button.icon()
        assert not btn_icon.isNull()
        assert btn_icon.cacheKey() == icon.cacheKey()
    finally:
        card.deleteLater()
        taskbar.deleteLater()
        QApplication.processEvents()
