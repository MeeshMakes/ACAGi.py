from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt, QEvent, QObject, Signal
from PySide6.QtGui import QKeyEvent, QTextCursor
from PySide6.QtWidgets import QApplication, QWidget

from Codex_Terminal import ChatInput
from repo_reference_helper import RepoReference


class StubCard:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def _convert_to_png(self, path: Path) -> Path:
        return path


@pytest.fixture
def qt_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class DummyHelper(QObject):
    refreshed = Signal()

    def __init__(self, reference: RepoReference):
        super().__init__()
        self._reference = reference

    def suggestions(self, query: str, limit: int = 5):
        return [self._reference]

    def refresh(self) -> None:  # pragma: no cover - not exercised in test
        pass


def test_chat_input_tab_accepts_repo_reference(qt_app):
    workspace = Path(os.environ["CODEX_WORKSPACE"])
    parent = QWidget()
    card = StubCard(workspace)
    input_widget = ChatInput(card, parent)

    # Swap the repo helper for a deterministic stub
    original_helper = input_widget._repo_helper
    original_helper.deleteLater()
    reference = RepoReference(workspace / "docs" / "index.md", "docs/index.md", "file")
    dummy_helper = DummyHelper(reference)
    input_widget._repo_helper = dummy_helper
    dummy_helper.refreshed.connect(input_widget._handle_repo_refresh)

    captured = []
    input_widget.referenceAccepted.connect(lambda payload: captured.append(payload))

    input_widget.setPlainText("docs/in")
    cursor = input_widget.textCursor()
    cursor.movePosition(QTextCursor.End)
    input_widget.setTextCursor(cursor)
    input_widget._update_suggestions()
    qt_app.processEvents()

    event = QKeyEvent(QEvent.KeyPress, Qt.Key_Tab, Qt.NoModifier)
    QApplication.sendEvent(input_widget, event)
    qt_app.processEvents()

    assert input_widget.toPlainText() == "docs/index.md"
    assert captured == [{"path": "docs/index.md", "type": "file"}]
    refs = input_widget.consume_references()
    assert refs == [{"path": "docs/index.md", "type": "file"}]
    assert not input_widget._suggestion_popup.isVisible()

    # Ensure references clear after consumption
    assert input_widget.consume_references() == []
