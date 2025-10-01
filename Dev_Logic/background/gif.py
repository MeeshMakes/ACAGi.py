"""Animated GIF background implementation."""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QLabel

from .base import BackgroundConfig, BackgroundFit, BackgroundLayer


class GifBg(BackgroundLayer):
    """Display an animated GIF behind desktop icons."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._label = QLabel(canvas)
        self._label.setObjectName("DesktopGifBackground")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._label.hide()
        self._movie: Optional[QMovie] = None
        self._config: Optional[BackgroundConfig] = None

    def start(self, config: BackgroundConfig) -> None:
        self._config = config
        if self._movie:
            self._movie.stop()
        if not (config.source and os.path.isfile(config.source)):
            self.stop()
            return
        movie = QMovie(config.source)
        if not movie.isValid():
            self.stop()
            return
        self._movie = movie
        self._label.setMovie(movie)
        self._label.show()
        self._label.lower()
        self.resize(self.canvas.size())
        movie.start()

    def stop(self) -> None:
        if self._movie:
            self._movie.stop()
        self._movie = None
        self._label.clear()
        self._label.hide()

    def resize(self, size: QSize) -> None:
        self._label.setGeometry(0, 0, size.width(), size.height())
        if not self._movie or not self._config:
            return
        fit = self._config.fit
        if fit == BackgroundFit.CENTER:
            self._label.setScaledContents(False)
            self._label.setAlignment(Qt.AlignCenter)
        else:
            self._label.setScaledContents(True)
            self._label.setAlignment(Qt.AlignCenter)
            self._movie.setScaledSize(size)

    def paint(self, *_args) -> bool:
        # Rendering handled by QLabel/QMovie.
        return bool(self._movie)
