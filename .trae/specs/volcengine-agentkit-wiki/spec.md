---
version: "1.0"
source: "seven-concepts: knowledge-scenario"
category: "learning"
---
# 火山引擎 AgentKit Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 基于火山引擎官方产品文档和开发者资源，系统梳理 AgentKit 企业级 AI Agent 基础设施平台的产品全貌、核心架构、VeADK 开发框架、SDK/CLI 工具链、应用场景与最佳实践，形成一套从入门到精通的结构化 wiki 教程。
- **Purpose**: 解决"能跑起来但难上线、能调用但难治理"的企业智能体工程化痛点，为开发者和技术决策者提供 AgentKit 产品体系的完整认知框架、快速上手路径和深度集成指南，降低从 Demo 走向生产的工程复杂度。
- **Target Users**: 
  - AI 应用开发者（需要快速构建和部署企业级智能体）
  - 架构师与技术决策者（评估 AgentKit 与现有技术栈的融合方案）
  - 平台工程师（负责智能体平台化建设与治理）
  - 产品经理（理解 AI Agent 工程化能力边界）

## Goals
- 提供 AgentKit 产品体系的全景认知：平台定位、核心价值、8 大功能模块
- 详解 VeADK（Volcengine Agent Development Kit）三语言 SDK 的安装、核心 API 与典型开发范式
- 覆盖 AgentKit SDK & CLI 的项目初始化、三种部署模式（Local/Hybrid/Cloud）、一键构建部署流程
- 梳理 4 大典型应用场景的落地方案（员工助手/业务系统改造/多Agent编排/生产级平台化交付）
- 建立与现有知识库的交叉引用（MCP 协议、A2A 协议、智能体七大组件、可观测性体系）
- 提炼可复用的「AI Agent 平台选型评估框架」与「存量系统智能化改造模式」

## Non-Goals (Out of Scope)
- 不编写可执行的生产代码（仅提供说明性代码示例）
- 不替代火山引擎官方文档的更新维护职责（内容为快照性质，标注更新时间）
- 不涉及付费咨询级别的深度定制方案（仅提供公开产品能力的结构化梳理）
- 不涵盖火山方舟（Ark）大模型平台、Viking 向量数据库等独立产品的完整教程（通过交叉引用关联）
- 不包含产品定价、商务条款、SLA 承诺等时效性强的商业信息

## Background & Context
### 产品定位
火山引擎 AgentKit 是面向企业与开发者的智能体（Agent）构建与运行平台，提供从代码侧开发到云端托管运行的全生命周期能力。随着企业将智能体引入业务流程，普遍遇到以下工程化挑战：
1. 权限边界不清：用户身份、智能体身份、工具访问权限缺乏统一治理
2. 工具接入分散：各业务系统 API 缺乏标准化接入层，改造成本高
3. 缺少可观测与审计链路：问题定位困难，无法区分模型/运行时/工具/知识库的异常来源
4. 上线后排障与质量评估成本高：缺少标准化评测体系与发布闸门

AgentKit 将上述能力标准化沉淀为 8 大平台组件：Runtime / Identity / Gateway / A2A / Session&Memory / Knowledge / Observability / Evaluation。

### 技术生态
- **VeADK Family**: 与 Google ADK 完全兼容的智能体开发套件，支持 Python/Go/Java 三语言
- **AgentKit SDK & CLI**: 基于装饰器的优雅 API，支持三种部署模式，一键构建部署到 Runtime
- **火山引擎产品融合**: 与火山方舟（大模型）、Viking DB（向量库）、VeFaaS（函数服务）、APMPlus（可观测）、TLS（日志服务）等 20+ 产品深度集成
- **开源协议**: veadk-python/veadk-go/veadk-java 均在 GitHub 开源，接受社区贡献

### 内容敏感度
火山引擎官网为公开产品页面，官方文档与 GitHub 开源仓库均为公开可访问内容，本教程属于 **Public（公开内容）** 级别，遵循标准工作流，产出物位于 `.agents/docs/knowledge/learning/03-agent-platforms-tools/volcengine-agentkit-wiki/`。

## Functional Requirements

### FR-1: 教程总览与知识地图
The system SHALL provide a `00-overview.md` file containing the complete tutorial structure, reading paths, AgentKit product ecosystem map (Mermaid), and cross-reference matrix with existing knowledge base wikis.

#### Scenario: 新读者访问教程入口
- **When**: 用户打开 `volcengine-agentkit-wiki/00-overview.md`
- **Then**: 文档包含：教程简介与目标读者、10 章导航表、AgentKit 产品生态全景图（Mermaid 组件关系图）、三条阅读路径（快速上手/深度开发/架构决策）、与现有 6+ 相关 wiki 的交叉引用矩阵

