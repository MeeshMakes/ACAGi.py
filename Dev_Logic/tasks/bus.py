"""Lightweight in-process pub/sub bus for task updates.

This module exposes ``publish`` and ``subscribe`` helpers so different
components (Codex Terminal, Virtual Desktop, etc.) can react to task
changes without tight coupling. The implementation keeps the API very
small yet provides:

* A fixed list of allowed topics (mirroring the task spec).
* Optional ``task.*`` wildcard subscribers for convenience.
* Thread-safe subscribe/publish operations guarded by ``RLock``.
* An unsubscribe handle so listeners can be cleaned up deterministically.
* Defensive logging so one faulty subscriber will not break others.
"""
from __future__ import annotations

from collections import defaultdict
import logging
from threading import RLock
from typing import Callable, List, MutableMapping

__all__ = [
    "TASK_TOPICS",
    "Subscription",
    "publish",
    "subscribe",
]

logger = logging.getLogger(__name__)

Subscriber = Callable[[dict], None]

TASK_TOPICS = {
    "task.created",
    "task.updated",
    "task.status",
    "task.diff",
    "task.deleted",
    "task.conversation",
    "system.metrics",
}
_WILDCARD_TOPIC = "task.*"


class Subscription:
    """Handle returned from :func:`subscribe` that can detach a listener."""

    __slots__ = ("_topic", "_callback", "_active")

    def __init__(self, topic: str, callback: Subscriber) -> None:
        self._topic = topic
        self._callback = callback
        self._active = True

    @property
    def active(self) -> bool:
        """Whether the subscription is currently registered."""

        return self._active

    def unsubscribe(self) -> None:
        """Remove the callback from the bus. Safe to call multiple times."""

        if not self._active:
            return
        with _LOCK:
            listeners = _SUBSCRIBERS.get(self._topic)
            if listeners is None:
                self._active = False
                return
            try:
                listeners.remove(self._callback)
            except ValueError:
                pass
            else:
                if not listeners:
                    _SUBSCRIBERS.pop(self._topic, None)
            self._active = False

    # Support ``handle()`` as syntactic sugar for ``handle.unsubscribe()``.
    def __call__(self) -> None:  # pragma: no cover - sugar
        self.unsubscribe()


_SUBSCRIBERS: MutableMapping[str, List[Subscriber]] = defaultdict(list)
_LOCK = RLock()


def _validate_topic(topic: str, allow_wildcard: bool = False) -> None:
    if topic in TASK_TOPICS:
        return
    if allow_wildcard and topic == _WILDCARD_TOPIC:
        return
    raise ValueError(f"Unsupported topic: {topic!r}")


def subscribe(topic: str, callback: Subscriber) -> Subscription:
    """Register ``callback`` for ``topic`` and return an unsubscribe handle."""

    if not callable(callback):
        raise TypeError("callback must be callable")
    _validate_topic(topic, allow_wildcard=True)

    with _LOCK:
        _SUBSCRIBERS[topic].append(callback)
    return Subscription(topic, callback)


def publish(topic: str, payload: dict) -> None:
    """Broadcast ``payload`` to subscribers registered for ``topic``."""

    if not isinstance(payload, dict):
        raise TypeError("payload must be a dictionary")
    _validate_topic(topic)

    with _LOCK:
        listeners = list(_SUBSCRIBERS.get(topic, ()))
        wildcard_listeners = list(_SUBSCRIBERS.get(_WILDCARD_TOPIC, ()))

    for callback in (*listeners, *wildcard_listeners):
        try:
            callback(payload)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Error dispatching %s to %r", topic, callback)
