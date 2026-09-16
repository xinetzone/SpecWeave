"""Podman/Docker client wrapper module.

Provides three-tier backend priority for container management:
- Tier 1: podman-compose (declarative YAML config, daemon-less, rootless-first)
- Tier 2: podman-py SDK (PodmanClient.from_env() auto-detection)
- Tier 3: CLI direct calls (fallback when both unavailable)
Supports with context manager for auto cleanup.
"""
from __future__ import annotations

import os
import shutil

# SDK 连接统一层（get_client / sdk_available / podman_sock_path / APIError）
# 的唯一实现位于组内共享包 jpman_common.connection：
#   - UID 推导走 env→XDG→getuid→Windows1000 多源事实（C-I5），不再无条件默认 1000；
#   - get_client 在 builder（多为 Linux 原生）等价于旧 from_env()+ping，
#     在 Windows 原生额外获得 P0/P1/P2 候选能力，行为承诺（全失败 yield None）不变。
from jpman_common.connection import (
    APIError,
    PodmanNotFound,
    get_client,
    podman_sock_path,
    sdk_available,
)

# Check for podman-compose (daemon-less declarative backend)
#
# ⚠️ Windows 原生宿主上恒不可用，原因不是「未安装」而是「路径语义错配」：
# podman-compose 是运行在宿主进程内的路径处理器——它先用宿主路径语义预处理
# compose 中的挂载源，再把结果交给 podman。Windows 下 ntpath 把以 `/` 开头的
# 组件当作「驱动器根」，于是 `/run/user/1000/bus` 被解析为当前盘符下的
# `D:\run\user\1000\bus`；随后 compose 内部 assert_volume()（1.6.0 第 591 行
# 做 os.path.join/abspath，第 600 行 os.makedirs）见该路径不存在，便试图在宿主
# 创建目录，实测触发 PermissionError [WinError 5] 与沙箱拦截
# `Not allow operate files: D:\run`；失败被 `except OSError: pass` 吞掉后
# podman 仍会收到被篡改的挂载源。
# 而 podman 本身（Windows 上是远程客户端）会把 Linux 绝对路径原样转发给
# machine 内 daemon 解析——即「路径语义一致」只在 SDK/CLI 层成立。
# 因此 Windows 上必须跳过 Tier 1，自动降级到 Tier 2 SDK / Tier 3 CLI。
_COMPOSE_BINARY_PRESENT = shutil.which("podman-compose") is not None
_COMPOSE_HOST_SUPPORTED = os.name != "nt"
_COMPOSE_AVAILABLE = _COMPOSE_BINARY_PRESENT and _COMPOSE_HOST_SUPPORTED

# ── SSH host key 持久卷（CLI/SDK/compose 三路必须同名同路径）──────────
# named volume 名称对齐 compose 项目名（jupyter-podman-rootless）+ 卷名
# （ssh-host-keys），与 registry-data 卷的命名先例一致；改任一处须同步
# compose.yaml 顶层 volumes 与服务挂载、entrypoint.sh HOST_KEY_DIR。
HOST_KEY_VOLUME = "jupyter-podman-rootless_ssh-host-keys"
HOST_KEY_DIR = "/var/lib/jpman/ssh-host-keys"


# ── B-scheme: host podman rootless socket pass-through ──────────
# 背景：容器内自建 daemon（Model A）在 WSL 三层 userns 嵌套下触发
# `newuidmap Operation not permitted`，不可行。改为直连宿主 rootless daemon：
# 把宿主 `/run/user/<uid>/podman/podman.sock` bind-mount 进容器同一路径，
# 并设置 `XDG_RUNTIME_DIR=/run/user/<uid>`，让容器内 podman SDK/CLI 复用宿主
# daemon。UID 推导（env→XDG→getuid→Windows1000）与 socket 路径统一由
# jpman_common.connection.podman_sock_path 承载（C-I5，禁硬编码 1000）。


