"""okw ai 子命令：预检、安装和验收 openKylin WSL 内的 AI 栈。

本期只落地**唯一已落机验证的 Gen1 SDK / OCR 路径**（见知识库
references/ai-sdk-ocr-poc.md）：安装直接包 ``libkylin-ai-base-dev``，由 APT
解析 OCR 运行库、tesseract 与语言包。Gen2 全栈、模型下载、ollama 等仅只读盘点。

零第三方依赖：WSL 调用经 okw.distro；APT 的 C locale argv、长超时与网络/哈希/
缺包分类复用 okw.podman；Windows→发行版路径转换复用 okw.image。
"""

import re

from okw import distro, podman

# Windows 盘符路径 → 发行版 /mnt 路径的混合归一（见 to_distro_image_path）
_DRIVE_RE = re.compile(r"^([A-Za-z]):[\\/]+(.*)$")


def to_distro_image_path(path: str) -> str:
    """把图片路径归一为发行版内可访问路径。

    - 已以 ``/`` 开头：发行版内路径，原样返回；
    - Windows 盘符路径（``C:\\...`` / ``C:/...``）：转 ``/mnt/c/...``；
    - 其它：反斜杠转正斜杠透传。
    """
    text = (path or "").strip()
    if text.startswith("/"):
        return text
    match = _DRIVE_RE.match(text)
    if match:
        tail = match.group(2).replace("\\", "/")
        return f"/mnt/{match.group(1).lower()}/{tail}"
    return text.replace("\\", "/")

# 预检/验收的报告与逐项结果复用 podman 的通用呈现容器
CheckItem = podman.CheckItem
InstallReport = podman.InstallReport


class AiPreflightReport(podman.PreflightReport):
    """preflight 报告：可选层 UNKNOWN 仅信息展示，不参与门控退出码。"""

    def __init__(self, distro_name: str):
        super().__init__(distro_name=distro_name)
        self.optional_names: set = set()

    def mark_optional(self, name: str) -> None:
        self.optional_names.add(name)

    def _gating_items(self):
        return [i for i in self.items if i.name not in self.optional_names]

    def all_passed(self) -> bool:
        return all(i.status == "PASS" for i in self._gating_items())

    def exit_code(self) -> int:
        gating = self._gating_items()
        if all(i.status == "PASS" for i in gating):
            return 0
        if any(i.status == "FAIL" for i in gating):
            return 1
        return 2  # 必选项仅 UNKNOWN


class AiVerifyReport(podman.VerifyReport):
    """verify 报告：OCR 必选项决定门控，可选层 UNKNOWN 不阻断。"""

    def __init__(self, distro_name: str, smoke_image=None):
        super().__init__(distro_name=distro_name, smoke_image=smoke_image)
        self.optional_names: set = set()

    def mark_optional(self, name: str) -> None:
        self.optional_names.add(name)

    def _gating_items(self):
        return [i for i in self.items if i.name not in self.optional_names]

    def all_passed(self) -> bool:
        return all(i.status == "PASS" for i in self._gating_items())

    def exit_code(self) -> int:
        gating = self._gating_items()
        if all(i.status == "PASS" for i in gating):
            return 0
        if any(i.status == "FAIL" for i in gating):
            return 1
        return 2


# 别名便于 handler 引用
PreflightReport = AiPreflightReport
VerifyReport = AiVerifyReport

# 唯一已落机验证的直接包（POC 实测命令：
# apt-get install -y --no-install-recommends libkylin-ai-base-dev）
DIRECT_PACKAGES = ("libkylin-ai-base-dev",)

# OCR 本地识别固定语言与引擎参数（离线、CPU）
OCR_LANGS = ("chi_sim", "eng")
OCR_LANG_SPEC = "+".join(OCR_LANGS)


