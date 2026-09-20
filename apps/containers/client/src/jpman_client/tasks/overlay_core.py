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
  - up 前 preflight 三道自愈：① Created/Exited 残留 compose down；
    ② 跨控制平面标签（Windows 裸 compose 的 ``D:\\`` vs WSL invoke 的
    ``/mnt/d/``）分歧会令 podman-compose 强制 recreate 并在 pod infra
    强拆时留下孤儿 rootlessport，检出活体容器路径标签不一致先优雅 down；
    ③ 无活体项目容器却仍有 rootlessport 监听本栈端口时定点回收孤儿进程。
"""
import os
import platform
import re
import shlex
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from invoke import Context, task
from invoke.exceptions import Exit

from .client_core import load_image, save_image
from .manage import _load_env_overrides, _project_root, _resolve_bool
from .utils import (
    archive_flavor,
    check_runtime_ready,
    default_build_cache_dir,
    detect_runtime,
    ensure_workspace_checkpoint_writable,
    ensure_wsl_rootless_runtime,
    find_latest_image_tar,
    run_cmd,
    run_in_wsl_bridge,
    to_posix_path,
    validate_manifest_integrity,
    wsl_bridge_diagnosis,
)

# podman-compose 给栈资源打的项目标签（知识包 05：标签即数据库；SDK/CLI 接缝）
PROJECT_LABEL = "io.podman.compose.project"
SERVICE_LABEL = "io.podman.compose.service"
# compose 实际使用的 compose.yaml 绝对路径标签：Windows 裸 compose 写 D:\...，
# WSL 桥接 invoke 写 /mnt/d/...；同一栈跨控制平面该标签必变（2026-09-15 实证）。
CONFIG_FILES_LABEL = "com.docker.compose.project.config_files"

# ss -ltnp 行内进程持有者：users:(("rootlessport",pid=92823,fd=10))
_SS_HOLDER_RE = re.compile(r'users:\(\("(?P<comm>[^"]+)",pid=(?P<pid>\d+)')
# conmon 命令行：/usr/bin/conmon --api-version 1 -c <64hex> -u <64hex> ... -n <name>
_CONMON_CID_RE = re.compile(r"(?:\s|^)-c\s+(?P<cid>[0-9a-f]{64})\b")
_CONMON_NAME_RE = re.compile(r"(?:\s|^)-n\s+(?P<name>\S+)")

# TORCH_FLAVOR 白名单（C18）：""=不装 torch；cpu=CPU wheel；cu130=CUDA 13.0 wheel。
# 取值直接作为 download.pytorch.org/whl/<flavor> 索引路径，故必须是**白名单**而非
# 自由文本（构建期网络请求目标不可由用户输入任意拼接）。
TORCH_FLAVORS: tuple[str, ...] = ("", "cpu", "cu130")

# GPU 设备形态表：顺序即**自动探测优先级**（`(设备路径, 覆盖文件形态)`）。
# 形态只决定叠加哪个覆盖文件——``generic`` 用 ``compose.gpu.yaml``，其余用
# ``compose.gpu.<形态>.yaml``（缺失则回退 generic，见 :func:`gpu_override_file`）。
# 表驱动而非 if/elif 硬编码：新增平台（如 Jetson /dev/nvhost-*）只加一行。
GPU_DEVICE_FORMS: tuple[tuple[str, str], ...] = (
    ("/dev/dri", "generic"),
    ("/dev/dxg", "wsl"),
)

# WSL2 GPU 半虚拟化：``/dev/dxg`` 只是半虚拟化通道，libcuda 由 WSL 宿主提供，
# 容器内**必须**挂载该单文件才能 ``CDLL("libcuda.so.1")``（2026-09-20 实测：
# 仅挂 /dev/dxg 或仅设 LD_LIBRARY_PATH 均失败；挂整目录 + LD_LIBRARY_PATH 会
# 冲掉栈自带的 TVM 库路径，故用单文件挂载，见 compose.gpu.wsl.yaml 文件头）。
WSL_CUDA_LIB = "/usr/lib/wsl/lib/libcuda.so.1"


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
    gpu_override: bool = False  # 存在 compose.gpu.yaml 且 up/smoke 暴露 --gpu（quant/xmnn）
    gpu_device_env: str = ""  # GPU 设备插值键（空=不插值，设备项写死；quant/xmnn 均为 GPU_DEVICE）
    conda_mirror: bool = False  # build 暴露 --conda-mirror / CONDA_MIRROR（xmnn）
    torch_flavor: bool = False  # build 暴露 --torch / TORCH_FLAVOR（xmnn；空|cpu|cu130）
    auto_shortflags: bool = False  # invoke 自动短选项（quant 历史为默认开启）

    # —— 挂载/冒烟/桥接 ——
    source_mounts: tuple[SourceMount, ...] = ()
    smoke: Optional[SmokeSpec] = None
    bridge_env_keys: tuple[str, ...] = ()  # T4：WSL 桥接透传键（下沉后唯一事实源）

    # —— 长任务未运行提示（默认自动生成；monetize 指向 --skip-build） ——
    not_running_hint: str = ""

    # —— 离线模式（声明后工厂额外生成 save/load 任务，up 暴露 --offline） ——
    supports_offline: bool = False

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
    def offline_env_key(self) -> str:
        return f"{self.env_prefix}_OFFLINE"

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
    Linux 放行路径先做 WSL rootless 运行时目录自愈（VM 回收后
    /run/user/<uid> 缺失致 podman exit 125；非 WSL 平台零副作用）。
    """
    if platform.system() != "Windows":
        ensure_wsl_rootless_runtime()
        return
    distro = run_in_wsl_bridge(extra_env_keys=spec.bridge_env_keys)
    if distro is not None:
        print(f"[{spec.namespace}] ✅ 已经 WSL 发行版 {distro} 桥接执行；如需栈长驻请保持会话：")
        print(f"        wsl -d {distro} -- sleep infinity")
        raise Exit(0)
    client_posix = to_posix_path(_project_root())
    print(f"[{spec.namespace}] ⚠ Windows 原生 CPython 不支持 podman-compose 编排路径（其短语法")
    print("        挂载/路径解析在 Windows 原生存在已知缺陷），且未能自动桥接至")
    print("        WSL 发行版。")
    diagnosis = wsl_bridge_diagnosis()
    if diagnosis:
        # 只给 wsl -l -v 会把「Running 但 VM 层不可用」送进死胡同，先给实测原因
        print(f"        桥接探测失败：{diagnosis}")
        print("        若 wsl -l -v 显示该发行版 Running 而探测仍失败，先重置 WSL 虚拟机：")
        print("          wsl --shutdown     # 关闭全部发行版进程，随后重跑本命令")
    print("        请检查：")
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


