import json
import subprocess
from pathlib import Path

import pytest

from tasks import diffs as task_diffs
from tasks import models as task_models
from tasks.bus import subscribe
from tasks.models import Task, TaskDiffSummary, append_task


@pytest.fixture(autouse=True)
def _isolate_datasets(tmp_path, monkeypatch):
    dataset_root = tmp_path / "datasets"
    replacements = {
        "DATASETS_DIR": dataset_root,
        "TASKS_FILE": dataset_root / "tasks.jsonl",
        "EVENTS_FILE": dataset_root / "task_events.jsonl",
        "DIFFS_FILE": dataset_root / "diffs.jsonl",
    }
    for attr, value in replacements.items():
        monkeypatch.setattr(task_models, attr, value, raising=False)

    diff_replacements = {
        "DATASETS_DIR": dataset_root,
        "DIFFS_FILE": dataset_root / "diffs.jsonl",
        "_SNAPSHOT_ROOT": dataset_root / "runs",
    }
    for attr, value in diff_replacements.items():
        monkeypatch.setattr(task_diffs, attr, value, raising=False)
    yield


@pytest.fixture(autouse=True)
def _reset_bus(monkeypatch):
    from collections import defaultdict

    from tasks import bus

    fresh = defaultdict(list)
    monkeypatch.setattr(bus, "_SUBSCRIBERS", fresh, raising=False)
    yield
    monkeypatch.setattr(bus, "_SUBSCRIBERS", defaultdict(list), raising=False)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    contents = path.read_text(encoding="utf-8")
    lines = (line for line in contents.splitlines() if line)
    return [json.loads(line) for line in lines]


def _create_task(task_id: str) -> Task:
    task = Task(
        id=task_id,
        title="Task",
        status="open",
        created_ts=1.0,
        updated_ts=1.0,
        session_id="sess",
        source="terminal",
        diffs=TaskDiffSummary(),
    )
    append_task(task)
    return task


def test_record_diff_uses_git_numstat_when_available(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
    )
    subprocess.run(
        ["git", "config", "user.email", "codex@example.com"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Codex"],
        cwd=repo,
        check=True,
    )

    sample = repo / "sample.txt"
    sample.write_text("alpha\nbeta\n", encoding="utf-8")
    subprocess.run(["git", "add", "sample.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True)

    sample.write_text("alpha\nbeta updated\ncharlie\n", encoding="utf-8")

    _create_task("tsk_git")

    events: list[dict] = []
    handle = subscribe("task.diff", lambda payload: events.append(payload))

    snapshot = task_diffs.record_diff("tsk_git", workspace_root=repo)

    handle.unsubscribe()

    assert snapshot is not None
    assert snapshot.added == 2
    assert snapshot.removed == 1
    assert snapshot.files == ["sample.txt"]

    diff_records = _read_jsonl(task_models.DIFFS_FILE)
    assert diff_records == [
        {
            "ts": pytest.approx(snapshot.ts, rel=0, abs=0.001),
            "task_id": "tsk_git",
            "added": 2,
            "removed": 1,
            "files": ["sample.txt"],
        }
    ]

    task_records = _read_jsonl(task_models.TASKS_FILE)
    stored = next(item for item in task_records if item["id"] == "tsk_git")
    assert stored["diffs"] == {"added": 2, "removed": 1}

    expected_event = {
        "id": "tsk_git",
        "added": 2,
        "removed": 1,
        "files": ["sample.txt"],
    }
    assert events == [expected_event]


def test_record_diff_falls_back_to_snapshots_for_non_git_files(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "notes.txt"
    target.write_text("first\nsecond\n", encoding="utf-8")

    _create_task("tsk_snap")

    events: list[dict] = []
    handle = subscribe("task.diff", lambda payload: events.append(payload))

    first = task_diffs.record_diff(
        "tsk_snap",
        files=["notes.txt"],
        workspace_root=workspace,
    )
    assert first is not None
    assert first.added == 2
    assert first.removed == 0
    assert first.files == ["notes.txt"]

    target.write_text("first\nthird\n", encoding="utf-8")

    second = task_diffs.record_diff(
        "tsk_snap",
        files=["notes.txt"],
        workspace_root=workspace,
    )

    handle.unsubscribe()

    assert second is not None
    assert second.added == 1
    assert second.removed == 1
    assert second.files == ["notes.txt"]

    diff_records = _read_jsonl(task_models.DIFFS_FILE)
    assert len(diff_records) == 2
    assert diff_records[0]["added"] == 2
    assert diff_records[0]["removed"] == 0
    assert diff_records[1]["added"] == 1
    assert diff_records[1]["removed"] == 1

    task_records = _read_jsonl(task_models.TASKS_FILE)
    stored = next(item for item in task_records if item["id"] == "tsk_snap")
    assert stored["diffs"] == {"added": 1, "removed": 1}

    snapshot_path = task_diffs._snapshot_file("tsk_snap", "notes.txt")
    assert snapshot_path.exists()
    assert snapshot_path.read_text(encoding="utf-8") == "first\nthird"

    assert events[0]["added"] == 2
    assert events[1]["added"] == 1
