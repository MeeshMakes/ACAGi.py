# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `Analyze_folders.py`

**Functions:** analyze_folders(start_path)
### `Error_Watcher.py`

**Functions:** monitor_my_everything()
### `My_Everything.py`

My_Everything.py

A unified AI tool for managing, auditing, and recalling files/projects:
  - Drag & drop or URL ingestion of ZIPs/folders
  - Auto-extract, recursive summarize, categorize, and preview
  - Embed (vectorize), Discard, Move, Backup, Archive, or Delete
  - Global RAG-backed recall via FAISS & Ollama/OpenAI
  - Auditor view with duplicate detection and actions
  - Chat interface with history for querying archive
  - Project mirror view for folder structure
  - Settings for embedding/summarization providers/models

**Classes:** ConfigManager, ProjectManager, RAGEngine, IngestorTab, AuditorTab, ProjectsTab, ProjectWindow, ChatTab, SettingsTab, MainWindow

**Functions:** compute_hash(text), dummy_embed(text, dim), embed_via_ollama(text, dim), get_embedding(text, dim), summarize_text(text), recursive_summarize(text, max_len), extract_text_from_file(path), download_and_extract_zip(url, extract_to), backup_file(path), archive_file(path, project_name), main()

## Other Files

The following files are present in the project but were not analysed in detail:

- `analyze.txt`
- `api\api_key.txt`
- `api\other\api_key.txt`
- `error_watcher.log`
- `rag_settings.json`


## Detailed Module Analyses


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


## Module `Error_Watcher.py`

```python
import subprocess
import time
import os

# Define paths
BASE_DIR = r"D:\AI\My Everything AI"
TARGET_SCRIPT = os.path.join(BASE_DIR, 'My_Everything.py')
LOG_FILE = os.path.join(BASE_DIR, 'error_watcher.log')

def monitor_my_everything():
    # Overwrite the log file each time it starts
    with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
        log_file.write(f"ErrorWatcher started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Monitoring: {TARGET_SCRIPT}\n")

    try:
        with subprocess.Popen(
            ['python', TARGET_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        ) as process:

            with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
                while True:
                    error_line = process.stderr.readline()

                    if error_line:
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        log_msg = f"[{timestamp}] ERROR: {error_line.strip()}\n"
                        print(log_msg)
                        log_file.write(log_msg)
                        log_file.flush()

                    if process.poll() is not None:
                        break

    except Exception as e:
        with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"[{timestamp}] Exception occurred: {str(e)}\n")

if __name__ == "__main__":
    print("ErrorWatcher: Launching and monitoring My_Everything.py...")
    monitor_my_everything()
    print("ErrorWatcher: My_Everything.py has stopped.")
```

**Functions:** monitor_my_everything()


## Module `My_Everything.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My_Everything.py

A unified AI tool for managing, auditing, and recalling files/projects:
  - Drag & drop or URL ingestion of ZIPs/folders
  - Auto-extract, recursive summarize, categorize, and preview
  - Embed (vectorize), Discard, Move, Backup, Archive, or Delete
  - Global RAG-backed recall via FAISS & Ollama/OpenAI
  - Auditor view with duplicate detection and actions
  - Chat interface with history for querying archive
  - Project mirror view for folder structure
  - Settings for embedding/summarization providers/models
