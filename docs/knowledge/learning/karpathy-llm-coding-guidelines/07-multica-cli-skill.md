---
title: "Multica CLI Skill：让外部 Agent 安全操作 Multica"
category: learning
tags: [karpathy, llm, coding, agent, multica, cli, skill, claude-code, cursor, codex, safety, external-agent]
date: "2026-07-02"
status: stable
author: "multica-ai"
summary: "multica-cli 是一个可移植 Skill，教任意本地编码 Agent（Claude Code、Codex、Cursor 等）通过已认证的 multica CLI 安全操作 Multica 平台：读取 Issue、回复评论、管理元数据、处理 mention 副作用。本文档包含安装方法、命令参考、安全规则、读写工作流和具体示例。"
source: "https://github.com/multica-ai/multica-cli"
---

# Multica CLI Skill：让外部 Agent 安全操作 Multica

`multica-cli` 是一个可移植的 Agent Skill，教任意本地编码 Agent（Claude Code、Codex、Cursor 等）通过已认证的 `multica` CLI 安全操作 Multica 平台。

> **核心定位**：本 Skill 教的是「如何安全地」操作 Multica。它本身不授予任何权限——权限只来自用户本机已登录的 CLI、所选 profile、当前 workspace，以及对每条命令的显式授权。

---

## 这个 Skill 不会做什么

在了解它能做什么之前，先明确安全边界：

- ❌ **不会绕过权限**：绝不绕过 workspace 权限，绝不调用私有 HTTP API
- ❌ **不会保存密钥**：不暴露或存储 tokens、cookies、API keys
- ❌ **不会伪造认证**：CLI 未登录时直接停止，让用户先认证
- ❌ **不会擅自写操作**：除非用户明确授权，否则写操作前先确认

---

## 覆盖范围

| 能力 | 说明 |
|------|------|
| ✅ 状态检查 | CLI 登录状态、profile、workspace 状态 |
| ✅ 读取 | Issue、Comment、Metadata、Project、Agent、Squad、Runtime、Repo、Skill、Autopilot、Attachment |
| ✅ 安全写评论 | 用 `--content-file` 安全地写 Issue 评论（避免 shell 转义问题） |
| ✅ 创建/更新 | 创建/更新 Issue 和高价值 Metadata |
| ✅ 处理副作用 | Mention、状态变更、分配、Rerun、子 Issue |
| ✅ PR 关联 | 把 Pull Request 关联回 Multica Issue |

---

## 安装

Skill 位于仓库的 `skills/multica-cli/` 目录，支持多种工具。

### Claude Code（插件市场，推荐）

```
/plugin marketplace add multica-ai/multica-cli
/plugin install multica-cli@multica-cli
```

### Codex（Skill 安装器）

```bash
install-skill-from-github.py --repo multica-ai/multica-cli --path skills/multica-cli
```

安装后重启 Codex。

### Cursor

**方式一：个人 Skill（跨项目）**

```bash
mkdir -p ~/.cursor/skills/multica-cli
cp -R skills/multica-cli/* ~/.cursor/skills/multica-cli/
```

**方式二：项目规则（单项目）**

