"""Windows-only helpers for embedding external GUI processes."""

from __future__ import annotations

import logging
import os
import shlex
import sys
import time
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence, Set, Tuple

from PySide6.QtWidgets import QWidget  # common base for typing


def _load_embed_timeout(default: float = 30.0) -> float:
    """Return the configured embed timeout in seconds."""

    value = os.getenv("CODEX_EXTERNAL_APP_EMBED_TIMEOUT")
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed


EXTERNAL_APP_EMBED_TIMEOUT_SECONDS = _load_embed_timeout()


@dataclass
class LaunchSpec:
    """Normalized launch configuration for an external process."""

    argv: List[str]
    cwd: str
    target_path: str
    original_path: str


if sys.platform.startswith("win"):
    import ctypes
    from ctypes import wintypes

    from PySide6.QtCore import Qt, QEvent, QPoint, QProcess, QTimer, Signal
    from PySide6.QtGui import QWindow
    from PySide6.QtWidgets import QLabel, QVBoxLayout

    _user32 = ctypes.windll.user32  # type: ignore[attr-defined]
    _ole32 = ctypes.windll.ole32  # type: ignore[attr-defined]
    _shell32 = ctypes.windll.shell32  # type: ignore[attr-defined]
    _shlwapi = ctypes.windll.shlwapi  # type: ignore[attr-defined]
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]

    _EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    _user32.EnumWindows.argtypes = [_EnumWindowsProc, wintypes.LPARAM]
    _user32.EnumWindows.restype = wintypes.BOOL
    _user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    _user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    _user32.IsWindowVisible.argtypes = [wintypes.HWND]
    _user32.IsWindowVisible.restype = wintypes.BOOL
    _user32.IsWindow.argtypes = [wintypes.HWND]
    _user32.IsWindow.restype = wintypes.BOOL
    _user32.GetWindow.argtypes = [wintypes.HWND, ctypes.c_uint]
    _user32.GetWindow.restype = wintypes.HWND
    _user32.GetParent.argtypes = [wintypes.HWND]
    _user32.GetParent.restype = wintypes.HWND
    _user32.SetParent.argtypes = [wintypes.HWND, wintypes.HWND]
    _user32.SetParent.restype = wintypes.HWND
    _user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    _user32.GetWindowLongW.restype = ctypes.c_long
    _user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
    _user32.SetWindowLongW.restype = ctypes.c_long
    _user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    _user32.SetWindowPos.restype = wintypes.BOOL
    _user32.ScreenToClient.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    _user32.ScreenToClient.restype = wintypes.BOOL
    _user32.SetFocus.argtypes = [wintypes.HWND]
    _user32.SetFocus.restype = wintypes.HWND
    _user32.SetActiveWindow.argtypes = [wintypes.HWND]
    _user32.SetActiveWindow.restype = wintypes.HWND
    _user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    _user32.ShowWindow.restype = wintypes.BOOL
    _user32.UpdateWindow.argtypes = [wintypes.HWND]
    _user32.UpdateWindow.restype = wintypes.BOOL

    _kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    _kernel32.OpenProcess.restype = wintypes.HANDLE
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.CloseHandle.restype = wintypes.BOOL
    _kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    _kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    _kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    _kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    _kernel32.TerminateProcess.restype = wintypes.BOOL
    _kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    _kernel32.WaitForSingleObject.restype = wintypes.DWORD

    _GW_OWNER = 4
    _GWL_STYLE = -16
    _WS_CHILD = 0x40000000
    _WS_POPUP = 0x80000000
    _WS_CAPTION = 0x00C00000
    _WS_THICKFRAME = 0x00040000
    _WS_MINIMIZEBOX = 0x00020000
    _WS_MAXIMIZEBOX = 0x00010000
    _SWP_NOSIZE = 0x0001
    _SWP_NOZORDER = 0x0004
    _SWP_NOACTIVATE = 0x0010
    _SWP_FRAMECHANGED = 0x0020
    _SWP_SHOWWINDOW = 0x0040
    _SWP_ASYNCWINDOWPOS = 0x4000
    _SW_SHOW = 5
    _COINIT_APARTMENTTHREADED = 0x2
    _CLSCTX_INPROC_SERVER = 0x1
    _PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    _PROCESS_TERMINATE = 0x0001
    _SYNCHRONIZE = 0x00100000
    _ERROR_INSUFFICIENT_BUFFER = 122
    _TH32CS_SNAPPROCESS = 0x00000002
    _INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
    _WAIT_TIMEOUT = 0x00000102

    HRESULT = ctypes.c_long
    ULONG = ctypes.c_ulong
    LPVOID = ctypes.c_void_p
    LPCOLESTR = wintypes.LPCWSTR
    LPWSTR = wintypes.LPWSTR

    class _GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", ctypes.c_ubyte * 8),
        ]


    def _guid(value: str) -> _GUID:
        guid = _GUID()
        if _ole32.CLSIDFromString(ctypes.c_wchar_p(value), ctypes.byref(guid)) != 0:  # type: ignore[arg-type]
            raise OSError(f"CLSIDFromString failed for {value}")
        return guid


    class _IShellLinkW(ctypes.Structure):
        pass


    class _IShellLinkWVTbl(ctypes.Structure):
        _fields_ = [
            ("QueryInterface", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), ctypes.POINTER(_GUID), ctypes.POINTER(LPVOID))),
            ("AddRef", ctypes.WINFUNCTYPE(ULONG, ctypes.POINTER(_IShellLinkW))),
            ("Release", ctypes.WINFUNCTYPE(ULONG, ctypes.POINTER(_IShellLinkW))),
            ("GetPath", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), LPWSTR, ctypes.c_int, ctypes.POINTER(wintypes.WIN32_FIND_DATAW), wintypes.DWORD)),
            ("GetIDList", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), ctypes.POINTER(LPVOID))),
            ("SetIDList", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), LPVOID)),
            ("GetDescription", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), LPWSTR, ctypes.c_int)),
            ("SetDescription", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), wintypes.LPCWSTR)),
            ("GetWorkingDirectory", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), LPWSTR, ctypes.c_int)),
            ("SetWorkingDirectory", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), wintypes.LPCWSTR)),
            ("GetArguments", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), LPWSTR, ctypes.c_int)),
            ("SetArguments", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), wintypes.LPCWSTR)),
            ("GetHotkey", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), ctypes.POINTER(wintypes.WORD))),
            ("SetHotkey", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), wintypes.WORD)),
            ("GetShowCmd", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), ctypes.POINTER(ctypes.c_int))),
            ("SetShowCmd", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), ctypes.c_int)),
            ("GetIconLocation", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), LPWSTR, ctypes.c_int, ctypes.POINTER(ctypes.c_int))),
            ("SetIconLocation", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), wintypes.LPCWSTR, ctypes.c_int)),
            ("SetRelativePath", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), wintypes.LPCWSTR, wintypes.DWORD)),
            ("Resolve", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), wintypes.HWND, wintypes.DWORD)),
            ("SetPath", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IShellLinkW), wintypes.LPCWSTR)),
        ]


    _IShellLinkW._fields_ = [("lpVtbl", ctypes.POINTER(_IShellLinkWVTbl))]


    class _IPersistFile(ctypes.Structure):
        pass


    class _IPersistFileVTbl(ctypes.Structure):
        _fields_ = [
            ("QueryInterface", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IPersistFile), ctypes.POINTER(_GUID), ctypes.POINTER(LPVOID))),
            ("AddRef", ctypes.WINFUNCTYPE(ULONG, ctypes.POINTER(_IPersistFile))),
            ("Release", ctypes.WINFUNCTYPE(ULONG, ctypes.POINTER(_IPersistFile))),
            ("GetClassID", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IPersistFile), ctypes.POINTER(_GUID))),
            ("IsDirty", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IPersistFile))),
            ("Load", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IPersistFile), LPCOLESTR, wintypes.DWORD)),
            ("Save", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IPersistFile), LPCOLESTR, ctypes.c_int)),
            ("SaveCompleted", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IPersistFile), LPCOLESTR)),
            ("GetCurFile", ctypes.WINFUNCTYPE(HRESULT, ctypes.POINTER(_IPersistFile), ctypes.POINTER(LPCOLESTR))),
        ]


    _IPersistFile._fields_ = [("lpVtbl", ctypes.POINTER(_IPersistFileVTbl))]

    class _PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_void_p),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    _kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)]
    _kernel32.Process32FirstW.restype = wintypes.BOOL
    _kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)]
    _kernel32.Process32NextW.restype = wintypes.BOOL

    _shell32.FindExecutableW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPWSTR]
    _shell32.FindExecutableW.restype = wintypes.HINSTANCE

    _shlwapi.AssocQueryStringW.argtypes = [
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    _shlwapi.AssocQueryStringW.restype = HRESULT

    _ASSOCF_NONE = 0x00000000
    _ASSOCSTR_EXECUTABLE = 2

    _CLSID_SHELL_LINK = _guid("{00021401-0000-0000-C000-000000000046}")
    _IID_ISHELL_LINK = _guid("{000214F9-0000-0000-C000-000000000046}")
    _IID_IPERSIST_FILE = _guid("{0000010b-0000-0000-C000-000000000046}")


    def _resolve_associated_executable(path: str) -> Optional[str]:
        if not path:
            return None

        normalized = os.path.abspath(path)

        try:
            buffer = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            result = _shell32.FindExecutableW(normalized, None, buffer)
        except OSError:
            result = 0

        if result > 32:
            candidate = buffer.value.strip().strip('"')
            if candidate and os.path.isfile(candidate):
                return os.path.abspath(candidate)

        _, ext = os.path.splitext(normalized)
        if not ext:
            return None

        length = wintypes.DWORD(0)
        hr = _shlwapi.AssocQueryStringW(
            _ASSOCF_NONE,
            _ASSOCSTR_EXECUTABLE,
            ext,
            None,
            None,
            ctypes.byref(length),
        )

        if hr not in (0, 1) or length.value == 0:
            return None

        buffer = ctypes.create_unicode_buffer(length.value)
        hr = _shlwapi.AssocQueryStringW(
            _ASSOCF_NONE,
            _ASSOCSTR_EXECUTABLE,
            ext,
            None,
            buffer,
            ctypes.byref(length),
        )
        if hr != 0:
            return None

        candidate = buffer.value.strip().strip('"')
        if candidate and os.path.isfile(candidate):
            return os.path.abspath(candidate)

        return None


    def _enum_top_level_windows() -> List[int]:
        handles: List[int] = []

        @_EnumWindowsProc
        def _callback(hwnd: wintypes.HWND, _lparam: wintypes.LPARAM) -> wintypes.BOOL:
            if not _user32.IsWindowVisible(hwnd):
                return True
            if _user32.GetWindow(hwnd, _GW_OWNER):
                return True
            if _user32.GetParent(hwnd):
                return True
            handles.append(int(hwnd))
            return True

        _user32.EnumWindows(_callback, 0)
        return handles


    def _enum_windows_for_pid(pid: int) -> List[int]:
        handles: List[int] = []

        @_EnumWindowsProc
        def _callback(hwnd: wintypes.HWND, _lparam: wintypes.LPARAM) -> wintypes.BOOL:
            proc_id = wintypes.DWORD()
            _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(proc_id))
            if proc_id.value != pid:
                return True
            if not _user32.IsWindowVisible(hwnd):
                return True
            if _user32.GetWindow(hwnd, _GW_OWNER):
                return True
            if _user32.GetParent(hwnd):
                return True
            handles.append(int(hwnd))
            return False

        _user32.EnumWindows(_callback, 0)
        return handles


    def _enum_descendant_processes(root_pid: int) -> Set[int]:
        descendants: Set[int] = set()
        if root_pid <= 0:
            return descendants

        snapshot = _kernel32.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
        handle_value = getattr(snapshot, "value", snapshot)
        if not snapshot or int(handle_value) == int(_INVALID_HANDLE_VALUE):
            return descendants

        parent_map: Dict[int, List[int]] = {}
        try:
            entry = _PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(_PROCESSENTRY32W)
            if not _kernel32.Process32FirstW(snapshot, ctypes.byref(entry)):
                return descendants
            while True:
                pid = int(entry.th32ProcessID)
                parent = int(entry.th32ParentProcessID)
                if pid > 0 and pid != root_pid:
                    parent_map.setdefault(parent, []).append(pid)
                if not _kernel32.Process32NextW(snapshot, ctypes.byref(entry)):
                    break
        finally:
            _kernel32.CloseHandle(snapshot)

        queue: List[int] = [root_pid]
        while queue:
            current = queue.pop()
            for child in parent_map.get(current, []):
                if child not in descendants:
                    descendants.add(child)
                    queue.append(child)
        return descendants


    def _query_process_image_path(pid: int) -> Optional[str]:
        if pid <= 0:
            return None
        process = _kernel32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not process:
            return None
        try:
            size = wintypes.DWORD(260)
            while size.value <= 32768:
                buffer = ctypes.create_unicode_buffer(size.value)
                required = wintypes.DWORD(size.value)
                ctypes.set_last_error(0)
                success = _kernel32.QueryFullProcessImageNameW(process, 0, buffer, ctypes.byref(required))
                if success:
                    return buffer.value.strip()
                error = ctypes.get_last_error()
                if error != _ERROR_INSUFFICIENT_BUFFER:
                    return None
                if required.value > size.value:
                    size = wintypes.DWORD(required.value + 1)
                else:
                    size = wintypes.DWORD(size.value * 2)
            return None
        finally:
            _kernel32.CloseHandle(process)


    def _find_window_for_executables(paths: Iterable[str], ignored: Set[int]) -> Optional[Tuple[int, int]]:
        normalized: Set[str] = set()
        for path in paths:
            if not path:
                continue
            try:
                normalized.add(os.path.normcase(os.path.abspath(path)))
            except Exception:
                continue
        if not normalized:
            return None

        for hwnd in _enum_top_level_windows():
            if hwnd in ignored:
                continue
            proc_id = wintypes.DWORD()
            _user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(proc_id))
            pid = int(proc_id.value)
            if pid <= 0:
                continue
            image = _query_process_image_path(pid)
            if not image:
                continue
            try:
                image_norm = os.path.normcase(os.path.abspath(image))
            except Exception:
                continue
            if image_norm in normalized:
                return hwnd, pid

        return None


    def _find_main_hwnd(pid: int) -> Optional[int]:
        handles = _enum_windows_for_pid(pid)
        return handles[0] if handles else None


    def _pe_is_gui_subsystem(path: str) -> Optional[bool]:
        try:
            with open(path, "rb") as fh:
                header = fh.read(64)
                if len(header) < 64 or header[:2] != b"MZ":
                    return None
                pe_offset = int.from_bytes(header[60:64], "little")
                fh.seek(pe_offset)
                if fh.read(4) != b"PE\0\0":
                    return None
                fh.seek(pe_offset + 24)
                optional = fh.read(0x60)
                if len(optional) < 0x46:
                    return None
                subsystem = int.from_bytes(optional[0x44:0x46], "little")
                if subsystem == 2:
                    return True
                if subsystem == 3:
                    return False
                return None
        except Exception:
            return None


    def _resolve_windows_shortcut(path: str) -> Optional[tuple[str, List[str], Optional[str]]]:
        if not path.lower().endswith(".lnk"):
            return None
        if not os.path.exists(path):
            return None
        hr = _ole32.CoInitializeEx(None, _COINIT_APARTMENTTHREADED)
        uninit = hr in (0, 1)
        try:
            shell_link_ptr = ctypes.c_void_p()
            result = _ole32.CoCreateInstance(
                ctypes.byref(_CLSID_SHELL_LINK),
                None,
                _CLSCTX_INPROC_SERVER,
                ctypes.byref(_IID_ISHELL_LINK),
                ctypes.byref(shell_link_ptr),
            )
            if result != 0 or not shell_link_ptr:
                return None
            shell_link = ctypes.cast(shell_link_ptr, ctypes.POINTER(_IShellLinkW))
            persist_ptr = ctypes.c_void_p()
            if shell_link.contents.lpVtbl.contents.QueryInterface(shell_link, ctypes.byref(_IID_IPERSIST_FILE), ctypes.byref(persist_ptr)) != 0:
                shell_link.contents.lpVtbl.contents.Release(shell_link)
                return None
            persist = ctypes.cast(persist_ptr, ctypes.POINTER(_IPersistFile))
            if persist.contents.lpVtbl.contents.Load(persist, ctypes.c_wchar_p(path), 0) != 0:
                persist.contents.lpVtbl.contents.Release(persist)
                shell_link.contents.lpVtbl.contents.Release(shell_link)
                return None
            buffer = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            find_data = wintypes.WIN32_FIND_DATAW()
            if shell_link.contents.lpVtbl.contents.GetPath(shell_link, buffer, len(buffer), ctypes.byref(find_data), 0) != 0:
                persist.contents.lpVtbl.contents.Release(persist)
                shell_link.contents.lpVtbl.contents.Release(shell_link)
                return None
            target = buffer.value
            args_buf = ctypes.create_unicode_buffer(1024)
            shell_link.contents.lpVtbl.contents.GetArguments(shell_link, args_buf, len(args_buf))
            cwd_buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            shell_link.contents.lpVtbl.contents.GetWorkingDirectory(shell_link, cwd_buf, len(cwd_buf))
            persist.contents.lpVtbl.contents.Release(persist)
            shell_link.contents.lpVtbl.contents.Release(shell_link)
            args = args_buf.value.strip()
            working_dir = cwd_buf.value.strip() or None
            arg_list = shlex.split(args, posix=False) if args else []
            return target, arg_list, working_dir
        except Exception:
            return None
        finally:
            if uninit:
                try:
                    _ole32.CoUninitialize()
                except Exception:
                    pass


    class ExternalAppCard(QWidget):  # pragma: no cover - Windows-specific widget
        request_close = Signal()
        process_finished = Signal(int, str)
        fallback_requested = Signal(str)

        def __init__(
            self,
            theme,
            spec: LaunchSpec,
            *,
            toast_cb: Optional[Callable[[str, str], None]] = None,
            log_cb: Optional[Callable[[str, int], None]] = None,
            embed_timeout: Optional[float] = None,
        ) -> None:
            super().__init__()
            self._theme = theme
            self._spec = spec
            self._toast_cb = toast_cb
            self._log_cb = log_cb
            self._process = QProcess(self)
            if spec.argv:
                self._process.setProgram(spec.argv[0])
                self._process.setArguments(spec.argv[1:])
            self._process.setWorkingDirectory(spec.cwd)
            self._process.finished.connect(self._on_finished)
            self._process.errorOccurred.connect(self._on_error)
            self._poll_timer = QTimer(self)
            self._poll_timer.setInterval(200)
            self._poll_timer.timeout.connect(self._poll_for_window)
            self._watchdog = QTimer(self)
            self._watchdog.setInterval(1000)
            self._watchdog.timeout.connect(self._check_window_alive)
            if embed_timeout is None:
                embed_timeout = EXTERNAL_APP_EMBED_TIMEOUT_SECONDS
            try:
                self._embed_timeout = float(embed_timeout)
            except (TypeError, ValueError):
                self._embed_timeout = float(EXTERNAL_APP_EMBED_TIMEOUT_SECONDS)
            self._embed_deadline = 0.0
            self._embedded_hwnd: int = 0
            self._original_parent: int = 0
            self._original_style: int = 0
            self._container: Optional[QWidget] = None
            self._embedded_window: Optional[QWindow] = None
            self._fallback_emitted = False
            self._suppress_finished = False
            self._card = None
            self._preexisting_windows: Set[int] = set(_enum_top_level_windows())
            self._discovered_executables: Set[str] = set()
            self._launcher_directories: Set[str] = self._compute_launcher_directories()
            self._candidate_executables: Set[str] = self._normalize_executable_candidates()
            self._tracked_pid: Optional[int] = None
            self._pending_exit_detail: Optional[Tuple[int, str]] = None
            self._window_released = True
            self._last_embedded_size: Optional[Tuple[int, int]] = None
            self._last_embedded_origin: Optional[Tuple[int, int]] = None
            self._last_position_sync_ts = 0.0
            self._position_sync_interval = 0.05

            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self._placeholder = QLabel("Launching…", self)
            self._placeholder.setAlignment(Qt.AlignCenter)
            self._placeholder.setStyleSheet(
                f"color:{getattr(theme, 'header_fg', '#eaf2ff')};font:600 10pt 'Cascadia Code';padding:24px;"
            )
            layout.addWidget(self._placeholder, 1)
            self.setFocusPolicy(Qt.StrongFocus)

        # ------------------------------------------------------------------
        def attach_card(self, card: QWidget) -> None:
            self._card = card
            connections = {
                "resized": self._sync_geometry,
                "moved": self._sync_geometry,
                "restored": self._sync_geometry,
                "moving": self._sync_embedded_position,
            }
            for signal_name, handler in connections.items():
                if not hasattr(card, signal_name):
                    continue
                try:
                    getattr(card, signal_name).connect(handler)
                except Exception:
                    continue

        # ------------------------------------------------------------------
        def start(self) -> bool:
            if not self._spec.argv:
                self._emit_fallback("No command specified.")
                return False
            try:
                program = self._spec.argv[0]
                args = self._spec.argv[1:]
                self._log(f"[external-app] Launching: {program} {' '.join(args)}")
                self._process.start(program, args)
            except Exception as exc:  # pragma: no cover - Qt start errors
                self._emit_fallback(f"Launch failed: {exc}")
                return False
            if not self._process.waitForStarted(5000):
                reason = self._process.errorString() or "Launch failed."
                self._emit_fallback(reason)
                return False
            if self._embed_timeout and self._embed_timeout > 0:
                self._embed_deadline = time.monotonic() + float(self._embed_timeout)
            else:
                self._embed_deadline = 0.0
            self._poll_timer.start()
            return True

        # ------------------------------------------------------------------
        def shutdown(self) -> None:
            self._poll_timer.stop()
            self._watchdog.stop()
            if self._process.state() == QProcess.NotRunning:
                self._force_terminate_tracked_process()
                self._release_window()
                return
            self._process.terminate()
            if self._process.waitForFinished(1500):
                self._release_window()
                return
            self._process.kill()
            if self._process.waitForFinished(1500) or self._process.state() == QProcess.NotRunning:
                self._release_window()

        # ------------------------------------------------------------------
        def _force_terminate_tracked_process(self) -> None:
            pid = self._tracked_pid
            if not pid or pid <= 0:
                self._tracked_pid = None
                return

            try:
                descendants = _enum_descendant_processes(pid)
            except Exception:
                descendants = set()

            targets = [child for child in descendants if child > 0]
            targets.sort(reverse=True)
            successes: List[int] = []
            failures: List[int] = []

            for target in targets:
                if self._terminate_process(target):
                    successes.append(target)
                else:
                    failures.append(target)

            if self._terminate_process(pid):
                successes.append(pid)
            else:
                failures.append(pid)

            self._tracked_pid = None

            if not successes and not failures:
                return

            detail_parts = [
                f"Forced termination for orphaned external app PID {pid}.",
            ]
            if successes:
                detail_parts.append(
                    "Terminated: " + ", ".join(str(value) for value in successes)
                )
            if failures:
                detail_parts.append(
                    "Failed: " + ", ".join(str(value) for value in failures)
                )
            level = logging.WARNING if not failures else logging.ERROR
            self._log("[external-app] " + " ".join(detail_parts), level)

            if callable(self._toast_cb):
                toast_message = "Force closed external app after launcher exit."
                toast_kind = "warning"
                if failures:
                    toast_message = (
                        "Unable to fully close external app after launcher exit."
                    )
                    toast_kind = "error"
                try:
                    self._toast_cb(toast_message, kind=toast_kind)
                except TypeError:
                    self._toast_cb(toast_message)  # type: ignore[misc]

        # ------------------------------------------------------------------
        def _terminate_process(self, pid: int) -> bool:
            if pid <= 0:
                return False

            desired_access = _PROCESS_TERMINATE | _SYNCHRONIZE
            try:
                handle = _kernel32.OpenProcess(desired_access, False, pid)
            except Exception:
                handle = None
            if not handle:
                return False

            try:
                try:
                    if not _kernel32.TerminateProcess(handle, 1):
                        return False
                except Exception:
                    return False
                try:
                    result = _kernel32.WaitForSingleObject(handle, 2000)
                except Exception:
                    result = None
                if result == _WAIT_TIMEOUT:
                    return False
                return True
            finally:
                try:
                    _kernel32.CloseHandle(handle)
                except Exception:
                    pass

        # ------------------------------------------------------------------
        def _emit_fallback(self, message: str) -> None:
            if self._fallback_emitted:
                return
            self._fallback_emitted = True
            self._suppress_finished = True
            self._pending_exit_detail = None
            self.shutdown()
            if callable(self._toast_cb):
                try:
                    self._toast_cb(message, kind="error")
                except TypeError:
                    self._toast_cb(message)  # type: ignore[misc]
            self.fallback_requested.emit(message)

        # ------------------------------------------------------------------
        def _compute_launcher_directories(self) -> Set[str]:
            directories: Set[str] = set()
            entries: List[str] = []
            if self._spec.argv:
                entries.append(self._spec.argv[0])
            if self._spec.target_path:
                entries.append(self._spec.target_path)
            base = self._spec.cwd or os.getcwd()
            for entry in entries:
                if not entry:
                    continue
                try:
                    path = entry
                    if not os.path.isabs(path):
                        path = os.path.join(base, path)
                    normalized = os.path.normcase(os.path.abspath(path))
                except Exception:
                    continue
                directory = os.path.dirname(normalized)
                if directory:
                    directories.add(directory)
            return directories

        # ------------------------------------------------------------------
        def _merge_discovered_executables(self, paths: Iterable[str]) -> None:
            added = False
            for path in paths:
                if not path:
                    continue
                try:
                    normalized = os.path.normcase(os.path.abspath(path))
                except Exception:
                    continue
                if normalized not in self._discovered_executables:
                    self._discovered_executables.add(normalized)
                    added = True
            if added:
                self._candidate_executables = self._normalize_executable_candidates()

        # ------------------------------------------------------------------
        def _normalize_executable_candidates(self) -> Set[str]:
            candidates: Set[str] = set()
            entries: List[str] = []
            if self._spec.argv:
                entries.append(self._spec.argv[0])
            if self._spec.target_path:
                entries.append(self._spec.target_path)
            entries.extend(self._discovered_executables)
            base = self._spec.cwd or os.getcwd()
            for entry in entries:
                if not entry:
                    continue
                try:
                    path = entry
                    if not os.path.isabs(path):
                        path = os.path.join(base, path)
                    candidates.add(os.path.normcase(os.path.abspath(path)))
                except Exception:
                    continue
            return candidates

        # ------------------------------------------------------------------
        def _poll_for_window(self) -> None:
            if self._embedded_hwnd or self._fallback_emitted:
                self._poll_timer.stop()
                return

            pid = int(self._process.processId())
            hwnd = 0
            if pid > 0:
                hwnd = _find_main_hwnd(pid)
            if hwnd:
                self._log(f"[external-app] Found HWND=0x{hwnd:x} for PID {pid}")
                self._embed_window(hwnd, owner_pid=pid)
                self._poll_timer.stop()
                self._watchdog.start()
                return
            fallback = self._locate_adoptable_window()
            if fallback:
                adopt_hwnd, adopt_pid = fallback
                self._log(
                    f"[external-app] Adopted HWND=0x{adopt_hwnd:x} from PID {adopt_pid} via executable scan"
                )
                self._embed_window(adopt_hwnd, owner_pid=adopt_pid)
                self._poll_timer.stop()
                self._watchdog.start()
                return
            if self._embed_deadline and time.monotonic() > self._embed_deadline:
                self._log(
                    f"[external-app] No window detected for PID {pid}; falling back.",
                    logging.WARNING,
                )
                self._emit_fallback("No window detected; falling back to console view.")

        # ------------------------------------------------------------------
        def _locate_adoptable_window(self) -> Optional[Tuple[int, int]]:
            if not self._candidate_executables:
                return None

            match = _find_window_for_executables(self._candidate_executables, self._preexisting_windows)
            if match:
                return match

            pid = int(self._process.processId()) if self._process else 0
            descendant_pids: Set[int] = set()
            descendant_paths: Set[str] = set()
            if pid > 0:
                try:
                    descendant_pids = _enum_descendant_processes(pid)
                except Exception:
                    descendant_pids = set()
                if descendant_pids:
                    for child_pid in descendant_pids:
                        image = _query_process_image_path(child_pid)
                        if image:
                            descendant_paths.add(image)
            if descendant_paths:
                self._merge_discovered_executables(descendant_paths)

            launcher_dirs = self._launcher_directories
            candidate: Optional[Tuple[int, int]] = None
            candidate_reason = ""
            new_executables: Set[str] = set()

            for hwnd in _enum_top_level_windows():
                if hwnd in self._preexisting_windows or hwnd == self._embedded_hwnd:
                    continue
                proc_id = self._window_pid(hwnd)
                if not proc_id or proc_id <= 0 or proc_id == pid:
                    continue
                image = _query_process_image_path(proc_id)
                if not image:
                    continue
                try:
                    image_norm = os.path.normcase(os.path.abspath(image))
                    image_dir = os.path.dirname(image_norm)
                except Exception:
                    continue

                reason = ""
                if proc_id in descendant_pids:
                    reason = "descendant"
                elif launcher_dirs and image_dir in launcher_dirs:
                    reason = "directory"
                if not reason:
                    continue

                new_executables.add(image_norm)
                current = (hwnd, proc_id)
                if reason == "descendant":
                    candidate = current
                    candidate_reason = reason
                    break
                if candidate is None:
                    candidate = current
                    candidate_reason = reason

            if new_executables:
                self._merge_discovered_executables(new_executables)

            if candidate:
                if candidate_reason == "descendant":
                    return candidate
                if candidate_reason == "directory":
                    return candidate
            return None

        # ------------------------------------------------------------------
        def _embed_window(self, hwnd: int, *, owner_pid: Optional[int] = None) -> None:
            if self._embedded_hwnd:
                return
            self._window_released = False
            self._embedded_hwnd = hwnd
            if owner_pid is None:
                owner_pid = self._window_pid(hwnd)
            self._tracked_pid = int(owner_pid) if owner_pid else None
            self._preexisting_windows.add(hwnd)
            try:
                self._original_parent = int(_user32.GetParent(hwnd) or 0)
            except Exception:
                self._original_parent = 0
            try:
                self._original_style = int(_user32.GetWindowLongW(hwnd, _GWL_STYLE))
            except Exception:
                self._original_style = 0
            window = QWindow.fromWinId(int(hwnd))
            window.setFlag(Qt.FramelessWindowHint, True)
            container = QWidget.createWindowContainer(window, self)
            self._last_embedded_size = None
            self._last_embedded_origin = None
            self._last_position_sync_ts = 0.0
            container.setFocusPolicy(Qt.StrongFocus)
            container.setMinimumSize(240, 180)
            container.installEventFilter(self)
            layout = self.layout()
            if isinstance(layout, QVBoxLayout):
                if self._placeholder:
                    layout.removeWidget(self._placeholder)
                    self._placeholder.deleteLater()
                    self._placeholder = None
                layout.addWidget(container, 1)
            self._container = container
            self._embedded_window = window
            new_style = (self._original_style | _WS_CHILD) & ~_WS_POPUP & ~_WS_THICKFRAME & ~_WS_CAPTION
            new_style &= ~_WS_MINIMIZEBOX & ~_WS_MAXIMIZEBOX
            try:
                _user32.SetWindowLongW(hwnd, _GWL_STYLE, new_style)
            except Exception:
                pass
            try:
                _user32.SetParent(hwnd, wintypes.HWND(int(container.winId())))
            except Exception:
                pass
            self._sync_geometry()
            try:
                _user32.ShowWindow(hwnd, _SW_SHOW)
            except Exception:
                pass

        # ------------------------------------------------------------------
        def _window_pid(self, hwnd: int) -> Optional[int]:
            proc_id = wintypes.DWORD()
            thread_id = _user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(proc_id))
            if thread_id == 0:
                return None
            value = int(proc_id.value)
            return value if value > 0 else None

        # ------------------------------------------------------------------
        def _release_window(self) -> None:
            if self._window_released:
                return
            self._window_released = True
            hwnd = self._embedded_hwnd
            self._embedded_hwnd = 0
            self._tracked_pid = None
            try:
                if hwnd and self._original_style:
                    _user32.SetWindowLongW(hwnd, _GWL_STYLE, self._original_style)
                if hwnd and self._original_parent:
                    _user32.SetParent(hwnd, wintypes.HWND(self._original_parent))
                if hwnd:
                    _user32.SetWindowPos(
                        hwnd,
                        None,
                        0,
                        0,
                        0,
                        0,
                        _SWP_NOZORDER | _SWP_NOACTIVATE | _SWP_FRAMECHANGED,
                    )
            except Exception:
                pass
            self._original_parent = 0
            self._original_style = 0
            if self._embedded_window:
                try:
                    self._embedded_window.setParent(None)
                except Exception:
                    pass
                self._embedded_window = None
            if self._container:
                self._container.deleteLater()
                self._last_embedded_size = None
                self._last_embedded_origin = None
                self._last_position_sync_ts = 0.0
                self._container = None

        # ------------------------------------------------------------------
        def _sync_geometry(self) -> None:
            if not self._embedded_hwnd or not self._container:
                return
            rect = self._container.rect()
            requested_size = (
                max(1, rect.width()),
                max(1, rect.height()),
            )
            last_size = self._last_embedded_size
            if last_size is not None and requested_size == last_size:
                return
            hwnd = wintypes.HWND(self._embedded_hwnd)
            flags = _SWP_NOZORDER | _SWP_NOACTIVATE | _SWP_FRAMECHANGED
            width, height = requested_size
            try:
                succeeded = bool(
                    _user32.SetWindowPos(
                        hwnd,
                        None,
                        0,
                        0,
                        width,
                        height,
                        flags,
                    )
                )
            except Exception:
                succeeded = False
            if not succeeded:
                self._last_embedded_size = None
                return
            if not (flags & _SWP_ASYNCWINDOWPOS):
                try:
                    _user32.UpdateWindow(hwnd)
                except Exception:
                    pass
                self._last_embedded_size = requested_size
                self._last_embedded_origin = None
                self._last_position_sync_ts = 0.0

        # ------------------------------------------------------------------
        def _sync_embedded_position(self, _pos: QPoint) -> None:
            if not self._embedded_hwnd or not self._container:
                return
            hwnd = wintypes.HWND(self._embedded_hwnd)
            try:
                parent_handle = _user32.GetParent(hwnd)
            except Exception:
                parent_handle = wintypes.HWND(0)
            parent_value = int(parent_handle or 0)
            if not parent_value:
                return
            parent_hwnd = wintypes.HWND(parent_value)
            global_origin = self._container.mapToGlobal(self._container.rect().topLeft())
            point = wintypes.POINT(int(global_origin.x()), int(global_origin.y()))
            try:
                mapped = bool(_user32.ScreenToClient(parent_hwnd, ctypes.byref(point)))
            except Exception:
                return
            if not mapped:
                return
            origin = (int(point.x), int(point.y))
            last_origin = self._last_embedded_origin
            if last_origin is not None and origin == last_origin:
                return
            now = time.monotonic()
            if self._last_position_sync_ts and now - self._last_position_sync_ts < self._position_sync_interval:
                return
            flags = _SWP_NOSIZE | _SWP_NOZORDER | _SWP_NOACTIVATE
            try:
                succeeded = bool(
                    _user32.SetWindowPos(
                        hwnd,
                        None,
                        origin[0],
                        origin[1],
                        0,
                        0,
                        flags,
                    )
                )
            except Exception:
                return
            if not succeeded:
                return
            self._last_embedded_origin = origin
            self._last_position_sync_ts = now
            try:
                _user32.UpdateWindow(hwnd)
            except Exception:
                pass

        # ------------------------------------------------------------------
        def _check_window_alive(self) -> None:
            if not self._embedded_hwnd:
                return
            hwnd_obj = wintypes.HWND(self._embedded_hwnd)
            if not _user32.IsWindow(hwnd_obj):
                self._watchdog.stop()
                self._log("[external-app] Embedded window destroyed.", logging.WARNING)
                self._poll_timer.stop()
                exit_code, detail = (-1, "Window closed unexpectedly.")
                if self._pending_exit_detail:
                    exit_code, detail = self._pending_exit_detail
                    self._log(f"[external-app] {detail}")
                self._pending_exit_detail = None
                self._release_window()
                self.process_finished.emit(exit_code, detail)
                self.request_close.emit()
                return
            if self._tracked_pid:
                current_pid = self._window_pid(self._embedded_hwnd)
                if current_pid is not None and current_pid != self._tracked_pid:
                    self._watchdog.stop()
                    self._log("[external-app] Embedded window ownership changed.", logging.WARNING)
                    self._poll_timer.stop()
                    exit_code, detail = (-1, "Window closed unexpectedly.")
                    if self._pending_exit_detail:
                        exit_code, detail = self._pending_exit_detail
                        self._log(f"[external-app] {detail}")
                    self._pending_exit_detail = None
                    self._release_window()
                    self.process_finished.emit(exit_code, detail)
                    self.request_close.emit()

        # ------------------------------------------------------------------
        def focusInEvent(self, event) -> None:  # type: ignore[override]
            super().focusInEvent(event)
            self._activate_focus()

        # ------------------------------------------------------------------
        def eventFilter(self, obj, event):  # type: ignore[override]
            if obj is self._container:
                etype = event.type()
                if etype == QEvent.FocusIn:
                    self._activate_focus()
                elif etype == QEvent.Resize:
                    self._sync_geometry()
            return super().eventFilter(obj, event)

        # ------------------------------------------------------------------
        def _activate_focus(self) -> None:
            if not self._embedded_hwnd:
                return
            try:
                _user32.SetActiveWindow(wintypes.HWND(self._embedded_hwnd))
                _user32.SetFocus(wintypes.HWND(self._embedded_hwnd))
            except Exception:
                pass

        # ------------------------------------------------------------------
        def _on_finished(self, exit_code: int, status) -> None:
            waiting_for_embed = (
                not self._embedded_hwnd
                and not self._fallback_emitted
                and (not self._embed_deadline or time.monotonic() <= self._embed_deadline)
            )
            detail = "Process exited." if exit_code == 0 else f"Process exited with code {exit_code}."
            if waiting_for_embed:
                self._pending_exit_detail = (exit_code, detail)
                self._log(
                    "[external-app] Process exited before embedding; continuing to poll for adoptable window."
                )
                if not self._poll_timer.isActive():
                    self._poll_timer.start()
                return

            self._poll_timer.stop()
            self._watchdog.stop()
            self._release_window()
            self._pending_exit_detail = None
            if self._suppress_finished:
                self._suppress_finished = False
                return
            self._log(f"[external-app] {detail}")
            self.process_finished.emit(exit_code, detail)
            self.request_close.emit()

        # ------------------------------------------------------------------
        def _on_error(self, _error) -> None:
            if self._fallback_emitted:
                return
            reason = self._process.errorString() or "Process error."
            self._log(f"[external-app] Error: {reason}", logging.ERROR)
            if self._process.state() == QProcess.NotRunning and not self._embedded_hwnd:
                self._emit_fallback(reason)

        # ------------------------------------------------------------------
        def _log(self, message: str, level: int = logging.INFO) -> None:
            if callable(self._log_cb):
                try:
                    self._log_cb(message, level)
                except TypeError:
                    self._log_cb(message)  # type: ignore[misc]

