---
id: "harness-engineering-wiki-01"
title: "范式演进：三代AI工程"
source: "https://mp.weixin.qq.com/s/0w_xMwto4sLx6J_85OhWQw?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/harness-engineering-wiki/01-paradigm-evolution.toml"
date: "2026-07-04"
category: "learning"
---
# 范式演进：三代AI工程

## 共鸣时刻：你是否也经历过这些？

- 凌晨三点回滚Agent线上事故
- 会话间失忆，昨天跑通的今天又不行了
- 20个工具列表面前，Agent开始"逛超市"
- 死循环，同样的错误重复十几次
- 800行AGENTS.md，模型读到200行就开始幻觉

如果你中了两条以上，这篇文章就是为你而写。

## 核心公式：Agent = Model + Harness

这个公式由Mitchell Hashimoto提出[1]，后被LangChain官方采用[2]。

- **模型（Model）**：CPU，负责推理
- **Harness（驾驭框架）**：操作系统，负责剩下所有事——工具管理、记忆、反馈、边界、熵控制

**LangChain实验案例**：不换模型，仅优化Harness，Terminal Bench排名从第30名跃升至第5名，分数从52.8提升至66.5分[2]。

| 条件 | Terminal Bench排名 | 分数 |
|------|-------------------|------|
| 优化Harness前 | 第30名 | 52.8 |
| 优化Harness后（不换模型） | 第5名 | 66.5 |

## 三代范式对比

| 代际 | 范式 | 核心问题 | 形象对比 |
|------|------|----------|----------|
| 第一代 | Prompt Engineering | 怎么把话说清楚 | 对马喊话 |
| 第二代 | Context Engineering | 怎么给AI喂对信息 | 给马看地图 |
| 第三代 | Harness Engineering | 怎么让Agent可控地工作 | 给马造高速公路 |

## Agent五层运行时全景

Agent运行时分为五层，Workspace横跨所有层作为状态基座：

```
┌─────────────────────────────────────────────────────────────┐
│                  User Interaction (用户交互层)                │
├─────────────────────────────────────────────────────────────┤
│                  Orchestration (编排调度层)                   │
├─────────────────────────────────────────────────────────────┤
│                  Capabilities (能力层：Tools/Skills)          │
├─────────────────────────────────────────────────────────────┤
│                  Execution (执行层)                           │
├─────────────────────────────────────────────────────────────┤
│                  MCP (工具协议层)                             │
└─────────────────────────────────────────────────────────────┘
                         ↕ 横跨所有层
              Workspace (状态基座/文件系统)
```

四根护栏贯穿整个体系：
1. **Context Engineering**：上下文工程化
2. **Architecture Constraints**：架构约束
3. **Feedback Loop**：反馈回路
4. **Entropy Management**：熵管理

## Context Engineering工程化四要素

Context Engineering是Harness Engineering的子集，但本身也需要工程化：

| 要素 | 说明 |
|------|------|
| **结构化** | 让上下文有schema，不是自由文本 |
| **分段化** | 按系统约束/任务定义/当前状态/工具签名/历史摘要分槽位 |
| **可回放** | 每次上下文构造可重放、可diff |
| **可审计** | 保留信息来源链 |

## 关键引用

- [1] Mitchell Hashimoto《My AI Adoption Journey》
- [2] LangChain官方博客《Improving Deep Agents with Harness Engineering》: https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering
