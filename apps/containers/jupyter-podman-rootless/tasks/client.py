"""Podman/Docker client wrapper module.

Provides SDK-first, CLI-fallback container runtime client management:
- Prefers official podman-py SDK (PodmanClient.from_env() auto-detection)
- Automatically falls back to CLI calls when SDK unavailable
- Supports with context manager for auto cleanup
"""
from __future__ import annotations

import os
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


def sdk_available():
    """Check if podman-py SDK is available."""
    return _SDK_AVAILABLE


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
    }

    environment = {
        "USER_PASSWORD": user_password,
        "JUPYTER_TOKEN": jupyter_token,
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
    "get_client",
    "sdk_available",
    "sdk_build_kwargs",
    "sdk_run_kwargs",
]
