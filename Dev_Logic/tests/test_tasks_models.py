from __future__ import annotations

import json
from pathlib import Path

import pytest

from tasks import models as task_models
from tasks.models import (
    DiffSnapshot,
    ErrorRecord,
    Task,
    TaskDiffSummary,
    TaskEvent,
    append_error_record,
    append_event,
    append_run_log,
    append_run_output,
    append_task,
    load_run_log_tail,
    update_task,
)


@pytest.fixture(autouse=True)
def _isolate_datasets(tmp_path, monkeypatch):
    monkeypatch.setattr(task_models, "DATASETS_DIR", tmp_path, raising=False)
    monkeypatch.setattr(
        task_models,
        "TASKS_FILE",
        tmp_path / "tasks.jsonl",
        raising=False,
    )
    monkeypatch.setattr(
        task_models,
        "EVENTS_FILE",
        tmp_path / "task_events.jsonl",
        raising=False,
    )
    monkeypatch.setattr(
        task_models,
        "DIFFS_FILE",
        tmp_path / "diffs.jsonl",
        raising=False,
    )
    monkeypatch.setattr(
        task_models,
        "ERRORS_FILE",
        tmp_path / "errors.jsonl",
        raising=False,
    )
    yield


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line]


def test_append_error_record_appends_jsonl():
    record = ErrorRecord(
        ts=123.456,
        level="ERROR",
        kind="UI",
        msg="Widget failed",
        path="/tmp/example.py",
        task_id="tsk_7",
    )

    append_error_record(record)

    records = read_jsonl(task_models.ERRORS_FILE)
    assert records == [
        {
            "ts": record.ts,
            "level": "ERROR",
            "kind": "UI",
            "msg": "Widget failed",
            "path": "/tmp/example.py",
            "task_id": "tsk_7",
        }
    ]


def test_append_task_writes_jsonl():
    task = Task(
        id="tsk_1",
        title="Initial setup",
        status="open",
        created_ts=1.0,
        updated_ts=1.0,
        session_id="sess",
        source="terminal",
        labels=["bootstrap"],
        diffs=TaskDiffSummary(
            added=10,
            removed=2,
        ),
        files=["README.md"],
        run_log_path="runs/tsk_1.log",
    )

    append_task(task)

    records = read_jsonl(task_models.TASKS_FILE)
    assert records == [
        {
            "id": "tsk_1",
            "title": "Initial setup",
            "status": "open",
            "created_ts": 1.0,
            "updated_ts": 1.0,
            "session_id": "sess",
            "source": "terminal",
            "labels": ["bootstrap"],
            "diffs": {"added": 10, "removed": 2},
            "files": ["README.md"],
            "run_log_path": "runs/tsk_1.log",
            "codex_conversation_id": None,
            "parent_id": None,
        }
    ]


def test_update_task_rewrites_atomically():
    first = Task(
        id="tsk_1",
        title="Initial setup",
        status="open",
        created_ts=1.0,
        updated_ts=1.0,
        session_id="sess",
        source="terminal",
    )
    second = Task(
        id="tsk_2",
        title="Follow-up",
        status="open",
        created_ts=2.0,
        updated_ts=2.0,
        session_id="sess",
        source="terminal",
    )
    append_task(first)
    append_task(second)

    updated = update_task("tsk_2", status="merged", updated_ts=3.0)

    assert updated.status == "merged"
    assert updated.updated_ts == 3.0

    records = read_jsonl(task_models.TASKS_FILE)
    statuses = {item["id"]: item["status"] for item in records}
    assert statuses == {"tsk_1": "open", "tsk_2": "merged"}
    assert not any(
        path.name.endswith(".tmp")
        for path in task_models.TASKS_FILE.parent.iterdir()
    )


def test_update_task_missing_id_raises():
    append_task(
        Task(
            id="tsk_1",
            title="Initial",
            status="open",
            created_ts=1.0,
            updated_ts=1.0,
            session_id="sess",
            source="terminal",
        )
    )

    with pytest.raises(ValueError):
        update_task("missing", status="closed")


def test_append_event_appends_line():
    event = TaskEvent(ts=5.0, task_id="tsk_1", event="created", by="terminal")
    append_event(event)

    records = read_jsonl(task_models.EVENTS_FILE)
    assert records == [
        {"ts": 5.0, "task_id": "tsk_1", "event": "created", "by": "terminal"}
    ]


def test_diff_snapshot_to_dict_includes_files():
    snapshot = DiffSnapshot(
        ts=10.0,
        task_id="tsk_1",
        added=5,
        removed=1,
        files=["a.py"],
    )
    assert snapshot.to_dict() == {
        "ts": 10.0,
        "task_id": "tsk_1",
        "added": 5,
        "removed": 1,
        "files": ["a.py"],
    }


def test_append_run_log_creates_directory(tmp_path):
    task = Task(
        id="tsk_run",
        title="Capture output",
        status="open",
        created_ts=1.0,
        updated_ts=1.0,
        session_id="sess",
        source="terminal",
    )

    path, relative, created = append_run_log(
        task,
        "first line",
        dataset_root=tmp_path,
    )

    assert created is True
    assert relative == f"runs/{task.id}/run.log"
    assert path == tmp_path / relative
    assert path.read_text(encoding="utf-8").splitlines() == ["first line"]

    _, _, created_again = append_run_log(
        task,
        ["second line"],
        dataset_root=tmp_path,
    )
    assert created_again is False
    assert path.read_text(encoding="utf-8").splitlines() == [
        "first line",
        "second line",
    ]


def test_append_run_output_labels_streams(tmp_path):
    task = Task(
        id="tsk_output",
        title="Stream capture",
        status="open",
        created_ts=1.0,
        updated_ts=1.0,
        session_id="sess",
        source="terminal",
    )

    append_run_output(
        task,
        stdout="hello\nworld\n",
        stderr="oops\n",
        dataset_root=tmp_path,
    )

    log_path = tmp_path / Path(task.run_log_path)
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert "[stdout] hello" in lines
    assert "[stdout] world" in lines
    assert "[stderr] oops" in lines


def test_load_run_log_tail_returns_recent_lines(tmp_path):
    run_rel = "runs/tsk_tail/run.log"
    task = Task(
        id="tsk_tail",
        title="Tail check",
        status="open",
        created_ts=1.0,
        updated_ts=1.0,
        session_id="sess",
        source="terminal",
        run_log_path=run_rel,
    )

    run_path = tmp_path / Path(run_rel)
    run_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"line {idx}" for idx in range(10)]
    run_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    tail = load_run_log_tail(task, tmp_path, max_lines=3)

    assert tail == lines[-3:]
