import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow

from error_console import ErrorConsole, StderrRedirector


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_log_writes_file(tmp_path: Path):
    _ensure_app()
    console = ErrorConsole(tmp_path)
    win = QMainWindow()
    win.addDockWidget(Qt.BottomDockWidgetArea, console)
    console.log("boom")
    files = list(tmp_path.glob("*.log"))
    assert len(files) == 1
    assert "boom" in files[0].read_text(encoding="utf-8")


def test_stderr_redirect(tmp_path: Path):
    _ensure_app()
    console = ErrorConsole(tmp_path)
    redirect = StderrRedirector(console, sys.stderr)
    sys.stderr = redirect
    try:
        print("hello", file=sys.stderr)
    finally:
        sys.stderr = redirect.original
    files = list(tmp_path.glob("*.log"))
    assert files and "hello" in files[-1].read_text(encoding="utf-8")


def test_accepts_parent(tmp_path: Path):
    _ensure_app()
    win = QMainWindow()
    console = ErrorConsole(errors_dir=tmp_path, parent=win)
    win.addDockWidget(Qt.BottomDockWidgetArea, console)
    console.log("boom")
    assert console.parent() is win
