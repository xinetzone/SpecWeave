---
id: "spec-workflow-readme"
title: "Spec工作流模式库索引"
source: "retrospective-analysis"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/spec-workflow/README.toml"
created_at: "2026-07-09"
last_updated: "2026-07-10"
status: "completed"
theme: "methodology-patterns"
version: "1.3"
archive_location: "docs/retrospective/patterns/methodology-patterns/spec-workflow/"
---
# Spec工作流模式库索引

本目录收录Spec（规格说明书）编写工作流相关的方法论模式、模板、规范和最佳实践，为PRD Spec（产品需求规格）和Change Spec（变更规格）提供完整的编写指导体系。

---

## 文档导航

| 文档 | 类型 | 核心内容 |
|------|------|---------|
| [deconstruction-analysis.md](./deconstruction-analysis.md) | 分析报告 | 高质量Spec的第一性原理解构分析，剖析每个章节"为什么存在" |
| [frontmatter-specification.md](./frontmatter-specification.md) | 规范标准 | YAML Frontmatter元数据规范，定义必填/推荐字段、状态机、命名规则 |
| [prd-structure-guide.md](./prd-structure-guide.md) | 结构指南 | PRD十节正文结构详解，每章核心目的、必填要素、正反示例、检查要点 |
| [format-selection-guide.md](./format-selection-guide.md) | 决策指南 | PRD Spec vs Change Spec三维度决策树，5个测试场景，混合使用模式 |
| [best-practices.md](./best-practices.md) | 实践指南 | Spec编写常见陷阱（12个）、正反示例、质量自检清单、避坑指南 |
| [universal-prd-template.md](./universal-prd-template.md) | 模板文件 | 通用PRD十节结构完整模板，含填写说明、注释提示、检查Checklist |
| [spec-reference-validation-pattern.md](./spec-reference-validation-pattern.md) | 方法论模式 | Spec阶段引用验证模式，防止引用不存在的文件导致返工 |
| [spec-mode-verification-gates.md](./spec-mode-verification-gates.md) | 方法论模式 | L2已验证：Spec Mode+验证门禁双保险工作流，四阶段外部化认知负担+六件套验证门禁；含80%验收标准测试量化决策标准和三类适用场景划分，3次验证证明可显著降低返工 |

---

## ✅ Dogfooding自验证状态

2026-07-09完成Dogfooding验证：
- 通用PRD模板已迭代至v1.1，共152行
- 结构指南已同步更新至v1.1
- 验证记录详见 [deconstruction-analysis.md 第七章](./deconstruction-analysis.md#七dogfooding自验证记录2026-07-09)
- 所有高优先级问题已修复，模板可投入使用

---

## 阅读顺序建议

### 入门路径（新手）

1. **[format-selection-guide.md](./format-selection-guide.md)** → 先判断该用PRD还是Change
2. **[frontmatter-specification.md](./frontmatter-specification.md)** → 学习元数据规范
3. **[universal-prd-template.md](./universal-prd-template.md)** → 直接复制模板开始写
4. **[best-practices.md](./best-practices.md)** → 写完对照检查避坑

### 进阶路径（有经验）

1. **[deconstruction-analysis.md](./deconstruction-analysis.md)** → 理解每个章节背后的设计原理
2. **[prd-structure-guide.md](./prd-structure-guide.md)** → 深入掌握每章写作技巧
3. **[spec-reference-validation-pattern.md](./spec-reference-validation-pattern.md)** → 建立质量保障流程
4. **[best-practices.md](./best-practices.md)** → 持续优化写作质量

---

## 与规则体系的关联

本模式库被以下规则文件引用：

- `.agents/rules/spec-writing-guide/08-prd-format-overview.md` → PRD格式概述，引用format-selection-guide
- `.agents/rules/spec-writing-guide/09-prd-template-reference.md` → PRD模板引用，链接到universal-prd-template

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0 | 2026-07-09 | 初始版本，索引7份Spec工作流相关文档 |
| 1.1 | 2026-07-09 | 添加Dogfooding自验证状态记录，模板v1.1发布 |
| 1.2 | 2026-07-09 | 新增spec-mode-verification-gates.md模式（Spec Mode+验证门禁双保险工作流，从best-practices目录断链修复复盘洞察归档） |
| 1.3 | 2026-07-10 | spec-mode-verification-gates升级至v1.1 L2（3次验证）：补充80%验收标准测试量化决策标准、三类适用场景划分（高ROI/需调整/不适用）、探索性任务弹性使用指导、三次验证对比表 |
