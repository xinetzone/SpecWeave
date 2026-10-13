"""okw desktop 子命令：openKylin WSL 内 UKUI 桌面（xrdp）预检、补齐与验收。

依据知识库实测资料（references/wsl-desktop-startup-tutorial.md 与
references/wsl-dual-image-selection.md §5.1，session
sc-20261008-openkylin-desktop-wsl-install）落机的三条契约：

1. openKylin 3.0 Desktop WSL 镜像**预装** UKUI 桌面与 xrdp/xrdp-sesman（开箱
   enabled），经 xrdp 默认端口 **3390** 供 Windows 侧 ``mstsc`` 连接；本工具不
   安装桌面套件，只在已预装的镜像上做只读预检/验收与链路补齐。
2. ``/etc/wsl.conf`` 必须启用 systemd，xrdp/xrdp-sesman 由 systemd 拉起。
3. 首次登录会**纯黑屏**（KWin 窗口管理器冷启动不驻留）：``startwm.sh`` 会
   ``unset XDG_RUNTIME_DIR``，须在默认用户 ``~/.xsession`` 补回该变量并加一个
   前 ~15 秒的幂等看门狗；文档给出可逆修复脚本（本模块以证据原文落地）。

边界：本模块只做只读预检/验收与用户级可逆补齐（写 ``~/.xsession``），不 apt
安装桌面套件、不改软件源、不改 wsl.conf、不推送任何凭据；零第三方依赖，WSL
调用经 okw.distro。
"""

import re
import socket
import subprocess
import time

from okw import distro, podman

# 报告容器复用 podman 的通用呈现（PASS/FAIL/UNKNOWN + 门控退出码），
# 并附带本次使用的端口，供格式函数回显。
CheckItem = podman.CheckItem


class DesktopPreflightReport(podman.PreflightReport):
    def __init__(self, distro_name: str, port: int = 3390):
        super().__init__(distro_name=distro_name)
        self.port = port


class DesktopInstallReport(podman.InstallReport):
    def __init__(self, distro_name: str, port: int = 3390):
        super().__init__(distro_name=distro_name)
        self.port = port


class DesktopVerifyReport(podman.VerifyReport):
    def __init__(self, distro_name: str, port: int = 3390):
        super().__init__(distro_name=distro_name)
        self.port = port


class DesktopLaunchReport(podman.VerifyReport):
    def __init__(self, distro_name: str, port: int = 3390):
        super().__init__(distro_name=distro_name)
        self.port = port


DEFAULT_PORT = 3390
DEFAULT_WAIT_SECONDS = 45.0
DEFAULT_POLL_INTERVAL = 0.8
XRDP_SERVICE = "xrdp"
XRDP_SESMAN_SERVICE = "xrdp-sesman"

# 首登黑屏看门狗的判别标记（两者同时命中即视为补丁在位）
WATCHDOG_MARKERS = ("XDG_RUNTIME_DIR", "kwin_x11")

# 证据原文脚本（wsl-dual-image-selection.md §5.1）：补回 XDG_RUNTIME_DIR，
# 并加一个前 ~15 秒、仅在 WM 缺失时幂等补拉的看门狗，最后交回 ukui-session。
XSESSION_WATCHDOG = """\
#!/bin/sh
[ -z "$XDG_RUNTIME_DIR" ] && export XDG_RUNTIME_DIR="/run/user/$(id -u)"
(
  sleep 3
  for n in 1 2 3 4 5 6; do
    pgrep -x kwin_x11 >/dev/null 2>&1 && exit 0
    kwin_x11 --replace >/tmp/kwin-watchdog.log 2>&1 &
    sleep 2
  done
) &
exec ukui-session
"""

DESKTOP_IMAGE_HINT = (
    "本命令只作用于**已预装**桌面的 openKylin Desktop WSL 镜像；"
    "若目标发行版是最小镜像（无 xrdp），请改用 Desktop WSL 镜像后重试"
)
INSTALL_HINT = "请先执行 okw desktop install <发行版> --yes 补齐桌面链路后重跑"

YES_SIDEEFFECTS_LINES = (
    "(1/3) 以 root 身份 systemctl enable --now xrdp xrdp-sesman（不安装桌面套件）；",
    "(2/3) 以默认用户身份备份并改写 ~/.xsession，写入首登黑屏看门狗补丁；",
    "(3/3) 只读复验桌面链路就绪度（服务/端口/补丁/默认用户）。",
)


