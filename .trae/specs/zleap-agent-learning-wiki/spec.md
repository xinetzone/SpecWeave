# Zleap-Agent 学习 Wiki 教程 Spec

## Why
Zleap-Agent 是一个 **workspace-first** 的 Agent Harness（面向本地模型与 OpenAI-compatible 模型），其核心命题是"Agent 不应在每一步都看到所有工具、记忆、规则与历史，而应先在知道自己身处哪个 Workspace 后，只拿到该 Workspace 真正需要的上下文"。它把运行时按 Workspace 拆分，每个 Workspace 拥有独立的提示词、工具、技能、记忆、模型与执行历史，对本地小模型、企业内网部署与权限/数据边界敏感的工作流有重要参考价值。需要系统学习其源码与文档，沉淀为一份结构清晰、通俗易懂的 wiki 教程，便于不同技术水平的读者理解这套 workspace-first 的 Agent 运行时设计，并为后续架构讨论或借鉴提供参考。

## What Changes
- 新增 wiki 教程文档集 `.agents/docs/knowledge/learning/03-agent-platforms-tools/zleap-agent-wiki/`，作为 Zleap-Agent 的系统性学习资料
- 文档集包含 `README.md` 索引 + 8 章递进式教程（00 概览 → 05 网关任务 → 07 快速上手 → 08 FAQ）
- 覆盖核心概念（Workspace 隔离 / Context 组装 / 分区记忆 / Skill / 权限 / 模型提供方 / 网关 / 任务 / 会话服务）
- 从源码深读中提炼 5-8 条架构洞察
- 在 `.agents/docs/knowledge/learning/03-agent-platforms-tools/README.md` 中登记新增文档条目
- **BREAKING**: 无破坏性变更（纯新增学习文档）

## Impact
- Affected specs: 无（独立新增学习文档）
- Affected code:
  - 新增 `.agents/docs/knowledge/learning/03-agent-platforms-tools/zleap-agent-wiki/` 目录（README.md + 8 章）
  - 修改 `.agents/docs/knowledge/learning/03-agent-platforms-tools/README.md`（追加索引条目）

## Background & Context
- **项目名称**: Zleap-Agent（GitHub: Zleap-AI/Zleap-Agent）
- **版本基准**: v0.3.3（package.json）
- **核心宣称**: "Workspace Is All Agents Need"
- **核心机制**: `Context = System Prompt + Workspace Prompt + Tools + Memory + History`
- **Workspace 存储**: 工作区存在于数据库（唯一真源），代码中无硬编码；内置默认由 seed 派生，`main`（常驻主空间，运行时 id 为 `session`）与 `work`（派发子空间）
- **上下文组装**: 稳定块（systemPrompt = persona + rules + space + impressions）→ 半稳定块（有界事件窗口 + 保留轮次）→ 可变块（近期轮次 + 匹配召回），并声明缓存断点；不变量"变化的记忆永不进入缓存前缀"
- **记忆分区**: person（impressions）/ event（work records）/ experience（经验），PostgreSQL 存储，A 线（people notes，无模型）+ B 线（core records 抽取/召回），RRF（Reciprocal Rank Fusion）多路径召回融合
- **Skill**: 以 `SKILL.md` 为入口的可复用能力包，含敏感性审计、token 预算、章节索引、调用策略、信任状态
- **权限**: `request_approval`（默认）/ `full_access` 两种模式
- **模型提供方**: OpenAI-compatible + Anthropic，ProviderRegistry/ModelRegistry，SSE 流式
- **对外入口**: Web UI（Next.js）、CLI（与 Web 同 runtime）、IM 网关（飞书/微信）、定时任务 Worker
- **本地源码**: `d:\spaces\SpecWeave\external\libs\Zleap-Agent`

## ADDED Requirements

### Requirement: Wiki 教程文档集主框架
系统 SHALL 提供一份 Markdown 格式的 wiki 教程文档集，放置在 `.agents/docs/knowledge/learning/03-agent-platforms-tools/zleap-agent-wiki/`，其中 `README.md` 作为索引，包含标题、适用人群、章节快速导航表、内容快照声明、资源链接；每章文档遵循分文件命名（`00-*.md`、`01-*.md`…），顶部含 YAML frontmatter，底部含上一章/返回目录/下一章导航。

#### Scenario: 用户打开教程索引
- **WHEN** 用户打开 `zleap-agent-wiki/README.md`
- **THEN** 展示完整目录导航，覆盖 8 章章节的锚点链接
- **AND** 每个章节文件可点击跳转，且每章底部有上一章/返回目录/下一章导航

### Requirement: 项目概述与核心定位章节（00）
系统 SHALL 阐述 Zleap-Agent 的项目定位、核心哲学（workspace-first）、项目背景（版本、仓库、许可状态）、核心宣称与原理解读。

