---
id: "templates-task-template"
title: "任务模板"
source: "AGENTS.md#模板"
x-toml-ref: "../../.meta/toml/.agents/templates/task-template.toml"
version: "1.1.0"
patterns_applied: ["spec-driven-development", "three-tier-governance"]
---
# 任务模板

> **L3标准化模式集成**：本模板已应用以下L3标准化模式——
> - [spec-driven-development](../../docs/retrospective/patterns/methodology-patterns/creative-design/spec-driven-development.md)：Spec驱动开发，非平凡任务先写spec再执行
> - [three-tier-governance](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)：三层治理闭环，验收包含自动化验证

## 任务描述

```
任务名称: {任务名称}
任务类型: {feature/bugfix/refactor/test/docs}
优先级: {high/medium/low}
负责人: {角色 ID}
Spec状态: {已完成/待编写/不适用（简单任务<3文件变更）}
```

## 验收标准

```
- [ ] 标准 1: {描述}
- [ ] 标准 2: {描述}
- [ ] 标准 3: {描述}
- [ ] 自动化验证: {check-links/check-frontmatter/其他脚本验证，或"人工检查"}
```

## 依赖项

```
- 依赖任务: {任务 ID 或无}
- 依赖资源: {资源描述或无}
- 关联Spec: {spec路径或无，非平凡任务必须关联}
```

## 任务上下文

```
背景说明: {任务背景}
相关文件: {文件列表}
风险提示: {风险描述}
遵循模式: {应用的L3模式，如"入口精简+零依赖+三层治理验证"}
```
