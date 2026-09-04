# -*- coding: utf-8 -*-
"""批次 2：knowledge-catalog 双源（01 分类 11 文件 + 07/google-cloud 11 文件）
合并入 meta/okf-spec（部分重叠 #4）。

策略：既有 tooling-knowledge-catalog.md 已覆盖仓库结构/CLI/npm 包基础；
本次仅迁入两源的独有实质内容，重写为 5 个增量概念 + 1 个信源登记：
  concepts/knowledge-catalog-platform.md      平台概述与架构（01/00+01）
  concepts/knowledge-catalog-reference-agent.md 参考 Agent 实现（01/03 + 07/02）
  concepts/knowledge-catalog-metadata-as-code.md 元数据即代码（07/03 + 01/04 mdcode 节）
  concepts/knowledge-catalog-samples.md       官方示例与示例 Agent（01/05 + 07/04）
  concepts/knowledge-catalog-adoption.md      集成模式与选型决策（01/06+07 + 07/05 反模式）
  references/knowledge-catalog-readme-zh.md   官方 README 中文转译（07 散文件）
重复确认（不迁入）：01/02 OKF 规范解析（与规范转译概念重叠）、01/08 术语表（与 terminology 重叠）、
01/04 可视化（与 tooling-knowledge-catalog 重叠）、两源 README/各级 index（导航元数据）。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from migrate_lib import (
    LEARNING, BUNDLES, MIGRATION_DATE,
    split_frontmatter, parse_fm, clean_body, yaml_str,
    write_doc,
)

SPEC = BUNDLES / "meta" / "okf-spec"
SRC1 = LEARNING / "01-agent-protocols-interfaces" / "knowledge-catalog-wiki"
SRC2 = LEARNING / "07-vendor-product-learning" / "google-cloud"

# 指向 learning 内部 wiki 的相对链接 → 去链接化（保留锚文本）
INTERNAL_LINK_RE = re.compile(r"\[([^\]]*)\]\((?:\.\./[^)]*|\.\.[^)]*)\)")


def strip_internal_links(body: str) -> str:
    """把指向 learning 内部 wiki 的相对链接去链接化（保留锚文本）。"""
    return INTERNAL_LINK_RE.sub(r"\1", body)


def read_body(p: Path) -> str:
    text = p.read_text(encoding="utf-8")
    _, body = split_frontmatter(text)
    return clean_body(strip_internal_links(body))


def fm_block(title: str, desc: str, tags: list[str], sources: list[tuple[str, str]]) -> str:
    lines = ["---", "type: Concept", f"title: {yaml_str(title)}", f"description: {yaml_str(desc)}"]
    lines.append(f"tags: [{', '.join(yaml_str(t) for t in tags)}]")
    lines.append(f"generated: {{ by: process:learning-bundles-merge, at: {MIGRATION_DATE}T00:00:00Z }}")
    lines.append("status: draft")
    lines.append(f"stale_after: 2027-09-02")
    lines.append("sources:")
    for i, (res, ttl) in enumerate(sources, 1):
        lines.append(f"  - id: src{i}")
        lines.append(f"    resource: {yaml_str(res)}")
        lines.append(f"    title: {yaml_str(ttl)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def main():
    concepts = SPEC / "concepts"
    refs = SPEC / "references"

    # 1. 平台概述与架构
    body = read_body(SRC1 / "00-overview.md") + "\n\n---\n\n" + read_body(SRC1 / "01-core-concepts.md")
    write_doc(concepts / "knowledge-catalog-platform.md", fm_block(
        "Knowledge Catalog 平台概述与架构",
        "Google Cloud Knowledge Catalog（原 Dataplex）AI 驱动数据目录与元数据管理平台——背景动机、三大设计哲学、核心概念体系、四层平台架构与知识生产-消费闭环定位。",
        ["okf", "knowledge-catalog", "google-cloud", "dataplex", "data-catalog", "platform"],
        [("SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/（00-overview.md、01-core-concepts.md）",
          "Knowledge Catalog Wiki 教程（learning 侧合并来源）")],
    ) + body)

    # 2. 参考 Agent 实现
    body = read_body(SRC1 / "03-reference-agent.md") + "\n\n---\n\n" + read_body(SRC2 / "knowledge-catalog-wiki" / "02-reference-agent.md")
    write_doc(concepts / "knowledge-catalog-reference-agent.md", fm_block(
        "Knowledge Catalog 参考 Agent 实现",
        "knowledge-catalog 参考 Agent 源码级解析——两阶段工作流架构、enrich 子命令参数、核心工具模块（bundle/source/web/context）、Python 实现细节、单概念迭代开发方法与 GCP 凭证配置。",
        ["okf", "knowledge-catalog", "reference-agent", "enrich", "python", "gcp"],
        [("SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/03-reference-agent.md",
          "Knowledge Catalog Wiki 参考 Agent 章（01 分类）"),
         ("SpecWeave docs/knowledge/learning/07-vendor-product-learning/google-cloud/knowledge-catalog-wiki/02-reference-agent.md",
          "Knowledge Catalog Wiki 参考智能体章（07 分类）")],
    ) + body)

    # 3. 元数据即代码
    body = read_body(SRC2 / "knowledge-catalog-wiki" / "03-metadata-as-code.md")
    write_doc(concepts / "knowledge-catalog-metadata-as-code.md", fm_block(
        "Knowledge Catalog 元数据即代码（mdcode）",
        "mdcode 元数据即代码工具链——元数据制品结构、init/pull/push/diff 双向同步命令、开发者工作流、BigQuery 集成与 mdcode 和 OKF 的关系。",
        ["okf", "knowledge-catalog", "mdcode", "metadata-as-code", "bigquery", "git-workflow"],
        [("SpecWeave docs/knowledge/learning/07-vendor-product-learning/google-cloud/knowledge-catalog-wiki/03-metadata-as-code.md",
          "Knowledge Catalog Wiki 元数据即代码章（07 分类）")],
    ) + body)

    # 4. 官方示例
    body = read_body(SRC1 / "05-samples-and-bundles.md") + "\n\n---\n\n" + read_body(SRC2 / "knowledge-catalog-wiki" / "04-samples.md")
    write_doc(concepts / "knowledge-catalog-samples.md", fm_block(
        "Knowledge Catalog 官方示例解析",
        "官方示例知识包与示例 Agent 实战——GA4/Stack Overflow/比特币区块链/Acme Retail 四个示例 Bundle 结构解析、recipe 配方对应关系、Discovery/Enrichment 两个示例智能体的运行与组合使用。",
        ["okf", "knowledge-catalog", "samples", "ga4", "discovery-agent", "enrichment-agent"],
        [("SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/05-samples-and-bundles.md",
          "Knowledge Catalog Wiki 示例 Bundle 章（01 分类）"),
         ("SpecWeave docs/knowledge/learning/07-vendor-product-learning/google-cloud/knowledge-catalog-wiki/04-samples.md",
          "Knowledge Catalog Wiki 示例智能体章（07 分类）")],
    ) + body)

    # 5. 集成模式与选型决策
    body = (read_body(SRC1 / "06-integration-patterns.md")
            + "\n\n---\n\n" + read_body(SRC1 / "07-architecture-decisions.md")
            + "\n\n---\n\n" + read_body(SRC2 / "knowledge-catalog-wiki" / "05-best-practices.md"))
    write_doc(concepts / "knowledge-catalog-adoption.md", fm_block(
        "Knowledge Catalog 集成模式与选型决策",
        "OKF/Knowledge Catalog 企业落地实践——四阶段渐进式落地路径、三种典型集成场景、与既有数据目录共存、Git 工作流集成、8 种替代方案对比与选型决策树、五大反模式与编写检查清单。",
        ["okf", "knowledge-catalog", "adoption", "integration", "architecture-decision", "anti-patterns"],
        [("SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/（06-integration-patterns.md、07-architecture-decisions.md）",
          "Knowledge Catalog Wiki 集成与决策章（01 分类）"),
         ("SpecWeave docs/knowledge/learning/07-vendor-product-learning/google-cloud/knowledge-catalog-wiki/05-best-practices.md",
          "Knowledge Catalog Wiki 最佳实践章（07 分类）")],
    ) + body)

    # 6. 信源登记：官方 README 中文转译
    src_readme = SRC2 / "knowledge-catalog-readme-zh.md"
    text = src_readme.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    src_fm = parse_fm(fm)
    body = clean_body(strip_internal_links(body))
    write_doc(refs / "knowledge-catalog-readme-zh.md", fm_block(
        "Google Cloud Knowledge Catalog README 中文转译",
        "GoogleCloudPlatform/knowledge-catalog 仓库 README 的中文转译信源登记——仓库定位、组件清单与快速上手。",
        ["okf", "knowledge-catalog", "reference", "readme"],
        [("SpecWeave docs/knowledge/learning/07-vendor-product-learning/google-cloud/knowledge-catalog-readme-zh.md",
          "Knowledge Catalog README 中文版（learning 侧合并来源）")],
    ) + body)

    print("batch2 merge docs written: 5 concepts + 1 reference")


if __name__ == "__main__":
    main()
