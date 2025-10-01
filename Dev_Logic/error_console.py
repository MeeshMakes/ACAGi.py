from __future__ import annotations

import io
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QTextEdit, QWidget


class ErrorConsole(QDockWidget):
    """Dockable console to display and persist error messages."""

    def __init__(self, errors_dir: Path | str = "errors", parent: Optional[QWidget] = None):
        super().__init__("Errors", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self._text = QTextEdit(self)
        self._text.setReadOnly(True)
        self.setWidget(self._text)
        self.errors_dir = Path(errors_dir)
        self.errors_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
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
    """File-like object that sends writes to the ErrorConsole."""

    def __init__(self, console: ErrorConsole, original):
        self.console = console
        self.original = original
        self._buffer = ""

    def write(self, s: str) -> int:  # type: ignore[override]
        self.original.write(s)
        self._buffer += s
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                self.console.log(line)
        return len(s)

    def flush(self) -> None:  # type: ignore[override]
        if self._buffer.strip():
            self.console.log(self._buffer)
            self._buffer = ""
        self.original.flush()


def log_exception(console: ErrorConsole, exc_type, exc, tb) -> None:
    """Format and log an exception using the provided console."""
    text = "".join(traceback.format_exception(exc_type, exc, tb))
    console.log(text)
