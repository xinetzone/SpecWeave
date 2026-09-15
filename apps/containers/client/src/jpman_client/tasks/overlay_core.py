"""数据驱动的 podman-compose 叠加栈编排内核（quant/xmnn/monetize 同族共享）。

设计目标（OKF 重构 R→I→E）：
  - 每个叠加栈只声明一份 ``StackSpec``（身份/端口/挂载/构建参数/冒烟形态/
    文案），六任务骨架（build/up/down/ps/logs/smoke）由 ``make_stack_tasks``
    工厂统一生成，消除三模块逐字重复的同构函数（AC-5）。
  - 本模块是 **client 内** 的栈编排内核：可以消费 ``.manage``/``.utils`` 的
    client 专属能力，但**不得** import 任何具体栈模块，也不出现具体栈常量
    （栈知识一律由 ``StackSpec`` 实例从外部注入）。
  - 与共享包 jpman_common 的边界：平台/进程/连接通用能力在 jpman_common；
    compose 声明式栈编排在本模块。本模块**禁止 import podman**（C11/C13），
    只通过 ``run_cmd`` 子进程驱动 podman-compose/podman。

行为契约（迁移自三模块 2026-09-15 实证版本）：
  - Windows 原生：优先透明桥接 WSL 发行版（run_in_wsl_bridge），不可桥接再
    Exit(1) 门禁；POSIX 缺 podman-compose 二进制给安装指引。
  - 环境优先级：shell 显式 export > root client .env（override=False）
    > compose.yaml 内 ``${VAR:-default}``。
  - argv 日志/拼接统一 ``shlex.quote``（修复旧 quant.py 裸 join 漂移，AC-2）。
  - up 前 reconcile Created/Exited 残留（rootlessport 端口占用自愈）。
"""
from __future__ import annotations

import os
import platform
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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

# podman-compose 给栈资源打的项目标签（知识包 05：标签即数据库；SDK/CLI 接缝）
PROJECT_LABEL = "io.podman.compose.project"
SERVICE_LABEL = "io.podman.compose.service"


# ---------------------------------------------------------------------------
# 声明式规格
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceMount:
    """运行时 bind 挂载的宿主路径规格。

    - env：注入子进程环境的变量名（compose.yaml 内同名插值）。
    - default_rel：缺省相对路径；相对 anchor 解析（repo=仓库根=client 上三级，
      client=client 根；external/chaos 类源码锚仓库根而非 client）。
    - must_exist：是否做宿主存在性硬校验（源码树 True；workspace 走自动 mkdir）。
    """

    env: str
    default_rel: str
    label: str
    anchor: str = "repo"  # "repo" | "client"
    must_exist: bool = True


@dataclass(frozen=True)
class SmokeSpec:
    """冒烟形态（三栈差异的声明式描述）。

    - python：栈内解释器绝对路径（quant 用 main env free-threaded 之外的
      /opt/conda/envs/main/bin/python；xmnn/monetize 用 base env /opt/conda/bin/python）。
    - exec_scripts：栈运行时经 ``compose exec`` 逐个执行的脚本（相对 smoke_dir）。
    - standalone_scripts：栈未运行时经 ``podman run --rm --entrypoint`` 逐个
      执行的脚本（quant 为全部 3 个纯 ONNX；xmnn/monetize 仅工具链守卫，
      挂载/原生冒烟要求先 up）。
    """

    python: str
    smoke_dir: str
    exec_scripts: tuple[str, ...]
    standalone_scripts: tuple[str, ...]
    running_note: str
    standalone_note: str
    done_message: str


@dataclass(frozen=True)
class TaskDocs:
    """六任务 docstring（invoke --list 描述文本，属任务表面契约，迁移须逐字）。"""

    build: str
    up: str
    down: str
    ps: str
    logs: str
    smoke: str


