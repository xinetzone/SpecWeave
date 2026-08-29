---
type: Concept
title: AI Agent Skills 生态概览
description: 六个开源项目构成的 AI Agent Skills 生态总览，涵盖人格集合、MCP 工具、Skill 知识包、UI 定位、Jira 集成与会话复盘
tags: [agent-skills, overview, ecosystem, mcp, skill, plugin]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: agency-agents-source
    resource: "/references/agency-agents-source.md"
    title: agency-agents 源码
  - id: awesun-mcp-source
    resource: "/references/awesun-mcp-source.md"
    title: awesun-mcp 源码
  - id: awesun-skill-source
    resource: "/references/awesun-skill-source.md"
    title: awesun-skill 源码
  - id: awesun-ui-locator-source
    resource: "/references/awesun-ui-locator-source.md"
    title: awesun-ui-locator 源码
  - id: jira-skill-source
    resource: "/references/jira-skill-source.md"
    title: jira-skill 源码
  - id: retro-skill-source
    resource: "/references/retro-skill-source.md"
    title: retro-skill 源码
---

# AI Agent Skills 生态概览

AI Agent Skills 生态是围绕"如何为 AI 编程助手（Claude Code、Cursor、Codex 等）扩展能力"这一核心问题形成的开源项目群。本知识包梳理了六个具有代表性的项目，它们分别从人格组织、工具协议、知识封装、视觉定位、工程集成和自我演进六个维度展示了 Agent Skills 的设计模式。

## 六个项目定位

| 项目 | 类型 | 核心能力 | 关键数字 |
|------|------|---------|---------|
| agency-agents | 人格集合 | 200+ 专业 AI 代理人格，按 17 个部门组织 | 17 部门、16 目标工具、3 种安装类型 |
| awesun-mcp | MCP 服务器 | 向日葵远程控制的 MCP 协议适配 | 22 个工具、双模式通信（Stdio/HTTP） |
| awesun-skill | Skill 知识包 | 将 MCP 工具封装为渐进式披露的 Skill | 1 个执行器（MCPExecutor）、22 个工具映射 |
| awesun-ui-locator | Skill 知识包 | 截图 UI 元素视觉定位，返回归一化坐标 | 5 步工作流、3 个坐标函数、5 类 UI 元素 |
| jira-skill | 插件 | Jira 全流程集成，双技能拆分 | 2 个技能、21 个脚本、PEP 723 内联依赖 |
| retro-skill | 插件 | LLM 驱动的会话复盘与自省 | 6 种模式、21 个机械信号、7 个目标位置 |

## 两种集成范式

生态中存在两种根本不同的 AI 集成范式：

**MCP（Model Context Protocol）是工具协议**。awesun-mcp 通过 stdio 或 HTTP 暴露结构化工具，每个工具有 JSON Schema 定义的参数，AI 通过协议动态发现和调用。MCP 的优势是跨客户端通用、工具发现自动化；代价是工具 Schema 持续占用上下文窗口（25 个工具约消耗 8,000-12,000 Token/会话）。

**Skill 是知识包**。Skill 不重新实现工具，而是通过 SKILL.md 文件告诉 AI"有哪些能力、何时用、怎么用"。awesun-skill 通过 executor.py 桥接 MCP 服务器；jira-skill 直接用 PEP 723 脚本调用 API；awesun-ui-locator 是纯知识+计算工具的 Skill。Skill 的优势是渐进式披露——未激活时仅消耗 description 的 Token，激活后按需展开。

两者不互斥：awesun-skill 是"MCP 工具 + Skill 知识"的组合典范。

## 标准与规范

- **Agent Skills 开放标准**（agentskills.io）：定义 SKILL.md 文件格式、frontmatter 字段和渐进式披露三层结构。jira-skill 和 retro-skill 均遵循此标准。
- **Agent Plugin 规范**（agent-plugins.org/schemas/1.0.0）：定义 plugin.json 插件元数据格式。jira-skill 和 retro-skill 的 plugin.json 遵循此 schema。
- **MCP 协议**：Model Context Protocol，定义 AI 与外部工具的通信标准。awesun-mcp 是 MCP 服务器实现。

## 共同设计模式

尽管六个项目的语言和用途各异，但它们共享若干设计模式：

1. **YAML frontmatter 作为元数据载体**：SKILL.md、Agent 人格文件、plugin.json 均使用结构化元数据声明身份、能力和约束。
2. **渐进式披露**：重型知识放入 references/ 子目录，可执行逻辑放入 scripts/，主入口保持精简。
3. **多工具兼容**：agency-agents 支持 16 种目标工具，通过 format 和 installKind 抽象差异；jira-skill 和 retro-skill 遵循开放标准以获得跨工具兼容性。
4. **机械优先、LLM 兜底**：retro-skill 用 21 个确定性正则信号做第一道检测，LLM 仅增强和过滤；awesun-ui-locator 用确定性公式计算坐标，视觉模型仅做元素识别。
5. **安全边界**：retro-skill 的"No silent writes"原则、jira-skill 的 --dry-run 保护、MCP 的 token 认证，都体现了对 AI 自动化的谨慎约束。

## 目录结构约定

典型的 Skill 目录结构如下：

```text
skill-name/
├── SKILL.md          # 必需：技能主入口（frontmatter + 工作流）
├── scripts/          # 可选：可执行脚本（Python/Shell）
├── references/       # 可选：深度参考文档
├── templates/        # 可选：模板文件
└── evals/            # 可选：评估测试
```

插件（plugin）在 Skill 之上增加：

```text
plugin-root/
├── plugin.json       # 插件元数据
├── commands/         # 斜杠命令定义
├── hooks/            # 生命周期钩子
├── skills/           # 包含的技能（可多个）
└── tests/            # 测试
```

## 相关概念

- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
- [agency-agents 部门化人格体系](/concepts/02-agency-agents-division.md)
- [MCP 协议与工具集成](/concepts/04-mcp-protocol.md)
- [插件架构](/concepts/05-plugin-architecture.md)
