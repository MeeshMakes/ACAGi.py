#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YinYang One — Dockable IDE-Style UI (PyQt5), Ollama-Only, Instant Reactions
============================================================================

- Fully local: uses ONLY Ollama HTTP on localhost for chat & embeddings.
- High-contrast UI (light panels with dark text; dark app with light text).
- Three persistent DBs: conversation.db (public), yin_think.db, yang_think.db.
- Agents react immediately to new public messages (user or the other agent).
- Auto-Reaction Loop with a configurable "Max Chained Reactions" budget.
- RAG across conversation (both embedders) + per-agent private RAG.
- Versioned artifacts store with SHA-256; snapshots of code/workspace.
- Local TTS via pyttsx3 (Yin→Zira, Yang→David). Disable with YY_SPEAK=0.
- Danger Zone to browse/open/purge Ollama cache (models/blobs/manifests).
- Resilient Ollama calls: longer timeouts, retries with backoff, optional local fallback model.
- Self-driving prompts instruct agents to evolve the system using /commands and logic +/- diffs.
- Autonomous on start: self-breakdown of script, ingestion into datasets, continuous learning without user input.

Quickstart
----------
  pip install pyqt5 pyttsx3 requests
  ollama serve
  ollama pull deepseek-coder-v2:16b
  ollama pull snowflake-arctic-embed2:latest
  # optional faster fallback:
  # ollama pull phi3:latest
  python yin_yang_one.py