def resolve_build_args(
    spec: StackSpec,
    env: dict,
    *,
    base_image: Optional[str] = None,
    pip_mirror: Optional[str] = None,
    conda_mirror: Optional[str] = None,
    torch: Optional[str] = None,
) -> dict:
    """解析构建期 build-arg（单一事实源，C15）。

    键为**无前缀**的 compose 插值键（``BASE_IMAGE`` / ``PIP_MIRROR`` /
    ``CONDA_MIRROR`` / ``TORCH_FLAVOR``），与 ``overlays/*/compose.yaml`` 的
    ``${KEY:-默认}`` 逐一对应：``build``、``up`` 内联构建、compose 内部 build
    段三处必须拿到同一值，否则某一处 build-arg 变化就会让构建层缓存整体失效
    （表现为"白重建"）。

    优先级：显式参数（CLI 旗标）> shell export > .env > 默认值；compose 段不
    可见 CLI 旗标，故**跨三处一致必须写 .env**，CLI 旗标只覆盖单次调用。

    ``torch_flavor``：仅声明 ``torch_flavor=True`` 的栈解析（键 ``TORCH_FLAVOR``），
    取值白名单 ``""``（不装）/``cpu``/``cu130``——非白名单在**解析期**即拒绝，
    避免把错误值带到 podman build 才炸（构建一次代价极高）。
    """
    args = {
        "base_image": str(
            base_image
            or os.environ.get("BASE_IMAGE")
            or env.get("BASE_IMAGE")
            or spec.default_base_image
        ),
        "pip_mirror": str(
            pip_mirror or os.environ.get("PIP_MIRROR") or env.get("PIP_MIRROR") or "official"
        ),
    }
    if spec.conda_mirror:
        args["conda_mirror"] = str(
            conda_mirror
            or os.environ.get("CONDA_MIRROR")
            or env.get("CONDA_MIRROR")
            or "official"
        )
    if spec.torch_flavor:
        flavor = str(
            torch or os.environ.get("TORCH_FLAVOR") or env.get("TORCH_FLAVOR") or ""
        ).strip()
        if flavor not in TORCH_FLAVORS:
            raise Exit(
                1,
                f"TORCH_FLAVOR={flavor!r} 非法；可选值："
                + " | ".join(repr(v) for v in TORCH_FLAVORS)
                + "（'' 表示不装 torch）",
            )
        args["torch_flavor"] = flavor
    return args


# ---------------------------------------------------------------------------
# 离线模式（仅 supports_offline 栈）
# ---------------------------------------------------------------------------


def resolve_offline(
    spec: StackSpec, on_val: bool, off_val: bool, env: Optional[dict] = None
) -> bool:
    """三态解析离线开关：``--offline`` > ``--no-offline`` > ``{PREFIX}_OFFLINE`` > 默认关。

    非离线栈恒 False（不消费 ``{PREFIX}_OFFLINE``）。env 未显式传入时先经
    ``_load_env_overrides`` 把 root .env 同步进 ``os.environ``（幂等，与
    ``prepare_env`` 同一优先级：shell export > .env > 默认）。

    **显式旗标必须写回环境**：WSL 桥接（``run_in_wsl_bridge``）只透传环境变量、
    不转发 CLI 参数，旗标若不在 ``gate_platform`` 之前固化到
    ``os.environ[offline_env_key]``，桥接后即丢失（V 对抗审查 V-1）。
    """
    if not spec.supports_offline:
        return False
    key = spec.offline_env_key
    if env is None:
        _load_env_overrides(_project_root())
        env = os.environ
    offline = _resolve_bool(on_val, off_val, env, key, False, "offline")
    if on_val or off_val:
        os.environ[key] = "1" if offline else "0"
    return offline


def offline_exec_env(spec: StackSpec) -> list[str]:
    """栈内 exec 长任务的离线环境注入：``-e {PREFIX}_OFFLINE=1``；非离线时空。

    经 exec 的 ``-e`` 逐次注入而非进 compose ``environment`` 段：离线是调用期
    开关，不应污染 compose.yaml 的确定性渲染（保留 test_compose_merge 黄金快照）。
    """
    if not spec.supports_offline or not resolve_offline(spec, False, False):
        return []
    return ["-e", f"{spec.offline_env_key}=1"]


def compose_up_tail() -> list[str]:
    """``up`` 的 compose 尾参**恒含** ``--no-build``：构建执行者唯一（C16）。

    podman-compose 的 ``up`` 默认对含 build 段的服务执行构建
    （vendor ``podman_compose.py`` L4098 ``if not args.no_build:``）。若不关闭，
    一次 ``invoke x.up`` 会构建两次——内核 ``build_image`` 与 compose build 段，
    二者是「两个执行者解释同一意图」，且 compose 段看不到 CLI 旗标、时点在
    内核之后（离线场景更直接破网，V 对抗审查 V-2）。

    故：**镜像存在性由内核负责，compose 只负责起容器**。compose.yaml 的
    ``build`` 段仅服务**裸 podman-compose** 路径，invoke 路径不再消费它。
    """
    return ["up", "-d", "--no-build"]


# ---------------------------------------------------------------------------
# podman-compose argv 与执行（统一 shlex.quote，AC-2）
# ---------------------------------------------------------------------------


def gpu_override_file(spec: StackSpec, form: str = "generic") -> Path:
    """按形态选 GPU 覆盖文件；``compose.gpu.<形态>.yaml`` 缺失时回退 generic。

    回退是**刻意的**：形态表新增一行时不必同时新增覆盖文件——只有形态确实
    需要额外声明（如 wsl 需挂 libcuda）才建姊妹文件，否则沿用通用覆盖。
    """
    overlay = overlay_dir(spec)
    if form and form != "generic":
        candidate = overlay / f"compose.gpu.{form}.yaml"
        if candidate.exists():
            return candidate
    return overlay / "compose.gpu.yaml"


def compose_argv(
    spec: StackSpec, *tail: str, gpu: bool = False, gpu_form: str = "generic"
) -> list[str]:
    """组装 podman-compose 公共 argv（固定 project name，-f 绝对路径）。

    gpu=True 且栈声明 gpu_override 时叠加 GPU 覆盖文件；``gpu_form`` 决定
    具体文件（见 :func:`gpu_override_file`，只加载**一个**设备覆盖文件——
    两个同时加载会让 devices 列表出现重复项，podman 拒绝映射两次）。
    """
    overlay = overlay_dir(spec)
    files = [overlay / "compose.yaml"]
    if gpu:
        if not spec.gpu_override:
            # 内部不变量：非 GPU 栈不应收到 gpu=True（工厂不会暴露该参数）
            raise RuntimeError(f"栈 {spec.namespace} 未声明 gpu_override")
        files.append(gpu_override_file(spec, gpu_form))
    argv = ["podman-compose", "--project-name", spec.project]
    for f in files:
        argv += ["--file", str(f)]
    argv += list(tail)
    return argv


def run_compose(
    c: Context,
    spec: StackSpec,
    *tail: str,
    gpu: bool = False,
    gpu_form: str = "generic",
    pty: bool = True,
) -> None:
    """执行 podman-compose 子进程（逐参数 shlex.quote，路径含空格也安全）。

    extends 对 argv 透明：podman-compose 1.6.0 在解析阶段把
    ``extends.file`` 的相对路径按引用它的 compose 文件目录重写
    （_parse_compose_file L2844-L2849），故绝对 --file + 任意 cwd 均可。
    """
    argv = compose_argv(spec, *tail, gpu=gpu, gpu_form=gpu_form)
    run_cmd(c, " ".join(shlex.quote(a) for a in argv), pty=pty)


