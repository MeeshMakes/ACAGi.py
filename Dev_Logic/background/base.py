"""Background layer abstractions for the Virtual Desktop."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Optional

from PySide6.QtCore import QObject, QSize
from PySide6.QtGui import QPainter


class BackgroundMode(str, Enum):
    """Supported background layer types."""

    SOLID = "solid"
    STATIC = "image"
    GIF = "gif"
    VIDEO = "video"
    GL = "gl"


class BackgroundFit(str, Enum):
    """Scaling strategies for image-backed backgrounds."""

    FILL = "fill"
    FIT = "fit"
    CENTER = "center"
    TILE = "tile"


@dataclass
class BackgroundConfig:
    """Runtime configuration for a background layer."""

    mode: BackgroundMode = BackgroundMode.SOLID
    source: str = ""
    fit: BackgroundFit = BackgroundFit.FILL
    loop: bool = True
    mute: bool = True
    playback_rate: float = 1.0

    @classmethod
    def from_state(cls, raw: object) -> "BackgroundConfig":
        """Create a config from the persisted vd_state entry."""

        if isinstance(raw, dict):
            mode = raw.get("mode", BackgroundMode.SOLID)
            source = raw.get("source", "")
            fit = raw.get("fit", BackgroundFit.FILL)
            loop = bool(raw.get("loop", True))
            mute = bool(raw.get("mute", True))
            try:
                playback_rate = float(raw.get("playback_rate", 1.0))
            except Exception:
                playback_rate = 1.0
        elif isinstance(raw, str) and raw:
            mode = BackgroundMode.STATIC
            source = raw
            fit = BackgroundFit.FILL
            loop = True
            mute = True
            playback_rate = 1.0
        else:
            mode = BackgroundMode.SOLID
            source = ""
            fit = BackgroundFit.FILL
            loop = True
            mute = True
            playback_rate = 1.0

        try:
            mode = BackgroundMode(mode)
        except Exception:
            mode = BackgroundMode.SOLID
        try:
            fit = BackgroundFit(fit)
        except Exception:
            fit = BackgroundFit.FILL
        return cls(mode=mode, source=source, fit=fit, loop=loop, mute=mute, playback_rate=playback_rate)

    def to_state(self) -> Dict[str, object]:
        """Serialize to vd_state-compatible dictionary."""

        return {
            "mode": self.mode.value,
            "source": self.source,
            "fit": self.fit.value,
            "loop": bool(self.loop),
            "mute": bool(self.mute),
            "playback_rate": float(self.playback_rate),
        }


class BackgroundLayer(QObject):
    """Interface implemented by background layer engines."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas

    def start(self, config: BackgroundConfig) -> None:
        """Activate the background using the provided configuration."""

    def stop(self) -> None:
        """Deactivate the background and release resources."""

    def paint(self, painter: QPainter, rect) -> bool:  # pragma: no cover - tiny wrapper
        """Draw into the canvas. Return True if painting handled."""

        return False

    def resize(self, size: QSize) -> None:
        """Resize hook used by the canvas when it changes dimensions."""


class BackgroundManager(QObject):
    """Lifecycle coordinator for desktop background layers."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self._factories: Dict[BackgroundMode, Callable[[object], BackgroundLayer]] = {}
        self._instances: Dict[BackgroundMode, BackgroundLayer] = {}
        self._active: Optional[BackgroundLayer] = None
        self._active_mode: Optional[BackgroundMode] = None

    def register(self, mode: BackgroundMode, factory: Callable[[object], BackgroundLayer]) -> None:
        self._factories[mode] = factory

    def apply(self, config: Optional[BackgroundConfig]) -> None:
        if config is None:
            self.clear()
            return
        if self._active and self._active_mode != config.mode:
            self._active.stop()
            self._active = None
            self._active_mode = None
        factory = self._factories.get(config.mode)
        if factory is None:
            self.clear()
            return
        layer = self._instances.get(config.mode)
        if layer is None:
            layer = factory(self.canvas)
            self._instances[config.mode] = layer
        self._active = layer
        self._active_mode = config.mode
        layer.start(config)
        layer.resize(self.canvas.size())
        self.canvas.update()

    def clear(self) -> None:
        if self._active:
            self._active.stop()
        self._active = None
        self._active_mode = None
        self.canvas.update()

    def paint(self, painter: QPainter, rect) -> bool:
        if self._active:
            return bool(self._active.paint(painter, rect))
        return False

    def resize(self, size: QSize) -> None:
        if self._active:
            self._active.resize(size)

    @property
    def active_mode(self) -> Optional[BackgroundMode]:
        return self._active_mode
