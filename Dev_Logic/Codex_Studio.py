# -*- coding: utf-8 -*-
"""
Codex_Lite.py — Local Ollama • Codex Rust (OSS mode) • Buckets • Agent.md • Error Bot • SQL Snapshots
OS: Windows 10/11, macOS, Linux

Highlights
- Ollama-only: lists models via /api/tags and uses them everywhere
- Codex runs with --oss and -m <ollama-model> (no OpenAI)
- Full Auto Mode toggle (--> --full-auto)
- Self-Repo mode: app folder becomes project; Agent.md created with dense directives
- Agent.md Manager (view/edit/rename/delete version files, keep Agent.md immutable)
- Buckets (Assistant/Notes/ErrorBot) in SQLite, versioned; snapshots + diffs; README generator
"""
import os, sys, json, sqlite3, subprocess, shlex, ast, difflib, hashlib, re, socket, logging, urllib.request, urllib.parse, urllib.error, tempfile, zipfile, tarfile, shutil
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from functools import lru_cache
import numpy as np
import time

from tools.task_manager import TaskManager

# ======== Optional GPU ========
try:
    import torch  # type: ignore
except Exception as e:  # pragma: no cover - torch is optional
    logging.warning("Torch import failed: %s", e)
    torch = None

# ======== Qt ========
try:
    from PySide6.QtCore import Qt, QEvent, QRegularExpression, QObject, QProcess, Signal
    from PySide6.QtGui import QFont, QColor, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QFontDatabase
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
        QPushButton, QLineEdit, QComboBox, QPlainTextEdit, QFileDialog, QMessageBox, QDialog,
        QDialogButtonBox, QInputDialog, QTabWidget, QListWidget, QListWidgetItem, QCheckBox, QTextBrowser,
        QDockWidget, QMenu
    )
except Exception as e:
    logging.exception("PySide6 import failed")
    sys.exit(1)

# ======== Optional RAG ========
try:
    from sentence_transformers import SentenceTransformer, util
    EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logging.warning("SentenceTransformer unavailable: %s", e)
    EMBED_MODEL = None

# ======== Logging ========
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ======== Paths ========
APP_ROOT: Path = Path(__file__).resolve().parent
CODEX_DIR: Path = APP_ROOT / "Codex"
LOG_DIR: Path = APP_ROOT / "logs"
DATASETS_ROOT: Path = APP_ROOT / "Project_datasets"
DIFFS_DIR: Path = APP_ROOT / "diffs"
CONFIG_JSON: Path = APP_ROOT / "config.lite.json"
PROJECTS_JSON: Path = APP_ROOT / "projects.lite.json"
APP_LOG: Path = LOG_DIR / "codex_lite.log"
ASSISTANT_TIMING_LOG: Path = LOG_DIR / "assistant_timing.log"
HANDSHAKE_NAME = ".codex_handshake.json"
ANSI_ESCAPE_RE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

# GitHub release info for Codex
CODEX_RELEASE_TAG = "rust-v0.23.0"
CODEX_RELEASE_BASE = f"https://github.com/openai/codex/releases/download/{CODEX_RELEASE_TAG}"
CODEX_REPO_URL = "https://github.com/openai/codex.git"
CODEX_ASSETS = {
    "nt": "codex-x86_64-pc-windows-msvc.exe.zip",
    "posix": {
        "Linux": "codex-x86_64-unknown-linux-gnu.tar.gz",
        "Darwin": "codex-x86_64-apple-darwin.tar.gz",
    },
}

DEFAULT_CONFIG = {
    "oss_base_url": "http://localhost:11434",
    "default_models": {
        "assistant": "gpt-oss:20b",
        "notes": "gpt-oss:20b",
        "errorbot": "gpt-oss:20b",
        "codex": "qwen3:8b",
    },
    "sandbox": "workspace-write",
    "approval": "on-request",
    "full_auto": False,
    "launch_mode": "Embedded"  # External | Embedded
}
DEFAULT_PROJECTS = {"projects": []}

EXCLUDE_DIRS = {
    ".git","node_modules",".venv","venv","env","__pycache__",
    "dist","build",".mypy_cache",".pytest_cache",".idea",".vscode",".DS_Store","Codex","Codex_Agents"
}
EXCLUDE_SUFFIXES = {".exe",".dll",".pyd",".so",".dylib",".bin",".o",".a",".pyc",".pyo",".zip",".tar",".gz",".7z"}

# ======== Utils ========
def ensure_layout():
    for p in [CODEX_DIR, LOG_DIR, DATASETS_ROOT, DIFFS_DIR]:
        p.mkdir(parents=True, exist_ok=True)
    if not CONFIG_JSON.exists():
        CONFIG_JSON.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    if not PROJECTS_JSON.exists():
        PROJECTS_JSON.write_text(json.dumps(DEFAULT_PROJECTS, indent=2), encoding="utf-8")
    if not APP_LOG.exists():
        APP_LOG.write_text("", encoding="utf-8")

def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logging.exception("Load %s failed", path)
        return default

def save_json(path: Path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)

def log_line(msg: str):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with APP_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")
    logging.info(msg)

def which(exe: str) -> str:
    try:
        if os.name == "nt":
            res = subprocess.run(["where", exe], capture_output=True, text=True)
        else:
            res = subprocess.run(["which", exe], capture_output=True, text=True)
        if res.returncode != 0:
            return ""
        for ln in res.stdout.splitlines():
            s = ln.strip()
            if s:
                return s
        return ""
    except Exception as e:
        logging.warning("which(%s) failed: %s", exe, e)
        return ""

def version_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def is_ollama_running(host='127.0.0.1', port=11434) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return True
    except Exception as e:
        logging.warning("Ollama connection failed: %s", e)
        return False

