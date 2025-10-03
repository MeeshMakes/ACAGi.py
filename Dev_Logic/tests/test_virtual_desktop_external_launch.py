from __future__ import annotations

import os
import sys
import time
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

import Virtual_Desktop as vd
import external_app_card as eac


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_external_shortcut_fallback_permits_user_approved_exec(tmp_path, monkeypatch):
    _ensure_app()

    workspace = tmp_path / "workspace"
    workspace.mkdir()

    external_root = tmp_path / "external"
    external_root.mkdir()
    external_exec = external_root / "tool.exe"
    external_exec.write_text("echo external\n", encoding="utf-8")

    monkeypatch.setattr(vd, "VDSK_ROOT", str(workspace))
    monkeypatch.setattr(vd, "ALLOWLIST", set())

    core = vd.VirtualDesktopCore(workspace=str(workspace))

    shortcut = tmp_path / "app.lnk"
    spec = vd.LaunchSpec(
        argv=[str(external_exec)],
        cwd=str(workspace),
        target_path=str(external_exec),
        original_path=str(shortcut),
    )

    monkeypatch.setattr(vd, "build_launch_spec", lambda path, script_dir: spec, raising=False)
    monkeypatch.setattr(vd, "should_embed_external_app", lambda s, allow: True, raising=False)

    class _StubExternalApp:
        def __init__(self, *args, **kwargs):
            pass

        def start(self) -> bool:
            return False

        def deleteLater(self) -> None:
            pass

    monkeypatch.setattr(vd, "ExternalAppCard", _StubExternalApp, raising=False)

    recorded: dict[str, object] = {}

    def _fake_open(self, launch_spec, title, persist_key, *, allow_external_exec=False):
        recorded["allow_external_exec"] = allow_external_exec
        recorded["spec"] = launch_spec
        recorded["title"] = title
        recorded["persist"] = persist_key
        return None

    monkeypatch.setattr(vd.VirtualDesktopCore, "_open_process_error_card", _fake_open, raising=False)

    try:
        core._load_process_card(str(shortcut), "Test Shortcut")
    finally:
        core.deleteLater()

    assert recorded["allow_external_exec"] is True

    assert isinstance(recorded["spec"], vd.LaunchSpec)
    allow_flag = bool(recorded["allow_external_exec"])

    allowed, detail = vd._validate_process_request(
        recorded["spec"].argv,
        recorded["spec"].cwd,
        allow_flag,
    )
    assert allowed, detail

    blocked, reason = vd._validate_process_request(
        recorded["spec"].argv,
        recorded["spec"].cwd,
        False,
    )
    assert not blocked
    assert "Blocked" in reason


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows only")
def test_external_blend_launch_resolves_association(tmp_path, monkeypatch):
    _ensure_app()

    workspace = tmp_path / "workspace"
    workspace.mkdir()

    blend_path = tmp_path / "scene.blend"
    blend_path.write_text("fake", encoding="utf-8")

    blender_dir = tmp_path / "blender"
    blender_dir.mkdir()
    blender_exe = blender_dir / "blender.exe"
    blender_exe.write_text("", encoding="utf-8")

    monkeypatch.setattr(vd, "VDSK_ROOT", str(workspace), raising=False)
    monkeypatch.setattr(vd, "ALLOWLIST", set(), raising=False)

    core = vd.VirtualDesktopCore(workspace=str(workspace))

    monkeypatch.setattr(eac, "_resolve_associated_executable", lambda _path: str(blender_exe), raising=False)

    observed: dict[str, object] = {}

    def _fake_should_embed(spec, allow):
        observed["embed_spec"] = spec
        assert spec.argv[0] == str(blender_exe)
        assert spec.argv[1] == str(blend_path)
        assert spec.target_path == str(blender_exe)
        return False

    monkeypatch.setattr(vd, "should_embed_external_app", _fake_should_embed, raising=False)

    def _fake_open(self, spec, title, persist_key, *, allow_external_exec=False):
        observed["open_spec"] = spec
        observed["title"] = title
        observed["persist"] = persist_key
        observed["allow_external_exec"] = allow_external_exec
        return None

    monkeypatch.setattr(vd.VirtualDesktopCore, "_open_process_error_card", _fake_open, raising=False)

    try:
        core._load_process_card(str(blend_path), "Scene")
    finally:
        core.deleteLater()

    assert "embed_spec" in observed
    assert "open_spec" in observed

    spec = observed["open_spec"]
    assert isinstance(spec, vd.LaunchSpec)
    assert spec.argv[0] == str(blender_exe)
    assert spec.argv[1] == str(blend_path)
    assert spec.target_path == str(blender_exe)
    assert spec.original_path == str(blend_path)
    assert spec.cwd == str(blender_dir)


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows only")
def test_external_app_card_adopts_child_window(monkeypatch, tmp_path):
    _ensure_app()

    launcher = tmp_path / "launcher.exe"
    child = tmp_path / "child.exe"

    spec = eac.LaunchSpec(
        argv=[str(launcher)],
        cwd=str(tmp_path),
        target_path=str(child),
        original_path=str(launcher),
    )

    monkeypatch.setattr(eac, "_enum_top_level_windows", lambda: [0x1000], raising=False)
    monkeypatch.setattr(eac, "_enum_windows_for_pid", lambda _pid: [], raising=False)

    fallback_hwnd = 0x2000
    fallback_pid = 4242

    def _fake_window_scan(paths, ignored):
        assert 0x1000 in ignored
        normalized = {os.path.normcase(os.path.abspath(p)) for p in paths}
        assert os.path.normcase(os.path.abspath(child)) in normalized
        return fallback_hwnd, fallback_pid

    monkeypatch.setattr(eac, "_find_window_for_executables", _fake_window_scan, raising=False)

    class _ProcessStub:
        def __init__(self, pid: int) -> None:
            self._pid = pid

        def state(self):
            return eac.QProcess.Running

        def processId(self):
            return self._pid

    recorded: dict[str, object] = {}

    def _fake_embed(self, hwnd, *, owner_pid=None):
        recorded["hwnd"] = hwnd
        recorded["pid"] = owner_pid
        self._embedded_hwnd = hwnd
        self._tracked_pid = owner_pid

    monkeypatch.setattr(eac.ExternalAppCard, "_embed_window", _fake_embed, raising=False)

    theme = type("_Theme", (), {})()
    card = eac.ExternalAppCard(theme, spec)
    try:
        card._process = _ProcessStub(1337)
        monkeypatch.setattr(card._watchdog, "start", lambda: recorded.setdefault("watchdog", True), raising=False)

        card._poll_for_window()
    finally:
        card.deleteLater()

    assert recorded.get("hwnd") == fallback_hwnd
    assert recorded.get("pid") == fallback_pid
    assert recorded.get("watchdog") is True
    assert not card._fallback_emitted


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows only")
def test_external_app_card_adopts_after_launcher_exit(monkeypatch, tmp_path):
    _ensure_app()

    launcher = tmp_path / "launcher.exe"
    child = tmp_path / "child.exe"

    spec = eac.LaunchSpec(
        argv=[str(launcher)],
        cwd=str(tmp_path),
        target_path=str(child),
        original_path=str(launcher),
    )

    fallback_hwnd = 0x5000
    fallback_pid = 4243

    monkeypatch.setattr(eac, "_find_main_hwnd", lambda _pid: 0, raising=False)

    def _fake_window_scan(paths, ignored):
        normalized = {os.path.normcase(os.path.abspath(p)) for p in paths}
        assert os.path.normcase(os.path.abspath(child)) in normalized
        return fallback_hwnd, fallback_pid

    monkeypatch.setattr(eac, "_find_window_for_executables", _fake_window_scan, raising=False)

    class _ProcessStub:
        def __init__(self, pid: int) -> None:
            self._pid = pid

        def state(self):
            return eac.QProcess.NotRunning

        def processId(self):
            return self._pid

    recorded: dict[str, object] = {}

    def _fake_embed(self, hwnd, *, owner_pid=None):
        recorded["hwnd"] = hwnd
        recorded["pid"] = owner_pid
        self._embedded_hwnd = hwnd
        self._tracked_pid = owner_pid

    monkeypatch.setattr(eac.ExternalAppCard, "_embed_window", _fake_embed, raising=False)

    theme = type("_Theme", (), {})()
    card = eac.ExternalAppCard(theme, spec)

    try:
        card._process = _ProcessStub(1337)
        card._embed_deadline = time.monotonic() + 5
        finishes: list[tuple[int, str]] = []
        closed: list[bool] = []

        card.process_finished.connect(lambda code, detail: finishes.append((code, detail)))
        card.request_close.connect(lambda: closed.append(True))

        card._on_finished(0, eac.QProcess.ExitStatus.NormalExit)
        assert card._poll_timer.isActive()
        assert card._pending_exit_detail == (0, "Process exited.")

        monkeypatch.setattr(card._watchdog, "start", lambda: recorded.setdefault("watchdog", True), raising=False)

        card._poll_for_window()
        assert recorded.get("watchdog") is True
        assert card._pending_exit_detail == (0, "Process exited.")

        monkeypatch.setattr(card._watchdog, "stop", lambda: recorded.setdefault("watchdog_stop", True), raising=False)

        def _fake_release() -> None:
            recorded.setdefault("released", True)
            card._embedded_hwnd = 0
            card._tracked_pid = None

        monkeypatch.setattr(card, "_release_window", _fake_release, raising=False)
        monkeypatch.setattr(eac._user32, "IsWindow", lambda _hwnd: False, raising=False)
        monkeypatch.setattr(card, "_window_pid", lambda _hwnd: fallback_pid, raising=False)

        card._check_window_alive()
        assert recorded.get("watchdog_stop") is True
        assert recorded.get("released") is True
        assert finishes == [(0, "Process exited.")]
        assert closed and closed[0] is True
        assert card._pending_exit_detail is None
        assert not card._poll_timer.isActive()
    finally:
        card.deleteLater()

    assert recorded.get("hwnd") == fallback_hwnd
    assert recorded.get("pid") == fallback_pid
    assert not card._fallback_emitted


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows only")
def test_external_app_card_shutdown_waits_for_process(monkeypatch, tmp_path):
    _ensure_app()

    launcher = tmp_path / "launcher.exe"
    launcher.write_text("", encoding="utf-8")

    spec = eac.LaunchSpec(
        argv=[str(launcher)],
        cwd=str(tmp_path),
        target_path=str(launcher),
        original_path=str(launcher),
    )

    class _ProcessStub:
        def __init__(self) -> None:
            self.state_value = eac.QProcess.Running
            self.terminate_calls: list[int] = []
            self.kill_calls: list[int] = []
            self.wait_calls: list[int] = []

        def state(self):
            return self.state_value

        def terminate(self):
            self.terminate_calls.append(1)

        def kill(self):
            self.kill_calls.append(1)

        def waitForFinished(self, msec: int) -> bool:
            self.wait_calls.append(msec)
            return self.state_value == eac.QProcess.NotRunning

        def set_state(self, value) -> None:
            self.state_value = value

        def processId(self):
            return 4242

    theme = type("_Theme", (), {})()
    card = eac.ExternalAppCard(theme, spec)

    process = _ProcessStub()
    card._process = process
    card._embedded_hwnd = 0
    card._window_released = False

    release_calls: list[bool] = []
    original_release = card._release_window

    def _tracking_release() -> None:
        release_calls.append(True)
        original_release()

    monkeypatch.setattr(card, "_release_window", _tracking_release, raising=False)

    try:
        card.shutdown()
        assert process.terminate_calls
        assert process.wait_calls
        assert release_calls == []
        assert card._window_released is False

        process.set_state(eac.QProcess.NotRunning)
        card._window_released = False
        card._on_finished(0, eac.QProcess.ExitStatus.NormalExit)
        assert release_calls == [True]
    finally:
        card.deleteLater()


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows only")
def test_external_app_card_discovers_descendant_gui(monkeypatch, tmp_path):
    _ensure_app()

    launcher = tmp_path / "launcher.exe"
    launcher.write_text("", encoding="utf-8")
    gui = tmp_path / "gui.exe"
    gui.write_text("", encoding="utf-8")

    spec = eac.LaunchSpec(
        argv=[str(launcher)],
        cwd=str(tmp_path),
        target_path=str(launcher),
        original_path=str(launcher),
    )

    existing_hwnd = 0x3000
    child_hwnd = 0x4000
    launcher_pid = 4242
    child_pid = 5252

    monkeypatch.setattr(eac, "_enum_top_level_windows", lambda: [existing_hwnd], raising=False)

    theme = type("_Theme", (), {})()
    card = eac.ExternalAppCard(theme, spec)

    recorded_scan: dict[str, object] = {}

    try:
        monkeypatch.setattr(eac, "_enum_top_level_windows", lambda: [existing_hwnd, child_hwnd], raising=False)
        monkeypatch.setattr(eac, "_find_main_hwnd", lambda _pid: 0, raising=False)

        def _fake_window_scan(paths, ignored):
            recorded_scan["paths"] = {os.path.normcase(os.path.abspath(p)) for p in paths}
            recorded_scan["ignored"] = set(ignored)
            return None

        monkeypatch.setattr(eac, "_find_window_for_executables", _fake_window_scan, raising=False)
        monkeypatch.setattr(eac, "_enum_descendant_processes", lambda _pid: {child_pid}, raising=False)

        def _fake_image_path(pid: int) -> str | None:
            if pid == child_pid:
                return str(gui)
            if pid == launcher_pid:
                return str(launcher)
            return None

        monkeypatch.setattr(eac, "_query_process_image_path", _fake_image_path, raising=False)

        def _fake_window_pid(self, hwnd: int) -> int:
            if hwnd == child_hwnd:
                return child_pid
            if hwnd == existing_hwnd:
                return launcher_pid
            return 0

        monkeypatch.setattr(eac.ExternalAppCard, "_window_pid", _fake_window_pid, raising=False)

        class _ProcessStub:
            def __init__(self, pid: int) -> None:
                self._pid = pid

            def state(self):
                return eac.QProcess.Running

            def processId(self):
                return self._pid

        card._process = _ProcessStub(launcher_pid)

        recorded: dict[str, object] = {}

        def _fake_embed(self, hwnd, *, owner_pid=None):
            recorded["hwnd"] = hwnd
            recorded["pid"] = owner_pid
            self._embedded_hwnd = hwnd
            self._tracked_pid = owner_pid

        monkeypatch.setattr(eac.ExternalAppCard, "_embed_window", _fake_embed, raising=False)
        monkeypatch.setattr(card._watchdog, "start", lambda: recorded.setdefault("watchdog", True), raising=False)

        card._poll_for_window()
    finally:
        card.deleteLater()

    assert recorded.get("hwnd") == child_hwnd
    assert recorded.get("pid") == child_pid
    assert recorded.get("watchdog") is True

    gui_path = os.path.normcase(os.path.abspath(str(gui)))
    assert gui_path not in recorded_scan.get("paths", set())
    assert gui_path in card._candidate_executables
    assert not card._fallback_emitted


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows only")
def test_external_app_card_sync_geometry_updates_during_drag(monkeypatch, tmp_path):
    _ensure_app()

    theme = vd.Theme()
    display_card = vd.Card(theme, "Drag Test")
    display_card.resize(320, 220)

    spec = eac.LaunchSpec(
        argv=["tool.exe"],
        cwd=str(tmp_path),
        target_path=str(tmp_path / "tool.exe"),
        original_path=str(tmp_path / "tool.exe"),
    )

    external_card = eac.ExternalAppCard(theme, spec)
    geometry_spy = Mock()
    position_spy = Mock()
    external_card._sync_geometry = geometry_spy  # type: ignore[assignment]
    external_card._sync_embedded_position = position_spy  # type: ignore[assignment]

    external_card.attach_card(display_card)
    geometry_spy.reset_mock()
    position_spy.reset_mock()

    try:
        press = QMouseEvent(
            QEvent.MouseButtonPress,
            QPointF(16, 16),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        move_a = QMouseEvent(
            QEvent.MouseMove,
            QPointF(48, 38),
            Qt.NoButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        move_b = QMouseEvent(
            QEvent.MouseMove,
            QPointF(72, 64),
            Qt.NoButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        release = QMouseEvent(
            QEvent.MouseButtonRelease,
            QPointF(72, 64),
            Qt.LeftButton,
            Qt.NoButton,
            Qt.NoModifier,
        )

        display_card.mousePressEvent(press)
        display_card.mouseMoveEvent(move_a)
        display_card.mouseMoveEvent(move_b)
        display_card.mouseReleaseEvent(release)
    finally:
        for widget in (display_card, external_card):
            widget.deleteLater()
    # The release event schedules one geometry sync after the move completes,
    # and the drag path should already be covered by the mid-drag position
    # sync calls.
    assert geometry_spy.call_count == 1
    assert position_spy.call_count >= 1
