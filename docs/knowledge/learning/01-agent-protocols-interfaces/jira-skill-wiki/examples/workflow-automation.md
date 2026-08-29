---
type: Example
title: "工作流自动化示例"
description: "演示意图动词、多步转换路径、QA上下文聚合、版本管理等高级工作流自动化模式。"
tags: ["jira", "workflow", "automation", "intent-verbs", "qa", "transition"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "/references/api-reference.md"
    type: "source-code"
    trust: high
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
---

# 工作流自动化示例

本示例演示如何利用 jira-skill 的意图动词和工作流脚本，将多步 Jira 操作压缩为单次命令调用，减少 AI 智能体与 Jira 之间的往返次数。

## 意图动词模式

### work：开始处理工单

当开发者或 AI 智能体需要"开始处理一个工单"时，通常需要：

1. 获取工单详情
2. 阅读历史评论
3. 查看状态变更历史
4. 了解已耗工时

传统方式需要 3-4 次 API 调用。`work` 意图动词将其压缩为一次：

```bash
uv run scripts/core/jira-issue.py work PROJ-123
```

该命令内部通过 `INTENT_FIELDS` 常量指定了需要一次性获取的字段集，返回完整的工作上下文。

### qa：QA 审查

QA 工程师审查工单时需要的上下文与开发者不同。`qa` 意图动词自动获取 QA 视角所需信息：

```bash
uv run scripts/core/jira-issue.py qa PROJ-123
```

### qa-gather：QA 上下文聚合

对于更复杂的 QA 场景，utility 层的 `jira-qa-gather` 提供更深层次的一次性聚合：

```bash
uv run scripts/utility/jira-qa-gather PROJ-123
```

该命令一次性获取：

- 工单详情和描述
- 所有评论
- 工时记录
- 工单链接关系
- 同级/子工单信息

这比手动逐个调用 core/utility 脚本减少 5-6 次往返。

### act：交互式状态变更

```bash
uv run scripts/core/jira-issue.py act PROJ-123
```

`act` 命令会列出当前工单可用的所有转换，并提示用户选择。它封装了"查询可用转换 → 用户选择 → 执行转换"的完整交互流程。

## 多步转换路径

### 问题

在 Jira 工作流中，从"To Do"到"Done"往往不能一步完成，需要经过"In Progress"→"Code Review"→"QA"→"Done"等中间状态。手动查询每一步可用的转换非常繁琐。

### 解决方案：path 子命令

```bash
# 自动寻找从当前状态到"Done"的路径并执行
uv run scripts/workflow/jira-transition.py path PROJ-123 "Done"

# 限制最大步数（防止路径过长）
uv run scripts/workflow/jira-transition.py path PROJ-123 "Done" --max-steps 5

# 先预览再执行
uv run scripts/workflow/jira-transition.py path PROJ-123 "Done" --dry-run
```

### 转换匹配机制

`jira-transition.py` 的 `find_matching_transition()` 函数使用三级匹配策略：

1. **精确匹配**：转换名称完全一致
2. **规范化匹配**：忽略大小写、空格和特殊字符
3. **子串匹配**：转换名称包含目标字符串

这意味着即使 Jira 中转换名为"Ready for QA"，你也可以用 `"qa"` 来匹配。

### 带评论和解决结果的转换

```bash
# 执行转换并添加评论
uv run scripts/workflow/jira-transition.py do PROJ-123 "QA" \
  --comment "代码审查通过，移交QA测试。"

# 关闭工单并设置解决结果
uv run scripts/workflow/jira-transition.py do PROJ-123 "Done" \
  --resolution "Fixed" \
  --comment "问题已修复并验证。" \
  --dry-run
```

## 版本发布工作流

### 完整版本生命周期

```bash
# 1. 创建版本
uv run scripts/workflow/jira-version.py create PROJ "v2.0.0" \
  --description "主要功能更新" \
  --release-date "2026-09-15"

# 2. 查看版本中的工单
uv run scripts/core/jira-search.py query "project = PROJ AND fixVersion = v2.0.0"

# 3. 发布版本
uv run scripts/workflow/jira-version.py release 10001

# 4. 如果有问题，取消发布
uv run scripts/workflow/jira-version.py unrelease 10001

# 5. 归档版本
uv run scripts/workflow/jira-version.py archive 10001
```

### 合并版本

当两个版本需要合并时：

```bash
# 将 v1.9.0 的工单合并到 v2.0.0
uv run scripts/workflow/jira-version.py merge 10000 10001
```

### 删除版本并迁移工单

```bash
# 删除版本，将其 fixVersion 工单迁移到目标版本
uv run scripts/workflow/jira-version.py delete 10000 \
  --move-fix-to 10001 \
  --move-affected-to 10001
```

## 看板与冲刺

```bash
# 列出所有看板
uv run scripts/workflow/jira-board.py list

# 获取看板上的工单
uv run scripts/workflow/jira-board.py issues 42

# 列出冲刺
uv run scripts/workflow/jira-sprint.py list --board 42

# 获取当前冲刺
uv run scripts/workflow/jira-sprint.py current --board 42

# 获取冲刺中的工单
uv run scripts/workflow/jira-sprint.py issues 123
```

这些命令使用 Jira Agile API（`rest/agile/1.0/`）。

## 工单链接批量操作

```bash
# 创建"克隆"关系
uv run scripts/utility/jira-link.py create PROJ-123 PROJ-124 --type Cloners

# 批量创建链接
uv run scripts/utility/jira-link.py bulk-create PROJ-123 PROJ-200,PROJ-201,PROJ-202 --type Relates

# 反转链接方向
uv run scripts/utility/jira-link.py invert PROJ-123 PROJ-124 --type Relates
```

## 关注者管理

```bash
# 列出关注者
uv run scripts/utility/jira-watchers.py list PROJ-123

# 添加关注者
uv run scripts/utility/jira-watchers.py add PROJ-123 john.doe

# 移除关注者
uv run scripts/utility/jira-watchers.py remove PROJ-123 john.doe
```

## 推荐工作流模式

### AI 智能体处理工单的标准流程

```bash
# 第1步：获取完整工作上下文
uv run scripts/core/jira-issue.py work PROJ-123

# 第2步：开始工作（状态流转）
uv run scripts/workflow/jira-transition.py do PROJ-123 "In Progress"

# 第3步：完成工作后添加评论
echo "h2. 完成情况\n\n* 已修复根因\n* 添加了单元测试" | \
  uv run scripts/workflow/jira-comment.py add PROJ-123 -

# 第4步：记录工时
uv run scripts/core/jira-worklog.py add PROJ-123 "4h" --comment "修复并测试"

# 第5步：流转到下一个状态（自动寻路）
uv run scripts/workflow/jira-transition.py path PROJ-123 "Code Review"
```

### QA 审查流程

```bash
# 第1步：聚合QA上下文（一次调用获取全部信息）
uv run scripts/utility/jira-qa-gather PROJ-123

# 第2步：验证通过，流转到下一状态
uv run scripts/core/jira-issue.py qa PROJ-123

# 第3步：如果通过
uv run scripts/workflow/jira-transition.py do PROJ-123 "Done" --resolution "Fixed"

# 如果失败
uv run scripts/core/jira-issue.py qa-fail PROJ-123
uv run scripts/workflow/jira-transition.py do PROJ-123 "Reopened" --resolution "Incomplete"
```

## 相关概念

- [jira-communication 技能](/concepts/04-jira-communication.md)：意图动词机制详解
- [最佳实践与反模式](/concepts/07-best-practices.md)：工作流使用建议
- [基础 CLI 使用示例](/examples/basic-cli-usage.md)：基础命令参考
- [CLI API 参考](/references/api-reference.md)：完整命令参考
