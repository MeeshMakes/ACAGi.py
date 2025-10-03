import json
import sys

from PySide6.QtWidgets import QApplication

from editor.card import CommandResult, EditorCard


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_editor_card_generates_summaries(tmp_path):
    _ensure_app()
    document = tmp_path / "architecture.md"
    document.write_text(
        "Overview\n\n"
        "Intro paragraph.\n\n"
        "Section One\n\n"
        "Alpha body.\n\n"
        "Section Two:\n\n"
        "Beta body.\n",
        encoding="utf-8",
    )

    class StubClient:
        def __init__(self):
            self.calls = 0
            self.responses = [
                "- Overview summary",
                "- Alpha summary",
                "- Beta summary",
            ]

        def chat(self, model, messages, images=None):
            idx = min(self.calls, len(self.responses) - 1)
            response = self.responses[idx]
            self.calls += 1
            return True, response, ""

    card = EditorCard(initial_path=str(document), client=StubClient())
    card.summarize_document()

    assert card.segment_list.count() == 3
    assert card.report_output.toPlainText()

    card.segment_list.setCurrentRow(2)
    QApplication.processEvents()

    summary_text = card.segment_summary.toPlainText()
    assert "Beta summary" in summary_text

    cursor_line = card.editor.textCursor().blockNumber() + 1
    assert cursor_line == card._summaries[2].segment.start_line

    report_path = tmp_path / "architecture.logic-summary.md"
    assert report_path.exists()
    report = report_path.read_text(encoding="utf-8")
    assert "editor://architecture.md?line" in report


def test_editor_card_chat_and_notes(tmp_path):
    _ensure_app()
    document = tmp_path / "example.py"
    document.write_text("print('hi')\n", encoding="utf-8")

    card = EditorCard(
        initial_path=str(document),
        client=None,
        storage_root=tmp_path / "mem",
    )

    card.chat_input.setPlainText("Need help")
    card._send_chat_message()

    assert card.chat_log_path.exists()
    log_payload = [
        json.loads(line)
        for line in card.chat_log_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert log_payload and log_payload[0]["content"] == "Need help"

    card.editor.selectAll()
    card._pin_editor_selection()

    assert card.notes_path.exists()
    notes_data = json.loads(card.notes_path.read_text(encoding="utf-8"))
    assert isinstance(notes_data, list) and notes_data[0]["source"] == "editor"


def test_editor_card_highlights_run_errors(tmp_path):
    _ensure_app()
    script = tmp_path / "script.py"
    script.write_text("print('hi')\n", encoding="utf-8")

    card = EditorCard(initial_path=str(script), storage_root=tmp_path / "mem")
    card._prepare_run_output()

    stderr = f"{script}:1: RuntimeError"
    result = CommandResult(
        label="Run",
        command=[sys.executable, str(script)],
        returncode=1,
        stdout="",
        stderr=stderr,
    )

    card._handle_command_result(result)

    output_html = card.run_output.toHtml()
    assert "stderr-0" in output_html
    assert card._output_link_map["stderr-0"].line == 1
    highlights = [
        sel
        for sel in card.editor.extraSelections()
        if sel.format.background().color().red() > 200
    ]
    assert highlights
