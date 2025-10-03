"""Utilities for maintaining the Codex logic inbox and memory schema."""

from tools.python_runtime import ensure_supported_python

ensure_supported_python()

import argparse
import json
import logging
from pathlib import Path
from typing import Iterable


def configure_logging() -> None:
    """Initialize verbose logging for deterministic CLI feedback."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def read_jsonl(path: Path) -> Iterable[dict]:
    """Yield JSON objects from a JSON Lines file."""

    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                logging.warning("Skipping empty line %s in %s", index, path)
                continue
            try:
                yield json.loads(stripped)
            except json.JSONDecodeError as error:
                message = (
                    f"Invalid JSON on line {index} of {path}: {error.msg}"
                )
                raise ValueError(message) from error


def validate_inbox(path: Path) -> None:
    """Validate that each inbox entry includes the required fields."""

    required_fields = {"id", "title", "status"}
    for entry in read_jsonl(path):
        missing = required_fields - entry.keys()
        if missing:
            message = (
                f"Inbox entry {entry} is missing required fields: {sorted(missing)}"
            )
            raise ValueError(message)
    logging.info("Logic inbox validation succeeded for %s", path)


def validate_memory(path: Path) -> None:
    """Ensure the codex memory document contains expected top-level keys."""

    data = json.loads(path.read_text(encoding="utf-8"))
    expected_keys = {"version", "last_updated", "stable_lessons", "procedures", "tooling"}
    missing = expected_keys - data.keys()
    if missing:
        message = (
            f"Memory file {path} is missing required keys: {sorted(missing)}"
        )
        raise ValueError(message)
    logging.info("Memory schema validation succeeded for %s", path)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for logic inbox tooling."""

    parser = argparse.ArgumentParser(description="Manage Codex logic inbox artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a JSONL logic inbox file.")
    validate_parser.add_argument("file", type=Path, help="Path to the logic inbox JSONL file.")

    memory_parser = subparsers.add_parser(
        "validate-memory",
        help="Validate the structured memory JSON document.",
    )
    memory_parser.add_argument("file", type=Path, help="Path to the memory JSON file.")

    return parser.parse_args()


def main() -> None:
    """CLI entry point for logic inbox validation tasks."""

    configure_logging()
    args = parse_args()

    if args.command == "validate":
        validate_inbox(args.file)
    elif args.command == "validate-memory":
        validate_memory(args.file)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
