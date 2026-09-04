---
status: "draft"
id: "spec-docs-to-knowledge-okf-migration"
title: "docs/ 到 docs/knowledge/ OKF Wiki 教程迁移"
source: "用户请求 + 代码库现状分析"
date: "2026-08-22"
category: "spec"
tags: ["migration", "okf-wiki", "knowledge-base", "docs", "refactor"]
---

# docs/ 到 docs/knowledge/ OKF Wiki 教程迁移 - 产品需求文档

## Overview

- **Summary**：将废弃的根目录 `docs/`（Jupyter Book/Sphinx 文档站）中尚未迁移的全部内容，按照目标知识库既有的 11 主题编号分类体系（00-10）和 OKF Wiki 教程格式规范，完整迁移至 `docs/knowledge/` 及对应的 `.agents/docs/retrospective/` 等目录。迁移包括文件移动、frontmatter 标准化、TOML 元数据创建、内部链接修复、README.md 索引生成等完整格式转换。
- **Purpose**：根目录 `docs/` 已在 AGENTS.md 中声明废弃为空壳，但仍有约 198 个 Markdown 文件（含 13 个完整 Wiki 文件夹、15 个方法论模式、18 个复盘报告）未迁移至 `.agents/docs/` 有效文档容器，导致知识分散、路径引用混乱、文档站构建配置残留。本次迁移彻底消除双轨文档问题。
- **Target Users**：项目维护者、AI Agent（需要统一路径访问知识库）、后续学习者

## Goals

- 将 `docs/` 中所有未迁移的 Markdown 内容按内容类型归入 `.agents/docs/` 对应目录
- 所有学习 Wiki 遵循目标目录的编号分类体系（00-10），实现唯一归属
- 所有迁移文件符合项目 Wiki 教程格式规范（frontmatter 4 字段标准 + TOML 元数据）
- 修复所有内部链接路径，确保无断链
- 每个原子化 Wiki 文件夹具备 README.md 索引和标准章节结构
- 迁移完成后更新相关索引文件（CATEGORIES.md、category-index.md 等）

## Non-Goals (Out of Scope)

- 不对迁移内容做实质性改写或内容增补（仅格式转换和路径修复）
- 不迁移 Sphinx/Jupyter Book 构建配置文件（`conf.py`、`_config.toml`、`requirements.txt`、`tasks.py`）
- 不迁移 `_static/` 目录下的 CSS/PNG 等站点主题资源（目标知识库不依赖 Jupyter Book 主题）
- 不对已存在于目标目录中的文件做重复迁移（仅补全缺失章节）
- 不删除 `docs/` 源文件（用户未确认清理方式，作为开放问题保留）

## Background & Context

- AGENTS.md 第 113 行明确声明："根目录 `docs/` 已废弃为空壳，所有文档引用均解析为 `.agents/docs/`"
- 目标知识库 `docs/knowledge/` 已有 1288 条目、53 分类、2514 标签，采用编号分类体系
- 目标 learning/ 目录已建立 11 主题架构（00-本质与思维 到 10-通用基础），有 CATEGORIES.md 作为分类权威依据
- 项目存在 `.agents/templates/wiki-spec-template.md`（v1.2.0）作为 Wiki 教程格式标准
- 项目存在自动化工具：`generate-readme.py`（索引生成）、`fix-x-toml-ref.py`（路径修复）、`check-links.py`（链接检查）、`check-filename-convention.py`（文件名检查）
- 源文件 frontmatter 格式不统一：部分使用丰富字段（version/type/description/category/status/author/summary），部分仅有简单字段
- 七概念方法论场景判定：本任务属于**场景3：重构优化**（I→F→A→C 链路）——洞察文档分散问题→第一性原理设计分类映射→原子化拆分迁移任务→原子提交交付

## Functional Requirements

- **FR-1**：将 13 个完全缺失的 Wiki 文件夹迁移至目标 learning/ 对应分类目录
- **FR-2**：补全 3 个部分迁移的 Wiki（open-code-review-wiki、agent-runtime-protocol-wiki、ai-engineering-four-milestones-wiki）的缺失章节
- **FR-3**：将 5 个微信文章分析文件夹的内容迁移至对应分类
- **FR-4**：将 ai-engineering/、algorithmic-art/、engineering/ 下的知识文件迁移至合适位置
- **FR-5**：将 retrospective/patterns/methodology-patterns/ 下 15 个模式文件迁移至 `.agents/docs/retrospective/patterns/methodology-patterns/`
- **FR-6**：将 retrospective/reports/ 下 18 个复盘报告迁移至 `.agents/docs/retrospective/` 对应子目录
- **FR-7**：将 tech/ 下 4 个未迁移文件归入 `docs/knowledge/tech/` 或根级对应位置
- **FR-8**：将 refactor/ 下 1 个文件归入合适位置
- **FR-9**：所有原子化 Wiki 文件 frontmatter 标准化为 4 字段（id/title/source/x-toml-ref）
- **FR-10**：为所有原子化 Wiki 创建配套 `.meta/toml/` 镜像路径下的 TOML 元数据文件
- **FR-11**：为每个迁移的 Wiki 文件夹创建/更新 README.md 索引
- **FR-12**：修复所有迁移文件中的内部相对路径链接
- **FR-13**：更新 CATEGORIES.md 中的 Wiki 清单和统计数字
- **FR-14**：迁移 3 个 HTML 附属文件至目标 Wiki 目录或合适的静态资源位置

