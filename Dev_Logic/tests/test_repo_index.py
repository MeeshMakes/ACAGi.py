import json
from pathlib import Path

from memory_manager import RepositoryIndex


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_repository_index_rebuild_and_query(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    python_source = '''"""Example module."""


def add_task_bus(event):
    """Add an event to the in-memory task bus."""
    return {"event": event, "status": "queued"}


class TaskWorker:
    def greet(self, name: str) -> str:
        return f"hello {name}"
'''
    _write_file(repo_root / "src" / "tasks.py", python_source)

    markdown_doc = (
        "# Overview\n\n"
        "The task bus coordinates publish/subscribe flows.\n\n"
        "## Processing\n\n"
        "Workers acknowledge task completion.\n"
    )
    _write_file(repo_root / "docs" / "tasks.md", markdown_doc)

    data_root = tmp_path / "datasets"

    index = RepositoryIndex(repo_root=repo_root, data_root=data_root)
    summary = index.rebuild()

    assert summary["files_indexed"] == 2
    assert summary["segments"] >= 3

    index_path = data_root / "repo_index" / "index.jsonl"
    assert index_path.exists()

    entries = [
        json.loads(line)
        for line in index_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert entries, "expected index entries"
    ids = [entry["id"] for entry in entries]
    assert len(ids) == len(set(ids)), "segment identifiers should be unique"
    assert any(
        entry["metadata"].get("language") == "markdown" for entry in entries
    )

    results = index.search("task bus queued", k=2)
    assert results, "expected at least one search result"
    top = results[0]
    assert top["path"].endswith("tasks.py")
    assert top["metadata"]["kind"] in {"function", "class"}

    summary_again = index.rebuild()
    assert summary_again["segments"] == summary["segments"]

    cached = list(index.iter_segments())
    assert cached, "expected cached segments"
    assert any(segment["path"].endswith("tasks.md") for segment in cached)


def test_repository_index_tracks_extra_roots(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "README.md").write_text("root", encoding="utf-8")

    extra_root = tmp_path / "shared"
    extra_root.mkdir()
    (extra_root / "notes.txt").write_text("shared", encoding="utf-8")

    data_root = tmp_path / "datasets"
    index = RepositoryIndex(repo_root=repo_root, data_root=data_root, extra_roots=[extra_root])
    summary = index.rebuild()

    assert summary["files_indexed"] == 2

    segments = list(index.iter_segments())
    assert any(segment["metadata"].get("scan_root") == str(repo_root.resolve()) for segment in segments)
    assert any(
        segment["metadata"].get("scan_root") == str(extra_root.resolve())
        for segment in segments
    )
