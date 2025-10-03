from pathlib import Path

import pytest

from memory_manager import RepositoryIndex
from repo_reference_helper import RepoReferenceIndex


class DummyRepositoryIndex:
    def __init__(self, segments: list[dict[str, str]]):
        self._segments = segments
        self.loaded = 0
        self.rebuilt = 0

    def load(self) -> None:
        self.loaded += 1

    def iter_segments(self):
        for segment in self._segments:
            yield segment

    def rebuild(self):
        self.rebuilt += 1
        return {"files_indexed": len(self._segments)}


class EmptyRepositoryIndex(DummyRepositoryIndex):
    def __init__(self):
        super().__init__([])

    def iter_segments(self):
        return iter(())


def test_repo_reference_index_collects_files_and_directories(tmp_path: Path):
    repo_root = tmp_path / "repo"
    (repo_root / "src").mkdir(parents=True)
    (repo_root / "src" / "main.py").write_text("print('hi')", encoding="utf-8")
    (repo_root / "README.md").write_text("hello", encoding="utf-8")

    stub = DummyRepositoryIndex([
        {"path": "src/main.py"},
        {"path": "README.md"},
    ])

    index = RepoReferenceIndex(repo_root, repository_index=stub)
    index.refresh()
    entries = index.entries()

    kinds = {(entry.relative_path, entry.kind) for entry in entries}
    assert ("src/main.py", "file") in kinds
    assert ("README.md", "file") in kinds
    assert ("src", "directory") in kinds
    assert stub.loaded >= 1
    assert stub.rebuilt == 0


def test_repo_reference_index_falls_back_to_filesystem(tmp_path: Path):
    repo_root = tmp_path / "repo"
    (repo_root / "docs").mkdir(parents=True)
    (repo_root / "docs" / "index.md").write_text("notes", encoding="utf-8")

    empty_stub = EmptyRepositoryIndex()
    index = RepoReferenceIndex(repo_root, repository_index=empty_stub)
    index.refresh()
    entries = index.entries()

    kinds = {(entry.relative_path, entry.kind) for entry in entries}
    assert ("docs/index.md", "file") in kinds
    assert ("docs", "directory") in kinds
    assert empty_stub.rebuilt >= 1


def test_repo_reference_index_includes_extra_roots_when_allowed(tmp_path: Path):
    repo_root = tmp_path / "workspace"
    extra_root = tmp_path / "external"
    (repo_root / "src").mkdir(parents=True)
    (repo_root / "src" / "main.py").write_text("print('hi')", encoding="utf-8")
    extra_root.mkdir()
    extra_file = extra_root / "notes.txt"
    extra_file.write_text("extra", encoding="utf-8")

    data_root = tmp_path / "datasets"
    index = RepositoryIndex(repo_root=repo_root, data_root=data_root, extra_roots=[extra_root])
    index.rebuild()

    allowed_index = RepoReferenceIndex(
        repo_root,
        repository_index=index,
        extra_roots=[extra_root],
    )
    allowed_index.refresh()
    allowed_paths = {entry.absolute_path for entry in allowed_index.entries()}
    assert extra_file.resolve() in allowed_paths

    restricted_index = RepoReferenceIndex(repo_root, repository_index=index)
    restricted_index.refresh()
    restricted_paths = {entry.absolute_path for entry in restricted_index.entries()}
    assert extra_file.resolve() not in restricted_paths
