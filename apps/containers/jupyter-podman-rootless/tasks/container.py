"""Jupyter Podman Rootless 核心容器管理任务（兼容层）。

本文件为向后兼容的聚合模块，所有实现已原子化拆分到子模块：
- client.py: Podman/Docker 客户端封装（SDK 优先 + CLI fallback）
- utils.py: 工具函数与常量
- build.py: 镜像构建任务
- manage.py: 容器生命周期管理（run/stop/status/clean）
- interact.py: 容器交互任务（shell/logs/exec）
"""
from .build import build
from .client import (
    APIError,
    PodmanNotFound,
    get_client,
    sdk_available,
    sdk_build_kwargs,
    sdk_run_kwargs,
)
from .interact import exec_task, logs, shell
from .manage import clean, run, status, stop
from .utils import (
    MIRROR_CHOICES,
    container_exists,
    container_running,
    detect_runtime,
    generate_random_string,
    run_cmd,
    to_posix_path,
)

__all__ = [
    "APIError",
    "MIRROR_CHOICES",
    "PodmanNotFound",
    "build",
    "clean",
    "container_exists",
    "container_running",
    "detect_runtime",
    "exec_task",
    "generate_random_string",
    "get_client",
    "logs",
    "run",
    "run_cmd",
    "sdk_available",
    "sdk_build_kwargs",
    "sdk_run_kwargs",
    "shell",
    "status",
    "stop",
    "to_posix_path",
]
