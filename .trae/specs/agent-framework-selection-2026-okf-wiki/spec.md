---
id: "agent-framework-selection-2026-okf-wiki"
title: "2026 AI Agent 框架选型 OKF 知识包"
theme: "knowledge-learning"
status: "in-progress"
created: "2026-11-10"
source: "https://dev.to/mr_manushukla/2026-ai-agent-frameworks-compared-langgraph-vs-crewai-vs-microsoft-agent-framework-vs-pydantic-ai-4f8k"
route: "summary-then-rewrite"
---

# 2026 AI Agent 框架选型 OKF 知识包 — 规格

## Overview

- **Summary**：把 DEV Community 转载、eCorpIT 原创的 2026 框架对比文系统学习后，转化为 OKF v0.2 知识包，落到 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/agent-framework-selection-2026/`。
- **Purpose**：给中文读者一份可溯源的选型地图：五个框架（LangGraph / CrewAI / Microsoft Agent Framework / Pydantic AI / LlamaIndex Workflows）各自的范式、2026 版本里程碑、生产就绪维度、成本结构与“按主导约束选型”的决策表。
- **Target users**：正在做 Agent 技术选型的架构师/技术负责人；已会 Python/.NET、准备从原型走向生产的开发者；需要理解 MAF 与 Semantic Kernel/AutoGen 关系的学习者。

## Goals

1. 所有日期、版本、用户名单、厂商能力声明登记 F 编号，P0 项逐一用官方源核验。
2. 保留作者的分析框架（主导约束决策表、双框架策略），但显式区分事实、作者观点与厂商自述。
3. 不设 `examples/`：原文是选型综述，没有读者可照做的安装/代码/实测流程（操作可复现性两问均为“否”）。
4. 接入 `ai-agent` 组索引、`frameworks`/`ai` 域索引与全库计数，保持 toctree 与链接可达。
5. 明确时效边界：框架版本迭代快，`stale_after` 设为 2027-01-31，并在正文标注“以当前官方文档为准”。

## Non-Goals

- 不做五个框架的源码级精读（信源是博文 + 官方发布页/文档，不是本地源码树）。
- 不替代官方文档做 API 教程；不给出“唯一最佳框架”的排名。
- 不复刻原文的印度市场服务推销段落，仅保留与选型相关的三条约束。
- 不评测具体模型价格；token 成本只保留原文区间并标注不可独立核验。

## 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/frameworks/ai-agent/agent-framework-selection-2026/` | **采用** | 主线是 Agent 框架横向对比；`ai-agent` 已有 62 束框架综述/教程，且 `pi-agent-harness`、`a2a-mcp-convergence` 等博文综述先例证明可容纳 |
| `jishu/ai/frameworks/microsoft-agent-framework/` | 否 | 该束只覆盖 MAF 单框架，本文是五框架对比；改为在“主题关联”互链 |
| `jishu/ai/practice/` | 否 | 内容不是工程方法论，而是具体框架的版本与能力对比 |

## 骨架判定（操作可复现性两问）

1. 是否有读者可照做的安装/配置/代码/调用/实测流程？→ **否**（全文无代码块、无安装命令、无实测输出）。
2. 这些流程是否经作者实测、具备可复现性？→ **否**（只有结论表与引用链接）。

结论：不设 `examples/`，采用 `index + concepts/ + references/ + log` 骨架。

## 目录骨架

```
agent-framework-selection-2026/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-five-frameworks-landscape.md
│   ├── 01-langgraph-control-and-durability.md
│   ├── 02-crewai-speed-and-maf-enterprise-merge.md
│   ├── 03-pydantic-ai-and-llamaindex.md
│   └── 04-selection-and-production-readiness.md
└── references/
    ├── index.md
    ├── article-source.md
    └── verification.md
```

## 质量门

- G1：事实清单不含“因为/所以/导致”等因果判断；作者观点标 📝，厂商自述标 🏷️。
- G2：每条洞察含陈述/证据（F 编号）/反常识/行动四元组。
- G3：模式（按主导约束选型、双框架分层）可迁移到非 Agent 领域的技术选型。
- G4：行动项单一职责、可验证、有 Owner、有时间、可独立交付（见 tasks.md）。
- V：四视角审查 + 双份 F 编号比对 + 链接/计数/UTF-8 机械门禁。

## 交付物

1. OKF bundle（7 个内容文档 + 3 个索引/日志）。
2. spec 五件套（spec/facts/insights/review/tasks）。
3. 组索引与全库计数更新。
4. 原子提交（子模块 → 主仓库），不 push。
