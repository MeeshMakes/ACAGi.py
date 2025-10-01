# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `Rant_PDD.py`

Rant_PDD.py — 2025 UI refresh with full workflow, Explorer, Dataset controls, safe resets, Sync & Summary features, versioned repository sync, and Package for GitHub.
🦈 SHARK_SENTINEL DeepSeek Progressive Script Integration + GitHub Enhancements
----------------------------------------------------------------
• Concept shift: Burner Script → Progressive Script (permanent, versioned)
• Progressive Scripts Archive under Design_Documents/<module>/progressive_scripts
• Headers include PDD hash, model used, timestamp
• UI updates:
  - NEW purple buttons: Pull Repo, Update Repo (single-branch mode + GitHub Desktop option)
  - “Progressive Script” tab (renamed) with: ▸ Promote to Repo (archive/inject) ▸ Archive Current Version
  - NEW checkbox: Use GitHub Desktop — routes Pull/Update to also open the repo in GitHub Desktop for verification. Stores per-project repo URL/branch; pulls one branch only. Accepts Git URL or x-github-client:// link.
  - NEW checkbox: Single-branch only — enforces tracking only the selected branch.
  - NEW Update Repo dialog with CHECKBOXES: ▸ Include Progressive Scripts ▸ Include Design_Documents ▸ Include Info (project_info excluding repository) These choices are remembered per project across sessions.
• GitHub flows:
  - Pull Repo remembers URL + branch; single-branch clone/pull only.
  - Update Repo wipes target subfolders first (no residuals), copies selected items, commits, pushes, and optionally opens GitHub Desktop.
• Robust deletion:
  - Delete Repository now wipes ALL nested content including hidden .git on Windows.
  - Reset Project wipes everything and recreates minimal structure.
• Dual export packaging for GitHub (Design_Documents + generated scripts)
  - export_generated_scripts_* is fully wiped on each run, then ALL Progressive Scripts from every module are copied (all *.py versions), no residuals.
• Full backward compatibility with existing Codex-based workflow
• Auto-refresh Explorer after file ops + F5 refresh key
• System Console panel for live logs with colored syntax (STEP/PROGRESS/WARN/ERROR/SUCCESS)
Fixes and Notables (2025-08-06):
• **Streaming System Console**: Sync Repo now runs in a background thread with frequent progress ticks. You immediately see “Starting repository sync …” and periodic updates.
• **Ollama not running resilience**:
  - Centralized retry logic (bounded) for /api/chat and /api/embeddings with exponential backoff.
  - Early WARN/ERROR lines in the console if the local server is down; operations won’t hang the UI.
  - Embeddings gracefully skip; summaries log an error and continue the sync pipeline.
• **Update Repo dialog** revamped with checkboxes and per-project persistence.
• **Wipe/Save semantics (no residuals)** for Update Repo and Package for GitHub.
• **Task Type wiring** influences default options in Update Repo (Coding → include scripts; PDD → include design).
New Features (2025-08-06 Implementation):
• Human-like summaries with conversational prompts.
• Global Update Mode checkbox; repo-wide updates with diff extraction and per-script tasks.
• Launchable exports: UI selector for launch script, Launch button, error capture to versioned logs.
• Packaging checkboxes (Design Docs, Burner Lists, Burner Scripts); persisted; clean wipe; versioned branch naming.
• Codex directive file: generated if missing, persistent, included in exports.
• Integration: Global chat ties with Codex suggestions, PDD updates, summaries in human tone.
• Runtime testing: Capture stdout/stderr/exceptions, asset discovery after launch.
• Embedded humanistic prompts in prompts_config.json.

**Classes:** UpdateRepoDialog, PackageDialog, RantPDD, PromptControlDialog

**Functions:** _set_process_dpi_awareness(), _apply_tk_scaling(root, base_px), get_contrast_color(bg_hex), apply_modern_theme(style), _retry(fn), discover_ollama_models(), _choose_embedding_model(configured), _ollama_post(host, endpoint, payload, timeout), call_ollama_chat(model, prompt, timeout), embed(text, model), cos(a, b), run_git(args, cwd), git_is_repo(path), parse_tasks(text), _on_rm_error(func, path, exc_info), wipe_directory_contents(folder), main()


## Detailed Module Analyses


## Module `Rant_PDD.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rant_PDD.py — 2025 UI refresh with full workflow, Explorer, Dataset controls, safe resets, Sync & Summary features, versioned repository sync, and Package for GitHub.
🦈 SHARK_SENTINEL DeepSeek Progressive Script Integration + GitHub Enhancements
----------------------------------------------------------------
• Concept shift: Burner Script → Progressive Script (permanent, versioned)
• Progressive Scripts Archive under Design_Documents/<module>/progressive_scripts
• Headers include PDD hash, model used, timestamp
• UI updates:
  - NEW purple buttons: Pull Repo, Update Repo (single-branch mode + GitHub Desktop option)
  - “Progressive Script” tab (renamed) with: ▸ Promote to Repo (archive/inject) ▸ Archive Current Version
  - NEW checkbox: Use GitHub Desktop — routes Pull/Update to also open the repo in GitHub Desktop for verification. Stores per-project repo URL/branch; pulls one branch only. Accepts Git URL or x-github-client:// link.
  - NEW checkbox: Single-branch only — enforces tracking only the selected branch.
  - NEW Update Repo dialog with CHECKBOXES: ▸ Include Progressive Scripts ▸ Include Design_Documents ▸ Include Info (project_info excluding repository) These choices are remembered per project across sessions.
• GitHub flows:
  - Pull Repo remembers URL + branch; single-branch clone/pull only.
  - Update Repo wipes target subfolders first (no residuals), copies selected items, commits, pushes, and optionally opens GitHub Desktop.
• Robust deletion:
  - Delete Repository now wipes ALL nested content including hidden .git on Windows.
  - Reset Project wipes everything and recreates minimal structure.
• Dual export packaging for GitHub (Design_Documents + generated scripts)
  - export_generated_scripts_* is fully wiped on each run, then ALL Progressive Scripts from every module are copied (all *.py versions), no residuals.
• Full backward compatibility with existing Codex-based workflow
• Auto-refresh Explorer after file ops + F5 refresh key
• System Console panel for live logs with colored syntax (STEP/PROGRESS/WARN/ERROR/SUCCESS)
Fixes and Notables (2025-08-06):
• **Streaming System Console**: Sync Repo now runs in a background thread with frequent progress ticks. You immediately see “Starting repository sync …” and periodic updates.
• **Ollama not running resilience**:
  - Centralized retry logic (bounded) for /api/chat and /api/embeddings with exponential backoff.
  - Early WARN/ERROR lines in the console if the local server is down; operations won’t hang the UI.
  - Embeddings gracefully skip; summaries log an error and continue the sync pipeline.
