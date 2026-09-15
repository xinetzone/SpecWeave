"""容器只读探测（CLI 路径，jpman-builder / jpman-client 共享）。

通过 ``<runtime> ps --filter`` 判断容器存在性/运行态；与 SDK 路径互补。
"""
from invoke import Context

from .proc import run_cmd

__all__ = ["container_exists", "container_running"]


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
