---
type: Reference
title: "官方文档与外部资源信源"
description: "Jira API、Agent Skills 标准、Wiki Markup 官方文档等外部参考资源登记"
tags: ["jira", "documentation", "official", "reference"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "https://developer.atlassian.com/cloud/jira/platform/rest/v3/"
    type: "official-docs"
    trust: high
  - resource: "https://agentskills.io"
    type: "standard"
    trust: high
  - resource: "https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all"
    type: "official-docs"
    trust: high
---

# 官方文档与外部资源信源

本文件登记与 jira-skill 相关的外部官方文档、标准和参考资源。

## Jira REST API

### Cloud REST API v3

- **URL**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **用途**: jira-communication 脚本通过 atlassian-python-api 间接调用的底层 REST API
- **关键端点**：
  - 搜索：`POST /rest/api/3/search/jql`（Cloud 专用分页端点）
  - 工单 CRUD：`/rest/api/3/issue/`
  - 评论：`/rest/api/3/issue/{issueIdOrKey}/comment`
  - 转换：`/rest/api/3/issue/{issueIdOrKey}/transitions`
  - Agile：`/rest/agile/1.0/`
  - Tempo Accounts：`/rest/tempo-accounts/1/`

### Server/Data Center REST API

- **URL**: https://developer.atlassian.com/server/jira/platform/rest-apis/
- **主要版本**: Jira Server/DC 9.12
- **认证方式**: Personal Access Token（PAT）
- **与 Cloud 差异**：
  - 用户标识使用 `username` 而非 `accountId`
  - JQL 搜索端点和分页机制不同
  - 部分字段和 expand 参数存在差异

## Agent Skills 开放标准

- **URL**: https://agentskills.io
- **用途**: jira-skill 遵循的 AI 智能体技能包标准
- **核心概念**：
  - SKILL.md 作为技能入口描述文件
  - 脚本通过自然语言描述触发（非 MCP 工具注册）
  - 技能包可移植，支持文件系统分发

## Jira Wiki Markup

- **官方帮助**: https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all
- **用途**: jira-syntax 技能的语法参考权威来源
- **注意**: Jira wiki markup 不是 Markdown，两者语法不兼容

## atlassian-python-api

- **PyPI**: https://pypi.org/project/atlassian-python-api/
- **版本约束**: >=3.41,<4（故意锁定 v3）
- **锁定原因**: v4 修复了 Cloud 问题但引入 DC 回归；项目主要目标为 Jira Server/DC 9.12

## PEP 723 — 内联脚本依赖

- **PEP**: https://peps.python.org/pep-0723/
- **用途**: 所有脚本使用 `# /// script` 块声明内联依赖
- **执行方式**: `uv run --script script.py`

## 源码仓库

- **GitHub**: https://github.com/netresearch/jira-skill
- **许可证**: MIT + CC-BY-SA-4.0

## 项目内参考文档

jira-communication 自带17个参考文档（位于 `skills/jira-communication/references/`），涵盖：

- 认证配置指南
- JQL 语法参考
- 各脚本详细使用说明
- 故障排查指南
- 最佳实践

jira-syntax 自带2个参考文档（位于 `skills/jira-syntax/references/`），涵盖：

- Wiki markup 语法对照表
- 支持的代码语言列表
