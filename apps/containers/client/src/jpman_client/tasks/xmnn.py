"""xmnn-dev 开发/打包叠加栈的 podman-compose 编排任务（opt-in 命名空间）。

声明式栈：唯一事实源 ``XMNN_SPEC``；六任务由
overlay_core.make_stack_tasks 工厂生成，栈内 exec 长任务（build-tvm/wheel）
用内核 helper 在本模块薄封装（形态 B）。

驱动 ``overlays/xmnn-dev`` 叠加栈：运行时 bind 挂载 npu_tvm / npuusertools /
models 源码（默认锚定仓库根 external/chaos），容器内 LLVM 22 + Nuitka 4.1.3
工具链，支持源码调试与 xmnn wheel 打包。

双 cp314 ABI 契约（C13，禁止互换）：
  - base env /opt/conda = cp314 GIL：工具链守卫、内核、apache-tvm-ffi 类依赖；
  - main env /opt/conda/envs/main = cp314t（free-threaded）：量化/运行时；
  - 本栈工具链/打包解释器为 BASE_PYTHON=/opt/conda/bin/python（见 compose/
    Containerfile），build-tvm/wheel 经 bash 脚本在栈内执行。

提供 8 个命令：
  invoke xmnn.build / up / down / ps / logs / smoke
  invoke xmnn.build-tvm   栈内编译 TVM C++ 原生库（libtvm.so，长任务）
  invoke xmnn.wheel       栈内 Nuitka 打包 xmnn whl（长任务，产物落 workspace/dist）

平台姿态（内核统一）：Windows 原生优先透明桥接 WSL，不可桥接再门禁；POSIX
缺 podman-compose 提示装 ``pip install -e ".[compose]"``。

环境变量优先级：shell 显式 export > root client .env（load_dotenv
override=False）> compose.yaml 内 ${VAR:-default}。
"""
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

BUILDER_SCRIPTS = "/opt/xmnn-builder/scripts"

XMNN_SPEC = StackSpec(
    namespace="xmnn",
    project="xmnn-dev",
    service="xmnn",
    overlay_subdir="xmnn-dev",
    containerfile="Containerfile.xmnn-dev",
    default_image_tag="localhost/xmnn-dev:latest",
    default_base_image="localhost/jupyter-podman-rootless:latest",
    env_prefix="XMNN",
    docs=TaskDocs(
        build="构建 xmnn-dev 叠加镜像（main env LLVM 22 工具链 + base env Nuitka 打包栈）。",
        up="渲染并启动 xmnn-dev 栈（podman-compose up -d，默认随带构建）。",
        down="停止并删除 xmnn-dev 栈容器与网络（源码/workspace 绑定不受影响）。",
        ps="查看 xmnn-dev 栈服务状态。",
        logs="跟踪 xmnn-dev 栈服务日志（Ctrl+C 退出，不影响容器运行）。",
        smoke="运行 xmnn-dev 冒烟：工具链守卫（始终）+ 源码挂载检查（栈运行时）。",
    ),
    down_volumes_help="同时删除 xmnn-ccache 命名卷（默认保留以加速重复打包）",
    ssh_default="2223",
    jupyter_default="8890",
    jupyter_banner_note="（内核：Python 3.14 (xmnn dev)）",
    up_footer=(
        "[xmnn]   状态: invoke xmnn.ps    日志: invoke xmnn.logs",
        "[xmnn]   冒烟: invoke xmnn.smoke",
        "[xmnn]   编译 TVM: invoke xmnn.build-tvm    打包 wheel: invoke xmnn.wheel",
    ),
    gpu_override=False,
    conda_mirror=True,
    auto_shortflags=False,
    source_mounts=(
        SourceMount("NPU_TVM_PATH", "external/chaos/npu_tvm", "npu_tvm 源码树（含 python/tvm）"),
        SourceMount("NPUUSERTOOLS_PATH", "external/chaos/npuusertools", "npuusertools 源码树（含 xmnn 包）"),
        SourceMount("MODELS_PATH", "external/chaos/models", "模型目录"),
    ),
    smoke=SmokeSpec(
        python="/opt/conda/bin/python",
        smoke_dir="/opt/xmnn-dev-smoke",
        exec_scripts=("_toolchain_guards.py", "smoke_mounts.py"),
        standalone_scripts=("_toolchain_guards.py",),
        running_note="检测到运行中的栈，经 compose exec 执行守卫与挂载冒烟：",
        standalone_note="栈未运行，使用一次性容器仅执行工具链守卫（挂载冒烟需先 up）：",
        done_message="冒烟通过",
    ),
    bridge_env_keys=(
        "XMNN_IMAGE_TAG", "XMNN_CONTAINER_NAME", "XMNN_WORKSPACE",
        "XMNN_SSH_PORT", "XMNN_JUPYTER_PORT",
        "NPU_TVM_PATH", "NPUUSERTOOLS_PATH", "MODELS_PATH",
    ),
)

