"""Helpers for capturing per-task diff statistics.

The helpers prefer Git ``--numstat`` output whenever the workspace is a
repository. If the workspace is not Git-controlled or a given file is
untracked, the module falls back to maintaining lightweight text
snapshots so we can still compute line-level additions/removals.

Each diff capture updates the corresponding :class:`~tasks.models.Task`
record, appends a :class:`~tasks.models.DiffSnapshot` to
``datasets/diffs.jsonl``, and emits a ``task.diff`` event on the shared
bus so UI surfaces stay synchronized.
"""
from __future__ import annotations

import difflib
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .bus import publish
from .models import (
    DATASETS_DIR,
    DIFFS_FILE,
    DiffSnapshot,
    TaskDiffSummary,
    update_task,
)

__all__ = ["record_diff"]

_SNAPSHOT_ROOT = DATASETS_DIR / "runs"


@dataclass(slots=True)
class _Target:
    """Normalized representation of a candidate file path."""

    abs_path: Path
    rel_workspace: str
    rel_repo: Optional[str] = None


def record_diff(
    task_id: str,
    files: Optional[Iterable[str]] = None,
    workspace_root: str | Path | None = None,
    timestamp: float | None = None,
) -> Optional[DiffSnapshot]:
    """Capture diff statistics for ``task_id`` and persist the results.

    Args:
        task_id: Identifier of the task being updated.
        files: Optional explicit list of files to diff. When omitted, all
            repository changes are considered.
        workspace_root: Working directory the task operates within.
        timestamp: Optional explicit timestamp. Defaults to ``time.time()``.

    Returns:
        The :class:`DiffSnapshot` that was recorded, or ``None`` when no
        diff information was available and no update occurred.
    """

    if not task_id:
        raise ValueError("task_id is required")

    workspace = Path(workspace_root or Path.cwd()).resolve()
    ts = float(timestamp) if timestamp is not None else time.time()

    targets = _normalize_targets(files, workspace)

    repo_root = _detect_git_repo(workspace)
    if repo_root:
        for target in targets.values():
            try:
                rel_repo = target.abs_path.resolve().relative_to(repo_root)
            except ValueError:
                continue
            target.rel_repo = rel_repo.as_posix()

    git_added = git_removed = 0
    git_files: List[str] = []
    git_handled: Set[Path] = set()
    if repo_root:
        git_added, git_removed, git_files, git_handled = _git_numstat(
            repo_root, workspace, targets
        )

    snapshot_added = snapshot_removed = 0
    snapshot_files: List[str] = []
    if targets:
        snapshot_added, snapshot_removed, snapshot_files = _snapshot_diff(
            task_id, targets, git_handled
        )

    total_added = git_added + snapshot_added
    total_removed = git_removed + snapshot_removed
    all_files = _unique(git_files + snapshot_files)

    if not all_files and not targets and total_added == 0 and total_removed == 0:
        # Nothing to record (no repo changes and no explicit targets provided).
        return None

    # Update the task record and persist a snapshot for auditing.
    updated = update_task(
        task_id,
        diffs=TaskDiffSummary(added=total_added, removed=total_removed).to_dict(),
        updated_ts=ts,
    )

    snapshot = DiffSnapshot(
        ts=ts,
        task_id=task_id,
        added=total_added,
        removed=total_removed,
        files=all_files,
    )
    _append_diff_snapshot(snapshot)

    publish(
        "task.diff",
        {
            "id": updated.id,
            "added": total_added,
            "removed": total_removed,
            "files": list(all_files),
        },
    )
    return snapshot


def _normalize_targets(files: Optional[Iterable[str]], workspace: Path) -> Dict[Path, _Target]:
    if not files:
        return {}

    targets: Dict[Path, _Target] = {}
    for entry in files:
        if not entry:
            continue
        candidate = Path(entry)
        abs_path = candidate if candidate.is_absolute() else (workspace / candidate)
        abs_path = abs_path.resolve()
        rel_workspace = _relative_to_workspace(abs_path, workspace)
        targets[abs_path] = _Target(abs_path=abs_path, rel_workspace=rel_workspace)
    return targets


def _relative_to_workspace(path: Path, workspace: Path) -> str:
    try:
        rel = path.relative_to(workspace)
        return rel.as_posix()
    except ValueError:
        return path.as_posix()


