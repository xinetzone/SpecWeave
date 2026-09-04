---
version: "1.0"
---

# DeepSeek Harness Wiki 教程 Spec

## Why

2026年8月13日，DeepSeek发布并开源了Agent驾驭框架 **DeepSeek Harness (dsh)** v0.1开发者预览版，采用MIT协议，以"一切皆插件"的架构哲学和Cordis元框架引发行业关注——发布12小时GitHub star破5万，两天超10万，被视为Agent界的Android。

当前知识库中尚无DeepSeek Harness的系统性教程，而该项目代表了Agent架构的重要范式跃迁：从"成品Agent"到"可扩展Agent操作系统内核"，其Cordis插件机制、会话日志即真相源、Capability Seam抽象等设计理念对Agent工程具有重要参考价值。

本教程基于9个权威来源（官方文档、Tony Bai深度技术分析、deepseekagent.io实用指南、新浪财经商业分析、极客公园产品评测、GitHub官方仓库）系统性学习并沉淀wiki教程，覆盖从快速上手到架构理解、从使用到插件开发的完整知识层。

## What Changes

- **新增** 1个原子化wiki目录：`docs/knowledge/ai/deepseek-harness/`
- **新增** 教程总览与快速导航（`00-overview.md`）
- **新增** 项目介绍与背景（`01-introduction-background.md`），覆盖Harness是什么、为什么重要、发布背景、行业定位
- **新增** 环境准备与安装（`02-installation-setup.md`），覆盖Node.js版本要求、API Key准备、启动命令、配置目录结构
- **新增** 快速上手：第一个任务（`03-quickstart-first-task.md`），覆盖Web UI使用、工作区选择、模型配置、运行第一个任务
- **新增** 四种运行模式详解（`04-four-modes.md`），覆盖Standard/Code(PTC)/Minimal/Creator四种模式的适用场景与能力差异
- **新增** 核心架构：一切皆插件（`05-architecture-everything-plugin.md`），覆盖Cordis元框架、无特权内核设计、Profile与Bundle分层机制
- **新增** Agent循环与事件模型（`06-agent-loop-events.md`），覆盖Turn/Step模型、三类事件系统、瀑布型事件拦截机制
- **新增** 会话日志与可观测性（`07-session-log-observability.md`），覆盖append-only日志设计、Trajectory轨迹视图、分叉/回放/恢复机制
- **新增** 模型配置与多模型支持（`08-model-configuration.md`），覆盖DeepSeek默认模型配置、多Provider接入、自定义模型配置
- **新增** 工具系统与Capability Seam（`09-tools-capability-seam.md`），覆盖内置工具、Capability Seam抽象、Service Definition/Provider/Consumer三角色
- **新增** 插件开发入门（`10-plugin-development.md`），覆盖插件结构、注册机制、可逆效应、简单插件示例
- **新增** 与Claude Code/Codex/MCP生态互操作（`11-ecosystem-interop.md`），覆盖hooks兼容、MCP支持、AGENTS.md/CLAUDE.md读取、委托机制
- **新增** 无头模式与SDK使用（`12-headless-sdk.md`），覆盖headless模式、Python SDK、JSON-RPC、ACP服务端
- **新增** 常见问题与故障排查（`13-faq-troubleshooting.md`），覆盖Node版本/端口/权限/Windows兼容性等常见问题
- **新增** 适用场景与风险提示（`14-use-cases-limitations.md`），覆盖适用/不适用场景、预览版风险、生产 readiness 评估
- **新增** 生态与资源链接（`15-ecosystem-resources.md`），覆盖官方资源、社区插件、相关文章、对比参考
- **更新** `docs/knowledge/ai/README.md` 导航（新增deepseek-harness条目）
- **不修改** 任何现有wiki文档内容（仅README追加导航条目）

## Impact

