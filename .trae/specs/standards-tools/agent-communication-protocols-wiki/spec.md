---
version: 1.0
---

# Agent 通信协议体系（MCP/ACP/A2A/ANP）Wiki 教程 - Product Requirement Document

<!-- changelog -->
- 2026-07-03 | feat | 初始PRD创建

## Overview
- **Summary**: 创建一份结构清晰、内容详实的 Agent 通信协议 wiki 教程，系统性解析 MCP（Model Context Protocol）、ACP（Agent Communication Protocol）、A2A（Agent-to-Agent Protocol）、ANP（Agent Network Protocol）四大核心协议。教程采用原子化文档组织模式（总览入口 + 分章子文件），包含准确定义、核心功能、系统定位、概念关联、交互流程、技术实现要点、典型应用场景、术语解释与 Mermaid 图示说明，适合技术人员系统学习参考。
- **Purpose**: 随着多 Agent 系统快速发展，MCP/ACP/A2A/ANP 构成 Agent 互联互通的协议栈，但技术人员缺乏一份系统性中文教程来理解各协议的定位差异、关联关系与适用场景。本教程填补这一空白，为 SpecWeave 项目内 Agent 互操作设计提供知识基础。
- **Target Users**: AI Agent 开发者、架构师、技术决策者、对多 Agent 系统感兴趣的工程师和研究者。

## Goals
- 系统性覆盖四大协议（MCP/ACP/A2A/ANP）的核心概念、定义和功能定位
- 清晰阐述各协议在 Agent 系统架构中的层级关系与协作模式
- 提供协议间的交互流程图示（Mermaid）和典型应用场景说明
- 解释关键技术术语，提供代码示例和实现要点
- 遵循项目知识库原子化文档规范，便于维护和扩展
- 教程内容准确、逻辑严谨，引用权威来源（官方规范、学术论文）

## Non-Goals (Out of Scope)
- 不实现任何协议的代码 SDK 或服务器/客户端
- 不深入到某一特定框架（如 LangChain、CrewAI）的集成教程
- 不包含特定编程语言的完整实现代码
- 不对比传统分布式系统协议（如 gRPC、REST、MessagePack）
- 不涉及协议安全审计或性能基准测试
- 不包含商业产品对比或选型推荐（仅做技术维度客观对比）

## Background & Context
- 2024年11月 Anthropic 发布 MCP（Model Context Protocol），解决 Agent↔工具/数据连接问题
- 2025年3月 IBM Research/BeeAI 贡献 ACP（Agent Communication Protocol）到 Linux 基金会，定位本地优先的 Agent↔Agent 通信
- 2025年4月 Google 联合 50+ 厂商发布 A2A（Agent-to-Agent Protocol），6月捐赠 Linux 基金会，定位跨厂商 Agent 协作
- ANP（Agent Network Protocol）是面向去中心化 Agent 网络/市场的新兴协议，使用 DID 和 JSON-LD
- arXiv 论文（2505.02279）提出四协议分层模型：MCP（工具层）→ ACP（本地消息层）→ A2A（跨平台协作层）→ ANP（去中心化网络层）
- 本项目已有的知识库采用原子化 wiki 模式（如 agent-skills-wiki、karpathy-llm-coding-guidelines），本教程遵循相同模式
- 文档位置：`docs/knowledge/learning/` 目录下，总览入口 `agent-communication-protocols-wiki.md` + 原子化子目录 `agent-communication-protocols/`

## Functional Requirements
- **FR-1**: 提供教程总览入口文档，包含协议全景图、学习路径、各章导航
- **FR-2**: 为每个协议（MCP/ACP/A2A/ANP）创建独立章节文件，包含定义、发起方、发布时间、核心功能、架构设计、关键概念、传输协议、消息格式
- **FR-3**: 创建协议对比与关联章节，包含分层架构图（Mermaid）、技术维度对比表、互补关系说明
- **FR-4**: 创建交互流程章节，包含典型多 Agent 协作场景的端到端流程图（Mermaid sequenceDiagram）
- **FR-5**: 创建技术实现要点章节，包含 Agent Card 格式、消息结构示例、核心 API 端点、代码片段（curl/Python/JS 示例）
- **FR-6**: 创建典型应用场景章节，覆盖企业内部协作、跨组织协作、边缘/IoT、去中心化 Agent 市场等场景
- **FR-7**: 创建术语表章节，解释 JSON-RPC、SSE、Agent Card、Task、Artifact、DID、mDNS、MIME 等关键术语
- **FR-8**: 创建资源与参考章节，汇总官方规范链接、GitHub 仓库、学术论文、SDK 资源
- **FR-9**: 所有 Mermaid 图示遵循项目 Mermaid 安全编码六规则（见 best-practices/mermaid-guide.md）
- **FR-10**: 文档使用 TOML frontmatter 标记来源溯源，格式符合项目规范

## Non-Functional Requirements
- **NFR-1**: 文档准确性 - 所有技术描述必须与官方规范一致，引用来源明确
- **NFR-2**: 结构清晰 - 采用编号分章（00-xx），便于顺序阅读和按需查阅
- **NFR-3**: 可读性 - 技术深度适中，既有概览也有实现细节，适合不同层次读者
- **NFR-4**: 可维护性 - 原子化单一职责文件，每个文件聚焦一个主题，便于后续更新
- **NFR-5**: 一致性 - 遵循项目现有 wiki 风格（参考 agent-skills-wiki），包括标题格式、表格样式、Mermaid 图示风格
- **NFR-6**: 链接规范 - 使用相对路径交叉引用，避免绝对路径和 file:/// 协议
- **NFR-7**: 中文为主 - 术语保留英文原文并附中文解释，代码和技术名词保持英文

