"""onnx-quantized 工作负载叠加栈的 podman-compose 编排任务（opt-in 命名空间）。

定位（与 manage.py / env_in_container.py 的边界）：
  - manage.py：podman-py SDK（优先）→ CLI fallback，管「单个容器」生命周期，
    不感知 compose；本模块**禁止 import podman**，只通过子进程驱动
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

平台姿态（对齐构建端 Windows 门禁经验）：
  - Windows 原生 CPython 一律门禁：podman-compose 子进程 + 短语法 os.makedirs
    在 Windows 原生有已知缺陷；请在 WSL2 发行版内运行，或经
    ``invoke env.run-cmd`` 进入自举容器（基底已内嵌 podman-compose）后运行。
  - POSIX 宿主缺 podman-compose 二进制：提示安装可选依赖
    ``pip install -e ".[compose]"`` 后退出。

环境变量优先级：shell 显式 export > root client .env（load_dotenv override=False）
> compose.yaml 内 ${VAR:-default}；overlay 自身 .env 仅供「裸 podman-compose」使用。
"""
import os
import platform
import shutil
from pathlib import Path

from invoke import Context, task
from invoke.exceptions import Exit

from .manage import _load_env_overrides, _project_root
from .utils import (
    check_runtime_ready,
    detect_runtime,
    ensure_workspace_checkpoint_writable,
    run_cmd,
    run_in_wsl_bridge,
    to_posix_path,
)

# ---------------------------------------------------------------------------
# 常量（compose 栈单一事实源；改目录/服务名时 compose.yaml 同步修改）
# ---------------------------------------------------------------------------
PROJECT_NAME = "onnx-quantized"
SERVICE_NAME = "quant"
DEFAULT_IMAGE_TAG = "localhost/onnx-quantized:latest"
DEFAULT_BASE_IMAGE = "localhost/jupyter-podman-rootless:latest"
MAIN_PYTHON = "/opt/conda/envs/main/bin/python"
SMOKE_DIR = "/opt/onnx-quantized-smoke"
SMOKE_SCRIPTS = (
    "smoke_dynamic_int8.py",
    "smoke_fp16.py",
    "smoke_static_qdq.py",
)
# podman-compose 给栈资源打的项目标签（知识包 05：标签即数据库；SDK/CLI 接缝）
PROJECT_LABEL = "io.podman.compose.project"
SERVICE_LABEL = "io.podman.compose.service"


def _overlay_dir() -> Path:
    """量化叠加层目录（compose.yaml / Containerfile.quantized 所在）。"""
    return _project_root() / "overlays" / "onnx-quantized"


# ---------------------------------------------------------------------------
# 平台 / 依赖门禁（AC-5；任何 quant.* 任务入口先过这道门）
# ---------------------------------------------------------------------------


def _gate_platform() -> None:
    """Windows 原生：优先透明桥接到 WSL 发行版执行；不可桥接再门禁。

    2026-09-15 起桥接优先（本质目标 = Windows 原生输入 inv quant.build 即可正确
    构建，而非被动门禁）。run_in_wsl_bridge 成功即已把本任务在
    jupyter-podman-rootless（或 COMPOSE_WSL_DISTRO 指定发行版）内完整执行，
    本进程 Exit(0) 收尾（WSL2 内 Python 报 Linux 自然放行，不进入本分支）。
    """
    if platform.system() != "Windows":
        return
    distro = run_in_wsl_bridge()
    if distro is not None:
        print(f"[quant] ✅ 已经 WSL 发行版 {distro} 桥接执行；如需栈长驻请保持会话：")
        print(f"        wsl -d {distro} -- sleep infinity")
        raise Exit(0)
    client_posix = to_posix_path(_project_root())
    print("[quant] ⚠ Windows 原生 CPython 不支持 podman-compose 编排路径（其短语法")
    print("        挂载/路径解析在 Windows 原生存在已知缺陷），且未能自动桥接至")
    print("        WSL 发行版。请检查：")
    print("          · WSL 发行版可启动（wsl --list --verbose），或设置")
    print("            COMPOSE_WSL_DISTRO=<发行版> 指定桥接目标（none=关闭桥接）")
    print("          · 发行版内已安装 client 与 compose 依赖：")
    print(f"            cd {client_posix} && pip install -e \".[compose]\"")
    print("        放行方式二选一：")
    print("        ① 在 WSL2 发行版内手动执行（推荐）：")
    print("           wsl -d <发行版>")
    print(f"           cd {client_posix}")
    print('           pip install -e ".[compose]" && invoke quant.up')
    print("        ② 或进入 client 自举容器后执行（基底已内嵌 podman-compose）：")
    print("           invoke env.run-cmd --cmd 'inv quant.up'")
    raise Exit(1)


