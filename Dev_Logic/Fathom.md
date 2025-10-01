# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `fathom.py`

FATHOM — Bedrock (single-file) — vNext (All-in-One)

Includes:
- Installer (Tk) + Launcher (Tk)  [fixed auto-launch quoting on Windows]
- Bedrock/Project UI (PyQt5)
- Tom & Jerry trainers (/trainers) + metrics DB
- Yin/Yang inner monolog → safe snippet proposals (with parsing; no blind core edits)
- Chat + Slash CLI: /status /evolve_launch /verify_all /apply_queue /auto_implement /datasets_refresh
  /code_map /code_show A-B /code_analyze <func> /code_insert /code_replace /trainers
  /autonomy on|off /tts voice <name> /tts readsel
- Apply queue with journaling, semver, CHANGELOG.md, backups
- Evolve Launch: batch apply + AST + py_compile sanity + rollback on failure
- Code Mirror, Function Analyses, Snapshots datasets
- RAG + DIFF-QA mini stores
- Self-heal task from recent errors
- TTS fallback voice; voice selection & restart
- Monolog lane only (no chat spam)
- Console alias (fixes earlier crash path)

Tested with: Python 3.10–3.13, Windows 10/11, PyQt5.

**Classes:** TTSManager, UiBridge, LineNumberArea, CodeEditor, LearningWorker, MainWindow

**Functions:** _log_line(kind, msg), log_info(msg), log_warn(msg), log_err(msg), record_error(source, message, detail), ensure_dirs(target_root), db_connect(path), _ensure_column(cx, table, col, decl), init_main_db(), ensure_assets_schema(), init_readme_db(), init_rag_db(), init_diffqa_db(), init_all_dbs(), _sha256_text(s), make_backup(path), readme_set(key, val), readme_topical_snapshot(topic, limit_chars), ingest_file(p, kind), rag_search_raw(query, limit), diffqa_add(q, a, tags), diffqa_search(q, limit_chars), _code_mirror_store(script_path, code), _code_mirror_load(script_path), _fn_analyses_store(script_path, analyses), _fn_analyses_load(script_path), create_function_snapshots(script_path), analyze_functions(script_path), rebuild_code_datasets(script_path), add_conversation(lane, role, content), get_conversation(lane, limit), add_task(title, body), set_task_status(tid, status), list_tasks(limit), add_snippet(task_id, label, content, target_path, apply_mode, start_line, end_line), list_snippets(limit), enqueue_snippet(sid), dequeue_next(), _read_setting(key, default), _write_setting(key, val), current_semver(), bump_semver(level, msg), _unified_diff_text(before, after, a_name, b_name), _count_changes(diff_text), _atomic_write_text(target, text), _record_indent_learning(after_text, target), append_changelog(title, file_path, diff_text, ok, note), apply_snippet(snippet), ensure_preloaded_tasks(), _desktop_dir(), _write(p, text), write_launcher_script(root), _create_windows_shortcut(desktop, root), write_desktop_shortcut(root), _elevated_launch_windows(py, arg_script, cwd, as_admin), launch_launcher(root, as_admin), schedule_self_delete(original_script), preseed_dev_key(root), _dev_token_fresh(), _dev_mode_requested(here), initialize_bedrock_root(target_root), _tk_install_gui(current_here), ensure_bedrock_install_or_exit(), build_machine_readme(code), ingest_initial(), _http_get(url, timeout), _http_post_json(url, data, timeout), ollama_reachable(url), chat_once(url, model, messages), add_hypothesis(title, evidence, pseudocode, confidence), _sanity_parse_script(path), _py_compile_script(path, timeout), run_trainer_box(name, color, lifetime_sec), run_trainer_pair(), _in_core_protected_range(a, b), _safe_to_text(x), _normalize_selected_text(txt), _slice_lines(text, start, end), run_qt(role)


## Detailed Module Analyses


## Module `fathom.py`

