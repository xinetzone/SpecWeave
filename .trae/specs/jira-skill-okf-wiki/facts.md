# Jira Skill 源码事实清单

> R阶段产出：所有事实均直接从源码提取，不含推测性表述。
> 源码路径：`d:\AI\.chaos\libs\tests\jira-skill`
> 版本：v3.29.0

## 一、项目整体事实

| ID | 事实 | 来源 |
|---|---|---|
| F-P001 | 项目名称为 jira-skill，是 Claude Code 插件 | README.md |
| F-P002 | 包含两个技能：jira-communication 和 jira-syntax | README.md |
| F-P003 | 版本号为 3.29.0，定义于 .claude-plugin/plugin.json | plugin.json |
| F-P004 | 许可证为 MIT + CC-BY-SA-4.0 双许可 | README.md |
| F-P005 | 要求 Python 3.10+ | pyproject.toml |
| F-P006 | 使用 atlassian-python-api >=3.41,<4（故意不升级到v4） | pyproject.toml |
| F-P007 | 使用 Click >=8.1.0,<9 作为 CLI 框架 | 所有脚本 PEP 723 头 |
| F-P008 | 所有脚本通过 `uv run --script` 执行，使用 PEP 723 内联依赖 | 所有脚本 shebang |
| F-P009 | 兼容 Jira Server/DC 和 Cloud 两种部署形态 | README.md |
| F-P010 | 零 MCP 开销，脚本通过 Bash 直接调用 | README.md |

## 二、目录结构事实

| ID | 事实 | 来源 |
|---|---|---|
| F-D001 | skills/jira-communication/scripts/core/ 包含6个核心脚本 | 目录列表 |
| F-D002 | skills/jira-communication/scripts/workflow/ 包含8个工作流脚本 | 目录列表 |
| F-D003 | skills/jira-communication/scripts/utility/ 包含7个工具脚本 | 目录列表 |
| F-D004 | skills/jira-communication/scripts/lib/ 包含11个共享库文件 | 目录列表 |
| F-D005 | skills/jira-communication/references/ 包含17个参考文档 | 目录列表 |
| F-D006 | skills/jira-syntax/references/ 包含2个参考文档 | 目录列表 |
| F-D007 | skills/jira-syntax/templates/ 包含2个模板文件 | 目录列表 |
| F-D008 | tests/ 目录包含23个测试文件 | 目录列表 |

## 三、共享库事实（lib/）

### client.py

| ID | 事实 |
|---|---|
| F-L001 | `class LazyJiraClient` — 延迟初始化的 Jira 客户端封装 |
| F-L002 | `LazyJiraClient.__init__(self, env_file=None, profile=None)` |
| F-L003 | `LazyJiraClient.jql(self, jql, limit=50, start=0, fields=None, **kwargs) -> dict` |
| F-L004 | Cloud JQL 使用端点 `rest/api/3/search/jql`（F-029） |
| F-L005 | Cloud 分页硬上限 `_CLOUD_DRAIN_HARDCAP = 1000`（F-028） |
| F-L006 | `get_jira_client(env_file=None, profile=None, issue_key=None, url=None) -> Jira` 工厂函数 |
| F-L007 | 工厂函数配置 Retry(total=3, backoff_factor=1, status_forcelist=[429,502,503,504]) |
| F-L008 | `is_account_id(s: str) -> bool` 判断是否为账户ID |
| F-L009 | `resolve_assignee(client, identifier: str) -> dict` 解析经办人 |
| F-L010 | `fetch_comments_paginated(client, issue_key, page_size=100)` 分页获取评论 |
| F-L011 | `resolve_status(client, identifier: str) -> str` 解析状态名 |
| F-L012 | `class SessionExpiredError(Exception)` 会话过期异常 |
| F-L013 | JIRA_TIMEOUT = 30 秒 |

### config.py

