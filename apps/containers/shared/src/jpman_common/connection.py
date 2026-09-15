"""podman-py SDK 连接统一层（jpman-builder / jpman-client 共享）。

对齐 OKF podman-py 知识包 §8 Windows 三路径，承载：
  - 宿主 rootless 运行时 UID/socket 推导（C-I5：禁硬编码 UID）
  - SDK 连接策略（auto/legacy/wsl/machine 四值白名单）与四级候选
  - :func:`get_client` 上下文管理器（全候选失败才 yield None）
  - W-I1~W-I4 / C-I1/C-I2/C-I5 诊断翻译

scheme 契约（C1）：仅 unix/http+unix/ssh/http+ssh/tcp/http 为 podman-py
合法 scheme；npipe（docker-py 专有）不做任何适配，由 SDK 报错后经
:func:`windows_diagnose_hint` 翻译为 W-I2 指引。
"""
import functools
import json
import os
import platform
import re
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from invoke.exceptions import Exit

from .proc import detect_runtime

# Try importing podman-py SDK（可选依赖：缺失时 get_client 直接 yield None）
try:
    import podman as _podman_sdk
    from podman.errors import APIError, NotFound as PodmanNotFound

    _SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - 环境未安装 [sdk] extras 时
    _podman_sdk = None
    APIError = Exception
    PodmanNotFound = Exception
    _SDK_AVAILABLE = False


# ---------------------------------------------------------------------------
# SDK 连接策略（逃生舱 · 对抗审查 V 阶段产物）
# PODMAN_CLIENT_SDK_STRATEGY 可选值：
#   auto   - 默认，按 P0 环境变量 → P1 WSL9P → P2 Podman Machine → P3 tcp 自动探测
#   legacy - 纯旧行为：直接 from_env()，无任何 Windows 特判
#   wsl    - 强制走 WSL2 9P 互通 socket（要求 wsl.exe 在 PATH + 发行版可探测）
#   machine- 强制走 Podman Machine 命名连接（active_service.is_machine=True）
# ---------------------------------------------------------------------------

SDK_STRATEGY_ENV = "PODMAN_CLIENT_SDK_STRATEGY"
WSL_DISTRO_ENV = "WSL_DISTRO_NAME"
CONTAINER_HOST_ENVS = ("CONTAINER_HOST", "DOCKER_HOST")  # 原生优先兼容兜底
_VALID_STRATEGIES = {"auto", "legacy", "wsl", "machine"}


# ── B-scheme: host podman rootless socket pass-through ──────────
# 背景：容器内自建 daemon（Model A）在 WSL 三层 userns 嵌套下触发
# `newuidmap Operation not permitted`，不可行。改为直连宿主 rootless daemon：
# 把宿主 `/run/user/<uid>/podman/podman.sock` bind-mount 进容器同一路径，
# 并设置 `HOST_PODMAN_SOCK`，让容器内 entrypoint 的 B-scheme 分支建立符号链接、
# 设置 `CONTAINER_HOST`，从而令容器内 podman SDK/CLI 复用宿主 daemon。
def host_runtime_uid() -> str:
    """daemon 宿主运行时 UID（B-scheme socket/透传路径推导的**唯一事实源**）。

    推导优先级：
      1. 显式 ``PODMAN_RUNTIME_UID``（跨主机场景：客户端在 Windows 原生、
         daemon 在 WSL2/Machine，或 daemon 宿主 UID 与客户端不同）；
      2. POSIX 本机 ``$XDG_RUNTIME_DIR`` 末段（形如 ``/run/user/1006`` → 1006）；
      3. POSIX 本机 ``os.getuid()``；
      4. Windows 原生回落 ``"1000"``（WSL2 默认用户惯例；本机 UID 无意义）。

    历史教训（2026-09-12，C-I5）：曾无条件默认 "1000"，在 UID=1006 的原生
    Linux 宿主上生成不存在的 ``/run/user/1000/...`` 挂载源，podman run 硬失败
    exit=125（statfs no such file）。UID 必须来自运行时事实而非发行版惯例。
    """
    explicit = os.environ.get("PODMAN_RUNTIME_UID", "").strip()
    if explicit:
        return explicit
    if platform.system() != "Windows":
        xdg = os.environ.get("XDG_RUNTIME_DIR", "")
        m = re.search(r"/run/user/(\d+)$", xdg)
        if m:
            return m.group(1)
        return str(os.getuid())
    return "1000"


