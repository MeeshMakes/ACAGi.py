"""Utilities for collecting repository system metrics."""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Sequence

from metrics_manager import record_metrics

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS: Sequence[Path] = (
    REPO_ROOT / "Virtual_Desktop.py",
    REPO_ROOT / "Codex_Terminal.py",
    REPO_ROOT / "tasks",
    REPO_ROOT / "tools",
)
DATASETS_ROOT = REPO_ROOT / "datasets"
DEFAULT_DB_NAME = "system_metrics.db"
TASKS_FILENAME = "tasks.jsonl"
ERRORS_FILENAME = "errors.jsonl"

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ErrorSummary:
    """Container describing error counts and recent entries."""

    count: int
    recent: List[Dict[str, object]]


def _normalize_repo_path(path: str | os.PathLike[str]) -> str:
    """Return a POSIX-style path relative to the repository when possible."""

    raw = str(path).strip()
    if not raw:
        return ""
    # Normalise Windows separators.
    candidate = raw.replace("\\", "/")
    path_obj = Path(candidate)

    # Handle drive letters on Windows-like paths (`C:/...`).
    drive, _ = os.path.splitdrive(candidate)
    if drive:
        try:
            path_obj = Path(candidate)
        except Exception:
            return candidate
    try:
        resolved = path_obj.resolve()
    except FileNotFoundError:
        resolved = (REPO_ROOT / path_obj).resolve() if not path_obj.is_absolute() else path_obj
    except RuntimeError:
        resolved = path_obj

    try:
        relative = resolved.relative_to(REPO_ROOT)
    except ValueError:
        return resolved.as_posix()
    return relative.as_posix()


