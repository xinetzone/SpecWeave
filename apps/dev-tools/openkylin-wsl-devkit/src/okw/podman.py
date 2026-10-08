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

# 三类 APT 失败各自的中文修复方向（AC-8/TR-2.4）
APT_PKG_MISSING_HINT = (
    "修复方向：确认当前软件源是否提供该包；禁止添加第三方源，"
    "如需启用官方 backports 或 proposed 组件请手动编辑 sources.list"
)
APT_NET_ERROR_HINT = "修复方向：检查发行版网络可达性与 DNS（如临时域名解析失败可稍后重试 apt update）"
APT_HASH_ERROR_HINT = (
    "修复方向：镜像源校验未通过，可更换官方镜像或在发行版内清理 "
    "/var/lib/apt/lists 后重新 apt update"
)
MAPPING_CONFLICT_HINT = (
    "请手动编辑 /etc/subuid 与 /etc/subgid，为目标用户选择不冲突的区间段后重跑 install"
)


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

    三列格式：name:start:count。任何非注释的畸形行都使整个文件无效，
    避免跳过未知映射后错误判断标准区间可用。
    """
    entries: list[SubordinateMapEntry] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(":")
        if len(parts) != 3:
            raise ValueError(f"映射文件第{line_number}行不是 name:start:count 三列")
        name, start_s, count_s = (p.strip() for p in parts)
        if not name or any(c.isspace() for c in name):
            raise ValueError(f"映射文件第{line_number}行用户名为空或含空白")
        if (
            not start_s.isascii()
            or not start_s.isdecimal()
            or not count_s.isascii()
            or not count_s.isdecimal()
        ):
            raise ValueError(f"映射文件第{line_number}行 start/count 必须为 ASCII 十进制整数")
        try:
            start = int(start_s)
            count = int(count_s)
        except ValueError as exc:
            raise ValueError(f"映射文件第{line_number}行 start/count 不是整数") from exc
        if start <= 0 or count <= 0:
            raise ValueError(f"映射文件第{line_number}行 start/count 必须为正整数")
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


def _is_apt_network_error(stderr: str) -> bool:
    lowered = (stderr or "").lower()
    return any(
        marker in lowered
        for marker in (
            "temporary failure resolving",
            "could not resolve",
            "network is unreachable",
            "could not connect",
            "failed to connect",
            "connection timed out",
            "connection refused",
            "connection reset",
        )
    )


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
    if _is_apt_network_error(stderr):
        return ("FAIL", f"{package}: {APT_NET_ERROR_LABEL}；{APT_NET_ERROR_HINT}")
    if "hash sum mismatch" in lowered or "hashes of expected file" in lowered:
        return ("FAIL", f"{package}: {APT_HASH_ERROR_LABEL}；{APT_HASH_ERROR_HINT}")
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
        return (
            "FAIL",
            f"{package}: {APT_PKG_MISSING_LABEL}（当前软件源无可安装候选）；{APT_PKG_MISSING_HINT}",
        )
    return ("PASS", f"{package} candidate={candidate}")


def _classify_apt_policy_result(policy: distro.CmdResult, package: str) -> tuple[str, str]:
    status, detail = _classify_apt_policy(policy.stdout, policy.stderr, package)
    if not policy.ok and APT_NET_ERROR_LABEL not in detail and APT_HASH_ERROR_LABEL not in detail:
        error = policy.stderr.strip() or f"exit={policy.exit_code}"
        return ("FAIL", f"{package}: apt-cache policy 命令失败（{error[:200]}）")
    return (status, detail)


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
        report.add("默认用户非 root", "FAIL", "无法获取默认用户（命令失败）")
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
        status, detail = _classify_apt_policy_result(policy, pkg)
        report.add(f"包候选 {pkg}", status, detail)

    # 5. subuid / subgid 映射探测
    default_user_for_map = default_info[0] if default_info and default_info[0] != "" else None
    _add_subordinate_item(report, distro_name, "/etc/subuid", "subuid 映射", default_user_for_map)
    _add_subordinate_item(report, distro_name, "/etc/subgid", "subgid 映射", default_user_for_map)

    return report


def _add_subordinate_item(
    report,
    distro_name: str,
    path: str,
    item_name: str,
    username: str | None,
    user: str | None = None,
) -> None:
    """读取一份从属 ID 映射文件并把判定结果追加到报告（preflight/verify 共用）。"""
    result = distro.exec_distro(distro_name, ["cat", path], user=user)
    if not result.ok:
        error = result.stderr.strip() or f"exit={result.exit_code}"
        report.add(item_name, "UNKNOWN", f"{path} 读取失败：{error}（干净系统可能尚未生成）")
        return
    if not username:
        report.add(item_name, "UNKNOWN", "无法定位默认用户，跳过映射有效性判定")
        return
    try:
        entries = parse_subordinate_file(result.stdout)
    except ValueError as exc:
        report.add(item_name, "FAIL", f"映射文件格式异常：{exc}")
        return
    if has_valid_mapping_for(entries, username):
        report.add(item_name, "PASS")
        return
    conflict_std = any(
        range_conflicts_with_standard(e) for e in entries if e.name != username
    )
    detail = f"默认用户 {username} 无有效映射"
    if conflict_std:
        detail += "；其它账户映射与标准 [100000,165536) 存在重叠，install 阶段将拒绝自动追加"
    report.add(item_name, "FAIL", detail)


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


# ----------------- 安装 -----------------

YES_SIDEEFFECTS_LINES = (
    "(1/4) 以 root 身份在发行版内执行 apt update，刷新 APT 索引；",
    "(2/4) 以 root 身份通过 apt install 安装 4 个包：podman / uidmap / slirp4netns / fuse-overlayfs；",
    "(3/4) 若默认用户缺少 subuid/subgid 映射，追加标准区间 [100000, 165536) 到 /etc/subuid 与 /etc/subgid；",
    "(4/4) 调用 rootless 验收检查（okw podman verify 的子集），确认 Podman 可作为默认用户运行。",
)


@dataclass
class InstallReport:
    distro_name: str
    items: list[CheckItem] = field(default_factory=list)
    missing_yes: bool = False

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.items.append(CheckItem(name=name, status=status, detail=detail))

    def all_passed(self) -> bool:
        return all(i.status == "PASS" for i in self.items)

    def exit_code(self) -> int:
        if self.missing_yes:
            return 2
        if self.all_passed():
            return 0
        if any(i.status == "FAIL" for i in self.items):
            return 1
        return 2


def _classify_apt_install_error(stderr: str, package: str, phase: str = "install") -> tuple[str, str]:
    """从 apt install 的 stderr 分类安装失败。"""
    lowered = (stderr or "").lower()
    if _is_apt_network_error(stderr):
        return ("FAIL", f"{package}: {APT_NET_ERROR_LABEL}；{APT_NET_ERROR_HINT}")
    if "hash sum mismatch" in lowered or "hashes of expected file" in lowered:
        return ("FAIL", f"{package}: {APT_HASH_ERROR_LABEL}；{APT_HASH_ERROR_HINT}")
    if "unable to locate package" in lowered or "has no installation candidate" in lowered or "couldn't find any package" in lowered:
        return ("FAIL", f"{package}: {APT_PKG_MISSING_LABEL}；{APT_PKG_MISSING_HINT}")
    label = "apt " + phase
    return ("FAIL", f"{package}: {label} 失败（stderr={stderr.strip()[:200] if stderr else '未知'}）")


def _apt_update_and_install(name: str, report: InstallReport) -> None:
    """执行 apt update → 逐包复查 candidate → apt install 4 直接包。"""
    update = distro.exec_distro(name, ["apt", "update"], user="root")
    if not update.ok:
        stage, detail = _classify_apt_install_error(update.stderr, "apt update", phase="update")
        report.add("apt update", stage, detail)
        return
    report.add("apt update", "PASS")

    for pkg in DIRECT_PACKAGES:
        policy = distro.exec_distro(name, ["apt-cache", "policy", pkg])
        status, detail = _classify_apt_policy_result(policy, pkg)
        if status != "PASS":
            report.add(f"候选复查 {pkg}", status, detail)
            return
        report.add(f"候选复查 {pkg}", "PASS", detail)

    install_cmd = ["apt", "install", "-y", "--no-install-recommends", *DIRECT_PACKAGES]
    install = distro.exec_distro(name, install_cmd, user="root")
    if not install.ok:
        # 安装失败不区分具体哪包，统一用 stderr 分类；注意 apt install 可能一次装多包
        stage, detail = _classify_apt_install_error(install.stderr, DIRECT_PACKAGES[0])
        # 细节里标注其他包也可能受影响
        full_detail = f"4 包批量安装失败：{detail[detail.find(':')+1:] if ':' in detail else detail}"
        report.add("apt install 4 包", stage, full_detail)
        return
    report.add("apt install 4 包", "PASS", ", ".join(DIRECT_PACKAGES))


def _mapping_writer_script() -> str:
    """返回先校验两份映射文件、再协调追加的发行版内脚本。"""
    return """import os, stat, sys