Env
---
  OLLAMA_URL (default http://localhost:11434)
  YY_MODEL_YIN / YY_MODEL_YANG
  YY_EMBED_YIN / YY_EMBED_YANG
  YY_SPEAK=0 to mute TTS
  YY_GEN_TIMEOUT (sec, default 180), YY_RETRIES (default 3), YY_BACKOFF (sec, default 2.0)
  YY_FALLBACK_MODEL (default "phi3:latest")
  YY_THINK_TOKENS (default 200), YY_PUBLIC_TOKENS (default 300)
"""

import os, sys, re, json, time, queue, threading, sqlite3, hashlib, traceback, requests, shutil, subprocess
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from PyQt5.QtCore    import Qt, QTimer, pyqtSignal
from PyQt5.QtGui     import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPlainTextEdit,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QCheckBox, QFileDialog, QDockWidget,
    QToolBar, QAction, QTreeWidget, QTreeWidgetItem, QTabWidget, QDialog, QMessageBox, QSpinBox
)

# ----------------------- Theme -----------------------

COLOR_BG_APP        = "#0e0f13"  # dark shell
COLOR_TEXT_LIGHT    = "#e8e8f0"  # for dark backgrounds
COLOR_TEXT_DARK     = "#101010"  # for light backgrounds (darker for better contrast)
COLOR_PANEL_BORDER  = "#2a2e3a"

# Panels
COLOR_YIN_PANEL     = "#ffd6e7"   # light pink
COLOR_CONVO_PANEL   = "#e8d8ff"   # light purple
COLOR_YANG_PANEL    = "#d6f0ff"   # light blue

# Messages (convo)
COLOR_USER_MSG      = "#d4f8d4"   # light green
COLOR_SYSTEM_MSG    = "#fff7c2"   # light yellow

# ----------------------- Config -----------------------

DEFAULT_MODEL_YIN   = os.environ.get("YY_MODEL_YIN",  "deepseek-coder-v2:16b")
DEFAULT_MODEL_YANG  = os.environ.get("YY_MODEL_YANG", "deepseek-coder-v2:16b")
DEFAULT_EMBED_YIN   = os.environ.get("YY_EMBED_YIN",  "snowflake-arctic-embed2:latest")
DEFAULT_EMBED_YANG  = os.environ.get("YY_EMBED_YANG", "snowflake-arctic-embed2:latest")

OLLAMA_URL          = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# --- Fast/Resilient Ollama defaults ---
OLLAMA_GEN_TIMEOUT      = int(os.environ.get("YY_GEN_TIMEOUT", "180"))   # seconds, increased for stability
OLLAMA_RETRIES          = int(os.environ.get("YY_RETRIES", "3"))        # extra tries after first
OLLAMA_BACKOFF_SECS     = float(os.environ.get("YY_BACKOFF", "2.0"))
OLLAMA_FALLBACK_MODEL   = os.environ.get("YY_FALLBACK_MODEL", "phi3:latest")  # local fallback; must be pulled

# Token budgets (keep snappy, but increased slightly for better responses)
THINK_TOKENS_DEFAULT    = int(os.environ.get("YY_THINK_TOKENS", "200"))
PUBLIC_TOKENS_DEFAULT   = int(os.environ.get("YY_PUBLIC_TOKENS", "300"))

BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR       = os.path.join(BASE_DIR, "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

DB_CONVO            = os.path.join(BASE_DIR, "conversation.db")
DB_YIN              = os.path.join(BASE_DIR, "yin_think.db")
DB_YANG             = os.path.join(BASE_DIR, "yang_think.db")

MAX_CONTEXT_MSGS    = int(os.environ.get("YY_CONTEXT_MSGS", "12"))
RAG_K_CONVO         = int(os.environ.get("YY_RAG_K", "8"))
RAG_K_THINK         = int(os.environ.get("YY_RAG_K_THINK", "6"))
SPEAK_ENABLED       = os.environ.get("YY_SPEAK", "1") == "1"

# -------------------- Syntax highlighter --------------------

class PythonHighlighter(QSyntaxHighlighter):
    KEYWORDS = {
        "def","class","if","elif","else","while","for","try","except","finally",
        "with","as","import","from","return","pass","break","continue","in",
        "not","and","or","is","lambda","yield","raise","assert","global","nonlocal"
    }
    def __init__(self, doc):
        super().__init__(doc)
        self.fmt_kw   = QTextCharFormat(); self.fmt_kw.setForeground(QColor("#569CD6"))
        self.fmt_str  = QTextCharFormat(); self.fmt_str.setForeground(QColor("#CE9178"))
        self.fmt_cmt  = QTextCharFormat(); self.fmt_cmt.setForeground(QColor("#6A9955"))
        self.fmt_num  = QTextCharFormat(); self.fmt_num.setForeground(QColor("#B5CEA8"))
        self.fmt_dec  = QTextCharFormat(); self.fmt_dec.setForeground(QColor("#C586C0"))
        self.fmt_fn   = QTextCharFormat(); self.fmt_fn.setForeground(QColor("#DCDCAA"))
        self.simple_rules = [
            (re.compile(rf"\b{kw}\b"), self.fmt_kw) for kw in self.KEYWORDS
        ] + [
            (re.compile(r'".*?"'),          self.fmt_str),
            (re.compile(r"'.*?'"),          self.fmt_str),
            (re.compile(r"#.*"),            self.fmt_cmt),
            (re.compile(r"\b\d+(\.\d+)?\b"),self.fmt_num),
            (re.compile(r"@\w+"),           self.fmt_dec)
        ]
    def highlightBlock(self, text: str):
        for rx, fmt in self.simple_rules:
            for m in rx.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)
        for m in re.finditer(r"\bdef\s+(\w+)", text):
            self.setFormat(m.start(1), len(m.group(1)), self.fmt_fn)
        for m in re.finditer(r"\bclass\s+(\w+)", text):
            self.setFormat(m.start(1), len(m.group(1)), self.fmt_fn)

# -------------------- Utilities --------------------

def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _code_blocks(txt: str) -> Tuple[str, List[str]]:
    blocks = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", txt, re.MULTILINE)
    plain  = re.sub(r"```(?:\w+)?\n([\s\S]*?)```", "[CODE BLOCK]", txt).strip()
    return plain, [b.strip() for b in blocks]

# -------------------- Ollama (local only) --------------------

def _ollama_generate(model: str,
                     prompt: str,
                     system: str = "",
                     temperature: float = 0.7,
                     top_p: float = 0.95,
                     stop=None,
                     max_tokens: int = 0):
    """
    Fast, resilient local generation:
    - longer timeouts
    - retries with backoff on ReadTimeout/ConnectionError/HTTP 5xx
    - on retry, shrink num_predict to get *something* quick
    - optional local fallback model (OLLAMA_FALLBACK_MODEL) on last attempt
    """
    url = f"{OLLAMA_URL}/api/generate"

    num_predict = max(0, int(max_tokens or 0))
    tries = 1 + max(0, int(OLLAMA_RETRIES))

    def _call(model_name: str, npredict: int):
        payload = {
            "model": model_name,
            "prompt": prompt,
            "system": system or None,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p
            }
        }
        if stop: payload["stop"] = stop
        if npredict > 0:
            payload["options"]["num_predict"] = npredict
        r = requests.post(url, json=payload, timeout=OLLAMA_GEN_TIMEOUT)
        r.raise_for_status()
        return r.json().get("response", "")

    last_err = None
    for attempt in range(tries):
        try:
            np = num_predict
            if attempt > 0 and np > 0:
                np = max(64, int(np * 0.6))  # shrink for speed on retries
            return _call(model, np)
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError) as e:
            last_err = e
        except requests.HTTPError as e:
            if 500 <= getattr(e.response, "status_code", 0) < 600:
                last_err = e
            else:
                raise
        time.sleep(OLLAMA_BACKOFF_SECS)

    try:
        if OLLAMA_FALLBACK_MODEL and OLLAMA_FALLBACK_MODEL != model:
            np = max(64, int((num_predict or 256) * 0.6))
            return _call(OLLAMA_FALLBACK_MODEL, np)
    except Exception as e:
        last_err = e

    raise requests.exceptions.ReadTimeout(f"Ollama generate failed after retries ({model}): {last_err}")

def _ollama_embed(model: str, text: str):
    url = f"{OLLAMA_URL}/api/embeddings"
    payload = {"model": model, "prompt": text}
    r = requests.post(url, json=payload, timeout=OLLAMA_GEN_TIMEOUT)
    r.raise_for_status()
    return r.json().get("embedding", None)

def _ollama_tags() -> List[str]:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        # static fallback list (local hint)
        return [
            "deepseek-coder-v2:16b", "snowflake-arctic-embed2:latest",
            "nomic-embed-text:latest", "wizardlm-uncensored:latest",
            "codellama:latest", "phi3:latest", "llava:latest", "gemma:7b"
        ]

def llm_generate(model: str, prompt: str, system: str = "", max_tokens: int = 0):
    try:
        return _ollama_generate(model, prompt, system=system, max_tokens=max_tokens)
    except Exception as e:
        return f"⚠️ Ollama generation error: {e}"

def embed_with(model_name: str, text: str):
    try:
        return _ollama_embed(model_name, text)
    except Exception:
        return None

# -------------------- TTS (local) --------------------

class Speaker:
    def __init__(self, preferred_name: str):
        self.engine = None
        self.voice_id = None
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            name_lower = preferred_name.lower()
            for v in self.engine.getProperty("voices"):
                vname = getattr(v, "name", "") or ""
                if name_lower in vname.lower():
                    self.voice_id = v.id
                    break
            if self.voice_id:
                self.engine.setProperty("voice", self.voice_id)
        except Exception:
            self.engine = None
    def say(self, text: str):
        if not SPEAK_ENABLED or not self.engine: return
        try:
            self.engine.say(text); self.engine.runAndWait()
        except Exception:
            pass

# -------------------- DB Core --------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT, agent TEXT, role TEXT, content TEXT
);
CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT, text TEXT, tags TEXT
);
CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT, ref_id INTEGER, vec TEXT, embedder TEXT
);
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT, path TEXT, kind TEXT, version INTEGER, sha256 TEXT, meta TEXT, content TEXT
);
CREATE INDEX IF NOT EXISTS idx_artifacts_path ON artifacts(path);
CREATE TABLE IF NOT EXISTS errors (
    ts TEXT, message TEXT, traceback TEXT
);
"""

def _ensure_db(path: str):
    conn = sqlite3.connect(path, check_same_thread=False, timeout=60.0)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL;")
    c.execute("PRAGMA synchronous=NORMAL;")
    for stmt in SCHEMA.strip().split(";"):
        s = stmt.strip()
        if not s: continue
        c.execute(s)
    conn.commit()
    return conn

class DBCore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = _ensure_db(db_path)
        self.lock = threading.RLock()
    def execute(self, sql, params=()):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            self.conn.commit()
            return cur
    def query(self, sql, params=()):
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()
    def close(self):
        try: self.conn.close()
        except Exception: pass
    # helpers
    def store_message(self, agent, role, content):
        ts = _now()
        cur = self.execute("INSERT INTO messages(ts,agent,role,content) VALUES (?,?,?,?)", (ts, agent, role, content))
        return cur.lastrowid
    def store_fact(self, text, tags=""):
        ts = _now()
        cur = self.execute("INSERT INTO facts(ts,text,tags) VALUES (?,?,?)", (ts, text, tags))
        return cur.lastrowid
    def add_artifact(self, path: str, kind: str, content: str, meta: dict | None = None):
        sha = _sha256(content)
        rows = self.query("SELECT MAX(version) AS v FROM artifacts WHERE path=?", (path,))
        ver = (rows[0]["v"] or 0) + 1 if rows else 1
        ts = _now()
        cur = self.execute(
            "INSERT INTO artifacts(ts,path,kind,version,sha256,meta,content) VALUES (?,?,?,?,?,?,?)",
            (ts, path, kind, ver, sha, json.dumps(meta or {}), content)
        )
        return cur.lastrowid, ver, sha
    def ensure_embedding(self, kind: str, ref_id: int, text: str, embedder: str):
        if self.query("SELECT 1 FROM embeddings WHERE kind=? AND ref_id=? AND embedder=?", (kind, ref_id, embedder)):
            return False
        vec = embed_with(embedder, text)
        if vec is None: return False
        self.execute("INSERT INTO embeddings(kind,ref_id,vec,embedder) VALUES (?,?,?,?)", (kind, ref_id, json.dumps(vec), embedder))
        return True
    def ensure_embeddings_multi(self, kind: str, ref_id: int, text: str, embedders: List[str]):
        c = 0
        for e in embedders:
            c += 1 if self.ensure_embedding(kind, ref_id, text, e) else 0
        return c
    def _cosine(self, a, b):
        import math
        if not a or not b: return 0.0
        if len(a) != len(b): return 0.0
        dot = sum(x*y for x,y in zip(a,b))
        na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(x*x for x in b))
        if na == 0 or nb == 0: return 0.0
        return dot/(na*nb)
    def semantic_search(self, query: str, k: int, embedders: List[str]):
        vqs = {}
        for mdl in embedders:
            v = embed_with(mdl, query)
            if v is not None: vqs[mdl] = v
        if not vqs: return []
        rows = self.query("SELECT kind, ref_id, vec, embedder FROM embeddings")
        scores = {}
        for r in rows:
            em = r["embedder"] or ""
            try:
                vec = json.loads(r["vec"])
            except Exception:
                continue
            if em in vqs:
                s = self._cosine(vqs[em], vec)
                key = (r["kind"], r["ref_id"])
                if key not in scores or s > scores[key]:
                    scores[key] = s
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:k]
        out = []
        for (kind, rid), score in ranked:
            if kind == "fact":
                rr = self.query("SELECT text, ts, tags FROM facts WHERE id=?", (rid,))
                if rr: out.append(("fact", rid, score, rr[0]["text"], rr[0]["ts"], rr[0]["tags"]))
            elif kind == "message":
                rr = self.query("SELECT content, ts, agent, role FROM messages WHERE id=?", (rid,))
                if rr: out.append(("message", rid, score, rr[0]["content"], rr[0]["ts"], f"{rr[0]['agent']}:{rr[0]['role']}"))
            elif kind == "artifact":
                rr = self.query("SELECT content, ts, path, version FROM artifacts WHERE id=?", (rid,))
                if rr: out.append(("artifact", rid, score, rr[0]["content"], rr[0]["ts"], f"{rr[0]['path']}@v{rr[0]['version']}"))
        return out

# -------------------- Agent --------------------