| ID | 事实 |
|---|---|
| F-L014 | `DEFAULT_ENV_FILE = Path.home() / ".env.jira"` |
| F-L015 | `PROFILES_FILE = Path.home() / ".jira" / "profiles.json"` |
| F-L016 | Cloud 认证需要 JIRA_URL + JIRA_USERNAME + JIRA_API_TOKEN |
| F-L017 | Server/DC 认证需要 JIRA_URL + JIRA_PERSONAL_TOKEN |
| F-L018 | `get_auth_mode(config) -> str` 返回 "pat" 或 "cloud" |
| F-L019 | `is_cloud_url(url) -> bool` 判断 netloc 是否为 atlassian.net |
| F-L020 | `load_config(profile=None, env_file=None, issue_key=None, url=None) -> dict` |
| F-L021 | `resolve_profile(issue_key=None, url=None, profile=None, project_dir=None) -> dict` |
| F-L022 | Issue key 正则：`r"^([A-Z][A-Z0-9_]+)-\d+$"` |
| F-L023 | DEFAULT_QA_STATUSES 包含9个状态名 |
| F-L024 | DEFAULT_WORKING_STATUSES 包含7个状态名 |
| F-L025 | DEFAULT_RESOLVED_STATUSES 包含5个状态名 |

### output.py

| ID | 事实 |
|---|---|
| F-L026 | `format_output(data, as_json=False, quiet=False) -> None` 统一输出 |
| F-L027 | `format_json(data, indent=2) -> str` |
| F-L028 | `format_table(data, columns=None) -> str`，空数据返回 "(no data)" |
| F-L029 | `error(message, suggestion=None)` 输出到 stderr，前缀 "✗ " |
| F-L030 | `success(message)` 输出到 stdout，前缀 "✓ " |
| F-L031 | `warning(message)` 输出到 stderr，前缀 "⚠ " |
| F-L032 | `extract_adf_text(adf) -> str` 从 Atlassian Document Format 提取纯文本 |
| F-L033 | Windows 下自动 reconfigure stdout/stderr 为 UTF-8 |

### users.py

| ID | 事实 |
|---|---|
| F-L034 | `MENTION_PATTERN = re.compile(r"(?<!\\)\[~([^\]\s]+)\]")` 匹配 @提及 |
| F-L035 | `find_users(client, query, limit=10) -> list[dict]` 查找用户 |
| F-L036 | `verify_mentions(client, text) -> dict[str, list[dict]]` 验证提及的用户存在 |
| F-L037 | `check_mentions_cli(client, text, skip=False) -> None` CLI级提及验证，失败则 exit(1) |
| F-L038 | Cloud 使用 accountId，Server 使用 username |

### markup.py

| ID | 事实 |
|---|---|
| F-L039 | `lint_wiki_markup(text: str) -> list[str]` Jira wiki 标记检查 |
| F-L040 | BLOCK_TAGS = ("code", "noformat", "quote", "panel") |
| F-L041 | 检测未闭合的块级标签、Markdown 泄漏等问题 |

### changelog.py

| ID | 事实 |
|---|---|
| F-L042 | `extract_status_transitions(issue) -> list[dict]` 提取状态变更历史 |
| F-L043 | `compute_time_in_status(...) -> dict[str, timedelta]` 计算各状态停留时间 |
| F-L044 | `classify_transition(transition, status_sets) -> TransitionKind` 分类转换类型 |
| F-L045 | TransitionKind 类型：into_qa/reject/forward/resolved/out/other |

### errors.py

| ID | 事实 |
|---|---|
| F-L046 | `class CaptchaError(Exception)` 含 login_url 属性 |
| F-L047 | `class AuthenticationError(Exception)` |
| F-L048 | `_sanitize_error(message) -> str` 脱敏错误消息中的凭证 |

### 其他库文件

| ID | 事实 |
|---|---|
| F-L049 | input.py: `read_stdin_utf8(max_chars=None) -> str` 从 stdin 读取 UTF-8 文本 |
| F-L050 | jql.py: `jql_escape(value: str) -> str` 转义 JQL 字符串中的反斜杠和双引号 |
| F-L051 | render.py: `print_comment(comment, truncate=None)` 和 `print_description(issue, truncate=None)` |

