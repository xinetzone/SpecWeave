---
title: "Agent Runtime Protocol 学习与 Wiki 教程文档"
source: "微信公众号文章《Agent Protocol：一个生产级的 Agent Runtime 应该包含什么？》（阿里云开发者）"
date: "2026-07-04"
tags: ["agent-runtime", "agent-protocol", "langgraph", "openai-assistants", "autogen", "claude-sdk", "mcp", "thread", "run", "checkpoint", "artifact", "event", "human-in-the-loop", "error-recovery", "multi-agent", "observability"]
---

# Agent Runtime Protocol 学习与 Wiki 教程文档 - 产品需求文档

## Overview
- **Summary**: 系统学习阿里云开发者发布的《Agent Protocol：一个生产级的 Agent Runtime 应该包含什么？》深度技术文章，理解生产级 Agent Runtime 的核心协议对象、八大维度能力（执行模型、状态管理、中断恢复、错误恢复、工具协议、流式输出、多 Agent 协作、可观测性与可评测性），基于学习成果创建一份结构清晰、内容详实的 wiki 教程文档，涵盖核心概念解析、跨框架对比、设计决策分析和开发者建议。
- **Purpose**: 为 AI Agent 开发者、架构师和技术决策者提供 Agent Runtime Protocol 的系统性学习资料，帮助理解跨框架的稳定协议边界，避免被短期流行的框架 API 牵着走，建立从"框架熟练度"到"系统设计判断力"的认知提升。
- **Target Users**: AI Agent 开发者、大模型应用工程师、系统架构师、技术决策者、关注 Agent 基础设施演进的技术人员、多 Agent 系统研究者。

## Goals
- 创建包含目录导航系统的 wiki 教程文档
- 解释文章核心观点：Agent Runtime 的核心不是模型调用，而是任务生命周期管理
- 详细解析六大核心协议对象：Thread/Session、Run/Task、Step、Event、Artifact、Checkpoint
- 系统讲解八大维度：执行模型、状态管理、中断恢复、错误恢复、工具协议、流式输出、多 Agent 协作、可观测性与可评测性
- 提供 LangGraph、OpenAI Assistants/Agents SDK、AutoGen、Claude SDK 五大框架的跨维度对比
- 分析三层概念区分：具体协议标准、通用协议对象、Runtime 实现能力
- 讲解 Agent Harness（如 Deep Agents）的定位与价值
- 阐述 Error-as-Data 错误处理哲学
- 分析 MCP 在工具层标准化中的作用
- 提供设计决策持久性判断和开发者投入建议
- 整理术语对照表
- 更新知识库索引添加本教程入口

## Non-Goals (Out of Scope)
- 不提供各框架的完整 API 使用教程
- 不进行框架性能基准测试
- 不实现具体的 Agent Runtime 代码
- 不深入某个单一协议标准（A2A/AG-UI/AITP/ACP）的完整规范
- 不涉及具体业务场景的 Agent 落地案例
- 不进行框架优劣的主观排名
- 不包含 Agent 安全和对齐的深度讨论

## Background & Context
- 文章来源：阿里云开发者公众号
- 作者核心观点：框架名词在变，但底层问题始终围绕任务、上下文、步骤、事件、状态和产物展开
- 核心主张：Thread/Run/Step/Event/Artifact/Checkpoint 会成为跨框架的稳定对象
- 关键判断：真正区分玩具 Agent 和生产 Agent 的，是状态持久化、中断恢复、可观测性和可评测性
- 对比框架：LangGraph（0.3.x）、Deep Agents SDK（2026.06）、OpenAI Assistants/Agents SDK（2025.04）、AutoGen 0.4、Claude Agent SDK（0.1.x）
- 涉及协议标准：A2A、AG-UI、LangChain Agent Protocol、AITP、ACP、MCP、OpenTelemetry GenAI
- 原文链接：https://mp.weixin.qq.com/s/0N-RnpGVy_PLSDHMwAIFNg

