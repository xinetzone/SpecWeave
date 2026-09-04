---
id: "extract-agent-workspace-template"
title: "通用智能体工作区模板萃取（来自 AGENTS.md + .agents/）"
source: "用户/spec指令 + seven-concepts-cmd 方法论编排"
created_at: "2026-08-19"
status: "planning"
theme: "retrospectives-insights"
methodology: "seven-concepts（场景4 知识沉淀，链路 R→I→E→V→C）"
---

# 通用智能体工作区模板萃取 Spec

## Why
SpecWeave 的 [AGENTS.md](../../AGENTS.md) 与 [.agents/](../../.agents/README.md) 构成一套完整的「智能体工作区枢纽」体系（启动协议、四大顶层区域、上下文路由表、渐进式披露、内容敏感度分流、规范容器等）。但该体系与 SpecWeave 项目本身深度耦合（如 vendor/flexloop 子模块、具体角色名、具体脚本库），新项目若要复用缺乏一个剥离项目特有内容、保留通用结构的模板。本任务用 seven-concepts 方法论（知识沉淀场景 R→I→E→V→C）从中萃取一套通用模板，使任何新项目都能快速引导出结构一致、规范完备的智能体工作区。

## What Changes
- 新建顶层 `templates/` 目录及索引 README
- 产出「通用 AGENTS.md 模板」（参数化占位符）
- 产出「精简版 .agents/ 目录骨架」
- 产出「脚手架使用说明」（复制/参数化/装载步骤）
- 产出「可复用模式文档」并归档至模式库

## Impact
- Affected specs: 无既有 spec 被修改或删除（全部为新增交付物）
- Affected code: 模式库索引（`docs/retrospective/patterns/` 对应目录 README）需新增登记
- 新增目录/文件：`templates/`、`docs/retrospective/patterns/architecture-patterns/agent-workspace-template.md`

## ADDED Requirements

### Requirement: 顶层 templates 目录与索引
系统 SHALL 提供顶层 `templates/` 目录承载通用脚手架模板，并提供索引 README 说明各类模板的用途与入口。

#### Scenario: 定位通用模板
- **WHEN** 开发者需要为新项目引导智能体工作区
- **THEN** 可从 `templates/README.md` 快速定位到通用脚手架并理解其用途

### Requirement: 通用 AGENTS.md 模板
系统 SHALL 提供一份「通用 AGENTS.md 模板」（`templates/agent-workspace-hub/AGENTS.md`），剥离 SpecWeave 特有内容（vendor 子模块、具体角色/脚本名），保留启动协议、四大顶层区域、上下文路由表、核心规范入口、开发规范、知识库复盘的通用结构与占位，并用占位符（如 `{{PROJECT_NAME}}`、`{{PROJECT_DESC}}`）标注需参数化的位置。

#### Scenario: 参数化复用
- **WHEN** 用户将模板复制到新项目
- **THEN** 仅需替换占位符即可得到结构一致的全局契约，无需从头设计启动协议与路由体系

### Requirement: 精简版 .agents 目录骨架
系统 SHALL 提供 `templates/agent-workspace-hub/.agents/` 精简骨架，覆盖关键子目录（roles/rules/workflows/protocols/templates/scripts/skills/commands/docs）并附占位 README，明确每一层的职责与最小内容要求。

#### Scenario: 最小可引导骨架
- **WHEN** 用户复制精简骨架
- **THEN** 得到可立即扩展的规范容器目录结构，无需重新设计目录分层

### Requirement: 脚手架使用说明
系统 SHALL 提供 `templates/agent-workspace-hub/README.md`，说明脚手架的使用步骤：复制目录、参数化占位符、装载/自举为有效规范体系。

#### Scenario: 开箱即用
- **WHEN** 用户阅读使用说明
- **THEN** 能按步骤完成复制与参数化，并成功装载为有效规范体系

### Requirement: 可复用模式文档
系统 SHALL 将「通用智能体工作区模板」沉淀为可复用模式文档，归档至 `docs/retrospective/patterns/architecture-patterns/agent-workspace-template.md`，包含触发场景、核心步骤、反模式、迁移验证，并遵循模式文档 TOML frontmatter 规范（id/domain/layer/maturity/validation_count/source 等）。

#### Scenario: 模式可迁移
- **WHEN** 后续遇到「新项目需引导智能体工作区」的同类场景
- **THEN** 可直接复用该模式，明确适用/不适用边界与常见陷阱