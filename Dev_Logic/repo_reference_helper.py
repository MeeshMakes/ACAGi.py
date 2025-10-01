"""Repository reference helper for chat input suggestions."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set

# Optional Qt imports (guarded for pure-Python usage/tests)
try:  # pragma: no cover - import guard
    from PySide6.QtCore import QObject, QTimer, Signal, QFileSystemWatcher
    _HAS_QT = True
except Exception:  # pragma: no cover - fallback when PySide6 absent
    QObject = object  # type: ignore[assignment]
    QTimer = None  # type: ignore[assignment]
    Signal = None  # type: ignore[assignment]
    QFileSystemWatcher = None  # type: ignore[assignment]
    _HAS_QT = False

from memory_manager import RepositoryIndex

logger = logging.getLogger(__name__)


def _normalize_extra_roots(repo_root: Path, roots: Optional[Sequence[Path | str]]) -> List[Path]:
    extras: List[Path] = []
    if not roots:
        return extras
    try:
        base = repo_root.resolve()
    except Exception:
        base = repo_root
    seen: Set[Path] = {base}
    for entry in roots:
        if not entry:
            continue
        try:
            candidate = Path(entry).expanduser().resolve()
        except Exception:
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        extras.append(candidate)
    return extras


@dataclass(frozen=True)
class RepoReference:
    """Lightweight reference describing a repository file or directory."""

    absolute_path: Path
    relative_path: str
    kind: str  # "file" or "directory"

    def display_label(self) -> str:
        suffix = "/" if self.kind == "directory" else ""
        return f"{self.relative_path}{suffix}"


class RepoReferenceIndex:
    """Maintain an in-memory list of repository file and directory references."""

    def __init__(
        self,
        repo_root: Path,
        *,
        repository_index: Optional[RepositoryIndex] = None,
        extra_roots: Optional[Sequence[Path | str]] = None,
    ) -> None:
        self.repo_root = Path(repo_root).resolve()
        self._extra_roots = _normalize_extra_roots(self.repo_root, extra_roots)
        self._allowed_roots: List[Path] = [self.repo_root] + self._extra_roots
        self.repository_index = repository_index or RepositoryIndex(
            repo_root=self.repo_root,
            extra_roots=self._extra_roots,
        )
        self._references: List[RepoReference] = []

    # ------------------------------------------------------------------
    # Refresh + query
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Refresh the cached references from the repository index."""

        references: List[RepoReference] = []
        file_paths = self._gather_file_paths()
        seen_dirs: Dict[Path, None] = {}

        for file_path in sorted(file_paths):
            rel = self._to_relative(file_path)
            references.append(
                RepoReference(absolute_path=file_path, relative_path=rel, kind="file")
            )
            for parent in file_path.parents:
                if parent == self.repo_root:
                    break
                if parent in seen_dirs:
                    continue
                seen_dirs[parent] = None
                references.append(
                    RepoReference(
                        absolute_path=parent,
                        relative_path=self._to_relative(parent),
                        kind="directory",
                    )
                )

        references.sort(key=lambda ref: (0 if ref.kind == "file" else 1, ref.relative_path.lower()))
        self._references = references

    def suggestions(self, query: str, limit: int = 5) -> List[RepoReference]:
        """Return matching references for ``query`` ordered by relevance."""

        text = (query or "").strip().lower()
        if not text:
            return []

        matches: List[tuple[int, int, RepoReference]] = []
        for ref in self._references:
            rel_lower = ref.relative_path.lower()
            name_lower = ref.absolute_path.name.lower()
            if text in rel_lower or text in name_lower:
                prefix_match = 0 if rel_lower.startswith(text) or name_lower.startswith(text) else 1
                matches.append((prefix_match, len(rel_lower), ref))

        matches.sort()
        return [ref for _, _, ref in matches[:limit]]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def entries(self) -> List[RepoReference]:
        return list(self._references)

    def _to_relative(self, path: Path) -> str:
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path
        for root in self._allowed_roots:
            try:
                rel = resolved.relative_to(root)
            except ValueError:
                continue
            rel_text = rel.as_posix()
            if root == self.repo_root:
                return rel_text
            prefix = root.name or root.as_posix()
            return f"{prefix}/{rel_text}" if rel_text else prefix
        return resolved.as_posix()

    def _match_allowed_root(self, value: object) -> Optional[Path]:
        if not value:
            return None
        try:
            candidate = Path(str(value)).expanduser().resolve()
        except Exception:
            return None
        for root in self._allowed_roots:
            if candidate == root:
                return root
        return None

    def _resolve_segment_path(self, base_root: Path, relative_path: str) -> Optional[Path]:
        try:
            candidate = Path(relative_path)
        except Exception:
            return None
        try:
            if candidate.is_absolute():
                resolved = candidate.resolve()
            else:
                resolved = (base_root / candidate).resolve()
        except Exception:
            return None
        try:
            resolved.relative_to(base_root)
        except ValueError:
            return None
        return resolved

    def _gather_file_paths(self) -> List[Path]:
        paths = set()
        segments: Iterable[Dict[str, object]] = []

        try:
            self.repository_index.load()
            segments = list(self.repository_index.iter_segments())
        except Exception:
            segments = []

        if not segments:
            try:
                self.repository_index.rebuild()
                self.repository_index.load()
                segments = list(self.repository_index.iter_segments())
            except Exception as exc:  # pragma: no cover - logged for visibility
                logger.debug("RepoReferenceIndex rebuild failed: %s", exc)
                segments = []

        allowed_set = {root for root in self._allowed_roots}
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            path_str = str(segment.get("path") or "")
            if not path_str:
                continue
            metadata = segment.get("metadata")
            base_root = None
            if isinstance(metadata, dict):
                base_root = self._match_allowed_root(metadata.get("scan_root"))
            if base_root is None:
                base_root = self.repo_root
            if base_root not in allowed_set:
                continue
            resolved = self._resolve_segment_path(base_root, path_str)
            if resolved is None:
                continue
            if resolved.is_file():
                paths.add(resolved)

        if not paths:
            for root in self._allowed_roots:
                if not root.exists():
                    continue
                for file_path in root.rglob("*"):
                    if file_path.is_file():
                        try:
                            resolved = file_path.resolve()
                        except Exception:
                            continue
                        paths.add(resolved)

        return list(paths)