## Functional Requirements
- **FR-1**: 创建 wiki 教程文档主页面，包含完整的目录导航系统
- **FR-2**: 编写概述与核心观点章节，介绍文章背景、核心问题和六大核心对象
- **FR-3**: 编写 Agent Protocol 边界定义章节，解析三层概念（标准/对象/Runtime能力）、Runtime Protocol 定义、最小生命周期
- **FR-4**: 编写执行模型章节，解析两层模型（Loop承载方式/编排协议）、Agent Harness 定位、Runtime Loop 隐藏主循环、Workspace/Sandbox 概念
- **FR-5**: 编写状态管理章节，解析持久化光谱、状态五层分层（Conversation/Run State/Checkpoint/Artifact/Semantic Memory）、Session/Thread/Run 关系、并发 Run 策略、Schema 演进
- **FR-6**: 编写中断与恢复章节，解析 Human-in-the-Loop 基础设施、中断/恢复通用流程、各框架实现对比
- **FR-7**: 编写错误恢复章节，解析 Error-as-Data vs Error-as-Exception 两种哲学、Checkpoint 回滚机制
- **FR-8**: 编写工具协议章节，解析工具协议独立分层、MCP 标准化形态、Runtime 控制面（权限/Guardrail/预算）
- **FR-9**: 编写流式输出章节，解析任务事件流概念、Server vs Library 分水岭、可恢复 SSE 机制
- **FR-10**: 编写多 Agent 协作章节，解析四种编排模式（子图嵌套/Subagent task/Handoff接力/群聊选择/发布订阅）、为什么不该过早押注
- **FR-11**: 编写可观测性与可评测性章节，解析 Trace 最小语义模型、三类观测数据（Trace/Event Stream/State Snapshot）、从可观测到质量闭环
- **FR-12**: 编写 Agent Protocol 对象映射章节，汇总 Protocol 对象到 Runtime 能力的映射表、九条协议设计原则、Protocol 与 Runtime 边界
- **FR-13**: 编写跨维度分析章节，解析设计决策持久性判断、行业收敛趋势、开发者重点投入方向、从零设计 Runtime Protocol 的选择建议
- **FR-14**: 编写附录：术语对照表（通用概念与五大框架术语映射）
- **FR-15**: 编写内容评估与个人见解章节，评估原文价值并提出对 Agent 基础设施演进的思考
- **FR-16**: 编写常见问题解答章节
- **FR-17**: 编写相关资源链接章节
- **FR-18**: 更新知识库索引（docs/knowledge/README.md）添加本教程入口

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平的读者（入门开发者/资深工程师/架构师/技术决策者）
- **NFR-2**: 在适当位置引用原网页内容作为参考依据，关键观点有原文支撑
- **NFR-3**: 文档结构清晰，便于阅读和导航，使用对比表格清晰呈现跨框架差异
- **NFR-4**: 文档格式符合项目规范（Markdown格式，kebab-case命名，YAML frontmatter，遵循 MDI v1.0 规范）
- **NFR-5**: 技术术语准确，六大核心对象和八大维度提供清晰定义和解释
- **NFR-6**: 跨框架对比客观中立，既肯定各框架优势也指出其局限性
- **NFR-7**: 表格内容准确，与原文对比信息一致

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范，放置在 docs/knowledge/learning/ 目录下，使用 YAML frontmatter（遵循 MDI v1.0 规范），文件名使用 kebab-case: agent-runtime-protocol-wiki.md
- **Business**: 基于公开文章内容创建，客观说明各框架的成熟度差异和适用场景
- **Dependencies**: 依赖已获取并清洗的网页内容（.temp/article_content.md），无需额外网络请求

## Assumptions
- 用户具备基本的大模型和 AI Agent 概念认知
- 用户了解至少一种 Agent 框架（LangChain/LangGraph、AutoGen、OpenAI SDK 等）
- 用户对 API、协议、Runtime 等软件工程概念有基本理解
- 用户可以访问互联网查阅各框架官方文档

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: wiki 教程文档包含目录导航、概述核心观点、Protocol边界、八大维度详解、对象映射、跨维度分析、术语对照、内容评估、FAQ和资源链接等完整章节
- **Verification**: `human-judgment`
- **Notes**: 文档应放置在 docs/knowledge/learning/ 目录下，文件名为 agent-runtime-protocol-wiki.md

