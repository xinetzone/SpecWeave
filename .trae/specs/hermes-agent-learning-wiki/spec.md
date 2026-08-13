---
id: "hermes-agent-learning-wiki-spec"
title: "Hermes Agent 学习 Wiki 教程产品需求文档"
source: "seven-concepts knowledge-scenario: https://hermes-agent.nousresearch.com/docs/zh-Hans/（官方中文文档）+ external/libs/hermes-agent（NousResearch/hermes-agent 本地源码）"
date: "2026-08-10"
tags: ["Hermes", "hermes-agent", "Nous Research", "Agent框架", "wiki教程", "知识沉淀", "自进化Agent"]
---

# Hermes Agent 学习 Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 基于 Hermes Agent 官方中文文档（hermes-agent.nousresearch.com/docs/zh-Hans/）与本地源码仓库 `external/libs/hermes-agent`（NousResearch/hermes-agent），系统创建一份原子化的 Hermes Agent 学习 Wiki 教程。Hermes 是由 Nous Research 构建的自进化 AI Agent，是"唯一内置学习闭环"的智能代理——从经验创建技能、在使用中改进技能、主动持久化知识、搜索过往对话、跨会话构建深度理解。教程覆盖产品定位、核心特性、快速安装上手、CLI/斜杠命令、配置、消息网关、工具与工具集、技能系统、记忆系统、MCP 集成、定时调度、委派与并行、架构解析与源码导读，输出到 `.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-wiki/` 目录。
- **Purpose**: 帮助 AI Agent 开发者、Hermes 生态用户、知识工程师、架构师快速掌握 Hermes Agent——如何用一套代理核心运行在 CLI/消息网关/TUI/桌面端，如何通过闭环学习（记忆+技能）跨会话成长，如何通过插件与技能扩展而非扩张核心，以及其"核心窄腰、能力在边缘"的架构哲学。
- **Target Users**: AI Agent 开发者、Hermes 用户、知识工程师、架构师、技术决策者、对自进化 Agent 框架感兴趣的技术人员。

## Goals
- 基于 Hermes 官方中文文档与本地源码整合形成结构化学习教程
- 清晰解释 Hermes Agent 的核心定位（Nous Research 自进化 AI Agent、闭环学习）
- 详解六大核心特性（真正终端界面/随你所在/闭环学习/定时自动化/委派并行/随处运行/研究就绪）
- 提供从零到一的快速安装上手指南（curl 安装 → hermes 对话 → hermes model/tools/config/setup）
- 完整覆盖 CLI 命令、斜杠命令、配置体系与消息网关
- 详解工具与工具集（40+ 工具、工具集系统、终端后端、Footprint Ladder）
- 详解技能系统（过程记忆、技能中心、SKILL.md、curator 技能生命周期）
- 详解记忆系统（持久记忆、用户画像、memory provider、Honcho）
- 阐述 MCP 集成、定时调度（cron）、委派与并行（delegate_task）
- 提供架构解析（AIAgent 核心循环、CLI/TUI/桌面架构、项目结构）与源码导读
- 提供术语表、FAQ、与既有 hermes-agent-integration 集成指南的交叉引用

## Non-Goals (Out of Scope)
- 不实现 Hermes Agent 源码或任何工具链代码
- 不深度复现 hermes-okf（OKF 记忆层）细节（已有独立 hermes-okf-wiki）
- 不覆盖"将 SpecWeave 接入 Hermes"的集成细节（已有 hermes-agent-integration）
- 不翻译整个官方文档站（提炼整合 + 本地化解读 + 中文语境最佳实践）
- 不深度对比所有 Agent 框架（仅做定位性对比，如与 OpenClaw 迁移关系）

## Background & Context
- Hermes Agent（NousResearch/hermes-agent）是 Nous Research 构建的自进化 AI Agent，MIT 许可，由同一 agent 核心运行在 CLI、消息网关（Telegram/Discord/Slack 等约 20 平台）、TUI、Electron 桌面端
- 核心主张：唯一内置学习闭环的智能代理——从经验创建技能、在使用中改进技能、主动持久化知识、搜索过往对话、跨会话构建深度理解
- 可在 $5 VPS、GPU 集群或几乎零成本的 Serverless 基础设施运行；可通过 Telegram 对话而代理在云端 VM 工作
- 支持任意模型：Nous Portal、OpenRouter（200+）、NVIDIA NIM、小米 MiMo、z.ai/GLM、Kimi、MiniMax、Hugging Face、OpenAI 或自定义端点，`hermes model` 切换无锁定
- 两项塑造所有设计决策的属性：(1) 每次对话的 prompt caching 神圣不可破坏；(2) 核心是窄腰、能力在边缘（Footprint Ladder 决定新能力放置）
- 本地源码仓库 `external/libs/hermes-agent` 提供完整项目结构（run_agent.py ~12k LOC、cli.py ~11k LOC、tools/、gateway/、plugins/、skills/、tests/ ~17k 测试）
- 官方中文文档站 docs/zh-Hans 覆盖 getting-started / user-guide / developer-guide / reference / guides / integrations 六大板块
- 项目知识库已有 hermes-okf-wiki（OKF 记忆层）、hermes-agent-integration（SpecWeave 接入指南），可与本学习教程交叉引用形成体系

