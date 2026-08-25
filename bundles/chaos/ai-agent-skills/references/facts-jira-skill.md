# jira-skill 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\tests\jira-skill\
> 采集日期：2026-08-23

## 项目概述

- F-001: 项目名称为"Jira Integration Plugin for Claude Code"，通过两个专业化技能提供全面的 Jira 集成 — 源码：`README.md:1,7`
- F-002: 两个技能分别为 jira-communication（通过 Python CLI 脚本进行 API 操作）和 jira-syntax（Wiki 标记语法、模板、验证） — 源码：`README.md:11-14`
- F-003: 遵循 Agent Skills 开放标准（agentskills.io），支持 Claude Code、Cursor、GitHub Copilot 等 — 源码：`README.md:18-28`
- F-004: 核心特性：零 MCP 开销（通过 Bash 调用脚本）、快速执行（无 Docker 容器启动）、完整 API 覆盖、支持 Jira Server/DC 和 Cloud — 源码：`README.md:31-36`
- F-005: 支持 Python 3.10、3.11、3.12、3.13 — 源码：`README.md:5`

## 插件结构（plugin.json）

- F-006: plugin.json 遵循 https://agent-plugins.org/schemas/1.0.0/plugin.schema.json — 源码：`plugin.json:2`
- F-007: 插件名称为 jira，版本 3.28.0 — 源码：`plugin.json:3-4`
- F-008: 描述为"Comprehensive Jira integration with auto-detection of issue keys" — 源码：`plugin.json:5`
- F-009: 作者为 Netresearch DTT GmbH，仓库为 https://github.com/netresearch/jira-skill — 源码：`plugin.json:6-9`
- F-010: 许可证为 (MIT AND CC-BY-SA-4.0) — 源码：`plugin.json:10`
- F-011: 关键词包括 jira、atlassian、issue-tracking、project-management、wiki-markup、syntax-validation、templates — 源码：`plugin.json:12-19`

## jira-communication SKILL.md

- F-012: SKILL.md frontmatter 包含 name、description、license、compatibility、metadata（author/version/repository）、allowed-tools — 源码：`skills/jira-communication/SKILL.md:1-11`
- F-013: 技能名称为 jira-communication，版本 3.28.0 — 源码：`skills/jira-communication/SKILL.md:2,7`
- F-014: allowed-tools 声明 Bash(python:*)、Bash(uv:*)、Read、Write — 源码：`skills/jira-communication/SKILL.md:10`
- F-015: 自动触发条件：Jira URL 或 issue key（PROJ-123），以及任何 Jira 意图（"create/find a ticket"、"pick a project"） — 源码：`skills/jira-communication/SKILL.md:3`
- F-016: 脚本按意图映射：triage/work→jira-issue.py work、QA review→jira-issue.py qa、字段查询→jira-issue.py get、状态变更→jira-issue.py act→jira-transition.py do — 源码：`skills/jira-communication/SKILL.md:21-29`
- F-017: 脚本组织在 scripts/{core,workflow,utility}/ 三个目录下 — 源码：`skills/jira-communication/SKILL.md:34`
- F-018: Core 脚本 6 个：jira-issue.py、jira-search.py、jira-worklog.py、jira-attachment.py、jira-setup.py、jira-validate.py — 源码：`skills/jira-communication/SKILL.md:36`
- F-019: Workflow 脚本 8 个：jira-create.py、jira-transition.py、jira-comment.py、jira-move.py、jira-sprint.py、jira-board.py、jira-version.py、tempo-account.py — 源码：`skills/jira-communication/SKILL.md:37`
- F-020: Utility 脚本 7 个：jira-user.py、jira-fields.py、jira-link.py、jira-weblink.py、jira-worklog-query.py、jira-watchers.py、jira-qa-gather.py — 源码：`skills/jira-communication/SKILL.md:38`
- F-021: 所有脚本支持 --help、--json、--quiet、--debug 参数，破坏性操作支持 --dry-run — 源码：`skills/jira-communication/SKILL.md:15,42`
- F-022: References 目录引用了 16 个参考文档，涵盖 JQL、配置、故障排除、问题编辑、创建、评论、工作日志、附件、链接、敏捷、无编辑化、字段用户、观察者、版本、QA 收集、意图动词 — 源码：`skills/jira-communication/SKILL.md:68-85`
- F-023: 认证方式：Cloud 使用 JIRA_URL + JIRA_USERNAME + JIRA_API_TOKEN；Server/DC 使用 JIRA_URL + JIRA_PERSONAL_TOKEN — 源码：`skills/jira-communication/SKILL.md:87-89`

