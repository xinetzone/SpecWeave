---
type: Concept
title: "快速开始"
description: "Jira 集成插件快速开始指南，覆盖搜索、工单详情、创建、流转、评论、工时、冲刺看板、工具查询的完整命令示例。"
tags: ["jira", "quickstart", "cli", "search", "worklog", "transition", "examples"]
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
---
# 第 3 章：快速开始

本章通过一组最常用的命令示例，让读者快速上手。命令需从 `skills/jira-communication/` 目录运行，或从仓库根目录使用 `skills/jira-communication/` 前缀。

## 3.1 快速上手四连

```bash
# 搜索工单
uv run scripts/core/jira-search.py query "project = PROJ AND status = 'In Progress'"

# 获取工单详情
uv run scripts/core/jira-issue.py get PROJ-123

# 记录工时
uv run scripts/core/jira-worklog.py add PROJ-123 "2h 30m" -c "Code review"

# 创建工单
uv run scripts/workflow/jira-create.py issue PROJ "Fix bug" --type Bug --priority High
```

## 3.2 搜索与筛选

```bash
# 查找项目中未关闭的 Bug
uv run scripts/core/jira-search.py query "project = PROJ AND type = Bug AND status != Done"

# 查找当前用户的工单
uv run scripts/core/jira-search.py query "assignee = currentUser()"

# 以 JSON 输出便于处理
uv run scripts/core/jira-search.py query "project = PROJ" --json --max-results 100
```

## 3.3 工单管理

```bash
# 获取工单详情
uv run scripts/core/jira-issue.py get PROJ-123

# 更新工单字段（先 dry-run 预览）
uv run scripts/core/jira-issue.py update PROJ-123 --labels "urgent,backend" --dry-run

# 创建新工单
uv run scripts/workflow/jira-create.py issue PROJ "Implement feature X" --type Story --priority Medium
```

## 3.4 工时记录

```bash
# 记录工作时长
uv run scripts/core/jira-worklog.py add PROJ-123 "2h 30m" -c "Implemented core logic"

# 查看工时记录
uv run scripts/core/jira-worklog.py list PROJ-123
```

## 3.5 工作流流转

```bash
# 列出可用流转
uv run scripts/workflow/jira-transition.py list PROJ-123

# 流转工单（先 dry-run 预览）
uv run scripts/workflow/jira-transition.py do PROJ-123 "In Progress" --dry-run

# 正式流转
uv run scripts/workflow/jira-transition.py do PROJ-123 "In Progress"
```

## 3.6 评论

```bash
# 添加评论
uv run scripts/workflow/jira-comment.py add PROJ-123 "Investigation complete - root cause identified"

# 查看最近的评论
uv run scripts/workflow/jira-comment.py list PROJ-123 --limit 5
```

## 3.7 冲刺与看板

```bash
# 列出项目的看板
uv run scripts/workflow/jira-board.py list --project PROJ

# 获取看板上的工单
uv run scripts/workflow/jira-board.py issues 42

# 列出进行中的冲刺
uv run scripts/workflow/jira-sprint.py list 42 --state active

# 获取冲刺工单
uv run scripts/workflow/jira-sprint.py issues 123

# 获取当前冲刺
uv run scripts/workflow/jira-sprint.py current 42
```

## 3.8 工具查询

```bash
# 搜索自定义字段
uv run scripts/utility/jira-fields.py search "story points"

# 列出所有自定义字段
uv run scripts/utility/jira-fields.py list --type custom

# 获取当前用户信息
uv run scripts/utility/jira-user.py me

# 列出可用的链接类型
uv run scripts/utility/jira-link.py list-types

# 关联两个工单（先 dry-run）
uv run scripts/utility/jira-link.py create PROJ-123 PROJ-456 --type "Blocks" --dry-run
```

下一章将深入讲解 `jira-communication` 技能的脚本体系与意图动词机制。

## 相关概念

- [jira-communication 技能](/concepts/04-jira-communication.md)：深入了解API操作
- [JQL 查询语言](/concepts/06-jql.md)：高级搜索技巧
- [最佳实践](/concepts/07-best-practices.md)：工程经验总结
- [CLI API 参考](/references/api-reference.md)：完整命令参考