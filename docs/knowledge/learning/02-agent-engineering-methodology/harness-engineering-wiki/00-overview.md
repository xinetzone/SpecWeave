---
id: "harness-engineering-wiki-00"
title: "Harness Engineering（驾驭工程）：概述与学习目标"
source: "https://mp.weixin.qq.com/s/0w_xMwto4sLx6J_85OhWQw?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/harness-engineering-wiki/00-overview.toml"
date: "2026-07-04"
category: "learning"
---

# Harness Engineering（驾驭工程）：概述与学习目标

## 背景介绍

本文源自阿里技术公众号文章，作者涅羽，写给所有被Agent折磨又离不开的开发者。当你经历过凌晨三点回滚Agent事故、会话间失忆、20个工具面前"逛超市"、死循环、800行AGENTS.md读到200行开始幻觉——这篇文章就是为你而写。

文章核心观点：**Agent = Model + Harness**。模型负责推理，Harness负责剩下所有事。瓶颈不在模型本身，而在环境设计——模型是CPU，Harness是操作系统。

## 学习目标

通过本文档，你将能够：

1. 理解三代AI工程范式的演进路径：Prompt Engineering → Context Engineering → Harness Engineering
2. 掌握Harness Engineering的四条反直觉铁律，并能在实践中应用
3. 学会六大工程模式，用于构建可控、可靠的Agent系统
4. 通过悟空AI招聘实战案例，理解从"全能Agent"到"专才架构"的落地方法
5. 洞察行业未来趋势，建立对Agent工程化的系统性认知

## 前置知识要求

- 了解AI Agent的基本概念
- 有LLM应用开发经验更佳
- 对Prompt Engineering和Context Engineering有初步认知

## 文档导航

| 章节 | 文件 | 内容概要 |
|------|------|----------|
| 01 | [01-paradigm-evolution.md](01-paradigm-evolution.md) | 三代AI工程范式演进、核心公式、LangChain实验、五层运行时 |
| 02 | [02-four-iron-laws.md](02-four-iron-laws.md) | 四条反直觉铁律详解 |
| 03 | [03-six-patterns.md](03-six-patterns.md) | 六大工程模式实践指南 |
| 04 | [04-wukong-case-study.md](04-wukong-case-study.md) | 悟空AI招聘实战案例 |
| 05 | [05-industry-benchmarks.md](05-industry-benchmarks.md) | 行业标杆地图与自查镜子 |
| 06 | [06-future-trends.md](06-future-trends.md) | 四大未来趋势与六条心法 |
| 07 | [07-critical-thinking.md](07-critical-thinking.md) | 批判性思考与SpecWeave关联映射 |
| 08 | [08-faq.md](08-faq.md) | 10个常见问题解答 |
| 09 | [09-resources.md](09-resources.md) | 资源链接与延伸阅读 |

## 术语表

| 术语 | 定义 |
|------|------|
| **Harness Engineering** | 驾驭工程，第三代AI工程范式，专注于为模型构建可控的工作环境（操作系统），而非仅优化话术或上下文 |
| **Prompt Engineering** | 第一代范式，核心问题是"怎么把话说清楚"，形象比喻为"对马喊话" |
| **Context Engineering** | 第二代范式，核心问题是"怎么给AI喂对信息"，形象比喻为"给马看地图" |
| **Agent** | 智能体， = Model + Harness，具备自主执行任务能力的AI系统 |
| **Sub-Agent** | 子智能体，专才架构下的分工单元，每个只具备完成特定任务所需的工具和上下文 |
| **Skill** | 技能，廉价的原子函数，无独立Context，一个函数+明确签名即可 |
| **Workspace** | 工作空间，横跨Agent五层运行时的状态基座，是Agent的"Git仓库"，真相的唯一来源 |
| **MCP** | Model Context Protocol，模型上下文协议，Agent与外部工具交互的标准接口 |
| **A2A** | Agent-to-Agent，智能体间协作协议，未来Agent操作系统的标准化方向 |
| **Linter** | 代码检查工具，在Harness中代表机器可执行的硬约束，区别于自然语言文档 |
| **Orchestrator** | 编排器，主Agent角色，负责任务拆解、分发、维护Workspace、跨会话记忆 |
| **Initializer** | 初始化器，双阶段架构中的第一阶段，理解任务并写出plan.md后退出 |
| **Executor** | 执行器，双阶段架构中的第二阶段，读取plan.md按步执行，不共享Initializer的Context |
| **Context Window** | 上下文窗口，模型当前能看到的信息范围，是稀缺资源而非无限仓库 |
| **Feedback Loop** | 反馈回路，Linter/Test/CI自动闭环，错误信号回传给上游修正 |
| **Entropy Management** | 熵管理，持续清理过期文档、检测架构漂移、小额持续还债 |
