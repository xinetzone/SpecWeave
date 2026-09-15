"""镜像消费端工具函数（client 专属层）。

职责边界（2026-09 重构后）：
  - **组内共享能力**（运行时检测、路径转换、命令执行、随机串、容器只读探测）
    唯一实现位于 ``jpman_common``（apps/containers/shared），本模块再导出，
    保持 ``from .utils import ...`` 既有路径稳定；
  - **client 专属能力**保留在本文件：透传 spec（PassthroughSpec）、
    ContainerConfig/LoadImageResult、镜像 tar 加载命令与缓存校验、
    WSL compose 透明桥接、host key 维护、checkpoint 权限。

Windows WSL 支持说明（对齐 podman-py OKF v0.2 §8 Windows 三路径）：
  - **挂载路径转换** (Dimension A)：Windows ``D:\\ws`` → POSIX ``/mnt/d/ws``
    （容器内的 ``/workspace`` 卷挂载源路径，由 ``jpman_common.to_posix_path`` /
    :func:`normalize_path_str` 负责）
  - **Daemon 连接 URL** (Dimension B)：podman-py SDK 需要的
    ``unix://`` / ``ssh://`` / ``tcp://`` 6 种合法 scheme 之一，
    由共享层 ``jpman_common.connection`` 的 ``sdk_base_url_candidates`` /
    ``wsl_distro_name`` 负责（与挂载路径解耦，不要混淆）。
"""
import functools
import os
import platform
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from invoke.exceptions import Exit

# 组内共享层（jpman-common）：进程/平台/容器只读工具的唯一实现位于共享包，
# 此处再导出以保持 client 内部 ``from .utils import ...`` 既有路径稳定。
from jpman_common import (
    check_runtime_ready,
    container_exists,
    container_running,
    detect_runtime,
    generate_random_string,
    normalize_path_str,
    run_cmd,
    to_posix_path,
)
# B-scheme daemon 连接层（UID/socket 推导唯一事实源）统一位于共享包。
from jpman_common.connection import host_runtime_dir


# ── 运行时透传（对齐构建端 docs/07-toolbx-passthrough.md 的 5 项 opt-in）────────
# 关键认知（F 阶段公理②）：透传挂载源（Wayland socket / D-Bus bus）与设备节点
# （/dev/dri、/dev/bus/usb）是 **daemon 宿主（WSL2 / Podman Machine）内的路径**，
# 客户端可能跑在 Windows 原生 CPython 上——本机 Path.exists() 对这些路径必然返回
# False。因此**禁止**用本机存在性做前置校验（会误判拒绝正确的透传请求），
# 资源缺失只能在 podman 硬失败后翻译为可执行指引（见 passthrough_diagnose_hint）。
CONTAINER_RUNTIME_DIR = "/tmp/runtime-user"


def passthrough_paths() -> dict:
    """解析 5 项透传在 **daemon 宿主** 上的资源路径（可用环境变量逐个覆盖）。

    变量命名与构建端 ``compose.passthrough*.yaml`` 保持一致，便于两端迁移复用：
      ``HOST_XDG_RUNTIME_DIR`` / ``HOST_WAYLAND_DISPLAY`` / ``DBUS_SESSION_BUS_PATH``
      / ``GPU_DEVICE`` / ``USB_DEVICE``。
    """
    xdg = os.environ.get("HOST_XDG_RUNTIME_DIR") or host_runtime_dir()
    wayland_display = os.environ.get("HOST_WAYLAND_DISPLAY") or "wayland-0"
    # VIDEO_DEVICES：逗号分隔的 UVC 字符设备列表（摄像头采集）。默认 /dev/video0-3
    # （典型 4 个 V4L2 节点，含 IR 摄像头）。宿主无 video* 时 podman 硬失败（exit 125），
    # 走 C-I3 诊断；用 VIDEO_DEVICES 精确指定所需节点。
    video_devices = [
        d.strip()
        for d in os.environ.get("VIDEO_DEVICES", "/dev/video0,/dev/video1,/dev/video2,/dev/video3").split(",")
        if d.strip()
    ]
    return {
        "xdg_runtime_dir": xdg,
        "wayland_display": wayland_display,
        "wayland_socket": f"{xdg}/{wayland_display}",
        "dbus_bus": os.environ.get("DBUS_SESSION_BUS_PATH") or f"{xdg}/bus",
        "gpu_device": os.environ.get("GPU_DEVICE") or "/dev/dri",
        "usb_device": os.environ.get("USB_DEVICE") or "/dev/bus/usb",
        "video_devices": video_devices,
    }