## 四、核心脚本事实（core/）

### jira-issue.py（9个子命令）

| ID | 事实 |
|---|---|
| F-C001 | 子命令 `get` — 获取工单详情，选项 --fields/--expand/--truncate/--raw |
| F-C002 | 子命令 `update` — 更新工单，选项 --summary/--description/--priority/--labels/--assignee/--fields-json/--dry-run |
| F-C003 | 子命令 `delete` — 删除工单，选项 --delete-subtasks/--dry-run |
| F-C004 | 子命令 `work` — 意图动词：处理工单（获取详情+评论+状态历史） |
| F-C005 | 子命令 `qa` — 意图动词：QA 审查（获取QA相关上下文） |
| F-C006 | 子命令 `qa-fail` — 意图动词：QA 失败跟进 |
| F-C007 | 子命令 `act` — 意图动词：变更状态（交互式选择转换） |
| F-C008 | 子命令 `time-in-status` — 计算各状态停留时间 |
| F-C009 | INTENT_FIELDS 常量定义意图命令获取的字段集 |

### jira-search.py

| ID | 事实 |
|---|---|
| F-C010 | 子命令 `query` — JQL 搜索 |
| F-C011 | 选项 --max-results/-n（默认50）、--fields/-f、--start-at、--order-by |
| F-C012 | 自动检测并追加 ORDER BY 子句 |

### jira-worklog.py

| ID | 事实 |
|---|---|
| F-C013 | 子命令 `add` — 添加工时，参数 ISSUE_KEY + TIME_SPENT（如 "2h 30m"） |
| F-C014 | 子命令 `list` — 列分工时 |
| F-C015 | 子命令 `delete` — 删除工时 |

### jira-attachment.py

| ID | 事实 |
|---|---|
| F-C016 | 子命令 `download` — 下载单个附件 |
| F-C017 | 子命令 `download-all` — 下载工单所有附件 |
| F-C018 | 子命令 `add` — 上传附件 |
| F-C019 | CHUNK_SIZE = 1048576（1MB）流式下载 |

### jira-setup.py（单命令）

| ID | 事实 |
|---|---|
| F-C020 | 交互式凭证配置向导 |
| F-C021 | 支持 --url/--type/--output/--profile/--projects/--migrate |
| F-C022 | 可验证凭证有效性 |

### jira-validate.py（单命令）

| ID | 事实 |
|---|---|
| F-C023 | 验证运行时环境、配置、连接性 |
| F-C024 | 支持 --all-profiles 验证所有配置文件 |

## 五、工作流脚本事实（workflow/）

### jira-transition.py

| ID | 事实 |
|---|---|
| F-W001 | 子命令 `list` — 列出可用转换 |
| F-W002 | 子命令 `do` — 执行状态转换，选项 --comment/--resolution/--dry-run |
| F-W003 | 子命令 `path` — 多步路径转换，自动寻找转换路径，选项 --max-steps |
| F-W004 | `find_matching_transition()` 三级匹配：精确→规范化→子串 |

### jira-comment.py

| ID | 事实 |
|---|---|
| F-W005 | 子命令 `add` — 添加评论，支持 "-" 从 stdin 读取（上限256KB） |
| F-W006 | 子命令 `edit` — 编辑评论 |
| F-W007 | 子命令 `delete` — 删除评论（无确认提示） |
| F-W008 | 子命令 `list` — 列出评论（最新在前），--limit 0 表示全部 |
| F-W009 | 自动运行 wiki markup 检查和 mention 验证 |

### jira-create.py

| ID | 事实 |
|---|---|
| F-W010 | 子命令 `issue` — 创建工单，选项 --type/--description/--priority/--labels/--assignee/--parent/--components/--fields-json |
| F-W011 | 子命令 `project` — 创建项目（从共享模板） |
| F-W012 | 支持子任务创建（--parent 自动解析子任务类型） |

### jira-board.py / jira-sprint.py