## Non-Functional Requirements

- **NFR-1**：迁移后 `check-links.py` 验证零断链
- **NFR-2**：迁移后 `check-filename-convention.py` 验证文件名全部合规（kebab-case、纯英文）
- **NFR-3**：迁移后 `fix-x-toml-ref.py` 验证 x-toml-ref 路径全部正确且 TOML 文件存在
- **NFR-4**：每个原子化 Wiki 的 frontmatter 字段数严格为 4 个，无多余字段
- **NFR-5**：迁移过程不破坏目标目录中已有的 1288 条目
- **NFR-6**：每个 Wiki 文件夹作为一个原子迁移单元，可独立验证和提交

## Constraints

- **Technical**：Windows 平台；PowerShell 环境；文件路径长度限制；Git 中文提交需使用 `git-commit-utf8.py`
- **Business**：遵循 AGENTS.md 全局契约；遵循 wiki-spec-template.md v1.2.0 格式规范；文件名 kebab-case 纯英文
- **Dependencies**：`.agents/scripts/fix-x-toml-ref.py`、`generate-readme.py`、`check-links.py`、`check-filename-convention.py`

## Assumptions

- 目标目录的 11 主题分类体系是稳定且权威的分类依据
- 源文件内容本身质量可接受，不需要实质性内容审查
- 已存在于目标目录中的同名文件是已迁移版本，不需要覆盖
- `seven-concepts-report.md` 文件属于过程产物，随 Wiki 一起迁移但不作为独立知识条目
- HTML 文件作为 Wiki 附属资源保留在对应 Wiki 目录中

## Acceptance Criteria

### AC-1: 完整 Wiki 文件夹迁移

- **Given**：源目录存在 13 个完全缺失的 Wiki 文件夹
- **When**：迁移完成后
- **Then**：每个 Wiki 文件夹在目标 learning/ 对应分类目录下存在，包含全部章节文件和 README.md
- **Verification**：`programmatic`
- **Notes**：通过文件系统对比验证

### AC-2: 部分迁移 Wiki 补全

- **Given**：3 个 Wiki 在目标中仅有部分章节
- **When**：迁移完成后
- **Then**：缺失章节文件已补充，章节编号连续完整
- **Verification**：`programmatic`

### AC-3: 复盘与模式文件迁移

- **Given**：源目录有 15 个方法论模式和 18 个复盘报告
- **When**：迁移完成后
- **Then**：所有文件在 `.agents/docs/retrospective/` 对应目录下存在
- **Verification**：`programmatic`

### AC-4: Frontmatter 格式合规

- **Given**：所有迁移的原子化 Wiki Markdown 文件
- **When**：检查 frontmatter
- **Then**：原子化 Wiki 严格包含 id/title/source/x-toml-ref 四个字段，无多余字段
- **Verification**：`programmatic`

### AC-5: 内部链接无断链

- **Given**：迁移后的所有 Markdown 文件
- **When**：运行 check-links.py
- **Then**：零断链报告
- **Verification**：`programmatic`

### AC-6: 文件名规范

- **Given**：所有迁移的文件和文件夹
- **When**：运行 check-filename-convention.py
- **Then**：全部文件名符合 kebab-case 纯英文规范
- **Verification**：`programmatic`

### AC-7: TOML 元数据完整

- **Given**：所有原子化 Wiki 的 x-toml-ref 引用
- **When**：检查 TOML 文件
- **Then**：每个 x-toml-ref 指向的 TOML 文件存在且包含 category/date/tags/status 等元数据
- **Verification**：`programmatic`

### AC-8: 分类索引更新

- **Given**：CATEGORIES.md 和 category-index.md
- **When**：迁移完成后
- **Then**：新增 Wiki 在对应主题清单中列出，统计数字已更新
- **Verification**：`human-judgment`

### AC-9: 分类映射合理性