把 [`.cursor/rules/multica-cli.mdc`](https://github.com/multica-ai/multica-cli/blob/main/.cursor/rules/multica-cli.mdc) 复制到项目的 `.cursor/rules/` 目录。详见 [CURSOR.md](https://github.com/multica-ai/multica-cli/blob/main/CURSOR.md)。

### 其他 Agent

把 [`skills/multica-cli/SKILL.md`](https://github.com/multica-ai/multica-cli/blob/main/skills/multica-cli/SKILL.md) 复制到你的工具加载 Skill/指令的位置即可。

---

## 前置条件

1. 本机已安装 `multica` CLI
2. 用户已通过 `multica login`（或 `multica setup`）完成认证
3. 已选择目标 workspace / profile，或通过 `--workspace-id`、`--profile` 显式传入

---

## 安全启动流程

在执行任何操作之前，Agent 必须先验证状态：

### 第一步：检查 CLI 和账户状态

```bash
multica version
multica auth status
multica config show
```

如果 `multica auth status` 报告没有活跃会话，**必须停止**，让用户先认证：

```bash
multica login        # 交互式认证 + workspace 设置
multica setup        # 替代方案：配置 CLI、认证、启动 daemon
```

### 第二步：确认 Workspace 和 Profile

```bash
multica workspace list --output json                 # 查看有哪些 workspace
multica workspace switch <workspace-id>              # 切换默认 workspace
multica --profile <profile> --workspace-id <workspace-id> issue list --output json
```

### 第三步：优先使用 JSON 输出

只要命令支持 `--output json`，就用它。解析 JSON 比抓取表格输出可靠。

### 安全红线

- **绝不**暴露或存储 tokens、cookies、API keys、CLI 配置密钥
- **绝不**通过直接调用私有 HTTP API 绕过 workspace 权限
- **先读后写**：先用读命令了解上下文，再决定是否需要写
- **写操作先确认**：如果用户没有明确要求写操作，执行前必须确认

---

## 命令参考

### Issue 读取

```bash
# 获取单个 Issue
multica issue get <id> --output json

# 列出 Issue（支持过滤）
multica issue list [--status <s>] [--assignee <name> | --assignee-id <uuid>] \
                   [--project <id>] [--priority <p>] [--limit N] \
                   [--metadata key=value] --output json

# 子 Issue
multica issue children <id> --output json

# 关联的 PR
multica issue pull-requests <id> --output json

# Metadata
multica issue metadata list <id> --output json
```

### 评论读取

```bash
# 最近 N 个活跃讨论串
multica issue comment list <id> --recent N --output json

# 单个讨论串（根评论 + 回复）
multica issue comment list <id> --thread <comment-id> [--tail N] --output json

# 仅根评论（用于 Triage）
multica issue comment list <id> --roots-only [--summary] --output json

# 分页参数
# --since <RFC3339>, --before/--before-id <cursor>
```

### 创建/更新 Issue

```bash
# 创建 Issue
multica issue create --title "..." \
                     [--description-file <path>] \
                     [--priority <p>] [--status <s>] \
                     [--assignee <name> | --assignee-id <uuid>] \
                     [--parent <id>] [--stage N] [--project <id>] \
                     [--due-date YYYY-MM-DD] [--attachment <path>] \
                     --output json

# 更新 Issue
multica issue update <id> \
                     [--title "..."] [--description-file <path>] \
                     [--status <s>] [--priority <p>] \
                     [--assignee-id <uuid>] \
                     [--parent <id> | --parent ""] [--stage N] \
                     [--due-date YYYY-MM-DD]
```

### 状态和分配

状态值：`backlog` | `todo` | `in_progress` | `in_review` | `done` | `blocked` | `cancelled`

```bash
multica issue status <id> <status>
multica issue assign <id> --to <name> | --to-id <uuid> | --unassign
```

> ⚠️ **注意参数不一致**：`issue assign` 使用 `--to` / `--to-id`，而 `issue create` / `issue update` 使用 `--assignee` / `--assignee-id`。

### 写评论（安全方式）

```bash
# 评论正文必须通过文件传递，不要用 --content（内联内容会被 shell 转义破坏）
multica issue comment add <id> [--parent <comment-id>] --content-file <path> [--attachment <path>]
```

### Metadata 操作

```bash
multica issue metadata set <id> --key <k> --value <v> [--type string|number|bool]
multica issue metadata delete <id> --key <k>
```

### 其他资源（用 --help 探索）

```bash
multica project --help
multica agent --help
multica squad --help
multica runtime --help
multica repo --help
multica skill --help
multica autopilot --help
multica attachment --help
```

---

## 读工作流

**先读后写**。在决定是否需要写操作之前，先收集完整上下文：

```bash
multica issue get <issue-id-or-key> --output json
multica issue comment list <issue-id-or-key> --recent 10 --output json
multica issue metadata list <issue-id-or-key> --output json
multica issue pull-requests <issue-id-or-key> --output json
```

### 大评论历史的高效读取

```bash
# 只看某个讨论串最近 30 条
multica issue comment list <issue-id> --thread <comment-id> --tail 30 --output json

# 只看最近活跃的 10 个讨论
multica issue comment list <issue-id> --recent 10 --output json
```

---

## 写工作流

写操作有副作用。如果用户没有明确要求写，**必须先问**。

需要确认的写操作包括：创建评论、创建 Issue、状态变更、分配、Rerun、Agent Mention、Squad Mention、Webhook/Autopilot 变更、Repo Checkout。

### 评论写入（必须用文件）

对于 Agent 写的评论，**必须**先把正文写到 UTF-8 文件，再用 `--content-file` 传递：

```bash
# 1. 先创建 reply.md（真实换行，不要用 \n 转义）
# 2. 然后：
multica issue comment add <issue-id> --parent <comment-id> --content-file ./reply.md
# 3. 清理临时文件
rm ./reply.md
```

**为什么不能用 `--content`？** Shell 会重写反引号、`$()` 表达式、变量、引号和换行符，CLI 收到的内容会被破坏。

回复讨论串时保持和被回复评论相同的 `--parent` 值。

### Issue 和描述

长描述也用文件：

```bash
multica issue create --title "..." --description-file ./description.md
multica issue update <issue-id> --description-file ./description.md
```

### Metadata 写入原则

Metadata 是**持久化的 Issue 状态**，不是日志。只写未来运行会重新读取的高价值信息：

| 适合写入 Metadata | 不适合写入 |
|------------------|-----------|
| `pr_url`, `pr_number` | "正在调查中" |
| `pipeline_status` | "第 3 次尝试" |
| `deploy_url` | 临时笔记 |
| `external_issue_url` | 日志信息 |
| `waiting_on`, `blocked_reason` | |
| `decision`（最终决策） | |

```bash
multica issue metadata set <issue-id> --key pr_url --value <url>
multica issue metadata delete <issue-id> --key stale_key
```

---

## Mention 副作用处理

Mention 链接是**动作**，不是装饰：

```markdown
[@Name](mention://agent/<agent-id>)   # 入队该 Agent（触发运行）
[@Name](mention://squad/<squad-id>)   # 入队 Squad Leader
[@Name](mention://member/<user-id>)   # 人员链接（无副作用）
[MUL-123](mention://issue/<issue-id>) # Issue 链接（安全交叉引用）
[@all](mention://all/all)             # 广播（不触发具体 Agent 运行）
```

### Mention 安全规则

1. **只有 `agent` 和 `squad` mention 会触发任务入队**，`member` 和 `issue` mention 是安全的
2. **构建 mention 前先查真实 UUID**（用 JSON 输出）：
   ```bash
   multica agent list --output json
   multica squad list --output json
   multica workspace member list --output json
   ```
3. **不要为了感谢/确认/收尾而 @ Agent**——在回复中再次 @ Agent 会触发新一轮运行，可能造成循环

---

## 状态和分配副作用

状态变更不是表面操作，它们会入队或停止工作：

- `backlog`：搁置分配给 Agent 的 Issue
- 从 `backlog` 移到 `todo` 或其他活跃状态：可能入队 assignee
- `done` 和 `cancelled` 是终止状态
- `in_review`：PR 或人工审核中，但仍然是写操作

### 有序子 Issue 模式

创建分步骤的子 Issue 时，用 stages 和 `backlog` 控制后续步骤：

```bash
multica issue create --title "Research" --parent <id> --assignee <agent> --stage 1 --status todo
multica issue create --title "Build" --parent <id> --assignee <agent> --stage 2 --status backlog
multica issue children <id> --output json
```

---

## Pull Request 关联

为 Multica Issue 做代码变更时，在 PR 标题、正文或分支名中包含可路由的 Issue Key：

```text
MUL-123: fix login redirect
```

只有合并 PR 应该关闭 Issue 时才用 close 意图：

```text
Closes MUL-123
Fixes MUL-123
Resolves MUL-123
```

从 Multica 读取关联 PR 状态，不要从 GitHub 搜索或 Metadata 猜测：

```bash
multica issue pull-requests <issue-id> --output json
```

---

## 外部 Agent 边界

外部 Agent（通过 CLI 操作的 Agent）不会自动收到 Multica 运行时上下文。如果用户要求对特定 Issue 或评论操作，必须确认或推导：

- Issue ID 或 Issue Key
- 触发评论 ID 和父讨论串（如果是回复）
- 目标 workspace/profile（如果配置了多个）
- 是否允许写操作
- 是否允许 mention、状态变更、rerun、分配

**如果以上任何一项缺失且操作会写状态，必须先问再继续。**

对于只读调查，可以先用 JSON 输出收集上下文，然后报告还需要什么信息。

---

## 使用示例

### 示例 1：读取 Issue 并总结阻塞原因

> **用户**：读一下 MUL-123，告诉我什么东西在阻塞它。

```bash
multica issue get MUL-123 --output json
multica issue comment list MUL-123 --recent 10 --output json
multica issue metadata list MUL-123 --output json
```

然后基于读取到的内容总结阻塞因素。

### 示例 2：起草回复供审核（不发布）

> **用户**：给 MUL-123 最新评论起草一个回复，但先别发。

```bash
multica issue comment list MUL-123 --thread <comment-id> --tail 30 --output json
# 写 reply.md，展示给用户
# 用户确认后：
multica issue comment add MUL-123 --parent <comment-id> --content-file ./reply.md
rm ./reply.md
```

### 示例 3：Triage 新 Issue

> **用户**：创建一个 bug issue，标题是"Login redirect loops"，分配给我。

```bash
multica issue create --title "Login redirect loops" --description-file ./desc.md
# 先查 assignee 的 ID（注意 assign 用 --to-id，不是 --assignee-id）：
multica workspace member list --output json
multica issue assign <issue-id> --to-id <user-id>
```

### 示例 4：检查 PR 合并状态

> **用户**：MUL-123 的 PR 合并了吗？

```bash
multica issue pull-requests MUL-123 --output json
```

### 示例 5：需要先确认的副作用操作

这些操作**不是**表面装饰——执行前必须和用户确认：

- 发布 @ 了 Agent 或 Squad 的评论（会入队运行）
- 变更状态（`todo`/`backlog`/`done` 会入队或停止工作）
- 分配、Rerun、创建子 Issue

---

## 安全检查清单

Agent 在操作前应自检：

- [ ] 已运行 `multica auth status` 确认登录状态
- [ ] 已确认当前 workspace（或显式传入 `--workspace-id`）
- [ ] 所有读取优先使用 `--output json`
- [ ] 写操作前已获得用户明确授权
- [ ] 评论正文通过 `--content-file` 传递，不是 `--content`
- [ ] Mention 前已查询真实 UUID
- [ ] 没有为了感谢而 @ Agent
- [ ] 理解状态变更会触发任务入队/停止
- [ ] PR 关联使用 `multica issue pull-requests` 读取，不是猜测
- [ ] 没有暴露或存储任何密钥/token

---

## 与 Karpathy 准则的对应

`multica-cli` Skill 的设计本身就是 Karpathy 四条准则的典范应用：

| Karpathy 原则 | multica-cli 中的体现 |
|--------------|---------------------|
| **编码前先思考** | 启动流程先验证状态、确认 workspace、不隐藏歧义；缺失上下文先问 |
| **简约至上** | 命令参考只列最常用的 flag，长尾命令用 `--help` 探索；不做多余抽象 |
| **精确编辑** | 写操作有明确边界；不擅自修改无关内容；评论用文件传递避免 shell 破坏 |
| **目标驱动** | 读工作流→收集上下文→决定是否写；明确哪些操作是副作用需要确认 |

---

## 延伸阅读

- [06 - Multica 平台介绍](06-multica-platform.md)：Multica 平台架构、核心概念、功能模块
- [03 - 快速上手指南](03-quickstart.md)：Karpathy 准则的安装和使用
- multica-cli 仓库：https://github.com/multica-ai/multica-cli
- Multica 主仓库：https://github.com/multica-ai/multica
