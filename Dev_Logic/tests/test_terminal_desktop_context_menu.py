import json

import Codex_Terminal as sct


def _ensure_app():
    app = sct.QApplication.instance()
    if app is None:
        app = sct.QApplication([])
    return app


def test_terminal_desktop_context_menu_creates_entries(monkeypatch, tmp_path):
    app = _ensure_app()
    monkeypatch.setattr(sct.OllamaClient, "health", lambda self: (True, "OK"))

    workspace = tmp_path / "Terminal Desktop"
    settings_path = tmp_path / "settings.json"

    monkeypatch.setattr(sct, "terminal_desktop_dir", lambda: workspace)
    monkeypatch.setattr(sct, "SETTINGS_JSON", settings_path)

    workspace.mkdir(parents=True, exist_ok=True)

    window, _ = sct.build_widget(embedded=False)
    try:
        desktop = window.desktop
        assert isinstance(desktop, sct.TerminalDesktop)
        canvas = desktop.canvas

        canvas._refresh_icons()
        app.processEvents()

        expectations = [
            (canvas._new_folder_desktop, workspace / "New Folder"),
            (canvas._new_text_desktop, workspace / "New Text File.txt"),
            (canvas._new_markdown_desktop, workspace / "New Markdown File.md"),
            (canvas._new_json_desktop, workspace / "New JSON File.json"),
            (canvas._new_python_desktop, workspace / "New Python File.py"),
            (
                canvas._new_powershell_desktop,
                workspace / "New PowerShell Script.ps1",
            ),
            (canvas._new_zip_desktop, workspace / "New Archive.zip"),
            (
                canvas._new_shortcut_desktop,
                workspace / "New Shortcut.shortcut.json",
            ),
        ]

        for action, expected_path in expectations:
            action()
            for _ in range(5):
                app.processEvents()
            assert expected_path.exists()
            assert str(expected_path) in canvas._icons
    finally:
        window.close()


def test_terminal_desktop_background_persistence_and_fallback(
    monkeypatch, tmp_path
):
    app = _ensure_app()
    monkeypatch.setattr(sct.OllamaClient, "health", lambda self: (True, "OK"))

    workspace = tmp_path / "Terminal Desktop"
    workspace.mkdir(parents=True, exist_ok=True)
    settings_path = tmp_path / "settings.json"

    monkeypatch.setattr(sct, "terminal_desktop_dir", lambda: workspace)
    monkeypatch.setattr(sct, "SETTINGS_JSON", settings_path)

    window, _ = sct.build_widget(embedded=False)
    try:
        desktop = window.desktop
        assert isinstance(desktop, sct.TerminalDesktop)
        image_path = workspace / "wall.png"
        img = sct.QImage(8, 8, sct.QImage.Format_ARGB32)
        img.fill(sct.Qt.white)
        assert img.save(str(image_path))

        cfg = sct.BackgroundConfig(
            mode=sct.BackgroundMode.STATIC,
            source=str(image_path),
            fit=sct.BackgroundFit.FIT,
        )
        desktop.set_background_config(cfg)
        app.processEvents()

        stored = json.loads(settings_path.read_text(encoding="utf-8"))
        node = stored.get("terminal_desktop", {})
        background = node.get("background", {})
        assert background.get("source") == str(image_path)
        assert background.get("mode") == sct.BackgroundMode.STATIC.value
        assert background.get("fit") == sct.BackgroundFit.FIT.value

        missing = workspace / "missing.png"
        desktop.set_background_config(
            sct.BackgroundConfig(
                mode=sct.BackgroundMode.STATIC,
                source=str(missing),
            )
        )
        app.processEvents()
        assert desktop.canvas._bg_manager.active_mode is None
    finally:
        window.close()
