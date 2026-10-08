"""okw podman 子命令：预检、安装和验收 openKylin WSL 内的 rootless Podman。

零第三方依赖，所有 WSL 调用经 okw.distro 统一封装。
"""

from dataclasses import dataclass, field

from okw import distro

# 预检需要探测的 4 个直接包
DIRECT_PACKAGES = ("podman", "uidmap", "slirp4netns", "fuse-overlayfs")

# rootless 标准映射区间（左闭右开）
STANDARD_SUBUID_START = 100000
STANDARD_SUBUID_COUNT = 65536
STANDARD_SUBUID_END = STANDARD_SUBUID_START + STANDARD_SUBUID_COUNT  # 165536

APT_POLICY_UNKNOWN_HINT = (
    "未知：发行版 APT 索引缺失或已过期，"
    "建议在发行版内先手动执行 sudo apt update 后重跑 preflight"
)
APT_PKG_MISSING_LABEL = "候选缺失"
APT_NET_ERROR_LABEL = "APT网络错误"
APT_HASH_ERROR_LABEL = "APT源哈希校验失败"
APT_UNKNOWN_LABEL = "APT索引未知"


# ----------------- 判定矩阵：映射区间/重叠 -----------------

@dataclass(frozen=True)
class SubordinateMapEntry:
    name: str
    start: int
    count: int

    @property
    def end(self) -> int:
        """区间右端（不含）。"""
        return self.start + self.count


def parse_subordinate_file(text: str) -> list[SubordinateMapEntry]:
    """解析 /etc/subuid 或 /etc/subgid，返回条目列表。

    三列格式：name:start:count。行格式错误时跳过（由上层判定无效）。
    """
    entries: list[SubordinateMapEntry] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(":")
        if len(parts) != 3:
            continue
        name, start_s, count_s = (p.strip() for p in parts)
        if not name or any(c.isspace() for c in name):
            continue
        try:
            start = int(start_s)
            count = int(count_s)
        except ValueError:
            continue
        if start <= 0 or count <= 0:
            continue
        entries.append(SubordinateMapEntry(name=name, start=start, count=count))
    return entries


def ranges_overlap(a: SubordinateMapEntry, b: SubordinateMapEntry) -> bool:
    """判定两个区间是否重叠，左闭右开 [start, start+count)。

    端点恰好相等 A.end == B.start 不算重叠（与 shadow-utils 语义对齐）。
    """
    return a.start < b.end and b.start < a.end


def range_conflicts_with_standard(entry: SubordinateMapEntry) -> bool:
    """判断一个既有映射条目是否与标准区间 [100000, 165536) 重叠。"""
    std = SubordinateMapEntry("__standard__", STANDARD_SUBUID_START, STANDARD_SUBUID_COUNT)
    return ranges_overlap(entry, std)


def has_valid_mapping_for(entries: list[SubordinateMapEntry], username: str) -> bool:
    """目标用户是否存在一条有效映射：长度 >= 65536、且与其它用户条目不冲突。"""
    user_entries = [e for e in entries if e.name == username]
    if not user_entries:
        return False
    other_entries = [e for e in entries if e.name != username]
    # 同名用户内部不能互相重叠
    for i, a in enumerate(user_entries):
        for b in user_entries[i + 1:]:
            if ranges_overlap(a, b):
                return False
    for ue in user_entries:
        if ue.count < STANDARD_SUBUID_COUNT:
            continue
        ok = True
        for oe in other_entries:
            if ranges_overlap(ue, oe):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------- 预检 -----------------

@dataclass
class CheckItem:
    name: str
    status: str  # PASS | FAIL | UNKNOWN
    detail: str = ""


@dataclass
class PreflightReport:
    distro_name: str
    items: list[CheckItem] = field(default_factory=list)
    _exit_cache: int | None = None

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.items.append(CheckItem(name=name, status=status, detail=detail))

    def all_passed(self) -> bool:
        return all(i.status == "PASS" for i in self.items)

    def exit_code(self) -> int:
        if self.all_passed():
            return 0
        if any(i.status == "FAIL" for i in self.items):
            return 1
        return 2  # 只有 UNKNOWN