## jira-syntax SKILL.md

- F-024: SKILL.md frontmatter 包含 name、description、license、metadata（author/version/repository），无 allowed-tools — 源码：`skills/jira-syntax/SKILL.md:1-9`
- F-025: 技能名称为 jira-syntax，版本 3.28.0 — 源码：`skills/jira-syntax/SKILL.md:2,7`
- F-026: 快速语法参考表对比了 Jira 语法与 Markdown：h2. 标题、*粗体*、_斜体_、{{代码}}、{code:java} 代码块、[text|url] 链接、[~username] 用户提及 — 源码：`skills/jira-syntax/SKILL.md:17-30`
- F-027: 提供两种模板：Bug Report（templates/bug-report-template.md）和 Feature Request（templates/feature-request-template.md） — 源码：`skills/jira-syntax/SKILL.md:35-43`
- F-028: 语法验证通过 validate-jira-syntax.sh 脚本执行，作为独立步骤运行，不与发布命令链式调用 — 源码：`skills/jira-syntax/SKILL.md:47-53`
- F-029: 验证清单包括标题格式、粗体、代码块、列表、链接、表格、颜色、面板 — 源码：`skills/jira-syntax/SKILL.md:55-63`
- F-030: 常见错误对照表列出 8 种错误写法与正确写法，包括 (/) 在开放项上的误用和 ( ) 非宏问题 — 源码：`skills/jira-syntax/SKILL.md:67-77`

## 脚本架构（PEP 723）

- F-031: 每个核心脚本使用 PEP 723 内联依赖声明，shebang 为 `#!/usr/bin/env -S uv run --script` — 源码：`skills/jira-communication/scripts/core/jira-issue.py:1-7`
- F-032: 依赖固定为 atlassian-python-api>=3.41.0,<4 和 click>=8.1.0,<9 — 源码：`skills/jira-communication/scripts/core/jira-issue.py:4-6`
- F-033: atlassian-python-api 固定在 >=3.41,<4 是有意为之，v4 有 Jira Cloud 变更和 DC 回归，主要目标是 Jira Server/DC 9.12 — 源码：`AGENTS.md:20`
- F-034: 脚本通过 PYTHONPATH 方式导入共享库（lib/ 目录），而非包安装 — 源码：`skills/jira-communication/scripts/core/jira-issue.py:19-22`
- F-035: jira-issue.py 使用 click 框架定义 CLI，导入了 lib.changelog、lib.client、lib.config、lib.input、lib.output、lib.users 等模块 — 源码：`skills/jira-communication/scripts/core/jira-issue.py:24-38`
- F-036: jira-search.py 定义了 JQL ORDER BY 检测逻辑（_has_top_level_order_by），能正确忽略引号内的 'order by' 字符串 — 源码：`skills/jira-communication/scripts/core/jira-search.py:51-59`

## lib/client.py 客户端库

