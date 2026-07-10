---
title: 大规模批量文件原子化拆分复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/atomization/retrospective-large-file-atomization-batch-20260703/insight-action-backlog.toml"
project: retrospective-large-file-atomization-batch-20260703
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
| IMP-001 | 行动项1 | atomic-commit-cmd增加三查暂存检查 | 高 | 📋 待执行 | 连续10次原子提交不需要amend修复暂存问题 | - |
| IMP-002 | 行动项2 | Windows环境git中文提交最佳实践文档化 | 高 | 📋 待执行 | 连续20次中文提交无乱码 | - |
| IMP-003 | 行动项3 | 固化三段式拆分架构模板 | 中 | 📋 待执行 | 使用模板拆分一个新文件比不使用模板节省至少5分钟 | - |
| IMP-004 | 行动项4 | CI中增加大文件门禁检查 | 中 | 📋 待执行 | 新增代码中不允许出现>500行文件，>300行文件有明确说明 | - |
| IMP-005 | 行动项5 | 开发半自动化拆分辅助脚本 | 低 | 📋 待执行 | 使用辅助脚本完成一个文件拆分比纯手动节省10分钟以上 | - |

## 行动项详情

### IMP-001: atomic-commit-cmd增加三查暂存检查
- **优先级**: 高
- **来源**: export-suggestions.md §高优先级 行动项1
- **说明**: 在原子提交流程中增加强制检查步骤：git status --short，自动检查D状态文件暂存、自动检测*.pyc/__pycache__等文件
- **建议产出物**: atomic-commit-cmd技能增强
- **建议完成时间**: 2026-07-04
- **状态**: 📋 待执行

---

### IMP-002: Windows环境git中文提交最佳实践文档化
- **优先级**: 高
- **来源**: export-suggestions.md §高优先级 行动项2
- **说明**: 在开发规范中明确Windows环境使用临时文件法提交中文信息，提供标准命令模板，在atomic-commit-cmd中自动使用
- **建议产出物**: `docs/knowledge/operations/` 开发规范文档 + atomic-commit-cmd增强
- **建议完成时间**: 2026-07-04
- **状态**: 📋 待执行

---

### IMP-003: 固化三段式拆分架构模板
- **优先级**: 中
- **来源**: export-suggestions.md §中优先级 行动项3
- **说明**: 将三段式拆分架构沉淀为标准模板，创建__init__.py.tpl、cli_shim.py.tpl等模板文件，编写拆分checklist
- **建议产出物**: `docs/retrospective/patterns/methodology-patterns/document-architecture/` 原子化方法论相关模板
- **建议完成时间**: 2026-07-05
- **状态**: 📋 待执行

---

### IMP-004: CI中增加大文件门禁检查
- **优先级**: 中
- **来源**: export-suggestions.md §中优先级 行动项4
- **说明**: 在ci-check-cmd中增加文件大小检查：>300行警告，>500行阻断提交/合并
- **建议产出物**: ci-check-cmd技能增强
- **建议完成时间**: 2026-07-05
- **状态**: 📋 待执行

---

### IMP-005: 开发半自动化拆分辅助脚本
- **优先级**: 低
- **来源**: export-suggestions.md §低优先级 行动项5
- **说明**: 编写atomization-assist.py脚本，自动创建包目录结构、生成标准模板文件、生成薄垫片代码框架、给出拆分建议
- **建议产出物**: atomization-assist.py脚本
- **建议完成时间**: 2026-07-10
- **状态**: 📋 待执行

## 模式沉淀计划

| 模式名称 | 计划目标路径 | 计划成熟度 | 计划沉淀时间 |
|---------|---------|--------|---------|
| 三段式原子化拆分架构 | `docs/retrospective/patterns/methodology-patterns/document-architecture/atomization-three-layer-arch.md` | L3 | 2026-07-05 |
| Windows git中文提交方案 | `docs/knowledge/operations/git-windows-utf8-commit.md` | L2 | 2026-07-04 |
| 原子提交三查验证法 | `docs/retrospective/patterns/methodology-patterns/governance-strategy/atomic-commit-three-check.md` | L2 | 2026-07-04 |

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| - | - | - | - |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移5项行动项至独立backlog文件