def _detect_git_repo(start: Path) -> Optional[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    top = result.stdout.strip()
    if not top:
        return None
    return Path(top).resolve()


def _git_numstat(
    repo_root: Path,
    workspace: Path,
    targets: Dict[Path, _Target],
) -> Tuple[int, int, List[str], Set[Path]]:
    paths = sorted({target.rel_repo for target in targets.values() if target.rel_repo})

    cmd: List[str] = [
        "git",
        "-C",
        str(repo_root),
        "--no-optional-locks",
        "diff",
        "--numstat",
    ]
    if paths:
        cmd.append("--")
        cmd.extend(paths)

    try:
        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return 0, 0, [], set()
    if result.returncode != 0:
        return 0, 0, [], set()

    added_total = removed_total = 0
    files: List[str] = []
    handled: Set[Path] = set()

    for line in result.stdout.splitlines():
        parsed = _parse_numstat_line(line)
        if not parsed:
            continue
        added, removed, rel_path = parsed
        abs_path = (repo_root / rel_path).resolve()
        files.append(_relative_to_workspace(abs_path, workspace))
        added_total += added
        removed_total += removed
        if abs_path in targets:
            handled.add(abs_path)
    return added_total, removed_total, _unique(files), handled


def _parse_numstat_line(line: str) -> Optional[Tuple[int, int, str]]:
    parts = line.strip().split("\t", 2)
    if len(parts) != 3:
        return None
    added_str, removed_str, path_field = parts
    added = _parse_int(added_str)
    removed = _parse_int(removed_str)
    normalized = _normalize_numstat_path(path_field)
    if not normalized:
        return None
    return added, removed, normalized


def _parse_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def _normalize_numstat_path(field: str) -> str:
    field = field.strip()
    if not field:
        return ""
    if " => " in field:
        return _normalize_rename(field, " => ")
    if "->" in field:
        return _normalize_rename(field, "->")
    return field


def _normalize_rename(field: str, token: str) -> str:
    cleaned = field.replace("{", "").replace("}", "")
    parts = cleaned.split(token, 1)
    if len(parts) != 2:
        return cleaned.strip()
    left, right = parts[0].strip(), parts[1].strip()
    if "/" in left:
        prefix = left.rsplit("/", 1)[0]
        if prefix:
            if right.startswith(prefix):
                return right
            return f"{prefix}/{right}"
    return right


def _snapshot_diff(
    task_id: str,
    targets: Dict[Path, _Target],
    skip: Set[Path],
) -> Tuple[int, int, List[str]]:
    added_total = removed_total = 0
    files: List[str] = []
    for abs_path, target in targets.items():
        if abs_path in skip:
            continue
        added, removed = _compute_snapshot_counts(task_id, abs_path, target.rel_workspace)
        if added or removed:
            files.append(target.rel_workspace)
        added_total += added
        removed_total += removed
    return added_total, removed_total, _unique(files)


def _compute_snapshot_counts(task_id: str, abs_path: Path, rel_path: str) -> Tuple[int, int]:
    snapshot_file = _snapshot_file(task_id, rel_path)

    previous_lines: List[str] = []
    if snapshot_file.exists():
        previous_lines = snapshot_file.read_text(encoding="utf-8", errors="ignore").splitlines()

    current_lines: List[str] = []
    file_exists = abs_path.exists()
    if file_exists:
        current_lines = abs_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    added = removed = 0
    for line in difflib.ndiff(previous_lines, current_lines):
        if line.startswith("+ "):
            added += 1
        elif line.startswith("- "):
            removed += 1

    if file_exists:
        snapshot_file.parent.mkdir(parents=True, exist_ok=True)
        snapshot_file.write_text(
            "\n".join(current_lines),
            encoding="utf-8",
        )
    elif snapshot_file.exists():
        snapshot_file.unlink()

    return added, removed


def _snapshot_file(task_id: str, rel_path: str) -> Path:
    safe_parts = [part for part in Path(rel_path).parts if part not in ("", ".", "..")]
    snapshot_root = _SNAPSHOT_ROOT / task_id / "snapshot"
    return (snapshot_root / Path(*safe_parts)).resolve()


def _append_diff_snapshot(snapshot: DiffSnapshot) -> None:
    DIFFS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DIFFS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(snapshot.to_dict(), ensure_ascii=False) + "\n")


def _unique(values: Sequence[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