@dataclass(frozen=True)
class StackSpec:
    """单个 podman-compose 叠加栈的完整声明（compose.yaml 之外的 Python 侧事实源）。"""

    # —— 身份 ——
    namespace: str  # invoke 命名空间/横幅前缀：quant | xmnn | monetize
    project: str  # compose --project-name（标签 io.podman.compose.project 值）
    service: str  # compose 服务名（io.podman.compose.service 值）
    overlay_subdir: str  # overlays/<本目录>（compose.yaml/Containerfile 所在）
    containerfile: str  # overlay 目录内的 Containerfile 文件名
    default_image_tag: str
    default_base_image: str
    env_prefix: str  # QUANT | XMNN | MONETIZE（衍生 _WORKSPACE/_IMAGE_TAG/端口键）

    # —— 任务表面文案（--list 黄金快照逐字保持） ——
    docs: TaskDocs
    down_volumes_help: str

    # —— 端口/横幅 ——
    ssh_default: str
    jupyter_default: str
    jupyter_banner_note: str = ""  # xmnn 的「（内核：Python 3.14 (xmnn dev)）」
    build_done_label: str = "叠加镜像"  # 构建完成文案（quant 历史为「量化叠加镜像」）
    build_next_hint: str = ""  # 构建完成行尾补充（quant：（启动声明式栈））
    up_footer: tuple[str, ...] = ()  # 空=自动单行；xmnn 用三行（含编译/打包提示）

    # —— compose 文件/构建参数差异 ——
    gpu_override: bool = False  # 存在 compose.gpu.yaml 且 up/smoke 暴露 --gpu（quant）
    conda_mirror: bool = False  # build 暴露 --conda-mirror / CONDA_MIRROR（xmnn）
    auto_shortflags: bool = False  # invoke 自动短选项（quant 历史为默认开启）

    # —— 挂载/冒烟/桥接 ——
    source_mounts: tuple[SourceMount, ...] = ()
    smoke: Optional[SmokeSpec] = None
    bridge_env_keys: tuple[str, ...] = ()  # T4：WSL 桥接透传键（下沉后唯一事实源）

    # —— 长任务未运行提示（默认自动生成；monetize 指向 --skip-build） ——
    not_running_hint: str = ""

    # 便捷衍生键
    @property
    def workspace_env(self) -> str:
        return f"{self.env_prefix}_WORKSPACE"

    @property
    def image_tag_env(self) -> str:
        return f"{self.env_prefix}_IMAGE_TAG"

    @property
    def ssh_port_env(self) -> str:
        return f"{self.env_prefix}_SSH_PORT"

    @property
    def jupyter_port_env(self) -> str:
        return f"{self.env_prefix}_JUPYTER_PORT"

    @property
    def stack_not_running_hint(self) -> str:
        return self.not_running_hint or (
            f"{self.project} 栈未运行，请先：invoke {self.namespace}.up"
        )


# ---------------------------------------------------------------------------
# 路径 / 门禁
# ---------------------------------------------------------------------------


def overlay_dir(spec: StackSpec) -> Path:
    """叠加层目录（compose.yaml / Containerfile 所在）。"""
    return _project_root() / "overlays" / spec.overlay_subdir


