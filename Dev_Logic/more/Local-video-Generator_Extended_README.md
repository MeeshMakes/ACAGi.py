# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analyzing the project contents. Python modules are parsed for docstrings, classes, and functions. Image files are embedded as previews. Executable files (.exe) are listed by name; their contents are intentionally skipped.

## Python Modules

- `opensora_workspace.py`
- `tools\codex_pr_sentinel.py`
- `tools\logic_inbox.py`

## Other Files

- `.git\config`
- `.git\description`
- `.git\FETCH_HEAD`
- `.git\HEAD`
- `.git\hooks\applypatch-msg.sample`
- `.git\hooks\commit-msg.sample`
- `.git\hooks\fsmonitor-watchman.sample`
- `.git\hooks\post-update.sample`
- `.git\hooks\pre-applypatch.sample`
- `.git\hooks\pre-commit.sample`
- `.git\hooks\pre-merge-commit.sample`
- `.git\hooks\pre-push.sample`
- `.git\hooks\pre-rebase.sample`
- `.git\hooks\pre-receive.sample`
- `.git\hooks\prepare-commit-msg.sample`
- `.git\hooks\push-to-checkout.sample`
- `.git\hooks\sendemail-validate.sample`
- `.git\hooks\update.sample`
- `.git\index`
- `.git\info\exclude`
- `.git\logs\HEAD`
- `.git\logs\refs\heads\main`
- `.git\logs\refs\remotes\origin\HEAD`
- `.git\objects\pack\pack-cd3b8e262107e9a9755f3f516a849ae38e1bc0b6.idx`
- `.git\objects\pack\pack-cd3b8e262107e9a9755f3f516a849ae38e1bc0b6.pack`
- `.git\objects\pack\pack-cd3b8e262107e9a9755f3f516a849ae38e1bc0b6.rev`
- `.git\packed-refs`
- `.git\refs\heads\main`
- `.git\refs\remotes\origin\HEAD`
- `.github\codex_sentinel.yml`
- `.github\workflows\codex-pr-sentinel.yml`
- `.gitignore`
- `AGENT.md`
- `Archived_Conversations\README.md`
- `CHANGELOG.md`
- `Dev_Logic\Implemented_logic\README.md`
- `Dev_Logic\README.md`
- `logs\server.log`
- `logs\session_2025-10-01.md`
- `logs\session_2025-10-02.md`
- `memory\codex_memory.json`
- `memory\logic_inbox.jsonl`
- `README.md`
- `workspace_settings.json`


## Detailed Module Analyses


## Module `opensora_workspace.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Open-Sora All-in-One (PyQt6, Windows host + WSL backend)
=========================================================
Desktop app that **SETS UP** Open-Sora (online-first setup, offline afterwards), **GENERATES** videos, and **PREVIEWS** them.
Everything stays inside this project folder. Live progress, single installer run, clear errors.

CONTRAST RULE (MANDATORY): high-contrast text vs background (dark UI, light text). No low-contrast combos.

Windows-side folders:
  logs/       -> server + job logs + crash logs
  runtime/    -> app-only temp files (no system TMP)
  outputs/    -> mirrored from WSL $REPO/outputs for in-app playback
  wheels/     -> (optional) local wheels for offline setup
  weights/    -> (optional) weights/Open-Sora-v2 or ckpts/ for offline
  repo_cache/Open-Sora -> (optional) offline repo snapshot