def _sh(name: str, script: str, user: str | None = None, timeout: int = 60):
    """在发行版内执行一段 bash 脚本（wsl -d name [-u user] -- bash -lc <script>）。"""
    return distro.exec_distro(name, ["/bin/bash", "-lc", script], user=user, timeout=timeout)


def _fail_evidence(res, limit: int = 80) -> str:
    """把发行版内执行失败归一为可判读证据：exit/kind + stderr/stdout 摘录。"""
    detail = res.stderr.strip() or res.stdout.strip()
    if detail:
        return f"exit={res.exit_code} kind={res.kind} {detail[:limit]}"
    return f"exit={res.exit_code} kind={res.kind} 无输出"


_EXEC_FAIL_NOTE = (
    "发行版可能未启动或启动失败（Stopped 首启失败常见于 WSL 内存不足 E_UNEXPECTED，"
    "见 okw ref wsl-troubleshoot）；先手动 wsl -d <name> -- /bin/bash -lc '<本条命令>' 探活"
)

# ----------------- 结构检查（preflight/install/verify 共用） -----------------

_STRUCTURAL_NAMES = ("发行版存在", "WSL 版本", "openKylin 身份", "systemd 启用")


def add_structural_checks(report, name: str) -> bool:
    """写入发行版/WSL2/openKylin/systemd 结构项；全部非 FAIL 返回 True。"""
    try:
        d = distro.get_distro(name)
    except distro.WslError as exc:
        report.add("发行版存在", "FAIL", f"{name} 未注册（wsl -l -v 查看：{exc}")
        return False
    if d is None:
        report.add("发行版存在", "FAIL", f"{name} 未注册（wsl -l -v 查看）")
        return False
    report.add("发行版存在", "PASS", f"{d.name} / WSL{d.version} / {d.state}")
    if d.version == "2":
        report.add("WSL 版本", "PASS")
    else:
        report.add("WSL 版本", "FAIL", f"检测到 WSL{d.version}，要求 WSL2")

    os_release = _sh(name, "cat /etc/os-release")
    if not os_release.ok:
        report.add("openKylin 身份", "FAIL", f"无法读取 /etc/os-release：{_fail_evidence(os_release)}")
    elif "ID=openkylin" in os_release.stdout:
        report.add("openKylin 身份", "PASS")
    else:
        report.add("openKylin 身份", "FAIL", "/etc/os-release 中 ID 不是 openkylin")

    wsl_conf = _sh(name, "cat /etc/wsl.conf")
    if not wsl_conf.ok:
        report.add("systemd 启用", "FAIL", f"wsl.conf 读取失败：{_fail_evidence(wsl_conf)}")
    elif re.search(r"\[boot\]", wsl_conf.stdout) and re.search(r"systemd\s*=\s*true", wsl_conf.stdout):
        report.add("systemd 启用", "PASS")
    else:
        report.add(
            "systemd 启用", "FAIL",
            "/etc/wsl.conf 未启用 systemd=true；xrdp 依赖 systemd 拉起，请先启用后重试",
        )

    return not any(i.name in _STRUCTURAL_NAMES and i.status == "FAIL" for i in report.items)


# ----------------- 运行时探针（单批只读） -----------------

# 注意：本模板用 __TOKEN__ 占位（而非 %-格式化），因为脚本内层 printf 需要字面 %s。
_RUNTIME_PROBE = """\
set +e
printf 'okw_xrdp_bin=%s\\n' "$(command -v __XRDP__ >/dev/null 2>&1 && echo yes || echo no)"
printf 'okw_xrdp_active=%s\\n' "$(systemctl is-active __XRDP__ 2>/dev/null || echo unknown)"
printf 'okw_sesman_active=%s\\n' "$(systemctl is-active __SESMAN__ 2>/dev/null || echo unknown)"
printf 'okw_port_listen=%s\\n' "$(ss -ltn 2>/dev/null | grep -c ':__PORT__ ')"
printf 'okw_user=%s\\n' "$(id -un)"
printf 'okw_uid=%s\\n' "$(id -u)"
printf 'okw_xsession=%s\\n' "$(test -f $HOME/.xsession && grep -q __M1__ $HOME/.xsession && grep -q __M2__ $HOME/.xsession && echo ok || echo missing)"
"""