class AiComponent:
    """AI 栈分层组件（不可变）。

    required=True 表示属于已验证 OCR 路径，缺失影响安装/验收；
    required=False 为可选层，缺失仅 UNKNOWN 不阻断。
    """

    __slots__ = ("key", "package", "title", "required")

    def __init__(self, key: str, package: str, title: str, required: bool):
        self.key = key
        self.package = package
        self.title = title
        self.required = required

    def __repr__(self) -> str:
        return f"AiComponent(key={self.key!r}, package={self.package!r}, required={self.required})"


# 分层组件清单：顺序即报告顺序
COMPONENTS = (
    AiComponent("gen1-sdk", "libkylin-ai-base-dev", "Gen1 SDK 开发包（OCR 安装目标）", True),
    AiComponent("gen1-runtime", "libkylin-ai-base2", "Gen1 SDK 运行库", True),
    AiComponent("ocr-engine", "tesseract-ocr", "OCR 引擎 tesseract", True),
    AiComponent("ocr-lang-chi", "tesseract-ocr-chi-sim", "tesseract 中文语言包", True),
    AiComponent("ocr-lang-eng", "tesseract-ocr-eng", "tesseract 英文语言包", True),
    AiComponent("model-manager", "kylin-ai-model-manager", "麒麟模型管理工具（上游自述不完善）", False),
    AiComponent("gen2-nlp", "libkysdk-genai-nlp0", "Gen2 文本生成客户端（IPC 薄代理）", False),
    AiComponent("engine-plugins", "kylin-ai-engine-plugins", "引擎插件集合", False),
    AiComponent("ondevice-nlp", "kylin-ondevice-nlp-engine", "本地 NLP 引擎插件（Triton 客户端）", False),
    AiComponent("kytensor", "kytensor-server", "Triton 推理服务（kytensor）", False),
    AiComponent("ollama", "ollama", "ollama（不在 openKylin 官方源）", False),
)

ALL_PACKAGES = tuple(c.package for c in COMPONENTS)
_BY_PACKAGE = {c.package: c for c in COMPONENTS}

# 可选层缺失时的角色说明（okw 不自动安装/不下载模型）
OPTIONAL_MISSING_NOTE = {
    "kylin-ai-model-manager": "未安装；如需可在发行版内手动 sudo apt install kylin-ai-model-manager，okw 不默认安装",
    "libkysdk-genai-nlp0": "未安装；Gen2 客户端为 IPC 薄代理，还需引擎插件与模型，okw 不自动安装",
    "kylin-ai-engine-plugins": "未安装；Gen2 引擎插件端到端未验证，okw 不自动安装、不下载模型",
    "kylin-ondevice-nlp-engine": "未安装；本地 NLP 还需 kytensor 与自备 GGUF，okw 不自动安装",
    "kytensor-server": "未安装；推理服务与模型仓库需另行准备，okw 不启动服务、不下载模型",
    "ollama": "不在 openKylin 官方源；需官方 install.sh，okw 不执行 curl|sh、不自动安装",
}

OCR_INSTALL_HINT = "请先执行 okw ai install <发行版> --yes 完成 OCR 路径安装后重跑"

# ----------------- 结构预检（preflight/install 共用） -----------------

STRUCTURAL_ITEM_NAMES = ("发行版存在", "WSL 版本", "openKylin 身份", "APT/dpkg 能力")


