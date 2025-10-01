# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analyzing the project contents. Python modules are parsed for docstrings, classes, and functions. Image files are embedded as previews. Executable files (.exe) are listed by name; their contents are intentionally skipped.

## Python Modules

- `Advanced_Chatbot.py`
- `Analyze_folders.py`

## Other Files

- `Advanced_Chatbot.md`
- `analyze.txt`
- `api\api_key.txt`
- `api\other\api_key.txt`
- `config.json`
- `logs\ACA_Chatbot.log`
- `project_config.json`
- `projects\Global_Prompts\global_prompt_settings.json`
- `projects\Rant_PDD\Rant_PDD Workspace\threads\Rant_PDD Workspace Thread 1754798078.db`
- `projects\Rant_PDD\Rant_PDD Workspace\threads\Rant_PDD Workspace Thread 1754798078.txt`
- `projects\Rant_PDD\Rant_PDD Workspace\workspace\Rant_PDD Workspace.db`
- `projects\Rant_PDD\Rant_PDD Workspace\workspace\Rant_PDD Workspace.txt`


## Detailed Module Analyses


## Module `Advanced_Chatbot.py`

```python
#!/usr/bin/env python3
"""
Advanced_Chatbot.py – Advanced Chatbot Application

This script implements an integrated chatbot that supports:
 • A unified Project, Workspace, and Thread management system (with right‐click actions for rename, fork, clone, and delete)
 • Conversation history with active prompts and token‐based truncation
 • Two LLM providers – OpenAI and Ollama – with dynamic model fetching;
   the default is OpenAI using model gpt-4o-mini (providers are mutually exclusive)
 • Speech-to-text (STT) using SpeechRecognition and text-to-speech (TTS) using pyttsx3
 • Syntax highlighting for Python code blocks in chat responses
 • Comprehensive logging (console widget and log file)

All configuration (including API keys and conversation logs) is stored in shared folders under a central BASE_DIR.
"""

import sys, os, json, time, re, subprocess, traceback, shutil, requests
import openai, tiktoken, pyperclip, pyttsx3, speech_recognition as sr
import sqlite3
import threading
import pathlib

from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPlainTextEdit,
    QLabel, QPushButton, QFrame, QComboBox, QInputDialog, QMessageBox, QSizePolicy,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QDialog, QListWidget, QListWidgetItem,
    QMenu, QCheckBox, QSlider, QDoubleSpinBox, QDialogButtonBox, QHeaderView
)
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# -------------------- ENUM ALIASES (Qt Compatibility) --------------------
# Define PyQt6-safe enum shortcuts for checkbox state compatibility
try:
    UNCHECKED = Qt.CheckState.Unchecked
    CHECKED = Qt.CheckState.Checked
except AttributeError:
    UNCHECKED = Qt.Unchecked
    CHECKED = Qt.Checked

# -------------------- GLOBAL PATHS & CONFIGURATION --------------------
BASE_DIR = r"C:\Users\Art PC\Desktop\Advanced ChatBot"
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "ACA_Chatbot.log")
# Clear log file on startup
with open(LOG_FILE_PATH, "w", encoding="utf-8") as log_file:
    log_file.write("")

API_KEY_PATH = os.path.join(BASE_DIR, "api", "api_key.txt")
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
PROJECT_CONFIG_FILE = os.path.join(BASE_DIR, "project_config.json")
CONV_ROOT = os.path.join(BASE_DIR, "conversation")
SIMPLE_CHAT_DIR = os.path.join(CONV_ROOT, "simple_chat")
PROMPT_CONTROL_DIR = os.path.join(SIMPLE_CHAT_DIR, "Prompt_Control")
for d in (SIMPLE_CHAT_DIR, PROMPT_CONTROL_DIR):
    os.makedirs(d, exist_ok=True)
METADATA_DIR = os.path.join(BASE_DIR, "metadata")
os.makedirs(METADATA_DIR, exist_ok=True)
TTS_CONFIG_FILE = os.path.join(METADATA_DIR, "tts_settings.json")
DEFAULT_TTS_SETTINGS = {
    "voice": "Zira",       # Default voice
    "speed": 1.2,          # Default speed multiplier for TTS
    "chat_files": []       # List of chat files for TTS integration
}

# Define a global conversation file for fallback usage
CONVO_FILE = os.path.join(SIMPLE_CHAT_DIR, "conversation.txt")

# Subscribers for log events.  Functions appended to this list will
# receive each log line as it is written.  See log_message() for
# broadcasting behavior.  Registered callbacks should accept two
# parameters: the log line (string) and the severity level (string).
LOG_SUBSCRIBERS: list = []

# -------------------- GLOBAL PROMPTS --------------------
GLOBAL_PROMPTS_DIR = os.path.join(PROJECTS_DIR, "Global_Prompts")
os.makedirs(GLOBAL_PROMPTS_DIR, exist_ok=True)
GLOBAL_PROMPTS_CONFIG_FILE = os.path.join(GLOBAL_PROMPTS_DIR, "global_prompt_settings.json")

import subprocess

def discover_ollama_models() -> list[str]:
    """Returns a list of locally available Ollama model names by querying `ollama list`."""
    models = []
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, timeout=4)
        for line in out.splitlines()[1:]:  # Skip the header row
            parts = line.split()
            if parts:
                models.append(parts[0])  # model name is always the first column
    except Exception as e:
        log_message(f"Failed to list Ollama models: {e}", level="ERROR")
    return models


def load_global_prompts_config():
    if os.path.exists(GLOBAL_PROMPTS_CONFIG_FILE):
        try:
            with open(GLOBAL_PROMPTS_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_global_prompts_config(cfg):
    with open(GLOBAL_PROMPTS_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

def sanitize_filename(name):
    return re.sub(r'[^\w\s-]', '_', name).strip().replace(" ", "_")

def get_global_prompts():
    prompts = []
    config = load_global_prompts_config()
    for filename in os.listdir(GLOBAL_PROMPTS_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(GLOBAL_PROMPTS_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    prompt_text = f.read().strip()
                    if prompt_text:
                        enabled = config.get(filename, True)
                        prompts.append({"text": prompt_text, "enabled": enabled, "filename": filename})
            except Exception as e:
                log_message(f"Error reading global prompt file {filename}: {e}", level="error")
    return prompts

# -------------------- STABILITY: TTS STARTUP --------------------
def is_tts_running():
    try:
        output = subprocess.check_output(["tasklist"], universal_newlines=True)
        return "tts.py" in output
    except Exception as e:
        log_message(f"Error checking tts.py process: {e}", level="error")
        return False

def ensure_tts_running():
    if not is_tts_running():
        tts_script = os.path.join(BASE_DIR, "scripts", "tts.py")
        if os.path.exists(tts_script):
            try:
                subprocess.Popen(["python", tts_script])
                log_message("tts.py launched on startup.")
            except Exception as e:
                log_message(f"Failed to launch tts.py: {e}", level="error")
        else:
            log_message("tts.py not found, skipping launch.", level="warning")

# -------------------- LOGGING FUNCTION --------------------
def log_message(message: str, level: str = "info") -> None:
    """
    Write a log message to the persistent log file and notify any
    registered subscribers.  A timestamp is prepended and the level
    is uppercased.  If the message is an error or critical level,
    also print it to stdout.  Subscribers in LOG_SUBSCRIBERS will
    receive the raw log line and the level for real‐time UI updates.

    Parameters
    ----------
    message : str
        The human readable log message.
    level : str
        Severity level: one of "info", "warning", "error", "critical".
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {level.upper()}: {message}\n"
    # Write to file
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(log_line)
    except Exception:
        # Fail silently on file I/O errors
        pass
    # Broadcast to subscribers for live updates (e.g., log window)
    for callback in list(LOG_SUBSCRIBERS):
        try:
            callback(log_line, level)
        except Exception:
            # Remove callbacks that raise exceptions
            try:
                LOG_SUBSCRIBERS.remove(callback)
            except ValueError:
                pass
    # Echo to console for high severity
    if level.lower() in ("error", "critical"):
        print(log_line.strip())

# -------------------- CONFIGURATION FUNCTIONS --------------------
def load_api_key():
    try:
        with open(API_KEY_PATH, "r") as f:
            return f.read().strip()
    except Exception as e:
        log_message(f"Error loading API key: {e}", level="error")
        return None

def save_global_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

def load_global_config():
    if not os.path.exists(CONFIG_FILE):
        cfg = {"provider": "OpenAI", "default_model": "gpt-4o-mini", "mic_device": None, "last_project": "", "last_workspace": ""}
        save_global_config(cfg)
        return cfg
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_project_config():
    if os.path.exists(PROJECT_CONFIG_FILE):
        with open(PROJECT_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_project_config(cfg):
    with open(PROJECT_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

GLOBAL_CONFIG = load_global_config()
GLOBAL_CONFIG["provider"] = "OpenAI"
GLOBAL_CONFIG["default_model"] = "gpt-4o-mini"
save_global_config(GLOBAL_CONFIG)
PROJECT_CONFIG = load_project_config()

# -------------------- CONVERSATION PARSING --------------------
def parse_conversation_file(file_path):
    # UPDATED: Now returns a list of 4‐tuple entries: (user_text, gpt_text, provider, model)
    pairs = []
    user_text = ""
    gpt_text = ""
    provider = None
    model = None
    current_role = None
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        log_message(f"parse_conversation_file: File {file_path} not found or is a directory.", level="error")
        return pairs
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("User:"):
                if user_text or gpt_text:
                    pairs.append((user_text.strip(), gpt_text.strip(), provider, model))
                user_text = line[len("User:"):].strip()
                gpt_text = ""
                provider = None
                model = None
                current_role = "user"
            elif line.startswith("OpenAI (") or line.startswith("Ollama ("):
                idx = line.find("):")
                if idx != -1:
                    # UPDATED: extract provider and model:
                    provider = line.split(" (")[0]
                    model = line[len(provider + " ("):idx]
                    gpt_text = line[idx+2:].strip()
                current_role = "gpt"
            elif line.startswith("GPT"):
                if line.startswith("GPT ("):
                    idx = line.find("):")
                    if idx != -1:
                        model = line[len("GPT ("):idx]
                        gpt_text = line[idx+2:].strip()
                    else:
                        gpt_text = line[len("GPT:"):].strip()
                elif line.startswith("GPT:"):
                    gpt_text = line[len("GPT:"):].strip()
                current_role = "gpt"
            elif line.startswith("-" * 40):
                pairs.append((user_text.strip(), gpt_text.strip(), provider, model))
                user_text, gpt_text, provider, model = "", "", None, None
                current_role = None
            else:
                if current_role == "user":
                    user_text += "\n" + line
                elif current_role == "gpt":
                    gpt_text += "\n" + line
    if user_text or gpt_text:
        pairs.append((user_text.strip(), gpt_text.strip(), provider, model))
    return pairs

# -------------------- DATASET (SQLite) FUNCTIONS --------------------

# Helper: derive a canonical dataset path from a conversation file path.
# A conversation file is always a plain text transcript located under a
# `workspace` or `threads` folder.  The dataset lives alongside the
# conversation file and shares its basename, but uses the `.db` extension.
def dataset_path_for(conv_path: str) -> str:
    """
    Returns the canonical dataset path for a given conversation file.

    Examples
    --------
    >>> dataset_path_for("/foo/bar/workspace/My Workspace.txt")
    '/foo/bar/workspace/My Workspace.db'
    >>> dataset_path_for("/foo/bar/threads/My Thread.txt")
    '/foo/bar/threads/My Thread.db'

    Parameters
    ----------
    conv_path : str
        Full path to the conversation text file.

    Returns
    -------
    str
        Full path to the corresponding dataset file (same folder, `.db` extension).
    """
    base, _ = os.path.splitext(conv_path)
    return base + ".db"

def ensure_dataset_db(db_file: str) -> None:
    """
    Ensure that a SQLite database exists at the given path and contains
    the required table structure.  The table `entries` stores each
    message pair along with metadata for semantic retrieval.  If the
    database or table does not exist, it is created.

    Parameters
    ----------
    db_file : str
        Path to the SQLite database file.  Directories are created
        automatically if needed.
    """
    try:
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                assistant TEXT,
                full_prompt TEXT,
                provider TEXT,
                model TEXT,
                timestamp REAL,
                embedding TEXT,
                token_count INTEGER,
                weight REAL
            )
            """
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log_message(f"Error ensuring dataset DB {db_file}: {e}", level="error")


def compute_embedding(text: str) -> str:
    """
    Compute a simple embedding for the given text.  This function
    tokenizes the text into alphanumeric words, converts them to
    lowercase, removes duplicates, and sorts them.  The resulting
    string of space‐separated tokens serves as a lightweight
    representation for semantic similarity comparisons.  In a
    production system this would be replaced with a proper vector
    embedding.

    Parameters
    ----------
    text : str
        The text to embed.

    Returns
    -------
    str
        A space‐separated string of sorted unique tokens.
    """
    tokens = re.findall(r"\w+", text.lower())
    unique_tokens = sorted(set(tokens))
    return " ".join(unique_tokens)


def add_to_dataset(db_file: str, user_text: str, assistant_text: str, full_prompt: str,
                   provider: str, model: str) -> None:
    """
    Insert a new message pair into the SQLite dataset.  Each entry
    includes both the user and assistant messages, the full prompt
    that generated the response, provider/model metadata, a timestamp,
    a simple embedding for semantic search, and token/weight metadata.

    Parameters
    ----------
    db_file : str
        Path to the dataset database file.
    user_text : str
        The user's input.
    assistant_text : str
        The assistant's reply.
    full_prompt : str
        The full prompt sent to the LLM (for context and future
        reference).  This is used for embedding.
    provider : str
        Which provider generated the response (e.g., "OpenAI", "Ollama").
    model : str
        Which model generated the response.
    """
    ensure_dataset_db(db_file)
    try:
        emb = compute_embedding(full_prompt)
        token_count = len(full_prompt.split())
        timestamp = time.time()
        weight = 1.0
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO entries (user, assistant, full_prompt, provider, model,
                                 timestamp, embedding, token_count, weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_text, assistant_text, full_prompt, provider, model,
             timestamp, emb, token_count, weight)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log_message(f"Error adding to dataset {db_file}: {e}", level="error")


def text_similarity_tokens(emb1: str, emb2: str) -> float:
    """
    Compute a Jaccard similarity between two embedding strings.  Both
    embeddings are expected to be space‐separated tokens.  The
    similarity is the ratio of the intersection size to the union
    size.  A zero union yields a similarity of zero.

    Parameters
    ----------
    emb1 : str
        First embedding (space‐separated tokens).
    emb2 : str
        Second embedding (space‐separated tokens).

    Returns
    -------
    float
        A value between 0 and 1 indicating similarity.
    """
    set1 = set(emb1.split())
    set2 = set(emb2.split())
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union else 0.0


def _query_dataset_for_similarity(db_file: str, query_emb: str, limit: int = 3) -> list:
    """
    Query a single dataset for entries most similar to the provided
    embedding.  Only the top `limit` entries are returned, sorted by
    descending similarity.  Each result is a tuple of (score, entry
    dict) where the entry includes the user and assistant messages.

    Parameters
    ----------
    db_file : str
        Path to the dataset database.
    query_emb : str
        The computed embedding for the query.
    limit : int
        Maximum number of results to return from this dataset.

    Returns
    -------
    list
        A list of (score, entry) tuples for the best matches.
    """
    ensure_dataset_db(db_file)
    results = []
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        for row in c.execute("SELECT user, assistant, embedding FROM entries"):
            u, a, emb = row
            sim = text_similarity_tokens(query_emb, emb or "")
            if sim > 0:
                results.append((sim, {"user": u, "assistant": a}))
        conn.close()
    except Exception as e:
        log_message(f"Error querying dataset {db_file}: {e}", level="error")
        return []
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:limit]


def query_semantic_context(query_text: str, current_dataset_file: str,
                           current_project_name: str = "", current_workspace_name: str = "",
                           current_thread_name: str = "", limit: int = 3) -> list:
    """
    Retrieve semantically relevant context from across available datasets.
    The current dataset is always included in the search.  Additional
    datasets from other projects are included only if their project is
    marked as semantic aware and the respective workspace or thread is
    not isolated.  Within the current project, isolated workspaces or
    threads are still searchable if they are the current scope.

    Parameters
    ----------
    query_text : str
        The user's new message to embed for searching.
    current_dataset_file : str
        The dataset file of the current conversation scope.
    current_project_name : str
        Name of the current project.
    current_workspace_name : str
        Name of the current workspace.
    current_thread_name : str
        Name of the current thread (empty if at workspace level).
    limit : int
        Maximum number of context entries to return overall.

    Returns
    -------
    list[dict]
        A list of dictionaries with keys "user" and "assistant"
        representing the most similar historical messages.
    """
    query_emb = compute_embedding(query_text)
    all_candidates: list = []
    visited_dbs = set()
    # Collect candidate datasets
    for proj_name, proj_cfg in PROJECT_CONFIG.items():
        # Determine if cross‐project semantic sharing is allowed
        cross_allowed = (proj_name == current_project_name) or proj_cfg.get("semantic_aware", False)
        for ws_name, ws_cfg in proj_cfg.get("workspaces", {}).items():
            # Workspace level dataset
            ds_file = ws_cfg.get("dataset_file")
            iso_ws = ws_cfg.get("isolated", False)
            include_ws = False
            if ds_file:
                # Always include the current dataset
                if ds_file == current_dataset_file:
                    include_ws = True
                else:
                    # Cross‐project or same project? cross_allowed indicates semantics allowed
                    if cross_allowed and not iso_ws:
                        include_ws = True
            if include_ws and ds_file and ds_file not in visited_dbs:
                visited_dbs.add(ds_file)
                all_candidates.extend(_query_dataset_for_similarity(ds_file, query_emb, limit))
            # Threads
            for th_name, th_cfg in ws_cfg.get("threads", {}).items():
                th_ds = th_cfg.get("dataset_file")
                iso_th = th_cfg.get("isolated", False)
                include_th = False
                if th_ds:
                    if th_ds == current_dataset_file:
                        include_th = True
                    else:
                        if cross_allowed and not iso_th:
                            include_th = True
                if include_th and th_ds and th_ds not in visited_dbs:
                    visited_dbs.add(th_ds)
                    all_candidates.extend(_query_dataset_for_similarity(th_ds, query_emb, limit))
    # Sort all candidates by similarity and return top `limit`
    all_candidates.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in all_candidates[:limit]]

# -------------------- TOKEN COUNTING --------------------
def get_openai_max_tokens(model):
    try:
        info = openai_client.models.retrieve(model)
        return getattr(info, "max_completion_tokens", 8192)
    except Exception as e:
        log_message(f"cannot connect to OpenAI: {e}", level="error")
        return 4096

def get_ollama_max_tokens(model):
    try:
        payload = {"model": model, "prompt": " ", "stream": False}
        resp = requests.post("http://localhost:11434/api/generate", json=payload).json()
        return resp.get("eval_count", 4096)
    except Exception as e:
        log_message(f"Error retrieving Ollama max tokens for {model}: {e}", level="error")
        return 4096

def count_tokens(text, model="gpt-4o-mini", provider="OpenAI"):
    if provider == "OpenAI":
        try:
            return len(encoder.encode(text))
        except Exception:
            return len(text.split())
    else:
        return int(len(text.split()) * 1.3)

def truncate_conversation(conversation_text, model, provider):
    max_tokens = get_openai_max_tokens(model) if provider == "OpenAI" else get_ollama_max_tokens(model)
    max_allowed = int(max_tokens * 0.75)
    total = count_tokens(conversation_text, model, provider)
    if total <= max_allowed:
        return conversation_text
    lines = conversation_text.split("\n")
    truncated = ""
    current = 0
    for line in reversed(lines):
        tokens = count_tokens(line, model, provider)
        if current + tokens > max_allowed:
            break
        truncated = line + "\n" + truncated
        current += tokens
    return truncated

# -------------------- HELPER: Ensure Ollama Connection --------------------
def ensure_ollama_connection():
    try:
        output = subprocess.check_output(["ollama", "list"], universal_newlines=True)
        return output
    except Exception as e:
        log_message("Ollama not connected. Starting Ollama server...", level="warning")
        try:
            subprocess.Popen(["ollama", "server"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e2:
            log_message(f"Failed to start Ollama server: {e2}", level="error")
        time.sleep(5)
        output = subprocess.check_output(["ollama", "list"], universal_newlines=True)
        return output

# -------------------- OPENAI & TOKENIZER SETUP --------------------
OPENAI_API_KEY = load_api_key()
if not OPENAI_API_KEY:
    log_message("OpenAI API key is missing. Please check the file path.", level="error")
    sys.exit(1)

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
try:
    encoder = tiktoken.encoding_for_model("gpt-4o-mini")
except KeyError:
    encoder = tiktoken.get_encoding("cl100k_base")

try:
    response = openai_client.models.list()
    openai_models = [model.id for model in response.data]
    if openai_models:
        AVAILABLE_MODELS = openai_models
except Exception as e:
    log_message("cannot connect to OpenAI", level="error")

log_message("OpenAI and tokenizer setup complete.")

# -------------------- TTS FUNCTIONS --------------------
current_tts_process = None

# -------------------- TTS QUEUE MANAGER --------------------
class TTSManager:
    """
    Manage text-to-speech playback using pyttsx3 with a message queue.
    New messages are enqueued and spoken in order.  Playback runs on a
    separate thread so as not to block the main UI.  Stop and resume
    controls allow the user to interrupt and restart reading at the
    latest unread message.  Only one TTS engine instance is used to
    prevent resource contention.
    """
    def __init__(self, voice_name: str = "Zira", speed: float = 2.4):
        self.queue: list[str] = []
        self.index: int = 0
        self.playing: bool = False
        self.engine = pyttsx3.init()
        # Configure voice
        voices = self.engine.getProperty("voices")
        voice_id = None
        for v in voices:
            if voice_name.lower() in v.name.lower():
                voice_id = v.id
                break
        if voice_id:
            self.engine.setProperty("voice", voice_id)
        # Configure speed
        default_rate = self.engine.getProperty("rate")
        self.engine.setProperty("rate", int(default_rate * speed))
        self.thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
    def add_message(self, text: str) -> None:
        """Enqueue a message for playback and start reading if idle."""
        with self._lock:
            self.queue.append(text)
        # If not currently playing, kick off playback
        if not self.playing:
            self._start_playback()
    def _start_playback(self):
        if self.thread and self.thread.is_alive():
            return
        self.playing = True
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._play_loop, daemon=True)
        self.thread.start()
    def _play_loop(self):
        while True:
            if self._stop_event.is_set():
                break
            with self._lock:
                if self.index >= len(self.queue):
                    # Reached end of queue
                    self.playing = False
                    break
                text = self.queue[self.index]
                self.index += 1
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                log_message(f"TTS error: {e}", level="error")
        self.playing = False
    def stop(self) -> None:
        """Stop playback immediately.  The current index does not reset."""
        if self.playing:
            self._stop_event.set()
            try:
                self.engine.stop()
            except Exception:
                pass
            self.playing = False
    def resume(self) -> None:
        """Resume playback from the current queue position."""
        if self.playing:
            return
        if self.index < len(self.queue):
            self._start_playback()

def load_tts_settings():
    if os.path.exists(TTS_CONFIG_FILE):
        try:
            with open(TTS_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_TTS_SETTINGS.copy()

def save_tts_settings(settings):
    with open(TTS_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def get_voice_id(engine, voice_name):
    for voice in engine.getProperty("voices"):
        if voice_name.lower() in voice.name.lower():
            return voice.id
    return None

def speak_text(text):
    global current_tts_process
    settings = load_tts_settings()
    engine = pyttsx3.init()
    default_rate = engine.getProperty("rate")
    rate = int(default_rate * settings["speed"])
    engine.setProperty("rate", rate)
    voice_id = get_voice_id(engine, settings["voice"])
    if voice_id:
        engine.setProperty("voice", voice_id)
    stop_tts()
    code = (
        "import pyttsx3;"
        "engine = pyttsx3.init();"
        f"engine.setProperty('rate', {rate});"
        f"engine.setProperty('voice', '{voice_id}');"
        f"engine.say({repr(text)});"
        "engine.runAndWait()"
    )
    current_tts_process = subprocess.Popen([sys.executable, "-c", code])

def stop_tts():
    global current_tts_process
    if current_tts_process:
        try:
            current_tts_process.terminate()
        except Exception as e:
            log_message(f"Error stopping TTS: {e}", level="error")
        current_tts_process = None

# -------------------- SYNTAX HIGHLIGHTER --------------------
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#C586C0"))
        keywords = [
            "def", "class", "if", "elif", "else", "while", "for", "try", "except",
            "finally", "with", "as", "import", "from", "return", "pass", "break",
            "continue", "in", "not", "and", "or", "is", "lambda", "yield", "raise",
            "assert", "global", "nonlocal"
        ]
        for word in keywords:
            pattern = fr"\b{word}\b"
            self.rules.append((pattern, keyword_format))
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.rules.append((r'".*?"', string_format))
        self.rules.append((r"'.*?'", string_format))
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.rules.append((r"#.*", comment_format))
    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)

SMALL_BUTTON_STYLE = (
    "QPushButton { background-color: #FFF; border: 1px solid #CCC; color: #333; padding: 2px 5px; font-size: 8px; }"
    " QPushButton:hover { background-color: #EEE; }"
)
BABY_BLUE_BUTTON_STYLE = (
    "QPushButton { background-color: #ADD8E6; border: 1px solid #CCC; color: #333; padding: 2px 5px; font-size: 8px; border-radius: 10px; }"
    " QPushButton:hover { background-color: #B0E0E6; }"
)

# -------------------- MODEL SELECTION DIALOG --------------------
from PyQt6.QtWidgets import QDialog  # Already imported above
class ModelSelectionDialog(QDialog):
    def __init__(self, parent_app, parent=None):
        super().__init__(parent)
        self.parent_app = parent_app
        self.setWindowTitle("Select Provider and Model")
        self.selected_provider = GLOBAL_CONFIG["provider"]
        self.selected_model = self.parent_app.model_selector.currentText()
        self.action = None  # will be "send" or "set"
        
        layout = QVBoxLayout(self)
        # Provider selection
        provider_label = QLabel("Select Provider:")
        layout.addWidget(provider_label)
        self.provider_combo = QComboBox(self)
        self.provider_combo.addItems(["OpenAI", "Ollama"])
        self.provider_combo.setCurrentText(GLOBAL_CONFIG["provider"])
        self.provider_combo.currentTextChanged.connect(self.update_models)
        layout.addWidget(self.provider_combo)
        # Model selection
        model_label = QLabel("Select Model:")
        layout.addWidget(model_label)
        self.model_combo = QComboBox(self)
        self.update_models(self.provider_combo.currentText())
        self.model_combo.setCurrentText(self.selected_model)
        layout.addWidget(self.model_combo)
        # Buttons: Send, Set, Cancel
        button_box = QDialogButtonBox()
        self.send_button = QPushButton("Send")
        self.set_button = QPushButton("Set")
        self.cancel_button = QPushButton("Cancel")
        button_box.addButton(self.send_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(self.set_button, QDialogButtonBox.ButtonRole.ActionRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        self.send_button.clicked.connect(self.send_clicked)
        self.set_button.clicked.connect(self.set_clicked)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(button_box)
    def update_models(self, provider):
        self.model_combo.clear()
        if provider == "Ollama":
            models = self.parent_app.ollama_models if self.parent_app.ollama_models else [
                "huihui_ai/deepseek-r1-abliterated:7b",
                "huihui_ai/deepseek-r1-abliterated:8b",
                "deepseek-r1:14b",
                "deepseek-r1:8b",
                "deepseek-r1:32b",
                "llama3.1:latest",
                "dolphin-llama3:latest",
                "codellama:latest",
                "mistral:latest",
                "dolphin-llama3:8b"
            ]
        else:
            try:
                response = openai_client.models.list()
                models = [m.id for m in response.data]
                if not models:
                    models = AVAILABLE_MODELS
            except Exception:
                models = AVAILABLE_MODELS
        self.model_combo.addItems(models)
    def send_clicked(self):
        self.selected_provider = self.provider_combo.currentText()
        self.selected_model = self.model_combo.currentText()
        self.action = "send"
        self.accept()
    def set_clicked(self):
        self.selected_provider = self.provider_combo.currentText()
        self.selected_model = self.model_combo.currentText()
        self.action = "set"
        self.accept()

# -------------------- DIALOGS (continued) --------------------
class NewPromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Prompt")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setPlaceholderText("Enter prompt text here...")
        self.text_edit.setStyleSheet("QPlainTextEdit { color: lightgray; }")
        layout.addWidget(self.text_edit)
        hlayout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.ok_button.clicked.connect(self.accept)
        hlayout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.reject)
        hlayout.addWidget(self.cancel_button)
        layout.addLayout(hlayout)
    def getText(self):
        return self.text_edit.toPlainText().strip()

class ChatPromptControlDialog(QDialog):
    def __init__(self, workspace_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chat Prompt Control")
        self.workspace_dir = workspace_dir
        self.config_file = os.path.join(self.workspace_dir, "settings_config.json")
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.workspace_config = json.load(f)
        else:
            self.workspace_config = {"prompts": []}
        main_layout = QVBoxLayout(self)
        label = QLabel(f"Workspace Prompts - {os.path.basename(os.path.dirname(self.workspace_dir))}", self)
        label.setStyleSheet("color: lightgray;")
        main_layout.addWidget(label)
        self.prompt_list = QListWidget(self)
        self.prompt_list.setStyleSheet("QListWidget { color: lightgray; }")
        main_layout.addWidget(self.prompt_list)
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("New Prompt", self)
        self.btn_add.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.btn_add.clicked.connect(self.add_prompt)
        btn_row.addWidget(self.btn_add)
        self.btn_edit = QPushButton("Edit Prompt", self)
        self.btn_edit.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.btn_edit.clicked.connect(self.edit_prompt)
        btn_row.addWidget(self.btn_edit)
        self.btn_delete = QPushButton("❌ Delete Prompt", self)
        self.btn_delete.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.btn_delete.clicked.connect(self.delete_prompt)
        btn_row.addWidget(self.btn_delete)
        self.btn_toggle = QPushButton("Toggle Enable", self)
        self.btn_toggle.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.btn_toggle.clicked.connect(self.toggle_enable)
        btn_row.addWidget(self.btn_toggle)
        main_layout.addLayout(btn_row)
        self.refresh_list()
    def save_config(self):
        self.workspace_config.setdefault("prompts", [])
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.workspace_config, f, indent=4)
    def refresh_list(self):
        self.prompt_list.clear()
        for p in self.workspace_config.get("prompts", []):
            display = f"[{'X' if p.get('enabled', True) else ' '}] {p.get('text', '')}"
            item = QListWidgetItem(display)
            item.setForeground(QColor("lightgray"))
            self.prompt_list.addItem(item)
    def add_prompt(self):
        dlg = NewPromptDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            text = dlg.getText()
            if text:
                self.workspace_config.setdefault("prompts", []).append({"text": text, "enabled": True})
                self.save_config()
                self.refresh_list()
    def edit_prompt(self):
        idx = self.prompt_list.currentRow()
        if idx >= 0:
            current_text = self.workspace_config["prompts"][idx]["text"]
            new_text, ok = QInputDialog.getMultiLineText(self, "Edit Prompt", "Modify prompt text:", current_text)
            if ok and new_text.strip():
                self.workspace_config["prompts"][idx]["text"] = new_text.strip()
                self.save_config()
                self.refresh_list()
        else:
            QMessageBox.warning(self, "Selection Error", "No prompt selected to edit.")
    def delete_prompt(self):
        idx = self.prompt_list.currentRow()
        if idx >= 0:
            del self.workspace_config["prompts"][idx]
            self.save_config()
            self.refresh_list()
        else:
            QMessageBox.warning(self, "Selection Error", "No prompt selected to delete.")
    def toggle_enable(self):
        idx = self.prompt_list.currentRow()
        if idx >= 0:
            self.workspace_config["prompts"][idx]["enabled"] = not self.workspace_config["prompts"][idx].get("enabled", True)
            self.save_config()
            self.refresh_list()
        else:
            QMessageBox.warning(self, "Selection Error", "No prompt selected to toggle enable.")
    @staticmethod
    def get_active_prompts(workspace_dir):
        cf = os.path.join(workspace_dir, "settings_config.json")
        if os.path.exists(cf):
            with open(cf, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            return [p["text"] for p in cfg.get("prompts", []) if p.get("enabled", True)]
        return []

class GlobalPromptControlDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Prompt Control")
        main_layout = QVBoxLayout(self)
        label = QLabel("Global Prompts:", self)
        label.setStyleSheet("color: lightgray;")
        main_layout.addWidget(label)
        self.prompt_list = QListWidget(self)
        self.prompt_list.setStyleSheet("QListWidget { color: lightgray; }")
        main_layout.addWidget(self.prompt_list)
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("New Global Prompt", self)
        self.btn_add.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.btn_add.clicked.connect(self.add_prompt)
        btn_row.addWidget(self.btn_add)
        self.btn_edit = QPushButton("Edit Prompt", self)
        self.btn_edit.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.btn_edit.clicked.connect(self.edit_prompt)
        btn_row.addWidget(self.btn_edit)
        self.btn_delete = QPushButton("❌ Delete Prompt", self)
        self.btn_delete.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.btn_delete.clicked.connect(self.delete_prompt)
        btn_row.addWidget(self.btn_delete)
        self.btn_toggle = QPushButton("Toggle Enable", self)
        self.btn_toggle.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.btn_toggle.clicked.connect(self.toggle_enable)
        btn_row.addWidget(self.btn_toggle)
        main_layout.addLayout(btn_row)
        self.refresh_list()
    def refresh_list(self):
        self.prompt_list.clear()
        global_prompts = get_global_prompts()
        for prompt in global_prompts:
            display = f"[{'X' if prompt['enabled'] else ' '}] {prompt['text']}"
            item = QListWidgetItem(display)
            item.setForeground(QColor("lightgray"))
            item.setData(Qt.ItemDataRole.UserRole, prompt)
            self.prompt_list.addItem(item)
    def add_prompt(self):
        text, ok = QInputDialog.getText(self, "New Global Prompt", "Enter global prompt:")
        if ok and text.strip():
            filename = sanitize_filename(text.strip()) + ".txt"
            file_path = os.path.join(GLOBAL_PROMPTS_DIR, filename)
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text.strip())
                config = load_global_prompts_config()
                config[filename] = True
                save_global_prompts_config(config)
                self.refresh_list()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save global prompt: {e}")
    def edit_prompt(self):
        idx = self.prompt_list.currentRow()
        if idx >= 0:
            prompt_data = self.prompt_list.item(idx).data(Qt.ItemDataRole.UserRole)
            current_text = prompt_data["text"]
            new_text, ok = QInputDialog.getMultiLineText(self, "Edit Global Prompt", "Modify global prompt text:", current_text)
            if ok and new_text.strip():
                filename = prompt_data["filename"]
                file_path = os.path.join(GLOBAL_PROMPTS_DIR, filename)
                if not os.path.exists(file_path):
                    QMessageBox.warning(self, "Error", "Global prompt file not found.")
                    return
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_text.strip())
                    self.refresh_list()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to edit global prompt: {e}")
        else:
            QMessageBox.warning(self, "Selection Error", "No prompt selected to edit.")
    def delete_prompt(self):
        idx = self.prompt_list.currentRow()
        if idx >= 0:
            prompt_data = self.prompt_list.item(idx).data(Qt.ItemDataRole.UserRole)
            filename = prompt_data["filename"]
            file_path = os.path.join(GLOBAL_PROMPTS_DIR, filename)
            try:
                os.remove(file_path)
                config = load_global_prompts_config()
                if filename in config:
                    del config[filename]
                save_global_prompts_config(config)
                self.refresh_list()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete global prompt: {e}")
        else:
            QMessageBox.warning(self, "Selection Error", "No prompt selected to delete.")
    def toggle_enable(self):
        idx = self.prompt_list.currentRow()
        if idx >= 0:
            item = self.prompt_list.item(idx)
            prompt_data = item.data(Qt.ItemDataRole.UserRole)
            prompt_data["enabled"] = not prompt_data.get("enabled", True)
            config = load_global_prompts_config()
            config[prompt_data["filename"]] = prompt_data["enabled"]
            save_global_prompts_config(config)
            display = f"[{'X' if prompt_data['enabled'] else ' '}] {prompt_data['text']}"
            item.setText(display)
        else:
            QMessageBox.warning(self, "Selection Error", "No prompt selected to toggle enable.")

# -------------------- CODE BLOCK WIDGET --------------------
class CodeBlockWidget(QWidget):
    DEFAULT_COLLAPSED_HEIGHT = 200

    def __init__(self, code_text, parent_app, parent=None):
        super().__init__(parent)
        self.parent_app = parent_app

        # --- code editor setup ---
        self.code_editor = QPlainTextEdit()
        self.code_editor.setPlainText(code_text)
        self.code_editor.setReadOnly(True)
        self.code_editor.setFont(QFont("Courier", 10))
        # Use WidgetWidth so that the code wraps within the available width.
        self.code_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        # Attach the syntax highlighter to restore colored syntax.
        self.highlighter = PythonHighlighter(self.code_editor.document())
        self.code_editor.setStyleSheet("QPlainTextEdit { color: #DCDCDC; background-color: #1E1E1E; }")
        self.code_editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Compute natural height (if needed, you might adjust this calculation)
        self.code_editor.document().setTextWidth(self.code_editor.viewport().width())
        doc_h = int(self.code_editor.document().size().height() * self.code_editor.fontMetrics().height() + 10)
        self.natural_height = doc_h
        self.code_editor.setFixedHeight(min(doc_h, self.DEFAULT_COLLAPSED_HEIGHT))

        # --- layout ---
        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0,0,0,0)
        main_l.setSpacing(5)

        # checkbox row for full expand/collapse
        chk_l = QHBoxLayout()
        self.full_expand_checkbox = QCheckBox("Full Expand")
        self.full_expand_checkbox.stateChanged.connect(self.toggle_full_size)
        chk_l.addWidget(self.full_expand_checkbox)
        chk_l.addStretch()
        main_l.addLayout(chk_l)

        # frame wrapper
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: #1E1E1E; border-radius: 5px;")
        frame.setLayout(QVBoxLayout())
        frame.layout().setContentsMargins(5,5,5,5)
        frame.layout().addWidget(self.code_editor)
        main_l.addWidget(frame)

        # copy button row
        btn_l = QHBoxLayout()
        copy_btn = QPushButton("📋 Copy Code")
        copy_btn.clicked.connect(self.copy_code)
        btn_l.addWidget(copy_btn)
        btn_l.addStretch()
        main_l.addLayout(btn_l)

    def toggle_full_size(self, state: int):
        """Expand to full document height or collapse back."""
        checked = (state == CHECKED.value)
        if checked:
            new_h = self.natural_height
        else:
            new_h = min(self.natural_height, self.DEFAULT_COLLAPSED_HEIGHT)

        self.code_editor.setFixedHeight(new_h)
        # force relayout
        self.code_editor.updateGeometry()
        self.updateGeometry()

    def copy_code(self):
        pyperclip.copy(self.code_editor.toPlainText())

# -------------------- USER MESSAGE WIDGET --------------------
class UserMessageWidget(QWidget):
    def __init__(self, user_text, parent_app, parent=None):
        super().__init__(parent)
        self.parent_app = parent_app
        self.user_text = user_text
        self.original_user_text = user_text
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        user_frame = QFrame(self)
        user_frame.setStyleSheet("background-color: #004444; border-radius: 5px;")
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(8, 8, 8, 8)
        self.user_label = QLabel(f"<b>User:</b> {self.user_text}", self)
        self.user_label.setStyleSheet("color: #427aff;")
        # Ensure message text wraps if too long
        self.user_label.setWordWrap(True)
        self.user_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        user_layout.addWidget(self.user_label)
        self.edit_button = QPushButton("🖊️", self)
        self.edit_button.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.edit_button.clicked.connect(self.enable_edit_mode)
        user_layout.addWidget(self.edit_button)
        self.copy_user_btn = QPushButton("📋 Copy User", self)
        self.copy_user_btn.setStyleSheet("QPushButton { background-color: #ADD8E6; border: 1px solid #CCC; color: #333; padding: 2px 5px; font-size: 8px; } QPushButton:hover { background-color: #B0E0E6; }")
        self.copy_user_btn.clicked.connect(self.copy_user_message)
        user_layout.addWidget(self.copy_user_btn)
        user_layout.addStretch()
        layout.addWidget(user_frame)

    def copy_user_message(self):
        pyperclip.copy(self.user_text)

    def enable_edit_mode(self):
        self.user_label.hide()
        self.edit_button.hide()
        self.edit_text_edit = QPlainTextEdit(self)
        self.edit_text_edit.setPlainText(self.user_text)
        self.edit_text_edit.setStyleSheet("background-color: black; color: white;")
        self.layout().insertWidget(0, self.edit_text_edit)
        btn_layout = QHBoxLayout()
        self.confirm_button = QPushButton("✅", self)
        self.confirm_button.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.confirm_button.clicked.connect(self.confirm_edit)
        btn_layout.addWidget(self.confirm_button)
        self.cancel_button = QPushButton("❌", self)
        self.cancel_button.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.cancel_edit)
        btn_layout.addWidget(self.cancel_button)
        self.layout().insertLayout(1, btn_layout)

    def confirm_edit(self):
        edited_text = self.edit_text_edit.toPlainText().strip()
        if not edited_text:
            QMessageBox.warning(self, "Invalid Edit", "Edited message cannot be empty.")
            return
        self.parent_app.handle_edited_message(self, edited_text)

    def cancel_edit(self):
        self.edit_text_edit.deleteLater()
        self.confirm_button.deleteLater()
        self.cancel_button.deleteLater()
        self.user_label.show()
        self.edit_button.show()

# -------------------- GPT MESSAGE WIDGET --------------------
class GPTMessageWidget(QWidget):
    # UPDATED: Now accepts an extra parameter "provider" to remember which provider was used when the message was generated.
    def __init__(self, user_text, gpt_text, model_name, provider, parent_app, parent=None):
        super().__init__(parent)
        self.parent_app = parent_app
        self.user_text = user_text
        self.gpt_text = gpt_text
        self.model_name = model_name
        self.provider = provider  # NEW: stored provider from when the response was generated
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        gpt_frame = QFrame(self)
        if self.provider == "Ollama":
            gpt_frame.setStyleSheet("background-color: #464259; border-radius: 5px;")
        else:
            gpt_frame.setStyleSheet("background-color: #006666; border-radius: 5px;")
        gpt_layout = QVBoxLayout(gpt_frame)
        gpt_layout.setContentsMargins(8, 8, 8, 8)
        # UPDATED: Use self.provider in header instead of GLOBAL_CONFIG provider.
        header_label = QLabel(f"<b>{self.provider} ({self.model_name}):</b>", self)
        if self.provider == "Ollama":
            header_label.setStyleSheet("color: #9370DB;")
        else:
            header_label.setStyleSheet("color: #55ff42;")
        header_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        header_label.setWordWrap(True)
        gpt_layout.addWidget(header_label)
        self.gpt_container = QWidget(self)
        self.gpt_container_layout = QVBoxLayout(self.gpt_container)
        self.gpt_container_layout.setContentsMargins(0, 0, 0, 0)
        self.populate_gpt_content(self.gpt_text)
        gpt_layout.addWidget(self.gpt_container)
        layout.addWidget(gpt_frame)
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("color: #AAAAAA; margin: 5px 0;")
        layout.addWidget(divider)

    def populate_gpt_content(self, text):
        while self.gpt_container_layout.count():
            item = self.gpt_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        dash = r"[\-\u2500]"
        combined_pattern = rf"(?:```(?:\w+)?\n(.*?)\n```)|(?:^{dash}{{10,}}\s*\n(.*?)\n^{dash}{{10,}}\s*$)"
        regex = re.compile(combined_pattern, re.DOTALL | re.MULTILINE)
        
        matches = regex.findall(text)
        
        def replacement(_):
            return "[CODE BLOCK]"
        
        main_text = regex.sub(replacement, text).strip()
        
        if main_text:
            content_label = QLabel(main_text, self)
            content_label.setWordWrap(True)
            content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            content_label.setStyleSheet("color: lightgray;")
            self.gpt_container_layout.addWidget(content_label)
        
        for m in matches:
            code = m[0] if m[0] else m[1]
            if code.strip():
                self.gpt_container_layout.addWidget(CodeBlockWidget(code.strip(), self.parent_app, self))
        
        btn_layout = QHBoxLayout()
        
        copy_all_btn = QPushButton("📋 Copy All", self)
        copy_all_btn.setStyleSheet(SMALL_BUTTON_STYLE)
        copy_all_btn.clicked.connect(self.copy_all)
        btn_layout.addWidget(copy_all_btn)
        
        copy_resp_btn = QPushButton("🤖 Copy Response Only", self)
        copy_resp_btn.setStyleSheet(SMALL_BUTTON_STYLE)
        copy_resp_btn.clicked.connect(self.copy_response_only)
        btn_layout.addWidget(copy_resp_btn)
        
        copy_user_btn = QPushButton("📋 Copy User", self)
        copy_user_btn.setStyleSheet(
            "QPushButton { background-color: #ADD8E6; border: 1px solid #CCC; color: #333; padding: 2px 5px; font-size: 8px; }"
            "QPushButton:hover { background-color: #B0E0E6; }"
        )
        copy_user_btn.clicked.connect(self.copy_user_message)
        btn_layout.addWidget(copy_user_btn)
        
        switch_model_btn = QPushButton("♻️ Switch Model", self)
        switch_model_btn.setStyleSheet(SMALL_BUTTON_STYLE)
        switch_model_btn.clicked.connect(self.switch_model)
        btn_layout.addWidget(switch_model_btn)
        
        btn_layout.addStretch()
        self.gpt_container_layout.addLayout(btn_layout)


    def copy_all(self):
        pyperclip.copy(f"User: {self.user_text}\n\n{self.provider} ({self.model_name}): {self.gpt_text}")

    def copy_response_only(self):
        pyperclip.copy(f"{self.provider} ({self.model_name}): {self.gpt_text}")

    def copy_user_message(self):
        pyperclip.copy(self.user_text)

    def switch_model(self):
        if self.parent_app.switch_in_progress:
            QMessageBox.information(self, "Please Wait", "A response is already being generated.")
            return
        self.parent_app.switch_in_progress = True
        dialog = ModelSelectionDialog(self.parent_app)
        if dialog.exec() == QDialog.DialogCode.Rejected:
            self.parent_app.switch_in_progress = False
            return
        selected_provider = dialog.selected_provider
        selected_model = dialog.selected_model
        action = dialog.action  # "send" or "set"
        if selected_provider != GLOBAL_CONFIG["provider"]:
            GLOBAL_CONFIG["provider"] = selected_provider
            save_global_config(GLOBAL_CONFIG)
            self.parent_app.update_provider(selected_provider)
        self.parent_app.model_selector.setCurrentText(selected_model)
        if action == "set":
            self.parent_app.switch_in_progress = False
            return
        layout = self.parent_app.chat_layout
        idx = None
        for i in range(layout.count()):
            if layout.itemAt(i).widget() is self:
                idx = i
                break
        if idx is None:
            self.parent_app.switch_in_progress = False
            return
        while layout.count() > idx:
            w = layout.takeAt(idx).widget()
            if w:
                w.deleteLater()
        try:
            provider = GLOBAL_CONFIG["provider"]
            if provider == "Ollama":
                payload = {"model": selected_model, "messages": [{"role": "user", "content": self.user_text}], "stream": False}
                resp = requests.post("http://localhost:11434/api/chat", json=payload).json()
                try:
                    new_text = resp["message"]["content"]
                except KeyError:
                    new_text = resp.get("response", f"Unexpected response structure: {resp}")
            else:
                resp = openai_client.chat.completions.create(model=selected_model, messages=[{"role": "user", "content": self.user_text}])
                new_text = resp.choices[0].message.content
        except Exception as e:
            new_text = f"Error: {str(e)}"
        # When switching model, the new message is created using the current provider.
        new_widget = GPTMessageWidget(self.user_text, new_text, selected_model, GLOBAL_CONFIG["provider"], self.parent_app)
        layout.insertWidget(idx, new_widget)
        self.parent_app.switch_in_progress = False

# -------------------- PROJECT MANAGER --------------------
class ProjectManager(QWidget):
    # signals
    threadSelected   = pyqtSignal(str)
    workspaceSelected = pyqtSignal(str)
    projectSelected   = pyqtSignal(str)

    ISOL_COL = 1           # column-index holding the “Isolated” check-box

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.clipboard = None

        layout   = QVBoxLayout(self)
        top_row  = QHBoxLayout()

        new_proj_btn  = QPushButton("New Project", self)
        new_proj_btn.setStyleSheet("background-color:#D8BFD8;")
        new_proj_btn.clicked.connect(self.new_project)
        top_row.addWidget(new_proj_btn)

        paste_proj_btn = QPushButton("Paste Project", self)
        paste_proj_btn.setStyleSheet("background-color:#D8BFD8;")
        paste_proj_btn.clicked.connect(self.paste_project)
        top_row.addWidget(paste_proj_btn)

        new_ws_btn   = QPushButton("New Workspace", self)
        new_ws_btn.setStyleSheet("background-color:#D8BFD8;")
        new_ws_btn.clicked.connect(self.new_workspace)
        top_row.addWidget(new_ws_btn)

        layout.addLayout(top_row)

        # ---- tree widget ----
        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Name", "Isolated"])
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setStyleSheet("QHeaderView::section{background:#333;color:white;font-weight:bold;}")

        self.tree.setItemsExpandable(True)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)

        layout.addWidget(self.tree)
        self.refresh_tree()
        self.tree.expandAll()

    # ------------------------------------------------------------------
    # CORE REFRESH ------------------------------------------------------
    # ------------------------------------------------------------------
    def refresh_tree(self):
        """Re-build hierarchy & restore isolation flags."""
        self.tree.blockSignals(True)
        self.tree.clear()

        global PROJECT_CONFIG
        prev_cfg = load_project_config()
        PROJECT_CONFIG = {}

        os.makedirs(PROJECTS_DIR, exist_ok=True)

        for proj in os.listdir(PROJECTS_DIR):
            if proj == "Global_Prompts":
                continue
            proj_path = os.path.join(PROJECTS_DIR, proj)
            if not os.path.isdir(proj_path):
                continue

            proj_cfg_prev = prev_cfg.get(proj, {})
            sem_flag   = bool(proj_cfg_prev.get("semantic_aware", False))

            PROJECT_CONFIG[proj] = {"path": proj_path,
                                    "semantic_aware": sem_flag,
                                    "workspaces": {}}

            # Project row (no “isolated” checkbox)
            proj_item = QTreeWidgetItem(self.tree, [proj, ""])
            proj_item.setFirstColumnSpanned(True)
            proj_item.setForeground(0, QColor("lightblue"))
            proj_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "project",
                                                            "path": proj_path})
            # semantic-aware checkbox lives in column-0 only
            proj_item.setFlags(proj_item.flags() |
                               Qt.ItemFlag.ItemIsUserCheckable |
                               Qt.ItemFlag.ItemIsAutoTristate)
            proj_item.setCheckState(0, CHECKED if sem_flag else Qt.CheckState.Unchecked)

            # -------- workspaces ----------
            for ws in os.listdir(proj_path):
                ws_path = os.path.join(proj_path, ws)
                if not os.path.isdir(ws_path):
                    continue

                conv_folder = os.path.join(ws_path, "workspace")
                os.makedirs(conv_folder, exist_ok=True)
                conv_file = os.path.join(conv_folder, f"{ws}.txt")
                if not os.path.exists(conv_file):
                    open(conv_file, "w", encoding="utf-8").close()

                ws_prev = proj_cfg_prev.get("workspaces", {}).get(ws, {})
                ws_iso  = bool(ws_prev.get("isolated", False))

                # derive the dataset path from the conversation file; this
                # ensures the dataset lives alongside the transcript and
                # uses the same basename with a `.db` suffix.  See
                # dataset_path_for for details.
                ws_dataset = dataset_path_for(conv_file)
                ensure_dataset_db(ws_dataset)

                PROJECT_CONFIG[proj]["workspaces"][ws] = {
                    "path": ws_path,
                    "conv_file": conv_file,
                    "dataset_file": ws_dataset,
                    "isolated": ws_iso,
                    "threads": {}
                }

                ws_item = QTreeWidgetItem(proj_item, [ws, ""])
                ws_item.setForeground(0, QColor("black"))
                ws_item.setBackground(0, QColor("#D8BFD8"))
                ws_item.setData(0, Qt.ItemDataRole.UserRole,
                                {"type": "workspace",
                                 "path": ws_path,
                                 "conv_file": conv_file})

                # column-0 (spawn-thread trigger) – checkable
                ws_item.setFlags(ws_item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable)
                ws_item.setCheckState(0, Qt.CheckState.Unchecked)

                # column-1 (isolated flag) – independent
                ws_item.setFlags(ws_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                ws_item.setCheckState(self.ISOL_COL, CHECKED if ws_iso else Qt.CheckState.Unchecked)

                # -------- threads ----------
                threads_folder = os.path.join(ws_path, "threads")
                os.makedirs(threads_folder, exist_ok=True)

                for fname in os.listdir(threads_folder):
                    if not fname.endswith(".txt"):
                        continue
                    th_path = os.path.join(threads_folder, fname)
                    th_base = fname[:-4]
                    # compute dataset path for this thread transcript.  This
                    # places the dataset alongside the .txt file and uses
                    # the same base name with `.db` suffix.
                    th_dataset = dataset_path_for(th_path)
                    ensure_dataset_db(th_dataset)

                    th_prev = ws_prev.get("threads", {}).get(fname, {})
                    th_iso  = bool(th_prev.get("isolated", False))

                    PROJECT_CONFIG[proj]["workspaces"][ws]["threads"][fname] = {
                        "path": th_path,
                        "dataset_file": th_dataset,
                        "isolated": th_iso
                    }

                    th_item = QTreeWidgetItem(ws_item, [fname, ""])
                    th_item.setForeground(0, QColor("white"))
                    th_item.setBackground(0, QColor("#8A2BE2"))
                    th_item.setData(0, Qt.ItemDataRole.UserRole,
                                    {"type": "thread",
                                     "path": th_path})

                    # no spawn-thread behaviour here
                    th_item.setFlags(th_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    th_item.setCheckState(self.ISOL_COL, CHECKED if th_iso else UNCHECKED)

        save_project_config(PROJECT_CONFIG)
        self.tree.blockSignals(False)
        self.tree.expandAll()

    # ------------------------------------------------------------------
    # HELPERS -----------------------------------------------------------
    # ------------------------------------------------------------------
    def _spawn_thread(self, ws_item: QTreeWidgetItem):
        """Create a brand-new thread under the given workspace item."""
        ws_data = ws_item.data(0, Qt.ItemDataRole.UserRole)
        ws_path = ws_data["path"]
        threads_folder = os.path.join(ws_path, "threads")
        os.makedirs(threads_folder, exist_ok=True)

        ts   = int(time.time())
        name = f"{ws_item.text(0)} Thread {ts}.txt"
        new_thread_path = os.path.join(threads_folder, name)
        open(new_thread_path, "w", encoding="utf-8").close()

        # compute dataset file path using the helper; this ensures the
        # dataset lives alongside the transcript and preserves naming
        # consistency across workspaces and threads.
        new_db = dataset_path_for(new_thread_path)
        ensure_dataset_db(new_db)

        # add to PROJECT_CONFIG
        proj_item = ws_item.parent()
        proj_name = proj_item.text(0)
        ws_name   = ws_item.text(0)
        PROJECT_CONFIG[proj_name]["workspaces"][ws_name]["threads"][name] = {
            "path": new_thread_path,
            "dataset_file": new_db,
            "isolated": False
        }
        save_project_config(PROJECT_CONFIG)

        # Add thread to tree under the workspace item
        th_item = QTreeWidgetItem(ws_item, [name, ""])
        th_item.setForeground(0, QColor("white"))
        th_item.setBackground(0, QColor("#8A2BE2"))
        th_item.setFlags(th_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        th_item.setCheckState(self.ISOL_COL, UNCHECKED)
        th_item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "thread",
            "path": new_thread_path
        })

        # Expand the workspace node and trigger thread load
        self.tree.expandItem(ws_item)
        self.parent().load_thread(new_thread_path)

    # ------------------------------------------------------------------
    # ITEM CLICK / CHANGE ----------------------------------------------
    # ------------------------------------------------------------------
    def on_item_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        if data["type"] == "thread":
            self.threadSelected.emit(data["path"])
        elif data["type"] == "workspace":
            self.workspaceSelected.emit(data["conv_file"])
        elif data["type"] == "project":
            self.projectSelected.emit(data["path"])

    def on_item_changed(self, item, column):
        """
        Handles item checkbox changes:
        - Column 0: Workspace "spawn new thread" checkbox
        - Column 1: Isolation mode toggle
        """
        if not item or not item.data(0, Qt.ItemDataRole.UserRole):
            return

        data = item.data(0, Qt.ItemDataRole.UserRole)

        # >>> Spawn new thread when column-0 of workspace is ticked
        if data["type"] == "workspace" and column == 0 and item.checkState(0) == CHECKED:
            self._spawn_thread(item)
            item.setCheckState(0, UNCHECKED)

        # >>> Isolation checkbox toggled
        if column != self.ISOL_COL:
            return

        iso_flag = (item.checkState(self.ISOL_COL) == CHECKED)

        if data["type"] == "workspace":
            self._set_workspace_isolation(item, iso_flag)

        elif data["type"] == "thread":
            self._set_thread_isolation(item, iso_flag)

    def _set_workspace_isolation(self, item, flag):
        proj = item.parent().text(0)
        ws   = item.text(0)
        PROJECT_CONFIG[proj]["workspaces"][ws]["isolated"] = flag
        save_project_config(PROJECT_CONFIG)

    def _set_thread_isolation(self, item, flag):
        proj = item.parent().parent().text(0)
        ws   = item.parent().text(0)
        th   = item.text(0)
        PROJECT_CONFIG[proj]["workspaces"][ws]["threads"][th]["isolated"] = flag
        save_project_config(PROJECT_CONFIG)

    # ------------------------------------------------------------------
    # (context-menu & misc handlers unchanged … keep your previous code)
    # ------------------------------------------------------------------
    def open_context_menu(self, position):
        item = self.tree.itemAt(position)
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        menu = QMenu()
        action_copy = menu.addAction("Copy")
        action_paste = menu.addAction("Paste")
        if data:
            if data.get("type") == "project":
                action_rename = menu.addAction("Rename Project")
                action_fork = menu.addAction("Fork Project")
                action_delete = menu.addAction("Delete Project")
                action = menu.exec(self.tree.viewport().mapToGlobal(position))
                if action == action_copy:
                    self.clipboard = {"type": "project", "path": data["path"], "name": item.text(0)}
                    log_message(f"Project {item.text(0)} copied for paste.")
                elif action == action_paste:
                    if self.clipboard and self.clipboard.get("type") == "project":
                        new_proj_name, ok = QInputDialog.getText(self, "Paste Project", "Enter new project name for paste:", text=self.clipboard["name"] + " Copy")
                        if ok and new_proj_name.strip():
                            if re.search(r'[<>:"/\\|?*\n]', new_proj_name):
                                QMessageBox.warning(self, "Invalid Name", "Project name contains invalid characters or newlines.")
                                return
                            dest = os.path.join(PROJECTS_DIR, new_proj_name.strip())
                            try:
                                shutil.copytree(self.clipboard["path"], dest)
                                PROJECT_CONFIG[new_proj_name.strip()] = {"path": dest, "workspaces": {}}
                                save_project_config(PROJECT_CONFIG)
                                log_message(f"Project pasted as {new_proj_name.strip()}.")
                                self.refresh_tree()
                            except Exception as e:
                                QMessageBox.warning(self, "Error", f"Paste project failed: {e}")
                                log_message(f"Paste project failed: {e}", level="error")
                        self.clipboard = None
                    else:
                        QMessageBox.warning(self, "Paste Error", "Clipboard does not contain a project.")
                elif action == action_rename:
                    new_name, ok = QInputDialog.getText(self, "Rename Project", "Enter new project name:")
                    if ok and new_name.strip():
                        if re.search(r'[<>:"/\\|?*\n]', new_name):
                            QMessageBox.warning(self, "Invalid Name", "Project name contains invalid characters or newlines.")
                            return
                        parent_dir = os.path.dirname(data["path"])
                        new_path = os.path.join(parent_dir, new_name.strip())
                        try:
                            os.rename(data["path"], new_path)
                            old_proj = item.text(0)
                            PROJECT_CONFIG[new_name.strip()] = PROJECT_CONFIG.pop(old_proj)
                            PROJECT_CONFIG[new_name.strip()]["path"] = new_path
                            for ws_name, ws_info in PROJECT_CONFIG[new_name.strip()]["workspaces"].items():
                                conv_folder = os.path.join(ws_info["path"], "workspace")
                                ws_info["conv_file"] = os.path.join(conv_folder, f"{os.path.basename(ws_info['path'])}.txt")
                            save_project_config(PROJECT_CONFIG)
                            item.setText(0, new_name.strip())
                            data["path"] = new_path
                            item.setData(0, Qt.ItemDataRole.UserRole, data)
                            self.refresh_tree()
                            log_message(f"Project renamed to {new_name.strip()}")
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Rename project failed: {e}")
                            log_message(f"Rename project failed: {e}", level="error")
                elif action == action_fork:
                    new_name, ok = QInputDialog.getText(self, "Fork Project", "Enter new project name for fork:")
                    if ok and new_name.strip():
                        if re.search(r'[<>:"/\\|?*\n]', new_name):
                            QMessageBox.warning(self, "Invalid Name", "Project name contains invalid characters or newlines.")
                            return
                        dest = os.path.join(PROJECTS_DIR, new_name.strip())
                        try:
                            shutil.copytree(data["path"], dest)
                            PROJECT_CONFIG[new_name.strip()] = {"path": dest, "workspaces": {}}
                            save_project_config(PROJECT_CONFIG)
                            log_message(f"Project forked as {new_name.strip()}.")
                            self.refresh_tree()
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Fork project failed: {e}")
                            log_message(f"Fork project failed: {e}", level="error")
                elif action == action_delete:
                    reply = QMessageBox.question(self, "Delete Project",
                        f"Are you sure you want to delete project '{item.text(0)}' and all its contents?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            shutil.rmtree(data["path"])
                            if self.parent().current_workspace_file and self.parent().current_workspace_file.startswith(data["path"]):
                                self.parent().clear_chat_layout()
                            PROJECT_CONFIG.pop(item.text(0), None)
                            save_project_config(PROJECT_CONFIG)
                            log_message(f"Project {item.text(0)} deleted.")
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Delete project failed: {e}")
                            log_message(f"Delete project failed: {e}", level="error")
                        self.refresh_tree()
            elif data.get("type") == "workspace":
                action_rename = menu.addAction("Rename Workspace")
                action_clone = menu.addAction("Clone Workspace")
                action_delete = menu.addAction("Delete Workspace")
                action = menu.exec(self.tree.viewport().mapToGlobal(position))
                if action == action_copy:
                    self.clipboard = {"type": "workspace", "path": data["path"], "name": item.text(0)}
                    log_message(f"Workspace {item.text(0)} copied for paste.")
                elif action == action_paste:
                    if self.clipboard and self.clipboard.get("type") == "workspace":
                        new_name, ok = QInputDialog.getText(self, "Paste Workspace", "Enter new workspace name for paste:", text=self.clipboard["name"] + " Copy")
                        if ok and new_name.strip():
                            if re.search(r'[<>:"/\\|?*\n]', new_name):
                                QMessageBox.warning(self, "Invalid Name", "Workspace name contains invalid characters or newlines.")
                                return
                            dest = os.path.join(os.path.dirname(data["path"]), new_name.strip())
                            try:
                                shutil.copytree(self.clipboard["path"], dest)
                                conv_folder = os.path.join(dest, "workspace")
                                os.makedirs(conv_folder, exist_ok=True)
                                conv_file = os.path.join(conv_folder, f"{new_name.strip()}.txt")
                                # ensure a new conversation file exists
                                with open(conv_file, "w", encoding="utf-8") as f:
                                    f.write("")
                                # compute dataset file for the pasted workspace
                                dataset_file = dataset_path_for(conv_file)
                                # determine original dataset and copy its contents if available
                                orig_ws_path = self.clipboard["path"]
                                orig_conv = os.path.join(orig_ws_path, "workspace", f"{os.path.basename(orig_ws_path)}.txt")
                                orig_dataset = dataset_path_for(orig_conv)
                                try:
                                    if os.path.exists(orig_dataset):
                                        shutil.copy2(orig_dataset, dataset_file)
                                    else:
                                        ensure_dataset_db(dataset_file)
                                except Exception:
                                    ensure_dataset_db(dataset_file)
                                proj_item = item.parent()
                                proj = proj_item.text(0)
                                PROJECT_CONFIG[proj]["workspaces"][new_name.strip()] = {
                                    "path": dest,
                                    "conv_file": conv_file,
                                    "dataset_file": dataset_file,
                                    "isolated": False,
                                    "threads": {}
                                }
                                save_project_config(PROJECT_CONFIG)
                                log_message(f"Workspace pasted as {new_name.strip()}.")
                                self.refresh_tree()
                                self.parent().load_workspace(conv_file)
                            except Exception as e:
                                QMessageBox.warning(self, "Error", f"Paste workspace failed: {e}")
                                log_message(f"Paste workspace failed: {e}", level="error")
                    else:
                        QMessageBox.warning(self, "Paste Error", "Clipboard does not contain a workspace.")
                elif action == action_rename:
                    new_name, ok = QInputDialog.getText(self, "Rename Workspace", "Enter new workspace name:", text=item.text(0))
                    if ok and new_name.strip():
                        if re.search(r'[<>:"/\\|?*\n]', new_name):
                            QMessageBox.warning(self, "Invalid Name", "Workspace name contains invalid characters or newlines.")
                            return
                        parent_path = os.path.dirname(data["path"])
                        new_path = os.path.join(parent_path, new_name.strip())
                        try:
                            # Keep track of the old values before modifying data
                            old_ws = item.text(0)
                            old_path = data["path"]
                            old_conv_file = data.get("conv_file") or os.path.join(os.path.join(old_path, "workspace"), f"{old_ws}.txt")
                            # rename the underlying directory on disk
                            os.rename(old_path, new_path)
                            # compute new conversation file path
                            conv_folder = os.path.join(new_path, "workspace")
                            os.makedirs(conv_folder, exist_ok=True)
                            new_conv_file = os.path.join(conv_folder, f"{os.path.basename(new_path)}.txt")
                            # rename conversation file if the old one exists
                            try:
                                if os.path.exists(old_conv_file) and old_conv_file != new_conv_file:
                                    os.rename(old_conv_file, new_conv_file)
                            except Exception:
                                pass
                            # rename the dataset file alongside the conversation file
                            try:
                                old_dataset = dataset_path_for(old_conv_file)
                                new_dataset = dataset_path_for(new_conv_file)
                                if os.path.exists(old_dataset) and old_dataset != new_dataset:
                                    os.rename(old_dataset, new_dataset)
                                else:
                                    ensure_dataset_db(new_dataset)
                            except Exception:
                                # fallback to creating the new dataset
                                ensure_dataset_db(dataset_path_for(new_conv_file))
                            # update the item and data record
                            item.setText(0, new_name.strip())
                            data["path"] = new_path
                            data["conv_file"] = new_conv_file
                            item.setData(0, Qt.ItemDataRole.UserRole, data)
                            # update PROJECT_CONFIG: remove old key, insert new
                            proj_item = item.parent()
                            proj = proj_item.text(0)
                            ws_cfg = PROJECT_CONFIG[proj]["workspaces"].pop(old_ws)
                            ws_cfg["path"] = new_path
                            ws_cfg["conv_file"] = new_conv_file
                            ws_cfg["dataset_file"] = dataset_path_for(new_conv_file)
                            PROJECT_CONFIG[proj]["workspaces"][new_name.strip()] = ws_cfg
                            save_project_config(PROJECT_CONFIG)
                            log_message(f"Workspace renamed to {new_name.strip()}")
                            # reload workspace in UI
                            self.parent().load_workspace(new_conv_file)
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Rename workspace failed: {e}")
                elif action == action_clone:
                    new_name, ok = QInputDialog.getText(self, "Clone Workspace", "Enter new workspace name for clone:", text=item.text(0) + " Clone")
                    if ok and new_name.strip():
                        if re.search(r'[<>:"/\\|?*\n]', new_name):
                            QMessageBox.warning(self, "Invalid Name", "Workspace name contains invalid characters or newlines.")
                            return
                        parent_path = os.path.dirname(data["path"])
                        dest = os.path.join(parent_path, new_name.strip())
                        try:
                            shutil.copytree(data["path"], dest)
                            conv_folder = os.path.join(dest, "workspace")
                            os.makedirs(conv_folder, exist_ok=True)
                            conv_file = os.path.join(conv_folder, f"{new_name.strip()}.txt")
                            # if the conversation file doesn't exist under the cloned folder, create it
                            if not os.path.exists(conv_file):
                                with open(conv_file, "w", encoding="utf-8") as f:
                                    f.write("")
                            # compute dataset file for the clone and copy original dataset if available
                            dataset_file = dataset_path_for(conv_file)
                            # compute original dataset path from original conversation
                            orig_conv = data.get("conv_file") or os.path.join(os.path.join(data["path"], "workspace"), f"{item.text(0)}.txt")
                            orig_dataset = dataset_path_for(orig_conv)
                            try:
                                if os.path.exists(orig_dataset):
                                    shutil.copy2(orig_dataset, dataset_file)
                                else:
                                    ensure_dataset_db(dataset_file)
                            except Exception:
                                ensure_dataset_db(dataset_file)
                            proj_item = item.parent()
                            proj = proj_item.text(0)
                            PROJECT_CONFIG[proj]["workspaces"][new_name.strip()] = {
                                "path": dest,
                                "conv_file": conv_file,
                                "dataset_file": dataset_file,
                                "isolated": False,
                                "threads": {}
                            }
                            save_project_config(PROJECT_CONFIG)
                            log_message(f"Workspace cloned as {new_name.strip()}")
                            self.refresh_tree()
                            self.parent().load_workspace(conv_file)
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Clone workspace failed: {e}")
                            log_message(f"Clone workspace failed: {e}", level="error")
                elif action == action_delete:
                    reply = QMessageBox.question(self, "Delete Workspace",
                        f"Are you sure you want to delete workspace '{item.text(0)}' and all its contents?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            shutil.rmtree(data["path"])
                            if self.parent().current_workspace_file and self.parent().current_workspace_file.startswith(data["path"]):
                                self.parent().clear_chat_layout()
                            proj_item = item.parent()
                            proj = proj_item.text(0)
                            PROJECT_CONFIG[proj]["workspaces"].pop(item.text(0), None)
                            save_project_config(PROJECT_CONFIG)
                            log_message(f"Workspace {item.text(0)} deleted.")
                            remaining = list(PROJECT_CONFIG.get(proj, {}).get("workspaces", {}).values())
                            if remaining:
                                default_conv = remaining[0]["conv_file"]
                                self.parent().load_workspace(default_conv)
                            else:
                                self.parent().clear_chat_layout()
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Delete workspace failed: {e}")
                            log_message(f"Delete workspace failed: {e}", level="error")
                        self.refresh_tree()
            elif data.get("type") == "thread":
                action_rename = menu.addAction("Rename Thread")
                action_clone = menu.addAction("Clone Thread")
                action_delete = menu.addAction("Delete Thread")
                action = menu.exec(self.tree.viewport().mapToGlobal(position))
                if action == action_copy:
                    self.clipboard = {"type": "thread", "path": data["path"], "name": item.text(0)}
                    log_message(f"Thread {item.text(0)} copied for paste.")
                elif action == action_paste:
                    if self.clipboard and self.clipboard.get("type") == "thread":
                        parent_item = item.parent()
                        ws_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
                        if ws_data and ws_data.get("path"):
                            threads_folder = os.path.join(ws_data["path"], "threads")
                            new_file = self.clipboard["name"] + " Copy.txt"
                            new_path = os.path.join(threads_folder, new_file)
                            try:
                                # copy the conversation transcript
                                shutil.copy(self.clipboard["path"], new_path)
                                # derive dataset path for the new thread
                                new_dataset = dataset_path_for(new_path)
                                # copy the original dataset file if present
                                orig_dataset = dataset_path_for(self.clipboard["path"])
                                try:
                                    if os.path.exists(orig_dataset):
                                        shutil.copy2(orig_dataset, new_dataset)
                                    else:
                                        ensure_dataset_db(new_dataset)
                                except Exception:
                                    ensure_dataset_db(new_dataset)
                                # update project configuration to include new thread metadata
                                proj_item = parent_item.parent()
                                proj = proj_item.text(0)
                                ws_name = parent_item.text(0)
                                PROJECT_CONFIG[proj]["workspaces"][ws_name]["threads"][new_file] = {
                                    "path": new_path,
                                    "dataset_file": new_dataset,
                                    "isolated": False
                                }
                                save_project_config(PROJECT_CONFIG)
                                log_message(f"Thread pasted as {new_file}")
                                self.refresh_tree()
                                self.parent().load_thread(new_path)
                            except Exception as e:
                                QMessageBox.warning(self, "Error", f"Paste thread failed: {e}")
                                log_message(f"Paste thread failed: {e}", level="error")
                    else:
                        QMessageBox.warning(self, "Paste Error", "Clipboard does not contain a thread.")
                elif action == action_rename:
                    old_thread_name = item.text(0)
                    new_name, ok = QInputDialog.getText(self, "Rename Thread", "Enter new thread name:", text=old_thread_name)
                    if ok and new_name.strip():
                        if re.search(r'[<>:"/\\|?*\n]', new_name):
                            QMessageBox.warning(self, "Invalid Name", "Thread name contains invalid characters or newlines.")
                            return
                        parent_item = item.parent()
                        ws_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
                        if ws_data and ws_data.get("path"):
                            threads_folder = os.path.join(ws_data["path"], "threads")
                            new_file = new_name.strip() + ".txt"
                            new_path = os.path.join(threads_folder, new_file)
                            try:
                                # rename the conversation file
                                os.rename(data["path"], new_path)
                                # rename the dataset alongside the conversation file
                                old_dataset = dataset_path_for(data["path"])
                                new_dataset = dataset_path_for(new_path)
                                try:
                                    if os.path.exists(old_dataset) and old_dataset != new_dataset:
                                        os.rename(old_dataset, new_dataset)
                                    else:
                                        ensure_dataset_db(new_dataset)
                                except Exception:
                                    ensure_dataset_db(new_dataset)
                                # update UI item
                                item.setText(0, new_file)
                                data["path"] = new_path
                                item.setData(0, Qt.ItemDataRole.UserRole, data)
                                # update project configuration
                                proj_item = parent_item.parent()
                                proj = proj_item.text(0)
                                ws_name = parent_item.text(0)
                                # capture old config entry if exists
                                old_cfg = PROJECT_CONFIG[proj]["workspaces"][ws_name]["threads"].pop(old_thread_name, None)
                                # new config entry
                                new_cfg = old_cfg if isinstance(old_cfg, dict) else {}
                                new_cfg["path"] = new_path
                                new_cfg["dataset_file"] = new_dataset
                                new_cfg["isolated"] = new_cfg.get("isolated", False)
                                PROJECT_CONFIG[proj]["workspaces"][ws_name]["threads"][new_file] = new_cfg
                                save_project_config(PROJECT_CONFIG)
                                log_message(f"Thread renamed to {new_file}")
                                self.parent().load_thread(new_path)
                            except Exception as e:
                                QMessageBox.warning(self, "Error", f"Rename thread failed: {e}")
                elif action == action_clone:
                    parent_item = item.parent()
                    ws_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
                    if ws_data and ws_data.get("path"):
                        threads_folder = os.path.join(ws_data["path"], "threads")
                        timestamp = int(time.time())
                        new_file = f"{item.text(0)} Clone {timestamp}.txt"
                        new_path = os.path.join(threads_folder, new_file)
                        try:
                            # copy the conversation transcript
                            shutil.copy(data["path"], new_path)
                            # derive dataset path for the clone
                            new_dataset = dataset_path_for(new_path)
                            # copy original dataset if present
                            orig_dataset = dataset_path_for(data["path"])
                            try:
                                if os.path.exists(orig_dataset):
                                    shutil.copy2(orig_dataset, new_dataset)
                                else:
                                    ensure_dataset_db(new_dataset)
                            except Exception:
                                ensure_dataset_db(new_dataset)
                            proj_item = parent_item.parent()
                            proj = proj_item.text(0)
                            ws_name = parent_item.text(0)
                            PROJECT_CONFIG[proj]["workspaces"][ws_name]["threads"][new_file] = {
                                "path": new_path,
                                "dataset_file": new_dataset,
                                "isolated": False
                            }
                            save_project_config(PROJECT_CONFIG)
                            log_message(f"Thread cloned as {new_file}")
                            self.refresh_tree()
                            self.parent().load_thread(new_path)
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Clone thread failed: {e}")
                            log_message(f"Clone thread failed: {e}", level="error")
                elif action == action_delete:
                    reply = QMessageBox.question(
                        self, "Delete Thread",
                        f"Are you sure you want to delete thread '{item.text(0)}'?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            os.remove(data["path"])
                            parent_item = item.parent()
                            proj_item = parent_item.parent()
                            proj = proj_item.text(0)
                            ws_name = parent_item.text(0)
                            PROJECT_CONFIG[proj]["workspaces"][ws_name]["threads"].pop(item.text(0), None)
                            save_project_config(PROJECT_CONFIG)
                            log_message(f"Thread {item.text(0)} deleted.")
                            if self.parent().current_thread == data["path"]:
                                remaining = list(PROJECT_CONFIG[proj]["workspaces"][ws_name]["threads"].values())
                                if remaining:
                                    self.parent().load_thread(remaining[0])
                                else:
                                    self.parent().clear_chat_layout()
                        except Exception as e:
                            QMessageBox.warning(self, "Error", f"Delete thread failed: {e}")
                            log_message(f"Delete thread failed: {e}", level="error")
                        self.refresh_tree()
        else:
            if self.clipboard:
                menu.addAction("Paste")
                action = menu.exec(self.tree.viewport().mapToGlobal(position))
                if action == action_paste:
                    QMessageBox.information(self, "Paste", "Paste is only available on specific items.")
    def new_project(self):
        proj_name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        if ok and proj_name.strip():
            if "\n" in proj_name or re.search(r'[<>:"/\\|?*\#!]', proj_name):
                QMessageBox.warning(self, "Invalid Name", "Project name contains invalid characters or newlines.")
                return
            proj_path = os.path.join(PROJECTS_DIR, proj_name.strip())
            try:
                os.makedirs(proj_path, exist_ok=False)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"New project creation failed: {e}")
                log_message(f"New project creation failed: {e}", level="error")
                return
            PROJECT_CONFIG[proj_name.strip()] = {"path": proj_path, "workspaces": {}}
            save_project_config(PROJECT_CONFIG)
            log_message(f"New project created: {proj_name.strip()}")
            self.refresh_tree()
    def paste_project(self):
        if self.clipboard and self.clipboard.get("type") == "project":
            new_proj_name, ok = QInputDialog.getText(self, "Paste Project", "Enter new project name for paste:", text=self.clipboard["name"] + " Copy")
            if ok and new_proj_name.strip():
                if "\n" in new_proj_name or re.search(r'[<>:"/\\|?*\#!]', new_proj_name):
                    QMessageBox.warning(self, "Invalid Name", "Project name contains invalid characters or newlines.")
                    return
                dest = os.path.join(PROJECTS_DIR, new_proj_name.strip())
                try:
                    shutil.copytree(self.clipboard["path"], dest)
                    PROJECT_CONFIG[new_proj_name.strip()] = {"path": dest, "workspaces": {}}
                    save_project_config(PROJECT_CONFIG)
                    log_message(f"Project pasted as {new_proj_name.strip()}.")
                    self.refresh_tree()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Paste project failed: {e}")
                    log_message(f"Paste project failed: {e}", level="error")
            self.clipboard = None
        else:
            QMessageBox.warning(self, "Paste Error", "Clipboard does not contain a project.")
    def new_workspace(self):
        item = self.tree.currentItem()
        if item is None:
            QMessageBox.warning(self, "Select Project", "Please select a project to add a workspace.")
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get("type") == "project":
            proj_item = item
        elif data and data.get("type") == "workspace":
            proj_item = item.parent()
        else:
            QMessageBox.warning(self, "Select Project", "Please select a project to add a workspace.")
            return
        proj_path = proj_item.data(0, Qt.ItemDataRole.UserRole)["path"]
        default_ws_name = f"{proj_item.text(0)} Workspace"
        ws_name, ok = QInputDialog.getText(self, "New Workspace", "Enter workspace name:", text=default_ws_name)
        if ok and ws_name.strip():
            if "\n" in ws_name or re.search(r'[<>:"/\\|?*\#!]', ws_name):
                QMessageBox.warning(self, "Invalid Name", "Workspace name contains invalid characters or newlines.")
                return
            ws_path = os.path.join(proj_path, ws_name.strip())
            os.makedirs(ws_path, exist_ok=True)
            workspace_folder = os.path.join(ws_path, "workspace")
            os.makedirs(workspace_folder, exist_ok=True)
            conv_file = os.path.join(workspace_folder, f"{ws_name.strip()}.txt")
            if not os.path.exists(conv_file):
                with open(conv_file, "w", encoding="utf-8") as f:
                    f.write("")
            # create and register a dataset for this workspace.  Use
            # dataset_path_for to derive the location from the conversation file.
            dataset_file = dataset_path_for(conv_file)
            ensure_dataset_db(dataset_file)
            proj = proj_item.text(0)
            PROJECT_CONFIG[proj]["workspaces"][ws_name.strip()] = {
                "path": ws_path,
                "conv_file": conv_file,
                "dataset_file": dataset_file,
                "isolated": False,
                "threads": {}
            }
            save_project_config(PROJECT_CONFIG)
            log_message(f"New workspace created: {ws_name.strip()} in project {proj}")
            self.refresh_tree()
            self.parent().load_workspace(conv_file)

# -------------------- MAIN CHATBOT APPLICATION --------------------
class ChatbotApp(QWidget):
    """
    Main window for the Advanced Chatbot.
    Manages UI layout, state, TTS/STT, project/workspace/thread switching,
    and all user interactions.
    """
    def __init__(self):
        super().__init__()
        self._init_state()
        self._init_tts()
        self.initUI()

    def _init_state(self) -> None:
        """Initialize all mutable application state."""
        self.chat_layout: QVBoxLayout | None = None
        self.last_user_text: str = ""
        self.switch_in_progress: bool = False
        self.speech_worker: SpeechWorker | None = None
        self.current_tts_process = None
        self.current_workspace_file: str = ""
        self.current_thread: str | None = None
        self.openai_models: list[str] = AVAILABLE_MODELS.copy()
        self.ollama_models: list[str] = []

    def _init_tts(self) -> None:
        """Load TTS settings from disk and initialize the queue manager."""
        settings = load_tts_settings()
        voice = settings.get("voice", "Zira")
        speed = settings.get("speed", 1.2)
        self.tts_manager = TTSManager(voice_name=voice, speed=speed)

    def initUI(self) -> None:
        """Build and configure the entire UI."""
        # --- Window basics ---
        self.setWindowTitle("Advanced Chatbot")
        self.resize(1200, 700)
        self.setMinimumSize(800, 600)
        # Dark base theme for main widgets
        self.setStyleSheet("background-color: #2A2A2A; QLineEdit { color: white; }")

        # --- Top-level layout ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        # 1) Project/Workspace/Thread manager on left
        self.project_manager = ProjectManager(self)
        self.project_manager.threadSelected.connect(self.load_thread)
        self.project_manager.workspaceSelected.connect(self.load_workspace)
        self.project_manager.projectSelected.connect(self.project_selected)
        main_layout.addWidget(self.project_manager)

        # 2) Right side: controls + chat area
        right_vbox = QVBoxLayout()
        right_vbox.setContentsMargins(0, 0, 0, 0)
        right_vbox.setSpacing(2)
        main_layout.addLayout(right_vbox)

        # --- Top control bar ---
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(2)
        self._populate_top_bar(top_bar)
        right_vbox.addLayout(top_bar)

        # --- Chat scroll area ---
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #808080; border: 2px solid #008080;")
        right_vbox.addWidget(self.scroll_area)

        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: #808080;")
        self.chat_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(2, 2, 2, 2)
        self.chat_layout.setSpacing(5)
        self.scroll_area.setWidget(self.chat_container)

        # --- User input area ---
        self.user_input = QPlainTextEdit(self)
        self.user_input.setPlaceholderText("Type your message here…")
        self.user_input.setStyleSheet("color: #D3D3D3;")
        self.user_input.setFixedHeight(100)
        right_vbox.addWidget(self.user_input)

        send_row = QHBoxLayout()
        self.revise_button = QPushButton("Revise Message", self)
        self.revise_button.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.revise_button.clicked.connect(self.revise_message)
        send_row.addWidget(self.revise_button)

        self.send_button = QPushButton("Send", self)
        self.send_button.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        self.send_button.clicked.connect(self.send_message)
        send_row.addWidget(self.send_button)

        send_row.addStretch()
        right_vbox.addLayout(send_row)

        # --- Hidden console log (optional) ---
        self.console_widget = QPlainTextEdit(self)
        self.console_widget.setReadOnly(True)
        self.console_widget.setStyleSheet("background-color: black; color: yellow; font-family: monospace;")
        self.console_widget.setFixedHeight(150)
        self.console_widget.hide()
        right_vbox.addWidget(self.console_widget)
        self._log = self.console_widget

    def _populate_top_bar(self, layout: QHBoxLayout) -> None:
        """Create all the controls in the top bar (provider, model, TTS/STT, etc.)."""
        def make_label(text: str) -> QLabel:
            lbl = QLabel(text, self)
            lbl.setStyleSheet("color: #FFFFFF; font-weight: bold;")
            return lbl

        # Provider selector
        layout.addWidget(make_label("Provider:"))
        self.provider_selector = QComboBox(self)
        self.provider_selector.setStyleSheet("color: white;")
        self.provider_selector.addItems(["OpenAI", "Ollama"])
        self.provider_selector.setCurrentText(GLOBAL_CONFIG.get("provider", "OpenAI"))
        self.provider_selector.currentTextChanged.connect(self.update_provider)
        layout.addWidget(self.provider_selector)

        # Model selector
        layout.addWidget(make_label("Model:"))
        self.model_selector = QComboBox(self)
        self.model_selector.setStyleSheet(
            "QComboBox {background-color: #000; color: #FFF; border:1px solid #CCC; padding:2px 6px;} "
            "QComboBox QAbstractItemView {background-color: #000; color: #FFF;}"
        )
        self._refresh_model_list()
        layout.addWidget(self.model_selector)

        # Mic selector
        layout.addWidget(make_label("Mic:"))
        self.mic_selector = QComboBox(self)
        self.mic_selector.setStyleSheet("color: white;")
        try:
            mics = sr.Microphone.list_microphone_names()
        except Exception:
            mics = ["Default Mic"]
        self.mic_selector.addItems(mics)
        self.mic_selector.setCurrentText(GLOBAL_CONFIG.get("mic_device", mics[0]))
        self.mic_selector.currentTextChanged.connect(self.update_mic)
        layout.addWidget(self.mic_selector)

        # Chat / Global prompt controls
        for text, slot in (
            ("Chat Prompt Control", self.open_chat_prompt_control),
            ("Global Prompt Control", self.open_global_prompt_control)
        ):
            btn = QPushButton(text, self)
            btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        # Semantic awareness toggle
        self.semantic_checkbox = QCheckBox("Semantic Awareness", self)
        self.semantic_checkbox.setStyleSheet("color: #FFFFFF;")
        self.semantic_checkbox.stateChanged.connect(self.toggle_semantic_awareness)
        self.semantic_checkbox.setEnabled(False)
        layout.addWidget(self.semantic_checkbox)

        # View logs button
        log_btn = QPushButton("View Logs", self)
        log_btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        log_btn.clicked.connect(self.open_log_window)
        layout.addWidget(log_btn)

        # Plugins launcher
        plugin_btn = QPushButton("Plugins", self)
        plugin_btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        plugin_btn.clicked.connect(self._toggle_plugins_dock)
        layout.addWidget(plugin_btn)

        # STT controls
        start_btn = QPushButton("Start Listening", self)
        start_btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        start_btn.clicked.connect(self.start_listening)
        layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop Listening", self)
        stop_btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        stop_btn.clicked.connect(self.stop_listening)
        layout.addWidget(stop_btn)

        # TTS controls
        play_btn = QPushButton("Play TTS", self)
        play_btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        play_btn.clicked.connect(lambda: self.tts_manager.resume())
        layout.addWidget(play_btn)

        stop_tts_btn = QPushButton("Stop TTS", self)
        stop_tts_btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        stop_tts_btn.clicked.connect(lambda: self.tts_manager.stop())
        layout.addWidget(stop_tts_btn)

        # Copy / Export conversation
        for text, slot in (
            ("📋 Copy Conversation", self.copy_conversation),
            ("📤 Export Conversation", self.export_conversation)
        ):
            btn = QPushButton(text, self)
            btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        # History slider
        layout.addWidget(make_label("History:"))
        self.history_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.history_slider.setRange(0, 101)
        self.history_slider.setTickInterval(1)
        self.history_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.history_slider.setValue(20)
        self.history_slider.valueChanged.connect(self.update_history_label)
        layout.addWidget(self.history_slider)

        self.history_label_display = QLabel("NONE", self)
        self.history_label_display.setStyleSheet("color: #FFFFFF; font-weight: bold;")
        layout.addWidget(self.history_label_display)

        layout.addStretch()
        
    def _toggle_plugins_dock(self) -> None:
        """Toggles visibility of the Plugins dock widget."""
        dock = self.plugins_dock
        dock.setVisible(not dock.isVisible())
        
        
    def open_plugins_dialog(self):
        """Open a simple popup showing all installed plugins with launch buttons."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Installed Plugins")
        dlg.setStyleSheet("background-color: #2A2A2A; color: white;")
        layout = QVBoxLayout(dlg)

        # If you have a plugin manager or list, plug it in here:
        if hasattr(self, "plugin_manager") and self.plugin_manager:
            for plugin in self.plugin_manager.get_all():
                row = QHBoxLayout()
                label = QLabel(plugin.name)
                label.setStyleSheet("color: white;")
                row.addWidget(label)

                launch_btn = QPushButton("Launch")
                launch_btn.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
                launch_btn.clicked.connect(lambda _, p=plugin: p.launch_ui())
                row.addWidget(launch_btn)

                layout.addLayout(row)
        else:
            layout.addWidget(QLabel("No plugins found."))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.setLayout(layout)
        dlg.exec()
        

    def _refresh_model_list(self) -> None:
        """Populate the model_selector with the current provider's models."""
        self.model_selector.clear()

        if GLOBAL_CONFIG.get("provider", "OpenAI") == "Ollama":
            self.ollama_models = discover_ollama_models()
            self.model_selector.addItems(self.ollama_models)
        else:
            try:
                resp = openai_client.models.list()
                self.openai_models = [m.id for m in resp.data] or AVAILABLE_MODELS
            except Exception:
                self.openai_models = AVAILABLE_MODELS
            self.model_selector.addItems(self.openai_models)

            default = GLOBAL_CONFIG.get("default_model", "gpt-4o-mini")
            idx = self.model_selector.findText(default)
            if idx >= 0:
                self.model_selector.setCurrentIndex(idx)


            # ---------- isolation helper ----------
    def _scope_is_isolated(self) -> bool:
        """Returns True if the *current* workspace or thread is flagged isolated."""
        if self.current_thread_name:          # thread view
            return bool(PROJECT_CONFIG
                        .get(self.current_project_name, {})
                        .get("workspaces", {})
                        .get(self.current_workspace_name, {})
                        .get("threads", {})
                        .get(self.current_thread_name, {})
                        .get("isolated", False))
        else:                                 # workspace view
            return bool(PROJECT_CONFIG
                        .get(self.current_project_name, {})
                        .get("workspaces", {})
                        .get(self.current_workspace_name, {})
                        .get("isolated", False))

    def update_history_label(self, value):
        if value == 0:
            self.history_label_display.setText("NONE")
        elif value == 101:
            self.history_label_display.setText("ALL")
        else:
            self.history_label_display.setText(str(value))
    def update_provider(self, provider: str) -> None:
        """Switch LLM provider (OpenAI or Ollama) and reload model list."""
        GLOBAL_CONFIG["provider"] = provider
        save_global_config(GLOBAL_CONFIG)
        log_message(f"Provider updated to {provider}")

        self.model_selector.clear()

        if provider == "Ollama":
            self.ollama_models = discover_ollama_models()

            if self.ollama_models:
                self.model_selector.addItems(self.ollama_models)
                self.model_selector.setCurrentIndex(0)
                log_message(f"Discovered {len(self.ollama_models)} Ollama model(s).")
            else:
                self.model_selector.addItem("⚠ No Ollama models found")
                log_message("No Ollama models found via `ollama list`", level="WARNING")

        else:
            try:
                response = openai_client.models.list()
                openai_models = [m.id for m in response.data]
                self.openai_models = openai_models if openai_models else AVAILABLE_MODELS
            except Exception as e:
                log_message(f"Error listing OpenAI models: {e}", level="ERROR")
                self.openai_models = AVAILABLE_MODELS

            self.model_selector.addItems(self.openai_models)

            default_model = GLOBAL_CONFIG.get("default_model", "gpt-4o-mini")
            default_index = self.model_selector.findText(default_model)
            if default_index >= 0:
                self.model_selector.setCurrentIndex(default_index)
            else:
                self.model_selector.setCurrentIndex(0)
                log_message(f"Default model '{default_model}' not found; using fallback.")



    def update_mic(self, mic):
        GLOBAL_CONFIG["mic_device"] = mic
        save_global_config(GLOBAL_CONFIG)
        log_message(f"Mic updated to {mic}")

    def project_selected(self, proj_path: str) -> None:
        """
        Called when a project item is selected in the tree.  This
        method records the current project name and updates the
        semantic awareness checkbox to reflect the project's state.

        Parameters
        ----------
        proj_path : str
            Filesystem path of the selected project.
        """
        # Determine project name from the path
        proj_name = os.path.basename(proj_path)
        self.current_project_name = proj_name
        # Reset workspace/thread context when selecting only a project
        self.current_workspace_name = ""
        self.current_thread_name = ""
        self.current_dataset_file = None
        # Look up semantic awareness flag
        sem_flag = False
        if proj_name in PROJECT_CONFIG:
            sem_flag = bool(PROJECT_CONFIG[proj_name].get("semantic_aware", False))
        # Enable the checkbox and set its state without emitting
        self.semantic_checkbox.blockSignals(True)
        self.semantic_checkbox.setEnabled(True)
        self.semantic_checkbox.setCheckState(CHECKED if sem_flag else Qt.CheckState.Unchecked)
        self.semantic_checkbox.blockSignals(False)

    def toggle_semantic_awareness(self, state: int) -> None:
        """
        Toggle the semantic awareness flag for the currently selected
        project.  This method updates PROJECT_CONFIG and persists the
        change.  If no project is selected, it has no effect.

        Parameters
        ----------
        state : int
            The new check state (checked or unchecked).
        """
        proj_name = getattr(self, "current_project_name", "") or ""
        if not proj_name:
            return
        new_flag = (state == CHECKED)
        # Update config and save
        if proj_name in PROJECT_CONFIG:
            PROJECT_CONFIG[proj_name]["semantic_aware"] = new_flag
            save_project_config(PROJECT_CONFIG)
            log_message(f"Semantic awareness for project {proj_name} set to {new_flag}")
            # Update corresponding tree item check state via ProjectManager
            # Find project item and set check state to reflect the change
            for i in range(self.project_manager.tree.topLevelItemCount()):
                item = self.project_manager.tree.topLevelItem(i)
                if item.text(0) == proj_name:
                    item.setCheckState(0, CHECKED if new_flag else Qt.CheckState.Unchecked)
                    break
    def clear_chat_layout(self):
        while self.chat_layout.count():
            w = self.chat_layout.takeAt(0).widget()
            if w:
                w.deleteLater()
    def toggle_console(self, state):
        if state == CHECKED:
            self.console_widget.show()
            log_message("Console toggled on")
        else:
            self.console_widget.hide()
            log_message("Console toggled off")

    def open_log_window(self):
        """
        Display a modal window that streams live logs.  The window shows
        existing log content on open and appends new log lines in real
        time via the global LOG_SUBSCRIBERS mechanism.  Includes a copy
        button to copy the entire log to the clipboard.  When closed,
        the window unregisters its callback.
        """
        dlg = QDialog(self)
        dlg.setWindowTitle("Application Logs")
        dlg.setMinimumSize(600, 400)
        layout = QVBoxLayout(dlg)
        log_view = QPlainTextEdit(dlg)
        log_view.setReadOnly(True)
        log_view.setStyleSheet("background-color: #000; color: #00FF00; font-family: Consolas, monospace;")
        # Load current log file contents
        try:
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                log_view.setPlainText(f.read())
        except Exception:
            log_view.setPlainText("")
        layout.addWidget(log_view)
        btn_copy = QPushButton("Copy to Clipboard", dlg)
        btn_copy.setStyleSheet(BABY_BLUE_BUTTON_STYLE)
        btn_copy.clicked.connect(lambda: pyperclip.copy(log_view.toPlainText()))
        layout.addWidget(btn_copy)
        # Define a callback to append new log lines
        def append_log(line: str, level: str):
            # Append the line to the text area; ensure executed on GUI thread
            log_view.appendPlainText(line.rstrip("\n"))
        # Register callback
        LOG_SUBSCRIBERS.append(append_log)
        # Remove callback when dialog closes
        def on_close():
            try:
                LOG_SUBSCRIBERS.remove(append_log)
            except ValueError:
                pass
        dlg.finished.connect(on_close)
        dlg.exec()
    def open_chat_prompt_control(self):
        if not self.current_workspace_file:
            QMessageBox.warning(self, "No Workspace Selected", "Please select a workspace first.")
            return
        workspace_dir = os.path.dirname(os.path.dirname(self.current_workspace_file))
        dlg = ChatPromptControlDialog(workspace_dir, self)
        dlg.exec()
        log_message("Chat Prompt Control dialog closed.")
    def open_global_prompt_control(self):
        dlg = GlobalPromptControlDialog(self)
        dlg.exec()
        log_message("Global Prompt Control dialog closed.")
    def start_listening(self):
        if self.speech_worker is None:
            self.speech_worker = SpeechWorker(device_index=0)
            self.speech_worker.textRecognized.connect(self.append_recognized_text)
            self.speech_worker.start()
            log_message("Speech recognition started.")
    def stop_listening(self):
        if self.speech_worker:
            self.speech_worker.stop()
            self.speech_worker = None
            log_message("Speech recognition stopped.")
    def append_recognized_text(self, text):
        current = self.user_input.toPlainText()
        self.user_input.setPlainText(current + " " + text)
        log_message(f"Speech recognized: {text}")
    def read_last_response(self):
        """
        Plays the most recent GPT response using the TTSManager.
        Clears the existing TTS queue, starts from scratch, and plays only the latest.
        """
        last_gpt = None
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if isinstance(widget, GPTMessageWidget):
                last_gpt = widget.gpt_text
                break
        if not last_gpt:
            QMessageBox.information(self, "TTS", "No assistant response found.")
            return

        # Stop any ongoing playback and clear the queue
        self.tts_manager.stop()
        with self.tts_manager._lock:
            self.tts_manager.queue.clear()
            self.tts_manager.index = 0
        self.tts_manager.add_message(last_gpt)

    def send_message(self):
        user_text = self.user_input.toPlainText().strip()
        if not user_text:
            return
        self.user_input.clear()
        self.add_user_message(user_text)

        # Before constructing prompts, ensure that a dataset file exists for the
        # current conversation scope.  If this is a brand new chat (no
        # workspace or thread loaded), derive a dataset path from the active
        # conversation file (workspace or thread) or fall back to the global
        # conversation file.  Isolation does not prevent writing to the
        # dataset.
        if not getattr(self, "current_dataset_file", None):
            # Determine the source of the conversation: thread > workspace > fallback
            if self.current_thread:
                conv_path = self.current_thread
            elif self.current_workspace_file:
                conv_path = self.current_workspace_file
            else:
                conv_path = CONVO_FILE
            self.current_dataset_file = dataset_path_for(conv_path)
        # ensure the dataset exists on disk
        ensure_dataset_db(self.current_dataset_file)

        # ----- Prompt Assembly -----
        active_prompts = []
        if self.current_workspace_file:
            workspace_dir = os.path.dirname(os.path.dirname(self.current_workspace_file))
            active_prompts = ChatPromptControlDialog.get_active_prompts(workspace_dir)

        global_prompts = []
        disable_global = False
        if self.current_workspace_file:
            workspace_dir = os.path.dirname(os.path.dirname(self.current_workspace_file))
            config_file = os.path.join(workspace_dir, "settings_config.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        ws_config = json.load(f)
                        disable_global = ws_config.get("disable_global_prompts", False)
                except Exception:
                    disable_global = False

        if not disable_global:
            global_prompts = [p for p in get_global_prompts() if p["enabled"]]

        # ----- History Assembly -----
        pairs = []
        if self.current_workspace_file:
            pairs = parse_conversation_file(self.current_workspace_file)

        slider_val = self.history_slider.value()
        if slider_val == 0:
            history_text = ""
        elif slider_val == 101:
            history_text = "\n".join([
                f"User: {p[0]}\n{p[2]} ({p[3] if p[3] else self.model_selector.currentText()}): {p[1]}"
                for p in pairs
            ])
        else:
            selected = pairs[-slider_val:]
            history_text = "\n".join([
                f"User: {p[0]}\n{p[2]} ({p[3] if p[3] else self.model_selector.currentText()}): {p[1]}"
                for p in selected
            ])

        full_prompt = ""

        # ----- Semantic Query (contextual recall) -----
        context_entries = []
        # Always attempt to include relevant semantic context from the current
        # dataset.  Isolation determines only whether other scopes are
        # included, not the current scope.  If a dataset hasn't been
        # initialized for this conversation yet, one will be created
        # lazily when saving below.
        if getattr(self, "current_dataset_file", None):
            try:
                context_entries = query_semantic_context(
                    user_text,
                    self.current_dataset_file,
                    getattr(self, "current_project_name", "") or "",
                    getattr(self, "current_workspace_name", "") or "",
                    getattr(self, "current_thread_name", "") or "",
                    limit=3
                )
            except Exception as e:
                log_message(f"Semantic query failed: {e}")
        context_text = ""
        if context_entries:
            for idx, entry in enumerate(context_entries):
                u = entry.get("user", "").strip()
                a = entry.get("assistant", "").strip()
                context_text += f"[Context {idx+1}]\nUser: {u}\nAssistant: {a}\n\n"
        # Begin assembling the full prompt: include context first
        full_prompt = context_text
        if global_prompts:
            full_prompt += "\n".join([p["text"] for p in global_prompts]) + "\n"
        if active_prompts:
            full_prompt += "\n".join(active_prompts) + "\n"
        if history_text:
            full_prompt += history_text + "\n"
        full_prompt += user_text
        model_name = self.model_selector.currentText()
        provider = GLOBAL_CONFIG["provider"]
        truncated_prompt = truncate_conversation(full_prompt, model_name, provider)
        log_message(f"Sending message with {len(active_prompts)} workspace prompts, {len(global_prompts)} global prompts, slider {slider_val}.", "info")
        try:
            if provider == "Ollama":
                payload = {"model": model_name, "messages": [{"role": "user", "content": truncated_prompt}], "stream": False}
                resp = requests.post("http://localhost:11434/api/chat", json=payload).json()
                try:
                    gpt_text = resp["message"]["content"]
                except KeyError:
                    gpt_text = resp.get("response", f"Unexpected response structure: {resp}")
                log_message("Received response from Ollama.")
            else:
                resp = openai_client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": truncated_prompt}])
                gpt_text = resp.choices[0].message.content
                log_message("Received response from OpenAI.")
        except Exception as e:
            gpt_text = f"Error: {str(e)}"
            log_message(f"Error during send_message: {e}", level="error")
        # Pass provider to add_gpt_message so that the response header preserves the original value.
        self.add_gpt_message(user_text, gpt_text, model_name, provider)
        self.scroll_to_bottom()
        # Enqueue the assistant response for TTS playback
        try:
            self.tts_manager.add_message(gpt_text)
        except Exception:
            pass
        # Persist conversation to flat conversation file
        conv_file = self.current_workspace_file if self.current_workspace_file else os.path.join(SIMPLE_CHAT_DIR, "conversation.txt")
        os.makedirs(os.path.dirname(conv_file), exist_ok=True)
        try:
            with open(conv_file, "a", encoding="utf-8") as f:
                f.write(f"User: {user_text}\n{provider} ({model_name}): {gpt_text}\n{'-' * 40}\n")
        except Exception as e:
            log_message(f"Error writing to conversation file: {e}", level="error")
        # Persist interaction into the SQLite dataset for the current scope
        try:
            if getattr(self, "current_dataset_file", None):
                add_to_dataset(self.current_dataset_file, user_text, gpt_text, truncated_prompt, provider, model_name)
        except Exception as e:
            log_message(f"Error adding entry to dataset: {e}", level="error")
    def revise_message(self):
        user_text = self.user_input.toPlainText().strip()
        if not user_text:
            return
        fixed_prompt = "Rewrite this better with more detail and forget nothing. Do not write code unless asked:"
        prompt = f"{fixed_prompt}\n\n{user_text}"
        log_message("Revising message.")
        try:
            response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            revised_text = response.choices[0].message.content
            log_message("Received revised message.")
        except Exception as e:
            revised_text = f"Error: {str(e)}"
            log_message(f"Error during revise_message: {e}", level="error")
        self.user_input.setPlainText(revised_text)
    def add_user_message(self, user_text):
        widget = UserMessageWidget(user_text, self)
        self.chat_layout.addWidget(widget)
    # UPDATED: Now add_gpt_message accepts an extra parameter "provider".
    def add_gpt_message(self, user_text, gpt_text, model_name, provider):
        widget = GPTMessageWidget(user_text, gpt_text, model_name, provider, self)
        self.chat_layout.addWidget(widget)
    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
    def copy_conversation(self):
        conversation = ""
        for i in range(self.chat_layout.count()):
            w = self.chat_layout.itemAt(i).widget()
            if isinstance(w, UserMessageWidget):
                conversation += f"User: {w.user_text}\n\n"
            elif isinstance(w, GPTMessageWidget):
                conversation += f"{w.provider} ({w.model_name}): {w.gpt_text}\n\n"
        pyperclip.copy(conversation)
        log_message("Conversation copied to clipboard.")
    def export_conversation(self):
        formats = ["PDF", "txt", "JSON", "CSV", "MD", ".py"]
        fmt, ok = QInputDialog.getItem(self, "Select Export Format", "Choose export format:", formats, editable=False)
        if not ok:
            return
        conversation = ""
        for i in range(self.chat_layout.count()):
            w = self.chat_layout.itemAt(i).widget()
            if isinstance(w, UserMessageWidget):
                conversation += f"User: {w.user_text}\n"
            elif isinstance(w, GPTMessageWidget):
                conversation += f"{w.provider} ({w.model_name}): {w.gpt_text}\n"
            conversation += "\n"
        options = QFileDialog.Options()
        file_filter = f"*.{fmt.lower()}"
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Conversation", "", f"Files ({file_filter})", options=options)
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(conversation)
                QMessageBox.information(self, "Export Successful", f"Conversation exported as {file_path}")
                log_message(f"Conversation exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Failed to export conversation:\n{str(e)}")
                log_message(f"Error exporting conversation: {e}", level="error")
    def handle_edited_message(self, user_widget, new_text):
        layout = self.chat_layout
        idx = None
        for i in range(layout.count()):
            if layout.itemAt(i).widget() is user_widget:
                idx = i
                break
        if idx is None:
            return
        while layout.count() > idx + 1:
            item = layout.takeAt(idx + 1)
            w = item.widget()
            if w:
                w.deleteLater()
        conv_file = self.current_workspace_file if self.current_workspace_file else os.path.join(SIMPLE_CHAT_DIR, "conversation.txt")
        conversation_so_far = ""
        for i in range(idx):
            w = layout.itemAt(i).widget()
            if isinstance(w, UserMessageWidget):
                conversation_so_far += f"User: {w.user_text}\n"
            elif isinstance(w, GPTMessageWidget):
                conversation_so_far += f"{w.provider} ({w.model_name}): {w.gpt_text}\n"
            conversation_so_far += "-" * 40 + "\n"
        conversation_so_far += f"User: {new_text}\n"
        user_widget.user_text = new_text
        user_widget.user_label.setText(f"<b>User:</b> {new_text}")
        if hasattr(user_widget, "edit_text_edit"):
            user_widget.edit_text_edit.deleteLater()
        if hasattr(user_widget, "confirm_button"):
            user_widget.confirm_button.deleteLater()
        if hasattr(user_widget, "cancel_button"):
            user_widget.cancel_button.deleteLater()
        user_widget.user_label.show()
        user_widget.edit_button.show()
        model_name = self.model_selector.currentText()
        provider = GLOBAL_CONFIG["provider"]
        try:
            if provider == "Ollama":
                payload = {"model": model_name, "messages": [{"role": "user", "content": new_text}], "stream": False}
                resp = requests.post("http://localhost:11434/api/chat", json=payload).json()
                try:
                    new_response = resp["message"]["content"]
                except KeyError:
                    new_response = resp.get("response", f"Unexpected response structure: {resp}")
            else:
                response = openai_client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": new_text}])
                new_response = response.choices[0].message.content
        except Exception as e:
            new_response = f"Error: {str(e)}"
            log_message(f"Error during resend of edited message: {e}", level="error")
        gpt_widget = GPTMessageWidget(new_text, new_response, model_name, provider, self)
        layout.addWidget(gpt_widget)
        conversation_so_far += f"{provider} ({model_name}): {new_response}\n{'-' * 40}\n"
        try:
            with open(conv_file, "w", encoding="utf-8") as f:
                f.write(conversation_so_far)
            log_message("Conversation file updated after edit with new response.")
        except Exception as e:
            log_message(f"Error updating conversation file after edit: {e}", level="error")
        # Save the edited interaction into the dataset for semantic recall
        try:
            if getattr(self, "current_dataset_file", None):
                # Use the edited text as the prompt for embedding; note that
                # this simplified save does not include historical context.
                add_to_dataset(self.current_dataset_file, new_text, new_response, new_text, provider, model_name)
        except Exception as e:
            log_message(f"Error adding edited entry to dataset: {e}", level="error")
    def load_workspace(self, conv_file):
        self.clear_chat_layout()
        self.current_thread = None
        if not os.path.exists(conv_file) or os.path.isdir(conv_file):
            workspace_dir = os.path.dirname(conv_file)
            ws_folder = os.path.basename(os.path.dirname(workspace_dir))
            conv_file = os.path.join(workspace_dir, f"{ws_folder}.txt")
            os.makedirs(workspace_dir, exist_ok=True)
            if not os.path.exists(conv_file):
                with open(conv_file, "w", encoding="utf-8") as f:
                    f.write("")
            log_message("Recalculated workspace conversation file path during load.")
        self.current_workspace_file = conv_file
        # Determine and record the current project/workspace dataset context
        # Reset scope variables
        self.current_project_name = ""
        self.current_workspace_name = ""
        self.current_thread_name = ""
        self.current_dataset_file = None
        # Find dataset file for this workspace in PROJECT_CONFIG
        for proj_name, proj_cfg in PROJECT_CONFIG.items():
            for ws_name, ws_cfg in proj_cfg.get("workspaces", {}).items():
                if ws_cfg.get("conv_file") == conv_file:
                    self.current_project_name = proj_name
                    self.current_workspace_name = ws_name
                    self.current_thread_name = ""
                    # fetch dataset_file from config; if missing, derive from conv_file
                    ds = ws_cfg.get("dataset_file")
                    if not ds:
                        ds = dataset_path_for(conv_file)
                    self.current_dataset_file = ds
                    break
            if self.current_project_name:
                break
        # Populate chat layout from the conversation file
        pairs = parse_conversation_file(conv_file)
        for (u_text, g_text, provider, model_name) in pairs:
            if not model_name:
                model_name = self.model_selector.currentText()
            self.add_user_message(u_text)
            self.add_gpt_message(u_text, g_text, model_name, provider if provider else GLOBAL_CONFIG["provider"])
        log_message("Workspace conversation loaded.")
        # Update semantic awareness checkbox based on current project
        proj_name = getattr(self, "current_project_name", "") or ""
        if proj_name:
            sem_flag = bool(PROJECT_CONFIG.get(proj_name, {}).get("semantic_aware", False))
            self.semantic_checkbox.blockSignals(True)
            self.semantic_checkbox.setEnabled(True)
            self.semantic_checkbox.setCheckState(CHECKED if sem_flag else Qt.CheckState.Unchecked)
            self.semantic_checkbox.blockSignals(False)
    def load_thread(self, thread_file):
        self.clear_chat_layout()
        self.current_thread = thread_file
        os.makedirs(os.path.dirname(thread_file), exist_ok=True)
        if not os.path.exists(thread_file) or not os.path.isfile(thread_file):
            with open(thread_file, "w", encoding="utf-8") as f:
                f.write("")
            log_message(f"Created missing thread file: {thread_file}")
        pairs = parse_conversation_file(thread_file)
        for (u_text, g_text, provider, model_name) in pairs:
            if not model_name:
                model_name = self.model_selector.currentText()
            self.add_user_message(u_text)
            self.add_gpt_message(u_text, g_text, model_name, provider if provider else GLOBAL_CONFIG["provider"])
        # Determine and record current project/workspace/thread dataset context
        self.current_project_name = ""
        self.current_workspace_name = ""
        self.current_thread_name = os.path.basename(thread_file)
        self.current_dataset_file = None
        # Find dataset file for this thread in PROJECT_CONFIG
        for proj_name, proj_cfg in PROJECT_CONFIG.items():
            for ws_name, ws_cfg in proj_cfg.get("workspaces", {}).items():
                for th_name, th_cfg in ws_cfg.get("threads", {}).items():
                    if th_cfg.get("path") == thread_file:
                        self.current_project_name = proj_name
                        self.current_workspace_name = ws_name
                        self.current_thread_name = th_name
                        # fetch dataset_file from config; fallback to dataset_path_for if missing
                        ds = th_cfg.get("dataset_file")
                        if not ds:
                            ds = dataset_path_for(thread_file)
                        self.current_dataset_file = ds
                        break
                if self.current_dataset_file:
                    break
            if self.current_dataset_file:
                break
        log_message("Thread conversation loaded.")
        # Update semantic awareness checkbox based on current project
        proj_name = getattr(self, "current_project_name", "") or ""
        if proj_name:
            sem_flag = bool(PROJECT_CONFIG.get(proj_name, {}).get("semantic_aware", False))
            self.semantic_checkbox.blockSignals(True)
            self.semantic_checkbox.setEnabled(True)
            self.semantic_checkbox.setCheckState(CHECKED if sem_flag else Qt.CheckState.Unchecked)
            self.semantic_checkbox.blockSignals(False)
    def closeEvent(self, event):
        save_global_config(GLOBAL_CONFIG)
        log_message("Application closed.")
        event.accept()

# -------------------- SPEECH RECOGNITION WORKER --------------------
class SpeechWorker(QThread):
    textRecognized = pyqtSignal(str)

    def __init__(self, device_index=None, parent=None):
        super().__init__(parent)
        self.device_index = device_index
        self._running = True
        self.recognizer = sr.Recognizer()
        self.last_spoken_time = None

    def run(self):
        try:
            mic = sr.Microphone(device_index=self.device_index)
        except Exception as e:
            self.textRecognized.emit(f"Error initializing microphone: {e}")
            return
        with mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self._running:
                try:
                    audio = self.recognizer.listen(source, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio)
                    now = time.time()
                    if self.last_spoken_time is not None:
                        pause = now - self.last_spoken_time
                        if pause >= 6:
                            text = ". " + text
                        elif pause >= 4:
                            text = ", " + text
                    self.last_spoken_time = now
                    self.textRecognized.emit(text)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    self.textRecognized.emit(f"Speech Recognition Error: {e}")
                    break

    def stop(self):
        self._running = False
        self.quit()
        self.wait()

# -------------------- MAIN --------------------
if __name__ == "__main__":
    try:
        # Optional startup utilities
        def clear_pycache_dirs(path):
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    if d == "__pycache__":
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)

        def compare_and_generate_pdd_all():
            log_message("compare_and_generate_pdd_all placeholder called.")

        def run_startup_analysis():
            log_message("run_startup_analysis placeholder called.")

        class StartupLogViewerDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Startup Logs")
                layout = QVBoxLayout(self)
                self.text_area = QPlainTextEdit(self)
                self.text_area.setReadOnly(True)
                self.text_area.setPlainText("Startup complete. Logs initialized.")
                layout.addWidget(self.text_area)
                btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
                btns.accepted.connect(self.accept)
                layout.addWidget(btns)

        # Run
        clear_pycache_dirs(BASE_DIR)
        compare_and_generate_pdd_all()
        run_startup_analysis()
        app = QApplication(sys.argv)
        # Ensure input fields in dialogs use white foreground on dark backgrounds
        # This global stylesheet applies to QLineEdit and QLabel within dialogs
        current_style = app.styleSheet() or ""
        # Apply a dark theme override for input fields.  Ensure text is
        # readable by forcing white foreground colors on line edits and
        # plain text edits.  Labels are also forced to white to avoid
        # dark-on-dark issues in dialogs.  These rules are appended to
        # whatever style the application might already have.
        app.setStyleSheet(
            current_style
            + "\nQLineEdit { color: white; }"
            + "\nQPlainTextEdit { color: white; }"
            + "\nQLabel { color: white; }"
        )
        startup_dialog = StartupLogViewerDialog()
        startup_dialog.exec()
        main_window = ChatbotApp()  # <- FIXED: was 'MainWindow()'
        main_window.show()
        log_message("MainWindow displayed.")
        sys.exit(app.exec())
    except Exception as e:
        log_message(f"Error in main: {e}", level="error")
        traceback.print_exc()
        sys.exit(1)

# -------------------- ACA Tab Integration --------------------
def get_tab_widget():
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    return ChatbotApp()
```

