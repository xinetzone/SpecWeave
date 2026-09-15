"""agent-monetize-dev 工作负载叠加栈的 podman-compose 编排任务（opt-in 命名空间）。

声明式栈：唯一事实源 ``MONETIZE_SPEC``；六任务由
overlay_core.make_stack_tasks 工厂生成，栈内 exec 长任务（build-native/wheel）
用内核 helper 在本模块薄封装（形态 B）。

驱动 ``overlays/agent-monetize-dev`` 叠加栈：栈内 clang++ 编译 tvm-ffi 原生
模块（score_opportunity.so，链接 apache-tvm-ffi）与 setuptools 打纯 Python
wheel；apache-tvm-ffi wheel 为 cp314 GIL，编译/运行/内核解释器统一 base env
（/opt/conda/bin/python，单 ABI；与 xmnn 双 ABI 不同）。

定位（红线）：
  - 本模块**禁止 import podman**，只通过子进程驱动 podman-compose；
  - 与根 SDK→CLI 两层平行，禁止回流 invoke run；
  - Windows 原生优先透明桥接 WSL，不可桥接再门禁 Exit(1)。

提供 8 个命令：
  invoke monetize.build / up / down / ps / logs / smoke
  invoke monetize.build-native  栈内 clang++ 编译原生 .so
  invoke monetize.wheel         栈内 setuptools 打纯 Python wheel
"""
from __future__ import annotations

from invoke import Context, task

from .overlay_core import (
    SmokeSpec,
    SourceMount,
    StackSpec,
    TaskDocs,
    ensure_runtime_ready,
    gates,
    make_stack_tasks,
    require_running,
    run_compose,
)

_NATIVE_SCRIPT = "/opt/monetize-builder/scripts/build-native.sh"
_WHEEL_SCRIPT = "/opt/monetize-builder/scripts/build-wheel.sh"

MONETIZE_SPEC = StackSpec(
    namespace="monetize",
    project="agent-monetize-dev",
    service="monetize",
    overlay_subdir="agent-monetize-dev",
    containerfile="Containerfile.agent-monetize",
    default_image_tag="localhost/agent-monetize-dev:latest",
    default_base_image="localhost/jupyter-podman-rootless:latest",
    env_prefix="MONETIZE",
    docs=TaskDocs(
        build="构建 agent-monetize-dev 叠加镜像（构建期守卫失败即失败）。",
        up="渲染并启动 agent-monetize-dev 栈（podman-compose up -d，默认随带构建）。",
        down="停止并删除 agent-monetize-dev 栈容器与网络（bind 数据不受影响）。",
        ps="查看 agent-monetize-dev 栈服务状态。",
        logs="跟踪 agent-monetize-dev 栈服务日志（Ctrl+C 退出，不影响容器运行）。",
        smoke="运行 agent-monetize 冒烟：工具链守卫（始终）+ 原生/挂载冒烟（栈运行时）。",
    ),
    down_volumes_help="同时删除栈命名卷（默认保留以加速重复运行）",
    ssh_default="2224",
    jupyter_default="8892",
    gpu_override=False,
    conda_mirror=False,
    auto_shortflags=False,
    source_mounts=(
        SourceMount("MONETIZE_SRC_PATH", "apps/agent-monetize", "agent-monetize 源码树"),
    ),
    smoke=SmokeSpec(
        python="/opt/conda/bin/python",
        smoke_dir="/opt/agent-monetize-dev-smoke",
        exec_scripts=("_toolchain_guards.py", "smoke_native.py"),
        standalone_scripts=("_toolchain_guards.py",),
        running_note="检测到运行中的栈，经 compose exec 执行守卫与原生冒烟：",
        standalone_note="栈未运行，使用一次性容器仅执行工具链守卫（原生冒烟需先 up）：",
        done_message="冒烟通过",
    ),
    bridge_env_keys=(
        "MONETIZE_IMAGE_TAG", "MONETIZE_CONTAINER_NAME", "MONETIZE_WORKSPACE",
        "MONETIZE_SSH_PORT", "MONETIZE_JUPYTER_PORT", "MONETIZE_SRC_PATH",
    ),
    not_running_hint="monetize 栈未运行，请先：invoke monetize.up --skip-build",
)

TASKS = make_stack_tasks(MONETIZE_SPEC)
build = TASKS["build"]
up = TASKS["up"]
down = TASKS["down"]
ps = TASKS["ps"]
logs = TASKS["logs"]
smoke = TASKS["smoke"]


# ---------------------------------------------------------------------------
# 栈内 exec 长任务（形态 B：clang++ 编译原生 .so / setuptools 打 wheel）
# ---------------------------------------------------------------------------


@task(auto_shortflags=False)
def build_native(c: Context) -> None:
    """栈内 clang++ 编译 score_opportunity.cc → native/build/score_opportunity.so。"""
    gates(MONETIZE_SPEC)
    ensure_runtime_ready(MONETIZE_SPEC)
    require_running(c, MONETIZE_SPEC)
    print("[monetize] 栈内编译 tvm-ffi 原生模块（链接 apache-tvm-ffi libtvm_ffi.so）")
    run_compose(
        c, MONETIZE_SPEC, "exec", "-T", MONETIZE_SPEC.service,
        "bash", _NATIVE_SCRIPT, pty=True,
    )


@task(auto_shortflags=False)
def wheel(c: Context) -> None:
    """栈内 setuptools 打 agent-monetize 纯 Python wheel（产物落 workspace/dist）。"""
    gates(MONETIZE_SPEC)
    ensure_runtime_ready(MONETIZE_SPEC)
    require_running(c, MONETIZE_SPEC)
    print("[monetize] 栈内打包 agent-monetize wheel（纯 Python，.so 不入库）")
    run_compose(
        c, MONETIZE_SPEC, "exec", "-T", MONETIZE_SPEC.service,
        "bash", _WHEEL_SCRIPT, pty=True,
    )
