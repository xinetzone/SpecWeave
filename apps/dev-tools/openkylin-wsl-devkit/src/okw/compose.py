"""okw compose 子命令：在已具备 rootless Podman 的 openKylin WSL 内引导
xuan-compose（命令名 ``xc``）。

定位：``okw podman`` 就绪后的**下游引导层**。三步族与 podman 组同构——
preflight 只读探测、install 显式副作用（``--yes`` 闸门）、verify 只读验收。

三条不可突破的边界：
1. **许可证**：xuan-compose 为 GPL-2.0-only，okw（Apache-2.0）不 import、不复制、
   不链接其源码，也不分发其制品；okw 仅在用户显式授权后，于用户自己的
   发行版内通过 uv 从用户给定来源安装（与 apt 安装 GPL 包同理）。
2. **解释器**：xuan-compose 要求 Python ≥3.14，而 openKylin 3.0 系统 Python
   为 3.12；okw 自身保持 Python ≥3.10，绝不引入 xuan-compose 作依赖，
   3.14 解释器由 uv 托管（python-build-standalone），安装到用户 HOME。
3. **零运行时依赖**：本模块只用标准库，所有发行版内动作经
   ``okw.distro.exec_distro`` 发出，不引入 pyyaml/python-dotenv 等第三方。

安装源三形态（``--source`` 必填，无任何内置默认路径）：
- local：本地目录（Windows 路径自动转 /mnt/<drive>，校验 pyproject.toml；
  默认拷贝安装，``--editable`` 显式开启可编辑安装）；
- url：``git+https://…``、``https://….tar.gz``、scp-like git 地址等，原样
  交给 uv（预检阶段不触网，标 UNKNOWN）；
- package：PEP 503 包名（可带 extras/版本说明符），前向兼容未来 PyPI 发布。
"""

import base64
import re
import shlex
from dataclasses import dataclass, field

from okw import distro

# ----------------- 产品契约常量（测试与文档的唯一事实源） -----------------

MIN_PYTHON = "3.14"

# 相对默认用户 HOME 的安装布局（rootless，全部落在用户目录）
LOCAL_BIN = ".local/bin"
UV_REL = f"{LOCAL_BIN}/uv"
XUAN_COMPOSE_EXE = "xuan-compose"
XC_EXE = "xc"

# uv 官方引导脚本（可经 --source 之外的环境镜像替换；此处仅默认值）
UV_INSTALLER_URL_DEFAULT = "https://astral.sh/uv/install.sh"

# 冒烟：隔离临时目录前缀、最小工程文件名、xc 只读配置子命令
SMOKE_TMP_PREFIX = "/tmp/okw-smoke-"
SMOKE_COMPOSE_FILE = "compose.yaml"
SMOKE_CONFIG_ARGS = ("config", "--quiet")

# 网络类操作超时秒数（下载解释器/构建 wheel 可能较慢）
NETWORK_TIMEOUT = 300

# 国内网络镜像指引（失败报告中给出，不自动改写用户环境）
UV_PYTHON_MIRROR_HINT = (
    "可设置 UV_PYTHON_INSTALL_MIRROR 指向 python-build-standalone 国内镜像后重试"
)
UV_INDEX_HINT = (
    "可设置 UV_DEFAULT_INDEX（或 UV_INDEX_URL）指向国内 PyPI 镜像后重试"
)
PODMAN_MISSING_HINT = (
    "rootless Podman 尚未就绪：请先执行 okw podman install <发行版> --yes，"
    "compose 引导层不负责安装 Podman"
)
COMPOSE_INSTALL_HINT = "可执行 okw compose install <发行版> --yes --source <来源> 完成安装"

LICENSE_NOTICE = (
    "许可证边界：xuan-compose（命令 xc）为 GPL-2.0-only 第三方软件，"
    "不随 okw 分发、也不与 okw 源码链接；okw 仅在你显式授权后，于目标发行版内"
    "按你指定的来源引导安装，其源码与许可证文本以安装源项目为准。"
)


# ----------------- 安装源三分类与路径归一化 -----------------

