"""WSL 发行版管理：wsl.exe 统一调用封装与发行版生命周期操作。

设计依据（知识库 docs/knowledge/tech/openkylin-docs-wiki/）：
- S26 本机实测：PATH 裁剪需全路径回退、WSL_UTF8=1 保证中文输出、E_UNEXPECTED 与空闲内存相关。
- §3.3 验收五步、F-017/F-018 WSL 官方安装路径与默认账号纪律。
"""

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

WSL_UTF8 = "1"
DEFAULT_IMPORT_VERSION = "2"
GZIP_MAGIC = b"\x1f\x8b"

class WslError(Exception):
    """受控的 WSL 错误（带中文可操作信息），禁止向外抛原始异常。"""

@dataclass(frozen=True)
class CmdResult:
    """run_wsl 的归一化结果。"""

    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    kind: str  # ok | command_missing | distro_missing | failed | timeout

@dataclass(frozen=True)
class Distro:
    """wsl -l -v 解析出的单个发行版。"""

    name: str
    version: str  # "2" (WSL2) | "1" (WSL1)
    state: str  # Running | Stopped | ...
    is_default: bool

def wsl_exe() -> str:
    """定位 wsl.exe：PATH 优先，失败回退 $env:WINDIR\\System32\\wsl.exe。"""
    exe = shutil.which("wsl.exe") or shutil.which("wsl")
    if exe:
        return exe
    windir = os.environ.get("WINDIR")
    if windir:
        candidate = Path(windir) / "System32" / "wsl.exe"
        if candidate.exists():
            return str(candidate)
    raise WslError("找不到 wsl.exe：请先安装 WSL2（管理员 PowerShell 运行 wsl --install）")

def _run_subprocess(cmd, env, timeout):
    """薄封装，便于测试注入。"""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=timeout,
    )

_DISTRO_MISSING_PATTERNS = [
    "no distribution",
    "no installed distributions",
    "没有已安装的分发版",
    "未安装发行版",
    "is not registered",
    "不存在",
    "terminate",
    "distribution name is not valid",
]

def _classify_failure(returncode: int, stderr: str) -> str:
    lowered = stderr.lower()
    if any(p in lowered for p in _DISTRO_MISSING_PATTERNS):
        return "distro_missing"
    return "failed"

def run_wsl(args: list[str], timeout: int = 60) -> CmdResult:
    """执行 wsl.exe 命令，注入 WSL_UTF8=1，归一化结果。"""
    exe = wsl_exe()
    cmd = [exe, *args]
    env = dict(os.environ)
    env["WSL_UTF8"] = WSL_UTF8
    try:
        proc = _run_subprocess(cmd, env, timeout)
    except FileNotFoundError:
        return CmdResult(False, 127, "", "wsl.exe not found", "command_missing")
    except subprocess.TimeoutExpired:
        return CmdResult(False, -1, "", "command timed out", "timeout")
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    if proc.returncode != 0:
        kind = _classify_failure(proc.returncode, stderr)
        return CmdResult(False, proc.returncode, stdout, stderr, kind)
    return CmdResult(True, 0, stdout, stderr, "ok")

def list_distros() -> list[Distro]:
    """解析 `wsl -l -v` 输出；格式漂移时 fail-fast（携带原始输出）。"""
    res = run_wsl(["-l", "-v"])
    if not res.ok:
        raise WslError(f"无法读取 WSL 发行版列表（exit={res.exit_code}）：{res.stderr.strip()}")
    return parse_list_output(res.stdout)