try:
    import fcntl
except ImportError:
    fcntl = None

uid_path, gid_path, username, start_text, count_text = sys.argv[1:6]
start = int(start_text)
count = int(count_text)
end = start + count
advice = "请手动编辑 /etc/subuid 与 /etc/subgid，为目标用户选择不冲突的区间段后重跑 install。"

def fail(code, message):
    print(message, file=sys.stderr)
    raise SystemExit(code)

def overlaps(left_start, left_end, right_start, right_end):
    return left_start < right_end and right_start < left_end

paths = (uid_path, gid_path)
lock_fds = []
handles = []
snapshots = {}
created_paths = set()
changed = []

def restore_files(file_paths):
    errors = []
    for path in reversed(file_paths):
        original, existed, unused = snapshots[path]
        try:
            with open(path, "rb") as stream:
                current = stream.read()
        except FileNotFoundError:
            current = b""
        appended = current[len(original):] if current.startswith(original) else None
        expected = suffixes.get(path, b"")
        if appended is None or not expected.startswith(appended):
            errors.append(path + ": 检测到并发修改，未截断文件")
            continue
        if path in created_paths:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
            except OSError as exc:
                errors.append(path + ": " + str(exc))
            continue
        if existed:
            fd = None
            try:
                fd = os.open(path, os.O_WRONLY)
                os.ftruncate(fd, len(original))
                os.fsync(fd)
            except OSError as exc:
                errors.append(path + ": " + str(exc))
            finally:
                if fd is not None:
                    try:
                        os.close(fd)
                    except OSError as exc:
                        errors.append(path + ": " + str(exc))
    return errors

