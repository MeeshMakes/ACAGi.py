#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtual_Desktop.py — Windows-style virtual desktop (contained), with Start panel and card window controls.

Directives satisfied:
- All former top toolbar actions moved into Start panel and Settings; no floating top bar.
- Start menu is a docked panel that rises from the taskbar and stays attached to the bottom.
- Window has standard minimize, maximize, close in the top-right (Qt title bar). Starts maximized with border.
- Each Card has its own Minimize, Max/Restore, Close buttons. Minimize hides to taskbar, restore via task button.
- Desktop edge trim removed. Background is clean blue gradient. High contrast enforced for text vs background.
- No drag-out to OS. No file URL clipboard exports. All dialogs non-native and modal to keep containment.
- Explorer and desktop icons support rename with extensions. Type/extension changes reflect immediately.
- Visual refreshes are immediate after file ops. QFileSystemWatcher also keeps UI current.
- Codex_Terminal.py can be launched from Start ▸ Apps ▸ Codex Terminal as an embedded card (factory supports embedded=True).  # See note re: citation in chat.

Notes:
- Contrast rule: inline comments and palettes ensure readable foreground/background in all states.
- Start panel includes: Apps (Explorer, Codex Terminal, Template Terminal), Recent, Settings, Power menu, Search.
- Settings panel collects previous toolbar utilities and view toggles.
"""

from __future__ import annotations

import os, sys, json, time, math, threading, subprocess, importlib.util, argparse, logging, traceback, ctypes, shutil, inspect, socket, difflib, zipfile, base64, binascii, weakref
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple, Callable, TYPE_CHECKING, Union, Sequence, Mapping, Iterable, Any, cast
from pathlib import Path

from PySide6.QtCore import (
    Qt, QPoint, QRect, QRectF, QSize, QEvent, QTimer, Signal, Slot, QUrl, QMimeData,
    QFileSystemWatcher, QDateTime, QDir, QFileInfo, QBuffer, QIODevice, QObject
)
try:  # Optional pointer helper (missing in some PySide6 builds)
    from PySide6.QtCore import QPointer as _QtQPointer  # type: ignore
except ImportError:  # pragma: no cover - fallback path when QPointer absent
    _QtQPointer = None  # type: ignore
from PySide6.QtGui import (
    QColor, QGuiApplication, QPainter, QPainterPath, QLinearGradient, QPalette,
    QAction, QKeySequence, QClipboard, QCursor, QIcon, QPixmap, QFont, QResizeEvent,
    QWindowStateChangeEvent, QDrag, QMouseEvent, QFontMetrics,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QScrollArea, QFrame, QLabel, QVBoxLayout,
    QHBoxLayout, QBoxLayout, QSizeGrip, QPushButton, QGraphicsDropShadowEffect, QMenuBar,
    QFileDialog, QPlainTextEdit, QMenu, QListWidget, QListWidgetItem, QStyle, QToolButton,
    QMessageBox, QInputDialog, QLineEdit, QDialog, QSplitter, QTextBrowser, QComboBox, QCheckBox,
    QGridLayout, QSizePolicy, QLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QDoubleSpinBox, QSpinBox, QFileIconProvider
)

try:
    import shiboken6  # type: ignore
except Exception:  # pragma: no cover - shiboken may be unavailable in some environments
    shiboken6 = None  # type: ignore

try:  # Optional Windows helpers for native icon conversion
    from PySide6.QtWinExtras import QtWin  # type: ignore
except Exception:  # pragma: no cover - QtWinExtras may be unavailable on non-Windows builds
    QtWin = None  # type: ignore

try:  # Optional plotting dependency
    import pyqtgraph as pg  # type: ignore
    from pyqtgraph import BarGraphItem
    from pyqtgraph.graphicsItems.DateAxisItem import DateAxisItem
except Exception:  # pragma: no cover - optional dependency may be unavailable
    pg = None
    BarGraphItem = None
    DateAxisItem = None

from error_center import ErrorCenterCard
from errors import ProcessErrorCard
from background import (
    BackgroundConfig,
    BackgroundFit,
    BackgroundManager,
    BackgroundMode,
    GifBg,
    GLViewportBg,
    StaticImageBg,
    VideoBg,
)
from metrics_manager import fetch_metrics
from tools.system_metrics import collect_metrics
from external_app_card import (
    ExternalAppCard,
    LaunchSpec,
    build_launch_spec,
    should_embed_external_app,
)

try:  # Optional User-Guided Notes card factory
    import User_Guided_Notes as _user_guided_notes_module  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _user_guided_notes_module = None
    _USER_GUIDED_NOTES_FACTORY = None
    _USER_GUIDED_NOTES_WINDOW_CLASS = None
    _USER_GUIDED_NOTES_WIDGET_CLASS = None
else:
    _USER_GUIDED_NOTES_FACTORY = getattr(_user_guided_notes_module, "build_widget", None)
    if not callable(_USER_GUIDED_NOTES_FACTORY):
        _USER_GUIDED_NOTES_FACTORY = getattr(_user_guided_notes_module, "create_card", None)
    if not callable(_USER_GUIDED_NOTES_FACTORY):
        _USER_GUIDED_NOTES_FACTORY = None
    _USER_GUIDED_NOTES_WINDOW_CLASS = getattr(_user_guided_notes_module, "UserGuidedNotesWindow", None)
    _USER_GUIDED_NOTES_WIDGET_CLASS = getattr(_user_guided_notes_module, "UserGuidedNotesWidget", None)

try:  # Optional task bus (absent when tasks module unavailable)
    from tasks.bus import subscribe as bus_subscribe, Subscription as BusSubscription  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    bus_subscribe = None
    BusSubscription = None  # type: ignore

# --------------------------------------------------------------------------------------
# Paths, logging & state
# --------------------------------------------------------------------------------------
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
STATE_PATH = os.path.join(SCRIPT_DIR, "vd_state.json")
LOG_PATH = os.path.join(SCRIPT_DIR, "vd_system.log")
WORKSPACE_ROOT = os.environ.get("CODEX_WORKSPACE")
VDSK_ROOT = WORKSPACE_ROOT or os.path.join(SCRIPT_DIR, "Virtual_Desktop")
os.makedirs(VDSK_ROOT, exist_ok=True)

def workspace_root() -> str:
    return VDSK_ROOT

def _is_contained(path: str) -> bool:
    root = Path(VDSK_ROOT).resolve()
    try:
        resolved = Path(path).resolve()
    except Exception:
        return False
    return resolved == root or root in resolved.parents

def _safe_resolve(path_str: Optional[str]) -> Optional[str]:
    if not path_str:
        return None
    cleaned = path_str.strip().strip('"')
    if not cleaned:
        return None
    try:
        path = Path(cleaned).expanduser()
        if not path.exists():
            return None
        return str(path.resolve())
    except Exception:
        return None

def _build_allowlist() -> set[str]:
    entries: set[str] = set()
    for candidate in (
        sys.executable,
        os.environ.get("COMSPEC"),
        os.environ.get("SHELL"),
        shutil.which("python"),
        shutil.which("python3"),
        shutil.which("cmd"),
        shutil.which("cmd.exe"),
        shutil.which("powershell"),
        shutil.which("powershell.exe"),
        shutil.which("pwsh"),
        shutil.which("bash"),
        shutil.which("sh"),
    ):
        resolved = _safe_resolve(candidate)
        if resolved:
            entries.add(resolved)
    return entries

ALLOWLIST: set[str] = _build_allowlist()

BASE_CARD_WIDTH = 1100
BASE_CARD_HEIGHT = 700
MIN_CARD_WIDTH = 520
MIN_CARD_HEIGHT = 360
CARD_SCALE_MIN = 0.6
CARD_SCALE_MAX = 1.6


def _make_card_pointer(card: "Card") -> Callable[[], Optional["Card"]]:
    """Return a callable that resolves the card while guarding against GC."""
    if _QtQPointer is not None:
        pointer = _QtQPointer(card)

        def _resolve() -> Optional["Card"]:
            try:
                return cast(Optional["Card"], pointer.data())
            except Exception:
                return None

        return _resolve

    ref = weakref.ref(card)

    def _resolve() -> Optional["Card"]:
        try:
            return cast(Optional["Card"], ref())
        except Exception:
            return None

    return _resolve


def _is_card_valid(card: Optional["Card"]) -> bool:
    if card is None:
        return False
    if shiboken6 is None:  # pragma: no cover - shiboken unavailable
        return True
    try:
        return bool(shiboken6.isValid(card))
    except Exception:  # pragma: no cover - defensive fallback
        return False


def _make_guarded_card_method(
    card: "Card",
    method: Union[str, Callable[["Card"], Any]],
    *args: object,
    **kwargs: object,
) -> Callable[[], bool]:
    """Create a callable that safely invokes ``method`` on ``card``.

    The returned function resolves the card via :func:`_make_card_pointer` to
    avoid holding a strong reference. It then checks the pointer with
    :func:`_is_card_valid` (which in turn uses ``shiboken6.isValid`` when
    available) before invoking the requested method. The callable returns
    ``True`` when the method was executed, ``False`` otherwise.
    """

    resolve_card = _make_card_pointer(card)
    method_name: Optional[str]
    method_ref: Optional[Callable[["Card"], Any]]
    if isinstance(method, str):
        method_name = method
        method_ref = None
    else:
        method_name = None
        method_ref = method

    def _invoke() -> bool:
        target = resolve_card()
        if target is None:
            return False
        card_obj = cast("Card", target)
        if not _is_card_valid(card_obj):
            return False
        try:
            if method_name is not None:
                bound = getattr(card_obj, method_name, None)
                if not callable(bound):
                    return False
                bound(*args, **kwargs)
            else:
                assert method_ref is not None
                method_ref(card_obj, *args, **kwargs)
        except (RuntimeError, ReferenceError):  # pragma: no cover - Qt GC race
            return False
        return True

    return _invoke

START_PANEL_AUTO_DELAY_MIN_MS = 500
START_PANEL_AUTO_DELAY_MAX_MS = 15000
DEFAULT_START_PANEL_AUTO_DELAY_MS = 2000
START_PANEL_CLOSE_DEFAULT = {
    "mode": "click",
    "auto_delay_ms": DEFAULT_START_PANEL_AUTO_DELAY_MS,
}

# Desktop icon grid offsets (align manual drags with auto arrange)
GRID_ORIGIN_X = 30
GRID_ORIGIN_Y = 40

_FILE_ICON_PROVIDER: Optional["QFileIconProvider"]
try:
    _FILE_ICON_PROVIDER = QFileIconProvider()
except Exception:  # pragma: no cover - provider may be unavailable in headless environments
    _FILE_ICON_PROVIDER = None

_ICON_DRAG_MIME = "application/x-codex-virtual-desktop-icon"
_ICON_OFFSET_MIME = "application/x-codex-virtual-desktop-icon-offset"

if sys.platform.startswith("win"):
    from ctypes import wintypes  # type: ignore

    class _SHFILEINFOW(ctypes.Structure):  # pragma: no cover - Windows specific helper
        _fields_ = [
            ("hIcon", wintypes.HICON),
            ("iIcon", ctypes.c_int),
            ("dwAttributes", wintypes.DWORD),
            ("szDisplayName", ctypes.c_wchar * 260),
            ("szTypeName", ctypes.c_wchar * 80),
        ]

    _SHGFI_ICON = 0x000000100
    _SHGFI_LARGEICON = 0x000000000
    _SHGFI_SMALLICON = 0x000000001

    def _try_shell_icon(path: Path, large: bool = True) -> Optional[QIcon]:
        if QtWin is None:
            return None
        info = _SHFILEINFOW()
        flags = _SHGFI_ICON | (_SHGFI_LARGEICON if large else _SHGFI_SMALLICON)
        try:
            result = ctypes.windll.shell32.SHGetFileInfoW(  # type: ignore[attr-defined]
                str(path),
                0,
                ctypes.byref(info),
                ctypes.sizeof(info),
                flags,
            )
        except Exception:
            return None
        if not result or not info.hIcon:
            return None
        try:
            pixmap = QtWin.fromHICON(info.hIcon)  # type: ignore[attr-defined]
            if pixmap and not pixmap.isNull():
                return QIcon(pixmap)
        finally:
            try:
                ctypes.windll.user32.DestroyIcon(info.hIcon)  # type: ignore[attr-defined]
            except Exception:
                pass
        return None
else:

    def _try_shell_icon(path: Path, large: bool = True) -> Optional[QIcon]:  # pragma: no cover - non-Windows stub
        return None


def _try_provider_icon(path: Path) -> Optional[QIcon]:
    provider = _FILE_ICON_PROVIDER
    if not provider:
        return None
    try:
        info = QFileInfo(str(path))
        icon = provider.icon(info)
    except Exception:
        return None
    if icon and not icon.isNull():
        return icon
    return None


def _fallback_icon_for_path(path: Path) -> QIcon:
    style = QApplication.style()
    if path.exists() and path.is_dir():
        return style.standardIcon(QStyle.SP_DirIcon)
    ext = path.suffix.lower()
    if ext in {".txt", ".md", ".log", ".ini", ".cfg", ".json"}:
        return QIcon.fromTheme("text-x-generic") or style.standardIcon(QStyle.SP_FileIcon)
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}:
        return QIcon.fromTheme("image-x-generic") or style.standardIcon(QStyle.SP_FileIcon)
    if ext == ".py":
        return QIcon.fromTheme("text-x-python") or style.standardIcon(QStyle.SP_FileIcon)
    return style.standardIcon(QStyle.SP_FileIcon)


def _icon_for_path(path_like: os.PathLike[str] | str) -> Tuple[QIcon, bool]:
    path = Path(path_like)
    native = False
    icon: Optional[QIcon] = None
    if path.exists():
        icon = _try_provider_icon(path)
        if icon and not icon.isNull():
            native = True
        else:
            shell_icon = _try_shell_icon(path)
            if shell_icon and not shell_icon.isNull():
                icon = shell_icon
                native = True
    if not icon or icon.isNull():
        icon = _fallback_icon_for_path(path)
        native = False
    return icon, native


_ICON_FOR_PATH_HELPER = _icon_for_path


def _clear_native_icon_caches() -> None:
    global _FILE_ICON_PROVIDER
    try:
        provider_type = QFileIconProvider
    except NameError:
        return
    if provider_type is None:
        return
    try:
        _FILE_ICON_PROVIDER = provider_type()
    except Exception:
        _FILE_ICON_PROVIDER = None

def _resolve_executable_path(cmd: List[str], cwd: Optional[str]) -> Optional[str]:
    if not cmd:
        return None
    first = cmd[0]
    resolved = _safe_resolve(first) if os.path.isabs(first) else None
    if resolved:
        return resolved
    search_path = None
    if cwd:
        try:
            candidate = Path(cwd).joinpath(first)
            candidate_resolved = candidate.resolve()
            if candidate_resolved.exists():
                return str(candidate_resolved)
        except Exception:
            pass
        try:
            resolved_cwd = Path(cwd).resolve()
            if resolved_cwd.exists():
                search_path = str(resolved_cwd)
        except Exception:
            search_path = None
    if search_path:
        located = shutil.which(first, path=search_path)
        if located:
            resolved = _safe_resolve(located)
            if resolved:
                return resolved
    located = shutil.which(first)
    if located:
        resolved = _safe_resolve(located)
        if resolved:
            return resolved
    return None

def _validate_process_request(
    cmd: List[str],
    cwd: Optional[str],
    allow_external: bool = False,
) -> Tuple[bool, str]:
    if not cmd:
        return False, "Blocked: no command specified."
    resolved_cwd = os.path.abspath(cwd or VDSK_ROOT)
    if not os.path.isdir(resolved_cwd):
        return False, f"Blocked: working directory does not exist ({resolved_cwd})."
    if not _is_contained(resolved_cwd):
        return False, "Blocked: working directory is outside the Virtual Desktop workspace."
    exec_path = _resolve_executable_path(cmd, resolved_cwd)
    if not exec_path:
        return False, "Blocked: executable could not be resolved inside the workspace."
    if _is_contained(exec_path) or exec_path in ALLOWLIST:
        return True, exec_path
    if allow_external:
        return True, exec_path
    name = os.path.basename(exec_path) or exec_path
    return False, f"Blocked: {name} is outside the Virtual Desktop workspace."
    return True, exec_path

LOGGER = logging.getLogger("VirtualDesktop")
LOGGER.setLevel(logging.INFO)
if LOGGER.handlers:
    LOGGER.handlers.clear()
_fh = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
LOGGER.addHandler(_fh)

def log(msg: str, level=logging.INFO):
    LOGGER.log(level, msg)


def _encode_icon(icon: Optional[QIcon], size: QSize = QSize(32, 32)) -> Optional[str]:
    if icon is None or icon.isNull():
        return None
    try:
        pixmap = icon.pixmap(size)
    except Exception:
        return None
    if pixmap.isNull():
        return None
    buffer = QBuffer()
    if not buffer.open(QIODevice.WriteOnly):
        return None
    try:
        if not pixmap.save(buffer, "PNG"):
            return None
        data = bytes(buffer.data())
    finally:
        buffer.close()
    if not data:
        return None
    return base64.b64encode(data).decode("ascii")


def _decode_icon(data: Optional[str]) -> Optional[QIcon]:
    if not data:
        return None
    try:
        raw = base64.b64decode(data)
    except (ValueError, binascii.Error):
        return None
    pixmap = QPixmap()
    if not pixmap.loadFromData(raw, "PNG"):
        return None
    return QIcon(pixmap)


def _icon_for_profile(profile: str) -> QIcon:
    style = QApplication.style()
    mapping = {
        "explorer": QStyle.SP_DirIcon,
        "tasks": QStyle.SP_FileDialogListView,
        "operator-manager": QStyle.SP_DesktopIcon,
        "codex-terminal": QStyle.SP_DesktopIcon,
        "template-terminal": QStyle.SP_ComputerIcon,
        "terminal": QStyle.SP_ComputerIcon,
        "text-viewer": QStyle.SP_FileIcon,
        "image-viewer": QStyle.SP_FileDialogContentsView,
        "error-center": QStyle.SP_MessageBoxCritical,
        "system-overview": QStyle.SP_DesktopIcon,
        "notes": QStyle.SP_FileDialogDetailedView,
        "settings": QStyle.SP_FileDialogDetailedView,
    }
    enum = mapping.get(profile, QStyle.SP_FileIcon)
    return style.standardIcon(enum)

def _load_state() -> Dict:
    if os.path.isfile(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"state load failed: {e}", logging.WARNING)
    # defaults
    return {
        "recent": [],
        "geom": {},
        "icon_pos": {},
        "background": BackgroundConfig().to_state(),
        "icon_size": "medium",
        "desktop_sort": "name",
        "ui_scale": 1.0,
        "taskbar_autohide": False,
        "taskbar_side": "bottom",
        "taskbar_pins": [],
        "allow_external_browse": False,
        "card_scale": 1.0,
        "start_panel_close": dict(START_PANEL_CLOSE_DEFAULT),
    }

def _save_state(state: Dict):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"state save failed: {e}", logging.WARNING)

def _remember_card(kind: str, path: str, title: str):
    st = _load_state()
    st["recent"] = [r for r in st.get("recent", []) if r.get("path") != path or r.get("kind") != kind]
    st["recent"].insert(0, {"kind": kind, "path": path, "title": title, "ts": int(time.time())})
    st["recent"] = st["recent"][:24]
    _save_state(st)

def _geom_key_for(kind: str, persist_tag: str) -> str:
    return f"{kind}:{persist_tag}"


def _rect_to_dict(rect: QRect) -> Dict[str, int]:
    """Convert a QRect into a plain dict with integer coordinates."""
    return {
        "x": int(rect.x()),
        "y": int(rect.y()),
        "width": int(rect.width()),
        "height": int(rect.height()),
    }


def _widget_geometry_snapshot(widget: Optional[QWidget]) -> Dict[str, object]:
    """Return local/global geometry information for automation hooks."""
    if widget is None:
        return {}
    try:
        local = _rect_to_dict(widget.geometry())
    except Exception:
        local = {}
    try:
        top_left = widget.mapToGlobal(QPoint(0, 0))
        global_rect = QRect(top_left, widget.geometry().size())
        global_geom = _rect_to_dict(global_rect)
    except Exception:
        global_geom = dict(local)
    snapshot: Dict[str, object] = {
        "local": local,
        "global": global_geom,
        "visible": bool(widget.isVisible()),
        "objectName": widget.objectName() or "",
    }
    return snapshot


# --------------------------------------------------------------------------------------
# System metrics helpers (pure functions for card + tests)
# --------------------------------------------------------------------------------------
_RECENT_SECONDS = 24 * 3600
_SCORE_BUCKET_LABELS: Dict[str, str] = {
    "healthy": "Healthy (≥0.80)",
    "watch": "Watch (0.50–0.79)",
    "critical": "Critical (<0.50)",
    "unknown": "Unknown",
}
_LAST_RUN_LABELS: Dict[str, str] = {
    "recent": "Ran <24h ago",
    "stale": "Ran ≥24h ago",
    "never": "Never run",
}


def _script_type_label(path: str) -> str:
    if not path:
        return "Unknown"
    norm = str(path).replace("\\", "/")
    if norm.startswith("tests/"):
        return "Tests"
    if norm.startswith("tasks/"):
        return "Tasks"
    if norm.startswith("tools/"):
        return "Tools"
    if norm.endswith("Virtual_Desktop.py"):
        return "Desktop"
    if norm.endswith("Codex_Terminal.py"):
        return "Terminal"
    if norm.endswith(".py"):
        return "Python"
    return "Other"


def _score_from_error_count(error_count: Optional[Any]) -> float:
    try:
        errors = int(error_count or 0)
    except (TypeError, ValueError):
        errors = 0
    if errors <= 0:
        return 1.0
    return 1.0 / (1.0 + float(errors))


def _score_bucket_key(score: Optional[float]) -> str:
    if score is None:
        return "unknown"
    try:
        value = float(score)
    except (TypeError, ValueError):
        return "unknown"
    if value >= 0.8:
        return "healthy"
    if value >= 0.5:
        return "watch"
    return "critical"


def _last_run_bucket(last_run_ts: Optional[Any], *, now: Optional[float] = None) -> str:
    if last_run_ts in (None, ""):
        return "never"
    try:
        ts = float(last_run_ts)
    except (TypeError, ValueError):
        return "never"
    ref = float(now) if now is not None else time.time()
    delta = max(0.0, ref - ts)
    if delta <= _RECENT_SECONDS:
        return "recent"
    return "stale"


def _flatten_metrics_summary(
    summary: Mapping[str, Any] | None,
    *,
    now: Optional[float] = None,
) -> List[Dict[str, Any]]:
    if not summary:
        return []
    components = summary.get("components")
    if not isinstance(components, Mapping):
        return []
    rows: List[Dict[str, Any]] = []
    ref_now = float(now) if now is not None else float(summary.get("generated_at") or time.time())
    for component_name, component_data in components.items():
        if not isinstance(component_data, Mapping):
            continue
        scripts = component_data.get("scripts")
        if not isinstance(scripts, Mapping):
            continue
        for script_path, payload in scripts.items():
            if not isinstance(payload, Mapping):
                continue
            script_type = _script_type_label(str(script_path))
            line_count = payload.get("line_count")
            try:
                lines = int(line_count or 0)
            except (TypeError, ValueError):
                lines = 0
            errors = payload.get("error_count")
            try:
                err_count = int(errors or 0)
            except (TypeError, ValueError):
                err_count = 0
            last_modified = payload.get("last_modified")
            try:
                modified_ts = float(last_modified) if last_modified is not None else None
            except (TypeError, ValueError):
                modified_ts = None
            last_run_ts = payload.get("last_run_ts")
            try:
                last_run = float(last_run_ts) if last_run_ts is not None else None
            except (TypeError, ValueError):
                last_run = None
            score = _score_from_error_count(err_count)
            row = {
                "component": str(component_name),
                "script_path": str(script_path),
                "script_type": script_type,
                "line_count": lines,
                "error_count": err_count,
                "score": score,
                "score_bucket": _score_bucket_key(score),
                "last_modified": modified_ts,
                "last_run_ts": last_run,
                "last_run_bucket": _last_run_bucket(last_run, now=ref_now),
            }
            rows.append(row)
    rows.sort(key=lambda item: (item["component"], item["script_path"]))
    return rows


def _filter_metrics_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    script_type: str = "all",
    last_run: str = "any",
    score_bucket: str = "all",
) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    type_key = (script_type or "all").strip()
    last_run_key = (last_run or "any").strip()
    score_key = (score_bucket or "all").strip()
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        if type_key.lower() != "all" and row.get("script_type") != type_key:
            continue
        if last_run_key.lower() not in {"any", "all"} and row.get("last_run_bucket") != last_run_key:
            continue
        if score_key.lower() != "all" and row.get("score_bucket") != score_key:
            continue
        filtered.append(dict(row))
    return filtered


def _score_distribution(rows: Sequence[Mapping[str, Any]]) -> Dict[str, int]:
    counts = {key: 0 for key in _SCORE_BUCKET_LABELS.keys()}
    for row in rows:
        bucket = row.get("score_bucket", "unknown") if isinstance(row, Mapping) else "unknown"
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts

# --------------------------------------------------------------------------------------
# Optional modules fallbacks
# --------------------------------------------------------------------------------------
def _fallback_build_editor_widget(parent=None, initial_path: Optional[str]=None, **_unused) -> QWidget:
    w = QWidget(parent)
    v = QVBoxLayout(w); v.setContentsMargins(10,10,10,10); v.setSpacing(8)
    lab = QLabel(f"Internal Code Viewer{f' — {os.path.basename(initial_path)}' if initial_path else ''}")
    lab.setStyleSheet("color:#eaf2ff; font:600 11pt 'Cascadia Code';")
    v.addWidget(lab)
    edit = QPlainTextEdit(w); edit.setReadOnly(True)
    # High-contrast palette: always set Base/Text with strong contrast
    p = edit.palette()
    bg = QColor("#0b1828"); fg = QColor("#d6e6ff")
    for g in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        p.setColor(g, QPalette.Base, bg); p.setColor(g, QPalette.Text, fg)
        p.setColor(g, QPalette.Window, bg); p.setColor(g, QPalette.WindowText, fg)
        p.setColor(g, QPalette.Highlight, QColor("#264f78")); p.setColor(g, QPalette.HighlightedText, QColor("#ffffff"))
    edit.setPalette(p)
    edit.setStyleSheet("QPlainTextEdit{border:1px solid #213040; border-radius:10px; font-family:'Cascadia Code',Consolas,monospace;}")
    try:
        if initial_path and os.path.isfile(initial_path):
            with open(initial_path, "r", encoding="utf-8", errors="replace") as f:
                edit.setPlainText(f.read())
        else:
            edit.setPlainText("No file selected.")
    except Exception as ex:
        edit.setPlainText(f"[open failed] {ex}")
    v.addWidget(edit, 1)
    return w

try:
    from code_editor import build_widget as build_editor_widget  # type: ignore
except Exception:
    build_editor_widget = _fallback_build_editor_widget  # type: ignore

class _FallbackTaskManager:
    def __init__(self, dataset_path: str, workspace_root: Optional[str] = None):
        self.dataset_path = dataset_path
        self._workspace = workspace_root

    def set_workspace(self, workspace_root: Optional[str]) -> None:
        self._workspace = workspace_root

    def start_system_metrics_job(self, *_, **__) -> None:  # pragma: no cover - fallback no-op
        return

    def stop_system_metrics_job(self) -> None:  # pragma: no cover - fallback no-op
        return


def _fallback_open_card(*_args, **_kwargs):  # type: ignore[override]
    QMessageBox.information(None, "Tasks", "Tasks module not available.")
    return None


try:  # pragma: no cover - import guard for optional module
    from tasks.card import TaskManager, open_card  # type: ignore
except Exception:  # pragma: no cover - fallback to placeholder
    TaskManager = _FallbackTaskManager  # type: ignore
    open_card = _fallback_open_card  # type: ignore

from operator_manager import OperatorManagerWidget

if TYPE_CHECKING:  # pragma: no cover - typing helpers
    from tasks.card import TaskCard

# --------------------------------------------------------------------------------------
# Theme
# --------------------------------------------------------------------------------------
@dataclass
class Theme:
    desktop_top: str = "#0f3b8e"
    desktop_mid: str = "#1c54cc"
    edge_glow: str = "#1c54cc"  # kept same as mid but not drawn anymore
    card_bg: str = "#0c1320"
    card_border: str = "#213040"
    card_radius: int = 12
    header_bg: str = "#0a111e"
    header_fg: str = "#eaf2ff"
    text_muted: str = "#c7d5ee"
    text_body: str = "#e9f3ff"
    accent: str = "#1E5AFF"
    accent_hov: str = "#2f72ff"
    editor_bg: str = "#0b1828"
    editor_fg: str = "#d6e6ff"
    editor_sel: str = "#264f78"
    menu_bg: str = "#0a111e"
    menu_fg: str = "#eaf2ff"
    taskbar_bg: str = "#0f1722"
    taskbar_fg: str = "#eaf2ff"
    task_btn_bg: str = "#172532"
    task_btn_fg: str = "#eaf2ff"
    task_btn_hv: str = "#24374a"
    start_bg: str = "#0f2342"
    start_panel: str = "#0d1526"
    start_tile: str = "#13213a"
    start_hv: str = "#1b7fd3"

def apply_contrast_palette(w: QWidget, bg_hex: str, fg_hex: str):
    # High-contrast rule: set strong Base/Text for all states
    p = w.palette(); bg = QColor(bg_hex); fg = QColor(fg_hex)
    for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        p.setColor(group, QPalette.Base, bg)
        p.setColor(group, QPalette.Text, fg)
        p.setColor(group, QPalette.Window, bg)
        p.setColor(group, QPalette.WindowText, fg)
        p.setColor(group, QPalette.Highlight, QColor("#2a5ea1"))
        p.setColor(group, QPalette.HighlightedText, QColor("#ffffff"))
    w.setPalette(p)

# --------------------------------------------------------------------------------------
# System Console (embedded log window)
# --------------------------------------------------------------------------------------
class SystemConsole(QWidget):
    def __init__(self, theme: Theme, log_path: str):
        super().__init__()
        self.setWindowFlag(Qt.Window, True)
        self.setWindowTitle("System Console")
        self.resize(900, 560)
        self.t = theme
        self.log_path = log_path
        self._pos = 0
        v = QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(8)
        self.text = QPlainTextEdit(self); self.text.setReadOnly(True)
        apply_contrast_palette(self.text, theme.editor_bg, theme.editor_fg)
        self.text.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; "
            f"selection-background-color:{theme.editor_sel}; border:1px solid {theme.card_border}; "
            f"font-family:'Cascadia Code',Consolas,monospace; }}"
        )
        v.addWidget(self.text, 1)
        row = QHBoxLayout(); row.setSpacing(8)
        def mk_btn(lbl, fn):
            b = QPushButton(lbl); b.clicked.connect(fn)
            b.setStyleSheet(f"QPushButton{{color:#fff;background:{self.t.accent};border:1px solid {self.t.card_border};border-radius:6px;padding:6px 10px;}}"
                            f"QPushButton:hover{{background:{self.t.accent_hov};}}")
            return b
        row.addWidget(mk_btn("Refresh", self.refresh))
        row.addWidget(mk_btn("Clear", self.clear_log))
        row.addStretch(1)
        v.addLayout(row)
        self.timer = QTimer(self); self.timer.setInterval(800); self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh(initial=True)
    def refresh(self, initial: bool=False):
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self._pos)
                chunk = f.read()
                self._pos = f.tell()
            if initial: self.text.setPlainText(chunk)
            else:
                if chunk:
                    self.text.moveCursor(self.text.textCursor().End)
                    self.text.insertPlainText(chunk)
            self.text.moveCursor(self.text.textCursor().End)
        except Exception:
            pass
    def clear_log(self):
        try:
            with open(self.log_path, "w", encoding="utf-8"): pass
            self._pos = 0; self.text.setPlainText("")
        except Exception as e:
            log(f"log clear failed: {e}", logging.WARNING)

# --------------------------------------------------------------------------------------
# Template Terminal (Card How-To)
# --------------------------------------------------------------------------------------
_TEMPLATE_INSTRUCTIONS = """\
Template Terminal — Card How-To
===============================
A Card is a QWidget hosted by the Virtual Desktop. It can be a terminal, editor,
dashboard—anything with a Qt widget.

Load cards in two ways:
1) Verified Card (embedded): define create_card(parent)->QWidget|(QWidget,title) or build_widget(parent)
2) Process Console (fallback): if no factory, we run it as a subprocess and stream output.

