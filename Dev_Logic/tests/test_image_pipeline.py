import base64

import pytest

import image_pipeline as ip

SMALL_PNG = base64.b64decode(
    (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
        "nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )
)


@pytest.mark.skipif(ip.Image is None, reason="Pillow not installed")
def test_perform_ocr_with_stub_engine(tmp_path):
    class StubEngine:
        def image_to_string(self, image, lang="eng"):
            return "Hello\nWorld"

    img = tmp_path / "image.png"
    img.write_bytes(SMALL_PNG)

    result = ip.perform_ocr(img, engine=StubEngine())

    assert result.ok
    assert "Hello" in result.text
    assert "Hello" in result.markdown


@pytest.mark.skipif(ip.Image is None, reason="Pillow not installed")
def test_perform_ocr_missing_engine(tmp_path, monkeypatch):
    img = tmp_path / "image.png"
    img.write_bytes(SMALL_PNG)

    monkeypatch.setattr(ip, "pytesseract", None)
    result = ip.perform_ocr(img, engine=None)

    assert not result.ok
    assert "pytesseract" in (result.error or "").lower()


def test_analyze_image_invokes_client(tmp_path):
    img = tmp_path / "image.png"
    img.write_bytes(SMALL_PNG)

    class StubClient:
        def __init__(self):
            self.calls = []

        def chat(self, model, messages, images=None):
            # pragma: no cover - exercised indirectly
            self.calls.append((model, messages, images))
            return True, "Summary text", ""

    client = StubClient()
    result = ip.analyze_image(
        img,
        "ocr markdown",
        client=client,
        model="vision-model",
        user_text="hello",
    )

    assert result.ok
    assert result.summary == "Summary text"
    assert client.calls
    called_model, messages, images = client.calls[0]
    assert called_model == "vision-model"
    assert images and isinstance(images[0], str)
    content = messages[1]["content"]
    assert "OCR Markdown" in content


def test_analyze_image_requires_client(tmp_path):
    img = tmp_path / "image.png"
    img.write_bytes(SMALL_PNG)

    result = ip.analyze_image(
        img,
        "ocr markdown",
        client=None,
        model="vision-model",
    )

    assert not result.ok
    assert "client" in (result.error or "").lower()


@pytest.mark.skipif(ip.Image is None, reason="Pillow not installed")
def test_thumbnailize_conversation_markdown(tmp_path):
    conv = tmp_path / "conversation.md"
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    first = images_dir / "first.png"
    second = images_dir / "second.png"
    third = images_dir / "third.png"
    for target in (first, second, third):
        target.write_bytes(SMALL_PNG)

    conv.write_text(
        "# Conversation\n\n"
        "**User:**\n\nHello\n\n"
        "![image](images/first.png)\n"
        "![image](images/second.png)\n"
        "![image](images/third.png)\n",
        encoding="utf-8",
    )

    updates = ip.thumbnailize_conversation_markdown(
        conv,
        keep_recent=1,
        max_size=(1, 1),
    )

    assert len(updates) == 2
    assert all(up.thumbnail_path.exists() for up in updates)

    text = conv.read_text(encoding="utf-8")
    assert "images/first_thumb.png" in text
    assert "images/second_thumb.png" in text
    assert "images/third.png" in text

    restored = ip.restore_conversation_image(conv, first)
    assert restored
    text_after = conv.read_text(encoding="utf-8")
    assert "images/first.png" in text_after
    assert "images/first_thumb.png" not in text_after
