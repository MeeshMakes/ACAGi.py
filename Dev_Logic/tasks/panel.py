from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Iterable, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
)

from .models import TASKS_FILE, Task, load_run_log_tail


STATUS_ORDER = [
    "all",
    "open",
    "merged",
    "closed",
    "cancelled",
    "failed",
    "deleted",
]


@dataclass(slots=True)
class _TaskRowData:
    task: Task
    matches_filter: bool = True


class _StatusPill(QLabel):
    """High-contrast badge representing a task status."""

    _PILL_STYLES = {
        "open": ("#1b8a5a", "#ffffff"),
        "merged": ("#6f42c1", "#ffffff"),
        "closed": ("#c0392b", "#ffffff"),
        "cancelled": ("#475061", "#ffffff"),
    }

    _TEXT_STYLES = {
        "failed": "#ff6b6b",
        "deleted": "#96a3bb",
    }

    def __init__(self, status: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        status_key = status.lower()
        font = QFont("Segoe UI", 9)
        font.setBold(True)
        self.setFont(font)
        if status_key in self._PILL_STYLES:
            bg, fg = self._PILL_STYLES[status_key]
            self.setText(status.capitalize())
            self.setStyleSheet(
                (
                    "QLabel{{padding:2px 8px;border-radius:8px;font-weight:600;"
                    "background:{bg};color:{fg};border:1px solid #0b1524;}}"
                ).format(bg=bg, fg=fg)
            )
        else:
            color = self._TEXT_STYLES.get(status_key, "#e9f3ff")
            self.setText(status.capitalize())
            self.setStyleSheet(
                (
                    "QLabel{{padding:0px;font-weight:600;"
                    "color:{color};background:transparent;}}"
                ).format(color=color)
            )


class _TaskRowWidget(QWidget):
    """Widget rendered inside the list view for each task."""

    def __init__(self, task: Task, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.task = task
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        self.pill = _StatusPill(task.status, self)
        layout.addWidget(self.pill)

        self.title = QLabel(task.title, self)
        self.title.setStyleSheet("color:#e9f3ff;font:600 10pt 'Segoe UI';")
        self.title.setWordWrap(True)
        layout.addWidget(self.title, 1)

        diff_text = _format_diff(task)
        self.diff = QLabel(diff_text, self)
        self.diff.setStyleSheet("color:#bcd5ff;font:500 9pt 'Segoe UI';")
        layout.addWidget(self.diff)

        ts_label = QLabel(_format_timestamp(task.updated_ts), self)
        ts_label.setStyleSheet("color:#8ea4c9;font:500 9pt 'Segoe UI';")
        layout.addWidget(ts_label)

        self.setAutoFillBackground(True)
        palette = self.palette()
        bg = QColor("#0c1320")
        palette.setColor(QPalette.Window, bg)
        self.setPalette(palette)


def _format_diff(task: Task) -> str:
    added = task.diffs.added if task.diffs else 0
    removed = task.diffs.removed if task.diffs else 0
    return f"+{added} \u2212{removed}"


def _format_timestamp(ts: float) -> str:
    try:
        dt = datetime.fromtimestamp(float(ts))
    except (TypeError, ValueError, OSError):
        return "--"
    return dt.strftime("%Y-%m-%d %H:%M")


class TaskPanel(QDockWidget):
    """Dockable Tasks panel shared by Terminal and Virtual Desktop."""

    task_selected = Signal(str)
    new_taskRequested = Signal(str)
    status_changed = Signal(str, str)
    load_conversationRequested = Signal(str, str)

    def __init__(self, dataset_path: str | Path | None = None, parent: Optional[QWidget] = None) -> None:
        super().__init__("Tasks", parent)
        self.setObjectName("TaskPanelDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.dataset_path = Path(dataset_path) if dataset_path else TASKS_FILE
        self._dataset_root = self.dataset_path.parent
        self._tasks: List[_TaskRowData] = []
        self._selected_task: Optional[Task] = None
        self._log_placeholder = "No run log entries yet."
        self._active_conversation_id: Optional[str] = None
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        container = QWidget(self)
        container.setObjectName("TaskPanelContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(8)
        self.filter_combo = QComboBox(container)
        self.filter_combo.addItems([status.capitalize() for status in STATUS_ORDER])
        self.filter_combo.currentIndexChanged.connect(self._apply_filters)
        self.filter_combo.setStyleSheet(
            "QComboBox{background:#0a111e;color:#eaf2ff;border:1px solid #1d2b3c;"
            "border-radius:6px;padding:4px 8px;}"
            "QComboBox QAbstractItemView{background:#0b1624;color:#eaf2ff;}"
        )
        header.addWidget(self.filter_combo)

        self.search_edit = QLineEdit(container)
        self.search_edit.setPlaceholderText("Search tasks…")
        self.search_edit.textChanged.connect(self._apply_filters)
        self.search_edit.setStyleSheet(
            "QLineEdit{background:#0b1624;color:#e9f3ff;border:1px solid #203040;"
            "border-radius:6px;padding:6px 10px;font:10pt 'Segoe UI';}"
            "QLineEdit:focus{border:1px solid #2f72ff;}"
        )
        header.addWidget(self.search_edit, 1)

        layout.addLayout(header)

        self.list = QListWidget(container)
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.itemSelectionChanged.connect(self._on_item_selected)
        self.list.setUniformItemSizes(False)
        self.list.setSpacing(4)
        self.list.setStyleSheet(
            "QListWidget{background:#0c1320;color:#e9f3ff;border:1px solid #1f2b3a;"
            "border-radius:8px;padding:4px;}"
            "QListWidget::item{margin:2px;padding:2px;border-radius:6px;}"
            "QListWidget::item:selected{background:#1f3a5b;}"
        )
        layout.addWidget(self.list, 1)

        self.detail = QFrame(container)
        self.detail.setFrameShape(QFrame.StyledPanel)
        self.detail.setObjectName("TaskDetailPopover")
        self.detail.setStyleSheet(
            "QFrame#TaskDetailPopover{background:#0b1624;border:1px solid #25405f;"
            "border-radius:10px;}"
        )
        detail_layout = QVBoxLayout(self.detail)
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(8)

        self.detail_title = QLabel("Select a task to view details", self.detail)
        self.detail_title.setStyleSheet("color:#eaf2ff;font:600 11pt 'Segoe UI';")
        self.detail_title.setWordWrap(True)
        detail_layout.addWidget(self.detail_title)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        status_label = QLabel("Status:", self.detail)
        status_label.setStyleSheet("color:#bcd5ff;font:500 9pt 'Segoe UI';")
        status_row.addWidget(status_label)

        self.status_combo = QComboBox(self.detail)
        for status in STATUS_ORDER[1:]:
            self.status_combo.addItem(status.capitalize(), status)
        self.status_combo.setStyleSheet(
            "QComboBox{background:#0a111e;color:#eaf2ff;border:1px solid #1d2b3c;"
            "border-radius:6px;padding:4px 8px;}"
            "QComboBox QAbstractItemView{background:#0b1624;color:#eaf2ff;}"
        )
        status_row.addWidget(self.status_combo, 1)

        self.status_apply = QPushButton("Update", self.detail)
        self.status_apply.clicked.connect(self._emit_status_change)
        self.status_apply.setStyleSheet(
            "QPushButton{background:#1E5AFF;color:#ffffff;border-radius:6px;"
            "padding:6px 12px;border:1px solid #1b3b73;font-weight:600;}"
            "QPushButton:hover{background:#2f72ff;}"
        )
        status_row.addWidget(self.status_apply)
        detail_layout.addLayout(status_row)

        self.detail_diff = QLabel("+0 \u22120", self.detail)
        self.detail_diff.setStyleSheet("color:#bcd5ff;font:500 9pt 'Segoe UI';")
        detail_layout.addWidget(self.detail_diff)

        self.detail_timestamps = QLabel("--", self.detail)
        self.detail_timestamps.setStyleSheet("color:#8ea4c9;font:500 9pt 'Segoe UI';")
        self.detail_timestamps.setWordWrap(True)
        detail_layout.addWidget(self.detail_timestamps)

        self.detail_labels = QLabel("", self.detail)
        self.detail_labels.setStyleSheet("color:#8ea4c9;font:500 9pt 'Segoe UI';")
        self.detail_labels.setWordWrap(True)
        detail_layout.addWidget(self.detail_labels)

        self.detail_log_label = QLabel("Run log", self.detail)
        self.detail_log_label.setStyleSheet("color:#bcd5ff;font:600 9pt 'Segoe UI';")
        detail_layout.addWidget(self.detail_log_label)

        self.detail_log = QPlainTextEdit(self.detail)
        self.detail_log.setReadOnly(True)
        self.detail_log.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.detail_log.setFont(QFont("Consolas", 9))
        self.detail_log.setStyleSheet(
            "QPlainTextEdit{background:#07101c;color:#e9f3ff;border:1px solid #203040;"
            "border-radius:6px;padding:8px;}"
        )
        self.detail_log.setFixedHeight(160)
        self.detail_log.setPlainText(self._log_placeholder)
        detail_layout.addWidget(self.detail_log)

        self.load_conversation_btn = QPushButton("Load Conversation", self.detail)
        self.load_conversation_btn.setEnabled(False)
        self.load_conversation_btn.setStyleSheet(
            "QPushButton{background:#1E5AFF;color:#ffffff;border-radius:6px;"
            "padding:6px 12px;border:1px solid #1b3b73;font-weight:600;}"
            "QPushButton:hover{background:#2f72ff;}"
            "QPushButton:disabled{background:#1b2c44;color:#6c7a96;border:1px solid #1b2c44;}"
        )
        self.load_conversation_btn.clicked.connect(self._emit_load_conversation)
        detail_layout.addWidget(self.load_conversation_btn, 0, Qt.AlignLeft)

        layout.addWidget(self.detail)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        self.new_task_input = QLineEdit(container)
        self.new_task_input.setPlaceholderText("Create new task…")
        self.new_task_input.returnPressed.connect(self._on_new_task_requested)
        self.new_task_input.setStyleSheet(
            "QLineEdit{background:#0b1624;color:#e9f3ff;border:1px solid #203040;"
            "border-radius:6px;padding:6px 10px;font:10pt 'Segoe UI';}"
            "QLineEdit:focus{border:1px solid #2f72ff;}"
        )
        footer.addWidget(self.new_task_input, 1)
        footer.addItem(QSpacerItem(12, 1, QSizePolicy.Fixed, QSizePolicy.Minimum))
        layout.addLayout(footer)

        container.setLayout(layout)
        self.setWidget(container)

        apply_palette(container)
        apply_palette(self.list)
        apply_palette(self.detail)
        apply_palette(self.new_task_input)
        apply_palette(self.search_edit)

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Reload tasks from the dataset path."""
        if not self.dataset_path.exists():
            self._tasks = []
            self._apply_filters()
            return
        records: List[Task] = []
        with self.dataset_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    records.append(Task.from_dict(payload))
                except json.JSONDecodeError:
                    continue
        self.set_tasks(records)

    # ------------------------------------------------------------------
    def set_tasks(self, tasks: Iterable[Task]) -> None:
        self._tasks = [_TaskRowData(task=task) for task in tasks]
        self._apply_filters()

    # ------------------------------------------------------------------
    def update_task(self, task: Task) -> None:
        for row in self._tasks:
            if row.task.id == task.id:
                row.task = task
                break
        else:
            self._tasks.append(_TaskRowData(task=task))
        self._apply_filters(preserve_selection=True)

    # ------------------------------------------------------------------
    def _apply_filters(self, preserve_selection: bool = False) -> None:
        search_text = self.search_edit.text().strip().lower()
        status_filter = STATUS_ORDER[self.filter_combo.currentIndex()]
        selected_id = self._selected_task.id if (preserve_selection and self._selected_task) else None

        self.list.blockSignals(True)
        self.list.clear()
        matched_task: Optional[Task] = None

        for row in self._tasks:
            task = row.task
            matches_status = status_filter == "all" or task.status.lower() == status_filter
            matches_search = not search_text or (
                search_text in task.title.lower()
                or search_text in task.id.lower()
                or any(search_text in label.lower() for label in task.labels)
            )
            row.matches_filter = matches_status and matches_search
            if not row.matches_filter:
                continue
            item = QListWidgetItem(self.list)
            item.setData(Qt.UserRole, task.id)
            widget = _TaskRowWidget(task, self.list)
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)
            if selected_id and task.id == selected_id:
                item.setSelected(True)
                matched_task = task

        self.list.blockSignals(False)
        if not preserve_selection or not matched_task:
            self._selected_task = None
            self.detail_title.setText("Select a task to view details")
            self.status_combo.blockSignals(True)
            self.status_combo.setCurrentIndex(0)
            self.status_combo.blockSignals(False)
            self.detail_diff.setText("+0 \u22120")
            self.detail_timestamps.setText("--")
            self.detail_labels.setText("")
            self._update_log_view(None)
            self._update_conversation_button(None)
        else:
            self._selected_task = matched_task
            self._populate_detail(matched_task)

    # ------------------------------------------------------------------
    def _on_item_selected(self) -> None:
        items = self.list.selectedItems()
        if not items:
            self._selected_task = None
            self._apply_filters()
            return
        task_id = items[0].data(Qt.UserRole)
        for row in self._tasks:
            if row.task.id == task_id:
                self._selected_task = row.task
                self._populate_detail(row.task)
                self.task_selected.emit(row.task.id)
                break

    # ------------------------------------------------------------------
    def _populate_detail(self, task: Task) -> None:
        self.detail_title.setText(task.title)
        status_index = self.status_combo.findData(task.status)
        self.status_combo.blockSignals(True)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
        else:
            self.status_combo.setCurrentIndex(0)
        self.status_combo.blockSignals(False)
        self.detail_diff.setText(_format_diff(task))
        created = _format_timestamp(task.created_ts)
        updated = _format_timestamp(task.updated_ts)
        self.detail_timestamps.setText(f"Created: {created}\nUpdated: {updated}")
        if task.labels:
            labels = ", ".join(task.labels)
            self.detail_labels.setText(f"Labels: {labels}")
        else:
            self.detail_labels.setText("")
        self._update_log_view(task)
        self._update_conversation_button(task)

    # ------------------------------------------------------------------
    def _emit_status_change(self) -> None:
        if not self._selected_task:
            return
        status = self.status_combo.currentData()
        if not status or status == self._selected_task.status:
            return
        self.status_changed.emit(self._selected_task.id, status)

    # ------------------------------------------------------------------
    def _on_new_task_requested(self) -> None:
        text = self.new_task_input.text().strip()
        if not text:
            return
        self.new_taskRequested.emit(text)
        self.new_task_input.clear()


    def _update_log_view(self, task: Optional[Task]) -> None:
        if not hasattr(self, "detail_log"):
            return
        if task is None:
            self.detail_log.setPlainText(self._log_placeholder)
            return
        lines = load_run_log_tail(task, self._dataset_root, max_lines=200)
        if lines:
            self.detail_log.setPlainText("\n".join(lines))
        else:
            self.detail_log.setPlainText(self._log_placeholder)
        scrollbar = self.detail_log.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def _update_conversation_button(self, task: Optional[Task]) -> None:
        if not hasattr(self, "load_conversation_btn"):
            return
        identifier: Optional[str] = None
        if task is not None:
            cid = (task.codex_conversation_id or "").strip()
            identifier = cid or (task.session_id or "").strip()
        self._active_conversation_id = identifier or None
        if identifier:
            self.load_conversation_btn.setEnabled(True)
            self.load_conversation_btn.setToolTip("Load the linked Codex transcript into the chat window.")
        else:
            self.load_conversation_btn.setEnabled(False)
            self.load_conversation_btn.setToolTip("No linked Codex conversation for this task.")

    def _emit_load_conversation(self) -> None:
        if not self._selected_task or not self._active_conversation_id:
            return
        self.load_conversationRequested.emit(self._selected_task.id, self._active_conversation_id)


def apply_palette(widget: QWidget) -> None:
    """Apply the high-contrast palette to the given widget."""

    palette = widget.palette()
    bg = QColor("#0c1320")
    fg = QColor("#e9f3ff")
    for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        palette.setColor(group, QPalette.Window, bg)
        palette.setColor(group, QPalette.WindowText, fg)
        palette.setColor(group, QPalette.Base, QColor("#0b1624"))
        palette.setColor(group, QPalette.Text, fg)
        palette.setColor(group, QPalette.Button, QColor("#1E5AFF"))
        palette.setColor(group, QPalette.ButtonText, QColor("#ffffff"))
        palette.setColor(group, QPalette.Highlight, QColor("#1f3a5b"))
        palette.setColor(group, QPalette.HighlightedText, QColor("#ffffff"))
    widget.setPalette(palette)
