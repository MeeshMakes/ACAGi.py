import os
import tempfile
import shutil
import pytest

_TEST_WORKSPACE = tempfile.mkdtemp(prefix="codex_workspace_")
os.environ["CODEX_WORKSPACE"] = _TEST_WORKSPACE


@pytest.fixture(scope="session", autouse=True)
def _cleanup_workspace():
    yield
    shutil.rmtree(_TEST_WORKSPACE, ignore_errors=True)