### FR-2: 产品介绍与核心概念
The system SHALL provide a `01-product-intro.md` file explaining AgentKit's definition, 8 core functional modules, value proposition, and target problems.

#### Scenario: 读者理解产品定位
- **When**: 用户阅读 `01-product-intro.md`
- **Then**: 文档包含：Wikipedia 风格产品定义、企业智能体工程化 4 大痛点分析、8 大功能模块详解（Runtime/Identity/Gateway/A2A/Session-Memory/Knowledge/Observability/Evaluation）、4 大产品优势（敏捷开发/生产就绪/开放兼容/成本优化）、产品发展时间线（Mermaid）

### FR-3: 产品架构与核心能力
The system SHALL provide a `02-core-architecture.md` file covering the AgentKit platform architecture, dynamic Harness orchestration, serverless runtime base, security permission model, and evaluation observability system.

#### Scenario: 架构师理解平台架构
- **When**: 用户阅读 `02-core-architecture.md`
- **Then**: 文档包含：Agent Ready 基础设施分层架构图（Mermaid）、动态 Harness 编排详解（配置即部署/热切换/复杂任务调度）、Serverless 运行底座（秒级扩缩容/多租户隔离/内置工具集）、安全防护三层模型（身份管控/云身份管控/内容护栏）、评测与可观测闭环（多维度评估/运行追踪/满意度分析）

### FR-4: VeADK 智能体开发框架
The system SHALL provide a `03-veadk-framework.md` file covering the VeADK (Volcengine Agent Development Kit) installation, core architecture, 3-language SDK, and ecosystem integration matrix.

#### Scenario: 开发者准备开发环境
- **When**: 用户阅读 `03-veadk-framework.md`
- **Then**: 文档包含：VeADK 定位（与 Google ADK 兼容说明）、Python/Go/Java 三语言安装命令与镜像地址、VeADK Family 产品融合矩阵（20+ 火山引擎产品映射表格）、DeepResearch 构建特性（多模型兼容/记忆知识库/内置工具/可观测评测/云原生部署/企业安全）、GitHub 开源仓库地址

### FR-5: AgentKit SDK & CLI 工具链
The system SHALL provide a `04-agentkit-sdk-cli.md` file covering the SDK API design, CLI commands, 3 deployment modes, and platform service integration.

#### Scenario: 开发者掌握工具链使用
- **When**: 用户阅读 `04-agentkit-sdk-cli.md`
- **Then**: 文档包含：装饰器式 API 设计（`@app.entrypoint` 代码示例）、CLI 全命令清单（init/config/build/deploy/launch）、三种部署模式对比表（Local/Hybrid/Cloud）、Platform 服务集成说明（Memory/Knowledge/MCP Gateway）

### FR-6: 快速入门指南
The system SHALL provide a `05-quickstart.md` file presenting a complete step-by-step quick start guide from environment setup to first agent deployment.

#### Scenario: 开发者 15 分钟快速上手
- **When**: 用户阅读 `05-quickstart.md`
- **Then**: 文档包含：前置条件清单（火山引擎账号/实名认证/权限开通）、5 步标准上手指南（环境安装→项目初始化→配置参数→构建部署→调用测试）、每步命令示例与预期输出、常见错误排查清单（≥5 个常见问题）

### FR-7: 应用场景与落地方案
The system SHALL provide a `06-application-scenarios.md` file detailing 4 typical enterprise scenarios with implementation architecture and key steps.

#### Scenario: 决策者匹配业务场景
- **When**: 用户阅读 `06-application-scenarios.md`
- **Then**: 文档包含：4 大场景详解（企业员工助手/业务系统智能化改造/多Agent编排与复杂工作流/生产级AI应用平台化交付），每个场景含：场景描述、参考架构图（Mermaid）、关键能力映射、实施步骤清单；3 大行业落地案例框架（泛互联网科技/零售电商/制造业）；通用标准化场景 vs 业务定制化场景的选型决策树

### FR-8: 核心功能深度解析
The system SHALL provide a `07-core-features-detailed.md` file offering deep dives into Identity/Gateway/A2A/Session-Memory/Knowledge modules with integration patterns.

#### Scenario: 深度集成开发
- **When**: 用户阅读 `07-core-features-detailed.md`
- **Then**: 文档包含：Identity 统一鉴权详解（用户池/IdP 集成/智能体身份/凭据托管/动态授权）、Gateway 工具接入（MCP Server 接入/REST-OpenAPI 转换/治理能力）、A2A 协议（多 Agent 任务分发/结果回传/状态同步）、Session&Memory 分层管理（短期持久化/长期召回/跨会话记忆）、Knowledge 知识检索（LlamaIndex 入口/Viking 后端），每模块含典型集成代码片段

### FR-9: 竞品对比与生态定位
The system SHALL provide a `08-comparison-ecosystem.md` file comparing AgentKit with mainstream Agent platforms and establishing an evaluation framework.

