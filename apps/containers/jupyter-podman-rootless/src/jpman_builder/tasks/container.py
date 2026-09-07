"""Jupyter Podman Rootless 核心容器管理任务（兼容层）。

本文件为向后兼容的聚合模块，所有实现已原子化拆分到子模块：
- client.py: Podman/Docker 客户端封装（三层后端优先级检测）
- compose_backend.py: podman-compose 声明式编排后端（Tier 1）
- utils.py: 工具函数与常量
- build.py: 镜像构建任务
- manage.py: 容器生命周期管理（run/stop/status/clean）
- interact.py: 容器交互任务（shell/logs/exec）
"""
from .build import build
from .client import (
    APIError,
    PodmanNotFound,
    compose_available,
    get_client,
    sdk_available,
    sdk_build_kwargs,
    sdk_run_kwargs,
)
from .compose_backend import (
    compose_build,
    compose_down,
    compose_exec,
    compose_logs,
    compose_ps,
    compose_up,
    is_compose_ready,
)
from .interact import exec_task, logs, shell
from .manage import clean, run, status, stop
from .utils import (
    MIRROR_CHOICES,
    check_runtime_ready,
    container_exists,
    container_running,
    detect_runtime,
    generate_random_string,
    normalize_path_str,
    run_cmd,
    to_posix_path,
)

__all__ = [
    "APIError",
    "MIRROR_CHOICES",
    "PodmanNotFound",
    "build",
    "check_runtime_ready",
    "clean",
    "compose_available",
    "compose_build",
    "compose_down",
    "compose_exec",
    "compose_logs",
    "compose_ps",
    "compose_up",
    "container_exists",
    "container_running",
    "detect_runtime",
    "exec_task",
    "generate_random_string",
    "get_client",
    "is_compose_ready",
    "logs",
    "normalize_path_str",
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
