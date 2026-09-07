"""镜像消费端工具函数。

提供容器运行时检测、路径转换、命令执行、随机字符串生成、
以及基于 dataclass 的配置对象。与构建端保持接口一致，
但避免跨应用 import，保持消费端的独立性与可移植性。
"""
import os
import platform
import secrets
import shutil
import string
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

from invoke import Context, Result
from invoke.exceptions import Exit, UnexpectedExit


@dataclass
class ContainerConfig:
    """容器运行配置（rootless 三必需参数已内置默认）。

    对应 jpman 日常驾驶纪律中的 rootless 容器三必需：
      - devices = ["/dev/fuse"]
      - security_opt = ["label=disable"]
      - cgroupns = "host"
    """

    image: str = "localhost/jupyter-podman-rootless:latest"
    name: str = "jupyter-podman"
    ssh_port: int = 2222
    jupyter_port: int = 8888
    workspace: str = "./workspace"
    user_password: str = ""
    jupyter_token: str = ""
    ssh_public_key: str = ""
    grant_sudo: bool = True
    devices: list[str] = field(default_factory=lambda: ["/dev/fuse"])
    security_opt: list[str] = field(default_factory=lambda: ["label=disable"])
    cgroupns: str = "host"
    detach: bool = True

    def resolved_workspace(self) -> Path:
        """将 workspace 解析为绝对路径（基于当前 cwd）。"""
        ws = Path(self.workspace)
        if not ws.is_absolute():
            ws = Path.cwd() / ws
        return ws.resolve()


@dataclass
class LoadImageResult:
    loaded: bool
    tags: list[str] = field(default_factory=list)
    id: str = ""
    message: str = ""


def detect_runtime() -> str:
    """检测容器运行时，优先 podman。"""
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise Exit("未找到 podman 或 docker，请先安装其中之一")


def to_posix_path(path: Path | str) -> str:
    """将路径转换为 POSIX 风格（适配 WSL2/远程 podman）。"""
    p = Path(path)
    path_str = str(p.resolve())
    if platform.system() == "Windows":
        if len(path_str) >= 2 and path_str[1] == ":":
            drive = path_str[0].lower()
            rest = path_str[2:].replace("\\", "/")
            return f"/mnt/{drive}{rest}"
        return path_str.replace("\\", "/")
    return path_str


def normalize_path_str(path_str: str) -> str:
    """规范化路径字符串（保持 podman-compose 卷挂载解析兼容）。

    Windows 路径（``D:\\...``）转 POSIX（``/mnt/d/...``），
    已经是 POSIX（以 ``/`` 开头）或非 Windows 原样返回。
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
    """命令执行包装（Windows 显式传完整环境，防止 PATH 被沙箱清空）。"""
    if echo and not hide:
        print(f"执行: {cmd}")
    use_pty = pty and platform.system() != "Windows"
    try:
        return c.run(cmd, pty=use_pty, hide=hide, warn=warn, echo=False, env=os.environ.copy())
    except UnexpectedExit as e:
        if not warn:
            raise
        return e.result


def generate_random_string(length: int = 12) -> str:
    """密码安全的随机字符串（密码 16 位 / token 32 位）。"""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def container_exists(c: Context, runtime: str, name: str) -> bool:
    """检查容器是否存在（包括停止态）。"""
    go_fmt = "{{.Names}}"
    result = run_cmd(
        c,
        runtime + ' ps -a --filter name=^' + name + '$ --format "' + go_fmt + '"',
        hide=True,
        warn=True,
        echo=False,
    )
    return result is not None and result.stdout.strip() == name


def container_running(c: Context, runtime: str, name: str) -> bool:
    """检查容器是否正在运行。"""
    go_fmt = "{{.Names}}"
    result = run_cmd(
        c,
        runtime + ' ps --filter name=^' + name + '$ --format "' + go_fmt + '"',
        hide=True,
        warn=True,
        echo=False,
    )
    return result is not None and result.stdout.strip() == name


def default_build_cache_dir() -> Path:
    """获取构建端默认的镜像缓存目录（供 load 命令默认搜索）。

    返回相对本 client 应用目录的：
        ../jupyter-podman-rootless/.image-cache
    """
    here = Path(__file__).parent.parent.resolve()
    cache = here / ".." / "jupyter-podman-rootless" / ".image-cache"
    return cache.resolve()


def find_latest_image_tar(search_dir: Path) -> Optional[Path]:
    """在缓存目录中搜索最新（按文件名/时间排序）的镜像 tar.gz。"""
    if not search_dir.exists():
        return None
    candidates = sorted(
        search_dir.glob("*.tar.gz"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None
