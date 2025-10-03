"""Tests covering interpreter path normalisation behaviour."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import python_runtime


@pytest.fixture()
def cleanup_home_artifacts():
    """Ensure temporary files created in the user's home directory are removed."""

    created: list[Path] = []

    yield created

    for path in created:
        try:
            path.unlink()
        except FileNotFoundError:
            continue


def test_executable_env_expands_user_directory(monkeypatch, cleanup_home_artifacts):
    """Environment overrides should honour ``~`` expansion before validation."""

    fake_executable = Path.home() / "acagi-python-env-test"
    fake_executable.write_text("#!/usr/bin/env python3\n")
    cleanup_home_artifacts.append(fake_executable)

    monkeypatch.setenv(
        python_runtime.EXECUTABLE_ENV,
        f"~/{fake_executable.name}",
    )

    assert python_runtime._executable_from_env() == fake_executable


def test_config_preferences_accept_relative_interpreter(tmp_path, monkeypatch):
    """Interpreter paths in config files should resolve relative to the file."""

    interpreter = tmp_path / "bin" / "python"
    interpreter.parent.mkdir()
    interpreter.write_text("#!/usr/bin/env python3\n")

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_path = config_dir / "python_runtime.json"
    config_path.write_text(
        json.dumps({"executable": "../bin/python"}),
        encoding="utf-8",
    )

    monkeypatch.setenv(python_runtime.CONFIG_ENV, str(config_path))

    preferences = python_runtime._load_config_preferences()

    assert preferences["executable"] == interpreter.resolve()


def test_config_candidates_expand_user_and_relative(monkeypatch, tmp_path, cleanup_home_artifacts):
    """``ACAGI_PYTHON_CONFIG`` accepts ``~`` and relative paths for discovery."""

    home_config = Path.home() / "python-runtime-home.json"
    home_config.write_text("{}", encoding="utf-8")
    cleanup_home_artifacts.append(home_config)

    monkeypatch.setenv(python_runtime.CONFIG_ENV, f"~/{home_config.name}")
    first_candidate = next(iter(python_runtime._config_candidates()))
    assert first_candidate == home_config

    relative_config = tmp_path / "configs" / "python_runtime.ini"
    relative_config.parent.mkdir()
    relative_config.write_text("", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(python_runtime.CONFIG_ENV, "configs/python_runtime.ini")

    first_candidate = next(iter(python_runtime._config_candidates()))
    assert first_candidate == relative_config.resolve()
