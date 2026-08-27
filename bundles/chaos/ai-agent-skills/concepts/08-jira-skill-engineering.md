---
type: Concept
title: Jira Skill 工程化实践
description: jira-skill v3.28.0 的双技能拆分、21脚本三层架构、PEP 723 内联依赖、LazyJiraClient 客户端、统一CLI契约与从MCP迁移的工程决策
tags: [agent-skills, jira, engineering, pep723, click, atlassian, plugin]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: jira-skill-source
    resource: "/references/jira-skill-source.md"
    title: jira-skill 源码
---

# Jira Skill 工程化实践

jira-skill（v3.28.0）是 AI Agent Skill 工程化的标杆项目。它由 Netresearch DTT GmbH 维护，将 Jira 完整集成拆分为两个专业化技能，通过 21 个 Python 脚本覆盖问题管理、工作流、敏捷、工作日志等全场景，并在 PEP 723 内联依赖、统一 CLI 契约、版本一致性门控等方面展示了成熟的工程实践。

## 双技能拆分：操作与知识分离

jira-skill 最核心的架构决策是将 Jira 集成为**两个独立技能**而非单体：

| 技能 | 定位 | allowed-tools | 脚本数 |
|------|------|--------------|--------|
| `jira-communication` | API 操作（CRUD、转换、评论、附件） | Bash(python:*), Bash(uv:*), Read, Write | 21 个 |
| `jira-syntax` | Wiki 标记语法、模板、验证 | 无（纯知识） | 1 个 Shell |

这种拆分的工程价值：
1. **上下文隔离**：语法参考不需要 Bash 执行权限，不会在纯写作任务中触发脚本加载
2. **独立分发**：发布时同时提供完整版和两个独立技能版，用户可按需安装
3. **关注点分离**：jira-syntax 的更新（语法表、模板）与 jira-communication 的更新（API 脚本）独立发版

## 21 脚本三层架构

jira-communication 的脚本按职责清晰地分为三层：

### Core（6 个，`scripts/core/`）

高频核心操作，每个脚本覆盖一个主要资源域：

| 脚本 | 子命令示例 | 职责 |
|------|-----------|------|
| `jira-issue.py` | get/update/delete/work/qa | 问题读取、更新、删除、分诊、QA |
| `jira-search.py` | — | JQL 搜索，含 ORDER BY 智能检测 |
| `jira-worklog.py` | — | 工作日志记录（使用频率最高，22.8%） |
| `jira-attachment.py` | — | 附件上传下载 |
| `jira-setup.py` | — | 配置初始化与认证 |
| `jira-validate.py` | — | 配置验证 |

### Workflow（8 个，`scripts/workflow/`）

状态流转和流程操作：

| 脚本 | 职责 |
|------|------|
| `jira-create.py` | 创建问题（支持多种 issue type） |
| `jira-transition.py` | 状态转换（含 `do` 子命令执行转换） |
| `jira-comment.py` | 评论增删改 |
| `jira-move.py` | 问题在项目间移动 |
| `jira-sprint.py` | Sprint 管理 |
| `jira-board.py` | 看板管理 |
| `jira-version.py` | 版本管理 |
| `tempo-account.py` | Tempo 账户管理 |

### Utility（7 个，`scripts/utility/`）

辅助查询和低频操作：

| 脚本 | 职责 |
|------|------|
| `jira-user.py` | 用户查询和经办人解析 |
| `jira-fields.py` | 字段元数据查询 |
| `jira-link.py` | 问题间链接 |
| `jira-weblink.py` | Web 远程链接 |
| `jira-worklog-query.py` | 工作日志查询（与 core 的记录分离） |
| `jira-watchers.py` | 观察者管理 |
| `jira-qa-gather.py` | QA 信息批量收集 |

### 共享库（`scripts/lib/`）

