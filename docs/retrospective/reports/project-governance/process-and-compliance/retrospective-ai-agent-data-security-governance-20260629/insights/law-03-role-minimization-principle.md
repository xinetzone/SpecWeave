+++
id = "law-role-minimization-principle"
date = "2026-06-29"
type = "insight"
scope = "role-design,raci,governance-organization"
source = "../insight-extraction.md#洞察3不新增角色原则优先扩展而非新增"
archived_to = "docs/retrospective/patterns/methodology-patterns/governance-strategy/role-minimization-principle.md"
+++

# 规律3："不新增角色"原则——优先扩展而非新增

→ 正式模式：[role-minimization-principle.md](../../../../../patterns/methodology-patterns/governance-strategy/role-minimization-principle.md)（L1，首次显式提炼）

## 事件事实

Spec中Open Questions提出"是否需要建立专门的数据安全官（DSO）角色"，最终决定不新增独立角色，而是通过RACI矩阵将数据安全职责扩展到现有5个角色（orchestrator、architect、developer、reviewer、tester）+ co-founder。

## 新增角色三问题分析

新增角色看似"职责清晰"，但会带来三个问题：

1. **角色膨胀**：每新增一个治理维度就新增角色，最终角色体系庞大难以维护
2. **职责灰色地带**：新角色与现有角色的边界需要重新定义，容易出现职责重叠或真空
3. **认知负担**：智能体需要加载更多角色定义，上下文窗口被角色描述占据

## 判断标准

治理体系建设中应遵循"角色最小化"原则——优先通过RACI矩阵扩展现有角色职责，而非新增角色。

**新增角色判断标准**：只有当某项职责完全无法被现有角色覆盖（需要完全不同的能力模型和决策权限）时，才考虑新增角色。

**经验法则**：如果某个角色80%的职责都可以映射到现有角色，就不应该新增。

## 适用边界

- 适用于治理体系建设初期的角色设计
- 当治理领域高度专业化（如财务审计、法律合规）且现有角色无相关能力时，可考虑新增
- 与RACI矩阵配合使用：先尝试RACI分配，无法分配时再考虑新增角色

## 关联洞察

- [law-01-five-layer-governance-architecture.md](law-01-five-layer-governance-architecture.md) — 五层架构的组织保障层对应角色设计
- [law-05-governance-building-five-steps.md](law-05-governance-building-five-steps.md) — 五步法步骤⑤集成验证中的角色验证环节

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
