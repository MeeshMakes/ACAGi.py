import os

import pytest
from PySide6.QtCore import QPoint, QRect, QSize, QEvent
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication

import Virtual_Desktop as vd


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _remove_state():
    if os.path.isfile(vd.STATE_PATH):
        os.remove(vd.STATE_PATH)


def test_taskbar_insets_by_side():
    _remove_state()
    app = _ensure_app()
    core = vd.VirtualDesktopCore()
    try:
        for side in ("bottom", "top", "left", "right"):
            core.set_taskbar_side(side, persist=False)
            app.processEvents()
            assert core.taskbar_side() == side
            insets = core.taskbar_insets()
            for key, value in insets.items():
                if key == side:
                    assert value > 0
                else:
                    assert value == 0
    finally:
        core.deleteLater()
        _remove_state()


def test_windows_taskbar_offset_helper(monkeypatch):
    _remove_state()
    app = _ensure_app()
    core = vd.VirtualDesktopCore()
    try:
        core.set_taskbar_side("bottom", persist=False)
        app.processEvents()
        core._last_synced_size = None
        monkeypatch.setattr(
            core,
            "_current_screen_size",
            lambda: QSize(1920, 1080),
        )
        class DummyScreen:
            def __init__(self, avail_height: int):
                self._avail_height = avail_height

            def geometry(self):
                return QRect(0, 0, 1920, 1080)

            def availableGeometry(self):
                return QRect(0, 0, 1920, self._avail_height)

        dummy_screen = DummyScreen(1032)
        monkeypatch.setattr(core, "_current_screen", lambda: dummy_screen)

        monkeypatch.setattr(core, "_is_window_maximized", lambda: True)
        monkeypatch.setattr(core, "_is_borderless_fullscreen", lambda: False)
        monkeypatch.setattr(
            type(core),
            "_native_windows_taskbar_height",
            staticmethod(lambda: 48),
        )
        core._sync_canvas_to_screen()
        assert core.canvas.height() == 1032

        core._last_synced_size = None
        dummy_screen._avail_height = 1040
        monkeypatch.setattr(
            type(core),
            "_native_windows_taskbar_height",
            staticmethod(lambda: 0),
        )
        core._sync_canvas_to_screen()
        assert core.canvas.height() == 1040

        core._last_synced_size = None
        monkeypatch.setattr(core, "_is_window_maximized", lambda: False)
        core._sync_canvas_to_screen()
        assert core.canvas.height() == 1080

        core._last_synced_size = None
        core.set_taskbar_side("top", persist=False)
        app.processEvents()
        monkeypatch.setattr(core, "_is_window_maximized", lambda: True)
        monkeypatch.setattr(core, "_is_borderless_fullscreen", lambda: True)
        core._sync_canvas_to_screen()
        assert core.canvas.height() == 1080
    finally:
        core.deleteLater()
        _remove_state()


def test_start_panel_geometry_all_sides():
    core_rect = QRect(0, 0, 1200, 900)
    thickness = 50
    panel_size = QSize(400, 300)
    taskbar_rects = {
        "bottom": QRect(
            0,
            core_rect.height() - thickness,
            core_rect.width(),
            thickness,
        ),
        "top": QRect(0, 0, core_rect.width(), thickness),
        "left": QRect(0, 0, thickness, core_rect.height()),
        "right": QRect(
            core_rect.width() - thickness,
            0,
            thickness,
            core_rect.height(),
        ),
    }
    start_rects = {
        "bottom": QRect(20, core_rect.height() - thickness + 5, 120, 40),
        "top": QRect(20, 5, 120, 40),
        "left": QRect(5, 60, 120, 40),
        "right": QRect(
            core_rect.width() - thickness + 5,
            60,
            120,
            40,
        ),
    }

    geom_bottom = vd.VirtualDesktopCore._start_panel_geometry_for_side(
        "bottom",
        core_rect,
        taskbar_rects["bottom"],
        start_rects["bottom"],
        panel_size,
    )
    # sanity for QRect creation
    assert geom_bottom.topLeft() == geom_bottom.topLeft()
    assert (
        geom_bottom.y()
        == core_rect.height() - thickness - panel_size.height() + 2
    )

    geom_top = vd.VirtualDesktopCore._start_panel_geometry_for_side(
        "top",
        core_rect,
        taskbar_rects["top"],
        start_rects["top"],
        panel_size,
    )
    assert geom_top.y() == taskbar_rects["top"].bottom() + 2

    geom_left = vd.VirtualDesktopCore._start_panel_geometry_for_side(
        "left",
        core_rect,
        taskbar_rects["left"],
        start_rects["left"],
        panel_size,
    )
    assert geom_left.x() == taskbar_rects["left"].right() + 2

    geom_right = vd.VirtualDesktopCore._start_panel_geometry_for_side(
        "right",
        core_rect,
        taskbar_rects["right"],
        start_rects["right"],
        panel_size,
    )
    expected_x = taskbar_rects["right"].left() - panel_size.width() - 2
    assert geom_right.x() == expected_x
    assert geom_right.width() == panel_size.width()
    assert geom_right.height() == panel_size.height()


def test_start_panel_auto_hides_when_cursor_leaves(monkeypatch):
    _remove_state()
    app = _ensure_app()
    core = vd.VirtualDesktopCore()
    try:
        core.set_taskbar_side("bottom", persist=False)
        app.processEvents()
        core._toggle_start_panel()
        app.processEvents()
        panel = core.start_panel
        assert panel.isVisible()

        panel.enterEvent(QEvent(QEvent.Enter))
        outside = panel.mapToGlobal(QPoint(panel.width() + 50, panel.height() + 50))
        monkeypatch.setattr(QCursor, "pos", staticmethod(lambda: outside))

        panel.leaveEvent(QEvent(QEvent.Leave))
        app.processEvents()
        assert not panel.isVisible()
    finally:
        core.deleteLater()
        _remove_state()


@pytest.mark.parametrize("side", ["bottom", "top", "left", "right"])
def test_start_panel_geometry_matches_taskbar_side(side):
    _remove_state()
    app = _ensure_app()
    core = vd.VirtualDesktopCore()
    try:
        core.set_taskbar_side(side, persist=False)
        app.processEvents()
        core._toggle_start_panel()
        app.processEvents()
        panel = core.start_panel
        assert panel.property("side") == side
        expected = core._compute_start_panel_rect(panel.size())
        assert panel.geometry() == expected

        core._hide_start_panel()
        app.processEvents()
        assert not panel.isVisible()
    finally:
        core.deleteLater()
        _remove_state()