- F-037: client.py 提供 Jira 客户端初始化，默认超时 JIRA_TIMEOUT = 30 秒 — 源码：`skills/jira-communication/scripts/lib/client.py:15-16`
- F-038: is_account_id() 检测 Jira Cloud 账户 ID，支持两种格式：带冒号的新格式（557058:uuid）和 24 字符十六进制旧格式 — 源码：`skills/jira-communication/scripts/lib/client.py:26-37`
- F-039: resolve_assignee() 将经办人标识符解析为 API 就绪字典，处理 "me"、Cloud 账户 ID、用户名/邮箱的精确匹配和模糊搜索 — 源码：`skills/jira-communication/scripts/lib/client.py:40-80`
- F-040: 对 Server/DC 先尝试精确用户名查找，再进行 Cloud 感知的片段搜索；多个模糊候选时回退到原始标识符让 Jira 显式拒绝 — 源码：`skills/jira-communication/scripts/lib/client.py:60-75`
- F-041: 使用 HTTPAdapter 和 Retry 配置请求重试策略 — 源码：`skills/jira-communication/scripts/lib/client.py:8-9`
- F-042: 从 .config 导入 get_auth_mode、is_cloud_url、load_config、validate_config，从 .errors 导入 AuthenticationError、CaptchaError — 源码：`skills/jira-communication/scripts/lib/client.py:11-12`

## lib/config.py 配置库

- F-043: config.py 处理环境配置加载，默认环境文件为 ~/.env.jira，配置文件为 ~/.jira/profiles.json — 源码：`skills/jira-communication/scripts/lib/config.py:32-33`
- F-044: Cloud 认证变量为 JIRA_USERNAME + JIRA_API_TOKEN，Server/DC 为 JIRA_PERSONAL_TOKEN，URL 变量为 JIRA_URL — 源码：`skills/jira-communication/scripts/lib/config.py:37-39`
- F-045: 配置加载优先级：显式 env_file 参数 → ~/.env.jira → 环境变量回退 — 源码：`skills/jira-communication/scripts/lib/config.py:44-51`
- F-046: normalize_netloc() 将 URL 网络位置小写化并剥离默认端口（HTTPS 443、HTTP 80） — 源码：`skills/jira-communication/scripts/lib/config.py:20-29`
- F-047: Windows 平台通过 _ensure_utf8_streams() 确保 UTF-8 输出 — 源码：`skills/jira-communication/scripts/lib/config.py:14-17`

## AGENTS.md 规范

- F-048: 根 AGENTS.md 规定最近的 AGENTS.md 优先，根目录仅保存全局默认值 — 源码：`AGENTS.md:5`
- F-049: 全局规则包括：PR 保持小体量（~300 净 LOC）、Conventional Commits、版本真相来源为 .claude-plugin/plugin.json — 源码：`AGENTS.md:13-15`
- F-050: 版本一致性要求：plugin.json 和两个 skills/*/SKILL.md 的 metadata.version 必须匹配，由 pre-commit 和 CI 强制执行 — 源码：`AGENTS.md:15,62`
- F-051: Pre-commit 检查包括：脚本帮助验证、pytest 测试、ruff check 和 format --check（两个独立门控）、markdownlint — 源码：`AGENTS.md:24-39`
- F-052: 发布流程自动化，标签推送时发布三个包族（完整版 + 两个独立技能版），包含 SHA256SUMS 和 SLSA 证明 — 源码：`AGENTS.md:50-56`
- F-053: jira-communication 的 AGENTS.md 规定脚本结构：argparse 子命令、共享 lib 导入、PEP 723 头、PYTHONPATH 操作 — 源码：`skills/jira-communication/AGENTS.md:27-31`
- F-054: 每个脚本必须支持三种输出格式（--json、--quiet、默认表格），写操作必须有 --dry-run — 源码：`skills/jira-communication/AGENTS.md:33-35`

## PRD.md 迁移背景

- F-055: PRD 记录了从 mcp-atlassian Docker MCP 服务器迁移到基于 uv run + atlassian-python-api + click 的轻量脚本架构 — 源码：`PRD.md:10-13`
- F-056: 原 MCP 方案问题：~25 个工具加载消耗 8,000-12,000 Token/会话、Docker 容器启动延迟、Confluence 工具未使用、凭证需挂载到容器 — 源码：`PRD.md:38-45`
- F-057: 126 个调试会话的使用分析显示 5 个工具占 80% 使用量：jira_add_worklog（22.8%）、jira_get_issue（18.6%）、jira_search（10.7%）、jira_update_issue（8.1%）、jira_create_issue（7.3%） — 源码：`PRD.md:48-58`
