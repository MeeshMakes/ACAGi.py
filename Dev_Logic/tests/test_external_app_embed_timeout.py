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


def test_external_app_waits_for_extended_timeout(monkeypatch):
    pytest.importorskip("PySide6")

    """Ledger 959d30d6-7381-4f97-925e-ef6ee16f124d: slow embeds respect extended timeout."""

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
            self._interval = 0
            self._active = False
            self.timeout = _StubSignal()

        def setInterval(self, interval):
            self._interval = interval

        def start(self):
            self._active = True

        def stop(self):
            self._active = False

        def isActive(self):
            return self._active

    class _StubProcess:
        NotRunning = 0
        Starting = 1
        Running = 2

        def __init__(self, *_, **__):
            self._state = self.Running
            self._pid = 4321
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
            self._pid = 4321

        def waitForStarted(self, _msecs):
            return True

        def state(self):
            return self._state

        def processId(self):
            return self._pid

        def terminate(self):
            self._state = self.NotRunning

        def waitForFinished(self, _msecs):
            return True

        def kill(self):
            self._state = self.NotRunning

        def errorString(self):
            return ""

    class _Clock:
        def __init__(self):
            self.value = 0.0

        def __call__(self):
            return self.value

    clock = _Clock()

    monkeypatch.setattr(card, "QProcess", _StubProcess)
    monkeypatch.setattr(card, "QTimer", _StubTimer)
    monkeypatch.setattr(card.time, "monotonic", clock)

    spec = card.LaunchSpec(
        argv=["C:/slow.exe"],
        cwd="C:/",
        target_path="C:/slow.exe",
        original_path="C:/slow.exe",
    )

    theme = types.SimpleNamespace(header_fg="#fff")

    embedded = {}

    def _fake_embed(self, hwnd):
        embedded["hwnd"] = hwnd
        self._embedded_hwnd = hwnd

    monkeypatch.setattr(card.ExternalAppCard, "_embed_window", _fake_embed, raising=False)
    monkeypatch.setattr(card.ExternalAppCard, "_log", lambda *args, **kwargs: None, raising=False)

    attempts = {"count": 0}

    def _fake_find(_pid):
        attempts["count"] += 1
        if attempts["count"] < 2:
            return None
        return 0x0ABC

    monkeypatch.setattr(card, "_find_main_hwnd", _fake_find, raising=False)

    widget = card.ExternalAppCard(theme, spec, embed_timeout=15.0)
    assert widget.start()

    clock.value = 5.0
    widget._poll_for_window()
    assert "hwnd" not in embedded

    clock.value = 12.0
    widget._poll_for_window()

    assert embedded["hwnd"] == 0x0ABC
    assert not widget._fallback_emitted

    widget.shutdown()