if _HAS_QT:

    class RepoReferenceHelper(QObject):
        """Qt-aware helper that refreshes repository references as the workspace changes."""

        refreshed = Signal()  # type: ignore[assignment]

        def __init__(
            self,
            repo_root: Path,
            *,
            parent: Optional[QObject] = None,
            repository_index: Optional[RepositoryIndex] = None,
            embed_contents: bool = True,
            case_sensitive: bool = False,
            token_guard: bool = True,
            extra_roots: Optional[Sequence[Path | str]] = None,
        ) -> None:
            super().__init__(parent)
            self.repo_root = Path(repo_root).resolve()
            self._extra_roots = _normalize_extra_roots(self.repo_root, extra_roots)
            self.index = RepoReferenceIndex(
                self.repo_root,
                repository_index=repository_index,
                extra_roots=self._extra_roots,
            )
            self.index.refresh()

            self.embed_contents = bool(embed_contents)
            self.case_sensitive = bool(case_sensitive)
            self.token_guard = bool(token_guard)

            self._watcher = QFileSystemWatcher(self)  # type: ignore[assignment]
            self._watcher.directoryChanged.connect(self._schedule_refresh)
            self._watcher.fileChanged.connect(self._schedule_refresh)

            self._debounce = QTimer(self)  # type: ignore[assignment]
            self._debounce.setSingleShot(True)
            self._debounce.setInterval(300)
            self._debounce.timeout.connect(self.refresh)

            self._register_watch_paths()

        # ------------------------------------------------------------------
        # Public API
        # ------------------------------------------------------------------
        def refresh(self) -> None:
            self.index.refresh()
            self.refreshed.emit()

        def suggestions(self, query: str, limit: int = 5) -> List[RepoReference]:
            return self.index.suggestions(query, limit)

        # ------------------------------------------------------------------
        # Internals
        # ------------------------------------------------------------------
        def _register_watch_paths(self) -> None:
            for root in [self.repo_root] + self._extra_roots:
                if not root.exists():
                    continue
                try:
                    self._watcher.addPath(str(root))
                except Exception as exc:  # pragma: no cover - watcher limitations
                    logger.debug("Failed to watch repo root %s: %s", root, exc)

            index_path = getattr(self.index.repository_index, "index_path", None)
            if index_path:
                path_obj = Path(index_path)
                if path_obj.exists():
                    try:
                        self._watcher.addPath(str(path_obj))
                    except Exception as exc:  # pragma: no cover - watcher limitations
                        logger.debug("Failed to watch index %s: %s", path_obj, exc)

        def _schedule_refresh(self, _path: str) -> None:
            self._debounce.start()

else:

    class RepoReferenceHelper:  # pragma: no cover - runtime guard
        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError("PySide6 is required to use RepoReferenceHelper")

        def refresh(self) -> None:
            raise RuntimeError("PySide6 is required to use RepoReferenceHelper")

        def suggestions(self, query: str, limit: int = 5) -> List[RepoReference]:
            raise RuntimeError("PySide6 is required to use RepoReferenceHelper")