• **Update Repo dialog** revamped with checkboxes and per-project persistence.
• **Wipe/Save semantics (no residuals)** for Update Repo and Package for GitHub.
• **Task Type wiring** influences default options in Update Repo (Coding → include scripts; PDD → include design).
New Features (2025-08-06 Implementation):
• Human-like summaries with conversational prompts.
• Global Update Mode checkbox; repo-wide updates with diff extraction and per-script tasks.
• Launchable exports: UI selector for launch script, Launch button, error capture to versioned logs.
• Packaging checkboxes (Design Docs, Burner Lists, Burner Scripts); persisted; clean wipe; versioned branch naming.
• Codex directive file: generated if missing, persistent, included in exports.
• Integration: Global chat ties with Codex suggestions, PDD updates, summaries in human tone.
• Runtime testing: Capture stdout/stderr/exceptions, asset discovery after launch.
• Embedded humanistic prompts in prompts_config.json.
"""
import os
import sys
import json
import time
import sqlite3
import hashlib
import threading
import subprocess
import platform
import ctypes
import logging
import shutil
import stat
import re
import difflib
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
import tkinter as tk
import tkinter.font as tkfont
import tkinter.simpledialog as simpledialog
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename
import speech_recognition as sr
import pyttsx3
import requests
import numpy as np
from scipy.spatial.distance import cosine

# -------------------- Paths / Config --------------------
ROOT_DIR = r"C:\Users\Art PC\Desktop\Rant_PDD"
BASE_DIR = os.path.join(ROOT_DIR, "Rant_PDD")
PROJECTS_DIR = os.path.join(BASE_DIR, "Projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
LOG_FILE = os.path.join(BASE_DIR, "rant_pdd.log")
UPDATE_WS_NAME = "project_info"
REPO_FOLDER = "repository"
THINK_DIR_NAME = "Logic_Thoughts"  # where <think> extractions go
DEFAULT_CONFIG = {
    "last_project": "",
    "tts_speed": 150,
    "tts_rate_factor": 1.0,
    "mic_device": 0,
    "context_depth": 20,
    "ollama_model_coding": "deepseek-coder-v2:16b",
    "ollama_model_text": "phi4:latest",  # Prefer embed2 if present; auto-detect in code when missing
    "embedding_model": "snowflake-arctic-embed2:latest",
    # Global defaults; project-specific settings are under "projects"
    "use_github_desktop_default": False,
    "single_branch_only_default": True,
    "projects": {  # "<project_name>": {
        # "use_github_desktop": bool,
        # "repo_url": "https://github.com/owner/repo.git" or "git@github.com:owner/repo.git"
        # or "x-github-client://openRepo/...",
        # "repo_branch": "main",
        # "single_branch_only": True,
        # "desktop_link": "x-github-client://openRepo/...",
        # "update_repo_options": {
        #     "include_scripts": True,
        #     "include_design": True,
        #     "include_info": False,
        #     "commit_direct": True,
        #     "commit_message": "Auto-injected progressive scripts from DeepSeek PDD update"
        # }
        # }
    },
    "global_update_mode": False,
    "launch_script": "main.py"
}
DEFAULT_PROMPTS = {
    "summary": (
        "Explain this script as if you’re handing it off to a new developer. Include why it exists, what its main functions do, how it connects to other parts of the project, and what someone maintaining it needs to know. Use a conversational but professional tone."
    ),
    "consistency": (
        "Scan the entire PDD for conflicts with the new update. "
        "Output only lines like: Section:<id>|Reason:<reason>\n\n"
        "New update:\n{summary}\n\nPDD:\n{full_pdd}"
    ),
    "rewrite": (
        "Rewrite ONLY this section to resolve the inconsistency and align with the new update.\n\n"
        "Section:\n{section_text}\n\nNew update:\n{summary}\n\nReason:\n{reason}"
    ),
    "pseudo": (
        "Pseudo-Code Bot: walk each new PDD section and inject light pseudocode hints "
        "wherever UI elements or code snippets were requested. "
        "Enclose each hint in /* … */ so we can strip or style them later.\n\nPDD:\n{full_pdd}"
    ),
    "burner_script": (
        "Draft a first pass Python script that implements the key behaviors described in this PDD. "
        "Be pragmatic; use TODOs where necessary.\n\nPDD:\n{pdd}"
    ),
    "prep_rewrite": (
        "Rewrite this text more clearly and concisely, preserving meaning:\n\n{text}"
    ),
    "project_sync": (
        "You are a project analyst. Summarize the entire project folder, including all code snippets, "
        "markdown, JSON, and existing PDD, into a single comprehensive PDD instantiation. "
        "Be detailed, structured, and ready for code implementation."
    ),
    "project_overview": (
        "Provide a static overview summary of this project: include high-level goals, "
        "folder structure, key modules, and the current PDD. Do not modify the PDD—just summarize."
    ),
    "global_diff_extraction": (
        "Take the user’s repository-wide instructions and, for each script, identify what changes need to be made and why. Generate a per-script task list that describes these changes in natural, human-readable language but is still actionable by an AI update pipeline. Output these tasks as structured JSON."
    ),
    "human_pdd_update": (
        "Update the PDD for this script to reflect new global architecture changes requested by the user and informed by Codex improvement suggestions. Include:\n1. Why this change was necessary.\n2. How it affects the script’s role in the system.\n3. What functions or components were modified or added.\n4. How it integrates with related scripts.\nUse a conversational but technical tone, like an experienced engineer documenting design changes for their team."
    ),
    "human_summary_update": (
        "Summarize the latest changes to this script after a global update. Focus on what was added or changed and why, and explain how it affects the overall workflow. Write as if to a teammate picking up this code tomorrow."
    ),
    "runtime_documentation": (
        "When launching this repo version, capture all runtime errors and warnings. Present them in a human-readable list explaining what each error means, where it likely originates, and what it impacts. Include file names, line numbers, and probable causes."
    ),
    "packaging": (
        "Package the repository as a new version branch. Include all active Python scripts, dependencies, and metadata (README, requirements.txt). Ensure folder structure matches a real repo root. Create a new GitHub branch using this folder as the base."
    ),
    "improvement_file": (
        "Create a directives file in the repo root instructing Codex to analyze the repository for structural and logic improvements. Ensure it contains explicit do-not-delete instructions and blank space for Codex to fill in improvement notes."
    ),
    "global_chat_execution": (
        "User has requested a repository-wide change. Determine which scripts are affected, generate per-script task plans, integrate Codex improvement suggestions, and update each script’s PDD, summary, pseudocode, and burner script. Stream all actions to the console and update Codex improvement directives for future review."
    ),
    "runtime_testing": (
        "Run the exported branch version using the selected launch script. Capture all console output, Python exceptions, and dynamically created files. Save logs and asset lists in project_info for future analysis."
    ),
    "pdd_generation": (
        "Generate a full Program Design Document for this script. Explain it like an experienced engineer onboarding a new team member. Cover purpose, design choices, dependencies, and potential evolution. Use clear, conversational language while staying technically precise."
    ),
    "summary_generation": (
        "Summarize this script for quick understanding. Explain why it exists, what it does, and how it connects to other parts of the system. Use a conversational but professional tone as if handing off to another developer."
    ),
    "codex_suggestion": (
        "Analyze the entire repository and propose changes to improve structure, performance, or clarity. Include missing features, refactor opportunities, and integration gaps. Write in human-readable actionable steps."
    ),
}

# -------------------- Logging --------------------
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("RantPDD")
try:
    logger.addHandler(RotatingFileHandler(LOG_FILE, maxBytes=10**6, backupCount=5))
except Exception:
    pass

# -------------------- DPI / Scaling --------------------
def _set_process_dpi_awareness() -> None:
    if platform.system() == "Windows":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

def _apply_tk_scaling(root: tk.Tk, base_px: int = 96) -> None:
    scale = 1.0
    if platform.system() == "Windows":
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
            scale = max(0.8, dpi / base_px)
        except Exception:
            pass
    try:
        root.call("tk", "scaling", scale)
    except Exception:
        pass

# -------------------- Theme & Contrast --------------------
def get_contrast_color(bg_hex: str) -> str:
    r, g, b = (int(bg_hex[i:i+2], 16) for i in (1, 3, 5))
    brightness = (r*299 + g*587 + b*114) / 1000
    return "#000000" if brightness > 125 else "#FFFFFF"

# Module-level theme constants so widgets can reference them safely
THEME_BG = "#0F1115"
THEME_SUR = "#151922"
THEME_ELEV = "#1B2130"
THEME_TEXT = get_contrast_color(THEME_BG)
THEME_ACC = "#60A5FA"
THEME_ACC2 = "#93C5FD"

# Console color palette
CLR_INFO = "#93C5FD"  # soft blue
CLR_WARN = "#FACC15"  # yellow
CLR_ERROR = "#F87171"  # red
CLR_STEP = "#22D3EE"  # cyan
CLR_SUCCESS = "#34D399"  # green
CLR_PROGRESS = "#C084FC"  # violet
CLR_MUTED = "#9CA3AF"  # gray

def apply_modern_theme(style: ttk.Style) -> None:
    style.theme_use("clam")
    for name in ("TFrame", "TLabelframe"):
        style.configure(name, background=THEME_BG)
    style.configure("TLabelframe.Label", background=THEME_BG, foreground=THEME_TEXT)
    style.configure("TLabel", background=THEME_BG, foreground=THEME_TEXT)
    style.configure("TButton", background=THEME_ACC, foreground=get_contrast_color(THEME_ACC), padding=(10, 6), borderwidth=0)
    style.map("TButton", background=[("active", THEME_ACC2)])
    style.configure("Secondary.TButton", background=THEME_SUR, foreground=get_contrast_color(THEME_SUR), padding=(10, 6))
    style.map("Secondary.TButton", background=[("active", THEME_ELEV)])
    style.configure("Purple.TButton", background="#9b59b6", foreground="white", padding=(10, 6))
    style.map("Purple.TButton", background=[("active", "#8e44ad")])
    style.configure("TEntry", fieldbackground=THEME_ELEV, background=THEME_ELEV, foreground=get_contrast_color(THEME_ELEV))
    style.configure("TCombobox", fieldbackground=THEME_ELEV, background=THEME_ELEV, foreground=get_contrast_color(THEME_ELEV))
    style.configure("Treeview", background=THEME_ELEV, fieldbackground=THEME_ELEV, foreground=get_contrast_color(THEME_ELEV), rowheight=24)
    style.map("Treeview", background=[("selected", "#2b5797")])
    base = ("Segoe UI Variable", 10) if platform.system() == "Windows" else ("Helvetica", 11)
    mono = ("Cascadia Mono", 10) if platform.system() == "Windows" else ("Menlo", 11)
    try:
        tkfont.nametofont("TkDefaultFont").configure(family=base[0], size=base[1])
        tkfont.nametofont("TkTextFont").configure(family=base[0], size=base[1])
        tkfont.nametofont("TkFixedFont").configure(family=mono[0], size=mono[1])
    except Exception:
        pass

# -------------------- Retry helpers for Ollama --------------------
def _retry(fn: Callable[[], Any], *, attempts: int = 3, base_delay: float = 0.6, what: str = "request") -> Any:
    """ Simple bounded retry with exponential backoff. Logs WARN on failures. Returns the function result or raises the last exception. """
    last_exc = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            wait = base_delay * (2 ** i)
            logger.warning(f"{what} attempt {i+1}/{attempts} failed: {e}; retrying in {wait:.1f}s")
            time.sleep(wait)
    raise last_exc if last_exc else RuntimeError(f"{what} failed without exception")

# -------------------- Ollama helpers --------------------
def discover_ollama_models() -> List[str]:
    models = []
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, timeout=4)
        for line in out.splitlines()[1:]:
            parts = line.split()
            if parts:
                models.append(parts[0])
    except Exception as e:
        logger.info("ollama list failed: %s", e)
    # Sensible defaults if detection fails
    models.extend([
        "deepseek-coder-v2:16b",
        "phi4:latest",
        "snowflake-arctic-embed2:latest",
        "snowflake-arctic-embed:latest"
    ])
    return sorted(set(models))

def _choose_embedding_model(configured: str) -> str:
    """Prefer configured; if not present in 'ollama list', try to pick an installed embed model."""
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, timeout=4)
        names = [ln.split()[0] for ln in out.splitlines()[1:] if ln.strip()]
        if configured in names:
            return configured
        for cand in names:
            if "embed" in cand:
                return cand
        for cand in ["snowflake-arctic-embed2:latest", "snowflake-arctic-embed:latest"]:
            if cand in names:
                return cand
    except Exception:
        pass
    return configured  # try as-is

def _ollama_post(host: str, endpoint: str, payload: dict, timeout: int):
    return requests.post(f"{host}{endpoint}", json=payload, timeout=timeout)

def call_ollama_chat(model: str, prompt: str, timeout: int = 60) -> str:
    """ Chat wrapper with retries and fallbacks. Non-blocking UI (caller should be on worker thread). """
    hosts = ("http://localhost:11434", "http://127.0.0.1:11434")
    last_err = ""
    def _try_chat_once():
        nonlocal last_err
        for host in hosts:
            try:
                resp = _ollama_post(host, "/api/chat", {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}, timeout)
                if resp.status_code == 404:  # Older server may support /api/generate
                    resp = _ollama_post(host, "/api/generate", {"model": model, "prompt": prompt, "stream": False}, timeout)
                resp.raise_for_status()
                j = resp.json()
                if isinstance(j, dict):
                    if "message" in j and isinstance(j["message"], dict):
                        return j["message"].get("content", "")
                    if "response" in j:
                        return j["response"]
                return ""
            except Exception as e:
                last_err = str(e)
                continue
        raise RuntimeError(last_err or "Ollama chat unreachable")
    try:
        return _retry(_try_chat_once, attempts=3, base_delay=0.7, what="ollama chat")
    except Exception as e:
        logger.error("Ollama chat error: %s", e)
        return f"Error: {e}"

def embed(text: str, model: str) -> Optional[List[float]]:
    """ Robust embeddings:
    • Uses /api/embeddings with {"input": "..."} (current spec).
    • Auto-picks an installed embedding model if the configured one is missing.
    • Bounded retries; returns None on failure (UI remains responsive).
    """
    chosen = _choose_embedding_model(model)
    payload_primary = {"model": chosen, "input": text}
    payload_legacy = {"model": chosen, "prompt": text}  # some older builds used 'prompt'
    hosts = ("http://localhost:11434", "http://127.0.0.1:11434")
    def _try_embed_once():
        last_exc = None
        for host in hosts:
            try:
                r = _ollama_post(host, "/api/embeddings", payload_primary, 18)
                if r.status_code == 404:
                    r = _ollama_post(host, "/api/embeddings", payload_legacy, 18)
                r.raise_for_status()
                j = r.json()
                if isinstance(j, dict):
                    if "embedding" in j:
                        return j.get("embedding")
                    if "data" in j and isinstance(j["data"], list) and j["data"]:
                        return j["data"][0].get("embedding")
                return None
            except Exception as e:
                last_exc = e
                continue
        if last_exc:
            raise last_exc
        return None
    try:
        return _retry(_try_embed_once, attempts=2, base_delay=0.5, what="ollama embeddings")
    except Exception as e:
        logger.warning("Embedding error (skipping): %s", e)
        return None

def cos(a, b) -> float:
    if a is None or b is None:
        return 0.0
    return 1 - cosine(np.array(a), np.array(b))

# -------------------- Git helpers --------------------
def run_git(args: List[str], cwd: str) -> Tuple[int, str, str]:
    try:
        cp = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return cp.returncode, cp.stdout, cp.stderr
    except Exception as e:
        return 1, "", str(e)

def git_is_repo(path: str) -> bool:
    code, out, _ = run_git(["rev-parse", "--is-inside-work-tree"], cwd=path)
    return code == 0 and out.strip() == "true"

# -------------------- Consistency parsing --------------------
def parse_tasks(text: str) -> List[Dict[str, str]]:
    tasks = []
    for line in text.splitlines():
        if line.strip().startswith("Section:"):
            parts = [p.strip() for p in line.split("|")]
            try:
                sid = parts[0].split(":", 1)[1].strip()
                reason = parts[1].split(":", 1)[1].strip()
                tasks.append({"section_id": sid, "reason": reason})
            except Exception:
                pass
    return tasks

# -------------------- Robust deletion helpers --------------------
def _on_rm_error(func, path, exc_info):
    # Clear read-only and retry
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def wipe_directory_contents(folder: Path):
    """Delete EVERYTHING inside a folder (including hidden .git trees) cross-platform."""
    if not folder.exists():
        return
    for entry in folder.iterdir():
        try:
            if entry.is_dir():
                shutil.rmtree(entry, onerror=_on_rm_error)
            else:
                try:
                    os.chmod(entry, stat.S_IWRITE)
                except Exception:
                    pass
                entry.unlink(missing_ok=True)
        except Exception:
            # Last resort: attempt with OS shell on Windows for stubborn files
            if platform.system() == "Windows":
                try:
                    subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", str(entry)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    subprocess.run(["cmd", "/c", "del", "/f", "/q", str(entry)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except Exception:
                    pass

# -------------------- Update Repo dialog (with checkboxes, persisted) --------------------
class UpdateRepoDialog(tk.Toplevel):
    def __init__(self, parent, default_branch: str, defaults: Dict[str, Any]):
        """ defaults keys: include_scripts (bool), include_design (bool), include_info (bool), commit_direct (bool), commit_message (str) """
        super().__init__(parent)
        self.title("Update Repository")
        self.configure(bg=THEME_BG)
        self.resizable(False, False)
        self.include_scripts = tk.BooleanVar(value=bool(defaults.get("include_scripts", True)))
        self.include_design = tk.BooleanVar(value=bool(defaults.get("include_design", True)))
        self.include_info = tk.BooleanVar(value=bool(defaults.get("include_info", False)))
        self.include_burner_lists = tk.BooleanVar(value=bool(defaults.get("include_burner_lists", False)))
        self.include_burner_scripts = tk.BooleanVar(value=bool(defaults.get("include_burner_scripts", False)))
        self.commit_direct = tk.BooleanVar(value=bool(defaults.get("commit_direct", True)))
        self.commit_message = tk.StringVar(value=defaults.get("commit_message", "Auto-injected progressive scripts from DeepSeek PDD update"))
        ttk.Label(self, text="What do you want to send? (remembered per project)", background=THEME_BG, foreground=THEME_TEXT).pack(anchor="w", padx=10, pady=(10, 6))
        ttk.Checkbutton(self, text="Include Progressive Scripts (ALL archived *.py)", variable=self.include_scripts).pack(anchor="w", padx=18)
        ttk.Checkbutton(self, text="Include Design_Documents", variable=self.include_design).pack(anchor="w", padx=18)
        ttk.Checkbutton(self, text=f"Include Info (/{UPDATE_WS_NAME} excluding /{UPDATE_WS_NAME}/{REPO_FOLDER})", variable=self.include_info).pack(anchor="w", padx=18)
        ttk.Checkbutton(self, text="Include Burner Lists", variable=self.include_burner_lists).pack(anchor="w", padx=18)
        ttk.Checkbutton(self, text="Include Burner Scripts", variable=self.include_burner_scripts).pack(anchor="w", padx=18)
        ttk.Label(self, text="Commit message:", background=THEME_BG, foreground=THEME_TEXT).pack(anchor="w", padx=10, pady=(10, 2))
        e = ttk.Entry(self, textvariable=self.commit_message, width=64)
        e.pack(fill="x", padx=10)
        ttk.Checkbutton(self, text=f"Commit directly to '{default_branch}' (single-branch mode)", variable=self.commit_direct).pack(anchor="w", padx=10, pady=(10, 2))
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=(10, 10))
        ttk.Button(btns, text="Cancel", command=self.destroy, style="Secondary.TButton").pack(side="right")
        ttk.Button(btns, text="Update", command=self._do_ok).pack(side="right", padx=6)
        self.ok = False
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _do_ok(self):
        self.ok = True
        self.destroy()

# -------------------- Package Dialog --------------------
class PackageDialog(tk.Toplevel):
    def __init__(self, parent, defaults: Dict[str, Any]):
        super().__init__(parent)
        self.title("Package for GitHub")
        self.configure(bg=THEME_BG)
        self.resizable(False, False)
        self.include_design = tk.BooleanVar(value=bool(defaults.get("include_design", True)))
        self.include_burner_lists = tk.BooleanVar(value=bool(defaults.get("include_burner_lists", False)))
        self.include_burner_scripts = tk.BooleanVar(value=bool(defaults.get("include_burner_scripts", False)))
        ttk.Label(self, text="What do you want to include? (remembered per project)", background=THEME_BG, foreground=THEME_TEXT).pack(anchor="w", padx=10, pady=(10, 6))
        ttk.Checkbutton(self, text="Include Design Documents", variable=self.include_design).pack(anchor="w", padx=18)
        ttk.Checkbutton(self, text="Include Burner Lists", variable=self.include_burner_lists).pack(anchor="w", padx=18)
        ttk.Checkbutton(self, text="Include Burner Scripts", variable=self.include_burner_scripts).pack(anchor="w", padx=18)
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=(10, 10))
        ttk.Button(btns, text="Cancel", command=self.destroy, style="Secondary.TButton").pack(side="right")
        ttk.Button(btns, text="Package", command=self._do_ok).pack(side="right", padx=6)
        self.ok = False
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _do_ok(self):
        self.ok = True
        self.destroy()

# -------------------- Main App --------------------
class RantPDD:
    def __init__(self, root: tk.Tk):
        self.root = root
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{min(1920, sw)}x{min(1080, sh)}")
        self.db_lock = threading.RLock()
        self.config = self._load_config()
        self.prompts = DEFAULT_PROMPTS.copy()
        self.current_project: Optional[str] = None
        self.current_db: Optional[sqlite3.Connection] = None
        self.sections: List[Dict[str, Any]] = []
        self.pdd_lines: List[str] = []
        self.tts = None
        self.tts_muted = False
        self.recognizer = None
        self.mic = None
        self.listening = False
        self.stt_thread: Optional[threading.Thread] = None
        self.task_type = tk.StringVar(value="PDD")  # Default task type
        self.global_mode = tk.BooleanVar(value=False)
        style = ttk.Style()
        apply_modern_theme(style)
        self._build_ui()
        self._init_audio()
        # Hook F5 to refresh
        self.root.bind("<F5>", lambda e: self._refresh_all_views())
        # Attach live console handler with color-aware emit
        class TkConsoleHandler(logging.Handler):
            def __init__(self, app):
                super().__init__()
                self.app = app
            def emit(self, record):
                msg = self.format(record)
                level = record.levelname.upper()
                # Marshal to UI thread with tag based on level
                self.app.root.after(0, self.app._console_write, msg, level)
        h = TkConsoleHandler(self)
        h.setLevel(logging.INFO)
        logger.addHandler(h)
        self._refresh_projects()
        if self.config["last_project"]:
            self._switch_project(self.config["last_project"])

    # ---------- config ----------
    def _load_config(self) -> Dict[str, Any]:
        d = DEFAULT_CONFIG.copy()
        try:
            if os.path.exists(CONFIG_FILE):
                loaded = json.loads(Path(CONFIG_FILE).read_text())
                # Deep-merge for "projects"
                d.update({k: v for k, v in loaded.items() if k != "projects"})
                pj = d.get("projects", {}).copy()
                pj.update(loaded.get("projects", {}))
                d["projects"] = pj
        except Exception:
            pass
        return d

    def _save_config(self):
        # Persist global toggles
        self.config["context_depth"] = int(self.sld_context.get())
        self.config["tts_rate_factor"] = float(self.sld_tts_speed.get())
        # Persist per-project repo settings
        if self.current_project:
            name = os.path.basename(self.current_project)
            proj_cfg = self.config["projects"].setdefault(name, {})
            proj_cfg["use_github_desktop"] = bool(self.use_desktop.get())
            proj_cfg["single_branch_only"] = bool(self.single_branch_only.get())
            proj_cfg["global_update_mode"] = bool(self.global_mode.get())
            proj_cfg["launch_script"] = self.cmb_launch_script.get()
        try:
            Path(CONFIG_FILE).write_text(json.dumps(self.config, indent=2))
        except Exception:
            pass

    # Helpers for per-project repo settings
    def _proj_cfg(self) -> Dict[str, Any]:
        name = os.path.basename(self.current_project) if self.current_project else ""
        cfg = self.config["projects"].setdefault(name, {})
        # Apply defaults if missing
        cfg.setdefault("use_github_desktop", self.config.get("use_github_desktop_default", False))
        cfg.setdefault("single_branch_only", self.config.get("single_branch_only_default", True))
        cfg.setdefault("repo_url", "")
        cfg.setdefault("repo_branch", "main")
        cfg.setdefault("desktop_link", "")  # optional x-github-client link
        cfg.setdefault("update_repo_options", {
            "include_scripts": True,
            "include_design": True,
            "include_info": False,
            "include_burner_lists": False,
            "include_burner_scripts": False,
            "commit_direct": True,
            "commit_message": "Auto-injected progressive scripts from DeepSeek PDD update",
        })
        cfg.setdefault("package_options", {
            "include_design": True,
            "include_burner_lists": False,
            "include_burner_scripts": False,
        })
        cfg.setdefault("global_update_mode", False)
        cfg.setdefault("launch_script", "main.py")
        return cfg

    # ---------- audio ----------
    def _init_audio(self):
        try:
            self.tts = pyttsx3.init()
            base_rate = DEFAULT_CONFIG["tts_speed"]
            factor = self.config.get("tts_rate_factor", 1.0)
            self.tts.setProperty("rate", int(base_rate * factor))
            # Force Zira if present
            for v in self.tts.getProperty("voices"):
                if "zira" in (v.name or "").lower():
                    self.tts.setProperty("voice", v.id)
                    break
        except Exception as e:
            logger.warning("TTS init error: %s", e)
            self.tts = None
        try:
            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone(device_index=self.config["mic_device"])
        except Exception as e:
            logger.warning("STT init error: %s", e)
            self.recognizer = None
            self.mic = None

    # ---------- UI construction ----------
    def _build_ui(self):
        _apply_tk_scaling(self.root)
        # Toolbar
        tb = ttk.Frame(self.root, padding=8)
        tb.pack(side="top", fill="x")
        ttk.Label(tb, text="Project:").pack(side="left")
        self.cmb_project = ttk.Combobox(tb, state="readonly", width=28)
        self.cmb_project.pack(side="left", padx=6)
        self.cmb_project.bind("<<ComboboxSelected>>", lambda e: self._switch_project(self.cmb_project.get()))
        ttk.Button(tb, text="New Project", command=self._create_project).pack(side="left", padx=6)
        ttk.Button(tb, text="Add Local Repo", command=self._add_local_repo, style="Secondary.TButton").pack(side="left", padx=6)
        # Backward-compatible Clone; new Pull (Purple) preferred
        ttk.Button(tb, text="Clone Repo", command=self._clone_repo, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Pull Repo", command=self._pull_repo, style="Purple.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Update Repo", command=self._update_repo_with_progressive, style="Purple.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Delete Repository", command=self._delete_repository, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Reset Data Set", command=self._reset_data_set, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Reset Project", command=self._reset_project_folder, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Open in Explorer", command=self._open_in_explorer, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Refresh (F5)", command=self._refresh_all_views, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Label(tb, text="Task Type:").pack(side="left", padx=(18, 0))
        self.cmb_task = ttk.Combobox(tb, state="readonly", values=["PDD", "Coding"], width=10, textvariable=self.task_type)
        self.cmb_task.pack(side="left", padx=6)
        self.cmb_task.set("PDD")
        self.cmb_task.bind("<<ComboboxSelected>>", lambda e: self._update_task_type())
        ttk.Label(tb, text="Context:").pack(side="left", padx=(18, 0))
        self.sld_context = ttk.Scale(tb, from_=1, to=60, value=self.config.get("context_depth", 20), orient="horizontal", length=160)
        self.sld_context.pack(side="left", padx=6)
        self.sld_context.bind("<ButtonRelease-1>", lambda e: self._save_config())
        ttk.Button(
            tb, text="Prompt/LLM Control", command=lambda: PromptControlDialog(self.root, self.prompts, app_ref=self), style="Secondary.TButton"
        ).pack(side="left", padx=10)
        # NOTE: Sync Repository now runs async (threaded) to keep UI/console alive
        ttk.Button(tb, text="Sync Repository", command=self._sync_repository, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Package for GitHub", command=self._package_for_github, style="Secondary.TButton").pack(side="left", padx=6)
        # Versions controls
        ttk.Label(tb, text="Version:").pack(side="left", padx=(18, 0))
        self.cmb_version = ttk.Combobox(tb, state="readonly", width=22)
        self.cmb_version.pack(side="left", padx=6)
        self.cmb_version.bind("<<ComboboxSelected>>", lambda e: self._load_version(self.cmb_version.get()))
        ttk.Button(tb, text="Save Version", command=self._save_version, style="Secondary.TButton").pack(side="left", padx=6)
        # Git Ops toggles
        ttk.Label(tb, text="Git Ops:").pack(side="left", padx=(18, 2))
        self.use_desktop = tk.BooleanVar(value=self.config.get("use_github_desktop_default", False))
        self.single_branch_only = tk.BooleanVar(value=self.config.get("single_branch_only_default", True))
        ttk.Checkbutton(tb, text="Use GitHub Desktop", variable=self.use_desktop, command=self._save_config).pack(side="left", padx=(2, 12))
        ttk.Checkbutton(tb, text="Single-branch only", variable=self.single_branch_only, command=self._save_config).pack(side="left", padx=(0, 6))
        # Global Mode
        ttk.Checkbutton(tb, text="Global Update Mode", variable=self.global_mode, command=self._save_config).pack(side="left", padx=(0, 6))
        # Launch Controls
        ttk.Label(tb, text="Launch Script:").pack(side="left", padx=(18, 0))
        self.cmb_launch_script = ttk.Combobox(tb, state="readonly", width=20)
        self.cmb_launch_script.pack(side="left", padx=6)
        ttk.Button(tb, text="Set Launch", command=self._set_launch_script, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Test Launch", command=self._test_launch, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Mark Stable", command=self._mark_stable, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(tb, text="Launch Script", command=self._launch_script, style="Secondary.TButton").pack(side="left", padx=6)
        # Main Paned: Explorer | Center
        outer = ttk.PanedWindow(self.root, orient="horizontal")
        outer.pack(fill="both", expand=True)
        # LEFT — Explorer + Viewer + Program Design Manager + Console
        left = ttk.PanedWindow(outer, orient="vertical")
        outer.add(left, weight=1)
        # Explorer
        lf1 = ttk.Labelframe(left, text="Explorer", padding=6)
        left.add(lf1, weight=2)
        self.tree = ttk.Treeview(lf1, show="tree")
        self.tree.pack(side="left", fill="both", expand=True)
        ysb = ttk.Scrollbar(lf1, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ysb.set)
        ysb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._on_tree_select())
        # Viewer
        lf2 = ttk.Labelframe(left, text="Viewer", padding=6)
        left.add(lf2, weight=2)
        mono = tkfont.nametofont("TkFixedFont")
        self.file_view = tk.Text(lf2, bg=THEME_BG, fg=THEME_TEXT, insertbackground=THEME_TEXT, wrap="none", font=mono)
        self.file_view.pack(side="left", fill="both", expand=True)
        ysv = ttk.Scrollbar(lf2, orient="vertical", command=self.file_view.yview)
        self.file_view.configure(yscrollcommand=ysv.set)
        ysv.pack(side="right", fill="y")
        ttk.Button(lf2, text="Delete Selected", command=self._delete_selected, style="Secondary.TButton").pack(side="bottom", pady=4)
        # Program Design Manager
        pdm = ttk.Labelframe(left, text="Program Design Manager", padding=6)
        left.add(pdm, weight=1)
        self.pdd_list = tk.Listbox(pdm, bg=THEME_ELEV, fg=THEME_TEXT, selectbackground="#2b5797")
        self.pdd_list.pack(side="left", fill="both", expand=True)
        self.pdd_list.bind("<<ListboxSelect>>", lambda e: self._on_pdd_list_select())
        pdm_buttons = ttk.Frame(pdm)
        pdm_buttons.pack(side="right", fill="y")
        ttk.Button(pdm_buttons, text="New Subfolder", command=self._new_pdd_subfolder, style="Secondary.TButton").pack(pady=4)
        ttk.Button(pdm_buttons, text="Delete Subfolder", command=self._delete_pdd_subfolder, style="Secondary.TButton").pack(pady=4)
        ttk.Button(pdm_buttons, text="Rename Subfolder", command=self._rename_pdd_subfolder, style="Secondary.TButton").pack(pady=4)
        ttk.Button(pdm_buttons, text="Add Burner Script", command=self._add_burner_script_to_selected, style="Secondary.TButton").pack(pady=4)
        # System Console
        con = ttk.Labelframe(left, text="System Console", padding=6)
        left.add(con, weight=1)
        self.console = tk.Text(con, height=10, bg=THEME_ELEV, fg=THEME_TEXT, insertbackground=THEME_TEXT, wrap="word", font=mono, padx=8, pady=6, state="disabled")
        self.console.pack(side="left", fill="both", expand=True)
        # Tag colors for syntax highlighting
        for tag, fg in [("INFO", CLR_INFO), ("WARN", CLR_WARN), ("ERROR", CLR_ERROR), ("STEP", CLR_STEP), ("SUCCESS", CLR_SUCCESS), ("PROGRESS", CLR_PROGRESS), ("MUTED", CLR_MUTED)]:
            self.console.tag_config(tag, foreground=fg)
        con_scroll = ttk.Scrollbar(con, orient="vertical", command=self.console.yview)
        self.console.configure(yscrollcommand=con_scroll.set)
        con_scroll.pack(side="right", fill="y")
        btns = ttk.Frame(con)
        btns.pack(side="bottom", fill="x", pady=4)
        ttk.Button(btns, text="Clear Console", command=self._clear_console, style="Secondary.TButton").pack(side="right")
        # CENTER — Prep + Input + Workflow
        center = ttk.Labelframe(outer, text="Chat / Workflow", padding=6)
        outer.add(center, weight=2)
        # PREP
        prep_frame = ttk.Labelframe(center, text="Prep (curated to send)", padding=6)
        prep_frame.pack(fill="both", expand=False)
        self.txt_prep = tk.Text(prep_frame, height=10, bg=THEME_ELEV, fg=THEME_TEXT, insertbackground=THEME_TEXT, wrap="word", font=mono, padx=8, pady=6)
        self.txt_prep.pack(side="left", fill="both", expand=True)
        prep_scroll = ttk.Scrollbar(prep_frame, orient="vertical", command=self.txt_prep.yview)
        self.txt_prep.configure(yscrollcommand=prep_scroll.set)
        prep_scroll.pack(side="right", fill="y")
        ttk.Button(prep_frame, text="Rewrite Prep", command=self._rewrite_prep, style="Secondary.TButton").pack(side="bottom", pady=4)
        # INPUT
        in_frame = ttk.Labelframe(center, text="Input (typing + speech-to-text)", padding=6)
        in_frame.pack(fill="both", expand=False, pady=(6, 0))
        self.txt_input = tk.Text(in_frame, height=6, bg=THEME_ELEV, fg=THEME_TEXT, insertbackground=THEME_TEXT, wrap="word", font=mono, padx=8, pady=6)
        self.txt_input.pack(side="left", fill="both", expand=True)
        in_scroll = ttk.Scrollbar(in_frame, orient="vertical", command=self.txt_input.yview)
        self.txt_input.configure(yscrollcommand=in_scroll.set)
        in_scroll.pack(side="right", fill="y")
        self.txt_input.bind("<Return>", self._send_on_enter)
        self.txt_input.bind("<KP_Enter>", self._send_on_enter)
        # INPUT ACTIONS
        in_actions = ttk.Frame(center)
        in_actions.pack(fill="x", pady=(4, 2))
        self.btn_sync = ttk.Button(in_actions, text="Sync Project", command=self._sync_to_project, style="Secondary.TButton")
        self.btn_sync.pack(side="left", padx=(0, 4))
        ttk.Button(in_actions, text="Send to Prep", command=self._send_to_prep).pack(side="left")
        ttk.Button(in_actions, text="Clear Prep", command=lambda: self.txt_prep.delete("1.0", "end"), style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(in_actions, text="Add to PDD", command=self._send_prep_to_llm).pack(side="left", padx=6)
        ttk.Button(in_actions, text="Append Prep → PDD", command=self._append_prep_to_pdd, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(in_actions, text="Start Mic", command=self._start_mic, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(in_actions, text="Stop Mic", command=self._stop_mic, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(in_actions, text="Stop TTS", command=self._stop_tts_immediate, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Label(in_actions, text="TTS Speed:").pack(side="left", padx=(12, 0))
        self.sld_tts_speed = ttk.Scale(in_actions, from_=0.5, to=2.0, value=self.config.get("tts_rate_factor", 1.0), orient="horizontal", length=100)
        self.sld_tts_speed.pack(side="left", padx=4)
        self.sld_tts_speed.bind("<ButtonRelease-1>", lambda e: self._update_tts_speed())
        ttk.Button(in_actions, text="Burner Script", command=self._burner_script, style="Secondary.TButton").pack(side="left", padx=6)
        ttk.Button(in_actions, text="Summarize Project", command=self._summarize_project, style="Secondary.TButton").pack(side="left", padx=6)
        # WORKFLOW OUTPUT — Notebook of PDD, Progressive & Overview
        wf_frame = ttk.Labelframe(center, text="Workflow Output", padding=6)
        wf_frame.pack(fill="both", expand=True, pady=(6, 0))
        self.nb = ttk.Notebook(wf_frame)
        self.nb.pack(fill="both", expand=True)
        # PDD tab
        tab1 = ttk.Frame(self.nb)
        self.nb.add(tab1, text="PDD")
        self.txt_pdd = tk.Text(tab1, bg=THEME_ELEV, fg=THEME_TEXT, insertbackground=THEME_TEXT, wrap="word", font=mono, padx=8, pady=6)
        self.txt_pdd.pack(fill="both", expand=True)
        self.txt_pdd.bind("<Control-s>", lambda e: self._save_pdd() or "break")
        self.txt_pdd.bind("<KeyRelease>", lambda e: (self._on_pdd_edit(), self._update_sync_state()))
        pdd_scroll = ttk.Scrollbar(tab1, orient="vertical", command=self.txt_pdd.yview)
        self.txt_pdd.configure(yscrollcommand=pdd_scroll.set)
        pdd_scroll.pack(side="right", fill="y")
        # Progressive Script tab (renamed from Burner Script)
        tab2 = ttk.Frame(self.nb)
        self.nb.add(tab2, text="Progressive Script")
        self.txt_progressive = tk.Text(tab2, bg=THEME_ELEV, fg=THEME_TEXT, insertbackground=THEME_TEXT, wrap="none", font=mono, padx=8, pady=6, height=20)
        self.txt_progressive.pack(fill="both", expand=True)
        psv_scroll = ttk.Scrollbar(tab2, orient="vertical", command=self.txt_progressive.yview)
        self.txt_progressive.configure(yscrollcommand=psv_scroll.set)
        psv_scroll.pack(side="right", fill="y")
        prog_btns = ttk.Frame(tab2)
        prog_btns.pack(fill="x", pady=4)
        ttk.Button(prog_btns, text="Promote to Repo", command=self._inject_progressive_scripts, style="Purple.TButton").pack(side="left", padx=4)
        ttk.Button(prog_btns, text="Archive Current Version", command=self._archive_current_progressive, style="Secondary.TButton").pack(side="left", padx=4)
        # Project Summary tab
        tab3 = ttk.Frame(self.nb)
        self.nb.add(tab3, text="Project Summary")
        self.txt_overview = tk.Text(tab3, bg=THEME_ELEV, fg=THEME_TEXT, insertbackground=THEME_TEXT, wrap="word", font=mono, padx=8, pady=6)
        self.txt_overview.pack(fill="both", expand=True)
        ov_scroll = ttk.Scrollbar(tab3, orient="vertical", command=self.txt_overview.yview)
        self.txt_overview.configure(yscrollcommand=ov_scroll.set)
        ov_scroll.pack(side="right", fill="y")
        # Diff tools
        diff = ttk.Labelframe(center, text="Diff Tools", padding=6)
        diff.pack(fill="x", pady=(6, 2))
        self.include_diff = tk.BooleanVar(value=False)
        ttk.Checkbutton(diff, text="Include Diff", variable=self.include_diff).pack(side="left", padx=(0, 8))
        ttk.Button(diff, text="Paste from Clipboard", command=self._paste_diff_clip, style="Secondary.TButton").pack(side="left", padx=4)
        ttk.Button(diff, text="Fetch Git diff (local)", command=self._fetch_local_diff, style="Secondary.TButton").pack(side="left", padx=4)
        ttk.Button(diff, text="Init Git Repo", command=self._init_git_repo, style="Secondary.TButton").pack(side="left", padx=4)
        ttk.Button(diff, text="Fetch GitHub Compare", command=self._fetch_github_compare, style="Secondary.TButton").pack(side="left", padx=4)
        ttk.Button(diff, text="Ingest Repo to Dataset", command=self._ingest_repo, style="Secondary.TButton").pack(side="left", padx=4)
        self.txt_diff = tk.Text(center, height=6, bg=THEME_ELEV, fg=THEME_TEXT, insertbackground=THEME_TEXT, font=mono, wrap="none", padx=8, pady=6)
        self.txt_diff.pack(fill="x")
        # Status
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status).pack(side="bottom", fill="x", padx=6, pady=3)
        # Initialize Sync button state
        self._update_sync_state()
        self._populate_launch_scripts()

    def _populate_launch_scripts(self):
        if not self.current_project:
            return
        scripts = []
        for cur, dirs, files in os.walk(self.current_project):
            for f in files:
                if f.endswith(".py"):
                    scripts.append(f)
        self.cmb_launch_script["values"] = sorted(scripts)
        cfg = self._proj_cfg()
        self.cmb_launch_script.set(cfg.get("launch_script", "main.py"))

    def _set_launch_script(self):
        if not self.current_project:
            return
        f = askopenfilename(initialdir=self.current_project, filetypes=[("Python", "*.py")])
        if f:
            self.cmb_launch_script.set(os.path.basename(f))
            cfg = self._proj_cfg()
            cfg["launch_script"] = os.path.basename(f)
            self._save_config()

    def _test_launch(self):
        if not self.current_project:
            return
        script = self.cmb_launch_script.get()
        if not script:
            return
        version_id = time.strftime("%Y%m%d_%H%M%S")
        self._log_step(f"Test launching {script}...")
        error_dir = Path(self.current_project) / UPDATE_WS_NAME / "errors"
        error_dir.mkdir(parents=True, exist_ok=True)
        error_path = error_dir / f"errors_v{version_id}.txt"
        try:
            with open(error_path, "w", encoding="utf-8") as err_f:
                proc = subprocess.Popen(["python", script], cwd=self.current_project, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in iter(proc.stdout.readline, ''):
                    err_f.write(line)
                    if "error" in line.lower() or "exception" in line.lower():
                        self._log_error(line.strip())
                        self._store_error("runtime", line.strip(), "", script, None, "new", version_id)
                proc.wait()
            if proc.returncode != 0:
                self._log_error(f"Script crashed with code {proc.returncode}")
                self._store_error("crash", f"Return code {proc.returncode}", "", script, None, "new", version_id)
            else:
                self._log_success("Script launched without crash.")
            # Parse log for more errors
            with open(error_path, "r", encoding="utf-8") as f:
                log = f.read()
            for match in re.finditer(r"(Error|Exception): (.*)", log, re.I | re.M):
                self._store_error(match.group(1), match.group(2), "", script, None, "new", version_id)
        except Exception as e:
            self._log_error(f"Launch failed: {e}")
            self._store_error("launch", str(e), "", script, None, "new", version_id)

    def _mark_stable(self):
        if not self.current_db:
            return
        with self.db_lock:
            c = self.current_db.cursor()
            c.execute("UPDATE errors SET status = 'stable' WHERE status = 'new'")
            self.current_db.commit()
        self._log_success("Marked as stable.")

    def _store_error(self, type: str, msg: str, tb: str, path: str, line: Optional[int] = None, status: str = "new", version: str = ""):
        if not self.current_db:
            return
        with self.db_lock:
            c = self.current_db.cursor()
            c.execute(
                "INSERT INTO errors (session_id, script, timestamp, type, message, traceback, path, line, status, version_tag) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (version, path, time.time(), type, msg, tb, path, line, status, version)
            )
            self.current_db.commit()

    def _get_current_errors(self):
        if not self.current_db:
            return ""
        with self.db_lock:
            c = self.current_db.cursor()
            c.execute("SELECT * FROM errors WHERE status = 'new' ORDER BY timestamp DESC LIMIT 10")
            errs = []
            for row in c.fetchall():
                errs.append(f"Error: {row[4]} - {row[5]} at {row[7]}:{row[8]}")  # type, message, path, line
        return "\n".join(errs)

    def _get_errors(self, include_archived: bool = False):
        if not self.current_db:
            return ""
        with self.db_lock:
            c = self.current_db.cursor()
            if include_archived:
                c.execute("SELECT * FROM errors ORDER BY timestamp DESC LIMIT 20")
            else:
                c.execute("SELECT * FROM errors WHERE status = 'new' ORDER BY timestamp DESC LIMIT 10")
            errs = []
            for row in c.fetchall():
                prefix = "Past error: " if row[9] != "new" else ""
                errs.append(f"{prefix}Error: {row[4]} - {row[5]} at {row[7]}:{row[8]}")
        return "\n".join(errs)

    # ---------- Streaming console helpers ----------
    def _console_write(self, msg: str, level: str = "INFO"):
        """Insert a console line with color tag based on level."""
        try:
            self.console.configure(state="normal")
            # Try to detect level from message like "[HH:MM:SS] LEVEL: ..."
            m = re.search(r"\]\s+([A-Z]+):\s", msg)
            tag = level.upper() if not m else m.group(1)
            if tag not in {"INFO", "WARN", "ERROR", "DEBUG"}:
                tag = level.upper()
            if tag == "DEBUG":
                tag = "MUTED"
            ts = time.strftime("%H:%M:%S")
            self.console.insert("end", f"[{ts}] ", ("MUTED",))
            self.console.insert("end", msg.split("] ", 1)[-1] + "\n", (tag,))
            self.console.see("end")
        finally:
            self.console.configure(state="disabled")

    def _console_line(self, text: str, tag: str):
        """Directly write a line with a specific tag (STEP/PROGRESS/SUCCESS/WARN/ERROR/INFO)."""
        try:
            self.console.configure(state="normal")
            ts = time.strftime("%H:%M:%S")
            self.console.insert("end", f"[{ts}] ", ("MUTED",))
            self.console.insert("end", text + "\n", (tag,))
            self.console.see("end")
        finally:
            self.console.configure(state="disabled")

    def _log_step(self, text: str):
        self._console_line(f"STEP: {text}", "STEP")

    def _log_progress(self, text: str):
        self._console_line(f"PROGRESS: {text}", "PROGRESS")

    def _log_success(self, text: str):
        self._console_line(f"SUCCESS: {text}", "SUCCESS")

    def _log_warn(self, text: str):
        self._console_line(f"WARN: {text}", "WARN")

    def _log_error(self, text: str):
        self._console_line(f"ERROR: {text}", "ERROR")

    def _clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    # ---------- Refresh helpers ----------
    def _refresh_all_views(self):
        """Refresh Explorer, PDD list, and force UI to repaint."""
        self._populate_explorer()
        self._populate_pdd_list()
        try:
            self._on_tree_select()
        except Exception:
            pass
        self.root.update_idletasks()
        self._status("Views refreshed")

    # ---------- Sync & Summary features ----------
    def _update_sync_state(self):
        content = self.txt_pdd.get("1.0", "end").strip()
        state = "normal" if not content else "disabled"
        self.btn_sync.configure(state=state)

    def _sync_to_project(self):
        """Generate initial PDD from entire project data."""
        if not self.current_project:
            return
        self._status("Syncing project to PDD…")
        self._log_step("Scanning project files for initial PDD generation…")
        info_dir = Path(self.current_project) / UPDATE_WS_NAME
        texts = []
        if info_dir.exists():
            files = list(info_dir.rglob("*.*"))
            total = len(files)
            self._log_progress(f"Found {total} files in {UPDATE_WS_NAME} for context.")
            for i, p in enumerate(files, 1):
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                    texts.append(f"[FILE:{p.relative_to(self.current_project)}]\n{txt}")
                except Exception:
                    pass
                if i % 25 == 0:
                    self._log_progress(f"Ingested {i}/{total} metadata files…")
        walked = []
        for cur, dirs, files in os.walk(self.current_project):
            for skip in (".git", "venv", UPDATE_WS_NAME):
                if skip in dirs:
                    dirs.remove(skip)
            for f in files:
                if f in ("pdd.txt", "index.json", "conversation.db"):
                    continue
                try:
                    p = Path(cur) / f
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                    texts.append(f"[FILE:{p.relative_to(self.current_project)}]\n{txt}")
                    walked.append(p)
                except Exception:
                    pass
        self._log_progress(f"Collected {len(walked)} additional project files.")
        prompt = self.prompts["project_sync"]
        merged = "\n\n".join(texts[-10:])
        errors = self._get_current_errors()
        self._log_step("Invoking text model for PDD synthesis…")
        out = call_ollama_chat(self.config["ollama_model_text"], f"{prompt}\nErrors:\n{errors}\n\nDATA:\n{merged}", timeout=120)
        if out.startswith("Error:"):
            self._log_error("Text model unavailable; initial PDD sync aborted. Start Ollama and retry.")
            return
        self.txt_pdd.delete("1.0", "end")
        self.txt_pdd.insert("end", out)
        self._on_pdd_edit()
        self._save_pdd()
        self._status("Project synced to PDD")
        self._add_msg(f"[SYNC_PDD]\n{out}")
        self._log_success("PDD updated from project snapshot.")
        self._update_sync_state()
        self._refresh_all_views()

    def _summarize_project(self):
        """Generate static overview summary in the Summary tab."""
        if not self.current_project:
            return
        self._status("Generating project overview…")
        self._log_step("Composing project overview from current PDD and design docs…")
        prompt = self.prompts["project_overview"]
        pdd = self.txt_pdd.get("1.0", "end").strip()
        data = f"PDD:\n{pdd}\n\n"
        info_dir = Path(self.current_project) / UPDATE_WS_NAME
        snippets = []
        if info_dir.exists():
            files = list(info_dir.rglob("*.*"))
            for p in files[-50:]:
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")[:2000]
                    snippets.append(f"[FILE:{p.relative_to(self.current_project)}]\n{txt}")
                except Exception:
                    pass
        data += "\n\n".join(snippets[-5:])
        errors = self._get_current_errors()
        out = call_ollama_chat(self.config["ollama_model_text"], f"{prompt}\nErrors:\n{errors}\n\nDATA:\n{data}", timeout=90)
        if out.startswith("Error:"):
            self._log_error("Text model unavailable; project overview aborted. Start Ollama and retry.")
            return
        self.txt_overview.delete("1.0", "end")
        self.txt_overview.insert("end", out)
        self._add_msg(f"[OVERVIEW]\n{out}")
        self._status("Project overview ready")
        self._log_success("Project overview generated.")
        self.nb.select(self.txt_overview.master)

    # ---------- Repository methods ----------
    def _delete_repository(self):
        """Clears the entire contents of the linked repository folder (including nested hidden .git)."""
        if not self.current_project:
            return
        repo = Path(self.current_project) / UPDATE_WS_NAME / REPO_FOLDER
        if not repo.exists():
            messagebox.showinfo("Delete Repository", "No repository linked.")
            return
        if not messagebox.askyesno("Delete Repository", f"Clear ALL contents under:\n{repo}\n\nThis removes nested .git folders too. Continue?"):
            return
        self._log_step(f"Wiping repository contents at {repo} …")
        wipe_directory_contents(repo)
        self._status("Repository contents cleared")
        self._log_success("Repository folder emptied (including hidden .git).")
        self._refresh_all_views()

    def _prompt_repo_settings_if_needed(self) -> Optional[Dict[str, str]]:
        """Ask for repo URL/branch if not set; persist."""
        cfg = self._proj_cfg()
        changed = False
        if not cfg.get("repo_url") and not cfg.get("desktop_link"):
            url = simpledialog.askstring("Repository URL", "Paste Git URL or 'Open in Desktop' link:\n(e.g. https://github.com/owner/repo.git or x-github-client://openRepo/...)")
            if not url:
                return None
            if url.startswith("x-github-client://"):
                cfg["desktop_link"] = url
                m = re.search(r"x-github-client://openRepo/(.+)$", url)
                if m:
                    cfg["repo_url"] = m.group(1)
            else:
                cfg["repo_url"] = url
            changed = True
        if not cfg.get("repo_branch"):
            br = simpledialog.askstring("Branch", "Branch name to pull (single-branch):", initialvalue="main")
            if not br:
                return None
            cfg["repo_branch"] = br
            changed = True
        if changed:
            self._save_config()
        return {"url": cfg.get("repo_url", ""), "branch": cfg["repo_branch"], "desktop_link": cfg.get("desktop_link", "")}

    def _open_in_github_desktop(self, repo_path: Path, desktop_link: str = ""):
        """Open GitHub Desktop for the repo (best-effort)."""
        self._log_step("Opening repository in GitHub Desktop…")
        try:
            subprocess.Popen(["github", str(repo_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass
        try:
            if platform.system() == "Windows":
                exe = Path(os.getenv("LOCALAPPDATA", "")) / "GitHubDesktop" / "GitHubDesktop.exe"
                if exe.exists():
                    subprocess.Popen([str(exe), f"--open-repository={repo_path}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
        except Exception:
            pass
        try:
            if desktop_link:
                if platform.system() == "Windows":
                    os.startfile(desktop_link)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", desktop_link])
                else:
                    subprocess.Popen(["xdg-open", desktop_link])
        except Exception:
            pass

    def _ensure_cloned_here(self, settings: Dict[str, str]) -> Optional[Path]:
        """Ensure the repo is cloned under UPDATE_WS_NAME/repository/<name> (single-branch)."""
        repo_root = Path(self.current_project) / UPDATE_WS_NAME / REPO_FOLDER
        repo_root.mkdir(parents=True, exist_ok=True)
        inner = self._resolve_inner_repo(repo_root)
        if git_is_repo(str(inner)):
            return inner
        default_name = "repo"
        url = settings["url"]
        if url and "/" in url:
            default_name = re.sub(r"\.git$", "", url.rstrip("/").split("/")[-1])
        name = simpledialog.askstring("Folder name", "Folder name for local clone:", initialvalue=default_name)
        if not name:
            return None
        target = repo_root / name
        target.mkdir(parents=True, exist_ok=True)
        branch = settings["branch"]
        self._log_step(f"Cloning {url} (branch {branch})…")
        code, out, err = run_git(["clone", "--single-branch", "--branch", branch, url, "."], cwd=str(target))
        if code != 0:
            messagebox.showerror("Clone failed", err or out or "Unknown error")
            self._log_error(f"Clone failed: {err or out or 'Unknown error'}")
            return None
        self._enforce_single_branch(target, branch)
        self._status(f"Cloned repo into {target.name}")
        self._log_success(f"Cloned into {target}.")
        return target

    def _pull_repo(self):
        """Pull latest from configured single branch; open GitHub Desktop if enabled."""
        if not self.current_project:
            return
        settings = self._prompt_repo_settings_if_needed()
        if not settings:
            return
        repo_root = Path(self.current_project) / UPDATE_WS_NAME / REPO_FOLDER
        target = self._resolve_inner_repo(repo_root)
        if not git_is_repo(str(target)):
            self._log_warn("No repo found—launching controlled clone flow.")
            target = self._ensure_cloned_here(settings)
            if not target:
                return
        self._log_step(f"Configuring single-branch tracking for '{settings['branch']}' …")
        self._enforce_single_branch(target, settings["branch"])
        self._log_step("Pulling from remote (ff-only)…")
        code, out, err = run_git(["pull", "--ff-only"], cwd=str(target))
        if code != 0:
            messagebox.showerror("Pull Repo", err or out or "Unknown error")
            self._log_error(f"Pull failed: {err or out or 'Unknown error'}")
        else:
            self._status(f"Repository updated from remote (branch {settings['branch']}).")
            self._log_success(f"Pulled latest on '{settings['branch']}'.")
        if self.use_desktop.get():
            self._open_in_github_desktop(target, settings.get("desktop_link", ""))
        # Get commit hash for version
        code, commit, _ = run_git(["rev-parse", "HEAD"], cwd=str(target))
        if code == 0:
            cfg = self._proj_cfg()
            cfg["repo_commit"] = commit.strip()
            self._save_config()
        self._refresh_all_views()

    def _enforce_single_branch(self, repo_path: Path, branch: str):
        """Configure repo to track ONLY the given branch and prune others locally."""
        run_git(["config", "--unset-all", "remote.origin.fetch"], cwd=str(repo_path))
        run_git(["config", "remote.origin.fetch", f"+refs/heads/{branch}:refs/remotes/origin/{branch}"], cwd=str(repo_path))
        run_git(["fetch", "--prune", "origin"], cwd=str(repo_path))
        run_git(["checkout", "-B", branch, f"origin/{branch}"], cwd=str(repo_path))
        code, out, _ = run_git(["for-each-ref", "--format=%(refname:short)", "refs/heads"], cwd=str(repo_path))
        if code == 0:
            for br in out.splitlines():
                br = br.strip()
                if br and br != branch:
                    run_git(["branch", "-D", br], cwd=str(repo_path))

    def _update_repo_with_progressive(self):
        """Ask (checkboxes) what to send; commit and push to configured branch. Wipes targets first."""
        if not self.current_project:
            return
        settings = self._prompt_repo_settings_if_needed()
        if not settings:
            return
        repo_root = Path(self.current_project) / UPDATE_WS_NAME / REPO_FOLDER
        target = self._resolve_inner_repo(repo_root)
        if not git_is_repo(str(target)):
            messagebox.showerror("Update Repo", "No valid Git repository in project. Use Pull Repo to clone first.")
            self._log_error("Update aborted: no valid git repository found.")
            return
        # Load per-project defaults and tailor by Task Type for initial UX
        cfg = self._proj_cfg()
        defaults = cfg.get("update_repo_options", {}).copy()
        if self.task_type.get() == "Coding":
            defaults.setdefault("include_scripts", True)
            defaults.setdefault("include_design", False)
            defaults.setdefault("include_info", False)
            defaults.setdefault("include_burner_lists", False)
            defaults.setdefault("include_burner_scripts", True)
        else:
            defaults.setdefault("include_scripts", True)
            defaults.setdefault("include_design", True)
            defaults.setdefault("include_info", False)
            defaults.setdefault("include_burner_lists", False)
            defaults.setdefault("include_burner_scripts", False)
        dlg = UpdateRepoDialog(self.root, settings["branch"], defaults)
        self.root.wait_window(dlg)
        if not dlg.ok:
            self._log_warn("Update cancelled by user.")
            return
        # Persist dialog choices per project
        cfg["update_repo_options"] = {
            "include_scripts": bool(dlg.include_scripts.get()),
            "include_design": bool(dlg.include_design.get()),
            "include_info": bool(dlg.include_info.get()),
            "include_burner_lists": bool(dlg.include_burner_lists.get()),
            "include_burner_scripts": bool(dlg.include_burner_scripts.get()),
            "commit_direct": bool(dlg.commit_direct.get()),
            "commit_message": dlg.commit_message.get().strip() or "Update from Rant_PDD",
        }
        self._save_config()
        self._log_step("Preparing files to stage (wipe/save mode)…")
        copied_count = 0
        if cfg["update_repo_options"]["include_scripts"]:
            c = self._copy_progressive_archives_into_repo(target)
            self._log_progress(f"Progressive scripts copied: {c}")
            copied_count += c
        if cfg["update_repo_options"]["include_design"]:
            c = self._copy_design_documents_into_repo(target)
            self._log_progress(f"Design_Documents copied: {c}")
            copied_count += c
        if cfg["update_repo_options"]["include_info"]:
            c = self._copy_project_info_into_repo(target)
            self._log_progress(f"Info package copied: {c}")
            copied_count += c
        if cfg["update_repo_options"]["include_burner_lists"]:
            c = self._copy_burner_lists_into_repo(target)
            self._log_progress(f"Burner lists copied: {c}")
            copied_count += c
        if cfg["update_repo_options"]["include_burner_scripts"]:
            c = self._copy_burner_scripts_into_repo(target)
            self._log_progress(f"Burner scripts copied: {c}")
            copied_count += c
        run_git(["add", "-A"], cwd=str(target))
        commit_msg = cfg["update_repo_options"]["commit_message"]
        branch = settings["branch"]
        if self.single_branch_only.get() and cfg["update_repo_options"]["commit_direct"]:
            self._log_step(f"Committing directly to '{branch}' (single-branch mode)…")
            self._enforce_single_branch(target, branch)
        else:
            branch = f"update_{time.strftime('%Y-%m-%d_%H%M')}"
            self._log_warn(f"Creating safety branch '{branch}' for update…")
            run_git(["checkout", "-b", branch], cwd=str(target))
        code, out, err = run_git(["commit", "-m", commit_msg], cwd=str(target))
        if code != 0 and "nothing to commit" in (out + err).lower():
            self._status("No changes to commit.")
            self._log_warn("No changes to commit.")
        elif code != 0:
            messagebox.showerror("Commit failed", err or out or "Unknown")
            self._log_error(f"Commit failed: {err or out or 'Unknown'}")
            return
        else:
            self._log_success("Local commit created.")
        self._log_step(f"Pushing branch '{branch}' to origin…")
        run_git(["push", "-u", "origin", branch], cwd=str(target))
        self._status(f"Updated repository ({copied_count} files) on branch '{branch}'.")
        self._log_success(f"Pushed updates to remote on '{branch}'.")
        if self.use_desktop.get():
            self._open_in_github_desktop(target, settings.get("desktop_link", ""))
        self._refresh_all_views()

    def _resolve_inner_repo(self, repo_root: Path) -> Path:
        """Return the actual git working dir beneath UPDATE_WS_NAME/repository."""
        if (repo_root / ".git").exists():
            return repo_root
        for child in repo_root.iterdir():
            if child.is_dir() and (child / ".git").exists():
                return child
        return repo_root

    # === Wipe/Save copy helpers ===
    def _copy_progressive_archives_into_repo(self, repo_dir: Path) -> int:
        """ Wipe repo/_progressive then copy ALL progressive *.py files from every module's Design_Documents/<module>/progressive_scripts/ into matching subfolders. """
        dest_root = repo_dir / "_progressive"
        if dest_root.exists():
            shutil.rmtree(dest_root, onerror=_on_rm_error)
        dest_root.mkdir(parents=True, exist_ok=True)
        copied = 0
        dd_root = Path(self.current_project) / "Design_Documents"
        if not dd_root.exists():
            return copied
        for module_dir in sorted([d for d in dd_root.iterdir() if d.is_dir()]):
            psv_dir = module_dir / "progressive_scripts"
            if not psv_dir.exists():
                continue
            dst_mod = dest_root / module_dir.name
            dst_mod.mkdir(parents=True, exist_ok=True)
            for py in sorted(psv_dir.glob("*.py")):
                shutil.copy(py, dst_mod / py.name)
                copied += 1
        return copied

    def _copy_design_documents_into_repo(self, repo_dir: Path) -> int:
        """Wipe repo/_design_docs then copy Design_Documents (files only, preserving structure)."""
        src = Path(self.current_project) / "Design_Documents"
        dst = repo_dir / "_design_docs"
        if dst.exists():
            shutil.rmtree(dst, onerror=_on_rm_error)
        copied = 0
        if src.exists():
            for p in src.rglob("*"):
                if p.is_dir():
                    continue
                rel = p.relative_to(src)
                outp = dst / rel
                outp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(p, outp)
                copied += 1
        return copied

    def _copy_project_info_into_repo(self, repo_dir: Path) -> int:
        """ Wipe repo/_info then copy project_info except the 'repository' subfolder to avoid recursion. """
        src = Path(self.current_project) / UPDATE_WS_NAME
        dst = repo_dir / "_info"
        if dst.exists():
            shutil.rmtree(dst, onerror=_on_rm_error)
        copied = 0
        if src.exists():
            for p in src.rglob("*"):
                if REPO_FOLDER in p.parts:
                    continue
                if p.is_dir():
                    continue
                rel = p.relative_to(src)
                outp = dst / rel
                outp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(p, outp)
                copied += 1
        return copied

    def _copy_burner_lists_into_repo(self, repo_dir: Path) -> int:
        dst = repo_dir / "_burner_lists"
        if dst.exists():
            shutil.rmtree(dst, onerror=_on_rm_error)
        copied = 0
        src = Path(self.current_project) / "burner_lists"
        if src.exists():
            dst.mkdir(parents=True, exist_ok=True)
            for f in src.glob("*"):
                if f.is_file():
                    shutil.copy(f, dst / f.name)
                    copied += 1
        return copied

    def _copy_burner_scripts_into_repo(self, repo_dir: Path) -> int:
        dst = repo_dir / "_burner_scripts"
        if dst.exists():
            shutil.rmtree(dst, onerror=_on_rm_error)
        copied = 0
        src = Path(self.current_project) / "burner_scripts"
        if src.exists():
            dst.mkdir(parents=True, exist_ok=True)
            for f in src.glob("*.txt"):
                shutil.copy(f, dst / f.name)
                copied += 1
        return copied

    # ---------- Repo sync to dataset / PDD ----------
    def _sync_repository(self):
        """ Public entrypoint — run sync in a worker thread so the UI stays responsive and the System Console streams progress lines even if Ollama is down. """
        if not self.current_project:
            return
        self._log_step("Starting repository sync (threaded)…")
        threading.Thread(target=self._sync_repository_worker, daemon=True).start()

    def _sync_repository_worker(self):
        version_id = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            self._status(f"Syncing repository (version {version_id})…")
            self._log_step(f"Scanning repository @ {version_id} …")
            repo_dir = Path(self.current_project) / UPDATE_WS_NAME / REPO_FOLDER
            actual_repo = self._resolve_inner_repo(repo_dir)
            if not actual_repo.exists():
                messagebox.showinfo("Sync Repository", "No repository linked yet.")
                self._log_warn("Sync aborted: no repository linked.")
                return
            files = [p for p in actual_repo.rglob("*.*") if ".git" not in p.parts]
            self._log_progress(f"Found {len(files)} files to ingest…")
            started = time.time()
            last_tick = started
            for i, file in enumerate(files, 1):
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                em = embed(content, self.config["embedding_model"])
                if self.current_db:
                    with self.db_lock:
                        c = self.current_db.cursor()
                        c.execute(
                            "INSERT INTO messages (text, embedding, timestamp) VALUES (?,?,?)",
                            (f"[REPO:{file.relative_to(self.current_project)}|ver:{version_id}]\n{content[:5000]}", json.dumps(em) if em else None, time.time())
                        )
                        self.current_db.commit()
                now = time.time()
                if now - last_tick > 0.35:
                    self._log_progress(f"Ingested {i}/{len(files)} files…")
                    last_tick = now
            # Generate/update PDD + Burner List per .py file
            py_files = [p for p in actual_repo.rglob("*.py") if ".git" not in p.parts]
            self._log_step(f"Generating module PDDs from {len(py_files)} Python files…")
            errors = self._get_errors(include_archived=True)
            for j, py in enumerate(py_files, 1):
                try:
                    code = py.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                name = py.stem
                pdd_folder = Path(self.current_project) / "Design_Documents" / name
                pdd_folder.mkdir(parents=True, exist_ok=True)
                self._log_progress(f"[{j}/{len(py_files)}] Summarizing {py.name} → {name}/pdd.txt …")
                summary = call_ollama_chat(
                    self.config["ollama_model_text"],
                    f"# Repository Version: {version_id}\n\n"
                    f"{self.prompts['project_sync']}\nErrors:\n{errors}\n\nDATA:\n{code[:2000]}",
                    timeout=120
                )
                if summary.startswith("Error:"):
                    self._log_error("Text model unavailable; skipping module summaries. Start Ollama and re-run sync.")
                    break
                versioned_pdd = (
                    f"# Repository Version: {version_id}\n\n"
                    f"{summary}\n\n"
                    "NOTE: All prior summaries are from earlier repository versions."
                )
                (pdd_folder / "pdd.txt").write_text(versioned_pdd, encoding="utf-8")
                # Maintain Burner List (legacy / backward compatibility)
                bl = Path(self.current_project) / "burner_lists" / f"{name}_burner_list.txt"
                if not bl.exists():
                    self._initialize_burner_list(bl, code, version_id, name)
                else:
                    self._append_burner_version(bl, code, version_id, name)
            self._generate_project_summary(version_id)
            self._status(f"Repository synced to version {version_id}")
            self._log_success("Repository sync complete.")
            self._refresh_all_views()
        except Exception as e:
            logger.error("Sync repository error: %s", e)
            self._status(f"Sync error: {e}")
            self._log_error(f"Sync error: {e}")

    # ---------- Burner List helpers (legacy) ----------
    def _initialize_burner_list(self, path: Path, code: str, version_id: str, module_name: str):
        header = (
            f"# BURNER LIST: {module_name}\n"
            f"# Linked PDD: Design_Documents/{module_name}/pdd.txt\n"
            f"# Created: {time.strftime('%Y-%m-%d')}\n"
            f"# Repository Version: {version_id}\n"
            f"# Total Versions: 1\n\n"
        )
        block = f"--- VERSION 1 START ---\n{code}\n--- VERSION 1 END ---\n"
        path.write_text(header + block, encoding="utf-8")
        burner_txt = Path(self.current_project) / "burner_scripts" / f"{module_name}.txt"
        burner_txt.write_text(code, encoding="utf-8")

    def _append_burner_version(self, path: Path, new_code: str, version_id: str, module_name: str):
        text = path.read_text(encoding="utf-8")
        try:
            last_start = text.rfind("--- VERSION ")
            last_block = text[last_start:]
            old_code = last_block.split("START ---\n", 1)[1].split("\n--- VERSION", 1)[0]
        except Exception:
            old_code = ""
        diff_txt = "\n".join(
            difflib.unified_diff(
                old_code.splitlines(),
                new_code.splitlines(),
                fromfile="prev.py",
                tofile="curr.py",
                lineterm=""
            )
        )
        try:
            header, body = text.split("\n\n", 1)
            total_line_idx = [i for i, ln in enumerate(header.splitlines()) if ln.startswith("# Total Versions:")][0]
            header_lines = header.splitlines()
            total = int(header_lines[total_line_idx].split(":")[1].strip())
            header_lines[total_line_idx] = f"# Total Versions: {total + 1}"
            for i, ln in enumerate(header_lines):
                if ln.startswith("# Repository Version:"):
                    header_lines[i] = f"# Repository Version: {version_id}"
            header = "\n".join(header_lines)
        except Exception:
            header, body = text, ""
            total = 1
        v_next = (total + 1)
        block = (
            f"\n--- VERSION {v_next} START ---\n{new_code}\n"
            f"--- DIFF FROM VERSION {v_next-1} ---\n{diff_txt}\n"
            f"--- VERSION {v_next} END ---\n"
        )
        path.write_text(header + "\n\n" + body + block, encoding="utf-8")
        burner_txt = Path(self.current_project) / "burner_scripts" / f"{module_name}.txt"
        burner_txt.write_text(new_code, encoding="utf-8")

    # ---------- Progressive Script helpers ----------
    def _current_selected_module(self) -> str:
        sel = self.pdd_list.curselection()
        if sel:
            return self.pdd_list.get(sel[0])
        return "General"

    def _pdd_hash(self) -> str:
        pdd_text = self.txt_pdd.get("1.0", "end")
        return hashlib.sha256(pdd_text.encode("utf-8")).hexdigest()[:12]

    def _make_progressive_header(self, model_used: str) -> str:
        return (
            f"# Progressive Script Archive\n"
            f"# Project: {os.path.basename(self.current_project or '')}\n"
            f"# Module: {self._current_selected_module()}\n"
            f"# Version Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"# PDD Hash: {self._pdd_hash()}\n"
            f"# Model: {model_used}\n"
            f"# Note: Generated by DeepSeek Progressive flow. Review before merge.\n\n"
        )

    def _archive_current_progressive(self):
        """Archive current Progressive Script text into module archive folder with metadata."""
        if not self.current_project:
            return
        ps_text = self.txt_progressive.get("1.0", "end").strip()
        if not ps_text:
            self._status("No Progressive Script content to archive")
            self._log_warn("Archive skipped: Progressive Script editor is empty.")
            return
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        mod_name = self._current_selected_module()
        out_dir = Path(self.current_project) / "Design_Documents" / mod_name / "progressive_scripts"
        out_dir.mkdir(parents=True, exist_ok=True)
        model_used = self.config.get("ollama_model_coding", "deepseek-coder-v2:16b")
        header = self._make_progressive_header(model_used)
        out_file = out_dir / f"version_{timestamp}.py"
        out_file.write_text(header + ps_text + "\n", encoding="utf-8")
        latest_prev = self._latest_progressive_file(out_dir, before=timestamp)
        if latest_prev:
            try:
                prev_txt = Path(latest_prev).read_text(encoding="utf-8").splitlines()
                curr_txt = (header + ps_text + "\n").splitlines()
                diff_txt = "\n".join(difflib.unified_diff(prev_txt, curr_txt, fromfile=Path(latest_prev).name, tofile=out_file.name, lineterm=""))
                (out_dir / f"diff_{timestamp}.txt").write_text(diff_txt, encoding="utf-8")
            except Exception:
                pass
        self._status(f"Progressive script archived: {out_file.name}")
        self._log_success(f"Archived Progressive Script → {out_file}")
        self._refresh_all_views()

    def _latest_progressive_file(self, psv_dir: Path, before: Optional[str] = None) -> Optional[Path]:
        """Return the latest version_*.py under psv_dir; optionally only those < before timestamp."""
        if not psv_dir.exists():
            return None
        files = sorted([p for p in psv_dir.glob("version_*.py") if p.is_file()])
        if before:
            files = [p for p in files if p.stem.split("_", 1)[1] < before]
        return files[-1] if files else None

    def _inject_progressive_scripts(self):
        """Archive current Progressive Script and copy ALL progressive scripts into repo/_progressive; does not commit."""
        if not self.current_project:
            return
        self._log_step("Archiving current Progressive Script…")
        self._archive_current_progressive()
        self._log_step("Copying ALL Progressive Scripts into repo working directory (wipe/save)…")
        repo_root = Path(self.current_project) / UPDATE_WS_NAME / REPO_FOLDER
        target = self._resolve_inner_repo(repo_root)
        if not target.exists():
            self._status("No repository linked—archived only. Use Pull Repo to link a repo.")
            self._log_warn("Promotion skipped: no repository linked.")
            return
        copied = self._copy_progressive_archives_into_repo(target)
        self._status(f"Promoted Progressive Scripts → repo/_progressive ({copied} files). Use 'Update Repo' to commit.")
        self._log_success(f"Promotion complete: {copied} file(s) staged in _progressive/")
        self._refresh_all_views()

    # ---------- Project Summary helpers ----------
    def _generate_project_summary(self, version_id: str):
        self._log_step("Composing project summary across modules…")
        prompt = self.prompts["project_overview"]
        pdds = []
        dd_root = Path(self.current_project) / "Design_Documents"
        if dd_root.exists():
            for d in dd_root.iterdir():
                if d.is_dir() and (d / "pdd.txt").exists():
                    pdds.append(f"### {d.name}\n\n" + (d / "pdd.txt").read_text(encoding="utf-8"))
        merged = "\n\n".join(pdds[-10:])
        errors = self._get_errors(include_archived=True)
        overview = call_ollama_chat(
            self.config["ollama_model_text"],
            f"# Project Summary – Version {version_id}\n\n{prompt}\nErrors:\n{errors}\n\nDATA:\n{merged}",
            timeout=90
        )
        if overview.startswith("Error:"):
            self._log_error("Text model unavailable; project summary skipped.")
            return
        versioned = (
            f"# Project Summary – Version {version_id}\n\n"
            f"{overview}\n\n"
            "NOTE: All prior summaries are from earlier repository versions."
        )
        Path(self.current_project, "project_summary.txt").write_text(versioned, encoding="utf-8")
        self._log_success("Project summary written to project_summary.txt")

    # ---------- Package for GitHub ----------
    def _package_for_github(self):
        """ Create two packages:
        • export_for_github_[ts]/Design_Documents (full tree)
        • export_generated_scripts_[ts]/<module>/*.py (ALL progressive script versions)
        Wipe both target folders before writing to avoid residuals.
        """
        if not self.current_project:
            return
        version_id = time.strftime("%Y%m%d_%H%M%S")
        repo_name = os.path.basename(self.current_project)
        out = Path(self.current_project) / f"{repo_name}_V{version_id}"
        out_gen = Path(self.current_project) / f"{repo_name}_V{version_id}_scripts"
        out.mkdir(parents=True, exist_ok=True)
        out_gen.mkdir(parents=True, exist_ok=True)
        self._log_step(f"Preparing export packages {out.name} and {out_gen.name} (wipe/save) …")
        wipe_directory_contents(out)
        wipe_directory_contents(out_gen)
        cfg = self._proj_cfg()
        defaults = cfg.get("package_options", {"include_design": True, "include_burner_lists": False, "include_burner_scripts": False})
        dlg = PackageDialog(self.root, defaults)
        self.root.wait_window(dlg)
        if not dlg.ok:
            self._log_warn("Packaging cancelled by user.")
            return
        package_options = {
            "include_design": bool(dlg.include_design.get()),
            "include_burner_lists": bool(dlg.include_burner_lists.get()),
            "include_burner_scripts": bool(dlg.include_burner_scripts.get()),
        }
        cfg["package_options"] = package_options
        self._save_config()
        dd_src = Path(self.current_project) / "Design_Documents"
        if package_options["include_design"] and dd_src.exists():
            shutil.copytree(dd_src, out / "Design_Documents", dirs_exist_ok=True)
        bl_src = Path(self.current_project) / "burner_lists"
        if package_options["include_burner_lists"] and bl_src.exists():
            shutil.copytree(bl_src, out / "burner_lists", dirs_exist_ok=True)
        bs_src = Path(self.current_project) / "burner_scripts"
        if package_options["include_burner_scripts"] and bs_src.exists():
            shutil.copytree(bs_src, out / "burner_scripts", dirs_exist_ok=True)
        # Always copy progressive scripts
        if dd_src.exists():
            for module_dir in sorted([d for d in dd_src.iterdir() if d.is_dir()]):
                psv = module_dir / "progressive_scripts"
                if not psv.exists():
                    continue
                dest_mod = out_gen / module_dir.name
                dest_mod.mkdir(parents=True, exist_ok=True)
                for py in sorted(psv.glob("*.py")):
                    shutil.copy(py, dest_mod / py.name)
        # Codex README
        readme = out / "README.md"
        readme.write_text("Repository export for Codex review.", encoding="utf-8")
        (out / "requirements.txt").touch(exist_ok=True)
        # Directive file
        self._ensure_codex_directive(out)
        # Version metadata
        metadata = out / "version_metadata.txt"
        metadata.write_text(
            f"# VERSION METADATA\nVersion: {version_id}\nBranch: {repo_name}_V{version_id}\nPackaged: {time.strftime('%Y-%m-%d %H:%M')}\nChanges:\n- Design docs included: {package_options['include_design']}\n- Burner lists included: {package_options['include_burner_lists']}\n- Burner scripts included: {package_options['include_burner_scripts']}",
            encoding="utf-8"
        )
        # Instructions for Codex + reference to generated scripts
        inst = out / "README_FOR_CODEX.txt"
        inst.write_text(
            f"Hello Codex,\n\n"
            f"You are Codex. Use ALL files in this folder and its subfolders to update the linked repository.\n\n"
            f"This package reflects repository version {version_id}.\n\n"
            "- Implement missing features\n"
            "- Apply PDD logic\n"
            "- Respect backward compatibility\n\n"
            f"Also see: ../{out_gen.name}/ for ALL Progressive Script versions (*.py) per module.\n"
            "All content is structured for implementation. Use every file.\n",
            encoding="utf-8"
        )
        # Add bot guard workflow
        workflow_dir = out / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        bot_guard = workflow_dir / "bot-guard.yml"
        bot_guard_yaml = """name: Bot Guard
on:
  pull_request:
jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: mikefarah/yq@v4
      - run: bash scripts/guard-gpt-changes.sh .gpt-guard.yaml "${{ github.event.pull_request.base.sha }}" "${{ github.event.pull_request.head.sha }}" """
        bot_guard.write_text(bot_guard_yaml, encoding="utf-8")
        self._status(f"Packaged for GitHub: {out.name} (+ {out_gen.name})")
        self._log_success("Packaging complete.")
        self._refresh_all_views()

    def _ensure_codex_directive(self, root: Path):
        file = root / "suggested_improvements_to_be_filled_out_by_codex.txt"
        if not file.exists():
            content = (
                "# DO NOT ERASE ME\n"
                "# I AM DIRECTIVES\n"
                "# Purpose:\n"
                "# This file is intended for Codex or any automated reasoning system reviewing this repository.\n"
                "# Use these directives to propose improvements.\n"
                "# Instructions:\n"
                "# 1. Analyze the entire repository, including:\n"
                "# - Source code scripts\n"
                "# - Generated burner scripts\n"
                "# - Design documents (PDDs)\n"
                "# - Version metadata\n"
                "# - Automation workflows\n"
                "# 2. Identify:\n"
                "# - Gaps or missing features\n"
                "# - Inefficiencies\n"
                "# - Logical inconsistencies\n"
                "# - Architecture issues\n"
                "# - Opportunities for automation or modernization\n"
                "# 3. Suggest improvements:\n"
                "# - What should be added, removed, or changed?\n"
                "# - How can the repository better align with its intended design?\n"
                "# - Which scripts or workflows need updates to support overall goals?\n"
                "# 4. Write your findings below in plain English, focusing on actionable changes.\n"
                "# Fill below:\n"
            )
            file.write_text(content, encoding="utf-8")

    # ---------- Explorer helpers ----------
    def _populate_explorer(self):
        self.tree.delete(*self.tree.get_children())
        if not self.current_project:
            return
        root_id = self.tree.insert("", "end", text=f"📁 {os.path.basename(self.current_project)}", open=True, values=[self.current_project])
        self._add_nodes(root_id, self.current_project, depth=0)

    def _add_nodes(self, parent, path, depth):
        try:
            for name in sorted(os.listdir(path)):
                if name.lower() in {".git", "venv"}:
                    continue
                full = os.path.join(path, name)
                icon = "📁" if os.path.isdir(full) else "📄"
                node = self.tree.insert(parent, "end", text=f"{icon} {name}", values=[full], open=(depth < 1))
                if os.path.isdir(full):
                    self._add_nodes(node, full, depth + 1)
        except Exception:
            pass

    def _on_tree_select(self):
        sel = self.tree.selection()
        if not sel:
            return
        path = self.tree.item(sel[0], "values")[0]
        self.file_view.delete("1.0", "end")
        if os.path.isdir(path):
            self.file_view.insert("end", f"[Folder] {path}")
        else:
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
                self.file_view.insert("end", text)
            except Exception as e:
                self.file_view.insert("end", f"Error: {e}")

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        path = self.tree.item(sel[0], "values")[0]
        if not messagebox.askyesno("Delete", f"Delete '{path}'? This cannot be undone."):
            return
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, onerror=_on_rm_error)
            else:
                try:
                    os.chmod(path, stat.S_IWRITE)
                except Exception:
                    pass
                Path(path).unlink(missing_ok=True)
            self._status(f"Deleted {path}")
            self._log_success(f"Deleted {path}")
        except Exception as e:
            messagebox.showerror("Delete failed", str(e))
            self._log_error(f"Delete failed: {e}")
        finally:
            self._refresh_all_views()

    # ---------- Program Design Manager helpers ----------
    def _populate_pdd_list(self):
        self.pdd_list.delete(0, tk.END)
        if not self.current_project:
            return
        dd_dir = Path(self.current_project) / "Design_Documents"
        if dd_dir.exists():
            for sub in sorted(dd_dir.iterdir()):
                if sub.is_dir():
                    self.pdd_list.insert(tk.END, sub.name)

    def _on_pdd_list_select(self):
        sel = self.pdd_list.curselection()
        if not sel:
            return
        name = self.pdd_list.get(sel[0])
        pdd_folder = Path(self.current_project) / "Design_Documents" / name
        pdd_file = pdd_folder / "pdd.txt"
        if pdd_file.exists():
            txt = pdd_file.read_text(encoding="utf-8")
            self.txt_pdd.delete("1.0", "end")
            self.txt_pdd.insert("end", txt)
            self._on_pdd_edit()
            self._status(f"Loaded PDD: {name}")
            self.nb.select(self.txt_pdd.master)
        psv_dir = pdd_folder / "progressive_scripts"
        latest = self._latest_progressive_file(psv_dir)
        if latest:
            try:
                prog_txt = Path(latest).read_text(encoding="utf-8")
                parts = re.split(r"\n\s*\n", prog_txt, maxsplit=1)
                body = parts[-1] if len(parts) > 1 else prog_txt
                self.txt_progressive.delete("1.0", "end")
                self.txt_progressive.insert("end", body)
            except Exception:
                pass
        burner_txt = Path(self.current_project) / "burner_scripts" / f"{name}.txt"
        if burner_txt.exists():
            code = burner_txt.read_text(encoding="utf-8")
            self.txt_progressive.delete("1.0", "end")
            self.txt_progressive.insert("end", code)

    def _new_pdd_subfolder(self):
        name = simpledialog.askstring("New Subfolder", "PDD Subfolder name:")
        if not name:
            return
        dd_dir = Path(self.current_project) / "Design_Documents" / name
        dd_dir.mkdir(parents=True, exist_ok=True)
        self._status(f"Created PDD subfolder: {name}")
        self._log_success(f"Created subfolder Design_Documents/{name}")
        self._refresh_all_views()

    def _delete_pdd_subfolder(self):
        sel = self.pdd_list.curselection()
        if not sel:
            return
        name = self.pdd_list.get(sel[0])
        if not messagebox.askyesno("Delete", f"Delete PDD subfolder '{name}'?"):
            return
        dd_dir = Path(self.current_project) / "Design_Documents" / name
        shutil.rmtree(dd_dir, onerror=_on_rm_error)
        self._status(f"Deleted PDD subfolder: {name}")
        self._log_success(f"Deleted subfolder Design_Documents/{name}")
        self._refresh_all_views()

    def _rename_pdd_subfolder(self):
        sel = self.pdd_list.curselection()
        if not sel:
            return
        old_name = self.pdd_list.get(sel[0])
        new_name = simpledialog.askstring("Rename", "New name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        old_dir = Path(self.current_project) / "Design_Documents" / old_name
        new_dir = Path(self.current_project) / "Design_Documents" / new_name
        try:
            old_dir.rename(new_dir)
            self._status(f"Renamed PDD subfolder: {old_name} → {new_name}")
            self._log_success(f"Renamed Design_Documents/{old_name} → {new_name}")
        except Exception as e:
            messagebox.showerror("Rename failed", str(e))
            self._log_error(f"Rename failed: {e}")
            return
        self._refresh_all_views()

    def _add_burner_script_to_selected(self):
        """Legacy flow: generate code into Burner List; also populate Progressive editor."""
        sel = self.pdd_list.curselection()
        if not sel:
            return
        name = self.pdd_list.get(sel[0])
        pdd_folder = Path(self.current_project) / "Design_Documents" / name
        pdd_text = (pdd_folder / "pdd.txt").read_text(encoding="utf-8") if (pdd_folder / "pdd.txt").exists() else ""
        self._log_step(f"Generating burner script for module {name} …")
        code = call_ollama_chat(self.config["ollama_model_coding"], self.prompts["burner_script"].format(pdd=pdd_text), timeout=90)
        if code.startswith("Error:"):
            self._log_error("Coding model unavailable; cannot generate burner script right now.")
            return
        code = self._handle_think_blocks(code, origin="BurnerScript")
        bl = Path(self.current_project) / "burner_lists" / f"{name}_burner_list.txt"
        version_id = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if not bl.exists():
            self._initialize_burner_list(bl, code, version_id, name)
        else:
            self._append_burner_version(bl, code, version_id, name)
        self.txt_progressive.delete("1.0", "end")
        self.txt_progressive.insert("end", code)
        self._status(f"Added burner script to {name} (and loaded into Progressive editor)")
        self._log_success(f"Burner script updated under burner_lists/{name}_burner_list.txt")
        self._refresh_all_views()

    # ---------- Add/Clone/Pull Repo ----------
    def _add_local_repo(self):
        if not self.current_project:
            messagebox.showwarning("Add Local Repo", "Select or create a project first.")
            return
        d = askdirectory(title="Select local repo folder", mustexist=True)
        if not d:
            return
        repo_dir = Path(self.current_project) / UPDATE_WS_NAME / REPO_FOLDER
        repo_dir.mkdir(parents=True, exist_ok=True)
        if any(repo_dir.iterdir()):
            if not messagebox.askyesno("Override Repo", "Repository already exists. Override?"):
                return
            self._log_step("Overriding existing repository folder…")
            wipe_directory_contents(repo_dir)
        name = os.path.basename(d.rstrip("/\\"))
        target = repo_dir / name
        shutil.copytree(d, target, dirs_exist_ok=True)
        self._status(f"Added local repo: {name}")
        self._log_success(f"Local repository added at {target}")
        self._refresh_all_views()

    def _clone_repo(self):
        """Legacy clone method — prefer Pull Repo (which remembers URL/branch and single-branch clones)."""
        if not self.current_project:
            messagebox.showwarning("Clone Repo", "Select or create a project first.")
            return
        url = simpledialog.askstring("Clone Repo", "Git URL:")
        if not url:
            return
        name = simpledialog.askstring("Clone Repo", "Folder name:", initialvalue="repo")
        if not name:
            return
        repo_dir = Path(self.current_project) / UPDATE_WS_NAME / REPO_FOLDER
        repo_dir.mkdir(parents=True, exist_ok=True)
        if any(repo_dir.iterdir()):
            if not messagebox.askyesno("Override Repo", "Repository already exists. Override?"):
                return
            self._log_step("Overriding existing repository folder…")
            wipe_directory_contents(repo_dir)
        target = repo_dir / name
        target.mkdir(exist_ok=True)
        self._log_step(f"Cloning {url} (no single-branch enforcement in legacy clone)…")
        code, out, err = run_git(["clone", url, "."], cwd=str(target))
        if code != 0:
            messagebox.showerror("Clone failed", err or out or "Unknown error")
            self._log_error(f"Clone failed: {err or out or 'Unknown error'}")
            return
        self._status(f"Cloned repo: {name}")
        self._log_success(f"Cloned into {target}")
        self._refresh_all_views()

    def _open_in_explorer(self):
        if not self.current_project:
            return
        try:
            if platform.system() == "Windows":
                os.startfile(self.current_project)
            elif platform.system() == "Darwin":
                subprocess.run(["open", self.current_project])
            else:
                subprocess.run(["xdg-open", self.current_project])
        except Exception as e:
            messagebox.showwarning("Open Folder", str(e))

    def _switch_project(self, name: str, absolute_path: Optional[str] = None):
        proj = absolute_path or str(Path(PROJECTS_DIR) / name)
        if not os.path.isdir(proj):
            messagebox.showwarning("Project", f"Not found: {proj}")
            return
        self.current_project = proj
        self.config["last_project"] = name
        cfg = self._proj_cfg()
        self.use_desktop.set(bool(cfg.get("use_github_desktop", self.config.get("use_github_desktop_default", False))))
        self.single_branch_only.set(bool(cfg.get("single_branch_only", self.config.get("single_branch_only_default", True))))
        self.global_mode.set(bool(cfg.get("global_update_mode", False)))
        self._save_config()
        self._ensure_structure(proj)
        self._ensure_db(Path(proj) / "conversation.db")
        pdd = Path(proj, "pdd.txt"); pdd.touch(exist_ok=True)
        txt = pdd.read_text(encoding="utf-8")
        self.txt_pdd.delete("1.0", "end"); self.txt_pdd.insert("end", txt)
        self.pdd_lines = txt.splitlines()
        idxf = Path(proj, "index.json")
        if not idxf.exists():
            idxf.write_text("[]", encoding="utf-8")
        try:
            self.sections = json.loads(idxf.read_text(encoding="utf-8"))
        except Exception:
            self.sections = []
        conn = sqlite3.connect(str(Path(proj) / "conversation.db"), check_same_thread=False)
        with self.db_lock:
            self.current_db = conn
        vdir = Path(proj, "versions"); vdir.mkdir(exist_ok=True)
        versions = sorted([p.name for p in vdir.glob("*.txt")])
        self.cmb_version["values"] = versions
        if versions:
            self.cmb_version.set(versions[-1])
        self._populate_explorer()
        self._populate_pdd_list()
        self._populate_launch_scripts()
        self._status(f"Opened project: {name}")
        self._log_success(f"Project opened: {name}")
        self._update_sync_state()

    # ---------- Project list / creation ----------
    def _refresh_projects(self):
        """Populate the Projects combobox with folder names under PROJECTS_DIR."""
        try:
            projects = [d.name for d in Path(PROJECTS_DIR).iterdir() if d.is_dir()]
        except Exception:
            projects = []
        self.cmb_project["values"] = sorted(projects)
        if self.config.get("last_project") in projects:
            self.cmb_project.set(self.config["last_project"])
        elif projects:
            self.cmb_project.set(projects[0])

    def _create_project(self):
        """Create a new project folder with baseline structure and switch to it."""
        name = simpledialog.askstring("New Project", "Project name:")
        if not name:
            return
        safe = re.sub(r"[^\w\-\. ]", "_", name).strip()
        proj_path = Path(PROJECTS_DIR) / safe
        if proj_path.exists():
            messagebox.showerror("New Project", f"Folder already exists:\n{proj_path}")
            self._log_error(f"Create project failed — folder exists: {proj_path}")
            return
        try:
            proj_path.mkdir(parents=True, exist_ok=False)
            self._ensure_structure(str(proj_path))
            self._ensure_db(proj_path / "conversation.db")
            (proj_path / "pdd.txt").write_text("", encoding="utf-8")
            (proj_path / "index.json").write_text("[]", encoding="utf-8")
        except Exception as e:
            messagebox.showerror("New Project", f"Failed to create project: {e}")
            self._log_error(f"Failed to create project: {e}")
            return
        self._refresh_projects()
        self.cmb_project.set(safe)
        self._switch_project(safe)
        self._status(f"Created project: {safe}")
        self._log_success(f"Project created: {safe}")
        self._refresh_all_views()

    def _ensure_structure(self, proj: str | Path):
        proj = Path(proj)
        (proj / UPDATE_WS_NAME).mkdir(parents=True, exist_ok=True)
        (proj / UPDATE_WS_NAME / REPO_FOLDER).mkdir(parents=True, exist_ok=True)
        (proj / UPDATE_WS_NAME / THINK_DIR_NAME).mkdir(parents=True, exist_ok=True)
        (proj / "Design_Documents").mkdir(parents=True, exist_ok=True)
        (proj / "versions").mkdir(parents=True, exist_ok=True)
        (proj / "burner_scripts").mkdir(parents=True, exist_ok=True)
        (proj / "burner_lists").mkdir(parents=True, exist_ok=True)
        (proj / UPDATE_WS_NAME / "errors").mkdir(parents=True, exist_ok=True)
        (proj / UPDATE_WS_NAME / "runtime_assets.json").touch(exist_ok=True)
        prompts_json = proj / "prompts_config.json"
        if not prompts_json.exists():
            prompts_json.write_text(json.dumps(DEFAULT_PROMPTS, indent=2), encoding="utf-8")

    def _ensure_db(self, db_path: Path):
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, text TEXT, embedding BLOB, timestamp REAL)")
        conn.execute("CREATE TABLE IF NOT EXISTS pdd_sections (id INTEGER PRIMARY KEY, section_text TEXT, embedding BLOB, section_hash TEXT, timestamp REAL)")
        # NEW: error diary (current + archived)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY,
                session_id TEXT,
                script TEXT,
                timestamp REAL,
                type TEXT,
                message TEXT,
                traceback TEXT,
                path TEXT,
                line INTEGER,
                status TEXT,  -- 'new' | 'archived' | 'stable'
                version_tag TEXT
            )
        """)
        conn.commit()
        conn.close()

    # ---------- Reset Data Set & Project ----------
    def _reset_data_set(self):
        if not self.current_project or not self.current_db:
            return
        if not messagebox.askyesno("Reset Data Set", "This will clear ALL semantic data (messages & sections). Continue?"):
            return
        self._log_step("Clearing semantic dataset (messages + sections)…")
        with self.db_lock:
            c = self.current_db.cursor()
            c.execute("DELETE FROM messages")
            c.execute("DELETE FROM pdd_sections")
            self.current_db.commit()
        info_dir = Path(self.current_project) / UPDATE_WS_NAME
        if info_dir.exists():
            for item in info_dir.rglob("*"):
                try:
                    if item.is_dir():
                        shutil.rmtree(item, onerror=_on_rm_error)
                    else:
                        try:
                            os.chmod(item, stat.S_IWRITE)
                        except Exception:
                            pass
                        item.unlink(missing_ok=True)
                except Exception:
                    pass
        self._status("Data set reset")
        self._log_success("Semantic dataset cleared.")
        self._refresh_all_views()

    def _reset_project_folder(self):
        if not self.current_project:
            return
        if not messagebox.askyesno("Reset Project", "This will delete ALL project files and recreate minimal structure. Continue?"):
            return
        self._log_step("Resetting project folder to minimal baseline…")
        proj = Path(self.current_project)
        for item in list(proj.iterdir()):
            try:
                if item.is_dir():
                    shutil.rmtree(item, onerror=_on_rm_error)
                else:
                    try:
                        os.chmod(item, stat.S_IWRITE)
                    except Exception:
                        pass
                    item.unlink(missing_ok=True)
            except Exception:
                pass
        (proj / "pdd.txt").write_text("", encoding="utf-8")
        (proj / "index.json").write_text("[]", encoding="utf-8")
        db = sqlite3.connect(str(proj / "conversation.db"), check_same_thread=False)
        db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, text TEXT, embedding BLOB, timestamp REAL)")
        db.execute("CREATE TABLE IF NOT EXISTS pdd_sections (id INTEGER PRIMARY KEY, section_text TEXT, embedding BLOB, section_hash TEXT, timestamp REAL)")
        db.close()
        self._switch_project(os.path.basename(proj), absolute_path=str(proj))
        self._status("Project reset")
        self._log_success("Project reset complete.")
        self._refresh_all_views()

    # ---------- PDD handling ----------
    def _on_pdd_edit(self):
        self.pdd_lines = self.txt_pdd.get("1.0", "end").splitlines()

    def _save_pdd(self):
        if not self.current_project:
            return
        Path(self.current_project, "pdd.txt").write_text(self.txt_pdd.get("1.0", "end"), encoding="utf-8")
        self._status("PDD saved")
        self._log_success("PDD saved to disk.")

    def _save_index(self):
        if not self.current_project:
            return
        Path(self.current_project, "index.json").write_text(json.dumps(self.sections, indent=2), encoding="utf-8")

    def _append_to_pdd(self, text: str):
        if not text:
            return
        if not text.endswith("\n"):
            text += "\n"
        self.txt_pdd.insert("end", text + "\n"); self.txt_pdd.see("end")
        self.pdd_lines = self.txt_pdd.get("1.0", "end").splitlines()
        sid = hashlib.md5(text.encode()).hexdigest()
        self.sections.append({
            "id": sid,
            "start": len(self.pdd_lines) - text.count("\n") - 1,
            "end": len(self.pdd_lines),
            "hash": sid
        })
        self._save_index()
        self._save_pdd()
        if self.current_db:
            snippet = text[:5000]
            em = embed(snippet, self.config["embedding_model"])
            with self.db_lock:
                c = self.current_db.cursor()
                c.execute(
                    "INSERT INTO messages (text, embedding, timestamp) VALUES (?,?,?)",
                    (f"[NEW_PDD_SECTION:{sid}]\n{snippet}", json.dumps(em) if em else None, time.time())
                )
                self.current_db.commit()

    def _extract_section(self, sid: str) -> Optional[str]:
        for s in self.sections:
            if s["hash"] == sid:
                return "\n".join(self.pdd_lines[s["start"]-1:s["end"]-1])
        return None

    def _replace_section(self, sid: str, new_text: str):
        for s in self.sections:
            if s["hash"] == sid:
                start, end = s["start"]-1, s["end"]-1
                nl = new_text.splitlines() + [""]
                self.pdd_lines[start:end+1] = nl
                s["end"] = start + len(nl) + 1
                s["hash"] = hashlib.md5(new_text.encode()).hexdigest()
                break
        self.txt_pdd.delete("1.0", "end")
        self.txt_pdd.insert("end", "\n".join(self.pdd_lines))
        self._save_index()
        self._save_pdd()

    def _highlight(self, sid: str):
        for s in self.sections:
            if s["hash"] == sid:
                a, b = f"{s['start']}.0", f"{s['end']}.0"
                self.txt_pdd.tag_add("hl", a, b)
                self.txt_pdd.tag_config("hl", background="#3b82f6", foreground="black")
                self.root.after(2500, lambda: self.txt_pdd.tag_remove("hl", a, b))
                break

    # ---------- DB / semantics ----------
    def _history(self, depth: int) -> str:
        if not self.current_db:
            return ""
        with self.db_lock:
            c = self.current_db.cursor()
            c.execute("SELECT text FROM messages ORDER BY timestamp DESC LIMIT ?", (depth,))
            return "\n".join([r[0] for r in c.fetchall()])

    def _semantic(self, query: str) -> str:
        if not self.current_db:
            return ""
        q = embed(query, self.config["embedding_model"])
        if not q:
            return ""
        with self.db_lock:
            c = self.current_db.cursor()
            c.execute("SELECT section_text, embedding FROM pdd_sections")
            res = []
            for t, b in c.fetchall():
                try:
                    e = json.loads(b) if b else None
                except Exception:
                    e = None
                s = cos(q, e) if e else 0
                if s > 0.5:
                    res.append((s, t))
            res.sort(key=lambda x: x[0], reverse=True)
            return "\n".join([t for _, t in res[:3]])

    def _add_msg(self, text: str):
        if not self.current_db:
            return
        em = embed(text, self.config["embedding_model"])
        with self.db_lock:
            c = self.current_db.cursor()
            c.execute(
                "INSERT INTO messages (text, embedding, timestamp) VALUES (?,?,?)",
                (text, json.dumps(em) if em else None, time.time())
            )
            self.current_db.commit()

    # ---------- Versions / model ----------
    def _save_version(self):
        if not self.current_project:
            return
        vdir = Path(self.current_project, "versions"); vdir.mkdir(exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        out = vdir / f"{ts}.txt"
        out.write_text(self.txt_pdd.get("1.0", "end"), encoding="utf-8")
        versions = sorted([p.name for p in vdir.glob("*.txt")])
        self.cmb_version["values"] = versions
        self.cmb_version.set(out.name)
        self._status(f"Saved version {out.name}")
        self._log_success(f"Version snapshot saved: {out.name}")
        self._refresh_all_views()

    def _load_version(self, name: str):
        if not self.current_project or not name:
            return
        vf = Path(self.current_project, "versions", name)
        if not vf.exists():
            return
        txt = vf.read_text(encoding="utf-8")
        self.txt_pdd.delete("1.0", "end"); self.txt_pdd.insert("end", txt); self._on_pdd_edit()

    def _update_task_type(self):
        """Wire Task Type to behaviors and log it (affects default Update Repo checkbox suggestions)."""
        tt = self.task_type.get()
        self._log_step(f"Task Type set to: {tt}")

    # ---------- Input/Prep flow ----------
    def _send_on_enter(self, event):
        if not (event.state & 0x0004):  # Ctrl not pressed
            self._send_to_prep()
            return "break"
        return None

    def _send_to_prep(self):
        txt = self.txt_input.get("1.0", "end").strip()
        if not txt:
            return
        if self.txt_prep.index("end-1c") != "1.0":
            self.txt_prep.insert("end", "\n\n")
        self.txt_prep.insert("end", txt)
        self.txt_prep.see("end")
        self.txt_input.delete("1.0", "end")

    def _append_prep_to_pdd(self):
        self._append_to_pdd(self.txt_prep.get("1.0", "end").strip())

    def _send_prep_to_llm(self):
        content = self.txt_prep.get("1.0", "end").strip()
        if not content:
            return
        self.txt_prep.delete("1.0", "end")
        if self.global_mode.get():
            threading.Thread(target=self._global_workflow, args=(content,), daemon=True).start()
        else:
            threading.Thread(target=self._workflow, args=(content,), daemon=True).start()

    def _rewrite_prep(self):
        text = self.txt_prep.get("1.0", "end").strip()
        if not text:
            return
        self._status("Rewriting Prep…")
        self._log_step("Invoking text model to rewrite prep content…")
        out = call_ollama_chat(self.config["ollama_model_text"], self.prompts["prep_rewrite"].format(text=text), timeout=30)
        if out.startswith("Error:"):
            self._log_error("Text model unavailable; cannot rewrite prep.")
            return
        self.txt_prep.delete("1.0", "end")
        self.txt_prep.insert("end", out)
        self._log_success("Prep rewritten.")
        self._status("Prep rewritten")

    # ---------- STT / TTS ----------
    def _start_mic(self):
        if self.listening or not self.recognizer or not self.mic:
            return
        self.listening = True
        self.stt_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.stt_thread.start()
        self._status("Listening…")
        self._log_step("Microphone listening started.")

    def _stop_mic(self):
        self.listening = False
        if self.stt_thread:
            self.stt_thread.join(timeout=0.2)
            self.stt_thread = None
        self._status("Mic stopped")
        self._log_success("Microphone listening stopped.")

    def _stop_tts_immediate(self):
        if self.tts:
            try:
                self.tts.stop()
            except Exception:
                pass
        self._status("TTS stopped")
        self._log_success("TTS stopped immediately.")

    def _update_tts_speed(self):
        factor = float(self.sld_tts_speed.get())
        self.config["tts_rate_factor"] = factor
        base = DEFAULT_CONFIG["tts_speed"]
        if self.tts:
            self.tts.setProperty("rate", int(base * factor))
        self._save_config()
        self._status(f"TTS speed set to {factor:.2f}×")
        self._log_success(f"TTS rate adjusted to {factor:.2f}×")

    def _toggle_tts(self):
        self.tts_muted = not self.tts_muted
        self._status("TTS muted" if self.tts_muted else "TTS unmuted")
        self._log_step("TTS mute toggled.")

    def _speak(self, text: str):
        if self.tts and not self.tts_muted:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                logger.warning("TTS speak error: %s", e)

    def _listen_loop(self):
        try:
            with self.mic as src:
                self.recognizer.adjust_for_ambient_noise(src)
                while self.listening:
                    try:
                        audio = self.recognizer.listen(src, timeout=5, phrase_time_limit=10)
                        txt = self.recognizer.recognize_google(audio)
                        sep = "" if self.txt_input.index("end-1c") == "1.0" else " "
                        self.txt_input.insert("end", sep + txt)
                        self.root.after(0, self.txt_input.see, "end")
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        logger.error("STT error: %s", e)
                        self._status(f"STT error: {e}")
        except Exception as e:
            logger.error("Mic loop error: %s", e)

    # ---------- Workflow (Summary → Consistency → Rewrites → Pseudo) ----------
    def _workflow(self, user_text: str):
        try:
            self._status("Summary Bot…")
            self._log_step("Summarizing user input into PDD update…")
            history = self._history(int(self.sld_context.get()))
            semantic = self._semantic(user_text)
            model = self.config["ollama_model_text"] if self.task_type.get() == "PDD" else self.config["ollama_model_coding"]
            errors = self._get_current_errors()
            summary = call_ollama_chat(model, f"{self.prompts['summary']}\nErrors:\n{errors}\n\n{user_text}")
            if summary.startswith("Error:"):
                self._log_error("Model unavailable; cannot summarize now.")
                return
            summary = self._handle_think_blocks(summary, origin="Summary")
            self._add_msg(summary)
            self._append_to_pdd(f"/* Summary */\n{summary}")
            was_empty = not any(line.strip() for line in self.pdd_lines[:-summary.count("\n")-2])
            if not was_empty:
                self._status("Consistency Bot…")
                self._log_step("Checking for PDD inconsistencies…")
                full_pdd = "\n".join(self.pdd_lines)
                cons_out = call_ollama_chat(model, self.prompts["consistency"].format(
                    summary=summary, full_pdd=full_pdd
                ))
                if cons_out.startswith("Error:"):
                    self._log_warn("Model unavailable; skipping consistency checks.")
                else:
                    tasks = parse_tasks(cons_out)
                    self._status("Spot Rewriter…")
                    self._log_step(f"Applying {len(tasks)} spot rewrites…")
                    for t in tasks:
                        sid = t["section_id"]
                        sec = self._extract_section(sid)
                        if not sec:
                            continue
                        new_sec = call_ollama_chat(model, self.prompts["rewrite"].format(
                            section_text=sec, summary=summary, reason=t["reason"]
                        ))
                        if new_sec.startswith("Error:"):
                            self._log_warn("Model unavailable; skipping a rewrite.")
                            continue
                        new_sec = self._handle_think_blocks(new_sec, origin="Rewrite")
                        self._replace_section(sid, new_sec)
                        if self.current_db:
                            em = embed(new_sec, self.config["embedding_model"])
                            with self.db_lock:
                                c = self.current_db.cursor()
                                c.execute(
                                    "UPDATE pdd_sections SET section_text=?, embedding=?, timestamp=? WHERE section_hash=?",
                                    (new_sec, json.dumps(em) if em else None, time.time(), sid)
                                )
                                self.current_db.commit()
                        self.root.after(0, lambda s=sid: self._highlight(s))
            else:
                self._status("First-time PDD—skipping consistency + rewrite")
                self._log_warn("First-time PDD detected; skipping rewrite phase.")
            self._status("Pseudo-Code Bot…")
            self._log_step("Injecting pseudocode hints across PDD…")
            full_pdd = "\n\n".join(self.pdd_lines)
            pseudo = call_ollama_chat(self.config["ollama_model_coding"], self.prompts["pseudo"].format(full_pdd=full_pdd))
            if not pseudo.startswith("Error:"):
                pseudo = self._handle_think_blocks(pseudo, origin="PseudoCode")
                self._append_to_pdd(pseudo)
            else:
                self._log_warn("Coding model unavailable; skipping pseudocode injection.")
            self._speak(summary)
            self._semantic_reweight_all()
            self._status("Done")
            self._log_success("Workflow complete.")
        except Exception as e:
            logger.error("Workflow error: %s", e)
            self._status(f"Error: {e}")
            self._log_error(f"Workflow error: {e}")

    def _global_workflow(self, user_text: str):
        try:
            self._status("Global Update Mode: Analyzing input…")
            self._log_step("Global mode: Extracting diffs and tasks…")
            errors = self._get_current_errors()
            task_json = call_ollama_chat(self.config["ollama_model_text"], f"{self.prompts['global_diff_extraction']}\nErrors:\n{errors}\n\n{user_text}")
            if task_json.startswith("Error:"):
                self._log_error("Model unavailable; global update aborted.")
                return
            tasks = json.loads(task_json)
            self._log_progress(f"Identified {len(tasks)} scripts for update.")
            for script, changes in tasks.items():
                self._log_step(f"Processing {script}…")
                # Update PDD
                pdd_path = Path(self.current_project) / "Design_Documents" / script / "pdd.txt"
                if pdd_path.exists():
                    pdd = pdd_path.read_text(encoding="utf-8")
                    updated_pdd = call_ollama_chat(self.config["ollama_model_text"], self.prompts["human_pdd_update"].format(pdd=pdd, changes=changes))
                    pdd_path.write_text(updated_pdd, encoding="utf-8")
                # Rewrite summary
                summary = call_ollama_chat(self.config["ollama_model_text"], self.prompts["human_summary_update"].format(changes=changes))
                summary_path = Path(self.current_project) / "Design_Documents" / script / "summary.txt"
                summary_path.write_text(summary, encoding="utf-8")
                # Pseudocode
                pseudo = call_ollama_chat(self.config["ollama_model_coding"], self.prompts["pseudo"].format(full_pdd=updated_pdd))
                pseudo_path = Path(self.current_project) / "Design_Documents" / script / "pseudocode.txt"
                pseudo_path.write_text(pseudo, encoding="utf-8")
                # Burner script
                burner = call_ollama_chat(self.config["ollama_model_coding"], self.prompts["burner_script"].format(pdd=updated_pdd))
                burner_path = Path(self.current_project) / "burner_scripts" / f"{script}.txt"
                burner_path.write_text(burner, encoding="utf-8")
            self._integrate_codex_suggestions()
            self._status("Global update complete")
            self._log_success("Global workflow complete.")
            self._refresh_all_views()
        except Exception as e:
            logger.error("Global workflow error: %s", e)
            self._status(f"Error: {e}")
            self._log_error(f"Global workflow error: {e}")

    def _integrate_codex_suggestions(self):
        directive_file = Path(self.current_project) / "suggested_improvements_to_be_filled_out_by_codex.txt"
        if directive_file.exists():
            suggestions = directive_file.read_text(encoding="utf-8").split("# Fill below:")[1].strip() if "# Fill below:" in directive_file.read_text(encoding="utf-8") else ""
            if suggestions:
                self._log_step("Integrating Codex suggestions…")
                # Apply suggestions to PDDs, summaries, etc.
                # For simplicity, append to project_summary.txt
                summary_path = Path(self.current_project) / "project_summary.txt"
                if summary_path.exists():
                    summary = summary_path.read_text(encoding="utf-8")
                    updated_summary = call_ollama_chat(self.config["ollama_model_text"], self.prompts["human_summary_update"].format(changes=suggestions))
                    summary_path.write_text(updated_summary, encoding="utf-8")

    def _handle_think_blocks(self, text: str, origin: str = "Unknown") -> str:
        """ Extract <think>…</think> blocks into project_info/Logic_Thoughts/ThinkList_YYYYMMDD.txt and replace them in-surface with a short provenance stub (<think>#YYYYMMDD-xxxxxxx). """
        think_matches = re.findall(r'<think>(.*?)</think>', text, re.DOTALL)
        if not think_matches or not self.current_project:
            return text
        logic_dir = Path(self.current_project) / UPDATE_WS_NAME / THINK_DIR_NAME
        logic_dir.mkdir(parents=True, exist_ok=True)
        day_tag = time.strftime('%Y%m%d')
        think_file = logic_dir / f"ThinkList_{day_tag}.txt"
        for think in think_matches:
            unique_id = hashlib.md5(think.encode()).hexdigest()[:8]
            with open(think_file, "a", encoding="utf-8") as f:
                f.write(
                    f"=== THINK BLOCK #{day_tag}-{unique_id} ===\n"
                    f"Origin: {origin}\n"
                    f"Project: {os.path.basename(self.current_project)}\n"
                    f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"---\n"
                    f"{think}\n"
                    f"=====================================\n\n"
                )
            text = text.replace(f"<think>{think}</think>", f"<think>#{day_tag}-{unique_id}")
        return text

    # ---------- Diff tools ----------
    def _paste_diff_clip(self):
        try:
            txt = self.root.clipboard_get()
        except Exception:
            txt = ""
        self.txt_diff.delete("1.0", "end")
        self.txt_diff.insert("end", txt)
        self._status("Diff pasted")
        self._log_success("Diff pasted from clipboard.")

    def _fetch_local_diff(self):
        if not self.current_project:
            return
        if git_is_repo(self.current_project):
            code, out, err = run_git(["diff"], cwd=self.current_project)
            if code != 0:
                messagebox.showerror("git diff", err or out or "Unknown")
                self._log_error(f"git diff failed: {err or out or 'Unknown'}")
                return
            self.txt_diff.delete("1.0", "end")
            self.txt_diff.insert("end", out or "(no changes)")
            self._status("Fetched git diff")
            self._log_success("Local git diff fetched.")
            return
        vdir = Path(self.current_project, "versions")
        latest = max(vdir.glob("*.txt"), default=None, key=lambda p: p.stat().st_mtime)
        if not latest:
            messagebox.showinfo("Diff", "Not a git repo and no versions available.")
            self._log_warn("No versions available to diff.")
            return
        a = latest.read_text(encoding="utf-8").splitlines(keepends=True)
        b = Path(self.current_project, "pdd.txt").read_text(encoding="utf-8").splitlines(keepends=True)
        d = difflib.unified_diff(a, b, fromfile=latest.name, tofile="pdd.txt")
        self.txt_diff.delete("1.0", "end")
        self.txt_diff.insert("end", "".join(d))
        self._status("Local diff (version vs pdd.txt)")
        self._log_success("Generated local diff against last version snapshot.")

    def _init_git_repo(self):
        if not self.current_project:
            return
        if git_is_repo(self.current_project):
            self._status("Already a git repo")
            self._log_warn("Current project folder is already a git repository.")
            return
        code, out, err = run_git(["init"], cwd=self.current_project)
        if code != 0:
            messagebox.showerror("git init", err or out or "Unknown")
            self._log_error(f"git init failed: {err or out or 'Unknown'}")
            return
        run_git(["add", "-A"], cwd=self.current_project)
        run_git(["commit", "-m", "Initial commit"], cwd=self.current_project)
        self._status("Initialized git repository")
        self._log_success("Git repository initialized in project folder.")
        self._refresh_all_views()

    def _fetch_github_compare(self):
        url = simpledialog.askstring("GitHub Compare", "Enter .diff or .patch URL:")
        if not url:
            return
        try:
            self._log_step("Fetching GitHub compare patch…")
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            self.txt_diff.delete("1.0", "end")
            self.txt_diff.insert("end", r.text)
            self._status("Fetched GitHub compare")
            self._log_success("GitHub compare fetched.")
        except Exception as e:
            messagebox.showerror("Fetch compare", str(e))
            self._log_error(f"Fetch compare failed: {e}")

    def _ingest_repo(self):
        if not (self.current_project and self.current_db):
            return
        info_dir = Path(self.current_project) / UPDATE_WS_NAME
        info_dir.mkdir(exist_ok=True)
        count = 0
        self._log_step("Ingesting repository files into dataset…")
        for cur, dirs, files in os.walk(self.current_project):
            for skip in (".git", "venv"):
                if skip in dirs:
                    dirs.remove(skip)
            for f in files:
                p = Path(cur) / f
                if UPDATE_WS_NAME in p.parts:
                    snippet = p.read_text(encoding="utf-8", errors="ignore")[:5000]
                    dst = info_dir / p.relative_to(self.current_project)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(snippet, encoding="utf-8")
                    em = embed(snippet, self.config["embedding_model"])
                    with self.db_lock:
                        c = self.current_db.cursor()
                        c.execute(
                            "INSERT OR REPLACE INTO messages (text, embedding, timestamp) VALUES (?,?,?)",
                            (f"[FILE:{p.relative_to(self.current_project)}]\n{snippet}", json.dumps(em) if em else None, time.time())
                        )
                    count += 1
                    if count % 50 == 0:
                        self._log_progress(f"Ingested {count} files…")
        with self.db_lock:
            self.current_db.commit()
        self._status(f"Ingested {count} files")
        self._log_success(f"Ingested {count} files into dataset.")
        self._refresh_all_views()

    # ---------- Quick commit ----------
    def _quick_commit(self):
        if not self.current_project:
            return
        if not git_is_repo(self.current_project):
            messagebox.showinfo("Git", "Not a git repo. Use 'Init Git Repo'.")
            self._log_warn("Quick commit aborted: not a git repository.")
            return
        msg = simpledialog.askstring("Quick Commit", "Commit message:", initialvalue=f"update {time.strftime('%Y-%m-%d %H:%M:%S')}")
        if not msg:
            return
        run_git(["add", "-A"], cwd=self.current_project)
        code, out, err = run_git(["commit", "-m", msg], cwd=self.current_project)
        if code != 0:
            messagebox.showerror("Commit failed", err or out or "Unknown")
            self._log_error(f"Quick commit failed: {err or out or 'Unknown'}")
        else:
            self._status("Committed changes")
            self._log_success("Quick commit completed.")
        self._refresh_all_views()

    # ---------- Burner script (legacy generator) ----------
    def _burner_script(self):
        pdd = self.txt_pdd.get("1.0", "end")
        self._log_step("Generating legacy burner script from PDD…")
        code = call_ollama_chat(self.config["ollama_model_coding"], self.prompts["burner_script"].format(pdd=pdd), timeout=90)
        if code.startswith("Error:"):
            self._log_error("Coding model unavailable; cannot generate burner script right now.")
            return
        code = self._handle_think_blocks(code, origin="BurnerScript")
        out = Path(self.current_project) / "burner_scripts" / "burner.txt"
        out.write_text(code, encoding="utf-8")
        self.txt_progressive.delete("1.0", "end")
        self.txt_progressive.insert("end", code)
        self.txt_pdd.insert("end", f"\n/* Burner Script: {out.name} */\n{code}\n")
        self._status(f"Burner script generated: {out.name} (loaded into Progressive editor)")
        self._log_success(f"Burner script written to {out}")
        self._refresh_all_views()

    # ---------- Semantic re-weight ----------
    def _semantic_reweight_all(self):
        if not (self.current_project and self.current_db):
            return
        info_dir = Path(self.current_project) / UPDATE_WS_NAME
        if not info_dir.exists():
            return
        count = 0
        self._log_step("Re-embedding project_info files for semantic weighting…")
        for file in info_dir.rglob("*.*"):
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")[:5000]
            except Exception:
                continue
            em = embed(text, self.config["embedding_model"])
            with self.db_lock:
                c = self.current_db.cursor()
                c.execute(""" INSERT OR REPLACE INTO messages (text, embedding, timestamp) VALUES (?, ?, ?) """,
                          (f"[FILE:{file.relative_to(self.current_project)}]\n{text}", json.dumps(em) if em else None, time.time()))
            count += 1
            if count % 40 == 0:
                self._log_progress(f"Re-embedded {count} files…")
        with self.db_lock:
            self.current_db.commit()
        self._status(f"Re-semantic-weighted {count} project_info files")
        self._log_success(f"Semantic weights updated for {count} files.")

    # ---------- Status ----------
    def _status(self, msg: str):
        self.status.set(msg)
        logger.info(msg)

    # ---------- Launch Script ----------
    def _launch_script(self):
        if not self.current_project:
            return
        script = self.cmb_launch_script.get()
        if not script:
            return
        version_id = time.strftime("%Y%m%d_%H%M%S")
        error_file = Path(self.current_project) / "project_info" / "errors" / f"errors_v{version_id}.txt"
        asset_file = Path(self.current_project) / "project_info" / "runtime_assets.json"
        before = set(Path(self.current_project).rglob("*"))
        try:
            proc = subprocess.Popen(["python", script], cwd=self.current_project, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate()
            with open(error_file, "w", encoding="utf-8") as f:
                f.write(f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}")
            after = set(Path(self.current_project).rglob("*"))
            new_assets = list(after - before)
            with open(asset_file, "w", encoding="utf-8") as f:
                json.dump({"new_assets": [str(p) for p in new_assets]}, f, indent=2)
            self._log_success("Script launched and logs captured.")
        except Exception as e:
            self._log_error(f"Launch failed: {e}")

# -------------------- Prompt dialog --------------------
class PromptControlDialog(tk.Toplevel):
    def __init__(self, parent, prompts: Dict[str, str], app_ref: RantPDD):
        super().__init__(parent)
        self.title("Prompt/LLM Control")
        self.configure(bg=THEME_BG)
        self.prompts = prompts
        self.models = discover_ollama_models()
        self.app = app_ref  # reference to RantPDD for saving model selections
        def field(lbl, key):
            ttk.Label(self, text=lbl, background=THEME_BG, foreground=THEME_TEXT).pack(anchor="w", padx=10, pady=(10, 2))
            w = tk.Text(self, height=5, bg=THEME_ELEV, fg=THEME_TEXT, insertbackground=THEME_TEXT, wrap="word")
            w.insert("end", prompts[key])
            w.pack(fill="x", padx=10)
            cmb = ttk.Combobox(self, state="readonly", values=self.models, width=28)
            cmb.pack(padx=10, pady=2)
            default = DEFAULT_CONFIG["ollama_model_coding"] if key in ["pseudo", "burner_script"] \
                else DEFAULT_CONFIG["ollama_model_text"]
            cmb.set(default)
            setattr(self, f"cmb_{key}", cmb)
            return w
        self.f_summary = field("Summary Prompt", "summary")
        self.f_consistency = field("Consistency Prompt", "consistency")
        self.f_rewrite = field("Rewrite Prompt", "rewrite")
        self.f_pseudo = field("Pseudo-Code Prompt", "pseudo")
        self.f_burner = field("Burner Script Prompt", "burner_script")
        self.f_prep_rewrite = field("Prep Rewrite Prompt", "prep_rewrite")
        self.f_sync = field("Project Sync Prompt", "project_sync")
        self.f_over = field("Project Overview Prompt", "project_overview")
        self.f_global_diff = field("Global Diff Extraction Prompt", "global_diff_extraction")
        self.f_human_pdd = field("Human PDD Update Prompt", "human_pdd_update")
        self.f_human_summary = field("Human Summary Update Prompt", "human_summary_update")
        self.f_runtime_doc = field("Runtime Documentation Prompt", "runtime_documentation")
        self.f_packaging = field("Packaging Prompt", "packaging")
        self.f_improvement = field("Improvement File Prompt", "improvement_file")
        self.f_global_exec = field("Global Chat Execution Prompt", "global_chat_execution")
        self.f_runtime_test = field("Runtime Testing Prompt", "runtime_testing")
        self.f_pdd_gen = field("PDD Generation Prompt", "pdd_generation")
        self.f_summary_gen = field("Summary Generation Prompt", "summary_generation")
        self.f_codex_sugg = field("Codex Suggestion Prompt", "codex_suggestion")
        ttk.Button(self, text="Save", command=self._save).pack(pady=10)

    def _save(self):
        for key in self.prompts:
            txt = getattr(self, f"f_{key.replace('-', '_')}").get("1.0", "end").strip()
            self.prompts[key] = txt
            model = getattr(self, f"cmb_{key.replace('-', '_')}").get()
            if key in ["pseudo", "burner_script"]:
                self.app.config["ollama_model_coding"] = model
            else:
                self.app.config["ollama_model_text"] = model
        try:
            Path(CONFIG_FILE).write_text(json.dumps(self.app.config, indent=2))
        except Exception:
            pass
        self.destroy()

# -------------------- Main --------------------
def main():
    _set_process_dpi_awareness()
    root = tk.Tk()
    _apply_tk_scaling(root)
    app = RantPDD(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

Rant_PDD.py — 2025 UI refresh with full workflow, Explorer, Dataset controls, safe resets, Sync & Summary features, versioned repository sync, and Package for GitHub.
🦈 SHARK_SENTINEL DeepSeek Progressive Script Integration + GitHub Enhancements
----------------------------------------------------------------
• Concept shift: Burner Script → Progressive Script (permanent, versioned)
• Progressive Scripts Archive under Design_Documents/<module>/progressive_scripts
• Headers include PDD hash, model used, timestamp
• UI updates:
  - NEW purple buttons: Pull Repo, Update Repo (single-branch mode + GitHub Desktop option)
  - “Progressive Script” tab (renamed) with: ▸ Promote to Repo (archive/inject) ▸ Archive Current Version
  - NEW checkbox: Use GitHub Desktop — routes Pull/Update to also open the repo in GitHub Desktop for verification. Stores per-project repo URL/branch; pulls one branch only. Accepts Git URL or x-github-client:// link.
  - NEW checkbox: Single-branch only — enforces tracking only the selected branch.
  - NEW Update Repo dialog with CHECKBOXES: ▸ Include Progressive Scripts ▸ Include Design_Documents ▸ Include Info (project_info excluding repository) These choices are remembered per project across sessions.
• GitHub flows:
  - Pull Repo remembers URL + branch; single-branch clone/pull only.
  - Update Repo wipes target subfolders first (no residuals), copies selected items, commits, pushes, and optionally opens GitHub Desktop.
• Robust deletion:
  - Delete Repository now wipes ALL nested content including hidden .git on Windows.
  - Reset Project wipes everything and recreates minimal structure.
• Dual export packaging for GitHub (Design_Documents + generated scripts)
  - export_generated_scripts_* is fully wiped on each run, then ALL Progressive Scripts from every module are copied (all *.py versions), no residuals.
• Full backward compatibility with existing Codex-based workflow
• Auto-refresh Explorer after file ops + F5 refresh key
• System Console panel for live logs with colored syntax (STEP/PROGRESS/WARN/ERROR/SUCCESS)
Fixes and Notables (2025-08-06):
• **Streaming System Console**: Sync Repo now runs in a background thread with frequent progress ticks. You immediately see “Starting repository sync …” and periodic updates.
• **Ollama not running resilience**:
  - Centralized retry logic (bounded) for /api/chat and /api/embeddings with exponential backoff.
  - Early WARN/ERROR lines in the console if the local server is down; operations won’t hang the UI.
  - Embeddings gracefully skip; summaries log an error and continue the sync pipeline.
• **Update Repo dialog** revamped with checkboxes and per-project persistence.
• **Wipe/Save semantics (no residuals)** for Update Repo and Package for GitHub.
• **Task Type wiring** influences default options in Update Repo (Coding → include scripts; PDD → include design).
New Features (2025-08-06 Implementation):
• Human-like summaries with conversational prompts.
• Global Update Mode checkbox; repo-wide updates with diff extraction and per-script tasks.
• Launchable exports: UI selector for launch script, Launch button, error capture to versioned logs.
• Packaging checkboxes (Design Docs, Burner Lists, Burner Scripts); persisted; clean wipe; versioned branch naming.
• Codex directive file: generated if missing, persistent, included in exports.
• Integration: Global chat ties with Codex suggestions, PDD updates, summaries in human tone.
• Runtime testing: Capture stdout/stderr/exceptions, asset discovery after launch.
• Embedded humanistic prompts in prompts_config.json.
**Classes:** UpdateRepoDialog, PackageDialog, RantPDD, PromptControlDialog
**Functions:** _set_process_dpi_awareness(), _apply_tk_scaling(root, base_px), get_contrast_color(bg_hex), apply_modern_theme(style), _retry(fn), discover_ollama_models(), _choose_embedding_model(configured), _ollama_post(host, endpoint, payload, timeout), call_ollama_chat(model, prompt, timeout), embed(text, model), cos(a, b), run_git(args, cwd), git_is_repo(path), parse_tasks(text), _on_rm_error(func, path, exc_info), wipe_directory_contents(folder), main()
