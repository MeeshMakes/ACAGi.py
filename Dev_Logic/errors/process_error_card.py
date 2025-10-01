"""Red-themed process error console card for the Virtual Desktop."""

from __future__ import annotations

import html
import os
import subprocess
import threading
import time
from typing import Callable, Iterable, List, Optional, Sequence

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from tasks.models import ErrorRecord, append_error_record

RecordWriter = Callable[[ErrorRecord], None]
GuardFn = Callable[[Sequence[str], Optional[str], bool], tuple[bool, str]]
ViolationCallback = Callable[[str], None]


class ProcessErrorCard(QWidget):
    """Widget that launches subprocesses and captures their error output."""

    isolation_requested = Signal(str, object)
    close_requested = Signal()

    _append_entry = Signal(str, str)
    _set_status = Signal(str, bool)
    _set_buttons = Signal(bool, bool)

    def __init__(
        self,
        theme,
        cmd: Sequence[str],
        *,
        cwd: Optional[str] = None,
        guard: Optional[GuardFn] = None,
        allow_external_exec: bool = False,
        violation_cb: Optional[ViolationCallback] = None,
        record_writer: Optional[RecordWriter] = None,
    ) -> None:
        super().__init__()
        self._theme = theme
        self._cmd = list(cmd)
        self._cwd = os.path.abspath(cwd or os.getcwd())
        self._guard = guard
        self._allow_external_exec = bool(allow_external_exec)
        self._violation_cb = violation_cb
        self._record_writer = record_writer or append_error_record

        self._proc: Optional[subprocess.Popen[str]] = None
        self._stdout_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None
        self._wait_thread: Optional[threading.Thread] = None
        self._kill = threading.Event()
        self._terminated_by_user = False
        self._stderr_lines: List[str] = []
        self._stderr_lock = threading.Lock()
        self._running = False

        self._append_entry.connect(self._handle_append)
        self._set_status.connect(self._handle_status)
        self._set_buttons.connect(self._handle_buttons)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("Process Error Console", self)
        title.setStyleSheet("color:#ffb8b8;font:700 12pt 'Cascadia Code';")
        root.addWidget(title)

        self._status_label = QLabel("Ready", self)
        self._status_label.setStyleSheet("color:#ff9292;font:500 9pt 'Segoe UI';")
        root.addWidget(self._status_label)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self._btn_start = QPushButton("Start", self)
        self._btn_stop = QPushButton("Stop", self)
        self._btn_stop.setEnabled(False)
        accent = getattr(theme, "accent", "#ff5c5c")
        border = getattr(theme, "card_border", "#5c1010")
        hover = getattr(theme, "accent_hov", "#ff7676")
        for button in (self._btn_start, self._btn_stop):
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(
                "QPushButton{color:#fff;background:%s;border:1px solid %s;border-radius:6px;padding:6px 12px;}"
                "QPushButton:hover{background:%s;}"
                % (accent, border, hover)
            )
        buttons.addWidget(self._btn_start)
        buttons.addWidget(self._btn_stop)
        buttons.addStretch(1)
        root.addLayout(buttons)

        self._log = QTextBrowser(self)
        self._log.setAcceptRichText(True)
        self._log.document().setDefaultStyleSheet(
            "body{background:#230000;color:#ffecec;font-family:'Cascadia Code',Consolas,monospace;font-size:10pt;}"
            ".stdout{color:#f5dada;}"
            ".stderr{color:#ff6b6b;font-weight:600;}"
            ".status{color:#ffb347;font-style:italic;}"
            ".meta{color:#ff9292;}"
        )
        self._log.setStyleSheet(
            "QTextBrowser{background:#230000;color:#ffecec;border:1px solid #5c1010;border-radius:10px;padding:8px;}"
        )
        root.addWidget(self._log, 1)

        self._btn_start.clicked.connect(self.start)
        self._btn_stop.clicked.connect(self.stop)

    # ------------------------------------------------------------------
    @property
    def is_running(self) -> bool:
        """Return True if the subprocess is currently running."""

        return self._running

    # ------------------------------------------------------------------
    @Slot()
    def start(self) -> None:
        """Start the configured subprocess."""

        if self._proc and self._proc.poll() is None:
            return
        if not self._cmd:
            self._set_status.emit("No command configured.", True)
            return
        if self._guard:
            allowed, detail = self._guard(self._cmd, self._cwd, self._allow_external_exec)
            if not allowed:
                message = detail or "Command blocked."
                self._set_status.emit(message, True)
                if self._violation_cb:
                    try:
                        self._violation_cb(message)
                    except Exception:
                        pass
                return
        try:
            self._append_entry.emit("meta", f"Launching: {' '.join(self._cmd)}")
            self._proc = subprocess.Popen(
                self._cmd,
                cwd=self._cwd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
            )
        except Exception as exc:  # pragma: no cover - launch guards
            reason = f"Launch failed: {exc}"
            self._set_status.emit(reason, True)
            self._record_failure(reason, exit_code=None)
            self.isolation_requested.emit(reason, None)
            return

        self._running = True
        self._kill.clear()
        self._terminated_by_user = False
        self._stderr_lines.clear()
        self._set_buttons.emit(False, True)
        self._set_status.emit("Process started.", False)

        if self._proc.stdout:
            self._stdout_thread = threading.Thread(
                target=self._stream_reader,
                args=(self._proc.stdout, "stdout"),
                daemon=True,
            )
            self._stdout_thread.start()
        if self._proc.stderr:
            self._stderr_thread = threading.Thread(
                target=self._stream_reader,
                args=(self._proc.stderr, "stderr"),
                daemon=True,
            )
            self._stderr_thread.start()
        self._wait_thread = threading.Thread(target=self._await_exit, daemon=True)
        self._wait_thread.start()

    # ------------------------------------------------------------------
    @Slot()
    def stop(self) -> None:
        """Terminate the running subprocess if any."""

        if not self._proc or self._proc.poll() is not None:
            return
        self._terminated_by_user = True
        self._kill.set()
        try:
            self._proc.terminate()
        except Exception:
            pass
        self._set_status.emit("Termination requested.", False)

    # ------------------------------------------------------------------
    def _stream_reader(self, pipe: Iterable[str], channel: str) -> None:
        for raw in pipe:
            if self._kill.is_set():
                break
            text = raw.rstrip("\n")
            if channel == "stderr":
                with self._stderr_lock:
                    self._stderr_lines.append(text)
            self._append_entry.emit(channel, text)

    # ------------------------------------------------------------------
    def _await_exit(self) -> None:
        assert self._proc is not None
        code = self._proc.wait()
        self._running = False
        self._kill.set()
        if self._stdout_thread:
            self._stdout_thread.join(timeout=0.5)
        if self._stderr_thread:
            self._stderr_thread.join(timeout=0.5)
        self._proc = None
        self._set_buttons.emit(True, False)

        if self._terminated_by_user:
            self._set_status.emit("Process terminated by user.", False)
            return
        if code == 0:
            self._set_status.emit("Process completed successfully.", False)
            return

        reason = self._summarise_failure(code)
        self._set_status.emit(reason, True)
        self._record_failure(reason, exit_code=code)
        self.isolation_requested.emit(reason, code)
        QTimer.singleShot(0, lambda: self.close_requested.emit())

    # ------------------------------------------------------------------
    def _summarise_failure(self, code: int) -> str:
        with self._stderr_lock:
            tail = [line for line in self._stderr_lines if line]
        detail = tail[-1] if tail else "no stderr output"
        return f"Process failed (code {code}): {detail}"

    # ------------------------------------------------------------------
    def _record_failure(self, message: str, *, exit_code: Optional[int]) -> None:
        record = ErrorRecord(
            ts=time.time(),
            level="ERROR",
            kind="Runtime",
            msg=f"{message} — cmd={' '.join(self._cmd)}",
            path=self._cmd[0] if self._cmd else None,
            task_id=None,
        )
        try:
            self._record_writer(record)
        except Exception:
            pass

    # ------------------------------------------------------------------
    @Slot(str, str)
    def _handle_append(self, channel: str, text: str) -> None:
        escaped = html.escape(text)
        self._log.append(f"<div class='{channel}'>{escaped}</div>")
        cursor = self._log.textCursor()
        cursor.movePosition(cursor.End)
        self._log.setTextCursor(cursor)

    # ------------------------------------------------------------------
    @Slot(str, bool)
    def _handle_status(self, text: str, is_error: bool) -> None:
        self._status_label.setText(text)
        self._append_entry.emit("status" if is_error else "meta", text)

    # ------------------------------------------------------------------
    @Slot(bool, bool)
    def _handle_buttons(self, start_enabled: bool, stop_enabled: bool) -> None:
        self._btn_start.setEnabled(start_enabled)
        self._btn_stop.setEnabled(stop_enabled)

