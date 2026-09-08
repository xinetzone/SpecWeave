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
import ctypes
import functools
import os
import platform
import re
import secrets
import shutil
import string
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

from invoke import Context, Result
from invoke.exceptions import Exit, UnexpectedExit


# ---------------------------------------------------------------------------
# Windows 双端字符集修复（模块级单例，防止 run_cmd 被重复调用 100+ 次时重复执行）。
#
# 乱码根因（三层模型，V 阶段对抗验证得出）：
#   ① 容器/Linux 输出的 bytes 永远 = UTF-8。
#   ② Trae Sandbox 把整个 Python 进程树的 stdout/stderr 以 PIPE 方式重定向，
#      并按宿主 Windows 默认 cp936(GBK) 解码 PIPE bytes → 经典错位乱码
#      （``清理`` → UTF-8 bytes → GBK 解读 → ``娓呯悊``）。
#   ③ invoke c.run() 内部 subprocess.Popen(stdout=PIPE) 同样按
#      locale.getpreferredencoding() = cp936 decode，在 Python 内部 Result.stdout
#      阶段就已经乱码，后续写入即使是 Console Handle 也无法救回。
#
# 双端修复策略（两端同时生效才闭环，缺一不可）：
#   A. 宿主打印端：sys.stdout/stderr.reconfigure(encoding=<宿主编码>, errors='replace')
#      → 宿主 print("执行：...") 写成 cp936 bytes，Sandbox 按 cp936 解码 → 中文正确。
#   B. 子进程捕获端：c.run(..., encoding='utf-8') 强制按 UTF-8 解码子进程 stdout
#      → Result.stdout 里的 str 就是正确中文，再走 A 路径编码成宿主 bytes。
#   辅助：SetConsoleOutputCP(65001)（非 Sandbox 原生 Console 的情况下生效，
#      做 defense-in-depth，失败静默）。
# ---------------------------------------------------------------------------
_WIN32_STDOUT_TRANSCODE_READY = False


