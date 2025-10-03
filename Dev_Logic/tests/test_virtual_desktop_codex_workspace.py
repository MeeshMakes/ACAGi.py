import os

from PySide6.QtWidgets import QApplication

import Virtual_Desktop as vd


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _DummySignal:
    def __init__(self):
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)

    def emit(self, *args, **kwargs):
        for callback in list(self._callbacks):
            callback(*args, **kwargs)


class _DummyCard:
    def __init__(self):
        self.closed = _DummySignal()


def test_open_codex_terminal_sets_workspace_during_load(tmp_path, monkeypatch):
    _ensure_app()
    script = tmp_path / "Codex_Terminal.py"
    script.write_text("print('codex terminal stub')\n")
    monkeypatch.setenv("CODEX_TERMINAL_PATH", str(script))

    recorded = {}

    def fake_loader(self, path, **kwargs):
        recorded["path"] = path
        recorded["workspace_env"] = os.environ.get("CODEX_WORKSPACE")
        return object()

    monkeypatch.setattr(
        vd.VirtualDesktopCore,
        "_load_python_as_card",
        fake_loader,
        raising=False,
    )

    core = vd.VirtualDesktopCore(workspace=str(tmp_path))
    expected_workspace = vd.workspace_root()

    monkeypatch.setenv("CODEX_WORKSPACE", "before-env")

    core.open_codex_terminal()

    assert recorded["path"] == str(script)
    assert recorded["workspace_env"] == expected_workspace
    assert os.environ.get("CODEX_WORKSPACE") == "before-env"


def test_start_panel_new_agent_selection_restores_environment(
    tmp_path, monkeypatch
):
    _ensure_app()
    script = tmp_path / "Codex_Terminal.py"
    script.write_text("print('codex terminal stub')\n")
    monkeypatch.setenv("CODEX_TERMINAL_PATH", str(script))

    new_workspace = tmp_path / "workspace"
    new_workspace.mkdir()

    monkeypatch.setattr(
        "Virtual_Desktop._non_native_open_dir",
        lambda parent, caption, start_dir: str(new_workspace),
        raising=False,
    )

    card = _DummyCard()
    recorded = {}

    def fake_loader(self, path, **kwargs):
        recorded["path"] = path
        recorded["env"] = os.environ.get("CODEX_WORKSPACE")
        recorded["kwargs"] = kwargs
        return card

    monkeypatch.setattr(
        vd.VirtualDesktopCore,
        "_load_python_as_card",
        fake_loader,
        raising=False,
    )

    core = vd.VirtualDesktopCore(workspace=str(tmp_path))
    panel = core.start_panel

    baseline_env = "baseline-env"
    monkeypatch.setenv("CODEX_WORKSPACE", baseline_env)

    entries = {entry["id"]: entry for entry in panel._app_entries}
    entries["codex-terminal-new"]["callback"]()

    expected_workspace = os.path.abspath(str(new_workspace))
    assert recorded["path"] == str(script)
    assert recorded["env"] == expected_workspace
    expected_key = f"{script}:{expected_workspace}"
    assert recorded["kwargs"]["persist_key"] == expected_key
    expected_tooltip = f"Workspace: {expected_workspace}"
    assert recorded["kwargs"]["task_tooltip"] == expected_tooltip
    assert os.environ.get("CODEX_WORKSPACE") == expected_workspace

    card.closed.emit(card)
    assert os.environ.get("CODEX_WORKSPACE") == baseline_env