@dataclass
class PassthroughSpec:
    """透传运行参数集合（SDK 与 CLI 两条路径共用同一份解析结果 → 参数天然一致）。"""

    network_mode: Optional[str] = None
    publish_ports: bool = True
    volumes: list[tuple[str, str, str]] = field(default_factory=list)
    devices: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)


def build_passthrough_spec(cfg: "ContainerConfig") -> PassthroughSpec:
    """把 5 个透传开关解析为统一的运行参数集合。

    与构建端 ``compose.passthrough*.yaml`` 的语义逐项对齐：
      ① Host 网络：``--network=host`` + **不再发布端口**（二者互斥）；rootless 无法
         绑定特权端口 22，故同时把 ``SSHD_PORT`` 设为 ``cfg.ssh_port``（默认 2222，
         非特权端口），令 host 网络下的 SSH 访问端口与端口映射模式保持一致。
      ② Wayland / ④ D-Bus：挂载到容器内 ``/tmp/runtime-user`` 并注入对应环境变量。
      ③ GPU / ⑤ USB：追加设备节点（rootless 三必需的 ``/dev/fuse`` 仍由
         ``ContainerConfig.devices`` 硬编码保留，见 C3）。
    """
    spec = PassthroughSpec()
    paths = passthrough_paths()

    if cfg.host_network:
        spec.network_mode = "host"
        spec.publish_ports = False
        spec.environment["SSHD_PORT"] = str(cfg.ssh_port)

    if cfg.wayland:
        spec.volumes.append(
            (
                paths["wayland_socket"],
                f"{CONTAINER_RUNTIME_DIR}/{paths['wayland_display']}",
                "rw",
            )
        )
        spec.environment["XDG_RUNTIME_DIR"] = CONTAINER_RUNTIME_DIR
        spec.environment["WAYLAND_DISPLAY"] = paths["wayland_display"]

    if cfg.dbus:
        spec.volumes.append((paths["dbus_bus"], f"{CONTAINER_RUNTIME_DIR}/bus", "ro"))
        spec.environment.setdefault("XDG_RUNTIME_DIR", CONTAINER_RUNTIME_DIR)
        spec.environment["DBUS_SESSION_BUS_ADDRESS"] = (
            f"unix:path={CONTAINER_RUNTIME_DIR}/bus"
        )

    if cfg.gpu:
        gpu = paths["gpu_device"]
        if gpu.startswith("/"):
            # 主机设备节点路径（如 /dev/dri，默认）：映射到容器内 /dev/dri
            spec.devices.append(f"{gpu}:/dev/dri")
        else:
            # CDI 设备引用（如 nvidia.com/gpu=all）：原样透传，由 podman 解析 CDI 规范。
            # NVIDIA WSL2 透传即走此形态——daemon 宿主需已生成 CDI 规范
            # （nvidia-ctk cdi generate → /etc/cdi/nvidia.yaml），见 docs/07 C-I3。
            spec.devices.append(gpu)

    if cfg.usb:
        spec.devices.append(f"{paths['usb_device']}:/dev/bus/usb")

    if cfg.video:
        # UVC 字符设备透传（摄像头采集）：--device <host>:/dev/video<n>（同名映射）。
        # 默认 VIDEO_DEVICES 为 /dev/video0-3，可通过 VIDEO_DEVICES 环境变量精确指定；
        # 宿主无对应节点时 podman 硬失败（exit 125），由 passthrough_diagnose_hint 翻译。
        for dev in paths["video_devices"]:
            spec.devices.append(f"{dev}:{dev}")

    return spec