_DRIVE_RE = re.compile(r"^([A-Za-z]):[\\/]+(.*)$", re.DOTALL)
# PEP 503 规范化包名只允许 ASCII 字母数字、点、连字符、下划线；
# 尾部允许单次 extras 与版本说明符。
_PACKAGE_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*"
    r"(?:\[[A-Za-z0-9._,-]+\])?"
    r"(?:===|==|!=|~=|>=|<=|>|<)[A-Za-z0-9.*+!_-]+$"
    r"|^[A-Za-z0-9][A-Za-z0-9._-]*$"
)


def classify_source(source: str) -> str:
    """把 --source 归类为 local / url / package；无法识别抛 ValueError。

    判定顺序：本地形态（盘符/*nix 路径前缀）→ URL/VCS 形态 → 包名规格。
    """
    text = (source or "").strip()
    if not text:
        raise ValueError("安装源为空")
    if any(ch.isspace() for ch in text):
        raise ValueError(f"安装源含空白字符：{source!r}")

    # 1. 本地：Windows 盘符，或 *nix 绝对/相对/Home 路径
    if _DRIVE_RE.match(text) or text.startswith(("/", "./", "../", "~/")):
        return "local"

    # 2. URL / VCS：协议式、git+ 前缀、.git 后缀、scp-like git@host:path
    if (
        "://" in text
        or text.startswith("git+")
        or text.endswith(".git")
        or ("@" in text and ":" in text.split("@", 1)[1])
    ):
        return "url"

    # 3. 包名（可带 extras 与版本说明符）
    if _PACKAGE_RE.match(text) and text.isascii():
        return "package"

    raise ValueError(f"无法识别的安装源（非本地路径/URL/PEP503 包名）：{source!r}")


def to_distro_path(win_path: str) -> str:
    """Windows 盘符路径 → 发行版内 /mnt/<drive>/...；其余形态原样（反斜杠转正斜杠）。"""
    m = _DRIVE_RE.match(win_path)
    if not m:
        return win_path.replace("\\", "/")
    return "/mnt/{}/{}".format(
        m.group(1).lower(), m.group(2).replace("\\", "/")
    )


# ----------------- 输出解析（纯函数） -----------------

_VERSION_RE = re.compile(r"\d+(?:\.\d+)+(?:[+-][0-9A-Za-z]+(?:\.[0-9A-Za-z]+)*)?")


def parse_version_token(text: str) -> str | None:
    """从 ``xc version --short`` 等输出中抽取首个点分版本号；无则 None。"""
    m = _VERSION_RE.search(text or "")
    return m.group(0) if m else None


def parse_uv_python_list(stdout: str) -> str:
    """解析 ``uv python list``：标准 GIL 构建 3.14 的 installed/available/absent。

    ``cpython-3.14.x+freethreaded`` 等变体构建不计入（xc 不要求自由线程版）。
    """
    status = "absent"
    for line in (stdout or "").splitlines():
        m = re.search(r"cpython-({}(?:\.\d+)?)(\S*)".format(re.escape(MIN_PYTHON)), line)
        if not m:
            continue
        if m.group(2).startswith("+"):
            # 紧接版本号的 +variant（如 +freethreaded）不是标准 GIL 构建
            continue
        if "<download available>" in line:
            status = "available"
        else:
            return "installed"
    return status


def tool_is_listed(tool_list_stdout: str) -> bool:
    """``uv tool list`` 输出中 xuan-compose 是否已登记（行首匹配，避免路径子串误判）。"""
    return re.search(r"(?m)^xuan-compose\s+v\S+", tool_list_stdout or "") is not None


def is_network_error(text: str) -> bool:
    """uv/curl 失败文本是否属于网络类（DNS/连接/TLS/下载），用于镜像指引。"""
    lowered = (text or "").lower()
    markers = (
        "could not resolve host",
        "temporary failure resolving",
        "could not resolve",
        "network is unreachable",
        "could not connect",
        "failed to connect",
        "connection timed out",
        "connection refused",
        "connection reset",
        "handshake",
        "error sending request for url",
        "failed to download",
        "timed out",
    )
    return any(marker in lowered for marker in markers)


# ----------------- 发行版内 shell 片段 -----------------