else:  # Non-Windows -----------------------------------------------------------------

    def _pe_is_gui_subsystem(path: str) -> Optional[bool]:  # pragma: no cover - non-Windows stub
        return None

    def _resolve_windows_shortcut(path: str) -> Optional[tuple[str, List[str], Optional[str]]]:  # pragma: no cover
        return None

    def _resolve_associated_executable(path: str) -> Optional[str]:  # pragma: no cover - non-Windows stub
        return None

    class ExternalAppCard(QWidget):  # type: ignore[dead-code]
        def __init__(self, *args, **kwargs):  # pragma: no cover - non-Windows stub
            raise RuntimeError("ExternalAppCard is only available on Windows.")

        def attach_card(self, card: QWidget) -> None:  # pragma: no cover - stub
            raise RuntimeError("ExternalAppCard is only available on Windows.")

        def start(self) -> bool:  # pragma: no cover - stub
            return False

        def shutdown(self) -> None:  # pragma: no cover - stub
            return None


# ----------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------

def build_launch_spec(path: str, script_dir: str) -> LaunchSpec:
    cwd = os.path.dirname(path) or script_dir
    target = path
    argv: List[str] = [path]

    if sys.platform.startswith("win") and path.lower().endswith(".lnk"):
        resolved = _resolve_windows_shortcut(path)
        if resolved:
            resolved_path, resolved_args, resolved_cwd = resolved
            if resolved_path:
                target = resolved_path
                argv = [resolved_path] + resolved_args
                if resolved_cwd:
                    cwd = resolved_cwd
                else:
                    cwd = os.path.dirname(resolved_path) or cwd

    lower_target = target.lower()
    if lower_target.endswith(".py"):
        argv = [sys.executable, target]
        cwd = os.path.dirname(target) or cwd
    elif sys.platform.startswith("win"):
        executable_exts = {".exe", ".scr", ".bat", ".cmd", ".com", ".py"}
        ext = os.path.splitext(lower_target)[1]
        if ext and ext not in executable_exts:
            associated = _resolve_associated_executable(target)
            if associated and os.path.normcase(associated) != os.path.normcase(target):
                target = associated
                argv = [associated, path]
                cwd = os.path.dirname(associated) or cwd

    return LaunchSpec(argv=argv, cwd=cwd, target_path=target, original_path=path)


def should_embed_external_app(spec: LaunchSpec, allowlist: Sequence[str]) -> bool:
    if not sys.platform.startswith("win"):
        return False
    if not spec.target_path:
        return False
    normalized_allowlist = {os.path.abspath(entry).lower() for entry in allowlist if entry}
    normalized = os.path.abspath(spec.target_path).lower()
    if normalized in normalized_allowlist:
        return False
    if spec.argv:
        primary = os.path.abspath(spec.argv[0]).lower()
        if primary in normalized_allowlist:
            return False
    ext = os.path.splitext(normalized)[1]
    if ext in {".bat", ".cmd", ".com", ".py"}:
        return False
    if ext not in {".exe", ".scr"}:
        return False
    subsystem = _pe_is_gui_subsystem(spec.target_path)
    if subsystem is False:
        return False
    if subsystem is True:
        return True
    return ext in {".exe", ".scr"}


__all__ = [
    "EXTERNAL_APP_EMBED_TIMEOUT_SECONDS",
    "ExternalAppCard",
    "LaunchSpec",
    "build_launch_spec",
    "should_embed_external_app",
]