### AC-2: 六大核心对象解释清晰
- **Given**: 用户阅读概述章节
- **When**: 用户理解核心协议对象
- **Then**: 用户能够准确解释 Thread/Session、Run/Task、Step、Event、Artifact、Checkpoint 六大对象的含义和各自回答的问题
- **Verification**: `human-judgment`
- **Notes**: 使用表格形式呈现对象名称、人话解释、回答的问题

### AC-3: 三层概念区分明确
- **Given**: 用户阅读 Protocol 边界定义章节
- **When**: 用户理解三层概念差异
- **Then**: 用户能够区分具体协议标准（A2A/AG-UI等）、通用协议对象（六大对象）、Runtime 实现能力（持久化/恢复等）三个层级
- **Verification**: `human-judgment`
- **Notes**: 原文重点强调本文讨论第二层：通用协议对象

### AC-4: 八大维度系统完整
- **Given**: 用户阅读八大维度章节
- **When**: 用户逐章学习执行模型、状态管理、中断恢复、错误恢复、工具协议、流式输出、多Agent协作、可观测性与可评测性
- **Then**: 用户能够系统理解每个维度的通用概念、子概念、跨框架映射、设计决策分析和章节结论
- **Verification**: `human-judgment`
- **Notes**: 每个维度应包含：通用概念、子概念、跨框架对比表、设计决策分析、本章结论

### AC-5: 跨框架对比表准确
- **Given**: 用户查看各章节的跨框架映射表
- **When**: 用户对比 LangGraph、OpenAI Assistants、Agents SDK、AutoGen、Claude SDK 五大框架
- **Then**: 表格内容准确反映各框架在对应维度的实现方式和差异
- **Verification**: `human-judgment`
- **Notes**: 对比表是本文核心价值，需与原文信息一致

### AC-6: Error-as-Data 哲学阐述到位
- **Given**: 用户阅读错误恢复章节
- **When**: 用户理解错误处理哲学
- **Then**: 用户能够解释 Error-as-Data 与 Error-as-Exception 的区别，以及为什么 Agent Runtime 更适合 Error-as-Data
- **Verification**: `human-judgment`
- **Notes**: 使用流程图对比两种错误处理模式

### AC-7: MCP 工具层标准化分析清晰
- **Given**: 用户阅读工具协议章节
- **When**: 用户理解 MCP 的定位
- **Then**: 用户能够说明 MCP 如何把工具发现/定义/调用/资源读取从框架内部抽出来，以及 MCP 与完整 Runtime Protocol 的关系
- **Verification**: `human-judgment`
- **Notes**: MCP 是工具层标准化，不是完整 Runtime 标准

### AC-8: 设计决策建议有指导性
- **Given**: 用户阅读跨维度分析章节
- **When**: 用户查看开发者投入建议
- **Then**: 用户能够理解哪些方向应该重点投入（协议对象模型、工具协议抽象、状态管理抽象等）、哪些应该谨慎投入（特定框架API）、哪些应该观望（多Agent模式）
- **Verification**: `human-judgment`
- **Notes**: 建议表格应明确方向、建议等级、理由

### AC-9: 术语对照表完整
- **Given**: 用户查阅附录术语对照表
- **When**: 用户遇到框架特定术语
- **Then**: 用户能够找到通用概念在五大框架中的对应术语
- **Verification**: `human-judgment`
- **Notes**: 至少覆盖执行上下文、会话、执行、步骤、工具调用、状态持久化、中断、流式事件等核心概念

### AC-10: 目录导航系统可用
- **Given**: 用户打开 wiki 教程文档
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录导航包含所有章节的链接，点击可跳转到对应章节
- **Verification**: `programmatic`
- **Notes**: 使用 Markdown 锚点链接实现

### AC-11: 知识库索引更新完成
- **Given**: wiki 文档创建完成
- **When**: 查看 docs/knowledge/README.md
- **Then**: learning 分类中新增 Agent Runtime Protocol 教程条目，包含标题、摘要、日期和标签
- **Verification**: `programmatic`
- **Notes**: 遵循现有索引格式

## Open Questions
- [ ] 是否需要补充各框架官方文档链接？
- [ ] 是否需要添加与本项目已有 Agent/Skill/MCP 体系的关联分析？
