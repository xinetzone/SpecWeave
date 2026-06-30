# 编写 TuyaClaw Skills 学习掌握指南 Spec

## Why

用户希望系统性地学习并掌握位于 `C:\Users\XMICUser\.tuyaclaw\skills` 目录下的全部技能。该目录包含 5 个相互关联的 TuyaClaw/OpenClaw 技能（环境诊断、设备控制、HA 桥接、安全治理、主机入侵检测），缺乏一份统一的、面向学习者的中文掌握指南，导致学习路径不清、知识点零散、上手成本高。

## What Changes

- 新增一份结构化的中文《TuyaClaw Skills 学习掌握指南》文档，作为本次 spec 的最终交付物。
- 文档涵盖以下五大部分：
  - 目录文件结构分析（5 个技能的组织方式、关键文件职责）
  - 各技能模块的学习顺序建议（依赖关系驱动的递进路径）
  - 核心知识点梳理（每个技能的设计理念、能力边界、关键约束）
  - 实践操作步骤（环境准备、配置、典型调用示例）
  - 常见问题与解决方法（凭据、网络、平台差异、权限等）
- 文档以纯中文撰写，使用 Markdown 格式，必要处使用 Mermaid 表达依赖与流程关系。

## Impact

- Affected specs: 无（纯文档新增，不修改既有 capability）
- Affected code: 无代码改动；仅在 `.trae/specs/docs-restructure/explain-tuyaclaw-skills-learning/` 下产出 spec 文档，最终学习指南交付物存放路径在实施阶段确认（默认随 spec 目录或用户指定路径）
- 数据来源：只读分析 `C:\Users\XMICUser\.tuyaclaw\skills` 下各技能的 `SKILL.md` / `README.md` / 目录结构，不修改该外部目录任何文件

## ADDED Requirements

### Requirement: 目录文件结构分析

文档 SHALL 提供对 skills 根目录及 5 个子技能目录的结构化解析，说明每个技能的关键文件（SKILL.md、references/、scripts/、tools/、contracts/ 等）的职责。

#### Scenario: 读者查阅目录结构
- **WHEN** 读者打开指南的"目录结构分析"章节
- **THEN** 能看到 5 个技能（openclaw-env、tuya-smart-control、tuya-ha-bridge、tuya-security-master、mini-hids）的目录树说明及每个关键文件/子目录的用途

### Requirement: 学习顺序建议

文档 SHALL 给出基于技能依赖关系的推荐学习顺序，并用 Mermaid 图表达技能间的前置/依赖关系。

#### Scenario: 读者规划学习路径
- **WHEN** 读者查阅"学习顺序建议"章节
- **THEN** 获得一条从环境准备（openclaw-env）到设备控制、再到安全治理的递进式学习路线，并理解每一步的前置条件

### Requirement: 核心知识点梳理

文档 SHALL 针对每个技能提炼其设计理念、能力范围、能力边界（不支持的操作）与关键安全/技术约束。

#### Scenario: 读者掌握单个技能要点
- **WHEN** 读者阅读某个技能的"核心知识点"小节
- **THEN** 能明确该技能解决什么问题、支持哪些操作、有哪些明确不支持的操作及关键约束（如凭据脱敏、确认门控、平台差异）

### Requirement: 实践操作步骤

文档 SHALL 提供可执行的实践步骤，包括环境变量配置、依赖安装、典型命令调用示例。

#### Scenario: 读者动手实践
- **WHEN** 读者按照"实践操作步骤"章节操作
- **THEN** 能完成环境检测、凭据配置，并运行至少一个技能的典型示例命令

### Requirement: 常见问题与解决方法

文档 SHALL 汇总各技能在使用中高频出现的问题及其排查/解决方法。

#### Scenario: 读者遇到问题排查
- **WHEN** 读者在使用技能时遇到报错（如凭据缺失、命令未找到、设备离线、Token 被截断等）
- **THEN** 能在"常见问题"章节找到对应的原因说明与解决步骤

## MODIFIED Requirements

无

## REMOVED Requirements

无
