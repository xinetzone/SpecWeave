---
id: "update-core-resources"
version: "1.0"
source: "方法论编排（I→F→A→C）场景3：重构优化"
---

# 更新项目核心资源 Spec

## Why

项目三个核心资源（README.md、AGENTS.md、.agents/）中的统计数据、目录结构描述和内容描述存在多处不一致，导致文档可信度下降。README.md 徽章数据与 AGENTS.md changelog 数据互相矛盾，.agents/README.md 的目录树和计数与实际情况不符。

## What Changes

- 通过 `docgen.py stats` 自动更新 README.md 和 AGENTS.md 中的核心数据指标
- 手动更新 README.md 徽章数据使其与 AGENTS.md changelog 保持一致
- 手动更新 .agents/README.md 的目录结构、子目录职责表和统计数据
- 确保三个资源之间数据一致性（同一指标在三处文档中数值一致）

## Impact

- Affected specs: 无（纯文档更新，不涉及功能变更）
- Affected code: 无代码变更，仅文档更新
- Affected files:
  - `d:\spaces\SpecWeave\README.md` — 徽章数据 + 核心数据
  - `d:\spaces\SpecWeave\AGENTS.md` — changelog 核心数据
  - `d:\spaces\SpecWeave\.agents\README.md` — 目录结构 + 子目录职责表 + 统计数据

## ADDED Requirements

### Requirement: 核心数据自动同步

系统 SHALL 通过 `docgen.py stats` 命令自动收集并更新 README.md 和 AGENTS.md 中的核心数据指标（Git 提交数、可复用模式数、Python 脚本数、Skill 数量、规则文件数、指令集数量、GitCode Stars 等）。

#### Scenario: 执行 stats 更新
- **WHEN** 运行 `python .agents/scripts/docgen.py stats`
- **THEN** README.md 徽章区域和 AGENTS.md changelog 最新条目中的核心数据被更新为当前实际值

#### Scenario: 数据一致性
- **WHEN** stats 更新完成后
- **THEN** README.md 与 AGENTS.md 中同一指标（如 Skill 数量、指令集数量）的数值一致

### Requirement: .agents/README.md 目录结构完整

系统 SHALL 在 .agents/README.md 中维护准确的目录树结构，包含所有实际存在的子目录。

#### Scenario: 目录树完整性
- **WHEN** 检查 .agents/README.md 目录树
- **THEN** 目录树包含所有实际存在的子目录，包括 `brand/` 等之前遗漏的目录

#### Scenario: 统计数据准确
- **WHEN** 检查 .agents/README.md 中的统计数据
- **THEN** Skill 数量、指令集数量、脚本数量等指标与实际文件系统一致

## MODIFIED Requirements

### Requirement: README.md 徽章数据

README.md 中的徽章（badge）区域 SHALL 展示与 AGENTS.md changelog 一致的核心数据指标。

#### Scenario: 徽章一致性
- **WHEN** 对比 README.md 徽章和 AGENTS.md changelog 最新条目
- **THEN** 脚本数量、Skill 数量、规则数量、指令集数量等关键指标数值一致

### Requirement: .agents/README.md 文档描述

.agents/README.md 的子目录职责表 SHALL 正确反映各子目录的实际内容，包括指令集数量、Skill 数量等。

#### Scenario: 指令集数量描述
- **WHEN** 检查 .agents/README.md 中 commands/ 目录的描述
- **THEN** 指令集数量（如 "14个"）与 commands/ 目录下实际 .md 文件数量一致

## REMOVED Requirements

无。