Advanced_Chatbot.py – Advanced Chatbot Application

This script implements an integrated chatbot that supports:
 • A unified Project, Workspace, and Thread management system (with right‐click actions for rename, fork, clone, and delete)
 • Conversation history with active prompts and token‐based truncation
 • Two LLM providers – OpenAI and Ollama – with dynamic model fetching;
   the default is OpenAI using model gpt-4o-mini (providers are mutually exclusive)
 • Speech-to-text (STT) using SpeechRecognition and text-to-speech (TTS) using pyttsx3
 • Syntax highlighting for Python code blocks in chat responses
 • Comprehensive logging (console widget and log file)

All configuration (including API keys and conversation logs) is stored in shared folders under a central BASE_DIR.
**Classes:** TTSManager, PythonHighlighter, ModelSelectionDialog, NewPromptDialog, ChatPromptControlDialog, GlobalPromptControlDialog, CodeBlockWidget, UserMessageWidget, GPTMessageWidget, ProjectManager, ChatbotApp, SpeechWorker
**Functions:** discover_ollama_models(), load_global_prompts_config(), save_global_prompts_config(cfg), sanitize_filename(name), get_global_prompts(), is_tts_running(), ensure_tts_running(), log_message(message, level), load_api_key(), save_global_config(cfg), load_global_config(), load_project_config(), save_project_config(cfg), parse_conversation_file(file_path), dataset_path_for(conv_path), ensure_dataset_db(db_file), compute_embedding(text), add_to_dataset(db_file, user_text, assistant_text, full_prompt, provider, model), text_similarity_tokens(emb1, emb2), _query_dataset_for_similarity(db_file, query_emb, limit), query_semantic_context(query_text, current_dataset_file, current_project_name, current_workspace_name, current_thread_name, limit), get_openai_max_tokens(model), get_ollama_max_tokens(model), count_tokens(text, model, provider), truncate_conversation(conversation_text, model, provider), ensure_ollama_connection(), load_tts_settings(), save_tts_settings(settings), get_voice_id(engine, voice_name), speak_text(text), stop_tts(), get_tab_widget()


