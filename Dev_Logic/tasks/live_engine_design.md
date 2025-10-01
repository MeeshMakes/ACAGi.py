# Live Script Background Engine Design

## Objective
Implement a reusable OpenGL background viewport for the Virtual Desktop that can execute user scripts with lifecycle hooks, limit rendering to a target framerate, support hot-reloading, and pause rendering when the desktop is minimized or the system is under heavy load.

## Scope & Files
- `background/live_engine.py`: new module implementing the live viewport widget and script controller.
- `background/gl.py`: refactor to use the new engine, expose configuration knobs, and wire pause heuristics.
- `background/__init__.py`: export the new engine if needed by other modules.
- `tests/test_live_engine.py`: unit tests covering the script controller’s loading and reload behavior without requiring an actual OpenGL context.

## Key Components
1. **LiveScriptController** (pure Python)
   - Tracks the script path, loads modules via `importlib.util`, records mtimes, and exposes helpers to call hooks (`init`, `resize`, `update`, `render`).
   - Provides `reload_if_changed()` to hot-reload when the file timestamp updates.
   - Raises descriptive errors while logging failures so the viewport can disable itself gracefully.

2. **LiveScriptViewport** (`QOpenGLWidget` subclass)
   - Owns a `LiveScriptController` instance.
   - Uses a `QTimer` with `Qt.PreciseTimer` to cap rendering FPS (`DEFAULT_FPS = 60`).
   - Keeps monotonic timestamps to compute `dt` for `update` hooks.
   - On each tick, it:
     - Skips work if the widget or window is hidden/minimized.
     - Checks the heavy-process predicate and optional psutil CPU/memory thresholds.
     - Hot-reloads the script if the file changed.
     - Schedules a paint when active and stores `dt` for `paintGL`.
   - Calls the script hooks (`init`, `resize`, `update`, `render`) inside try/except blocks, logging failures without crashing the UI.
   - Exposes setters for FPS cap and heavy-process checker so `GLViewportBg` can adapt behavior.

3. **GLViewportBg integration**
   - Lazily creates a `LiveScriptViewport` and configures it from the background config (fps derived from playback rate, script path, heavy-process callback).
   - Starts/stops the viewport alongside background lifecycle events and resizes it with the canvas.

## Heavy-Process Detection
- `LiveScriptViewport` accepts an optional predicate to indicate Virtual Desktop heavy workload (e.g., Process Card active). If unavailable, it falls back to periodic psutil polling (`cpu_percent` and `virtual_memory`) with conservative thresholds.

## Tests & Validation
- `tests/test_live_engine.py` verifies `LiveScriptController` loading and reload behavior by writing temporary scripts and asserting hook calls.
- No direct Qt/OpenGL tests to avoid GUI dependencies; logic is validated at controller level.

## Verification Commands
- `python -m py_compile $(git ls-files '*.py')`
- `flake8 tests`
- `QT_QPA_PLATFORM=offscreen pytest`
- `python tools/manage_tests.py`
- `python tools/logic_inbox.py --validate`
