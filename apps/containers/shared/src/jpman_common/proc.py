"""进程执行与运行时探测工具（jpman-builder / jpman-client 共享）。

- :func:`detect_runtime` / :func:`check_runtime_ready`：podman/docker 探测与 ping
- :func:`run_cmd`：invoke 命令包装（Windows UTF-8 / 宿主编码双路径，防止乱码）
- :func:`generate_random_string`：密码安全随机串
"""
import os
import platform
import secrets
import shutil
import string
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
]


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
) -> Optional[Result]:
    """命令执行包装（Windows UTF-8 / 宿主编码双路径，防止乱码/沙箱清空 PATH）。"""
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
