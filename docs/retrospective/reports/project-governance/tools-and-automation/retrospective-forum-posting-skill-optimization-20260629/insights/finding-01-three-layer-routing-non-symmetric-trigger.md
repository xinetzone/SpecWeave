---
id: "finding-three-layer-routing-non-symmetric-trigger"
source: "../insight-extraction.md#发现1三层路由的非对称触发陷阱"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/finding-01-three-layer-routing-non-symmetric-trigger.toml"
---
# 发现1：三层路由的"非对称触发"陷阱

→ 落地措施：AGENTS.md启动协议增加步骤2.0（任务类型预检）+ vendor方法论资产映射表  
→ 关联模式：[task-type-first-indexing.md](../../../../../patterns/methodology-patterns/governance-strategy/task-type-first-indexing.md)（任务类型优先索引）

## 事件发现

工作目录在 SpecWeave 根目录（`.agents/skills/`）时，容易认为"不需要进入 vendor"，从而错过 vendor 子模块中的成熟方法论资产。

本次任务中，工作目录在根目录 `.agents/skills/forum-posting/`，但 vendor/flexloop/apps/chaos 中的 skill-creator 才是该任务类型最权威的方法论来源。初始优化时未读取vendor资产，导致v1.0.x版本虽然做对了双方案和JS函数，但description存在undertrigger、缺乏Why解释、没有决策树。

## 根因分析

AGENTS.md 中三层路由的触发条件原描述为"若任务工作目录位于 vendor/ 内"，这导致一个反向盲区：**工作目录不在 vendor/ 内，但任务类型需要 vendor 资产的场景**，没有被显式覆盖。

## 深层含义

三层路由应该是**任务类型驱动**而非仅**工作目录驱动**。当任务涉及"创建/优化 skill"、"子模块协同"等类型时，无论当前工作目录在哪里，都需要主动检查 vendor 区域是否有对应规范或技能。

## 落地措施

1. AGENTS.md启动协议增加**步骤2.0（任务类型预检）**：无论工作目录是否在vendor/内，先检查任务类型是否命中vendor方法论资产
2. 增加vendor方法论资产映射表，按任务类型显式列出需要路由到vendor的场景
3. vendor/AGENTS.md增加"按任务类型索引"章节，零摩擦命中正确资产

## 关联洞察

- [meta-05-availability-heuristic-structural-guard.md](meta-05-availability-heuristic-structural-guard.md) — "就近直觉"是系统性认知偏差
- [law-02-three-layer-routing-task-type-precheck.md](law-02-three-layer-routing-task-type-precheck.md) — 任务类型预检补充流程
- [meta-02-nonlinear-correction-cost.md](meta-02-nonlinear-correction-cost.md) — 路由违规的非线性返工成本

---
*来源：[forum-posting Skill优化复盘](../README.md)*
