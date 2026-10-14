"""okw ai 子命令：预检、安装和验收 openKylin WSL 内的 AI 栈。

本期只落地**唯一已落机验证的 Gen1 SDK / OCR 路径**（见知识库
references/ai-sdk-ocr-poc.md）：安装直接包 ``libkylin-ai-base-dev``，由 APT
解析 OCR 运行库、tesseract 与语言包。Gen2 全栈、模型下载、ollama 等仅只读盘点。

零第三方依赖：WSL 调用经 okw.distro；APT 的 C locale argv、长超时与网络/哈希/
缺包分类复用 okw.podman；Windows→发行版路径转换复用 okw.image。

组件清单的知识边界（与上游 ``kylin-ai-subsystem`` 仓学习结论一致）：

- 盘点对象是 openKylin 3（huanghe）软件源可探测的 **deb 包**，包名经本机
  dpkg/apt 核验（见 references/ai-subsystem-source-architecture.md §3）；
- 上游 ``kylin-ai-subsystem`` 仓 ``openkylin/nile-sp2`` 分支的 ``repos.md``
  （47 项，引擎/协议/SDK/厂商插件四层）是**下一代源码总装图**：源码仓名不
  等于 deb 包名，不作为安装/盘点对象，仅在报告脚注给出处；
- ``COMPONENTS`` 是清单的**单一事实源**（镜像 build-deploy.sh 的 manifest
  纪律）：组件即数据，携带 layer（分层）/required（门控边界）/missing_note
  （缺失措辞）；顺序即 policy/dpkg 探测与报告分组顺序，OCR 门控层在最前。
"""

import re
from dataclasses import dataclass

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

# ----------------- 分层组件清单（单一事实源） -----------------
#
# 层级模型（来源：kylin-ai-subsystem README 四层划分 + huanghe debian/control
# 全栈清单 + 本机 dpkg/apt 核验）：
#   ocr      已验证 OCR 路径（Gen1，唯一门控层；本地 tesseract CPU 离线）
#   engine   引擎与子系统层（Gen2 服务端/引擎插件/模型配置）
#   sdk      Gen2 SDK 客户端层（全部是 IPC/D-Bus 薄代理，桌面镜像常预装）
#   infer    推理底座与知识服务（Triton/RAG，okw 不启动服务、不下载模型）
#   external 外部组件（不在 openKylin 官方源）
LAYER_OCR = "ocr"
LAYER_ENGINE = "engine"
LAYER_SDK = "sdk"
LAYER_INFER = "infer"
LAYER_EXTERNAL = "external"

LAYER_ORDER = (LAYER_OCR, LAYER_ENGINE, LAYER_SDK, LAYER_INFER, LAYER_EXTERNAL)

LAYER_TITLES = {
    LAYER_OCR: "已验证 OCR 路径（门控项；本地 tesseract CPU 离线）",
    LAYER_ENGINE: "引擎与子系统层（可选；Gen2 服务端/插件，仅只读盘点）",
    LAYER_SDK: "Gen2 SDK 客户端层（可选；IPC 薄代理，不含推理）",
    LAYER_INFER: "推理底座与知识服务（可选；okw 不启动服务、不下载模型）",
    LAYER_EXTERNAL: "外部组件（可选；不在 openKylin 官方源）",
}


@dataclass(frozen=True)
class AiComponent:
    """AI 栈分层组件（不可变）。

    required=True 表示属于已验证 OCR 路径，缺失影响安装/验收门控；
    required=False 为可选层，缺失仅 UNKNOWN 不阻断。missing_note 是该
    可选组件缺失时的角色说明（okw 不自动安装/不下载模型的边界内联在清单上）。
    """

    key: str
    package: str
    title: str
    layer: str
    required: bool = False
    missing_note: str = ""

    def __repr__(self) -> str:
        return (
            f"AiComponent(key={self.key!r}, package={self.package!r}, "
            f"layer={self.layer!r}, required={self.required})"
        )


