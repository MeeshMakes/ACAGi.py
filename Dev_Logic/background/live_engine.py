"""Live OpenGL background engine with script hot-reload and throttled rendering."""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
import time
from dataclasses import dataclass
from types import ModuleType
from typing import Callable, Optional

from PySide6.QtCore import QObject, QTimer, Qt

try:  # Optional dependency: OpenGL widget may be unavailable in headless envs
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
except Exception:  # pragma: no cover - optional dependency guard
    QOpenGLWidget = None  # type: ignore

try:  # Optional: use psutil when available to gauge heavy system load
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency guard
    psutil = None  # type: ignore

LOGGER = logging.getLogger("VirtualDesktop.LiveEngine")


@dataclass
class ScriptHooks:
    """Bundle of lifecycle hooks exposed by a background script."""

    module: ModuleType
    path: str
    mtime: float

    def invoke(self, name: str, *args) -> None:
        func = getattr(self.module, name, None)
        if callable(func):
            func(*args)


class LiveScriptController(QObject):
    """Manage loading and hot-reloading of a background script module."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._hooks: Optional[ScriptHooks] = None
        self._script_path: Optional[str] = None
        self._missing_warned = False

    @property
    def module(self) -> Optional[ModuleType]:
        return self._hooks.module if self._hooks else None

    @property
    def script_path(self) -> str:
        return self._script_path or ""

    def set_script(self, path: Optional[str]) -> None:
        self._script_path = path or ""
        self._missing_warned = False
        if not self._script_path:
            self._hooks = None
            return
        self._load(force=True)

    def reload_if_changed(self) -> bool:
        """Reload the script when the file timestamp changes or becomes available."""

        if not self._script_path:
            return False
        try:
            mtime = os.path.getmtime(self._script_path)
        except OSError:
            if not self._missing_warned:
                LOGGER.warning("Live background script missing: %s", self._script_path)
                self._missing_warned = True
            self._hooks = None
            return False
        if not self._hooks:
            self._load(force=True)
            return self._hooks is not None
        if mtime <= self._hooks.mtime:
            return False
        self._load(force=True)
        return self._hooks is not None and self._hooks.mtime == mtime

    def _load(self, force: bool = False) -> None:
        path = self._script_path
        if not path:
            self._hooks = None
            return
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            if not self._missing_warned:
                LOGGER.warning("Live background script not found: %s", path)
                self._missing_warned = True
            self._hooks = None
            return
        if not force and self._hooks and mtime <= self._hooks.mtime:
            return
        spec = importlib.util.spec_from_file_location("vdsk_live_background", path)
        if not spec or not spec.loader:
            LOGGER.error("Unable to create spec for live background script: %s", path)
            self._hooks = None
            return
        module = importlib.util.module_from_spec(spec)
        try:
            loader = spec.loader
            assert loader is not None
            loader.exec_module(module)  # type: ignore[union-attr]
        except Exception:
            LOGGER.exception("Live background script import failed")
            self._hooks = None
            return
        sys.modules[spec.name] = module
        self._hooks = ScriptHooks(module=module, path=path, mtime=mtime)
        self._missing_warned = False

    def call(self, name: str, *args) -> None:
        if not self._hooks:
            return
        try:
            self._hooks.invoke(name, *args)
        except Exception:
            LOGGER.exception("Live background script %s() failed", name)


if QOpenGLWidget is None:  # pragma: no cover - executed when Qt OpenGL widget missing
    LiveScriptViewport = None  # type: ignore
else:

    class LiveScriptViewport(QOpenGLWidget):  # pragma: no cover - requires OpenGL context
        """OpenGL viewport that executes scripted hooks at a capped frame rate."""

        DEFAULT_FPS = 60.0
        MIN_FPS = 5.0
        MAX_FPS = 120.0
        RESOURCE_POLL_INTERVAL = 1.0
        CPU_THRESHOLD = 85.0
        MEMORY_THRESHOLD = 90.0

        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.setUpdateBehavior(QOpenGLWidget.PartialUpdate)
            self._controller = LiveScriptController(self)
            self._timer = QTimer(self)
            self._timer.setTimerType(Qt.PreciseTimer)
            self._timer.timeout.connect(self._tick)
            self._fps_cap = self.DEFAULT_FPS
            self._pending_dt = 0.0
            self._last_frame_time: Optional[float] = None
            self._needs_init = False
            self._heavy_checker: Optional[Callable[[], bool]] = None
            self._resource_flag = False
            self._last_resource_poll = 0.0

        # ---- configuration helpers -------------------------------------------------
        def set_script(self, path: Optional[str]) -> None:
            self._controller.set_script(path)
            self._needs_init = True
            self._last_frame_time = None
            if path:
                self._ensure_running()
            else:
                self.stop()

        def set_fps_cap(self, fps: float) -> None:
            fps = max(self.MIN_FPS, min(self.MAX_FPS, float(fps) if fps else self.DEFAULT_FPS))
            self._fps_cap = fps
            if self._timer.isActive():
                self._ensure_running()

        def set_heavy_process_checker(self, checker: Optional[Callable[[], bool]]) -> None:
            self._heavy_checker = checker

        def start(self) -> None:
            if not self._timer.isActive():
                self._ensure_running()

        def stop(self) -> None:
            self._timer.stop()

        # ---- Qt lifecycle ----------------------------------------------------------
        def initializeGL(self) -> None:
            self._needs_init = True
            self._last_frame_time = time.monotonic()

        def resizeGL(self, w: int, h: int) -> None:
            self._controller.call("resize", w, h)

        def paintGL(self) -> None:
            module = self._controller.module
            if module is None:
                return
            if self._needs_init and self.isValid():
                self._controller.call("init", self)
                self._needs_init = False
            dt = self._pending_dt
            if dt < 0:
                dt = 0.0
            self._controller.call("update", dt)
            self._controller.call("render", self)

        def showEvent(self, event):  # pragma: no cover - thin Qt wrapper
            super().showEvent(event)
            self._ensure_running()

        def hideEvent(self, event):  # pragma: no cover - thin Qt wrapper
            super().hideEvent(event)
            self.stop()

        # ---- internal helpers ------------------------------------------------------
        def _ensure_running(self) -> None:
            if not self._controller.module and not self._controller.script_path:
                return
            interval_ms = int(max(1.0, 1000.0 / self._fps_cap))
            self._timer.start(interval_ms)

        def _tick(self) -> None:
            changed = self._controller.reload_if_changed()
            if self._controller.module is None:
                return
            if changed:
                self._needs_init = True
            if not self._should_render():
                self._last_frame_time = None
                return
            now = time.monotonic()
            if self._last_frame_time is None:
                self._pending_dt = 0.0
            else:
                self._pending_dt = max(0.0, now - self._last_frame_time)
            self._last_frame_time = now
            self.update()

        def _should_render(self) -> bool:
            if not self.isVisible():
                return False
            window = self.window()
            if window is not None:
                if hasattr(window, "isMinimized") and window.isMinimized():
                    return False
                if not window.isVisible():
                    return False
            if self._heavy_checker and self._heavy_checker():
                return False
            now = time.monotonic()
            if now - self._last_resource_poll >= self.RESOURCE_POLL_INTERVAL:
                self._resource_flag = self._system_is_heavy()
                self._last_resource_poll = now
            if self._resource_flag:
                return False
            return True

        def _system_is_heavy(self) -> bool:
            if psutil is None:
                return False
            try:
                cpu = psutil.cpu_percent(interval=None)
                if cpu >= self.CPU_THRESHOLD:
                    return True
                mem = psutil.virtual_memory().percent
                return mem >= self.MEMORY_THRESHOLD
            except Exception:
                return False