## Functional Requirements
- **FR-1**: 教程采用原子化 wiki 结构（README + 多个编号章节文件），放置在 `03-agent-platforms-tools/hermes-agent-wiki/` 目录
- **FR-2**: 包含 8-11 个核心章节（00-overview 到 10/11-resources），遵循现有原子化 wiki 模板
- **FR-3**: frontmatter 遵循现有原子化 wiki 格式（id/title/source/description/tags/category/date/status 等字段）
- **FR-4**: 包含产品定位与核心理念（Nous Research 自进化 AI Agent、闭环学习、核心窄腰/能力在边缘）
- **FR-5**: 包含核心特性详解（真正终端界面/随你所在/闭环学习/定时自动化/委派并行/随处运行/研究就绪）
- **FR-6**: 包含快速安装与上手指南（curl/install.ps1 安装 → hermes 对话 → model/tools/config/setup/gateway）
- **FR-7**: 包含 CLI 命令与斜杠命令详解（`hermes <subcommand>`、`/model`、`/skills`、`/compress`、COMMAND_REGISTRY）
- **FR-8**: 包含配置体系（config.yaml 顶层 section、.env 仅密钥、HERMES_HOME、profiles 多实例）
- **FR-9**: 包含消息网关详解（Telegram/Discord/Slack/WhatsApp/Signal 等约 20 平台、gateway setup/start）
- **FR-10**: 包含工具与工具集详解（40+ 工具、TOOLSETS、Footprint Ladder、服务门控 check_fn）
- **FR-11**: 包含技能系统详解（SKILL.md frontmatter、skill authoring 标准、skills/ vs optional-skills/、curator 生命周期）
- **FR-12**: 包含记忆系统详解（持久记忆、memory provider ABC、memory_manager、Honcho、用户画像）
- **FR-13**: 包含 MCP 集成、定时调度（cron 格式与命令）、委派与并行（delegate_task 单/批、角色）
- **FR-14**: 包含架构解析与源码导读（AIAgent 核心循环、CLI/TUI/桌面架构、项目结构、插件系统）
- **FR-15**: 包含术语表、FAQ、资源链接与既有 wiki（hermes-okf-wiki / hermes-agent-integration）交叉引用
- **FR-16**: 更新 03-agent-platforms-tools/README.md 子 Wiki 索引表，添加 hermes-agent-wiki 入口

## Non-Functional Requirements
- **NFR-1**: 所有内容使用标准现代汉语书面语，专业术语统一（Hermes/prompt caching/toolset/memory provider/skill 等首次出现给出解释）
- **NFR-2**: 章节粒度适中，单文件 <300 行（遵循原子化原则）
- **NFR-3**: 代码示例（CLI 命令、配置片段、Python 集成）完整可复制，标注预期输出或"示例/需验证"
- **NFR-4**: 版本提示明确（Hermes agent 持续演进，API/命令可能变化，以官方文档为准）
- **NFR-5**: 交叉链接正确，文件间引用使用相对路径，禁止 `file:///` 绝对路径
- **NFR-6**: frontmatter 字段与现有 wiki 保持一致，不添加额外无依据字段
- **NFR-7**: 三级标题使用 x.y 编号格式（1.1、2.3 等，从 x.1 开始）
- **NFR-8**: 不虚构未公开特性；所有命令/字段有官方文档或本地源码依据，或明确标注为"示例/需验证"

## Constraints
- **Technical**: 输出为纯 Markdown 文件 + YAML frontmatter，无额外依赖
- **Business**: 基于 Hermes 官方中文文档与本地源码整理，不虚构；命令与版本号有据可查
- **Dependencies**:
  - 参考现有 wiki 格式：`hermes-agent-integration/`、`echobird-wiki/`、`eve-wiki/`、`zleap-agent-wiki/`
  - 资料来源：<https://hermes-agent.nousresearch.com/docs/zh-Hans/>（官方中文文档）、`external/libs/hermes-agent/`（本地源码：README.zh-CN.md、AGENTS.md、website/docs/ 目录结构、核心 Python 文件）
  - 输出路径：`.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-wiki/`

## Assumptions
- 输出目录归类在 `03-agent-platforms-tools/` 下是合理的（Hermes 属 Agent 平台/工具）
- 原子化 wiki 结构（而非单文件）更适合 Hermes 这种内容丰富、章节独立性高的主题
- 现有原子化 wiki 的 frontmatter 格式（含 category/tags/date/status 等字段）是当前标准
- 面向中国开发者的中文语境解读，命令与示例保留英文原文
- 本任务是"学习/知识沉淀"类产出（knowledge-scenario），非源码改动
- 与既有的 hermes-agent-integration（SpecWeave 接入）形成互补：本教程聚焦 Hermes 本身，彼聚焦接入实践

## Acceptance Criteria

