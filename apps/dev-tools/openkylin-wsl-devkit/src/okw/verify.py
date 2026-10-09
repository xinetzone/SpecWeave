"""openKylin WSL 环境五步验收（对应知识库 §3.3 实测口径）。

验收项：
1. 发行版在列且为 WSL2，默认星标未被本工具改变；
2. /etc/os-release 版本与 ID；
3. 默认用户与 UID（预置账号 openkylin / UID 1000，F-017）；
4. /etc/wsl.conf 的 [user] default= 与 [boot] systemd=true（systemd 已启用，S26）；
5. 软件包计数（dpkg-query -W 口径，与 S26 实测 405 包对照）。
"""

import re
from dataclasses import dataclass, field

from okw import distro

@dataclass(frozen=True)
class CheckResult:
    """单项验收结果。"""

    key: str
    label: str
    command: str
    expected: str
    actual: str
    passed: bool
    note: str = ""

@dataclass
class VerifyReport:
    name: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)

_OS_RELEASE_VERSION_RE = re.compile(r"^VERSION\s*=\s*[\"']?(.+?)[\"']?\s*$", re.M)
_OS_RELEASE_ID_RE = re.compile(r"^ID\s*=\s*[\"']?(.+?)[\"']?\s*$", re.M)
_USER_UID_RE = re.compile(r"user=(\S+)\s+uid=(\d+)", re.DOTALL)

def _exec_in(name: str, cmd: str) -> distro.CmdResult:
    """在发行版内执行单条命令（wsl -d name -- bash -lc 'cmd'）。"""
    return distro.run_wsl(["-d", name, "--", "/bin/bash", "-lc", cmd])

def _fail_evidence(res: distro.CmdResult, limit: int = 80) -> str:
    """把发行版内执行失败归一为可判读证据：exit/kind + stderr/stdout 摘录。

    背景：实测故障中 stderr 为空，原实现拼出"读取失败: "空串，零证据无法排障；
    故优先取 stderr，回退 stdout（WSL 部分错误路径只写一侧），两者皆空则明示"无输出"。
    """
    detail = res.stderr.strip() or res.stdout.strip()
    if detail:
        return f"exit={res.exit_code} kind={res.kind} {detail[:limit]}"
    return f"exit={res.exit_code} kind={res.kind} 无输出"

_EXEC_FAIL_NOTE = (
    "发行版可能未启动或启动失败（Stopped 首启失败常见于 WSL 内存不足 E_UNEXPECTED，"
    "见 okw ref wsl-troubleshoot）；先手动 wsl -d <name> -- /bin/bash -lc '<本条命令>' 探活"
)