def parse_runtime_probe(stdout: str) -> dict:
    """解析运行时探针的 ``okw_<key>=<value>`` 行，返回 {key: value}。"""
    result: dict = {}
    for raw in (stdout or "").splitlines():
        line = raw.strip()
        if line.startswith("okw_") and "=" in line:
            key, _, value = line.partition("=")
            result[key[len("okw_"):]] = value.strip()
    return result


def _probe_runtime(name: str, port: int):
    """执行单批运行时探针；返回 (parsed_dict, CmdResult)。"""
    script = (
        _RUNTIME_PROBE
        .replace("__SESMAN__", XRDP_SESMAN_SERVICE)
        .replace("__XRDP__", XRDP_SERVICE)
        .replace("__PORT__", str(port))
        .replace("__M1__", WATCHDOG_MARKERS[0])
        .replace("__M2__", WATCHDOG_MARKERS[1])
    )
    res = _sh(name, script)
    return parse_runtime_probe(res.stdout), res


def add_runtime_checks(report, name: str, port: int) -> None:
    """把 xrdp/服务/端口/默认用户/看门狗只读检查写入报告。"""
    parsed, res = _probe_runtime(name, port)
    if not parsed:
        report.add("桌面运行时探针", "FAIL", f"探针无输出：{_fail_evidence(res)}")
        return

    installed = parsed.get("xrdp_bin") == "yes"
    report.add(
        "xrdp 已安装", "PASS" if installed else "FAIL",
        "已找到 xrdp 可执行文件" if installed else f"未找到 xrdp；{DESKTOP_IMAGE_HINT}",
    )

    for key, label in ((XRDP_SERVICE, "xrdp 服务"), (XRDP_SESMAN_SERVICE, "xrdp-sesman 服务")):
        state = parsed.get("xrdp_active" if key == XRDP_SERVICE else "sesman_active", "unknown")
        if state == "active":
            report.add(label, "PASS", "active")
        elif state == "unknown":
            report.add(label, "FAIL", f"无法判定（systemctl is-active 输出 unknown）；{INSTALL_HINT}")
        else:
            report.add(label, "FAIL", f"当前 {state}；{INSTALL_HINT}")

    listen = parsed.get("port_listen", "0")
    if listen.isdigit() and int(listen) > 0:
        report.add(f"端口 {port} 监听", "PASS", f"发行版内监听 :{port}")
    else:
        report.add(f"端口 {port} 监听", "FAIL", f"发行版内未监听 :{port}；检查 xrdp 服务与 /etc/xrdp/xrdp.ini 的 port=")

    uid = parsed.get("uid", "")
    user = parsed.get("user", "?")
    if uid == "1000":
        report.add("默认用户 / UID", "PASS", f"user={user} uid={uid}")
    else:
        report.add(
            "默认用户 / UID", "FAIL",
            f"user={user} uid={uid}；预置账号应为 openkylin/uid 1000（弱口令，首登请 passwd）",
        )

    if parsed.get("xsession") == "ok":
        report.add("首登黑屏看门狗", "PASS", "~/.xsession 含 XDG_RUNTIME_DIR 与 kwin_x11")
    else:
        report.add(
            "首登黑屏看门狗", "FAIL",
            f"~/.xsession 缺少 {'/'.join(WATCHDOG_MARKERS)}；{INSTALL_HINT}",
        )


def probe_windows_port(port: int, timeout: float = 2.0) -> bool:
    """从 Windows 侧探测 localhost:<port> 是否可达（回环，不触网卡）。"""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


# ----------------- 预检 -----------------

def preflight_check(name: str, port: int = DEFAULT_PORT) -> DesktopPreflightReport:
    """只读预检：结构项 + 运行时探针；不写文件、不改服务。"""
    report = DesktopPreflightReport(name, port=port)
    if not add_structural_checks(report, name):
        return report
    add_runtime_checks(report, name, port)
    return report


