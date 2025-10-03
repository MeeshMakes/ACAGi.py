import pytest
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QStyle

from Virtual_Desktop import VirtualDesktopCore


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_start_panel_prefers_helper_icon(monkeypatch, tmp_path):
    _ensure_app()
    core = VirtualDesktopCore(workspace=str(tmp_path))
    panel = core.start_panel

    blend_path = tmp_path / "scene.blend"
    blend_path.write_text("blend data")

    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor("orange"))
    blender_icon = QIcon(pixmap)

    call_count = 0

    def fake_helper(path_obj):
        nonlocal call_count
        call_count += 1
        return blender_icon, True

    monkeypatch.setattr("Virtual_Desktop._ICON_FOR_PATH_HELPER", fake_helper, raising=False)

    item = {"title": "Scene", "kind": "doc", "path": str(blend_path)}
    icon = panel._icon_for_item("Recent", item)
    assert icon.cacheKey() == blender_icon.cacheKey()

    icon_again = panel._icon_for_item("Recent", item)
    assert icon_again.cacheKey() == blender_icon.cacheKey()
    assert call_count == 1, "Expected path icon helper to be cached per absolute path"


def test_start_panel_falls_back_when_helper_null(monkeypatch, tmp_path):
    _ensure_app()
    core = VirtualDesktopCore(workspace=str(tmp_path))
    panel = core.start_panel

    doc_path = tmp_path / "notes.txt"
    doc_path.write_text("notes")

    call_count = 0

    def fake_helper(_):
        nonlocal call_count
        call_count += 1
        return QIcon(), True

    monkeypatch.setattr("Virtual_Desktop._ICON_FOR_PATH_HELPER", fake_helper, raising=False)

    item = {"title": "Notes", "kind": "doc", "path": str(doc_path)}
    icon = panel._icon_for_item("Files", item)
    expected = QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView)
    assert icon.cacheKey() == expected.cacheKey()

    icon_again = panel._icon_for_item("Files", item)
    assert icon_again.cacheKey() == expected.cacheKey()
    assert call_count == 1
