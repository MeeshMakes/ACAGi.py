import editor.logic_doc as logic


def test_parse_segments_detects_headings():
    text = (
        "Overview\n\n"
        "Intro paragraph.\n\n"
        "Section One\n\n"
        "Details about one.\n\n"
        "Section Two:\n\n"
        "Details about two.\n"
    )

    segments = logic.parse_segments(text, fallback_title="Doc")

    titles = [seg.title for seg in segments]
    assert titles == ["Overview", "Section One", "Section Two"]
    assert segments[0].start_line == 1
    assert segments[1].start_line == 5
    assert segments[2].start_line == 9
    assert "Details about two" in segments[2].content


def test_parse_segments_falls_back_when_no_headings():
    text = "Single paragraph without headings.\nSecond line."

    segments = logic.parse_segments(text, fallback_title="Doc")

    assert len(segments) == 1
    assert segments[0].title == "Doc"
    assert segments[0].start_line == 1
    assert segments[0].end_line == 2


def test_summarize_segments_invokes_client():
    class StubClient:
        def __init__(self):
            self.calls = []
            self.responses = ["Summary A", "Summary B"]

        def chat(self, model, messages, images=None):
            self.calls.append((model, messages))
            return True, self.responses[len(self.calls) - 1], ""

    segs = [
        logic.Segment(
            title="Alpha",
            start_line=1,
            end_line=3,
            content="Alpha body",
        ),
        logic.Segment(
            title="Beta",
            start_line=4,
            end_line=6,
            content="Beta body",
        ),
    ]

    client = StubClient()
    results = logic.summarize_segments(segs, client=client, model="model")

    assert len(results) == 2
    assert results[0].summary == "Summary A"
    assert results[1].summary == "Summary B"
    assert client.calls[0][0] == "model"
    assert "Alpha" in client.calls[0][1][1]["content"]


def test_build_summary_markdown_includes_editor_links(tmp_path):
    segment = logic.Segment(
        title="Alpha",
        start_line=5,
        end_line=10,
        content="body",
    )
    summary = logic.SegmentSummary(segment=segment, summary="- point")
    source = tmp_path / "doc.md"
    source.write_text("Alpha\n", encoding="utf-8")

    markdown = logic.build_summary_markdown([summary], source=source)

    assert "editor://doc.md?line=5" in markdown
    assert "## Alpha" in markdown
    assert "point" in markdown

    target = logic.write_report(source, markdown)
    assert target and target.read_text(encoding="utf-8") == markdown
