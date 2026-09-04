# -*- coding: utf-8 -*-
"""批次 1：00/01 分类新束迁移（9 个新束）。

新束：
  A  zhexue/methodology/first-principles（嵌套 concepts）
  B  jishu/comm/ffi、jishu/comm/idl、jishu/comm/tvm-ffi、jishu/comm/interface-api-abi（flat）
     jishu/ai/jira-skill（保留 concepts/examples/references）
     meta/okf-desktop（flat）
     jishu/ai/ai-agent/agent-interface（flat）
     jishu/ai/ai-agent/agent-runtime-protocol（flat + references html）
     jishu/ai/ai-agent/agent-communication-protocols（flat + 散文件并入）
不执行 git 操作。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from migrate_lib import (
    LEARNING, BUNDLES, MIGRATION_DATE,
    should_skip, transform_md, write_doc, clean_body,
    split_frontmatter, parse_fm, build_frontmatter,
    gen_dir_index, gen_bundle_root_index, gen_log_md,
    list_content_files,
)

STATS = {"files": 0, "skipped": 0}


def migrate_file(src: Path, dst: Path, rel_source: str, doc_type: str = "Concept"):
    content = transform_md(src, rel_source, doc_type)
    write_doc(dst, content)
    STATS["files"] += 1


def rel_to_learning(p: Path) -> str:
    return str(p.relative_to(LEARNING)).replace("\\", "/")


def migrate_flat_bundle(src_dir: Path, dst_dir: Path, *,
                        title: str, description: str, overview: str,
                        extra_refs: list[tuple[Path, str]] = (),
                        extra_concepts: list[tuple[Path, str, str]] = (),
                        merge_lines: list[str] | None = None,
                        skip_files: set[str] = frozenset()):
    """flat 束：源目录全部章节 md → concepts/；html/toml 由 extra_refs 指定。"""
    concepts = dst_dir / "concepts"
    concepts.mkdir(parents=True, exist_ok=True)
    entries = []
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and f.suffix == ".md" and f.name != "index.md" and not should_skip(f):
            if f.name in skip_files:
                continue
            migrate_file(f, concepts / f.name, rel_to_learning(f))
            entries.append(f.stem)
    for src, dst_name, src_rel in extra_concepts:
        content = transform_md(src, src_rel)
        write_doc(concepts / dst_name, content)
        entries.append(Path(dst_name).stem)
        STATS["files"] += 1
    # concepts/index.md
    lines = ["# 概念文档", ""]
    for f in sorted(concepts.iterdir()):
        if f.suffix == ".md" and f.name != "index.md":
            lines.append(f"* [{f.stem}]({f.name})")
    lines += ["", "```{toctree}", ":maxdepth: 2", ""]
    lines += sorted(e for e in {f.stem for f in concepts.iterdir() if f.suffix == '.md' and f.name != 'index.md'})
    lines += ["```", ""]
    write_doc(concepts / "index.md", "\n".join(lines))

    refs_dir = None
    if extra_refs:
        refs_dir = dst_dir / "references"
        refs_dir.mkdir(exist_ok=True)
        for src, name in extra_refs:
            (refs_dir / name).write_bytes(Path(src).read_bytes())

    nav = [("concepts/", "concepts/index.md", "概念文档")]
    toctree = ["concepts/index"]
    root = gen_bundle_root_index(title, description, overview, nav, toctree + ["log"])
    write_doc(dst_dir / "index.md", root)
    write_doc(dst_dir / "log.md", gen_log_md(merge_lines))
    print(f"[bundle] {dst_dir.relative_to(BUNDLES)}: {STATS['files']} files so far")


def main():
    L01 = LEARNING / "01-agent-protocols-interfaces"
    L00 = LEARNING / "00-essence-and-thinking"

    # ---------- A. zhexue/methodology/first-principles ----------
    src = L00 / "first-principles"
    dst = BUNDLES / "zhexue" / "methodology" / "first-principles"
    concepts = dst / "concepts"
    concepts.mkdir(parents=True, exist_ok=True)

    # 根级章节 → concepts/
    root_files = []
    for f in sorted(src.iterdir()):
        if f.is_file() and f.suffix == ".md" and f.name != "index.md" and not should_skip(f):
            migrate_file(f, concepts / f.name, rel_to_learning(f))
            root_files.append(f.stem)
    # 三个子目录 → concepts/ 下同名子目录
    subdir_map = {
        "15-cross-domain-cases": "cross-domain-cases",
        "chinese-philosophy-parallels": "chinese-philosophy-parallels",
        "exercises": "exercises",
    }
    for s, d in subdir_map.items():
        sd = src / s
        td = concepts / d
        td.mkdir(exist_ok=True)
        for f in sorted(sd.iterdir()):
            if f.is_file() and f.suffix == ".md" and f.name != "index.md" and not should_skip(f):
                migrate_file(f, td / f.name, rel_to_learning(f))
        write_doc(td / "index.md", gen_dir_index(td, {
            "cross-domain-cases": "跨学科案例",
            "chinese-philosophy-parallels": "中国哲学对照",
            "exercises": "练习手册",
        }[d]))
    # 非 md 资源 → references/
    refs = dst / "references"
    refs.mkdir(exist_ok=True)
    (refs / "12-knowledge-graph.html").write_bytes((src / "12-knowledge-graph.html").read_bytes())
    (refs / "knowledge-graph-config.toml").write_bytes((src / "knowledge-graph-config.toml").read_bytes())

    # concepts/index.md
    cfiles = sorted(f.stem for f in concepts.iterdir() if f.is_file() and f.suffix == ".md" and f.name != "index.md")
    csubs = sorted(d for d in subdir_map.values())
    lines = ["# 概念文档", "", "## 主体章节", ""]
    for s in cfiles:
        lines.append(f"* [{s}]({s}.md)")
    lines += ["", "## 专题子目录", ""]
    for d in csubs:
        lines.append(f"* [{d}/]({d}/index.md)")
    lines += ["", "```{toctree}", ":maxdepth: 2", ""]
    lines += cfiles + [f"{d}/index" for d in csubs]
    lines += ["```", ""]
    write_doc(concepts / "index.md", "\n".join(lines))

    root_idx = gen_bundle_root_index(
        "第一性原理（First Principles）",
        "第一性原理思维方法的系统化知识档案——哲学起源、物理学应用、商业创新案例、方法论框架、认知科学基础、AI 时代应用与跨学科案例，采用对抗性审查机制与四级可信度评级，核心论据可追溯、可验证。",
        "本束覆盖 7 大知识领域，累计引用 100+ 来源：既追溯亚里士多德、笛卡尔、康德等哲学源头，也考察费曼、马斯克等现当代实践者，同时不回避「More is Different」等批评声音与事后归因偏差问题。配套六步练习手册（问题定义→假设识别→分解→质疑→重构→验证）与中国哲学跨文化对照。",
        [("concepts/", "concepts/index.md", "概念文档（主体章节 + 跨学科案例 + 中国哲学对照 + 练习手册）"),
         ("references/", "references/12-knowledge-graph.html", "知识图谱可视化（HTML）与配置（TOML）")],
        ["concepts/index", "log"],
    )
    write_doc(dst / "index.md", root_idx)
    write_doc(dst / "log.md", gen_log_md([
        "* 源：00-essence-and-thinking/first-principles/（51 文件，含 2 非 md 资源随迁 references/）",
        "* 舍弃：README.md/各级 index.md（导航元数据）",
    ]))
    print(f"[bundle] zhexue/methodology/first-principles done")

    # ---------- B1. jishu/comm/ffi ----------
    migrate_flat_bundle(
        L01 / "ffi-wiki", BUNDLES / "jishu" / "comm" / "ffi",
        title="FFI 外部函数接口",
        description="FFI（Foreign Function Interface）跨语言互操作机制系统教程——定义与核心概念、工作原理、各语言实现（Python ctypes/cffi、JNI、P/Invoke、Rust extern、Go cgo）、应用场景、优势局限与 RPC/IPC/序列化等相邻机制对比。",
        overview="",
    )

    # ---------- B2. jishu/comm/idl ----------
    migrate_flat_bundle(
        L01 / "idl-wiki", BUNDLES / "jishu" / "comm" / "idl",
        title="IDL 接口描述语言",
        description="IDL（Interface Definition Language）接口描述语言系统教程——定义与历史、类型系统与接口语法、主流 IDL 规范（CORBA IDL/COM IDL/Protobuf/Thrift/gRPC/GraphQL Schema 等）、横向对比、工具链、应用场景与现代格式（JSON Schema/OpenAPI）关系辨析。",
        overview="",
    )

    # ---------- B3. jishu/comm/tvm-ffi ----------
    migrate_flat_bundle(
        L01 / "tvm-ffi-wiki", BUNDLES / "jishu" / "comm" / "tvm-ffi",
        title="Apache TVM FFI",
        description="Apache TVM FFI 跨语言调用层完整教程——架构总览、C++ 核心 API、类型系统、容器对象、反射机制、序列化、Python 绑定、CUDA 支持、OrcJIT 扩展、DLPack 集成、构建集成、示例与最佳实践。",
        overview="",
    )

    # ---------- B4. jishu/comm/interface-api-abi-protocol ----------
    migrate_flat_bundle(
        L01 / "interface-api-abi-protocol-wiki", BUNDLES / "jishu" / "comm" / "interface-api-abi",
        title="接口·API·ABI·协议",
        description="接口（Interface）、API、ABI、协议（Protocol）四大基础概念辨析教程——各自定义、层次关系、稳定性规则、典型实例与横向对比，建立软件边界设计的概念坐标系。",
        overview="",
    )

    # ---------- B5. jishu/ai/jira-skill（保留三层结构） ----------
    src = L01 / "jira-skill-wiki"
    dst = BUNDLES / "jishu" / "ai" / "jira-skill"
    for sub in ("concepts", "examples", "references"):
        sd = src / sub
        td = dst / sub
        td.mkdir(parents=True, exist_ok=True)
        for f in sorted(sd.iterdir()):
            if f.is_file() and f.suffix == ".md" and f.name != "index.md" and not should_skip(f):
                dtype = {"concepts": "Concept", "examples": "Example", "references": "Reference"}[sub]
                migrate_file(f, td / f.name, rel_to_learning(f), dtype)
        write_doc(td / "index.md", gen_dir_index(td, {
            "concepts": "概念文档", "examples": "使用示例", "references": "信源登记簿"}[sub]))
    root_idx = gen_bundle_root_index(
        "Jira Skill",
        "Jira 工程化集成 Skill 完整教程——双技能架构（jira-communication API 操作 + jira-syntax Wiki markup 语法）、三层脚本体系、JQL 查询语言、安装配置、最佳实践与故障排查。",
        "本束覆盖 jira-skill 插件的定位、架构设计、六种安装方式、Cloud/Server 认证差异、意图动词机制、提交前校验与 dry-run 安全实践，配套 CLI 基础用法、语法模板与工作流自动化三组示例及 API/官方文档/源码信源登记。",
        [("concepts/", "concepts/index.md", "概念文档（10 篇，入门→核心→高级）"),
         ("examples/", "examples/index.md", "使用示例（CLI 用法、语法模板、工作流自动化）"),
         ("references/", "references/index.md", "信源登记簿（API 参考、官方文档、源码）")],
        ["concepts/index", "examples/index", "references/index", "log"],
    )
    write_doc(dst / "index.md", root_idx)
    write_doc(dst / "log.md", gen_log_md([
        "* 源：01-agent-protocols-interfaces/jira-skill-wiki/（22 文件，保留 concepts/examples/references 三层）",
        "* 舍弃：README.md/index.md（导航元数据）、log.md（工作流元数据，含个人路径）",
    ]))
    print("[bundle] jishu/ai/jira-skill done")

    # ---------- B6. meta/okf-desktop ----------
    migrate_flat_bundle(
        L01 / "okf-desktop-wiki", BUNDLES / "meta" / "okf-desktop",
        title="OKF Desktop",
        description="OKF Desktop 桌面阅读器完整教程——架构总览、快速开始、UI 界面解析、API 与数据流、打包分发、FAQ 与资源。",
        overview="",
    )

    # ---------- B7. jishu/ai/ai-agent/agent-interface ----------
    migrate_flat_bundle(
        L01 / "agent-interface-deep-dive", BUNDLES / "jishu" / "ai" / "ai-agent" / "agent-interface",
        title="Agent 接口深潜",
        description="AI Agent 接口四层概念深潜——Agent Interface、Agent API、Agent ABI、Agent Protocol 的定义、层次关系、设计权衡与横向对比，附资源索引。",
        overview="",
    )

    # ---------- B8. jishu/ai/ai-agent/agent-runtime-protocol ----------
    dst = BUNDLES / "jishu" / "ai" / "ai-agent" / "agent-runtime-protocol"
    migrate_flat_bundle(
        L01 / "agent-runtime-protocol-wiki", dst,
        title="Agent Runtime Protocol",
        description="生产级 Agent 运行时协议完整教程——六大 Protocol 对象（Agent/Thread/Run/Step/Checkpoint/Artifact）与八大维度解析：边界与生命周期、执行模型、状态管理、中断与错误恢复、工具协议与流式输出、多 Agent 协作、可观测性与可评测性、设计原则，附五大框架对比与企业级选型指南。",
        overview="",
        extra_refs=[(L01 / "agent-runtime-protocol-wiki" / "interactive-selection-matrix.html",
                     "interactive-selection-matrix.html")],
        merge_lines=[
            "* 源：01-agent-protocols-interfaces/agent-runtime-protocol-wiki/（17 文件）+ 可交互选型决策矩阵（HTML）随迁 references/",
            "* 分类根散文件 agent-runtime-protocol-wiki.md 为原子化导航页（无独有正文），未迁入，登记于此",
            "* 舍弃：log.md（工作流元数据）",
        ],
    )

    # ---------- B9. jishu/ai/ai-agent/agent-communication-protocols ----------
    dst = BUNDLES / "jishu" / "ai" / "ai-agent" / "agent-communication-protocols"
    migrate_flat_bundle(
        L01 / "agent-communication-protocols", dst,
        title="Agent 通信协议",
        description="Agent 通信四大协议完整教程——MCP（工具连接层）、ACP（本地消息层）、A2A（跨平台协作层）、ANP（去中心化网络层）四层协议栈：协议详解、对比与分层架构、交互流程、技术实现、典型场景、术语表与快速参考。",
        overview="",
        extra_concepts=[
            (L01 / "agent-communication-protocols-wiki.md", "protocol-stack-map.md",
             "01-agent-protocols-interfaces/agent-communication-protocols-wiki.md"),
            (L01 / "domestic-skill-mcp-ecosystem-wiki.md", "domestic-skill-mcp-ecosystem.md",
             "01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md"),
        ],
        merge_lines=[
            "* 源：01-agent-protocols-interfaces/agent-communication-protocols/（14 文件）",
            "* 分类根散文件 agent-communication-protocols-wiki.md 的独有内容（四层协议栈架构图、一句话定位表、阅读建议）并入为 concepts/protocol-stack-map.md",
            "* 分类根散文件 domestic-skill-mcp-ecosystem-wiki.md（国内 Skill/MCP 生态 16 品牌盘点）无同名主题束，按台账「并入」处置并入本束为 concepts/domestic-skill-mcp-ecosystem.md",
        ],
    )

    print(f"DONE batch1: migrated={STATS['files']}")


if __name__ == "__main__":
    main()
