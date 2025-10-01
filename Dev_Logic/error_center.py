"""Error Center card for the Virtual Desktop.

Provides filtered log tabs, severity highlighting, and task shortcuts
based on guidance from `concepts/dev_logic/Virtual_Desktop logic.md`.
"""

from __future__ import annotations

import html
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Optional, Sequence, Set

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QTextCursor, QTextOption
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from tasks.models import ErrorRecord, append_error_record

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class _CategoryProfile:
    name: str
    keywords: Sequence[str]


_CATEGORY_PROFILES: Sequence[_CategoryProfile] = (
    _CategoryProfile("Runtime", ("[runtime]", " runtime", "process", "worker", "card", "canvas")),
    _CategoryProfile("UI", ("[ui]", " ui", "widget", "qt", "paint", "hover", "button", "window", "start panel")),
    _CategoryProfile("I/O", ("[io]", "i/o", "io ", "filesystem", "disk", "read", "write", "socket", "network", "save", "load", "path")),
    _CategoryProfile("Security", ("[security]", " security", "auth", "permission", "policy", "denied", "sandbox")),
)

_SEVERITY_COLORS: Dict[str, str] = {
    "[ERROR]": "#ff5c5c",
    "[ERR]": "#ff5c5c",
    "[CRITICAL]": "#ff5c5c",
    "[WARN]": "#ffb347",
    "[WARNING]": "#ffb347",
}

_TASK_PATTERN = re.compile(r"task_id=([A-Za-z0-9_-]+)")
_LOG_LINE_PATTERN = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:,\d{3})?)\s+\[(?P<level>[A-Z]+)\]\s+(?P<msg>.*)$"
)
_PATH_PATTERN = re.compile(r"(?P<path>(?:[A-Za-z]:\\|/)[^\s]+)")
_ERROR_LEVELS = {"ERROR", "CRITICAL"}


