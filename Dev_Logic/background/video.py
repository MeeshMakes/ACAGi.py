"""Video background implementation."""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, QSize, QUrl

try:  # QtMultimedia may be missing in minimal environments
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
    from PySide6.QtMultimediaWidgets import QVideoWidget
except Exception:  # pragma: no cover - optional dependency guard
    QAudioOutput = None  # type: ignore
    QMediaPlayer = None  # type: ignore
    QVideoWidget = None  # type: ignore

from .base import BackgroundConfig, BackgroundLayer


class VideoBg(BackgroundLayer):
    """Loop a muted video behind the desktop icons."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._player: Optional[QMediaPlayer] = None
        self._audio: Optional[QAudioOutput] = None
        self._widget: Optional[QVideoWidget] = None
        self._config: Optional[BackgroundConfig] = None

    # Helper to lazily construct multimedia stack
    def _ensure_stack(self) -> bool:
        if QMediaPlayer is None or QVideoWidget is None or QAudioOutput is None:
            return False
        if self._player is None:
            self._player = QMediaPlayer(self.canvas)
            self._audio = QAudioOutput(self.canvas)
            self._player.setAudioOutput(self._audio)
            self._widget = QVideoWidget(self.canvas)
            self._widget.setObjectName("DesktopVideoBackground")
            self._widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self._widget.hide()
            self._player.mediaStatusChanged.connect(self._handle_status)
        return True

    def start(self, config: BackgroundConfig) -> None:
        self._config = config
        if not (config.source and os.path.isfile(config.source)):
            self.stop()
            return
        if not self._ensure_stack():
            self.stop()
            return
        assert self._player and self._widget and self._audio  # satisfy type checkers
        self._player.stop()
        self._player.setSource(QUrl.fromLocalFile(config.source))
        try:
            loops = -1 if config.loop else 1
            self._player.setLoops(loops)
        except Exception:
            pass
        self._audio.setMuted(bool(config.mute))
        self._player.setPlaybackRate(config.playback_rate or 1.0)
        self._widget.show()
        self._widget.lower()
        self.resize(self.canvas.size())
        self._player.play()

    def stop(self) -> None:
        if self._player:
            self._player.stop()
        if self._widget:
            self._widget.hide()
        self._config = None

    def resize(self, size: QSize) -> None:
        if self._widget:
            self._widget.setGeometry(0, 0, size.width(), size.height())

    def paint(self, *_args) -> bool:
        return bool(self._widget and self._widget.isVisible())

    def _handle_status(self, status) -> None:  # pragma: no cover - signal callback
        if not self._player or not self._config or QMediaPlayer is None:
            return
        try:
            end_status = QMediaPlayer.MediaStatus.EndOfMedia
        except Exception:  # Fallback for older Qt
            end_status = getattr(QMediaPlayer, "EndOfMedia", None)
        if getattr(self._config, "loop", True) and status == end_status:
            self._player.setPosition(0)
            self._player.play()
