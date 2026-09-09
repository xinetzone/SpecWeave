# Codex Agent 工作流实践 — Spec 规划

## 骨架判定（操作可复现性两问）

**Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？**
→ 否。本文为个人实践心得分享，描述的是工作范式与思考方式，非逐步教程。文中虽提及多个 skill（review-change-loop、babysit-mr、tdd、execute-plan 等），但未提供可直接复现的代码或安装步骤，属于"经验总结"而非"操作手册"。

**Q2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？**
→ N/A（Q1 已为否）。

**结论：不设 `examples/`，走"技术综述/实践盘点"骨架。**
目录结构：`index.md + concepts/ + references/ + log.md`

## 归属判定

| 候选分组 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/`（已有 34 束） | ✅ 采用 | 主线实体为 AI Coding Agent 工作流实践，同组已有 `agent-platform-notes`、`ai-engineering-methodology`、`planning-with-files` 等同类非源码实践类 bundle，证明可容纳 |
| 新建 `jishu/ai/codex/` | ❌ 过度工程 | 单篇博文禁止新建分组（规则③） |

**最终落点：`jishu/ai/codex-agent-workflow-practices/`**

## 三层知识拆分规划

| 层次 | 篇目 | 内容要点 |
|------|------|---------|
| 事件/实践概览层 | 00-overview.md | 作者背景、token 用量变化曲线、四大核心杠杆总览 |
| 方法论层（并行化） | 01-parallel-workflow.md | 多 session 并行、sub-agent 分工、背景任务 |
| 方法论层（大闭环） | 02-large-closed-loop.md | 工具提供、反馈信息、monorepo、集成测试、文档价值、context 管理 |
| 方法论层（对抗提升） | 03-adversarial-improvement.md | Review fix loop、test fix loop、Best-of-N |
| 方法论层（真实需求） | 04-real-demand-driven.md | Feature flag、用户反馈信号自动获取、AI native 流程 |
| 问题解决层（Review） | 05-review-challenges.md | 多轮耗时、Review 左移、Scope 膨胀、无用测试 |
| 问题解决层（Spec/Plan） | 06-spec-and-plan.md | Spec 写什么/怎么写、任务切分（垂直切片）、开发自闭环、长程任务推进 |
| 问题解决层（质量保障） | 07-quality-assurance.md | 技术债控制、High level 视角注入（DDD+ADR）、Skill 开发原则 |

## 主题关联

- 与 [`agent-platform-notes`](../../agent-platform-notes/index.md) 互补：后者聚合各平台散篇，本篇为单篇深度实践
- 与 [`planning-with-files`](../../planning-with-files/index.md) 互补：后者讲 3-File Pattern 文件系统外存，本篇讲 Spec+Plan 文档组合与垂直切片
- 与 [`context-optimization`](../../context-optimization/index.md) 互补：后者讲 Token 优化技术，本篇讲上下文管理的工作流策略
