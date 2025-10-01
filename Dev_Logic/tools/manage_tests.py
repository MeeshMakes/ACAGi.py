"""Run Codex-Local test suites through a single entry point."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]


def build_pytest_command(pytest_args: Sequence[str]) -> list[str]:
    """Construct the pytest command using the active Python interpreter."""

    return [sys.executable, "-m", "pytest", *pytest_args]


def run_pytest(pytest_args: Sequence[str]) -> int:
    """Execute pytest with the provided arguments and return the exit code."""

    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    command = build_pytest_command(pytest_args)
    printable = " ".join(shlex.quote(part) for part in command)
    print(f"Running tests via pytest: {printable}")
    try:
        result = subprocess.run(command, cwd=REPO_ROOT, env=env)
    except FileNotFoundError as exc:  # pragma: no cover - defensive guard
        print(f"pytest invocation failed: {exc}")
        return 1
    return result.returncode


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse arguments and invoke pytest."""

    parser = argparse.ArgumentParser(description="Run Codex-Local test suites")
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Arguments forwarded to pytest (e.g. -k pattern)",
    )
    options = parser.parse_args(argv)
    return run_pytest(options.pytest_args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
