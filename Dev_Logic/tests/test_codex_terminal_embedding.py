import copy
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QApplication

import Codex_Terminal as sct


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _patch_transit(monkeypatch, target, settings_path=None):
    def _transit_dir():
        target.mkdir(parents=True, exist_ok=True)
        return target

    monkeypatch.setattr(sct, "transit_dir", _transit_dir)
    monkeypatch.setattr(sct, "_legacy_transit_candidates", lambda: [])
    if settings_path is not None:
        monkeypatch.setattr(sct, "SETTINGS_JSON", settings_path)


def test_embedded_build_widget_uses_chat_card(monkeypatch, tmp_path):
    _ensure_app()
    monkeypatch.setattr(sct.OllamaClient, "health", lambda self: (True, "OK"))
    target = tmp_path / "Terminal Desktop"
    _patch_transit(monkeypatch, target, tmp_path / "settings.json")

    window, _ = sct.build_widget(embedded=True)
    try:
        central = window.centralWidget()
        assert isinstance(central, sct.ChatCard)
        assert central is window.chat
        assert window.desktop is None
    finally:
        window.close()


def test_standalone_build_widget_creates_terminal_desktop_dir(
    monkeypatch, tmp_path,
):
    _ensure_app()
    monkeypatch.setattr(sct.OllamaClient, "health", lambda self: (True, "OK"))

    target = tmp_path / "Terminal Desktop"
    _patch_transit(monkeypatch, target, tmp_path / "settings.json")

    window, _ = sct.build_widget(embedded=False)
    try:
        assert target.exists() and target.is_dir()
        central = window.centralWidget()
        assert isinstance(central, sct.TerminalDesktop)
    finally:
        window.close()


def test_terminal_desktop_first_run_centers_proxy(monkeypatch):
    app = _ensure_app()
    monkeypatch.setattr(sct.OllamaClient, "health", lambda self: (True, "OK"))
    target = Path(tempfile.mkdtemp()) / "Terminal Desktop"
    settings_path = target.parent / "settings.json"
    _patch_transit(monkeypatch, target, settings_path)

    initial_settings = copy.deepcopy(sct.DEFAULT_SETTINGS)
    initial_settings["terminal_desktop"] = {
        "width": 980,
        "height": 620,
        "x": -1,
        "y": -1,
    }

    monkeypatch.setattr(sct, "load_codex_settings", lambda: initial_settings)

    saved = []

    def _capture(settings):
        saved.append(copy.deepcopy(settings))
        initial_settings.update(settings)

    monkeypatch.setattr(sct, "save_codex_settings", _capture)

    window, _ = sct.build_widget(embedded=False)
    try:
        window.show()
        desktop = window.desktop
        assert isinstance(desktop, sct.TerminalDesktop)

        for _ in range(50):
            app.processEvents()
            if desktop.canvas.width() > 0 and desktop.canvas.height() > 0:
                break
        else:
            raise AssertionError("canvas size did not initialize")

        for _ in range(10):
            app.processEvents()

        geom = desktop.proxy.geometry()
        canvas_w = desktop.canvas.width()
        canvas_h = desktop.canvas.height()
        assert canvas_w > 0 and canvas_h > 0

        expected_x = max(0, (canvas_w - geom.width()) // 2)
        expected_y = max(0, (canvas_h - geom.height()) // 2)
        assert geom.x() == expected_x
        assert geom.y() == expected_y

        assert saved
        persisted = saved[-1]["terminal_desktop"]
        assert persisted["x"] == expected_x
        assert persisted["y"] == expected_y
    finally:
        window.close()