def _iter_python_files(target: Path) -> Iterator[Path]:
    if target.is_file() and target.suffix == ".py":
        yield target
        return
    if target.is_dir():
        for path in sorted(target.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            yield path


def _count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def _load_task_updates(tasks_file: Path) -> Mapping[str, float]:
    updates: MutableMapping[str, float] = {}
    if not tasks_file.exists():
        return updates
    try:
        with tasks_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = float(payload.get("updated_ts") or payload.get("created_ts") or 0.0)
                for file_path in payload.get("files", []) or []:
                    key = _normalize_repo_path(file_path)
                    current = updates.get(key, 0.0)
                    updates[key] = max(current, ts)
    except OSError:
        return updates
    return updates


def _load_error_map(errors_file: Path, limit: int = 5) -> Mapping[str, ErrorSummary]:
    grouped: Dict[str, ErrorSummary] = {}
    if not errors_file.exists():
        return grouped
    try:
        with errors_file.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                raw_path = payload.get("path")
                if not raw_path:
                    continue
                key = _normalize_repo_path(raw_path)
                summary = grouped.setdefault(key, ErrorSummary(count=0, recent=[]))
                summary.count += 1
                summary.recent.append(
                    {
                        "ts": float(payload.get("ts", 0.0)),
                        "level": payload.get("level"),
                        "kind": payload.get("kind"),
                        "msg": payload.get("msg"),
                    }
                )
    except OSError:
        return grouped

    for summary in grouped.values():
        summary.recent.sort(key=lambda entry: float(entry.get("ts", 0.0)), reverse=True)
        if limit > 0:
            del summary.recent[limit:]
    return grouped


def _prepare_component(
    target: Path,
    *,
    updates: Mapping[str, float],
    errors: Mapping[str, ErrorSummary],
) -> Optional[Dict[str, object]]:
    scripts: Dict[str, Dict[str, object]] = {}
    for script in _iter_python_files(target):
        try:
            rel = script.resolve().relative_to(REPO_ROOT)
            component_key = rel.as_posix()
        except ValueError:
            component_key = script.resolve().as_posix()
        line_count = _count_lines(script)
        last_modified = script.stat().st_mtime if script.exists() else None
        error_summary = errors.get(component_key, ErrorSummary(count=0, recent=[]))
        scripts[component_key] = {
            "line_count": line_count,
            "last_modified": last_modified,
            "last_run_ts": updates.get(component_key),
            "error_count": error_summary.count,
            "errors": list(error_summary.recent),
        }

    if not scripts:
        return None

    try:
        component_name = target.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        component_name = target.resolve().as_posix()

    total_lines = sum(entry["line_count"] for entry in scripts.values())
    last_run = max((entry["last_run_ts"] or 0.0) for entry in scripts.values()) if scripts else 0.0
    last_modified = max((entry["last_modified"] or 0.0) for entry in scripts.values())
    error_count = sum(int(entry["error_count"]) for entry in scripts.values())

    return {
        "component": component_name,
        "file_count": len(scripts),
        "total_lines": total_lines,
        "last_run_ts": last_run or None,
        "last_modified": last_modified or None,
        "error_count": error_count,
        "scripts": scripts,
    }

def _compute_score(payload: Mapping[str, object]) -> float:
    try:
        errors = int(payload.get("error_count") or 0)
    except (TypeError, ValueError):
        errors = 0
    if errors <= 0:
        return 1.0
    return 1.0 / (1.0 + float(errors))


def _store_metrics(
    summary: Mapping[str, object],
    *,
    db_path: Path,
    runtime_ms: Optional[float] = None,
) -> None:
    components = summary.get("components")
    if not isinstance(components, dict) or not components:
        return

    entries: List[Dict[str, object]] = []
    generated_at = float(summary.get("generated_at", time.time()))
    for component_name, component_data in components.items():
        scripts = component_data.get("scripts", {})
        if not isinstance(scripts, dict):
            continue
        file_count = int(component_data.get("file_count", 0))
        total_lines = int(component_data.get("total_lines", 0))
        for script_name, payload in scripts.items():
            metadata = {
                "file_count": file_count,
                "total_lines": total_lines,
                "line_count": payload.get("line_count"),
                "last_modified": payload.get("last_modified"),
                "last_run_ts": payload.get("last_run_ts"),
                "error_count": payload.get("error_count"),
                "errors": payload.get("errors"),
            }
            entries.append(
                {
                    "timestamp": generated_at,
                    "script_path": script_name,
                    "score": _compute_score(payload),
                    "runtime_ms": runtime_ms,
                    "component": component_name,
                    "metadata": metadata,
                }
            )

    if not entries:
        return

    record_metrics(entries, scopes=("local",), db_paths={"local": db_path})


def collect_metrics(
    targets: Optional[Iterable[os.PathLike[str] | str]] = None,
    *,
    store: bool = False,
    db_path: Optional[os.PathLike[str] | str] = None,
    datasets_root: Optional[os.PathLike[str] | str] = None,
    error_limit: int = 5,
) -> Dict[str, object]:
    """Collect filesystem, task, and error metrics for selected targets."""

    start_time = time.perf_counter()
    resolved_targets: List[Path] = []
    if targets is None:
        resolved_targets.extend(Path(path) for path in DEFAULT_TARGETS)
    else:
        for target in targets:
            resolved_targets.append(Path(target))

    dataset_root = Path(datasets_root) if datasets_root else DATASETS_ROOT
    tasks_file = dataset_root / TASKS_FILENAME
    errors_file = dataset_root / ERRORS_FILENAME

    updates = _load_task_updates(tasks_file)
    error_map = _load_error_map(errors_file, limit=error_limit)

    components: Dict[str, Dict[str, object]] = {}
    for target in resolved_targets:
        component = _prepare_component(target, updates=updates, errors=error_map)
        if component is None:
            continue
        components[component["component"]] = component

    summary: Dict[str, object] = {
        "generated_at": time.time(),
        "components": components,
    }

    runtime_ms = (time.perf_counter() - start_time) * 1000.0
    summary["runtime_ms"] = runtime_ms

    if store:
        database_path = Path(db_path) if db_path else dataset_root / DEFAULT_DB_NAME
        _store_metrics(summary, db_path=database_path, runtime_ms=runtime_ms)

    return summary


class SystemMetricsJob:
    """Background helper that refreshes metrics on a fixed cadence."""

    def __init__(
        self,
        *,
        interval: float,
        targets: Optional[Iterable[os.PathLike[str] | str]] = None,
        datasets_root: Optional[os.PathLike[str] | str] = None,
        db_path: Optional[os.PathLike[str] | str] = None,
        publish_callback: Optional[Callable[[Dict[str, object]], None]] = None,
    ) -> None:
        if interval <= 0:
            raise ValueError("interval must be positive")
        self._interval = float(interval)
        self._targets = list(targets) if targets is not None else None
        self._datasets_root = Path(datasets_root) if datasets_root else None
        self._db_path = Path(db_path) if db_path else None
        self._publish_callback = publish_callback
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._stopped = False

    def start(self) -> None:
        with self._lock:
            self._stopped = False
        self._run_now()

    def stop(self) -> None:
        with self._lock:
            self._stopped = True
            timer = self._timer
            self._timer = None
        if timer:
            timer.cancel()

    def _schedule(self) -> None:
        with self._lock:
            if self._stopped:
                return
            timer = threading.Timer(self._interval, self._run_now)
            timer.daemon = True
            self._timer = timer
            timer.start()

    def _run_now(self) -> None:
        with self._lock:
            if self._stopped:
                return
        summary: Optional[Dict[str, object]] = None
        try:
            summary = collect_metrics(
                targets=self._targets,
                store=True,
                db_path=self._db_path,
                datasets_root=self._datasets_root,
            )
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("System metrics collection failed")
        else:
            if self._publish_callback is not None and summary is not None:
                try:
                    self._publish_callback(summary)
                except Exception:
                    logger.exception("System metrics publish callback failed")
        self._schedule()


__all__ = [
    "collect_metrics",
    "SystemMetricsJob",
]
