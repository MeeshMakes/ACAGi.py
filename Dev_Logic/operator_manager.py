"""Operator Manager registry and Qt panel for Codex-Local agents."""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
)

from prompt_loader import get_prompt_watcher


@dataclass
class OperatorRecord:
    """Metadata tracked for a single operator."""

    name: str
    role: str
    prompt_path: Optional[str] = None
    restart_callback: Optional[Callable[[], None]] = None
    status: str = "offline"
    status_detail: str = ""

    def clone(self) -> "OperatorRecord":
        return OperatorRecord(
            name=self.name,
            role=self.role,
            prompt_path=self.prompt_path,
            restart_callback=self.restart_callback,
            status=self.status,
            status_detail=self.status_detail,
        )


class OperatorManager(QObject):
    """Central registry that maintains agent metadata and emits status signals."""

    status_changed = Signal(str, str, str)  # name, status, detail
    operator_registered = Signal(str)
    operator_removed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._operators: Dict[str, OperatorRecord] = {}
        self._lock = threading.RLock()

    # -------- registry helpers --------
    def register(
        self,
        name: str,
        role: str,
        prompt_path: Optional[str] = None,
        restart_callback: Optional[Callable[[], None]] = None,
        status: str = "offline",
        status_detail: str = "",
    ) -> None:
        """Register or update an operator."""
        with self._lock:
            record = self._operators.get(name)
            is_new = record is None
            if is_new:
                record = OperatorRecord(
                    name=name,
                    role=role,
                    prompt_path=prompt_path,
                    restart_callback=restart_callback,
                    status=status,
                    status_detail=status_detail,
                )
                self._operators[name] = record
            else:
                record.role = role
                record.prompt_path = prompt_path
                record.restart_callback = restart_callback
                record.status = status
                record.status_detail = status_detail
        if is_new:
            self.operator_registered.emit(name)
        self.status_changed.emit(name, status, status_detail)

    def remove(self, name: str) -> None:
        with self._lock:
            if name not in self._operators:
                return
            del self._operators[name]
        self.operator_removed.emit(name)

    def list_records(self) -> Iterable[OperatorRecord]:
        with self._lock:
            return [rec.clone() for rec in self._operators.values()]

    def get(self, name: str) -> Optional[OperatorRecord]:
        with self._lock:
            record = self._operators.get(name)
            return record.clone() if record else None

    # -------- status helpers --------
    def update_status(self, name: str, status: str, detail: str = "") -> None:
        with self._lock:
            record = self._operators.get(name)
            if not record:
                return
            record.status = status
            record.status_detail = detail
        self.status_changed.emit(name, status, detail)

    def restart(self, name: str) -> bool:
        callback: Optional[Callable[[], None]]
        with self._lock:
            record = self._operators.get(name)
            if not record or not record.restart_callback:
                return False
            callback = record.restart_callback
        try:
            callback()  # type: ignore[operator]
            return True
        except Exception:
            raise


_manager_singleton: Optional[OperatorManager] = None


def get_operator_manager() -> OperatorManager:
    global _manager_singleton
    if _manager_singleton is None:
        _manager_singleton = OperatorManager()
    return _manager_singleton


_STATUS_COLORS: Dict[str, str] = {
    "idle": "#4caf50",
    "busy": "#ffb300",
    "listening": "#42a5f5",
    "error": "#ef5350",
    "offline": "#78909c",
}


