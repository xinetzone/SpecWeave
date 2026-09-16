"""proc（运行时探测 / run_cmd / 随机串）测试，全部打桩无真实子进程。"""
import platform
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
    # 默认切断 stdin 转发：invoke 不创建 handle_stdin 线程（FIONREAD 崩溃根因）
    assert kwargs["in_stream"] is False


def test_run_cmd_forward_stdin_opt_in_omits_in_stream():
    """真交互式命令 opt-in 时不得注入 in_stream=False（否则容器 shell 无键盘输入）。"""
    c = FakeContext()
    proc.run_cmd(c, "podman exec -it c bash", hide=True, echo=False, forward_stdin=True)
    _, kwargs = c.calls[0]
    assert "in_stream" not in kwargs


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


# ── invoke stdin 兼容补丁（FIONREAD × Python 3.14） ──────────────────────


class _NoFileno:
    pass


def test_safe_bytes_to_read_non_fileno_returns_one():
    """无 fileno 的对象（不可判定）必须回退 1 且不抛异常。"""
    assert proc._safe_bytes_to_read(_NoFileno()) == 1


def test_safe_bytes_to_read_non_tty_fd_returns_one():
    """非 TTY fd（管道/重定向文件）不做 ioctl，直接回退 1。"""
    import io
    import os as _os

    r, w = _os.pipe()
    try:
        assert proc._safe_bytes_to_read(io.FileIO(r, mode="rb", closefd=False)) == 1
    finally:
        _os.close(r)
        _os.close(w)


@pytest.mark.skipif(platform.system() == "Windows", reason="FIONREAD/pty 仅 POSIX")
def test_safe_bytes_to_read_tty_does_not_overflow():
    """回归实证：invoke 3.0.3 的 2 字节写法在 py3.14 必崩；4 字节补丁不崩。"""
    import fcntl
    import pty
    import termios

    master, slave = pty.openpty()
    try:
        # 先证明环境确实复现上游崩溃（2 字节缓冲，queued=0 也崩）
        with pytest.raises(SystemError, match="buffer overflow"):
            fcntl.ioctl(slave, termios.FIONREAD, b"  ")
        # 补丁实现对同一 tty 正常返回正整数
        import io

        value = proc._safe_bytes_to_read(io.FileIO(slave, mode="rb", closefd=False))
        assert isinstance(value, int) and value >= 1
    finally:
        import os as _os

        _os.close(master)
        _os.close(slave)


def test_apply_invoke_stdin_compat_is_idempotent():
    """补丁幂等：重复应用不重复打标；Windows 上返回 False（上游本就无 ioctl）。"""
    first = proc.apply_invoke_stdin_compat()
    second = proc.apply_invoke_stdin_compat()
    assert first == second
    if platform.system() != "Windows":
        assert first is True
        from invoke import runners, terminals

        # 两个绑定都必须替换：runners 以 from-import 持有独立名字绑定
        assert terminals.bytes_to_read is proc._safe_bytes_to_read
        assert runners.bytes_to_read is proc._safe_bytes_to_read
        assert getattr(terminals, "_jpman_stdin_compat", False) is True
    else:
        assert first is False
