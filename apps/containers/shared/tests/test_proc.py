"""proc（运行时探测 / run_cmd / 随机串）测试，全部打桩无真实子进程。"""
import types

import pytest
from invoke.exceptions import Exit, UnexpectedExit

from jpman_common import proc


class FakeResult:
    def __init__(self, stdout="", stderr="", exited=0):
        self.stdout = stdout
        self.stderr = stderr
        self.exited = exited
        self.ok = exited == 0


class FakeContext:
    """记录 c.run 调用并返回预设结果的 invoke.Context 替身。"""

    def __init__(self, result=None, raise_exc=None):
        self._result = result or FakeResult()
        self._raise_exc = raise_exc
        self.calls: list[tuple[str, dict]] = []

    def run(self, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._result


# ── detect_runtime ──────────────────────────────────────────────────────

def test_detect_runtime_prefers_podman(monkeypatch):
    monkeypatch.setattr(proc.shutil, "which", lambda name: f"/usr/bin/{name}" if name == "podman" else None)
    assert proc.detect_runtime() == "podman"


def test_detect_runtime_falls_back_docker(monkeypatch):
    monkeypatch.setattr(proc.shutil, "which", lambda name: f"/usr/bin/{name}" if name == "docker" else None)
    assert proc.detect_runtime() == "docker"


def test_detect_runtime_missing_raises(monkeypatch):
    monkeypatch.setattr(proc.shutil, "which", lambda name: None)
    with pytest.raises(Exit):
        proc.detect_runtime()


# ── generate_random_string ──────────────────────────────────────────────

def test_generate_random_string_length_and_charset():
    import string
    s = proc.generate_random_string(32)
    assert len(s) == 32
    allowed = set(string.ascii_letters + string.digits)
    assert set(s) <= allowed
    assert proc.generate_random_string(0) == ""


# ── run_cmd ─────────────────────────────────────────────────────────────

def test_run_cmd_success_passes_invoke_kwargs():
    sentinel = FakeResult(stdout="ok")
    c = FakeContext(result=sentinel)
    out = proc.run_cmd(c, "podman ps", hide=True, echo=False)
    assert out is sentinel
    cmd, kwargs = c.calls[0]
    assert cmd == "podman ps"
    assert kwargs["hide"] is True
    assert kwargs["echo"] is False
    assert kwargs["env"]["PYTHONIOENCODING"] == "utf-8"
    assert kwargs["env"]["PYTHONUTF8"] == "1"


def test_run_cmd_echo_prints(capsys, monkeypatch):
    # PIPE 环境（is_tty=False），hide=False 才会进入 echo 打印分支
    monkeypatch.setattr(
        proc, "_ensure_win32_stdout_transcode", lambda: ("utf-8", False)
    )
    c = FakeContext()
    proc.run_cmd(c, "podman info", hide=False, echo=True)
    captured = capsys.readouterr()
    assert "执行: podman info" in captured.out


def test_run_cmd_warn_returns_result_on_failure():
    bad = FakeResult(stdout="", exited=1)
    c = FakeContext(raise_exc=UnexpectedExit(bad))
    assert proc.run_cmd(c, "podman bad", hide=True, warn=True, echo=False) is bad


def test_run_cmd_no_warn_reraises():
    bad = FakeResult(exited=1)
    c = FakeContext(raise_exc=UnexpectedExit(bad))
    with pytest.raises(UnexpectedExit):
        proc.run_cmd(c, "podman bad", hide=True, warn=False, echo=False)


def test_run_cmd_tty_console_bypass(monkeypatch):
    """Windows TTY 分支：subprocess.call 直继承 Console，返回码 0 时返回 None。"""
    monkeypatch.setattr(proc.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        proc, "_ensure_win32_stdout_transcode", lambda: ("utf-8", True)
    )
    called: dict = {}

    def fake_call(cmd, shell, env):
        called["cmd"] = cmd
        return 0

    monkeypatch.setattr(proc.subprocess, "call", fake_call)
    c = FakeContext()
    assert proc.run_cmd(c, "podman ps", echo=False) is None
    assert called["cmd"] == "podman ps"
    assert c.calls == []  # 绕过了 invoke c.run


def test_run_cmd_tty_console_bypass_failure_raises(monkeypatch):
    monkeypatch.setattr(proc.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        proc, "_ensure_win32_stdout_transcode", lambda: ("utf-8", True)
    )
    monkeypatch.setattr(proc.subprocess, "call", lambda *a, **k: 7)
    c = FakeContext()
    with pytest.raises(Exit, match="exit=7"):
        proc.run_cmd(c, "podman bad", echo=False)


# ── check_runtime_ready ─────────────────────────────────────────────────

def _fake_completed(returncode=0, stdout="5.7.0"):
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")


def test_check_runtime_ready_ok(monkeypatch):
    monkeypatch.setattr(proc, "detect_runtime", lambda: "podman")
    monkeypatch.setattr(proc.subprocess, "run", lambda *a, **k: _fake_completed())
    ok, hint = proc.check_runtime_ready()
    assert ok is True and hint is None


def test_check_runtime_ready_missing_binary(monkeypatch):
    def _raise():
        raise Exit("none")

    monkeypatch.setattr(proc, "detect_runtime", _raise)
    ok, hint = proc.check_runtime_ready()
    assert ok is False
    assert "未找到" in hint


def test_check_runtime_ready_windows_hint(monkeypatch):
    monkeypatch.setattr(proc, "detect_runtime", lambda: "podman")
    monkeypatch.setattr(proc.platform, "system", lambda: "Windows")
    monkeypatch.setattr(proc.subprocess, "run", lambda *a, **k: _fake_completed(returncode=1, stdout=""))
    ok, hint = proc.check_runtime_ready()
    assert ok is False and "podman machine start" in hint


def test_check_runtime_ready_darwin_hint(monkeypatch):
    monkeypatch.setattr(proc, "detect_runtime", lambda: "podman")
    monkeypatch.setattr(proc.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(proc.subprocess, "run", lambda *a, **k: _fake_completed(returncode=1, stdout=""))
    ok, hint = proc.check_runtime_ready()
    assert ok is False and "Podman machine" in hint


def test_check_runtime_ready_linux_hint(monkeypatch):
    monkeypatch.setattr(proc, "detect_runtime", lambda: "podman")
    monkeypatch.setattr(proc.platform, "system", lambda: "Linux")
    monkeypatch.setattr(proc.subprocess, "run", lambda *a, **k: _fake_completed(returncode=1, stdout=""))
    ok, hint = proc.check_runtime_ready()
    assert ok is False and "systemctl" in hint
