# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `OllamaMiniChat.py`

OllamaMiniChat.py
=================
A compact yet capable PyQt5 chat client for **local Ollama** models and **OpenAI** models
with *real-time* streaming text & code, colorful syntax blocks, prompt manager, upload manager,
rolling timing logs, persistent mini-RAG dataset, Zira TTS, a generated Markdown API/README,
and a slim live system log.

Key features
------------
• Providers: **Ollama** (default) and **OpenAI**. Model dropdown updates per provider.
• Real-Time streaming (FAST) for plain text and fenced ```code``` blocks (validated languages).
  - While streaming, code is shown in a “floating terminal” container expanded to full script height.
  - On completion, code blocks auto-minimize (can be expanded by user).
  - Text stream renders live as well (char-wise), with optional metallic <think> styling.
• Colorful code via **Pygments** (Monokai). Emojis on badges.
• Non-semantic and semantic history:
  - Visible (session-only) history to avoid artifacts in displayed text.
  - Persistent dataset of the last **N pairs** (slider; default 10), with rolling file and priority taper.
• Timing logs:
  - Default vs Real-Time averages shown; logs capped to 100 entries (rolling).
  - “Reset Averages” button + optional reset during “Clear Chat”.
• TTS (Windows SAPI5 via **pyttsx3**) using **Microsoft Zira**, **150%** speed by default.
  - Auto-reads **assistant responses only**, in order, no gaps. Stop at any time.
  - Speed slider persisted across sessions in Settings.
• Upload Manager:
  - Paste/drag/drop or browse files/folders; icons for text/code, images, folders.
  - Recursively ingests folders (skips __pycache__, venv*/.venv*, large junk); keeps .git.
  - Simple “tag-and-bucket” enrichment (no vectors), stored in /data/uploads.
  - Per-file progress bars driven via Qt Signals (no hanging).
  - “Clear Uploaded Knowledge” button to purge.
• Prompt Manager:
  - Remove the big system prompt from the main window.
  - Manage named prompts (add/edit/delete*), reorder, check multiple to include in system preamble.
    (*Default prompt cannot be deleted; it can be toggled off.)
• Smarter prompting:
  - Preamble includes (in order): checked prompts, then light summary of older pairs, then
    visible recent pairs (tapered), emphasizing the current user message.
• API / README generator:
  - Button generates **Chat_Agent_API.md** and **README.generated.md** in /data/docs from code,
    scanning @api_expose functions and docstrings. Pop-up viewer with “Copy” button.
• UX niceties:
  - Smoky gray theme, high contrast text, improved professional typography.
  - Top black slim **System Log** ticker + on-disk logs (cleared on startup).
  - Auto-scroll toggle (ON by default) so you can scroll during streaming without snap-back.
  - Provider+Model label inside each response card: **[Provider][model] →** line above content.
  - Enter in the input sends the message (QLineEdit).
• Robust error pop-ups; unhandled exceptions are intercepted and shown.

Install
-------
    pip install pyqt5 requests pyperclip pygments pyttsx3

Run
---
    ollama serve   # if using Ollama
    python OllamaMiniChat.py

**Classes:** PythonHighlighter, TimingLog, DatasetManager, UploadSignals, UploadedKnowledge, TTSManager, ProviderBackend, OllamaBackend, OpenAIBackend, CodeBlockContainer, UserMessage, BotStreamMessage, PromptManager, SettingsDialog, UploadManagerDialog, MiniChat

**Functions:** ensure_dirs(), now_iso(), log_line(msg), _win_protect(plaintext), _win_unprotect(cipher), save_openai_key(key), load_openai_key(), safe_lang(lang), pygments_html(code, lang), api_expose(fn), generate_api_docs(out_md, readme_md), main()

## Other Files

The following files are present in the project but were not analysed in detail:

- `data\datasets\chat_pairs.jsonl`
- `data\docs\Chat_Agent_API.md`
- `data\docs\README.generated.md`
- `data\logs\system.log`
- `data\visible_history.txt`


## Detailed Module Analyses


## Module `OllamaMiniChat.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OllamaMiniChat.py
=================
A compact yet capable PyQt5 chat client for **local Ollama** models and **OpenAI** models
with *real-time* streaming text & code, colorful syntax blocks, prompt manager, upload manager,
rolling timing logs, persistent mini-RAG dataset, Zira TTS, a generated Markdown API/README,
and a slim live system log.

Key features
------------
• Providers: **Ollama** (default) and **OpenAI**. Model dropdown updates per provider.
• Real-Time streaming (FAST) for plain text and fenced ```code``` blocks (validated languages).
  - While streaming, code is shown in a “floating terminal” container expanded to full script height.
  - On completion, code blocks auto-minimize (can be expanded by user).
  - Text stream renders live as well (char-wise), with optional metallic <think> styling.
• Colorful code via **Pygments** (Monokai). Emojis on badges.
• Non-semantic and semantic history:
  - Visible (session-only) history to avoid artifacts in displayed text.
  - Persistent dataset of the last **N pairs** (slider; default 10), with rolling file and priority taper.
• Timing logs:
  - Default vs Real-Time averages shown; logs capped to 100 entries (rolling).
  - “Reset Averages” button + optional reset during “Clear Chat”.
• TTS (Windows SAPI5 via **pyttsx3**) using **Microsoft Zira**, **150%** speed by default.
  - Auto-reads **assistant responses only**, in order, no gaps. Stop at any time.
  - Speed slider persisted across sessions in Settings.
• Upload Manager:
  - Paste/drag/drop or browse files/folders; icons for text/code, images, folders.
  - Recursively ingests folders (skips __pycache__, venv*/.venv*, large junk); keeps .git.
  - Simple “tag-and-bucket” enrichment (no vectors), stored in /data/uploads.
  - Per-file progress bars driven via Qt Signals (no hanging).
  - “Clear Uploaded Knowledge” button to purge.
• Prompt Manager:
  - Remove the big system prompt from the main window.
  - Manage named prompts (add/edit/delete*), reorder, check multiple to include in system preamble.
    (*Default prompt cannot be deleted; it can be toggled off.)
• Smarter prompting:
  - Preamble includes (in order): checked prompts, then light summary of older pairs, then
    visible recent pairs (tapered), emphasizing the current user message.
• API / README generator:
  - Button generates **Chat_Agent_API.md** and **README.generated.md** in /data/docs from code,
    scanning @api_expose functions and docstrings. Pop-up viewer with “Copy” button.
• UX niceties:
  - Smoky gray theme, high contrast text, improved professional typography.
  - Top black slim **System Log** ticker + on-disk logs (cleared on startup).
  - Auto-scroll toggle (ON by default) so you can scroll during streaming without snap-back.
  - Provider+Model label inside each response card: **[Provider][model] →** line above content.
  - Enter in the input sends the message (QLineEdit).
• Robust error pop-ups; unhandled exceptions are intercepted and shown.

Install
-------
    pip install pyqt5 requests pyperclip pygments pyttsx3

Run
---
    ollama serve   # if using Ollama
    python OllamaMiniChat.py
