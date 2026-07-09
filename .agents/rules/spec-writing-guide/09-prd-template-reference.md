---
id: "spec-writing-09"
title: "09 PRD模板引用"
source: "rules/spec-writing-guide.md#09"
x-toml-ref: "../../../.meta/toml/.agents/rules/spec-writing-guide/09-prd-template-reference.toml"
---

# 09 PRD模板引用

---

## 章节导航

本章节提供PRD Spec的通用模板引用，说明模板结构、使用方法、以及配套的规范文档。

---

## 通用PRD模板

完整的通用PRD模板位于patterns库中，包含十节标准结构的完整模板、填写说明和检查要点：

**→ [通用PRD模板](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/universal-prd-template.md)**

---

## PRD十节结构概览

通用PRD模板包含以下标准章节：

| 章节 | 英文名称 | 核心内容 |
|------|---------|---------|
| 1 | Overview | 项目摘要、目的、目标用户 |
| 2 | Goals | 3-8个可衡量目标（G1,G2...） |
| 3 | Non-Goals | 明确不做什么及原因 |
| 4 | Background & Context | 历史脉络、问题现状、关联项目 |
| 5 | Functional Requirements | 功能需求（FR-1,FR-2...），追溯Goal |
| 6 | Non-Functional Requirements | 非功能需求（NFR-1...），按性能/可靠性/可维护性分类 |
| 7 | Constraints | 技术约束、业务约束、依赖项 |
| 8 | Assumptions | 显式化隐含假设，说明不成立的影响 |
| 9 | Acceptance Criteria | Given/When/Then格式验收标准，标注验证方式 |
| 10 | Open Questions | 记录决策过程，已解答/未解答问题 |

可选扩展章节：Requirements Traceability Matrix（需求追溯矩阵）、Risks & Mitigation（风险与缓解）。

---

## 模板使用说明

使用通用PRD模板时，请遵循以下步骤：

1. **复制模板**：复制`universal-prd-template.md`文件，重命名为`[项目id].md`，id使用kebab-case英文命名
2. **修改Frontmatter**：填写id（全局唯一）、title、created_at等字段，status初始为`candidate`
3. **按章节填写**：逐节填写内容，删除`<!-- -->`注释提示
4. **更新状态**：规划阶段status改为`planning`，执行中改为`in-progress`，完成后改为`completed`

每个章节模板内均包含检查要点Checklist，填写完成后请逐项核对。

---

## 配套规范文档

编写PRD Spec时，建议同时参考以下配套文档：

| 文档 | 用途 | 链接 |
|------|------|------|
| Frontmatter规范 | YAML元数据字段定义 | [frontmatter-specification.md](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/frontmatter-specification.md) |
| PRD结构指南 | 各章节详细填写指南 | [prd-structure-guide.md](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/prd-structure-guide.md) |
| 格式选择指南 | PRD vs Change决策树 | [format-selection-guide.md](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/format-selection-guide.md) |
| 最佳实践 | Spec编写经验总结 | [best-practices.md](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/best-practices.md) |
| 解构分析 | 优秀Spec案例分析 | [deconstruction-analysis.md](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/deconstruction-analysis.md) |

---

## 与Change Spec模板的关系

本指南07章提供的是**Change Spec模板**，适用于增量变更；本章引用的是**PRD Spec模板**，适用于全新项目/重大重构。两者关系如下：

- **Change Spec**：本指南01-07章完整定义，适用于<30%变更比例的迭代场景
- **PRD Spec**：引用patterns库中的universal-prd-template，适用于全新项目或>70%变更的重构场景
- **混合模式**：参考format-selection-guide.md中的混合模式说明

两种模板共享相同的基本原则：清晰、完整、可执行、可验收，仅在结构组织和适用场景上有所区别。

---

## 相关模式

- [Spec九段叙事法](../../../docs/retrospective/patterns/methodology-patterns/product-growth/spec-nine-section-narrative.md)
- [规范三同步原则](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- [双向导航链接](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/bidirectional-navigation-links.md)
- [Spec引用验证模式](../../../docs/retrospective/patterns/methodology-patterns/spec-workflow/spec-reference-validation-pattern.md)
---

← 上一章: [08 PRD Spec格式概述](08-prd-format-overview.md) | **[返回索引](../spec-writing-guide.md)**
