import json

from Codex_Terminal import ConversationIO


class DummyOllama:
    def embeddings(self, model, text):
        vec = [1.0, 0.0] if "hello" in text else [0.0, 1.0]
        return True, vec, ""


def test_conversation_jsonl_and_retrieve(tmp_path):
    archive_root = tmp_path / "archive"
    conv = ConversationIO(
        tmp_path,
        "dummy",
        DummyOllama(),
        True,
        session_token="session-a",
        archive_root=archive_root,
    )
    conv.append("user", "hello world", [])
    conv.append("assistant", "foo bar", [])
    data_path = tmp_path / "conversation.jsonl"
    vec_path = tmp_path / "conversation.vec"
    assert data_path.exists()
    lines = [
        json.loads(line)
        for line in data_path.read_text().splitlines()
    ]
    assert lines[0]["text"] == "hello world"
    assert vec_path.exists()
    res = conv.retrieve("hello", k=1)
    assert res and res[0]["text"] == "hello world"


def test_session_rollover_archives_logs(tmp_path):
    archive_root = tmp_path / "archive"
    conv_a = ConversationIO(
        tmp_path,
        "dummy",
        DummyOllama(),
        True,
        session_token="session-a",
        archive_root=archive_root,
    )
    conv_a.append("user", "hello world", [])
    assert (tmp_path / "conversation.jsonl").exists()

    conv_b = ConversationIO(
        tmp_path,
        "dummy",
        DummyOllama(),
        True,
        session_token="session-b",
        archive_root=archive_root,
    )

    archive_dirs = sorted(p for p in archive_root.iterdir() if p.is_dir())
    assert archive_dirs, "expected archived session"
    archived_jsonl = archive_dirs[0] / "conversation.jsonl"
    assert archived_jsonl.exists()
    archived_lines = [
        json.loads(line)
        for line in archived_jsonl.read_text().splitlines()
    ]
    assert archived_lines[0]["text"] == "hello world"
    meta = json.loads((archive_dirs[0] / "meta.json").read_text())
    assert meta["reason"] == "session-rollover"
    assert meta["entry_count"] == 1
    assert not conv_b.recent(1)


def test_length_threshold_archives_logs(tmp_path):
    archive_root = tmp_path / "archive"
    conv = ConversationIO(
        tmp_path,
        "dummy",
        DummyOllama(),
        True,
        session_token="session-threshold",
        archive_root=archive_root,
        max_entries=2,
        max_bytes=1_000_000,
    )
    conv.append("user", "first", [])
    conv.append("assistant", "second", [])
    conv.append("user", "third", [])

    archive_dirs = sorted(p for p in archive_root.iterdir() if p.is_dir())
    assert archive_dirs, "expected archive directory"
    archived_jsonl = archive_dirs[0] / "conversation.jsonl"
    archived_lines = [
        json.loads(line)
        for line in archived_jsonl.read_text().splitlines()
    ]
    assert len(archived_lines) == 2
    assert archived_lines[0]["text"] == "first"
    meta = json.loads((archive_dirs[0] / "meta.json").read_text())
    assert meta["reason"] == "length-threshold"

    remaining_lines = [
        json.loads(line)
        for line in (tmp_path / "conversation.jsonl").read_text().splitlines()
    ]
    assert len(remaining_lines) == 1
    assert remaining_lines[0]["text"] == "third"


def test_resolve_conversation_handles_live_and_archived(tmp_path):
    archive_root = tmp_path / "archive"
    conv = ConversationIO(
        tmp_path,
        "dummy",
        DummyOllama(),
        True,
        session_token="session-live",
        archive_root=archive_root,
    )
    conv.append("user", "hello", [])
    record_live = conv.resolve_conversation("session-live")
    assert record_live is not None
    assert record_live.source == "live"
    assert record_live.jsonl_path.exists()

    conv_archive = ConversationIO(
        tmp_path,
        "dummy",
        DummyOllama(),
        True,
        session_token="session-next",
        archive_root=archive_root,
    )
    record_archived = conv_archive.resolve_conversation("session-live")
    assert record_archived is not None
    assert record_archived.source == "archive"
    assert record_archived.jsonl_path.exists()
    assert record_archived.root.parent == archive_root