## Constraints
- **Technical**:
  - 遵循项目 docs/knowledge/learning/ 目录下的原子化文档模式
  - Mermaid 图表必须通过 mermaid-guide.md 中的安全编码六规则
  - Markdown 使用标准 CommonMark 语法，交叉引用使用相对路径
  - 文档 frontmatter 使用 TOML 格式（--- 包裹），包含 version 和 source 字段（如适用）
- **Business**:
  - 内容聚焦四大协议，不无限扩展到其他协议
  - 客观技术描述，不偏向任何厂商
- **Dependencies**:
  - Mermaid 图表依赖项目 Mermaid 渲染环境
  - 内容基于公开发布的官方规范和学术论文（arXiv:2505.02279 等）

## Assumptions
- 读者具备基本的 AI/LLM 概念和 HTTP/REST/JSON 技术基础
- 四大协议的官方规范在 2026 年 7 月前已公开发布，可作为准确参考
- 项目知识库索引脚本可正常工作，新文档加入后可被正确索引
- Mermaid 图示在目标 Markdown 渲染器（GitHub/VS Code/Trae IDE）中可正常显示

## Acceptance Criteria

### AC-1: 总览入口文档完整性
- **Given**: 教程总览文件已创建
- **When**: 读者打开总览文档
- **Then**: 能看到四大协议的全景介绍、学习路径建议、各章节导航链接、协议分层 Mermaid 架构图
- **Verification**: `human-judgment`

### AC-2: 各协议独立章节内容完整
- **Given**: MCP/ACP/A2A/ANP 各章节文件已创建
- **When**: 读者阅读任一协议章节
- **Then**: 该章节包含：准确定义、发起方与发布时间、核心功能、在 Agent 系统中的定位、架构设计图（Mermaid）、关键概念解释、传输与消息格式、安全机制
- **Verification**: `human-judgment`

### AC-3: 协议对比与关联关系清晰
- **Given**: 协议对比章节已创建
- **When**: 读者阅读对比章节
- **Then**: 能看到多维度技术对比表（传输/发现/安全/适用场景等）、互补关系说明、分层架构图、选型建议决策树（Mermaid flowchart）
- **Verification**: `human-judgment`

### AC-4: 交互流程图示准确
- **Given**: 交互流程章节已创建
- **When**: 读者查看流程图
- **Then**: 至少包含 3 个典型交互流程 Mermaid 时序图：(1) 单 Agent 通过 MCP 调用工具，(2) 多 Agent 通过 A2A 跨平台协作，(3) 本地 Agent 通过 ACP 对等通信；流程步骤清晰、消息方向正确
- **Verification**: `human-judgment`

### AC-5: 技术实现要点可操作
- **Given**: 技术实现章节已创建
- **When**: 开发者阅读实现要点
- **Then**: 能看到 Agent Card JSON 示例、核心 API 请求/响应格式、curl 命令示例、至少一个 Python 或 JS 的最小可用代码片段
- **Verification**: `programmatic`（代码片段语法正确、JSON格式合法）

### AC-6: 应用场景覆盖典型案例
- **Given**: 应用场景章节已创建
- **When**: 读者查看场景章节
- **Then**: 至少覆盖 4 类场景：企业数字员工团队、跨组织/跨 SaaS 协作、边缘 IoT/机器人、去中心化 Agent 市场；每个场景说明推荐协议组合和协作模式
- **Verification**: `human-judgment`

### AC-7: 术语表完整准确
- **Given**: 术语表章节已创建
- **When**: 读者查阅术语表
- **Then**: 包含至少 15 个关键术语的简明解释，涵盖协议核心概念和技术名词
- **Verification**: `human-judgment`

### AC-8: 资源链接可访问
- **Given**: 资源章节已创建
- **When**: 读者查阅资源
- **Then**: 包含官方规范链接、GitHub 仓库、学术论文、SDK 等分类整理的参考资源
- **Verification**: `programmatic`（链接格式正确）

### AC-9: Mermaid 图表合规
- **Given**: 所有 Mermaid 图表已创建
- **When**: 运行 Mermaid 安全检查
- **Then**: 所有 Mermaid 代码块遵循安全编码六规则，无 click 事件、无 style class 引用、无 end 关键字、无 script 注入风险
- **Verification**: `programmatic`（对照 mermaid-guide.md 六规则人工审核）

### AC-10: 文档结构与原子化规范
- **Given**: 所有文档文件已创建
- **When**: 检查文件结构
- **Then**: 文件位于 docs/knowledge/learning/agent-communication-protocols/ 目录下，编号 00-09（或更多），每个文件聚焦单一主题；总览入口在 docs/knowledge/learning/agent-communication-protocols-wiki.md
- **Verification**: `programmatic`（目录结构检查）

### AC-11: 交叉引用正确
- **Given**: 所有文档已创建
- **When**: 运行链接检查
- **Then**: 所有内部交叉引用使用相对路径，无 file:/// 绝对路径，无断链
- **Verification**: `programmatic`（运行 check-links.py 验证）

### AC-12: frontmatter 规范
- **Given**: 所有文档文件已创建
- **When**: 检查文档头部
- **Then**: 每个文件包含 TOML frontmatter（--- 包裹），含 version 字段；子文件含 source 字段溯源到总览文档或来源
- **Verification**: `programmatic`

## Open Questions
- [ ] ANP（Agent Network Protocol）的公开规范成熟度如何？是否有足够资料撰写深度章节，还是仅做概述性介绍？
- [ ] 是否需要包含 MCP 与 IDE 集成（如 Claude Code、Cursor、Trae）的实际使用示例？
- [ ] 是否需要一个快速参考/速查表章节（类似 agent-skills-wiki 的 14-quick-reference.md）？
