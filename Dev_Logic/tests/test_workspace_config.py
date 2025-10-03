from pathlib import Path
import os
import Codex_Terminal as ct
import Virtual_Desktop as vd


def test_modules_share_workspace(monkeypatch):
    ws = Path(os.environ["CODEX_WORKSPACE"])
    monkeypatch.setattr(ct, "_legacy_transit_candidates", lambda: [])
    assert ct.workspace_root() == ws
    assert ct.transit_dir() == ws / "Terminal Desktop"
    assert Path(vd.workspace_root()) == ws
    data_root = ct.agent_data_root()
    assert data_root == ws / ".codex_agent"
    assert data_root.is_dir()
    assert ct.agent_images_dir() == data_root / "images"
    assert ct.agent_sessions_dir() == data_root / "sessions"
    assert ct.agent_archives_dir() == data_root / "archives"