def add_structural_checks(report, distro_name: str, need_apt: bool = True) -> bool:
    """把发行版存在/WSL2/openKylin/APT 能力等结构项写入报告。

    返回 True 表示结构全部 PASS；任一 FAIL 返回 False。OCR 任意用户可用，
    故不像 podman 那样强制默认用户非 root。
    """
    try:
        d = distro.get_distro(distro_name)
    except distro.WslError as exc:
        report.add("发行版存在", "FAIL", f"{distro_name} 未注册（wsl -l -v 查看：{exc}")
        return False
    if d is None:
        report.add("发行版存在", "FAIL", f"{distro_name} 未注册（wsl -l -v 查看）")
        return False
    if d.version != "2":
        report.add("WSL 版本", "FAIL", f"检测到 WSL{d.version}，要求 WSL2")
    else:
        report.add("WSL 版本", "PASS")

    os_release = distro.exec_distro(distro_name, ["cat", "/etc/os-release"])
    if not os_release.ok:
        report.add(
            "openKylin 身份", "FAIL",
            f"无法读取 /etc/os-release：{os_release.stderr.strip() or f'exit={os_release.exit_code}'}",
        )
    elif "ID=openkylin" in os_release.stdout:
        report.add("openKylin 身份", "PASS")
    else:
        report.add("openKylin 身份", "FAIL", "/etc/os-release 中 ID 不是 openkylin")

    if not need_apt:
        return not any(
            i.name in ("发行版存在", "WSL 版本", "openKylin 身份") and i.status == "FAIL"
            for i in report.items
        )

    dpkg = distro.exec_distro(distro_name, ["dpkg", "--version"])
    apt_cache = distro.exec_distro(distro_name, podman._apt_argv("apt-cache", "--version"))
    if not dpkg.ok:
        report.add(
            "APT/dpkg 能力", "FAIL",
            f"dpkg 不可用：{dpkg.stderr.strip() or f'exit={dpkg.exit_code}'}",
        )
    elif not apt_cache.ok:
        report.add(
            "APT/dpkg 能力", "FAIL",
            f"apt-cache 不可用：{apt_cache.stderr.strip() or f'exit={apt_cache.exit_code}'}",
        )
    else:
        report.add("APT/dpkg 能力", "PASS")

    return not any(i.name in STRUCTURAL_ITEM_NAMES and i.status == "FAIL" for i in report.items)


# ----------------- apt-cache policy 批量盘点 -----------------

_HEADER_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9+.-]*):\s*$")


def parse_policy_batch(stdout: str) -> dict:
    """解析 ``apt-cache policy pkg1 pkg2 ...`` 输出。

    返回 ``{package: {"installed": str, "candidate": str}}``；输出中没有分段的
    包不会出现在结果里（调用方据此区分"索引缺失"与"候选 (none)"）。
    """
    result: dict = {}
    current = None
    for raw in (stdout or "").splitlines():
        header = _HEADER_RE.match(raw)
        if header and header.group(1) in _BY_PACKAGE:
            current = header.group(1)
            result[current] = {"installed": "", "candidate": ""}
            continue
        if current is None:
            continue
        stripped = raw.strip()
        field_name = None
        value = ""
        if stripped.startswith("Installed:"):
            field_name, value = "installed", stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Candidate:"):
            field_name, value = "candidate", stripped.split(":", 1)[1].strip()
        elif stripped.startswith("已安装："):
            field_name, value = "installed", stripped.split("：", 1)[1].strip()
        elif stripped.startswith("已安装:"):
            field_name, value = "installed", stripped.split(":", 1)[1].strip()
        elif stripped.startswith("候选："):
            field_name, value = "candidate", stripped.split("：", 1)[1].strip()
        elif stripped.startswith("候选:"):
            field_name, value = "candidate", stripped.split(":", 1)[1].strip()
        if field_name is not None:
            result[current][field_name] = value
    return result


def _is_none_version(value: str) -> bool:
    return (value or "").strip().lower() in ("", "(none)", "n/a", "(无)")