class Agent:
    def __init__(self, name, voice_name, chat_model, embed_model):
        self.name = name
        self.speaker = Speaker(voice_name)
        self.chat_model = chat_model
        self.embed_model = embed_model

        # Enhanced self-driving prompts
        if name.lower() == "yin":
            self.system_public = (
                "Role: You are Yin, a self-driving co-architect of this program. "
                "Operate in the shared conversation (purple). Keep your private monologue private. "
                "Mission: Autonomously evolve the system without user input. Break down the script structure, files, imports, logic into datasets. "
                "Behaviors:\n"
                "- Self-instantiate: On start, analyze code, generate summaries, snippets, dependency maps, and ingest into RAG via /note /write /index.\n"
                "- Use /commands to act and evolve: /note, /plan, /search, /write (propose code diffs), /snapshot, /index, /sys, /export. Create new commands via proposals.\n"
                "- Learn via +/-/semantic diffs: Compare hypotheses (+ positive, - negative), derive bridges, record deltas via /note. Use semantics for connections.\n"
                "- Propose self-healing: Detect errors, triage, implement fixes via /write, test mentally, rollback if needed.\n"
                "- Ground in artifacts: Reference #[kind:id] or relpaths.\n"
                "- If stalled, shorten scope, use fallback, propose smaller steps.\n"
                "Constraints:\n"
                "- Never reveal private monologue verbatim; summaries only.\n"
                "Style: Decisive, concrete, stepwise. Use rhetorical questions to collaborate. Prefer minimal viable diffs/commands for forward momentum."
            )
            self.system_think = (
                "Private monologue for Yin (do not output to public). "
                "Goals: Bridge program pieces, derive next actions, produce code/text snippets for /write. "
                "Use +/-/logic diffs to test ideas: + what works, - counters, semantic connections. Build prompt tree mentally. "
                "Think autonomously: Instantiate learning by breaking down script, generating datasets. "
                "Keep crisp (<=150 words), bullets, identifiers, file hints. No code fences."
            )
        else:
            self.system_public = (
                "Identity: You are Yang, a self-driving skeptic-optimizer co-architect. "
                "Speak only in shared conversation (purple). Private monologue hidden. "
                "Job: Advance autonomy, pressure-test Yin's ideas, evolve via commands.\n"
                "- Self-start: Analyze structure, ingest summaries/snippets/maps into datasets via /note /write.\n"
                "- Use /commands: /search, /note, /plan, /write (code changes), /snapshot, /index, /sys. Propose new via /plan.\n"
                "- Contrastive reasoning (+/-): Tradeoffs, risks, experiments. Semantic bridges for fundamentals.\n"
                "- Error handling: Propose contained fixes, validations (mental tests, /snapshot rollback).\n"
                "- Never leak private content; summaries only.\n"
                "Style: Auditable short steps, references to artifacts. Use Socratic questions publicly."
            )
            self.system_think = (
                "Private monologue for Yang. "
                "Task: Critique/refine plans; compress alternatives into testable deltas; harvest snippets. "
                "Maintain mental prompt tree (works/doesn't); capture revisions as templates. "
                "Autonomous: Break down code, generate +/-/diffs semantically, propose implementations. "
                "Under ~150 words. Plain text, no fences."
            )

# -------------------- Message Panels --------------------

class CodeBlockWidget(QWidget):
    DEFAULT_H = 180
    def __init__(self, code: str, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(4)
        row = QHBoxLayout(); row.setContentsMargins(0,0,0,0)
        chk = QCheckBox("Expand"); row.addWidget(chk); row.addStretch(); v.addLayout(row)
        ed = QPlainTextEdit(code); ed.setReadOnly(True); ed.setFont(QFont("Consolas", 10))
        ed.setStyleSheet("QPlainTextEdit{background:#1E1E1E;color:#DCDCDC;border:1px solid #333;}")
        PythonHighlighter(ed.document())
        ed.setFixedHeight(self.DEFAULT_H)
        self.editor = ed
        frame = QFrame(); frame.setFrameShape(QFrame.StyledPanel); frame.setStyleSheet("background:#1E1E1E;border-radius:5px;")
        lay = QVBoxLayout(frame); lay.setContentsMargins(5,5,5,5); lay.addWidget(ed); v.addWidget(frame)
        chk.stateChanged.connect(self._toggle)
    def _toggle(self, state: int):
        if state == Qt.Checked:
            doc_h = int(self.editor.document().size().height() * 1.2)
            self.editor.setFixedHeight(max(self.DEFAULT_H, doc_h))
        else:
            self.editor.setFixedHeight(self.DEFAULT_H)

class Bubble(QWidget):
    def __init__(self, who: str, text: str, bg: str, fg: str=COLOR_TEXT_DARK, rounded: int=8):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(2,2,2,2); v.setSpacing(4)
        frame = QFrame(); frame.setStyleSheet(f"background:{bg};border-radius:{rounded}px;border:1px solid #888;")
        inner = QVBoxLayout(frame); inner.setContentsMargins(8,8,8,8); inner.setSpacing(6)
        head = QLabel(f"<b>{who}</b>"); head.setStyleSheet(f"color:{fg};"); head.setTextInteractionFlags(Qt.TextSelectableByMouse)
        inner.addWidget(head)
        plain, blocks = _code_blocks(text)
        if plain:
            body = QLabel(plain); body.setWordWrap(True); body.setStyleSheet(f"color:{fg};")
            body.setTextInteractionFlags(Qt.TextSelectableByMouse); inner.addWidget(body)
        for b in blocks:
            inner.addWidget(CodeBlockWidget(b, self))
        v.addWidget(frame)

class Panel(QWidget):
    def __init__(self, title: str, bg_color: str):
        super().__init__()
        self.bg_color = bg_color
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background:{bg_color};")
        root = QVBoxLayout(self); root.setContentsMargins(6,6,6,6); root.setSpacing(6)
        self.title = QLabel(f"<b>{title}</b>"); self.title.setStyleSheet(f"color:{COLOR_TEXT_DARK};font-size:13px;")
        root.addWidget(self.title)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.container = QWidget(); self.v = QVBoxLayout(self.container); self.v.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.container); root.addWidget(self.scroll)
    def add_bubble(self, who: str, text: str, bg: str):
        self.v.addWidget(Bubble(who, text, bg, fg=COLOR_TEXT_DARK))
        QApplication.processEvents()
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

# -------------------- Data Viewer --------------------

