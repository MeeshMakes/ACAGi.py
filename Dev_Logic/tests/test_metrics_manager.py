from __future__ import annotations

from pathlib import Path

from metrics_manager import fetch_metrics, record_metrics


def test_record_metrics_writes_to_multiple_scopes(tmp_path: Path) -> None:
    local_db = tmp_path / "local.db"
    global_db = tmp_path / "global.db"
    entries = [
        {
            "timestamp": 123.0,
            "script_path": "tools/example.py",
            "score": 0.75,
            "runtime_ms": 42.0,
            "component": "tools/example.py",
            "metadata": {"line_count": 10},
        }
    ]

    result = record_metrics(
        entries,
        scopes=("local", "global"),
        db_paths={"local": local_db, "global": global_db},
    )

    assert result == {"local": 1, "global": 1}

    local_rows = fetch_metrics(scope="local", db_paths={"local": local_db})
    global_rows = fetch_metrics(scope="global", db_paths={"global": global_db})

    assert len(local_rows) == len(global_rows) == 1
    assert local_rows[0]["script_path"] == "tools/example.py"
    assert local_rows[0]["metadata"] == {"line_count": 10}
    assert global_rows[0]["component"] == "tools/example.py"


def test_fetch_metrics_filters_and_limits(tmp_path: Path) -> None:
    db_path = tmp_path / "metrics.db"
    record_metrics(
        [
            {
                "timestamp": 50.0,
                "script_path": "a.py",
                "score": 0.5,
                "runtime_ms": 5.0,
            },
            {
                "timestamp": 150.0,
                "script_path": "b.py",
                "score": 0.9,
                "runtime_ms": 7.5,
            },
        ],
        db_paths={"local": db_path},
    )

    record_metrics(
        [
            {
                "timestamp": 250.0,
                "script_path": "b.py",
                "score": 0.6,
                "runtime_ms": 8.0,
            }
        ],
        db_paths={"local": db_path},
    )

    only_b = fetch_metrics(
        scope="local",
        script_path="b.py",
        db_paths={"local": db_path},
    )
    assert all(row["script_path"] == "b.py" for row in only_b)
    assert only_b[0]["timestamp"] >= only_b[-1]["timestamp"]

    recent = fetch_metrics(
        scope="local",
        since=100.0,
        db_paths={"local": db_path},
    )
    assert all(row["timestamp"] >= 100.0 for row in recent)

    limited = fetch_metrics(
        scope="local",
        limit=1,
        db_paths={"local": db_path},
    )
    assert len(limited) == 1
    assert limited[0]["timestamp"] == max(row["timestamp"] for row in recent)
