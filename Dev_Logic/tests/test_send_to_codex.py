import copy
import json
import types

import Codex_Terminal as sct


def test_task_command_creation_uses_conversation_id(monkeypatch):
    captured = {}

    def _capture_task(task):
        captured["task"] = task

    monkeypatch.setattr(sct, "append_task", _capture_task)
    monkeypatch.setattr(sct, "append_event", lambda event: None)
    monkeypatch.setattr(sct, "publish", lambda topic, payload: None)

    dummy = types.SimpleNamespace(
        session_id="term_test_123",
        _emit_system_notice=lambda message: None,
    )

    bound = types.MethodType(sct.ChatCard._command_task_create, dummy)
    bound("Resume task flow")

    assert "task" in captured
    assert captured["task"].codex_conversation_id == "term_test_123"


def test_send_to_codex_records_before_enter(monkeypatch):
    events = []

    class DummyBridge:
        def __init__(self):
            self.pid = 1

        def running(self):
            return True

        def busy(self):
            return False

        def send_text(self, txt):
            events.append(("send_text", txt))
            return True

        def press_enter_async(self, hwnd):
            events.append("enter")

    dummy = types.SimpleNamespace(
        bridge=DummyBridge(),
        input=types.SimpleNamespace(
            toPlainText=lambda: "echo hi",
            clear=lambda: events.append("clear"),
        ),
        view=types.SimpleNamespace(
            append_message=lambda role, text, **kwargs: events.append(
                ("append_message", role, text)
            )
        ),
        _ui_hwnd=lambda: 0,
        conv=types.SimpleNamespace(
            append=lambda role, text, images: events.append(
                ("conv", role, text)
            ),
            recent=lambda k: [],
            retrieve=lambda q, k: [],
        ),
        lex=types.SimpleNamespace(auto_tags=lambda text: []),
        dataset=types.SimpleNamespace(
            add_entry=lambda *a, **k: events.append(("dataset", a[0], a[1]))
        ),
        share_context=False,
        share_limit=1,
        settings={"enable_semantic": False},
        codex_interpreter=types.SimpleNamespace(
            observe_user=lambda text: None,
            observe_codex_output=lambda text: None,
        ),
    )
    dummy._store_session_note = lambda *a, **k: None
    dummy._record_message = types.MethodType(
        sct.ChatCard._record_message, dummy
    )

    sct.ChatCard._send_to_codex(dummy)

    assert events == [
        ("send_text", "echo hi"),
        ("conv", "user", "echo hi"),
        ("dataset", "user", "echo hi"),
        ("append_message", "system", "→ Codex: echo hi ✓"),
        "clear",
        "enter",
    ]


def test_codex_output_logged_before_render():
    events = []

    conv = types.SimpleNamespace(
        append=lambda role, text, images: events.append(("conv", role, text))
    )
    dataset = types.SimpleNamespace(
        add_entry=lambda *a, **k: events.append(("dataset", a[0], a[1]))
    )
    append_signal = types.SimpleNamespace(
        emit=lambda msg: events.append(("append", msg))
    )
    view = types.SimpleNamespace(append_message=lambda *a, **k: None)

    def _dismiss(reason):
        events.append(("dismiss", reason))

    dummy = types.SimpleNamespace(
        conv=conv,
        lex=types.SimpleNamespace(auto_tags=lambda text: []),
        dataset=dataset,
        append_signal=append_signal,
        _dismiss_active_approvals=_dismiss,
        view=view,
        codex_interpreter=types.SimpleNamespace(
            observe_codex_output=lambda text: None,
        ),
    )
    dummy._parse_codex_approval_events = (
        sct.ChatCard._parse_codex_approval_events
    )
    dummy._record_message = types.MethodType(
        sct.ChatCard._record_message, dummy
    )

    sct.ChatCard._on_codex_output(dummy, "hi out")

    assert events[0] == ("conv", "assistant", "hi out")
    assert events[1] == ("dataset", "assistant", "hi out")
    kind, message = events[2]
    assert kind == "append"
    assert isinstance(message, sct.ChatMessage)
    assert message.role == "assistant"
    assert message.text == "hi out"
    assert message.kind == "text"


