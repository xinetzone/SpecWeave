---
type: Concept
title: "jira-communication 技能详解"
description: "jira-communication 技能完整详解，涵盖自动触发条件、三层脚本体系、意图动词机制（work/qa/qa-fail/act）、通用选项与认证方式。"
tags: ["jira", "jira-communication", "cli", "intent-verbs", "scripts", "authentication"]
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
# 第 4 章：jira-communication 技能详解

本章深入讲解负责 API 交互的 `jira-communication` 技能，重点介绍其"意图动词"机制（用单个命令替换多次调用的设计）。

## 4.1 技能定位与自动触发

`jira-communication` 技能处理所有与 Jira 工单、冲刺、看板、链接、字段、工时、附件、用户相关的操作。它在以下场景自动触发：

- 出现 Jira URL 或工单号（如 `PROJ-123`）。
- 出现 Jira 意图但**没有**工单号（如"创建一个工单"、"找一下某个工单"）。
- MCP Atlassian 工具不可用或对 Jira Server/DC 失效时。

关键原则：**该技能本身就是 Jira 通道**，即使没有工单号也能开工——`jira-search.py` 用 JQL 找已有工单、`jira-create.py` 新建工单。

## 4.2 三层脚本体系

脚本位于 `${CLAUDE_SKILL_DIR}/scripts/{core,workflow,utility}/`，三层分工如下：

**Core（核心层）**：

| 脚本 | 命令 | 用途 |
|------|------|------|
| `jira-setup.py` | （默认） | 交互式凭证配置 |
| `jira-validate.py` | （默认） | 校验环境配置 |
| `jira-issue.py` | `get`、`update` | 获取与更新工单 |
| `jira-search.py` | `query` | JQL 搜索 |
| `jira-worklog.py` | `add`、`list` | 工时记录 |
| `jira-attachment.py` | `download` | 下载附件 |

**Workflow（工作流层）**：

| 脚本 | 命令 | 用途 |
|------|------|------|
| `jira-create.py` | `issue` | 创建工单 |
| `jira-transition.py` | `list`、`do`、`path` | 状态流转 |
| `jira-comment.py` | `add`、`list` | 评论 |
| `jira-sprint.py` | `list`、`issues`、`current` | 冲刺操作 |
| `jira-board.py` | `list`、`issues` | 看板操作 |
| `jira-move.py`、`jira-version.py`、`tempo-account.py` | — | 移动、版本、Tempo 账户 |

**Utility（工具层）**：

| 脚本 | 命令 | 用途 |
|------|------|------|
| `jira-fields.py` | `search`、`list` | 查找字段 ID |
| `jira-user.py` | `me`、`get` | 用户信息 |
| `jira-link.py` | `create`、`list-types` | 工单链接 |
| `jira-weblink.py`、`jira-watchers.py`、`jira-worklog-query.py`、`jira-qa-gather.py` | — | 网页链接、Watcher、工时查询、QA 审计 |

## 4.3 意图动词机制

`jira-issue.py` 提供四个**意图动词**，用单次调用返回针对某个意图定制的上下文包，替代传统的"`get` + 多次 `comment list`"组合：

```bash
jira-issue.py work    KEY   # description + 全部评论 + 附件 + 链接
jira-issue.py qa      KEY   # description + 转交包（INTO_QA 流转前后的评论）
jira-issue.py qa-fail KEY   # description + 评审驳回 + 实现者的范围上下文
jira-issue.py act     KEY   # 元信息 + 可用流转
```

这四个动词分别对应"处理工单 / 开始 QA 评审 / QA 失败跟进 / 变更状态"四种常见意图，经验证可将 3–6 次独立调用合并为 1 次。

### 4.3.1 intent 到工具的映射

出现 Jira 工单号时，按**意图**选择工具，每次一个调用：

| 意图 | 工具 |
|------|------|
| 分诊 / 处理工单 | `jira-issue.py work KEY` |
| 开始 QA 评审 | `jira-issue.py qa KEY` |
| QA 失败跟进 | `jira-issue.py qa-fail KEY` |
| 仅查字段 | `jira-issue.py get KEY --fields ...` |
| 变更状态 | `jira-issue.py act KEY` → `jira-transition.py do` |
| 审计 / 兄弟工单发现 | `jira-qa-gather.py KEY` |

> **反模式**：用 `get` + `comment list` 组合来做分诊。应直接使用匹配意图的动词。

### 4.3.2 QA 转交启发式（`qa` 动词）

`qa` 动词寻找最近的 INTO_QA 流转，返回：转交作者在流转前后窗口内的评论（覆盖"先评论后点流转"或"先流转后补评论"两种情况），以及转交后任意作者的 QA 讨论。经验样本（10 个工单、41 次流转）显示 80% 的转交评论发生在点击流转**之前**。

### 4.3.3 状态集合分类

流转通过三组可配置的状态集合进行分类：

| 集合 | 默认值 | 含义 |
|------|--------|------|
| `qa_status_names` | `QA, Review, In Review, Code Review, ...` | 进入评审的状态 |
| `working_status_names` | `In Progress, Open, Reopened, To Do, ...` | 驳回后回退的状态 |
| `resolved_status_names` | `Closed, Resolved, Done, Won't Fix, Cancelled` | 终态 |

据此将流转分类为：`into_qa`（转交）、`reject`（驳回）、`forward`（多阶段推进，如 QA→QA2）、`resolved`（完成）、`out`、`other`。多阶段识别的能力使多阶段 QA 工作流（Review → UAT → Acceptance → Closed）与单阶段工作流无需改代码即可统一处理。

## 4.4 通用选项

所有脚本统一支持以下全局选项（须置于子命令之前）：

| 选项 | 说明 |
|------|------|
| `--json` | 以 JSON 格式输出 |
| `--quiet` / `-q` | 最小化输出 |
| `--env-file PATH` | 指定自定义环境文件 |
| `--debug` | 显示详细错误 |
| `--help` | 显示命令帮助 |

写操作额外支持：

| 选项 | 说明 |
|------|------|
| `--dry-run` | 预览变更但不实际执行 |

例如，全局标志放在子命令之前：

```bash
jira-issue.py --json get PROJ-123
```

## 4.5 执行风格

脚本直接运行，以 `✓` / `✗` 报告结果。破坏性操作须配合 `--dry-run` 预览。认证相关问题交给 `jira-setup.py`。

## 4.6 认证

- **Cloud**：`JIRA_URL` + `JIRA_USERNAME` + `JIRA_API_TOKEN`。
- **Server/DC**：`JIRA_URL` + `JIRA_PERSONAL_TOKEN`。

配置载体为 `~/.env.jira` 或 `~/.jira/profiles.json`（详见第 2 章）。

## 4.7 无编辑化原则（No editorializing）

在工单内容与评论中，只陈述**发生了什么**，不评价"做得多好"。脚本与模板均遵循此原则，避免 AI 在工单中写入自我褒扬式措辞。

下一章介绍负责内容规范的 `jira-syntax` 技能。

## 相关概念

- [架构设计](/concepts/01-architecture.md)：理解三层脚本体系
- [jira-syntax 技能](/concepts/05-jira-syntax.md)：内容格式规范
- [最佳实践](/concepts/07-best-practices.md)：意图动词使用建议
- [CLI API 参考](/references/api-reference.md)：完整命令参考