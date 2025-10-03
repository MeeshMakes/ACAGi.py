"""Regression tests for the process error console card."""

from __future__ import annotations

import sys
import textwrap
import time
from pathlib import Path
from typing import List

from PySide6.QtWidgets import QApplication

from errors.process_error_card import ProcessErrorCard
from Virtual_Desktop import Theme


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _drain_events(app: QApplication, deadline: float) -> None:
    while time.time() < deadline:
        app.processEvents()
        time.sleep(0.01)


def test_process_error_card_persists_failure(tmp_path: Path) -> None:
    app = _ensure_app()
    script = tmp_path / "fail.py"
    script.write_text(
        textwrap.dedent(
            """
            import sys
            sys.stderr.write("boom!\\n")
            sys.stderr.flush()
            sys.exit(2)
            """
        ),
        encoding="utf-8",
    )

    records: List = []
    isolation_events: List = []
    closes: List = []

    card = ProcessErrorCard(
        Theme(),
        [sys.executable, str(script)],
        cwd=str(tmp_path),
        record_writer=lambda record: records.append(record),
    )
    card.isolation_requested.connect(lambda message, code: isolation_events.append((message, code)))
    card.close_requested.connect(lambda: closes.append(True))
    card.start()

    deadline = time.time() + 5.0
    while card.is_running and time.time() < deadline:
        app.processEvents()
        time.sleep(0.05)
    _drain_events(app, time.time() + 0.2)

    assert records, "Failure should be persisted through the error dataset helper."
    payload = records[-1]
    assert "boom" in payload.msg
    assert payload.level == "ERROR"
    assert isolation_events and isolation_events[0][1] == 2
    assert closes, "Card should request closure after failure."
    assert "boom" in card._log.toPlainText()
