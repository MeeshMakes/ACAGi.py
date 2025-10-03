import json
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow

from tasks.task_panel import TaskPanel


STATUSES = ["Open", "Merged", "Closed", "Cancelled", "Failed", "Deleted"]


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _write_task(path: Path, **overrides):
    payload = {
        "id": overrides.get("id", "tsk_1"),
        "title": overrides.get("title", "Task"),
        "status": overrides.get("status", "open"),
        "created_ts": overrides.get("created_ts", 1_695_000_000.0),
        "updated_ts": overrides.get("updated_ts", 1_695_000_000.0),
        "session_id": overrides.get("session_id", "sess"),
        "source": overrides.get("source", "terminal"),
        "labels": overrides.get("labels", []),
        "diffs": overrides.get("diffs", {"added": 1, "removed": 0}),
        "files": overrides.get("files", []),
        "run_log_path": overrides.get("run_log_path"),
        "codex_conversation_id": overrides.get("codex_conversation_id"),
        "parent_id": overrides.get("parent_id"),
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload) + "\n")


def test_refresh_and_filtering(tmp_path):
    _ensure_app()
    dataset = tmp_path / "tasks.jsonl"
    _write_task(
        dataset,
        id="tsk_open",
        title="Investigate render glitch",
        status="open",
    )
    _write_task(
        dataset,
        id="tsk_merge",
        title="Refactor panel logic",
        status="merged",
        labels=["ui"],
    )
    _write_task(dataset, id="tsk_fail", title="Nightly build", status="failed")

    win = QMainWindow()
    panel = TaskPanel(dataset, win)
    win.addDockWidget(Qt.RightDockWidgetArea, panel)

    assert panel.list.count() == 3

    panel.filter_combo.setCurrentText("Merged")
    assert panel.list.count() == 1

    panel.filter_combo.setCurrentText("All")
    panel.search_edit.setText("panel")
    assert panel.list.count() == 1
    item = panel.list.item(0)
    assert item.data(Qt.UserRole) == "tsk_merge"


@pytest.mark.parametrize("status_label", STATUSES)
def test_status_change_signal(tmp_path, status_label):
    _ensure_app()
    dataset = tmp_path / "tasks.jsonl"
    _write_task(dataset, id="tsk_edit", title="Editable", status="open")

    win = QMainWindow()
    panel = TaskPanel(dataset, win)
    win.addDockWidget(Qt.RightDockWidgetArea, panel)

    # Select first row to populate detail view
    panel.list.setCurrentRow(0)
    emitted: list[tuple[str, str]] = []

    def _capture(task_id: str, status: str) -> None:
        emitted.append((task_id, status))

    panel.status_changed.connect(_capture)

    if status_label == "Open":
        pytest.skip("No change emitted when status remains identical")

    index = panel.status_combo.findText(status_label)
    assert index >= 0
    panel.status_combo.setCurrentIndex(index)
    panel.status_apply.click()

    assert emitted == [("tsk_edit", status_label.lower())]


def test_new_task_signal(tmp_path):
    _ensure_app()
    dataset = tmp_path / "tasks.jsonl"
    _write_task(dataset, id="tsk_edit", title="Editable", status="open")

    win = QMainWindow()
    panel = TaskPanel(dataset, win)
    win.addDockWidget(Qt.RightDockWidgetArea, panel)

    payloads: list[str] = []
    panel.new_taskRequested.connect(payloads.append)

    panel.new_task_input.setText("Document architecture")
    panel.new_task_input.returnPressed.emit()

    assert payloads == ["Document architecture"]


def test_detail_populates_run_log_tail(tmp_path):
    _ensure_app()
    dataset = tmp_path / "tasks.jsonl"
    run_rel = "runs/tsk_log/run.log"
    run_path = tmp_path / run_rel
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text("first\nsecond\nthird\n", encoding="utf-8")
    _write_task(
        dataset,
        id="tsk_log",
        title="Review",
        status="open",
        run_log_path=run_rel,
    )

    win = QMainWindow()
    panel = TaskPanel(dataset, win)
    win.addDockWidget(Qt.RightDockWidgetArea, panel)

    panel.list.setCurrentRow(0)

    log_text = panel.detail_log.toPlainText()
    assert "second" in log_text
    assert "third" in log_text


def test_load_conversation_button_emits_signal(tmp_path):
    _ensure_app()
    dataset = tmp_path / "tasks.jsonl"
    _write_task(
        dataset,
        id="tsk_linked",
        title="Linked",
        status="open",
        codex_conversation_id="conv_123",
    )
    _write_task(dataset, id="tsk_plain", title="Plain", status="open", session_id="")

    win = QMainWindow()
    panel = TaskPanel(dataset, win)
    win.addDockWidget(Qt.RightDockWidgetArea, panel)

    captured: list[tuple[str, str]] = []

    def _capture(task_id: str, conversation_id: str) -> None:
        captured.append((task_id, conversation_id))

    panel.load_conversationRequested.connect(_capture)

    panel.list.setCurrentRow(0)
    QApplication.processEvents()
    assert panel.load_conversation_btn.isEnabled()
    panel.load_conversation_btn.click()
    assert captured == [("tsk_linked", "conv_123")]

    panel.list.setCurrentRow(1)
    QApplication.processEvents()
    assert not panel.load_conversation_btn.isEnabled()
