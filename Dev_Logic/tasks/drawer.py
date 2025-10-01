"""Slide-out drawer wrapper around :class:`tasks.task_panel.TaskPanel`."""
from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QFrame, QSizePolicy, QVBoxLayout, QWidget

from .bus import Subscription, publish, subscribe
from .models import TASKS_FILE, Task, TaskEvent, append_event, append_task, update_task
from .task_panel import TaskPanel

logger = logging.getLogger(__name__)

__all__ = ["TaskDrawer"]


class TaskDrawer(QFrame):
    """Right-aligned container that hosts the shared :class:`TaskPanel` UI."""

    def __init__(
        self,
        session_id: str,
        dataset_path: Optional[Path] = None,
        source: str = "terminal",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("TaskDrawer")
        self.setFocusPolicy(Qt.NoFocus)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setStyleSheet(
            "QFrame#TaskDrawer{background:#0a111e;border-left:1px solid #1d2b3c;}"
        )

        self._session_id = session_id or "terminal"
        self._source = source or "terminal"
        self._dataset_path = Path(dataset_path) if dataset_path else TASKS_FILE

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.panel = TaskPanel(self._dataset_path, self)
        self.panel.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.panel.setTitleBarWidget(QWidget(self.panel))
        layout.addWidget(self.panel)

        width_hint = max(360, self.panel.sizeHint().width())
        self.setFixedWidth(width_hint)

        self.panel.new_taskRequested.connect(self._create_task)
        self.panel.status_changed.connect(self._apply_status_change)
        self.panel.load_conversationRequested.connect(self._publish_conversation_request)

        self._subscriptions: List[Subscription] = [
            subscribe("task.created", self._on_task_payload),
            subscribe("task.updated", self._on_task_payload),
        ]
        self.destroyed.connect(lambda *_: self._teardown())

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Refresh the embedded panel from disk."""

        self.panel.refresh()

    # ------------------------------------------------------------------
    def _teardown(self) -> None:
        for handle in self._subscriptions:
            try:
                handle.unsubscribe()
            except Exception:  # pragma: no cover - defensive cleanup
                logger.exception("Failed to unsubscribe task drawer handle")
        self._subscriptions.clear()

    # ------------------------------------------------------------------
    def _create_task(self, title: str) -> None:
        title = (title or "").strip()
        if not title:
            return
        now = datetime.now(UTC).timestamp()
        task_id = self._generate_task_id()
        task = Task(
            id=task_id,
            title=title,
            status="open",
            created_ts=now,
            updated_ts=now,
            session_id=self._session_id,
            source=self._source,
            codex_conversation_id=self._session_id,
        )
        try:
            append_task(task)
            append_event(TaskEvent(ts=now, task_id=task_id, event="created", by=self._source))
        except Exception:
            logger.exception("Failed to persist new task: %s", task_id)
            return

        publish("task.created", task.to_dict())
        publish("task.updated", task.to_dict())
        self.panel.update_task(task)

    # ------------------------------------------------------------------
    def _publish_conversation_request(self, task_id: str, conversation_id: str) -> None:
        conv = (conversation_id or "").strip()
        if not conv:
            return
        payload = {
            "id": task_id,
            "conversation_id": conv,
            "session_id": self._session_id,
            "source": self._source,
        }
        try:
            publish("task.conversation", payload)
        except Exception:  # pragma: no cover - defensive guard
            logger.exception("Failed to publish task conversation request")

    # ------------------------------------------------------------------
    def _apply_status_change(self, task_id: str, status: str) -> None:
        if not task_id or not status:
            return
        now = datetime.now(UTC).timestamp()
        try:
            updated = update_task(task_id, status=status, updated_ts=now)
            append_event(
                TaskEvent(
                    ts=now,
                    task_id=task_id,
                    event="status",
                    by=self._source,
                    to=status,
                )
            )
        except ValueError:
            logger.warning("Task %s not found when applying status", task_id)
            self.panel.refresh()
            return
        except Exception:
            logger.exception("Failed to update task status for %s", task_id)
            return

        publish("task.status", {"id": updated.id, "status": updated.status})
        publish("task.updated", updated.to_dict())
        self.panel.update_task(updated)

    # ------------------------------------------------------------------
    def _on_task_payload(self, payload: dict) -> None:
        if not isinstance(payload, dict):
            return
        try:
            task = Task.from_dict(payload)
        except Exception:
            logger.debug("Skipping malformed task payload: %r", payload)
            self.panel.refresh()
            return
        self.panel.update_task(task)

    # ------------------------------------------------------------------
    def _generate_task_id(self) -> str:
        stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"tsk_{stamp}_{uuid.uuid4().hex[:6]}"