def format_preflight(report) -> str:
    """格式化预检报告。"""
    lines = [f"== okw desktop preflight：{report.distro_name} =="]
    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        lines.append(f"  [{it.status:<7}] {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append(f"结论：桌面链路已就绪，可在 Windows 侧用 mstsc 连接 localhost:{report.port}")
        lines.append("  完成一次 mstsc 会话即进入 UKUI 桌面（登录窗 Session 选 xorg）。")
    else:
        lines.append("结论：桌面链路未就绪，可执行 okw desktop install <name> --yes 补齐后重试。")
        lines.append(f"  {DESKTOP_IMAGE_HINT}。")
    return "\n".join(lines)


# ----------------- 安装（补齐链路） -----------------

def install_run(name: str, yes: bool, port: int = DEFAULT_PORT) -> DesktopInstallReport:
    """执行 install 补齐流程；无 --yes 仅返回缺失确认报告（零写入）。"""
    report = DesktopInstallReport(name, port=port)
    if not yes:
        report.missing_yes = True
        return report

    pre = DesktopPreflightReport(name, port=port)
    if not add_structural_checks(pre, name):
        for item in pre.items:
            report.items.append(item)
        return report

    # ① 确保 xrdp 已装（okw 不安装桌面套件）
    parsed, _res = _probe_runtime(name, port)
    if parsed.get("xrdp_bin") != "yes":
        report.add("xrdp 已安装", "FAIL", f"未找到 xrdp；{DESKTOP_IMAGE_HINT}")
        return report
    report.add("xrdp 已安装", "PASS", "已找到 xrdp 可执行文件")

    # ② root 启用并启动 xrdp / xrdp-sesman（幂等）
    enable = _sh(
        name,
        f"systemctl enable --now {XRDP_SERVICE} {XRDP_SESMAN_SERVICE}",
        user="root",
        timeout=120,
    )
    if enable.ok:
        report.add("启用并启动 xrdp", "PASS", "systemctl enable --now 已执行")
    else:
        report.add("启用并启动 xrdp", "FAIL", f"systemctl 失败：{_fail_evidence(enable)}")
        return report

    # ③ 默认用户身份补齐 ~/.xsession 看门狗（先备份；已含标记则跳过）
    patch = _sh(name, _xsession_patch_script())
    if not patch.ok:
        report.add("补齐 ~/.xsession 看门狗", "FAIL", f"写入失败：{_fail_evidence(patch)}")
        return report
    action = patch.stdout.strip().splitlines()[-1] if patch.stdout.strip() else ""
    if action == "unchanged":
        report.add("补齐 ~/.xsession 看门狗", "PASS", "已含标记，保持不变")
    else:
        report.add("补齐 ~/.xsession 看门狗", "PASS", "已备份原文件并写入看门狗补丁")

    # ④ 复盘只读复验
    verify_report = DesktopVerifyReport(name, port=port)
    add_runtime_checks(verify_report, name, port)
    for item in verify_report.items:
        report.items.append(item)
    return report


def _xsession_patch_script() -> str:
    """构造幂等的 ~/.xsession 补齐脚本（含备份，追加 unchanged 标记行）。"""
    # 注意：脚本经 Windows wsl.exe 桥接（整段为一个 argv），$() 内不得再嵌双引号——
    # 嵌套双引号会被桥接转义吞掉（2026-10-13 实测：嵌套引号使 test 恒为假）。
    # 故这里一律用未加引号的 $HOME 路径（家目录无空格）。
    return (
        'set +e\n'
        f'if [ -f $HOME/.xsession ] && grep -q {WATCHDOG_MARKERS[0]} $HOME/.xsession '
        f'&& grep -q {WATCHDOG_MARKERS[1]} $HOME/.xsession; then echo unchanged; exit 0; fi\n'
        'if [ -f $HOME/.xsession ]; then '
        'cp -a $HOME/.xsession $HOME/.xsession.bak-$(date +%Y%m%d%H%M%S); fi\n'
        'cat > $HOME/.xsession <<\'OKW_XSESSION_EOF\'\n'
        f'{XSESSION_WATCHDOG}'
        "OKW_XSESSION_EOF\n"
        'chmod 755 $HOME/.xsession\n'
        'echo patched\n'
    )


def format_install(report) -> str:
    """格式化补齐报告。"""
    lines = [f"== okw desktop install：{report.distro_name} =="]
    if report.missing_yes:
        lines.append("未提供 --yes，为避免以下副作用，任何写入操作均未执行：")
        lines.extend(f"  {line}" for line in YES_SIDEEFFECTS_LINES)
        lines.append("")
        lines.append("okw 只在已预装桌面的镜像上补齐链路：不 apt 安装桌面套件、不改软件源、不改 wsl.conf。")
        lines.append("请确认副作用可接受后，重跑：okw desktop install <发行版> --yes")
        return "\n".join(lines)

    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        lines.append(f"  [{it.status:<7}] {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append(f"结论：桌面链路已补齐并复验通过，可在 Windows 侧 mstsc 连接 localhost:{report.port}")
    else:
        lines.append(f"结论：补齐未通过（{sum(1 for i in report.items if i.status == 'FAIL')} 项 FAIL）")
        lines.append("  请按 FAIL 项修复后重试；~/.xsession 的改写可用 ~/.xsession.bak-* 回滚。")
    return "\n".join(lines)


# ----------------- 验收（只读） -----------------

def verify_run(name: str, port: int = DEFAULT_PORT) -> DesktopVerifyReport:
    """只读验收桌面链路；附加 Windows 侧回环端口可达性。"""
    report = DesktopVerifyReport(name, port=port)
    if not add_structural_checks(report, name):
        return report
    add_runtime_checks(report, name, port)

    if probe_windows_port(port):
        report.add(f"Windows 侧 localhost:{port}", "PASS", "回环端口可达")
    else:
        report.add(
            f"Windows 侧 localhost:{port}", "FAIL",
            "回环端口不可达（发行版可能未运行，或 xrdp 未监听）；先启动发行版后重试",
        )
    return report


def format_verify(report) -> str:
    """格式化验收报告。"""
    lines = [f"== okw desktop verify：{report.distro_name} =="]
    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        lines.append(f"  [{it.status:<7}] {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append(f"结论：桌面链路验收通过（只读）；在 Windows 侧用 mstsc 连接 localhost:{report.port}")
        lines.append("  提示：首次连接的证书提示与登录后改密码见知识库桌面使用教程。")
    else:
        fails = sum(1 for i in report.items if i.status == "FAIL")
        lines.append(f"结论：验收未通过（{fails} 项 FAIL）；本命令只读，修复方向见各项说明。")
    return "\n".join(lines)


# ----------------- 启动（启动发行版→等端口→拉起 mstsc） -----------------

def open_mstsc(port: int) -> None:
    """在 Windows 侧拉起 mstsc 连接 localhost:<port>（独立函数便于测试注入）。"""
    subprocess.Popen(["mstsc", f"/v:localhost:{port}"])


def _wait_port(port: int, wait_seconds: float, poll_interval: float) -> bool:
    """轮询 Windows 侧回环端口直到就绪或超时。"""
    deadline = time.monotonic() + wait_seconds
    while True:
        if probe_windows_port(port):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(poll_interval)


def launch_run(
    name: str,
    port: int = DEFAULT_PORT,
    wait_seconds: float = DEFAULT_WAIT_SECONDS,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
) -> DesktopLaunchReport:
    """启动发行版（幂等）→ 等回环端口就绪 → 拉起 mstsc。"""
    report = DesktopLaunchReport(name, port=port)
    if not add_structural_checks(report, name):
        return report

    start = distro.exec_distro(name, ["/bin/true"], timeout=120)
    if not start.ok:
        report.add("启动发行版", "FAIL", f"启动失败：{_fail_evidence(start)}")
        return report
    report.add("启动发行版", "PASS", "已触发开机（幂等）")

    if not _wait_port(port, wait_seconds, poll_interval):
        report.add(
            f"等待端口 {port}", "FAIL",
            f"{int(wait_seconds)} 秒内 localhost:{port} 未就绪；"
            "在发行版内 systemctl status xrdp 后重试，或确认端口与 --port 一致",
        )
        return report
    report.add(f"等待端口 {port}", "PASS", f"localhost:{port} 已就绪")

    try:
        open_mstsc(port)
        report.add("拉起 mstsc", "PASS", f"已启动 mstsc /v:localhost:{port}")
    except OSError as exc:
        report.add("拉起 mstsc", "FAIL", f"无法启动 mstsc：{exc}")
    return report


def format_launch(report) -> str:
    """格式化启动报告。"""
    lines = [f"== okw desktop launch：{report.distro_name} =="]
    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        lines.append(f"  [{it.status:<7}] {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append(f"结论：已启动并拉起远程桌面 localhost:{report.port}（登录窗 Session 选 xorg）")
        lines.append("  用完想释放内存：wsl --terminate " + report.distro_name)
    else:
        fails = sum(1 for i in report.items if i.status == "FAIL")
        lines.append(f"结论：启动未完成（{fails} 项 FAIL）；修复方向见各项说明。")
    return "\n".join(lines)