def passthrough_diagnose_hint(exc_msg: str) -> str:
    """把 podman 对透传资源缺失的**硬失败**翻译为可执行中文指引（诊断条目 C-I3）。

    实测行为（podman 5.7 rootless）：挂载源或设备节点不存在时直接失败，退出码 125，
    且**不会自动创建**该路径，三种写法表现一致：
      - 卷缺失：``Error: statfs /run/user/1000/wayland-0: no such file or directory``
      - 设备缺失：``Error: stat /dev/dri: no such file or directory``

    这些路径由 daemon 宿主解析，客户端本机不可见（见模块头部说明），故只能事后翻译。
    与 windows_diagnose_hint 的 C-I1/C-I2 同属「容器侧坑」诊断家族，编号顺延为 C-I3。
    """
    msg = exc_msg or ""
    if "no such file or directory" not in msg.lower():
        return ""
    if not re.search(r"\b(statfs|stat)\b", msg):
        return ""

    matched = re.search(r"(?:statfs|stat)\s+(\S+?):", msg)
    missing = matched.group(1) if matched else "(见上方原生报错)"

    # B-scheme 宿主 rootless socket 是**必选核心挂载**（与 opt-in 的 wayland/gpu/usb/dbus
    # 不同），其缺失有专门的 C-I5 诊断（UID 漂移 / socket 服务未启动），禁止在此误报
    # 「去掉 --wayland/--gpu 开关」——那会把用户引向完全无关的操作（2026-09-12 实测）。
    if missing.rstrip("/").endswith("podman.sock") or "podman.sock" in msg:
        return ""

    return (
        "[C-I3] 透传资源在 daemon 宿主上不存在（podman 硬失败，退出码 125，且不会自动创建路径）。\n"
        f"     → 缺失路径：{missing}\n"
        "     → 修复（30 秒）：确认该资源在 WSL2 / Podman Machine 内真实存在；"
        "路径不同则用 HOST_XDG_RUNTIME_DIR / HOST_WAYLAND_DISPLAY / DBUS_SESSION_BUS_PATH / "
        "GPU_DEVICE / USB_DEVICE 覆盖；宿主本就不具备该资源时，去掉对应的 --wayland / "
        "--gpu / --usb / --dbus 开关即可。\n"
        "     → 自检：`podman machine ssh \"test -e <路径>\"`（Machine）"
        "或 `wsl -d <Distro> -- test -e <路径>`（WSL2）"
    )


@dataclass
class ContainerConfig:
    """容器运行配置（rootless 三必需参数已内置默认）。

    对应 jpman 日常驾驶纪律中的 rootless 容器三必需：
      - devices = ["/dev/fuse"]
      - security_opt = ["label=disable"]
      - cgroupns = "host"
    """

    image: str = "localhost/jupyter-podman-client:latest"
    name: str = "jupyter-podman"
    ssh_port: int = 2222
    jupyter_port: int = 8888
    workspace: str = "./workspace"
    user_password: str = ""
    jupyter_token: str = ""
    ssh_public_key: str = ""
    grant_sudo: bool = True
    devices: list[str] = field(default_factory=lambda: ["/dev/fuse"])
    security_opt: list[str] = field(default_factory=lambda: ["label=disable"])
    cgroupns: str = "host"
    # entrypoint.sh 需以 root 运行（chpasswd 写 /etc/shadow、写 /root/.jupyter、
    # supervisord 均要求 root；supervisord 内部再降权给 devuser 跑 jupyter/sshd）。
    # client 镜像固化 USER=devuser，运行时必须以 user=root 覆盖，否则 setup_passwords
    # 触发 PAM chpasswd 失败，容器在 set -euo pipefail 下立即退出。
    user: str = "root"
    detach: bool = True

    # ── 运行时透传开关（对齐 docs/07-toolbx-passthrough.md 的 5 项 opt-in）──
    # 全部默认关闭：``compose.yaml`` 的「默认隔离」原则在消费端等价为「默认不传任何
    # 透传参数」。资源路径不进入本 dataclass（否则按 invoke-tasks 规范须各配一个 CLI
    # 旗标），统一由 passthrough_paths() 从环境变量读取。
    # ⚠️ 资源均在 daemon 宿主侧解析，缺失时 podman 硬失败 → 见 C-I3 诊断。
    host_network: bool = False
    wayland: bool = False
    gpu: bool = False
    usb: bool = False
    dbus: bool = False
    video: bool = False

    def resolved_workspace(self) -> Path:
        """将 workspace 解析为**宿主系统**下的绝对路径（用于卷挂载源路径）。

        三语义识别（避免 Windows Python 把 POSIX 绝对路径误判为相对再拼到 cwd 下
        导致 ``/mnt/d/spaces/SpecWeave`` → ``D:\\mnt\\d\\spaces\\SpecWeave`` 这种
        错目录挂载，表现为容器内 ``/workspace`` 下只剩 apps/Untitled.ipynb 这种
        少文件现象）：

        ① 宿主 Windows，输入形如 ``/mnt/<drive>/...`` → 先还原成 ``D:\\...`` 再 resolve
        ② 宿主 Windows，输入形如 ``D:/...`` / ``D:\\...``（带盘符冒号）→ 直接 resolve
        ③ 宿主 Windows，输入以 ``/`` 开头但不是 WSL ``/mnt/<drive>`` 格式
           （如 Unix 绝对路径 ``/workspace``）→ 按原样返回 Path，不要相对拼接
        ④ 宿主 Windows / 非 Windows，输入相对路径（``./workspace`` / ``workspace``）
           → 基于 ``Path.cwd()`` 拼接后 resolve
        ⑤ 非 Windows，输入 POSIX 绝对路径 → Path(...).resolve() 原生处理
        """
        raw = str(self.workspace).strip()
        is_win = platform.system() == "Windows"

        if is_win and raw.startswith("/"):
            m = re.match(r"^/mnt/([a-z])(?:/(.*))?$", raw)
            if m:
                drive = m.group(1).upper()
                rest = (m.group(2) or "").replace("/", "\\")
                return Path(f"{drive}:\\{rest}").resolve()
            return Path(raw)

        ws = Path(raw)
        if not ws.is_absolute():
            ws = Path.cwd() / ws
        return ws.resolve()