def _detect_default_user(name: str) -> tuple[str, int, str] | None:
    """尝试通过发行版内 id -u、whoami 确定默认用户。返回 (user, uid, error) 之一。

    成功：(user, uid, ""); 失败：("", 0, error_detail)
    """
    res = distro.exec_distro(name, ["id", "-un"])
    if not res.ok:
        return None
    user = res.stdout.strip()
    res_uid = distro.exec_distro(name, ["id", "-u"])
    if not res_uid.ok:
        return (user, -1, "")
    try:
        uid = int(res_uid.stdout.strip())
    except ValueError:
        uid = -1
    return (user, uid, "")


def _classify_apt_policy(policy_stdout: str, policy_stderr: str, package: str) -> tuple[str, str]:
    """从 apt-cache policy <pkg> 的输出分类单项状态。

    Returns (status, detail)。
    """
    stdout = policy_stdout or ""
    stderr = policy_stderr or ""
    lowered = stderr.lower()
    # 失败分类优先从 stderr 抓
    if "temporary failure resolving" in lowered or "could not resolve" in lowered or "network is unreachable" in lowered:
        return ("FAIL", f"{package}: {APT_NET_ERROR_LABEL}")
    if "hash sum mismatch" in lowered or "hashes of expected file" in lowered:
        return ("FAIL", f"{package}: {APT_HASH_ERROR_LABEL}")
    # 从 stdout 的 Candidate: 行判断
    candidate = ""
    for line in stdout.splitlines():
        line = line.strip()
        if line.lower().startswith("candidate:"):
            candidate = line.split(":", 1)[1].strip()
            break
    if not candidate:
        # 没 Candidate 行也没 stderr 分类：判 UNKNOWN（索引过期）
        return ("UNKNOWN", f"{package}: {APT_UNKNOWN_LABEL}; {APT_POLICY_UNKNOWN_HINT}")
    if candidate.lower() in ("(none)", "n/a", ""):
        return ("FAIL", f"{package}: {APT_PKG_MISSING_LABEL}（当前软件源无可安装候选）")
    return ("PASS", f"{package} candidate={candidate}")


