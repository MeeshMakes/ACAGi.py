import prompt_loader


def _reset_loader(tmp_path, monkeypatch):
    monkeypatch.setattr(prompt_loader, "PROMPTS_DIR", tmp_path)
    prompt_loader._PROMPT_CACHE.clear()


def test_prompt_loader_falls_back_to_default(tmp_path, monkeypatch):
    _reset_loader(tmp_path, monkeypatch)
    watcher = prompt_loader.get_prompt_watcher("chat_system")
    default_text = prompt_loader._PROMPT_DEFINITIONS["chat_system"].default
    assert watcher.text() == default_text
    created = tmp_path / "chat_system.txt"
    assert created.exists()
    assert created.read_text(encoding="utf-8").strip() == default_text


def test_prompt_loader_merges_overlay_and_hot_reload(tmp_path, monkeypatch):
    _reset_loader(tmp_path, monkeypatch)
    base = tmp_path / "chat_system.txt"
    base.write_text("Base", encoding="utf-8")
    overlay = tmp_path / "chat_system.overlay.txt"
    overlay.write_text("Overlay", encoding="utf-8")

    watcher = prompt_loader.get_prompt_watcher("chat_system")
    assert watcher.text() == "Base\n\nOverlay"

    overlay.write_text("Overlay v2", encoding="utf-8")
    assert watcher.text() == "Base\n\nOverlay v2"