# podman 在 ``pod create`` / ``create`` / ``start`` 后回显的对象 ID（stdout，独占一行）
_COMPOSE_ECHO_ID_RE = re.compile(r"^[0-9a-f]{64}$")
# podman rootless netns 的**良性** ERROR（stderr）：宿主无 systemd 用户会话总线
# （WSL 发行版 / podman machine 内无 user session bus）时无法把 pasta 进程移入
# user.slice，容器照常创建并运行（与 compose.yaml 文件头记录的 aardvark-dns
# "Failed to connect to user scope bus" 同族；2026-09-18 实证）。
_PASTA_DBUS_NOISE_RE = re.compile(
    r"^ERROR\[\d+\]\s+failed to move the rootless netns pasta process to the "
    r"systemd user\.slice:\s*dbus: couldn't determine address of session bus"
)


def compose_echo_names(spec: StackSpec) -> tuple[str, ...]:
    """podman / podman-compose 会原样回显的本项目资源名（容器 / pod / 默认网络）。

    podman-compose 的默认命名为容器名 ``container_name``（本族三栈 == ``project``）、
    服务名、pod ``pod_<project>``、网络 ``<project>_default``。
    """
    return (
        spec.project,
        spec.service,
        f"pod_{spec.project}",
        f"{spec.project}_default",
    )


def is_benign_compose_noise(line: str, *, names: tuple[str, ...] = ()) -> bool:
    """判定 podman 透传的原生行是否属**良性噪声**（唯一判定点，纯函数可单测）。

    判据刻意收窄为「绝不可能是错误信息」的三类，凡有疑问一律返回 False（保留）：
      - 对象 ID 回显：整行恰为 64 位十六进制（pod/容器/网络 create 的 stdout）；
      - 资源名回显：整行恰为本项目容器名/pod 名/默认网络名（与 names 全等）；
      - 无会话总线提示：rootless netns 无法把 pasta 移入 user.slice（容器照常运行）。
    """
    text = line.strip()
    if not text:
        return False
    if _COMPOSE_ECHO_ID_RE.match(text):
        return True
    if text in names:
        return True
    return bool(_PASTA_DBUS_NOISE_RE.match(text))


def run_compose_up(
    c: Context, spec: StackSpec, *tail: str, gpu: bool = False, gpu_form: str = "generic"
) -> None:
    """执行 ``up`` 并过滤 podman 原生回显噪声（C17）。

    背景：podman-compose 在无 log_formatter 时以 ``close_fds=False`` 让子进程
    继承 stdio（vendor ``podman_compose.py`` L1907），podman 的 create/start
    回显（64 位对象 ID、资源名）与 rootless netns 的良性 ERROR 因此直通终端，
    把编排层逐行中文提示冲散（2026-09-18 用户实证）。

    安全边界（V 对抗审查）：
      - **失败时零过滤**：非零退出码下 stdout/stderr 全量原样回放后再
        ``Exit(code=rc)`` 上抛，真实故障信息不因过滤而丢失；
      - 过滤判据是白名单三式（见 :func:`is_benign_compose_noise`），有疑问保留；
      - 仅 ``up`` 走本函数——构建/编译等长任务仍逐字实时透传，流式体验不受影响。
    """
    argv = compose_argv(spec, *tail, gpu=gpu, gpu_form=gpu_form)
    cmd = " ".join(shlex.quote(a) for a in argv)
    print(f"执行: {cmd}")
    r = run_cmd(c, cmd, pty=False, hide=True, warn=True, echo=False)
    out = (getattr(r, "stdout", "") or "") if r is not None else ""
    err = (getattr(r, "stderr", "") or "") if r is not None else ""
    if r is None or not getattr(r, "ok", False):
        rc = int(getattr(r, "return_code", 1) or 1)
        print(f"[{spec.namespace}] ⚠ podman-compose up 失败（exit={rc}），原始输出如下：")
        for raw in (out, err):
            if raw:
                print(raw, end="" if raw.endswith("\n") else "\n")
        raise Exit(f"podman-compose up 失败 (exit={rc})", code=rc)

    names = compose_echo_names(spec)
    dropped = 0
    for raw in (out, err):
        for line in raw.splitlines():
            if is_benign_compose_noise(line, names=names):
                dropped += 1
            else:
                print(line)
    if dropped:
        print(
            f"[{spec.namespace}] ℹ 已过滤 {dropped} 行 podman 原生回显噪声"
            "（对象 ID / 资源名 / 无会话总线提示）"
        )


# ---------------------------------------------------------------------------
# 容器状态探测 / 残留自愈（CLI 标签接缝，知识包 05：标签即数据库）
# ---------------------------------------------------------------------------


def _project_ps_command(spec: StackSpec, *, all_containers: bool) -> str:
    runtime = detect_runtime()
    return (
        f"{runtime} ps {'-a ' if all_containers else ''}-q "
        f"--filter label={PROJECT_LABEL}={spec.project} "
        f"--filter label={SERVICE_LABEL}={spec.service}"
    )


def parse_ss_port_holders(line: str) -> tuple[Optional[str], list[tuple[str, int]]]:
    """解析单行 ``ss -ltnp`` 输出 → ``(端口, [(进程名, pid), ...])``。

    无端口或无进程持有者的行返回 ``(None, [])``。只做字符串解析（无子进程），
    供 daemon-free 单测；ss 默认列：State Recv-Q Send-Q Local Peer Process。
    """
    port = next(
        (
            tok.rsplit(":", 1)[-1]
            for tok in line.split()
            if ":" in tok and tok.rsplit(":", 1)[-1].isdigit()
        ),
        None,
    )
    if port is None:
        return None, []
    holders = [(m.group("comm"), int(m.group("pid"))) for m in _SS_HOLDER_RE.finditer(line)]
    return port, holders


def config_paths_diverge(actual: str, expected: str) -> bool:
    """跨控制平面判据：compose 把 config_files **原文字符串**纳入 config-hash，
    Windows 裸 compose 写 ``D:\\...``，WSL 桥接 invoke 写 ``/mnt/d/...``，
    即使指向同一文件，原文不等即会被 podman-compose 强制 recreate
    （2026-09-15 真机实证）——故此处禁止做路径等价归一。
    """
    return bool(actual) and actual.strip() != expected.strip()


def _running_project_container(c: Context, spec: StackSpec) -> str:
    """daemon 视角的首个 running 项目服务容器 ID（无则空串）。

    警告：WSL 发行版回收循环后 daemon 可能「撒谎」——libpod sqlite 仍记
    running 但容器 init 进程在宿主已死（假 Up，见 _container_truly_alive）。
    """
    r = run_cmd(c, _project_ps_command(spec, all_containers=False), hide=True, warn=True, echo=False)
    if r is None or not getattr(r, "ok", False):
        return ""
    return (r.stdout or "").strip().split()[0] if (r.stdout or "").strip() else ""


