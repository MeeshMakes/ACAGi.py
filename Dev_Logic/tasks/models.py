"""Task data models and JSONL persistence helpers.

This module provides dataclasses that model Codex tasks and helper
functions to persist them in append-only datasets housed under
``datasets/``. The APIs keep the on-disk format aligned with the
specification documented in ``concepts/dev_logic/Task System.md``.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

__all__ = [
    "Task",
    "TaskEvent",
    "DiffSnapshot",
    "ErrorRecord",
    "append_task",
    "update_task",
    "append_event",
    "append_run_log",
    "append_run_output",
    "load_run_log_tail",
    "resolve_run_log_path",
    "append_error_record",
]

DATASETS_DIR = Path(__file__).resolve().parent.parent / "datasets"
TASKS_FILE = DATASETS_DIR / "tasks.jsonl"
EVENTS_FILE = DATASETS_DIR / "task_events.jsonl"
DIFFS_FILE = DATASETS_DIR / "diffs.jsonl"
ERRORS_FILE = DATASETS_DIR / "errors.jsonl"
_RUNS_SUBDIR = "runs"
_RUN_LOG_FILENAME = "run.log"


@dataclass(slots=True)
class TaskDiffSummary:
    """Summary of cumulative diff counts attached to a task."""

    added: int = 0
    removed: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {"added": int(self.added), "removed": int(self.removed)}


@dataclass(slots=True)
class Task:
    """Representation of a tracked task entry."""

    id: str
    title: str
    status: str
    created_ts: float
    updated_ts: float
    session_id: str
    source: str
    labels: List[str] = field(default_factory=list)
    diffs: TaskDiffSummary = field(default_factory=TaskDiffSummary)
    files: List[str] = field(default_factory=list)
    run_log_path: Optional[str] = None
    codex_conversation_id: Optional[str] = None
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "created_ts": self.created_ts,
            "updated_ts": self.updated_ts,
            "session_id": self.session_id,
            "source": self.source,
            "labels": list(self.labels),
            "diffs": self.diffs.to_dict(),
            "files": list(self.files),
            "run_log_path": self.run_log_path,
            "codex_conversation_id": self.codex_conversation_id,
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Task":
        diffs = payload.get("diffs") or {}
        summary = TaskDiffSummary(
            added=int(diffs.get("added", 0)),
            removed=int(diffs.get("removed", 0)),
        )
        return cls(
            id=str(payload["id"]),
            title=str(payload["title"]),
            status=str(payload["status"]),
            created_ts=float(payload["created_ts"]),
            updated_ts=float(payload["updated_ts"]),
            session_id=str(payload["session_id"]),
            source=str(payload["source"]),
            labels=list(payload.get("labels", [])),
            diffs=summary,
            files=list(payload.get("files", [])),
            run_log_path=payload.get("run_log_path"),
            codex_conversation_id=payload.get("codex_conversation_id"),
            parent_id=payload.get("parent_id"),
        )


@dataclass(slots=True)
class TaskEvent:
    """Immutable event describing a change to a task."""

    ts: float
    task_id: str
    event: str
    by: Optional[str] = None
    to: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "ts": self.ts,
            "task_id": self.task_id,
            "event": self.event,
        }
        if self.by is not None:
            payload["by"] = self.by
        if self.to is not None:
            payload["to"] = self.to
        if self.data is not None:
            payload["data"] = self.data
        return payload


@dataclass(slots=True)
class DiffSnapshot:
    """Snapshot of diff statistics emitted during a task run."""

    ts: float
    task_id: str
    added: int
    removed: int
    files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts,
            "task_id": self.task_id,
            "added": int(self.added),
            "removed": int(self.removed),
            "files": list(self.files),
        }


@dataclass(slots=True)
class ErrorRecord:
    """Structured record describing a captured error event."""

    ts: float
    level: str
    kind: str
    msg: str
    path: Optional[str] = None
    task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "ts": float(self.ts),
            "level": str(self.level),
            "kind": str(self.kind),
            "msg": str(self.msg),
        }
        if self.path is not None:
            payload["path"] = self.path
        if self.task_id is not None:
            payload["task_id"] = self.task_id
        return payload


def _ensure_datasets_dir() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_datasets_dir()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    items: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def _write_jsonl_atomic(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    _ensure_datasets_dir()
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    os.replace(tmp_path, path)


def _dataset_root(candidate: Optional[Path]) -> Path:
    return Path(candidate) if candidate else DATASETS_DIR


def append_error_record(record: ErrorRecord) -> None:
    """Persist ``record`` to the shared ``errors.jsonl`` dataset."""

    _append_jsonl(ERRORS_FILE, record.to_dict())


def resolve_run_log_path(task: Task, dataset_root: Optional[Path] = None) -> Tuple[Path, str]:
    """Return absolute and relative run-log paths for ``task``.

    Args:
        task: Task instance describing the record being updated.
        dataset_root: Optional override for the datasets directory root.

    Returns:
        Tuple of ``(absolute_path, relative_posix)``.
    """

    root = _dataset_root(dataset_root)
    if task.run_log_path:
        raw = Path(task.run_log_path)
    else:
        raw = Path(_RUNS_SUBDIR) / task.id / _RUN_LOG_FILENAME
    absolute = raw if raw.is_absolute() else root / raw
    relative = raw.as_posix()
    return absolute, relative


def append_run_log(
    task: Task,
    lines: Iterable[str] | str,
    dataset_root: Optional[Path] = None,
    *,
    channel: Optional[str] = None,
) -> Tuple[Path, str, bool]:
    """Append ``lines`` to the task run log, creating directories as needed.

    Args:
        task: Task whose run log is being updated.
        lines: Text lines to append. Strings are treated as a single line.
        dataset_root: Optional root directory for datasets (defaults to
            :data:`DATASETS_DIR`).
        channel: Optional label such as ``"stdout"`` or ``"stderr"`` to prefix
            each line with ``[channel] ``.

    Returns:
        ``(absolute_path, relative_posix, created)`` where ``created`` indicates
        the task previously lacked a ``run_log_path`` value.
    """

    absolute, relative = resolve_run_log_path(task, dataset_root)
    absolute.parent.mkdir(parents=True, exist_ok=True)

    created = task.run_log_path is None

    entries: List[str]
    if isinstance(lines, str):
        entries = [lines]
    else:
        entries = [str(line) for line in lines]

    if entries:
        prefix = f"[{channel}]" if channel else ""
        with absolute.open("a", encoding="utf-8") as fh:
            for entry in entries:
                text = entry.rstrip("\n")
                if prefix:
                    text = f"{prefix} {text}" if text else prefix
                if text:
                    fh.write(text + "\n")
                else:
                    fh.write("\n")
    else:
        absolute.touch(exist_ok=True)

    if task.run_log_path is None:
        task.run_log_path = relative

    return absolute, relative, created


def append_run_output(
    task: Task,
    *,
    stdout: str = "",
    stderr: str = "",
    dataset_root: Optional[Path] = None,
) -> Tuple[Path, str, bool]:
    """Append captured stdout/stderr streams to the task run log."""

    created = False
    path: Optional[Path] = None
    relative: Optional[str] = None

    if stdout:
        path, relative, created_stdout = append_run_log(
            task,
            stdout.splitlines(),
            dataset_root,
            channel="stdout",
        )
        created = created or created_stdout

    if stderr:
        path, relative, created_stderr = append_run_log(
            task,
            stderr.splitlines(),
            dataset_root,
            channel="stderr",
        )
        created = created or created_stderr

    if path is None or relative is None:
        path, relative = resolve_run_log_path(task, dataset_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        if task.run_log_path is None:
            task.run_log_path = relative
            created = True

    return path, relative, created


def load_run_log_tail(
    task: Task,
    dataset_root: Optional[Path] = None,
    *,
    max_lines: int = 200,
) -> List[str]:
    """Return the last ``max_lines`` entries from the task run log."""

    if max_lines <= 0:
        return []
    if not task.run_log_path:
        return []

    absolute, _ = resolve_run_log_path(task, dataset_root)
    if not absolute.exists():
        return []

    tail: deque[str] = deque(maxlen=int(max_lines))
    with absolute.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            tail.append(line.rstrip("\n"))
    return list(tail)


def append_task(task: Task) -> None:
    """Append a task entry to ``tasks.jsonl``."""

    _append_jsonl(TASKS_FILE, task.to_dict())


def update_task(task_id: str, **changes: Any) -> Task:
    """Apply updates to a task entry and rewrite the dataset atomically.

    Args:
        task_id: Identifier of the task to update.
        **changes: Key/value pairs to merge into the stored representation.

    Returns:
        The updated :class:`Task` instance.

    Raises:
        ValueError: If the task identifier does not exist.
    """

    records = _read_jsonl(TASKS_FILE)
    updated_record: Optional[Dict[str, Any]] = None
    for record in records:
        if record.get("id") == task_id:
            record.update(changes)
            updated_record = record
            break
    if updated_record is None:
        raise ValueError(f"Task '{task_id}' does not exist")
    _write_jsonl_atomic(TASKS_FILE, records)
    return Task.from_dict(updated_record)


def append_event(event: TaskEvent) -> None:
    """Append a task event to ``task_events.jsonl``."""

    _append_jsonl(EVENTS_FILE, event.to_dict())
