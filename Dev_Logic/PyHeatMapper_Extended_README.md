# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analyzing the project contents. Python modules are parsed for docstrings, classes, and functions. Image files are embedded as previews. Executable files (.exe) are listed by name; their contents are intentionally skipped.

## Python Modules

- `PyHeatMapper.py`

## Other Files

- `data\__init__`
- `data\cache\__init__`
- `data\exports\__init__`
- `data\index\__init__`
- `data\pdd\__init__`
- `data\pyheat.log`
- `data\readme\__init__`
- `data\stacks\__init__`
- `data\summary\__init__`
- `data\vectors\__init__`
- `datasets\__init__`
- `datasets\metadata_default.json`
- `datasets\scan_cache_default.json`


## Detailed Module Analyses


## Module `PyHeatMapper.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyHeatMapper — Advanced Scan, Pre-Scan Counts, Content-Hash Dedup, Semantic Weighting, PDDs, Favorites,
README Builder, and Integrated ScriptMover (clipboard + hotkey)

What this build adds (highlights):
- NEW: Pre-Scan (.py counts) dialog (WinDirStat-style) showing, per top-level folder under each selected root,
  the recursive count of Python files (respecting exclusions). Sortable table + bar chart + CSV export.
- Content-hash (SHA-1) dedup: a "script" is defined by its exact bytes, not its path.
  • meta.records are keyed by sha and store: {'paths': [...]} of all locations.
  • Duplicates don't inflate unique counts or re-embed vectors unnecessarily.
- Robust Windows-safe dataset file naming and atomic writes for metadata/scan-cache.
- Strong default excludes (venv, __pycache__, AppData, Temp, Windows, Program Files, etc.)
  + user regex excludes remain available. Only *.py files are considered.
- Deepen Selected checkbox, Favorites (★), PDD previews in all relevant tabs,
  README Builder (from Favorites or a folder subset), Radar + Heat Grid.
- "Mover" tab: PyQt clone of ScriptMover workflow (destination chooser, clipboard watcher, hotkey, README/Locations docs).

Run:
    pip install PyQt6 faiss-cpu matplotlib requests numpy psutil keyboard pywin32
    python PyHeatMapper.py