def podman_sock_path() -> str:
    """Host rootless daemon socket path (also used as container mount target)."""
    return f"/run/user/{host_runtime_uid()}/podman/podman.sock"


def host_runtime_dir() -> str:
    """daemon 宿主的用户运行时目录 ``/run/user/<uid>``（UID 约定同 host_runtime_uid）。"""
    return f"/run/user/{host_runtime_uid()}"


def bsock_missing_guidance(detail: str = "") -> str:
    """C-I5：B-scheme 宿主 rootless socket 缺失的可执行中文指引。

    与 C-I3（opt-in 透传资源）区分：该 socket 是必选核心挂载，
    缺失只有两类根因——UID 漂移（推导路径错误）或 socket 服务未启动。
    """
    uid = host_runtime_uid()
    sock = podman_sock_path()
    lines = [
        "[C-I5] B-scheme 宿主 rootless socket 挂载源不存在（podman run 必然 statfs 硬失败，exit=125）。",
        f"     → 目标路径：{sock}（推导 UID={uid}）",
        "     → 修复（按顺序）：",
        "       1) 核对 UID：本机执行 `id -u`；若与上方 UID 不符，导出 "
        "`PODMAN_RUNTIME_UID=<id -u 的值>`（或写入客户端 .env）后重试",
        "       2) 启动用户级 API socket：`systemctl --user start podman.socket`"
        "（本工具在原生 Linux 上会尝试自动执行此步；无 systemd 的环境改手工运行 "
        "`podman system service --time=0 unix:///run/user/$(id -u)/podman/podman.sock`）",
        "       3) 重启后仍丢失则开启 lingering：`sudo loginctl enable-linger $USER`",
    ]
    if detail:
        lines.append(f"     → 自动启动失败详情：{detail}")
    return "\n".join(lines)