WSL-side layout:
  $HOME/Local video Generator/Open-Sora     (repo)
  $HOME/Local video Generator/.venv         (venv dir)
  $REPO/.cache/*                            (HF/transformers caches inside repo)
  $REPO/outputs                             (generation results)

Privacy:
  WANDB + HF hub telemetry disabled by env vars. Optional HF offline mode for generation.

Order of operations (on Setup):
  1) Check WSL
  2) Optionally Clean (delete repo & venv) for a fresh install
  3) Clone/Stage repo (online or from repo_cache)
  4) Install APT prereqs (root; non-interactive): python3-venv, python3-virtualenv, python3-pip, git, build-essential, ca-certificates, curl, ffmpeg
  5) Create venv (python3.12/3 fallback; if ensurepip missing -> bootstrap pip via get-pip.py; else virtualenv fallback)
  6) Install torch/vision & requirements (+ xformers/flash-attn best-effort)
  7) Stage weights (online huggingface-cli or offline copy)
  8) Verify imports & list weights
"""

from __future__ import annotations

import os
import sys
import shlex
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict

# ---------- Project-local folders (Windows host) ----------
BASE_DIR      = Path(__file__).resolve().parent
LOG_DIR       = BASE_DIR / "logs"
OUT_DIR_WIN   = BASE_DIR / "outputs"        # Windows-visible mirror
RUNTIME_DIR   = BASE_DIR / "runtime"
SETTINGS_JSON = BASE_DIR / "workspace_settings.json"
CRASH_LOG     = LOG_DIR / "crash.log"
SERVER_LOG    = LOG_DIR / "server.log"

for d in (LOG_DIR, OUT_DIR_WIN, RUNTIME_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Keep all temp files inside project (no low-contrast UI note: not relevant to TMP)
os.environ["TMP"] = str(RUNTIME_DIR)
os.environ["TEMP"] = str(RUNTIME_DIR)
os.environ["TMPDIR"] = str(RUNTIME_DIR)

# ---------- WSL defaults ----------
DEFAULT_WSL_HOME_VAR = "$HOME"
DEFAULT_WSL_ROOT     = f'{DEFAULT_WSL_HOME_VAR}/Local video Generator'
DEFAULT_WSL_REPO     = f'{DEFAULT_WSL_ROOT}/Open-Sora'
DEFAULT_WSL_VENV_DIR = f'{DEFAULT_WSL_ROOT}/.venv'
DEFAULT_WSL_VENV_ACT = f'{DEFAULT_WSL_VENV_DIR}/bin/activate'


def repo_outputs_dir(repo: str) -> str:
    """Return the outputs directory associated with a given WSL repository path."""

    repo = (repo or "").rstrip("/")
    return f"{repo}/outputs" if repo else "outputs"


DEFAULT_WSL_OUTPUTS  = repo_outputs_dir(DEFAULT_WSL_REPO)

# Caches/telemetry — exported on every call inside WSL
WSL_CACHE_EXPORT = (
    "export HF_HOME=./.cache/hf; "
    "export TRANSFORMERS_CACHE=./.cache/transformers; "
    "export XDG_CACHE_HOME=./.cache; "
)
WSL_PRIVACY_EXPORT = (
    "export HF_HUB_DISABLE_TELEMETRY=1; "
    "export WANDB_DISABLED=1; "
    "export TF_DISABLE_TELEMETRY=1; "
    "export PIP_DISABLE_PIP_VERSION_CHECK=1; "
    "export TRANSFORMERS_NO_ADVISORY_WARNINGS=1; "
)
WSL_HF_OFFLINE_EXPORT = "export HF_HUB_OFFLINE=1; "

# ---------- logging ----------
def _stamp() -> str:
    return time.strftime("%H:%M:%S")

def log_line(msg: str) -> str:
    line = f"[{_stamp()}] {msg}"
    print(line, flush=True)
    SERVER_LOG.parent.mkdir(parents=True, exist_ok=True)
    with SERVER_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return line

# ---------- WSL helpers ----------
def wsl_ok() -> bool:
    try:
        subprocess.check_output(["wsl.exe", "-e", "bash", "-lc", "echo OK"], text=True, timeout=8)
        return True
    except Exception:
        return False

def wsl_run(cmd: str, timeout: Optional[int] = None) -> Tuple[int, str]:
    try:
        p = subprocess.Popen(["wsl.exe", "-e", "bash", "-lc", cmd],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True)
        out = p.communicate(timeout=timeout)[0] if timeout else p.communicate()[0]
        return p.returncode, out
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or "") + "\n[TIMEOUT]"
    except Exception as e:
        return 1, f"[EXC] {e!r}"

def wsl_stream(cmd: str, line_cb, end_cb=None) -> int:
    try:
        p = subprocess.Popen(["wsl.exe", "-e", "bash", "-lc", cmd],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, bufsize=1)
        assert p.stdout is not None
        for ln in p.stdout:
            line_cb(ln.rstrip("\n"))
        rc = p.wait()
        if end_cb: end_cb(rc)
        return rc
    except Exception as e:
        line_cb(f"[stream error] {e!r}")
        if end_cb: end_cb(1)
        return 1

# Run as root (no sudo prompts)
def wsl_run_root(cmd: str, timeout: Optional[int] = None) -> Tuple[int, str]:
    try:
        p = subprocess.Popen(["wsl.exe", "-u", "root", "-e", "bash", "-lc", cmd],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True)
        out = p.communicate(timeout=timeout)[0] if timeout else p.communicate()[0]
        return p.returncode, out
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or "") + "\n[TIMEOUT]"
    except Exception as e:
        return 1, f"[EXC] {e!r}"

def wsl_stream_root(cmd: str, line_cb, end_cb=None) -> int:
    try:
        p = subprocess.Popen(["wsl.exe", "-u", "root", "-e", "bash", "-lc", cmd],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, bufsize=1)
        assert p.stdout is not None
        for ln in p.stdout:
            line_cb(ln.rstrip("\n"))
        rc = p.wait()
        if end_cb: end_cb(rc)
        return rc
    except Exception as e:
        line_cb(f"[root stream error] {e!r}")
        if end_cb: end_cb(1)
        return 1

def bashify(path_like: str) -> str:
    if path_like.startswith("$HOME"):
        return '"' + path_like.replace('"', r'\"') + '"'
    return shlex.quote(path_like)

def win_to_wsl_path(p: Path) -> str:
    p = p.resolve()
    drive = p.drive.rstrip(":").lower()
    return shlex.quote(f"/mnt/{drive}{p.as_posix()[2:]}")

def wsl_file_exists(path_like: str) -> bool:
    rc, out = wsl_run(f"test -e {bashify(path_like)} && echo OK || echo MISS", timeout=8)
    return "OK" in (out or "")

# ---------- Installer logic ----------
def choose_pytorch_index_cuda_label(auto_or_label: str) -> Tuple[str, str]:
    c = (auto_or_label or "auto").lower()
    if c in ("cu121", "cu124", "cpu"):
        idx = f"https://download.pytorch.org/whl/{'cpu' if c=='cpu' else c}"
        return c, idx
    rc, out = wsl_run("nvidia-smi | awk -F'CUDA Version: ' '/CUDA Version/{print $2}' | awk '{print $1}'", timeout=5)
    if rc != 0 or not out.strip():
        return "cpu", "https://download.pytorch.org/whl/cpu"
    try:
        maj, minr = out.strip().split(".")[:2]
        minr = int(minr)
        return ("cu124", "https://download.pytorch.org/whl/cu124") if int(maj) > 12 or minr >= 4 \
               else ("cu121", "https://download.pytorch.org/whl/cu121")
    except Exception:
        return "cu121", "https://download.pytorch.org/whl/cu121"

def ensure_wsl_root():
    wsl_run(f"mkdir -p {bashify(DEFAULT_WSL_ROOT)}", timeout=10)

def ensure_linux_prereqs(online: bool, stream) -> bool:
    """
    Install system prerequisites as root, non-interactively.
    Noble/Ubuntu packages: python3-venv, python3-virtualenv, python3-pip, git, build-essential, ca-certificates, curl, ffmpeg
    (We intentionally do NOT ask for python3.10-venv; it's not in Noble.)
    """
    if not online:
        stream("Offline mode: skipping apt prerequisites.")
        return True
    stream("[root] apt-get update/install prerequisites…")
    rc = wsl_stream_root(
        "set -e; export DEBIAN_FRONTEND=noninteractive; "
        "apt-get update -y && "
        "apt-get install -y --no-install-recommends "
        "python3-venv python3-virtualenv python3-pip git build-essential ca-certificates curl ffmpeg && "
        "update-ca-certificates || true",
        stream
    )
    return rc == 0

def maybe_force_clean(force: bool, stream, repo: str, venv_dir: str):
    if not force:
        return
    stream(f"[CLEAN] Removing repo {repo} and venv {venv_dir}")
    wsl_stream_root(f"rm -rf {bashify(repo)} {bashify(venv_dir)}", stream)

def clone_or_stage_repo_wsl(repo: str, *, online: bool, stream) -> bool:
    if online:
        cmd = (
            f"if [ ! -d {bashify(repo)} ]; then "
            f"  cd {bashify(DEFAULT_WSL_ROOT)} && git clone --depth 1 --branch main https://github.com/hpcaitech/Open-Sora.git {bashify(repo)}; "
            f"else echo 'REPO_EXISTS'; fi"
        )
        rc = wsl_stream(cmd, stream)
        return rc == 0
    src_folder = BASE_DIR / "repo_cache" / "Open-Sora"
    if src_folder.exists():
        src_w = win_to_wsl_path(src_folder)
        wsl_stream(f"rm -rf {bashify(repo)} && mkdir -p {bashify(repo)}", stream)
        rc = wsl_stream(f"cp -a {src_w}/. {bashify(repo)}/", stream)
        return rc == 0
    stream("Offline repo staging failed: place a copy at repo_cache/Open-Sora")
    return False

def _venv_ok(venv_dir: str) -> bool:
    return wsl_file_exists(f'{venv_dir}/bin/activate') and wsl_file_exists(f'{venv_dir}/bin/python') and wsl_file_exists(f'{venv_dir}/bin/pip')

def _pip_ok(venv_dir: str) -> bool:
    return wsl_file_exists(f'{venv_dir}/bin/pip')

def create_or_reuse_venv_wsl(venv_dir: str, online: bool, stream) -> bool:
    """
    Robust venv creation under WSL:
      * Try python3.12/3 venv
      * If ensurepip missing, bootstrap pip with get-pip.py when online
      * If still stuck, try virtualenv -p python3.12 or python3
      * Verify bin/python, bin/activate, bin/pip
    """
    if _venv_ok(venv_dir):
        stream("venv exists and looks valid.")
        return True

    cmds = [
        f'command -v python3.12 >/dev/null 2>&1 && python3.12 -m venv {bashify(venv_dir)} || true',
        f'command -v python3 >/dev/null 2>&1 && python3 -m venv {bashify(venv_dir)} || true',
    ]
    for c in cmds:
        stream(f"$ {c}")
        wsl_stream(c, stream)
        if wsl_file_exists(f'{venv_dir}/bin/activate') and wsl_file_exists(f'{venv_dir}/bin/python'):
            break

    # Bootstrap pip if missing and we created a venv
    if wsl_file_exists(f'{venv_dir}/bin/python') and not _pip_ok(venv_dir):
        if online:
            stream("Bootstrapping pip (get-pip.py)…")
            wsl_stream(
                f"cd {bashify(DEFAULT_WSL_ROOT)} && "
                f"curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && "
                f"{bashify(venv_dir)}/bin/python get-pip.py && rm -f get-pip.py",
                stream
            )

    # If still no activate or pip, try virtualenv fallback
    if not _venv_ok(venv_dir):
        stream("Falling back to virtualenv…")
        vcmds = [
            f'command -v virtualenv >/dev/null 2>&1 && virtualenv -p python3.12 {bashify(venv_dir)} || true',
            f'command -v virtualenv >/dev/null 2>&1 && virtualenv -p python3 {bashify(venv_dir)} || true',
            f'command -v virtualenv >/dev/null 2>&1 && virtualenv {bashify(venv_dir)} || true',
        ]
        for c in vcmds:
            stream(f"$ {c}")
            wsl_stream(c, stream)
            if _venv_ok(venv_dir):
                break

        # If virtualenv created python but pip still missing, try get-pip.py online
        if wsl_file_exists(f'{venv_dir}/bin/python') and not _pip_ok(venv_dir) and online:
            stream("Bootstrapping pip (get-pip.py) after virtualenv…")
            wsl_stream(
                f"cd {bashify(DEFAULT_WSL_ROOT)} && "
                f"curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && "
                f"{bashify(venv_dir)}/bin/python get-pip.py && rm -f get-pip.py",
                stream
            )

    if not _venv_ok(venv_dir):
        stream("venv create failed (activate/python/pip missing).")
        return False

    # Final: ensure pip is usable
    wsl_stream(f'{bashify(venv_dir)}/bin/pip --version || true', stream)
    return True

def pip_install_wsl_stream(venv_act: str, args: str, *, index_url: Optional[str]=None,
                           offline: bool=False, wheels_dir_win: Optional[Path]=None,
                           stream=None) -> bool:
    if not wsl_file_exists(venv_act):
        if stream: stream(f"activate missing: {venv_act}")
        return False
    if offline:
        if not wheels_dir_win or not wheels_dir_win.exists():
            if stream: stream("Offline install requested but wheels dir not found.")
            return False
        wheels_wsl = win_to_wsl_path(wheels_dir_win)
        cmd = f"source {bashify(venv_act)} && python -m pip install --no-index --find-links {wheels_wsl} {args}"
    else:
        if index_url:
            cmd = f"source {bashify(venv_act)} && python -m pip install --index-url {shlex.quote(index_url)} {args}"
        else:
            cmd = f"source {bashify(venv_act)} && python -m pip install {args}"
    rc = wsl_stream(cmd, stream or (lambda l: None))
    return rc == 0

def install_deps_wsl(repo: str, venv_act: str, *, online: bool, cuda_label: str,
                     wheels_dir_win: Optional[Path], stream) -> bool:
    if not wsl_file_exists(venv_act):
        stream("activate missing — cannot install deps.")
        return False

    ok_all = True

    # Upgrade pip/setuptools/wheel
    ok = pip_install_wsl_stream(venv_act, "-U pip setuptools wheel", offline=False, stream=stream)
    ok_all &= ok

    # Torch + torchvision
    label, idx = choose_pytorch_index_cuda_label(cuda_label)
    stream(f"PyTorch index: {idx}")
    ok = pip_install_wsl_stream(venv_act, "torch==2.4.0 torchvision==0.19.0",
                                index_url=(None if not online else idx),
                                offline=(not online), wheels_dir_win=wheels_dir_win, stream=stream)
    if not ok and online and label != "cpu":
        stream("CUDA wheels failed, retrying CPU wheels…")
        ok = pip_install_wsl_stream(venv_act, "torch==2.4.0 torchvision==0.19.0",
                                    index_url="https://download.pytorch.org/whl/cpu",
                                    offline=False, wheels_dir_win=None, stream=stream)
    ok_all &= ok

    # Project requirements
    if online:
        rc = wsl_stream(f"cd {bashify(repo)} && source {bashify(venv_act)} && python -m pip install -r requirements.txt", stream)
        ok_all &= (rc == 0)
    else:
        ok = pip_install_wsl_stream(venv_act, f"-r {bashify(repo)}/requirements.txt",
                                    offline=True, wheels_dir_win=wheels_dir_win, stream=stream)
        ok_all &= ok

    # Optional accelerators (best-effort)
    if online:
        pip_install_wsl_stream(venv_act, "xformers==0.0.27.post2", index_url=idx, stream=stream)
    else:
        pip_install_wsl_stream(venv_act, "xformers==0.0.27.post2", offline=True, wheels_dir_win=wheels_dir_win, stream=stream)

    pip_install_wsl_stream(venv_act, "flash-attn --no-build-isolation",
                           offline=not online, wheels_dir_win=wheels_dir_win, stream=stream)

    # Install repo itself
    rc = wsl_stream(f"cd {bashify(repo)} && source {bashify(venv_act)} && python -m pip install -v .", stream)
    ok_all &= (rc == 0)

    # Verify imports
    rc, out = wsl_run(
        f"cd {bashify(repo)} && source {bashify(venv_act)} && "
        f"{WSL_CACHE_EXPORT}{WSL_PRIVACY_EXPORT} python - <<'PY'\n"
        "import sys\n"
        "print('python', sys.version)\n"
        "ok=True\n"
        "try:\n"
        "  import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())\n"
        "except Exception as e:\n"
        "  print('torch_import_error', repr(e)); ok=False\n"
        "try:\n"
        "  import opensora; print('opensora_import', 'ok')\n"
        "except Exception as e:\n"
        "  print('opensora_import_error', repr(e)); ok=False\n"
        "print('OK' if ok else 'FAIL')\n"
        "PY\n", timeout=180)
    stream(out.strip())
    ok_all &= ("OK" in (out or ""))

    return ok_all

def stage_weights_wsl(repo: str, *, online: bool, venv_act: str,
                      weights_dir_win: Optional[Path], stream) -> bool:
    ckpts = f"{repo}/ckpts"
    rc = wsl_stream(f"mkdir -p {bashify(ckpts)}", stream)
    if rc != 0:
        return False
    if online:
        pip_install_wsl_stream(venv_act, "-U 'huggingface_hub[cli]'", offline=False, stream=stream)
        rc = wsl_stream(f"source {bashify(venv_act)} && huggingface-cli download hpcai-tech/Open-Sora-v2 --local-dir {bashify(ckpts)}", stream)
        if rc != 0:
            stream("huggingface-cli download failed (model may require acceptance/login). Place weights offline into weights/Open-Sora-v2 or repo/ckpts and rerun.")
        return rc == 0
    # Offline copy
    candidates = []
    if weights_dir_win and weights_dir_win.exists():
        candidates.append(weights_dir_win)
    if (BASE_DIR / "weights" / "Open-Sora-v2").exists():
        candidates.append(BASE_DIR / "weights" / "Open-Sora-v2")
    if (BASE_DIR / "ckpts").exists():
        candidates.append(BASE_DIR / "ckpts")
    if not candidates:
        stream("No offline weights directory found; add weights to run fully offline.")
        return False
    src = candidates[0]
    stream(f"Staging weights from: {src}")
    src_wsl = win_to_wsl_path(src)
    rc = wsl_stream(f"cp -a {src_wsl}/. {bashify(ckpts)}/", stream)
    return rc == 0

# ---------- PyQt6 UI ----------
try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PyQt6.QtMultimediaWidgets import QVideoWidget
    from PyQt6.QtCore import Qt, QUrl
except Exception as e:
    print(
        "PyQt6 missing. Install:\n"
        "  py -3.10 -m pip install PyQt6 PyQt6-Qt6 PyQt6-sip\n"
        f"Import error: {e}",
        file=sys.stderr)
    raise

class StreamProc(QtCore.QThread):
    line = QtCore.pyqtSignal(str)
    done = QtCore.pyqtSignal(int)
    def __init__(self, proc: subprocess.Popen):
        super().__init__()
        self._p = proc
    def run(self):
        try:
            assert self._p.stdout is not None
            for ln in self._p.stdout:
                self.line.emit(ln.rstrip("\n"))
        except Exception as e:
            self.line.emit(f"[stream] {e!r}")
        finally:
            rc = self._p.poll()
            self.done.emit(0 if rc is None else rc)

class SetupWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(int, str)
    line     = QtCore.pyqtSignal(str)
    finished_ok = QtCore.pyqtSignal(bool)
    def __init__(self, repo: str, venv: str, *, online: bool, cuda_label: str,
                 wheels_dir: Optional[Path], weights_dir: Optional[Path],
                 force_clean: bool):
        super().__init__()
        self.repo = repo
        self.venv = venv
        venv_path = Path(self.venv)
        self.venv_dir = str(venv_path.parent.parent if len(venv_path.parents) >= 2 else venv_path.parent)
        self.online = online
        self.cuda_label = cuda_label
        self.wheels_dir = wheels_dir
        self.weights_dir = weights_dir
        self.force_clean = force_clean
        self._cancel = False
    def cancel(self): self._cancel = True
    def s(self, msg: str): self.line.emit(msg)
    def run(self):
        steps = [
            ("Check WSL", self.step_check_wsl),
            ("Create root dir", self.step_root),
            ("Clean (optional)", self.step_clean),
            ("Clone/Stage repo", self.step_repo),
            ("Install APT prereqs", self.step_prereqs),
            ("Create venv", self.step_venv),
            ("Install deps", self.step_deps),
            ("Stage weights", self.step_weights),
            ("Make outputs dir", self.step_outputs),
            ("Verify final", self.step_verify),
        ]
        n = len(steps); ok = True
        for i, (title, fn) in enumerate(steps, start=1):
            if self._cancel: ok = False; break
            self.progress.emit(int((i-1)/n*100), f"{title} …")
            try:
                if not fn(): ok = False; break
            except Exception as e:
                self.s(f"[error] {title}: {e!r}"); ok = False; break
        self.progress.emit(100 if ok else 0, "Done" if ok else "Failed")
        self.finished_ok.emit(ok)
    def step_check_wsl(self) -> bool:
        if not wsl_ok(): self.s("WSL is not available."); return False
        self.s("WSL OK."); return True
    def step_root(self) -> bool:
        ensure_wsl_root(); self.s(f"Root dir ready at {DEFAULT_WSL_ROOT}"); return True
    def step_clean(self) -> bool:
        if self.force_clean: maybe_force_clean(True, self.s, self.repo, self.venv_dir)
        return True
    def step_repo(self) -> bool:
        self.s(f"Preparing repo at {self.repo}")
        return clone_or_stage_repo_wsl(self.repo, online=self.online, stream=self.s)
    def step_prereqs(self) -> bool:
        return ensure_linux_prereqs(self.online, self.s)
    def step_venv(self) -> bool:
        self.s(f"Preparing venv at {self.venv_dir}")
        ok = create_or_reuse_venv_wsl(self.venv_dir, online=self.online, stream=self.s)
        self.s("venv verified (python/activate/pip present)." if ok else "venv verification failed.")
        return ok
    def step_deps(self) -> bool:
        self.s("Installing dependencies (torch/vision, requirements, xformers, flash-attn, repo)…")
        return install_deps_wsl(self.repo, self.venv, online=self.online, cuda_label=self.cuda_label,
                                wheels_dir_win=self.wheels_dir, stream=self.s)
    def step_weights(self) -> bool:
        self.s("Staging weights into ckpts/ …")
        return stage_weights_wsl(self.repo, online=self.online, venv_act=self.venv,
                                 weights_dir_win=self.weights_dir, stream=self.s)
    def step_outputs(self) -> bool:
        outputs_dir = repo_outputs_dir(self.repo)
        rc, _ = wsl_run(f"mkdir -p {bashify(outputs_dir)}", timeout=20)
        return rc == 0
    def step_verify(self) -> bool:
        ok = wsl_file_exists(self.venv)
        if not ok: self.s("Final verify: venv activate missing."); return False
        rc, out = wsl_run(
            f"cd {bashify(self.repo)} && source {bashify(self.venv)} && "
            f"{WSL_CACHE_EXPORT}{WSL_PRIVACY_EXPORT} python - <<'PY'\n"
            "import os, sys\n"
            "ok=True\n"
            "try:\n"
            "  import torch\n"
            "  print('torch', torch.__version__, 'cuda', torch.cuda.is_available())\n"
            "except Exception as e:\n"
            "  print('torch_import_error', repr(e)); ok=False\n"
            "try:\n"
            "  import opensora; print('opensora_import', 'ok')\n"
            "except Exception as e:\n"
            "  print('opensora_import_error', repr(e)); ok=False\n"
            "print('OK' if ok else 'FAIL')\n"
            "PY\n", timeout=180)
        self.s(out.strip())
        return "OK" in (out or "")

class SetupDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setup Progress")
        self.resize(860, 560)
        self.setModal(True)
        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("Starting…")
        self.pbar  = QtWidgets.QProgressBar(); self.pbar.setRange(0, 100)
        self.log   = QtWidgets.QPlainTextEdit(); self.log.setReadOnly(True); self.log.setMaximumBlockCount(100000)
        self.log.setStyleSheet("QPlainTextEdit { background:#0f0f0f; color:#EAEAEA; border:1px solid #2A2A2A; }")  # CONTRAST
        btns  = QtWidgets.QHBoxLayout()
        self.cancelBtn = QtWidgets.QPushButton("Cancel")
        self.closeBtn  = QtWidgets.QPushButton("Close"); self.closeBtn.setEnabled(False)
        btns.addStretch(1); btns.addWidget(self.cancelBtn); btns.addWidget(self.closeBtn)
        layout.addWidget(self.label); layout.addWidget(self.pbar); layout.addWidget(self.log, 1); layout.addLayout(btns)
    def append(self, line: str):
        self.log.appendPlainText(line)
        sb = self.log.verticalScrollBar(); sb.setValue(sb.maximum())

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open-Sora All-in-One (PyQt6)")
        self.resize(1480, 960)
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#121212"))
        pal.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor("#0f0f0f"))
        pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor("#1b1b1b"))
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("#EAEAEA"))
        pal.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("#EAEAEA"))
        self.setPalette(pal)
        self.setStyleSheet("""
            QWidget { background:#121212; color:#EAEAEA; } /* High contrast enforced */
            QLineEdit, QComboBox, QTextEdit, QPlainTextEdit, QListWidget {
                background:#181818; color:#EAEAEA; border:1px solid #2A2A2A; border-radius:6px;
            }
            QPushButton {
                background:#1F2A3A; border:1px solid #2E5A9B; border-radius:6px; padding:6px 10px;
            }
            QPushButton:hover { background:#2A3A52; }
            QPushButton[destructive="true"] { background:#402222; border:1px solid #8b3b3b; }
            QGroupBox { border:1px solid #2A2A2A; border-radius:8px; margin-top:10px; }
            QGroupBox::title { subcontrol-origin: margin; left:10px; padding:0 6px; color:#B8B8B8; }
            QSplitter::handle { background:#2A2A2A; }
        """)
        self.mono = QtGui.QFont("Consolas, Menlo, 'DejaVu Sans Mono'", 10)

        self.proc: Optional[subprocess.Popen] = None
        self.reader: Optional[StreamProc] = None
        self.setup_worker: Optional[SetupWorker] = None
        self.setup_running: bool = False

        self.settings = self.load_settings()

        # Left: Setup + Generate
        left = QtWidgets.QWidget(); l = QtWidgets.QVBoxLayout(left); l.setContentsMargins(8,8,8,8); l.setSpacing(8)
        gSetup = QtWidgets.QGroupBox("Setup (WSL)"); f = QtWidgets.QFormLayout(gSetup)
        self.repoEdit = QtWidgets.QLineEdit(self.settings["wsl_repo"])
        self.venvEdit = QtWidgets.QLineEdit(self.settings["wsl_venv"])
        self.onlineCheck = QtWidgets.QCheckBox("Online (first time). Untick for 100% offline after.")
        self.onlineCheck.setChecked(True)
        self.forceClean = QtWidgets.QCheckBox("Force clean install (delete repo & venv)")
        self.cudaCombo = QtWidgets.QComboBox(); self.cudaCombo.addItems(["auto (detect)", "cu121", "cu124", "cpu"])
        self.wheelsEdit  = QtWidgets.QLineEdit(str(self.settings.get("wheels_dir", BASE_DIR / "wheels")));   btnWheels  = QtWidgets.QPushButton("…")
        self.weightsEdit = QtWidgets.QLineEdit(str(self.settings.get("weights_dir", BASE_DIR / "weights" / "Open-Sora-v2"))); btnWeights = QtWidgets.QPushButton("…")
        btnWheels.clicked.connect(self.browse_wheels); btnWeights.clicked.connect(self.browse_weights)
        rowWheels  = QtWidgets.QHBoxLayout(); rowWheels.addWidget(self.wheelsEdit);  rowWheels.addWidget(btnWheels)
        rowWeights = QtWidgets.QHBoxLayout(); rowWeights.addWidget(self.weightsEdit); rowWeights.addWidget(btnWeights)
        self.setupBtn = QtWidgets.QPushButton("Create / Repair (Full)")
        self.setupReqBtn = QtWidgets.QPushButton("Only Install Requirements")
        self.termBtn = QtWidgets.QPushButton("Open WSL Terminal")
        f.addRow("Repo ($HOME…)", self.repoEdit)
        f.addRow("Venv activate", self.venvEdit)
        f.addRow(self.onlineCheck)
        f.addRow(self.forceClean)
        f.addRow("Torch wheels", self.cudaCombo)
        f.addRow("Offline wheels (Windows)", rowWheels)
        f.addRow("Offline weights (Windows)", rowWeights)
        f.addRow(self.setupBtn, self.setupReqBtn)
        f.addRow(self.termBtn)

        gGen = QtWidgets.QGroupBox("Generate"); ff = QtWidgets.QFormLayout(gGen)
        self.promptEdit = QtWidgets.QLineEdit(); self.promptEdit.setPlaceholderText("e.g., raining, sea")
        self.preset = QtWidgets.QComboBox(); self.preset.addItems(["256 (t2i2v_256px)", "768 (t2i2v_768px)"])
        self.seedEdit = QtWidgets.QLineEdit(); self.seedEdit.setPlaceholderText("blank = random")
        self.offload = QtWidgets.QCheckBox("Offload to save VRAM")
        self.hfOffline = QtWidgets.QCheckBox("HF Hub OFFLINE for generation")
        self.startBtn = QtWidgets.QPushButton("Start")
        self.stopBtn  = QtWidgets.QPushButton("Stop"); self.stopBtn.setProperty("destructive", True)
        self.diagBtn  = QtWidgets.QPushButton("Diagnostics")
        h = QtWidgets.QHBoxLayout(); h.addWidget(self.startBtn); h.addWidget(self.stopBtn); h.addWidget(self.diagBtn)
        ff.addRow("Prompt", self.promptEdit); ff.addRow("Preset", self.preset)
        ff.addRow("Seed", self.seedEdit); ff.addRow("", self.offload); ff.addRow("", self.hfOffline); ff.addRow(h)
        l.addWidget(gSetup); l.addWidget(gGen); l.addStretch(1)

        # Right: Logs + Video + List
        right = QtWidgets.QWidget(); r = QtWidgets.QVBoxLayout(right); r.setContentsMargins(8,8,8,8); r.setSpacing(8)
        splitTop = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        gSys = QtWidgets.QGroupBox("System Console"); vs = QtWidgets.QVBoxLayout(gSys)
        self.sysLog = QtWidgets.QPlainTextEdit(); self.sysLog.setReadOnly(True); self.sysLog.setFont(self.mono); self.sysLog.setMaximumBlockCount(100000)
        vs.addWidget(self.sysLog)
        gJob = QtWidgets.QGroupBox("Job Log"); vj = QtWidgets.QVBoxLayout(gJob)
        self.jobLog = QtWidgets.QPlainTextEdit(); self.jobLog.setReadOnly(True); self.jobLog.setFont(self.mono); self.jobLog.setMaximumBlockCount(100000)
        vj.addWidget(self.jobLog)
        splitTop.addWidget(gSys); splitTop.addWidget(gJob); splitTop.setStretchFactor(0,1); splitTop.setStretchFactor(1,1)

        splitBot = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        gVid = QtWidgets.QGroupBox("Preview"); vv = QtWidgets.QVBoxLayout(gVid)
        self.videoWidget = QVideoWidget()
        self.player = QMediaPlayer(); self.audio = QAudioOutput(); self.player.setVideoOutput(self.videoWidget); self.player.setAudioOutput(self.audio)
        self.openExt = QtWidgets.QPushButton("Open Externally"); self.openExt.clicked.connect(self.open_external_video)
        vv.addWidget(self.videoWidget, stretch=6)
        vv.addWidget(self.openExt)
        gList = QtWidgets.QGroupBox("Videos (Windows outputs/)"); vl = QtWidgets.QVBoxLayout(gList)
        self.listView = QtWidgets.QListWidget()
        self.refreshBtn = QtWidgets.QPushButton("Refresh / Pull from repo"); self.refreshBtn.clicked.connect(self.refresh_videos)
        vl.addWidget(self.listView); vl.addWidget(self.refreshBtn)
        splitBot.addWidget(gVid); splitBot.addWidget(gList); splitBot.setStretchFactor(0,3); splitBot.setStretchFactor(1,2)

        r.addWidget(splitTop); r.addWidget(splitBot)
        main = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        main.addWidget(left); main.addWidget(right)
        main.setStretchFactor(0,0); main.setStretchFactor(1,1)
        self.setCentralWidget(main)

        # Wire buttons
        self.setupBtn.clicked.connect(self.full_setup_dialog)
        self.setupReqBtn.clicked.connect(self.install_requirements_only_dialog)
        self.termBtn.clicked.connect(self.open_wsl_terminal)
        self.startBtn.clicked.connect(self.start_job)
        self.stopBtn.clicked.connect(self.stop_job)
        self.diagBtn.clicked.connect(self.run_diagnostics)
        self.listView.itemSelectionChanged.connect(self.play_selected)

        # Boot
        self.log_sys(f"Workspace dir: {BASE_DIR}")
        self.log_sys(f"Outputs dir (Windows mirror): {OUT_DIR_WIN}")
        self.log_sys(f"Logs dir: {LOG_DIR}")
        if not wsl_ok():
            self.log_sys("⚠ WSL not responding. Install/enable WSL + Ubuntu.", warn=True)
        self.refresh_videos()
        missing = []
        if not self.wsl_exists(DEFAULT_WSL_REPO): missing.append("repo")
        if not self.wsl_exists(DEFAULT_WSL_VENV_ACT): missing.append("venv")
        if missing:
            self.log_sys(f"Missing: {', '.join(missing)}")
            online_default = self.onlineCheck.isChecked()
            cuda_default = self.cudaCombo.currentText().split()[0]
            self.run_full_setup_now(
                online=online_default,
                cuda_label=cuda_default,
                wheels_dir=self.wheelsEdit.text(),
                weights_dir=self.weightsEdit.text(),
                force_clean=self.forceClean.isChecked(),
            )
        else:
            self.run_diagnostics(silent=True)

    # ----- settings -----
    def save_settings(self) -> Dict[str,str]:
        s = {
            "wsl_repo": self.repoEdit.text().strip() or DEFAULT_WSL_REPO,
            "wsl_venv": self.venvEdit.text().strip() or DEFAULT_WSL_VENV_ACT,
            "wheels_dir": self.wheelsEdit.text().strip(),
            "weights_dir": self.weightsEdit.text().strip(),
        }
        SETTINGS_JSON.write_text(json.dumps(s, indent=2), encoding="utf-8")
        return s
    def load_settings(self) -> Dict[str,str]:
        s = {"wsl_repo": DEFAULT_WSL_REPO, "wsl_venv": DEFAULT_WSL_VENV_ACT}
        if SETTINGS_JSON.exists():
            try: s.update(json.loads(SETTINGS_JSON.read_text(encoding="utf-8")))
            except Exception as e: log_line(f"settings read error: {e!r}")
        for k in ("wsl_repo","wsl_venv"):
            if s[k].startswith("~"): s[k] = s[k].replace("~", DEFAULT_WSL_HOME_VAR, 1)
        return s

    # ----- ui helpers -----
    def set_setup_busy(self, busy: bool):
        self.setup_running = busy
        self.setupBtn.setEnabled(not busy)
        self.setupReqBtn.setEnabled(not busy)
        self.termBtn.setEnabled(not busy)

    def log_sys(self, text: str, warn: bool=False):
        line = log_line(text)
        if warn: line = "⚠ " + line
        self.sysLog.appendPlainText(line)
        self.sysLog.verticalScrollBar().setValue(self.sysLog.verticalScrollBar().maximum())
    def log_job(self, text: str):
        line = f"[{_stamp()}] {text}"
        self.jobLog.appendPlainText(line)
        self.jobLog.verticalScrollBar().setValue(self.jobLog.verticalScrollBar().maximum())
    def browse_wheels(self):
        dlg = QtWidgets.QFileDialog(self, "Select wheels folder"); dlg.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        if dlg.exec():
            sel = dlg.selectedFiles()
            if sel: self.wheelsEdit.setText(sel[0])
    def browse_weights(self):
        dlg = QtWidgets.QFileDialog(self, "Select weights folder (contains model files)"); dlg.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        if dlg.exec():
            sel = dlg.selectedFiles()
            if sel: self.weightsEdit.setText(sel[0])

    # ----- diagnostics -----
    def wsl_exists(self, path_like: str) -> bool:
        rc, out = wsl_run(f"test -e {bashify(path_like)} && echo OK || echo MISS", timeout=8)
        return "OK" in (out or "")
    def run_diagnostics(self, *, silent: bool=False):
        s = self.save_settings()
        ok = wsl_ok()
        self.log_sys(f"[{'OK' if ok else 'FAIL'}] WSL available — {'wsl.exe responded' if ok else 'wsl.exe not responding'}", warn=not ok)
        repo = s["wsl_repo"]; venv = s["wsl_venv"]
        ok_repo = self.wsl_exists(repo); self.log_sys(f"[{'OK' if ok_repo else 'FAIL'}] Repo path — {repo}", warn=not ok_repo)
        ok_venv = self.wsl_exists(venv); self.log_sys(f"[{'OK' if ok_venv else 'FAIL'}] Venv activate — {venv}", warn=not ok_venv)
        if ok_repo and ok_venv:
            rc, out = wsl_run(
                f"cd {bashify(repo)} && source {bashify(venv)} && "
                f"{WSL_CACHE_EXPORT}{WSL_PRIVACY_EXPORT} python - <<'PY'\n"
                "import sys\n"
                "print('python', sys.version)\n"
                "try:\n"
                "  import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())\n"
                "except Exception as e:\n"
                "  print('torch_import_error', repr(e))\n"
                "try:\n"
                "  import opensora; print('opensora_import', 'ok')\n"
                "except Exception as e:\n"
                "  print('opensora_import_error', repr(e))\n"
                "PY\n", timeout=180)
            self.log_sys(f"[{'OK' if rc == 0 else 'FAIL'}] Python/torch/opensora — {out.strip()}", warn=(rc != 0))
            rc2, out2 = wsl_run(
                f"cd {bashify(repo)} && [ -d ckpts ] && find ckpts -type f -maxdepth 3 2>/dev/null | head -n 3 | wc -l || echo 0",
                timeout=10)
            try: n = int(out2.strip() or "0")
            except Exception: n = 0
            self.log_sys(f"[{'OK' if n>0 else 'FAIL'}] Weights in ckpts/ — files_found={n}", warn=(n==0))
        else:
            self.log_sys("[FAIL] Python/torch/opensora — Skipped: missing repo/venv.", warn=True)
            self.log_sys("[FAIL] Weights in ckpts/ — Skipped: repo missing", warn=True)
        if not silent:
            QtWidgets.QMessageBox.information(self, "Diagnostics", "Checks complete. See System Console for details.")

    # ----- setup actions -----
    @staticmethod
    def _normalize_optional_path(value: Optional[str | Path]) -> Optional[Path]:
        """Convert optional string/Path values into ``Path`` objects or ``None``."""
        if value is None:
            return None
        if isinstance(value, Path):
            return value
        stripped = value.strip()
        return Path(stripped) if stripped else None

    def run_full_setup_now(self, *, online: bool, cuda_label: str,
                            wheels_dir: Optional[str | Path],
                            weights_dir: Optional[str | Path],
                            force_clean: bool) -> None:
        """Execute the full setup workflow immediately with the provided options."""
        if self.setup_running:
            self.log_sys("Startup setup skipped: another setup task is already running.", warn=True)
            return
        settings = self.save_settings()
        if not wsl_ok():
            self.log_sys("WSL not available. Automatic setup cannot continue.", warn=True)
            return
        dlg = SetupDialog(self)
        worker = SetupWorker(
            settings["wsl_repo"],
            settings["wsl_venv"],
            online=online,
            cuda_label=cuda_label,
            wheels_dir=self._normalize_optional_path(wheels_dir),
            weights_dir=self._normalize_optional_path(weights_dir),
            force_clean=force_clean,
        )
        self.setup_worker = worker
        self.set_setup_busy(True)
        worker.progress.connect(lambda p, m: (dlg.pbar.setValue(p), dlg.label.setText(m)))
        worker.line.connect(lambda ln: (dlg.append(ln), self.log_sys(ln)))

        def on_finish(ok: bool):
            dlg.closeBtn.setEnabled(True)
            dlg.cancelBtn.setEnabled(False)
            self.set_setup_busy(False)
            dlg.label.setText("Setup complete." if ok else "Setup failed.")
            self.setup_worker = None
            if not ok:
                self.log_sys("Automatic setup failed. Use the Setup panel to retry.", warn=True)
            self.run_diagnostics(silent=True)

        worker.finished_ok.connect(on_finish)
        dlg.cancelBtn.clicked.connect(worker.cancel)
        dlg.closeBtn.clicked.connect(dlg.accept)
        self.log_sys("== Setup: Automatic Create/Repair (startup) ==")
        worker.start()
        dlg.exec()

    def full_setup_dialog(self):
        if self.setup_running: return
        s = self.save_settings()
        online = self.onlineCheck.isChecked()
        cuda_label = self.cudaCombo.currentText().split()[0]
        wheels_dir = self._normalize_optional_path(self.wheelsEdit.text())
        weights_dir = self._normalize_optional_path(self.weightsEdit.text())
        force_clean = self.forceClean.isChecked()
        if not wsl_ok():
            QtWidgets.QMessageBox.critical(self, "WSL", "WSL is not available.")
            self.log_sys("WSL not available.", warn=True); return
        dlg = SetupDialog(self)
        worker = SetupWorker(s["wsl_repo"], s["wsl_venv"], online=online, cuda_label=cuda_label,
                             wheels_dir=wheels_dir, weights_dir=weights_dir, force_clean=force_clean)
        self.setup_worker = worker; self.set_setup_busy(True)
        worker.progress.connect(lambda p, m: (dlg.pbar.setValue(p), dlg.label.setText(m)))
        worker.line.connect(lambda ln: (dlg.append(ln), self.log_sys(ln)))
        def on_finish(ok: bool):
            dlg.closeBtn.setEnabled(True); dlg.cancelBtn.setEnabled(False)
            self.set_setup_busy(False)
            dlg.label.setText("Setup complete." if ok else "Setup failed.")
            self.setup_worker = None; self.run_diagnostics(silent=True)
        worker.finished_ok.connect(on_finish)
        dlg.cancelBtn.clicked.connect(worker.cancel); dlg.closeBtn.clicked.connect(dlg.accept)
        self.log_sys("== Setup: Create/Repair (repo, venv, torch, deps, weights) ==")
        worker.start(); dlg.exec()

    def install_requirements_only_dialog(self):
        if self.setup_running: return
        s = self.save_settings()
        online = self.onlineCheck.isChecked()
        cuda_label = self.cudaCombo.currentText().split()[0]
        wheels_dir = Path(self.wheelsEdit.text().strip()) if self.wheelsEdit.text().strip() else (BASE_DIR / "wheels")
        venv_act = s["wsl_venv"]
        venv_path = Path(venv_act)
        venv_dir = str(venv_path.parent.parent if len(venv_path.parents) >= 2 else venv_path.parent)
        venv_exists = self.wsl_exists(venv_act) or self.wsl_exists(venv_dir)
        if not (self.wsl_exists(s["wsl_repo"]) and venv_exists):
            QtWidgets.QMessageBox.warning(self, "Missing", "Repo or venv missing. Use Full setup.")
            return
        dlg = SetupDialog(self)
        def stream(ln): dlg.append(ln); self.log_sys(ln)
        dlg.label.setText("Installing requirements…"); dlg.pbar.setValue(10); dlg.show(); QtWidgets.QApplication.processEvents()
        self.set_setup_busy(True)
        ok = install_deps_wsl(s["wsl_repo"], s["wsl_venv"], online=online, cuda_label=cuda_label,
                              wheels_dir_win=wheels_dir, stream=stream)
        dlg.pbar.setValue(100 if ok else 0); dlg.label.setText("Done" if ok else "Failed")
        self.set_setup_busy(False); self.run_diagnostics(silent=True)

    # ----- terminal -----
    def open_wsl_terminal(self):
        s = self.save_settings()
        repo = s["wsl_repo"]; venv = s["wsl_venv"]
        bootstrap = f'cd {bashify(repo)} && source {bashify(venv)} && exec bash'
        wt = self.which("wt.exe")
        try:
            if wt: subprocess.Popen([wt, "-w", "0", "wsl.exe", "-e", "bash", "-lc", bootstrap])
            else:  subprocess.Popen(["wsl.exe", "-e", "bash", "-lc", bootstrap])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Terminal error", repr(e))

    # ----- inference -----
    def build_infer_cmd(self, repo: str, venv: str, preset: str, prompt: str,
                        seed: Optional[int], offload: bool, hf_offline: bool) -> str:
        cfg = "configs/diffusion/inference/t2i2v_256px.py" if preset.startswith("256") else "configs/diffusion/inference/t2i2v_768px.py"
        offline_flag = (WSL_HF_OFFLINE_EXPORT if hf_offline else "")
        outputs_dir = repo_outputs_dir(repo)
        cmd = (
            f"cd {bashify(repo)} && source {bashify(venv)} && "
            f"{WSL_CACHE_EXPORT}{WSL_PRIVACY_EXPORT}{offline_flag}"
            "python -m torch.distributed.run --nproc_per_node 1 --standalone "
            f"scripts/diffusion/inference.py {cfg} --save-dir {bashify(outputs_dir)} --prompt {shlex.quote(prompt)}"
        )
        if offload: cmd += " --offload True"
        if seed is not None: cmd += f" --seed {int(seed)}"
        return cmd

    def start_job(self):
        if self.proc is not None and self.proc.poll() is None:
            QtWidgets.QMessageBox.warning(self, "Busy", "A job is already running."); return
        s = self.save_settings()
        repo = s["wsl_repo"]; venv = s["wsl_venv"]
        if not self.wsl_exists(repo) or not self.wsl_exists(venv):
            QtWidgets.QMessageBox.critical(self, "Missing", "WSL repo or venv not found. Run Setup."); return
        rc, out = wsl_run(f"cd {bashify(repo)} && [ -d ckpts ] && find ckpts -type f -maxdepth 3 | head -n 1 | wc -l || echo 0", timeout=10)
        if int((out or "0").strip() or 0) == 0:
            QtWidgets.QMessageBox.warning(self, "Weights", "No weights found in ckpts/. Add weights (offline) or run Setup with Online checked.")
        prompt = self.promptEdit.text().strip()
        if not prompt:
            QtWidgets.QMessageBox.warning(self, "Prompt", "Please enter a prompt."); return
        seed = int(self.seedEdit.text()) if self.seedEdit.text().strip().isdigit() else None
        cmd = self.build_infer_cmd(repo, venv, self.preset.currentText(), prompt, seed, self.offload.isChecked(), self.hfOffline.isChecked())
        self.log_job("Command:"); self.log_job(cmd)
        self.proc = subprocess.Popen(["wsl.exe", "-e", "bash", "-lc", cmd],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, text=True, bufsize=1)
        self.reader = StreamProc(self.proc); self.reader.line.connect(self.log_job); self.reader.done.connect(self.job_finished); self.reader.start()
        self.startBtn.setEnabled(False); self.stopBtn.setEnabled(True)

    def job_finished(self, code: int):
        self.log_job(f"Process exited with code {code}.")
        self.proc = None; self.reader = None
        self.startBtn.setEnabled(True); self.stopBtn.setEnabled(False)
        self.pull_outputs(); self.refresh_videos()

    def stop_job(self):
        if self.proc is None or self.proc.poll() is not None:
            QtWidgets.QMessageBox.information(self, "Idle", "No job is running."); return
        self.log_job("Stopping…")
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.proc.pid)], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            wsl_run("pkill -f scripts/diffusion/inference.py || true", timeout=6)
        except Exception as e:
            self.log_job(f"Stop error: {e!r}")
        finally:
            self.proc = None; self.reader = None
            self.startBtn.setEnabled(True); self.stopBtn.setEnabled(False)

    # ----- videos -----
    def pull_outputs(self):
        repo = self.repoEdit.text().strip() or DEFAULT_WSL_REPO
        if repo.startswith("~"):
            repo = repo.replace("~", DEFAULT_WSL_HOME_VAR, 1)
        src = repo_outputs_dir(repo)
        dst = win_to_wsl_path(OUT_DIR_WIN)
        wsl_run(f"mkdir -p {bashify(src)} {dst} && cp -n {bashify(src)}/*.mp4 {dst} 2>/dev/null || true", timeout=60)
        self.log_sys("Pulled videos from repo → Windows outputs/")
    def refresh_videos(self):
        self.pull_outputs()
        self.listView.clear()
        for p in sorted(OUT_DIR_WIN.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)[:300]:
            it = QtWidgets.QListWidgetItem(p.name); it.setData(Qt.ItemDataRole.UserRole, str(p))
            self.listView.addItem(it)
    def play_selected(self):
        items = self.listView.selectedItems()
        if not items: return
        p = Path(items[0].data(Qt.ItemDataRole.UserRole))
        if p.exists():
            self.player.setSource(QUrl.fromLocalFile(str(p))); self.player.play()
    def open_external_video(self):
        items = self.listView.selectedItems()
        if not items:
            QtWidgets.QMessageBox.information(self, "Open", "Select a video first."); return
        p = Path(items[0].data(Qt.ItemDataRole.UserRole))
        if p.exists():
            try: os.startfile(str(p))
            except Exception as e: QtWidgets.QMessageBox.critical(self, "Open", repr(e))

    # ----- misc -----
    def which(self, name: str) -> Optional[str]:
        for path in os.environ.get("PATH","").split(os.pathsep):
            cand = Path(path)/name
            if cand.exists(): return str(cand)
        return None

# ---------- App bootstrap ----------
def main():
    from PyQt6 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Open-Sora All-in-One (PyQt6)")
    win = Window()
    app.setStyleSheet(app.styleSheet() + " QSplitter::handle { width: 10px; } ")
    win.show()
    try:
        sys.exit(app.exec())
    except Exception as e:
        CRASH_LOG.write_text(f"FATAL: {repr(e)}\n", encoding="utf-8")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FATAL: {e!r}", file=sys.stderr)
        try: os.startfile(str(CRASH_LOG))
        except Exception: pass
        raise
```

Open-Sora All-in-One (PyQt6, Windows host + WSL backend)
=========================================================
Desktop app that **SETS UP** Open-Sora (online-first setup, offline afterwards), **GENERATES** videos, and **PREVIEWS** them.
Everything stays inside this project folder. Live progress, single installer run, clear errors.

CONTRAST RULE (MANDATORY): high-contrast text vs background (dark UI, light text). No low-contrast combos.

Windows-side folders:
  logs/       -> server + job logs + crash logs
  runtime/    -> app-only temp files (no system TMP)
  outputs/    -> mirrored from WSL $REPO/outputs for in-app playback
  wheels/     -> (optional) local wheels for offline setup
  weights/    -> (optional) weights/Open-Sora-v2 or ckpts/ for offline
  repo_cache/Open-Sora -> (optional) offline repo snapshot

WSL-side layout:
  $HOME/Local video Generator/Open-Sora     (repo)
  $HOME/Local video Generator/.venv         (venv dir)
  $REPO/.cache/*                            (HF/transformers caches inside repo)
  $REPO/outputs                             (generation results)

Privacy:
  WANDB + HF hub telemetry disabled by env vars. Optional HF offline mode for generation.

Order of operations (on Setup):
  1) Check WSL
  2) Optionally Clean (delete repo & venv) for a fresh install
  3) Clone/Stage repo (online or from repo_cache)
  4) Install APT prereqs (root; non-interactive): python3-venv, python3-virtualenv, python3-pip, git, build-essential, ca-certificates, curl, ffmpeg
  5) Create venv (python3.12/3 fallback; if ensurepip missing -> bootstrap pip via get-pip.py; else virtualenv fallback)
  6) Install torch/vision & requirements (+ xformers/flash-attn best-effort)
  7) Stage weights (online huggingface-cli or offline copy)
  8) Verify imports & list weights
**Classes:** StreamProc, SetupWorker, SetupDialog, Window
**Functions:** repo_outputs_dir(repo), _stamp(), log_line(msg), wsl_ok(), wsl_run(cmd, timeout), wsl_stream(cmd, line_cb, end_cb), wsl_run_root(cmd, timeout), wsl_stream_root(cmd, line_cb, end_cb), bashify(path_like), win_to_wsl_path(p), wsl_file_exists(path_like), choose_pytorch_index_cuda_label(auto_or_label), ensure_wsl_root(), ensure_linux_prereqs(online, stream), maybe_force_clean(force, stream, repo, venv_dir), clone_or_stage_repo_wsl(repo), _venv_ok(venv_dir), _pip_ok(venv_dir), create_or_reuse_venv_wsl(venv_dir, online, stream), pip_install_wsl_stream(venv_act, args), install_deps_wsl(repo, venv_act), stage_weights_wsl(repo), main()


## Module `tools\codex_pr_sentinel.py`

```python
"""Codex PR Sentinel

This script performs lightweight validation for pull requests using
configuration rules defined in `.github/codex_sentinel.yml`.

The utility is intentionally dependency-light so that it can run inside
GitHub Actions without extra packages. It supports two rule types:

* ``body_contains`` – ensure the pull request body includes a required
  substring (case sensitive).
* ``file_modified`` – check whether a file appears in the diff between the
  PR head commit and the base branch. This is useful for verifying that a
  changelog update accompanies substantive changes.

The script exits with a non-zero status if any required rule fails.
Optional rules will emit warnings but do not fail the check.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


@dataclass
class RuleResult:
    """Represents the outcome of a sentinel rule evaluation."""

    name: str
    description: str
    success: bool
    required: bool
    message: str

    def as_log(self) -> str:
        status = "PASS" if self.success else ("WARN" if not self.required else "FAIL")
        return f"[{status}] {self.name}: {self.message}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate pull requests using Codex sentinel rules.")
    parser.add_argument("--event-path", required=True, help="Path to the GitHub event payload JSON file.")
    parser.add_argument("--config", required=True, help="Path to the sentinel configuration file (YAML or JSON).")
    return parser.parse_args()


def load_event(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise SystemExit(f"Event file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in event file {path}: {exc}") from exc


def load_config(path: Path) -> Dict[str, Any]:
    text = path.read_text()
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text) or {}
    except ModuleNotFoundError:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return _parse_minimal_yaml(text)


def _parse_minimal_yaml(text: str) -> Dict[str, Any]:
    """Parse a restricted subset of YAML used by the sentinel config."""

    lines = [line.rstrip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    index = 0

    def parse_block(indent: int = 0) -> Any:
        nonlocal index
        mapping: Dict[str, Any] = {}
        while index < len(lines):
            line = lines[index]
            current_indent = len(line) - len(line.lstrip(" "))
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ValueError("Invalid indentation in minimal YAML parser")
            stripped = line.strip()
            if stripped.startswith("- "):
                if not mapping:
                    raise ValueError("List item defined before key in minimal YAML parser")
                key = next(reversed(mapping))
                if not isinstance(mapping[key], list):
                    mapping[key] = []
                sequence = mapping[key]
                item_line = stripped[2:].strip()
                index += 1
                if item_line:
                    if ":" in item_line:
                        key_name, _, remainder = item_line.partition(":")
                        remainder = remainder.strip()
                        if remainder:
                            sequence.append({key_name.strip(): _convert_scalar(remainder)})
                        else:
                            nested = parse_block(indent + 2)
                            sequence.append({key_name.strip(): nested})
                    else:
                        sequence.append(_convert_scalar(item_line))
                else:
                    sequence.append(parse_block(indent + 2))
                continue
            key, _, remainder = stripped.partition(":")
            key = key.strip()
            remainder = remainder.strip()
            index += 1
            if remainder:
                mapping[key] = _convert_scalar(remainder)
            else:
                if index < len(lines) and (len(lines[index]) - len(lines[index].lstrip(" "))) > indent:
                    mapping[key] = parse_block(indent + 2)
                else:
                    mapping[key] = {}
        return mapping

    index = 0
    return parse_block(0)


def _convert_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value.strip('"')


def evaluate_rules(config: Dict[str, Any], event: Dict[str, Any]) -> List[RuleResult]:
    rules: Sequence[Dict[str, Any]] = config.get("review_rules", []) or []
    pr = event.get("pull_request") or {}
    body = pr.get("body", "") or ""
    results: List[RuleResult] = []

    diff_files: Optional[Sequence[str]] = None
    for rule in rules:
        name = rule.get("name", "Unnamed Rule")
        description = rule.get("description", "")
        rule_checks = rule.get("checks", []) or []
        required = bool(rule.get("required", True))
        for check in rule_checks:
            check_type = check.get("type")
            if check_type == "body_contains":
                pattern = check.get("pattern", "")
                success = pattern in body
                message = "Pattern present in PR body" if success else f"Missing required pattern '{pattern}' in PR body"
                results.append(RuleResult(name, description, success, True, message))
            elif check_type == "file_modified":
                path = check.get("path")
                if diff_files is None:
                    diff_files = list(collect_diff_files(pr) or [])
                success = path in diff_files if diff_files is not None else False
                required_flag = bool(check.get("required", check.get("required", required)))
                if diff_files is None:
                    message = "Unable to determine diff files"
                elif success:
                    message = f"Detected changes to {path}"
                else:
                    message = f"No changes detected for {path}"
                results.append(RuleResult(name, description, success, required_flag, message))
            else:
                results.append(
                    RuleResult(
                        name,
                        description,
                        True,
                        False,
                        f"Unsupported check type '{check_type}' skipped",
                    )
                )
    return results


def collect_diff_files(pr: Dict[str, Any]) -> Optional[Iterable[str]]:
    base_ref = pr.get("base", {}).get("ref")
    if not base_ref:
        return None

    try:
        subprocess.run(["git", "fetch", "origin", base_ref, "--depth", "0"], check=False, capture_output=True)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Warning: unable to fetch base ref {base_ref}: {exc}", file=sys.stderr)

    diff_cmd = ["git", "diff", f"origin/{base_ref}...HEAD", "--name-only"]
    try:
        completed = subprocess.run(diff_cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        print(f"Warning: git diff failed: {exc}", file=sys.stderr)
        return None

    files = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return files


def main() -> None:
    args = parse_args()
    event = load_event(Path(args.event_path))
    config = load_config(Path(args.config))
    results = evaluate_rules(config, event)

    has_failure = False
    for result in results:
        log_line = result.as_log()
        if result.success:
            print(log_line)
        elif result.required:
            has_failure = True
            print(log_line, file=sys.stderr)
        else:
            print(log_line, file=sys.stderr)

    if has_failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

Codex PR Sentinel

This script performs lightweight validation for pull requests using
configuration rules defined in `.github/codex_sentinel.yml`.

The utility is intentionally dependency-light so that it can run inside
GitHub Actions without extra packages. It supports two rule types:

* ``body_contains`` – ensure the pull request body includes a required
  substring (case sensitive).
* ``file_modified`` – check whether a file appears in the diff between the
  PR head commit and the base branch. This is useful for verifying that a
  changelog update accompanies substantive changes.

The script exits with a non-zero status if any required rule fails.
Optional rules will emit warnings but do not fail the check.
**Classes:** RuleResult
**Functions:** parse_args(), load_event(path), load_config(path), _parse_minimal_yaml(text), _convert_scalar(value), evaluate_rules(config, event), collect_diff_files(pr), main()


## Module `tools\logic_inbox.py`

```python
"""Command-line interface for managing the Codex logic inbox."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_INBOX_PATH = Path("memory/logic_inbox.jsonl")


@dataclass
class InboxItem:
    """Represents a single inbox task."""

    identifier: str
    title: str
    details: str
    status: str = "open"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)

    @staticmethod
    def from_json(line: str) -> "InboxItem":
        data = json.loads(line)
        return InboxItem(**data)


class Inbox:
    """Simple JSONL-backed inbox for autonomous task tracking."""

    def __init__(self, path: Path = DEFAULT_INBOX_PATH):
        self.path = path
        self.items: List[InboxItem] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()
            return
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                self.items.append(InboxItem.from_json(line))

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            for item in self.items:
                handle.write(item.to_json() + "\n")

    def add(self, title: str, details: str) -> InboxItem:
        identifier = f"task-{len(self.items) + 1:04d}"
        item = InboxItem(identifier=identifier, title=title, details=details)
        self.items.append(item)
        self.save()
        return item

    def list(self, include_resolved: bool = False) -> List[InboxItem]:
        if include_resolved:
            return list(self.items)
        return [item for item in self.items if item.status != "resolved"]

    def resolve(self, identifier: str) -> InboxItem:
        for item in self.items:
            if item.identifier == identifier:
                item.status = "resolved"
                item.resolved_at = datetime.now(timezone.utc).isoformat()
                self.save()
                return item
        raise SystemExit(f"No inbox item found with id {identifier}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the Codex logic inbox JSONL file.")
    parser.add_argument("--path", type=Path, default=DEFAULT_INBOX_PATH, help="Path to the inbox JSONL file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new inbox item.")
    add_parser.add_argument("title", help="Short title for the task.")
    add_parser.add_argument("details", help="Detailed description of the task.")

    list_parser = subparsers.add_parser("list", help="List inbox items.")
    list_parser.add_argument("--all", action="store_true", help="Include resolved items.")

    resolve_parser = subparsers.add_parser("resolve", help="Mark an inbox item as resolved.")
    resolve_parser.add_argument("identifier", help="Identifier of the task to resolve (e.g., task-0001).")

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    inbox = Inbox(path=args.path)

    if args.command == "add":
        item = inbox.add(args.title, args.details)
        print(f"Added {item.identifier}: {item.title}")
    elif args.command == "list":
        items = inbox.list(include_resolved=args.all)
        if not items:
            print("No inbox items found.")
            return
        for item in items:
            status = item.status.upper()
            print(f"{item.identifier} [{status}] {item.title} :: {item.details}")
    elif args.command == "resolve":
        item = inbox.resolve(args.identifier)
        print(f"Resolved {item.identifier}: {item.title}")
    else:
        parser.error("Unsupported command")


def run() -> None:
    """Entry point used for console_scripts compatibility."""

    main()


if __name__ == "__main__":
    main()
```

Command-line interface for managing the Codex logic inbox.
**Classes:** InboxItem, Inbox
**Functions:** build_parser(), main(argv), run()



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