---
id: "spec-writing-08"
title: "08 PRD Spec格式概述"
source: "rules/spec-writing-guide.md#08"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-writing-guide/08-prd-format-overview.toml"
---

# 08 PRD Spec格式概述

---

## 章节导航

本章节介绍PRD Spec（产品需求规格说明书）的完整格式体系，与Change Spec的适用场景对比，以及如何根据项目特征选择合适的Spec格式。

---

## 两种Spec格式体系

在规范体系中，存在两种互补的Spec格式，分别适用于不同场景：

### Change Spec（变更规格）

本指南前7章（01-07）主要定义的**Change Spec**格式，适用于基于已有系统/产品的增量变更场景，包含：

```
YAML Frontmatter → Why → What Changes → Impact
→ ADDED Requirements → MODIFIED Requirements → REMOVED Requirements
```

**核心特征**：增量式、聚焦变更点、分类管理需求变更、适用于迭代优化/Bug修复/小功能添加。

---

### PRD Spec（产品需求规格）

**PRD Spec**适用于从零开始定义完整产品/功能的场景，包含十节完整结构：

```
YAML Frontmatter → Overview → Goals → Non-Goals → Background
→ FR → NFR → Constraints → Assumptions → AC → Open Questions
```

**核心特征**：全量定义、明确范围边界、强调可衡量目标、包含完整追溯链、适用于新项目/新模块立项/架构级重构。

---

## PRD Spec vs Change Spec 核心差异

| 维度 | PRD Spec | Change Spec |
|------|----------|-------------|
| **出发点** | 从零开始定义 | 基于已有基线变更 |
| **范围描述** | Goals + Non-Goals明确边界 | What Changes列出变更点 |
| **需求组织** | FR/NFR完整分解 | ADDED/MODIFIED/REMOVED分类 |
| **背景深度** | Background完整前因后果 | Why简洁说明动机 |
| **验收标准** | AC全量Given/When/Then | Scenario基于WHEN/THEN |
| **追溯关系** | G→FR→AC完整追溯链 | 引用原有Requirement编号 |
| **典型篇幅** | 200-500行 | 50-200行 |
| **适用阶段** | 新项目/新模块立项 | 迭代/优化/重构 |

---

## 格式选择指南

如何判断应该使用PRD Spec还是Change Spec？请参考三维度决策框架：

### 维度1：基线存在性

- **无已有基线**（全新项目、从无到有的功能）→ PRD Spec
- **有已有基线**（已上线/已合并代码、已有完整Spec）→ 倾向Change Spec

### 维度2：变更比例

- **<30%**（增量优化、小功能、Bug修复）→ Change Spec
- **>70%**（几乎重写、架构级变更）→ PRD Spec
- **30%-70%**（中等规模）→ 结合维度3判断

### 维度3：受众范围

- **需要完整上下文**（新人入职、跨团队、长期归档、重大决策）→ 倾向PRD Spec或混合模式
- **不需要完整上下文**（团队内部迭代、已知上下文、快速修复）→ 倾向Change Spec

完整的决策树、测试场景验证、混合使用模式请参考：

**→ [Spec格式选择指南：PRD Spec vs Change Spec](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/format-selection-guide.md)**

---

## 格式选择反模式

### ❌ 小变更用PRD Spec

修改一个按钮文案、增加一个配置项，却写完整的Overview/Goals/Non-Goals/Background，导致Spec篇幅是实际代码的10倍，阅读成本远大于收益。

**修正**：用Change Spec，Why+What Changes+MODIFIED三章即可，50行以内搞定。

### ❌ 大重构用Change Spec

核心模块重写、架构级变更，却只列ADDED/MODIFIED/REMOVED，不重新定义Goals和NFR，导致新系统质量标准缺失，验收无依据。

**修正**：用PRD Spec完整定义，或采用混合模式。

---

## 相关模式

- [Spec九段叙事法](../../../docs/retrospective/patterns/methodology-patterns/product-growth/spec-nine-section-narrative.md)
- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [双向导航链接](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/bidirectional-navigation-links.md)
- [PRD结构指南](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/prd-structure-guide.md)
- [通用PRD模板](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/universal-prd-template.md)
---

← 上一章: [07 完整Spec模板](07-template-reference.md) | **[返回索引](../spec-writing-guide.md)** | 下一章: [09 PRD模板引用](09-prd-template-reference.md) →
