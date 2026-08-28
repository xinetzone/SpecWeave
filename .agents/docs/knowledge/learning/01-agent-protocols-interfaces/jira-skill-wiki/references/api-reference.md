---
type: Reference
title: "CLI API 参考信源"
description: "jira-communication 所有CLI脚本的子命令、选项和参数完整登记"
tags: ["jira", "cli", "api", "reference"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "file:///d:/AI/vendor/jira-skill/skills/jira-communication/scripts/core/"
    type: "source-code"
    trust: high
  - resource: "file:///d:/AI/vendor/jira-skill/skills/jira-communication/scripts/workflow/"
    type: "source-code"
    trust: high
  - resource: "file:///d:/AI/vendor/jira-skill/skills/jira-communication/scripts/utility/"
    type: "source-code"
    trust: high
  - resource: "file:///d:/AI/vendor/jira-skill/skills/jira-communication/scripts/lib/"
    type: "source-code"
    trust: high
---

# CLI API 参考信源

本文件登记所有脚本的命令行接口细节，作为概念文档和示例文档中命令引用的溯源依据。

## 全局选项

所有命令组脚本共享以下5个全局选项（F-G001）：

| 选项 | 说明 |
|------|------|
| `--json` | 输出机器可读 JSON |
| `--quiet` | 最小输出模式 |
| `--env-file PATH` | 指定环境变量文件（默认 `~/.env.jira`） |
| `--profile NAME` | 指定配置 profile（默认 `~/.jira/profiles.json`） |
| `--debug` | 启用调试输出 |

写操作通用选项：

| 选项 | 说明 |
|------|------|
| `--dry-run` | 预览变更但不实际执行 |

## core/jira-issue.py

### get

```
jira-issue.py get ISSUE_KEY [--fields FIELDS] [--expand EXPAND] [--truncate N] [--raw]
```

- 获取工单详情
- `--fields`：指定返回字段
- `--expand`：Jira REST API expand 参数
- `--truncate`：截断长文本
- `--raw`：输出原始 API 响应

### update

```
jira-issue.py update ISSUE_KEY [--summary TEXT] [--description TEXT] [--priority NAME]
                               [--labels LABELS] [--assignee USER] [--fields-json JSON]
                               [--dry-run]
```

- 更新工单字段
- 支持通过 `--fields-json` 传递任意自定义字段

### delete

```
jira-issue.py delete ISSUE_KEY [--delete-subtasks] [--dry-run]
```

### work（意图动词）

```
jira-issue.py work ISSUE_KEY
```

- 自动获取：工单详情 + 评论 + 状态历史 + 时间统计
- 对应常量：`INTENT_FIELDS`

### qa（意图动词）

```
jira-issue.py qa ISSUE_KEY
```

- 获取 QA 审查所需上下文

### qa-fail（意图动词）

```
jira-issue.py qa-fail ISSUE_KEY
```

- QA 失败跟进上下文

### act（意图动词）

```
jira-issue.py act ISSUE_KEY
```

- 交互式选择并执行状态转换

### time-in-status

```
jira-issue.py time-in-status ISSUE_KEY
```

- 计算工单在各状态的停留时间

## core/jira-search.py

### query

```
jira-search.py query JQL [--max-results N] [--fields FIELDS] [--start-at N] [--order-by FIELD]
```

- `--max-results/-n`：结果上限，默认 50
- `--fields/-f`：返回字段
- `--start-at`：分页起始位置
- 自动检测并追加 ORDER BY 子句

## core/jira-worklog.py

### add

```
jira-worklog.py add ISSUE_KEY TIME_SPENT [--comment TEXT] [--started DATETIME]
```

- `TIME_SPENT` 格式示例：`"2h 30m"`

### list

```
jira-worklog.py list ISSUE_KEY
```

### delete

```
jira-worklog.py delete ISSUE_KEY WORKLOG_ID
```

## core/jira-attachment.py

### download

```
jira-attachment.py download ATTACHMENT_ID [--output PATH]
```

### download-all

```
jira-attachment.py download-all ISSUE_KEY [--output-dir DIR]
```

### add

```
jira-attachment.py add ISSUE_KEY FILE_PATH
```

- 流式上传/下载，`CHUNK_SIZE = 1048576`（1MB）

## core/jira-setup.py

```
jira-setup.py [--url URL] [--type cloud|pat] [--output PATH] [--profile NAME]
              [--projects PROJECTS] [--migrate]
```

- 交互式凭证配置向导
- 可验证凭证有效性

## core/jira-validate.py

```
jira-validate.py [--all-profiles]
```

- 验证运行时环境、配置、连接性

## workflow/jira-transition.py

### list

```
jira-transition.py list ISSUE_KEY
```

### do

```
jira-transition.py do ISSUE_KEY TRANSITION_NAME [--comment TEXT] [--resolution NAME] [--dry-run]
```

### path

```
jira-transition.py path ISSUE_KEY TARGET_STATUS [--max-steps N] [--dry-run]
```

- 自动寻找多步转换路径
- 转换匹配三级策略：精确匹配 → 规范化匹配 → 子串匹配（`find_matching_transition()`）

## workflow/jira-comment.py

### add

```
jira-comment.py add ISSUE_KEY [COMMENT_TEXT | -]
```

- `-` 从 stdin 读取（上限 256KB）
- 自动运行 wiki markup 检查和 @提及验证

### edit / delete / list

```
jira-comment.py edit ISSUE_KEY COMMENT_ID [COMMENT_TEXT | -]
jira-comment.py delete ISSUE_KEY COMMENT_ID
jira-comment.py list ISSUE_KEY [--limit N]
```

- `--limit 0` 表示获取全部评论
- 评论列表最新在前

## workflow/jira-create.py

### issue

```
jira-create.py issue PROJECT SUMMARY [--type TYPE] [--description TEXT | -]
                                      [--priority NAME] [--labels LABELS]
                                      [--assignee USER] [--parent KEY]
                                      [--components COMPONENTS] [--fields-json JSON]
```

- `--parent` 自动解析为子任务类型

### project

```
jira-create.py project KEY NAME [--lead USER]
```

## workflow/jira-board.py

```
jira-board.py list
jira-board.py issues BOARD_ID [--jql JQL]
```

使用 Agile API（`rest/agile/1.0/`）。

## workflow/jira-sprint.py

```
jira-sprint.py list [--board BOARD_ID]
jira-sprint.py issues SPRINT_ID
jira-sprint.py current [--board BOARD_ID]
```

## workflow/jira-version.py

共12个子命令：

```
jira-version.py list PROJECT
jira-version.py get VERSION_ID
jira-version.py create PROJECT NAME [--description TEXT] [--start-date DATE] [--release-date DATE]
jira-version.py update VERSION_ID [--name NAME] [--description TEXT] ...
jira-version.py release VERSION_ID
jira-version.py unrelease VERSION_ID
jira-version.py archive VERSION_ID
jira-version.py unarchive VERSION_ID
jira-version.py move VERSION_ID --position POSITION
jira-version.py merge SOURCE_ID TARGET_ID
jira-version.py delete VERSION_ID [--move-fix-to ID] [--move-affected-to ID]
```

## workflow/jira-move.py

```
jira-move.py issue ISSUE_KEY NEW_TYPE
```

- 故意拒绝跨项目移动

## workflow/tempo-account.py

```
tempo-account.py customer ...
tempo-account.py account create|link ...
```

使用 Tempo Timesheets API（`rest/tempo-accounts/1/`）。

## utility/ 脚本

| 脚本 | 主要子命令 |
|------|-----------|
| `jira-fields` | `search QUERY`、`list`、`types` |
| `jira-user` | `me`、`get ACCOUNT_ID`、`search QUERY` |
| `jira-link` | `create`、`list ISSUE_KEY`、`list-types`、`delete`、`bulk-create`、`bulk-delete`、`invert` |
| `jira-watchers` | `list ISSUE_KEY`、`add ISSUE_KEY USER`、`remove ISSUE_KEY USER` |
| `jira-weblink` | `add ISSUE_KEY URL TITLE`、`list ISSUE_KEY`、`update`、`delete` |
| `jira-qa-gather` | `ISSUE_KEY`（单命令，一次性聚合QA上下文） |
| `jira-worklog-query` | 跨 cut 工时查询，支持 Jira 和 Tempo 双后端 |

## 共享库关键 API

### client.py

- `LazyJiraClient(env_file=None, profile=None)` — 延迟初始化客户端
- `LazyJiraClient.jql(jql, limit=50, start=0, fields=None, **kwargs) -> dict`
- `get_jira_client(env_file=None, profile=None, issue_key=None, url=None) -> Jira`
- `is_account_id(s) -> bool`
- `resolve_assignee(client, identifier) -> dict`
- `fetch_comments_paginated(client, issue_key, page_size=100)`
- `resolve_status(client, identifier) -> str`
- `SessionExpiredError` — 会话过期异常
- Cloud JQL 端点：`rest/api/3/search/jql`，分页硬上限 1000

### config.py

- `DEFAULT_ENV_FILE = ~/.env.jira`
- `PROFILES_FILE = ~/.jira/profiles.json`
- `get_auth_mode(config) -> str`（返回 `"pat"` 或 `"cloud"`）
- `is_cloud_url(url) -> bool`（判断 netloc 是否为 atlassian.net）
- `load_config(profile=None, env_file=None, issue_key=None, url=None) -> dict`
- `resolve_profile(issue_key=None, url=None, profile=None, project_dir=None) -> dict`
- Issue key 正则：`^([A-Z][A-Z0-9_]+)-\d+$`

### users.py

- `MENTION_PATTERN = re.compile(r"(?<!\\)\[~([^\]\s]+)]")`
- `find_users(client, query, limit=10) -> list[dict]`
- `verify_mentions(client, text) -> dict[str, list[dict]]`
- `check_mentions_cli(client, text, skip=False)`

### markup.py

- `lint_wiki_markup(text) -> list[str]`
- `BLOCK_TAGS = ("code", "noformat", "quote", "panel")`

### changelog.py

- `parse_jira_datetime(s: str) -> datetime` — 解析 Jira ISO 8601 日期时间字符串
- `extract_status_transitions(issue: dict) -> list[dict]` — 从工单数据提取状态变更历史
- `compute_time_in_status(issue_created: datetime, transitions: list[dict], current_status: str, now: datetime) -> dict[str, timedelta]` — 计算各状态停留时间
- `extract_status_transitions_with_authors(issue: dict) -> list[dict]` — 提取状态变更记录（含作者信息）
- `classify_transition(transition: dict, status_sets: dict) -> TransitionKind` — 分类转换类型
- `find_transition_window(transitions: list[dict], target_index: int) -> tuple[datetime | None, datetime | None]` — 查找指定转换的时间窗口
- `format_timedelta(delta: timedelta) -> str` — 将 timedelta 格式化为人类可读字符串
- TransitionKind: into_qa, reject, forward, resolved, out, other

### errors.py

- `CaptchaError(Exception)`（含 `login_url` 属性）
- `AuthenticationError(Exception)`
- `_sanitize_error(message) -> str`

### 其他

- `input.py`: `read_stdin_utf8(max_chars=None) -> str`
- `jql.py`: `jql_escape(value) -> str`（转义反斜杠和双引号）
- `render.py`: `print_comment(comment, truncate=None)`、`print_description(issue, truncate=None)`
- `output.py`: `format_output(data, as_json=False, quiet=False)`、`format_json()`、`format_table()`、`error()`、`success()`、`warning()`、`extract_adf_text()`