- **Affected specs**: 无（独立新增wiki教程）
- **Affected code**: 无代码改动，仅文档新增
- **Affected files**:
  - 新增：`docs/knowledge/ai/deepseek-harness/00-overview.md` ~ `15-ecosystem-resources.md` 共16个文件
  - 更新：`docs/knowledge/ai/README.md`（追加子目录导航条目）
- **Related wikis**: 后续可关联Agent工程、Harness设计模式、插件架构等相关主题

## Background & Context

DeepSeek Harness (dsh) 是DeepSeek于2026年8月13日开源的Agent驾驭框架，核心设计要点：

1. **架构哲学**："一切皆插件"——基于Cordis元框架，模型/工具/Agent循环本身都是插件，无特权内核
2. **分层配置**：Profile（配置档案）+ Bundle（能力捆绑包）实现类似乐高的能力组装
3. **事件模型**：Agent循环拆解为Turn/Step，三类事件（会话/Agent/能力）支持瀑布型拦截
4. **可观测性**：会话日志是唯一真相源（append-only），强制"模型看到的必须写进日志"，支持Trajectory轨迹、分叉、回放
5. **Capability Seam**：Service Definition/Provider/Consumer三角色抽象，一次替换全局生效
6. **四种模式**：Standard（完整）/ Code（程序化工具调用）/ Minimal（极简评测）/ Creator（定制模式）
7. **多模型支持**：默认DeepSeek V4 Pro/Flash，支持Anthropic/OpenAI/Bedrock/Azure/Vertex + 自定义Provider
8. **生态兼容**：兼容Claude Code/Codex hooks，支持MCP协议，读取AGENTS.md/CLAUDE.md
9. **本地优先**：仅设计为本地服务，CLI拒绝`--host 0.0.0.0`，数据全部存储在`~/.dsh/`
10. **当前状态**：v0.1开发者预览版，明确警告会有破坏性变更，不建议生产使用

本教程基于9个权威来源：
1. https://tonybai.com/2026/08/14/deepseek-harness-everything-is-a-plugin/ — Tony Bai深度技术分析
2. https://deepseekagent.io/zh/guides/deepseek-harness — deepseekagent.io实用指南
3. https://developer.cloud.tencent.com/article/2726629 — 腾讯云开发者社区
4. https://finance.sina.com.cn/stock/wbstock/2026-08-15/doc-ininmane3342332.shtml — 新浪财经商业分析
5. https://news.qq.com/rain/a/20260814A0725C00 — 极客公园产品评测
6. https://github.com/deepseek-ai/deepseek-harness — GitHub官方仓库
7. https://deepseek.com/harness — DeepSeek官方页面
8. https://www.msn.cn/.../tencent-qq-bot — QQ Bot接入新闻
9. https://www.msn.com/.../deepseek-v4-pro — V4 Pro上线国家超算互联网新闻

教程采用原子化文档结构，遵循项目已有wiki规范（参照mermaid-wiki、tvm-ffi-wiki等），每个文档聚焦单一主题，前置YAML frontmatter，包含章节导航。

## ADDED Requirements

### Requirement: Wiki教程目录与总览

The system SHALL provide a `00-overview.md` file at `docs/knowledge/ai/deepseek-harness/` containing complete tutorial overview.

#### Scenario: 用户访问DeepSeek Harness wiki入口

- **WHEN** 用户打开 `deepseek-harness/00-overview.md`
- **THEN** 文档包含：教程简介、目标读者、16章导航表、学习路径建议（入门→使用→架构→进阶）、核心概念速览、与其他Agent框架的对比

### Requirement: 项目介绍与背景

The system SHALL provide a `01-introduction-background.md` file covering Harness定位、发布背景、行业意义。

#### Scenario: 用户了解Harness是什么

- **WHEN** 用户阅读本章
- **THEN** 文档包含：Agent = Model + Harness的核心定位、发布时间线与star增长数据、与Claude Code/Codex的本质区别、"Agent界的Android"战略意义、开源协议与商业模式

### Requirement: 环境准备与安装

The system SHALL provide a `02-installation-setup.md` file covering environment requirements and installation.

