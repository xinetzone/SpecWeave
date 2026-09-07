"""镜像消费端工具函数。

提供容器运行时检测、路径转换、命令执行、随机字符串生成、
以及基于 dataclass 的配置对象。与构建端保持接口一致，
但避免跨应用 import，保持消费端的独立性与可移植性。

Windows WSL 支持说明（对齐 podman-py OKF v0.2 §8 Windows 三路径）：
  - **挂载路径转换** (Dimension A)：Windows ``D:\\ws`` → POSIX ``/mnt/d/ws``
    （容器内的 ``/workspace`` 卷挂载源路径，由 :func:`to_posix_path` /
    :func:`normalize_path_str` 负责）
  - **Daemon 连接 URL** (Dimension B)：podman-py SDK 需要的
    ``unix://`` / ``ssh://`` / ``tcp://`` 6 种合法 scheme 之一，
    由本文件新增的 :func:`sdk_base_url_candidates` / :func:`wsl_distro_name`
    负责（与挂载路径解耦，不要混淆）。
"""
import functools
import os
import platform
import re
import secrets
import shutil
import string
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

from invoke import Context, Result
from invoke.exceptions import Exit, UnexpectedExit


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


def sdk_strategy_from_env() -> str:
    """读取逃生舱策略环境变量，非法值回退为 ``auto``。"""
    raw = os.environ.get(SDK_STRATEGY_ENV, "auto").strip().lower()
    return raw if raw in _VALID_STRATEGIES else "auto"


@dataclass
class ContainerConfig:
    """容器运行配置（rootless 三必需参数已内置默认）。

    对应 jpman 日常驾驶纪律中的 rootless 容器三必需：
      - devices = ["/dev/fuse"]
      - security_opt = ["label=disable"]
      - cgroupns = "host"
    """

    image: str = "localhost/jupyter-podman-rootless:latest"
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
    detach: bool = True

    def resolved_workspace(self) -> Path:
        """将 workspace 解析为绝对路径（基于当前 cwd）。"""
        ws = Path(self.workspace)
        if not ws.is_absolute():
            ws = Path.cwd() / ws
        return ws.resolve()


