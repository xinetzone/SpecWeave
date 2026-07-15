---
id: "workflows-feature-development"
title: "功能开发流程"
source: "AGENTS.md#标准工作流"
x-toml-ref: "../../.meta/toml/.agents/workflows/feature-development.toml"
---
# 功能开发流程

---
id: "workflows-feature-development"
title: "功能开发流程"
source: "AGENTS.md#标准工作流"
x-toml-ref: "../../.meta/toml/.agents/workflows/feature-development.toml"
---
# 功能开发流程

本流程定义功能开发的标准阶段序列、角色参与、变更类型分类与执行要点。所有开发任务必须遵循本流程，并遵守阶段守卫规则和前置文档强制读取协议。

## 文档导航

| 文档 | 内容 |
|------|------|
| [01 变更类型判定与流程概览](feature-development/01-change-type-overview.md) | 变更类型判定（新功能/扩展/重构）+ 三种流程图 + 角色参与矩阵 |
| [02 新功能完整流程（8步）](feature-development/02-new-feature-flow.md) | 新功能完整8步流程详解（需求→设计→分配→实现→测试→审查→合并→确认） |
| [03 功能扩展轻量流程（6步）](feature-development/03-extension-flow.md) | 功能扩展轻量6步流程（影响分析→增量方案→实现→回归→审查→合并） |
| [04 功能重构重量流程（7步）](feature-development/04-refactoring-flow.md) | 功能重构重量7步流程（全量评估→方案重审→重规划→迁移实现→全量回归→双重审查→合并） |
| [05 治理规则引用](feature-development/05-governance-references.md) | 治理规则引用（阶段守卫/PDR/交接/硬编码治理） |
| [06 结构化日志与交接协议](feature-development/06-logging-handoff.md) | 结构化日志输出要求（SG-LOG/PDR-LOG格式+合规要求）+ 交接协议 |

---

## 相关模式

- [学习-验证-采用](../docs/retrospective/patterns/methodology-patterns/governance-strategy/learn-validate-adopt.md)
- [两阶段处理](../docs/retrospective/patterns/methodology-patterns/document-architecture/two-phase-processing.md)
