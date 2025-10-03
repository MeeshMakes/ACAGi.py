import types
import Codex_Terminal as sct


def test_on_images_from_editor_appends_path(tmp_path):
    img = tmp_path / "img.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    events = []
    dummy = types.SimpleNamespace(
        pending_images=[],
        input=types.SimpleNamespace(
            append=lambda s: events.append(("append", s))
        ),
        _convert_to_png=lambda p: p,
        _append_html=lambda *a, **k: None,
        settings={"enable_vision": True},
    )
    sct.ChatCard._on_images_from_editor(dummy, [img])
    expected = f'view_image "{img.as_posix()}"'
    assert events == [("append", expected)]