def _ensure_win32_stdout_transcode() -> tuple[str, bool]:
    """Windows 双端字符集初始化（TTY / PIPE 分路径策略）。

    返回值 ``(subproc_encoding, is_tty_console)``：
        - ``subproc_encoding``：传给 invoke ``c.run(encoding=...)`` 的值；空串表示走默认。
        - ``is_tty_console``：True = 原生 TTY Console，可 bypass invoke PIPE 捕获层
                                用 ``subprocess.call(shell=True, stdout=None)`` 直接继承 Console Handle；
                              False = 被外层 Sandbox/PIPE 重定向，必须走 invoke c.run + Python stdout 重编码。

    只 Windows 执行，其他平台直接返回 ``("", False)``。初始化完成后单例标记不再重复执行。

    分路径策略（V阶段对抗验证出的双环境分裂）：
      1. 原生 TTY Console（用户在自己的 PowerShell / cmd / IDE Terminal 直接跑 invoke）
         → 子进程（podman/docker/...）直接继承 Console Handle 写入，
            只要把 SetConsoleOutputCP/SetConsoleCP 切到 65001，并把 PowerShell
            Console::OutputEncoding/InputEncoding 改成 UTF8，
            再加 sys.stdout/stderr 的 TextIOWrapper encoding=utf-8，中文就能 100% 正确渲染。
      2. 外层 PIPE 捕获（Trae Sandbox / CI 重定向 stdout）
         → Python 进程树 stdout 是 PIPE 而非 Console Handle，
            SetConsoleOutputCP 对 PIPE 解码端无效；必须把 sys.stdout/stderr
            的 TextIOWrapper encoding 改成 GetConsoleOutputCP() 的宿主原生编码（通常 cp936），
            保证 write 端 bytes 与外层 capture 端的解码编码匹配，才能把正确中文传出去。
    """
    global _WIN32_STDOUT_TRANSCODE_READY
    if platform.system() != "Windows":
        return "", False
    if _WIN32_STDOUT_TRANSCODE_READY:
        # 注意：第一次初始化时已把 (subproc_encoding, is_tty_console) 缓存在闭包外
        return _WIN32_TRANSCODE_CACHED_RESULT

    kernel32 = None
    console_cp = 0
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        # ⚠ 先 Get 再 Set：启动时的真实 Console CP 才是宿主/PIPE 捕获端的解码编码；
        # SetConsoleOutputCP(65001) 会让后续 GetConsoleOutputCP() 返回 65001，影响判断。
        console_cp = kernel32.GetConsoleOutputCP()
        CP_UTF8 = 65001
        # 原生 TTY Console 时才需要 Set*CP：PIPE 场景下此调用无副作用也无效
        kernel32.SetConsoleOutputCP(ctypes.c_uint(CP_UTF8))
        kernel32.SetConsoleCP(ctypes.c_uint(CP_UTF8))
    except Exception:
        console_cp = 0

    # ── TTY vs PIPE 判别 ──
    is_tty = False
    try:
        is_tty = os.isatty(sys.stdout.fileno())
    except Exception:
        is_tty = False  # 典型：sys.stdout 被重定向成 StringIO

    subproc_encoding = ""
    if is_tty:
        # 路径 1：原生 TTY Console
        #   SetConsoleOutputCP 已切到 65001；现在把 PowerShell [Console]::OutputEncoding 也
        #   改到 UTF8（影响用 PowerShell CreateProcess 启动的子进程在父 PS 里的编码行为）。
        try:
            import io as _io

            try:
                from System import Console as _NETConsole  # type: ignore
                from System.Text import Encoding as _NETEncoding  # type: ignore
                _utf8 = _NETEncoding.UTF8
                _NETConsole.OutputEncoding = _utf8
                _NETConsole.InputEncoding = _utf8
            except Exception:
                # .NET interop 不可用时回退到 chcp.com（外部命令，副作用大）
                try:
                    import subprocess as _sp
                    _sp.run(
                        ["chcp.com", "65001"],
                        stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, check=False,
                    )
                except Exception:
                    pass
        except Exception:
            pass
        # A 端：sys.stdout / stderr 写 UTF-8 bytes → Console 按 CP65001 渲染 → 中文正确
        _wrap_stdio_encoding("utf-8")
        # B 端：invoke c.run 捕获子进程 bytes → 源头按 UTF-8 解码才会得到正确 str
        subproc_encoding = "utf-8"
    else:
        # 路径 2：外层 PIPE 捕获（Trae Sandbox / CI）
        #   宿主捕获端通常按启动时 console_cp 解码（一般是 cp936）。
        #   A 端必须：Python print str → encode 成宿主端一致的 bytes → 捕获端 decode 后得回正确中文。
        host_encoding = ""
        if console_cp and console_cp != 65001:
            host_encoding = f"cp{console_cp}"
        else:
            try:
                import locale
                pref = locale.getpreferredencoding(False) or ""
                if pref and pref.lower() not in ("utf-8", "utf8", "cp65001"):
                    host_encoding = pref
            except Exception:
                pass
        if host_encoding:
            _wrap_stdio_encoding(host_encoding)
        # B 端：invoke c.run 仍然强制 UTF-8 解码子进程 stdout bytes（容器/Podman 永远输出 UTF-8）
        subproc_encoding = "utf-8"

    _WIN32_STDOUT_TRANSCODE_READY = True
    cached = (subproc_encoding, is_tty)
    globals()["_WIN32_TRANSCODE_CACHED_RESULT"] = cached
    return cached


def _wrap_stdio_encoding(encoding_name: str) -> None:
    """把 sys.stdout/sys.stderr 的 TextIOWrapper 换壳为指定 encoding；失败静默跳过。"""
    import io
    for _io_name in ("stdout", "stderr"):
        _io = getattr(sys, _io_name)
        try:
            old_buf = _io.buffer
            line_buffering = getattr(_io, "line_buffering", True)
            write_through = getattr(_io, "write_through", False)
            try:
                _io.flush()
            except Exception:
                pass
            new_wrap = io.TextIOWrapper(
                old_buf,
                encoding=encoding_name,
                errors="replace",
                line_buffering=line_buffering,
                write_through=write_through,
            )
            setattr(sys, _io_name, new_wrap)
        except Exception:
            # 典型：被重定向成 StringIO / BytesIO 无 buffer 的对象 —— 不影响主流程
            pass


# 运行期单例结果缓存（避免每次 run_cmd 重新判别；但第一次必须真正初始化完毕后才写入）
_WIN32_TRANSCODE_CACHED_RESULT: tuple[str, bool] = ("", False)