TASKS = make_stack_tasks(XMNN_SPEC)
build = TASKS["build"]
up = TASKS["up"]
down = TASKS["down"]
ps = TASKS["ps"]
logs = TASKS["logs"]
smoke = TASKS["smoke"]


# ---------------------------------------------------------------------------
# 栈内 exec 长任务（build-tvm / wheel；产物落 /workspace，源码/workspace 绑定）
# ---------------------------------------------------------------------------


@task(
    help={
        "jobs": "Nuitka 并行任务数（映射 NUITKA_JOBS，默认读 compose env=8；内存不足用 4）",
        "clean": "CLEAN_REBUILD=1：禁用 ccache 全量重编（不清空缓存）",
        "tvm-flags": "透传给三次 Nuitka 调用的额外参数（映射 TVM_COMPILE_FLAGS，加引号）",
    },
    auto_shortflags=False,
)
def wheel(
    c: Context,
    jobs: int | None = None,
    clean: bool = False,
    tvm_flags: str | None = None,
) -> None:
    """栈内执行 Nuitka 全流程打包 xmnn whl（tvm→vta/xmnn→wheel，长任务）。

    产物落 /workspace/dist（宿主 workspace/dist）。前置：
    栈在运行且 /workspace/npu_tvm/build/libtvm.so 已就位（否则先 build-tvm）。
    """
    gates(XMNN_SPEC)
    ensure_runtime_ready(XMNN_SPEC)
    require_running(c, XMNN_SPEC)
    extra: list[str] = []
    if jobs is not None:
        extra += ["-e", f"NUITKA_JOBS={int(jobs)}"]
    if clean:
        extra += ["-e", "CLEAN_REBUILD=1"]
    if tvm_flags:
        extra += ["-e", f"TVM_COMPILE_FLAGS={tvm_flags}"]
    run_compose(
        c, XMNN_SPEC, "exec", *extra, "-T", XMNN_SPEC.service,
        "bash", f"{BUILDER_SCRIPTS}/build-wheel.sh", pty=True,
    )
    print("[xmnn] ✅ wheel 打包流程结束；产物目录：容器 /workspace/dist（宿主 workspace/dist）")
    print("[xmnn]   10 项隔离验证（临时 venv，不污染源码环境）：")
    print(f"           podman-compose exec xmnn bash {BUILDER_SCRIPTS}/verify-wheel.sh")


@task(auto_shortflags=False)
def build_tvm(c: Context) -> None:
    """栈内编译 TVM C++ 原生库（inv config -f + USE_EXAMPLE_TARGET_HOOKS + inv make）。"""
    gates(XMNN_SPEC)
    ensure_runtime_ready(XMNN_SPEC)
    require_running(c, XMNN_SPEC)
    print("[xmnn] 首次全量编译耗时较长（ccache 命中后增量很快）；Ctrl+C 不影响容器。")
    run_compose(
        c, XMNN_SPEC, "exec", "-T", XMNN_SPEC.service,
        "bash", f"{BUILDER_SCRIPTS}/build-tvm.sh", pty=True,
    )
