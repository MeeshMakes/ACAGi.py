import types

import pytest
from PySide6.QtWidgets import QApplication

import Codex_Terminal as sct


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_parse_single_prompt_block():
    delta = (
        "Allow command?\n\n"
        "> rm -rf temp\n"
        "[y] Yes\n"
        "[n] No\n"
        "[a] Always allow\n"
    )
    events = sct.ChatCard._parse_codex_approval_events(delta)
    assert len(events) == 1
    prompt_event = events[0]
    assert prompt_event.kind == "prompt"
    prompt = prompt_event.payload
    assert isinstance(prompt, sct.ApprovalPrompt)
    assert prompt.header == "Allow command?"
    assert "> rm -rf temp" in prompt.body
    assert prompt.options["yes"] == "y"
    assert prompt.options["no"] == "n"
    assert prompt.options["always"] == "a"


def test_parse_multiple_prompts_in_delta():
    delta = (
        "System ready.\n\n"
        "Allow command?\n> echo hi\n[y] Yes\n[n] No\n\n"
        "Approve and run this plan?\n- Step 1\n- Step 2\n(y) Yes\n(n) No\n"
    )
    events = sct.ChatCard._parse_codex_approval_events(delta)
    kinds = [evt.kind for evt in events]
    assert kinds == ["text", "prompt", "prompt"]
    assert events[0].payload.strip() == "System ready."


def test_parse_prompt_with_box_glyph_layout():
    delta = (
        "╭─ Allow Codex to run git status?\n"
        "│ Codex wants to run:\n"
        "│   git status\n"
        "│\n"
        "▌ Yes   Always allow   No   Provide feedback\n"
        "│  y     always        n    feedback\n"
        "╰─ Choose an option:\n"
    )
    events = sct.ChatCard._parse_codex_approval_events(delta)
    prompt_events = [evt for evt in events if evt.kind == "prompt"]
    assert prompt_events, "Expected at least one prompt event"
    prompt = prompt_events[0].payload
    assert isinstance(prompt, sct.ApprovalPrompt)
    assert prompt.header == "Allow Codex to run git status?"
    assert "Codex wants to run:" in prompt.body
    assert "git status" in prompt.body
    assert "Yes" not in prompt.body
    assert prompt.options["yes"] == "y"
    assert prompt.options["always"] == "always"
    assert prompt.options["no"] == "n"
    assert prompt.options["feedback"] == "feedback"


def test_parse_select_colon_prompt():
    delta = (
        "Select: Harden the Codex task event flow.\n"
        "> Should Codex mark action payloads with event metadata?\n"
        "[y] Yes — include codex_action_type.\n"
        "[n] No — leave current behavior.\n"
    )
    events = sct.ChatCard._parse_codex_approval_events(delta)
    prompt_events = [evt for evt in events if evt.kind == "prompt"]
    assert prompt_events, "Expected select header to produce a prompt"
    prompt = prompt_events[0].payload
    assert isinstance(prompt, sct.ApprovalPrompt)
    assert prompt.header.startswith("Select: Harden the Codex task event flow")
    assert prompt.options["yes"] == "y"
    assert prompt.options["no"] == "n"


def test_parse_falls_back_to_plain_text():
    delta = "No approval needed."
    events = sct.ChatCard._parse_codex_approval_events(delta)
    assert len(events) == 1
    evt = events[0]
    assert evt.kind == "text"
    assert evt.payload == "No approval needed."


def test_widget_sends_tokens_and_updates_status(qapp):
    prompt = sct.ApprovalPrompt(
        header="Allow command?",
        body="> dir",
        options={
            "yes": "y",
            "always": "always",
            "no": "n",
            "feedback": "feedback",
        },
    )
    captured = []

    def _capture(widget, action, token):
        captured.append((widget, action, token))

    widget = sct.ApprovalPromptWidget(sct.Theme(), prompt, _capture)
    widget._handle_click("yes")
    assert captured[0][1:] == ("yes", "y")
    widget.mark_submitted("yes")
    assert "Sent: Yes" in widget._status.text()
    assert not widget.is_active()


def test_dismissal_disables_buttons(qapp):
    prompt = sct.ApprovalPrompt(
        header="Approve edit?",
        body="Update file?",
        options=sct.DEFAULT_APPROVAL_TOKENS.copy(),
    )
    widget = sct.ApprovalPromptWidget(sct.Theme(), prompt, lambda *a: None)
    widget.mark_dismissed("Prompt dismissed.")
    assert widget._status.text() == "Prompt dismissed."
    assert not widget.is_active()


def test_handle_approval_decision_sends_token(qapp):
    events = []

    class DummyBridge:
        def __init__(self):
            self.pid = 1

        def running(self):
            return True

        def send_text(self, token):
            events.append(("send_text", token))
            return True

        def press_enter_async(self, hwnd):
            events.append(("enter", hwnd))

    view = types.SimpleNamespace(
        append_message=lambda *a, **k: events.append(("view", a, k))
    )
    led_signal = types.SimpleNamespace(
        emit=lambda state: events.append(("led", state))
    )
    dummy = types.SimpleNamespace(
        bridge=DummyBridge(),
        view=view,
        codex_led_signal=led_signal,
        _codex_status=lambda msg: events.append(("status", msg)),
        _ui_hwnd=lambda: 0,
    )

    prompt = sct.ApprovalPrompt(
        header="Allow command?",
        body="",
        options=sct.DEFAULT_APPROVAL_TOKENS.copy(),
    )
    widget = sct.ApprovalPromptWidget(sct.Theme(), prompt, lambda *a: None)

    sct.ChatCard._handle_approval_decision(dummy, widget, "yes", "y")

    assert ("send_text", "y") in events
    assert any(ev for ev in events if ev == ("led", "yellow"))
    assert any("Approval → Yes" in ev[1] for ev in events if ev[0] == "status")
    assert not widget.is_active()
