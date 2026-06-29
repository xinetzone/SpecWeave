+++
id = "law-three-layer-routing-task-type-precheck"
date = "2026-06-29"
type = "insight"
scope = "three-layer-routing,task-type-precheck,vendor,protocol"
source = "../insight-extraction.md#规律2三层路由协议的任务类型预检补充"
archived_to = "AGENTS.md步骤2.0任务类型预检, task-type-first-indexing模式"
+++

# 规律2：三层路由协议的"任务类型预检"补充

→ 落地措施：AGENTS.md启动协议增加步骤2.0；vendor/AGENTS.md增加按任务类型索引章节  
→ 关联模式：[task-type-first-indexing.md](../../../../../patterns/methodology-patterns/governance-strategy/task-type-first-indexing.md)

## 核心规律

三层路由不应仅由"工作目录是否在 vendor/ 内"触发，还应增加**任务类型预检**步骤，无论工作目录在哪里，只要任务类型命中vendor方法论资产，就必须主动检查vendor路由。

## 修正后的路由流程

```
收到任务 → 检查AGENTS.md全局路由表
  ├─ 步骤2.0（必做）：任务类型预检
  │    ├─ 任务类型命中vendor方法论资产？（如Skill创建/优化、跨项目子模块协同）
  │    │    └─ 是 → 读取对应vendor规范
  │    └─ 否 → 继续
  ├─ 工作目录在 vendor/ 内？ → 是 → 执行嵌套路由（vendor→flexloop→...）
  └─ 工作目录不在 vendor/ 内？→ 按根目录规范执行
```

## vendor区域常见任务类型映射

| 任务类型 | vendor资产路径 |
|---------|---------------|
| Skill 创建/优化 | vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md |
| Skill目录结构规范 | vendor/flexloop/apps/chaos/.agents/rules/skills.md |
| 跨项目子模块协同 | docs/knowledge/VENDOR-INTEGRATION.md + vendor/AGENTS.md |

## 为什么必须这样做？

"工作目录驱动"的路由会导致**反向盲区**：当工作目录在根目录时，Agent容易产生"就近直觉"，只读取当前目录下的规范，而忽略vendor子模块中更权威的方法论资产。任务类型预检是对抗这种认知偏差的结构性机制。

## 关联洞察

- [finding-01-three-layer-routing-non-symmetric-trigger.md](finding-01-three-layer-routing-non-symmetric-trigger.md) — 非对称触发陷阱
- [meta-05-availability-heuristic-structural-guard.md](meta-05-availability-heuristic-structural-guard.md) — 可得性启发的结构性防范
- [meta-02-nonlinear-correction-cost.md](meta-02-nonlinear-correction-cost.md) — 路由违规的非线性成本

---
*来源：[forum-posting Skill优化复盘](../README.md)*