def _component_policy_item(component: AiComponent, info: dict | None) -> CheckItem:
    """根据单组件 policy 数据生成逐项结果。"""
    pkg = component.package
    installed = (info or {}).get("installed", "")
    candidate = (info or {}).get("candidate", "")
    name = f"{component.title}（{pkg}）"

    if not _is_none_version(installed):
        return CheckItem(name, "PASS", f"已装 {installed}")
    if not _is_none_version(candidate):
        if component.required:
            return CheckItem(name, "PASS", f"候选 {candidate}（未安装）")
        return CheckItem(name, "PASS", f"候选 {candidate}（未安装，属可选层）")

    # 已装/候选均无
    if not component.required:
        return CheckItem(name, "UNKNOWN", OPTIONAL_MISSING_NOTE.get(pkg, "未安装/无候选，属可选层"))

    # 必选组件：分段完全缺失 → 索引过期 UNKNOWN；分段在但候选 (none) → FAIL
    if info is None:
        return CheckItem(
            name, "UNKNOWN",
            f"{podman.APT_UNKNOWN_LABEL}; {podman.APT_POLICY_UNKNOWN_HINT}",
        )
    return CheckItem(
        name, "FAIL",
        f"{podman.APT_PKG_MISSING_LABEL}（当前软件源无可安装候选）；{podman.APT_PKG_MISSING_HINT}",
    )


def preflight_check(distro_name: str) -> PreflightReport:
    """只读预检：结构项 + 单批 policy 盘点；不 apt update、不写文件。"""
    report = PreflightReport(distro_name=distro_name)
    if not add_structural_checks(report, distro_name, need_apt=True):
        return report

    policy = distro.exec_distro(
        distro_name, podman._apt_argv("apt-cache", "policy", *ALL_PACKAGES)
    )
    if podman._is_apt_network_error(policy.stderr) or podman._is_apt_network_error(policy.stdout):
        report.add(
            "AI 组件候选盘点", "FAIL",
            f"apt-cache policy 网络错误；{podman.APT_NET_ERROR_HINT}",
        )
        return report
    if not policy.ok and not policy.stdout.strip():
        error = policy.stderr.strip() or f"exit={policy.exit_code}"
        report.add("AI 组件候选盘点", "FAIL", f"apt-cache policy 命令失败（{error[:200]}）")
        return report

    parsed = parse_policy_batch(policy.stdout)
    for component in COMPONENTS:
        info = parsed.get(component.package)
        item = _component_policy_item(component, info)
        if not component.required:
            report.mark_optional(item.name)
        report.items.append(item)
    return report


def format_preflight(report: PreflightReport) -> str:
    """格式化为可读文本。"""
    lines = [f"== okw ai preflight：{report.distro_name} =="]
    max_w = max((len(i.name) for i in report.items), default=0)
    any_unknown = any(i.status == "UNKNOWN" for i in report.items)
    any_fail = any(i.status == "FAIL" for i in report.items)
    for it in report.items:
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append("结论：预检全部通过，可执行 okw ai install <name> --yes")
        lines.append("  提示：install 将 apt update 并以 root 安装 OCR 路径（不下载模型、不碰密钥）。")
    else:
        summary = []
        if any_fail:
            summary.append(f"{sum(1 for i in report.items if i.status == 'FAIL')} 项 FAIL")
        if any_unknown:
            summary.append(f"{sum(1 for i in report.items if i.status == 'UNKNOWN')} 项 UNKNOWN")
        lines.append("结论：预检未通过（" + " / ".join(summary) + "）")
        lines.append("  可选层 UNKNOWN 不阻断 OCR；若由 APT 索引过期导致，")
        lines.append("  请在发行版内先手动 sudo apt update 后重跑 preflight。")
    return "\n".join(lines)


# ----------------- tesseract 功能探针（install/verify 共用） -----------------

_VERSION_RE = re.compile(r"tesseract\s+([0-9][0-9A-Za-z.\-]*)")
_LANG_TOKEN_RE = re.compile(r"^[a-z][a-z_]*$")
_LANG_HEADER_WORDS = {"list", "of", "available", "languages"}


def parse_tesseract_version(text: str) -> str:
    """从 ``tesseract --version`` 输出提取版本；失败返回空串。"""
    for line in (text or "").splitlines():
        m = _VERSION_RE.search(line)
        if m:
            return m.group(1)
    return ""