def installer_script(url: str) -> str:
    """uv 官方安装器一行脚本；URL 经 shlex 引号化，杜绝 & ; 等元字符截断。"""
    return f"curl -LsSf {shlex.quote(url)} | sh"


def _b64(text: str) -> str:
    """把多行 shell 脚本编码为单个 ASCII token（跨 wsl.exe argv 无损透传）。"""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _b64_runner(text: str) -> str:
    """生成发行版内 bash -c 参数：解码并执行脚本。"""
    return f"echo {_b64(text)} | base64 -d | bash"


def smoke_script() -> str:
    """最小只读冒烟：在隔离临时目录写 compose.yaml，跑 xc config --quiet。

    xc 在非 dry-run 的 config 解析时会做 podman 版本探测与 podman info 探活，
    因此本冒烟是「xc ↔ podman」端到端链路验证；不 up/down、不起容器、不拉镜像，
    临时目录经 trap 必然清理。
    """
    return f"""set -euo pipefail
work="$(mktemp -d {SMOKE_TMP_PREFIX}XXXXXXXX)"
trap 'rm -rf "$work"' EXIT
cat > "$work/{SMOKE_COMPOSE_FILE}" <<'YAML'
services: {{}}
YAML
( cd "$work" && "$HOME/{LOCAL_BIN}/{XC_EXE}" {' '.join(SMOKE_CONFIG_ARGS)} )
"""


# ----------------- 共享报告类型 -----------------

@dataclass
class CheckItem:
    name: str
    status: str  # PASS | FAIL | UNKNOWN
    detail: str = ""


@dataclass
class _BaseReport:
    distro_name: str
    items: list[CheckItem] = field(default_factory=list)

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.items.append(CheckItem(name=name, status=status, detail=detail))

    def all_passed(self) -> bool:
        return all(i.status == "PASS" for i in self.items)

    def _generic_exit(self) -> int:
        if self.all_passed():
            return 0
        if any(i.status == "FAIL" for i in self.items):
            return 1
        return 2


@dataclass
class PreflightReport(_BaseReport):
    def exit_code(self) -> int:
        return self._generic_exit()


@dataclass
class VerifyReport(_BaseReport):
    smoke: bool = False

    def exit_code(self) -> int:
        return self._generic_exit()


@dataclass
class InstallReport(_BaseReport):
    missing_yes: bool = False

    def exit_code(self) -> int:
        if self.missing_yes:
            return 2
        return self._generic_exit()


def _format_items(items: list[CheckItem]) -> list[str]:
    max_w = max((len(i.name) for i in items), default=0)
    return [
        f"  [{it.status:<7}] {it.name:<{max_w}}  {it.detail}".rstrip()
        for it in items
    ]


# ----------------- 共享结构探针 -----------------

def _structural_gate(report: _BaseReport, name: str) -> tuple[str, str] | None:
    """发行版存在/WSL2/openKylin 身份/默认非 root 用户。

    成功返回 (default_user, home)；失败把 FAIL 项写入报告并返回 None。
    发行版不存在时早退（与 podman 组同构）。
    """
    try:
        d = distro.get_distro(name)
    except distro.WslError as exc:
        report.add("发行版存在", "FAIL", f"{name} 未注册（wsl -l -v 查看：{exc}")
        return None
    if d is None:
        report.add("发行版存在", "FAIL", f"{name} 未注册（wsl -l -v 查看）")
        return None
    if d.version != "2":
        report.add("WSL 版本", "FAIL", f"检测到 WSL{d.version}，要求 WSL2")
    else:
        report.add("WSL 版本", "PASS")

    os_release = distro.exec_distro(name, ["cat", "/etc/os-release"])
    if not os_release.ok:
        report.add(
            "openKylin 身份", "FAIL",
            f"无法读取 /etc/os-release：{os_release.stderr.strip() or f'exit={os_release.exit_code}'}",
        )
    elif "ID=openkylin" in os_release.stdout:
        report.add("openKylin 身份", "PASS")
    else:
        report.add("openKylin 身份", "FAIL", "/etc/os-release 中 ID 不是 openKylin")

    user_res = distro.exec_distro(name, ["id", "-un"])
    uid_res = distro.exec_distro(name, ["id", "-u"])
    user = user_res.stdout.strip() if user_res.ok else ""
    try:
        uid = int(uid_res.stdout.strip()) if uid_res.ok else -1
    except ValueError:
        uid = -1
    if not user_res.ok or not uid_res.ok:
        report.add("默认用户非 root", "FAIL", "无法获取默认用户身份（id 命令失败）")
        return None
    if not user or user == "root" or uid == 0:
        report.add(
            "默认用户非 root", "FAIL",
            f"检测到默认用户={user or '未知'} uid={uid}，要求非 root 用户",
        )
        return None
    report.add("默认用户非 root", "PASS", f"默认用户={user} uid={uid}")

    home_res = distro.exec_distro(name, ["printenv", "HOME"], user=user)
    home = home_res.stdout.strip() if home_res.ok else ""
    if not home or not home.startswith("/"):
        report.add(
            "默认用户 HOME", "FAIL",
            f"无法读取默认用户 {user} 的 HOME（compose 全程 rootless 安装到用户目录）",
        )
        return None
    return (user, home)


