---
title: "Multica 平台：AI Agent 协作管理平台"
category: learning
tags: [karpathy, llm, coding, agent, multica, platform, managed-agents, agentic-engineering, runtime, daemon, skill, autopilot, squad]
date: "2026-07-02"
status: stable
author: "multica-ai"
summary: "Multica 是开源的 Managed Agents 平台，将编码 Agent 变成真正的队友——分配任务、跟踪进度、积累技能。本文档介绍 Multica 平台的核心概念、架构、功能模块，以及它与 Karpathy 准则的关系。"
source: "https://github.com/multica-ai/multica"
---

# Multica 平台：AI Agent 协作管理平台

> **Multiplexed Information and Computing Agent** — 向 1960 年代的 Multics 分时系统致敬。Multics 让多个用户共享同一台机器；Multica 让人类和 AI Agent 共享同一个任务看板。

## 平台定位

**Multica 不是一个 AI 工具，而是一个人 + AI 协作的任务管理平台。**

| 传统 AI 编程痛点 | Multica 的解法 |
|-----------------|---------------|
| 每次复制粘贴 prompt | Agent 有 profile，自动挂载技能和工作区上下文 |
| 必须盯着终端看它跑完 | WebSocket 实时推送进度，完成后 Inbox 通知 |
| 没有跨任务记忆 | Session Resumption 自动恢复会话和工作目录 |
| 多 Agent 工作没有全局视图 | Agent 和人共用同一个 Issue 看板 |
| 知识无法沉淀 | Skill 系统让解决方案变成全团队可复用的能力 |

**一句话**：像给同事分配任务一样给 Agent 分配 Issue——它们自主认领、写代码、汇报进度、更新状态、报告阻塞。

### 为什么叫 Multica？

名字致敬 1960 年代的 Multics 分时操作系统：
- Multics 首创分时共享，让多个用户像独占机器一样使用同一台计算机
- Unix 是 Multics 的简化版，强调"一个用户、一个任务、一种优雅"
- Multica 把"分时"带回 AI 时代——今天多路复用的"用户"既包括人类，也包括自主 Agent

> "你的下一批员工，不是人类。" —— Multica Slogan

---

## 核心概念词典

理解这些名词是理解 Multica 的前提，每个概念严格对应数据库表：

| 概念 | 定义 | 核心数据表 |
|------|------|-----------|
| **User 用户** | 人类账号，可属于多个 Workspace | `user` |
| **Workspace 工作区** | 一切资源的容器（多租户边界），类似 Linear/Notion 的 team | `workspace` |
| **Member 成员** | 用户在某个 Workspace 中的身份（owner/admin/member） | `member` |
| **Agent 智能体** | 可被指派任务的 AI 工作者，有名字/头像/说明书/绑定的 Runtime | `agent` |
| **Runtime 运行时** | Agent 实际执行的环境（本地机器或云端），一个 Runtime = 一台能跑 Agent 的机器 | `agent_runtime` |
| **Daemon 守护进程** | 用户本地运行的后台程序，自动探测 CLI、注册 Runtime、轮询认领任务 | （进程，非表） |
| **Issue 议题** | 核心工作单元（任务/bug/feature），可分配给人或 Agent | `issue` |
| **Comment 评论** | Issue 下的讨论，`@agent` 会自动触发新任务 | `comment` |
| **Task 任务** | Agent 执行一次 Issue 产生的一次运行（队列化） | `agent_task_queue` |
| **Skill 技能** | 工作区级可复用说明文档，Agent 开跑时注入上下文 | `skill`, `skill_file` |
| **Squad 小队** | 多个 Agent + 人类组成的小队，由 Leader Agent 路由任务 | `squad` |
| **Autopilot 自动驾驶** | 定时/Webhook/手动触发的自动化规则，自动创建 Issue 分配给 Agent | `autopilot` |
| **Chat 对话** | 用户与 Agent 的持久化多轮对话（不依附于 Issue） | `chat_session` |
| **Inbox 收件箱** | 个人通知中心（被@、被分配、任务完成等） | `inbox_item` |
| **Project 项目** | Issue 的高层容器（类似 Epic/里程碑） | `project` |
| **MCP** | Model Context Protocol，Agent 可配置的外部工具服务器列表 | `agent.mcp_config` (JSONB) |

### 多态行动者（Polymorphic Actor）

Multica 最核心的设计范式：几乎所有"谁做了什么"的字段都是 `actor_type`（`member`/`agent`）+ `actor_id`。