#### Scenario: 读者理解项目定位
- **WHEN** 读者阅读 00 章节
- **THEN** 能复述"Workspace Is All Agents Need"的核心命题
- **AND** 理解"Agent 先知道自己身处哪个 Workspace，再只拿到该 Workspace 需要的上下文"这一设计

### Requirement: 核心架构与技术栈章节（01）
系统 SHALL 讲解 Zleap-Agent 的整体架构与 13 个 package 的职责（agent/core/store/ai/web/cli/gateway/tasks/host/runtime/avatar/desktop），并说明 monorepo 结构、构建工具（pnpm、TypeScript）与后端存储（PostgreSQL + pgvector）。

#### Scenario: 读者把握整体架构
- **WHEN** 读者阅读 01 章节
- **THEN** 能说出每个 package 的核心职责
- **AND** 理解架构分层（模型提供方 / 核心运行时 / 会话服务 / 网关 / 存储）

### Requirement: Workspace 隔离机制与上下文组装章节（02）
系统 SHALL 深入讲解 Workspace 的代码实现：`main`/`work` 空间、数据库为唯一真源、`when`/`notFor` 路由提示、`persona` 系统提示词、`toolIds` 工具白名单，以及 Kernel 从 `session` 空间经 `switchWorkspace(space, task)` 路由到子空间的机制；同时讲解 `assembleContext` 的三块上下文组装（stable/semiStable/variable）与缓存断点、以及"变化的记忆永不进入缓存前缀"的不变量。

#### Scenario: 读者理解隔离机制
- **WHEN** 读者阅读 02 章节
- **THEN** 能解释 Workspace 如何在代码层面隔离 prompt/tools/memory/history
- **AND** 能复述上下文组装的稳定/半稳定/可变三块结构

### Requirement: 分区记忆系统章节（03）
系统 SHALL 讲解 Zleap-Agent 的分区记忆：person（impressions）、event（work）、experience（经验）三类记忆；A 线（people notes，无模型）+ B 线（core records 抽取/召回）双线；prefetch 快速读取（无 LLM）与 recall 精排（LLM）的区别；RRF（Reciprocal Rank Fusion）多路径召回融合算法；抽取管线（LLM 抽取器 → event + 实体，content_hash 幂等）。

#### Scenario: 读者理解记忆机制
- **WHEN** 读者阅读 03 章节
- **THEN** 能解释三类记忆分区与两条写入线
- **AND** 能说明 RRF 如何融合多路径召回结果

### Requirement: Skill / 工具 / 权限章节（04）
系统 SHALL 讲解 Skill 机制（SKILL.md 入口、SkillRegistry、敏感性审计、token 预算、调用策略、信任状态）、工具权限模型（`request_approval` / `full_access`）、MCP Runtime 与 MCP Secrets 机制。

#### Scenario: 读者理解 Skill 与权限
- **WHEN** 读者阅读 04 章节
- **THEN** 能解释 Skill 与工具（API）的区别
- **AND** 能说明两种权限模式的行为差异

### Requirement: 模型提供方与对外入口章节（05）
系统 SHALL 讲解模型提供方抽象（OpenAI-compatible + Anthropic，ProviderRegistry/ModelRegistry，SSE 流式）、Web UI（Next.js）与 CLI 的入口、`ConversationService` 作为所有触发（web/tasks/IM）的统一入口与 inbound → reply → 流式回传的数据流。

#### Scenario: 读者理解运行时与入口
- **WHEN** 读者阅读 05 章节
- **THEN** 能说出模型提供方的注册与调用方式
- **AND** 能描绘从 inbound 消息到流式回复的完整数据流

### Requirement: 网关与定时任务章节（06）
系统 SHALL 讲解 IM 网关（飞书/微信/飞书 CLI 适配器、ChannelSupervisor、worker、dedup）与定时任务服务（cron、queue、worker、service），以及它们如何接入 `ConversationService`。

#### Scenario: 读者理解网关与任务
- **WHEN** 读者阅读 06 章节
- **THEN** 能理解外部渠道（飞书/微信）如何接入 agent
- **AND** 能说明定时任务如何触发 agent 运行

### Requirement: 快速上手指南章节（07）
系统 SHALL 提供从源码快速启动的完整步骤：环境要求、安装依赖、启动 Web UI、配置模型、CLI 使用、常用命令、环境变量表。

#### Scenario: 读者按指南上手
- **WHEN** 读者按 07 章节操作
- **THEN** 能完成环境安装、依赖安装、启动 Web UI 或 CLI
- **AND** 能配置 OpenAI-compatible 模型并运行一次对话

### Requirement: FAQ 与术语表章节（08）
系统 SHALL 提供 FAQ 章节解答常见问题，并提供 ≥10 个核心术语的通俗解释表（Workspace、Context Layout、Person/Event/Experience Memory、Skill、RRF、MCP、Gateway、Turn Loop、Approval 等）。

