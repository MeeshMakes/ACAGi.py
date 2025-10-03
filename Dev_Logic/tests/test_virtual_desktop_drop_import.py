import shutil
import uuid
from pathlib import Path

from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtGui import QDropEvent, QMimeData, QUrl
from PySide6.QtWidgets import QApplication

import Virtual_Desktop as vd


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_drop_local_file_imports_into_workspace(tmp_path):
    _ensure_app()

    src_dir = tmp_path / "source"
    src_dir.mkdir()
    src_file = src_dir / f"dropped_{uuid.uuid4().hex}.txt"
    src_file.write_text("sample drop contents", encoding="utf-8")

    dest_root = Path(vd.workspace_root())
    dest_root.mkdir(parents=True, exist_ok=True)

    canvas = vd.DesktopCanvas(vd.Theme(), QSize(400, 300))

    refresh_calls = []

    def _record_refresh():
        refresh_calls.append(True)

    canvas._refresh_icons = _record_refresh  # type: ignore[assignment]

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(src_file))])
    event = QDropEvent(QPointF(20, 20), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier)

    canvas.dropEvent(event)

    expected_path = dest_root / src_file.name
    assert expected_path.exists()
    assert expected_path.read_text(encoding="utf-8") == src_file.read_text(encoding="utf-8")
    assert refresh_calls, "drop should trigger icon refresh"
    assert event.isAccepted()
    assert event.dropAction() == Qt.CopyAction

    # Cleanup the copied file to keep the workspace tidy for other tests
    if expected_path.is_dir():
        shutil.rmtree(expected_path, ignore_errors=True)
    else:
        expected_path.unlink(missing_ok=True)