def read_entries(path):
    try:
        with open(path, "rb") as stream:
            original = stream.read()
        existed = True
    except FileNotFoundError:
        original = b""
        existed = False
    try:
        text = original.decode("utf-8")
    except UnicodeDecodeError:
        fail(2, "MAPPING_INVALID: " + path + " 不是有效 UTF-8；" + advice)

    entries = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(":")
        if len(parts) != 3:
            fail(2, "MAPPING_INVALID: " + path + " 第" + str(line_number) + "行不是三列；" + advice)
        name, start_value, count_value = (part.strip() for part in parts)
        if not name or any(char.isspace() for char in name):
            fail(2, "MAPPING_INVALID: " + path + " 第" + str(line_number) + "行用户名无效；" + advice)
        try:
            entry_start = int(start_value)
            entry_count = int(count_value)
        except ValueError:
            fail(2, "MAPPING_INVALID: " + path + " 第" + str(line_number) + "行 start/count 不是整数；" + advice)
        if (
            not start_value.isascii()
            or not start_value.isdecimal()
            or not count_value.isascii()
            or not count_value.isdecimal()
        ):
            fail(2, "MAPPING_INVALID: " + path + " 第" + str(line_number) + "行 start/count 必须为 ASCII 十进制整数；" + advice)
        if entry_start <= 0 or entry_count <= 0:
            fail(2, "MAPPING_INVALID: " + path + " 第" + str(line_number) + "行 start/count 必须为正整数；" + advice)
        entries.append((name, entry_start, entry_start + entry_count, entry_count))
    return original, existed, entries