### AC-1: Wiki 目录结构完整
- **Given**: 教程创建完成
- **When**: 查看输出目录
- **Then**: 存在 `hermes-agent-wiki/` 目录，包含 README.md 和 00-0X 编号章节文件（8-11 篇）
- **Verification**: `programmatic`
- **Notes**: 验证文件存在和命名规范（kebab-case）

### AC-2: Frontmatter 格式合规
- **Given**: 每个章节文件
- **When**: 检查 frontmatter
- **Then**: 包含 id/title/source/description/tags/category/date/status 字段，格式与现有原子化 wiki 一致（YAML）
- **Verification**: `programmatic`

### AC-3: 产品定位与核心理念阐述清晰
- **Given**: 00-overview.md 或 01 章节
- **When**: 阅读产品定位部分
- **Then**: 清晰说明 Hermes 是 Nous Research 自进化 AI Agent、闭环学习、核心窄腰/能力在边缘
- **Verification**: `human-judgment`

### AC-4: 核心特性覆盖完整
- **Given**: 相关章节
- **When**: 阅读核心特性
- **Then**: 覆盖真正终端界面/随你所在/闭环学习/定时自动化/委派并行/随处运行/研究就绪
- **Verification**: `human-judgment`

### AC-5: 快速安装上手可实操
- **Given**: 快速上手章节
- **When**: 按步骤操作
- **Then**: 可以完成 curl/install.ps1 安装 → `hermes` 对话 → `hermes model/tools/config/setup` 的完整流程
- **Verification**: `human-judgment`
- **Notes**: 步骤清晰，命令完整可复制

### AC-6: CLI 与斜杠命令覆盖完整
- **Given**: CLI 章节
- **When**: 检查命令清单
- **Then**: 覆盖 `hermes <subcommand>` 主要子命令与常用斜杠命令（/model、/skills、/compress、/new 等）
- **Verification**: `programmatic`

### AC-7: 配置体系阐述清晰
- **Given**: 配置章节
- **When**: 阅读配置说明
- **Then**: 说明 config.yaml 顶层 section、.env 仅密钥、HERMES_HOME、profiles 多实例
- **Verification**: `human-judgment`

### AC-8: 消息网关与工具/技能/记忆系统覆盖完整
- **Given**: 相关章节
- **When**: 检查内容
- **Then**: 覆盖消息网关（多平台）、工具与工具集（Footprint Ladder）、技能系统（SKILL.md/curator）、记忆系统（provider/memory_manager）
- **Verification**: `human-judgment`

### AC-9: MCP/cron/委派并行覆盖完整
- **Given**: 相关章节
- **When**: 检查内容
- **Then**: 覆盖 MCP 集成、定时调度（cron 格式与命令）、委派与并行（delegate_task 单/批/角色）
- **Verification**: `human-judgment`

### AC-10: 架构解析与源码导读覆盖完整
- **Given**: 架构章节
- **When**: 阅读架构分析
- **Then**: 覆盖 AIAgent 核心循环、CLI/TUI/桌面架构、项目结构、插件系统，含代码/结构示例
- **Verification**: `human-judgment`

### AC-11: 术语表/FAQ/资源完整
- **Given**: 相关章节
- **When**: 检查内容
- **Then**: 术语表覆盖 Hermes/prompt caching/toolset/memory provider/skill/plugin/context engine 等；FAQ 覆盖常见问题；资源含官方链接
- **Verification**: `programmatic` + `human-judgment`

### AC-12: 交叉链接有效且索引更新
- **Given**: 所有章节文件
- **When**: 检查 markdown 链接
- **Then**: 文件间相对链接路径正确；与 hermes-okf-wiki / hermes-agent-integration 的交叉引用指向存在文件；03-agent-platforms-tools/README.md 已添加 hermes-agent-wiki 入口
- **Verification**: `programmatic`

### AC-13: Mermaid 图表正确（如使用）
- **Given**: 包含 Mermaid 图表的章节
- **When**: 渲染 Mermaid 代码
- **Then**: 图表语法正确，可正常渲染，清晰表达架构关系
- **Verification**: `human-judgment`

## Open Questions
- [ ] 章节数量定为 8 章（00-07）还是 11 章（00-10）？（取决于是否拆分"工具"与"技能/记忆"）
- [ ] 是否需要补充 Hermes 实际安装验证（受网络环境限制，建议以官方文档为准并标注"示例/需验证"）？
- [ ] 是否需要在教程中纳入"与 OpenClaw 迁移"章节（Hermes 官方提供 hermes claw migrate）？

## Impact
- **Affected specs**: `03-agent-platforms-tools/` Agent 平台知识体系；与 `hermes-agent-integration/`、`01-agent-protocols-interfaces/okf-wiki/hermes-okf-wiki/` 形成互补
- **Affected code**: 无源代码变更；仅新增知识文档 + 更新 03-agent-platforms-tools/README.md 索引
- **Affected docs**: `.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-wiki/`（新建）、`03-agent-platforms-tools/README.md`（更新索引）
