"""平台路径转换工具（jpman-builder / jpman-client 共享）。

Windows 宿主路径 ↔ WSL2/POSIX 路径（Dimension A：挂载路径转换，与 SDK 连接
URL 的 Dimension B 解耦）。
"""
import platform
from pathlib import Path


def to_posix_path(path: Path | str) -> str:
    """将路径转换为 POSIX 风格（适配 WSL2/远程 podman）。

    Windows 宿主 ``D:\\ws`` → ``/mnt/d/ws``；非 Windows 原样返回 resolve 结果。
    """
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
