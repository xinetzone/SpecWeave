"""xmnn-dev 开发/打包叠加栈的 podman-compose 编排任务（opt-in 命名空间）。

定位（与 quant.py 同族，与 manage.py 边界一致）：
  - 本模块**禁止 import podman**，只通过子进程驱动 ``podman-compose``；
  - 驱动 ``overlays/xmnn-dev`` 叠加栈：运行时 bind 挂载 npu_tvm /
    npuusertools / models 源码，容器内具备 LLVM 22 + Nuitka 4.1.3 工具链，
    支持源码调试与 xmnn wheel 打包。

提供 8 个命令：
  invoke xmnn.build       构建叠加镜像（工具链 + 构建期守卫）
  invoke xmnn.up          渲染并启动栈（默认随带构建）
  invoke xmnn.down        停止并清理栈（--volumes 连 ccache 卷一起删）
  invoke xmnn.ps          查看栈服务状态
  invoke xmnn.logs        跟踪服务日志
  invoke xmnn.smoke       工具链守卫 + 源码挂载冒烟（双路径）
  invoke xmnn.build-tvm   栈内编译 TVM C++ 库（libtvm.so，长任务）
  invoke xmnn.wheel       栈内 Nuitka 打包 xmnn whl（长任务，产物落 workspace/dist）

平台姿态（同 quant.*）：Windows 原生 CPython 一律 Exit(1)；WSL2 发行版内或
``invoke env.run-cmd`` 自举容器内放行；POSIX 缺 podman-compose 提示装
``pip install -e ".[compose]"``。

环境变量优先级：shell 显式 export > root client .env（load_dotenv
override=False）> compose.yaml 内 ${VAR:-default}。
"""
import os
import platform
import shlex
import shutil
from pathlib import Path

from invoke import Context, task
from invoke.exceptions import Exit

from .manage import _load_env_overrides, _project_root
from .utils import (
    check_runtime_ready,
    detect_runtime,
    run_cmd,
    to_posix_path,
)

# ---------------------------------------------------------------------------
# 常量（compose 栈单一事实源；改目录/服务名时 compose.yaml 同步修改）
# ---------------------------------------------------------------------------
PROJECT_NAME = "xmnn-dev"
SERVICE_NAME = "xmnn"
DEFAULT_IMAGE_TAG = "localhost/xmnn-dev:latest"
DEFAULT_BASE_IMAGE = "localhost/jupyter-podman-rootless:latest"
BASE_PYTHON = "/opt/conda/bin/python"
SMOKE_DIR = "/opt/xmnn-dev-smoke"
GUARD_SCRIPT = "_toolchain_guards.py"
MOUNTS_SCRIPT = "smoke_mounts.py"
BUILDER_SCRIPTS = "/opt/xmnn-builder/scripts"
# podman-compose 项目标签（知识包 05：标签即数据库）
PROJECT_LABEL = "io.podman.compose.project"
SERVICE_LABEL = "io.podman.compose.service"

# 运行时 bind 挂载的三个源码目录（invoke cwd 为 client/，仓库根即其上两级）
_SOURCE_MOUNTS = {
    "NPU_TVM_PATH": ("external/chaos/npu_tvm", "npu_tvm 源码树（含 python/tvm）"),
    "NPUUSERTOOLS_PATH": ("external/chaos/npuusertools", "npuusertools 源码树（含 xmnn 包）"),
    "MODELS_PATH": ("external/chaos/models", "模型目录"),
}


def _overlay_dir() -> Path:
    """xmnn-dev 叠加层目录（compose.yaml / Containerfile.xmnn-dev 所在）。"""
    return _project_root() / "overlays" / "xmnn-dev"


# ---------------------------------------------------------------------------
# 平台 / 依赖门禁（任何 xmnn.* 任务入口先过门）
# ---------------------------------------------------------------------------