#### Scenario: 读者疑问被解答
- **WHEN** 读者查阅 FAQ 与术语表
- **THEN** 至少 6 个常见问题被解答
- **AND** 术语表覆盖 ≥10 个核心术语

### Requirement: 架构洞察提炼
系统 SHALL 在教程中提炼 5-8 条从源码深读中获得的架构洞察（如"数据库是工作区唯一真源，代码零硬编码"、"变化的记忆永不进入缓存前缀"、"所有触发统一走 ConversationService"、"Main→work 深度为 1"等），以提升教程的深度价值。

#### Scenario: 读者获得深层洞察
- **WHEN** 读者阅读相关章节
- **THEN** 能获得非表面化、源于源码的架构洞察
- **AND** 洞察与源码文件路径可追溯

### Requirement: 知识库索引登记
系统 SHALL 在 `.agents/docs/knowledge/learning/03-agent-platforms-tools/README.md` 的对应类目下登记新增的 Zleap-Agent 学习文档条目。

#### Scenario: 索引可发现
- **WHEN** 用户浏览 `03-agent-platforms-tools/README.md`
- **THEN** 能看到 Zleap-Agent 学习 wiki 的条目
- **AND** 条目包含文档标题与相对路径链接

## Non-Functional Requirements
- **NFR-1**: 文档语言使用标准现代汉语，逻辑严谨，对不同技术水平的读者友好
- **NFR-2**: 内容基于实际源码与 README，不添加未经验证的信息；引用具体源码文件路径作为依据
- **NFR-3**: 文档使用 Markdown 标准标题层级（H1/H2/H3）、列表、表格、引用块；每章含 YAML frontmatter
- **NFR-4**: 文件命名遵循 kebab-case 纯英文规范（如 `00-overview.md`、`zleap-agent-wiki`）
- **NFR-5**: 文档集篇幅适中，重点突出，避免冗余；每章聚焦单一主题

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范与原子化原则
- **Business**: 基于公开 GitHub 仓库内容创建，不添加未验证的推测性信息；不改动 Zleap-Agent 仓库内任何文件
- **Dependencies**: 源码深读已完成（覆盖 README、package.json 及 10+ 核心源码文件）

## Assumptions
- 读者对 Agent / LLM / Workspace 概念有基础认知
- 读者可访问 GitHub 或本地源码深入阅读
- 读者对 Agent 运行时设计有兴趣或借鉴需求

## Acceptance Criteria

### AC-1: Wiki 教程文档集创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: `03-agent-platforms-tools/zleap-agent-wiki/` 包含 README.md 索引 + 8 章教程，覆盖概览、架构、Workspace、记忆、Skill/权限、运行时入口、网关任务、快速上手、FAQ
- **Verification**: `human-judgment`

### AC-2: 目录导航系统可用
- **Given**: 用户打开 README.md
- **When**: 用户查看章节导航
- **Then**: 目录包含所有章节的锚点链接，每章底部有上一章/返回目录/下一章导航
- **Verification**: `programmatic`

### AC-3: 核心概念讲解完整
- **Given**: 用户阅读教程
- **When**: 用户按顺序阅读 Workspace、Context、Memory、Skill、权限章节
- **Then**: 用户能阐述每个核心概念的定位与实现机制
- **Verification**: `human-judgment`

### AC-4: 架构洞察有深度
- **Given**: 用户阅读教程
- **When**: 用户检查洞察内容
- **Then**: 教程包含 5-8 条源于源码的架构洞察，且可追溯源码路径
- **Verification**: `human-judgment`

### AC-5: 快速上手可操作
- **Given**: 用户按快速上手章节操作
- **When**: 用户执行安装与启动命令
- **Then**: 命令与步骤与 README 一致，可完成环境搭建
- **Verification**: `programmatic`

### AC-6: FAQ 与术语表实用
- **Given**: 用户遇到疑问
- **When**: 用户查阅 FAQ 与术语表
- **Then**: FAQ 至少 6 个问题，术语表 ≥10 个核心术语
- **Verification**: `human-judgment`

### AC-7: 知识库索引已登记
- **Given**: wiki 文档集创建完成
- **When**: 用户浏览 `03-agent-platforms-tools/README.md`
- **Then**: 对应类目下出现 Zleap-Agent 学习文档条目
- **Verification**: `programmatic`

### AC-8: 文件命名规范合规
- **Given**: wiki 文档集创建完成
- **When**: 检查文件命名
- **Then**: 所有文件遵循 kebab-case 纯英文规范（`00-*.md`、`README.md`）
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要为 Context 组装与 Workspace 路由添加 Mermaid 流程图？（倾向：加入 1-2 张图增强可读性）
- [ ] 是否需要加入 RRF 召回算法的示意图？（倾向：用文字 + 公式说明，避免绘制不准确的示意图）