def preflight_check(distro_name: str) -> PreflightReport:
    """对指定发行版执行只读预检。不修改任何文件、不触发 apt update。"""
    report = PreflightReport(distro_name=distro_name)

    # 1. 发行版存在性 + WSL 版本 + openKylin 身份
    try:
        d = distro.get_distro(distro_name)
    except distro.WslError as exc:
        report.add("发行版存在", "FAIL", f"{distro_name} 未注册（wsl -l -v 查看：{exc}")
        return report
    if d is None:
        report.add("发行版存在", "FAIL", f"{distro_name} 未注册（wsl -l -v 查看）")
        return report
    if d.version != "2":
        report.add("WSL 版本", "FAIL", f"检测到 WSL{d.version}，要求 WSL2")
    else:
        report.add("WSL 版本", "PASS")

    os_release = distro.exec_distro(distro_name, ["cat", "/etc/os-release"])
    if not os_release.ok:
        report.add("openKylin 身份", "FAIL", f"无法读取 /etc/os-release：{os_release.stderr.strip() or f'exit={os_release.exit_code}'}")
    else:
        if "ID=openkylin" in os_release.stdout:
            report.add("openKylin 身份", "PASS")
        else:
            report.add("openKylin 身份", "FAIL", "/etc/os-release 中 ID 不是 openKylin")

    # 2. 默认用户非 root
    default_info = _detect_default_user(distro_name)
    if default_info is None:
        report.add("默认用户非 root", "FAIL", f"无法获取默认用户（命令失败）")
    else:
        user, uid, _err = default_info
        if user == "root" or uid == 0:
            report.add("默认用户非 root", "FAIL", f"检测到默认用户={user} uid={uid}，要求非 root 用户")
        else:
            report.add("默认用户非 root", "PASS", f"默认用户={user} uid={uid}")

    # 3. APT / dpkg 能力
    dpkg = distro.exec_distro(distro_name, ["dpkg", "--version"])
    apt_cache = distro.exec_distro(distro_name, ["apt-cache", "--version"])
    if not dpkg.ok:
        report.add("APT/dpkg 能力", "FAIL", f"dpkg 不可用：{dpkg.stderr.strip() or f'exit={dpkg.exit_code}'}")
    elif not apt_cache.ok:
        report.add("APT/dpkg 能力", "FAIL", f"apt-cache 不可用：{apt_cache.stderr.strip() or f'exit={apt_cache.exit_code}'}")
    else:
        report.add("APT/dpkg 能力", "PASS")

    # 4. 4 个直接包候选（只读，不 update）
    for pkg in DIRECT_PACKAGES:
        policy = distro.exec_distro(distro_name, ["apt-cache", "policy", pkg])
        status, detail = _classify_apt_policy(policy.stdout, policy.stderr, pkg)
        report.add(f"包候选 {pkg}", status, detail)

    # 5. subuid / subgid 映射探测
    default_user_for_map = default_info[0] if default_info and default_info[0] != "" else None
    subuid_text = ""
    subgid_text = ""
    r_subuid = distro.exec_distro(distro_name, ["cat", "/etc/subuid"])
    if r_subuid.ok:
        subuid_text = r_subuid.stdout
    r_subgid = distro.exec_distro(distro_name, ["cat", "/etc/subgid"])
    if r_subgid.ok:
        subgid_text = r_subgid.stdout
    if not r_subuid.ok:
        subuid_err = r_subuid.stderr.strip() or f"exit={r_subuid.exit_code}"
        report.add("subuid 映射", "UNKNOWN", f"/etc/subuid 读取失败：{subuid_err}（干净系统可能尚未生成）")
    elif not default_user_for_map:
        report.add("subuid 映射", "UNKNOWN", "无法定位默认用户，跳过映射有效性判定")
    else:
        entries = parse_subordinate_file(subuid_text)
        if has_valid_mapping_for(entries, default_user_for_map):
            report.add("subuid 映射", "PASS")
        else:
            conflict_std = any(range_conflicts_with_standard(e) for e in entries if e.name != default_user_for_map)
            detail = f"默认用户 {default_user_for_map} 无有效映射"
            if conflict_std:
                detail += "；其它账户映射与标准 [100000,165536) 存在重叠，install 阶段将拒绝自动追加"
            report.add("subuid 映射", "FAIL", detail)

    if not r_subgid.ok:
        subgid_err = r_subgid.stderr.strip() or f"exit={r_subgid.exit_code}"
        report.add("subgid 映射", "UNKNOWN", f"/etc/subgid 读取失败：{subgid_err}（干净系统可能尚未生成）")
    elif not default_user_for_map:
        report.add("subgid 映射", "UNKNOWN", "无法定位默认用户，跳过映射有效性判定")
    else:
        entries = parse_subordinate_file(subgid_text)
        if has_valid_mapping_for(entries, default_user_for_map):
            report.add("subgid 映射", "PASS")
        else:
            conflict_std = any(range_conflicts_with_standard(e) for e in entries if e.name != default_user_for_map)
            detail = f"默认用户 {default_user_for_map} 无有效映射"
            if conflict_std:
                detail += "；其它账户映射与标准 [100000,165536) 存在重叠，install 阶段将拒绝自动追加"
            report.add("subgid 映射", "FAIL", detail)

    return report


def format_preflight(report: PreflightReport) -> str:
    """把预检报告格式化为可读文本。"""
    lines = [f"== okw podman preflight：{report.distro_name} =="]
    max_w = max((len(i.name) for i in report.items), default=0)
    any_unknown = False
    any_fail = False
    for it in report.items:
        if it.status == "UNKNOWN":
            any_unknown = True
        if it.status == "FAIL":
            any_fail = True
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append("结论：预检全部通过，可以执行 okw podman install <name> --yes")
        lines.append("  提示：install 将执行 apt update 并以 root 身份修改系统文件。")
    else:
        summary = []
        if any_fail:
            summary.append(f"{sum(1 for i in report.items if i.status=='FAIL')} 项 FAIL")
        if any_unknown:
            summary.append(f"{sum(1 for i in report.items if i.status=='UNKNOWN')} 项 UNKNOWN")
        lines.append("结论：预检未通过（" + " / ".join(summary) + "）")
        lines.append("  请修复 FAIL 项后重试；UNKNOWN 项若由 APT 索引过期导致，")
        lines.append("  请在发行版内先手动执行 sudo apt update 后再重跑 preflight。")
    return "\n".join(lines)


def cmd_preflight(args) -> int:
    """CLI 入口：okw podman preflight <发行版>。"""
    name = args.name
    report = preflight_check(name)
    print(format_preflight(report))
    return report.exit_code()
