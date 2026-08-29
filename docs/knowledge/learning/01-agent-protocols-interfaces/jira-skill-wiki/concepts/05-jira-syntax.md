---
type: Concept
title: "jira-syntax 技能详解"
description: "jira-syntax 技能完整详解，涵盖 Jira wiki 标记与 Markdown 的语法对照、Bug/特性模板、提交前语法校验清单与常见错误。"
tags: ["jira", "jira-syntax", "wiki-markup", "templates", "validation", "markdown"]
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
# 第 5 章：jira-syntax 技能详解

本章讲解负责"内容怎么写才对"的 `jira-syntax` 技能。它不发起 API 调用，而是提供 Jira wiki 标记语法、模板与校验能力。

## 5.1 技能定位

`jira-syntax` 技能在撰写或格式化 Jira 描述、评论，或任何将以 Jira 呈现的文本时触发。它完成三件事：

1. 将 Markdown 转换为 Jira wiki 标记。
2. 提供 Bug 报告与特性请求模板。
3. 在提交前校验语法。

> **核心提醒**：Jira 描述与评论使用 **Jira wiki 标记**，而非 Markdown。二者语法相似但不可混用。

## 5.2 快速语法对照

| Jira 语法 | 用途 | 禁止（Markdown） |
|-----------|------|-----------------|
| `h2. Title` | 标题 | `## Title` |
| `*bold*` | 加粗 | `**bold**` |
| `_italic_` | 斜体 | `*italic*` |
| `{{code}}` | 行内代码 | `` `code` `` |
| `{code:java}...{code}` | 代码块 | ``` ```java ``` |
| `[text\|url]` | 链接 | `[text](url)` |
| `[PROJ-123]` | 工单链接 | — |
| `[~username]` | 提及用户 | `@username` |
| `* item` | 无序列表 | `- item` |
| `# item` | 有序列表 | `1. item` |
| `\|\|Header\|\|` | 表头 | `\|Header\|` |

## 5.3 可用模板

### 5.3.1 Bug 报告模板

路径：`templates/bug-report-template.md`

包含章节：环境（Environment）、复现步骤（Steps to Reproduce）、预期/实际行为（Expected/Actual Behavior）、错误信息（Error Messages）、技术备注（Technical Notes）。

### 5.3.2 特性请求模板

路径：`templates/feature-request-template.md`

包含章节：概述（Overview）、用户故事（User Stories）、验收标准（Acceptance Criteria）、技术方案（Technical Approach）、成功指标（Success Metrics）。

## 5.4 语法校验

提交到 Jira 前，运行校验脚本：

```bash
${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh path/to/content.txt
```

> **关键约束**：校验是发帖前的**门禁**，应作为独立的一步运行，绝不与发帖命令串联在一起。

### 5.4.1 校验清单

- [ ] 标题：`h2. Title`（句点后有空格）
- [ ] 加粗：`*text*`（单星号）
- [ ] 代码块：`{code:language}...{code}`
- [ ] 列表：`*` 表示无序、`#` 表示有序
- [ ] 链接：`[label|url]` 或 `[PROJ-123]`
- [ ] 表格：`||Header||` 与 `|Cell|`
- [ ] 颜色：`{color:red}text{color}`
- [ ] 面板：`{panel:title=X}...{panel}`

### 5.4.2 常见错误

| ❌ 错误 | ✅ 正确 |
|---------|---------|
| `## Heading` | `h2. Heading` |
| `**bold**` | `*bold*` |
| `` `code` `` | `{{code}}` |
| `[text](url)` | `[text\|url]` |
| `- bullet` | `* bullet` |
| `h2.Title` | `h2. Title` |
| `MR !42`（裸 GitLab 引用） | `[MR 42\|url]` 或完整 `group/project!42`——裸 `!…!` 是图片标记 |
| `(/)` 用于未完成项 | `(x)`——`(/)` 渲染为绿色对勾（已完成） |
| `( )` 作复选框 | `(x)`——`( )` 非宏，会原样渲染 |

## 5.5 与 jira-communication 的协作

两个技能的协作工作流：

1. 从 `jira-syntax` 获取模板。
2. 用 Jira wiki 标记填充内容。
3. 用 `validate-jira-syntax.sh` 校验语法。
4. 通过 `jira-communication` 技能提交。

## 5.6 参考资料

- `references/jira-syntax-quick-reference.md` — 完整语法文档。
- `references/cross-project-refs.md` — 从 Jira 链接到 GitLab 时的跨项目引用约定（`group/project!N`、`group/project#N`、`group/project@tag`）。
- `templates/bug-report-template.md`、`templates/feature-request-template.md` — 模板文件。
- [官方 Jira Wiki Markup](https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all) — 官方语法参考。

下一章介绍检索工单的 JQL 查询语言。

## 相关概念

- [jira-communication 技能](/concepts/04-jira-communication.md)：API操作技能
- [快速开始](/concepts/03-quickstart.md)：命令快速上手
- [语法模板示例](/examples/syntax-templates.md)：模板实操示例
- [官方文档信源](/references/official-docs.md)：Wiki Markup官方参考