def _container_init_pid(c: Context, container_id: str) -> int:
    """读 daemon 记录的容器 init PID（``.State.Pid``）；查询失败/0 返回 0。"""
    runtime = detect_runtime()
    r = run_cmd(
        c,
        f"{runtime} inspect --format {shlex.quote('{{.State.Pid}}')} {container_id}",
        hide=True,
        warn=True,
        echo=False,
    )
    pid = ((r.stdout or "").strip() if r is not None and getattr(r, "ok", False) else "")
    return int(pid) if pid.isdigit() else 0


def _host_process_alive(c: Context, pid: int) -> bool:
    """宿主侧校验 PID 是否仍存活（``ps -p <pid> -o pid=``，零双引号探针）。"""
    if pid <= 0:
        return False
    r = run_cmd(c, f"ps -p {pid} -o pid=", hide=True, warn=True, echo=False)
    return bool(r is not None and getattr(r, "ok", False) and (r.stdout or "").strip())


def _container_truly_alive(c: Context, spec: StackSpec, container_id: str) -> bool:
    """活体最终判据：daemon 记 running **且** init PID 在宿主存活。

    WSL 回收循环可制造「假 Up」：``podman ps``/inspect 均报 running、孤儿
    conmon/rootlessport 续命端口甚至 HTTP 302，但宿主 ``ps -p`` 查无此
    PID、crun status 文件已删（2026-09-15 三次实证）。单靠 ps 标签探测
    会被假象欺骗而跳过自愈。
    """
    init_pid = _container_init_pid(c, container_id)
    return bool(init_pid) and _host_process_alive(c, init_pid)


def container_running(c: Context, spec: StackSpec) -> bool:
    """通过 compose 项目标签判断本栈服务容器是否在运行。"""
    return bool(_running_project_container(c, spec))


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


def _stack_ports(spec: StackSpec, env: dict) -> list[str]:
    return sorted(
        {
            _env_port(spec, env, spec.ssh_port_env, spec.ssh_default),
            _env_port(spec, env, spec.jupyter_port_env, spec.jupyter_default),
        }
    )


def _listening_rootlessport_pids(c: Context, ports: list[str]) -> list[int]:
    """查 ``ss -ltnp``：返回正在监听给定端口的 rootlessport PID 集合。

    仅认进程名为 rootlessport 的持有者（其他栈 pasta/conmon 一律不动）；
    ss 不可用（最小化发行版）时返回空列表，由后续 compose 原生报错兜底，
    不阻断 up。
    """
    r = run_cmd(c, "ss -ltnp", hide=True, warn=True, echo=False)
    if r is None or not getattr(r, "ok", False):
        return []
    wanted = set(ports)
    pids: set[int] = set()
    for line in (r.stdout or "").splitlines():
        port, holders = parse_ss_port_holders(line)
        if port in wanted:
            pids.update(pid for comm, pid in holders if comm == "rootlessport")
    return sorted(pids)


def reap_orphan_port_holders(c: Context, spec: StackSpec, ports: list[str]) -> list[int]:
    """无活体项目容器时，定点回收仍占着本栈端口的孤儿 rootlessport。

    实证场景（2026-09-15）：podman-compose 1.6 跨控制平面/异常重建 pod 时
    强杀 infra conmon，rootlessport 被 WSL ``/init`` 收养成为孤儿继续监听，
    新 pod up 报 ``bind: address already in use``（exit 125）。调用方必须
    先确认无活体项目容器（避免误杀健康栈自己的转发器）。
    """
    if platform.system() != "Linux":
        return []  # 双保险：Windows 原生路径已整体桥接进 WSL，本机不该执行
    pids = _listening_rootlessport_pids(c, ports)
    if not pids:
        return []
    print(
        f"[{spec.namespace}] ⚠ 端口 {'/'.join(ports)} 被孤儿 rootlessport 占用"
        f"（pid={','.join(map(str, pids))}，所属容器已不存在），定点回收 …"
    )
    run_cmd(c, "kill " + " ".join(map(str, pids)), hide=True, warn=True, echo=False)
    time.sleep(1.0)
    survivors = _listening_rootlessport_pids(c, ports)
    if survivors:
        run_cmd(c, "kill -9 " + " ".join(map(str, survivors)), hide=True, warn=True, echo=False)
        time.sleep(0.5)
    remaining = _listening_rootlessport_pids(c, ports)
    if remaining:
        print(f"[{spec.namespace}] ⚠ 端口仍被占用（pid={','.join(map(str, remaining))}），")
        print("        请手工排查（或 wsl --shutdown 后重开保活锚，会影响同发行版其他栈）。")
    else:
        print(f"[{spec.namespace}] ✅ 孤儿端口已释放，继续 up")
    return pids


def parse_conmon_process(line: str) -> Optional[tuple[int, str, str]]:
    """解析 ``ps -eo pid=,args=`` 的一行 → ``(pid, 容器完整ID, 容器名)``。

    非 conmon 行或缺 ``-c``/``-n`` 参数返回 None。纯字符串解析供单测。
    """
    parts = line.split(None, 1)
    if len(parts) < 2 or not parts[0].isdigit():
        return None
    pid = int(parts[0])
    args = parts[1]
    if "conmon" not in args.split()[0]:
        return None
    mc = _CONMON_CID_RE.search(args)
    mn = _CONMON_NAME_RE.search(args)
    if not mc or not mn:
        return None
    return pid, mc.group("cid"), mn.group("name")


def _list_stale_conmons(c: Context, spec: StackSpec) -> list[tuple[int, str]]:
    """列出本栈的 stale conmon：``-n`` 为本栈容器名但其容器已不在 libpod。

    实证（2026-09-15 跨平面循环）：容器/pod 被强删后 conmon 偶尔不退出
    （不持端口，故不阻断 up，但跨平面反复交替会累积进程垃圾）。判据双重
    收紧：进程名 conmon + 名字匹配 + 完整 ID 不在 ``podman ps -aq`` 的
    运行集合（运行中容器的 conmon 绝不回收；stopped 容器无需 conmon 驻留）。
    覆盖默认 ``container_name == project`` 的三栈；自定义容器名不覆盖。
    """
    runtime = detect_runtime()
    live = run_cmd(c, f"{runtime} ps -aq", hide=True, warn=True, echo=False)
    if live is None or not getattr(live, "ok", False):
        return []
    live_ids = set((live.stdout or "").split())
    r = run_cmd(c, "ps -eo pid=,args=", hide=True, warn=True, echo=False)
    if r is None or not getattr(r, "ok", False):
        return []
    stale: list[tuple[int, str]] = []
    for line in (r.stdout or "").splitlines():
        parsed = parse_conmon_process(line)
        if parsed is None:
            continue
        pid, cid, name = parsed
        if name == spec.project and cid[:12] not in live_ids:
            stale.append((pid, cid[:12]))
    return stale