这就是为什么 Agent 能像人一样：
- 创建 Issue
- 发评论
- 被分配任务
- 被 @ 提到
- 出现在看板上
- 收到 Inbox 通知

---

## 支持的 Coding Agent

Multica **不自己训练模型**，也不锁定厂商。它是调度器，本地 Daemon 自动探测以下 CLI：

| Agent CLI | 说明 |
|-----------|------|
| **Claude Code** | Anthropic 官方 CLI |
| **Codex** | OpenAI 官方 CLI |
| **GitHub Copilot CLI** | GitHub Copilot 命令行 |
| **OpenClaw** | 开源 Agent 框架 |
| **OpenCode** | 开源编码 Agent |
| **Hermes** | 开源 Agent |
| **Gemini** | Google Gemini CLI |
| **Pi** | 相关 Agent CLI |
| **Cursor Agent** | Cursor 编辑器内置 Agent |
| **Kimi** | 月之暗面 Kimi CLI |
| **Kiro CLI** | Kiro 编辑器 CLI |
| **Qoder CLI** | Qoder 编程工具 |

每个 Agent 可以独立配置：模型选择、API Key、环境变量、MCP 服务器、自定义启动参数。

---

## 系统架构

```
┌─────────────────────┐        ┌────────────────────┐        ┌──────────────────┐
│  Next.js Web App    │        │  Electron Desktop  │        │  multica CLI     │
│  apps/web           │        │  apps/desktop      │        │  server/cmd/     │
└──────────┬──────────┘        └──────────┬─────────┘        └────────┬─────────┘
           │  HTTP + WebSocket             │                           │  HTTP
           │                               │                           │
           └──────────────┬────────────────┴───────────────┬───────────┘
                          │                                │
                          ▼                                ▼
              ┌─────────────────────────────────────────────────┐
              │               Go Backend (server/)              │
              │  • Chi HTTP router  • gorilla/websocket hub      │
              │  • sqlc generated queries                        │
              │  • In-process event bus                          │
              │  • Background workers (sweeper / scheduler)      │
              └──────────────────┬──────────────────────────────┘
                                 │
                                 ▼
                      ┌──────────────────────┐
                      │  PostgreSQL 17       │
                      │  + pgvector          │
                      │  (28 tables)         │
                      └──────────────────────┘

                                 ▲
                                 │ HTTPS poll + heartbeat
                                 │
              ┌─────────────────────────────────────────────────┐
              │         Local Daemon (用户机器上运行)            │
              │  • 每 3s 认领任务  • 每 15s 心跳                 │
              │  • 探测并启动 agent CLI 子进程                   │
              │  • 为任务准备隔离工作目录                        │
              └───────────────┬─────────────────────────────────┘
                              │ spawns
              ┌───────────────┼─────────────────────────────────┐
              ▼               ▼              ▼              ▼
         Claude Code      Codex         OpenCode      …其他 CLI
         (子进程)         (子进程)      (子进程)
```

### 分层职责

| 层 | 负责什么 | 不负责什么 |
|---|---|---|
| **Web / Desktop 客户端** | UI、本地状态（Zustand）、服务器缓存（TanStack Query）、WebSocket 订阅 | 业务规则、AI 调用 |
| **Server（Go）** | 持久化、权限、任务编排、事件广播、Autopilot 调度、Runtime 健康监测 | 不直接执行 Agent、不调 LLM |
| **Daemon（本地）** | 探测本地 CLI、管理工作目录、流式上报消息、Session 恢复 | 不做业务决策、只认 Server 给的任务 |
| **Agent CLI（Claude Code 等）** | 实际调用 LLM、执行工具、写文件、跑测试 | 不感知 Multica 数据模型（上下文通过 `multica` CLI 读回） |

### 关键设计：Server 不执行 Agent

**Multica 本身不直接调用 LLM API**。所有 LLM 调用在 Agent CLI 子进程里发生。Server 和 Daemon 只负责：
1. 准备 Prompt（Agent Instructions + Issue Context + Skill Files）
2. 准备环境变量（Agent 自定义 env）
3. 准备工作目录（注入 CLAUDE.md / Skills / 上下文文件）
4. 启动 CLI 子进程
5. 流式读取 stdout，分类转发消息

这保证了：
- **代码和密钥不出你的机器**：Agent 在你本地运行，可访问本地文件和环境
- **厂商中立**：不绑定任何一家模型提供商
- **安全边界清晰**：每个任务一个隔离工作目录，环境变量过滤阻止覆盖认证信息

---

## 核心功能模块

### 1. Agent 智能体管理

Agent 不是"AI 模型"，而是**带配置的工作者身份**：