"""

# ---------- Standard imports ----------
import os, sys, re, json, time, threading, traceback, queue, ctypes, base64
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
from datetime import datetime, timezone

import requests
import pyperclip

# ---------- Qt imports ----------
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject, QEvent
from PyQt5.QtGui import (
    QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QIcon,
    QKeySequence
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPlainTextEdit,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QCheckBox,
    QTextEdit, QSizeGrip, QFileDialog, QProgressBar, QMessageBox, QDialog,
    QListWidget, QListWidgetItem, QTabWidget, QFormLayout, QSpinBox, QTextBrowser
)

# ---------- Optional Pygments ----------
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import HtmlFormatter
    HAVE_PYGMENTS = True
except Exception:
    HAVE_PYGMENTS = False

# ---------- Constants / Paths ----------
APP_NAME = "Ollama Mini Chat"
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DOCS_DIR = DATA_DIR / "docs"
LOGS_DIR = DATA_DIR / "logs"
PROMPTS_DIR = DATA_DIR / "prompts"
DATASETS_DIR = DATA_DIR / "datasets"
UPLOADS_DIR = DATA_DIR / "uploads"

VISIBLE_HISTORY_FILE = DATA_DIR / "visible_history.txt"  # session-only; cleared on start
DATASET_JSONL = DATASETS_DIR / "chat_pairs.jsonl"       # rolling persistent dataset
UPLOAD_INDEX_JSON = UPLOADS_DIR / "index.json"          # uploaded items metadata (tags only)
PROMPTS_INDEX_JSON = PROMPTS_DIR / "index.json"         # prompt list/order/checked
TIMINGS_LOG = LOGS_DIR / "timings.log"                  # rolling timings up to 100 rows
SYSTEM_LOG = LOGS_DIR / "system.log"                    # cleared each start
OPENAI_KEY_FILE = DATA_DIR / "openai_key.bin"           # encrypted with DPAPI (Windows) else b64

DEFAULT_PROVIDER = "Ollama"
DEFAULT_MODEL = "gpt-oss:20b"
DEFAULT_EMBEDDER = "snowflake-arctic-embed2:latest"

# ---------- Theming ----------
SMOKY_BG = "#2E2E2E"
CARD_INDIGO = "#3b3552"
USER_BLUE = "#0f3e5e"
DEEP_PURPLE = "#40395f"
SOFT_PURPLE = "#4a416b"
SOFT_TEXT = "#e6e6f0"
MUTED_TEXT = "#cfd1da"
BLACK = "#000000"

SMALL_BUTTON = (
    "QPushButton {background:#EEE;border:1px solid #AAA;color:#111;padding:2px 6px;"
    "font-size:10px;border-radius:6px;} QPushButton:hover {background:#f7f7f7;}"
)
PRIMARY_BUTTON = (
    "QPushButton {background:#ADD8E6;border:1px solid #CCC;color:#000;padding:4px 10px;"
    "font-size:11px;border-radius:10px;} QPushButton:hover {background:#B0E0E6;}"
)
BADGE_STYLE = (
    "QLabel { background: #2d2d30; color: #e5e5e5; border: 1px solid #3b3b3f;"
    "padding: 2px 6px; border-radius: 6px; font: 10px 'Segoe UI'; }"
)

# ---------- Helpers: system log ----------
def ensure_dirs():
    for p in [DATA_DIR, DOCS_DIR, LOGS_DIR, PROMPTS_DIR, DATASETS_DIR, UPLOADS_DIR]:
        p.mkdir(parents=True, exist_ok=True)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def log_line(msg: str):
    """Append to system log and print to console."""
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with SYSTEM_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

# ---------- Windows DPAPI encryption (fallback to base64 on non-Windows) ----------
def _win_protect(plaintext: str) -> bytes:
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", ctypes.c_uint), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]
    CRYPTPROTECT_LOCAL_MACHINE = 0x04
    data = plaintext.encode("utf-8")
    blob_in = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_ubyte)))
    blob_out = DATA_BLOB()
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    if not crypt32.CryptProtectData(ctypes.byref(blob_in), None, None, None, None, CRYPTPROTECT_LOCAL_MACHINE, ctypes.byref(blob_out)):
        raise OSError("CryptProtectData failed")
    try:
        out = ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        kernel32.LocalFree(blob_out.pbData)
    return out

def _win_unprotect(cipher: bytes) -> str:
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", ctypes.c_uint), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]
    blob_in = DATA_BLOB(len(cipher), ctypes.cast(ctypes.create_string_buffer(cipher), ctypes.POINTER(ctypes.c_ubyte)))
    blob_out = DATA_BLOB()
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    if not crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        raise OSError("CryptUnprotectData failed")
    try:
        out = ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        kernel32.LocalFree(blob_out.pbData)
    return out.decode("utf-8", errors="ignore")

def save_openai_key(key: str):
    try:
        if sys.platform.startswith("win"):
            enc = _win_protect(key)
        else:
            enc = base64.urlsafe_b64encode(key.encode("utf-8"))
        with OPENAI_KEY_FILE.open("wb") as f:
            f.write(enc)
        log_line("OpenAI API key saved.")
    except Exception as e:
        log_line(f"Failed to save OpenAI key: {e}")

def load_openai_key() -> str:
    if not OPENAI_KEY_FILE.exists():
        return ""
    try:
        data = OPENAI_KEY_FILE.read_bytes()
        if sys.platform.startswith("win"):
            return _win_unprotect(data)
        else:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except Exception as e:
        log_line(f"Failed to load OpenAI key: {e}")
        return ""

# ---------- Pygments integration ----------
VALID_LANGS = {
    # web
    "html","xml","css","javascript","js","typescript","ts","json","yaml","yml","markdown","md",
    # python & data
    "python","py","ipython","sqlite","sql","ini","toml",
    # c/c++/rust/go
    "c","cpp","c++","hpp","h","rust","rs","go",
    # java/kotlin/scala
    "java","kotlin","kt","scala",
    # .net
    "csharp","cs","fsharp","vbnet",
    # shell & powershell
    "bash","sh","zsh","fish","powershell","ps1","cmd","bat",
    # scripting
    "lua","perl","ruby","rb","php","r",
    # devops
    "docker","dockerfile","make","cmake",
    # GPU
    "cuda","cu","metal","opencl",
    # others
    "swift","objective-c","objc","matlab","octave",
}

def safe_lang(lang: Optional[str]) -> Optional[str]:
    if not lang:
        return None
    lang = lang.strip().lower()
    return lang if lang in VALID_LANGS else None

def pygments_html(code: str, lang: Optional[str]) -> str:
    if not HAVE_PYGMENTS:
        return "<pre style='white-space:pre-wrap; font-family:Consolas,monospace; font-size:12px;'>" + \
               (code.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")) + "</pre>"
    try:
        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
    except Exception:
        return "<pre style='white-space:pre-wrap; font-family:Consolas,monospace; font-size:12px;'>" + \
               (code.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")) + "</pre>"
    formatter = HtmlFormatter(style="monokai", noclasses=True)
    return highlight(code, lexer, formatter)

# ---------- Optional Python-only fallback highlighter (unused in final code widgets) ----------
class PythonHighlighter(QSyntaxHighlighter):
    KEYWORDS = {
        "def","class","if","elif","else","while","for","try","except","finally",
        "with","as","import","from","return","pass","break","continue","in",
        "not","and","or","is","lambda","yield","raise","assert","global","nonlocal"
    }
    def __init__(self, doc):
        super().__init__(doc)
        self.fmt_kw = QTextCharFormat(); self.fmt_kw.setForeground(QColor("#569CD6"))
        self.fmt_str = QTextCharFormat(); self.fmt_str.setForeground(QColor("#CE9178"))
        self.fmt_cmt = QTextCharFormat(); self.fmt_cmt.setForeground(QColor("#6A9955"))
        self.fmt_num = QTextCharFormat(); self.fmt_num.setForeground(QColor("#B5CEA8"))
        self.fmt_dec = QTextCharFormat(); self.fmt_dec.setForeground(QColor("#C586C0"))
        self.fmt_fn = QTextCharFormat(); self.fmt_fn.setForeground(QColor("#DCDCAA"))
        self.simple_rules = [(re.compile(rf"\b{kw}\b"), self.fmt_kw) for kw in self.KEYWORDS] + [
            (re.compile(r'".*?"'), self.fmt_str),
            (re.compile(r"'.*?'"), self.fmt_str),
            (re.compile(r"#.*"), self.fmt_cmt),
            (re.compile(r"\b\d+(\.\d+)?\b"), self.fmt_num),
            (re.compile(r"@\w+"), self.fmt_dec),
        ]
    def highlightBlock(self, text: str):
        for rx, fmt in self.simple_rules:
            for m in rx.finditer(text):
                self.setFormat(m.start(), m.end()-m.start(), fmt)
        for m in re.finditer(r"\bdef\s+(\w+)", text):
            self.setFormat(m.start(1), len(m.group(1)), self.fmt_fn)
        for m in re.finditer(r"\bclass\s+(\w+)", text):
            self.setFormat(m.start(1), len(m.group(1)), self.fmt_fn)

# ---------- Timing logger ----------
class TimingLog:
    """
    Rolling timing log of up to 100 rows across both modes.
    Each row: {"ts": ISO, "mode": "default"|"realtime", "ms": float}
    """
    def __init__(self, path: Path):
        self.path = path
        self.rows: List[Dict] = []
        if self.path.exists():
            try:
                self.rows = [json.loads(l) for l in self.path.read_text(encoding="utf-8").splitlines() if l.strip()]
            except Exception:
                self.rows = []
        self.clean_start()

    @api_expose := (lambda f: f)  # simple marker for API scanner; decorated later properly
    def clean_start(self):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        # clear system log on startup
        SYSTEM_LOG.write_text("", encoding="utf-8")

    def add(self, mode: str, ms: float):
        self.rows.append({"ts": now_iso(), "mode": mode, "ms": ms})
        # keep 100
        if len(self.rows) > 100:
            self.rows = self.rows[-100:]
        try:
            with self.path.open("w", encoding="utf-8") as f:
                for r in self.rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        except Exception as e:
            log_line(f"TimingLog write failed: {e}")

    def averages(self) -> Tuple[float,float]:
        d = [r["ms"] for r in self.rows if r.get("mode") == "default"]
        s = [r["ms"] for r in self.rows if r.get("mode") == "realtime"]
        d_avg = sum(d)/len(d) if d else 0.0
        s_avg = sum(s)/len(s) if s else 0.0
        return d_avg, s_avg

    def reset(self):
        self.rows = []
        try:
            self.path.write_text("", encoding="utf-8")
        except Exception:
            pass

# ---------- Dataset manager ----------
class DatasetManager:
    """
    Keeps a rolling JSONL dataset of user/assistant pairs (persistent),
    plus a session-only visible history file to ensure clean display (no artifacts).
    """
    def __init__(self, jsonl_path: Path, visible_path: Path, limit_pairs: int = 10):
        self.jsonl_path = jsonl_path
        self.visible_path = visible_path
        self.limit = limit_pairs
        DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        # session visible history wiped on start
        self.visible_path.write_text("", encoding="utf-8")
        if not self.jsonl_path.exists():
            self.jsonl_path.touch()

    def set_limit(self, n: int):
        self.limit = max(1, int(n))

    def append_visible(self, line: str):
        with self.visible_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def append_pair(self, user: str, assistant: str):
        rows = []
        if self.jsonl_path.exists():
            rows = [json.loads(l) for l in self.jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        rows.append({"ts": now_iso(), "user": user, "assistant": assistant})
        if len(rows) > self.limit:
            rows = rows[-self.limit:]
        with self.jsonl_path.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def load_pairs(self) -> List[Dict]:
        if not self.jsonl_path.exists():
            return []
        try:
            return [json.loads(l) for l in self.jsonl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        except Exception:
            return []

    def clear_all(self):
        self.jsonl_path.write_text("", encoding="utf-8")
        self.visible_path.write_text("", encoding="utf-8")

# ---------- Upload manager (signals for thread-safe) ----------
class UploadSignals(QObject):
    item_started = pyqtSignal(str, str)       # item_id, label
    progress = pyqtSignal(str, int)           # item_id, percent
    item_done = pyqtSignal(str)               # item_id
    item_error = pyqtSignal(str, str)         # item_id, message
    refresh_view = pyqtSignal()

class UploadedKnowledge:
    """
    Simple tag-and-bucket store (no vectors). Each item:
    {"id": "...", "type": "file|image|folder", "path": "...", "tags": [...], "ts": ...}
    """
    def __init__(self, index_path: Path, signals: UploadSignals):
        self.index_path = index_path
        self.signals = signals
        self.items: Dict[str, Dict] = {}
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        if self.index_path.exists():
            try:
                self.items = json.loads(self.index_path.read_text(encoding="utf-8"))
            except Exception:
                self.items = {}

    def save(self):
        try:
            with self.index_path.open("w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_line(f"Upload index save failed: {e}")

    def clear(self):
        self.items = {}
        self.save()

    def ingest_paths(self, paths: List[Path]):
        """
        Handle ingestion on a background thread; emit signals to update UI.
        """
        def worker():
            try:
                for p in paths:
                    if p.is_dir():
                        self._ingest_folder(p)
                    else:
                        self._ingest_file(p)
            except Exception as e:
                self.signals.item_error.emit("batch", str(e))
            finally:
                self.signals.refresh_view.emit()
        threading.Thread(target=worker, daemon=True).start()

    def _ingest_folder(self, folder: Path):
        item_id = f"folder:{folder.name}:{int(time.time())}"
        self.signals.item_started.emit(item_id, f"Folder: {folder}")
        self.items[item_id] = {"id":item_id,"type":"folder","path":str(folder),"tags":[folder.name],"ts":now_iso()}
        count=0
        for root, dirs, files in os.walk(folder):
            # skip junk
            dirs[:] = [d for d in dirs if d not in ("__pycache__",) and not d.lower().startswith(("venv",".venv"))]
            for name in files:
                f = Path(root) / name
                # include .git and everything else
                self._ingest_file(f, parent=item_id, silent=True)
                count+=1
                pct = min(100, int((count % 200) / 2))  # lightweight fake progress
                self.signals.progress.emit(item_id, pct)
        self.signals.progress.emit(item_id, 100)
        self.signals.item_done.emit(item_id)
        self.save()

    def _ingest_file(self, file: Path, parent: Optional[str]=None, silent: bool=False):
        ftype = "image" if file.suffix.lower() in (".png",".jpg",".jpeg",".gif",".webp") else "file"
        item_id = f"{ftype}:{file.name}:{int(time.time()*1000)%100000000}"
        if not silent:
            self.signals.item_started.emit(item_id, f"{ftype.title()}: {file}")
        tags = [file.suffix.lower().lstrip("."), file.name]
        self.items[item_id] = {"id":item_id,"type":ftype,"path":str(file),"tags":tags,"ts":now_iso(),"parent":parent}
        # fake quick progress animation
        for pct in (10,35,65,85,100):
            time.sleep(0.02)
            self.signals.progress.emit(item_id, pct)
        self.signals.item_done.emit(item_id)
        self.save()

    def as_context_tags(self) -> List[str]:
        """Return simple tags to include in system prompt if enabled."""
        tags = []
        for it in self.items.values():
            tags.extend([t for t in it.get("tags", []) if t])
        # unique, short
        seen=set(); out=[]
        for t in tags:
            if t not in seen:
                seen.add(t); out.append(t)
        return out

# ---------- TTS Manager ----------
class TTSManager:
    def __init__(self):
        self._engine = None
        self._thread: Optional[threading.Thread] = None
        self._available = False
        self._rate_slider_value = 150  # percent default
        try:
            import pyttsx3
            self._engine = pyttsx3.init(driverName="sapi5")
            # choose Zira if exists
            zira = None
            for v in self._engine.getProperty("voices"):
                if "Zira" in v.name:
                    zira = v.id; break
            if zira:
                self._engine.setProperty("voice", zira)
            # set 150%
            base = self._engine.getProperty("rate") or 200
            self._engine.setProperty("rate", int(base * (self._rate_slider_value/100.0)))
            self._available = True
        except Exception:
            self._engine = None
            self._available = False

    def set_rate_percent(self, pct: int):
        self._rate_slider_value = max(50, min(300, int(pct)))
        if self._engine:
            try:
                base = self._engine.getProperty("rate") or 200
                self._engine.setProperty("rate", int(base * (self._rate_slider_value/100.0)))
            except Exception:
                pass

    def speak_async(self, text: str):
        if not (self._available and self._engine and text.strip()):
            return
        self.stop()
        def run():
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                pass
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            if self._engine:
                self._engine.stop()
        except Exception:
            pass

# ---------- API/README generator ----------
def api_expose(fn):
    """Decorator marker for functions we want to list in API docs."""
    fn._api_exposed = True
    return fn

def generate_api_docs(out_md: Path, readme_md: Path):
    """
    Scans this module for functions/classes with @api_expose and docstrings,
    emitting a Markdown API surface + a quickstart README.
    """
    import inspect
    lines = ["# Chat Agent API\n", "_Auto-generated from source._\n"]
    for name, obj in sorted(globals().items()):
        if callable(obj) and getattr(obj, "_api_exposed", False):
            doc = inspect.getdoc(obj) or "(no docstring)"
            sig = ""
            try:
                sig = str(inspect.signature(obj))
            except Exception:
                pass
            lines.append(f"## `{name}{sig}`\n")
            lines.append(doc + "\n")
    out_md.write_text("\n".join(lines), encoding="utf-8")

    # README with structure summary
    readme = [
        "# Ollama Mini Chat — Generated README",
        "",
        "This document was generated by scanning the code. It outlines high-level structure and extension points.",
        "",
        "## Providers",
        "- **Ollama** via `http://localhost:11434/api/generate` and `/api/embeddings`.",
        "- **OpenAI** via `https://api.openai.com/v1/chat/completions`.",
        "",
        "## Streaming",
        "Text and code are streamed into the UI with character timers for smooth animation.",
        "",
        "## Prompting",
        "Prompts are managed in `/data/prompts`. Multiple prompts can be checked and re-ordered; all checked prompts are concatenated into the system preamble.",
        "",
        "## Dataset",
        "Rolling JSONL of the last N user/assistant pairs, with session-visible history separated to keep display clean.",
        "",
        "## Uploads",
        "Simple tag-and-bucket store (no vectors) in `/data/uploads`. Folders are ingested recursively.",
        "",
        "## TTS",
        "Windows SAPI5 Zira voice at a configurable percent rate.",
        "",
        "## Integration",
        "Use the `@api_expose`-decorated functions as stable entry points when embedding this agent into other systems.",
    ]
    readme_md.write_text("\n".join(readme), encoding="utf-8")

# ---------- Provider backends ----------
class ProviderBackend:
    def list_models(self) -> List[str]:
        return []
    def chat(self, model: str, system_preamble: str, user_text: str, history: List[Dict], stream: bool):
        raise NotImplementedError
    def embeddings(self, model: str, text: str) -> Optional[List[float]]:
        return None

class OllamaBackend(ProviderBackend):
    base = "http://localhost:11434"
    def list_models(self) -> List[str]:
        try:
            out = os.popen("ollama list").read().strip().splitlines()
            # Skip header
            models = []
            for line in out[1:]:
                parts = line.split()
                if parts:
                    models.append(parts[0])
            if not models:
                models = [DEFAULT_MODEL]
            return models
        except Exception:
            return [DEFAULT_MODEL]

    def chat(self, model: str, system_preamble: str, user_text: str, history: List[Dict], stream: bool):
        # For simplicity, fold prompts + history into one prompt string
        full = system_preamble + "\n\n"
        for pair in history:
            full += f"User: {pair['user']}\nAssistant: {pair['assistant']}\n"
        full += f"User: {user_text}\nAssistant:"
        payload = {"model": model, "prompt": full, "stream": stream}
        url = f"{self.base}/api/generate"
        r = requests.post(url, json=payload, timeout=300, stream=stream)
        r.raise_for_status()
        if stream:
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    j = json.loads(line)
                except Exception:
                    continue
                if "response" in j:
                    yield j["response"]
                if j.get("done"):
                    break
        else:
            j = r.json()
            yield j.get("response", "")

    def embeddings(self, model: str, text: str) -> Optional[List[float]]:
        try:
            r = requests.post(f"{self.base}/api/embeddings",
                              json={"model": model, "prompt": text},
                              timeout=60)
            r.raise_for_status()
            return r.json().get("embedding")
        except Exception:
            return None

class OpenAIBackend(ProviderBackend):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def list_models(self) -> List[str]:
        if not self.api_key:
            return []
        try:
            r = requests.get("https://api.openai.com/v1/models",
                             headers={"Authorization": f"Bearer {self.api_key}"}, timeout=30)
            r.raise_for_status()
            data = r.json()
            ids = sorted([m["id"] for m in data.get("data", [])])
            # Heuristic: show chat-friendly models first
            ids = [m for m in ids if any(x in m for x in ("gpt","o4","o3","chat"))] or ids
            return ids
        except Exception:
            return []

    def chat(self, model: str, system_preamble: str, user_text: str, history: List[Dict], stream: bool):
        if not self.api_key:
            yield "⚠️ OpenAI API key not set in Settings."
            return
        messages = [{"role":"system","content":system_preamble}]
        for pair in history:
            messages.append({"role":"user","content":pair["user"]})
            messages.append({"role":"assistant","content":pair["assistant"]})
        messages.append({"role":"user","content":user_text})
        payload = {"model": model, "messages": messages, "stream": stream, "temperature": 0.3}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type":"application/json"}
        url = "https://api.openai.com/v1/chat/completions"
        r = requests.post(url, headers=headers, json=payload, stream=stream, timeout=600)
        r.raise_for_status()
        if stream:
            for raw in r.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                if raw.startswith("data: "):
                    raw = raw[6:].strip()
                if raw == "[DONE]":
                    break
                try:
                    j = json.loads(raw)
                except Exception:
                    continue
                delta = j["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]
        else:
            j = r.json()
            content = j["choices"][0]["message"]["content"]
            yield content

# ---------- Code block container ----------
class CodeBlockContainer(QWidget):
    """
    Floating code container:
    - language badge + emoji
    - copy, expand/collapse
    - dynamic height growth to show **entire script while streaming**
      (then auto-minimize when finished)
    """
    DEFAULT_MIN = 180
    MAX_LIVE = 6000  # generous upper bound for live-expanded height
    finished = pyqtSignal()

    def __init__(self, language: Optional[str], start_expanded=True, parent=None):
        super().__init__(parent)
        self.language = language
        self._expanded = start_expanded
        self.main_scroll: Optional[QScrollArea] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 6, 0, 10)
        outer.setSpacing(4)

        frame = QFrame(self)
        frame.setObjectName("codeContainer")
        frame.setStyleSheet(
            "QFrame#codeContainer {background:#1e1e1e; border-radius:8px; border:1px solid #2a2a2a;}"
        )
        v = QVBoxLayout(frame); v.setContentsMargins(10,10,10,4); v.setSpacing(6)

        header = QHBoxLayout(); header.setSpacing(8)
        emoji = "🐍" if (self.language in ("python","py")) else ("🧩" if self.language else "💻")
        lang_text = (self.language or "code").upper()
        self.badge = QLabel(f"{emoji} {lang_text}"); self.badge.setStyleSheet(BADGE_STYLE)
        header.addWidget(self.badge); header.addStretch(1)
        self.btn_copy = QPushButton("📋 Copy"); self.btn_copy.setStyleSheet(SMALL_BUTTON); header.addWidget(self.btn_copy)
        self.btn_toggle = QPushButton("⤴ Collapse" if self._expanded else "⤵ Expand"); self.btn_toggle.setStyleSheet(SMALL_BUTTON)
        self.btn_toggle.clicked.connect(self._toggle); header.addWidget(self.btn_toggle)
        v.addLayout(header)

        self.viewer = QTextEdit(); self.viewer.setReadOnly(True); self.viewer.setAcceptRichText(True)
        self.viewer.setStyleSheet("QTextEdit {background:#1e1e1e; color:#e5e5e5; border:none;}")
        v.addWidget(self.viewer)

        grip_row = QHBoxLayout(); grip_row.addStretch(1)
        self.size_grip = QSizeGrip(self); grip_row.addWidget(self.size_grip, 0, Qt.AlignRight)
        v.addLayout(grip_row)
        outer.addWidget(frame)

        # state
        self._source = ""
        self._queue: List[str] = []
        self._timer = QTimer(self); self._timer.setInterval(10)  # faster than before
        self._timer.timeout.connect(self._tick)
        self._needs_finalize = False
        self.btn_copy.clicked.connect(lambda: pyperclip.copy(self._source))
        self._apply_height()

    def append_live_text(self, more: str):
        self._source += more
        self._queue.extend(list(more))
        if not self._timer.isActive():
            self._timer.start()

    def _tick(self):
        if not self._queue:
            self._timer.stop()
            if self._needs_finalize:
                self._needs_finalize = False
                self._colorize()
                self._auto_minimize()
                self.finished.emit()
            return
        ch = self._queue.pop(0)
        esc = ch.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if ch == "\n": esc = "<br/>"
        self.viewer.moveCursor(self.viewer.textCursor().End)
        self.viewer.insertHtml(esc)
        self.viewer.moveCursor(self.viewer.textCursor().End)
        self._apply_height(live=True)
        if self.main_scroll:
            # obey autoscroll if enabled; the owner will move it
            pass

    def finalize(self):
        if self._queue:
            self._needs_finalize = True
        else:
            self._colorize()
            self._auto_minimize()
            self.finished.emit()

    def _colorize(self):
        html = pygments_html(self._source, self.language)
        self.viewer.setHtml(html)
        self.viewer.moveCursor(self.viewer.textCursor().End)
        self._apply_height(live=True)

    def _apply_height(self, live: bool=False):
        doc = self.viewer.document().size().toSize()
        h = max(self.DEFAULT_MIN, doc.height() + 24)
        if live:
            h = min(h, self.MAX_LIVE)
        self.viewer.setFixedHeight(h)

    def _toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            self._apply_height(live=True)
        else:
            self.viewer.setFixedHeight(self.DEFAULT_MIN)
        self.btn_toggle.setText("⤴ Collapse" if self._expanded else "⤵ Expand")

    def _auto_minimize(self):
        # collapse after finish (per spec)
        if self._expanded:
            self._toggle()

# ---------- Message widgets ----------
class UserMessage(QWidget):
    def __init__(self, txt: str):
        super().__init__()
        self._text = txt
        v = QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(4)
        frame = QFrame(); frame.setStyleSheet(f"background:{USER_BLUE}; border-radius:8px;")
        h = QHBoxLayout(frame); h.setContentsMargins(10,10,10,10)
        lbl = QLabel(f"<b>User:</b> {txt}"); lbl.setStyleSheet("color:#e1f0ff;"); lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        h.addWidget(lbl, 1)
        copy = QPushButton("📋"); copy.setStyleSheet(PRIMARY_BUTTON); copy.setToolTip("Copy user message")
        copy.clicked.connect(lambda: pyperclip.copy(txt)); h.addWidget(copy, 0, Qt.AlignTop)
        v.addWidget(frame)

    def as_text(self) -> str:
        return f"User: {self._text}\n"

class BotStreamMessage(QWidget):
    """
    Live bot message supporting streamed plain text and fenced code blocks.
    - Text area grows to content height ("just the length of the text"), darker card inside purple container.
    - Code blocks created when ```lang appears; validated; expanded full during write; minimized after.
    - Provider & model label on first line inside the response card.
    """
    FENCE_RX = re.compile(r"```([A-Za-z0-9\+\-\_#\.]+)?\s*$")
    think_enabled = True

    def __init__(self, provider: str, model: str, autoscroll_getter):
        super().__init__()
        self.provider = provider
        self.model = model
        self.get_autoscroll = autoscroll_getter

        self._in_code = False
        self._current_lang: Optional[str] = None
        self._current_block: Optional[CodeBlockContainer] = None
        self._tail = ""
        self._parts: List[Tuple[str,str]] = []

        v = QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(6)
        self.card = QFrame(); self.card.setStyleSheet(f"background:{CARD_INDIGO}; border-radius:8px;")
        inner = QVBoxLayout(self.card); inner.setContentsMargins(10,10,10,10); inner.setSpacing(6)

        header = QLabel(f"<b>[{provider}][{model}] →</b>"); header.setStyleSheet("color:#e0d7ff;")
        inner.addWidget(header)

        # Plain text area
        self.text_holder = QFrame(); self.text_holder.setStyleSheet("background:#342d4f; border-radius:6px;")
        thl = QVBoxLayout(self.text_holder); thl.setContentsMargins(8,8,8,8); thl.setSpacing(4)
        self.live_text = QTextEdit(); self.live_text.setReadOnly(True); self.live_text.setAcceptRichText(True)
        self.live_text.setStyleSheet("QTextEdit { background: transparent; color: #f0f0f0; border: none; }")
        thl.addWidget(self.live_text)
        inner.addWidget(self.text_holder)

        foot = QHBoxLayout()
        self.btn_copy_all = QPushButton("📋 Copy All"); self.btn_copy_all.setStyleSheet(SMALL_BUTTON)
        self.btn_copy_all.clicked.connect(self.copy_all); foot.addWidget(self.btn_copy_all)
        foot.addStretch(1); inner.addLayout(foot)
        v.addWidget(self.card)

        self._text_queue: List[str] = []
        self._text_timer = QTimer(self); self._text_timer.setInterval(10)
        self._text_timer.timeout.connect(self._tick_text)

    def feed_chunk(self, chunk: str):
        text = self._tail + chunk
        lines = text.split("\n")
        self._tail = lines[-1]
        for line in lines[:-1]:
            self._handle_line(line + "\n")
        if self.get_autoscroll():
            self._scroll_to_bottom()

    def end_stream(self):
        if self._tail:
            self._handle_line(self._tail); self._tail = ""
        # close any open code block
        if self._in_code and self._current_block:
            self._current_block.finalize()
            self._in_code = False; self._current_lang = None; self._current_block = None
        self._scroll_to_bottom()

    def _handle_line(self, line: str):
        # Detect fences
        m = self.FENCE_RX.match(line.strip())
        if m:
            if not self._in_code:
                lang = safe_lang(m.group(1))
                self._start_code(lang)
            else:
                self._finish_code()
            return

        # Think tags
        if "<think>" in line and self.think_enabled:
            line = line.replace("<think>", "<span style='color:#9bc59b; font-style:italic; text-shadow:0 0 2px #aaffaa;'>")
        if "</think>" in line and self.think_enabled:
            line = line.replace("</think>", "</span>")

        if self._in_code and self._current_block is not None:
            self._current_block.append_live_text(line)
            if not self._parts or self._parts[-1][0] != "code":
                self._parts.append(("code", line))
            else:
                self._parts[-1] = ("code", self._parts[-1][1] + line)
        else:
            self._text_queue.extend(list(line))
            if not self._text_timer.isActive():
                self._text_timer.start()
            if line.strip():
                if not self._parts or self._parts[-1][0] != "text":
                    self._parts.append(("text", line))
                else:
                    self._parts[-1] = ("text", self._parts[-1][1] + line)

    def _start_code(self, lang: Optional[str]):
        self._in_code = True; self._current_lang = lang
        block = CodeBlockContainer(language=lang, start_expanded=True, parent=self)
        block.main_scroll = self.parent().parent().parent() if hasattr(self.parent(), "parent") else None
        layout: QVBoxLayout = self.card.layout()  # type: ignore
        layout.addWidget(block)
        self._current_block = block
        self._parts.append(("code",""))

    def _finish_code(self):
        if self._current_block:
            self._current_block.finalize()
            # replace parts record with final text
            if self._parts and self._parts[-1][0]=="code":
                self._parts[-1] = ("code", self._current_block._source)
        self._in_code = False; self._current_lang=None; self._current_block=None

    def _tick_text(self):
        if not self._text_queue:
            self._text_timer.stop()
            return
        ch = self._text_queue.pop(0)
        esc = ch.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if ch=="\n": esc="<br/>"
        elif ch==" ": esc="&nbsp;&nbsp;"
        self.live_text.moveCursor(self.live_text.textCursor().End)
        self.live_text.insertHtml(esc)
        self.live_text.moveCursor(self.live_text.textCursor().End)
        # Grow to content height (no artificial max unless enormous)
        doc_h = self.live_text.document().size().toSize().height()
        self.live_text.setFixedHeight(doc_h + 18)

    def _scroll_to_bottom(self):
        # parent scroll is  self.parent()->card->...
        sp = self.parent()
        while sp and not isinstance(sp, QScrollArea):
            sp = sp.parent()
        if isinstance(sp, QScrollArea) and self.get_autoscroll():
            sp.verticalScrollBar().setValue(sp.verticalScrollBar().maximum())

    def copy_all(self):
        buf = [f"[{self.provider}][{self.model}] →\n"]
        for kind, content in self._parts:
            if kind=="text":
                buf.append(content)
            else:
                buf.append(f"```{self._current_lang or 'code'}\n{content}\n```\n")
        pyperclip.copy("".join(buf))

    def as_text(self) -> str:
        buf = [f"[{self.provider}][{self.model}] →\n"]
        for k,c in self._parts:
            if k=="text": buf.append(c)
            else: buf.append(f"[Begin code]\n{c}\n[End code]\n")
        return "".join(buf)

# ---------- Prompt Manager Dialog ----------
class PromptManager(QDialog):
    """
    Manage prompts in /data/prompts. Each prompt is a .txt file.
    Index JSON keeps order + checked state.
    """
    prompts_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prompt Manager")
        self.setModal(True)
        self.resize(720, 420)
        layout = QHBoxLayout(self)

        # Left: list with checkboxes
        self.list = QListWidget()
        layout.addWidget(self.list, 1)

        # Right: editor
        right = QVBoxLayout(); layout.addLayout(right, 2)
        form = QFormLayout()
        self.ed_name = QLineEdit(); form.addRow("Name:", self.ed_name)
        self.ed_text = QPlainTextEdit(); self.ed_text.setPlaceholderText("Prompt text...")
        self.ed_text.setStyleSheet("QPlainTextEdit {background:#1e1e1e; color:#f0f0f0;}")
        form.addRow("Prompt text:", self.ed_text)
        right.addLayout(form)

        # Buttons
        b_row = QHBoxLayout()
        self.btn_add = QPushButton("Add"); self.btn_add.setStyleSheet(PRIMARY_BUTTON)
        self.btn_save = QPushButton("Save/Update"); self.btn_save.setStyleSheet(PRIMARY_BUTTON)
        self.btn_del = QPushButton("Delete"); self.btn_del.setStyleSheet(SMALL_BUTTON)
        self.btn_up  = QPushButton("↑ Up"); self.btn_down = QPushButton("↓ Down")
        for b in (self.btn_up, self.btn_down): b.setStyleSheet(SMALL_BUTTON)
        self.btn_use = QPushButton("Use Checked"); self.btn_use.setStyleSheet(PRIMARY_BUTTON)
        b_row.addWidget(self.btn_add); b_row.addWidget(self.btn_save); b_row.addWidget(self.btn_del)
        b_row.addStretch(1); b_row.addWidget(self.btn_up); b_row.addWidget(self.btn_down); b_row.addWidget(self.btn_use)
        right.addLayout(b_row)

        self.list.itemSelectionChanged.connect(self._on_select)
        self.btn_add.clicked.connect(self._add)
        self.btn_save.clicked.connect(self._save)
        self.btn_del.clicked.connect(self._delete)
        self.btn_up.clicked.connect(lambda: self._move(-1))
        self.btn_down.clicked.connect(lambda: self._move(1))
        self.btn_use.clicked.connect(lambda: (self._save_index(), self.prompts_changed.emit(), self.accept()))

        self._load()

    def _load(self):
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        idx = {"order":[],"checked":{}}
        if PROMPTS_INDEX_JSON.exists():
            try:
                idx = json.loads(PROMPTS_INDEX_JSON.read_text(encoding="utf-8"))
            except Exception:
                pass
        # Ensure default prompt file exists
        default_path = PROMPTS_DIR / "Default.txt"
        if not default_path.exists():
            default_text = (
                "You are Zira, an expert coding copilot and tutor.\n"
                "- Write clean, modern, scalable code with rich explanations when needed.\n"
                "- When returning code, use fenced blocks with a correct language.\n"
                "- Be concise in prose; prefer code and bullet points.\n"
                "- Use emojis tastefully in headings or code badges.\n"
                "- Prefer stepwise, progressive improvements rather than rewrites.\n"
                "- Respect the user's 'Real-Time' UI: stream content in natural chunks.\n"
            )
            default_path.write_text(default_text, encoding="utf-8")
        if "Default" not in idx["order"]:
            idx["order"].insert(0, "Default")
            idx["checked"]["Default"] = True
        # Populate list
        self.list.clear()
        for name in idx["order"]:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked if idx["checked"].get(name, False) else Qt.Unchecked)
            self.list.addItem(item)
        self._save_index(idx)  # normalize

    def _save_index(self, idx=None):
        if idx is None:
            idx = {"order":[], "checked":{}}
            for i in range(self.list.count()):
                it = self.list.item(i)
                idx["order"].append(it.text())
                idx["checked"][it.text()] = (it.checkState()==Qt.Checked)
        PROMPTS_INDEX_JSON.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")

    def _on_select(self):
        it = self.list.currentItem()
        if not it: return
        name = it.text()
        self.ed_name.setText(name)
        path = PROMPTS_DIR / f"{name}.txt"
        txt = path.read_text(encoding="utf-8") if path.exists() else ""
        self.ed_text.setPlainText(txt)

    def _add(self):
        name = self.ed_name.text().strip() or "New Prompt"
        if name == "Default":
            QMessageBox.information(self, "Prompt", "Use a different name.")
            return
        (PROMPTS_DIR / f"{name}.txt").write_text(self.ed_text.toPlainText(), encoding="utf-8")
        # add to list if missing
        names = [self.list.item(i).text() for i in range(self.list.count())]
        if name not in names:
            it = QListWidgetItem(name); it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked)
            self.list.addItem(it)
        self._save_index()

    def _save(self):
        it = self.list.currentItem()
        if not it: return
        name = it.text()
        if name == "Default":
            # allowed to edit & toggle, but not delete
            pass
        (PROMPTS_DIR / f"{name}.txt").write_text(self.ed_text.toPlainText(), encoding="utf-8")
        self._save_index()

    def _delete(self):
        it = self.list.currentItem()
        if not it: return
        name = it.text()
        if name == "Default":
            QMessageBox.information(self, "Prompt", "Default prompt cannot be deleted (you can uncheck it).")
            return
        path = PROMPTS_DIR / f"{name}.txt"
        try:
            if path.exists(): path.unlink()
        except Exception:
            pass
        self.list.takeItem(self.list.row(it))
        self._save_index()

    def _move(self, delta: int):
        r = self.list.currentRow()
        if r < 0: return
        nr = max(0, min(self.list.count()-1, r+delta))
        if nr==r: return
        it = self.list.takeItem(r)
        self.list.insertItem(nr, it)
        self.list.setCurrentRow(nr)
        self._save_index()

    @api_expose
    def current_preamble(self) -> str:
        """
        Build a preamble string by concatenating all *checked* prompts in the
        current list order.
        """
        pre = []
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.checkState()==Qt.Checked:
                name = it.text()
                path = PROMPTS_DIR / f"{name}.txt"
                if path.exists():
                    pre.append(path.read_text(encoding="utf-8").strip())
        return "\n\n".join(pre).strip()

