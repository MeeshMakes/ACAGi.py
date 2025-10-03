import os

from PySide6.QtWidgets import QApplication, QWidget

import Virtual_Desktop as vd


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _remove_state():
    if os.path.isfile(vd.STATE_PATH):
        os.remove(vd.STATE_PATH)


def _drain_events(app: QApplication) -> None:
    for _ in range(5):
        app.processEvents()


def test_add_card_replaces_previous_card(tmp_path):
    _remove_state()
    app = _ensure_app()
    core = vd.VirtualDesktopCore(workspace=str(tmp_path))
    try:
        first = core.add_card(QWidget(), "First")
        _drain_events(app)
        second = core.add_card(QWidget(), "Second")
        _drain_events(app)
        remaining = core._iter_cards()
        assert remaining == [second]
        assert first not in remaining
    finally:
        core.deleteLater()
        _remove_state()


def test_template_card_reference_cleared_when_replaced(tmp_path):
    _remove_state()
    app = _ensure_app()
    core = vd.VirtualDesktopCore(workspace=str(tmp_path))
    try:
        core.toggle_template_terminal(True)
        _drain_events(app)
        template = core._template_card
        assert template is not None
        replacement = core.add_card(QWidget(), "Replacement")
        _drain_events(app)
        assert core._template_card is None
        assert template not in core._iter_cards()
        assert replacement in core._iter_cards()
    finally:
        core.deleteLater()
        _remove_state()