def gate_platform(spec: StackSpec) -> None:
    """Windows 原生：优先透明桥接到 WSL 发行版执行；不可桥接再门禁。

    桥接成功时 run_in_wsl_bridge 已在发行版内完整执行任务，本进程 Exit(0)
    收尾（WSL2 内 Python 报 Linux 直接放行，不进入 Windows 分支）。
    """
    if platform.system() != "Windows":
        return
    distro = run_in_wsl_bridge(extra_env_keys=spec.bridge_env_keys)
    if distro is not None:
        print(f"[{spec.namespace}] ✅ 已经 WSL 发行版 {distro} 桥接执行；如需栈长驻请保持会话：")
        print(f"        wsl -d {distro} -- sleep infinity")
        raise Exit(0)
    client_posix = to_posix_path(_project_root())
    print(f"[{spec.namespace}] ⚠ Windows 原生 CPython 不支持 podman-compose 编排路径（其短语法")
    print("        挂载/路径解析在 Windows 原生存在已知缺陷），且未能自动桥接至")
    print("        WSL 发行版。请检查：")
    print("          · WSL 发行版可启动（wsl --list --verbose），或设置")
    print("            COMPOSE_WSL_DISTRO=<发行版> 指定桥接目标（none=关闭桥接）")
    print("          · 发行版内已安装 client 与 compose 依赖：")
    print(f'            cd {client_posix} && pip install -e ".[compose]"')
    print("        放行方式二选一：")
    print("        ① 在 WSL2 发行版内手动执行（推荐）：")
    print("           wsl -d <发行版>")
    print(f"           cd {client_posix}")
    print(f'           pip install -e ".[compose]" && invoke {spec.namespace}.up')
    print("        ② 或进入 client 自举容器后执行（基底已内嵌 podman-compose）：")
    print(f"           invoke env.run-cmd --cmd 'inv {spec.namespace}.up'")
    raise Exit(1)


def gate_compose_binary(spec: StackSpec) -> None:
    """POSIX 宿主缺 podman-compose 时给可执行安装指引。"""
    if shutil.which("podman-compose") is not None:
        return
    print(f'[{spec.namespace}] ⚠ 未找到 podman-compose；本命名空间为声明式编排层，请先安装：')
    print('         pip install -e ".[compose]"')
    print("        （rootless 基底镜像内已内置；亦可 `invoke env.run-cmd` 在容器内执行）")
    raise Exit(1)


def gates(spec: StackSpec) -> None:
    """任何栈任务入口先过的两道门（平台桥接/门禁 → compose 二进制）。"""
    gate_platform(spec)
    gate_compose_binary(spec)


def ensure_runtime_ready(spec: StackSpec) -> None:
    """daemon 预检（machine 未运行时的提示先于镜像/构建误报）。"""
    ready, hint = check_runtime_ready()
    if not ready:
        print(f"[{spec.namespace}] ⚠ {hint}")
        raise Exit(1)


# ---------------------------------------------------------------------------
# 配置解析
# ---------------------------------------------------------------------------


def _resolve_path(spec: StackSpec, raw: str, *, must_exist: bool, label: str) -> str:
    """相对路径相对 invoke cwd 解析；转绝对 POSIX；可选存在性硬校验。"""
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    if must_exist and not p.exists():
        print(f"[{spec.namespace}] ⚠ {label}宿主路径不存在：{p}")
        print("        请在 .env / 环境变量中设置对应变量指向有效目录后重试。")
        raise Exit(1)
    return to_posix_path(p)


def prepare_env(spec: StackSpec) -> dict:
    """加载 root .env（override=False，副作用同步 os.environ）并补全默认值。

    - workspace 解析为绝对 POSIX 路径注入（compose 任务可从任意 cwd 调用，
      不能依赖 compose.yaml 内相对路径）；幂等 mkdir + checkpoint 可写放宽。
    - source_mounts 的源码路径按各自锚点（仓库根/client 根）取缺省值，
      解析为绝对 POSIX，must_exist 时做存在性硬校验。
    """
    env = _load_env_overrides(_project_root())
    root = _project_root()
    repo_root = root.parents[2]

    ws = os.environ.get(spec.workspace_env) or env.get(spec.workspace_env)
    if not ws:
        ws = str((root / "workspace").resolve())
    ws_path = Path(ws).expanduser()
    if not ws_path.is_absolute():
        # 相对路径相对 invoke 执行目录解析（与 compose 文件目录默认值语义不同，
        # 任务路径以用户 cwd 为基准更符合直觉）
        ws_path = (Path.cwd() / ws_path).resolve()
    ws_path.mkdir(parents=True, exist_ok=True)
    # rootless+9p/drvfs 下 root 预建的 checkpoint 目录对容器内 devuser 不可写，
    # Jupyter 保存会 Errno 13；编排层幂等放宽该单一目录（详见 utils docstring）
    ensure_workspace_checkpoint_writable(ws_path)
    os.environ[spec.workspace_env] = to_posix_path(ws_path)

    for mount in spec.source_mounts:
        base = repo_root if mount.anchor == "repo" else root
        raw = (
            os.environ.get(mount.env)
            or env.get(mount.env)
            or str((base / mount.default_rel).resolve())
        )
        os.environ[mount.env] = _resolve_path(
            spec, raw, must_exist=mount.must_exist, label=mount.label
        )

    return env


