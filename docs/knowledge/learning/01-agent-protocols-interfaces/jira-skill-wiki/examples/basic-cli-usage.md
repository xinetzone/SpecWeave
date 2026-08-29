---
type: Example
title: "基础 CLI 使用示例"
description: "通过真实命令示例演示 jira-communication 的核心操作：搜索、获取、创建、评论、工时和附件管理。"
tags: ["jira", "cli", "examples", "search", "issue", "comment", "worklog"]
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

# 基础 CLI 使用示例

本示例演示 jira-communication 最常用的 CLI 操作。所有命令均需从 `skills/jira-communication/` 目录运行，或使用完整路径前缀。

## 前置条件

- 已完成[安装与配置](/concepts/02-installation.md)
- 凭证文件位于 `~/.env.jira`，或通过 `--env-file` 指定
- 已运行 `uv run scripts/core/jira-validate.py` 验证连接

## 搜索工单

使用 JQL（Jira Query Language）搜索工单：

```bash
# 基本搜索：查找项目 PROJ 中进行中的工单
uv run scripts/core/jira-search.py query "project = PROJ AND status = 'In Progress'"

# 限制返回数量并指定字段
uv run scripts/core/jira-search.py query "project = PROJ AND assignee = currentUser()" \
  --max-results 10 \
  --fields "summary,status,priority,updated"

# JSON 输出（适合管道处理）
uv run scripts/core/jira-search.py query "project = PROJ AND type = Bug" --json
```

**预期输出**（默认表格模式）：

```text
Key          Status        Priority    Summary
PROJ-123     In Progress   High        Login page crashes on Safari
PROJ-124     To Do         Medium      Add export to PDF feature
```

## 获取工单详情

```bash
# 获取工单完整信息
uv run scripts/core/jira-issue.py get PROJ-123

# 仅获取指定字段
uv run scripts/core/jira-issue.py get PROJ-123 --fields "summary,status,assignee,description"

# 使用意图动词 work（自动获取详情+评论+状态历史）
uv run scripts/core/jira-issue.py work PROJ-123
```

`work` 命令会自动聚合以下信息（对应源码中的 `INTENT_FIELDS` 常量）：

- 工单基本字段（summary、status、priority、assignee 等）
- 评论列表
- 状态变更历史
- 时间统计信息

## 创建工单

```bash
# 创建一个 Bug
uv run scripts/workflow/jira-create.py issue PROJ "登录页面在 Safari 上崩溃" \
  --type Bug \
  --priority High \
  --description "h2. 重现步骤\n\n# 打开 Safari 17\n# 导航到 /login\n# 输入凭证并点击登录\n\n*预期结果*：成功登录\n*实际结果*：页面白屏"

# 创建子任务
uv run scripts/workflow/jira-create.py issue PROJ "修复登录崩溃" \
  --type Sub-task \
  --parent PROJ-123 \
  --assignee "john.doe"

# 从 stdin 读取描述
cat description.txt | uv run scripts/workflow/jira-create.py issue PROJ "新功能" --description -
```

> **注意**：描述内容使用 Jira wiki markup 语法，而非 Markdown。参见 [jira-syntax 技能](/concepts/05-jira-syntax.md)。

## 添加评论

```bash
# 直接添加评论
uv run scripts/workflow/jira-comment.py add PROJ-123 "已定位问题，PR 已提交。"

# 从 stdin 读取长评论（上限 256KB）
echo "h2. 审查结果\n\n* 代码逻辑正确\n* 建议添加单元测试" | \
  uv run scripts/workflow/jira-comment.py add PROJ-123 -

# 列出评论
uv run scripts/workflow/jira-comment.py list PROJ-123 --limit 5
```

添加评论时，脚本会自动：

1. 运行 `lint_wiki_markup()` 检查 wiki 标记语法
2. 运行 `verify_mentions()` 验证 `[~username]` 提及的用户存在
3. 如果检查失败，输出错误并以退出码 1 终止

## 记录工时

```bash
# 记录 2 小时 30 分钟工时
uv run scripts/core/jira-worklog.py add PROJ-123 "2h 30m" --comment "代码审查"

# 查看已有工时
uv run scripts/core/jira-worklog.py list PROJ-123
```

时间格式支持 Jira 标准简写：`w`（周）、`d`（天）、`h`（小时）、`m`（分钟）。

## 状态流转

```bash
# 查看可用转换
uv run scripts/workflow/jira-transition.py list PROJ-123

# 执行转换
uv run scripts/workflow/jira-transition.py do PROJ-123 "In Progress"

# 使用意图动词 act（交互式选择转换）
uv run scripts/core/jira-issue.py act PROJ-123

# 多步路径转换（自动寻路）
uv run scripts/workflow/jira-transition.py path PROJ-123 "Done"
```

## 附件管理

```bash
# 上传附件
uv run scripts/core/jira-attachment.py add PROJ-123 ./screenshot.png

# 下载单个附件
uv run scripts/core/jira-attachment.py download 10001 --output ./screenshot.png

# 下载工单所有附件
uv run scripts/core/jira-attachment.py download-all PROJ-123 --output-dir ./attachments
```

附件以 1MB 块大小（`CHUNK_SIZE = 1048576`）进行流式传输，支持大文件。

## 工具查询

```bash
# 查找用户
uv run scripts/utility/jira-user.py search "john"

# 列出可用字段
uv run scripts/utility/jira-fields.py list

# 搜索字段
uv run scripts/utility/jira-fields.py search "resolution"

# 列出工单链接类型
uv run scripts/utility/jira-link.py list-types
```

## 使用 --dry-run 安全预览

所有写操作支持 `--dry-run` 选项，在不实际修改 Jira 的情况下预览将要执行的操作：

```bash
uv run scripts/workflow/jira-comment.py add PROJ-123 "测试评论" --dry-run
uv run scripts/core/jira-issue.py update PROJ-123 --priority Critical --dry-run
uv run scripts/workflow/jira-transition.py do PROJ-123 "Done" --dry-run
```

建议在首次执行写操作或批量操作前始终使用 `--dry-run`。

## 相关概念

- [快速开始](/concepts/03-quickstart.md)：更多命令速查
- [jira-communication 技能](/concepts/04-jira-communication.md)：技能机制详解
- [最佳实践](/concepts/07-best-practices.md)：工程经验与反模式
- [CLI API 参考](/references/api-reference.md)：完整命令和参数参考