def test_codex_output_ignores_bare_approval_tokens():
    events = []

    conv = types.SimpleNamespace(
        append=lambda role, text, images: events.append(("conv", role, text))
    )
    dataset = types.SimpleNamespace(
        add_entry=lambda *a, **k: events.append(("dataset", a[0], a[1]))
    )
    append_signal = types.SimpleNamespace(
        emit=lambda msg: events.append(("append", msg))
    )
    view = types.SimpleNamespace(append_message=lambda *a, **k: None)

    dummy = types.SimpleNamespace(
        conv=conv,
        lex=types.SimpleNamespace(auto_tags=lambda text: []),
        dataset=dataset,
        append_signal=append_signal,
        _dismiss_active_approvals=lambda reason: events.append(("dismiss", reason)),
        view=view,
        codex_interpreter=types.SimpleNamespace(
            observe_codex_output=lambda text: events.append(("observe", text)),
        ),
    )
    dummy._parse_codex_approval_events = (
        sct.ChatCard._parse_codex_approval_events
    )
    dummy._record_message = types.MethodType(
        sct.ChatCard._record_message, dummy
    )

    tokens = ["always", "YES", "n", "feedback"]
    for token in tokens:
        sct.ChatCard._on_codex_output(dummy, token)

    assert events == []


def test_codex_bridge_drops_injected_token_delta(monkeypatch):
    outputs = []

    bridge = sct.CodexBridge(lambda s: None, lambda c: None, outputs.append)
    bridge.attach(42)

    monkeypatch.setattr(sct, "write_console_input_text", lambda pid, text: True)
    monkeypatch.setattr(sct, "codex_ready_banner", lambda snap: False)
    monkeypatch.setattr(sct.time, "sleep", lambda *a, **k: None)

    snapshots = ["", "Always", ""]

    def _snapshot(pid):
        assert pid == 42
        value = snapshots.pop(0)
        if not snapshots:
            bridge._stop_evt.set()
        return value

    monkeypatch.setattr(sct, "read_console_snapshot", _snapshot)

    assert bridge.send_text("Always")
    bridge._busy_evt.clear()
    bridge._stop_evt.clear()

    bridge._idle_loop()

    assert outputs == []
    assert bridge._last_injected is None


def test_send_to_codex_prepends_context(monkeypatch):
    events = []

    class DummyBridge:
        def __init__(self):
            self.pid = 1

        def running(self):
            return True

        def busy(self):
            return False

        def send_text(self, txt):
            events.append(("send_text", txt))
            return True

        def press_enter_async(self, hwnd):
            events.append("enter")

    conv = types.SimpleNamespace(
        append=lambda *a, **k: None,
        recent=lambda k: [{"role": "user", "text": "ctx"}],
        retrieve=lambda q, k: [],
    )
    dummy = types.SimpleNamespace(
        bridge=DummyBridge(),
        input=types.SimpleNamespace(
            toPlainText=lambda: "echo hi",
            clear=lambda: events.append("clear"),
        ),
        view=types.SimpleNamespace(append_message=lambda *a, **k: None),
        _ui_hwnd=lambda: 0,
        conv=conv,
        lex=types.SimpleNamespace(auto_tags=lambda text: []),
        dataset=types.SimpleNamespace(add_entry=lambda *a, **k: None),
        share_context=True,
        share_limit=1,
        settings={"enable_semantic": False},
        codex_interpreter=types.SimpleNamespace(
            observe_user=lambda text: None,
            observe_codex_output=lambda text: None,
        ),
    )
    dummy._store_session_note = lambda *a, **k: None
    dummy._record_message = types.MethodType(
        sct.ChatCard._record_message, dummy
    )

    sct.ChatCard._send_to_codex(dummy)

    assert events[0] == ("send_text", "user: ctx\necho hi")


