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
from contextlib import contextmanager

# Try importing podman-py SDK (optional dependency)
try:
    import podman as _podman_sdk
    from podman.errors import APIError, NotFound as PodmanNotFound
    _SDK_AVAILABLE = True
except ImportError:
    _podman_sdk = None
    APIError = Exception
    PodmanNotFound = Exception
    _SDK_AVAILABLE = False

# Check for podman-compose (daemon-less declarative backend)
_COMPOSE_AVAILABLE = shutil.which("podman-compose") is not None


# ── B-scheme: host podman rootless socket pass-through ──────────
# 背景：容器内自建 daemon（Model A）在 WSL 三层 userns 嵌套下触发
# `newuidmap Operation not permitted`，不可行。改为直连宿主 rootless daemon：
# 把宿主 `/run/user/<uid>/podman/podman.sock` bind-mount 进容器同一路径，
# 并设置 `XDG_RUNTIME_DIR=/run/user/<uid>`，让容器内 podman SDK/CLI 复用宿主
# daemon。默认 uid=1000（WSL2 常见），可用 PODMAN_RUNTIME_UID 环境变量覆盖。
def _podman_runtime_uid():
    return os.environ.get("PODMAN_RUNTIME_UID", "1000")


def podman_sock_path():
    """Host rootless daemon socket path (also used as container mount target)."""
    return f"/run/user/{_podman_runtime_uid()}/podman/podman.sock"


def sdk_available():
    """Check if podman-py SDK is available."""
    return _SDK_AVAILABLE


def compose_available():
    """Check if podman-compose command is available."""
    return _COMPOSE_AVAILABLE


@contextmanager
def get_client():
    """Get container runtime client as context manager.

    Yields PodmanClient instance in SDK mode; yields None when SDK unavailable,
    caller should check for None and fall back to CLI.
    """
    if not _SDK_AVAILABLE:
        yield None
        return

    client = None
    try:
        client = _podman_sdk.from_env()
        client.ping()
        yield client
    except Exception:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
        yield None
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass


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
    "get_client",
    "podman_sock_path",
    "sdk_available",
    "sdk_build_kwargs",
    "sdk_run_kwargs",
]
