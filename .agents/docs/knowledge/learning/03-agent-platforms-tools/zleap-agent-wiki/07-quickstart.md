---
id: "zleap-agent-wiki-quickstart"
title: "快速上手指南"
source: "https://github.com/Zleap-AI/Zleap-Agent (README) + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "quickstart", "install", "setup", "cli", "web-ui", "environment-variables", "pnpm"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent 快速上手指南：环境要求、安装依赖、启动 Web UI、配置模型、CLI 使用、一次性运行、常用命令与环境变量表。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 07 快速上手指南

## 环境要求

- **Node.js 20+**
- **pnpm 9.x**
- **Docker Desktop**，或一个可连接的 **PostgreSQL + pgvector** 数据库

## 安装依赖

```bash
git clone https://github.com/Zleap-AI/Zleap-Agent.git
cd Zleap-Agent

corepack enable
corepack prepare pnpm@9.15.0 --activate
pnpm install
```

## 启动 Web UI

```bash
pnpm dev:web
```

该命令会执行本地开发路径：

1. 读取仓库根目录环境变量文件（存在时）。
2. 启动或连接 PostgreSQL。
3. 构建必要的 workspace packages。
4. 执行数据库迁移。
5. 启动 Next.js Web UI。

打开：

```text
http://localhost:3000
```

如果已有自己的 PostgreSQL：

```bash
ZLEAP_DATABASE_URL=postgres://user:password@127.0.0.1:5432/zleap pnpm dev:web
```

## 配置模型

在 Web UI 的**设置**里添加一个 OpenAI-compatible 模型提供方。CLI 实验也可使用环境变量：

```bash
ZLEAP_MODEL_BASE_URL=https://api.example.com/v1
ZLEAP_MODEL_API_KEY=sk-...
ZLEAP_MODEL_NAME=qwen3.6-flash
```

## CLI 使用

启动交互式 CLI：

```bash
pnpm cli
```

一次性运行：

```bash
ZLEAP_MODEL_BASE_URL=https://api.example.com/v1 \
ZLEAP_MODEL_API_KEY=sk-... \
ZLEAP_MODEL_NAME=qwen3.6-flash \
ZLEAP_DATABASE_URL=postgres://zleap:zleap@127.0.0.1:5433/zleap \
pnpm --filter @zleap-ai/cli start -- "总结这个仓库"
```

一次性模式允许高风险工具自动执行：

```bash
pnpm --filter @zleap-ai/cli start -- --yes "在当前目录生成 README 草稿"
```

## 常用命令

```bash
pnpm dev:web       # Web UI 开发循环
pnpm dev           # Web UI + 任务 worker + 网关开发循环
pnpm dev:tasks     # 仅启动任务 worker
pnpm dev:gateway   # 仅启动 IM 网关 worker
pnpm cli           # 启动 CLI
pnpm build         # 构建所有 packages
pnpm check         # 构建并执行类型检查
pnpm test          # 运行 package tests
```

## 环境变量

| 变量 | 说明 |
| --- | --- |
| `ZLEAP_DATABASE_URL` | PostgreSQL 连接串，用于持久化、记忆、技能和任务 |
| `ZLEAP_MODEL_BASE_URL` | OpenAI-compatible LLM base URL |
| `ZLEAP_MODEL_API_KEY` | LLM API key |
| `ZLEAP_MODEL_NAME` | 默认 LLM 模型名 |
| `ZLEAP_EMBED_BASE_URL` | Embedding provider base URL |
| `ZLEAP_EMBED_API_KEY` | Embedding provider API key |
| `ZLEAP_EMBED_MODEL` | Embedding 模型名 |
| `ZLEAP_EMBED_DIM` | Embedding 向量维度 |
| `ZLEAP_FILE_WORKSPACE_ROOT` | 未选择项目时的默认文件工作区根目录 |
| `ZLEAP_WEB_SKILLS_ROOT` | Web UI 扫描的本地技能目录 |

## 本章小结

- 从源码启动只需 Node.js 20+、pnpm 9.x 与 PostgreSQL + pgvector。
- `pnpm dev:web` 一键拉起 Web UI（含数据库、构建、迁移、Next.js）。
- 配置模型用环境变量或 Web UI 设置，CLI 与 Web 共用同一运行时。
- 常用命令覆盖开发、构建、检查、测试、网关与任务 worker。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [06 IM 网关与定时任务](./06-gateway-tasks.md) | [README](./README.md) | → [08 FAQ 与术语表](./08-faq-glossary.md) |