def test_send_to_codex_respects_share_toggle(monkeypatch):
    events = []

    class DummyBridge:
        def __init__(self):
            self.pid = 1

        def running(self):
            return True

        def busy(self):
            return False

        def send_text(self, txt):
            events.append(("send_text", txt))
            return True

        def press_enter_async(self, hwnd):
            events.append("enter")

    dummy = types.SimpleNamespace(
        bridge=DummyBridge(),
        input=types.SimpleNamespace(
            toPlainText=lambda: "echo hi",
            clear=lambda: None,
        ),
        view=types.SimpleNamespace(append_message=lambda *a, **k: None),
        _ui_hwnd=lambda: 0,
        conv=types.SimpleNamespace(
            append=lambda *a, **k: None,
            recent=lambda k: [],
            retrieve=lambda q, k: [],
        ),
        lex=types.SimpleNamespace(auto_tags=lambda text: []),
        dataset=types.SimpleNamespace(add_entry=lambda *a, **k: None),
        share_context=False,
        share_limit=1,
        settings={"enable_semantic": False},
        codex_interpreter=types.SimpleNamespace(
            observe_user=lambda text: None,
            observe_codex_output=lambda text: None,
        ),
    )
    dummy._store_session_note = lambda *a, **k: None
    dummy._record_message = types.MethodType(
        sct.ChatCard._record_message, dummy
    )

    sct.ChatCard._send_to_codex(dummy)

    assert events[0] == ("send_text", "echo hi")


def test_send_to_codex_skips_large_reference(monkeypatch, tmp_path):
    events = []

    class DummyBridge:
        def __init__(self):
            self.pid = 1

        def running(self):
            return True

        def busy(self):
            return False

        def send_text(self, txt):
            events.append(("send_text", txt))
            return True

        def press_enter_async(self, hwnd):
            events.append(("enter", hwnd))

    monkeypatch.setattr(sct.token_budget, "count_tokens", lambda text, model=None: len(text))
    monkeypatch.setattr(sct.token_budget, "prompt_token_budget", lambda model, headroom: 50)

    ref_path = tmp_path / "big.txt"
    ref_path.write_text("x" * 200, encoding="utf-8")

    class DummyInput:
        def __init__(self, references):
            self._text = "echo hi"
            self._accepted_references = [dict(r) for r in references]

        def toPlainText(self):
            return self._text

        def clear(self):
            events.append("clear")

        def consume_references(self):
            refs = self._accepted_references
            self._accepted_references = []
            return refs

    references = [{"path": ref_path.name, "type": "file"}]

    dummy = types.SimpleNamespace(
        bridge=DummyBridge(),
        input=DummyInput(references),
        view=types.SimpleNamespace(
            append_message=lambda role, text, **kwargs: events.append(("append_message", role, text))
        ),
        _ui_hwnd=lambda: 0,
        conv=types.SimpleNamespace(recent=lambda k: [], retrieve=lambda q, k: []),
        share_context=False,
        share_limit=1,
        settings={
            "enable_semantic": False,
            "reference_embed_contents": True,
            "reference_token_guard": True,
            "reference_token_headroom": 50,
            "chat_model": "tiny",
        },
        workspace=tmp_path,
        codex_interpreter=types.SimpleNamespace(
            observe_user=lambda text: None,
            observe_codex_output=lambda text: None,
        ),
    )
    dummy._emit_system_notice = lambda message: events.append(("notice", message))
    dummy._record_message = types.MethodType(sct.ChatCard._record_message, dummy)

    sct.ChatCard._send_to_codex(dummy)

    assert events[0] == ("send_text", "echo hi")
    notices = [msg for kind, msg in events if kind == "notice"]
    assert any("Skipped 1 reference" in msg for msg in notices)


def _dummy_bridge(events):
    class DummyBridge:
        def __init__(self):
            self.auto_events = []

        def running(self):
            return True

        def busy(self):
            return False

        def send_text(self, txt):
            events.append(("send", txt))
            return True

        def press_enter_async(self, hwnd):
            events.append(("enter", hwnd))

    return DummyBridge()


def _make_interpreter(bridge, enabled=True):
    return sct.CodexInterpreter(
        bridge=bridge,
        get_busy=lambda: False,
        get_hwnd=lambda: 99,
        on_auto=lambda cmd: bridge.auto_events.append(cmd),
        enabled=enabled,
    )