Contrast rule: always set Base/Text colors for Active/Inactive/Disabled *or* style with QSS so
read-only and disabled text stays readable.
"""
_TEMPLATE_CODE = r'''# minimal_card.py — simple verified card (high-contrast)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
def _apply_palette(w, bg="#0b1828", fg="#e9f3ff"):
    p=w.palette(); bgc,fgc=QColor(bg),QColor(fg)
    for g in (QPalette.Active,QPalette.Inactive,QPalette.Disabled):
        p.setColor(g,QPalette.Base,bgc); p.setColor(g,QPalette.Text,fgc)
        p.setColor(g,QPalette.Window,bgc); p.setColor(g,QPalette.WindowText,fgc)
    w.setPalette(p)
def create_card(parent=None):
    w=QWidget(parent); _apply_palette(w)
    w.setStyleSheet("QLabel{color:#c7d5ee; font:600 11pt 'Cascadia Code';}"
                    "QPushButton{color:#fff; background:#1E5AFF; border:1px solid #213040; border-radius:6px; padding:6px 10px;}"
                    "QPushButton:hover{background:#2f72ff;}")
    lay=QVBoxLayout(w); lay.setContentsMargins(14,14,14,14); lay.setSpacing(8)
    title=QLabel('🧩 My Card'); title.setAlignment(Qt.AlignCenter)
    btn=QPushButton('Click Me'); lay.addWidget(title); lay.addWidget(btn)
    return w,"My First Card"
'''
class TemplateTerminal(QWidget):
    def __init__(self, theme: Theme):
        super().__init__()
        self.t = theme
        v = QVBoxLayout(self); v.setContentsMargins(12, 12, 12, 12); v.setSpacing(10)
        hdr = QLabel("Template Terminal — Card How-To ✨")
        hdr.setStyleSheet("color:#eaf2ff; font:700 12pt 'Cascadia Code';")
        v.addWidget(hdr)
        self.txt = QPlainTextEdit(self); self.txt.setReadOnly(True)
        self.txt.setPlainText(_TEMPLATE_INSTRUCTIONS)
        apply_contrast_palette(self.txt, theme.editor_bg, theme.editor_fg)
        self.txt.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; "
            f"selection-background-color:{theme.editor_sel}; border:1px solid {theme.card_border}; "
            f"font-family:'Cascadia Code',Consolas,monospace; }}"
        )
        v.addWidget(self.txt, 1)
        row = QHBoxLayout(); row.setSpacing(8)
        btn_copy_info = QPushButton("📋 Copy Instructions")
        btn_copy_tpl = QPushButton("📋 Copy Minimal Card Template")
        for b in (btn_copy_info, btn_copy_tpl):
            b.setStyleSheet(f"QPushButton{{color:#fff;background:{self.t.accent};border:1px solid {self.t.card_border};border-radius:6px;padding:6px 10px;}}"
                            f"QPushButton:hover{{background:{self.t.accent_hov};}}")
        btn_copy_info.clicked.connect(lambda: QApplication.clipboard().setText(_TEMPLATE_INSTRUCTIONS, QClipboard.Clipboard))
        btn_copy_tpl.clicked.connect(lambda: QApplication.clipboard().setText(_TEMPLATE_CODE, QClipboard.Clipboard))
        row.addWidget(btn_copy_info); row.addWidget(btn_copy_tpl); row.addStretch(1)
        v.addLayout(row)
        code_hdr = QLabel("🧪 Minimal Card (verified) — save as minimal_card.py then use Start ▸ Apps ▸ Load Script as Card…")
        code_hdr.setStyleSheet("color:#c7d5ee;")
        v.addWidget(code_hdr)
        self.code = QPlainTextEdit(self); self.code.setReadOnly(True)
        self.code.setPlainText(_TEMPLATE_CODE)
        apply_contrast_palette(self.code, theme.editor_bg, theme.editor_fg)
        self.code.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; "
            f"selection-background-color:{self.t.editor_sel}; border:1px solid {self.t.card_border}; "
            f"font-family:'Cascadia Code',Consolas,monospace; }}"
        )
        v.addWidget(self.code, 1)

# --------------------------------------------------------------------------------------
# Explorer (renames change extension; non-native dialogs to keep containment)
# --------------------------------------------------------------------------------------
def _non_native_open_files(parent, caption, start_dir, filt) -> Tuple[List[str], str]:
    dlg = QFileDialog(parent, caption, start_dir, filt)
    dlg.setOption(QFileDialog.DontUseNativeDialog, True)  # containment: no OS-native surfaces
    dlg.setFileMode(QFileDialog.ExistingFiles)
    if dlg.exec(): return dlg.selectedFiles(), dlg.selectedNameFilter()
    return [], ""

def _non_native_open_file(parent, caption, start_dir, filt) -> Tuple[str, str]:
    files, nf = _non_native_open_files(parent, caption, start_dir, filt)
    return (files[0] if files else ""), nf

def _non_native_open_dir(parent, caption, start_dir) -> str:
    dlg = QFileDialog(parent, caption, start_dir)
    dlg.setOption(QFileDialog.DontUseNativeDialog, True)
    dlg.setFileMode(QFileDialog.Directory)
    dlg.setOption(QFileDialog.ShowDirsOnly, True)
    return dlg.selectedFiles()[0] if dlg.exec() else ""

class ExplorerCard(QWidget):
    def __init__(self, root_path: str, open_cb: Callable[[str], None], theme: Theme, refresh_hook: Optional[Callable[[], None]] = None):
        super().__init__()
        self.root = root_path
        self.open_cb = open_cb
        self.t = theme
        self.refresh_hook = refresh_hook
        v = QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(8)
        hdr = QFrame(self); hdr.setStyleSheet(f"background:{self.t.header_bg}; border:1px solid {self.t.card_border}; border-radius:8px;")
        h = QHBoxLayout(hdr); h.setContentsMargins(8,6,8,6); h.setSpacing(8)
        self.lbl_path = QLabel(self.root); self.lbl_path.setStyleSheet(f"color:{self.t.header_fg}; font:600 10pt 'Cascadia Code';")
        btn_up = QPushButton("Up"); btn_new = QPushButton("New Folder"); btn_refresh = QPushButton("Refresh"); self.btn_view = QPushButton("List View")
        for b in (btn_up, btn_new, btn_refresh, self.btn_view):
            b.setStyleSheet(
                f"QPushButton{{color:#fff; background:{self.t.accent}; border:1px solid {self.t.card_border}; border-radius:6px; padding:4px 10px;}}"
                f"QPushButton:hover{{background:{self.t.accent_hov};}}"
            )
        h.addWidget(self.lbl_path); h.addStretch(1); h.addWidget(self.btn_view); h.addWidget(btn_refresh); h.addWidget(btn_new); h.addWidget(btn_up)
        v.addWidget(hdr)
        self.list = QListWidget(self)
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setIconSize(QSize(48,48))
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setMovement(QListWidget.Static)
        self.list.setSpacing(12)
        self.list.setStyleSheet(
            f"QListWidget{{ background:{self.t.editor_bg}; color:{self.t.editor_fg}; border:1px solid {self.t.card_border}; border-radius:10px; }}"
        )
        v.addWidget(self.list, 1)
        btn_up.clicked.connect(self._go_up)
        btn_new.clicked.connect(self._new_folder)
        btn_refresh.clicked.connect(self._refresh)
        self.btn_view.clicked.connect(self._toggle_view_mode)
        self.list.itemActivated.connect(self._open_item)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._icon_context)
        self._cwd = self.root
        self._view_mode = "grid"
        self._thumb_cache: Dict[str, QIcon] = {}
        self._native_icon_cache: Dict[str, QIcon] = {}
        self._apply_view_mode()
        self._refresh()

    def _apply_view_mode(self):
        if self._view_mode == "list":
            self.list.setViewMode(QListWidget.ListMode)
            self.list.setIconSize(QSize(96, 72))
            self.list.setSpacing(6)
            self.list.setWordWrap(True)
            self.btn_view.setText("Grid View")
        else:
            self.list.setViewMode(QListWidget.IconMode)
            self.list.setIconSize(QSize(64, 64))
            self.list.setSpacing(12)
            self.list.setWordWrap(False)
            self.btn_view.setText("List View")

    def _toggle_view_mode(self):
        self._view_mode = "list" if self._view_mode == "grid" else "grid"
        self._thumb_cache.clear()
        self._native_icon_cache.clear()
        _clear_native_icon_caches()
        self._apply_view_mode()
        self._refresh()

    def _icon_for_path(self, path: str) -> QIcon:
        norm_path = os.path.abspath(path)
        path_obj = Path(norm_path)
        if self._view_mode == "list":
            ext = path_obj.suffix.lower()
            if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp"} and path_obj.exists():
                cached_thumb = self._thumb_cache.get(norm_path)
                if cached_thumb:
                    return cached_thumb
                pix = QPixmap(norm_path)
                if not pix.isNull():
                    icon = QIcon(
                        pix.scaled(self.list.iconSize(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    )
                    self._thumb_cache[norm_path] = icon
                    return icon

        cached_icon = self._native_icon_cache.get(norm_path)
        if cached_icon:
            return cached_icon

        icon, _ = _ICON_FOR_PATH_HELPER(path_obj)
        if icon.isNull():
            icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
        self._native_icon_cache[norm_path] = icon
        return icon

    def _refresh(self):
        self.list.clear()
        self.lbl_path.setText(self._cwd)
        try:
            ents = sorted(os.listdir(self._cwd), key=lambda s: s.lower())
        except Exception as e:
            log(f"Explorer list failed: {e}", logging.WARNING)
            ents = []
        if os.path.abspath(self._cwd) != os.path.abspath(self.root):
            it = QListWidgetItem("..")
            it.setIcon(QApplication.style().standardIcon(QStyle.SP_ArrowUp))
            it.setData(Qt.UserRole, os.path.abspath(os.path.join(self._cwd, "..")))
            self.list.addItem(it)
        for name in ents:
            full = os.path.join(self._cwd, name)
            it = QListWidgetItem(name)
            it.setIcon(self._icon_for_path(full))
            it.setData(Qt.UserRole, full)
            self.list.addItem(it)

    def _open_item(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if not path: return
        if os.path.isdir(path):
            self._cwd = path; self._refresh()
        else:
            self.open_cb(path)

    def _go_up(self):
        if os.path.abspath(self._cwd) == os.path.abspath(self.root):
            return
        self._cwd = os.path.abspath(os.path.join(self._cwd, ".."))
        self._refresh()

    def _new_folder(self):
        base = os.path.join(self._cwd, "New Folder")
        name = base; i = 1
        while os.path.exists(name):
            name = f"{base} {i}"; i += 1
        try:
            os.makedirs(name, exist_ok=False)
            self._refresh()
            if self.refresh_hook: self.refresh_hook(); QApplication.processEvents()
        except Exception as e:
            log(f"mkdir failed: {e}", logging.WARNING)

    def _icon_context(self, pos: QPoint):
        item = self.list.itemAt(pos)
        if not item: return
        path = item.data(Qt.UserRole)
        if not path: return
        m = QMenu(self)
        act_open = m.addAction("Open")
        act_rename = m.addAction("Rename")
        act_delete = m.addAction("Delete")
        act_props = m.addAction("Properties")
        act = m.exec(self.list.mapToGlobal(pos))
        if act == act_open:
            self._open_item(item)
        elif act == act_rename:
            new_name, ok = QInputDialog.getText(self, "Rename", "New name (extensions allowed):", text=os.path.basename(path))
            if ok and new_name:
                try:
                    os.rename(path, os.path.join(self._cwd, new_name))
                    self._refresh()
                    if self.refresh_hook: self.refresh_hook(); QApplication.processEvents()
                except Exception as e:
                    QMessageBox.warning(self, "Rename", f"Rename failed: {e}")
        elif act == act_delete:
            try:
                if os.path.isdir(path): shutil.rmtree(path)
                else: os.remove(path)
                self._refresh()
                if self.refresh_hook: self.refresh_hook(); QApplication.processEvents()
            except Exception as e:
                QMessageBox.warning(self, "Delete", f"Delete failed: {e}")
        elif act == act_props:
            size = os.path.getsize(path) if os.path.isfile(path) else "Folder"
            QMessageBox.information(self, "Properties", f"Path: {path}\nSize: {size}")

# --------------------------------------------------------------------------------------
# Card with Min/Max/Close and taskbar integration
# --------------------------------------------------------------------------------------
class CardSizeGrip(QSizeGrip):
    """Custom size grip that directly resizes the owning :class:`Card`."""

    def __init__(self, card: "Card", corner: Qt.Corner):
        super().__init__(card)
        self._card = card
        self._corner = corner
        self._dragging = False
        self._press_pos = QPoint()
        self._start_geom = QRect()

    def _handles_left(self) -> bool:
        return self._corner in (Qt.TopLeftCorner, Qt.BottomLeftCorner)

    def _handles_right(self) -> bool:
        return self._corner in (Qt.TopRightCorner, Qt.BottomRightCorner)

    def _handles_top(self) -> bool:
        return self._corner in (Qt.TopLeftCorner, Qt.TopRightCorner)

    def _handles_bottom(self) -> bool:
        return self._corner in (Qt.BottomLeftCorner, Qt.BottomRightCorner)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if getattr(self._card, "_maximized", False):
                event.ignore()
                return
            self._dragging = True
            self._press_pos = event.globalPosition().toPoint()
            self._start_geom = QRect(self._card.geometry())
            self._card.raise_()
            self._card.activateWindow()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self._dragging:
            super().mouseMoveEvent(event)
            return
        if getattr(self._card, "_maximized", False):
            self._dragging = False
            event.ignore()
            return
        delta = event.globalPosition().toPoint() - self._press_pos
        dx = delta.x()
        dy = delta.y()
        geom = self._start_geom
        x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()

        if self._handles_left():
            x += dx
            w -= dx
        elif self._handles_right():
            w += dx

        if self._handles_top():
            y += dy
            h -= dy
        elif self._handles_bottom():
            h += dy

        min_w = max(self._card.minimumWidth(), MIN_CARD_WIDTH)
        min_h = max(self._card.minimumHeight(), MIN_CARD_HEIGHT)

        if w < min_w:
            if self._handles_left():
                x -= (min_w - w)
            w = min_w

        if h < min_h:
            if self._handles_top():
                y -= (min_h - h)
            h = min_h

        parent = self._card.parentWidget()
        margin = 6
        if parent:
            avail_w = max(min_w, parent.width() - margin * 2)
            avail_h = max(min_h, parent.height() - margin * 2)
            if w > avail_w:
                w = avail_w
                if self._handles_left():
                    x = margin
                else:
                    x = parent.width() - margin - w
            if h > avail_h:
                h = avail_h
                if self._handles_top():
                    y = margin
                else:
                    y = parent.height() - margin - h

            max_x = parent.width() - margin - w
            max_y = parent.height() - margin - h
            x = max(margin, min(x, max_x))
            y = max(margin, min(y, max_y))

        new_geom = QRect(x, y, w, h)
        if new_geom != self._card.geometry():
            self._card.setGeometry(new_geom)
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging and event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()
            return
        super().mouseReleaseEvent(event)


class Card(QFrame):
    moved = Signal()
    moving = Signal(QPoint)
    resized = Signal()
    closed = Signal(object)     # self on close
    minimized = Signal(object)  # self on minimize
    restored = Signal(object)   # self on restore

    def __init__(self, theme: Theme, title: str = "Card", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.t = theme
        self._drag = False
        self._press = QPoint()
        self._persist_tag: Optional[str] = None
        self._maximized = False
        self._normal_geom = QRect(0,0,0,0)
        st = QApplication.style()
        self.task_profile = "card"
        self.task_icon = st.standardIcon(QStyle.SP_FileIcon)
        self.task_tooltip = title

        self.setObjectName("Card")
        self.setStyleSheet(
            f"#Card {{ background:{self.t.card_bg}; border:1px solid {self.t.card_border}; border-radius:{self.t.card_radius}px; }}"
        )
        sh = QGraphicsDropShadowEffect(self); sh.setColor(QColor(0, 30, 80, 150))
        sh.setBlurRadius(28); sh.setOffset(0, 12); self.setGraphicsEffect(sh)

        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        # Header
        self.header = QFrame(self); self.header.setObjectName("Hdr")
        self.header.setStyleSheet(
            f"#Hdr {{ background:{self.t.header_bg}; border-top-left-radius:{self.t.card_radius}px; "
            f"border-top-right-radius:{self.t.card_radius}px; }}"
            f"QLabel {{ color:{self.t.header_fg}; font:600 10.5pt 'Cascadia Code'; }}"
            f"QPushButton {{ color:#fff; background:{self.t.accent}; border:1px solid {self.t.card_border}; border-radius:6px; padding:3px 8px; }}"
            f"QPushButton:hover {{ background:{self.t.accent_hov}; }}"
        )
        H = QHBoxLayout(self.header); H.setContentsMargins(12, 8, 12, 6); H.setSpacing(8)
        self.title_label = QLabel(title, self.header)

        H.addWidget(self.title_label); H.addStretch(1)

        self.btn_min = QPushButton("—", self.header); self.btn_min.setFixedWidth(28)
        self.btn_max = QPushButton("▢", self.header); self.btn_max.setFixedWidth(28)
        self.close_btn = QPushButton("✕", self.header); self.close_btn.setFixedWidth(28)

        self.btn_min.clicked.connect(self._minimize_card)
        self.btn_max.clicked.connect(self._toggle_max_restore)
        self.close_btn.clicked.connect(self._close_card)

        for b in (self.btn_min, self.btn_max, self.close_btn):
            b.setCursor(Qt.PointingHandCursor)

        H.addWidget(self.btn_min); H.addWidget(self.btn_max); H.addWidget(self.close_btn)
        root.addWidget(self.header)

        # Body
        self.body = QFrame(self); self.body.setObjectName("Body")
        self.body.setStyleSheet(f"#Body {{ background:{self.t.card_bg}; }}")
        root.addWidget(self.body, 1)

        # Size grips
        corners = (
            Qt.BottomLeftCorner,
            Qt.BottomRightCorner,
            Qt.TopLeftCorner,
            Qt.TopRightCorner,
        )
        self._grips = [CardSizeGrip(self, corner) for corner in corners]
        for g in self._grips: g.setFixedSize(16, 16); g.raise_()

    def set_persist_tag(self, tag: str):
        self._persist_tag = tag

    def set_task_metadata(self, profile: Optional[str] = None, icon: Optional[QIcon] = None, tooltip: Optional[str] = None):
        if profile:
            self.task_profile = profile
        if icon is not None and not icon.isNull():
            self.task_icon = icon
        if tooltip:
            self.task_tooltip = tooltip

    def header_geom(self) -> QRect:
        return QRect(0, 0, self.width(), 44)

    def resizeEvent(self, e):
        w, h = self.width(), self.height(); m = 6; g = self._grips
        g[0].move(m, h - g[0].height() - m)
        g[1].move(w - g[1].width() - m, h - g[1].height() - m)
        g[2].move(m, m)
        g[3].move(w - g[3].width() - m, m)
        self.resized.emit()
        super().resizeEvent(e)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton and self.header_geom().contains(ev.position().toPoint()):
            self._drag = True; self._press = ev.position().toPoint()
            self.raise_(); self.activateWindow(); self.setFocus(Qt.ActiveWindowFocusReason)
            ev.accept()
        else:
            super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if not self._drag:
            super().mouseMoveEvent(ev); return
        delta = ev.position().toPoint() - self._press
        current_pos = self.pos()
        canvas = self.parentWidget()
        effect = self.graphicsEffect()
        cached_rect: Optional[QRect] = None
        if canvas is not None:
            if effect is not None:
                cached_rect = effect.boundingRectFor(QRectF(self.rect())).translated(current_pos.x(), current_pos.y()).toAlignedRect()
            else:
                cached_rect = self.geometry()
        if delta.isNull():
            ev.accept()
            return
        new_pos = current_pos + delta
        if canvas:
            r = canvas.rect()
            new_pos.setX(max(6, min(new_pos.x(), r.width() - self.width() - 6)))
            new_pos.setY(max(6, min(new_pos.y(), r.height() - self.height() - 6)))
        if new_pos == current_pos:
            ev.accept()
            return
        self.move(new_pos)
        if canvas is not None and cached_rect is not None:
            canvas.update(cached_rect)
            if effect is not None:
                new_rect = effect.boundingRectFor(QRectF(self.rect())).translated(new_pos.x(), new_pos.y()).toAlignedRect()
            else:
                new_rect = self.geometry()
            canvas.update(new_rect)
        self.moving.emit(new_pos)
        ev.accept()

    def mouseReleaseEvent(self, ev):
        if self._drag:
            self._drag = False; self.moved.emit()
        super().mouseReleaseEvent(ev)

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == Qt.LeftButton and self.header_geom().contains(ev.position().toPoint()):
            self._toggle_max_restore()
            ev.accept()
            return
        super().mouseDoubleClickEvent(ev)

    def contextMenuEvent(self, e):
        if not self.header_geom().contains(e.pos()): return
        menu = QMenu(self)
        act_min = menu.addAction("Minimize")
        act_max = menu.addAction("Maximize" if not self._maximized else "Restore")
        act_close = menu.addAction("Close")
        act = menu.exec(e.globalPos())
        if act == act_min: self._minimize_card()
        elif act == act_max: self._toggle_max_restore()
        elif act == act_close: self._close_card()

    def _minimize_card(self):
        self.hide()
        self.minimized.emit(self)

    def _toggle_max_restore(self):
        canvas = self.parentWidget()
        if not canvas: return
        if not self._maximized:
            self._normal_geom = QRect(self.x(), self.y(), self.width(), self.height())
            margin = 8
            insets = {"left": 0, "top": 0, "right": 0, "bottom": 0}
            parent_core = getattr(canvas, "parent", lambda: None)()
            if parent_core and hasattr(parent_core, "taskbar_insets"):
                try:
                    fetched = parent_core.taskbar_insets()
                    if isinstance(fetched, dict):
                        insets.update({k: int(max(0, v)) for k, v in fetched.items()})
                except Exception:
                    insets = {"left": 0, "top": 0, "right": 0, "bottom": 0}
            width = max(200, canvas.width() - insets["left"] - insets["right"] - 2 * margin)
            height = max(160, canvas.height() - insets["top"] - insets["bottom"] - 2 * margin)
            x = margin + insets["left"]
            y = margin + insets["top"]
            self.setGeometry(x, y, width, height)
            self._maximized = True
            self.btn_max.setText("❐")  # restore glyph
        else:
            if self._normal_geom.width() > 0:
                self.setGeometry(self._normal_geom)
            self._maximized = False
            self.btn_max.setText("▢")
        self.raise_(); self.activateWindow()
        self.restored.emit(self)

    def _close_card(self):
        try:
            self.closed.emit(self)
        finally:
            self.deleteLater()


# --------------------------------------------------------------------------------------
# System Overview card
# --------------------------------------------------------------------------------------
class SystemOverviewCard(Card):
    """Interactive dashboard presenting collected system metrics."""

    _DEFAULT_DB_NAME = "system_metrics.db"

    def __init__(
        self,
        theme: Theme,
        datasets_root: os.PathLike[str] | str,
        *,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(theme, "System Overview", parent)
        self._datasets_root = Path(datasets_root)
        self._datasets_root.mkdir(parents=True, exist_ok=True)
        self._db_path = self._datasets_root / self._DEFAULT_DB_NAME
        self._rows: List[Dict[str, Any]] = []
        self._filtered_rows: List[Dict[str, Any]] = []
        self._history_by_script: Dict[str, List[Dict[str, Any]]] = {}
        self._summary_time: float = time.time()
        self._subscription: Optional[BusSubscription] = None
        self._building_filters = False

        self._build_body()
        self._subscribe_bus()
        QTimer.singleShot(0, self.refresh)

    # ------------------------------------------------------------------
    def _build_body(self) -> None:
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(16, 16, 16, 16)
        body_layout.setSpacing(12)

        stats_frame = QFrame(self.body)
        stats_frame.setObjectName("SystemStats")
        stats_frame.setStyleSheet(
            (
                "#SystemStats{background:#0a111e;border:1px solid #1d2b3c;border-radius:12px;}"
                "QLabel{color:#eaf2ff;font:600 10pt 'Segoe UI';}"
            )
        )
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(12, 10, 12, 10)
        stats_layout.setSpacing(18)

        self._components_label = QLabel("Components: 0", stats_frame)
        self._scripts_label = QLabel("Scripts: 0", stats_frame)
        self._score_label = QLabel("Average Score: 0.00", stats_frame)
        self._generated_label = QLabel("Generated: --", stats_frame)
        for label in (
            self._components_label,
            self._scripts_label,
            self._score_label,
            self._generated_label,
        ):
            stats_layout.addWidget(label)
        stats_layout.addStretch(1)
        body_layout.addWidget(stats_frame)

        filter_frame = QFrame(self.body)
        filter_frame.setObjectName("SystemFilters")
        filter_frame.setStyleSheet(
            (
                "#SystemFilters{background:#0a111e;border:1px solid #1d2b3c;border-radius:12px;}"
                "QComboBox{color:#eaf2ff;background:#122035;border:1px solid #1f2b3c;border-radius:8px;padding:4px 8px;}"
                "QPushButton{color:#ffffff;background:#1E5AFF;border:none;border-radius:8px;padding:6px 12px;}"
                "QPushButton:hover{background:#2f72ff;}"
            )
        )
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(12)

        self.filter_type = QComboBox(filter_frame)
        self.filter_type.setMinimumWidth(180)
        self.filter_last_run = QComboBox(filter_frame)
        self.filter_last_run.setMinimumWidth(160)
        self.filter_score = QComboBox(filter_frame)
        self.filter_score.setMinimumWidth(180)
        self.refresh_button = QPushButton("Refresh", filter_frame)

        self._building_filters = True
        self.filter_type.addItem("All Script Types", "all")
        self.filter_last_run.addItem("Any Last Run", "any")
        for key, label in _LAST_RUN_LABELS.items():
            self.filter_last_run.addItem(label, key)
        self.filter_score.addItem("All Scores", "all")
        for key, label in _SCORE_BUCKET_LABELS.items():
            self.filter_score.addItem(label, key)
        self._building_filters = False

        filter_layout.addWidget(self.filter_type)
        filter_layout.addWidget(self.filter_last_run)
        filter_layout.addWidget(self.filter_score)
        filter_layout.addStretch(1)
        filter_layout.addWidget(self.refresh_button)
        body_layout.addWidget(filter_frame)

        splitter = QSplitter(Qt.Horizontal, self.body)
        splitter.setChildrenCollapsible(False)

        self.table = QTableWidget(0, 6, splitter)
        self.table.setObjectName("SystemTable")
        self.table.setHorizontalHeaderLabels(
            [
                "Script",
                "Component",
                "Type",
                "Last Run",
                "Errors",
                "Score",
            ]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for idx in range(2, 6):
            header.setSectionResizeMode(idx, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            (
                "QTableWidget{background:#0b1828;color:#eaf2ff;border:1px solid #1f2b3c;border-radius:10px;}"
                "QHeaderView::section{background:#122035;color:#d6e6ff;padding:6px;border:none;}"
                "QTableWidget::item:selected{background:#264f78;}"
            )
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        splitter.addWidget(self.table)

        self._charts_container = QWidget(splitter)
        charts_layout = QVBoxLayout(self._charts_container)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(12)

        distribution_label = QLabel("Score Distribution", self._charts_container)
        distribution_label.setStyleSheet("color:#eaf2ff;font:600 10pt 'Segoe UI';")
        charts_layout.addWidget(distribution_label)

        if pg and BarGraphItem is not None:
            self._distribution_plot = pg.PlotWidget(background=self.t.card_bg)
            self._distribution_plot.showGrid(y=True, alpha=0.2)
            charts_layout.addWidget(self._distribution_plot, 1)
        else:
            self._distribution_plot = None
            placeholder = QLabel(
                "PyQtGraph not available — install it to see charts.",
                self._charts_container,
            )
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color:#9ab0d6;font:600 10pt 'Segoe UI';")
            charts_layout.addWidget(placeholder)

        history_label = QLabel("Score History", self._charts_container)
        history_label.setStyleSheet("color:#eaf2ff;font:600 10pt 'Segoe UI';")
        charts_layout.addWidget(history_label)

        if pg:
            axis_items = {"bottom": DateAxisItem(orientation="bottom")} if DateAxisItem else None
            self._history_plot = pg.PlotWidget(
                axisItems=axis_items,
                background=self.t.card_bg,
            )
            self._history_plot.setYRange(0, 1.05)
            self._history_plot.showGrid(y=True, alpha=0.2)
            charts_layout.addWidget(self._history_plot, 1)
        else:
            self._history_plot = None
            history_placeholder = QLabel(
                "Score history charts require pyqtgraph.",
                self._charts_container,
            )
            history_placeholder.setAlignment(Qt.AlignCenter)
            history_placeholder.setStyleSheet("color:#9ab0d6;font:600 10pt 'Segoe UI';")
            charts_layout.addWidget(history_placeholder)

        self._history_hint = QLabel("Select a script to view trend details.", self._charts_container)
        self._history_hint.setStyleSheet("color:#9ab0d6;font:500 9pt 'Segoe UI';")
        charts_layout.addWidget(self._history_hint)

        splitter.addWidget(self._charts_container)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        body_layout.addWidget(splitter, 1)

        self._status_label = QLabel("Collecting metrics…", self.body)
        self._status_label.setStyleSheet("color:#9ab0d6;font:500 9pt 'Segoe UI';")
        body_layout.addWidget(self._status_label)

        self.refresh_button.clicked.connect(lambda: self.refresh(store=True))
        self.filter_type.currentIndexChanged.connect(self._apply_filters)
        self.filter_last_run.currentIndexChanged.connect(self._apply_filters)
        self.filter_score.currentIndexChanged.connect(self._apply_filters)
        self.table.itemSelectionChanged.connect(self._handle_selection_changed)
        self.destroyed.connect(lambda *_: self._cleanup())

    # ------------------------------------------------------------------
    def _subscribe_bus(self) -> None:
        if bus_subscribe is None:
            return
        try:
            self._subscription = bus_subscribe("system.metrics", self._on_metrics_event)
        except Exception:
            log("SystemOverviewCard bus subscription failed", logging.DEBUG)

    # ------------------------------------------------------------------
    def _cleanup(self) -> None:
        if self._subscription is not None:
            try:
                self._subscription.unsubscribe()
            except Exception:
                pass
            finally:
                self._subscription = None

    # ------------------------------------------------------------------
    def _on_metrics_event(self, _payload: dict) -> None:  # pragma: no cover - callback bridge
        QTimer.singleShot(0, self.refresh)

    # ------------------------------------------------------------------
    def refresh(self, store: bool = False) -> None:
        self._status_label.setText("Refreshing metrics…")
        QApplication.processEvents()
        try:
            summary = collect_metrics(store=store, datasets_root=self._datasets_root)
        except Exception as exc:
            self._status_label.setText(f"Metrics refresh failed: {exc}")
            log(f"SystemOverviewCard refresh failed: {exc}", logging.DEBUG)
            return
        try:
            history = fetch_metrics(scope="local", db_paths={"local": str(self._db_path)})
        except Exception as exc:
            history = []
            log(f"Metrics history fetch failed: {exc}", logging.DEBUG)

        generated_at = float(summary.get("generated_at") or time.time()) if summary else time.time()
        self._summary_time = generated_at
        self._rows = _flatten_metrics_summary(summary, now=generated_at)
        self._group_history(history)
        self._update_filters()
        self._apply_filters()
        self._update_stats()
        self._status_label.setText(f"Last updated {self._format_timestamp(generated_at)}")

    # ------------------------------------------------------------------
    def _group_history(self, history: Iterable[Mapping[str, Any]]) -> None:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for entry in history or []:
            if not isinstance(entry, Mapping):
                continue
            script = entry.get("script_path")
            if not script:
                continue
            grouped.setdefault(str(script), []).append(dict(entry))
        for values in grouped.values():
            values.sort(key=lambda item: float(item.get("timestamp") or 0.0))
        self._history_by_script = grouped

    # ------------------------------------------------------------------
    def _update_filters(self) -> None:
        self._building_filters = True
        current_type = self.filter_type.currentData()
        self.filter_type.clear()
        self.filter_type.addItem("All Script Types", "all")
        types = sorted({row.get("script_type", "Unknown") for row in self._rows})
        for label in types:
            self.filter_type.addItem(label, label)
        if current_type in {"all", *types}:
            index = self.filter_type.findData(current_type)
            if index >= 0:
                self.filter_type.setCurrentIndex(index)
        else:
            self.filter_type.setCurrentIndex(0)
        self._building_filters = False

    # ------------------------------------------------------------------
    def _apply_filters(self) -> None:
        if self._building_filters:
            return
        script_type = self.filter_type.currentData() or "all"
        last_run = self.filter_last_run.currentData() or "any"
        score_bucket = self.filter_score.currentData() or "all"
        filtered = _filter_metrics_rows(
            self._rows,
            script_type=script_type,
            last_run=last_run,
            score_bucket=score_bucket,
        )
        self._filtered_rows = filtered
        self._populate_table(filtered)
        self._update_distribution_chart(filtered if filtered else self._rows)
        if filtered:
            QTimer.singleShot(0, lambda: self._select_first_row())
        else:
            self._update_history_plot(None)

    # ------------------------------------------------------------------
    def _select_first_row(self) -> None:
        if self.table.rowCount() and not self.table.selectedItems():
            self.table.selectRow(0)

    # ------------------------------------------------------------------
    def _populate_table(self, rows: Sequence[Mapping[str, Any]]) -> None:
        self.table.setRowCount(len(rows))
        for idx, row in enumerate(rows):
            script_path = str(row.get("script_path", ""))
            component = str(row.get("component", ""))
            script_type = str(row.get("script_type", "Unknown"))
            last_run_text = self._format_last_run(row)
            errors = int(row.get("error_count") or 0)
            score = float(row.get("score") or 0.0)
            bucket = row.get("score_bucket", "unknown")
            score_label = _SCORE_BUCKET_LABELS.get(bucket, bucket.title())

            items = [
                QTableWidgetItem(script_path),
                QTableWidgetItem(component),
                QTableWidgetItem(script_type),
                QTableWidgetItem(last_run_text),
                QTableWidgetItem(str(errors)),
                QTableWidgetItem(f"{score:.2f} — {score_label}"),
            ]
            for col, item in enumerate(items):
                if col == 0:
                    item.setData(Qt.UserRole, script_path)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(idx, col, item)

    # ------------------------------------------------------------------
    def _format_last_run(self, row: Mapping[str, Any]) -> str:
        bucket = row.get("last_run_bucket")
        if bucket == "never":
            return _LAST_RUN_LABELS["never"]
        ts = row.get("last_run_ts")
        if ts in (None, ""):
            return _LAST_RUN_LABELS.get(str(bucket), "Unknown")
        try:
            timestamp = float(ts)
        except (TypeError, ValueError):
            return _LAST_RUN_LABELS.get(str(bucket), "Unknown")
        relative = self._relative_time(timestamp)
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone()
        return f"{relative} ({dt.strftime('%Y-%m-%d %H:%M')})"

    # ------------------------------------------------------------------
    def _relative_time(self, timestamp: float) -> str:
        delta = max(0.0, self._summary_time - float(timestamp))
        if delta < 60:
            return "Just now"
        if delta < 3600:
            minutes = int(delta // 60)
            return f"{minutes}m ago"
        if delta < 86400:
            hours = int(delta // 3600)
            return f"{hours}h ago"
        days = int(delta // 86400)
        return f"{days}d ago"

    # ------------------------------------------------------------------
    def _update_stats(self) -> None:
        components = {row["component"] for row in self._rows}
        total_scripts = len(self._rows)
        avg_score = sum(row.get("score", 0.0) for row in self._rows)
        avg_value = (avg_score / total_scripts) if total_scripts else 0.0
        self._components_label.setText(f"Components: {len(components)}")
        self._scripts_label.setText(f"Scripts: {total_scripts}")
        self._score_label.setText(f"Average Score: {avg_value:.2f}")
        self._generated_label.setText(f"Generated: {self._format_timestamp(self._summary_time)}")

    # ------------------------------------------------------------------
    def _format_timestamp(self, ts: float) -> str:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()
        return dt.strftime("%Y-%m-%d %H:%M")

    # ------------------------------------------------------------------
    def _handle_selection_changed(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            self._update_history_plot(None)
            return
        script_path = selected[0].data(Qt.UserRole)
        self._update_history_plot(script_path)

    # ------------------------------------------------------------------
    def _update_distribution_chart(self, rows: Sequence[Mapping[str, Any]]) -> None:
        if not pg or self._distribution_plot is None:
            return
        counts = _score_distribution(rows)
        self._distribution_plot.clear()
        keys = ["healthy", "watch", "critical", "unknown"]
        colors = {
            "healthy": "#1E5AFF",
            "watch": "#f2c744",
            "critical": "#ef5b68",
            "unknown": "#6b7a90",
        }
        ticks = []
        max_height = 1
        for idx, key in enumerate(keys):
            height = counts.get(key, 0)
            max_height = max(max_height, height)
            ticks.append((idx, _SCORE_BUCKET_LABELS.get(key, key.title())))
            if BarGraphItem is None:
                continue
            bar = BarGraphItem(
                x=[idx],
                height=[height],
                width=0.6,
                brush=pg.mkBrush(colors[key]),
                pen=pg.mkPen(colors[key]),
            )
            self._distribution_plot.addItem(bar)
        axis = self._distribution_plot.getAxis("bottom")
        if axis:
            axis.setTicks([ticks])
        self._distribution_plot.setYRange(0, max_height + 1)

    # ------------------------------------------------------------------
    def _update_history_plot(self, script_path: Optional[str]) -> None:
        if not pg or self._history_plot is None:
            return
        self._history_plot.clear()
        if not script_path:
            self._history_hint.setText("Select a script to view trend details.")
            return
        history = self._history_by_script.get(str(script_path), [])
        if not history:
            self._history_hint.setText("No historical scores recorded for this script yet.")
            return
        points = []
        for entry in history:
            try:
                ts = float(entry.get("timestamp"))
            except (TypeError, ValueError):
                continue
            score = entry.get("score")
            if score is None:
                continue
            try:
                val = float(score)
            except (TypeError, ValueError):
                continue
            points.append((ts, val))
        if not points:
            self._history_hint.setText("History available but contains no numeric scores.")
            return
        xs, ys = zip(*points)
        self._history_plot.plot(
            x=list(xs),
            y=list(ys),
            pen=pg.mkPen(self.t.accent, width=2),
            symbol="o",
            symbolBrush=pg.mkBrush(self.t.accent_hov),
        )
        self._history_hint.setText(str(script_path))

# --------------------------------------------------------------------------------------
# Desktop icons (no OS drag-out; internal only)
# --------------------------------------------------------------------------------------
class DesktopIcon(QToolButton):
    request_open = Signal(str)
    request_move_to_folder = Signal(str, str)  # src, dst_folder
    def __init__(self, theme: Theme, path: str, parent: QWidget, grid_size: Tuple[int, int]):
        super().__init__(parent)
        self.t = theme
        self.path = path
        self.grid_size = grid_size
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(QSize(*grid_size))
        self.setAcceptDrops(False)  # containment: icons themselves do not accept external drops
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        base = os.path.basename(path)
        self._caption_base = os.path.splitext(base)[0] if os.path.isfile(path) else base
        self._set_icon_size_from_state()
        self.setCursor(Qt.OpenHandCursor)
        self._resolved_icon: Optional[QIcon] = None
        self._resolved_icon_native: bool = False
        self._pick_icon()
        self._drag_active = False
        self._press_pos = QPoint()
        self._moved = False
        self._hovered = False
        self._selected = False
        self._drag_hotspot = QPoint()
        self.setStyleSheet("QToolButton{color:#eaf2ff;}")  # high-contrast text
        self.setFocusPolicy(Qt.ClickFocus)
        self._update_caption_text()
        self._update_tooltip()

    def _set_icon_size_from_state(self):
        st = _load_state()
        sz = st.get("icon_size", "medium")
        if sz == "small": self.setIconSize(QSize(32, 32))
        elif sz == "large": self.setIconSize(QSize(64, 64))
        else: self.setIconSize(QSize(48, 48))
        self._update_caption_text()

    def _pick_icon(self):
        path = Path(self.path)
        icon, native = _icon_for_path(path)
        self._resolved_icon = icon
        self._resolved_icon_native = native
        self.setIcon(icon)
        self._update_tooltip()

    def changeEvent(self, event: QEvent) -> None:  # pragma: no cover - GUI update
        if event.type() == QEvent.FontChange:
            self._update_caption_text()
        super().changeEvent(event)

    def _update_caption_text(self) -> None:
        caption_source = getattr(self, "_caption_base", None)
        if caption_source is None:
            base_name = os.path.basename(self.path)
            caption_source = os.path.splitext(base_name)[0] if os.path.isfile(self.path) else base_name
        formatted = self._format_caption(caption_source)
        self.setText(formatted)

    def _format_caption(self, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return ""
        metrics = QFontMetrics(self.font())
        max_width = max(24, self.grid_size[0] - 12)
        lines: List[str] = []
        remainder = cleaned
        for _ in range(2):
            if not remainder:
                break
            segment, remainder = self._consume_caption_segment(remainder, metrics, max_width)
            if not segment:
                # ensure forward progress even when measuring fails
                segment, remainder = remainder[0], remainder[1:]
            lines.append(metrics.elidedText(segment, Qt.ElideRight, max_width))
        if not lines:
            return ""
        if remainder:
            lines[-1] = metrics.elidedText(lines[-1], Qt.ElideRight, max_width)
        return "\n".join(lines)

    def _consume_caption_segment(self, text: str, metrics: QFontMetrics, max_width: int) -> Tuple[str, str]:
        snippet = text.lstrip()
        if not snippet:
            return "", ""
        consumed = ""
        last_space = -1
        for idx, ch in enumerate(snippet):
            candidate = consumed + ch
            if metrics.horizontalAdvance(candidate) <= max_width or not consumed:
                consumed = candidate
                if ch.isspace():
                    last_space = len(consumed.rstrip())
            else:
                break
        if len(consumed) == len(snippet):
            return consumed.rstrip(), ""
        break_at = last_space if last_space > 0 else len(consumed)
        segment = consumed[:break_at].rstrip()
        remainder = snippet[break_at:].lstrip()
        return segment, remainder

    def _update_tooltip(self) -> None:
        info = QFileInfo(self.path)
        if not info.exists():
            self.setToolTip("")
            return
        display_name = info.fileName() or os.path.basename(self.path)
        if _FILE_ICON_PROVIDER is not None:
            try:
                type_desc = _FILE_ICON_PROVIDER.type(info)
            except Exception:
                type_desc = "File"
        else:
            type_desc = "File folder" if info.isDir() else (info.suffix() or "File")
        created_dt: QDateTime = info.birthTime() if info.birthTime().isValid() else info.created()
        if not created_dt.isValid():
            created_str = "Unknown"
        else:
            created_dt = created_dt.toTimeZone(QDateTime.currentDateTime().timeZone())
            created_str = created_dt.toString("dddd, MMMM d, yyyy h:mm AP")
        tooltip = f"{display_name}\nType: {type_desc}\nDate created: {created_str}"
        self.setToolTip(tooltip)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            parent = self.parentWidget()
            if parent and hasattr(parent, "set_active_icon"):
                parent.set_active_icon(self)
            self.setCursor(Qt.ClosedHandCursor)
            self._drag_active = True
            self._press_pos = ev.position().toPoint()
            self._drag_hotspot = QPoint(self._press_pos)
            self._moved = False
        elif ev.button() == Qt.RightButton:
            parent = self.parentWidget()
            if parent and hasattr(parent, "set_active_icon"):
                parent.set_active_icon(self)
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._drag_active:
            delta = ev.position().toPoint() - self._press_pos
            if delta.manhattanLength() > QApplication.startDragDistance():
                self._moved = True
                drag = QDrag(self)
                mime = QMimeData()
                mime.setData(_ICON_DRAG_MIME, self.path.encode("utf-8"))
                mime.setData(_ICON_OFFSET_MIME, f"{self._drag_hotspot.x()},{self._drag_hotspot.y()}".encode("utf-8"))
                mime.setUrls([QUrl.fromLocalFile(self.path)])
                drag.setMimeData(mime)
                pixmap = self._build_drag_pixmap()
                drag.setPixmap(pixmap)
                drag.setHotSpot(self._drag_hotspot)
                parent = self.parentWidget()
                if isinstance(parent, DesktopCanvas):
                    parent.begin_icon_drag(self.path)
                drop_actions = Qt.DropActions(Qt.MoveAction | Qt.CopyAction)
                result = drag.exec(drop_actions, Qt.MoveAction)
                if isinstance(parent, DesktopCanvas):
                    parent.end_icon_drag(result, self.path)
                self._drag_active = False
                self.setCursor(Qt.OpenHandCursor)
                return
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self._drag_active:
            self.setCursor(Qt.OpenHandCursor)
            self._drag_active = False
            self._moved = False
            # Simple clicks fall through so QToolButton handles selection; activation stays in mouseDoubleClickEvent.
        super().mouseReleaseEvent(ev)

    def mouseDoubleClickEvent(self, ev):
        if ev.button() == Qt.LeftButton: self.request_open.emit(self.path)

    def enterEvent(self, event: QEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def setSelected(self, selected: bool) -> None:
        if self._selected == selected:
            return
        self._selected = selected
        self.update()

    def isSelected(self) -> bool:
        return self._selected

    def paintEvent(self, event):
        if self._hovered or self._selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(2, 2, -2, -2)
            border_color = QColor(112, 169, 255, 200 if self._selected else 140)
            fill_color = QColor(112, 169, 255, 60 if self._selected else 30)
            painter.setPen(border_color)
            painter.setBrush(fill_color)
            painter.drawRoundedRect(rect, 6, 6)
            painter.end()
        super().paintEvent(event)

    def _build_drag_pixmap(self) -> QPixmap:
        pixmap = self.grab()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        painter.fillRect(pixmap.rect(), QColor(64, 128, 255, 120))
        painter.end()
        return pixmap

    # CONTAINMENT: removed any external clipboard or drag-out behavior

    def contextMenuEvent(self, e):
        parent = self.parentWidget()
        if parent and hasattr(parent, "set_active_icon"):
            parent.set_active_icon(self)
        m = QMenu(self)
        act_open = m.addAction("Open")
        act_rename = m.addAction("Rename")
        act_delete = m.addAction("Delete")
        act_props = m.addAction("Properties")
        act = m.exec(e.globalPos())
        if act == act_open:
            handled = False
            parent_obj = self.parent()
            open_cb = getattr(parent_obj, "_open_path_from_icon", None)
            if callable(open_cb):
                try:
                    open_cb(self.path)
                    handled = True
                except Exception as exc:
                    log(f"Context open failed for {self.path}: {exc}", logging.DEBUG)
                    handled = False
            if not handled:
                self.request_open.emit(self.path)
        elif act == act_rename:
            new_name, ok = QInputDialog.getText(self, "Rename", "New name (extensions allowed):", text=os.path.basename(self.path))
            if ok and new_name:
                try:
                    os.rename(self.path, os.path.join(os.path.dirname(self.path), new_name))
                    parent_canvas = self.parentWidget()
                    if isinstance(parent_canvas, DesktopCanvas):
                        parent_canvas.refresh_icons_once()
                    QApplication.processEvents()
                except Exception as exc:
                    QMessageBox.warning(self, "Rename", f"Rename failed: {exc}")
        elif act == act_delete:
            try:
                os.remove(self.path) if os.path.isfile(self.path) else shutil.rmtree(self.path)
                parent_canvas = self.parentWidget()
                if isinstance(parent_canvas, DesktopCanvas):
                    parent_canvas.refresh_icons_once()
                QApplication.processEvents()
            except Exception as exc:
                QMessageBox.warning(self, "Delete", f"Delete failed: {exc}")
        elif act == act_props:
            size = os.path.getsize(self.path) if os.path.isfile(self.path) else sum(f.stat().st_size for f in Path(self.path).rglob('*') if f.is_file())
            QMessageBox.information(self, "Properties", f"Path: {self.path}\nSize: {size} bytes")

# --------------------------------------------------------------------------------------
# Desktop canvas
# --------------------------------------------------------------------------------------
class DesktopCanvas(QWidget):
    def __init__(
        self,
        theme: Theme,
        size: QSize,
        parent: Optional[QWidget] = None,
        core: Optional["VirtualDesktopCore"] = None,
    ):
        super().__init__(parent)
        self.t = theme
        self.resize(size)
        self._core_ref: Optional[Callable[[], Optional["VirtualDesktopCore"]]] = None
        if core is not None:
            self._core_ref = weakref.ref(core)
        else:
            resolved = self._resolve_core()
            if resolved is not None:
                self._core_ref = weakref.ref(resolved)
        self.setAcceptDrops(True)  # Allow internal icon drags; external drops remain disabled via MIME checks
        self._icons: Dict[str, DesktopIcon] = {}
        self._drag_origin_path: Optional[str] = None
        self._internal_drop_paths: set[str] = set()
        self._fswatcher = QFileSystemWatcher(self)
        self._fswatcher.addPath(VDSK_ROOT)
        self._fswatcher.directoryChanged.connect(self._refresh_icons)
        self._fswatcher.fileChanged.connect(lambda _: self._refresh_icons())
        self._grid_size = (96, 96)  # square spacing keeps icons aligned
        self._selected_icon: Optional[DesktopIcon] = None
        self._selected_path: Optional[str] = None
        self._drag_active = False
        self._pending_refresh = False
        self._bg_manager = BackgroundManager(self)
        self._bg_manager.register(BackgroundMode.STATIC, lambda canvas: StaticImageBg(canvas))
        self._bg_manager.register(BackgroundMode.GIF, lambda canvas: GifBg(canvas))
        self._bg_manager.register(BackgroundMode.VIDEO, lambda canvas: VideoBg(canvas))
        self._bg_manager.register(BackgroundMode.GL, lambda canvas: GLViewportBg(canvas))
        self._bg_config = BackgroundConfig.from_state(_load_state().get("background"))
        self._sort_mode = _load_state().get("desktop_sort", "name")
        self._last_sorted_paths: List[str] = []
        self._apply_background_config(self._bg_config, persist=False)
        QTimer.singleShot(0, self._refresh_icons)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._desktop_context)

    def _resolve_core(self) -> Optional["VirtualDesktopCore"]:
        candidate: Optional[QObject] = self.parent()
        while candidate is not None:
            if hasattr(candidate, "open_any_path") and callable(getattr(candidate, "open_any_path", None)):
                return cast("VirtualDesktopCore", candidate)
            candidate = candidate.parent() if isinstance(candidate, QObject) else None
        return None

    def _core(self) -> Optional["VirtualDesktopCore"]:
        if self._core_ref is not None:
            core = self._core_ref()
            if core is not None:
                return core
        resolved = self._resolve_core()
        if resolved is not None:
            self._core_ref = weakref.ref(resolved)
        return resolved

    def _open_path_from_icon(self, path: str) -> None:
        core = self._core()
        if not core:
            log(f"Dropped icon open for {path}: no VirtualDesktopCore", logging.DEBUG)
            return
        try:
            core.open_any_path(path)
        except Exception as exc:
            log(f"Icon open failed for {path}: {exc}", logging.DEBUG)

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        # Clean blue desktop. No trim, no inner vignette. High contrast icons ensure readability.
        painted = self._bg_manager.paint(p, r)
        if not painted:
            g = QLinearGradient(r.topLeft(), r.bottomLeft())
            g.setColorAt(0.00, QColor(self.t.desktop_top))
            g.setColorAt(1.00, QColor(self.t.desktop_mid))
            p.fillRect(r, g)

    def resizeEvent(self, ev: QResizeEvent):  # pragma: no cover - trivial wrapper
        super().resizeEvent(ev)
        self._bg_manager.resize(ev.size())

    def _refresh_icons(self):
        if self._drag_active:
            self._pending_refresh = True
            return
        self._do_refresh_icons()

    def refresh_icons_once(self) -> None:
        if self._drag_active:
            self._pending_refresh = True
            return
        self._do_refresh_icons()

    def begin_icon_drag(self, path: str) -> None:
        if self._drag_active:
            return
        self._drag_active = True
        self._drag_origin_path = self._normalize_drop_path(path)
        self._internal_drop_paths.clear()

    def _register_internal_drop(self, path: str) -> None:
        normalized = self._normalize_drop_path(path)
        if normalized:
            self._internal_drop_paths.add(normalized)

    def _normalize_drop_path(self, path: str) -> Optional[str]:
        try:
            return str(Path(path).resolve())
        except Exception:
            try:
                return os.path.abspath(path)
            except Exception:
                return None

    def end_icon_drag(self, action: Qt.DropAction, path: Optional[str]) -> None:
        if not self._drag_active:
            return
        self._drag_active = False
        normalized = self._normalize_drop_path(path) if path else None
        if normalized is None:
            normalized = self._drag_origin_path
        delete_source = False
        workspace_root_str: Optional[str]
        try:
            workspace_root_str = str(Path(VDSK_ROOT).resolve())
        except Exception:
            workspace_root_str = None
        if action == Qt.MoveAction and normalized and _is_contained(normalized):
            if workspace_root_str and normalized == workspace_root_str:
                delete_source = False
            elif normalized not in self._internal_drop_paths:
                delete_source = True
        if delete_source and normalized:
            try:
                resolved = Path(normalized)
                if resolved.is_dir():
                    shutil.rmtree(resolved)
                elif resolved.exists():
                    resolved.unlink()
            except Exception as exc:
                log(f"External move cleanup failed for {normalized}: {exc}", logging.WARNING)
                delete_source = False
        need_refresh = delete_source or self._pending_refresh
        self._pending_refresh = False
        self._internal_drop_paths.clear()
        self._drag_origin_path = None
        if need_refresh:
            self._do_refresh_icons()

    def _do_refresh_icons(self) -> None:
        self._pending_refresh = False
        self._core()  # ensure we attempt to cache a core reference before wiring callbacks
        current = set(self._icons.keys())
        want_paths = [str(p) for p in self._sorted_workspace_entries()]
        self._last_sorted_paths = want_paths
        want_set = set(want_paths)
        changed = False
        for path in list(current - want_set):
            btn = self._icons.pop(path, None)
            if not btn:
                continue
            btn.setParent(None)
            btn.deleteLater()
            if self._selected_path == path:
                self._selected_icon = None
                self._selected_path = None
            changed = True
        for path in want_paths:
            if path in self._icons:
                continue
            btn = DesktopIcon(self.t, path, self, self._grid_size)
            btn.request_open.connect(self._open_path_from_icon)
            btn.request_move_to_folder.connect(self._move_file_to_folder)
            btn.show()
            btn.lower()
            self._icons[path] = btn
            pos = self.restore_icon_position(path)
            if pos is None:
                idx = len(self._icons) - 1
                cols = max(1, int((self.width() - GRID_ORIGIN_X * 2) / self._grid_size[0]))
                row, col = divmod(idx, cols)
                btn.move(
                    GRID_ORIGIN_X + col * self._grid_size[0],
                    GRID_ORIGIN_Y + row * self._grid_size[1],
                )
            else:
                btn.move(pos)
            changed = True
        for path, btn in self._icons.items():
            btn._set_icon_size_from_state()
            btn.setSelected(path == self._selected_path)
            try:
                btn.lower()
            except Exception:
                pass
            if path == self._selected_path:
                self._selected_icon = btn
        if changed:
            if self._sort_mode in {"type", "date"}:
                self._arrange_icons()
            self._notify_workspace_changed()
        parent = self.parent()
        if parent and hasattr(parent, "_iter_cards"):
            try:
                cards = list(parent._iter_cards())  # type: ignore[attr-defined]
            except Exception:
                cards = []
            for card in cards:
                try:
                    card.raise_()
                except Exception:
                    pass
        QApplication.processEvents()

    def _sorted_workspace_entries(self) -> List[Path]:
        try:
            entries = list(Path(VDSK_ROOT).iterdir())
        except Exception as exc:
            log(f"list workspace failed: {exc}", logging.DEBUG)
            return []
        mode = self._sort_mode if self._sort_mode in {"name", "type", "date"} else "name"
        def base_key(p: Path) -> int:
            return 0 if p.is_dir() else 1

        if mode == "type":
            entries.sort(key=lambda p: (base_key(p), p.suffix.lower(), p.name.lower()))
        elif mode == "date":
            def mtime(path: Path) -> float:
                try:
                    return float(path.stat().st_mtime)
                except Exception:
                    return 0.0
            entries.sort(key=lambda p: (base_key(p), -mtime(p), p.name.lower()))
        else:
            entries.sort(key=lambda p: (base_key(p), p.name.lower()))
        return entries

    def _notify_workspace_changed(self) -> None:
        core = self.parent()
        if core and hasattr(core, "mark_start_index_stale"):
            try:
                core.mark_start_index_stale()
            except Exception:
                pass

    def _current_icon_size(self) -> str:
        return str(_load_state().get("icon_size", "medium"))

    def _set_sort_mode(self, mode: str) -> None:
        target = mode if mode in {"name", "type", "date"} else "name"
        if target == self._sort_mode:
            return
        self._sort_mode = target
        st = _load_state()
        st["desktop_sort"] = target
        _save_state(st)
        self._refresh_icons()
        self._arrange_icons()

    def _arrange_icons(self) -> None:
        if not self._icons:
            return
        paths = self._last_sorted_paths or [str(p) for p in self._sorted_workspace_entries()]
        cols = max(1, int((self.width() - GRID_ORIGIN_X * 2) / self._grid_size[0]))
        for idx, path in enumerate(paths):
            btn = self._icons.get(path)
            if not btn:
                continue
            row, col = divmod(idx, cols)
            pos = QPoint(
                GRID_ORIGIN_X + col * self._grid_size[0],
                GRID_ORIGIN_Y + row * self._grid_size[1],
            )
            btn.move(pos)
            self.save_icon_position(path, pos)

    def _unique_path(self, base_name: str, extension: str = "") -> Path:
        candidate = Path(VDSK_ROOT) / f"{base_name}{extension}"
        if not candidate.exists():
            return candidate
        idx = 1
        while True:
            alt = Path(VDSK_ROOT) / f"{base_name} ({idx}){extension}"
            if not alt.exists():
                return alt
            idx += 1

    def _create_text_file(self, base_name: str, extension: str, contents: str = "") -> None:
        try:
            path = self._unique_path(base_name, extension)
            path.write_text(contents, encoding="utf-8")
            self.refresh_icons_once()
        except Exception as exc:
            log(f"new file failed: {exc}", logging.WARNING)

    def _move_file_to_folder(self, src: str, dst: str):
        try:
            shutil.move(src, dst)
            self.refresh_icons_once()
        except Exception as e:
            log(f"move failed: {e}", logging.WARNING)

    def save_icon_position(self, path: str, pos: QPoint):
        st = _load_state()
        st.setdefault("icon_pos", {})[path] = [pos.x(), pos.y()]
        _save_state(st)

    def restore_icon_position(self, path: str) -> Optional[QPoint]:
        st = _load_state()
        xy = st.get("icon_pos", {}).get(path)
        if not xy: return None
        try:
            return QPoint(int(xy[0]), int(xy[1]))
        except Exception:
            return None

    def set_active_icon(self, icon: Optional[DesktopIcon]) -> None:
        if icon is self._selected_icon:
            if icon is not None and not icon.isSelected():
                icon.setSelected(True)
                self._selected_path = icon.path
            return
        if self._selected_icon:
            self._selected_icon.setSelected(False)
        self._selected_icon = icon
        if icon is None:
            self._selected_path = None
            return
        self._selected_path = icon.path
        icon.setSelected(True)

    def clear_selection(self) -> None:
        self.set_active_icon(None)

    def mousePressEvent(self, ev):  # pragma: no cover - GUI interaction
        if ev.button() == Qt.LeftButton:
            child = self.childAt(ev.position().toPoint()) if hasattr(ev, "position") else self.childAt(ev.pos())
            if not isinstance(child, DesktopIcon):
                self.clear_selection()
        super().mousePressEvent(ev)

    def dragEnterEvent(self, event):  # pragma: no cover - GUI interaction
        mime = event.mimeData()
        if mime.hasFormat(_ICON_DRAG_MIME):
            event.setDropAction(Qt.MoveAction)
            event.accept()
            return
        if self._drop_paths_from_mime(mime):
            event.setDropAction(Qt.CopyAction)
            event.accept()
            return
        event.ignore()

    def dragMoveEvent(self, event):  # pragma: no cover - GUI interaction
        mime = event.mimeData()
        if mime.hasFormat(_ICON_DRAG_MIME):
            event.setDropAction(Qt.MoveAction)
            event.accept()
            return
        if self._drop_paths_from_mime(mime):
            event.setDropAction(Qt.CopyAction)
            event.accept()
            return
        event.ignore()

    def dropEvent(self, event):  # pragma: no cover - GUI interaction
        mime = event.mimeData()
        if mime.hasFormat(_ICON_DRAG_MIME):
            try:
                path = bytes(mime.data(_ICON_DRAG_MIME)).decode("utf-8")
            except Exception:
                event.ignore()
                return
            icon = self._icons.get(path)
            if not icon:
                event.ignore()
                return
            offset = QPoint(icon.width() // 2, icon.height() // 2)
            if mime.hasFormat(_ICON_OFFSET_MIME):
                raw = bytes(mime.data(_ICON_OFFSET_MIME)).decode("utf-8")
                try:
                    ox, oy = (int(part) for part in raw.split(",", 1))
                    offset = QPoint(ox, oy)
                except Exception:
                    pass
            drop_point = (event.position().toPoint() if hasattr(event, "position") else event.pos()) - offset
            drop_point = self._clamp_to_bounds(drop_point, icon)
            snapped_point = self._snap_to_grid(drop_point)
            drop_center = event.position().toPoint() if hasattr(event, "position") else event.pos()
            target_folder: Optional[DesktopIcon] = None
            for sib in self._icons.values():
                if sib is icon:
                    continue
                if sib.geometry().contains(drop_center) and os.path.isdir(sib.path):
                    target_folder = sib
                    break
            if target_folder:
                self._register_internal_drop(icon.path)
                icon.request_move_to_folder.emit(icon.path, target_folder.path)
                self.set_active_icon(target_folder)
                event.acceptProposedAction()
                return
            icon.move(snapped_point)
            self.save_icon_position(icon.path, snapped_point)
            self.set_active_icon(icon)
            self._register_internal_drop(icon.path)
            event.acceptProposedAction()
            return

        drop_paths = self._drop_paths_from_mime(mime)
        if not drop_paths:
            event.ignore()
            return
        drop_center = event.position().toPoint() if hasattr(event, "position") else event.pos()
        target_folder: Optional[DesktopIcon] = None
        for candidate in self._icons.values():
            if not os.path.isdir(candidate.path):
                continue
            if candidate.geometry().contains(drop_center):
                target_folder = candidate
                break
        destination_dir: Optional[Path]
        if target_folder is not None:
            try:
                destination_dir = Path(target_folder.path)
            except Exception:
                destination_dir = Path(VDSK_ROOT)
        else:
            destination_dir = Path(VDSK_ROOT)
        drop_point = event.position().toPoint() if hasattr(event, "position") else event.pos()
        imported = self._import_dropped_paths(drop_paths, destination_dir, drop_point=drop_point)
        if not imported:
            event.ignore()
            return
        if target_folder is not None:
            self.set_active_icon(target_folder)
        try:
            dest_resolved = Path(destination_dir).resolve()
        except Exception:
            dest_resolved = Path(VDSK_ROOT).resolve()
        if _is_contained(str(dest_resolved)):
            for created in imported.keys():
                self._register_internal_drop(str(created))
        self.refresh_icons_once()
        if dest_resolved == Path(VDSK_ROOT).resolve():
            for created_path, preferred in imported.items():
                if preferred is None:
                    continue
                try:
                    self.save_icon_position(str(created_path), preferred)
                except Exception as exc:
                    log(f"Import position save failed for {created_path}: {exc}", logging.DEBUG)
                    continue
                icon = self._icons.get(str(created_path))
                if icon is not None:
                    try:
                        icon.move(preferred)
                    except Exception:
                        pass
        event.setDropAction(Qt.CopyAction)
        event.acceptProposedAction()

    def _drop_paths_from_mime(self, mime: QMimeData) -> List[Path]:
        paths: List[Path] = []
        if not mime.hasUrls():
            return paths
        for url in mime.urls():
            if not url.isValid() or not url.isLocalFile():
                continue
            local_path = url.toLocalFile()
            if not local_path:
                continue
            try:
                resolved = Path(local_path).expanduser().resolve()
            except Exception:
                continue
            if not resolved.exists():
                continue
            paths.append(resolved)
        return paths

    def _unique_destination_path(self, dest: Path) -> Path:
        if not dest.exists():
            return dest
        suffix = "".join(dest.suffixes)
        base_name = dest.name[:-len(suffix)] if suffix else dest.name
        parent = dest.parent
        idx = 1
        while True:
            candidate = parent / f"{base_name} ({idx}){suffix}"
            if not candidate.exists():
                return candidate
            idx += 1

    def _import_dropped_paths(
        self,
        paths: Sequence[Path],
        destination_dir: Optional[Union[str, Path]] = None,
        drop_point: Optional[QPoint] = None,
    ) -> Dict[str, Optional[QPoint]]:
        imported: Dict[str, Optional[QPoint]] = {}
        created_paths: List[Path] = []
        target_dir = destination_dir if destination_dir is not None else VDSK_ROOT
        try:
            dest_root = Path(target_dir).expanduser().resolve()
        except Exception as exc:
            log(f"Drop destination resolution failed for {target_dir}: {exc}", logging.DEBUG)
            return imported
        try:
            dest_root.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            log(f"Drop destination mkdir failed for {dest_root}: {exc}", logging.WARNING)
            return imported
        for source in paths:
            try:
                resolved = source.resolve()
            except Exception:
                continue
            if resolved == dest_root:
                continue
            if resolved.is_dir():
                try:
                    dest_root.relative_to(resolved)
                except Exception:
                    pass
                else:
                    # Prevent copying a directory that already contains the workspace root
                    continue
            destination = self._unique_destination_path(dest_root / resolved.name)
            try:
                if resolved.is_dir():
                    shutil.copytree(resolved, destination)
                else:
                    shutil.copy2(resolved, destination)
            except Exception as exc:
                log(f"Drop copy failed for {resolved}: {exc}", logging.WARNING)
                continue
            created_paths.append(destination)
        if not created_paths:
            return imported
        dest_is_desktop = False
        try:
            dest_is_desktop = dest_root == Path(VDSK_ROOT).resolve()
        except Exception:
            dest_is_desktop = False
        if not drop_point or not dest_is_desktop:
            for path in created_paths:
                imported[str(path)] = None
            return imported
        grid_w, grid_h = self._grid_size
        origin_x, origin_y = GRID_ORIGIN_X, GRID_ORIGIN_Y
        cols = max(1, int((self.width() - origin_x * 2) / grid_w))
        half_cell = QPoint(grid_w // 2, grid_h // 2)
        aligned_point = self._snap_to_grid(drop_point - half_cell)
        base_col = int(round((aligned_point.x() - origin_x) / grid_w)) if grid_w else 0
        base_row = int(round((aligned_point.y() - origin_y) / grid_h)) if grid_h else 0
        base_col = max(0, min(base_col, cols - 1))
        if grid_h:
            base_row = max(0, base_row)
        rect = self.rect()
        max_x = max(origin_x, rect.width() - grid_w)
        max_y = max(origin_y, rect.height() - grid_h)
        start_index = max(0, base_row * cols + base_col)
        for idx, path in enumerate(created_paths):
            target_index = start_index + idx
            target_row = target_index // cols if cols else 0
            target_col = target_index % cols if cols else 0
            x = origin_x + target_col * grid_w
            y = origin_y + target_row * grid_h
            x = max(origin_x, min(x, max_x))
            y = max(origin_y, min(y, max_y))
            imported[str(path)] = QPoint(x, y)
        return imported

    def _clamp_to_bounds(self, point: QPoint, icon: DesktopIcon) -> QPoint:
        rect = self.rect()
        x = max(6, min(point.x(), rect.width() - icon.width() - 6))
        y = max(30, min(point.y(), rect.height() - icon.height() - 30))
        return QPoint(x, y)

    def _snap_to_grid(self, point: QPoint) -> QPoint:
        gx, gy = self._grid_size
        origin_x, origin_y = GRID_ORIGIN_X, GRID_ORIGIN_Y
        snapped_x = int(round((point.x() - origin_x) / gx)) * gx + origin_x
        snapped_y = int(round((point.y() - origin_y) / gy)) * gy + origin_y
        return QPoint(snapped_x, snapped_y)

    def _desktop_context(self, pos: QPoint):
        m = QMenu(self)
        current_size = self._current_icon_size()
        view_m = m.addMenu("View")
        view_actions = {
            "large": view_m.addAction("Large icons"),
            "medium": view_m.addAction("Medium icons"),
            "small": view_m.addAction("Small icons"),
        }
        for key, action in view_actions.items():
            action.setCheckable(True)
            action.setChecked(current_size == key)
            action.triggered.connect(lambda _checked, size=key: self._set_icon_size(size))
        sort_m = m.addMenu("Sort by")
        for key, label in (("name", "Name"), ("type", "Type"), ("date", "Date modified")):
            act = sort_m.addAction(label)
            act.setCheckable(True)
            act.setChecked(self._sort_mode == key)
            act.triggered.connect(lambda _checked, mode=key: self._set_sort_mode(mode))
        m.addAction("Refresh", self._refresh_icons)
        m.addSeparator()
        new_m = m.addMenu("New")
        new_m.addAction("Folder", self._new_folder_desktop)
        new_m.addAction("Text Document", self._new_text_desktop)
        new_m.addAction("Markdown Document", self._new_markdown_desktop)
        new_m.addAction("JSON Document", self._new_json_desktop)
        new_m.addAction("Python File", self._new_python_desktop)
        new_m.addAction("PowerShell Script", self._new_powershell_desktop)
        new_m.addAction("ZIP Archive", self._new_zip_desktop)
        new_m.addAction("Shortcut", self._new_shortcut_desktop)
        m.addSeparator()
        pers_m = m.addMenu("Personalize")
        pers_m.addAction("Solid color", lambda: self._select_background(BackgroundMode.SOLID))
        pers_m.addAction("Image…", lambda: self._select_background(BackgroundMode.STATIC))
        pers_m.addAction("Animated GIF…", lambda: self._select_background(BackgroundMode.GIF))
        pers_m.addAction("Video…", lambda: self._select_background(BackgroundMode.VIDEO))
        pers_m.addAction("Live GL viewport…", lambda: self._select_background(BackgroundMode.GL))
        m.addSeparator()
        m.addAction("Display settings", self._open_display_settings)
        m.addAction("Desktop settings", self._open_desktop_settings)
        m.exec(self.mapToGlobal(pos))

    def _set_icon_size(self, sz: str):
        st = _load_state(); st["icon_size"] = sz; _save_state(st); self._refresh_icons()

    def _new_folder_desktop(self):
        try:
            path = self._unique_path("New Folder")
            path.mkdir()
            self._refresh_icons()
        except Exception as e:
            log(f"new folder failed: {e}", logging.WARNING)

    def _new_text_desktop(self):
        self._create_text_file("New Text Document", ".txt")

    def _new_markdown_desktop(self):
        self._create_text_file("New Markdown Document", ".md", "# New Markdown Document\n\n")

    def _new_json_desktop(self):
        self._create_text_file("New JSON Document", ".json", "{\n\n}\n")

    def _new_python_desktop(self):
        self._create_text_file(
            "New Python File",
            ".py",
            "#!/usr/bin/env python3\n\n\"\"\"New script.\"\"\"\n\n",
        )

    def _new_powershell_desktop(self):
        self._create_text_file("New PowerShell Script", ".ps1", "Write-Host 'Hello from Virtual Desktop'\n")

    def _new_zip_desktop(self):
        try:
            path = self._unique_path("New Archive", ".zip")
            with zipfile.ZipFile(path, "w") as zf:
                pass
            self._refresh_icons()
        except Exception as e:
            log(f"new zip failed: {e}", logging.WARNING)

    def _new_shortcut_desktop(self):
        try:
            path = self._unique_path("New Shortcut", ".shortcut.json")
            payload = {"target": "", "args": [], "working_dir": ""}
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            self._refresh_icons()
        except Exception as e:
            log(f"new shortcut failed: {e}", logging.WARNING)

    def _open_display_settings(self):
        core = self.parent()
        if core and hasattr(core, "_open_settings_panel"):
            core._open_settings_panel(section="display")

    def _open_desktop_settings(self):
        core = self.parent()
        if core and hasattr(core, "_open_settings_panel"):
            core._open_settings_panel(section="desktop")

    def background_config(self) -> BackgroundConfig:
        return self._bg_config

    def set_background_config(self, config: BackgroundConfig) -> None:
        self._apply_background_config(config)

    def _apply_background_config(self, config: BackgroundConfig, *, persist: bool = True) -> None:
        self._bg_config = config
        if persist:
            st = _load_state()
            st["background"] = config.to_state()
            _save_state(st)
        if config.mode == BackgroundMode.SOLID or not config.source:
            self._bg_manager.clear()
        else:
            self._bg_manager.apply(config)
        self.update()
        QApplication.processEvents()

    def _select_background(self, mode: BackgroundMode):
        config = BackgroundConfig.from_state(self._bg_config.to_state()) if self._bg_config else BackgroundConfig()
        config.mode = mode
        if mode == BackgroundMode.SOLID:
            config.source = ""
            self._apply_background_config(config)
            return
        path = self.prompt_background_path(mode)
        if not path:
            return
        config.source = path
        if mode in (BackgroundMode.STATIC, BackgroundMode.GIF) and not isinstance(config.fit, BackgroundFit):
            config.fit = BackgroundFit.FILL
        if mode == BackgroundMode.VIDEO:
            config.loop = True
            config.mute = True
        self._apply_background_config(config)

    def _validate_background_path(self, path: str) -> bool:
        core = self.parent()
        allow_external = bool(getattr(core, "allow_external_browse", lambda: False)()) if core else False
        if not _is_contained(path) and not allow_external:
            if core and hasattr(core, "_toast"):
                core._toast("Background must stay inside the workspace.")
            log(f"Blocked background outside workspace: {path}", logging.WARNING)
            return False
        return True

    def validate_background_source(self, path: str) -> bool:
        return self._validate_background_path(path)

    def _background_prompt_details(self, mode: BackgroundMode) -> Tuple[str, str]:
        filters = {
            BackgroundMode.STATIC: "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
            BackgroundMode.GIF: "GIF images (*.gif)",
            BackgroundMode.VIDEO: "Videos (*.mp4 *.mov *.mkv *.avi *.webm)",
            BackgroundMode.GL: "Python Scripts (*.py)",
        }
        captions = {
            BackgroundMode.STATIC: "Choose Background Image",
            BackgroundMode.GIF: "Choose Animated GIF",
            BackgroundMode.VIDEO: "Choose Background Video",
            BackgroundMode.GL: "Choose GL Background Script",
        }
        return filters.get(mode, "*"), captions.get(mode, "Choose Background")

    def prompt_background_path(self, mode: BackgroundMode) -> Optional[str]:
        path_filter, caption = self._background_prompt_details(mode)
        path, _ = _non_native_open_file(self, caption, VDSK_ROOT, path_filter)
        if not path:
            return None
        if not self._validate_background_path(path):
            return None
        return path

# --------------------------------------------------------------------------------------
# Camera viewport
# --------------------------------------------------------------------------------------
class Camera(QScrollArea):
    def __init__(self, content: DesktopCanvas, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWidget(content)
        self.setAcceptDrops(True)
        if self.viewport():
            self.viewport().setAcceptDrops(True)
        # Allow the scroll area to resize the canvas with the viewport so edge drags
        # on the main window immediately reflect in the desktop geometry.
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Drag-to-pan
        self._dragging = False; self._last = QPoint()
        self.viewport().installEventFilter(self)

    def center_on_widget(self, w: QWidget | None):
        if not w: return
        c = w.geometry().center()
        self.center_on_point(c)

    def center_on_point(self, pt: QPoint):
        cont = self.widget(); vw = self.viewport().size()
        x = max(0, min(pt.x() - vw.width() // 2, max(0, cont.width() - vw.width())))
        y = max(0, min(pt.y() - vw.height() // 2, max(0, cont.height() - vw.height())))
        self.horizontalScrollBar().setValue(x)
        self.verticalScrollBar().setValue(y)

    def pan(self, dx: int, dy: int):
        hs = self.horizontalScrollBar(); vs = self.verticalScrollBar()
        hs.setValue(max(hs.minimum(), min(hs.maximum(), hs.value() + dx)))
        vs.setValue(max(vs.minimum(), min(vs.maximum(), vs.value() + dy)))

    def eventFilter(self, obj, ev):
        if obj is self.viewport():
            if ev.type() == QEvent.Type.Wheel:
                delta = ev.angleDelta()
                steps = delta.y() // 120 if delta.y() else delta.x() // 120
                if ev.modifiers() & Qt.ShiftModifier:
                    self.pan(-int(steps) * 120, 0)
                else:
                    self.pan(0, -int(steps) * 120)
                return True
            if ev.type() == QEvent.MouseButtonPress and ev.button() == Qt.MiddleButton:
                self._dragging = True; self._last = ev.position().toPoint(); return True
            elif ev.type() == QEvent.MouseMove and self._dragging:
                cur = ev.position().toPoint()
                delta = cur - self._last; self._last = cur
                self.pan(-delta.x(), -delta.y()); return True
            elif ev.type() in (QEvent.MouseButtonRelease, QEvent.Leave):
                self._dragging = False
            elif ev.type() in (
                QEvent.Type.DragEnter,
                QEvent.Type.DragMove,
                QEvent.Type.Drop,
            ):
                method_map = {
                    QEvent.Type.DragEnter: "dragEnterEvent",
                    QEvent.Type.DragMove: "dragMoveEvent",
                    QEvent.Type.Drop: "dropEvent",
                }
                method = method_map.get(ev.type())
                if method and self._forward_drag_event(method, ev):
                    return True
        return super().eventFilter(obj, ev)

    # --- Drag and drop bridging -------------------------------------------------
    def _forward_drag_event(self, method: str, event) -> bool:
        canvas = self.widget()
        handler = getattr(canvas, method, None) if canvas else None
        if not callable(handler):
            return False
        try:
            handler(event)
        except Exception:
            return False
        return event.isAccepted()

    def dragEnterEvent(self, event):  # pragma: no cover - GUI interaction
        if self._forward_drag_event("dragEnterEvent", event):
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):  # pragma: no cover - GUI interaction
        if self._forward_drag_event("dragMoveEvent", event):
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event):  # pragma: no cover - GUI interaction
        if self._forward_drag_event("dropEvent", event):
            return
        super().dropEvent(event)

# --------------------------------------------------------------------------------------
# Taskbar + Start panel
# --------------------------------------------------------------------------------------
class StartPanel(QFrame):
    request_close = Signal()
    cursor_exited = Signal()
    FACETS = [
        ("all", "All"),
        ("apps", "Apps"),
        ("docs", "Docs"),
        ("images", "Images"),
        ("scripts", "Scripts"),
    ]
    _RECENT_KIND_MAP = {
        "text": "docs",
        "image": "images",
        "py_card": "scripts",
        "process": "apps",
        "template": "apps",
        "builtin": "apps",
    }

    def __init__(self, core: "VirtualDesktopCore"):
        super().__init__(core)
        self.core = core
        self.t = core.t
        self.setObjectName("StartPanel")
        self.setAutoFillBackground(False)
        self.setStyleSheet(
            f"""
            QFrame#StartPanel {{
                background:{self.t.start_panel};
                border-top:1px solid {self.t.card_border};
                border-left:1px solid {self.t.card_border};
                border-right:1px solid {self.t.card_border};
                border-top-left-radius:10px;
                border-top-right-radius:10px;
            }}
            QLabel {{ color:{self.t.menu_fg}; }}
            QLineEdit {{
                background:#0b1828; color:#eaf2ff; border:1px solid {self.t.card_border}; border-radius:6px; padding:6px 8px;
            }}
            QToolButton#FacetButton {{
                background:transparent; color:{self.t.menu_fg}; border:1px solid transparent; border-radius:6px; padding:4px 10px;
            }}
            QToolButton#FacetButton:checked {{ background:{self.t.accent}; color:#fff; border:1px solid {self.t.accent}; }}
            QListWidget#RecommendedList {{
                background:#0f1c2d; color:{self.t.menu_fg}; border:1px solid {self.t.card_border}; border-radius:8px; padding:4px;
            }}
            QListWidget#RecommendedList::item {{
                padding:6px 8px; margin:2px 2px; border-radius:6px;
            }}
            QListWidget#RecommendedList::item:hover {{ background:rgba(45, 91, 160, 0.35); }}
            QListWidget#RecommendedList::item:selected {{ background:{self.t.accent}; color:#fff; }}
            QToolButton#PinnedAppButton {{
                background:{self.t.start_tile}; color:{self.t.menu_fg}; border:1px solid {self.t.card_border}; border-radius:8px; padding:8px 6px 6px;
            }}
            QToolButton#PinnedAppButton:hover,
            QToolButton#PinnedAppButton:checked {{
                background:{self.t.accent}; color:#fff; border:1px solid {self.t.accent};
            }}
            QLabel#PinnedTypeLabel {{ color:{self.t.menu_fg}; font:600 11pt 'Cascadia Code'; padding-left:2px; }}
            QPushButton[class="RecentItem"] {{
                background:#1b4fbf; color:#fff; border:1px solid #0d214b; border-radius:6px; padding:8px 10px; text-align:left;
            }}
            QPushButton[class="RecentItem"]:hover {{ background:#2a64ff; }}
            QPushButton[class="ResultItem"] {{
                background:#162438; color:#eaf2ff; border:1px solid {self.t.card_border}; border-radius:8px; padding:6px 9px; text-align:left;
            }}
            QPushButton[class="ResultItem"]:hover {{ background:{self.t.accent}; color:#fff; }}
            QPushButton[class="Power"] {{
                background:{self.t.start_tile}; color:#dfe9ff; border:1px solid {self.t.card_border}; border-radius:8px; padding:10px 16px;
            }}
            QPushButton[class="Power"]:hover {{ background:{self.t.accent}; color:#fff; }}
            QPushButton#Shutdown {{
                background:#E04B4B; color:#fff; border:1px solid #3b0f0f; border-radius:8px; padding:10px 16px;
            }}
            QPushButton#Shutdown:hover {{ background:#ff5c5c; }}
            """
        )
        self.setMinimumHeight(580)
        self._facet = "all"
        self._workspace_items: List[Dict[str, str]] = []
        self._index_stale = True
        self._app_entries = self._build_app_entries()
        self._selected_app_id: Optional[str] = None
        self._icon_buttons: Dict[str, QToolButton] = {}
        self._cursor_inside = False
        self._focus_refresh_pending = True
        self._warm_thread: Optional[threading.Thread] = None
        self._path_icon_cache: Dict[str, QIcon] = {}

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(180)
        self._cursor_exit_timer = QTimer(self)
        self._cursor_exit_timer.setSingleShot(True)
        self._cursor_exit_timer.timeout.connect(self._on_cursor_exit_timeout)
        self.refresh_close_behavior()
        main = QVBoxLayout(self)
        main.setContentsMargins(12, 10, 12, 12)
        main.setSpacing(10)

        search_row = QHBoxLayout(); search_row.setSpacing(8)
        self.search = QLineEdit(self); self.search.setPlaceholderText("Search apps, files, and recents")
        self.search.installEventFilter(self)
        self.search.textChanged.connect(self._on_search_changed)
        self.search.returnPressed.connect(self._run_search)
        self.btn_close = QPushButton("✕"); self.btn_close.setFixedWidth(32)
        self.btn_close.clicked.connect(self.hide)
        search_row.addWidget(self.search, 1)
        search_row.addWidget(self.btn_close, 0)
        main.addLayout(search_row)

        facet_row = QHBoxLayout(); facet_row.setSpacing(6)
        self._facet_buttons: Dict[str, QToolButton] = {}
        for key, label in self.FACETS:
            btn = QToolButton(self)
            btn.setObjectName("FacetButton")
            btn.setText(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _checked, f=key: self._set_facet(f))
            if key == self._facet:
                btn.setChecked(True)
            self._facet_buttons[key] = btn
            facet_row.addWidget(btn)
        facet_row.addStretch(1)
        main.addLayout(facet_row)

        self.results_scroll = QScrollArea(self)
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setFrameShape(QFrame.NoFrame)
        self.results_scroll.setMinimumHeight(220)
        self.results_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._results_widget = QWidget(self.results_scroll)
        self._results_layout = QVBoxLayout(self._results_widget)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(6)
        self.results_scroll.setWidget(self._results_widget)
        self._show_results_placeholder()
        self.results_scroll.setVisible(False)
        main.addWidget(self.results_scroll)

        apps_header = QHBoxLayout(); apps_header.setSpacing(6)
        apps_label = QLabel("Recommended")
        apps_header.addWidget(apps_label)
        apps_header.addStretch(1)
        main.addLayout(apps_header)

        pinned_row = QHBoxLayout(); pinned_row.setSpacing(12)
        self.recommended_list = QListWidget(self)
        self.recommended_list.setObjectName("RecommendedList")
        self.recommended_list.setSelectionMode(QListWidget.SingleSelection)
        self.recommended_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.recommended_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.recommended_list.setMinimumWidth(160)
        self.recommended_list.setIconSize(QSize(24, 24))
        self.recommended_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.recommended_list.itemActivated.connect(self._on_recent_item_activated)
        pinned_row.addWidget(self.recommended_list, 2)

        right_column = QVBoxLayout(); right_column.setSpacing(6)
        self.apps_type_label = QLabel("Pinned", self)
        self.apps_type_label.setObjectName("PinnedTypeLabel")
        right_column.addWidget(self.apps_type_label, 0)
        self.apps_grid_widget = QWidget(self)
        self.apps_grid_widget.setMinimumWidth(260)
        self.apps_grid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.apps_grid_layout = QGridLayout(self.apps_grid_widget)
        self.apps_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.apps_grid_layout.setSpacing(8)
        self.apps_grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        right_column.addWidget(self.apps_grid_widget, 1)
        pinned_row.addLayout(right_column, 3)
        pinned_row.setStretch(0, 2)
        pinned_row.setStretch(1, 3)
        main.addLayout(pinned_row)
        self._rebuild_apps_views()

        self.recent_frame = QFrame(self)
        self.recent_frame.setObjectName("RecentFrame")
        self.recent_layout = QVBoxLayout(self.recent_frame)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_layout.setSpacing(6)
        self.recent_title = QLabel("Recent")
        self.recent_layout.addWidget(self.recent_title)
        main.addWidget(self.recent_frame)

        self._populate_recent()

        bottom = QHBoxLayout(); bottom.addStretch(1)
        btn_settings = QPushButton("Settings…"); btn_settings.setProperty("class", "Power")
        btn_settings.clicked.connect(self._make_click_handler(core._open_settings_panel))
        btn_console = QPushButton("System Console"); btn_console.setProperty("class", "Power")
        btn_console.clicked.connect(self._make_click_handler(core._open_system_console))
        btn_errors = QPushButton("Error Center"); btn_errors.setProperty("class", "Power")
        btn_errors.clicked.connect(self._make_click_handler(core._open_error_center))
        btn_quit = QPushButton("Shut down"); btn_quit.setObjectName("Shutdown")
        btn_quit.clicked.connect(self._make_click_handler(lambda: core.window().close() if core.window() else None))
        for b in (btn_settings, btn_console, btn_errors, btn_quit):
            b.setMinimumHeight(38)
        bottom.addWidget(btn_settings)
        bottom.addWidget(btn_console)
        bottom.addWidget(btn_errors)
        bottom.addWidget(btn_quit)
        main.addLayout(bottom)

    def enterEvent(self, event):
        self._cursor_inside = True
        self._cancel_cursor_exit_timer()
        super().enterEvent(event)

    def leaveEvent(self, event):
        was_inside = self._cursor_inside
        self._cursor_inside = False
        super().leaveEvent(event)
        if was_inside:
            self._handle_cursor_exit()

    def hideEvent(self, event):
        self._cursor_inside = False
        self._cancel_cursor_exit_timer()
        super().hideEvent(event)

    def _handle_cursor_exit(self) -> None:
        if not self.isVisible():
            return
        if not self._auto_close_enabled():
            self._cancel_cursor_exit_timer()
            return
        if self.search.hasFocus():
            self._cancel_cursor_exit_timer()
            return
        if self.underMouse():
            return
        try:
            global_pos = QCursor.pos()
        except Exception:
            self._cursor_exit_timer.stop()
            self._cursor_exit_timer.start()
            return
        local_pos = self.mapFromGlobal(global_pos)
        if not self.rect().contains(local_pos):
            self._cursor_exit_timer.stop()
            self._cursor_exit_timer.start()

    def eventFilter(self, obj, event):
        if obj is self.search and event and event.type() == QEvent.FocusIn:
            self._refresh_index_if_pending()
            self._cancel_cursor_exit_timer()
        return super().eventFilter(obj, event)

    def _auto_close_enabled(self) -> bool:
        getter = getattr(self.core, "start_panel_auto_close_enabled", None)
        if callable(getter):
            try:
                return bool(getter())
            except Exception:
                return False
        return False

    def _auto_close_delay(self) -> int:
        getter = getattr(self.core, "start_panel_auto_close_delay", None)
        if callable(getter):
            try:
                delay = int(getter())
            except Exception:
                delay = DEFAULT_START_PANEL_AUTO_DELAY_MS
            else:
                if delay <= 0:
                    delay = DEFAULT_START_PANEL_AUTO_DELAY_MS
            return delay
        return DEFAULT_START_PANEL_AUTO_DELAY_MS

    def refresh_close_behavior(self) -> None:
        delay = max(0, int(self._auto_close_delay()))
        if delay <= 0:
            delay = DEFAULT_START_PANEL_AUTO_DELAY_MS
        self._cursor_exit_timer.setInterval(delay)
        if not self._auto_close_enabled():
            self._cursor_exit_timer.stop()

    def _cancel_cursor_exit_timer(self) -> None:
        if self._cursor_exit_timer.isActive():
            self._cursor_exit_timer.stop()

    def _on_cursor_exit_timeout(self) -> None:
        if not self.isVisible():
            return
        if not self._auto_close_enabled():
            self._cancel_cursor_exit_timer()
            return
        if self.underMouse():
            return
        if self.search.hasFocus():
            self._cancel_cursor_exit_timer()
            return
        try:
            global_pos = QCursor.pos()
        except Exception:
            self.cursor_exited.emit()
            return
        local_pos = self.mapFromGlobal(global_pos)
        if not self.rect().contains(local_pos):
            self.cursor_exited.emit()

    def showEvent(self, event):
        self.refresh_close_behavior()
        self._rebuild_apps_views()
        self._populate_recent()
        self._ensure_index()
        self._run_search()
        super().showEvent(event)

    def warm_index_async(self) -> None:
        if self._warm_thread and self._warm_thread.is_alive():
            return

        def _runner():
            try:
                self._ensure_index()
            finally:
                self._warm_thread = None

        thread = threading.Thread(target=_runner, name="StartIndexWarm", daemon=True)
        self._warm_thread = thread
        thread.start()

    def mark_index_stale(self) -> None:
        self._index_stale = True
        self._focus_refresh_pending = True

    def _refresh_index_if_pending(self) -> None:
        if not self._focus_refresh_pending:
            return
        self._focus_refresh_pending = False
        self._ensure_index(force=True)

    def _build_app_entries(self) -> List[Dict[str, object]]:
        style = QApplication.style()
        entries: List[Dict[str, object]] = [
            {
                "id": "explorer",
                "title": "Desktop Explorer",
                "icon": style.standardIcon(QStyle.SP_DirIcon),
                "callback": self.core._open_explorer,
                "kind": "app",
            },
            {
                "id": "tasks",
                "title": "Tasks",
                "icon": style.standardIcon(QStyle.SP_FileDialogListView),
                "callback": self.core._open_tasks,
                "kind": "app",
            },
            {
                "id": "operators",
                "title": "Operator Manager",
                "icon": style.standardIcon(QStyle.SP_DesktopIcon),
                "callback": self.core._open_operator_manager,
                "kind": "app",
            },
            {
                "id": "codex-terminal",
                "title": "Codex Terminal",
                "icon": style.standardIcon(QStyle.SP_DesktopIcon),
                "callback": self.core.open_codex_terminal,
                "kind": "app",
            },
            {
                "id": "codex-terminal-new",
                "title": "New Codex Agent…",
                "icon": style.standardIcon(QStyle.SP_FileDialogNewFolder),
                "callback": self._launch_codex_agent_for_directory,
                "kind": "app",
            },
            {
                "id": "template-terminal",
                "title": "Template Terminal",
                "icon": style.standardIcon(QStyle.SP_ComputerIcon),
                "callback": lambda: self.core.toggle_template_terminal(True),
                "kind": "app",
            },
            {
                "id": "load-script",
                "title": "Load Script as Card…",
                "icon": style.standardIcon(QStyle.SP_FileDialogDetailedView),
                "callback": self.core._load_script_dialog,
                "kind": "app",
            },
        ]

        if self.core.has_user_guided_notes():
            notes_entry = {
                "id": "user-guided-notes",
                "title": "User-Guided Notes",
                "icon": style.standardIcon(QStyle.SP_FileDialogDetailedView),
                "callback": self.core._open_user_guided_notes,
                "kind": "app",
            }
            insert_pos = max(0, len(entries) - 1)
            entries.insert(insert_pos, notes_entry)

        system_entry = {
            "id": "system-overview",
            "title": "System Overview",
            "icon": style.standardIcon(QStyle.SP_DesktopIcon),
            "callback": self.core._open_system_overview,
            "kind": "app",
        }
        entries = [e for e in entries if e.get("id") != system_entry["id"]]
        entries.insert(2, system_entry)
        return entries

    def _launch_codex_agent_for_directory(self) -> None:
        start_dir = workspace_root()
        chosen = _non_native_open_dir(
            self,
            "Select Codex workspace",
            start_dir or SCRIPT_DIR,
        )
        if not chosen:
            return
        script_path = self.core._resolve_codex_terminal_path()
        if not script_path:
            QMessageBox.information(self, "Codex", "Codex_Terminal.py not found.")
            return
        workspace = os.path.abspath(chosen)
        previous_env = os.environ.get("CODEX_WORKSPACE")
        os.environ["CODEX_WORKSPACE"] = workspace
        icon = QApplication.style().standardIcon(QStyle.SP_DesktopIcon)
        try:
            card = self.core._load_python_as_card(
                script_path,
                persist_key=f"{script_path}:{workspace}",
                nice_title="Codex Terminal",
                task_profile="codex-terminal",
                task_icon=icon,
                task_tooltip=f"Workspace: {workspace}",
            )
        except Exception:
            if previous_env is None:
                os.environ.pop("CODEX_WORKSPACE", None)
            else:
                os.environ["CODEX_WORKSPACE"] = previous_env
            raise
        if card is None:
            if previous_env is None:
                os.environ.pop("CODEX_WORKSPACE", None)
            else:
                os.environ["CODEX_WORKSPACE"] = previous_env
            return

        def _restore_env(_=None) -> None:
            if os.environ.get("CODEX_WORKSPACE") != workspace:
                return
            if previous_env is None:
                os.environ.pop("CODEX_WORKSPACE", None)
            else:
                os.environ["CODEX_WORKSPACE"] = previous_env

        card.closed.connect(_restore_env)

    def _make_click_handler(self, callback: Callable[[], None]):
        def handler(_=False):
            self.hide()
            try:
                callback()
            except Exception as exc:
                log(f"Start launch failed: {exc}", logging.DEBUG)
        return handler

    def _rebuild_apps_views(self) -> None:
        recents = self._recent_entries()
        self.recommended_list.blockSignals(True)
        self.recommended_list.clear()
        for rec in recents:
            title = rec.get("title") or Path(rec.get("path", "")).name or "Recent Item"
            item = QListWidgetItem(title)
            icon = self._icon_for_item("Recent", rec)
            if icon:
                item.setIcon(icon)
            tooltip = rec.get("path") or rec.get("tooltip") or ""
            if tooltip:
                item.setToolTip(tooltip)
            item.setData(Qt.UserRole, rec)
            self.recommended_list.addItem(item)
        if not recents:
            placeholder = QListWidgetItem("No recommendations yet.")
            placeholder.setFlags(Qt.NoItemFlags)
            self.recommended_list.addItem(placeholder)
        self.recommended_list.blockSignals(False)
        self.apps_type_label.setText("Pinned")
        self._populate_icon_grid(None, self._selected_app_id)

    def _make_app_button(self, entry: Dict[str, object]) -> QToolButton:
        btn = QToolButton(self)
        btn.setObjectName("PinnedAppButton")
        btn.setIcon(entry.get("icon") if isinstance(entry.get("icon"), QIcon) else QIcon())
        btn.setIconSize(QSize(44, 44))
        btn.setCheckable(True)
        btn.setAutoRaise(False)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        title = str(entry.get("title") or "")
        btn.setText(title)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(96, 88)
        btn.setFocusPolicy(Qt.TabFocus)
        btn.setToolTip(title)
        btn.clicked.connect(lambda _=False, entry_id=entry.get("id"): self._handle_icon_activated(entry_id))
        return btn

    def _select_entry_by_id(self, entry_id: Optional[str]) -> None:
        if not self._app_entries:
            self._selected_app_id = None
            return
        normalized = entry_id if entry_id and self._entry_by_id(entry_id) else self._app_entries[0]["id"]
        self._selected_app_id = normalized if isinstance(normalized, str) else None
        for entry_key, button in self._icon_buttons.items():
            button.setChecked(entry_key == self._selected_app_id)

    def _populate_icon_grid(self, kind: Optional[str], selected_id: Optional[str]) -> None:
        self._clear_layout(self.apps_grid_layout)
        self._icon_buttons.clear()
        if not self._app_entries:
            self._selected_app_id = None
            return
        if kind:
            normalized = self._normalize_kind(kind)
            matching = [e for e in self._app_entries if self._normalize_kind(e.get("kind")) == normalized]
        else:
            matching = list(self._app_entries)
        if not matching:
            self._selected_app_id = None
            return
        current_id = None
        if selected_id and any(e.get("id") == selected_id for e in matching):
            current_id = selected_id
        else:
            first = matching[0].get("id")
            current_id = first if isinstance(first, str) else None
        cols = max(1, min(4, int(len(matching) ** 0.5) + 1))
        for idx, entry in enumerate(matching):
            btn = self._make_app_button(entry)
            btn.setChecked(entry.get("id") == current_id)
            row, col = divmod(idx, cols)
            self.apps_grid_layout.addWidget(btn, row, col)
            entry_id = entry.get("id")
            if isinstance(entry_id, str):
                self._icon_buttons[entry_id] = btn
        self._selected_app_id = current_id if isinstance(current_id, str) else None

    def _handle_icon_activated(self, entry_id: Optional[str]) -> None:
        if not entry_id:
            return
        entry = self._entry_by_id(entry_id)
        if not entry:
            return
        self._select_entry_by_id(entry_id)
        cb = entry.get("callback")
        if callable(cb):
            self._make_click_handler(cb)()

    def _on_recent_item_activated(self, item: QListWidgetItem) -> None:
        if not item:
            return
        payload = item.data(Qt.UserRole)
        if not isinstance(payload, dict):
            return
        callback = payload.get("callback")
        if callable(callback):
            self._make_click_handler(callback)()
            return
        path = payload.get("path") or payload.get("value")
        if path:
            self._make_click_handler(lambda p=path: self.core.open_any_path(p))()

    def _entry_by_id(self, entry_id: Optional[str]) -> Optional[Dict[str, object]]:
        if not entry_id:
            return None
        for entry in self._app_entries:
            if entry.get("id") == entry_id:
                return entry
        return None

    def _normalize_kind(self, kind: Optional[object]) -> str:
        if not kind:
            return ""
        value = str(kind).strip().lower()
        if value.endswith("s"):
            value = value[:-1]
        return value

    def _kind_label(self, kind: Optional[object]) -> str:
        normalized = self._normalize_kind(kind)
        mapping = {
            "app": "Apps",
            "doc": "Docs",
            "image": "Images",
            "script": "Scripts",
        }
        if not normalized:
            return "Pinned"
        return mapping.get(normalized, normalized.capitalize())

    def _set_facet(self, facet: str) -> None:
        if facet == self._facet:
            return
        if facet not in {f for f, _ in self.FACETS}:
            facet = "all"
        self._facet = facet
        for key, btn in self._facet_buttons.items():
            btn.setChecked(key == facet)
        self._run_search()

    def _on_search_changed(self, _text: str) -> None:
        self._search_timer.start()

    def _run_search(self) -> None:
        self._search_timer.stop()
        query = self.search.text().strip()
        if not query:
            self._clear_layout(self._results_layout)
            self._show_results_placeholder()
            self.results_scroll.setVisible(False)
            return
        self._ensure_index()
        results = self._perform_search(query)
        self._render_results(results)

    def _ensure_index(self, force: bool = False) -> bool:
        if not force and not self._index_stale and self._workspace_items:
            return False
        root = Path(self.core._workspace or VDSK_ROOT)
        self._workspace_items = self._index_workspace(root)
        self._index_stale = False
        return True

    def _index_workspace(self, root: Path) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        image_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
        doc_exts = {".txt", ".md", ".json", ".log", ".cfg", ".ini"}
        try:
            for p in root.rglob("*"):
                if p.is_dir():
                    continue
                ext = p.suffix.lower()
                if ext in image_exts:
                    kind = "image"
                elif ext == ".py":
                    kind = "script"
                elif ext in doc_exts:
                    kind = "doc"
                else:
                    kind = "file"
                items.append({"path": str(p), "title": p.name, "kind": kind})
        except Exception as exc:
            log(f"Start index failed: {exc}", logging.DEBUG)
        return items

    def _perform_search(self, query: str) -> Dict[str, List[Dict[str, object]]]:
        out: Dict[str, List[Dict[str, object]]] = {"Apps": [], "Recent": [], "Files": []}
        # Apps
        if self._facet in {"all", "apps"}:
            names = [entry["title"] for entry in self._app_entries]
            for title in self._fuzzy_names(query, names):
                entry = next((e for e in self._app_entries if e["title"] == title), None)
                if entry:
                    out["Apps"].append(entry)
        # Recent
        recents = self._recent_entries()
        filtered_recents = []
        for rec in recents:
            mapped = self._RECENT_KIND_MAP.get(rec.get("kind"), "apps")
            if self._facet in {"all", mapped}:
                filtered_recents.append(rec)
        recent_pairs = [(rec, rec.get("title") or Path(rec.get("path", "")).name) for rec in filtered_recents]
        rec_titles = [name for _, name in recent_pairs]
        for title in self._fuzzy_names(query, rec_titles):
            for rec, rec_name in recent_pairs:
                if rec_name == title:
                    out["Recent"].append(rec)
                    break
        # Files
        if self._facet in {"all", "docs", "images", "scripts"}:
            kinds = {
                "docs": {"doc"},
                "images": {"image"},
                "scripts": {"script"},
                "all": {"doc", "image", "script", "file"},
            }
            allowed = kinds.get(self._facet, kinds["all"])
            pool = [item for item in self._workspace_items if item.get("kind") in allowed]
            names = [item["title"] for item in pool]
            for title in self._fuzzy_names(query, names):
                item = next((it for it in pool if it["title"] == title), None)
                if item:
                    out["Files"].append(item)
        return out

    def _render_results(self, results: Dict[str, List[Dict[str, object]]]) -> None:
        self._clear_layout(self._results_layout)
        has_results = False
        for section in ("Apps", "Recent", "Files"):
            items = results.get(section, [])
            if not items:
                continue
            has_results = True
            header = QLabel(section)
            header.setStyleSheet("font:600 11pt 'Cascadia Code'; color:#eaf2ff;")
            self._results_layout.addWidget(header)
            for item in items[:12]:
                btn = self._make_result_button(section, item)
                self._results_layout.addWidget(btn)
        if not has_results:
            self._show_results_placeholder()
        self.results_scroll.setVisible(has_results)

    def _make_result_button(self, section: str, item: Dict[str, object]) -> QPushButton:
        btn = QPushButton(str(item.get("title", "")), self)
        btn.setProperty("class", "ResultItem")
        icon = self._icon_for_item(section, item)
        if icon:
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
        subtitle = str(item.get("path") or item.get("tooltip") or "")
        if subtitle:
            btn.setToolTip(subtitle)
        if section == "Apps":
            cb = item.get("callback") if callable(item.get("callback")) else None
        else:
            path = item.get("path") or item.get("value")
            cb = (lambda p=path: self.core.open_any_path(p)) if path else None
        if callable(cb):
            btn.clicked.connect(self._make_click_handler(cb))
        return btn

    def _normalized_item_path(self, item: Mapping[str, object]) -> Optional[str]:
        raw_path = item.get("path") or item.get("value")
        if not isinstance(raw_path, str):
            return None
        candidate = raw_path.strip()
        if not candidate:
            return None
        if candidate.startswith("(builtin") and candidate.endswith(")"):
            return None
        if "://" in candidate:
            return None
        try:
            path_obj = Path(candidate).expanduser()
        except Exception:
            return None
        if not path_obj.is_absolute():
            base = getattr(self.core, "_workspace", None) or VDSK_ROOT
            try:
                path_obj = Path(base).joinpath(path_obj)
            except Exception:
                return None
        try:
            resolved = path_obj.resolve()
        except Exception:
            try:
                resolved = Path(os.path.abspath(str(path_obj)))
            except Exception:
                return None
        return str(resolved)

    def _icon_from_item_path(self, item: Mapping[str, object]) -> Optional[QIcon]:
        kind = str(item.get("kind", ""))
        if kind.lower() == "builtin":
            return None
        normalized = self._normalized_item_path(item)
        if not normalized:
            return None
        cached = self._path_icon_cache.get(normalized)
        if cached is None:
            try:
                icon, _ = _ICON_FOR_PATH_HELPER(Path(normalized))
            except Exception:
                icon = QIcon()
            if not isinstance(icon, QIcon):
                icon = QIcon()
            cached = QIcon(icon)
            self._path_icon_cache[normalized] = cached
        return cached

    def _icon_for_item(self, section: str, item: Dict[str, object]) -> Optional[QIcon]:
        style = QApplication.style()
        path_icon = self._icon_from_item_path(item)
        if path_icon is not None and not path_icon.isNull():
            return path_icon
        if section == "Apps":
            icon = item.get("icon")
            return icon if isinstance(icon, QIcon) else style.standardIcon(QStyle.SP_FileIcon)
        kind = item.get("kind", "")
        if kind == "image":
            return style.standardIcon(QStyle.SP_FileDialogContentsView)
        if kind in {"doc", "text"}:
            return style.standardIcon(QStyle.SP_FileDialogDetailedView)
        if kind == "script":
            return style.standardIcon(QStyle.SP_FileDialogInfoView)
        if path_icon is not None and path_icon.isNull():
            return style.standardIcon(QStyle.SP_FileIcon)
        return style.standardIcon(QStyle.SP_FileIcon)

    def _recent_entries(self) -> List[Dict[str, object]]:
        st = _load_state()
        return st.get("recent", [])[:8]

    def _populate_recent(self):
        while True:
            item = self.recent_layout.takeAt(1)  # preserve title at index 0
            if not item:
                break
            if item.widget():
                item.widget().deleteLater()
        for rec in self._recent_entries():
            title = rec.get("title", "")
            path = rec.get("path", "")
            btn = QPushButton(title or path or "Recent Item", self)
            btn.setProperty("class", "RecentItem")
            btn.setToolTip(path)
            btn.clicked.connect(self._make_click_handler(lambda p=path: self.core.open_any_path(p)))
            self.recent_layout.addWidget(btn)
        if self.recent_layout.count() == 1:
            placeholder = QLabel("No recent items yet.")
            placeholder.setStyleSheet("color:#7c8cab;")
            self.recent_layout.addWidget(placeholder)

    def _fuzzy_names(self, query: str, names: List[str], limit: int = 12) -> List[str]:
        if not query:
            return names[:limit]
        picks = difflib.get_close_matches(query, names, n=limit, cutoff=0.3)
        q = query.lower()
        picks += [name for name in names if q in name.lower()]
        seen: set[str] = set()
        out: List[str] = []
        for name in picks:
            if name in seen:
                continue
            seen.add(name)
            out.append(name)
            if len(out) >= limit:
                break
        return out

    def _clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _show_results_placeholder(self) -> None:
        placeholder = QLabel("Type to search for apps or files.", self._results_widget)
        placeholder.setStyleSheet("color:#7c8cab; font:italic 10pt 'Cascadia Code';")
        self._results_layout.addWidget(placeholder)

@dataclass
class TaskGroup:
    profile: str
    button: QToolButton
    cards: List[Card]
    index: int = 0
    pinned: bool = False
    removable: bool = True
    display_name: str = ""
    launcher_id: Optional[str] = None
    icon_payload: Optional[str] = None


class Taskbar(QWidget):
    SIDES = {"bottom", "top", "left", "right"}

    request_start_menu = Signal()

    def __init__(self, theme: Theme, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.t = theme
        self._core = parent
        self._side = "bottom"
        self.setAutoFillBackground(False)
        self.setStyleSheet(f"QWidget{{background:{self.t.taskbar_bg};}}")

        self.row = QBoxLayout(QBoxLayout.LeftToRight)
        self.row.setContentsMargins(8, 4, 8, 4)
        self.row.setSpacing(6)
        self.setLayout(self.row)

        self.start_btn = QPushButton(" ⊞ Start")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet(
            f"QPushButton{{background:{self.t.accent}; color:#fff; border:none; border-radius:6px; padding:0 12px;}}"
            f"QPushButton:hover{{background:{self.t.accent_hov};}}"
        )
        self.start_btn.clicked.connect(lambda: self.request_start_menu.emit())

        self._pin_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self._pin_layout.setSpacing(6)
        self._pin_layout.setContentsMargins(0, 0, 0, 0)
        self._pin_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._pinned_holder = QWidget(self)
        self._pinned_holder.setLayout(self._pin_layout)
        self._pinned_holder.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        self.tasks = QBoxLayout(QBoxLayout.LeftToRight)
        self.tasks.setSpacing(6)
        self.tasks.setContentsMargins(0, 0, 0, 0)
        self.tasks.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._tasks_holder = QWidget(self)
        self._tasks_holder.setLayout(self.tasks)
        self._tasks_holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.clock = QLabel("")
        self.clock.setStyleSheet(f"color:{self.t.taskbar_fg}; font:600 10pt 'Cascadia Code';")
        self.clock.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.row.addWidget(self.start_btn, 0)
        self.row.addWidget(self._pinned_holder, 0)
        self.row.addWidget(self._tasks_holder, 1)
        self.row.addWidget(self.clock, 0)
        self.row.setStretch(self.row.indexOf(self._tasks_holder), 1)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_bar_menu)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()

        self._groups: Dict[str, TaskGroup] = {}
        self._card_group: Dict[Card, str] = {}
        self._pin_records: Dict[str, Dict[str, Any]] = {}
        self._pin_order: List[str] = []
        self._prune_guard = False

        self.set_side(self._side)

    def configure_pins(self, entries: Sequence[Mapping[str, Any]]) -> None:
        self._pin_records.clear()
        self._pin_order.clear()
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            profile = str(entry.get("profile", "")).strip()
            if not profile:
                continue
            title = str(entry.get("title", "")).strip() or profile.title()
            removable = bool(entry.get("removable", True))
            launcher_raw = entry.get("launcher")
            launcher = str(launcher_raw).strip() if isinstance(launcher_raw, str) and launcher_raw.strip() else profile
            icon_payload = entry.get("icon") if isinstance(entry.get("icon"), str) else None
            icon = _decode_icon(icon_payload) if icon_payload else None
            if icon is None:
                icon = _icon_for_profile(profile)
                if icon_payload is None:
                    icon_payload = _encode_icon(icon)
            group = self._ensure_group(
                profile,
                pinned=True,
                display_name=title,
                icon=icon,
                launcher=launcher,
                removable=removable,
                icon_payload=icon_payload,
            )
            self._pin_records[profile] = {
                "profile": profile,
                "title": group.display_name or title,
                "icon": group.icon_payload,
                "removable": removable,
                "launcher": group.launcher_id or launcher,
            }
            if profile not in self._pin_order:
                self._pin_order.append(profile)
            self._refresh_group_tooltip(profile)
        self._refresh_group_metrics()

    def _invoke_core(self, method: str, *args) -> None:
        core = self._core
        if core is None:
            return
        func = getattr(core, method, None)
        if callable(func):
            try:
                func(*args)
            except Exception as exc:
                log(f"Taskbar core call {method} failed: {exc}", logging.DEBUG)

    def _show_bar_menu(self, pos: QPoint) -> None:
        menu = QMenu(self)
        if hasattr(self._core, "_open_settings_panel"):
            menu.addAction("Taskbar settings…", lambda: self._invoke_core("_open_settings_panel"))
        if hasattr(self._core, "_open_explorer"):
            menu.addAction("Open Desktop Explorer", lambda: self._invoke_core("_open_explorer"))
        if hasattr(self._core, "_open_tasks"):
            menu.addAction("Open Tasks", lambda: self._invoke_core("_open_tasks", None))
        if not menu.actions():
            return
        global_pos = self.mapToGlobal(pos)
        menu.exec(global_pos)

    def _ensure_group(
        self,
        profile: str,
        *,
        pinned: bool = False,
        display_name: Optional[str] = None,
        icon: Optional[QIcon] = None,
        launcher: Optional[str] = None,
        removable: Optional[bool] = None,
        icon_payload: Optional[str] = None,
    ) -> TaskGroup:
        group = self._groups.get(profile)
        created = False
        if group is None:
            btn = QToolButton(self)
            btn.setAutoRaise(True)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setStyleSheet(
                f"QToolButton{{background:{self.t.task_btn_bg}; border:1px solid {self.t.card_border}; border-radius:8px; padding:4px;}}"
                f"QToolButton:hover{{background:{self.t.task_btn_hv};}}"
                f"QToolButton:checked{{background:{self.t.accent}; border:1px solid {self.t.accent}; color:#fff;}}"
            )
            btn.clicked.connect(lambda _=False, key=profile: self._activate_group(key))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda point, key=profile, button=btn: self._show_button_menu(key, button.mapToGlobal(point))
            )
            group = TaskGroup(profile=profile, button=btn, cards=[])
            group.launcher_id = profile
            self._groups[profile] = group
            created = True
        if pinned:
            group.pinned = True
        if removable is not None:
            group.removable = bool(removable)
        if display_name:
            group.display_name = display_name
        if launcher:
            group.launcher_id = launcher
        if icon_payload is not None:
            group.icon_payload = icon_payload
        if icon is not None and not icon.isNull():
            group.button.setIcon(icon)
            if group.pinned and not group.icon_payload:
                payload = _encode_icon(icon)
                if payload:
                    group.icon_payload = payload
        elif group.pinned and group.icon_payload:
            fallback = _decode_icon(group.icon_payload)
            if fallback:
                group.button.setIcon(fallback)
        elif created:
            group.button.setIcon(_icon_for_profile(profile))
        self._move_group_button(group)
        self._update_group_button_metrics(group)
        if group.display_name and not group.cards:
            group.button.setToolTip(group.display_name)
        return group

    def _detach_button(self, button: QToolButton) -> None:
        for layout in (self._pin_layout, self.tasks):
            idx = layout.indexOf(button)
            if idx >= 0:
                layout.takeAt(idx)

    def _move_group_button(self, group: TaskGroup) -> None:
        button = group.button
        self._detach_button(button)
        layout = self._pin_layout if group.pinned else self.tasks
        alignment = Qt.AlignHCenter if self._side in ("left", "right") else Qt.AlignVCenter
        if layout is self._pin_layout and self._side not in ("left", "right"):
            alignment = Qt.AlignVCenter
        layout.addWidget(button, 0, alignment)
        if group.pinned and group.profile not in self._pin_order:
            self._pin_order.append(group.profile)

    def _show_button_menu(self, profile: str, global_pos: QPoint) -> None:
        group = self._groups.get(profile)
        if not group:
            return
        menu = QMenu(self)
        if group.pinned:
            action = menu.addAction("Unpin from taskbar", lambda: self._unpin_profile(profile))
            action.setEnabled(group.removable)
        else:
            menu.addAction("Pin to taskbar", lambda: self._pin_profile(profile))
        if group.cards:
            menu.addSeparator()
            menu.addAction("Close all windows", lambda: self._close_group_cards(profile))
        if menu.actions():
            menu.exec(global_pos)

    def _close_group_cards(self, profile: str) -> None:
        group = self._groups.get(profile)
        if not group:
            return
        for card in list(group.cards):
            try:
                card.close()
            except Exception:
                pass

    def _pin_profile(self, profile: str) -> None:
        group = self._groups.get(profile)
        if not group or group.pinned:
            return
        group.pinned = True
        group.removable = True
        if not group.display_name:
            group.display_name = group.button.toolTip() or profile.title()
        if not group.launcher_id:
            group.launcher_id = profile
        self._move_group_button(group)
        self._store_group_icon_snapshot(group)
        self._pin_records[profile] = {
            "profile": profile,
            "title": group.display_name,
            "icon": group.icon_payload,
            "removable": True,
            "launcher": group.launcher_id,
        }
        if profile not in self._pin_order:
            self._pin_order.append(profile)
        self._refresh_group_tooltip(profile)
        self._refresh_group_metrics()
        self._sync_pin_state()

    def _unpin_profile(self, profile: str) -> None:
        group = self._groups.get(profile)
        if not group or not group.pinned or not group.removable:
            return
        group.pinned = False
        self._pin_records.pop(profile, None)
        self._pin_order = [p for p in self._pin_order if p != profile]
        if group.cards:
            self._move_group_button(group)
            self._refresh_group_tooltip(profile)
            self._refresh_group_metrics()
        else:
            self._remove_group(profile, force=True)
        self._sync_pin_state()

    def _store_group_icon_snapshot(self, group: TaskGroup) -> None:
        icon_payload = _encode_icon(group.button.icon())
        if not icon_payload:
            return
        group.icon_payload = icon_payload
        rec = self._pin_records.get(group.profile)
        if rec is None:
            rec = {
                "profile": group.profile,
                "title": group.display_name or group.profile.title(),
                "removable": group.removable,
                "launcher": group.launcher_id or group.profile,
            }
            self._pin_records[group.profile] = rec
        rec["icon"] = icon_payload

    def _sync_pin_state(self) -> None:
        core = self._core
        if core is None or not hasattr(core, "update_taskbar_pin_state"):
            return
        payload: List[Dict[str, Any]] = []
        for profile in self._pin_order:
            group = self._groups.get(profile)
            if not group or not group.pinned or not group.removable:
                continue
            rec = dict(self._pin_records.get(profile, {}))
            if not rec.get("title"):
                rec["title"] = group.display_name or profile.title()
            if not rec.get("launcher"):
                rec["launcher"] = group.launcher_id or profile
            icon_payload = rec.get("icon") or group.icon_payload or _encode_icon(group.button.icon())
            if icon_payload:
                rec["icon"] = icon_payload
            rec["profile"] = profile
            rec["removable"] = True
            payload.append(rec)
        try:
            core.update_taskbar_pin_state(payload)
        except Exception as exc:
            log(f"Persisting taskbar pins failed: {exc}", logging.DEBUG)

    def _launch_profile(self, profile: str) -> None:
        target = profile
        group = self._groups.get(profile)
        if group and group.launcher_id:
            target = group.launcher_id
        launcher = getattr(self._core, "launch_task_profile", None)
        if callable(launcher):
            try:
                launcher(target)
            except Exception as exc:
                log(f"Taskbar launch failed for {target}: {exc}", logging.DEBUG)

    def side(self) -> str:
        return self._side

    def thickness(self) -> int:
        if self._side in ("left", "right"):
            value = self.width() or self.sizeHint().width()
        else:
            value = self.height() or self.sizeHint().height()
        return int(max(0, value))

    def set_side(self, side: str) -> None:
        normalized = side if side in self.SIDES else "bottom"
        self._apply_side(normalized)
        self._refresh_group_metrics()

    def _apply_side(self, side: str) -> None:
        self._side = side
        horizontal = side in ("bottom", "top")
        if horizontal:
            self.setMinimumHeight(40)
            self.setMaximumHeight(40)
            self.setFixedHeight(40)
            self.setMinimumWidth(0)
            self.setMaximumWidth(16777215)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.row.setDirection(QBoxLayout.LeftToRight)
            self.row.setContentsMargins(8, 4, 8, 4)
            self.row.setSpacing(6)
            self._pin_layout.setDirection(QBoxLayout.LeftToRight)
            self._pin_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._pinned_holder.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            self.tasks.setDirection(QBoxLayout.LeftToRight)
            self.tasks.setSpacing(6)
            self.tasks.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._tasks_holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.row.setAlignment(self.start_btn, Qt.AlignVCenter)
            self.row.setAlignment(self._pinned_holder, Qt.AlignVCenter)
            self.row.setAlignment(self._tasks_holder, Qt.AlignVCenter)
            self.row.setAlignment(self.clock, Qt.AlignVCenter | Qt.AlignRight)
            self.clock.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.start_btn.setFixedHeight(30)
            self.start_btn.setMinimumWidth(120)
            self.start_btn.setMaximumWidth(220)
        else:
            self.setMinimumWidth(96)
            self.setMaximumWidth(96)
            self.setFixedWidth(96)
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.row.setDirection(QBoxLayout.TopToBottom)
            self.row.setContentsMargins(6, 10, 6, 10)
            self.row.setSpacing(10)
            self._pin_layout.setDirection(QBoxLayout.TopToBottom)
            self._pin_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            self._pinned_holder.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.tasks.setDirection(QBoxLayout.TopToBottom)
            self.tasks.setSpacing(6)
            self.tasks.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            self._tasks_holder.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.row.setAlignment(self.start_btn, Qt.AlignHCenter)
            self.row.setAlignment(self._pinned_holder, Qt.AlignHCenter)
            self.row.setAlignment(self._tasks_holder, Qt.AlignHCenter)
            self.row.setAlignment(self.clock, Qt.AlignHCenter)
            self.clock.setAlignment(Qt.AlignHCenter)
            self.start_btn.setFixedHeight(48)
            self.start_btn.setMinimumWidth(72)
            self.start_btn.setMaximumWidth(140)
        idx = self.row.indexOf(self._tasks_holder)
        if idx >= 0:
            self.row.setStretch(idx, 1)
        self._refresh_group_metrics()

    def _refresh_group_metrics(self) -> None:
        for group in self._groups.values():
            self._update_group_button_metrics(group)

    def _update_group_button_metrics(self, group: TaskGroup) -> None:
        btn = group.button
        if not btn:
            return
        if self._side in ("left", "right"):
            btn.setIconSize(QSize(36, 36))
            btn.setFixedSize(64, 64)
        else:
            btn.setIconSize(QSize(28, 28))
            btn.setFixedSize(44, 44)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout = self._pin_layout if group.pinned else self.tasks
        alignment = Qt.AlignHCenter if self._side in ("left", "right") else Qt.AlignVCenter
        if layout is self._pin_layout and self._side not in ("left", "right"):
            alignment = Qt.AlignVCenter
        layout.setAlignment(btn, alignment)

    def _tick(self):
        self.clock.setText(QDateTime.currentDateTime().toString("hh:mm:ss yyyy-MM-dd"))

    def add_task(self, card: Card):
        profile = getattr(card, "task_profile", None) or card.title_label.text().lower() or f"card-{id(card)}"
        icon = getattr(card, "task_icon", None)
        if icon is None or icon.isNull():
            icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
        tooltip = getattr(card, "task_tooltip", "") or card.title_label.text()
        group = self._ensure_group(profile, pinned=False)
        if not group.display_name and tooltip:
            group.display_name = tooltip
        if icon and not icon.isNull():
            group.button.setIcon(icon)
            if group.pinned and not group.icon_payload:
                payload = _encode_icon(icon)
                if payload:
                    group.icon_payload = payload
                    rec = self._pin_records.get(profile)
                    if rec is not None:
                        rec["icon"] = payload
        elif group.pinned and group.icon_payload:
            fallback = _decode_icon(group.icon_payload)
            if fallback:
                group.button.setIcon(fallback)
        if group.pinned:
            self._store_group_icon_snapshot(group)
        if tooltip:
            group.button.setToolTip(tooltip)
        elif group.display_name:
            group.button.setToolTip(group.display_name)
        group.cards.append(card)
        group.index = len(group.cards) - 1
        self._card_group[card] = profile
        group.button.setChecked(True)
        self._refresh_group_tooltip(profile)

        card.closed.connect(lambda _=None, c=card: self._remove_card(c))
        card.minimized.connect(lambda _c, c=card: self._on_card_minimized(c))
        card.restored.connect(lambda _c, c=card: self._on_card_restored(c))
        card.destroyed.connect(lambda _=None, c=card: self._remove_card(c))

    def _activate_group(self, profile: str):
        group = self._prune_invalid_cards(profile)
        if not group:
            return
        if group.index >= len(group.cards):
            group.index = max(len(group.cards) - 1, 0)
        if not group.cards:
            if group.pinned:
                self._launch_profile(profile)
            else:
                self._remove_group(profile)
            return
        if len(group.cards) == 1:
            card = group.cards[0]
            if card.isVisible() and card.window() and card.window().isActiveWindow():
                card.hide()
                self._set_group_checked(profile)
            else:
                self._show_card(card)
                group.index = 0
            return
        group.index = (group.index + 1) % len(group.cards)
        card = group.cards[group.index]
        self._show_card(card)

    def _prune_invalid_cards(self, profile: str) -> Optional[TaskGroup]:
        group = self._groups.get(profile)
        if not group:
            return None
        if getattr(self, "_prune_guard", False):
            return group
        if any(card is None for card in group.cards):
            group.cards = [c for c in group.cards if c is not None]
            if not group.cards:
                group.index = 0
                if group.pinned:
                    group.button.setChecked(False)
                    fallback = _decode_icon(group.icon_payload) if group.icon_payload else None
                    if fallback:
                        group.button.setIcon(fallback)
                    else:
                        group.button.setIcon(_icon_for_profile(profile))
                    self._refresh_group_tooltip(profile)
                else:
                    self._remove_group(profile)
                    return None
            else:
                group.index = min(group.index, len(group.cards) - 1)
                self._refresh_group_tooltip(profile)
        invalid_cards = [card for card in list(group.cards) if not _is_card_valid(card)]
        if not invalid_cards:
            return group
        self._prune_guard = True
        try:
            for invalid in invalid_cards:
                self._remove_card(invalid)
        finally:
            self._prune_guard = False
        return self._groups.get(profile)

    def _show_card(self, card: Card):
        if not _is_card_valid(card):
            self._remove_card(card)
            return
        card.show()
        card.raise_()
        card.activateWindow()
        try:
            card.restored.emit(card)
        except Exception:
            pass
        profile = self._card_group.get(card)
        if profile:
            self._set_group_checked(profile)

    def _remove_card(self, card: Card):
        profile = self._card_group.pop(card, None)
        if not profile:
            return
        group = self._groups.get(profile)
        if not group:
            return
        group.cards = [c for c in group.cards if c is not card]
        if not group.cards:
            group.index = 0
            if group.pinned:
                group.button.setChecked(False)
                fallback = _decode_icon(group.icon_payload) if group.icon_payload else None
                if fallback:
                    group.button.setIcon(fallback)
                else:
                    group.button.setIcon(_icon_for_profile(profile))
                self._refresh_group_tooltip(profile)
            else:
                self._remove_group(profile)
        else:
            group.index = min(group.index, len(group.cards) - 1)
            self._refresh_group_tooltip(profile)
            self._set_group_checked(profile)

    def _remove_group(self, profile: str, force: bool = False):
        group = self._groups.get(profile)
        if not group:
            return
        if group.pinned and not force:
            group.cards = []
            group.index = 0
            group.button.setChecked(False)
            fallback = _decode_icon(group.icon_payload) if group.icon_payload else None
            if fallback:
                group.button.setIcon(fallback)
            else:
                group.button.setIcon(_icon_for_profile(profile))
            self._refresh_group_tooltip(profile)
            return
        group = self._groups.pop(profile, None)
        if not group:
            return
        btn = group.button
        if btn:
            self._detach_button(btn)
            btn.setParent(None)
            btn.deleteLater()

    def _set_group_checked(self, profile: str):
        group = self._prune_invalid_cards(profile)
        if not group:
            return
        any_visible = any(_is_card_valid(card) and card.isVisible() for card in group.cards)
        group.button.setChecked(any_visible)

    def _on_card_minimized(self, card: Card):
        profile = self._card_group.get(card)
        if profile:
            self._set_group_checked(profile)

    def _on_card_restored(self, card: Card):
        profile = self._card_group.get(card)
        if profile:
            self._set_group_checked(profile)

    def _refresh_group_tooltip(self, profile: str):
        group = self._groups.get(profile)
        if not group:
            return
        cleaned = []
        for card in group.cards:
            if not _is_card_valid(card):
                continue
            text = card.title_label.text() if hasattr(card.title_label, "text") else card.windowTitle()
            if text:
                cleaned.append(text)
        tooltip = "\n".join(cleaned) if cleaned else (group.display_name or profile)
        group.button.setToolTip(tooltip)

# --------------------------------------------------------------------------------------
# Settings panel (pull former toolbar items here)
# --------------------------------------------------------------------------------------
class SettingsPanel(QWidget):
    def __init__(self, core: "VirtualDesktopCore"):
        super().__init__(core)
        self.core = core
        self.t = core.t
        self.setObjectName("SettingsPanel")
        self._section_frames: Dict[str, QFrame] = {}
        self._pending_section: Optional[str] = None
        self._highlight_timer = QTimer(self)
        self._highlight_timer.setSingleShot(True)
        self._highlight_timer.timeout.connect(self._clear_section_highlight)
        accent_pressed = QColor(self.t.accent).darker(125).name(QColor.HexRgb)
        self.setStyleSheet(
            f"QWidget#SettingsPanel{{background:{self.t.card_bg};border:1px solid {self.t.card_border};border-radius:10px;}}"
            f"QLabel{{color:{self.t.header_fg};}} QComboBox,QLineEdit,QPlainTextEdit,QDoubleSpinBox{{background:#0b1828;color:#eaf2ff;border:1px solid {self.t.card_border};border-radius:6px;padding:6px;}}"
            f"QCheckBox{{color:#eaf2ff;}} QPushButton{{background:{self.t.accent};color:#fff;border:1px solid {self.t.card_border};border-radius:6px;padding:6px 10px;}}"
            f"QPushButton:hover{{background:{self.t.accent_hov};}}"
            f"QPushButton:pressed{{background:{accent_pressed};}}"
            f"QFrame#SectionFrame{{background:#0b1828;border:1px solid {self.t.card_border};border-radius:8px;}}"
            f"QFrame#SectionFrame[highlighted=\"true\"]{{border:2px solid {self.t.accent};background:#12284a;}}"
        )
        main = QVBoxLayout(self)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(10)

        title = QLabel("Virtual Desktop Settings")
        title.setStyleSheet(f"color:{self.t.header_fg}; font:600 12pt 'Cascadia Code';")
        main.addWidget(title)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        main.addWidget(self.scroll, 1)

        content = QWidget(self.scroll)
        self.scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        desktop_frame, desktop_layout = self._make_section("desktop", "Desktop")
        content_layout.addWidget(desktop_frame)

        display_frame, display_layout = self._make_section("display", "Display")
        content_layout.addWidget(display_frame)
        content_layout.addStretch(1)

        icon_row = QHBoxLayout()
        icon_row.addWidget(QLabel("Icon size"))
        self.cmb_icon = QComboBox()
        self.cmb_icon.addItems(["small", "medium", "large"])
        self.cmb_icon.setCurrentText(_load_state().get("icon_size", "medium"))
        icon_row.addWidget(self.cmb_icon)
        icon_row.addStretch(1)
        desktop_layout.addLayout(icon_row)

        sort_row = QHBoxLayout()
        sort_row.addWidget(QLabel("Desktop sort order"))
        self.cmb_sort = QComboBox()
        self.cmb_sort.addItem("Name", "name")
        self.cmb_sort.addItem("Type", "type")
        self.cmb_sort.addItem("Date modified", "date")
        stored_sort = str(_load_state().get("desktop_sort", "name")).lower()
        if stored_sort not in {"name", "type", "date"}:
            stored_sort = "name"
        idx_sort = self.cmb_sort.findData(stored_sort)
        if idx_sort >= 0:
            self.cmb_sort.setCurrentIndex(idx_sort)
        sort_row.addWidget(self.cmb_sort)
        sort_row.addStretch(1)
        desktop_layout.addLayout(sort_row)

        autohide_row = QHBoxLayout()
        autohide_row.addWidget(QLabel("Taskbar autohide"))
        self.chk_autohide = QCheckBox()
        self.chk_autohide.setChecked(bool(_load_state().get("taskbar_autohide", False)))
        autohide_row.addWidget(self.chk_autohide)
        autohide_row.addStretch(1)
        desktop_layout.addLayout(autohide_row)

        side_row = QHBoxLayout()
        side_row.addWidget(QLabel("Taskbar position"))
        self.cmb_taskbar_side = QComboBox()
        for label, value in (
            ("Bottom", "bottom"),
            ("Top", "top"),
            ("Left", "left"),
            ("Right", "right"),
        ):
            self.cmb_taskbar_side.addItem(label, value)
        stored_side = str(_load_state().get("taskbar_side", "bottom")).lower()
        if stored_side not in Taskbar.SIDES:
            stored_side = "bottom"
        idx_side = self.cmb_taskbar_side.findData(stored_side)
        if idx_side >= 0:
            self.cmb_taskbar_side.setCurrentIndex(idx_side)
        side_row.addWidget(self.cmb_taskbar_side)
        side_row.addStretch(1)
        desktop_layout.addLayout(side_row)

        external_row = QHBoxLayout()
        external_row.addWidget(QLabel("Allow browsing outside workspace"))
        self.chk_external = QCheckBox()
        self.chk_external.setChecked(bool(_load_state().get("allow_external_browse", False)))
        external_row.addWidget(self.chk_external)
        external_row.addStretch(1)
        desktop_layout.addLayout(external_row)

        close_cfg = core.start_panel_close_config()
        close_row = QHBoxLayout()
        close_row.addWidget(QLabel("Start menu close behavior"))
        self.cmb_start_close = QComboBox()
        self.cmb_start_close.addItem("Click off (stay open)", "click")
        self.cmb_start_close.addItem("Auto close after delay", "auto")
        idx_close = self.cmb_start_close.findData(close_cfg.get("mode", "click"))
        if idx_close < 0:
            idx_close = 0
        self.cmb_start_close.setCurrentIndex(idx_close)
        close_row.addWidget(self.cmb_start_close)
        self.spin_start_close_delay = QSpinBox()
        self.spin_start_close_delay.setRange(1, 10)
        self.spin_start_close_delay.setSuffix(" s")
        try:
            delay_sec = int(round(close_cfg.get("auto_delay_ms", DEFAULT_START_PANEL_AUTO_DELAY_MS) / 1000))
        except Exception:
            delay_sec = int(round(DEFAULT_START_PANEL_AUTO_DELAY_MS / 1000))
        if delay_sec <= 0:
            delay_sec = 1
        delay_sec = max(1, min(10, delay_sec))
        self.spin_start_close_delay.setValue(delay_sec)
        close_row.addWidget(self.spin_start_close_delay)
        close_row.addStretch(1)
        desktop_layout.addLayout(close_row)

        self.cmb_start_close.currentIndexChanged.connect(self._update_start_close_controls)
        self._update_start_close_controls()

        bg_cfg = core.canvas.background_config()

        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("Card scale"))
        self.spin_card_scale = QDoubleSpinBox()
        self.spin_card_scale.setRange(CARD_SCALE_MIN, CARD_SCALE_MAX)
        self.spin_card_scale.setDecimals(2)
        self.spin_card_scale.setSingleStep(0.05)
        self.spin_card_scale.setKeyboardTracking(False)
        self.spin_card_scale.setValue(core.card_scale())
        self.spin_card_scale.setSuffix("×")
        scale_row.addWidget(self.spin_card_scale)
        scale_row.addStretch(1)
        display_layout.addLayout(scale_row)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Background mode"))
        self.cmb_bg_mode = QComboBox()
        self.cmb_bg_mode.addItem("Solid (gradient)", BackgroundMode.SOLID)
        self.cmb_bg_mode.addItem("Image", BackgroundMode.STATIC)
        self.cmb_bg_mode.addItem("Animated GIF", BackgroundMode.GIF)
        self.cmb_bg_mode.addItem("Video", BackgroundMode.VIDEO)
        self.cmb_bg_mode.addItem("Live GL viewport", BackgroundMode.GL)
        idx_mode = self.cmb_bg_mode.findData(bg_cfg.mode)
        if idx_mode >= 0:
            self.cmb_bg_mode.setCurrentIndex(idx_mode)
        mode_row.addWidget(self.cmb_bg_mode)
        mode_row.addStretch(1)
        display_layout.addLayout(mode_row)

        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("Background source"))
        self.bg_path_edit = QLineEdit(bg_cfg.source)
        self.bg_path_edit.setReadOnly(True)
        path_row.addWidget(self.bg_path_edit, 1)
        self.btn_bg_browse = QPushButton("Browse…")
        path_row.addWidget(self.btn_bg_browse)
        display_layout.addLayout(path_row)

        fit_row = QHBoxLayout()
        fit_row.addWidget(QLabel("Image fit"))
        self.cmb_bg_fit = QComboBox()
        self.cmb_bg_fit.addItem("Fill", BackgroundFit.FILL)
        self.cmb_bg_fit.addItem("Fit", BackgroundFit.FIT)
        self.cmb_bg_fit.addItem("Center", BackgroundFit.CENTER)
        self.cmb_bg_fit.addItem("Tile", BackgroundFit.TILE)
        idx_fit = self.cmb_bg_fit.findData(bg_cfg.fit)
        if idx_fit >= 0:
            self.cmb_bg_fit.setCurrentIndex(idx_fit)
        fit_row.addWidget(self.cmb_bg_fit)
        fit_row.addStretch(1)
        display_layout.addLayout(fit_row)

        flags_row = QHBoxLayout()
        self.chk_bg_loop = QCheckBox("Loop playback")
        self.chk_bg_loop.setChecked(bool(bg_cfg.loop))
        self.chk_bg_mute = QCheckBox("Mute audio")
        self.chk_bg_mute.setChecked(bool(bg_cfg.mute))
        flags_row.addWidget(self.chk_bg_loop)
        flags_row.addWidget(self.chk_bg_mute)
        flags_row.addStretch(1)
        display_layout.addLayout(flags_row)

        self.cmb_bg_mode.currentIndexChanged.connect(self._update_bg_controls)
        self.btn_bg_browse.clicked.connect(self._browse_background)
        self._update_bg_controls()

        action_row = QHBoxLayout()
        btn_apply = QPushButton("Apply")
        btn_close = QPushButton("Close")
        action_row.addStretch(1)
        action_row.addWidget(btn_apply)
        action_row.addWidget(btn_close)
        main.addLayout(action_row)

        btn_apply.clicked.connect(self._apply)
        btn_close.clicked.connect(self.core._close_settings)

    def _apply(self):
        st = _load_state()
        st["icon_size"] = self.cmb_icon.currentText().strip()
        st["taskbar_autohide"] = bool(self.chk_autohide.isChecked())
        side_data = self.cmb_taskbar_side.currentData()
        side_value = side_data if isinstance(side_data, str) else "bottom"
        if side_value not in Taskbar.SIDES:
            side_value = "bottom"
        st["taskbar_side"] = side_value
        st["allow_external_browse"] = bool(self.chk_external.isChecked())
        sort_data = self.cmb_sort.currentData()
        sort_value = sort_data if isinstance(sort_data, str) else str(self.cmb_sort.currentText()).lower()
        if sort_value not in {"name", "type", "date"}:
            sort_value = "name"
        st["desktop_sort"] = sort_value
        mode_data = self.cmb_start_close.currentData()
        mode_value = mode_data if isinstance(mode_data, str) else "click"
        if mode_value not in ("click", "auto"):
            mode_value = "click"
        delay_seconds = int(self.spin_start_close_delay.value())
        delay_seconds = max(1, min(10, delay_seconds))
        delay_ms = delay_seconds * 1000
        self.core.set_start_panel_close_behavior(mode_value, delay_ms, persist=False)
        st["start_panel_close"] = dict(self.core.start_panel_close_config())
        st["card_scale"] = float(self.spin_card_scale.value())
        _save_state(st)
        self.core.set_taskbar_autohide(st["taskbar_autohide"])
        self.core.set_taskbar_side(st["taskbar_side"], persist=False)
        self.core.set_allow_external_browse(st["allow_external_browse"])
        self.core.canvas._set_sort_mode(sort_value)
        self.core.set_card_scale(st["card_scale"])
        cfg = BackgroundConfig.from_state(self.core.canvas.background_config().to_state())
        mode_data = self.cmb_bg_mode.currentData()
        mode = mode_data if isinstance(mode_data, BackgroundMode) else BackgroundMode.SOLID
        cfg.mode = mode
        if mode == BackgroundMode.SOLID:
            cfg.source = ""
        else:
            cfg.source = self.bg_path_edit.text().strip()
        fit_data = self.cmb_bg_fit.currentData()
        cfg.fit = fit_data if isinstance(fit_data, BackgroundFit) else BackgroundFit.FILL
        cfg.loop = bool(self.chk_bg_loop.isChecked())
        cfg.mute = bool(self.chk_bg_mute.isChecked())
        if cfg.source and not self.core.canvas.validate_background_source(cfg.source):
            return
        self.core.canvas.set_background_config(cfg)
        self.core.canvas._refresh_icons()
        self.core.canvas._arrange_icons()
        self.core._toast("Settings applied.")
        QApplication.processEvents()

    def _current_mode(self) -> BackgroundMode:
        mode_data = self.cmb_bg_mode.currentData()
        return mode_data if isinstance(mode_data, BackgroundMode) else BackgroundMode.SOLID

    def _update_bg_controls(self):
        mode = self._current_mode()
        is_solid = mode == BackgroundMode.SOLID
        is_image = mode in (BackgroundMode.STATIC, BackgroundMode.GIF)
        is_video = mode == BackgroundMode.VIDEO
        self.bg_path_edit.setEnabled(not is_solid)
        self.btn_bg_browse.setEnabled(not is_solid)
        self.cmb_bg_fit.setEnabled(is_image)
        self.chk_bg_loop.setEnabled(mode in (BackgroundMode.GIF, BackgroundMode.VIDEO))
        self.chk_bg_mute.setEnabled(is_video)

    def _update_start_close_controls(self) -> None:
        mode = self.cmb_start_close.currentData()
        self.spin_start_close_delay.setEnabled(mode == "auto")

    def _browse_background(self):
        mode = self._current_mode()
        if mode == BackgroundMode.SOLID:
            return
        path = self.core.canvas.prompt_background_path(mode)
        if path:
            self.bg_path_edit.setText(path)

    def _make_section(self, key: str, title: str) -> Tuple[QFrame, QVBoxLayout]:
        frame = QFrame(self)
        frame.setObjectName("SectionFrame")
        frame.setProperty("highlighted", "false")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)
        header = QLabel(title)
        header.setStyleSheet(f"color:{self.t.header_fg}; font:600 11pt 'Cascadia Code';")
        layout.addWidget(header)
        self._section_frames[key] = frame
        return frame, layout

    def _set_section_highlight(self, frame: QFrame, highlighted: bool) -> None:
        frame.setProperty("highlighted", "true" if highlighted else "false")
        style = frame.style()
        if style:
            style.unpolish(frame)
            style.polish(frame)
        frame.update()

    def _clear_section_highlight(self) -> None:
        for frame in self._section_frames.values():
            self._set_section_highlight(frame, False)

    def _apply_section_focus(self) -> None:
        if not self._pending_section:
            return
        frame = self._section_frames.get(self._pending_section)
        self._pending_section = None
        if not frame:
            return
        self._clear_section_highlight()
        self._set_section_highlight(frame, True)
        self.scroll.ensureWidgetVisible(frame, 0, 48)
        focus_target = None
        for child in frame.findChildren(QWidget):
            if child.focusPolicy() != Qt.NoFocus:
                focus_target = child
                break
        if focus_target:
            focus_target.setFocus(Qt.OtherFocusReason)
        self._highlight_timer.start(1600)

    def focus_section(self, section: Optional[str]) -> None:
        if not section:
            return
        key = section.lower()
        if key not in self._section_frames:
            return
        self._pending_section = key
        QTimer.singleShot(0, self._apply_section_focus)

    def showEvent(self, event):
        super().showEvent(event)
        if self._pending_section:
            QTimer.singleShot(0, self._apply_section_focus)

# --------------------------------------------------------------------------------------
# Core desktop widget
# --------------------------------------------------------------------------------------
class VirtualDesktopCore(QWidget):
    """Embeddable desktop widget."""
    def __init__(self, workspace: Optional[str] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.t = Theme()
        self._workspace = workspace or VDSK_ROOT
        self._template_card: Optional[Card] = None
        self._tasks_card: Optional[Card] = None
        self._tasks_widget: Optional["TaskCard"] = None
        self._operator_card: Optional[Card] = None
        self._notes_card: Optional[Card] = None
        self._notes_widget: Optional[QWidget] = None
        self._notes_window: Optional[QMainWindow] = None
        self._notes_card_tag: Optional[str] = None
        self._sys_console: Optional[SystemConsole] = None
        self._error_card: Optional[Card] = None
        self._error_widget: Optional[ErrorCenterCard] = None
        self._system_card: Optional[SystemOverviewCard] = None
        st = _load_state()
        self._card_scale: float = self._clamp_card_scale(st.get("card_scale", 1.0))
        self._allow_external_browse = bool(st.get("allow_external_browse", False))
        self._taskbar_autohide = bool(st.get("taskbar_autohide", False))
        self._taskbar_side = self._normalize_taskbar_side(st.get("taskbar_side", "bottom"))
        self._start_panel_close = self._normalize_start_panel_close(st.get("start_panel_close"))
        self._taskbar_pin_state: List[Dict[str, Any]] = self._normalize_taskbar_pins(st.get("taskbar_pins"))
        tasks_dataset = os.path.join(SCRIPT_DIR, "datasets", "tasks.jsonl")
        self.task_mgr = TaskManager(tasks_dataset, self._workspace)
        if hasattr(self.task_mgr, "start_system_metrics_job"):
            try:
                self.task_mgr.start_system_metrics_job()
            except Exception:
                log("Unable to start system metrics job", logging.DEBUG)
        if hasattr(self.task_mgr, "stop_system_metrics_job"):
            self.destroyed.connect(lambda *_: self.task_mgr.stop_system_metrics_job())

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Canvas + camera
        canvas_size = self._current_screen_size()
        self.canvas = DesktopCanvas(self.t, canvas_size, self, core=self)
        self.camera = Camera(self.canvas, self)

        # Taskbar
        self.taskbar = Taskbar(self.t, self)
        self.taskbar.configure_pins(self._effective_taskbar_pins())
        self.taskbar.request_start_menu.connect(self._toggle_start_panel)
        self.taskbar.set_side(self._taskbar_side)
        self._apply_taskbar_side()

        # Docked Start panel (hidden initially)
        self.start_panel = StartPanel(self)
        self.start_panel.cursor_exited.connect(self._hide_start_panel)
        self.start_panel.hide()
        self._start_panel_filter_installed = False
        try:
            self.start_panel.warm_index_async()
        except Exception:
            pass
        self._apply_start_panel_close_behavior()
        self.destroyed.connect(lambda *_: self._remove_start_panel_click_filter())

        # Settings panel (card-like small)
        self._settings_card: Optional[Card] = None
        self._settings_panel_widget: Optional[SettingsPanel] = None

        # Automation state
        self._card_seq: int = 0
        self._card_lookup: Dict[int, Card] = {}
        self._last_focus: Optional[Card] = None

        # Debounced screen sync
        self._last_synced_size: Optional[QSize] = None
        self._force_native_taskbar_offset = False
        self._sync_timer = QTimer(self); self._sync_timer.setSingleShot(True)
        self._sync_timer.timeout.connect(self._sync_canvas_to_screen)
        QTimer.singleShot(0, self._sync_canvas_to_screen)

        # Initial workspace
        self.load_workspace(self._workspace)

    # ---------- actions ----------
    def load_workspace(self, folder: Optional[str] = None) -> None:
        folder = folder or self._workspace
        if not folder or not os.path.isdir(folder): return
        if hasattr(self.task_mgr, "set_workspace"):
            try:
                self.task_mgr.set_workspace(folder)
            except Exception:
                log("Task manager workspace update failed", logging.DEBUG)
        self.canvas._refresh_icons()

    def clear_icons(self):
        self.canvas._icons.clear()

    def _iter_cards(self) -> List[Card]:
        return [w for w in self.canvas.findChildren(Card) if isinstance(w, Card)]

    def _enforce_single_card(self, new_card: Card) -> None:
        """Ensure only ``new_card`` remains attached to the desktop."""
        for existing in list(self._iter_cards()):
            if existing is new_card:
                continue
            close = getattr(existing, "_close_card", None)
            try:
                if callable(close):
                    close()
                else:
                    existing.close()
            except Exception:
                try:
                    existing.close()
                except Exception:
                    log(
                        "Failed to close previous card during single-card enforcement",
                        logging.DEBUG,
                    )

    @staticmethod
    def _clamp_card_scale(value: object) -> float:
        try:
            scale = float(value)
        except (TypeError, ValueError):
            return 1.0
        return max(CARD_SCALE_MIN, min(scale, CARD_SCALE_MAX))

    @staticmethod
    def _normalize_taskbar_side(value: object) -> str:
        try:
            side = str(value).lower()
        except Exception:
            return "bottom"
        return side if side in Taskbar.SIDES else "bottom"

    @staticmethod
    def _normalize_start_panel_close(value: object) -> Dict[str, int]:
        config = dict(START_PANEL_CLOSE_DEFAULT)
        if isinstance(value, dict):
            mode = value.get("mode", config["mode"])
            try:
                mode_str = str(mode).lower()
            except Exception:
                mode_str = config["mode"]
            if mode_str not in ("click", "auto"):
                mode_str = config["mode"]
            delay_raw = value.get("auto_delay_ms", config["auto_delay_ms"])
            try:
                delay = int(delay_raw)
            except Exception:
                delay = config["auto_delay_ms"]
            lo = min(START_PANEL_AUTO_DELAY_MIN_MS, START_PANEL_AUTO_DELAY_MAX_MS)
            hi = max(START_PANEL_AUTO_DELAY_MIN_MS, START_PANEL_AUTO_DELAY_MAX_MS)
            delay = max(lo, min(delay, hi))
            config = {"mode": mode_str, "auto_delay_ms": delay}
        return config

    def _normalize_taskbar_pins(self, value: object) -> List[Dict[str, Any]]:
        pins: List[Dict[str, Any]] = []
        if not isinstance(value, Sequence):
            return pins
        seen: set[str] = set()
        for entry in value:
            if not isinstance(entry, Mapping):
                continue
            raw_profile = entry.get("profile")
            try:
                profile = str(raw_profile).strip()
            except Exception:
                profile = ""
            if not profile or profile in seen:
                continue
            seen.add(profile)
            title_raw = entry.get("title")
            title = str(title_raw).strip() if isinstance(title_raw, str) else ""
            if not title:
                title = profile.title()
            icon_payload = entry.get("icon") if isinstance(entry.get("icon"), str) and entry.get("icon") else None
            launcher_raw = entry.get("launcher")
            launcher = (
                str(launcher_raw).strip()
                if isinstance(launcher_raw, str) and launcher_raw.strip()
                else profile
            )
            pins.append(
                {
                    "profile": profile,
                    "title": title,
                    "icon": icon_payload,
                    "removable": True,
                    "launcher": launcher,
                }
            )
        return pins

    def _default_taskbar_pins(self) -> List[Dict[str, Any]]:
        explorer_icon = _encode_icon(_icon_for_profile("explorer"))
        return [
            {
                "profile": "explorer",
                "title": "Desktop Explorer",
                "icon": explorer_icon,
                "removable": False,
                "launcher": "explorer",
            }
        ]

    def _effective_taskbar_pins(self) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for base in self._default_taskbar_pins():
            entry = dict(base)
            profile = entry.get("profile", "")
            if isinstance(profile, str) and profile:
                seen.add(profile)
            icon_payload = entry.get("icon") if isinstance(entry.get("icon"), str) else None
            if not icon_payload:
                icon_payload = _encode_icon(_icon_for_profile(str(profile)))
                entry["icon"] = icon_payload
            entries.append(entry)
        for stored in self._taskbar_pin_state:
            profile = stored.get("profile")
            if not isinstance(profile, str) or not profile or profile in seen:
                continue
            title = stored.get("title") if isinstance(stored.get("title"), str) else ""
            if not title:
                title = profile.title()
            icon_payload = stored.get("icon") if isinstance(stored.get("icon"), str) else None
            if not icon_payload:
                icon_payload = _encode_icon(_icon_for_profile(profile))
            launcher_raw = stored.get("launcher")
            launcher = (
                str(launcher_raw).strip()
                if isinstance(launcher_raw, str) and launcher_raw.strip()
                else profile
            )
            entries.append(
                {
                    "profile": profile,
                    "title": title,
                    "icon": icon_payload,
                    "removable": True,
                    "launcher": launcher,
                }
            )
            seen.add(profile)
        return entries

    def update_taskbar_pin_state(self, entries: Sequence[Mapping[str, Any]]) -> None:
        normalized = self._normalize_taskbar_pins(entries)
        self._taskbar_pin_state = normalized
        st = _load_state()
        st["taskbar_pins"] = normalized
        _save_state(st)

    def launch_task_profile(self, profile: Optional[str]) -> None:
        if profile is None:
            return
        try:
            key = str(profile).strip()
        except Exception:
            return
        if not key:
            return
        mapping: Dict[str, Callable[[], None]] = {
            "explorer": self._open_explorer,
            "tasks": lambda: self._open_tasks(),
            "operator-manager": self._open_operator_manager,
            "codex-terminal": self.open_codex_terminal,
            "template-terminal": lambda: self.toggle_template_terminal(True),
            "error-center": self._open_error_center,
            "system-overview": self._open_system_overview,
            "notes": self._open_user_guided_notes,
            "settings": self._open_settings_panel,
        }
        callback = mapping.get(key)
        if callback is None:
            return
        try:
            callback()
        except Exception as exc:
            log(f"Taskbar launch failed for profile {key}: {exc}", logging.DEBUG)

    def start_panel_close_config(self) -> Dict[str, int]:
        return dict(self._start_panel_close)

    def start_panel_close_mode(self) -> str:
        return self._start_panel_close.get("mode", START_PANEL_CLOSE_DEFAULT["mode"])

    def start_panel_auto_close_delay(self) -> int:
        try:
            return int(self._start_panel_close.get("auto_delay_ms", DEFAULT_START_PANEL_AUTO_DELAY_MS))
        except Exception:
            return DEFAULT_START_PANEL_AUTO_DELAY_MS

    def start_panel_auto_close_enabled(self) -> bool:
        return self.start_panel_close_mode() == "auto"

    def set_start_panel_close_behavior(self, mode: str, delay_ms: int, *, persist: bool = True) -> None:
        config = self._normalize_start_panel_close({"mode": mode, "auto_delay_ms": delay_ms})
        if config != self._start_panel_close:
            self._start_panel_close = config
            if persist:
                st = _load_state()
                st["start_panel_close"] = dict(config)
                _save_state(st)
            self._apply_start_panel_close_behavior()
            return
        if persist:
            st = _load_state()
            st["start_panel_close"] = dict(config)
            _save_state(st)

    def _apply_start_panel_close_behavior(self) -> None:
        panel = getattr(self, "start_panel", None)
        if panel:
            try:
                panel.refresh_close_behavior()
            except Exception:
                pass
        if panel and panel.isVisible():
            self._install_start_panel_click_filter()
        else:
            self._remove_start_panel_click_filter()

    def _install_start_panel_click_filter(self) -> None:
        if getattr(self, "_start_panel_filter_installed", False):
            return
        app = QApplication.instance()
        if not app:
            return
        app.installEventFilter(self)
        self._start_panel_filter_installed = True

    def _remove_start_panel_click_filter(self) -> None:
        if not getattr(self, "_start_panel_filter_installed", False):
            return
        app = QApplication.instance()
        if app:
            try:
                app.removeEventFilter(self)
            except Exception:
                pass
        self._start_panel_filter_installed = False

    def eventFilter(self, obj, event):
        panel = getattr(self, "start_panel", None)
        if (
            panel
            and panel.isVisible()
            and event is not None
            and event.type() == QEvent.MouseButtonPress
            and isinstance(event, QMouseEvent)
        ):
            if self._should_close_start_panel_on_click(event):
                self._hide_start_panel()
        return super().eventFilter(obj, event)

    def _should_close_start_panel_on_click(self, event: QMouseEvent) -> bool:
        if event.button() not in (Qt.LeftButton, Qt.RightButton, Qt.MiddleButton):
            return False
        panel = getattr(self, "start_panel", None)
        if not panel or not panel.isVisible():
            return False
        try:
            global_pos = event.globalPosition().toPoint()
        except AttributeError:
            global_pos = event.globalPos()
        local = panel.mapFromGlobal(global_pos)
        return not panel.rect().contains(local)

    def card_scale(self) -> float:
        return float(self._card_scale)

    def _scaled_card_dimensions(self) -> Tuple[int, int]:
        width = max(MIN_CARD_WIDTH, int(round(BASE_CARD_WIDTH * self._card_scale)))
        height = max(MIN_CARD_HEIGHT, int(round(BASE_CARD_HEIGHT * self._card_scale)))
        return width, height

    def _apply_scale_to_card(self, card: Card, ratio: float) -> None:
        if ratio <= 0:
            return
        geom = card.geometry()
        center = geom.center()
        width = max(MIN_CARD_WIDTH, int(round(geom.width() * ratio)))
        height = max(MIN_CARD_HEIGHT, int(round(geom.height() * ratio)))
        card.resize(width, height)
        new_geom = card.geometry()
        new_geom.moveCenter(center)
        x, y = new_geom.x(), new_geom.y()
        parent = card.parentWidget()
        if parent:
            rect = parent.rect()
            max_x = max(8, rect.width() - width - 8)
            max_y = max(8, rect.height() - height - 8)
            x = max(8, min(x, max_x))
            y = max(8, min(y, max_y))
        card.move(x, y)
        setattr(card, "_vd_scale", self._card_scale)

    def set_card_scale(self, scale: float, *, persist: bool = True) -> None:
        target = self._clamp_card_scale(scale)
        if math.isclose(target, self._card_scale, rel_tol=1e-3):
            return
        previous = self._card_scale if self._card_scale else 1.0
        self._card_scale = target
        ratio = target / previous if previous else 1.0
        for card in self._iter_cards():
            self._apply_scale_to_card(card, ratio)
        if persist:
            st = _load_state()
            st["card_scale"] = self._card_scale
            _save_state(st)
        QApplication.processEvents()

    def taskbar_side(self) -> str:
        return getattr(self, "_taskbar_side", "bottom")

    def set_taskbar_side(self, side: str, *, persist: bool = True) -> None:
        normalized = self._normalize_taskbar_side(side)
        previous = getattr(self, "_taskbar_side", "bottom")
        self._taskbar_side = normalized
        self._apply_taskbar_side()
        if persist and normalized != previous:
            st = _load_state()
            st["taskbar_side"] = normalized
            _save_state(st)
        if normalized != previous:
            self._sync_canvas_to_screen()
        else:
            self._position_start_panel()

    def _apply_taskbar_side(self) -> None:
        layout = getattr(self, "_layout", None)
        if layout is None:
            return
        camera = getattr(self, "camera", None)
        taskbar = getattr(self, "taskbar", None)
        if not camera or not taskbar:
            return
        layout.removeWidget(camera)
        layout.removeWidget(taskbar)
        taskbar.set_side(self._taskbar_side)
        # reset stretches for 2x2 grid
        for row in range(2):
            layout.setRowStretch(row, 0)
        for col in range(2):
            layout.setColumnStretch(col, 0)
        side = self._taskbar_side
        if side == "top":
            layout.addWidget(taskbar, 0, 0)
            layout.addWidget(camera, 1, 0)
            layout.setRowStretch(1, 1)
            layout.setColumnStretch(0, 1)
        elif side == "bottom":
            layout.addWidget(camera, 0, 0)
            layout.addWidget(taskbar, 1, 0)
            layout.setRowStretch(0, 1)
            layout.setColumnStretch(0, 1)
        elif side == "left":
            layout.addWidget(taskbar, 0, 0)
            layout.addWidget(camera, 0, 1)
            layout.setColumnStretch(1, 1)
            layout.setRowStretch(0, 1)
        else:  # right
            layout.addWidget(camera, 0, 0)
            layout.addWidget(taskbar, 0, 1)
            layout.setColumnStretch(0, 1)
            layout.setRowStretch(0, 1)
        layout.invalidate()
        if hasattr(self, "start_panel") and self.start_panel.isVisible():
            self._position_start_panel()

    def taskbar_insets(self) -> Dict[str, int]:
        insets = {"left": 0, "top": 0, "right": 0, "bottom": 0}
        bar = getattr(self, "taskbar", None)
        if not bar:
            return insets
        if getattr(self, "_taskbar_autohide", False) and not bar.underMouse():
            thickness = 0
        else:
            thickness = bar.thickness()
        if thickness <= 0:
            return insets
        side = self._taskbar_side
        if side == "left":
            insets["left"] = thickness
        elif side == "right":
            insets["right"] = thickness
        elif side == "top":
            insets["top"] = thickness
        else:
            insets["bottom"] = thickness
        return insets

    def _position_start_panel(self) -> None:
        panel = getattr(self, "start_panel", None)
        if not panel or not panel.isVisible():
            return
        geom = self._compute_start_panel_rect(panel.size())
        panel.setGeometry(geom)
        panel.raise_()

    def _compute_start_panel_rect(self, size: QSize) -> QRect:
        side = self._taskbar_side
        core_rect = self.rect()
        taskbar_rect = self.taskbar.geometry() if self.taskbar else QRect()
        start_pos = self.taskbar.start_btn.mapTo(self, QPoint(0, 0)) if self.taskbar else QPoint(0, 0)
        start_rect = QRect(start_pos, self.taskbar.start_btn.size() if self.taskbar else QSize(0, 0))
        return self._start_panel_geometry_for_side(side, core_rect, taskbar_rect, start_rect, size)

    @staticmethod
    def _start_panel_geometry_for_side(
        side: str,
        core_rect: QRect,
        taskbar_rect: QRect,
        start_rect: QRect,
        panel_size: QSize,
    ) -> QRect:
        normalized = VirtualDesktopCore._normalize_taskbar_side(side)
        width = max(0, int(panel_size.width()))
        height = max(0, int(panel_size.height()))
        pad = 10

        def clamp(value: int, low: int, high: int) -> int:
            if high < low:
                return low
            return max(low, min(value, high))

        max_x = core_rect.width() - width - pad
        max_y = core_rect.height() - height - pad
        start_center = start_rect.center()
        if normalized in ("bottom", "top"):
            anchor_x = clamp(start_center.x() - width // 2, pad, max_x)
            if normalized == "bottom":
                anchor_y = clamp(taskbar_rect.top() - height + 2, pad, max_y)
            else:
                anchor_y = clamp(taskbar_rect.bottom() + 2, pad, max_y)
        else:
            anchor_y = clamp(start_center.y() - height // 2, pad, max_y)
            if normalized == "left":
                anchor_x = clamp(taskbar_rect.right() + 2, pad, max_x)
            else:
                anchor_x = clamp(taskbar_rect.left() - width - 2, pad, max_x)
        return QRect(anchor_x, anchor_y, width, height)

    def _attach_card(
        self,
        card: Card,
        *,
        task_profile: Optional[str] = None,
        task_icon: Optional[QIcon] = None,
        task_tooltip: Optional[str] = None,
    ) -> Card:
        self._enforce_single_card(card)
        card.setParent(self.canvas)
        card_id = self._register_card(card)
        card.setMinimumSize(MIN_CARD_WIDTH, MIN_CARD_HEIGHT)
        if card.width() <= 0 or card.height() <= 0:
            width, height = self._scaled_card_dimensions()
            card.resize(width, height)
        setattr(card, "_vd_scale", self._card_scale)
        self._center_card(card)
        card.show()
        card.raise_()
        card.activateWindow()
        tooltip = task_tooltip or self._card_title(card) or "Card"
        profile = task_profile or self._derive_task_profile(self._card_title(card))
        card.set_task_metadata(profile, task_icon, tooltip)
        card.moved.connect(lambda: self._maybe_refocus(card))
        card.closed.connect(self._on_card_closed)
        self.taskbar.add_task(card)
        self._last_focus = card
        log(f"Card added: {self._card_title(card)} (id={card_id})")
        return card

    def add_card(
        self,
        widget: QWidget,
        title: str = "Card",
        *,
        task_profile: Optional[str] = None,
        task_icon: Optional[QIcon] = None,
        task_tooltip: Optional[str] = None,
    ) -> Card:
        card = Card(self.t, title, self.canvas)
        self._enforce_single_card(card)
        widget.setParent(card.body)
        lay = QVBoxLayout(card.body); lay.setContentsMargins(10, 10, 10, 10); lay.addWidget(widget)
        tooltip = task_tooltip or title
        profile = task_profile or self._derive_task_profile(title)
        return self._attach_card(card, task_profile=profile, task_icon=task_icon, task_tooltip=tooltip)

    def _derive_task_profile(self, title: str) -> str:
        base = title.split("—")[0].strip().lower() if title else "card"
        base = base.replace(" ", "-") or "card"
        return base

    def _center_card(self, card: Card) -> None:
        canvas = self.canvas
        if not canvas:
            return
        viewport = self.camera.viewport() if self.camera else None
        h_scroll = self.camera.horizontalScrollBar() if self.camera else None
        v_scroll = self.camera.verticalScrollBar() if self.camera else None
        offset_x = h_scroll.value() if h_scroll else 0
        offset_y = v_scroll.value() if v_scroll else 0
        if viewport:
            vw = viewport.size()
            cx = offset_x + vw.width() // 2 - card.width() // 2
            cy = offset_y + vw.height() // 2 - card.height() // 2
        else:
            rect = canvas.rect()
            cx = rect.center().x() - card.width() // 2
            cy = rect.center().y() - card.height() // 2
        bounds = canvas.rect()
        max_x = bounds.width() - card.width() - 8
        max_y = bounds.height() - card.height() - 8
        x = max(8, min(cx, max_x))
        y = max(8, min(cy, max_y))
        card.move(x, y)

    def _bring_card_forward(self, card: Card):
        try:
            card.show(); card.raise_(); card.activateWindow()
            self.raise_(); self.activateWindow()
            self.camera.center_on_widget(card)
        except Exception:
            pass

    def _maybe_refocus(self, w: QWidget):
        self.camera.center_on_widget(w)

    def _maybe_clear_focus(self, w: QWidget):
        if getattr(self, "_last_focus", None) is w:
            self._last_focus = None

    def _register_card(self, card: Card) -> int:
        self._card_seq += 1
        card_id = self._card_seq
        setattr(card, "_automation_id", card_id)
        self._card_lookup[card_id] = card
        try:
            card.destroyed.connect(lambda _=None, ident=card_id: self._card_lookup.pop(ident, None))
        except Exception:
            pass
        return card_id

    def _card_title(self, card: Card) -> str:
        if hasattr(card, "title_label") and card.title_label.text():
            return str(card.title_label.text())
        title = card.windowTitle() if hasattr(card, "windowTitle") else ""
        return str(title or "")

    @Slot(object)
    def _on_card_closed(self, card: object) -> None:
        if not isinstance(card, Card):
            return
        self._maybe_clear_focus(card)
        card_id = getattr(card, "_automation_id", None)
        if isinstance(card_id, int):
            self._card_lookup.pop(card_id, None)

    def taskbar_offset(self) -> int:
        return int(self.taskbar_insets().get("bottom", 0))

    def set_taskbar_autohide(self, enabled: bool) -> None:
        self._taskbar_autohide = bool(enabled)

    def allow_external_browse(self) -> bool:
        return bool(getattr(self, "_allow_external_browse", False))

    def set_allow_external_browse(self, enabled: bool) -> None:
        self._allow_external_browse = bool(enabled)

    def has_user_guided_notes(self) -> bool:
        return _USER_GUIDED_NOTES_FACTORY is not None

    def mark_start_index_stale(self) -> None:
        panel = getattr(self, "start_panel", None)
        if panel and hasattr(panel, "mark_index_stale"):
            panel.mark_index_stale()

    def _current_screen(self) -> Optional["QScreen"]:
        win = self.window()
        screen = None
        if win and hasattr(win, "windowHandle"):
            try:
                handle = win.windowHandle()
            except Exception:
                handle = None
            if handle is not None:
                try:
                    screen = handle.screen()
                except Exception:
                    screen = None
        if screen is None:
            try:
                global_pos = self.mapToGlobal(self.rect().center())
            except Exception:
                global_pos = QPoint()
            screen = QGuiApplication.screenAt(global_pos)
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        return screen

    def _current_screen_size(self) -> QSize:
        screen = self._current_screen()
        if screen is None:
            return QSize(0, 0)
        geom = screen.geometry()
        return geom.size()

    def set_force_native_taskbar_offset(self, enabled: bool) -> None:
        self._force_native_taskbar_offset = bool(enabled)

    def _sync_canvas_to_screen(self, force_native_taskbar: bool = False):
        if force_native_taskbar:
            self._force_native_taskbar_offset = True
        screen = self._current_screen()
        is_fullscreen = self._is_borderless_fullscreen()
        is_maximized = self._is_window_maximized()
        use_screen_bounds = is_fullscreen or is_maximized

        top_margin = 0
        bottom_margin = 0
        adjusted = QSize()

        if use_screen_bounds:
            geom = None
            available = None
            if screen is not None:
                try:
                    geom = screen.geometry()
                except Exception:
                    geom = None
                try:
                    available = screen.availableGeometry()
                except Exception:
                    available = None
            if geom is not None:
                base_width = geom.width()
                base_height = geom.height()
            else:
                base_size = self._current_screen_size()
                base_width = base_size.width()
                base_height = base_size.height()

            if is_fullscreen:
                target_width = base_width
                target_height = base_height
                top_margin = 0
                bottom_margin = 0
            else:
                target_width = base_width
                if geom is not None and available is not None:
                    top_margin = max(0, available.top() - geom.top())
                    bottom_margin = max(0, geom.bottom() - available.bottom())
                    target_width = available.width()
                should_use_native_taskbar = (
                    is_maximized
                    and screen is not None
                    and (
                        self._force_native_taskbar_offset
                        or self._should_use_native_taskbar_offset()
                    )
                )
                if should_use_native_taskbar:
                    try:
                        native_offset = int(self._native_windows_taskbar_height())
                    except Exception:
                        native_offset = 0
                    bottom_margin = max(bottom_margin, native_offset)
                target_height = max(0, base_height - top_margin - bottom_margin)
                if is_maximized and geom is not None and available is not None:
                    target_height = min(target_height, available.height())
            adjusted = QSize(max(0, target_width), target_height)
        else:
            camera = getattr(self, "camera", None)
            viewport_size = QSize()
            if camera is not None:
                try:
                    viewport = camera.viewport()
                except Exception:
                    viewport = None
                if viewport is not None:
                    viewport_size = viewport.size()
                if (not viewport_size.isValid() or viewport_size.isEmpty()) and hasattr(camera, "size"):
                    try:
                        viewport_size = camera.size()
                    except Exception:
                        viewport_size = QSize()
            if not viewport_size.isValid() or viewport_size.isEmpty():
                viewport_size = self.size()
            adjusted = QSize(max(0, viewport_size.width()), max(0, viewport_size.height()))

        layout = getattr(self, "_layout", None)
        if layout is not None:
            layout_top_margin = top_margin
            layout_bottom_margin = bottom_margin
            side = self.taskbar_side()
            if side in ("bottom", "top"):
                taskbar = getattr(self, "taskbar", None)
                thickness = 0
                if taskbar is not None and hasattr(taskbar, "thickness"):
                    try:
                        thickness = int(taskbar.thickness())
                    except Exception:
                        thickness = 0
                if thickness <= 0:
                    thickness = 40
                if side == "bottom" and bottom_margin > 0:
                    layout_bottom_margin = max(0, int(bottom_margin) - thickness)
                if side == "top" and top_margin > 0:
                    layout_top_margin = max(0, int(top_margin) - thickness)
            layout_top_margin = int(layout_top_margin)
            layout_bottom_margin = int(layout_bottom_margin)
            margins = layout.contentsMargins()
            if (
                margins.left() != 0
                or margins.top() != layout_top_margin
                or margins.right() != 0
                or margins.bottom() != layout_bottom_margin
            ):
                layout.setContentsMargins(0, layout_top_margin, 0, layout_bottom_margin)
        if self._last_synced_size and adjusted == self._last_synced_size:
            return
        self._last_synced_size = QSize(adjusted)
        self.canvas.resize(adjusted)
        self.camera.center_on_widget(self.canvas)
        log(f"Canvas synced to screen: {adjusted.width()}x{adjusted.height()}")

    def _should_use_native_taskbar_offset(self) -> bool:
        if self.taskbar_side() != "bottom":
            return False
        if self._is_borderless_fullscreen():
            return False
        return self._is_window_maximized()

    def _is_borderless_fullscreen(self) -> bool:
        win = self.window()
        if not win:
            return False
        try:
            return bool(win.isFullScreen())
        except Exception:
            return False

    def _is_window_maximized(self) -> bool:
        win = self.window()
        if not win:
            return False
        try:
            if hasattr(win, "isMaximized") and win.isMaximized():
                return True
        except Exception:
            return False
        try:
            state = win.windowState() if hasattr(win, "windowState") else None
        except Exception:
            state = None
        if state is None:
            return False
        try:
            return bool(state & Qt.WindowMaximized)
        except Exception:
            return False

    @staticmethod
    def _native_windows_taskbar_height() -> int:
        return _query_windows_taskbar_height()

    def _toast(self, msg: str, *, kind: str = "info"):
        box = QWidget()
        box.setAttribute(Qt.WA_StyledBackground, True)
        v = QVBoxLayout(box); v.setContentsMargins(12, 12, 12, 12); v.setSpacing(4)
        lab = QLabel(msg)
        lab.setWordWrap(True)
        if kind == "error":
            box.setStyleSheet("background:#3a0f19; border:1px solid #ff6d88; border-radius:12px;")
            lab.setStyleSheet("color:#ffeef4; font:600 10pt 'Cascadia Code';")
            icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical)
            title = "Blocked"
            profile = "toast-blocked"
            timeout = 3200
        else:
            box.setStyleSheet("background:#0f1d33; border:1px solid #2f72ff; border-radius:12px;")
            lab.setStyleSheet("color:#eaf2ff; font:600 10pt 'Cascadia Code';")
            icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation)
            title = "Notice"
            profile = "toast"
            timeout = 2000
        v.addWidget(lab)
        card = self.add_card(box, title, task_profile=profile, task_icon=icon, task_tooltip=msg)
        timer = QTimer(self)
        timer.setSingleShot(True)
        cleaned = False
        close_card = _make_guarded_card_method(card, "_close_card")

        def _cleanup_timer() -> None:
            nonlocal cleaned
            if cleaned:
                return
            cleaned = True
            try:
                if timer.isActive():
                    timer.stop()
            except Exception:
                pass
            timer.deleteLater()

        def _close_card_if_valid() -> None:
            try:
                close_card()
            finally:
                _cleanup_timer()

        timer.timeout.connect(_close_card_if_valid)

        def _cancel_timer_on_destroyed(*_args: object) -> None:
            _cleanup_timer()

        try:
            card.destroyed.connect(_cancel_timer_on_destroyed)
        except Exception:
            pass

        timer.start(timeout)
        log(f"Toast[{kind}]: {msg}")

    # ---------- Automation hooks ----------
    def list_cards(self) -> List[Dict[str, object]]:
        """Return metadata for all open cards in a deterministic order."""
        cards: List[Dict[str, object]] = []
        for card in sorted(self._iter_cards(), key=lambda c: getattr(c, "_automation_id", 0)):
            card_id = getattr(card, "_automation_id", None)
            if not isinstance(card_id, int):
                card_id = self._register_card(card)
            cards.append(self._serialize_card(card, card_id))
        return cards

    def _serialize_card(self, card: Card, card_id: int) -> Dict[str, object]:
        title = self._card_title(card)
        geometry = {
            "card": _widget_geometry_snapshot(card),
            "header": _widget_geometry_snapshot(getattr(card, "header", None)),
            "body": _widget_geometry_snapshot(getattr(card, "body", None)),
        }
        data: Dict[str, object] = {
            "id": card_id,
            "title": title,
            "profile": getattr(card, "task_profile", ""),
            "tooltip": getattr(card, "task_tooltip", title),
            "persist_tag": getattr(card, "_persist_tag", None),
            "visible": bool(card.isVisible()),
            "maximized": bool(getattr(card, "_maximized", False)),
            "geometry": geometry,
        }
        return data

    def focus_card(self, identifier: Union[int, str]) -> bool:
        """Focus the first card matching the identifier (id or title)."""
        target: Optional[Card] = None
        if isinstance(identifier, int):
            target = self._card_lookup.get(identifier)
        else:
            name = str(identifier or "").strip()
            if not name:
                return False
            # Prefer exact match, then case-insensitive, then substring
            for card in self._iter_cards():
                if self._card_title(card) == name:
                    target = card
                    break
            if target is None:
                lowered = name.lower()
                for card in self._iter_cards():
                    if self._card_title(card).lower() == lowered:
                        target = card
                        break
            if target is None:
                lowered = name.lower()
                for card in self._iter_cards():
                    if lowered in self._card_title(card).lower():
                        target = card
                        break
        if target is None:
            return False
        if not target.isVisible():
            target.show()
        self._bring_card_forward(target)
        self._last_focus = target
        return True

    def list_icons(self) -> List[Dict[str, object]]:
        """List desktop icons with geometry suitable for automation."""
        icons: List[Dict[str, object]] = []
        icon_widgets = getattr(self.canvas, "_icons", {})
        for path in sorted(icon_widgets.keys()):
            widget = icon_widgets.get(path)
            if widget is None:
                continue
            entry: Dict[str, object] = {
                "path": path,
                "title": widget.text() if hasattr(widget, "text") else os.path.basename(path),
                "kind": "folder" if os.path.isdir(path) else "file",
                "geometry": _widget_geometry_snapshot(widget),
            }
            icons.append(entry)
        return icons

    def open(self, path: str) -> Dict[str, object]:
        """Open a path inside the Virtual Desktop and report success."""
        result: Dict[str, object] = {"success": False, "card_id": None, "path": path}
        if not path:
            result["error"] = "empty path"
            return result
        target = path
        if not os.path.isabs(target):
            base = self._workspace or VDSK_ROOT
            target = os.path.join(base, path)
        target = os.path.abspath(target)
        result["resolved_path"] = target
        if not os.path.exists(target):
            result["error"] = "path not found"
            return result
        before = set(self._card_lookup.keys())
        try:
            self.open_any_path(target)
        except Exception as exc:
            log(f"Automation open failed: {exc}", logging.WARNING)
            result["error"] = str(exc)
            return result
        app = QApplication.instance()
        if app is not None:
            try:
                app.processEvents()
            except Exception:
                pass
        after = set(self._card_lookup.keys())
        new_ids = sorted(after - before)
        result["success"] = True
        if new_ids:
            result["card_id"] = new_ids[-1]
        return result

    def search(self, query: str, facet: Optional[str] = None) -> Dict[str, object]:
        """Run the Start menu search without mutating UI state."""
        panel = getattr(self, "start_panel", None)
        if panel is None:
            return {"query": query, "facet": facet or "all", "Apps": [], "Recent": [], "Files": []}
        q = (query or "").strip()
        if not q:
            return {"query": q, "facet": facet or panel._facet, "Apps": [], "Recent": [], "Files": []}
        allowed = {key for key, _ in getattr(panel, "FACETS", [])}
        prev_facet = panel._facet
        facet_to_use = prev_facet
        if facet:
            candidate = str(facet).strip().lower()
            facet_to_use = candidate if candidate in allowed else "all"
        try:
            panel._facet = facet_to_use
            panel._ensure_index()
            results = panel._perform_search(q)
        finally:
            panel._facet = prev_facet
        return self._serialize_search_results(results, facet_to_use, q)

    def _serialize_search_results(
        self, results: Dict[str, List[Dict[str, object]]], facet: str, query: str
    ) -> Dict[str, object]:
        payload: Dict[str, object] = {"query": query, "facet": facet, "Apps": [], "Recent": [], "Files": []}
        apps_serialized: List[Dict[str, object]] = []
        for item in results.get("Apps", []):
            apps_serialized.append(
                {
                    "id": str(item.get("id", "")),
                    "title": str(item.get("title", "")),
                    "tooltip": str(item.get("tooltip", item.get("title", ""))),
                }
            )
        payload["Apps"] = apps_serialized
        recent_serialized: List[Dict[str, object]] = []
        for item in results.get("Recent", []):
            entry: Dict[str, object] = {
                "title": str(item.get("title") or item.get("path") or ""),
                "path": str(item.get("path", "")),
                "kind": str(item.get("kind", "")),
            }
            if item.get("ts") is not None:
                try:
                    entry["ts"] = int(item.get("ts"))
                except Exception:
                    pass
            recent_serialized.append(entry)
        payload["Recent"] = recent_serialized
        files_serialized: List[Dict[str, object]] = []
        for item in results.get("Files", []):
            files_serialized.append(
                {
                    "title": str(item.get("title", "")),
                    "path": str(item.get("path", "")),
                    "kind": str(item.get("kind", "")),
                }
            )
        payload["Files"] = files_serialized
        return payload

    def geometry_snapshot(self) -> Dict[str, object]:
        """Provide geometry for key widgets (camera, taskbar, start)."""
        snapshot: Dict[str, object] = {
            "workspace_root": self._workspace or VDSK_ROOT,
            "taskbar_autohide": bool(self._taskbar_autohide),
            "taskbar_offset": self.taskbar_offset(),
            "taskbar_side": self.taskbar_side(),
            "core": _widget_geometry_snapshot(self),
            "camera": _widget_geometry_snapshot(self.camera),
            "camera_viewport": _widget_geometry_snapshot(self.camera.viewport() if self.camera else None),
            "canvas": _widget_geometry_snapshot(self.canvas),
            "taskbar": _widget_geometry_snapshot(self.taskbar),
            "start_button": _widget_geometry_snapshot(self.taskbar.start_btn if self.taskbar else None),
        }
        snapshot["start_panel"] = _widget_geometry_snapshot(self.start_panel if self.start_panel.isVisible() else None)
        snapshot["cards"] = self.list_cards()
        snapshot["icons"] = self.list_icons()
        return snapshot

    # ---------- Start panel ----------
    def _hide_start_panel(self) -> None:
        if getattr(self, "start_panel", None) and self.start_panel.isVisible():
            self.start_panel.hide()
        self._remove_start_panel_click_filter()

    def _toggle_start_panel(self):
        if self.start_panel.isVisible():
            self._hide_start_panel()
            return
        horizontal = self._taskbar_side in ("bottom", "top")
        thickness = self.taskbar.thickness() if self.taskbar else 0
        available_width = self.width() - (thickness if not horizontal else 0) - 30
        available_height = self.height() - (thickness if horizontal else 0) - 30
        available_width = max(200, available_width)
        available_height = max(200, available_height)
        min_size = self.start_panel.minimumSize().expandedTo(self.start_panel.minimumSizeHint())
        min_width = max(0, min_size.width())
        min_height = max(0, min_size.height())
        if horizontal:
            base_width = min(780, max(260, available_width))
            base_height = max(240, int(self.height() * 0.55))
        else:
            base_width = min(560, max(240, available_width))
            base_height = max(260, available_height)
        width = max(base_width, min_width)
        height = max(base_height, min_height)
        width = min(width, available_width)
        height = min(height, available_height)
        panel_size = QSize(int(width), int(height))
        geom = self._compute_start_panel_rect(panel_size)
        self.start_panel.setParent(self)
        self.start_panel.setProperty("side", self._taskbar_side)
        panel_style = self.start_panel.style()
        if panel_style:
            panel_style.unpolish(self.start_panel)
            panel_style.polish(self.start_panel)
        self.start_panel.setGeometry(geom)
        self._apply_start_panel_close_behavior()
        self.start_panel._rebuild_apps_views()
        self.start_panel._populate_recent()
        self.start_panel.show()
        self.start_panel.raise_()
        self._install_start_panel_click_filter()

    # ---------- Settings ----------
    def _open_settings_panel(self, section: Optional[str] = None):
        if self._settings_card and self._settings_card.isVisible():
            self._bring_card_forward(self._settings_card)
            if section and isinstance(self._settings_panel_widget, SettingsPanel):
                self._settings_panel_widget.focus_section(section)
            return
        panel = SettingsPanel(self)
        self._settings_panel_widget = panel
        settings_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        self._settings_card = self.add_card(
            panel,
            "Virtual Desktop Settings",
            task_profile="settings",
            task_icon=settings_icon,
            task_tooltip="Virtual Desktop Settings",
        )
        tag = "(builtin:settings)"
        self._settings_card.set_persist_tag(tag)
        _restore_card_geom(self._settings_card, "template", tag)
        self._settings_card.moved.connect(lambda: _save_card_geom(self._settings_card, "template", tag))
        self._settings_card.resized.connect(lambda: _save_card_geom(self._settings_card, "template", tag))
        self._settings_card.closed.connect(lambda _=None: self._on_settings_closed())
        if section:
            panel.focus_section(section)

    def _close_settings(self):
        if self._settings_card:
            self._settings_card._close_card()
        self._on_settings_closed()

    def _on_settings_closed(self) -> None:
        self._settings_card = None
        self._settings_panel_widget = None

    # ---------- App launchers ----------
    def _load_script_dialog(self):
        path, _ = _non_native_open_file(self, "Load Script as Card…", self._workspace or SCRIPT_DIR,
                                        "Python (*.py);;Executables (*.exe *.bat *.cmd *.sh);;All files (*.*)")
        if not path: return
        self.open_any_path(path)

    def open_any_path(self, path: str):
        if not path:
            return
        resolved = os.path.abspath(path)
        if not _is_contained(resolved) and not self.allow_external_browse():
            self._toast("Blocked: path is outside the Virtual Desktop workspace.", kind="error")
            log(f"Blocked open outside workspace: {resolved}", logging.WARNING)
            return
        if os.path.isdir(resolved):
            widget = ExplorerCard(resolved, self.open_any_path, self.t, refresh_hook=self.canvas._refresh_icons)
            explorer_icon = QApplication.style().standardIcon(QStyle.SP_DirIcon)
            card = self.add_card(
                widget,
                f"Explorer — {os.path.basename(resolved) or resolved}",
                task_profile="explorer",
                task_icon=explorer_icon,
                task_tooltip=resolved,
            )
            tag = f"(explorer:{resolved})"
            card.set_persist_tag(tag)
            _restore_card_geom(card, "template", tag)
            card.moved.connect(lambda: _save_card_geom(card, "template", tag))
            card.resized.connect(lambda: _save_card_geom(card, "template", tag))
            self._bring_card_forward(card)
            self.mark_start_index_stale()
            return

        ext = os.path.splitext(resolved)[1].lower()
        if ext in {".txt", ".md", ".log", ".ini", ".cfg", ".json"}:
            widget = TextViewer(resolved, self.t)
            title = f"Text — {os.path.basename(resolved)}"
            text_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView)
            card = self.add_card(
                widget,
                title,
                task_profile="text-viewer",
                task_icon=text_icon,
                task_tooltip=resolved,
            )
            tag = resolved
            card.set_persist_tag(tag)
            _restore_card_geom(card, "text", tag)
            card.moved.connect(lambda: _save_card_geom(card, "text", tag))
            card.resized.connect(lambda: _save_card_geom(card, "text", tag))
            self._bring_card_forward(card)
            _remember_card("text", resolved, title)
        elif ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}:
            widget = ImageViewer(resolved, self.t)
            title = f"Image — {os.path.basename(resolved)}"
            image_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogContentsView)
            card = self.add_card(
                widget,
                title,
                task_profile="image-viewer",
                task_icon=image_icon,
                task_tooltip=resolved,
            )
            tag = resolved
            card.set_persist_tag(tag)
            _restore_card_geom(card, "image", tag)
            card.moved.connect(lambda: _save_card_geom(card, "image", tag))
            card.resized.connect(lambda: _save_card_geom(card, "image", tag))
            self._bring_card_forward(card)
            _remember_card("image", resolved, title)
        elif ext == ".py":
            if self._load_python_as_card(resolved, persist_key=resolved) is None:
                self._load_process_card(resolved, os.path.basename(resolved), persist_key=resolved)
        else:
            self._load_process_card(resolved, os.path.basename(resolved), persist_key=resolved)
        self.mark_start_index_stale()
        QApplication.processEvents()

    def _call_factory(self, factory):
        sig = inspect.signature(factory)
        if "embedded" in sig.parameters:
            return factory(None, embedded=True)
        return factory(None)

    def _instantiate_card_from_factory(
        self,
        factory: Callable[..., object],
        *,
        default_title: str,
        task_profile: Optional[str] = None,
        task_icon: Optional[QIcon] = None,
        task_tooltip: Optional[str] = None,
    ) -> Tuple[Card, Dict[str, object]]:
        output = self._call_factory(factory)
        title = default_title
        profile = task_profile
        icon = task_icon
        tooltip = task_tooltip
        metadata: Dict[str, object] = {}

        payload: object = output
        extras: Sequence[object] = []
        if isinstance(output, (list, tuple)):
            seq = list(output)
            payload = seq[0] if seq else None
            extras = seq[1:]
            if extras and isinstance(extras[0], str):
                maybe_title = extras[0].strip()
                if maybe_title:
                    title = maybe_title
                extras = extras[1:]
            if extras and isinstance(extras[0], Mapping):
                meta_map = dict(extras[0])
                maybe_title = meta_map.get("title")
                if isinstance(maybe_title, str) and maybe_title.strip():
                    title = maybe_title.strip()
                maybe_profile = meta_map.get("task_profile")
                if isinstance(maybe_profile, str) and maybe_profile.strip():
                    profile = maybe_profile.strip()
                maybe_tooltip = meta_map.get("task_tooltip")
                if isinstance(maybe_tooltip, str) and maybe_tooltip.strip():
                    tooltip = maybe_tooltip.strip()
                maybe_icon = meta_map.get("task_icon")
                if isinstance(maybe_icon, QIcon):
                    icon = maybe_icon
                if meta_map.get("persist_tag") is not None:
                    metadata["persist_tag"] = str(meta_map["persist_tag"])

        final_title = title or default_title
        final_profile = profile
        final_icon = icon
        final_tooltip = tooltip or final_title

        if isinstance(payload, Card):
            card = payload
            if final_title and final_title != self._card_title(card) and hasattr(card, "title_label"):
                card.title_label.setText(final_title)
            if not final_profile:
                existing_profile = getattr(card, "task_profile", None)
                if isinstance(existing_profile, str) and existing_profile:
                    final_profile = existing_profile
                else:
                    final_profile = "card"
            if final_icon is None:
                existing_icon = getattr(card, "task_icon", None)
                if isinstance(existing_icon, QIcon) and not existing_icon.isNull():
                    final_icon = existing_icon
            if not final_tooltip:
                existing_tooltip = getattr(card, "task_tooltip", None)
                if isinstance(existing_tooltip, str) and existing_tooltip:
                    final_tooltip = existing_tooltip
                else:
                    final_tooltip = final_title
            card = self._attach_card(
                card,
                task_profile=final_profile,
                task_icon=final_icon,
                task_tooltip=final_tooltip,
            )
        elif isinstance(payload, QWidget):
            final_profile = final_profile or "python-card"
            card = self.add_card(
                payload,
                final_title,
                task_profile=final_profile,
                task_icon=final_icon,
                task_tooltip=final_tooltip,
            )
        else:
            raise RuntimeError("factory returned unsupported object")

        metadata.setdefault("title", final_title)
        metadata.setdefault("task_profile", final_profile)
        if final_icon is not None:
            metadata.setdefault("task_icon", final_icon)
        metadata.setdefault("task_tooltip", final_tooltip)
        return card, metadata

    def _load_python_as_card(
        self,
        path: str,
        persist_key: Optional[str]=None,
        nice_title: Optional[str]=None,
        task_profile: Optional[str]=None,
        task_icon: Optional[QIcon]=None,
        task_tooltip: Optional[str]=None,
    ) -> Optional[Card]:
        log(f"Load python as card: {path}")
        try:
            name = f"card_{int(time.time())}_{os.path.splitext(os.path.basename(path))[0]}"
            spec = importlib.util.spec_from_file_location(name, path)
            if not spec or not spec.loader:
                raise RuntimeError("spec loader failed")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)  # type: ignore
        except Exception as e:
            self._toast(f"Import failed: {e}")
            log(f"Import failed: {e}", logging.ERROR)
            return None

        factory = getattr(mod, "build_widget", None)
        if not callable(factory):
            factory = getattr(mod, "create_card", None)
        if not callable(factory):
            self._toast("No build_widget/create_card; running as process instead.")
            log("card factory not found; falling back to process", logging.INFO)
            return None

        default_title = nice_title or os.path.basename(path)
        default_icon = task_icon or QApplication.style().standardIcon(QStyle.SP_DesktopIcon)
        default_profile = task_profile or "python-card"
        default_tooltip = task_tooltip or path

        old_flag = os.environ.get("CODEX_EMBEDDED")
        os.environ["CODEX_EMBEDDED"] = "1"  # hint for embedded-compatible widgets
        try:
            card, card_meta = self._instantiate_card_from_factory(
                factory,
                default_title=default_title,
                task_profile=default_profile,
                task_icon=default_icon,
                task_tooltip=default_tooltip,
            )
        except Exception as e:
            if old_flag is None:
                os.environ.pop("CODEX_EMBEDDED", None)
            else:
                os.environ["CODEX_EMBEDDED"] = old_flag
            self._toast(f"factory error: {e}")
            log(
                f"factory error: {e}\n{traceback.format_exc()}",
                logging.ERROR,
            )
            return None
        finally:
            if old_flag is None:
                os.environ.pop("CODEX_EMBEDDED", None)
            else:
                os.environ["CODEX_EMBEDDED"] = old_flag

        persist_tag = persist_key or str(card_meta.get("persist_tag", "")).strip() or None
        if persist_tag:
            card.set_persist_tag(persist_tag)
            _restore_card_geom(card, "py_card", persist_tag)
            card.moved.connect(lambda: _save_card_geom(card, "py_card", persist_tag))
            card.resized.connect(lambda: _save_card_geom(card, "py_card", persist_tag))

        title_for_log = str(card_meta.get("title", default_title))
        card.closed.connect(lambda _: log(f"Card closed: {title_for_log}"))
        self._bring_card_forward(card)
        _remember_card("py_card", path, title_for_log)
        log(f"Card loaded: {title_for_log}")
        return card

    def _load_process_card(self, path: str, title: str, persist_key: Optional[str]=None):
        spec = build_launch_spec(path, SCRIPT_DIR)
        log(f"Run process as card: {spec.argv}")

        approved_launch = self.allow_external_browse()
        embed_candidate = should_embed_external_app(spec, ALLOWLIST)

        if embed_candidate:
            approved_launch = True
            try:
                external_widget = ExternalAppCard(
                    self.t,
                    spec,
                    toast_cb=lambda msg, kind="info": self._toast(msg, kind=kind),
                    log_cb=lambda message, level=logging.INFO: log(message, level),
                )
            except Exception as exc:  # pragma: no cover - defensive guard
                log(f"[external-app] failed to initialize for {path}: {exc}", logging.ERROR)
            else:
                started = False
                try:
                    started = external_widget.start()
                except Exception as exc:  # pragma: no cover - Qt failures
                    log(f"[external-app] start error for {path}: {exc}", logging.ERROR)
                if started:
                    proc_icon, _ = _icon_for_path(spec.target_path or spec.original_path)
                    card = self.add_card(
                        external_widget,
                        f"App — {title}",
                        task_profile="external-app",
                        task_icon=proc_icon,
                        task_tooltip=spec.original_path,
                    )
                    external_widget.attach_card(card)
                    external_widget.request_close.connect(card._close_card)
                    external_widget.process_finished.connect(
                        lambda code, detail, source=spec.original_path: self._handle_external_exit(source, code, detail)
                    )
                    external_widget.fallback_requested.connect(
                        lambda reason, _spec=spec, _title=title, _persist=persist_key, _card=card, _widget=external_widget, _approved=approved_launch: self._handle_external_fallback(
                            reason,
                            _spec,
                            _title,
                            _persist,
                            _approved,
                            _card,
                            _widget,
                        )
                    )
                    card.closed.connect(lambda _=None: external_widget.shutdown())
                    if persist_key:
                        card.set_persist_tag(persist_key)
                        _restore_card_geom(card, "external-app", persist_key)
                        card.moved.connect(lambda: _save_card_geom(card, "external-app", persist_key))
                        card.resized.connect(lambda: _save_card_geom(card, "external-app", persist_key))
                    self._bring_card_forward(card)
                    _remember_card("external-app", spec.original_path, title)
                    return
                external_widget.deleteLater()

        self._open_process_error_card(
            spec,
            title,
            persist_key,
            allow_external_exec=approved_launch,
        )

    def _open_process_error_card(
        self,
        spec: LaunchSpec,
        title: str,
        persist_key: Optional[str],
        *,
        allow_external_exec: bool = False,
    ) -> None:
        cmd = spec.argv if spec.argv else [spec.original_path]
        widget = ProcessErrorCard(
            self.t,
            cmd,
            cwd=spec.cwd,
            guard=_validate_process_request,
            allow_external_exec=allow_external_exec,
            violation_cb=lambda m: self._toast(m, kind="error"),
        )
        widget.isolation_requested.connect(
            lambda message, code, src=spec.original_path: self._handle_process_isolation(message, code, src)
        )
        icon_source = spec.target_path or spec.original_path
        proc_icon, _ = _icon_for_path(icon_source)
        card = self.add_card(
            widget,
            f"Process — {title}",
            task_profile="process",
            task_icon=proc_icon,
            task_tooltip=spec.original_path,
        )
        widget.close_requested.connect(card.close)
        card.closed.connect(lambda _=None: widget.stop())
        if persist_key:
            card.set_persist_tag(persist_key)
            _restore_card_geom(card, "process", persist_key)
            card.moved.connect(lambda: _save_card_geom(card, "process", persist_key))
            card.resized.connect(lambda: _save_card_geom(card, "process", persist_key))
        self._bring_card_forward(card)
        _remember_card("process", spec.original_path, title)

    def _handle_external_exit(self, path: str, exit_code: int, detail: str) -> None:
        name = os.path.basename(path) or path
        if exit_code != 0:
            message = detail or f"{name} exited with code {exit_code}."
            self._toast(message, kind="error")
            log(f"[external-app] {message} — {path}", logging.ERROR)
        else:
            log(f"[external-app] {name} exited normally.")

    def _handle_external_fallback(
        self,
        reason: str,
        spec: LaunchSpec,
        title: str,
        persist_key: Optional[str],
        approved_external: bool,
        card: "Card",
        _widget: ExternalAppCard,
    ) -> None:
        log(f"[external-app] fallback: {reason} — {spec.original_path}", logging.WARNING)
        try:
            card._close_card()
        except Exception:
            try:
                card.close()
            except Exception:
                pass
        QTimer.singleShot(
            0,
            lambda: self._open_process_error_card(
                spec,
                title,
                persist_key,
                allow_external_exec=approved_external or self.allow_external_browse(),
            ),
        )

    def _handle_process_isolation(self, message: str, code: Optional[int], path: str) -> None:
        detail = message or "Process failure detected."
        if code is not None:
            detail = f"{detail} (exit code {code})"
        self._toast(detail, kind="error")
        log(f"[process-error] {detail} — {path}", logging.ERROR)

    def _open_system_console(self):
        if self._sys_console and self._sys_console.isVisible():
            self._sys_console.raise_(); self._sys_console.activateWindow(); return
        self._sys_console = SystemConsole(self.t, LOG_PATH)
        parent_window = self.window()
        if parent_window:
            self._sys_console.setParent(parent_window, Qt.Window)  # containment with window chrome
        else:
            self._sys_console.setWindowFlag(Qt.Window, True)
        self._sys_console.show()
        log("System Console opened")

    def _open_error_center(self) -> None:
        if self._error_card and self._error_card.isVisible():
            self._bring_card_forward(self._error_card)
            self.camera.center_on_widget(self._error_card)
            return
        can_open_tasks = not isinstance(self.task_mgr, _FallbackTaskManager)
        callback = self._open_tasks_from_error_center if can_open_tasks else None
        widget = ErrorCenterCard(self.t, LOG_PATH, open_task=callback)
        if can_open_tasks:
            widget.task_requested.connect(self._open_tasks_from_error_center)
        else:
            widget.set_open_task_callback(None)
        error_icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical)
        card = self.add_card(
            widget,
            "Error Center",
            task_profile="error-center",
            task_icon=error_icon,
            task_tooltip="Error Center",
        )
        tag = "(builtin:error-center)"
        card.set_persist_tag(tag)
        _restore_card_geom(card, "builtin", tag)
        card.moved.connect(lambda: _save_card_geom(card, "builtin", tag))
        card.resized.connect(lambda: _save_card_geom(card, "builtin", tag))
        card.closed.connect(self._on_error_center_closed)
        self._error_card = card
        self._error_widget = widget
        self._bring_card_forward(card)
        self.camera.center_on_widget(card)
        _remember_card("builtin", tag, "Error Center")
        log("Error Center opened")

    def _on_error_center_closed(self, *_):
        self._error_card = None
        self._error_widget = None

    def _open_tasks_from_error_center(self, task_id: Optional[str]) -> None:
        if not task_id:
            return
        self._open_tasks(task_id=task_id)

    def _open_code_editor(self, path: Optional[str] = None) -> None:
        if not path:
            self._toast("No file selected for editor.")
            return
        resolved = path
        if not os.path.isabs(resolved):
            base = self._workspace or VDSK_ROOT
            resolved = os.path.join(base, path)
        if not os.path.isfile(resolved):
            self._toast(f"File not found: {resolved}")
            log(f"Editor open skipped; missing file {resolved}", logging.WARNING)
            return
        try:
            storage_root = Path(self._workspace or VDSK_ROOT) / "memory"
            widget = build_editor_widget(
                parent=None,
                initial_path=resolved,
                storage_root=storage_root,
            )
        except Exception as exc:
            self._toast("Unable to open editor card.")
            log(f"Editor widget failed for {resolved}: {exc}", logging.ERROR)
            return
        title = f"Editor — {os.path.basename(resolved)}"
        editor_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        card = self.add_card(
            widget,
            title,
            task_profile="editor",
            task_icon=editor_icon,
            task_tooltip=resolved,
        )
        tag = f"(editor:{resolved})"
        card.set_persist_tag(tag)
        _restore_card_geom(card, "editor", tag)
        card.moved.connect(lambda: _save_card_geom(card, "editor", tag))
        card.resized.connect(lambda: _save_card_geom(card, "editor", tag))
        self._bring_card_forward(card)
        self.camera.center_on_widget(card)
        _remember_card("editor", resolved, title)
        log(f"Editor opened for {resolved}")

    def _open_terminal_at(self, directory: Optional[str] = None) -> None:
        base = directory or self._workspace or SCRIPT_DIR
        cwd = base if os.path.isdir(base) else os.path.dirname(base) or (self._workspace or SCRIPT_DIR)
        if not os.path.isdir(cwd):
            self._toast(f"Folder not found: {cwd}")
            log(f"Terminal launch skipped; missing folder {cwd}", logging.WARNING)
            return
        if os.name == "nt":
            shell = os.environ.get("COMSPEC", "cmd.exe")
            cmd = [shell]
        else:
            shell = os.environ.get("SHELL", "/bin/bash")
            cmd = [shell]
        title = f"Terminal — {os.path.basename(cwd) or cwd}"
        widget = ProcessConsole(
            self.t,
            cmd,
            cwd=cwd,
            guard=_validate_process_request,
            violation_cb=lambda m: self._toast(m, kind="error"),
        )
        term_icon = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
        card = self.add_card(
            widget,
            title,
            task_profile="terminal",
            task_icon=term_icon,
            task_tooltip=cwd,
        )
        tag = f"(terminal:{cwd})"
        card.set_persist_tag(tag)
        _restore_card_geom(card, "process", tag)
        card.moved.connect(lambda: _save_card_geom(card, "process", tag))
        card.resized.connect(lambda: _save_card_geom(card, "process", tag))
        self._bring_card_forward(card)
        self.camera.center_on_widget(card)
        _remember_card("process", cwd, title)
        log(f"Terminal card opened at {cwd}")

    def _open_explorer(self):
        widget = ExplorerCard(self._workspace, self.open_any_path, self.t, refresh_hook=self.canvas._refresh_icons)
        explorer_icon = QApplication.style().standardIcon(QStyle.SP_DirIcon)
        card = self.add_card(
            widget,
            "Desktop Explorer",
            task_profile="explorer",
            task_icon=explorer_icon,
            task_tooltip=self._workspace,
        )
        tag = "(builtin:explorer)"
        card.set_persist_tag(tag)
        _restore_card_geom(card, "template", tag)
        card.moved.connect(lambda: _save_card_geom(card, "template", tag))
        card.resized.connect(lambda: _save_card_geom(card, "template", tag))
        self._bring_card_forward(card)

    def _open_operator_manager(self) -> None:
        if self._operator_card:
            self._bring_card_forward(self._operator_card)
            return
        widget = OperatorManagerWidget(self.t)
        ops_icon = QApplication.style().standardIcon(QStyle.SP_DesktopIcon)
        card = self.add_card(
            widget,
            "Operator Manager",
            task_profile="operator-manager",
            task_icon=ops_icon,
            task_tooltip="Operator Manager",
        )
        tag = "(builtin:operators)"
        card.set_persist_tag(tag)
        card.closed.connect(lambda _: setattr(self, "_operator_card", None))
        self._operator_card = card
        self._bring_card_forward(card)
        _remember_card("builtin", tag, "Operator Manager")
        log("Operator Manager opened")

    def _open_tasks(self, task_id: Optional[str] = None) -> None:
        if self._tasks_card and self._tasks_card.isVisible():
            self._bring_card_forward(self._tasks_card)
            self.camera.center_on_widget(self._tasks_card)
            if task_id:
                QTimer.singleShot(0, lambda: self._focus_task(task_id))
            return
        widget = open_card(
            self.task_mgr,
            self.t,
            self._open_code_editor,
            self._open_terminal_at,
            workspace_root=self._workspace,
            source="desktop",
        )
        if widget is None:
            return
        tasks_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogListView)
        card = self.add_card(
            widget,
            "Tasks",
            task_profile="tasks",
            task_icon=tasks_icon,
            task_tooltip="Tasks",
        )
        tag = "(builtin:tasks)"
        card.set_persist_tag(tag)
        _restore_card_geom(card, "template", tag)
        card.moved.connect(lambda: _save_card_geom(card, "template", tag))
        card.resized.connect(lambda: _save_card_geom(card, "template", tag))
        card.closed.connect(self._on_tasks_card_closed)
        self._tasks_card = card
        self._tasks_widget = widget
        self._bring_card_forward(card)
        self.camera.center_on_widget(card)
        _remember_card("template", "(builtin:tasks)", "Tasks")
        log("Tasks card opened")
        if task_id:
            QTimer.singleShot(200, lambda: self._focus_task(task_id))

    def _open_user_guided_notes(self) -> Optional[Card]:
        if _USER_GUIDED_NOTES_FACTORY is None:
            self._toast("User-Guided Notes is unavailable.", kind="error")
            log("User_Guided_Notes factory unavailable", logging.INFO)
            return None
        if self._notes_window and self._notes_window.isVisible():
            try:
                self._notes_window.show()
                self._notes_window.raise_()
                self._notes_window.activateWindow()
            except Exception:
                pass
            return None
        if self._notes_card and self._notes_card.isVisible():
            self._bring_card_forward(self._notes_card)
            self.camera.center_on_widget(self._notes_card)
            return self._notes_card
        notes_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        try:
            card, meta = self._instantiate_card_from_factory(
                _USER_GUIDED_NOTES_FACTORY,
                default_title="User-Guided Notes",
                task_profile="notes",
                task_icon=notes_icon,
                task_tooltip="User-Guided Notes",
            )
        except Exception as exc:
            self._toast("Unable to open Notes card.", kind="error")
            log(
                f"Notes card factory failed: {exc}\n{traceback.format_exc()}",
                logging.ERROR,
            )
            return None

        tag = str(meta.get("persist_tag") or "(builtin:user-guided-notes)")
        if tag:
            self._notes_card_tag = tag
            self._configure_notes_card(card, tag)
        else:
            self._notes_card_tag = None
            card.closed.connect(self._on_notes_card_closed)
        self._notes_card = card
        widget = self._extract_notes_widget(card)
        if widget is not None:
            self._install_notes_widget(widget)
        self._bring_card_forward(card)
        self.camera.center_on_widget(card)
        title = str(meta.get("title", "User-Guided Notes"))
        _remember_card("builtin", tag, title)
        log("User-Guided Notes card opened")
        return card

    def _configure_notes_card(self, card: Card, tag: str) -> None:
        card.set_persist_tag(tag)
        _restore_card_geom(card, "builtin", tag)
        card.moved.connect(lambda: _save_card_geom(card, "builtin", tag))
        card.resized.connect(lambda: _save_card_geom(card, "builtin", tag))
        card.closed.connect(self._on_notes_card_closed)

    def _extract_notes_widget(self, card: Card) -> Optional[QWidget]:
        widget: Optional[QWidget] = None
        if _USER_GUIDED_NOTES_WIDGET_CLASS is not None:
            try:
                widget = card.findChild(_USER_GUIDED_NOTES_WIDGET_CLASS)  # type: ignore[arg-type]
            except Exception:
                widget = None
        if widget is None:
            body_layout = card.body.layout()
            if body_layout and body_layout.count():
                candidate = body_layout.itemAt(0).widget()
                if isinstance(candidate, QWidget):
                    widget = candidate
        return widget

    def _install_notes_widget(self, widget: QWidget) -> None:
        if self._notes_widget is widget:
            self._set_notes_embedded_state(True)
            return
        if self._notes_widget is not None and self._notes_widget is not widget:
            self._disconnect_notes_widget()
        self._notes_widget = widget
        self._set_notes_embedded_state(True)
        try:
            widget.request_detach.connect(self._detach_notes_widget)  # type: ignore[attr-defined]
            widget.request_redock.connect(self._redock_notes_widget)  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            widget.destroyed.connect(self._clear_notes_widget)  # type: ignore[attr-defined]
        except Exception:
            pass

    def _disconnect_notes_widget(self) -> None:
        if self._notes_widget is None:
            return
        try:
            self._notes_widget.request_detach.disconnect(self._detach_notes_widget)  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            self._notes_widget.request_redock.disconnect(self._redock_notes_widget)  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            self._notes_widget.destroyed.disconnect(self._clear_notes_widget)  # type: ignore[attr-defined]
        except Exception:
            pass

    def _set_notes_embedded_state(self, embedded: bool) -> None:
        widget = self._notes_widget
        if widget is None:
            return
        apply_state = getattr(widget, "apply_embedded_state", None)
        if callable(apply_state):
            try:
                apply_state(embedded)
            except Exception:
                pass

    def _detach_notes_widget(self, widget: object) -> None:
        if widget is not self._notes_widget or self._notes_widget is None:
            return
        if _USER_GUIDED_NOTES_WINDOW_CLASS is None:
            self._toast("Pop-out window unavailable.", kind="error")
            self._set_notes_embedded_state(True)
            return
        card = self._notes_card
        if card is None:
            if self._notes_window:
                try:
                    self._notes_window.show()
                    self._notes_window.raise_()
                    self._notes_window.activateWindow()
                except Exception:
                    pass
            return
        if self._notes_card_tag:
            _save_card_geom(card, "builtin", self._notes_card_tag)
        body_layout = card.body.layout()
        if body_layout:
            body_layout.removeWidget(self._notes_widget)
        self._notes_widget.setParent(None)
        self._set_notes_embedded_state(False)
        try:
            window = _USER_GUIDED_NOTES_WINDOW_CLASS(self._notes_widget)  # type: ignore[misc]
        except Exception as exc:
            self._toast("Unable to pop out Notes window.", kind="error")
            log(f"Notes window creation failed: {exc}", logging.ERROR)
            if body_layout:
                body_layout.addWidget(self._notes_widget)
            self._set_notes_embedded_state(True)
            return
        self._notes_window = window
        try:
            window.destroyed.connect(self._on_notes_window_destroyed)
        except Exception:
            pass
        _restore_window_geom(window, "notes")
        try:
            window.show()
            window.raise_()
            window.activateWindow()
        except Exception:
            pass
        self._notes_card = None
        card.close()

    def _redock_notes_widget(self, widget: object) -> None:
        if widget is not self._notes_widget or self._notes_widget is None:
            return
        window = self._notes_window
        if window is None:
            self._set_notes_embedded_state(True)
            return
        _save_window_geom(window, "notes")
        taken_widget: Optional[QWidget] = None
        try:
            taken_widget = window.takeCentralWidget()
        except Exception:
            taken_widget = None
        if taken_widget is not None and taken_widget is not self._notes_widget:
            self._install_notes_widget(taken_widget)
        widget_obj = self._notes_widget
        if widget_obj is None:
            window.close()
            self._notes_window = None
            return
        widget_obj.setParent(None)
        notes_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        card = self.add_card(
            widget_obj,
            "User-Guided Notes",
            task_profile="notes",
            task_icon=notes_icon,
            task_tooltip="User-Guided Notes",
        )
        self._notes_card = card
        if self._notes_card_tag:
            self._configure_notes_card(card, self._notes_card_tag)
        else:
            card.closed.connect(self._on_notes_card_closed)
        self._set_notes_embedded_state(True)
        self._bring_card_forward(card)
        self.camera.center_on_widget(card)
        window.close()
        self._notes_window = None

    def _on_notes_card_closed(self, card: object) -> None:
        if self._notes_card is card:
            self._notes_card = None
        if not self._notes_window:
            self._notes_card_tag = None

    def _on_notes_window_destroyed(self, *args) -> None:
        self._notes_window = None

    def _clear_notes_widget(self, *args) -> None:
        self._disconnect_notes_widget()
        self._notes_widget = None
        if not self._notes_window:
            self._notes_card = None
            self._notes_card_tag = None
    def _open_system_overview(self) -> None:
        if self._system_card and self._system_card.isVisible():
            self._bring_card_forward(self._system_card)
            self.camera.center_on_widget(self._system_card)
            return
        dataset_path = getattr(self.task_mgr, "dataset_path", None)
        try:
            dataset_root = Path(dataset_path).resolve().parent if dataset_path else Path(SCRIPT_DIR, "datasets")
        except Exception:
            dataset_root = Path(SCRIPT_DIR, "datasets")
        card = SystemOverviewCard(self.t, dataset_root, parent=self.canvas)
        tag = "(builtin:system-overview)"
        system_icon = QApplication.style().standardIcon(QStyle.SP_DesktopIcon)
        card = self._attach_card(
            card,
            task_profile="system-overview",
            task_icon=system_icon,
            task_tooltip="System Overview",
        )
        card.set_persist_tag(tag)
        _restore_card_geom(card, "builtin", tag)
        card.moved.connect(lambda: _save_card_geom(card, "builtin", tag))
        card.resized.connect(lambda: _save_card_geom(card, "builtin", tag))
        card.closed.connect(self._on_system_card_closed)
        self._system_card = card
        _remember_card("builtin", tag, "System Overview")
        self._bring_card_forward(card)
        self.camera.center_on_widget(card)
        log("System Overview opened")

    def _on_tasks_card_closed(self, *_):
        self._tasks_card = None
        self._tasks_widget = None

    def _on_system_card_closed(self, *_):
        self._system_card = None

    def _focus_task(self, task_id: Optional[str]) -> None:
        if not task_id or not self._tasks_widget:
            return
        panel = getattr(self._tasks_widget, "panel", None)
        if panel is None:
            return
        try:
            panel.refresh()
        except Exception:
            log(f"Task panel refresh failed for focus: {task_id}", logging.DEBUG)
        list_widget = getattr(panel, "list", None)
        if list_widget is None:
            return
        for idx in range(list_widget.count()):
            item = list_widget.item(idx)
            if item and item.data(Qt.UserRole) == task_id:
                list_widget.setCurrentItem(item)
                list_widget.scrollToItem(item)
                break

    def toggle_template_terminal(self, on: bool):
        tag = "(builtin:template)"
        if on:
            if self._template_card:
                self._bring_card_forward(self._template_card); self.camera.center_on_widget(self._template_card); return
            widget = TemplateTerminal(self.t)
            template_icon = QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
            card = self.add_card(
                widget,
                "Template Terminal",
                task_profile="template-terminal",
                task_icon=template_icon,
                task_tooltip="Template Terminal",
            )
            card.set_persist_tag(tag)
            _restore_card_geom(card, "template", tag)
            card.moved.connect(lambda: _save_card_geom(card, "template", tag))
            card.resized.connect(lambda: _save_card_geom(card, "template", tag))
            def on_closed(_):
                self._template_card = None
            card.closed.connect(on_closed)
            self._template_card = card
            _remember_card("template", "(builtin)", "Template Terminal")
            self._bring_card_forward(card)
            self.camera.center_on_widget(card)
            log("Template Terminal opened")
        else:
            if self._template_card:
                c = self._template_card; self._template_card = None
                try: c._close_card()
                except Exception: pass
                log("Template Terminal closed")

    def _resolve_codex_terminal_path(self) -> Optional[str]:
        candidates = [
            os.environ.get("CODEX_TERMINAL_PATH", "").strip(),
            os.path.join(SCRIPT_DIR, "Codex_Terminal.py"),
            os.path.join(os.getcwd(), "Codex_Terminal.py"),
        ]
        path = next((p for p in candidates if p and os.path.isfile(p)), None)
        if path:
            return path
        selected, _ = _non_native_open_file(
            self,
            "Select Codex_Terminal.py",
            SCRIPT_DIR,
            "Python (*.py)",
        )
        return selected or None

    def open_codex_terminal(self):
        # Try common locations or prompt. Keep containment via non-native dialog.
        path = self._resolve_codex_terminal_path()
        if not path:
            QMessageBox.information(self, "Codex", "Codex_Terminal.py not found.")
            return
        codex_icon = QApplication.style().standardIcon(QStyle.SP_DesktopIcon)
        previous_env = os.environ.get("CODEX_WORKSPACE")
        workspace = workspace_root()
        applied_env = False
        if workspace:
            os.environ["CODEX_WORKSPACE"] = workspace
            applied_env = True
        try:
            card = self._load_python_as_card(
                path,
                persist_key=path,
                nice_title="Codex Terminal",
                task_profile="codex-terminal",
                task_icon=codex_icon,
                task_tooltip=path,
            )
        finally:
            if applied_env:
                if previous_env is None:
                    os.environ.pop("CODEX_WORKSPACE", None)
                else:
                    os.environ["CODEX_WORKSPACE"] = previous_env
        if card is None:
            log("[Codex] embed failed; showing System Console.", logging.ERROR)
            self._open_system_console()

# --------------------------------------------------------------------------------------
# Text/Image viewers
# --------------------------------------------------------------------------------------
class TextViewer(QWidget):
    def __init__(self, path: str, theme: Theme):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(8)
        self.info = QLabel(os.path.basename(path)); self.info.setStyleSheet(f"color:{theme.text_muted}; font:600 10pt 'Cascadia Code';")
        v.addWidget(self.info)
        self.edit = QPlainTextEdit(self); self.edit.setReadOnly(True)
        apply_contrast_palette(self.edit, theme.editor_bg, theme.editor_fg)
        self.edit.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; border:1px solid {theme.card_border}; "
            f"selection-background-color:{theme.editor_sel}; font-family:'Cascadia Code',Consolas,monospace; }}"
        )
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.edit.setPlainText(f.read())
        except Exception as e:
            self.edit.setPlainText(f"[Error] {e}")
        v.addWidget(self.edit, 1)

class ImageViewer(QWidget):
    def __init__(self, path: str, theme: Theme):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(8)
        self.info = QLabel(os.path.basename(path)); self.info.setStyleSheet(f"color:{theme.text_muted}; font:600 10pt 'Cascadia Code';")
        v.addWidget(self.info)
        self.label = QLabel(self); self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"background:{theme.editor_bg}; border:1px solid {theme.card_border};")
        pix = QPixmap(path)
        if pix.isNull():
            self.label.setText("Unable to load image.")
        else:
            self.label.setPixmap(pix.scaled(1024, 768, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        v.addWidget(self.label, 1)
        self.label.setScaledContents(False)

# --------------------------------------------------------------------------------------
# Process console (fallback)
# --------------------------------------------------------------------------------------
class ProcessConsole(QWidget):
    def __init__(
        self,
        theme: Theme,
        cmd: List[str],
        cwd: Optional[str] = None,
        guard: Optional[Callable[[List[str], Optional[str], bool], Tuple[bool, str]]] = None,
        *,
        allow_external_exec: bool = False,
        violation_cb: Optional[Callable[[str], None]] = None,
    ):
        super().__init__()
        self.t = theme
        self.cmd = list(cmd)
        self.cwd = os.path.abspath(cwd or SCRIPT_DIR)
        self.proc: Optional[subprocess.Popen] = None
        self.reader: Optional[threading.Thread] = None
        self._kill = threading.Event()
        self._guard = guard
        self._allow_external_exec = bool(allow_external_exec)
        self._violation_cb = violation_cb

        v = QVBoxLayout(self); v.setContentsMargins(10, 10, 10, 10); v.setSpacing(8)
        row = QHBoxLayout(); row.setSpacing(8)
        self.btn_start = QPushButton("Start"); self.btn_stop = QPushButton("Stop"); self.btn_stop.setEnabled(False)
        for b in (self.btn_start, self.btn_stop):
            b.setStyleSheet(f"QPushButton{{color:#fff;background:{self.t.accent};border:1px solid {self.t.card_border};border-radius:6px;padding:6px 10px;}}"
                            f"QPushButton:hover{{background:{self.t.accent_hov};}}")
        row.addWidget(self.btn_start); row.addWidget(self.btn_stop); row.addStretch(1)
        v.addLayout(row)

        self.console = QPlainTextEdit(self); self.console.setReadOnly(True)
        apply_contrast_palette(self.console, theme.editor_bg, theme.editor_fg)
        self.console.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; "
            f"selection-background-color:{self.t.editor_sel}; border:1px solid {self.t.card_border}; "
            f"font-family:'Cascadia Code',Consolas,monospace; }}"
        )
        v.addWidget(self.console, 1)
        self.btn_start.clicked.connect(self._start)
        self.btn_stop.clicked.connect(self._stop)

    def _println(self, s: str):
        self.console.appendPlainText(s)
        log(f"[process] {s}")

    def _start(self):
        if self.proc and self.proc.poll() is None: return
        detail = None
        if self._guard:
            allowed, detail = self._guard(self.cmd, self.cwd, self._allow_external_exec)
            if not allowed:
                message = detail or "Blocked: command rejected."
                self._println(message)
                log(f"[process] blocked: {' '.join(self.cmd)} — {message}", logging.WARNING)
                if self._violation_cb:
                    try:
                        self._violation_cb(message)
                    except Exception:
                        log("[process] violation callback failed", logging.DEBUG)
                return
        try:
            self._println(f"Run: {' '.join(self.cmd)}")
            if detail:
                log(f"[process] launching {detail} (cwd={self.cwd})")
            self.proc = subprocess.Popen(self.cmd, cwd=self.cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception as e:
            self._println(f"Error: {e}"); return
        self._kill.clear()
        self.reader = threading.Thread(target=self._reader, daemon=True); self.reader.start()
        self.btn_start.setEnabled(False); self.btn_stop.setEnabled(True)
        self._println("Streaming output…")

    def _stop(self):
        if not self.proc: return
        self._kill.set()
        try: self.proc.terminate()
        except Exception: pass
        self.btn_start.setEnabled(True); self.btn_stop.setEnabled(False)
        self._println("Terminated")

    def _reader(self):
        assert self.proc and self.proc.stdout
        for line in self.proc.stdout:
            if self._kill.is_set(): break
            s = line.rstrip("\n")
            self.console.appendPlainText(s)
            log(f"[out] {s}")
        self.btn_start.setEnabled(True); self.btn_stop.setEnabled(False)

# --------------------------------------------------------------------------------------
# Persistence helpers
# --------------------------------------------------------------------------------------
def _restore_card_geom(card: Card, kind: str, persist_tag: str):
    st = _load_state(); key = _geom_key_for(kind, persist_tag)
    g = st.get("geom", {}).get(key)
    if not g: return
    try:
        saved_x = int(g["x"])
        saved_y = int(g["y"])
        saved_w = int(g["w"])
        saved_h = int(g["h"])
        saved_scale = float(g.get("scale", 1.0)) if g.get("scale") is not None else 1.0
        current_scale = float(getattr(card, "_vd_scale", saved_scale or 1.0))
        x, y, w, h = saved_x, saved_y, saved_w, saved_h
        if saved_scale > 0 and current_scale > 0 and not math.isclose(saved_scale, current_scale, rel_tol=1e-3):
            ratio = current_scale / saved_scale
            w = max(MIN_CARD_WIDTH, int(round(saved_w * ratio)))
            h = max(MIN_CARD_HEIGHT, int(round(saved_h * ratio)))
            center_x = saved_x + saved_w / 2
            center_y = saved_y + saved_h / 2
            x = int(round(center_x - w / 2))
            y = int(round(center_y - h / 2))
        parent = card.parentWidget()
        if parent:
            rect = parent.rect()
            max_x = max(8, rect.width() - w - 8)
            max_y = max(8, rect.height() - h - 8)
            x = max(8, min(x, max_x))
            y = max(8, min(y, max_y))
        card.resize(w, h); card.move(x, y)
        setattr(card, "_vd_scale", current_scale)
    except Exception:
        pass

def _save_card_geom(card: Card, kind: str, persist_tag: str):
    st = _load_state(); key = _geom_key_for(kind, persist_tag)
    st.setdefault("geom", {})[key] = {
        "x": card.x(),
        "y": card.y(),
        "w": card.width(),
        "h": card.height(),
        "scale": float(getattr(card, "_vd_scale", 1.0)),
    }
    _save_state(st)

def _restore_window_geom(window: QWidget, key: str) -> None:
    st = _load_state()
    payload = st.get("window_geom", {}).get(key)
    if not isinstance(payload, dict):
        return
    try:
        x = int(payload.get("x"))
        y = int(payload.get("y"))
        w = int(payload.get("w"))
        h = int(payload.get("h"))
    except Exception:
        return
    window.setGeometry(x, y, max(w, 1), max(h, 1))

def _save_window_geom(window: QWidget, key: str) -> None:
    geom = window.geometry()
    st = _load_state()
    st.setdefault("window_geom", {})[key] = {
        "x": geom.x(),
        "y": geom.y(),
        "w": geom.width(),
        "h": geom.height(),
    }
    _save_state(st)

# --------------------------------------------------------------------------------------
# Window wrapper
# --------------------------------------------------------------------------------------
class VirtualDesktopWindow(QMainWindow):
    def __init__(self, workspace: Optional[str] = None):
        super().__init__()
        self.t = Theme()
        pal = self.palette()
        # High-contrast window and text
        pal.setColor(QPalette.Window, QColor("#0a1430"))
        pal.setColor(QPalette.Base, QColor("#0a1430"))
        pal.setColor(QPalette.Text, QColor("#e6f0ff"))
        pal.setColor(QPalette.WindowText, QColor("#e6f0ff"))
        self.setPalette(pal)
        self.setWindowTitle("Virtual Desktop")
        self.core = VirtualDesktopCore(workspace=workspace, parent=self)
        self.setCentralWidget(self.core)

        # Menubar retains system-level items; former top toolbar actions moved into Start/Settings
        self._menu()
        self._shortcuts()

        # Start maximized with border so Min/Max/Close work; Fullscreen toggle is optional
        QTimer.singleShot(0, self.showMaximized)

        self.installEventFilter(self)
        self._is_fitting = False
        self._last_window_state = self.windowState()
        self._current_screen = self.windowHandle().screen() if self.windowHandle() else None
        if self.windowHandle():
            self.windowHandle().screenChanged.connect(self._handle_screen_changed)
        self._fit_timer = QTimer(self); self._fit_timer.setSingleShot(True)
        self._fit_timer.timeout.connect(self.fit_to_current_screen)
        self._force_taskbar_clear_timer = QTimer(self)
        self._force_taskbar_clear_timer.setSingleShot(True)
        self._force_taskbar_clear_timer.timeout.connect(self._clear_forced_native_taskbar_offset)
        self._pending_maximize_fit = False

    def _menu(self):
        bar: QMenuBar = self.menuBar()
        bar.setStyleSheet(
            f"""
            QMenuBar {{
                background: {self.t.menu_bg};
                color: {self.t.menu_fg};
                border: none;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{ background: #0f1d33; }}
            QMenu {{
                background: #0b1828;
                color: {self.t.menu_fg};
                border: 1px solid {self.t.card_border};
            }}
            QMenu::item:selected {{ background: {self.t.accent}; color: #ffffff; }}
            """
        )
        view = bar.addMenu("&View")
        a_full = QAction("Toggle Fullscreen (Alt+Enter)", self); a_full.setShortcut("Alt+Return")
        a_full.triggered.connect(self._toggle_fullscreen); view.addAction(a_full)
        a_center = QAction("Center on Desktop (Ctrl+Home)", self); a_center.setShortcut("Ctrl+Home")
        a_center.triggered.connect(lambda: self.core.camera.center_on_widget(self.core.canvas)); view.addAction(a_center)
        a_fit = QAction("Fit to Current Screen", self); a_fit.setShortcut("Ctrl+0")
        a_fit.triggered.connect(self.fit_to_current_screen); view.addAction(a_fit)

        tools = bar.addMenu("&Tools")
        tools.addAction("Settings…", self.core._open_settings_panel)
        tools.addAction("System Console", self.core._open_system_console)
        tools.addAction("Error Center", self.core._open_error_center)
        tools.addAction("Open Desktop Explorer", self.core._open_explorer)
        tools.addAction("Template Terminal", lambda: self.core.toggle_template_terminal(True))
        tools.addAction("Load Script as Card…", self.core._load_script_dialog)
        tools.addAction("Open Codex_Terminal.py", self.core.open_codex_terminal)

        bar.addMenu("&Help").addAction("About", lambda: QMessageBox.information(self, "Virtual Desktop", "Contained virtual desktop. All dialogs non-native to keep containment.\nMin/Max/Close on each card.\nStart panel attached to taskbar."))

    def _shortcuts(self):
        def pan_guarded(dx, dy): self.core.camera.pan(dx, dy)
        self.addAction(self._mk_action("Ctrl+Left", lambda: pan_guarded(-160, 0)))
        self.addAction(self._mk_action("Ctrl+Right", lambda: pan_guarded(+160, 0)))
        self.addAction(self._mk_action("Ctrl+Up", lambda: pan_guarded(0, -160)))
        self.addAction(self._mk_action("Ctrl+Down", lambda: pan_guarded(0, +160)))

    def _mk_action(self, shortcut: str, fn):
        a = QAction(self); a.setShortcut(QKeySequence(shortcut)); a.triggered.connect(fn); return a

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if self._is_fitting:
            return
        if self.isFullScreen():
            return
        if bool(self.windowState() & Qt.WindowMaximized):
            return
        timer = getattr(self.core, "_sync_timer", None)
        if timer is not None:
            timer.start(0)
        else:
            QTimer.singleShot(0, self.core._sync_canvas_to_screen)

    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(0, self.fit_to_current_screen)

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.WindowStateChange:
            state_event: QWindowStateChangeEvent | None = None
            if isinstance(ev, QWindowStateChangeEvent):
                state_event = ev
            old_state = None
            if state_event is not None:
                getter = getattr(state_event, "oldState", None)
                if callable(getter):
                    try:
                        old_state = getter()
                    except Exception:
                        old_state = None
            if old_state is None:
                old_state = Qt.WindowStates(self._last_window_state)
            new_state = self.windowState()
            was_maximized = bool(old_state & Qt.WindowMaximized)
            is_maximized = bool(new_state & Qt.WindowMaximized)
            self._last_window_state = new_state
            if self._is_fitting:
                return super().eventFilter(obj, ev)
            if is_maximized and not was_maximized:
                self._pending_maximize_fit = True
                if not self._fit_timer.isActive():
                    self._fit_timer.start(10)
            elif was_maximized and not is_maximized:
                self._pending_maximize_fit = False
                self._fit_timer.stop()
        return super().eventFilter(obj, ev)

    def _handle_screen_changed(self, screen):
        if screen is self._current_screen:
            return
        self._current_screen = screen
        if self._is_fitting:
            return
        self._pending_maximize_fit = bool(self.windowState() & Qt.WindowMaximized)
        self._fit_timer.start(10)

    def _clear_forced_native_taskbar_offset(self):
        self.core.set_force_native_taskbar_offset(False)

    def fit_to_current_screen(self, *, force_native_taskbar: bool = False):
        if self._is_fitting:
            return
        self._is_fitting = True
        try:
            self._fit_timer.stop()
            if self.isFullScreen():
                if force_native_taskbar:
                    self.core.set_force_native_taskbar_offset(True)
                    self._force_taskbar_clear_timer.stop()
                self.core._sync_canvas_to_screen(force_native_taskbar=force_native_taskbar)
                if force_native_taskbar:
                    self._force_taskbar_clear_timer.start(0)
                self._pending_maximize_fit = False
                return
            scr = None
            if self.windowHandle() and self.windowHandle().screen():
                scr = self.windowHandle().screen()
            if not scr:
                scr = QGuiApplication.screenAt(self.frameGeometry().center())
            if not scr:
                scr = QGuiApplication.primaryScreen()
            self._current_screen = scr
            target_geom = QRect(scr.availableGeometry())
            applied = False
            should_force_taskbar = force_native_taskbar or self._pending_maximize_fit
            tolerance_px = 2

            def _within_tolerance(rect: QRect, target: QRect, tol: int) -> bool:
                return (
                    abs(rect.left() - target.left()) <= tol
                    and abs(rect.top() - target.top()) <= tol
                    and abs(rect.width() - target.width()) <= tol
                    and abs(rect.height() - target.height()) <= tol
                )

            handle = self.windowHandle()
            margins = None
            if handle is not None:
                try:
                    margins = handle.frameMargins()
                except Exception:
                    margins = None

            frame_rect = QRect()
            if handle is not None:
                try:
                    frame_rect = QRect(handle.frameGeometry())
                except Exception:
                    frame_rect = QRect()
            if not frame_rect.isValid() or frame_rect.isNull():
                frame_candidate = QRect(self.frameGeometry())
                if frame_candidate.isValid() and not frame_candidate.isNull():
                    frame_rect = frame_candidate

            def _apply_margins(rect: QRect) -> QRect:
                if margins is None or not rect.isValid() or rect.isNull():
                    return rect

                def _margin_value(name: str) -> int:
                    getter = getattr(margins, name, None)
                    value = 0.0
                    if callable(getter):
                        try:
                            value = getter()
                        except Exception:
                            value = 0.0
                    elif getter is not None:
                        value = getter
                    try:
                        return int(round(float(value)))
                    except Exception:
                        return 0

                left = _margin_value("left")
                top = _margin_value("top")
                right = _margin_value("right")
                bottom = _margin_value("bottom")
                adjusted_frame = QRect(rect)
                adjusted_frame.adjust(left, top, -right, -bottom)
                if adjusted_frame.isValid() and not adjusted_frame.isNull():
                    return adjusted_frame
                return rect

            is_maximized = bool(self.windowState() & Qt.WindowMaximized)
            current_client = QRect()
            if is_maximized:
                current_client = _apply_margins(frame_rect)
            else:
                if handle is not None:
                    try:
                        candidate = QRect(handle.geometry())
                    except Exception:
                        candidate = QRect()
                    if candidate.isValid() and not candidate.isNull():
                        current_client = candidate
                if not current_client.isValid() or current_client.isNull():
                    geom_candidate = QRect(self.geometry())
                    if geom_candidate.isValid() and not geom_candidate.isNull():
                        current_client = geom_candidate
                if not current_client.isValid() or current_client.isNull():
                    normal_candidate = QRect(self.normalGeometry())
                    if normal_candidate.isValid() and not normal_candidate.isNull():
                        current_client = normal_candidate

            if margins is not None and not is_maximized:
                current_client = _apply_margins(current_client)
            if current_client.isNull() or not current_client.isValid():
                current_client = QRect(target_geom)

            if is_maximized:
                matches_target = _within_tolerance(current_client, target_geom, tolerance_px)
                if matches_target:
                    self._pending_maximize_fit = False
                else:
                    should_force_taskbar = True
                    self.core.set_force_native_taskbar_offset(True)
                    self._force_taskbar_clear_timer.stop()

                    target_rect = QRect(target_geom)

                    def _apply_maximized_geometry():
                        try:
                            window = self.windowHandle()
                            if window is not None:
                                window.setGeometry(target_rect)
                                return
                        except Exception:
                            pass
                        try:
                            self.setGeometry(target_rect)
                        except Exception:
                            self.showMaximized()

                    self._pending_maximize_fit = False
                    QTimer.singleShot(0, _apply_maximized_geometry)
                    applied = True
            if should_force_taskbar and not applied:
                self.core.set_force_native_taskbar_offset(True)
                self._force_taskbar_clear_timer.stop()
            self.core._sync_canvas_to_screen(force_native_taskbar=should_force_taskbar)
            if should_force_taskbar:
                self._force_taskbar_clear_timer.start(0)
            self._pending_maximize_fit = False
            if applied:
                log(
                    f"Window fit to monitor: {target_geom.width()}x{target_geom.height()} @ {scr.name()}"
                )
            elif bool(self.windowState() & Qt.WindowMaximized):
                log(
                    "Window fit skipped — already aligned within tolerance; "
                    f"screen {scr.name()} available {target_geom.width()}x{target_geom.height()}"
                )
            else:
                log(
                    "Window fit skipped — not maximized; "
                    f"screen {scr.name()} available {target_geom.width()}x{target_geom.height()}"
                )
        finally:
            self._is_fitting = False

    def _toggle_fullscreen(self):
        if self.isFullScreen(): self.showNormal(); log("Exit fullscreen")
        else: self.showFullScreen(); log("Enter fullscreen")
        QTimer.singleShot(50, self.core._sync_canvas_to_screen)

# --------------------------------------------------------------------------------------
# Elevation helpers (Windows)
# --------------------------------------------------------------------------------------
def _is_windows() -> bool:
    return os.name == "nt"


def _query_windows_taskbar_height() -> int:
    if not _is_windows():
        return 0
    try:
        from ctypes import wintypes
    except Exception:
        return 0

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    class APPBARDATA(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_uint),
            ("hWnd", wintypes.HWND),
            ("uCallbackMessage", ctypes.c_uint),
            ("uEdge", ctypes.c_uint),
            ("rc", RECT),
            ("lParam", ctypes.c_long),
        ]

    ABM_GETTASKBARPOS = 0x00000005
    data = APPBARDATA()
    data.cbSize = ctypes.sizeof(APPBARDATA)
    try:
        result = ctypes.windll.shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(data))
    except Exception:
        return 0
    if not result:
        return 0
    if data.uEdge != 3:  # only bottom-aligned taskbar contributes to height offset
        return 0
    height = int(data.rc.bottom - data.rc.top)
    return max(0, height)


def _is_admin_windows() -> bool:
    if not _is_windows(): return True
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False
def _elevate_windows_if_needed():
    if not _is_windows(): return
    if os.environ.get("VD_NO_ELEVATE") == "1": return
    if _is_admin_windows(): return
    try:
        r = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f"\"{os.path.abspath(__file__)}\"", None, 1)
        if r > 32: sys.exit(0)
    except Exception as e:
        log(f"[elevate] failed: {e}", logging.WARNING)

# --------------------------------------------------------------------------------------
# Embedding API
# --------------------------------------------------------------------------------------
def build_widget(parent: Optional[QWidget] = None, workspace: Optional[str] = None):
    return VirtualDesktopCore(workspace=workspace, parent=parent)

def create_card(parent: Optional[QWidget] = None):
    w = build_widget(parent=parent, workspace=VDSK_ROOT)
    return w, "Virtual Desktop"

# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------
def _parse_args():
    ap = argparse.ArgumentParser(description="Virtual Desktop")
    ap.add_argument("--open", dest="open_path", help="Load a script/binary as a Card")
    ap.add_argument("--show-template", action="store_true", help="Show the Template Terminal on launch")
    ap.add_argument("--workspace", help="Folder to scan for files on launch")
    return ap.parse_args()

def main():
    _elevate_windows_if_needed()
    args = _parse_args()
    app = QApplication(sys.argv)
    win = VirtualDesktopWindow(workspace=args.workspace)
    if args.show_template:
        QTimer.singleShot(0, lambda: win.core.toggle_template_terminal(True))
    if args.open_path:
        QTimer.singleShot(0, lambda: win.core.open_any_path(args.open_path))
    win.show()
    log("Application exec()")
    rc = app.exec()
    log(f"Application exit code: {rc}")
    sys.exit(rc)

if __name__ == "__main__":
    main()