def image_tag(spec: StackSpec, env: dict) -> str:
    return str(
        os.environ.get(spec.image_tag_env)
        or env.get(spec.image_tag_env)
        or spec.default_image_tag
    )


def _env_port(spec: StackSpec, env: dict, key: str, default: str) -> str:
    return str(os.environ.get(key) or env.get(key) or default)


# ---------------------------------------------------------------------------
# podman-compose argv 与执行（统一 shlex.quote，AC-2）
# ---------------------------------------------------------------------------


def compose_argv(spec: StackSpec, *tail: str, gpu: bool = False) -> list[str]:
    """组装 podman-compose 公共 argv（固定 project name，-f 绝对路径）。

    gpu=True 且栈声明 gpu_override 时叠加 compose.gpu.yaml（透传 /dev/dri）。
    """
    overlay = overlay_dir(spec)
    files = [overlay / "compose.yaml"]
    if gpu:
        if not spec.gpu_override:
            # 内部不变量：非 GPU 栈不应收到 gpu=True（工厂不会暴露该参数）
            raise RuntimeError(f"栈 {spec.namespace} 未声明 gpu_override")
        files.append(overlay / "compose.gpu.yaml")
    argv = ["podman-compose", "--project-name", spec.project]
    for f in files:
        argv += ["--file", str(f)]
    argv += list(tail)
    return argv


def run_compose(c: Context, spec: StackSpec, *tail: str, gpu: bool = False, pty: bool = True) -> None:
    """执行 podman-compose 子进程（逐参数 shlex.quote，路径含空格也安全）。

    extends 对 argv 透明：podman-compose 1.6.0 在解析阶段把
    ``extends.file`` 的相对路径按引用它的 compose 文件目录重写
    （_parse_compose_file L2844-L2849），故绝对 --file + 任意 cwd 均可。
    """
    argv = compose_argv(spec, *tail, gpu=gpu)
    run_cmd(c, " ".join(shlex.quote(a) for a in argv), pty=pty)


# ---------------------------------------------------------------------------
# 容器状态探测 / 残留自愈（CLI 标签接缝，知识包 05：标签即数据库）
# ---------------------------------------------------------------------------


def container_running(c: Context, spec: StackSpec) -> bool:
    """通过 compose 项目标签判断本栈服务容器是否在运行。"""
    runtime = detect_runtime()
    r = run_cmd(
        c,
        (
            f"{runtime} ps -q "
            f"--filter label={PROJECT_LABEL}={spec.project} "
            f"--filter label={SERVICE_LABEL}={spec.service}"
        ),
        hide=True,
        warn=True,
        echo=False,
    )
    return bool(r is not None and getattr(r, "ok", False) and (r.stdout or "").strip())


