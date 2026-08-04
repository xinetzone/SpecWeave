---
id: "zleap-agent-wiki-readme"
title: "Zleap-Agent workspace-first Agent Harness Wiki 教程"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "agent-harness", "workspace", "agent-runtime", "local-models", "openai-compatible", "postgresql", "memory", "skill", "mcp", "gateway", "feishu", "wechat", "multi-agent"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent 从入门到精通的 workspace-first Agent Harness 结构化 wiki 教程，覆盖核心哲学、整体架构、Workspace 隔离与上下文组装、分区记忆、Skill/工具/权限、模型提供方与运行时入口、网关与定时任务、快速上手、FAQ 与术语表。"
last_verified: "2026-08-04"
wiki_version: "1.0"
zleap_version_target: "0.3.3"
---

# Zleap-Agent workspace-first Agent Harness Wiki 教程

**Workspace Is All Agents Need** —— 面向本地模型与 OpenAI-compatible 模型的 workspace-first Agent Harness。

## 适用人群

| 序号 | 人群 | 核心诉求 |
|------|------|---------|
| 1 | Agent 运行时架构研究者 | 理解"Workspace 隔离"如何在代码层面实现（prompt/tools/memory/history 按空间隔离），学习 Context 组装与缓存断点设计 |
| 2 | 本地模型 / 企业内网部署者 | 评估 Zleap-Agent 对本地小模型、企业内网与数据边界敏感场景的适配性 |
| 3 | 多 Agent 工作流设计者 | 理解 Main→Work 空间路由、`switchWorkspace` 机制、分区记忆与 Skill 复用 |
| 4 | 开源 Agent 框架选型者 | 对比 Web/CLI/IM 网关/定时任务多入口统一运行时（ConversationService）的架构价值 |

## 8 章快速导航

| 章号 | 文件名 | 标题 | 一句话简介 |
|------|--------|------|-----------|
| 00 | [00-overview.md](./00-overview.md) | 项目概述与核心定位 | workspace-first 哲学、"Workspace Is All Agents Need"、项目背景（v0.3.3、预览状态、License 未定）、核心概念初览 |
| 01 | [01-core-architecture.md](./01-core-architecture.md) | 核心架构与技术栈 | pnpm monorepo、13 个 package 职责、PostgreSQL+pgvector 存储、架构分层 |
| 02 | [02-workspace-context.md](./02-workspace-context.md) | Workspace 隔离与上下文组装 | main/work 空间、数据库为唯一真源、路由提示、Context 稳定/半稳定/可变三块组装、缓存断点不变量 |
| 03 | [03-memory-system.md](./03-memory-system.md) | 分区记忆系统 | person/event/experience 三类记忆、A/B 双线、prefetch/recall、RRF 多路径召回、抽取管线 |
| 04 | [04-skills-tools-permissions.md](./04-skills-tools-permissions.md) | Skill 与工具权限 | SKILL.md 入口、SkillRegistry、敏感性审计、request_approval/full_access 权限、MCP Runtime |
| 05 | [05-model-providers-runtime.md](./05-model-providers-runtime.md) | 模型提供方与运行时入口 | OpenAI-compatible/Anthropic、Web UI/CLI、ConversationService 统一数据流 |
| 06 | [06-gateway-tasks.md](./06-gateway-tasks.md) | IM 网关与定时任务 | 飞书/微信接入、ChannelSupervisor、定时任务服务、如何接入 ConversationService |
| 07 | [07-quickstart.md](./07-quickstart.md) | 快速上手指南 | 环境要求、安装、启动 Web UI、配置模型、CLI 使用、常用命令与环境变量 |
| 08 | [08-faq-glossary.md](./08-faq-glossary.md) | FAQ 与术语表 | 常见问题解答 + 核心术语通俗解释 |

## 内容快照声明

> 本教程基于 2026 年 8 月 Zleap-Agent 公开仓库（https://github.com/Zleap-AI/Zleap-Agent）与本地源码（d:\spaces\SpecWeave\external\libs\Zleap-Agent，含 README、package.json 及 10+ 核心源码文件）整理而成，为结构化知识快照性质。项目仍处于早期预览阶段，API、UI、打包与发布流程可能持续变化，后续请以仓库最新代码为准。

| 元数据 | 值 |
|--------|-----|
| Wiki 版本 | **v1.0** |
| 覆盖 Zleap-Agent 版本 | 0.3.3 |
| 最后验证日期 | 2026-08-04 |
| 文件总数 | 9（README + 8 章教程） |

## 架构洞察速览

> 本教程从源码深读中提炼了 5-8 条架构洞察，散布于各章，全部可追溯源码路径。核心包括：
> - **数据库是工作区唯一真源**：代码中无硬编码工作区定义，空间存于数据库，内置默认由 seed 派生（`packages/agent/src/workspaces/index.ts`）。
> - **"变化的记忆永不进入缓存前缀"**：Context 组装按稳定/半稳定/可变三块设计，缓存断点让记忆这类易变内容不会污染缓存前缀（`packages/core/src/context/assembly.ts`）。
> - **所有触发统一走 ConversationService**：Web / 定时任务 / IM 网关都调用同一个 L2 会话层入口（`packages/agent/src/conversation/service.ts`）。
> - **Main→Work 深度为 1**：内核只运行 `session` 主空间，由会话模型自行调用 `switchWorkspace` 路由到子空间（`packages/agent/src/kernel/kernel.ts`）。

## 资源链接

- **GitHub**：https://github.com/Zleap-AI/Zleap-Agent
- **本地源码**：d:\spaces\SpecWeave\external\libs\Zleap-Agent
- **README_EN**：https://github.com/Zleap-AI/Zleap-Agent/blob/main/README_EN.md
- **README_ZH**：https://github.com/Zleap-AI/Zleap-Agent/blob/main/README_ZH.md