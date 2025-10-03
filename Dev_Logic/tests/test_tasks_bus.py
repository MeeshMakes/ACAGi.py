import importlib

import pytest

from tasks import bus


@pytest.fixture(autouse=True)
def reset_bus():
    importlib.reload(bus)
    yield
    importlib.reload(bus)


def test_publish_notifies_subscribers(reset_bus):
    received: list[dict] = []
    handle = bus.subscribe("task.created", received.append)

    bus.publish("task.created", {"id": "tsk_1"})

    assert received == [{"id": "tsk_1"}]
    handle.unsubscribe()


def test_publish_notifies_multiple_subscribers(reset_bus):
    results: list[str] = []

    def recorder(label: str):
        def _record(payload: dict) -> None:
            results.append(f"{label}:{payload['id']}")

        return _record

    handle_a = bus.subscribe("task.updated", recorder("a"))
    handle_b = bus.subscribe("task.updated", recorder("b"))

    bus.publish("task.updated", {"id": "tsk_1", "status": "open"})

    assert sorted(results) == ["a:tsk_1", "b:tsk_1"]
    handle_a.unsubscribe()
    handle_b.unsubscribe()


def test_unsubscribe_stops_notifications(reset_bus):
    calls: list[dict] = []
    handle = bus.subscribe("task.status", calls.append)

    handle.unsubscribe()
    bus.publish("task.status", {"id": "tsk_2", "status": "merged"})

    assert calls == []


def test_invalid_topics_raise(reset_bus):
    with pytest.raises(ValueError):
        bus.subscribe("task.invalid", lambda payload: None)

    with pytest.raises(ValueError):
        bus.publish("task.invalid", {})


def test_system_metrics_topic(reset_bus):
    received: list[dict] = []
    handle = bus.subscribe("system.metrics", received.append)

    bus.publish("system.metrics", {"generated_at": 123.0})

    assert received == [{"generated_at": 123.0}]
    handle.unsubscribe()


def test_wildcard_receives_all(reset_bus):
    topics: list[str] = []

    def _capture(payload: dict) -> None:
        topics.append(payload["topic"])

    handle = bus.subscribe("task.*", _capture)

    bus.publish("task.created", {"topic": "task.created"})
    bus.publish("task.deleted", {"topic": "task.deleted"})

    assert topics == ["task.created", "task.deleted"]
    handle.unsubscribe()


def test_subscribe_requires_callable(reset_bus):
    with pytest.raises(TypeError):
        bus.subscribe("task.created", None)


def test_publish_requires_dict(reset_bus):
    with pytest.raises(TypeError):
        bus.publish("task.created", object())
