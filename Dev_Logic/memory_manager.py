from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import re
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Set, Tuple

Vector = List[float]
TextEmbedder = Callable[[str], Sequence[float]]
ImageEmbedder = Callable[[Path], Sequence[float]]

__all__ = ["MemoryManager", "RepositoryIndex", "TextEmbedder", "ImageEmbedder"]


_FALLBACK_EMBED_DIM = 16
_REPO_DEFAULT_EXCLUDE = {
    ".git",
    "__pycache__",
    "datasets",
    "errors",
    "memory",
    "Archived Conversations",
}
_MAX_INDEX_FILE_SIZE = 256_000
_WINDOW_SIZE = 60
_WINDOW_OVERLAP = 10


def _hash_embedding(data: bytes, dims: int = _FALLBACK_EMBED_DIM) -> Vector:
    """Return a deterministic unit vector for ``data`` using BLAKE2b."""

    if not data:
        return [0.0] * dims

    digest = hashlib.blake2b(data, digest_size=dims * 4).digest()
    ints = [int.from_bytes(digest[i : i + 4], "big", signed=False) for i in range(0, len(digest), 4)]
    vec = [value / 4294967295.0 for value in ints]
    norm = math.sqrt(sum(component * component for component in vec))
    if norm == 0:
        return vec
    return [component / norm for component in vec]


def _fallback_text_embedding(text: str) -> Vector:
    return _hash_embedding(text.encode("utf-8"))


def _fallback_image_embedding(path: Path) -> Vector:
    try:
        data = path.read_bytes()
    except OSError:
        data = b""
    return _hash_embedding(data)


def _fallback_repo_embedding(text: str) -> Vector:
    tokens = [token for token in re.findall(r"[A-Za-z0-9_]+", text.lower()) if token]
    if not tokens:
        return _hash_embedding(text.encode("utf-8"))
    dims = _FALLBACK_EMBED_DIM
    vec = [0.0] * dims
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % dims
        vec[index] += 1.0
    norm = math.sqrt(sum(component * component for component in vec))
    if norm == 0:
        return vec
    return [component / norm for component in vec]


def _ensure_vector(value: Any) -> Vector:
    if isinstance(value, list):
        result: Vector = []
        for item in value:
            try:
                result.append(float(item))
            except (TypeError, ValueError):
                return []
        return result
    return []


def _cosine(a: Vector, b: Vector) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(y * y for y in b))
    if da == 0 or db == 0:
        return 0.0
    return dot / (da * db)


@dataclass(slots=True)
class _ImageRecord:
    session: str
    entry_id: str
    image_path: str
    image_embedding: Vector
    ocr_embedding: Vector
    text_embedding: Vector
    text: str
    ocr_text: str
    metadata: Dict[str, Any]
    tags: List[str]
    timestamp: float

    def score(self, query_vec: Vector) -> float:
        scores = []
        if self.image_embedding:
            scores.append(_cosine(query_vec, self.image_embedding))
        if self.ocr_embedding:
            scores.append(_cosine(query_vec, self.ocr_embedding))
        if self.text_embedding:
            scores.append(_cosine(query_vec, self.text_embedding))
        return max(scores) if scores else 0.0


@dataclass(slots=True)
class _RepoSegment:
    path: Path
    start_line: int
    end_line: int
    text: str
    metadata: Dict[str, Any]


@dataclass(slots=True)
class _RepoIndexRecord:
    identifier: str
    path: str
    start_line: int
    end_line: int
    text: str
    embedding: Vector
    metadata: Dict[str, Any]
    timestamp: float

    def score(self, query_vec: Vector) -> float:
        if not self.embedding or not query_vec:
            return 0.0
        return _cosine(query_vec, self.embedding)


def _segment_identifier(path: str, start_line: int, end_line: int) -> str:
    payload = f"{path}:{start_line}:{end_line}".encode("utf-8", "ignore")
    return hashlib.blake2b(payload, digest_size=16).hexdigest()