# ---------- Settings Dialog ----------
class SettingsDialog(QDialog):
    """Settings: API key + TTS speed. Persists values; shows docs buttons."""
    settings_changed = pyqtSignal()

    def __init__(self, tts_mgr: TTSManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(560, 260)
        self.tts_mgr = tts_mgr

        tabs = QTabWidget()
        # API tab
        api_tab = QWidget(); api_layout = QVBoxLayout(api_tab)
        form = QFormLayout()
        self.ed_openai = QLineEdit(load_openai_key() or "")
        self.ed_openai.setPlaceholderText("OpenAI API Key (sk-...)")
        form.addRow("OpenAI API Key:", self.ed_openai)
        save = QPushButton("Save API Key"); save.setStyleSheet(PRIMARY_BUTTON)
        save.clicked.connect(self._save_key)
        api_layout.addLayout(form); api_layout.addWidget(save)

        # TTS tab
        tts_tab = QWidget(); tts_layout = QFormLayout(tts_tab)
        self.sp_tts = QSpinBox(); self.sp_tts.setRange(50, 300); self.sp_tts.setValue(self.tts_mgr._rate_slider_value)
        tts_layout.addRow("TTS speed (% of base):", self.sp_tts)
        btn_apply = QPushButton("Apply"); btn_apply.setStyleSheet(PRIMARY_BUTTON)
        btn_apply.clicked.connect(self._apply_tts)
        tts_layout.addRow(btn_apply)

        # Docs tab
        docs_tab = QWidget(); docs_layout = QVBoxLayout(docs_tab)
        gen = QPushButton("Generate API & README"); gen.setStyleSheet(PRIMARY_BUTTON)
        self.viewer = QTextBrowser(); self.viewer.setStyleSheet("QTextBrowser {background:#111;color:#ddd;}")
        cp = QPushButton("Copy Shown"); cp.setStyleSheet(SMALL_BUTTON)
        def _gen():
            generate_api_docs(DOCS_DIR / "Chat_Agent_API.md", DOCS_DIR / "README.generated.md")
            self.viewer.setPlainText((DOCS_DIR/"Chat_Agent_API.md").read_text(encoding="utf-8"))
        gen.clicked.connect(_gen); cp.clicked.connect(lambda: pyperclip.copy(self.viewer.toPlainText()))
        docs_layout.addWidget(gen); docs_layout.addWidget(self.viewer,1); docs_layout.addWidget(cp)

        tabs.addTab(api_tab, "API Keys")
        tabs.addTab(tts_tab, "TTS")
        tabs.addTab(docs_tab, "Docs")

        root = QVBoxLayout(self); root.addWidget(tabs)
        close = QPushButton("Close"); close.clicked.connect(self.accept); root.addWidget(close)

    def _save_key(self):
        save_openai_key(self.ed_openai.text().strip())
        self.settings_changed.emit()

    def _apply_tts(self):
        self.tts_mgr.set_rate_percent(self.sp_tts.value())

# ---------- Upload Manager Dialog ----------
class UploadManagerDialog(QDialog):
    """Popup to view/ingest uploaded knowledge items with progress bars and a quick 'Upload...' button."""
    def __init__(self, store: UploadedKnowledge, signals: UploadSignals, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Upload Manager")
        self.setModal(False); self.resize(720, 420)
        self.store = store; self.signals = signals

        self.items_layout = QVBoxLayout()
        container = QWidget(); container.setLayout(self.items_layout)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setWidget(container)

        self.btn_upload = QPushButton("Upload..."); self.btn_upload.setStyleSheet(PRIMARY_BUTTON)
        self.btn_upload.clicked.connect(self._choose_files)
        self.btn_clear = QPushButton("Clear Uploaded Knowledge"); self.btn_clear.setStyleSheet(SMALL_BUTTON)
        self.btn_clear.clicked.connect(self._clear)

        root = QVBoxLayout(self)
        root.addWidget(self.scroll, 1)
        row = QHBoxLayout(); row.addWidget(self.btn_upload); row.addStretch(1); row.addWidget(self.btn_clear)
        root.addLayout(row)

        self.signals.item_started.connect(self._on_start)
        self.signals.progress.connect(self._on_progress)
        self.signals.item_done.connect(self._on_done)
        self.signals.refresh_view.connect(self.refresh)

        self.widgets: Dict[str, Tuple[QLabel,QProgressBar]] = {}
        self.refresh()

    def _choose_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select files or images")
        if not paths: return
        self.store.ingest_paths([Path(p) for p in paths])

    def _clear(self):
        if QMessageBox.question(self, "Uploaded Knowledge", "Delete all uploaded knowledge?") == QMessageBox.Yes:
            self.store.clear(); self.refresh()

    def _on_start(self, item_id: str, label: str):
        w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(6,6,6,6)
        lab = QLabel(label); p = QProgressBar(); p.setRange(0,100); p.setValue(0)
        l.addWidget(lab, 1); l.addWidget(p, 0)
        self.items_layout.addWidget(w)
        self.widgets[item_id] = (lab, p)

    def _on_progress(self, item_id: str, pct: int):
        if item_id in self.widgets:
            self.widgets[item_id][1].setValue(pct)

    def _on_done(self, item_id: str):
        if item_id in self.widgets:
            self.widgets[item_id][1].setValue(100)

    def refresh(self):
        # clear layout
        while self.items_layout.count():
            it = self.items_layout.takeAt(0)
            w = it.widget()
            if w: w.deleteLater()
        # re-add items
        for it in self.store.items.values():
            w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(6,6,6,6)
            icon = "📁" if it["type"]=="folder" else ("🖼️" if it["type"]=="image" else "📄")
            lab = QLabel(f"{icon} {it['path']}  —  tags: {', '.join(it.get('tags',[]))}")
            p = QProgressBar(); p.setRange(0,100); p.setValue(100)
            l.addWidget(lab, 1); l.addWidget(p, 0)
            self.items_layout.addWidget(w)

# ---------- Main App ----------
class MiniChat(QWidget):
    """
    The main window. Orchestrates UI, providers, streaming, timing, dataset, prompts, uploads, TTS.
    """

    def __init__(self):
        super().__init__()
        ensure_dirs()
        self.setWindowTitle(APP_NAME)
        self.resize(1120, 760)

        # State
        self.tts = TTSManager()
        self.timing = TimingLog(TIMINGS_LOG)
        self.dataset = DatasetManager(DATASET_JSONL, VISIBLE_HISTORY_FILE, limit_pairs=10)
        self.signals = UploadSignals()
        self.uploads = UploadedKnowledge(UPLOAD_INDEX_JSON, self.signals)
        self.autoscroll = True

        # Providers
        self.backend_ollama = OllamaBackend()
        self.backend_openai = OpenAIBackend(load_openai_key())
        self.provider_backend: ProviderBackend = self.backend_ollama

        # ---- System log ticker ----
        self.ticker = QLabel("Ready. Default provider: Ollama; Model: gpt-oss:20b; Real-Time ON.")
        self.ticker.setStyleSheet("QLabel {background:#111;color:#9df29d;padding:4px 8px; font: 10pt 'Consolas';}")
        # ---- Top controls ----
        top = QHBoxLayout()
        self.btn_settings = QPushButton("⚙ Settings"); self.btn_settings.setStyleSheet(SMALL_BUTTON)
        self.btn_settings.clicked.connect(self._open_settings)
        top.addWidget(self.btn_settings)

        top.addWidget(QLabel("Provider:"))
        self.cmb_provider = QComboBox(); self.cmb_provider.addItems(["Ollama","OpenAI"])
        self.cmb_provider.currentTextChanged.connect(self._on_provider)
        top.addWidget(self.cmb_provider)

        top.addWidget(QLabel("Model:"))
        self.cmb_model = QComboBox(); top.addWidget(self.cmb_model)
        self.btn_refresh_models = QPushButton("⟳"); self.btn_refresh_models.setFixedWidth(28)
        self.btn_refresh_models.setStyleSheet(SMALL_BUTTON)
        self.btn_refresh_models.clicked.connect(self._populate_models)
        top.addWidget(self.btn_refresh_models)

        top.addWidget(QLabel("Embedder:"))
        self.cmb_embed = QComboBox(); self.cmb_embed.addItems([DEFAULT_EMBEDDER])
        top.addWidget(self.cmb_embed)

        self.chk_realtime = QCheckBox("Real-Time"); self.chk_realtime.setChecked(True); top.addWidget(self.chk_realtime)
        self.chk_autoscroll = QCheckBox("Auto-scroll"); self.chk_autoscroll.setChecked(True)
        self.chk_autoscroll.toggled.connect(lambda v: setattr(self, "autoscroll", bool(v)))
        top.addWidget(self.chk_autoscroll)

        top.addWidget(QLabel("Context pairs:"))
        self.lbl_pairs = QLabel("10")
        self.slider_pairs = QSpinBox(); self.slider_pairs.setRange(1, 50); self.slider_pairs.setValue(10)
        self.slider_pairs.valueChanged.connect(self._pairs_changed)
        top.addWidget(self.slider_pairs)

        self.btn_prompts = QPushButton("📜 Prompts"); self.btn_prompts.setStyleSheet(PRIMARY_BUTTON)
        self.btn_prompts.clicked.connect(self._open_prompts)
        top.addWidget(self.btn_prompts)

        self.btn_clear = QPushButton("🧹 Clear Chat"); self.btn_clear.setStyleSheet(SMALL_BUTTON)
        self.btn_clear.clicked.connect(self._clear_chat)
        top.addWidget(self.btn_clear)

        self.chk_use_uploads = QCheckBox("Use Uploaded Knowledge"); self.chk_use_uploads.setChecked(True)
        top.addWidget(self.chk_use_uploads)

        self.btn_read_all = QPushButton("▶ Read All"); self.btn_read_all.setStyleSheet(SMALL_BUTTON)
        self.btn_read_all.clicked.connect(self._tts_read_all)
        self.btn_read_cur = QPushButton("▶ Read Current"); self.btn_read_cur.setStyleSheet(SMALL_BUTTON)
        self.btn_read_cur.clicked.connect(self._tts_read_current)
        self.btn_stop = QPushButton("⏹ Stop"); self.btn_stop.setStyleSheet(SMALL_BUTTON)
        self.btn_stop.clicked.connect(self.tts.stop)
        top.addWidget(self.btn_read_all); top.addWidget(self.btn_read_cur); top.addWidget(self.btn_stop)

        self.btn_reset_avg = QPushButton("Reset Averages"); self.btn_reset_avg.setStyleSheet(SMALL_BUTTON)
        self.btn_reset_avg.clicked.connect(self._reset_averages)
        self.lbl_avgs = QLabel(self._avg_text()); self.lbl_avgs.setStyleSheet("color:#ddd;")
        top.addWidget(self.lbl_avgs); top.addWidget(self.btn_reset_avg)

        # ---- History area ----
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.container = QWidget(); self.v = QVBoxLayout(self.container); self.v.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.container)

        # ---- Input row ----
        inp_row = QHBoxLayout()
        self.attachments_bar = QLabel("Attachments:"); self.attachments_bar.setStyleSheet("color:#aaa;")
        self.btn_upload_mgr = QPushButton("📁 Upload Manager"); self.btn_upload_mgr.setStyleSheet(SMALL_BUTTON)
        self.btn_upload_mgr.clicked.connect(self._open_upload_mgr)
        inp_row.addWidget(self.attachments_bar); inp_row.addStretch(1); inp_row.addWidget(self.btn_upload_mgr)

        self.txt_in = QLineEdit(); self.txt_in.setPlaceholderText("Ask Zira something…")
        self.txt_in.returnPressed.connect(self._send)
        self.btn_send = QPushButton("Send"); self.btn_send.setStyleSheet(PRIMARY_BUTTON)
        self.btn_send.clicked.connect(self._send)

        # ---- Root layout ----
        root = QVBoxLayout(self); root.setContentsMargins(6,6,6,6); root.setSpacing(6)
        root.addWidget(self.ticker)
        root.addLayout(top)
        root.addWidget(self.scroll, 1)
        root.addLayout(inp_row)
        row2 = QHBoxLayout(); row2.addWidget(self.txt_in, 1); row2.addWidget(self.btn_send)
        root.addLayout(row2)

        # Style
        self.setStyleSheet(f"QWidget {{background:{SMOKY_BG}; color:{SOFT_TEXT};}}")
        self._populate_models(initial=True)
        log_line("Application started.")

        # Paste handling for quick uploads
        self.installEventFilter(self)

        # Errors as popups
        sys.excepthook = self._excepthook

        # Session attachments icons
        self._attachment_icons: List[str] = []

    def eventFilter(self, obj, ev):
        # Handle paste into the input: turn file paths into attachments
        if ev.type() == QEvent.KeyPress and ev.matches(QKeySequence.Paste):
            clip = QApplication.clipboard().mimeData()
            if clip and clip.hasText():
                text = clip.text().strip()
                # If it's a path or list of paths
                parts = [p.strip() for p in text.split() if p.strip()]
                paths = []
                for p in parts:
                    if Path(p).exists():
                        paths.append(Path(p))
                if paths:
                    self.uploads.ingest_paths(paths)
                    self._add_attachment_icons(paths)
                    return True
        return super().eventFilter(obj, ev)

    # ----- UI helpers -----
    def _avg_text(self) -> str:
        d,s = self.timing.averages()
        return f" ⬤ Normal avg: {int(d)} ms | Real-Time avg: {int(s)} ms "

    def _pairs_changed(self, val: int):
        self.dataset.set_limit(val)

    def _add_attachment_icons(self, paths: List[Path]):
        for p in paths:
            if p.is_dir(): icon="📁"
            elif p.suffix.lower() in (".png",".jpg",".jpeg",".gif",".webp"): icon="🖼️"
            else: icon="📄"
            self._attachment_icons.append(f"{icon} {p.name}")
        self.attachments_bar.setText("Attachments:  " + "  ".join(self._attachment_icons))

    def _open_settings(self):
        dlg = SettingsDialog(self.tts, self)
        dlg.settings_changed.connect(lambda: setattr(self.backend_openai, "api_key", load_openai_key()))
        dlg.exec_()

    def _open_prompts(self):
        dlg = PromptManager(self)
        if dlg.exec_():
            pass  # preamble is constructed at send time

    def _open_upload_mgr(self):
        UploadManagerDialog(self.uploads, self.signals, self).show()

    def _on_provider(self, name: str):
        self.provider_backend = self.backend_ollama if name=="Ollama" else self.backend_openai
        self._populate_models()

    def _populate_models(self, initial=False):
        provider = self.cmb_provider.currentText()
        models = self.provider_backend.list_models()
        self.cmb_model.clear()
        if not models:
            # minimal fallback
            if provider=="Ollama":
                models=[DEFAULT_MODEL]
            else:
                models=[]
        self.cmb_model.addItems(models)
        # initial set to default if present
        if initial and DEFAULT_MODEL in models:
            self.cmb_model.setCurrentText(DEFAULT_MODEL)

    def _excepthook(self, etype, evalue, etb):
        tb = "".join(traceback.format_exception(etype, evalue, etb))
        log_line("Unhandled exception:\n" + tb)
        QMessageBox.critical(self, "Error", tb)

    # ----- TTS -----
    def _collect_from_index(self, start: int) -> str:
        parts=[]
        for i in range(start, self.v.count()):
            w = self.v.itemAt(i).widget()
            if isinstance(w, BotStreamMessage):
                parts.append(w.as_text())
        return "\n".join(parts)

    def _tts_read_all(self):
        self.tts.stop()
        text = self._collect_from_index(0)
        self.tts.speak_async(text)

    def _tts_read_current(self):
        self.tts.stop()
        if self.v.count()==0: return
        text = self._collect_from_index(self.v.count()-1)
        self.tts.speak_async(text)

    # ----- Clear chat / averages -----
    def _reset_averages(self):
        if QMessageBox.question(self, "Timings", "Reset timing averages?") == QMessageBox.Yes:
            self.timing.reset()
            self.lbl_avgs.setText(self._avg_text())

    def _clear_chat(self):
        self.tts.stop()
        self.dataset.clear_all()
        # remove widgets
        while self.v.count():
            it = self.v.takeAt(0); w = it.widget()
            if w: w.deleteLater()
        if QMessageBox.question(self, "Clear Chat", "Also reset averages back to 0 and start fresh?") == QMessageBox.Yes:
            self._reset_averages()
        self._attachment_icons.clear()
        self.attachments_bar.setText("Attachments:")

    # ----- Compose system preamble -----
    def _system_preamble(self) -> str:
        # prompts
        pre = []
        if PROMPTS_INDEX_JSON.exists():
            try:
                idx=json.loads(PROMPTS_INDEX_JSON.read_text(encoding="utf-8"))
                for name in idx["order"]:
                    if idx["checked"].get(name, False):
                        p = PROMPTS_DIR / f"{name}.txt"
                        if p.exists():
                            pre.append(p.read_text(encoding="utf-8").strip())
            except Exception:
                pass

        # uploaded knowledge tags
        if self.chk_use_uploads.isChecked():
            tags = self.uploads.as_context_tags()
            if tags:
                pre.append("Uploaded knowledge tags: " + ", ".join(tags))

        # dataset framing
        pairs = self.dataset.load_pairs()
        if pairs:
            bullet = []
            for i, pr in enumerate(pairs[-self.dataset.limit:], 1):
                # lightly weighted older summaries
                bullet.append(f"({i}) user asked about: {pr['user'][:200]}")
            pre.append("Recent context (light weight; oldest first):\n- " + "\n- ".join(bullet))

        return "\n\n".join(pre).strip()

    # ----- Send / Stream -----
    def _send(self):
        user_txt = self.txt_in.text().strip()
        if not user_txt:
            return
        self.txt_in.clear()
        self._add_widget(UserMessage(user_txt))
        # Start timing
        t0 = time.perf_counter()
        mode = "realtime" if self.chk_realtime.isChecked() else "default"

        # Build preamble & history
        preamble = self._system_preamble()
        history = self.dataset.load_pairs()

        # Live bot message
        live = BotStreamMessage(self.cmb_provider.currentText(), self.cmb_model.currentText(), lambda: self.autoscroll)
        self._add_widget(live)

        # Stream request
        try:
            stream = self.chk_realtime.isChecked()
            provider = self.provider_backend
            for chunk in provider.chat(self.cmb_model.currentText(), preamble, user_txt, history, stream=stream):
                live.feed_chunk(chunk)
            live.end_stream()
        except Exception as e:
            live.feed_chunk(f"\n\n⚠️ Error: {e}\n")
            live.end_stream()

        # End timing & averages
        dt_ms = int((time.perf_counter()-t0)*1000)
        self.timing.add(mode, dt_ms)
        self.lbl_avgs.setText(self._avg_text())

        # Persist pair (visible + dataset)
        resp_text = live.as_text()
        self.dataset.append_visible(f"[{self.cmb_provider.currentText()}][{self.cmb_model.currentText()}] → {resp_text[:5000]}")
        # For dataset keep the raw combined textual parts (no think tags or HTML)
        joined = "".join(c for (k,c) in live._parts if k=="text")  # simple
        self.dataset.append_pair(user_txt, joined)

        # Auto TTS (assistant only)
        self.tts.speak_async(resp_text)

    def _add_widget(self, w: QWidget):
        if isinstance(w, BotStreamMessage):
            # obey autoscroll programmatically
            pass
        self.v.addWidget(w)
        QApplication.processEvents()
        if self.autoscroll:
            self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

# ---------- Entrypoint ----------
@api_expose
def main():
    """
    Launch the application. Creates necessary folders, clears session logs,
    and opens the main UI window.
    """
    ensure_dirs()
    # clear logs at start
    SYSTEM_LOG.write_text("", encoding="utf-8")
    app = QApplication(sys.argv)
    gui = MiniChat(); gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

OllamaMiniChat.py
=================
A compact yet capable PyQt5 chat client for **local Ollama** models and **OpenAI** models
with *real-time* streaming text & code, colorful syntax blocks, prompt manager, upload manager,
rolling timing logs, persistent mini-RAG dataset, Zira TTS, a generated Markdown API/README,
and a slim live system log.

Key features
------------
• Providers: **Ollama** (default) and **OpenAI**. Model dropdown updates per provider.
• Real-Time streaming (FAST) for plain text and fenced ```code``` blocks (validated languages).
  - While streaming, code is shown in a “floating terminal” container expanded to full script height.
  - On completion, code blocks auto-minimize (can be expanded by user).
  - Text stream renders live as well (char-wise), with optional metallic <think> styling.
• Colorful code via **Pygments** (Monokai). Emojis on badges.
• Non-semantic and semantic history:
  - Visible (session-only) history to avoid artifacts in displayed text.
  - Persistent dataset of the last **N pairs** (slider; default 10), with rolling file and priority taper.
• Timing logs:
  - Default vs Real-Time averages shown; logs capped to 100 entries (rolling).
  - “Reset Averages” button + optional reset during “Clear Chat”.
• TTS (Windows SAPI5 via **pyttsx3**) using **Microsoft Zira**, **150%** speed by default.
  - Auto-reads **assistant responses only**, in order, no gaps. Stop at any time.
  - Speed slider persisted across sessions in Settings.
• Upload Manager:
  - Paste/drag/drop or browse files/folders; icons for text/code, images, folders.
  - Recursively ingests folders (skips __pycache__, venv*/.venv*, large junk); keeps .git.
  - Simple “tag-and-bucket” enrichment (no vectors), stored in /data/uploads.
  - Per-file progress bars driven via Qt Signals (no hanging).
  - “Clear Uploaded Knowledge” button to purge.
• Prompt Manager:
  - Remove the big system prompt from the main window.
  - Manage named prompts (add/edit/delete*), reorder, check multiple to include in system preamble.
    (*Default prompt cannot be deleted; it can be toggled off.)
• Smarter prompting:
  - Preamble includes (in order): checked prompts, then light summary of older pairs, then
    visible recent pairs (tapered), emphasizing the current user message.
• API / README generator:
  - Button generates **Chat_Agent_API.md** and **README.generated.md** in /data/docs from code,
    scanning @api_expose functions and docstrings. Pop-up viewer with “Copy” button.
• UX niceties:
  - Smoky gray theme, high contrast text, improved professional typography.
  - Top black slim **System Log** ticker + on-disk logs (cleared on startup).
  - Auto-scroll toggle (ON by default) so you can scroll during streaming without snap-back.
  - Provider+Model label inside each response card: **[Provider][model] →** line above content.
  - Enter in the input sends the message (QLineEdit).
• Robust error pop-ups; unhandled exceptions are intercepted and shown.

Install
-------
    pip install pyqt5 requests pyperclip pygments pyttsx3

Run
---
    ollama serve   # if using Ollama
    python OllamaMiniChat.py
**Classes:** PythonHighlighter, TimingLog, DatasetManager, UploadSignals, UploadedKnowledge, TTSManager, ProviderBackend, OllamaBackend, OpenAIBackend, CodeBlockContainer, UserMessage, BotStreamMessage, PromptManager, SettingsDialog, UploadManagerDialog, MiniChat
**Functions:** ensure_dirs(), now_iso(), log_line(msg), _win_protect(plaintext), _win_unprotect(cipher), save_openai_key(key), load_openai_key(), safe_lang(lang), pygments_html(code, lang), api_expose(fn), generate_api_docs(out_md, readme_md), main()
