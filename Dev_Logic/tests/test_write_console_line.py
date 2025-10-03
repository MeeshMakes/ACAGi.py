import types
import threading
import ctypes
from ctypes import wintypes

import pytest
import Codex_Terminal as sct

if not hasattr(sct, "write_console_line"):
    pytest.skip("write_console_line not available", allow_module_level=True)


def test_write_console_line_atomic(monkeypatch):
    writes = []
    monkeypatch.setattr(sct, "_attach", lambda pid: True)
    monkeypatch.setattr(sct, "_open_conin_write", lambda: 42)

    def fake_writefile(h, data, length, written, overlapped):
        assert h == 42
        writes.append(data[:length])
        ctypes.cast(written, ctypes.POINTER(wintypes.DWORD))[0] = length
        return 1

    monkeypatch.setattr(sct, "WriteFile", fake_writefile)
    monkeypatch.setattr(sct, "CloseHandle", lambda h: None)
    monkeypatch.setattr(sct, "FreeConsole", lambda: None)

    ok, err = sct.write_console_line(1, "hello")
    assert (ok, err) == (True, 0)
    assert writes == [("hello\r\n").encode("utf-16le")]


def test_write_console_line_failure_exposes_error(monkeypatch):
    monkeypatch.setattr(sct, "_attach", lambda pid: False)
    monkeypatch.setattr(ctypes, "get_last_error", lambda: 5, raising=False)
    ok, err = sct.write_console_line(1, "hello")
    assert ok is False and err == 5


def test_send_uses_write_console_line(monkeypatch):
    called = {}

    def fake_write_console_line(pid, text):
        called["args"] = (pid, text)
        return True, 0

    monkeypatch.setattr(sct, "write_console_line", fake_write_console_line)

    after_calls = []

    def fake_after(*args, **kwargs):
        after_calls.append((args, kwargs))

    class FakeInput:
        def __init__(self):
            self.text = "hi"

        def get(self, start, end):
            return self.text + "\n"

        def delete(self, start, end):
            self.text = ""

    dummy = types.SimpleNamespace(
        cmd_pid=111,
        _busy=threading.Event(),
        input=FakeInput(),
        log_status=lambda msg: None,
        _watch_until_settled=lambda: None,
        after=fake_after,
    )

    class FakeThread:
        def __init__(self, target, daemon=True):
            self.target = target

        def start(self):
            self.target()

    monkeypatch.setattr(threading, "Thread", FakeThread)
    sct.BridgeGUI._send(dummy)
    assert called["args"] == (111, "hi")
    assert after_calls == []