def _check_rootless_podman(name: str, user: str) -> tuple[bool, str]:
    """rootless podman 就绪门：podman --version + 默认用户 podman info Rootless=true。"""
    pv = distro.exec_distro(name, ["podman", "--version"], user=user)
    if not pv.ok:
        error = pv.stderr.strip() or f"exit={pv.exit_code}"
        return False, f"podman 不可执行：{error}；{PODMAN_MISSING_HINT}"
    info = distro.exec_distro(
        name, ["podman", "info", "--format", "{{.Host.Security.Rootless}}"], user=user
    )
    if not info.ok:
        error = info.stderr.strip() or f"exit={info.exit_code}"
        return False, f"podman info 失败：{error}；{PODMAN_MISSING_HINT}"
    if info.stdout.strip().lower() != "true":
        return (
            False,
            f"podman info Rootless={info.stdout.strip()!r}，预期 true；{PODMAN_MISSING_HINT}",
        )
    return True, pv.stdout.strip()


def _uv_bin(home: str) -> str:
    return f"{home}/{UV_REL}"


def _shim_paths(home: str) -> tuple[str, str]:
    return f"{home}/{LOCAL_BIN}/{XUAN_COMPOSE_EXE}", f"{home}/{LOCAL_BIN}/{XC_EXE}"


# ----------------- preflight（只读） -----------------

def preflight_check(distro_name: str, source: str | None = None) -> PreflightReport:
    """只读预检：结构门 → rootless podman → 安装源（可选）→ uv/Python3.14/shim。

    uv、Python 3.14、xc shim 缺失一律标 UNKNOWN（install 可自动补齐），不阻断；
    结构门与 rootless podman 失败为 FAIL。
    """
    report = PreflightReport(distro_name=distro_name)
    gate = _structural_gate(report, distro_name)
    if gate is None:
        return report
    user, home = gate

    ok, detail = _check_rootless_podman(distro_name, user)
    report.add("rootless Podman", "PASS" if ok else "FAIL", detail)

    if source is not None:
        _add_source_item(report, distro_name, source, user)

    uv = _uv_bin(home)
    uv_res = distro.exec_distro(distro_name, [uv, "--version"], user=user)
    if uv_res.ok:
        report.add("uv 引导器", "PASS", uv_res.stdout.strip())
        py_list = distro.exec_distro(distro_name, [uv, "python", "list"], user=user)
        state = parse_uv_python_list(py_list.stdout if py_list.ok else "")
        if state == "installed":
            report.add(f"托管 Python {MIN_PYTHON}", "PASS", "uv 已托管标准 CPython 3.14")
        elif state == "available":
            report.add(
                f"托管 Python {MIN_PYTHON}", "UNKNOWN",
                "uv 可见 3.14 但尚未下载；install 阶段将执行 uv python install 自动获取",
            )
        else:
            report.add(
                f"托管 Python {MIN_PYTHON}", "UNKNOWN",
                "uv 未报告标准 CPython 3.14；install 阶段将执行 uv python install 自动获取",
            )
    else:
        report.add(
            "uv 引导器", "UNKNOWN",
            "未检测到用户级 uv；install 阶段将经官方脚本安装到 "
            f"~/{UV_REL}（仅用户目录，无需 root）",
        )
        report.add(
            f"托管 Python {MIN_PYTHON}", "UNKNOWN", "依赖 uv；install 阶段将一并自动获取"
        )

    _add_shim_item(report, distro_name, home, user)
    return report


