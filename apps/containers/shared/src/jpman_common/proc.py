"""进程执行与运行时探测工具（jpman-builder / jpman-client 共享）。

- :func:`detect_runtime` / :func:`check_runtime_ready`：podman/docker 探测与 ping
- :func:`run_cmd`：invoke 命令包装（Windows UTF-8 / 宿主编码双路径，防止乱码；
  默认切断父进程 stdin 转发，规避 invoke 3.0.3 + Python 3.14 的 FIONREAD 崩溃）
- :func:`generate_random_string`：密码安全随机串
- :func:`apply_invoke_stdin_compat`：invoke ``bytes_to_read`` 兼容补丁（交互式
  opt-in 路径在 Python 3.14 下的键盘输入保障）
"""
import os
import platform
import secrets
import shutil
import string
import struct
import subprocess
from typing import Optional

from invoke import Context, Result
from invoke.exceptions import Exit, UnexpectedExit

from ._win32_transcode import (
    _ensure_win32_console_utf8,
    _ensure_win32_stdout_transcode,
)

__all__ = [
    "detect_runtime",
    "check_runtime_ready",
    "run_cmd",
    "generate_random_string",
    "apply_invoke_stdin_compat",
]


# ---------------------------------------------------------------------------
# invoke stdin 兼容补丁（invoke 3.0.3 × Python 3.14 × TTY/WSL 桥接）
# ---------------------------------------------------------------------------


def _safe_bytes_to_read(input_):
    """``invoke.terminals.bytes_to_read`` 的兼容替换。

    上游 invoke 3.0.3（terminals.py L246）对 TTY stdin 用 **2 字节**缓冲执行
    ``fcntl.ioctl(fd, FIONREAD, b"  ")`` 并按 signed short 解析；但 Linux 的
    FIONREAD 固定向用户缓冲写回 ``sizeof(int)`` = 4 字节。Python 3.14 加固
    fcntl（检测内核写超出提供缓冲长度）后，该调用必抛
    ``SystemError: buffer overflow``——与队列字节数无关（0 字节也崩，
    2026-09-16 py3.14.2 实证，session sc-20260916-xmnn-wheel-stdin）。
    WSL 透明桥接的 stdin 是 console 中继 pty（isatty=真），invoke 的 stdin
    转发线程在命令收尾（中继 fd 半关闭/可读）时必触发，表现为构建成功却
    ThreadException 假失败。

    这里用与内核等长的 4 字节缓冲重做同一查询；任何不可判定情形一律回退 1
    （invoke 上游文档既定语义："unable to tell → read 1 byte"），绝不抛出。
    """
    try:
        fd = input_.fileno()
        if not os.isatty(fd):
            return 1
        import fcntl
        import termios

        buf = fcntl.ioctl(input_, termios.FIONREAD, b"\x00\x00\x00\x00")
        count = int(struct.unpack("i", bytes(buf))[0])
        return count if count > 0 else 1
    except Exception:
        # OSError/SystemError（旧 fcntl 行为）/ValueError/AttributeError/
        # UnsupportedOperation：无法判定时按上游约定读 1 字节，由 read 暴露 EOF
        return 1


def apply_invoke_stdin_compat() -> bool:
    """幂等替换 invoke 的 ``bytes_to_read`` 为兼容实现。

    必须同时改两个绑定：``invoke.terminals.bytes_to_read``（定义点）与
    ``invoke.runners.bytes_to_read``——后者在 runners.py 顶部以
    ``from .terminals import bytes_to_read`` 导入为**模块级名字绑定**，
    只改定义点不会影响 stdin 线程实际调用的引用（2026-09-16 三态 pty
    探针实证：仅补丁 terminals 时崩溃依旧）。

    仅 POSIX 生效（Windows 分支上游直接返回 1，无 ioctl）；invoke 缺失或
    内部结构变化（无该属性）时静默跳过——补丁是加固而非硬依赖。

    :returns: 是否处于已补丁状态（含此前已补丁的幂等命中）。
    """
    if platform.system() == "Windows":
        return False
    try:
        from invoke import terminals
    except Exception:
        return False
    if getattr(terminals, "_jpman_stdin_compat", False):
        return True
    targets = [terminals]
    try:
        from invoke import runners

        targets.append(runners)
    except Exception:
        pass
    patched = False
    for module in targets:
        if getattr(module, "bytes_to_read", None) is not None:
            module.bytes_to_read = _safe_bytes_to_read
            patched = True
    if patched:
        terminals._jpman_stdin_compat = True
    return patched


