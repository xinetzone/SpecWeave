---
id: "zleap-agent-wiki-overview"
title: "项目概述与核心定位"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "workspace-first", "agent-harness", "context", "local-models"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent 项目概述与核心定位：workspace-first 的 Agent Harness，核心命题是'Agent 先知道自己身处哪个 Workspace，再只拿到该 Workspace 需要的上下文'，而非把所有工具/记忆/规则/历史塞进一个大 prompt。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 00 项目概述与核心定位

## 一句话定位

> **Zleap-Agent 是一个 workspace-first 的 Agent Harness（Agent 运行时框架），面向本地模型与 OpenAI-compatible 模型**，核心宣称是 **"Workspace Is All Agents Need"**。

它不把上下文当作一段越来越长的大 prompt，而是把 Agent 运行时拆成多个 **Workspace（工作区）**，每个 Workspace 拥有自己的提示词、工具、技能、记忆、模型和执行历史。这构成了本教程其余七章（核心架构、Workspace 隔离与上下文组装、分区记忆、Skill 与工具权限、模型提供方与运行时入口、网关与定时任务、快速上手、FAQ 与术语表）的认知基座。

## 核心哲学与设计动机

Zleap-Agent 围绕一个非常实际的判断构建：

> 一个 Agent 不应该在每一步都看到所有工具、记忆、规则和历史消息。它应该**先知道自己在哪个 Workspace**，然后**只拿到这个 Workspace 真正需要的上下文**。

这一判断源于对三类场景的观察：

| 场景 | 单一大 prompt 的痛点 | Zleap-Agent 的应对 |
|------|--------------------|-------------------|
| 本地小模型 | 上下文窗口有限，塞满无关内容会损耗注意力、提升成本 | 按 Workspace 隔离，只加载当前空间需要的上下文 |
| 企业内网部署 | 需要严格的权限与数据边界 | 每个 Workspace 是权限与数据隔离边界 |
| 复杂工作流 | 工具/记忆/规则混杂难以推理 | 每个空间独立组合 prompt/tools/memory/history |

## 项目背景

| 维度 | 详情 |
|------|------|
| 出品方 | Zleap-AI（GitHub 组织） |
| 仓库 | https://github.com/Zleap-AI/Zleap-Agent |
| 当前版本 | **0.3.3**（package.json） |
| 项目状态 | **早期预览（Preview）**，API/UI/打包/发布流程稳定前可能持续调整 |
| License | **尚未最终确定**（预览版请勿假设生产再分发授权） |
| 技术栈 | Node.js 20+、TypeScript、pnpm 9.x、Next.js、PostgreSQL + pgvector、Tauri（桌面端） |

## 亮点

- **Workspace 隔离**：提示词、工具、技能、模型、记忆和历史按空间隔离。
- **Web UI**：对话、空间、助手、模型、工具、MCP、技能、记忆、任务、网关配置和产物管理。
- **CLI**：与 Web UI 共用同一套运行时。
- **PostgreSQL 持久化**：记忆与运行时状态使用 PostgreSQL + pgvector。
- **内置工具**：文件、命令、系统、MCP 工具支持。
- **双权限模式**：请求审批（approval-required）与完全访问（full-access）。
- **任务 Worker 与 IM 网关**：为长任务与外部渠道（飞书/微信）工作流提供基础。
- **模型提供方**：OpenAI-compatible 为主，仓库含 Anthropic provider 代码。

## 核心概念初览

本章先给四个核心概念一个"一句话"定义，后续章节逐一展开：

| 概念 | 一句话定义 |
|------|-----------|
| **Workspace** | 不只是工具分组，而是 Agent 可见上下文与可执行动作的**隔离边界**。常见如 `Main`（对话/路由）、`Cli`（文件/命令）、`Web Search`（搜索/读网页）及自定义领域工作台。 |
| **Context Layout** | 上下文视为运行时布局：`Context = System Prompt + Workspace Prompt + Tools + Memory + History`，运行时不会把所有内容塞进每一轮。 |
| **Memory** | 分区管理而非一个泛化大桶：人（person，用户偏好与稳定事实）、事（event，与用户/任务/空间相关的状态）、经验（experience，从已完成任务中沉淀的可复用方法），存储于 PostgreSQL。 |
| **Skill** | 可复用能力包，通常以 `SKILL.md` 为入口。工具是 API，Skill 是工作流、说明、示例与配套资源。 |

## 本章小结

- Zleap-Agent 不是另一款"聊天框"，而是一个 **workspace-first 的 Agent Harness**——核心命题是"按空间隔离 Agent 上下文与动作"。
- 它面向本地/OpenAI-compatible 模型，尤其适合本地小模型、企业内网与数据边界敏感场景。
- 当前处于早期预览（v0.3.3），License 未定，适合源码阅读、本地开发与反馈，不建议直接用于生产分发。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← 这是教程第 1 章 | [README](./README.md) | → [01 核心架构与技术栈](./01-core-architecture.md) |