def reconcile_stale_containers(c: Context, spec: StackSpec, env: Optional[dict] = None) -> None:
    """up 前清理本项目残留的非 running 容器（Created/Exited 持有 rootlessport
    端口分配致 up bind 端口报 address already in use，exit 125；2026-09-15
    三栈实证）。命中即 compose down（不加 --volumes，保留命名卷/绑定数据）。"""
    runtime = detect_runtime()
    r = run_cmd(
        c,
        (
            f"{runtime} ps -a -q "
            f"--filter label={PROJECT_LABEL}={spec.project} "
            "--filter status=created --filter status=exited"
        ),
        hide=True,
        warn=True,
        echo=False,
    )
    stale = bool(r is not None and getattr(r, "ok", False) and (r.stdout or "").strip())
    if not stale:
        return
    env = env if env is not None else {}
    ssh = _env_port(spec, env, spec.ssh_port_env, spec.ssh_default)
    jupyter = _env_port(spec, env, spec.jupyter_port_env, spec.jupyter_default)
    print(
        f"[{spec.namespace}] ⚠ 检测到项目残留容器（Created/Exited 持有 "
        f"{ssh}/{jupyter} 端口分配），"
    )
    print(f"[{spec.namespace}]   先 compose down 清理（保留命名卷/绑定数据）后重新 up …")
    run_compose(c, spec, "down")
    print(f"[{spec.namespace}] ✅ 残留已清理，继续 up")


def require_running(c: Context, spec: StackSpec) -> None:
    """长任务（build-tvm/wheel/build-native）前置：栈必须运行。"""
    if not container_running(c, spec):
        print(f"[{spec.namespace}] ⚠ {spec.stack_not_running_hint}")
        raise Exit(1)


# ---------------------------------------------------------------------------
# 镜像构建 / 栈生命周期内核
# ---------------------------------------------------------------------------


def build_image(
    c: Context,
    spec: StackSpec,
    *,
    tag: Optional[str],
    base_image: str,
    pip_mirror: str,
    conda_mirror: Optional[str] = None,
    no_cache: bool = False,
) -> str:
    """podman build 薄封装（不引入 compose build 黑盒）；返回最终镜像标签。"""
    env = prepare_env(spec)
    runtime = detect_runtime()
    img_tag = tag or image_tag(spec, env)
    overlay = overlay_dir(spec)
    containerfile = overlay / spec.containerfile
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
        print(f"[{spec.namespace}] ⚠ 本地缺少基底镜像 {base_image}")
        print("[%s]   先执行: invoke load   （从构建端缓存加载 rootless 基底）" % spec.namespace)
        raise Exit(1)

    parts = [
        runtime,
        "build",
        f"-f {shlex.quote(str(containerfile))}",
        f"--build-arg BASE_IMAGE={shlex.quote(base_image)}",
        f"--build-arg PIP_MIRROR={shlex.quote(pip_mirror)}",
    ]
    if spec.conda_mirror:
        parts.append(f"--build-arg CONDA_MIRROR={shlex.quote(conda_mirror or 'official')}")
    parts.append(f"-t {shlex.quote(img_tag)}")
    if no_cache:
        parts.append("--no-cache")
    parts.append(shlex.quote(str(overlay)))
    run_cmd(c, " ".join(parts), pty=True)
    print(f"[{spec.namespace}] ✅ {spec.build_done_label}构建完成: {img_tag}")
    tail = f"invoke {spec.namespace}.up"
    if spec.build_next_hint:
        tail = f"{tail}    {spec.build_next_hint}"
    print(f"[{spec.namespace}]   下一步: {tail}")
    return img_tag


def up_stack(c: Context, spec: StackSpec, *, gpu: bool = False, skip_build: bool = False) -> None:
    """渲染并启动栈（默认随带构建；up 前端口残留自愈）。"""
    if not skip_build:
        # up 内联构建只按默认参数执行（mirror/tag/base 自定义走显式 build 两步路径）
        build_image(
            c,
            spec,
            tag=None,
            base_image=spec.default_base_image,
            pip_mirror="official",
            conda_mirror="official" if spec.conda_mirror else None,
            no_cache=False,
        )
    env = dict(os.environ)
    reconcile_stale_containers(c, spec, env=env)
    run_compose(c, spec, "up", "-d", gpu=gpu)
    ssh = _env_port(spec, env, spec.ssh_port_env, spec.ssh_default)
    jupyter = _env_port(spec, env, spec.jupyter_port_env, spec.jupyter_default)
    print(f"[{spec.namespace}] ✅ 栈已启动：")
    print(f"        SSH     localhost:{ssh}")
    jupyter_line = f"        Jupyter localhost:{jupyter}"
    if spec.jupyter_banner_note:
        jupyter_line = f"{jupyter_line}{spec.jupyter_banner_note}"
    print(jupyter_line)
    if gpu and spec.gpu_override:
        print("        GPU     /dev/dri 已透传（compose.gpu.yaml）")
    if spec.up_footer:
        for line in spec.up_footer:
            print(line)
    else:
        print(
            f"[{spec.namespace}]   状态: invoke {spec.namespace}.ps    "
            f"日志: invoke {spec.namespace}.logs    冒烟: invoke {spec.namespace}.smoke"
        )