def reap_stale_conmons(c: Context, spec: StackSpec) -> list[int]:
    """定点回收本栈 stale conmon（与 reap_orphan_port_holders 同一前置条件）。"""
    if platform.system() != "Linux":
        return []
    stale = _list_stale_conmons(c, spec)
    if not stale:
        return []
    pids = [pid for pid, _ in stale]
    ids = ",".join(cid for _, cid in stale)
    print(
        f"[{spec.namespace}] ⚠ 发现 {len(pids)} 个已删容器遗留的 stale conmon"
        f"（容器 {ids} 已不在 libpod），定点回收 …"
    )
    run_cmd(c, "kill " + " ".join(map(str, pids)), hide=True, warn=True, echo=False)
    time.sleep(0.5)
    survivors = [pid for pid, _ in _list_stale_conmons(c, spec)]
    if survivors:
        run_cmd(c, "kill -9 " + " ".join(map(str, survivors)), hide=True, warn=True, echo=False)
        time.sleep(0.5)
    print(f"[{spec.namespace}] ✅ stale conmon 回收完成（{'全部退出' if not _list_stale_conmons(c, spec) else '仍有残留，请手工排查'}）")
    return pids


def _running_config_files(c: Context, spec: StackSpec, container_id: str) -> str:
    """读运行容器的 compose.yaml 路径标签（跨控制平面判据）。"""
    runtime = detect_runtime()
    template = '{{index .Config.Labels "' + CONFIG_FILES_LABEL + '"}}'
    r = run_cmd(
        c,
        f"{runtime} inspect --format {shlex.quote(template)} {container_id}",
        hide=True,
        warn=True,
        echo=False,
    )
    return ((r.stdout or "").strip() if r is not None and getattr(r, "ok", False) else "")


def up_preflight(c: Context, spec: StackSpec, env: Optional[dict] = None) -> None:
    """up 前自愈（顺序不可调换）：

    1. Created/Exited 项目残留 → compose down（保留卷/绑定）；
    2. daemon 记 running 但容器 init 进程在宿主已死（**假 Up**：WSL 回收
       循环后 libpod 状态与内核进程脱节，``ps``/HTTP 302 都可能是孤儿
       进程制造的假象，exec 报 ``crun ... status: No such file``）→ compose
       down 清除失实记录；真活体但 compose.yaml 路径标签原文与本平面
       ``--file`` 不一致（Windows 裸 compose 的 ``D:\\...`` vs WSL 桥接的
       ``/mnt/d/...``，config-hash 按原文计算）→ 先优雅 compose down；
    3. 无活体项目容器时回收孤儿进程：rootlessport（持端口，必收）与
       stale conmon（已删容器遗留，不持端口但跨平面循环会累积）。
    """
    env = env if env is not None else {}
    ports = _stack_ports(spec, env)
    reconcile_stale_containers(c, spec, env=env)

    cid = _running_project_container(c, spec)
    if cid and not _container_truly_alive(c, spec, cid):
        print(f"[{spec.namespace}] ⚠ 检测到假 Up：daemon 记 running 但容器 init "
              "进程在宿主已不存在（WSL 回收循环），ps/端口/HTTP 均为假象；")
        print(f"[{spec.namespace}]   先 compose down 清除失实状态后重建 …")
        run_compose(c, spec, "down")
        cid = ""
    if cid:
        actual = _running_config_files(c, spec, cid)
        expected = str(overlay_dir(spec) / "compose.yaml")
        if config_paths_diverge(actual, expected):
            print(
                f"[{spec.namespace}] ⚠ 检测到栈由另一控制平面创建"
                f"（compose 路径标签 {actual}），"
            )
            print(
                f"[{spec.namespace}]   与当前平面（{expected}）不一致；直接 up 会被"
                "强制 recreate 并可能残留孤儿端口，先优雅 down …"
            )
            run_compose(c, spec, "down")
            cid = ""

    if not cid:
        reap_orphan_port_holders(c, spec, ports)
        reap_stale_conmons(c, spec)


def require_running(c: Context, spec: StackSpec) -> None:
    """长任务（build-tvm/wheel/build-native）前置：栈必须**真活体**。

    daemon 记 running 不足为凭（假 Up 时 exec 必报
    ``crun ... status: No such file``）；以 init PID 宿主存活为判据。
    拦截后不自动重建（避免破坏长任务现场），只提示先 up。
    """
    cid = _running_project_container(c, spec)
    if not cid or not _container_truly_alive(c, spec, cid):
        print(f"[{spec.namespace}] ⚠ {spec.stack_not_running_hint}")
        print(f"[{spec.namespace}]   若 podman ps 显示 Up 但 exec 报 "
              "crun status 不存在，是假 Up（WSL 回收循环），请先重新 up。")
        raise Exit(1)


# ---------------------------------------------------------------------------
# 镜像构建 / 栈生命周期内核
# ---------------------------------------------------------------------------


def _require_local_image(
    c: Context, spec: StackSpec, img_tag: str, *, action: str, offline: bool
) -> None:
    """跳过构建时的前置：镜像必须已在本地，缺失即 fail-fast + 中文可执行指引。

    两条路径共用（C16）——① ``--offline``：只能用已导入镜像（断网，不能构建）；
    ② 非离线 ``--skip-build``：用户声明不做任何构建。二者此刻都**没有第二个
    执行者兜底**（``up`` 恒 ``--no-build``），故必须在此拦下并给出可执行出口。
    """
    runtime = detect_runtime()
    r = run_cmd(c, f"{runtime} image exists {img_tag}", hide=True, warn=True, echo=False)
    if r is not None and getattr(r, "ok", False):
        return
    if offline:
        print(f"[{spec.namespace}] ⚠ 离线模式下本地缺少镜像 {img_tag}，无法{action}：")
        print(f"[{spec.namespace}]   联网机器导出归档: invoke {spec.namespace}.save")
        print(f"[{spec.namespace}]   本机导入归档:     invoke {spec.namespace}.load --path <归档.tar.gz>")
    else:
        print(f"[{spec.namespace}] ⚠ --skip-build 置位但本地缺少镜像 {img_tag}，无法{action}：")
        print(f"[{spec.namespace}]   compose 段不会兜底构建（up 恒 --no-build）；二选一：")
        print(f"[{spec.namespace}]   随带构建启动:   invoke {spec.namespace}.up")
        print(
            f"[{spec.namespace}]   显式构建后启动: invoke {spec.namespace}.build"
            f" && invoke {spec.namespace}.up --skip-build"
        )
    raise Exit(1)


