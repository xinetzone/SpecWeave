---
okf_version: "0.2"
type: Index
title: AI Agent Skills 知识包
description: AI Agent Skills 生态——SKILL.md 标准、MCP 工具协议、人格集合与工程化集成
tags: [ai-agent, skill, mcp, agent-framework]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
stale_after: 2027-08-23
---

# AI Agent Skills 知识包

本知识包（bundle）系统梳理 AI Agent Skills 生态的架构与实践，涵盖六个开源项目：agency-agents（部门化人格集合）、awesun-mcp（向日葵远程控制 MCP 服务器）、awesun-skill（MCP Skill 桥接）、awesun-ui-locator（截图 UI 元素定位）、jira-skill（Jira 工程化集成）、retro-skill（会话复盘与自省）。内容涵盖 SKILL.md 开放标准、MCP 工具协议、插件架构、PEP 723 脚本模式、机械信号检测、渐进式披露等核心概念，遵循 OKF v0.2 规范。

## 目录分组

* [concepts/](concepts/) - 核心概念：12 篇概念文档，分两批排列，从标准入门到实战模式
  * [00 — AI Agent Skills 生态概览](concepts/00-overview.md)
  * [01 — SKILL.md 标准与渐进式披露](concepts/01-skill-md-standard.md)
  * [02 — agency-agents 部门化人格体系](concepts/02-agency-agents-division.md)
  * [03 — Agent 人格文件格式与 frontmatter](concepts/03-agent-persona-format.md)
  * [04 — MCP 协议与工具集成](concepts/04-mcp-protocol.md)
  * [05 — 插件架构（plugin.json/hooks/commands）](concepts/05-plugin-architecture.md)
  * [06 — Awesun 远程控制 Skill 实战](concepts/06-awesun-remote-control.md)
  * [07 — UI 定位器模式（坐标归一化、视觉定位）](concepts/07-ui-locator-pattern.md)
  * [08 — Jira Skill 工程化实践](concepts/08-jira-skill-engineering.md)
  * [09 — Retro Skill 自省与演进模式](concepts/09-retro-skill-introspection.md)
  * [10 — Skill 脚本工具模式（Python/Shell）](concepts/10-skill-tooling-scripts.md)
  * [11 — 多工具兼容与集成模式](concepts/11-integration-patterns.md)
* [examples/](examples/) - 使用示例：SKILL.md 编写教程
  * [SKILL.md 编写示例](examples/skill-authoring.md)
* [references/](references/) - 信源登记簿：13 篇信源文件，含 R 阶段事实清单、I 阶段洞察与源码登记
  * [agency-agents 事实清单](references/facts-agency-agents.md)
  * [awesun-mcp 事实清单](references/facts-awesun-mcp.md)
  * [awesun-skill 事实清单](references/facts-awesun-skill.md)
  * [awesun-ui-locator 事实清单](references/facts-awesun-ui-locator.md)
  * [jira-skill 事实清单](references/facts-jira-skill.md)
  * [retro-skill 事实清单](references/facts-retro-skill.md)
  * [架构洞察](references/insights.md)
  * [agency-agents 源码](references/agency-agents-source.md)
  * [awesun-mcp 源码](references/awesun-mcp-source.md)
  * [awesun-skill 源码](references/awesun-skill-source.md)
  * [awesun-ui-locator 源码](references/awesun-ui-locator-source.md)
  * [jira-skill 源码](references/jira-skill-source.md)
  * [retro-skill 源码](references/retro-skill-source.md)
