---
id: "hermes-agent-wiki-09-extensions-cron-delegation"
title: "09 扩展能力：MCP、定时任务与委派"
source: "NousResearch/hermes-agent 本地源码仓库（website/docs/user-guide/features/mcp.md、cron.md、delegation.md、guides/automate-with-cron.md；源码 tools/delegate_tool.py、tools/mcp_tool.py、mcp_serve.py、cron/）"
type: "Wiki Tutorial"
description: "Hermes Agent 扩展能力详解：MCP 集成、cron 定时调度、委派与并行（delegate_task 与 subagent 生命周期）、角色（roles）"
status: "stable"
category: "learning"
tags: ["hermes", "mcp", "cron", "delegation", "extension"]
date: "2026-08-10"
author: "hermes-agent-wiki knowledge-scenario"
summary: "MCP 让 Hermes 连接外部工具服务器；cron 提供自然语言定时任务；delegate_task 派生隔离子代理并行工作；角色（leaf/orchestrator）控制委派深度"
last_verified: "2026-08-10"
wiki_version: "1.0"
---
# 09 扩展能力：MCP、定时任务与委派

## 9.1 MCP 集成：连接外部工具

**MCP**（Model Context Protocol，模型上下文协议）是连接 AI 应用与外部工具服务器的开放协议。Hermes **内置 MCP 客户端**（源码 `tools/mcp_tool.py`），可连接 stdio 本地服务器与远程 HTTP 服务器，从而使用 GitHub、数据库、文件系统、浏览器栈等**位于 Hermes 之外**的工具。

在 `~/.hermes/config.yaml` 的 `mcp_servers` 下声明服务器：

```yaml
mcp_servers:
  filesystem:                       # stdio 服务器（本地子进程，stdin/stdout 通信）
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
  remote_api:                       # HTTP 远程服务器
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

MCP 工具以 `mcp_<server>_<tool>` 前缀注册（如 `mcp_filesystem_read_file`），避免与内置工具冲突。可用 `/reload-mcp` 重载配置。

**MCP catalog（目录）**：Hermes 内置经 Nous 审核的 MCP 服务器目录（源码存放于 `optional-mcps/`），默认禁用、按需安装：

```bash
hermes mcp                # 交互式选择（默认）
hermes mcp catalog        # 纯文本列出目录条目
hermes mcp install n8n    # 按名称安装目录条目
hermes mcp configure <name>   # 重新选择工具子集
```

**Hermes 也可作为 MCP 服务器**：`hermes mcp serve` 启动 stdio MCP 服务器，让 Claude Code、Cursor 等客户端通过 Hermes 收发各平台消息（`messages_send`、`messages_read`、`events_wait` 等 10 个工具，见 `mcp_serve.py`）。

## 9.2 cron 定时调度：自然语言自动化

**Cron**（源自 Unix 的定时任务机制，名字取自希腊语 chronos"时间"）让 Hermes 用自然语言或 cron 表达式调度任务自动运行。所有管理通过**单一 `cronjob` 工具**以动作式操作完成。

**创建任务**：

```bash
/cron add 30m "Remind me to check the build"              # 聊天内
hermes cron create "every 2h" "Check server status"        # CLI
cronjob(action="create", prompt="...", schedule="0 9 * * *")  # 工具调用
```

**调度格式**：相对延迟（`30m`、`2h`、`1d`）、间隔（`every 30m`、`every 2h`）、cron 表达式（`0 9 * * *` 每日 9 点）、ISO 时间戳。

**生命周期动作**：`/cron list|pause|resume|run|remove <job_id>`（CLI 对应 `hermes cron …`）。任务可附带 0/1/多个**技能（skill）**，并支持 `no_agent` 纯脚本模式（无需 LLM）。

**执行机制**：由 **gateway 守护进程**负责，每 60 秒 tick 一次调度器，为每个到期任务启动全新 `AIAgent` 会话运行，然后把结果投递到目标（`deliver:`，如 `telegram`、`local`、`origin`）。任务存于 `~/.hermes/cron/jobs.json`，运行输出存于 `~/.hermes/cron/output/{job_id}/`。cron 会话内**禁止递归创建 cron**（防失控循环）。

> 定时任务在多用户/长周期场景与[01 核心特性](01-core-features.md)所述消息网关配合使用；详细指南见[集成 Wiki 快速接入](../hermes-agent-integration/06-usage-examples.md)。

## 9.3 委派与并行：delegate_task

**委派（delegation）**通过 `delegate_task` 工具（源码 `tools/delegate_tool.py`）派生**隔离上下文**的子 AIAgent 实例，实现并行工作流。

```python
# 单个任务
delegate_task(goal="Debug why tests fail", context="Error: assertion in test_foo.py line 42")

# 并行批量（默认最多 3 个并发子代理）
delegate_task(tasks=[
    {"goal": "Research topic A", "context": "Focus on recent primary sources"},
    {"goal": "Fix the build",   "context": "Project root: /home/user/project"},
])
```

**subagent 生命周期关键点**：
- 子代理以**全新会话**开始，对父会话一无所知——父必须把一切需要的信息放进 `goal`/`context`
- 每个子代理有独立**终端会话**，继承父的已启用工具集（模型不能自行扩大）
- 仅最终摘要进入父上下文（token 高效）
- 某些工具对子代理**屏蔽**：`delegate_task`（叶子）、`clarify`（无法与用户交互）、`memory`（不写共享记忆）、`send_message`、`cronjob`
- 后台委派自动运行，父可继续对话，结果以新消息回贴

**配置**（`~/.hermes/config.yaml`）：

```yaml
delegation:
  max_iterations: 50             # 每个子代理的最大轮数（默认 50）
  max_concurrent_children: 3     # 每批并行子代理数
  max_spawn_depth: 1             # 委派树深度（1 = 扁平，默认）
  model: "google/gemini-3-flash-preview"   # 子代理可用更便宜/更快的模型
```

## 9.4 角色（roles）

委派的**角色（role）**控制子代理能否继续向下委派，默认委派是**扁平**的（父派生子，子不能再派生）：

- **`leaf`（叶子，默认）**：子代理不能再委派，防止递归失控。
- **`orchestrator`（编排者）**：子代理保留 `delegate_task` 工具，可派生自己的 worker。由 `delegation.max_spawn_depth` 门控（默认 `1` = 扁平，`role="orchestrator"` 在默认下无效；提到 `2` 允许编排者派生叶子孙代，`3+` 更深）。

```python
delegate_task(
    goal="Survey three code review approaches and recommend one",
    role="orchestrator",    # 允许该子代理派生自己的 worker
    context="...",
)
```

`delegation.orchestrator_enabled: false` 为全局总开关，强制所有子代理为 `leaf`。**成本警告**：`max_spawn_depth: 3` 且 `max_concurrent_children: 3` 时树可达 27 个并发叶子代理，需谨慎提升。

## 9.5 扩展能力对比

| 机制 | 用途 | 生命周期 |
|------|------|---------|
| MCP 客户端 | 连接外部工具服务器 | 随 Hermes 启动，工具注册到工具注册表 |
| cron | 定时/周期自动化任务 | 由 gateway 调度，全新会话运行，结果投递 |
| delegate_task | 并行子代理工作流 | 后台运行，结果回贴父会话 |
| execute_code | 机械式脚本执行（无推理） | 同步，仅返回 stdout |

> 术语"技能（skill）""工具集（toolset）"见本 Wiki [11 术语表](11-glossary-faq-resources.md)。