def test_interpreter_auto_continue_on_prompt():
    events = []
    bridge = _dummy_bridge(events)
    interpreter = _make_interpreter(bridge, enabled=True)
    interpreter.observe_user("update settings dialog labels")
    continue_prompt = "Working... Would you like me to continue?"
    interpreter.observe_codex_output(continue_prompt)

    expected = "continue, focusing on update settings dialog labels"
    assert ("send", expected) in events
    assert ("enter", 99) in events
    assert expected in bridge.auto_events


def test_interpreter_reacts_to_repeated_plan_once():
    events = []
    bridge = _dummy_bridge(events)
    interpreter = _make_interpreter(bridge, enabled=True)
    interpreter.observe_user("refactor the codex interpreter helper")

    plan_text = "Plan:\n1. Prep\n2. Apply"
    interpreter.observe_codex_output(plan_text)
    assert events == []

    interpreter.observe_codex_output(plan_text)
    expected = "continue, focusing on refactor the codex interpreter helper"
    assert events[0] == ("send", expected)
    assert events[1] == ("enter", 99)


def test_interpreter_halts_after_completion_until_new_user_instruction():
    events = []
    bridge = _dummy_bridge(events)
    interpreter = _make_interpreter(bridge, enabled=False)
    interpreter.observe_user("add new workflow")
    interpreter.observe_codex_output("Would you like me to continue?")
    assert events == []

    interpreter.enabled = True
    interpreter.observe_codex_output("Would you like me to continue?")
    first_expected = "continue, focusing on add new workflow"
    assert events[0] == ("send", first_expected)
    events.clear()

    interpreter.observe_codex_output("Completed file change main.py")
    interpreter.observe_codex_output("Would you like me to continue?")
    assert events == []

    interpreter.observe_user("write regression tests")
    interpreter.observe_codex_output("Would you like me to continue?")
    second_expected = "continue, focusing on write regression tests"
    assert events[0] == ("send", second_expected)


def test_refresh_interpreter_toggle_disabled_when_bridge_offline():
    events = []

    class DummyToggle:
        def __init__(self):
            self.enabled_state = None
            self.tooltip_text = ""
            self.checked = False

        def setEnabled(self, value):
            self.enabled_state = bool(value)

        def setToolTip(self, text):
            self.tooltip_text = text

        def isChecked(self):
            return self.checked

    class OfflineBridge:
        def running(self):
            return False

    toggle = DummyToggle()

    def capture_caption(enabled):
        events.append(("caption", enabled))

    dummy = types.SimpleNamespace(
        bridge=OfflineBridge(),
        interpreter_toggle=toggle,
        _interpreter_tooltip="Auto follow-ups.",
        _led_state="red",
        _update_interpreter_caption=capture_caption,
    )

    sct.ChatCard._refresh_interpreter_toggle_enabled(dummy)

    assert toggle.enabled_state is False
    assert "Bridge offline" in toggle.tooltip_text
    assert events == [("caption", False)]


def test_refresh_interpreter_toggle_enabled_when_bridge_live():
    events = []

    class DummyToggle:
        def __init__(self):
            self.enabled_state = None
            self.tooltip_text = ""
            self.checked = True

        def setEnabled(self, value):
            self.enabled_state = bool(value)

        def setToolTip(self, text):
            self.tooltip_text = text

        def isChecked(self):
            return self.checked

    class LiveBridge:
        def running(self):
            return True

    toggle = DummyToggle()

    def capture_caption(enabled):
        events.append(("caption", enabled))

    dummy = types.SimpleNamespace(
        bridge=LiveBridge(),
        interpreter_toggle=toggle,
        _interpreter_tooltip="Auto follow-ups.",
        _led_state="green",
        _update_interpreter_caption=capture_caption,
    )

    sct.ChatCard._refresh_interpreter_toggle_enabled(dummy)

    assert toggle.enabled_state is True
    assert toggle.tooltip_text == "Auto follow-ups."
    assert events == [("caption", True)]


