"""Static image background implementation."""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QBrush

from .base import BackgroundConfig, BackgroundFit, BackgroundLayer


class StaticImageBg(BackgroundLayer):
    """Render a still image as the desktop background."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._pixmap: Optional[QPixmap] = None
        self._config: Optional[BackgroundConfig] = None

    def start(self, config: BackgroundConfig) -> None:
        self._config = config
        if config.source and os.path.isfile(config.source):
            pixmap = QPixmap(config.source)
            self._pixmap = pixmap if not pixmap.isNull() else None
        else:
            self._pixmap = None

    def stop(self) -> None:
        self._pixmap = None

    def paint(self, painter: QPainter, rect: QRect) -> bool:
        if not self._pixmap or not self._config:
            return False
        fit = self._config.fit
        if fit == BackgroundFit.TILE:
            brush = QBrush(self._pixmap)
            painter.fillRect(rect, brush)
            return True
        if fit == BackgroundFit.CENTER:
            target = self._pixmap.rect()
            target.moveCenter(rect.center())
            painter.drawPixmap(target, self._pixmap)
            return True
        mode = Qt.KeepAspectRatio
        if fit == BackgroundFit.FILL:
            mode = Qt.KeepAspectRatioByExpanding
        scaled = self._pixmap.scaled(rect.size(), mode, Qt.SmoothTransformation)
        painter.drawPixmap(rect, scaled)
        return True
