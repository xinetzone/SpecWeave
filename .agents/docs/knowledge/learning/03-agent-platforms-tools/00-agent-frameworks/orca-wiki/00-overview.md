---
id: "orca-wiki-overview"
title: "项目概述与核心定位"
source: "https://www.onorca.dev/ 官网 + d:\AI\external\tools\orca 本地开源源码"
category: "learning"
tags: ["orca", "stablyai", "ai-orchestrator", "agent-ide", "worktree", "claude-code", "codex", "opencode", "parallel-agents", "multi-agent", "yc"]
date: "2026-08-03"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Orca 项目概述与核心定位：面向 100x 构建者的 AI 编排器，并排运行多个 Agent 于隔离 worktree，一段话核心价值 + 传统多 Agent 开发痛点 vs Orca 解决方案对照表 + 平台支持矩阵"
last_verified: "2026-08-03"
wiki_version: "1.0"

---

# 00 项目概述与核心定位

## 一句话定位

> **Orca 是面向 100x 构建者的 AI 编排器（AI Orchestrator for 100x builders）**，官网定位为 **"Ship 100x With The Agent IDE"**。

它让开发者**并排运行 Codex、Claude Code、OpenCode、Pi 等多个 Agent**，每个 Agent 都在**彼此隔离的 git worktree** 中运行，并在**一个地方统一跟踪**——这构成了本教程其余七章（核心架构、八大核心功能、Orca CLI 与多 Agent 编排、支持的 Agent 清单、快速上手、价值总结与行业趋势、FAQ 与术语表）的认知基座。

## 项目背景

| 维度 | 详情 |
|------|------|
| 出品方 | **Stably.ai** |
| 投资背书 | **YC（Y Combinator）** 孵化 |
| 开源协议 | **MIT** 协议，自由开源 |
| 开源热度 | GitHub 约 **35.2k Star** 且持续增长 |
| 迭代节奏 | **每日更新**（daily ship），功能列表以 [changelog](https://github.com/stablyai/orca/releases) 为准 |
| GitHub 仓库 | https://github.com/stablyai/orca |
| 官网 | https://www.onorca.dev/ |

> 因为每日更新，"功能清单永远追不上产品迭代"，README 也明确说明 changelog 才是真正的功能列表。本教程所覆盖的版本基准为 `1.4.165-rc.0`（详见 [README](./README.md) 内容快照声明）。

## 核心价值一句话

传统多 Agent 开发方式的核心痛点在于**多个 Agent 各自为政、工作区互相污染、结果难以统一跟踪与择优**。Orca 用「隔离 worktree + 统一编排」的方式解决：

> **把一个提示同时分发给多个 Agent，每个 Agent 在自己的隔离 git worktree 中运行，比较结果后合并最佳方案，全程在一个地方跟踪。**

## 平台支持

| 端 | 平台 | 说明 |
|----|------|------|
| 桌面端 | macOS / Windows / Linux | 主应用，支持并行 worktree、终端分屏、设计模式等核心能力 |
| 移动端 | iOS / Android | **Companion（伴侣）应用**，与桌面端配对，用于监控并远程指挥 Agent |

## 传统多 Agent 开发痛点 vs Orca 解决方案

| 传统多 Agent 开发痛点 | Orca 解决方案 |
|----------------------|--------------|
| 多个 Agent 共用同一工作区，文件互相覆盖、改动互相污染 | 每个 Agent 运行在**隔离的 git worktree** 中，互不干扰 |
| 手动来回切换不同 Agent 的终端窗口，上下文支离破碎 | 一个应用内**统一跟踪**所有 Agent，无需切换上下文 |
| 同一任务想对比多个方案，只能逐个串行跑、手动比对 | 把一个提示**并行分发给多个 Agent**，同时比较结果 |
| 只能依赖单一 Agent，无法发挥不同 Agent 的差异化优势 | 自由混跑 Codex、Claude Code、OpenCode、Pi 等 **25+ CLI Agent** |
| 被锁定在某一款 Agent 的生态里，无法更换 | 与**任意 CLI Agent** 兼容——只要能在终端跑，就能在 Orca 跑 |
| 离开电脑就无法跟进 Agent 进度 | iOS / Android **Companion 应用**，手机随时监控并下发后续指令 |
| 多 Agent 结果择优后合并费时费力 | 内置 diff 评审、标注与合并流程，支持**择优合并** |

## 本章小结

- Orca 不是又一款"代码编辑器"，而是一个**把 Agent 作为一等公民进行编排的 Agent IDE**——核心命题是"一个地方并排运行、隔离跟踪多个 Agent"。
- 它出身 Stably.ai、背靠 YC、MIT 开源、约 35.2k Star 且每日更新，生态与迭代动能强劲。
- 桌面端覆盖主流三大系统，移动端 Companion 补齐了远程监控短板，形成"桌边 + 手掌"双端闭环。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← 这是教程第 1 章 | [README](./README.md) | → [01 核心架构与技术栈](./01-core-architecture.md) |