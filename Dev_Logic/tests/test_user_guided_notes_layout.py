import shutil

import pytest
from PySide6.QtWidgets import QApplication

from User_Guided_Notes import NoteTab, UserGuidedNotesWidget, UserGuidedNotesWindow


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _cleanup_widget_notes(widget: UserGuidedNotesWidget) -> None:
    tab = widget.tabs.widget(0)
    if isinstance(tab, NoteTab):
        shutil.rmtree(tab.meta.paths.root, ignore_errors=True)


def _assert_font_is_smaller(original_font, new_font) -> None:
    app_point = original_font.pointSizeF()
    widget_point = new_font.pointSizeF()
    if app_point > 0 and widget_point > 0:
        assert widget_point == pytest.approx(max(app_point - 1.0, 1.0))
    else:
        app_pixel = original_font.pixelSize()
        widget_pixel = new_font.pixelSize()
        if app_pixel > 0 and widget_pixel > 0:
            assert widget_pixel == max(app_pixel - 1, 1)


def test_embedded_widget_uses_compact_metrics():
    app = _ensure_app()
    baseline_font = app.font()
    widget = UserGuidedNotesWidget(embedded=True)
    try:
        min_size = widget.minimumSize()
        assert min_size.width() == 520
        assert min_size.height() == 360

        _assert_font_is_smaller(baseline_font, widget.font())

        tab = widget.tabs.widget(0)
        assert isinstance(tab, NoteTab)
        style = tab.styleSheet()
        assert "#010409" in style
        assert "#f6f8fa" in style
    finally:
        _cleanup_widget_notes(widget)
        widget.deleteLater()


def test_standalone_window_uses_compact_defaults():
    app = _ensure_app()
    baseline_font = app.font()
    window = UserGuidedNotesWindow()
    try:
        size = window.size()
        assert size.width() == 1100
        assert size.height() == 700

        _assert_font_is_smaller(baseline_font, window.font())

        tab = window.widget.tabs.widget(0)
        assert isinstance(tab, NoteTab)
        style = tab.styleSheet()
        assert "#010409" in style
        assert "#f6f8fa" in style
    finally:
        _cleanup_widget_notes(window.widget)
        window.close()
        window.deleteLater()


def test_detach_toggle_updates_text_state():
    _ensure_app()
    widget = UserGuidedNotesWidget(embedded=True)
    try:
        button = widget.top_strip.detach_btn
        assert button.text() == "Pop Out"
        widget.apply_embedded_state(False)
        assert button.text() == "Dock"
        widget.apply_embedded_state(True)
        assert button.text() == "Pop Out"
    finally:
        _cleanup_widget_notes(widget)
        widget.deleteLater()


def test_detach_and_redock_signals_emit_per_mode():
    _ensure_app()
    widget = UserGuidedNotesWidget(embedded=True)
    detach_events = []
    redock_events = []
    widget.request_detach.connect(lambda payload: detach_events.append(payload))
    widget.request_redock.connect(lambda payload: redock_events.append(payload))
    try:
        widget.top_strip.detach_btn.click()
        assert detach_events == [widget]
        assert redock_events == []

        widget.apply_embedded_state(False)
        widget.top_strip.detach_btn.click()
        assert detach_events == [widget]
        assert redock_events == [widget]
    finally:
        _cleanup_widget_notes(widget)
        widget.deleteLater()