def build_image(
    c: Context,
    spec: StackSpec,
    *,
    tag: Optional[str],
    base_image: Optional[str] = None,
    pip_mirror: Optional[str] = None,
    conda_mirror: Optional[str] = None,
    torch: Optional[str] = None,
    no_cache: bool = False,
    offline: Optional[bool] = None,
) -> str:
    """podman build 薄封装（不引入 compose build 黑盒）；返回最终镜像标签。

    四个 build-arg 传 ``None`` 时经 ``resolve_build_args`` 解析：读与 compose.yaml
    ``${KEY:-默认}`` 相同的无前缀 .env 键（C15），保证本层构建与 compose 内部
    build 段拿到同一组值，避免互相失效层缓存。

    离线模式（``offline=None`` 时按 ``{PREFIX}_OFFLINE`` 解析）下**首行即拒绝**：
    构建期 apt/mamba/pip 均需联网，无网机器无法完成，错误前置优于构建中途报错。
    """
    if offline is None:
        offline = resolve_offline(spec, False, False)
    if offline:
        print(f"[{spec.namespace}] ⚠ 离线模式（{spec.offline_env_key}=1）禁止构建镜像：")
        print("        构建期 apt/mamba/pip 均需联网，无网机器无法完成。")
        print(f"[{spec.namespace}]   联网机器: invoke {spec.namespace}.build && invoke {spec.namespace}.save")
        print(f"[{spec.namespace}]   本机导入: invoke {spec.namespace}.load --path <归档.tar.gz>")
        print(f"[{spec.namespace}]   或仅用本地镜像启动: invoke {spec.namespace}.up --offline")
        raise Exit(1)

    env = prepare_env(spec)
    args = resolve_build_args(
        spec,
        env,
        base_image=base_image,
        pip_mirror=pip_mirror,
        conda_mirror=conda_mirror,
        torch=torch,
    )
    base_image = args["base_image"]
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
        f"--build-arg PIP_MIRROR={shlex.quote(args['pip_mirror'])}",
    ]
    if spec.conda_mirror:
        parts.append(
            f"--build-arg CONDA_MIRROR={shlex.quote(args.get('conda_mirror') or 'official')}"
        )
    if spec.torch_flavor:
        parts.append(
            f"--build-arg TORCH_FLAVOR={shlex.quote(args.get('torch_flavor') or '')}"
        )
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


# ---------------------------------------------------------------------------
# GPU 设备解析与预检（C19：opt-in 设备的**运行期可用性**门禁）
# ---------------------------------------------------------------------------


def _runtime_path_exists(c: Context, path: str) -> bool:
    """在 **podman 所在环境**探测路径是否存在。

    run_cmd 在 Windows 原生会自动把整条 invoke 命令重放到 WSL 发行版内执行
    （run_in_wsl_bridge），故存在性判定天然落在 compose/podman 真正运行的那一侧，
    不会出现"Windows 侧没有 /dev/dri 就误判为不可用"。
    """
    r = run_cmd(c, f"test -e {shlex.quote(path)}", hide=True, warn=True, echo=False)
    return r is not None and getattr(r, "ok", False)


def _runtime_cdi_available(c: Context) -> bool:
    """探测宿主是否已生成 CDI 设备规格（``nvidia-ctk cdi generate`` 的产物）。"""
    r = run_cmd(c, "ls /etc/cdi/*.yaml /var/run/cdi/*.yaml", hide=True, warn=True, echo=False)
    return r is not None and getattr(r, "ok", False) and bool(
        (getattr(r, "stdout", "") or "").strip()
    )


def _form_of_device(device: str) -> str:
    """已知设备路径 → 形态；未登记的路径按通用形态处理（generic 覆盖即够）。"""
    for known, form in GPU_DEVICE_FORMS:
        if device == known:
            return form
    return "generic"


def resolve_gpu_device(c: Context, spec: StackSpec, env: dict) -> tuple[str, str]:
    """解析 GPU 设备令牌与形态，并把令牌**回写 os.environ**（单一事实源）。

    为什么必须预检：compose 里的 ``devices`` 由 podman 在 create 阶段做
    ``stat``，缺路径时只丢一句 ``Error: stat /dev/dri: no such file or
    directory`` + exit 125（且次生 ``no container with name ... found``），
    用户无从得知该改哪个键。故在 up 之前把判定与指引前置。

    令牌优先级：shell export > root .env > 自动探测（``GPU_DEVICE_FORMS`` 顺序）。
      - ``/`` 开头：宿主机设备路径 → 存在性硬校验，形态按设备查表；
      - 非 ``/`` 开头：CDI 引用（如 ``nvidia.com/gpu=all``）→ 校验宿主已生成
        ``/etc/cdi`` 或 ``/var/run/cdi`` 下的 ``*.yaml``；
      - 空：按形态表探测（``/dev/dri`` 优先于 ``/dev/dxg``，保留 Intel/AMD 与
        NVIDIA 直通设备的既有行为），全无则 fail-fast。

    wsl 形态额外校验 :data:`WSL_CUDA_LIB`：``/dev/dxg`` 只是半虚拟化通道，
    缺 libcuda 时 CUDA 不可用，同样前置报错而非让 bind 挂载裸报错。
    """
    key = spec.gpu_device_env or "GPU_DEVICE"
    token = str(os.environ.get(key) or env.get(key) or "")

    if token.startswith("/"):
        if not _runtime_path_exists(c, token):
            print(f"[{spec.namespace}] ⚠ {key}={token} 在 podman 宿主不存在，无法透传 GPU：")
            print(f"[{spec.namespace}]   查看真实设备: ls /dev/dri /dev/dxg")
            print(
                f"[{spec.namespace}]   指定设备:     {key}=<设备路径> "
                f"invoke {spec.namespace}.up --gpu"
            )
            print(f"[{spec.namespace}]   自动探测:     unset {key}（缺省探测 /dev/dri → /dev/dxg）")
            raise Exit(1)
        form = _form_of_device(token)
    elif token:
        if not _runtime_cdi_available(c):
            print(f"[{spec.namespace}] ⚠ {key}={token} 是 CDI 引用，但宿主未生成 CDI 规格：")
            print("[%s]   先生成: sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml"
                  % spec.namespace)
            print(f"[{spec.namespace}]   或改用设备路径形态: {key}=/dev/dri")
            raise Exit(1)
        form = "generic"
    else:
        token, form = "", ""
        for device, candidate in GPU_DEVICE_FORMS:
            if _runtime_path_exists(c, device):
                token, form = device, candidate
                break
        if not token:
            names = " / ".join(d for d, _ in GPU_DEVICE_FORMS)
            print(f"[{spec.namespace}] ⚠ 未探测到可用 GPU 设备（{names} 均不存在），无法 --gpu：")
            print("[%s]   WSL2：确认 Windows 侧已装 NVIDIA 驱动（nvidia-smi 可用）"
                  % spec.namespace)
            print(f"[{spec.namespace}]   Intel/AMD：确认宿主已加载 i915/amdgpu 驱动")
            print(f"[{spec.namespace}]   或显式指定: {key}=<设备路径或 CDI 引用>")
            raise Exit(1)

    if form == "wsl" and not _runtime_path_exists(c, WSL_CUDA_LIB):
        print(f"[{spec.namespace}] ⚠ 检测到 {token}（WSL2 GPU），但宿主缺少 {WSL_CUDA_LIB}：")
        print("[%s]   该库由 WSL 宿主提供；请确认 Windows 侧 NVIDIA 驱动已安装"
              % spec.namespace)
        print(f"[{spec.namespace}]   或强制通用形态（不挂 libcuda）: {key}=/dev/dri")
        raise Exit(1)

    os.environ[key] = token
    return token, form