def _add_source_item(
    report: _BaseReport, distro_name: str, source: str, user: str
) -> None:
    kind = classify_source(source)
    if kind == "local":
        path = to_distro_path(source)
        check = distro.exec_distro(
            distro_name, ["test", "-f", f"{path}/pyproject.toml"], user=user
        )
        if check.ok:
            report.add("安装源", "PASS", f"本地源 {path}（pyproject.toml 存在）")
        else:
            report.add(
                "安装源", "FAIL",
                f"本地源 {path} 下未找到 pyproject.toml，请确认 xuan-compose 源码目录",
            )
    elif kind == "url":
        report.add(
            "安装源", "UNKNOWN",
            f"URL/VCS 源 {source}：预检不触网，install 阶段交由 uv 解析获取",
        )
    else:
        report.add(
            "安装源", "UNKNOWN",
            f"包名源 {source}：预检不触网，install 阶段交由 uv 从包索引获取",
        )


def _add_shim_item(
    report: _BaseReport, distro_name: str, home: str, user: str
) -> None:
    main_path, alias_path = _shim_paths(home)
    main_res = distro.exec_distro(
        distro_name, [main_path, "version", "--short"], user=user
    )
    alias_res = distro.exec_distro(
        distro_name, [alias_path, "version", "--short"], user=user
    )
    main_ver = parse_version_token(main_res.stdout) if main_res.ok else None
    alias_ver = parse_version_token(alias_res.stdout) if alias_res.ok else None
    if not main_ver or not alias_ver:
        detail = "未检测到 xuan-compose/xc shim"
        if main_res.ok != alias_res.ok:
            failed = XUAN_COMPOSE_EXE if not main_res.ok else XC_EXE
            detail += f"（{failed} 执行异常）"
        report.add("xuan-compose shim", "UNKNOWN", f"{detail}；{COMPOSE_INSTALL_HINT}")
        return
    if main_ver != alias_ver:
        report.add(
            "xuan-compose shim", "FAIL",
            f"两个 shim 版本不一致：{XUAN_COMPOSE_EXE}={main_ver} / {XC_EXE}={alias_ver}，"
            "建议重新执行 compose install --yes 修复",
        )
        return
    report.add("xuan-compose shim", "PASS", f"{XUAN_COMPOSE_EXE} 与 {XC_EXE} 均为 {main_ver}")


def format_preflight(report: PreflightReport) -> str:
    lines = [f"== okw compose preflight：{report.distro_name} =="]
    lines.extend(_format_items(report.items))
    lines.append("")
    if report.all_passed():
        lines.append("结论：预检全部通过，可以执行 okw compose install <发行版> --yes --source <来源>")
    else:
        fail_n = sum(1 for i in report.items if i.status == "FAIL")
        unk_n = sum(1 for i in report.items if i.status == "UNKNOWN")
        summary = []
        if fail_n:
            summary.append(f"{fail_n} 项 FAIL")
        if unk_n:
            summary.append(f"{unk_n} 项 UNKNOWN（install 阶段可自动补齐，不阻断）")
        lines.append("结论：预检未通过（" + " / ".join(summary) + "）")
        lines.append("  请先修复 FAIL 项；UNKNOWN 为可自动引导项，确认安装源后执行 install 即可。")
    return "\n".join(lines)


# ----------------- install（显式副作用，--yes 闸门在 handler 层） -----------------