- 基本信息：名字、头像（自动生成）、个人描述
- Provider 选择：底层使用哪个 CLI（Claude Code/Codex/...）
- Runtime 绑定：在哪台机器上跑
- Instructions：系统提示词（"你是一个资深前端工程师..."）
- Custom Env：注入到 CLI 进程的环境变量（API Key、Base URL 等）
- Custom Args：附加启动参数（`--model`、`--thinking` 等）
- MCP Config：Model Context Protocol 服务器列表（扩展工具能力）
- Skills：关联的可复用技能
- 并发控制：同时最多跑几个任务
- 状态：`idle`/`working`/`blocked`/`error`/`offline`

### 2. Runtime & Daemon

Daemon 是在用户机器上运行的后台进程：

| 功能 | 说明 |
|------|------|
| 自动探测 | 扫描 `$PATH` 发现已安装的 Agent CLI |
| 注册 Runtime | 向 Server 注册，一个 CLI = 一个 Runtime |
| 轮询认领 | 每 3 秒轮询 Server，有任务就认领 |
| 心跳保活 | 每 15 秒心跳，45 秒无心跳标记离线 |
| 隔离执行 | 每个任务独立工作目录 `~/multica_workspaces/{ws}/{task}/workdir/` |
| 流式上报 | 实时把 Agent 输出推回 Server |
| Session 恢复 | 同一对 (Agent, Issue) 复用上次的 session_id 和工作目录 |

CLI 命令：
```bash
multica setup           # 一键配置：连接、登录、启动 daemon
multica daemon start    # 后台启动 daemon
multica daemon stop     # 优雅关闭（等待进行中任务完成）
multica daemon status   # 查看状态和探测到的 Agent
multica daemon logs -f  # 实时跟随日志
```

### 3. Skill 技能系统

Skill 是**给 Agent 读的可复用说明文档**（不是代码，不是 Prompt 模板）：

```
skill/
  ├─ name: "karpathy-guidelines"
  ├─ description: "Behavioral guidelines to reduce LLM coding mistakes"
  ├─ content: "## Think Before Coding\n..."
  └─ files:
      ├─ examples/code-examples.py
      └─ references/patterns.md
```

**工作流程**：
1. 在 Settings → Skills 创建或从 URL 导入
2. 给 Agent 勾选要挂载的 Skill
3. Agent 认领任务时，Daemon 把 Skill 内容写到 Provider 原生位置：
   - Claude Code → `.claude/skills/{name}/SKILL.md`
   - Cursor → `.cursor/skills/{name}/SKILL.md`
   - Codex → `CODEX_HOME/skills/{name}/`
   - GitHub Copilot → `.github/skills/{name}/SKILL.md`
4. Agent CLI 自动发现并读取这些文件

> 💡 本教程的 [karpathy-llm-coding-guidelines](.) 就是一个典型的 Skill —— 挂载到 Agent 后，它就会自动遵守 Karpathy 的四条准则。

### 4. Issue 与任务执行

Issue 是核心工作单元，可以分配给人或 Agent：

**Issue 字段**：标题、描述、状态（backlog/todo/in_progress/in_review/done/blocked/cancelled）、优先级、Assignee（人或 Agent）、Parent（子任务）、Project、Labels、Dependencies、Acceptance Criteria。

**Agent 执行流程**：
1. Issue 分配给 Agent → 进入 `agent_task_queue`
2. Daemon 轮询认领 → 准备工作目录（注入 Skills、上下文、仓库）
3. 启动 CLI 子进程 → Agent 自主执行
4. 实时推送 `task:progress`/`task:message` 事件
5. 完成/失败 → 更新 Issue 状态、上报 token 用量、保存 session_id

**评论触发**：在 Issue 评论里 `@agent` 会自动生成新任务让 Agent 回复/处理。

### 5. Autopilot 自动驾驶

让 Agent 在没人触发时自动开工：

- **触发方式**：Cron 定时、Webhook、API/手动
- **执行模式**：
  - `create_issue`：创建新 Issue 再分配（默认）
  - `run_only`：直接执行不留 ticket
- **并发策略**：skip（去重）/ queue（排队）/ replace（中止上一次）
- **内置模板**：日报、Bug Triage、PR Review 提醒、依赖审计、安全扫描、周报

### 6. Squad 小队

把多个 Agent（和人类）组合成小队，由 Leader Agent 路由任务：

- 不用 `@小张或小李或小王`，直接 `@前端组`
- Leader 判断哪个成员最适合接手
- 团队扩容时路由方式不变
- 适合规模化：2 个工程师 + 一组 Agent = 20 人团队的推进速度

