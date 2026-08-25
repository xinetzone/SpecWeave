---
type: Reference
title: jira-skill 源码
description: Jira Integration Plugin v3.28.0 源码登记，含双技能架构、21脚本分层、PEP 723 内联依赖、LazyJiraClient 与配置库
tags: [agent-skills, jira, source, reference, plugin, pep723]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-jira-skill
    resource: "/references/facts-jira-skill.md"
    title: jira-skill 事实清单
---

# jira-skill 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | Jira Integration Plugin for Claude Code |
| 版本 | 3.28.0 |
| 作者 | Netresearch DTT GmbH |
| 仓库 | https://github.com/netresearch/jira-skill |
| 许可证 | (MIT AND CC-BY-SA-4.0) |
| 源码路径 | `d:\AI\.chaos\libs\tests\jira-skill\` |
| Python 要求 | 3.10、3.11、3.12、3.13 |
| 遵循标准 | Agent Skills 开放标准（agentskills.io） |
| 支持平台 | Jira Server/DC 和 Cloud |

## 插件配置（plugin.json）

遵循 `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`。

| 属性 | 值 |
|------|-----|
| name | `jira` |
| version | `3.28.0` |
| description | "Comprehensive Jira integration with auto-detection of issue keys" |
| keywords | jira、atlassian、issue-tracking、project-management、wiki-markup、syntax-validation、templates |

## 双技能架构

| 技能 | 定位 | allowed-tools |
|------|------|--------------|
| `jira-communication` | 通过 Python CLI 脚本进行 API 操作 | Bash(python:*), Bash(uv:*), Read, Write |
| `jira-syntax` | Wiki 标记语法、模板、验证 | 无（纯知识技能） |

两个技能的 `metadata.version` 必须与 plugin.json 版本一致，由 pre-commit 和 CI 强制执行。

## jira-communication 脚本架构

21 个脚本按三层组织：

### Core 脚本（6 个，`scripts/core/`）

| 脚本 | 职责 |
|------|------|
| `jira-issue.py` | 问题操作（get/update/delete/work/qa 等子命令） |
| `jira-search.py` | JQL 搜索，含 ORDER BY 检测逻辑 |
| `jira-worklog.py` | 工作日志记录 |
| `jira-attachment.py` | 附件上传/下载 |
| `jira-setup.py` | 配置初始化 |
| `jira-validate.py` | 配置验证 |

### Workflow 脚本（8 个，`scripts/workflow/`）

| 脚本 | 职责 |
|------|------|
| `jira-create.py` | 创建问题 |
| `jira-transition.py` | 状态转换（含 do 子命令） |
| `jira-comment.py` | 评论管理 |
| `jira-move.py` | 问题移动 |
| `jira-sprint.py` | Sprint 管理 |
| `jira-board.py` | 看板管理 |
| `jira-version.py` | 版本管理 |
| `tempo-account.py` | Tempo 账户管理 |

### Utility 脚本（7 个，`scripts/utility/`）

| 脚本 | 职责 |
|------|------|
| `jira-user.py` | 用户查询 |
| `jira-fields.py` | 字段查询 |
| `jira-link.py` | 问题链接 |
| `jira-weblink.py` | Web 链接 |
| `jira-worklog-query.py` | 工作日志查询 |
| `jira-watchers.py` | 观察者管理 |
| `jira-qa-gather.py` | QA 信息收集 |

### 共享库（`scripts/lib/`）

| 模块 | 职责 |
|------|------|
| `client.py` | `LazyJiraClient` 类、`SessionExpiredError`、`resolve_assignee()`、`resolve_status()`、`fetch_comments_paginated()`、`_sanitize_error()`、`is_account_id()` |
| `config.py` | 配置加载（`load_config`、`validate_config`、`get_auth_mode`、`is_cloud_url`）、`normalize_netloc()`、`load_status_sets()`、Windows UTF-8 保证 |
| `errors.py` | `CaptchaError`、`AuthenticationError` 异常类 |
| `input.py` | `read_stdin_utf8()` 等输入处理 |
| `output.py` | `format_output()`、`compact_json()`、`success()`、`warning()`、`error()`、`comment_to_text()`、`extract_adf_text()` |
| `users.py` | `check_mentions_cli()`、`person_label()` |
| `jql.py` | JQL 处理 |
| `markup.py` | Wiki 标记处理 |
| `changelog.py` | 变更日志分析（`classify_transition`、`compute_time_in_status`、`extract_status_transitions` 等） |

所有脚本支持 `--help`、`--json`、`--quiet`、`--debug` 参数，破坏性操作支持 `--dry-run`。

## PEP 723 内联依赖

每个核心脚本使用 PEP 723 内联依赖声明：

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "atlassian-python-api>=3.41.0,<4",
#     "click>=8.1.0,<9",
# ]
# ///
```

- `atlassian-python-api` 固定在 `>=3.41,<4` 是有意为之：v4 有 Jira Cloud 变更和 DC 回归，主要目标是 Jira Server/DC 9.12。
- 脚本通过 PYTHONPATH 方式导入共享库（`sys.path.insert(0, str(_lib_path.parent))`），而非包安装。
- CLI 使用 click 框架定义子命令。

## 认证方式

| 部署类型 | 环境变量 |
|---------|---------|
| Jira Cloud | `JIRA_URL` + `JIRA_USERNAME` + `JIRA_API_TOKEN` |
| Jira Server/DC | `JIRA_URL` + `JIRA_PERSONAL_TOKEN` |

配置加载优先级：显式 env_file 参数 → `~/.env.jira` → 环境变量回退。配置文件路径：`~/.jira/profiles.json`。

`is_account_id()` 支持两种 Cloud 账户 ID 格式：带冒号的新格式（`557058:uuid`）和 24 字符十六进制旧格式。`resolve_assignee()` 处理 "me"、Cloud 账户 ID、用户名/邮箱的精确匹配和模糊搜索。

## jira-syntax 技能

### 快速语法参考

| Jira 语法 | Markdown 等价 |
|-----------|--------------|
| `h2. 标题` | `## 标题` |
| `*粗体*` | `**粗体**` |
| `_斜体_` | `*斜体*` |
| `{{代码}}` | `` `代码` `` |
| `{code:java}代码块{code}` | ` ```java 代码块 ``` ` |
| `[text\|url]` | `[text](url)` |
| `[~username]` | @用户提及 |

### 模板与验证

- 模板：`templates/bug-report-template.md`、`templates/feature-request-template.md`
- 验证脚本：`scripts/validate-jira-syntax.sh`（独立步骤运行，不与发布命令链式调用）
- 验证清单：标题格式、粗体、代码块、列表、链接、表格、颜色、面板
- 参考文档：`references/cross-project-refs.md`、`references/jira-syntax-quick-reference.md`

## jira-communication References（16 篇）

jql-cookbook、jql-quick-reference、multi-profile、troubleshooting、issue-editing、creation、comments、worklog、attachments、links、agile、no-editorializing、fields-and-users、watchers、versions、qa-gather、intent-verbs。

## 迁移背景（PRD.md）

从 mcp-atlassian Docker MCP 服务器迁移到基于 `uv run` + atlassian-python-api + click 的轻量脚本架构。原 MCP 方案问题：
- ~25 个工具加载消耗 8,000-12,000 Token/会话
- Docker 容器启动延迟
- Confluence 工具未使用
- 凭证需挂载到容器

126 个调试会话的使用分析显示 5 个工具占 80% 使用量：jira_add_worklog（22.8%）、jira_get_issue（18.6%）、jira_search（10.7%）、jira_update_issue（8.1%）、jira_create_issue（7.3%）。