def validate(path, entries):
    user_entries = [entry for entry in entries if entry[0] == username]
    conflicts = []
    for index, left in enumerate(user_entries):
        for right in user_entries[index + 1:]:
            if overlaps(left[1], left[2], right[1], right[2]):
                conflicts.extend((left, right))
    for target in user_entries:
        for other in entries:
            if other[0] != username and overlaps(target[1], target[2], other[1], other[2]):
                conflicts.extend((target, other))
    if conflicts:
        details = ", ".join(
            entry[0] + ":" + str(entry[1]) + ":" + str(entry[2] - entry[1])
            for entry in dict.fromkeys(conflicts)
        )
        fail(2, "MAPPING_CONFLICT: " + path + " 目标用户既有映射冲突：" + details + "；" + advice)

    has_valid = any(
        entry[3] >= count
        and all(
            other[0] == username
            or not overlaps(entry[1], entry[2], other[1], other[2])
            for other in entries
        )
        for entry in user_entries
    )
    if has_valid:
        return b""
    if user_entries:
        details = ", ".join(
            entry[0] + ":" + str(entry[1]) + ":" + str(entry[3])
            for entry in user_entries
        )
        fail(
            2,
            "MAPPING_INVALID: " + path + " 目标用户已有映射但跨度不足：" + details + "；" + advice,
        )

    conflicts = [entry for entry in entries if overlaps(entry[1], entry[2], start, end)]
    if conflicts:
        details = ", ".join(
            entry[0] + ":" + str(entry[1]) + ":" + str(entry[2] - entry[1])
            for entry in conflicts
        )
        fail(2, "MAPPING_CONFLICT: " + path + " 标准区间 [100000, 165536) 冲突：" + details + "；" + advice)

    original = snapshots[path][0]
    separator = b"" if not original or original.endswith(b"\\n") else b"\\n"
    return separator + (username + ":" + start_text + ":" + count_text + "\\n").encode("utf-8")

try:
    directories = sorted({os.path.dirname(os.path.abspath(path)) for path in paths})
    if fcntl is not None:
        for directory in directories:
            lock_fd = os.open(directory, os.O_RDONLY)
            lock_fds.append(lock_fd)
            fcntl.flock(lock_fd, fcntl.LOCK_EX)

    for path in paths:
        snapshots[path] = read_entries(path)

    suffixes = {path: validate(path, snapshots[path][2]) for path in paths}
    changed = [path for path in paths if suffixes[path]]
    if not changed:
        print("ALREADY")
        sys.exit(0)

    for path in changed:
        existed = snapshots[path][1]
        flags = os.O_WRONLY | os.O_APPEND
        if not existed:
            flags |= os.O_CREAT | os.O_EXCL
        fd = os.open(path, flags, 0o600)
        if not existed:
            created_paths.add(path)
        if existed and os.name == "posix" and stat.S_IMODE(os.fstat(fd).st_mode) & 0o022:
            os.close(fd)
            raise OSError("MAPPING_INVALID: " + path + " 组或其他用户可写；" + advice)
        try:
            mapping = os.fdopen(fd, "ab", buffering=0)
        except Exception:
            try:
                os.close(fd)
            except OSError:
                pass
            raise
        handles.append((path, mapping))

    try:
        for path, mapping in handles:
            suffix = suffixes[path]
            written = mapping.write(suffix)
            if written != len(suffix):
                raise OSError("追加字节数不完整：" + path)
            mapping.flush()
            os.fsync(mapping.fileno())
    except Exception as exc:
        close_errors = []
        for path, mapping in handles:
            try:
                mapping.close()
            except OSError as close_error:
                close_errors.append(str(close_error))
        handles = []
        rollback_errors = restore_files(changed)
        if rollback_errors:
            fail(1, "MAPPING_WRITE_FAILED: 写入失败且回滚不完整：" + "; ".join(rollback_errors))
        close_detail = ("；关闭错误：" + "; ".join(close_errors)) if close_errors else ""
        fail(1, "MAPPING_WRITE_FAILED: 写入失败，原文件已恢复：" + str(exc) + close_detail)

    close_errors = []
    for path, mapping in handles:
        try:
            mapping.close()
        except OSError as close_error:
            close_errors.append(str(close_error))
    handles = []
    if close_errors:
        rollback_errors = restore_files(changed)
        if rollback_errors:
            fail(
                1,
                "MAPPING_WRITE_FAILED: 关闭失败且回滚不完整："
                + "; ".join(close_errors + rollback_errors),
            )
        fail(
            1,
            "MAPPING_WRITE_FAILED: 关闭映射文件失败，原文件已恢复："
            + "; ".join(close_errors),
        )

    print("APPENDED")
