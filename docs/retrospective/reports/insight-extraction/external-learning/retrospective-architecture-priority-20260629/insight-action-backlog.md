---
title: 架构优先级评估复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/insight-action-backlog.toml"
project: retrospective-architecture-priority-20260629
template_upgrade: 2026-07-06 v1.2
ssot:
  suggestions_source: export-suggestions.md → export/action-items.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。P0+P1+P2模块6已完成，其余P2/P3项待触发条件满足后实施。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 行动建议§已完成 | 复盘原子化完成 | 高 | ✅ 已完成 | 执行复盘原子化拆分，完成所有原子文件 | 2026-06-29 |
| IMP-002 | 行动建议§已完成 | P0模块1：能力注册中心创建 | 高 | ✅ 已完成 | .agents/capabilities/目录创建，含ARCHITECTURE.md/ONBOARDING-TEMPLATE.md/REGISTRY-TEMPLATE.md/README.md，.agents/ONBOARDING.md和.capability-registry.md创建 | 2026-06-30 |
| IMP-003 | 行动建议§已完成 | P0模块2：6个指令集SKILL化 | 高 | ✅ 已完成 | atomic-commit-cmd/atomization-cmd/retrospective-cmd/insight-cmd/export-report-cmd/mermaid-cmd六个SKILL创建完成 | 2026-06-30 |
| IMP-004 | 行动建议§已完成 | skill-development.md规范补充 | 中 | ✅ 已完成 | 补充指令集和脚本Skill化五要素模型、双方案模式、资产盘点、验证清单等规范 | 2026-06-30 |
| IMP-005 | 行动建议§已完成 | P0模块3：Agent Onboarding协议 | 高 | ✅ 已完成 | .agents/protocols/onboarding-protocol.md创建 | 2026-06-30 |
| IMP-006 | 行动建议§已完成 | 6个可复用模式沉淀到模式库 | 中 | ✅ 已完成 | P-ARCH-001到P-ARCH-006共6个模式全部沉淀至对应正式位置 | 2026-06-30 |
| IMP-007 | 行动建议§已完成 | P1：第一批5个高频脚本Skill化 | 高 | ✅ 已完成 | link-check-cmd/docgen-cmd/ci-check-cmd/atomization-finalize-cmd/check-duplication-cmd五个SKILL创建完成 | 2026-07-01 |
| IMP-008 | 行动建议§已完成 | 质量保障（计划外增量） | 高 | ✅ 已完成 | 282个单元测试、20个性能基准、6处Windows编码修复、YAML注释规则Bug修复 | 2026-07-01 |
| IMP-009 | 行动建议§已完成 | P2模块6：规范分层治理 | 中 | ✅ 已完成 | .agents/README.md明确Core/Tools双层治理模型，含6维度分层原则、18个目录归属、6条跨层引用规则、6题边界判定清单 | 2026-07-01 |
| IMP-010 | 行动建议§待执行 | P2模块7：模型路由层 | 中 | ⏳ 待执行 | 多模型API可用时，SKILL.md frontmatter增加model_hint字段(fast/balanced/precise) | - |
| IMP-011 | 行动建议§待执行 | P2模块8：资源调度框架 | 中 | ⏳ 待执行 | 多Agent并发场景落地时，实施self-management资源分配 | - |
| IMP-012 | 行动建议§待执行 | 第二批脚本Skill化 | 中 | ⏳ 待执行 | 根据使用频率评估优先级，封装下一批高频脚本 | - |
| IMP-013 | 行动建议§待执行 | P3：REGISTRY自动生成 | 低 | ⏳ 待执行 | SKILL数量超20个时，用docgen聚合frontmatter自动生成REGISTRY | - |
| IMP-014 | 行动建议§待执行 | P3：asset-inventory登记 | 低 | ⏳ 待执行 | 下次资产盘点时登记本报告为知识资产 | - |

## 行动项详情

### IMP-001: 复盘原子化完成
- **优先级**: 高
- **执行结果**: 完成本次复盘原子化拆分，建立execution/、insights/、export/等原子化目录结构
- **产出物**: execution-retrospective.md、insight-extraction.md、export-suggestions.md及各原子子目录文件
- **提交**: 2026-06-29完成

---

### IMP-002: P0模块1：能力注册中心创建
- **优先级**: 高
- **执行结果**: 创建.agents/capabilities/目录（ARCHITECTURE.md、ONBOARDING-TEMPLATE.md、REGISTRY-TEMPLATE.md、README.md）+.agents/ONBOARDING.md+.agents/capability-registry.md
- **产出物**: [.agents/capabilities/](../../../../../../.agents/capabilities/)、[ONBOARDING.md](../../../../../../.agents/ONBOARDING.md)
- **提交**: 2026-06-30完成

---

### IMP-003: P0模块2：6个指令集SKILL化
- **优先级**: 高
- **执行结果**: 完成atomic-commit-cmd、atomization-cmd、retrospective-cmd、insight-cmd、export-report-cmd、mermaid-cmd共6个指令集SKILL创建（含原计划5个+mermaid-cmd补充）
- **产出物**: [.agents/skills/](../../../../../../.agents/skills/)下6个-cmd后缀SKILL目录
- **提交**: 2026-06-30完成

