import threading
import time

import pytest
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from Virtual_Desktop import StartPanel, VirtualDesktopCore


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _wait_for(condition, *, timeout: float = 1.0) -> bool:
    app = _ensure_app()
    deadline = time.time() + timeout
    while time.time() < deadline:
        if condition():
            return True
        app.processEvents()
        time.sleep(0.01)
    return condition()


@pytest.mark.parametrize("filename", ["alpha.txt", "beta.txt"])
def test_search_warm_index_prevents_rescan(tmp_path, monkeypatch, filename):
    _ensure_app()
    (tmp_path / filename).write_text("sample data")

    call_count = 0
    lock = threading.Lock()
    original_index = StartPanel._index_workspace

    def counting(self, root):
        nonlocal call_count
        with lock:
            call_count += 1
        return original_index(self, root)

    monkeypatch.setattr(StartPanel, "_index_workspace", counting, raising=False)

    core = VirtualDesktopCore(workspace=str(tmp_path))
    panel = core.start_panel

    assert _wait_for(lambda: call_count >= 1)
    _wait_for(lambda: getattr(panel, "_warm_thread", None) is None)

    with lock:
        initial_calls = call_count

    result = core.search(filename.split(".")[0])
    assert result["Files"], "Expected warmed search to return indexed file"

    with lock:
        assert call_count == initial_calls, "Search should use warmed index without rescanning"


def test_focus_refresh_runs_once_until_marked_stale(tmp_path, monkeypatch):
    _ensure_app()
    (tmp_path / "gamma.txt").write_text("focus data")

    call_count = 0
    lock = threading.Lock()
    original_index = StartPanel._index_workspace

    def counting(self, root):
        nonlocal call_count
        with lock:
            call_count += 1
        return original_index(self, root)

    monkeypatch.setattr(StartPanel, "_index_workspace", counting, raising=False)

    core = VirtualDesktopCore(workspace=str(tmp_path))
    panel = core.start_panel

    assert _wait_for(lambda: call_count >= 1)
    _wait_for(lambda: getattr(panel, "_warm_thread", None) is None)

    panel._refresh_index_if_pending()
    assert _wait_for(lambda: call_count >= 2)
    assert not panel._focus_refresh_pending

    with lock:
        after_first_focus = call_count

    panel._refresh_index_if_pending()
    with lock:
        assert call_count == after_first_focus

    core.mark_start_index_stale()
    assert panel._focus_refresh_pending

    panel._refresh_index_if_pending()
    assert _wait_for(lambda: call_count >= after_first_focus + 1)
    assert not panel._focus_refresh_pending


def test_search_result_buttons_use_compact_icon_size(tmp_path):
    _ensure_app()
    (tmp_path / "doc.txt").write_text("data")

    core = VirtualDesktopCore(workspace=str(tmp_path))
    panel = core.start_panel

    item = {"title": "Doc Item", "kind": "doc", "path": str(tmp_path / "doc.txt")}
    btn = panel._make_result_button("Files", item)

    assert not btn.icon().isNull(), "Expected search result button to have an icon"
    assert btn.iconSize() == QSize(20, 20)