# 分层组件清单：顺序即探测/报告顺序；OCR 层须在最前（其前两包同时是
# install 候选复查与批量 policy 调用的锚点包）。
COMPONENTS = (
    # ---- OCR 已验证路径（门控） ----
    AiComponent("gen1-sdk", "libkylin-ai-base-dev", "Gen1 SDK 开发包（OCR 安装目标）", LAYER_OCR, True),
    AiComponent("gen1-runtime", "libkylin-ai-base2", "Gen1 SDK 运行库", LAYER_OCR, True),
    AiComponent("ocr-engine", "tesseract-ocr", "OCR 引擎 tesseract", LAYER_OCR, True),
    AiComponent("ocr-lang-chi", "tesseract-ocr-chi-sim", "tesseract 中文语言包", LAYER_OCR, True),
    AiComponent("ocr-lang-eng", "tesseract-ocr-eng", "tesseract 英文语言包", LAYER_OCR, True),
    # ---- 引擎与子系统层（可选） ----
    AiComponent(
        "ai-runtime", "kylin-ai-runtime", "Gen2 IPC 服务端（kylin-ai-runtime）", LAYER_ENGINE,
        missing_note="未安装；Gen2 D-Bus 服务端载体，由客户端首调按需对接，okw 不启动服务、不自动安装",
    ),
    AiComponent(
        "subsystem-meta", "kylin-ai-subsystem", "Gen2 全栈元包（一条 Depends 拉齐全栈）", LAYER_ENGINE,
        missing_note="未安装；Gen2 全栈元包端到端未验证、下载量大，okw 不自动安装、不下载模型",
    ),
    AiComponent(
        "subsystem-plugin", "kylin-ai-subsystem-plugin", "子系统插件管理组件", LAYER_ENGINE,
        missing_note="未安装；Gen2 子系统插件管理组件，okw 不自动安装",
    ),
    AiComponent(
        "subsystem-modelconfig", "kylin-ai-subsystem-modelconfig", "模型配置后端（modelconfig）", LAYER_ENGINE,
        missing_note="未安装；模型配置服务（对应 gsettings model-config 后端），okw 不自动安装、不下载模型",
    ),
    AiComponent(
        "engine-plugins", "kylin-ai-engine-plugins", "引擎插件集合（AbstractAiEngine 框架）", LAYER_ENGINE,
        missing_note="未安装；Gen2 引擎插件端到端未验证，okw 不自动安装、不下载模型",
    ),
    AiComponent(
        "ondevice-nlp", "kylin-ondevice-nlp-engine", "本地 NLP 引擎插件（Triton 客户端）", LAYER_ENGINE,
        missing_note="未安装；本地 NLP 还需 kytensor 与自备 GGUF，okw 不自动安装",
    ),
    AiComponent(
        "model-manager", "kylin-ai-model-manager", "麒麟模型管理工具（上游自述不完善）", LAYER_ENGINE,
        missing_note="未安装；如需可在发行版内手动 sudo apt install kylin-ai-model-manager，okw 不默认安装",
    ),
    # ---- Gen2 SDK 客户端层（可选；IPC 薄代理） ----
    AiComponent(
        "kysdk-common", "libkysdk-ai-common", "Gen2 公共库（枚举/错误码/宏）", LAYER_SDK,
        missing_note="未安装；Gen2 IPC 公共库，随客户端链路使用，okw 不自动安装",
    ),
    AiComponent(
        "gen2-nlp", "libkysdk-genai-nlp0", "Gen2 文本生成客户端（IPC 薄代理）", LAYER_SDK,
        missing_note="未安装；Gen2 客户端为 IPC 薄代理，还需引擎插件与模型，okw 不自动安装",
    ),
    AiComponent(
        "gen2-vision", "libkysdk-genai-vision0", "Gen2 图像生成客户端（IPC 薄代理）", LAYER_SDK,
        missing_note="未安装；Gen2 图像生成代理还需引擎插件与模型，okw 不自动安装",
    ),
    AiComponent(
        "coreai-speech", "libkysdk-coreai-speech0", "Gen2 语音客户端（IPC 薄代理）", LAYER_SDK,
        missing_note="未安装；Gen2 语音代理还需云端/本地语音引擎，okw 不自动安装",
    ),
    AiComponent(
        "coreai-vision", "libkysdk-coreai-vision0", "Gen2 视觉客户端（含 OCR，IPC 薄代理）", LAYER_SDK,
        missing_note="未安装；Gen2 视觉代理还需引擎侧支持，okw 不自动安装",
    ),
    AiComponent(
        "advanced-ai", "libkysdk-advanced-ai0", "Gen2 高级能力聚合库", LAYER_SDK,
        missing_note="未安装；Gen2 高级能力聚合库，okw 不自动安装",
    ),
    AiComponent(
        "kysdk-mcp", "libkysdk-mcp", "Gen2 MCP 客户端/服务端共享库（仅库级底座）", LAYER_SDK,
        missing_note="未安装；仅 MCP client/server 库级底座，openKylin 3 无随附 MCP 服务或技能市场，okw 不自动安装",
    ),
    AiComponent(
        "kyai-assistant", "libkyai-assistant0", "Gen2 助手业务库", LAYER_SDK,
        missing_note="未安装；Gen2 助手业务库，okw 不自动安装",
    ),
    AiComponent(
        "kyai-config", "libkyai-config0", "Gen2 配置业务库", LAYER_SDK,
        missing_note="未安装；Gen2 配置业务库，okw 不自动安装",
    ),
    # ---- 推理底座与知识服务（可选） ----
    AiComponent(
        "kytensor", "kytensor-server", "Triton 推理服务（kytensor）", LAYER_INFER,
        missing_note="未安装；推理服务与模型仓库需另行准备，okw 不启动服务、不下载模型",
    ),
    AiComponent(
        "business-framework", "libkyai-business-framework", "AI 业务编排框架库", LAYER_INFER,
        missing_note="未安装；AI 业务编排框架库，随文档问答全栈使用，okw 不自动安装",
    ),
    AiComponent(
        "document-qa", "libkylin-ai-document-qa-service", "文档问答/RAG 服务", LAYER_INFER,
        missing_note="未安装；文档问答还需向量引擎与文档服务配合，okw 不自动安装、不下载模型",
    ),
    AiComponent(
        "vector-client", "libkysdk-vector-engine-client", "向量引擎客户端库", LAYER_INFER,
        missing_note="未安装；向量引擎客户端库，需向量引擎服务端，okw 不自动安装",
    ),
    AiComponent(
        "vector-engine", "kylin-ai-vector-engine", "向量引擎服务", LAYER_INFER,
        missing_note="未安装；文档问答/RAG 的向量引擎服务端，okw 不自动安装、不下载模型",
    ),
    AiComponent(
        "data-management-client", "libkyai-data-management-client", "数据管理客户端库", LAYER_INFER,
        missing_note="未安装；数据管理客户端库，需数据管理服务端，okw 不自动安装",
    ),
    # ---- 外部（非官方源） ----
    AiComponent(
        "ollama", "ollama", "ollama（外部模型运行时）", LAYER_EXTERNAL,
        missing_note="不在 openKylin 官方源；需官方 install.sh，okw 不执行 curl|sh、不自动安装",
    ),
)

