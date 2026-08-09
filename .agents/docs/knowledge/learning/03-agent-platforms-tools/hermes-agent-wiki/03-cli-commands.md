---
id: "hermes-agent-wiki-03-cli-commands"
title: "03 Hermes Agent CLI 与斜杠命令详解"
source: "NousResearch/hermes-agent 本地源码仓库（website/docs/reference/cli-commands.md / reference/slash-commands.md / hermes_cli/commands.py）"
type: "Wiki Tutorial"
description: "Hermes Agent 主要 CLI 子命令、会话内斜杠命令，以及 COMMAND_REGISTRY 集中注册机制的详解"
status: "stable"
category: "learning"
tags: ["hermes", "cli", "slash-commands", "command-registry"]
date: "2026-08-10"
author: "hermes-agent-wiki knowledge-scenario"
summary: "覆盖 hermes 顶层子命令族、交互式/消息斜杠命令，并阐释 COMMAND_REGISTRY（hermes_cli/commands.py）集中定义、多端消费的机制"
last_verified: "2026-08-10"
wiki_version: "1.0"
---
# 03 Hermes Agent CLI 与斜杠命令详解

Hermes 有两套命令面：

1. **终端 CLI 子命令**（在 shell 里运行 `hermes <子命令>`）
2. **会话内斜杠命令**（进入对话后输入 `/xxx`）

两者都由一个**中央命令注册表**（COMMAND_REGISTRY）驱动，见 3.3 节。

## 3.1 顶层 CLI 子命令

入口形式：`hermes [全局选项] <command> [subcommand/options]`。

### 全局选项（常用）

| 选项 | 说明 |
|------|------|
| `--version`, `-V` | 显示版本并退出 |
| `--profile <name>`, `-p` | 选择 profile（多实例隔离） |
| `--resume <session>`, `-r` | 按 ID/标题恢复会话；`latest` 恢复最近会话 |
| `--continue [name]`, `-c` | 恢复最近会话 |
| `--tui` | 启动现代 TUI（等价 `HERMES_TUI=1`） |
| `--cli` | 强制经典 CLI |
| `--yolo` | 绕过危险命令审批提示 |

### 主要子命令族

下表为 `reference/cli-commands.md` 中实际存在的顶层命令（选取常用者，非穷尽）：

| 命令 | 用途 |
|------|------|
| `hermes chat` | 交互式或一次性聊天（`-q` 非交互、`-z` 纯脚本输出） |
| `hermes model` | 交互式选择提供商与模型（**完整提供商设置向导**） |
| `hermes tools` | 按平台配置启用工具（`--summary` 打印摘要并退出） |
| `hermes setup` | 完整设置向导（`--portal` 一键 Nous Portal） |
| `hermes config` | 显示/编辑/迁移配置（`set`/`get`/`show`/`edit`/`migrate`） |
| `hermes gateway` | 消息网关：`run`/`start`/`stop`/`restart`/`status`/`setup`/`install`/`uninstall` |
| `hermes cron` | 定时任务：`list`/`create`/`edit`/`pause`/`resume`/`run`/`remove`/`status`/`tick` |
| `hermes plugins` | 插件管理（通用插件 + 内存/上下文提供商插件） |
| `hermes skills` | 技能：`browse`/`search`/`install`/`inspect`/`list`/`check`/`update`/`audit`/`uninstall`/`publish` 等 |
| `hermes doctor` | 诊断配置与依赖问题（`--fix` 尝试自动修复） |
| `hermes update` | 更新到最新版本（`--check`/`--backup`） |
| `hermes uninstall` | 卸载 Hermes（`--full` 连配置数据一并删除） |
| `hermes mcp` | 管理 MCP 服务器配置 / 以 MCP 服务器模式运行 |
| `hermes memory` | 配置外部记忆提供商（honcho/mem0/supermemory 等，仅单实例） |
| `hermes curator` | 技能后台维护：`status`/`run`/`pause`/`pin`/`archive`/`restore` 等 |
| `hermes sessions` | 浏览/导出/清理/重命名会话 |
| `hermes insights` | token/成本/活动分析 |
| `hermes status` | 显示 agent/认证/平台状态 |
| `hermes auth` | 管理凭据（add/list/remove/reset/status/logout） |
| `hermes backup` / `import` | 备份 / 恢复 Hermes 主目录 |
| `hermes logs` | 查看/跟踪日志（agent/errors/gateway/gui/desktop） |
| `hermes send` | 向配置好的消息平台发一次性消息（脚本/CI 用） |
| `hermes secrets` | 外部密钥源（Bitwarden）管理 |
| `hermes kanban` | 多 profile 协作看板 |
| `hermes profile` | 多实例 profile 管理 |
| `hermes acp` | 以 ACP 服务器运行（编辑器集成，VS Code/Zed/JetBrains） |
| `hermes dashboard` / `serve` | Web 仪表盘 / 无头后端服务器 |
| `hermes desktop` | 构建并启动 Electron 桌面应用 |
| `hermes claw migrate` | 从 OpenClaw 迁移 |