def down_stack(c: Context, spec: StackSpec, *, volumes: bool = False) -> None:
    tail = ["down"]
    if volumes:
        tail.append("--volumes")
    run_compose(c, spec, *tail)
    print(f"[{spec.namespace}] ✅ 栈已停止并清理")


def ps_stack(c: Context, spec: StackSpec) -> None:
    run_compose(c, spec, "ps", pty=False)


def logs_stack(c: Context, spec: StackSpec, tail: int = 100) -> None:
    run_compose(c, spec, "logs", "--follow", f"--tail={tail}")


# ---------------------------------------------------------------------------
# 冒烟
# ---------------------------------------------------------------------------


def smoke_stack(c: Context, spec: StackSpec, *, gpu: bool = False) -> None:
    """运行栈冒烟：栈在运行 → compose exec 执行 exec_scripts；未运行 →
    podman run --rm 一次性容器执行 standalone_scripts。"""
    if spec.smoke is None:
        raise RuntimeError(f"栈 {spec.namespace} 未声明 smoke 规格")
    ensure_runtime_ready(spec)
    env = prepare_env(spec)
    img_tag = image_tag(spec, env)
    runtime = detect_runtime()
    smoke = spec.smoke

    if container_running(c, spec):
        print(f"[{spec.namespace}] {smoke.running_note}")
        for script in smoke.exec_scripts:
            run_compose(
                c,
                spec,
                "exec",
                "-T",
                spec.service,
                smoke.python,
                f"{smoke.smoke_dir}/{script}",
                gpu=gpu,
                pty=False,
            )
    else:
        print(f"[{spec.namespace}] {smoke.standalone_note}")
        for script in smoke.standalone_scripts:
            # 注意：standalone 路径为迁移前逐字节等价的裸 `podman run --rm`
            # （不带 rootless 三必需，历史仅跑纯 CPU ONNX/守卫脚本）。未来若
            # 有冒烟脚本产生设备依赖（GPU/NPU/fuse），必须先在此补三必需或改
            # 走 compose 路径，不得直接加 --device（见 client AGENTS C3）。
            run_cmd(
                c,
                " ".join(
                    [
                        runtime,
                        "run",
                        "--rm",
                        "--entrypoint",
                        smoke.python,
                        shlex.quote(img_tag),
                        f"{smoke.smoke_dir}/{script}",
                    ]
                ),
                pty=True,
            )
    print(f"[{spec.namespace}] ✅ {smoke.done_message}")


# ---------------------------------------------------------------------------
# 任务工厂：由 StackSpec 生成六任务骨架
# ---------------------------------------------------------------------------


def _build_help(spec: StackSpec) -> dict:
    help_ = {
        "tag": f"产出镜像标签，默认 {spec.default_image_tag}（或 root .env {spec.image_tag_env}）",
        "base-image": "基底镜像（Containerfile ARG BASE_IMAGE），默认 %s" % spec.default_base_image,
        "pip-mirror": "构建期 pip 镜像源：official|aliyun|tuna（默认 official）",
        "no-cache": "等价 podman build --no-cache（强制全量重建）",
    }
    if spec.conda_mirror:
        help_["conda-mirror"] = (
            "构建期 conda 镜像源：official|aliyun|tuna（.env 经 up 的 compose 内联 build 生效）"
        )
    return help_