"""

from __future__ import annotations
import os
import sys
import re
import io
import json
import ast
import time
import math
import shutil
import queue
import hashlib
import logging
import threading
import platform
import traceback
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import warnings
warnings.filterwarnings("ignore", r"invalid escape sequence", SyntaxWarning)

import numpy as np
try:
    import faiss
except ImportError:
    faiss = None

import requests
try:
    import psutil
except ImportError:
    psutil = None

# Optional deps used by Mover tab (Windows friendly)
try:
    import win32clipboard, win32con, pythoncom  # type: ignore
    HAS_WIN_CLIP = True
except Exception:
    HAS_WIN_CLIP = False

try:
    import keyboard  # type: ignore
    HAS_KEYBOARD = True
except Exception:
    HAS_KEYBOARD = False

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QObject
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QSplitter, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QPlainTextEdit,
    QProgressBar, QMessageBox, QComboBox, QCheckBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QFileDialog,
    QListWidget, QScrollArea, QStackedWidget, QInputDialog, QMenu, QTextEdit, QToolBar
)
from PyQt6.QtGui import QAction, QTextCursor

# Use the Qt6 backend for Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.cm
import matplotlib.colors

# ─────────────────────────────── CONSTANTS & DIRECTORIES ───────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent

DATA_DIR    = BASE_DIR / "data"
LOG_PATH    = DATA_DIR / "pyheat.log"
CONFIG_PATH = BASE_DIR / "config.json"

DATASETS_DIR    = BASE_DIR / "datasets"
DEFAULT_DATASET = "default"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

# default paths (subject to dataset slug below)
META_PATH    = DATASETS_DIR / f"metadata_{DEFAULT_DATASET}.json"
SCAN_CACHE   = DATASETS_DIR / f"scan_cache_{DEFAULT_DATASET}.json"

CACHE_DIR   = DATA_DIR / "cache"
PDD_DIR     = DATA_DIR / "pdd"
SUM_DIR     = DATA_DIR / "summary"
VEC_DIR     = DATA_DIR / "vectors"
INDEX_DIR   = DATA_DIR / "index"
STACKS_DIR  = DATA_DIR / "stacks"
EXPORTS_DIR = DATA_DIR / "exports"
README_DIR  = DATA_DIR / "readme"

for d in (DATA_DIR, CACHE_DIR, PDD_DIR, SUM_DIR, VEC_DIR, INDEX_DIR, STACKS_DIR, EXPORTS_DIR, README_DIR):
    d.mkdir(parents=True, exist_ok=True)

for path in (META_PATH, SCAN_CACHE):
    if not path.exists():
        path.write_text("{}", encoding="utf-8")

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("PyHeatMapper")
log.addHandler(logging.StreamHandler(sys.stdout))

OLLAMA_URL = "http://localhost:11434"

ALLOWED_MODELS = [
    "nomic-embed-text:latest",
    "wizardlm-uncensored:latest",
    "huihui_ai/deepseek-r1-abliterated:14b",
    "huihui_ai/deepseek-r1-abliterated:8b",
    "codellama:latest",
    "deepseek-coder-v2:16b",
    "phi4:latest",
    "llava:latest",
    "snowflake-arctic-embed2:latest",
    "gemma3:27b",
]
DEFAULT_EMBED = "snowflake-arctic-embed2:latest"
DEFAULT_LLM   = "phi4:latest"

# Robust folder-name excludes (non-regex first, faster; users can still add regex)
EXCLUDE_DIR_NAMES = {
    "venv", ".venv", "__pycache__", "node_modules",
    "AppData", "Temp", "Local", "Roaming",
    "Windows", "Program Files", "Program Files (x86)", "ProgramData",
    "$Recycle.Bin", "System Volume Information",
    ".git", ".mypy_cache", ".pytest_cache", ".ipynb_checkpoints"
}
# Path substring excludes (case-insensitive)
EXCLUDE_SUBSTRS = [
    "\\AppData\\", "\\Temp\\", "\\Local\\", "\\Roaming\\",
    "\\node_modules\\", "\\venv\\", "\\.venv\\", "\\__pycache__\\",
    "\\.git\\", "\\.mypy_cache\\", "\\.pytest_cache\\", "\\.ipynb_checkpoints\\"
]

CPU_PAUSE_THRESHOLD = 90.0  # percent
CPU_PAUSE_SECONDS   = 5.0
FAST_CHUNK_CHARS    = 3000
PDD_MAX_TOKENS      = 8000
EMBED_SOURCE        = "pdd"

CATEGORY_KEYWORDS = {
    "autonomy": ["agent","autonomous","scheduler","daemon","thread","loop"],
    "chatbot":  ["chat","prompt","llm","conversation","assistant","ollama","openai","gpt"],
    "gui":      ["qt","pyqt","tkinter","widget","window","pyside","panda3d","matplotlib"],
    "data":     ["json","csv","pandas","sqlite","database","faiss","vector","index","numpy"],
    "ml":       ["torch","tensorflow","sklearn","model","embedding","train","inference"],
    "utils":    ["os.","shutil","pathlib","argparse","logging","requests","subprocess"]
}
CATEGORY_ORDER = ["autonomy","chatbot","gui","data","ml","utils"]

# ───────────────────────────────────────────────────────────────────────────
#                             UTILITY FUNCTIONS
# ───────────────────────────────────────────────────────────────────────────
def is_windows() -> bool:
    return platform.system().lower().startswith("win")

def list_windows_drives() -> List[str]:
    if not is_windows():
        return [str(Path.home())]
    import string
    drives = []
    for letter in string.ascii_uppercase:
        root = Path(f"{letter}:\\")
        if root.exists():
            drives.append(str(root))
    return drives

def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")
    return s or "file"

def ensure_model(name: str, fallback: str) -> str:
    return name if name in ALLOWED_MODELS else fallback

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def pct(x: float) -> float:
    return clamp01(x) * 100.0

WINDOWS_FORBIDDEN = '<>:"/\\|?*'
def sanitize_windows_filename(name: str) -> str:
    name = "".join(ch for ch in name if 31 < ord(ch) < 127)
    for ch in WINDOWS_FORBIDDEN:
        name = name.replace(ch, "_")
    name = " ".join(name.split())
    return name.rstrip(" .") or "dataset"

def dataset_slug(name: str) -> str:
    import re as _re
    name = sanitize_windows_filename(name)
    return _re.sub(r"[^A-Za-z0-9._-]+", "_", name)

def _atomic_write(path: Path, text: str):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def excluded_dirpath(dirpath: str) -> bool:
    low = dirpath.lower()
    parts = {p.lower() for p in Path(dirpath).parts}
    if any(name.lower() in parts for name in EXCLUDE_DIR_NAMES):
        return True
    return any(s.lower() in low for s in EXCLUDE_SUBSTRS)

# ───────────────────────────────────────────────────────────────────────────
#                         CONFIGURATION & STATE CLASSES
# ───────────────────────────────────────────────────────────────────────────
@dataclass
class Config:
    selected_roots: List[str]      = field(default_factory=list)
    user_excludes: List[str]       = field(default_factory=list)  # regex (optional)
    embed_model: str               = DEFAULT_EMBED
    llm_model: str                 = DEFAULT_LLM
    heat_view: str                 = "radar"      # radar | grid
    max_scan_workers: int          = 8
    max_fast_workers: int          = 8
    max_embed_workers: int         = 6
    max_deep_workers: int          = 3
    fast_embed_from: str           = EMBED_SOURCE # pdd | source
    deep_on_finish: bool           = False        # “Deepen Selected” checkbox
    cpu_guard: bool                = True
    current_dataset: str           = DEFAULT_DATASET
    # Mover
    mover_destination: str         = str(Path.home() / "ScriptMover_Archive")
    mover_generate_docs: bool      = True
    mover_hotkey: str              = "ctrl+shift+m"  # global hotkey (requires 'keyboard')

class ConfigManager:
    def __init__(self, path=CONFIG_PATH):
        self.path = Path(path)
        self.cfg  = Config()
        self.load()

    def load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.cfg = Config(**{**asdict(self.cfg), **data})
            except Exception as e:
                log.warning(f"Config load failed: {e}")

    def save(self):
        try:
            self.path.write_text(json.dumps(asdict(self.cfg), indent=2), encoding="utf-8")
        except Exception as e:
            log.error(f"Config save failed: {e}")

class MetadataStore:
    """
    Records are keyed by sha (sha1 of contents), and each record contains:
      {
        'paths': [list of absolute paths that match this sha],
        'mtime': last seen mtime for *one* path (informational),
        'size' : size in bytes (informational),
        'pdd'  : PDD path,
        'summary': summary path,
        'vector': vec path or None,
        'categories': {...},
        'complexity': float,
        'stats': {...},
        'doc_quality': {...},
        'readme_ready': float,
        'fundamental_depth': float,
        'semantic_score': float,
        'favorite': bool
      }
    """
    def __init__(self, path=META_PATH):
        self.path = Path(path)
        self.records: Dict[str, dict] = {}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                self.records = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception as e:
                log.warning(f"Metadata load failed: {e}")

    def save(self):
        try:
            _atomic_write(self.path, json.dumps(self.records, indent=2))
        except Exception as e:
            log.error(f"Metadata save failed: {e}")

    def upsert(self, sha: str, rec: dict, new_path: Optional[str] = None):
        old = self.records.get(sha)
        if old:
            # merge while preserving favorite and paths
            if "favorite" in old and not rec.get("favorite"):
                rec["favorite"] = old["favorite"]
            paths = set(old.get("paths", []))
            if new_path:
                paths.add(new_path)
            rec["paths"] = sorted(paths)
        else:
            if new_path:
                rec["paths"] = [new_path]
            else:
                rec["paths"] = []
        self.records[sha] = rec

    def append_path(self, sha: str, path: str):
        rec = self.records.get(sha)
        if not rec:
            return
        paths = set(rec.get("paths", []))
        paths.add(path)
        rec["paths"] = sorted(paths)

    def toggle_favorite(self, sha: str) -> bool:
        rec = self.records.get(sha)
        if not rec:
            return False
        rec["favorite"] = not bool(rec.get("favorite"))
        self.save()
        return rec["favorite"]

class ScanCache:
    """
    Path-based cache for change detection:
      map[path] = (mtime, size, sha)
    """
    def __init__(self, path=SCAN_CACHE):
        self.path = Path(path)
        self.map: Dict[str, Tuple[float,int,str]] = {}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                self.map = {k: tuple(v) for k,v in json.loads(self.path.read_text(encoding="utf-8")).items()}
            except Exception as e:
                log.warning(f"Scan cache load failed: {e}")

    def save(self):
        try:
            _atomic_write(self.path, json.dumps({k:list(v) for k,v in self.map.items()}, indent=2))
        except Exception as e:
            log.error(f"Scan cache save failed: {e}")

    def changed(self, path: str, mtime: float, size: int, sha: Optional[str]) -> bool:
        prev = self.map.get(path)
        if not prev:
            return True
        pm, ps, psha = prev
        if psha and sha and psha == sha and pm == mtime and ps == size:
            return False
        return pm != mtime or ps != size or (sha is not None and psha != sha)

    def update(self, path: str, mtime: float, size: int, sha: str):
        self.map[path] = (mtime, size, sha)

# ───────────────────────────────────────────────────────────────────────────
#                               CPU USAGE GUARD
# ───────────────────────────────────────────────────────────────────────────
class CpuGuard(threading.Thread):
    def __init__(self, pause_event: threading.Event,
                 threshold=CPU_PAUSE_THRESHOLD, duration=CPU_PAUSE_SECONDS):
        super().__init__(daemon=True)
        self.pause_event = pause_event
        self.threshold = threshold
        self.duration = duration
        self._stop = threading.Event()

    def run(self):
        if psutil is None:
            return
        high_since = None
        while not self._stop.is_set():
            cpu = psutil.cpu_percent(interval=0.5)
            if cpu >= self.threshold:
                if high_since is None:
                    high_since = time.time()
                elif time.time() - high_since >= self.duration:
                    self.pause_event.set()
            else:
                high_since = None
                self.pause_event.clear()
            time.sleep(0.25)

    def stop(self):
        self._stop.set()

# ───────────────────────────────────────────────────────────────────────────
#                               OLLAMA CLIENTS
# ───────────────────────────────────────────────────────────────────────────
def ollama_generate(model: str, prompt: str, timeout: int = 45) -> str:
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        r.raise_for_status()
        j = r.json()
        return j.get("response","") or j.get("message","") or ""
    except Exception as e:
        log.warning(f"Ollama generate failed: {e}")
        return ""

def ollama_embed(model: str, text: str, timeout: int = 30) -> Optional[np.ndarray]:
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=timeout
        )
        r.raise_for_status()
        vec = np.array(r.json().get("embedding",[]), dtype="float32")
        return vec if vec.ndim == 1 and vec.size > 0 else None
    except Exception as e:
        log.warning(f"Ollama embed failed: {e}")
        return None

def dummy_embed(text: str, dim: int = 768) -> np.ndarray:
    v = np.zeros(dim, dtype="float32")
    for i, c in enumerate(text):
        v[i % dim] += (ord(c) % 17) * 0.07
    norm = np.linalg.norm(v)
    return v if norm == 0 else (v / norm)

# ───────────────────────────────────────────────────────────────────────────
#                           AST & COMPLEXITY MEASUREMENT
# ───────────────────────────────────────────────────────────────────────────
LOW_LEVEL_IMPORTS = {
    "os","sys","pathlib","threading","asyncio","subprocess","socket","select",
    "re","math","hashlib","logging","queue","multiprocessing","concurrent",
}

README_TEMPL_HEADINGS = [
    "overview","features","installation","usage","configuration",
    "api","examples","roadmap","contributing","license","faq"
]

def ast_info(source: str) -> dict:
    data = {"imports": [], "classes": [], "functions": []}
    try:
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    data["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    data["imports"].append(f"{mod}.{alias.name}")
            elif isinstance(node, ast.ClassDef):
                cls = {"name": node.name, "methods": [], "doc": ast.get_docstring(node) or ""}
                for member in cls.body:
                    if isinstance(member, ast.FunctionDef):
                        args = [a.arg for a in member.args.args]
                        cls["methods"].append({
                            "name": member.name,
                            "args": args,
                            "doc": ast.get_docstring(member) or ""
                        })
                data["classes"].append(cls)
            elif isinstance(node, ast.FunctionDef):
                args = [a.arg for a in node.args.args]
                data["functions"].append({
                    "name": node.name,
                    "args": args,
                    "doc": ast.get_docstring(node) or ""
                })
    except Exception:
        pass
    return data

def measure_complexity(source: str, info: dict) -> float:
    lines = source.count("\n") + 1
    n_cls = len(info.get("classes", []))
    n_fn  = len(info.get("functions", []))
    return math.log(max(lines, 1), 1.6) + n_cls * 2.0 + n_fn * 1.0

def category_weights(source: str) -> Dict[str, float]:
    lower = source.lower()
    weights = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        score = sum(lower.count(kw) for kw in kws) * 10.0
        weights[cat] = float(min(100.0, score))
    return weights

def doc_quality(source: str, info: dict) -> Dict[str, float]:
    lines = source.count("\n") + 1
    comments = sum(1 for ln in source.splitlines() if ln.strip().startswith("#"))
    comment_density = comments / max(lines, 1)

    total_defs = len(info.get("functions", [])) + len(info.get("classes", []))
    docd_defs = sum(1 for fn in info.get("functions", []) if fn.get("doc")) + \
                sum(1 for cls in info.get("classes", []) if cls.get("doc"))
    cov = (docd_defs / total_defs) if total_defs else 0.0
    try:
        module_doc = bool(ast.get_docstring(ast.parse(source)))
    except Exception:
        module_doc = False

    return {
        "docstring_coverage": float(clamp01(cov)),
        "comment_density":    float(clamp01(comment_density)),
        "module_doc":         1.0 if module_doc else 0.0
    }

def readme_template_readiness(source: str) -> float:
    s = source.lower()
    score = 0.0
    for h in README_TEMPL_HEADINGS:
        if f"## {h}" in s or f"# {h}" in s or f"### {h}" in s:
            score += 0.08
    if "prompt" in s:
        score += 0.12
    if "template" in s or "jinja" in s or "f-string" in s:
        score += 0.08
    if "usage" in s and "installation" in s:
        score += 0.15
    return float(clamp01(score))

def fundamental_depth(info: dict) -> float:
    imps = [i.split(".")[0] for i in info.get("imports", [])]
    hits = sum(1 for i in imps if i in LOW_LEVEL_IMPORTS)
    return float(clamp01(hits / 8.0))

def complexity_norm(x: float) -> float:
    return float(clamp01(math.tanh(x / 15.0)))

def category_avg(cats: Dict[str, float]) -> float:
    if not cats:
        return 0.0
    return float(sum(cats.values()) / (len(cats) * 100.0))

def semantic_score(comp: float, cats: Dict[str, float], dq: Dict[str, float], rtr: float, fdepth: float) -> float:
    c = complexity_norm(comp)
    a = category_avg(cats)
    dq_mix = 0.6 * dq["docstring_coverage"] + 0.4 * dq["comment_density"]
    score01 = 0.35*c + 0.30*a + 0.20*dq_mix + 0.10*rtr + 0.05*fdepth
    return float(round(pct(score01), 1))

# ───────────────────────────────────────────────────────────────────────────
#                         PDD GENERATION (FAST & STAT)
# ───────────────────────────────────────────────────────────────────────────
def pdd_skeleton(path: Path, source: str, info: dict,
                 comp: float, cats: Dict[str,float],
                 dq: Dict[str,float], rtr: float, fdepth: float,
                 sem_score: float, stats: dict) -> str:
    lines = []
    lines.append(f"# Program Design Document — {path.name}")
    lines.append("")
    lines.append("## Overview")
    lines.append(f"- **File**: `{path}`")
    lines.append(f"- **Approx. Lines**: {source.count(os.linesep) + 1}")
    if info["imports"]:
        lines.append(f"- **Imports**: {', '.join(sorted(set(info['imports'])))}")
    lines.append("")
    if info["classes"]:
        lines.append("## Classes")
        for cls in info["classes"]:
            lines.append(f"### class {cls['name']}")
            if cls["doc"].strip():
                lines.append(cls["doc"].strip())
            if cls["methods"]:
                lines.append("**Methods:**")
                for m in cls["methods"]:
                    sig = f"{m['name']}({', '.join(m['args'])})"
                    lines.append(f"- `{sig}`")
                    if m["doc"].strip():
                        lines.append(f"  - {m['doc'].strip()}")
            lines.append("")
    if info["functions"]:
        lines.append("## Functions")
        for fn in info["functions"]:
            sig = f"{fn['name']}({', '.join(fn['args'])})"
            lines.append(f"### def {sig}")
            if fn["doc"].strip():
                lines.append(fn["doc"].strip())
            lines.append("")

    hints = []
    if "open(" in source or "pathlib" in source:
        hints.append("File I/O")
    if "requests" in source or "http" in source:
        hints.append("Network")
    if "threading" in source or "asyncio" in source:
        hints.append("Concurrency")
    if "PyQt" in source or "tkinter" in source or "panda3d" in source:
        hints.append("GUI")
    if hints:
        lines.append("## Behavior Hints")
        lines.append("- " + ", ".join(hints))
        lines.append("")

    # Statistics + Semantic Profile
    lines.append("## Statistics")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Lines | {stats.get('Lines', '')} |")
    lines.append(f"| Imports | {stats.get('Imports','')} |")
    lines.append(f"| Classes | {stats.get('Classes','')} |")
    lines.append(f"| Functions | {stats.get('Functions','')} |")
    lines.append(f"| Complexity | {comp:.2f} |")
    lines.append("")
    lines.append("## Semantic Profile")
    lines.append("| Component | Score |")
    lines.append("|---|---:|")
    lines.append(f"| Docstring Coverage | {round(dq['docstring_coverage']*100,1)} |")
    lines.append(f"| Comment Density | {round(dq['comment_density']*100,1)} |")
    lines.append(f"| Module Docstring | {int(dq['module_doc']*100)} |")
    lines.append(f"| README Template Readiness | {round(rtr*100,1)} |")
    lines.append(f"| Fundamental Depth | {round(fdepth*100,1)} |")
    lines.append(f"| Category Avg | {round(category_avg(cats)*100,1)} |")
    for cat in CATEGORY_ORDER:
        lines.append(f"| Category: {cat} | {cats.get(cat,0.0):.1f} |")
    lines.append(f"| **Semantic Score** | **{sem_score:.1f}** |")
    lines.append("")
    lines.append("## Notes")
    lines.append("- This is a FAST skeleton. Enable *Deepen Selected* to append LLM-authored narratives for classes/functions.")
    return "\n".join(lines)

def deepen_chunks_prompt() -> str:
    return (
        "You are an expert Python software analyst. For the given code block, produce a precise, "
        "developer-grade narrative covering:\n"
        "• What this function/class does\n"
        "• Key inputs/outputs and side effects\n"
        "• Interactions with other parts of the file\n"
        "• Edge cases, error handling, and performance notes\n"
        "Write 4–10 concise bullet points. Do not invent APIs."
    )

def chunk_text(s: str, n: int) -> List[str]:
    if len(s) <= n:
        return [s]
    return [s[i:i + n] for i in range(0, len(s), n)]

# ───────────────────────────────────────────────────────────────────────────
#                             INDEX MANAGEMENT
# ───────────────────────────────────────────────────────────────────────────
class IndexManager:
    def __init__(self, index_dir=INDEX_DIR, dim=768):
        self.index_path = Path(index_dir) / "heat.index"
        self.dim = dim
        self.idx = None
        self.load_or_new()

    def load_or_new(self):
        if faiss is None:
            log.warning("FAISS unavailable — vector search disabled.")
            self.idx = None
            return
        if self.index_path.exists():
            try:
                self.idx = faiss.read_index(str(self.index_path))
                return
            except Exception as e:
                log.warning(f"FAISS read failed: {e}")
        self.idx = faiss.IndexFlatL2(self.dim)

    def save(self):
        if self.idx is not None:
            try:
                faiss.write_index(self.idx, str(self.index_path))
            except Exception as e:
                log.error(f"FAISS save failed: {e}")

    def rebuild(self, vecs: List[np.ndarray]):
        if faiss is None:
            return
        self.idx = faiss.IndexFlatL2(self.dim)
        if vecs:
            mat = np.stack(vecs).astype("float32")
            self.idx.add(mat)

    def search(self, vec: np.ndarray, k=5):
        if self.idx is None:
            return np.array([]), np.array([])
        q = vec.reshape(1, -1).astype("float32")
        D, I = self.idx.search(q, k)
        return D[0], I[0]

# ───────────────────────────────────────────────────────────────────────────
#                            FAST PIPELINE THREAD
# ───────────────────────────────────────────────────────────────────────────
class FastPipeline(threading.Thread):
    """
    FAST PASS: AST → stats → PDD skeleton → embeddings (parallel), with semantic scoring.
    Deduplicates on content hash (sha1). Maintains path->sha and sha->paths[].
    """
    def __init__(
        self, roots: List[str], excludes_regex: List[str], cfg: Config,
        meta: MetadataStore, scache: ScanCache,
        status_cb, log_cb, progress_cb, counters_cb,
        pause_event: threading.Event
    ):
        super().__init__(daemon=True)
        self.roots      = [Path(r) for r in roots]
        self.ex_re      = [re.compile(p, re.IGNORECASE) for p in excludes_regex] if excludes_regex else []
        self.cfg        = cfg
        self.meta       = meta
        self.scache     = scache
        self.status_cb  = status_cb
        self.log_cb     = log_cb
        self.progress_cb= progress_cb
        self.counters_cb= counters_cb
        self.pause_event= pause_event

        self.q_files  = queue.Queue(maxsize=4 * cfg.max_fast_workers)
        self.q_embed  = queue.Queue(maxsize=4 * cfg.max_embed_workers)
        self.stop_flag= False

        self.total_paths = 0
        self.done_paths  = 0

        self.unique_shas    = set()
        self.unique_lock    = threading.Lock()

        self.start_ts      = time.time()
        self.last_rate_ts  = self.start_ts
        self.last_done     = 0

        self.fast_workers  = []
        self.embed_workers = []

    def stop(self):
        self.stop_flag = True

    def _excluded(self, dirpath: str) -> bool:
        if excluded_dirpath(dirpath):
            return True
        if self.ex_re and any(rx.search(dirpath) for rx in self.ex_re):
            return True
        return False

    def _scan(self):
        files = []
        for root in self.roots:
            if not root.exists():
                continue
            for dirpath, dirnames, filenames in os.walk(root):
                if self.stop_flag:
                    break
                if self._excluded(dirpath):
                    # prevent descent
                    dirnames[:] = []
                    continue
                # only .py files
                for fn in filenames:
                    if fn.lower().endswith(".py"):
                        files.append(Path(dirpath) / fn)
        self.total_paths = len(files)
        self.status_cb(f"Found {self.total_paths} Python file paths.")
        for p in files:
            self.q_files.put(p)
        for _ in range(self.cfg.max_fast_workers):
            self.q_files.put(None)

    def _fast_worker(self, idx: int):
        while not self.stop_flag:
            p = self.q_files.get()
            if p is None:
                self.q_files.task_done()
                break

            while self.pause_event.is_set():
                time.sleep(0.25)

            spath = str(p)
            try:
                st = p.stat()
                mtime, size = st.st_mtime, st.st_size
            except Exception:
                self.done_paths += 1
                self._tick_progress(spath)
                self.q_files.task_done()
                continue

            # Hash first for dedup (unique script identity)
            try:
                sha = sha1_file(p)
            except Exception:
                self.done_paths += 1
                self._tick_progress(spath)
                self.q_files.task_done()
                continue

            # Update unique shas count
            with self.unique_lock:
                new_sha = sha not in self.unique_shas
                if new_sha:
                    self.unique_shas.add(sha)

            # If path not changed vs cache (and sha matches), just append its path to meta and continue
            if not self.scache.changed(spath, mtime, size, sha):
                # path is known; ensure meta has this path
                if sha in self.meta.records:
                    self.meta.append_path(sha, spath)
                    self.meta.save()
                self.done_paths += 1
                self._tick_progress(spath)
                self.q_files.task_done()
                continue

            src  = safe_read(p)
            info = ast_info(src)
            comp = measure_complexity(src, info)
            cats = category_weights(src)
            dq   = doc_quality(src, info)
            rtr  = readme_template_readiness(src)
            fdep = fundamental_depth(info)
            sem  = semantic_score(comp, cats, dq, rtr, fdep)

            stats = {
                "Lines":      src.count("\n") + 1,
                "Imports":    len(info["imports"]),
                "Classes":    len(info["classes"]),
                "Functions":  len(info["functions"]),
            }

            base     = f"{sha}__{slugify(p.name)}"
            pdd_path = PDD_DIR / f"{base}.md"
            sum_path = SUM_DIR / f"{base}.txt"

            # If we've already created this sha's PDD, don't regenerate; just append path
            if sha in self.meta.records and Path(self.meta.records[sha].get("pdd","")).exists():
                self.meta.append_path(sha, spath)
                # still refresh cache entries
                self.scache.update(spath, mtime, size, sha)
                self.meta.save()
                self.scache.save()
            else:
                pdd_text = pdd_skeleton(p, src, info, comp, cats, dq, rtr, fdep, sem, stats)
                try:
                    pdd_path.write_text(pdd_text, encoding="utf-8")
                    if not sum_path.exists():
                        sum_path.write_text("FAST skeleton created.\n", encoding="utf-8")
                except Exception:
                    pass

                rec = {
                    "sha":        sha,
                    "mtime":      mtime,
                    "size":       size,
                    "pdd":        str(pdd_path),
                    "summary":    str(sum_path),
                    "vector":     None,
                    "categories": cats,
                    "complexity": comp,
                    "stats":      stats,
                    "doc_quality": dq,
                    "readme_ready": rtr,
                    "fundamental_depth": fdep,
                    "semantic_score": sem,
                    "favorite":   self.meta.records.get(sha,{}).get("favorite", False)
                }
                self.meta.upsert(sha, rec, new_path=spath)
                self.scache.update(spath, mtime, size, sha)
                self.meta.save()
                self.scache.save()

                # embed on first time (per sha). Embed source from PDD or source.
                embed_source = pdd_text if self.cfg.fast_embed_from == "pdd" else src
                self.q_embed.put((sha, base, embed_source))

            self.done_paths += 1
            self._tick_progress(spath)
            self.q_files.task_done()

    def _embed_worker(self, idx: int):
        while not self.stop_flag:
            item = self.q_embed.get()
            if item is None:
                self.q_embed.task_done()
                break

            while self.pause_event.is_set():
                time.sleep(0.25)

            sha, base, text = item

            # If vector already exists for sha, skip
            rec = self.meta.records.get(sha)
            if rec and rec.get("vector") and Path(rec["vector"]).exists():
                self.q_embed.task_done()
                continue

            tmp_vec = ollama_embed(self.cfg.embed_model, text)
            vec = tmp_vec if tmp_vec is not None else dummy_embed(text, 768)

            vec_path = VEC_DIR / f"{base}.npy"
            try:
                np.save(str(vec_path), vec.astype("float32"))
            except Exception:
                pass

            rec = self.meta.records.get(sha)
            if rec:
                rec["vector"] = str(vec_path)
                self.meta.save()

            self.q_embed.task_done()

    def _tick_progress(self, current_file: str):
        pct_val = int((self.done_paths / max(self.total_paths, 1)) * 100)
        self.progress_cb(pct_val)
        now = time.time()
        if now - self.last_rate_ts >= 1.0:
            rate      = (self.done_paths - self.last_done) / (now - self.last_rate_ts)
            remaining = self.total_paths - self.done_paths
            eta       = remaining / max(rate, 1e-6)
            self.last_rate_ts = now
            self.last_done    = self.done_paths
            self.counters_cb(self.total_paths, self.done_paths, rate, eta)

    def run(self):
        for i in range(self.cfg.max_embed_workers):
            t = threading.Thread(target=self._embed_worker, args=(i,), daemon=True)
            t.start()
            self.embed_workers.append(t)
        for i in range(self.cfg.max_fast_workers):
            t = threading.Thread(target=self._fast_worker, args=(i,), daemon=True)
            t.start()
            self.fast_workers.append(t)

        self._scan()

        for t in self.fast_workers:
            t.join()
        for _ in range(self.cfg.max_embed_workers):
            self.q_embed.put(None)
        for t in self.embed_workers:
            t.join()

        uniq = 0
        with self.unique_lock:
            uniq = len(self.unique_shas)
        self.status_cb(f"FAST pass complete. Paths: {self.total_paths} → Unique scripts by content: {uniq}.")

# ───────────────────────────────────────────────────────────────────────────
#                              DEEPEN WORKER (LLM PASS)
# ───────────────────────────────────────────────────────────────────────────
class DeepenWorker(QThread):
    status   = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, shas: List[str], cfg: Config, meta: MetadataStore):
        super().__init__()
        self.shas = shas
        self.cfg  = cfg
        self.meta = meta
        self.stop_flag = False

    def stop(self):
        self.stop_flag = True

    def run(self):
        total = len(self.shas)
        for idx, sha in enumerate(self.shas):
            if self.stop_flag:
                break
            rec = self.meta.records.get(sha)
            if not rec:
                continue

            # choose a representative path for this sha
            paths = rec.get("paths", [])
            if not paths:
                continue
            path = Path(paths[0])

            src  = safe_read(path)
            info = ast_info(src)

            chunks = []
            for cls in info["classes"]:
                block = self._extract_block(src, cls["name"], is_class=True)
                if block:
                    chunks.append((f"class {cls['name']}", block))
            for fn in info["functions"]:
                block = self._extract_block(src, fn["name"], is_class=False)
                if block:
                    chunks.append((f"def {fn['name']}", block))
            if not chunks:
                for chunk in chunk_text(src, FAST_CHUNK_CHARS):
                    chunks.append(("module chunk", chunk))

            sys_prompt = deepen_chunks_prompt()
            deep_sections = []
            for title, code in chunks:
                prompt = f"{sys_prompt}\n\n{title} code:\n```python\n{code}\n```"
                part = ollama_generate(self.cfg.llm_model, prompt)
                deep_sections.append(f"### {title}\n{part.strip() or '(no response)'}\n")

            pdd_path = Path(rec["pdd"])
            pdd_text = pdd_path.read_text(encoding="utf-8", errors="ignore") if pdd_path.exists() else ""
            pdd_text += "\n\n## Deep Analysis\n" + "\n".join(deep_sections)
            pdd_path.write_text(pdd_text, encoding="utf-8")

            sum_path = Path(rec["summary"])
            sum_text = sum_path.read_text(encoding="utf-8", errors="ignore") if sum_path.exists() else ""
            sum_text += "\n\n" + "\n".join(deep_sections)
            sum_path.write_text(sum_text, encoding="utf-8")

            # Embeddings after deepening (vector refresh)
            tmp_vec = ollama_embed(self.cfg.embed_model, pdd_text)
            vec = tmp_vec if tmp_vec is not None else dummy_embed(pdd_text, 768)
            base = f"{sha}__{slugify(path.name)}"
            vec_path = VEC_DIR / f"{base}.npy"
            np.save(str(vec_path), vec.astype("float32"))
            rec["vector"] = str(vec_path)
            self.meta.save()

            self.status.emit(f"Deepened: {Path(path).name}")
            self.progress.emit(int((idx + 1) / max(total, 1) * 100))

        self.finished.emit()

    def _extract_block(self, source: str, name: str, is_class: bool) -> Optional[str]:
        pattern = rf"\b{'class' if is_class else 'def'}\s+{re.escape(name)}\b"
        match = re.search(pattern, source)
        if not match:
            return None
        start = match.start()
        tail  = source[start:]
        next_match = re.search(r"\n(?:class|def)\s+\w+", tail)
        end   = start + (next_match.start() if next_match else len(tail))
        return source[start:end]

# ───────────────────────────────────────────────────────────────────────────
#                         MATPLOTLIB-BASED CANVASES
# ───────────────────────────────────────────────────────────────────────────
class RadarCanvas(FigureCanvas):
    def __init__(self, categories: List[str]):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111, polar=True)
        self.categories = categories
        self._configure_base()

    def _configure_base(self):
        self.ax.set_theta_offset(np.pi / 2)
        self.ax.set_theta_direction(-1)
        ticks = np.linspace(0, 2 * np.pi, len(self.categories), endpoint=False)
        self.ax.set_xticks(ticks)
        self.ax.set_xticklabels(self.categories)
        self.ax.set_ylim(0, 100)

    def plot(self, scores: Dict[str, float], title: str = ""):
        self.ax.clear()
        self._configure_base()
        cats   = self.categories
        values = [scores.get(c, 0.0) for c in cats] + [scores.get(cats[0], 0.0)]
        angles = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist() + [0]
        self.ax.plot(angles, values)
        self.ax.fill(angles, values, alpha=0.25)
        self.ax.set_title(title)
        self.draw()

class HeatGridCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(6, 5), dpi=100)
        super().__init__(self.fig)
        self.ax  = self.fig.add_subplot(111)

    def plot(self, rows: List[str], cols: List[str], data: np.ndarray, title: str = ""):
        self.ax.clear()
        self.ax.invert_yaxis()
        cmap = matplotlib.cm.get_cmap("RdYlGn")
        norm = matplotlib.colors.Normalize(vmin=0, vmax=100)
        im = self.ax.imshow(data, aspect="auto", cmap=cmap, norm=norm)
        filenames = [Path(r).name for r in rows]
        self.ax.set_yticks(np.arange(len(filenames)))
        self.ax.set_yticklabels(filenames)
        self.ax.set_xticks(np.arange(len(cols)))
        self.ax.set_xticklabels(cols, rotation=45, ha="right")
        for y in range(len(filenames)+1):
            self.ax.axhline(y - 0.5, color="w", linewidth=0.5)
        self.ax.set_title(title)
        cbar = self.fig.colorbar(im, ax=self.ax, fraction=0.046, pad=0.04)
        cbar.set_label("Category score")
        cbar.set_ticks([0, 25, 50, 75, 100])
        self.fig.tight_layout()
        self.draw()

# ───────────────────────────────────────────────────────────────────────────
#                             PRE-SCAN DIALOG (NEW)
# ───────────────────────────────────────────────────────────────────────────
class PreScanWorker(QThread):
    row     = pyqtSignal(str, str, int, int)  # root, folder, count, size_bytes
    progress= pyqtSignal(int, int)            # done, total
    finished= pyqtSignal()

    def __init__(self, roots: List[str], user_excludes: List[str]):
        super().__init__()
        self.roots = [Path(r) for r in roots]
        self.re = [re.compile(p, re.IGNORECASE) for p in user_excludes] if user_excludes else []

    def _excluded(self, dirpath: str) -> bool:
        if excluded_dirpath(dirpath):
            return True
        if self.re and any(rx.search(dirpath) for rx in self.re):
            return True
        return False

    def _count_dir(self, top: Path) -> Tuple[int, int]:
        count = 0
        size  = 0
        for dirpath, dirnames, filenames in os.walk(top):
            if self._excluded(dirpath):
                dirnames[:] = []
                continue
            for fn in filenames:
                if fn.lower().endswith(".py"):
                    count += 1
                    try:
                        size += (Path(dirpath)/fn).stat().st_size
                    except Exception:
                        pass
        return count, size

    def run(self):
        # Build a list of "top-level entries" across all roots
        top_entries: List[Tuple[Path, Optional[Path]]] = []  # (root, child_dir_or_None_for_root_files)
        for root in self.roots:
            if not root.exists():
                continue
            # Child dirs
            try:
                for child in sorted([p for p in root.iterdir() if p.is_dir()]):
                    top_entries.append((root, child))
            except Exception:
                pass
            # Root files bucket
            top_entries.append((root, None))

        total = len(top_entries)
        done  = 0
        self.progress.emit(done, total)
        for root, child in top_entries:
            if child is None:
                # Count only files directly under root (not subfolders)
                cnt = 0
                size = 0
                try:
                    for p in root.iterdir():
                        if p.is_file() and p.suffix.lower() == ".py":
                            cnt += 1
                            try:
                                size += p.stat().st_size
                            except Exception:
                                pass
                except Exception:
                    pass
                name = "(root)"
                self.row.emit(str(root), name, cnt, size)
            else:
                if self._excluded(str(child)):
                    # fully excluded subtree
                    self.row.emit(str(root), child.name + " [excluded]", 0, 0)
                else:
                    cnt, size = self._count_dir(child)
                    self.row.emit(str(root), child.name, cnt, size)
            done += 1
            self.progress.emit(done, total)
        self.finished.emit()

class PreScanDialog(QDialog):
    def __init__(self, parent: QWidget, roots: List[str], user_excludes: List[str]):
        super().__init__(parent)
        self.setWindowTitle("Pre-Scan (.py counts)")
        self.resize(1100, 700)

        self.rows: List[Tuple[str,str,int,int]] = []  # (root, folder, count, size)
        self._setup_ui()

        self.worker = PreScanWorker(roots, user_excludes)
        self.worker.row.connect(self._add_row)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.lbl_roots = QLabel("")
        layout.addWidget(self.lbl_roots)

        prog_row = QHBoxLayout()
        self.progress = QProgressBar()
        prog_row.addWidget(self.progress)
        self.lbl_prog = QLabel("0 / 0")
        prog_row.addWidget(self.lbl_prog)
        layout.addLayout(prog_row)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Root", "Top Folder", ".py Count", "Size (MB)", "Share (%)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 3)

        # Chart
        chart_box = QVBoxLayout()
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, 2)

        # Actions
        btns = QHBoxLayout()
        self.btn_export = QPushButton("Export CSV…")
        self.btn_export.clicked.connect(self._export_csv)
        btns.addWidget(self.btn_export)
        btns.addStretch()
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        btns.addWidget(self.btn_close)
        layout.addLayout(btns)

    def _add_row(self, root: str, folder: str, count: int, size: int):
        self.rows.append((root, folder, count, size))
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(root))
        self.table.setItem(row, 1, QTableWidgetItem(folder))
        self.table.setItem(row, 2, QTableWidgetItem(str(count)))
        self.table.setItem(row, 3, QTableWidgetItem(f"{size/1_000_000:.2f}"))
        # Share filled in after totals known
        self.table.setItem(row, 4, QTableWidgetItem(""))

    def _on_progress(self, done: int, total: int):
        self.progress.setMaximum(max(1,total))
        self.progress.setValue(done)
        self.lbl_prog.setText(f"{done} / {total}")
        # Update roots label on first call
        if not self.lbl_roots.text():
            self.lbl_roots.setText("Roots: " + ", ".join(sorted(set(r for r,_,_,_ in self.rows))))

    def _on_finished(self):
        # Compute shares and draw chart
        total_py = sum(c for _,_,c,_ in self.rows)
        for i in range(self.table.rowCount()):
            cnt = int(self.table.item(i,2).text())
            share = (cnt / total_py * 100.0) if total_py else 0.0
            self.table.setItem(i, 4, QTableWidgetItem(f"{share:.1f}"))
        self._draw_chart()
        QMessageBox.information(self, "Pre-Scan", f"Counted {total_py} Python files across top-level folders.")

    def _draw_chart(self, top_n: int = 40):
        # Top N folders by count
        data = sorted(self.rows, key=lambda x: x[2], reverse=True)[:top_n]
        if not data:
            self.ax.clear()
            self.canvas.draw()
            return
        names = [f"{Path(root).name}/{folder}" for root,folder,_,_ in data]
        counts = [c for _,_,c,_ in data]
        self.ax.clear()
        y = np.arange(len(names))
        self.ax.barh(y, counts)
        self.ax.set_yticks(y)
        self.ax.set_yticklabels(names)
        self.ax.invert_yaxis()
        self.ax.set_xlabel(".py count")
        self.ax.set_title("Top folders by Python-file count")
        self.fig.tight_layout()
        self.canvas.draw()

    def _export_csv(self):
        f, _ = QFileDialog.getSaveFileName(self, "Export CSV", str(EXPORTS_DIR / "prescan_counts.csv"), "CSV Files (*.csv)")
        if not f:
            return
        try:
            with open(f, "w", encoding="utf-8") as out:
                out.write("root,folder,py_count,size_bytes\n")
                for root, folder, cnt, size in self.rows:
                    out.write(f"\"{root}\",\"{folder}\",{cnt},{size}\n")
            QMessageBox.information(self, "Exported", f"CSV exported to: {f}")
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))

# ───────────────────────────────────────────────────────────────────────────
#                              GUI: TABS
# ───────────────────────────────────────────────────────────────────────────
STAR_FILLED = "★"
STAR_EMPTY  = "☆"

def star_for(rec: dict) -> str:
    return STAR_FILLED if rec.get("favorite") else STAR_EMPTY

class ScanTab(QWidget):
    start_fast = pyqtSignal(list, list)  # roots, excludes
    deepen     = pyqtSignal(list)        # list of shas

    def __init__(self, cfg_mgr: ConfigManager, meta: MetadataStore):
        super().__init__()
        self.cfg_mgr = cfg_mgr
        self.meta    = meta
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Roots selection
        roots_layout = QHBoxLayout()
        roots_layout.addWidget(QLabel("Roots:"))
        self.txt_roots = QLineEdit(",".join(self.cfg_mgr.cfg.selected_roots))
        self.txt_roots.setPlaceholderText("C:\\, D:\\, E:\\  (comma-separated)")
        roots_layout.addWidget(self.txt_roots, 1)
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self._add_root)
        roots_layout.addWidget(btn_browse)
        btn_drives = QPushButton("Drives")
        btn_drives.clicked.connect(self._show_drives)
        roots_layout.addWidget(btn_drives)
        layout.addLayout(roots_layout)

        # Excludes editor (regex, optional)
        layout.addWidget(QLabel("Additional exclusion regex (one per line, optional):"))
        self.txt_exc = QPlainTextEdit("\n".join(self.cfg_mgr.cfg.user_excludes or []))
        self.txt_exc.setMinimumHeight(80)
        self.txt_exc.setToolTip("Paths matching these regexes will be skipped (case-insensitive).")
        layout.addWidget(self.txt_exc)

        # Model & concurrency controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("LLM:"))
        self.cmb_llm = QComboBox()
        self.cmb_llm.addItems(ALLOWED_MODELS)  # ← fixed indentation
        self.cmb_llm.setCurrentText(self.cfg_mgr.cfg.llm_model)
        controls.addWidget(self.cmb_llm)

        controls.addWidget(QLabel("Embed:"))
        self.cmb_emb = QComboBox()
        self.cmb_emb.addItems(ALLOWED_MODELS)
        self.cmb_emb.setCurrentText(self.cfg_mgr.cfg.embed_model)
        controls.addWidget(self.cmb_emb)

        self.chk_cpu = QCheckBox("CPU Guard")
        self.chk_cpu.setToolTip("Pause scanning if CPU usage is too high.")
        self.chk_cpu.setChecked(self.cfg_mgr.cfg.cpu_guard)
        controls.addWidget(self.chk_cpu)

        controls.addWidget(QLabel("Embed from:"))
        self.cmb_embed_src = QComboBox()
        self.cmb_embed_src.addItems(["pdd", "source"])
        self.cmb_embed_src.setCurrentText(self.cfg_mgr.cfg.fast_embed_from)
        controls.addWidget(self.cmb_embed_src)

        controls.addWidget(QLabel("FAST workers:"))
        self.sp_fast = QSpinBox()
        self.sp_fast.setRange(1, 64)
        self.sp_fast.setValue(self.cfg_mgr.cfg.max_fast_workers)
        controls.addWidget(self.sp_fast)

        controls.addWidget(QLabel("EMBED workers:"))
        self.sp_emb = QSpinBox()
        self.sp_emb.setRange(1, 64)
        self.sp_emb.setValue(self.cfg_mgr.cfg.max_embed_workers)
        controls.addWidget(self.sp_emb)

        controls.addWidget(QLabel("DEEP workers:"))
        self.sp_deep = QSpinBox()
        self.sp_deep.setRange(1, 32)
        self.sp_deep.setValue(self.cfg_mgr.cfg.max_deep_workers)
        controls.addWidget(self.sp_deep)

        # Deepen Selected checkbox
        self.chk_deepen = QCheckBox("Deepen Selected after FAST")
        self.chk_deepen.setChecked(self.cfg_mgr.cfg.deep_on_finish)
        self.chk_deepen.setToolTip("When enabled, runs Deep pass on the selected rows after FAST finishes.")
        controls.addWidget(self.chk_deepen)

        layout.addLayout(controls)

        # Progress indicators
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.lbl_counters = QLabel("Queued: 0 • Done: 0 • 0.0 it/s • ETA: —")
        layout.addWidget(self.lbl_counters)

        # Log output
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log, 1)

        # Actions row
        actions = QHBoxLayout()
        btn_save = QPushButton("Save Prefs")
        btn_save.clicked.connect(self._save_config)
        actions.addWidget(btn_save)

        btn_prescan = QPushButton("Pre-Scan (.py counts)")
        btn_prescan.clicked.connect(self._open_prescan)
        actions.addWidget(btn_prescan)

        btn_scan = QPushButton("FAST Scan / Sync")
        btn_scan.clicked.connect(self._start_scan)
        actions.addWidget(btn_scan)

        btn_deepen_now = QPushButton("Deepen Now (Selected)")
        btn_deepen_now.clicked.connect(self._deepen_selection)
        actions.addWidget(btn_deepen_now)

        actions.addStretch()
        layout.addLayout(actions)

        # Splitter: left table + right PDD preview
        splitter = QSplitter()
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Results table — using sha identity
        # Cols: [★, Name, Complexity, SemScore, SHA, Paths]
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["★", "Name", "Complexity", "SemScore", "SHA", "Paths"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._context_menu)
        self.table.cellClicked.connect(self._cell_clicked)
        self.table.itemSelectionChanged.connect(self._on_selection_change)
        left_layout.addWidget(self.table, 2)

        splitter.addWidget(left_panel)

        # Right: PDD Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.addWidget(QLabel("PDD Preview"))
        self.pdd_preview = QPlainTextEdit()
        self.pdd_preview.setReadOnly(True)
        right_layout.addWidget(self.pdd_preview, 1)
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter, 2)

        self._refresh_table()

    def _add_root(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Root")
        if d:
            roots = [p.strip() for p in self.txt_roots.text().split(",") if p.strip()]
            if d not in roots:
                roots.append(d)
                self.txt_roots.setText(",".join(roots))

    def _show_drives(self):
        drives = list_windows_drives()
        QMessageBox.information(self, "Available Drives", "\n".join(drives))

    def _save_config(self):
        cfg = self.cfg_mgr.cfg
        cfg.selected_roots   = [p.strip() for p in self.txt_roots.text().split(",") if p.strip()]
        # normalize/trim user regex lines
        cfg.user_excludes    = [ln.strip() for ln in self.txt_exc.toPlainText().splitlines() if ln.strip()]
        cfg.llm_model        = ensure_model(self.cmb_llm.currentText(), DEFAULT_LLM)
        cfg.embed_model      = ensure_model(self.cmb_emb.currentText(), DEFAULT_EMBED)
        cfg.cpu_guard        = self.chk_cpu.isChecked()
        cfg.fast_embed_from  = self.cmb_embed_src.currentText()
        cfg.max_fast_workers = self.sp_fast.value()
        cfg.max_embed_workers= self.sp_emb.value()
        cfg.max_deep_workers = self.sp_deep.value()
        cfg.deep_on_finish   = self.chk_deepen.isChecked()
        self.cfg_mgr.save()
        self._log("Preferences saved.")

    def _open_prescan(self):
        self._save_config()
        roots = self.cfg_mgr.cfg.selected_roots
        if not roots:
            QMessageBox.warning(self, "Roots Required", "Add at least one root directory.")
            return
        dlg = PreScanDialog(self, roots, self.cfg_mgr.cfg.user_excludes or [])
        dlg.exec()

    def _start_scan(self):
        self._save_config()
        roots = self.cfg_mgr.cfg.selected_roots
        if not roots:
            QMessageBox.warning(self, "Roots Required", "Add at least one root directory.")
            return
        excludes = self.cfg_mgr.cfg.user_excludes or []
        self.start_fast.emit(roots, excludes)

    def _deepen_selection(self):
        selected = self.table.selectionModel().selectedRows()
        shas = [self.table.item(r.row(), 4).text() for r in selected]
        if not shas:
            QMessageBox.warning(self, "No Selection", "Select one or more rows first.")
            return
        self.deepen.emit(shas)

    def _context_menu(self, pos):
        row = self.table.currentRow()
        if row < 0:
            return
        sha = self.table.item(row, 4).text()
        m = QMenu(self)
        act_toggle = m.addAction("Toggle Favorite")
        act_deepen = m.addAction("Deepen This")
        act = m.exec(self.table.viewport().mapToGlobal(pos))
        if act == act_toggle:
            fav = self.meta.toggle_favorite(sha)
            self.table.item(row, 0).setText(STAR_FILLED if fav else STAR_EMPTY)
        elif act == act_deepen:
            self.deepen.emit([sha])

    def _cell_clicked(self, row: int, col: int):
        if col == 0:
            sha = self.table.item(row, 4).text()
            fav = self.meta.toggle_favorite(sha)
            self.table.item(row, 0).setText(STAR_FILLED if fav else STAR_EMPTY)

    def _on_selection_change(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        sha = self.table.item(rows[0].row(), 4).text()
        rec = self.meta.records.get(sha)
        if not rec:
            return
        try:
            self.pdd_preview.setPlainText(Path(rec["pdd"]).read_text(encoding="utf-8"))
        except Exception:
            self.pdd_preview.setPlainText("(PDD not available)")

    def _refresh_table(self):
        recs = sorted(self.meta.records.values(), key=lambda r: (r.get("semantic_score",0.0), r.get("complexity",0.0)), reverse=True)
        self.table.setRowCount(len(recs))
        for i, r in enumerate(recs):
            star = QTableWidgetItem(star_for(r))
            star.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name = QTableWidgetItem(Path(r["paths"][0]).name if r.get("paths") else "?")
            tooltip = "\n".join(r.get("paths", [])[:20])
            if len(r.get("paths", [])) > 20:
                tooltip += f"\n… (+{len(r['paths']) - 20} more)"
            name.setToolTip(tooltip if tooltip else "(no paths)")
            cx   = QTableWidgetItem(f"{r.get('complexity',0.0):.1f}")
            ss   = QTableWidgetItem(f"{r.get('semantic_score',0.0):.1f}")
            sha  = QTableWidgetItem(r.get("sha",""))
            npaths = QTableWidgetItem(str(len(r.get("paths",[]))))
            self.table.setItem(i, 0, star)
            self.table.setItem(i, 1, name)
            self.table.setItem(i, 2, cx)
            self.table.setItem(i, 3, ss)
            self.table.setItem(i, 4, sha)
            self.table.setItem(i, 5, npaths)

    def set_progress(self, val: int):
        self.progress.setValue(val)

    def set_status(self, msg: str):
        self._log(msg)

    def set_counters(self, total: int, done: int, rate: float, eta: float):
        eta_str = time.strftime("%M:%S", time.gmtime(max(0, int(eta))))
        queued = total - done
        self.lbl_counters.setText(f"Queued: {queued} • Done: {done}/{total} • {rate:.1f} it/s • ETA: {eta_str}")

    def _log(self, msg: str):
        self.log.appendPlainText(msg)
        log.info(msg)

class HeatMapTab(QWidget):
    def __init__(self, meta: MetadataStore):
        super().__init__()
        self.meta = meta
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("View:"))
        self.view = QComboBox()
        self.view.addItems(["Radar (per selection)", "Grid Heat (all scripts)"])
        control_layout.addWidget(self.view)

        control_layout.addWidget(QLabel("Min complexity:"))
        self.min_comp = QSpinBox()
        self.min_comp.setRange(0, 5000)
        self.min_comp.setValue(0)
        control_layout.addWidget(self.min_comp)

        self.chk_favs = QCheckBox("Favorites only")
        control_layout.addWidget(self.chk_favs)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self._refresh)
        control_layout.addWidget(btn_refresh)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        splitter = QSplitter()

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["★", "Name", "Complexity", "SemScore", "SHA", "Paths"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.cellClicked.connect(self._cell_clicked)
        self.table.itemSelectionChanged.connect(self._on_selection_change)
        left_layout.addWidget(self.table, 2)

        self.info_tabs = QTabWidget()
        self.stats_table = QTableWidget(0, 2)
        self.stats_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.stats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.pdd_preview = QPlainTextEdit()
        self.pdd_preview.setReadOnly(True)
        self.info_tabs.addTab(self.stats_table, "Stats")
        self.info_tabs.addTab(self.pdd_preview, "PDD Preview")
        left_layout.addWidget(self.info_tabs, 3)

        splitter.addWidget(left_panel)

        self.radar_canvas = RadarCanvas(CATEGORY_ORDER)
        self.radar_toolbar = NavigationToolbar2QT(self.radar_canvas, self)
        radar_container = QWidget()
        rc_layout = QVBoxLayout(radar_container)
        rc_layout.setContentsMargins(0, 0, 0, 0)
        rc_layout.addWidget(self.radar_toolbar)
        rc_layout.addWidget(self.radar_canvas)

        self.grid_canvas = HeatGridCanvas()
        self.grid_toolbar = NavigationToolbar2QT(self.grid_canvas, self)
        grid_container = QWidget()
        gc_layout = QVBoxLayout(grid_container)
        gc_layout.setContentsMargins(0, 0, 0, 0)
        gc_layout.addWidget(self.grid_toolbar)
        grid_area = QScrollArea()
        grid_area.setWidget(self.grid_canvas)
        grid_area.setWidgetResizable(True)
        gc_layout.addWidget(grid_area)

        self.canvas_stack = QStackedWidget()
        self.canvas_stack.addWidget(radar_container)
        self.canvas_stack.addWidget(grid_container)

        splitter.addWidget(self.canvas_stack)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        layout.addWidget(splitter, 1)

        self.view.currentIndexChanged.connect(self._switch_view)
        self._refresh()

    def _filtered(self) -> List[dict]:
        thr = float(self.min_comp.value())
        favs_only = self.chk_favs.isChecked()
        vals = [r for r in self.meta.records.values() if r.get("complexity",0.0) >= thr]
        if favs_only:
            vals = [r for r in vals if r.get("favorite")]
        return vals

    def _refresh(self):
        recs = sorted(self._filtered(), key=lambda r: (r.get("semantic_score",0.0), r.get("complexity",0.0)), reverse=True)
        self.table.setRowCount(len(recs))
        for i, r in enumerate(recs):
            star = QTableWidgetItem(star_for(r))
            star.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name = QTableWidgetItem(Path(r["paths"][0]).name if r.get("paths") else "?")
            tooltip = "\n".join(r.get("paths", [])[:20])
            if len(r.get("paths", [])) > 20:
                tooltip += f"\n… (+{len(r['paths']) - 20} more)"
            name.setToolTip(tooltip if tooltip else "(no paths)")
            cx   = QTableWidgetItem(f"{r.get('complexity',0.0):.1f}")
            ss   = QTableWidgetItem(f"{r.get('semantic_score',0.0):.1f}")
            sha  = QTableWidgetItem(r.get("sha",""))
            npaths = QTableWidgetItem(str(len(r.get("paths",[]))))
            self.table.setItem(i, 0, star)
            self.table.setItem(i, 1, name)
            self.table.setItem(i, 2, cx)
            self.table.setItem(i, 3, ss)
            self.table.setItem(i, 4, sha)
            self.table.setItem(i, 5, npaths)
        self.table.setColumnHidden(4, True)  # hide sha in this view
        if self.view.currentIndex() == 1:
            self._draw_grid()

    def _switch_view(self, idx: int):
        self.canvas_stack.setCurrentIndex(idx)
        if idx == 1:
            self._draw_grid()

    def _cell_clicked(self, row: int, col: int):
        if col == 0:
            sha = self.table.item(row, 4).text()
            rec = self.meta.records.get(sha)
            fav = self.meta.toggle_favorite(sha)
            self.table.item(row, 0).setText(STAR_FILLED if fav else STAR_EMPTY)

    def _on_selection_change(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        sha = self.table.item(rows[0].row(), 4).text()
        rec = self.meta.records.get(sha)
        if not rec:
            return
        self._fill_stats(rec)
        try:
            self.pdd_preview.setPlainText(Path(rec["pdd"]).read_text(encoding="utf-8"))
        except Exception:
            self.pdd_preview.setPlainText("(PDD not available)")
        self.radar_canvas.plot(rec["categories"], title=Path(rec["paths"][0]).name if rec.get("paths") else "?")

    def _fill_stats(self, rec: dict):
        self.stats_table.setRowCount(0)
        stats = rec.get("stats", {})
        for key in ["Lines", "Imports", "Classes", "Functions"]:
            val = stats.get(key, "")
            row = self.stats_table.rowCount()
            self.stats_table.insertRow(row)
            self.stats_table.setItem(row, 0, QTableWidgetItem(key))
            self.stats_table.setItem(row, 1, QTableWidgetItem(str(val)))
        row = self.stats_table.rowCount()
        self.stats_table.insertRow(row)
        self.stats_table.setItem(row, 0, QTableWidgetItem("Complexity"))
        self.stats_table.setItem(row, 1, QTableWidgetItem(f"{rec.get('complexity',0.0):.2f}"))
        row = self.stats_table.rowCount()
        self.stats_table.insertRow(row)
        self.stats_table.setItem(row, 0, QTableWidgetItem("Semantic Score"))
        self.stats_table.setItem(row, 1, QTableWidgetItem(f"{rec.get('semantic_score',0.0):.1f}"))
        dq = rec.get("doc_quality", {})
        add = [
            ("Docstring Coverage", f"{dq.get('docstring_coverage',0.0)*100:.1f}"),
            ("Comment Density", f"{dq.get('comment_density',0.0)*100:.1f}"),
            ("Module Docstring", f"{int(dq.get('module_doc',0.0)*100)}"),
            ("README Template Ready", f"{rec.get('readme_ready',0.0)*100:.1f}"),
            ("Fundamental Depth", f"{rec.get('fundamental_depth',0.0)*100:.1f}"),
        ]
        for k, v in add:
            row = self.stats_table.rowCount()
            self.stats_table.insertRow(row)
            self.stats_table.setItem(row, 0, QTableWidgetItem(k))
            self.stats_table.setItem(row, 1, QTableWidgetItem(v))
        for cat in CATEGORY_ORDER:
            w = rec["categories"].get(cat, 0.0)
            row = self.stats_table.rowCount()
            self.stats_table.insertRow(row)
            self.stats_table.setItem(row, 0, QTableWidgetItem(f"Category: {cat}"))
            self.stats_table.setItem(row, 1, QTableWidgetItem(f"{w:.1f}"))

    def _draw_grid(self):
        recs = self._filtered()
        rows = [r["paths"][0] if r.get("paths") else "" for r in recs]
        cols = CATEGORY_ORDER
        data = np.zeros((len(rows), len(cols)), dtype=float)
        for i, r in enumerate(recs):
            for j, c in enumerate(cols):
                data[i, j] = r["categories"].get(c, 0.0)
        self.grid_canvas.plot(rows, cols, data, title="Category Heat Grid")

class PipelineTab(QWidget):
    def __init__(self, meta: MetadataStore):
        super().__init__()
        self.meta = meta
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.stack_name = QLineEdit()
        self.stack_name.setPlaceholderText("Stack name…")
        top.addWidget(self.stack_name)
        btn_save = QPushButton("Save Stack")
        btn_save.clicked.connect(self._save_stack)
        top.addWidget(btn_save)
        btn_load = QPushButton("Load Stack")
        btn_load.clicked.connect(self._load_stack)
        top.addWidget(btn_load)
        btn_favs = QPushButton("Load Favorites")
        btn_favs.clicked.connect(self._load_favorites)
        top.addWidget(btn_favs)
        top.addStretch()
        layout.addLayout(top)

        mid = QSplitter()

        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["★", "Name", "Complexity", "SemScore", "SHA", "Paths"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.cellClicked.connect(self._cell_clicked)
        self.table.itemSelectionChanged.connect(self._on_selection_change)
        left_layout.addWidget(self.table, 5)

        btn_layout = QVBoxLayout()
        btn_add = QPushButton("→ Add")
        btn_add.clicked.connect(self._add_to_basket)
        btn_layout.addWidget(btn_add)
        btn_remove = QPushButton("← Remove")
        btn_remove.clicked.connect(self._remove_from_basket)
        btn_layout.addWidget(btn_remove)
        btn_layout.addStretch()

        self.basket = QListWidget()

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.pdd_preview = QPlainTextEdit()
        self.pdd_preview.setReadOnly(True)
        right_layout.addWidget(QLabel("PDD Preview"))
        right_layout.addWidget(self.pdd_preview)

        mid.addWidget(left)
        control = QWidget()
        c_layout = QVBoxLayout(control)
        c_layout.addLayout(btn_layout)
        mid.addWidget(control)
        mid.addWidget(right)
        mid.setStretchFactor(0, 5)
        mid.setStretchFactor(1, 1)
        mid.setStretchFactor(2, 5)
        layout.addWidget(mid)

        actions = QHBoxLayout()
        btn_copy = QPushButton("Copy to…")
        btn_copy.clicked.connect(self._copy_basket)
        actions.addWidget(btn_copy)
        btn_move = QPushButton("Move to…")
        btn_move.clicked.connect(self._move_basket)
        actions.addWidget(btn_move)
        btn_export = QPushButton("Export PDDs (txt/json)")
        btn_export.clicked.connect(self._export_basket)
        actions.addWidget(btn_export)
        actions.addStretch()
        layout.addLayout(actions)

        self._refresh_table()

    def _refresh_table(self):
        recs = sorted(self.meta.records.values(), key=lambda r: (r.get("semantic_score",0.0), r.get("complexity",0.0)), reverse=True)
        self.table.setRowCount(len(recs))
        for i, r in enumerate(recs):
            star = QTableWidgetItem(star_for(r))
            star.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name = QTableWidgetItem(Path(r["paths"][0]).name if r.get("paths") else "?")
            tooltip = "\n".join(r.get("paths", [])[:20])
            if len(r.get("paths", [])) > 20:
                tooltip += f"\n… (+{len(r['paths']) - 20} more)"
            name.setToolTip(tooltip if tooltip else "(no paths)")
            cx   = QTableWidgetItem(f"{r.get('complexity',0.0):.1f}")
            ss   = QTableWidgetItem(f"{r.get('semantic_score',0.0):.1f}")
            sha  = QTableWidgetItem(r.get("sha",""))
            npaths = QTableWidgetItem(str(len(r.get("paths",[]))))
            self.table.setItem(i, 0, star)
            self.table.setItem(i, 1, name)
            self.table.setItem(i, 2, cx)
            self.table.setItem(i, 3, ss)
            self.table.setItem(i, 4, sha)
            self.table.setItem(i, 5, npaths)
        self.table.setColumnHidden(4, True)

    def _selected_paths(self) -> List[str]:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return []
        sha = self.table.item(rows[0].row(), 4).text()
        rec = self.meta.records.get(sha, {})
        return rec.get("paths", [])

    def _add_to_basket(self):
        for p in self._selected_paths():
            if not any(self.basket.item(i).text() == p for i in range(self.basket.count())):
                self.basket.addItem(p)

    def _remove_from_basket(self):
        for item in self.basket.selectedItems():
            self.basket.takeItem(self.basket.row(item))

    def _cell_clicked(self, row: int, col: int):
        if col == 0:
            sha = self.table.item(row, 4).text()
            fav = self.meta.toggle_favorite(sha)
            self.table.item(row, 0).setText(STAR_FILLED if fav else STAR_EMPTY)

    def _on_selection_change(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self.pdd_preview.setPlainText("")
            return
        sha = self.table.item(rows[0].row(), 4).text()
        rec = self.meta.records.get(sha, {})
        try:
            self.pdd_preview.setPlainText(Path(rec["pdd"]).read_text(encoding="utf-8"))
        except Exception:
            self.pdd_preview.setPlainText("(PDD not available)")

    def _load_favorites(self):
        self.basket.clear()
        for r in self.meta.records.values():
            if r.get("favorite"):
                for p in r.get("paths", []):
                    self.basket.addItem(p)

    def _save_stack(self):
        name = self.stack_name.text().strip() or time.strftime("%Y%m%d_%H%M%S")
        items = [self.basket.item(i).text() for i in range(self.basket.count())]
        path = STACKS_DIR / f"{name}.json"
        path.write_text(json.dumps(items, indent=2), encoding="utf-8")
        QMessageBox.information(self, "Stack Saved", f"Saved stack: {name}")

    def _load_stack(self):
        f, _ = QFileDialog.getOpenFileName(self, "Load Stack", str(STACKS_DIR), "JSON Files (*.json)")
        if not f:
            return
        items = json.loads(Path(f).read_text(encoding="utf-8"))
        self.basket.clear()
        for p in items:
            self.basket.addItem(p)
        self.stack_name.setText(Path(f).stem)

    def _copy_basket(self):
        dest = QFileDialog.getExistingDirectory(self, "Copy to")
        if not dest:
            return
        for i in range(self.basket.count()):
            src = self.basket.item(i).text()
            try:
                shutil.copy2(src, dest)
            except Exception as e:
                log.error(f"Copy failed for {src}: {e}")
        QMessageBox.information(self, "Copied", "Basket copied successfully.")

    def _move_basket(self):
        dest = QFileDialog.getExistingDirectory(self, "Move to")
        if not dest:
            return
        for i in range(self.basket.count()):
            src = self.basket.item(i).text()
            try:
                shutil.move(src, dest)
            except Exception as e:
                log.error(f"Move failed for {src}: {e}")
        QMessageBox.information(self, "Moved", "Basket moved successfully.")

    def _export_basket(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        txt_path = EXPORTS_DIR / f"{timestamp}.txt"
        json_path = EXPORTS_DIR / f"{timestamp}.json"
        data = {}
        for i in range(self.basket.count()):
            p = self.basket.item(i).text()
            # pick sha rec that contains p
            for rec in self.meta.records.values():
                if p in rec.get("paths", []):
                    if Path(rec["pdd"]).exists():
                        data[p] = Path(rec["pdd"]).read_text(encoding="utf-8")
                    break
        txt_path.write_text("\n\n".join(f"# {Path(k).name}\n{v}" for k, v in data.items()), encoding="utf-8")
        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        QMessageBox.information(self, "Exported", f"Exported to:\n{txt_path}\n{json_path}")

# ───────────────────────────────────────────────────────────────────────────
#                              MOVER TAB (ScriptMover workflow)
# ───────────────────────────────────────────────────────────────────────────
def analyze_script_for_readme(path: Path):
    try:
        code = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(code)
    except Exception as e:
        return "", [], [], [], code
    doc = ast.get_docstring(tree) or ""
    classes, funcs, imports = [], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports += [n.name for n in node.names]
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports += [f"{mod} → {n.name}" for n in node.names]
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            funcs.append(f"{node.name}({', '.join(args)})")
    return doc.strip(), sorted(set(classes)), sorted(set(funcs)), sorted(set(imports)), code

def generate_readme_for_script(path: Path):
    import datetime as dt
    doc, classes, funcs, imports, code = analyze_script_for_readme(path)
    return "\n".join([
        f"# {path.name}",
        f"*Cloned on {dt.datetime.now().isoformat(timespec='seconds')}*",
        f"Original location: `{path}`",
        "",
        "## Source",
        "```python",
        code.strip(),
        "```",
        "",
        "## Docstring", doc or "― None ―",
        "## Imports", ", ".join(imports) or "― None ―",
        "## Classes", ", ".join(classes) or "― None ―",
        "## Functions", ", ".join(funcs) or "― None ―",
        "---",
        "*README generated by PyHeatMapper • Mover*"
    ])

def has_python_files(path: Path) -> bool:
    for cur_root, dirs, files in os.walk(path):
        if excluded_dirpath(cur_root):
            continue
        if any(f.lower().endswith(".py") for f in files):
            return True
    return False

class ClipboardWatcher(threading.Thread):
    def __init__(self, on_files):
        super().__init__(daemon=True)
        self.on_files = on_files
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        if not HAS_WIN_CLIP:
            return
        prev = None
        while self.running:
            try:
                pythoncom.CoInitialize()
                file_list = []
                opened = False
                try:
                    win32clipboard.OpenClipboard()
                    opened = True
                    if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                        file_list = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                finally:
                    if opened:
                        win32clipboard.CloseClipboard()
                files = [Path(f) for f in file_list if Path(f).exists()]
                cur = tuple(files)
                if files and cur != prev:
                    prev = cur
                    self.on_files(list(files))
            except Exception:
                pass
            time.sleep(0.5)

class MoverTab(QWidget):
    def __init__(self, cfg_mgr: ConfigManager):
        super().__init__()
        self.cfg_mgr = cfg_mgr
        self._setup_ui()
        self.watcher: Optional[ClipboardWatcher] = None
        self._install_hotkey()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("Destination:"))
        self.txt_dest = QLineEdit(self.cfg_mgr.cfg.mover_destination)
        row.addWidget(self.txt_dest, 1)
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self._browse)
        row.addWidget(btn_browse)
        layout.addLayout(row)

        ctrl = QHBoxLayout()
        self.chk_docs = QCheckBox("Generate README.md + Locations.txt")
        self.chk_docs.setChecked(self.cfg_mgr.cfg.mover_generate_docs)
        ctrl.addWidget(self.chk_docs)
        self.chk_watch = QCheckBox("Watch clipboard (Windows)")
        self.chk_watch.setChecked(False)
        self.chk_watch.stateChanged.connect(self._toggle_watch)
        ctrl.addWidget(self.chk_watch)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        hk = QHBoxLayout()
        hk.addWidget(QLabel("Global hotkey:"))
        self.txt_hotkey = QLineEdit(self.cfg_mgr.cfg.mover_hotkey)
        hk.addWidget(self.txt_hotkey)
        btn_hotkey = QPushButton("Apply")
        btn_hotkey.clicked.connect(self._apply_hotkey)
        hk.addWidget(btn_hotkey)
        hk.addStretch()
        layout.addLayout(hk)

        actions = QHBoxLayout()
        btn_proc = QPushButton("Process Clipboard Now")
        btn_proc.clicked.connect(self._process_clipboard_now)
        actions.addWidget(btn_proc)
        actions.addStretch()
        layout.addLayout(actions)

        # Logs
        split = QSplitter(Qt.Orientation.Vertical)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.err = QPlainTextEdit()
        self.err.setReadOnly(True)
        split.addWidget(self.log)
        split.addWidget(self.err)
        split.setSizes([400, 200])
        layout.addWidget(split, 1)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Destination", self.txt_dest.text().strip() or str(Path.home()))
        if d:
            self.txt_dest.setText(d)

    def _toggle_watch(self):
        if self.chk_watch.isChecked():
            if not HAS_WIN_CLIP:
                QMessageBox.warning(self, "Unavailable", "win32clipboard not available on this system.")
                self.chk_watch.setChecked(False)
                return
            self._start_watcher()
        else:
            self._stop_watcher()

    def _start_watcher(self):
        self._stop_watcher()
        self.watcher = ClipboardWatcher(self._on_files_detected)
        self.watcher.start()
        self._log("🟢 Clipboard watcher started.")

    def _stop_watcher(self):
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
            self._log("🛑 Clipboard watcher stopped.")

    def _apply_hotkey(self):
        key = self.txt_hotkey.text().strip()
        self.cfg_mgr.cfg.mover_hotkey = key or "ctrl+shift+m"
        self.cfg_mgr.save()
        self._install_hotkey()
        self._log(f"Hotkey set to: {self.cfg_mgr.cfg.mover_hotkey}")

    def _install_hotkey(self):
        if not HAS_KEYBOARD:
            self._log("⚠️ 'keyboard' module not available; global hotkey disabled.")
            return
        # Clear existing
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        combo = self.cfg_mgr.cfg.mover_hotkey or "ctrl+shift+m"
        try:
            keyboard.add_hotkey(combo, self._process_clipboard_now)
            self._log(f"⌨️ Hotkey active: {combo}")
        except Exception as e:
            self._err(f"Hotkey failed: {e}")

    def _process_clipboard_now(self):
        if not HAS_WIN_CLIP:
            QMessageBox.warning(self, "Unavailable", "win32clipboard not available on this system.")
            return
        def read_files():
            pythoncom.CoInitialize()
            opened = False
            try:
                win32clipboard.OpenClipboard()
                opened = True
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                    flist = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                else:
                    flist = []
            finally:
                if opened:
                    win32clipboard.CloseClipboard()
            return [Path(f) for f in flist if Path(f).exists()]

        files = read_files()
        if not files:
            self._log("📋 Clipboard empty or no files.")
            return
        self._on_files_detected(files)

    def _on_files_detected(self, files: List[Path]):
        dest = Path(self.txt_dest.text().strip()).expanduser().resolve()
        gen_docs = self.chk_docs.isChecked()
        dest.mkdir(parents=True, exist_ok=True)
        self.cfg_mgr.cfg.mover_destination = str(dest)
        self.cfg_mgr.cfg.mover_generate_docs = bool(gen_docs)
        self.cfg_mgr.save()
        for item in files:
            try:
                if item.is_dir():
                    if not has_python_files(item):
                        self._log(f"🚫 No .py files in '{item}'. Skipping.")
                        continue
                    self._copy_folder(item, dest, gen_docs)
                elif item.suffix.lower() == ".py":
                    d = dest / item.stem
                    self._copy_script(item, d, item.name, gen_docs)
            except Exception:
                self._err(traceback.format_exc())

    def _variant_folder(self, base_dir: Path, folder_name: str) -> Path:
        variant_root = base_dir / folder_name / "Variants"
        variant_root.mkdir(parents=True, exist_ok=True)
        i = 2
        while True:
            variant_path = variant_root / f"{folder_name}_{i}"
            if not variant_path.exists():
                return variant_path
            i += 1

    def _folder_identical(self, src: Path, dest: Path) -> bool:
        src_files = sorted([p for p in src.rglob("*.py") if not excluded_dirpath(str(p.parent))])
        dest_files = sorted([p for p in dest.rglob("*.py") if not excluded_dirpath(str(p.parent))])
        if len(src_files) != len(dest_files):
            return False
        for s, d in zip(src_files, dest_files):
            if not d.exists() or sha256_file(s) != sha256_file(d):
                return False
        return True

    def _copy_folder(self, src_folder: Path, dest_root: Path, gen_docs: bool):
        folder_name = src_folder.name
        dest_folder = dest_root / folder_name
        if not dest_folder.exists():
            dest_folder.mkdir(parents=True)
        else:
            if self._folder_identical(src_folder, dest_folder):
                self._log(f"🟰 Identical folder skipped → {folder_name}")
                return
            dest_folder = self._variant_folder(dest_root, folder_name)

        for cur_root, dirs, files in os.walk(src_folder):
            if excluded_dirpath(cur_root):
                continue
            for f in files:
                if f.lower().endswith(".py"):
                    src = Path(cur_root) / f
                    rel = src.relative_to(src_folder)
                    target_dir = dest_folder / rel.parent
                    self._copy_script(src, target_dir, rel.name, gen_docs)

    def _copy_script(self, src: Path, dest_dir: Path, fname: str, gen_docs: bool):
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / fname
        base = dest.with_suffix('')
        ext = dest.suffix
        i = 2
        while dest.exists() and sha256_file(dest) != sha256_file(src):
            dest = base.with_name(f"{base.name}_{i}").with_suffix(ext)
            i += 1
        if dest.exists() and sha256_file(dest) == sha256_file(src):
            self._log(f"🟰 Identical pair → {dest}")
            return
        shutil.copy2(src, dest)
        self._log(f"✅ Copied → {dest}")
        if gen_docs:
            import datetime as dt
            (dest_dir / "Locations.txt").open("a", encoding="utf-8").write(
                f"{dt.datetime.now().isoformat(timespec='seconds')}: {src}\n"
            )
            (dest_dir / "README.md").write_text(generate_readme_for_script(src), encoding="utf-8")

    def _log(self, msg: str):
        from datetime import datetime as _dt
        self.log.appendPlainText(f"{_dt.now().strftime('%H:%M:%S')} • {msg}")
        self.log.moveCursor(QTextCursor.MoveOperation.End)

    def _err(self, tb: str):
        self.err.appendPlainText(tb)
        self.err.moveCursor(QTextCursor.MoveOperation.End)
        QMessageBox.critical(self, "Mover Error", tb)

# ───────────────────────────────────────────────────────────────────────────
#                               MAIN WINDOW
# ───────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyHeatMapper")
        self.resize(1500, 950)

        self.cfg_mgr = ConfigManager()
        self.dataset = self.cfg_mgr.cfg.current_dataset or DEFAULT_DATASET

        ds_slug = dataset_slug(self.dataset)
        mpath = DATASETS_DIR / f"metadata_{ds_slug}.json"
        scpath = DATASETS_DIR / f"scan_cache_{ds_slug}.json"
        for p in (mpath, scpath):
            if not p.exists():
                p.write_text("{}", encoding="utf-8")

        self.meta   = MetadataStore(path=mpath)
        self.scache = ScanCache(path=scpath)
        self.index  = IndexManager()

        self.pause_event = threading.Event()
        if self.cfg_mgr.cfg.cpu_guard and psutil:
            self.cpu_guard = CpuGuard(self.pause_event)
            self.cpu_guard.start()
        else:
            self.cpu_guard = None

        self.tabs      = QTabWidget()
        self.scan_tab  = ScanTab(self.cfg_mgr, self.meta)
        self.heat_tab  = HeatMapTab(self.meta)
        self.pipe_tab  = PipelineTab(self.meta)
        self.mover_tab = MoverTab(self.cfg_mgr)
        self.tabs.addTab(self.scan_tab, "Scan")
        self.tabs.addTab(self.heat_tab, "Heat Map")
        self.tabs.addTab(self.pipe_tab, "Pipeline")
        self.tabs.addTab(self.mover_tab, "Mover")
        self.setCentralWidget(self.tabs)

        self._create_menu()
        self._setup_dataset_toolbar()

        self.scan_tab.start_fast.connect(self._run_fast)
        self.scan_tab.deepen.connect(self._run_deepen)

        # Watcher for auto-deepen
        self._fast_watcher = QTimer(self)
        self._fast_watcher.setInterval(500)
        self._fast_watcher.timeout.connect(self._maybe_auto_deepen)
        self._fast_active = False

        QTimer.singleShot(250, self.heat_tab._refresh)

    def _create_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        exp_meta = QAction("Export Metadata…", self)
        exp_meta.triggered.connect(self._export_metadata)
        file_menu.addAction(exp_meta)

        build_readme = QAction("Build README…", self)
        build_readme.triggered.connect(self._build_readme_dialog)
        file_menu.addAction(build_readme)

        rebuild_idx = QAction("Rebuild Index", self)
        rebuild_idx.triggered.connect(self._rebuild_index)
        file_menu.addAction(rebuild_idx)

        prescan = QAction("Pre-Scan (.py counts)…", self)
        prescan.triggered.connect(self._menu_prescan)
        file_menu.addAction(prescan)

        quit_act = QAction("Quit", self)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        # Toolbar (quick dataset view)
        tb = QToolBar("Quick")
        self.addToolBar(tb)
        tb.setMovable(False)
        self.lbl_ds = QLabel("")
        tb.addWidget(self.lbl_ds)

    def _setup_dataset_toolbar(self):
        tb = self.addToolBar("Datasets")
        tb.setMovable(False)
        tb.addWidget(QLabel("Dataset:"))
        self.dataset_combo = QComboBox()
        self._load_dataset_list()
        self.dataset_combo.currentTextChanged.connect(self._switch_dataset)
        tb.addWidget(self.dataset_combo)
        new_act = QAction("New", self)
        new_act.triggered.connect(self._new_dataset)
        tb.addAction(new_act)
        del_act = QAction("Delete", self)
        del_act.triggered.connect(self._delete_dataset)
        tb.addAction(del_act)
        saveas_act = QAction("Save As", self)
        saveas_act.triggered.connect(self._save_as_dataset)
        tb.addAction(saveas_act)
        self._update_ds_label()

    def _update_ds_label(self):
        ds_slug = dataset_slug(self.dataset)
        self.lbl_ds.setText(f"Dataset: {self.dataset}  →  files: metadata_{ds_slug}.json / scan_cache_{ds_slug}.json")

    def _load_dataset_list(self):
        names = []
        for p in DATASETS_DIR.glob("metadata_*.json"):
            names.append(p.stem[len("metadata_"):])
        if DEFAULT_DATASET not in names:
            names.append(DEFAULT_DATASET)
        names = sorted(set(names))
        self.dataset_combo.blockSignals(True)
        self.dataset_combo.clear()
        self.dataset_combo.addItems(names)
        idx = names.index(self.dataset) if self.dataset in names else 0
        self.dataset_combo.setCurrentIndex(idx)
        self.dataset_combo.blockSignals(False)

    def _new_dataset(self):
        name, ok = QInputDialog.getText(self, "New Dataset", "Dataset name:")
        if not ok or not name.strip():
            return
        name = " ".join(name.strip().split())
        ds_slug = dataset_slug(name)
        mpath = DATASETS_DIR / f"metadata_{ds_slug}.json"
        scpath = DATASETS_DIR / f"scan_cache_{ds_slug}.json"
        if mpath.exists() or scpath.exists():
            QMessageBox.warning(self, "Error", f"Dataset '{name}' already exists.")
            return
        mpath.write_text("{}", encoding="utf-8")
        scpath.write_text("{}", encoding="utf-8")
        self.dataset = name
        self.cfg_mgr.cfg.current_dataset = name
        self.cfg_mgr.save()
        self._load_dataset_list()
        self.dataset_combo.setCurrentText(name)
        self._switch_dataset(name)

    def _delete_dataset(self):
        name = self.dataset
        if name == DEFAULT_DATASET:
            QMessageBox.warning(self, "Error", "Cannot delete default dataset.")
            return
        resp = QMessageBox.question(
            self, "Delete Dataset",
            f"Delete dataset '{name}' and its metadata? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        ds_slug = dataset_slug(name)
        mpath = DATASETS_DIR / f"metadata_{ds_slug}.json"
        scpath = DATASETS_DIR / f"scan_cache_{ds_slug}.json"
        try:
            if mpath.exists(): mpath.unlink()
            if scpath.exists(): scpath.unlink()
        except Exception as e:
            log.warning(f"Failed to delete dataset {name}: {e}")
        self.cfg_mgr.cfg.current_dataset = DEFAULT_DATASET
        self.cfg_mgr.save()
        self.dataset = DEFAULT_DATASET
        self._load_dataset_list()
        self.dataset_combo.setCurrentText(DEFAULT_DATASET)
        self._switch_dataset(DEFAULT_DATASET)

    def _save_as_dataset(self):
        old = self.dataset
        name, ok = QInputDialog.getText(self, "Save Dataset As", "New dataset name:")
        if not ok or not name.strip() or name == old:
            return
        name = " ".join(name.strip().split())
        ds_old = dataset_slug(old)
        ds_new = dataset_slug(name)
        m_old = DATASETS_DIR / f"metadata_{ds_old}.json"
        sc_old = DATASETS_DIR / f"scan_cache_{ds_old}.json"
        m_new = DATASETS_DIR / f"metadata_{ds_new}.json"
        sc_new = DATASETS_DIR / f"scan_cache_{ds_new}.json"
        if m_new.exists() or sc_new.exists():
            QMessageBox.warning(self, "Error", f"Dataset '{name}' already exists.")
            return
        shutil.copy2(str(m_old), str(m_new))
        shutil.copy2(str(sc_old), str(sc_new))
        self.dataset = name
        self.cfg_mgr.cfg.current_dataset = name
        self.cfg_mgr.save()
        self._load_dataset_list()
        self.dataset_combo.setCurrentText(name)
        self._switch_dataset(name)

    def _switch_dataset(self, name: str):
        old = self.dataset
        if name == old:
            return
        self.dataset = name
        self.cfg_mgr.cfg.current_dataset = name
        self.cfg_mgr.save()
        ds_slug = dataset_slug(name)
        mpath = DATASETS_DIR / f"metadata_{ds_slug}.json"
        scpath = DATASETS_DIR / f"scan_cache_{ds_slug}.json"
        if not mpath.exists(): mpath.write_text("{}", encoding="utf-8")
        if not scpath.exists(): scpath.write_text("{}", encoding="utf-8")
        self.meta   = MetadataStore(path=mpath)
        self.scache = ScanCache(path=scpath)
        self.scan_tab.meta = self.meta
        self.heat_tab.meta = self.meta
        self.pipe_tab.meta = self.meta
        self.scan_tab._refresh_table()
        self.heat_tab._refresh()
        self.pipe_tab._refresh_table()
        self._update_ds_label()

    def _export_metadata(self):
        ds_slug = dataset_slug(self.dataset)
        f, _ = QFileDialog.getSaveFileName(
            self, "Export Metadata",
            str(EXPORTS_DIR / f"metadata_{ds_slug}.json"),
            "JSON Files (*.json)"
        )
        if not f:
            return
        Path(f).write_text(json.dumps(self.meta.records, indent=2), encoding="utf-8")
        QMessageBox.information(self, "Exported", f"Metadata saved to: {f}")

    def _run_fast(self, roots: List[str], excludes: List[str]):
        self.scan_tab.progress.setValue(0)
        self.scan_tab._log("Starting FAST pass …")
        pause_evt = self.pause_event if self.cfg_mgr.cfg.cpu_guard and psutil else threading.Event()
        self.fast_pipeline = FastPipeline(
            roots, excludes, self.cfg_mgr.cfg, self.meta, self.scache,
            status_cb=self.scan_tab.set_status,
            log_cb=self.scan_tab._log,
            progress_cb=self.scan_tab.set_progress,
            counters_cb=self.scan_tab.set_counters,
            pause_event=pause_evt
        )
        self.fast_pipeline.start()
        self._fast_active = True
        self._fast_watcher.start()

    def _maybe_auto_deepen(self):
        if not self._fast_active:
            return
        if self.fast_pipeline.is_alive():
            return
        self._fast_active = False
        self._fast_watcher.stop()
        self.scan_tab._log("FAST finished.")
        self.scan_tab._refresh_table()
        self.heat_tab._refresh()
        self.pipe_tab._refresh_table()

        if self.scan_tab.chk_deepen.isChecked():
            selected = self.scan_tab.table.selectionModel().selectedRows()
            shas = [self.scan_tab.table.item(r.row(), 4).text() for r in selected]
            if shas:
                self.scan_tab._log(f"Auto-Deepening {len(shas)} selected scripts …")
                self._run_deepen(shas)
            else:
                self.scan_tab._log("Deepen Selected enabled, but no selection found. Skipping.")

    def _run_deepen(self, shas: List[str]):
        self.scan_tab._log(f"Deepening {len(shas)} files …")
        self.deep_worker = DeepenWorker(shas, self.cfg_mgr.cfg, self.meta)
        self.deep_worker.status.connect(self.scan_tab.set_status)
        self.deep_worker.progress.connect(self.scan_tab.set_progress)
        self.deep_worker.finished.connect(self._deep_finished)
        self.deep_worker.start()

    def _deep_finished(self):
        self.scan_tab._log("Deep pass finished.")
        self.scan_tab._refresh_table()
        self.heat_tab._refresh()
        self.pipe_tab._refresh_table()

    def _rebuild_index(self):
        vecs = []
        for rec in self.meta.records.values():
            vpath = rec.get("vector")
            if vpath and Path(vpath).exists():
                try:
                    vecs.append(np.load(vpath).astype("float32"))
                except Exception:
                    pass
        self.index.rebuild(vecs)
        self.index.save()
        QMessageBox.information(self, "Index Rebuilt", "Vector index has been rebuilt successfully.")

    def _build_readme_dialog(self):
        options = ["From Favorites (dataset-wide)", "From Folder (choose a root path)"]
        choice, ok = QInputDialog.getItem(self, "Build README", "Source:", options, 0, False)
        if not ok:
            return
        if choice == options[0]:
            recs = [r for r in self.meta.records.values() if r.get("favorite")]
            if not recs:
                QMessageBox.warning(self, "No Favorites", "No favorites found in this dataset.")
                return
            md = ReadmeBuilder.build_from_records(recs, title="Project README (Favorites)")
            f, _ = QFileDialog.getSaveFileName(self, "Save README", str(README_DIR / "README_favorites.md"), "Markdown (*.md)")
            if not f:
                return
            Path(f).write_text(md, encoding="utf-8")
            QMessageBox.information(self, "README Built", f"Saved to: {f}")
        else:
            folder = QFileDialog.getExistingDirectory(self, "Choose folder to summarize")
            if not folder:
                return
            root = Path(folder)
            recs = []
            for r in self.meta.records.values():
                if any(root in Path(p).parents or Path(p) == root for p in r.get("paths", [])):
                    recs.append(r)
            if not recs:
                QMessageBox.warning(self, "No Files", "No indexed Python files under that folder.")
                return
            md = ReadmeBuilder.build_from_records(recs, title=f"Project README — {root.name}")
            out_path = Path(folder) / "Readme.md"
            out_path.write_text(md, encoding='utf-8')
            QMessageBox.information(self, "README Built", f"Saved to: {out_path}")

    def _menu_prescan(self):
        roots = self.cfg_mgr.cfg.selected_roots or []
        if not roots:
            QMessageBox.warning(self, "Roots Required", "Add at least one root directory on the Scan tab.")
            return
        dlg = PreScanDialog(self, roots, self.cfg_mgr.cfg.user_excludes or [])
        dlg.exec()

    # Graceful shutdown: stop background timer / threads
    def closeEvent(self, event):
        try:
            if self._fast_watcher.isActive():
                self._fast_watcher.stop()
        except Exception:
            pass
        try:
            if getattr(self, "cpu_guard", None) is not None:
                self.cpu_guard.stop()
        except Exception:
            pass
        super().closeEvent(event)

# ───────────────────────────────────────────────────────────────────────────
#                                   README BUILDER
# ───────────────────────────────────────────────────────────────────────────
class ReadmeBuilder:
    @staticmethod
    def build_from_records(recs: List[dict], title: str = "Project Documentation") -> str:
        ordered = sorted(recs, key=lambda r: (r.get("semantic_score",0.0), r.get("complexity",0.0)), reverse=True)
        lines = []
        lines.append(f"# {title}")
        lines.append("")
        lines.append("This README was assembled from per-file PDDs generated by PyHeatMapper.")
        lines.append("")
        lines.append("## Summary Table (Top Scripts)")
        lines.append("| Name | SemScore | Complexity | Classes | Functions | Paths |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for r in ordered[:100]:
            name = Path(r["paths"][0]).name if r.get("paths") else "?"
            stats = r.get("stats", {})
            lines.append(f"| `{name}` | {r.get('semantic_score',0.0):.1f} | {r.get('complexity',0.0):.2f} | "
                         f"{stats.get('Classes',0)} | {stats.get('Functions',0)} | {len(r.get('paths',[]))} |")
        lines.append("")
        lines.append("## File Details")
        for r in ordered:
            name = Path(r["paths"][0]).name if r.get("paths") else "?"
            lines.append(f"### {name}")
            try:
                pdd_text = Path(r["pdd"]).read_text(encoding="utf-8")
            except Exception:
                pdd_text = "(PDD not available)"
            if len(pdd_text) > 120_000:
                pdd_text = pdd_text[:120_000] + "\n\n> [Truncated in README for size]\n"
            lines.append(pdd_text)
            lines.append("")
        return "\n".join(lines)

# ───────────────────────────────────────────────────────────────────────────
#                                   MAIN
# ───────────────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)

    def handle_exception(exc_type, exc_value, exc_tb):
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        dlg = QMessageBox()
        dlg.setWindowTitle("Unexpected Error")
        dlg.setIcon(QMessageBox.Icon.Critical)
        dlg.setText("An unexpected error occurred:")
        dlg.setDetailedText(tb_str)
        dlg.exec()
        sys.exit(1)

    sys.excepthook = handle_exception

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

PyHeatMapper — Advanced Scan, Pre-Scan Counts, Content-Hash Dedup, Semantic Weighting, PDDs, Favorites,
README Builder, and Integrated ScriptMover (clipboard + hotkey)

What this build adds (highlights):
- NEW: Pre-Scan (.py counts) dialog (WinDirStat-style) showing, per top-level folder under each selected root,
  the recursive count of Python files (respecting exclusions). Sortable table + bar chart + CSV export.
- Content-hash (SHA-1) dedup: a "script" is defined by its exact bytes, not its path.
  • meta.records are keyed by sha and store: {'paths': [...]} of all locations.
  • Duplicates don't inflate unique counts or re-embed vectors unnecessarily.
- Robust Windows-safe dataset file naming and atomic writes for metadata/scan-cache.
- Strong default excludes (venv, __pycache__, AppData, Temp, Windows, Program Files, etc.)
  + user regex excludes remain available. Only *.py files are considered.
- Deepen Selected checkbox, Favorites (★), PDD previews in all relevant tabs,
  README Builder (from Favorites or a folder subset), Radar + Heat Grid.
- "Mover" tab: PyQt clone of ScriptMover workflow (destination chooser, clipboard watcher, hotkey, README/Locations docs).

Run:
    pip install PyQt6 faiss-cpu matplotlib requests numpy psutil keyboard pywin32
    python PyHeatMapper.py
**Classes:** Config, ConfigManager, MetadataStore, ScanCache, CpuGuard, IndexManager, FastPipeline, DeepenWorker, RadarCanvas, HeatGridCanvas, PreScanWorker, PreScanDialog, ScanTab, HeatMapTab, PipelineTab, ClipboardWatcher, MoverTab, MainWindow, ReadmeBuilder
**Functions:** is_windows(), list_windows_drives(), sha1_file(path), sha256_file(path), safe_read(path), slugify(name), ensure_model(name, fallback), clamp01(x), pct(x), sanitize_windows_filename(name), dataset_slug(name), _atomic_write(path, text), excluded_dirpath(dirpath), ollama_generate(model, prompt, timeout), ollama_embed(model, text, timeout), dummy_embed(text, dim), ast_info(source), measure_complexity(source, info), category_weights(source), doc_quality(source, info), readme_template_readiness(source), fundamental_depth(info), complexity_norm(x), category_avg(cats), semantic_score(comp, cats, dq, rtr, fdepth), pdd_skeleton(path, source, info, comp, cats, dq, rtr, fdepth, sem_score, stats), deepen_chunks_prompt(), chunk_text(s, n), star_for(rec), analyze_script_for_readme(path), generate_readme_for_script(path), has_python_files(path), main()



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