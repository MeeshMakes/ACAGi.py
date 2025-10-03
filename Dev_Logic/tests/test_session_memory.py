import json

import Codex_Terminal as sct
from PySide6.QtWidgets import QApplication


class DummyOllama:
    def health(self):
        return True, "OK"

    def embeddings(self, model, text):
        return False, [], ""

    def chat(self, model, messages, images=None):
        return True, "", ""


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _chatcard(tmp_path, monkeypatch, memory_data=None):
    mem_path = tmp_path / "codex_memory.json"
    if memory_data is None:
        memory_data = {"sessions": [], "work_items": []}
    mem_path.write_text(json.dumps(memory_data, indent=2), encoding="utf-8")
    monkeypatch.setattr(sct, "MEMORY_PATH", mem_path)

    def _fake_agent_root():
        root = tmp_path / ".codex_agent"
        root.mkdir(parents=True, exist_ok=True)
        for name in ("images", "sessions", "logs", "archives", "data", "lexicons"):
            (root / name).mkdir(parents=True, exist_ok=True)
        return root

    monkeypatch.setattr(sct, "agent_data_root", _fake_agent_root)
    settings = {
        "context_pairs": 4,
        "share_context": False,
        "share_limit": 2,
        "enable_semantic": False,
        "enable_vision": False,
        "workspace": tmp_path,
        "data_root": str(tmp_path),
    }
    lex_dir = tmp_path / "lex"
    lex_dir.mkdir(parents=True, exist_ok=True)
    lex_mgr = sct.LexiconManager(lex_dir)
    card = sct.ChatCard(sct.Theme(), DummyOllama(), settings, lex_mgr)
    return card, mem_path


def test_session_notes_loaded_on_startup(tmp_path, monkeypatch):
    _ensure_app()
    data = {
        "sessions": [
            {
                "timestamp": "2025-09-15T00:00:00Z",
                "notes": "Prefers dark mode",
            },
            {
                "timestamp": "2025-09-16T00:00:00Z",
                "notes": "Needs keyboard shortcuts",
            },
        ],
        "work_items": [],
    }
    chat, _ = _chatcard(tmp_path, monkeypatch, data)
    try:
        assert chat.session_notes[0]["notes"] == "Prefers dark mode"
        assert chat.session_notes[1]["notes"] == "Needs keyboard shortcuts"
    finally:
        chat.deleteLater()


def test_gather_context_includes_session_notes(tmp_path, monkeypatch):
    _ensure_app()
    chat, _ = _chatcard(tmp_path, monkeypatch)
    try:
        chat.session_notes = [
            {"timestamp": "2025-09-16T00:00:00Z", "notes": "Prefers CLI tools"}
        ]
        chat.messages = []
        ctx = chat._gather_context("hello")
        assert ctx and ctx[0]["role"] == "system"
        assert "Prefers CLI tools" in ctx[0]["content"]
    finally:
        chat.deleteLater()


def test_user_turn_appends_session_note(tmp_path, monkeypatch):
    _ensure_app()
    chat, mem_path = _chatcard(tmp_path, monkeypatch)
    try:
        chat._record_message("user", "I prefer dark themes", [])
        data = json.loads(mem_path.read_text(encoding="utf-8"))
        assert data["sessions"]
        assert "dark themes" in data["sessions"][-1]["notes"]
        assert "dark themes" in chat.session_notes[-1]["notes"]
        assert data.get("work_items") == []
    finally:
        chat.deleteLater()