#### Scenario: 用户完成环境准备并启动dsh

- **WHEN** 用户按文档操作
- **THEN** 文档包含：Node.js版本要求（^22.19 || >=24）及安装方法、DeepSeek API Key获取方式、npx一键启动命令、源码构建步骤、~/.dsh配置目录结构说明、3080端口说明

### Requirement: 快速上手：第一个任务

The system SHALL provide a `03-quickstart-first-task.md` file covering Web UI basic usage.

#### Scenario: 用户运行第一个Agent任务

- **WHEN** 用户按文档操作
- **THEN** 文档包含：Web UI界面介绍、工作区选择（Choose workspace）、模型配置（Settings → Models填入API Key）、第一个任务示例（总结仓库/重构代码等）、实时统计面板解读、权限审批弹窗说明

### Requirement: 四种运行模式详解

The system SHALL provide a `04-four-modes.md` file covering four runtime modes in detail.

#### Scenario: 用户理解不同模式的适用场景

- **WHEN** 用户阅读本章
- **THEN** 文档包含：四种模式对比表、Standard模式能力清单、Code(PTC)模式（程序化工具调用，减少轮次）、Minimal模式（仅bash+str_replace_editor，用于评测）、Creator模式（运行时自省+插件试验）

### Requirement: 核心架构：一切皆插件

The system SHALL provide a `05-architecture-everything-plugin.md` file covering Cordis元框架与插件架构。

#### Scenario: 用户理解"一切皆插件"架构哲学

- **WHEN** 用户阅读本章
- **THEN** 文档包含：Cordis元框架介绍（时空可组合性论文）、无特权内核设计原则、可逆效应（reversible effects）、Bundle分发格式、Profile配置档案、分层叠加与补丁机制、--dump-config查看实际插件树

### Requirement: Agent循环与事件模型

The system SHALL provide a `06-agent-loop-events.md` file covering Turn/Step model and event system.

#### Scenario: 用户理解Agent循环机制

- **WHEN** 用户阅读本章
- **THEN** 文档包含：Step定义（一次模型请求+工具调用）、Turn定义（零到多个Step）、典型回合流程、三类事件详解（会话事件/Agent事件/能力事件）、瀑布型事件（waterfall）与next()机制、agent/pre-step等关键拦截点、Loop本身也是插件

### Requirement: 会话日志与可观测性

The system SHALL provide a `07-session-log-observability.md` file covering session log and Trajectory view.

#### Scenario: 用户利用日志进行调试与复盘

- **WHEN** 用户阅读本章并使用Trajectory
- **THEN** 文档包含："模型看到的必须写进日志"硬性规则、append-only SessionEvent流、deriveMessages()投射机制、Trajectory轨迹视图使用（查看系统提示词/思维链/工具调用/子Agent调度）、分叉（fork）/恢复（resume）/回放机制

### Requirement: 模型配置与多模型支持

The system SHALL provide a `08-model-configuration.md` file covering model configuration and multi-provider support.

#### Scenario: 用户配置不同模型供应商

- **WHEN** 用户按文档配置
- **THEN** 文档包含：默认模型（deepseek-v4-pro/flash）参数配置（100万上下文/256k输出/三档思考强度）、API Key配置与凭证安全、添加Anthropic/OpenAI/Bedrock/Azure/Vertex等内置Provider、自定义Provider配置（Provider ID/Base URL/协议/模型列表）、视觉模型input配置

### Requirement: 工具系统与Capability Seam

The system SHALL provide a `09-tools-capability-seam.md` file covering tool system and capability seam abstraction.

#### Scenario: 用户理解能力替换机制

- **WHEN** 用户阅读本章
- **THEN** 文档包含：内置工具清单（文件编辑/shell/搜索/skills/计划/目标/子Agent等）、Capability Seam三角色（Service Definition/Provider/Consumer）、"一次替换，全局生效"设计价值、文件系统+子进程共享执行世界示例、子Agent provider切换示例

