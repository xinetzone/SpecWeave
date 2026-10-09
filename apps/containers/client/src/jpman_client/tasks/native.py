"""native-dev 原生开发/打包叠加栈的 podman-compose 编排任务（opt-in 命名空间）。
声明式栈：唯一事实源 ``NATIVE_SPEC``；八任务由 overlay_core.make_stack_tasks
工厂生成，栈内 exec 长任务（build-tvm/wheel）用内核 helper 薄封装（形态 B）。
驱动 ``overlays/native-dev``：运行时 bind 挂载 npu_tvm / npuusertools / models
源码（锚定 external/chaos）与 .temp（容器内 /workspace/temp，
``NATIVE_TEMP_PATH`` 可覆盖），容器内 LLVM 22 + Nuitka 4.2.2 工具链。

栈本质是通用原生编译/wheel 打包平台：TVM 与 npuusertools 均为可改绑/可剥离
的默认挂载变体，命名不绑定任何可插拔依赖；当前默认产品为 xmnn wheel。
双 cp314 ABI 契约（C13，禁止互换）：base env /opt/conda = cp314 GIL（工具链
守卫/内核/打包解释器 BASE_PYTHON）；main env /opt/conda/envs/main = cp314t
free-threading（量化/运行时）。10 命令：build/up/down/ps/logs/smoke/save/load，
加长任务 build-tvm（栈内编译 TVM C++）、wheel（Nuitka 打 xmnn whl）。

四组可选能力（默认全关 = 默认隔离，C18）：
  - GPU：``up --gpu`` 叠加 ``compose.gpu.yaml``，设备经 ``GPU_DEVICE`` 双形态
    插值（``/`` 开头=设备路径，缺省 ``/dev/dri``；否则=CDI 引用）；
  - 透传：``--passthrough`` host 网络 + D-Bus 主层（Jupyter 固定 8888、SSH 2223，
    镜像切 :passthrough 自动 tag）；``--gui`` Wayland/X11 显示 socket（WSLg
    双通道、bridge 可用，C33）；``--usb`` USB 总线（先 usbipd attach）；缺失即 fail-fast；
  - torch：``build --torch cpu|cu130``（或 .env ``TORCH_FLAVOR``）才在 base env
    装对应 wheel，形态落 /opt/native-torch-flavor 供构建期守卫 §8 断言；
  - 离线：``up --offline``（或 .env ``NATIVE_OFFLINE=1``）只以本地已 load 镜像
    ``up --no-build``，并注入 ``NATIVE_OFFLINE=1`` 禁容器内联网。

平台姿态（内核统一）：Windows 原生优先透明桥接 WSL，不可桥接再门禁；POSIX
缺 podman-compose 提示 ``pip install -e ".[compose]"``。变量优先级：shell export
> root client .env（override=False）> compose.yaml 内 ${VAR:-default}。
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
    offline_exec_env,
    require_running,
    run_compose,
)

BUILDER_SCRIPTS = "/opt/native-builder/scripts"

NATIVE_SPEC = StackSpec(
    namespace="native",
    project="native-dev",
    service="native",
    overlay_subdir="native-dev",
    containerfile="Containerfile.native-dev",
    default_image_tag="localhost/native-dev:latest",
    default_base_image="localhost/jupyter-podman-rootless:latest",
    env_prefix="NATIVE",
    docs=TaskDocs(
        build="构建 native-dev 叠加镜像（main env LLVM 22 工具链 + base env Nuitka 打包栈）。",
        up="渲染并启动 native-dev 栈（podman-compose up -d，默认随带构建）。",
        down="停止并删除 native-dev 栈容器与网络（源码/workspace 绑定不受影响）。",
        ps="查看 native-dev 栈服务状态。",
        logs="跟踪 native-dev 栈服务日志（Ctrl+C 退出，不影响容器运行）。",
        smoke="运行 native-dev 冒烟：工具链守卫（始终）+ 源码挂载检查（栈运行时）。",
    ),
    down_volumes_help="同时删除 native-ccache / native-jupyter / native-ssh-host-keys 命名卷（默认保留：Nuitka 编译缓存 + Jupyter 登录态 + SSH 主机指纹）",
    ssh_default="2223",
    jupyter_default="8890",
    jupyter_banner_note="（内核：Python 3.14 (native dev)）",
    up_footer=(
        "[native]   状态: invoke native.ps    日志: invoke native.logs",
        "[native]   冒烟: invoke native.smoke",
        "[native]   编译 TVM: invoke native.build-tvm    打包 wheel: invoke native.wheel",
    ),
    gpu_override=True, gpu_device_env="GPU_DEVICE",
    passthrough_overlay=True, usb_overlay=True, gui_overlay=True,
    passthrough_tag_default="localhost/native-dev:passthrough",
    conda_mirror=True, torch_flavor=True, auto_shortflags=False,
    source_mounts=(
        SourceMount("NPU_TVM_PATH", "external/chaos/npu_tvm", "npu_tvm 源码树（含 python/tvm）"),
        SourceMount("NPUUSERTOOLS_PATH", "external/containers/workspace/dev/npuusertools", "npuusertools 源码树（含 xmnn 包）"),
        SourceMount("MODELS_PATH", "external/chaos/models", "模型目录"),
        # 临时目录（/workspace/temp）：缺省锚仓库根上溯四级 = 根工作区 .temp；
        # must_exist=False → 缺失幂等 mkdir（追加在末尾：既有用例锁 source_mounts[0]）。
        SourceMount("NATIVE_TEMP_PATH", "../../../../.temp", "临时目录（根工作区 .temp）", must_exist=False),
    ),
    smoke=SmokeSpec(
        python="/opt/conda/bin/python",
        smoke_dir="/opt/native-dev-smoke",
        exec_scripts=("_toolchain_guards.py", "smoke_mounts.py"),
        standalone_scripts=("_toolchain_guards.py",),
        running_note="检测到运行中的栈，经 compose exec 执行守卫与挂载冒烟：",
        standalone_note="栈未运行，使用一次性容器仅执行工具链守卫（挂载冒烟需先 up）：",
        done_message="冒烟通过",
    ),
    bridge_env_keys=(
        "NATIVE_IMAGE_TAG", "NATIVE_CONTAINER_NAME", "NATIVE_WORKSPACE",
        "NATIVE_SSH_PORT", "NATIVE_JUPYTER_PORT", "NATIVE_OFFLINE",
        "NPU_TVM_PATH", "NPUUSERTOOLS_PATH", "MODELS_PATH", "NATIVE_TEMP_PATH",
        "TORCH_FLAVOR", "GPU_DEVICE", "NATIVE_PASSTHROUGH_IMAGE_TAG",
        "DBUS_SESSION_BUS_PATH", "HOST_NET_SSHD_PORT", "USB_DEVICE",
        # GUI（C33）：仅转发用户可设键；末两键供 ssh -X 的 X11/TCP 形态；探测令牌不入桥接。
        "HOST_XDG_RUNTIME_DIR", "HOST_WAYLAND_DISPLAY", "GUI_X11_SOCKETDIR", "GUI_DISPLAY",
        "GUI_X11_TCP_DISPLAY", "GUI_XAUTHORITY_FILE",
    ),
    supports_offline=True,
)

TASKS = make_stack_tasks(NATIVE_SPEC)
build, up, down, ps, logs, smoke, save, load = (
    TASKS[k] for k in ("build", "up", "down", "ps", "logs", "smoke", "save", "load")
)

# 栈内 exec 长任务（build-tvm / wheel；产物落 /workspace，源码/workspace 绑定）
@task(
    help={
        "jobs": "Nuitka 并行任务数（映射 NUITKA_JOBS，默认读 compose env=8；内存不足用 4）",
        "clean": "CLEAN_REBUILD=1：禁用 ccache 全量重编（不清空缓存）",
        "tvm-flags": "透传给三次 Nuitka 调用的额外参数（映射 TVM_COMPILE_FLAGS，加引号）",
    },
    auto_shortflags=False,
)
def wheel(
    c: Context, jobs: int | None = None, clean: bool = False,
    tvm_flags: str | None = None,
) -> None:
    """栈内执行 Nuitka 全流程打包 xmnn whl（tvm→vta/xmnn→wheel，长任务）。

    产物落 /workspace/dist（宿主 workspace/dist）。前置：
    栈在运行且 /workspace/npu_tvm/build/libtvm.so 已就位（否则先 build-tvm）。
    """
    gates(NATIVE_SPEC)
    ensure_runtime_ready(NATIVE_SPEC)
    require_running(c, NATIVE_SPEC)
    extra: list[str] = []
    if jobs is not None:
        extra += ["-e", f"NUITKA_JOBS={int(jobs)}"]
    if clean:
        extra += ["-e", "CLEAN_REBUILD=1"]
    if tvm_flags:
        extra += ["-e", f"TVM_COMPILE_FLAGS={tvm_flags}"]
    run_compose(
        c, NATIVE_SPEC, "exec", *extra, *offline_exec_env(NATIVE_SPEC),
        "-T", NATIVE_SPEC.service,
        "bash", f"{BUILDER_SCRIPTS}/build-wheel.sh", pty=True,
    )
    print("[native] ✅ wheel 打包流程结束；产物目录：容器 /workspace/dist（宿主 workspace/dist）")
    print("[native]   10 项隔离验证（临时 venv，不污染源码环境）：")
    print(f"           podman-compose exec native bash {BUILDER_SCRIPTS}/verify-wheel.sh")


@task(auto_shortflags=False)
def build_tvm(c: Context) -> None:
    """栈内编译 TVM C++ 原生库（inv config -f + USE_EXAMPLE_TARGET_HOOKS + inv make）。"""
    gates(NATIVE_SPEC)
    ensure_runtime_ready(NATIVE_SPEC)
    require_running(c, NATIVE_SPEC)
    print("[native] 首次全量编译耗时较长（ccache 命中后增量很快）；Ctrl+C 不影响容器。")
    run_compose(
        c, NATIVE_SPEC, "exec", *offline_exec_env(NATIVE_SPEC), "-T", NATIVE_SPEC.service,
        "bash", f"{BUILDER_SCRIPTS}/build-tvm.sh", pty=True,
    )
