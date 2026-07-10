---
id: "superpowers-index"
title: "超能计划文档库"
x-toml-ref: "../../.meta/toml/docs/superpowers/README.toml"
category: "superpowers"
date: "2026-07-09"
---
# 超能计划文档库

> **本目录**存放 SpecWeave 项目的"超能计划"（Superpowers）——即通过 `/spec` 规格前置模式驱动的能力增强方案，包含执行计划（plans/）与设计文档（specs/）两类资产。

## 🎯 超能计划概述

> **什么是超能计划？**
>
> 超能计划是 SpecWeave 项目中"规格前置知识交付模式"的具体实践载体：先输出设计文档（specs/）明确 Why/What/How，再输出可勾选执行的分步计划（plans/），执行者按 checkbox 逐任务推进并验证，确保能力增强过程可追溯、可验证、可复用。

### plans/ 与 specs/ 的关系

| 目录 | 定位 | 内容特征 | 文件名模式 |
|------|------|---------|-----------|
| 📋 **plans/** | 执行计划 | 可勾选的 Task/Step 清单，含具体文件路径、命令、预期结果 | `{日期}-{编号或主题}-plan.md` |
| 📐 **specs/** | 设计文档 | 背景分析、目标/非目标、方案比较、验收标准、风险控制 | `{日期}-{编号}-{主题}-design.md` |

### 核心工作流

```mermaid
flowchart LR
    A["能力增强需求"] --> B["设计文档 specs/"]
    B --> C["方案评审确认"]
    C --> D["执行计划 plans/"]
    D --> E["按Step逐任务执行"]
    E --> F["每步验证+checkbox标记"]
    F --> G["完成后沉淀复盘"]
```

---

## 📚 plans/ 目录索引（执行计划）

> 执行计划采用 checkbox 语法（`- [ ]`），每个 Task 包含具体文件路径、操作步骤、验证命令与预期结果。

### ACT 系列方案（ACT-001 ~ ACT-004）

| ACT编号 | 计划文件 | 主题 | 核心目标 |
|---------|---------|------|---------|
| **ACT-001** | [2026-07-01-act-001-template-package.md](plans/2026-07-01-act-001-template-package.md) | 完整模板包 | 为"规格前置知识交付模式"落地可复用模板包，新增使用说明并接入复盘模板索引 |
| **ACT-002** | [2026-07-01-act-002-risk-clustering-enhancement-plan.md](plans/2026-07-01-act-002-risk-clustering-enhancement-plan.md) | 风险聚类增强 | 引入基于规则词典的风险语义聚类，生成 `risk_clusters` 与 `risk_cluster_details` |
| **ACT-002** | [2026-07-01-act-002-xlsx-test-report-plan.md](plans/2026-07-01-act-002-xlsx-test-report-plan.md) | xlsx测试报告 | xlsx测试报告智能体化能力增强（配套风险聚类） |
| **ACT-003** | [2026-07-01-act-003-release-gate-summary-plan.md](plans/2026-07-01-act-003-release-gate-summary-plan.md) | 发布门禁摘要 | 新增发布判断摘要模板，补充"平台语义映射"与"平台影响面" |
| **ACT-004** | [2026-07-01-act-004-summary-example-and-platform-mapping-plan.md](plans/2026-07-01-act-004-summary-example-and-platform-mapping-plan.md) | 摘要示例与平台映射 | 基于真实xlsx样本生成正式summary.md产物，平台语义映射轻量抽象 |

### 方法论沉淀计划

| 计划文件 | 主题 | 核心目标 |
|---------|------|---------|
| [2026-07-08-git-hooks-three-tier-trust.md](plans/2026-07-08-git-hooks-three-tier-trust.md) | Git钩子三层信任模型 | 将"L1 pre-commit→L2 pre-push→L3 CI"分层信任模型沉淀为独立模式文档，更新所有索引 |

---

## 📐 specs/ 目录索引（设计文档）

> 设计文档遵循标准结构：背景→目标/非目标→方案比较→交付物→分阶段设计→测试策略→验收标准→风险控制。

### ACT 系列设计文档（ACT-001 ~ ACT-004）

| ACT编号 | 设计文件 | 主题 | 对应计划 |
|---------|---------|------|---------|
| **ACT-001** | [2026-07-01-act-001-template-package-design.md](specs/2026-07-01-act-001-template-package-design.md) | 完整模板包设计 | ACT-001计划 |
| **ACT-002** | [2026-07-01-act-002-risk-clustering-enhancement-design.md](specs/2026-07-01-act-002-risk-clustering-enhancement-design.md) | 风险聚类增强设计 | ACT-002风险聚类计划 |
| **ACT-002** | [2026-07-01-act-002-xlsx-test-report-design.md](specs/2026-07-01-act-002-xlsx-test-report-design.md) | xlsx测试报告设计 | ACT-002 xlsx计划 |
| **ACT-003** | [2026-07-01-act-003-release-gate-summary-design.md](specs/2026-07-01-act-003-release-gate-summary-design.md) | 发布门禁摘要设计 | ACT-003计划 |
| **ACT-004** | [2026-07-01-act-004-summary-example-and-platform-mapping-design.md](specs/2026-07-01-act-004-summary-example-and-platform-mapping-design.md) | 摘要示例与平台映射设计 | ACT-004计划 |

---

## 🧭 阅读路径建议

### 按角色推荐

| 角色 | 推荐阅读顺序 |
|------|-------------|
| 🆕 新接触超能计划 | ACT-001设计 → ACT-001计划 → 理解模板包工作流 → 按需阅读其他ACT |
| 🏗️ 方案设计者 | 先读对应specs/下的设计文档 → 确认方案 → 再读/写plans/执行计划 |
| 👨‍💻 执行者 | 直接读plans/下对应计划 → 从Task 1开始 → 逐Step勾选执行 |
| 🔍 复盘/沉淀者 | 通读所有ACT理解能力演进脉络 → 重点关注方法论沉淀类计划（如Git钩子三层信任） |

### 按能力域推荐

| 能力域 | 相关文档 |
|--------|---------|
| 📄 文档/模板体系 | ACT-001（模板包） |
| 📊 xlsx测试报告分析 | ACT-002（风险聚类 + xlsx报告） |
| 🚀 发布门禁/质量控制 | ACT-003（发布摘要）→ ACT-004（真实示例验证） |
| 🪝 Git钩子/CI体系 | Git钩子三层信任模型计划 |

---

## 📋 执行计划通用结构说明

每个 plans/ 下的执行计划通常包含以下标准章节：

| 章节 | 内容 |
|------|------|
| **Goal** | 一句话说明本次计划的核心目标 |
| **Architecture** | 方案架构概述，说明新增/修改/复用的文件 |
| **Tech Stack** | 使用的技术栈 |
| **文件结构** | 明确的 Create/Modify/Reference/Verify 文件清单表格 |
| **Task N** | 分任务执行，每个Task含Files清单和带checkbox的Step |
| **Step** | 每步含具体操作（Markdown片段/命令/验证方式） |
| **自检结论** | Spec覆盖、占位符扫描、命名一致性检查 |

## 📐 设计文档通用结构说明

每个 specs/ 下的设计文档通常包含以下标准章节：

| 章节 | 内容 |
|------|------|
| **1. 背景** | 问题背景、现状分析、为什么需要做这次增强 |
| **2. 目标与非目标** | 明确哪些要做、哪些不做（防止范围蔓延） |
| **3. 方案选择** | 备选方案对比→推荐方案→推荐理由 |
| **4. 交付物与文件范围** | 新增/修改/不修改的文件清单 |
| **5. 分阶段实施设计** | 分阶段的详细设计说明 |
| **6. 数据与渲染行为约束** | 兼容性、信息密度、优先级原则 |
| **7. 测试策略** | 测试重点、建议测试项、回归重点 |
| **8. 验收标准** | 可量化、可验证的验收条件 |
| **9. 风险与应对** | 风险识别+应对策略 |
| **10. 兼容性与边界** | 与现有体系的关系、扩展边界说明 |

---

## 🔗 相关资源

- [📁 复盘模板目录](../retrospective/templates/README.md) - spec-template.md / tasks-template.md / checklist-template.md 基础模板
- [📁 可复用模式库](../retrospective/patterns/README.md) - 超能计划完成后沉淀的可复用方法论模式
- [📁 .trae/specs/](../../.trae/specs/README.md) - 任务级spec实例存放目录
- [🏠 文档首页](../README.md) - 返回文档总入口
