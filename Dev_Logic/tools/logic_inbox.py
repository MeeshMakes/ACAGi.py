"""CLI for managing logic inbox entries."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INBOX_PATH = Path(__file__).resolve().parent.parent / "memory" / "logic_inbox.jsonl"


def validate() -> bool:
    if not INBOX_PATH.exists():
        print("logic_inbox.jsonl not found", file=sys.stderr)
        return False
    ok = True
    with INBOX_PATH.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Line {idx}: invalid JSON: {e}", file=sys.stderr)
                ok = False
                continue
            status = obj.get("status")
            if status not in {"pending", "done"}:
                print(f"Line {idx}: invalid status '{status}'", file=sys.stderr)
                ok = False
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Logic inbox utilities")
    parser.add_argument("--validate", action="store_true", help="Validate inbox entries")
    args = parser.parse_args()
    if args.validate:
        ok = validate()
        sys.exit(0 if ok else 1)
    parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