def compose_available():
    """Check if podman-compose backend is usable on this host.

    Windows 原生宿主恒为 False（见模块顶部说明）：podman-compose 会用 ntpath
    语义解析 compose 中的 Linux 绝对挂载源，并试图在宿主创建错误目录。
    此时应改走 Tier 2 SDK / Tier 3 CLI——它们把路径原样交给 podman 远程客户端。
    """
    return _COMPOSE_AVAILABLE


def compose_unavailable_reason():
    """Return why the podman-compose backend is unusable; None when it is usable."""
    if not _COMPOSE_BINARY_PRESENT:
        return "podman-compose 未安装（pip install -e \".[compose]\"）"
    if not _COMPOSE_HOST_SUPPORTED:
        return (
            "Windows 原生宿主不支持 podman-compose：它会把 compose 中的 Linux 绝对挂载源"
            "按当前盘符解析（/run/... → D:\\run\\...）并试图在宿主创建该目录"
            "（报 Not allow operate files: D:\\run）。请在 WSL / `podman machine ssh` 内执行，"
            "或改用 invoke（自动降级到 SDK/CLI 后端，路径由远端 daemon 解析）"
        )
    return None


def sdk_run_kwargs(
    ssh_port,
    jupyter_port,
    workspace_posix,
    name,
    tag,
    user_password,
    jupyter_token,
    ssh_public_key=None,
    grant_sudo=False,
    detach=True,
):
    """Build kwargs dict for SDK containers.run()."""
    ports = {
        "22/tcp": ssh_port,
        "8888/tcp": jupyter_port,
    }

    volumes = {
        workspace_posix: {"bind": "/workspace", "mode": "rw"},
        # B-scheme: 直连宿主 rootless daemon（绕过嵌套 userns）。
        # 宿主 socket bind-mount 到容器同一路径，SDK from_env() 即可连通。
        podman_sock_path(): {"bind": podman_sock_path(), "mode": "rw"},
        # SSH host key 持久化：容器删除重建不轮换密钥（entrypoint 按挂载点分流）
        HOST_KEY_VOLUME: {"bind": HOST_KEY_DIR, "mode": "rw"},
    }

    environment = {
        "USER_PASSWORD": user_password,
        "JUPYTER_TOKEN": jupyter_token,
        # B-scheme: 告知 entrypoint 宿主 daemon socket 已经 bind-mount 到容器内
        # 的哪个路径，由它在 devuser 可控目录内建立符号链接并设置 CONTAINER_HOST，
        # 从而使容器内 podman SDK/CLI 复用宿主 daemon（绕过嵌套 userns）。
        "HOST_PODMAN_SOCK": podman_sock_path(),
    }

    if ssh_public_key:
        environment["SSH_PUBLIC_KEY"] = ssh_public_key
    if grant_sudo:
        environment["GRANT_SUDO"] = "yes"

    devices = ["/dev/fuse"]
    security_opt = ["label=disable"]

    kwargs = {
        "image": tag,
        "name": name,
        "ports": ports,
        "volumes": volumes,
        "environment": environment,
        "detach": detach,
        "devices": devices,
        "security_opt": security_opt,
        "cgroupns": "host",
    }

    return kwargs


def sdk_build_kwargs(
    tag,
    apt_mirror,
    conda_mirror,
    pip_mirror,
    no_cache=False,
):
    """Build kwargs dict for SDK images.build()."""
    buildargs = {
        "APT_MIRROR": apt_mirror,
        "CONDA_MIRROR": conda_mirror,
        "PIP_MIRROR": pip_mirror,
    }

    kwargs = {
        "path": ".",
        "tag": tag,
        "buildargs": buildargs,
        "nocache": no_cache,
        "dockerfile": "Containerfile",
    }

    return kwargs


__all__ = [
    "APIError",
    "PodmanNotFound",
    "compose_available",
    "compose_unavailable_reason",
    "get_client",
    "podman_sock_path",
    "sdk_available",
    "sdk_build_kwargs",
    "sdk_run_kwargs",
]
