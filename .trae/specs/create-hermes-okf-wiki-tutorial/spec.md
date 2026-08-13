---
id: "create-hermes-okf-wiki-tutorial-spec"
title: "Hermes OKF（基于OKF的Agent持久记忆）Wiki教程产品需求文档"
source: "seven-concepts knowledge-scenario: hermes-okf 官方 README（GitHub EliaszDev/hermes-okf v0.5.9）+ vendor/awesome-okf 中文索引"
date: "2026-08-09"
tags: ["hermes-okf", "OKF", "Open Knowledge Format", "Agent记忆", "持久记忆", "Hermes", "wiki教程", "知识沉淀"]
---

# Hermes OKF（基于OKF的Agent持久记忆）Wiki教程 - Product Requirement Document

## Overview
- **Summary**: 基于 hermes-okf 官方仓库（GitHub EliaszDev/hermes-okf，v0.5.9）与 OKF 生态中文索引，系统创建一份原子化的 Hermes OKF Wiki 教程。Hermes OKF 是首个基于 Google Open Knowledge Format（OKF）构建的开源 Agent 持久记忆系统，专为 Hermes agent 生态设计。教程覆盖项目定位、核心特性、五层架构、快速上手、Hermes 插件 CLI、独立 CLI、Agent 集成、RAG 集成、故障排查与路线图，输出到 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/hermes-okf-wiki/` 目录。
- **Purpose**: 帮助 AI Agent 开发者、Hermes 生态用户、知识工程师快速掌握 Hermes OKF——如何用纯 Markdown + YAML（无数据库、无锁定）为 Agent 构建持久、结构化、可版本化的记忆层，并理解其在 OKF 生态中的定位（"OKF 当 Agent 记忆层"的代表项目）。
- **Target Users**: AI Agent 开发者、Hermes agent 用户、知识工程师、架构师、技术决策者、对 OKF 生态感兴趣的技术人员。

## Goals
- 基于 hermes-okf 官方仓库与 OKF 生态资料整合形成结构化学习教程
- 清晰解释 Hermes OKF 的核心定位（OKF 生态中"Agent 持久记忆"方向的代表项目）
- 详解五层架构（Human Interface / Hermes Plugin / Universal Provider / Core OKF / Persistence）
- 提供从零到一的快速上手指南（PyPI 安装 → 注册插件 → 校验 → 激活 provider）
- 完整覆盖 Hermes 插件 CLI（`hermes okf`）与独立 CLI（`hermes-okf`）命令
- 阐述 Agent 集成（装饰器、HermesMemoryMixin）与可选 RAG 集成（LangChain/ChromaDB）
- 提供故障排查（Troubleshooting）与路线图（Roadmap）解读
- 包含术语表、FAQ、与 OKF 生态的关系定位及后续演进

## Non-Goals (Out of Scope)
- 不实现 Hermes OKF 源码或任何工具链代码
- 不深度分析 hermes-okf 的 Python 源码实现细节（仅做架构与用法解读）
- 不覆盖 Hermes agent 框架本身的完整使用教程（仅涉及其记忆供应商接口）
- 不翻译整个 hermes-okf 官方 README（提炼整合 + 本地化解读 + 中文语境最佳实践）
- 不深度对比所有 Agent 记忆方案（仅做 OKF 生态内的定位对比，如 throughline / okf-harness / echoes-vault）

## Background & Context
- Hermes OKF 是首个基于 Google OKF 构建的开源 Agent 持久记忆系统，专为 Hermes agent 生态设计
- 核心主张：Agent 的决策、观察、工具调用历史跨会话持久化，存为 markdown + YAML 的知识图
- 无数据库、无锁定（no lock-in），Filesystem-First，仅单一核心依赖 `pyyaml`，可选 RAG（LangChain/ChromaDB）
- 已发布到 PyPI（`pip install hermes-okf`），可作 Hermes 插件（通过 `hermes-okf install-plugin` 注册）
- 提供 `search / list / show / snapshot / restore` 等命令，含 `init / validate / log / diff / revert / graph / context / sessions / plans / tools`
- 五层架构：Human Interface → Hermes Plugin Layer → Universal Provider → Core OKF Layer → Persistence
- 同属"OKF 当 Agent 记忆 / 上下文层"方向：throughline（代码仓库记忆层）、okf-harness（本地 agent harness）、echoes-vault（OpenCode 持久记忆）
- 项目知识库已有 OKF 通用教程（okf-wiki）与 OKF 生态基建知识（okf-ecosystem-wiki）
- OKF（Open Knowledge Format）是 Google Cloud 2026-06-12 发布的厂商中立开放规范，把 Karpathy 的 LLM wiki 模式标准化

## Functional Requirements
- **FR-1**: 教程采用原子化 wiki 结构（README + 多个编号章节文件），放置在 `okf-wiki/hermes-okf-wiki/` 目录
- **FR-2**: 包含 8-10 个核心章节（00-overview 到 07/08-resources），遵循 OKF wiki 原子化模板
- **FR-3**: frontmatter 遵循现有原子化 wiki 格式（id/title/source/description/tags/category/date/status 等字段）
- **FR-4**: 包含项目定位与生态背景（OKF 生态中 Agent 记忆层代表项目，与 throughline/okf-harness/echoes-vault 对比）
- **FR-5**: 包含核心特性与价值主张（持久记忆、隐式知识图、Filesystem-First、零数据库、Hermes 插件、可续接/可移植、Git 历史）
- **FR-6**: 包含五层架构详解（Human Interface / Hermes Plugin / Universal Provider / Core OKF / Persistence），含 Mermaid 图
- **FR-7**: 包含快速上手完整实操（`pip install hermes-okf` → `install-plugin` → `validate-config` → `hermes memory setup` → 卸载）
- **FR-8**: 包含 Hermes 插件 CLI 命令详解（`hermes okf search|list|show|snapshot|restore`）
- **FR-9**: 包含独立 CLI 命令详解（`hermes-okf init/validate/list/show/search/log/diff/revert/log-append/graph-edges/graph-neighbors/snapshot/context/sessions/plans/tools`）
- **FR-10**: 包含 Agent 集成（HermesMemoryMixin、`@memorize_decision`、`@memorize_tool`、`with_context`）代码示例
- **FR-11**: 包含可选 RAG 集成（LangChain DirectoryLoader + MarkdownHeaderTextSplitter + Chroma）代码示例
- **FR-12**: 包含故障排查（Troubleshooting）章节，覆盖 install-plugin 失败 / memory setup 不显示 / show 显示错误模型 / bundle 未找到 / Windows 文件名错误
- **FR-13**: 包含 Roadmap 解读与 v0.5.9 里程碑（15 项特性，已交付 10 项 / 待办 5 项）
- **FR-14**: 包含术语表、FAQ、资源链接与 OKF 生态交叉引用
- **FR-15**: 更新 okf-wiki/README.md 文档索引表，添加 hermes-okf-wiki 入口

## Non-Functional Requirements
- **NFR-1**: 所有内容使用标准现代汉语书面语，专业术语统一（OKF/Hermes/provider/concept 等首次出现给出解释）
- **NFR-2**: 章节粒度适中，单文件 <300 行（遵循原子化原则）
- **NFR-3**: 代码示例（CLI 命令、Python 集成）完整可复制，标注预期输出
- **NFR-4**: 版本提示明确（hermes-okf v0.5.9，OKF 生态早期，API 可能演进）
- **NFR-5**: 交叉链接正确，文件间引用使用相对路径，禁止 `file:///` 绝对路径
- **NFR-6**: frontmatter 字段与现有 wiki 保持一致，不添加额外无依据字段
- **NFR-7**: 三级标题使用 x.y 编号格式（1.1、2.3 等，从 x.1 开始）

