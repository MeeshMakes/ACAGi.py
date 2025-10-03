from __future__ import annotations

from pathlib import Path

import pytest

from Codex_Terminal import run_checked
from safety import SafetyViolation, manager as safety_manager


def test_protected_file_overwrite_blocked(tmp_path: Path):
    protected = tmp_path / "Agent.md"
    protected.write_text("initial", encoding="utf-8")
    safety_manager.add_protected_path(protected)
    try:
        with pytest.raises(SafetyViolation):
            protected.write_text("overwrite", encoding="utf-8")
        with protected.open("a", encoding="utf-8") as handle:
            handle.write("\nappend")
        contents = protected.read_text(encoding="utf-8")
        assert "initial" in contents
        assert "append" in contents
    finally:
        safety_manager.remove_protected_path(protected)


def test_run_checked_blocks_risky_command(tmp_path: Path):
    messages: list[str] = []
    token = safety_manager.add_notifier(messages.append)
    try:
        rc, out, err = run_checked(["rm", "-rf", "/"], cwd=tmp_path)
    finally:
        safety_manager.remove_notifier(token)
    assert rc != 0
    assert not out
    assert "Blocked command" in err
    assert any("Blocked command" in msg for msg in messages)


def test_run_checked_executes_when_confirmed(tmp_path: Path):
    victim = tmp_path / "victim"
    victim.mkdir()
    (victim / "file.txt").write_text("data", encoding="utf-8")

    messages: list[str] = []
    token = safety_manager.add_notifier(messages.append)
    safety_manager.set_confirmer(lambda prompt, command: True)
    try:
        rc, out, err = run_checked(
            ["rm", "-rf", victim.as_posix()],
            cwd=tmp_path,
        )
    finally:
        safety_manager.set_confirmer(None)
        safety_manager.remove_notifier(token)

    assert rc == 0
    assert victim.exists() is False
    assert any("Approved" in msg for msg in messages)
    assert err == ""
