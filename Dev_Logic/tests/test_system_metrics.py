import json
from pathlib import Path

import pytest

from metrics_manager import fetch_metrics
from tools import system_metrics


def _write_jsonl(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item) + "\n")


def test_collect_metrics_aggregates_files(tmp_path: Path) -> None:
    script = tmp_path / "module.py"
    script.write_text("print('hello')\nprint('world')\n", encoding="utf-8")

    datasets_root = tmp_path / "datasets"
    _write_jsonl(
        datasets_root / "tasks.jsonl",
        [
            {
                "id": "tsk_1",
                "updated_ts": 123.0,
                "files": [str(script)],
            }
        ],
    )
    _write_jsonl(
        datasets_root / "errors.jsonl",
        [
            {
                "ts": 120.0,
                "level": "ERROR",
                "kind": "RuntimeError",
                "msg": "boom",
                "path": str(script),
            },
            {
                "ts": 100.0,
                "level": "WARNING",
                "kind": "UserWarning",
                "msg": "heads up",
                "path": str(script),
            },
        ],
    )

    summary = system_metrics.collect_metrics(
        targets=[script],
        datasets_root=datasets_root,
        store=False,
        error_limit=1,
    )

    assert "generated_at" in summary
    assert summary["runtime_ms"] >= 0
    components = summary["components"]
    assert isinstance(components, dict)
    assert components

    component_data = next(iter(components.values()))
    assert component_data["file_count"] == 1
    assert component_data["total_lines"] == 2
    assert component_data["error_count"] == 1

    script_metrics = next(iter(component_data["scripts"].values()))
    assert script_metrics["line_count"] == 2
    assert script_metrics["last_run_ts"] == pytest.approx(123.0)
    assert script_metrics["error_count"] == 1
    errors = script_metrics["errors"]
    assert errors
    assert errors[0]["msg"] == "boom"


def test_collect_metrics_persists_via_manager(tmp_path: Path) -> None:
    script = tmp_path / "app.py"
    script.write_text("print('x')\n", encoding="utf-8")
    datasets_root = tmp_path / "datasets"
    db_path = tmp_path / "metrics.db"

    summary = system_metrics.collect_metrics(
        targets=[script],
        datasets_root=datasets_root,
        db_path=db_path,
        store=True,
    )

    assert db_path.exists()

    rows = fetch_metrics(scope="local", db_paths={"local": db_path})
    assert rows, "expected at least one metrics row"
    row = rows[0]
    assert row["timestamp"] == pytest.approx(summary["generated_at"])
    assert row["runtime_ms"] == pytest.approx(summary["runtime_ms"])
    assert row["score"] == pytest.approx(1.0)
    assert row["script_path"].endswith("app.py")
    assert row["component"].endswith("app.py")
    metadata = row["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["line_count"] == 1