# 兼容老命名（给任何可能存在的历史直接调用点留别名）
def _ensure_win32_console_utf8() -> None:
    _ensure_win32_stdout_transcode()
    return None


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
    """命令执行包装（Windows UTF-8 / 宿主编码双路径，防止乱码/沙箱清空 PATH）。"""
    subproc_encoding, is_tty_console = _ensure_win32_stdout_transcode()
    if echo and not hide:
        print(f"执行: {cmd}")
    use_pty = pty and platform.system() != "Windows"
    # 强制统一 Python stdout/stderr 编码为 UTF-8（防止容器内 invoke 输出时被 locale 覆盖）
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")

    # ── 原生 TTY Console（非 hide / 非 warn）：绕过 invoke c.run PIPE 捕获层
    #   invoke c.run(pty=False) 内部 subprocess.Popen(stdout=PIPE) → 按 locale cp936 decode
    #   即便是我们在 B 端加了 encoding='utf-8'，对某些版本的 invoke 仍可能被忽略；
    #   而 subprocess.call(shell=True, stdout=None, stderr=None) 直接继承父进程
    #   Console Handle → SetConsoleOutputCP(65001) 已改好，子进程自己写 UTF-8 bytes 就能 100% 渲染对。
    if (
        platform.system() == "Windows"
        and is_tty_console
        and not hide
        and not warn
    ):
        rc = subprocess.call(cmd, shell=True, env=env)
        if rc != 0:
            raise Exit(f"命令执行失败 (exit={rc}): {cmd}")
        return None

    kwargs: dict = dict(
        pty=use_pty, hide=hide, warn=warn, echo=False, env=env,
    )
    if subproc_encoding:
        kwargs["encoding"] = subproc_encoding
    try:
        return c.run(cmd, **kwargs)
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
    """在缓存目录中搜索最新（按文件名/时间排序）的镜像 tar.gz。"""
    if not search_dir.exists():
        return None
    candidates = sorted(
        search_dir.glob("*.tar.gz"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def ensure_known_hosts(cfg: ContainerConfig) -> None:
    """确保 ~/.ssh/known_hosts 中 [localhost]:{ssh_port} 条目是最新的。

    JPMan 容器每次重建（podman container restart/recreate）会重新生成 SSH
    host key（``/etc/ssh/ssh_host_*_key``），导致本地 known_hosts 记录的旧 key
    与远程新 key 不匹配，触发 ``Offending key in .../known_hosts:N`` 错误。

    本函数在容器启动前自动处理：
      1. 读取 ``~/.ssh/known_hosts``
      2. 移除所有 ``[localhost]:{ssh_port}`` 和 ``[127.0.0.1]:{ssh_port}`` 条目
      3. 使用 ``ssh-keyscan`` 获取最新 key 并写入 known_hosts（若可用）
      4. 若 ssh-keyscan 不可用，仅清理旧条目（SSH 首次连接时会提示接受新 key）

    调用方：在 ``run_container()`` 之前、``image_exists`` 检查通过后调用。
    """
    import os as _os

    known_hosts_path = Path(_os.environ.get("HOME", "~")) / ".ssh" / "known_hosts"
    port = str(cfg.ssh_port)

    # 匹配 [localhost]:PORT 或 [127.0.0.1]:PORT 的完整行（包括注释行）
    pattern_host = re.compile(
        r"^(\[[^\]]+\]:" + re.escape(port) + r"\s+)"
    )

    if not known_hosts_path.exists():
        return

    try:
        lines = known_hosts_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        try:
            lines = known_hosts_path.read_text(encoding="utf-8-sig").splitlines()
        except Exception:
            return

    original_count = len(lines)
    filtered = [line for line in lines if not pattern_host.match(line)]

    if len(filtered) == original_count:
        return  # 无需更新

    # 尝试用 ssh-keyscan 获取最新 key
    try:
        result = subprocess.run(
            ["ssh-keyscan", "-T", "5", "-p", str(cfg.ssh_port), "localhost"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            # 过滤掉错误行和空行，保留有效 key 行
            key_lines = [
                l for l in result.stdout.splitlines()
                if l and not l.startswith("#") and ":" in l
            ]
            if key_lines:
                filtered.extend(key_lines)

        known_hosts_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")
        print(f"[Run] ✓ known_hosts 已更新：移除 {original_count - len(filtered)} 条过期条目")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # ssh-keyscan 不可用（如 Windows 原生环境），仅清理旧条目
        known_hosts_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")
        print(f"[Run] ✓ known_hosts 已清理 {original_count - len(filtered)} 条过期条目（ssh-keyscan 不可用，SSH 首次连接时将提示接受新 key）")
