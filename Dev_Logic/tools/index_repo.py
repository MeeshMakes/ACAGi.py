"""CLI entry point for building and querying the repository text index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, List, Optional, Sequence

from memory_manager import RepositoryIndex


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_default_repo_root(),
        help="Repository root to index (defaults to project root).",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Optional datasets directory (defaults to <repo>/datasets).",
    )
    parser.add_argument(
        "--no-embed",
        action="store_true",
        help="Skip embedding generation (querying will be disabled).",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("rebuild", help="Rebuild the repository index (default).")

    query_parser = subparsers.add_parser("query", help="Query the repository index.")
    query_parser.add_argument("--text", required=True, help="Text to search for.")
    query_parser.add_argument(
        "--limit", type=int, default=5, help="Maximum number of results to display (default: 5)."
    )

    return parser


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _resolve_path(value: Optional[Path]) -> Optional[Path]:
    if value is None:
        return None
    return value.expanduser().resolve()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = _resolve_path(args.repo_root)
    data_root = _resolve_path(args.data_root)

    index = RepositoryIndex(
        repo_root=repo_root,
        data_root=data_root,
        enable_embeddings=not args.no_embed,
    )

    command = args.command or "rebuild"

    if command == "rebuild":
        summary = index.rebuild()
        payload = {
            "files_indexed": summary.get("files_indexed", 0),
            "segments": summary.get("segments", 0),
            "timestamp": summary.get("timestamp"),
            "index_path": str(summary.get("index_path")),
        }
        _print_json(payload)
        return 0

    if command == "query":
        if args.no_embed:
            parser.error("--no-embed cannot be used when querying the index.")
        results: List[dict[str, Any]] = index.search(args.text, k=args.limit)
        _print_json(results)
        return 0

    parser.error(f"Unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
