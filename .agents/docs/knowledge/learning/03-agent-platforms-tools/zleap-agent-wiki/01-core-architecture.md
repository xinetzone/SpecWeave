---
id: "zleap-agent-wiki-core-architecture"
title: "核心架构与技术栈"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "architecture", "monorepo", "pnpm", "postgresql", "pgvector", "packages"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent 核心架构与技术栈：pnpm monorepo、TypeScript、13 个 package 职责、PostgreSQL+pgvector 存储、四层架构分层（模型层/运行时/会话服务/网关/存储）。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 01 核心架构与技术栈

## 技术栈总览

| 维度 | 选型 |
|------|------|
| 语言 | TypeScript（全仓 ESM，`"type": "module"`） |
| 包管理 | **pnpm 9.15.0**（monorepo workspace） |
| 运行时 | Node.js 20+ |
| 后端存储 | **PostgreSQL + pgvector**（记忆、技能、任务、会话持久化） |
| Web UI | **Next.js**（packages/web） |
| 桌面端 | **Tauri**（Rust + Web，packages/desktop） |
| 测试 | Vitest 2.x |
| 代码规范 | commitlint + husky（Conventional Commits） |

## Monorepo 结构

Zleap-Agent 采用 pnpm workspace 的 monorepo 布局，所有业务代码集中在 `packages/` 下，根目录 `package.json` 提供 `dev:web`、`dev:tasks`、`dev:gateway`、`cli`、`build`、`check`、`test` 等统一脚本。

## 13 个 Package 职责

| Package | 目录 | 核心职责 |
|---------|------|---------|
| `@zleap/ai` | `packages/ai` | 模型提供方与模型调用抽象（OpenAI-compatible / Anthropic / SSE 流式 / 注册表） |
| `@zleap/agent` | `packages/agent` | **核心 Agent 运行时**：Workspace、Skill、Tool、Memory、permissions、turn loop、conversation service |
| `@zleap/avatar` | `packages/avatar` | inbound、scheduled、web-chat 运行组装（run assembly） |
| `@zleap/cli` | `packages/cli` | 终端 UI 与 CLI 入口（init/config/sessions/connect/serve 等） |
| `@zleap/core` | `packages/core` | 共享类型与策略基础（workspace、memory、skills、tools、toolPolicy、runtime、records） |
| `@zleap/gateway` | `packages/gateway` | 飞书、微信、飞书 CLI 等 IM 网关 worker |
| `@zleap/host` | `packages/host` | 本地 supervisor、Postgres bootstrap、安装/更新辅助 |
| `@zleap/runtime` | `packages/runtime` | 面向运行时的 workspace 与 conversation API |
| `@zleap/store` | `packages/store` | PostgreSQL 存储、迁移、召回逻辑（抽取、RRF、record-memory） |
| `@zleap/tasks` | `packages/tasks` | 定时任务服务与 worker（cron/queue/execution） |
| `@zleap/web` | `packages/web` | Next.js Web UI |
| `@zleap/desktop` | `packages/desktop` | Tauri 桌面端（可选） |
| `@zleap-ai/cli` | `packages/cli`（别名） | CLI 发布包（`@zleap-ai/cli`） |

## 架构分层

从数据流看，Zleap-Agent 大致可分为五层：

```text
┌─────────────────────────────────────────────────────────────┐
│  入口层：Web UI (Next.js) / CLI / IM 网关 / 定时任务 Worker   │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  会话服务层：ConversationService（统一 inbound→reply 入口）   │
│  packages/agent/src/conversation/service.ts                 │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  核心运行时：Kernel → Workspace → Turn Loop → ChatEngine      │
│  packages/agent + packages/core + packages/runtime          │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  模型层：ProviderRegistry / ModelRegistry（OpenAI/Anthropic）│
│  packages/ai                                                │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  存储层：PostgreSQL + pgvector（记忆/技能/任务/会话）          │
│  packages/store（抽取、RRF、迁移）                            │
└─────────────────────────────────────────────────────────────┘
```

## 后端存储：PostgreSQL + pgvector

- **为什么选 PostgreSQL**：记忆参与 Agent 每一轮运行，需要检索、隔离、审计与回滚能力；pgvector 提供向量检索支撑。
- **store 包**（`packages/store`）负责：schema 定义、迁移（`migrate.ts`）、seed（`seed.ts`）、核心抽取管线（`core/extract.ts`）、记录记忆（`core/record-memory.ts`）、RRF 召回融合（`core/rrf.ts`）。

## 架构洞察

> **洞察 1：分层解耦使"多入口共用同一运行时"成为可能。** 所有入口（Web/CLI/网关/任务）最终都汇聚到 `ConversationService`，再由它调用核心运行时与模型层。这让 Agent 的"智能"逻辑只写一遍，入口层只是薄适配（来源：`packages/agent/src/conversation/service.ts`）。

> **洞察 2：存储是第一等公民，而非可选插件。** 记忆、技能、任务、会话全部持久化到 PostgreSQL，而非留在内存或文件里。这保证了长任务、多入口、进程重启后的状态一致性（来源：`packages/store/src/store.ts`、`packages/host/src/postgres.ts`）。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [00 项目概述与核心定位](./00-overview.md) | [README](./README.md) | → [02 Workspace 隔离与上下文组装](./02-workspace-context.md) |