def _gate_compose_binary() -> None:
    """POSIX 宿主缺 podman-compose 时给可执行安装指引。"""
    if shutil.which("podman-compose") is not None:
        return
    print('[quant] ⚠ 未找到 podman-compose；本命名空间为声明式编排层，请先安装：')
    print('         pip install -e ".[compose]"')
    print("        （rootless 基底镜像内已内置；亦可 `invoke env.run-cmd` 在容器内执行）")
    raise Exit(1)


def _gate_all() -> None:
    _gate_platform()
    _gate_compose_binary()


def _ensure_runtime_ready() -> None:
    """daemon 预检（machine 未运行时的提示先于镜像/构建误报）。"""
    ready, hint = check_runtime_ready()
    if not ready:
        print(f"[quant] ⚠ {hint}")
        raise Exit(1)


# ---------------------------------------------------------------------------
# 配置解析
# ---------------------------------------------------------------------------


def _prepare_env() -> dict:
    """加载 root .env（override=False，副作用同步 os.environ）并补全默认值。

    关键动作：把 QUANT_WORKSPACE 解析为绝对 POSIX 路径注入子进程环境——
    compose 任务可能从任意 cwd 调用，不能依赖 compose.yaml 内相对路径
    （../../workspace 是相对 compose 文件目录的裸 compose 默认）。
    """
    env = _load_env_overrides(_project_root())

    ws = os.environ.get("QUANT_WORKSPACE") or env.get("QUANT_WORKSPACE")
    if not ws:
        ws = str((_project_root() / "workspace").resolve())
    ws_path = Path(ws).expanduser()
    if not ws_path.is_absolute():
        # 相对路径相对 invoke 执行目录解析（与 compose 文件目录默认值语义不同，
        # 任务路径以用户 cwd 为基准更符合直觉）
        ws_path = (Path.cwd() / ws_path).resolve()
    ws_path.mkdir(parents=True, exist_ok=True)
    # 同 xmnn 栈：rootless+9p/drvfs 下保证 Jupyter(devuser) 可写 checkpoint 目录
    ensure_workspace_checkpoint_writable(ws_path)
    os.environ["QUANT_WORKSPACE"] = to_posix_path(ws_path)
    return env


def _image_tag(env: dict) -> str:
    return str(os.environ.get("QUANT_IMAGE_TAG") or env.get("QUANT_IMAGE_TAG") or DEFAULT_IMAGE_TAG)


def _compose_argv(gpu: bool, *tail: str) -> list[str]:
    """组装 podman-compose 公共 argv（固定 project name，-f 绝对路径）。"""
    overlay = _overlay_dir()
    files = [overlay / "compose.yaml"]
    if gpu:
        files.append(overlay / "compose.gpu.yaml")
    argv = ["podman-compose", "--project-name", PROJECT_NAME]
    for f in files:
        argv += ["--file", str(f)]
    argv += list(tail)
    return argv


def _run_compose(c: Context, gpu: bool, *tail: str, pty: bool = True) -> None:
    """执行 podman-compose 子进程（命令以单参数串拼接，路径含空格也安全）。"""
    argv = _compose_argv(gpu, *tail)
    run_cmd(c, " ".join(argv), pty=pty)


# ---------------------------------------------------------------------------
# 任务：镜像构建（podman build 薄封装；不引入 compose build 的额外黑盒）
# ---------------------------------------------------------------------------


