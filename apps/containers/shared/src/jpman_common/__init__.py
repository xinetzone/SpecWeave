"""jpman-common：apps/containers 组内共享运行时工具。

jupyter-podman-client（消费端）与 jupyter-podman-rootless（构建端）共同依赖。
本包零栈知识：不得出现 quant/xmnn/monetize 等具体栈常量。

公共 API：
- 平台路径：:func:`to_posix_path` / :func:`normalize_path_str`
- 进程执行：:func:`run_cmd` / :func:`detect_runtime` /
  :func:`check_runtime_ready` / :func:`generate_random_string`
- 容器探测：:func:`container_exists` / :func:`container_running` /
  :func:`container_phase`
"""
from .containers import (
    PHASE_ABSENT,
    PHASE_RUNNING,
    PHASE_STOPPED,
    PHASE_UNKNOWN,
    container_exists,
    container_phase,
    container_running,
)
from .platform_paths import normalize_path_str, to_posix_path
from .proc import (
    check_runtime_ready,
    detect_runtime,
    generate_random_string,
    run_cmd,
)

__version__ = "0.1.0"

__all__ = [
    "PHASE_ABSENT",
    "PHASE_RUNNING",
    "PHASE_STOPPED",
    "PHASE_UNKNOWN",
    "container_exists",
    "container_phase",
    "container_running",
    "normalize_path_str",
    "to_posix_path",
    "check_runtime_ready",
    "detect_runtime",
    "generate_random_string",
    "run_cmd",
]