def parse_list_output(text: str) -> list[Distro]:
    """解析 wsl -l -v 文本。

    支持三种形态：
    1) 表格形态（表头含 NAME/STATE/VERSION，星号标记默认发行版）；
    2) 无表头短形态（`[*] name state version`，WSL 某些输出风格）；
    3) 旧列表形态（"Windows Subsystem for Linux Distributions:" + 名称 + Running/Stopped 行）。
    全部无法识别时抛 WslError 而非静默错解析。
    """
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []

    # 形态一：表格（表头 NAME ... STATE ... VERSION）
    header_idx = next(
        (i for i, ln in enumerate(lines) if re.search(r"\bNAME\b", ln) and re.search(r"\bVERSION\b", ln)),
        None,
    )
    if header_idx is not None:
        distros: list[Distro] = []
        for ln in lines[header_idx + 1 :]:
            parts = ln.split()
            if len(parts) < 3:
                continue
            is_default = parts[0].startswith("*")
            name_col = 1 if is_default else 0
            name = parts[name_col]
            version = parts[-1]
            state = " ".join(parts[name_col + 1 : -1]) if len(parts) > name_col + 2 else ""
            distros.append(Distro(name=name, version=version, state=state, is_default=is_default))
        if distros:
            return distros
        raise WslError("无法解析 wsl -l -v 输出（表头后无发行版行），原始输出如下：\n" + text)

    # 形态二：无表头短形态 `[*] name state version`
    simple: list[Distro] = []
    for ln in lines:
        m = re.match(r"^(\*?)\s*(\S+)\s+(\S+)\s+(\S+)\s*$", ln)
        if m:
            simple.append(
                Distro(name=m.group(2), version=m.group(4), state=m.group(3),
                       is_default=bool(m.group(1)))
            )
    if simple and len(simple) == len(lines):
        return simple

    # 形态三：旧列表形态
    if "windows subsystem for linux distributions" in text.lower():
        distros = []
        current_name: str | None = None
        for ln in lines:
            m = re.match(r"^\s*([A-Za-z0-9][A-Za-z0-9 ._\-]*?(?:\s*\(默认\))?)\s*$", ln)
            if m and ":" not in ln and not ln.lower().startswith("windows"):
                current_name = re.sub(r"\s*\(默认\)\s*$", "", m.group(1)).strip()
                continue
            st = re.match(r"^\s*(Running|Stopped|Installing)\s*[:：]?\s*\d*\s*$", ln)
            if st and current_name:
                distros.append(Distro(name=current_name, version="2",
                                      state=st.group(1), is_default=False))
                current_name = None
        if distros:
            return distros

    raise WslError("无法识别 wsl -l -v 输出格式（可能是 WSL 版本变化），原始输出如下：\n" + text)

def get_distro(name: str) -> Distro | None:
    """按名称查找发行版；不存在返回 None。"""
    for d in list_distros():
        if d.name == name:
            return d
    return None

def exec_distro(name: str, cmd: list[str]) -> CmdResult:
    """在指定发行版内执行命令（参数透传）。"""
    try:
        if get_distro(name) is None:
            return CmdResult(False, 1, "", f"发行版 {name} 不存在", "distro_missing")
    except WslError:
        # 列表不可读（wsl 异常）时不让异常外泄，交由上层统一提示
        return CmdResult(False, 1, "", f"无法确认发行版 {name} 状态（wsl -l -v 读取失败）", "distro_missing")
    return run_wsl(["-d", name, "--", *cmd])

def import_distro(image: str, name: str, location: str, version: str = DEFAULT_IMPORT_VERSION) -> CmdResult:
    """构造并执行 wsl --import；校验镜像 gzip 头。"""
    image_path = Path(image)
    if not image_path.exists():
        raise WslError(f"镜像文件不存在：{image}")
    with open(image_path, "rb") as fh:
        head = fh.read(2)
    if head != GZIP_MAGIC:
        raise WslError(
            "镜像文件头不是 gzip（1F 8B）：openKylin 的 .wsl 镜像是 gzip 压缩的 tar 包。"
            "请确认使用官方下载的 openKylin-*-wsl-amd64.wsl 镜像。"
        )
    return run_wsl(["--import", name, location, image, "--version", version], timeout=600)

def export_distro(name: str, output: str) -> CmdResult:
    """导出发行版为 tar 包（wsl --export 封装）。"""
    return run_wsl(["--export", name, output], timeout=600)

def unregister_distro(name: str, yes: bool = False) -> CmdResult:
    """注销发行版（wsl --unregister）。必须显式 --yes，防止误删。"""
    if not yes:
        return CmdResult(
            False,
            2,
            "",
            "注销是破坏性操作：请显式加 --yes 确认（本工具不会静默更改你的发行版）",
            "failed",
        )
    return run_wsl(["--unregister", name], timeout=600)

def default_distro_name() -> str | None:
    """读取 wsl --list --quiet 首行的默认发行版名（星标保护快照用）。"""
    res = run_wsl(["--list", "--quiet"])
    if not res.ok:
        return None
    first = next((ln.strip() for ln in res.stdout.splitlines() if ln.strip()), None)
    return first or None
