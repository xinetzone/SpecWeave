+++
id = "architecture-priority-export-knowledge-paths"
date = "2026-06-30"
type = "export-knowledge-paths"
source = "export-suggestions.md#二知识沉淀路径"
+++

# 二、知识沉淀路径

## 应更新的现有文档

| 目标文档 | 更新内容 | 优先级 | 状态 |
|---------|---------|--------|------|
| .agents/README.md | 在路线图中加入架构重构 P0 模块规划 | P0 | 📋 待更新 |
| .agents/rules/skill-development.md | 补充「命令集Skill化」「脚本Skill化」规范 | P1 | 📋 待更新 |
| docs/retrospective/patterns/README.md | 新增架构模式索引（P-ARCH-001至P-ARCH-006） | P1 | 📋 待更新 |
| docs/retrospective/assets/asset-inventory.md | 登记本报告为知识资产 | P2 | 📋 待更新 |

## 应新建的文档（P0模块实施时创建）

> **说明**：以下为实施时实际创建的文档，路径以实际落地为准。

| 计划文档 | 实际文档 | 所属模块 | 状态 |
|--------|---------|---------|------|
| .agents/capabilities/ONBOARDING.md | .agents/capabilities/README.md + ONBOARDING-TEMPLATE.md | P0模块1（能力注册中心） | ✅ 已创建 |
| .agents/capabilities/REGISTRY.md | .agents/capabilities/REGISTRY-TEMPLATE.md + .agents/capability-registry.md | P0模块1（能力注册中心） | ✅ 已创建 |
| .agents/skills/retrospective/SKILL.md | .agents/skills/retrospective-cmd/SKILL.md | P0模块2（高频指令集SKILL化） | ✅ 已创建 |
| .agents/skills/insight/SKILL.md | .agents/skills/insight-cmd/SKILL.md | P0模块2 | ✅ 已创建 |
| .agents/skills/atomization/SKILL.md | .agents/skills/atomization-cmd/SKILL.md | P0模块2 | ✅ 已创建 |
| .agents/skills/export-report/SKILL.md | .agents/skills/export-report-cmd/SKILL.md | P0模块2 | ✅ 已创建 |
| .agents/skills/atomic-commit/SKILL.md | .agents/skills/atomic-commit-cmd/SKILL.md | P0模块2 | ✅ 已创建 |
| .agents/protocols/agent-onboarding.md | .agents/protocols/onboarding-protocol.md | P0模块3（Onboarding协议） | ✅ 已创建 |
| .agents/capabilities/ARCHITECTURE.md | .agents/capabilities/ARCHITECTURE.md（v1.1.0，L2成熟度） | P0模块1（三层架构规范） | ✅ 已创建 |

## Spec 生命周期路径

| 阶段 | 位置 | 说明 |
|------|------|------|
| 开发中（不成熟） | `.trae/specs/<theme>/<spec-name>/` | Spec工作区，含spec.md、tasks.md、checklist.md |
| 成熟归档 | `.agents/` 对应子目录 | commands/、rules/、protocols/、capabilities/、skills/、roles/等，按类型归档 |

P0模块1的实施未在 `.trae/specs/` 下创建独立Spec（直接通过复盘→行动→实施完成），后续模块应遵循Spec生命周期：先在 `.trae/specs/` 建Spec，成熟实施后归档到 `.agents/`。
