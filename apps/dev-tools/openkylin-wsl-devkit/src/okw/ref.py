"""openKylin 知识库快速参考索引。

只读引用 docs/knowledge/tech/openkylin/docs-wiki/，不复制内容、不改变结构。
"""

from dataclasses import dataclass

KB_ROOT = "docs/knowledge/tech/openkylin/docs-wiki"

@dataclass(frozen=True)
class RefTopic:
    name: str
    title: str
    lines: list[str]
    sources: list[str]

_TOPICS: dict[str, RefTopic] = {
    "series": RefTopic(
        name="series",
        title="openKylin 版本与系列代号",
        lines=[
            "双轨版本制：LTS 每 3 年（2+3 维护）、创新版每 1 年（12 个月被动维护）",
            "1.0 = yangtze（长江）",
            "2.0 = nile（尼罗河）LTS，内核 Linux 6.6，2024-08 发布",
            "3.0 = huanghe（黄河）创新版，内核 Linux 7.0，2026-09 发布",
            "changelog 系列代号必须与软件源代号一致（F-015 纪律）",
            "四架构同源：X86 / ARM / RISC-V / LoongArch",
        ],
        sources=[
            f"{KB_ROOT}/concepts/02-release-lifecycle.md",
            f"{KB_ROOT}/concepts/01-platform-and-repository.md",
        ],
    ),
    "wsl-troubleshoot": RefTopic(
        name="wsl-troubleshoot",
        title="WSL 排障（E_UNEXPECTED / E_ABORT 三问）",
        lines=[
            "失败位置是否漂移（镜像位置/导入目录发生变化）→ 固定位置重试",
            "空闲内存是否不足：0.8GB 失败 / 4.5GB 成功（S26 实测）→ wsl --shutdown 后重试",
            "仍失败：把 .wsl（gzip tar，魔数 1F 8B）解压为纯 tar 再 import",
            "稀疏 VHD：wsl --import ... --version 2 后执行 wsl --manage <name> --set-sparse true --allow-unsafe",
            "默认账号 openkylin/openkylin 为弱口令，首次进入立即 passwd",
        ],
        sources=[
            f"{KB_ROOT}/references/wsl-install-sparse-vhd-guide.md",
            f"{KB_ROOT}/references/wsl-dual-image-selection.md",
        ],
    ),
    "okbs": RefTopic(
        name="okbs",
        title="OKBS 编译平台五步流程",
        lines=[
            "1) 注册：https://build.openkylin.top 注册 openKylin ID（先签 CLA：https://cla.openkylin.top）",
            "2) 建 PPA 仓库（对应软件包源码提交目标）",
            "3) 配置 SSH 公钥与 PGP 密钥",
            "4) 配置 ~/.dput.cf：[okbs] fqdn=upload.build.openkylin.top:2121 / method=sftp / incoming=%(okbs)s",
            "5) 上传：dput okbs:~<ID>/ppa <source.changes>，到 archive.build.openkylin.top/dput-logs/ 查结果",
            "前置依赖：sftp 方式需安装 paramiko / dput-ng（见 okw scaffold dput）",
        ],
        sources=[f"{KB_ROOT}/concepts/06-developer-infrastructure.md"],
    ),
    "verify": RefTopic(
        name="verify",
        title="openKylin WSL 五步验收口径",
        lines=[
            "1) 发行版在列且为 WSL2（wsl -l -v，默认星标不被工具改变）",
            "2) /etc/os-release 的 ID=openkylin 与 VERSION",
            "3) 默认用户/UID：user=openkylin uid=1000（弱口令，先 passwd）",
            "4) /etc/wsl.conf：[boot] systemd=true、[user] default=openkylin",
            "5) 软件包计数：dpkg-query -W | wc -l（S26 实测最小镜像约 405 包）",
        ],
        sources=[f"{KB_ROOT}/references/wsl-install-sparse-vhd-guide.md"],
    ),
    "ai-stack": RefTopic(
        name="ai-stack",
        title="openKylin AI 三层体系 + 贡献治理",
        lines=[
            "成文分层：用户使用 / 模型接入配置 / 开发者 SDK，外加贡献治理",
            "用户层：kylin-ai-model-manager（apt，上游自述不完善）、ollama（不在官方源）跑 DeepSeek-R1、KylinCode",
            "模型接入三类来源：云端 API Key / 局域网端点 / 本地模型包；先确认 AI 子系统版本",
            "Gen1 SDK：libkylin-ai-base-dev（手册 8 能力域；OCR 已实测，其余多为 D-Bus 代理）",
            "Gen2 SDK：libkysdk-* 全 IPC 薄代理；客户端预装但引擎插件/模型缺省",
            "OCR 实测：本地 tesseract 5.3.4（chi_sim+eng）CPU 离线，精度中等、有形近误识",
            "红线：API Key/Token 禁入仓库、禁传外部 AI；okw 不配置密钥、不下载模型、不装 ollama",
        ],
        sources=[
            f"{KB_ROOT}/concepts/05-ai-stack.md",
            f"{KB_ROOT}/references/ai-sdk-ocr-poc.md",
            f"{KB_ROOT}/references/ai-subsystem-source-architecture.md",
        ],
    ),
}

def list_topics() -> list[str]:
    return sorted(_TOPICS)

def get_topic(name: str) -> RefTopic | None:
    return _TOPICS.get(name)

def format_topic(topic: RefTopic) -> str:
    lines = [f"== {topic.title} =="]
    lines.extend(f"  - {ln}" for ln in topic.lines)
    lines.append("  来源：")
    lines.extend(f"    - {s}" for s in topic.sources)
    return "\n".join(lines)
