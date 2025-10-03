import math
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


def test_card_scale_resizes_existing_cards(tmp_path):
    _remove_state()
    app = _ensure_app()
    core = vd.VirtualDesktopCore(workspace=str(tmp_path))
    try:
        card = core.add_card(QWidget(), "Sample")
        app.processEvents()
        expected_default = max(
            vd.MIN_CARD_WIDTH,
            int(round(vd.BASE_CARD_WIDTH * core.card_scale())),
        )
        assert math.isclose(card.width(), expected_default, abs_tol=3)
        scale_target = 0.75
        core.set_card_scale(scale_target)
        app.processEvents()
        scaled_width = max(
            vd.MIN_CARD_WIDTH,
            int(round(vd.BASE_CARD_WIDTH * scale_target)),
        )
        assert math.isclose(card.width(), scaled_width, abs_tol=3)
    finally:
        core.deleteLater()
        _remove_state()


def test_restore_geometry_respects_scale(tmp_path):
    _remove_state()
    app = _ensure_app()
    core = vd.VirtualDesktopCore(workspace=str(tmp_path))
    try:
        first = core.add_card(QWidget(), "One")
        first.set_persist_tag("test-tag")
        vd._save_card_geom(first, "pytest", "test-tag")
        app.processEvents()
        core.set_card_scale(0.7)
        second = core.add_card(QWidget(), "Two")
        second.set_persist_tag("test-tag")
        vd._restore_card_geom(second, "pytest", "test-tag")
        app.processEvents()
        expected_width = max(
            vd.MIN_CARD_WIDTH,
            int(round(vd.BASE_CARD_WIDTH * 0.7)),
        )
        assert math.isclose(second.width(), expected_width, abs_tol=3)
    finally:
        core.deleteLater()
        _remove_state()