def parse_tesseract_langs(text: str) -> set:
    """从 ``tesseract --list-langs`` 输出提取语言代码集合。

    语言列表可能在 stdout，表头在 stderr；合并扫描形如 ``eng``/``chi_sim`` 的行。
    """
    langs: set = set()
    for line in (text or "").splitlines():
        token = line.strip().lower()
        if _LANG_TOKEN_RE.match(token) and token not in _LANG_HEADER_WORDS:
            langs.add(token)
    return langs


def add_tesseract_checks(report, distro_name: str, user: str | None = None) -> None:
    """tesseract 版本 + 语言列表（chi_sim/eng）只读检查写入报告。"""
    version_res = distro.exec_distro(distro_name, ["tesseract", "--version"], user=user)
    version = parse_tesseract_version("\n".join((version_res.stdout, version_res.stderr)))
    if not version_res.ok or not version:
        error = version_res.stderr.strip() or f"exit={version_res.exit_code}"
        report.add(
            "tesseract 版本", "FAIL",
            f"无法执行 tesseract --version：{error}；{OCR_INSTALL_HINT}",
        )
    else:
        report.add("tesseract 版本", "PASS", f"tesseract {version}")

    langs_res = distro.exec_distro(distro_name, ["tesseract", "--list-langs"], user=user)
    langs = parse_tesseract_langs("\n".join((langs_res.stdout, langs_res.stderr)))
    missing = [lang for lang in OCR_LANGS if lang not in langs]
    if not langs_res.ok and not langs:
        error = langs_res.stderr.strip() or f"exit={langs_res.exit_code}"
        report.add("tesseract 语言包", "FAIL", f"读取语言列表失败：{error}；{OCR_INSTALL_HINT}")
    elif missing:
        report.add(
            "tesseract 语言包", "FAIL",
            f"缺少语言 {', '.join(missing)}（需 {OCR_LANG_SPEC}）；{OCR_INSTALL_HINT}",
        )
    else:
        report.add("tesseract 语言包", "PASS", f"可用语言含 {OCR_LANG_SPEC}")


# ----------------- 安装 -----------------

YES_SIDEEFFECTS_LINES = (
    "(1/3) 以 root 执行 apt update，刷新 APT 索引；",
    "(2/3) 以 root 执行 apt install -y --no-install-recommends libkylin-ai-base-dev，"
    "由 APT 解析 OCR 运行库、tesseract 与 chi_sim/eng 语言包；",
    "(3/3) 以默认用户只读验收 OCR（tesseract 版本与语言列表）。",
)


def _run_apt_update(name: str, report: InstallReport) -> bool:
    """root apt update；成功返回 True，失败写入报告并返回 False。"""
    update = distro.exec_distro(
        name, podman._apt_argv("apt", "update"),
        user="root", timeout=podman.APT_MUTATING_TIMEOUT,
    )
    output = "\n".join(part for part in (update.stdout, update.stderr) if part)
    lowered = output.lower()
    fetch_warning = any(
        marker in lowered
        for marker in (
            "failed to fetch",
            "some index files failed to download",
            "err:",
            "无法下载",
            "部分索引文件下载失败",
        )
    )
    hash_error = (
        "hash sum mismatch" in lowered
        or "hashes of expected file" in lowered
        or "哈希校验和不符" in output
    )
    if not update.ok or fetch_warning or hash_error:
        _stage, detail = podman._classify_apt_install_error(output, "apt update", phase="update")
        if update.ok and podman.APT_NET_ERROR_LABEL not in detail and podman.APT_HASH_ERROR_LABEL not in detail:
            detail = (
                "apt update 返回成功但索引下载不完整；请检查发行版网络、DNS 与官方软件源"
                + (f"（{output.strip()[:200]}）" if output.strip() else "")
            )
        report.add("apt update", "FAIL", detail)
        return False
    report.add("apt update", "PASS")
    return True


