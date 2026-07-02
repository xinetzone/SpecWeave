---
id: "architecture-priority-export-knowledge-paths"
title: "二、知识沉淀路径"
source: "export-suggestions.md#二知识沉淀路径"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-architecture-priority-20260629/export/knowledge-paths.toml"
---
# 二、知识沉淀路径

## 应更新的现有文档

| 目标文档 | 更新内容 | 优先级 | 状态 |
|---------|---------|--------|------|
| .agents/README.md | 在路线图中加入架构重构 P0 模块规划 | P0 | ✅ 已更新（标注Skill发现协议P0实施） |
| .agents/rules/skill-development.md | 补充「命令集Skill化」「脚本Skill化」规范 | P1 | ✅ 已更新（五要素模型、双方案模式、资产盘点、验证清单） |
| docs/retrospective/patterns/README.md | 新增架构模式索引（P-ARCH-001至P-ARCH-006） | P1 | ✅ 已更新（6个模式全部入库，统计自动更新） |
| docs/retrospective/assets/asset-inventory.md | 登记本报告为知识资产 | P2 | ⏳ 待更新 |

## 应新建的文档（P0模块实施时创建）

| 计划文档 | 实际文档 | 所属模块 | 状态 |
|--------|---------|---------|------|
| .agents/capabilities/ONBOARDING.md | [.agents/ONBOARDING.md](../../../../../../.agents/ONBOARDING.md) | P0模块1（能力注册中心） | ✅ 已创建 |
| .agents/capabilities/REGISTRY.md | [.agents/capability-registry.md](../../../../../../.agents/capability-registry.md) | P0模块1（能力注册中心） | ✅ 已创建 |
| .agents/skills/retrospective/SKILL.md | [.agents/skills/retrospective-cmd/SKILL.md](../../../../../../.agents/skills/retrospective-cmd/SKILL.md) | P0模块2（高频指令集SKILL化） | ✅ 已创建 |
| .agents/skills/insight/SKILL.md | [.agents/skills/insight-cmd/SKILL.md](../../../../../../.agents/skills/insight-cmd/SKILL.md) | P0模块2 | ✅ 已创建 |
| .agents/skills/atomization/SKILL.md | [.agents/skills/atomization-cmd/SKILL.md](../../../../../../.agents/skills/atomization-cmd/SKILL.md) | P0模块2 | ✅ 已创建 |
| .agents/skills/export-report/SKILL.md | [.agents/skills/export-report-cmd/SKILL.md](../../../../../../.agents/skills/export-report-cmd/SKILL.md) | P0模块2 | ✅ 已创建 |
| .agents/skills/atomic-commit/SKILL.md | [.agents/skills/atomic-commit-cmd/SKILL.md](../../../../../../.agents/skills/atomic-commit-cmd/SKILL.md) | P0模块2 | ✅ 已创建 |
| .agents/skills/mermaid/SKILL.md | [.agents/skills/mermaid-cmd/SKILL.md](../../../../../../.agents/skills/mermaid-cmd/SKILL.md) | P0模块2（计划外新增） | ✅ 已创建 |
| .agents/protocols/agent-onboarding.md | [.agents/protocols/onboarding-protocol.md](../../../../../../.agents/protocols/onboarding-protocol.md) | P0模块3（Onboarding协议） | ✅ 已创建 |
| .agents/capabilities/ARCHITECTURE.md | [.agents/capabilities/ARCHITECTURE.md](../../../../../../.agents/capabilities/ARCHITECTURE.md) | P0模块1（三层架构规范） | ✅ 已创建（v1.1.0，L2成熟度） |
| .agents/capabilities/README.md | [.agents/capabilities/README.md](../../../../../../.agents/capabilities/README.md) | P0模块1 | ✅ 已创建 |
| .agents/capabilities/ONBOARDING-TEMPLATE.md | [.agents/capabilities/ONBOARDING-TEMPLATE.md](../../../../../../.agents/capabilities/ONBOARDING-TEMPLATE.md) | P0模块1 | ✅ 已创建 |
| .agents/capabilities/REGISTRY-TEMPLATE.md | [.agents/capabilities/REGISTRY-TEMPLATE.md](../../../../../../.agents/capabilities/REGISTRY-TEMPLATE.md) | P0模块1 | ✅ 已创建 |

## P1模块新建文档（第一批脚本Skill化）

| 实际文档 | 所属模块 | 状态 |
|---------|---------|------|
| [.agents/skills/link-check-cmd/SKILL.md](../../../../../../.agents/skills/link-check-cmd/SKILL.md) | P1模块5（高频脚本Skill化） | ✅ 已创建 |
| [.agents/skills/docgen-cmd/SKILL.md](../../../../../../.agents/skills/docgen-cmd/SKILL.md) | P1模块5 | ✅ 已创建 |
| [.agents/skills/ci-check-cmd/SKILL.md](../../../../../../.agents/skills/ci-check-cmd/SKILL.md) | P1模块5 | ✅ 已创建 |
| [.agents/skills/atomization-finalize-cmd/SKILL.md](../../../../../../.agents/skills/atomization-finalize-cmd/SKILL.md) | P1模块5 | ✅ 已创建 |
| [.agents/skills/check-duplication-cmd/SKILL.md](../../../../../../.agents/skills/check-duplication-cmd/SKILL.md) | P1模块5 | ✅ 已创建 |

## 模式沉淀路径

| 模式 | 沉淀位置 | 状态 |
|------|---------|------|
| P-ARCH-001 渐进式披露架构 | [.agents/capabilities/ARCHITECTURE.md](../../../../../../.agents/capabilities/ARCHITECTURE.md)（L2正式规范） | ✅ 已沉淀 |
| P-ARCH-002 Markdown即接口 | [docs/retrospective/patterns/methodology-patterns/ai-collaboration/markdown-as-interface.md](../../../../patterns/methodology-patterns/ai-collaboration/markdown-as-interface.md) | ✅ 已沉淀 |
| P-ARCH-003 瓶颈优先重构法 | [docs/retrospective/patterns/methodology-patterns/governance-strategy/bottleneck-first-refactoring.md](../../../../patterns/methodology-patterns/governance-strategy/bottleneck-first-refactoring.md) | ✅ 已沉淀 |
| P-ARCH-004 不重构清单 | [docs/retrospective/patterns/methodology-patterns/governance-strategy/no-touch-list.md](../../../../patterns/methodology-patterns/governance-strategy/no-touch-list.md) | ✅ 已沉淀 |
| P-ARCH-005 架构决策三角验证 | [docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md](../../../../patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md) | ✅ 已沉淀 |
| P-ARCH-006 元能力依赖倒置 | [docs/retrospective/patterns/architecture-patterns/meta-capability-inversion.md](../../../../patterns/architecture-patterns/meta-capability-inversion.md) | ✅ 已沉淀 |

## Spec 生命周期路径

| 阶段 | 位置 | 说明 |
|------|------|------|
| 开发中（不成熟） | `.trae/specs/<theme>/<spec-name>/` | Spec工作区，含spec.md、tasks.md、checklist.md |
| 成熟归档 | `.agents/` 对应子目录 | commands/、rules/、protocols/、capabilities/、skills/、roles/等，按类型归档 |

P0模块1的实施未在 `.trae/specs/` 下创建独立Spec（直接通过复盘→行动→实施完成），后续模块应遵循Spec生命周期：先在 `.trae/specs/` 建Spec，成熟实施后归档到 `.agents/`。
