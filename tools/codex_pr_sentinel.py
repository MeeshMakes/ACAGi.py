"""Codex PR Sentinel orchestration script.

This module executes repository-defined validation checks whenever the GitHub
workflow triggers. The implementation favors explicit logging, richly annotated
code paths, and deterministic output so that future maintainers understand the
system without guesswork.
"""

import argparse
import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import yaml


@dataclass
class CheckResult:
    """Container for individual check metadata."""

    name: str
    command: str
    passed: bool
    output: str


def configure_logging() -> None:
    """Configure a verbose logging formatter suitable for CI environments."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_config(config_path: Path) -> dict:
    """Load the Codex sentinel configuration file."""

    if not config_path.exists():
        message = (
            "Sentinel configuration missing at %s. Ensure .github/codex_sentinel.yml "
            "is committed before running the workflow."
        )
        raise FileNotFoundError(message % config_path)

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    logging.info("Loaded sentinel configuration: version=%s", config.get("version"))
    return config


def run_command(command: str, workdir: Path) -> CheckResult:
    """Execute a shell command and capture its output for reporting."""

    logging.info("Running check command: %s", command)
    completed = subprocess.run(
        command,
        cwd=workdir,
        capture_output=True,
        text=True,
        shell=True,
        check=False,
    )

    passed = completed.returncode == 0
    output = "".join([completed.stdout or "", completed.stderr or ""])
    logging.info("Check finished with return code %s", completed.returncode)
    return CheckResult(name=command, command=command, passed=passed, output=output)


def extract_checks(config: dict) -> Iterable[dict]:
    """Yield check definitions from the loaded configuration."""

    checks = config.get("checks", [])
    for entry in checks:
        if "name" not in entry or "run" not in entry:
            logging.warning("Skipping malformed check entry: %s", entry)
            continue
        yield entry


def run_checks(check_definitions: Iterable[dict], repo_root: Path) -> List[CheckResult]:
    """Execute each configured check and collect the results."""

    results: List[CheckResult] = []
    for definition in check_definitions:
        command = definition["run"]
        result = run_command(command=command, workdir=repo_root)
        result.name = definition.get("name", command)
        results.append(result)
    return results


def write_report(report_path: Path, results: Iterable[CheckResult]) -> None:
    """Persist a human-readable report summarizing check outcomes."""

    report_lines: List[str] = ["Codex PR Sentinel Report", "==========================", ""]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        report_lines.append(f"Check: {result.name}")
        report_lines.append(f"Command: {result.command}")
        report_lines.append(f"Status: {status}")
        report_lines.append("Output:")
        report_lines.append(result.output.strip() or "<no output>")
        report_lines.append("-" * 40)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    logging.info("Wrote sentinel report to %s", report_path)


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments for the sentinel runner."""

    parser = argparse.ArgumentParser(description="Run Codex PR Sentinel checks.")
    parser.add_argument(
        "--event",
        required=True,
        help="GitHub event name that triggered the workflow.",
    )
    parser.add_argument(
        "--payload",
        required=False,
        help="Serialized JSON payload from GitHub. Stored for audit trail.",
    )
    parser.add_argument(
        "--config",
        default=".github/codex_sentinel.yml",
        help="Path to the sentinel configuration file.",
    )
    parser.add_argument(
        "--report",
        default=".codex/pr_sentinel_report.txt",
        help="Destination path for the generated report.",
    )
    return parser.parse_args()


def persist_payload(payload: str | None, destination: Path) -> None:
    """Optionally persist the GitHub event payload for auditing."""

    if not payload:
        return

    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        logging.warning("Payload is not valid JSON; writing raw contents.")
        destination.write_text(payload, encoding="utf-8")
        return

    destination.write_text(json.dumps(parsed, indent=2, sort_keys=True), encoding="utf-8")
    logging.info("Stored normalized payload at %s", destination)


def main() -> None:
    """Entry point for invoking the sentinel logic from CI."""

    configure_logging()
    args = parse_arguments()
    repo_root = Path.cwd()
    logging.info("Running Codex PR Sentinel for event: %s", args.event)

    config = load_config(Path(args.config))
    results = run_checks(extract_checks(config), repo_root)

    report_path = Path(args.report)
    write_report(report_path, results)

    payload_dir = Path(".codex")
    payload_dir.mkdir(exist_ok=True)
    persist_payload(args.payload, payload_dir / "payload.json")

    if not all(result.passed for result in results):
        logging.error("One or more sentinel checks failed.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