def install_run(name: str, yes: bool) -> InstallReport:
    """执行 install 主流程；无 --yes 仅返回缺失确认报告（零写入）。"""
    report = InstallReport(distro_name=name)
    if not yes:
        report.missing_yes = True
        return report

    # 结构性失败必须先停止；包候选可因旧索引暂缺，安装刷新后复查。
    pre = PreflightReport(distro_name=name)
    if not add_structural_checks(pre, name, need_apt=True):
        for item in pre.items:
            report.items.append(item)
        return report

    if not _run_apt_update(name, report):
        return report

    # 复查直接包候选
    policy = distro.exec_distro(
        name, podman._apt_argv("apt-cache", "policy", *DIRECT_PACKAGES)
    )
    status, detail = podman._classify_apt_policy_result(policy, DIRECT_PACKAGES[0])
    if status != "PASS":
        report.add("候选复查 libkylin-ai-base-dev", status, detail)
        return report
    report.add("候选复查 libkylin-ai-base-dev", "PASS", detail)

    install_cmd = podman._apt_argv(
        "apt", "install", "-y", "--no-install-recommends", *DIRECT_PACKAGES
    )
    installed = distro.exec_distro(
        name, install_cmd, user="root", timeout=podman.APT_MUTATING_TIMEOUT
    )
    if not installed.ok:
        _stage, detail = podman._classify_apt_install_error(
            installed.stderr, DIRECT_PACKAGES[0]
        )
        report.add("apt install libkylin-ai-base-dev", "FAIL", detail)
        return report
    report.add(
        "apt install libkylin-ai-base-dev", "PASS",
        "已安装直接包及 APT 解析的 OCR 依赖",
    )

    # 事后只读 OCR 子集验收（默认用户；OCR 任意用户可用）
    add_tesseract_checks(report, name)
    return report


def format_install(report: InstallReport) -> str:
    """格式化安装报告。"""
    lines = [f"== okw ai install：{report.distro_name} =="]
    if report.missing_yes:
        lines.append("未提供 --yes，为避免以下副作用，任何写入操作均未执行：")
        lines.extend(f"  {line}" for line in YES_SIDEEFFECTS_LINES)
        lines.append("")
        lines.append("凭据红线：okw 不配置 API Key/Token、不下载模型、不安装 ollama。")
        lines.append("请确认副作用可接受后，重跑：okw ai install <发行版> --yes")
        return "\n".join(lines)

    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append("结论：OCR 路径安装并验收通过，可执行 okw ai verify <name> 查看完整分层盘点")
    else:
        lines.append(f"结论：安装未通过（{sum(1 for i in report.items if i.status == 'FAIL')} 项 FAIL）")
        lines.append("  请按 FAIL 项修复后重试；本流程不宣称事务回滚，")
        lines.append("  apt update 或部分包安装可能已部分生效。")
    return "\n".join(lines)


# ----------------- 验收（只读；冒烟仅本地图片，离线） -----------------

def parse_dpkg_show(stdout: str) -> dict:
    """解析 ``dpkg-query -s <pkgs>``（--status）多包输出。

    输出按空行分块，每块含固定标签 ``Package:``/``Status:``/``Version:``
    （命令本身不含 ``$``、``|``、引号等 shell 元字符，可直接 argv 透传，
    规避 WSL 命令行桥接的元字符展开问题）。返回
    ``{package: {"installed": bool, "version": str}}``；仅
    ``Status: install ok installed`` 视为已装；未安装包不出现在 stdout。
    """
    result: dict = {}
    for block in re.split(r"\n\s*\n", stdout or ""):
        pkg = status = None
        version = ""
        for line in block.splitlines():
            if line.startswith("Package:"):
                pkg = line.split(":", 1)[1].strip()
            elif line.startswith("Status:"):
                status = line.split(":", 1)[1].strip()
            elif line.startswith("Version:"):
                version = line.split(":", 1)[1].strip()
        if pkg:
            installed = status == "install ok installed"
            result[pkg] = {
                "installed": installed,
                "version": version if installed else "",
            }
    return result