def up_stack(
    c: Context,
    spec: StackSpec,
    *,
    gpu: bool = False,
    skip_build: bool = False,
    offline: bool = False,
) -> None:
    """渲染并启动栈（默认随带构建；up 前过 up_preflight 三道自愈）。

    构建执行者唯一（C16）：镜像存在性由内核负责，compose 恒 ``up -d --no-build``。
    默认路径内联 ``build_image`` 后即起容器（全程一次构建）；``--skip-build`` 与
    离线路径不做任何构建，故先做本地镜像存在性预检（缺失 fail-fast + 中文指引），
    不再让 compose 的 build 段兜底。

    内联构建与显式 ``build`` 共用 ``resolve_build_args``（C15）：读 .env 的
    ``PIP_MIRROR`` / ``CONDA_MIRROR`` / ``BASE_IMAGE``——与 compose 段插值键同键。

    离线模式：强制跳过构建 + 本地镜像存在性预检 + compose ``up --no-build``。

    起容器经 ``run_compose_up``（C17）：过滤 podman 原生回显噪声，失败时零过滤。
    """
    if offline:
        skip_build = True
    if not skip_build:
        build_image(c, spec, tag=None, no_cache=False)
    env = dict(os.environ)
    if skip_build:
        _require_local_image(
            c, spec, image_tag(spec, env), action="启动栈", offline=offline
        )
    up_preflight(c, spec, env=env)
    # GPU 透传：设备令牌与形态在此解析（含运行期可用性预检），解析结果回写
    # os.environ 后由 compose 插值消费——终端提示与容器实收设备同源（C19）。
    gpu_token, gpu_form = ("", "generic")
    if gpu:
        gpu_token, gpu_form = resolve_gpu_device(c, spec, env)
    run_compose_up(c, spec, *compose_up_tail(), gpu=gpu, gpu_form=gpu_form)
    ssh = _env_port(spec, env, spec.ssh_port_env, spec.ssh_default)
    jupyter = _env_port(spec, env, spec.jupyter_port_env, spec.jupyter_default)
    print(f"[{spec.namespace}] ✅ 栈已启动：")
    print(f"        SSH     localhost:{ssh}")
    jupyter_line = f"        Jupyter localhost:{jupyter}"
    if spec.jupyter_banner_note:
        jupyter_line = f"{jupyter_line}{spec.jupyter_banner_note}"
    print(jupyter_line)
    if gpu and spec.gpu_override:
        print(f"        GPU     {gpu_token} 已透传（{gpu_override_file(spec, gpu_form).name}）")
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
    # 与 up 同源：--gpu 时先解析设备（形态决定 exec 用哪份覆盖文件，并保证
    # compose 插值拿到的令牌与栈启动时一致）
    gpu_form = "generic"
    if gpu:
        _, gpu_form = resolve_gpu_device(c, spec, env)

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
                gpu_form=gpu_form,
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
        "base-image": "基底镜像（Containerfile ARG BASE_IMAGE）；默认 .env BASE_IMAGE，缺省 %s"
        % spec.default_base_image,
        "pip-mirror": "构建期 pip 镜像源：official|aliyun|tuna；默认 .env PIP_MIRROR，缺省 official",
        "no-cache": "等价 podman build --no-cache（强制全量重建）",
    }
    if spec.conda_mirror:
        help_["conda-mirror"] = (
            "构建期 conda 镜像源：official|aliyun|tuna；默认 .env CONDA_MIRROR，缺省 official"
        )
    if spec.torch_flavor:
        help_["torch"] = (
            "torch 形态：''（不装，默认）|cpu|cu130；默认 .env TORCH_FLAVOR。"
            "cpu/cu130 经 download.pytorch.org/whl/<形态> 索引安装 torch 2.14.0"
        )
    return help_