@dataclass
class LoadImageResult:
    loaded: bool
    tags: list[str] = field(default_factory=list)
    id: str = ""
    message: str = ""


def image_load_cli_command(runtime: str, tar_path: Path | str) -> str:
    """构造跨平台 ``<runtime> load`` 命令（CLI fallback 唯一事实源）。

    平台矩阵（两条路径不可互相"统一"，各有硬约束）：

    - **Windows 原生 CPython**：``type "<file>" | <runtime> load``。
      ``type`` 是 cmd.exe 的读文件内建命令；保留 stdin 管道是历史实测结论——
      ``-i`` / REST path 方式经 Windows→WSL2 远距 daemon 传输超大镜像时
      会触发 daemon EOF。invoke 在 Windows 的 runner 走 COMSPEC（cmd.exe），
      ``type`` 语义成立。
    - **POSIX（Linux 原生 / WSL2 内 / macOS / 容器内 B-scheme）**：
      ``<runtime> load -i "<file>"``。此处**严禁**使用
      ``type file | ...``（POSIX shell 的 ``type`` 是"显示命令类型"内建，
      zsh 向 stdout 回显路径文本、bash 向 stderr 报 not found，送给 daemon 的
      根本不是 tar 字节流），也不要用 ``cat file | ...``：podman 3.4.x
      （RHEL8/Ubuntu22.04 自带版本）的 stdin 路径对未压缩 docker-archive
      会在 Copying 数个 blob 后误报
      "payload does not match any of the supported image formats"，
      同一文件 ``-i`` 加载正常（2026-09-12 实测）。``-i`` 同时免去对
      cat/type 的依赖与大文件管道的 SIGPIPE 风险。
    """
    path_str = os.fspath(tar_path)
    if platform.system() == "Windows":
        return f'type "{path_str}" | {runtime} load'
    return f'{runtime} load -i "{path_str}"'


def ensure_workspace_checkpoint_writable(workspace: Path | str) -> None:
    """确保工作区根的 Jupyter checkpoint 目录对容器内非 root 服务可写。

    背景（2026-09-14 xmnn-dev 栈实测）：基底 entrypoint 仅对 ``/workspace`` 根
    本身 chmod 777（非递归，保护宿主文件属主），而 Jupyter 经 supervisord 以
    devuser（容器内 uid 1000）运行。rootless podman 经 9p/drvfs 挂载宿主工作区
    时，容器内 root 预建的 ``.ipynb_checkpoints`` 在容器视角属主为 0:0、模式
    755，devuser 无 w 位，保存 notebook 时报
    ``[Errno 13] Permission denied: /workspace/.ipynb_checkpoints/<nb>-checkpoint.ipynb``。

    本函数幂等：目录不存在则创建、存在则放宽到 0777。**只改权限位、不改属主**
    （与 entrypoint 对工作区根的处理同级），且**只作用于这一个固定子目录、不
    递归**——bind 进来的 npu_tvm/npuusertools/models 等源码树是宿主侧独立路径，
    物理上不在作用域内。在宿主侧（WSL uid 即 drvfs 挂载 uid）执行即可透传到
    容器视图（drvfs metadata 模式实测即时生效）。

    失败只警告不抛错：栈启动不应被边缘文件系统语义阻断；工作区根本身可写时，
    Jupyter 首次自建 checkpoint 目录的场景本就不受影响。
    """
    cp = Path(workspace) / ".ipynb_checkpoints"
    try:
        cp.mkdir(parents=True, exist_ok=True)
        cp.chmod(0o777)
    except OSError as exc:
        print(f"[compose] ⚠ 未能放宽 checkpoint 目录权限（Jupyter 保存可能报 Errno 13）：{exc}")
        print(f'        可在宿主侧手动修正：chmod 777 "{cp}"')