## Constraints
- **Technical**: 输出为纯 Markdown 文件 + YAML frontmatter，无额外依赖
- **Business**: 基于 hermes-okf 官方仓库公开信息整理，不虚构未公开的特性；所有命令与版本号有据可查
- **Dependencies**:
  - 参考现有 wiki 格式：`okf-wiki/`（00-overview 等章节结构）、`okf-ecosystem-wiki/`、`knowledge-catalog-wiki/`
  - 资料来源：hermes-okf 官方 README（v0.5.9）、vendor/awesome-okf/references/hermes-okf.md、resources-zh.md
  - 输出路径：`.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/hermes-okf-wiki/`

## Assumptions
- 输出目录归类在 `okf-wiki/` 子目录下是合理的（Hermes OKF 是 OKF 生态的 Agent 记忆层工具）
- 原子化 wiki 结构（而非单文件）更适合 Hermes OKF 这种内容丰富、章节独立性高的主题
- 现有原子化 wiki 的 frontmatter 格式（含 category/tags/date/status 等字段）是当前标准
- 面向中国开发者的中文语境解读，命令与示例保留英文原文

## Acceptance Criteria

### AC-1: Wiki 目录结构完整
- **Given**: 教程创建完成
- **When**: 查看输出目录
- **Then**: 存在 `hermes-okf-wiki/` 目录，包含 README.md 和 00-07（或 08）编号章节文件
- **Verification**: `programmatic`
- **Notes**: 验证文件存在和命名规范（kebab-case）

### AC-2: Frontmatter 格式合规
- **Given**: 每个章节文件
- **When**: 检查 frontmatter
- **Then**: 包含 id/title/source/description/tags/category/date/status 字段，格式与现有原子化 wiki 一致（YAML，非 TOML）
- **Verification**: `programmatic`
- **Notes**: 参考 okf-wiki/00-overview.md 的 frontmatter 格式

