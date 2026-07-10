---
title: Mermaid治理闭环执行复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-governance-closure-20260629/insight-action-backlog.toml"
project: retrospective-mermaid-governance-closure-20260629
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 已完成§1 | 补全速查表换行符陷阱 | 高 | ✅ 已完成 | mermaid-trap-cheatsheet.md补充换行符陷阱说明 | 2026-06-29 |
| IMP-002 | 已完成§2 | 更新五规则→六规则 | 高 | ✅ 已完成 | mermaid-safe-coding-rules.md和development-standards.md更新为六规则 | 2026-06-29 |
| IMP-003 | 已完成§3 | check-mermaid添加\n检测 | 高 | ✅ 已完成 | mermaid.py新增_check_backslash_n函数 | 2026-06-29 |
| IMP-004 | 已完成§4 | 修正成熟度评估 | 中 | ✅ 已完成 | mermaid-safe-coding-rules.md成熟度从L4修正为L3 | 2026-06-29 |
| IMP-005 | 已完成§5 | CI集成验证 | 中 | ✅ 已完成 | 确认ci-check.ps1/sh第4步已集成Mermaid检查 | 2026-06-29 |
| IMP-006 | 已完成§6 | 模板内置安全提醒 | 高 | ✅ 已完成 | safe-starter.md内置%%注释安全提醒 | 2026-06-29 |
| IMP-007 | 已完成§7 | check-mermaid注释感知 | 高 | ✅ 已完成 | mermaid.py新增_strip_inline_comment()函数 | 2026-06-29 |
| IMP-008 | 已完成§8 | 一站式操作指南 | 高 | ✅ 已完成 | mermaid-guide.md整合所有Mermaid相关资源 | 2026-06-29 |
| IMP-009 | 待执行§1 | 修复check-mermaid单元测试用例 | 中 | ⏳ 待规划 | pytest .agents/scripts/tests/test_checks_mermaid.py -v全部通过 | - |
| IMP-010 | 待执行§2 | 在开发流程文档中集成Mermaid指南入口 | 中 | ⏳ 待规划 | feature-development.md文档编写章节添加Mermaid指南引用 | - |
| IMP-011 | 待执行§3 | 将"工具自测文档模式"沉淀为可复用方法论模式 | 低 | ⏳ 待规划 | patterns/methodology-patterns/中新增模式文档 | - |

## 行动项详情

### IMP-001: 补全速查表换行符陷阱
- **优先级**: 高
- **执行结果**: mermaid-trap-cheatsheet.md补充了换行符陷阱说明
- **产出物**: [mermaid-trap-cheatsheet.md](../../../../patterns/code-patterns/mermaid-trap-cheatsheet.md)
- **提交**: commit d8faa30

---

### IMP-002: 更新五规则→六规则
- **优先级**: 高
- **执行结果**: mermaid-safe-coding-rules.md和development-standards.md从五规则更新为六规则
- **产出物**: [mermaid-safe-coding-rules.md](../../../../patterns/code-patterns/mermaid-safe-coding-rules.md) + [development-standards.md](../../../../../development-standards.md)
- **提交**: commit d8faa30

---

### IMP-003: check-mermaid添加\n检测
- **优先级**: 高
- **执行结果**: mermaid.py新增_check_backslash_n函数检测\n字面量问题
- **产出物**: [mermaid.py](../../../../../../.agents/scripts/lib/checks/mermaid.py)
- **提交**: commit d8faa30

---

### IMP-004: 修正成熟度评估
- **优先级**: 中
- **执行结果**: mermaid-safe-coding-rules.md成熟度从L4修正为L3
- **产出物**: [mermaid-safe-coding-rules.md](../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)
- **提交**: commit d8faa30

---

### IMP-005: CI集成验证
- **优先级**: 中
- **执行结果**: 确认ci-check.ps1/sh第4步已集成Mermaid检查，无需重复建设
- **产出物**: 验证确认
- **提交**: commit 06c634b

---

### IMP-006: 模板内置安全提醒
- **优先级**: 高
- **执行结果**: safe-starter.md内置%%注释安全提醒，源头预防注释中的\n误报
- **产出物**: [safe-starter.md](../../../../../../.agents/templates/mermaid-templates/safe-starter.md)
- **提交**: commit ec556bd

---

### IMP-007: check-mermaid注释感知
- **优先级**: 高
- **执行结果**: mermaid.py新增_strip_inline_comment()函数，跳过注释行中的检测
- **产出物**: [mermaid.py](../../../../../../.agents/scripts/lib/checks/mermaid.py)
- **提交**: commit ec556bd

---

### IMP-008: 一站式操作指南
- **优先级**: 高
- **执行结果**: mermaid-guide.md整合所有Mermaid相关资源，解决文档入口分散问题
- **产出物**: [mermaid-guide.md](../../../../../knowledge/best-practices/mermaid-guide.md)
- **提交**: commit d39813b

---

### IMP-009: 修复check-mermaid单元测试用例
- **优先级**: 中
- **状态**: ⏳ 待规划
- **执行结果**: 待执行
- **验收标准**: `pytest .agents/scripts/tests/test_checks_mermaid.py -v` 全部通过

---

### IMP-010: 在开发流程文档中集成Mermaid指南入口
- **优先级**: 中
- **状态**: ⏳ 待规划
- **执行结果**: 待执行
- **验收标准**: feature-development.md文档编写章节添加Mermaid指南引用

---

### IMP-011: 将"工具自测文档模式"沉淀为可复用方法论模式
- **优先级**: 低
- **状态**: ⏳ 待规划
- **执行结果**: 待执行
- **验收标准**: patterns/methodology-patterns/中新增工具自测文档模式

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~004 | 2026-06-29 | commit d8faa30 | 前置提交完成4项高/中优先级改进 |
| IMP-005 | 2026-06-29 | commit 06c634b | CI集成验证确认已存在 |
| IMP-006~007 | 2026-06-29 | commit ec556bd | 模板安全提醒和注释感知修复完成 |
| IMP-008 | 2026-06-29 | commit d39813b | 一站式操作指南整合完成 |
| IMP-009~011 | - | - | 待规划执行 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件（8项已闭环，3项待规划）