def is_ollama_available(base_url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(base_url)
        host = parsed.hostname or '127.0.0.1'
        port = parsed.port or 11434
        return is_ollama_running(host, port)
    except Exception as e:
        logging.warning("Ollama availability check failed: %s", e)
        return False

# ======== Ollama HTTP ========
def ollama_list(base_url: str) -> Tuple[List[str], Optional[Exception]]:
    """Return models from an Ollama server.

    Parameters
    ----------
    base_url: str
        The server base URL.

    Returns
    -------
    Tuple[List[str], Optional[Exception]]
        A tuple of available model names and a possible exception. Network
        errors like ``URLError`` or ``timeout`` are caught and returned
        so callers can surface user-facing diagnostics. Other exceptions
        are propagated to the caller.
    """
    try:
        req = urllib.request.Request(base_url.rstrip("/") + "/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        return [m["name"] for m in data.get("models", [])], None
    except (urllib.error.URLError, socket.timeout) as e:
        log_line(f"Ollama list failed: {e}")
        return [], e

@lru_cache(maxsize=128)
def _ollama_chat_cached(base_url: str, model: str, messages_tuple: Tuple[Tuple[str, str], ...], system: Optional[str]) -> Tuple[bool, str]:
    messages = [{'role': r, 'content': c} for r, c in messages_tuple]
    if system:
        messages = [{'role': 'system', 'content': system}] + messages
    body = {"model": model, "messages": messages, "stream": False}
    req = urllib.request.Request(base_url.rstrip("/") + "/api/chat",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        return True, data.get("message", {}).get("content", "").strip()
    except Exception as e:
        logging.exception("Ollama chat failed")
        return False, f"[OLLAMA ERROR] {e}"

def ollama_chat(base_url: str, model: str, messages: list, system: Optional[str] = None) -> Tuple[bool, str]:
    messages_tuple = tuple((m.get('role'), m.get('content')) for m in messages)
    return _ollama_chat_cached(base_url, model, messages_tuple, system)

def ollama_cache_clear() -> None:
    _ollama_chat_cached.cache_clear()

# ======== SQLite ========
def dataset_paths(project: Path) -> List[Path]:
    local_dir = project / "datasets"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_db = local_dir / "cortex_lite.db"
    global_db = DATASETS_ROOT / f"{project.name}.db"
    return [local_db, global_db]

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS buckets(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         project TEXT, operator TEXT, tab_name TEXT, content TEXT, version TEXT, ts TEXT
       )""",
    """CREATE TABLE IF NOT EXISTS repo_files(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         project TEXT, path TEXT, content TEXT, version TEXT, ts TEXT
       )""",
    """CREATE TABLE IF NOT EXISTS diffs(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         project TEXT, source TEXT, content TEXT, version TEXT, ts TEXT
       )"""
]

def dataset_init(project: Path):
    for db in dataset_paths(project):
        conn = sqlite3.connect(str(db))
        try:
            cur = conn.cursor()
            for sql in SCHEMA: cur.execute(sql)
            conn.commit()
        finally:
            conn.close()

def dataset_insert(table: str, project: Path, cols: List[str], vals: Tuple):
    for db in dataset_paths(project):
        conn = sqlite3.connect(str(db))
        try:
            cur = conn.cursor()
            cur.execute(f"INSERT INTO {table}({', '.join(cols)}) VALUES({', '.join(['?']*len(cols))})", vals)
            conn.commit()
        finally:
            conn.close()

def dataset_store_bucket(project: Path, operator: str, tab: str, content: str, ver: str):
    ts = datetime.now().isoformat(timespec="seconds")
    dataset_insert("buckets", project, ["project","operator","tab_name","content","version","ts"],
                   (project.name, operator, tab, content, ver, ts))

def dataset_delete_bucket(project: Path, operator: str, tab: str):
    for db in dataset_paths(project):
        conn = sqlite3.connect(str(db))
        try:
            conn.execute("DELETE FROM buckets WHERE project=? AND operator=? AND tab_name=?",
                         (project.name, operator, tab))
            conn.commit()
        finally:
            conn.close()

def dataset_store_repo_files(project: Path, files: List[Tuple[str,str]], ver: str):
    ts = datetime.now().isoformat(timespec="seconds")
    for db in dataset_paths(project):
        conn = sqlite3.connect(str(db))
        try:
            conn.executemany(
                "INSERT INTO repo_files(project,path,content,version,ts) VALUES(?,?,?,?,?)",
                [(project.name, p, c, ver, ts) for p, c in files]
            )
            conn.commit()
        finally:
            conn.close()

def dataset_store_diff(project: Path, source: str, content: str, ver: str):
    ts = datetime.now().isoformat(timespec="seconds")
    dataset_insert("diffs", project, ["project","source","content","version","ts"],
                   (project.name, source, content, ver, ts))

def dataset_fetch_diffs_desc(project: Path) -> List[Tuple[str,str,str]]:
    db = dataset_paths(project)[0]
    conn = sqlite3.connect(str(db)); conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT ts, source, content FROM diffs WHERE project=? ORDER BY id DESC", (project.name,))
        return [(r["ts"], r["source"], r["content"]) for r in cur.fetchall()]
    finally:
        conn.close()

def clone_codex_repo(codex_dir: Path) -> Optional[Path]:
    repo_dir = codex_dir / "codex-src"
    try:
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
        subprocess.run([
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            CODEX_RELEASE_TAG,
            CODEX_REPO_URL,
            str(repo_dir),
        ], check=True)
        return repo_dir
    except Exception as e:
        logging.exception("Clone failed")
        log_line(f"Clone failed: {e}")
        return None

# ======== Snapshots & Diffs ========
def text_sha1(s: str) -> str: return hashlib.sha1(s.encode("utf-8","ignore")).hexdigest()

def sanitize_skip(path: Path) -> bool:
    low = path.name.lower()
    if low.startswith("readme") and path.suffix.lower()==".md": return True
    if "Codex_Agents" in [p.lower() for p in path.parts]: return True
    return False

def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in EXCLUDE_SUFFIXES: return False
    try:
        with path.open("rb") as f: chunk = f.read(4096)
        if b"\x00" in chunk: return False
        return True
    except Exception as e:
        logging.warning("Could not read %s: %s", path, e)
        return False

def iter_files(root: Path):
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            p = Path(cur) / fn
            if sanitize_skip(p): continue
            if not is_text_file(p): continue
            yield p

class Snapshot:
    def __init__(self, stamp: str, files: Dict[str, Tuple[str,str]]):
        self.stamp = stamp
        self.files = files  # rel -> (sha, text)

def make_snapshot(root: Path, limit_bytes=2_000_000) -> Snapshot:
    files: Dict[str, Tuple[str,str]] = {}
    for p in iter_files(root):
        try:
            if p.stat().st_size > limit_bytes: continue
        except Exception as e:
            logging.warning("Could not stat %s: %s", p, e)
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logging.warning("Could not read %s: %s", p, e)
            txt = f"[[unreadable: {e}]]"
        rel = str(p.relative_to(root)).replace("\\","/")
        files[rel] = (text_sha1(txt), txt)
    return Snapshot(version_stamp(), files)

def unified(a_text: str, b_text: str, a_label: str, b_label: str) -> str:
    return "\n".join(difflib.unified_diff(a_text.splitlines(), b_text.splitlines(),
                                          fromfile=a_label, tofile=b_label, lineterm=""))

def diff_snapshots(a: Snapshot, b: Snapshot) -> List[Tuple[str,str]]:
    a_paths, b_paths = set(a.files), set(b.files)
    out: List[Tuple[str,str]] = []
    for rel in sorted(b_paths - a_paths):
        out.append(("added", unified("", b.files[rel][1], f"a/{rel}", f"b/{rel}")))
    for rel in sorted(a_paths - b_paths):
        out.append(("removed", unified(a.files[rel][1], "", f"a/{rel}", f"b/{rel}")))
    for rel in sorted(a_paths & b_paths):
        (sa, ta) = a.files[rel]; (sb, tb) = b.files[rel]
        if sa != sb:
            out.append(("changed", unified(ta, tb, f"a/{rel}", f"b/{rel}")))
    return out

# ======== README (light) ========
def analyse_overview(root: Path) -> str:
    py_sections, other = [], []
    for p in iter_files(root):
        rel = str(p.relative_to(root)).replace("\\","/")
        if p.suffix.lower()==".py":
            doc, classes, funcs = "", [], []
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
                doc = (ast.get_docstring(tree) or "").strip()
                for n in tree.body:
                    if isinstance(n, ast.ClassDef): classes.append(n.name)
                    if isinstance(n, ast.FunctionDef): funcs.append(n.name)
            except Exception as e:
                logging.warning("Could not parse %s: %s", p, e)
            sec = [f"### `{rel}`"]
            if doc: sec.append(doc)
            if classes: sec.append("**Classes:** " + ", ".join(classes))
            if funcs: sec.append("**Functions:** " + ", ".join(funcs))
            py_sections.append("\n\n".join(sec))
        else:
            other.append(rel)
    out = ["# Project Documentation", "", "Auto-generated after update.", ""]
    if py_sections: out += ["## Python Modules",""] + py_sections + [""]
    if other:
        out += ["## Other Files", ""] + [f"- `{x}`" for x in sorted(other)] + [""]
    return "\n".join(out)

def generate_readme(project: Path, log=lambda s: None, ver: Optional[str]=None):
    try:
        md = analyse_overview(project); ts = ver or version_stamp()
        readme = project / "README.md"; hist = project / ".readmes"; hist.mkdir(exist_ok=True)
        prev = readme.read_text(encoding="utf-8", errors="ignore") if readme.exists() else ""
        readme.write_text(md, encoding="utf-8")
        (hist / f"README_{ts}.md").write_text(md, encoding="utf-8")
        log(f"[SYSTEM] README generated at {readme} (snapshot README_{ts}.md)")
        if prev:
            patch = unified(prev, md, "README.md(prev)","README.md(curr)")
            if patch.strip(): dataset_store_diff(project, "readme", patch, ts)
    except Exception as e:
        logging.exception("README generation failed")
        log(f"[SYSTEM] README generation failed: {e}")

# ======== UI Helpers ========
class DiffHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        def fmt(c): f=QTextCharFormat(); f.setForeground(QColor(c)); return f
        self.rules = [
            (QRegularExpression(r"^(\+.*)$"), fmt("#00a859")),
            (QRegularExpression(r"^(\-.*)$"), fmt("#d14")),
            (QRegularExpression(r"^@@.*@@"), fmt("#b58900")),
            (QRegularExpression(r"^(diff --git|index |--- |\+\+\+ )"), fmt("#7b5cff")),
        ]
    def highlightBlock(self, text: str):
        for rx, sty in self.rules:
            it = rx.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), sty)

class DiffPane(QWidget):
    def __init__(self):
        super().__init__()
        self.blocks: List[Tuple[str,str,str]] = []
        self.idx = -1
        v = QVBoxLayout(self)
        head = QHBoxLayout()
        self.lbl = QLabel("Diffs: 0")
        self.prev = QPushButton("◀ Prev"); self.nextb = QPushButton("Next ▶")
        head.addWidget(self.lbl); head.addStretch(1); head.addWidget(self.prev); head.addWidget(self.nextb)
        v.addLayout(head)
        self.view = QPlainTextEdit(); self.view.setReadOnly(True); self.view.setLineWrapMode(QPlainTextEdit.NoWrap)
        v.addWidget(self.view, 1)
        self.hl = DiffHighlighter(self.view.document())
        mono = QFont("Consolas" if os.name=="nt" else "Monospace"); mono.setStyleHint(QFont.TypeWriter)
        self.view.setFont(mono)
        self.prev.clicked.connect(self._prev); self.nextb.clicked.connect(self._next)
    def set_blocks(self, blocks: List[Tuple[str,str,str]]):
        self.blocks = blocks; self.idx = 0 if blocks else -1; self._render()
    def _render(self):
        n=len(self.blocks); self.lbl.setText(f"Diffs: {n} (page {self.idx+1 if self.idx>=0 else 0}/{n})")
        self.view.setPlainText("" if self.idx<0 else f"--- [{self.blocks[self.idx][0]}] source={self.blocks[self.idx][1]} ---\n{self.blocks[self.idx][2]}")
    def _prev(self):
        if self.idx>0: self.idx-=1; self._render()
    def _next(self):
        if self.blocks and self.idx<len(self.blocks)-1: self.idx+=1; self._render()

# ======== Chat Pane ========
class ChatPane(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        # Load emoji font
        fd = QFontDatabase()
        emoji = None
        for path in (
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/truetype/emoji/NotoColorEmoji.ttf",
        ):
            fid = fd.addApplicationFont(path)
            if fid != -1:
                fam = fd.applicationFontFamilies(fid)
                if fam:
                    emoji = QFont(fam[0])
                    break
        if emoji:
            self.setFont(emoji)
        css = (
            """
            QTextBrowser { border:1px solid #c7c7c7; background:#0f1113; color:#ededed; padding:4px; }
            .user { background:#4b6ef5; color:#fff; padding:6px; border-radius:6px; margin:4px 40px 4px 4px; }
            .assistant { background:#444; color:#fff; padding:6px; border-radius:6px; margin:4px 4px 4px 40px; }
            .codex { background:#2f2f2f; color:#98c379; padding:6px; border-radius:6px; margin:4px 40px 4px 4px; }
            .system { background:#222; color:#f1c40f; padding:6px; border-radius:6px; margin:4px 40px; }
            """
        )
        self.setStyleSheet(css)
        self.document().setDefaultStyleSheet(css)

    def append_message(self, role: str, text: str):
        esc = html.escape(text).replace("\n", "<br>")
        self.append(f"<div class='{role}'>{esc}</div>")
        self.moveCursor(QTextCursor.End)

# ======== Agent Manager Dialog ========
class AgentManager(QDialog):
    def __init__(self, root: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agent.md Manager")
        self.root = root
        v = QVBoxLayout(self)
        self.list = QListWidget(); v.addWidget(self.list, 2)
        self.edit = QPlainTextEdit(); self.edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        v.addWidget(self.edit, 5)
        row = QHBoxLayout()
        self.btn_open = QPushButton("Open"); self.btn_save = QPushButton("Save")
        self.btn_new = QPushButton("New version file…")
        self.btn_rename = QPushButton("Rename")
        self.btn_delete = QPushButton("Delete")
        row.addWidget(self.btn_open); row.addWidget(self.btn_save); row.addWidget(self.btn_new)
        row.addWidget(self.btn_rename); row.addWidget(self.btn_delete)
        v.addLayout(row)
        self._refresh()
        self.btn_open.clicked.connect(self._open)
        self.btn_save.clicked.connect(self._save)
        self.btn_new.clicked.connect(self._new)
        self.btn_rename.clicked.connect(self._rename)
        self.btn_delete.clicked.connect(self._delete)
    def _agent_dir(self) -> Path:
        d = self.root / "Codex_Agents"; d.mkdir(exist_ok=True); return d
    def _refresh(self):
        self.list.clear()
        d = self._agent_dir()
        files = sorted([p.name for p in d.glob("*.md")])
        for name in files:
            self.list.addItem(name)
    def _sel_path(self) -> Optional[Path]:
        it = self.list.currentItem()
        if not it: return None
        return self._agent_dir() / it.text()
    def _open(self):
        p = self._sel_path()
        if not p: return
        try:
            self.edit.setPlainText(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception as e:
            logging.exception("Open agent file failed")
            QMessageBox.warning(self, "Open", str(e))
    def _save(self):
        p = self._sel_path()
        if not p: return
        if p.name == "Agent.md":
            QMessageBox.warning(self, "Agent.md", "Agent.md is immutable; edits are blocked.")
            return
        try:
            p.write_text(self.edit.toPlainText(), encoding="utf-8")
            QMessageBox.information(self, "Saved", f"Saved {p.name}")
        except Exception as e:
            logging.exception("Save agent file failed")
            QMessageBox.warning(self, "Save", str(e))
    def _new(self):
        name, ok = QInputDialog.getText(self, "New Agent Version", "Name (e.g., v1):")
        if not ok or not name.strip(): return
        p = self._agent_dir() / f"Agent_{name.strip()}.md"
        if p.exists(): QMessageBox.information(self, "Exists", "File exists."); return
        p.write_text("# Agent Version\n\n(Add directives…)\n", encoding="utf-8")
        self._refresh()
    def _rename(self):
        p = self._sel_path()
        if not p: return
        if p.name=="Agent.md":
            QMessageBox.information(self, "Agent.md", "Agent.md is immutable (cannot be renamed).")
            return
        name, ok = QInputDialog.getText(self, "Rename", "New name (without .md):", text=p.stem)
        if not ok or not name.strip(): return
        dest = p.with_name(f"{name.strip()}.md")
        if dest.exists(): QMessageBox.information(self, "Exists", "Target exists."); return
        p.rename(dest); self._refresh()
    def _delete(self):
        p = self._sel_path()
        if not p: return
        if p.name=="Agent.md":
            QMessageBox.information(self, "Agent.md", "Agent.md is immutable (cannot be deleted).")
            return
        if QMessageBox.question(self, "Delete", f"Delete {p.name}?") == QMessageBox.Yes:
            p.unlink(missing_ok=True); self._refresh()
class SecurityDialog(QDialog):
    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Settings")
        self.cfg = cfg
        v = QVBoxLayout(self)
        row1 = QHBoxLayout()
        self.cb_sandbox = QComboBox()
        self.cb_sandbox.addItems(["workspace-write", "read-only", "none"])
        self.cb_sandbox.setCurrentText(cfg.get("sandbox", "workspace-write"))
        row1.addWidget(QLabel("Sandbox:"))
        row1.addWidget(self.cb_sandbox, 1)
        v.addLayout(row1)
        row2 = QHBoxLayout()
        self.cb_approval = QComboBox()
        self.cb_approval.addItems(["on-request", "on-failure", "never"])
        self.cb_approval.setCurrentText(cfg.get("approval", "on-request"))
        row2.addWidget(QLabel("Approval:"))
        row2.addWidget(self.cb_approval, 1)
        v.addLayout(row2)
        self.chk_full_auto = QCheckBox("Full Auto Mode")
        self.chk_full_auto.setChecked(bool(cfg.get("full_auto", False)))
        v.addWidget(self.chk_full_auto)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        v.addWidget(btns)

    def values(self):
        return {
            "sandbox": self.cb_sandbox.currentText(),
            "approval": self.cb_approval.currentText(),
            "full_auto": self.chk_full_auto.isChecked(),
        }

# ======== Main Widget ========
class CodexLite(QWidget):
    def __init__(self, status_cb):
        super().__init__()
        ensure_layout()
        self.cfg = load_json(CONFIG_JSON, DEFAULT_CONFIG)
        self.projects = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        self.status_cb = status_cb

        self._pre_snapshot = None
        self._pre_project: Optional[Path] = None

        self.codex_proc = QProcess(self)
        self.codex_proc.readyReadStandardOutput.connect(self._codex_out)
        self.codex_proc.readyReadStandardError.connect(self._codex_err)
        self.codex_proc.finished.connect(lambda *_: self._status("Embedded Codex exited."))
        self._strip_ansi = False
        self._last_assistant_msg = ""

        self.task_manager = TaskManager(LOG_DIR / "tasks.json")

        self._build_ui()
        self._apply_theme()
        self._reload_projects()
        self._populate_models(initial=True)
        self._status("Ready")

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        split = QSplitter(Qt.Horizontal); root.addWidget(split, 1)

        # LEFT: Assistant side
        left = QWidget(); lv = QVBoxLayout(left)
        gA = QGroupBox("Assistant"); av = QVBoxLayout(gA)

        row_models = QHBoxLayout()
        self.cb_assistant = QComboBox()
        self.cb_notes = QComboBox()
        self.cb_error = QComboBox()
        row_models.addWidget(QLabel("Assistant:")); row_models.addWidget(self.cb_assistant, 1)
        row_models.addWidget(QLabel("Notes:")); row_models.addWidget(self.cb_notes, 1)
        row_models.addWidget(QLabel("Error Bot:")); row_models.addWidget(self.cb_error, 1)
        av.addLayout(row_models)

        self.chat = ChatPane(); av.addWidget(self.chat, 1)

        compose = QHBoxLayout()
        self.ass_in = QPlainTextEdit(); self.ass_in.setFixedHeight(90)
        self.ass_in.setPlaceholderText("Ask your assistant… (Enter to send; Shift+Enter = newline)")
        self.btn_send = QPushButton("Send"); self.btn_send.clicked.connect(self._assistant_send)
        self.btn_to_note = QPushButton("Summarize → Notes"); self.btn_to_note.clicked.connect(self._assistant_to_note)
        compose.addWidget(self.ass_in, 1); compose.addWidget(self.btn_send); compose.addWidget(self.btn_to_note)
        av.addLayout(compose)
        self.input_line = QLineEdit(); self.input_line.setPlaceholderText("Type to send to Embedded Codex…")
        self.input_line.returnPressed.connect(self._send_to_embedded)
        av.addWidget(self.input_line)
        lv.addWidget(gA, 1)

        # RIGHT: Project / Codex / Buckets / Diff
        right = QWidget(); rv = QVBoxLayout(right)

        # Project row
        gP = QGroupBox("Project"); pv = QVBoxLayout(gP)
        prow1 = QHBoxLayout()
        self.cb_project = QComboBox()
        self.btn_add = QPushButton("Add…")
        self.btn_open = QPushButton("Open Folder")
        self.btn_forget = QPushButton("Forget")
        self.btn_selfrepo = QPushButton("Self-Repo Mode")
        prow1.addWidget(QLabel("Current:")); prow1.addWidget(self.cb_project, 1)
        for b, fn in [(self.btn_add, self._add_project), (self.btn_open, self._open_project),
                      (self.btn_forget, self._forget_project), (self.btn_selfrepo, self._self_repo)]:
            b.clicked.connect(fn); prow1.addWidget(b)
        pv.addLayout(prow1)

        prow2 = QHBoxLayout()
        self.cb_codex_model = QComboBox()
        self.btn_refresh_models = QPushButton("Refresh Ollama Models"); self.btn_refresh_models.clicked.connect(self._populate_models)
        self.chk_full_auto = QCheckBox("Full Auto Mode")
        self.chk_full_auto.setChecked(bool(self.cfg.get("full_auto", False)))
        self.btn_security = QPushButton("Security Settings…")
        self.btn_security.clicked.connect(self._security_settings)
        self.btn_setup_codex = QPushButton("Setup Codex"); self.btn_setup_codex.clicked.connect(self._setup_codex)
        self.btn_setup_codex.setToolTip("Download binary and clone source from GitHub")
        self.btn_upload_src = QPushButton("Upload Codex Source"); self.btn_upload_src.clicked.connect(self._upload_codex_source)
        self.btn_upload_src.setToolTip("Push Codex source to your GitHub repo")
        self.btn_launch_ext = QPushButton("Launch External"); self.btn_launch_ext.clicked.connect(lambda: self._launch_codex(mode="External"))
        self.btn_launch_ext.setToolTip("Open Codex in a separate terminal window")
        self.btn_launch_emb = QPushButton("Launch Embedded"); self.btn_launch_emb.clicked.connect(lambda: self._launch_codex(mode="Embedded"))
        self.btn_launch_emb.setToolTip("Run Codex inside this GUI")
        prow2.addWidget(QLabel("Codex model:")); prow2.addWidget(self.cb_codex_model, 1)
        prow2.addWidget(self.btn_refresh_models)
        prow2.addStretch(1)
        prow2.addWidget(self.chk_full_auto)
        prow2.addWidget(self.btn_security)
        prow2.addWidget(self.btn_setup_codex)
        prow2.addWidget(self.btn_upload_src)
        prow2.addWidget(self.btn_launch_ext)
        prow2.addWidget(self.btn_launch_emb)
        pv.addLayout(prow2)
        rv.addWidget(gP)

        # Agents / README row
        gR = QGroupBox("Agents / README"); grv = QHBoxLayout(gR)
        self.btn_core_agent = QPushButton("Create Core Agent.md"); self.btn_core_agent.clicked.connect(self._create_core_agent)
        self.btn_agent_new = QPushButton("New Agent file…"); self.btn_agent_new.clicked.connect(self._new_agent_file)
        self.btn_export_note = QPushButton("Export Note → Agent_v*.md"); self.btn_export_note.clicked.connect(self._export_selected_note)
        self.btn_agent_mgr = QPushButton("Agent.md Manager"); self.btn_agent_mgr.clicked.connect(self._open_agent_manager)
        self.btn_readme = QPushButton("Generate README"); self.btn_readme.clicked.connect(self._gen_readme)
        for b in [self.btn_core_agent, self.btn_agent_new, self.btn_export_note, self.btn_agent_mgr, self.btn_readme]:
            grv.addWidget(b)
        rv.addWidget(gR)

        # Buckets row
        gB = QGroupBox("Buckets"); gbv = QHBoxLayout(gB)
        # Notes
        notes = QGroupBox("Notes (Buckets)"); nv = QVBoxLayout(notes)
        self.tabs_notes = QTabWidget(); self.tabs_notes.setTabsClosable(True)
        self.tabs_notes.tabCloseRequested.connect(lambda i: self._close_bucket(self.tabs_notes,"notes",i))
        nv.addWidget(self.tabs_notes, 1)
        rown = QHBoxLayout()
        self.btn_note_new = QPushButton("New Note"); self.btn_note_new.clicked.connect(lambda: self._note_create("# Note\n"))
        self.btn_note_save = QPushButton("Save Note"); self.btn_note_save.clicked.connect(self._note_save)
        rown.addWidget(self.btn_note_new); rown.addWidget(self.btn_note_save)
        nv.addLayout(rown)
        # Tasks
        tasks = QGroupBox("Tasks"); tv = QVBoxLayout(tasks)
        self.list_tasks = QListWidget(); tv.addWidget(self.list_tasks, 1)
        self.list_tasks.currentItemChanged.connect(self._task_selection_changed)
        rowt = QHBoxLayout()
        self.btn_task_pause = QPushButton("Pause"); self.btn_task_pause.clicked.connect(self._task_pause)
        self.btn_task_done = QPushButton("Complete"); self.btn_task_done.clicked.connect(self._task_done)
        self.btn_task_remove = QPushButton("Delete"); self.btn_task_remove.clicked.connect(self._task_remove)
        for b in [self.btn_task_pause, self.btn_task_done, self.btn_task_remove]:
            rowt.addWidget(b)
        tv.addLayout(rowt)
        # Error Bot
        eb = QGroupBox("Error Bot"); ev = QVBoxLayout(eb)
        self.tabs_error = QTabWidget(); self.tabs_error.setTabsClosable(True)
        self.tabs_error.tabCloseRequested.connect(lambda i: self._close_bucket(self.tabs_error,"errorbot",i))
        ev.addWidget(self.tabs_error, 1)
        rowe = QHBoxLayout()
        self.btn_scan = QPushButton("Run Error Bot (Analyze diffs + buckets)"); self.btn_scan.clicked.connect(self._run_error_bot)
        self.btn_clear_diffs = QPushButton("Clear Diff View"); self.btn_clear_diffs.clicked.connect(lambda: self.diffpane.set_blocks([]))
        self.btn_save_patch = QPushButton("Export Patch"); self.btn_save_patch.clicked.connect(self._save_patch)
        rowe.addWidget(self.btn_scan); rowe.addWidget(self.btn_clear_diffs); rowe.addWidget(self.btn_save_patch)
        ev.addLayout(rowe)
        gbv.addWidget(notes,1); gbv.addWidget(tasks,1); gbv.addWidget(eb,1)
        rv.addWidget(gB, 2)

        # Diff viewer
        self.diffpane = DiffPane()
        rv.addWidget(self.diffpane, 2)

        split.addWidget(left); split.addWidget(right)
        split.setStretchFactor(0, 3); split.setStretchFactor(1, 5)

        # Enter to send in assistant input
        self.ass_in.installEventFilter(self._enter_filter(self._assistant_send))
        self.task_manager.tasks_changed.connect(self._tasks_refresh)
        self._tasks_refresh()

    def _apply_theme(self):
        self.setStyleSheet("""
        QWidget { background:#d3d4d1; }
        QGroupBox { background:#e6e6e6; border:1px solid #c6c6c6; border-radius:6px; margin-top:8px; font-weight:bold; color:#222; }
        QGroupBox::title { left:10px; padding:0 4px; }
        QPlainTextEdit, QTextBrowser { border:1px solid #c7c7c7; background:#0f1113; color:#ededed; }
        QPushButton { border:none; border-radius:6px; padding:8px 12px; color:#fff; background:#7b5cff; }
        QPushButton:hover { background:#6a4be0; }
        """)
        mono = QFont("Consolas" if os.name=="nt" else "Monospace"); mono.setStyleHint(QFont.TypeWriter)
        for w in [self.diffpane.view, self.ass_in]:
            w.setFont(mono)

    def _status(self, s: str):
        self.status_cb(s); log_line(s)
        self.chat.append_message('system', s)

    def _enter_filter(self, fn):
        class F(QObject):
            def eventFilter(s, o, e):
                if e.type() == QEvent.KeyPress and e.key() in (Qt.Key_Return, Qt.Key_Enter) and not (e.modifiers() & Qt.ShiftModifier):
                    fn(); return True
                return False
        return F(self)

    # ---------- Models ----------
    def _populate_models(self, initial=False):
        base = self.cfg.get("oss_base_url","http://localhost:11434")
        if not is_ollama_available(base):
            for cb in [self.cb_assistant, self.cb_notes, self.cb_error, self.cb_codex_model]:
                cb.clear(); cb.addItem("Ollama offline")
            self._status(f"Ollama server unavailable at {base}")
            return
        models, err = ollama_list(base)
        if err:
            for cb in [self.cb_assistant, self.cb_notes, self.cb_error, self.cb_codex_model]:
                cb.clear(); cb.addItem("Ollama error")
            self._status(f"Failed to list Ollama models: {err}")
            return
        if not models:
            for cb in [self.cb_assistant, self.cb_notes, self.cb_error, self.cb_codex_model]:
                cb.clear(); cb.addItem("No Ollama models")
            self._status("Ollama reachable but no models found. Pull models with 'ollama pull <model>'.")
            return
        for cb in [self.cb_assistant, self.cb_notes, self.cb_error, self.cb_codex_model]:
            sel = cb.currentText()
            cb.clear(); cb.addItems(models)
        # set defaults
        defaults = self.cfg.get("default_models", {})
        def set_default(cb, key):
            want = defaults.get(key)
            i = cb.findText(want) if want else -1
            if i >= 0:
                cb.setCurrentIndex(i)
            else:
                cb.setCurrentIndex(0)
                if key == "codex" and want == "qwen3:8b":
                    self._status("Default 'qwen3:8b' not found; using first available model.")
        if initial:
            set_default(self.cb_assistant, "assistant")
            set_default(self.cb_notes, "notes")
            set_default(self.cb_error, "errorbot")
            set_default(self.cb_codex_model, "codex")
        self._status("Ollama models refreshed.")

    # ---------- Projects ----------
    def _reload_projects(self):
        self.cb_project.clear()
        self.projects = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        self.cb_project.addItem("<none>")
        for p in self.projects.get("projects", []):
            self.cb_project.addItem(p["name"])
        if self.cfg.get("default_project"):
            i = self.cb_project.findText(self.cfg["default_project"])
            if i>=0: self.cb_project.setCurrentIndex(i)

    def _get_project_entry(self, name: str):
        return next((x for x in self.projects.get("projects", []) if x.get("name")==name), None)

    def _current_project(self) -> Optional[Path]:
        name = self.cb_project.currentText()
        if not name or name=="<none>": return None
        ent = self._get_project_entry(name); 
        if not ent: return None
        p = Path(ent.get("path",""))
        if not p.exists(): self._status("Project path missing."); return None
        ent["last_used"] = datetime.now().isoformat(); save_json(PROJECTS_JSON, self.projects)
        dataset_init(p)
        return p

    def _add_project(self):
        d = QFileDialog.getExistingDirectory(self, "Select Project Folder", str(Path.home()))
        if not d: return
        p = Path(d)
        data = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        if not any(x.get("path")==str(p) for x in data.get("projects", [])):
            data["projects"].append({"name": p.name, "path": str(p), "type":"local", "last_used": datetime.now().isoformat()})
            save_json(PROJECTS_JSON, data)
        self._reload_projects()
        self.cb_project.setCurrentText(p.name)
        self.cfg["default_project"] = p.name; save_json(CONFIG_JSON, self.cfg)
        dataset_init(p)
        self._status("Project added and initialized (SQL).")

    def _open_project(self):
        p = self._current_project()
        if not p: return
        try:
            if os.name=="nt": os.startfile(str(p))  # type: ignore
            elif sys.platform=="darwin": subprocess.Popen(["open", str(p)])
            else: subprocess.Popen(["xdg-open", str(p)])
        except Exception as e:
            logging.exception("Open project failed")
            self._status(f"Open project failed: {e}")

    def _forget_project(self):
        sel = self.cb_project.currentText()
        if not sel or sel=="<none>": return
        data = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        data["projects"] = [x for x in data.get("projects", []) if x.get("name")!=sel]
        save_json(PROJECTS_JSON, data)
        if self.cfg.get("default_project")==sel:
            self.cfg["default_project"] = ""; save_json(CONFIG_JSON, self.cfg)
        self._reload_projects()
        self._status("Project forgotten.")

    def _self_repo(self):
        # Make the app folder itself the project and ensure SQL + Agent.md exist
        data = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        if not any(x.get("path")==str(APP_ROOT) for x in data.get("projects", [])):
            data["projects"].append({"name": APP_ROOT.name, "path": str(APP_ROOT), "type":"local", "last_used": datetime.now().isoformat()})
            save_json(PROJECTS_JSON, data)
        self._reload_projects()
        self.cb_project.setCurrentText(APP_ROOT.name)
        self.cfg["default_project"] = APP_ROOT.name; save_json(CONFIG_JSON, self.cfg)
        dataset_init(APP_ROOT)
        self._status("Self-Repo mode: current project = app root.")
        self._create_core_agent(force=True)

    # ---------- Agent.md ----------
    def _agent_dir(self, project: Path) -> Path:
        d = project / "Codex_Agents"; d.mkdir(exist_ok=True); return d

    def _default_agent_body(self) -> str:
        return (
            "# Agent.md — Operating Charter for Codex (Local-Ollama, Self-Evolving)\n\n"
            "You are **Codex** running entirely with **local Ollama models** via the `--oss` provider.\n"
            "This repository is your **workspace and subject**. Your primary objective is to **self-improve Codex_Lite** and its ecosystem while strictly honoring the user's intent.\n\n"
            "## Ground Rules\n"
            "1. **Provider**: Use local models (Ollama). Never request OpenAI or remote APIs. Assume an Ollama server at `http://localhost:11434`.\n"
            "2. **Models**: Default to `gpt-oss:20b` (or user-selected). Be concise but precise; prefer small diffs and incremental PR-style changes.\n"
            "3. **Workspace**: Treat this folder as the project root. Use `-C <root>` when you run the Codex CLI.\n"
            "4. **Artifacts**: Maintain buckets in SQLite, snapshots, diffs, and `README.md`. Avoid editing generated snapshots directly.\n"
            "5. **Agent Files**: `Codex_Agents/Agent.md` is the **immutable global policy**. Also consult any `Codex_Agents/Agent_Versions/Agent_*.md` files as **versioned directives**. If none exist, propose improvements.\n"
            "6. **Notes**: User can convert Notes buckets into `Agent_Versions/Agent_*.md`. Treat them as **high-priority directives** when present.\n"
            "7. **Safety**: Unless Full Auto Mode is enabled, ask for approval before risky actions. Respect sandbox configuration.\n\n"
            "## Operating Procedure\n"
            "- On start: read `Agent.md` + latest `Agent_Versions/Agent_*.md` files, SQLite buckets, and most recent diffs.\n"
            "- Detect logical gaps, missing features, UX rough edges, and reliability problems.\n"
            "- Propose changes as *minimal diffs*, with file paths, reasoning, and test/validation steps.\n"
            "- When the user approves (or Full Auto Mode), apply patches safely and update documentation.\n\n"
            "## Priorities\n"
            "1. Robust **Ollama-only** integration and model selection across Assistant/Notes/ErrorBot/Codex.\n"
            "2. Reliability: clean error handling, cross-platform terminal behavior, snapshot consistency, and DB integrity.\n"
            "3. Humanistic UX: clear status lines, safe defaults, reversible actions, and readable diffs.\n"
            "4. Autonomy: self-diagnose failures, suggest fixes, and refine prompts/agents to improve over time.\n\n"
            "## Datasets\n"
            "- You may index project text into embeddings if enabled. Use them only for retrieval—not as ground truth.\n\n"
            "## Deliverables\n"
            "- Small, reviewable diffs; updated READMEs; new/updated `Agent_Versions/Agent_*.md` when turning Notes into persistent directives; Error Bot reports after each update.\n"
        )

    def _create_core_agent(self, force=False):
        p = self._current_project()
        if not p: QMessageBox.information(self, "Select project", "Choose a project."); return
        d = self._agent_dir(p)
        core = d / "Agent.md"
        if core.exists() and not force:
            self._status(f"Core Agent.md already exists at {core}")
            return
        core.write_text(self._default_agent_body(), encoding="utf-8")
        self._status(f"Core Agent.md created at {core}")

    def _new_agent_file(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        name, ok = QInputDialog.getText(self, "New Agent File", "Agent name (e.g. v1):")
        if not ok or not name.strip(): return
        path = self._agent_dir(p) / f"Agent_{name.strip()}.md"
        path.write_text("# Agent Version\n\n(Add directives…)\n", encoding="utf-8")
        self._status(f"Agent file created: {path}")

    def _export_selected_note(self):
        idx = self.tabs_notes.currentIndex()
        if idx < 0: QMessageBox.information(self,"Notes","Select a note tab first."); return
        w = self.tabs_notes.widget(idx)
        if not isinstance(w, QPlainTextEdit): return
        txt = w.toPlainText()
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        out = self._agent_dir(p) / f"Agent_{version_stamp()}.md"
        out.write_text(txt, encoding="utf-8")
        self._status(f"Exported note to {out}")

    def _open_agent_manager(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        AgentManager(p, self).exec()

    # ---------- Assistant / Notes / ErrorBot ----------
    def _assistant_send(self):
        msg = self.ass_in.toPlainText().strip()
        if not msg: return
        self.ass_in.clear()
        base = self.cfg.get("oss_base_url","http://localhost:11434")
        model = self.cb_assistant.currentText()
        sys_prompt = "You are a pragmatic engineering copilot inside Codex Lite. Prefer concrete steps, short patches, and file paths."
        start = time.time()
        ok, out = ollama_chat(base, model, [{'role':'user','content':msg}], sys_prompt)
        self.chat.append_message('user', msg)
        if not ok:
            self._status(out)
            self.chat.append_message('assistant', out)
            return
        self.chat.append_message('assistant', out)
        self._last_assistant_msg = out
        elapsed = time.time() - start
        self._status(f"Assistant responded in {elapsed:.2f}s")
        content = f"You: {msg}\n\nAssistant({model}):\n{out}"
        p = self._current_project()
        if p: dataset_store_bucket(p, "assistant", f"Asst_{version_stamp()}", content, version_stamp())
        try:
            ASSISTANT_TIMING_LOG.open("a", encoding="utf-8").write(f"{datetime.now().isoformat()}\n")
        except Exception as e:
            logging.exception("Assistant timing log failed")
            self._status(f"Assistant timing log failed: {e}")

    def _assistant_to_note(self):
        if not getattr(self, '_last_assistant_msg', ''):
            QMessageBox.information(self,"Assistant","No assistant output to summarize."); return
        summary = self._summarize_text(self._last_assistant_msg)
        self._note_create(summary)

    def _summarize_text(self, text: str) -> str:
        base = self.cfg.get("oss_base_url","http://localhost:11434")
        model = self.cb_notes.currentText()
        sys_prompt = "Summarize into actionable, terse bullet points with file paths and diffs when relevant."
        ok, out = ollama_chat(base, model, [{'role':'user','content':text}], sys_prompt)
        return out if ok and out.strip() else text[:2000]

    def _note_create(self, content: str):
        te = QPlainTextEdit(); te.setLineWrapMode(QPlainTextEdit.NoWrap); te.setPlainText(content)
        title = f"Note_{version_stamp()}"
        idx = self.tabs_notes.addTab(te, title); self.tabs_notes.setCurrentIndex(idx)
        p = self._current_project()
        if p: dataset_store_bucket(p, "notes", title, content, version_stamp())
        try:
            self.task_manager.add_task(title=title, content=content, status="new")
        except Exception as e:
            logging.exception("add_task failed")

    def _note_save(self):
        idx = self.tabs_notes.currentIndex()
        if idx < 0: return
        w = self.tabs_notes.widget(idx)
        if not isinstance(w, QPlainTextEdit): return
        content = w.toPlainText()
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        dataset_store_bucket(p, "notes", self.tabs_notes.tabText(idx), content, version_stamp())
        try:
            self.task_manager.add_task(title=self.tabs_notes.tabText(idx), content=content, status="saved")
        except Exception as e:
            logging.exception("add_task failed")
        self._status("Note saved (SQL version bump).")

    def _close_bucket(self, tabs: QTabWidget, operator: str, i: int):
        if i<0: return
        title = tabs.tabText(i)
        tabs.removeTab(i)
        p = self._current_project()
        if p:
            dataset_delete_bucket(p, operator, title)
            self._status(f"{operator} bucket removed: {title}")

    # ---------- Tasks ----------
    def _tasks_refresh(self):
        self.task_manager.reload()
        self.list_tasks.clear()
        try:
            tasks = self.task_manager.list_tasks()
        except Exception as e:
            logging.exception("Task refresh failed")
            self._status(f"Task refresh failed: {e}")
            return
        for t in tasks:
            text = f"{t.get('title', '')} ({t.get('status')})"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, t.get("id"))
            item.setData(Qt.UserRole + 1, t.get("status"))
            self.list_tasks.addItem(item)
            summary = t.get("summary")
            if summary:
                summary = html.escape(summary)
                summ = QLabel()
                summ.setTextFormat(Qt.RichText)
                summ.setText(summary)
                self.list_tasks.setItemWidget(item, summ)
        self._task_selection_changed(self.list_tasks.currentItem(), None)

    def _task_done(self):
        item = self.list_tasks.currentItem()
        if not item: return
        tid = item.data(Qt.UserRole)
        try:
            self.task_manager.mark_done(tid)
        except Exception as e:
            logging.exception("Mark done failed")
            QMessageBox.information(self, "Tasks", f"Complete failed: {e}")

    def _task_pause(self):
        item = self.list_tasks.currentItem()
        if not item:
            return
        tid = item.data(Qt.UserRole)
        try:
            self.task_manager.pause_task(tid)
        except Exception as e:
            logging.exception("Pause task failed")
            QMessageBox.information(self, "Tasks", f"Pause failed: {e}")

    def _task_remove(self):
        item = self.list_tasks.currentItem()
        if not item: return
        tid = item.data(Qt.UserRole)
        if QMessageBox.question(self, "Tasks", "Remove selected task?") != QMessageBox.Yes:
            return
        try:
            self.task_manager.remove_task(tid)
        except Exception as e:
            logging.exception("Remove task failed")
            QMessageBox.information(self, "Tasks", f"Remove failed: {e}")

    def _task_selection_changed(self, current, _prev):
        status = current.data(Qt.UserRole + 1) if current else None
        disabled = status == "done"
        for b in [self.btn_task_pause, self.btn_task_done, self.btn_task_remove]:
            b.setEnabled(current is not None and not disabled)

    def _security_settings(self):
        dlg = SecurityDialog(self.cfg, self)
        if dlg.exec_():
            self.cfg.update(dlg.values())
            save_json(CONFIG_JSON, self.cfg)
            self.chk_full_auto.setChecked(self.cfg.get("full_auto", False))

    # ---------- Codex Setup / Launch ----------
    def _codex_bin_in_project(self, project: Path) -> Path:
        return project / "Codex" / ("codex.exe" if os.name=="nt" else "codex")

    def _codex_repo_dir(self, project: Path) -> Path:
        return project / "Codex" / "codex-src"

    def _setup_codex(self) -> Optional[Path]:
        p = self._current_project()
        if not p:
            QMessageBox.information(self, "Select project", "Choose a project.")
            return None
        target = self._codex_bin_in_project(p)
        target.parent.mkdir(parents=True, exist_ok=True)

        # Sources to copy from (priority order)
        candidates = [
            Path(r"C:\Users\Art PC\Desktop\Codex\Codex-Transit\codex-rust-v0.23.0\codex-x86_64-pc-windows-msvc.exe"),
            Path(r"C:\Users\Art PC\Desktop\Codex\codex-x86_64-pc-windows-msvc.exe"),
        ]
        src = next((c for c in candidates if c.exists()), None)
        if not src:
            # fallback: download from GitHub release
            plat = os.name
            asset = CODEX_ASSETS.get(plat)
            if isinstance(asset, dict):
                import platform as _pf
                asset = asset.get(_pf.system(), "")
            if not asset:
                self._status("Unknown platform; please install Codex manually.")
                return None
            url = f"{CODEX_RELEASE_BASE}/{asset}"
            self._status("Downloading Codex from GitHub…")
            try:
                tmp_dir = Path(tempfile.mkdtemp())
                archive = tmp_dir / asset
                with urllib.request.urlopen(url, timeout=60) as r:
                    archive.write_bytes(r.read())
                bin_path = archive
                if asset.endswith('.zip'):
                    with zipfile.ZipFile(archive) as z:
                        z.extractall(tmp_dir)
                    for name in ['codex.exe', 'codex']:
                        cand = tmp_dir / name
                        if cand.exists():
                            bin_path = cand
                            break
                elif asset.endswith('.tar.gz'):
                    with tarfile.open(archive, 'r:gz') as t:
                        t.extractall(tmp_dir)
                    for name in ['codex.exe', 'codex']:
                        cand = tmp_dir / name
                        if cand.exists():
                            bin_path = cand
                            break
                if plat != 'nt':
                    os.chmod(bin_path, 0o755)
                src = bin_path
                self._status('Download complete.')
            except Exception as e:
                logging.exception("Download failed")
                self._status(f'Download failed: {e}')
                return None

        if target.exists():
            if QMessageBox.question(self, "Overwrite?", "Codex already installed in this project. Overwrite?") == QMessageBox.No:
                self._status("Setup Codex skipped (already installed).")
                return None
        try:
            data = src.read_bytes()
            target.write_bytes(data)
            self._status(f"Codex installed into {target.parent}")
            # make executable on unix
            if os.name!="nt":
                os.chmod(target, 0o755)
        except Exception as e:
            logging.exception("Install failed")
            self._status(f"Install failed: {e}")
            return None

        repo = clone_codex_repo(target.parent)
        if repo:
            self._status(f"Source cloned to {repo}")
        return repo

    def _upload_codex_source(self):
        p = self._current_project()
        if not p:
            QMessageBox.information(self, "Select project", "Choose a project.")
            return
        default = p / "Codex" / "codex-src"
        folder = QFileDialog.getExistingDirectory(self, "Select Codex Source Folder", str(default if default.exists() else p))
        if not folder:
            return
        owner, ok = QInputDialog.getText(self, "GitHub Owner", "Enter your GitHub owner/org name (e.g. Meesh-Makes):")
        if not ok or not owner:
            return
        repo_name, ok = QInputDialog.getText(self, "GitHub Repo Name", "Enter the repository name (e.g. Codex_Studio):")
        if not ok or not repo_name:
            return

        repo_url = f"https://github.com/{owner}/{repo_name}.git"
        QMessageBox.information(self, "Starting", f"Uploading {folder} to {repo_url}...")

        script = APP_ROOT / "tools" / "codex_repo_manager.py"
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "upload",
                    "--workdir",
                    folder,
                    "--remote-url",
                    repo_url,
                    "--default-branch",
                    "main",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            out = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            out = (e.stdout + e.stderr).strip()

        QMessageBox.information(self, "Done", f"Upload complete!\n\n{out}")

    def _write_handshake(self, project: Path):
        info = {
            "project_root": str(project),
            "agent_dir": str(self._agent_dir(project)),
            "datasets": [str(p) for p in dataset_paths(project)],
            "generated": datetime.now().isoformat()
        }
        repo_dir = self._codex_repo_dir(project)
        if repo_dir.exists():
            info["codex_repo"] = str(repo_dir)
        path = project / HANDSHAKE_NAME
        path.write_text(json.dumps(info, indent=2), encoding="utf-8")
        # export env for spawned processes
        os.environ["CODEX_HANDSHAKE"] = str(path)
        self._status(f"Handshake written: {path}")

    def _pre_snapshot_now(self, project: Path):
        snap = make_snapshot(project)
        self._pre_snapshot = snap; self._pre_project = project
        files = [(rel, txt) for rel, (_, txt) in snap.files.items()]
        dataset_store_repo_files(project, files, snap.stamp)
        self._status(f"Pre-snapshot captured (v={snap.stamp}).")

    def _codex_args(self, project: Path, model: str) -> List[str]:
        args = []
        args += ["--oss"]
        args += ["-m", model]
        args += ["-C", str(project)]
        if self.chk_full_auto.isChecked():
            args += ["--full-auto"]
        if torch and getattr(torch, "cuda", None) and torch.cuda.is_available():
            os.environ["OLLAMA_GPU"] = "1"
            args += ["--gpu"]
        else:
            os.environ.pop("OLLAMA_GPU", None)
        # no explicit approval/sandbox flags here—`--full-auto` covers it; otherwise Codex defaults apply
        return args

    def _launch_codex(self, mode: str):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        codex = self._codex_bin_in_project(p)
        if not codex.exists():
            self._status("Codex not installed in this project. Click 'Setup Codex' first.")
            return

        self._write_handshake(p)
        self._pre_snapshot_now(p)

        model = self.cb_codex_model.currentText()
        args = self._codex_args(p, model)

        if mode=="External":
            # Spawn terminal window running codex with args
            cmdline = f"\"{codex}\" " + " ".join(shlex.quote(a) for a in args)
            try:
                if os.name=="nt":
                    subprocess.Popen(f'start "" cmd /k {cmdline}', cwd=str(p), shell=True)
                elif sys.platform=="darwin":
                    osa = f'tell application "Terminal"\nactivate\ndo script "cd {shlex.quote(str(p))}; {cmdline}"\nend tell\n'
                    subprocess.Popen(["osascript","-e",osa])
                else:
                    subprocess.Popen(["gnome-terminal","--","bash","-lc",cmdline])
                self._status("External Codex launched. If needed, echo %CODEX_HANDSHAKE% (Windows) to verify.")
            except Exception as e:
                logging.exception("External launch failed")
                self._status(f"External launch failed: {e}")
        else:
            # Embedded QProcess
            self.input_line.setEnabled(True)
            self.codex_proc.setWorkingDirectory(str(p))
            use_pywinpty = False
            prog = str(codex)
            try:
                if os.name == "nt":
                    import pywinpty  # type: ignore
                    prog = sys.executable
                    args = ["-m", "pywinpty", str(codex)] + args
                    use_pywinpty = True
            except Exception as e:
                self._strip_ansi = True
                msg = f"pywinpty unavailable, stripping ANSI: {e}"
                self._status(msg)
                logging.warning(msg)
            self.codex_proc.setProgram(prog)
            self.codex_proc.setArguments(args)
            env = self.codex_proc.processEnvironment()
            env.insert("CODEX_HANDSHAKE", str(p / HANDSHAKE_NAME))
            self.codex_proc.setProcessEnvironment(env)
            self.codex_proc.start()
            if self.codex_proc.waitForStarted(5000):
                self._status("Embedded Codex started.")
            else:
                if os.name == "nt" and use_pywinpty:
                    msg = f"Embedded launch failed via pywinpty: {self.codex_proc.errorString()}"
                    self._strip_ansi = True
                    self._status(msg)
                    logging.warning(msg)
                else:
                    self._status("Embedded launch failed: " + self.codex_proc.errorString())

    def _codex_out(self):
        out = bytes(self.codex_proc.readAllStandardOutput()).decode("utf-8","ignore")
        if self._strip_ansi:
            out = ANSI_ESCAPE_RE.sub('', out)
        if out:
            self.chat.append_message('codex', out)

    def _codex_err(self):
        err = bytes(self.codex_proc.readAllStandardError()).decode("utf-8","ignore")
        if self._strip_ansi:
            err = ANSI_ESCAPE_RE.sub('', err)
        if err:
            self.chat.append_message('codex', err)

    def _handle_slash(self, txt: str) -> bool:
        cmd = txt.strip().split()[0]
        if cmd == "/processdumps":
            try:
                from distill_dumps import main as distill_main
                distill_main()
                self.chat.append_message('system', "/processdumps complete")
            except Exception as e:
                logging.exception("/processdumps failed")
                self.chat.append_message('system', f"/processdumps failed: {e}")
            return True
        if cmd == "/help":
            self.chat.append_message('system',
                "Slash commands:\n/processdumps – process Codex_Agents/dump*.md into datasets.")
            return True
        return False

    def _send_to_embedded(self):
        txt = self.input_line.text().rstrip()
        if not txt: return
        self.input_line.clear()
        self.chat.append_message('user', txt)
        if txt.startswith('/'):
            if self._handle_slash(txt):
                return
        try:
            self.codex_proc.write((txt + "\n").encode())
        except Exception as e:
            logging.exception("Write to embedded failed")
            self._status(f"Write to embedded failed: {e}")

    # ---------- README ----------
    def _gen_readme(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        generate_readme(p, self._status, ver=version_stamp())

    # ---------- Error Bot ----------
    def _run_error_bot(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        if not self._pre_snapshot or self._pre_project!=p:
            self._pre_snapshot_now(p)
        post = make_snapshot(p)
        files = [(rel, txt) for rel, (_, txt) in post.files.items()]
        dataset_store_repo_files(p, files, post.stamp)
        diffs = diff_snapshots(self._pre_snapshot, post)
        blocks=[]
        for src, patch in diffs:
            if patch.strip():
                dataset_store_diff(p, src, patch, post.stamp)
                blocks.append((datetime.now().isoformat(timespec="seconds"), src, patch))
        self.diffpane.set_blocks(dataset_fetch_diffs_desc(p))
        self._status(f"Error Bot: computed {len(blocks)} diffs (v {post.stamp}).")

        # Compose analysis
        notes_text = self._collect_recent_notes(p, 5)
        agent_snapshot = self._collect_agent_snapshot(p, 1400)
        prompt = self._compose_errorbot_prompt(diffs, notes_text, agent_snapshot)
        base = self.cfg.get("oss_base_url","http://localhost:11434")
        model = self.cb_error.currentText()
        sys_prompt = "You are Error Bot. Be precise; list errors (file:line), risky changes, and next steps."
        ok, out = ollama_chat(base, model, [{'role':'user','content':prompt}], sys_prompt)
        report = out if ok else "Error Bot failed to produce output."
        te = QPlainTextEdit(); te.setLineWrapMode(QPlainTextEdit.NoWrap); te.setPlainText(report)
        title = f"ErrorBot_{version_stamp()}"; idx = self.tabs_error.addTab(te, title); self.tabs_error.setCurrentIndex(idx)
        dataset_store_bucket(p, "errorbot", title, report, version_stamp())
        self._status("Error Bot report created.")

        generate_readme(p, self._status, ver=post.stamp)

    def _collect_recent_notes(self, project: Path, limit:int=5) -> str:
        db = dataset_paths(project)[0]
        conn = sqlite3.connect(str(db)); conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT tab_name, content, version, ts FROM buckets WHERE project=? AND operator='notes' ORDER BY id DESC LIMIT ?",
                (project.name, limit)).fetchall()
            secs=[]
            for r in rows: secs.append(f"[{r['tab_name']} v{r['version']} @{r['ts']}]\n{r['content']}\n")
            return "\n".join(secs)
        finally:
            conn.close()

    def _collect_agent_snapshot(self, project: Path, head_chars:int=1200) -> str:
        d = self._agent_dir(project)
        files = sorted([p for p in d.glob("*.md")], key=lambda p: p.stat().st_mtime, reverse=True)
        names = [p.name for p in files]
        head = ""
        if files:
            try:
                head = files[0].read_text(encoding="utf-8", errors="ignore")[:head_chars]
            except Exception as e:
                logging.warning("Failed to read %s: %s", files[0], e)
                head = ""
        return "AGENT_FILES:\n- " + "\n- ".join(names) + ("\n\nLATEST_HEAD:\n" + head if head else "")

    def _compose_errorbot_prompt(self, diffs: List[Tuple[str,str]], notes: str, agents: str) -> str:
        parts = ["Analyze codebase changes and surface:\n- Errors introduced (-diff)\n- Improvement hints (+diff)\n- Cross-check with Notes and Agent directives.\n"]
        if diffs:
            parts.append("\n".join([f"--- DIFF ({src}) ---\n{patch}" for src, patch in diffs[:50]]))
        if notes: parts.append("\n--- NOTES ---\n" + notes)
        if agents: parts.append("\n--- AGENT SNAPSHOT ---\n" + agents)
        parts.append("\nProvide:\n- Errors (file:line → reason)\n- Risky changes\n- Concrete next actions\n")
        return "\n".join(parts)

    def _save_patch(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        rows = dataset_fetch_diffs_desc(p)
        if not rows: QMessageBox.information(self,"No diffs","Nothing to export."); return
        ts = version_stamp()
        out = DIFFS_DIR / f"diff_{ts}.patch"
        with out.open("w", encoding="utf-8") as f:
            for ts_, src, content in rows:
                f.write(f"--- [{ts_}] source={src} ---\n{content}\n\n")
        self.chat.append_message('system', f"Patch exported: {out}")

# ======== Main Window ========
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Codex Lite — Local Ollama • Codex Rust • Buckets • Agent.md • Error Bot")
        self.resize(1480, 980)
        self.statusBar().showMessage("Booting…")
        self.w = CodexLite(self.statusBar().showMessage)
        self.setCentralWidget(self.w)

        # Task panel docked on the right
        self.tasks_dock = QDockWidget("Tasks", self)
        self.task_list = QListWidget()
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self._task_menu)
        self.tasks_dock.setWidget(self.task_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tasks_dock)

        self.w.task_manager.tasks_changed.connect(self._refresh_tasks)
        self._refresh_tasks()

    def _refresh_tasks(self):
        self.task_list.clear()
        for t in self.w.task_manager.list_tasks():
            item = QListWidgetItem(f"{t['title']} ({t['status']})")
            item.setData(Qt.UserRole, t['id'])
            item.setData(Qt.UserRole + 1, t['status'])
            self.task_list.addItem(item)

    def _task_menu(self, pos):
        item = self.task_list.itemAt(pos)
        if not item:
            return
        task_id = item.data(Qt.UserRole)
        status = item.data(Qt.UserRole + 1)
        menu = QMenu(self)
        if status != "done":
            act_done = menu.addAction("Complete")
            act_done.triggered.connect(lambda: self.w.task_manager.mark_done(task_id))
        act_remove = menu.addAction("Remove")
        act_remove.triggered.connect(lambda: self.w.task_manager.remove_task(task_id))
        menu.exec_(self.task_list.mapToGlobal(pos))

# ======== Entry ========
if __name__ == "__main__":
    try:
        ensure_layout()
        app = QApplication(sys.argv); app.setApplicationName("Codex Lite")
        win = Main(); win.show()
        sys.exit(app.exec())
    except Exception:
        logging.exception("Main failed")
        sys.exit(1)