### AC-3: 项目定位与生态背景阐述清晰
- **Given**: 00-overview.md 或 01 章节
- **When**: 阅读项目定位部分
- **Then**: 清晰说明 Hermes OKF 是 OKF 生态中"Agent 持久记忆"方向的代表项目，与 throughline/okf-harness/echoes-vault 的定位对比
- **Verification**: `human-judgment`

### AC-4: 核心特性覆盖完整
- **Given**: 相关章节
- **When**: 阅读核心特性
- **Then**: 覆盖持久记忆、隐式知识图、Filesystem-First、零数据库核心（仅 pyyaml）、Hermes 插件、可续接/可移植、Git 历史、Config Validator
- **Verification**: `human-judgment`

### AC-5: 五层架构阐述清晰
- **Given**: 架构章节
- **When**: 阅读架构分析
- **Then**: 清晰说明五层架构（Human Interface → Hermes Plugin → Universal Provider → Core OKF → Persistence），含 Mermaid 图
- **Verification**: `human-judgment`

### AC-6: 快速上手可实操
- **Given**: 快速上手章节
- **When**: 按步骤操作
- **Then**: 可以完成 `pip install hermes-okf` → `hermes-okf install-plugin` → `hermes-okf validate-config` → `hermes memory setup` 的完整流程
- **Verification**: `human-judgment`
- **Notes**: 步骤清晰，命令完整可复制，标注预期输出

### AC-7: Hermes 插件 CLI 命令完整
- **Given**: 插件 CLI 章节
- **When**: 检查命令清单
- **Then**: 覆盖 `hermes okf search|list|show|snapshot|restore` 全部子命令及示例
- **Verification**: `programmatic`

### AC-8: 独立 CLI 命令完整
- **Given**: 独立 CLI 章节
- **When**: 检查命令清单
- **Then**: 覆盖 `hermes-okf init/validate/list/show/search/log/diff/revert/log-append/graph-edges/graph-neighbors/snapshot/context/sessions/plans/tools` 全部命令
- **Verification**: `programmatic`

### AC-9: Agent 集成代码示例正确
- **Given**: Agent 集成章节
- **When**: 阅读代码示例
- **Then**: 包含 HermesMemoryMixin、`@memorize_decision`、`@memorize_tool`、`with_context` 的完整可运行示例
- **Verification**: `human-judgment`

### AC-10: RAG 集成代码示例正确
- **Given**: RAG 集成章节
- **When**: 阅读代码示例
- **Then**: 包含 LangChain DirectoryLoader + MarkdownHeaderTextSplitter + Chroma 的完整示例，标注可选依赖 `pip install hermes-okf[rag]`
- **Verification**: `human-judgment`

### AC-11: 故障排查覆盖完整
- **Given**: 故障排查章节
- **When**: 检查问题清单
- **Then**: 覆盖 install-plugin 失败 / memory setup 不显示 / show 显示错误模型 / bundle 未找到 / Windows 文件名错误
- **Verification**: `human-judgment`

### AC-12: Roadmap 与术语表完整
- **Given**: 相关章节
- **When**: 检查内容
- **Then**: Roadmap 包含 15 项特性状态（已交付/待办）；术语表覆盖 OKF/Hermes/provider/concept/bundle/hot-cold memory 等核心术语
- **Verification**: `programmatic` + `human-judgment`

### AC-13: Mermaid 图表正确
- **Given**: 包含 Mermaid 图表的章节
- **When**: 渲染 Mermaid 代码
- **Then**: 图表语法正确，可正常渲染，清晰表达五层架构关系
- **Verification**: `human-judgment`

### AC-14: 交叉链接有效
- **Given**: 所有章节文件
- **When**: 检查 markdown 链接
- **Then**: 文件间相对链接路径正确，指向目标文件存在；okf-wiki/README.md 已添加 hermes-okf-wiki 入口
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要单独增加"与 OKF 生态的关系"对比章节（throughline/okf-harness/echoes-vault）？（建议纳入 00-overview 或单独 01 章节）
- [ ] 章节数量定为 8 章（00-07）还是 9 章（00-08）？（取决于是否拆分"核心特性"与"架构"）
- [ ] 是否需要补充 PyPI 实际安装验证（受网络环境限制，建议以官方 README 为准）？

## Impact
- **Affected specs**: okf-wiki（`01-agent-protocols-interfaces/okf-wiki/`）知识体系
- **Affected code**: 无源代码变更；仅新增知识文档 + 更新 okf-wiki/README.md 索引
- **Affected docs**: `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/hermes-okf-wiki/`（新建）、`okf-wiki/README.md`（更新索引）