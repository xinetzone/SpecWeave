---
type: Concept
title: "JQL 查询语言"
description: "JQL 查询语言完整参考，涵盖排序、比较/文本/列表/历史操作符、用户/日期/冲刺/版本函数、常见查询与引号规则、Cloud 与 Server/DC 差异。"
tags: ["jira", "jql", "query", "search", "operators", "functions"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
  - resource: "/references/api-reference.md"
    type: "source-code"
    trust: high
  - resource: "/references/official-docs.md"
    type: "official-docs"
    trust: high
---
# 第 6 章：JQL 查询语言

**JQL**（Jira Query Language，Jira 查询语言）是 Jira 用于检索工单的查询语法，通过 `jira-search.py query "<JQL>"` 使用。本章汇总常用 JQL 模式。

## 6.1 排序（ORDER BY）

两种等价写法，二选一（脚本会拒绝混用）：

```bash
# 内嵌在 JQL 字符串中
jira-search query "project = PROJ AND status = Open ORDER BY updated DESC"

# 通过 --order-by 标志（可重复用于多键排序）
jira-search query "project = PROJ AND status = Open" --order-by "updated DESC"
jira-search query "project = PROJ" \
    --order-by "priority DESC" --order-by "created ASC"
```

## 6.2 操作符

### 6.2.1 比较操作符

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `=` | `status = "In Progress"` | 精确匹配 |
| `!=` | `status != Done` | 不相等 |
| `>` | `votes > 4` | 大于 |
| `>=` | `duedate >= "2024-01-01"` | 大于等于 |
| `<` | `priority < High` | 小于 |
| `<=` | `updated <= -4w` | 小于等于 |

### 6.2.2 文本搜索

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `~` | `summary ~ "login"` | 包含（模糊匹配） |
| `!~` | `summary !~ "test"` | 不包含 |

### 6.2.3 列表与空值

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `IN` | `status IN (Open, "In Progress")` | 多值 |
| `NOT IN` | `priority NOT IN (Low, Lowest)` | 排除多值 |
| `IS EMPTY` | `assignee IS EMPTY` | 字段无值 |
| `IS NOT EMPTY` | `fixVersion IS NOT EMPTY` | 字段有值 |

### 6.2.4 历史操作符

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `WAS` | `assignee WAS "john"` | 曾经的值 |
| `WAS IN` | `status WAS IN (Open, "To Do")` | 曾在列表中 |
| `WAS NOT` | `status WAS NOT Done` | 从未是某值 |
| `CHANGED` | `status CHANGED` | 值被修改过 |

`CHANGED` 支持谓词 `FROM`、`TO`、`BY`、`DURING`、`BEFORE`、`AFTER`、`ON`：

```jql
status CHANGED FROM "Open" TO "In Progress" BY currentUser() AFTER -7d
```

## 6.3 函数

### 6.3.1 用户函数

| 函数 | 说明 |
|------|------|
| `currentUser()` | 当前登录用户 |
| `membersOf("group")` | 组成员 |

### 6.3.2 日期函数

| 函数 | 说明 |
|------|------|
| `now()` | 当前时间 |
| `startOfDay()` | 今日零点 |
| `startOfWeek()` | 本周开始 |
| `startOfMonth()` | 本月第一天 |
| `startOfYear()` | 今年 1 月 1 日 |
| `endOfDay()` / `endOfWeek()` / `endOfMonth()` / `endOfYear()` | 对应周期结束 |

日期偏移：`startOfDay(-1)` 表示昨天，`startOfWeek(1)` 表示下周。

### 6.3.3 相对日期

| 格式 | 示例 | 说明 |
|------|------|------|
| `-Nd` | `-7d` | N 天前 |
| `-Nw` | `-2w` | N 周前 |
| `-Nm` | `-1m` | N 月前 |
| `"YYYY-MM-DD"` | `"2024-01-15"` | 具体日期 |

### 6.3.4 冲刺与版本函数

| 函数 | 说明 |
|------|------|
| `openSprints()` / `closedSprints()` / `futureSprints()` | 活跃 / 已完成 / 计划冲刺 |
| `releasedVersions()` / `unreleasedVersions()` / `latestReleasedVersion()` | 发布 / 未发布 / 最新发布版本 |

## 6.4 常见查询

```jql
# 按指派人
assignee = currentUser()
assignee IS EMPTY
assignee IN membersOf("developers")

# 按状态
status = "In Progress"
status IN (Open, "To Do", "In Progress")
status WAS "Open"

# 按日期
created >= -7d
updated >= startOfWeek()
resolved >= "2024-01-01"

# 按冲刺
sprint IN openSprints()
sprint = "Sprint 42"

# 按文本
text ~ "error message"
summary ~ "login bug"
```

## 6.5 组合条件

```jql
project = PROJ AND status = Open

priority = High OR priority = Highest

project = PROJ AND (status = Open OR status = "In Progress") AND assignee = currentUser()

NOT status = Done
```

## 6.6 引号规则

**必须加引号的值**：

- 含空格：`project = "My Project"`
- 含特殊字符：`summary ~ "error@host"`
- 保留字作值：`labels = "AND"`

**无需引号的值**：

- 单词：`status = Open`
- 项目键：`project = PROJ`
- 函数调用：`assignee = currentUser()`

## 6.7 Cloud 与 Server/DC 差异

- **用户引用**：Cloud 用 `accountId`（如 `assignee = "5b10ac8d82e05b22cc7d4ef5"`），Server/DC 用 `username`（如 `assignee = "john.doe"`）。`currentUser()` 在两者均可用。
- 函数如 `currentUser()`、`membersOf()`、日期函数、冲刺函数在两种平台均可工作。

## 6.8 参考资料

- [JQL 操作符（Cloud）](https://support.atlassian.com/jira-software-cloud/docs/jql-operators/)
- [JQL 函数（Cloud）](https://support.atlassian.com/jira-software-cloud/docs/jql-functions/)
- [JQL 操作符（Server/DC）](https://confluence.atlassian.com/jirasoftwareserver/advanced-searching-operators-reference-939938753.html)

## 相关概念

- [快速开始](/concepts/03-quickstart.md)：搜索命令入门
- [jira-communication 技能](/concepts/04-jira-communication.md)：API操作详解
- [最佳实践](/concepts/07-best-practices.md)：查询优化建议
- [CLI API 参考](/references/api-reference.md)：search命令参数