def ensure_host_podman_socket() -> tuple[bool, str, bool]:
    """原生 Linux 上预检并尽力自愈 B-scheme 宿主 socket。

    返回 ``(就绪, 诊断明细, 是否本次自动拉起)``。以下场景**直接放行**
    （本机文件系统无法代表 daemon 宿主判断，交给远端 C-I1/C-I3 体系）：
      - 非 Linux（Windows/macOS 的 daemon 在 WSL2/Podman Machine 远端）；
      - 已在 B-scheme 容器内（``HOST_PODMAN_SOCK`` 已注入，socket 是 bind-mount 产物，
        绝不能在容器内去 systemctl 宿主单元）；
      - 运行时不是 podman；
      - socket 文件已存在。

    自愈仅限用户级 systemd 单元（``systemctl --user start podman.socket``）：
    无需提权、可逆、带 10s 超时；任何异常都降级为 C-I5 指引，绝不阻断在非预期环境。
    """
    if platform.system() != "Linux" or os.environ.get("HOST_PODMAN_SOCK"):
        return True, "", False
    try:
        if detect_runtime() != "podman":
            return True, "", False
    except Exit:
        return True, "", False

    sock = podman_sock_path()
    if Path(sock).exists():
        return True, "", False

    systemctl = shutil.which("systemctl")
    if not systemctl:
        return False, "本机无 systemctl（非 systemd 环境），需手工启动 podman system service", False
    try:
        result = subprocess.run(
            [systemctl, "--user", "start", "podman.socket"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return False, "systemctl --user start podman.socket 超时（>10s）", False
    except OSError as exc:
        return False, f"systemctl 调用失败：{exc}", False

    if Path(sock).exists():
        return True, "", True
    detail = (result.stderr or result.stdout or "systemctl 返回成功但 socket 文件仍不存在").strip()
    return False, detail, False


def sdk_available() -> bool:
    """podman-py 模块是否已安装。"""
    return _SDK_AVAILABLE


def sdk_strategy_from_env() -> str:
    """读取逃生舱策略环境变量，非法值回退为 ``auto``。"""
    raw = os.environ.get(SDK_STRATEGY_ENV, "auto").strip().lower()
    return raw if raw in _VALID_STRATEGIES else "auto"


# ---------------------------------------------------------------------------
# Windows WSL 平台探测（Dimension B：Daemon 连接 URL）
# 区分两种"跑在 Windows 上"的场景（边界声明，避免维护者踩坑）：
#   HOST Windows: platform.system() == "Windows"，Python 宿主原生 CPython
#       → 需要 wsl.exe 与 /mnt/wsl/ 9P 互通路径
#   WSL内部 Linux: platform.system() == "Linux" 且 WSL_DISTRO_NAME 非空
#       → 直接默认 unix:///run/user/$UID/podman/podman.sock，不走本模块分支
# ---------------------------------------------------------------------------


def _has_wsl_host_support() -> bool:
    """宿主 Windows 侧是否具备 WSL2 互操作基本条件。

    双门卫：① ``wsl.exe`` 在 PATH 可见  ② ``/mnt/wsl/`` 9P 互通挂载点存在。
    任一不满足直接返回 ``False``，避免后续候选尝试抛 IO 拖慢启动。
    """
    if platform.system() != "Windows":
        return False
    if shutil.which("wsl.exe") is None:
        return False
    try:
        return Path("/mnt/wsl/").exists()
    except OSError:
        return False


@functools.lru_cache(maxsize=1)
def wsl_distro_name() -> Optional[str]:
    """WSL2 发行版名三级回退探测（结果全局缓存）。

    回退顺序（对应 G3 模式「WSL2 发行版名 3 级回退」）：
      ① 环境变量 ``WSL_DISTRO_NAME``（宿主进程被 wsl.exe -d 启动时会带）
      ② ``wsl.exe --list --quiet`` 第一行 = 默认发行版
      ③ ``wsl.exe --list --verbose`` 中 ``State == Running`` 的首个
    都取不到返回 ``None``，上层候选会跳过 WSL9P 分支。
    """
    env_val = os.environ.get(WSL_DISTRO_ENV)
    if env_val:
        return env_val.strip() or None

    if not _has_wsl_host_support():
        return None

    def _run_wsl(*args: str) -> str:
        try:
            cp = subprocess.run(
                ["wsl.exe", *args],
                capture_output=True,
                text=True,
                timeout=5,
                encoding="utf-16-le",  # wsl.exe 默认在中文 Windows 输出 UTF-16 LE（C6）
                errors="replace",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""
        out = cp.stdout or ""
        # 去 BOM / 空行 / 不可见控制符
        return "\n".join(
            line.rstrip("\r").strip("﻿")
            for line in out.splitlines()
            if line.strip()
        )

    default_raw = _run_wsl("--list", "--quiet")
    if default_raw:
        first = default_raw.splitlines()[0].strip()
        if first:
            return first

    verbose = _run_wsl("--list", "--verbose")
    if verbose:
        # 表头形如 "  NAME            STATE           VERSION"
        lines = verbose.splitlines()[1:]
        for line in lines:
            parts = re.split(r"\s{2,}", line.strip())
            if len(parts) >= 3 and parts[1].lower() == "running":
                return parts[0]
    return None


@functools.lru_cache(maxsize=8)
def _wsl_user_uid(distro: str) -> Optional[int]:
    """探测给定发行版内默认用户的 UID（结果缓存）。

    不硬编码 1000（对抗审查 V 视角2 加固）：有些发行版默认用户改了 UID，
    硬编码会导致 ``/run/user/1000/podman/podman.sock`` 不存在但真实 socket 在
    其他 UID 下的"看似连不上其实路径拼错"伪故障。
    """
    if not distro:
        return None
    try:
        cp = subprocess.run(
            ["wsl.exe", "-d", distro, "id", "-u"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-16-le",
            errors="replace",
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
    out = (cp.stdout or "").strip().strip("﻿\r\n")
    try:
        return int(out)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# SDK base_url 候选生成（对齐 OKF §8 Windows 三路径 + P0 环境变量）
# ---------------------------------------------------------------------------


class BaseUrlCandidate:
    """一个连接候选及其来源说明，失败时附带诊断可给用户。"""

    def __init__(self, source: str, base_url: Optional[str], hint: str = ""):
        self.source = source  # P0-env / P1-wsl-9p / P2-machine / legacy
        # None 表示"不拼 URL，直接用 PodmanClient() 无参 or from_env()"
        self.base_url = base_url
        self.hint = hint  # 失败时对用户的提示


def sdk_base_url_candidates(strategy: Optional[str] = None) -> list[BaseUrlCandidate]:
    """按逃生舱 ``strategy`` 生成 podman-py SDK 连接候选列表。

    ``auto`` 策略候选顺序（P0→P1→P2→P3，前一个 ping 成功就停）：
      0. CONTAINER_HOST / DOCKER_HOST 环境变量显式指定
      1. WSL2 9P 互通 socket：``unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock``
      2. Podman Machine 命名连接（不传 base_url，PodmanClient() 走 active_service）
      3. 兜底 legacy：from_env()（无任何候选时追加）

    其他策略：强制只保留对应分支，便于用户紧急逃生。
    """
    if strategy is None:
        strategy = sdk_strategy_from_env()

    candidates: list[BaseUrlCandidate] = []

    # ── P0: 用户显式环境变量（所有策略除 legacy 外都先看一眼） ────────────
    if strategy != "legacy":
        for env_key in CONTAINER_HOST_ENVS:
            val = os.environ.get(env_key)
            if val:
                candidates.append(
                    BaseUrlCandidate(
                        source="P0-env",
                        base_url=val,
                        hint=f"环境变量 {env_key}={val}（若连不上请检查值是否合法，"
                        f"scheme 仅支持 unix/http+unix/ssh/http+ssh/tcp/http）",
                    )
                )
                break  # 原生优先兜底：CONTAINER_HOST 读到就不再读 DOCKER_HOST

    is_host_windows = platform.system() == "Windows"

    # ── P1: WSL2 9P 互通 socket（auto / wsl 强制） ────────────────────────
    if strategy in {"auto", "wsl"} and is_host_windows:
        distro = wsl_distro_name()
        if distro:
            uid = _wsl_user_uid(distro)
            if uid is not None:
                socket_path = f"/mnt/wsl/{distro}/run/user/{uid}/podman/podman.sock"
                candidates.append(
                    BaseUrlCandidate(
                        source="P1-wsl-9p",
                        base_url=f"unix://{socket_path}",
                        hint=(
                            f"WSL2 发行版={distro} UID={uid}。"
                            f"请在 WSL2 内执行：\n"
                            f"  sudo loginctl enable-linger $USER\n"
                            f"  systemctl --user enable --now podman.socket\n"
                            f"  ls -l {socket_path}  # 确认 socket 存在"
                        ),
                    )
                )
            else:
                # 发行版探测到了但拿不到 UID，给个带说明的空候选，失败时用户知道为什么
                candidates.append(
                    BaseUrlCandidate(
                        source="P1-wsl-9p",
                        base_url=None,
                        hint=(
                            f"WSL2 发行版={distro} 但无法通过 `wsl.exe -d {distro} id -u` 拿到 UID。"
                            "请确认该发行版已启动并能正常进入 shell。"
                        ),
                    )
                )
        elif strategy == "wsl":
            # 用户强制 wsl 策略但发行版探不到 → 失败时要明确告诉怎么设 env
            candidates.append(
                BaseUrlCandidate(
                    source="P1-wsl-9p",
                    base_url=None,
                    hint=(
                        "SDK_STRATEGY=wsl 但未探测到 WSL2 发行版。请在当前终端先设：\n"
                        "  $env:WSL_DISTRO_NAME=\"Ubuntu\"   # PowerShell\n"
                        "  export WSL_DISTRO_NAME=Ubuntu     # bash（如果是在 WSL 内部 shell）"
                    ),
                )
            )

    # ── P2: Podman Machine（auto / machine 强制） ────────────────────────
    if strategy in {"auto", "machine"}:
        # Windows 原生：from_env()/无参构造依赖 os.getuid（podman.api.path_utils）
        # 与 unix 适配需要 socket.AF_UNIX，Windows 原生 CPython 两者皆缺 → 必然 AttributeError。
        # 绕开 crash：直接探测宿主 `podman system connection list` 的默认连接
        # （Podman Desktop 初始化时自动写入 containers.conf），拿到 ssh:// 显式 base_url。
        # Linux 原生无此问题，保持 base_url=None 走 SDK 自身的 active_service 解析。
        fallback_url = machine_connection_uri() if is_host_windows else None
        candidates.append(
            BaseUrlCandidate(
                source="P2-machine",
                base_url=fallback_url,
                hint=(
                    "Podman Machine（Podman Desktop）。请确保：\n"
                    "  1) 打开 Podman Desktop 并点击「Initialize Podman Machine」\n"
                    "  2) 命令行执行一次 `podman machine ssh true` 并在首次交互敲 yes\n"
                    "     （防止 SSH host key 验证卡子进程 stdin → W-I3 Timeout）"
                ),
            )
        )

    # ── legacy 逃生舱：回到旧的纯 from_env() 行为 ────────────────────────
    if strategy == "legacy" or not candidates:
        candidates.append(
            BaseUrlCandidate(
                source="legacy",
                base_url=None,
                hint=(
                    "（legacy 策略）直接 from_env()。若在 Windows 原生失败，"
                    f"请尝试取消设置 {SDK_STRATEGY_ENV}=legacy 改回 auto，"
                    "或显式设置 CONTAINER_HOST=tcp://127.0.0.1:<port>（仅当手动执行过"
                    " podman system service tcp://... --time=0 才有效）。"
                ),
            )
        )

    return candidates


@functools.lru_cache(maxsize=1)
def machine_connection_uri() -> Optional[str]:
    """Windows 原生下探测 Podman Machine 默认连接的显式 base_url。

    通过 ``podman system connection list --format json`` 读取 Default=true 的连接
    （Podman Desktop 初始化时会把 Machine 的 ssh:// URI 写入 containers.conf 的
    [engine].active_service，CLI fallback 正是借此连接的）。

    返回 ssh:// URI（如 ``ssh://user@127.0.0.1:63851/run/user/1000/podman/podman.sock``）
    或 None（探测失败：podman CLI 不在 PATH / 无 Machine / 非 Windows）。

    Windows 原生下必须绕开 ``from_env()``（其回退链调用 ``podman.api.path_utils.get_runtime_dir()``
    依赖 ``os.getuid()``，Windows 无此属性 → AttributeError），故 P2 候选在 Windows 用
    本函数的返回值作显式 base_url；Linux 原生 ``from_env()`` 正常，无需此探测。
    """
    if platform.system() != "Windows":
        return None
    runtime = shutil.which("podman")
    if not runtime:
        return None
    try:
        cp = subprocess.run(
            [runtime, "system", "connection", "list", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=8,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if cp.returncode != 0 or not (cp.stdout or "").strip():
        return None
    try:
        conns = json.loads(cp.stdout)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(conns, list):
        return None
    for conn in conns:
        if isinstance(conn, dict) and conn.get("Default") and conn.get("URI"):
            uri = str(conn["URI"]).strip()
            if uri.startswith(("ssh://", "unix://", "tcp://")):
                return uri
    return None


def windows_diagnose_hint(exc_type: str, exc_msg: str) -> str:
    """根据捕获到的异常类型+消息，匹配 OKF §8.4 W-I1~W-I3 + 容器内坑 C-I1/C-I2 速查表。

    返回空串表示没有匹配到已知坑。
    注意：C-I2 是**容器内坑（平台无关）**，其分支必须置于 Windows 平台守卫之前，
    否则容器内（Linux）的 EACCES 永远匹配不到。
    """
    et = exc_type.lower() if exc_type else ""
    em = (exc_msg or "").lower()

    # C-I2：容器内 devuser 访问宿主直通 podman socket 被拒（EACCES，平台无关 → 先于平台守卫）
    _is_eacces = (
        "permissionerror" in et
        or "errno 13" in em
        or "permission denied" in em
        or "eacces" in em
    )
    _is_c1_like = "libpod/tmp" in em or "temporary file" in em
    if _is_eacces and not _is_c1_like and "/run/user/" in em and "podman" in em:
        return (
            "[C-I2] 容器内 devuser 无权访问宿主直通 podman socket（Errno 13 / EACCES，容器内坑，与平台无关）。\n"
            "     → 根因：宿主 rootless socket（宿主 <uid>:<gid> 0660）经 userns 映射进容器后呈现为 root:root 0660，\n"
            "        而 devuser 是非 root UID（固定 1000，≠0）且未加入 socket 属组，socket.connect() 直接 EACCES。\n"
            "     → 修复（30 秒）：重建镜像并重启容器——entrypoint.sh::setup_podman() 的 B-scheme 分支会自动\n"
            "        执行 usermod -aG <socket组> ${NON_ROOT_USER}（必须早于 exec supervisord，jupyter 子进程才能继承补充组）\n"
            "        并以 devuser 身份实测 socket 可读写；严禁 chmod 666 / chown 宿主 socket（会破坏宿主侧权限）。\n"
            "     → 自检：容器内 `supervisorctl status jupyter` 取 PID 后看 /proc/<pid>/status 的 Groups 应含 socket 属组。"
        )

    if platform.system() != "Windows":
        return ""

    # W-I1：无参构造回退 /run/user/$UID 不存在
    if (
        "filenotfounderror" in et
        or "no such file or directory" in em
    ) and "/run/user/" in em:
        return (
            "[W-I1] podman-py 默认 socket 路径是纯 Linux 语义，在 Windows 原生不存在。\n"
            "     → 修复（30 秒）：三种方式任选其一：\n"
            "        a) 改在 WSL2 里跑本脚本（100% Linux 行为）\n"
            "        b) 打开 Podman Desktop 初始化 Podman Machine（推荐零配置）\n"
            "        c) 显式设 CONTAINER_HOST=unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock"
        )

    # W-I2：docker-py 老用户写 npipe://
    if "unsupported url scheme" in em and "npipe" in em:
        return (
            "[W-I2] podman-py 不支持 Windows 命名管道 npipe://（docker-py 专有）。\n"
            "     → 修复（30 秒）：把 base_url 改成：\n"
            "        unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock  或\n"
            "        ssh://user@127.0.0.1:<MachinePort>  或 tcp://127.0.0.1:8888"
        )

    # W-I3：SSH 模式 Waiting on podman-forward-*.sock 超时
    if ("timeout" in et or "timeoutexpired" in et) and "podman-forward" in em:
        return (
            "[W-I3] SSH 隧道子进程卡在首次 host key 交互（std 阻塞在 yes/no 提问）。\n"
            "     → 修复（30 秒）：命令行先手动执行一次 `podman machine ssh true`\n"
            "        在 Are you sure ...? 提示后敲 yes 回车，把 machine key 写进 known_hosts。"
        )

    # W-I4：Windows 原生 CPython 缺少 POSIX 专属属性（os.getuid / socket.AF_UNIX）。
    if (
        "attributeerror" in et
        and ("getuid" in em or "af_unix" in em)
    ) or (
        "has no attribute" in em and ("getuid" in em or "af_unix" in em)
    ):
        return (
            "[W-I4] podman-py 在 Windows 原生 CPython 结构性不可用（依赖 POSIX 专属属性）。\n"
            "     → 根因：from_env() 回退链调用 os.getuid()；unix/ssh 适配调用 socket.AF_UNIX，\n"
            "        Windows 原生 Python 两者皆无 → AttributeError。与配置无关，SDK 无法在此平台直连。\n"
            "     → 修复（30 秒）：本工具已自动降级 CLI fallback（podman.exe 子进程，可用）；\n"
            "        如需 SDK 路径，a) 改在 WSL2 内跑本脚本（100% Linux 行为），\n"
            "        b) 或显式设 CONTAINER_HOST=ssh://user@127.0.0.1:<MachinePort>/run/user/1000/podman/podman.sock\n"
            "        （端口可用 `podman system connection list --format json` 查询）"
        )
    return ""


@contextmanager
def get_client():
    """获取 PodmanClient 的上下文管理器（SDK 不可达时 yield None）。

    按 ``PODMAN_CLIENT_SDK_STRATEGY``（默认 ``auto``）依次尝试候选：
    P0 环境变量显式 URL → P1 WSL2 9P socket → P2 Podman Machine → legacy，
    全部失败时输出降级诊断（PODMAN_CLIENT_LOG_LEVEL=DEBUG 打印完整清单），
    然后 yield None 进入 CLI fallback。**行为承诺**：所有候选都失败时才返回
    ``None``，调用方 ``if client is not None:`` 判断无需修改。
    """
    if not _SDK_AVAILABLE:
        yield None
        return

    strategy = sdk_strategy_from_env()
    candidates = sdk_base_url_candidates(strategy)

    attempts: list[dict] = []
    client = None

    def _close_safe(c):
        if c is None:
            return
        try:
            c.close()
        except Exception:
            pass

    try:
        for cand in candidates:
            this_client = None
            try:
                if cand.base_url is None:
                    # None → 走 SDK 默认分支：from_env() / 无参 PodmanClient()，
                    # 让其自身读取 containers.conf active_service（含 PM-1 PM-2 Machine）
                    this_client = _podman_sdk.from_env()
                else:
                    this_client = _podman_sdk.PodmanClient(base_url=cand.base_url)
                ping_result = this_client.ping()
                # podman-py 5.x ``system.ping()`` 返回 bool（HTTP response.text == "OK"）。
                # 严格 True 才当选：防止 ping 返回 False（打到 Jupyter/其他 HTTP 服务，
                # 200 OK 但 body 不是 "OK"）时错误选中假 client。
                if ping_result is not True:
                    raise RuntimeError(
                        f"ping()={ping_result!r}，未返回 True"
                        f"（可能连接到非 Podman daemon，如其他监听该端口的服务）"
                    )
                # 成功：把这个 client 作为最终 yield 的，跳出循环
                client = this_client
                this_client = None
                break
            except Exception as exc:  # noqa: BLE001 - 失败需要记录信息，不能吞
                attempts.append(
                    {
                        "source": cand.source,
                        "base_url": cand.base_url,
                        "hint": cand.hint,
                        "exc_type": type(exc).__name__,
                        "exc_msg": str(exc),
                    }
                )
            finally:
                _close_safe(this_client)

        if client is not None:
            yield client
            return

        # 所有候选全部失败：
        #   - LOG_LEVEL=DEBUG 才打印完整候选诊断（每轮10+行，避免每次调用打印噪音）
        #   - 普通 INFO 级仅 1 行「[INFO][降级]」统一前缀，用户一眼懂：不是失败=降级
        log_level = (os.environ.get("PODMAN_CLIENT_LOG_LEVEL") or "INFO").upper()
        is_debug = log_level in {"DEBUG", "TRACE"}
        first_err = attempts[0] if attempts else {"exc_type": "Unknown", "source": "-"}
        print(
            "[INFO][降级] SDK路径不可用（首候选="
            f"{first_err['source']} {first_err['exc_type']}）→ 走CLI fallback"
            f"（PODMAN_CLIENT_LOG_LEVEL=DEBUG 打印完整诊断）"
        )
        if is_debug:
            print("[SDK-DEBUG] 全部连接候选失败，降级到 CLI。诊断清单：")
            print(f"           strategy = {strategy} (通过 {SDK_STRATEGY_ENV} 修改)")
            for i, att in enumerate(attempts, 1):
                src = att["source"]
                url = att["base_url"] or "(SDK 自行读 from_env/containers.conf)"
                print(f"    [{i}/{len(attempts)}] source={src}")
                print(f"          base_url = {url}")
                print(f"          错误     = {att['exc_type']}: {att['exc_msg']}")
                if att["hint"]:
                    for line in att["hint"].splitlines():
                        print(f"          提示     = {line}")
            last = attempts[-1] if attempts else {"exc_type": "", "exc_msg": ""}
            hint = windows_diagnose_hint(last["exc_type"], last["exc_msg"])
            if hint:
                print("[SDK-DEBUG] 已知坑匹配（W-I1~W-I3 / C-I1~C-I2）:")
                for line in hint.splitlines():
                    print(f"           {line}")
        yield None
    finally:
        _close_safe(client)


__all__ = [
    "APIError",
    "PodmanNotFound",
    "sdk_available",
    "get_client",
    "host_runtime_uid",
    "podman_sock_path",
    "host_runtime_dir",
    "ensure_host_podman_socket",
    "bsock_missing_guidance",
    "sdk_strategy_from_env",
    "sdk_base_url_candidates",
    "BaseUrlCandidate",
    "wsl_distro_name",
    "machine_connection_uri",
    "windows_diagnose_hint",
    "SDK_STRATEGY_ENV",
    "WSL_DISTRO_ENV",
    "CONTAINER_HOST_ENVS",
]