### Requirement: 插件开发入门

The system SHALL provide a `10-plugin-development.md` file covering basic plugin development.

#### Scenario: 用户开发第一个dsh插件

- **WHEN** 用户按文档开发
- **THEN** 文档包含：插件结构概述、Cordis插件注册方法、事件监听示例、可逆效应实现、简单插件示例（如自定义工具/UI主题）、dsh-plugin标签与社区发现机制

### Requirement: 与Claude Code/Codex/MCP生态互操作

The system SHALL provide a `11-ecosystem-interop.md` file covering ecosystem compatibility.

#### Scenario: 用户在dsh中复用现有生态

- **WHEN** 用户阅读本章
- **THEN** 文档包含：Claude Code hooks桥接与hooks.json复用、Codex兼容、MCP客户端支持、AGENTS.md/CLAUDE.md读取规则、任务委托给本机Claude Code/Codex（默认关闭）

### Requirement: 无头模式与SDK使用

The system SHALL provide a `12-headless-sdk.md` file covering headless mode and SDKs.

#### Scenario: 用户在程序中嵌入dsh

- **WHEN** 用户按文档集成
- **THEN** 文档包含：--profile headless一次性执行任务、Python SDK使用（pip install deepseek-harness-sdk，自带Node运行时）、JSON-RPC SDK、ACP服务端、嵌入自己的程序示例

### Requirement: 常见问题与故障排查

The system SHALL provide a `13-faq-troubleshooting.md` file covering common issues.

#### Scenario: 用户排查常见问题

- **WHEN** 用户查阅FAQ
- **THEN** 文档包含：不少于10个常见问题（Node版本错误/3080端口占用/MISSING_CREDENTIAL/UNKNOWN_MODEL/输入框灰色/Windows PTY限制等）及解决方案

### Requirement: 适用场景与风险提示

The system SHALL provide a `14-use-cases-limitations.md` file covering use cases and risk warnings.

#### Scenario: 用户评估是否适合自己的场景

- **WHEN** 用户阅读本章
- **THEN** 文档包含：适用场景表（官方编程Agent/可控运行时/模型评测/内部平台等）、不适用场景表（立即上生产/非技术用户/团队协作SaaS等）、v0.1预览版破坏性变更风险、会话格式兼容性警告、本地服务限制（不支持0.0.0.0远程访问）、Windows平台限制

### Requirement: 生态与资源链接

The system SHALL provide a `15-ecosystem-resources.md` file covering ecosystem resources.

#### Scenario: 用户查找更多资源

- **WHEN** 用户查阅本章
- **THEN** 文档包含：官方资源链接（GitHub/官网/API文档/Cordis仓库）、社区插件生态示例、推荐阅读文章列表、同类Harness框架对比参考

## Data Sources

学习材料来源：

1. https://tonybai.com/2026/08/14/deepseek-harness-everything-is-a-plugin/ — Tony Bai深度技术分析，架构解读最权威
2. https://deepseekagent.io/zh/guides/deepseek-harness — deepseekagent.io实用指南，实测版本0.1.0-rc.6，上手步骤最详细
3. https://github.com/deepseek-ai/deepseek-harness — GitHub官方仓库，源码与README权威来源
4. https://news.qq.com/rain/a/20260814A0725C00 — 极客公园产品评测，实测体验与生态观察
5. https://finance.sina.com.cn/stock/wbstock/2026-08-15/doc-ininmane3342332.shtml — 新浪财经商业分析，战略定位与行业影响
6. https://developer.cloud.tencent.com/article/2726629 — 腾讯云开发者社区
7. https://deepseek.com/harness — DeepSeek官方产品页面
8. QQ Bot官宣接入DeepSeek Harness相关新闻（生态扩展）
9. DeepSeek V4 Pro上线国家超算互联网相关新闻（应用落地）

<!-- changelog -->
<!--
- 2026-08-16 | initial | 初始版本，定义16章原子化文档的完整Requirements
-->