# ---------------------------------------------------------------------------
# Windows 原生 → WSL 发行版透明桥接（compose 子进程层的平台门禁平替）
#
# 背景（F/V 阶段 2026-09-15 设计）：
#   quant/xmnn/monetize 三栈的 podman-compose 短语法挂载在 Windows 原生 CPython
#   存在已知缺陷（os.makedirs 误建源路径等），原设计一律 _gate_platform() 门禁
#   Exit(1)。但"门禁"是保护手段而非目标——本质目标 = Windows 原生输入
#   ``invoke <stack>.build`` 能正确构建。已实证的 POSIX 执行环境
#   （podman-machine-default：client 专用 rootless 发行版，与 flapping 的
#   Podman Desktop 默认 machine 相互独立、镜像存储不互通；自带 podman 5.7 +
#   podman-compose + /mnt/d 直通 + client editable 安装）可作为透明桥接目标：
#   把当前 invoke 任务原样转发到发行版内 ``bash -lc`` 执行，stdout/stderr
#   继承透传，返回码原样上抛。桥接不可用（无 wsl.exe / 发行版不存在 /
#   COMPOSE_WSL_DISTRO=none 哨兵）才回退门禁提示。
#
#   为什么不用 WSL_DISTRO_NAME？该键是 SDK 连接（Dimension B）专用；桥接目标
#   用独立键 COMPOSE_WSL_DISTRO。默认 podman-machine-default 为 client 专用
#   rootless 发行版，与 flapping 的 Podman Desktop 默认 machine 相互独立、
#   镜像存储不互通；COMPOSE_WSL_DISTRO 可覆盖目标，none 显式关闭。
# ---------------------------------------------------------------------------
COMPOSE_WSL_DISTRO_ENV = "COMPOSE_WSL_DISTRO"
_DEFAULT_COMPOSE_DISTRO = "podman-machine-default"
# 桥接时透传到 WSL 的**通用**键集（三栈无关）：.env 会被 WSL 内 invoke 再次
# 读取（override=False），这里只补「shell 显式 export 的覆盖值」（保持 shell
# export > .env 优先级）。栈专属键（<PREFIX>_* / 源码路径）不再在此枚举
# （F-10：utils 零栈知识），由 overlay_core.gate_platform 按
# StackSpec.bridge_env_keys 经 extra_env_keys 传入。
# 显式不含 CONTAINER_HOST：不把 Windows SDK URL 带进 compose 子进程层（禁 REST 模式）。
_BRIDGE_COMMON_ENV_KEYS = (
    COMPOSE_WSL_DISTRO_ENV,
    "WSL_DISTRO_NAME",
    "PIP_MIRROR", "CONDA_MIRROR", "BASE_IMAGE",
    "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
    "OMP_NUM_THREADS", "NUITKA_JOBS",
)


@functools.lru_cache(maxsize=4)
def _wsl_distro_available(distro: str) -> bool:
    """探测 WSL 发行版是否可启动（10-15s 超时，结果缓存）。"""
    try:
        cp = subprocess.run(
            ["wsl.exe", "-d", distro, "--", "true"],
            capture_output=True,
            timeout=15,
        )
        return cp.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def _wsl_bridge_distro() -> Optional[str]:
    """解析桥接目标发行版。

    ``COMPOSE_WSL_DISTRO`` 环境变量（Windows 原生进程，含 .env 同步值）：
      - 设为 ``none`` → 显式关闭桥接（回退门禁；上游修复 Windows 原生后逃生舱）；
      - 未设 → 默认 ``podman-machine-default``（client 专用 rootless 发行版，
        与 flapping 的 Podman Desktop 默认 machine 相互独立、镜像存储不互通；
        2026-09-15 起的可靠 compose 执行环境）。
    发行版不可启动返回 None（调用方回退门禁）。
    """
    raw = os.environ.get(COMPOSE_WSL_DISTRO_ENV, "").strip()
    if raw.lower() == "none":
        return None
    candidate = raw or _DEFAULT_COMPOSE_DISTRO
    if platform.system() != "Windows":
        return None
    if _wsl_distro_available(candidate):
        return candidate
    return None


