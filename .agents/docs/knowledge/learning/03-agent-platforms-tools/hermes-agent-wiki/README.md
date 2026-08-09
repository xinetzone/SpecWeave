---
id: "hermes-agent-wiki-readme"
title: "Hermes Agent 学习 Wiki 教程"
source: "https://github.com/NousResearch/hermes-agent + https://hermes-agent.nousresearch.com/docs/"
category: "learning"
tags: ["hermes", "agent", "self-evolving", "learning-loop", "nous-research", "message-gateway", "skill", "memory", "mcp", "cron", "delegation", "architecture"]
date: "2026-08-10"
status: "stable"
author: "hermes-agent-wiki knowledge-scenario"
summary: "Hermes Agent 从入门到精通的 12 章结构化 Wiki 教程，覆盖产品总览、核心特性、快速上手、CLI/斜杠命令、配置体系、消息网关、工具与工具集、技能系统、记忆系统、MCP/cron/委派扩展、架构解析与源码导读、术语表/FAQ/资源。"
last_verified: "2026-08-10"
wiki_version: "1.0"
description: "Hermes Agent 学习 Wiki 教程：自进化 AI Agent 的唯一内置学习闭环深度解析"
---

# Hermes Agent 学习 Wiki 教程

**唯一内置学习闭环的自进化 AI Agent** —— Nous Research 出品，把"学习"内建到运行时里：从经验创建技能、在使用中改进技能、主动持久化知识、搜索过往对话、跨会话构建深度理解。

## 主题概述

**Hermes Agent**（[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)，MIT 许可）是 Nous Research 构建的自进化 AI Agent。与大多数只做"一次性对话"的 Agent 不同，Hermes 把**学习闭环**内建到了运行时中，并刻意设计为"核心窄腰、能力在边缘"（*core is a narrow waist; capability lives at the edges*），能力以 CLI 命令 + 技能、服务门控工具、插件、MCP 服务器等形式落在核心之外。

本 Wiki 是 Hermes Agent 的**结构化学习教程**，共 12 章，覆盖从产品认知、快速上手到配置、网关、工具、技能、记忆、扩展能力与源码架构的完整知识图谱。所有内容基于官方文档（https://hermes-agent.nousresearch.com/docs/）与公开仓库整理，标注"示例/需验证"处以官方最新为准。

## 适用人群

| 序号 | 人群 | 核心诉求 |
|------|------|---------|
| 1 | 想快速上手 Agent 的开发者 | 一键安装、初始化配置、第一个对话、常用 CLI/斜杠命令 |
| 2 | 深度集成 / 能力接入者 | 配置体系、消息网关、工具集、技能系统、记忆系统与 MCP/cron/委派扩展 |
| 3 | 架构与源码研究者 | AIAgent 核心循环、整体架构、gateway 架构、项目结构与插件系统 |

## 📄 12 章导航

| 章号 | 章节 | 一句话摘要 |
|------|------|-----------|
| 00 | [产品总览](00-overview.md) | Hermes 的定位（唯一内置学习闭环）、三种运行形态、"核心窄腰/能力在边缘"设计哲学与两条近乎不可破坏的属性 |
| 01 | [核心特性详解](01-core-features.md) | 七大核心能力：TUI、约 28 平台消息网关、闭环学习、cron 自动化、委派并行、随处运行、研究就绪 |
| 02 | [快速安装与上手](02-quickstart.md) | 一键安装（install.sh/ps1）、初始化配置、第一个对话、升级与疑难速查 |
| 03 | [CLI 与斜杠命令详解](03-cli-commands.md) | `hermes` 子命令族、会话内斜杠命令，以及 COMMAND_REGISTRY 集中注册机制 |
| 04 | [配置体系](04-configuration.md) | config.yaml 分层、.env 密钥隔离、HERMES_HOME、profiles 多实例、配置优先级 |
| 05 | [消息网关](05-messaging-gateway.md) | 约 28 平台支持、单进程多平台、跨平台会话连续、relay 连接器 |
| 06 | [工具与工具集](06-tools-toolsets.md) | 40+ 内置工具、TOOLSETS 工具集、Footprint Ladder 决策、服务门控 `check_fn` |
| 07 | [技能系统](07-skills.md) | SKILL.md 标准、bundled/optional 分层、技能中心、curator 生命周期 |
| 08 | [记忆系统](08-memory.md) | MEMORY.md/USER.md、memory provider ABC、Honcho 辩证式建模、FTS5 会话搜索 |
| 09 | [扩展能力：MCP/cron/委派](09-extensions-cron-delegation.md) | MCP 集成、自然语言 cron 调度、delegate_task 并行委派与 leaf/orchestrator 角色 |
| 10 | [架构解析与源码导读](10-architecture-source.md) | AIAgent 核心循环、整体架构、Gateway 架构、项目结构与关键文件、插件系统 |
| 11 | [术语表/FAQ/资源](11-glossary-faq-resources.md) | 术语速查、常见问题、官方资源链接与相关 Wiki 交叉引用 |

## 📖 三条阅读路径

根据目标选择路径：

### 路径一：新手快速上手（想立刻跑通）
```
00-overview.md → 02-quickstart.md → 03-cli-commands.md → 11-glossary-faq-resources.md
```
先建立产品认知，再按官方安装流程跑通第一个对话，掌握常用命令，遇到问题查 FAQ。

### 路径二：开发者深度集成（想完整掌握能力面）
```
00-overview.md → 04-configuration.md → 05-messaging-gateway.md → 06-tools-toolsets.md → 07-skills.md → 08-memory.md → 09-extensions-cron-delegation.md
```
系统理解配置、网关、工具集、技能、记忆与 MCP/cron/委派扩展，把 Hermes 用成生产力工具。

### 路径三：架构源码研究（想理解内部实现）
```
00-overview.md → 10-architecture-source.md → 03-cli-commands.md → 06-tools-toolsets.md → 01-core-features.md
```
以 AIAgent 核心循环为起点，结合 COMMAND_REGISTRY、Footprint Ladder 与项目结构，理解"核心窄腰、能力在边缘"如何在代码中落地。

## 🧭 前置知识

深入阅读前建议先了解以下互补内容：

- [Hermes Agent 集成指南](../hermes-agent-integration/README.md) — 如何把 SpecWeave 等能力/知识库接入 Hermes（插件路径 + OKF 记忆层）
- [Hermes OKF Wiki 教程](../../01-agent-protocols-interfaces/okf-wiki/README.md) — OKF 开放知识格式、Bundle/Concept/Frontmatter 基础（Hermes 记忆层常配合 OKF 使用）

> 若你对"能力接入"或"知识持久化"更感兴趣，可优先阅读上述两个链接；本 Wiki 侧重 Hermes 本体（产品、特性、安装、命令、架构）。

## 🔗 资源链接

- **官方文档**：https://hermes-agent.nousresearch.com/docs/
- **GitHub 仓库**：https://github.com/NousResearch/hermes-agent
- **社区/支持**：Nous Research Discord（链接见仓库 README）
- **中文说明**：仓库 `README.zh-CN.md`

## 🔗 相关 Wiki 交叉引用

- [Hermes Agent 集成指南](../hermes-agent-integration/README.md) — Hermes 能力接入实战（本 Wiki 为 Hermes 本体学习教程，二者互补）
- [Hermes OKF Wiki 教程](../../01-agent-protocols-interfaces/okf-wiki/README.md) — OKF 开放知识格式（Hermes 记忆层常配合使用）
