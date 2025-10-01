"""Helpers for persisting and querying script metrics."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parent
DATASETS_ROOT = REPO_ROOT / "datasets"
DEFAULT_DB_PATHS: Mapping[str, Path] = {
    "local": DATASETS_ROOT / "local.db",
    "global": DATASETS_ROOT / "global.db",
}
_TABLE_NAME = "metrics"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {_TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            script_path TEXT NOT NULL,
            score REAL,
            runtime_ms REAL,
            component TEXT,
            metadata TEXT
        )
        """
    )
    conn.execute(
        f"""
        CREATE INDEX IF NOT EXISTS idx_{_TABLE_NAME}_script_ts
        ON {_TABLE_NAME} (script_path, timestamp)
        """
    )


def _normalise_entry(entry: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    script_path = entry.get("script_path")
    if not script_path:
        return None
    timestamp = entry.get("timestamp")
    ts = float(timestamp) if timestamp is not None else time.time()
    metadata = entry.get("metadata")
    if metadata is not None and not isinstance(metadata, str):
        try:
            metadata_json = json.dumps(metadata, ensure_ascii=False)
        except (TypeError, ValueError):
            metadata_json = None
    else:
        metadata_json = metadata if isinstance(metadata, str) else None
    return {
        "timestamp": ts,
        "script_path": str(script_path),
        "score": float(entry.get("score")) if entry.get("score") is not None else None,
        "runtime_ms": float(entry.get("runtime_ms")) if entry.get("runtime_ms") is not None else None,
        "component": entry.get("component"),
        "metadata": metadata_json,
    }


def _resolve_scopes(
    scopes: Sequence[str] | str | None,
    db_paths: Optional[Mapping[str, Path | str]] = None,
) -> Dict[str, Path]:
    scope_list: Sequence[str]
    if scopes is None:
        scope_list = ("local",)
    elif isinstance(scopes, str):
        scope_list = (scopes,)
    else:
        scope_list = scopes

    resolved: Dict[str, Path] = {}
    overrides: Dict[str, Path] = {}
    if db_paths:
        overrides = {key: Path(value) for key, value in db_paths.items()}
    for scope in scope_list:
        if scope in overrides:
            resolved[scope] = overrides[scope]
        else:
            default_path = DEFAULT_DB_PATHS.get(scope)
            if default_path is None:
                raise KeyError(f"Unknown metrics scope: {scope}")
            resolved[scope] = default_path
    return resolved


def _write_entries(db_path: Path, entries: Sequence[Dict[str, Any]]) -> int:
    if not entries:
        return 0
    _ensure_parent(db_path)
    with sqlite3.connect(db_path) as conn:
        _ensure_schema(conn)
        conn.executemany(
            f"""
            INSERT INTO {_TABLE_NAME} (timestamp, script_path, score, runtime_ms, component, metadata)
            VALUES (:timestamp, :script_path, :score, :runtime_ms, :component, :metadata)
            """,
            entries,
        )
        conn.commit()
        return conn.total_changes


def record_metrics(
    entries: Iterable[Mapping[str, Any]],
    *,
    scopes: Sequence[str] | str | None = ("local",),
    db_paths: Optional[Mapping[str, Path | str]] = None,
) -> Dict[str, int]:
    """Persist metrics ``entries`` into the configured database scopes."""

    materialised: List[Dict[str, Any]] = []
    for entry in entries:
        normalised = _normalise_entry(entry)
        if normalised is not None:
            materialised.append(normalised)
    if not materialised:
        return {}

    resolved_paths = _resolve_scopes(scopes, db_paths=db_paths)
    results: Dict[str, int] = {}
    for scope, path in resolved_paths.items():
        results[scope] = _write_entries(path, materialised)
    return results


def fetch_metrics(
    *,
    scope: str = "local",
    script_path: Optional[str] = None,
    since: Optional[float] = None,
    limit: Optional[int] = None,
    db_paths: Optional[Mapping[str, Path | str]] = None,
) -> List[Dict[str, Any]]:
    """Fetch metrics rows from the requested scope."""

    resolved_paths = _resolve_scopes(scope, db_paths=db_paths)
    db_path = next(iter(resolved_paths.values()))
    if not db_path.exists():
        return []

    query = [
        f"SELECT id, timestamp, script_path, score, runtime_ms, component, metadata FROM {_TABLE_NAME}",
    ]
    clauses: List[str] = []
    params: List[Any] = []
    if script_path:
        clauses.append("script_path = ?")
        params.append(script_path)
    if since is not None:
        clauses.append("timestamp >= ?")
        params.append(float(since))
    if clauses:
        query.append(" WHERE " + " AND ".join(clauses))
    query.append(" ORDER BY timestamp DESC, id DESC")
    if limit is not None:
        query.append(" LIMIT ?")
        params.append(int(limit))

    with sqlite3.connect(db_path) as conn:
        _ensure_schema(conn)
        rows = list(conn.execute("".join(query), params))

    results: List[Dict[str, Any]] = []
    for row in rows:
        ident, ts, path, score, runtime, component, metadata_json = row
        metadata_obj: Any
        if metadata_json is None:
            metadata_obj = None
        else:
            try:
                metadata_obj = json.loads(metadata_json)
            except json.JSONDecodeError:
                metadata_obj = metadata_json
        results.append(
            {
                "id": int(ident),
                "timestamp": float(ts),
                "script_path": str(path),
                "score": float(score) if score is not None else None,
                "runtime_ms": float(runtime) if runtime is not None else None,
                "component": component,
                "metadata": metadata_obj,
            }
        )
    return results


__all__ = ["record_metrics", "fetch_metrics"]