- **Given**：每个迁移 Wiki 的目标分类位置
- **When**：人工审核
- **Then**：分类符合 CATEGORIES.md 中的主题边界说明，无明显错分
- **Verification**：`human-judgment`

## Open Questions

- [ ] 迁移完成后是否删除 `docs/` 源文件？用户未明确回答，默认保留，后续可单独发起清理任务
- [ ] `docs/tech/` 中的项目技术文档（contributing.md、four-layer-logging-pattern.md 等）是否应迁移至 `.agents/docs/` 根级而非 knowledge/ 目录？
- [ ] 微信文章分析文件夹中的 `analysis-report.md` 和 `article-content.md` 是过程文件还是最终知识条目？是否需要全部保留？
- [ ] `codewhale/` 目录在源和目标中都有文件但结构不同，是否需要合并？

---

## 附录：Wiki 分类映射表（待审核确认）

| 源 Wiki 文件夹 | 文件数 | 目标分类 | 目标路径 |
|---|---|---|---|
| agency-agents-wiki | 12 | 03 Agent平台与工具 | `learning/03-agent-platforms-tools/agency-agents-wiki/` |
| cordis-spatiotemporal-composability-wiki | 14 | 01 Agent协议与接口 | `learning/01-agent-protocols-interfaces/cordis-wiki/` |
| deepseek-harness-wiki | 17 | 07 厂商产品→DeepSeek | `learning/07-vendor-product-learning/deepseek/deepseek-harness-wiki/` |
| okf-kit-wiki | 12 | 01 协议接口→OKF生态 | `learning/01-agent-protocols-interfaces/okf-wiki/okf-kit-wiki/` |
| open-code-review-wiki（补全） | 9 | 03 平台工具→代码工具 | `learning/03-agent-platforms-tools/03-code-devtools/open-code-review-wiki/` |
| agent-runtime-protocol-wiki（扩展） | 12 | 01 协议与接口 | `learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki/` |
| ai-engineering-four-milestones-wiki | 8 | 02 工程方法论→范式 | `learning/02-agent-engineering-methodology/01-paradigms/ai-engineering-four-milestones-wiki/` |
| baidu-unlimited-ocr-wiki | 9 | 07 厂商产品→百度 | `learning/07-vendor-product-learning/baidu/baidu-ocr-wiki/` |
| book-to-skill-wiki | 10 | 02 工程方法论→Prompt | `learning/02-agent-engineering-methodology/02-prompt-coding/book-to-skill-wiki/` |
| github-cli-wiki | 9 | 08 底层系统→Git | `learning/08-systems-infrastructure/github-cli-wiki/` |
| minit2i-minimalist-t2i-wiki | 8 | 05 AI多模态内容 | `learning/05-ai-multimodal-content/minit2i-wiki/` |
| python314-cpython-wiki | 17 | 10 通用基础知识 | `learning/10-foundational-knowledge/python314-cpython-wiki/` |
| python314-stdlib-wiki | 18 | 04 文档工具链/Python | `learning/04-docs-markup-tooling/python314-stdlib-wiki/` |
| three-ai-tools-learning-wiki | 2 | 06 商业趋势观察 | `learning/06-business-trends-analysis/three-ai-tools-wiki/` |
| analyze-wechat-article-ai-switch-governance | 3 | 06 商业趋势 | `learning/06-business-trends-analysis/ai-switch-governance/` |
| analyze-wechat-article-causal-ai | 2 | 05 多模态内容 | `learning/05-ai-multimodal-content/causal-ai/` |
| analyze-wechat-article-mainecoon | 10 | 05 多模态内容 | `learning/05-ai-multimodal-content/mainecoon-wiki/` |
| analyze-wechat-article-quantdinger | 2 | 03 平台工具 | `learning/03-agent-platforms-tools/quantdinger/` |
| analyze-wechat-article-rqndd | 1 | 06 商业趋势 | `learning/06-business-trends-analysis/rqndd/` |
| ai-engineering/*.md | 2 | 02 工程方法论 | `learning/02-agent-engineering-methodology/` |
| algorithmic-art/atomic-emergence/ | 2 | 05 多模态/创意 | `learning/05-ai-multimodal-content/atomic-emergence/` |
| engineering/deep-learning-atomic-design/ | 3 | 02 工程方法论 | `learning/02-agent-engineering-methodology/` |
| retrospective/patterns/methodology-patterns/ | 15 | 复盘模式库 | `.agents/docs/retrospective/patterns/methodology-patterns/` |
| retrospective/reports/ | 18 | 复盘报告 | `.agents/docs/retrospective/` 对应子目录 |
| tech/*.md | 4 | 技术文档 | `docs/knowledge/tech/` |
| refactor/*.md | 1 | 重构记录 | `docs/knowledge/best-practices/` |
