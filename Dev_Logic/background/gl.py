"""Programmable OpenGL background layer."""

from __future__ import annotations

import logging
from typing import Callable, Optional, TYPE_CHECKING

from PySide6.QtCore import QSize

from .base import BackgroundConfig, BackgroundLayer
from .live_engine import LiveScriptViewport

LOGGER = logging.getLogger("VirtualDesktop.GLBackground")

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .live_engine import LiveScriptViewport as _ViewportType


class GLViewportBg(BackgroundLayer):
    """Host a programmable OpenGL viewport as the background."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._viewport: Optional["_ViewportType"] = None
        self._config: Optional[BackgroundConfig] = None

    def _ensure_viewport(self) -> bool:
        if LiveScriptViewport is None:
            LOGGER.warning("Qt OpenGL widgets unavailable; GL background disabled")
            return False
        if self._viewport is None:
            self._viewport = LiveScriptViewport(self.canvas)
            self._viewport.setObjectName("DesktopGLViewport")
            self._viewport.hide()
        checker = self._resolve_heavy_checker()
        if checker:
            self._viewport.set_heavy_process_checker(checker)
        return True

    def start(self, config: BackgroundConfig) -> None:
        self._config = config
        if not (config.source and self._ensure_viewport()):
            self.stop()
            return
        assert self._viewport is not None
        try:
            base_fps = LiveScriptViewport.DEFAULT_FPS if LiveScriptViewport else 60.0
            playback = float(config.playback_rate or 1.0)
            fps = max(LiveScriptViewport.MIN_FPS, min(LiveScriptViewport.MAX_FPS, base_fps * playback))
        except Exception:
            fps = LiveScriptViewport.DEFAULT_FPS if LiveScriptViewport else 60.0
        self._viewport.set_fps_cap(fps)
        self._viewport.set_script(config.source)
        checker = self._resolve_heavy_checker()
        if checker:
            self._viewport.set_heavy_process_checker(checker)
        self._viewport.show()
        self._viewport.lower()
        self.resize(self.canvas.size())
        self._viewport.start()

    def stop(self) -> None:
        if self._viewport:
            self._viewport.stop()
            self._viewport.hide()
        self._config = None

    def resize(self, size: QSize) -> None:
        if self._viewport:
            self._viewport.setGeometry(0, 0, size.width(), size.height())

    def paint(self, *_args) -> bool:
        return bool(self._viewport and self._viewport.isVisible())

    def _resolve_heavy_checker(self) -> Optional[Callable[[], bool]]:
        if self.canvas is None or self.canvas.window() is None:
            return None
        window = self.canvas.window()
        checker = getattr(window, "is_heavy_process_active", None)
        if callable(checker):
            return lambda: bool(checker())
        return None