def _gate_platform() -> None:
    """Windows 原生直接门禁（WSL2 内 Python 报 Linux，自然放行）。"""
    if platform.system() != "Windows":
        return
    print("[xmnn] ⚠ Windows 原生 CPython 不支持 podman-compose 编排路径：")
    print("        podman-compose 以子进程方式工作，其短语法挂载/路径解析在")
    print("        Windows 原生存在已知缺陷。请改用：")
    print("        ① 在 WSL2 发行版内执行（推荐）：")
    print("           wsl -d <发行版>")
    print("           cd /mnt/d/spaces/SpecWeave/apps/containers/client")
    print('           pip install -e ".[compose]" && invoke xmnn.up')
    print("        ② 或进入 client 自举容器后执行（基底已内嵌 podman-compose）：")
    print("           invoke env.run-cmd --cmd 'inv xmnn.up'")
    raise Exit(1)


def _gate_compose_binary() -> None:
    """POSIX 宿主缺 podman-compose 时给可执行安装指引。"""
    if shutil.which("podman-compose") is not None:
        return
    print('[xmnn] ⚠ 未找到 podman-compose；本命名空间为声明式编排层，请先安装：')
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
        print(f"[xmnn] ⚠ {hint}")
        raise Exit(1)


# ---------------------------------------------------------------------------
# 配置解析
# ---------------------------------------------------------------------------


def _resolve_path(raw: str, *, must_exist: bool, label: str) -> str:
    """相对路径相对 invoke cwd 解析；转绝对 POSIX；可选存在性硬校验。"""
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    if must_exist and not p.exists():
        print(f"[xmnn] ⚠ {label}宿主路径不存在：{p}")
        print(f"        请在 .env / 环境变量中设置对应变量指向有效目录后重试。")
        raise Exit(1)
    return to_posix_path(p)


def _prepare_env() -> dict:
    """加载 root .env（override=False），把 workspace 与三源码路径解析为
    绝对 POSIX 路径注入子进程环境（与 quant.py 同一 Dimension A 复用）。"""
    env = _load_env_overrides(_project_root())
    root = _project_root()

    ws = os.environ.get("XMNN_WORKSPACE") or env.get("XMNN_WORKSPACE")
    if not ws:
        ws = str((root / "workspace").resolve())
    ws_path = Path(ws).expanduser()
    if not ws_path.is_absolute():
        ws_path = (Path.cwd() / ws_path).resolve()
    ws_path.mkdir(parents=True, exist_ok=True)
    os.environ["XMNN_WORKSPACE"] = to_posix_path(ws_path)

    for var, (default_rel, label) in _SOURCE_MOUNTS.items():
        raw = os.environ.get(var) or env.get(var) or str((root / default_rel).resolve())
        os.environ[var] = _resolve_path(raw, must_exist=True, label=label)

    return env


def _image_tag(env: dict) -> str:
    return str(os.environ.get("XMNN_IMAGE_TAG") or env.get("XMNN_IMAGE_TAG") or DEFAULT_IMAGE_TAG)


def _compose_argv(*tail: str) -> list[str]:
    """组装 podman-compose 公共 argv（固定 project name，-f 绝对路径）。"""
    overlay = _overlay_dir()
    argv = [
        "podman-compose", "--project-name", PROJECT_NAME,
        "--file", str(overlay / "compose.yaml"),
    ]
    argv.extend(tail)
    return argv


def _run_compose(c: Context, *tail: str, pty: bool = True) -> None:
    run_cmd(c, " ".join(shlex.quote(a) for a in _compose_argv(*tail)), pty=pty)


# ---------------------------------------------------------------------------
# 任务：镜像构建
# ---------------------------------------------------------------------------


