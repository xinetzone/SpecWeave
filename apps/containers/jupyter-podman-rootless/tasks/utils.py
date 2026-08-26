"""容器管理工具函数。

提供容器运行时检测、路径转换、命令执行、随机字符串生成等基础工具。
"""
import platform
import secrets
import shutil
import string
from pathlib import Path
from typing import Optional

from invoke import Context, Result
from invoke.exceptions import Exit, UnexpectedExit

MIRROR_CHOICES: list[str] = ["official", "tuna", "aliyun"]


def detect_runtime() -> str:
    """检测容器运行时，优先使用podman。"""
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise Exit("未找到podman或docker，请先安装其中之一")


def to_posix_path(path: Path) -> str:
    """将路径转换为POSIX风格（适配WSL2/远程Linux podman）。"""
    path_str = str(path.resolve())
    if platform.system() == "Windows":
        if len(path_str) >= 2 and path_str[1] == ":":
            drive = path_str[0].lower()
            rest = path_str[2:].replace("\\", "/")
            return f"/mnt/{drive}{rest}"
        return path_str.replace("\\", "/")
    return path_str


def run_cmd(
    c: Context,
    cmd: str,
    pty: bool = False,
    hide: bool = False,
    warn: bool = False,
    echo: bool = True,
) -> Optional[Result]:
    """执行命令的包装函数。"""
    if echo and not hide:
        print(f"执行: {cmd}")
    try:
        return c.run(cmd, pty=pty, hide=hide, warn=warn, echo=False)
    except UnexpectedExit as e:
        if not warn:
            raise
        return e.result


def generate_random_string(length: int = 12) -> str:
    """生成随机字符串（用于密码/token）。"""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def container_exists(c: Context, runtime: str, name: str) -> bool:
    """检查容器是否存在（包括停止状态）。"""
    result = run_cmd(
        c, f"{runtime} ps -a --filter name=^{name}$ --format '{{{{.Names}}}}'", hide=True, warn=True, echo=False
    )
    return result is not None and result.stdout.strip() == name


def container_running(c: Context, runtime: str, name: str) -> bool:
    """检查容器是否正在运行。"""
    result = run_cmd(
        c, f"{runtime} ps --filter name=^{name}$ --format '{{{{.Names}}}}'", hide=True, warn=True, echo=False
    )
    return result is not None and result.stdout.strip() == name