### `hermes -z`：脚本化一次性模式

最纯粹的脚本入口：**单个 prompt 进、最终答案文本出**，stdout/stderr 无任何横幅/进度/`Session:` 噪音：

```bash
hermes -z "What's the capital of France?"
answer=$(hermes -z "summarize this" < /path/to/file.txt)
hermes -z "…" --usage-file /tmp/usage.json   # 机器可读用量报告
```

同一 agent、同一套工具与技能，只是剥掉所有交互/装饰层。若还需要工具输出进转录，改用 `hermes chat -q`。

## 3.2 会话内斜杠命令

### 交互式 CLI 斜杠命令（常用）

类型 `/` 打开自动补全，内建命令不区分大小写：

**Session（会话）类**
- `/new [name]`（别名 `/reset`）— 开始新会话
- `/clear` — 清屏并开始新会话
- `/save` — 保存当前对话
- `/retry`、`/undo` — 重试 / 撤销上一轮
- `/compress [here [N] | focus topic]` — 手动压缩上下文
- `/rollback` — 列出/恢复文件系统检查点
- `/resume [name]` — 恢复指定会话
- `/background <prompt>`（别名 `/bg`/`/btw`）— 后台会话并行跑
- `/title`、`/history`、`/stop`、`/branch`

**Configuration（配置）类**
- `/model [provider:model]` — 显示/切换模型（仅限已配置提供商；`--global` 持久化）
- `/personality [name]` — 设置人格
- `/skin` — 显示/切换皮肤主题
- `/yolo`、`/approvals` — 危险命令审批相关
- `/reasoning [level]`、`/voice`、`/wake`

**Tools & Skills 类**
- `/tools [list|disable|enable]` — 管理工具
- `/skills` — 搜索/安装/管理技能（`pending`/`approve`/`reject`/`diff` 审批子命令）
- `/learn <what>` — 从任意来源提炼可复用技能
- `/init [notes]` — 生成/更新 `AGENTS.md`
- `/cron` — 管理定时任务
- `/memory [pending|approve|reject|approval]` — 管理记忆写入
- `/plugins`、`/reload-mcp`、`/reload-skills`、`/reload`
- `/<skill-name>` — 动态调用任意已装技能

**Info（信息）类**
- `/help` — 显示帮助
- `/version`、`/status`、`/whoami`
- `/usage`、`/insights`、`/topup`
- `/update`、`/debug`、`/platforms`

**Exit（退出）类**：`/quit`（别名 `/exit`）

> 破坏性命令（`/clear`、`/new`、`/undo`、`/exit --delete` 等）会弹出三选确认模态框（Approve Once / Always Approve / Cancel），可追加 `now`、`--yes`、`-y` 跳过。