class ErrorCenterCard(QWidget):
    """Movable Error Center card with filtered log tails."""

    task_requested = Signal(str)

    def __init__(
        self,
        theme,
        log_path: str,
        open_task: Optional[Callable[[str], None]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._log_path = log_path
        self._open_task_cb = open_task
        self._last_pos = 0
        self._buffer = ""
        self._latest_task_id: Optional[str] = None
        self._max_blocks = 2000
        self._tabs: Dict[str, QTextBrowser] = {}

        self.setObjectName("ErrorCenterCard")
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QLabel("Error Center")
        title.setStyleSheet("color:#eaf2ff;font:700 12pt 'Cascadia Code';")
        root.addWidget(title)

        self._tab_widget = QTabWidget(self)
        self._tab_widget.setTabPosition(QTabWidget.North)
        self._tab_widget.setDocumentMode(True)
        self._tab_widget.setStyleSheet(
            "QTabWidget::pane{border:1px solid #1f2b3a;border-radius:10px;}"
            "QTabBar::tab{background:#0b1624;color:#dfe9ff;padding:6px 12px;border:1px solid #1f2b3a;"
            "border-radius:8px;margin-right:4px;}"
            "QTabBar::tab:selected{background:#1e5aff;}"
        )
        root.addWidget(self._tab_widget, 1)

        for profile in _CATEGORY_PROFILES:
            view = QTextBrowser(self)
            view.setAcceptRichText(True)
            view.setOpenExternalLinks(False)
            view.setLineWrapMode(QTextEdit.NoWrap)
            view.setWordWrapMode(QTextOption.NoWrap)
            view.document().setDefaultStyleSheet(
                "body{font-family:'Cascadia Code',Consolas,monospace;font-size:10pt;"
                "color:%s;background:%s;}" % (self._theme.editor_fg, self._theme.editor_bg)
            )
            view.document().setMaximumBlockCount(self._max_blocks)
            view.setStyleSheet(
                "QTextBrowser{background:%s;color:%s;border:1px solid %s;border-radius:10px;padding:8px;}" % (
                    self._theme.editor_bg,
                    self._theme.editor_fg,
                    self._theme.card_border,
                )
            )
            self._tab_widget.addTab(view, profile.name)
            self._tabs[profile.name] = view

        footer = QHBoxLayout()
        footer.setSpacing(8)
        self._task_label = QLabel("No task reference detected.")
        self._task_label.setStyleSheet("color:#bcd5ff;font:500 9pt 'Segoe UI';")
        footer.addWidget(self._task_label, 1)

        self._task_button = QPushButton("Open related task")
        self._task_button.setEnabled(False)
        self._task_button.setStyleSheet(
            "QPushButton{background:%s;color:#ffffff;border:1px solid %s;border-radius:6px;padding:6px 12px;}"
            "QPushButton:disabled{background:#1b2c44;color:#6c7a96;border:1px solid #1b2c44;}"
            % (self._theme.accent, self._theme.card_border)
        )
        self._task_button.clicked.connect(self._handle_task_button)
        footer.addWidget(self._task_button, 0)
        root.addLayout(footer)

        self._timer = QTimer(self)
        self._timer.setInterval(800)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        QTimer.singleShot(0, self.refresh)

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Read any new log bytes and append them to the tab views."""

        chunk = ""
        try:
            with open(self._log_path, "r", encoding="utf-8", errors="replace") as fh:
                fh.seek(self._last_pos)
                chunk = fh.read()
                self._last_pos = fh.tell()
        except FileNotFoundError:
            return
        except Exception as exc:  # pragma: no cover - defensive guard
            LOGGER.debug("ErrorCenter refresh failed: %s", exc)
            return

        if not chunk:
            return

        text = self._buffer + chunk
        lines = text.splitlines()
        if text and not text.endswith("\n"):
            self._buffer = lines[-1] if lines else text
            lines = lines[:-1]
        else:
            self._buffer = ""

        for line in lines:
            self._process_line(line)

    # ------------------------------------------------------------------
    def _process_line(self, line: str) -> None:
        categories = self._categorise(line)
        formatted = self._format_line(line)
        task_id = self._extract_task_id(line)
        parsed = self._parse_log_line(line)

        for name in categories:
            view = self._tabs.get(name)
            if not view:
                continue
            view.append(f"<span>{formatted}</span>")
            view.moveCursor(QTextCursor.End)

        if task_id:
            self._latest_task_id = task_id
            self._task_label.setText(f"Latest task reference: {task_id}")
            self._task_button.setEnabled(True)
        elif self._latest_task_id is None:
            self._task_label.setText("No task reference detected.")
            self._task_button.setEnabled(False)

        if parsed and parsed[1] in _ERROR_LEVELS:
            self._persist_error(parsed, categories, task_id)

    # ------------------------------------------------------------------
    def _categorise(self, line: str) -> Set[str]:
        lowered = line.lower()
        matches: Set[str] = set()
        for profile in _CATEGORY_PROFILES:
            if any(keyword in lowered for keyword in profile.keywords):
                matches.add(profile.name)
        if not matches:
            matches.add("Runtime")
        return matches

    # ------------------------------------------------------------------
    def _format_line(self, line: str) -> str:
        safe = html.escape(line.rstrip())
        for token, color in _SEVERITY_COLORS.items():
            if token in safe:
                safe = safe.replace(token, f"<span style='color:{color};font-weight:600;'>{token}</span>")
        return safe

    # ------------------------------------------------------------------
    def _extract_task_id(self, line: str) -> Optional[str]:
        match = _TASK_PATTERN.search(line)
        if match:
            return match.group(1)
        return None

    # ------------------------------------------------------------------
    def _parse_log_line(self, line: str) -> Optional[tuple[str, str, str]]:
        match = _LOG_LINE_PATTERN.match(line.strip())
        if not match:
            return None
        return match.group("ts"), match.group("level"), match.group("msg")

    # ------------------------------------------------------------------
    def _extract_path(self, message: str) -> Optional[str]:
        match = _PATH_PATTERN.search(message)
        if match:
            return match.group("path")
        return None

    # ------------------------------------------------------------------
    def _primary_category(self, categories: Set[str]) -> str:
        if not categories:
            return "Runtime"
        ordered = sorted(categories)
        for name in ordered:
            if name != "Runtime":
                return name
        return ordered[0]

    # ------------------------------------------------------------------
    def _persist_error(
        self,
        parsed: tuple[str, str, str],
        categories: Set[str],
        task_id: Optional[str],
    ) -> None:
        ts_raw, level, message = parsed
        try:
            dt = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S,%f")
            ts_value = dt.timestamp()
        except ValueError:
            try:
                dt = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S")
                ts_value = dt.timestamp()
            except ValueError:
                ts_value = datetime.utcnow().timestamp()
        kind = self._primary_category(categories)
        path = self._extract_path(message)
        record = ErrorRecord(
            ts=ts_value,
            level=level,
            kind=kind,
            msg=message,
            path=path,
            task_id=task_id,
        )
        try:
            append_error_record(record)
        except Exception as exc:  # pragma: no cover - persistence guard
            LOGGER.debug("Unable to persist error record: %s", exc)

    # ------------------------------------------------------------------
    def _handle_task_button(self) -> None:
        if not self._latest_task_id:
            return
        task_id = self._latest_task_id
        self.task_requested.emit(task_id)
        if self._open_task_cb:
            try:
                self._open_task_cb(task_id)
            except Exception as exc:  # pragma: no cover - guard callbacks
                LOGGER.debug("Error Center task callback failed: %s", exc)

    # ------------------------------------------------------------------
    def set_open_task_callback(self, callback: Optional[Callable[[str], None]]) -> None:
        """Update the callback invoked when the related-task button is clicked."""

        self._open_task_cb = callback
        if callback is None:
            self._task_button.setEnabled(False)
            self._task_label.setText("Task integration unavailable.")
