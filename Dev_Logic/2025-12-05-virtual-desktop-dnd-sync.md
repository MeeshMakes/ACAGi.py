# Virtual Desktop Drag/Drop Synchronization

## Mini Design Doc (2025-12-05)
- **Paths to edit**: `Virtual_Desktop.py`, `Dev_Logic/2025-12-05-virtual-desktop-dnd-sync.md`, `CHANGELOG.md`.
- **Key functions/classes**: `DesktopIcon.mouseMoveEvent`, `DesktopCanvas.begin_icon_drag`, `DesktopCanvas.end_icon_drag`, `DesktopCanvas.dropEvent`.
- **Tests/validations**: `python -m py_compile $(git ls-files '*.py')`, `flake8`, `QT_QPA_PLATFORM=offscreen pytest`, `python tools/manage_tests.py`, `python tools/logic_inbox.py --validate` (best-effort; document missing dependencies if any fail).
- **Dependencies/env**: Requires PySide6 for Qt tests (may be unavailable); flake8 binary might be absent in container.

## Implementation Summary (2025-12-05)
- Desktop icon drags now embed file URLs so host apps can interpret drops correctly and report move/copy semantics.
- `DesktopCanvas` tracks drag origins plus internal drop targets to ensure only external move drops trigger filesystem cleanup.
- Internal folder moves and grid snaps register the originating path as internal drops, preventing accidental deletions.

## Implementation Summary (2025-12-06)
- External file drops inspect the cursor position for folder targets, routing imports into that directory while preserving its selection state.
- `_import_dropped_paths` now accepts an optional destination, ensuring the directory exists and applying `_unique_destination_path` within it for every copy.
- Workspace-local imports register with `_register_internal_drop` to keep cleanup logic from removing freshly copied entries and always trigger an icon refresh.

:::task-stub{title="Synchronize Virtual Desktop icon drag/drop cleanup"}
1. Update `Virtual_Desktop.py` ➜ `DesktopIcon.mouseMoveEvent` to add `mime.setUrls([QUrl.fromLocalFile(path)])`, call `DesktopCanvas.begin_icon_drag(path)` before `drag.exec`, and route the resulting `DropAction` plus `path` into `DesktopCanvas.end_icon_drag`.
2. Extend `DesktopCanvas` in `Virtual_Desktop.py`: initialize `_drag_origin_path` and `_internal_drop_paths`, add `_register_internal_drop`, and ensure `end_icon_drag` deletes the source only when the action is `Qt.MoveAction`, the path resolves inside `VDSK_ROOT`, and it was not registered as an internal drop.
3. Within `DesktopCanvas.dropEvent`, invoke `_register_internal_drop(icon.path)` for folder drops and grid snaps so rearrangements remain internal; refresh selection logic as needed.
4. Document the behavior update in `Dev_Logic/2025-12-05-virtual-desktop-dnd-sync.md` and record a dated summary in `CHANGELOG.md`.
5. Run `python -m py_compile $(git ls-files '*.py')`, `flake8`, `QT_QPA_PLATFORM=offscreen pytest`, `python tools/manage_tests.py`, and `python tools/logic_inbox.py --validate`; capture unmet dependency notes if any command fails.
:::

## Mini Design Doc (2025-12-06)
- **Paths to edit**: `Virtual_Desktop.py`, `Dev_Logic/2025-12-05-virtual-desktop-dnd-sync.md`.
- **Key functions/classes**: `DesktopCanvas.dropEvent`, `DesktopCanvas._import_dropped_paths`.
- **Tests/validations**: `python -m py_compile $(git ls-files '*.py')`, `flake8`, `QT_QPA_PLATFORM=offscreen pytest`, `python tools/manage_tests.py`, `python tools/logic_inbox.py --validate` (best effort; document missing dependencies).
- **Dependencies/env**: PySide6 and flake8 may be unavailable in the container; expect related validation failures.

:::task-stub{title="Route external drops into targeted Virtual Desktop folders"}
1. Modify `Virtual_Desktop.py` ➜ `DesktopCanvas.dropEvent` to detect folder icons beneath the drop cursor, pass the resolved directory into `_import_dropped_paths`, register imported paths as internal drops when the destination resides in `VDSK_ROOT`, refresh icons, and keep the folder selected.
2. Update `DesktopCanvas._import_dropped_paths` in `Virtual_Desktop.py` to accept an optional destination directory (defaulting to `VDSK_ROOT`), ensure that directory exists, and apply `_unique_destination_path` within that destination before copying.
3. Extend `Dev_Logic/2025-12-05-virtual-desktop-dnd-sync.md` with implementation notes summarizing the behavior change once complete.
4. Execute `python -m py_compile $(git ls-files '*.py')`, `flake8`, `QT_QPA_PLATFORM=offscreen pytest`, `python tools/manage_tests.py`, and `python tools/logic_inbox.py --validate`, logging missing dependencies where applicable.
:::

## Behavior Notes
- External move drops rely on Qt reporting `Qt.MoveAction`; copy drops leave the source intact by design.
- `_internal_drop_paths` resets with each drag start, covering multi-step drags without leaking state.
- `_normalize_drop_path` tolerates missing files so cleanup can proceed even after the OS relocates the source before Qt returns.

## Testing
- `python -m py_compile $(git ls-files '*.py')`
- `flake8` _(missing command in container)_
- `QT_QPA_PLATFORM=offscreen pytest` _(fails: PySide6 missing)_
- `python tools/manage_tests.py` _(fails: PySide6 missing)_
- `python tools/logic_inbox.py --validate`