| ID | 事实 |
|---|---|
| F-W013 | jira-board: list（列出看板）、issues（获取看板问题） |
| F-W014 | jira-sprint: list（列出冲刺）、issues（获取冲刺问题）、current（获取当前冲刺） |
| F-W015 | 使用 Agile API（rest/agile/1.0/） |

### jira-version.py（12个子命令）

| ID | 事实 |
|---|---|
| F-W016 | list/get/create/update/release/unrelease/archive/unarchive/move/merge/delete |
| F-W017 | 完整的版本生命周期管理 |
| F-W018 | merge 支持合并版本，delete 支持迁移 fix/affected 工单 |

### jira-move.py

| ID | 事实 |
|---|---|
| F-W019 | 子命令 `issue` — 同项目内更改工单类型 |
| F-W020 | 故意拒绝跨项目移动 |

### tempo-account.py

| ID | 事实 |
|---|---|
| F-W021 | 子组 `customer` — Tempo 客户管理 |
| F-W022 | 子组 `account` — Tempo 账户管理（create/link） |
| F-W023 | 使用 Tempo Timesheets API（rest/tempo-accounts/1/） |

## 六、工具脚本事实（utility/）

| ID | 事实 |
|---|---|
| F-U001 | jira-fields: search/list/types — 查找和列出字段 |
| F-U002 | jira-user: me/get/search — 用户信息查询 |
| F-U003 | jira-link: create/list/list-types/delete/bulk-create/bulk-delete/invert — 工单链接 |
| F-U004 | jira-watchers: list/add/remove — 关注者管理 |
| F-U005 | jira-weblink: add/list/update/delete — 远程链接管理 |
| F-U006 | jira-qa-gather: 单命令，一次性获取QA审查所需全部上下文 |
| F-U007 | jira-worklog-query: 跨 cut 工时查询，支持 Jira 和 Tempo 双后端 |

## 七、jira-syntax 技能事实

### Wiki 标记语法

| ID | 事实 |
|---|---|
| F-S001 | 粗体：`*text*`；斜体：`_text_`；等宽：`{{text}}` |
| F-S002 | 标题：`h1.` 至 `h6.`，句点后必须有空格 |
| F-S003 | 无序列表：`*`；有序列表：`#`；嵌套追加符号 |
| F-S004 | 链接：`[label|url]`、`[KEY-123]`、`[~username]` |
| F-S005 | 代码块：`{code:language}...{code}`；无高亮：`{noformat}...{noformat}` |
| F-S006 | 表格：表头 `||Header||`，单元格 `|Cell|` |
| F-S007 | 面板：`{panel:title=X|bgColor=#HEX}...{panel}` |
| F-S008 | 颜色：`{color:red}text{color}` |
| F-S009 | 支持的语言固定列表（不含 typescript/rust/kotlin 等） |
| F-S010 | CLI 标志 `--foo` 中的连字符会触发删除线，需转义为 `\-\-foo` |

### 验证脚本

| ID | 事实 |
|---|---|
| F-S011 | validate-jira-syntax.sh 检查成对宏平衡、Markdown 泄漏、不支持语言等 |
| F-S012 | 退出码：0=通过（可能有警告），1=有错误 |
| F-S013 | 验证应作为独立步骤运行，不得与发布命令链式连接 |

### 模板

| ID | 事实 |
|---|---|
| F-S014 | bug-report-template.md：环境/重现步骤/预期实际行为/错误信息/技术备注 |
| F-S015 | feature-request-template.md：业务价值/用户故事/验收标准/需求分级/成功指标 |

## 八、通用CLI事实

| ID | 事实 |
|---|---|
| F-G001 | 所有命令组脚本共享5个全局选项：--json/--quiet/--env-file/--profile/--debug |
| F-G002 | 写操作支持 --dry-run 预览变更 |
| F-G003 | 所有脚本使用 LazyJiraClient 延迟初始化 |
| F-G004 | 脚本通过相同的 PYTHONPATH 引导模式加载 lib/ |
| F-G005 | --json 输出机器可读JSON，--quiet 最小输出，默认表格输出 |
