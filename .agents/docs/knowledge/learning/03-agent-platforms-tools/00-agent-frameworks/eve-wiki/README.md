---
id: "eve-wiki-readme"
title: "Vercel Eve 开源 Agent 框架 Wiki 教程"
source: "https://blog.nixapi.com/blog/vercel-eve-agent-framework-2026/ + https://zhuanlan.zhihu.com/p/2051780593944416346 + https://zhuanlan.zhihu.com/p/2050951746332124853 + https://juejin.cn/post/7657863114352754726 + https://vercel.com/eve"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "nextjs-for-agents", "filesystem-first", "durable-execution", "sandbox", "mcp", "typescript", "ai-agent", "open-source"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "面向前端与 AI 开发者的 Vercel Eve 开源 Agent 框架结构化 wiki 教程，覆盖产品定位（Next.js for Agents）、目录即 Agent 设计哲学、九大生产级能力、与 Mastra/LangGraph 对比、快速上手、工程化理念与趋势洞察、FAQ 与术语表。已结合本地源码（external/tools/eve）校准 API 细节。"
last_verified: "2026-08-04"
wiki_version: "1.1"
eve_version_target: "2026 public preview"
---

# Vercel Eve 开源 Agent 框架 Wiki 教程

> **Eve 是 Vercel 发布的开源 AI Agent 框架，定位"Next.js for Agents"**。它把 Agent 视为一个文件目录（filesystem-first），用 Markdown 定义指令与技能、用 TypeScript 定义工具，内置持久化执行、沙箱计算、人工审批、MCP 连接等生产级能力，开箱即用。

## 适用人群

| 序号 | 人群 | 核心诉求 |
|------|------|---------|
| 1 | 前端开发者 | 复用已有的文件系统、目录约定、Git、部署经验，以最低门槛切入 Agent 开发 |
| 2 | AI 应用开发者 | 理解"从 Demo 到生产"的工程化路径，掌握 Agent 生产级底座（持久化/沙箱/审批/评测） |
| 3 | 技术架构师 | 评估 Eve 作为 Agent 基础设施的选型价值，与 Mastra/LangGraph 对比 |
| 4 | 技术决策者 | 洞察 Agent 工程化趋势与 Vercel 的 AI 战略布局 |

## 10 章快速导航

| 章号 | 文件名 | 标题 | 一句话简介 |
|------|--------|------|-----------|
| 00 | [00-overview.md](./00-overview.md) | 教程总览与知识地图 | Eve 生态全景图、10 章导航、三条阅读路径、交叉引用矩阵 |
| 01 | [01-product-intro.md](./01-product-intro.md) | 产品介绍与核心概念 | 定位（Next.js for Agents）、与 AI SDK/Agent Loop 层次区分、及 A 目录哲学 |
| 02 | [02-directory-core-capabilities.md](./02-directory-core-capabilities.md) | 目录结构与核心能力 | agent.ts/instructions.md/tools/skills/sandbox 详解 |
| 03 | [03-production-capabilities.md](./03-production-capabilities.md) | 生产级能力详解 | durable execution/approvals/connections/channels/tracing/evals |
| 04 | [04-advanced-capabilities.md](./04-advanced-capabilities.md) | 进阶能力 | subagents/schedules/多 Agent 协作实战模式 |
| 05 | [05-quickstart.md](./05-quickstart.md) | 快速上手指南 | 官方九步 + 五步快启 + 最小指令先行 + 部署说明 |
| 06 | [06-comparison-selection.md](./06-comparison-selection.md) | 竞品对比与选型 | Eve vs Mastra vs LangGraph、适用团队边界、选型决策树 |
| 07 | [07-engineering-philosophy-trends.md](./07-engineering-philosophy-trends.md) | 工程化理念与趋势洞察 | Demo→生产、工程底座竞争、前端工程化迁移 |
| 08 | [08-faq.md](./08-faq.md) | FAQ 与适用范围 | 常见问题、适用团队、局限性 |
| 09 | [09-glossary-resources.md](./09-glossary-resources.md) | 术语表与参考资源 | 核心术语 + 5 个来源 + 官方文档 + 知识库扩展 |

## 内容快照声明

> 本教程基于 2026 年 6-8 月的 5 个公开来源整理而成（nixapi 深度解析博客、知乎两篇分析、掘金工程化解读、Vercel 官方产品页），为结构化知识快照性质。v1.1 起已结合本地源码 `external/tools/eve` 的官方文档（docs/）对 API 细节进行校准（如 `agent.ts` 的 `defineAgent`、`defineTool`、`defineSchedule`、`defineEval`、`approval` 策略、沙箱后端等），修正了早期公开资料中的过时写法。Eve 目前处于 public preview / beta 阶段，框架、API、文档和行为可能持续变化，后续请以官方文档为准。

| 元数据 | 值 |
|--------|-----|
| Wiki 版本 | **v1.1**（源码校准版） |
| 覆盖 Eve 阶段 | public preview（2026-08 快照） |
| 最后验证日期 | 2026-08-04 |
| 文件总数 | 11（README + 10 章教程） |

## 资源链接

- **官方产品页**：https://vercel.com/eve
- **官方发布博客**：https://vercel.com/blog/introducing-eve
- **官方文档**：https://beta.eve.dev/docs
- **GitHub 仓库**：https://github.com/vercel/eve