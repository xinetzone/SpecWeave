---
id: "karpathy-llm-coding-guidelines-multica-cli-skill"
title: "Multica CLI Skill：让外部 Agent 安全操作 Multica"
category: learning
tags: [karpathy, llm, coding, agent, multica, cli, skill, claude-code, cursor, codex, safety, external-agent]
date: "2026-07-02"
status: stable
author: "multica-ai"
summary: "multica-cli 是一个可移植 Skill，教任意本地编码 Agent（Claude Code、Codex、Cursor 等）通过已认证的 multica CLI 安全操作 Multica 平台。本文档按「背景→核心安全原则→命令正反例→快速上手→工作流实战→生态设计理念」六层认知阶梯组织，帮助读者从理解为什么需要到掌握最佳实践。"
source: "https://github.com/multica-ai/multica-cli"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/07-multica-cli-skill.toml"
maturity: "L2-validated"
structure: "tutorial-cognitive-ladder"
---
# Multica CLI Skill：让外部 Agent 安全操作 Multica

> 本文档遵循 [教程认知阶梯模式](../../../../retrospective/patterns/methodology-patterns/document-architecture/tutorial-cognitive-ladder.md)，按六层递进结构组织。你可以在任何一层停下来使用，也可以一直深入到设计理念层。

| 层级 | 章节 | 你将获得 |
|------|------|---------|
| L1 背景 | [一、为什么需要这个 Skill](#一为什么需要-这个-skill) | 理解问题背景和设计动机 |
| L2 核心 | [二、核心安全原则](#二核心安全原则) | 掌握安全边界、能力范围、红线规则 |
| L3 示例 | [三、命令参考与正反案例](#三命令参考与正反案例) | 每个操作都有❌错误和✅正确做法 |
| L4 上手 | [四、快速上手](#四快速上手) | 安装→验证→第一个读操作 |
| L5 落地 | [五、工作流实战](#五工作流实战) | 读写工作流、PR关联、子Issue模式 |
| L6 生态 | [六、设计理念与生态上下文](#六设计理念与生态上下文) | 为什么这样设计、与Karpathy准则关系、违反代价 |

---

## 一、为什么需要这个 Skill

`multica-cli` 是一个可移植的 Agent Skill，教任意本地编码 Agent（Claude Code、Codex、Cursor 等）通过已认证的 `multica` CLI 安全操作 Multica 平台。

### 直接用 CLI 不行吗？

如果你（人类）直接在终端用 `multica` 命令，完全不需要这个 Skill。但当 AI Agent 替你操作时，会出现三类人类不会犯的错误：

| 问题 | 人类不会犯 | Agent 容易犯 |
|------|-----------|-------------|
| **Shell 转义破坏** | 人会自然处理引号和换行 | Agent 用 `--content "多行文本"` 时，反引号、`$()`、换行符会被shell转义破坏 |
| **无确认副作用** | 人知道@人会通知对方 | Agent 在感谢回复中随意 `@Agent`，触发无限任务循环 |
| **上下文缺失硬猜** | 人会先问清楚再操作 | Agent 猜测 issue ID、assignee UUID，写入错误数据 |

**这个 Skill 解决的核心问题**：给 Agent 一套"安全操作手册"，让它在操作 Multica 时像一个谨慎的团队成员——先确认上下文、不越权、不随意触发副作用、出错了停下来问。

> **核心定位**：本 Skill 教的是「如何安全地」操作 Multica。它本身不授予任何权限——权限只来自用户本机已登录的 CLI、所选 profile、当前 workspace，以及对每条命令的显式授权。

---

## 二、核心安全原则

### 2.1 安全边界：这个 Skill 不会做什么

在了解它能做什么之前，先明确四条不可逾越的红线：

- ❌ **不会绕过权限**：绝不绕过 workspace 权限，绝不调用私有 HTTP API
- ❌ **不会保存密钥**：不暴露或存储 tokens、cookies、API keys
- ❌ **不会伪造认证**：CLI 未登录时直接停止，让用户先认证
- ❌ **不会擅自写操作**：除非用户明确授权，否则写操作前先确认

### 2.2 能力覆盖范围

| 能力 | 说明 | 副作用风险 |
|------|------|-----------|
| ✅ 状态检查 | CLI 登录状态、profile、workspace 状态 | 无（只读） |
| ✅ 读取 | Issue、Comment、Metadata、Project、Agent、Squad、Runtime等 | 无（只读） |
| ✅ 安全写评论 | 用 `--content-file` 安全地写 Issue 评论 | ⚠️ 中（可能mention触发） |
| ✅ 创建/更新 | 创建/更新 Issue 和高价值 Metadata | ⚠️ 中高 |
| ✅ 处理副作用 | Mention、状态变更、分配、Rerun、子 Issue | 🔴 高（可能触发任务入队） |
| ✅ PR 关联 | 把 Pull Request 关联回 Multica Issue | ⚠️ 中 |

### 2.3 四条安全红线

在任何操作中都必须遵守：

1. **绝不**暴露或存储 tokens、cookies、API keys、CLI 配置密钥
2. **绝不**通过直接调用私有 HTTP API 绕过 workspace 权限
3. **先读后写**：先用读命令了解上下文，再决定是否需要写
4. **写操作先确认**：如果用户没有明确要求写操作，执行前必须确认

### 2.4 Mention 不是装饰，是动作

Mention 链接在 Multica 中是**触发器**，不是文本装饰：

```markdown
[@Name](mention://agent/<agent-id>)   # 🔴 入队该 Agent（触发运行！）
[@Name](mention://squad/<squad-id>)   # 🔴 入队 Squad Leader（触发运行！）
[@Name](mention://member/<user-id>)   # ✅ 人员链接（无副作用）
[MUL-123](mention://issue/<issue-id>) # ✅ Issue 链接（安全交叉引用）
[@all](mention://all/all)             # ✅ 广播（不触发具体 Agent 运行）
```

**Mention 安全三规则**：
1. 只有 `agent` 和 `squad` mention 会触发任务入队
2. 构建 mention 前**必须**先查真实 UUID（用 `--output json`）
3. **不要为了感谢/确认/收尾而 @ Agent**——回复中再次 @ Agent 会触发新一轮运行，可能造成无限循环

### 2.5 状态变更会入队或停止工作

状态转换不是表面标签变更，它们有实际副作用：

| 状态 | 副作用 |
|------|--------|
| `backlog` | 搁置已分配给 Agent 的 Issue |
| `backlog` → `todo` | 可能入队 assignee 开始工作 |
| `done` / `cancelled` | 终止状态，Agent 停止工作 |
| `in_review` | PR 或人工审核中，仍是写操作 |

### 2.6 外部 Agent 的信息边界

外部 Agent 不会自动收到 Multica 运行时上下文。如果以下信息缺失且操作会写状态，**必须先问再继续**：

- Issue ID 或 Issue Key
- 触发评论 ID 和父讨论串（如果是回复）
- 目标 workspace/profile（如果配置了多个）
- 是否允许写操作
- 是否允许 mention、状态变更、rerun、分配

### 2.7 安全检查清单

每次操作前自检：

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

## 三、命令参考与正反案例

> 💡 **本章组织方式**：每个操作先列命令，紧接着给出 ❌ 常见错误做法和 ✅ 正确做法。**先看反例再看正例**，避免踩坑。

### 3.1 前置状态检查

```bash
multica version
multica auth status
multica config show
```

❌ **错误做法**：直接开始操作，不验证登录状态
```bash
# 还没确认是否登录就直接读 issue
multica issue get MUL-123 --output json
# → 如果没登录，可能返回误导性错误或提示认证
```

✅ **正确做法**：先验证，再操作
```bash
multica auth status
# 如果报告没有活跃会话，先让用户登录：
multica login
# 然后确认 workspace：
multica workspace list --output json
```

### 3.2 Issue 读取

```bash
multica issue get <id> --output json
multica issue list [--status <s>] [--assignee <name>] [--project <id>] [--limit N] --output json
multica issue children <id> --output json
multica issue pull-requests <id> --output json
multica issue metadata list <id> --output json
```

❌ **错误做法**：解析表格输出，或猜测字段名
```bash
multica issue list
# → 返回人类可读的表格，Agent 解析时容易出错
```

✅ **正确做法**：优先 JSON 输出
```bash
multica issue list --status todo --assignee me --limit 20 --output json
# → 结构化 JSON，可靠解析
```

### 3.3 评论读取

```bash
multica issue comment list <id> --recent N --output json
multica issue comment list <id> --thread <comment-id> [--tail N] --output json
multica issue comment list <id> --roots-only [--summary] --output json
```

❌ **错误做法**：一次性拉取全部评论（大 Issue 可能有上百条）
```bash
multica issue comment list MUL-123 --output json
# → 可能返回大量历史评论，浪费 token
```

✅ **正确做法**：按需读取，用分页参数
```bash
# Triage 新 Issue：只看根评论
multica issue comment list MUL-123 --roots-only --summary --output json
# 回复特定讨论：只看该讨论串最近30条
multica issue comment list MUL-123 --thread <comment-id> --tail 30 --output json
# 快速了解动态：只看最近10个活跃讨论
multica issue comment list MUL-123 --recent 10 --output json
```

### 3.4 写评论（最重要的安全规则）

```bash
multica issue comment add <id> [--parent <comment-id>] --content-file <path> [--attachment <path>]
```

❌ **错误做法**：用 `--content` 内联传递正文
```bash
multica issue comment add MUL-123 --content "已修复，请看 `$PR_URL`，结果：$(echo $?)"
# → Shell 会展开反引号、$()、$变量、破坏换行符
# → 发布的评论内容被严重篡改
```

✅ **正确做法**：正文写入 UTF-8 文件，用 `--content-file` 传递
```bash
# 1. 先创建 reply.md（真实换行，不要用 \n 转义）
# 2. 然后发布：
multica issue comment add MUL-123 --parent <comment-id> --content-file ./reply.md
# 3. 清理临时文件
rm ./reply.md
```

> **为什么必须用文件？** Shell 会重写反引号、`$()` 表达式、变量、引号和换行符，CLI 收到的内容会被破坏。这不是 Multica 的限制，是命令行界面的通用问题。

### 3.5 创建/更新 Issue

```bash
multica issue create --title "..." [--description-file <path>] [--priority <p>] [--status <s>] \
                     [--assignee <name>] [--parent <id>] [--stage N] [--project <id>] \
                     [--due-date YYYY-MM-DD] --output json
multica issue update <id> [--title "..."] [--description-file <path>] [--status <s>] [--priority <p>]
```

❌ **错误做法**：分配时直接用名字（不同命令参数名不一致！）
```bash
multica issue assign MUL-123 --assignee-id <uuid>
# → 错误！issue assign 用 --to-id，不是 --assignee-id
```

✅ **正确做法**：注意参数名不一致，先查 ID 再操作
```bash
# 注意：issue create/update 用 --assignee/--assignee-id
#       issue assign 用 --to/--to-id
multica workspace member list --output json  # 先查真实 user ID
multica issue assign <issue-id> --to-id <user-id>
```

### 3.6 状态变更

```bash
multica issue status <id> <status>
```

状态值：`backlog` | `todo` | `in_progress` | `in_review` | `done` | `blocked` | `cancelled`

❌ **错误做法**：把状态当标签随意切换
```bash
multica issue status MUL-123 done
# → 直接终止 Agent 工作，如果还有未完成的子任务会导致数据不一致
```

✅ **正确做法**：理解副作用，确认后再执行
```bash
# 先检查是否有关联 PR 未合并
multica issue pull-requests MUL-123 --output json
# 确认所有子任务完成后再标记 done
multica issue children MUL-123 --output json
```

### 3.7 Metadata 操作

```bash
multica issue metadata set <id> --key <k> --value <v> [--type string|number|bool]
multica issue metadata delete <id> --key <k>
```

Metadata 是**持久化的 Issue 状态**，不是日志。

❌ **错误做法**：把 Metadata 当便签本
```bash
multica issue metadata set MUL-123 --key note --value "正在调查中，第3次尝试"
# → 临时笔记不属于 Metadata，会被其他运行时读取造成误导
```

✅ **正确做法**：只写未来运行会重新读取的高价值信息

| 适合写入 Metadata | 不适合写入 |
|------------------|-----------|
| `pr_url`, `pr_number` | "正在调查中" |
| `pipeline_status` | "第 3 次尝试" |
| `deploy_url` | 临时笔记 |
| `external_issue_url` | 日志信息 |
| `waiting_on`, `blocked_reason` | |
| `decision`（最终决策） | |

### 3.8 Mention 构建

❌ **错误做法**：凭名字猜 UUID，或为了礼貌而感谢
```markdown
感谢 @builder-agent 的帮助！
[@builder-agent](mention://agent/猜测的uuid)
// → 如果 UUID 错误，mention 会失败；如果 UUID 正确，会触发 Agent 再次运行
```

✅ **正确做法**：先查 UUID，仅在需要 Agent 行动时才 mention
```bash
multica agent list --output json   # 获取真实 agent UUID
multica squad list --output json   # 获取真实 squad UUID
```
```markdown
请 [@builder-agent](mention://agent/<真实uuid>) 开始实现这个功能。
```

### 3.9 其他资源（探索式学习）

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

## 四、快速上手

### 4.1 前置条件

1. 本机已安装 `multica` CLI
2. 用户已通过 `multica login`（或 `multica setup`）完成认证
3. 已选择目标 workspace / profile，或通过 `--workspace-id`、`--profile` 显式传入

### 4.2 安装 Skill

Skill 位于仓库的 `skills/multica-cli/` 目录，支持多种工具：

**Claude Code（插件市场，推荐）**
```
/plugin marketplace add multica-ai/multica-cli
/plugin install multica-cli@multica-cli
```

**Codex（Skill 安装器）**
```bash
install-skill-from-github.py --repo multica-ai/multica-cli --path skills/multica-cli
```
安装后重启 Codex。

**Cursor**
```bash
# 方式一：个人 Skill（跨项目）
mkdir -p ~/.cursor/skills/multica-cli
cp -R skills/multica-cli/* ~/.cursor/skills/multica-cli/

# 方式二：项目规则（单项目）
# 把 .cursor/rules/multica-cli.mdc 复制到项目的 .cursor/rules/ 目录
```

**其他 Agent**：把 `skills/multica-cli/SKILL.md` 复制到你的工具加载 Skill/指令的位置即可。

### 4.3 安全启动流程

安装后，每次操作前必须执行三步验证：

**第一步：检查 CLI 和账户状态**
```bash
multica version
multica auth status
multica config show
```

如果 `auth status` 报告没有活跃会话，**必须停止**：
```bash
multica login
```

**第二步：确认 Workspace 和 Profile**
```bash
multica workspace list --output json
multica workspace switch <workspace-id>
```

**第三步：第一个读操作（验证连通性）**
```bash
multica issue list --status todo --limit 5 --output json
```

如果能正常返回 JSON，说明配置正确，可以开始操作。

---

## 五、工作流实战

### 5.1 读工作流：先收集上下文

**先读后写**。在决定是否需要写操作之前，先收集完整上下文：

```bash
multica issue get <issue-id-or-key> --output json
multica issue comment list <issue-id-or-key> --recent 10 --output json
multica issue metadata list <issue-id-or-key> --output json
multica issue pull-requests <issue-id-or-key> --output json
```

**大评论历史的高效读取**：
```bash
# 只看某个讨论串最近 30 条
multica issue comment list <issue-id> --thread <comment-id> --tail 30 --output json
# 只看最近活跃的 10 个讨论
multica issue comment list <issue-id> --recent 10 --output json
```

### 5.2 写工作流：副作用确认

写操作有副作用。如果用户没有明确要求写，**必须先问**。

需要确认的写操作包括：创建评论、创建 Issue、状态变更、分配、Rerun、Agent Mention、Squad Mention、Webhook/Autopilot 变更、Repo Checkout。

**评论写入标准流程**：
```bash
# 1. 先创建 reply.md（真实换行，不要用 \n 转义）
# 2. 然后：
multica issue comment add <issue-id> --parent <comment-id> --content-file ./reply.md
# 3. 清理临时文件
rm ./reply.md
```

**长描述也用文件**：
```bash
multica issue create --title "..." --description-file ./description.md
multica issue update <issue-id> --description-file ./description.md
```

### 5.3 Pull Request 关联

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

❌ **错误做法**：从 GitHub 搜索 PR 状态，或从 Metadata 猜测
```bash
# 不要猜！
gh pr list --search "MUL-123"
```

✅ **正确做法**：从 Multica 读取关联 PR 状态
```bash
multica issue pull-requests <issue-id> --output json
```

### 5.4 有序子 Issue 模式

创建分步骤的子 Issue 时，用 stages 和 `backlog` 控制后续步骤的执行顺序：

```bash
# 第一步：立即开始
multica issue create --title "Research" --parent <id> --assignee <agent> --stage 1 --status todo
# 后续步骤：排队等待
multica issue create --title "Build" --parent <id> --assignee <agent> --stage 2 --status backlog
multica issue create --title "Test" --parent <id> --assignee <agent> --stage 3 --status backlog
# 查看进度
multica issue children <id> --output json
```

---

## 六、设计理念与生态上下文

### 6.1 这个 Skill 本身就是 Karpathy 准则的典范

`multica-cli` Skill 的设计完美体现了 Karpathy 四条 LLM 编程准则：

| Karpathy 原则 | multica-cli 中的体现 | 具体规则 |
|--------------|---------------------|---------|
| **编码前先思考** | 启动流程先验证状态、确认 workspace；缺失上下文先问而非硬猜 | 安全启动三步法、外部Agent信息边界 |
| **简约至上** | 命令参考只列最常用 flag，长尾命令用 `--help` 探索；不做多余抽象 | 其他资源用 --help 探索、Metadata写入原则 |
| **精确编辑** | 写操作有明确边界；不擅自修改无关内容；评论用文件传递避免 shell 破坏 | --content-file强制、Mention精确UUID |
| **目标驱动** | 读工作流→收集上下文→决定是否写；明确哪些操作是副作用需要确认 | 先读后写、写操作确认清单 |

### 6.2 违反安全规则的真实代价

不只是"最佳实践"——以下是真实会发生的后果：

| 违规行为 | 真实代价 |
|---------|---------|
| 用 `--content` 传评论 | Shell转义破坏代码块、链接、变量，发布乱码或错误内容 |
| 在感谢回复中 @Agent | Agent被触发重新运行，可能再次回复并@回来→无限循环，消耗大量token |
| 不查UUID就Mention | Mention失败（无效UUID）或@错Agent（触发错误的人/Agent工作） |
| 随意切状态到done | 正在工作的Agent被终止，未完成的子任务数据不一致 |
| Metadata写临时笔记 | 其他Agent读取到过时信息（如"正在调查中"但实际已修复），做出错误决策 |
| 猜测PR状态 | 可能重复创建PR、合并错误分支、或遗漏已有的修复方案 |
| 未登录就操作 | Agent收到认证错误后可能尝试"修复"（如重新登录、猜测token），造成安全风险 |

### 6.3 Multica 平台生态中 Skill 的位置

```
┌─────────────────────────────────────────────────┐
│  你（人类用户）                                  │
│  用自然语言给 Agent 下达指令                      │
└──────────────┬──────────────────────────────────┘
               │ 自然语言指令
               ▼
┌─────────────────────────────────────────────────┐
│  外部编码 Agent（Claude Code / Codex / Cursor）  │
│  + multica-cli SKILL.md（本文件=安全操作手册）   │
└──────────────┬──────────────────────────────────┘
               │ multica CLI 命令
               ▼
┌─────────────────────────────────────────────────┐
│  multica CLI（本地已认证）                       │
│  权限来自本机登录态，不经过第三方                 │
└──────────────┬──────────────────────────────────┘
               │ HTTP/本地Daemon
               ▼
┌─────────────────────────────────────────────────┐
│  Multica 平台（Server + Daemon + DB）           │
│  Agent Runtime / Issue / Squad / Autopilot      │
└─────────────────────────────────────────────────┘
```

关键设计：**Server 不直接调用 LLM**，代码和密钥不出用户机器。Skill 只是教 Agent 如何"礼貌地"使用 CLI，不做任何权限提升。

### 6.4 延伸阅读

- [06 - Multica 平台介绍](06-multica-platform.md)：Multica 平台架构、17个核心概念词典、系统架构图、8大功能模块
- [01 - 四条核心原则](01-four-principles.md)：Karpathy LLM编程四条准则的完整解读
- [02 - 代码示例](02-code-examples.md)：LLM编程中常见错误与正确做法的代码级正反例
- multica-cli 仓库：https://github.com/multica-ai/multica-cli
- Multica 主仓库：https://github.com/multica-ai/multica
- [教程认知阶梯模式](../../../../retrospective/patterns/methodology-patterns/document-architecture/tutorial-cognitive-ladder.md)：本文档使用的结构设计方法论