"""

import os
import sys
import io
import zipfile
import uuid
import hashlib
import datetime
import json
import shutil
import logging
import requests
import numpy as np
import faiss
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

import openai
from fpdf import FPDF
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QInputDialog, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QComboBox,
    QProgressBar, QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "rag_settings.json")
DB_DIR = os.path.join(BASE_DIR, "database")
INDEX_PATH = os.path.join(DB_DIR, "vector_store.index")
META_PATH = os.path.join(DB_DIR, "vector_store.meta.json")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archives")
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
SUMMARIES_DIR = os.path.join(BASE_DIR, "summaries")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
CHAT_HISTORY_DIR = os.path.join(BASE_DIR, "chat_history")
ARCHIVE_MANIFEST = os.path.join(ARCHIVE_DIR, "archive_manifest.json")

for d in [
    DB_DIR, BACKUP_DIR, ARCHIVE_DIR,
    PROJECTS_DIR, SUMMARIES_DIR,
    EXPORTS_DIR, CHAT_HISTORY_DIR
]:
    os.makedirs(d, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

DEFAULT_CONFIG = {
    "text_embedding_provider": "Ollama",
    "text_embedding_model":    "mxbai-embed-large:latest",
    "summary_provider":        "OpenAI",
    "summary_model":           "gpt-4o-mini",
    "chunk_size":              2000
}

class ConfigManager:
    def __init__(self, path=CONFIG_PATH):
        self.path = path
        self.config = DEFAULT_CONFIG.copy()
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except:
                logging.warning("Failed to load config, using defaults")
        self.save()

    def get(self, key):
        return self.config.get(key, DEFAULT_CONFIG[key])

    def set(self, key, value):
        self.config[key] = value

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

CONFIG = ConfigManager()

# -----------------------------------------------------------------------------
# PROJECT MANAGEMENT
# -----------------------------------------------------------------------------
class ProjectManager:
    def __init__(self, projects_dir=PROJECTS_DIR):
        self.projects_dir = projects_dir
        self.categories = defaultdict(list)

    def create_project(self, name):
        proj_dir = os.path.join(self.projects_dir, name)
        for sub in ("texts", "summaries", "vectors", "meta"):
            os.makedirs(os.path.join(proj_dir, sub), exist_ok=True)
        return proj_dir

    def suggest_category(self, summary):
        keywords = {
            "art": ["art", "design", "sketch", "painting", "graphic"],
            "code": ["python", "java", "script", "program", "coding"],
            "game": ["game", "unity", "unreal", "level", "asset"],
            "misc": []
        }
        summary_lower = summary.lower()
        for cat, kws in keywords.items():
            if any(kw in summary_lower for kw in kws):
                return cat
        return "misc"

    def add_to_project(self, file_path, text, summary, vector, metadata):
        proj_name = os.path.basename(os.path.dirname(file_path)) or "Default"
        proj_dir = self.create_project(proj_name)
        h = compute_hash(text)
        cat = self.suggest_category(summary)
        self.categories[cat].append(file_path)

        # Save text, summary, vector, meta
        with open(os.path.join(proj_dir, "texts", f"{h}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        with open(os.path.join(proj_dir, "summaries", f"{h}.json"), "w", encoding="utf-8") as f:
            json.dump({"summary": summary}, f)
        np.save(os.path.join(proj_dir, "vectors", f"{h}.npy"), vector)
        with open(os.path.join(proj_dir, "meta", f"{h}.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f)
        return proj_name, cat

# -----------------------------------------------------------------------------
# RAG ENGINE
# -----------------------------------------------------------------------------
def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

def dummy_embed(text: str, dim: int = 768):
    vec = np.zeros(dim, dtype="float32")
    for i, c in enumerate(text):
        vec[i % dim] += ord(c)
    norm = np.linalg.norm(vec)
    return (vec / norm) if norm > 0 else vec

def embed_via_ollama(text: str, dim: int = 768):
    model = CONFIG.get("text_embedding_model")
    try:
        resp = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=10
        )
        data = resp.json()
        vec = np.array(data.get("embedding", []), dtype="float32")
        if vec.shape[0] == dim:
            return vec
    except Exception as e:
        logging.warning(f"Ollama embed failed: {e}")
    return None

def get_embedding(text: str, dim: int = 768):
    if CONFIG.get("text_embedding_provider") == "Ollama":
        vec = embed_via_ollama(text, dim)
        if vec is not None:
            return vec
    return dummy_embed(text, dim)

class RAGEngine:
    def __init__(self, dim=768, index_path=INDEX_PATH, meta_path=META_PATH):
        self.dim         = dim
        self.index_path  = index_path
        self.meta_path   = meta_path
        self.index       = faiss.IndexFlatL2(dim)
        self.metadata    = []
        self.project_mgr = ProjectManager()

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = []

    def add_document(self, text, filename, source_path="", summary=""):
        vec = get_embedding(text, self.dim)
        self.index.add(np.expand_dims(vec, axis=0))
        h = compute_hash(text)
        uid = str(uuid.uuid4())
        entry = {
            "uid": uid,
            "filename": filename,
            "hash": h,
            "timestamp": datetime.datetime.now().isoformat(),
            "source_path": source_path,
            "summary": summary,
            "category": self.project_mgr.suggest_category(summary)
        }
        self.metadata.append(entry)

        # save raw text
        texts_dir = os.path.join(os.path.dirname(self.meta_path), "texts")
        os.makedirs(texts_dir, exist_ok=True)
        with open(os.path.join(texts_dir, f"{h}.txt"), "w", encoding="utf-8") as f:
            f.write(text)

        # project integration
        self.project_mgr.add_to_project(source_path or filename, text, summary, vec, entry)

        self.save()
        return entry

    def query(self, qtext, k=5):
        qvec = get_embedding(qtext, self.dim)
        D, I   = self.index.search(np.expand_dims(qvec, axis=0), k)
        return [self.metadata[i] for i in I[0] if i < len(self.metadata)]

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

    def delete_by_hash(self, h):
        md = next((m for m in self.metadata if m["hash"] == h), None)
        if md and os.path.exists(md["source_path"]):
            reply = QMessageBox.question(
                None,
                "Backup Original?",
                f"Original file {md['source_path']} exists. Backup before deleting?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                backup_file(md["source_path"])

        self.metadata = [m for m in self.metadata if m["hash"] != h]
        texts_dir = os.path.join(os.path.dirname(self.meta_path), "texts")
        tfile     = os.path.join(texts_dir, f"{h}.txt")
        if os.path.exists(tfile):
            os.remove(tfile)
        self.save()

# -----------------------------------------------------------------------------
# SUMMARIZATION
# -----------------------------------------------------------------------------
def summarize_text(text: str) -> str:
    provider = CONFIG.get("summary_provider")
    model    = CONFIG.get("summary_model")
    if provider == "OpenAI":
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        try:
            res = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Summarize the following text concisely:"},
                    {"role": "user",   "content": text}
                ],
                max_tokens=300
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logging.warning(f"OpenAI summarize failed: {e}")
            return ""
    else:
        payload = {"model": model, "prompt": f"Summarize concisely:\n\n{text}"}
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json=payload, timeout=20
            )
            return resp.json().get("response", "").strip()
        except Exception as e:
            logging.warning(f"Ollama summarize failed: {e}")
            return ""

def recursive_summarize(text, max_len=2000):
    h          = compute_hash(text)
    cache_path = os.path.join(SUMMARIES_DIR, f"{h}.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)["summary"]

    if len(text) <= max_len:
        summary = summarize_text(text)
    else:
        chunks    = [text[i:i + max_len] for i in range(0, len(text), max_len)]
        with ThreadPoolExecutor() as executor:
            summaries = list(executor.map(summarize_text, chunks))
        combined  = " ".join(summaries)
        summary   = recursive_summarize(combined, max_len)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary}, f)
    return summary

# -----------------------------------------------------------------------------
# FILE UTILITIES
# -----------------------------------------------------------------------------
TEXT_EXTS  = {".txt", ".md", ".json", ".py", ".csv", ".log"}
MEDIA_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp4", ".mov", ".avi", ".mkv"}

def extract_text_from_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXTS:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except:
            return ""
    if ext in MEDIA_EXTS:
        return f"[Media file: {os.path.basename(path)}]"
    return ""

def download_and_extract_zip(url, extract_to):
    os.makedirs(extract_to, exist_ok=True)
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(extract_to)
    return extract_to

def backup_file(path):
    ts   = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"{ts}_{os.path.basename(path)}.zip")
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(path, arcname=os.path.basename(path))
    return dest

def archive_file(path, project_name="Default"):
    ts   = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    dest = os.path.join(ARCHIVE_DIR, f"{project_name}_{ts}.zip")
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(path, arcname=os.path.basename(path))
    manifest = {
        "file": os.path.basename(path),
        "project": project_name,
        "timestamp": ts,
        "archive_path": dest
    }
    data = []
    if os.path.exists(ARCHIVE_MANIFEST):
        with open(ARCHIVE_MANIFEST, "r", encoding="utf-8") as f:
            data = json.load(f)
    data.append(manifest)
    with open(ARCHIVE_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return dest

# -----------------------------------------------------------------------------
# GUI: INGESTOR TAB
# -----------------------------------------------------------------------------
class IngestorTab(QWidget):
    def __init__(self, rag: RAGEngine):
        super().__init__()
        self.rag = rag
        self.pending = []
        self.summaries = {}
        self.exported = set()
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search files...")
        self.search_bar.textChanged.connect(self.filter_items)
        toolbar.addWidget(self.search_bar)

        self.search_content = QCheckBox("Search in content")
        self.search_content.stateChanged.connect(self.filter_items)
        toolbar.addWidget(self.search_content)

        self.select_all = QCheckBox("Select All")
        self.select_all.stateChanged.connect(self.toggle_select_all)
        toolbar.addWidget(self.select_all)

        self.sort_asc = QCheckBox("Sort Ascending")
        self.sort_asc.stateChanged.connect(self.filter_items)
        toolbar.addWidget(self.sort_asc)

        self.archive_mode = QCheckBox("Archive Mode")
        toolbar.addWidget(self.archive_mode)

        self.compile_context = QCheckBox("Compile Context")
        self.compile_context.stateChanged.connect(self.show_summary)
        toolbar.addWidget(self.compile_context)

        layout.addLayout(toolbar)

        # Input Buttons
        btns = QHBoxLayout()
        self.btn_add_folder = QPushButton("Add Folder")
        self.btn_add_folder.clicked.connect(self.add_folder)
        btns.addWidget(self.btn_add_folder)

        self.btn_add_zip = QPushButton("Add ZIP")
        self.btn_add_zip.clicked.connect(self.add_zip)
        btns.addWidget(self.btn_add_zip)

        self.btn_add_url = QPushButton("Add URL → ZIP")
        self.btn_add_url.clicked.connect(self.add_url)
        btns.addWidget(self.btn_add_url)

        layout.addLayout(btns)

        # File Tree & Summary
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File", "Summary", "Category"])
        self.tree.itemSelectionChanged.connect(self.show_summary)
        layout.addWidget(self.tree, stretch=3)

        self.summary_view = QPlainTextEdit()
        self.summary_view.setReadOnly(True)
        layout.addWidget(self.summary_view, stretch=2)

        # Action Buttons
        actions = QHBoxLayout()
        self.btn_embed = QPushButton("Embed Selected")
        self.btn_embed.clicked.connect(self.embed_selected)
        actions.addWidget(self.btn_embed)

        self.btn_discard = QPushButton("Discard Selected")
        self.btn_discard.clicked.connect(self.discard_selected)
        actions.addWidget(self.btn_discard)

        self.btn_move = QPushButton("Move Selected")
        self.btn_move.clicked.connect(self.move_selected)
        actions.addWidget(self.btn_move)

        self.btn_backup = QPushButton("Backup Selected")
        self.btn_backup.clicked.connect(self.backup_selected)
        actions.addWidget(self.btn_backup)
        layout.addLayout(actions)

        # Progress & Status
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.status = QLabel("Idle")
        layout.addWidget(self.status)

        # Export Options
        export = QHBoxLayout()
        self.name_export = QLineEdit()
        self.name_export.setPlaceholderText("Export base name")
        export.addWidget(self.name_export)

        self.pdf_chk = QCheckBox("PDF")
        export.addWidget(self.pdf_chk)
        self.json_chk = QCheckBox("JSON")
        export.addWidget(self.json_chk)
        self.txt_chk = QCheckBox("TXT")
        export.addWidget(self.txt_chk)
        self.py_chk = QCheckBox("PY")
        export.addWidget(self.py_chk)

        self.btn_export = QPushButton("Export Summary")
        self.btn_export.clicked.connect(self.export_summary)
        export.addWidget(self.btn_export)

        self.btn_continue = QPushButton("Continue Exports")
        self.btn_continue.clicked.connect(self.continue_exports)
        export.addWidget(self.btn_continue)
        layout.addLayout(export)

    def filter_items(self):
        q = self.search_bar.text().lower()
        in_content = self.search_content.isChecked()
        asc = self.sort_asc.isChecked()
        results = []
        for path, summary in self.summaries.items():
            if in_content:
                if q in summary.lower():
                    results.append((path, summary))
            else:
                if q in path.lower():
                    results.append((path, summary))
        results.sort(key=lambda x: x[0], reverse=not asc)
        self.tree.clear()
        for path, summary in results:
            cat = self.rag.project_mgr.suggest_category(summary)
            item = QTreeWidgetItem([path, summary.replace("\n", " ")[:80] + "...", cat])
            self.tree.addTopLevelItem(item)

    def toggle_select_all(self):
        if self.select_all.isChecked():
            self.tree.selectAll()
        else:
            self.tree.clearSelection()

    def show_summary(self):
        if self.compile_context.isChecked():
            txt = ""
            for it in self.tree.selectedItems():
                p = it.text(0)
                txt += f"{os.path.basename(p)}:\n{self.summaries.get(p, '')}\n\n"
            self.summary_view.setPlainText(txt)
        else:
            sel = self.tree.selectedItems()
            if sel:
                p = sel[0].text(0)
                self.summary_view.setPlainText(self.summaries.get(p, ""))

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.process_folder(folder)

    def add_zip(self):
        zf, _ = QFileDialog.getOpenFileName(self, "Select ZIP File", filter="ZIP files (*.zip)")
        if zf:
            tmp = os.path.join(BASE_DIR, "temp_ingest")
            shutil.rmtree(tmp, ignore_errors=True)
            zipfile.ZipFile(zf).extractall(tmp)
            self.process_folder(tmp)

    def add_url(self):
        url, ok = QInputDialog.getText(self, "Enter ZIP URL", "URL:")
        if ok and url:
            tmp = os.path.join(BASE_DIR, "temp_ingest")
            shutil.rmtree(tmp, ignore_errors=True)
            download_and_extract_zip(url, tmp)
            self.process_folder(tmp)

    def process_folder(self, folder):
        self.pending.clear()
        self.summaries.clear()
        self.tree.clear()
        self.progress.setValue(0)
        self.status.setText("Scanning folder...")

        for root, _, files in os.walk(folder):
            for f in files:
                self.pending.append(os.path.join(root, f))

        total = len(self.pending)
        self.progress.setMaximum(total)

        def worker(idx, path):
            txt = extract_text_from_file(path)
            summary = recursive_summarize(txt)
            self.summaries[path] = summary
            cat = self.rag.project_mgr.suggest_category(summary)
            item = QTreeWidgetItem([path, summary.replace("\n", " ")[:80] + "...", cat])
            self.tree.addTopLevelItem(item)
            self.progress.setValue(idx + 1)
            self.status.setText(f"Summarized {idx + 1}/{total}")
            QApplication.processEvents()

        with ThreadPoolExecutor() as ex:
            for idx, path in enumerate(self.pending):
                ex.submit(worker, idx, path)

        self.status.setText("Done summarizing.")

    def embed_selected(self):
        for item in self.tree.selectedItems():
            path = item.text(0)
            text = extract_text_from_file(path)
            summary = self.summaries.get(path, "")
            entry = self.rag.add_document(text, os.path.basename(path), path, summary)
            logging.info(f"Embedded: {entry}")
            if self.archive_mode.isChecked():
                archive_file(path, os.path.basename(os.path.dirname(path)))
                os.remove(path)
        self.rag.save()
        QMessageBox.information(self, "Embed", "Selected files embedded.")

    def discard_selected(self):
        for item in self.tree.selectedItems():
            path = item.text(0)
            if self.archive_mode.isChecked():
                archive_file(path, os.path.basename(os.path.dirname(path)))
                os.remove(path)
            if path in self.pending:
                self.pending.remove(path)
            idx = self.tree.indexOfTopLevelItem(item)
            self.tree.takeTopLevelItem(idx)

    def move_selected(self):
        dest = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not dest:
            return
        for item in self.tree.selectedItems():
            src = item.text(0)
            try:
                shutil.move(src, dest)
                item.setText(0, os.path.join(dest, os.path.basename(src)))
            except Exception as e:
                logging.error(f"Move failed: {e}")

    def backup_selected(self):
        for item in self.tree.selectedItems():
            path = item.text(0)
            bk = backup_file(path)
            logging.info(f"Backed up {path} → {bk}")
        QMessageBox.information(self, "Backup", "Selected files backed up.")

    def export_summary(self):
        sel = self.tree.selectedItems()
        if not sel:
            QMessageBox.warning(self, "Export", "No files selected.")
            return
        base = self.name_export.text().strip() or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = EXPORTS_DIR
        os.makedirs(out_dir, exist_ok=True)
        data = {item.text(0): self.summaries.get(item.text(0), "") for item in sel}

        if self.json_chk.isChecked():
            with open(os.path.join(out_dir, f"{base}.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        if self.txt_chk.isChecked():
            with open(os.path.join(out_dir, f"{base}.txt"), "w", encoding="utf-8") as f:
                for p, s in data.items():
                    f.write(f"{p}:\n{s}\n\n")
        if self.py_chk.isChecked():
            with open(os.path.join(out_dir, f"{base}.py"), "w", encoding="utf-8") as f:
                for p, s in data.items():
                    f.write(f"# {p}\n\"\"\"\n{s}\n\"\"\"\n\n")
        if self.pdf_chk.isChecked():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for p, s in data.items():
                pdf.multi_cell(0, 10, f"{p}:\n{s}\n\n")
            pdf.output(os.path.join(out_dir, f"{base}.pdf"))
        self.exported.update(data.keys())
        QMessageBox.information(self, "Export", "Summaries exported.")

    def continue_exports(self):
        remaining = [p for p in self.pending if p not in self.exported]
        self.tree.clear()
        for p in remaining:
            cat = self.rag.project_mgr.suggest_category(self.summaries.get(p, ""))
            item = QTreeWidgetItem([p, self.summaries.get(p, "")[:80] + "...", cat])
            self.tree.addTopLevelItem(item)
        QMessageBox.information(self, "Continue Exports", "Showing remaining files.")

# -----------------------------------------------------------------------------
# GUI: AUDITOR TAB
# -----------------------------------------------------------------------------
class AuditorTab(QWidget):
    def __init__(self, rag: RAGEngine):
        super().__init__()
        self.rag = rag
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search metadata...")
        self.search_bar.textChanged.connect(self.filter_items)
        toolbar.addWidget(self.search_bar)

        self.search_content = QCheckBox("Search in content")
        self.search_content.stateChanged.connect(self.filter_items)
        toolbar.addWidget(self.search_content)

        self.select_all = QCheckBox("Select All")
        self.select_all.stateChanged.connect(self.toggle_select_all)
        toolbar.addWidget(self.select_all)

        self.sort_asc = QCheckBox("Sort Ascending")
        self.sort_asc.stateChanged.connect(self.refresh_list)
        toolbar.addWidget(self.sort_asc)

        layout.addLayout(toolbar)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Filename", "Hash", "Time", "Category"])
        self.tree.itemSelectionChanged.connect(self.show_entry)
        layout.addWidget(self.tree, stretch=3)

        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        layout.addWidget(self.detail, stretch=2)

        actions = QHBoxLayout()
        self.btn_rerun = QPushButton("Re-Embed Selected")
        self.btn_rerun.clicked.connect(self.rerun_selected)
        actions.addWidget(self.btn_rerun)

        self.btn_move = QPushButton("Move File")
        self.btn_move.clicked.connect(self.move_selected)
        actions.addWidget(self.btn_move)

        self.btn_backup = QPushButton("Backup File")
        self.btn_backup.clicked.connect(self.backup_selected)
        actions.addWidget(self.btn_backup)

        self.btn_delete = QPushButton("Delete Entry")
        self.btn_delete.clicked.connect(self.delete_selected)
        actions.addWidget(self.btn_delete)

        layout.addLayout(actions)
        self.refresh_list()

    def refresh_list(self):
        self.tree.clear()
        entries = list(self.rag.metadata)
        entries.sort(key=lambda m: m["filename"] if self.sort_asc.isChecked() else m["timestamp"],
                     reverse=not self.sort_asc.isChecked())
        for m in entries:
            self.tree.addTopLevelItem(QTreeWidgetItem([
                m["filename"], m["hash"], m["timestamp"], m["category"]
            ]))

    def filter_items(self):
        q = self.search_bar.text().lower()
        in_content = self.search_content.isChecked()
        self.tree.clear()
        for m in self.rag.metadata:
            match = q in m["filename"].lower() or q in m["category"].lower()
            if in_content:
                try:
                    txt = open(
                        os.path.join(os.path.dirname(self.rag.meta_path), "texts", f"{m['hash']}.txt"),
                        "r", encoding="utf-8"
                    ).read().lower()
                    match = match or (q in txt)
                except:
                    pass
            if match:
                self.tree.addTopLevelItem(QTreeWidgetItem([
                    m["filename"], m["hash"], m["timestamp"], m["category"]
                ]))

    def toggle_select_all(self):
        if self.select_all.isChecked():
            self.tree.selectAll()
        else:
            self.tree.clearSelection()

    def show_entry(self):
        sel = self.tree.selectedItems()
        if not sel:
            return
        h = sel[0].text(1)
        try:
            with open(os.path.join(os.path.dirname(self.rag.meta_path), "texts", f"{h}.txt"),
                      "r", encoding="utf-8") as f:
                self.detail.setPlainText(f.read())
        except:
            self.detail.setPlainText("Error loading content.")

    def rerun_selected(self):
        for item in self.tree.selectedItems():
            h = item.text(1)
            path = os.path.join(os.path.dirname(self.rag.meta_path), "texts", f"{h}.txt")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                # remove old
                self.rag.delete_by_hash(h)
                # re-add
                self.rag.add_document(
                    text,
                    item.text(0),
                    "",
                    next(m["summary"] for m in self.rag.metadata if m["hash"] == h)
                )
            except Exception as e:
                logging.error(f"Re-embed failed: {e}")
        self.rag.save()
        self.refresh_list()
        QMessageBox.information(self, "Re-Embed", "Selected entries re-embedded.")

    def move_selected(self):
        dest = QFileDialog.getExistingDirectory(self, "Destination")
        if not dest:
            return
        for item in self.tree.selectedItems():
            fname = item.text(0)
            md = next((m for m in self.rag.metadata if m["filename"] == fname and m["hash"] == item.text(1)), None)
            if md and os.path.exists(md["source_path"]):
                try:
                    shutil.move(md["source_path"], dest)
                    md["source_path"] = os.path.join(dest, fname)
                except Exception as e:
                    logging.error(f"Move failed: {e}")
        self.rag.save()
        self.refresh_list()

    def backup_selected(self):
        for item in self.tree.selectedItems():
            h = item.text(1)
            path = os.path.join(os.path.dirname(self.rag.meta_path), "texts", f"{h}.txt")
            backup_file(path)
        QMessageBox.information(self, "Backup", "Selected entries backed up.")

    def delete_selected(self):
        for item in self.tree.selectedItems():
            h = item.text(1)
            self.rag.delete_by_hash(h)
        self.rag.save()
        self.refresh_list()
        QMessageBox.information(self, "Delete", "Selected entries deleted.")

# -----------------------------------------------------------------------------
# GUI: PROJECTS TAB
# -----------------------------------------------------------------------------
class ProjectsTab(QWidget):
    def __init__(self, rag: RAGEngine):
        super().__init__()
        self.rag = rag
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search projects...")
        self.search_bar.textChanged.connect(self.refresh_tree)
        toolbar.addWidget(self.search_bar)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh_tree)
        toolbar.addWidget(self.btn_refresh)

        layout.addLayout(toolbar)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Project/Folder/File", "Summary", "Category"])
        self.tree.itemDoubleClicked.connect(self.open_project_window)
        layout.addWidget(self.tree, stretch=4)
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.clear()
        q = self.search_bar.text().lower()
        projects = defaultdict(list)
        for m in self.rag.metadata:
            proj_name = os.path.basename(os.path.dirname(m["source_path"])) or "Default"
            if q and q not in proj_name.lower() and q not in m["filename"].lower():
                continue
            projects[proj_name].append(m)
        for proj, items in projects.items():
            proj_item = QTreeWidgetItem([proj, "", "Project"])
            self.tree.addTopLevelItem(proj_item)
            for m in items:
                summary = m.get("summary", "")[:80] + "..."
                self.tree.addChild(proj_item, QTreeWidgetItem([m["filename"], summary, m["category"]]))

    def open_project_window(self, item, column):
        if item.text(2) == "Project":
            proj_name = item.text(0)
            win = ProjectWindow(proj_name, self.rag)
            win.show()

# -----------------------------------------------------------------------------
# GUI: PROJECT WINDOW
# -----------------------------------------------------------------------------
class ProjectWindow(QWidget):
    def __init__(self, proj_name, rag: RAGEngine):
        super().__init__()
        self.setWindowTitle(f"Project: {proj_name}")
        self.proj_name = proj_name
        self.rag = rag
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File", "Summary", "Category"])
        self.tree.itemSelectionChanged.connect(self.show_summary)
        layout.addWidget(self.tree, stretch=3)

        self.summary_view = QPlainTextEdit()
        self.summary_view.setReadOnly(True)
        layout.addWidget(self.summary_view, stretch=2)

        self.refresh_tree()

    def refresh_tree(self):
        self.tree.clear()
        for m in self.rag.metadata:
            if os.path.basename(os.path.dirname(m["source_path"])) or "Default" == self.proj_name:
                if os.path.basename(os.path.dirname(m["source_path"])) == self.proj_name or (self.proj_name == "Default" and not os.path.dirname(m["source_path"])):
                    summary = m.get("summary", "")[:80] + "..."
                    self.tree.addTopLevelItem(QTreeWidgetItem([m["filename"], summary, m["category"]]))

    def show_summary(self):
        sel = self.tree.selectedItems()
        if sel:
            fname = sel[0].text(0)
            md = next((m for m in self.rag.metadata if m["filename"] == fname), None)
            if md:
                self.summary_view.setPlainText(md.get("summary", ""))

# -----------------------------------------------------------------------------
# GUI: CHAT TAB
# -----------------------------------------------------------------------------
class ChatTab(QWidget):
    def __init__(self, rag: RAGEngine):
        super().__init__()
        self.rag = rag
        layout = QVBoxLayout(self)

        self.chat_view = QPlainTextEdit()
        self.chat_view.setReadOnly(True)
        layout.addWidget(self.chat_view, stretch=4)

        controls = QHBoxLayout()
        self.provider_cb = QComboBox()
        self.provider_cb.addItems(["OpenAI", "Ollama"])
        self.provider_cb.currentTextChanged.connect(self.update_models)
        controls.addWidget(self.provider_cb)

        self.model_cb = QComboBox()
        self.model_cb.addItems(["gpt-4o-mini", "phi4:latest"])
        controls.addWidget(self.model_cb)
        layout.addLayout(controls)

        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Ask your archive...")
        input_layout.addWidget(self.input_line)

        btn_send = QPushButton("Send")
        btn_send.clicked.connect(self.send_message)
        input_layout.addWidget(btn_send)
        layout.addLayout(input_layout)

        history_file = os.path.join(CHAT_HISTORY_DIR, "history.json")
        self.history = []
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            for entry in self.history:
                self.chat_view.appendPlainText(f"> {entry['role'].capitalize()}: {entry['content']}\n")

    def update_models(self):
        self.model_cb.clear()
        if self.provider_cb.currentText() == "OpenAI":
            self.model_cb.addItems(["gpt-4o-mini", "gpt-3.5-turbo"])
        else:
            self.model_cb.addItems(["phi4:latest", "mistral:latest", "gemma3:27b"])

    def send_message(self):
        q = self.input_line.text().strip()
        if not q:
            return
        self.history.append({"role": "user", "content": q})
        self.chat_view.appendPlainText(f"> You: {q}\n")

        hits = self.rag.query(q, 5)
        context = ""
        for h in hits:
            try:
                with open(os.path.join(os.path.dirname(self.rag.meta_path), "texts", f"{h['hash']}.txt"),
                          "r", encoding="utf-8") as f:
                    context += f"{h['filename']}:\n{f.read()}\n\n"
            except:
                continue

        prompt = f"Context:\n{context}\n\nQuestion: {q}\nAnswer based on context and history."
        if len(prompt) > 6000:
            prompt = recursive_summarize(prompt, CONFIG.get("chunk_size"))

        ans = ""
        prov = self.provider_cb.currentText()
        mdl = self.model_cb.currentText()
        if prov == "OpenAI":
            openai.api_key = os.getenv("OPENAI_API_KEY", "")
            try:
                res = openai.ChatCompletion.create(
                    model=mdl,
                    messages=[{"role": "system", "content": "Answer using provided context and history."}] +
                             [{"role": e["role"], "content": e["content"]} for e in self.history[-5:]] +
                             [{"role": "user", "content": prompt}],
                    max_tokens=512
                )
                ans = res.choices[0].message.content.strip()
            except Exception as e:
                ans = f"Error: {e}"
        else:
            try:
                resp = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": mdl, "prompt": prompt}, timeout=20
                )
                ans = resp.json().get("response", "")
            except Exception as e:
                ans = f"Error: {e}"

        self.history.append({"role": "assistant", "content": ans})
        self.chat_view.appendPlainText(f"> AI: {ans}\n\n")
        self.input_line.clear()

        with open(os.path.join(CHAT_HISTORY_DIR, "history.json"), "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

# -----------------------------------------------------------------------------
# GUI: SETTINGS TAB
# -----------------------------------------------------------------------------
class SettingsTab(QWidget):
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.cfg = config
        layout = QVBoxLayout(self)

        emb_layout = QHBoxLayout()
        emb_layout.addWidget(QLabel("Embedding Provider:"))
        self.cmb_emb_prov = QComboBox()
        self.cmb_emb_prov.addItems(["Ollama", "Dummy"])
        self.cmb_emb_prov.setCurrentText(self.cfg.get("text_embedding_provider"))
        emb_layout.addWidget(self.cmb_emb_prov)

        emb_layout.addWidget(QLabel("Model:"))
        self.cmb_emb_model = QComboBox()
        self.cmb_emb_model.addItems([
            "mxbai-embed-large:latest",
            "snowflake-arctic-embed:latest",
            "all-minilm:latest"
        ])
        self.cmb_emb_model.setCurrentText(self.cfg.get("text_embedding_model"))
        emb_layout.addWidget(self.cmb_emb_model)
        layout.addLayout(emb_layout)

        sum_layout = QHBoxLayout()
        sum_layout.addWidget(QLabel("Summarize Provider:"))
        self.cmb_sum_prov = QComboBox()
        self.cmb_sum_prov.addItems(["OpenAI", "Ollama"])
        self.cmb_sum_prov.setCurrentText(self.cfg.get("summary_provider"))
        sum_layout.addWidget(self.cmb_sum_prov)

        sum_layout.addWidget(QLabel("Model:"))
        self.cmb_sum_model = QComboBox()
        self.cmb_sum_model.addItems([
            "gpt-4o-mini", "phi4:latest", "mistral:latest", "gemma3:27b"
        ])
        self.cmb_sum_model.setCurrentText(self.cfg.get("summary_model"))
        sum_layout.addWidget(self.cmb_sum_model)
        layout.addLayout(sum_layout)

        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Chunk Size (tokens):"))
        self.chunk_size = QLineEdit(str(self.cfg.get("chunk_size")))
        chunk_layout.addWidget(self.chunk_size)
        layout.addLayout(chunk_layout)

        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        layout.addWidget(btn_save)

    def save_settings(self):
        self.cfg.set("text_embedding_provider", self.cmb_emb_prov.currentText())
        self.cfg.set("text_embedding_model",    self.cmb_emb_model.currentText())
        self.cfg.set("summary_provider",         self.cmb_sum_prov.currentText())
        self.cfg.set("summary_model",            self.cmb_sum_model.currentText())
        self.cfg.set("chunk_size",              int(self.chunk_size.text()))
        self.cfg.save()
        QMessageBox.information(self, "Settings", "Configuration saved.")

# -----------------------------------------------------------------------------
# MAIN WINDOW
# -----------------------------------------------------------------------------
class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Everything AI")
        self.resize(1200, 800)
        self.rag = RAGEngine()

        self.tab_ingest   = IngestorTab(self.rag)
        self.tab_audit    = AuditorTab (self.rag)
        self.tab_projects = ProjectsTab(self.rag)
        self.tab_chat     = ChatTab    (self.rag)
        self.tab_settings = SettingsTab(CONFIG)

        self.addTab(self.tab_ingest,   "Ingestor")
        self.addTab(self.tab_audit,    "Auditor")
        self.addTab(self.tab_projects, "Projects")
        self.addTab(self.tab_chat,     "Chat")
        self.addTab(self.tab_settings, "Settings")

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

My_Everything.py

A unified AI tool for managing, auditing, and recalling files/projects:
  - Drag & drop or URL ingestion of ZIPs/folders
  - Auto-extract, recursive summarize, categorize, and preview
  - Embed (vectorize), Discard, Move, Backup, Archive, or Delete
  - Global RAG-backed recall via FAISS & Ollama/OpenAI
  - Auditor view with duplicate detection and actions
  - Chat interface with history for querying archive
  - Project mirror view for folder structure
  - Settings for embedding/summarization providers/models
**Classes:** ConfigManager, ProjectManager, RAGEngine, IngestorTab, AuditorTab, ProjectsTab, ProjectWindow, ChatTab, SettingsTab, MainWindow
**Functions:** compute_hash(text), dummy_embed(text, dim), embed_via_ollama(text, dim), get_embedding(text, dim), summarize_text(text), recursive_summarize(text, max_len), extract_text_from_file(path), download_and_extract_zip(url, extract_to), backup_file(path), archive_file(path, project_name), main()