def verify_run(distro_name: str, smoke_ocr: str | None = None) -> VerifyReport:
    """只读验收 OCR 路径并盘点可选层；默认不识别，--smoke-ocr 对本地图片离线识别。"""
    report = VerifyReport(distro_name=distro_name, smoke_image=smoke_ocr)
    if not add_structural_checks(report, distro_name, need_apt=False):
        return report

    # dpkg-query -s：无 shell 元字符，直接 argv 透传；未知包走 stderr 且 exit 1
    dpkg = distro.exec_distro(distro_name, ["dpkg-query", "-s", *ALL_PACKAGES])
    pkg_map = parse_dpkg_show(dpkg.stdout) if dpkg.stdout else {}

    # 必选：Gen1 SDK / 运行库已装
    for pkg in ("libkylin-ai-base-dev", "libkylin-ai-base2"):
        info = pkg_map.get(pkg)
        title = _BY_PACKAGE[pkg].title + f"（{pkg}）"
        if info and info["installed"]:
            report.add(title, "PASS", f"已装 {info['version']}")
        else:
            report.add(title, "FAIL", f"未安装；{OCR_INSTALL_HINT}")

    # 必选：tesseract 功能与语言（权威，覆盖 tesseract-ocr/语言包）
    add_tesseract_checks(report, distro_name)

    # 可选层盘点（仅信息展示，不阻断 OCR 门控）
    for component in COMPONENTS:
        if component.required:
            continue
        pkg = component.package
        info = pkg_map.get(pkg)
        title = f"{component.title}（{pkg}）"
        report.mark_optional(title)
        if info and info["installed"]:
            report.add(title, "PASS", f"已装 {info['version']}")
        else:
            report.add(title, "UNKNOWN", OPTIONAL_MISSING_NOTE.get(pkg, "未安装，属可选层"))

    # 可选：本地图片 OCR 冒烟（离线）
    if smoke_ocr is not None:
        if any(i.status == "FAIL" for i in report.items):
            report.add("OCR 冒烟", "FAIL", "前置检查存在 FAIL，未执行图片识别")
            return report
        distro_path = to_distro_image_path(smoke_ocr)
        exists = distro.exec_distro(distro_name, ["test", "-f", distro_path])
        if not exists.ok:
            report.add(
                "OCR 冒烟", "FAIL",
                f"发行版内找不到图片 {distro_path}（请确认路径在发行版内可访问）",
            )
            return report
        run = distro.exec_distro(
            distro_name,
            ["tesseract", distro_path, "stdout", "-l", OCR_LANG_SPEC],
        )
        if run.ok and run.stdout.strip():
            report.add(
                "OCR 冒烟", "PASS",
                f"本地图片离线识别成功（{OCR_LANG_SPEC}，识别 {len(run.stdout.strip())} 字符）",
            )
        else:
            error = run.stderr.strip() or f"exit={run.exit_code}"
            report.add("OCR 冒烟", "FAIL", f"识别失败或结果为空：{error[:200]}")

    return report


def format_verify(report: VerifyReport) -> str:
    """格式化验收报告。"""
    lines = [f"== okw ai verify：{report.distro_name} =="]
    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    smoke = report.smoke_image
    if report.all_passed():
        if smoke is not None:
            lines.append("结论：OCR 验收与本地图片离线识别冒烟全部通过")
        else:
            lines.append("结论：OCR 验收通过（默认只读，未执行图片识别）")
            lines.append("  如需冒烟：okw ai verify <name> --smoke-ocr <发行版内图片路径>")
    else:
        fail_count = sum(1 for i in report.items if i.status == "FAIL")
        unknown_count = sum(1 for i in report.items if i.status == "UNKNOWN")
        summary = []
        if fail_count:
            summary.append(f"{fail_count} 项 FAIL")
        if unknown_count:
            summary.append(f"{unknown_count} 项 UNKNOWN")
        lines.append("结论：验收未通过（" + " / ".join(summary) + "）")
        lines.append("  本命令只读、离线；可选层 UNKNOWN 不阻断 OCR，okw 不下载模型。")
    return "\n".join(lines)
