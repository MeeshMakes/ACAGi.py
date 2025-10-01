from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, List, Optional, Sequence

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .bus import Subscription, publish, subscribe
from .models import TASKS_FILE, Task, TaskEvent, append_event, update_task
from .panel import TaskPanel
from tools.system_metrics import SystemMetricsJob

logger = logging.getLogger(__name__)

__all__ = [
    "TaskManager",
    "TaskCard",
    "open_card",
]


class TaskManager:
    """Lightweight loader for task dataset records."""

    def __init__(self, dataset_path: str | Path | None = None, workspace_root: str | Path | None = None) -> None:
        path = Path(dataset_path) if dataset_path else TASKS_FILE
        self.dataset_path = path
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        self._workspace_root: Optional[Path] = Path(workspace_root).resolve() if workspace_root else None
        self._metrics_job: Optional[SystemMetricsJob] = None

    # ------------------------------------------------------------------
    def set_workspace(self, workspace_root: str | Path | None) -> None:
        """Update the workspace root used for resolving relative paths."""

        self._workspace_root = Path(workspace_root).resolve() if workspace_root else None

    # ------------------------------------------------------------------
    def list_tasks(self) -> List[Task]:
        """Return all task entries from the dataset."""

        if not self.dataset_path.exists():
            return []
        tasks: List[Task] = []
        with self.dataset_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                try:
                    tasks.append(Task.from_dict(payload))
                except Exception:
                    logger.debug("Skipping malformed task payload: %r", payload)
        return tasks

    # ------------------------------------------------------------------
    def get_task(self, task_id: str) -> Optional[Task]:
        """Return a single task by identifier."""

        for task in self.list_tasks():
            if task.id == task_id:
                return task
        return None

    # ------------------------------------------------------------------
    def resolve_path(self, candidate: Optional[str]) -> Optional[Path]:
        """Resolve ``candidate`` against the workspace root if needed."""

        if not candidate:
            return None
        path = Path(candidate)
        if not path.is_absolute():
            base = self._workspace_root or Path.cwd()
            path = base / path
        return path

    # ------------------------------------------------------------------
    def start_system_metrics_job(
        self,
        interval_seconds: int = 900,
        *,
        targets: Optional[Sequence[str | Path]] = None,
    ) -> None:
        """Start a background job that refreshes system metrics periodically."""

        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self.stop_system_metrics_job()

        datasets_root = self.dataset_path.parent

        def _publish(summary: dict) -> None:
            try:
                components = summary.get("components", {})
                publish(
                    "system.metrics",
                    {
                        "generated_at": summary.get("generated_at"),
                        "components": list(components.keys()),
                    },
                )
            except Exception:
                logger.exception("Failed to publish system metrics summary")

        job = SystemMetricsJob(
            interval=float(interval_seconds),
            targets=targets,
            datasets_root=datasets_root,
            db_path=datasets_root / "system_metrics.db",
            publish_callback=_publish,
        )
        self._metrics_job = job
        job.start()

    # ------------------------------------------------------------------
    def stop_system_metrics_job(self) -> None:
        """Stop the background system metrics refresher if active."""

        if self._metrics_job is not None:
            try:
                self._metrics_job.stop()
            finally:
                self._metrics_job = None