@task(
    help={
        "tag": "产出镜像标签，默认 localhost/xmnn-dev:latest",
        "base-image": "基底镜像，默认 localhost/jupyter-podman-rootless:latest",
        "pip-mirror": "构建期 pip 镜像源：official|aliyun|tuna。注意：独立 xmnn.build 只认本参数；.env 的 PIP_MIRROR 仅在 xmnn.up 的 compose 内联 build 时插值生效",
        "conda-mirror": "构建期 conda 镜像源：official|aliyun|tuna；口径同 --pip-mirror（.env 经 xmnn.up 生效）",
        "no-cache": "等价 podman build --no-cache（强制全量重建）",
    },
    auto_shortflags=False,
)
def build(
    c: Context,
    tag: str | None = None,
    base_image: str = DEFAULT_BASE_IMAGE,
    pip_mirror: str = "official",
    conda_mirror: str = "official",
    no_cache: bool = False,
) -> None:
    """构建 xmnn-dev 叠加镜像（main env LLVM 22 工具链 + base env Nuitka 打包栈）。"""
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    runtime = detect_runtime()
    image_tag = tag or _image_tag(env)
    overlay = _overlay_dir()
    containerfile = overlay / "Containerfile.xmnn-dev"
    if not containerfile.exists():
        raise Exit(1, f"未找到 {containerfile}")

    chk = run_cmd(
        c,
        f"{runtime} image exists {base_image}",
        hide=True, warn=True, echo=False,
    )
    if chk is None or not getattr(chk, "ok", False):
        print(f"[xmnn] ⚠ 本地缺少基底镜像 {base_image}")
        print("[xmnn]   先执行: invoke load   （从构建端缓存加载 rootless 基底）")
        raise Exit(1)

    parts = [
        runtime, "build",
        f"-f {shlex.quote(str(containerfile))}",
        f"--build-arg BASE_IMAGE={shlex.quote(base_image)}",
        f"--build-arg PIP_MIRROR={shlex.quote(pip_mirror)}",
        f"--build-arg CONDA_MIRROR={shlex.quote(conda_mirror)}",
        f"-t {shlex.quote(image_tag)}",
    ]
    if no_cache:
        parts.append("--no-cache")
    parts.append(shlex.quote(str(overlay)))
    run_cmd(c, " ".join(parts), pty=True)
    print(f"[xmnn] ✅ 叠加镜像构建完成: {image_tag}")
    print("[xmnn]   下一步: invoke xmnn.up")


# ---------------------------------------------------------------------------
# 任务：栈生命周期
# ---------------------------------------------------------------------------


@task(help={"skip-build": "跳过启动前的镜像构建（默认每次 up 随带构建跟随层更新）"},
      auto_shortflags=False)
def up(c: Context, skip_build: bool = False) -> None:
    """渲染并启动 xmnn-dev 栈（podman-compose up -d，默认随带构建）。"""
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    if not skip_build:
        build(c)
    _run_compose(c, "up", "-d")
    ssh_port = os.environ.get("XMNN_SSH_PORT", env.get("XMNN_SSH_PORT", "2223"))
    jupyter_port = os.environ.get("XMNN_JUPYTER_PORT", env.get("XMNN_JUPYTER_PORT", "8890"))
    print("[xmnn] ✅ 栈已启动：")
    print(f"        SSH     localhost:{ssh_port}")
    print(f"        Jupyter localhost:{jupyter_port}（内核：Python 3.14 (xmnn dev)）")
    print("[xmnn]   状态: invoke xmnn.ps    日志: invoke xmnn.logs")
    print("[xmnn]   冒烟: invoke xmnn.smoke")
    print("[xmnn]   编译 TVM: invoke xmnn.build-tvm    打包 wheel: invoke xmnn.wheel")


@task(help={"volumes": "同时删除 xmnn-ccache 命名卷（默认保留以加速重复打包）"},
      auto_shortflags=False)
def down(c: Context, volumes: bool = False) -> None:
    """停止并删除 xmnn-dev 栈容器与网络（源码/workspace 绑定不受影响）。"""
    _gate_all()
    tail = ["down"]
    if volumes:
        tail.append("--volumes")
    _run_compose(c, *tail)
    print("[xmnn] ✅ 栈已停止并清理（ccache 卷默认保留）")


@task
def ps(c: Context) -> None:
    """查看 xmnn-dev 栈服务状态。"""
    _gate_all()
    _run_compose(c, "ps", pty=False)


@task(help={"tail": "显示最近 N 行后持续跟踪（默认 100）"}, auto_shortflags=False)
def logs(c: Context, tail: int = 100) -> None:
    """跟踪 xmnn-dev 栈服务日志（Ctrl+C 退出，不影响容器运行）。"""
    _gate_all()
    _run_compose(c, "logs", "--follow", f"--tail={tail}")