---

### IMP-004: skill-development.md规范补充
- **优先级**: 中
- **执行结果**: 补充指令集和脚本Skill化的具体规范，包括五要素模型、双方案模式、资产盘点、验证清单等
- **产出物**: [skill-development.md](../../../../../../.agents/rules/skill-development.md)
- **提交**: 2026-06-30完成

---

### IMP-005: P0模块3：Agent Onboarding协议
- **优先级**: 高
- **执行结果**: 创建.agents/protocols/onboarding-protocol.md，将PDR从强制全量读取升级为渐进式按需加载
- **产出物**: [onboarding-protocol.md](../../../../../../.agents/protocols/onboarding-protocol.md)
- **提交**: 2026-06-30完成

---

### IMP-006: 6个可复用模式沉淀到模式库
- **优先级**: 中
- **执行结果**: P-ARCH-001到P-ARCH-006共6个模式全部沉淀至对应正式位置
- **产出物**: 
  - [ARCHITECTURE.md](../../../../../../.agents/capabilities/ARCHITECTURE.md)（P-ARCH-001）
  - [markdown-as-interface.md](../../../../patterns/methodology-patterns/ai-collaboration/markdown-as-interface.md)（P-ARCH-002）
  - [bottleneck-first-refactoring.md](../../../../patterns/methodology-patterns/governance-strategy/bottleneck-first-refactoring.md)（P-ARCH-003）
  - [no-touch-list.md](../../../../patterns/methodology-patterns/governance-strategy/no-touch-list.md)（P-ARCH-004）
  - [triangular-source-verification.md](../../../../patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md)（P-ARCH-005）
  - [meta-capability-inversion.md](../../../../patterns/architecture-patterns/meta-capability-inversion.md)（P-ARCH-006）
- **提交**: 2026-06-30完成

---

### IMP-007: P1：第一批5个高频脚本Skill化
- **优先级**: 高
- **执行结果**: link-check-cmd、docgen-cmd、ci-check-cmd、atomization-finalize-cmd、check-duplication-cmd五个脚本SKILL创建完成，通过check-skill-quality.py质量门验证
- **产出物**: [.agents/skills/](../../../../../../.agents/skills/)下5个脚本SKILL目录
- **提交**: 2026-07-01完成

---

### IMP-008: 质量保障（计划外增量）
- **优先级**: 高
- **执行结果**: 补充282个单元测试（含50个CLI边界测试）、20个性能基准测试、修复6处Windows编码兼容性问题、修复YAML frontmatter注释规则Bug
- **产出物**: 测试用例、编码兼容性防御性改进
- **提交**: 2026-07-01完成

---

### IMP-009: P2模块6：规范分层治理
- **优先级**: 中
- **执行结果**: 在.agents/README.md中明确Core/Tools双层治理模型，定义6维度分层原则、15个Core目录+3个Tools目录归属、6条跨层引用规则、6题边界判定清单、三层正交关系说明、目录树图标注[Core]/[Tools]标记
- **产出物**: [.agents/README.md](../../../../../../.agents/README.md)
- **提交**: 2026-07-01完成

---

### IMP-010: P2模块7：模型路由层
- **优先级**: 中
- **状态**: ⏳ 待执行
- **触发条件**: 多模型API可用时
- **DoD**: SKILL.md frontmatter增加model_hint字段(fast/balanced/precise)，Agent根据任务类型选择推理策略

---

### IMP-011: P2模块8：资源调度框架
- **优先级**: 中
- **状态**: ⏳ 待执行
- **触发条件**: 多Agent并发场景落地时
- **DoD**: 实施self-management资源分配能力，支持多Agent任务优先级调度

---

### IMP-012: 第二批脚本Skill化
- **优先级**: 中
- **状态**: ⏳ 待执行
- **触发条件**: 根据实际使用频率重新评估优先级
- **DoD**: 封装下一批高频脚本（check-spec-consistency.py、generate-nav.py、build-ref-index.py等）

---

### IMP-013: P3：REGISTRY自动生成
- **优先级**: 低
- **状态**: ⏳ 待执行
- **触发条件**: SKILL数量超过20个手动维护困难时
- **DoD**: 用docgen聚合SKILL frontmatter自动生成REGISTRY.md

---

### IMP-014: P3：asset-inventory登记
- **优先级**: 低
- **状态**: ⏳ 待执行
- **触发条件**: 下次资产盘点时
- **DoD**: 登记本报告为知识资产

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001 | 2026-06-29 | 原子化拆分 | 复盘原子化完成，建立完整目录结构 |
| IMP-002~006 | 2026-06-30 | P0模块并行实施 | P0三个模块+skill规范+6个模式沉淀全部完成 |
| IMP-007~009 | 2026-07-01 | P1模块+质量+P2模块6 | 第一批脚本Skill化、质量保障、规范分层治理完成 |
| IMP-010~014 | - | - | 待触发条件满足后实施 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级：从export/action-items.md迁移行动项至独立backlog文件