YES_SIDEEFFECTS_LINES = (
    "(1/4) 若用户级 uv 缺失，经官方脚本将 uv 安装到 ~/.local/bin（仅用户目录，无需 root）；",
    "(2/4) 执行 uv python install 3.14，由 uv 托管一份独立 CPython 3.14（不改系统 Python）；",
    "(3/4) 执行 uv tool install，把 xuan-compose 及其依赖装进 3.14 隔离环境并生成 xc/xuan-compose 两个 shim；",
    "(4/4) 以全路径执行两个 shim 的 version --short 完成验收（非 login shell 的 PATH 不含 ~/.local/bin）。",
)


def _ensure_uv(
    name: str, user: str, home: str, report: InstallReport
) -> tuple[bool, bool]:
    """确保用户级 uv 可用。

    返回 (是否成功, uv 是否在本次调用前就已存在)。第二个返回值用于决定 Python
    3.14 的获取策略：uv 已存在时先 ``python list`` 判定、installed 即跳过；
    uv 本次新装时直接 ``python install``（全新引导器无需先列清单）。
    """
    uv = _uv_bin(home)
    if distro.exec_distro(name, [uv, "--version"], user=user).ok:
        report.add("uv 引导器", "PASS", "用户级 uv 已存在")
        return True, True

    install = distro.exec_distro(
        name, ["bash", "-c", installer_script(UV_INSTALLER_URL_DEFAULT)],
        user=user, timeout=NETWORK_TIMEOUT,
    )
    if not install.ok:
        detail = f"uv 安装脚本执行失败：{install.stderr.strip() or f'exit={install.exit_code}'}"
        if is_network_error(install.stderr):
            detail += "（网络类错误：检查发行版 DNS/代理，或手动安装 uv 后重试）"
        report.add("uv 引导器", "FAIL", detail)
        return False, False

    recheck = distro.exec_distro(name, [uv, "--version"], user=user)
    if not recheck.ok:
        report.add(
            "uv 引导器", "FAIL",
            f"安装脚本返回成功但 {uv} 仍不可执行，请检查 ~/{LOCAL_BIN} 与磁盘空间",
        )
        return False, False
    report.add("uv 引导器", "PASS", f"已安装 {recheck.stdout.strip()}")
    return True, False