| 模块 | 核心导出 |
|------|---------|
| `client.py` | `LazyJiraClient`、`SessionExpiredError`、`resolve_assignee()`、`resolve_status()`、`is_account_id()`、`fetch_comments_paginated()` |
| `config.py` | `load_config()`、`validate_config()`、`get_auth_mode()`、`is_cloud_url()`、`normalize_netloc()`、`load_status_sets()` |
| `errors.py` | `CaptchaError`、`AuthenticationError` |
| `output.py` | `format_output()`、`compact_json()`、`success()`、`warning()`、`error()`、`extract_adf_text()` |
| `input.py` | `read_stdin_utf8()` |
| `users.py` | `check_mentions_cli()`、`person_label()` |
| `changelog.py` | `classify_transition()`、`compute_time_in_status()`、`extract_status_transitions()` |
| `jql.py` | JQL 处理工具 |
| `markup.py` | Wiki 标记处理 |

## PEP 723 内联依赖

每个核心脚本使用 PEP 723 标准声明内联依赖，这是现代 Python 脚本分发的关键模式：

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "atlassian-python-api>=3.41.0,<4",
#     "click>=8.1.0,<9",
# ]
# ///
"""Jira issue operations - get, update, and delete issue details."""
```

### 关键设计决策

1. **shebang 使用 `uv run --script`**：通过 uv 自动创建隔离环境执行，无需手动管理虚拟环境。
2. **依赖固定主版本**：`atlassian-python-api>=3.41.0,<4` 是有意为之——v4 有 Jira Cloud 变更和 DC 回归，项目主要目标是 Jira Server/DC 9.12。
3. **click 框架**：使用 click 而非 argparse，支持子命令、参数类型校验和自动帮助生成。
4. **PYTHONPATH 导入**：通过 `sys.path.insert(0, str(_lib_path.parent))` 导入共享 lib，而非将 lib 打包安装。

### PYTHONPATH 模式

```python
_script_dir = Path(__file__).parent
_lib_path = _script_dir.parent / "lib"
if _lib_path.exists():
    sys.path.insert(0, str(_lib_path.parent))

