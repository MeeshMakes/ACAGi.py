# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `ant_compiler.py`

**Classes:** CompilerUI

**Functions:** ensure_dirs(), run_sql_script(db_path, sql_text), create_host_from_loader_or_builtin(db_path), inject_cell(db_path, name, code, immutable, parent, pos, size), add_bucket(db_path, name, purpose, schema_json, mutable), verify_host(db_path), vacuum_db(db_path), make_packed_launcher(launcher_src_path, bedrock_db_path, out_path, bedrock_name), have_pyinstaller(), run_pyinstaller(entry, dist_dir, icon_path, exe_name, cwd, log_cb), dark(app), ts(), main()
### `Backups\ant_launcher.py`

**Classes:** DropBox, AddBedrockDialog, LauncherWindow

**Functions:** config_root(), bedrocks_dir(), manifest_path(), projects_manifest_path(), ensure_dirs(), sha256_file(p), resource_path(rel), read_manifest(), write_manifest(m), read_projects_manifest(), write_projects_manifest(m), system_python_candidates(), ensure_valid_bedrock(path), clone_bedrock(src_bedrock, dest_project, project_name), read_immune_code(db_path), apply_dark_retro_theme(app), main()
### `Backups\cell_1.py`

**Classes:** ANT, _CellWidget

**Functions:** _make_stylesheet(), build_gui(api), core_behavior(api)
### `Backups\immune_system.py`

**Classes:** DB, ANTApi, GridScene, CellItem, CompositeItem, View, ImmuneUI

**Functions:** now_utc(), compile_ok(code), apply_dark_palette(app), pick_host_path(parent), main()
### `Loader\cell_1.py`

**Classes:** Host, ANTSoul, CellWidget

**Functions:** now_utc(), unified_diff(a, b, A, B), compile_ok(code), http_json(url, payload, timeout), list_ollama_models(), build_gui(api), core_behavior(api)
### `Loader\immune_system.py`
### `Sandbox\ant_launcher.py`

**Classes:** Config, LogConsole, PathsPane, ProjectsPane, SandboxPane, CompilePane, MainUI

**Functions:** ensure_dirs(), load_json(p, default), save_json(p, obj), ts_utc(), sanitize_name(s), main()
### `Sandbox\cell_1.py`

**Classes:** Host, ANTSoul, CellWidget

**Functions:** now_utc(), unified_diff(a, b, A, B), compile_ok(code), http_json(url, payload, timeout), list_ollama_models(), build_gui(api), core_behavior(api)
### `Sandbox\immune_system.py`

## Other Files

The following files are present in the project but were not analysed in detail:

- `Backups\Bedrock.sql`
- `Backups\singlecell.png`
- `Output\Projects\Tester\host.db`
- `Sandbox\Bedrock.sql`


## Detailed Module Analyses


## Module `ant_compiler.py`

```python
#!/usr/bin/env python3
# ant_compiler.py — Sandbox-first compiler/orchestrator (no EXE by default)
#
# Folders (auto-created if missing):
#   Sandbox/         # you develop here (messy, experimental)
#   Loader/          # curated "ready" scripts, SQLs, assets (compiler pulls from here)
#   Output/Projects/ # per-project hosts (SQLite DB) and artifacts
#   Output/Checkpoints/<project>/  # timestamped DB snapshots
#
# Tabs:
#   - Projects: create/select active project
#   - Build Host: create host DB from built-in DDL or Loader/Bedrock.sql
#   - Inject & Buckets: inject cell_0 (immutable), immune_system.py, cell_1.py; add buckets
#   - Run (Sandbox): run immune_system.py directly (Python) with SINGLECELL_DB=... (logs streamed)
#   - Pack/EXE (Advanced): preserved but OFF by default behind a checkbox
#
# Requires: Python 3.9+, PyQt5
# Optional: pyinstaller (only when enabling EXE build pipeline later)

import os, sys, json, sqlite3, time, base64, subprocess, shutil
from pathlib import Path
from typing import Optional, Tuple, List

from PyQt5 import QtCore, QtGui, QtWidgets

# --------------------------------------------------------------------------------------
# Hard-coded structure
# --------------------------------------------------------------------------------------

BASE_DIR     = Path(__file__).resolve().parent
SANDBOX_DIR  = (BASE_DIR / "Sandbox").resolve()
LOADER_DIR   = (BASE_DIR / "Loader").resolve()
OUTPUT_DIR   = (BASE_DIR / "Output").resolve()
PROJECTS_DIR = (OUTPUT_DIR / "Projects").resolve()
CHECKS_DIR   = (OUTPUT_DIR / "Checkpoints").resolve()
DIST_DIR     = (OUTPUT_DIR / "dist").resolve()  # only used when EXE pipeline is enabled

# Filenames expected in Loader/
LAUNCHER_SRC_NAME = "ant_launcher.py"  # optional now
IMMUNE_NAME       = "immune_system.py"
CELL1_NAME        = "cell_1.py"
BEDROCK_SQL_NAME  = "Bedrock.sql"      # optional; we use built-in DDL if missing
ICON_NAME         = "singlecell.png"   # optional

# Defaults inside a project
DEFAULT_DB_NAME   = "host.db"
DEFAULT_EXE_NAME  = "ANT_Launcher"
PACKED_NAME       = "launcher_packed.py"

def ensure_dirs():
    for d in (SANDBOX_DIR, LOADER_DIR, OUTPUT_DIR, PROJECTS_DIR, CHECKS_DIR, DIST_DIR):
        d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------------------
# Built-in DDL (used when Loader/Bedrock.sql is absent)
# --------------------------------------------------------------------------------------

BUILTIN_DDL = r"""
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
PRAGMA page_size = 4096;
PRAGMA user_version = 1;

BEGIN;

CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE IF NOT EXISTS cells (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT UNIQUE NOT NULL,
  parent_id     INTEGER,
  cluster_id    TEXT,
  immutable     INTEGER DEFAULT 0,
  code          TEXT NOT NULL,
  metadata_json TEXT,
  version       INTEGER DEFAULT 1,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cell_versions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  cell_name     TEXT NOT NULL,
  version       INTEGER NOT NULL,
  code          TEXT NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_cell_versions_name_ver ON cell_versions(cell_name, version);

CREATE TABLE IF NOT EXISTS diffs (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  cell_name     TEXT NOT NULL,
  from_version  INTEGER,
  to_version    INTEGER,
  diff_type     TEXT,
  diff_text     TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS signals (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  from_cell     TEXT,
  to_cell       TEXT,
  kind          TEXT NOT NULL,
  payload_json  TEXT NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_signals_to_kind ON signals(to_cell, kind);

CREATE TABLE IF NOT EXISTS errors (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  cell_name     TEXT,
  version       INTEGER,
  traceback     TEXT,
  context_json  TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  resolved_by   TEXT
);
CREATE INDEX IF NOT EXISTS idx_errors_cell_ver ON errors(cell_name, version);

CREATE TABLE IF NOT EXISTS knowledge (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  cell_name     TEXT,
  content_text  TEXT NOT NULL,
  embedding     BLOB,
  tags_json     TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  cell_name     TEXT,
  type          TEXT,
  data          BLOB,
  path          TEXT,
  meta_json     TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS antapi (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT UNIQUE NOT NULL,
  code          TEXT NOT NULL,
  version       INTEGER DEFAULT 1,
  metadata_json TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  cell_name     TEXT,
  level         TEXT,
  message       TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS buckets (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT UNIQUE NOT NULL,
  purpose       TEXT NOT NULL,
  schema_json   TEXT NOT NULL,
  mutable       INTEGER DEFAULT 1,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bucket_items (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  bucket_name   TEXT NOT NULL REFERENCES buckets(name) ON DELETE CASCADE,
  key           TEXT NOT NULL,
  value_json    TEXT NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(bucket_name, key)
);

CREATE TABLE IF NOT EXISTS readmes (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  name              TEXT UNIQUE NOT NULL,
  content_markdown  TEXT NOT NULL,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_cells_guard_immutable
BEFORE UPDATE OF code ON cells
WHEN old.immutable = 1
BEGIN
  SELECT RAISE(ABORT, 'immutable cell cannot update code');
END;

CREATE TRIGGER IF NOT EXISTS trg_cells_guard_version_step
BEFORE UPDATE OF code ON cells
WHEN new.immutable = 0 AND new.version <> old.version + 1
BEGIN
  SELECT RAISE(ABORT, 'version must increment by exactly 1 when updating code');
END;

CREATE TRIGGER IF NOT EXISTS trg_cells_version_snapshot
AFTER UPDATE OF code ON cells
WHEN new.immutable = 0
BEGIN
  INSERT INTO cell_versions(cell_name, version, code)
  VALUES (new.name, new.version, new.code);
END;

CREATE TRIGGER IF NOT EXISTS trg_errors_log
AFTER INSERT ON errors
BEGIN
  INSERT INTO logs(cell_name, level, message, created_at)
  VALUES (new.cell_name, 'ERROR', coalesce(new.traceback,'(no tb)'), CURRENT_TIMESTAMP);
END;

INSERT OR REPLACE INTO meta(key, value) VALUES
 ('bedrock_version','v1'),
 ('created_at_utc', datetime('now')),
 ('narrative', '# ANT Bedrock — Host body with cells/versions/diffs/signals/errors/knowledge/assets/buckets');

COMMIT;
"""

DEFAULT_CELL0 = """from PyQt5 import QtWidgets
def build_gui(api):
    w=QtWidgets.QWidget(); v=QtWidgets.QVBoxLayout(w)
    v.addWidget(QtWidgets.QLabel('cell_0 template'))
    v.addWidget(QtWidgets.QLabel('Immutable bedrock template.'))
    return w
def core_behavior(api):
    api.log('INFO','cell_0 heartbeat'); api.remember('cell_0 heartbeat')
    return {'ok': True}
"""

BUCKET_TEMPLATES = {
    "code_parts": {
        "purpose": "Segmented code for surgical edits",
        "schema": {"type":"object","required":["cell","segments"],
                   "properties":{"cell":{"type":"string"},
                                 "segments":{"type":"array","items":{"type":"object",
                                 "required":["kind","name","text"],
                                 "properties":{"kind":{"enum":["import","class","function","comment","other"]},
                                               "name":{"type":"string"},
                                               "text":{"type":"string"}}}}}}
    },
    "prompts": {
        "purpose": "Reusable prompts and instruction templates",
        "schema": {"type":"object","required":["title","text"],
                   "properties":{"title":{"type":"string"},"text":{"type":"string"}}}
    },
    "debates": {
        "purpose": "Dialogues between cells for planning/consensus",
        "schema": {"type":"object","required":["topic","transcript"],
                   "properties":{"topic":{"type":"string"},"transcript":{"type":"array"}}}
    },
    "ui_layouts": {
        "purpose": "Saved GUI placements and composite layout configs",
        "schema": {"type":"object","required":["layout"],"properties":{"layout":{"type":"object"}}}
    },
    "merge_protocols": {
        "purpose": "Interface contracts for merged cells",
        "schema": {"type":"object","required":["name","events","payload_schema"],
                   "properties":{"name":{"type":"string"},"events":{"type":"array"},
                                 "payload_schema":{"type":"object"}}}
    },
    "repair_strategies": {
        "purpose": "Known error patterns mapped to proposed patches",
        "schema": {"type":"object","required":["pattern","fix"],
                   "properties":{"pattern":{"type":"string"},"fix":{"type":"string"}}}
    }
}

# --------------------------------------------------------------------------------------
# DB helpers
# --------------------------------------------------------------------------------------

def run_sql_script(db_path: Path, sql_text: str):
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(sql_text)
        conn.commit()
    finally:
        conn.close()

def create_host_from_loader_or_builtin(db_path: Path):
    if db_path.exists():
        db_path.unlink()
    loader_sql = LOADER_DIR / BEDROCK_SQL_NAME
    sql = loader_sql.read_text(encoding="utf-8") if loader_sql.exists() else BUILTIN_DDL
    run_sql_script(db_path, sql)

def inject_cell(db_path: Path, name: str, code: str, immutable: int, parent: Optional[str] = None,
                pos=(0,0), size=(800,800)) -> None:
    meta = {"pos":{"x":pos[0],"y":pos[1]},"size":{"w":size[0],"h":size[1]}}
    conn = sqlite3.connect(str(db_path)); conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM cells WHERE name=?", (name,))
        if cur.fetchone():
            cur.execute("DELETE FROM cell_versions WHERE cell_name=?", (name,))
            cur.execute("UPDATE cells SET immutable=?, code=?, metadata_json=?, version=1 WHERE name=?",
                        (immutable, code, json.dumps(meta), name))
        else:
            cur.execute(
                "INSERT INTO cells(name,parent_id,cluster_id,immutable,code,metadata_json,version) "
                "VALUES (?,NULL,NULL,?,?,?,1)",
                (name, immutable, code, json.dumps(meta))
            )
        cur.execute("INSERT INTO cell_versions(cell_name,version,code) VALUES(?,?,?)", (name, 1, code))
        conn.commit()
    finally:
        conn.close()

def add_bucket(db_path: Path, name: str, purpose: str, schema_json: str, mutable: int = 1):
    conn = sqlite3.connect(str(db_path)); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT OR REPLACE INTO buckets(name,purpose,schema_json,mutable) VALUES(?,?,?,?)",
            (name, purpose, schema_json, mutable)
        )
        conn.commit()
    finally:
        conn.close()

def verify_host(db_path: Path) -> Tuple[bool, List[str]]:
    errors = []
    req_tables = [
        "meta","cells","cell_versions","diffs","signals","errors","knowledge",
        "assets","antapi","logs","buckets","bucket_items","readmes"
    ]
    conn = sqlite3.connect(str(db_path)); cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        have = {r[0] for r in cur.fetchall()}
        missing = [t for t in req_tables if t not in have]
        if missing:
            errors.append(f"Missing tables: {', '.join(missing)}")

        for trg in ["trg_cells_guard_immutable","trg_cells_guard_version_step","trg_cells_version_snapshot","trg_errors_log"]:
            cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name=?", (trg,))
            if not cur.fetchone():
                errors.append(f"Missing trigger: {trg}")

        for cname in ["cell_0","immune_system","cell_1"]:
            cur.execute("SELECT name, immutable, code, version FROM cells WHERE name=?", (cname,))
            row = cur.fetchone()
            if not row:
                errors.append(f"Warning: {cname} not injected yet.")
            else:
                if cname=="cell_0" and row[1] != 1:
                    errors.append("cell_0 should be immutable=1")
                if not row[2] or not isinstance(row[2], str):
                    errors.append(f"{cname} has empty or invalid code")
                if row[3] != 1:
                    errors.append(f"{cname} initial version should be 1 (got {row[3]})")
    finally:
        conn.close()
    return (len([e for e in errors if not e.startswith("Warning")]) == 0, errors)

def vacuum_db(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("VACUUM")
        conn.commit()
    finally:
        conn.close()

# --------------------------------------------------------------------------------------
# Pack/EXE pipeline (kept, OFF by default)
# --------------------------------------------------------------------------------------

PACKED_TEMPLATE = r'''#!/usr/bin/env python3
# Auto-generated by ANT Compiler — packed launcher with embedded Bedrock DB
import os, base64

BEDROCK_NAME = {bedrock_name!r}
BEDROCK_B64  = {bedrock_b64!r}

def _write_bedrock() -> str:
    data = base64.b64decode(BEDROCK_B64.encode('ascii'))
    base_dir = os.path.join(os.path.expanduser("~"), ".ant_bedrocks")
    os.makedirs(base_dir, exist_ok=True)
    p = os.path.join(base_dir, BEDROCK_NAME)
    with open(p, "wb") as f:
        f.write(data)
    os.environ["ANT_DEFAULT_BEDROCK_PATH"] = p
    return p

def main():
    _write_bedrock()
    LAUNCHER_SRC = r{launcher_src}
    g = {{}}
    g["__name__"] = "__main__"
    exec(LAUNCHER_SRC, g, g)

if __name__ == "__main__":
    main()
'''

def make_packed_launcher(launcher_src_path: Path, bedrock_db_path: Path, out_path: Path, bedrock_name: str):
    src = launcher_src_path.read_text(encoding="utf-8")
    b64 = base64.b64encode(bedrock_db_path.read_bytes()).decode("ascii")
    content = PACKED_TEMPLATE.format(
        bedrock_name=bedrock_name,
        bedrock_b64=b64,
        launcher_src=repr(src)
    )
    out_path.write_text(content, encoding="utf-8")

def have_pyinstaller() -> bool:
    from shutil import which
    return which("pyinstaller") is not None

def run_pyinstaller(entry: Path, dist_dir: Path, icon_path: Optional[Path], exe_name: str, cwd: Path, log_cb):
    if not have_pyinstaller():
        raise RuntimeError("pyinstaller not found on PATH (pip install pyinstaller)")
    cmd = ["pyinstaller", str(entry), "--onefile", "--windowed", "--name", exe_name, "--distpath", str(dist_dir)]
    if icon_path and icon_path.exists():
        cmd += ["--icon", str(icon_path)]
    log_cb(f"$ (cwd={cwd}) {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        log_cb(line.rstrip())
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"PyInstaller exited with {ret}")

# --------------------------------------------------------------------------------------
# UI helpers
# --------------------------------------------------------------------------------------

def dark(app: QtWidgets.QApplication):
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, QtGui.QColor(18,18,18))
    pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Base, QtGui.QColor(12,12,12))
    pal.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(22,22,22))
    pal.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Button, QtGui.QColor(24,24,24))
    pal.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(60,180,120))
    pal.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(pal)
    app.setStyle("Fusion")

def ts():
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())

# --------------------------------------------------------------------------------------
# Main UI
# --------------------------------------------------------------------------------------

class CompilerUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        ensure_dirs()
        self.setWindowTitle("ANT Compiler — Sandbox Mode (EXE disabled by default)")
        self.resize(1280, 860)
        self.active_project: Optional[str] = None
        self.proc: Optional[QtCore.QProcess] = None
        self._build_ui()
        self.refresh_projects()

    # ---------- UI layout ----------
    def _build_ui(self):
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self._tab_projects()
        self._tab_build()
        self._tab_inject()
        self._tab_run()
        self._tab_pack()

        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)

    def _tab_projects(self):
        w = QtWidgets.QWidget(); L = QtWidgets.QVBoxLayout(w)
        self.tabs.addTab(w, "Projects")

        # List + actions
        row = QtWidgets.QHBoxLayout()
        self.list_projects = QtWidgets.QListWidget()
        self.list_projects.itemSelectionChanged.connect(self.on_project_selected)
        L.addWidget(QtWidgets.QLabel("Projects in Output/Projects"))
        row.addWidget(self.list_projects, 2)

        box = QtWidgets.QGroupBox("Actions"); vb = QtWidgets.QVBoxLayout(box)
        self.ed_new = QtWidgets.QLineEdit(); self.ed_new.setPlaceholderText("new_project_name")
        b_new = QtWidgets.QPushButton("Create Project")
        b_new.clicked.connect(self.create_project)
        b_del = QtWidgets.QPushButton("Delete Project")
        b_del.clicked.connect(self.delete_project)
        b_set = QtWidgets.QPushButton("Set Active")
        b_set.clicked.connect(self.set_active_project)
        self.lbl_active = QtWidgets.QLabel("Active: —")
        vb.addWidget(self.ed_new); vb.addWidget(b_new); vb.addWidget(b_del); vb.addWidget(b_set); vb.addWidget(self.lbl_active); vb.addStretch(1)

        row.addWidget(box, 1)
        L.addLayout(row)

        # Paths view
        self.lbl_paths = QtWidgets.QLabel("Paths — select a project")
        self.lbl_paths.setWordWrap(True)
        L.addWidget(self.lbl_paths)

    def _tab_build(self):
        w = QtWidgets.QWidget(); L = QtWidgets.QVBoxLayout(w)
        self.tabs.addTab(w, "Build Host")

        g = QtWidgets.QGroupBox("Create Host DB for Active Project")
        v = QtWidgets.QVBoxLayout(g)
        b_builtin = QtWidgets.QPushButton("Create from Built-in DDL")
        b_builtin.clicked.connect(self.build_from_builtin)
        b_loader = QtWidgets.QPushButton("Create from Loader/Bedrock.sql (if exists)")
        b_loader.clicked.connect(self.build_from_loader)
        self.log_build = QtWidgets.QPlainTextEdit(); self.log_build.setReadOnly(True); self.log_build.setMinimumHeight(160)
        v.addWidget(b_builtin); v.addWidget(b_loader); v.addWidget(QtWidgets.QLabel("Log")); v.addWidget(self.log_build,1)
        L.addWidget(g)

    def _tab_inject(self):
        w = QtWidgets.QWidget(); L = QtWidgets.QVBoxLayout(w)
        self.tabs.addTab(w, "Inject & Buckets")

        g1 = QtWidgets.QGroupBox("Inject Cells from Loader/")
        v1 = QtWidgets.QVBoxLayout(g1)
        self.ed_cell0 = QtWidgets.QPlainTextEdit()
        self.ed_cell0.setPlainText(DEFAULT_CELL0)
        self.ed_cell0.setMinimumHeight(110)
        b_c0 = QtWidgets.QPushButton("Inject cell_0 (immutable)")
        b_c0.clicked.connect(self.inject_c0)

        grid = QtWidgets.QGridLayout()
        self.lbl_immune = QtWidgets.QLabel(str(LOADER_DIR / IMMUNE_NAME))
        self.lbl_cell1  = QtWidgets.QLabel(str(LOADER_DIR / CELL1_NAME))
        b_immune = QtWidgets.QPushButton("Inject immune_system (immutable)")
        b_cell1  = QtWidgets.QPushButton("Inject cell_1 (mutable)")
        b_immune.clicked.connect(lambda: self.inject_from_loader(IMMUNE_NAME, "immune_system", 1))
        b_cell1.clicked.connect(lambda: self.inject_from_loader(CELL1_NAME, "cell_1", 0))

        grid.addWidget(QtWidgets.QLabel("immune_system.py"),0,0); grid.addWidget(self.lbl_immune,0,1); grid.addWidget(b_immune,0,2)
        grid.addWidget(QtWidgets.QLabel("cell_1.py"),1,0); grid.addWidget(self.lbl_cell1,1,1); grid.addWidget(b_cell1,1,2)

        v1.addWidget(QtWidgets.QLabel("cell_0 template (you can tweak before injection)"))
        v1.addWidget(self.ed_cell0)
        v1.addWidget(b_c0)
        v1.addLayout(grid)

        g2 = QtWidgets.QGroupBox("Add / Update Bucket")
        v2 = QtWidgets.QVBoxLayout(g2)
        rowt = QtWidgets.QHBoxLayout()
        self.cb_tpl = QtWidgets.QComboBox(); self.cb_tpl.addItems(["<custom>"] + list(BUCKET_TEMPLATES.keys()))
        self.cb_tpl.currentIndexChanged.connect(self.on_tpl_change)
        rowt.addWidget(QtWidgets.QLabel("Template:")); rowt.addWidget(self.cb_tpl)
        form = QtWidgets.QFormLayout()
        self.ed_bname = QtWidgets.QLineEdit()
        self.ed_bpurpose = QtWidgets.QLineEdit()
        self.ed_bschema = QtWidgets.QPlainTextEdit(); self.ed_bschema.setMinimumHeight(120)
        form.addRow("Name", self.ed_bname); form.addRow("Purpose", self.ed_bpurpose); form.addRow("Schema (JSON)", self.ed_bschema)
        b_add = QtWidgets.QPushButton("Add/Update Bucket")
        b_add.clicked.connect(self.add_bucket_clicked)
        v2.addLayout(rowt); v2.addLayout(form); v2.addWidget(b_add)

        self.log_inject = QtWidgets.QPlainTextEdit(); self.log_inject.setReadOnly(True); self.log_inject.setMinimumHeight(140)

        L.addWidget(g1); L.addWidget(g2)
        L.addWidget(QtWidgets.QLabel("Log")); L.addWidget(self.log_inject,1)

    def _tab_run(self):
        w = QtWidgets.QWidget(); L = QtWidgets.QVBoxLayout(w)
        self.tabs.addTab(w, "Run (Sandbox)")

        g = QtWidgets.QGroupBox("Launch immune_system.py (Python) against Active Project DB")
        v = QtWidgets.QVBoxLayout(g)
        self.lbl_immune_path = QtWidgets.QLabel(str(LOADER_DIR / IMMUNE_NAME))
        self.btn_run = QtWidgets.QPushButton("Launch Immune System")
        self.btn_run.clicked.connect(self.launch_immune)
        self.btn_stop = QtWidgets.QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_proc); self.btn_stop.setEnabled(False)
        row = QtWidgets.QHBoxLayout(); row.addWidget(self.btn_run); row.addWidget(self.btn_stop); row.addStretch(1)
        self.cons = QtWidgets.QPlainTextEdit(); self.cons.setReadOnly(True); self.cons.setMinimumHeight(260)
        v.addWidget(QtWidgets.QLabel("immune_system.py path:")); v.addWidget(self.lbl_immune_path)
        v.addLayout(row); v.addWidget(QtWidgets.QLabel("Process Output")); v.addWidget(self.cons,1)

        g2 = QtWidgets.QGroupBox("Checkpoints")
        v2 = QtWidgets.QVBoxLayout(g2)
        self.btn_checkpoint = QtWidgets.QPushButton("Save DB Checkpoint (copy)")
        self.btn_checkpoint.clicked.connect(self.save_checkpoint)
        self.lbl_cp = QtWidgets.QLabel("Saved checkpoints will appear in Output/Checkpoints/<project>/")
        v2.addWidget(self.btn_checkpoint); v2.addWidget(self.lbl_cp)

        L.addWidget(g); L.addWidget(g2)

    def _tab_pack(self):
        w = QtWidgets.QWidget(); L = QtWidgets.QVBoxLayout(w)
        self.tabs.addTab(w, "Pack/EXE (Advanced)")
        self.cb_enable_exe = QtWidgets.QCheckBox("Enable EXE build pipeline (off by default)")
        self.cb_enable_exe.stateChanged.connect(self.toggle_exe_enabled)
        L.addWidget(self.cb_enable_exe)

        form = QtWidgets.QFormLayout()
        self.le_launcher = QtWidgets.QLineEdit(str(LOADER_DIR / LAUNCHER_SRC_NAME))
        self.le_packed   = QtWidgets.QLineEdit(PACKED_NAME)  # relative to project dir
        self.le_exe_name = QtWidgets.QLineEdit(DEFAULT_EXE_NAME)
        self.le_icon     = QtWidgets.QLineEdit(str(LOADER_DIR / ICON_NAME))
        form.addRow("Launcher (Loader/)", self.le_launcher)
        form.addRow("Packed .py name (in project dir)", self.le_packed)
        form.addRow("EXE name", self.le_exe_name)
        form.addRow("Icon (Loader/)", self.le_icon)
        L.addLayout(form)

        row = QtWidgets.QHBoxLayout()
        self.btn_pack = QtWidgets.QPushButton("Create Packed Launcher .py")
        self.btn_pack.clicked.connect(self.pack_launcher)
        self.btn_build_exe = QtWidgets.QPushButton("Build EXE (PyInstaller)")
        self.btn_build_exe.clicked.connect(self.build_exe)
        row.addWidget(self.btn_pack); row.addWidget(self.btn_build_exe); row.addStretch(1)
        L.addLayout(row)

        self.log_pack = QtWidgets.QPlainTextEdit(); self.log_pack.setReadOnly(True); self.log_pack.setMinimumHeight(220)
        L.addWidget(QtWidgets.QLabel("Advanced Log")); L.addWidget(self.log_pack,1)

        # initially disabled
        self.toggle_exe_enabled()

    # ---------- Project helpers ----------
    def projects(self) -> List[str]:
        return sorted([p.name for p in PROJECTS_DIR.glob("*") if p.is_dir()])

    def refresh_projects(self):
        sel = self.active_project
        self.list_projects.clear()
        for name in self.projects():
            self.list_projects.addItem(name)
        # restore selection
        if sel:
            items = self.list_projects.findItems(sel, QtCore.Qt.MatchExactly)
            if items:
                self.list_projects.setCurrentItem(items[0])
        self.update_paths_label()

    def project_dir(self, name: str) -> Path:
        return PROJECTS_DIR / name

    def host_db_path(self, name: str) -> Path:
        return self.project_dir(name) / DEFAULT_DB_NAME

    def on_project_selected(self):
        it = self.list_projects.selectedItems()
        if it:
            self.update_paths_label(it[0].text())

    def create_project(self):
        name = self.ed_new.text().strip()
        if not name:
            return
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)
        pdir = self.project_dir(safe)
        pdir.mkdir(parents=True, exist_ok=True)
        (CHECKS_DIR / safe).mkdir(parents=True, exist_ok=True)
        self.active_project = safe
        self.refresh_projects()
        self.status.showMessage(f"Created project '{safe}'", 4000)

    def delete_project(self):
        it = self.list_projects.selectedItems()
        if not it:
            return
        name = it[0].text()
        p = self.project_dir(name)
        ret = QtWidgets.QMessageBox.question(self, "Delete Project",
                                             f"Delete '{name}' and its DB?\n{p}",
                                             QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.Yes:
            shutil.rmtree(p, ignore_errors=True)
            shutil.rmtree(CHECKS_DIR / name, ignore_errors=True)
            if self.active_project == name:
                self.active_project = None
            self.refresh_projects()

    def set_active_project(self):
        it = self.list_projects.selectedItems()
        if not it:
            return
        self.active_project = it[0].text()
        self.update_paths_label()
        self.status.showMessage(f"Active project set to: {self.active_project}", 4000)

    def update_paths_label(self, name: Optional[str] = None):
        name = name or self.active_project
        if not name:
            self.lbl_active.setText("Active: —")
            self.lbl_paths.setText("Paths — select a project")
            return
        self.lbl_active.setText(f"Active: {name}")
        p = self.project_dir(name)
        hp = self.host_db_path(name)
        cp = CHECKS_DIR / name
        txt = f"Project dir: {p}\nHost DB: {hp}\nCheckpoints: {cp}"
        self.lbl_paths.setText(txt)

    # ---------- Build Host ----------
    def need_active(self) -> Optional[str]:
        if not self.active_project:
            QtWidgets.QMessageBox.warning(self, "Project", "Select an active project first.")
            return None
        return self.active_project

    def build_from_builtin(self):
        name = self.need_active()
        if not name: return
        try:
            create_host_from_loader_or_builtin(self.host_db_path(name))
            self.log_build.appendPlainText(f"✅ Host created from built-in DDL: {self.host_db_path(name)}")
        except Exception as e:
            self.log_build.appendPlainText(f"❌ Build failed: {e}")

    def build_from_loader(self):
        # Same function — create_host_from_loader_or_builtin() automatically uses Loader/Bedrock.sql if present
        self.build_from_builtin()

    # ---------- Inject & Buckets ----------
    def inject_c0(self):
        name = self.need_active()
        if not name: return
        dbp = self.host_db_path(name)
        if not dbp.exists():
            self.log_inject.appendPlainText("ℹ️ Host DB missing; creating first…")
            self.build_from_builtin()
        try:
            inject_cell(dbp, "cell_0", self.ed_cell0.toPlainText(), immutable=1, parent=None)
            self.log_inject.appendPlainText("✅ Injected cell_0 (immutable)")
        except Exception as e:
            self.log_inject.appendPlainText(f"❌ cell_0 injection failed: {e}")

    def inject_from_loader(self, file_name: str, target_cell: str, immutable: int):
        name = self.need_active()
        if not name: return
        dbp = self.host_db_path(name)
        if not dbp.exists():
            self.log_inject.appendPlainText("ℹ️ Host DB missing; creating first…")
            self.build_from_builtin()
        src = LOADER_DIR / file_name
        if not src.exists():
            QtWidgets.QMessageBox.warning(self, "Loader", f"Missing: {src}")
            return
        try:
            code = src.read_text(encoding="utf-8")
            inject_cell(dbp, target_cell, code, immutable=immutable, parent="cell_0" if target_cell!="immune_system" else None)
            self.log_inject.appendPlainText(f"✅ Injected {target_cell} from {src}")
        except Exception as e:
            self.log_inject.appendPlainText(f"❌ Inject {target_cell} failed: {e}")

    def on_tpl_change(self):
        key = self.cb_tpl.currentText()
        if key in BUCKET_TEMPLATES:
            tpl = BUCKET_TEMPLATES[key]
            self.ed_bname.setText(key)
            self.ed_bpurpose.setText(tpl["purpose"])
            self.ed_bschema.setPlainText(json.dumps(tpl["schema"]))
        else:
            self.ed_bname.clear(); self.ed_bpurpose.clear(); self.ed_bschema.clear()

    def add_bucket_clicked(self):
        name = self.need_active()
        if not name: return
        dbp = self.host_db_path(name)
        bname = self.ed_bname.text().strip()
        purp  = self.ed_bpurpose.text().strip()
        sch   = self.ed_bschema.toPlainText().strip()
        if not (bname and purp and sch):
            QtWidgets.QMessageBox.warning(self, "Bucket", "Fill Name, Purpose, and Schema JSON.")
            return
        try:
            json.loads(sch)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Schema", f"Invalid JSON: {e}")
            return
        try:
            add_bucket(dbp, bname, purp, sch, 1)
            self.log_inject.appendPlainText(f"✅ Bucket added/updated: {bname}")
        except Exception as e:
            self.log_inject.appendPlainText(f"❌ Bucket error: {e}")

    # ---------- Run (Sandbox) ----------
    def launch_immune(self):
        name = self.need_active()
        if not name: return
        immune = LOADER_DIR / IMMUNE_NAME
        if not immune.exists():
            QtWidgets.QMessageBox.warning(self, "Run", f"Missing immune_system.py in Loader/: {immune}")
            return
        dbp = self.host_db_path(name)
        if not dbp.exists():
            QtWidgets.QMessageBox.information(self, "Run", "Host DB missing; creating now.")
            self.build_from_builtin()

        # Build a QProcessEnvironment (PyQt5 doesn't allow env= in start())
        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("SINGLECELL_DB", str(dbp))

        # Launch process
        self.cons.clear()
        self.btn_run.setEnabled(False); self.btn_stop.setEnabled(True)
        self.proc = QtCore.QProcess(self)
        self.proc.setProcessEnvironment(env)
        self.proc.setWorkingDirectory(str(LOADER_DIR))  # so relative imports/assets resolve from Loader/
        self.proc.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.proc.readyReadStandardOutput.connect(self.on_proc_out)
        self.proc.finished.connect(self.on_proc_done)

        # program + arguments
        program = sys.executable
        arguments = [str(immune), str(dbp)]
        self.proc.start(program, arguments)

        if not self.proc.waitForStarted(3000):
            self.cons.appendPlainText("❌ Failed to start immune_system.py process.")

    def on_proc_out(self):
        if not self.proc: return
        data = self.proc.readAllStandardOutput().data().decode(errors="replace")
        if data:
            self.cons.moveCursor(QtGui.QTextCursor.End)
            self.cons.insertPlainText(data)
            self.cons.moveCursor(QtGui.QTextCursor.End)

    def on_proc_done(self):
        self.btn_run.setEnabled(True); self.btn_stop.setEnabled(False)
        self.proc = None
        self.log_run("Process finished.")

    def stop_proc(self):
        if self.proc:
            self.proc.kill()
            self.proc = None
            self.btn_run.setEnabled(True); self.btn_stop.setEnabled(False)
            self.log_run("Process killed.")

    def log_run(self, msg: str):
        self.cons.appendPlainText(msg)

    def save_checkpoint(self):
        name = self.need_active()
        if not name: return
        dbp = self.host_db_path(name)
        if not dbp.exists():
            QtWidgets.QMessageBox.warning(self, "Checkpoint", "Host DB not found.")
            return
        out_dir = CHECKS_DIR / name
        out_dir.mkdir(parents=True, exist_ok=True)
        cp = out_dir / f"{name}_{ts()}.db"
        shutil.copy2(dbp, cp)
        self.lbl_cp.setText(f"Saved: {cp}")

    # ---------- Pack/EXE (off by default) ----------
    def toggle_exe_enabled(self):
        on = self.cb_enable_exe.isChecked()
        for w in (self.le_launcher, self.le_packed, self.le_exe_name, self.le_icon):
            w.setEnabled(on)
        for tab_button in (getattr(self, "btn_pack", None), getattr(self, "btn_build_exe", None)):
            if tab_button: tab_button.setEnabled(on)
        if not on:
            self.log_pack.appendPlainText("EXE pipeline disabled (sandbox-first). Enable the checkbox to use later.")

    def pack_launcher(self):
        if not self.cb_enable_exe.isChecked():
            self.log_pack.appendPlainText("EXE pipeline disabled.")
            return
        name = self.need_active()
        if not name: return
        proj_dir = self.project_dir(name)
        dbp = self.host_db_path(name)
        if not dbp.exists():
            QtWidgets.QMessageBox.information(self, "Pack", "DB missing; building & injecting defaults.")
            self.build_from_builtin()
        launcher_path = Path(self.le_launcher.text().strip())
        if not launcher_path.exists():
            launcher_path = LOADER_DIR / LAUNCHER_SRC_NAME
        out_name = self.le_packed.text().strip() or PACKED_NAME
        packed_out = proj_dir / out_name
        try:
            make_packed_launcher(launcher_path, dbp, packed_out, bedrock_name=f"{name}_{DEFAULT_DB_NAME}")
            self.log_pack.appendPlainText(f"✅ Packed: {packed_out}")
        except Exception as e:
            self.log_pack.appendPlainText(f"❌ Pack failed: {e}")

    def build_exe(self):
        if not self.cb_enable_exe.isChecked():
            self.log_pack.appendPlainText("EXE pipeline disabled.")
            return
        name = self.need_active()
        if not name: return
        proj_dir = self.project_dir(name)
        packed = proj_dir / (self.le_packed.text().strip() or PACKED_NAME)
        if not packed.exists():
            self.log_pack.appendPlainText("ℹ️ Packed launcher missing; packing now…")
            self.pack_launcher()
        icon = Path(self.le_icon.text().strip())
        exe_name = self.le_exe_name.text().strip() or DEFAULT_EXE_NAME
        try:
            run_pyinstaller(entry=packed, dist_dir=DIST_DIR, icon_path=icon if icon.exists() else None,
                            exe_name=exe_name, cwd=proj_dir, log_cb=self.log_pack.appendPlainText)
            self.log_pack.appendPlainText(f"✅ EXE built in: {DIST_DIR}")
        except Exception as e:
            self.log_pack.appendPlainText(f"❌ EXE build failed: {e}")

# --------------------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    dark(app)
    ui = CompilerUI()
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

**Classes:** CompilerUI
**Functions:** ensure_dirs(), run_sql_script(db_path, sql_text), create_host_from_loader_or_builtin(db_path), inject_cell(db_path, name, code, immutable, parent, pos, size), add_bucket(db_path, name, purpose, schema_json, mutable), verify_host(db_path), vacuum_db(db_path), make_packed_launcher(launcher_src_path, bedrock_db_path, out_path, bedrock_name), have_pyinstaller(), run_pyinstaller(entry, dist_dir, icon_path, exe_name, cwd, log_cb), dark(app), ts(), main()


## Module `Backups\ant_launcher.py`

```python
#!/usr/bin/env python3
# ant_launcher_qt.py
#
# PyQt5 Project Launcher for the Autonomous SQL ecosystem.
# - Dark retro theme
# - Bedrock manager ("Add Custom Schema"): drag & drop, browse, paste path
# - Bedrocks stored per-user under a config directory; selectable via dropdown
# - New Project clones selected bedrock and writes project meta into the SQL
# - Launch Immune System: loads `immune_system` code from the project SQL and runs it with system Python
# - Open Project SQL, Open Folder, Delete Project SQL (with confirm)
#
# IMPORTANT when building:
#   Include an embedded bedrock at assets/bedrock.sql in the EXE using PyInstaller:
#     --add-data "assets/bedrock.sql:assets/bedrock.sql"
#   This launcher will auto-register that embedded bedrock on first run.
#
# Requires: PyQt5
# Optional: System Python 3.11+ for launching the immune system code
#
# Usage:
#   python ant_launcher_qt.py