class _StatusDot(QFrame):
    def __init__(self, color: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self.set_color(color)

    def set_color(self, color: str) -> None:
        self.setStyleSheet(
            f"background:{color}; border-radius:7px; border:1px solid rgba(0,0,0,0.4);"
        )


class _PromptDialog(QDialog):
    def __init__(self, title: str, path: Optional[str], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(640, 480)
        layout = QVBoxLayout(self)
        text = QPlainTextEdit(self)
        text.setReadOnly(True)
        font = QFont("Cascadia Code", 10)
        text.setFont(font)
        if path and os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    text.setPlainText(fh.read())
            except Exception as exc:  # pragma: no cover - UI feedback only
                text.setPlainText(f"[Failed to load prompt]\n{exc}")
        else:
            pretty = Path(path).name if path else "prompt"
            text.setPlainText(f"No prompt file found for {pretty}.")
        layout.addWidget(text, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.Close, Qt.Horizontal, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class _OperatorRow(QFrame):
    def __init__(
        self,
        record: OperatorRecord,
        manager: OperatorManager,
        theme: Optional[object] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._record = record
        self._manager = manager
        self._theme = theme
        self.setObjectName("OperatorRow")
        bg = getattr(theme, "card_bg", "#0c1320")
        border = getattr(theme, "card_border", "#1f2a3a")
        text_fg = getattr(theme, "text_body", "#e8f1ff")
        muted = getattr(theme, "text_muted", "#b9c5db")
        accent = getattr(theme, "accent", "#1E5AFF")
        self.setStyleSheet(
            f"QFrame#OperatorRow{{background:{bg};border:1px solid {border};border-radius:10px;}}"
            f"QFrame#OperatorRow QLabel{{color:{text_fg};}}"
            f"QFrame#OperatorRow QLabel.status-detail{{color:{muted};font-size:10pt;}}"
            f"QFrame#OperatorRow QPushButton{{background:{accent};color:#fff;border:1px solid {border};border-radius:6px;padding:6px 12px;}}"
            f"QFrame#OperatorRow QPushButton:hover{{background:{getattr(theme, 'accent_hov', '#2f72ff')};}}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout(); header.setSpacing(8)
        name_label = QLabel(record.name, self)
        font = QFont(); font.setPointSize(12); font.setBold(True)
        name_label.setFont(font)
        header.addWidget(name_label)
        header.addStretch(1)
        self._dot = _StatusDot(_STATUS_COLORS.get(record.status, "#607d8b"), self)
        header.addWidget(self._dot, 0)
        self._status_label = QLabel(record.status.title(), self)
        header.addWidget(self._status_label, 0)
        layout.addLayout(header)

        role_label = QLabel(record.role, self)
        role_label.setWordWrap(True)
        layout.addWidget(role_label)

        self._detail = QLabel(record.status_detail or "", self)
        self._detail.setObjectName("status-detail")
        self._detail.setWordWrap(True)
        if not record.status_detail:
            self._detail.hide()
        layout.addWidget(self._detail)

        buttons = QHBoxLayout(); buttons.setSpacing(8)
        self._restart_btn = QPushButton("Restart", self)
        self._restart_btn.clicked.connect(self._on_restart)
        self._prompt_btn = QPushButton("View Prompt", self)
        self._prompt_btn.clicked.connect(self._on_prompt)
        for btn in (self._restart_btn, self._prompt_btn):
            buttons.addWidget(btn)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        if record.restart_callback is None:
            self._restart_btn.setEnabled(False)

    def update_status(self, status: str, detail: str) -> None:
        self._status_label.setText(status.title())
        color = _STATUS_COLORS.get(status, "#607d8b")
        self._dot.set_color(color)
        if detail:
            self._detail.setText(detail)
            self._detail.show()
        else:
            self._detail.hide()

    def _on_restart(self) -> None:
        try:
            ok = self._manager.restart(self._record.name)
        except Exception as exc:  # pragma: no cover - user feedback only
            QMessageBox.critical(self, "Restart failed", str(exc))
            return
        if not ok:
            QMessageBox.information(self, "Restart", "No restart hook registered.")

    def _on_prompt(self) -> None:
        dlg = _PromptDialog(f"{self._record.name} Prompt", self._record.prompt_path, self)
        dlg.exec()


class OperatorManagerWidget(QWidget):
    """Scrollable list of operator rows bound to the OperatorManager singleton."""

    def __init__(self, theme: Optional[object] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._manager = get_operator_manager()
        self._rows: Dict[str, _OperatorRow] = {}
        self.setObjectName("OperatorManagerWidget")
        bg = getattr(theme, "card_bg", "#0c1320")
        border = getattr(theme, "card_border", "#1f2a3a")
        fg = getattr(theme, "text_body", "#e8f1ff")
        self.setStyleSheet(
            f"QWidget#OperatorManagerWidget{{background:{bg};border:1px solid {border};border-radius:12px;}}"
            f"QWidget#OperatorManagerWidget QLabel{{color:{fg};}}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("Operator Manager", self)
        title_font = QFont(); title_font.setPointSize(14); title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title, 0)

        subtitle = QLabel("Monitor and control Codex-Local agents.", self)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(scroll, 1)

        container = QWidget(scroll)
        self._rows_layout = QVBoxLayout(container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(10)
        scroll.setWidget(container)

        hint = QLabel("Status updates stream live from registered agents.", self)
        hint.setWordWrap(True)
        layout.addWidget(hint, 0)

        self._manager.operator_registered.connect(self._on_registered)
        self._manager.operator_removed.connect(self._on_removed)
        self._manager.status_changed.connect(self._on_status)

        for record in self._manager.list_records():
            self._add_row(record)

    def _add_row(self, record: OperatorRecord) -> None:
        if record.name in self._rows:
            row = self._rows[record.name]
            row.update_status(record.status, record.status_detail)
            return
        row = _OperatorRow(record, self._manager, self._theme, self)
        self._rows[record.name] = row
        self._rows_layout.addWidget(row)

    def _on_registered(self, name: str) -> None:
        record = self._manager.get(name)
        if record:
            self._add_row(record)

    def _on_removed(self, name: str) -> None:
        row = self._rows.pop(name, None)
        if row:
            row.setParent(None)
            row.deleteLater()

    def _on_status(self, name: str, status: str, detail: str) -> None:
        row = self._rows.get(name)
        if row:
            row.update_status(status, detail)


def _prompt_path_for(slug: str) -> Optional[str]:
    try:
        watcher = get_prompt_watcher(slug)
    except KeyError:
        return None
    return str(watcher.base_path)


def ensure_default_operators() -> None:
    manager = get_operator_manager()
    manager.register(
        name="Codex",
        role="Code agent that executes commands and edits files.",
        prompt_path=_prompt_path_for("codex_system"),
        status="idle",
    )
    manager.register(
        name="Chat",
        role="Conversational assistant for analysis, explanations, and planning.",
        prompt_path=_prompt_path_for("chat_system"),
        status="idle",
    )
    manager.register(
        name="Voice",
        role="Speech interface handling microphone input and spoken output.",
        prompt_path=_prompt_path_for("voice_system"),
        status="offline",
    )


# Initialize defaults on import so other modules can update immediately.
ensure_default_operators()