except SystemExit:
    raise
except OSError as exc:
    close_errors = []
    for path, mapping in handles:
        try:
            mapping.close()
        except OSError as close_error:
            close_errors.append(str(close_error))
    handles = []
    rollback_errors = restore_files(changed)
    if rollback_errors:
        fail(
            1,
            "MAPPING_WRITE_FAILED: 无法安全更新且回滚不完整："
            + "; ".join(close_errors + rollback_errors),
        )
    fail(1, "MAPPING_WRITE_FAILED: 无法安全更新 subuid/subgid：" + str(exc))
finally:
    for path, mapping in handles:
        try:
            mapping.close()
        except OSError:
            pass
    for lock_fd in reversed(lock_fds):
        if fcntl is not None:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)
"""


def _ensure_subordinate_files(name: str, default_user: str, report: InstallReport) -> None:
    """先共同校验 subuid/subgid，再以一次发行版内调用幂等追加。"""
    res = distro.exec_distro(
        name,
        [
            "python3",
            "-c",
            _mapping_writer_script(),
            "/etc/subuid",
            "/etc/subgid",
            default_user,
            str(STANDARD_SUBUID_START),
            str(STANDARD_SUBUID_COUNT),
        ],
        user="root",
    )
    if not res.ok:
        res_err = res.stderr.strip() or f"exit={res.exit_code}"
        detail = f"两份原文件均未确认修改：{res_err}"
        if "MAPPING_CONFLICT" in res_err:
            detail += f"；{MAPPING_CONFLICT_HINT}"
        elif "MAPPING_INVALID" in res_err:
            detail += "；请检查映射文件的三列格式、正整数值及目标用户映射有效性后重跑 install"
        elif "MAPPING_WRITE_FAILED" in res_err:
            detail += "；请检查映射文件权限与磁盘空间后重跑 install"
        report.add("subuid/subgid 映射", "FAIL", detail)
        return
    result = res.stdout.strip()
    if result == "ALREADY":
        report.add("subuid/subgid 映射", "PASS", f"{default_user} 的 UID/GID 映射均有效，未修改文件")
    elif result == "APPENDED":
        report.add(
            "subuid/subgid 映射",
            "PASS",
            f"两份文件均已校验，仅追加缺失的 {default_user}:{STANDARD_SUBUID_START}:{STANDARD_SUBUID_COUNT}",
        )
    else:
        report.add("subuid/subgid 映射", "FAIL", f"写入结果无法确认（输出：{result or '空'}）")


def install_run(name: str, yes: bool) -> InstallReport:
    """执行 install 主流程。"""
    report = InstallReport(distro_name=name)
    if not yes:
        report.missing_yes = True
        return report

    # 包候选可因旧索引暂时不可用，安装会刷新索引后复查；结构性失败则必须先停止。
    pre = preflight_check(name)
    structural_checks = {
        "发行版存在",
        "WSL 版本",
        "openKylin 身份",
        "默认用户非 root",
        "APT/dpkg 能力",
    }
    failed_checks = [
        item for item in pre.items
        if item.name in structural_checks and item.status == "FAIL"
    ]
    if failed_checks:
        for item in failed_checks:
            report.add(item.name, "FAIL", item.detail)
        return report

    user_result = distro.exec_distro(name, ["id", "-un"])
    uid_result = distro.exec_distro(name, ["id", "-u"])
    if not user_result.ok or not uid_result.ok:
        detail = user_result.stderr.strip() or uid_result.stderr.strip() or "无法读取默认用户身份"
        report.add("默认用户非 root", "FAIL", detail)
        return report
    default_user = user_result.stdout.strip()
    try:
        default_uid = int(uid_result.stdout.strip())
    except ValueError:
        report.add("默认用户非 root", "FAIL", "默认用户 UID 不是有效整数")
        return report
    if not default_user or default_user == "root" or default_uid <= 0:
        report.add(
            "默认用户非 root",
            "FAIL",
            f"检测到默认用户={default_user or '未知'} uid={default_uid}，要求非 root 用户",
        )
        return report

    # APT 流程
    _apt_update_and_install(name, report)
    if not report.all_passed():
        return report

    # 映射幂等追加
    _ensure_subordinate_files(name, default_user, report)
    if any(i.status == "FAIL" for i in report.items):
        return report

    # 子集验收：podman --version + 以默认用户跑 podman info 中 rootless 状态（不跑容器）
    pv = distro.exec_distro(name, ["podman", "--version"])
    if not pv.ok:
        report.add("podman --version", "FAIL",
            f"{pv.stderr.strip() or f'exit={pv.exit_code}'}（请确认安装成功）")
        return report
    report.add("podman --version", "PASS", pv.stdout.strip())

    info = distro.exec_distro(name, ["podman", "info", "--format", "{{.Host.Security.Rootless}}"], user=default_user)
    if not info.ok:
        report.add("rootless 验收", "FAIL",
            f"podman info 失败：{info.stderr.strip() or f'exit={info.exit_code}'}")
        return report
    out = info.stdout.strip()
    if out.lower() == "true":
        report.add("rootless 验收", "PASS")
    else:
        report.add("rootless 验收", "FAIL",
            f"podman info 返回 Rootless={out!r}，预期 true。请确认 subuid/subgid 已生效并重登")
    return report


def format_install(report: InstallReport) -> str:
    lines = [f"== okw podman install：{report.distro_name} =="]
    if report.missing_yes:
        lines.append("未提供 --yes，为避免以下副作用，任何写入操作均未执行：")
        lines.extend(f"  {line}" for line in YES_SIDEEFFECTS_LINES)
        lines.append("")
        lines.append("请确认副作用可接受后，重跑：okw podman install <发行版> --yes")
        return "\n".join(lines)

    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append("结论：安装成功，可执行 okw podman verify <发行版> [--smoke-image <本地镜像>] 进行验收")
    else:
        lines.append(f"结论：安装未通过（{sum(1 for i in report.items if i.status=='FAIL')} 项 FAIL）")
        lines.append("  请根据 FAIL 项修复后重试；注意本流程不宣称事务回滚，")
        lines.append("  apt update / 部分包安装 / 映射写入可能已部分生效。")
        all_detail = "\n".join(i.detail for i in report.items if i.status == "FAIL")
        if APT_PKG_MISSING_LABEL in all_detail:
            lines.append(f"  {APT_PKG_MISSING_HINT}")
        if APT_NET_ERROR_LABEL in all_detail:
            lines.append(f"  {APT_NET_ERROR_HINT}")
        if APT_HASH_ERROR_LABEL in all_detail:
            lines.append(f"  {APT_HASH_ERROR_HINT}")
    return "\n".join(lines)


def cmd_install(args) -> int:
    """CLI 入口：okw podman install <发行版> [--yes]。"""
    name = args.name
    yes = getattr(args, "yes", False)
    if not yes:
        report = InstallReport(distro_name=name, missing_yes=True)
        print(format_install(report))
        return report.exit_code()
    report = install_run(name, yes=True)
    print(format_install(report))
    return report.exit_code()


# ----------------- 验收（只读；冒烟仅用本地镜像，禁止拉取） -----------------

# 冒烟容器固定的禁拉取语义与最小探针（要求镜像内存在 /bin/true，常规发行版镜像均满足）
SMOKE_PULL_POLICY = "--pull=never"
SMOKE_PROBE_ARGS = ("/bin/true",)

PODMAN_MISSING_HINT = "请先执行 okw podman install <发行版> --yes 完成安装后重跑 verify"
UNSHARE_FAIL_HINT = (
    "用户命名空间不可用：请确认 WSL2 内核允许非特权 user namespace、"
    "subuid/subgid 映射已配置并在写入后重新登录发行版会话"
)
ROOT_VERIFY_HINT = (
    "root 身份下 Podman 必为 rootful，禁止据此报告 rootless PASS；"
    "请改用非 root 默认用户执行 verify"
)
SMOKE_IMAGE_MISSING_HINT = (
    "本地镜像不存在：请先在发行版内执行 podman pull <镜像> 或 "
    "podman load -i <镜像包> 后再试；verify 不会触发任何隐式拉取"
)
SMOKE_RUN_HINT = (
    f"可在发行版内手动复现：podman run --rm {SMOKE_PULL_POLICY} <镜像> /bin/true"
)


@dataclass
class VerifyReport:
    distro_name: str
    smoke_image: str | None = None
    items: list[CheckItem] = field(default_factory=list)

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


def verify_run(distro_name: str, smoke_image: str | None = None) -> VerifyReport:
    """以发行版默认非 root 用户执行只读 rootless 验收。

    默认不创建/启动任何容器；仅当显式给出 smoke_image 时跑一次性临时容器，
    且全程禁止拉取镜像（先 podman image exists 本地确认，再 --pull=never）。
    """
    report = VerifyReport(distro_name=distro_name, smoke_image=smoke_image)

    try:
        d = distro.get_distro(distro_name)
    except distro.WslError as exc:
        report.add("发行版存在", "FAIL", f"{distro_name} 未注册（wsl -l -v 查看：{exc}）")
        return report
    if d is None:
        report.add("发行版存在", "FAIL", f"{distro_name} 未注册（wsl -l -v 查看）")
        return report
    if d.version != "2":
        report.add("WSL 版本", "FAIL", f"检测到 WSL{d.version}，rootless Podman 要求 WSL2")
    else:
        report.add("WSL 版本", "PASS")

    # 验收必须以默认用户身份执行；身份不明时后续用户级检查无意义
    user_result = distro.exec_distro(distro_name, ["id", "-un"])
    uid_result = distro.exec_distro(distro_name, ["id", "-u"])
    if not user_result.ok or not uid_result.ok:
        detail = user_result.stderr.strip() or uid_result.stderr.strip() or "无法读取默认用户身份"
        report.add("默认用户非 root", "FAIL", detail)
        return report
    default_user = user_result.stdout.strip()
    try:
        default_uid = int(uid_result.stdout.strip())
    except ValueError:
        report.add("默认用户非 root", "FAIL", "默认用户 UID 不是有效整数")
        return report
    is_root = (not default_user) or default_user == "root" or default_uid == 0
    if is_root:
        report.add(
            "默认用户非 root",
            "FAIL",
            f"检测到默认用户={default_user or '未知'} uid={default_uid}，root 身份不得作为 rootless 验收对象",
        )
    else:
        report.add("默认用户非 root", "PASS", f"默认用户={default_user} uid={default_uid}")

    # 1. Podman 是否可执行及版本
    pv = distro.exec_distro(distro_name, ["podman", "--version"], user=default_user)
    if not pv.ok:
        error = pv.stderr.strip() or f"exit={pv.exit_code}"
        report.add("podman 版本", "FAIL", f"无法执行 podman --version：{error}；{PODMAN_MISSING_HINT}")
    else:
        report.add("podman 版本", "PASS", pv.stdout.strip())

    # 2. subuid/subgid 映射（只读解析）
    _add_subordinate_item(
        report, distro_name, "/etc/subuid", "subuid 映射", default_user, user=default_user
    )
    _add_subordinate_item(
        report, distro_name, "/etc/subgid", "subgid 映射", default_user, user=default_user
    )

    # 3. 用户命名空间可用性
    unshare = distro.exec_distro(
        distro_name,
        ["unshare", "--user", "--map-root-user", "/bin/true"],
        user=default_user,
    )
    if unshare.ok:
        report.add("unshare 用户命名空间", "PASS")
    else:
        error = unshare.stderr.strip() or f"exit={unshare.exit_code}"
        report.add(
            "unshare 用户命名空间", "FAIL", f"unshare 探针失败：{error}；{UNSHARE_FAIL_HINT}"
        )

    # 4. Podman 自报的 rootless 状态；root 身份即使返回 true 也强制 FAIL（AC-4）
    info = distro.exec_distro(
        distro_name,
        ["podman", "info", "--format", "{{.Host.Security.Rootless}}"],
        user=default_user,
    )
    rootless_value = info.stdout.strip() if info.ok else ""
    if is_root:
        detail = ROOT_VERIFY_HINT
        if rootless_value:
            detail += f"（实测 podman info Rootless={rootless_value!r}）"
        report.add("rootless 状态", "FAIL", detail)
    elif not info.ok:
        error = info.stderr.strip() or f"exit={info.exit_code}"
        report.add("rootless 状态", "FAIL", f"podman info 失败：{error}")
    elif rootless_value.lower() == "true":
        report.add("rootless 状态", "PASS")
    else:
        report.add(
            "rootless 状态",
            "FAIL",
            f"podman info 返回 Rootless={rootless_value!r}，预期 true；"
            "请确认 subuid/subgid 已生效并重新登录会话",
        )

    # 5. 可选：仅本地镜像的一次性容器冒烟（任何路径都不得拉取）
    if smoke_image is not None:
        if any(i.status == "FAIL" for i in report.items):
            report.add("冒烟容器", "FAIL", "前置检查存在 FAIL，未执行容器冒烟")
            return report
        exists = distro.exec_distro(
            distro_name, ["podman", "image", "exists", smoke_image], user=default_user
        )
        if not exists.ok:
            if exists.exit_code == 1:
                report.add(
                    "冒烟容器",
                    "FAIL",
                    f"本地镜像 {smoke_image} 不存在（podman image exists=1）；{SMOKE_IMAGE_MISSING_HINT}",
                )
            else:
                error = exists.stderr.strip() or f"exit={exists.exit_code}"
                report.add("冒烟容器", "FAIL", f"本地镜像检查失败：{error}；{SMOKE_IMAGE_MISSING_HINT}")
            return report
        run = distro.exec_distro(
            distro_name,
            [
                "podman", "run", "--rm", SMOKE_PULL_POLICY,
                smoke_image, *SMOKE_PROBE_ARGS,
            ],
            user=default_user,
        )
        if run.ok:
            report.add("冒烟容器", "PASS", f"{smoke_image} 临时容器以 {SMOKE_PULL_POLICY} 运行成功")
        else:
            error = run.stderr.strip() or f"exit={run.exit_code}"
            report.add(
                "冒烟容器",
                "FAIL",
                f"{smoke_image} 容器运行失败：{error[:200]}；{SMOKE_RUN_HINT}",
            )

    return report


def format_verify(report: VerifyReport) -> str:
    """把验收报告格式化为可读文本。"""
    lines = [f"== okw podman verify：{report.distro_name} =="]
    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        if report.smoke_image is not None:
            lines.append("结论：rootless 验收与本地镜像容器冒烟全部通过")
        else:
            lines.append("结论：rootless 验收通过（默认只读，未执行容器冒烟）")
            lines.append("  如需冒烟：okw podman verify <发行版> --smoke-image <本地已存在镜像>")
    else:
        fail_count = sum(1 for i in report.items if i.status == "FAIL")
        unknown_count = sum(1 for i in report.items if i.status == "UNKNOWN")
        summary = []
        if fail_count:
            summary.append(f"{fail_count} 项 FAIL")
        if unknown_count:
            summary.append(f"{unknown_count} 项 UNKNOWN")
        lines.append("结论：验收未通过（" + " / ".join(summary) + "）")
        lines.append("  本命令为只读检查，未修改发行版任何配置；")
        lines.append("  容器冒烟也只使用本地镜像并显式禁止拉取（--pull=never）。")
    return "\n".join(lines)


def cmd_verify(args) -> int:
    """CLI 入口：okw podman verify <发行版> [--smoke-image LOCAL_IMAGE]。"""
    smoke_image = getattr(args, "smoke_image", None)
    report = verify_run(args.name, smoke_image=smoke_image)
    print(format_verify(report))
    return report.exit_code()
