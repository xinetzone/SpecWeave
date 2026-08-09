---
id: "hermes-agent-integration-00-overview"
title: "00 集成总览与两条路径"
source: "hermes-agent 插件文档 v2.5.0 + hermes-okf v0.5.9 Wiki + SpecWeave 现状"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/00-overview.toml"
type: "Wiki Tutorial"
description: "SpecWeave 接入 Hermes Agent 集成总览：集成目标、两条路径、章节导航、前置知识"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "把 SpecWeave 整个工作区接入 Hermes Agent，使其能力可被正确识别、调用与执行；涉及 Hermes Agent 框架插件路径与 Hermes OKF 记忆层两条路径"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 00 集成总览与两条路径

## 0.1 集成目标

将 **SpecWeave 整个工作区**集成到 Hermes Agent 的目标是：让 Hermes 能够**正确识别、调用和执行** SpecWeave 的能力。具体而言：

- **识别**：Hermes 能发现 SpecWeave 暴露的工具（tools）、技能（skills）、钩子（hooks）与记忆层
- **调用**：Hermes 在会话中能正确发起对 SpecWeave 能力的调用（参数校验、schema 匹配）
- **执行**：被调用的能力能正确执行并返回结果，且结果可被记忆层持久化

SpecWeave 可供暴露的能力资产包括：

| 能力资产 | 位置 | 内容 |
|---------|------|------|
| AGENTS.md 契约 | 根目录 | 启动协议、上下文路由、内容敏感度分流 |
| 规范体系 | `.agents/` | roles/commands/scripts/skills/protocols/rules/workflows |
| Skills 门面 | `.agents/skills/` | 10 命令集门面 + 3 完整 Skill + 6 脚本命令门面 |
| 指令集 | `.agents/commands/` | 复盘/洞察/萃取/原子化/原子提交/mermaid 等 14 项 |
| 脚本库 | `.agents/scripts/` | 25+ 验证/生成/CI 自动化脚本 |
| 角色 | `.agents/roles/` | 7 角色定义（orchestrator/architect/developer/reviewer/tester/co-founder/thesis-advisor 等） |
| 知识库 | `.agents/docs/knowledge/` | 学习教程、复盘、模式库、wiki |
| vendor 子模块 | `vendor/` | flexloop（9 技能）、ark-cli、awesome-okf 等 |

## 0.2 两条集成路径

### 路径一：Hermes Agent 框架插件

把 SpecWeave 能力注册为 **Hermes 插件**。Hermes 插件分三类：

- **通用插件（General）**：注册自定义工具、钩子、斜杠命令 —— 适合承载 SpecWeave 的 skills/commands/scripts
- **内存插件（Memory Provider）**：替换/增强内置记忆 —— 适合挂接 hermes-okf 或自定义记忆
- **上下文插件（Context Engine）**：替换内置上下文压缩 —— 仅单实例，需谨慎

**适用场景**：希望 Hermes 直接调用 SpecWeave 的复盘/洞察/萃取/原子化等命令与脚本。

### 路径二：Hermes OKF 记忆层

把 SpecWeave 的知识库（`knowledge/` 下的 markdown + YAML frontmatter）作为 **OKF memory bundle** 挂接到 Hermes 会话，使决策、观察、工具调用历史跨会话持久化。

**适用场景**：希望 SpecWeave 知识库成为 Hermes 可检索、可持久化的记忆/上下文层。

> 两条路径**可并行**：路径一负责"能力可调用"，路径二负责"记忆可持久化"。多数生产集成两者都用。

## 0.3 前置知识

在深入阅读前，建议先了解以下基础（交叉引用项目内 wiki）：

- [Hermes OKF Wiki 教程](../../01-agent-protocols-interfaces/okf-wiki/README.md) — hermes-okf 基础概念、五层架构、CLI、Agent 集成
- [OKF 开放知识格式指南](../../01-agent-protocols-interfaces/okf-wiki/README.md) — OKF 规范、Bundle/Concept/Frontmatter
- [SpecWeave 能力注册中心](../../../../../capability-registry.md) — SpecWeave 全量能力索引
- [SpecWeave skills 索引](../../../../../skills/README.md) — SpecWeave Skill 分类与触发词

## 0.4 章节导航与阅读路径

| 章节 | 内容 | 路径 |
|------|------|------|
| [01 插件接口规范](01-hermes-plugin-interface.md) | 插件三类、发现路径、plugin.yaml、register(ctx) | 深度集成 |
| [02 能力盘点与映射矩阵](02-capability-mapping.md) | SpecWeave 能力 → Hermes 能力映射 | 深度集成 |
| [03 配置文件设置](03-configuration.md) | config.yaml、HERMES_HOME、hermes-okf 自动配置 | 快速接入 |
| [04 数据格式转换](04-data-conversion.md) | AGENTS.md→plugin、md→OKF concept | 深度/记忆层 |
| [05 权限认证流程](05-auth-permission.md) | name 消毒、路径安全、API key | 深度集成 |
| [06 调用方式示例](06-usage-examples.md) | plugins install、hermes okf、会话内调用 | 快速接入 |
| [07 常见问题及解决方案](07-troubleshooting.md) | 未发现/未启用/schema/单实例/Windows | 快速接入 |

三条阅读路径见 [README](README.md) 的"阅读建议"。

## 0.5 关键概念速查

| 术语 | 含义 |
|------|------|
| **Hermes Agent** | 模块化 Agent 框架（NousResearch/hermes-agent），插件系统是其扩展核心 |
| **Plugin** | Hermes 扩展模块，独立目录，通过 plugin.yaml + register(ctx) 注入能力 |
| **Memory Provider** | 内存插件类型，替换/增强内置记忆，仅单实例 |
| **Context Engine** | 上下文插件类型，替换内置上下文压缩，仅单实例 |
| **OKF** | Open Knowledge Format，Google 发布的开放知识格式（Markdown+YAML） |
| **Concept** | OKF 中的基本知识单元（带 frontmatter 的 markdown） |
| **Bundle** | OKF 知识单元集合，作为 Agent 记忆层挂载 |
