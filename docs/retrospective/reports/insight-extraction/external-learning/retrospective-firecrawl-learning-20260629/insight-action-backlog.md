---
title: Firecrawl系统学习复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-firecrawl-learning-20260629/insight-action-backlog.toml"
project: retrospective-firecrawl-learning-20260629
template_upgrade: 2026-07-06 v1.2
ssot:
  suggestions_source: export-suggestions.md → actions/
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。三角验证法模式已通过后续架构优先级项目落地，其余项待实施。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | actions/action-1 | 三角验证法纳入洞察指令集标准流程 | 高 | ✅ 已完成 | triangular-source-verification.md沉淀为正式模式，insight-cmd包含三源验证规范 | 2026-06-30 |
| IMP-002 | actions/action-2 | 增强Skill发现协议 | 高 | ✅ 已完成 | .agents/capabilities/ONBOARDING.md+REGISTRY.md建成，渐进式披露三层架构落地 | 2026-06-30 |
| IMP-003 | actions/action-3 | Agent间资源调度Credit模型 | 中 | ⏳ 暂缓 | 多Agent并发场景落地时实施self-management资源分配 | - |
| IMP-004 | actions/action-4 | LLM调用层双模型切换 | 中 | ⏳ 待执行 | 多模型API可用时SKILL.md增加model_hint字段支持fast/balanced/precise路由 | - |
| IMP-005 | actions/action-5 | 更新知识资产索引 | 低 | ⏳ 待执行 | 下次资产盘点时登记本报告为知识资产 | - |
| IMP-006 | actions/action-6 | Firecrawl能力引入评估 | 低 | ⏳ 暂缓 | 有大规模网页抓取需求时再评估自托管vs托管方案 | - |
| IMP-007 | 知识沉淀§1 | 三角验证法模式入库 | 高 | ✅ 已完成 | triangular-source-verification.md写入retrospective-knowledge/模式库，L2成熟度 | 2026-06-30 |
| IMP-008 | 知识沉淀§2 | Agent-First API设计模式入库 | 中 | ✅ 已完成 | 扩展为渐进式披露架构(P-ARCH-001)和Markdown即接口(P-ARCH-002)两个模式入库 | 2026-06-30 |
| IMP-009 | 知识沉淀§3 | Firecrawl技术知识库补充 | 低 | ⏳ 待执行 | docs/knowledge/learning/新增firecrawl-web-data-api.md，含架构摘要/API速查/自托管对比 | - |

## 行动项详情

### IMP-001: 三角验证法纳入洞察指令集标准流程
- **优先级**: 高
- **执行结果**: 在架构优先级评估项目中，三角验证法已纳入insight-cmd标准流程，作为信息采集规范强制执行
- **产出物**: [triangular-source-verification.md](../../../../patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md)
- **提交**: 2026-06-30通过retrospective-architecture-priority项目落地

---

### IMP-002: 增强Skill发现协议
- **优先级**: 高
- **执行结果**: 在架构优先级评估项目中，作为P0模块1-3完成：能力注册中心、指令集Skill化、Agent Onboarding协议
- **产出物**: [.agents/capabilities/](../../../../../../.agents/capabilities/)（REGISTRY+ONBOARDING）、6个指令集SKILL、onboarding-protocol.md
- **提交**: 2026-06-30通过retrospective-architecture-priority项目落地

---

### IMP-003: Agent间资源调度Credit模型
- **优先级**: 中
- **状态**: ⏳ 暂缓
- **触发条件**: 多Agent并发场景落地时
- **DoD**: 实施self-management资源分配能力，支持基于Credit的任务优先级调度

---

### IMP-004: LLM调用层双模型切换
- **优先级**: 中
- **状态**: ⏳ 待执行
- **触发条件**: 多模型API可用时
- **DoD**: SKILL.md frontmatter增加model_hint字段(fast/balanced/precise)，Agent根据任务类型选择推理策略

---

### IMP-005: 更新知识资产索引
- **优先级**: 低
- **状态**: ⏳ 待执行
- **触发条件**: 下次资产盘点时
- **DoD**: 登记本报告及8个洞察为知识资产

---

### IMP-006: Firecrawl能力引入评估
- **优先级**: 低
- **状态**: ⏳ 暂缓
- **触发条件**: 有大规模网页抓取需求时
- **DoD**: 评估自托管vs托管方案的成本收益，决定是否引入

---

### IMP-007: 三角验证法模式入库
- **优先级**: 高
- **执行结果**: triangular-source-verification.md正式写入retrospective-knowledge目录，包含三源验证标准流程、信息维度互补性矩阵、交叉验证检查清单
- **产出物**: [triangular-source-verification.md](../../../../patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md)
- **提交**: 2026-06-30完成

---

### IMP-008: Agent-First API设计模式入库
- **优先级**: 中
- **执行结果**: 原计划合并洞察1+4为Agent-First API Design模式，在架构优先级项目中扩展为两个更具体的模式：P-ARCH-001渐进式披露架构（L3）和P-ARCH-002 Markdown即接口（L2）
- **产出物**: [ARCHITECTURE.md](../../../../../../.agents/capabilities/ARCHITECTURE.md)、[markdown-as-interface.md](../../../../patterns/methodology-patterns/ai-collaboration/markdown-as-interface.md)
- **提交**: 2026-06-30完成

---

### IMP-009: Firecrawl技术知识库补充
- **优先级**: 低
- **状态**: ⏳ 待执行
- **DoD**: docs/knowledge/learning/新增firecrawl-web-data-api.md，包含技术架构摘要、API端点速查表、自托管vs托管对比、竞品参考维度、快速上手代码片段

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001/002/007/008 | 2026-06-30 | 通过retrospective-architecture-priority项目落地 | 高优先级行动项及2个模式沉淀已在后续架构重构项目中完成 |
| IMP-003/006 | - | - | 暂缓，待触发条件满足 |
| IMP-004/005/009 | - | - | 待执行 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级：从export-suggestions.md和actions/迁移行动项至独立backlog文件