class MemoryManager:
    """Append-only conversation memory with text and image embeddings."""

    def __init__(
        self,
        data_root: Optional[Path | str] = None,
        *,
        text_embedder: Optional[TextEmbedder] = None,
        image_embedder: Optional[ImageEmbedder] = None,
        enable_embeddings: bool = True,
    ) -> None:
        base = Path(data_root) if data_root is not None else Path(__file__).resolve().parent / "datasets"
        self.data_root = base
        self.conversations_dir = self.data_root / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        self.enable_embeddings = enable_embeddings
        self._text_embedder = text_embedder or _fallback_text_embedding
        self._image_embedder = image_embedder or _fallback_image_embedding
        self._lock = RLock()
        self._image_cache: List[_ImageRecord] = []
        self._cache_loaded = False

    def log_interaction(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        images: Optional[Sequence[Path | str]] = None,
        ocr_map: Optional[Mapping[str, str]] = None,
        tags: Optional[Sequence[str]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Append a conversation record for ``session_id``.

        Parameters
        ----------
        session_id:
            Name of the logical conversation folder.
        role:
            Speaker associated with ``content`` (e.g. ``"user"``).
        content:
            Plain-text message body.
        images:
            Optional collection of image paths associated with the turn.
        ocr_map:
            Mapping of image path (stem, name, or resolved path) to OCR text.
        tags:
            Optional labels describing the interaction.
        metadata:
            Extra metadata persisted alongside the entry.
        """

        if not session_id:
            raise ValueError("session_id is required")

        session_dir = self.conversations_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        dataset_path = session_dir / "conversation.jsonl"

        timestamp = time.time()
        entry_id = uuid.uuid4().hex
        tag_list = [str(tag) for tag in (tags or [])]
        meta: Dict[str, Any] = dict(metadata or {})

        image_payloads: List[Dict[str, Any]] = []
        record_source: List[tuple[str, Vector, Vector, str]] = []
        ocr_texts: List[str] = []

        for raw in images or []:
            img_path = Path(raw)
            path_str = img_path.as_posix()
            ocr_text = _resolve_ocr_text(img_path, ocr_map)
            ocr_texts.append(ocr_text)
            ocr_vec = self._embed_text(ocr_text) if (self.enable_embeddings and ocr_text) else []
            img_vec = self._embed_image(img_path) if self.enable_embeddings else []
            payload = {
                "path": path_str,
                "name": img_path.name,
                "ocr_text": ocr_text,
                "ocr_embedding": ocr_vec,
                "image_embedding": img_vec,
            }
            image_payloads.append(payload)
            record_source.append((path_str, img_vec, ocr_vec, ocr_text))

        combined_sources = [content.strip()]
        combined_sources.extend(text.strip() for text in ocr_texts if text.strip())
        combined_text = "\n".join([text for text in combined_sources if text])
        text_embedding = self._embed_text(combined_text) if (self.enable_embeddings and combined_text) else []

        entry = {
            "id": entry_id,
            "session": session_id,
            "ts": timestamp,
            "role": role,
            "text": content,
            "text_embedding": text_embedding,
            "images": image_payloads,
            "tags": tag_list,
            "metadata": meta,
        }

        serialised = json.dumps(entry, ensure_ascii=False)

        with self._lock:
            with dataset_path.open("a", encoding="utf-8") as fh:
                fh.write(serialised + "\n")
            if self._cache_loaded:
                for path_str, img_vec, ocr_vec, ocr_text in record_source:
                    if not (img_vec or ocr_vec or text_embedding):
                        continue
                    self._image_cache.append(
                        _ImageRecord(
                            session=session_id,
                            entry_id=entry_id,
                            image_path=path_str,
                            image_embedding=list(img_vec),
                            ocr_embedding=list(ocr_vec),
                            text_embedding=list(text_embedding),
                            text=content,
                            ocr_text=ocr_text,
                            metadata=dict(meta),
                            tags=list(tag_list),
                            timestamp=timestamp,
                        )
                    )

        return entry

    def search_images(
        self,
        query: str,
        k: int = 5,
        *,
        session_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return the ``k`` most similar image entries for ``query``."""

        if not self.enable_embeddings or k <= 0:
            return []

        query_text = query.strip()
        if not query_text:
            return []

        query_vec = self._embed_text(query_text)
        if not query_vec:
            return []

        with self._lock:
            self._ensure_cache_locked()
            records = list(self._image_cache)

        hits: List[tuple[float, _ImageRecord]] = []
        for record in records:
            if session_filter and record.session != session_filter:
                continue
            score = record.score(query_vec)
            if score <= 0:
                continue
            hits.append((score, record))

        hits.sort(key=lambda item: item[0], reverse=True)

        results: List[Dict[str, Any]] = []
        for score, record in hits[:k]:
            results.append(
                {
                    "score": score,
                    "session": record.session,
                    "entry_id": record.entry_id,
                    "image_path": record.image_path,
                    "text": record.text,
                    "ocr_text": record.ocr_text,
                    "metadata": dict(record.metadata),
                    "tags": list(record.tags),
                    "timestamp": record.timestamp,
                }
            )
        return results

    def _ensure_cache_locked(self) -> None:
        if self._cache_loaded:
            return

        cache: List[_ImageRecord] = []
        for session_dir in sorted(self.conversations_dir.iterdir()):
            if not session_dir.is_dir():
                continue
            dataset_path = session_dir / "conversation.jsonl"
            if not dataset_path.exists():
                continue
            with dataset_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    images = entry.get("images") or []
                    text_embedding = _ensure_vector(entry.get("text_embedding"))
                    metadata = dict(entry.get("metadata") or {})
                    tags = [str(tag) for tag in entry.get("tags") or []]
                    session_name = str(entry.get("session") or session_dir.name)
                    entry_id = str(entry.get("id") or "")
                    text = str(entry.get("text") or "")
                    timestamp = float(entry.get("ts") or 0.0)
                    for img in images:
                        if not isinstance(img, Mapping):
                            continue
                        path_str = str(img.get("path") or "")
                        if not path_str:
                            continue
                        image_embedding = _ensure_vector(img.get("image_embedding"))
                        ocr_embedding = _ensure_vector(img.get("ocr_embedding"))
                        ocr_text = str(img.get("ocr_text") or "")
                        if not (image_embedding or ocr_embedding or text_embedding):
                            continue
                        cache.append(
                            _ImageRecord(
                                session=session_name,
                                entry_id=entry_id,
                                image_path=path_str,
                                image_embedding=image_embedding,
                                ocr_embedding=ocr_embedding,
                                text_embedding=text_embedding,
                                text=text,
                                ocr_text=ocr_text,
                                metadata=dict(metadata),
                                tags=list(tags),
                                timestamp=timestamp,
                            )
                        )
        self._image_cache = cache
        self._cache_loaded = True

    def _embed_text(self, text: str) -> Vector:
        if not text:
            return []
        vec = self._text_embedder(text)
        return [float(v) for v in vec]

    def _embed_image(self, path: Path) -> Vector:
        vec = self._image_embedder(path)
        return [float(v) for v in vec]


class RepositoryIndex:
    """Build and query a lightweight repository text index."""

    def __init__(
        self,
        repo_root: Optional[Path | str] = None,
        data_root: Optional[Path | str] = None,
        *,
        text_embedder: Optional[TextEmbedder] = None,
        enable_embeddings: bool = True,
        include_extensions: Optional[Sequence[str]] = None,
        exclude_dirs: Optional[Sequence[str]] = None,
        extra_roots: Optional[Sequence[Path | str]] = None,
    ) -> None:
        base_repo = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parent
        self.repo_root = base_repo.resolve()
        base_data = Path(data_root) if data_root is not None else Path(__file__).resolve().parent / "datasets"
        self.data_root = base_data.resolve()
        self.index_dir = self.data_root / "repo_index"
        self.index_path = self.index_dir / "index.jsonl"
        self.manifest_path = self.index_dir / "manifest.json"
        self.enable_embeddings = enable_embeddings
        self._text_embedder = text_embedder or _fallback_repo_embedding
        self._include_extensions = tuple(include_extensions) if include_extensions else None
        self._exclude_dirs = set(exclude_dirs) if exclude_dirs else set(_REPO_DEFAULT_EXCLUDE)
        extras: List[Path] = []
        seen: Set[Path] = {self.repo_root}
        if extra_roots:
            for entry in extra_roots:
                try:
                    candidate = Path(entry).expanduser().resolve()
                except Exception:
                    continue
                if candidate in seen:
                    continue
                seen.add(candidate)
                extras.append(candidate)
        self._extra_roots: Tuple[Path, ...] = tuple(extras)
        self._roots: Tuple[Path, ...] = (self.repo_root, *self._extra_roots)
        self._records: List[_RepoIndexRecord] = []
        self._loaded = False
        self._lock = RLock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def rebuild(self) -> Dict[str, Any]:
        """Rebuild the repository index and return a summary."""

        segments: List[Tuple[Path, _RepoSegment]] = []
        files_indexed = 0
        timestamp = time.time()

        for base_root, path in self._iter_repo_files():
            text = self._read_file_text(path)
            if text is None:
                continue
            files_indexed += 1
            for segment in self._segment_file(path, text):
                segments.append((base_root, segment))

        entries = []
        for base_root, segment in segments:
            rel_path = self._relative_path(segment.path, base_root)
            embedding: Vector = []
            if self.enable_embeddings and segment.text.strip():
                embedding = self._embed_text(segment.text)
            record_id = _segment_identifier(rel_path, segment.start_line, segment.end_line)
            metadata = dict(segment.metadata)
            metadata.setdefault("scan_root", str(base_root))
            entry = {
                "id": record_id,
                "path": rel_path,
                "start_line": segment.start_line,
                "end_line": segment.end_line,
                "text": segment.text,
                "embedding": embedding,
                "metadata": metadata,
                "ts": timestamp,
            }
            entries.append(entry)

        self.index_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = self._write_index(entries)
        tmp_path.replace(self.index_path)

        embed_dim = 0
        if entries and entries[0]["embedding"]:
            embed_dim = len(entries[0]["embedding"])

        manifest = {
            "timestamp": timestamp,
            "segments": len(entries),
            "files_indexed": files_indexed,
            "embedding_dim": embed_dim,
        }
        with self.manifest_path.open("w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)

        records = [
            _RepoIndexRecord(
                identifier=entry["id"],
                path=str(entry["path"]),
                start_line=int(entry["start_line"]),
                end_line=int(entry["end_line"]),
                text=str(entry["text"]),
                embedding=_ensure_vector(entry.get("embedding")),
                metadata=dict(entry.get("metadata") or {}),
                timestamp=float(entry.get("ts") or timestamp),
            )
            for entry in entries
        ]

        with self._lock:
            self._records = records
            self._loaded = True

        return {
            "files_indexed": files_indexed,
            "segments": len(entries),
            "timestamp": timestamp,
            "index_path": self.index_path,
        }

    def load(self) -> None:
        """Ensure the in-memory cache reflects the current on-disk index."""

        with self._lock:
            if self._loaded:
                return
            self._load_locked()

    def iter_segments(self) -> Iterator[Dict[str, Any]]:
        """Yield cached segment dictionaries without computing scores."""

        self.load()
        with self._lock:
            for record in self._records:
                yield {
                    "id": record.identifier,
                    "path": record.path,
                    "start_line": record.start_line,
                    "end_line": record.end_line,
                    "text": record.text,
                    "metadata": dict(record.metadata),
                    "timestamp": record.timestamp,
                }

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Return the top ``k`` matching segments for ``query``."""

        query_text = query.strip()
        if not query_text or k <= 0 or not self.enable_embeddings:
            return []

        query_vec = self._embed_text(query_text)
        if not query_vec:
            return []

        self.load()

        with self._lock:
            records = list(self._records)

        scored: List[Tuple[float, _RepoIndexRecord]] = []
        for record in records:
            score = record.score(query_vec)
            if score <= 0:
                continue
            scored.append((score, record))

        scored.sort(key=lambda item: item[0], reverse=True)

        results: List[Dict[str, Any]] = []
        for score, record in scored[:k]:
            results.append(
                {
                    "id": record.identifier,
                    "path": record.path,
                    "start_line": record.start_line,
                    "end_line": record.end_line,
                    "text": record.text,
                    "metadata": dict(record.metadata),
                    "score": score,
                    "timestamp": record.timestamp,
                }
            )
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _embed_text(self, text: str) -> Vector:
        vec = self._text_embedder(text) if text else []
        return [float(value) for value in vec]

    def _iter_repo_files(self) -> Iterator[Tuple[Path, Path]]:
        for base_root in self._roots:
            if not base_root.exists():
                continue
            try:
                base_resolved = base_root.resolve()
            except Exception:
                base_resolved = base_root
            for root, dirs, files in os.walk(base_root):
                path_root = Path(root)
                try:
                    relative_parts = set(path_root.relative_to(base_resolved).parts)
                except ValueError:
                    relative_parts = set()
                if relative_parts & self._exclude_dirs:
                    dirs[:] = []
                    continue
                dirs[:] = [
                    d
                    for d in dirs
                    if d not in self._exclude_dirs and not d.endswith(".egg-info")
                ]
                for name in files:
                    candidate = path_root / name
                    if candidate.is_symlink():
                        continue
                    if self._include_extensions and candidate.suffix not in self._include_extensions:
                        continue
                    yield base_resolved, candidate

    def _read_file_text(self, path: Path) -> Optional[str]:
        try:
            if path.stat().st_size > _MAX_INDEX_FILE_SIZE:
                return None
        except OSError:
            return None
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None
        except OSError:
            return None

    def _segment_file(self, path: Path, text: str) -> List[_RepoSegment]:
        suffix = path.suffix.lower()
        lines = text.splitlines()
        if suffix == ".py":
            segments = self._segment_python(path, lines)
            if segments:
                return segments
        if suffix in {".md", ".rst"}:
            segments = self._segment_markdown(path, lines)
            if segments:
                return segments
        return self._segment_generic(path, lines)

    def _segment_python(self, path: Path, lines: List[str]) -> List[_RepoSegment]:
        source = "\n".join(lines)
        try:
            module = ast.parse(source)
        except SyntaxError:
            return []

        segments: List[_RepoSegment] = []

        if module.body:
            first = module.body[0]
            if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant):
                constant = first.value
                if isinstance(constant.value, str):
                    start = getattr(first, "lineno", 1)
                    end = getattr(first, "end_lineno", start)
                    text_block = self._slice_lines(lines, start, end)
                    segment = self._make_segment(
                        path,
                        start,
                        end,
                        text_block,
                        {"language": "python", "kind": "docstring"},
                    )
                    if segment:
                        segments.append(segment)

        for node in module.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = getattr(node, "lineno", 1)
                end = getattr(node, "end_lineno", start)
                text_block = self._slice_lines(lines, start, end)
                segment = self._make_segment(
                    path,
                    start,
                    end,
                    text_block,
                    {
                        "language": "python",
                        "kind": "function",
                        "name": getattr(node, "name", ""),
                    },
                )
                if segment:
                    segments.append(segment)
            elif isinstance(node, ast.ClassDef):
                start = getattr(node, "lineno", 1)
                end = getattr(node, "end_lineno", start)
                text_block = self._slice_lines(lines, start, end)
                segment = self._make_segment(
                    path,
                    start,
                    end,
                    text_block,
                    {
                        "language": "python",
                        "kind": "class",
                        "name": getattr(node, "name", ""),
                    },
                )
                if segment:
                    segments.append(segment)

        if not segments:
            return []
        return segments

    def _segment_markdown(self, path: Path, lines: List[str]) -> List[_RepoSegment]:
        segments: List[_RepoSegment] = []
        total = len(lines)
        if total == 0:
            return segments
        current_start = 0
        for idx, line in enumerate(lines):
            if line.lstrip().startswith("#") and idx != current_start:
                text_block = self._slice_lines(lines, current_start + 1, idx)
                segment = self._make_segment(
                    path,
                    current_start + 1,
                    idx,
                    text_block,
                    {"language": "markdown", "kind": "section"},
                )
                if segment:
                    segments.append(segment)
                current_start = idx
        text_block = self._slice_lines(lines, current_start + 1, total)
        segment = self._make_segment(
            path,
            current_start + 1,
            total,
            text_block,
            {"language": "markdown", "kind": "section"},
        )
        if segment:
            segments.append(segment)
        return segments

    def _segment_generic(self, path: Path, lines: List[str]) -> List[_RepoSegment]:
        segments: List[_RepoSegment] = []
        window = max(_WINDOW_SIZE, 1)
        overlap = min(_WINDOW_OVERLAP, window - 1) if window > 1 else 0
        total = len(lines)
        if total == 0:
            return segments
        step = window - overlap if window > overlap else window
        start = 0
        while start < total:
            end = min(total, start + window)
            text_block = self._slice_lines(lines, start + 1, end)
            segment = self._make_segment(
                path,
                start + 1,
                end,
                text_block,
                {"language": self._guess_language(path), "kind": "block"},
            )
            if segment:
                segments.append(segment)
            if end == total:
                break
            start += step
        return segments

    def _make_segment(
        self,
        path: Path,
        start_line: int,
        end_line: int,
        text: str,
        metadata: Dict[str, Any],
    ) -> Optional[_RepoSegment]:
        cleaned = text.strip("\n")
        if not cleaned.strip():
            return None
        return _RepoSegment(
            path=path,
            start_line=start_line,
            end_line=end_line,
            text=cleaned,
            metadata=dict(metadata),
        )

    def _slice_lines(self, lines: List[str], start: int, end: int) -> str:
        start_index = max(start - 1, 0)
        end_index = max(start_index, min(end, len(lines)))
        return "\n".join(lines[start_index:end_index])

    def _guess_language(self, path: Path) -> str:
        suffix = path.suffix.lower().lstrip(".")
        if not suffix:
            return "text"
        return suffix

    def _relative_path(self, path: Path, base_root: Optional[Path] = None) -> str:
        try:
            resolved = path.resolve()
        except Exception:
            resolved = path
        roots: List[Path] = []
        if base_root is not None:
            roots.append(base_root)
        roots.append(self.repo_root)
        for root in roots:
            try:
                return resolved.relative_to(root).as_posix()
            except ValueError:
                continue
        return resolved.as_posix()

    def _write_index(self, entries: List[Dict[str, Any]]) -> Path:
        tmp_file = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=self.index_dir)
        try:
            for entry in entries:
                json.dump(entry, tmp_file, ensure_ascii=False)
                tmp_file.write("\n")
        finally:
            tmp_file.close()
        return Path(tmp_file.name)

    def _load_locked(self) -> None:
        records: List[_RepoIndexRecord] = []
        if not self.index_path.exists():
            self._records = []
            self._loaded = True
            return
        with self.index_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                payload = line.strip()
                if not payload:
                    continue
                try:
                    entry = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                record = _RepoIndexRecord(
                    identifier=str(entry.get("id") or ""),
                    path=str(entry.get("path") or ""),
                    start_line=int(entry.get("start_line") or 1),
                    end_line=int(entry.get("end_line") or 1),
                    text=str(entry.get("text") or ""),
                    embedding=_ensure_vector(entry.get("embedding")),
                    metadata=dict(entry.get("metadata") or {}),
                    timestamp=float(entry.get("ts") or 0.0),
                )
                records.append(record)
        self._records = records
        self._loaded = True

def _resolve_ocr_text(path: Path, ocr_map: Optional[Mapping[str, str]]) -> str:
    if not ocr_map:
        return ""
    candidates: Iterable[str] = (
        path.as_posix(),
        str(path),
        path.name,
        path.stem,
    )
    for key in candidates:
        if key in ocr_map:
            return ocr_map[key]
    return ""