#### Scenario: 技术选型评估
- **When**: 用户阅读 `08-comparison-ecosystem.md`
- **Then**: 文档包含：AgentKit vs LangGraph/LangChain/LlamaIndex/Coze/Dify 等 5+ 主流平台的 10 维度对比表格（抽象层次/开发者体验/部署模式/安全治理/可观测性/成本/生态/开源协议/企业级能力/学习曲线）、「AI Agent 平台选型评估框架」（8 维度加权打分模板）、AgentKit 在火山引擎 AI 产品矩阵中的定位图（Mermaid）

### FR-10: FAQ、最佳实践与术语资源
The system SHALL provide a `09-faq-best-practices.md` and `10-resources-glossary.md` file covering common questions, best practices, glossary, and reference links.

#### Scenario: 问题排查与深入学习
- **When**: 用户阅读 `09-faq-best-practices.md` 和 `10-resources-glossary.md`
- **Then**: FAQ 文档包含：≥15 个常见问题与解答（覆盖开通计费/权限配置/部署问题/调试排障/性能优化/安全合规六大类）、8 条最佳实践（从 Demo 到生产的检查清单/存量系统改造 SOP/多租户隔离策略/成本优化建议等）；术语资源文档包含：≥20 条术语表（AgentKit/Harness/VeADK/A2A/MCP Gateway/Session/Memory/Knowledge/RAG/Runtime/Identity 等）、官方文档链接汇总、GitHub 仓库地址、与知识库 10+ 相关 wiki 的交叉引用

### FR-11: 文档元数据与导航规范
The system SHALL ensure all 11 wiki files follow consistent metadata and navigation conventions matching the existing `ffi-wiki` and `agent-communication-protocols` patterns.

#### Scenario: 验证文档规范性
- **When**: 检查任意 wiki 文件
- **Then**: 每个文档包含完整 YAML frontmatter（id/title/source/category/tags/date/status/author/summary）；分章文档底部包含双向导航（上一章/返回目录/下一章）；所有内部链接使用相对路径，无 `file:///` 绝对路径

## Non-Functional Requirements
- **NFR-1**: 每个原子文档不超过 300 行，遵循单一职责原则
- **NFR-2**: 技术术语准确，引用火山引擎官方文档、VeADK GitHub 仓库、SDK 文档等权威来源
- **NFR-3**: 语言专业准确同时保持 Wikipedia 风格——客观中立、结构清晰、适合技术读者参考
- **NFR-4**: 所有内部链接使用相对路径，无 `file:///` 绝对路径，通过链接检查
- **NFR-5**: 代码示例标注语言类型，使用 Python 为主（VeADK 最成熟的 SDK），补充必要的 Shell 命令
- **NFR-6**: 遵循项目文档命名规范（kebab-case，两位数前缀排序）
- **NFR-7**: 所有图表使用 Mermaid 语法，确保可读性（每个文档图表 1-3 个，不超过 5 个）

## Constraints
- **Technical**: 使用 Markdown + Mermaid 图表，遵循项目现有 wiki 格式（参考 `ffi-wiki` 结构和 `agent-communication-protocols` 的元数据规范）
- **Business**: 教程内容需与现有知识库中 `agent-communication-protocols`（MCP/A2A 协议）、`harness-seven-components-wiki`（智能体七大组件）、`adversarial-review-wiki`（对抗审查评测方法论）形成知识互补，通过交叉引用建立关联
- **Dependencies**:
  - 依赖项目现有知识库结构（`docs/knowledge/learning/03-agent-platforms-tools/` 目录）
  - 依赖火山引擎官方文档与开源仓库内容作为事实来源（公开可访问）
  - 依赖 `docgen-cmd` 后续自动纳入知识库索引

## Assumptions
- 读者具备基础 AI/ML 概念，了解大语言模型、RAG、Tool Calling 等基础概念
- 读者具备 Python 编程基础（VeADK 最成熟的 SDK 语言）
- 读者了解至少一种云服务的基本使用（账号、权限、部署）
- 文档放置于 `.agents/docs/knowledge/learning/03-agent-platforms-tools/volcengine-agentkit-wiki/` 目录
- 教程内容为快照性质，基于 2026 年 7 月官方公开资料，后续读者需以官方文档更新为准

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 教程创建完成
- **When**: 查看目标目录 `volcengine-agentkit-wiki/`
- **Then**: 包含 `00-overview.md` 到 `10-resources-glossary.md` 共 11 个文件，加上 `README.md` 索引，共 12 个文件；每个文件 < 300 行
- **Verification**: `programmatic`

### AC-2: 产品介绍与核心概念完整
- **Given**: `01-product-intro.md` 文档
- **When**: 阅读文档
- **Then**: 包含产品定义、工程化 4 大痛点分析、8 大功能模块详解、4 大产品优势、发展时间线（Mermaid）
- **Verification**: `human-judgment`