ALL_PACKAGES = tuple(c.package for c in COMPONENTS)
_BY_PACKAGE = {c.package: c for c in COMPONENTS}

# 唯一已落机验证的直接包（POC 实测命令：
# apt-get install -y --no-install-recommends libkylin-ai-base-dev）
DIRECT_PACKAGES = ("libkylin-ai-base-dev",)

# verify 中以 dpkg-query 门控的 OCR 包；tesseract 三项以功能探针为权威
_OCR_DPKG_GATE = frozenset(("libkylin-ai-base-dev", "libkylin-ai-base2"))

# OCR 本地识别固定语言与引擎参数（离线、CPU）
OCR_LANGS = ("chi_sim", "eng")
OCR_LANG_SPEC = "+".join(OCR_LANGS)

OCR_INSTALL_HINT = "请先执行 okw ai install <发行版> --yes 完成 OCR 路径安装后重跑"

# 报告脚注：上游源码总装图与 deb 盘点的世代边界（一次成文，两处报告复用）
UPSTREAM_SOURCE_FOOTER = (
    "上游参照：kylin-ai-subsystem 仓 openkylin/nile-sp2 的 repos.md 是 47 项四层源码总装图"
    "（引擎/协议/SDK/厂商插件）；本清单仅盘点 openKylin 3 huanghe 源可探测的 deb 包，"
    "源码仓≠deb 包；分层说明见 okw ref ai-stack。"
)


