import time
from pathlib import Path

import pytest

from background.live_engine import LiveScriptController


def test_controller_loads_and_calls_hooks(tmp_path: Path) -> None:
    script = tmp_path / "bg.py"
    script.write_text(
        "state = {'init': 0, 'resize': None, 'update': 0, 'render': 0}\n"
        "def init(widget):\n    state['init'] += 1\n"
        "def resize(w, h):\n    state['resize'] = (w, h)\n"
        "def update(dt):\n    state['update'] += 1; state['last_dt'] = dt\n"
        "def render(widget):\n    state['render'] += 1\n",
        encoding="utf-8",
    )

    controller = LiveScriptController()
    controller.set_script(str(script))
    module = controller.module
    assert module is not None
    controller.call("init", object())
    controller.call("resize", 320, 200)
    controller.call("update", 0.016)
    controller.call("render", object())

    assert module.state["init"] == 1
    assert module.state["resize"] == (320, 200)
    assert module.state["update"] == 1
    assert module.state["render"] == 1
    assert module.state["last_dt"] == pytest.approx(0.016, rel=1e-3)

    # Modify the script to ensure reload picks up new behavior
    time.sleep(0.05)  # ensure filesystem mtime ticks
    script.write_text(
        "state = {'version': 2}\n"
        "def init(widget):\n    state['initialized'] = True\n",
        encoding="utf-8",
    )
    assert controller.reload_if_changed() is True
    new_module = controller.module
    assert new_module is not None
    assert new_module is not module
    controller.call("init", object())
    assert new_module.state["initialized"] is True


def test_controller_loads_after_file_appears(tmp_path: Path) -> None:
    script = tmp_path / "bg_missing.py"
    controller = LiveScriptController()
    controller.set_script(str(script))
    assert controller.module is None

    script.write_text("flag = 41\n", encoding="utf-8")
    assert controller.reload_if_changed() is True
    module = controller.module
    assert module is not None
    assert module.flag == 41