def install_run(
    distro_name: str, source: str, *, editable: bool = False
) -> InstallReport:
    """执行 compose 安装主流程（调用方须已确认 --yes 与安装源形态合法）。"""
    report = InstallReport(distro_name=distro_name)
    gate = _structural_gate(report, distro_name)
    if gate is None:
        return report
    user, home = gate

    ok, detail = _check_rootless_podman(distro_name, user)
    if not ok:
        report.add("rootless Podman", "FAIL", detail)
        return report
    report.add("rootless Podman", "PASS", detail)

    # 安装源解析与本地源结构校验（任何下载动作之前）。
    # 语义区分：`test -f` 退出码 1（普通业务失败，stderr 干净）= 文件确实不存在，
    # 必须在任何下载前硬中止；distro_missing 是 WSL/发行版平台层信号——结构门既已通过，
    # 真实环境此处不会出现，若真出现会话级故障，紧随其后的 uv 等真实命令会原样失败并
    # 如实报告，故不在源门以"文件缺失"名义重复阻断。
    kind = classify_source(source)
    if kind == "local":
        target = to_distro_path(source)
        check = distro.exec_distro(
            distro_name, ["test", "-f", f"{target}/pyproject.toml"], user=user
        )
        if not check.ok and check.kind != "distro_missing":
            report.add(
                "安装源", "FAIL",
                f"本地源 {target} 下未找到 pyproject.toml，已在任何下载前中止",
            )
            return report
        report.add("安装源", "PASS", f"本地源 {target}")
    else:
        target = source
        report.add("安装源", "PASS", f"{'URL/VCS' if kind == 'url' else '包名'}源 {target}")

    # 1. uv
    uv_ok, uv_already = _ensure_uv(distro_name, user, home, report)
    if not uv_ok:
        return report
    uv = _uv_bin(home)

    # 2. 托管 Python 3.14：uv 已存在则先列清单，标准 CPython 3.14 已托管即跳过
    #    （避免重复下载）；uv 本次新装或清单显示缺失/可下载时执行 install（幂等）。
    need_python = True
    if uv_already:
        py_listed = distro.exec_distro(distro_name, [uv, "python", "list"], user=user)
        if parse_uv_python_list(py_listed.stdout if py_listed.ok else "") == "installed":
            need_python = False
            report.add(
                f"托管 Python {MIN_PYTHON}", "PASS", "uv 已托管标准 CPython 3.14，无需重复下载"
            )
    if need_python:
        py = distro.exec_distro(
            distro_name, [uv, "python", "install", MIN_PYTHON],
            user=user, timeout=NETWORK_TIMEOUT,
        )
        if not py.ok:
            detail = (
                f"托管 Python 获取失败：{py.stderr.strip() or f'exit={py.exit_code}'}；"
                f"{UV_PYTHON_MIRROR_HINT}"
            )
            report.add(f"托管 Python {MIN_PYTHON}", "FAIL", detail)
            return report
        report.add(f"托管 Python {MIN_PYTHON}", "PASS", (py.stdout.strip() or "已就绪"))

    # 3. uv tool install（已登记则 --force 幂等重装；本地源默认非 editable）
    listed = tool_is_listed(
        distro.exec_distro(distro_name, [uv, "tool", "list"], user=user).stdout
    )
    cmd = [uv, "tool", "install"]
    if listed:
        cmd.append("--force")
    if editable:
        cmd.append("--editable")
    cmd.extend(["--python", MIN_PYTHON, target])
    tool = distro.exec_distro(distro_name, cmd, user=user, timeout=NETWORK_TIMEOUT)
    if not tool.ok:
        detail = f"uv tool install 失败：{tool.stderr.strip() or f'exit={tool.exit_code}'}"
        if is_network_error(tool.stderr):
            detail += f"；{UV_INDEX_HINT}"
        report.add("uv tool install", "FAIL", detail)
        return report
    report.add(
        "uv tool install", "PASS",
        ("已重装（--force）" if listed else "已安装")
        + f" xuan-compose（shim：{XUAN_COMPOSE_EXE}/{XC_EXE}）",
    )

    # 4. 双 shim 全路径验收
    main_path, alias_path = _shim_paths(home)
    main_res = distro.exec_distro(distro_name, [main_path, "version", "--short"], user=user)
    alias_res = distro.exec_distro(distro_name, [alias_path, "version", "--short"], user=user)
    main_ver = parse_version_token(main_res.stdout) if main_res.ok else None
    alias_ver = parse_version_token(alias_res.stdout) if alias_res.ok else None
    if not main_ver or not alias_ver:
        error = (main_res.stderr if not main_res.ok else alias_res.stderr).strip()
        report.add(
            "shim 验收", "FAIL",
            f"安装已完成但 shim 执行失败：{error or '无版本输出'}；"
            "xuan-compose 要求 Python 3.14，请确认 uv 托管解释器未被损坏",
        )
        return report
    if main_ver != alias_ver:
        report.add(
            "shim 验收", "FAIL",
            f"两个 shim 版本不一致：{XUAN_COMPOSE_EXE}={main_ver} / {XC_EXE}={alias_ver}",
        )
        return report
    report.add("shim 验收", "PASS", f"{XUAN_COMPOSE_EXE} 与 {XC_EXE} 版本一致：{main_ver}")
    return report


def format_install(report: InstallReport) -> str:
    lines = [f"== okw compose install：{report.distro_name} =="]
    if report.missing_yes:
        lines.append("未提供 --yes，为避免以下副作用，任何写入/下载操作均未执行：")
        lines.extend(f"  {line}" for line in YES_SIDEEFFECTS_LINES)
        lines.append("")
        lines.append(LICENSE_NOTICE)
        lines.append("")
        lines.append("请确认副作用与许可证边界可接受后，重跑：")
        lines.append("  okw compose install <发行版> --yes --source <本地目录|URL|包名>")
        return "\n".join(lines)

    lines.extend(_format_items(report.items))
    lines.append("")
    if report.all_passed():
        lines.append("结论：安装成功，可执行 okw compose verify <发行版> [--smoke] 验收")
        lines.append(f"  {LICENSE_NOTICE}")
    else:
        lines.append(f"结论：安装未通过（{sum(1 for i in report.items if i.status == 'FAIL')} 项 FAIL）")
        lines.append("  本流程不宣称事务回滚：uv/Python/tool 的部分下载或安装可能已生效，")
        lines.append("  修复 FAIL 项后重跑即可（各步骤幂等）。")
        all_detail = "\n".join(i.detail for i in report.items if i.status == "FAIL")
        if "UV_PYTHON_INSTALL_MIRROR" in all_detail:
            lines.append(f"  {UV_PYTHON_MIRROR_HINT}")
        if "UV_DEFAULT_INDEX" in all_detail:
            lines.append(f"  {UV_INDEX_HINT}")
    return "\n".join(lines)


