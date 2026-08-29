---
type: Concept
title: "术语表与资源"
description: "Jira 集成插件核心术语表与参考资料索引，包含 22 个核心术语的中文翻译与通俗解释，以及插件源码、官方语法与 JQL 参考等资源汇总。"
tags: ["jira", "glossary", "reference", "terminology", "resources"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
  - resource: "/references/official-docs.md"
    type: "official-docs"
    trust: high
---
# 第 9 章：术语表与资源

本章汇集 Jira 集成插件生态中的核心术语与参考资源，方便读者快速查阅概念定义，并提供延伸阅读指引。

## 9.1 术语表（Glossary）

### A

#### Agent Skills 开放标准（Agent Skills open standard）
**一句话解释**：一种将专业知识与工作流打包成可移植、版本控制文件夹的轻量级格式标准，最初由 Anthropic 开发，现已跨产品通用。

其核心是一个包含 `SKILL.md` 文件的文件夹，可额外捆绑脚本、参考资料与模板，支持在任意兼容该标准的智能体（Claude Code、Cursor、GitHub Copilot、Trae 等）中复用。

#### Atlassian
**一句话解释**：Jira 与 Confluence 等协作工具的开发公司。

### C

#### Claude Code
**一句话解释**：Anthropic 推出的命令行 AI 编程助手，可通过插件与技能扩展能力，是本插件的宿主环境。

#### CLI（Command-Line Interface）
**一句话解释**：命令行界面，用户通过键入命令与程序交互的方式。

### D

#### dry-run
**一句话解释**：只预览操作将要做出的变更、而不实际执行的运行模式。

本插件所有写操作均支持 `--dry-run`，用于在正式提交前核对将写入的内容。

### I

#### 意图动词（Intent verbs）
**一句话解释**：`jira-issue.py` 提供的 `work`/`qa`/`qa-fail`/`act` 四个子命令，用单次调用返回针对某个特定意图定制的上下文包。

### J

#### Jira
**一句话解释**：Atlassian 推出的项目与工单跟踪工具，用于软件研发中的缺陷跟踪、任务管理与敏捷开发。

#### Jira Cloud（Jira 云端）
**一句话解释**：由 Atlassian 托管的 Jira 部署形态，用户无需自行维护服务器。

#### Jira Server/Data Center（Jira 服务器/数据中心）
**一句话解释**：由组织自行托管、部署在自己基础设施上的 Jira 部署形态。

#### JQL（Jira Query Language）
**一句话解释**：Jira 用于检索工单的查询语言，通过字段、操作符与函数组合成查询条件。

#### Jira wiki 标记（Jira Wiki Markup）
**一句话解释**：Jira 用于格式化描述与评论的专属标记语法，与 Markdown 相似但语法不同（如加粗用 `*text*` 而非 `**text**`）。

### M

#### MCP（Model Context Protocol）
**一句话解释**：一种让 AI 智能体连接外部工具与数据源的标准协议；本插件刻意绕过它，改由脚本直连 Jira API 以降低开销。

#### Markdown
**一句话解释**：一种轻量级纯文本标记语言；注意它不能直接用于 Jira 内容，需转换为 Jira wiki 标记。

### P

#### PEP 723
**一句话解释**：Python 增强提案中定义"内联脚本元数据"的规范，允许在脚本文件头部以注释形式声明运行依赖。

### R

#### Resolution（解决结果）
**一句话解释**：Jira 中表示工单最终处置方式的字段（如 `Done`、`Won't do`、`Duplicate`），独立于工单的"状态"。

### S

#### Skill（技能）
**一句话解释**：Agent Skills 标准中的能力单元，即一个含 `SKILL.md` 的可复用文件夹，指导智能体完成特定任务。

#### SKILL.md
**一句话解释**：技能定义文件，包含元数据（至少 `name` 与 `description`）与指导智能体的指令。

#### Sprint（冲刺）
**一句话解释**：敏捷开发中一个固定时长的迭代周期，团队在周期内完成既定工作。

#### Status（状态）
**一句话解释**：Jira 中表示工单当前所处阶段的字段（如 `Open`、`In Progress`、`Done`）。

### T

#### Transition（流转）
**一句话解释**：Jira 中将工单从一个状态切换到另一个状态的操作。

### U

#### uv / uvx
**一句话解释**：快速 Python 包安装器与运行器，无需虚拟环境即可解析并运行含 PEP 723 声明的脚本。

### W

#### Worklog（工时日志）
**一句话解释**：Jira 中记录工单上花费工作时间的条目。

## 9.2 参考资源

### 插件源码与文档

- [jira-skill 仓库](https://github.com/netresearch/jira-skill) — 插件源码。
- [Agent Skills 开放标准](https://agentskills.io) — 技能标准官网。
- [skills.sh](https://skills.sh) — 技能安装命令行工具。

### Jira 官方语法与查询参考

- [官方 Jira Wiki Markup](https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all) — Jira wiki 标记语法。
- [JQL 操作符（Cloud）](https://support.atlassian.com/jira-software-cloud/docs/jql-operators/)
- [JQL 函数（Cloud）](https://support.atlassian.com/jira-software-cloud/docs/jql-functions/)
- [JQL 操作符（Server/DC）](https://confluence.atlassian.com/jirasoftwareserver/advanced-searching-operators-reference-939938753.html)

### 依赖库

- [atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) — 本插件用于访问 Jira REST API 的 Python 库。

## 9.3 学习路径建议

1. 先通读 [总览](/concepts/00-overview.md) 与 [架构设计](/concepts/01-architecture.md)，建立整体认知。
2. 按 [安装与配置](/concepts/02-installation.md) 完成环境准备，再用 [快速开始](/concepts/03-quickstart.md) 上手命令。
3. 深入 [jira-communication](/concepts/04-jira-communication.md) 与 [jira-syntax](/concepts/05-jira-syntax.md) 两大技能。
4. 掌握 [JQL](/concepts/06-jql.md) 后，结合 [最佳实践与反模式](/concepts/07-best-practices.md) 提升使用质量，遇到问题查阅 [故障排查](/concepts/08-troubleshooting.md)。