---
id: "rules-stage-guardrails"
title: "开发流程阶段守卫规则"
source: "AGENTS.md#规则体系"
x-toml-ref: "../../.meta/toml/.agents/rules/stage-guardrails.toml"
---
# 开发流程阶段守卫规则

本规则定义功能开发流程的标准阶段序列、每个阶段的操作边界、跨阶段拦截机制与阶段跳转审批流程。所有智能体在执行开发任务时必须遵守本规则，确保在正确的阶段做正确的事。

## 文档导航

| 文档 | 内容 |
|------|------|
| [01 核心原则与治理基建模型](stage-guardrails/01-principles-governance.md) | 核心原则 + 治理基建四层递进模型（B1→B2→C1→C2） |
| [02 标准阶段序列](stage-guardrails/02-standard-stages.md) | 标准8阶段序列（流程图 + 概览表） |
| [03 各阶段操作边界](stage-guardrails/03-stage-boundaries.md) | 各阶段①-⑧操作边界（允许/禁止/正例/反例） |
| [04 跨阶段拦截与跳转审批](stage-guardrails/04-interception-approval.md) | 跨阶段拦截机制 + 阶段跳转审批流程 + L0 探针豁免规则 |
| [05 关键节点日志规范](stage-guardrails/05-logging-spec.md) | 关键节点结构化日志输出规范（格式/事件枚举/模板） |

---

## 相关模式

- [三层检查工具模式](../../docs/retrospective/patterns/code-patterns/three-tier-check-tool.md)
- [Spec即代码自动门禁](../../docs/retrospective/patterns/methodology-patterns/tools-automation/spec-as-code-automated-gates.md)
- [豁免机制合法化](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/exemption-mechanism-legalization.md)——L0 探针豁免规则的设计方法论
- [L0-L3 流程分级示例模板](../templates/l0-l3-process-tier-template.md)——L0 探针豁免规则的来源与完整定义