def run_in_wsl_bridge(
    argv: list[str] | None = None,
    extra_env_keys: tuple[str, ...] | list[str] = (),
) -> Optional[str]:
    """Windows 原生把当前 compose 任务透明桥接到 WSL 发行版内执行。

    - 成功：子进程继承 stdio 实时透传（构建日志/中文原样渲染），返回发行版名
      （**调用方必须立即终止本进程继续执行**，桥接子进程已完整跑完任务）；
      子进程非 0 返回码 → ``Exit(rc)`` 原样上抛（防"假成功"）。
    - 不可桥接（非 Windows / 发行版缺失 / none 哨兵 / wsl.exe 无法启动）：
      返回 None，调用方回退门禁提示。
    - extra_env_keys：本栈专属透传键（来自 StackSpec.bridge_env_keys），与
      三栈无关的通用键集合并；utils 自身不再枚举任何具体栈（F-10）。
    """
    if platform.system() != "Windows":
        return None
    distro = _wsl_bridge_distro()
    if not distro:
        return None
    task_cmd = [str(a) for a in (argv or sys.argv[1:])]
    if not task_cmd:
        return None
    # 当前 cwd → WSL POSIX（任务内相对路径解析与 Windows 侧一致）
    workdir = to_posix_path(Path.cwd())
    keys = set(_BRIDGE_COMMON_ENV_KEYS) | set(extra_env_keys)
    exports = " ".join(
        f"{k}={shlex.quote(v)}"
        for k, v in os.environ.items()
        if k in keys and v
    )
    # PATH 前缀双保险（bash -lc 通常已 source profile；找不到 invoke 时仍可命中
    # ~/.local/bin），cwd 先于任务；env 覆盖前缀保持 shell export > .env。
    bash = (
        f"cd {shlex.quote(workdir)} "
        f'&& export PATH="$HOME/.local/bin:$PATH" '
        f"&& {exports} invoke {shlex.join(task_cmd)}"
    )
    try:
        cp = subprocess.run(
            ["wsl.exe", "-d", distro, "--", "bash", "-lc", bash],
        )
    except (FileNotFoundError, OSError) as exc:
        print(f"[compose] ⚠ WSL 桥接启动失败：{exc}")
        return None
    if cp.returncode != 0:
        raise Exit(cp.returncode, f"WSL 桥接命令失败 (exit={cp.returncode})，详见上方输出")
    return distro


def default_build_cache_dir() -> Path:
    """默认镜像缓存目录。

    优先级（同整个 invoke 客户端体系约定）：
      1. 显式 CLI 参数 ``--cache-dir``（调用方在 manage.load 层传入）
      2. 环境变量 ``IMAGE_CACHE_DIR``（来自 shell export 或 cwd/.env）
      3. 当前执行目录 ``Path.cwd() / ".image-cache"``（用户把缓存放 cwd 的默认行为）

    调用方未传 CLI 参数时，可直接调用本函数拿到正确默认值。
    注意：不再默认跳回兄弟目录 ``../jupyter-podman-rootless/.image-cache``，
    避免 ``inv load`` 扫到预期外的路径。
    """
    import os as _os

    env_val = _os.environ.get("IMAGE_CACHE_DIR")
    if env_val:
        return Path(env_val).expanduser().resolve()
    return (Path.cwd() / ".image-cache").resolve()


def find_latest_image_tar(search_dir: Path) -> Optional[Path]:
    """在缓存目录中搜索最新（按 mtime 排序）的镜像 tar/tar.gz。

    同时覆盖 ``*.tar.gz``（构建端 ``jpman save`` 产物）与 ``*.tar``（save 在
    Windows 原生无 gzip/pigz 时的未压缩降级产物），任一扩展名都可能是最新备份。

    跳过符号链接（``*-latest.tar.gz`` 等）：缓存目录里的 latest 链接由
    WSL/9p 侧 ``ln -sf`` 创建，Windows 原生 Python 的 ``os.stat`` 无法解析
    其目标（9p 挂载的符号链接），抛 ``OSError: [WinError 1920]``——修复前
    ``inv load`` 在 Windows 原生下即因此崩溃。真实镜像文件会被正常 glob
    匹配，latest 链接只是冗余别名，跳过不影响"取最新"语义。
    """
    if not search_dir.exists():
        return None
    candidates = []
    for pattern in ("*.tar.gz", "*.tar"):
        for p in search_dir.glob(pattern):
            try:
                if p.is_symlink():
                    continue
                candidates.append((p.stat().st_mtime, p))
            except OSError:
                # 单个坏文件（损坏链接/权限异常）不阻断整体搜索
                continue
    if not candidates:
        return None
    candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates[0][1]


