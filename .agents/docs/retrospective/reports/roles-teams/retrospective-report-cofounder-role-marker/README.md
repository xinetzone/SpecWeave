---
id: "retrospective-report-cofounder-role-marker-readme"
title: "联合创始角色特殊标记 — 项目复盘分析报告"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/roles-teams/retrospective-report-cofounder-role-marker/README.toml"
---
# 联合创始角色特殊标记 — 项目复盘分析报告

> **项目名称**：联合创始角色特殊标记
> **复盘日期**：2026-06-23
> **项目周期**：单次交付（spec → 实现 → 验证全闭环）
> **报告类型**：项目结项复盘

## 项目概览

### 1.1 项目背景

项目 `.agents/roles` 角色管理模块中现有五个角色（orchestrator、architect、developer、reviewer、tester）采用同质化呈现，无法区分项目初创阶段的"联合创始"角色与普通角色。需要为联合创始角色引入特殊标记机制，在角色数据模型、索引清单与详情页面中保持一致的高辨识度视觉呈现，并通过权限声明约束其查看与管理范围。

### 1.2 项目目标

- 在角色数据模型（TOML frontmatter）中新增 `tier` 标识字段与 `[permissions]` 权限表
- 新增联合创始角色定义文件 `co-founder.md`
- 在 `README.md` 角色职责矩阵中新增"层级标记"列与视觉徽章（🏛️）
- 在角色详情文件标题中应用统一文字前缀 `[联合创始] 🏛️`
- 在 `README.md` 中补充权限控制说明章节
- 同步 `AGENTS.md` 角色定义索引表

## 子模块导航

| 章节 | 权威来源 | 说明 |
|------|---------|------|
| 执行复盘 | [execution-retrospective.md](execution-retrospective.md) | 实施过程回顾、关键节点分析、执行数据、成功经验与问题 |
| 洞察萃取 | [insight-extraction.md](insight-extraction.md) | 关键发现、规律认知、潜在机会 |
| 导出建议 | [export-suggestions.md](export-suggestions.md) | 改进建议、行动计划、后续优化方向、知识萃取模式 |

## 关联报告

[retrospective-report-cofounder-improvement-execution/](../retrospective-report-cofounder-improvement-execution/README.md)、[review-insight-export-loop.md](../../../patterns/methodology-patterns/retrospective-knowledge/review-insight-export-loop.md)