class TaskCard(QWidget):
    """Card widget presenting global task list with contextual actions."""

    def __init__(
        self,
        manager: TaskManager,
        theme,
        open_editor: Callable[[str], None],
        open_terminal: Optional[Callable[[str], None]] = None,
        workspace_root: str | Path | None = None,
        source: str = "desktop",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.manager = manager
        self.manager.set_workspace(workspace_root)
        self._theme = theme
        self._open_editor = open_editor
        self._open_terminal = open_terminal
        self._source = source
        self._selected_task: Optional[Task] = None
        self._subscriptions: List[Subscription] = []

        self.setObjectName("TasksCard")
        self.setStyleSheet(
            (
                "QWidget#TasksCard{background:#0c1320;border:1px solid #1f2b3a;border-radius:12px;}"
                "QLabel{color:#e9f3ff;}"
            )
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Tasks — All Sessions", self)
        header.setStyleSheet("font:700 12pt 'Segoe UI'; color:#eaf2ff;")
        layout.addWidget(header)

        self.panel = TaskPanel(manager.dataset_path, self)
        # Disable inline creation to keep desktop card focused on review/actions.
        self.panel.new_task_input.setEnabled(False)
        self.panel.new_task_input.setPlaceholderText("Create tasks from Codex Terminal runs.")
        layout.addWidget(self.panel, 1)

        action_frame = QFrame(self)
        action_frame.setObjectName("TasksCardActions")
        action_frame.setStyleSheet(
            (
                "QFrame#TasksCardActions{background:#0a111e;border:1px solid #1d2b3c;"
                "border-radius:10px;}"
            )
        )
        action_row = QHBoxLayout(action_frame)
        action_row.setContentsMargins(12, 10, 12, 10)
        action_row.setSpacing(10)

        self.btn_open_editor = QPushButton("Open in Editor", action_frame)
        self.btn_open_terminal = QPushButton("Open Terminal", action_frame)
        self.btn_archive = QPushButton("Archive", action_frame)

        button_style = (
            "QPushButton{{background:{accent};color:#ffffff;border-radius:6px;"
            "border:1px solid {border};padding:6px 14px;font-weight:600;}}"
            "QPushButton:hover{{background:{accent_hov};}}"
            "QPushButton:disabled{{background:#1b2c44;color:#6c7a96;border:1px solid #1b2c44;}}"
        ).format(
            accent=self._theme.accent,
            border=self._theme.card_border,
            accent_hov=self._theme.accent_hov,
        )
        for btn in (self.btn_open_editor, self.btn_open_terminal, self.btn_archive):
            btn.setStyleSheet(button_style)
            action_row.addWidget(btn)

        action_row.addStretch(1)
        layout.addWidget(action_frame)

        self.panel.task_selected.connect(self._on_task_selected)
        self.panel.status_changed.connect(self._apply_status_change)
        self.panel.load_conversationRequested.connect(self._publish_conversation_request)

        self.btn_open_editor.clicked.connect(self._open_selected_in_editor)
        self.btn_open_terminal.clicked.connect(self._open_selected_in_terminal)
        self.btn_archive.clicked.connect(self._archive_selected_task)

        self._update_action_state()
        self._install_bus_subscriptions()
        self.destroyed.connect(lambda *_: self._teardown())

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Force a dataset reload."""

        self.panel.refresh()
        if self._selected_task:
            updated = self.manager.get_task(self._selected_task.id)
            if updated:
                self._selected_task = updated
            self._update_action_state()

    # ------------------------------------------------------------------
    def _install_bus_subscriptions(self) -> None:
        topics = {
            "task.created": self._on_task_payload,
            "task.updated": self._on_task_payload,
            "task.status": self._on_status_payload,
            "task.deleted": self._on_status_payload,
            "task.diff": self._on_diff_payload,
        }
        for topic, callback in topics.items():
            try:
                self._subscriptions.append(subscribe(topic, callback))
            except Exception:  # pragma: no cover - defensive guard
                logger.exception("Failed to subscribe to %s", topic)

    # ------------------------------------------------------------------
    def _teardown(self) -> None:
        for handle in self._subscriptions:
            try:
                handle.unsubscribe()
            except Exception:  # pragma: no cover - defensive cleanup
                logger.exception("Error unsubscribing task handle")
        self._subscriptions.clear()

    # ------------------------------------------------------------------
    def _on_task_selected(self, task_id: str) -> None:
        self._selected_task = self.manager.get_task(task_id)
        self._update_action_state()

    # ------------------------------------------------------------------
    def _on_task_payload(self, payload: dict) -> None:
        task = self._task_from_payload(payload)
        if task is None:
            self.panel.refresh()
            return
        self.panel.update_task(task)
        if self._selected_task and self._selected_task.id == task.id:
            self._selected_task = task
        self._update_action_state()

    # ------------------------------------------------------------------
    def _on_status_payload(self, payload: dict) -> None:
        task_id = payload.get("id") if isinstance(payload, dict) else None
        if not task_id:
            return
        task = self.manager.get_task(str(task_id))
        if task:
            self.panel.update_task(task)
            if self._selected_task and self._selected_task.id == task.id:
                self._selected_task = task
                self._update_action_state()
        else:
            self.panel.refresh()

    # ------------------------------------------------------------------
    def _on_diff_payload(self, payload: dict) -> None:  # noqa: ARG002 - payload unused beyond refresh
        self.panel.refresh()
        if self._selected_task:
            latest = self.manager.get_task(self._selected_task.id)
            if latest:
                self._selected_task = latest
        self._update_action_state()

    # ------------------------------------------------------------------
    def _publish_conversation_request(self, task_id: str, conversation_id: str) -> None:
        conv = (conversation_id or "").strip()
        if not conv:
            return
        payload = {
            "id": task_id,
            "conversation_id": conv,
            "session_id": self._selected_task.session_id if self._selected_task else "",
            "source": self._source,
        }
        try:
            publish("task.conversation", payload)
        except Exception:  # pragma: no cover - defensive guard
            logger.exception("Failed to publish conversation request from TaskCard")

    # ------------------------------------------------------------------
    def _task_from_payload(self, payload: dict | None) -> Optional[Task]:
        if not isinstance(payload, dict):
            return None
        try:
            return Task.from_dict(payload)
        except Exception:
            logger.debug("Task payload missing fields: %r", payload)
            task_id = payload.get("id")
            if task_id:
                return self.manager.get_task(str(task_id))
        return None

    # ------------------------------------------------------------------
    def _update_action_state(self) -> None:
        has_task = self._selected_task is not None
        self.btn_open_editor.setEnabled(has_task and self._resolve_primary_path(self._selected_task) is not None)
        self.btn_open_terminal.setEnabled(has_task and self._open_terminal is not None)
        self.btn_archive.setEnabled(has_task)

    # ------------------------------------------------------------------
    def _resolve_primary_path(self, task: Optional[Task]) -> Optional[Path]:
        if not task:
            return None
        for candidate in list(task.files or []):
            resolved = self.manager.resolve_path(candidate)
            if resolved is not None:
                return resolved
        if task.run_log_path:
            resolved = self.manager.resolve_path(task.run_log_path)
            if resolved is not None:
                return resolved
        return None

    # ------------------------------------------------------------------
    def _resolve_directory(self, task: Optional[Task]) -> Path:
        workspace = self.manager.resolve_path(".")
        if task is None:
            return workspace or Path.cwd()
        primary = self._resolve_primary_path(task)
        if primary and primary.exists():
            return primary.parent
        if primary:
            return primary.parent
        if task.run_log_path:
            resolved = self.manager.resolve_path(task.run_log_path)
            if resolved:
                return resolved.parent
        return workspace or Path.cwd()

    # ------------------------------------------------------------------
    def _open_selected_in_editor(self) -> None:
        if not self._selected_task:
            return
        path = self._resolve_primary_path(self._selected_task)
        if path is None or not self._open_editor:
            QMessageBox.information(self, "Tasks", "Task has no associated files to open.")
            return
        if not path.exists():
            QMessageBox.information(self, "Tasks", f"File not found: {path}")
            return
        self._open_editor(str(path))

    # ------------------------------------------------------------------
    def _open_selected_in_terminal(self) -> None:
        if not self._selected_task or not self._open_terminal:
            return
        directory = self._resolve_directory(self._selected_task)
        if not directory.exists():
            QMessageBox.information(self, "Tasks", f"Folder not found: {directory}")
            return
        self._open_terminal(str(directory))

    # ------------------------------------------------------------------
    def _archive_selected_task(self) -> None:
        if not self._selected_task:
            return
        self._update_status(self._selected_task.id, "deleted")

    # ------------------------------------------------------------------
    def _apply_status_change(self, task_id: str, status: str) -> None:
        if not task_id or not status:
            return
        self._update_status(task_id, status)

    # ------------------------------------------------------------------
    def _update_status(self, task_id: str, status: str) -> None:
        now = datetime.now(UTC).timestamp()
        try:
            updated = update_task(task_id, status=status, updated_ts=now)
            append_event(
                TaskEvent(ts=now, task_id=task_id, event="status", by=self._source, to=status)
            )
        except ValueError:
            QMessageBox.warning(self, "Tasks", f"Task {task_id} no longer exists.")
            self.panel.refresh()
            return
        except Exception:
            logger.exception("Failed to update task %s", task_id)
            QMessageBox.warning(self, "Tasks", "Unable to update the selected task.")
            return

        publish("task.status", {"id": updated.id, "status": updated.status})
        publish("task.updated", updated.to_dict())
        if status == "deleted":
            publish("task.deleted", {"id": updated.id})
        self.panel.update_task(updated)
        if self._selected_task and self._selected_task.id == updated.id:
            self._selected_task = updated
        self._update_action_state()


def open_card(
    manager: TaskManager,
    theme,
    open_editor: Callable[[str], None],
    open_terminal: Optional[Callable[[str], None]] = None,
    workspace_root: str | Path | None = None,
    parent: Optional[QWidget] = None,
    source: str = "desktop",
) -> Optional[TaskCard]:
    """Factory returning a configured :class:`TaskCard` widget."""

    try:
        return TaskCard(
            manager=manager,
            theme=theme,
            open_editor=open_editor,
            open_terminal=open_terminal,
            workspace_root=workspace_root,
            source=source,
            parent=parent,
        )
    except Exception:  # pragma: no cover - guard unexpected Qt errors
        logger.exception("Failed to create TaskCard")
        QMessageBox.critical(parent, "Tasks", "Unable to open Tasks card.")
        return None
