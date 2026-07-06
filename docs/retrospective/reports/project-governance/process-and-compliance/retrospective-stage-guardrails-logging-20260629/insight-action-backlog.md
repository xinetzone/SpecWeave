---
title: 开发流程阶段守卫机制落地迭代复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "comprehensive-retrospective-template/insight-action-backlog.md"
project: retrospective-stage-guardrails-logging-20260629
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---

# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本次项目已完成阶段守卫机制落地和结构化日志规范，剩余改进项待后续执行。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 项目交付 | 阶段守卫规则stage-guardrails.md交付 | 高 | ✅ 已完成 | 8阶段定义、操作边界、拦截标准、审批流程、[SG-LOG]规范 | 2026-06-29 |
| IMP-002 | 项目交付 | 前置文档读取协议pre-document-reading.md交付 | 高 | ✅ 已完成 | 角色×阶段必读矩阵、确认机制、[PDR-LOG]规范 | 2026-06-29 |
| IMP-003 | 项目交付 | 功能开发工作流增强feature-development.md | 高 | ✅ 已完成 | 三路径分类（新功能/扩展/重构）、变更判定决策树 | 2026-06-29 |
| IMP-004 | 项目交付 | 5角色Non-Goals更新 | 高 | ✅ 已完成 | orchestrator/developer/architect/tester/reviewer补充阶段守卫约束 | 2026-06-29 |
| IMP-005 | 项目交付 | check-stage-guardrails.py日志分析脚本 | 高 | ✅ 已完成 | 12+种异常检测，支持--demo/--json | 2026-06-29 |
| IMP-006 | 知识更新 | AGENTS.md上下文路由表更新 | 高 | ✅ 已完成 | 日志规范+check脚本入口同步更新 | 2026-06-29 |
| IMP-007 | 知识更新 | 全局看板更新 | 高 | ✅ 已完成 | roles-governance 5/5完成 | 2026-06-29 |
| IMP-008 | P0-A1 | 萃取规则落地三层模型模式 | P0 | ⏳ 待萃取 | three-layer-rule-enforcement入库governance-strategy/ | - |
| IMP-009 | P0-A2 | 萃取结构化轻量日志模式 | P0 | ⏳ 待萃取 | structured-lightweight-logging入库code-patterns/ | - |
| IMP-010 | P0-A3 | 配置.gitattributes统一换行符 | P0 | ⏳ 待执行 | 创建.gitattributes，设置* text=auto，*.md text eol=lf | - |
| IMP-011 | P1-B1 | check-stage-guardrails.py集成到CI | P1 | ⏳ 待规划 | ci-check.ps1/sh增加阶段守卫日志检查步骤 | - |
| IMP-012 | P1-B2 | 添加--strict模式 | P1 | ⏳ 待规划 | strict模式下WARN返回非零退出码用于CI门禁 | - |
| IMP-013 | P1-B3 | spec模板增加"可观测性需求" | P1 | ⏳ 待规划 | spec模板强制要求考虑日志/验证 | - |
| IMP-014 | P2-C1 | 阶段守卫运行时强制执行 | P2 | 💡 远期规划 | 装饰器/中间件层实时检查阶段权限 | - |
| IMP-015 | P2-C2 | 日志聚合仪表盘 | P2 | 💡 远期规划 | 多会话日志聚合，阶段完成率等指标可视化 | - |
| IMP-016 | P2-C3 | PowerShell UTF-8配置 | P2 | ⏳ 待规划 | 设置Console输出编码和git编码 | - |
| IMP-017 | 知识更新 | 创建stage-guardrails-guide.md使用指南 | - | ⏳ 待创建 | docs/knowledge/新增阶段守卫使用指南 | - |
| IMP-018 | 模式萃取 | 萃取弹性流程分级模式 | - | ⏳ 待萃取 | elastic-workflow-classification入库governance-strategy/ | - |

## 行动项详情

### IMP-001~007: 项目交付物（已完成）
- **IMP-001**: [stage-guardrails.md](../../../../../../.agents/rules/stage-guardrails.md)
- **IMP-002**: [pre-document-reading.md](../../../../../../.agents/protocols/pre-document-reading.md)
- **IMP-003**: [feature-development.md](../../../../../../.agents/workflows/feature-development.md)
- **IMP-004**: 5角色Non-Goals更新
- **IMP-005**: [check-stage-guardrails.py](../../../../../../.agents/scripts/check-stage-guardrails.py)
- **IMP-006**: [AGENTS.md](../../../../../../AGENTS.md)
- **IMP-007**: [全局看板](../../../../../../.trae/specs/README.md)

---

### IMP-008: 萃取规则落地三层模型模式
- **优先级**: P0
- **状态**: ⏳ 待萃取
- **验收标准**: three-layer-rule-enforcement（定义层+痕迹层+验证层）入库governance-strategy/

---

### IMP-009: 萃取结构化轻量日志模式
- **优先级**: P0
- **状态**: ⏳ 待萃取
- **验收标准**: structured-lightweight-logging（[PREFIX] | key=value | ctx={json}格式）入库code-patterns/

---

### IMP-010: 配置.gitattributes统一换行符
- **优先级**: P0
- **状态**: ⏳ 待执行
- **验收标准**: 创建.gitattributes，设置* text=auto，*.md text eol=lf

---

### IMP-011: check-stage-guardrails.py集成到CI
- **优先级**: P1
- **状态**: ⏳ 待规划
- **验收标准**: ci-check.ps1/sh增加阶段守卫日志检查步骤（日志文件存在时检查）

---

### IMP-012: 添加--strict模式
- **优先级**: P1
- **状态**: ⏳ 待规划
- **验收标准**: strict模式下WARN也返回非零退出码，用于CI门禁

---

### IMP-013: spec模板增加"可观测性需求"
- **优先级**: P1
- **状态**: ⏳ 待规划
- **验收标准**: .trae/specs/模板强制要求考虑日志/验证需求

---

### IMP-014~016: P2后续规划
- **IMP-014**: 阶段守卫运行时强制执行（远期规划）
- **IMP-015**: 日志聚合仪表盘（远期规划）
- **IMP-016**: PowerShell UTF-8配置（待规划）

---

### IMP-017: 创建stage-guardrails-guide.md使用指南
- **状态**: ⏳ 待创建
- **验收标准**: docs/knowledge/新增阶段守卫使用指南

---

### IMP-018: 萃取弹性流程分级模式
- **状态**: ⏳ 待萃取
- **验收标准**: elastic-workflow-classification（变更类型决策树→三路径流程）入库governance-strategy/

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~007 | 2026-06-29 | 3次原子提交 | 阶段守卫规则+协议+工作流+角色更新+脚本+索引同步完成 |
| IMP-008~018 | - | - | 待后续规划执行 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件（7项已交付完成，11项待萃取/待执行/待规划）
