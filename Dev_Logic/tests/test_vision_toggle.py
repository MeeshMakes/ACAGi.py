import types

import Codex_Terminal as sct


def test_disable_vision_skips_pipeline(tmp_path):
    img = tmp_path / "img.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    events = []
    dummy = types.SimpleNamespace(
        settings={
            "enable_vision": False,
            "chat_model": sct.DEFAULT_CHAT_MODEL,
        },
        dataset=types.SimpleNamespace(add_entry=lambda *a, **k: None),
        lex=types.SimpleNamespace(auto_tags=lambda text: []),
        append_signal=types.SimpleNamespace(
            emit=lambda msg: events.append(msg.text)
        ),
        conv=types.SimpleNamespace(append=lambda *a, **k: None),
        state_signal=types.SimpleNamespace(emit=lambda *a, **k: None),
        messages=[],
        context_pairs=0,
        ollama=types.SimpleNamespace(
            chat=lambda *a, **k: (True, "ok", None)
        ),
    )

    def fake_sum(self, imgs, text):
        events.append("summarized")
        return [], [], ""

    dummy._summarize_images_dual = types.MethodType(fake_sum, dummy)
    dummy._gather_context = lambda q: []
    dummy._system_prompt = types.MethodType(sct.ChatCard._system_prompt, dummy)
    dummy._record_message = lambda *a, **k: None

    sct.ChatCard._infer_thread(dummy, "hello", [img])

    assert "summarized" not in events