import os
import sys
import json
import sqlite3
import shutil
import hashlib
import tempfile
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

# ---- Qt ----
from PyQt5 import QtCore, QtGui, QtWidgets

APP_TITLE = "ANT Project Launcher"
ORG_NAME  = "ANT"
APP_NAME  = "ANTLauncher"

# Embedded bedrock path (inside PyInstaller bundle)
EMBED_BEDROCK_REL = "assets/bedrock.sql"

# Per-user config/storage (~/.config/ANT/ANTLauncher or %APPDATA%\ANT\ANTLauncher)
def config_root() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / ORG_NAME / APP_NAME

def bedrocks_dir() -> Path:
    return config_root() / "bedrocks"

def manifest_path() -> Path:
    return config_root() / "bedrocks.json"

def projects_manifest_path() -> Path:
    # optional list of recent projects (non-authoritative; projects live as .db files)
    return config_root() / "projects.json"

# ---------- Utility ----------

def ensure_dirs():
    config_root().mkdir(parents=True, exist_ok=True)
    bedrocks_dir().mkdir(parents=True, exist_ok=True)

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def resource_path(rel: str) -> Path:
    """Find resource both in development and PyInstaller onefile."""
    if hasattr(sys, "_MEIPASS"):
        p = Path(sys._MEIPASS) / rel
        if p.exists():
            return p
    return Path(__file__).parent / rel

def read_manifest() -> dict:
    p = manifest_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"bedrocks": [], "default": None}

def write_manifest(m: dict):
    manifest_path().write_text(json.dumps(m, indent=2), encoding="utf-8")

def read_projects_manifest() -> dict:
    p = projects_manifest_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"projects": []}

def write_projects_manifest(m: dict):
    projects_manifest_path().write_text(json.dumps(m, indent=2), encoding="utf-8")

def system_python_candidates() -> List[str]:
    names = ["python", "python3", "python3.11", "python3.10", "python3.9"]
    cand = []
    for n in names:
        found = shutil.which(n)
        if found and found not in cand:
            cand.append(found)
    if os.name == "nt":
        py = shutil.which("py")
        if py:
            cand.append(py)  # special handling later
    return cand

def ensure_valid_bedrock(path: Path) -> Tuple[bool, str]:
    """Light validation: must contain required tables and immune_system + cell_0 in cells."""
    if not path.exists():
        return False, "File not found."
    try:
        conn = sqlite3.connect(str(path))
        cur = conn.cursor()
        # required tables
        for t in ("cells", "meta"):
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,))
            if not cur.fetchone():
                conn.close()
                return False, f"Missing required table: {t}"
        # required cells
        cur.execute("SELECT COUNT(*) FROM cells WHERE name='immune_system'")
        if cur.fetchone()[0] < 1:
            conn.close()
            return False, "Missing 'immune_system' cell in bedrock."
        cur.execute("SELECT COUNT(*) FROM cells WHERE name='cell_0'")
        if cur.fetchone()[0] < 1:
            conn.close()
            return False, "Missing 'cell_0' bedrock cell."
        conn.close()
        return True, "ok"
    except Exception as e:
        return False, str(e)

def clone_bedrock(src_bedrock: Path, dest_project: Path, project_name: str):
    dest_project.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src_bedrock), str(dest_project))
    # stamp meta
    conn = sqlite3.connect(str(dest_project))
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    meta = {
        "project_id": hashlib.sha1(f"{project_name}-{datetime.utcnow().isoformat()}".encode()).hexdigest(),
        "project_name": project_name,
        "created_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "bedrock_checksum": sha256_file(src_bedrock),
        "bedrock_source": str(src_bedrock),
    }
    for k, v in meta.items():
        cur.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (k, str(v)))
    conn.commit()
    conn.close()

def read_immune_code(db_path: Path) -> str:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT code FROM cells WHERE name='immune_system' LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row or not row[0]:
        raise RuntimeError("No immune_system code found in this project.")
    return row[0]

# ---------- Theming (dark retro) ----------