```python
# -*- coding: utf-8 -*-
"""
FATHOM — Bedrock (single-file) — vNext (All-in-One)

Includes:
- Installer (Tk) + Launcher (Tk)  [fixed auto-launch quoting on Windows]
- Bedrock/Project UI (PyQt5)
- Tom & Jerry trainers (/trainers) + metrics DB
- Yin/Yang inner monolog → safe snippet proposals (with parsing; no blind core edits)
- Chat + Slash CLI: /status /evolve_launch /verify_all /apply_queue /auto_implement /datasets_refresh
  /code_map /code_show A-B /code_analyze <func> /code_insert /code_replace /trainers
  /autonomy on|off /tts voice <name> /tts readsel
- Apply queue with journaling, semver, CHANGELOG.md, backups
- Evolve Launch: batch apply + AST + py_compile sanity + rollback on failure
- Code Mirror, Function Analyses, Snapshots datasets
- RAG + DIFF-QA mini stores
- Self-heal task from recent errors
- TTS fallback voice; voice selection & restart
- Monolog lane only (no chat spam)
- Console alias (fixes earlier crash path)

Tested with: Python 3.10–3.13, Windows 10/11, PyQt5.
"""

from __future__ import annotations

import os, sys, re, json, time, shutil, sqlite3, traceback, threading, difflib, hashlib, subprocess, tempfile, signal
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Tuple, List, Any

# -------------------- Constants & Theme --------------------

APP_NAME = "FATHOM"
PRIMARY_MODEL = "deepseek-coder-v2:16b"
FALLBACK_MODEL = "phi4:latest"
DEFAULT_OLLAMA_URL = "http://localhost:11434"

MAX_CODE_CHUNK_CHARS = 120_000
MAX_SNAPSHOT_JSON_CHARS = 24_000

# Colors
BEDROCK_GREEN = "#18612b"
PROJECT_GREEN = "#1e7a36"
ORANGE_IMPL   = "#f39c12"
DARK_BG       = "#0f1113"
PANEL_BG      = "#15181a"
TEXT_FG       = "#e8e6e3"
ERROR_RED     = "#ff4d4d"
OK_GREEN      = "#33c655"
AGENT_PURPLE  = "#c679ff"
LINK_BLUE     = "#58a6ff"

# -------------------- Script/Root detection --------------------

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_NAME = SCRIPT_PATH.name
HERE        = SCRIPT_PATH.parent

# Rebound by ensure_dirs(...)
ROOT: Path = HERE
RUNTIME: Path = ROOT / "runtime"
DB_DIR: Path = RUNTIME / "db"
DOCS_DIR: Path = RUNTIME / "docs"
LOGS_DIR: Path = RUNTIME / "logs"
BACKUPS_DIR: Path = ROOT / "backups"
LAUNCHER_DIR: Path = ROOT / "launcher"
PROJECTS_DIR: Path = ROOT / "projects"

MAIN_DB: Path = DB_DIR / "main.sqlite3"
README_DB: Path = DB_DIR / "readme.db"
RAG_DB: Path = DB_DIR / "rag.db"
DIFFQA_DB: Path = DB_DIR / "diffqa.db"
ASSETS_DB: Path = DB_DIR / "assets.db"

CHANGELOG_MD: Path = DOCS_DIR / "CHANGELOG.md"

LAUNCHER_NAME = "fathom_launcher.py"
DEV_KEY_DEFAULT = "3030"  # hashed and stored in runtime/dev/dev_key.txt

# Markers/tokens
BEDROCK_MARK = ".bedrock_marker"
INSTALL_DONE = ".install_complete"
LAUNCHER_READY = ".launcher_ready"
DEV_DIR_NAME = "dev"
DEV_KEY_FILE = "dev_key.txt"
DEV_TOKEN = "allow_bedrock_ui.token"

# -------------------- Logging --------------------

def _log_line(kind: str, msg: str):
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with (LOGS_DIR / "events.log").open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {kind.upper()}: {msg}\n")
    except Exception:
        pass

def log_info(msg: str): _log_line("info", msg)
def log_warn(msg: str): _log_line("warn", msg)
def log_err(msg: str):  _log_line("err", msg)

def record_error(source: str, message: str, detail: str = ""):
    _log_line("error", f"{source} | {message} | {detail[:800]}")
    try:
        with db_connect(MAIN_DB) as cx:
            cx.execute("""INSERT INTO errors(source, message, detail, created_at)
                          VALUES(?,?,?,?)""", (source, message, detail[:8000], int(time.time())))
    except Exception:
        pass

# -------------------- Paths / Dirs --------------------

def ensure_dirs(target_root: Path):
    """Rebind globals to a new root and ensure directories exist."""
    global ROOT, RUNTIME, DB_DIR, DOCS_DIR, LOGS_DIR, BACKUPS_DIR, LAUNCHER_DIR, PROJECTS_DIR
    global MAIN_DB, README_DB, RAG_DB, DIFFQA_DB, ASSETS_DB, CHANGELOG_MD

    ROOT = target_root
    RUNTIME = ROOT / "runtime"
    DB_DIR = RUNTIME / "db"
    DOCS_DIR = RUNTIME / "docs"
    LOGS_DIR = RUNTIME / "logs"
    BACKUPS_DIR = ROOT / "backups"
    LAUNCHER_DIR = ROOT / "launcher"
    PROJECTS_DIR = ROOT / "projects"

    MAIN_DB = DB_DIR / "main.sqlite3"
    README_DB = DB_DIR / "readme.db"
    RAG_DB = DB_DIR / "rag.db"
    DIFFQA_DB = DB_DIR / "diffqa.db"
    ASSETS_DB = DB_DIR / "assets.db"

    CHANGELOG_MD = DOCS_DIR / "CHANGELOG.md"

    for d in (RUNTIME, DB_DIR, DOCS_DIR, LOGS_DIR, BACKUPS_DIR, LAUNCHER_DIR, PROJECTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

# -------------------- DB Helpers & Schema --------------------

def db_connect(path: Path) -> sqlite3.Connection:
    cx = sqlite3.connect(str(path))
    cx.row_factory = sqlite3.Row
    return cx

def _ensure_column(cx: sqlite3.Connection, table: str, col: str, decl: str):
    try:
        cols = [r[1] for r in cx.execute(f"PRAGMA table_info({table})")]
        if col not in cols:
            cx.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")
    except Exception as e:
        record_error("db_add_column", f"{table}.{col} failed", repr(e))

def init_main_db():
    with db_connect(MAIN_DB) as cx:
        cx.executescript("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lane TEXT,
            role TEXT,
            content TEXT,
            pushed INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        );
        CREATE INDEX IF NOT EXISTS idx_messages_lane ON messages(lane);

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            body TEXT,
            status TEXT,
            created_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            label TEXT,
            content TEXT,
            target_path TEXT,
            apply_mode TEXT,
            start_line INTEGER,
            end_line INTEGER,
            created_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snippet_id INTEGER,
            enqueued_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            message TEXT,
            detail TEXT,
            created_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semver TEXT,
            tag TEXT,
            message TEXT,
            created_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS settings (
            k TEXT PRIMARY KEY,
            v TEXT
        );

        CREATE TABLE IF NOT EXISTS patch_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            snippet_id INTEGER,
            file_path TEXT,
            apply_mode TEXT,
            before_sha TEXT,
            after_sha TEXT,
            lines_added INTEGER,
            lines_removed INTEGER,
            diff TEXT,
            ok INTEGER,
            error TEXT,
            created_at INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_journal_when ON patch_journal(created_at);
        CREATE INDEX IF NOT EXISTS idx_journal_file ON patch_journal(file_path);

        -- vNext additions
        CREATE TABLE IF NOT EXISTS hypotheses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            evidence_json TEXT,
            pseudocode TEXT,
            confidence REAL,
            created_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS trainer_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainer TEXT,
            success INTEGER,
            summary TEXT,
            metrics_json TEXT,
            created_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS evolve_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at INTEGER,
            ended_at INTEGER,
            ok INTEGER,
            applied_snippets INTEGER,
            rolled_back INTEGER,
            note TEXT
        );

        CREATE TABLE IF NOT EXISTS indent_learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            kind TEXT,
            line INTEGER,
            message TEXT,
            context_sha TEXT,
            created_at INTEGER
        );
        """)
        _ensure_column(cx, "snippets", "start_line", "INTEGER")
        _ensure_column(cx, "snippets", "end_line", "INTEGER")
    with db_connect(MAIN_DB) as cx:
        row = cx.execute("SELECT v FROM settings WHERE k='semver'").fetchone()
        if not row:
            cx.execute("INSERT INTO settings(k,v) VALUES('semver','0.0.0')")

def ensure_assets_schema():
    with db_connect(ASSETS_DB) as cx:
        cx.executescript("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT,
            key TEXT,
            value TEXT,
            updated_at INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_assets_kind_key ON assets(kind,key);

        CREATE TABLE IF NOT EXISTS fn_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_path TEXT,
            func_name TEXT,
            start_line INTEGER,
            end_line INTEGER,
            hash TEXT,
            code TEXT,
            updated_at INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_fn_snap ON fn_snapshots(script_path, func_name);

        CREATE TABLE IF NOT EXISTS code_mirrors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_path TEXT,
            checksum TEXT,
            line_count INTEGER,
            code TEXT,
            updated_at INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_code_mirror ON code_mirrors(script_path);

        CREATE TABLE IF NOT EXISTS fn_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_path TEXT,
            func_name TEXT,
            start_line INTEGER,
            end_line INTEGER,
            params TEXT,
            returns TEXT,
            raises TEXT,
            side_effects TEXT,
            notes TEXT,
            has_docstring INTEGER,
            updated_at INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_fn_analyses ON fn_analyses(script_path, func_name);
        """)

def init_readme_db():
    with db_connect(README_DB) as cx:
        cx.executescript("""
        CREATE TABLE IF NOT EXISTS readme (
            k TEXT PRIMARY KEY,
            v TEXT
        );
        """)

def init_rag_db():
    with db_connect(RAG_DB) as cx:
        cx.executescript("""
        CREATE TABLE IF NOT EXISTS artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            kind TEXT,
            title TEXT,
            content TEXT,
            created_at INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_artifacts_path ON artifacts(path);
        """)

def init_diffqa_db():
    with db_connect(DIFFQA_DB) as cx:
        cx.executescript("""
        CREATE TABLE IF NOT EXISTS diffqa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q TEXT,
            a TEXT,
            tags TEXT,
            created_at INTEGER
        );
        """)

def init_all_dbs():
    init_main_db()
    ensure_assets_schema()
    init_readme_db()
    init_rag_db()
    init_diffqa_db()

# -------------------- Small utils --------------------

def _sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8","replace")).hexdigest()

def make_backup(path: Path):
    try:
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        to = BACKUPS_DIR / f"{path.name}.{ts}.bak"
        shutil.copy2(str(path), str(to))
    except Exception as e:
        record_error("backup", f"failed to backup {path}", repr(e))

# -------------------- README / RAG / DIFFQA --------------------

def readme_set(key: str, val: str):
    with db_connect(README_DB) as cx:
        cx.execute("INSERT INTO readme(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (key, val))

def readme_topical_snapshot(topic: str, limit_chars: int = 2000) -> str:
    with db_connect(README_DB) as cx:
        rows = cx.execute("SELECT v FROM readme").fetchall()
    text = "\n\n".join(r["v"] for r in rows)
    return text[:limit_chars]

def ingest_file(p: Path, kind: str = "data"):
    try:
        title = p.name
        content = p.read_text(encoding="utf-8", errors="replace")
        with db_connect(RAG_DB) as cx:
            cx.execute("INSERT INTO artifacts(path, kind, title, content, created_at) VALUES(?,?,?,?,?)",
                       (str(p), kind, title, content[:200000], int(time.time())))
    except Exception as e:
        record_error("ingest", f"failed ingest {p}", repr(e))

def rag_search_raw(query: str, limit: int = 50) -> List[Dict[str,Any]]:
    with db_connect(RAG_DB) as cx:
        rows = cx.execute("SELECT * FROM artifacts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]

def diffqa_add(q: str, a: str, tags: str = ""):
    with db_connect(DIFFQA_DB) as cx:
        cx.execute("INSERT INTO diffqa(q,a,tags,created_at) VALUES(?,?,?,?)", (q, a, tags, int(time.time())))

def diffqa_search(q: str, limit_chars: int = 1200) -> str:
    with db_connect(DIFFQA_DB) as cx:
        rows = cx.execute("SELECT q,a FROM diffqa ORDER BY id DESC LIMIT 40").fetchall()
    out, size = [], 0
    for r in rows:
        seg = f"Q: {r['q']}\nA: {r['a']}\n"
        if size + len(seg) > limit_chars: break
        out.append(seg); size += len(seg)
    return "".join(out)

# -------------------- Code Mirror & Function Analyses --------------------

def _code_mirror_store(script_path: Path, code: str):
    try:
        with db_connect(ASSETS_DB) as cx:
            cx.execute("DELETE FROM code_mirrors WHERE script_path=?", (str(script_path),))
            cx.execute("""INSERT INTO code_mirrors(script_path, checksum, line_count, code, updated_at)
                          VALUES(?,?,?,?,?)""",
                       (str(script_path), _sha256_text(code), len(code.splitlines()), code, int(time.time())))
    except Exception as e:
        record_error("code_mirror", "store failed", repr(e))

def _code_mirror_load(script_path: Path) -> Dict[str,Any]:
    with db_connect(ASSETS_DB) as cx:
        row = cx.execute("SELECT * FROM code_mirrors WHERE script_path=?", (str(script_path),)).fetchone()
    return dict(row) if row else {}

def _fn_analyses_store(script_path: Path, analyses: List[Dict[str,Any]]):
    try:
        with db_connect(ASSETS_DB) as cx:
            cx.execute("DELETE FROM fn_analyses WHERE script_path=?", (str(script_path),))
            for a in analyses:
                cx.execute("""INSERT INTO fn_analyses(script_path, func_name, start_line, end_line,
                              params, returns, raises, side_effects, notes, has_docstring, updated_at)
                              VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                           (str(script_path), a["func_name"], a["start_line"], a["end_line"],
                            json.dumps(a["params"], ensure_ascii=False),
                            a["returns"], a["raises"], a["side_effects"], a["notes"],
                            1 if a["has_docstring"] else 0, int(time.time())))
    except Exception as e:
        record_error("fn_analyses", "store failed", repr(e))

def _fn_analyses_load(script_path: Path) -> List[Dict[str,Any]]:
    with db_connect(ASSETS_DB) as cx:
        rows = cx.execute("""SELECT func_name,start_line,end_line,params,returns,raises,side_effects,notes,has_docstring
                             FROM fn_analyses WHERE script_path=? ORDER BY start_line ASC""", (str(script_path),)).fetchall()
    out: List[Dict[str,Any]] = []
    for r in rows:
        d = dict(r)
        try: d["params"] = json.loads(d.get("params") or "[]")
        except Exception: d["params"] = []
        out.append(d)
    return out

def create_function_snapshots(script_path: Path) -> int:
    import ast
    try:
        text = script_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
        lines = text.splitlines(True)
    except Exception as e:
        record_error("snapshots", "parse failed", repr(e))
        return 0

    now = int(time.time()); count = 0
    with db_connect(ASSETS_DB) as cx:
        cx.execute("DELETE FROM fn_snapshots WHERE script_path=?", (str(script_path),))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start = node.lineno
                end = getattr(node, "end_lineno", None)
                if not end:
                    end = max((getattr(n, "lineno", start) for n in ast.walk(node)), default=start)
                code = "".join(lines[start-1:end])
                h = _sha256_text(code)
                cx.execute("""INSERT INTO fn_snapshots(script_path,func_name,start_line,end_line,hash,code,updated_at)
                              VALUES(?,?,?,?,?,?,?)""",
                           (str(script_path), node.name, start, end, h, code, now))
                count += 1
    log_info(f"Function snapshots updated: {count}")
    return count

def analyze_functions(script_path: Path) -> List[Dict[str,Any]]:
    import ast
    try:
        code = script_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(code)
    except Exception as e:
        record_error("fn_analyze", "parse failed", repr(e))
        return []

    analyses = []
    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            params = []
            for a in node.args.args: params.append(a.arg)
            if node.args.vararg: params.append("*" + node.args.vararg.arg)
            for a in node.args.kwonlyargs: params.append(a.arg)
            if node.args.kwarg: params.append("**" + node.args.kwarg.arg)

            def ann_to_str(ann):
                if ann is None: return ""
                try:
                    return ast.unparse(ann)
                except Exception:
                    return ""

            returns = ann_to_str(node.returns)

            has_doc = ast.get_docstring(node) is not None

            raises = []
            side_effects = set()
            notes = []
            bare_except = False
            pass_in_except = False
            uses_record_error = False

            for child in ast.walk(node):
                if isinstance(child, ast.Raise):
                    try:
                        txt = ast.unparse(child.exc) if hasattr(ast, "unparse") else "raise"
                    except Exception:
                        txt = "raise"
                    raises.append(txt[:120])
                if isinstance(child, ast.Call):
                    try:
                        txt = ast.unparse(child.func) if hasattr(ast, "unparse") else ""
                    except Exception:
                        txt = ""
                    if txt:
                        if txt.startswith("record_error"): uses_record_error = True
                        if txt.startswith(("Path(", "open(", "shutil.", "os.", "subprocess.")):
                            side_effects.add("io/process")
                if isinstance(child, ast.ExceptHandler):
                    if child.type is None: bare_except = True
                    body_txt = "".join([type(x).__name__ for x in child.body])
                    if body_txt.strip() in ("Pass",): pass_in_except = True

            if bare_except: notes.append("bare except")
            if pass_in_except: notes.append("except body: pass")
            if not uses_record_error and ("io/process" in side_effects or raises):
                notes.append("no record_error around risky ops")

            analyses.append({
                "func_name": node.name,
                "start_line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "params": params,
                "returns": returns,
                "raises": ", ".join(raises[:4]),
                "side_effects": ", ".join(sorted(side_effects)) or "",
                "notes": "; ".join(notes) or "",
                "has_docstring": has_doc
            })

    Visitor().visit(tree)
    return analyses

def rebuild_code_datasets(script_path: Path):
    try:
        code = script_path.read_text(encoding="utf-8", errors="replace")
        _code_mirror_store(script_path, code)
        create_function_snapshots(script_path)
        _fn_analyses_store(script_path, analyze_functions(script_path))
    except Exception as e:
        record_error("dataset_rebuild", "failed", repr(e))

# -------------------- Conversations / Tasks / Snippets / Queue --------------------

def add_conversation(lane: str, role: str, content: str):
    with db_connect(MAIN_DB) as cx:
        cx.execute("INSERT INTO messages(lane,role,content,created_at) VALUES(?,?,?,?)", (lane, role, content, int(time.time())))

def get_conversation(lane: str, limit: int = 200) -> List[Dict[str,Any]]:
    with db_connect(MAIN_DB) as cx:
        rows = cx.execute("SELECT role,content,pushed FROM messages WHERE lane=? ORDER BY id DESC LIMIT ?",
                          (lane, limit)).fetchall()
    return [dict(r) for r in rows][::-1]

def add_task(title: str, body: str) -> int:
    with db_connect(MAIN_DB) as cx:
        cx.execute("INSERT INTO tasks(title, body, status, created_at) VALUES(?,?,?,?)", (title, body, "new", int(time.time())))
        return cx.execute("SELECT last_insert_rowid()").fetchone()[0]

def set_task_status(tid: int, status: str):
    with db_connect(MAIN_DB) as cx:
        cx.execute("UPDATE tasks SET status=? WHERE id=?", (status, tid))

def list_tasks(limit: int = 200) -> List[Dict[str,Any]]:
    with db_connect(MAIN_DB) as cx:
        rows = cx.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]

def add_snippet(task_id: int, label: str, content: str, target_path: str, apply_mode: str,
                start_line: Optional[int]=None, end_line: Optional[int]=None) -> int:
    with db_connect(MAIN_DB) as cx:
        cx.execute("""INSERT INTO snippets(task_id,label,content,target_path,apply_mode,start_line,end_line,created_at)
                      VALUES(?,?,?,?,?,?,?,?)""",
                   (task_id, label, content, target_path, apply_mode, start_line, end_line, int(time.time())))
        sid = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        return sid

def list_snippets(limit: int = 200) -> List[Dict[str,Any]]:
    with db_connect(MAIN_DB) as cx:
        rows = cx.execute("SELECT * FROM snippets ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]

def enqueue_snippet(sid: int):
    with db_connect(MAIN_DB) as cx:
        cx.execute("INSERT INTO queue(snippet_id,enqueued_at) VALUES(?,?)", (sid, int(time.time())))

def dequeue_next() -> Optional[Dict[str,Any]]:
    """Pop next snippet from the queue (FIX: always pass a 1-tuple to sqlite)."""
    with db_connect(MAIN_DB) as cx:
        row = cx.execute(
            "SELECT id, snippet_id FROM queue ORDER BY id ASC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        cx.execute("DELETE FROM queue WHERE id=?", (row["id"],))
        # IMPORTANT: sqlite parameter MUST be a 1-tuple -> (value,)
        sn = cx.execute(
            "SELECT * FROM snippets WHERE id=?",
            (int(row["snippet_id"]),)
        ).fetchone()
        return dict(sn) if sn else None



# -------------------- Versioning + Changelog + Journaled apply --------------------

def _read_setting(key: str, default: str = "") -> str:
    with db_connect(MAIN_DB) as cx:
        row = cx.execute("SELECT v FROM settings WHERE k=?", (key,)).fetchone()
        return row["v"] if row else default

def _write_setting(key: str, val: str):
    with db_connect(MAIN_DB) as cx:
        cx.execute("INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (key, val))

def current_semver() -> str:
    v = _read_setting("semver", "0.0.0")
    return v or "0.0.0"

def bump_semver(level: str = "patch", msg: str = "") -> str:
    major, minor, patch = [int(x) for x in current_semver().split(".")]
    if level == "major": major, minor, patch = major+1, 0, 0
    elif level == "minor": minor, patch = minor+1, 0
    else: patch += 1
    newv = f"{major}.{minor}.{patch}"
    _write_setting("semver", newv)
    with db_connect(MAIN_DB) as cx:
        cx.execute("INSERT INTO versions(semver, tag, message, created_at) VALUES(?,?,?,?)",
                   (newv, level, msg, int(time.time())))
    return newv

def _unified_diff_text(before: str, after: str, a_name: str, b_name: str) -> str:
    diff = difflib.unified_diff(before.splitlines(), after.splitlines(), fromfile=a_name, tofile=b_name, lineterm="")
    return "\n".join(diff)

def _count_changes(diff_text: str) -> Tuple[int,int]:
    adds = sum(1 for ln in diff_text.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
    rems = sum(1 for ln in diff_text.splitlines() if ln.startswith("-") and not ln.startswith("---"))
    return adds, rems

def _atomic_write_text(target: Path, text: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(prefix=".fathom_tmp_", dir=str(target.parent))
        with os.fdopen(fd, "w", encoding="utf-8", errors="replace") as f:
            f.write(text)
        if target.exists():
            make_backup(target)
        if hasattr(os, "replace"):
            os.replace(tmp, target); tmp = None
        else:
            shutil.move(tmp, target); tmp = None
    finally:
        try:
            if tmp and os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

def _record_indent_learning(after_text: str, target: Path):
    """Attempt AST parse; record indentation/syntax failures into DB (learning signal)."""
    try:
        import ast
        ast.parse(after_text)
    except IndentationError as e:
        with db_connect(MAIN_DB) as cx:
            cx.execute("""INSERT INTO indent_learning(file_path,kind,line,message,context_sha,created_at)
                          VALUES(?,?,?,?,?,?)""",
                       (str(target), "IndentationError", getattr(e, "lineno", 0), str(e),
                        _sha256_text(after_text), int(time.time())))
        record_error("indent_learning", "IndentationError recorded", repr(e))
    except SyntaxError as e:
        with db_connect(MAIN_DB) as cx:
            cx.execute("""INSERT INTO indent_learning(file_path,kind,line,message,context_sha,created_at)
                          VALUES(?,?,?,?,?,?)""",
                       (str(target), "SyntaxError", getattr(e, "lineno", 0), str(e),
                        _sha256_text(after_text), int(time.time())))
        record_error("indent_learning", "SyntaxError recorded", repr(e))
    except Exception:
        pass

def append_changelog(title: str, file_path: str, diff_text: str, ok: bool, note: str = ""):
    try:
        CHANGELOG_MD.parent.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        status = "OK" if ok else "FAIL"
        header = f"## {ts} — {title} [{status}]"
        block = f"{header}\n**File:** {file_path}\n\n```diff\n{diff_text}\n```\n"
        if note:
            block += f"\n_Note:_ {note}\n"
        old = "# CHANGELOG (FATHOM)\n\n"
        if CHANGELOG_MD.exists():
            old = CHANGELOG_MD.read_text(encoding="utf-8", errors="replace")
        CHANGELOG_MD.write_text(old + "\n" + block + "\n", encoding="utf-8")
    except Exception as e:
        record_error("changelog", "write failed", repr(e))

def apply_snippet(snippet: Dict[str,Any]) -> bool:
    target = Path(snippet["target_path"])
    mode = (snippet.get("apply_mode") or "patch").lower()
    content = snippet.get("content") or ""
    label = snippet.get("label") or "SNIPPET"
    start_line = snippet.get("start_line")
    end_line = snippet.get("end_line")

    ok = False; err_txt = ""; before = ""; after = ""; diff_text = ""; adds=rems=0
    bsha = asha = ""
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        before = target.read_text(encoding="utf-8", errors="replace") if target.exists() else ""

        if mode == "replace":
            after = content
        elif mode == "append":
            after = before + ("" if not before or before.endswith("\n") else "\n") + content + ("" if content.endswith("\n") else "\n")
        elif mode in ("insert_at_line", "replace_range"):
            lines = before.splitlines(True)
            max_line = len(lines)
            if mode == "insert_at_line":
                if not isinstance(start_line, int) or start_line < 1: raise ValueError("insert_at_line requires start_line>=1")
                idx = min(start_line-1, max_line)
                after = "".join(lines[:idx]) + (content if content.endswith("\n") else content + "\n") + "".join(lines[idx:])
            else:  # replace_range
                if not (isinstance(start_line, int) and isinstance(end_line, int) and 1 <= start_line <= end_line):
                    raise ValueError("replace_range requires valid start_line<=end_line")
                a = max(0, start_line-1); b = min(max_line, end_line)
                after = "".join(lines[:a]) + (content if content.endswith("\n") else content + "\n") + "".join(lines[b:])
        else:
            marker = f"# >>> {label}"
            if marker in before and f"# <<< {label}" in before:
                start = before.find(marker)
                end = before.find(f"# <<< {label}", start)
                if end != -1:
                    end += len(f"# <<< {label}")
                    block = f"{marker}\n{content}\n# <<< {label}"
                    after = before[:start] + block + before[end:]
                else:
                    after = before + f"\n{marker}\n{content}\n# <<< {label}\n"
            else:
                pad1 = "" if (before.endswith("\n") or not before) else "\n"
                pad2 = "" if content.endswith("\n") else "\n"
                after = before + f"{pad1}# >>> {label}\n{content}{pad2}# <<< {label}\n"

        diff_text = _unified_diff_text(before, after, f"a/{target.name}", f"b/{target.name}")
        adds, rems = _count_changes(diff_text)
        bsha = _sha256_text(before); asha = _sha256_text(after)

        _atomic_write_text(target, after)
        ok = True

        # learning signal (non-blocking)
        _record_indent_learning(after, target)

    except Exception:
        err_txt = traceback.format_exc()
        record_error("apply_snippet", f"failed {label} → {target}", err_txt)

    # Journal + UI
    try:
        with db_connect(MAIN_DB) as cx:
            cx.execute("""
            INSERT INTO patch_journal(task_id, snippet_id, file_path, apply_mode, before_sha, after_sha,
                                      lines_added, lines_removed, diff, ok, error, created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (int(snippet.get("task_id") or 0),
             int(snippet.get("id") or 0),
             str(target), mode, bsha, asha, int(adds), int(rems),
             diff_text if ok else (err_txt or ""), 1 if ok else 0,
             ("" if ok else err_txt)[:3000], int(time.time())))
    except Exception as e:
        record_error("journal", "insert failed", repr(e))

    title = f"Apply {label}"
    append_changelog(title, str(target), (diff_text if ok else (err_txt or ""))[:40000], ok)
    try:
        if hasattr(MainWindow, "_singleton_ref") and MainWindow._singleton_ref:
            ui = MainWindow._singleton_ref
            if ok:
                newv = bump_semver("patch", f"{title} → {target.name}")
                ui.post_main_line("assistant", f"Implemented **{label}** → {target.name}  (+{adds}/-{rems})  v{newv}")
                ui.post_console(f"Patched {target}  (+{adds}/-{rems}) v{newv}")
                ui.post_refresh_journal()
                if ui.tts.enabled and ui.tts_voice_id:
                    ui.tts.speak(f"Patch applied to {target.name}. Added {adds}, removed {rems}.")
            else:
                ui.post_main_line("error", f"Failed to apply {label} → {target.name}. See Change Journal.")
                ui.post_console_err(f"Apply failed: {label} → {target}")
                ui.post_blink("APPLY FAILED")
                ui.post_refresh_journal()
    except Exception:
        pass

    return ok

# -------------------- Preloaded Tasks --------------------

def ensure_preloaded_tasks():
    existing = {t["title"] for t in list_tasks(9999)}
    wanted = [
        ("Self-Growth Patch", "Ensure learning mode: rebuild datasets; improve instrumentation, logging, and error recovery."),
        ("Requirements-Based Action List", "Discover missing code/data assets; create minimal stubs; record follow-up actions for agents."),
        ("Initial Missing Assets Generation", "Create baseline prompt/trigger/rule tables and README mirrors; ensure agents have contextual scaffolding.")
    ]
    for title, body in wanted:
        if title not in existing:
            tid = add_task(title, body)
            set_task_status(tid, "draft")
    log_info("Preloaded self-growth tasks ensured.")

# -------------------- Tiny Installer GUI (Tk) + Launcher writing --------------------

def _desktop_dir() -> Path:
    if sys.platform.startswith("win"):
        return Path(os.path.join(os.path.expanduser("~"), "Desktop"))
    return Path.home()

def _write(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", errors="replace")

def write_launcher_script(root: Path):
    launcher_dir = root / "launcher"
    launcher_dir.mkdir(parents=True, exist_ok=True)
    launcher_py = launcher_dir / LAUNCHER_NAME
    text = f"""# Tiny FATHOM Launcher (generated)
import os, sys, json, time, shutil, subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
BEDROCK = ROOT / "{SCRIPT_NAME}"
DEV_DIR = ROOT / "runtime" / "dev"
DEV_DIR.mkdir(parents=True, exist_ok=True)
DEV_KEY_FILE = DEV_DIR / "dev_key.txt"
DEV_TOKEN = DEV_DIR / "allow_bedrock_ui.token"
(LAUNCHER_DIR := ROOT / "launcher").mkdir(parents=True, exist_ok=True)
(LAUNCHER_DIR / "{LAUNCHER_READY}").write_text("1")

GREEN = "{BEDROCK_GREEN}"
BG="#101212"; PANEL="#15181a"; TEXT="#e8e6e3"

def read_text(p: Path, d=""):
    try: return p.read_text(encoding="utf-8", errors="replace")
    except: return d

def write_text(p: Path, t: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t, encoding="utf-8", errors="replace")

def read_json(p: Path, d=None):
    try: return json.loads(read_text(p, ""))
    except: return d if d is not None else {{}}

def write_json(p: Path, obj: dict):
    try: write_text(p, json.dumps(obj, indent=2))
    except Exception as e:
        messagebox.showerror("Write failed", str(e))

def verify_dev_key(k: str) -> bool:
    import hashlib
    want = read_text(DEV_KEY_FILE, "").strip()
    if not want: return False
    return want == hashlib.sha256(k.encode("utf-8","replace")).hexdigest()

def place_dev_token():
    write_text(DEV_TOKEN, str(int(time.time())))

def project_list():
    if not PROJECTS.exists(): return []
    return [p for p in PROJECTS.iterdir() if p.is_dir() and (p/".project_marker").exists()]

def create_project():
    name = simpledialog.askstring("New Project", "Project name:")
    if not name: return
    name = name.strip()
    if not name:
        messagebox.showerror("Invalid name","Please enter a non-empty name."); return
    target = PROJECTS / name
    if target.exists():
        messagebox.showerror("Exists","A project with that name already exists."); return
    details = simpledialog.askstring("Details (optional)", "Short note / purpose:")
    try:
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(BEDROCK), str(target / "{SCRIPT_NAME}"))
        (target / ".project_marker").write_text("1")
        (target / "runtime" / "db").mkdir(parents=True, exist_ok=True)
        (target / "runtime" / "docs").mkdir(parents=True, exist_ok=True)
        (target / "runtime" / "logs").mkdir(parents=True, exist_ok=True)
        (target / "backups").mkdir(parents=True, exist_ok=True)
        write_json(target / "project.json", {{"name": name, "details": (details or "").strip(), "created_at": int(time.time())}})
        messagebox.showinfo("Created", f"Project created: {{name}}")
    except Exception as e:
        messagebox.showerror("Create failed", str(e))

def launch_project(p: Path, as_admin=False):
    script = p / "{SCRIPT_NAME}"
    if not script.exists():
        messagebox.showerror("Missing", "Project script missing."); return
    try:
        if os.name == "nt" and as_admin:
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{{script}}"', str(p), 1)
        else:
            subprocess.Popen([sys.executable, str(script)], cwd=str(p))
    except Exception as e:
        messagebox.showerror("Launch failed", str(e))

def delete_project(p: Path):
    if not p or not p.exists(): return
    if not messagebox.askyesno("Delete","Really delete this project?"): return
    try:
        shutil.rmtree(str(p))
        messagebox.showinfo("Deleted", "Project removed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_folder(p: Path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(p))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])
    except Exception as e:
        messagebox.showerror("Open failed", str(e))

def open_bedrock(as_admin=False):
    key = simpledialog.askstring("Dev Portal", "Enter Dev Key:", show="*")
    if not key or not verify_dev_key(key):
        messagebox.showerror("Denied","Bad or missing dev key."); return
    place_dev_token()  # file gate for Bedrock
    # Always pass both: an environment hint and an explicit CLI flag
    try:
        if os.name == "nt" and as_admin:
            import ctypes
            args = f'"{{BEDROCK}}" --bedrock-dev'
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, str(ROOT), 1)
        else:
            env = dict(os.environ)
            env["FATHOM_DEV"] = "1"
            subprocess.Popen([sys.executable, str(BEDROCK), "--bedrock-dev"], cwd=str(ROOT), env=env)
    except Exception as e:
        messagebox.showerror("Launch failed", str(e))

def main():
    PROJECTS.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    root.title("FATHOM Launcher")
    root.configure(bg=BG)
    frm = tk.Frame(root, bg=BG); frm.pack(fill="both", expand=True, padx=12, pady=12)
    title = tk.Label(frm, text="FATHOM Launcher", fg=TEXT, bg=BG, font=("Segoe UI", 16,"bold")); title.pack(anchor="w")
    sub = tk.Label(frm, text="Create and run project clones without touching Bedrock", fg=TEXT, bg=BG); sub.pack(anchor="w", pady=(0,10))

    btns = tk.Frame(frm, bg=BG); btns.pack(anchor="w", pady=(0,10))
    as_admin = tk.BooleanVar(value=False)
    tk.Checkbutton(btns, text="Run as Admin (Windows)", variable=as_admin, bg=BG, fg=TEXT, selectcolor="#333").pack(side="left", padx=(0,12))
    tk.Button(btns, text="New Project", command=lambda: (create_project(), refresh())).pack(side="left", padx=(0,8))
    tk.Button(btns, text="Refresh Projects", command=lambda: refresh()).pack(side="left", padx=(0,8))
    tk.Button(btns, text="Open Bedrock (Dev)", command=lambda: open_bedrock(as_admin.get())).pack(side="left", padx=(0,8))

    listfrm = tk.Frame(frm, bg=PANEL); listfrm.pack(fill="both", expand=True)
    lb = tk.Listbox(listfrm, bg=PANEL, fg=TEXT, selectbackground=GREEN, highlightthickness=0); lb.pack(side="left", fill="both", expand=True)
    sb = tk.Scrollbar(listfrm, command=lb.yview); sb.pack(side="right", fill="y"); lb.config(yscrollcommand=sb.set)

    def refresh():
        lb.delete(0, "end")
        for p in project_list():
            lb.insert("end", p.name)
    refresh()

    act = tk.Frame(frm, bg=BG); act.pack(anchor="w", pady=8)
    def sel():
        s = lb.curselection()
        if not s: return None
        return PROJECTS / lb.get(s[0])

    tk.Button(act, text="Launch", command=lambda: launch_project(sel() or PROJECTS, as_admin.get())).pack(side="left", padx=6)
    tk.Button(act, text="Open Folder", command=lambda: open_folder(sel() or PROJECTS)).pack(side="left", padx=6)
    tk.Button(act, text="Delete", command=lambda: (delete_project(sel() or PROJECTS), refresh())).pack(side="left", padx=6)

    root.mainloop()

if __name__ == "__main__":
    main()
"""
    _write(launcher_py, text)
    _write(launcher_dir / LAUNCHER_READY, "1")


def _create_windows_shortcut(desktop: Path, root: Path) -> Optional[Path]:
    try:
        import pythoncom  # type: ignore
        from win32com.client import Dispatch  # type: ignore
        shell = Dispatch('WScript.Shell')
        shortcut_path = str(desktop / f"{APP_NAME} Launcher.lnk")
        target = sys.executable
        args = f'"{str((root / "launcher" / LAUNCHER_NAME))}"'
        working = str(root / "launcher")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.Arguments = args
        shortcut.WorkingDirectory = working
        shortcut.WindowStyle = 1
        shortcut.IconLocation = target
        shortcut.save()
        return Path(shortcut_path)
    except Exception:
        try:
            bat = desktop / f"{APP_NAME} Launcher.bat"
            launcher_py = root / "launcher" / LAUNCHER_NAME
            bat.write_text(f'@echo off\r\npushd "{launcher_py.parent}"\r\n"{sys.executable}" "{launcher_py.name}"\r\n', encoding="utf-8")
            return bat
        except Exception:
            return None

def write_desktop_shortcut(root: Path) -> Optional[Path]:
    desktop = _desktop_dir()
    try:
        desktop.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return _create_windows_shortcut(desktop, root)

def _elevated_launch_windows(py: Path, arg_script: str, cwd: Path, as_admin: bool):
    """
    FIXED: Non-admin path passes script as its own argv element (no quotes); 
    Admin path uses ShellExecuteW with a quoted string as Windows expects.
    """
    if not as_admin:
        subprocess.Popen([str(py), arg_script], cwd=str(cwd))
        return
    import ctypes
    ctypes.windll.shell32.ShellExecuteW(None, "runas", str(py), f'"{arg_script}"', str(cwd), 1)

def launch_launcher(root: Path, as_admin: bool = False):
    lp = root / "launcher" / LAUNCHER_NAME
    if not lp.exists():
        write_launcher_script(root)
    if sys.platform.startswith("win"):
        _elevated_launch_windows(Path(sys.executable), str(lp), lp.parent, as_admin)
    else:
        subprocess.Popen([sys.executable, str(lp)], cwd=str(lp.parent))

def schedule_self_delete(original_script: Path):
    if not sys.platform.startswith("win"): return
    try:
        bat = original_script.parent / f"_del_{original_script.stem}.bat"
        bat.write_text(
            f"""@echo off
            ping 127.0.0.1 -n 3 >nul
            del "{original_script}" >nul 2>&1
            del "%~f0" >nul 2>&1
            """.replace("            ", ""),
            encoding="utf-8"
        )
        subprocess.Popen([str(bat)], cwd=str(bat.parent), creationflags=0x08000000)
    except Exception as e:
        record_error("self_delete", "schedule failed", repr(e))

def preseed_dev_key(root: Path):
    try:
        dev_dir = root / "runtime" / DEV_DIR_NAME
        dev_dir.mkdir(parents=True, exist_ok=True)
        f = dev_dir / DEV_KEY_FILE
        if not f.exists():
            f.write_text(hashlib.sha256(DEV_KEY_DEFAULT.encode("utf-8","replace")).hexdigest(), encoding="utf-8")
    except Exception as e:
        record_error("devkey", "preseed failed", repr(e))

def _dev_token_fresh() -> bool:
    try:
        tok = ROOT / "runtime" / DEV_DIR_NAME / DEV_TOKEN
        if not tok.exists(): return False
        return True
    except Exception:
        return False
        
# ---- Dev mode gate (no recursion; env, token, or argv unlock) ----
def _dev_mode_requested(here: Path) -> bool:
    """
    Return True when Bedrock should open directly (skip Launcher).
    Triggers:
      • env FATHOM_DEV=1
      • token file: runtime/dev/allow_bedrock_ui.token (written by Launcher after code 3030)
      • CLI flags: --bedrock-dev / --dev / --open-bedrock
    """
    try:
        # 1) Environment flag (Launcher sets this for "Open Bedrock (Dev)")
        if os.environ.get("FATHOM_DEV") == "1":
            return True

        # 2) Token file dropped by the Launcher after verifying the dev key (3030)
        tok = here / "runtime" / DEV_DIR_NAME / DEV_TOKEN
        if tok.exists():
            return True

        # 3) Command-line switches
        if any(arg in sys.argv for arg in ("--bedrock-dev", "--dev", "--open-bedrock")):
            return True

        return False
    except Exception:
        return False

        

def initialize_bedrock_root(target_root: Path):
    ensure_dirs(target_root)
    init_all_dbs()
    ingest_initial()
    ensure_preloaded_tasks()
    preseed_dev_key(target_root)
    _write(target_root / BEDROCK_MARK, "1")
    _write(target_root / INSTALL_DONE, "1")

def _tk_install_gui(current_here: Path) -> Tuple[Optional[Path], bool, bool]:
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title("FATHOM Setup")
    root.configure(bg="#101212")
    fg = "#e8e6e3"

    frm = tk.Frame(root, bg="#101212")
    frm.pack(padx=14, pady=14)

    tk.Label(frm, text="Install FATHOM", fg=fg, bg="#101212", font=("Segoe UI", 15, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,12))
    tk.Label(frm, text="Choose install location. Default is a new 'FATHOM' folder next to this script.", fg=fg, bg="#101212").grid(row=1, column=0, columnspan=3, sticky="w")

    default_target = (current_here / "FATHOM").resolve()
    path_var = tk.StringVar(value=str(default_target))

    tk.Entry(frm, textvariable=path_var, width=58).grid(row=2, column=0, columnspan=2, sticky="we", pady=8)
    def browse():
        p = filedialog.askdirectory(title="Choose install folder (the parent)")
        if p:
            path_var.set(str(Path(p) / "FATHOM"))
    tk.Button(frm, text="Browse…", command=browse).grid(row=2, column=2, sticky="e")

    make_shortcut = tk.BooleanVar(value=True)
    run_admin = tk.BooleanVar(value=False)

    tk.Checkbutton(frm, text="Create Desktop shortcut to the Launcher", variable=make_shortcut, bg="#101212", fg=fg, selectcolor="#333").grid(row=3, column=0, columnspan=3, sticky="w")
    if sys.platform.startswith("win"):
        tk.Checkbutton(frm, text="Run Launcher as Administrator (Windows)", variable=run_admin, bg="#101212", fg=fg, selectcolor="#333").grid(row=4, column=0, columnspan=3, sticky="w")

    btns = tk.Frame(frm, bg="#101212"); btns.grid(row=5, column=0, columnspan=3, sticky="we", pady=(10,0))
    result = {"target": None, "shortcut": False, "admin": False}

    def do_install():
        loc = Path(path_var.get()).resolve()
        parent = loc.parent
        if not parent.exists():
            messagebox.showerror("Bad path", "Parent folder does not exist."); return
        if loc.exists() and not (loc / BEDROCK_MARK).exists():
            tss = time.strftime("%Y%m%d_%H%M%S")
            loc = (parent / f"FATHOM_{tss}").resolve()
        result["target"] = loc
        result["shortcut"] = bool(make_shortcut.get())
        result["admin"] = bool(run_admin.get())
        root.destroy()

    def cancel():
        result["target"] = None
        root.destroy()

    tk.Button(btns, text="Install", command=do_install).pack(side="left", padx=(0,10))
    tk.Button(btns, text="Cancel", command=cancel).pack(side="left")

    root.mainloop()
    return result["target"], result["shortcut"], result["admin"]

def ensure_bedrock_install_or_exit() -> Tuple[str, Path]:
    """
    Returns ("bedrock"| "project", root) if we should continue to open the Qt UI.
    Otherwise this function will launch the external Launcher and sys.exit().
    """
    here = HERE.resolve()

    # Project clones enter directly
    if (here / ".project_marker").exists():
        ensure_dirs(here)
        for d in (here / "runtime" / "db", here / "runtime" / "docs", here / "runtime" / "logs", here / "backups"):
            d.mkdir(parents=True, exist_ok=True)
        return ("project", here)

    # Bedrock folder
    if (here / BEDROCK_MARK).exists():
        ensure_dirs(here)
        # Always (re)write the launcher so fixes propagate
        try:
            write_launcher_script(here)
        except Exception as e:
            record_error("launcher_write", "could not refresh launcher", repr(e))

        # If a dev token/env/flag is present, open Bedrock directly
        if _dev_mode_requested(here):
            return ("bedrock", here)

        # Otherwise, enforce the launcher gate
        try:
            launch_launcher(here, as_admin=False)
        except Exception as e:
            record_error("launch_launcher", "spawn failed", repr(e))
        print("Bedrock is opened only via the Launcher. Opening Launcher and exiting Bedrock…")
        time.sleep(0.6)
        sys.exit(0)

    # Not installed yet → run installer
    target_root, want_shortcut, run_admin = _tk_install_gui(here)
    if not target_root:
        print("Installation aborted by user. Exiting without changes.")
        sys.exit(0)

    try:
        target_root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(SCRIPT_PATH), str(target_root / SCRIPT_NAME))
        write_launcher_script(target_root)
        initialize_bedrock_root(target_root)
        if want_shortcut:
            out = write_desktop_shortcut(target_root)
            if out:
                print(f"Desktop shortcut created: {out}")
        try:
            launch_launcher(target_root, as_admin=run_admin)
        except Exception as e:
            record_error("install", "auto-launch failed", repr(e))
        print("Bedrock installed. Opening the Launcher. Exiting Bedrock…")
    except Exception as e:
        from tkinter import messagebox, Tk
        try:
            tk = Tk(); tk.withdraw()
            messagebox.showerror("FATHOM Setup", f"Installation failed:\\n{e}")
        except Exception:
            pass
        record_error("install", "failed", repr(e))
        sys.exit(1)

    schedule_self_delete(SCRIPT_PATH)
    sys.exit(0)


    target_root, want_shortcut, run_admin = _tk_install_gui(here)
    if not target_root:
        print("Installation aborted by user. Exiting without changes.")
        sys.exit(0)

    try:
        target_root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(SCRIPT_PATH), str(target_root / SCRIPT_NAME))
        write_launcher_script(target_root)
        initialize_bedrock_root(target_root)
        if want_shortcut:
            out = write_desktop_shortcut(target_root)
            if out:
                print(f"Desktop shortcut created: {out}")
        try:
            launch_launcher(target_root, as_admin=run_admin)
        except Exception as e:
            record_error("install", "auto-launch failed", repr(e))
        print("Bedrock installed. Opening the Launcher. Exiting Bedrock…")
    except Exception as e:
        from tkinter import messagebox, Tk
        try:
            tk = Tk(); tk.withdraw()
            messagebox.showerror("FATHOM Setup", f"Installation failed:\n{e}")
        except Exception:
            pass
        record_error("install", "failed", repr(e))
        sys.exit(1)

    schedule_self_delete(SCRIPT_PATH)
    sys.exit(0)

# -------------------- Ingest Initial --------------------

def build_machine_readme(code: str) -> str:
    return f"{APP_NAME} Machine Overview\n\nScript: {SCRIPT_NAME}\nRoot: {ROOT}\n\nLines: {len(code.splitlines())}\n"

def ingest_initial():
    try:
        code = (ROOT / SCRIPT_NAME).read_text(encoding="utf-8", errors="replace")
        readme_set("fathom.py", build_machine_readme(code))
        ingest_file(ROOT / SCRIPT_NAME, "code")
        rebuild_code_datasets(ROOT / SCRIPT_NAME)
    except Exception as e:
        record_error("ingest_initial", "failed", repr(e))

# -------------------- HTTP utilities (no external deps) --------------------

def _http_get(url: str, timeout: int = 5) -> Tuple[int, str]:
    try:
        import urllib.request
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read().decode("utf-8", "replace")
    except Exception as e:
        record_error("http_get", f"{url}", repr(e))
        raise

def _http_post_json(url: str, data: Dict[str,Any], timeout: int = 30) -> Tuple[int, Dict[str,Any], str]:
    try:
        import urllib.request
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            txt = resp.read().decode("utf-8","replace")
            try:
                return resp.getcode(), json.loads(txt), txt
            except Exception:
                return resp.getcode(), {}, txt
    except Exception as e:
        record_error("http_post", f"{url}", repr(e))
        raise

# -------------------- Ollama chat --------------------

def ollama_reachable(url: str) -> bool:
    try:
        base = url.rstrip("/")
        code, _ = _http_get(f"{base}/api/tags", timeout=4)
        return code == 200
    except Exception:
        return False

def chat_once(url: str, model: str, messages: List[Dict[str,str]]) -> str:
    base = (url or DEFAULT_OLLAMA_URL).rstrip("/")

    def _call(mdl: str) -> Tuple[bool, str]:
        payload = {"model": mdl, "messages": messages, "stream": False}
        try:
            code, data, raw = _http_post_json(f"{base}/api/chat", payload, timeout=60)
            if code != 200:
                return False, f"HTTP {code}: {raw[:500]}"
            content = (data.get("message") or {}).get("content") or ""
            if not content:
                return False, "Empty content from model."
            out = {"rationale": "chat_ok", "actions": [], "answer": content}
            return True, json.dumps(out)
        except Exception as e:
            return False, repr(e)

    ok, out = _call(model)
    if not ok and FALLBACK_MODEL and FALLBACK_MODEL != model:
        record_error("chat", f"primary failed ({model}) → fallback", out)
        ok2, out2 = _call(FALLBACK_MODEL)
        if ok2:
            return out2
        record_error("chat", f"fallback failed ({FALLBACK_MODEL})", out2)
        return json.dumps({
            "rationale": "chat_error",
            "actions": ["notify:user", "log:error"],
            "answer": f"(LLM failed)\nPrimary: {out}\nFallback: {out2}"
        })
    if not ok:
        record_error("chat", f"primary failed ({model}) and no fallback", out)
        return json.dumps({
            "rationale": "chat_error",
            "actions": ["notify:user", "log:error"],
            "answer": f"(LLM failed)\n{out}"
        })
    return out

# -------------------- PyQt5 UI --------------------
from PyQt5.QtCore import Qt, QRect, QSize, QPoint, QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QTextCursor, QTextFormat, QPainter, QFontMetrics
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDockWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QPlainTextEdit,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QComboBox
)

try:
    from PyQt5.QtCore import qRegisterMetaType, QItemSelection
    qRegisterMetaType(QTextCursor, "QTextCursor")
    qRegisterMetaType(QItemSelection, "QItemSelection")
except Exception:
    pass

# -------- TTS (with fallback voice, selectable) --------
class TTSManager:
    def __init__(self):
        self.engine = None
        self.enabled = False
        self.voice_id = None
        self._lock = threading.Lock()
        try:
            import pyttsx3  # type: ignore
            e = pyttsx3.init()
            # pick Zira if present; otherwise first available
            chosen = None
            for v in e.getProperty("voices"):
                nm = (getattr(v, "name", "") or "").lower()
                if "zira" in nm:
                    chosen = v.id; break
            if not chosen:
                vs = e.getProperty("voices")
                if vs: chosen = vs[0].id
            if chosen:
                e.setProperty("voice", chosen)
                self.voice_id = chosen
                self.enabled = True
                self.engine = e
        except Exception as e:
            self.enabled = False
            self.engine = None
            record_error("tts", "init failed", repr(e))

    def list_voices(self) -> List[str]:
        try:
            import pyttsx3  # type: ignore
            e = self.engine or pyttsx3.init()
            return [v.id for v in e.getProperty("voices")]
        except Exception:
            return []

    def set_voice(self, name_or_id: str) -> bool:
        if not self.enabled: return False
        try:
            import pyttsx3  # type: ignore
            e = pyttsx3.init()
            got = None
            for v in e.getProperty("voices"):
                if name_or_id.lower() in (v.id.lower(), (v.name or "").lower()):
                    got = v.id; break
            if got:
                e.setProperty("voice", got)
                with self._lock:
                    self.engine = e
                    self.voice_id = got
                return True
        except Exception as ex:
            record_error("tts", "set_voice failed", repr(ex))
        return False

    def speak(self, text: str):
        if not self.enabled or not self.engine: return
        def run():
            with self._lock:
                try:
                    self.engine.stop()
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    record_error("tts", "speak failed", repr(e))
        threading.Thread(target=run, daemon=True).start()

    def stop(self):
        if not self.enabled or not self.engine: return
        try:
            self.engine.stop()
        except Exception:
            pass

class UiBridge(QObject):
    consoleSig = pyqtSignal(str)
    consoleErrSig = pyqtSignal(str)
    mainLineSig = pyqtSignal(str, str)      # role, text
    composeLineSig = pyqtSignal(str, str)   # role, text
    monologSig = pyqtSignal(str)            # text
    statusSig = pyqtSignal(str)
    blinkSig = pyqtSignal(str)
    stopBlinkSig = pyqtSignal()
    refreshJournalSig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

# Code editor (with line-number gutter)
class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor"):
        super().__init__(editor)
        self.codeEditor = editor
    def sizeHint(self):
        return QSize(self.codeEditor.line_number_area_width(), 0)
    def paintEvent(self, event):
        self.codeEditor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self._lineNumberArea = LineNumberArea(self)
        self.setStyleSheet(
            f"QPlainTextEdit {{ background-color: {PANEL_BG}; color: {TEXT_FG}; "
            f"border: 1px solid #333; line-height: 160%; font-size: 12.5px; "
            f"font-family: Consolas, 'Courier New', monospace; }}"
        )
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space + 8

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self._lineNumberArea.scroll(0, dy)
        else:
            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._lineNumberArea)
        painter.fillRect(event.rect(), QColor("#101214"))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        fm = QFontMetrics(self.font())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#666"))
                painter.drawText(
                    0, top, self._lineNumberArea.width() - 6, fm.height(),
                    Qt.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlight_current_line(self):
        try:
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#2a2a2a")
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            c = self.textCursor()
            c.clearSelection()
            selection.cursor = c
            self.setExtraSelections([selection])
        except Exception:
            pass

# ===== Helper inserts for new features =====

def add_hypothesis(title: str, evidence: dict, pseudocode: str, confidence: float = 0.5):
    try:
        with db_connect(MAIN_DB) as cx:
            cx.execute("""INSERT INTO hypotheses(title, evidence_json, pseudocode, confidence, created_at)
                          VALUES(?,?,?,?,?)""",
                       (title, json.dumps(evidence)[:8000], pseudocode[:8000], float(confidence), int(time.time())))
    except Exception as e:
        record_error("hypothesis", "insert failed", repr(e))

def _sanity_parse_script(path: Path) -> Tuple[bool, str]:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        import ast
        ast.parse(src)
        return True, "AST OK"
    except Exception as e:
        return False, repr(e)

def _py_compile_script(path: Path, timeout: int = 10) -> Tuple[bool, str]:
    try:
        cp = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=timeout, check=False, text=True)
        ok = cp.returncode == 0
        return ok, (cp.stderr or cp.stdout or "py_compile ok")
    except subprocess.TimeoutExpired:
        return False, "py_compile timeout"
    except Exception as e:
        return False, repr(e)

def run_trainer_box(name: str = "Tom", color: str = "#2244ff", lifetime_sec: int = 5) -> Tuple[bool, str]:
    """Ephemeral window via python -c; no files, killable/timeboxed."""
    code = f"""
import tkinter as tk, time
root = tk.Tk()
root.title('{name} Trainer')
root.configure(bg='{color}')
root.geometry('260x160+120+120')
lab = tk.Label(root, text='{name}', bg='{color}', fg='white', font=('Segoe UI',14,'bold'))
lab.pack(expand=True, fill='both')
root.update()
t0 = time.time()
while time.time()-t0 < {lifetime_sec}:
    root.update_idletasks(); root.update(); time.sleep(0.02)
"""
    try:
        p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, err = p.communicate(timeout=lifetime_sec + 2)
        except subprocess.TimeoutExpired:
            p.kill(); return False, "timeout"
        ok = (p.returncode == 0)
        return ok, (err.decode("utf-8","replace") if not ok else "ok")
    except Exception as e:
        return False, repr(e)

def run_trainer_pair():
    """Run Tom (blue) and Jerry (purple); record trainer_metrics."""
    results = []
    for name, color in (("Tom", "#2d6cdf"), ("Jerry", "#7f3fd1")):
        ok, msg = run_trainer_box(name, color, lifetime_sec=4)
        results.append((name, ok, msg))
        try:
            with db_connect(MAIN_DB) as cx:
                cx.execute("""INSERT INTO trainer_metrics(trainer, success, summary, metrics_json, created_at)
                              VALUES(?,?,?,?,?)""",
                           (name, 1 if ok else 0, msg[:240], json.dumps({"lifetime":4}) , int(time.time())))
        except Exception as e:
            record_error("trainer_metrics", "insert failed", repr(e))
    return results

def _in_core_protected_range(a: int, b: int) -> bool:
    """Heuristic: protect early bootstrap & DB/IO heavy regions from blind mass replace."""
    # protect first ~400 lines and last ~400 lines as a coarse guard (adjust as needed)
    return a < 400 or b < 400

# Learning worker
class LearningWorker(threading.Thread):
    def __init__(self, ui: "MainWindow", interval_sec: int = 12):
        super().__init__(daemon=True)
        self.ui = ui
        self.interval = interval_sec
        self.stop_flag = threading.Event()
    def stop(self): self.stop_flag.set()
    def run(self):
        self.ui.post_console("Learning worker started.")
        while not self.stop_flag.is_set():
            try:
                scanned = 0
                for p in ROOT.rglob("*"):
                    if self.stop_flag.is_set(): break
                    if p.is_dir(): continue
                    suf = p.suffix.lower()
                    if suf in (".py",".md",".txt",".json",".yml",".yaml",".ini",".log"):
                        try:
                            if p.stat().st_size > 2_000_000:
                                continue
                        except Exception:
                            pass
                        ingest_file(p, "code" if suf==".py" else ("log" if suf==".log" else "data"))
                        scanned += 1
                rebuild_code_datasets(ROOT / SCRIPT_NAME)

                problems = []
                for a in _fn_analyses_load(ROOT / SCRIPT_NAME):
                    notes = (a.get("notes") or "")
                    if "bare except" in notes or "except body: pass" in notes or (not a.get("has_docstring")):
                        problems.append(a)
                for a in problems[:6]:
                    title = f"Refactor: {a['func_name']}@{a['start_line']} ({a['notes']})"
                    existing = {t["title"] for t in list_tasks(100)}
                    if title not in existing:
                        tid = add_task(title, f"Improve function '{a['func_name']}' lines {a['start_line']}-{a['end_line']}. Notes: {a['notes']}")
                        set_task_status(tid, "draft")
                        self.ui.post_console(f"Auto-created task: {title}")

                self.ui.post_console(f"Learning scan complete. Artifacts: ~{scanned}. Datasets rebuilt.")
            except Exception as e:
                record_error("learning_worker", "scan failed", repr(e))
                self.ui.post_console_err(f"Worker error: {e}")
            for _ in range(self.interval):
                if self.stop_flag.is_set(): break
                time.sleep(1)
        self.ui.post_console("Learning worker stopped.")

# -------------------- MainWindow --------------------

def _safe_to_text(x) -> str:
    if x is None: return ""
    if isinstance(x, str): return x
    try: return json.dumps(x, ensure_ascii=False)
    except Exception: return str(x)

def _normalize_selected_text(txt: str) -> str:
    return (txt or "").replace("\u2029", "\n")

def _slice_lines(text: str, start: int, end: int) -> str:
    lines = text.splitlines(True)
    start = max(1, start); end = max(start, end)
    return "".join(lines[start-1:end])

class MainWindow(QMainWindow):
    _singleton_ref: Optional["MainWindow"] = None

    def __init__(self, role: str = "bedrock"):
        super().__init__()
        MainWindow._singleton_ref = self

        self.theme_green = BEDROCK_GREEN if role == "bedrock" else PROJECT_GREEN

        self.setWindowTitle(f"{APP_NAME} — Bedrock" if role=="bedrock" else f"{APP_NAME} — Project")
        self.resize(1600, 980)
        self.autonomy = True
        self.last_user_or_assistant = ""
        self.last_monolog = ""
        self.tts = TTSManager()
        self.tts_voice_id: Optional[str] = self.tts.voice_id if self.tts.enabled else None

        self.bridge = UiBridge(self)
        self.bridge.consoleSig.connect(self._console)
        self.bridge.consoleErrSig.connect(self._console_error)
        self.bridge.mainLineSig.connect(self._append_user_facing_main)
        self.bridge.composeLineSig.connect(self._append_user_facing_compose)
        self.bridge.monologSig.connect(self._append_monolog)
        self.bridge.statusSig.connect(self._append_status)
        self.bridge.blinkSig.connect(self._start_blink)
        self.bridge.stopBlinkSig.connect(self._stop_blink)
        self.bridge.refreshJournalSig.connect(self.refresh_journal_list)

        self._yinyang_timer: Optional[QTimer] = None
        self._yy_busy = False
        self._yy_interval_sec = 10

        self.init_ui()
        self.load_initial_history()
        self.refresh_current_status()
        self.append_user_facing_main("system", f"{APP_NAME} ready. Primary model: {PRIMARY_MODEL} (fallback: {FALLBACK_MODEL}).")
        self.append_monolog("System boot complete. Agents idle; autonomy enabled.")

    # ---------- Thread-safe posts ----------
    def post_console(self, msg: str): self.bridge.consoleSig.emit(_safe_to_text(msg))
    def post_console_err(self, msg: str): self.bridge.consoleErrSig.emit(_safe_to_text(msg))
    def post_main_line(self, role: str, text: str): self.bridge.mainLineSig.emit(role, _safe_to_text(text))
    def post_compose_line(self, role: str, text: str): self.bridge.composeLineSig.emit(role, _safe_to_text(text))
    def post_monolog(self, text: str): self.bridge.monologSig.emit(_safe_to_text(text))
    def post_status(self, text: str): self.bridge.statusSig.emit(_safe_to_text(text))
    def post_blink(self, text: str): self.bridge.blinkSig.emit(_safe_to_text(text))
    def post_stop_blink(self): self.bridge.stopBlinkSig.emit()
    def post_refresh_journal(self): self.bridge.refreshJournalSig.emit()

    # ---- Console alias (fixes callers using self.console()) ----
    def console(self, text: str): self.post_console(text)
    def console_err(self, text: str): self.post_console_err(text)

    # ---------- UI helpers ----------
    def _dock(self, title: str, widget: QWidget, area=Qt.RightDockWidgetArea) -> QDockWidget:
        d = QDockWidget(title, self)
        d.setObjectName(title.replace(" ","_"))
        d.setWidget(widget)
        d.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.addDockWidget(area, d)
        return d

    def _style_textedit(self, te: QTextEdit):
        te.setReadOnly(True)
        te.setStyleSheet(f"""
            QTextEdit {{
                background-color: {PANEL_BG};
                color: {TEXT_FG};
                border: 1px solid #333;
                line-height: 165%;
                letter-spacing: 0.15px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 12.5px;
            }}
        """)

    def _append_html(self, te: QTextEdit, html_text: str):
        te.moveCursor(QTextCursor.End)
        te.insertHtml(html_text + "<br/><br/>")
        te.moveCursor(QTextCursor.End)

    # ---- Back-compat alias for “Automate Everything” button ----
    def on_automate_updates(self):
        """End-to-end: agents → verify → apply → checkpoint → status. Produces human chat output too."""
        try:
            self.append_user_facing_main("assistant", "Kicking off full automation…")
            # Let agents propose something right now (will also speak in chat)
            if hasattr(self, "run_agents_pipeline"):
                self.run_agents_pipeline(user_turn="(Fully Automate)", prior_answer="")
            # Safety: verify tasks (quick notes snippet), then apply queue
            if hasattr(self, "on_verify_all"):
                self.on_verify_all()
            if hasattr(self, "on_apply_queue"):
                self.on_apply_queue()
            # Optional: checkpoint + status
            if hasattr(self, "make_checkpoint"):
                self.make_checkpoint()
            if hasattr(self, "analyze_and_recommend"):
                self.analyze_and_recommend()
            self.append_user_facing_main("assistant", "Automation pass complete ✅")
            if getattr(self, "tts", None) and getattr(self, "tts_voice_id", None):
                try: self.tts.speak("Automation complete.")
                except Exception: pass
        except Exception as e:
            record_error("automate_updates", "cycle failed", repr(e))
            self.append_user_facing_main("error", f"Automate cycle error: {e}")
            self.post_console_err(f"Automate cycle error: {e}")
            self.post_blink("AUTOMATE ERROR")

    # ---- Tom & Jerry (button + /trainers) ----
    def on_run_trainers(self):
        try:
            results = run_trainer_pair()
            lines = []
            for name, ok, msg in results:
                msg_line = f"Trainer {name}: {'ok' if ok else 'fail'} — {msg}"
                self.post_console(msg_line)
                lines.append(msg_line)
            self.append_user_facing_main("assistant", "Tom & Jerry finished:\n" + "\n".join(lines))
        except Exception as e:
            record_error("trainers", "run failed", repr(e))
            self.append_user_facing_main("error", f"Trainers failed: {e}")

    # ---- Yin/Yang control ----
    def toggle_yinyang(self):
        if self._yinyang_timer and self._yinyang_timer.isActive():
            self._yinyang_timer.stop()
            self._yinyang_timer = None
            self._yy_busy = False
            self.btn_yinyang.setText("Yin/Yang: OFF")
            self.append_monolog("Yin/Yang paused.")
            self.append_user_facing_main("assistant", "Paused Yin/Yang background brainstorming.")
            return

        # start it
        try:
            self._yy_interval_sec = max(4, int(self.ed_yinyang_interval.text().strip() or "10"))
        except Exception:
            self._yy_interval_sec = 10

        self._yinyang_timer = QTimer(self)
        self._yinyang_timer.timeout.connect(self._yinyang_tick_safe)
        self._yinyang_timer.start(self._yy_interval_sec * 1000)
        self.btn_yinyang.setText("Yin/Yang: ON")
        self.append_monolog("Yin/Yang engaged.")
        self.append_user_facing_main("assistant", f"Yin/Yang engaged. I’ll propose safe notes every {self._yy_interval_sec}s.")

    def _yinyang_tick_safe(self):
        if self._yy_busy:
            return
        self._yy_busy = True
        try:
            self.yinyang_tick()
        except Exception as e:
            record_error("yinyang", "tick error", repr(e))
            msg = "Tick error: parameters are of unsupported type" if "unsupported type" in str(e) else f"Tick error: {e}"
            self.append_monolog(msg)
        finally:
            self._yy_busy = False

    def _extract_first_json(self, text: str) -> dict:
        """Extract first JSON object from mixed text/```json blocks; return {} if none."""
        try:
            m = re.search(r"```json\\s*(\\{.*?\\})\\s*```", text, flags=re.S | re.I)
            if not m:
                m = re.search(r"\\{.*\\}", text, flags=re.S)
            return json.loads(m.group(0)) if m else {}
        except Exception:
            return {}

    def yinyang_tick(self):
        """Inner debate proposes a *safe* snippet and also talks to the user with a human-style summary."""
        status = self.gather_status_snapshot()
        last_user = (self.last_user_or_assistant or "").strip()[-800:]
        monolog_hint = (self.last_monolog or "").strip()[-800:]

        sysmsg = (
            "You are FATHOM's inner duo (Yin/Yang)."
            " 1) Write ONE short, human-friendly note (<=120 words) explaining a safe improvement we can make now,"
            "    preferably a docs/NOTES update or a tiny non-destructive code comment."
            " 2) Then provide JSON with fields: {\"rationale\": str, \"note\": str}."
            " Keep it concrete and safe. If unsure, propose a NOTES.txt addition."
        )
        user = {
            "status": status,
            "last_user": last_user,
            "monolog_hint": monolog_hint,
            "instruction": "Suggest a single actionable improvement and a concise note text."
        }

        try:
            url = self.cmb_url.text().strip() or DEFAULT_OLLAMA_URL
            model = self.cmb_model.currentText().strip() or PRIMARY_MODEL
            raw = chat_once(url, model, [
                {"role": "system", "content": sysmsg},
                {"role": "user", "content": json.dumps(user)}
            ])

            data = self._extract_first_json(raw)
            human_note = ""
            if isinstance(data, dict):
                if data.get("rationale"):
                    self.append_monolog(str(data["rationale"]))
                human_note = str(data.get("note") or "").strip()

            # If model didn't fill JSON properly, fall back: use leading non-JSON text as the note
            if not human_note:
                # strip any trailing JSON block to keep just the human-ish preface
                preface = re.split(r"```json|\\{\\s*\"|\\{\\s*'", raw, maxsplit=1, flags=re.S)[0].strip()
                human_note = preface[:500].strip() or "Keeping the learning loop healthy; appended a brief NOTES update."

            # Speak to the user (human-friendly)
            self.append_user_facing_main("assistant", f"Proposed a safe improvement:\n{human_note}")

            # Convert into a NOTES.txt snippet and (optionally) apply
            sid = self._propose_notes_snippet(human_note)
            self.append_monolog("Proposed a safe snippet (NOTES.txt).")
            if self.autonomy:
                enqueue_snippet(int(sid))
                self.on_apply_queue()

        except Exception as e:
            record_error("yinyang", "chat/proposal failed", repr(e))
            self.append_monolog(f"Proposal failed: {e}")

    def _propose_notes_snippet(self, text: str) -> int:
        """Create a NOTES.txt snippet from agent output."""
        tid = add_task("Agent Note", "Append agent suggestion to NOTES.txt")
        target = DOCS_DIR / "NOTES.txt"
        content = f"\n### Agent proposal ({time.strftime('%Y-%m-%d %H:%M:%S')})\n{text}\n"
        sid = add_snippet(tid, "AGENT-NOTE", content, str(target), "append")
        set_task_status(tid, "verified")
        return sid

    # ---- Agent pipeline entry (used by chat + Automate) ----
    def run_agents_pipeline(self, user_turn: str, prior_answer: str):
        """
        Single pass: read cues → make one safe snippet → enqueue/apply if autonomy ON.
        Also narrates a brief human-facing summary in the Main Chat.
        """
        # First, generate & apply a safe note via Yin/Yang
        self.yinyang_tick()

        # Then offer a compact status blurb for the user
        try:
            snap = self.gather_status_snapshot()
            url = self.cmb_url.text().strip() or DEFAULT_OLLAMA_URL
            model = self.cmb_model.currentText().strip() or PRIMARY_MODEL
            sysmsg = ("Be concise and human. Summarize what I just did in one or two sentences maximum.")
            raw = chat_once(url, model, [
                {"role": "system", "content": sysmsg},
                {"role": "user", "content": json.dumps({"recent_action": "Yin/Yang safe note + queue/apply", "snapshot": snap})}
            ])
            summary = (raw or "").strip()
            # Trim off any accidental JSON; keep it conversational
            summary = re.split(r"```json|\\{\\s*\"|\\{\\s*'", summary, maxsplit=1, flags=re.S)[0].strip()
            if summary:
                self.append_user_facing_main("assistant", summary[:600])
        except Exception:
            pass

    # ===== Apply queue / Auto-implement (hardened) =====
    def on_apply_queue(self):
        applied = 0; failed = 0
        while True:
            sn = dequeue_next()
            if not sn:
                break
            try:
                ok = apply_snippet(sn)
                applied += int(bool(ok))
                failed += int(not ok)
            except Exception as e:
                record_error("apply_queue", "apply failed", repr(e))
                failed += 1
        self.post_console(f"Apply queue complete. ok={applied} fail={failed}")
        if failed:
            self.post_blink("APPLY FAILED")
        self.refresh_journal_list()

    def on_auto_implement(self):
        """Enqueue all collected snippets and apply them."""
        try:
            for sn in list_snippets(2000):
                enqueue_snippet(int(sn["id"]))
            self.on_apply_queue()
            self.append_user_facing_main("assistant", "Queued all snippets and applied the queue.")
        except Exception as e:
            record_error("auto_impl", "failed", repr(e))
            self.append_user_facing_main("error", f"Auto implement failed: {e}")


    # ---------- UI layout helpers (unchanged) ----------
    def _tag(self, label: str, color: str) -> str:
        return f"""<span style="background:{color}22;color:{color};padding:2px 6px;border-radius:4px;border:1px solid {color}55;font-weight:600;">{label}</span>"""

    def _line(self, prefix_label: str, color_hex: str, text: str) -> str:
        import html
        tag = self._tag(prefix_label, color_hex)
        safe = html.escape(_safe_to_text(text))
        return f"""<div style="margin:4px 0">{tag}&nbsp;<span style="color:{TEXT_FG}">{safe}</span></div>"""

    def _impl_button_style(self) -> str:
        return f"""
        QPushButton {{
            background-color: {ORANGE_IMPL};
            color: #222;
            border: 1px solid #8a6f00;
            padding: 6px 10px;
            font-weight: 700;
        }}
        QPushButton:disabled {{
            background-color: #5f5a3a;
            color: #333;
            border: 1px solid #444;
        }}
        """

    def _normal_button_style(self) -> str:
        return f"""
        QPushButton {{
            background-color: #333;
            color: {TEXT_FG};
            border: 1px solid #555;
            padding: 6px 10px;
        }}
        QPushButton:hover {{
            background-color: #3a3a3a;
        }}
        """

    # ---------- UI layout ----------
    def init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(6,6,6,6); root.setSpacing(6)

        # Top bar
        top = QHBoxLayout()
        self.cmb_model = QComboBox(); self.cmb_model.addItems([PRIMARY_MODEL, FALLBACK_MODEL])
        self.cmb_url = QLineEdit(DEFAULT_OLLAMA_URL); self.cmb_url.setMinimumWidth(240)
        self.btn_ping = QPushButton("Ping Ollama"); self.btn_ping.setStyleSheet(self._normal_button_style())
        self.chk_autonomy = QCheckBox("Autonomy ON"); self.chk_autonomy.setChecked(True)
        self.btn_run_agents = QPushButton("Run Agents Now"); self.btn_run_agents.setStyleSheet(self._normal_button_style())
        self.btn_yinyang = QPushButton("Yin/Yang: OFF"); self.btn_yinyang.setStyleSheet(self._normal_button_style())
        self.ed_yinyang_interval = QLineEdit("10"); self.ed_yinyang_interval.setFixedWidth(50)
        self.lbl_attention = QLabel("• ATTENTION REQUIRED •")
        self.lbl_attention.setStyleSheet("color:#ffd166; font-weight:800;")
        self.lbl_attention.setVisible(False)

        top.addWidget(QLabel("Model:")); top.addWidget(self.cmb_model)
        top.addSpacing(10); top.addWidget(QLabel("URL:")); top.addWidget(self.cmb_url)
        top.addSpacing(10); top.addWidget(self.btn_ping)
        top.addSpacing(10); top.addWidget(self.chk_autonomy)
        top.addSpacing(10); top.addWidget(self.btn_run_agents)
        top.addSpacing(18); top.addWidget(self.btn_yinyang)
        top.addWidget(QLabel("YY interval (s):")); top.addWidget(self.ed_yinyang_interval)
        top.addSpacing(20); top.addWidget(self.lbl_attention)
        root.addLayout(top)

        # Split main area
        main_split = QSplitter(Qt.Horizontal)
        root.addWidget(main_split, 1)

        # ===== Left column: Chat/Compose/TTS =====
        left = QSplitter(Qt.Vertical)

        # Main chat lane
        main_lane = QWidget(); ml = QVBoxLayout(main_lane); ml.setContentsMargins(0,0,0,0); ml.setSpacing(6)
        self.chat_view = QTextEdit(); self._style_textedit(self.chat_view)
        self.chat_view.setMinimumHeight(240)
        ml.addWidget(QLabel("Main Chat (talk to FATHOM)"))
        ml.addWidget(self.chat_view, 1)
        row_main = QHBoxLayout()
        self.chat_input = QLineEdit(); self.chat_input.setPlaceholderText("Talk to Fathom… (/help, /status, /evolve_launch, /datasets_refresh, /code_map, /code_show 100-160, /code_analyze func, /verify_all, /apply_queue, /commit_main)")
        self.btn_send = QPushButton("Send"); self.btn_send.setStyleSheet(self._normal_button_style())
        self.btn_automate = QPushButton("Automate Everything"); self.btn_automate.setStyleSheet(self._impl_button_style())
        row_main.addWidget(self.chat_input, 1); row_main.addWidget(self.btn_send); row_main.addWidget(self.btn_automate)
        ml.addLayout(row_main)

        # Compose lane
        compose_lane = QWidget(); cl = QVBoxLayout(compose_lane); cl.setContentsMargins(0,0,0,0); cl.setSpacing(6)
        self.compose_view = QTextEdit(); self._style_textedit(self.compose_view)
        self.compose_view.setMinimumHeight(200)
        cl.addWidget(QLabel("Task Composer (curate → Create Task Sheet)"))
        cl.addWidget(self.compose_view, 1)
        row_comp = QHBoxLayout()
        self.compose_input = QLineEdit(); self.compose_input.setPlaceholderText("Notes for the task sheet…")
        self.btn_compose_add = QPushButton("Add to Draft"); self.btn_compose_add.setStyleSheet(self._normal_button_style())
        self.btn_compose_create = QPushButton("Create Task Sheet → Verify"); self.btn_compose_create.setStyleSheet(self._impl_button_style())
        row_comp.addWidget(self.compose_input, 1); row_comp.addWidget(self.btn_compose_add); row_comp.addWidget(self.btn_compose_create)
        cl.addLayout(row_comp)

        # TTS controls
        tts_lane = QWidget(); tl = QHBoxLayout(tts_lane); tl.setContentsMargins(0,0,0,0); tl.setSpacing(8)
        self.btn_tts_start = QPushButton("Start Reading"); self.btn_tts_start.setStyleSheet(self._normal_button_style())
        self.btn_tts_stop = QPushButton("Stop Reading"); self.btn_tts_stop.setStyleSheet(self._normal_button_style())
        self.btn_tts_play_current = QPushButton("Play Current (Main→Monolog)"); self.btn_tts_play_current.setStyleSheet(self._normal_button_style())
        self.btn_tts_read_sel = QPushButton("Read Selection"); self.btn_tts_read_sel.setStyleSheet(self._normal_button_style())
        tl.addWidget(QLabel(f"TTS: {'on' if self.tts.enabled else 'off'}"))
        tl.addWidget(self.btn_tts_start)
        tl.addWidget(self.btn_tts_play_current)
        tl.addWidget(self.btn_tts_read_sel)
        tl.addWidget(self.btn_tts_stop)

        left.addWidget(main_lane)
        left.addWidget(compose_lane)
        left.addWidget(tts_lane)
        main_split.addWidget(left)

        # ===== Right column: docks =====
        right = QSplitter(Qt.Vertical)

        self.tasks_list = QListWidget()
        dock_tasks = self._dock("Tasks", self.tasks_list, Qt.LeftDockWidgetArea); right.addWidget(dock_tasks)
        task_controls = QWidget(); tcl = QHBoxLayout(task_controls); tcl.setContentsMargins(6,6,6,6); tcl.setSpacing(6)
        self.btn_verify_selected = QPushButton("Verify → Snippets"); self.btn_verify_selected.setStyleSheet(self._impl_button_style())
        self.btn_verify_all = QPushButton("Verify All"); self.btn_verify_all.setStyleSheet(self._impl_button_style())
        tcl.addWidget(self.btn_verify_selected); tcl.addWidget(self.btn_verify_all)
        dock_tasks.setTitleBarWidget(task_controls)

        self.snippets_list = QListWidget()
        dock_snips = self._dock("Snippets", self.snippets_list, Qt.LeftDockWidgetArea); right.addWidget(dock_snips)
        sn_controls = QWidget(); snl = QHBoxLayout(sn_controls); snl.setContentsMargins(6,6,6,6); snl.setSpacing(6)
        self.btn_implement_selected = QPushButton("Implement Selected"); self.btn_implement_selected.setStyleSheet(self._impl_button_style())
        self.btn_apply_queue = QPushButton("Apply Queue"); self.btn_apply_queue.setStyleSheet(self._impl_button_style())
        self.btn_auto_implement = QPushButton("Auto Implement (All)"); self.btn_auto_implement.setStyleSheet(self._impl_button_style())
        self.btn_trainers = QPushButton("Run Trainers (Tom/Jerry)"); self.btn_trainers.setStyleSheet(self._impl_button_style())
        snl.addWidget(self.btn_implement_selected); snl.addWidget(self.btn_apply_queue); snl.addWidget(self.btn_auto_implement); snl.addWidget(self.btn_trainers)
        dock_snips.setTitleBarWidget(sn_controls)

        self.journal_list = QListWidget()
        dock_journal = self._dock("Change Journal", self.journal_list, Qt.LeftDockWidgetArea); right.addWidget(dock_journal)
        self.diff_view = QPlainTextEdit(); self.diff_view.setReadOnly(True)
        self.diff_view.setStyleSheet(f"QPlainTextEdit {{ background-color: {PANEL_BG}; color: {TEXT_FG}; border: 1px solid #333; }}")
        dock_diff = self._dock("Diff Viewer", self.diff_view, Qt.RightDockWidgetArea); right.addWidget(dock_diff)

        self.console_view = QTextEdit(); self._style_textedit(self.console_view)
        dock_console = self._dock("System Console", self.console_view, Qt.BottomDockWidgetArea); right.addWidget(dock_console)

        flw = QWidget(); fll = QVBoxLayout(flw); fll.setContentsMargins(6,6,6,6); fll.setSpacing(6)
        self.btn_open_script = QPushButton(f"Open {SCRIPT_NAME}"); self.btn_open_script.setStyleSheet(self._normal_button_style())
        self.btn_open_logs = QPushButton("Open events.log"); self.btn_open_logs.setStyleSheet(self._normal_button_style())
        self.files_view = QTextEdit(); self._style_textedit(self.files_view)
        rowF = QHBoxLayout(); rowF.addWidget(self.btn_open_script); rowF.addWidget(self.btn_open_logs)
        fll.addLayout(rowF); fll.addWidget(self.files_view,1)
        dock_files = self._dock("Files/Logs", flw, Qt.RightDockWidgetArea); right.addWidget(dock_files)

        self.status_overview = QTextEdit(); self._style_textedit(self.status_overview)
        sw = QWidget(); swl = QVBoxLayout(sw); swl.setContentsMargins(6,6,6,6); swl.setSpacing(6)
        self.btn_status_refresh = QPushButton("Refresh"); self.btn_status_refresh.setStyleSheet(self._normal_button_style())
        self.btn_status_analyze = QPushButton("Analyze & Recommend (/status)"); self.btn_status_analyze.setStyleSheet(self._impl_button_style())
        rowS = QHBoxLayout(); rowS.addWidget(self.btn_status_refresh); rowS.addWidget(self.btn_status_analyze)
        swl.addLayout(rowS); swl.addWidget(self.status_overview, 1)
        dock_status = self._dock("Current Status (User-facing)", sw, Qt.BottomDockWidgetArea); right.addWidget(dock_status)

        self.monolog_view = QTextEdit(); self._style_textedit(self.monolog_view)
        dock_monolog = self._dock("Inner Monolog (Agents)", self.monolog_view, Qt.BottomDockWidgetArea); right.addWidget(dock_monolog)

        edw = QWidget(); edl = QVBoxLayout(edw); edl.setContentsMargins(6,6,6,6); edl.setSpacing(6)
        self.editor = CodeEditor()
        ed_controls = QHBoxLayout()
        self.btn_editor_open = QPushButton("Load file…"); self.btn_editor_open.setStyleSheet(self._normal_button_style())
        self.btn_editor_save = QPushButton("Save"); self.btn_editor_save.setStyleSheet(self._normal_button_style())
        self.btn_editor_goto = QPushButton("Go to line…"); self.btn_editor_goto.setStyleSheet(self._normal_button_style())
        ed_controls.addWidget(self.btn_editor_open); ed_controls.addWidget(self.btn_editor_save); ed_controls.addWidget(self.btn_editor_goto)
        edl.addLayout(ed_controls); edl.addWidget(self.editor, 1)
        dock_editor = self._dock("Code Editor", edw, Qt.LeftDockWidgetArea); right.addWidget(dock_editor)

        main_split.addWidget(right)
        main_split.setStretchFactor(0, 3)
        main_split.setStretchFactor(1, 2)

        # Action row
        action_row = QHBoxLayout()
        self.btn_analyze = QPushButton("Analyze (/status)"); self.btn_analyze.setStyleSheet(self._normal_button_style())
        self.btn_walk = QPushButton("Walk Files → Ingest"); self.btn_walk.setStyleSheet(self._normal_button_style())
        self.btn_checkpoint = QPushButton("Checkpoint Now (/commit_main)"); self.btn_checkpoint.setStyleSheet(self._normal_button_style())
        self.btn_auto_chain = QPushButton("Auto Verify & Apply"); self.btn_auto_chain.setStyleSheet(self._impl_button_style())
        self.btn_evolve = QPushButton("Evolve Launch"); self.btn_evolve.setStyleSheet(self._impl_button_style())
        action_row.addWidget(self.btn_analyze); action_row.addWidget(self.btn_walk); action_row.addWidget(self.btn_checkpoint)
        action_row.addWidget(self.btn_auto_chain); action_row.addWidget(self.btn_evolve)
        root.addLayout(action_row)

        # Bindings
        self.btn_ping.clicked.connect(self.ping_ollama)
        self.btn_send.clicked.connect(self.on_send_main)
        self.chat_input.returnPressed.connect(self.on_send_main)
        self.btn_automate.clicked.connect(self.on_automate_updates)

        self.btn_compose_add.clicked.connect(self.on_compose_add)
        self.btn_compose_create.clicked.connect(self.on_compose_create)
        self.compose_input.returnPressed.connect(self.on_compose_add)

        self.btn_verify_selected.clicked.connect(self.on_verify_selected)
        self.btn_verify_all.clicked.connect(self.on_verify_all)
        self.btn_implement_selected.clicked.connect(self.on_implement_selected)
        self.btn_apply_queue.clicked.connect(self.on_apply_queue)
        self.btn_auto_implement.clicked.connect(self.on_auto_implement)
        self.btn_trainers.clicked.connect(self.on_run_trainers)

        self.btn_analyze.clicked.connect(self.analyze_and_recommend)
        self.btn_walk.clicked.connect(self.deploy_agent_walk_files)
        self.btn_open_script.clicked.connect(self.open_script)
        self.btn_open_logs.clicked.connect(self.open_logs)
        self.btn_status_refresh.clicked.connect(self.refresh_current_status)
        self.btn_status_analyze.clicked.connect(self.on_status_clicked)
        self.chk_autonomy.stateChanged.connect(self.on_toggle_autonomy)
        self.btn_run_agents.clicked.connect(self.on_run_agents_clicked)
        self.btn_checkpoint.clicked.connect(self.make_checkpoint)
        self.btn_auto_chain.clicked.connect(self.on_auto_chain)
        self.btn_evolve.clicked.connect(self.on_evolve_launch_clicked)

        self.btn_tts_start.clicked.connect(self.on_tts_start)
        self.btn_tts_stop.clicked.connect(self.on_tts_stop)
        self.btn_tts_play_current.clicked.connect(self.on_tts_play_current)
        self.btn_tts_read_sel.clicked.connect(self.on_tts_read_selection)

        self.btn_editor_open.clicked.connect(self.on_editor_open)
        self.btn_editor_save.clicked.connect(self.on_editor_save)
        self.btn_editor_goto.clicked.connect(self.on_editor_goto)

        self.btn_yinyang.clicked.connect(self.toggle_yinyang)

        self.setStyleSheet(
            f"QMainWindow {{ background-color: {DARK_BG}; color: {TEXT_FG}; }}"
            f"QLabel {{ color: {TEXT_FG}; }} "
            f"QDockWidget::title {{ background: {self.theme_green}; color: #fff; padding: 4px; }}"
        )

        self.refresh_journal_list()

        try:
            code = (ROOT / SCRIPT_NAME).read_text(encoding="utf-8", errors="replace")
            self.editor.setPlainText(code)
        except Exception as e:
            record_error("editor_init", "load script failed", repr(e))


    # ---------- System Console helpers ----------
    def _console(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        self._append_html(self.console_view, self._line("Console", self.theme_green, f"[{ts}] {msg}"))

    def _console_error(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        self._append_html(self.console_view, self._line("Console", ERROR_RED, f"[{ts}] {msg}"))

    def _start_blink(self, text="ATTENTION REQUIRED"):
        self.lbl_attention.setText(f"• {text} •")
        self.lbl_attention.setVisible(True)
        if not hasattr(self, "_blink_timer"):
            self._blink_timer = QTimer(self)
            self._blink_on = True
            def _tick():
                self._blink_on = not self._blink_on
                self.lbl_attention.setStyleSheet("color:#ffd166; font-weight:800;" if self._blink_on else "color:#5f5138; font-weight:800;")
            self._blink_timer.timeout.connect(_tick)
            self._blink_timer.start(450)

    def _stop_blink(self):
        self.lbl_attention.setVisible(False)
        if hasattr(self, "_blink_timer"):
            self._blink_timer.stop()
            del self._blink_timer

    def require_human(self, message: str):
        self.append_user_facing_main("system", f"[INTERVENTION] {message}")
        self.console(f"[INTERVENTION] {message}")
        self._start_blink("INTERVENTION")

    def announce(self, text: str):
        self.append_user_facing_main("assistant", text)
        self.console(text)

    # ---------- History ----------
    def load_initial_history(self):
        msgs = get_conversation("main", 200)
        for m in msgs:
            role = m["role"]; content = m["content"]
            self._append_line(self.chat_view, role, content, pushed=bool(m.get("pushed",0)))
        msgs2 = get_conversation("compose", 80)
        for m in msgs2:
            role = m["role"]; content = m["content"]
            self._append_line(self.compose_view, role, content)
        msgs3 = get_conversation("monolog", 120)
        for m in msgs3:
            self._append_line(self.monolog_view, "agent", m["content"])

    # ---------- UI appenders ----------
    def _append_line(self, te: QTextEdit, role: str, text: str, pushed: bool=False):
        label = role.capitalize() if role not in ("assistant","agent") else ("Fathom" if role=="assistant" else "Agent")
        tag_color = {
            "user": LINK_BLUE,
            "assistant": self.theme_green,
            "system": "#6aaaff",
            "error": ERROR_RED,
            "agent": AGENT_PURPLE,
        }.get(role, TEXT_FG)
        seg = self._line(label + (" (Automated)" if pushed else ""), tag_color, text)
        self._append_html(te, seg)

    def _append_user_facing_main(self, role: str, text: str):
        self._append_line(self.chat_view, role, text)
        if role in ("user","assistant","system","error"):
            self.last_user_or_assistant = _safe_to_text(text)

    def _append_user_facing_compose(self, role: str, text: str):
        self._append_line(self.compose_view, role, text)

    def _append_monolog(self, text: str):
        self._append_line(self.monolog_view, "agent", text)
        self.last_monolog = _safe_to_text(text)
        add_conversation("monolog", "agent", _safe_to_text(text))  # store in monolog lane only

    def _append_status(self, text: str):
        self.status_overview.clear()
        html_line = self._line("Status", "#6aaaff", text)
        self._append_html(self.status_overview, html_line)

    # Public wrappers
    def append_user_facing_main(self, role: str, text: str): self._append_user_facing_main(role, text)
    def append_user_facing_compose(self, role: str, text: str): self._append_user_facing_compose(role, text)
    def append_monolog(self, text: str): self._append_monolog(text)
    def append_status(self, text: str): self._append_status(text)

    # ---------- Buttons / Actions ----------
    def on_toggle_autonomy(self, state: int):
        self.autonomy = bool(state)
        self.append_user_facing_main("system", f"Autonomy {'enabled' if self.autonomy else 'disabled'}.")

    def ping_ollama(self):
        url = self.cmb_url.text().strip() or DEFAULT_OLLAMA_URL
        ok = ollama_reachable(url)
        QMessageBox.information(self, "Ollama", "Reachable ✅" if ok else "Not reachable ❌")

    def _rebuild_readme(self):
        try:
            code = (ROOT / SCRIPT_NAME).read_text(encoding="utf-8", errors="replace")
            readme_set("fathom.py", build_machine_readme(code))
        except Exception as e:
            record_error("readme_update", "failed to rebuild README", repr(e))

    # ===== Main chat lane
    def on_send_main(self):
        s = self.chat_input.text().strip()
        if not s: return
        self.chat_input.clear()
        self.append_user_facing_main("user", s)
        add_conversation("main", "user", s)

        if self.handle_command(s, lane="main"):
            return

        self._rebuild_readme()

        readme_ctx = readme_topical_snapshot("chat", 2500)
        diffqa_ctx = diffqa_search(s, 1200)
        snap = self.gather_status_snapshot()

        cm = _code_mirror_load(ROOT / SCRIPT_NAME)
        line_count = int(cm.get("line_count") or 0)
        chunk_hint = f"CODE_MIRROR available: {SCRIPT_NAME} lines 1..{line_count}. Use /code_show A-B to fetch exact lines."

        sem = {"hints": ["datasets=ready", "fn_analyses=ready"]}

        url = self.cmb_url.text().strip() or DEFAULT_OLLAMA_URL
        model = self.cmb_model.currentText().strip() or PRIMARY_MODEL

        sysmsg = (
            "You are FATHOM, the system’s own voice. Always answer tersely and act like an IDE copilot. "
            "If asked about code, request exact line ranges or function names to limit context. "
            "Return JSON with fields: {\"rationale\":..., \"actions\":[...], \"answer\":...}"
        )
        usr = (
            f"README:\n{readme_ctx}\n\n"
            f"RECENT DIFF-QA:\n{diffqa_ctx}\n\n"
            f"SNAPSHOT(JSON):\n{json.dumps(snap)[:MAX_SNAPSHOT_JSON_CHARS]}\n\n"
            f"{chunk_hint}\n\n"
            f"SEMANTICS:\n{json.dumps(sem)}\n\n"
            f"USER:\n{s}\n"
            "Return JSON only."
        )

        try:
            raw = chat_once(url, model, [{"role":"system","content": sysmsg}, {"role":"user","content": usr}])
            m = re.search(r"\{.*\}", raw, flags=re.S)
            data = json.loads(m.group(0)) if m else {"rationale": raw[:400], "actions": [], "answer": "(no JSON)"}
        except Exception as e:
            record_error("chat", "llm failed", repr(e))
            data = {"rationale": f"LLM error: {e}", "actions": [], "answer": "(LLM failed)"}

        if data.get("rationale"):
            self.append_monolog(data["rationale"])
        for a in (data.get("actions") or []):
            self.append_user_facing_main("assistant", f"[action] {a}")

        answer = data.get("answer") or "(no answer)"
        self.append_user_facing_main("assistant", answer)
        add_conversation("main", "assistant", answer)

        if len(s) < 800 and 10 < len(answer) < 6000:
            diffqa_add(s, answer, tags="chat")

        if self.autonomy:
            self.run_agents_pipeline(user_turn=s, prior_answer=answer)

        self.refresh_current_status(user_hint="Updated after your message.")


    # ===== Compose lane
    def on_compose_add(self):
        t = self.compose_input.text().strip()
        if not t: return
        self.compose_input.clear()
        self.append_user_facing_compose("user", t)
        add_conversation("compose", "user", t)

    def on_compose_create(self):
        msgs = get_conversation("compose", 200)
        if not msgs:
            QMessageBox.information(self, "Task Composer", "No draft notes to create a task sheet.")
            return
        title = "User-curated Task Sheet"
        body_lines = []
        for m in msgs:
            body_lines.append(f"{m['role'].upper()}: {m['content']}")
        body = "\n".join(body_lines[:400])
        tid = add_task(title, body)
        set_task_status(tid, "draft")
        self.load_tasks()
        self.append_user_facing_main("assistant", f"Created task #{tid} from Task Composer draft. Use /verify_selected then /apply_queue.")
        self._verify_task_id(tid, auto_enq=True)

    # ===== Commands
    def handle_command(self, s: str, lane: str) -> bool:
        def say(text: str):
            (self.append_user_facing_main if lane=="main" else self.append_user_facing_compose)("assistant", text)

        if s == "/help":
            msg = ("Commands: /help, /status, /evolve_launch, /datasets_refresh, /code_map, /code_show A-B, /code_analyze <func>, "
                   "/code_insert <line> <<...>>, /code_replace <start>-<end> <<...>>, "
                   "/deploy_agent_walk-files, /self_heal, /verify_selected, /verify_all, "
                   "/implement [id?], /auto_implement, /apply_queue, /compose_to_tasks, /commit_main, "
                   "/trainers, /autonomy on|off, /tts voice <name>, /tts readsel")
            say(msg); return True

        if s in ("/status", "/analyze"):
            self.analyze_and_recommend(); return True

        if s == "/evolve_launch":
            self.evolve_launch(); return True

        if s == "/datasets_refresh":
            try:
                rebuild_code_datasets(ROOT / SCRIPT_NAME)
                say("Datasets refreshed (Code Mirror + Function Analyses + Snapshots).")
            except Exception as e:
                record_error("datasets_refresh", "failed", repr(e))
                say(f"Refresh failed: {e}")
            return True

        if s == "/code_map":
            cm = _code_mirror_load(ROOT / SCRIPT_NAME)
            if not cm:
                say("No Code Mirror found. Run /datasets_refresh.")
                return True
            analyses = _fn_analyses_load(ROOT / SCRIPT_NAME)
            lines = [f"{SCRIPT_NAME}: 1..{cm.get('line_count',0)}"]
            for a in analyses[:200]:
                lines.append(f"- {a['func_name']}  [{a['start_line']}-{a['end_line']}]  notes: {a['notes']}")
            say("\n".join(lines[:400]))
            return True

        if s.startswith("/code_show "):
            rng = s.split("/code_show ",1)[1].strip()
            m = re.match(r"(\d+)\s*-\s*(\d+)$", rng)
            if not m:
                say("Usage: /code_show A-B"); return True
            a, b = int(m.group(1)), int(m.group(2))
            code = (ROOT / SCRIPT_NAME).read_text(encoding="utf-8", errors="replace")
            say(f"```python\n{_slice_lines(code, a, b)}\n```")
            return True

        if s.startswith("/code_analyze "):
            name = s.split("/code_analyze ",1)[1].strip()
            found = [a for a in _fn_analyses_load(ROOT / SCRIPT_NAME) if a["func_name"] == name]
            if not found:
                say(f"No analysis for function: {name}"); return True
            a = found[0]
            info = {
                "func": a["func_name"],
                "lines": f"{a['start_line']}-{a['end_line']}",
                "params": a["params"],
                "returns": a["returns"],
                "raises": a["raises"],
                "side_effects": a["side_effects"],
                "has_docstring": bool(a["has_docstring"]),
                "notes": a["notes"],
            }
            say(json.dumps(info, indent=2))
            return True

        if s.startswith("/code_insert "):
            m = re.match(r"/code_insert\s+(\d+)\s+<<(.+?)>>\s*$", s, flags=re.S)
            if not m:
                say("Usage: /code_insert <line> <<code...>>"); return True
            line = int(m.group(1)); content = m.group(2)
            tid = add_task("Insert code", f"Insert at line {line}")
            sid = add_snippet(tid, f"Insert@{line}", content, str(ROOT / SCRIPT_NAME), "insert_at_line", start_line=line)
            enqueue_snippet(sid)
            set_task_status(tid, "verified")
            self.load_tasks(); self.load_snippets()
            say(f"Queued insert at line {line}. Snippet #{sid}."); return True

        if s.startswith("/code_replace "):
            m = re.match(r"/code_replace\s+(\d+)\s*-\s*(\d+)\s+<<(.+?)>>\s*$", s, flags=re.S)
            if not m:
                say("Usage: /code_replace <start>-<end> <<code...>>"); return True
            a, b, content = int(m.group(1)), int(m.group(2)), m.group(3)
            # protect core if huge region
            if _in_core_protected_range(a, b):
                say("Protected region; proposal queued but not auto-applied.")
            tid = add_task("Replace code", f"Replace {a}-{b}")
            sid = add_snippet(tid, f"Replace@{a}-{b}", content, str(ROOT / SCRIPT_NAME), "replace_range", start_line=a, end_line=b)
            enqueue_snippet(sid)
            set_task_status(tid, "verified")
            self.load_tasks(); self.load_snippets()
            say(f"Queued replace {a}-{b}. Snippet #{sid}."); return True

        if s == "/deploy_agent_walk-files":
            self.deploy_agent_walk_files(); return True
        if s == "/self_heal":
            self.self_heal(); return True
        if s == "/verify_selected":
            self.on_verify_selected(); return True
        if s == "/verify_all":
            self.on_verify_all(); return True
        if s.startswith("/implement"):
            parts = s.split()
            if len(parts) > 1 and parts[1].isdigit():
                self.on_implement_snippet_id(int(parts[1]))
            else:
                self.on_implement_selected()
            return True
        if s == "/auto_implement":
            self.on_auto_implement(); return True
        if s == "/apply_queue":
            self.on_apply_queue(); return True
        if s == "/compose_to_tasks":
            self.on_compose_create(); return True
        if s == "/commit_main":
            self.make_checkpoint(); return True
        if s == "/trainers":
            self.on_run_trainers(); return True
        if s.startswith("/autonomy"):
            if "on" in s.lower():
                self.chk_autonomy.setChecked(True); self.on_toggle_autonomy(1)
            else:
                self.chk_autonomy.setChecked(False); self.on_toggle_autonomy(0)
            return True
        if s.startswith("/tts voice "):
            name = s.split("/tts voice ",1)[1].strip()
            ok = self.tts.set_voice(name)
            say(f"TTS voice {'set' if ok else 'not changed'}."); return True
        if s == "/tts readsel":
            self.on_tts_read_selection(); return True
        return False

    # ===== Verify selected/all tasks
    def _verify_task_id(self, tid: int, auto_enq: bool = True):
        tasks = {t["id"]:t for t in list_tasks(9999)}
        t = tasks.get(tid)
        if not t:
            QMessageBox.warning(self, "Verify", f"Task #{tid} not found."); return
        # safe note append; real edits come from explicit commands or agents
        target = DOCS_DIR / "NOTES.txt"
        snippet = {
            "label": f"TASK-{tid}",
            "content": f"# Task #{tid}: {t['title']}\n{t['body']}\n",
            "target_path": str(target),
            "apply_mode": "append"
        }
        sid = add_snippet(t["id"], snippet["label"], snippet["content"], snippet["target_path"], snippet["apply_mode"])
        if auto_enq: enqueue_snippet(sid)
        set_task_status(t["id"], "verified")
        self.load_snippets(); self.load_tasks()
        self.announce(f"Verified task #{tid} → 1 snippet queued.")

    def on_verify_selected(self):
        item = self.tasks_list.currentItem()
        if not item:
            QMessageBox.information(self, "Verify", "Select a task to verify.")
            return
        txt = item.text()
        m = re.search(r"#(\d+)", txt)
        if not m:
            QMessageBox.information(self, "Verify", "Couldn’t parse a task id from the selection.")
            return
        tid = int(m.group(1))
        self._verify_task_id(tid, auto_enq=True)

    def on_verify_all(self):
        tasks = list_tasks(9999)
        if not tasks:
            QMessageBox.information(self, "Verify", "No tasks to verify.")
            return
        for t in tasks:
            if (t.get("status") or "") not in ("verified", "done"):
                self._verify_task_id(int(t["id"]), auto_enq=True)
        self.append_user_facing_main("assistant", "All tasks verified → snippets queued.")
        self.load_snippets()

    # ===== Snippets / Apply =====
    def load_tasks(self):
        self.tasks_list.clear()
        for t in list_tasks(1000):
            status = t.get("status") or "new"
            self.tasks_list.addItem(f"[{status}] {t['title']}  #{t['id']}")

    def load_snippets(self):
        self.snippets_list.clear()
        for sn in list_snippets(1000):
            label = sn.get("label") or "snippet"
            path = sn.get("target_path") or "?"
            self.snippets_list.addItem(f"{label} → {Path(path).name}  #{sn['id']}")

    def on_implement_selected(self):
        items = self.snippets_list.selectedItems()
        if not items:
            QMessageBox.information(self, "Implement", "Select one or more snippets first.")
            return
        for it in items:
            m = re.search(r"#(\d+)", it.text())
            if not m: continue
            sid = int(m.group(1))
            self.on_implement_snippet_id(sid)

    def on_implement_snippet_id(self, sid: int):
        try:
            all_sn = {s["id"]: s for s in list_snippets(2000)}
            sn = all_sn.get(int(sid))
            if not sn:
                self.post_console_err(f"Snippet #{sid} not found.")
                return
            ok = apply_snippet(sn)
            if ok:
                self.post_console(f"Applied snippet #{sid} → {sn['target_path']}")
            else:
                self.post_console_err(f"Apply failed for snippet #{sid}")
        except Exception as e:
            record_error("implement_snippet", f"#{sid}", repr(e))
        self.refresh_journal_list()

    def on_apply_queue(self):
        applied = 0; failed = 0
        while True:
            sn = dequeue_next()
            if not sn: break
            ok = apply_snippet(sn)
            applied += 1 if ok else 0
            failed  += 0 if ok else 1
        self.append_user_facing_main("assistant", f"Queue done. Applied: {applied}, Failed: {failed}.")
        self.refresh_journal_list(); self.load_snippets()

    def on_auto_implement(self):
        # Enqueue everything then apply queue
        for sn in list_snippets(2000):
            enqueue_snippet(int(sn["id"]))
        self.on_apply_queue()

    # ===== Checkpoint / Git-lite =====
    def make_checkpoint(self):
        try:
            nowtag = bump_semver("patch", "manual checkpoint")
            # back up the main script
            make_backup(ROOT / SCRIPT_NAME)
            # write a lightweight tag file
            tagfile = DOCS_DIR / f"CHECKPOINT_{nowtag}.txt"
            tagfile.write_text(time.strftime("%Y-%m-%d %H:%M:%S"), encoding="utf-8")
            self.append_user_facing_main("assistant", f"Checkpoint created: v{nowtag}")
            self.post_console(f"Checkpoint v{nowtag} written → {tagfile}")
        except Exception as e:
            record_error("checkpoint", "failed", repr(e))
            self.append_user_facing_main("error", f"Checkpoint failed: {e}")

    # ===== Status / Analysis =====
    def gather_status_snapshot(self) -> Dict[str, Any]:
        try:
            semver = current_semver()
            msgs = len(get_conversation("main", 99999))
            snips = list_snippets(9999)
            tasks = list_tasks(9999)
            with db_connect(MAIN_DB) as cx:
                errs = cx.execute("SELECT COUNT(1) AS c FROM errors").fetchone()["c"]
                qlen = cx.execute("SELECT COUNT(1) AS c FROM queue").fetchone()["c"]
                last5 = cx.execute("SELECT * FROM patch_journal ORDER BY id DESC LIMIT 5").fetchall()
            recent = [{
                "file": r["file_path"],
                "ok": bool(r["ok"]),
                "adds": r["lines_added"],
                "rems": r["lines_removed"]
            } for r in last5]
            return {
                "semver": semver,
                "messages": msgs,
                "tasks": len(tasks),
                "snippets": len(snips),
                "queue": qlen,
                "errors": errs,
                "recent_journal": recent
            }
        except Exception as e:
            record_error("snapshot", "failed", repr(e))
            return {"error": str(e)}

    def refresh_current_status(self, user_hint: str = ""):
        snap = self.gather_status_snapshot()
        txt = f"v{snap.get('semver','?')} • tasks={snap.get('tasks',0)} • snippets={snap.get('snippets',0)} • queue={snap.get('queue',0)} • errors={snap.get('errors',0)}"
        if user_hint:
            txt += f"\n\nNote: {user_hint}"
        self.append_status(txt)
        self.load_tasks(); self.load_snippets()

    def analyze_and_recommend(self):
        snap = self.gather_status_snapshot()
        tips = []
        if (snap.get("queue", 0) or 0) > 0:
            tips.append("You have items in the Apply Queue. Click ‘Apply Queue’.")
        if (snap.get("tasks", 0) or 0) > 0 and (snap.get("snippets", 0) or 0) == 0:
            tips.append("Verify tasks to generate snippets.")
        if (snap.get("errors", 0) or 0) > 0:
            tips.append("Open events.log in Files/Logs to review errors, then run /self_heal.")
        if not tips:
            tips.append("Everything looks calm. Try ‘Automate Everything’ or start Yin/Yang.")
        self.append_user_facing_main("assistant", "Recommendations:\n- " + "\n- ".join(tips))

    def on_status_clicked(self):
        self.analyze_and_recommend()

    # ===== Agents / Autonomy =====
    def on_run_agents_clicked(self):
        self.run_agents_pipeline(user_turn="(manual run)", prior_answer="")

    def run_agents_pipeline(self, user_turn: str, prior_answer: str):
        try:
            # 1) quick walk to keep RAG fresh (lightweight)
            self.deploy_agent_walk_files(silent=True)
            # 2) convert current compose notes into a task sheet if any
            msgs = get_conversation("compose", 20)
            if msgs:
                self.on_compose_create()
            # 3) verify all → snippets → apply queue
            self.on_verify_all()
            self.on_apply_queue()
            # 4) checkpoint
            self.make_checkpoint()
            self.append_user_facing_main("assistant", "Autonomy cycle complete.")
        except Exception as e:
            record_error("agents", "pipeline failed", repr(e))
            self.append_user_facing_main("error", f"Agent pipeline error: {e}")

    def deploy_agent_walk_files(self, silent: bool = False):
        try:
            scanned = 0
            for p in ROOT.rglob("*"):
                if p.is_dir(): continue
                try:
                    if p.stat().st_size > 2_000_000:
                        continue
                except Exception:
                    continue
                suf = p.suffix.lower()
                ingest_file(p, "code" if suf == ".py" else ("log" if suf == ".log" else "data"))
                scanned += 1
            rebuild_code_datasets(ROOT / SCRIPT_NAME)
            if not silent:
                self.append_user_facing_main("assistant", f"Walked & ingested ~{scanned} files. Datasets rebuilt.")
        except Exception as e:
            record_error("walk", "failed", repr(e))
            if not silent:
                self.append_user_facing_main("error", f"Walk failed: {e}")

    def self_heal(self):
        try:
            with db_connect(MAIN_DB) as cx:
                row = cx.execute("SELECT * FROM errors ORDER BY id DESC LIMIT 1").fetchone()
            if not row:
                self.append_user_facing_main("assistant", "No recent errors to heal.")
                return
            title = f"Self-heal: {row['source']}"
            body = f"{row['message']}\n\n{row['detail'][:600]}"
            tid = add_task(title, body)
            set_task_status(tid, "draft")
            self._verify_task_id(tid, auto_enq=True)
            self.append_user_facing_main("assistant", f"Filed self-heal task #{tid} and queued a note into docs.")
        except Exception as e:
            record_error("self_heal", "failed", repr(e))

    def on_auto_chain(self):
        self.on_verify_all()
        self.on_apply_queue()
        self.analyze_and_recommend()

    # ===== Evolve Launch (batch sanity + rollback) =====
    def evolve_launch(self) -> bool:
        # Collect queued snippets targeting the main script
        queued: List[Dict[str, Any]] = []
        others: List[Dict[str, Any]] = []
        # Drain queue non-destructively: snapshot queue rows
        with db_connect(MAIN_DB) as cx:
            rows = cx.execute("SELECT q.id as qid, s.* FROM queue q JOIN snippets s ON s.id=q.snippet_id ORDER BY q.id ASC").fetchall()
        for r in rows:
            d = dict(r)
            if Path(d.get("target_path") or "") == (ROOT / SCRIPT_NAME):
                queued.append(d)
            else:
                others.append(d)
        if not queued and not others:
            self.append_user_facing_main("assistant", "Nothing in the queue to evolve.")
            return False

        # Combine main-script changes in-memory
        base = (ROOT / SCRIPT_NAME).read_text(encoding="utf-8", errors="replace")
        combined = base
        try:
            for sn in queued:
                mode = (sn.get("apply_mode") or "patch").lower()
                label = sn.get("label") or "SN"
                start_line = sn.get("start_line"); end_line = sn.get("end_line")
                content = sn.get("content") or ""
                if mode == "replace":
                    combined = content
                elif mode == "append":
                    combined = combined + ("" if combined.endswith("\n") else "\n") + content + ("" if content.endswith("\n") else "\n")
                elif mode == "insert_at_line":
                    lines = combined.splitlines(True)
                    idx = min(max(1, int(start_line or 1)) - 1, len(lines))
                    combined = "".join(lines[:idx]) + (content if content.endswith("\n") else content + "\n") + "".join(lines[idx:])
                elif mode == "replace_range":
                    lines = combined.splitlines(True)
                    a = max(0, int((start_line or 1)) - 1)
                    b = min(len(lines), int((end_line or a+1)))
                    combined = "".join(lines[:a]) + (content if content.endswith("\n") else content + "\n") + "".join(lines[b:])
                else:
                    # patch block markers
                    marker = f"# >>> {label}"
                    if marker in combined and f"# <<< {label}" in combined:
                        s = combined.find(marker); e = combined.find(f"# <<< {label}", s)
                        if e != -1:
                            e += len(f"# <<< {label}")
                            block = f"{marker}\n{content}\n# <<< {label}"
                            combined = combined[:s] + block + combined[e:]
                        else:
                            combined += f"\n{marker}\n{content}\n# <<< {label}\n"
                    else:
                        pad1 = "" if (combined.endswith("\n") or not combined) else "\n"
                        pad2 = "" if content.endswith("\n") else "\n"
                        combined += f"{pad1}# >>> {label}\n{content}{pad2}# <<< {label}\n"

            ok_ast, msg_ast = _sanity_parse_script(ROOT / SCRIPT_NAME)
            if not ok_ast:
                self.append_user_facing_main("error", f"AST parse failed on base: {msg_ast}")
                return False

            # Write combined to a temp, py_compile it
            tmp = Path(tempfile.mkstemp(prefix="evolve_", suffix=".py")[1])
            tmp.write_text(combined, encoding="utf-8")
            ok_pc, msg_pc = _py_compile_script(tmp, timeout=12)
            tmp.unlink(missing_ok=True)
            if not ok_pc:
                self.append_user_facing_main("error", f"py_compile failed on combined plan:\n{msg_pc[:400]}")
                return False

            # If sanity OK: apply everything (main-script + others) sequentially
            # First clear queue rows we just snapshot to avoid double-apply; then apply.
            with db_connect(MAIN_DB) as cx:
                cx.execute("DELETE FROM queue")

            applied = 0; failed = 0
            for sn in queued + others:
                ok = apply_snippet(sn)
                applied += 1 if ok else 0
                failed  += 0 if ok else 1

            # Journal evolve run
            with db_connect(MAIN_DB) as cx:
                cx.execute("""INSERT INTO evolve_runs(started_at, ended_at, ok, applied_snippets, rolled_back, note)
                              VALUES(?,?,?,?,?,?)""",
                           (int(time.time())-1, int(time.time()), 1, applied, 0, "evolve batch ok"))
            self.append_user_facing_main("assistant", f"Evolve Launch applied {applied} snippet(s); {failed} failed.")
            return True

        except Exception as e:
            record_error("evolve", "failed", repr(e))
            with db_connect(MAIN_DB) as cx:
                cx.execute("""INSERT INTO evolve_runs(started_at, ended_at, ok, applied_snippets, rolled_back, note)
                              VALUES(?,?,?,?,?,?)""",
                           (int(time.time())-1, int(time.time()), 0, 0, 1, f"exception: {e}"))
            self.append_user_facing_main("error", f"Evolve failed: {e}")
            return False

    def on_evolve_launch_clicked(self):
        self.evolve_launch()

    # ===== Yin/Yang =====
    def toggle_yinyang(self):
        if self._yinyang_timer and self._yinyang_timer.isActive():
            self._yinyang_timer.stop(); self._yinyang_timer = None
            self.btn_yinyang.setText("Yin/Yang: OFF")
            self.append_monolog("Yin/Yang paused.")
            return
        try:
            iv = int(self.ed_yinyang_interval.text().strip() or "10")
        except Exception:
            iv = 10
        self._yinyang_timer = QTimer(self)
        self._yinyang_timer.timeout.connect(self._yy_tick)
        self._yinyang_timer.start(max(3, iv) * 1000)
        self.btn_yinyang.setText("Yin/Yang: ON")
        self.append_monolog("Yin/Yang engaged.")

    def _yy_tick(self):
        if self._yy_busy: return
        self._yy_busy = True
        try:
            # Safe proposal: append a tiny reflective note into NOTES.txt, never touch core.
            note = f"- {time.strftime('%H:%M:%S')} YY reflection: ensure launcher and installer paths are robust."
            tid = add_task("YY: reflective note", note)
            sn = add_snippet(tid, "YY_NOTE", note, str(DOCS_DIR / "NOTES.txt"), "append")
            enqueue_snippet(sn)
            set_task_status(tid, "verified")
            self.append_monolog("Proposed a safe snippet (NOTES.txt).")
            if self.autonomy:
                self.on_apply_queue()
        except Exception as e:
            record_error("yinyang", "tick failed", repr(e))
            self.append_monolog(f"Tick error: {e}")
        finally:
            self._yy_busy = False

    # ===== TTS =====
    def on_tts_start(self):
        if not self.tts.enabled:
            self.post_console_err("TTS not available.")
            return
        txt = self.last_user_or_assistant or "Ready."
        self.tts.speak(txt)

    def on_tts_stop(self):
        self.tts.stop()

    def on_tts_play_current(self):
        if not self.tts.enabled: return
        txt = (self.last_user_or_assistant or "") + "\n" + (self.last_monolog or "")
        self.tts.speak(txt or "Nothing to read.")

    def on_tts_read_selection(self):
        if not self.tts.enabled: return
        txt = ""
        try:
            c = self.chat_view.textCursor()
            if c and c.hasSelection():
                txt = c.selectedText()
            else:
                c2 = self.compose_view.textCursor()
                if c2 and c2.hasSelection():
                    txt = c2.selectedText()
                else:
                    c3 = self.editor.textCursor()
                    if c3 and c3.hasSelection():
                        txt = c3.selectedText()
        except Exception:
            pass
        txt = _normalize_selected_text(txt).strip()
        if not txt:
            self.post_console("Nothing selected to read.")
            return
        self.tts.speak(txt)

    # ===== Editor / Files =====
    def on_editor_open(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open file", str(ROOT))
        if not p: return
        try:
            self.editor.setPlainText(Path(p).read_text(encoding="utf-8", errors="replace"))
            self.editor._open_path = p
            self.post_console(f"Loaded {p}")
        except Exception as e:
            record_error("editor_open", p, repr(e))
            self.post_console_err(f"Open failed: {e}")

    def on_editor_save(self):
        p = getattr(self.editor, "_open_path", None)
        if not p:
            QMessageBox.information(self, "Save", "Use ‘Load file…’ first.")
            return
        try:
            Path(p).write_text(self.editor.toPlainText(), encoding="utf-8")
            self.post_console(f"Saved {p}")
        except Exception as e:
            record_error("editor_save", p, repr(e))
            self.post_console_err(f"Save failed: {e}")

    def on_editor_goto(self):
        from PyQt5.QtWidgets import QInputDialog
        ln, ok = QInputDialog.getInt(self, "Go to line", "Line #:", 1, 1, 10_000_000, 1)
        if not ok: return
        try:
            c = self.editor.textCursor()
            c.movePosition(QTextCursor.Start)
            for _ in range(ln-1):
                c.movePosition(QTextCursor.Down)
            self.editor.setTextCursor(c)
            self.post_console(f"Jumped to line {ln}")
        except Exception:
            pass

    def open_script(self):
        self._open_path(ROOT / SCRIPT_NAME)

    def open_logs(self):
        self._open_path(LOGS_DIR / "events.log")

    def _open_path(self, p: Path):
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(p))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(p)])
            else:
                subprocess.Popen(["xdg-open", str(p)])
        except Exception as e:
            record_error("open_path", str(p), repr(e))
            self.post_console_err(f"Open failed: {e}")

    # ===== Journal / Diff =====
    def refresh_journal_list(self):
        self.journal_list.clear()
        rows = []
        try:
            with db_connect(MAIN_DB) as cx:
                rows = cx.execute("SELECT id,file_path,ok,lines_added,lines_removed,created_at FROM patch_journal ORDER BY id DESC LIMIT 200").fetchall()
        except Exception as e:
            record_error("journal_list", "query failed", repr(e))
        for r in rows:
            ts = time.strftime("%H:%M:%S", time.localtime(r["created_at"]))
            ok = "OK" if r["ok"] else "FAIL"
            self.journal_list.addItem(f"[{ok} {ts}] {Path(r['file_path']).name}  #{r['id']}")
        # bind selection → diff view
        self.journal_list.itemSelectionChanged.connect(self._load_selected_diff)

    def _load_selected_diff(self):
        items = self.journal_list.selectedItems()
        if not items: 
            self.diff_view.setPlainText("")
            return
        m = re.search(r"#(\d+)$", items[0].text())
        if not m:
            self.diff_view.setPlainText("")
            return
        jid = int(m.group(1))
        try:
            with db_connect(MAIN_DB) as cx:
                row = cx.execute("SELECT diff,error,ok FROM patch_journal WHERE id=?", (jid,)).fetchone()
            if not row:
                self.diff_view.setPlainText("(missing)")
                return
            if row["ok"]:
                self.diff_view.setPlainText(row["diff"] or "")
            else:
                self.diff_view.setPlainText(row["error"] or "(no error)")
        except Exception as e:
            record_error("diff_view", "load failed", repr(e))
            self.diff_view.setPlainText(f"Error: {e}")

# -------------------- Entrypoint --------------------

def run_qt(role: str):
    app = QApplication(sys.argv)
    w = MainWindow(role=role)
    w.show()
    # Start the learning worker
    worker = LearningWorker(w, interval_sec=25)
    w._learning_worker = worker
    worker.start()
    rc = app.exec_()
    try:
        worker.stop()
    except Exception:
        pass
    sys.exit(rc)

if __name__ == "__main__":
    # If we’re in a pure first-run context, we’ll land in the installer/launcher path.
    mode, root = ensure_bedrock_install_or_exit()
    ensure_dirs(root)
    init_all_dbs()
    # Ingest our own script if missing
    try:
        ingest_initial()
    except Exception:
        pass
    # Open the proper UI
    run_qt(role=mode)
```

FATHOM — Bedrock (single-file) — vNext (All-in-One)

Includes:
- Installer (Tk) + Launcher (Tk)  [fixed auto-launch quoting on Windows]
- Bedrock/Project UI (PyQt5)
- Tom & Jerry trainers (/trainers) + metrics DB
- Yin/Yang inner monolog → safe snippet proposals (with parsing; no blind core edits)
- Chat + Slash CLI: /status /evolve_launch /verify_all /apply_queue /auto_implement /datasets_refresh
  /code_map /code_show A-B /code_analyze <func> /code_insert /code_replace /trainers
  /autonomy on|off /tts voice <name> /tts readsel
- Apply queue with journaling, semver, CHANGELOG.md, backups
- Evolve Launch: batch apply + AST + py_compile sanity + rollback on failure
- Code Mirror, Function Analyses, Snapshots datasets
- RAG + DIFF-QA mini stores
- Self-heal task from recent errors
- TTS fallback voice; voice selection & restart
- Monolog lane only (no chat spam)
- Console alias (fixes earlier crash path)

Tested with: Python 3.10–3.13, Windows 10/11, PyQt5.
**Classes:** TTSManager, UiBridge, LineNumberArea, CodeEditor, LearningWorker, MainWindow
**Functions:** _log_line(kind, msg), log_info(msg), log_warn(msg), log_err(msg), record_error(source, message, detail), ensure_dirs(target_root), db_connect(path), _ensure_column(cx, table, col, decl), init_main_db(), ensure_assets_schema(), init_readme_db(), init_rag_db(), init_diffqa_db(), init_all_dbs(), _sha256_text(s), make_backup(path), readme_set(key, val), readme_topical_snapshot(topic, limit_chars), ingest_file(p, kind), rag_search_raw(query, limit), diffqa_add(q, a, tags), diffqa_search(q, limit_chars), _code_mirror_store(script_path, code), _code_mirror_load(script_path), _fn_analyses_store(script_path, analyses), _fn_analyses_load(script_path), create_function_snapshots(script_path), analyze_functions(script_path), rebuild_code_datasets(script_path), add_conversation(lane, role, content), get_conversation(lane, limit), add_task(title, body), set_task_status(tid, status), list_tasks(limit), add_snippet(task_id, label, content, target_path, apply_mode, start_line, end_line), list_snippets(limit), enqueue_snippet(sid), dequeue_next(), _read_setting(key, default), _write_setting(key, val), current_semver(), bump_semver(level, msg), _unified_diff_text(before, after, a_name, b_name), _count_changes(diff_text), _atomic_write_text(target, text), _record_indent_learning(after_text, target), append_changelog(title, file_path, diff_text, ok, note), apply_snippet(snippet), ensure_preloaded_tasks(), _desktop_dir(), _write(p, text), write_launcher_script(root), _create_windows_shortcut(desktop, root), write_desktop_shortcut(root), _elevated_launch_windows(py, arg_script, cwd, as_admin), launch_launcher(root, as_admin), schedule_self_delete(original_script), preseed_dev_key(root), _dev_token_fresh(), _dev_mode_requested(here), initialize_bedrock_root(target_root), _tk_install_gui(current_here), ensure_bedrock_install_or_exit(), build_machine_readme(code), ingest_initial(), _http_get(url, timeout), _http_post_json(url, data, timeout), ollama_reachable(url), chat_once(url, model, messages), add_hypothesis(title, evidence, pseudocode, confidence), _sanity_parse_script(path), _py_compile_script(path, timeout), run_trainer_box(name, color, lifetime_sec), run_trainer_pair(), _in_core_protected_range(a, b), _safe_to_text(x), _normalize_selected_text(txt), _slice_lines(text, start, end), run_qt(role)
