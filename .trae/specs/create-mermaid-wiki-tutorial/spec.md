---
version: "1.0"
---

# Mermaid 官方文档 Wiki 教程 Spec

## Why

Mermaid 是 SpecWeave 项目首选的图表可视化工具（见 AGENTS.md 全局规则），但当前知识库中只有项目内部的 [mermaid-guide.md](../../../.agents/docs/knowledge/best-practices/mermaid-guide.md)（操作手册，偏"怎么做"），缺少一套基于 Mermaid 官方权威文档（[mermaid.ai/docs](https://mermaid.ai/docs)）与在线编辑器（[mermaid.live](https://mermaid.live/edit)）的系统性学习 wiki，覆盖"图表类型全览、语法、配置、主题、集成"等完整知识层。

本教程旨在系统学习官方文档与在线编辑器，沉淀结构化、可检索、可复现的 wiki 教程，填补知识库在"Mermaid 全景知识"这一领域的空白，与现有操作指南形成互补（操作指南讲项目内规范，本教程讲 Mermaid 本体能力）。

## What Changes

- **新增** 1 个原子化 wiki 目录：`docs/knowledge/learning/04-docs-markup-tooling/mermaid-wiki/`
- **新增** 教程总览与导航索引（`00-overview.md`）
- **新增** Mermaid 入门与安装（`01-introduction-quickstart.md`），覆盖什么是 Mermaid、快速开始、mermaid.live 在线编辑器使用
- **新增** 基础图表类型（`02-flowchart.md`），覆盖 flowchart 的节点、连线、subgraph、方向、样式
- **新增** 序列图（`03-sequence-diagram.md`），覆盖时序图参与者、消息、激活、循环/分支
- **新增** 结构型图表（`04-class-state-er.md`），覆盖 classDiagram、stateDiagram-v2、erDiagram
- **新增** 可视化图表（`05-aggregate-diagrams.md`），覆盖 gantt、pie、journey、timeline、sankey、quadrantChart
- **新增** 进阶图表（`06-advanced-diagrams.md`），覆盖 gitGraph、requirementDiagram、mindmap、C4、block、zenuml
- **新增** 配置与主题（`07-configuration-theming.md`），覆盖配置选项、主题、字体、交互
- **新增** 集成与生态（`08-integrations-ecosystem.md`），覆盖 mermaid-cli、mermaid-live、插件、渲染器对比
- **新增** 常见问题与最佳实践（`09-faq-best-practices.md`）
- **新增** 命令速查表（`10-cheatsheet.md`）
- **更新** `04-docs-markup-tooling/README.md` 子目录导航（新增 mermaid-wiki 条目）
- **不修改** 任何现有 wiki 文档内容（仅 README 追加导航条目）

## Impact

- **Affected specs**: 无（独立新增 wiki 教程）
- **Affected code**: 无代码改动，仅文档新增
- **Affected files**:
  - 新增：`docs/knowledge/learning/04-docs-markup-tooling/mermaid-wiki/00-overview.md` ~ `10-cheatsheet.md` 共 11 个文件 + `README.md`
  - 更新：`04-docs-markup-tooling/README.md`（追加子目录导航条目）
- **Related wikis**: 关联现有 [mermaid-guide.md](../../../.agents/docs/knowledge/best-practices/mermaid-guide.md)（本项目操作指南）与 `mermaid-cmd` 指令集

## Background & Context

Mermaid 是一个基于 JavaScript 的图表与流程图工具，通过 Markdown 风格的文本描述定义图表，再由渲染引擎生成 SVG 图表。核心特性：

- **文本即图表**：用接近自然语言的 DSL 描述，无需专业绘图工具
- **多类型支持**：流程图、时序图、类图、状态图、ER 图、甘特图、饼图、思维导图、用户旅程、Git 图、需求图、C4 架构图、时间线、桑基图、象限图等
- **生态集成**：官方 CLI（mermaid-cli）、在线编辑器（mermaid.live）、mermaid-js GitHub 仓库
- **版本演进**：持续迭代，各图表类型语法在不同版本间有差异

本教程基于两大权威来源学习：
1. [mermaid.ai/docs](https://mermaid.ai/docs) — 官方文档，覆盖全部图表类型语法、配置、主题、集成
2. [mermaid.live/edit](https://mermaid.live/edit) — 官方在线编辑器，用于实时渲染验证学习

教程采用原子化文档结构，遵循项目已有 wiki 规范（参照 `weasyprint-wiki`、`tvm-ffi-wiki` 的文件组织、YAML frontmatter、导航链接模式），所有示例严格遵循 mermaid-cmd 安全编码六规则并运行 `check-mermaid.py` 校验。

## ADDED Requirements

### Requirement: Mermaid Wiki 教程目录与总览

The system SHALL provide a `00-overview.md` file at `docs/knowledge/learning/04-docs-markup-tooling/mermaid-wiki/` containing a complete tutorial overview with reading guide, chapter navigation table, and Mermaid diagram-type hierarchy.

#### Scenario: 用户访问 Mermaid wiki 入口

- **WHEN** 用户打开 `mermaid-wiki/00-overview.md`
- **THEN** 文档包含：教程简介、目标读者、11 章导航表、Mermaid 图表类型总览图（Mermaid）、阅读路径建议、与项目 `mermaid-guide.md` 操作指南及 `mermaid-cmd` 指令集的关联指引

### Requirement: 入门与快速开始

The system SHALL provide a `01-introduction-quickstart.md` file covering what Mermaid is, quickstart, and mermaid.live usage.

#### Scenario: 用户完成 Mermaid 入门

- **WHEN** 用户按文档学习
- **THEN** 文档包含：Mermaid 核心概念（文本即图表）、工作原理、快速开始（mermaid.live 打开→写代码→渲染）、在线编辑器功能（语法高亮/实时预览/分享/导出）、本地集成方式概览

### Requirement: 基础图表 — 流程图

The system SHALL provide a `02-flowchart.md` file covering flowchart syntax comprehensively.

#### Scenario: 用户掌握 flowchart 语法

- **WHEN** 用户按文档学习
- **THEN** 文档包含：节点形状（矩形/圆角/菱形/圆形等）、连线类型（箭头/虚线/粗线）、节点文本与标签、subgraph 分组、direction 方向设置、样式（style/classDef）、链接交互

### Requirement: 时序图

The system SHALL provide a `03-sequence-diagram.md` file covering sequenceDiagram syntax.

#### Scenario: 用户掌握 sequenceDiagram 语法

- **WHEN** 用户按文档学习
- **THEN** 文档包含：participant 参与者、消息类型（实线/虚线/响应）、激活与去激活（activate/deactivate）、循环/分支/并行（loop/alt/opt/par）、注释（Note）、自动序号

### Requirement: 结构型图表

The system SHALL provide a `04-class-state-er.md` file covering classDiagram, stateDiagram-v2, and erDiagram.

#### Scenario: 用户掌握结构型图表

- **WHEN** 用户按文档学习
- **THEN** 文档包含：classDiagram（类/属性/方法/关系/泛型）、stateDiagram-v2（状态/迁移/复合状态/并发）、erDiagram（实体/属性/关系/基数）的完整语法与示例

### Requirement: 可视化图表

The system SHALL provide a `05-aggregate-diagrams.md` file covering gantt, pie, journey, timeline, sankey, and quadrantChart.

#### Scenario: 用户掌握数据可视化类图表

- **WHEN** 用户按文档学习
- **THEN** 文档包含：gantt（甘特图/任务/依赖/里程碑）、pie（饼图）、journey（用户旅程）、timeline（时间线）、sankey（桑基图）、quadrantChart（象限图）的语法与示例

### Requirement: 进阶图表

The system SHALL provide a `06-advanced-diagrams.md` file covering gitGraph, requirementDiagram, mindmap, C4, block, and zenuml.

#### Scenario: 用户掌握进阶图表类型

- **WHEN** 用户按文档学习
- **THEN** 文档包含：gitGraph（Git 分支/提交/合并）、requirementDiagram（需求图）、mindmap（思维导图）、C4（C4 架构图）、block（块图）、zenuml 的语法与示例

### Requirement: 配置与主题

The system SHALL provide a `07-configuration-theming.md` file covering Mermaid configuration and theming.

#### Scenario: 用户掌握 Mermaid 配置

- **WHEN** 用户按文档学习
- **THEN** 文档包含：全局配置（Configuration）、主题（Theme/ThemeVariables）、字体与颜色、安全级别（securityLevel）、常用配置项示例、mermaid.initialize 用法

### Requirement: 集成与生态

The system SHALL provide a `08-integrations-ecosystem.md` file covering mermaid-cli, mermaid.live, and ecosystem integrations.

#### Scenario: 用户掌握 Mermaid 集成方式

- **WHEN** 用户按文档学习
- **THEN** 文档包含：mermaid-cli（mmdc 命令行渲染）、mermaid.live 在线编辑器、Markdown/渲染器集成（GitHub/飞书/VS Code）、mermaid.js 库 API、生态工具对比

### Requirement: 常见问题与最佳实践

The system SHALL provide a `09-faq-best-practices.md` file covering common issues and best practices.

#### Scenario: 用户能自行排查与写出高质量图表

- **WHEN** 用户查阅 FAQ 文档
- **THEN** 文档包含：不少于 8 个常见问题（语法错误/渲染失败/版本差异/中文乱码等）、最佳实践建议、与项目安全编码六规则的对接说明

### Requirement: 命令速查表

The system SHALL provide a `10-cheatsheet.md` file containing quick-reference for all diagram types.

#### Scenario: 用户快速查找语法

- **WHEN** 用户需要速查命令
- **THEN** 文档包含：按图表类型分类的语法速查表（flowchart/sequence/class/state/er/gantt/pie/journey/timeline/sankey/quadrant/gitgraph/requirement/mindmap/C4/block/zenuml）、常用配置速查、mermaid.live 使用速查

## Data Sources

学习材料来源：

1. [mermaid.ai/docs](https://mermaid.ai/docs) — Mermaid 官方文档，覆盖全部图表类型语法、配置、主题、集成
2. [mermaid.live/edit](https://mermaid.live/edit) — 官方在线编辑器，用于实时渲染验证、分享与导出

<!-- changelog -->
<!--
- 2026-08-06 | initial | 初始版本，定义 11 章原子化文档的完整 Requirements
-->