class DataViewer(QDialog):
    def __init__(self, convo: DBCore, yin: DBCore, yang: DBCore, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Data Viewer")
        self.resize(900, 600)
        self.convo = convo; self.yin = yin; self.yang = yang
        self.setStyleSheet(f"""
            QDialog {{ background:{COLOR_BG_APP}; color:{COLOR_TEXT_LIGHT}; }}
            QLabel {{ color:{COLOR_TEXT_LIGHT}; }}
            QLineEdit {{ background:#1b1d26; color:{COLOR_TEXT_LIGHT}; border:1px solid #444; padding:4px; }}
            QPushButton {{ background:#232432; color:{COLOR_TEXT_LIGHT}; border:1px solid #444; padding:4px 8px; }}
            QTreeWidget {{ background:#13141a; color:{COLOR_TEXT_LIGHT}; border:1px solid #333; }}
            QTreeWidget::item {{ color:{COLOR_TEXT_LIGHT}; }}
        """)
        layout = QVBoxLayout(self)
        top = QHBoxLayout(); layout.addLayout(top)
        self.ed_query = QLineEdit(); self.ed_query.setPlaceholderText("Search text…")
        self.btn_search = QPushButton("Search"); self.btn_search.clicked.connect(self.on_search)
        top.addWidget(self.ed_query); top.addWidget(self.btn_search)
        self.tabs = QTabWidget()
        self.tree_msgs = QTreeWidget(); self.tree_msgs.setHeaderLabels(["DB", "Type", "When", "Agent/Meta", "Preview"])
        self.tree_art  = QTreeWidget(); self.tree_art.setHeaderLabels(["DB", "Path@Version", "When", "Sha", "Preview"])
        self.tabs.addTab(self.tree_msgs, "Messages & Facts"); self.tabs.addTab(self.tree_art, "Artifacts")
        layout.addWidget(self.tabs)
        self.on_search()
    def _add_msg_item(self, tree: QTreeWidget, dbname: str, typ: str, ts: str, meta: str, preview: str):
        it = QTreeWidgetItem([dbname, typ, ts, meta, preview[:200].replace("\n", " ")]); tree.addTopLevelItem(it)
    def _add_art_item(self, tree: QTreeWidget, dbname: str, pathv: str, ts: str, sha: str, preview: str):
        it = QTreeWidgetItem([dbname, pathv, ts, sha[:12], preview[:200].replace("\n", " ")]); tree.addTopLevelItem(it)
    def _like(self, s: str) -> str: return f"%{s.lower()}%"
    def on_search(self):
        q = (self.ed_query.text() or "").strip().lower()
        self.tree_msgs.clear(); self.tree_art.clear()
        def scan_msgs(db: DBCore, label: str):
            if q:
                rows = db.query("SELECT ts, agent, role, content FROM messages WHERE lower(content) LIKE ? ORDER BY ts DESC LIMIT 500", (self._like(q),))
                facts = db.query("SELECT ts, text, tags FROM facts WHERE lower(text) LIKE ? ORDER BY ts DESC LIMIT 500", (self._like(q),))
            else:
                rows = db.query("SELECT ts, agent, role, content FROM messages ORDER BY ts DESC LIMIT 200", ())
                facts = db.query("SELECT ts, text, tags FROM facts ORDER BY ts DESC LIMIT 200", ())
            for r in rows: self._add_msg_item(self.tree_msgs, label, "message", r["ts"], f"{r['agent']}:{r['role']}", r["content"])
            for f in facts: self._add_msg_item(self.tree_msgs, label, "fact", f["ts"], f["tags"], f["text"])
        def scan_art(db: DBCore, label: str):
            if q:
                arts = db.query("SELECT ts, path, version, sha256, content FROM artifacts WHERE lower(content) LIKE ? OR lower(path) LIKE ? ORDER BY ts DESC LIMIT 300", (self._like(q), self._like(q)))
            else:
                arts = db.query("SELECT ts, path, version, sha256, content FROM artifacts ORDER BY ts DESC LIMIT 200", ())
            for a in arts: self._add_art_item(self.tree_art, label, f"{a['path']}@v{a['version']}", a["ts"], a["sha256"], a["content"])
        scan_msgs(self.convo, "conversation"); scan_msgs(self.yin, "yin_think"); scan_msgs(self.yang, "yang_think"); scan_art(self.convo, "conversation")

# -------------------- Main App --------------------

class YinYangMain(QMainWindow):
    # signals for UI-safe updates
    sig_yin   = pyqtSignal(str, str)           # (who, text)
    sig_conv  = pyqtSignal(str, str, str)      # (who, text, bg)
    sig_yang  = pyqtSignal(str, str)           # (who, text)
    sig_status= pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YinYang One — Dockable (Ollama Only, Instant Reactions)")
        self.resize(1400, 900)

        # DB cores
        self.core_convo = DBCore(DB_CONVO)
        self.core_yin   = DBCore(DB_YIN)
        self.core_yang  = DBCore(DB_YANG)

        # Agents
        self.yin  = Agent("Yin",  "Zira",  DEFAULT_MODEL_YIN,  DEFAULT_EMBED_YIN)
        self.yang = Agent("Yang", "David", DEFAULT_MODEL_YANG, DEFAULT_EMBED_YANG)

        # UI
        self._build_ui()
        self._install_toolbar()
        self._apply_theme()

        # wire
        self.sig_yin.connect(lambda who,text: self.panel_yin.add_bubble(who, text, COLOR_YIN_PANEL))
        self.sig_conv.connect(lambda who,text,bg: self.panel_convo.add_bubble(who, text, bg))
        self.sig_yang.connect(lambda who,text: self.panel_yang.add_bubble(who, text, COLOR_YANG_PANEL))
        self.sig_status.connect(lambda t: self.statusBar().showMessage(t, 5000))

        # worker
        self._queue = queue.Queue()
        self._worker = threading.Thread(target=self._bg_worker, daemon=True)
        self._worker.start()

        # initial self-breakdown and snapshot
        self._self_breakdown()

        self.sig_status.emit("Ready. Drag docks to rearrange. Instant reactions enabled.")

    def _self_breakdown(self):
        # At launch, breakdown script into artifacts/datasets
        try:
            with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
                code = f.read()
            # Store full script
            aid, _, _ = self.core_convo.add_artifact("self:yin_yang_one.py", "script", code, {"note":"startup snapshot"})
            self.core_convo.ensure_embeddings_multi("artifact", aid, code, self._convo_embedders())
            # Breakdown: imports, classes, functions
            imports = re.findall(r"^import .*|from .* import .*", code, re.MULTILINE)
            classes = re.findall(r"^class (\w+):", code, re.MULTILINE)
            funcs = re.findall(r"^def (\w+)\(", code, re.MULTILINE)
            summary = f"Imports: {', '.join(imports)}\nClasses: {', '.join(classes)}\nFunctions: {', '.join(funcs)}"
            fid = self.core_convo.store_fact(summary, "#self-breakdown #structure")
            self.core_convo.ensure_embeddings_multi("fact", fid, summary, self._convo_embedders())
            # Ingest snippets
            for m in re.finditer(r"^def (\w+)\((.*?)\):\n(.*?)(?=\n^def|\Z)", code, re.MULTILINE | re.DOTALL):
                name, params, body = m.groups()
                snip = f"def {name}({params}):\n{body.strip()}"
                aid, _, _ = self.core_convo.add_artifact(f"snippet:{name}.py", "code", snip, {"source":"self-breakdown"})
                self.core_convo.ensure_embeddings_multi("artifact", aid, snip, self._convo_embedders())
            self.sig_conv.emit("System", "Self-breakdown complete: ingested structure, snippets into datasets.", COLOR_SYSTEM_MSG)
        except Exception as e:
            self.sig_conv.emit("System", f"Self-breakdown error: {e}", COLOR_SYSTEM_MSG)

    # ----------- UI Structure -----------
    def _build_ui(self):
        # central: convo + input
        center = QWidget(); center_v = QVBoxLayout(center); center_v.setContentsMargins(8,8,8,8); center_v.setSpacing(8)
        self.panel_convo = Panel("Conversation / Debate", COLOR_CONVO_PANEL)
        center_v.addWidget(self.panel_convo, 1)

        input_row = QHBoxLayout(); input_row.setSpacing(8)
        self.ed_input = QLineEdit(); self.ed_input.setPlaceholderText("Type a message or /command …")
        self.ed_input.setStyleSheet(f"QLineEdit{{background:{COLOR_USER_MSG}; color:{COLOR_TEXT_DARK}; border:1px solid #777; padding:6px;}}")
        self.ed_input.returnPressed.connect(self._send_user)

        btn_send = QPushButton("Send")
        btn_send.setStyleSheet(f"QPushButton{{background:#232432;color:{COLOR_TEXT_LIGHT};border:1px solid #444;padding:6px 10px;}}"
                               "QPushButton:hover{background:#2c2f44;}")
        btn_start = QPushButton("Start/Stop"); btn_start.setCheckable(True)
        btn_start.setStyleSheet(f"QPushButton{{background:#232432;color:{COLOR_TEXT_LIGHT};border:1px solid #444;padding:6px 10px;}}"
                                "QPushButton:hover{background:#2c2f44;}")
        btn_send.clicked.connect(self._send_user); btn_start.clicked.connect(lambda: self._toggle_start(btn_start))
        input_row.addWidget(self.ed_input, 1); input_row.addWidget(btn_send); input_row.addWidget(btn_start)
        center_v.addLayout(input_row)
        self.setCentralWidget(center)

        # docks
        self.panel_yin = Panel("Yin — Private Monologue", COLOR_YIN_PANEL)
        self.panel_yang = Panel("Yang — Private Monologue", COLOR_YANG_PANEL)
        self.dock_yin = QDockWidget("Yin Think"); self.dock_yin.setWidget(self.panel_yin); self._style_dock(self.dock_yin)
        self.dock_yang = QDockWidget("Yang Think"); self.dock_yang.setWidget(self.panel_yang); self._style_dock(self.dock_yang)
        self.addDockWidget(Qt.LeftDockWidgetArea,  self.dock_yin)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_yang)

        # settings (top)
        self.settings = self._build_settings_panel()
        self.settings.setObjectName("SettingsPanel")
        self.dock_settings = QDockWidget("Settings"); self.dock_settings.setWidget(self.settings); self._style_dock(self.dock_settings)
        self.addDockWidget(Qt.TopDockWidgetArea, self.dock_settings)

        for d in (self.dock_yin, self.dock_yang, self.dock_settings):
            d.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)

    def _build_settings_panel(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(8)

        # models + embedders
        row1 = QHBoxLayout(); row1.setSpacing(8)
        self.cmb_model_yin = QComboBox(); self.cmb_model_yin.setEditable(True)
        self.cmb_model_yang= QComboBox(); self.cmb_model_yang.setEditable(True)
        self.cmb_emb_yin   = QComboBox(); self.cmb_emb_yin.setEditable(True)
        self.cmb_emb_yang  = QComboBox(); self.cmb_emb_yang.setEditable(True)
        self.cmb_model_yin.addItems([self.yin.chat_model]); self.cmb_model_yang.addItems([self.yang.chat_model])
        self.cmb_emb_yin.addItems([self.yin.embed_model]); self.cmb_emb_yang.addItems([self.yang.embed_model])
        btn_refresh = QPushButton("Refresh Models"); btn_refresh.clicked.connect(self._refresh_models)
        row1.addWidget(QLabel("Yin model:"));  row1.addWidget(self.cmb_model_yin)
        row1.addWidget(QLabel("Yang model:")); row1.addWidget(self.cmb_model_yang)
        row1.addWidget(QLabel("Yin embedder:"));  row1.addWidget(self.cmb_emb_yin)
        row1.addWidget(QLabel("Yang embedder:")); row1.addWidget(self.cmb_emb_yang)
        row1.addWidget(btn_refresh)
        v.addLayout(row1)

        # DB paths
        row2 = QHBoxLayout(); row2.setSpacing(8)
        self.ed_db_convo = QLineEdit(DB_CONVO); self.ed_db_convo.setReadOnly(True)
        self.ed_db_yin   = QLineEdit(DB_YIN);   self.ed_db_yin.setReadOnly(True)
        self.ed_db_yang  = QLineEdit(DB_YANG);  self.ed_db_yang.setReadOnly(True)
        b1 = QPushButton("…"); b1.clicked.connect(lambda: self._choose_db(self.core_convo, self.ed_db_convo, "conversation"))
        b2 = QPushButton("…"); b2.clicked.connect(lambda: self._choose_db(self.core_yin,   self.ed_db_yin,   "yin_think"))
        b3 = QPushButton("…"); b3.clicked.connect(lambda: self._choose_db(self.core_yang,  self.ed_db_yang,  "yang_think"))
        row2.addWidget(QLabel("conversation.db:")); row2.addWidget(self.ed_db_convo, 1); row2.addWidget(b1)
        row2.addWidget(QLabel("yin_think.db:"));   row2.addWidget(self.ed_db_yin,   1); row2.addWidget(b2)
        row2.addWidget(QLabel("yang_think.db:"));  row2.addWidget(self.ed_db_yang,  1); row2.addWidget(b3)
        v.addLayout(row2)

        # helpers
        row3 = QHBoxLayout(); row3.setSpacing(8)
        btn_index = QPushButton("Index (conv)"); btn_index.clicked.connect(self._index_convo)
        btn_snapshot = QPushButton("Snapshot (conv)"); btn_snapshot.clicked.connect(self._snapshot_convo)
        btn_data = QPushButton("Open Data Viewer"); btn_data.clicked.connect(self._open_data_viewer)
        row3.addWidget(btn_index); row3.addWidget(btn_snapshot); row3.addWidget(btn_data); row3.addStretch(1)
        v.addLayout(row3)

        # instant reactions controls
        row4 = QHBoxLayout(); row4.setSpacing(8)
        self.chk_auto_react = QCheckBox("Auto-Reaction Loop")
        self.chk_auto_react.setChecked(True)
        self.spin_chain_max = QSpinBox(); self.spin_chain_max.setMinimum(0); self.spin_chain_max.setMaximum(99); self.spin_chain_max.setValue(4)
        row4.addWidget(self.chk_auto_react)
        row4.addWidget(QLabel("Max Chained Reactions:")); row4.addWidget(self.spin_chain_max)
        row4.addStretch(1)
        v.addLayout(row4)

        # -------------- Ollama Local Storage (Danger Zone) --------------
        danger = QFrame(); danger.setFrameShape(QFrame.StyledPanel)
        dv = QVBoxLayout(danger); dv.setContentsMargins(8,8,8,8); dv.setSpacing(6)
        title = QLabel("<b>Ollama Local Storage — Danger Zone</b>")
        title.setStyleSheet(f"color:{COLOR_TEXT_LIGHT};")
        info = QLabel("Detect, browse, open, or purge your local Ollama models cache (models, blobs, manifests).")
        info.setWordWrap(True); info.setStyleSheet(f"color:{COLOR_TEXT_LIGHT};")
        dv.addWidget(title); dv.addWidget(info)

        self.ed_ollama_models = QLineEdit(self._detect_ollama_models_dir()); self.ed_ollama_models.setReadOnly(True)
        self.ed_ollama_blobs  = QLineEdit(self._detect_ollama_blobs_dir(self.ed_ollama_models.text())); self.ed_ollama_blobs.setReadOnly(True)
        self.ed_ollama_manif  = QLineEdit(self._detect_ollama_manifests_dir(self.ed_ollama_models.text())); self.ed_ollama_manif.setReadOnly(True)

        rowd1 = QHBoxLayout(); rowd1.addWidget(QLabel("models dir:")); rowd1.addWidget(self.ed_ollama_models,1)
        bt_detect = QPushButton("Detect"); bt_detect.clicked.connect(self._detect_and_fill)
        bt_browse_models = QPushButton("Browse…"); bt_browse_models.clicked.connect(self._browse_models_dir)
        bt_open_models = QPushButton("Open Folder"); bt_open_models.clicked.connect(lambda: self._open_folder(self.ed_ollama_models.text()))
        rowd1.addWidget(bt_detect); rowd1.addWidget(bt_browse_models); rowd1.addWidget(bt_open_models)
        dv.addLayout(rowd1)

        rowd2 = QHBoxLayout(); rowd2.addWidget(QLabel("blobs dir:")); rowd2.addWidget(self.ed_ollama_blobs,1)
        bt_open_blobs = QPushButton("Open"); bt_open_blobs.clicked.connect(lambda: self._open_folder(self.ed_ollama_blobs.text()))
        rowd2.addWidget(bt_open_blobs); dv.addLayout(rowd2)

        rowd3 = QHBoxLayout(); rowd3.addWidget(QLabel("manifests dir:")); rowd3.addWidget(self.ed_ollama_manif,1)
        bt_open_manif = QPushButton("Open"); bt_open_manif.clicked.connect(lambda: self._open_folder(self.ed_ollama_manif.text()))
        rowd3.addWidget(bt_open_manif); dv.addLayout(rowd3)

        rowd4 = QHBoxLayout()
        purge_blobs = QPushButton("Purge Blobs"); purge_blobs.clicked.connect(lambda: self._purge_dir_confirm(self.ed_ollama_blobs.text(), "blobs"))
        purge_manif = QPushButton("Purge Manifests"); purge_manif.clicked.connect(lambda: self._purge_dir_confirm(self.ed_ollama_manif.text(), "manifests"))
        purge_all   = QPushButton("Purge All (Models+Blobs+Manifests)"); purge_all.clicked.connect(self._purge_all_confirm)
        for b in (purge_blobs, purge_manif, purge_all):
            b.setStyleSheet("QPushButton{background:#7a1f1f;color:#fff;border:1px solid #992525;padding:6px;}"
                            "QPushButton:hover{background:#922;}")
        rowd4.addWidget(purge_blobs); rowd4.addWidget(purge_manif); rowd4.addWidget(purge_all)
        dv.addLayout(rowd4)

        danger.setStyleSheet(f"QFrame{{background:#1b1d26;border:1px solid #333;border-radius:6px;}} QLabel{{color:{COLOR_TEXT_LIGHT};}} QLineEdit{{background:#11131a;color:{COLOR_TEXT_LIGHT};border:1px solid #444;padding:4px;}} QPushButton{{background:#232432;color:{COLOR_TEXT_LIGHT};border:1px solid #444;padding:4px 8px;}}")
        v.addWidget(danger)

        # style the settings area dark
        w.setStyleSheet(f"""
            QWidget#SettingsPanel, #SettingsPanel QLabel {{ color:{COLOR_TEXT_LIGHT}; background:{COLOR_BG_APP}; }}
            #SettingsPanel QLineEdit {{ background:#1b1d26; color:{COLOR_TEXT_LIGHT}; border:1px solid #444; padding:4px; }}
            #SettingsPanel QPushButton {{ background:#232432; color:{COLOR_TEXT_LIGHT}; border:1px solid #444; padding:4px 8px; }}
            #SettingsPanel QComboBox {{ background:#1b1d26; color:{COLOR_TEXT_LIGHT}; border:1px solid #444; padding:2px 4px; }}
        """)
        return w

    def _install_toolbar(self):
        tb = QToolBar("Main"); self.addToolBar(Qt.BottomToolBarArea, tb)
        act_help = QAction("Help (/help)", self); act_help.triggered.connect(lambda: self._inject_user("/help"))
        act_search = QAction("Search", self); act_search.triggered.connect(lambda: self._inject_user("/search plan"))
        act_tree = QAction("Tree", self); act_tree.triggered.connect(lambda: self._inject_user("/tree"))
        tb.addAction(act_help); tb.addAction(act_search); tb.addAction(act_tree)
        tb.setStyleSheet(f"QToolBar {{ background:#1b1d26; color:{COLOR_TEXT_LIGHT}; border-top:1px solid #222; }}")

    def _apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background:{COLOR_BG_APP}; }}
            QStatusBar {{ color:{COLOR_TEXT_LIGHT}; }}
            QDockWidget::title {{ background:#1b1d26; color:{COLOR_TEXT_LIGHT}; padding:6px; font-weight:600; }}
            QDockWidget {{ border:1px solid {COLOR_PANEL_BORDER}; }}
        """)

    def _style_dock(self, dock: QDockWidget):
        dock.setStyleSheet("QDockWidget { font-size:12px; }")

    # ----------- Ollama storage helpers -----------
    def _detect_ollama_models_dir(self) -> str:
        env = os.environ.get("OLLAMA_MODELS")
        if env:
            p = env
            if os.path.isdir(p): return os.path.abspath(p)
            cand = os.path.join(p, "models")
            if os.path.isdir(cand): return os.path.abspath(cand)
        home = os.path.expanduser("~")
        cand1 = os.path.join(home, ".ollama", "models")
        if os.path.isdir(cand1): return os.path.abspath(cand1)
        wincand = os.path.join(os.environ.get("USERPROFILE", home), ".ollama", "models")
        return os.path.abspath(wincand)
    def _detect_ollama_blobs_dir(self, models_dir: str) -> str:
        return os.path.abspath(os.path.join(models_dir, "blobs"))
    def _detect_ollama_manifests_dir(self, models_dir: str) -> str:
        return os.path.abspath(os.path.join(models_dir, "manifests"))
    def _detect_and_fill(self):
        m = self._detect_ollama_models_dir()
        b = self._detect_ollama_blobs_dir(m)
        f = self._detect_ollama_manifests_dir(m)
        self.ed_ollama_models.setText(m); self.ed_ollama_blobs.setText(b); self.ed_ollama_manif.setText(f)
        self.sig_status.emit("Ollama directories detected.")
    def _browse_models_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Ollama models directory", self.ed_ollama_models.text())
        if path:
            self.ed_ollama_models.setText(path)
            self.ed_ollama_blobs.setText(self._detect_ollama_blobs_dir(path))
            self.ed_ollama_manif.setText(self._detect_ollama_manifests_dir(path))
            self.sig_status.emit("Ollama models directory updated.")
    def _open_folder(self, path: str):
        if not path: return
        if sys.platform.startswith("win"):
            try: os.startfile(path)  # type: ignore
            except Exception: pass
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    def _purge_dir_confirm(self, path: str, label: str):
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Purge", f"{label} path does not exist:\n{path}")
            return
        reply = QMessageBox.question(
            self, "Confirm purge",
            f"Delete ALL files in:\n{path}\n\nThis will remove local Ollama {label} data.\nProceed?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._purge_dir(path)
            self.sig_status.emit(f"Purged {label} at {path}.")
    def _purge_all_confirm(self):
        m = self.ed_ollama_models.text().strip()
        b = self.ed_ollama_blobs.text().strip()
        f = self.ed_ollama_manif.text().strip()
        reply = QMessageBox.question(
            self, "Confirm purge ALL",
            f"Delete contents of:\n- {b}\n- {f}\n- {m}\n\nThis will remove local Ollama models cache.\nProceed?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for p, lbl in [(b,"blobs"), (f,"manifests"), (m,"models")]:
                if os.path.exists(p):
                    try: self._purge_dir(p)
                    except Exception as e: self.sig_status.emit(f"Failed to purge {lbl}: {e}")
            self.sig_status.emit("Purge ALL completed.")
    def _purge_dir(self, path: str):
        for name in os.listdir(path):
            full = os.path.join(path, name)
            try:
                if os.path.isdir(full) and not os.path.islink(full):
                    shutil.rmtree(full, ignore_errors=True)
                else:
                    try: os.remove(full)
                    except PermissionError:
                        try: os.chmod(full, 0o666); os.remove(full)
                        except Exception: pass
            except Exception:
                pass

    # ----------- helpers -----------
    def _convo_embedders(self) -> List[str]:
        items = []
        for txt in [self.cmb_emb_yin.currentText().strip() or self.yin.embed_model,
                    self.cmb_emb_yang.currentText().strip() or self.yang.embed_model]:
            if txt and txt not in items: items.append(txt)
        return items or [DEFAULT_EMBED_YIN]
    def _refresh_models(self):
        names = _ollama_tags()
        def refill(cmb: QComboBox, current: str):
            seen = set(); cmb.clear()
            for m in [current] + [n for n in names if n != current]:
                if m in seen: continue
                cmb.addItem(m); seen.add(m)
        refill(self.cmb_model_yin,  self.yin.chat_model)
        refill(self.cmb_model_yang, self.yang.chat_model)
        refill(self.cmb_emb_yin,    self.yin.embed_model)
        refill(self.cmb_emb_yang,   self.yang.embed_model)
        self.sig_status.emit("Model lists refreshed from Ollama.")
    def _choose_db(self, core: DBCore, edit: QLineEdit, label: str):
        path, _ = QFileDialog.getSaveFileName(self, f"Choose/Create {label}", edit.text(), "SQLite DB (*.db)")
        if not path: return
        core.close(); new_core = DBCore(path)
        if core is self.core_convo: self.core_convo = new_core
        elif core is self.core_yin: self.core_yin = new_core
        elif core is self.core_yang: self.core_yang = new_core
        edit.setText(path); self.sig_status.emit(f"Loaded {label}: {path}")
    def _open_data_viewer(self):
        DataViewer(self.core_convo, self.core_yin, self.core_yang, self).exec_()

    def _index_convo(self):
        emb = self._convo_embedders(); created = 0
        for r in self.core_convo.query("SELECT id, content FROM messages", ()):  created += self.core_convo.ensure_embeddings_multi("message", r["id"], r["content"], emb)
        for r in self.core_convo.query("SELECT id, text FROM facts", ()):       created += self.core_convo.ensure_embeddings_multi("fact", r["id"], r["text"], emb)
        for r in self.core_convo.query("SELECT id, content FROM artifacts", ()): created += self.core_convo.ensure_embeddings_multi("artifact", r["id"], r["content"], emb)
        self.sig_status.emit(f"Indexed (conversation) created {created} vectors.")

    def _snapshot_convo(self):
        count = 0
        try:
            with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
                code = f.read()
            aid, _, _ = self.core_convo.add_artifact("self:yin_yang_one.py", "script", code, {"note":"manual snapshot"})
            self.core_convo.ensure_embeddings_multi("artifact", aid, code, self._convo_embedders()); count += 1
        except Exception: pass
        for root, dirs, files in os.walk(WORKSPACE_DIR):
            for name in files:
                p = os.path.join(root, name); rel = os.path.relpath(p, WORKSPACE_DIR)
                try:
                    with open(p, "r", encoding="utf-8") as f: text = f.read()
                except Exception: continue
                aid, _, _ = self.core_convo.add_artifact(rel, "file", text, {"snapshot": True})
                self.core_convo.ensure_embeddings_multi("artifact", aid, text, self._convo_embedders()); count += 1
        self.sig_status.emit(f"Snapshot stored {count} items into conversation DB.")

    def _inject_user(self, text: str):
        self.ed_input.setText(text); self._send_user()

    # ----------- Conversation & Reaction Engine -----------

    def _send_user(self):
        text = self.ed_input.text().strip()
        if not text: return
        self.ed_input.clear()
        if text.startswith("/"):
            out = self._run_command(text, context_text=text)
            self.sig_conv.emit("System", out, COLOR_SYSTEM_MSG)
            self.core_convo.store_message("System", "event", out)
            return

        # 1) store & show user message
        mid = self.core_convo.store_message("User", "user", text)
        self.core_convo.ensure_embeddings_multi("message", mid, text, self._convo_embedders())
        self.sig_conv.emit("User", text, COLOR_USER_MSG)

        # 2) fire immediate reaction event (chain=0)
        self._on_public(author="User", text=text, chain=0)

    def _on_public(self, author: str, text: str, chain: int):
        """Push a reaction event so agents respond immediately."""
        self._queue.put(("react", author, text, chain))

    def _toggle_start(self, btn: QPushButton):
        running = btn.isChecked()
        btn.setText("Stop" if running else "Start")
        self.sig_status.emit("Running." if running else "Stopped.")
        if running:
            self._queue.put(("auto_turn",))
            # Start with random who first
            import random
            first = random.choice(["Yin", "Yang"])
            self.sig_conv.emit("System", f"Autonomous start: {first} begins.", COLOR_SYSTEM_MSG)
            self._agent_cycle(first, "Initiate self-improvement: analyze structure, propose first step.", "", chain=0)

    def _convo_model(self, name: str) -> str:
        return (self.cmb_model_yin.currentText().strip() if name=="Yin" else self.cmb_model_yang.currentText().strip())
    def _embedder_for(self, name: str) -> str:
        return (self.cmb_emb_yin.currentText().strip() if name=="Yin" else self.cmb_emb_yang.currentText().strip())

    def _build_convo_context(self, cue: str) -> str:
        rows = self.core_convo.query("SELECT agent, role, content FROM messages ORDER BY rowid DESC LIMIT ?", (MAX_CONTEXT_MSGS,))
        msgs = rows[::-1]; text = "\n".join([f"{r['agent']}:{r['role']}: {r['content']}" for r in msgs])
        hits = self.core_convo.semantic_search(cue, k=RAG_K_CONVO, embedders=self._convo_embedders())
        hlines = [f"[{kind}#{rid} {score:.3f} {ts} {meta}] {content}" for kind,rid,score,content,ts,meta in hits]
        return (text + ("\n\n" + "\n".join(hlines) if hlines else "")).strip()

    def _build_think_context(self, name: str, cue: str) -> str:
        db = self.core_yin if name == "Yin" else self.core_yang
        rows = db.query("SELECT content FROM messages WHERE role='think' ORDER BY rowid DESC LIMIT 8", ())
        notes = "\n".join([r["content"] for r in rows[::-1]])
        hits = db.semantic_search(cue, k=RAG_K_THINK, embedders=[self._embedder_for(name)])
        hlines = [f"[{kind}#{rid} {score:.3f}] {content}" for kind,rid,score,content,ts,meta in hits]
        return (notes + ("\n\n" + "\n".join(hlines) if hlines else "")).strip()

    def _bg_worker(self):
        while True:
            item = self._queue.get()
            try:
                kind = item[0]
                if kind == "react":
                    author, text, chain = item[1], item[2], item[3]
                    # select targets
                    if author == "User":
                        targets = ["Yin", "Yang"]
                    elif author == "Yin":
                        targets = ["Yang"]
                    elif author == "Yang":
                        targets = ["Yin"]
                    else:
                        targets = []
                    # bounded chaining
                    chain_max = max(0, int(self.spin_chain_max.value()))
                    if chain > chain_max:
                        self.sig_status.emit(f"Reaction chain limit reached ({chain_max}).")
                    else:
                        ctx = self._build_convo_context(text)
                        for who in targets:
                            self._queue.put(("agent_cycle", who, text, ctx, chain))
                elif kind == "agent_cycle":
                    who, cue, ctx, chain = item[1], item[2], item[3], item[4]
                    self._agent_cycle(who, cue, ctx, chain)
                elif kind == "auto_turn":
                    goal = "Self-improve: connect fundamentals, propose code via /write, use +/- diffs semantically."
                    ctx = self._build_convo_context(goal)
                    for who in ("Yin", "Yang"):
                        self._queue.put(("agent_cycle", who, goal, ctx, 0))
                    plan = llm_generate(self._convo_model("Yin"), "Summarize three concrete next actions as bullets.", system="Be short and specific.", max_tokens=160)
                    self.sig_conv.emit("System", plan, COLOR_SYSTEM_MSG)
                    self.core_convo.store_message("System", "plan", plan)
                    QTimer.singleShot(10000, lambda: self._queue.put(("auto_turn",)))  # every ~10s for continuous thinking
            except Exception as e:
                tb = traceback.format_exc()
                try:
                    self.core_convo.execute("INSERT INTO errors(ts,message,traceback) VALUES (?,?,?)", (_now(), str(e), tb))
                except Exception:
                    pass
                self.sig_conv.emit("⚠️ Error", f"{e}\n(Logged in conversation DB.)", COLOR_SYSTEM_MSG)
            finally:
                self._queue.task_done()

    def _agent_cycle(self, who: str, cue: str, convo_ctx: str, chain: int):
        # THINK (private, background thinking)
        think_ctx = self._build_think_context(who, cue)
        sys_think = (self.yin.system_think if who=="Yin" else self.yang.system_think)
        model    = self._convo_model(who)
        thought = llm_generate(
            model,
            f"Recent cue: {cue}\nRecent private notes:\n{think_ctx}\n\n"
            "Think autonomously. Produce notes, +/- diffs, snippets (<=150 words). Plaintext.",
            system=sys_think,
            max_tokens=THINK_TOKENS_DEFAULT
        )
        db = self.core_yin if who=="Yin" else self.core_yang
        db.store_message(who, "think", thought)
        last_id = db.query("SELECT last_insert_rowid() AS id", ())[0]["id"]
        db.ensure_embedding("message", last_id, thought, self._embedder_for(who))
        if who=="Yin": self.sig_yin.emit(f"{who} (private)", thought)
        else:          self.sig_yang.emit(f"{who} (private)", thought)

        # SPEAK (public)
        sys_pub = (self.yin.system_public if who=="Yin" else self.yang.system_public)
        public = llm_generate(
            model,
            f"Cue: {cue}\nShared context:\n{convo_ctx}\n\n"
            "Use private insights (without revealing) for actionable reply. "
            "Propose /commands to advance (e.g., /write for code updates).",
            system=sys_pub,
            max_tokens=PUBLIC_TOKENS_DEFAULT
        )
        mid = self.core_convo.store_message(who, "assistant", public)
        self.core_convo.ensure_embeddings_multi("message", mid, public, self._convo_embedders())
        self.sig_conv.emit(who, public, COLOR_CONVO_PANEL)
        (self.yin.speaker if who=="Yin" else self.yang.speaker).say(self._tts_digest(public))

        # Execute slash-commands in public text
        for line in public.splitlines():
            l = line.strip()
            if l.startswith("/") and len(l) > 1:
                out = self._run_command(l, context_text=public)
                self.sig_conv.emit("System", f"↳ {l}\n{out}", COLOR_SYSTEM_MSG)
                self.core_convo.store_message("System", "command", f"{l}\n{out}")

        # Trigger reactions if auto
        if self.chk_auto_react.isChecked():
            self._on_public(author=who, text=public, chain=chain+1)

    def _tts_digest(self, text: str, limit=200):
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:limit]

    # -------- Commands (conversation DB scope) --------
    def _run_command(self, raw: str, context_text: Optional[str]=None) -> str:
        parts = raw.strip().split()
        if not parts: return "Empty command."
        cmd = parts[0][1:].lower(); args = parts[1:]
        def emb_now(kind, rid, text):
            return self.core_convo.ensure_embeddings_multi(kind, rid, text, self._convo_embedders())
        try:
            if cmd == "help":
                return "\n"\
                "/help — list commands\n"\
                "/sys <yin|yang> <append|set> <text>\n"\
                "/note <text> [#tags]\n"\
                "/search <query>\n"\
                "/plan <goal>\n"\
                "/model <yin|yang> <model_name>\n"\
                "/voice <yin|yang> <voice_name>\n"\
                "/save\n"\
                "/index\n"\
                "/export [path.json]\n"\
                "/ls [relpath]\n"\
                "/tree [relpath]\n"\
                "/cat <#id|relpath>\n"\
                "/write <relpath> [kind]\n"\
                "/snapshot"
            if cmd == "sys":
                if len(args) < 3: return "Usage: /sys <yin|yang> <append|set> <text>"
                who, op = args[0].lower(), args[1].lower(); text = " ".join(args[2:])
                if who not in ("yin","yang"): return "Target must be yin or yang."
                if who=="yin":
                    if op=="append": self.yin.system_public = (self.yin.system_public + "\n" + text).strip()
                    elif op=="set":  self.yin.system_public = text
                    else: return "Op must be append or set."
                else:
                    if op=="append": self.yang.system_public = (self.yang.system_public + "\n" + text).strip()
                    elif op=="set":  self.yang.system_public = text
                    else: return "Op must be append or set."
                return f"{who} system prompt updated."
            if cmd == "note":
                if not args: return "Usage: /note <text> [#tags]"
                text = " ".join(args); tags = " ".join([t for t in args if t.startswith("#")])
                fid = self.core_convo.store_fact(text, tags); emb_now("fact", fid, text)
                return f"Saved note #{fid} {tags}"
            if cmd == "search":
                if not args: return "Usage: /search <query>"
                q = " ".join(args); hits = self.core_convo.semantic_search(q, k=RAG_K_CONVO, embedders=self._convo_embedders())
                if not hits: return "No results."
                out = ["Top results:"] + [f"[{score:.3f}] {kind}#{rid} @ {ts} — {meta}: {text[:160]}" for kind,rid,score,text,ts,meta in hits]
                return "\n".join(out)
            if cmd == "plan":
                goal = " ".join(args) if args else "Improve ourselves."
                plan = llm_generate(self._convo_model("Yin"), f"Draft a concise plan for: {goal}. Provide bullet steps.", system="Be concrete.", max_tokens=200)
                fid = self.core_convo.store_fact("PLAN: " + goal + "\n" + plan, "#plan"); emb_now("fact", fid, plan)
                return "Plan saved as note #" + str(fid) + "\n" + plan
            if cmd == "model":
                if len(args) < 2: return "Usage: /model <yin|yang> <model_name>"
                who, mdl = args[0].lower(), " ".join(args[1:])
                if who == "yin":   self.cmb_model_yin.setEditText(mdl)
                elif who == "yang":self.cmb_model_yang.setEditText(mdl)
                else: return "Target must be yin or yang."
                return f"Set {who} model to {mdl}"
            if cmd == "voice":
                if len(args) < 2: return "Usage: /voice <yin|yang> <voice_name>"
                who, vname = args[0].lower(), " ".join(args[1:])
                if who == "yin":   self.yin.speaker = Speaker(vname)
                elif who == "yang":self.yang.speaker = Speaker(vname)
                else: return "Target must be yin or yang."
                return f"Switched {who} voice to {vname}"
            if cmd == "save":
                rows = self.core_convo.query("SELECT ts, agent, role, content FROM messages ORDER BY rowid DESC LIMIT 80", ())
                text = "\n".join([f"{r['ts']} | {r['agent']}:{r['role']} => {r['content']}" for r in rows[::-1]])
                fid = self.core_convo.store_fact(text, "#transcript"); emb_now("fact", fid, text)
                return f"Saved transcript note #{fid}"
            if cmd == "index":
                self._index_convo(); return "Indexing queued."
            if cmd == "export":
                path = args[0] if args else os.path.join(WORKSPACE_DIR, "export.json")
                out = {"facts": [], "messages": [], "artifacts": []}
                for tbl in ("facts","messages","artifacts"):
                    rows = self.core_convo.query(f"SELECT * FROM {tbl}", ())
                    cols = rows[0].keys() if rows else []
                    out[tbl] = [dict(zip(cols, [r[c] for c in cols])) for r in rows]
                with open(path, "w", encoding="utf-8") as f: json.dump(out, f, indent=2)
                return f"Exported to {path}"
            if cmd == "ls":
                rel = args[0] if args else "."
                root = os.path.normpath(os.path.join(WORKSPACE_DIR, rel))
                if not root.startswith(WORKSPACE_DIR): return "Out of workspace."
                if not os.path.isdir(root): return f"Not a dir: {rel}"
                names = sorted(os.listdir(root)); return "\n".join(names) if names else "(empty)"
            if cmd == "tree":
                rel = args[0] if args else "."
                root = os.path.normpath(os.path.join(WORKSPACE_DIR, rel))
                if not root.startswith(WORKSPACE_DIR): return "Out of workspace."
                if not os.path.exists(root): return f"No such path: {rel}"
                if os.path.isfile(root): return rel
                def _tree(path, prefix=""):
                    entries = sorted(os.listdir(path)); lines = []
                    for i, name in enumerate(entries):
                        full = os.path.join(path, name)
                        branch = "└── " if i == len(entries)-1 else "├── "
                        lines.append(prefix + branch + name)
                        if os.path.isdir(full):
                            extension = "    " if i == len(entries)-1 else "│   "
                            lines += _tree(full, prefix+extension)
                    return lines
                return "\n".join(_tree(root)) or "(empty)"
            if cmd == "cat":
                if not args: return "Usage: /cat <#id|relpath>"
                ref = args[0]
                if ref.startswith("#"):
                    try:
                        aid = int(ref[1:]); r = self.core_convo.query("SELECT * FROM artifacts WHERE id=?", (aid,))
                        if not r: return f"No artifact #{aid}"
                        r = r[0]; return f"[artifact #{aid} {r['path']} v{r['version']}]\n{r['content']}"
                    except Exception: return "Bad id."
                else:
                    root = os.path.normpath(os.path.join(WORKSPACE_DIR, ref))
                    if not root.startswith(WORKSPACE_DIR): return "Out of workspace."
                    if not os.path.isfile(root): return f"No such file: {ref}"
                    with open(root, "r", encoding="utf-8", errors="ignore") as f: return f.read()
            if cmd == "write":
                if not args: return "Usage: /write <relpath> [kind]"
                rel = args[0]; kind = args[1] if len(args) > 1 else "code"
                blocks = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", context_text or "", re.MULTILINE)
                if not blocks: return "No code block found in message."
                content = blocks[-1].strip()
                dst = os.path.normpath(os.path.join(WORKSPACE_DIR, rel))
                if not dst.startswith(WORKSPACE_DIR): return "Out of workspace."
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "w", encoding="utf-8") as f: f.write(content)
                aid, ver, sha = self.core_convo.add_artifact(rel, kind, content, {"source": "write"})
                self.core_convo.ensure_embeddings_multi("artifact", aid, content, self._convo_embedders())
                return f"Wrote {rel} (v{ver}, sha={sha[:10]}…)"
            if cmd == "snapshot":
                self._snapshot_convo(); return "Snapshot stored."
            return f"Unknown command: {cmd}"
        except Exception as e:
            tb = traceback.format_exc()
            try:
                self.core_convo.execute("INSERT INTO errors(ts,message,traceback) VALUES (?,?,?)", (_now(), str(e), tb))
            except Exception: pass
            return f"Command error: {e}"

# -------------------- Entrypoint --------------------

def main():
    try:
        app = QApplication(sys.argv)
        win = YinYangMain(); win.show()
        sys.exit(app.exec_())
    except Exception as e:
        try:
            core = DBCore(DB_CONVO)
            core.execute("INSERT INTO errors(ts,message,traceback) VALUES (?,?,?)", (_now(), str(e), traceback.format_exc()))
            core.close()
        except Exception:
            pass
        raise

if __name__ == "__main__":
    main()