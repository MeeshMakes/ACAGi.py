import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

import pytest

from Codex_Terminal import run_checked
from tasks import diffs as task_diffs
from tasks import models as task_models
from tasks.bus import subscribe
from tasks.models import Task, append_task


@pytest.fixture(autouse=True)
def _isolate_datasets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
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
def _reset_bus(monkeypatch: pytest.MonkeyPatch):
    from tasks import bus

    fresh = defaultdict(list)
    monkeypatch.setattr(bus, "_SUBSCRIBERS", fresh, raising=False)
    yield
    monkeypatch.setattr(bus, "_SUBSCRIBERS", defaultdict(list), raising=False)


def _read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    contents = path.read_text(encoding="utf-8")
    lines = (line for line in contents.splitlines() if line)
    return [json.loads(line) for line in lines]


def _init_repo(repo: Path) -> None:
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


def _make_task(task_id: str) -> Task:
    task = Task(
        id=task_id,
        title="Task",
        status="open",
        created_ts=1.0,
        updated_ts=1.0,
        session_id="sess",
        source="terminal",
    )
    append_task(task)
    return task


def test_run_checked_marks_task_merged_on_success(tmp_path: Path):
    repo = tmp_path / "repo"
    _init_repo(repo)
    task = _make_task("tsk_merge")

    events: List[Tuple[str, dict]] = []
    handle_status = subscribe(
        "task.status",
        lambda payload: events.append(("task.status", payload)),
    )
    handle_update = subscribe(
        "task.updated",
        lambda payload: events.append(("task.updated", payload)),
    )
    try:
        script = (
            "from pathlib import Path\n"
            "p = Path('sample.txt')\n"
            "p.write_text(p.read_text() + 'gamma\\n')\n"
        )
        cmd = [sys.executable, "-c", script]
        rc, _, _ = run_checked(cmd, cwd=repo, task=task)
    finally:
        handle_status.unsubscribe()
        handle_update.unsubscribe()

    assert rc == 0

    records = _read_jsonl(task_models.TASKS_FILE)
    stored = next(item for item in records if item["id"] == task.id)
    assert stored["status"] == "merged"
    assert stored["diffs"]["added"] >= 1

    status_events = [
        item
        for item in _read_jsonl(task_models.EVENTS_FILE)
        if item.get("event") == "status" and item.get("task_id") == task.id
    ]
    assert status_events and status_events[-1]["to"] == "merged"
    assert status_events[-1]["data"]["exit_code"] == 0

    assert any(topic == "task.status" for topic, _ in events)
    assert any(topic == "task.updated" for topic, _ in events)


def test_run_checked_marks_task_failed_on_nonzero_exit(tmp_path: Path):
    repo = tmp_path / "repo"
    _init_repo(repo)
    task = _make_task("tsk_fail")

    events: List[Tuple[str, dict]] = []
    handle_status = subscribe(
        "task.status",
        lambda payload: events.append(("task.status", payload)),
    )
    handle_update = subscribe(
        "task.updated",
        lambda payload: events.append(("task.updated", payload)),
    )
    try:
        cmd = [
            sys.executable,
            "-c",
            "import sys\n"
            "sys.exit(5)",
        ]
        rc, _, _ = run_checked(cmd, cwd=repo, task=task)
    finally:
        handle_status.unsubscribe()
        handle_update.unsubscribe()

    assert rc == 5

    records = _read_jsonl(task_models.TASKS_FILE)
    stored = next(item for item in records if item["id"] == task.id)
    assert stored["status"] == "failed"

    status_events = [
        item
        for item in _read_jsonl(task_models.EVENTS_FILE)
        if item.get("event") == "status" and item.get("task_id") == task.id
    ]
    assert status_events and status_events[-1]["to"] == "failed"
    assert status_events[-1]["data"]["exit_code"] == 5

    assert any(topic == "task.status" for topic, _ in events)
    assert any(topic == "task.updated" for topic, _ in events)


def test_run_checked_marks_task_cancelled_when_flagged(tmp_path: Path):
    repo = tmp_path / "repo"
    _init_repo(repo)
    task = _make_task("tsk_cancel")

    events: List[Tuple[str, dict]] = []
    handle_status = subscribe(
        "task.status",
        lambda payload: events.append(("task.status", payload)),
    )
    handle_update = subscribe(
        "task.updated",
        lambda payload: events.append(("task.updated", payload)),
    )
    try:
        cmd = [sys.executable, "-c", "print('cancelled run')"]
        rc, _, _ = run_checked(cmd, cwd=repo, task=task, cancelled=True)
    finally:
        handle_status.unsubscribe()
        handle_update.unsubscribe()

    assert rc == 0

    records = _read_jsonl(task_models.TASKS_FILE)
    stored = next(item for item in records if item["id"] == task.id)
    assert stored["status"] == "cancelled"

    status_events = [
        item
        for item in _read_jsonl(task_models.EVENTS_FILE)
        if item.get("event") == "status" and item.get("task_id") == task.id
    ]
    assert status_events and status_events[-1]["to"] == "cancelled"
    assert status_events[-1]["data"]["cancelled"] is True

    assert any(topic == "task.status" for topic, _ in events)
    assert any(topic == "task.updated" for topic, _ in events)


def test_run_checked_keeps_task_open_without_changes(tmp_path: Path):
    repo = tmp_path / "repo"
    _init_repo(repo)
    task = _make_task("tsk_open")

    events: List[Tuple[str, dict]] = []
    handle_status = subscribe(
        "task.status",
        lambda payload: events.append(("task.status", payload)),
    )
    handle_update = subscribe(
        "task.updated",
        lambda payload: events.append(("task.updated", payload)),
    )
    try:
        cmd = [sys.executable, "-c", "print('noop')"]
        rc, _, _ = run_checked(cmd, cwd=repo, task=task)
    finally:
        handle_status.unsubscribe()
        handle_update.unsubscribe()

    assert rc == 0

    records = _read_jsonl(task_models.TASKS_FILE)
    stored = next(item for item in records if item["id"] == task.id)
    assert stored["status"] == "open"

    status_events = [
        item
        for item in _read_jsonl(task_models.EVENTS_FILE)
        if item.get("event") == "status" and item.get("task_id") == task.id
    ]
    assert not status_events
    assert events == []
