import Codex_Terminal as sct
from PySide6.QtWidgets import QApplication


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_settings_dialog_round_trips_interpreter(monkeypatch):
    _ensure_app()

    class _StubOllama:
        def list_models(self):
            return True, ["stub-model"], "ok"

    monkeypatch.setattr(sct, "OllamaClient", lambda: _StubOllama())

    dialog = sct.SettingsDialog(sct.Theme(), None, _StubOllama(), None)
    try:
        dialog.enable_interpreter.setChecked(True)
        values = dialog.values()
        assert values["enable_interpreter"] is True

        dialog.enable_interpreter.setChecked(False)
        values = dialog.values()
        assert values["enable_interpreter"] is False
    finally:
        dialog.close()


def test_settings_dialog_scan_roots_requires_trusted(monkeypatch, tmp_path):
    _ensure_app()

    class _StubOllama:
        def list_models(self):
            return True, ["stub-model"], "ok"

    monkeypatch.setattr(sct, "OllamaClient", lambda: _StubOllama())

    dialog = sct.SettingsDialog(sct.Theme(), None, _StubOllama(), None)
    try:
        existing_root = tmp_path / "existing"
        existing_root.mkdir()
        dialog.set_scan_roots([str(existing_root)])

        assert dialog.scan_roots_list.count() == 1
        assert dialog.scan_roots_list.isEnabled() is False

        values = dialog.values()
        assert values["codex"]["scan_roots"] == []

        dialog.apply_sandbox_settings({"level": "trusted", "approval_policy": "require_approval"})
        assert dialog.scan_roots_list.isEnabled() is True

        new_root = tmp_path / "other"
        new_root.mkdir()
        monkeypatch.setattr(
            sct.QFileDialog,
            "getExistingDirectory",
            lambda *args, **kwargs: str(new_root),
        )
        dialog._on_add_scan_root()

        values = dialog.values()
        normalized = str(new_root.resolve())
        assert values["codex"]["scan_roots"] == [normalized]
        assert values["scan_roots"] == [normalized]
    finally:
        dialog.close()