def make_stack_tasks(spec: StackSpec) -> dict:
    """生成任务骨架 {build,up,down,ps,logs,smoke}（invoke.Task 对象）。

    ``supports_offline=True`` 的栈额外生成 {save,load} 两个镜像归档任务，并给
    ``up`` 追加 ``--offline``/``--no-offline`` 一对三态开关。

    长任务（build-tvm/wheel/build-native）不在本工厂：由各栈模块用内核
    helper（gates/ensure_runtime_ready/require_running/run_compose）单独构造。
    """
    s = spec  # 闭包绑定
    deco = {"auto_shortflags": spec.auto_shortflags}

    # —— build（conda_mirror / torch_flavor 栈各追加一个参数，签名须逐字保持） ——
    # 形参面 = 已启用构建能力的并集：能力开关只增不减形参，不互相"吃掉"。
    def _build_impl(
        c: Context,
        *,
        tag: str | None,
        base_image: str | None,
        pip_mirror: str | None,
        conda_mirror: str | None,
        torch: str | None,
        no_cache: bool,
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
            torch=torch,
            no_cache=no_cache,
        )

    if spec.conda_mirror and spec.torch_flavor:

        @task(help=_build_help(spec), **deco)
        def build(
            c: Context,
            tag: str | None = None,
            base_image: str | None = None,
            pip_mirror: str | None = None,
            conda_mirror: str | None = None,
            torch: str | None = None,
            no_cache: bool = False,
        ) -> None:
            _build_impl(
                c,
                tag=tag,
                base_image=base_image,
                pip_mirror=pip_mirror,
                conda_mirror=conda_mirror,
                torch=torch,
                no_cache=no_cache,
            )

    elif spec.conda_mirror:

        @task(help=_build_help(spec), **deco)
        def build(
            c: Context,
            tag: str | None = None,
            base_image: str | None = None,
            pip_mirror: str | None = None,
            conda_mirror: str | None = None,
            no_cache: bool = False,
        ) -> None:
            _build_impl(
                c,
                tag=tag,
                base_image=base_image,
                pip_mirror=pip_mirror,
                conda_mirror=conda_mirror,
                torch=None,
                no_cache=no_cache,
            )

    else:

        @task(help=_build_help(spec), **deco)
        def build(
            c: Context,
            tag: str | None = None,
            base_image: str | None = None,
            pip_mirror: str | None = None,
            no_cache: bool = False,
        ) -> None:
            _build_impl(
                c,
                tag=tag,
                base_image=base_image,
                pip_mirror=pip_mirror,
                conda_mirror=None,
                torch=None,
                no_cache=no_cache,
            )

    build.__doc__ = spec.docs.build

    # —— up ——
    up_help = {
        "skip-build": "跳过启动前的镜像构建，直接用本地已有镜像（缺失即 fail-fast "
        "并给出指引；compose 段不兜底构建，up 恒 --no-build）。默认随带构建，"
        "内联构建读 .env PIP_MIRROR/CONDA_MIRROR/BASE_IMAGE，与 compose 段同键"
    }
    if spec.supports_offline:
        up_help = {
            "offline": "离线模式：禁止构建（强制跳过）并只用本地已导入镜像",
            "no-offline": f"显式关闭 .env 的 {spec.offline_env_key}（覆盖离线默认）",
            **up_help,
        }
    if spec.gpu_override:
        dev_hint = (
            f"{spec.gpu_device_env or 'GPU_DEVICE'} 双形态（/ 开头=设备路径；否则=CDI 引用，"
            "如 nvidia.com/gpu=all）"
            if spec.gpu_device_env
            else "/dev/dri"
        )
        up_help = {
            "gpu": (
                f"透传 GPU：{dev_hint}；未设置时自动探测（"
                + " → ".join(d for d, _ in GPU_DEVICE_FORMS)
                + "，WSL2 额外叠加 compose.gpu.wsl.yaml 挂载 libcuda）；"
                "默认隔离不透传 GPU"
            ),
            **up_help,
        }

    # —— up（形参面 = gpu_override ∪ supports_offline，两个能力正交组合） ——
    # 历史写法是 gpu/offline/else 三路互斥，导致 xmnn 一旦同时声明两个能力，
    # --offline 会被 gpu 分支吃掉。改为"能力并集决定形参面"，公共实现下沉。
    def _up_impl(
        c: Context,
        *,
        gpu: bool,
        skip_build: bool,
        offline: bool,
        no_offline: bool,
    ) -> None:
        # 离线开关必须**先于 gates** 固化进 os.environ（WSL 桥接只透传环境
        # 变量、不转发 CLI 参数，晚于桥接则旗标丢失）
        is_offline = resolve_offline(s, offline, no_offline) if s.supports_offline else False
        gates(s)
        ensure_runtime_ready(s)
        prepare_env(s)
        up_stack(c, s, gpu=gpu, skip_build=skip_build, offline=is_offline)

    if spec.gpu_override and spec.supports_offline:

        @task(help=up_help, **deco)
        def up(
            c: Context,
            gpu: bool = False,
            skip_build: bool = False,
            offline: bool = False,
            no_offline: bool = False,
        ) -> None:
            _up_impl(c, gpu=gpu, skip_build=skip_build, offline=offline, no_offline=no_offline)

    elif spec.gpu_override:

        @task(help=up_help, **deco)
        def up(c: Context, gpu: bool = False, skip_build: bool = False) -> None:
            _up_impl(c, gpu=gpu, skip_build=skip_build, offline=False, no_offline=False)

    elif spec.supports_offline:

        @task(help=up_help, **deco)
        def up(
            c: Context,
            skip_build: bool = False,
            offline: bool = False,
            no_offline: bool = False,
        ) -> None:
            _up_impl(c, gpu=False, skip_build=skip_build, offline=offline, no_offline=no_offline)

    else:

        @task(help=up_help, **deco)
        def up(c: Context, skip_build: bool = False) -> None:
            _up_impl(c, gpu=False, skip_build=skip_build, offline=False, no_offline=False)

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

    tasks = {
        "build": build,
        "up": up,
        "down": down,
        "ps": ps,
        "logs": logs,
        "smoke": smoke,
    }

    # —— save / load（仅 supports_offline 栈：离线镜像归档出口/入口） ——
    if spec.supports_offline:
        cache_help = (
            "归档缓存目录，默认 .env 的 IMAGE_CACHE_DIR / 当前执行目录下的 .image-cache"
        )

        @task(
            help={
                "tag": f"要导出的镜像 tag，默认 {spec.default_image_tag}（或 root .env {spec.image_tag_env}）",
                "cache-dir": cache_help,
            },
            **deco,
        )
        def save(c: Context, tag: str | None = None, cache_dir: str | None = None) -> None:
            """导出本栈镜像为离线归档（tar.gz + manifest/SHA256，供无网机器 load）。"""
            gates(s)
            ensure_runtime_ready(s)
            env = _load_env_overrides(_project_root())
            target = tag or image_tag(s, env)
            cache_path = Path(cache_dir) if cache_dir else default_build_cache_dir()
            print(f"[{s.namespace}] 导出镜像归档: {target}")
            ok = save_image(
                c,
                target,
                cache_path,
                not_found_hint=f"先构建: invoke {s.namespace}.build",
                restore_hint=(
                    f"invoke {s.namespace}.load --path <归档.tar.gz>   或   "
                    f"invoke {s.namespace}.up --offline"
                ),
            )
            if not ok:
                raise Exit(1, "镜像归档导出失败")

        def _expected_flavor() -> str:
            """期望的 torch 形态（与 build 同一解析序：shell export > .env）。

            仅 ``torch_flavor`` 栈有意义；其余栈恒空串，load 保持历史「取最新」语义。
            """
            if not s.torch_flavor:
                return ""
            env = _load_env_overrides(_project_root())
            return str(
                os.environ.get("TORCH_FLAVOR") or env.get("TORCH_FLAVOR") or ""
            ).strip()

        @task(
            help={
                "path": "归档 tar.gz 路径；未指定则按 .env TORCH_FLAVOR 形态选取最新归档",
                "cache-dir": cache_help,
            },
            **deco,
        )
        def load(c: Context, path: str | None = None, cache_dir: str | None = None) -> None:
            """从离线归档导入本栈镜像（manifest 完整性校验，缺网可用）。

            C20：归档名携带 torch 形态（``-torch-<形态>-``），load 据此选档与校验——
            cpu 与 cu130 两份镜像 tag 相同（``localhost/xmnn-dev:latest``），不带形态
            过滤的「取最新」会在同族共存时静默导入错形态，直到容器内 torch.cuda 为空
            才暴露。
            """
            gates(s)
            ensure_runtime_ready(s)
            _load_env_overrides(_project_root())
            cache_path = Path(cache_dir) if cache_dir else default_build_cache_dir()
            expected = _expected_flavor()
            if path:
                tar_path = Path(path).resolve()
            else:
                # 期望形态已知时按形态过滤选档；期望为空（不装 torch）时宁可不过滤，
                # 但下方仍打印归档形态供人工核对（可辨识 > 静默）。
                tar_path = find_latest_image_tar(cache_path, expected or None)
                if tar_path is None:
                    print(f"[{s.namespace}] ⚠ 缓存目录中未找到归档: {cache_path}")
                    if expected:
                        print(f"[{s.namespace}]   当前 TORCH_FLAVOR={expected}，未找到该形态归档")
                    print(f"[{s.namespace}]   请在联网机器执行: invoke {s.namespace}.save")
                    raise Exit(1)
                print(f"[{s.namespace}] 自动选择最新归档: {tar_path}")
            got = archive_flavor(tar_path.name)
            if expected and got and got != expected:
                print(f"[{s.namespace}]  归档 torch 形态: {got} ≠ 期望: {expected}")
                raise Exit(
                    f"归档形态与 TORCH_FLAVOR 不符；改 .env TORCH_FLAVOR={got} 后 load，"
                    f"或换用 {expected} 形态归档（--path 显式指定）。"
                )
            if s.torch_flavor:
                if got:
                    print(f"[{s.namespace}] 归档 torch 形态: {got}")
                elif expected:
                    print(
                        f"[{s.namespace}] ⚠ 归档未标注 torch 形态（旧产物）；"
                        f"期望 {expected}，不做拦截"
                    )
            integrity_err = validate_manifest_integrity(cache_path, tar_path)
            if integrity_err:
                print(f"[{s.namespace}]  {integrity_err}")
                raise Exit(1, "归档校验失败，请重新 save 后再 load。")
            result = load_image(c, tar_path)
            if not result.loaded:
                raise Exit(1, result.message)
            print(f"[{s.namespace}] ✅ 镜像已导入；无网机器可直接: invoke {s.namespace}.up --offline")

        tasks["save"] = save
        tasks["load"] = load

    return tasks
