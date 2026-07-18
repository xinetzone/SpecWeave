---
title: Mermaid渲染回归问题复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-rendering-regression-20260629/insight-action-backlog.toml"
project: retrospective-mermaid-rendering-regression-20260629
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
| IMP-001 | 立即执行§1 | 补全mermaid-trap-cheatsheet的换行符陷阱 | 高 | ✅ 已完成 | 速查表新增换行符陷阱条目，含正反例对比 | 2026-06-29 |
| IMP-002 | 立即执行§2 | 更新mermaid-safe-coding-rules规则2 | 高 | ✅ 已完成 | 规则2补充换行符说明或新增规则2c | 2026-06-29 |
| IMP-003 | 立即执行§3 | 为check-mermaid.py添加\n换行符检测与自动修复 | 高 | ✅ 已完成 | flowchart/stateDiagram节点\n检测，--fix自动替换为<br/> | 2026-06-29 |
| IMP-004 | 立即执行§4 | 修正mermaid-safe-coding-rules的成熟度评估 | 中 | ✅ 已完成 | 成熟度从L4调整为L3 | 2026-06-29 |
| IMP-005 | 短期执行§5 | 将check-mermaid集成到CI检查和提交前流程 | 高 | ✅ 部分完成 | CI已集成（ci-check.ps1/sh第4步），工作流指引待补充 | 2026-06-29 |
| IMP-006 | 短期执行§6 | Mermaid模板中内置安全规则注释 | 中 | ✅ 已完成 | safe-starter.md内置%%注释安全提醒，修复注释感知bug | 2026-06-29 |
| IMP-007 | 短期执行§7 | 建立"修复→工具补全"的强制闭环 | 中 | ⏳ 待规划 | Code Review和阶段守卫加入规则：Mermaid bug修复必须同步更新check-mermaid | - |
| IMP-008 | 中期执行§8 | 探索编辑器实时检查集成 | 低 | 💡 远期规划 | VS Code扩展或Language Server实时提示Mermaid问题 | - |
| IMP-009 | 中期执行§9 | 将治理成熟度模型应用到其他规范领域 | 中 | 💡 远期规划 | 硬编码治理、Git提交规范、文档链接规范、命名约定等领域推广成熟度模型 | - |

## 行动项详情

### IMP-001: 补全mermaid-trap-cheatsheet的换行符陷阱
- **优先级**: 高
- **执行结果**: 速查表新增换行符陷阱条目，说明flowchart/stateDiagram必须用<br/>，sequenceDiagram可用\n
- **产出物**: [mermaid-trap-cheatsheet.md](../../../../patterns/code-patterns/mermaid-trap-cheatsheet.md)
- **提交**: commit d8faa30

---

### IMP-002: 更新mermaid-safe-coding-rules规则2
- **优先级**: 高
- **执行结果**: 五规则更新为六规则，补充换行符规则说明
- **产出物**: [mermaid-safe-coding-rules.md](../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)
- **提交**: commit d8faa30

---

### IMP-003: 为check-mermaid.py添加\n换行符检测与自动修复
- **优先级**: 高
- **执行结果**: _check_flowchart和_check_state_diagram中添加\n检测，--fix模式自动替换为<br/>
- **产出物**: [mermaid.py](../../../../../../scripts/lib/checks/mermaid.py)
- **提交**: commit d8faa30

---

### IMP-004: 修正mermaid-safe-coding-rules的成熟度评估
- **优先级**: 中
- **执行结果**: 成熟度从L4（标准化）调整为L3（标准化+工具检查）
- **产出物**: [mermaid-safe-coding-rules.md](../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)
- **提交**: commit d8faa30

---

### IMP-005: 将check-mermaid集成到CI检查和提交前流程
- **优先级**: 高
- **执行结果**: CI已集成（ci-check.ps1/sh第4步），失败时阻断；功能开发工作流中Mermaid检查指引待补充
- **产出物**: [ci-check.ps1](../../../../../../scripts/ci-check.ps1)（已存在验证）
- **提交**: commit 06c634b（验证确认）

---

### IMP-006: Mermaid模板中内置安全规则注释
- **优先级**: 中
- **执行结果**: 创建safe-starter.md安全起步模板，内置%%注释六规则提醒，同步修复注释感知bug
- **产出物**: [safe-starter.md](../../../../../../templates/mermaid-templates/safe-starter.md)
- **提交**: commit ec556bd

---

### IMP-007: 建立"修复→工具补全"的强制闭环
- **优先级**: 中
- **状态**: ⏳ 待规划
- **执行结果**: 待执行
- **验收标准**: Code Review和阶段守卫加入规则：任何Mermaid渲染bug修复，如果check-mermaid未能自动检测，必须同步更新check-mermaid.py

---

### IMP-008: 探索编辑器实时检查集成
- **优先级**: 低
- **状态**: 💡 远期规划
- **执行结果**: 待研究
- **验收标准**: VS Code扩展或Language Server实现Mermaid编辑时实时提示

---

### IMP-009: 将治理成熟度模型应用到其他规范领域
- **优先级**: 中
- **状态**: 💡 远期规划
- **执行结果**: 待推广
- **验收标准**: 硬编码治理、Git提交规范、文档链接规范、命名约定等领域评估成熟度等级

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~004 | 2026-06-29 | commit d8faa30 | 立即执行4项高/中优先级改进完成 |
| IMP-005 | 2026-06-29 | commit 06c634b | CI集成验证确认已存在 |
| IMP-006 | 2026-06-29 | commit ec556bd | 安全模板创建和注释感知bug修复完成 |
| IMP-007 | - | - | 待规划建立修复→工具补全闭环 |
| IMP-008~009 | - | - | 远期规划 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件（6项已闭环/部分完成，1项待规划，2项远期规划）