from lib.client import LazyJiraClient, resolve_assignee, resolve_status
from lib.config import load_status_sets
from lib.output import format_output, success, warning, error
```

这种方式使得脚本可以直接运行（通过 uv run），同时共享 lib/ 中的通用逻辑，无需安装包。

## LazyJiraClient 客户端

`lib/client.py` 中的 `LazyJiraClient` 是 API 交互的核心：

- **默认超时**：`JIRA_TIMEOUT = 30` 秒
- **重试策略**：使用 `HTTPAdapter` 和 `Retry` 配置请求重试
- **账户 ID 检测**：`is_account_id()` 支持两种 Jira Cloud 格式：
  - 新格式：带冒号（`557058:uuid`）
  - 旧格式：24 字符十六进制
- **经办人解析**：`resolve_assignee()` 智能处理多种输入：
  - `"me"` → 当前用户
  - Cloud 账户 ID → 直接使用
  - 用户名/邮箱 → 先精确匹配，再模糊搜索
  - Server/DC：先精确用户名查找，再 Cloud 感知的片段搜索
  - 多个模糊候选时回退到原始标识符让 Jira 显式拒绝（不猜测）

## 配置管理

`lib/config.py` 处理多环境配置：

### 认证方式

| 部署类型 | 环境变量 |
|---------|---------|
| Jira Cloud | `JIRA_URL` + `JIRA_USERNAME` + `JIRA_API_TOKEN` |
| Jira Server/DC | `JIRA_URL` + `JIRA_PERSONAL_TOKEN` |

### 配置加载优先级

1. 显式 `env_file` 参数
2. `~/.env.jira` 文件
3. 环境变量回退

配置文件路径：`~/.jira/profiles.json`（支持多 profile）。

### URL 规范化

`normalize_netloc()` 将 URL 网络位置：
- 小写化
- 剥离默认端口（HTTPS 443、HTTP 80）

这确保了同一 Jira 实例的不同 URL 写法被识别为同一配置。

### Windows 兼容

`_ensure_utf8_streams()` 在 Windows 平台确保 UTF-8 输出，避免编码问题。

## 统一 CLI 契约

所有 21 个脚本遵循统一的命令行接口规范：

| 参数 | 说明 |
|------|------|
| `--help` | 自动生成的帮助信息 |
| `--json` | JSON 格式输出（机器可读） |
| `--quiet` | 静默模式（仅输出关键信息/错误） |
| `--debug` | 调试输出（详细日志） |
| `--dry-run` | 破坏性操作的预览模式（不实际执行） |

三种输出格式的设计使得：
- AI 可通过 `--json` 获取结构化数据
- 人类用户可使用默认表格输出
- 脚本链式调用可通过 `--quiet` 减少噪声

## 意图映射

SKILL.md 不要求 AI 浏览全部 21 个脚本，而是提供**意图到脚本的映射表**：

| 用户意图 | 脚本调用 |
|---------|---------|
| 分诊/处理任务 | `jira-issue.py work` |
| QA 审查 | `jira-issue.py qa` |
| 查询字段 | `jira-issue.py get` |
| 状态变更 | `jira-issue.py act` → `jira-transition.py do` |
| 创建问题 | `jira-create.py` |
| 搜索问题 | `jira-search.py` |
| 记录工时 | `jira-worklog.py` |

自动触发条件：Jira URL 或 issue key（如 `PROJ-123`），以及任何 Jira 意图（"create/find a ticket"、"pick a project"）。

## 从 MCP 迁移的数据驱动决策

PRD.md 记录了从 mcp-atlassian Docker MCP 服务器迁移到轻量脚本架构的决策过程：

### 原 MCP 方案的问题

1. **Token 消耗**：~25 个工具加载消耗 8,000-12,000 Token/会话
2. **启动延迟**：Docker 容器启动
3. **工具冗余**：Confluence 工具未使用
4. **凭证管理**：需挂载到容器

### 使用分析

126 个调试会话的数据显示了极端的二八分布：

| 工具 | 使用占比 |
|------|---------|
| jira_add_worklog | 22.8% |
| jira_get_issue | 18.6% |
| jira_search | 10.7% |
| jira_update_issue | 8.1% |
| jira_create_issue | 7.3% |
| **合计** | **67.5%** |

5 个工具占近 70% 使用量，其余 20 个工具仅占 30%。全量 Schema 注入的 Token 浪费显著。

### 迁移后的架构

- `uv run --script` 直接执行，无 Docker 启动延迟
- 按需加载脚本（AI 根据意图选择），Token 消耗与实际使用相关
- PEP 723 依赖自动管理，无容器凭证挂载

## jira-syntax 技能

jira-syntax 是纯知识技能，无 allowed-tools：

### 快速语法参考

| Jira 语法 | Markdown 等价 |
|-----------|--------------|
| `h2. 标题` | `## 标题` |
| `*粗体*` | `**粗体**` |
| `_斜体_` | `*斜体*` |
| `{{代码}}` | `` `代码` `` |
| `{code:java}` | ` ```java ` |
| `[text\|url]` | `[text](url)` |
| `[~username]` | @用户提及 |

### 模板与验证

- Bug Report 和 Feature Request 两个模板
- `validate-jira-syntax.sh` 独立验证脚本（不与发布命令链式调用）
- 常见错误对照表列出 8 种错误写法与正确写法

## 工程化保障

### 版本一致性

plugin.json、skills/jira-communication/SKILL.md、skills/jira-syntax/SKILL.md 三者的 `version`/`metadata.version` 必须匹配，由 pre-commit 和 CI 强制执行。

### Pre-commit 门控

- 脚本帮助验证（`--help` 可正常执行）
- pytest 测试套件
- `ruff check`（代码规范）
- `ruff format --check`（格式化检查，独立门控）
- markdownlint（文档规范）

### 发布工程

- 标签推送自动发布三个包族（完整版 + 两个独立技能版）
- 包含 SHA256SUMS 校验和
- SLSA 证明（供应链安全）
- PR 保持小体量（~300 净 LOC）
- Conventional Commits

## 相关概念

- [插件架构（plugin.json/hooks/commands）](/concepts/05-plugin-architecture.md)
- [Skill 脚本工具模式](/concepts/10-skill-tooling-scripts.md)
- [MCP 协议与工具集成](/concepts/04-mcp-protocol.md)
