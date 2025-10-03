import logging
import sys
import types

import pytest

pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("win"),
    reason="External app embedding is only available on Windows.",
)


def _ensure_qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_shutdown_terminates_tracked_process_tree(monkeypatch):
    pytest.importorskip("PySide6")

    """Ensure orphaned external processes are terminated when the launcher is gone."""

    _ensure_qapp()

    import external_app_card as card

    class _StubSignal:
        def __init__(self):
            self._callbacks = []

        def connect(self, callback):
            self._callbacks.append(callback)

        def emit(self, *args, **kwargs):
            for callback in list(self._callbacks):
                callback(*args, **kwargs)

    class _StubTimer:
        def __init__(self, parent=None):
            self.timeout = _StubSignal()
            self._active = False

        def setInterval(self, _interval):
            return None

        def start(self):
            self._active = True

        def stop(self):
            self._active = False

        def isActive(self):
            return self._active

    class _StubProcess:
        NotRunning = 0
        Running = 1

        def __init__(self, *_, **__):
            self._state = self.NotRunning
            self.finished = _StubSignal()
            self.errorOccurred = _StubSignal()
            self._program = ""
            self._args = []
            self._cwd = ""

        def setProgram(self, program):
            self._program = program

        def setArguments(self, args):
            self._args = list(args)

        def setWorkingDirectory(self, cwd):
            self._cwd = cwd

        def start(self, program, args):
            self._program = program
            self._args = list(args)
            self._state = self.Running

        def waitForStarted(self, _timeout):
            return True

        def state(self):
            return self._state

        def terminate(self):
            self._state = self.NotRunning

        def waitForFinished(self, _timeout):
            self._state = self.NotRunning
            return True

        def kill(self):
            self._state = self.NotRunning

        def errorString(self):
            return ""

    monkeypatch.setattr(card, "QProcess", _StubProcess)
    monkeypatch.setattr(card, "QTimer", _StubTimer)

    spec = card.LaunchSpec(
        argv=["C:/dummy-launcher.exe"],
        cwd="C:/",
        target_path="C:/dummy-launcher.exe",
        original_path="C:/dummy-launcher.exe",
    )

    theme = types.SimpleNamespace(header_fg="#fff")

    toasts = []

    def _toast(message, *, kind="info"):
        toasts.append((message, kind))

    kernel_calls = {
        "open": [],
        "terminate": [],
        "wait": [],
        "close": [],
    }

    class _KernelStub:
        def OpenProcess(self, access, inherit, pid):
            kernel_calls["open"].append((access, inherit, pid))
            return pid

        def TerminateProcess(self, handle, exit_code):
            kernel_calls["terminate"].append((handle, exit_code))
            return True

        def WaitForSingleObject(self, handle, timeout):
            kernel_calls["wait"].append((handle, timeout))
            return 0

        def CloseHandle(self, handle):
            kernel_calls["close"].append(handle)
            return True

    kernel = _KernelStub()
    monkeypatch.setattr(card, "_kernel32", kernel)
    monkeypatch.setattr(card, "_enum_descendant_processes", lambda pid: {pid + 1})

    logs = []

    def _log(self, message, level=logging.INFO):
        logs.append((message, level))

    release_called = {"value": False}

    def _release(self):
        release_called["value"] = True

    monkeypatch.setattr(card.ExternalAppCard, "_log", _log, raising=False)
    monkeypatch.setattr(card.ExternalAppCard, "_release_window", _release, raising=False)

    widget = card.ExternalAppCard(theme, spec, toast_cb=_toast)
    widget._tracked_pid = 4321

    widget.shutdown()

    assert release_called["value"] is True
    assert widget._tracked_pid is None

    opened_pids = [pid for _, _, pid in kernel_calls["open"]]
    assert opened_pids == [4322, 4321]

    terminated_handles = [handle for handle, _ in kernel_calls["terminate"]]
    assert terminated_handles == [4322, 4321]

    waited_handles = [handle for handle, _ in kernel_calls["wait"]]
    assert waited_handles == [4322, 4321]

    assert kernel_calls["close"] == [4322, 4321]

    assert any("Forced termination" in entry[0] for entry in logs)
    levels = {entry[1] for entry in logs}
    assert logging.WARNING in levels

    assert toasts == [("Force closed external app after launcher exit.", "warning")]

