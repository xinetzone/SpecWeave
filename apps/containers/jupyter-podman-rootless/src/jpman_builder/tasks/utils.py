"""容器管理工具函数。

提供容器运行时检测、路径转换、命令执行、随机字符串生成等基础工具。
"""
import os
import platform
import secrets
import shutil
import string
import subprocess
from pathlib import Path
from typing import Optional, Tuple

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


def normalize_path_str(path_str: str) -> str:
    """将路径字符串规范化为POSIX格式（适配podman-compose卷挂载解析）。

    在Windows上将Windows路径（``D:\\\\...``）转换为WSL POSIX路径（``/mnt/d/...``）。
    已经是POSIX格式的路径（以``/``开头）原样返回。非Windows平台原样返回。
    """
    if platform.system() != "Windows":
        return path_str
    if path_str.startswith("/"):
        return path_str
    if len(path_str) >= 2 and path_str[1] == ":":
        drive = path_str[0].lower()
        rest = path_str[2:].replace("\\", "/")
        return f"/mnt/{drive}{rest}"
    return path_str.replace("\\", "/")


def check_runtime_ready() -> Tuple[bool, Optional[str]]:
    """检查容器运行时服务是否可达。

    Returns:
        (True, None) 服务可达；(False, hint) 不可达时返回平台相关启动建议。
    """
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
            f"如尚未初始化，请执行：podman machine init"
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
    """执行命令的包装函数。

    Windows 上显式传递完整环境变量，防止沙箱清空 PATH 导致 cmd.exe
    找不到 podman/docker 等命令。Windows 不支持 pty，自动降级。
    """
    if echo and not hide:
        print(f"执行: {cmd}")
    # Windows 不支持 pty 模块，自动降级为管道模式
    use_pty = pty and platform.system() != "Windows"
    try:
        return c.run(cmd, pty=use_pty, hide=hide, warn=warn, echo=False, env=os.environ.copy())
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