# 进程一旦导入本模块（所有 invoke 任务经 run_cmd 驱动），即保证全进程内
# Context().run 的 stdin 线程不再触发 FIONREAD 崩溃（含交互式 opt-in 路径）。
apply_invoke_stdin_compat()


def detect_runtime() -> str:
    """检测容器运行时，优先 podman。"""
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise Exit("未找到 podman 或 docker，请先安装其中之一")


def check_runtime_ready() -> tuple[bool, Optional[str]]:
    """检查容器运行时服务端是否可达（ping 测试）。"""
    try:
        runtime = detect_runtime()
    except Exit:
        return False, "未找到 podman 或 docker，请先安装其中之一"

    result = subprocess.run(
        [runtime, "version", "--format", "{{.Server.Version}}"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode == 0 and result.stdout.strip():
        return True, None

    if platform.system() == "Windows":
        hint = (
            f"无法连接到 {runtime} 服务。请确保 Podman machine 正在运行：\n"
            f"  podman machine start\n"
            f"如尚未初始化：podman machine init"
        )
    elif platform.system() == "Darwin":
        hint = (
            f"无法连接到 {runtime} 服务。请确保 Podman machine 正在运行：\n"
            f"  podman machine start"
        )
    else:
        hint = (
            f"无法连接到 {runtime} 服务。请检查 Podman 服务状态：\n"
            f"  systemctl --user status podman\n"
            f"  sudo systemctl status podman"
        )
    return False, hint


def run_cmd(
    c: Context,
    cmd: str,
    pty: bool = False,
    hide: bool = False,
    warn: bool = False,
    echo: bool = True,
    forward_stdin: bool = False,
) -> Optional[Result]:
    """命令执行包装（Windows UTF-8 / 宿主编码双路径，防止乱码/沙箱清空 PATH）。

    :param forward_stdin: 是否把父进程 stdin 转发给子进程。默认 **False**——
        编排命令全部非交互，且 invoke 默认会创建 stdin 转发线程，在
        invoke 3.0.3 × Python 3.14 × TTY（含 WSL 透明桥接的 console 中继）
        下该线程必触发 ``FIONREAD`` 2 字节缓冲 ``SystemError: buffer
        overflow``（详见 :func:`_safe_bytes_to_read`）。仅真交互式命令
        （``podman exec/run -it ... bash``）才传 ``True`` opt-in；其崩溃面
        已由 :func:`apply_invoke_stdin_compat` 兜住。非交互命令无需 stdin，
        Ctrl+C 仍经 invoke 的 KeyboardInterrupt→send_interrupt 信号路径传播。
    """
    subproc_encoding, is_tty_console = _ensure_win32_stdout_transcode()
    if echo and not hide:
        print(f"执行: {cmd}")
    use_pty = pty and platform.system() != "Windows"
    # 强制统一 Python stdout/stderr 编码为 UTF-8（防止容器内 invoke 输出时被 locale 覆盖）
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")

    # ── 原生 TTY Console（非 hide / 非 warn）：绕过 invoke c.run PIPE 捕获层
    #   invoke c.run(pty=False) 内部 subprocess.Popen(stdout=PIPE) → 按 locale cp936 decode
    #   即便是我们在 B 端加了 encoding='utf-8'，对某些版本的 invoke 仍可能被忽略；
    #   而 subprocess.call(shell=True, stdout=None, stderr=None) 直接继承父进程
    #   Console Handle → SetConsoleOutputCP(65001) 已改好，子进程自己写 UTF-8 bytes 就能 100% 渲染对。
    if (
        platform.system() == "Windows"
        and is_tty_console
        and not hide
        and not warn
    ):
        rc = subprocess.call(cmd, shell=True, env=env)
        if rc != 0:
            raise Exit(f"命令执行失败 (exit={rc}): {cmd}")
        return None

    kwargs: dict = dict(
        pty=use_pty, hide=hide, warn=warn, echo=False, env=env,
    )
    if not forward_stdin:
        # invoke 钦定的"stdin 不存在/不可用"标记：不创建 handle_stdin 线程
        # （runners.py create_io_threads 对 falsy in_stream 直接跳过），
        # 从根上消除 FIONREAD 缓冲溢出崩溃；非交互命令零行为损失。
        kwargs["in_stream"] = False
    if subproc_encoding:
        kwargs["encoding"] = subproc_encoding
    try:
        return c.run(cmd, **kwargs)
    except UnexpectedExit as e:
        if not warn:
            raise
        return e.result


def generate_random_string(length: int = 12) -> str:
    """密码安全的随机字符串（密码 16 位 / token 32 位）。"""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))