def _display_name(component: AiComponent) -> str:
    """报告中的组件统一显示名：中文角色（deb 包名）。"""
    return f"{component.title}（{component.package}）"


# 全部组件项的显示名：渲染时据此区分「组件项」与结构/探针/冒烟项
_COMPONENT_NAMES = frozenset(_display_name(c) for c in COMPONENTS)


class _OptionalGating:
    """可选层 UNKNOWN 不参与门控的共用逻辑（preflight/verify 报告混入）。

    门控口径：必选项全 PASS → 0；任一必选 FAIL → 1；必选仅 UNKNOWN → 2。
    可选组件经 add_component_item 登记后自动标为非门控。
    """

    def _gating_init(self) -> None:
        self.optional_names: set[str] = set()
        # (layer, CheckItem)：渲染层分组的唯一登记处，与 items 中的对象同一身份
        self.component_layers: list[tuple[str, CheckItem]] = []

    def mark_optional(self, name: str) -> None:
        self.optional_names.add(name)

    def add_component_item(self, component: AiComponent, item: CheckItem) -> None:
        """登记组件检查项：入 items、记层；可选组件同时标记不参与门控。"""
        self.items.append(item)
        self.component_layers.append((component.layer, item))
        if not component.required:
            self.optional_names.add(item.name)

    def _gating_items(self) -> list[CheckItem]:
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


class AiPreflightReport(_OptionalGating, podman.PreflightReport):
    """preflight 报告：可选层 UNKNOWN 仅信息展示，不参与门控退出码。"""

    def __init__(self, distro_name: str):
        super().__init__(distro_name=distro_name)
        self._gating_init()


class AiVerifyReport(_OptionalGating, podman.VerifyReport):
    """verify 报告：OCR 必选项决定门控，可选层 UNKNOWN 不阻断。"""

    def __init__(self, distro_name: str, smoke_image=None):
        super().__init__(distro_name=distro_name, smoke_image=smoke_image)
        self._gating_init()


# 别名便于 handler 引用
PreflightReport = AiPreflightReport
VerifyReport = AiVerifyReport

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
    name = _display_name(component)

    if not _is_none_version(installed):
        return CheckItem(name, "PASS", f"已装 {installed}")
    if not _is_none_version(candidate):
        if component.required:
            return CheckItem(name, "PASS", f"候选 {candidate}（未安装）")
        return CheckItem(name, "PASS", f"候选 {candidate}（未安装，属可选层）")

    # 已装/候选均无
    if not component.required:
        return CheckItem(name, "UNKNOWN", component.missing_note or "未安装/无候选，属可选层")

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
        report.add_component_item(
            component, _component_policy_item(component, parsed.get(component.package))
        )
    return report


# ----------------- 分层渲染（preflight/verify 共用） -----------------

_PROBE_ITEM_NAMES = ("tesseract 版本", "tesseract 语言包")
_SMOKE_ITEM_NAME = "OCR 冒烟"
_STRUCTURE_SECTION_TITLE = "结构检查"
_BATCH_SECTION_TITLE = "组件批量盘点"
_SMOKE_SECTION_TITLE = "本地图片 OCR 冒烟（离线）"


def _emit_section(lines: list[str], title: str, items: list[CheckItem]) -> None:
    """按统一缩进追加一个分组；空组跳过。"""
    if not items:
        return
    lines.append(f"[{title}]")
    width = max((len(i.name) for i in items), default=0)
    for it in items:
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{width}}  {it.detail}".rstrip())


