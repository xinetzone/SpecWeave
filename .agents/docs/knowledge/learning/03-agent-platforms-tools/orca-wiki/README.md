---
id: "orca-wiki-readme"
title: "Orca 多代理 AI 编排器 Wiki 教程"
source: "https://www.onorca.dev/ 官网 + d:\AI\external\tools\orca 本地开源源码"
category: "learning"
tags: ["orca", "stablyai", "ai-orchestrator", "agent-ide", "worktree", "claude-code", "codex", "opencode", "electron", "parallel-agents", "multi-agent", "yc"]
date: "2026-08-03"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "面向 100x 构建者的 AI 编排器 Orca 从入门到精通的结构化 wiki 教程，覆盖产品定位、核心架构、八大核心功能、Orca CLI 与多 Agent 编排、支持的 Agent 清单、快速上手、FAQ 与术语表。"
last_verified: "2026-08-03"
wiki_version: "1.0"
orca_version_target: "1.4.165-rc.0"

---

# Orca 多代理 AI 编排器 Wiki 教程

面向 100x 构建者的 AI 编排器——并排运行 Codex、Claude Code、OpenCode 或 Pi，每个都在自己的 worktree 中运行，并在一个地方统一跟踪。

## 适用人群

| 序号 | 人群 | 核心诉求 |
|------|------|---------|
| 1 | AI 辅助开发实践者 | 同时运行多个 AI 编程 Agent（Claude Code、Codex、OpenCode 等），实现并行工作区隔离与结果择优合并 |
| 2 | 多 Agent 协作研究者 | 理解 Orca 的多 Agent 编排机制（Run/Task/Dispatch/worker_done）与完整交接（full handoff）流程 |
| 3 | IDE 工具选型决策者 | 评估"IDE 从代码编辑器向代理编排器演进"的行业趋势与 Orca 的差异化定位 |
| 4 | 并行开发流程优化者 | 通过移动 Companion、终端分屏、SSH Worktree 等能力落地远程监控与并行开发 |

## 8 章快速导航

| 章号 | 文件名 | 标题 | 一句话简介 |
|------|--------|------|-----------|
| 00 | [00-overview.md](./00-overview.md) | 项目概述与核心定位 | Orca 定位、背景（Stably.ai/YC/MIT/Star 数）、传统痛点 vs 解决方案对照表 |
| 01 | [01-core-architecture.md](./01-core-architecture.md) | 核心架构与技术栈 | Electron+TypeScript 技术栈、工作区/编排/终端/浏览器分层、架构示意图 |
| 02 | [02-core-features.md](./02-core-features.md) | 八大核心功能详解 | 移动 Companion、并行 Worktree、终端分屏、设计模式、GitHub&Linear、SSH Worktree、注释 AI Diff、拖拽文件 |
| 03 | [03-orca-cli-orchestration.md](./03-orca-cli-orchestration.md) | Orca CLI 与多 Agent 编排 | worktree/terminal/repo/automations/browser/linear/computer 命令面 + Run/Task/Dispatch/worker_done 编排机制 |
| 04 | [04-supported-agents.md](./04-supported-agents.md) | 支持的 Agent 清单 | 任意 CLI Agent 均可运行，25+ 款 Agent 清单与简要说明 |
| 05 | [05-quickstart.md](./05-quickstart.md) | 快速上手指南 | 安装、启动登录、添加 Agent、创建分发 worktree、并行监控五步流程 |
| 06 | [06-value-and-trends.md](./06-value-and-trends.md) | 核心价值总结与行业趋势 | "IDE 从代码编辑器向代理编排器演进"、自带 Agent 理念、与开篇定位呼应 |
| 07 | [07-faq-glossary.md](./07-faq-glossary.md) | FAQ 与术语表 | 常见问题解答 + 15+ 核心术语通俗解释 |

## 内容快照声明

> 本教程基于 2026 年 8 月 Orca 官网公开资料（https://www.onorca.dev/）与本地开源源码（d:\AI\external\tools\orca，含 README、skill-guides、package.json）整理而成，为结构化知识快照性质。产品功能会持续演进（Orca 每日更新），后续请以官网最新文档为准。

| 元数据 | 值 |
|--------|-----|
| Wiki 版本 | **v1.0** |
| 覆盖 Orca 版本 | 1.4.165-rc.0 |
| 最后验证日期 | 2026-08-03 |
| 文件总数 | 8（README + 7 章教程） |

## 资源链接

- **GitHub**：https://github.com/stablyai/orca
- **官网**：https://www.onorca.dev/
- **下载页**：https://www.onorca.dev/download
- **本地源码**：d:\AI\external\tools\orca