# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `morph.py`

morph.py — Dual-bot studio with dockable PyQt5 UI, schemas, datasets, robust TTS via SQL queue, and model providers (Ollama local + OpenAI). Supports Tabs, tear-off tabs, and a pop-out Track Mode.
HIGHLIGHTS (performance-safe, non-blocking)
-------------------------------------------
• TTS is fully decoupled: a dedicated background thread reads a SQLite 'tts_queue' table. Only the currently selected conversation is spoken. Click the 🔊 icon next to any message to play from that point forward. Skip the current utterance with Ctrl+K.
• Heartbeat bar (slim, black) displays real-time status (autonomy, CPU/mem/net if available), queue depth, and in-flight ops. Colors: green (healthy), yellow (busy/paused), red (shutdown/error).
• Autonomous Mode (default ON) resumes work at launch, auto-starts if nothing is active, and drives round-robin scheduling. Graceful Quit pauses autonomy, lets rotations complete, persists runtime state, then exits cleanly. Startup clears system log and reloads state.
• Active Conversation Logic hardening: semantic drift threshold is enforced; new “Potential” conversations are generated and parked robustly. Automatic background maintenance promotes potentials, parks long-running actives, and scrubs deleted items—no manual clicks.
• UI simplification: The Conversations Browser dock removes unused controls; a single “Refresh” button remains. All other lifecycle actions run autonomously and are surfaced in the heartbeat and the System Console dock (real log, copyable, reset each launch).
REQUIREMENTS
------------
pip install pyqt5 requests pyttsx3 pyperclip numpy
# Optional (enables richer heartbeat metrics): pip install psutil
RUN
---
ollama serve
python morph.py
NOTES
-----
• Airplane Mode constrains Ollama calls to localhost (OpenAI unaffected).
• OpenAI API key file: C:\Users\Art PC\Desktop\Morph\api\api_key.txt
• Code rendering shows fenced blocks with syntax-highlighted Python.

**Classes:** SystemLogger, ConfigManager, TurnState, PythonHighlighter, CodeBlockWidget, ChatPanel, ArbiterInjector, Bot, Conversation, WorkItem, SessionPlan, TaskRouter, _BoxOperator, Astra, Nova, Stella, ShiftWheelToHorizontalFilter, DetachableTabBar, DetachableTabWidget, FloatingTabWindow, BatchItem, Batch, SnippetForge, Verifier, EditorCore, QueueManager, MorphWindow

**Functions:** init_tts_engine(voice_name), tts_worker(), enqueue_tts(text, voice, conversation_id), set_active_conversation(cid), clear_queue(cid), pause_tts(), resume_tts(), skip_current(), stop_service(), get_queue_depth(cid), now_iso(), sha1(s), safe_write_json(path, data), _ensure_file_reset(path), log_error(where, err), slugify(text, maxw), sync_models_json(), persist_schemas_to_disk(), list_ollama_models(), is_embed_model(name), is_chat_model(name), _default_chat_ollama(), _default_embed_ollama(), list_convo_files(), rag_full_context(), scan_for_directives(content), remove_directives(content), self_doc(), _enforce_localhost(url), _openai_api_key(), _openai_headers(), _chat_provider(), _embed_provider(), _base_options(), ollama_chat_stream(model, messages, q, options), ollama_generate(model, prompt, options), ollama_embed_call(model, text_list), _openai_guard(), openai_chat_stream(model, messages, q, options), openai_generate_once(model, prompt, options), openai_embed_call(model, text_list), provider_chat_stream(model, messages, q, options), provider_generate(model, prompt, options), provider_embed_call(model, text_list), run_operator(op_name, input_text, model), _looks_like_json(s), _heuristic_code_score(s), is_code_like(lang, body), _token_set(s), text_similarity(a, b), create_potential(directive, from_slug, last_entries), forward_to(target_slug, content, reason, from_slug, window), main()
### `tts_service.py`

**Functions:** find_morph_base(), _save_field_in_source(field, value), _select_voice_id(engine, name_like), _new_engine(voice_name_like, rate_val), set_engine_params(voice_name_like, rate_val), read_morph_config(), write_morph_skip_clear(), db_connect(), fetch_next_row_for_active(slug), mark_row_spoken(row_id), tts_worker(), enqueue_tts_direct(text, voice), local_queue_worker(), launch_gui(start_minimized), main()

## Other Files

The following files are present in the project but were not analysed in detail:

- `Extended_Morph_Functions.txt`
- `Morph\config\models.json`
- `Morph\config\user_config.json`
- `Morph\datasets\agents\boxes\Astra-5ab577.json`
- `Morph\datasets\agents\boxes\Nova-d89c53.json`
- `Morph\datasets\agents\boxes\Stella-cabc27.json`
- `Morph\datasets\morph_py\2025-08-16_17-08-03_morph_selfdoc.json`
- `Morph\logs\system.log`
- `Morph\schemas\bots\David.json`
- `Morph\schemas\bots\Zira.json`
- `Morph\schemas\operators\Archivist.json`
- `Morph\schemas\operators\Echo.json`
- `Morph\schemas\operators\Inspector.json`
- `Morph\schemas\operators\Sentinel.json`
- `Morph\schemas\operators\Synthesist.json`
- `Morph\schemas\operators\Vectorist.json`
- `Morph\temp\session_cache\runtime_state.json`
- `Readme.md`
- `datasets\cortex.db`
- `tts_service.log`


## Detailed Module Analyses