### AC-3: 架构与核心能力覆盖
- **Given**: `02-core-architecture.md` 文档
- **When**: 阅读文档
- **Then**: 包含分层架构图（Mermaid）、动态 Harness 编排 3 特性、Serverless 底座 3 能力、安全防护 3 层模型、评测可观测闭环
- **Verification**: `human-judgment`

### AC-4: VeADK 开发框架完整
- **Given**: `03-veadk-framework.md` 文档
- **When**: 阅读文档
- **Then**: 包含三语言安装命令、VeADK Family 20+ 产品融合矩阵（表格）、DeepResearch 6 大特性、开源仓库地址
- **Verification**: `human-judgment`

### AC-5: SDK & CLI 工具链完整
- **Given**: `04-agentkit-sdk-cli.md` 文档
- **When**: 阅读文档
- **Then**: 包含装饰器 API 代码示例、CLI 命令清单、三种部署模式对比表、Platform 服务集成说明
- **Verification**: `human-judgment`

### AC-6: 快速入门可操作
- **Given**: `05-quickstart.md` 文档
- **When**: 阅读文档
- **Then**: 包含前置条件清单、5 步标准上手流程（每步含命令+预期输出）、≥5 个常见问题排查
- **Verification**: `human-judgment`

### AC-7: 应用场景充分
- **Given**: `06-application-scenarios.md` 文档
- **When**: 阅读文档
- **Then**: 包含 4 大场景详解（每个含架构图 Mermaid + 实施步骤）、3 大行业落地框架、标准化 vs 定制化选型决策树
- **Verification**: `human-judgment`

### AC-8: 核心功能深度解析
- **Given**: `07-core-features-detailed.md` 文档
- **When**: 阅读文档
- **Then**: 包含 5 大模块深度解析（Identity/Gateway/A2A/Session-Memory/Knowledge），每模块含集成模式说明与代码片段
- **Verification**: `human-judgment`

### AC-9: 竞品对比与评估框架
- **Given**: `08-comparison-ecosystem.md` 文档
- **When**: 阅读文档
- **Then**: 包含 10 维度 × 5+ 平台对比表格、8 维度选型评估框架（可复用模板）、火山引擎 AI 产品矩阵定位图（Mermaid）
- **Verification**: `human-judgment`

### AC-10: FAQ 与最佳实践完整
- **Given**: `09-faq-best-practices.md` 文档
- **When**: 阅读文档
- **Then**: 包含 ≥15 个 FAQ（6 大分类）、8 条最佳实践、从 Demo 到生产检查清单
- **Verification**: `human-judgment`

### AC-11: 术语与资源完整
- **Given**: `10-resources-glossary.md` 文档
- **When**: 阅读文档
- **Then**: 包含 ≥20 条术语表、官方文档/GitHub 链接汇总、与知识库 ≥10 个相关 wiki 的交叉引用
- **Verification**: `human-judgment`

### AC-12: 元数据规范
- **Given**: 所有 11+1 个文档
- **When**: 检查 frontmatter
- **Then**: 每个文档包含完整 YAML frontmatter，`source` 字段值为 `seven-concepts: volcengine-agentkit-wiki`，`category` 为 `learning`
- **Verification**: `programmatic`

### AC-13: 链接有效
- **Given**: 教程完成
- **When**: 运行链接检查
- **Then**: 所有内部相对路径链接有效，无 `file:///` 绝对路径断链
- **Verification**: `programmatic`

### AC-14: 双向导航
- **Given**: 分章文档（01-10）
- **When**: 检查导航链接
- **Then**: 每个文档底部包含上一章、返回目录、下一章的双向导航链接
- **Verification**: `human-judgment`

### AC-15: 交叉引用充分
- **Given**: 全部教程
- **When**: 检查跨 wiki 引用
- **Then**: 至少引用以下已有 wiki：agent-communication-protocols（MCP/A2A）、harness-seven-components-wiki、adversarial-review-wiki、agent-interface-deep-dive、agent-skills-wiki、longcat-agent-learning-wiki 等 ≥6 个
- **Verification**: `human-judgment`

## Open Questions
- [ ] 快速入门章节是否需要基于真实火山引擎控制台截图进行指引？（当前假设仅用文字+命令描述，避免图片版权与时效性问题）
- [ ] 核心功能深度解析中是否需要包含具体的 IAM 权限配置 JSON 示例？（当前假设提供高层说明与官方配置链接，不提供可直接复制的生产配置）
- [ ] 竞品对比章节是否需要纳入 Coze/扣子、Dify 等国内流行平台的深度对比？（当前假设以 LangGraph/LlamaIndex 等开源框架为主对比对象）