def test_load_codex_settings_defaults_to_workspace(monkeypatch, tmp_path):
    settings_file = tmp_path / "settings.json"
    workspace = tmp_path / "workspace"
    target = workspace / "Terminal Desktop"

    monkeypatch.setenv("CODEX_WORKSPACE", str(workspace))
    monkeypatch.setattr(sct, "SETTINGS_JSON", settings_file)
    monkeypatch.setattr(sct, "_legacy_transit_candidates", lambda: [])
    monkeypatch.setitem(sct.DEFAULT_SETTINGS, "working_folder", "legacy")

    result = sct.load_codex_settings()

    assert result["working_folder"] == str(target)
    saved = json.loads(settings_file.read_text(encoding="utf-8"))
    assert saved["working_folder"] == str(target)


def test_load_codex_settings_migrates_transit_default(monkeypatch, tmp_path):
    settings_file = tmp_path / "settings.json"
    workspace = tmp_path / "workspace"
    legacy = tmp_path / "Codex-Transit"
    legacy.mkdir()
    (legacy / "keep.txt").write_text("legacy", encoding="utf-8")

    monkeypatch.setenv("CODEX_WORKSPACE", str(workspace))
    monkeypatch.setattr(sct, "SETTINGS_JSON", settings_file)
    monkeypatch.setattr(sct, "_legacy_transit_candidates", lambda: [legacy])
    monkeypatch.setitem(sct.DEFAULT_SETTINGS, "working_folder", "legacy")

    settings_file.write_text(json.dumps({"working_folder": str(legacy)}), encoding="utf-8")

    result = sct.load_codex_settings()

    target = workspace / "Terminal Desktop"
    assert result["working_folder"] == str(target)
    saved = json.loads(settings_file.read_text(encoding="utf-8"))
    assert saved["working_folder"] == str(target)
    assert (target / "keep.txt").read_text(encoding="utf-8") == "legacy"
    assert not legacy.exists() or not any(legacy.iterdir())


def test_reference_settings_round_trip(monkeypatch, tmp_path):
    settings_file = tmp_path / "settings.json"
    workspace = tmp_path / "workspace"
    target = workspace / "Terminal Desktop"

    monkeypatch.setenv("CODEX_WORKSPACE", str(workspace))
    monkeypatch.setattr(sct, "SETTINGS_JSON", settings_file)
    monkeypatch.setattr(sct, "_legacy_transit_candidates", lambda: [])
    monkeypatch.setitem(sct.DEFAULT_SETTINGS, "working_folder", str(target))

    initial = copy.deepcopy(sct.DEFAULT_SETTINGS)
    initial["reference_embed_contents"] = not bool(
        sct.DEFAULT_SETTINGS["reference_embed_contents"]
    )
    initial["reference_case_sensitive"] = not bool(
        sct.DEFAULT_SETTINGS["reference_case_sensitive"]
    )
    initial["reference_token_guard"] = not bool(
        sct.DEFAULT_SETTINGS["reference_token_guard"]
    )
    initial["reference_token_headroom"] = (
        int(sct.DEFAULT_SETTINGS.get("reference_token_headroom", 80)) - 5
    )

    sct.save_codex_settings(initial)

    loaded = sct.load_codex_settings()

    assert loaded["reference_embed_contents"] == initial["reference_embed_contents"]
    assert loaded["reference_case_sensitive"] == initial["reference_case_sensitive"]
    assert loaded["reference_token_guard"] == initial["reference_token_guard"]
    assert loaded["reference_token_headroom"] == initial["reference_token_headroom"]

    saved = json.loads(settings_file.read_text(encoding="utf-8"))
    assert saved["reference_embed_contents"] == initial["reference_embed_contents"]
    assert saved["reference_case_sensitive"] == initial["reference_case_sensitive"]
    assert saved["reference_token_guard"] == initial["reference_token_guard"]
    assert saved["reference_token_headroom"] == initial["reference_token_headroom"]