def verify(name: str, default_before: str | None = None) -> VerifyReport:
    """执行五步验收；单项失败不中断，汇总 PASS/FAIL。"""
    report = VerifyReport(name=name)

    # ① 在列且 WSL2
    d = distro.get_distro(name)
    if d is None:
        report.checks.append(
            CheckResult("listed", "发行版在列", f"wsl -l -v | {name}", "在列且 WSL2",
                        "未找到", False, f"发行版 {name} 不存在，请先 import")
        )
        return report
    check1 = CheckResult(
        "listed", "发行版在列且 WSL2", f"wsl -l -v | {name}",
        "在列且 WSL2", f"在列 / WSL{d.version} / {d.state}", d.version == "2",
        "默认星标对比：调用前后默认发行版必须一致（本工具不改默认）",
    )
    # 默认星标保护：default_before 快照对比
    default_now = distro.default_distro_name()
    if default_before is not None and default_now != default_before:
        check1 = CheckResult(
            "listed", "发行版在列且 WSL2", f"wsl -l -v | {name}",
            "在列且 WSL2", f"在列 / WSL{d.version} / 默认已变({default_before}->{default_now})",
            False, "本工具不得改变默认发行版（星标保护失败）",
        )
    report.checks.append(check1)

    # ② os-release
    res2 = _exec_in(name, "cat /etc/os-release")
    if res2.ok:
        version = _OS_RELEASE_VERSION_RE.search(res2.stdout)
        idv = _OS_RELEASE_ID_RE.search(res2.stdout)
        actual = f"ID={idv.group(1) if idv else '?'} VERSION={version.group(1) if version else '?'}"
        passed = bool(version and idv and "openkylin" in (idv.group(1).lower() if idv else ""))
        report.checks.append(CheckResult(
            "os-release", "/etc/os-release 版本与 ID", "cat /etc/os-release",
            "openkylin 发行版且有 VERSION", actual, passed,
            note="openKylin-3.0 对应 VERSION=\"3.0\"；2.0 LTS 对应 VERSION=\"2.0\"",
        ))
    else:
        report.checks.append(CheckResult("os-release", "/etc/os-release 版本与 ID", "cat /etc/os-release",
                                         "openkylin 发行版且有 VERSION", f"读取失败: {_fail_evidence(res2)}", False,
                                         note=_EXEC_FAIL_NOTE))

    # ③ 默认用户 / UID
    res3 = _exec_in(name, 'echo "user=$(whoami) uid=$(id -u)"')
    if res3.ok:
        m = _USER_UID_RE.search(res3.stdout)
        if m:
            user, uid = m.group(1), int(m.group(2))
            passed = uid == 1000
            report.checks.append(CheckResult(
                "user", "默认用户 / UID", 'echo "user=$(whoami) uid=$(id -u)"',
                "user=openkylin uid=1000", f"user={user} uid={uid}", passed,
                note="预置账号 openkylin/openkylin（弱口令，首次进入请立即 passwd，F-018）",
            ))
        else:
            report.checks.append(CheckResult("user", "默认用户 / UID", 'echo "user=$(whoami) uid=$(id -u)"',
                                             "user=openkylin uid=1000", f"无法解析输出: {res3.stdout.strip()[:60]}", False))
    else:
        report.checks.append(CheckResult("user", "默认用户 / UID", 'echo "user=$(whoami) uid=$(id -u)"',
                                         "user=openkylin uid=1000", f"执行失败: {_fail_evidence(res3)}", False,
                                         note=_EXEC_FAIL_NOTE))

    # ④ wsl.conf：systemd 与默认用户
    res4 = _exec_in(name, "cat /etc/wsl.conf")
    if res4.ok:
        conf_text = res4.stdout
        has_user_default = bool(re.search(r"\[user\]", conf_text) and re.search(r"default\s*=", conf_text))
        has_systemd = bool(re.search(r"\[boot\]", conf_text) and re.search(r"systemd\s*=\s*true", conf_text))
        report.checks.append(CheckResult(
            "wsl.conf", "wsl.conf 的 systemd 与默认用户", "cat /etc/wsl.conf",
            "[boot] systemd=true 且 [user] default= 存在",
            f"[boot] systemd={'true' if has_systemd else '未启用'} / [user] default={'存在' if has_user_default else '缺失'}",
            has_systemd and has_user_default,
            note="systemd 未启用时桌面栈（xrdp 等）可能异常；无 [user] 段则默认 root，需注意",
        ))
    else:
        # 读取失败≠配置缺失：原实现在读失败时把解析空串当成"systemd 未启用 / default=缺失"，
        # 产出假结论；此处如实报读失败并附证据。
        report.checks.append(CheckResult(
            "wsl.conf", "wsl.conf 的 systemd 与默认用户", "cat /etc/wsl.conf",
            "[boot] systemd=true 且 [user] default= 存在",
            f"wsl.conf 读取失败: {_fail_evidence(res4)}", False,
            note=_EXEC_FAIL_NOTE,
        ))

    # ⑤ 软件包计数
    res5 = _exec_in(name, "dpkg-query -W | wc -l")
    if res5.ok:
        pkg_count = res5.stdout.strip()
        try:
            count = int(pkg_count)
            passed = count > 0
        except ValueError:
            count = -1
            passed = False
        report.checks.append(CheckResult(
            "packages", "软件包计数", "dpkg-query -W | wc -l",
            "约 405（S26 实测最小镜像基准）", f"{pkg_count} 包",
            passed,
            note="口径：dpkg-query -W（不含表头）；dpkg -l 含表头会多约 5 行。数量随系统使用增长属正常",
        ))
    else:
        report.checks.append(CheckResult("packages", "软件包计数", "dpkg-query -W | wc -l",
                                         "约 405", f"执行失败: {_fail_evidence(res5)}", False,
                                         note=_EXEC_FAIL_NOTE))

    return report

def format_report(report: VerifyReport) -> str:
    """渲染 PASS/FAIL 清单。"""
    lines = [f"== openKylin WSL 环境验收：{report.name} =="]
    for c in report.checks:
        mark = "PASS" if c.passed else "FAIL"
        lines.append(f"[{mark}] {c.label}")
        lines.append(f"      命令: {c.command}")
        lines.append(f"      期望: {c.expected}")
        lines.append(f"      实际: {c.actual}")
        if c.note:
            lines.append(f"      说明: {c.note}")
    lines.append(f"== 结果: {'全部通过' if report.all_passed else f'{len([c for c in report.checks if not c.passed])} 项未通过'} ==")
    return "\n".join(lines)
