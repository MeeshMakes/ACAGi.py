"""PySide6 editor card with inline chat, notes, and summarization."""

from __future__ import annotations

import html
import json
import keyword
import os
import re
import subprocess
import sys
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from PySide6.QtCore import Qt, QRect, QSize, QTimer, QUrl
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPalette,
    QTextCharFormat,
    QTextCursor,
    QSyntaxHighlighter,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import logic_doc

try:  # pragma: no cover - optional import
    from Codex_Terminal import OllamaClient  # type: ignore
except Exception:  # pragma: no cover - fallback when module unavailable
    OllamaClient = None  # type: ignore


_STORAGE_ROOT = Path("memory")
_CHAT_DIR_NAME = "editor_chats"
_NOTES_DIR_NAME = "editor_notes"
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_SLUG_PATTERN = re.compile(r"[^a-zA-Z0-9]+")


@dataclass
class Theme:
    """Minimal theme definition for consistent styling."""

    background: str = "#0b1828"
    foreground: str = "#d6e6ff"
    panel_bg: str = "#101d33"
    accent: str = "#1E5AFF"
    muted: str = "#9bb4dd"


@dataclass
class ConversationEntry:
    role: str
    content: str
    model: str
    timestamp: str


@dataclass
class PinnedNote:
    note_id: str
    content: str
    source: str
    timestamp: str

    def title(self) -> str:
        for line in self.content.splitlines():
            stripped = line.strip()
            if stripped:
                if len(stripped) > 60:
                    return stripped[:57] + "…"
                return stripped
        return "(empty note)"