def test_launch_codex_cmd_uses_requested_cwd(monkeypatch, tmp_path):
    captured = {}

    def fake_popen(cmd, cwd=None, creationflags=None):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        captured["creationflags"] = creationflags
        return types.SimpleNamespace(pid=999)

    monkeypatch.setattr(sct.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(sct.subprocess, "CREATE_NEW_CONSOLE", 0x10, raising=False)

    bootstrap = sct.CodexBootstrap(types.SimpleNamespace())
    exe = tmp_path / "codex.exe"

    proc = bootstrap.launch_codex_cmd(exe, "codex-model", tmp_path)

    assert proc.pid == 999
    assert captured["cwd"] == str(tmp_path)
    assert captured["cmd"][:3] == ["cmd", "/k", "title"]
    assert captured["cmd"][3].startswith("CODEX_CMD_")
    assert captured["cmd"][4:] == ["&&", str(exe), "--model", "codex-model"]
    assert captured["creationflags"] == sct.subprocess.CREATE_NEW_CONSOLE


def test_start_codex_bridge_uses_saved_working_folder(monkeypatch, tmp_path):
    launches = {}

    def fake_launch(exe, model, cwd):
        launches["exe"] = exe
        launches["model"] = model
        launches["cwd"] = cwd
        return types.SimpleNamespace(pid=321)

    codex = types.SimpleNamespace(
        ensure_ollama=lambda: None,
        ensure_release=lambda: tmp_path / "codex.exe",
        write_config_toml=lambda model: launches.setdefault("config_model", model),
        launch_codex_cmd=fake_launch,
    )

    messages = []
    dummy = types.SimpleNamespace(
        codex=codex,
        settings={"chat_model": "fallback-model"},
        view=types.SimpleNamespace(append_message=lambda role, text: messages.append((role, text))),
        bridge=types.SimpleNamespace(
            attach=lambda pid: None,
            start=lambda: None,
        ),
        codex_led_signal=types.SimpleNamespace(emit=lambda state: None),
        btn_codex_start=types.SimpleNamespace(setEnabled=lambda value: None),
        btn_codex_stop=types.SimpleNamespace(setEnabled=lambda value: None),
        _refresh_interpreter_toggle_enabled=lambda: None,
    )

    bound = types.MethodType(sct.ChatCard._start_codex_bridge, dummy)
    monkeypatch.setattr(
        sct,
        "load_codex_settings",
        lambda: {"model": "setting-model", "working_folder": str(tmp_path)},
    )

    bound()

    assert launches["model"] == "setting-model"
    assert launches["cwd"] == tmp_path
    assert all("Working folder" not in text for _, text in messages)


def test_start_codex_bridge_falls_back_to_transit_dir(monkeypatch, tmp_path):
    launches = {}

    def fake_launch(exe, model, cwd):
        launches["cwd"] = cwd
        return types.SimpleNamespace(pid=654)

    codex = types.SimpleNamespace(
        ensure_ollama=lambda: None,
        ensure_release=lambda: tmp_path / "codex.exe",
        write_config_toml=lambda model: None,
        launch_codex_cmd=fake_launch,
    )

    messages = []
    dummy = types.SimpleNamespace(
        codex=codex,
        settings={"chat_model": "fallback-model"},
        view=types.SimpleNamespace(append_message=lambda role, text: messages.append((role, text))),
        bridge=types.SimpleNamespace(attach=lambda pid: None, start=lambda: None),
        codex_led_signal=types.SimpleNamespace(emit=lambda state: None),
        btn_codex_start=types.SimpleNamespace(setEnabled=lambda value: None),
        btn_codex_stop=types.SimpleNamespace(setEnabled=lambda value: None),
        _refresh_interpreter_toggle_enabled=lambda: None,
    )

    bound = types.MethodType(sct.ChatCard._start_codex_bridge, dummy)
    monkeypatch.setattr(
        sct,
        "load_codex_settings",
        lambda: {
            "model": "setting-model",
            "working_folder": str(tmp_path / "missing"),
        },
    )

    default_transit = tmp_path / "Terminal Desktop"

    def fake_transit_dir():
        default_transit.mkdir(parents=True, exist_ok=True)
        return default_transit

    monkeypatch.setattr(sct, "transit_dir", fake_transit_dir)
    monkeypatch.setattr(sct, "_legacy_transit_candidates", lambda: [])

    bound()

    assert launches["cwd"] == default_transit
    assert any("Using default transit folder" in text for _, text in messages)
    assert any(str(default_transit) in text for _, text in messages)
