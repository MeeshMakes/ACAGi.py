import sys

from tools import manage_tests


def test_manage_tests_invokes_pytest(monkeypatch, capsys):
    calls = {}

    def fake_run(cmd, cwd=None, env=None):
        calls["cmd"] = cmd
        calls["cwd"] = cwd
        calls["env"] = env

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(manage_tests.subprocess, "run", fake_run)

    exit_code = manage_tests.main(["-k", "sample"])

    assert exit_code == 0
    assert calls["cmd"][:3] == [sys.executable, "-m", "pytest"]
    assert "-k" in calls["cmd"] and "sample" in calls["cmd"]
    assert calls["cwd"] == manage_tests.REPO_ROOT
    assert calls["env"].get("QT_QPA_PLATFORM") == "offscreen"
    output = capsys.readouterr().out
    assert "Running tests via pytest" in output
