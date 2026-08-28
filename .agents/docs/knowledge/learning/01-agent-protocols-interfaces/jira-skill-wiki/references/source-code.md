---
type: Reference
title: "源码结构信源"
description: "jira-skill v3.29.0 源码目录结构、模块划分和版本信息登记"
tags: ["jira", "source-code", "architecture", "reference"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "file:///d:/AI/vendor/jira-skill/README.md"
    type: "source-code"
    trust: high
  - resource: "file:///d:/AI/vendor/jira-skill/pyproject.toml"
    type: "source-code"
    trust: high
  - resource: "file:///d:/AI/vendor/jira-skill/.claude-plugin/plugin.json"
    type: "source-code"
    trust: high
---

# 源码结构信源

本文件登记 jira-skill 源码的目录结构、版本和模块划分，作为概念文档的溯源依据。

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名称 | jira-skill |
| 版本 | 3.29.0 |
| 许可证 | MIT + CC-BY-SA-4.0 |
| Python 要求 | 3.10+ |
| CLI 框架 | Click >=8.1.0,<9 |
| 核心依赖 | atlassian-python-api >=3.41,<4 |
| 执行方式 | `uv run --script`（PEP 723 内联依赖） |
| MCP 依赖 | 无（零 MCP 开销） |

## 顶层目录结构

```text
jira-skill/
├── .claude-plugin/plugin.json    # Claude Code 插件清单
├── skills/
│   ├── jira-communication/       # API 操作技能
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── core/             # 6个核心原子操作脚本
│   │   │   ├── workflow/         # 8个工作流组合脚本
│   │   │   ├── utility/          # 7个辅助查询脚本
│   │   │   └── lib/              # 11个共享库文件
│   │   └── references/           # 17个参考文档
│   └── jira-syntax/              # 语法规范技能（纯静态）
│       ├── SKILL.md
│       ├── references/           # 2个参考文档
│       ├── templates/            # 2个模板文件
│       └── scripts/              # shell 验证脚本
├── tests/                        # 24个 test_*.py + conftest.py（共25个 Python 文件）
├── pyproject.toml                # 仅含 ruff/bandit 工具配置，无 [project] 表
└── README.md
```

## jira-communication 脚本清单

### core/（6个）

| 脚本 | 子命令 | 职责 |
|------|--------|------|
| `jira-issue.py` | get, update, delete, work, qa, qa-fail, act, time-in-status | 工单 CRUD 与意图动词 |
| `jira-search.py` | query | JQL 搜索 |
| `jira-worklog.py` | add, list, delete | 工时管理 |
| `jira-attachment.py` | download, download-all, add | 附件管理 |
| `jira-setup.py` | （单命令） | 交互式凭证配置向导 |
| `jira-validate.py` | （单命令） | 运行时环境与连接验证 |

### workflow/（8个）

| 脚本 | 子命令 | 职责 |
|------|--------|------|
| `jira-transition.py` | list, do, path | 状态转换（含多步路径寻路） |
| `jira-comment.py` | add, edit, delete, list | 评论管理 |
| `jira-create.py` | issue, project | 创建工单/项目 |
| `jira-board.py` | list, issues | 看板查询 |
| `jira-sprint.py` | list, issues, current | 冲刺查询 |
| `jira-version.py` | list, get, create, update, release, unrelease, archive, unarchive, move, merge, delete | 版本生命周期管理（12个子命令） |
| `jira-move.py` | issue | 同项目内更改工单类型 |
| `tempo-account.py` | customer, account | Tempo 客户/账户管理 |

### utility/（7个）

| 脚本 | 子命令 | 职责 |
|------|--------|------|
| `jira-fields` | search, list, types | 字段查找与列出 |
| `jira-user` | me, get, search | 用户信息查询 |
| `jira-link` | create, list, list-types, delete, bulk-create, bulk-delete, invert | 工单链接管理 |
| `jira-watchers` | list, add, remove | 关注者管理 |
| `jira-weblink` | add, list, update, delete | 远程链接管理 |
| `jira-qa-gather` | （单命令） | QA审查上下文一次性聚合 |
| `jira-worklog-query` | （单命令） | 跨 cut 工时查询（Jira/Tempo双后端） |

### lib/（11个共享库）

| 文件 | 核心内容 |
|------|----------|
| `client.py` | `LazyJiraClient`、`get_jira_client()`、Cloud/Server差异处理、重试配置 |
| `config.py` | 凭证加载、profile 管理、`is_cloud_url()`、状态集合常量 |
| `output.py` | `format_output()`、JSON/表格格式化、错误输出、ADF文本提取 |
| `users.py` | 用户搜索、@提及验证（`MENTION_PATTERN`） |
| `markup.py` | `lint_wiki_markup()` wiki标记检查 |
| `changelog.py` | 状态变更提取、停留时间计算、转换分类 |
| `errors.py` | `CaptchaError`、`AuthenticationError`、凭证脱敏 |
| `input.py` | `read_stdin_utf8()` 标准输入读取 |
| `jql.py` | `jql_escape()` JQL字符串转义 |
| `render.py` | 评论/描述渲染输出 |
| `__init__.py` | 包初始化 |

## jira-syntax 内容清单

- **references/**：2个参考文档（wiki markup 语法参考）
- **templates/**：`bug-report-template.md`、`feature-request-template.md`
- **scripts/validate-jira-syntax.sh**：shell 验证脚本（检查宏平衡、Markdown泄漏等）

## 版本锁定说明

`atlassian-python-api` 被故意锁定在 `>=3.41,<4`，因为 v4 虽然修复了 Cloud 相关问题但引入了 Jira Data Center 回归。项目主要目标为 Jira Server/DC 9.12。