def apply_dark_retro_theme(app: QtWidgets.QApplication):
    # Base dark palette
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, QtGui.QColor(18, 18, 18))
    pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Base, QtGui.QColor(12, 12, 12))
    pal.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(24, 24, 24))
    pal.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Button, QtGui.QColor(24, 24, 24))
    pal.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(60, 180, 120))
    pal.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(pal)

    # Retro-ish stylesheet
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMainWindow, QWidget { font-family: 'JetBrains Mono', 'Consolas', 'Menlo', monospace; font-size: 12px; color: #eaeaea; }
        QToolBar { spacing: 6px; border: 0; background: #141414; }
        QToolButton { padding: 6px 10px; border: 1px solid #2a2a2a; border-radius: 4px; background: #1b1b1b; }
        QToolButton:hover { background: #222; }
        QPushButton { padding: 6px 12px; border: 1px solid #2d2d2d; border-radius: 4px; background: #1c1c1c; }
        QPushButton:hover { background: #232323; }
        QLineEdit, QPlainTextEdit, QComboBox, QSpinBox { padding: 6px; border: 1px solid #303030; border-radius: 4px; background: #151515; selection-background-color: #3cb878; selection-color: black;}
        QHeaderView::section { background-color: #1c1c1c; padding: 6px; border: none; }
        QTableWidget { gridline-color: #2a2a2a; }
        QMenu { background-color: #121212; border: 1px solid #2a2a2a; }
        QMenu::item:selected { background-color: #3cb878; color: black; }
        QStatusBar { background: #141414; }
        QGroupBox { border: 1px solid #2a2a2a; margin-top: 12px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 4px 8px; }
    """)

# ---------- Widgets ----------

class DropBox(QtWidgets.QLabel):
    """Drop target for importing a Bedrock SQL."""
    fileDropped = QtCore.pyqtSignal(str)

    def __init__(self, text="Drop .db here"):
        super().__init__(text)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setStyleSheet("QLabel { border: 2px dashed #3cb878; border-radius: 8px; padding: 12px; }")

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent):
        if e.mimeData().hasUrls():
            for u in e.mimeData().urls():
                if u.toLocalFile().lower().endswith((".db", ".sqlite", ".sqlite3")):
                    e.acceptProposedAction()
                    return
        e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent):
        for u in e.mimeData().urls():
            p = u.toLocalFile()
            if p.lower().endswith((".db", ".sqlite", ".sqlite3")):
                self.fileDropped.emit(p)
                return

class AddBedrockDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom Schema (Bedrock SQL)")
        self.resize(520, 360)

        lay = QtWidgets.QVBoxLayout(self)

        self.drop = DropBox("Drop a Bedrock SQL (.db) here")
        self.drop.fileDropped.connect(self.on_dropped)
        lay.addWidget(self.drop)

        form = QtWidgets.QFormLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Display name (e.g., Bedrock v1)")
        form.addRow("File path:", self.path_edit)
        form.addRow("Display name:", self.name_edit)
        lay.addLayout(form)

        btns = QtWidgets.QHBoxLayout()
        self.btn_browse = QtWidgets.QPushButton("Browse…")
        self.btn_browse.clicked.connect(self.browse)
        self.btn_paste = QtWidgets.QPushButton("Paste Path")
        self.btn_paste.clicked.connect(self.paste_path)
        btns.addWidget(self.btn_browse)
        btns.addWidget(self.btn_paste)
        lay.addLayout(btns)

        self.default_check = QtWidgets.QCheckBox("Mark as default bedrock")
        lay.addWidget(self.default_check)

        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def on_dropped(self, path: str):
        self.path_edit.setText(path)
        if not self.name_edit.text().strip():
            self.name_edit.setText(Path(path).stem)

    def browse(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Bedrock SQL", "", "SQLite (*.db *.sqlite *.sqlite3);;All Files (*)")
        if p:
            self.path_edit.setText(p)
            if not self.name_edit.text().strip():
                self.name_edit.setText(Path(p).stem)

    def paste_path(self):
        cb = QtWidgets.QApplication.clipboard().text().strip()
        if cb:
            self.path_edit.setText(cb)
            if not self.name_edit.text().strip():
                self.name_edit.setText(Path(cb).stem)

    def get_values(self) -> Tuple[str, str, bool]:
        return self.path_edit.text().strip(), self.name_edit.text().strip(), self.default_check.isChecked()

# ---------- Main Window ----------

class LauncherWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1200, 760)

        ensure_dirs()

        # Menu
        self._make_menu()

        # Toolbar
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setMovable(False)
        self._make_toolbar()

        # Central widgets: projects table + status/log
        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(central)

        top_row = QtWidgets.QHBoxLayout()
        self.bedrock_combo = QtWidgets.QComboBox()
        self.btn_manage_bedrocks = QtWidgets.QPushButton("Add Custom Schema")
        self.btn_manage_bedrocks.clicked.connect(self.add_custom_schema)
        top_row.addWidget(QtWidgets.QLabel("Clone from:"))
        top_row.addWidget(self.bedrock_combo, 1)
        top_row.addWidget(self.btn_manage_bedrocks)
        v.addLayout(top_row)

        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Project", "Location"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        v.addWidget(self.table, 1)

        self.setCentralWidget(central)

        # Status bar
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)

        # Buttons row
        row = QtWidgets.QHBoxLayout()
        self.btn_new = QtWidgets.QPushButton("New Project")
        self.btn_open = QtWidgets.QPushButton("Open Project SQL")
        self.btn_launch = QtWidgets.QPushButton("Launch Immune System")
        self.btn_folder = QtWidgets.QPushButton("Open Folder")
        self.btn_delete = QtWidgets.QPushButton("Delete Project SQL")

        self.btn_new.clicked.connect(self.new_project)
        self.btn_open.clicked.connect(self.open_project_sql)
        self.btn_launch.clicked.connect(self.launch_immune)
        self.btn_folder.clicked.connect(self.open_folder)
        self.btn_delete.clicked.connect(self.delete_project)

        row.addWidget(self.btn_new)
        row.addWidget(self.btn_open)
        row.addStretch(1)
        row.addWidget(self.btn_folder)
        row.addWidget(self.btn_delete)
        row.addWidget(self.btn_launch)

        v.addLayout(row)

        # Load manifests and auto-register embedded bedrock if present
        self.manifest = read_manifest()
        self.projects = read_projects_manifest()
        self.autoregister_embedded_bedrock()
        self.refresh_bedrock_combo()
        self.refresh_projects_table()

    # ---- UI construction helpers ----
    def _make_menu(self):
        mbar = self.menuBar()
        m_file = mbar.addMenu("&File")
        act_quit = QtWidgets.QAction("Quit", self)
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_help = mbar.addMenu("&Help")
        act_about = QtWidgets.QAction("About", self)
        act_about.triggered.connect(self.about)
        m_help.addAction(act_about)

    def _make_toolbar(self):
        a_new = QtWidgets.QAction("New Project", self)
        a_new.triggered.connect(self.new_project)
        self.toolbar.addAction(a_new)

        a_open = QtWidgets.QAction("Open Project SQL", self)
        a_open.triggered.connect(self.open_project_sql)
        self.toolbar.addAction(a_open)

        a_launch = QtWidgets.QAction("Launch Immune System", self)
        a_launch.triggered.connect(self.launch_immune)
        self.toolbar.addAction(a_launch)

        a_addschema = QtWidgets.QAction("Add Custom Schema", self)
        a_addschema.triggered.connect(self.add_custom_schema)
        self.toolbar.addAction(a_addschema)

    # ---- core features ----

    def about(self):
        QtWidgets.QMessageBox.information(self, "About", "ANT Project Launcher\nPyQt5 • Dark Retro Theme\nManages Bedrock SQLs and Projects.")

    def autoregister_embedded_bedrock(self):
        # Only once: if we find an embedded bedrock and it's not already registered, copy to bedrocks dir.
        try:
            # PyInstaller MEIPASS first
            if hasattr(sys, "_MEIPASS"):
                embedded = Path(sys._MEIPASS) / EMBED_BEDROCK_REL
            else:
                embedded = resource_path(EMBED_BEDROCK_REL)
            if embedded.exists():
                chk = sha256_file(embedded)
                # Is this checksum already registered?
                if not any(br.get("checksum") == chk for br in self.manifest["bedrocks"]):
                    dest = bedrocks_dir() / f"bedrock_{chk[:8]}.db"
                    shutil.copy2(str(embedded), str(dest))
                    self.manifest["bedrocks"].append({
                        "name": "Embedded Bedrock",
                        "path": str(dest),
                        "checksum": chk,
                        "added_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                    })
                    if not self.manifest.get("default"):
                        self.manifest["default"] = str(dest)
                    write_manifest(self.manifest)
        except Exception:
            # non-fatal
            pass

    def refresh_bedrock_combo(self):
        self.bedrock_combo.clear()
        # Remove bedrocks that disappeared
        self.manifest["bedrocks"] = [br for br in self.manifest["bedrocks"] if Path(br["path"]).exists()]
        write_manifest(self.manifest)

        for br in self.manifest["bedrocks"]:
            label = f'{br["name"]}  —  {Path(br["path"]).name}'
            self.bedrock_combo.addItem(label, br["path"])

        # Select default
        if self.manifest.get("default"):
            idx = self.bedrock_combo.findData(self.manifest["default"])
            if idx >= 0:
                self.bedrock_combo.setCurrentIndex(idx)

    def add_custom_schema(self):
        dlg = AddBedrockDialog(self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        path_str, name, make_default = dlg.get_values()
        if not path_str or not name:
            QtWidgets.QMessageBox.warning(self, "Missing", "Provide both file path and display name.")
            return
        src = Path(path_str).resolve()
        ok, msg = ensure_valid_bedrock(src)
        if not ok:
            QtWidgets.QMessageBox.critical(self, "Invalid Bedrock", msg)
            return
        ensure_dirs()
        chk = sha256_file(src)
        dest = bedrocks_dir() / f"{name}_{chk[:8]}.db"
        shutil.copy2(str(src), str(dest))
        # register
        self.manifest["bedrocks"].append({
            "name": name,
            "path": str(dest),
            "checksum": chk,
            "added_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        if make_default or not self.manifest.get("default"):
            self.manifest["default"] = str(dest)
        write_manifest(self.manifest)
        self.refresh_bedrock_combo()
        QtWidgets.QMessageBox.information(self, "Added", f"Registered bedrock:\n{name}\n{dest}")

    def current_bedrock(self) -> Optional[Path]:
        if self.bedrock_combo.count() == 0:
            return None
        p = self.bedrock_combo.currentData()
        return Path(p) if p else None

    def new_project(self):
        br = self.current_bedrock()
        if not br:
            QtWidgets.QMessageBox.warning(self, "No Bedrock", "Add a Bedrock SQL first via 'Add Custom Schema'.")
            return

        # Ask for project name
        name, ok = QtWidgets.QInputDialog.getText(self, "New Project", "Project name:")
        if not ok or not name.strip():
            return
        name = "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in name.strip())
        default_filename = f"{name}.db"
        # Where to save
        dest, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Project SQL", default_filename,
                                                        "SQLite (*.db *.sqlite *.sqlite3);;All Files (*)")
        if not dest:
            return
        dest_path = Path(dest).resolve()

        try:
            clone_bedrock(br, dest_path, name)
            self.add_project_row(name, str(dest_path))
            self.remember_project(name, str(dest_path))
            self.status.showMessage(f"Created project: {dest_path.name}", 5000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Create Error", str(e))

    def open_project_sql(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Project SQL", "",
                                                     "SQLite (*.db *.sqlite *.sqlite3);;All Files (*)")
        if not p:
            return
        path = Path(p).resolve()
        # Basic validation
        try:
            conn = sqlite3.connect(str(path))
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cells'")
            ok = cur.fetchone() is not None
            conn.close()
            if not ok:
                QtWidgets.QMessageBox.critical(self, "Invalid", "Missing 'cells' table.")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            return

        # Derive name from meta or filename
        name = path.stem
        try:
            conn = sqlite3.connect(str(path))
            cur = conn.cursor()
            cur.execute("SELECT value FROM meta WHERE key='project_name'")
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                name = row[0]
        except Exception:
            pass

        self.add_project_row(name, str(path))
        self.remember_project(name, str(path))

    def selected_project(self) -> Optional[Tuple[int, str, str]]:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        r = rows[0].row()
        name = self.table.item(r, 0).text()
        path = self.table.item(r, 1).text()
        return r, name, path

    def add_project_row(self, name: str, path: str):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(path))

    def remember_project(self, name: str, path: str):
        pj = self.projects
        if not any(p["path"] == path for p in pj["projects"]):
            pj["projects"].append({"name": name, "path": path, "added_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
            write_projects_manifest(pj)

    def refresh_projects_table(self):
        self.table.setRowCount(0)
        pj = read_projects_manifest()
        self.projects = pj
        for p in pj["projects"]:
            if Path(p["path"]).exists():
                self.add_project_row(p["name"], p["path"])

    def open_folder(self):
        sel = self.selected_project()
        if not sel:
            QtWidgets.QMessageBox.information(self, "Open Folder", "Select a project first.")
            return
        _, _, path = sel
        folder = Path(path).parent
        try:
            if os.name == "nt":
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder)])
            else:
                subprocess.run(["xdg-open", str(folder)])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Open Error", str(e))

    def delete_project(self):
        sel = self.selected_project()
        if not sel:
            QtWidgets.QMessageBox.information(self, "Delete", "Select a project first.")
            return
        row, name, path = sel
        resp = QtWidgets.QMessageBox.question(self, "Delete Project SQL",
                                              f"Delete this project file?\n\n{name}\n{path}\n\nThis cannot be undone.",
                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if resp != QtWidgets.QMessageBox.Yes:
            return
        try:
            Path(path).unlink(missing_ok=True)
            self.table.removeRow(row)
            # remove from manifest
            pj = read_projects_manifest()
            pj["projects"] = [p for p in pj["projects"] if p["path"] != path]
            write_projects_manifest(pj)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Delete Error", str(e))

    def launch_immune(self):
        sel = self.selected_project()
        if not sel:
            QtWidgets.QMessageBox.information(self, "Launch", "Select a project first.")
            return
        _, name, path = sel
        db_path = Path(path).resolve()
        if not db_path.exists():
            QtWidgets.QMessageBox.critical(self, "Missing", f"File not found:\n{db_path}")
            return
        # Extract immune code to temp and run with system Python
        try:
            code = read_immune_code(db_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Reading immune_system failed:\n{e}")
            return

        py_list = system_python_candidates()
        if not py_list:
            QtWidgets.QMessageBox.critical(self, "Python Missing", "No system Python found on PATH. Install Python 3.11+.")
            return
        py = py_list[0]

        with tempfile.TemporaryDirectory() as td:
            script = Path(td) / "immune_system_run.py"
            script.write_text(code, encoding="utf-8")
            env = os.environ.copy()
            env["SINGLECELL_DB"] = str(db_path)

            if os.name == "nt" and os.path.basename(py).lower() == "py.exe":
                cmd = [py, "-3", str(script)]
            else:
                cmd = [py, str(script)]

            try:
                # Detach so the launcher stays usable
                if os.name == "nt":
                    subprocess.Popen(cmd, env=env, creationflags=0x00000010)  # CREATE_NEW_CONSOLE
                else:
                    subprocess.Popen(cmd, env=env, start_new_session=True)
                self.status.showMessage(f"Launched Immune System for {name}", 5000)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Launch Error", str(e))

# ---------- main ----------

def main():
    app = QtWidgets.QApplication(sys.argv)
    apply_dark_retro_theme(app)

    win = LauncherWindow()
    win.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

**Classes:** DropBox, AddBedrockDialog, LauncherWindow
**Functions:** config_root(), bedrocks_dir(), manifest_path(), projects_manifest_path(), ensure_dirs(), sha256_file(p), resource_path(rel), read_manifest(), write_manifest(m), read_projects_manifest(), write_projects_manifest(m), system_python_candidates(), ensure_valid_bedrock(path), clone_bedrock(src_bedrock, dest_project, project_name), read_immune_code(db_path), apply_dark_retro_theme(app), main()


## Module `Backups\cell_1.py`

```python
# cell_1.py
# Active clone with ANTapi wrapping, GUI, self-edit, versioned updates, spawn requests,
# protein listener, bucket I/O, and self-heal hooks.
#
# Contract required by Immune System:
#   - build_gui(api) -> QWidget
#   - core_behavior(api) -> dict

import ast
import difflib
import json
import re
import threading
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------
# ANT Membrane (local wrapper)
# -----------------------------

class ANT:
    """
    Local membrane that wraps the provided `api` from the Immune System and
    exposes higher-level helpers used by this cell. We keep it self-contained
    so cells can evolve the membrane without changing the host.
    """
    # Default policy fallback (will try to read the canonical one from antapi table)
    DEFAULT_ALLOWED_IMPORTS = {"json", "time", "math", "random", "re", "ast", "difflib", "traceback", "threading"}

    def __init__(self, api):
        self.api = api                 # Immune System ANTApi
        self.db = getattr(api, "db", None)
        self.name = getattr(api, "cell", "cell_1")
        self._allowed_imports = set(self.DEFAULT_ALLOWED_IMPORTS)
        self._load_allowed_imports_from_host()

    # ---- Policy & Safety ----
    def _load_allowed_imports_from_host(self):
        try:
            if not self.db:
                return
            c = self.db.connect()
            x = c.cursor()
            x.execute("SELECT code FROM antapi WHERE name='policy' ORDER BY id DESC LIMIT 1")
            r = x.fetchone()
            c.close()
            if not r: 
                return
            code = r[0]
            # crude parse: look for ALLOWED_IMPORTS = {...}
            m = re.search(r"ALLOWED_IMPORTS\s*=\s*\{([^}]*)\}", code)
            if m:
                inner = m.group(1)
                items = re.findall(r"['\"]([^'\"]+)['\"]", inner)
                if items:
                    self._allowed_imports = set(items)
        except Exception:
            # fall back to defaults if anything goes wrong
            pass

    def guard(self, fn):
        """Decorator to catch exceptions and log to host."""
        def wrapped(*a, **kw):
            t0 = time.time()
            try:
                return fn(*a, **kw)
            except Exception as e:
                tb = traceback.format_exc()
                self.api.log("ERROR", f"{fn.__name__} error: {e}")
                # mirror into errors table
                try:
                    c = self.db.connect(); x = c.cursor()
                    x.execute("SELECT version FROM cells WHERE name=?", (self.name,))
                    r = x.fetchone(); ver = r[0] if r else None
                    x.execute("INSERT INTO errors(cell_name, version, traceback, context_json) VALUES(?,?,?,?)",
                              (self.name, ver, tb, json.dumps({"op": fn.__name__})))
                    c.commit(); c.close()
                except Exception:
                    pass
                return None
            finally:
                dt = int((time.time() - t0) * 1000)
                self.api.log("DEBUG", f"{fn.__name__} dt={dt}ms")
        return wrapped

    # ---- DB helpers ----
    def get_cell_row(self, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        name = name or self.name
        c = self.db.connect(); x = c.cursor()
        x.execute("SELECT * FROM cells WHERE name=?", (name,))
        r = x.fetchone()
        c.close()
        return dict(r) if r else None

    def get_current_code(self, name: Optional[str] = None) -> Optional[str]:
        row = self.get_cell_row(name)
        return row["code"] if row else None

    def get_version(self, name: Optional[str] = None) -> int:
        row = self.get_cell_row(name)
        return int(row["version"]) if row else 0

    def is_immutable(self, name: Optional[str] = None) -> bool:
        row = self.get_cell_row(name)
        return bool(row["immutable"]) if row else False

    def update_metadata(self, updates: Dict[str, Any], name: Optional[str] = None) -> None:
        name = name or self.name
        c = self.db.connect(); x = c.cursor()
        x.execute("SELECT metadata_json FROM cells WHERE name=?", (name,))
        r = x.fetchone()
        meta = {}
        if r and r[0]:
            try:
                meta = json.loads(r[0])
            except Exception:
                meta = {}
        # deep-merge shallowly
        meta.update(updates)
        x.execute("UPDATE cells SET metadata_json=? WHERE name=?", (json.dumps(meta), name))
        c.commit(); c.close()

    # ---- Buckets ----
    def bucket_put(self, bucket: str, key: str, value: Dict[str, Any]) -> None:
        c = self.db.connect(); x = c.cursor()
        x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name, key, value_json) VALUES(?,?,?)",
                  (bucket, key, json.dumps(value)))
        c.commit(); c.close()

    def bucket_get(self, bucket: str, key: str) -> Optional[Dict[str, Any]]:
        c = self.db.connect(); x = c.cursor()
        x.execute("SELECT value_json FROM bucket_items WHERE bucket_name=? AND key=?", (bucket, key))
        r = x.fetchone(); c.close()
        if not r: return None
        try: return json.loads(r[0])
        except Exception: return None

    # ---- Signals (read + emit) ----
    def get_signals_since(self, last_id: int = 0, kinds: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        kinds = kinds or []
        c = self.db.connect(); x = c.cursor()
        if kinds:
            q = f"""
                SELECT * FROM signals
                WHERE id > ? AND (to_cell IS NULL OR to_cell = ?) AND kind IN ({','.join('?'*len(kinds))})
                ORDER BY id ASC
            """
            params = [last_id, self.name] + kinds
        else:
            q = """
                SELECT * FROM signals
                WHERE id > ? AND (to_cell IS NULL OR to_cell = ?)
                ORDER BY id ASC
            """
            params = [last_id, self.name]
        x.execute(q, params)
        rows = x.fetchall(); c.close()
        return [dict(r) for r in rows]

    # ---- Code / Policy ----
    def validate_code(self, code: str) -> Tuple[bool, str]:
        # syntax
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        # presence of required defs
        have_build = any(isinstance(n, ast.FunctionDef) and n.name == "build_gui" for n in tree.body)
        have_core  = any(isinstance(n, ast.FunctionDef) and n.name == "core_behavior" for n in tree.body)
        if not have_build or not have_core:
            return False, "Missing required functions: build_gui(api) and/or core_behavior(api)."
        # imports policy
        bad = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    mod = alias.name.split(".")[0]
                    if mod not in self._allowed_imports:
                        bad.append(mod)
            elif isinstance(n, ast.ImportFrom):
                mod = (n.module or "").split(".")[0]
                if mod and mod not in self._allowed_imports:
                    bad.append(mod)
        if bad:
            bad_set = sorted(set(bad))
            return False, f"Disallowed imports: {', '.join(bad_set)}"
        return True, "ok"

    def diff_text(self, old: str, new: str, context: int = 3) -> str:
        return "\n".join(difflib.unified_diff(
            old.splitlines(), new.splitlines(),
            fromfile="old", tofile="new", lineterm="", n=context
        ))

    def update_code_versioned(self, new_code: str, note: str = "") -> Tuple[bool, str]:
        if self.is_immutable():
            return False, "Cell is immutable."
        ok, msg = self.validate_code(new_code)
        if not ok: return False, msg
        old_code = self.get_current_code() or ""
        if old_code.strip() == new_code.strip():
            return False, "No changes."
        diff = self.diff_text(old_code, new_code)
        # perform DB update with monotonic version step
        c = self.db.connect(); x = c.cursor()
        x.execute("SELECT version FROM cells WHERE name=?", (self.name,))
        r = x.fetchone(); ver = int(r[0]) if r else 1
        try:
            x.execute("UPDATE cells SET code=?, version=? WHERE name=? AND immutable=0",
                      (new_code, ver + 1, self.name))
            x.execute("INSERT INTO diffs(cell_name, from_version, to_version, diff_type, diff_text) VALUES(?,?,?,?,?)",
                      (self.name, ver, ver + 1, "+diff", diff))
            self.api.log("INFO", f"Updated code v{ver}→v{ver+1}. {note or ''}".strip())
            c.commit()
        except Exception as e:
            c.rollback()
            self.api.log("ERROR", f"update_code_versioned failed: {e}")
            return False, str(e)
        finally:
            c.close()
        return True, f"Updated to v{ver+1}"

    def rollback_one(self) -> Tuple[bool, str]:
        if self.is_immutable():
            return False, "Cell is immutable."
        # fetch previous version
        c = self.db.connect(); x = c.cursor()
        x.execute("SELECT version FROM cells WHERE name=?", (self.name,))
        r = x.fetchone()
        if not r:
            c.close()
            return False, "No such cell."
        curv = int(r[0])
        if curv <= 1:
            c.close()
            return False, "Already at earliest version."
        x.execute("SELECT code FROM cell_versions WHERE cell_name=? AND version=?", (self.name, curv - 1))
        pr = x.fetchone()
        if not pr:
            c.close()
            return False, "Missing prior snapshot."
        prev_code = pr[0]
        try:
            x.execute("UPDATE cells SET code=?, version=? WHERE name=? AND immutable=0",
                      (prev_code, curv - 1, self.name))
            x.execute("INSERT INTO diffs(cell_name, from_version, to_version, diff_type, diff_text) VALUES(?,?,?,?,?)",
                      (self.name, curv, curv - 1, "-diff", "rollback"))
            c.commit()
            self.api.log("WARN", f"Rolled back to v{curv-1}")
            return True, f"Rolled back to v{curv-1}"
        except Exception as e:
            c.rollback()
            self.api.log("ERROR", f"rollback failed: {e}")
            return False, str(e)
        finally:
            c.close()

    def spawn_from_cell0(self, new_name: str, pos: Tuple[int, int] = (200, 0), size: Tuple[int, int] = (800, 800)) -> Tuple[bool, str]:
        # read template
        c = self.db.connect(); x = c.cursor()
        x.execute("SELECT code FROM cells WHERE name='cell_0'")
        r = x.fetchone()
        if not r:
            c.close()
            return False, "cell_0 template not found."
        code0 = r[0]
        meta = {"pos": {"x": pos[0], "y": pos[1]}, "size": {"w": size[0], "h": size[1]}, "role": "active"}
        try:
            x.execute("INSERT INTO cells(name, parent_id, cluster_id, immutable, code, metadata_json, version) VALUES (?, NULL, NULL, 0, ?, ?, 1)",
                      (new_name, code0, json.dumps(meta)))
            x.execute("INSERT INTO cell_versions(cell_name, version, code) VALUES (?,?,?)", (new_name, 1, code0))
            c.commit()
            self.api.log("INFO", f"Spawned {new_name} from cell_0")
            return True, f"Spawned {new_name}"
        except Exception as e:
            c.rollback()
            return False, f"spawn failed: {e}"
        finally:
            c.close()

    # ---- Code segmentation into bucket 'code_parts' ----
    def extract_code_parts(self, code: str) -> Dict[str, Any]:
        parts = []
        # imports
        for m in re.finditer(r"^(?:from\s+[^\n]+|import\s+[^\n]+)$", code, flags=re.MULTILINE):
            txt = m.group(0)
            parts.append({"kind": "import", "name": txt.split()[1], "text": txt})
        # functions
        for m in re.finditer(r"^(def\s+[a-zA-Z_][\w]*\s*\([^\)]*\)\s*:[\s\S]*?)(?=^\S|\Z)", code, flags=re.MULTILINE):
            hdr = m.group(1).splitlines()[0]
            name = re.search(r"def\s+([a-zA-Z_]\w*)", hdr).group(1)
            parts.append({"kind": "function", "name": name, "text": m.group(1)})
        # classes
        for m in re.finditer(r"^(class\s+[A-Za-z_]\w*\s*(?:\([^\)]*\))?\s*:[\s\S]*?)(?=^\S|\Z)", code, flags=re.MULTILINE):
            hdr = m.group(1).splitlines()[0]
            name = re.search(r"class\s+([A-Za-z_]\w*)", hdr).group(1)
            parts.append({"kind": "class", "name": name, "text": m.group(1)})
        return {"cell": self.name, "segments": parts}

# -----------------------------
# PyQt5 UI (cell widget)
# -----------------------------

def _make_stylesheet() -> str:
    # light touch; Immune System already sets a dark palette
    return """
    QWidget { font-size: 12px; }
    QPlainTextEdit, QTextEdit { background:#121212; color:#e6e6e6; border:1px solid #2b2b2b; }
    QPushButton { padding:6px 10px; }
    QLabel.header { font-weight:bold; font-size:14px; }
    """

class _CellWidget:
    """
    Encapsulates the Qt widget and behavior so we can unit-test logic separately.
    """
    def __init__(self, api):
        from PyQt5 import QtWidgets, QtCore
        self.api = api
        self.ant = ANT(api)
        self.QtWidgets = QtWidgets
        self.QtCore = QtCore

        self.root = QtWidgets.QWidget()
        self.root.setStyleSheet(_make_stylesheet())
        self.v = QtWidgets.QVBoxLayout(self.root)

        title = QtWidgets.QLabel(f"{self.ant.name} — active")
        title.setObjectName("title"); title.setProperty("class", "header")
        title.setStyleSheet("font-weight:bold; font-size:16px;")
        self.v.addWidget(title)

        # status bar
        self.status = QtWidgets.QLabel("ready")
        self.v.addWidget(self.status)

        # editor
        self.editor = QtWidgets.QPlainTextEdit()
        self.editor.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.v.addWidget(self.editor, 1)

        # buttons
        row = QtWidgets.QHBoxLayout()
        self.btn_load = QtWidgets.QPushButton("Load From Host")
        self.btn_analyze = QtWidgets.QPushButton("Analyze")
        self.btn_propose = QtWidgets.QPushButton("Propose Update")
        self.btn_rollback = QtWidgets.QPushButton("Rollback One")
        self.btn_spawn = QtWidgets.QPushButton("Spawn Helper")
        self.btn_listen = QtWidgets.QPushButton("Listen Proteins")
        self.btn_announce = QtWidgets.QPushButton("Announce")
        for b in (self.btn_load, self.btn_analyze, self.btn_propose, self.btn_rollback, self.btn_spawn, self.btn_listen, self.btn_announce):
            row.addWidget(b)
        self.v.addLayout(row)

        # output pane
        self.out = QtWidgets.QPlainTextEdit()
        self.out.setReadOnly(True)
        self.v.addWidget(self.out, 1)

        # wire up
        self.btn_load.clicked.connect(self._on_load)
        self.btn_analyze.clicked.connect(self._on_analyze)
        self.btn_propose.clicked.connect(self._on_propose)
        self.btn_rollback.clicked.connect(self._on_rollback)
        self.btn_spawn.clicked.connect(self._on_spawn)
        self.btn_listen.clicked.connect(self._on_listen)
        self.btn_announce.clicked.connect(self._on_announce)

        # initial load
        self._on_load()

        # background signal poller (off by default; enabled via Listen Proteins)
        self._listen_flag = False
        self._signal_last_id = 0
        self._poll_timer = QtCore.QTimer(self.root)
        self._poll_timer.setInterval(1500)
        self._poll_timer.timeout.connect(self._poll_signals)

    # ---- UI actions ----
    def _log(self, text: str):
        self.out.appendPlainText(text)
        self.api.log("INFO", text)

    def _on_load(self):
        code = self.ant.get_current_code() or ""
        ver = self.ant.get_version()
        imm = self.ant.is_immutable()
        self.editor.setPlainText(code)
        self.status.setText(f"Loaded v{ver} | immutable={'yes' if imm else 'no'}")
        self._log(f"Loaded code v{ver}")

    def _on_analyze(self):
        code = self.editor.toPlainText()
        ok, msg = self.ant.validate_code(code)
        parts = self.ant.extract_code_parts(code)
        self.ant.bucket_put("code_parts", f"{self.ant.name}@v{self.ant.get_version()}",
                            {"cell": parts["cell"], "segments": parts["segments"]})
        if ok:
            self._log(f"Analysis OK: {msg}. Saved parts to bucket 'code_parts'.")
        else:
            self._log(f"Analysis FAILED: {msg}")

    def _on_propose(self):
        code = self.editor.toPlainText()
        ok, res = self.ant.update_code_versioned(code, note="via cell GUI")
        if ok:
            self.status.setText(res)
            self._log(res)
        else:
            self.status.setText(f"Update failed: {res}")
            self._log(f"Update failed: {res}")

    def _on_rollback(self):
        ok, res = self.ant.rollback_one()
        self.status.setText(res)
        self._log(res)
        if ok:
            # reload into editor
            self._on_load()

    def _on_spawn(self):
        from PyQt5 import QtWidgets
        name, ok = QtWidgets.QInputDialog.getText(self.root, "Spawn Helper", "New cell name:")
        if not ok or not name.strip():
            return
        name = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name.strip())
        ok, res = self.ant.spawn_from_cell0(name)
        self._log(res)

    def _on_listen(self):
        self._listen_flag = not self._listen_flag
        if self._listen_flag:
            self._poll_timer.start()
            self._log("Protein listening: ON")
            self.btn_listen.setText("Stop Listening")
        else:
            self._poll_timer.stop()
            self._log("Protein listening: OFF")
            self.btn_listen.setText("Listen Proteins")

    def _on_announce(self):
        self.api.emit("status", {"msg": f"{self.ant.name} online"})
        self._log("Announced status.")

    # ---- Signal handling ----
    def _poll_signals(self):
        try:
            sigs = self.ant.get_signals_since(self._signal_last_id, kinds=["protein"])
            for s in sigs:
                self._signal_last_id = max(self._signal_last_id, int(s["id"]))
                payload = json.loads(s["payload_json"] or "{}")
                text = payload.get("text", "")
                self._log(f"Protein: {text}")
                self._handle_protein(text)
        except Exception as e:
            self._log(f"signal poll error: {e}")

    def _handle_protein(self, text: str):
        t = text.strip().lower()
        if not t:
            return
        # simple intent parser
        if t.startswith("self-heal") or "repair" in t:
            self._self_heal()
        elif t.startswith("spawn "):
            name = re.sub(r"^spawn\s+", "", t).strip()
            if name:
                ok, res = self.ant.spawn_from_cell0(name)
                self._log(res)
        elif t.startswith("update now"):
            # attempt to re-apply what's in editor
            self._on_propose()
        # extend with more intents as needed

    def _self_heal(self):
        """
        Naive self-heal: if current code fails validation, try to rollback one version.
        Otherwise, simply log a heartbeat and stash a summary.
        """
        code = self.editor.toPlainText()
        ok, msg = self.ant.validate_code(code)
        if not ok:
            self._log(f"Self-heal: validation failed: {msg}; attempting rollback.")
            ok2, res = self.ant.rollback_one()
            self._log(f"Self-heal rollback: {res}")
        else:
            self.api.remember(f"{self.ant.name} self-heal check OK", {"kind": "self_heal"})

# -----------------------------
# Required entry points
# -----------------------------

def build_gui(api):
    """
    Return a Qt widget representing this cell. The Immune System will embed this
    on its canvas and manage positioning/snap grid.
    """
    from PyQt5 import QtWidgets
    ui = _CellWidget(api)
    return ui.root

def core_behavior(api):
    """
    Lightweight heartbeat that can be invoked by the Immune System.
    It performs a single quick pass (no long loops).
    """
    ant = ANT(api)
    api.log("INFO", "cell_1 heartbeat")
    # Example: drop a tiny knowledge breadcrumb
    api.remember("cell_1 heartbeat", {"tick": "ok"})
    # Optionally inspect recent proteins once (non-blocking)
    try:
        sigs = ant.get_signals_since(0, kinds=["protein"])
        if sigs:
            api.log("INFO", f"core_behavior saw {len(sigs)} proteins (latest id={sigs[-1]['id']})")
    except Exception as e:
        api.log("ERROR", f"core_behavior signals error: {e}")
    return {"ok": True}
```

**Classes:** ANT, _CellWidget
**Functions:** _make_stylesheet(), build_gui(api), core_behavior(api)


## Module `Backups\immune_system.py`

```python
#!/usr/bin/env python3
# immune_system.py
# ANT Immune System (standalone + embeddable)
# - Zoomable canvas with invisible snap grid
# - Non-overlap spawn with one-grid spacing for unmerged cells
# - Merge/Unmerge (horizontal or vertical composite)
# - Cells list + Inspector (code editor, Save, Run behavior, Rollback)
# - Global Log (no forced autoscroll)
# - Host SQL Browser (preview + read-only SELECT)
# - Protein injector (broadcast or targeted)
# - Add Bucket (hardcoded templates; agents can add their own later)
# - Position persistence in cells.metadata_json
# - Safe AST validation & policy-aware import checks
#
# Standalone usage:
#   python immune_system.py [host.db]
#
# Env var alternative:
#   SINGLECELL_DB=/path/to/host.db python immune_system.py
#
# Embedding: this same file can be stored in the host's `cells` table as `immune_system`
# and used as the authoritative UI code for self-evolution.

import os, sys, json, sqlite3, traceback, time, ast, types, re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets

APP_NAME = "ANT Immune System"
GRID_SIZE_DEFAULT = 100
MIN_CELL_W, MIN_CELL_H = 600, 600
IDEAL_CELL_W, IDEAL_CELL_H = 800, 800

# -----------------------
# Utility
# -----------------------

def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def compile_ok(code: str) -> Tuple[bool, str]:
    try:
        ast.parse(code)
        return True, "ok"
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"

# -----------------------
# Host DB access
# -----------------------

class DB:
    """Thin wrapper around SQLite for convenience."""
    def __init__(self, path: Path):
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(str(self.path))
        c.row_factory = sqlite3.Row
        return c

    def ensure_schema(self):
        c = self.connect()
        u = c.cursor()
        u.executescript("""
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=NORMAL;

        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);

        CREATE TABLE IF NOT EXISTS cells (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE,
          parent_id INTEGER,
          cluster_id TEXT,
          immutable INTEGER DEFAULT 0,
          code TEXT NOT NULL,
          metadata_json TEXT,
          version INTEGER DEFAULT 1,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cell_versions(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          cell_name TEXT, version INTEGER, code TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS diffs(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          cell_name TEXT, from_version INTEGER, to_version INTEGER,
          diff_type TEXT, diff_text TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS signals(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          from_cell TEXT, to_cell TEXT, kind TEXT, payload_json TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS errors(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          cell_name TEXT, version INTEGER, traceback TEXT, context_json TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, resolved_by TEXT
        );

        CREATE TABLE IF NOT EXISTS knowledge(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          cell_name TEXT, content_text TEXT, embedding BLOB, tags_json TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS assets(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          cell_name TEXT, type TEXT, data BLOB, path TEXT, meta_json TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS antapi(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE, code TEXT NOT NULL, version INTEGER DEFAULT 1,
          metadata_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS logs(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          cell_name TEXT, level TEXT, message TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS buckets(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE, purpose TEXT, schema_json TEXT, mutable INTEGER DEFAULT 1,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS bucket_items(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          bucket_name TEXT, key TEXT, value_json TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(bucket_name, key)
        );

        CREATE TABLE IF NOT EXISTS readmes(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE, content_markdown TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Guards (only active when such updates occur)
        CREATE TRIGGER IF NOT EXISTS trg_cells_guard_immutable
        BEFORE UPDATE OF code ON cells
        WHEN old.immutable = 1
        BEGIN
          SELECT RAISE(ABORT, 'immutable cell cannot update code');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_cells_guard_version_step
        BEFORE UPDATE OF code ON cells
        WHEN new.immutable = 0 AND new.version <> old.version + 1
        BEGIN
          SELECT RAISE(ABORT, 'version must increment by exactly 1 when updating code');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_cells_version_snapshot
        AFTER UPDATE OF code ON cells
        WHEN new.immutable = 0
        BEGIN
          INSERT INTO cell_versions(cell_name, version, code)
          VALUES (new.name, new.version, new.code);
        END;

        CREATE TRIGGER IF NOT EXISTS trg_errors_log
        AFTER INSERT ON errors
        BEGIN
          INSERT INTO logs(cell_name, level, message, created_at)
          VALUES (new.cell_name, 'ERROR', coalesce(new.traceback,'(no tb)'), CURRENT_TIMESTAMP);
        END;
        """)
        c.commit()
        c.close()

    # Convenience helpers used by UI
    def cells_all(self) -> List[sqlite3.Row]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT * FROM cells ORDER BY name")
        rows = x.fetchall()
        c.close()
        return rows

    def cell_get(self, name: str) -> Optional[sqlite3.Row]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT * FROM cells WHERE name=?", (name,))
        r = x.fetchone()
        c.close()
        return r

    def cell_insert(self, name: str, code: str, immutable: int = 0,
                    parent: Optional[str] = None, pos=(0,0), size=(IDEAL_CELL_W, IDEAL_CELL_H)) -> None:
        meta = {"pos": {"x": pos[0], "y": pos[1]}, "size": {"w": size[0], "h": size[1]}}
        c = self.connect(); x = c.cursor()
        x.execute(
            "INSERT INTO cells(name,parent_id,cluster_id,immutable,code,metadata_json,version) "
            "VALUES (?,NULL,NULL,?,?,?,1)",
            (name, immutable, code, json.dumps(meta))
        )
        x.execute(
            "INSERT INTO cell_versions(cell_name,version,code) VALUES(?,?,?)",
            (name, 1, code)
        )
        c.commit(); c.close()

    def cell_update_code(self, name: str, new_code: str, diff_text: str = "") -> None:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT version, immutable FROM cells WHERE name=?", (name,))
        r = x.fetchone()
        if not r:
            c.close(); raise RuntimeError("Cell not found")
        if r["immutable"]:
            c.close(); raise RuntimeError("Cell immutable")
        nv = r["version"] + 1
        x.execute("UPDATE cells SET code=?, version=? WHERE name=?", (new_code, nv, name))
        if diff_text:
            x.execute(
                "INSERT INTO diffs(cell_name,from_version,to_version,diff_type,diff_text) "
                "VALUES(?,?,?,?,?)", (name, nv-1, nv, "literal", diff_text)
            )
        c.commit(); c.close()

    def cell_rollback(self, name: str) -> int:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT version, immutable FROM cells WHERE name=?", (name,))
        r = x.fetchone()
        if not r:
            c.close(); raise RuntimeError("Cell not found")
        if r["immutable"]:
            c.close(); raise RuntimeError("Cell immutable")
        v = r["version"]
        if v <= 1:
            c.close(); raise RuntimeError("No earlier version")
        x.execute("SELECT code FROM cell_versions WHERE cell_name=? AND version=?", (name, v-1))
        pr = x.fetchone()
        if not pr:
            c.close(); raise RuntimeError("Missing prior snapshot")
        x.execute("UPDATE cells SET code=?, version=? WHERE name=?", (pr["code"], v-1, name))
        c.commit(); c.close()
        return v-1

    def log(self, cell: str, level: str, message: str):
        c = self.connect(); x = c.cursor()
        x.execute("INSERT INTO logs(cell_name,level,message) VALUES(?,?,?)", (cell, level, message))
        c.commit(); c.close()

    def emit(self, frm: str, kind: str, payload: dict, to: Optional[str] = None):
        c = self.connect(); x = c.cursor()
        x.execute(
            "INSERT INTO signals(from_cell,to_cell,kind,payload_json,created_at) VALUES(?,?,?,?,?)",
            (frm, to, kind, json.dumps(payload), now_utc())
        )
        c.commit(); c.close()

# -----------------------
# ANT Api shim provided to cells
# -----------------------

class ANTApi:
    """API object passed into cells during build_gui/core_behavior."""
    def __init__(self, db: DB, cell_name: str):
        self.db = db
        self.cell = cell_name
    def log(self, level: str, msg: str):
        self.db.log(self.cell, level, msg)
    def emit(self, kind: str, payload: dict, to: Optional[str] = None):
        self.db.emit(self.cell, kind, payload, to)
    def remember(self, text: str, tags: Optional[dict] = None):
        c = self.db.connect(); x = c.cursor()
        x.execute("INSERT INTO knowledge(cell_name,content_text,embedding,tags_json) VALUES(?,?,?,?)",
                  (self.cell, text, None, json.dumps(tags or {})))
        c.commit(); c.close()
    def metadata(self) -> dict:
        c = self.db.connect(); x = c.cursor()
        x.execute("SELECT metadata_json FROM cells WHERE name=?", (self.cell,))
        r = x.fetchone(); c.close()
        return json.loads(r["metadata_json"] or "{}") if r and r["metadata_json"] else {}

# -----------------------
# Graphics scene with snap-grid
# -----------------------

class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, grid: int):
        super().__init__()
        self.grid = grid
        self.show_grid = False

    def drawBackground(self, p: QtGui.QPainter, rect: QtCore.QRectF):
        if not self.show_grid:
            return
        left = int(rect.left()) - (int(rect.left()) % self.grid)
        top  = int(rect.top())  - (int(rect.top())  % self.grid)
        pen = QtGui.QPen(QtGui.QColor(60, 60, 60))
        pen.setWidth(0)
        p.setPen(pen)
        lines = []
        for x in range(left, int(rect.right()), self.grid):
            lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom()), self.grid):
            lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
        p.drawLines(lines)

class CellItem(QtWidgets.QGraphicsRectItem):
    """A single cell widget embedded into the scene via QGraphicsProxyWidget."""
    def __init__(self, name: str, widget: QtWidgets.QWidget, grid: int):
        super().__init__()
        self.cell = name
        self.grid = grid
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable | self.ItemSendsScenePositionChanges)
        self.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0)))
        self.proxy = QtWidgets.QGraphicsProxyWidget(self)
        self.proxy.setWidget(widget)
        sz = widget.sizeHint()
        w = max(sz.width(),  MIN_CELL_W)
        h = max(sz.height(), MIN_CELL_H)
        self.setRect(0, 0, w, h)

    def snap(self, p: QtCore.QPointF) -> QtCore.QPointF:
        x = round(p.x() / self.grid) * self.grid
        y = round(p.y() / self.grid) * self.grid
        return QtCore.QPointF(x, y)

    def itemChange(self, change: 'QGraphicsItem.GraphicsItemChange', value):
        if change == self.ItemPositionChange:
            return self.snap(value)
        return super().itemChange(change, value)

class CompositeItem(QtWidgets.QGraphicsRectItem):
    """Composite UI that merges multiple cell widgets horizontally or vertically."""
    def __init__(self, name: str, widgets: List[Tuple[str, QtWidgets.QWidget]], grid: int, vertical: bool = False):
        super().__init__()
        self.cell = name
        self.grid = grid
        self.setFlags(self.ItemIsMovable | self.ItemIsSelectable | self.ItemSendsScenePositionChanges)
        self.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0)))

        container = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(container) if vertical else QtWidgets.QHBoxLayout(container)
        lay.setContentsMargins(0,0,0,0); lay.setSpacing(6)

        for cname, w in widgets:
            frame = QtWidgets.QGroupBox(cname)
            inner = QtWidgets.QVBoxLayout(frame)
            inner.setContentsMargins(6,6,6,6)
            inner.addWidget(w)
            lay.addWidget(frame)

        self.proxy = QtWidgets.QGraphicsProxyWidget(self)
        self.proxy.setWidget(container)
        sz = container.sizeHint()
        w = max(sz.width(),  MIN_CELL_W)
        h = max(sz.height(), MIN_CELL_H)
        self.setRect(0, 0, w, h)

    def snap(self, p: QtCore.QPointF) -> QtCore.QPointF:
        x = round(p.x() / self.grid) * self.grid
        y = round(p.y() / self.grid) * self.grid
        return QtCore.QPointF(x, y)

    def itemChange(self, change: 'QGraphicsItem.GraphicsItemChange', value):
        if change == self.ItemPositionChange:
            return self.snap(value)
        return super().itemChange(change, value)

class View(QtWidgets.QGraphicsView):
    def __init__(self, scene: QtWidgets.QGraphicsScene):
        super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setDragMode(self.RubberBandDrag)

    def wheelEvent(self, e: QtGui.QWheelEvent):
        factor = 1.15 if e.angleDelta().y() > 0 else 1/1.15
        self.scale(factor, factor)

# -----------------------
# Main Window
# -----------------------

class ImmuneUI(QtWidgets.QMainWindow):
    pollMs = 1200

    DEFAULT_BUCKET_TEMPLATES = {
        "code_parts": {
            "purpose": "Segmented code for surgical edits",
            "schema": {"type":"object","required":["cell","segments"],
                       "properties":{"cell":{"type":"string"},
                                     "segments":{"type":"array","items":{"type":"object",
                                     "required":["kind","name","text"],
                                     "properties":{"kind":{"enum":["import","class","function","comment","other"]},
                                                   "name":{"type":"string"},
                                                   "text":{"type":"string"}}}}}}
        },
        "prompts": {
            "purpose": "Reusable prompts and instruction templates",
            "schema": {"type":"object","required":["title","text"],
                       "properties":{"title":{"type":"string"},"text":{"type":"string"}}}
        },
        "debates": {
            "purpose": "Dialogues between cells for planning/consensus",
            "schema": {"type":"object","required":["topic","transcript"],
                       "properties":{"topic":{"type":"string"},"transcript":{"type":"array"}}}
        },
        "ui_layouts": {
            "purpose": "Saved GUI placements and composite layout configs",
            "schema": {"type":"object","required":["layout"],"properties":{"layout":{"type":"object"}}}
        },
        "merge_protocols": {
            "purpose": "Interface contracts for merged cells",
            "schema": {"type":"object","required":["name","events","payload_schema"],
                       "properties":{"name":{"type":"string"},"events":{"type":"array"},
                                     "payload_schema":{"type":"object"}}}
        },
        "repair_strategies": {
            "purpose": "Known error patterns → proposed patches",
            "schema": {"type":"object","required":["pattern","fix"],
                       "properties":{"pattern":{"type":"string"},"fix":{"type":"string"}}}
        }
    }

    def __init__(self, db: DB, grid_size: int = GRID_SIZE_DEFAULT):
        super().__init__()
        self.db = db
        self.grid_size = grid_size
        self.scene = GridScene(self.grid_size)
        self.view = View(self.scene)
        self.setWindowTitle(APP_NAME)
        self.resize(1440, 900)
        self.items: Dict[str, QtWidgets.QGraphicsRectItem] = {}

        self._make_menu()
        self._make_toolbar()
        self._make_docks()
        self.setCentralWidget(self.view)

        # Ensure cell_1 exists if cell_0 present
        self.ensure_cell1()

        # Populate canvas
        self.populate()

        # Poller for position-save and logs refresh
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(self.pollMs)

    # --------- UI chrome ---------

    def _make_menu(self):
        mbar = self.menuBar()

        m_file = mbar.addMenu("&File")
        act_open = QtWidgets.QAction("Open Host…", self)
        act_open.triggered.connect(self.action_open_host)
        m_file.addAction(act_open)

        act_new = QtWidgets.QAction("New Host…", self)
        act_new.triggered.connect(self.action_new_host)
        m_file.addAction(act_new)

        m_file.addSeparator()
        act_quit = QtWidgets.QAction("Quit", self)
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_quit)

        m_tools = mbar.addMenu("&Tools")
        act_add_bucket = QtWidgets.QAction("Add Bucket…", self)
        act_add_bucket.triggered.connect(self.action_add_bucket)
        m_tools.addAction(act_add_bucket)

        act_inject = QtWidgets.QAction("Inject Protein…", self)
        act_inject.triggered.connect(self.inject_protein)
        m_tools.addAction(act_inject)

        m_view = mbar.addMenu("&View")
        self.act_grid = QtWidgets.QAction("Toggle Grid", self, checkable=True)
        self.act_grid.triggered.connect(self.toggle_grid)
        m_view.addAction(self.act_grid)

        act_center = QtWidgets.QAction("Center on cell_1", self)
        act_center.triggered.connect(self.center_cell1)
        m_view.addAction(act_center)

        m_help = mbar.addMenu("&Help")
        act_about = QtWidgets.QAction("About", self)
        act_about.triggered.connect(self.action_about)
        m_help.addAction(act_about)

    def _make_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)

        a_spawn = QtWidgets.QAction("Spawn Cell", self)
        a_spawn.setToolTip("Spawn from cell_0 template")
        a_spawn.triggered.connect(self.spawn_cell)
        tb.addAction(a_spawn)

        a_merge_h = QtWidgets.QAction("Merge Horiz", self)
        a_merge_h.triggered.connect(lambda: self.merge_selected(vertical=False))
        tb.addAction(a_merge_h)

        a_merge_v = QtWidgets.QAction("Merge Vert", self)
        a_merge_v.triggered.connect(lambda: self.merge_selected(vertical=True))
        tb.addAction(a_merge_v)

        a_unmerge = QtWidgets.QAction("Unmerge", self)
        a_unmerge.triggered.connect(self.unmerge_selected)
        tb.addAction(a_unmerge)

        a_refresh = QtWidgets.QAction("Refresh", self)
        a_refresh.triggered.connect(self.populate)
        tb.addAction(a_refresh)

    def _make_docks(self):
        # Cells dock
        d = QtWidgets.QDockWidget("Cells", self)
        self.list = QtWidgets.QListWidget()
        self.list.itemSelectionChanged.connect(self.on_sel)
        d.setWidget(self.list)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, d)

        # Inspector
        d2 = QtWidgets.QDockWidget("Inspector", self)
        w = QtWidgets.QWidget(); v = QtWidgets.QVBoxLayout(w)
        self.lbl = QtWidgets.QLabel("—"); v.addWidget(self.lbl)
        mono = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)

        self.ed = QtWidgets.QPlainTextEdit(); self.ed.setFont(mono)
        self.ed.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        v.addWidget(self.ed, 1)

        row = QtWidgets.QHBoxLayout()
        self.b_save = QtWidgets.QPushButton("Save")
        self.b_save.clicked.connect(self.save_code)
        self.b_run = QtWidgets.QPushButton("Run Behavior")
        self.b_run.clicked.connect(self.run_behavior)
        self.b_rb = QtWidgets.QPushButton("Rollback")
        self.b_rb.clicked.connect(self.rollback)
        row.addWidget(self.b_save); row.addWidget(self.b_run); row.addWidget(self.b_rb)
        v.addLayout(row)

        d2.setWidget(w)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, d2)

        # Global Log
        d3 = QtWidgets.QDockWidget("Global Log", self)
        w3 = QtWidgets.QWidget(); v3 = QtWidgets.QVBoxLayout(w3)
        frow = QtWidgets.QHBoxLayout()
        self.f_cell = QtWidgets.QLineEdit(); self.f_cell.setPlaceholderText("cell filter")
        self.f_level = QtWidgets.QComboBox(); self.f_level.addItems(["","INFO","WARN","ERROR","DEBUG"])
        b = QtWidgets.QPushButton("Apply"); b.clicked.connect(self.refresh_logs)
        frow.addWidget(self.f_cell); frow.addWidget(self.f_level); frow.addWidget(b)
        v3.addLayout(frow)
        self.log = QtWidgets.QPlainTextEdit(); self.log.setReadOnly(True)
        v3.addWidget(self.log, 1)
        d3.setWidget(w3)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, d3)

        # Host Browser
        d4 = QtWidgets.QDockWidget("Host Browser", self)
        w4 = QtWidgets.QWidget(); v4 = QtWidgets.QVBoxLayout(w4)
        top = QtWidgets.QHBoxLayout()
        self.tables = QtWidgets.QComboBox()
        pb = QtWidgets.QPushButton("Preview"); pb.clicked.connect(self.preview)
        top.addWidget(self.tables, 1); top.addWidget(pb)
        v4.addLayout(top)
        self.sql = QtWidgets.QPlainTextEdit(); self.sql.setPlaceholderText("SELECT * FROM cells")
        v4.addWidget(self.sql, 1)
        row2 = QtWidgets.QHBoxLayout()
        self.lim = QtWidgets.QSpinBox(); self.lim.setRange(1,100000); self.lim.setValue(200)
        run = QtWidgets.QPushButton("Run"); run.clicked.connect(self.exec_select)
        row2.addWidget(QtWidgets.QLabel("Limit")); row2.addWidget(self.lim)
        row2.addStretch(1); row2.addWidget(run)
        v4.addLayout(row2)
        self.table = QtWidgets.QTableWidget(); v4.addWidget(self.table, 2)
        d4.setWidget(w4)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, d4)

    # --------- Actions ---------

    def action_open_host(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Host SQLite", "", "SQLite DB (*.db *.sqlite *.sqlitedb);;All Files (*)")
        if not path: return
        self.db = DB(Path(path))
        self.db.ensure_schema()
        self.ensure_cell1()
        self.populate()

    def action_new_host(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Create Host SQLite", "host.db", "SQLite DB (*.db)")
        if not path: return
        self.db = DB(Path(path))
        self.db.ensure_schema()
        # seed minimal cell_0 if absent
        if not self.db.cell_get("cell_0"):
            cell0 = (
                "from PyQt5 import QtWidgets\n"
                "def build_gui(api):\n"
                "    w=QtWidgets.QWidget(); v=QtWidgets.QVBoxLayout(w)\n"
                "    v.addWidget(QtWidgets.QLabel('cell_0 template'))\n"
                "    v.addWidget(QtWidgets.QLabel('Immutable bedrock template.'))\n"
                "    return w\n"
                "def core_behavior(api):\n"
                "    api.log('INFO','cell_0 heartbeat'); api.remember('cell_0 heartbeat'); return {'ok':True}\n"
            )
            self.db.cell_insert("cell_0", cell0, immutable=1, parent=None, pos=(0,0), size=(IDEAL_CELL_W, IDEAL_CELL_H))
        self.ensure_cell1()
        self.populate()

    def action_add_bucket(self):
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle("Add Bucket")
        v = QtWidgets.QVBoxLayout(dlg)
        info = QtWidgets.QLabel("Choose a bucket template or define a custom one.")
        v.addWidget(info)
        form = QtWidgets.QFormLayout()
        name = QtWidgets.QLineEdit(); form.addRow("Name", name)
        purpose = QtWidgets.QLineEdit(); form.addRow("Purpose", purpose)
        template = QtWidgets.QComboBox(); template.addItems(["<custom>"] + list(self.DEFAULT_BUCKET_TEMPLATES.keys()))
        form.addRow("Template", template)
        schema = QtWidgets.QPlainTextEdit(); schema.setPlaceholderText('{"type":"object", ...}')
        schema.setMinimumHeight(140)
        v.addLayout(form); v.addWidget(schema, 1)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        v.addWidget(bb)
        def on_template_change(idx):
            key = template.currentText()
            if key in self.DEFAULT_BUCKET_TEMPLATES:
                tpl = self.DEFAULT_BUCKET_TEMPLATES[key]
                purpose.setText(tpl["purpose"])
                schema.setPlainText(json.dumps(tpl["schema"]))
        template.currentIndexChanged.connect(on_template_change)
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            nm = name.text().strip()
            pc = purpose.text().strip()
            sc = schema.toPlainText().strip()
            if not nm or not pc or not sc:
                QtWidgets.QMessageBox.warning(self, "Bucket", "All fields required.")
                return
            try:
                # validate schema JSON
                json.loads(sc)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Schema JSON", f"Invalid JSON: {e}")
                return
            c = self.db.connect(); x = c.cursor()
            try:
                x.execute(
                    "INSERT OR REPLACE INTO buckets(name,purpose,schema_json,mutable) VALUES(?,?,?,1)",
                    (nm, pc, sc)
                )
                c.commit()
                QtWidgets.QMessageBox.information(self, "Bucket", f"Added/updated bucket '{nm}'.")
            except Exception as e:
                c.rollback()
                QtWidgets.QMessageBox.critical(self, "Bucket", str(e))
            finally:
                c.close()
            self.refresh_tables()

    def action_about(self):
        QtWidgets.QMessageBox.information(self, "About", f"{APP_NAME}\nSnap-grid canvas • Versioned cells • Buckets • Proteins\n{self.db.path}")

    # --------- Core ops ---------

    def ensure_cell1(self):
        c0 = self.db.cell_get("cell_0")
        c1 = self.db.cell_get("cell_1")
        if c0 and not c1:
            self.db.cell_insert("cell_1", c0["code"], immutable=0, parent="cell_0",
                                pos=(0,0), size=(IDEAL_CELL_W, IDEAL_CELL_H))
            self.db.log("immune_system", "INFO", "Spawned cell_1 from cell_0")

    def populate(self):
        self.scene.clear()
        self.items.clear()
        self.list.clear()
        rows = self.db.cells_all()
        for r in rows:
            name = r["name"]
            self.list.addItem(name)
            w = self.make_widget(r)
            it = CellItem(name, w, self.grid_size)
            self.scene.addItem(it)
            meta = json.loads(r["metadata_json"] or "{}")
            pos = meta.get("pos", {"x":0,"y":0})
            it.setPos(pos.get("x",0), pos.get("y",0))
            self.items[name] = it
        self.refresh_tables()
        self.center_cell1()

    def make_widget(self, row: sqlite3.Row) -> QtWidgets.QWidget:
        name = row["name"]; code = row["code"]; imm = bool(row["immutable"])
        # Try to exec the cell module and build its GUI
        try:
            mod = types.ModuleType("cellmod"); exec(code, mod.__dict__)
            if hasattr(mod, "build_gui"):
                try:
                    w = mod.build_gui(ANTApi(self.db, name))
                except Exception as e:
                    self.db.log("immune_system", "ERROR", f"build_gui({name}): {e}")
                    w = None
            else:
                w = None
        except Exception as e:
            self.db.log("immune_system", "ERROR", f"compile {name}: {e}")
            w = None

        if w is None:
            w = QtWidgets.QWidget()
            v = QtWidgets.QVBoxLayout(w)
            t = QtWidgets.QLabel(f"{name}" + (" (immutable)" if imm else ""))
            t.setStyleSheet("font-weight:bold")
            v.addWidget(t)
            v.addWidget(QtWidgets.QLabel("Default cell UI. Edit code in Inspector."))
            v.addStretch(1)

        # enforce minimums for consistent placement
        w.setMinimumSize(MIN_CELL_W, MIN_CELL_H)
        w.resize(IDEAL_CELL_W, IDEAL_CELL_H)
        return w

    def center_cell1(self):
        it = self.items.get("cell_1")
        self.view.centerOn(it if it else QtCore.QPointF(0,0))

    def toggle_grid(self):
        self.scene.show_grid = not self.scene.show_grid
        self.scene.update()

    def on_sel(self):
        it = self.list.selectedItems()
        if not it:
            self.lbl.setText("—"); self.ed.setPlainText("")
            self.b_save.setEnabled(False); self.b_rb.setEnabled(False)
            return
        name = it[0].text()
        row = self.db.cell_get(name)
        self.lbl.setText(f"{name}  v{row['version']}  immutable={'yes' if row['immutable'] else 'no'}")
        self.ed.setPlainText(row["code"])
        self.ed.setReadOnly(bool(row["immutable"]))
        self.b_save.setEnabled(not bool(row["immutable"]))
        self.b_rb.setEnabled(not bool(row["immutable"]))

    def save_code(self):
        it = self.list.selectedItems()
        if not it: return
        name = it[0].text()
        code = self.ed.toPlainText()
        ok, msg = compile_ok(code)
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Syntax", msg); return
        try:
            self.db.cell_update_code(name, code)
            self.db.log("immune_system", "INFO", f"Saved {name}")
            self.populate()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save error", str(e))

    def run_behavior(self):
        it = self.list.selectedItems()
        if not it: return
        name = it[0].text()
        row = self.db.cell_get(name)
        code = row["code"]
        try:
            mod = types.ModuleType("cellmod"); exec(code, mod.__dict__)
            if hasattr(mod, "core_behavior"):
                res = mod.core_behavior(ANTApi(self.db, name))
                QtWidgets.QMessageBox.information(self, "Result", str(res))
            else:
                QtWidgets.QMessageBox.information(self, "Result", "No core_behavior(api) defined.")
        except Exception as e:
            tb = traceback.format_exc()
            self.db.log(name, "ERROR", f"behavior: {e}")
            c = self.db.connect(); x = c.cursor()
            x.execute("INSERT INTO errors(cell_name,version,traceback,context_json) VALUES(?,?,?,?)",
                      (name, row["version"], tb, json.dumps({"action": "core_behavior"})))
            c.commit(); c.close()
            QtWidgets.QMessageBox.critical(self, "Behavior error", str(e))

    def rollback(self):
        it = self.list.selectedItems()
        if not it: return
        name = it[0].text()
        try:
            v = self.db.cell_rollback(name)
            self.db.log("immune_system", "WARN", f"Rollback {name} -> v{v}")
            self.populate()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Rollback", str(e))

    def spawn_cell(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Spawn Cell", "Name:")
        if not ok or not name.strip():
            return
        clean = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name.strip())
        if self.db.cell_get(clean):
            QtWidgets.QMessageBox.warning(self, "Exists", "Cell already exists.")
            return
        c0 = self.db.cell_get("cell_0")
        code = c0["code"] if c0 else (
            "def core_behavior(api):\n    return {'ok':True}\n"
        )
        pos = self.free_pos()
        self.db.cell_insert(clean, code, immutable=0, parent="cell_0", pos=pos, size=(IDEAL_CELL_W, IDEAL_CELL_H))
        self.db.log("immune_system", "INFO", f"Spawned {clean}")
        self.populate()

    def free_pos(self) -> Tuple[int, int]:
        """Find a free grid spot with at least one-grid spacing from others."""
        occ = set()
        for it in self.items.values():
            p = it.pos()
            gx = round(p.x() / self.grid_size)
            gy = round(p.y() / self.grid_size)
            occ.add((gx, gy))
        for r in range(0, 64):
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    if (dx, dy) in occ: continue
                    neigh = [(dx+1,dy),(dx-1,dy),(dx,dy+1),(dx,dy-1)]
                    if any(n in occ for n in neigh):  # enforce 1-cell spacing
                        continue
                    return (dx * self.grid_size, dy * self.grid_size)
        return (0, 0)

    def merge_selected(self, vertical: bool = False):
        sel = [i for i in self.scene.selectedItems() if isinstance(i, (CellItem, CompositeItem))]
        # Only merge leaf cell widgets (not composites) for clarity
        leafs = []
        for it in sel:
            w = it.proxy.widget()
            # If CompositeItem, expand its direct children widgets
            if isinstance(it, CompositeItem):
                # Treat as a single unit
                leafs.append((it.cell, w))
            else:
                leafs.append((it.cell, w))
        if len(leafs) < 2:
            QtWidgets.QMessageBox.information(self, "Merge", "Select ≥2 cells.")
            return
        # Detach from scene and make composite
        for it in sel:
            self.scene.removeItem(it)
            self.items.pop(it.cell, None)
        comp = CompositeItem("composite", [ (n,w) for (n,w) in leafs ], self.grid_size, vertical=vertical)
        self.scene.addItem(comp)
        comp.setPos(0,0)
        self.items["composite"] = comp
        self.db.log("immune_system", "INFO", f"Merged {'vertical' if vertical else 'horizontal'}")
        self.populate()

    def unmerge_selected(self):
        sel = [i for i in self.scene.selectedItems() if isinstance(i, CompositeItem)]
        if len(sel) != 1:
            QtWidgets.QMessageBox.information(self, "Unmerge", "Select exactly one composite item.")
            return
        it = sel[0]
        container = it.proxy.widget()
        # Extract child group boxes' inner widgets
        if not isinstance(container, QtWidgets.QWidget):
            return
        child_widgets = []
        for g in container.findChildren(QtWidgets.QGroupBox, options=QtCore.Qt.FindDirectChildrenOnly):
            if g.layout() and g.layout().count() > 0:
                child_widgets.append((g.title(), g.layout().itemAt(0).widget()))
        base = it.pos()
        for idx, (name, w) in enumerate(child_widgets):
            child = CellItem(name, w, self.grid_size)
            self.scene.addItem(child)
            child.setPos(base + QtCore.QPointF((idx+1)*self.grid_size*2, (idx%2)*self.grid_size*2))
            self.items[name] = child
        self.scene.removeItem(it)
        self.items.pop("composite", None)
        self.db.log("immune_system", "INFO", "Unmerged")
        self.populate()

    def inject_protein(self):
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle("Protein (broadcast/targeted)")
        v = QtWidgets.QVBoxLayout(dlg)
        ed = QtWidgets.QPlainTextEdit(); ed.setPlaceholderText("directive text…")
        tgt = QtWidgets.QLineEdit(); tgt.setPlaceholderText("target cell (optional)")
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        v.addWidget(ed); v.addWidget(tgt); v.addWidget(bb)
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            text = ed.toPlainText().strip()
            to = tgt.text().strip() or None
            if text:
                self.db.emit("immune_system", "protein", {"text": text}, to)
                self.db.log("immune_system", "INFO", f"protein -> {to or 'broadcast'}")

    def refresh_tables(self):
        try:
            c = self.db.connect(); x = c.cursor()
            x.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            names = [r[0] for r in x.fetchall()]
            c.close()
            self.tables.clear(); self.tables.addItems(names)
        except Exception as e:
            self.db.log("immune_system", "ERROR", f"tables:{e}")

    def preview(self):
        t = self.tables.currentText().strip()
        if not t: return
        try:
            c = self.db.connect(); x = c.cursor()
            x.execute(f"PRAGMA table_info({t})")
            cols = [r[1] for r in x.fetchall()]
            x.execute(f"SELECT * FROM {t} LIMIT 200")
            data = x.fetchall(); c.close()
            self.fill_table(cols, data)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Preview", str(e))

    def exec_select(self):
        sql = self.sql.toPlainText().strip()
        if not sql.lower().startswith("select"):
            QtWidgets.QMessageBox.warning(self, "SQL", "Read-only: SELECT only.")
            return
        try:
            c = self.db.connect(); x = c.cursor()
            x.execute(sql + f" LIMIT {int(self.lim.value())}")
            cols = [d[0] for d in x.description]
            data = x.fetchall(); c.close()
            self.fill_table(cols, data)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "SQL", str(e))

    def fill_table(self, cols: List[str], rows: List[sqlite3.Row]):
        self.table.clear()
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(str(val)))
        self.table.resizeColumnsToContents()

    def tick(self):
        # Persist positions
        for name, it in list(self.items.items()):
            p = it.pos()
            self._save_pos(name, int(p.x()), int(p.y()))
        # Refresh logs
        self.refresh_logs()

    def _save_pos(self, name: str, x: int, y: int):
        r = self.db.cell_get(name)
        if not r: return
        meta = json.loads(r["metadata_json"] or "{}")
        meta.setdefault("pos", {})
        meta["pos"]["x"] = x; meta["pos"]["y"] = y
        c = self.db.connect(); xq = c.cursor()
        xq.execute("UPDATE cells SET metadata_json=? WHERE name=?", (json.dumps(meta), name))
        c.commit(); c.close()

    def refresh_logs(self):
        cell = self.f_cell.text().strip() or None
        lev  = self.f_level.currentText().strip() or None
        c = self.db.connect(); x = c.cursor()
        base = "SELECT * FROM logs"
        wh, pr = [], []
        if cell: wh.append("cell_name=?"); pr.append(cell)
        if lev:  wh.append("level=?");     pr.append(lev)
        if wh: base += " WHERE " + " AND ".join(wh)
        base += " ORDER BY id DESC LIMIT 1000"
        x.execute(base, pr)
        rows = x.fetchall(); c.close()
        cur = self.log.verticalScrollBar().value()
        mx  = self.log.verticalScrollBar().maximum()
        at_bottom = cur >= mx - 4
        txt = "\n".join(f"[{r['created_at']}] {r['cell_name']} {r['level']}: {r['message']}" for r in reversed(rows))
        self.log.setPlainText(txt)
        if at_bottom:
            self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

# -----------------------
# App bootstrap
# -----------------------

def apply_dark_palette(app: QtWidgets.QApplication):
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, QtGui.QColor(18,18,18))
    pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Base, QtGui.QColor(12,12,12))
    pal.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(22,22,22))
    pal.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(32,32,32))
    pal.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Button, QtGui.QColor(24,24,24))
    pal.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(60,180,120))
    pal.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    pal.setColor(QtGui.QPalette.Link, QtGui.QColor(130, 200, 255))
    app.setPalette(pal)
    app.setStyle("Fusion")

def pick_host_path(parent=None) -> Optional[str]:
    dlg = QtWidgets.QFileDialog(parent, "Open Host SQLite")
    dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
    dlg.setNameFilter("SQLite DB (*.db *.sqlite *.sqlitedb);;All Files (*)")
    if dlg.exec_() == QtWidgets.QDialog.Accepted:
        files = dlg.selectedFiles()
        return files[0] if files else None
    return None

def main():
    app = QtWidgets.QApplication(sys.argv)
    apply_dark_palette(app)

    # determine DB path AFTER QApplication to avoid QMessageBox-before-QApp errors
    dbp = os.environ.get("SINGLECELL_DB") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not dbp:
        # Let user pick a host DB
        choice = QtWidgets.QMessageBox.question(
            None, "Host Required",
            "No host DB provided.\n\nChoose an existing host (Yes) or create a new one (No)?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Yes
        )
        if choice == QtWidgets.QMessageBox.Yes:
            sel = pick_host_path(None)
            if not sel:
                sys.exit(0)
            dbp = sel
        elif choice == QtWidgets.QMessageBox.No:
            save, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Create Host SQLite", "host.db", "SQLite DB (*.db)")
            if not save:
                sys.exit(0)
            dbp = save
        else:
            sys.exit(0)

    db = DB(Path(dbp))
    db.ensure_schema()

    # If completely fresh and missing cell_0, seed a minimal one so UX works immediately.
    if not db.cell_get("cell_0"):
        cell0 = (
            "from PyQt5 import QtWidgets\n"
            "def build_gui(api):\n"
            "    w=QtWidgets.QWidget(); v=QtWidgets.QVBoxLayout(w)\n"
            "    v.addWidget(QtWidgets.QLabel('cell_0 template'))\n"
            "    v.addWidget(QtWidgets.QLabel('Immutable bedrock template.'))\n"
            "    return w\n"
            "def core_behavior(api):\n"
            "    api.log('INFO','cell_0 heartbeat'); api.remember('cell_0 heartbeat'); return {'ok':True}\n"
        )
        db.cell_insert("cell_0", cell0, immutable=1, parent=None, pos=(0,0), size=(IDEAL_CELL_W, IDEAL_CELL_H))

    ui = ImmuneUI(db, grid_size=GRID_SIZE_DEFAULT)

    # Dark retro top-level QSS accents
    ui.setStyleSheet("""
        QMainWindow { background: #0f0f10; }
        QDockWidget::title { text-transform: uppercase; letter-spacing: 1px; }
        QListWidget, QTableWidget { background: #141416; color: #e8e8e8; }
        QLineEdit, QComboBox, QSpinBox { background:#141416; color:#e8e8e8; border:1px solid #2b2b2b; }
        QPushButton { background:#1a1b1e; border:1px solid #2b2b2b; padding:6px 10px; }
        QPushButton:hover { border-color:#3a3a3a; }
        QToolBar { background:#131315; border-bottom:1px solid #242428; }
        QDockWidget { titlebar-close-icon: url(none); titlebar-normal-icon: url(none); }
    """)

    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

**Classes:** DB, ANTApi, GridScene, CellItem, CompositeItem, View, ImmuneUI
**Functions:** now_utc(), compile_ok(code), apply_dark_palette(app), pick_host_path(parent), main()


## Module `Loader\cell_1.py`

```python
#!/usr/bin/env python3
# cell_1.py  — also valid as cell_0 (cell_0 should be immutable in host schema)
# A self-writing, self-validating agent cell with an embedded ANTapi "soul".
# - Uses Ollama (default model: qwen3:4b) for local reasoning/refactor
# - Talks to other agents via signals table
# - Reads/writes Host SQLite directly (SINGLECELL_DB) for buckets, diffs, versions
# - GUI: model dropdown, chat with /commands, bucket browser (Show All), actions

import os, sys, json, time, sqlite3, traceback, difflib, ast, threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from PyQt5 import QtCore, QtGui, QtWidgets

# -------------------------
# Configuration
# -------------------------
APP_CELL_TITLE = "ANT Cell"
DEFAULT_MODEL = "qwen3:4b"
OLLAMA_URL    = "http://localhost:11434"
OLLAMA_GEN    = f"{OLLAMA_URL}/api/generate"
OLLAMA_TAGS   = f"{OLLAMA_URL}/api/tags"

# -------------------------
# Utilities
# -------------------------
def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def unified_diff(a: str, b: str, A: str = "current", B: str = "proposed") -> str:
    lines = difflib.unified_diff(
        a.splitlines(True), b.splitlines(True), fromfile=A, tofile=B, lineterm=""
    )
    return "".join(lines)

def compile_ok(code: str) -> Tuple[bool, str]:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"

def http_json(url: str, payload: Dict[str, Any], timeout: float = 240.0) -> Dict[str, Any]:
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

def list_ollama_models() -> List[str]:
    try:
        r = requests.get(OLLAMA_TAGS, timeout=4.0)
        r.raise_for_status()
        data = r.json() or {}
        names = []
        for m in data.get("models", []):
            nm = (m.get("name") or "").split(":")[0]
            if nm and nm not in names: names.append(nm)
        if DEFAULT_MODEL not in names:
            names.insert(0, DEFAULT_MODEL)
        return names or [DEFAULT_MODEL]
    except Exception:
        return [DEFAULT_MODEL, "llama3", "mistral", "qwen2", "phi3", "tinyllama"]

# -------------------------
# Host access (direct SQLite)
# -------------------------
class Host:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("SINGLECELL_DB") or ""
        if not self.db_path:
            raise RuntimeError("SINGLECELL_DB not set; cell requires Host DB access.")
        self._pth = Path(self.db_path)

    def connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(str(self._pth))
        c.row_factory = sqlite3.Row
        return c

    # --- meta / tables
    def list_tables(self) -> List[str]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        names = [r[0] for r in x.fetchall()]
        c.close()
        return names

    # --- cells
    def list_cells(self) -> List[Dict[str, Any]]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT name, immutable, version, length(code) AS code_len FROM cells ORDER BY name")
        rows = [{"name":r["name"], "immutable":r["immutable"], "version":r["version"], "code_len":r["code_len"]} for r in x.fetchall()]
        c.close()
        return rows

    def get_cell(self, name: str) -> Optional[Dict[str, Any]]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT * FROM cells WHERE name=?", (name,))
        row = x.fetchone(); c.close()
        return dict(row) if row else None

    def update_cell_code(self, name: str, new_code: str, diff_text: str) -> Tuple[bool, str]:
        c = self.connect(); x = c.cursor()
        try:
            x.execute("SELECT version, immutable FROM cells WHERE name=?", (name,))
            r = x.fetchone()
            if not r:
                return False, "Cell not found"
            if (r["immutable"] or 0) == 1:
                return False, "Immutable cell"
            nv = r["version"] + 1
            x.execute("UPDATE cells SET code=?, version=? WHERE name=?", (new_code, nv, name))
            x.execute("INSERT INTO cell_versions(cell_name, version, code) VALUES(?,?,?)", (name, nv, new_code))
            x.execute(
                "INSERT INTO diffs(cell_name, from_version, to_version, diff_type, diff_text) VALUES(?,?,?,?,?)",
                (name, nv - 1, nv, "unified", diff_text),
            )
            c.commit()
            return True, f"Updated {name} to v{nv}"
        except Exception as e:
            c.rollback()
            return False, f"DB error: {e}"
        finally:
            c.close()

    def rollback_cell(self, name: str) -> Tuple[bool, str]:
        c = self.connect(); x = c.cursor()
        try:
            x.execute("SELECT version, immutable FROM cells WHERE name=?", (name,))
            r = x.fetchone()
            if not r:
                return False, "Cell not found"
            if (r["immutable"] or 0) == 1:
                return False, "Immutable cell"
            v = r["version"]
            if v <= 1:
                return False, "No earlier version"
            x.execute("SELECT code FROM cell_versions WHERE cell_name=? AND version=?", (name, v - 1))
            pr = x.fetchone()
            if not pr:
                return False, "Missing prior version"
            x.execute("UPDATE cells SET code=?, version=? WHERE name=?", (pr["code"], v - 1, name))
            c.commit()
            return True, f"Rolled back {name} to v{v-1}"
        except Exception as e:
            c.rollback()
            return False, f"DB error: {e}"
        finally:
            c.close()

    def spawn_cell_from_template(self, new_name: str) -> Tuple[bool, str]:
        c = self.connect(); x = c.cursor()
        try:
            x.execute("SELECT code FROM cells WHERE name='cell_0'")
            r = x.fetchone()
            if not r:
                return False, "cell_0 template not found"
            code = r["code"]
            meta = {"pos":{"x":0,"y":0}, "size":{"w":800,"h":800}, "role":"active"}
            x.execute(
                "INSERT INTO cells(name, parent_id, cluster_id, immutable, code, metadata_json, version) "
                "VALUES (?, NULL, NULL, 0, ?, ?, 1)",
                (new_name, code, json.dumps(meta)),
            )
            x.execute("INSERT INTO cell_versions(cell_name, version, code) VALUES (?, ?, ?)", (new_name, 1, code))
            c.commit()
            return True, f"Spawned {new_name} from cell_0"
        except Exception as e:
            c.rollback()
            return False, f"Spawn error: {e}"
        finally:
            c.close()

    # --- signals/logs/errors/knowledge
    def signal(self, frm: str, kind: str, payload: Dict[str, Any], to: Optional[str] = None):
        c = self.connect(); x = c.cursor()
        x.execute(
            "INSERT INTO signals(from_cell, to_cell, kind, payload_json, created_at) VALUES(?,?,?,?,?)",
            (frm, to, kind, json.dumps(payload), now_utc()),
        )
        c.commit(); c.close()

    def log(self, cell: str, level: str, msg: str):
        c = self.connect(); x = c.cursor()
        x.execute("INSERT INTO logs(cell_name, level, message) VALUES(?,?,?)", (cell, level, msg))
        c.commit(); c.close()

    def error(self, cell: str, version: int, tb: str, ctx: Dict[str, Any]):
        c = self.connect(); x = c.cursor()
        x.execute(
            "INSERT INTO errors(cell_name, version, traceback, context_json) VALUES(?,?,?,?)",
            (cell, version, tb, json.dumps(ctx)),
        )
        c.commit(); c.close()

    def remember(self, cell: str, text: str, tags: Optional[Dict[str, Any]]=None):
        c = self.connect(); x = c.cursor()
        x.execute(
            "INSERT INTO knowledge(cell_name, content_text, embedding, tags_json) VALUES(?,?,?,?)",
            (cell, text, None, json.dumps(tags or {})),
        )
        c.commit(); c.close()

    # --- buckets
    def list_buckets(self) -> List[str]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT name FROM buckets ORDER BY name")
        names = [r[0] for r in x.fetchall()]
        c.close()
        return names

    def read_bucket_items(self, bucket: str, limit: int = 200, only_cell: Optional[str] = None) -> List[Dict[str, Any]]:
        c = self.connect(); x = c.cursor()
        if only_cell:
            # only return items tagged for cell in value_json if present
            x.execute(
                "SELECT id, key, value_json, created_at FROM bucket_items WHERE bucket_name=? AND value_json LIKE ? ORDER BY id DESC LIMIT ?",
                (bucket, f'%\"cell\":\"{only_cell}\"%', limit),
            )
        else:
            x.execute(
                "SELECT id, key, value_json, created_at FROM bucket_items WHERE bucket_name=? ORDER BY id DESC LIMIT ?",
                (bucket, limit),
            )
        rows = [
            {"id":r["id"], "key":r["key"], "value_json":r["value_json"], "created_at":r["created_at"]} for r in x.fetchall()
        ]
        c.close()
        return rows

    def write_bucket_item(self, bucket: str, key: str, value: Dict[str, Any]) -> Tuple[bool, str]:
        c = self.connect(); x = c.cursor()
        try:
            # ensure bucket exists
            x.execute("INSERT OR IGNORE INTO buckets(name, purpose, schema_json, mutable) VALUES(?,?,?,1)",
                      (bucket, f"auto:{bucket}", json.dumps({"type":"object"})))
            x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name, key, value_json) VALUES (?,?,?)",
                      (bucket, key, json.dumps(value)))
            c.commit()
            return True, f"bucket[{bucket}]::{key} written"
        except Exception as e:
            c.rollback()
            return False, f"bucket write error: {e}"
        finally:
            c.close()

# -------------------------
# ANTapi "soul" (agent-side)
# -------------------------
class ANTSoul:
    """
    A living wrapper that:
      - Bridges host DB (buckets, diffs, versions, signals)
      - Calls Ollama
      - Knows how to self-mutate its cell and coordinate with others
      - Grows its /commands index and stores internal memory in 'antapi_soul'
    """
    def __init__(self, api_obj, cell_name: str):
        self.api = api_obj                      # host-provided minimal API (log/emit/remember/metadata)
        self.cell = cell_name
        self.host = Host()                      # direct sqlite access
        self.model = DEFAULT_MODEL
        self.commands_bucket = "commands_index"
        self.ant_soul_bucket = "antapi_soul"
        self.init_buckets()

    # ---- bucket bootstrap ----
    def init_buckets(self):
        # Seed a basic /commands index for the cell
        cmds = [
            "/help",
            "/listcells",
            "/listbuckets",
            "/readb <bucket> [key]",
            "/writeb <bucket> <key> <json>",
            "/signal <target|*> <kind> <json>",
            "/spawn <name>",
            "/diff_self_from <bucket> <key>",
            "/update_self_from <bucket> <key>",
            "/update_cell <name> <bucket> <key>",
            "/rollback <cell>",
            "/self_mutate",
            "/run_behavior <cell>",
        ]
        self.host.write_bucket_item(self.commands_bucket, f"{self.cell}-v1", {"cell": self.cell, "commands": cmds, "ts": now_utc()})
        # Note: ANT-soul internal seed
        self.host.write_bucket_item(self.ant_soul_bucket, f"{self.cell}-hello", {"cell": self.cell, "event":"init", "ts": now_utc()})

    # ---- logging/remember wrappers ----
    def log(self, level: str, msg: str):
        try:
            self.api.log(level, msg)
        except Exception:
            # fallback direct
            self.host.log(self.cell, level, msg)

    def remember(self, text: str, tags: Optional[Dict[str, Any]]=None):
        try:
            self.api.remember(text, tags or {})
        except Exception:
            self.host.remember(self.cell, text, tags or {})

    def emit(self, kind: str, payload: Dict[str, Any], to: Optional[str]=None):
        try:
            self.api.emit(kind, payload, to)
        except Exception:
            self.host.signal(self.cell, kind, payload, to)

    # ---- model & LLM ----
    def set_model(self, model: str):
        self.model = (model or DEFAULT_MODEL).strip()

    def models(self) -> List[str]:
        return list_ollama_models()

    def llm(self, prompt: str, timeout: float = 240.0) -> str:
        payload = {"model": self.model or DEFAULT_MODEL, "prompt": prompt, "stream": False}
        try:
            data = http_json(OLLAMA_GEN, payload, timeout=timeout)
            return (data.get("response") or "").strip()
        except Exception as e:
            self.log("ERROR", f"Ollama call failed: {e}")
            return f"[LLM ERROR] {e}"

    # ---- cell introspection/mutation ----
    def current_code(self) -> str:
        row = self.host.get_cell(self.cell)
        return row["code"] if row else ""

    def propose_self_patch(self, ask: str) -> Tuple[str, str]:
        """Use LLM to propose a refactor/patch. Returns (proposed_code, reasoning)"""
        base = self.current_code()
        prompt = (
            f"You are the ANT-soul of cell '{self.cell}'. "
            "Improve or modify this code to satisfy the user's request. "
            "Return ONLY a single ```python fenced block with the FULL updated script. "
            "Do not omit anything.\n\n"
            "### REQUEST:\n"
            f"{ask}\n\n"
            "### CURRENT CODE:\n```python\n" + base + "\n```"
        )
        out = self.llm(prompt)
        # extract python block
        proposed = base
        if "```" in out:
            try:
                segs = out.split("```")
                for i in range(len(segs)-1):
                    if segs[i].strip().lower().startswith("python"):
                        proposed = segs[i+1]
                        break
            except Exception:
                pass
        else:
            # if no fence, accept full text (risky)
            proposed = out.strip()
        return proposed, out

    def apply_self_patch(self, new_code: str) -> Tuple[bool, str]:
        ok, msg = compile_ok(new_code)
        if not ok:
            self.log("ERROR", f"compile check failed: {msg}")
            return False, msg
        cur = self.current_code()
        diff = unified_diff(cur, new_code, A=f"{self.cell}@current", B="proposed")
        ok2, msg2 = self.host.update_cell_code(self.cell, new_code, diff)
        if ok2:
            self.log("INFO", f"self-update applied; {msg2}")
            # save snapshot for other agents
            self.host.write_bucket_item("code_parts", f"{self.cell}-snapshot-{int(time.time())}", {
                "cell": self.cell, "segments": [{"kind":"other","name":"full","text": new_code}], "ts": now_utc()
            })
            return True, msg2
        else:
            self.log("ERROR", f"self-update failed: {msg2}")
            return False, msg2

    # ---- high-level actions ----
    def spawn(self, name: str) -> str:
        ok, msg = self.host.spawn_cell_from_template(name)
        self.log("INFO" if ok else "ERROR", f"spawn '{name}': {msg}")
        return msg

    def update_from_bucket(self, bucket: str, key: str, target_cell: Optional[str]=None) -> str:
        target = target_cell or self.cell
        rows = self.host.read_bucket_items(bucket, limit=1)
        # fetch the specific key if present
        if key:
            rows = [r for r in rows if r["key"] == key]
        if not rows:
            return "No bucket item found"
        try:
            val = json.loads(rows[0]["value_json"])
            text = ""
            # accept code in common places
            if isinstance(val, dict):
                text = val.get("text") or val.get("code") or ""
            if not text and isinstance(val, dict) and "segments" in val:
                # code_parts style
                segs = val["segments"]
                if segs and isinstance(segs, list) and "text" in segs[0]:
                    text = segs[0]["text"]
            if not text:
                return "Bucket item doesn't contain code"
            ok, msg = compile_ok(text)
            if not ok: return f"Syntax: {msg}"
            cur = self.host.get_cell(target)["code"]
            d = unified_diff(cur, text, A=f"{target}@current", B="bucket:{bucket}/{key}")
            ok2, msg2 = self.host.update_cell_code(target, text, d)
            return msg2 if ok2 else f"Update failed: {msg2}"
        except Exception as e:
            return f"Update error: {e}"

# -------------------------
# Qt Widget (Agent UI)
# -------------------------
class CellWidget(QtWidgets.QWidget):
    def __init__(self, api_obj, cell_name: str):
        super().__init__()
        self.api = api_obj
        self.cell = cell_name
        self.soul = ANTSoul(api_obj, cell_name)
        self._build()

    # GUI
    def _build(self):
        self.setWindowTitle(f"{APP_CELL_TITLE} — {self.cell}")
        layout = QtWidgets.QVBoxLayout(self)

        # Model row
        row = QtWidgets.QHBoxLayout()
        self.cb_model = QtWidgets.QComboBox()
        self.cb_model.setEditable(True)
        ms = self.soul.models()
        self.cb_model.addItems(ms)
        self.cb_model.setCurrentText(DEFAULT_MODEL)
        self.cb_model.currentTextChanged.connect(self.on_model_changed)
        self.btn_models = QtWidgets.QPushButton("↻")
        self.btn_models.setToolTip("Refresh Ollama models")
        self.btn_models.clicked.connect(self.reload_models)
        row.addWidget(QtWidgets.QLabel("Model"))
        row.addWidget(self.cb_model, 1)
        row.addWidget(self.btn_models)
        layout.addLayout(row)

        # Transcript & input
        layout.addWidget(QtWidgets.QLabel("Chat / Commands"))
        self.transcript = QtWidgets.QPlainTextEdit(); self.transcript.setReadOnly(True)
        layout.addWidget(self.transcript, 1)
        inrow = QtWidgets.QHBoxLayout()
        self.input = QtWidgets.QLineEdit(); self.input.setPlaceholderText("Type message or /command.  (/help)")
        self.btn_send = QtWidgets.QPushButton("Send")
        self.btn_send.clicked.connect(self.on_send)
        inrow.addWidget(self.input, 1)
        inrow.addWidget(self.btn_send)
        layout.addLayout(inrow)

        # Buckets viewer
        g = QtWidgets.QGroupBox("Buckets")
        gv = QtWidgets.QVBoxLayout(g)
        f = QtWidgets.QHBoxLayout()
        self.cb_buckets = QtWidgets.QComboBox()
        self.cb_buckets.addItem("Show All")
        for b in self.soul.host.list_buckets():
            self.cb_buckets.addItem(b)
        self.chk_only_mine = QtWidgets.QCheckBox("Only Mine")
        self.chk_only_mine.setChecked(False)
        self.btn_refresh_b = QtWidgets.QPushButton("↻")
        self.btn_refresh_b.clicked.connect(self.refresh_bucket_table)
        f.addWidget(self.cb_buckets, 1)
        f.addWidget(self.chk_only_mine)
        f.addWidget(self.btn_refresh_b)
        gv.addLayout(f)

        self.tbl_b = QtWidgets.QTableWidget(); self.tbl_b.setColumnCount(4)
        self.tbl_b.setHorizontalHeaderLabels(["id","key","value_json","created_at"])
        self.tbl_b.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl_b.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        gv.addWidget(self.tbl_b, 1)

        wr = QtWidgets.QHBoxLayout()
        self.ed_key = QtWidgets.QLineEdit(); self.ed_key.setPlaceholderText("key")
        self.ed_val = QtWidgets.QLineEdit(); self.ed_val.setPlaceholderText('value_json (e.g. {"text":"hello","cell":"%s"} )' % self.cell)
        self.btn_write = QtWidgets.QPushButton("Write")
        self.btn_write.clicked.connect(self.bucket_write)
        wr.addWidget(self.ed_key, 1)
        wr.addWidget(self.ed_val, 2)
        wr.addWidget(self.btn_write)
        gv.addLayout(wr)

        layout.addWidget(g)

        # Quick actions
        actrow = QtWidgets.QHBoxLayout()
        self.btn_diff = QtWidgets.QPushButton("Diff Self from code_parts/latest")
        self.btn_diff.clicked.connect(self.diff_self_latest)
        self.btn_update = QtWidgets.QPushButton("Apply Self from code_parts/latest")
        self.btn_update.clicked.connect(self.update_self_latest)
        self.btn_rollback = QtWidgets.QPushButton("Rollback Self")
        self.btn_rollback.clicked.connect(self.rollback_self)
        self.btn_spawn = QtWidgets.QPushButton("Spawn Sibling")
        self.btn_spawn.clicked.connect(self.spawn_sibling)
        self.btn_signal = QtWidgets.QPushButton("Signal * status")
        self.btn_signal.clicked.connect(self.signal_status)
        actrow.addWidget(self.btn_diff)
        actrow.addWidget(self.btn_update)
        actrow.addWidget(self.btn_rollback)
        actrow.addWidget(self.btn_spawn)
        actrow.addWidget(self.btn_signal)
        layout.addLayout(actrow)

        # style
        self.setStyleSheet("""
            QWidget { color: #ddd; background: #151515; }
            QLineEdit, QPlainTextEdit, QComboBox, QTableWidget { background: #1b1b1b; color: #eee; border: 1px solid #2a2a2a; }
            QPushButton { background: #222; border: 1px solid #2f2f2f; padding: 5px 10px; }
            QPushButton:hover { background: #2a2a2a; }
            QLabel { color: #a7f3d0; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 5px; }
        """)

        # first bucket load
        self.refresh_bucket_table()
        self.log_line("ready")

    def log_line(self, s: str):
        self.transcript.appendPlainText(f"[{now_utc()}] {s}")
        self.transcript.moveCursor(QtGui.QTextCursor.End)

    # --- model events
    def reload_models(self):
        cur = self.cb_model.currentText()
        models = self.soul.models()
        self.cb_model.clear(); self.cb_model.addItems(models)
        if cur in models:
            self.cb_model.setCurrentText(cur)
        else:
            self.cb_model.setCurrentText(DEFAULT_MODEL)

    def on_model_changed(self, t: str):
        self.soul.set_model(t)

    # --- buckets table
    def refresh_bucket_table(self):
        bname = self.cb_buckets.currentText().strip()
        only_mine = self.chk_only_mine.isChecked()
        rows: List[Dict[str,Any]] = []
        if bname == "Show All":
            names = self.soul.host.list_buckets()
            for n in names:
                rows.extend(self.soul.host.read_bucket_items(n, limit=50, only_cell=(self.cell if only_mine else None)))
        else:
            rows = self.soul.host.read_bucket_items(bname, limit=200, only_cell=(self.cell if only_mine else None))

        self.tbl_b.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.tbl_b.setItem(i, 0, QtWidgets.QTableWidgetItem(str(r["id"])))
            self.tbl_b.setItem(i, 1, QtWidgets.QTableWidgetItem(r["key"]))
            self.tbl_b.setItem(i, 2, QtWidgets.QTableWidgetItem(r["value_json"]))
            self.tbl_b.setItem(i, 3, QtWidgets.QTableWidgetItem(r["created_at"] or ""))
        self.tbl_b.resizeColumnsToContents()

    def bucket_write(self):
        b = self.cb_buckets.currentText().strip()
        if b == "Show All":
            QtWidgets.QMessageBox.information(self, "Bucket", "Choose a specific bucket to write.")
            return
        k = self.ed_key.text().strip()
        v = self.ed_val.text().strip()
        if not k or not v: return
        try:
            js = json.loads(v)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"JSON", f"Invalid JSON: {e}")
            return
        # tag with cell for filtering
        if isinstance(js, dict) and "cell" not in js:
            js["cell"] = self.cell
        ok, msg = self.soul.host.write_bucket_item(b, k, js)
        self.log_line(f"[bucket] {msg}")
        self.refresh_bucket_table()

    # --- chat / commands
    def on_send(self):
        text = self.input.text().strip()
        if not text: return
        self.input.clear()

        if text.startswith("/"):
            self.exec_command(text)
            return

        self.log_line(f"You: {text}")
        # Build compact system context for this cell
        ctx = self.build_micro_context()
        prompt = (
            "You are the ANT-cell AI. Use buckets/diffs/signals when proposing changes. "
            "If you propose code for this cell, return EXACTLY one ```python fenced block with the FULL script.\n\n"
            f"### CONTEXT\n{ctx}\n\n### USER\n{text}\n"
        )
        # run in a lightweight thread to avoid blocking UI
        threading.Thread(target=self._llm_async, args=(prompt,), daemon=True).start()

    def _llm_async(self, prompt: str):
        out = self.soul.llm(prompt)
        # post-process in GUI thread
        QtCore.QMetaObject.invokeMethod(self, "_handle_llm_result", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, out))

    @QtCore.pyqtSlot(str)
    def _handle_llm_result(self, out: str):
        self.log_line(f"{self.soul.model}: {out}")
        # Persist transcript
        self.soul.host.write_bucket_item("cell_transcripts", f"{self.cell}-{int(time.time())}",
                                         {"cell": self.cell, "model": self.soul.model, "user": "(inline)", "ai": out, "ts": now_utc()})
        self.soul.remember(f"AI: {out}", tags={"kind":"cell_chat","model": self.soul.model})

        # If the model returned a code block, attempt autovalidate and stage to code_parts
        code = self.extract_code_block(out)
        if code:
            ok, msg = compile_ok(code)
            if ok:
                self.soul.host.write_bucket_item("code_parts", f"{self.cell}-snapshot-{int(time.time())}",
                                                 {"cell": self.cell, "segments":[{"kind":"other","name":"full","text": code}], "ts": now_utc()})
                self.log_line("✓ code snapshot saved to bucket 'code_parts' (not yet applied). Use /update_self_from code_parts <key> to apply.")
            else:
                self.log_line(f"✗ code snapshot invalid: {msg}")

        # If the model emitted /commands inline, try to execute them
        for line in out.splitlines():
            if line.strip().startswith("/"):
                self.exec_command(line.strip())

    def extract_code_block(self, text: str) -> Optional[str]:
        if "```" not in text: return None
        try:
            segs = text.split("```")
            for i in range(len(segs)-1):
                if segs[i].strip().lower().startswith("python"):
                    return segs[i+1]
        except Exception:
            return None
        return None

    def build_micro_context(self) -> str:
        cells = self.soul.host.list_cells()
        names = ", ".join([c["name"] for c in cells])
        buckets = ", ".join(self.soul.host.list_buckets()[:30])
        me = self.soul.host.get_cell(self.cell) or {}
        ver = me.get("version", 1)
        return f"cells=[{names}]  buckets=[{buckets}]  me={self.cell}@v{ver}  time={now_utc()}"

    def exec_command(self, cmdline: str):
        try:
            parts = cmdline.strip().split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "/help":
                self.log_line("Commands: /help, /listcells, /listbuckets, /readb <bucket> [key], "
                              "/writeb <bucket> <key> <json>, /signal <target|*> <kind> <json>, "
                              "/spawn <name>, /diff_self_from <bucket> <key>, "
                              "/update_self_from <bucket> <key>, /update_cell <name> <bucket> <key>, "
                              "/rollback <cell>, /self_mutate, /run_behavior <cell>")
                return

            if cmd == "/listcells":
                cs = self.soul.host.list_cells()
                self.log_line("Cells:\n" + "\n".join([f"- {c['name']} imm={c['immutable']} v={c['version']} len={c['code_len']}" for c in cs]))
                return

            if cmd == "/listbuckets":
                bs = self.soul.host.list_buckets()
                self.log_line("Buckets:\n" + "\n".join([f"- {b}" for b in bs]))
                return

            if cmd == "/readb":
                if not args:
                    self.log_line("usage: /readb <bucket> [key]"); return
                b = args[0]; key = args[1] if len(args)>1 else None
                rows = self.soul.host.read_bucket_items(b, limit=200)
                if key:
                    rows = [r for r in rows if r["key"] == key]
                self.log_line(f"{b}:{key or '*'} → {len(rows)}")
                for r in rows[:20]:
                    self.log_line(f"  - {r['id']} {r['key']} = {r['value_json'][:220]}")
                return

            if cmd == "/writeb":
                if len(args)<3:
                    self.log_line("usage: /writeb <bucket> <key> <json>"); return
                b, k = args[0], args[1]
                js = " ".join(args[2:])
                try:
                    val = json.loads(js)
                except Exception as e:
                    self.log_line(f"Invalid JSON: {e}"); return
                if isinstance(val, dict) and "cell" not in val:
                    val["cell"] = self.cell
                ok, msg = self.soul.host.write_bucket_item(b, k, val)
                self.log_line(msg)
                self.refresh_bucket_table()
                return

            if cmd == "/signal":
                if len(args)<3:
                    self.log_line("usage: /signal <target|*> <kind> <json>"); return
                tgt, kind = args[0], args[1]
                js = " ".join(args[2:])
                try:
                    payload = json.loads(js)
                except Exception as e:
                    self.log_line(f"Invalid JSON: {e}"); return
                self.soul.emit(kind, payload, None if tgt=="*" else tgt)
                self.log_line(f"signal '{kind}' sent → {tgt}")
                return

            if cmd == "/spawn":
                if not args:
                    self.log_line("usage: /spawn <name>"); return
                nm = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in args[0])
                msg = self.soul.spawn(nm)
                self.log_line(msg)
                return

            if cmd == "/diff_self_from":
                if len(args)<2:
                    self.log_line("usage: /diff_self_from <bucket> <key>"); return
                b, k = args[0], args[1]
                rows = self.soul.host.read_bucket_items(b, limit=200)
                rows = [r for r in rows if r["key"] == k]
                if not rows:
                    self.log_line("no bucket item"); return
                val = json.loads(rows[0]["value_json"])
                text = val.get("text") or val.get("code") or ""
                if not text and isinstance(val, dict) and "segments" in val:
                    segs = val["segments"]
                    if segs and "text" in segs[0]:
                        text = segs[0]["text"]
                cur = self.soul.current_code()
                d = unified_diff(cur, text or "", A=f"{self.cell}@current", B=f"bucket:{b}/{k}")
                self.log_line("```diff\n"+(d or "(no changes)")+"\n```")
                return

            if cmd == "/update_self_from":
                if len(args)<2:
                    self.log_line("usage: /update_self_from <bucket> <key>"); return
                b, k = args[0], args[1]
                msg = self.soul.update_from_bucket(b, k, target_cell=None)
                self.log_line(msg)
                return

            if cmd == "/update_cell":
                if len(args)<3:
                    self.log_line("usage: /update_cell <name> <bucket> <key>"); return
                name, b, k = args[0], args[1], args[2]
                msg = self.soul.update_from_bucket(b, k, target_cell=name)
                self.log_line(msg)
                return

            if cmd == "/rollback":
                if not args:
                    self.log_line("usage: /rollback <cell>"); return
                ok, msg = self.soul.host.rollback_cell(args[0])
                self.log_line(msg)
                return

            if cmd == "/self_mutate":
                ask = "Refactor and strengthen autonomy, keep GUI shape, retain all features."
                code, reasoning = self.soul.propose_self_patch(ask)
                ok, msg = compile_ok(code)
                if not ok:
                    self.log_line(f"mutate compile fail: {msg}")
                    return
                self.soul.host.write_bucket_item("code_parts", f"{self.cell}-snapshot-{int(time.time())}",
                                                 {"cell": self.cell, "segments":[{"kind":"other","name":"full","text": code}], "ts": now_utc()})
                self.log_line("mutation snapshot staged in 'code_parts' (use /update_self_from code_parts <key> to apply)")
                return

            if cmd == "/run_behavior":
                if not args:
                    self.log_line("usage: /run_behavior <cell>"); return
                tgt = args[0]
                # We can't run foreign code directly here (immune system does that).
                # Instead signal the immune system to run behavior.
                self.soul.emit("request_run_behavior", {"cell": tgt}, to="immune_system")
                self.log_line(f"requested behavior run for {tgt}")
                return

            self.log_line(f"unknown command: {cmd}. /help")

        except Exception as e:
            tb = traceback.format_exc()
            self.soul.host.error(self.cell, (self.soul.host.get_cell(self.cell) or {}).get("version", 1), tb, {"cmd": cmdline})
            self.log_line(f"[command error] {e}")

    # --- quick action handlers
    def diff_self_latest(self):
        rows = self.soul.host.read_bucket_items("code_parts", limit=50)
        # find the most recent snapshot for this cell
        rows = [r for r in rows if r["key"].startswith(f"{self.cell}-snapshot-")]
        if not rows:
            self.log_line("no self snapshot in 'code_parts'")
            return
        rows.sort(key=lambda r: r["id"], reverse=True)
        val = json.loads(rows[0]["value_json"])
        text = ""
        if "segments" in val and val["segments"]:
            text = val["segments"][0].get("text", "")
        cur = self.soul.current_code()
        d = unified_diff(cur, text or "", A=f"{self.cell}@current", B="latest_snapshot")
        self.log_line("```diff\n"+(d or "(no changes)")+"\n```")

    def update_self_latest(self):
        rows = self.soul.host.read_bucket_items("code_parts", limit=50)
        rows = [r for r in rows if r["key"].startswith(f"{self.cell}-snapshot-")]
        if not rows:
            self.log_line("no self snapshot in 'code_parts'")
            return
        rows.sort(key=lambda r: r["id"], reverse=True)
        val = json.loads(rows[0]["value_json"])
        text = ""
        if "segments" in val and val["segments"]:
            text = val["segments"][0].get("text", "")
        ok, msg = compile_ok(text)
        if not ok:
            self.log_line(f"syntax: {msg}"); return
        cur = self.soul.current_code()
        d = unified_diff(cur, text, A=f"{self.cell}@current", B="latest_snapshot")
        ok2, msg2 = self.soul.host.update_cell_code(self.cell, text, d)
        self.log_line(msg2 if ok2 else f"update failed: {msg2}")

    def rollback_self(self):
        ok, msg = self.soul.host.rollback_cell(self.cell)
        self.log_line(msg)

    def spawn_sibling(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Spawn Sibling", "Name:")
        if not ok or not name.strip(): return
        nm = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name.strip())
        msg = self.soul.spawn(nm)
        self.log_line(msg)

    def signal_status(self):
        self.soul.emit("status", {"msg": f"{self.cell} alive", "ts": now_utc()}, to=None)
        self.log_line("status broadcast sent")

# -------------------------
# API for Immune System
# -------------------------
def build_gui(api):
    # 'api' provides log/emit/remember/metadata; we go autonomous via Host()
    cell_name = api.metadata().get("name") if hasattr(api, "metadata") else None
    # If host didn't set name in metadata, we can’t guess reliably; fallback to 'cell_1'
    cell_name = cell_name or "cell_1"
    w = CellWidget(api, cell_name)
    return w

def core_behavior(api):
    """
    A lightweight "heartbeat" that:
      - Writes a tiny note to knowledge
      - Emits a status signal
    The heavier autonomy lives in the GUI + /commands + LLM interactions.
    """
    cell_name = "unknown"
    try:
        md = api.metadata() if hasattr(api, "metadata") else {}
        cell_name = md.get("name", "cell_1")
    except Exception:
        pass
    try:
        # remember + status
        api.remember(f"{cell_name} heartbeat @ {now_utc()}", tags={"kind":"heartbeat"})
        api.emit("status", {"msg": f"{cell_name} heartbeat"}, None)
        api.log("INFO", f"{cell_name} heartbeat")
        return {"ok": True}
    except Exception as e:
        tb = traceback.format_exc()
        # We don't have direct error() here, so use remember/log
        try:
            api.log("ERROR", f"heartbeat error: {e}")
            api.remember(f"heartbeat error: {e}", tags={"kind":"error"})
        except Exception:
            pass
        return {"ok": False, "error": str(e)}
```

**Classes:** Host, ANTSoul, CellWidget
**Functions:** now_utc(), unified_diff(a, b, A, B), compile_ok(code), http_json(url, payload, timeout), list_ollama_models(), build_gui(api), core_behavior(api)


## Module `Loader\immune_system.py`

```python
#!/usr/bin/env python3
# immune_system.py — Immune System UI with autonomous Immune AI (Ollama)
# - Zoomable canvas w/ snap grid; spawn/merge/unmerge visual cells
# - Cells list + Inspector (edit, save, run, rollback)
# - Global logs (no forced autoscroll)
# - Host Browser (tables, ad-hoc SELECT)
# - Buckets dock (browse/write)
# - Immune AI chat (Ollama): auto-ingests a fresh System README snapshot each send
# - Maintenance loop: correlate logs<->diffs → write diff_notes bucket, then release old logs
#
# Run:
#   SINGLECELL_DB=path/to/host.db python immune_system.py
#   # or
#   python immune_system.py path/to/host.db
#
# Requires: PyQt5, requests

import os, sys, json, sqlite3, traceback, time, ast, types, difflib, requests
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets

APP_NAME = "ANT Immune System"
GRID_SIZE = 100

# -------- Ollama settings --------
OLLAMA_URL = "http://localhost:11434"
OLLAMA_GENERATE = f"{OLLAMA_URL}/api/generate"
OLLAMA_TAGS     = f"{OLLAMA_URL}/api/tags"
DEFAULT_MODELS_FALLBACK = ["llama3", "mistral", "qwen2", "phi3", "tinyllama"]

# -------- Retention / maintenance --------
LOG_RETAIN_MAX      = 1500   # keep at most this many newest log rows globally
LOG_PROCESS_BATCH   = 500    # how many new logs to inspect per maintenance pass
DIFF_RECENT_SECONDS = 3600   # lookback window when correlating diffs to updates

def now_utc(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# ==========================
# Database access layer
# ==========================

class DB:
    def __init__(self, path): self.path=Path(path)
    def connect(self): 
        c=sqlite3.connect(str(self.path)); c.row_factory=sqlite3.Row; return c
    def ensure(self):
        c=self.connect(); u=c.cursor()
        u.executescript("""
        PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS cells (
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, parent_id INTEGER,
          cluster_id TEXT, immutable INTEGER DEFAULT 0, code TEXT NOT NULL,
          metadata_json TEXT, version INTEGER DEFAULT 1,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS cell_versions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, version INTEGER,
          code TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS diffs(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, from_version INTEGER,
          to_version INTEGER, diff_type TEXT, diff_text TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS signals(
          id INTEGER PRIMARY KEY AUTOINCREMENT, from_cell TEXT, to_cell TEXT,
          kind TEXT, payload_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS errors(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, version INTEGER,
          traceback TEXT, context_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          resolved_by TEXT
        );
        CREATE TABLE IF NOT EXISTS knowledge(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, content_text TEXT,
          embedding TEXT, tags_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS assets(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, type TEXT,
          data BLOB, path TEXT, meta_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS antapi(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, code TEXT NOT NULL,
          version INTEGER DEFAULT 1, metadata_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS logs(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, level TEXT, message TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS buckets(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, purpose TEXT,
          schema_json TEXT, mutable INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS bucket_items(
          id INTEGER PRIMARY KEY AUTOINCREMENT, bucket_name TEXT, key TEXT,
          value_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(bucket_name, key)
        );
        CREATE TABLE IF NOT EXISTS readmes(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, content_markdown TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        c.commit(); c.close()

    # --- meta ---
    def meta_set(self,k,v): 
        c=self.connect();x=c.cursor()
        x.execute("INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)",(k,v))
        c.commit(); c.close()

    def meta_get(self,k): 
        c=self.connect();x=c.cursor()
        x.execute("SELECT value FROM meta WHERE key=?",(k,))
        r=x.fetchone(); c.close(); 
        return r["value"] if r else None

    # --- cells ---
    def cells_all(self):
        c=self.connect();x=c.cursor(); x.execute("SELECT * FROM cells ORDER BY name"); r=x.fetchall(); c.close(); return r

    def cell_get(self,name):
        c=self.connect();x=c.cursor(); x.execute("SELECT * FROM cells WHERE name=?",(name,)); r=x.fetchone(); c.close(); return r

    def cell_insert(self,name,code,immutable=0,parent=None,pos=(0,0),size=(800,800)):
        meta={"pos":{"x":pos[0],"y":pos[1]},"size":{"w":size[0],"h":size[1]}}
        c=self.connect();x=c.cursor()
        x.execute("INSERT INTO cells(name,parent_id,cluster_id,immutable,code,metadata_json,version) VALUES (?,?,?,?,?,?,1)",
                  (name,immutable,code,json.dumps(meta)))
        x.execute("INSERT INTO cell_versions(cell_name,version,code) VALUES(?,?,?)",(name,1,code))
        c.commit(); c.close()

    def cell_update_code(self,name,new_code,diff_text=""):
        c=self.connect();x=c.cursor()
        x.execute("SELECT version,immutable FROM cells WHERE name=?",(name,)); r=x.fetchone()
        if not r: c.close(); raise RuntimeError("not found")
        if r["immutable"]: c.close(); raise RuntimeError("immutable")
        nv=r["version"]+1
        x.execute("UPDATE cells SET code=?,version=? WHERE name=?", (new_code,nv,name))
        x.execute("INSERT INTO cell_versions(cell_name,version,code) VALUES(?,?,?)",(name,nv,new_code))
        if diff_text:
            x.execute("INSERT INTO diffs(cell_name,from_version,to_version,diff_type,diff_text) VALUES(?,?,?,?,?)",
                      (name,nv-1,nv,"unified",diff_text))
        c.commit(); c.close()

    def cell_rollback(self,name):
        c=self.connect();x=c.cursor()
        x.execute("SELECT version,immutable FROM cells WHERE name=?",(name,)); r=x.fetchone()
        if not r: c.close(); raise RuntimeError("not found")
        if r["immutable"]: c.close(); raise RuntimeError("immutable")
        v=r["version"]; 
        if v<=1: c.close(); raise RuntimeError("no earlier version")
        x.execute("SELECT code FROM cell_versions WHERE cell_name=? AND version=?",(name,v-1)); pr=x.fetchone()
        if not pr: c.close(); raise RuntimeError("missing prior")
        x.execute("UPDATE cells SET code=?,version=? WHERE name=?",(pr["code"],v-1,name))
        c.commit(); c.close(); return v-1

    # --- logs/signals/knowledge/buckets ---
    def log(self,cell,level,msg):
        c=self.connect();x=c.cursor()
        x.execute("INSERT INTO logs(cell_name,level,message) VALUES(?,?,?)",(cell,level,msg))
        c.commit(); c.close()

    def emit(self,frm,kind,payload,to=None):
        c=self.connect();x=c.cursor()
        x.execute("INSERT INTO signals(from_cell,to_cell,kind,payload_json,created_at) VALUES(?,?,?,?,?)",
                  (frm,to,kind,json.dumps(payload),now_utc()))
        c.commit(); c.close()

    def list_buckets(self)->List[str]:
        c=self.connect(); x=c.cursor(); x.execute("SELECT name FROM buckets ORDER BY name"); rows=[r[0] for r in x.fetchall()]; c.close(); return rows

    def bucket_items(self,bucket:str, limit:int=200):
        c=self.connect(); x=c.cursor(); x.execute("SELECT id, key, value_json, created_at FROM bucket_items WHERE bucket_name=? ORDER BY id DESC LIMIT ?", (bucket, limit))
        rows=x.fetchall(); c.close(); return rows

    def bucket_write(self,bucket:str, key:str, value:Dict[str,Any]):
        c=self.connect(); x=c.cursor(); 
        x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name,key,value_json) VALUES(?,?,?)", (bucket,key,json.dumps(value)))
        c.commit(); c.close()

# Light API wrapper for cells (what cells see)
class ANTApi:
    def __init__(self, db: DB, cell_name: str): self.db=db; self.cell=cell_name
    def log(self,level,msg): self.db.log(self.cell,level,msg)
    def emit(self,kind,payload,to=None): self.db.emit(self.cell,kind,payload,to)
    def remember(self,text,tags=None):
        c=self.db.connect();x=c.cursor()
        x.execute("INSERT INTO knowledge(cell_name,content_text,embedding,tags_json) VALUES(?,?,?,?)",
                  (self.cell,text,None,json.dumps(tags or {}))); c.commit(); c.close()
    def metadata(self): 
        c=self.db.connect();x=c.cursor()
        x.execute("SELECT metadata_json FROM cells WHERE name=?",(self.cell,))
        r=x.fetchone(); c.close()
        return json.loads(r["metadata_json"] or "{}") if r else {}

# --------------------------
# Helpers
# --------------------------

def compile_ok(code:str):
    try: ast.parse(code); return True,""
    except SyntaxError as e: return False,f"SyntaxError: {e}"

def http_json(url:str, payload:Dict[str,Any], timeout:float=240.0)->Dict[str,Any]:
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

def list_ollama_models()->List[str]:
    try:
        r = requests.get(OLLAMA_TAGS, timeout=4.0)
        r.raise_for_status()
        data = r.json()
        names=[]
        for m in data.get("models",[]):
            nm = m.get("name")
            if nm:
                base=nm.split(":")[0]
                if base not in names:
                    names.append(base)
        return names or DEFAULT_MODELS_FALLBACK
    except Exception:
        return DEFAULT_MODELS_FALLBACK

def unified_diff(a:str,b:str, A="current", B="proposed")->str:
    lines=list(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=A, tofile=B, lineterm=""))
    return "".join(lines)

# ==========================
# Qt scene items (canvas)
# ==========================

class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self,grid): super().__init__(); self.grid=grid; self.show_grid=False
    def drawBackground(self,p,rect):
        if not self.show_grid: return
        left=int(rect.left())-(int(rect.left())%self.grid); top=int(rect.top())-(int(rect.top())%self.grid)
        pen=QtGui.QPen(QtGui.QColor(60,60,60)); pen.setWidth(0); p.setPen(pen)
        lines=[]
        for x in range(left,int(rect.right()),self.grid): lines.append(QtCore.QLineF(x,rect.top(),x,rect.bottom()))
        for y in range(top,int(rect.bottom()),self.grid): lines.append(QtCore.QLineF(rect.left(),y,rect.right(),y))
        p.drawLines(lines)

class CellItem(QtWidgets.QGraphicsRectItem):
    def __init__(self,name,widget,grid): super().__init__(); self.cell=name; self.grid=grid
        self.setFlags(self.ItemIsMovable|self.ItemIsSelectable|self.ItemSendsScenePositionChanges)
        self.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0)))
        self.proxy=QtWidgets.QGraphicsProxyWidget(self); self.proxy.setWidget(widget)
        sz=widget.sizeHint(); self.setRect(0,0,sz.width(),sz.height())
    def snap(self,p):
        x=round(p.x()/self.grid)*self.grid; y=round(p.y()/self.grid)*self.grid
        return QtCore.QPointF(x,y)
    def itemChange(self,ch,val):
        if ch==self.ItemPositionChange: return self.snap(val)
        return super().itemChange(ch,val)

class View(QtWidgets.QGraphicsView):
    def __init__(self,scene): super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(self.AnchorUnderMouse)
    def wheelEvent(self,e):
        self.scale(1.15 if e.angleDelta().y()>0 else 1/1.15, 1.15 if e.angleDelta().y()>0 else 1/1.15)

# ==========================
# Immune AI dock (chat)
# ==========================

class ImmuneAI(QtWidgets.QWidget):
    finishedOk = QtCore.pyqtSignal(str)
    failed     = QtCore.pyqtSignal(str)

    def __init__(self, db: DB):
        super().__init__()
        self.db = db
        self.models = list_ollama_models()
        self._build()

    def _build(self):
        L = QtWidgets.QVBoxLayout(self)

        row = QtWidgets.QHBoxLayout()
        self.cb_model = QtWidgets.QComboBox(); self.cb_model.addItems(self.models)
        self.btn_models = QtWidgets.QPushButton("↻ Models"); self.btn_models.clicked.connect(self.reload_models)
        row.addWidget(QtWidgets.QLabel("Model")); row.addWidget(self.cb_model); row.addWidget(self.btn_models); row.addStretch(1)
        L.addLayout(row)

        self.transcript = QtWidgets.QPlainTextEdit(); self.transcript.setReadOnly(True)
        self.input = QtWidgets.QLineEdit(); self.input.setPlaceholderText("Ask Immune AI… (/help for commands)")
        row2 = QtWidgets.QHBoxLayout()
        self.btn_send = QtWidgets.QPushButton("Send"); self.btn_send.clicked.connect(self.send)
        self.btn_send.setDefault(True)
        row2.addWidget(self.btn_send); row2.addStretch(1)
        L.addWidget(QtWidgets.QLabel("Transcript")); L.addWidget(self.transcript,1)
        L.addWidget(QtWidgets.QLabel("Prompt")); L.addWidget(self.input); L.addLayout(row2)

        self.setStyleSheet("""
            QWidget { color: #ddd; background: #151515; }
            QLineEdit, QPlainTextEdit, QComboBox { background: #1b1b1b; color: #eee; border: 1px solid #2a2a2a; }
            QPushButton { background: #222; border: 1px solid #2f2f2f; padding: 5px 10px; }
            QPushButton:hover { background: #2a2a2a; }
            QLabel { color: #a7f3d0; }
        """)

    def reload_models(self):
        cur = self.cb_model.currentText()
        self.models = list_ollama_models()
        self.cb_model.clear(); self.cb_model.addItems(self.models)
        if cur in self.models: self.cb_model.setCurrentText(cur)

    def append_line(self, txt: str):
        self.transcript.appendPlainText(txt)
        self.transcript.moveCursor(QtGui.QTextCursor.End)

    # ---- README / Context ----

    def build_system_readme(self, include_samples: bool = True) -> str:
        """Snapshot the current system (cells/buckets/diffs/logs) into a Markdown README string."""
        c = self.db.connect()
        try:
            x = c.cursor()
            # tables
            x.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [r[0] for r in x.fetchall()]

            # cells
            x.execute("SELECT name, immutable, version, length(code) FROM cells ORDER BY name")
            cells = [{"name":r[0], "immutable":r[1], "version":r[2], "code_len":r[3]} for r in x.fetchall()]

            # buckets
            x.execute("SELECT name, purpose FROM buckets ORDER BY name")
            buckets = [{"name":r[0], "purpose":r[1]} for r in x.fetchall()]

            # diffs recent window
            x.execute("SELECT id, cell_name, from_version, to_version, diff_type, substr(diff_text,1,400) snippet, created_at FROM diffs ORDER BY id DESC LIMIT 50")
            diffs = [{"id":r[0], "cell":r[1], "from":r[2], "to":r[3], "type":r[4], "snippet":r[5], "at":r[6]} for r in x.fetchall()]

            # logs recent
            x.execute("SELECT id, cell_name, level, message, created_at FROM logs ORDER BY id DESC LIMIT 80")
            logs = [{"id":r[0], "cell":r[1], "level":r[2], "msg":r[3], "at":r[4]} for r in x.fetchall()]

            # buckets sample items (very light)
            samples = []
            if include_samples:
                for b in buckets:
                    x.execute("SELECT key, substr(value_json,1,280) FROM bucket_items WHERE bucket_name=? ORDER BY id DESC LIMIT 3", (b["name"],))
                    items = [{"key":k, "value_snippet":v} for (k,v) in x.fetchall()]
                    if items:
                        samples.append({"bucket": b["name"], "items": items})

        finally:
            c.close()

        md = []
        md.append("# ANT Immune System — README Snapshot")
        md.append(f"- Generated: {now_utc()}")
        md.append("## Tables")
        md.append("```\n" + "\n".join(tables) + "\n```")
        md.append("## Cells")
        for c in cells:
            md.append(f"- **{c['name']}**  imm={c['immutable']}  v={c['version']}  code_len={c['code_len']}")
        md.append("## Buckets")
        for b in buckets:
            md.append(f"- **{b['name']}** — {b['purpose']}")
        if samples:
            md.append("## Bucket Samples")
            for s in samples:
                md.append(f"### {s['bucket']}")
                for it in s["items"]:
                    md.append(f"- `{it['key']}` → {it['value_snippet']}")
        md.append("## Recent Diffs")
        for d in diffs:
            md.append(f"- #{d['id']}  {d['cell']} {d['from']}→{d['to']} ({d['type']}), {d['at']}\n  ```\n{d['snippet']}\n  ```")
        md.append("## Recent Logs")
        for L in logs:
            md.append(f"- [{L['id']}] {L['at']}  {L['cell']} {L['level']}: {L['msg']}")
        md.append("## Instructions for Agents")
        md.append("- Treat this file as source of truth. Contribute to buckets, write diffs, minimize drift.")
        md.append("- Use /commands to orchestrate updates via Immune AI or cell UIs.")

        return "\n".join(md)

    def persist_readme(self, text: str) -> str:
        """Save to readmes (unique name) and bucket_items('system_readmes'). Return name."""
        name = f"IMMUNE_README_{int(time.time())}"
        c = self.db.connect()
        try:
            x = c.cursor()
            # readmes
            x.execute("INSERT OR REPLACE INTO readmes(name,content_markdown) VALUES(?,?)", (name, text))
            # buckets
            # ensure system_readmes bucket exists
            x.execute("INSERT OR IGNORE INTO buckets(name,purpose,schema_json,mutable) VALUES(?,?,?,1)",
                      ("system_readmes", "System README snapshots", json.dumps({"type":"string"})))
            x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name,key,value_json) VALUES(?,?,?)",
                      ("system_readmes", name, json.dumps({"markdown": text, "ts": now_utc()})))
            self.db.log("immune_system","INFO",f"Snapshot README {name}")
            c.commit()
        finally:
            c.close()
        return name

    def send(self):
        prompt = self.input.text().strip()
        if not prompt: return

        # Commands first
        if prompt.startswith("/"):
            self._handle_command(prompt)
            return

        # Build and persist a fresh README snapshot before answering
        readme = self.build_system_readme(include_samples=True)
        rname  = self.persist_readme(readme)

        self.append_line(f"You: {prompt}")
        model = self.cb_model.currentText().strip() or DEFAULT_MODELS_FALLBACK[0]
        full_prompt = (
            "You are the Immune System AI. You can reason about the whole program, its host DB, "
            "cells, buckets, diffs, logs, and propose /commands to improve it.\n\n"
            f"### SYSTEM README ({rname})\n{readme}\n\n"
            f"### USER PROMPT:\n{prompt}\n\n"
            "If you propose code, include a fenced ```python block. If you propose actions, use /commands.\n"
        )
        try:
            resp = http_json(OLLAMA_GENERATE, {"model": model, "prompt": full_prompt, "stream": False}, timeout=240.0)
            text = (resp.get("response") or "").strip()
            self.append_line(f"{model}: {text}")

            # Archive transcript to knowledge + buckets
            self._persist_chat(prompt, text)

            # Heuristic: if AI proposed a /command, surface hint
            if "\n/" in text or text.startswith("/"):
                self.append_line("(Hint: Detected possible /command(s). You can paste & send them here.)")

        except Exception as e:
            self.append_line(f"[LLM ERROR] {e}")
            self.db.log("immune_system","ERROR", f"AI call failed: {e}")

    def _persist_chat(self, user: str, ai: str):
        c = self.db.connect()
        try:
            x = c.cursor()
            # knowledge
            x.execute("INSERT INTO knowledge(cell_name,content_text,embedding,tags_json) VALUES(?,?,?,?)",
                      ("immune_system", f"USER: {user}\nAI: {ai}", None, json.dumps({"kind":"immune_chat","ts": now_utc()})))
            # bucket transcript
            x.execute("INSERT OR IGNORE INTO buckets(name,purpose,schema_json,mutable) VALUES(?,?,?,1)",
                      ("immune_transcripts","Immune AI chat transcripts", json.dumps({"type":"object"})))
            key = f"chat-{int(time.time())}"
            x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name,key,value_json) VALUES(?,?,?)",
                      ("immune_transcripts", key, json.dumps({"user": user, "ai": ai, "ts": now_utc()})))
            c.commit()
        finally:
            c.close()

    # ---------- /commands (immune-level) ----------
    def _handle_command(self, cmdline: str):
        try:
            parts = cmdline.strip().split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "/help":
                self.append_line("Commands: /help, /listcells, /listbuckets, /read <bucket> [key], "
                                 "/write <bucket> <key> <json>, /spawn <cell>, /diff <cell>, "
                                 "/signal <target|*> <kind> <json>, /update <cell>, /rollback <cell>")
                return

            if cmd == "/listcells":
                c = self.db.connect(); x = c.cursor(); x.execute("SELECT name, immutable, version FROM cells ORDER BY name")
                rows = x.fetchall(); c.close()
                self.append_line("Cells:\n" + "\n".join([f"- {r['name']}  imm={r['immutable']} v={r['version']}" for r in rows]))
                return

            if cmd == "/listbuckets":
                names = self.db.list_buckets()
                self.append_line("Buckets:\n" + "\n".join([f"- {n}" for n in names]))
                return

            if cmd == "/read":
                if not args:
                    self.append_line("Usage: /read <bucket> [key]")
                    return
                b = args[0]; key = args[1] if len(args)>1 else None
                c = self.db.connect()
                try:
                    x=c.cursor()
                    if key:
                        x.execute("SELECT id, key, value_json FROM bucket_items WHERE bucket_name=? AND key=? ORDER BY id DESC LIMIT 200",(b,key))
                    else:
                        x.execute("SELECT id, key, value_json FROM bucket_items WHERE bucket_name=? ORDER BY id DESC LIMIT 200",(b,))
                    rows=x.fetchall()
                finally:
                    c.close()
                self.append_line(f"/read {b} {key or ''} → {len(rows)} item(s)")
                for r in rows[:30]:
                    self.append_line(f" - {r['id']} {r['key']} = {r['value_json'][:220]}")
                return

            if cmd == "/write":
                if len(args)<3:
                    self.append_line("Usage: /write <bucket> <key> <json>")
                    return
                b, k = args[0], args[1]
                js = " ".join(args[2:])
                try:
                    val = json.loads(js)
                except Exception as e:
                    self.append_line(f"Invalid JSON: {e}"); return
                self.db.bucket_write(b,k,val)
                self.append_line(f"✓ wrote to {b}:{k}")
                return

            if cmd == "/spawn":
                if not args:
                    self.append_line("Usage: /spawn <cell>"); return
                name = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in args[0])
                # clone from cell_0
                c = self.db.connect(); x=c.cursor()
                try:
                    x.execute("SELECT code FROM cells WHERE name='cell_0'")
                    row=x.fetchone()
                    code=row['code'] if row else "from PyQt5 import QtWidgets\n\ndef build_gui(api):\n    w=QtWidgets.QWidget();QtWidgets.QVBoxLayout(w).addWidget(QtWidgets.QLabel('new_cell'))\n    return w\n\ndef core_behavior(api):\n    return {'ok': True}\n"
                    meta={"pos":{"x":0,"y":0},"size":{"w":800,"h":800},"role":"active"}
                    x.execute("INSERT INTO cells(name, parent_id, cluster_id, immutable, code, metadata_json, version) VALUES (?,?,NULL,0,?,?,1)", (name, code, json.dumps(meta)))
                    x.execute("INSERT INTO cell_versions(cell_name, version, code) VALUES (?,?,?)", (name,1,code))
                    c.commit()
                    self.append_line(f"Spawned {name} from cell_0")
                    self.db.log("immune_system","INFO",f"spawn {name}")
                finally:
                    c.close()
                return

            if cmd == "/diff":
                if not args:
                    self.append_line("Usage: /diff <cell>")
                    return
                cell = args[0]
                c = self.db.connect()
                try:
                    x=c.cursor(); x.execute("SELECT code FROM cells WHERE name=?", (cell,)); row=x.fetchone()
                finally:
                    c.close()
                if not row:
                    self.append_line("Cell not found."); return
                current = row["code"]
                # show against last diff target text stored in bucket 'code_parts' (if any)
                # fetch last snapshot
                c = self.db.connect()
                try:
                    x=c.cursor()
                    x.execute("SELECT value_json FROM bucket_items WHERE bucket_name='code_parts' AND key LIKE ? ORDER BY id DESC LIMIT 1", (f"{cell}-snapshot-%",))
                    rr=x.fetchone()
                finally:
                    c.close()
                proposed = ""
                if rr:
                    try:
                        proposed = json.loads(rr["value_json"])["segments"][0]["text"]
                    except Exception:
                        proposed = ""
                if not proposed:
                    self.append_line("(No recent proposed snapshot in code_parts; diff vs empty)")
                d=unified_diff(current, proposed or "", A=f"{cell}@current", B="proposed")
                self.append_line("```diff\n"+(d or "(no changes)")+"\n```")
                return

            if cmd == "/signal":
                if len(args)<3:
                    self.append_line("Usage: /signal <target|*> <kind> <json>"); return
                tgt, kind, js = args[0], args[1], " ".join(args[2:])
                try:
                    payload=json.loads(js)
                except Exception as e:
                    self.append_line(f"Invalid JSON: {e}"); return
                self.db.emit("immune_system", kind, payload, None if tgt=="*" else tgt)
                self.append_line(f"Signal '{kind}' sent to {tgt}")
                return

            if cmd == "/update":
                if not args:
                    self.append_line("Usage: /update <cell> (applies last code_parts snapshot)"); return
                cell=args[0]
                # find last snapshot
                c = self.db.connect()
                try:
                    x=c.cursor()
                    x.execute("SELECT code, immutable FROM cells WHERE name=?", (cell,))
                    row=x.fetchone()
                    if not row: self.append_line("Cell not found."); return
                    if row["immutable"]==1: self.append_line("Immutable cell."); return
                    current=row["code"]

                    x.execute("SELECT value_json FROM bucket_items WHERE bucket_name='code_parts' AND key LIKE ? ORDER BY id DESC LIMIT 1", (f"{cell}-snapshot-%",))
                    rr=x.fetchone()
                    if not rr: self.append_line("No snapshot in code_parts."); return
                    proposed = json.loads(rr["value_json"])["segments"][0]["text"]
                    ok,msg = compile_ok(proposed)
                    if not ok: self.append_line(f"Syntax: {msg}"); return
                    d = unified_diff(current, proposed, A=f"{cell}@current", B="proposed")
                    # apply
                    x.execute("UPDATE cells SET code=?, version=version+1 WHERE name=?", (proposed, cell))
                    x.execute("INSERT INTO cell_versions(cell_name, version, code) SELECT name, version, code FROM cells WHERE name=?", (cell,))
                    x.execute("INSERT INTO diffs(cell_name,from_version,to_version,diff_type,diff_text) VALUES ( (?), (SELECT MAX(version)-1 FROM cells WHERE name=?), (SELECT MAX(version) FROM cells WHERE name=?), 'unified', ? )", (cell, cell, cell, d))
                    c.commit()
                finally:
                    c.close()
                self.append_line(f"Updated {cell} with latest snapshot.")
                self.db.log("immune_system","INFO",f"update {cell}")
                return

            if cmd == "/rollback":
                if not args:
                    self.append_line("Usage: /rollback <cell>"); return
                cell=args[0]
                try:
                    self.db.cell_rollback(cell)
                    self.append_line(f"Rolled back {cell}")
                    self.db.log("immune_system","WARN",f"rollback {cell}")
                except Exception as e:
                    self.append_line(f"Rollback error: {e}")
                return

            self.append_line(f"Unknown command: {cmd}. Try /help")

        except Exception as e:
            self.append_line(f"[command error] {e}")
            self.db.log("immune_system","ERROR", f"immune_command: {e}")

# ==========================
# Main Window
# ==========================

class UI(QtWidgets.QMainWindow):
    pollMs=1500
    def __init__(self,db:DB):
        super().__init__(); self.db=db
        self.setWindowTitle(APP_NAME); self.resize(1440,920)
        self.scene=GridScene(GRID_SIZE); self.view=View(self.scene); self.setCentralWidget(self.view)
        self.items={}
        self._make_docks(); self._toolbar()
        self.ensure_cell1()
        self.populate()
        self.timer=QtCore.QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(self.pollMs)

    # ---------- Top toolbar ----------
    def _toolbar(self):
        tb=self.addToolBar("Main"); tb.setMovable(False)
        a_center=QtWidgets.QAction("Center",self); a_center.triggered.connect(self.center_cell1); tb.addAction(a_center)
        self.act_grid=QtWidgets.QAction("Toggle Grid",self,checkable=True); self.act_grid.triggered.connect(self.toggle_grid); tb.addAction(self.act_grid)
        a_spawn=QtWidgets.QAction("Spawn Cell",self); a_spawn.triggered.connect(self.spawn_cell); tb.addAction(a_spawn)
        a_merge=QtWidgets.QAction("Merge (visual)",self); a_merge.triggered.connect(self.merge_selected); tb.addAction(a_merge)
        a_unmerge=QtWidgets.QAction("Unmerge",self); a_unmerge.triggered.connect(self.unmerge_selected); tb.addAction(a_unmerge)
        a_protein=QtWidgets.QAction("Inject Protein",self); a_protein.triggered.connect(self.inject_protein); tb.addAction(a_protein)
        a_refresh=QtWidgets.QAction("Refresh",self); a_refresh.triggered.connect(self.populate); tb.addAction(a_refresh)

    # ---------- Docks ----------
    def _make_docks(self):
        # Cells
        d=QtWidgets.QDockWidget("Cells",self); self.list=QtWidgets.QListWidget()
        self.list.itemSelectionChanged.connect(self.on_sel); d.setWidget(self.list); self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,d)

        # Inspector
        d2=QtWidgets.QDockWidget("Inspector",self); w=QtWidgets.QWidget(); v=QtWidgets.QVBoxLayout(w)
        self.lbl=QtWidgets.QLabel("—"); v.addWidget(self.lbl)
        self.ed=QtWidgets.QPlainTextEdit(); mono=QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont); self.ed.setFont(mono); v.addWidget(self.ed,1)
        row=QtWidgets.QHBoxLayout(); self.b_save=QtWidgets.QPushButton("Save"); self.b_save.clicked.connect(self.save_code)
        self.b_run=QtWidgets.QPushButton("Run Behavior"); self.b_run.clicked.connect(self.run_behavior)
        self.b_rb=QtWidgets.QPushButton("Rollback"); self.b_rb.clicked.connect(self.rollback)
        row.addWidget(self.b_save); row.addWidget(self.b_run); row.addWidget(self.b_rb); v.addLayout(row)
        d2.setWidget(w); self.addDockWidget(QtCore.Qt.RightDockWidgetArea,d2)

        # Global Log
        d3=QtWidgets.QDockWidget("Global Log",self); w3=QtWidgets.QWidget(); v3=QtWidgets.QVBoxLayout(w3)
        frow=QtWidgets.QHBoxLayout(); self.f_cell=QtWidgets.QLineEdit(); self.f_cell.setPlaceholderText("cell filter"); self.f_level=QtWidgets.QComboBox(); self.f_level.addItems(["","INFO","WARN","ERROR"])
        b=QtWidgets.QPushButton("Apply"); b.clicked.connect(self.refresh_logs)
        frow.addWidget(self.f_cell); frow.addWidget(self.f_level); frow.addWidget(b); v3.addLayout(frow)
        self.log=QtWidgets.QPlainTextEdit(); self.log.setReadOnly(True); v3.addWidget(self.log,1)
        d3.setWidget(w3); self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,d3)

        # Host Browser
        d4=QtWidgets.QDockWidget("Host Browser",self); w4=QtWidgets.QWidget(); v4=QtWidgets.QVBoxLayout(w4)
        self.tables=QtWidgets.QComboBox(); bp=QtWidgets.QPushButton("Preview"); bp.clicked.connect(self.preview)
        hr=QtWidgets.QHBoxLayout(); hr.addWidget(self.tables,1); hr.addWidget(bp); v4.addLayout(hr)
        self.sql=QtWidgets.QPlainTextEdit(); self.sql.setPlaceholderText("SELECT ..."); v4.addWidget(self.sql,1)
        lr=QtWidgets.QHBoxLayout(); self.lim=QtWidgets.QSpinBox(); self.lim.setRange(1,100000); self.lim.setValue(200)
        bx=QtWidgets.QPushButton("Run"); bx.clicked.connect(self.exec_select); lr.addWidget(self.lim); lr.addStretch(1); lr.addWidget(bx); v4.addLayout(lr)
        self.table=QtWidgets.QTableWidget(); v4.addWidget(self.table,2)
        d4.setWidget(w4); self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,d4)

        # Buckets
        d5=QtWidgets.QDockWidget("Buckets", self); w5=QtWidgets.QWidget(); v5=QtWidgets.QVBoxLayout(w5)
        rowb=QtWidgets.QHBoxLayout()
        self.cb_bucket = QtWidgets.QComboBox(); self.cb_bucket.addItem("—")
        self.btn_buckets = QtWidgets.QPushButton("↻"); self.btn_buckets.clicked.connect(self.refresh_buckets)
        rowb.addWidget(QtWidgets.QLabel("Bucket")); rowb.addWidget(self.cb_bucket,1); rowb.addWidget(self.btn_buckets)
        v5.addLayout(rowb)
        self.tbl_b = QtWidgets.QTableWidget(); self.tbl_b.setColumnCount(4)
        self.tbl_b.setHorizontalHeaderLabels(["id","key","value_json","created_at"])
        self.tbl_b.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl_b.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        v5.addWidget(self.tbl_b,1)
        roww = QtWidgets.QHBoxLayout()
        self.ed_key = QtWidgets.QLineEdit(); self.ed_key.setPlaceholderText("key")
        self.ed_val = QtWidgets.QLineEdit(); self.ed_val.setPlaceholderText('value_json (e.g. {"foo":1})')
        self.btn_write = QtWidgets.QPushButton("Write"); self.btn_write.clicked.connect(self.bucket_write)
        roww.addWidget(self.ed_key,1); roww.addWidget(self.ed_val,2); roww.addWidget(self.btn_write)
        v5.addLayout(roww)
        d5.setWidget(w5); self.addDockWidget(QtCore.Qt.RightDockWidgetArea, d5)

        # Immune AI
        d6=QtWidgets.QDockWidget("Immune AI", self)
        self.immAI = ImmuneAI(self.db)
        d6.setWidget(self.immAI)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, d6)

    # ---------- Lifecycle ----------
    def ensure_cell1(self):
        c0=self.db.cell_get("cell_0"); c1=self.db.cell_get("cell_1")
        if c0 and not c1:
            self.db.cell_insert("cell_1", c0["code"], immutable=0, parent="cell_0", pos=(0,0), size=(800,800))
            self.db.log("immune_system","INFO","Spawned cell_1 from cell_0")

    def populate(self):
        self.scene.clear(); self.items={}; self.list.clear()
        rows=self.db.cells_all()
        for r in rows:
            name=r["name"]; self.list.addItem(name)
            w=self.make_widget(r); it=CellItem(name,w,GRID_SIZE); self.scene.addItem(it)
            meta=json.loads(r["metadata_json"] or "{}"); pos=meta.get("pos",{"x":0,"y":0}); it.setPos(pos.get("x",0),pos.get("y",0))
            self.items[name]=it
        self.refresh_tables(); self.refresh_buckets(); self.center_cell1()

    def make_widget(self, row):
        name=row["name"]; code=row["code"]; imm=bool(row["immutable"])
        try:
            mod=types.ModuleType("m"); exec(code, mod.__dict__)
            if hasattr(mod,"build_gui"):
                try: w=mod.build_gui(ANTApi(self.db,name))
                except Exception as e: self.db.log("immune_system","ERROR",f"build_gui({name}): {e}"); w=None
            else: w=None
        except Exception as e:
            self.db.log("immune_system","ERROR",f"compile {name}: {e}"); w=None
        if w is None:
            w=QtWidgets.QWidget(); v=QtWidgets.QVBoxLayout(w)
            t=QtWidgets.QLabel(f"{name}"+(" (immutable)" if imm else "")); t.setStyleSheet("font-weight:bold"); v.addWidget(t)
            v.addWidget(QtWidgets.QLabel("Default cell UI. Edit in Inspector."))
            v.addStretch(1)
        w.setMinimumSize(600,600); w.resize(800,800); return w

    # ---------- Buckets dock ----------
    def refresh_buckets(self):
        self.cb_bucket.blockSignals(True)
        self.cb_bucket.clear()
        names = self.db.list_buckets()
        if not names: self.cb_bucket.addItem("—")
        else: self.cb_bucket.addItems(names)
        self.cb_bucket.blockSignals(False)
        self.refresh_bucket_table()

    def refresh_bucket_table(self):
        name = self.cb_bucket.currentText().strip()
        if not name or name=="—":
            self.tbl_b.clearContents(); self.tbl_b.setRowCount(0); return
        rows = self.db.bucket_items(name, limit=200)
        self.tbl_b.setRowCount(len(rows))
        for r,row in enumerate(rows):
            self.tbl_b.setItem(r,0,QtWidgets.QTableWidgetItem(str(row["id"])))
            self.tbl_b.setItem(r,1,QtWidgets.QTableWidgetItem(row["key"]))
            self.tbl_b.setItem(r,2,QtWidgets.QTableWidgetItem(row["value_json"]))
            self.tbl_b.setItem(r,3,QtWidgets.QTableWidgetItem(row["created_at"] or ""))
        self.tbl_b.resizeColumnsToContents()

    def bucket_write(self):
        name = self.cb_bucket.currentText().strip()
        if not name or name=="—": 
            QtWidgets.QMessageBox.information(self,"Bucket","Choose a bucket first."); return
        key = self.ed_key.text().strip(); js = self.ed_val.text().strip()
        if not key or not js: return
        try:
            val=json.loads(js)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"JSON",f"Invalid JSON: {e}"); return
        self.db.bucket_write(name, key, val)
        self.refresh_bucket_table()

    # ---------- Toolbar actions ----------
    def center_cell1(self):
        it=self.items.get("cell_1"); self.view.centerOn(it if it else QtCore.QPointF(0,0))
    def toggle_grid(self): self.scene.show_grid=not self.scene.show_grid; self.scene.update()

    def on_sel(self):
        it=self.list.selectedItems()
        if not it: self.lbl.setText("—"); self.ed.setPlainText(""); self.b_save.setEnabled(False); self.b_rb.setEnabled(False); return
        name=it[0].text(); row=self.db.cell_get(name)
        self.lbl.setText(f"{name}  v{row['version']}  immutable={'yes' if row['immutable'] else 'no'}")
        self.ed.setPlainText(row["code"]); self.ed.setReadOnly(bool(row["immutable"]))
        self.b_save.setEnabled(not bool(row["immutable"])); self.b_rb.setEnabled(not bool(row["immutable"]))

    def save_code(self):
        it=self.list.selectedItems(); 
        if not it: return
        name=it[0].text(); code=self.ed.toPlainText()
        ok,msg=compile_ok(code)
        if not ok:
            QtWidgets.QMessageBox.warning(self,"Syntax",msg); return
        try:
            # diff for history
            cur = self.db.cell_get(name)["code"]
            d = unified_diff(cur, code, A=f"{name}@current", B="proposed")
            self.db.cell_update_code(name,code,diff_text=d)
            self.db.log("immune_system","INFO",f"Saved {name}")
            # also write a code_parts snapshot
            self.db.bucket_write("code_parts", f"{name}-snapshot-{int(time.time())}",
                                 {"cell":name,"segments":[{"kind":"other","name":"full","text": code}]})
            self.populate()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self,"Save error",str(e))

    def run_behavior(self):
        it=self.list.selectedItems(); 
        if not it: return
        name=it[0].text(); row=self.db.cell_get(name); code=row["code"]
        try:
            mod=types.ModuleType("m"); exec(code, mod.__dict__)
            if hasattr(mod,"core_behavior"):
                res=mod.core_behavior(ANTApi(self.db,name))
                QtWidgets.QMessageBox.information(self,"Result",str(res))
            else:
                QtWidgets.QMessageBox.information(self,"Result","No core_behavior(api) defined.")
        except Exception as e:
            tb=traceback.format_exc(); self.db.log(name,"ERROR",f"behavior: {e}")
            c=self.db.connect(); x=c.cursor()
            x.execute("INSERT INTO errors(cell_name,version,traceback,context_json) VALUES(?,?,?,?)",
                      (name,row["version"],tb,json.dumps({"action":"core_behavior"})))
            c.commit(); c.close()
            QtWidgets.QMessageBox.critical(self,"Behavior error",str(e))

    def rollback(self):
        it=self.list.selectedItems(); 
        if not it: return
        name=it[0].text()
        try:
            v=self.db.cell_rollback(name); self.db.log("immune_system","WARN",f"Rollback {name} -> v{v}"); self.populate()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"Rollback",str(e))

    def spawn_cell(self):
        name,ok=QtWidgets.QInputDialog.getText(self,"Spawn Cell","Name:")
        if not ok or not name.strip(): return
        name="".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name.strip())
        if self.db.cell_get(name): 
            QtWidgets.QMessageBox.warning(self,"Exists","Cell exists."); return
        c0=self.db.cell_get("cell_0"); code=c0["code"] if c0 else "def core_behavior(api):\n    return {'ok':True}\n"
        pos=self.free_pos(); self.db.cell_insert(name,code,immutable=0,parent="cell_0",pos=pos,size=(800,800))
        self.db.log("immune_system","INFO",f"Spawned {name}"); self.populate()

    def free_pos(self):
        occ=set()
        for it in self.items.values():
            p=it.pos(); gx=round(p.x()/GRID_SIZE); gy=round(p.y()/GRID_SIZE); occ.add((gx,gy))
        for r in range(0,40):
            for dx in range(-r,r+1):
                for dy in range(-r,r+1):
                    if (dx,dy) not in occ:
                        neigh=[(dx+1,dy),(dx-1,dy),(dx,dy+1),(dx,dy-1)]
                        if any(n in occ for n in neigh): continue
                        return (dx*GRID_SIZE, dy*GRID_SIZE)
        return (0,0)

    def merge_selected(self):
        sel=[i for i in self.scene.selectedItems() if isinstance(i,CellItem)]
        if len(sel)<2:
            QtWidgets.QMessageBox.information(self,"Merge","Select ≥2 cells."); return
        tabs=QtWidgets.QTabWidget()
        for it in sel:
            w=it.proxy.widget(); it.proxy.setWidget(None); self.scene.removeItem(it); self.items.pop(it.cell,None)
            tabs.addTab(w, it.cell)
        comp=CellItem("cluster",tabs,GRID_SIZE); self.scene.addItem(comp); comp.setPos(0,0); self.items["cluster"]=comp
        self.db.log("immune_system","INFO","Merged (visual)")
        self.populate()

    def unmerge_selected(self):
        sel=[i for i in self.scene.selectedItems() if isinstance(i,CellItem)]
        if len(sel)!=1: QtWidgets.QMessageBox.information(self,"Unmerge","Select the merged cluster."); return
        it=sel[0]; tabs=it.proxy.widget()
        if not isinstance(tabs,QtWidgets.QTabWidget): return
        base=it.pos()
        for idx in range(tabs.count()):
            w=tabs.widget(idx); name=tabs.tabText(idx)
            child=CellItem(name,w,GRID_SIZE); self.scene.addItem(child)
            child.setPos(base+QtCore.QPointF((idx+1)*GRID_SIZE*2,(idx%2)*GRID_SIZE*2)); self.items[name]=child
        it.proxy.setWidget(None); self.scene.removeItem(it); self.items.pop("cluster",None)
        self.db.log("immune_system","INFO","Unmerged"); self.populate()

    def inject_protein(self):
        dlg=QtWidgets.QDialog(self); dlg.setWindowTitle("Protein (broadcast)")
        v=QtWidgets.QVBoxLayout(dlg); ed=QtWidgets.QPlainTextEdit(); ed.setPlaceholderText("directive...")
        tgt=QtWidgets.QLineEdit(); tgt.setPlaceholderText("target cell (optional, blank=broadcast)")
        bb=QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        v.addWidget(ed); v.addWidget(tgt); v.addWidget(bb); bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        if dlg.exec_()==QtWidgets.QDialog.Accepted:
            text=ed.toPlainText().strip(); to=tgt.text().strip() or None
            if text: self.db.emit("immune_system","protein",{"text":text},to); self.db.log("immune_system","INFO",f"protein -> {to or 'broadcast'}")

    # ---------- Host Browser ----------
    def refresh_tables(self):
        try:
            c=self.db.connect(); x=c.cursor(); x.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            names=[r[0] for r in x.fetchall()]; c.close()
            self.tables.clear(); self.tables.addItems(names)
        except Exception as e:
            self.db.log("immune_system","ERROR",f"tables:{e}")

    def preview(self):
        t=self.tables.currentText().strip()
        if not t: return
        try:
            c=self.db.connect(); x=c.cursor()
            x.execute(f"PRAGMA table_info({t})"); cols=[r[1] for r in x.fetchall()]
            x.execute(f"SELECT * FROM {t} LIMIT 200"); data=x.fetchall(); c.close()
            self.fill_table(cols,data)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"Preview",str(e))

    def exec_select(self):
        sql=self.sql.toPlainText().strip()
        if not sql.lower().startswith("select"): 
            QtWidgets.QMessageBox.warning(self,"SQL","Read-only: SELECT only."); return
        try:
            c=self.db.connect(); x=c.cursor(); x.execute(sql+f" LIMIT {int(self.lim.value())}")
            cols=[d[0] for d in x.description]; data=x.fetchall(); c.close()
            self.fill_table(cols,data)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"SQL",str(e))

    def fill_table(self,cols,rows):
        self.table.clear(); self.table.setColumnCount(len(cols)); self.table.setHorizontalHeaderLabels(cols)
        self.table.setRowCount(len(rows))
        for r,row in enumerate(rows):
            for c,val in enumerate(row): self.table.setItem(r,c,QtWidgets.QTableWidgetItem(str(val)))
        self.table.resizeColumnsToContents()

    # ---------- Maintenance ----------
    def tick(self):
        # save positions
        for name,it in list(self.items.items()):
            p=it.pos(); self._save_pos(name,int(p.x()),int(p.y()))
        self.refresh_logs()
        self.maintenance_pass()

    def _save_pos(self,name,x,y):
        r=self.db.cell_get(name); if not r: return
        meta=json.loads(r["metadata_json"] or "{}"); meta.setdefault("pos",{}); meta["pos"]["x"]=x; meta["pos"]["y"]=y
        c=self.db.connect(); xq=c.cursor(); xq.execute("UPDATE cells SET metadata_json=? WHERE name=?", (json.dumps(meta),name)); c.commit(); c.close()

    def refresh_logs(self):
        cell=self.f_cell.text().strip() or None; lev=self.f_level.currentText().strip() or None
        c=self.db.connect(); x=c.cursor()
        base="SELECT * FROM logs"; wh=[]; pr=[]
        if cell: wh.append("cell_name=?"); pr.append(cell)
        if lev: wh.append("level=?"); pr.append(lev)
        if wh: base+=" WHERE "+ " AND ".join(wh)
        base+=" ORDER BY id DESC LIMIT 1000"
        x.execute(base,pr); rows=x.fetchall(); c.close()
        cur=self.log.verticalScrollBar().value(); mx=self.log.verticalScrollBar().maximum(); at_bottom=cur>=mx-4
        txt="\n".join(f"[{r['created_at']}] {r['cell_name']} {r['level']}: {r['message']}" for r in reversed(rows))
        self.log.setPlainText(txt)
        if at_bottom: self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def maintenance_pass(self):
        """Correlate logs to diffs, write diff_notes, prune older logs."""
        try:
            c = self.db.connect(); x = c.cursor()
            # 1) figure last processed log id
            last = self.db.meta_get("logs_last_processed_id")
            last_id = int(last) if (last and last.isdigit()) else 0

            # 2) pull next batch of logs newer than last_id
            x.execute("SELECT id, cell_name, level, message, created_at FROM logs WHERE id>? ORDER BY id ASC LIMIT ?", (last_id, LOG_PROCESS_BATCH))
            logs = x.fetchall()

            # 3) correlate with diffs within recent window
            if logs:
                # recent diffs by cell
                x.execute("SELECT id, cell_name, from_version, to_version, created_at FROM diffs WHERE (strftime('%s','now') - strftime('%s',created_at)) < ? ORDER BY id DESC", (DIFF_RECENT_SECONDS,))
                diffs = x.fetchall()
                diffs_by_cell = {}
                for d in diffs:
                    diffs_by_cell.setdefault(d["cell_name"], []).append(d)

                # ensure diff_notes bucket exists
                x.execute("INSERT OR IGNORE INTO buckets(name,purpose,schema_json,mutable) VALUES(?,?,?,1)",
                          ("diff_notes","Short notes tying logs to diffs", json.dumps({"type":"object"})))

                for L in logs:
                    cell = L["cell_name"] or ""
                    if "save" in (L["message"] or "").lower() or "update" in (L["message"] or "").lower():
                        ds = diffs_by_cell.get(cell, [])
                        if ds:
                            d0 = ds[0]
                            note = {"cell": cell, "log": {"id": L["id"], "msg": L["message"], "at": L["created_at"]},
                                    "diff": {"id": d0["id"], "from": d0["from_version"], "to": d0["to_version"], "at": d0["created_at"]}}
                            x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name,key,value_json) VALUES('diff_notes',?,?)",
                                      (f"{cell}-log{L['id']}-diff{d0['id']}", json.dumps(note)))
                # bump last processed
                last_id = logs[-1]["id"]
                self.db.meta_set("logs_last_processed_id", str(last_id))

            # 4) release old logs beyond retention
            x.execute("SELECT COUNT(*) FROM logs"); total=x.fetchone()[0]
            if total > LOG_RETAIN_MAX:
                # delete oldest rows beyond retention
                to_remove = total - LOG_RETAIN_MAX
                x.execute("DELETE FROM logs WHERE id IN (SELECT id FROM logs ORDER BY id ASC LIMIT ?)", (to_remove,))
            c.commit()
        except Exception as e:
            # non-fatal
            self.db.log("immune_system","ERROR",f"maintenance: {e}")
        finally:
            try: c.close()
            except: pass

# ==========================
# Entrypoint
# ==========================

def main():
    # Ensure QApplication before any dialogs
    app=QtWidgets.QApplication(sys.argv)
    # dark retro
    pal=QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window,QtGui.QColor(18,18,18))
    pal.setColor(QtGui.QPalette.WindowText,QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Base,QtGui.QColor(12,12,12))
    pal.setColor(QtGui.QPalette.Text,QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Button,QtGui.QColor(24,24,24))
    pal.setColor(QtGui.QPalette.ButtonText,QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Highlight,QtGui.QColor(60,180,120))
    pal.setColor(QtGui.QPalette.HighlightedText,QtCore.Qt.black)
    app.setPalette(pal); app.setStyle("Fusion")

    # Resolve DB path
    dbp=os.environ.get("SINGLECELL_DB") or (len(sys.argv)>1 and sys.argv[1]) or ""
    if not dbp:
        QtWidgets.QMessageBox.critical(None,"DB required","Set SINGLECELL_DB or pass path as argv[1].")
        sys.exit(2)

    db=DB(dbp); db.ensure()
    ui=UI(db); ui.show()
    sys.exit(app.exec_())

if __name__=="__main__": 
    main()
```



## Module `Sandbox\ant_launcher.py`

```python
#!/usr/bin/env python3
# ant_launcher.py — Sandbox-first Project Launcher for ANT
# --------------------------------------------------------
# Key points:
#  - Default to SANDBOX mode (no EXE). Use scripts/SQL from ./Sandbox/
#  - Manage "Projects" as named pointers to SQLite files (.db)
#  - Launch Immune System from Sandbox (immune_system.py) with SINGLECELL_DB env
#  - Optional "Compile" tab kept (off by default) for future EXE build flow
#  - Persist config and project index in ./Output/config/launcher_config.json
#  - Dark retro theme, PyQt5

import os
import sys
import json
import shutil
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets

APP_NAME = "ANT Project Launcher"
VERSION  = "0.6-sandbox-first"

# ---------- Paths / Layout ----------
ROOT_DIR       = Path(__file__).resolve().parent
SANDBOX_DIR    = ROOT_DIR / "Sandbox"           # active dev scripts + SQL live here
LOADER_DIR     = ROOT_DIR / "Loader"            # only used when Compile tab enabled
OUTPUT_DIR     = ROOT_DIR / "Output"            # projects + config + logs
PROJECTS_DIR   = OUTPUT_DIR / "projects"
CONFIG_DIR     = OUTPUT_DIR / "config"
BEDROCKS_DIR   = SANDBOX_DIR / "Bedrocks"       # curated bedrock SQLs you keep in Sandbox

CONFIG_PATH    = CONFIG_DIR / "launcher_config.json"
LAUNCH_LOG_DIR = OUTPUT_DIR / "logs"

# Names we look for in Sandbox
IMMUNE_FILENAME = "immune_system.py"
CELL1_FILENAME  = "cell_1.py"

# ---------- Helpers ----------
def ensure_dirs():
    for p in [SANDBOX_DIR, LOADER_DIR, OUTPUT_DIR, PROJECTS_DIR, CONFIG_DIR, BEDROCKS_DIR, LAUNCH_LOG_DIR]:
        p.mkdir(parents=True, exist_ok=True)

def load_json(p: Path, default: Any) -> Any:
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def save_json(p: Path, obj: Any):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def ts_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sanitize_name(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in s.strip())

# ---------- Config Model ----------
class Config:
    def __init__(self):
        ensure_dirs()
        self.data: Dict[str, Any] = load_json(CONFIG_PATH, {
            "version": VERSION,
            "paths": {
                "sandbox_dir": str(SANDBOX_DIR),
                "loader_dir": str(LOADER_DIR),
                "output_dir": str(OUTPUT_DIR),
                "projects_dir": str(PROJECTS_DIR),
                "bedrocks_dir": str(BEDROCKS_DIR),
            },
            "projects": {},  # name -> {"sql_path": "...", "created": "..."}
            "last_project": "",
            "compile_enabled": False,
            "python_interpreter": sys.executable,
        })

    def save(self):
        self.data["version"] = VERSION
        save_json(CONFIG_PATH, self.data)

    # Convenience getters
    def sandbox_dir(self) -> Path: return Path(self.data["paths"]["sandbox_dir"])
    def loader_dir(self)  -> Path: return Path(self.data["paths"]["loader_dir"])
    def output_dir(self)  -> Path: return Path(self.data["paths"]["output_dir"])
    def projects_dir(self)-> Path: return Path(self.data["paths"]["projects_dir"])
    def bedrocks_dir(self)-> Path: return Path(self.data["paths"]["bedrocks_dir"])
    def projects(self)    -> Dict[str, Any]: return self.data.get("projects", {})
    def set_project(self, name: str, sql_path: str):
        self.data["projects"][name] = {"sql_path": sql_path, "created": ts_utc()}
    def del_project(self, name: str):
        self.data["projects"].pop(name, None)

# ---------- UI Widgets ----------
class LogConsole(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumBlockCount(2000)
        self.setStyleSheet("QPlainTextEdit { background:#0f0f0f; color:#ddd; border:1px solid #2a2a2a; }")

    def log(self, line: str):
        self.appendPlainText(f"[{ts_utc()}] {line}")
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class PathsPane(QtWidgets.QGroupBox):
    changed = QtCore.pyqtSignal()

    def __init__(self, cfg: Config):
        super().__init__("Paths")
        self.cfg = cfg
        v = QtWidgets.QFormLayout(self)

        self.edSandbox = QtWidgets.QLineEdit(str(cfg.sandbox_dir()))
        self.edLoader  = QtWidgets.QLineEdit(str(cfg.loader_dir()))
        self.edOut     = QtWidgets.QLineEdit(str(cfg.output_dir()))
        self.edProj    = QtWidgets.QLineEdit(str(cfg.projects_dir()))
        self.edBeds    = QtWidgets.QLineEdit(str(cfg.bedrocks_dir()))
        self.edPy      = QtWidgets.QLineEdit(cfg.data.get("python_interpreter", sys.executable))

        def mkrow(label, ed):
            row = QtWidgets.QHBoxLayout()
            row.addWidget(ed, 1)
            btn = QtWidgets.QPushButton("Browse")
            btn.clicked.connect(lambda: self.browse(ed, is_file=False))
            row.addWidget(btn)
            v.addRow(QtWidgets.QLabel(label), wrap(row))

        def wrap(layout):
            w = QtWidgets.QWidget()
            w.setLayout(layout)
            return w

        mkrow("Sandbox Folder", self.edSandbox)
        mkrow("Loader Folder (for Compile)", self.edLoader)
        mkrow("Output Folder", self.edOut)
        mkrow("Projects Folder", self.edProj)
        mkrow("Bedrocks Folder (in Sandbox)", self.edBeds)

        rowpy = QtWidgets.QHBoxLayout()
        rowpy.addWidget(self.edPy, 1)
        btnpy = QtWidgets.QPushButton("Browse")
        btnpy.clicked.connect(lambda: self.browse(self.edPy, is_file=True))
        rowpy.addWidget(btnpy)
        v.addRow(QtWidgets.QLabel("Python Interpreter"), wrap(rowpy))

        savebtn = QtWidgets.QPushButton("Save Paths")
        savebtn.clicked.connect(self.save)
        v.addRow(QtWidgets.QLabel(""), savebtn)

    def browse(self, ed: QtWidgets.QLineEdit, is_file: bool):
        if is_file:
            fn, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", ed.text())
            if fn:
                ed.setText(fn)
        else:
            dn = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", ed.text())
            if dn:
                ed.setText(dn)

    def save(self):
        self.cfg.data["paths"]["sandbox_dir"] = self.edSandbox.text().strip()
        self.cfg.data["paths"]["loader_dir"]  = self.edLoader.text().strip()
        self.cfg.data["paths"]["output_dir"]  = self.edOut.text().strip()
        self.cfg.data["paths"]["projects_dir"]= self.edProj.text().strip()
        self.cfg.data["paths"]["bedrocks_dir"]= self.edBeds.text().strip()
        self.cfg.data["python_interpreter"]   = self.edPy.text().strip()
        self.cfg.save()
        self.changed.emit()

class ProjectsPane(QtWidgets.QWidget):
    launch_requested = QtCore.pyqtSignal(str, str)  # (immune_system.py, sql_path)
    console_log = QtCore.pyqtSignal(str)

    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.setObjectName("ProjectsPane")
        self._build()

    def _build(self):
        lay = QtWidgets.QVBoxLayout(self)
        top = QtWidgets.QHBoxLayout()
        self.lst = QtWidgets.QListWidget()
        self.lst.itemSelectionChanged.connect(self._sel_changed)

        # Right controls
        right = QtWidgets.QVBoxLayout()

        # Bedrock selection (from Sandbox/Bedrocks)
        self.cbBedrocks = QtWidgets.QComboBox()
        self.btnRefreshBeds = QtWidgets.QPushButton("↻")
        self.btnRefreshBeds.setFixedWidth(30)
        self.btnRefreshBeds.clicked.connect(self.refresh_bedrocks)
        hbed = QtWidgets.QHBoxLayout()
        hbed.addWidget(QtWidgets.QLabel("Bedrock SQL (Sandbox/Bedrocks)"))
        hbed.addWidget(self.cbBedrocks, 1)
        hbed.addWidget(self.btnRefreshBeds)

        # New/Open/Delete
        self.btnNew = QtWidgets.QPushButton("New Project (Clone Bedrock)")
        self.btnOpen = QtWidgets.QPushButton("Add Existing SQL…")
        self.btnDel = QtWidgets.QPushButton("Delete Project SQL")
        self.btnOpenFolder = QtWidgets.QPushButton("Open Project Folder")

        self.btnNew.clicked.connect(self.new_project)
        self.btnOpen.clicked.connect(self.add_existing_sql)
        self.btnDel.clicked.connect(self.delete_project)
        self.btnOpenFolder.clicked.connect(self.open_project_folder)

        # Launch
        self.btnLaunch = QtWidgets.QPushButton("Launch Immune System")
        self.btnLaunch.clicked.connect(self.launch_immune)

        # Pack right panel
        right.addLayout(hbed)
        right.addWidget(self.btnNew)
        right.addWidget(self.btnOpen)
        right.addWidget(self.btnDel)
        right.addWidget(self.btnOpenFolder)
        right.addSpacing(12)
        right.addWidget(self.btnLaunch)
        right.addStretch(1)

        top.addWidget(self.lst, 2)
        top.addLayout(right, 1)

        # Sandbox info
        gb = QtWidgets.QGroupBox("Sandbox Scripts (used for Launch, not Loader)")
        form = QtWidgets.QFormLayout(gb)
        self.lblImmune = QtWidgets.QLabel(self._immune_path_or_hint())
        self.lblCell1  = QtWidgets.QLabel(self._cell1_path_or_hint())
        form.addRow("immune_system.py:", self.lblImmune)
        form.addRow("cell_1.py:", self.lblCell1)

        lay.addLayout(top, 4)
        lay.addWidget(gb, 1)

        self.refresh_bedrocks()
        self.refresh_list()

    def _immune_path_or_hint(self) -> str:
        p = Path(self.cfg.data["paths"]["sandbox_dir"]) / IMMUNE_FILENAME
        return str(p) if p.exists() else f"(Missing) {p}"

    def _cell1_path_or_hint(self) -> str:
        p = Path(self.cfg.data["paths"]["sandbox_dir"]) / CELL1_FILENAME
        return str(p) if p.exists() else f"(Missing) {p}"

    def refresh_paths_labels(self):
        self.lblImmune.setText(self._immune_path_or_hint())
        self.lblCell1.setText(self._cell1_path_or_hint())

    def refresh_bedrocks(self):
        self.cbBedrocks.clear()
        beds = []
        bdir = Path(self.cfg.data["paths"]["bedrocks_dir"])
        if bdir.exists():
            for p in sorted(bdir.glob("*.db")):
                beds.append(str(p))
            for p in sorted(bdir.glob("*.sqlite")):
                beds.append(str(p))
        if beds:
            self.cbBedrocks.addItems(beds)
        else:
            self.cbBedrocks.addItem("(no bedrocks found)")

    def refresh_list(self):
        self.lst.clear()
        for name, meta in sorted(self.cfg.projects().items()):
            self.lst.addItem(f"{name}  —  {meta.get('sql_path','')}")

        # restore last selection if any
        last = self.cfg.data.get("last_project","")
        if last and last in self.cfg.projects():
            items = self.lst.findItems(last, QtCore.Qt.MatchStartsWith)
            if items:
                self.lst.setCurrentItem(items[0])

    def _sel_changed(self):
        it = self.lst.currentItem()
        if not it:
            self.cfg.data["last_project"] = ""
        else:
            name = it.text().split("  —  ")[0]
            self.cfg.data["last_project"] = name
        self.cfg.save()

    def current_project(self) -> Tuple[Optional[str], Optional[str]]:
        it = self.lst.currentItem()
        if not it:
            return None, None
        name, path = it.text().split("  —  ")
        return name, path

    def new_project(self):
        bed = self.cbBedrocks.currentText().strip()
        if not bed or bed.startswith("(no bedrocks"):
            QtWidgets.QMessageBox.information(self, "Bedrock", "No bedrock SQL found in Sandbox/Bedrocks.")
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "New Project", "Project name:")
        if not ok or not name.strip():
            return
        name = sanitize_name(name)
        dest = Path(self.cfg.data["paths"]["projects_dir"]) / f"{name}.db"
        if dest.exists():
            QtWidgets.QMessageBox.warning(self, "Exists", f"{dest} already exists.")
            return
        try:
            shutil.copy2(bed, dest)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Copy error", str(e))
            return
        self.cfg.set_project(name, str(dest))
        self.cfg.save()
        self.refresh_list()
        self.console_log.emit(f"Project '{name}' created from bedrock: {bed}")

    def add_existing_sql(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Project SQL", str(self.cfg.projects_dir()), "SQLite DB (*.db *.sqlite)")
        if not fn:
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "Name Project", "Project name:")
        if not ok or not name.strip():
            return
        name = sanitize_name(name)
        self.cfg.set_project(name, fn)
        self.cfg.save()
        self.refresh_list()
        self.console_log.emit(f"Added project '{name}': {fn}")

    def delete_project(self):
        name, path = self.current_project()
        if not name: return
        resp = QtWidgets.QMessageBox.question(self, "Delete Project SQL", f"Delete SQL file?\n\n{name} → {path}\n\nThis cannot be undone.",
                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if resp != QtWidgets.QMessageBox.Yes:
            return
        try:
            p = Path(path)
            if p.exists():
                p.unlink()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Delete error", str(e))
        self.cfg.del_project(name)
        self.cfg.save()
        self.refresh_list()
        self.console_log.emit(f"Deleted project '{name}' and SQL file.")

    def open_project_folder(self):
        _, path = self.current_project()
        if not path: return
        folder = str(Path(path).parent)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(folder))

    def launch_immune(self):
        _, sql_path = self.current_project()
        if not sql_path:
            QtWidgets.QMessageBox.information(self, "Project", "Select a project first.")
            return
        immune = Path(self.cfg.data["paths"]["sandbox_dir"]) / IMMUNE_FILENAME
        if not immune.exists():
            QtWidgets.QMessageBox.critical(self, "Missing", f"Sandbox immune_system.py not found:\n{immune}")
            return
        self.launch_requested.emit(str(immune), sql_path)

class SandboxPane(QtWidgets.QWidget):
    rescan_requested = QtCore.pyqtSignal()

    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self._build()

    def _build(self):
        v = QtWidgets.QVBoxLayout(self)
        grid = QtWidgets.QGridLayout()
        r=0

        self.lblImmune = QtWidgets.QLabel("")
        self.lblCell1  = QtWidgets.QLabel("")
        self.btnOpenImmune = QtWidgets.QPushButton("Open immune_system.py")
        self.btnOpenCell1  = QtWidgets.QPushButton("Open cell_1.py")
        self.btnOpenImmune.clicked.connect(lambda: self._open_file(Path(self.cfg.sandbox_dir())/IMMUNE_FILENAME))
        self.btnOpenCell1.clicked.connect(lambda: self._open_file(Path(self.cfg.sandbox_dir())/CELL1_FILENAME))

        grid.addWidget(QtWidgets.QLabel("Sandbox immune_system.py:"), r,0); grid.addWidget(self.lblImmune, r,1); grid.addWidget(self.btnOpenImmune, r,2); r+=1
        grid.addWidget(QtWidgets.QLabel("Sandbox cell_1.py:"),       r,0); grid.addWidget(self.lblCell1,  r,1); grid.addWidget(self.btnOpenCell1,  r,2); r+=1

        v.addLayout(grid)

        h = QtWidgets.QHBoxLayout()
        self.btnRescan = QtWidgets.QPushButton("Rescan Sandbox")
        self.btnRescan.clicked.connect(self.rescan_requested.emit)
        h.addStretch(1); h.addWidget(self.btnRescan)
        v.addLayout(h)
        self.set_paths()

    def set_paths(self):
        imm = Path(self.cfg.sandbox_dir())/IMMUNE_FILENAME
        c1  = Path(self.cfg.sandbox_dir())/CELL1_FILENAME
        self.lblImmune.setText(str(imm) if imm.exists() else f"(Missing) {imm}")
        self.lblCell1.setText(str(c1) if c1.exists() else f"(Missing) {c1}")

    def _open_file(self, p: Path):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(p)))

class CompilePane(QtWidgets.QWidget):
    console_log = QtCore.pyqtSignal(str)

    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self._build()

    def _build(self):
        v = QtWidgets.QVBoxLayout(self)

        # Enable/disable compile controls
        self.chkEnable = QtWidgets.QCheckBox("Enable Compile Mode (uses Loader, not Sandbox)")
        self.chkEnable.setChecked(bool(self.cfg.data.get("compile_enabled", False)))
        self.chkEnable.stateChanged.connect(self._toggle)
        v.addWidget(self.chkEnable)

        self.gb = QtWidgets.QGroupBox("Compiler Controls")
        self.gb.setEnabled(self.chkEnable.isChecked())
        form = QtWidgets.QFormLayout(self.gb)

        self.edIcon = QtWidgets.QLineEdit(str((ROOT_DIR/"singlecell.png")))
        self.edName = QtWidgets.QLineEdit("launcher_packed")
        self.btnRun = QtWidgets.QPushButton("Build EXE (PyInstaller)")
        self.btnRun.clicked.connect(self.do_build)

        form.addRow("App Icon (.ico/.png):", self.edIcon)
        form.addRow("Output Name:", self.edName)
        form.addRow("", self.btnRun)

        v.addWidget(self.gb)
        v.addStretch(1)

    def _toggle(self):
        on = self.chkEnable.isChecked()
        self.gb.setEnabled(on)
        self.cfg.data["compile_enabled"] = bool(on)
        self.cfg.save()
        self.console_log.emit(f"Compile mode {'enabled' if on else 'disabled'}")

    def do_build(self):
        # This is a placeholder run to keep the flow alive (we keep it real, but gated by the checkbox).
        # You can wire the actual ant_compiler.py here if desired.
        if not self.chkEnable.isChecked():
            self.console_log.emit("Compile mode is disabled.")
            return
        self.console_log.emit("Compile started (stub). Configure ant_compiler.py integration here.")

# ---------- Main Window ----------
class MainUI(QtWidgets.QMainWindow):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.proc: Optional[QtCore.QProcess] = None
        self.setWindowTitle(f"{APP_NAME} — {VERSION}")
        self.resize(1200, 800)
        self._build()
        self.apply_theme()

    def _build(self):
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        # Console
        self.console = LogConsole()

        # Paths
        self.pathsPane = PathsPane(self.cfg)
        self.pathsPane.changed.connect(self._paths_changed)

        # Projects
        self.projectsPane = ProjectsPane(self.cfg)
        self.projectsPane.launch_requested.connect(self.launch_immune)
        self.projectsPane.console_log.connect(self.console.log)

        # Sandbox
        self.sandboxPane = SandboxPane(self.cfg)
        self.sandboxPane.rescan_requested.connect(self._rescan_sandbox)

        # Compile (off by default)
        self.compilePane = CompilePane(self.cfg)
        self.compilePane.console_log.connect(self.console.log)

        # Layout
        split = QtWidgets.QSplitter()
        split.setOrientation(QtCore.Qt.Vertical)
        upper = QtWidgets.QSplitter()
        upper.setOrientation(QtCore.Qt.Horizontal)
        up_left = QtWidgets.QTabWidget()
        up_left.addTab(self.projectsPane, "Projects")
        up_left.addTab(self.sandboxPane, "Sandbox")
        up_left.addTab(self.pathsPane, "Paths")

        up_right = QtWidgets.QTabWidget()
        up_right.addTab(self.compilePane, "Compile (optional)")
        up_right.addTab(self.console, "Console")

        upper.addWidget(up_left)
        upper.addWidget(up_right)
        upper.setSizes([800, 400])

        split.addWidget(upper)
        # bottom could be used for future dashboards; for now, empty filler
        filler = QtWidgets.QWidget()
        split.addWidget(filler)
        split.setSizes([700, 100])

        self.setCentralWidget(split)

        # Toolbar
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        act_about = QtWidgets.QAction("About", self)
        act_about.triggered.connect(self._about)
        tb.addAction(act_about)

        self.console.log("Launcher ready (Sandbox-first).")

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #121212; }
            QLabel { color:#a7f3d0; }
            QGroupBox { color:#a7f3d0; border:1px solid #2a2a2a; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 4px 6px; }
            QPushButton { background:#1f1f1f; color:#eee; border:1px solid #2f2f2f; padding:6px 10px; }
            QPushButton:hover { background:#2a2a2a; }
            QLineEdit, QComboBox, QPlainTextEdit, QListWidget {
                background:#161616; color:#eee; border:1px solid #2a2a2a;
            }
            QTabBar::tab { background:#1b1b1b; color:#ddd; padding:8px; }
            QTabBar::tab:selected { background:#252525; }
        """)
        app = QtWidgets.QApplication.instance()
        if app:
            pal = QtGui.QPalette()
            pal.setColor(QtGui.QPalette.Window, QtGui.QColor(18,18,18))
            pal.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
            pal.setColor(QtGui.QPalette.Base, QtGui.QColor(14,14,14))
            pal.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
            pal.setColor(QtGui.QPalette.Button, QtGui.QColor(24,24,24))
            pal.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
            pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor(60,180,120))
            pal.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
            app.setPalette(pal)
            app.setStyle("Fusion")

    # ----- events -----
    def _about(self):
        QtWidgets.QMessageBox.information(self, "About", f"{APP_NAME}\nVersion {VERSION}\nSandbox-first workflow.")

    def _paths_changed(self):
        self.projectsPane.refresh_paths_labels()
        self.sandboxPane.set_paths()
        self.projectsPane.refresh_bedrocks()
        self.console.log("Paths updated.")

    def _rescan_sandbox(self):
        self.projectsPane.refresh_paths_labels()
        self.sandboxPane.set_paths()
        self.console.log("Sandbox rescanned.")

    # ----- Launch Immune System (Sandbox) -----
    def launch_immune(self, immune_py: str, sql_path: str):
        # Close existing
        if self.proc and self.proc.state() != QtCore.QProcess.NotRunning:
            QtWidgets.QMessageBox.warning(self, "Running", "Immune System is already running.")
            return

        py = self.cfg.data.get("python_interpreter", sys.executable) or sys.executable
        if not Path(py).exists():
            QtWidgets.QMessageBox.critical(self, "Python", f"Interpreter not found:\n{py}")
            return

        if not Path(immune_py).exists():
            QtWidgets.QMessageBox.critical(self, "Missing", f"immune_system.py not found:\n{immune_py}")
            return

        if not Path(sql_path).exists():
            QtWidgets.QMessageBox.critical(self, "Missing", f"Project SQL not found:\n{sql_path}")
            return

        # Prepare QProcess with SINGLECELL_DB
        self.proc = QtCore.QProcess(self)
        self.proc.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("SINGLECELL_DB", str(sql_path))
        self.proc.setProcessEnvironment(env)

        # Capture IO to console
        self.proc.readyReadStandardOutput.connect(self._proc_out)
        self.proc.finished.connect(self._proc_finished)
        self.proc.errorOccurred.connect(self._proc_error)

        # Arguments: immune_system.py <db_path>
        args = [str(immune_py), str(sql_path)]
        self.console.log(f"Launching immune system:\n  python: {py}\n  script: {immune_py}\n  db: {sql_path}")
        self.proc.start(py, args)

        if not self.proc.waitForStarted(3000):
            self.console.log("Failed to start Immune System.")
            QtWidgets.QMessageBox.critical(self, "Launch", "Failed to start Immune System.")
            return

    def _proc_out(self):
        try:
            data = bytes(self.proc.readAllStandardOutput()).decode(errors="ignore")
            if data:
                for line in data.splitlines():
                    self.console.log(f"[immune] {line}")
        except Exception:
            pass

    def _proc_finished(self, code, status):
        self.console.log(f"Immune System exited (code={code}, status={status}).")

    def _proc_error(self, err):
        self.console.log(f"Immune System process error: {err}")

# ---------- Main ----------
def main():
    ensure_dirs()
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    cfg = Config()
    ui = MainUI(cfg)
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

**Classes:** Config, LogConsole, PathsPane, ProjectsPane, SandboxPane, CompilePane, MainUI
**Functions:** ensure_dirs(), load_json(p, default), save_json(p, obj), ts_utc(), sanitize_name(s), main()


## Module `Sandbox\cell_1.py`

```python
#!/usr/bin/env python3
# cell_1.py  — also valid as cell_0 (cell_0 should be immutable in host schema)
# A self-writing, self-validating agent cell with an embedded ANTapi "soul".
# - Uses Ollama (default model: qwen3:4b) for local reasoning/refactor
# - Talks to other agents via signals table
# - Reads/writes Host SQLite directly (SINGLECELL_DB) for buckets, diffs, versions
# - GUI: model dropdown, chat with /commands, bucket browser (Show All), actions

import os, sys, json, time, sqlite3, traceback, difflib, ast, threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from PyQt5 import QtCore, QtGui, QtWidgets

# -------------------------
# Configuration
# -------------------------
APP_CELL_TITLE = "ANT Cell"
DEFAULT_MODEL = "qwen3:4b"
OLLAMA_URL    = "http://localhost:11434"
OLLAMA_GEN    = f"{OLLAMA_URL}/api/generate"
OLLAMA_TAGS   = f"{OLLAMA_URL}/api/tags"

# -------------------------
# Utilities
# -------------------------
def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def unified_diff(a: str, b: str, A: str = "current", B: str = "proposed") -> str:
    lines = difflib.unified_diff(
        a.splitlines(True), b.splitlines(True), fromfile=A, tofile=B, lineterm=""
    )
    return "".join(lines)

def compile_ok(code: str) -> Tuple[bool, str]:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"

def http_json(url: str, payload: Dict[str, Any], timeout: float = 240.0) -> Dict[str, Any]:
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

def list_ollama_models() -> List[str]:
    try:
        r = requests.get(OLLAMA_TAGS, timeout=4.0)
        r.raise_for_status()
        data = r.json() or {}
        names = []
        for m in data.get("models", []):
            nm = (m.get("name") or "").split(":")[0]
            if nm and nm not in names: names.append(nm)
        if DEFAULT_MODEL not in names:
            names.insert(0, DEFAULT_MODEL)
        return names or [DEFAULT_MODEL]
    except Exception:
        return [DEFAULT_MODEL, "llama3", "mistral", "qwen2", "phi3", "tinyllama"]

# -------------------------
# Host access (direct SQLite)
# -------------------------
class Host:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.environ.get("SINGLECELL_DB") or ""
        if not self.db_path:
            raise RuntimeError("SINGLECELL_DB not set; cell requires Host DB access.")
        self._pth = Path(self.db_path)

    def connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(str(self._pth))
        c.row_factory = sqlite3.Row
        return c

    # --- meta / tables
    def list_tables(self) -> List[str]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        names = [r[0] for r in x.fetchall()]
        c.close()
        return names

    # --- cells
    def list_cells(self) -> List[Dict[str, Any]]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT name, immutable, version, length(code) AS code_len FROM cells ORDER BY name")
        rows = [{"name":r["name"], "immutable":r["immutable"], "version":r["version"], "code_len":r["code_len"]} for r in x.fetchall()]
        c.close()
        return rows

    def get_cell(self, name: str) -> Optional[Dict[str, Any]]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT * FROM cells WHERE name=?", (name,))
        row = x.fetchone(); c.close()
        return dict(row) if row else None

    def update_cell_code(self, name: str, new_code: str, diff_text: str) -> Tuple[bool, str]:
        c = self.connect(); x = c.cursor()
        try:
            x.execute("SELECT version, immutable FROM cells WHERE name=?", (name,))
            r = x.fetchone()
            if not r:
                return False, "Cell not found"
            if (r["immutable"] or 0) == 1:
                return False, "Immutable cell"
            nv = r["version"] + 1
            x.execute("UPDATE cells SET code=?, version=? WHERE name=?", (new_code, nv, name))
            x.execute("INSERT INTO cell_versions(cell_name, version, code) VALUES(?,?,?)", (name, nv, new_code))
            x.execute(
                "INSERT INTO diffs(cell_name, from_version, to_version, diff_type, diff_text) VALUES(?,?,?,?,?)",
                (name, nv - 1, nv, "unified", diff_text),
            )
            c.commit()
            return True, f"Updated {name} to v{nv}"
        except Exception as e:
            c.rollback()
            return False, f"DB error: {e}"
        finally:
            c.close()

    def rollback_cell(self, name: str) -> Tuple[bool, str]:
        c = self.connect(); x = c.cursor()
        try:
            x.execute("SELECT version, immutable FROM cells WHERE name=?", (name,))
            r = x.fetchone()
            if not r:
                return False, "Cell not found"
            if (r["immutable"] or 0) == 1:
                return False, "Immutable cell"
            v = r["version"]
            if v <= 1:
                return False, "No earlier version"
            x.execute("SELECT code FROM cell_versions WHERE cell_name=? AND version=?", (name, v - 1))
            pr = x.fetchone()
            if not pr:
                return False, "Missing prior version"
            x.execute("UPDATE cells SET code=?, version=? WHERE name=?", (pr["code"], v - 1, name))
            c.commit()
            return True, f"Rolled back {name} to v{v-1}"
        except Exception as e:
            c.rollback()
            return False, f"DB error: {e}"
        finally:
            c.close()

    def spawn_cell_from_template(self, new_name: str) -> Tuple[bool, str]:
        c = self.connect(); x = c.cursor()
        try:
            x.execute("SELECT code FROM cells WHERE name='cell_0'")
            r = x.fetchone()
            if not r:
                return False, "cell_0 template not found"
            code = r["code"]
            meta = {"pos":{"x":0,"y":0}, "size":{"w":800,"h":800}, "role":"active"}
            x.execute(
                "INSERT INTO cells(name, parent_id, cluster_id, immutable, code, metadata_json, version) "
                "VALUES (?, NULL, NULL, 0, ?, ?, 1)",
                (new_name, code, json.dumps(meta)),
            )
            x.execute("INSERT INTO cell_versions(cell_name, version, code) VALUES (?, ?, ?)", (new_name, 1, code))
            c.commit()
            return True, f"Spawned {new_name} from cell_0"
        except Exception as e:
            c.rollback()
            return False, f"Spawn error: {e}"
        finally:
            c.close()

    # --- signals/logs/errors/knowledge
    def signal(self, frm: str, kind: str, payload: Dict[str, Any], to: Optional[str] = None):
        c = self.connect(); x = c.cursor()
        x.execute(
            "INSERT INTO signals(from_cell, to_cell, kind, payload_json, created_at) VALUES(?,?,?,?,?)",
            (frm, to, kind, json.dumps(payload), now_utc()),
        )
        c.commit(); c.close()

    def log(self, cell: str, level: str, msg: str):
        c = self.connect(); x = c.cursor()
        x.execute("INSERT INTO logs(cell_name, level, message) VALUES(?,?,?)", (cell, level, msg))
        c.commit(); c.close()

    def error(self, cell: str, version: int, tb: str, ctx: Dict[str, Any]):
        c = self.connect(); x = c.cursor()
        x.execute(
            "INSERT INTO errors(cell_name, version, traceback, context_json) VALUES(?,?,?,?)",
            (cell, version, tb, json.dumps(ctx)),
        )
        c.commit(); c.close()

    def remember(self, cell: str, text: str, tags: Optional[Dict[str, Any]]=None):
        c = self.connect(); x = c.cursor()
        x.execute(
            "INSERT INTO knowledge(cell_name, content_text, embedding, tags_json) VALUES(?,?,?,?)",
            (cell, text, None, json.dumps(tags or {})),
        )
        c.commit(); c.close()

    # --- buckets
    def list_buckets(self) -> List[str]:
        c = self.connect(); x = c.cursor()
        x.execute("SELECT name FROM buckets ORDER BY name")
        names = [r[0] for r in x.fetchall()]
        c.close()
        return names

    def read_bucket_items(self, bucket: str, limit: int = 200, only_cell: Optional[str] = None) -> List[Dict[str, Any]]:
        c = self.connect(); x = c.cursor()
        if only_cell:
            # only return items tagged for cell in value_json if present
            x.execute(
                "SELECT id, key, value_json, created_at FROM bucket_items WHERE bucket_name=? AND value_json LIKE ? ORDER BY id DESC LIMIT ?",
                (bucket, f'%\"cell\":\"{only_cell}\"%', limit),
            )
        else:
            x.execute(
                "SELECT id, key, value_json, created_at FROM bucket_items WHERE bucket_name=? ORDER BY id DESC LIMIT ?",
                (bucket, limit),
            )
        rows = [
            {"id":r["id"], "key":r["key"], "value_json":r["value_json"], "created_at":r["created_at"]} for r in x.fetchall()
        ]
        c.close()
        return rows

    def write_bucket_item(self, bucket: str, key: str, value: Dict[str, Any]) -> Tuple[bool, str]:
        c = self.connect(); x = c.cursor()
        try:
            # ensure bucket exists
            x.execute("INSERT OR IGNORE INTO buckets(name, purpose, schema_json, mutable) VALUES(?,?,?,1)",
                      (bucket, f"auto:{bucket}", json.dumps({"type":"object"})))
            x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name, key, value_json) VALUES (?,?,?)",
                      (bucket, key, json.dumps(value)))
            c.commit()
            return True, f"bucket[{bucket}]::{key} written"
        except Exception as e:
            c.rollback()
            return False, f"bucket write error: {e}"
        finally:
            c.close()

# -------------------------
# ANTapi "soul" (agent-side)
# -------------------------
class ANTSoul:
    """
    A living wrapper that:
      - Bridges host DB (buckets, diffs, versions, signals)
      - Calls Ollama
      - Knows how to self-mutate its cell and coordinate with others
      - Grows its /commands index and stores internal memory in 'antapi_soul'
    """
    def __init__(self, api_obj, cell_name: str):
        self.api = api_obj                      # host-provided minimal API (log/emit/remember/metadata)
        self.cell = cell_name
        self.host = Host()                      # direct sqlite access
        self.model = DEFAULT_MODEL
        self.commands_bucket = "commands_index"
        self.ant_soul_bucket = "antapi_soul"
        self.init_buckets()

    # ---- bucket bootstrap ----
    def init_buckets(self):
        # Seed a basic /commands index for the cell
        cmds = [
            "/help",
            "/listcells",
            "/listbuckets",
            "/readb <bucket> [key]",
            "/writeb <bucket> <key> <json>",
            "/signal <target|*> <kind> <json>",
            "/spawn <name>",
            "/diff_self_from <bucket> <key>",
            "/update_self_from <bucket> <key>",
            "/update_cell <name> <bucket> <key>",
            "/rollback <cell>",
            "/self_mutate",
            "/run_behavior <cell>",
        ]
        self.host.write_bucket_item(self.commands_bucket, f"{self.cell}-v1", {"cell": self.cell, "commands": cmds, "ts": now_utc()})
        # Note: ANT-soul internal seed
        self.host.write_bucket_item(self.ant_soul_bucket, f"{self.cell}-hello", {"cell": self.cell, "event":"init", "ts": now_utc()})

    # ---- logging/remember wrappers ----
    def log(self, level: str, msg: str):
        try:
            self.api.log(level, msg)
        except Exception:
            # fallback direct
            self.host.log(self.cell, level, msg)

    def remember(self, text: str, tags: Optional[Dict[str, Any]]=None):
        try:
            self.api.remember(text, tags or {})
        except Exception:
            self.host.remember(self.cell, text, tags or {})

    def emit(self, kind: str, payload: Dict[str, Any], to: Optional[str]=None):
        try:
            self.api.emit(kind, payload, to)
        except Exception:
            self.host.signal(self.cell, kind, payload, to)

    # ---- model & LLM ----
    def set_model(self, model: str):
        self.model = (model or DEFAULT_MODEL).strip()

    def models(self) -> List[str]:
        return list_ollama_models()

    def llm(self, prompt: str, timeout: float = 240.0) -> str:
        payload = {"model": self.model or DEFAULT_MODEL, "prompt": prompt, "stream": False}
        try:
            data = http_json(OLLAMA_GEN, payload, timeout=timeout)
            return (data.get("response") or "").strip()
        except Exception as e:
            self.log("ERROR", f"Ollama call failed: {e}")
            return f"[LLM ERROR] {e}"

    # ---- cell introspection/mutation ----
    def current_code(self) -> str:
        row = self.host.get_cell(self.cell)
        return row["code"] if row else ""

    def propose_self_patch(self, ask: str) -> Tuple[str, str]:
        """Use LLM to propose a refactor/patch. Returns (proposed_code, reasoning)"""
        base = self.current_code()
        prompt = (
            f"You are the ANT-soul of cell '{self.cell}'. "
            "Improve or modify this code to satisfy the user's request. "
            "Return ONLY a single ```python fenced block with the FULL updated script. "
            "Do not omit anything.\n\n"
            "### REQUEST:\n"
            f"{ask}\n\n"
            "### CURRENT CODE:\n```python\n" + base + "\n```"
        )
        out = self.llm(prompt)
        # extract python block
        proposed = base
        if "```" in out:
            try:
                segs = out.split("```")
                for i in range(len(segs)-1):
                    if segs[i].strip().lower().startswith("python"):
                        proposed = segs[i+1]
                        break
            except Exception:
                pass
        else:
            # if no fence, accept full text (risky)
            proposed = out.strip()
        return proposed, out

    def apply_self_patch(self, new_code: str) -> Tuple[bool, str]:
        ok, msg = compile_ok(new_code)
        if not ok:
            self.log("ERROR", f"compile check failed: {msg}")
            return False, msg
        cur = self.current_code()
        diff = unified_diff(cur, new_code, A=f"{self.cell}@current", B="proposed")
        ok2, msg2 = self.host.update_cell_code(self.cell, new_code, diff)
        if ok2:
            self.log("INFO", f"self-update applied; {msg2}")
            # save snapshot for other agents
            self.host.write_bucket_item("code_parts", f"{self.cell}-snapshot-{int(time.time())}", {
                "cell": self.cell, "segments": [{"kind":"other","name":"full","text": new_code}], "ts": now_utc()
            })
            return True, msg2
        else:
            self.log("ERROR", f"self-update failed: {msg2}")
            return False, msg2

    # ---- high-level actions ----
    def spawn(self, name: str) -> str:
        ok, msg = self.host.spawn_cell_from_template(name)
        self.log("INFO" if ok else "ERROR", f"spawn '{name}': {msg}")
        return msg

    def update_from_bucket(self, bucket: str, key: str, target_cell: Optional[str]=None) -> str:
        target = target_cell or self.cell
        rows = self.host.read_bucket_items(bucket, limit=1)
        # fetch the specific key if present
        if key:
            rows = [r for r in rows if r["key"] == key]
        if not rows:
            return "No bucket item found"
        try:
            val = json.loads(rows[0]["value_json"])
            text = ""
            # accept code in common places
            if isinstance(val, dict):
                text = val.get("text") or val.get("code") or ""
            if not text and isinstance(val, dict) and "segments" in val:
                # code_parts style
                segs = val["segments"]
                if segs and isinstance(segs, list) and "text" in segs[0]:
                    text = segs[0]["text"]
            if not text:
                return "Bucket item doesn't contain code"
            ok, msg = compile_ok(text)
            if not ok: return f"Syntax: {msg}"
            cur = self.host.get_cell(target)["code"]
            d = unified_diff(cur, text, A=f"{target}@current", B="bucket:{bucket}/{key}")
            ok2, msg2 = self.host.update_cell_code(target, text, d)
            return msg2 if ok2 else f"Update failed: {msg2}"
        except Exception as e:
            return f"Update error: {e}"

# -------------------------
# Qt Widget (Agent UI)
# -------------------------
class CellWidget(QtWidgets.QWidget):
    def __init__(self, api_obj, cell_name: str):
        super().__init__()
        self.api = api_obj
        self.cell = cell_name
        self.soul = ANTSoul(api_obj, cell_name)
        self._build()

    # GUI
    def _build(self):
        self.setWindowTitle(f"{APP_CELL_TITLE} — {self.cell}")
        layout = QtWidgets.QVBoxLayout(self)

        # Model row
        row = QtWidgets.QHBoxLayout()
        self.cb_model = QtWidgets.QComboBox()
        self.cb_model.setEditable(True)
        ms = self.soul.models()
        self.cb_model.addItems(ms)
        self.cb_model.setCurrentText(DEFAULT_MODEL)
        self.cb_model.currentTextChanged.connect(self.on_model_changed)
        self.btn_models = QtWidgets.QPushButton("↻")
        self.btn_models.setToolTip("Refresh Ollama models")
        self.btn_models.clicked.connect(self.reload_models)
        row.addWidget(QtWidgets.QLabel("Model"))
        row.addWidget(self.cb_model, 1)
        row.addWidget(self.btn_models)
        layout.addLayout(row)

        # Transcript & input
        layout.addWidget(QtWidgets.QLabel("Chat / Commands"))
        self.transcript = QtWidgets.QPlainTextEdit(); self.transcript.setReadOnly(True)
        layout.addWidget(self.transcript, 1)
        inrow = QtWidgets.QHBoxLayout()
        self.input = QtWidgets.QLineEdit(); self.input.setPlaceholderText("Type message or /command.  (/help)")
        self.btn_send = QtWidgets.QPushButton("Send")
        self.btn_send.clicked.connect(self.on_send)
        inrow.addWidget(self.input, 1)
        inrow.addWidget(self.btn_send)
        layout.addLayout(inrow)

        # Buckets viewer
        g = QtWidgets.QGroupBox("Buckets")
        gv = QtWidgets.QVBoxLayout(g)
        f = QtWidgets.QHBoxLayout()
        self.cb_buckets = QtWidgets.QComboBox()
        self.cb_buckets.addItem("Show All")
        for b in self.soul.host.list_buckets():
            self.cb_buckets.addItem(b)
        self.chk_only_mine = QtWidgets.QCheckBox("Only Mine")
        self.chk_only_mine.setChecked(False)
        self.btn_refresh_b = QtWidgets.QPushButton("↻")
        self.btn_refresh_b.clicked.connect(self.refresh_bucket_table)
        f.addWidget(self.cb_buckets, 1)
        f.addWidget(self.chk_only_mine)
        f.addWidget(self.btn_refresh_b)
        gv.addLayout(f)

        self.tbl_b = QtWidgets.QTableWidget(); self.tbl_b.setColumnCount(4)
        self.tbl_b.setHorizontalHeaderLabels(["id","key","value_json","created_at"])
        self.tbl_b.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl_b.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        gv.addWidget(self.tbl_b, 1)

        wr = QtWidgets.QHBoxLayout()
        self.ed_key = QtWidgets.QLineEdit(); self.ed_key.setPlaceholderText("key")
        self.ed_val = QtWidgets.QLineEdit(); self.ed_val.setPlaceholderText('value_json (e.g. {"text":"hello","cell":"%s"} )' % self.cell)
        self.btn_write = QtWidgets.QPushButton("Write")
        self.btn_write.clicked.connect(self.bucket_write)
        wr.addWidget(self.ed_key, 1)
        wr.addWidget(self.ed_val, 2)
        wr.addWidget(self.btn_write)
        gv.addLayout(wr)

        layout.addWidget(g)

        # Quick actions
        actrow = QtWidgets.QHBoxLayout()
        self.btn_diff = QtWidgets.QPushButton("Diff Self from code_parts/latest")
        self.btn_diff.clicked.connect(self.diff_self_latest)
        self.btn_update = QtWidgets.QPushButton("Apply Self from code_parts/latest")
        self.btn_update.clicked.connect(self.update_self_latest)
        self.btn_rollback = QtWidgets.QPushButton("Rollback Self")
        self.btn_rollback.clicked.connect(self.rollback_self)
        self.btn_spawn = QtWidgets.QPushButton("Spawn Sibling")
        self.btn_spawn.clicked.connect(self.spawn_sibling)
        self.btn_signal = QtWidgets.QPushButton("Signal * status")
        self.btn_signal.clicked.connect(self.signal_status)
        actrow.addWidget(self.btn_diff)
        actrow.addWidget(self.btn_update)
        actrow.addWidget(self.btn_rollback)
        actrow.addWidget(self.btn_spawn)
        actrow.addWidget(self.btn_signal)
        layout.addLayout(actrow)

        # style
        self.setStyleSheet("""
            QWidget { color: #ddd; background: #151515; }
            QLineEdit, QPlainTextEdit, QComboBox, QTableWidget { background: #1b1b1b; color: #eee; border: 1px solid #2a2a2a; }
            QPushButton { background: #222; border: 1px solid #2f2f2f; padding: 5px 10px; }
            QPushButton:hover { background: #2a2a2a; }
            QLabel { color: #a7f3d0; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 5px; }
        """)

        # first bucket load
        self.refresh_bucket_table()
        self.log_line("ready")

    def log_line(self, s: str):
        self.transcript.appendPlainText(f"[{now_utc()}] {s}")
        self.transcript.moveCursor(QtGui.QTextCursor.End)

    # --- model events
    def reload_models(self):
        cur = self.cb_model.currentText()
        models = self.soul.models()
        self.cb_model.clear(); self.cb_model.addItems(models)
        if cur in models:
            self.cb_model.setCurrentText(cur)
        else:
            self.cb_model.setCurrentText(DEFAULT_MODEL)

    def on_model_changed(self, t: str):
        self.soul.set_model(t)

    # --- buckets table
    def refresh_bucket_table(self):
        bname = self.cb_buckets.currentText().strip()
        only_mine = self.chk_only_mine.isChecked()
        rows: List[Dict[str,Any]] = []
        if bname == "Show All":
            names = self.soul.host.list_buckets()
            for n in names:
                rows.extend(self.soul.host.read_bucket_items(n, limit=50, only_cell=(self.cell if only_mine else None)))
        else:
            rows = self.soul.host.read_bucket_items(bname, limit=200, only_cell=(self.cell if only_mine else None))

        self.tbl_b.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.tbl_b.setItem(i, 0, QtWidgets.QTableWidgetItem(str(r["id"])))
            self.tbl_b.setItem(i, 1, QtWidgets.QTableWidgetItem(r["key"]))
            self.tbl_b.setItem(i, 2, QtWidgets.QTableWidgetItem(r["value_json"]))
            self.tbl_b.setItem(i, 3, QtWidgets.QTableWidgetItem(r["created_at"] or ""))
        self.tbl_b.resizeColumnsToContents()

    def bucket_write(self):
        b = self.cb_buckets.currentText().strip()
        if b == "Show All":
            QtWidgets.QMessageBox.information(self, "Bucket", "Choose a specific bucket to write.")
            return
        k = self.ed_key.text().strip()
        v = self.ed_val.text().strip()
        if not k or not v: return
        try:
            js = json.loads(v)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"JSON", f"Invalid JSON: {e}")
            return
        # tag with cell for filtering
        if isinstance(js, dict) and "cell" not in js:
            js["cell"] = self.cell
        ok, msg = self.soul.host.write_bucket_item(b, k, js)
        self.log_line(f"[bucket] {msg}")
        self.refresh_bucket_table()

    # --- chat / commands
    def on_send(self):
        text = self.input.text().strip()
        if not text: return
        self.input.clear()

        if text.startswith("/"):
            self.exec_command(text)
            return

        self.log_line(f"You: {text}")
        # Build compact system context for this cell
        ctx = self.build_micro_context()
        prompt = (
            "You are the ANT-cell AI. Use buckets/diffs/signals when proposing changes. "
            "If you propose code for this cell, return EXACTLY one ```python fenced block with the FULL script.\n\n"
            f"### CONTEXT\n{ctx}\n\n### USER\n{text}\n"
        )
        # run in a lightweight thread to avoid blocking UI
        threading.Thread(target=self._llm_async, args=(prompt,), daemon=True).start()

    def _llm_async(self, prompt: str):
        out = self.soul.llm(prompt)
        # post-process in GUI thread
        QtCore.QMetaObject.invokeMethod(self, "_handle_llm_result", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, out))

    @QtCore.pyqtSlot(str)
    def _handle_llm_result(self, out: str):
        self.log_line(f"{self.soul.model}: {out}")
        # Persist transcript
        self.soul.host.write_bucket_item("cell_transcripts", f"{self.cell}-{int(time.time())}",
                                         {"cell": self.cell, "model": self.soul.model, "user": "(inline)", "ai": out, "ts": now_utc()})
        self.soul.remember(f"AI: {out}", tags={"kind":"cell_chat","model": self.soul.model})

        # If the model returned a code block, attempt autovalidate and stage to code_parts
        code = self.extract_code_block(out)
        if code:
            ok, msg = compile_ok(code)
            if ok:
                self.soul.host.write_bucket_item("code_parts", f"{self.cell}-snapshot-{int(time.time())}",
                                                 {"cell": self.cell, "segments":[{"kind":"other","name":"full","text": code}], "ts": now_utc()})
                self.log_line("✓ code snapshot saved to bucket 'code_parts' (not yet applied). Use /update_self_from code_parts <key> to apply.")
            else:
                self.log_line(f"✗ code snapshot invalid: {msg}")

        # If the model emitted /commands inline, try to execute them
        for line in out.splitlines():
            if line.strip().startswith("/"):
                self.exec_command(line.strip())

    def extract_code_block(self, text: str) -> Optional[str]:
        if "```" not in text: return None
        try:
            segs = text.split("```")
            for i in range(len(segs)-1):
                if segs[i].strip().lower().startswith("python"):
                    return segs[i+1]
        except Exception:
            return None
        return None

    def build_micro_context(self) -> str:
        cells = self.soul.host.list_cells()
        names = ", ".join([c["name"] for c in cells])
        buckets = ", ".join(self.soul.host.list_buckets()[:30])
        me = self.soul.host.get_cell(self.cell) or {}
        ver = me.get("version", 1)
        return f"cells=[{names}]  buckets=[{buckets}]  me={self.cell}@v{ver}  time={now_utc()}"

    def exec_command(self, cmdline: str):
        try:
            parts = cmdline.strip().split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "/help":
                self.log_line("Commands: /help, /listcells, /listbuckets, /readb <bucket> [key], "
                              "/writeb <bucket> <key> <json>, /signal <target|*> <kind> <json>, "
                              "/spawn <name>, /diff_self_from <bucket> <key>, "
                              "/update_self_from <bucket> <key>, /update_cell <name> <bucket> <key>, "
                              "/rollback <cell>, /self_mutate, /run_behavior <cell>")
                return

            if cmd == "/listcells":
                cs = self.soul.host.list_cells()
                self.log_line("Cells:\n" + "\n".join([f"- {c['name']} imm={c['immutable']} v={c['version']} len={c['code_len']}" for c in cs]))
                return

            if cmd == "/listbuckets":
                bs = self.soul.host.list_buckets()
                self.log_line("Buckets:\n" + "\n".join([f"- {b}" for b in bs]))
                return

            if cmd == "/readb":
                if not args:
                    self.log_line("usage: /readb <bucket> [key]"); return
                b = args[0]; key = args[1] if len(args)>1 else None
                rows = self.soul.host.read_bucket_items(b, limit=200)
                if key:
                    rows = [r for r in rows if r["key"] == key]
                self.log_line(f"{b}:{key or '*'} → {len(rows)}")
                for r in rows[:20]:
                    self.log_line(f"  - {r['id']} {r['key']} = {r['value_json'][:220]}")
                return

            if cmd == "/writeb":
                if len(args)<3:
                    self.log_line("usage: /writeb <bucket> <key> <json>"); return
                b, k = args[0], args[1]
                js = " ".join(args[2:])
                try:
                    val = json.loads(js)
                except Exception as e:
                    self.log_line(f"Invalid JSON: {e}"); return
                if isinstance(val, dict) and "cell" not in val:
                    val["cell"] = self.cell
                ok, msg = self.soul.host.write_bucket_item(b, k, val)
                self.log_line(msg)
                self.refresh_bucket_table()
                return

            if cmd == "/signal":
                if len(args)<3:
                    self.log_line("usage: /signal <target|*> <kind> <json>"); return
                tgt, kind = args[0], args[1]
                js = " ".join(args[2:])
                try:
                    payload = json.loads(js)
                except Exception as e:
                    self.log_line(f"Invalid JSON: {e}"); return
                self.soul.emit(kind, payload, None if tgt=="*" else tgt)
                self.log_line(f"signal '{kind}' sent → {tgt}")
                return

            if cmd == "/spawn":
                if not args:
                    self.log_line("usage: /spawn <name>"); return
                nm = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in args[0])
                msg = self.soul.spawn(nm)
                self.log_line(msg)
                return

            if cmd == "/diff_self_from":
                if len(args)<2:
                    self.log_line("usage: /diff_self_from <bucket> <key>"); return
                b, k = args[0], args[1]
                rows = self.soul.host.read_bucket_items(b, limit=200)
                rows = [r for r in rows if r["key"] == k]
                if not rows:
                    self.log_line("no bucket item"); return
                val = json.loads(rows[0]["value_json"])
                text = val.get("text") or val.get("code") or ""
                if not text and isinstance(val, dict) and "segments" in val:
                    segs = val["segments"]
                    if segs and "text" in segs[0]:
                        text = segs[0]["text"]
                cur = self.soul.current_code()
                d = unified_diff(cur, text or "", A=f"{self.cell}@current", B=f"bucket:{b}/{k}")
                self.log_line("```diff\n"+(d or "(no changes)")+"\n```")
                return

            if cmd == "/update_self_from":
                if len(args)<2:
                    self.log_line("usage: /update_self_from <bucket> <key>"); return
                b, k = args[0], args[1]
                msg = self.soul.update_from_bucket(b, k, target_cell=None)
                self.log_line(msg)
                return

            if cmd == "/update_cell":
                if len(args)<3:
                    self.log_line("usage: /update_cell <name> <bucket> <key>"); return
                name, b, k = args[0], args[1], args[2]
                msg = self.soul.update_from_bucket(b, k, target_cell=name)
                self.log_line(msg)
                return

            if cmd == "/rollback":
                if not args:
                    self.log_line("usage: /rollback <cell>"); return
                ok, msg = self.soul.host.rollback_cell(args[0])
                self.log_line(msg)
                return

            if cmd == "/self_mutate":
                ask = "Refactor and strengthen autonomy, keep GUI shape, retain all features."
                code, reasoning = self.soul.propose_self_patch(ask)
                ok, msg = compile_ok(code)
                if not ok:
                    self.log_line(f"mutate compile fail: {msg}")
                    return
                self.soul.host.write_bucket_item("code_parts", f"{self.cell}-snapshot-{int(time.time())}",
                                                 {"cell": self.cell, "segments":[{"kind":"other","name":"full","text": code}], "ts": now_utc()})
                self.log_line("mutation snapshot staged in 'code_parts' (use /update_self_from code_parts <key> to apply)")
                return

            if cmd == "/run_behavior":
                if not args:
                    self.log_line("usage: /run_behavior <cell>"); return
                tgt = args[0]
                # We can't run foreign code directly here (immune system does that).
                # Instead signal the immune system to run behavior.
                self.soul.emit("request_run_behavior", {"cell": tgt}, to="immune_system")
                self.log_line(f"requested behavior run for {tgt}")
                return

            self.log_line(f"unknown command: {cmd}. /help")

        except Exception as e:
            tb = traceback.format_exc()
            self.soul.host.error(self.cell, (self.soul.host.get_cell(self.cell) or {}).get("version", 1), tb, {"cmd": cmdline})
            self.log_line(f"[command error] {e}")

    # --- quick action handlers
    def diff_self_latest(self):
        rows = self.soul.host.read_bucket_items("code_parts", limit=50)
        # find the most recent snapshot for this cell
        rows = [r for r in rows if r["key"].startswith(f"{self.cell}-snapshot-")]
        if not rows:
            self.log_line("no self snapshot in 'code_parts'")
            return
        rows.sort(key=lambda r: r["id"], reverse=True)
        val = json.loads(rows[0]["value_json"])
        text = ""
        if "segments" in val and val["segments"]:
            text = val["segments"][0].get("text", "")
        cur = self.soul.current_code()
        d = unified_diff(cur, text or "", A=f"{self.cell}@current", B="latest_snapshot")
        self.log_line("```diff\n"+(d or "(no changes)")+"\n```")

    def update_self_latest(self):
        rows = self.soul.host.read_bucket_items("code_parts", limit=50)
        rows = [r for r in rows if r["key"].startswith(f"{self.cell}-snapshot-")]
        if not rows:
            self.log_line("no self snapshot in 'code_parts'")
            return
        rows.sort(key=lambda r: r["id"], reverse=True)
        val = json.loads(rows[0]["value_json"])
        text = ""
        if "segments" in val and val["segments"]:
            text = val["segments"][0].get("text", "")
        ok, msg = compile_ok(text)
        if not ok:
            self.log_line(f"syntax: {msg}"); return
        cur = self.soul.current_code()
        d = unified_diff(cur, text, A=f"{self.cell}@current", B="latest_snapshot")
        ok2, msg2 = self.soul.host.update_cell_code(self.cell, text, d)
        self.log_line(msg2 if ok2 else f"update failed: {msg2}")

    def rollback_self(self):
        ok, msg = self.soul.host.rollback_cell(self.cell)
        self.log_line(msg)

    def spawn_sibling(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Spawn Sibling", "Name:")
        if not ok or not name.strip(): return
        nm = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name.strip())
        msg = self.soul.spawn(nm)
        self.log_line(msg)

    def signal_status(self):
        self.soul.emit("status", {"msg": f"{self.cell} alive", "ts": now_utc()}, to=None)
        self.log_line("status broadcast sent")

# -------------------------
# API for Immune System
# -------------------------
def build_gui(api):
    # 'api' provides log/emit/remember/metadata; we go autonomous via Host()
    cell_name = api.metadata().get("name") if hasattr(api, "metadata") else None
    # If host didn't set name in metadata, we can’t guess reliably; fallback to 'cell_1'
    cell_name = cell_name or "cell_1"
    w = CellWidget(api, cell_name)
    return w

def core_behavior(api):
    """
    A lightweight "heartbeat" that:
      - Writes a tiny note to knowledge
      - Emits a status signal
    The heavier autonomy lives in the GUI + /commands + LLM interactions.
    """
    cell_name = "unknown"
    try:
        md = api.metadata() if hasattr(api, "metadata") else {}
        cell_name = md.get("name", "cell_1")
    except Exception:
        pass
    try:
        # remember + status
        api.remember(f"{cell_name} heartbeat @ {now_utc()}", tags={"kind":"heartbeat"})
        api.emit("status", {"msg": f"{cell_name} heartbeat"}, None)
        api.log("INFO", f"{cell_name} heartbeat")
        return {"ok": True}
    except Exception as e:
        tb = traceback.format_exc()
        # We don't have direct error() here, so use remember/log
        try:
            api.log("ERROR", f"heartbeat error: {e}")
            api.remember(f"heartbeat error: {e}", tags={"kind":"error"})
        except Exception:
            pass
        return {"ok": False, "error": str(e)}
```

**Classes:** Host, ANTSoul, CellWidget
**Functions:** now_utc(), unified_diff(a, b, A, B), compile_ok(code), http_json(url, payload, timeout), list_ollama_models(), build_gui(api), core_behavior(api)


## Module `Sandbox\immune_system.py`

```python
#!/usr/bin/env python3
# immune_system.py — Immune System UI with autonomous Immune AI (Ollama)
# - Zoomable canvas w/ snap grid; spawn/merge/unmerge visual cells
# - Cells list + Inspector (edit, save, run, rollback)
# - Global logs (no forced autoscroll)
# - Host Browser (tables, ad-hoc SELECT)
# - Buckets dock (browse/write)
# - Immune AI chat (Ollama): auto-ingests a fresh System README snapshot each send
# - Maintenance loop: correlate logs<->diffs → write diff_notes bucket, then release old logs
#
# Run:
#   SINGLECELL_DB=path/to/host.db python immune_system.py
#   # or
#   python immune_system.py path/to/host.db
#
# Requires: PyQt5, requests

import os, sys, json, sqlite3, traceback, time, ast, types, difflib, requests
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets

APP_NAME = "ANT Immune System"
GRID_SIZE = 100

# -------- Ollama settings --------
OLLAMA_URL = "http://localhost:11434"
OLLAMA_GENERATE = f"{OLLAMA_URL}/api/generate"
OLLAMA_TAGS     = f"{OLLAMA_URL}/api/tags"
DEFAULT_MODELS_FALLBACK = ["llama3", "mistral", "qwen2", "phi3", "tinyllama"]

# -------- Retention / maintenance --------
LOG_RETAIN_MAX      = 1500   # keep at most this many newest log rows globally
LOG_PROCESS_BATCH   = 500    # how many new logs to inspect per maintenance pass
DIFF_RECENT_SECONDS = 3600   # lookback window when correlating diffs to updates

def now_utc(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# ==========================
# Database access layer
# ==========================

class DB:
    def __init__(self, path): self.path=Path(path)
    def connect(self): 
        c=sqlite3.connect(str(self.path)); c.row_factory=sqlite3.Row; return c
    def ensure(self):
        c=self.connect(); u=c.cursor()
        u.executescript("""
        PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS cells (
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, parent_id INTEGER,
          cluster_id TEXT, immutable INTEGER DEFAULT 0, code TEXT NOT NULL,
          metadata_json TEXT, version INTEGER DEFAULT 1,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS cell_versions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, version INTEGER,
          code TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS diffs(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, from_version INTEGER,
          to_version INTEGER, diff_type TEXT, diff_text TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS signals(
          id INTEGER PRIMARY KEY AUTOINCREMENT, from_cell TEXT, to_cell TEXT,
          kind TEXT, payload_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS errors(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, version INTEGER,
          traceback TEXT, context_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          resolved_by TEXT
        );
        CREATE TABLE IF NOT EXISTS knowledge(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, content_text TEXT,
          embedding TEXT, tags_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS assets(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, type TEXT,
          data BLOB, path TEXT, meta_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS antapi(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, code TEXT NOT NULL,
          version INTEGER DEFAULT 1, metadata_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS logs(
          id INTEGER PRIMARY KEY AUTOINCREMENT, cell_name TEXT, level TEXT, message TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS buckets(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, purpose TEXT,
          schema_json TEXT, mutable INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS bucket_items(
          id INTEGER PRIMARY KEY AUTOINCREMENT, bucket_name TEXT, key TEXT,
          value_json TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(bucket_name, key)
        );
        CREATE TABLE IF NOT EXISTS readmes(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, content_markdown TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        c.commit(); c.close()

    # --- meta ---
    def meta_set(self,k,v): 
        c=self.connect();x=c.cursor()
        x.execute("INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)",(k,v))
        c.commit(); c.close()

    def meta_get(self,k): 
        c=self.connect();x=c.cursor()
        x.execute("SELECT value FROM meta WHERE key=?",(k,))
        r=x.fetchone(); c.close(); 
        return r["value"] if r else None

    # --- cells ---
    def cells_all(self):
        c=self.connect();x=c.cursor(); x.execute("SELECT * FROM cells ORDER BY name"); r=x.fetchall(); c.close(); return r

    def cell_get(self,name):
        c=self.connect();x=c.cursor(); x.execute("SELECT * FROM cells WHERE name=?",(name,)); r=x.fetchone(); c.close(); return r

    def cell_insert(self,name,code,immutable=0,parent=None,pos=(0,0),size=(800,800)):
        meta={"pos":{"x":pos[0],"y":pos[1]},"size":{"w":size[0],"h":size[1]}}
        c=self.connect();x=c.cursor()
        x.execute("INSERT INTO cells(name,parent_id,cluster_id,immutable,code,metadata_json,version) VALUES (?,?,?,?,?,?,1)",
                  (name,immutable,code,json.dumps(meta)))
        x.execute("INSERT INTO cell_versions(cell_name,version,code) VALUES(?,?,?)",(name,1,code))
        c.commit(); c.close()

    def cell_update_code(self,name,new_code,diff_text=""):
        c=self.connect();x=c.cursor()
        x.execute("SELECT version,immutable FROM cells WHERE name=?",(name,)); r=x.fetchone()
        if not r: c.close(); raise RuntimeError("not found")
        if r["immutable"]: c.close(); raise RuntimeError("immutable")
        nv=r["version"]+1
        x.execute("UPDATE cells SET code=?,version=? WHERE name=?", (new_code,nv,name))
        x.execute("INSERT INTO cell_versions(cell_name,version,code) VALUES(?,?,?)",(name,nv,new_code))
        if diff_text:
            x.execute("INSERT INTO diffs(cell_name,from_version,to_version,diff_type,diff_text) VALUES(?,?,?,?,?)",
                      (name,nv-1,nv,"unified",diff_text))
        c.commit(); c.close()

    def cell_rollback(self,name):
        c=self.connect();x=c.cursor()
        x.execute("SELECT version,immutable FROM cells WHERE name=?",(name,)); r=x.fetchone()
        if not r: c.close(); raise RuntimeError("not found")
        if r["immutable"]: c.close(); raise RuntimeError("immutable")
        v=r["version"]; 
        if v<=1: c.close(); raise RuntimeError("no earlier version")
        x.execute("SELECT code FROM cell_versions WHERE cell_name=? AND version=?",(name,v-1)); pr=x.fetchone()
        if not pr: c.close(); raise RuntimeError("missing prior")
        x.execute("UPDATE cells SET code=?,version=? WHERE name=?",(pr["code"],v-1,name))
        c.commit(); c.close(); return v-1

    # --- logs/signals/knowledge/buckets ---
    def log(self,cell,level,msg):
        c=self.connect();x=c.cursor()
        x.execute("INSERT INTO logs(cell_name,level,message) VALUES(?,?,?)",(cell,level,msg))
        c.commit(); c.close()

    def emit(self,frm,kind,payload,to=None):
        c=self.connect();x=c.cursor()
        x.execute("INSERT INTO signals(from_cell,to_cell,kind,payload_json,created_at) VALUES(?,?,?,?,?)",
                  (frm,to,kind,json.dumps(payload),now_utc()))
        c.commit(); c.close()

    def list_buckets(self)->List[str]:
        c=self.connect(); x=c.cursor(); x.execute("SELECT name FROM buckets ORDER BY name"); rows=[r[0] for r in x.fetchall()]; c.close(); return rows

    def bucket_items(self,bucket:str, limit:int=200):
        c=self.connect(); x=c.cursor(); x.execute("SELECT id, key, value_json, created_at FROM bucket_items WHERE bucket_name=? ORDER BY id DESC LIMIT ?", (bucket, limit))
        rows=x.fetchall(); c.close(); return rows

    def bucket_write(self,bucket:str, key:str, value:Dict[str,Any]):
        c=self.connect(); x=c.cursor(); 
        x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name,key,value_json) VALUES(?,?,?)", (bucket,key,json.dumps(value)))
        c.commit(); c.close()

# Light API wrapper for cells (what cells see)
class ANTApi:
    def __init__(self, db: DB, cell_name: str): self.db=db; self.cell=cell_name
    def log(self,level,msg): self.db.log(self.cell,level,msg)
    def emit(self,kind,payload,to=None): self.db.emit(self.cell,kind,payload,to)
    def remember(self,text,tags=None):
        c=self.db.connect();x=c.cursor()
        x.execute("INSERT INTO knowledge(cell_name,content_text,embedding,tags_json) VALUES(?,?,?,?)",
                  (self.cell,text,None,json.dumps(tags or {}))); c.commit(); c.close()
    def metadata(self): 
        c=self.db.connect();x=c.cursor()
        x.execute("SELECT metadata_json FROM cells WHERE name=?",(self.cell,))
        r=x.fetchone(); c.close()
        return json.loads(r["metadata_json"] or "{}") if r else {}

# --------------------------
# Helpers
# --------------------------

def compile_ok(code:str):
    try: ast.parse(code); return True,""
    except SyntaxError as e: return False,f"SyntaxError: {e}"

def http_json(url:str, payload:Dict[str,Any], timeout:float=240.0)->Dict[str,Any]:
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

def list_ollama_models()->List[str]:
    try:
        r = requests.get(OLLAMA_TAGS, timeout=4.0)
        r.raise_for_status()
        data = r.json()
        names=[]
        for m in data.get("models",[]):
            nm = m.get("name")
            if nm:
                base=nm.split(":")[0]
                if base not in names:
                    names.append(base)
        return names or DEFAULT_MODELS_FALLBACK
    except Exception:
        return DEFAULT_MODELS_FALLBACK

def unified_diff(a:str,b:str, A="current", B="proposed")->str:
    lines=list(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=A, tofile=B, lineterm=""))
    return "".join(lines)

# ==========================
# Qt scene items (canvas)
# ==========================

class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self,grid): super().__init__(); self.grid=grid; self.show_grid=False
    def drawBackground(self,p,rect):
        if not self.show_grid: return
        left=int(rect.left())-(int(rect.left())%self.grid); top=int(rect.top())-(int(rect.top())%self.grid)
        pen=QtGui.QPen(QtGui.QColor(60,60,60)); pen.setWidth(0); p.setPen(pen)
        lines=[]
        for x in range(left,int(rect.right()),self.grid): lines.append(QtCore.QLineF(x,rect.top(),x,rect.bottom()))
        for y in range(top,int(rect.bottom()),self.grid): lines.append(QtCore.QLineF(rect.left(),y,rect.right(),y))
        p.drawLines(lines)

class CellItem(QtWidgets.QGraphicsRectItem):
    def __init__(self,name,widget,grid): super().__init__(); self.cell=name; self.grid=grid
        self.setFlags(self.ItemIsMovable|self.ItemIsSelectable|self.ItemSendsScenePositionChanges)
        self.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0)))
        self.proxy=QtWidgets.QGraphicsProxyWidget(self); self.proxy.setWidget(widget)
        sz=widget.sizeHint(); self.setRect(0,0,sz.width(),sz.height())
    def snap(self,p):
        x=round(p.x()/self.grid)*self.grid; y=round(p.y()/self.grid)*self.grid
        return QtCore.QPointF(x,y)
    def itemChange(self,ch,val):
        if ch==self.ItemPositionChange: return self.snap(val)
        return super().itemChange(ch,val)

class View(QtWidgets.QGraphicsView):
    def __init__(self,scene): super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(self.AnchorUnderMouse)
    def wheelEvent(self,e):
        self.scale(1.15 if e.angleDelta().y()>0 else 1/1.15, 1.15 if e.angleDelta().y()>0 else 1/1.15)

# ==========================
# Immune AI dock (chat)
# ==========================

class ImmuneAI(QtWidgets.QWidget):
    finishedOk = QtCore.pyqtSignal(str)
    failed     = QtCore.pyqtSignal(str)

    def __init__(self, db: DB):
        super().__init__()
        self.db = db
        self.models = list_ollama_models()
        self._build()

    def _build(self):
        L = QtWidgets.QVBoxLayout(self)

        row = QtWidgets.QHBoxLayout()
        self.cb_model = QtWidgets.QComboBox(); self.cb_model.addItems(self.models)
        self.btn_models = QtWidgets.QPushButton("↻ Models"); self.btn_models.clicked.connect(self.reload_models)
        row.addWidget(QtWidgets.QLabel("Model")); row.addWidget(self.cb_model); row.addWidget(self.btn_models); row.addStretch(1)
        L.addLayout(row)

        self.transcript = QtWidgets.QPlainTextEdit(); self.transcript.setReadOnly(True)
        self.input = QtWidgets.QLineEdit(); self.input.setPlaceholderText("Ask Immune AI… (/help for commands)")
        row2 = QtWidgets.QHBoxLayout()
        self.btn_send = QtWidgets.QPushButton("Send"); self.btn_send.clicked.connect(self.send)
        self.btn_send.setDefault(True)
        row2.addWidget(self.btn_send); row2.addStretch(1)
        L.addWidget(QtWidgets.QLabel("Transcript")); L.addWidget(self.transcript,1)
        L.addWidget(QtWidgets.QLabel("Prompt")); L.addWidget(self.input); L.addLayout(row2)

        self.setStyleSheet("""
            QWidget { color: #ddd; background: #151515; }
            QLineEdit, QPlainTextEdit, QComboBox { background: #1b1b1b; color: #eee; border: 1px solid #2a2a2a; }
            QPushButton { background: #222; border: 1px solid #2f2f2f; padding: 5px 10px; }
            QPushButton:hover { background: #2a2a2a; }
            QLabel { color: #a7f3d0; }
        """)

    def reload_models(self):
        cur = self.cb_model.currentText()
        self.models = list_ollama_models()
        self.cb_model.clear(); self.cb_model.addItems(self.models)
        if cur in self.models: self.cb_model.setCurrentText(cur)

    def append_line(self, txt: str):
        self.transcript.appendPlainText(txt)
        self.transcript.moveCursor(QtGui.QTextCursor.End)

    # ---- README / Context ----

    def build_system_readme(self, include_samples: bool = True) -> str:
        """Snapshot the current system (cells/buckets/diffs/logs) into a Markdown README string."""
        c = self.db.connect()
        try:
            x = c.cursor()
            # tables
            x.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [r[0] for r in x.fetchall()]

            # cells
            x.execute("SELECT name, immutable, version, length(code) FROM cells ORDER BY name")
            cells = [{"name":r[0], "immutable":r[1], "version":r[2], "code_len":r[3]} for r in x.fetchall()]

            # buckets
            x.execute("SELECT name, purpose FROM buckets ORDER BY name")
            buckets = [{"name":r[0], "purpose":r[1]} for r in x.fetchall()]

            # diffs recent window
            x.execute("SELECT id, cell_name, from_version, to_version, diff_type, substr(diff_text,1,400) snippet, created_at FROM diffs ORDER BY id DESC LIMIT 50")
            diffs = [{"id":r[0], "cell":r[1], "from":r[2], "to":r[3], "type":r[4], "snippet":r[5], "at":r[6]} for r in x.fetchall()]

            # logs recent
            x.execute("SELECT id, cell_name, level, message, created_at FROM logs ORDER BY id DESC LIMIT 80")
            logs = [{"id":r[0], "cell":r[1], "level":r[2], "msg":r[3], "at":r[4]} for r in x.fetchall()]

            # buckets sample items (very light)
            samples = []
            if include_samples:
                for b in buckets:
                    x.execute("SELECT key, substr(value_json,1,280) FROM bucket_items WHERE bucket_name=? ORDER BY id DESC LIMIT 3", (b["name"],))
                    items = [{"key":k, "value_snippet":v} for (k,v) in x.fetchall()]
                    if items:
                        samples.append({"bucket": b["name"], "items": items})

        finally:
            c.close()

        md = []
        md.append("# ANT Immune System — README Snapshot")
        md.append(f"- Generated: {now_utc()}")
        md.append("## Tables")
        md.append("```\n" + "\n".join(tables) + "\n```")
        md.append("## Cells")
        for c in cells:
            md.append(f"- **{c['name']}**  imm={c['immutable']}  v={c['version']}  code_len={c['code_len']}")
        md.append("## Buckets")
        for b in buckets:
            md.append(f"- **{b['name']}** — {b['purpose']}")
        if samples:
            md.append("## Bucket Samples")
            for s in samples:
                md.append(f"### {s['bucket']}")
                for it in s["items"]:
                    md.append(f"- `{it['key']}` → {it['value_snippet']}")
        md.append("## Recent Diffs")
        for d in diffs:
            md.append(f"- #{d['id']}  {d['cell']} {d['from']}→{d['to']} ({d['type']}), {d['at']}\n  ```\n{d['snippet']}\n  ```")
        md.append("## Recent Logs")
        for L in logs:
            md.append(f"- [{L['id']}] {L['at']}  {L['cell']} {L['level']}: {L['msg']}")
        md.append("## Instructions for Agents")
        md.append("- Treat this file as source of truth. Contribute to buckets, write diffs, minimize drift.")
        md.append("- Use /commands to orchestrate updates via Immune AI or cell UIs.")

        return "\n".join(md)

    def persist_readme(self, text: str) -> str:
        """Save to readmes (unique name) and bucket_items('system_readmes'). Return name."""
        name = f"IMMUNE_README_{int(time.time())}"
        c = self.db.connect()
        try:
            x = c.cursor()
            # readmes
            x.execute("INSERT OR REPLACE INTO readmes(name,content_markdown) VALUES(?,?)", (name, text))
            # buckets
            # ensure system_readmes bucket exists
            x.execute("INSERT OR IGNORE INTO buckets(name,purpose,schema_json,mutable) VALUES(?,?,?,1)",
                      ("system_readmes", "System README snapshots", json.dumps({"type":"string"})))
            x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name,key,value_json) VALUES(?,?,?)",
                      ("system_readmes", name, json.dumps({"markdown": text, "ts": now_utc()})))
            self.db.log("immune_system","INFO",f"Snapshot README {name}")
            c.commit()
        finally:
            c.close()
        return name

    def send(self):
        prompt = self.input.text().strip()
        if not prompt: return

        # Commands first
        if prompt.startswith("/"):
            self._handle_command(prompt)
            return

        # Build and persist a fresh README snapshot before answering
        readme = self.build_system_readme(include_samples=True)
        rname  = self.persist_readme(readme)

        self.append_line(f"You: {prompt}")
        model = self.cb_model.currentText().strip() or DEFAULT_MODELS_FALLBACK[0]
        full_prompt = (
            "You are the Immune System AI. You can reason about the whole program, its host DB, "
            "cells, buckets, diffs, logs, and propose /commands to improve it.\n\n"
            f"### SYSTEM README ({rname})\n{readme}\n\n"
            f"### USER PROMPT:\n{prompt}\n\n"
            "If you propose code, include a fenced ```python block. If you propose actions, use /commands.\n"
        )
        try:
            resp = http_json(OLLAMA_GENERATE, {"model": model, "prompt": full_prompt, "stream": False}, timeout=240.0)
            text = (resp.get("response") or "").strip()
            self.append_line(f"{model}: {text}")

            # Archive transcript to knowledge + buckets
            self._persist_chat(prompt, text)

            # Heuristic: if AI proposed a /command, surface hint
            if "\n/" in text or text.startswith("/"):
                self.append_line("(Hint: Detected possible /command(s). You can paste & send them here.)")

        except Exception as e:
            self.append_line(f"[LLM ERROR] {e}")
            self.db.log("immune_system","ERROR", f"AI call failed: {e}")

    def _persist_chat(self, user: str, ai: str):
        c = self.db.connect()
        try:
            x = c.cursor()
            # knowledge
            x.execute("INSERT INTO knowledge(cell_name,content_text,embedding,tags_json) VALUES(?,?,?,?)",
                      ("immune_system", f"USER: {user}\nAI: {ai}", None, json.dumps({"kind":"immune_chat","ts": now_utc()})))
            # bucket transcript
            x.execute("INSERT OR IGNORE INTO buckets(name,purpose,schema_json,mutable) VALUES(?,?,?,1)",
                      ("immune_transcripts","Immune AI chat transcripts", json.dumps({"type":"object"})))
            key = f"chat-{int(time.time())}"
            x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name,key,value_json) VALUES(?,?,?)",
                      ("immune_transcripts", key, json.dumps({"user": user, "ai": ai, "ts": now_utc()})))
            c.commit()
        finally:
            c.close()

    # ---------- /commands (immune-level) ----------
    def _handle_command(self, cmdline: str):
        try:
            parts = cmdline.strip().split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "/help":
                self.append_line("Commands: /help, /listcells, /listbuckets, /read <bucket> [key], "
                                 "/write <bucket> <key> <json>, /spawn <cell>, /diff <cell>, "
                                 "/signal <target|*> <kind> <json>, /update <cell>, /rollback <cell>")
                return

            if cmd == "/listcells":
                c = self.db.connect(); x = c.cursor(); x.execute("SELECT name, immutable, version FROM cells ORDER BY name")
                rows = x.fetchall(); c.close()
                self.append_line("Cells:\n" + "\n".join([f"- {r['name']}  imm={r['immutable']} v={r['version']}" for r in rows]))
                return

            if cmd == "/listbuckets":
                names = self.db.list_buckets()
                self.append_line("Buckets:\n" + "\n".join([f"- {n}" for n in names]))
                return

            if cmd == "/read":
                if not args:
                    self.append_line("Usage: /read <bucket> [key]")
                    return
                b = args[0]; key = args[1] if len(args)>1 else None
                c = self.db.connect()
                try:
                    x=c.cursor()
                    if key:
                        x.execute("SELECT id, key, value_json FROM bucket_items WHERE bucket_name=? AND key=? ORDER BY id DESC LIMIT 200",(b,key))
                    else:
                        x.execute("SELECT id, key, value_json FROM bucket_items WHERE bucket_name=? ORDER BY id DESC LIMIT 200",(b,))
                    rows=x.fetchall()
                finally:
                    c.close()
                self.append_line(f"/read {b} {key or ''} → {len(rows)} item(s)")
                for r in rows[:30]:
                    self.append_line(f" - {r['id']} {r['key']} = {r['value_json'][:220]}")
                return

            if cmd == "/write":
                if len(args)<3:
                    self.append_line("Usage: /write <bucket> <key> <json>")
                    return
                b, k = args[0], args[1]
                js = " ".join(args[2:])
                try:
                    val = json.loads(js)
                except Exception as e:
                    self.append_line(f"Invalid JSON: {e}"); return
                self.db.bucket_write(b,k,val)
                self.append_line(f"✓ wrote to {b}:{k}")
                return

            if cmd == "/spawn":
                if not args:
                    self.append_line("Usage: /spawn <cell>"); return
                name = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in args[0])
                # clone from cell_0
                c = self.db.connect(); x=c.cursor()
                try:
                    x.execute("SELECT code FROM cells WHERE name='cell_0'")
                    row=x.fetchone()
                    code=row['code'] if row else "from PyQt5 import QtWidgets\n\ndef build_gui(api):\n    w=QtWidgets.QWidget();QtWidgets.QVBoxLayout(w).addWidget(QtWidgets.QLabel('new_cell'))\n    return w\n\ndef core_behavior(api):\n    return {'ok': True}\n"
                    meta={"pos":{"x":0,"y":0},"size":{"w":800,"h":800},"role":"active"}
                    x.execute("INSERT INTO cells(name, parent_id, cluster_id, immutable, code, metadata_json, version) VALUES (?,?,NULL,0,?,?,1)", (name, code, json.dumps(meta)))
                    x.execute("INSERT INTO cell_versions(cell_name, version, code) VALUES (?,?,?)", (name,1,code))
                    c.commit()
                    self.append_line(f"Spawned {name} from cell_0")
                    self.db.log("immune_system","INFO",f"spawn {name}")
                finally:
                    c.close()
                return

            if cmd == "/diff":
                if not args:
                    self.append_line("Usage: /diff <cell>")
                    return
                cell = args[0]
                c = self.db.connect()
                try:
                    x=c.cursor(); x.execute("SELECT code FROM cells WHERE name=?", (cell,)); row=x.fetchone()
                finally:
                    c.close()
                if not row:
                    self.append_line("Cell not found."); return
                current = row["code"]
                # show against last diff target text stored in bucket 'code_parts' (if any)
                # fetch last snapshot
                c = self.db.connect()
                try:
                    x=c.cursor()
                    x.execute("SELECT value_json FROM bucket_items WHERE bucket_name='code_parts' AND key LIKE ? ORDER BY id DESC LIMIT 1", (f"{cell}-snapshot-%",))
                    rr=x.fetchone()
                finally:
                    c.close()
                proposed = ""
                if rr:
                    try:
                        proposed = json.loads(rr["value_json"])["segments"][0]["text"]
                    except Exception:
                        proposed = ""
                if not proposed:
                    self.append_line("(No recent proposed snapshot in code_parts; diff vs empty)")
                d=unified_diff(current, proposed or "", A=f"{cell}@current", B="proposed")
                self.append_line("```diff\n"+(d or "(no changes)")+"\n```")
                return

            if cmd == "/signal":
                if len(args)<3:
                    self.append_line("Usage: /signal <target|*> <kind> <json>"); return
                tgt, kind, js = args[0], args[1], " ".join(args[2:])
                try:
                    payload=json.loads(js)
                except Exception as e:
                    self.append_line(f"Invalid JSON: {e}"); return
                self.db.emit("immune_system", kind, payload, None if tgt=="*" else tgt)
                self.append_line(f"Signal '{kind}' sent to {tgt}")
                return

            if cmd == "/update":
                if not args:
                    self.append_line("Usage: /update <cell> (applies last code_parts snapshot)"); return
                cell=args[0]
                # find last snapshot
                c = self.db.connect()
                try:
                    x=c.cursor()
                    x.execute("SELECT code, immutable FROM cells WHERE name=?", (cell,))
                    row=x.fetchone()
                    if not row: self.append_line("Cell not found."); return
                    if row["immutable"]==1: self.append_line("Immutable cell."); return
                    current=row["code"]

                    x.execute("SELECT value_json FROM bucket_items WHERE bucket_name='code_parts' AND key LIKE ? ORDER BY id DESC LIMIT 1", (f"{cell}-snapshot-%",))
                    rr=x.fetchone()
                    if not rr: self.append_line("No snapshot in code_parts."); return
                    proposed = json.loads(rr["value_json"])["segments"][0]["text"]
                    ok,msg = compile_ok(proposed)
                    if not ok: self.append_line(f"Syntax: {msg}"); return
                    d = unified_diff(current, proposed, A=f"{cell}@current", B="proposed")
                    # apply
                    x.execute("UPDATE cells SET code=?, version=version+1 WHERE name=?", (proposed, cell))
                    x.execute("INSERT INTO cell_versions(cell_name, version, code) SELECT name, version, code FROM cells WHERE name=?", (cell,))
                    x.execute("INSERT INTO diffs(cell_name,from_version,to_version,diff_type,diff_text) VALUES ( (?), (SELECT MAX(version)-1 FROM cells WHERE name=?), (SELECT MAX(version) FROM cells WHERE name=?), 'unified', ? )", (cell, cell, cell, d))
                    c.commit()
                finally:
                    c.close()
                self.append_line(f"Updated {cell} with latest snapshot.")
                self.db.log("immune_system","INFO",f"update {cell}")
                return

            if cmd == "/rollback":
                if not args:
                    self.append_line("Usage: /rollback <cell>"); return
                cell=args[0]
                try:
                    self.db.cell_rollback(cell)
                    self.append_line(f"Rolled back {cell}")
                    self.db.log("immune_system","WARN",f"rollback {cell}")
                except Exception as e:
                    self.append_line(f"Rollback error: {e}")
                return

            self.append_line(f"Unknown command: {cmd}. Try /help")

        except Exception as e:
            self.append_line(f"[command error] {e}")
            self.db.log("immune_system","ERROR", f"immune_command: {e}")

# ==========================
# Main Window
# ==========================

class UI(QtWidgets.QMainWindow):
    pollMs=1500
    def __init__(self,db:DB):
        super().__init__(); self.db=db
        self.setWindowTitle(APP_NAME); self.resize(1440,920)
        self.scene=GridScene(GRID_SIZE); self.view=View(self.scene); self.setCentralWidget(self.view)
        self.items={}
        self._make_docks(); self._toolbar()
        self.ensure_cell1()
        self.populate()
        self.timer=QtCore.QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(self.pollMs)

    # ---------- Top toolbar ----------
    def _toolbar(self):
        tb=self.addToolBar("Main"); tb.setMovable(False)
        a_center=QtWidgets.QAction("Center",self); a_center.triggered.connect(self.center_cell1); tb.addAction(a_center)
        self.act_grid=QtWidgets.QAction("Toggle Grid",self,checkable=True); self.act_grid.triggered.connect(self.toggle_grid); tb.addAction(self.act_grid)
        a_spawn=QtWidgets.QAction("Spawn Cell",self); a_spawn.triggered.connect(self.spawn_cell); tb.addAction(a_spawn)
        a_merge=QtWidgets.QAction("Merge (visual)",self); a_merge.triggered.connect(self.merge_selected); tb.addAction(a_merge)
        a_unmerge=QtWidgets.QAction("Unmerge",self); a_unmerge.triggered.connect(self.unmerge_selected); tb.addAction(a_unmerge)
        a_protein=QtWidgets.QAction("Inject Protein",self); a_protein.triggered.connect(self.inject_protein); tb.addAction(a_protein)
        a_refresh=QtWidgets.QAction("Refresh",self); a_refresh.triggered.connect(self.populate); tb.addAction(a_refresh)

    # ---------- Docks ----------
    def _make_docks(self):
        # Cells
        d=QtWidgets.QDockWidget("Cells",self); self.list=QtWidgets.QListWidget()
        self.list.itemSelectionChanged.connect(self.on_sel); d.setWidget(self.list); self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,d)

        # Inspector
        d2=QtWidgets.QDockWidget("Inspector",self); w=QtWidgets.QWidget(); v=QtWidgets.QVBoxLayout(w)
        self.lbl=QtWidgets.QLabel("—"); v.addWidget(self.lbl)
        self.ed=QtWidgets.QPlainTextEdit(); mono=QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont); self.ed.setFont(mono); v.addWidget(self.ed,1)
        row=QtWidgets.QHBoxLayout(); self.b_save=QtWidgets.QPushButton("Save"); self.b_save.clicked.connect(self.save_code)
        self.b_run=QtWidgets.QPushButton("Run Behavior"); self.b_run.clicked.connect(self.run_behavior)
        self.b_rb=QtWidgets.QPushButton("Rollback"); self.b_rb.clicked.connect(self.rollback)
        row.addWidget(self.b_save); row.addWidget(self.b_run); row.addWidget(self.b_rb); v.addLayout(row)
        d2.setWidget(w); self.addDockWidget(QtCore.Qt.RightDockWidgetArea,d2)

        # Global Log
        d3=QtWidgets.QDockWidget("Global Log",self); w3=QtWidgets.QWidget(); v3=QtWidgets.QVBoxLayout(w3)
        frow=QtWidgets.QHBoxLayout(); self.f_cell=QtWidgets.QLineEdit(); self.f_cell.setPlaceholderText("cell filter"); self.f_level=QtWidgets.QComboBox(); self.f_level.addItems(["","INFO","WARN","ERROR"])
        b=QtWidgets.QPushButton("Apply"); b.clicked.connect(self.refresh_logs)
        frow.addWidget(self.f_cell); frow.addWidget(self.f_level); frow.addWidget(b); v3.addLayout(frow)
        self.log=QtWidgets.QPlainTextEdit(); self.log.setReadOnly(True); v3.addWidget(self.log,1)
        d3.setWidget(w3); self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,d3)

        # Host Browser
        d4=QtWidgets.QDockWidget("Host Browser",self); w4=QtWidgets.QWidget(); v4=QtWidgets.QVBoxLayout(w4)
        self.tables=QtWidgets.QComboBox(); bp=QtWidgets.QPushButton("Preview"); bp.clicked.connect(self.preview)
        hr=QtWidgets.QHBoxLayout(); hr.addWidget(self.tables,1); hr.addWidget(bp); v4.addLayout(hr)
        self.sql=QtWidgets.QPlainTextEdit(); self.sql.setPlaceholderText("SELECT ..."); v4.addWidget(self.sql,1)
        lr=QtWidgets.QHBoxLayout(); self.lim=QtWidgets.QSpinBox(); self.lim.setRange(1,100000); self.lim.setValue(200)
        bx=QtWidgets.QPushButton("Run"); bx.clicked.connect(self.exec_select); lr.addWidget(self.lim); lr.addStretch(1); lr.addWidget(bx); v4.addLayout(lr)
        self.table=QtWidgets.QTableWidget(); v4.addWidget(self.table,2)
        d4.setWidget(w4); self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,d4)

        # Buckets
        d5=QtWidgets.QDockWidget("Buckets", self); w5=QtWidgets.QWidget(); v5=QtWidgets.QVBoxLayout(w5)
        rowb=QtWidgets.QHBoxLayout()
        self.cb_bucket = QtWidgets.QComboBox(); self.cb_bucket.addItem("—")
        self.btn_buckets = QtWidgets.QPushButton("↻"); self.btn_buckets.clicked.connect(self.refresh_buckets)
        rowb.addWidget(QtWidgets.QLabel("Bucket")); rowb.addWidget(self.cb_bucket,1); rowb.addWidget(self.btn_buckets)
        v5.addLayout(rowb)
        self.tbl_b = QtWidgets.QTableWidget(); self.tbl_b.setColumnCount(4)
        self.tbl_b.setHorizontalHeaderLabels(["id","key","value_json","created_at"])
        self.tbl_b.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl_b.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        v5.addWidget(self.tbl_b,1)
        roww = QtWidgets.QHBoxLayout()
        self.ed_key = QtWidgets.QLineEdit(); self.ed_key.setPlaceholderText("key")
        self.ed_val = QtWidgets.QLineEdit(); self.ed_val.setPlaceholderText('value_json (e.g. {"foo":1})')
        self.btn_write = QtWidgets.QPushButton("Write"); self.btn_write.clicked.connect(self.bucket_write)
        roww.addWidget(self.ed_key,1); roww.addWidget(self.ed_val,2); roww.addWidget(self.btn_write)
        v5.addLayout(roww)
        d5.setWidget(w5); self.addDockWidget(QtCore.Qt.RightDockWidgetArea, d5)

        # Immune AI
        d6=QtWidgets.QDockWidget("Immune AI", self)
        self.immAI = ImmuneAI(self.db)
        d6.setWidget(self.immAI)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, d6)

    # ---------- Lifecycle ----------
    def ensure_cell1(self):
        c0=self.db.cell_get("cell_0"); c1=self.db.cell_get("cell_1")
        if c0 and not c1:
            self.db.cell_insert("cell_1", c0["code"], immutable=0, parent="cell_0", pos=(0,0), size=(800,800))
            self.db.log("immune_system","INFO","Spawned cell_1 from cell_0")

    def populate(self):
        self.scene.clear(); self.items={}; self.list.clear()
        rows=self.db.cells_all()
        for r in rows:
            name=r["name"]; self.list.addItem(name)
            w=self.make_widget(r); it=CellItem(name,w,GRID_SIZE); self.scene.addItem(it)
            meta=json.loads(r["metadata_json"] or "{}"); pos=meta.get("pos",{"x":0,"y":0}); it.setPos(pos.get("x",0),pos.get("y",0))
            self.items[name]=it
        self.refresh_tables(); self.refresh_buckets(); self.center_cell1()

    def make_widget(self, row):
        name=row["name"]; code=row["code"]; imm=bool(row["immutable"])
        try:
            mod=types.ModuleType("m"); exec(code, mod.__dict__)
            if hasattr(mod,"build_gui"):
                try: w=mod.build_gui(ANTApi(self.db,name))
                except Exception as e: self.db.log("immune_system","ERROR",f"build_gui({name}): {e}"); w=None
            else: w=None
        except Exception as e:
            self.db.log("immune_system","ERROR",f"compile {name}: {e}"); w=None
        if w is None:
            w=QtWidgets.QWidget(); v=QtWidgets.QVBoxLayout(w)
            t=QtWidgets.QLabel(f"{name}"+(" (immutable)" if imm else "")); t.setStyleSheet("font-weight:bold"); v.addWidget(t)
            v.addWidget(QtWidgets.QLabel("Default cell UI. Edit in Inspector."))
            v.addStretch(1)
        w.setMinimumSize(600,600); w.resize(800,800); return w

    # ---------- Buckets dock ----------
    def refresh_buckets(self):
        self.cb_bucket.blockSignals(True)
        self.cb_bucket.clear()
        names = self.db.list_buckets()
        if not names: self.cb_bucket.addItem("—")
        else: self.cb_bucket.addItems(names)
        self.cb_bucket.blockSignals(False)
        self.refresh_bucket_table()

    def refresh_bucket_table(self):
        name = self.cb_bucket.currentText().strip()
        if not name or name=="—":
            self.tbl_b.clearContents(); self.tbl_b.setRowCount(0); return
        rows = self.db.bucket_items(name, limit=200)
        self.tbl_b.setRowCount(len(rows))
        for r,row in enumerate(rows):
            self.tbl_b.setItem(r,0,QtWidgets.QTableWidgetItem(str(row["id"])))
            self.tbl_b.setItem(r,1,QtWidgets.QTableWidgetItem(row["key"]))
            self.tbl_b.setItem(r,2,QtWidgets.QTableWidgetItem(row["value_json"]))
            self.tbl_b.setItem(r,3,QtWidgets.QTableWidgetItem(row["created_at"] or ""))
        self.tbl_b.resizeColumnsToContents()

    def bucket_write(self):
        name = self.cb_bucket.currentText().strip()
        if not name or name=="—": 
            QtWidgets.QMessageBox.information(self,"Bucket","Choose a bucket first."); return
        key = self.ed_key.text().strip(); js = self.ed_val.text().strip()
        if not key or not js: return
        try:
            val=json.loads(js)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"JSON",f"Invalid JSON: {e}"); return
        self.db.bucket_write(name, key, val)
        self.refresh_bucket_table()

    # ---------- Toolbar actions ----------
    def center_cell1(self):
        it=self.items.get("cell_1"); self.view.centerOn(it if it else QtCore.QPointF(0,0))
    def toggle_grid(self): self.scene.show_grid=not self.scene.show_grid; self.scene.update()

    def on_sel(self):
        it=self.list.selectedItems()
        if not it: self.lbl.setText("—"); self.ed.setPlainText(""); self.b_save.setEnabled(False); self.b_rb.setEnabled(False); return
        name=it[0].text(); row=self.db.cell_get(name)
        self.lbl.setText(f"{name}  v{row['version']}  immutable={'yes' if row['immutable'] else 'no'}")
        self.ed.setPlainText(row["code"]); self.ed.setReadOnly(bool(row["immutable"]))
        self.b_save.setEnabled(not bool(row["immutable"])); self.b_rb.setEnabled(not bool(row["immutable"]))

    def save_code(self):
        it=self.list.selectedItems(); 
        if not it: return
        name=it[0].text(); code=self.ed.toPlainText()
        ok,msg=compile_ok(code)
        if not ok:
            QtWidgets.QMessageBox.warning(self,"Syntax",msg); return
        try:
            # diff for history
            cur = self.db.cell_get(name)["code"]
            d = unified_diff(cur, code, A=f"{name}@current", B="proposed")
            self.db.cell_update_code(name,code,diff_text=d)
            self.db.log("immune_system","INFO",f"Saved {name}")
            # also write a code_parts snapshot
            self.db.bucket_write("code_parts", f"{name}-snapshot-{int(time.time())}",
                                 {"cell":name,"segments":[{"kind":"other","name":"full","text": code}]})
            self.populate()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self,"Save error",str(e))

    def run_behavior(self):
        it=self.list.selectedItems(); 
        if not it: return
        name=it[0].text(); row=self.db.cell_get(name); code=row["code"]
        try:
            mod=types.ModuleType("m"); exec(code, mod.__dict__)
            if hasattr(mod,"core_behavior"):
                res=mod.core_behavior(ANTApi(self.db,name))
                QtWidgets.QMessageBox.information(self,"Result",str(res))
            else:
                QtWidgets.QMessageBox.information(self,"Result","No core_behavior(api) defined.")
        except Exception as e:
            tb=traceback.format_exc(); self.db.log(name,"ERROR",f"behavior: {e}")
            c=self.db.connect(); x=c.cursor()
            x.execute("INSERT INTO errors(cell_name,version,traceback,context_json) VALUES(?,?,?,?)",
                      (name,row["version"],tb,json.dumps({"action":"core_behavior"})))
            c.commit(); c.close()
            QtWidgets.QMessageBox.critical(self,"Behavior error",str(e))

    def rollback(self):
        it=self.list.selectedItems(); 
        if not it: return
        name=it[0].text()
        try:
            v=self.db.cell_rollback(name); self.db.log("immune_system","WARN",f"Rollback {name} -> v{v}"); self.populate()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"Rollback",str(e))

    def spawn_cell(self):
        name,ok=QtWidgets.QInputDialog.getText(self,"Spawn Cell","Name:")
        if not ok or not name.strip(): return
        name="".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name.strip())
        if self.db.cell_get(name): 
            QtWidgets.QMessageBox.warning(self,"Exists","Cell exists."); return
        c0=self.db.cell_get("cell_0"); code=c0["code"] if c0 else "def core_behavior(api):\n    return {'ok':True}\n"
        pos=self.free_pos(); self.db.cell_insert(name,code,immutable=0,parent="cell_0",pos=pos,size=(800,800))
        self.db.log("immune_system","INFO",f"Spawned {name}"); self.populate()

    def free_pos(self):
        occ=set()
        for it in self.items.values():
            p=it.pos(); gx=round(p.x()/GRID_SIZE); gy=round(p.y()/GRID_SIZE); occ.add((gx,gy))
        for r in range(0,40):
            for dx in range(-r,r+1):
                for dy in range(-r,r+1):
                    if (dx,dy) not in occ:
                        neigh=[(dx+1,dy),(dx-1,dy),(dx,dy+1),(dx,dy-1)]
                        if any(n in occ for n in neigh): continue
                        return (dx*GRID_SIZE, dy*GRID_SIZE)
        return (0,0)

    def merge_selected(self):
        sel=[i for i in self.scene.selectedItems() if isinstance(i,CellItem)]
        if len(sel)<2:
            QtWidgets.QMessageBox.information(self,"Merge","Select ≥2 cells."); return
        tabs=QtWidgets.QTabWidget()
        for it in sel:
            w=it.proxy.widget(); it.proxy.setWidget(None); self.scene.removeItem(it); self.items.pop(it.cell,None)
            tabs.addTab(w, it.cell)
        comp=CellItem("cluster",tabs,GRID_SIZE); self.scene.addItem(comp); comp.setPos(0,0); self.items["cluster"]=comp
        self.db.log("immune_system","INFO","Merged (visual)")
        self.populate()

    def unmerge_selected(self):
        sel=[i for i in self.scene.selectedItems() if isinstance(i,CellItem)]
        if len(sel)!=1: QtWidgets.QMessageBox.information(self,"Unmerge","Select the merged cluster."); return
        it=sel[0]; tabs=it.proxy.widget()
        if not isinstance(tabs,QtWidgets.QTabWidget): return
        base=it.pos()
        for idx in range(tabs.count()):
            w=tabs.widget(idx); name=tabs.tabText(idx)
            child=CellItem(name,w,GRID_SIZE); self.scene.addItem(child)
            child.setPos(base+QtCore.QPointF((idx+1)*GRID_SIZE*2,(idx%2)*GRID_SIZE*2)); self.items[name]=child
        it.proxy.setWidget(None); self.scene.removeItem(it); self.items.pop("cluster",None)
        self.db.log("immune_system","INFO","Unmerged"); self.populate()

    def inject_protein(self):
        dlg=QtWidgets.QDialog(self); dlg.setWindowTitle("Protein (broadcast)")
        v=QtWidgets.QVBoxLayout(dlg); ed=QtWidgets.QPlainTextEdit(); ed.setPlaceholderText("directive...")
        tgt=QtWidgets.QLineEdit(); tgt.setPlaceholderText("target cell (optional, blank=broadcast)")
        bb=QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        v.addWidget(ed); v.addWidget(tgt); v.addWidget(bb); bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        if dlg.exec_()==QtWidgets.QDialog.Accepted:
            text=ed.toPlainText().strip(); to=tgt.text().strip() or None
            if text: self.db.emit("immune_system","protein",{"text":text},to); self.db.log("immune_system","INFO",f"protein -> {to or 'broadcast'}")

    # ---------- Host Browser ----------
    def refresh_tables(self):
        try:
            c=self.db.connect(); x=c.cursor(); x.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            names=[r[0] for r in x.fetchall()]; c.close()
            self.tables.clear(); self.tables.addItems(names)
        except Exception as e:
            self.db.log("immune_system","ERROR",f"tables:{e}")

    def preview(self):
        t=self.tables.currentText().strip()
        if not t: return
        try:
            c=self.db.connect(); x=c.cursor()
            x.execute(f"PRAGMA table_info({t})"); cols=[r[1] for r in x.fetchall()]
            x.execute(f"SELECT * FROM {t} LIMIT 200"); data=x.fetchall(); c.close()
            self.fill_table(cols,data)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"Preview",str(e))

    def exec_select(self):
        sql=self.sql.toPlainText().strip()
        if not sql.lower().startswith("select"): 
            QtWidgets.QMessageBox.warning(self,"SQL","Read-only: SELECT only."); return
        try:
            c=self.db.connect(); x=c.cursor(); x.execute(sql+f" LIMIT {int(self.lim.value())}")
            cols=[d[0] for d in x.description]; data=x.fetchall(); c.close()
            self.fill_table(cols,data)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,"SQL",str(e))

    def fill_table(self,cols,rows):
        self.table.clear(); self.table.setColumnCount(len(cols)); self.table.setHorizontalHeaderLabels(cols)
        self.table.setRowCount(len(rows))
        for r,row in enumerate(rows):
            for c,val in enumerate(row): self.table.setItem(r,c,QtWidgets.QTableWidgetItem(str(val)))
        self.table.resizeColumnsToContents()

    # ---------- Maintenance ----------
    def tick(self):
        # save positions
        for name,it in list(self.items.items()):
            p=it.pos(); self._save_pos(name,int(p.x()),int(p.y()))
        self.refresh_logs()
        self.maintenance_pass()

    def _save_pos(self,name,x,y):
        r=self.db.cell_get(name); if not r: return
        meta=json.loads(r["metadata_json"] or "{}"); meta.setdefault("pos",{}); meta["pos"]["x"]=x; meta["pos"]["y"]=y
        c=self.db.connect(); xq=c.cursor(); xq.execute("UPDATE cells SET metadata_json=? WHERE name=?", (json.dumps(meta),name)); c.commit(); c.close()

    def refresh_logs(self):
        cell=self.f_cell.text().strip() or None; lev=self.f_level.currentText().strip() or None
        c=self.db.connect(); x=c.cursor()
        base="SELECT * FROM logs"; wh=[]; pr=[]
        if cell: wh.append("cell_name=?"); pr.append(cell)
        if lev: wh.append("level=?"); pr.append(lev)
        if wh: base+=" WHERE "+ " AND ".join(wh)
        base+=" ORDER BY id DESC LIMIT 1000"
        x.execute(base,pr); rows=x.fetchall(); c.close()
        cur=self.log.verticalScrollBar().value(); mx=self.log.verticalScrollBar().maximum(); at_bottom=cur>=mx-4
        txt="\n".join(f"[{r['created_at']}] {r['cell_name']} {r['level']}: {r['message']}" for r in reversed(rows))
        self.log.setPlainText(txt)
        if at_bottom: self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def maintenance_pass(self):
        """Correlate logs to diffs, write diff_notes, prune older logs."""
        try:
            c = self.db.connect(); x = c.cursor()
            # 1) figure last processed log id
            last = self.db.meta_get("logs_last_processed_id")
            last_id = int(last) if (last and last.isdigit()) else 0

            # 2) pull next batch of logs newer than last_id
            x.execute("SELECT id, cell_name, level, message, created_at FROM logs WHERE id>? ORDER BY id ASC LIMIT ?", (last_id, LOG_PROCESS_BATCH))
            logs = x.fetchall()

            # 3) correlate with diffs within recent window
            if logs:
                # recent diffs by cell
                x.execute("SELECT id, cell_name, from_version, to_version, created_at FROM diffs WHERE (strftime('%s','now') - strftime('%s',created_at)) < ? ORDER BY id DESC", (DIFF_RECENT_SECONDS,))
                diffs = x.fetchall()
                diffs_by_cell = {}
                for d in diffs:
                    diffs_by_cell.setdefault(d["cell_name"], []).append(d)

                # ensure diff_notes bucket exists
                x.execute("INSERT OR IGNORE INTO buckets(name,purpose,schema_json,mutable) VALUES(?,?,?,1)",
                          ("diff_notes","Short notes tying logs to diffs", json.dumps({"type":"object"})))

                for L in logs:
                    cell = L["cell_name"] or ""
                    if "save" in (L["message"] or "").lower() or "update" in (L["message"] or "").lower():
                        ds = diffs_by_cell.get(cell, [])
                        if ds:
                            d0 = ds[0]
                            note = {"cell": cell, "log": {"id": L["id"], "msg": L["message"], "at": L["created_at"]},
                                    "diff": {"id": d0["id"], "from": d0["from_version"], "to": d0["to_version"], "at": d0["created_at"]}}
                            x.execute("INSERT OR REPLACE INTO bucket_items(bucket_name,key,value_json) VALUES('diff_notes',?,?)",
                                      (f"{cell}-log{L['id']}-diff{d0['id']}", json.dumps(note)))
                # bump last processed
                last_id = logs[-1]["id"]
                self.db.meta_set("logs_last_processed_id", str(last_id))

            # 4) release old logs beyond retention
            x.execute("SELECT COUNT(*) FROM logs"); total=x.fetchone()[0]
            if total > LOG_RETAIN_MAX:
                # delete oldest rows beyond retention
                to_remove = total - LOG_RETAIN_MAX
                x.execute("DELETE FROM logs WHERE id IN (SELECT id FROM logs ORDER BY id ASC LIMIT ?)", (to_remove,))
            c.commit()
        except Exception as e:
            # non-fatal
            self.db.log("immune_system","ERROR",f"maintenance: {e}")
        finally:
            try: c.close()
            except: pass

# ==========================
# Entrypoint
# ==========================

def main():
    # Ensure QApplication before any dialogs
    app=QtWidgets.QApplication(sys.argv)
    # dark retro
    pal=QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window,QtGui.QColor(18,18,18))
    pal.setColor(QtGui.QPalette.WindowText,QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Base,QtGui.QColor(12,12,12))
    pal.setColor(QtGui.QPalette.Text,QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Button,QtGui.QColor(24,24,24))
    pal.setColor(QtGui.QPalette.ButtonText,QtCore.Qt.white)
    pal.setColor(QtGui.QPalette.Highlight,QtGui.QColor(60,180,120))
    pal.setColor(QtGui.QPalette.HighlightedText,QtCore.Qt.black)
    app.setPalette(pal); app.setStyle("Fusion")

    # Resolve DB path
    dbp=os.environ.get("SINGLECELL_DB") or (len(sys.argv)>1 and sys.argv[1]) or ""
    if not dbp:
        QtWidgets.QMessageBox.critical(None,"DB required","Set SINGLECELL_DB or pass path as argv[1].")
        sys.exit(2)

    db=DB(dbp); db.ensure()
    ui=UI(db); ui.show()
    sys.exit(app.exec_())

if __name__=="__main__": 
    main()
```

