"""onnx-quantized 工作负载叠加栈的 podman-compose 编排任务（opt-in 命名空间）。

本模块是**声明式栈**：唯一事实源是 ``QUANT_SPEC``（StackSpec），六个任务
（build/up/down/ps/logs/smoke）全部由 overlay_core.make_stack_tasks 工厂生成；
同构门控/argv/残留自愈/冒烟双路径逻辑不在本模块重复（AC-5）。

定位（与 manage.py / env_in_container.py 的边界）：
  - manage.py：podman-py SDK（优先）→ CLI fallback，管「单个容器」生命周期，
    不感知 compose；本栈**禁止 import podman**，只通过子进程驱动
    ``podman-compose``（声明式栈，参考 OKF podman-compose 知识包）。
  - env_in_container.py：client SDK 自举叠加层；本模块管的是「量化工作负载」
    叠加镜像（overlays/onnx-quantized，FROM rootless 基底）。

提供 6 个命令：
  invoke quant.build  构建量化叠加镜像（podman build 薄封装）
  invoke quant.up     渲染并启动栈（podman-compose up -d，默认随带构建）
  invoke quant.down   停止并清理栈（podman-compose down）
  invoke quant.ps     查看栈服务状态
  invoke quant.logs   跟踪服务日志
  invoke quant.smoke  运行 3 个纯 ONNX 冒烟（运行栈 exec 优先，否则 run --rm）

平台姿态（内核统一实现）：Windows 原生 CPython 优先透明桥接 WSL 发行版
（run_in_wsl_bridge），不可桥接再门禁；POSIX 缺 podman-compose 提示安装
``pip install -e ".[compose]"``。

环境变量优先级：shell 显式 export > root client .env（load_dotenv override=False）
> compose.yaml 内 ${VAR:-default}；overlay 自身 .env 仅供「裸 podman-compose」使用。
"""
from __future__ import annotations

from .overlay_core import SmokeSpec, StackSpec, TaskDocs, make_stack_tasks

QUANT_SPEC = StackSpec(
    namespace="quant",
    project="onnx-quantized",
    service="quant",
    overlay_subdir="onnx-quantized",
    containerfile="Containerfile.quantized",
    default_image_tag="localhost/onnx-quantized:latest",
    default_base_image="localhost/jupyter-podman-rootless:latest",
    env_prefix="QUANT",
    docs=TaskDocs(
        build="构建 ONNX 量化叠加镜像（构建期自动执行守卫与 3 个冒烟测试）。",
        up="渲染并启动量化栈（podman-compose up -d，默认随带构建）。",
        down="停止并删除量化栈容器与网络（workspace 绑定数据不受影响）。",
        ps="查看量化栈服务状态。",
        logs="跟踪量化栈服务日志（Ctrl+C 退出，不影响容器运行）。",
        smoke="运行 3 个纯 ONNX 冒烟（动态 INT8 / FP16 / 静态 QDQ）。",
    ),
    down_volumes_help="同时删除栈关联的匿名/命名卷（默认不删 workspace 绑定）",
    ssh_default="2222",
    jupyter_default="8888",
    build_done_label="量化叠加镜像",
    build_next_hint="（启动声明式栈）",
    gpu_override=True,
    conda_mirror=False,
    auto_shortflags=True,
    smoke=SmokeSpec(
        python="/opt/conda/envs/main/bin/python",
        smoke_dir="/opt/onnx-quantized-smoke",
        exec_scripts=(
            "smoke_dynamic_int8.py",
            "smoke_fp16.py",
            "smoke_static_qdq.py",
        ),
        standalone_scripts=(
            "smoke_dynamic_int8.py",
            "smoke_fp16.py",
            "smoke_static_qdq.py",
        ),
        running_note="检测到运行中的栈，经 compose exec 执行冒烟：",
        standalone_note="栈未运行，使用一次性容器执行冒烟：",
        done_message="3 个冒烟全部通过（dynamic INT8 / FP16 / static QDQ）",
    ),
    # WSL 桥接透传的栈专属键（通用键由 run_in_wsl_bridge 内置，F-10）
    bridge_env_keys=(
        "QUANT_IMAGE_TAG", "QUANT_CONTAINER_NAME", "QUANT_WORKSPACE",
        "QUANT_SSH_PORT", "QUANT_JUPYTER_PORT",
    ),
)

TASKS = make_stack_tasks(QUANT_SPEC)
build = TASKS["build"]
up = TASKS["up"]
down = TASKS["down"]
ps = TASKS["ps"]
logs = TASKS["logs"]
smoke = TASKS["smoke"]
