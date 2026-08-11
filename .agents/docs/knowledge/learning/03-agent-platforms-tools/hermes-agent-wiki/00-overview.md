---
id: "hermes-agent-wiki-00-overview"
title: "00 Hermes Agent 产品总览"
source: "NousResearch/hermes-agent 本地源码仓库（README.zh-CN.md / AGENTS.md / website/docs/architecture.md）"
type: "Wiki Tutorial"
description: "Hermes Agent 产品总览：定位、学习闭环、运行形态、设计哲学、章节导航与前置知识"
status: "stable"
category: "learning"
tags: ["hermes", "agent", "overview", "self-evolving", "narrow-waist"]
date: "2026-08-10"
author: "hermes-agent-wiki knowledge-scenario"
summary: "Hermes 是 Nous Research 构建的自进化 AI Agent，唯一内置学习闭环；核心窄腰、能力在边缘的设计哲学由两项属性塑造"
last_verified: "2026-08-10"
wiki_version: "1.0"
---
# 00 Hermes Agent 产品总览

## 0.1 Hermes 是什么

**Hermes Agent**（仓库 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)）是 **Nous Research** 构建的自进化 AI Agent，采用 **MIT 许可**（见仓库 `LICENSE`）。它被称为**唯一内置学习闭环的智能代理**——与大多数只做"一次性对话"的 Agent 不同，Hermes 把学习内建到了运行时里。

官方定位（README.zh-CN.md 原文语义）概括为五个核心能力：

- **从经验中创建技能**：复杂任务完成后，自动把可复用的步骤沉淀为"技能"（skill）
- **在使用中改进技能**：技能不是一次性产物，会在后续使用中自我改进
- **主动持久化知识**：把关于你、项目、环境的观察写进持久记忆
- **搜索过往对话**：基于 FTS5 全文索引回溯历史会话
- **跨会话构建深度理解**：在多次对话之间逐步累积对你的认识

> 一句话理解：Hermes 不绑定你的笔记本，也不只是"回答问题"。它在一个长期、自学习的循环里持续演化，且能把这份能力带到 Telegram、Discord 等任何它"所在"的地方。

## 0.2 运行形态：从 $5 VPS 到 GPU 集群到 Serverless

Hermes 刻意设计为"随处运行、不绑定单一机器"。官方 README 给出的三种典型形态：

| 运行形态 | 说明 |
|---------|------|
| **$5 VPS** | 低成本云主机即可承载完整代理，适合个人长期运行 |
| **GPU 集群** | 需要大规模并行、批量轨迹生成时扩展到 GPU 资源 |
| **Serverless** | 借助 Modal、Daytona 等后端，空闲时休眠、按需唤醒，空闲期近乎零成本 |

典型场景：你在 Telegram 上给它发消息，而它实际上运行在一台云端 VM 上。终端后端（terminal backend）支持六种：本地（local）、Docker、SSH、Daytona、Singularity、Modal。

## 0.3 核心窄腰、能力在边缘的设计哲学

Hermes 的架构哲学是**"核心窄腰、能力在边缘"**（*core is a narrow waist; capability lives at the edges*）。含义是：

- **核心（窄腰）**：agent 核心循环（`run_agent.py` 的 `AIAgent`）尽量保持小而稳定，不轻易膨胀
- **边缘（能力）**：绝大多数新能力以 CLI 命令 + 技能（skill）、服务门控工具、插件（plugin）、MCP 服务器等形式落在核心之外，而不是堆进核心

官方在 AGENTS.md 中明确提出评估任何改动时的**"Footprint Ladder"（占用阶梯）**，从低占用到高占用排列：

1. 扩展现有代码（零新增表面）
2. **CLI 命令 + 技能**（默认首选，零模型工具占用）
3. 服务门控工具（`check_fn`，仅在满足前置条件时出现）
4. 插件（plugin，落在外置目录）
5. MCP 服务器（加进目录）
6. 新增核心工具（最后手段）

## 0.4 两项塑造设计决策的属性

AGENTS.md 明确列出**两条近乎不可破坏的属性**，它们决定了几乎所有设计取舍，也是代码评审的透镜：

**① 对话内提示词缓存神圣不可破坏（prompt caching is sacred）。**
长期会话的每一轮都会复用缓存的前缀。任何"中途篡改过去上下文、切换工具集、重建系统提示"的操作都会使缓存失效，从而成倍抬高用户的成本。因此设计上不允许在会话中途做这些事——唯一例外是上下文压缩（context compression）。这也是为什么技能（skill）等会改变系统提示状态的能力默认采用"延迟到下一会话生效"，并提供显式的 `--now` 立即生效开关。

**② 核心窄腰（narrow waist）。**
每一个新增的核心模型工具（model tool）都会随每次 API 调用发送给模型，因此新增**核心**工具的门槛极高。新能力应优先以 CLI 命令 + 技能、服务门控工具、插件、MCP 服务器的方式落地，而非扩成核心表面。用原文概括：**"我们在边缘激进扩张，在核心保守克制"**（*expansive at the edges and conservative at the waist*）。

## 0.5 章节导航

| 章节 | 内容 | 适合场景 |
|------|------|---------|
| [01 核心特性详解](01-core-features.md) | TUI、消息网关、闭环学习、cron、委派、随处运行、研究就绪 | 想了解能做什么 |
| [02 快速安装与上手](02-quickstart.md) | 安装、初始化、第一个对话、升级 | 想立刻跑通 |
| [03 CLI 与斜杠命令详解](03-cli-commands.md) | hermes 子命令、斜杠命令、COMMAND_REGISTRY | 想掌握操作 |

建议阅读顺序：先读本总览（00）建立全局认知，再按需进入 01 了解特性、02 上手、03 深入命令。

## 0.6 前置知识

本 Wiki 与项目内其他文档互补。深入阅读前建议先了解：

- [Hermes Agent 集成指南](../hermes-agent-integration/README.md) — 如何把 SpecWeave 等能力/知识库接入 Hermes（插件路径 + OKF 记忆层）
- [OKF Wiki 教程](../../01-agent-protocols-interfaces/okf-wiki/README.md) — OKF 开放知识格式、Bundle/Concept/Frontmatter 基础（Hermes 记忆层常配合 OKF 使用）

> 若你对"能力接入"或"知识持久化"更感兴趣，可优先阅读上述两个链接；本 Wiki 侧重 Hermes 本体（产品、特性、安装、命令）。