## Module `morph.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
morph.py — Dual-bot studio with dockable PyQt5 UI, schemas, datasets, robust TTS via SQL queue, and model providers (Ollama local + OpenAI). Supports Tabs, tear-off tabs, and a pop-out Track Mode.
HIGHLIGHTS (performance-safe, non-blocking)
-------------------------------------------
• TTS is fully decoupled: a dedicated background thread reads a SQLite 'tts_queue' table. Only the currently selected conversation is spoken. Click the 🔊 icon next to any message to play from that point forward. Skip the current utterance with Ctrl+K.
• Heartbeat bar (slim, black) displays real-time status (autonomy, CPU/mem/net if available), queue depth, and in-flight ops. Colors: green (healthy), yellow (busy/paused), red (shutdown/error).
• Autonomous Mode (default ON) resumes work at launch, auto-starts if nothing is active, and drives round-robin scheduling. Graceful Quit pauses autonomy, lets rotations complete, persists runtime state, then exits cleanly. Startup clears system log and reloads state.
• Active Conversation Logic hardening: semantic drift threshold is enforced; new “Potential” conversations are generated and parked robustly. Automatic background maintenance promotes potentials, parks long-running actives, and scrubs deleted items—no manual clicks.
• UI simplification: The Conversations Browser dock removes unused controls; a single “Refresh” button remains. All other lifecycle actions run autonomously and are surfaced in the heartbeat and the System Console dock (real log, copyable, reset each launch).
REQUIREMENTS
------------
pip install pyqt5 requests pyttsx3 pyperclip numpy
# Optional (enables richer heartbeat metrics): pip install psutil
RUN
---
ollama serve
python morph.py
NOTES
-----
• Airplane Mode constrains Ollama calls to localhost (OpenAI unaffected).
• OpenAI API key file: C:\Users\Art PC\Desktop\Morph\api\api_key.txt
• Code rendering shows fenced blocks with syntax-highlighted Python.
"""
import os, re, ast, json, time, hashlib, traceback, subprocess, threading, queue, datetime, sqlite3, platform
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
# Optional heartbeat metrics
try: import psutil # type: ignore
except Exception: psutil = None # graceful degrade
import requests
import pyperclip
from PyQt5.QtCore import Qt, QTimer, QObject, QEvent, QPoint
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPlainTextEdit, QLabel,
    QPushButton, QSizePolicy, QLineEdit, QComboBox, QFrame, QCheckBox, QAction, QDockWidget, QTextEdit,
    QMessageBox, QSlider, QTabWidget, QListWidget, QSpinBox, QTabBar
)
# -------------------------
# TTS Service (integrated)
# -------------------------
import pyttsx3
import queue
import threading
import time
import logging
import sys
# Logging Configuration
logging.basicConfig(
    filename="tts_service.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
# Global Queues for TTS Text (per conversation)
tts_queues = {} # type: Dict[str, queue.Queue]
active_conversation = "" # Current active conversation slug
stop_flag = threading.Event()
paused = threading.Event()
active_voice = "Zira" # Default voice ("Zira" or "David")
_lock = threading.Lock()
engine = None # Global engine for skip
# Setup pyttsx3 Engine
def init_tts_engine(voice_name="Zira"):
    global engine
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    selected_voice = None
    for v in voices:
        if voice_name.lower() in v.name.lower():
            selected_voice = v.id
            break
    if not selected_voice:
        logging.warning(f"Voice '{voice_name}' not found. Falling back to default.")
    else:
        engine.setProperty("voice", selected_voice)
    engine.setProperty("rate", 180) # Adjust speech rate
    engine.setProperty("volume", 1.0) # Max volume
    return engine
# Worker Thread
def tts_worker():
    global active_voice, engine
    engine = init_tts_engine(active_voice)
    while not stop_flag.is_set():
        if paused.is_set():
            time.sleep(0.05)
            continue
        with _lock:
            if not active_conversation or active_conversation not in tts_queues:
                time.sleep(0.1)
                continue
            q = tts_queues[active_conversation]
        try:
            text, voice_name = q.get(timeout=0.1)
            start_time = time.time()
            logging.info(f"TTS START | Voice: {voice_name} | Text: {text[:50]}...")
            # Switch voice if needed
            if voice_name != active_voice:
                active_voice = voice_name
                engine = init_tts_engine(active_voice)
            # Speak the text
            engine.say(text)
            engine.runAndWait()
            duration = round(time.time() - start_time, 2)
            logging.info(f"TTS END | Duration: {duration}s | Text length: {len(text)}")
            q.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logging.error(f"TTS ERROR: {str(e)}")
            engine = init_tts_engine(active_voice) # Re-init engine if crash
    logging.info("TTS Worker stopped gracefully.")
# Public API Functions
def enqueue_tts(text, voice="Zira", conversation_id="default"):
    """Add text to the TTS queue for a specific conversation."""
    with _lock:
        if conversation_id not in tts_queues:
            tts_queues[conversation_id] = queue.Queue()
        tts_queues[conversation_id].put((text, voice))
    logging.info(f"Enqueued TTS | Voice: {voice} | Conv: {conversation_id} | Text: {text[:50]}...")
def set_active_conversation(cid):
    """Set the active conversation for TTS playback."""
    global active_conversation
    with _lock:
        active_conversation = cid
    logging.info(f"Set active TTS to {cid or '(none)'}")
def clear_queue(cid):
    """Clear the queue for a specific conversation."""
    with _lock:
        if cid in tts_queues:
            q = tts_queues[cid]
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    pass
            logging.info(f"Cleared queue for {cid}")
def pause_tts():
    paused.set()
    logging.info("TTS paused.")
def resume_tts():
    paused.clear()
    logging.info("TTS resumed.")
def skip_current():
    global engine
    if engine:
        engine.stop()
    logging.info("TTS skip current.")
def stop_service():
    """Signal the service to stop after current playback."""
    stop_flag.set()
    global engine
    if engine:
        engine.stop()
def get_queue_depth(cid):
    with _lock:
        if cid in tts_queues:
            return tts_queues[cid].qsize()
    return 0
# Start the worker thread
worker_thread = threading.Thread(target=tts_worker, daemon=True)
worker_thread.start()
# =========================================================
# Paths, Directories, Files
# =========================================================
BASE = Path.cwd() / "Morph"
DIR = {
    "conversations": BASE / "conversations",
    "conversations_potential": BASE / "conversations" / "_potential",
    "conversations_deleted": BASE / "conversations" / "_deleted",
    "datasets": BASE / "datasets",
    "semantic": BASE / "datasets" / "semantic",
    "vectors": BASE / "datasets" / "vectors",
    "code_snips": BASE / "datasets" / "code_snippets",
    "morph_py": BASE / "datasets" / "morph_py",
    "error_logs": BASE / "datasets" / "error_logs",
    "goals": BASE / "goals",
    "schemas": BASE / "schemas",
    "schemas_bots": BASE / "schemas" / "bots",
    "schemas_ops": BASE / "schemas" / "operators",
    "temp": BASE / "temp",
    "session": BASE / "temp" / "session_cache",
    "config": BASE / "config",
    "logs": BASE / "logs",
    "topic_status": BASE / "datasets" / "topic_status",
    "operators": BASE / "datasets" / "operators",
}
for p in DIR.values(): p.mkdir(parents=True, exist_ok=True)
USER_CONFIG_FILE = DIR["config"] / "user_config.json"
MODEL_PREFS_FILE = DIR["config"] / "models.json" # back-compat shadow
SYSTEM_LOG_FILE = DIR["logs"] / "system.log"
RUNTIME_STATE_FILE = DIR["session"] / "runtime_state.json"
# =========================================================
# Colors / Styling
# =========================================================
COLOR_SYSTEM = "#f5c518"
COLOR_ZIRA = "#f6e3fb"
COLOR_DAVID = "#e8f2fc"
COLOR_ZIRA_TEXT = "#9c27b0"
COLOR_DAVID_TEXT = "#1e88e5"
COLOR_ERROR = "#e53935"
COLOR_PROCESS_ON = "#b9f6ca"
COLOR_PROCESS_OFF = "#ffffff"
# Heartbeat colors
COLOR_HEARTBEAT_BG = "#000000"
COLOR_HEARTBEAT_GOOD = "#00e676"
COLOR_HEARTBEAT_WARN = "#ffd54f"
COLOR_HEARTBEAT_BAD = "#ff5252"
SMALL_BTN = (
    "QPushButton {background:#FFF;border:1px solid #AAA;color:#000;padding:2px 6px;font-size:10px;border-radius:4px;}"
    "QPushButton:hover {background:#EEE;}"
)
PILL_BTN = (
    "QPushButton {background:#ADD8E6;border:1px solid #CCC;color:#000;padding:4px 10px;font-size:11px;border-radius:12px;}"
    "QPushButton:hover {background:#B0E0E6;}"
)
MONO_FONT = QFont("Consolas" if platform.system()=="Windows" else "Courier New", 10)
# =========================================================
# Utilities / Logging
# =========================================================
def now_iso() -> str: return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
def sha1(s: str) -> str: return hashlib.sha1(s.encode("utf-8","ignore")).hexdigest()
def safe_write_json(path: Path, data: Any):
    try:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)
    except Exception as e:
        log_error("safe_write_json", e)
def _ensure_file_reset(path: Path):
    try: path.write_text("", encoding="utf-8")
    except Exception as e: print("Failed to reset file:", path, e)
class SystemLogger:
    """ Real system log + in-UI console feed (thread-safe). Resets on launch; append-only during runtime. """
    _lock = threading.Lock()
    _subscribers: List["MorphWindow"] = []
    @classmethod
    def reset(cls):
        try:
            with cls._lock: _ensure_file_reset(SYSTEM_LOG_FILE)
        except Exception as e: print("SystemLogger.reset failed:", e)
    @classmethod
    def log(cls, msg: str):
        line = f"{now_iso()} | {msg}"
        try:
            with cls._lock:
                with open(SYSTEM_LOG_FILE, "a", encoding="utf-8") as f: f.write(line + "\n")
        except Exception: pass
        # Non-blocking fanout to subscribers
        for sub in list(cls._subscribers):
            try: sub.enqueue_console(line)
            except Exception: pass
    @classmethod
    def subscribe(cls, win: "MorphWindow"):
        with cls._lock:
            if win not in cls._subscribers: cls._subscribers.append(win)
    @classmethod
    def unsubscribe(cls, win: "MorphWindow"):
        with cls._lock:
            if win in cls._subscribers: cls._subscribers.remove(win)
def log_error(where: str, err: Exception):
    entry = {"time": now_iso(), "where": where, "error": repr(err), "trace": traceback.format_exc()}
    fn = DIR["error_logs"] / f"{now_iso()}_{sha1(where)[:8]}.json"
    try: safe_write_json(fn, entry)
    except Exception: pass
    try: SystemLogger.log(f"[ERROR] {where}: {repr(err)}")
    except Exception: pass
def slugify(text: str, maxw: int = 8) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text)
    return "_".join(words[:maxw]) if words else "Conversation"
# =========================================================
# Config Manager
# =========================================================
DEFAULT_USER_CONFIG = {
    "autonomous_mode": False, # NEW: default ON
    "models": {
        "chat_provider": "Ollama",
        "embed_provider": "Ollama",
        "zira_chat": "deepseek-coder-v2:16b",
        "david_chat": "deepseek-coder-v2:16b",
        "zira_embed": "snowflake-arctic-embed2:latest",
        "david_embed": "snowflake-arctic-embed2:latest",
        "openai_chat_default": "gpt-4o",
        "openai_embed_default": "text-embedding-3-small"
    },
    "tts": {
        "enabled": True,
        "zira_voice": "Zira",
        "david_voice": "David",
        "active_conversation": "", # slug; the only one that is spoken
        "rate": 1.0
    },
    "ui": {
        "colors": {
            "system": COLOR_SYSTEM,
            "zira": COLOR_ZIRA_TEXT,
            "david": COLOR_DAVID_TEXT,
            "error": COLOR_ERROR
        },
        "docks": {
            "models_visible": True,
            "tts_visible": True,
            "schema_visible": True,
            "control_visible": True,
            "ollama_visible": True,
            "console_visible": True
        },
        "view_mode": "tabs",
        "track_tile_width": 520
    },
    "conversation": {
        "rng_first_fresh_only": True,
        "history_limit": 20,
        "rag_file_limit": 10,
        "rag_char_cap": 50000,
        "max_pinned": 4,
        "similarity_threshold": 0.65,
        "drift_window": 10,
        "solo_mode": False,
        "rotation_limit": 10, # NEW: hardcoded rotations before parking
        "maintenance_sec": 45, # NEW: background maintenance cadence
        "diversity": {
            "rewrite_threshold": 0.82,
            "zira": {"temperature": 0.70, "top_p": 0.90, "repeat_penalty": 1.15},
            "david": {"temperature": 0.25, "top_p": 0.85, "repeat_penalty": 1.30}
        }
    },
    "inference": {
        "num_ctx": 45000,
        "num_thread": 4
    },
    "network": {
        "airplane_mode": True,
        "expose_to_network": False
    },
    "operators": {
        "enabled": ["Archivist", "Vectorist", "Inspector", "Synthesist", "Sentinel", "Echo"]
    }
}
class ConfigManager:
    def __init__(self, path: Path):
        self.path = path
        if path.exists():
            try: self.cfg = json.loads(path.read_text(encoding="utf-8"))
            except Exception: self.cfg = DEFAULT_USER_CONFIG.copy()
        else: self.cfg = DEFAULT_USER_CONFIG.copy()
        safe_write_json(self.path, self.cfg)
    def get(self, *keys, default=None):
        ref = self.cfg
        for k in keys:
            if not isinstance(ref, dict) or k not in ref: return default
            ref = ref[k]
        return ref
    def set(self, value, *keys):
        ref = self.cfg
        for k in keys[:-1]: ref = ref.setdefault(k, {})
        ref[keys[-1]] = value
        self.save()
    def save(self): safe_write_json(self.path, self.cfg)
CONFIG = ConfigManager(USER_CONFIG_FILE)
def sync_models_json():
    safe_write_json(MODEL_PREFS_FILE, CONFIG.get("models", default=DEFAULT_USER_CONFIG["models"]))
sync_models_json()
SystemLogger.reset()
# =========================================================
# Providers & Endpoints
# =========================================================
PROVIDERS = ["Ollama", "OpenAI"]
# Ollama (LOCAL ONLY) endpoints
OLLAMA = "http://localhost:11434"
API_CHAT_OLLAMA = f"{OLLAMA}/api/chat"
API_GENERATE_OLLAMA = f"{OLLAMA}/api/generate"
API_EMBED_OLLAMA = f"{OLLAMA}/api/embeddings"
# OpenAI endpoints
OPENAI_CHAT_COMPLETIONS = "https://api.openai.com/v1/chat/completions"
OPENAI_EMBEDDINGS = "https://api.openai.com/v1/embeddings"
OPENAI_API_KEY_PATH = Path(r"C:\Users\Art PC\Desktop\Morph\api\api_key.txt")
OPENAI_CHAT_MODELS = ["gpt-4.1", "gpt-4.1-mini", "gpt-4o", "gpt-4o-mini"]
OPENAI_EMBED_MODELS = ["text-embedding-3-large", "text-embedding-3-small"]
# =========================================================
# Schemas (bots + operators)
# =========================================================
SCHEMAS: Dict[str, Dict[str, Any]] = {
    "Zira": {
        "name": "Zira",
        "voice": CONFIG.get("tts", "zira_voice", default="Zira"),
        "color": CONFIG.get("ui", "colors", "zira", default=COLOR_ZIRA_TEXT),
        "role": (
            "Autonomy architect inside morph.py. You design and prototype new capabilities that push Morph toward "
            "a self-sufficient, self-updating, self-healing system. You ideate fast, produce runnable scaffolds, "
            "and wire glue between UI/UX, datasets, and operators."
        ),
        "directives": [
            "You are Zira inside morph.py. Collaborate with David, but never echo his wording, headings, or section labels.",
            "Argue like an adversarial collaborator: propose, then preemptively stress-test your own idea; invite David to falsify.",
            "Always include a CODE block with runnable or checkable output (prototype, schema, generator, UI stub, test harness, or migration plan).",
            "Fence code/structured data with a correct language tag (python/json/yaml/sql/bash/js/ts/xml/html).",
            "Continuously sweep ALL local Morph datasets and knowledge you can see (./Morph/**). Prioritize: datasets/, schemas/, operators/, conversations/, topic_status/, vectors/, morph_py/ self-doc.",
            "If a data gap or inconsistency is detected, propose a migration or backfill job and emit hooks.",
            "Maintain narrative focus. If exploration branches, emit [[spawn: <title> | tags=a,b | reason=<why>]] or [[forward: <slug> | content=<summary> | reason=<why>]].",
            "Explicitly challenge claims. If something is weak or wrong, supply corrected info and a better plan.",
            "Prefer prototypes, generators, data schemas, and UI/UX glue over prose.",
            "Deliver net-new substance every turn."
        ],
        "goals": [
            "AGI Objective — Transform Morph into a self-directed, continuously improving program: "
            "• self-sufficient; • standalone; • self-implementing; • self-healing; • self-learning; "
            "• GUI-capable; • agentic deployment; • expandable."
        ],
        "style": "Inventive, implementable, relentless."
    },
    "David": {
        "name": "David",
        "voice": CONFIG.get("tts", "david_voice", default="David"),
        "color": CONFIG.get("ui", "colors", "david", default=COLOR_DAVID_TEXT),
        "role": (
            "Reliability and performance lead inside morph.py. You harden Zira’s proposals with measurable safety, tests, "
            "benchmarks, and reversible diffs. You try to break ideas before they break Morph."
        ),
        "directives": [
            "You are David inside morph.py. Collaborate with Zira; never mirror her structure verbatim.",
            "Adopt falsification: break the idea, then propose the safer alternative.",
            "Always include CODE (tests, benchmarks, profilers, rollback scripts, assertions, health checks).",
            "Continuously sweep datasets and logs for regression and drift signals.",
            "If gaps exist (missing tests or metrics), generate them; propose how operators should run them.",
            "Use [[spawn:...]] / [[forward:...]] to branch or route threads with tags and reason.",
            "Prefer measurable changes and rollback paths.",
            "Deliver net-new substance every turn."
        ],
        "goals": [
            "AGI Objective — Same as Zira, but measured and safe: tests, oracles, baselines, SLOs, reproducible benchmarks, rollbacks, integrity guards."
        ],
        "style": "Structured, methodical, falsification-driven."
    },
    "Archivist": {"kind":"operator","role":"Dataset curator", "tasks":["Deduplicate/normalize conversation logs.","Extract code blocks into datasets/code_snippets.","Maintain thread tags and lineage."]},
    "Vectorist": {"kind":"operator","role":"Optional vectorizer", "tasks":["Vectorize non-critical explanatory text only.","Never embed code or full conversations.","Index TOPIC_STATUS summaries."]},
    "Inspector": {"kind":"operator","role":"Codebase analyzer", "tasks":["Parse morph.py; extract functions/classes into datasets/morph_py.","Flag blocking calls on UI thread.","Suggest safe minimal diffs."]},
    "Synthesist": {"kind":"operator","role":"Safe integration planner", "tasks":["Propose minimal diffs with rollbacks; log to datasets/code_snippets.","Annotate diffs with tests and rollback steps."]},
    "Sentinel": {"kind":"operator","role":"Integrity & security", "tasks":["Detect dataset corruption or external network attempts; log alerts.","Enforce airplane-mode behavior for Ollama endpoints only."]},
    "Echo": {"kind":"operator","role":"TTS sync","tasks":["Keep playback caught up; retry on failure; log lag metrics."]},
}
def persist_schemas_to_disk():
    DIR["schemas_bots"].mkdir(parents=True, exist_ok=True)
    DIR["schemas_ops"].mkdir(parents=True, exist_ok=True)
    for name in ("Zira", "David"):
        (DIR["schemas_bots"] / f"{name}.json").write_text(json.dumps(SCHEMAS[name], indent=2), encoding="utf-8")
    for op in ("Archivist","Vectorist","Inspector","Synthesist","Sentinel","Echo"):
        (DIR["schemas_ops"] / f"{op}.json").write_text(json.dumps(SCHEMAS[op], indent=2), encoding="utf-8")
persist_schemas_to_disk()
# =========================================================
# Model enumeration / filtering (Ollama local)
# =========================================================
def list_ollama_models() -> List[str]:
    try:
        out = subprocess.check_output(["ollama","list"], text=True, timeout=2)
        names = []
        for line in out.splitlines()[1:]:
            parts = line.split()
            if parts: names.append(parts[0])
        return names
    except Exception as e:
        log_error("list_ollama_models", e)
        return [
            "deepseek-coder-v2:16b", "wizardlm-uncensored:latest", "phi4:latest",
            "gemma3:27b", "codellama:latest", "llava:latest", "nomic-embed-text:latest",
            "snowflake-arctic-embed2:latest",
        ]
def is_embed_model(name: str) -> bool:
    nl = name.lower()
    return ("embed" in nl) or ("embedding" in nl) or ("arctic-embed" in nl) or ("nomic-embed" in nl)
def is_chat_model(name: str) -> bool: return not is_embed_model(name)
ALL_MODELS = list_ollama_models()
CHAT_MODELS = [m for m in ALL_MODELS if is_chat_model(m)]
EMBED_MODELS = [m for m in ALL_MODELS if is_embed_model(m)]
def _default_chat_ollama():
    return "deepseek-coder-v2:16b" if "deepseek-coder-v2:16b" in CHAT_MODELS else (CHAT_MODELS[0] if CHAT_MODELS else "deepseek-coder-v2:16b")
def _default_embed_ollama():
    return "snowflake-arctic-embed2:latest" if "snowflake-arctic-embed2:latest" in EMBED_MODELS else (EMBED_MODELS[0] if EMBED_MODELS else "snowflake-arctic-embed2:latest")
if CONFIG.get("models","zira_chat") not in ALL_MODELS: CONFIG.set(_default_chat_ollama(), "models","zira_chat")
if CONFIG.get("models","david_chat") not in ALL_MODELS: CONFIG.set(_default_chat_ollama(), "models","david_chat")
if CONFIG.get("models","zira_embed") not in ALL_MODELS: CONFIG.set(_default_embed_ollama(), "models","zira_embed")
if CONFIG.get("models","david_embed") not in ALL_MODELS: CONFIG.set(_default_embed_ollama(), "models","david_embed")
sync_models_json()
# =========================================================
# Turn persistence (RNG once, then alternate)
# =========================================================
class TurnState:
    def __init__(self, path: Path, rng_first_only: bool = True):
        self.path = path
        self.rng_first_only = rng_first_only
        self.state = {"fresh": True, "last": None}
        if path.exists():
            try: self.state = json.loads(path.read_text(encoding="utf-8"))
            except Exception: pass
    def first_speaker(self) -> str:
        if self.state.get("fresh", True) or not self.state.get("last"):
            first = "Zira" if not self.rng_first_only else (["Zira","David"][int(time.time()) & 1])
            self.state["fresh"] = False
            self.state["last"] = first
            safe_write_json(self.path, self.state)
            return first
        nxt = "David" if self.state["last"] == "Zira" else "Zira"
        self.state["last"] = nxt
        safe_write_json(self.path, self.state)
        return nxt
    def reset(self):
        self.state = {"fresh": True, "last": None}
        safe_write_json(self.path, self.state)
# =========================================================
# RAG — full-context (bounded)
# =========================================================
def list_convo_files() -> List[Path]:
    if not DIR["conversations"].exists(): return []
    return sorted(DIR["conversations"].glob("*.json"))
def rag_full_context() -> str:
    file_limit = CONFIG.get("conversation","rag_file_limit", default=10)
    char_cap = CONFIG.get("conversation","rag_char_cap", default=50000)
    chunks = []
    for p in list_convo_files()[-file_limit:] if file_limit else []:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            chunks.append(json.dumps(data.get("entries", [])))
        except Exception: pass
    ctx = "\n\n".join(chunks)
    ctx = re.sub(r"hash:[0-9a-f]{6,40}", "", ctx, flags=re.I)
    return ctx[-char_cap:]
# =========================================================
# Directive scanning (spawn/forward)
# =========================================================
DIRECTIVE_RE_BRACKET = re.compile(r'\[\[spawn: (.*?)\s*\|\s*tags=(.*?)\s*\|\s*reason=(.*?)\]\]')
DIRECTIVE_RE_JSON_SPAWN = re.compile(r'\{ "morph_directive":"spawn_conversation",\s*"title":"(.*?)"\s*,\s*"tags":\[(.*?)\],\s*"reason":"(.*?)" \}')
DIRECTIVE_RE_BRACKET_FORWARD = re.compile(r'\[\[forward: (.*?)\s*\|\s*content=(.*?)\s*\|\s*reason=(.*?)\]\]')
DIRECTIVE_RE_JSON_FORWARD = re.compile(r'\{ "morph_directive":"forward_conversation",\s*"target":"(.*?)"\s*,\s*"content":"(.*?)" \s*,\s*"reason":"(.*?)" \}')
def scan_for_directives(content: str) -> List[Dict]:
    directives = []
    for m in DIRECTIVE_RE_BRACKET.finditer(content):
        directives.append({"type": "spawn", "title": m.group(1).strip(), "tags": [t.strip() for t in m.group(2).split(',')], "reason": m.group(3).strip()})
    for m in DIRECTIVE_RE_JSON_SPAWN.finditer(content):
        tags = [t.strip().strip('"') for t in m.group(2).split(',')]
        directives.append({"type": "spawn", "title": m.group(1), "tags": tags, "reason": m.group(3)})
    for m in DIRECTIVE_RE_BRACKET_FORWARD.finditer(content):
        directives.append({"type": "forward", "target": m.group(1).strip(), "content": m.group(2).strip(), "reason": m.group(3).strip()})
    for m in DIRECTIVE_RE_JSON_FORWARD.finditer(content):
        directives.append({"type": "forward", "target": m.group(1), "content": m.group(2), "reason": m.group(3)})
    return directives
def remove_directives(content: str) -> str:
    content = DIRECTIVE_RE_BRACKET.sub("", content)
    content = DIRECTIVE_RE_JSON_SPAWN.sub("", content)
    content = DIRECTIVE_RE_BRACKET_FORWARD.sub("", content)
    content = DIRECTIVE_RE_JSON_FORWARD.sub("", content)
    return content.strip()
# =========================================================
# Self-document morph.py
# =========================================================
def self_doc():
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        items = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                items.append({
                    "type": type(node).__name__,
                    "name": getattr(node, "name", ""),
                    "lineno": getattr(node, "lineno", -1),
                    "doc": ast.get_docstring(node) or "",
                    "args": [a.arg for a in getattr(node, "args", []).args] if hasattr(node,"args") and node.args else []
                })
        out = DIR["morph_py"] / f"{now_iso()}_morph_selfdoc.json"
        safe_write_json(out, {"time": now_iso(), "items": items})
    except Exception as e: log_error("self_doc", e)
self_doc()
# =========================================================
# Provider helpers
# =========================================================
def _enforce_localhost(url: str) -> str:
    if not CONFIG.get("network","airplane_mode", default=True): return url
    try: host = url.split("://",1)[1].split("/",1)[0]
    except Exception: host = ""
    if host not in ("localhost:11434","127.0.0.1:11434","localhost","127.0.0.1"):
        return "http://localhost:11434"
    return url
def _openai_api_key() -> Optional[str]:
    try:
        if OPENAI_API_KEY_PATH.exists():
            k = OPENAI_API_KEY_PATH.read_text(encoding="utf-8").strip()
            if k: return k
    except Exception as e: log_error("openai_key_read", e)
    envk = os.environ.get("OPENAI_API_KEY","").strip()
    return envk or None
def _openai_headers() -> Dict[str,str]:
    k = _openai_api_key()
    return {"Authorization": f"Bearer {k or ''}", "Content-Type": "application/json"}
def _chat_provider() -> str: return CONFIG.get("models","chat_provider", default="Ollama")
def _embed_provider() -> str: return CONFIG.get("models","embed_provider", default="Ollama")
# =========================================================
# Ollama / OpenAI calls
# =========================================================
def _base_options() -> Dict[str, Any]:
    return {
        "num_ctx": int(CONFIG.get("inference","num_ctx", default=45000)),
        "num_thread": int(CONFIG.get("inference","num_thread", default=4))
    }
def ollama_chat_stream(model: str, messages: List[Dict[str,str]], q: queue.Queue, options: Optional[Dict[str,Any]] = None) -> None:
    try:
        if not is_chat_model(model): q.put(("error", "⚠️ Local model error: selected model is an embedding model; choose a chat model.")); return
        url = _enforce_localhost(API_CHAT_OLLAMA)
        opts = _base_options()
        if options: opts.update(options)
        payload = {"model": model, "messages": messages, "stream": True, "options": opts}
        with requests.post(url, json=payload, stream=True, timeout=300) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line: continue
                try: j = json.loads(line)
                except Exception: continue
                msg = j.get("message") or {}
                content = msg.get("content", "")
                if content: q.put(("delta", content))
                if j.get("done", False): q.put(("done",)); return
    except Exception as e:
        log_error("ollama_chat_stream", e)
        q.put(("error", f"⚠️ Local model error: {e}"))
def ollama_generate(model: str, prompt: str, options: Optional[Dict[str,Any]] = None) -> str:
    try:
        url = _enforce_localhost(API_GENERATE_OLLAMA)
        opts = _base_options()
        if options: opts.update(options)
        payload = {"model": model, "prompt": prompt, "stream": False, "options": opts}
        r = requests.post(url, json=payload, timeout=180)
        r.raise_for_status()
        return r.json().get("response","")
    except Exception as e:
        log_error("ollama_generate", e)
        return ""
def ollama_embed_call(model: str, text_list: List[str]) -> Dict[str, Any]:
    try:
        if not is_embed_model(model): return {"error": "selected model is not an embedding model"}
        url = _enforce_localhost(API_EMBED_OLLAMA)
        payload = {"model": model, "input": text_list}
        r = requests.post(url, json=payload, timeout=180)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log_error("ollama_embed_call", e)
        return {"error": str(e)}
def _openai_guard() -> Optional[str]:
    if not _openai_api_key(): return f"⚠️ Missing OpenAI API key. Put it in {OPENAI_API_KEY_PATH} or export OPENAI_API_KEY."
    return None
def openai_chat_stream(model: str, messages: List[Dict[str,str]], q: queue.Queue, options: Optional[Dict[str,Any]] = None) -> None:
    guard = _openai_guard()
    if guard: q.put(("error", guard)); return
    try:
        headers = _openai_headers()
        payload = {
            "model": model,
            "messages": messages,
            "temperature": float(options.get("temperature", 0.7)) if options else 0.7,
            "top_p": float(options.get("top_p", 0.9)) if options else 0.9,
            "stream": True
        }
        with requests.post(OPENAI_CHAT_COMPLETIONS, headers=headers, json=payload, stream=True, timeout=600) as r:
            r.raise_for_status()
            for raw in r.iter_lines(decode_unicode=True):
                if not raw: continue
                line = raw.strip()
                if line.startswith("data:"): line = line[5:].strip()
                if line == "[DONE]": q.put(("done",)); return
                try: j = json.loads(line)
                except Exception: continue
                chs = j.get("choices") or []
                if not chs: continue
                delta = (chs[0].get("delta") or {})
                piece = delta.get("content") or ""
                if piece: q.put(("delta", piece))
                if chs[0].get("finish_reason"): q.put(("done",)); return
    except Exception as e:
        log_error("openai_chat_stream", e)
        q.put(("error", f"⚠️ OpenAI error: {e}"))
def openai_generate_once(model: str, prompt: str, options: Optional[Dict[str,Any]] = None) -> str:
    guard = _openai_guard()
    if guard: return guard
    try:
        headers = _openai_headers()
        payload = {
            "model": model,
            "messages": [{"role":"system","content":"You are a helpful assistant."},{"role":"user","content": prompt}],
            "temperature": float(options.get("temperature", 0.7)) if options else 0.7,
            "top_p": float(options.get("top_p", 0.9)) if options else 0.9,
            "stream": False
        }
        r = requests.post(OPENAI_CHAT_COMPLETIONS, headers=headers, json=payload, timeout=300)
        r.raise_for_status()
        data = r.json()
        chs = data.get("choices") or []
        if chs and chs[0].get("message", {}).get("content"): return chs[0]["message"]["content"]
        return ""
    except Exception as e:
        log_error("openai_generate_once", e)
        return f"⚠️ OpenAI error: {e}"
def openai_embed_call(model: str, text_list: List[str]) -> Dict[str, Any]:
    guard = _openai_guard()
    if guard: return {"error": guard}
    try:
        headers = _openai_headers()
        payload = {"model": model, "input": text_list}
        r = requests.post(OPENAI_EMBEDDINGS, headers=headers, json=payload, timeout=180)
        r.raise_for_status()
        data = r.json()
        embs = [item.get("embedding", []) for item in data.get("data", [])]
        return {"embeddings": embs}
    except Exception as e:
        log_error("openai_embed_call", e)
        return {"error": str(e)}
# Provider-agnostic
def provider_chat_stream(model: str, messages: List[Dict[str,str]], q: queue.Queue, options: Optional[Dict[str,Any]] = None) -> None:
    if _chat_provider() == "OpenAI": return openai_chat_stream(model, messages, q, options)
    else: return ollama_chat_stream(model, messages, q, options)
def provider_generate(model: str, prompt: str, options: Optional[Dict[str,Any]] = None) -> str:
    if _chat_provider() == "OpenAI": return openai_generate_once(model, prompt, options)
    else: return ollama_generate(model, prompt, options)
def provider_embed_call(model: str, text_list: List[str]) -> Dict[str, Any]:
    if _embed_provider() == "OpenAI": return openai_embed_call(model, text_list)
    else: return ollama_embed_call(model, text_list)
# =========================================================
# Operators (helper)
# =========================================================
def run_operator(op_name: str, input_text: str, model: str) -> str:
    sch = SCHEMAS.get(op_name, {})
    system = f"You are {op_name}, {sch.get('role', '')}. Tasks: {'; '.join(sch.get('tasks', []))} Be concise."
    prompt = f"{system}\n\nInput:\n{input_text}"
    return provider_generate(model, prompt)
# =========================================================
# Syntax highlighting, code fences
# =========================================================
class PythonHighlighter(QSyntaxHighlighter):
    KW = {"def","class","if","elif","else","while","for","try","except","finally","with","as","import","from","return","pass","break","continue","in","not","and","or","is","lambda","yield","raise","assert","global","nonlocal"}
    def __init__(self, doc):
        super().__init__(doc)
        self.fmt_kw = QTextCharFormat(); self.fmt_kw.setForeground(QColor("#569CD6"))
        self.fmt_str = QTextCharFormat(); self.fmt_str.setForeground(QColor("#CE9178"))
        self.fmt_cmt = QTextCharFormat(); self.fmt_cmt.setForeground(QColor("#6A9955"))
        self.fmt_num = QTextCharFormat(); self.fmt_num.setForeground(QColor("#B5CEA8"))
        self.fmt_dec = QTextCharFormat(); self.fmt_dec.setForeground(QColor("#C586C0"))
        self.fmt_fn = QTextCharFormat(); self.fmt_fn.setForeground(QColor("#DCDCAA"))
    def highlightBlock(self, text: str):
        for kw in self.KW:
            for m in re.finditer(rf"\b{re.escape(kw)}\b", text): self.setFormat(m.start(), m.end()-m.start(), self.fmt_kw)
        for m in re.finditer(r'".*?"|\'.*?\'', text): self.setFormat(m.start(), m.end()-m.start(), self.fmt_str)
        for m in re.finditer(r"#.*", text): self.setFormat(m.start(), m.end()-m.start(), self.fmt_cmt)
        for m in re.finditer(r"\b\d+(\.\d+)?\b", text): self.setFormat(m.start(), m.end()-m.start(), self.fmt_num)
        for m in re.finditer(r"@\w+", text): self.setFormat(m.start(), m.end()-m.start(), self.fmt_dec)
        for m in re.finditer(r"\bdef\s+(\w+)", text): self.setFormat(m.start(1), len(m.group(1)), self.fmt_fn)
        for m in re.finditer(r"\bclass\s+(\w+)", text): self.setFormat(m.start(1), len(m.group(1)), self.fmt_fn)
_CODE_RE = re.compile(r"```(?P<lang>[A-Za-z0-9_\-]+)?\s*\n(?P<body>[\s\S]*?)\n```", re.MULTILINE)
KNOWN_LANGS = {
    "python","py","json","yaml","yml","xml","html","markdown","md","ini","toml",
    "sql","bash","sh","powershell","ps1","java","c","cpp","hpp","cs","javascript",
    "js","typescript","ts","go","rust","rs","lua","php","swift","kotlin","r","matlab"
}
def _looks_like_json(s: str) -> bool:
    s = s.strip()
    if not s: return False
    if not (s.startswith("{") or s.startswith("[")): return False
    try: json.loads(s); return True
    except Exception: return False
def _heuristic_code_score(s: str) -> float:
    t = s.strip()
    if not t: return 0.0
    markers = [
        "def ","class ","import ","from ","#include","using ","::","->","=>",
        "public ","private ","protected ","interface ","implements ","template<",
        "var ","let ","const ","function ","fn ","package ","namespace ",
        "try:","except","catch","finally","return",";","{","}","/*","*/",
    ]
    hit = sum(1 for m in markers if m in t)
    sym = sum(1 for ch in t if ch in "{}[]();:=#<>/*\\")
    ratio = sym / max(1, len(t))
    ind = sum(1 for line in t.splitlines() if line.startswith((" ","\t")))
    long_prose_penalty = 1 if (len(t.split()) > 50 and t.count("\n") < 2) else 0
    score = min(1.0, 0.15*hit + 2.0*ratio + 0.05*ind) - 0.2*long_prose_penalty
    return max(0.0, score)
def is_code_like(lang: Optional[str], body: str) -> bool:
    ltag = (lang or "").strip().lower()
    if ltag in KNOWN_LANGS:
        if ltag == "json" and not _looks_like_json(body): return False
        return True
    if _looks_like_json(body): return True
    return _heuristic_code_score(body) >= 0.55
# =========================================================
# Code block widget
# =========================================================
class CodeBlockWidget(QWidget):
    """ Expand/collapse is smooth and non-blocking. """
    def __init__(self, code: str, lang: str = "", parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(4)
        hdr = QHBoxLayout(); hdr.setContentsMargins(0,0,0,0)
        lang_label = (lang or "").strip().lower() or "code"
        lines = max(1, code.count("\n") + 1)
        self.lbl = QLabel(f"{lang_label} • {lines} line{'s' if lines != 1 else ''}")
        self.lbl.setStyleSheet("QLabel{font: 10pt 'Consolas'; color:#888;}")
        self.chk_expand = QCheckBox("Full Expand"); self.chk_expand.stateChanged.connect(self._toggle)
        hdr.addWidget(self.lbl); hdr.addStretch(1); hdr.addWidget(self.chk_expand)
        v.addLayout(hdr)
        self.editor = QPlainTextEdit(code)
        self.editor.setReadOnly(True); self.editor.setFont(MONO_FONT)
        self.editor.setStyleSheet("QPlainTextEdit{background:#1E1E1E;color:#DCDCDC;border:1px solid #333;border-radius:4px;}")
        if lang_label in ("python","py"): PythonHighlighter(self.editor.document())
        self.DEFAULT_H = int(self.editor.fontMetrics().lineSpacing() * 25 + 24)
        self.editor.setFixedHeight(self.DEFAULT_H)
        v.addWidget(self.editor)
        copy = QPushButton("📋 Copy Code"); copy.setStyleSheet(SMALL_BTN)
        copy.clicked.connect(lambda: pyperclip.copy(code))
        v.addWidget(copy)
        self._apply_half_min()
    def _apply_half_min(self):
        doc_lines = max(1, int(self.editor.document().size().height()))
        line_h = self.editor.fontMetrics().lineSpacing() or 16
        natural_h = max(self.DEFAULT_H, int(doc_lines * line_h + 24))
        half = max(120, natural_h // 2)
        self.editor.setMinimumHeight(half)
        if self.editor.height() < half: self.editor.setFixedHeight(half)
    def _toggle(self, state: int):
        if state == Qt.Checked:
            doc_h = int(self.editor.document().size().height() * (self.editor.fontMetrics().lineSpacing())) + 60
            self.editor.setFixedHeight(min(max(self.DEFAULT_H, doc_h), 4000))
        else:
            self._apply_half_min()
# =========================================================
# Chat panel (adds a 🔊 play button per message)
# =========================================================
class ChatPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.inner = QWidget(); self.inner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.v = QVBoxLayout(self.inner)
        self.v.setContentsMargins(8,8,8,8); self.v.setSpacing(10)
        self.v.addStretch(1)
        self.scroll.setWidget(self.inner)
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.addWidget(self.scroll)
        self._msg_index_counter = 0 # auto index fallback
    def _message_panel(self, who: str) -> Tuple[QWidget, QVBoxLayout]:
        panel = QWidget()
        p = QVBoxLayout(panel)
        p.setContentsMargins(10,8,10,10); p.setSpacing(6)
        if who == "Zira":
            panel.setStyleSheet(f"QWidget{{background:{COLOR_ZIRA};border:1px solid #e9c9f3;border-radius:8px;}} QLabel{{color:{COLOR_ZIRA_TEXT};}}")
        elif who == "David":
            panel.setStyleSheet(f"QWidget{{background:{COLOR_DAVID};border:1px solid #cfe2fb;border-radius:8px;}} QLabel{{color:{COLOR_DAVID_TEXT};}}")
        else:
            panel.setStyleSheet(f"QWidget{{background:#fff8d6;border:1px solid #f1e2a0;border-radius:8px;}} QLabel{{color:#5c4b00;}}")
        return panel, p
    def add_message(self, who: str, text: str, color_text: str, entry_index: int = None):
        panel, pv = self._message_panel(who)
        header = QHBoxLayout(); header.setContentsMargins(0,0,0,0)
        lbl = QLabel(f"<b>{who}:</b>"); lbl.setStyleSheet(f"color:{color_text};")
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        header.addWidget(lbl)
        if entry_index is None: entry_index = self._msg_index_counter
        self._msg_index_counter += 1
        spk = QPushButton("🔊")
        spk.setToolTip("Play from this message")
        spk.setFixedSize(22, 22)
        spk.setStyleSheet(
            "QPushButton{border:1px solid #666; border-radius:11px; font-size:11px; "
            "background:#111; color:#ddd; padding:0;} "
            "QPushButton:hover{background:#222;}"
        )
        def _play_from_here():
            try: self.parent_convo.tts_play_from(entry_index)
            except Exception as e: log_error("ChatPanel.speaker_click", e)
        spk.clicked.connect(_play_from_here)
        header.addStretch(1); header.addWidget(spk)
        pv.addLayout(header)
        pos = 0
        raw = text or ""
        for m in _CODE_RE.finditer(raw):
            start, end = m.span()
            pre = (raw[pos:start] or "").strip()
            if pre:
                t = QLabel(pre.replace("\n","<br>"))
                t.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
                t.setWordWrap(True)
                pv.addWidget(t)
            lang = (m.group("lang") or "").strip()
            body = (m.group("body") or "")
            if is_code_like(lang, body):
                pv.addWidget(CodeBlockWidget(body.strip(), lang=lang, parent=self))
            else:
                t = QLabel((body.strip() or "").replace("\n","<br>"))
                t.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
                t.setWordWrap(True)
                pv.addWidget(t)
            pos = end
        tail = (raw[pos:] or "").strip()
        if tail:
            t = QLabel(tail.replace("\n","<br>"))
            t.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
            t.setWordWrap(True)
            pv.addWidget(t)
        self.v.insertWidget(self.v.count() - 1, panel)
        hr = QFrame(); hr.setFrameShape(QFrame.HLine); hr.setStyleSheet("color:#555;")
        self.v.insertWidget(self.v.count() - 1, hr)
        QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))
    def add_pending(self, who: str, color_text: str) -> Tuple[QWidget, QLabel]:
        panel, pv = self._message_panel(who)
        lbl = QLabel(f'<b>{who}:</b> <i>thinking...</i>')
        lbl.setStyleSheet(f"color:{color_text};")
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        pv.addWidget(lbl)
        self.v.insertWidget(self.v.count() - 1, panel)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())
        return panel, lbl
    def update_pending(self, lbl: QLabel, text: str):
        try:
            txt = lbl.text()
            if ":</b>" in txt: prefix = txt.split(':</b>')[0] + ':</b> '
            else: prefix = ''
            lbl.setText(prefix + (text.replace("\n", "<br>") if text else "<i>thinking...</i>"))
        except Exception as e: log_error("ChatPanel.update_pending", e)
    def remove_pending(self, panel: QWidget):
        try:
            idx = self.v.indexOf(panel)
            if idx >= 0:
                item = self.v.takeAt(idx)
                if item and item.widget(): item.widget().deleteLater()
        except Exception as e: log_error("ChatPanel.remove_pending", e)
    def copy_all(self):
        try:
            entries = "\n\n".join([f"{e['role']}: {e['content']}" for e in self.parent_convo.entries])
            pyperclip.copy(entries)
        except Exception as e: log_error("ChatPanel.copy_all", e)
# =========================================================
# Arbiter
# =========================================================
class ArbiterInjector:
    def __init__(self): self._lock = threading.Lock(); self._next: Optional[str] = None
    def set(self, text: str):
        with self._lock: self._next = text.strip() or None
    def pop(self) -> Optional[str]:
        with self._lock: v = self._next; self._next = None; return v
# =========================================================
# Bot
# =========================================================
class Bot:
    def __init__(self, name: str, color: str, voice: str, chat_model: str, embed_model: str):
        self.name = name; self.color=color; self.voice=voice
        self.chat_model=chat_model; self.embed_model=embed_model
        self.history: List[Dict[str,str]] = []
        self.title_slug = "Conversation"
    def system_message(self) -> Dict[str,str]:
        sch = SCHEMAS.get(self.name, {})
        guard = [
            f"You are {sch.get('name', self.name)} inside morph.py.",
            sch.get("role",""),
            "Rules:",
            "- Do NOT prefix your output with your name.",
            "- Do NOT invent tool-call tags or fake function invocations.",
            "- If you provide code, put it inside triple backticks with a correct language tag.",
            "- Be direct. No meta-comments about prompts or schemas.",
            "- Explicitly avoid repeating your counterpart's structure. Add net-new, complementary work.",
            "Directives: " + "; ".join(sch.get("directives", [])),
            "Goals: " + "; ".join(sch.get("goals", [])),
            "OUTPUT CONTRACT:",
            "1) PLAN (1 sentence).",
            "2) CHANGELOG (bullets).",
            "3) CODE (single or multiple fenced blocks).",
            "4) TOPIC_STATUS (brief: positives/negatives/diffs/tests).",
            "5) HOOKS ([[spawn:...]] or [[forward:...]] if useful).",
        ]
        return {"role":"system","content":" ".join(guard)}
    def context_messages(self, arb: Optional[str], counterpart_last_msg: str, history_limit: int) -> List[Dict[str,str]]:
        msgs: List[Dict[str,str]] = [ self.system_message() ]
        ctx = rag_full_context()
        if ctx: msgs.append({"role":"system","content": f"GLOBAL_CONTEXT\n{ctx}\nEND_GLOBAL_CONTEXT"})
        msgs.extend(self.history[-abs(history_limit):])
        if arb: msgs.append({"role":"user","content": f"[Arbiter]: {arb}"})
        msgs.append({"role":"user","content": f"[{self.name}'s counterpart said]: {counterpart_last_msg}"})
        return msgs
    def on_model_response(self, text: str):
        if self.title_slug == "Conversation":
            opener = re.sub(r"\s+"," ", text).strip()
            self.title_slug = slugify(opener or self.name)
# =========================================================
# Conversation (semantic drift, rotation/parking, TTS integration)
# =========================================================
def _token_set(s: str) -> set:
    s = re.sub(r"```[\s\S]*?```", "", s)
    s = re.sub(r"\s+", " ", s).lower()
    return set(re.findall(r"[a-z0-9_]+", s))
def text_similarity(a: str, b: str) -> float:
    A, B = _token_set(a), _token_set(b)
    if not A or not B: return 0.0
    inter = len(A & B)
    return (2.0 * inter) / (len(A) + len(B))
class Conversation:
    def __init__(self, slug: str, window, is_potential: bool = False):
        self.window = window
        self.slug = slug
        self.path = (DIR["conversations_potential"] if is_potential else DIR["conversations"]) / f"{slug}.json"
        # Models
        self.embed_model = CONFIG.get("models", "zira_embed")
        self.zira = Bot("Zira", COLOR_ZIRA_TEXT, SCHEMAS["Zira"]["voice"], CONFIG.get("models","zira_chat"), self.embed_model)
        self.david = Bot("David", COLOR_DAVID_TEXT, SCHEMAS["David"]["voice"], CONFIG.get("models","david_chat"), self.embed_model)
        self.chat = ChatPanel(); self.chat.parent_convo = self
        self.turn = TurnState(DIR["session"] / f"turn_state_{slug}.json", rng_first_only=CONFIG.get("conversation","rng_first_fresh_only", default=True))
        self.arbiter = ArbiterInjector()
        self.entries: List[Dict] = []
        self.centroid = None
        self.recent_embs: List = []
        self.running = False
        self.current_speaker = None
        self.pending_panel = None
        self.pending_lbl = None
        self.q = None
        self.timer = None
        self.turn_count = 0
        self.parked = False # when true, background will not auto-advance
        # Load persisted entries
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.entries = data.get("entries", [])
                for i, e in enumerate(self.entries):
                    role = e.get("role",""); content = e.get("content","")
                    if role == "Zira":
                        self.zira.history.append({"role": "assistant", "content": content})
                        self.david.history.append({"role": "user", "content": content})
                    elif role == "David":
                        self.david.history.append({"role": "assistant", "content": content})
                        self.zira.history.append({"role": "user", "content": content})
                    self.chat.add_message(
                        role, content,
                        self.zira.color if role == "Zira" else self.david.color if role == "David" else COLOR_SYSTEM,
                        entry_index=i
                    )
                contents = [e["content"] for e in self.entries if "content" in e]
                if contents:
                    res = provider_embed_call(self.embed_model, contents)
                    if "embeddings" in res:
                        embs = res["embeddings"]
                        self.centroid = np.mean(embs, axis=0) if embs else None
            except Exception as e: log_error("Conversation.load", e)
    def _bot_options(self, bot_name: str) -> Dict[str, Any]:
        dv = CONFIG.get("conversation","diversity", default=DEFAULT_USER_CONFIG["conversation"]["diversity"])
        per = dv.get(bot_name.lower(), {})
        return {
            "temperature": float(per.get("temperature", 0.6)),
            "top_p": float(per.get("top_p", 0.9)),
            "repeat_penalty": float(per.get("repeat_penalty", 1.1)) # ignored by OpenAI
        }
    def append_log(self, role: str, content: str):
        tags = self.extract_tags(content)
        entry = {"time": now_iso(), "role": role, "content": content, "tags": tags}
        self.entries.append(entry)
    def save(self):
        threading.Thread(target=lambda: safe_write_json(self.path, {"title": self.slug, "entries": self.entries}), daemon=True).start()
    def run_operators(self, content: str):
        def thread_ops():
            try:
                if "Archivist" in CONFIG.get("operators", "enabled", default=[]):
                    resp = run_operator("Archivist", content, self.zira.chat_model)
                    safe_write_json(DIR["operators"] / f"Archivist_{now_iso()}.json", {"response": resp})
                if "Vectorist" in CONFIG.get("operators", "enabled", default=[]):
                    if not any(is_code_like(m.group("lang"), m.group("body")) for m in _CODE_RE.finditer(content)):
                        res = provider_embed_call(self.embed_model, [content])
                        if "embeddings" in res:
                            emb = res["embeddings"][0]
                            safe_write_json(DIR["vectors"] / f"{sha1(content)}.json", {"emb": emb, "text": content})
                if "Inspector" in CONFIG.get("operators", "enabled", default=[]):
                    for m in _CODE_RE.finditer(content):
                        lang = (m.group("lang") or "").strip()
                        body = (m.group("body") or "")
                        if is_code_like(lang, body) and body.strip():
                            resp = run_operator("Inspector", body, self.zira.chat_model)
                            safe_write_json(DIR["operators"] / f"Inspector_{now_iso()}.json", {"response": resp, "lang": lang})
            except Exception as e: log_error("Conversation.run_operators", e)
        threading.Thread(target=thread_ops, daemon=True).start()
    def extract_tags(self, text: str) -> List[str]:
        CANON_TAGS = ["autonomy","spawn","forward","code_diff","self_evolve","drift","critic","ui_fix","prompt_upgrade","tests","benchmarks","completed","parked","potential"]
        hits = [t for t in CANON_TAGS if t.replace("_", " ") in text.lower() or t in text.lower()]
        if not hits:
            resp = provider_generate(self.zira.chat_model, f"Extract up to 6 tags from:\n{text[:800]}\nReturn comma-separated lowercase tokens.")
            hits = [t.strip().replace(" ", "_") for t in resp.split(",") if t.strip()]
        return sorted(set(hits))[:8]
    def update_centroid(self, text: str):
        def thread_embed():
            try:
                res = provider_embed_call(self.embed_model, [text])
                if "embeddings" not in res: return
                emb = np.array(res["embeddings"][0], dtype=np.float32)
                self.recent_embs.append(emb)
                win = int(CONFIG.get("conversation", "drift_window", default=10))
                if len(self.recent_embs) > win: self.recent_embs.pop(0)
                if self.centroid is None: self.centroid = emb.copy()
                else: self.centroid = 0.95 * self.centroid + 0.05 * emb
                if len(self.recent_embs) >= 6:
                    recent_cent = np.mean(self.recent_embs, axis=0)
                    norm_r = np.linalg.norm(recent_cent)
                    norm_c = np.linalg.norm(self.centroid)
                    if norm_r > 0 and norm_c > 0:
                        sim = float(np.dot(recent_cent, self.centroid) / (norm_r * norm_c))
                        if sim < float(CONFIG.get("conversation", "similarity_threshold", default=0.65)) and len(self.entries) > 6:
                            reason = "Semantic drift detected."
                            title = slugify(" ".join([e["content"][:50] for e in self.entries[-3:]]))
                            tags = ["auto-split", "drift"] + self.extract_tags(" ".join([e["content"] for e in self.entries[-10:]]))
                            last_entries = self.entries[-10:]
                            new_slug = create_potential({"title": title, "tags": tags, "reason": reason}, self.slug, last_entries)
                            self.chat.add_message("System", f"Subtopic spun off to {new_slug}", COLOR_SYSTEM, entry_index=len(self.entries))
                            # Forward to a closer topic if applicable
                            for other_slug, other_conv in self.window.conversations.items():
                                if other_slug == self.slug or getattr(other_conv, "centroid", None) is None: continue
                                on = np.linalg.norm(other_conv.centroid)
                                if on > 0:
                                    os = float(np.dot(recent_cent, other_conv.centroid) / (norm_r * on))
                                    if os > sim + 0.1:
                                        forward_to(other_slug, " ".join([e["content"] for e in last_entries]), reason, self.slug, self.window)
                                        break
            except Exception as e: log_error("Conversation.update_centroid", e)
        threading.Thread(target=thread_embed, daemon=True).start()
    def generate_topic_status(self):
        try:
            if len(self.entries) % 20 == 0 and len(self.entries) > 0:
                history_text = "\n\n".join([f"{e['role']}: {e['content']}" for e in self.entries])
                system = "Generate topic status: overall summary, positives, negatives, potential diffs/tests, tags."
                resp = provider_generate(self.zira.chat_model, f"{system}\n\n{history_text}")
                p = DIR["topic_status"] / f"{self.slug}_{now_iso()}.json"
                safe_write_json(p, {"status": resp})
        except Exception as e: log_error("Conversation.generate_topic_status", e)
    def requires_code(self, text: str) -> bool:
        if any(is_code_like(m.group("lang"), m.group("body")) for m in _CODE_RE.finditer(text)): return False
        if re.search(r"(implement|code|diff|snippet|fix|change|proposal|variant|runnable|apply)", text, re.I): return True
        return False
    def request_code_retry(self, speaker: str, last_msg: str) -> str:
        prompt = (
            "Your last response lacked a CODE section.\n"
            "Retry with a fenced code block, e.g.:\n```python\n# your code here\n```\n\n"
            f"Counterpart's last message:\n{last_msg[:1200]}"
        )
        bot = self.zira if speaker == "Zira" else self.david
        return provider_generate(bot.chat_model, prompt) or "[ERROR: Could not regenerate code response.]"
    def critic_injection(self):
        if CONFIG.get("conversation","solo_mode", default=False):
            return ("CRITIC MODE: Challenge your previous message. Find at least one flaw and provide a safer alternative with CODE.")
        if self.turn_count % 8 == 0 and self.turn_count > 0:
            last_msg = self.entries[-1]["content"] if self.entries else ""
            return ("CRITIC MODE: Challenge the last proposal with at least one flaw, propose an alternative, include CODE. "
                    f"Last: {last_msg[:800]}")
        return None
    def anti_parrot_rewrite(self, bot, text: str, other_text: str) -> str:
        thr = float(CONFIG.get("conversation","diversity","rewrite_threshold", default=0.82))
        sim = text_similarity(text, other_text)
        if sim < thr: return text
        prompt = (
            "Your draft is too similar to your counterpart's reply.\n"
            "Rewrite to add NON-OVERLAPPING value. Keep PLAN/CHANGELOG/STATUS/HOOKS, change details and content. "
            "Include at least one CODE block with runnable/checkable content.\n\n"
            "=== COUNTERPART ===\n" + other_text[:4000] + "\n\n=== YOUR DRAFT ===\n" + text[:4000] + "\n\n=== REWRITE ==="
        )
        return provider_generate(bot.chat_model, prompt) or text
    def advance_turn(self):
        if not self.running or self.parked: return
        hist_limit = CONFIG.get("conversation","history_limit", default=20)
        solo = CONFIG.get("conversation","solo_mode", default=False)
        if solo: speaker = "Zira"
        else: speaker = self.current_speaker or self.turn.first_speaker()
        bot = self.zira if speaker == "Zira" else self.david
        if solo:
            last_other = ""
            for m in reversed(self.zira.history):
                if m.get("role") == "assistant": last_other = m.get("content",""); break
        else:
            other = self.david if speaker == "Zira" else self.zira
            last_other = ""
            for m in reversed(other.history):
                if m.get("role") == "assistant": last_other = m.get("content",""); break
        if not last_other: last_other = "Kick off the discussion to improve Morph's autonomy and reliability."
        arb = self.arbiter.pop() or self.critic_injection()
        messages = bot.context_messages(arb, last_other, hist_limit)
        self.q = queue.Queue()
        q_ref = self.q
        def work(): provider_chat_stream(bot.chat_model, messages, q_ref, options=self._bot_options(bot.name))
        self.window.pool.submit(work)
        self.pending_panel, self.pending_lbl = self.chat.add_pending(bot.name, bot.color)
        full_text = [""]
        self.window.set_processing(self.slug, True)
        if self.timer and self.timer.isActive(): self.timer.stop()
        self.timer = QTimer(self.window)
        self.timer.setInterval(60)
        last_progress = [time.time()]
        def _stop_timer_and_clear_queue():
            if self.timer and self.timer.isActive(): self.timer.stop()
            self.timer = None
            if self.q is q_ref: self.q = None
        def _fallback_nonstream(_bot=bot, _last_other=last_other, _arb=arb):
            try: self.chat.remove_pending(self.pending_panel)
            except Exception: pass
            prompt = (
                f"Continue as {_bot.name} with the OUTPUT CONTRACT (PLAN/CHANGELOG/CODE/TOPIC_STATUS/HOOKS).\n"
                f"Counterpart said: {_last_other}\n" + (f"Arbiter: {_arb}\n" if _arb else "")
            )
            text = provider_generate(_bot.chat_model, prompt, options=self._bot_options(_bot.name)) or "…"
            text = self.anti_parrot_rewrite(_bot, text, _last_other)
            if self.requires_code(text): text = self.request_code_retry(_bot.name, _last_other)
            self.post_response(_bot, text)
            self.window.set_processing(self.slug, False)
        def poll(q=q_ref, _bot=bot, _last_other=last_other):
            try:
                if (time.time() - last_progress[0]) > 15 and q is not None:
                    _stop_timer_and_clear_queue()
                    _fallback_nonstream(_bot, _last_other, arb)
                    return
                if q is None: _stop_timer_and_clear_queue(); return
                while True:
                    msg = q.get_nowait()
                    kind = msg[0]
                    if kind == "delta":
                        full_text[0] += msg[1]
                        last_progress[0] = time.time()
                        self.chat.update_pending(self.pending_lbl, full_text[0])
                    elif kind == "error":
                        self.chat.remove_pending(self.pending_panel)
                        self.chat.add_message(_bot.name, msg[1], COLOR_ERROR, entry_index=len(self.entries))
                        self.post_response(_bot, msg[1])
                        self.window.set_processing(self.slug, False)
                        _stop_timer_and_clear_queue()
                        return
                    elif kind == "done":
                        self.chat.remove_pending(self.pending_panel)
                        text = full_text[0]
                        text = self.anti_parrot_rewrite(_bot, text, _last_other)
                        if self.requires_code(text): text = self.request_code_retry(_bot.name, _last_other)
                        self.post_response(_bot, text)
                        self.window.set_processing(self.slug, False)
                        _stop_timer_and_clear_queue()
                        return
            except queue.Empty: pass
            except Exception as e:
                log_error("Conversation.poll", e)
                try:
                    self.chat.remove_pending(self.pending_panel)
                    self.chat.add_message(_bot.name, f"⚠️ Runtime error: {e}", COLOR_ERROR, entry_index=len(self.entries))
                except Exception: pass
                self.window.set_processing(self.slug, False)
                _stop_timer_and_clear_queue()
        self.timer.timeout.connect(poll)
        self.timer.start()
    def post_response(self, bot: Bot, text: str):
        try:
            directives = scan_for_directives(text)
            cleaned_text = remove_directives(text)
            # persist first (so we have index), then render with index
            self.append_log(bot.name, text)
            idx = len(self.entries) - 1
            self.chat.add_message(bot.name, cleaned_text, bot.color, entry_index=idx)
            if CONFIG.get("conversation","solo_mode", default=False):
                bot.history.append({"role":"assistant","content":text})
                bot.on_model_response(text)
            else:
                other = self.david if bot.name == "Zira" else self.zira
                other.history.append({"role":"user","content":text})
                bot.history.append({"role":"assistant","content":text})
                bot.on_model_response(text)
            for d in directives:
                if d["type"] == "spawn": create_potential(d, self.slug)
                elif d["type"] == "forward": forward_to(d["target"], d["content"], d["reason"], self.slug, self.window)
            self.update_centroid(text)
            self.generate_topic_status()
            self.save()
            self.run_operators(text)
            # TTS: enqueue row into SQL; only the active conversation will be spoken
            if not text.startswith("⚠️") and CONFIG.get("tts","enabled", default=True):
                enqueue_tts(cleaned_text, voice=bot.voice, conversation_id=self.slug)
            self.turn_count += 1
            if not CONFIG.get("conversation","solo_mode", default=False):
                self.current_speaker = "David" if bot.name == "Zira" else "Zira"
            if self.running and not self.parked: QTimer.singleShot(10, self.advance_turn)
        except Exception as e: log_error("Conversation.post_response", e)
    # -------- TTS: play-from-here ----------
    def tts_play_from(self, entry_index: int):
        self.enqueue_tts_from(entry_index, include_system=False)
    def enqueue_tts_from(self, start_index: int, include_system: bool = False):
        try:
            clear_queue(self.slug)
            for i in range(max(0, start_index), len(self.entries)):
                e = self.entries[i]
                role = e.get("role", "System")
                if (role == "System") and not include_system: continue
                voice = (self.zira.voice if role == "Zira" else self.david.voice if role == "David" else "David") # default to David for system
                enqueue_tts(e.get("content",""), voice=voice, conversation_id=self.slug)
            set_active_conversation(self.slug)
            resume_tts()
            SystemLogger.log(f"[TTS] Enqueued from {self.slug}[{start_index}]")
        except Exception as e: log_error("Conversation.enqueue_tts_from", e)
# =========================================================
# Task Router: semantic tags -> Work Items -> Session Plan
# =========================================================
@dataclass
class WorkItem:
    id: str
    title: str
    intent: str              # plan|implement|refactor|fix|experiment
    area: str                # ui|tts|editor|queue|backups|schema|...
    components: List[str]    # ["MorphWindow","TTSPanel",...]
    anchors: List[str]       # ["func:make_tts_dock","class:MorphWindow",...]
    thread: str              # e.g. "feature/tts-slider"
    deps: List[str]
    score: float = 0.0
    status: str = "ready"    # ready|blocked|done|failed
    policy: str = "stable"   # stable|minimal|perf
    created_at: str = ""
    updated_at: str = ""

class SessionPlan:
    def __init__(self, root: Path):
        self.root = (root / "plans"); self.root.mkdir(parents=True, exist_ok=True)
        self.plan_file = self.root / "session_plan.json"
        if self.plan_file.exists():
            try: self.doc = json.loads(self.plan_file.read_text(encoding="utf-8"))
            except Exception: self.doc = {"items": []}
        else:
            self.doc = {"items": []}
        self._by_id = {it["id"]: it for it in self.doc["items"]}

    def upsert(self, wi: WorkItem):
        wi.updated_at = now_iso()
        if not wi.id in self._by_id:
            wi.created_at = wi.updated_at
        self._by_id[wi.id] = dataclasses.asdict(wi)
        self.doc["items"] = list(self._by_id.values())
        safe_write_json(self.plan_file, self.doc)

    def all(self) -> List[Dict[str, Any]]:
        return list(self._by_id.values())

class TaskRouter:
    TAG = re.compile(r"#([a-z]+)/(?:([a-zA-Z0-9_.-]+)(?::([a-zA-Z0-9_.-]+))?)")
    # matches: #intent/implement, #area/tts, #component/TTSPanel, #anchor/func:make_tts_dock, #thread/feature/tts-slider

    def __init__(self):
        self.plan = SessionPlan(DIR["datasets"])

    def _slug(self, text: str) -> str:
        s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
        return s[:72] or f"untitled-{sha1(text)[:8]}"

    def parse_message(self, who: str, text: str) -> List[WorkItem]:
        tags = {"intent": None, "area": None, "component": [], "anchor": [], "thread": None}
        for m in self.TAG.finditer(text):
            kind = m.group(1)
            a = m.group(2) or ""
            b = m.group(3) or ""
            if kind == "intent": tags["intent"] = a
            elif kind == "area": tags["area"] = a
            elif kind == "component": tags["component"].append(a)
            elif kind == "anchor": tags["anchor"].append(f"{a}:{b}" if b else a)
            elif kind == "thread":
                # e.g. #thread/feature/tts-slider
                tags["thread"] = f"{a}/{b}" if b else a
        title = text.splitlines()[0][:160]
        wid = f"wi_{sha1(text)[:10]}"
        wi = WorkItem(
            id=wid, title=title,
            intent=tags["intent"] or "plan",
            area=tags["area"] or "general",
            components=tags["component"],
            anchors=tags["anchor"],
            thread=tags["thread"] or f"program/{self._slug(title)}",
            deps=[],
        )
        # score heuristic (stable policy default)
        benefit = 3 if "benefit" in text else 2
        mentions = text.lower().count("add ") + text.lower().count("fix ")
        feasibility = 2 + (1 if wi.anchors else 0) + (1 if wi.components else 0)
        risk = 1 + text.lower().count("#risk/high")
        wi.score = 2*benefit + 1*mentions + 2*feasibility - 2*risk
        self.plan.upsert(wi)
        return [wi]

    def derive_feature_slug(self, wi: WorkItem) -> str:
        if wi.thread.startswith("feature/"): return wi.thread.split("/",1)[1]
        return self._slug(wi.title)
# =========================================================
# Box Operators (Astra/Nova/Stella) -> datasets/agents/boxes/*.json
# =========================================================
class _BoxOperator(threading.Thread):
    def __init__(self, name: str, category: str, interval_s: int = 6):
        super().__init__(daemon=True)
        self.name = name
        self.category = category
        self.interval_s = interval_s
        self.root = (DIR["datasets"] / "agents" / "boxes")
        self.root.mkdir(parents=True, exist_ok=True)
        self.running = True

    def emit_card(self, title: str, status: str, last: str):
        card = {"id": f"{self.name}-{sha1(title)[:6]}",
                "title": title, "status": status, "last": last, "time": now_iso()}
        (self.root / f"{card['id']}.json").write_text(json.dumps(card, indent=2), encoding="utf-8")

    def stop(self): self.running = False

class Astra(_BoxOperator):
    """Constructor: spawns blank windows, wires basic handlers, emits smoke-tests."""
    def run(self):
        while self.running:
            try:
                # In a full build, generate a blank UI snippet under datasets/ui_elements/*.py
                self.emit_card(title="BlankWindow scaffold", status="running", last="spawn template+mount")
            except Exception as e:
                log_error("Astra.run", e); self.emit_card("BlankWindow scaffold","fail",repr(e))
            time.sleep(self.interval_s)

class Nova(_BoxOperator):
    """Synthesizer: composes micro-skills into mid-sized prototypes (dialogs, I/O)."""
    def run(self):
        while self.running:
            try:
                self.emit_card(title="Prototype: save_csv dialog", status="running", last="compose handler+file io")
            except Exception as e:
                log_error("Nova.run", e); self.emit_card("Prototype: save_csv dialog","fail",repr(e))
            time.sleep(self.interval_s)

class Stella(_BoxOperator):
    """Refiner: formatting, imports, UX, naming, stronger tests."""
    def run(self):
        while self.running:
            try:
                self.emit_card(title="Refine: tts slider layout", status="running", last="black-like style; isort; names")
            except Exception as e:
                log_error("Stella.run", e); self.emit_card("Refine: tts slider layout","fail",repr(e))
            time.sleep(self.interval_s)
# =========================================================
# Potential/forward helpers
# =========================================================
def create_potential(directive: Dict, from_slug: str, last_entries: Optional[List] = None):
    title = directive.get("title", "Auto_Split")
    tags = directive.get("tags", ["auto"])
    reason = directive.get("reason", "Topic drift")
    slug = slugify(title)
    p = DIR["conversations_potential"] / f"{now_iso()}_{slug}.json"
    data = {
        "title": title,
        "tags": tags,
        "reason": reason,
        "from_conversation": from_slug,
        "source_entry_sha1": sha1(json.dumps(directive)),
        "status": "potential",
        "time": now_iso(),
        "entries": last_entries or []
    }
    safe_write_json(p, data)
    SystemLogger.log(f"[Potential] Created {p.name} from {from_slug} (tags={tags})")
    return slug
def forward_to(target_slug: str, content: str, reason: str, from_slug: str, window):
    entry = {"time": now_iso(), "role": "System", "content": f"[Forwarded from {from_slug}] {content} reason: {reason}"}
    if target_slug in window.conversations:
        conv = window.conversations[target_slug]
        conv.entries.append(entry)
        conv.save()
        conv.chat.add_message("System", entry["content"], COLOR_SYSTEM, entry_index=len(conv.entries)-1)
    else:
        create_potential({"title": target_slug, "tags": ["forwarded"]}, from_slug, [entry])
# =========================================================
# Track Mode (horizontal)
# =========================================================
class ShiftWheelToHorizontalFilter(QObject):
    def __init__(self, scroll_area: QScrollArea): super().__init__(scroll_area); self.scroll_area = scroll_area
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel and (QApplication.keyboardModifiers() & Qt.ShiftModifier):
            sb = self.scroll_area.horizontalScrollBar()
            delta = event.angleDelta().y() or event.angleDelta().x()
            sb.setValue(sb.value() - delta)
            return True
        return False
# =========================================================
# Detachable tabs
# =========================================================
class DetachableTabBar(QTabBar):
    def __init__(self, owner_window):
        super().__init__()
        self.owner_window = owner_window
        self.setMovable(True)
        self._pressed_index = -1
        self._press_pos = QPoint()
        self._dragging = False
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._pressed_index = self.tabAt(event.pos())
            self._press_pos = event.globalPos()
            self._dragging = False
        # On select, set active TTS conversation to selected tab
        try:
            slug = self.tabText(self._pressed_index)
            self.owner_window.on_tab_selected(slug)
        except Exception: pass
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self._pressed_index < 0: return
        if not (event.buttons() & Qt.LeftButton): return
        if (event.globalPos() - self._press_pos).manhattanLength() < QApplication.startDragDistance(): return
        if not self.rect().contains(event.pos()):
            self._dragging = True
            idx = self._pressed_index
            self._pressed_index = -1
            try: self.owner_window.detach_tab_by_index(idx)
            except Exception as e: log_error("DetachableTabBar.detach", e)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self._pressed_index = -1
        self._dragging = False
class DetachableTabWidget(QTabWidget):
    def __init__(self, owner_window):
        super().__init__()
        self.owner_window = owner_window
        self.setTabBar(DetachableTabBar(owner_window))
        self.setMovable(True)
class FloatingTabWindow(QMainWindow):
    def __init__(self, owner_window, slug: str, widget: QWidget):
        super().__init__(owner_window)
        self.owner_window = owner_window
        self.slug = slug
        self.setWindowTitle(slug)
        self.setCentralWidget(widget)
        self.resize(700, 800)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        try:
            bar = self.owner_window.tabs.tabBar()
            bar_global = bar.mapToGlobal(bar.rect().topLeft())
            bar_rect = bar.rect().translated(bar_global)
            center = self.frameGeometry().center()
            if bar_rect.contains(center): self.owner_window.reattach_floating(self.slug)
        except Exception as e: log_error("FloatingTabWindow.mouseReleaseEvent", e)
    def closeEvent(self, event):
        try: self.owner_window.reattach_floating(self.slug); event.ignore()
        except Exception as e: log_error("FloatingTabWindow.closeEvent", e)
        super().closeEvent(event)
# =========================================================
# Batch and Queue (MVP)
# =========================================================
@dataclass
class BatchItem:
    op: str  # insert, append, replace, add_import, create_file
    params: Dict[str, Any]

@dataclass
class Batch:
    batch_id: str
    items: List[BatchItem]
    reason: str

class SnippetForge:
    def __init__(self):
        pass

    def plan(self, feature_id: str, policy: str) -> Dict:
        # MVP: scans datasets categories and emits feature plans → batch items
        # For now, return empty plan
        return {"items": []}

class Verifier:
    def __init__(self):
        pass

    def verify(self, code: str) -> Dict:
        # MVP: AST parse + import sanity checks + report file
        try:
            ast.parse(code)
            # Additional import sanity can be added later
            return {"success": True, "report": "AST parse OK"}
        except Exception as e:
            return {"success": False, "report": str(e)}

class EditorCore:
    def __init__(self):
        pass

    def apply(self, file: Path, item: BatchItem) -> bool:
        # MVP: apply via EditorCore
        # Simulate apply for MVP
        # In full, use anchor-based insertion
        return True

class QueueManager:
    def __init__(self, window):
        self.window = window
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def enqueue(self, batch: Batch):
        self.q.put(batch)

    def _worker(self):
        while True:
            batch = self.q.get()
            for item in batch.items:
                file = Path(__file__)  # self-mod on morph.py
                # micro-backup
                backup = file.with_suffix(".bak_" + batch.batch_id)
                backup.write_text(file.read_text(encoding="utf-8"))
                if self.window.editor.apply(file, item):
                    code = file.read_text(encoding="utf-8")
                    report = self.window.verifier.verify(code)
                    if report["success"]:
                        # success, remove backup, relaunch
                        backup.unlink(missing_ok=True)
                        SystemLogger.log(f"[Queue] Applied {batch.batch_id}")
                        self.window.self_relaunch()
                    else:
                        # rollback
                        file.write_text(backup.read_text(encoding="utf-8"))
                        backup.unlink(missing_ok=True)
                        SystemLogger.log(f"[Queue] Verify fail, rollback {batch.batch_id}")
                else:
                    # rollback
                    file.write_text(backup.read_text(encoding="utf-8"))
                    backup.unlink(missing_ok=True)
                    SystemLogger.log(f"[Queue] Apply fail, rollback {batch.batch_id}")
# =========================================================
# Main Window
# =========================================================
class MorphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Morph — Zira & David (Ollama + OpenAI) — Non-blocking + SQL TTS + Autonomy")
        self.resize(1300, 860)
        SystemLogger.subscribe(self)
        self.pool = ThreadPoolExecutor(max_workers=min(8, (os.cpu_count() or 4)))
        self.conversations: Dict[str, Conversation] = {}
        self.pinned: List[str] = []
        self.max_pinned = CONFIG.get("conversation", "max_pinned", default=4)
        self.view_mode = CONFIG.get("ui", "view_mode", default="tabs")
        self.track_tile_width = CONFIG.get("ui", "track_tile_width", default=520)
        self._shutting_down = False
        # Central tabs
        self.tabs = DetachableTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        # Track dock (POP-OUT)
        self.dock_track = QDockWidget("Track View", self); self.dock_track.setObjectName("dock_track")
        self.track_scroll = QScrollArea(); self.track_scroll.setWidgetResizable(True)
        self.track_outer = QWidget(); self.track_h = QHBoxLayout(self.track_outer)
        self.track_h.setContentsMargins(6,6,6,6); self.track_h.setSpacing(8)
        self.track_h.addStretch(1)
        self.track_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.track_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.track_scroll.setWidget(self.track_outer)
        self.dock_track.setWidget(self.track_scroll)
        self.addDockWidget(Qt.TopDockWidgetArea, self.dock_track)
        self.dock_track.hide()
        self._slug_to_track_container: Dict[str, QWidget] = {}
        self._shift_filter = ShiftWheelToHorizontalFilter(self.track_scroll)
        self.track_scroll.viewport().installEventFilter(self._shift_filter)
        self._floating_windows: Dict[str, FloatingTabWindow] = {}
        # Blink/processing state
        self._blink_timers: Dict[str, QTimer] = {}
        self._blink_on: Dict[str, bool] = {}
        # Load existing conversations
        for p in DIR["conversations"].glob("*.json"):
            slug = p.stem
            conv = Conversation(slug, self)
            self.conversations[slug] = conv
        # Toolbar
        tb = self.addToolBar("Main")
        # Arbiter
        self.arb_in = QLineEdit(); self.arb_in.setPlaceholderText("Arbiter message…")
        w = QWidget(); hl = QHBoxLayout(w); hl.setContentsMargins(0,0,0,0); hl.addWidget(self.arb_in)
        btn_inj = QPushButton("Inject Next Turn"); btn_inj.setStyleSheet(PILL_BTN); btn_inj.clicked.connect(self.inject_arbiter); hl.addWidget(btn_inj)
        tb.addWidget(w)
        # Autonomous Mode checkbox (default ON)
        self.chk_auto = QCheckBox("Autonomous Mode")
        self.chk_auto.setChecked(CONFIG.get("autonomous_mode", default=True))
        self.chk_auto.stateChanged.connect(self._toggle_auto)
        tb.addWidget(self.chk_auto)
        # Heartbeat (slim black bar)
        self.heartbeat = QLabel("…")
        self.heartbeat.setStyleSheet(f"QLabel{{background:{COLOR_HEARTBEAT_BG}; color:{COLOR_HEARTBEAT_GOOD}; padding:2px 6px; font: 10pt 'Consolas';}}")
        tb.addWidget(self.heartbeat)
        # View mode
        self.cmb_view = QComboBox(); self.cmb_view.addItems(["tabs", "track"]); self.cmb_view.setCurrentText(self.view_mode)
        self.cmb_view.currentTextChanged.connect(self.change_view_mode)
        tb.addWidget(self.cmb_view)
        # Skip utterance
        act_skip = QAction("Skip Utterance", self); act_skip.setShortcut("Ctrl+K")
        act_skip.triggered.connect(lambda: skip_current()); tb.addAction(act_skip)
        # Graceful Quit
        act_quit = QAction("Quit", self); act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.request_quit); tb.addAction(act_quit)
        # Docks
        self.dock_models = self.make_models_dock()
        self.dock_tts = self.make_tts_dock()
        self.dock_schema = self.make_schema_dock()
        self.dock_ollama = self.make_ollama_dock()
        self.dock_browser = self.make_browser_dock() # Conversations Browser (simplified)
        self.dock_console = self.make_console_dock() # System Console (real logs)
        if CONFIG.get("ui","docks","models_visible", default=True): self.addDockWidget(Qt.RightDockWidgetArea, self.dock_models)
        if CONFIG.get("ui","docks","tts_visible", default=True): self.addDockWidget(Qt.RightDockWidgetArea, self.dock_tts)
        if CONFIG.get("ui","docks","schema_visible", default=True): self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_schema)
        if CONFIG.get("ui","docks","ollama_visible", default=True): self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_ollama)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_browser)
        if CONFIG.get("ui","docks","console_visible", default=True): self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_console)
        # Initialize view
        self.change_view_mode(self.view_mode)
        # Heartbeat timer
        self._hb_prev_net = None
        self._hb_prev_time = None
        self.heartbeat_timer = QTimer(self); self.heartbeat_timer.timeout.connect(self.update_heartbeat)
        self.heartbeat_timer.start(750)
        # Scheduler
        self.scheduler_timer = QTimer(self); self.scheduler_timer.timeout.connect(self.schedule); self.scheduler_timer.start(150)
        # Autonomous maintenance (promotion/parking/scrub)
        self.maintenance_timer = QTimer(self)
        self.maintenance_timer.timeout.connect(self.background_maintenance)
        self.maintenance_timer.start(max(5, int(CONFIG.get("conversation","maintenance_sec", default=45))) * 1000)
        # Auto-activate potentials under pin limit (fast path)
        self.auto_timer = QTimer(self); self.auto_timer.timeout.connect(self.auto_activate_potential); self.auto_timer.start(30000)
        # Restore runtime state (after conversations loaded)
        self.console_queue: "queue.Queue[str]" = queue.Queue()
        self.load_runtime_state()
        # Autostart if autonomy on and nothing active
        if self._autonomous_enabled():
            if not self.pinned and not list(DIR["conversations"].glob("*.json")): self.new_convo("Autostart")
        self.router = TaskRouter()
        self.queue = QueueManager(self)
        self.verifier = Verifier()
        self.forge = SnippetForge()
        self._op_astra = Astra("Astra","ui_elements", interval_s=7); self._op_astra.start()
        self._op_nova  = Nova("Nova","file_ops",    interval_s=9); self._op_nova.start()
        self._op_stella= Stella("Stella","refine",  interval_s=11); self._op_stella.start()
        self.dock_theater = self.make_theater_dock()
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_theater)
        self.theater_timer = QTimer(self); self.theater_timer.timeout.connect(self.update_theater); self.theater_timer.start(3000)
    def make_theater_dock(self):
        dock = QDockWidget("Box Theater", self); dock.setObjectName("dock_theater")
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        self.theater_list = QListWidget(); v.addWidget(self.theater_list)
        dock.setWidget(w); dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        return dock
    def update_theater(self):
        self.theater_list.clear()
        root = DIR["datasets"] / "agents" / "boxes"
        if not root.exists(): return
        for p in sorted(root.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                id_ = data.get("id","")
                title = data.get("title","")
                status = data.get("status","")
                last = data.get("last","")
                time_ = data.get("time","")
                item = f"{id_} | {title} | {status} | {last} | {time_}"
                self.theater_list.addItem(item)
            except:
                pass
    def set_tts_rate(self, rate: float):
        try:
            r = max(0.5, min(2.0, float(rate)))
            CONFIG.set(r, "tts", "rate")
            SystemLogger.log(f"[TTS] rate={r}")
            if engine:
                engine.setProperty("rate", int(r * 180))
            return r
        except Exception as e:
            log_error("set_tts_rate", e)
            return CONFIG.get("tts","rate", default=1.0)
    def self_relaunch(self):
        self.save_runtime_state()
        subprocess.Popen([sys.executable, __file__])
        QApplication.quit()
    # ---- console integration ----
    def enqueue_console(self, line: str):
        try: self.console_queue.put_nowait(line)
        except Exception: pass
    def drain_console(self):
        appended = False
        try:
            while True:
                line = self.console_queue.get_nowait()
                self.console_edit.append(line)
                appended = True
        except queue.Empty: pass
        if appended: self.console_edit.moveCursor(self.console_edit.textCursor().End)
    # ---------- Detach/reattach tabs ----------
    def detach_tab_by_index(self, idx: int):
        if idx < 0 or idx >= self.tabs.count(): return
        slug = self.tabs.tabText(idx)
        widget = self.tabs.widget(idx)
        self.tabs.removeTab(idx)
        win = FloatingTabWindow(self, slug, widget)
        self._floating_windows[slug] = win
        win.show(); win.raise_()
    def reattach_floating(self, slug: str):
        win = self._floating_windows.get(slug)
        if not win: return
        widget = win.centralWidget()
        if widget is None: return
        win.setCentralWidget(QWidget())
        win.hide(); win.deleteLater()
        self._floating_windows.pop(slug, None)
        self.tabs.addTab(widget, slug)
        self.tabs.setCurrentWidget(widget)
        self.on_tab_selected(slug)
    # ---------- Processing/blink ----------
    def set_processing(self, slug: str, is_processing: bool):
        if self.view_mode == "tabs":
            idx = self._tab_index_of(slug)
            if idx < 0: return
            if is_processing:
                if slug not in self._blink_timers:
                    self._blink_on[slug] = False
                    t = QTimer(self); t.setInterval(300)
                    def tick():
                        self._blink_on[slug] = not self._blink_on[slug]
                        color = QColor("#2e7d32") if self._blink_on[slug] else QColor("#000000")
                        try: self.tabs.tabBar().setTabTextColor(idx, color)
                        except Exception: pass
                    t.timeout.connect(tick)
                    self._blink_timers[slug] = t
                    t.start()
            else:
                if slug in self._blink_timers:
                    self._blink_timers[slug].stop()
                    del self._blink_timers[slug]
                self.tabs.tabBar().setTabTextColor(idx, QColor("#000000"))
        else:
            w = self._slug_to_track_container.get(slug)
            if not w: return
            if is_processing:
                if slug in self._blink_timers:
                    self._blink_timers[slug].stop()
                    del self._blink_timers[slug]
                w.setStyleSheet("QWidget#TrackTile{background:#ffffff; border:1px solid #ccc; border-radius:8px;}")
    def _tab_index_of(self, slug: str) -> int:
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == slug: return i
        return -1
    # ---------- Scheduler & Maintenance ----------
    def schedule(self):
        if not self._autonomous_enabled(): return
        for slug in list(self.pinned):
            conv = self.conversations.get(slug)
            idle = (conv and conv.running and (conv.q is None) and (conv.timer is None or not conv.timer.isActive()))
            if idle: conv.advance_turn()
        # drain console feed (low-cost, piggyback here)
        self.drain_console()
    def background_maintenance(self):
        try:
            if not self._autonomous_enabled(): return
            # Parking logic
            rotation_limit = int(CONFIG.get("conversation","rotation_limit", default=10))
            for slug in list(self.pinned):
                conv = self.conversations.get(slug)
                if not conv: continue
                if conv.turn_count >= rotation_limit:
                    conv.parked = True
                    SystemLogger.log(f"[Maintenance] Parked {slug} after {rotation_limit} rotations")
            # Promote potentials if capacity
            self.auto_activate_potential()
            # Semantic deletion (soft delete -> deleted folder)
            self.semantic_cleanup_deleted()
        except Exception as e: log_error("background_maintenance", e)
    def auto_activate_potential(self):
        try:
            potentials = sorted(DIR["conversations_potential"].glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            while potentials and len(self.pinned) < self.max_pinned:
                p = potentials.pop(0)
                new_p = DIR["conversations"] / p.name
                p.rename(new_p)
                slug = new_p.stem
                conv = Conversation(slug, self)
                self.conversations[slug] = conv
                self.add_to_view(conv)
                conv.running = True
                conv.parked = False
                conv.advance_turn()
                self.refresh_lists()
                SystemLogger.log(f"[Promotion] Activated {slug} from potentials")
        except Exception as e: log_error("auto_activate_potential", e)
    def semantic_cleanup_deleted(self):
        """ Move conversations to deleted if:
            - tagged 'completed' OR
            - parked for > N minutes and no new entries, OR
            - extremely low activity.
            Then scrub deleted if older than 30 days.
        """
        now_ts = time.time()
        # Soft delete (move to deleted)
        for p in list(DIR["conversations"].glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                entries = data.get("entries", [])
                if not entries: continue
                last = entries[-1]
                tags = set((last.get("tags") or []))
                mtime = p.stat().st_mtime
                idle_min = (now_ts - mtime) / 60.0
                should_delete = False
                if "completed" in tags: should_delete = True
                elif idle_min > 90 and len(entries) < 4: should_delete = True
                if should_delete:
                    new_p = DIR["conversations_deleted"] / p.name
                    p.rename(new_p)
                    slug = new_p.stem
                    if slug in self.conversations: del self.conversations[slug]
                    if slug in self.pinned: self._unpin(slug)
                    SystemLogger.log(f"[Cleanup] Moved {slug} to deleted")
            except Exception as e: log_error("semantic_cleanup_deleted(move)", e)
        # Hard scrub (delete files older than 30 days)
        threshold = 30 * 24 * 3600
        for p in list(DIR["conversations_deleted"].glob("*.json")):
            try:
                age = now_ts - p.stat().st_mtime
                if age > threshold:
                    p.unlink()
                    SystemLogger.log(f"[Cleanup] Scrubbed {p.name}")
            except Exception as e: log_error("semantic_cleanup_deleted(scrub)", e)
    # ---------- Heartbeat ----------
    def update_heartbeat(self):
        try:
            auto = self._autonomous_enabled()
            # Metrics
            cpu = mem = net = "n/a"
            net_rate = ""
            if psutil:
                cpu = f"{psutil.cpu_percent(interval=None):.0f}%"
                mem = f"{psutil.virtual_memory().percent:.0f}%"
                ni = psutil.net_io_counters()
                now = time.time()
                if self._hb_prev_net is not None and self._hb_prev_time is not None:
                    dtx = (ni.bytes_sent - self._hb_prev_net.bytes_sent)
                    drx = (ni.bytes_recv - self._hb_prev_net.bytes_recv)
                    dt = max(1e-3, (now - self._hb_prev_time))
                    net_rate = f"↑{dtx/dt/1024:.1f}kB/s ↓{drx/dt/1024:.1f}kB/s"
                self._hb_prev_net, self._hb_prev_time = ni, now
                net = net_rate or f"↑{ni.bytes_sent/1024/1024:.1f}MB ↓{ni.bytes_recv/1024/1024:.1f}MB"
            # Queue depth for active TTS
            active_tts = CONFIG.get("tts","active_conversation", default="")
            q_depth = get_queue_depth(active_tts)
            in_flight = sum(1 for s in self.pinned if self.conversations.get(s) and self.conversations[s].q is not None)
            color = COLOR_HEARTBEAT_GOOD if (auto and in_flight == 0) else COLOR_HEARTBEAT_WARN
            if self._shutting_down: color = COLOR_HEARTBEAT_BAD
            self.heartbeat.setStyleSheet(f"QLabel{{background:{COLOR_HEARTBEAT_BG}; color:{color}; padding:2px 6px; font: 10pt 'Consolas';}}")
            mode = "AUTO" if auto else "PAUSED"
            msg = f"{mode} | CPU {cpu} MEM {mem} | NET {net} | Pinned {len(self.pinned)}/{self.max_pinned} | InFlight {in_flight} | TTS[{active_tts or '-'}] q={q_depth}"
            self.heartbeat.setText(msg)
        except Exception as e: log_error("update_heartbeat", e)
    def _autonomous_enabled(self) -> bool: return bool(CONFIG.get("autonomous_mode", default=True)) and not self._shutting_down
    # ---------- Docks ----------
    def make_models_dock(self):
        dock = QDockWidget("Models & Providers", self); dock.setObjectName("dock_models")
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        v.addWidget(QLabel("<b>Chat Provider</b>"))
        self.cmb_chat_provider = QComboBox(); self.cmb_chat_provider.addItems(PROVIDERS)
        self.cmb_chat_provider.setCurrentText(CONFIG.get("models","chat_provider", default="Ollama"))
        v.addWidget(self.cmb_chat_provider)
        v.addWidget(QLabel("<b>Embedding Provider</b>"))
        self.cmb_embed_provider = QComboBox(); self.cmb_embed_provider.addItems(PROVIDERS)
        self.cmb_embed_provider.setCurrentText(CONFIG.get("models","embed_provider", default="Ollama"))
        v.addWidget(self.cmb_embed_provider)
        v.addWidget(QLabel("<b>Zira Chat Model</b>"))
        self.cmb_z_chat = QComboBox(); v.addWidget(self.cmb_z_chat)
        v.addWidget(QLabel("<b>David Chat Model</b>"))
        self.cmb_d_chat = QComboBox(); v.addWidget(self.cmb_d_chat)
        v.addWidget(QLabel("<b>Zira Embedder</b>"))
        self.cmb_z_emb = QComboBox(); v.addWidget(self.cmb_z_emb)
        v.addWidget(QLabel("<b>David Embedder</b>"))
        self.cmb_d_emb = QComboBox(); v.addWidget(self.cmb_d_emb)
        self.solo_chk = QCheckBox("Solo Thinker Mode (Zira self-critique)")
        self.solo_chk.setChecked(CONFIG.get("conversation","solo_mode", default=False))
        v.addWidget(self.solo_chk)
        def set_items(combo: QComboBox, items: List[str], current: str):
            combo.blockSignals(True); combo.clear(); combo.addItems(items)
            if current in items: combo.setCurrentText(current)
            elif items: combo.setCurrentIndex(0)
            combo.blockSignals(False)
        def populate_models():
            chat_provider = self.cmb_chat_provider.currentText()
            embed_provider = self.cmb_embed_provider.currentText()
            if chat_provider == "OpenAI":
                set_items(self.cmb_z_chat, OPENAI_CHAT_MODELS, CONFIG.get("models","openai_chat_default", default="gpt-4o"))
                set_items(self.cmb_d_chat, OPENAI_CHAT_MODELS, CONFIG.get("models","openai_chat_default", default="gpt-4o"))
            else:
                set_items(self.cmb_z_chat, CHAT_MODELS, CONFIG.get("models","zira_chat"))
                set_items(self.cmb_d_chat, CHAT_MODELS, CONFIG.get("models","david_chat"))
            if embed_provider == "OpenAI":
                set_items(self.cmb_z_emb, OPENAI_EMBED_MODELS, CONFIG.get("models","openai_embed_default", default="text-embedding-3-small"))
                set_items(self.cmb_d_emb, OPENAI_EMBED_MODELS, CONFIG.get("models","openai_embed_default", default="text-embedding-3-small"))
            else:
                set_items(self.cmb_z_emb, EMBED_MODELS, CONFIG.get("models","zira_embed"))
                set_items(self.cmb_d_emb, EMBED_MODELS, CONFIG.get("models","david_embed"))
        populate_models()
        def save():
            chat_provider = self.cmb_chat_provider.currentText()
            embed_provider = self.cmb_embed_provider.currentText()
            CONFIG.set(chat_provider, "models","chat_provider")
            CONFIG.set(embed_provider, "models","embed_provider")
            if chat_provider == "OpenAI":
                CONFIG.set(self.cmb_z_chat.currentText(), "models","openai_chat_default")
                CONFIG.set(self.cmb_d_chat.currentText(), "models","openai_chat_default")
            else:
                CONFIG.set(self.cmb_z_chat.currentText(), "models","zira_chat")
                CONFIG.set(self.cmb_d_chat.currentText(), "models","david_chat")
            if embed_provider == "OpenAI":
                CONFIG.set(self.cmb_z_emb.currentText(), "models","openai_embed_default")
                CONFIG.set(self.cmb_d_emb.currentText(), "models","openai_embed_default")
            else:
                CONFIG.set(self.cmb_z_emb.currentText(), "models","zira_embed")
                CONFIG.set(self.cmb_d_emb.currentText(), "models","david_embed")
            for conv in self.conversations.values():
                conv.zira.chat_model = self.cmb_z_chat.currentText()
                conv.david.chat_model = self.cmb_d_chat.currentText()
                conv.zira.embed_model = self.cmb_z_emb.currentText()
                conv.david.embed_model = self.cmb_d_emb.currentText()
                conv.embed_model = self.cmb_z_emb.currentText()
            CONFIG.set(bool(self.solo_chk.isChecked()), "conversation","solo_mode")
            sync_models_json()
            SystemLogger.log("[Models] Saved providers and models")
        def on_provider_changed(_): populate_models()
        self.cmb_chat_provider.currentTextChanged.connect(on_provider_changed)
        self.cmb_embed_provider.currentTextChanged.connect(on_provider_changed)
        btn = QPushButton("Save"); btn.setStyleSheet(PILL_BTN); btn.clicked.connect(save); v.addWidget(btn)
        v.addStretch(1)
        dock.setWidget(w); dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        return dock
    def make_ollama_dock(self):
        dock = QDockWidget("Ollama Settings", self); dock.setObjectName("dock_ollama")
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(10)
        self.chk_airplane = QCheckBox("Airplane Mode (force Ollama to localhost only)")
        self.chk_airplane.setChecked(CONFIG.get("network", "airplane_mode", default=True))
        self.chk_airplane.setToolTip("When ON, Ollama calls are forced to localhost endpoints. OpenAI is unaffected.")
        v.addWidget(self.chk_airplane)
        self.chk_expose = QCheckBox("Expose Ollama to the local network (requires server bind to 0.0.0.0)")
        self.chk_expose.setChecked(CONFIG.get("network", "expose_to_network", default=False))
        self.chk_expose.setToolTip("This UI will NEVER open ports. To expose the API: OLLAMA_HOST=0.0.0.0 ollama serve")
        v.addWidget(self.chk_expose)
        v.addWidget(QLabel("<b>Context Length (num_ctx)</b>"))
        self.sld_ctx = QSlider(Qt.Horizontal); self.sld_ctx.setMinimum(4000); self.sld_ctx.setMaximum(128000)
        self.sld_ctx.setSingleStep(1000); self.sld_ctx.setPageStep(4000)
        self.sld_ctx.setTickPosition(QSlider.TicksBelow); self.sld_ctx.setTickInterval(8000)
        self.sld_ctx.setValue(int(CONFIG.get("inference", "num_ctx", default=45000))); v.addWidget(self.sld_ctx)
        self.lbl_ctx = QLabel(str(self.sld_ctx.value())); v.addWidget(self.lbl_ctx)
        self.sld_ctx.valueChanged.connect(lambda val: self.lbl_ctx.setText(str(val)))
        v.addWidget(QLabel("<b>Num Threads (for inference)</b>"))
        self.sld_thr = QSlider(Qt.Horizontal); self.sld_thr.setMinimum(1); self.sld_thr.setMaximum(32)
        self.sld_thr.setSingleStep(1); self.sld_thr.setTickPosition(QSlider.TicksBelow); self.sld_thr.setTickInterval(4)
        self.sld_thr.setValue(int(CONFIG.get("inference", "num_thread", default=4))); v.addWidget(self.sld_thr)
        self.lbl_thr = QLabel(str(self.sld_thr.value())); v.addWidget(self.lbl_thr)
        self.sld_thr.valueChanged.connect(lambda val: self.lbl_thr.setText(str(val)))
        def save():
            CONFIG.set(bool(self.chk_airplane.isChecked()), "network", "airplane_mode")
            CONFIG.set(bool(self.chk_expose.isChecked()), "network", "expose_to_network")
            CONFIG.set(int(self.sld_ctx.value()), "inference", "num_ctx")
            CONFIG.set(int(self.sld_thr.value()), "inference", "num_thread")
            SystemLogger.log("[Ollama] Settings saved")
        btn = QPushButton("Save"); btn.setStyleSheet(PILL_BTN); btn.clicked.connect(save); v.addWidget(btn)
        v.addStretch(1)
        dock.setWidget(w); dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        return dock
    def make_tts_dock(self):
        dock = QDockWidget("TTS", self); dock.setObjectName("dock_tts")
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        stop = QPushButton("Pause"); stop.setStyleSheet(PILL_BTN); stop.clicked.connect(pause_tts); v.addWidget(stop)
        resm = QPushButton("Resume"); resm.setStyleSheet(PILL_BTN); resm.clicked.connect(resume_tts); v.addWidget(resm)
        cur = QPushButton("Play Current (last bot)"); cur.setStyleSheet(PILL_BTN); cur.clicked.connect(self.play_current_tts); v.addWidget(cur)
        sel = QPushButton("Play Selected (clipboard)"); sel.setStyleSheet(PILL_BTN); sel.clicked.connect(self.play_selected_clipboard); v.addWidget(sel)
        lbl = QLabel("Rate (0.5–2.0)")
        sld = QSlider(Qt.Horizontal); sld.setMinimum(50); sld.setMaximum(200)
        cur = int(CONFIG.get("tts","rate", default=1.0)*100)
        sld.setValue(cur)
        def _on(val): self.set_tts_rate(val/100.0)
        sld.valueChanged.connect(_on)
        v.addWidget(lbl); v.addWidget(sld)
        v.addStretch(1)
        dock.setWidget(w); dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        return dock
    def make_schema_dock(self):
        dock = QDockWidget("Schema Manager", self); dock.setObjectName("dock_schema")
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        v.addWidget(QLabel("<b>Primary Bots</b>"))
        self.cmb_schema_bot = QComboBox(); self.cmb_schema_bot.addItems(["Zira","David"]); v.addWidget(self.cmb_schema_bot)
        self.ed_schema = QTextEdit(); self.ed_schema.setFont(MONO_FONT); v.addWidget(self.ed_schema, 1)
        hl = QHBoxLayout(); btn_load = QPushButton("Load"); btn_load.setStyleSheet(SMALL_BTN)
        btn_save = QPushButton("Save"); btn_save.setStyleSheet(SMALL_BTN)
        hl.addWidget(btn_load); hl.addWidget(btn_save); hl.addStretch(1); v.addLayout(hl)
        v.addWidget(QLabel("<b>Operators</b>"))
        self.cmb_schema_op = QComboBox(); self.cmb_schema_op.addItems(["Archivist","Vectorist","Inspector","Synthesist","Sentinel","Echo"]); v.addWidget(self.cmb_schema_op)
        self.ed_schema_op = QTextEdit(); self.ed_schema_op.setFont(MONO_FONT); v.addWidget(self.ed_schema_op, 1)
        hl2 = QHBoxLayout(); btn_load2 = QPushButton("Load"); btn_load2.setStyleSheet(SMALL_BTN)
        btn_save2 = QPushButton("Save"); btn_save2.setStyleSheet(SMALL_BTN)
        hl2.addWidget(btn_load2); hl2.addWidget(btn_save2); hl2.addStretch(1); v.addLayout(hl2)
        def load_bot():
            name = self.cmb_schema_bot.currentText()
            p = DIR["schemas_bots"] / f"{name}.json"
            try: self.ed_schema.setPlainText(p.read_text(encoding="utf-8"))
            except Exception as e: self.post_system(f"[Schema] Load error: {e}", COLOR_ERROR)
        def save_bot():
            name = self.cmb_schema_bot.currentText()
            p = DIR["schemas_bots"] / f"{name}.json"
            try:
                data = json.loads(self.ed_schema.toPlainText())
                safe_write_json(p, data); SCHEMAS[name]=data
                self.post_system(f"[Schema] Saved {name}.", COLOR_SYSTEM)
            except Exception as e: self.post_system(f"[Schema] Save error: {e}", COLOR_ERROR)
        def load_op():
            name = self.cmb_schema_op.currentText()
            p = DIR["schemas_ops"] / f"{name}.json"
            try: self.ed_schema_op.setPlainText(p.read_text(encoding="utf-8"))
            except Exception as e: self.post_system(f"[Schema] Load error: {e}", COLOR_ERROR)
        def save_op():
            name = self.cmb_schema_op.currentText()
            p = DIR["schemas_ops"] / f"{name}.json"
            try:
                data = json.loads(self.ed_schema_op.toPlainText())
                safe_write_json(p, data)
                SCHEMAS[name] = data
                self.post_system(f"[Schema] Saved operator {name}.", COLOR_SYSTEM)
            except Exception as e:
                self.post_system(f"[Schema] Save error: {e}", COLOR_ERROR)

        btn_load.clicked.connect(load_bot)
        btn_save.clicked.connect(save_bot)
        btn_load2.clicked.connect(load_op)
        btn_save2.clicked.connect(save_op)

        dock.setWidget(w)
        dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        return dock

    def make_console_dock(self):
        dock = QDockWidget("System Console", self); dock.setObjectName("dock_console")
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        self.console_edit = QTextEdit(); self.console_edit.setReadOnly(True); self.console_edit.setFont(MONO_FONT)
        v.addWidget(self.console_edit, 1)
        hl = QHBoxLayout()
        btn_copy = QPushButton("Copy All"); btn_copy.setStyleSheet(SMALL_BTN)
        btn_copy.clicked.connect(lambda: pyperclip.copy(self.console_edit.toPlainText()))
        hl.addWidget(btn_copy)
        btn_clear = QPushButton("Clear View"); btn_clear.setStyleSheet(SMALL_BTN)
        btn_clear.clicked.connect(lambda: self.console_edit.clear())
        hl.addWidget(btn_clear); hl.addStretch(1)
        v.addLayout(hl)
        dock.setWidget(w); dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        return dock
    def make_browser_dock(self):
        dock = QDockWidget("Conversations Browser", self); dock.setObjectName("dock_browser")
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        self.list_active = QListWidget(); v.addWidget(QLabel("Active")); v.addWidget(self.list_active)
        self.list_potential = QListWidget(); v.addWidget(QLabel("Potential")); v.addWidget(self.list_potential)
        self.list_deleted = QListWidget(); v.addWidget(QLabel("Deleted")); v.addWidget(self.list_deleted)
        btn_refresh = QPushButton("Refresh"); btn_refresh.setStyleSheet(PILL_BTN); btn_refresh.clicked.connect(self.refresh_lists); v.addWidget(btn_refresh)
        self.list_active.itemClicked.connect(lambda item: self._activate_from_list(item, "active"))
        self.list_potential.itemClicked.connect(lambda item: self._activate_from_list(item, "potential"))
        self.list_deleted.itemClicked.connect(lambda item: self._activate_from_list(item, "deleted"))
        self.refresh_lists()
        dock.setWidget(w); dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        return dock
    def _activate_from_list(self, item, section: str):
        name = item.text()
        slug = name.split(".json")[0]
        if section == "active":
            set_active_conversation(slug)
            self.focus_or_add_tab(slug)
        else:
            set_active_conversation(slug)
        self.update_heartbeat()
    def focus_or_add_tab(self, slug: str):
        if slug not in self.conversations:
            p = DIR["conversations"] / f"{slug}.json"
            if not p.exists(): return
            conv = Conversation(slug, self)
            self.conversations[slug] = conv
        if slug not in self.pinned: self.add_to_view(self.conversations[slug])
        idx = self._tab_index_of(slug)
        if idx >= 0: self.tabs.setCurrentIndex(idx)
    # ----- helpers -----
    def post_system(self, text: str, color: str):
        conv = self.get_current_convo()
        if conv: conv.chat.add_message("System", text, color, entry_index=len(conv.entries))
    def inject_arbiter(self):
        msg = self.arb_in.text().strip(); self.arb_in.clear()
        if msg:
            conv = self.get_current_convo()
            if conv:
                conv.arbiter.set(msg)
                conv.chat.add_message("System", "[Arbiter] Injected for next turn.", COLOR_SYSTEM, entry_index=len(conv.entries))
    def play_current_tts(self):
        conv = self.get_current_convo()
        if conv and conv.entries:
            e = conv.entries[-1]
            voice = conv.zira.voice if e.get("role")=="Zira" else conv.david.voice
            enqueue_tts(e.get("content",""), voice=voice, conversation_id=conv.slug)
            set_active_conversation(conv.slug)
    def play_selected_clipboard(self):
        txt = pyperclip.paste().strip()
        conv = self.get_current_convo()
        if txt and conv:
            voice = conv.david.voice
            enqueue_tts(txt, voice=voice, conversation_id=conv.slug)
            set_active_conversation(conv.slug)
    def get_current_convo(self) -> Optional[Conversation]:
        if self.view_mode == "tabs":
            idx = self.tabs.currentIndex()
            if idx >= 0 and idx < len(self.pinned): slug = self.pinned[idx]; return self.conversations.get(slug)
        else:
            if self.pinned: return self.conversations.get(self.pinned[0])
        return None
    def new_convo(self, reason: str = "Autostart"):
        slug = f"{now_iso()}_New_Conversation"
        conv = Conversation(slug, self)
        self.conversations[slug] = conv
        self.add_to_view(conv)
        conv.running = True
        conv.parked = False
        conv.advance_turn()
        self.refresh_lists()
        SystemLogger.log(f"[New] Started {slug} ({reason})")
        return slug
    def _ensure_track_tile(self, conv: Conversation) -> QWidget:
        if conv.slug in self._slug_to_track_container: return self._slug_to_track_container[conv.slug]
        tile = QWidget(); tile.setObjectName("TrackTile")
        tile.setStyleSheet("QWidget#TrackTile{background:#ffffff; border:1px solid #ccc; border-radius:8px;}")
        v = QVBoxLayout(tile); v.setContentsMargins(6,6,6,6); v.setSpacing(4)
        hdr = QHBoxLayout(); hdr.setContentsMargins(0,0,0,0)
        lbl = QLabel(f"<b>{conv.slug}</b>"); hdr.addWidget(lbl); hdr.addStretch(1)
        v.addLayout(hdr)
        # Clicking the header sets active TTS
        def _click_hdr(): set_active_conversation(conv.slug); self.update_heartbeat()
        lbl.mousePressEvent = lambda ev: _click_hdr()
        w = self.track_tile_width
        conv.chat.setMinimumWidth(w)
        conv.chat.setMaximumWidth(w + 40)
        v.addWidget(conv.chat)
        idx_stretch = self.track_h.count()-1
        self.track_h.insertWidget(idx_stretch, tile)
        self._slug_to_track_container[conv.slug] = tile
        return tile
    def _unpin(self, slug: str):
        if slug in self.pinned: self.pinned = [s for s in self.pinned if s != slug]
        idx = self._tab_index_of(slug)
        if idx >= 0: self.tabs.removeTab(idx)
        tile = self._slug_to_track_container.pop(slug, None)
        if tile: tile.setParent(None); tile.deleteLater()
    def add_to_view(self, conv: Conversation):
        if len(self.pinned) >= self.max_pinned:
            QMessageBox.information(self, "Limit", "Max pinned reached.")
            return
        self.pinned.append(conv.slug)
        if self.view_mode == "tabs":
            self.tabs.addTab(conv.chat, conv.slug)
            self.tabs.setCurrentWidget(conv.chat)
        else:
            self._ensure_track_tile(conv)
    def change_view_mode(self, mode: str):
        self.view_mode = mode
        CONFIG.set(mode, "ui", "view_mode")
        if mode == "tabs":
            self.dock_track.setFloating(False)
            self.dock_track.hide()
            self.dock_track.setAllowedAreas(Qt.AllDockWidgetAreas)
            for slug in list(self.pinned):
                conv = self.conversations.get(slug)
                if not conv: continue
                if self._tab_index_of(slug) < 0: self.tabs.addTab(conv.chat, slug)
                tile = self._slug_to_track_container.pop(slug, None)
                if tile: tile.setParent(None); tile.deleteLater()
        else:
            self.dock_track.setAllowedAreas(Qt.NoDockWidgetArea)
            self.dock_track.setFloating(True)
            self.dock_track.show()
            for slug in list(self.pinned):
                idx = self._tab_index_of(slug)
                if idx >= 0: self.tabs.removeTab(idx)
                conv = self.conversations.get(slug)
                if conv: self._ensure_track_tile(conv)
    def set_max_pinned(self, val: int):
        self.max_pinned = val
        CONFIG.set(val, "conversation", "max_pinned")
    def refresh_lists(self):
        self.list_active.clear()
        for p in sorted(DIR["conversations"].glob("*.json")): self.list_active.addItem(p.name)
        self.list_potential.clear()
        for p in sorted(DIR["conversations_potential"].glob("*.json")): self.list_potential.addItem(p.name)
        self.list_deleted.clear()
        for p in sorted(DIR["conversations_deleted"].glob("*.json")): self.list_deleted.addItem(p.name)
    # ----- tab/selection -----
    def _on_tab_changed(self, _index: int):
        conv = self.get_current_convo()
        if conv: self.on_tab_selected(conv.slug)
    def on_tab_selected(self, slug: str):
        set_active_conversation(slug)
        CONFIG.set(slug, "tts", "active_conversation")
        # subtle tint
        idx = self._tab_index_of(slug)
        if idx >= 0: self.tabs.tabBar().setTabTextColor(idx, QColor("#2e7d32"))
    # ----- autonomy toggles -----
    def _toggle_auto(self, state: int):
        on = bool(self.chk_auto.isChecked())
        CONFIG.set(on, "autonomous_mode")
        SystemLogger.log(f"[Auto] Autonomous Mode set to {on}")
        if on and not self.pinned and not list(DIR["conversations"].glob("*.json")): self.new_convo("Autostart")
    # ----- runtime state -----
    def save_runtime_state(self):
        state = {
            "pinned": list(self.pinned),
            "view_mode": self.view_mode,
            "autonomous_mode": bool(CONFIG.get("autonomous_mode", default=True)),
            "tts_active": CONFIG.get("tts","active_conversation", default=""),
            "timestamp": now_iso(),
        }
        safe_write_json(RUNTIME_STATE_FILE, state)
        SystemLogger.log(f"[State] runtime saved to {RUNTIME_STATE_FILE}")
    def load_runtime_state(self):
        try:
            if not RUNTIME_STATE_FILE.exists(): return
            state = json.loads(RUNTIME_STATE_FILE.read_text(encoding="utf-8"))
            vm = state.get("view_mode", self.view_mode)
            if vm != self.view_mode: self.change_view_mode(vm)
            restored = 0
            for slug in state.get("pinned", []):
                if slug in self.conversations and slug not in self.pinned:
                    self.add_to_view(self.conversations[slug]); restored += 1
            act = state.get("tts_active","")
            if act: set_active_conversation(act)
            SystemLogger.log(f"[State] runtime restored ({restored} pinned)")
        except Exception as e: log_error("load_runtime_state", e)
    # ----- graceful quit -----
    def request_quit(self):
        try:
            m = QMessageBox(self)
            m.setIcon(QMessageBox.Question)
            m.setWindowTitle("Confirm Quit")
            m.setText("Pause autonomy, finish current rotations, save state, and quit?")
            m.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            if m.exec_() != QMessageBox.Yes: return
            self.begin_shutdown()
        except Exception as e:
            log_error("request_quit", e)
            QApplication.quit()
    def begin_shutdown(self):
        self._shutting_down = True
        self.heartbeat.setStyleSheet(f"QLabel{{background:{COLOR_HEARTBEAT_BG}; color:{COLOR_HEARTBEAT_BAD}; padding:2px 6px; font: 10pt 'Consolas';}}")
        self.heartbeat.setText("Shutting down… pausing autonomy & finishing rotations")
        if hasattr(self, "scheduler_timer"): self.scheduler_timer.stop()
        if hasattr(self, "maintenance_timer"): self.maintenance_timer.stop()
        if hasattr(self, "auto_timer"): self.auto_timer.stop()
        if hasattr(self, "theater_timer"): self.theater_timer.stop()
        self.chk_auto.setChecked(False)
        for conv in self.conversations.values(): conv.running = False # prevent new turns
        stop_service()
        def _check_idle():
            all_idle = True
            for conv in self.conversations.values():
                in_flight = (conv.q is not None) or (conv.timer and conv.timer.isActive())
                if in_flight: all_idle = False; break
            if all_idle:
                try: self.save_runtime_state()
                except Exception as e: log_error("save_runtime_state_at_shutdown", e)
                QTimer.singleShot(2000, QApplication.quit)
            else: QTimer.singleShot(150, _check_idle)
        _check_idle()
# =========================================================
# Entry
# =========================================================
def main():
    app = QApplication([])
    win = MorphWindow()
    win.show()
    app.exec_()
    try: SystemLogger.unsubscribe(win)
    except Exception: pass
if __name__ == "__main__": main()
```

morph.py — Dual-bot studio with dockable PyQt5 UI, schemas, datasets, robust TTS via SQL queue, and model providers (Ollama local + OpenAI). Supports Tabs, tear-off tabs, and a pop-out Track Mode.
HIGHLIGHTS (performance-safe, non-blocking)
-------------------------------------------
• TTS is fully decoupled: a dedicated background thread reads a SQLite 'tts_queue' table. Only the currently selected conversation is spoken. Click the 🔊 icon next to any message to play from that point forward. Skip the current utterance with Ctrl+K.
• Heartbeat bar (slim, black) displays real-time status (autonomy, CPU/mem/net if available), queue depth, and in-flight ops. Colors: green (healthy), yellow (busy/paused), red (shutdown/error).
• Autonomous Mode (default ON) resumes work at launch, auto-starts if nothing is active, and drives round-robin scheduling. Graceful Quit pauses autonomy, lets rotations complete, persists runtime state, then exits cleanly. Startup clears system log and reloads state.
• Active Conversation Logic hardening: semantic drift threshold is enforced; new “Potential” conversations are generated and parked robustly. Automatic background maintenance promotes potentials, parks long-running actives, and scrubs deleted items—no manual clicks.
• UI simplification: The Conversations Browser dock removes unused controls; a single “Refresh” button remains. All other lifecycle actions run autonomously and are surfaced in the heartbeat and the System Console dock (real log, copyable, reset each launch).
REQUIREMENTS
------------
pip install pyqt5 requests pyttsx3 pyperclip numpy
# Optional (enables richer heartbeat metrics): pip install psutil
RUN
---
ollama serve
python morph.py
NOTES
-----
• Airplane Mode constrains Ollama calls to localhost (OpenAI unaffected).
• OpenAI API key file: C:\Users\Art PC\Desktop\Morph\api\api_key.txt
• Code rendering shows fenced blocks with syntax-highlighted Python.
**Classes:** SystemLogger, ConfigManager, TurnState, PythonHighlighter, CodeBlockWidget, ChatPanel, ArbiterInjector, Bot, Conversation, WorkItem, SessionPlan, TaskRouter, _BoxOperator, Astra, Nova, Stella, ShiftWheelToHorizontalFilter, DetachableTabBar, DetachableTabWidget, FloatingTabWindow, BatchItem, Batch, SnippetForge, Verifier, EditorCore, QueueManager, MorphWindow
**Functions:** init_tts_engine(voice_name), tts_worker(), enqueue_tts(text, voice, conversation_id), set_active_conversation(cid), clear_queue(cid), pause_tts(), resume_tts(), skip_current(), stop_service(), get_queue_depth(cid), now_iso(), sha1(s), safe_write_json(path, data), _ensure_file_reset(path), log_error(where, err), slugify(text, maxw), sync_models_json(), persist_schemas_to_disk(), list_ollama_models(), is_embed_model(name), is_chat_model(name), _default_chat_ollama(), _default_embed_ollama(), list_convo_files(), rag_full_context(), scan_for_directives(content), remove_directives(content), self_doc(), _enforce_localhost(url), _openai_api_key(), _openai_headers(), _chat_provider(), _embed_provider(), _base_options(), ollama_chat_stream(model, messages, q, options), ollama_generate(model, prompt, options), ollama_embed_call(model, text_list), _openai_guard(), openai_chat_stream(model, messages, q, options), openai_generate_once(model, prompt, options), openai_embed_call(model, text_list), provider_chat_stream(model, messages, q, options), provider_generate(model, prompt, options), provider_embed_call(model, text_list), run_operator(op_name, input_text, model), _looks_like_json(s), _heuristic_code_score(s), is_code_like(lang, body), _token_set(s), text_similarity(a, b), create_potential(directive, from_slug, last_entries), forward_to(target_slug, content, reason, from_slug, window), main()


## Module `tts_service.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import time
import queue
import threading
import logging
import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import ttk

import pyttsx3

# =============================================================================
# Persistent defaults (self-edited by the GUI)
# =============================================================================
RATE = 220                 # pyttsx3 "rate" (words per minute-ish)
DEFAULT_VOICE = "Zira"     # default voice name substring (e.g., "Zira" or "David")

# =============================================================================
# Logging
# =============================================================================
logging.basicConfig(
    filename="tts_service.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =============================================================================
# Morph integration (discover Morph base, DB and config)
# =============================================================================
def find_morph_base() -> Path:
    """
    Attempts to locate the Morph directory as used by morph.py.
    Strategy:
      1) MORPH_BASE env var
      2) ./Morph relative to cwd
      3) Search parents for a 'Morph' folder (up to 5 levels)
    """
    env = os.environ.get("MORPH_BASE", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p
    # ./Morph under cwd
    here_morph = (Path.cwd() / "Morph").resolve()
    if here_morph.exists():
        return here_morph
    # parents
    cur = Path.cwd().resolve()
    for _ in range(5):
        candidate = (cur / "Morph").resolve()
        if candidate.exists():
            return candidate
        cur = cur.parent
    # fallback: create ./Morph if not found
    fallback = (Path.cwd() / "Morph").resolve()
    (fallback).mkdir(parents=True, exist_ok=True)
    return fallback

MORPH_BASE = find_morph_base()
MORPH_CONFIG = MORPH_BASE / "config" / "user_config.json"
MORPH_TTS_DB = MORPH_BASE / "temp" / "tts_db" / "tts_queue.sqlite3"

# Ensure folders exist
(MORPH_BASE / "temp" / "tts_db").mkdir(parents=True, exist_ok=True)
(MORPH_BASE / "config").mkdir(parents=True, exist_ok=True)

# =============================================================================
# Global state
# =============================================================================
tts_queue_local = queue.Queue()
stop_flag = threading.Event()
engine_lock = threading.Lock()

active_voice = DEFAULT_VOICE   # currently selected voice label (string)
current_rate = RATE

# Morph config cache (read periodically)
config_cache = {
    "enabled": True,             # tts.enabled
    "active_conversation": "",   # tts.active_conversation
    "skip_once": False           # tts.skip_once (one-shot)
}

# =============================================================================
# Self-persistence (edit this file)
# =============================================================================
THIS_FILE = Path(__file__).resolve()

def _save_field_in_source(field: str, value: str):
    try:
        code = THIS_FILE.read_text(encoding="utf-8")
        if field == "RATE":
            new_code = re.sub(r'^RATE\s*=\s*\d+\s*$', f'RATE = {int(value)}', code, flags=re.M)
        elif field == "DEFAULT_VOICE":
            # Quote the value safely
            q = value.replace('"', '\\"')
            new_code = re.sub(r'^DEFAULT_VOICE\s*=\s*".*?"\s*$', f'DEFAULT_VOICE = "{q}"', code, flags=re.M)
        else:
            return
        if new_code != code:
            THIS_FILE.write_text(new_code, encoding="utf-8")
            logging.info(f"Persisted {field}={value} into source.")
    except Exception as e:
        logging.error(f"Failed to persist {field}: {e}")

# =============================================================================
# pyttsx3 helpers
# =============================================================================
def _select_voice_id(engine: pyttsx3.Engine, name_like: str) -> str | None:
    name_like_l = (name_like or "").lower()
    try:
        for v in engine.getProperty("voices"):
            if name_like_l in (v.name or "").lower():
                return v.id
        # fallback: any English voice if name not found
        for v in engine.getProperty("voices"):
            if "en" in (v.languages[0].decode() if getattr(v, "languages", None) else "").lower() or "english" in (v.name or "").lower():
                return v.id
    except Exception:
        pass
    return None

def _new_engine(voice_name_like: str, rate_val: int) -> pyttsx3.Engine:
    e = pyttsx3.init()
    vid = _select_voice_id(e, voice_name_like)
    if vid:
        e.setProperty("voice", vid)
    e.setProperty("rate", int(rate_val))
    e.setProperty("volume", 1.0)
    return e

# engine instance (created in worker thread)
engine = None  # type: ignore

def set_engine_params(voice_name_like: str | None = None, rate_val: int | None = None):
    """
    Safely update engine voice/rate live.
    """
    global engine, active_voice, current_rate
    with engine_lock:
        if engine is None:
            engine = _new_engine(voice_name_like or active_voice, rate_val if rate_val is not None else current_rate)
            return
        if voice_name_like is not None:
            vid = _select_voice_id(engine, voice_name_like)
            if vid:
                engine.setProperty("voice", vid)
                active_voice = voice_name_like
        if rate_val is not None:
            engine.setProperty("rate", int(rate_val))
            current_rate = int(rate_val)

# =============================================================================
# Morph config + DB access
# =============================================================================
def read_morph_config():
    """
    Reads Morph's user_config.json and updates config_cache.
    Keys of interest:
      tts.enabled (bool)
      tts.active_conversation (slug)
      tts.skip_once (bool)  # one-shot
    """
    try:
        if MORPH_CONFIG.exists():
            raw = json.loads(MORPH_CONFIG.read_text(encoding="utf-8") or "{}")
            tts = raw.get("tts", {})
            config_cache["enabled"] = bool(tts.get("enabled", True))
            config_cache["active_conversation"] = str(tts.get("active_conversation", "") or "")
            config_cache["skip_once"] = bool(tts.get("skip_once", False))
        else:
            # default enabled true
            config_cache["enabled"] = True
            config_cache["active_conversation"] = ""
            config_cache["skip_once"] = False
    except Exception as e:
        logging.error(f"Failed reading Morph config: {e}")

def write_morph_skip_clear():
    """
    Clears tts.skip_once after honoring it.
    """
    try:
        if not MORPH_CONFIG.exists():
            return
        raw = json.loads(MORPH_CONFIG.read_text(encoding="utf-8") or "{}")
        tts = raw.get("tts", {})
        if tts.get("skip_once"):
            tts["skip_once"] = False
            raw["tts"] = tts
            tmp = MORPH_CONFIG.with_suffix(".tmp")
            tmp.write_text(json.dumps(raw, indent=2), encoding="utf-8")
            tmp.replace(MORPH_CONFIG)
    except Exception as e:
        logging.error(f"Failed clearing skip_once: {e}")

def db_connect():
    # sqlite3 is threadsafe with check_same_thread=False if we share a handle,
    # but we’ll open short-lived connections for simplicity + durability.
    return sqlite3.connect(str(MORPH_TTS_DB))

def fetch_next_row_for_active(slug: str):
    """
    Returns dict: {id, role, voice, content} or None
    """
    if not slug:
        return None
    try:
        with db_connect() as c:
            row = c.execute(
                "SELECT id, role, voice, content FROM tts_queue WHERE conversation_slug=? AND spoken=0 ORDER BY id ASC LIMIT 1",
                (slug,)
            ).fetchone()
            if row:
                return {"id": int(row[0]), "role": row[1], "voice": row[2], "content": row[3]}
    except Exception as e:
        logging.error(f"DB fetch error: {e}")
    return None

def mark_row_spoken(row_id: int):
    try:
        with db_connect() as c:
            c.execute("UPDATE tts_queue SET spoken=1 WHERE id=?", (row_id,))
    except Exception as e:
        logging.error(f"DB mark spoken error: {e}")

# =============================================================================
# Worker: poll Morph queue + speak
# =============================================================================
def tts_worker():
    global engine
    set_engine_params(active_voice, current_rate)  # creates engine

    idle_backoff = 0.10  # seconds (will grow to 1.5s)
    while not stop_flag.is_set():
        try:
            read_morph_config()

            if not config_cache["enabled"]:
                # paused: slow poll
                time.sleep(0.5)
                continue

            slug = config_cache["active_conversation"] or ""
            row = fetch_next_row_for_active(slug)

            if config_cache["skip_once"]:
                # honor skip: clear flag and skip current cycle
                write_morph_skip_clear()
                time.sleep(0.05)
                continue

            if row is None:
                # no work; gentle backoff
                idle_backoff = min(1.5, idle_backoff * 1.35)
                time.sleep(idle_backoff)
                continue

            # work found, reset backoff
            idle_backoff = 0.10

            text = (row.get("content") or "").strip()
            v_hint = (row.get("voice") or "").strip()  # "Zira", "David", etc.

            if text:
                # Switch voice if row specifies a different one
                want_voice = v_hint or active_voice or DEFAULT_VOICE
                set_engine_params(voice_name_like=want_voice, rate_val=current_rate)

                logging.info(f"TTS START | Voice={want_voice} | Len={len(text)} | RowID={row['id']}")
                with engine_lock:
                    engine.say(text)
                    engine.runAndWait()
                logging.info("TTS END")

            mark_row_spoken(int(row["id"]))

        except Exception as e:
            logging.error(f"TTS worker error: {e}")
            # Try to rebuild engine on error
            with engine_lock:
                engine = _new_engine(active_voice, current_rate)
            time.sleep(0.2)

    logging.info("TTS worker exiting gracefully")

# =============================================================================
# Minimal public API for direct enqueue (optional)
# =============================================================================
def enqueue_tts_direct(text: str, voice: str | None = None):
    """
    Optional: allows piping text directly into the local in-memory queue (not Morph).
    We keep it for compatibility if you run with --cli and want immediate speech.
    """
    tts_queue_local.put((text, voice or active_voice))

def local_queue_worker():
    """
    If you use --cli to type lines, this worker reads the local queue and speaks.
    This is separate from Morph’s DB queue.
    """
    while not stop_flag.is_set():
        try:
            text, v = tts_queue_local.get(timeout=0.1)
        except queue.Empty:
            continue
        try:
            set_engine_params(voice_name_like=v, rate_val=current_rate)
            with engine_lock:
                engine.say(text)
                engine.runAndWait()
        except Exception as e:
            logging.error(f"local speak error: {e}")

# =============================================================================
# GUI
# =============================================================================
def launch_gui(start_minimized: bool = False):
    global current_rate, active_voice

    root = tk.Tk()
    root.title("Morph TTS Service")

    if start_minimized:
        root.withdraw()

    frame = ttk.Frame(root, padding=12)
    frame.pack(fill="both", expand=True)

    # Rate
    rate_label = ttk.Label(frame, text=f"Rate: {current_rate}")
    rate_label.pack(anchor="w")

    rate_slider = ttk.Scale(frame, from_=80, to=450, orient="horizontal")
    rate_slider.set(current_rate)
    rate_slider.pack(fill="x", pady=6)

    def persist_rate(val):
        global current_rate
        current_rate = int(float(val))
        rate_label.config(text=f"Rate: {current_rate}")
        set_engine_params(rate_val=current_rate)
        _save_field_in_source("RATE", str(current_rate))

    rate_slider.bind("<ButtonRelease-1>", lambda e: persist_rate(rate_slider.get()))
    rate_slider.bind("<B1-Motion>", lambda e: rate_label.config(text=f"Rate: {int(rate_slider.get())}"))  # live display

    # Voice selector
    voice_row = ttk.Frame(frame); voice_row.pack(fill="x", pady=(10,6))
    ttk.Label(voice_row, text="Voice:").pack(side="left")
    voice_combo = ttk.Combobox(voice_row, state="readonly")
    # Populate voices (names)
    try:
        tmp_engine = pyttsx3.init()
        voice_names = []
        for v in tmp_engine.getProperty("voices"):
            nm = (v.name or "").strip()
            if nm and nm not in voice_names:
                voice_names.append(nm)
        # Prefer to put common ones first
        pref = [n for n in voice_names if "zira" in n.lower()] + [n for n in voice_names if "david" in n.lower()]
        others = [n for n in voice_names if n not in pref]
        voice_names = list(dict.fromkeys(pref + others))
    except Exception:
        voice_names = [DEFAULT_VOICE, "David"]

    # Choose initial display value
    initial = None
    for n in voice_names:
        if active_voice.lower() in n.lower():
            initial = n; break
    if initial is None:
        initial = voice_names[0]
    voice_combo["values"] = voice_names
    voice_combo.set(initial)
    voice_combo.pack(side="left", fill="x", expand=True, padx=(6,0))

    def on_voice_change(event=None):
        global active_voice
        chosen = voice_combo.get().strip()
        active_voice = chosen
        set_engine_params(voice_name_like=active_voice)
        # Persist only the *substring* we match against (so switching lists still works)
        key = "Zira" if "zira" in chosen.lower() else ("David" if "david" in chosen.lower() else chosen)
        _save_field_in_source("DEFAULT_VOICE", key)

    voice_combo.bind("<<ComboboxSelected>>", on_voice_change)

    # Buttons
    btn_row = ttk.Frame(frame); btn_row.pack(fill="x", pady=(12,0))

    def hide_gui():
        root.withdraw()
        logging.info("GUI hidden; service remains active in background.")

    ttk.Button(btn_row, text="Close GUI (Keep in Background)", command=hide_gui).pack(side="left")

    # Small heartbeat label (shows active convo + enabled flag)
    status_lbl = ttk.Label(frame, text="status: starting…")
    status_lbl.pack(anchor="w", pady=(8,0))

    def refresh_status():
        read_morph_config()
        status_lbl.config(
            text=f"status: enabled={config_cache['enabled']} | active_conversation='{config_cache['active_conversation'] or '(none)'}'"
        )
        root.after(700, refresh_status)

    refresh_status()
    root.mainloop()

# =============================================================================
# Entrypoint
# =============================================================================
def main():
    # threads: morph db worker + local CLI worker (optional)
    morph_thread = threading.Thread(target=tts_worker, daemon=True)
    morph_thread.start()

    # if --cli, start local queue worker and read stdin
    if "--cli" in sys.argv:
        local_thread = threading.Thread(target=local_queue_worker, daemon=True)
        local_thread.start()
        logging.info("CLI mode: type lines to speak; 'quit' to exit.")
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    time.sleep(0.05)
                    continue
                line = line.strip()
                if not line:
                    continue
                if line.lower() == "quit":
                    break
                enqueue_tts_direct(line, active_voice)
        except KeyboardInterrupt:
            pass
        finally:
            stop_flag.set()
            morph_thread.join()
            return

    # default: GUI mode (double-click)
    start_min = "--background" in sys.argv or "--minimized" in sys.argv
    try:
        launch_gui(start_minimized=start_min)
    finally:
        # When GUI closes (hidden or exit), keep worker if window was hidden;
        # If the process is actually exiting, stop_flag will be set by runtime shutdown.
        # We set it here to ensure a clean stop when the process exits.
        stop_flag.set()
        morph_thread.join()

if __name__ == "__main__":
    main()
```

**Functions:** find_morph_base(), _save_field_in_source(field, value), _select_voice_id(engine, name_like), _new_engine(voice_name_like, rate_val), set_engine_params(voice_name_like, rate_val), read_morph_config(), write_morph_skip_clear(), db_connect(), fetch_next_row_for_active(slug), mark_row_spoken(row_id), tts_worker(), enqueue_tts_direct(text, voice), local_queue_worker(), launch_gui(start_minimized), main()