def _slug_for_path(path: Optional[Path]) -> str:
    if path is None:
        return "buffer"
    try:
        resolved = path.resolve()
    except Exception:
        resolved = path
    slug = _SLUG_PATTERN.sub("-", str(resolved)).strip("-")
    return slug or "buffer"


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:  # pragma: no cover - trivial
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # pragma: no cover - trivial paint hook
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Plain text editor with line numbers and themed palette."""

    def __init__(self, theme: Theme, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._line_area = LineNumberArea(self)
        self._error_selections: List[QTextEdit.ExtraSelection] = []
        self._current_line_selection: Optional[QTextEdit.ExtraSelection] = None
        self.blockCountChanged.connect(self._update_line_area_width)
        self.updateRequest.connect(self._update_line_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._apply_palette()
        self._update_line_area_width(0)
        self._highlight_current_line()

    def _apply_palette(self) -> None:
        palette = self.palette()
        bg = QColor(self._theme.background)
        fg = QColor(self._theme.foreground)
        sel = QColor(self._theme.accent)
        for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            palette.setColor(group, QPalette.Base, bg)
            palette.setColor(group, QPalette.Text, fg)
            palette.setColor(group, QPalette.Window, bg)
            palette.setColor(group, QPalette.WindowText, fg)
            palette.setColor(group, QPalette.Highlight, sel)
            palette.setColor(group, QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)
        self.setStyleSheet(
            "QPlainTextEdit {"
            f" border: 1px solid #1b2a3f;"
            f" border-radius: 10px;"
            f" font-family: 'Cascadia Code', Consolas, monospace;"
            f" font-size: 11pt;"
            f" color: {self._theme.foreground};"
            f" background-color: {self._theme.background};"
            "}"
        )


    def _apply_extra_selections(self) -> None:
        selections: List[QTextEdit.ExtraSelection] = []
        if self._current_line_selection is not None:
            selections.append(self._current_line_selection)
        selections.extend(self._error_selections)
        super().setExtraSelections(selections)

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def _update_line_area_width(self, _new_block_count: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_area(self, rect: QRect, dy: int) -> None:  # pragma: no cover - UI
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_area_width(0)

    def resizeEvent(self, event) -> None:  # pragma: no cover - UI
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event) -> None:  # pragma: no cover - UI
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), QColor("#0f1d33"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        height = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(self._theme.muted))
                painter.drawText(
                    0,
                    int(top),
                    self._line_area.width() - 6,
                    int(height),
                    Qt.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def _highlight_current_line(self) -> None:
        if self.isReadOnly():  # pragma: no cover - simple guard
            return
        selection = QTextEdit.ExtraSelection()
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        selection.format.setBackground(QColor(30, 90, 255, 40))
        selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
        self._current_line_selection = selection
        self._apply_extra_selections()

    def set_error_lines(self, lines: Sequence[int]) -> None:
        selections: List[QTextEdit.ExtraSelection] = []
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(255, 107, 107, 80))
        fmt.setProperty(QTextCharFormat.FullWidthSelection, True)
        doc = self.document()
        for line in lines:
            block = doc.findBlockByLineNumber(max(line - 1, 0))
            if not block.isValid():
                continue
            cursor = QTextCursor(block)
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.cursor.clearSelection()
            selection.format = fmt
            selections.append(selection)
        self._error_selections = selections
        self._apply_extra_selections()


class BasicHighlighter(QSyntaxHighlighter):
    """Lightweight syntax highlighter for a few common languages."""

    def __init__(self, document, language: str = "plain") -> None:
        super().__init__(document)
        self._language = language
        self._keyword_format = QTextCharFormat()
        self._keyword_format.setForeground(QColor("#5ccfe6"))
        bold = QFont()
        bold.setBold(True)
        self._keyword_format.setFont(bold)
        self._comment_format = QTextCharFormat()
        self._comment_format.setForeground(QColor("#7a88b9"))
        self._string_format = QTextCharFormat()
        self._string_format.setForeground(QColor("#c5e478"))
        self._heading_format = QTextCharFormat()
        self._heading_format.setForeground(QColor("#84a9ff"))
        self._number_format = QTextCharFormat()
        self._number_format.setForeground(QColor("#f78c6c"))
        self._patterns: List[re.Pattern[str]] = []
        self._update_patterns()
    def set_language(self, language: str) -> None:
        if language == self._language:
            return
        self._language = language
        self._update_patterns()
        self.rehighlight()

    def _update_patterns(self) -> None:
        self._patterns.clear()
        if self._language == "python":
            kw = "|".join(map(re.escape, keyword.kwlist))
            self._patterns.append(re.compile(rf"\b({kw})\b"))
            self._comment_re = re.compile(r"#[^\n]*")
            self._string_re = re.compile(
                r"('''.*?'''|\"\"\".*?\"\"\"|'[^'\\]*(?:\\.[^'\\]*)*'|\"[^\"\\]*(?:\\.[^\"\\]*)*\")",
                re.S,
            )
            self._number_re = re.compile(r"\b[0-9]+\b")
        elif self._language == "markdown":
            self._heading_re = re.compile(r"^#{1,6}.*$", re.M)
            self._code_fence_re = re.compile(r"```.*?```", re.S)
        elif self._language == "json":
            self._string_re = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"')
            self._number_re = re.compile(r"\b-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b")
            self._keyword_re = re.compile(r"\b(true|false|null)\b")
        else:
            self._comment_re = None
            self._string_re = None
            self._number_re = None

    def highlightBlock(self, text: str) -> None:  # pragma: no cover - rendering
        if self._language == "python":
            for pat in self._patterns:
                for match in pat.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._keyword_format)
            if getattr(self, "_comment_re", None):
                for match in self._comment_re.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._comment_format)
            if getattr(self, "_string_re", None):
                for match in self._string_re.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._string_format)
            if getattr(self, "_number_re", None):
                for match in self._number_re.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._number_format)
        elif self._language == "markdown":
            if getattr(self, "_heading_re", None):
                for match in self._heading_re.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._heading_format)
            if getattr(self, "_code_fence_re", None):
                for match in self._code_fence_re.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._string_format)
        elif self._language == "json":
            if getattr(self, "_string_re", None):
                for match in self._string_re.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._string_format)
            if getattr(self, "_number_re", None):
                for match in self._number_re.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._number_format)
            if getattr(self, "_keyword_re", None):
                for match in self._keyword_re.finditer(text):
                    self.setFormat(match.start(), match.end() - match.start(), self._keyword_format)


class EditorCard(QWidget):
    """Code/markdown editor with summaries, chat, notes, and console."""

    def __init__(
        self,
        *,
        initial_path: Optional[str] = None,
        client: Optional[logic_doc.ChatClient] = None,
        model: str = logic_doc.DEFAULT_SUMMARY_MODEL,
        theme: Theme = Theme(),
        parent: Optional[QWidget] = None,
        storage_root: Optional[os.PathLike[str] | str] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("EditorCard")
        self._theme = theme
        self._model = model
        self._client = client
        self._current_path: Optional[Path] = Path(initial_path) if initial_path else None
        self._summaries: List[logic_doc.SegmentSummary] = []
        self._chat_entries: List[ConversationEntry] = []
        self._notes: dict[str, PinnedNote] = {}
        self._active_note_id: Optional[str] = None
        self._storage_root = Path(storage_root) if storage_root else _STORAGE_ROOT
        self._chat_dir = self._storage_root / _CHAT_DIR_NAME
        self._notes_dir = self._storage_root / _NOTES_DIR_NAME
        self._chat_dir.mkdir(parents=True, exist_ok=True)
        self._notes_dir.mkdir(parents=True, exist_ok=True)
        self._chat_log_path = self._chat_dir / f"{_slug_for_path(self._current_path)}.jsonl"
        self._notes_path = self._notes_dir / f"{_slug_for_path(self._current_path)}.json"
        self._project_root: Optional[Path] = self._discover_project_root()
        self._output_link_map: Dict[str, "ErrorLocation"] = {}
        self._init_ui()
        self._load_chat_history()
        self._load_notes()
        if self._current_path:
            self.load_file(self._current_path)
        else:
            self._update_title()
    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)
        self.title_label = QLabel("Editor")
        self.title_label.setStyleSheet("font: 600 12pt 'Cascadia Code';")
        header.addWidget(self.title_label)
        header.addStretch(1)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {self._theme.muted};")
        header.addWidget(self.status_label)
        layout.addLayout(header)

        tools = QHBoxLayout()
        tools.setSpacing(8)
        self.save_btn = QPushButton("Save")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_file)
        tools.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("Save As…")
        self.save_as_btn.setCursor(Qt.PointingHandCursor)
        self.save_as_btn.clicked.connect(self._save_file_as)
        tools.addWidget(self.save_as_btn)

        self.summarize_btn = QPushButton("Summarize document")
        self.summarize_btn.setCursor(Qt.PointingHandCursor)
        self.summarize_btn.clicked.connect(self.summarize_document)
        tools.addWidget(self.summarize_btn)

        self.diff_btn = QPushButton("Preview Diff")
        self.diff_btn.setCursor(Qt.PointingHandCursor)
        self.diff_btn.clicked.connect(self._preview_diff)
        tools.addWidget(self.diff_btn)

        self.run_btn = QPushButton("Run")
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.clicked.connect(self._run_current_file)
        tools.addWidget(self.run_btn)

        self.test_btn = QPushButton("Run Tests")
        self.test_btn.setCursor(Qt.PointingHandCursor)
        self.test_btn.clicked.connect(self._run_tests)
        tools.addWidget(self.test_btn)
        tools.addStretch(1)
        layout.addLayout(tools)

        self.editor = CodeEditor(self._theme, self)
        self.editor.setObjectName("editorText")
        self.editor.document().modificationChanged.connect(self._on_modification_changed)

        self.highlighter = BasicHighlighter(self.editor.document())

        self.segment_list = QListWidget(self)
        self.segment_list.setObjectName("segmentList")
        self.segment_list.setSelectionMode(QListWidget.SingleSelection)
        self.segment_list.itemSelectionChanged.connect(self._segment_selected)

        self.segment_summary = QTextBrowser(self)
        self.segment_summary.setObjectName("segmentSummary")
        self.segment_summary.setOpenExternalLinks(True)
        self.segment_summary.setPlaceholderText("Select a section to preview its summary.")
        self.segment_summary.document().setDefaultStyleSheet(
            f"body {{ color: {self._theme.foreground}; background-color: {self._theme.panel_bg}; }}"
        )

        self.report_output = QPlainTextEdit(self)
        self.report_output.setObjectName("reportOutput")
        self.report_output.setReadOnly(True)
        self.report_output.setPlaceholderText("Generated markdown report will appear here.")
        self.report_output.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        summary_tab = QWidget(self)
        summary_layout = QVBoxLayout(summary_tab)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(8)
        summary_layout.addWidget(self.segment_list, 1)
        summary_layout.addWidget(self.segment_summary, 1)
        summary_layout.addWidget(self.report_output, 1)

        chat_tab = self._build_chat_tab()
        notes_tab = self._build_notes_tab()

        self.side_tabs = QTabWidget(self)
        self.side_tabs.addTab(summary_tab, "Summaries")
        self.side_tabs.addTab(chat_tab, "Chat")
        self.side_tabs.addTab(notes_tab, "Notes")

        top_splitter = QSplitter(Qt.Horizontal, self)
        top_splitter.setChildrenCollapsible(False)
        top_splitter.addWidget(self.editor)
        top_splitter.addWidget(self.side_tabs)
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 2)

        self.diff_output = QPlainTextEdit(self)
        self.diff_output.setReadOnly(True)
        self.diff_output.setPlaceholderText("Diff preview will appear here.")

        self.run_output = QTextBrowser(self)
        self.run_output.setOpenLinks(False)
        self.run_output.setPlaceholderText("Run and test output will appear here.")
        self.run_output.anchorClicked.connect(self._handle_output_link)

        self.console_tabs = QTabWidget(self)
        self.console_tabs.addTab(self.diff_output, "Diff")
        self.console_tabs.addTab(self.run_output, "Run/Test")

        main_splitter = QSplitter(Qt.Vertical, self)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(self.console_tabs)
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 1)
        layout.addWidget(main_splitter, 1)

        self._set_status("Ready")
        self._populate_model_list()

    def _build_chat_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.setSpacing(6)
        model_label = QLabel("Model:")
        model_label.setStyleSheet(f"color: {self._theme.muted};")
        controls.addWidget(model_label)
        self.chat_model_combo = QComboBox(tab)
        controls.addWidget(self.chat_model_combo, 1)
        self.chat_pin_btn = QPushButton("Pin to notes")
        self.chat_pin_btn.clicked.connect(self._pin_selected_chat)
        controls.addWidget(self.chat_pin_btn)
        layout.addLayout(controls)

        self.chat_list = QListWidget(tab)
        self.chat_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.chat_list, 1)

        self.chat_input = QPlainTextEdit(tab)
        self.chat_input.setPlaceholderText("Ask a question about this file…")
        self.chat_input.setFixedHeight(90)
        layout.addWidget(self.chat_input)

        bottom = QHBoxLayout()
        bottom.setSpacing(6)
        self.chat_status = QLabel("")
        self.chat_status.setStyleSheet(f"color: {self._theme.muted};")
        bottom.addWidget(self.chat_status, 1)
        self.chat_send_btn = QPushButton("Send")
        self.chat_send_btn.clicked.connect(self._send_chat_message)
        bottom.addWidget(self.chat_send_btn)
        layout.addLayout(bottom)
        return tab

    def _build_notes_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        buttons = QHBoxLayout()
        buttons.setSpacing(6)
        self.note_new_btn = QPushButton("New note")
        self.note_new_btn.clicked.connect(self._create_note)
        buttons.addWidget(self.note_new_btn)
        self.note_pin_selection_btn = QPushButton("Pin selection")
        self.note_pin_selection_btn.clicked.connect(self._pin_editor_selection)
        buttons.addWidget(self.note_pin_selection_btn)
        self.note_delete_btn = QPushButton("Delete")
        self.note_delete_btn.clicked.connect(self._delete_note)
        buttons.addWidget(self.note_delete_btn)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        self.note_list = QListWidget(tab)
        self.note_list.setSelectionMode(QListWidget.SingleSelection)
        self.note_list.itemSelectionChanged.connect(self._on_note_selected)
        layout.addWidget(self.note_list, 1)

        self.note_editor = QPlainTextEdit(tab)
        self.note_editor.setPlaceholderText("Select or create a note to edit…")
        layout.addWidget(self.note_editor, 1)

        save_row = QHBoxLayout()
        save_row.setSpacing(6)
        self.note_status = QLabel("")
        self.note_status.setStyleSheet(f"color: {self._theme.muted};")
        save_row.addWidget(self.note_status, 1)
        self.note_save_btn = QPushButton("Save note")
        self.note_save_btn.clicked.connect(self._save_note_content)
        save_row.addWidget(self.note_save_btn)
        layout.addLayout(save_row)
        return tab

    def load_file(self, path: os.PathLike[str] | str) -> None:
        try:
            source = Path(path)
            text = source.read_text(encoding="utf-8")
        except Exception as exc:
            self.editor.setPlainText(f"[open failed] {exc}")
            self._set_status(f"Failed to open {path}: {exc}")
            return
        self._current_path = source
        self._project_root = self._discover_project_root()
        self.editor.setPlainText(text)
        self.editor.document().setModified(False)
        self._update_title()
        self._chat_log_path = self._chat_dir / f"{_slug_for_path(self._current_path)}.jsonl"
        self._notes_path = self._notes_dir / f"{_slug_for_path(self._current_path)}.json"
        self._load_chat_history()
        self._load_notes()
        self.highlighter.set_language(self._language_for_path(self._current_path))
        self._set_status(f"Loaded {source.name}")

    def summarize_document(self) -> None:
        text = self.editor.toPlainText()
        segments = logic_doc.parse_segments(text, fallback_title=self._current_title())
        if not segments:
            self._set_status("No sections detected.")
            return
        client = self._ensure_client()
        summaries = logic_doc.summarize_segments(
            segments,
            client=client,
            model=self._model,
        )
        self._summaries = summaries
        report = logic_doc.build_summary_markdown(summaries, source=self._current_path)
        self.report_output.setPlainText(report)
        self._populate_segments()
        saved = logic_doc.write_report(self._current_path, report)
        if saved is not None:
            self._set_status(f"Summary saved to {saved.name}")
        else:
            self._set_status("Summary generated (unsaved buffer).")

    @property
    def chat_log_path(self) -> Path:
        return self._chat_log_path

    @property
    def notes_path(self) -> Path:
        return self._notes_path

    def _ensure_client(self) -> Optional[logic_doc.ChatClient]:
        if self._client is not None:
            return self._client
        if OllamaClient is None:
            return None
        self._client = OllamaClient()  # type: ignore[call-arg]
        return self._client

    def _current_title(self) -> str:
        if self._current_path is None:
            return "Document"
        return self._current_path.name

    def _populate_segments(self) -> None:
        self.segment_list.clear()
        for summary in self._summaries:
            title = f"{summary.segment.title} (L{summary.segment.start_line})"
            if summary.error:
                title += " — error"
            item = QListWidgetItem(title, self.segment_list)
            item.setData(Qt.UserRole, summary)
        if self.segment_list.count():
            self.segment_list.setCurrentRow(0)

    def _segment_selected(self) -> None:
        items = self.segment_list.selectedItems()
        if not items:
            self.segment_summary.clear()
            return
        summary: logic_doc.SegmentSummary = items[0].data(Qt.UserRole)
        if summary.error:
            self.segment_summary.setPlainText(f"Summary failed: {summary.error}")
        else:
            self.segment_summary.setPlainText(summary.summary or "(empty summary)")
        self._jump_to_line(summary.segment.start_line)

    def _jump_to_line(self, line: int) -> None:
        doc = self.editor.document()
        block = doc.findBlockByLineNumber(max(line - 1, 0))
        cursor = QTextCursor(block)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()

    def _set_status(self, message: str) -> None:
        self.status_label.setText(message)

    def _update_title(self) -> None:
        name = self._current_title()
        if self.editor.document().isModified():
            name = f"*{name}"
        self.title_label.setText(f"Editor — {name}")

    def _on_modification_changed(self, _changed: bool) -> None:
        self._update_title()

    def _language_for_path(self, path: Optional[Path]) -> str:
        if not path:
            return "plain"
        suffix = path.suffix.lower()
        if suffix == ".py":
            return "python"
        if suffix in {".md", ".markdown"}:
            return "markdown"
        if suffix in {".json", ".jsonl"}:
            return "json"
        return "plain"
    def _save_file(self) -> None:
        if self._current_path is None:
            self._save_file_as()
            return
        try:
            self._current_path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except Exception as exc:
            QMessageBox.warning(self, "Save failed", str(exc))
            self._set_status(f"Save failed: {exc}")
            return
        self.editor.document().setModified(False)
        self._set_status(f"Saved {self._current_path.name}")

    def _save_file_as(self) -> None:
        suggested = str(self._current_path) if self._current_path else ""
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", suggested)
        if not filename:
            return
        self._current_path = Path(filename)
        self._project_root = self._discover_project_root()
        try:
            self._current_path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except Exception as exc:
            QMessageBox.warning(self, "Save failed", str(exc))
            self._set_status(f"Save failed: {exc}")
            return
        self.editor.document().setModified(False)
        self._update_title()
        self._chat_log_path = self._chat_dir / f"{_slug_for_path(self._current_path)}.jsonl"
        self._notes_path = self._notes_dir / f"{_slug_for_path(self._current_path)}.json"
        self._set_status(f"Saved {self._current_path.name}")

    def _populate_model_list(self) -> None:
        models: Sequence[str] = []
        client = self._ensure_client()
        if client is not None and hasattr(client, "list_models"):
            try:
                ok, names, _ = client.list_models()  # type: ignore[attr-defined]
            except Exception:
                ok, names = False, []
            if ok and names:
                models = sorted(set(names))
        if not models:
            models = sorted({self._model, "codex", "llama3:8b", "qwen3:8b"})
        self.chat_model_combo.clear()
        self.chat_model_combo.addItems(models)
        idx = self.chat_model_combo.findText(self._model)
        if idx >= 0:
            self.chat_model_combo.setCurrentIndex(idx)

    def _load_chat_history(self) -> None:
        self._chat_entries.clear()
        if self._chat_log_path.exists():
            try:
                with self._chat_log_path.open("r", encoding="utf-8") as fh:
                    for line in fh:
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        entry = ConversationEntry(
                            role=data.get("role", "user"),
                            content=data.get("content", ""),
                            model=data.get("model", self._model),
                            timestamp=data.get("timestamp", self._now()),
                        )
                        self._chat_entries.append(entry)
            except Exception:
                self._chat_entries.clear()
        self._refresh_chat_view()

    def _refresh_chat_view(self) -> None:
        self.chat_list.clear()
        for entry in self._chat_entries:
            prefix = "You" if entry.role == "user" else "Assistant"
            item = QListWidgetItem(f"{prefix} — {entry.timestamp}\n{entry.content}")
            item.setData(Qt.UserRole, entry)
            self.chat_list.addItem(item)
        if self.chat_list.count():
            self.chat_list.scrollToBottom()

    def _append_chat_entry(self, entry: ConversationEntry, persist: bool = True) -> None:
        self._chat_entries.append(entry)
        if persist:
            try:
                with self._chat_log_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry.__dict__) + "\n")
            except Exception:
                pass
        self._refresh_chat_view()

    def _send_chat_message(self) -> None:
        text = self.chat_input.toPlainText().strip()
        if not text:
            self._set_chat_status("Enter a prompt to send.")
            return
        model = self.chat_model_combo.currentText() or self._model
        entry = ConversationEntry(role="user", content=text, model=model, timestamp=self._now())
        self._append_chat_entry(entry)
        self.chat_input.clear()
        client = self._ensure_client()
        if client is None:
            self._set_chat_status("LLM client unavailable; logged prompt only.")
            return
        messages = [{"role": item.role, "content": item.content} for item in self._chat_entries]
        self._set_chat_status("Contacting model…")
        self._toggle_chat_enabled(False)

        def worker() -> tuple[bool, str, str]:
            try:
                return client.chat(model, messages)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive
                return False, "", str(exc)

        self._run_async(worker, lambda result: self._handle_chat_response(model, result))

    def _handle_chat_response(self, model: str, result: tuple[bool, str, str]) -> None:
        ok, content, error = result
        if ok and content.strip():
            entry = ConversationEntry(role="assistant", content=content.strip(), model=model, timestamp=self._now())
            self._append_chat_entry(entry)
            self._set_chat_status("Response received.")
        else:
            self._set_chat_status(error or "Model returned no content.")
        self._toggle_chat_enabled(True)

    def _toggle_chat_enabled(self, enabled: bool) -> None:
        self.chat_send_btn.setEnabled(enabled)
        self.chat_input.setEnabled(enabled)
        self.chat_model_combo.setEnabled(enabled)

    def _set_chat_status(self, message: str) -> None:
        self.chat_status.setText(message)

    def _pin_selected_chat(self) -> None:
        items = self.chat_list.selectedItems()
        if not items:
            self._set_chat_status("Select a message to pin.")
            return
        entry: ConversationEntry = items[0].data(Qt.UserRole)
        self._create_note_from_text(entry.content, source=f"chat:{entry.role}")
        self._set_chat_status("Pinned chat message to notes.")
    def _load_notes(self) -> None:
        self._notes.clear()
        if self._notes_path.exists():
            try:
                data = json.loads(self._notes_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for node in data:
                        try:
                            note = PinnedNote(
                                note_id=node["note_id"],
                                content=node.get("content", ""),
                                source=node.get("source", "manual"),
                                timestamp=node.get("timestamp", self._now()),
                            )
                            self._notes[note.note_id] = note
                        except Exception:
                            continue
            except Exception:
                self._notes.clear()
        self._refresh_notes_view()

    def _refresh_notes_view(self) -> None:
        self.note_list.clear()
        for note in self._notes.values():
            item = QListWidgetItem(f"{note.title()}\n{note.source} — {note.timestamp}")
            item.setData(Qt.UserRole, note.note_id)
            self.note_list.addItem(item)
        if self.note_list.count():
            self.note_list.setCurrentRow(0)
        else:
            self.note_editor.clear()
            self._active_note_id = None

    def _create_note(self) -> None:
        note_id = uuid.uuid4().hex
        note = PinnedNote(note_id=note_id, content="", source="manual", timestamp=self._now())
        self._notes[note_id] = note
        self._persist_notes()
        self._refresh_notes_view()
        self._select_note(note_id)
        self._set_note_status("Created empty note.")

    def _pin_editor_selection(self) -> None:
        cursor = self.editor.textCursor()
        text = cursor.selectedText().replace("\u2029", "\n").strip()
        if not text:
            self._set_note_status("Select text in the editor first.")
            return
        self._create_note_from_text(text, source="editor")
        self._set_note_status("Pinned editor selection.")

    def _create_note_from_text(self, text: str, *, source: str) -> None:
        note_id = uuid.uuid4().hex
        note = PinnedNote(note_id=note_id, content=text.strip(), source=source, timestamp=self._now())
        self._notes[note_id] = note
        self._persist_notes()
        self._refresh_notes_view()
        self._select_note(note_id)

    def _delete_note(self) -> None:
        items = self.note_list.selectedItems()
        if not items:
            self._set_note_status("Select a note to delete.")
            return
        note_id = items[0].data(Qt.UserRole)
        if note_id in self._notes:
            del self._notes[note_id]
            self._persist_notes()
            self._refresh_notes_view()
            self._set_note_status("Deleted note.")

    def _on_note_selected(self) -> None:
        items = self.note_list.selectedItems()
        if not items:
            self._active_note_id = None
            self.note_editor.clear()
            return
        note_id = items[0].data(Qt.UserRole)
        note = self._notes.get(note_id)
        self._active_note_id = note_id
        if note:
            self.note_editor.setPlainText(note.content)
        else:
            self.note_editor.clear()

    def _save_note_content(self) -> None:
        if not self._active_note_id or self._active_note_id not in self._notes:
            self._set_note_status("Select a note to save.")
            return
        note = self._notes[self._active_note_id]
        note.content = self.note_editor.toPlainText().strip()
        note.timestamp = self._now()
        self._persist_notes()
        self._refresh_notes_view()
        self._select_note(self._active_note_id)
        self._set_note_status("Note saved.")

    def _persist_notes(self) -> None:
        try:
            payload = [note.__dict__ for note in self._notes.values()]
            self._notes_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _select_note(self, note_id: str) -> None:
        for idx in range(self.note_list.count()):
            item = self.note_list.item(idx)
            if item.data(Qt.UserRole) == note_id:
                self.note_list.setCurrentRow(idx)
                return

    def _set_note_status(self, message: str) -> None:
        self.note_status.setText(message)

    def _preview_diff(self) -> None:
        if self._current_path is None:
            self._set_status("Save file before diff preview.")
            return
        if self.editor.document().isModified():
            self._set_status("Save changes before generating diff.")
            return

        def worker() -> tuple[int, str, str]:
            try:
                result = subprocess.run(
                    ["git", "diff", "--", str(self._current_path)],
                    cwd=self._current_path.parent,
                    capture_output=True,
                    text=True,
                )
                return result.returncode, result.stdout, result.stderr
            except Exception as exc:  # pragma: no cover - defensive
                return 1, "", str(exc)

        self._set_status("Running git diff…")
        self._run_async(worker, self._update_diff_output)

    def _update_diff_output(self, result: tuple[int, str, str]) -> None:
        rc, out, err = result
        if rc != 0:
            self.diff_output.setPlainText(err or out or "git diff failed")
            self._set_status("Diff preview failed.")
        else:
            self.diff_output.setPlainText(out or "(no changes)")
            self._set_status("Diff preview updated.")

    def _run_current_file(self) -> None:
        if self._current_path is None:
            self._set_status("Save file before running.")
            return
        if self.editor.document().isModified():
            self._set_status("Save changes before running.")
            return
        if self._current_path.suffix != ".py":
            self._set_status("Run is supported for Python files only.")
            return
        command = [sys.executable, str(self._current_path)]
        self._start_command("Run", command, self._current_path.parent)

    def _run_tests(self) -> None:
        project_root = self._ensure_project_root()
        if project_root is None:
            self._set_status("Project root not found for tests.")
            return
        command = [sys.executable, str(project_root / "tools" / "manage_tests.py")]
        self._start_command("Tests", command, project_root)

    def _start_command(self, label: str, command: Sequence[str], cwd: Path) -> None:
        def worker() -> CommandResult:
            try:
                result = subprocess.run(
                    command,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                )
                return CommandResult(
                    label=label,
                    command=list(command),
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
            except Exception as exc:  # pragma: no cover - defensive
                return CommandResult(
                    label=label,
                    command=list(command),
                    returncode=1,
                    stdout="",
                    stderr=str(exc),
                )

        self._set_status(f"{label} running…")
        self._prepare_run_output()
        self._run_async(worker, self._handle_command_result)

    def _prepare_run_output(self) -> None:
        self.console_tabs.setCurrentWidget(self.run_output)
        self.run_output.setHtml("<i>Running…</i>")
        self._output_link_map.clear()
        self.editor.set_error_lines([])

    def _handle_command_result(self, result: CommandResult) -> None:
        html_output, link_map = self._compose_output_html(result)
        self._output_link_map = link_map
        self.run_output.setHtml(html_output)
        self._highlight_editor_errors(link_map.values())
        if result.returncode == 0:
            self._set_status(f"{result.label} completed.")
        else:
            self._set_status(f"{result.label} failed ({result.returncode}).")

    def _compose_output_html(self, result: CommandResult) -> tuple[str, Dict[str, "ErrorLocation"]]:
        command_str = html.escape(" ".join(result.command))
        header = (
            f'<div style="color:{self._theme.muted}; font-family:\'Cascadia Code\', Consolas, monospace;">'
            f'$ {command_str}</div>'
        )
        streams_html, link_map = self._compose_stream_sections(result.stdout, result.stderr)
        return header + streams_html, link_map

    def _compose_stream_sections(
        self, stdout: str, stderr: str
    ) -> tuple[str, Dict[str, "ErrorLocation"]]:
        sections: List[str] = []
        link_map: Dict[str, ErrorLocation] = {}
        counter = 0
        for prefix, title, content, color in (
            ("stdout", "Standard Output", stdout, "#7bc6ff"),
            ("stderr", "Standard Error", stderr, "#ff9b9b"),
        ):
            if not content:
                continue
            block_html, block_links, counter = self._render_output_with_links(
                content, prefix, counter
            )
            sections.append(
                '<div style="margin-bottom:8px;">'
                f'<div style="color:{color}; font-weight:600;">{title}</div>'
                '<div style="font-family:\'Cascadia Code\', Consolas, monospace; white-space:pre-wrap;">'
                f'{block_html}</div></div>'
            )
            link_map.update(block_links)
        if not sections:
            sections.append(
                '<div style="font-family:\'Cascadia Code\', Consolas, monospace;"><i>(no output)</i></div>'
            )
        return "".join(sections), link_map

    def _render_output_with_links(
        self, text: str, prefix: str, start_index: int
    ) -> tuple[str, Dict[str, "ErrorLocation"], int]:
        lines = text.splitlines()
        if not lines:
            lines = [""]
        html_lines: List[str] = []
        link_map: Dict[str, ErrorLocation] = {}
        counter = start_index
        for raw in lines:
            locations = self._find_error_locations(raw)
            escaped = html.escape(raw) if raw else "&nbsp;"
            if locations:
                primary = locations[0]
                anchor = f"{prefix}-{counter}"
                counter += 1
                link_map[anchor] = primary
                html_lines.append(
                    '<span style="color:#ff6b6b;">'
                    f'<a href="{anchor}" style="color:#ff6b6b; text-decoration: underline;">'
                    f'{escaped}</a></span>'
                )
                for extra in locations[1:]:
                    anchor = f"{prefix}-{counter}"
                    counter += 1
                    link_map[anchor] = extra
                    html_lines.append(
                        '<span style="color:#ff6b6b;">↳ '
                        f'<a href="{anchor}" style="color:#ff6b6b; text-decoration: underline;">'
                        f'{html.escape(extra.path.name)}:{extra.line}</a></span>'
                    )
            else:
                html_lines.append(escaped)
        return "<br>".join(html_lines), link_map, counter

    def _find_error_locations(self, line: str) -> List["ErrorLocation"]:
        locations: List[ErrorLocation] = []
        seen: set[tuple[Path, int]] = set()
        for pattern in (_TRACEBACK_RE, _PYTEST_RE):
            for match in pattern.finditer(line):
                raw_path, line_text = match.groups()[:2]
                resolved = self._resolve_error_path(raw_path)
                if resolved is None:
                    continue
                try:
                    line_no = int(line_text)
                except ValueError:
                    continue
                key = (resolved, line_no)
                if key in seen:
                    continue
                seen.add(key)
                locations.append(ErrorLocation(resolved, line_no))
        return locations

    def _resolve_error_path(self, raw_path: str) -> Optional[Path]:
        candidate = Path(raw_path.strip().strip("'\""))
        possibilities: List[Path] = []
        if candidate.is_absolute():
            possibilities.append(candidate)
        else:
            if self._project_root is not None:
                possibilities.append(self._project_root / candidate)
            if self._current_path is not None:
                possibilities.append(self._current_path.parent / candidate)
        for option in possibilities:
            try:
                resolved = option.resolve()
            except Exception:
                resolved = option
            if resolved.exists():
                return resolved
        if self._current_path is not None and candidate.name == self._current_path.name:
            return self._current_path
        if candidate.is_absolute():
            return candidate
        return None

    def _highlight_editor_errors(self, locations: Iterable["ErrorLocation"]) -> None:
        if self._current_path is None:
            self.editor.set_error_lines([])
            return
        try:
            current = self._current_path.resolve()
        except Exception:
            current = self._current_path
        lines = sorted(
            {loc.line for loc in locations if self._paths_match(loc.path, current)}
        )
        self.editor.set_error_lines(lines)

    def _paths_match(self, left: Path, right: Path) -> bool:
        try:
            return left.resolve() == right.resolve()
        except Exception:
            return left == right

    def _handle_output_link(self, url: QUrl) -> None:
        key = url.toString()
        location = self._output_link_map.get(key)
        if location is None:
            return
        if self._current_path is not None and self._paths_match(
            location.path, self._current_path
        ):
            self._jump_to_line(location.line)
        else:
            self._set_status(f"Open {location.path}:{location.line} in editor")

    def _discover_project_root(self) -> Optional[Path]:
        if self._current_path is None:
            return None
        search = self._current_path.parent
        for candidate in [search, *search.parents]:
            if (candidate / "tools" / "manage_tests.py").exists():
                return candidate
            if (candidate / ".git").exists():
                return candidate
        return None

    def _ensure_project_root(self) -> Optional[Path]:
        if self._project_root is None or not self._project_root.exists():
            self._project_root = self._discover_project_root()
        return self._project_root

    def _run_async(self, worker, callback) -> None:
        def runner():
            outcome = worker()
            QTimer.singleShot(0, lambda: callback(outcome))

        threading.Thread(target=runner, daemon=True).start()

    def _now(self) -> str:
        return datetime.utcnow().strftime(_TIMESTAMP_FORMAT)


@dataclass
class CommandResult:
    label: str
    command: List[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass
class ErrorLocation:
    path: Path
    line: int


_TRACEBACK_RE = re.compile(r'File "([^"]+)", line (\d+)')
_PYTEST_RE = re.compile(r'([^\s:]+\.py):(\d+)')


def build_widget(
    parent: Optional[QWidget] = None,
    *,
    initial_path: Optional[str] = None,
    client: Optional[logic_doc.ChatClient] = None,
    model: str = logic_doc.DEFAULT_SUMMARY_MODEL,
    theme: Optional[Theme] = None,
    storage_root: Optional[os.PathLike[str] | str] = None,
) -> EditorCard:
    """Factory used by the Virtual Desktop to create the editor card."""

    return EditorCard(
        initial_path=initial_path,
        client=client,
        model=model,
        theme=theme or Theme(),
        parent=parent,
        storage_root=storage_root,
    )
