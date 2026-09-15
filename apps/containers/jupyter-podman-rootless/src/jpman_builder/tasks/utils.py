"""容器管理基础工具（构建端垫片）。

唯一实现已上移至组内共享包 ``jpman_common``（apps/containers/shared），
本模块仅再导出以保持构建端 ``from .utils import ...`` 路径稳定；
``MIRROR_CHOICES`` 为构建端镜像源专属常量，仍定义于此。
"""
from jpman_common import (
    PHASE_ABSENT,
    PHASE_RUNNING,
    PHASE_STOPPED,
    PHASE_UNKNOWN,
    check_runtime_ready,
    container_exists,
    container_phase,
    container_running,
    detect_runtime,
    generate_random_string,
    normalize_path_str,
    run_cmd,
    to_posix_path,
)

MIRROR_CHOICES: list[str] = ["official", "tuna", "aliyun"]

__all__ = [
    "MIRROR_CHOICES",
    "PHASE_ABSENT",
    "PHASE_RUNNING",
    "PHASE_STOPPED",
    "PHASE_UNKNOWN",
    "check_runtime_ready",
    "container_exists",
    "container_phase",
    "container_running",
    "detect_runtime",
    "generate_random_string",
    "normalize_path_str",
    "run_cmd",
    "to_posix_path",
]