def validate_manifest_integrity(search_dir: Path, tar_path: Path) -> Optional[str]:
    """校验 .image-cache/manifest.txt 中对应文件的 SIZE 和 SHA256。

    返回：无问题返回 None；发现问题返回描述字符串（用于报错）。
    如果 manifest.txt 不存在或文件不在 manifest 中，跳过校验返回 None。
    """
    import hashlib

    manifest_path = search_dir / "manifest.txt"
    if not manifest_path.exists():
        return None

    try:
        content = manifest_path.read_text(encoding="utf-8")
    except Exception:
        return None

    # 解析 manifest：按 "## " 分段，找到 IMAGE_FILE 与当前 tar 文件同名的段。
    # 注意：manifest 首行注释之后紧跟第一个 "## "，split 产生的头部片段需跳过；
    # 段内标题行（## xxx）不含 "="，解析字段时自然被忽略。
    filename = tar_path.name
    blocks = content.split("## ")
    current_fields: dict[str, str] | None = None
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        fields: dict[str, str] = {}
        for line in block.split("\n"):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, _, val = line.partition("=")
                fields[key.strip()] = val.strip()
        # 关键：IMAGE_FILE 必须与当前 tar 文件名完全一致，
        # 否则首个块会被白名单标题行命中，导致永远匹配错镜像。
        if fields.get("IMAGE_FILE") == filename:
            current_fields = fields
            break

    if current_fields is None:
        return None  # 文件不在 manifest 中，跳过校验

    manifest_fields = current_fields

    expected_size_str = manifest_fields.get("SIZE")
    expected_sha256 = manifest_fields.get("SHA256", "").upper()

    if not expected_size_str and not expected_sha256:
        return None

    # 校验 SIZE
    if expected_size_str:
        try:
            num = int(expected_size_str.rstrip("MG"))
            unit = expected_size_str[-1].upper()
            expected_bytes = num * (1024 ** (3 if unit == "G" else 2))
            actual_bytes = tar_path.stat().st_size
            # 允许 10% 浮动（压缩比差异）
            if abs(actual_bytes - expected_bytes) > expected_bytes * 0.10:
                return (
                    f"[Integrity] SIZE 校验失败: manifest={expected_size_str}, "
                    f"实际={actual_bytes / (1024**2):.0f}MB"
                )
        except (ValueError, IndexError):
            pass  # SIZE 格式异常则跳过

    # 校验 SHA256
    if expected_sha256:
        h = hashlib.sha256()
        with open(tar_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        actual_sha256 = h.hexdigest().upper()
        if actual_sha256 != expected_sha256:
            return (
                f"[Integrity] SHA256 不匹配! manifest={expected_sha256[:16]}..., "
                f"实际={actual_sha256[:16]}... — 文件可能已损坏，建议重新保存镜像。"
            )

    return None


def clean_stale_host_keys(cfg: ContainerConfig) -> bool:
    """清理 known_hosts 中本机容器映射端口的过期 host key 条目。

    JPMan 容器每次重建会重新生成 SSH host key（``/etc/ssh/ssh_host_*_key``，
    entrypoint 安全设计：镜像内不携带预生成密钥），导致宿主机 known_hosts
    保留的旧 key 与新容器不匹配，触发 ``REMOTE HOST IDENTIFICATION HAS CHANGED``
    拒绝连接。

    本函数在容器启动前移除 ``[localhost]:{port}`` / ``[127.0.0.1]:{port}``
    的旧条目，消除冲突报错。

    ⚠️ 不得在本函数内用 ssh-keyscan 预写新 key：容器尚未启动、或同名旧容器
    仍在运行时，keyscan 抓取到的是过期 key；新 key 获取须由
    :func:`refresh_host_keys` 在容器真正启动后完成。

    返回 True 表示清理了条目；False 表示无需清理或 known_hosts 不存在。
    调用方：``invoke run`` 的 ``run_container()`` 之前调用。
    """
    known_hosts_path = Path.home() / ".ssh" / "known_hosts"
    if not known_hosts_path.exists():
        return False
    port = str(cfg.ssh_port)
    # 仅匹配本机地址（localhost/127.0.0.1/::1），避免误删其他主机同名端口条目
    pattern_host = re.compile(
        r"^\[(localhost|127\.0\.0\.1|::1)\]:" + re.escape(port) + r"\s+"
    )

    try:
        lines = known_hosts_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        try:
            lines = known_hosts_path.read_text(encoding="utf-8-sig").splitlines()
        except Exception:
            return False

    original_count = len(lines)
    filtered = [line for line in lines if not pattern_host.match(line)]

    if len(filtered) == original_count:
        return False  # 无需更新

    known_hosts_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    print(f"[Run] ✓ known_hosts 已清理 {original_count - len(filtered)} 条过期 host key")
    return True


def refresh_host_keys(cfg: ContainerConfig) -> None:
    """容器启动后获取新容器的 host key 并追加到 known_hosts（尽力而为）。

    调用时机：detach 方式启动容器之后（旧容器已删除，新容器 sshd 需经
    entrypoint 7 步启动才就绪，故先 TCP 探测等待，最长约 20 秒）。ssh-keyscan
    缺失或 sshd 超时未就绪时跳过，首次 SSH 连接会提示输入 ``yes`` 接受新
    host key（因清理先行，不会误报 ``HAS CHANGED``）。

    只追加不重建：避免丢失 known_hosts 中其他主机的既有条目。
    调用方：``invoke run`` 的 ``run_container()`` 之后调用。
    """
    import time as _time

    known_hosts_path = Path.home() / ".ssh" / "known_hosts"
    port = str(cfg.ssh_port)

    # 载入已有条目（去重基准）
    existing: set[str] = set()
    tail_lines: list[str] = []
    if known_hosts_path.exists():
        try:
            tail_lines = known_hosts_path.read_text(encoding="utf-8").splitlines()
            existing = {line for line in tail_lines if line}
        except Exception:
            tail_lines = []

    # Phase 1: 逐个探测本机地址，等待 sshd 就绪。entrypoint 需完成 7 步
    # （含重新生成 host key、supervisord 拉起 sshd）才监听 {port}；容器刚
    # detached 时 keyscan 必扑空。注意 localhost 可能优先解析到未监听的 ::1
    # 而端口转发只绑定 127.0.0.1，故显式尝试两个地址并记录命中的那个。
    import socket as _socket

    probe_addrs = ("127.0.0.1", "::1")
    live_addr: str | None = None
    deadline = _time.monotonic() + 20.0
    while _time.monotonic() < deadline:
        for addr in probe_addrs:
            try:
                with _socket.create_connection((addr, int(port)), timeout=1):
                    live_addr = addr
                    break
            except OSError:
                continue
        if live_addr is not None:
            break
        _time.sleep(0.75)
    if live_addr is None:
        print(f"[Run] ⚠ sshd 在 20 秒内未就绪（port {port}），首次 SSH 连接请输入 yes 接受新 host key")
        return

    # Phase 2: sshd 就绪后 keyscan 获取 host key。用命中地址的 IP 直连以
    # 规避 localhost 双栈解析差异。注意：Windows System32\OpenSSH 的
    # ssh-keyscan KEX 构建集可能无法与 OpenSSH 10 服务器协商
    # （choose_kex: unsupported KEX method sntrup761x25519-sha512），
    # Git 附带的 MSYS ssh-keyscan 兼容性更好，故按序尝试多个候选。
    import shutil as _shutil

    host_keys_pats = (
        f"[{live_addr}]:{port} ",
        f"[localhost]:{port} ",
        f"[127.0.0.1]:{port} ",
        f"[::1]:{port} ",
    )
    keyscan_cands: list[str] = []
    for git_path in (
        r"C:\Program Files\Git\usr\bin\ssh-keyscan.exe",
        r"C:\Program Files\Git\bin\ssh-keyscan.exe",
    ):
        if Path(git_path).exists():
            keyscan_cands.append(git_path)
    which_ks = _shutil.which("ssh-keyscan")
    if which_ks and which_ks not in keyscan_cands:
        keyscan_cands.append(which_ks)

    def _as_localhost(line: str) -> str:
        """将 keyscan 输出行的 host 段规范化为 [localhost]:{port}。

        keyscan 以 IP 为连接目标时输出 ``[127.0.0.1]:2222 ...``，而用户 ssh
        使用 ``devuser@localhost``，known_hosts 按主机名字符串匹配，须改写为
        ``[localhost]:2222 ...``（host key 与连接地址无关）。
        """
        return re.sub(
            r"^(\[[^\]]+\]|[^:\s]+):\d+\s+",
            f"[localhost]:{port} ",
            line,
        )

    for _ in range(3):
        for exe in keyscan_cands:
            try:
                result = subprocess.run(
                    [exe, "-T", "3", "-p", port, live_addr],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
            key_lines = [
                _as_localhost(l.strip())
                for l in (result.stdout or "").splitlines()
                if l and not l.startswith("#")
                and l.startswith(host_keys_pats)
            ]
            if key_lines:
                added = False
                merged = tail_lines[:]
                seen = set(existing)
                for kl in key_lines:
                    if kl not in seen:
                        merged.append(kl)
                        seen.add(kl)
                        added = True
                if added:
                    known_hosts_path.parent.mkdir(parents=True, exist_ok=True)
                    known_hosts_path.write_text("\n".join(merged) + "\n", encoding="utf-8")
                    print(f"[Run] ✓ known_hosts 已更新为新容器 host key ({port})")
                return
        _time.sleep(1)

    print("[Run] ⚠ 未能从 sshd 获取 host key（keyscan 与服务器 KEX 不兼容或 sshd 异常），首次 SSH 连接请输入 yes 接受新 host key")