def make_stack_tasks(spec: StackSpec) -> dict:
    """生成六任务骨架 {build,up,down,ps,logs,smoke}（invoke.Task 对象）。

    长任务（build-tvm/wheel/build-native）不在本工厂：由各栈模块用内核
    helper（gates/ensure_runtime_ready/require_running/run_compose）单独构造。
    """
    s = spec  # 闭包绑定
    deco = {"auto_shortflags": spec.auto_shortflags}

    # —— build（conda_mirror 栈多一个 --conda-mirror 参数，签名须逐字保持） ——
    if spec.conda_mirror:

        @task(help=_build_help(spec), **deco)
        def build(
            c: Context,
            tag: str | None = None,
            base_image: str = spec.default_base_image,
            pip_mirror: str = "official",
            conda_mirror: str = "official",
            no_cache: bool = False,
        ) -> None:
            gates(s)
            ensure_runtime_ready(s)
            build_image(
                c,
                s,
                tag=tag,
                base_image=base_image,
                pip_mirror=pip_mirror,
                conda_mirror=conda_mirror,
                no_cache=no_cache,
            )

    else:

        @task(help=_build_help(spec), **deco)
        def build(
            c: Context,
            tag: str | None = None,
            base_image: str = spec.default_base_image,
            pip_mirror: str = "official",
            no_cache: bool = False,
        ) -> None:
            gates(s)
            ensure_runtime_ready(s)
            build_image(
                c,
                s,
                tag=tag,
                base_image=base_image,
                pip_mirror=pip_mirror,
                no_cache=no_cache,
            )

    build.__doc__ = spec.docs.build

    # —— up ——
    up_help = {"skip-build": "跳过启动前的镜像构建（默认每次 up 随带构建跟随层更新）"}
    if spec.gpu_override:
        up_help = {
            "gpu": "叠加 compose.gpu.yaml（透传 /dev/dri；默认隔离不透传 GPU）",
            **up_help,
        }

    if spec.gpu_override:

        @task(help=up_help, **deco)
        def up(c: Context, gpu: bool = False, skip_build: bool = False) -> None:
            gates(s)
            ensure_runtime_ready(s)
            prepare_env(s)
            up_stack(c, s, gpu=gpu, skip_build=skip_build)

    else:

        @task(help=up_help, **deco)
        def up(c: Context, skip_build: bool = False) -> None:
            gates(s)
            ensure_runtime_ready(s)
            prepare_env(s)
            up_stack(c, s, skip_build=skip_build)

    up.__doc__ = spec.docs.up

    # —— down ——
    @task(help={"volumes": spec.down_volumes_help}, **deco)
    def down(c: Context, volumes: bool = False) -> None:
        gates(s)
        down_stack(c, s, volumes=volumes)

    down.__doc__ = spec.docs.down

    # —— ps ——
    @task(**deco)
    def ps(c: Context) -> None:
        gates(s)
        ps_stack(c, s)

    ps.__doc__ = spec.docs.ps

    # —— logs ——
    @task(help={"tail": "显示最近 N 行后持续跟踪（默认 100）"}, **deco)
    def logs(c: Context, tail: int = 100) -> None:
        gates(s)
        logs_stack(c, s, tail)

    logs.__doc__ = spec.docs.logs

    # —— smoke ——
    if spec.gpu_override:

        @task(
            help={
                "gpu": "运行栈经 compose 启动时是否带 GPU 覆盖（仅影响 exec 寻址，不影响冒烟本身）"
            },
            **deco,
        )
        def smoke(c: Context, gpu: bool = False) -> None:
            gates(s)
            smoke_stack(c, s, gpu=gpu)

    else:

        @task(**deco)
        def smoke(c: Context) -> None:
            gates(s)
            smoke_stack(c, s)

    smoke.__doc__ = spec.docs.smoke

    return {
        "build": build,
        "up": up,
        "down": down,
        "ps": ps,
        "logs": logs,
        "smoke": smoke,
    }