@task(
    help={
        "tag": "产出镜像标签，默认 localhost/onnx-quantized:latest（或 root .env QUANT_IMAGE_TAG）",
        "base-image": "基底镜像（Containerfile ARG BASE_IMAGE），默认 localhost/jupyter-podman-rootless:latest",
        "pip-mirror": "构建期 pip 镜像源：official|aliyun|tuna（默认 official）",
        "no-cache": "等价 podman build --no-cache（强制全量重建）",
    }
)
def build(
    c: Context,
    tag: str | None = None,
    base_image: str = DEFAULT_BASE_IMAGE,
    pip_mirror: str = "official",
    no_cache: bool = False,
) -> None:
    """构建 ONNX 量化叠加镜像（构建期自动执行守卫与 3 个冒烟测试）。"""
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    runtime = detect_runtime()
    image_tag = tag or _image_tag(env)
    overlay = _overlay_dir()
    containerfile = overlay / "Containerfile.quantized"
    if not containerfile.exists():
        raise Exit(1, f"未找到 {containerfile}")

    # 基底存在性预检（错误前置，避免 FROM 失败时裸报堆栈）
    chk = run_cmd(
        c,
        f"{runtime} image exists {base_image}",
        hide=True,
        warn=True,
        echo=False,
    )
    if chk is None or not getattr(chk, "ok", False):
        print(f"[quant] ⚠ 本地缺少基底镜像 {base_image}")
        print("[quant]   先执行: invoke load   （从构建端缓存加载 rootless 基底）")
        raise Exit(1)

    parts = [
        runtime,
        "build",
        f"-f {containerfile}",
        f"--build-arg BASE_IMAGE={base_image}",
        f"--build-arg PIP_MIRROR={pip_mirror}",
        f"-t {image_tag}",
    ]
    if no_cache:
        parts.append("--no-cache")
    parts.append(str(overlay))
    run_cmd(c, " ".join(parts), pty=True)
    print(f"[quant] ✅ 量化叠加镜像构建完成: {image_tag}")
    print("[quant]   下一步: invoke quant.up    （启动声明式栈）")


# ---------------------------------------------------------------------------
# 任务：栈生命周期
# ---------------------------------------------------------------------------


# 注意：up 内联构建只按默认参数执行，不透传 PIP_MIRROR/tag/base-image；
# 需要 pip 镜像源或自定义基底时先走 `invoke quant.build --pip-mirror tuna ...`
# 再 `invoke quant.up --skip-build`（两步路径见 overlay README）。
@task(
    help={
        "gpu": "叠加 compose.gpu.yaml（透传 /dev/dri；默认隔离不透传 GPU）",
        "skip-build": "跳过启动前的镜像构建（默认每次 up 都随带构建跟随层更新）",
    }
)
def up(c: Context, gpu: bool = False, skip_build: bool = False) -> None:
    """渲染并启动量化栈（podman-compose up -d，默认随带构建）。"""
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    if not skip_build:
        # invoke task 对象可直接以 Context 调用；复用 build 的全部预检与门禁
        build(c)
    # up 前自愈：Created/Exited 残留容器持有 2222/8888 端口分配致 up 失败
    _reconcile_stale_containers(c)
    tail = ["up", "-d"]
    _run_compose(c, gpu, *tail)
    print("[quant] ✅ 栈已启动：")
    print(f"        SSH     localhost:{os.environ.get('QUANT_SSH_PORT', env.get('QUANT_SSH_PORT', '2222'))}")
    print(f"        Jupyter localhost:{os.environ.get('QUANT_JUPYTER_PORT', env.get('QUANT_JUPYTER_PORT', '8888'))}")
    if gpu:
        print("        GPU     /dev/dri 已透传（compose.gpu.yaml）")
    print("[quant]   状态: invoke quant.ps    日志: invoke quant.logs    冒烟: invoke quant.smoke")


@task(help={"volumes": "同时删除栈关联的匿名/命名卷（默认不删 workspace 绑定）"})
def down(c: Context, volumes: bool = False) -> None:
    """停止并删除量化栈容器与网络（workspace 绑定数据不受影响）。"""
    _gate_all()
    tail = ["down"]
    if volumes:
        tail.append("--volumes")
    _run_compose(c, False, *tail)
    print("[quant] ✅ 栈已停止并清理")


