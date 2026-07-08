---
id: "templates-task-template"
title: "任务模板"
source: "AGENTS.md#模板"
x-toml-ref: "../../.meta/toml/.agents/templates/task-template.toml"
version: "1.2.0"
patterns_applied: ["spec-driven-development", "three-tier-governance", "context-recovery-protocol"]
---
# 任务模板

> **L3标准化模式集成**：本模板已应用以下L3标准化模式——
> - [spec-driven-development](../../docs/retrospective/patterns/methodology-patterns/creative-design/spec-driven-development.md)：Spec驱动开发，非平凡任务先写spec再执行
> - [three-tier-governance](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)：三层治理闭环，验收包含自动化验证
> - [context-recovery-protocol](../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/context-recovery-protocol.md)：上下文恢复协议，保障任务上下文完整性

## 任务描述

```
任务名称: {任务名称}
任务类型: {feature/bugfix/refactor/test/docs}
优先级: {high/medium/low}
负责人: {角色 ID}
组ID: {group-id，同组任务将合并执行；单独执行填"N/A"}
Spec状态: {已完成/待编写/不适用（简单任务<3文件变更）}
预探索状态: {已完成/待执行/不适用（小型任务<5个分析对象）}
```

### 任务分组规则（group-id 说明）

同组任务（相同 group-id）将在同一次子代理调用中合并执行。合并判断标准：
- **输入源重叠度 > 60%**：多个任务的输入文件/目录/URL有显著重叠
- **输出可自然融合**：任务产出可以合并到同一文档或输出物中
- **合并后输出量 < 上下文窗口60%**：合并后的总输出不会超过子代理上下文窗口的60%

单独执行的任务 group-id 填 "N/A"。

### Pre-flight预探索阶段（中大规模任务必须）

对于中型（5-10个分析对象）和大型（>10个分析对象）任务，在任务分解后、子代理执行前，必须执行Pre-flight预探索阶段：

**目的**：减少子代理重复探索成本，提升并行执行效率（预计节省15-20%时间）

**执行方式**：主控代理一次性完成所有分析对象的结构概览（文档站点sitemap/目录结构、代码仓库顶层目录/核心入口文件路径），将预探索结果作为共享上下文注入所有子代理prompt

**输出物**：preflight-exploration.md（按 [preflight-exploration-template.md](preflight-exploration-template.md) 格式）

**触发条件**：
| 任务规模 | 是否触发预探索 |
|---------|--------------|
| 小型（<5个分析对象） | 不适用，跳过 |
| 中型（5-10个分析对象） | 推荐 |
| 大型（>10个分析对象） | 必须 |

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
