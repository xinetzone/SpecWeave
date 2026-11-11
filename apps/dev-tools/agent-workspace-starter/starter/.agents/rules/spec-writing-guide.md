---
id: "rules-spec-writing-guide"
title: "Spec 文档编写指南"
source: ".agents/rules/spec-writing-guide.md"
---
# Spec 文档编写指南

本指南定义 Spec 文档的标准章节结构、必需与可选元素、命名格式化要求及完整模板，覆盖 Change Spec 与 PRD Spec 两种格式体系。

## 文档导航

完整内容分为九节：01 概述与核心原则 → 02 标准章节结构（Why / What Changes / Impact / ADDED / MODIFIED / REMOVED 六大章节）→ 03 必需元素清单（Requirement 结构 + Scenario WHEN/AND/THEN）→ 04 可选元素（技术指标 / 依赖关系 / 实施优先级）→ 05 命名规范与格式化要求 → 06 正反示例与检查清单（5 大类）→ 07 完整 Spec 模板（可直接复制使用）→ 08 PRD Spec 格式概述 → 09 PRD 模板引用。

## 核心原则

- 每个需求以 `Requirement` 结构描述，配 `Scenario` 说明 WHEN/AND/THEN。
- 章节结构完整、命名规范统一，便于工具解析与看板生成。

> 完整子文档见 SpecWeave 开源仓库。