# ----------------- verify（只读；smoke 为隔离目录内的只读配置解析） -----------------

def verify_run(distro_name: str, *, smoke: bool = False) -> VerifyReport:
    """只读验收：结构门 → rootless podman → 双 shim 版本一致；可选端到端冒烟。"""
    report = VerifyReport(distro_name=distro_name, smoke=smoke)
    gate = _structural_gate(report, distro_name)
    if gate is None:
        return report
    user, home = gate

    ok, detail = _check_rootless_podman(distro_name, user)
    report.add("rootless Podman", "PASS" if ok else "FAIL", detail)

    main_path, alias_path = _shim_paths(home)
    main_res = distro.exec_distro(distro_name, [main_path, "version", "--short"], user=user)
    alias_res = distro.exec_distro(distro_name, [alias_path, "version", "--short"], user=user)
    main_ver = parse_version_token(main_res.stdout) if main_res.ok else None
    alias_ver = parse_version_token(alias_res.stdout) if alias_res.ok else None
    if not main_ver or not alias_ver:
        report.add(
            "xuan-compose shim", "FAIL",
            f"未检测到可用的 xc/xuan-compose shim；{COMPOSE_INSTALL_HINT}",
        )
    elif main_ver != alias_ver:
        report.add(
            "xuan-compose shim", "FAIL",
            f"两个 shim 版本不一致：{XUAN_COMPOSE_EXE}={main_ver} / {XC_EXE}={alias_ver}",
        )
    else:
        report.add("xuan-compose shim", "PASS", f"两个 shim 版本一致：{main_ver}")

    if smoke:
        if any(i.status == "FAIL" for i in report.items):
            report.add("compose 冒烟", "FAIL", "前置检查存在 FAIL，未执行 compose 冒烟")
            return report
        run = distro.exec_distro(
            distro_name, ["bash", "-c", _b64_runner(smoke_script())],
            user=user, timeout=NETWORK_TIMEOUT,
        )
        if run.ok:
            report.add(
                "compose 冒烟", "PASS",
                "隔离临时目录内 xc config --quiet 通过（xc↔podman 端到端探活成功，未起容器未拉镜像）",
            )
        else:
            error = (run.stderr.strip() or run.stdout.strip() or f"exit={run.exit_code}")
            report.add(
                "compose 冒烟", "FAIL",
                f"xc config --quiet 失败：{error[:200]}（可在发行版内手动执行 xc config 复现）",
            )
    return report


def format_verify(report: VerifyReport) -> str:
    lines = [f"== okw compose verify：{report.distro_name} =="]
    lines.extend(_format_items(report.items))
    lines.append("")
    if report.all_passed():
        if report.smoke:
            lines.append("结论：rootless 验收、双 shim 与 compose 端到端冒烟全部通过")
        else:
            lines.append("结论：验收通过（默认只读，未执行 compose 冒烟）")
            lines.append("  如需端到端探活：okw compose verify <发行版> --smoke")
    else:
        fail_n = sum(1 for i in report.items if i.status == "FAIL")
        unk_n = sum(1 for i in report.items if i.status == "UNKNOWN")
        summary = []
        if fail_n:
            summary.append(f"{fail_n} 项 FAIL")
        if unk_n:
            summary.append(f"{unk_n} 项 UNKNOWN")
        lines.append("结论：验收未通过（" + " / ".join(summary) + "）")
        lines.append("  本命令为只读检查；冒烟也仅在隔离临时目录做配置解析，不起容器不拉镜像。")
    return "\n".join(lines)
