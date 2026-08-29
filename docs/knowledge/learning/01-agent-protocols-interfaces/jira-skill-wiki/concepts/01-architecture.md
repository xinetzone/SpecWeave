---
type: Concept
title: "架构设计：双技能插件"
description: "Jira 集成插件架构设计详解，涵盖系统总览、目录结构、双技能组件划分、三层脚本体系、数据流与四项关键设计决策。"
tags: ["jira", "architecture", "plugin", "skill", "directory-structure", "data-flow"]
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
  - resource: "/references/official-docs.md"
    type: "official-docs"
    trust: high
---
# 第 1 章：架构设计

本章剖析 jira-skill 插件的整体架构，帮助读者理解"一个插件、两个技能、三层脚本"的组织方式及其背后的设计决策。

## 1.1 系统总览

jira-skill 是一个 **Claude Code 插件**，内部含两个技能：

- **`jira-communication`**：负责与 Jira 的 API 交互，通过组织为三层的 Python CLI 脚本来执行操作。
- **`jira-syntax`**：提供 Jira wiki 标记语法的参考资料与模板，按需加载，负责"内容怎么写才对"。

两个技能各有独立的 `SKILL.md`（技能定义文件），由 Claude Code 根据上下文自动发现并激活。当用户提示中涉及 Jira URL 或工单号（如 `PROJ-123`）时，`jira-communication` 技能被激活；当需要撰写或格式化 Jira 内容时，`jira-syntax` 技能被激活。

## 1.2 目录结构

插件的核心目录结构如下（省略 CI、评估与测试等工程化目录）：

```
jira-skill/
├── .claude-plugin/
│   └── plugin.json            # 插件元数据（版本、技能声明、入口）
├── plugin.json                # 插件元数据（根级副本，两者版本需一致）
├── README.md                  # 插件说明
├── PRD.md                     # 迁移到脚本化架构的产品需求文档
├── MIGRATION.md               # 版本迁移指南
├── docs/
│   └── ARCHITECTURE.md        # 架构说明文档
├── skills/
│   ├── jira-communication/    # API 操作技能
│   │   ├── SKILL.md           # 技能定义（触发条件、用法）
│   │   ├── AGENTS.md          # 脚本开发指南
│   │   ├── references/        # 17 份按主题拆分的参考文档（JQL、工时、附件等）
│   │   └── scripts/
│   │       ├── core/          # 核心操作（工单、搜索、工时等）
│   │       ├── workflow/      # 工作流操作（创建、流转、评论、看板等）
│   │       ├── utility/       # 工具操作（字段、用户、链接等）
│   │       └── lib/           # 共享库（认证、输出、异常等）
│   └── jira-syntax/           # 语法技能
│       ├── SKILL.md           # 技能定义
│       ├── references/        # 语法快速参考、跨项目引用规范
│       ├── scripts/           # 语法校验脚本
│       └── templates/         # Bug 报告、特性请求模板
```

## 1.3 组件说明

### 1.3.1 jira-communication 技能

该技能的核心是组织为**三层**的 Python CLI 脚本：

| 层级 | 目录 | 职责 | 代表脚本 |
|------|------|------|---------|
| **Core（核心层）** | `scripts/core/` | 基础操作：工单读写、JQL 搜索、工时、附件、配置初始化与校验 | `jira-issue.py`、`jira-search.py`、`jira-worklog.py` |
| **Workflow（工作流层）** | `scripts/workflow/` | 高阶操作：创建工单、状态流转、评论、冲刺、看板、版本 | `jira-create.py`、`jira-transition.py`、`jira-sprint.py` |
| **Utility（工具层）** | `scripts/utility/` | 辅助查询：字段、用户、链接、Watcher、QA 审计 | `jira-fields.py`、`jira-user.py`、`jira-link.py` |

所有脚本共享一个 **`lib/` 共享库**，统一处理认证（`config.py`、`client.py`）、输出格式化（`output.py`）、异常（`errors.py`）、JQL 构造（`jql.py`）等横切关注点。脚本之间通过 `uv run` 运行，依赖声明采用 **PEP 723 内联脚本元数据**——即在脚本头部以注释形式声明依赖，`uv` 读取后自动解析环境，无需虚拟环境。

### 1.3.2 jira-syntax 技能

该技能不发起 API 调用，纯粹提供"内容规范"能力：

- **`references/`**：Jira wiki 标记语法的完整参考，以及 GitLab 跨项目引用的格式约定。
- **`templates/`**：两份模板——Bug 报告模板与特性请求模板。
- **`scripts/validate-jira-syntax.sh`**：提交前的语法校验脚本，用于拦截 Markdown 语法误用。

### 1.3.3 插件元数据

`.claude-plugin/plugin.json` 与根级 `plugin.json` 共同声明插件的名称、版本、技能清单与入口，供 Claude Code 发现。两者以及两个 `SKILL.md` 中的 `metadata.version` 必须保持一致（由 pre-commit 与 CI 强制校验版本奇偶一致性）。

## 1.4 数据流

一次典型调用的完整数据流如下：

```
用户提示（如"搜索 Jira 中未关闭的 Bug"）
  → Claude Code 激活 jira-communication 技能
  → 技能指示智能体运行对应 Python 脚本
  → 脚本从 ~/.env.jira 读取凭证
  → 脚本调用 Jira REST API
  → 结构化输出返回给智能体
```

关键点在于：**Jira 凭证不进入智能体上下文，而是由脚本在本地读取**，这既保护了凭证安全，也保持了上下文的简洁。

## 1.5 关键设计决策

| 决策 | 内容 | 理由 |
|------|------|------|
| 零 MCP 开销 | 脚本经 Bash 直接调用，不加载工具描述 | 避免上下文窗口膨胀 |
| uv 依赖管理 | 用 `uv`/`uvx` 解析 PEP 723 依赖 | 快速、可复现，无需 Docker |
| 双部署兼容 | 通过环境变量区分 Server/DC 与 Cloud | 同一套脚本覆盖两种部署形态 |
| 单依赖版本钉扎 | `atlassian-python-api` 钉扎在 `>=3.41,<4` | 主目标为 Jira Server/DC 9.12，v4 在 DC 上有回归风险 |

关于 `atlassian-python-api` 的版本钉扎值得特别说明：v4 为 Jira Cloud 新增了 `search/jql` 端点（因 Atlassian 在 Cloud 上移除了 `/rest/api/3/search`），但在 DC 上到 4.0.5 前存在回归。由于该插件的主目标是 Jira Server/DC，故选择钉扎 v3，仅在具备 Cloud 测试租户后才考虑升级。

## 相关概念

- [教程总览](/concepts/00-overview.md)：返回教程总览
- [安装与配置](/concepts/02-installation.md)：环境搭建指南
- [jira-communication 技能](/concepts/04-jira-communication.md)：API操作技能详解
- [源码结构信源](/references/source-code.md)：源码目录结构参考