def _render_layered_sections(report, *, with_probes: bool) -> list[str]:
    """把报告项渲染为「结构 → 各层（OCR 层含 tesseract 探针）→ 冒烟」分组。"""
    lines: list[str] = []
    _emit_section(
        lines, _STRUCTURE_SECTION_TITLE,
        [i for i in report.items if i.name in STRUCTURAL_ITEM_NAMES],
    )

    # 组件项已按 component_layers 分层渲染；其余（结构/探针/失败占位）入 leftovers
    leftovers = [
        i for i in report.items
        if i.name not in _COMPONENT_NAMES
        and i.name not in STRUCTURAL_ITEM_NAMES
        and i.name not in _PROBE_ITEM_NAMES
        and i.name != _SMOKE_ITEM_NAME
    ]
    _emit_section(lines, _BATCH_SECTION_TITLE, leftovers)

    probes = [i for i in report.items if i.name in _PROBE_ITEM_NAMES]
    for layer in LAYER_ORDER:
        items = [item for ly, item in report.component_layers if ly == layer]
        if layer == LAYER_OCR and with_probes:
            # tesseract 版本/语言探针是 OCR 门控的权威功能项，与包项同组
            items = items + probes
        _emit_section(lines, LAYER_TITLES[layer], items)

    if with_probes:
        _emit_section(lines, _SMOKE_SECTION_TITLE, [i for i in report.items if i.name == _SMOKE_ITEM_NAME])
    return lines


def format_preflight(report: PreflightReport) -> str:
    """格式化为可读文本。"""
    lines = [f"== okw ai preflight：{report.distro_name} =="]
    lines.extend(_render_layered_sections(report, with_probes=False))
    lines.append("")
    if report.all_passed():
        lines.append("结论：预检全部通过，可执行 okw ai install <name> --yes")
        lines.append("  提示：install 将 apt update 并以 root 安装 OCR 路径（不下载模型、不碰密钥）。")
    else:
        summary = []
        if any(i.status == "FAIL" for i in report.items):
            summary.append(f"{sum(1 for i in report.items if i.status == 'FAIL')} 项 FAIL")
        if any(i.status == "UNKNOWN" for i in report.items):
            summary.append(f"{sum(1 for i in report.items if i.status == 'UNKNOWN')} 项 UNKNOWN")
        lines.append("结论：预检未通过（" + " / ".join(summary) + "）")
        lines.append("  可选层 UNKNOWN 不阻断 OCR；若由 APT 索引过期导致，")
        lines.append("  请在发行版内先手动 sudo apt update 后重跑 preflight。")
    if report.component_layers:
        lines.append(UPSTREAM_SOURCE_FOOTER)
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

    # 必选：Gen1 SDK / 运行库已装（tesseract 三项以下方功能探针为权威）
    for component in COMPONENTS:
        if not component.required or component.package not in _OCR_DPKG_GATE:
            continue
        info = pkg_map.get(component.package)
        if info and info["installed"]:
            item = CheckItem(_display_name(component), "PASS", f"已装 {info['version']}")
        else:
            item = CheckItem(_display_name(component), "FAIL", f"未安装；{OCR_INSTALL_HINT}")
        report.add_component_item(component, item)

    # 必选：tesseract 功能与语言（权威，覆盖 tesseract-ocr/语言包）
    add_tesseract_checks(report, distro_name)

    # 可选层盘点（仅信息展示，不阻断 OCR 门控）
    for component in COMPONENTS:
        if component.required:
            continue
        pkg = component.package
        info = pkg_map.get(pkg)
        if info and info["installed"]:
            item = CheckItem(_display_name(component), "PASS", f"已装 {info['version']}")
        else:
            item = CheckItem(
                _display_name(component), "UNKNOWN",
                component.missing_note or "未安装，属可选层",
            )
        report.add_component_item(component, item)

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
    lines.extend(_render_layered_sections(report, with_probes=True))
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
    if report.component_layers:
        lines.append(UPSTREAM_SOURCE_FOOTER)
    return "\n".join(lines)
