# 概念文档

## 第一批：入门组（标准与架构）

* [00 — AI Agent Skills 生态概览](00-overview.md) — 六个开源项目构成的生态总览，两种集成范式（MCP vs Skill），共同设计模式
* [01 — SKILL.md 标准与渐进式披露](01-skill-md-standard.md) — frontmatter 字段规范、三层渐进式披露、技能类型谱系
* [02 — agency-agents 部门化人格体系](02-agency-agents-division.md) — 17 部门 divisions.json、16 工具 tools.json、三种 installKind、CI 一致性校验
* [03 — Agent 人格文件格式与 frontmatter](03-agent-persona-format.md) — 必需/可选字段、九段正文结构、Persona/Operations 语义分组、lint 规则
* [04 — MCP 协议与工具集成](04-mcp-protocol.md) — MCP 工具协议、22 工具三类划分、Stdio/HTTP 双模式、MCPExecutor 桥接
* [05 — 插件架构（plugin.json/hooks/commands）](05-plugin-architecture.md) — Plugin 规范、双技能打包、commands 命令、hooks 钩子、checkpoints 门控

## 第二批：实战组（项目实践）

* [06 — Awesun 远程控制 Skill 实战](06-awesun-remote-control.md) — MCP+Skill 混合架构、MCPExecutor 类、mcp-config.json 配置、典型场景
* [07 — UI 定位器模式（坐标归一化、视觉定位）](07-ui-locator-pattern.md) — 五步视觉工作流、归一化坐标公式、坐标工具函数、UI 元素特征对照
* [08 — Jira Skill 工程化实践](08-jira-skill-engineering.md) — 双技能拆分、21 脚本三层架构、PEP 723、LazyJiraClient、统一 CLI 契约
* [09 — Retro Skill 自省与演进模式](09-retro-skill-introspection.md) — 六种复盘模式、五层流水线、21 机械信号、七目标路由、No silent writes
* [10 — Skill 脚本工具模式（Python/Shell）](10-skill-tooling-scripts.md) — PEP 723 内联依赖、click CLI、共享库组织、Shell 无依赖原则、信号注册模式
* [11 — 多工具兼容与集成模式](11-integration-patterns.md) — 格式转换引擎、开放标准、插件规范、三种 installKind、字节级 format 约束

```{toctree}
:maxdepth: 2

00-overview
01-skill-md-standard
02-agency-agents-division
03-agent-persona-format
04-mcp-protocol
05-plugin-architecture
06-awesun-remote-control
07-ui-locator-pattern
08-jira-skill-engineering
09-retro-skill-introspection
10-skill-tooling-scripts
11-integration-patterns
```