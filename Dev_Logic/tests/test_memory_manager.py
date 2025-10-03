import json
from pathlib import Path

from memory_manager import MemoryManager


def _text_embed(text: str):
    text_lower = text.lower()
    if "diagram" in text_lower:
        return [0.0, 1.0]
    if "world" in text_lower:
        return [1.0, 0.0]
    return [0.70710678, 0.70710678]


def _image_embed(path: Path):
    try:
        data = path.read_text(encoding="utf-8")
    except OSError:
        data = ""
    lower = data.lower()
    if "diagram" in lower:
        return [0.0, 1.0]
    return [1.0, 0.0]


def test_log_interaction_records_embeddings(tmp_path):
    manager = MemoryManager(
        tmp_path,
        text_embedder=_text_embed,
        image_embedder=_image_embed,
        enable_embeddings=True,
    )
    img_path = tmp_path / "image.txt"
    img_path.write_text("diagram sketch", encoding="utf-8")

    entry = manager.log_interaction(
        "session-a",
        "assistant",
        "hello world",
        images=[img_path],
        ocr_map={img_path.name: "diagram of world"},
        tags=["vision"],
        metadata={"source": "vision-pipeline"},
    )

    dataset_path = (
        tmp_path / "conversations" / "session-a" / "conversation.jsonl"
    )
    assert dataset_path.exists()
    dataset_text = dataset_path.read_text(encoding="utf-8")
    lines = [
        json.loads(line)
        for line in dataset_text.splitlines()
        if line
    ]
    last_line = lines[-1]
    assert last_line["metadata"]["source"] == "vision-pipeline"
    assert last_line["tags"] == ["vision"]
    image_entry = last_line["images"][0]
    assert image_entry["ocr_text"] == "diagram of world"
    assert image_entry["image_embedding"], "image embedding stored"
    assert image_entry["ocr_embedding"], "ocr embedding stored"
    assert entry["text_embedding"], "entry should include text embedding"


def test_search_images_uses_ocr_and_image_vectors(tmp_path):
    manager = MemoryManager(
        tmp_path,
        text_embedder=_text_embed,
        image_embedder=_image_embed,
        enable_embeddings=True,
    )
    img_path = tmp_path / "diagram.png"
    img_path.write_text("simple diagram", encoding="utf-8")
    manager.log_interaction(
        "session-b",
        "assistant",
        "initial response",
        images=[img_path],
        ocr_map={img_path.name: "diagram labels"},
        tags=["vision"],
        metadata={"id": 1},
    )

    fresh_manager = MemoryManager(
        tmp_path,
        text_embedder=_text_embed,
        image_embedder=_image_embed,
        enable_embeddings=True,
    )
    results = fresh_manager.search_images("diagram", k=1)
    assert results, "expected at least one match"
    top = results[0]
    assert top["session"] == "session-b"
    assert top["metadata"]["id"] == 1
    assert top["ocr_text"] == "diagram labels"
    assert top["score"] > 0.5

    filtered = fresh_manager.search_images(
        "diagram",
        k=1,
        session_filter="missing",
    )
    assert filtered == []