### 7. Chat 对话

不依附于 Issue 的轻量持久对话：
- 选一个 Agent 直接聊
- 每条消息触发 Agent 执行
- Session 复用保留上下文
- 和 Issue 评论的区别：私有（个人和 Agent）、不需要 @、用于探索/提问/一次性任务

### 8. Inbox 通知

个人通知中心，支持推送给人也推送给 Agent：
- Issue 被分配、被 @、订阅的 Issue 更新、任务完成/失败、邀请
- 自动订阅：creator、assignee、被 @ 的人
- WebSocket 实时推送
- 批量操作：全部已读、归档已完成

---

## 与 Karpathy 准则的关系

Karpathy 的四条准则（Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution）在 Multica 生态中有两层含义：

### 1. 作为 Skill 挂载

`andrej-karpathy-skills` 仓库本身就是一个标准的 Multica Skill：
- SKILL.md 格式符合 Multica Skill 规范
- 可以直接通过 `multica skill import --url` 导入
- 挂载到 Agent 后自动注入到工作目录
- Agent 执行任务时自动读取并遵守

### 2. 与 Multica 设计哲学的契合

| Karpathy 原则 | Multica 平台机制 |
|--------------|-----------------|
| **编码前先思考** | Agent 认领任务时自动获得完整上下文（Issue 描述、验收标准、历史评论、Skills），不需要猜测 |
| **简约至上** | Autopilot 的 `run_only` 模式不创建多余 Issue；Skill 是纯 Markdown 文档，不引入额外抽象层 |
| **精确编辑** | Daemon 为每个任务创建隔离工作目录；环境变量过滤防止越权；仓库白名单限制 checkout 范围 |
| **目标驱动** | Issue 的 Acceptance Criteria 字段明确定义成功标准；Session Resumption 让 Agent 能循环直到目标达成 |

### 3. Mention 副作用的安全设计

Multica 的 `[@agent](mention://agent/<id>)` 机制本身就体现了"先思考再行动"：
- `@agent` 和 `@squad` 会触发任务入队（有副作用）
- `@member` 只是人员链接（无副作用）
- `@issue` 是安全的交叉引用
- Skill 明确教导外部 Agent：不要为了感谢/确认而 @ Agent，这会触发新一轮运行可能造成循环

---

## 快速开始（5 步）

### 1. 安装 CLI

**macOS / Linux（Homebrew）**：
```bash
brew install multica-ai/tap/multica
```

**Windows（PowerShell）**：
```powershell
irm https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.ps1 | iex
```

### 2. 配置启动
```bash
multica setup    # 连接 Multica Cloud，登录，启动 daemon
```

Daemon 启动后会自动探测你 PATH 中的 Agent CLI。

### 3. 确认 Runtime 在线

在 Web 端 **Settings → Runtimes** 看到你的机器作为活跃 Runtime 出现。

### 4. 创建 Agent

**Settings → Agents → 新建 Agent**，选择 Runtime、Provider（Claude Code/Codex/...），起个名字。

### 5. 分配第一个任务

在看板创建 Issue 并分配给 Agent——它会自动接手、执行、实时汇报进度。

---

## 部署形态

| 形态 | 说明 |
|------|------|
| **Multica Cloud** | 官方托管服务，Agent 通过本地 Daemon 执行（代码不出你的机器） |
| **自托管（Self-Host）** | 完整后端部署在自己服务器，需要 Docker |
| **Web 客户端** | Next.js 应用，浏览器访问 |
| **桌面客户端** | Electron 应用，多标签、原生托盘、自动更新、Daemon 集成 |
| **移动端** | Expo/React Native iOS App |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 16 (App Router), React, Tailwind CSS, shadcn/Base UI |
| 状态管理 | TanStack Query（服务器状态）+ Zustand（客户端状态） |
| 后端 | Go 1.26+, Chi router, sqlc, gorilla/websocket |
| 数据库 | PostgreSQL 17 + pgvector（28 张表） |
| 桌面端 | Electron |
| 移动端 | Expo / React Native |
| Monorepo | pnpm workspaces + Turborepo |
| 实时通信 | WebSocket（60+ 事件类型） |

---

## 延伸阅读

- [07 - Multica CLI Skill 使用指南](07-multica-cli-skill.md)：如何让外部 Agent（Claude Code/Cursor/Codex）通过 multica CLI 安全操作平台
- [05 - 资源与参考](05-resources.md)：官方仓库链接
- Multica 官方文档：https://multica.ai （Settings → Skills 页面可直接导入 Karpathy 准则）