## Module `Analyze_folders.py`

```python
import os

def analyze_folders(start_path):
    script_name = os.path.basename(__file__)  # Get script file name
    analyze_file = os.path.join(start_path, "analyze.txt")  # Output file path

    with open(analyze_file, "w", encoding="utf-8") as file:
        file.write(f"Folder Analysis Report\n")
        file.write(f"{'='*50}\n\n")
        file.write(f"Root Directory: {start_path}\n\n")
        
        for root, dirs, files in os.walk(start_path):
            # Skip directories named 'venv'
            if "venv" in root.split(os.sep):
                continue

            level = root.replace(start_path, "").count(os.sep)
            indent = "|   " * level  # Tree structure formatting
            file.write(f"{indent}|-- {os.path.basename(root)}/\n")

            # Filter out the script and output file from the list of files
            filtered_files = [f for f in files if f not in {script_name, "analyze.txt"}]

            # List files in the directory
            for f in filtered_files:
                file_indent = "|   " * (level + 1)
                file.write(f"{file_indent}|-- {f}\n")
    
    print(f"Analysis complete. Results saved in {analyze_file}")

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    analyze_folders(script_directory)
```

**Functions:** analyze_folders(start_path)



---
**Generation Parameters**


```text

You are an expert software engineer.  Carefully read every
file under the target directory (skipping any virtual environment
folders) and produce a comprehensive, well‑structured README in
Markdown.  Focus most of your attention on Python (.py) files: parse
their module‑level docstrings, enumerate classes and functions, and
describe what each does.  Summarise the purpose of non‑Python files
(such as JSON, YAML, text, images) briefly.  Provide an overview of
the project architecture and any dependencies you can infer from the
code.  Include usage notes or examples where appropriate.  Do not
invent information – base your summary solely on the source content.
Use headings, subheadings and lists to organise the README.

```