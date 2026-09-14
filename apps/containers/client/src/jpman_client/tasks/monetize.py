"""agent-monetize-dev 工作负载叠加栈的 podman-compose 编排任务（opt-in 命名空间）。

由 client-overlay-scaffold 骨架生成。替换全部 __X__ 占位符：
  monetize 命名空间（Collection 名）/ agent-monetize-dev 栈目录/project name /
  monetize compose 服务名 / MONETIZE env 前缀（如 QUANT/XMNN）/
  localhost/agent-monetize-dev:latest 默认镜像标签 / 2224 8892 默认端口。

定位（红线）：
  - 本模块**禁止 import podman**，只通过子进程驱动 podman-compose；
  - 与根 SDK→CLI 两层平行，禁止回流 invoke run；
  - Windows 原生 CPython 一律门禁 Exit(1)（WSL2/自举容器双路径放行）。

形态 B 的 exec 长任务（编译/打包）参考 xmnn.py 的 build-tvm/wheel 任务，
在标注位置追加；本骨架只含 6 个生命周期/冒烟任务（形态 A 即完整）。
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
    ensure_workspace_checkpoint_writable,
    run_cmd,
    to_posix_path,
)

# 常量（compose 栈单一事实源；改目录/服务名时 compose.yaml 同步）
PROJECT_NAME = "agent-monetize-dev"
SERVICE_NAME = "monetize"
DEFAULT_IMAGE_TAG = "localhost/agent-monetize-dev:latest"
DEFAULT_BASE_IMAGE = "localhost/jupyter-podman-rootless:latest"
# podman-compose 项目标签（知识包 05：标签即数据库）
PROJECT_LABEL = "io.podman.compose.project"
SERVICE_LABEL = "io.podman.compose.service"

# 运行时存在性硬校验的宿主源码路径。
# 默认值锚定**仓库根**（_project_root().parents[2]，即 client→containers→
# apps→根），不是 client 目录；与 xmnn.py _SOURCE_MOUNTS 同型（G：路径层级）。
_SOURCE_MOUNTS = {
    "MONETIZE_SRC_PATH": ("apps/agent-monetize", "agent-monetize 源码树"),
}


def _overlay_dir() -> Path:
    """agent-monetize-dev 叠加层目录（compose.yaml / Containerfile 所在）。"""
    return _project_root() / "overlays" / "agent-monetize-dev"


# ---------------------------------------------------------------------------
# 平台 / 依赖门禁（任何 monetize.* 任务入口先过门）
# ---------------------------------------------------------------------------

def _gate_platform() -> None:
    if platform.system() != "Windows":
        return
    print("[monetize] ⚠ Windows 原生 CPython 不支持 podman-compose 编排路径：")
    print("        podman-compose 以子进程方式工作，其短语法挂载/路径解析在")
    print("        Windows 原生存在已知缺陷。请改用：")
    print("        ① 在 WSL2 发行版内执行（推荐）：")
    print("           wsl -d <发行版>")
    print("           cd /mnt/d/spaces/SpecWeave/apps/containers/client")
    print('           pip install -e ".[compose]" && invoke monetize.up')
    print("        ② 或进入 client 自举容器后执行（基底已内嵌 podman-compose）：")
    print("           invoke env.run-cmd --cmd 'inv monetize.up'")
    raise Exit(1)


def _gate_compose_binary() -> None:
    if shutil.which("podman-compose") is not None:
        return
    print('[monetize] ⚠ 未找到 podman-compose；本命名空间为声明式编排层，请先安装：')
    print('         pip install -e ".[compose]"')
    print("        （rootless 基底镜像内已内置；亦可 `invoke env.run-cmd` 在容器内执行）")
    raise Exit(1)


def _gate_all() -> None:
    _gate_platform()
    _gate_compose_binary()


def _ensure_runtime_ready() -> None:
    ready, hint = check_runtime_ready()
    if not ready:
        print(f"[monetize] ⚠ {hint}")
        raise Exit(1)


# ---------------------------------------------------------------------------
# 配置解析
# ---------------------------------------------------------------------------

def _prepare_env() -> dict:
    """加载 root .env（override=False）；workspace 解析为绝对 POSIX 注入；
    形态 B 的源码路径在 _SOURCE_MOUNTS 存在时做存在性硬校验。"""
    env = _load_env_overrides(_project_root())
    root = _project_root()
    # 仓库根 = client 上三级（client → containers → apps → 根）；
    # apps/agent-monetize 默认值锚定仓库根，不是 client 目录。
    repo_root = root.parents[2]

    ws = os.environ.get("MONETIZE_WORKSPACE") or env.get("MONETIZE_WORKSPACE")
    if not ws:
        ws = str((root / "workspace").resolve())
    ws_path = Path(ws).expanduser()
    if not ws_path.is_absolute():
        ws_path = (Path.cwd() / ws_path).resolve()
    ws_path.mkdir(parents=True, exist_ok=True)
    # 同 xmnn/quant 栈：rootless+9p/drvfs 下保证 Jupyter(devuser) 可写
    # checkpoint 目录（三栈共享 client/workspace，幂等且只作用该单一目录）
    ensure_workspace_checkpoint_writable(ws_path)
    os.environ["MONETIZE_WORKSPACE"] = to_posix_path(ws_path)

    for var, (default_rel, label) in list(globals().get("_SOURCE_MOUNTS", {}).items()):
        raw = os.environ.get(var) or env.get(var) or str((repo_root / default_rel).resolve())
        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        if not p.exists():
            print(f"[monetize] ⚠ {label}宿主路径不存在：{p}")
            print("        请在 .env / 环境变量中设置对应变量指向有效目录后重试。")
            raise Exit(1)
        os.environ[var] = to_posix_path(p)

    return env


def _image_tag(env: dict) -> str:
    return str(os.environ.get("MONETIZE_IMAGE_TAG")
               or env.get("MONETIZE_IMAGE_TAG") or DEFAULT_IMAGE_TAG)


def _compose_argv(*tail: str) -> list[str]:
    return [
        "podman-compose", "--project-name", PROJECT_NAME,
        "--file", str(_overlay_dir() / "compose.yaml"),
        *tail,
    ]


def _run_compose(c: Context, *tail: str, pty: bool = True) -> None:
    run_cmd(c, " ".join(shlex.quote(a) for a in _compose_argv(*tail)), pty=pty)


def _stack_container_running(c: Context) -> bool:
    runtime = detect_runtime()
    r = run_cmd(
        c,
        (f"{runtime} ps -q "
         f"--filter label={PROJECT_LABEL}={PROJECT_NAME} "
         f"--filter label={SERVICE_LABEL}={SERVICE_NAME}"),
        hide=True, warn=True, echo=False,
    )
    return bool(r is not None and getattr(r, "ok", False) and (r.stdout or "").strip())


# ---------------------------------------------------------------------------
# 任务：镜像构建
# ---------------------------------------------------------------------------

@task(
    help={
        "tag": "产出镜像标签，默认 localhost/agent-monetize-dev:latest",
        "base-image": "基底镜像，默认 localhost/jupyter-podman-rootless:latest",
        "pip-mirror": "构建期 pip 镜像源：official|aliyun|tuna（默认 official）",
        "no-cache": "等价 podman build --no-cache（强制全量重建）",
    },
    auto_shortflags=False,
)
def build(c: Context, tag: str | None = None, base_image: str = DEFAULT_BASE_IMAGE,
          pip_mirror: str = "official", no_cache: bool = False) -> None:
    """构建 agent-monetize-dev 叠加镜像（构建期守卫失败即失败）。"""
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    runtime = detect_runtime()
    image_tag = tag or _image_tag(env)
    containerfile = _overlay_dir() / "Containerfile.agent-monetize"
    if not containerfile.exists():
        raise Exit(1, f"未找到 {containerfile}")

    chk = run_cmd(c, f"{runtime} image exists {base_image}", hide=True, warn=True, echo=False)
    if chk is None or not getattr(chk, "ok", False):
        print(f"[monetize] ⚠ 本地缺少基底镜像 {base_image}")
        print("[monetize]   先执行: invoke load   （从构建端缓存加载 rootless 基底）")
        raise Exit(1)

    parts = [
        runtime, "build", f"-f {shlex.quote(str(containerfile))}",
        f"--build-arg BASE_IMAGE={shlex.quote(base_image)}",
        f"--build-arg PIP_MIRROR={shlex.quote(pip_mirror)}",
        f"-t {shlex.quote(image_tag)}",
    ]
    if no_cache:
        parts.append("--no-cache")
    parts.append(shlex.quote(str(_overlay_dir())))
    run_cmd(c, " ".join(parts), pty=True)
    print(f"[monetize] ✅ 叠加镜像构建完成: {image_tag}")
    print("[monetize]   下一步: invoke monetize.up")


# ---------------------------------------------------------------------------
# 任务：栈生命周期
# ---------------------------------------------------------------------------

@task(help={"skip-build": "跳过启动前的镜像构建（默认每次 up 随带构建）"},
      auto_shortflags=False)
def up(c: Context, skip_build: bool = False) -> None:
    """渲染并启动 agent-monetize-dev 栈（podman-compose up -d，默认随带构建）。"""
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    if not skip_build:
        build(c)
    _run_compose(c, "up", "-d")
    ssh_port = os.environ.get("MONETIZE_SSH_PORT",
                              env.get("MONETIZE_SSH_PORT", "2224"))
    jp = os.environ.get("MONETIZE_JUPYTER_PORT",
                        env.get("MONETIZE_JUPYTER_PORT", "8892"))
    print("[monetize] ✅ 栈已启动：")
    print(f"        SSH     localhost:{ssh_port}")
    print(f"        Jupyter localhost:{jp}")
    print("[monetize]   状态: invoke monetize.ps    日志: invoke monetize.logs    冒烟: invoke monetize.smoke")


@task(help={"volumes": "同时删除栈命名卷（默认保留以加速重复运行）"},
      auto_shortflags=False)
def down(c: Context, volumes: bool = False) -> None:
    """停止并删除 agent-monetize-dev 栈容器与网络（bind 数据不受影响）。"""
    _gate_all()
    _run_compose(c, *(["down", "--volumes"] if volumes else ["down"]))
    print("[monetize] ✅ 栈已停止并清理")


@task
def ps(c: Context) -> None:
    """查看 agent-monetize-dev 栈服务状态。"""
    _gate_all()
    _run_compose(c, "ps", pty=False)


@task(help={"tail": "显示最近 N 行后持续跟踪（默认 100）"}, auto_shortflags=False)
def logs(c: Context, tail: int = 100) -> None:
    """跟踪 agent-monetize-dev 栈服务日志（Ctrl+C 退出，不影响容器运行）。"""
    _gate_all()
    _run_compose(c, "logs", "--follow", f"--tail={tail}")


# ---------------------------------------------------------------------------
# 任务：冒烟（栈运行 → compose exec；未运行 → run --rm 仅镜像守卫）
# ---------------------------------------------------------------------------

# 镜像烤入的守卫/冒烟脚本路径
SMOKE_DIR = "/opt/agent-monetize-dev-smoke"
GUARD_SCRIPT = "_toolchain_guards.py"
MOUNTS_SMOKE = "smoke_native.py"
# apache-tvm-ffi wheel 为 cp314 GIL；编译/运行/内核解释器统一用 base env
SMOKE_PYTHON = "/opt/conda/bin/python"


@task(auto_shortflags=False)
def smoke(c: Context) -> None:
    """运行 agent-monetize 冒烟：工具链守卫（始终）+ 原生/挂载冒烟（栈运行时）。"""
    _gate_all()
    _ensure_runtime_ready()
    env = _prepare_env()
    image_tag = _image_tag(env)
    runtime = detect_runtime()

    if _stack_container_running(c):
        print("[monetize] 检测到运行中的栈，经 compose exec 执行守卫与原生冒烟：")
        _run_compose(c, "exec", "-T", SERVICE_NAME, SMOKE_PYTHON,
                     f"{SMOKE_DIR}/{GUARD_SCRIPT}", pty=False)
        _run_compose(c, "exec", "-T", SERVICE_NAME, SMOKE_PYTHON,
                     f"{SMOKE_DIR}/{MOUNTS_SMOKE}", pty=False)
    else:
        print("[monetize] 栈未运行，使用一次性容器仅执行工具链守卫（原生冒烟需先 up）：")
        run_cmd(c, " ".join([
            runtime, "run", "--rm", "--entrypoint", SMOKE_PYTHON,
            shlex.quote(image_tag), f"{SMOKE_DIR}/{GUARD_SCRIPT}",
        ]), pty=True)
    print("[monetize] ✅ 冒烟通过")


# ---------------------------------------------------------------------------
# 任务：栈内 exec 长任务（clang++ 编译原生 .so / 打 wheel）
# ---------------------------------------------------------------------------

@task(auto_shortflags=False)
def build_native(c: Context) -> None:
    """栈内 clang++ 编译 score_opportunity.cc → native/build/score_opportunity.so。"""
    _gate_all()
    _ensure_runtime_ready()
    if not _stack_container_running(c):
        print("[monetize] ⚠ monetize 栈未运行，请先：invoke monetize.up --skip-build")
        raise Exit(1)
    print("[monetize] 栈内编译 tvm-ffi 原生模块（链接 apache-tvm-ffi libtvm_ffi.so）")
    _run_compose(c, "exec", "-T", SERVICE_NAME, "bash",
                 "/opt/monetize-builder/scripts/build-native.sh", pty=True)


@task(auto_shortflags=False)
def wheel(c: Context) -> None:
    """栈内 setuptools 打 agent-monetize 纯 Python wheel（产物落 workspace/dist）。"""
    _gate_all()
    _ensure_runtime_ready()
    if not _stack_container_running(c):
        print("[monetize] ⚠ 栈未运行，请先：invoke monetize.up --skip-build")
        raise Exit(1)
    print("[monetize] 栈内打包 agent-monetize wheel（纯 Python，.so 不入库）")
    _run_compose(c, "exec", "-T", SERVICE_NAME, "bash",
                 "/opt/monetize-builder/scripts/build-wheel.sh", pty=True)
