import time

from Virtual_Desktop import (
    _filter_metrics_rows,
    _flatten_metrics_summary,
    _last_run_bucket,
    _score_bucket_key,
    _score_distribution,
    _script_type_label,
)


def test_script_type_label_variants():
    assert _script_type_label("tests/test_demo.py") == "Tests"
    assert _script_type_label("tasks/card.py") == "Tasks"
    assert _script_type_label("tools/helper.py") == "Tools"
    assert _script_type_label("Virtual_Desktop.py") == "Desktop"
    assert _script_type_label("Codex_Terminal.py") == "Terminal"
    assert _script_type_label("scripts/runner.py") == "Python"
    assert _script_type_label("") == "Unknown"


def test_score_bucket_key_thresholds():
    assert _score_bucket_key(0.9) == "healthy"
    assert _score_bucket_key(0.65) == "watch"
    assert _score_bucket_key(0.25) == "critical"
    assert _score_bucket_key(None) == "unknown"


def test_last_run_bucket_thresholds():
    now = time.time()
    assert _last_run_bucket(None, now=now) == "never"
    assert _last_run_bucket(now - 10, now=now) == "recent"
    assert _last_run_bucket(now - 90000, now=now) == "stale"


def test_flatten_metrics_summary_and_filters():
    now = time.time()
    summary = {
        "generated_at": now,
        "components": {
            "tasks": {
                "scripts": {
                    "tasks/card.py": {
                        "line_count": 120,
                        "error_count": 2,
                        "last_run_ts": now - 3600,
                        "last_modified": now - 7200,
                    },
                    "tests/test_card.py": {
                        "line_count": 50,
                        "error_count": 0,
                        "last_run_ts": None,
                        "last_modified": now - 3600,
                    },
                }
            }
        },
    }
    rows = _flatten_metrics_summary(summary, now=now)
    assert len(rows) == 2

    critical_rows = [
        row for row in rows if row["script_path"] == "tasks/card.py"
    ]
    assert critical_rows
    assert critical_rows[0]["score_bucket"] == "critical"
    assert critical_rows[0]["last_run_bucket"] == "recent"

    filtered = _filter_metrics_rows(
        rows,
        script_type="Tasks",
        last_run="recent",
        score_bucket="critical",
    )
    assert len(filtered) == 1
    assert filtered[0]["script_path"] == "tasks/card.py"

    none_match = _filter_metrics_rows(
        rows,
        script_type="Tests",
        score_bucket="critical",
    )
    assert none_match == []


def test_score_distribution_counts():
    rows = [
        {"score_bucket": "healthy"},
        {"score_bucket": "healthy"},
        {"score_bucket": "watch"},
        {"score_bucket": "critical"},
        {"score_bucket": "unknown"},
        {},
    ]
    counts = _score_distribution(rows)
    assert counts["healthy"] == 2
    assert counts["watch"] == 1
    assert counts["critical"] == 1
    assert counts["unknown"] == 2