# ---------------------------------------------------------------------------
# 任务：栈内开发/打包操作
# ---------------------------------------------------------------------------


def _xmnn_container_running(c: Context) -> bool:
    """通过 compose 项目标签判断 xmnn 服务容器是否在运行。"""
    runtime = detect_runtime()
    r = run_cmd(
        c,
        (
            f"{runtime} ps -q "
            f"--filter label={PROJECT_LABEL}={PROJECT_NAME} "
            f"--filter label={SERVICE_LABEL}={SERVICE_NAME}"
        ),
        hide=True, warn=True, echo=False,
    )
    return bool(r is not None and getattr(r, "ok", False) and (r.stdout or "").strip())


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
    _gate_all()
    _ensure_runtime_ready()
    if not _xmnn_container_running(c):
        print("[xmnn] ⚠ xmnn-dev 栈未运行，请先：invoke xmnn.up")
        raise Exit(1)
    extra: list[str] = []
    if jobs is not None:
        extra += ["-e", f"NUITKA_JOBS={int(jobs)}"]
    if clean:
        extra += ["-e", "CLEAN_REBUILD=1"]
    if tvm_flags:
        extra += ["-e", f"TVM_COMPILE_FLAGS={tvm_flags}"]
    _run_compose(
        c, "exec", *extra, "-T", SERVICE_NAME,
        "bash", f"{BUILDER_SCRIPTS}/build-wheel.sh",
        pty=True,
    )
    print("[xmnn] ✅ wheel 打包流程结束；产物目录：容器 /workspace/dist（宿主 workspace/dist）")
    print("[xmnn]   10 项隔离验证（临时 venv，不污染源码环境）：")
    print(f"           podman-compose exec xmnn bash {BUILDER_SCRIPTS}/verify-wheel.sh")


@task(auto_shortflags=False)
def build_tvm(c: Context) -> None:
    """栈内编译 TVM C++ 原生库（inv config -f + USE_EXAMPLE_TARGET_HOOKS + inv make）。"""
    _gate_all()
    _ensure_runtime_ready()
    if not _xmnn_container_running(c):
        print("[xmnn] ⚠ xmnn-dev 栈未运行，请先：invoke xmnn.up")
        raise Exit(1)
    print("[xmnn] 首次全量编译耗时较长（ccache 命中后增量很快）；Ctrl+C 不影响容器。")
    _run_compose(
        c, "exec", "-T", SERVICE_NAME,
        "bash", f"{BUILDER_SCRIPTS}/build-tvm.sh",
        pty=True,
    )


# ---------------------------------------------------------------------------
# 任务：冒烟（栈运行→compose exec 双脚本；未运行→run --rm 仅工具链守卫）
# ---------------------------------------------------------------------------


@task(auto_shortflags=False)
def smoke(c: Context) -> None:
    """运行 xmnn-dev 冒烟：工具链守卫（始终）+ 源码挂载检查（栈运行时）。"""
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    image_tag = _image_tag(env)
    runtime = detect_runtime()

    if _xmnn_container_running(c):
        print("[xmnn] 检测到运行中的栈，经 compose exec 执行守卫与挂载冒烟：")
        _run_compose(
            c, "exec", "-T", SERVICE_NAME,
            BASE_PYTHON, f"{SMOKE_DIR}/{GUARD_SCRIPT}",
            pty=False,
        )
        _run_compose(
            c, "exec", "-T", SERVICE_NAME,
            BASE_PYTHON, f"{SMOKE_DIR}/{MOUNTS_SCRIPT}",
            pty=False,
        )
    else:
        print("[xmnn] 栈未运行，使用一次性容器仅执行工具链守卫（挂载冒烟需先 up）：")
        run_cmd(
            c,
            " ".join([
                runtime, "run", "--rm",
                "--entrypoint", BASE_PYTHON,
                shlex.quote(image_tag),
                f"{SMOKE_DIR}/{GUARD_SCRIPT}",
            ]),
            pty=True,
        )
    print("[xmnn] ✅ 冒烟通过")
