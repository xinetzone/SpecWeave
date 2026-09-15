"""_win32_transcode 分支测试（真实控制台副作用全部打桩）。"""
import platform as _platform

import pytest

from jpman_common import _win32_transcode as wt


IS_WINDOWS = _platform.system() == "Windows"


def test_non_windows_returns_empty(monkeypatch):
    monkeypatch.setattr(wt.platform, "system", lambda: "Linux")
    assert wt._ensure_win32_stdout_transcode() == ("", False)


@pytest.mark.skipif(not IS_WINDOWS, reason="仅在 Windows 宿主验证 PIPE 分支")
def test_windows_pipe_branch(reset_transcode_singleton):
    # 测试运行器下 stdout 为 PIPE（os.isatty=False），走路径 2
    enc, is_tty = wt._ensure_win32_stdout_transcode()
    assert enc == "utf-8"
    assert is_tty is False


def test_cached_singleton_short_circuit(monkeypatch, reset_transcode_singleton):
    # platform 守卫先于缓存判定：返回 Windows 后，命中缓存不得再触碰 ctypes 等初始化路径
    monkeypatch.setattr(wt.platform, "system", lambda: "Windows")
    wt._WIN32_STDOUT_TRANSCODE_READY = True
    wt._WIN32_TRANSCODE_CACHED_RESULT = ("cached-enc", True)

    def _boom(*a, **k):
        raise AssertionError("缓存命中时不应再执行 WinDLL 初始化")

    monkeypatch.setattr(wt.ctypes, "WinDLL", _boom)
    assert wt._ensure_win32_stdout_transcode() == ("cached-enc", True)


@pytest.mark.skipif(not IS_WINDOWS, reason="ctypes.WinDLL 路径仅 Windows 有效")
def test_windows_pipe_branch_host_cp936(monkeypatch, reset_transcode_singleton):
    """PIPE + 宿主 CP936：换壳编码取宿主 cp936，子进程仍强制 UTF-8。"""

    class _FakeKernel32:
        def GetConsoleOutputCP(self):
            return 936

        def SetConsoleOutputCP(self, cp):
            return None

        def SetConsoleCP(self, cp):
            return None

    monkeypatch.setattr(wt.ctypes, "WinDLL", lambda *a, **k: _FakeKernel32())
    wrapped: list[str] = []
    monkeypatch.setattr(wt, "_wrap_stdio_encoding", lambda enc: wrapped.append(enc))
    enc, is_tty = wt._ensure_win32_stdout_transcode()
    assert (enc, is_tty) == ("utf-8", False)
    assert wrapped == ["cp936"]


@pytest.mark.skipif(not IS_WINDOWS, reason="ctypes.WinDLL 路径仅 Windows 有效")
def test_windows_pipe_branch_kernel32_error_locale_fallback(monkeypatch, reset_transcode_singleton):
    """WinDLL 不可用 → console_cp=0；locale 首选编码非 UTF-8 时回落宿主编码。"""

    def _boom(*a, **k):
        raise OSError("no kernel32")

    monkeypatch.setattr(wt.ctypes, "WinDLL", _boom)
    import locale
    monkeypatch.setattr(locale, "getpreferredencoding", lambda do_setlocale=False: "cp936")
    wrapped: list[str] = []
    monkeypatch.setattr(wt, "_wrap_stdio_encoding", lambda enc: wrapped.append(enc))
    enc, is_tty = wt._ensure_win32_stdout_transcode()
    assert (enc, is_tty) == ("utf-8", False)
    assert wrapped == ["cp936"]


@pytest.mark.skipif(not IS_WINDOWS, reason="ctypes.WinDLL 路径仅 Windows 有效")
def test_windows_isatty_exception_falls_to_pipe(monkeypatch, reset_transcode_singleton):
    """os.isatty/fileno 抛异常（典型 StringIO stdout）→ 安全回落 PIPE 分支。"""
    monkeypatch.setattr(wt.ctypes, "WinDLL", lambda *a, **k: None)

    def _raise(fd):
        raise OSError("bad fd")

    monkeypatch.setattr(wt.os, "isatty", _raise)
    enc, is_tty = wt._ensure_win32_stdout_transcode()
    assert is_tty is False and enc == "utf-8"


@pytest.mark.skipif(not IS_WINDOWS, reason="ctypes.WinDLL 路径仅 Windows 有效")
def test_windows_tty_branch(monkeypatch, reset_transcode_singleton):
    """原生 TTY Console 分支：UTF-8 换壳 + 子进程 UTF-8 编码。"""
    wrapped: list[str] = []
    monkeypatch.setattr(wt, "_wrap_stdio_encoding", lambda enc: wrapped.append(enc))

    class _FakeKernel32:
        def GetConsoleOutputCP(self):
            return 936

        def SetConsoleOutputCP(self, cp):
            return None

        def SetConsoleCP(self, cp):
            return None

    monkeypatch.setattr(wt.ctypes, "WinDLL", lambda *a, **k: _FakeKernel32())
    # pytest 捕获下 sys.stdout 无真实 fd，打桩 fileno + isatty 模拟原生 TTY
    import sys as _sys
    monkeypatch.setattr(_sys.stdout, "fileno", lambda: 1, raising=False)
    seen: list = []
    monkeypatch.setattr(wt.os, "isatty", lambda fd: seen.append(fd) or True)
    assert _sys.stdout.fileno() == 1
    # chcp.com 仅在 .NET interop 不可用时回退触发；打桩为零副作用
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)

    enc, is_tty = wt._ensure_win32_stdout_transcode()
    assert seen == [1], f"isatty 调用记录异常: {seen}"
    assert enc == "utf-8"
    assert is_tty is True
    assert wrapped == ["utf-8"]


def test_wrap_stdio_encoding_swallows_objects_without_buffer(monkeypatch):
    """被重定向成 StringIO 等无 buffer 对象时静默跳过，不抛异常。"""

    class _NoBuffer:
        buffer = None  # 显式无有效 buffer

    monkeypatch.setattr("sys.stdout", _NoBuffer())
    monkeypatch.setattr("sys.stderr", _NoBuffer())
    wt._wrap_stdio_encoding("utf-8")  # 不应抛出


def test_legacy_alias_is_callable():
    wt._ensure_win32_console_utf8()  # 非 Windows 直接返回；Windows 幂等