@dataclass
class LoadImageResult:
    loaded: bool
    tags: list[str] = field(default_factory=list)
    id: str = ""
    message: str = ""


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
                encoding="utf-16-le",  # wsl.exe 默认在中文 Windows 输出 UTF-16 LE
                errors="replace",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return ""
        out = cp.stdout or ""
        # 去 BOM / 空行 / 不可见控制符
        return "\n".join(
            line.rstrip("\r").strip("\ufeff")
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
    out = (cp.stdout or "").strip().strip("\ufeff\r\n")
    try:
        return int(out)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# SDK base_url 候选生成（对齐 OKF v0.2 §8 Windows 三路径 + P0 环境变量）
# ---------------------------------------------------------------------------


@dataclass
class BaseUrlCandidate:
    """一个连接候选及其来源说明，失败时附带诊断可给用户。"""

    source: str  # P0-env / P1-wsl-9p / P2-machine / P3-tcp-loopback / legacy
    base_url: Optional[str]  # None 表示"不拼 URL，直接用 PodmanClient() 无参 or from_env()"
    hint: str = ""  # 失败时对用户的提示


def sdk_base_url_candidates(strategy: Optional[str] = None) -> list[BaseUrlCandidate]:
    """按逃生舱 ``strategy`` 生成 podman-py SDK 连接候选列表。

    ``auto`` 策略候选顺序（P0→P1→P2→P3，前一个 ping 成功就停）：
      0. CONTAINER_HOST / DOCKER_HOST 环境变量显式指定
      1. WSL2 9P 互通 socket：``unix:///mnt/wsl/<Distro>/run/user/<UID>/podman/podman.sock``
      2. Podman Machine 命名连接（不传 base_url，PodmanClient() 走 active_service）
      3. TCP 本机回环 ``tcp://127.0.0.1:8888``（用户手动起过 podman system service 才有用）

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
        # base_url=None 表示：直接 PodmanClient() / from_env()，让 SDK 自己
        # 读 containers.conf active_service.is_machine 走 PM-1 / PM-2 命名连接
        candidates.append(
            BaseUrlCandidate(
                source="P2-machine",
                base_url=None,
                hint=(
                    "Podman Machine（Podman Desktop）。请确保：\n"
                    "  1) 打开 Podman Desktop 并点击「Initialize Podman Machine」\n"
                    "  2) 命令行执行一次 `podman machine ssh true` 并在首次交互敲 yes\n"
                    "     （防止 SSH host key 验证卡子进程 stdin → W-I3 Timeout）"
                ),
            )
        )

    # ── P3: TCP 回环兜底（仅 auto，非强制避免误导） ──────────────────────
    if strategy == "auto":
        candidates.append(
            BaseUrlCandidate(
                source="P3-tcp-loopback",
                base_url="tcp://127.0.0.1:8888",
                hint=(
                    "TCP 127.0.0.1:8888。此端口需要用户在 WSL2/Machine 内手动执行：\n"
                    "  podman system service tcp://0.0.0.0:8888 --time=0\n"
                    "生产环境务必追加双向 TLS，不要裸监听。"
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
                    f"请尝试取消设置 {SDK_STRATEGY_ENV}=legacy 改回 auto。"
                ),
            )
        )

    return candidates


def windows_diagnose_hint(exc_type: str, exc_msg: str) -> str:
    """根据捕获到的异常类型+消息，匹配 OKF v0.2 §8.4 W-I1~W-I3 速查表。

    返回空串表示没有匹配到 Windows 专属坑。
    """
    if platform.system() != "Windows":
        return ""
    et = exc_type.lower() if exc_type else ""
    em = (exc_msg or "").lower()

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
    return ""


def detect_runtime() -> str:
    """检测容器运行时，优先 podman。"""
    if shutil.which("podman"):
        return "podman"
    if shutil.which("docker"):
        return "docker"
    raise Exit("未找到 podman 或 docker，请先安装其中之一")


def to_posix_path(path: Path | str) -> str:
    """将路径转换为 POSIX 风格（适配 WSL2/远程 podman）。"""
    p = Path(path)
    path_str = str(p.resolve())
    if platform.system() == "Windows":
        if len(path_str) >= 2 and path_str[1] == ":":
            drive = path_str[0].lower()
            rest = path_str[2:].replace("\\", "/")
            return f"/mnt/{drive}{rest}"
        return path_str.replace("\\", "/")
    return path_str


def normalize_path_str(path_str: str) -> str:
    """规范化路径字符串（保持 podman-compose 卷挂载解析兼容）。

    Windows 路径（``D:\\...``）转 POSIX（``/mnt/d/...``），
    已经是 POSIX（以 ``/`` 开头）或非 Windows 原样返回。
    """
    if platform.system() != "Windows":
        return path_str
    if path_str.startswith("/"):
        return path_str
    if len(path_str) >= 2 and path_str[1] == ":":
        drive = path_str[0].lower()
        rest = path_str[2:].replace("\\", "/")
        return f"/mnt/{drive}{rest}"
    return path_str.replace("\\", "/")


def check_runtime_ready() -> Tuple[bool, Optional[str]]:
    """检查容器运行时服务端是否可达（ping 测试）。"""
    try:
        runtime = detect_runtime()
    except Exit:
        return False, "未找到 podman 或 docker，请先安装其中之一"

    result = subprocess.run(
        [runtime, "version", "--format", "{{.Server.Version}}"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode == 0 and result.stdout.strip():
        return True, None

    if platform.system() == "Windows":
        hint = (
            f"无法连接到 {runtime} 服务。请确保 Podman machine 正在运行：\n"
            f"  podman machine start\n"
            f"如尚未初始化：podman machine init"
        )
    elif platform.system() == "Darwin":
        hint = (
            f"无法连接到 {runtime} 服务。请确保 Podman machine 正在运行：\n"
            f"  podman machine start"
        )
    else:
        hint = (
            f"无法连接到 {runtime} 服务。请检查 Podman 服务状态：\n"
            f"  systemctl --user status podman\n"
            f"  sudo systemctl status podman"
        )
    return False, hint


def run_cmd(
    c: Context,
    cmd: str,
    pty: bool = False,
    hide: bool = False,
    warn: bool = False,
    echo: bool = True,
) -> Optional[Result]:
    """命令执行包装（Windows 显式传完整环境，防止 PATH 被沙箱清空）。"""
    if echo and not hide:
        print(f"执行: {cmd}")
    use_pty = pty and platform.system() != "Windows"
    try:
        return c.run(cmd, pty=use_pty, hide=hide, warn=warn, echo=False, env=os.environ.copy())
    except UnexpectedExit as e:
        if not warn:
            raise
        return e.result


def generate_random_string(length: int = 12) -> str:
    """密码安全的随机字符串（密码 16 位 / token 32 位）。"""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def container_exists(c: Context, runtime: str, name: str) -> bool:
    """检查容器是否存在（包括停止态）。"""
    go_fmt = "{{.Names}}"
    result = run_cmd(
        c,
        runtime + ' ps -a --filter name=^' + name + '$ --format "' + go_fmt + '"',
        hide=True,
        warn=True,
        echo=False,
    )
    return result is not None and result.stdout.strip() == name


def container_running(c: Context, runtime: str, name: str) -> bool:
    """检查容器是否正在运行。"""
    go_fmt = "{{.Names}}"
    result = run_cmd(
        c,
        runtime + ' ps --filter name=^' + name + '$ --format "' + go_fmt + '"',
        hide=True,
        warn=True,
        echo=False,
    )
    return result is not None and result.stdout.strip() == name


def default_build_cache_dir() -> Path:
    """获取构建端默认的镜像缓存目录（供 load 命令默认搜索）。

    返回相对本 client 应用目录的：
        ../jupyter-podman-rootless/.image-cache
    """
    here = Path(__file__).parent.parent.resolve()
    cache = here / ".." / "jupyter-podman-rootless" / ".image-cache"
    return cache.resolve()


def find_latest_image_tar(search_dir: Path) -> Optional[Path]:
    """在缓存目录中搜索最新（按文件名/时间排序）的镜像 tar.gz。"""
    if not search_dir.exists():
        return None
    candidates = sorted(
        search_dir.glob("*.tar.gz"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None