### 消息平台斜杠命令（网关）

在 Telegram/Discord/Slack/WhatsApp/Signal 等里，同一套命令大多通用，另有一些平台专用命令：`/start`（协议握手）、`/sethome`、`/stop`、`/restart`、`/approve`、`/deny`、`/topic`、`/platform`、`/commands` 等。管理员与普通用户通过 `user_allowed_commands` 做两级权限切分（普通用户至少保留 `/help`、`/whoami`）。

### 用户自定义快速命令（quick_commands）

可在 `~/.hermes/config.yaml` 把短斜杠命令映射到 shell 命令或另一条斜杠命令：

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  inbox:
    type: alias
    target: /gmail unread
```

然后直接输入 `/status`、`/inbox` 即可。

> 上例中的 `/gmail` 为**演示用的用户自定义命令**，并非 Hermes 内置命令——它需要你在 `quick_commands` 中自行定义对应的别名/执行命令后才能使用。

## 3.3 COMMAND_REGISTRY 概念

**COMMAND_REGISTRY** 是 Hermes 斜杠命令的**集中定义表**，位于源码 `hermes_cli/commands.py`。它是一个 `CommandDef` 对象列表，每个定义记录：

- `name` — 规范名（不含斜杠，如 `"background"`）
- `description` — 人类可读描述
- `category` — 分类：`"Session"` / `"Configuration"` / `"Tools & Skills"` / `"Info"` / `"Exit"`
- `aliases` — 别名元组（如 `("bg",)`）
- `args_hint` — 帮助中显示的参数占位符
- `cli_only` / `gateway_only` — 是否仅限某端
- `gateway_config_gate` — 配置门控

**关键设计：所有下游消费者都从这个注册表自动派生**，无需重复维护命令列表：

- **CLI** — `process_command()` 经 `resolve_command()` 解析别名、按规范名分发
- **网关** — `GATEWAY_KNOWN_COMMANDS` frozenset 用于钩子发射、`resolve_command()` 分发
- **网关帮助** — `gateway_help_lines()` 生成 `/help` 输出
- **Telegram** — `telegram_bot_commands()` 生成 BotCommand 菜单
- **Slack** — `slack_subcommand_map()` 生成 `/hermes` 子命令路由
- **自动补全** — `COMMANDS` 平面字典喂给 `SlashCommandCompleter`
- **CLI 帮助** — `COMMANDS_BY_CATEGORY` 字典喂给 `show_help()`

**新增一条斜杠命令**只需两步（源码 AGENTS.md 规范）：
1. 在 `hermes_cli/commands.py` 的 `COMMAND_REGISTRY` 加一条 `CommandDef`
2. 在 `cli.py` 的 `process_command()` 加对应处理器

若网关也需要，在 `gateway/run.py` 加对应分支。**新增别名**则只需在现有 `CommandDef` 的 `aliases` 元组里加一个名字——分发、帮助、Telegram 菜单、Slack 映射、自动补全会自动更新。

> **补充**：命令支持前缀匹配（如 `/h` → `/help`、`/mod` → `/model`），歧义时按注册表顺序取首个匹配；完整命令名与注册别名优先于前缀匹配。

## 3.4 小结

| 层面 | 入口 | 定义来源 |
|------|------|---------|
| 终端子命令 | `hermes <command>` | `hermes_cli/main.py`（各子命令模块） |
| CLI 斜杠命令 | 会话内 `/xxx` | `COMMAND_REGISTRY`（`hermes_cli/commands.py`） |
| 消息斜杠命令 | 网关内 `/xxx` | 同一 `COMMAND_REGISTRY` 派生 |
| 技能动态命令 | `/<skill-name>` | 扫描 `~/.hermes/skills/` 动态注入 |

完整命令清单以官方 `reference/cli-commands.md` 与 `reference/slash-commands.md` 为准（Hermes 生态演进快，命令可能增减）。