@task
def ps(c: Context) -> None:
    """查看量化栈服务状态。"""
    _gate_all()
    _run_compose(c, False, "ps", pty=False)


@task(help={"tail": "显示最近 N 行后持续跟踪（默认 100）"})
def logs(c: Context, tail: int = 100) -> None:
    """跟踪量化栈服务日志（Ctrl+C 退出，不影响容器运行）。"""
    _gate_all()
    _run_compose(c, False, "logs", "--follow", f"--tail={tail}")


# ---------------------------------------------------------------------------
# 任务：冒烟测试（运行栈 exec 优先；栈未运行则 podman run --rm 一次性容器）
# ---------------------------------------------------------------------------


def _quant_container_running(c: Context) -> bool:
    """通过 compose 项目标签判断 quant 服务容器是否在运行（SDK 接缝，CLI 实现）。"""
    runtime = detect_runtime()
    r = run_cmd(
        c,
        (
            f"{runtime} ps -q "
            f"--filter label={PROJECT_LABEL}={PROJECT_NAME} "
            f"--filter label={SERVICE_LABEL}={SERVICE_NAME}"
        ),
        hide=True,
        warn=True,
        echo=False,
    )
    return bool(r is not None and getattr(r, "ok", False) and (r.stdout or "").strip())


def _reconcile_stale_containers(c: Context) -> None:
    """up 前清理 compose 项目残留的非 running 容器（Created/Exited 持有
    rootlessport 端口分配致 up bind 2222/8888 报 address already in use，
    2026-09-15 实证同 xmnn 栈）。down 不删镜像/ccache 卷/workspace/源码 bind。"""
    runtime = detect_runtime()
    r = run_cmd(
        c,
        (
            f"{runtime} ps -a -q "
            f"--filter label={PROJECT_LABEL}={PROJECT_NAME} "
            "--filter status=created --filter status=exited"
        ),
        hide=True, warn=True, echo=False,
    )
    stale = bool(r is not None and getattr(r, "ok", False) and (r.stdout or "").strip())
    if not stale:
        return
    print("[quant] ⚠ 检测到项目残留容器（Created/Exited 持有 2222/8888 端口分配），")
    print("[quant]   先 compose down 清理（保留 ccache 卷/workspace/源码）后重新 up …")
    _run_compose(c, False, "down")
    print("[quant] ✅ 残留已清理，继续 up")


@task(help={"gpu": "运行栈经 compose 启动时是否带 GPU 覆盖（仅影响 exec 寻址，不影响冒烟本身）"})
def smoke(c: Context, gpu: bool = False) -> None:
    """运行 3 个纯 ONNX 冒烟（动态 INT8 / FP16 / 静态 QDQ）。

    栈在运行 → ``podman-compose exec`` 进服务容器执行；
    栈未运行 → ``podman run --rm --entrypoint <main python> <镜像> <脚本>``
    起一次性容器执行（纯 CPU 计算，无需 GPU/透传开关）。
    """
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    image_tag = _image_tag(env)
    runtime = detect_runtime()

    if _quant_container_running(c):
        print("[quant] 检测到运行中的栈，经 compose exec 执行冒烟：")
        for script in SMOKE_SCRIPTS:
            _run_compose(
                c,
                gpu,
                "exec",
                "-T",
                SERVICE_NAME,
                MAIN_PYTHON,
                f"{SMOKE_DIR}/{script}",
                pty=False,
            )
    else:
        print("[quant] 栈未运行，使用一次性容器执行冒烟：")
        for script in SMOKE_SCRIPTS:
            run_cmd(
                c,
                " ".join(
                    [
                        runtime,
                        "run",
                        "--rm",
                        "--entrypoint",
                        MAIN_PYTHON,
                        image_tag,
                        f"{SMOKE_DIR}/{script}",
                    ]
                ),
                pty=True,
            )
    print("[quant] ✅ 3 个冒烟全部通过（dynamic INT8 / FP16 / static QDQ）")
