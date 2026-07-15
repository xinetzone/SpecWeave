---
title: Frontmatter元数据规范统一迁移复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/meta-methodology/retrospective-frontmatter-metadata-unification-20260702/insight-action-backlog.toml"
project: retrospective-frontmatter-metadata-unification-20260702
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: insight-extraction.md §3 改进建议
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本项目短期和中期建议均已执行完毕，归档完成。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 短期建议§1 | 完成Frontmatter元数据规范文档 | 高 | ✅ 已完成 | frontmatter-metadata-standard.md已创建，定义四字段flat结构 | 2026-07-02 |
| IMP-002 | 短期建议§2 | 批量迁移全项目存量文档 | 高 | ✅ 已完成 | 785+ Markdown文件完成title字段批量添加 | 2026-07-02 |
| IMP-003 | 短期建议§3 | 萃取3个可复用模式并入库 | 高 | ✅ 已完成 | metadata-layering、depth-reference-table、spec-triple-sync三个L1模式入库 | 2026-07-02 |
| IMP-004 | 短期建议§4 | 更新所有相关索引确保可发现 | 高 | ✅ 已完成 | 所有相关索引文档同步更新，新规范可发现 | 2026-07-02 |
| IMP-005 | 短期建议§5 | 用深度参考表解决路径计算问题 | 中 | ✅ 已完成 | depth-reference-table模式已沉淀，提供预计算参考表 | 2026-07-02 |
| IMP-006 | 短期建议§6 | 规范发布严格遵循三同步原则 | 高 | ✅ 已完成 | 本次规范发布完整执行"发现→导航→示范"三同步 | 2026-07-02 |
| IMP-007 | 中期建议§1 | 开发x-toml-ref自动生成脚本 | 高 | ✅ 已完成 | fix-x-toml-ref.py开发完成，支持自动计算/修复路径 | 2026-07-02 |
| IMP-008 | 中期建议§2 | frontmatter完整性校验工具 | 高 | ✅ 已完成 | check-frontmatter.py开发完成，支持--strict/--fix/--exclude | 2026-07-02 |
| IMP-009 | 中期建议§3 | 规范发布Checklist模板 | 中 | ✅ 已完成 | spec-release-checklist-template.md创建完成，三同步Checklist化 | 2026-07-02 |
| IMP-010 | 长期建议§1 | 元数据分层自动校验 | 中 | ⏳ 待办 | 脚本自动检测应外部化字段，提示重构机会 | - |
| IMP-011 | 长期建议§2 | 规范落地度量指标 | 中 | ⏳ 待办 | 跟踪新规范发布后遵循率，识别落地失败规范 | - |
| IMP-012 | 长期建议§3 | 模式反哺规范更新 | 低 | ⏳ 待办 | 定期从复盘中萃取模式，反向更新基础规范，形成闭环 | - |

## 行动项详情

### IMP-001: 完成Frontmatter元数据规范文档
- **优先级**: 高
- **来源**: insight-extraction.md §3 短期建议1
- **执行结果**: frontmatter-metadata-standard.md已创建，明确定义四字段flat结构（id/title/source/x-toml-ref），区分内联字段与外部TOML字段
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-002: 批量迁移全项目存量文档
- **优先级**: 高
- **来源**: insight-extraction.md §3 短期建议2
- **执行结果**: 785+ Markdown文件完成title字段批量添加，使用add-frontmatter-title.py自动化脚本
- **产出物**: [add-frontmatter-title.py](../../../../../../scripts/add-frontmatter-title.py)
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-003: 萃取3个可复用模式并入库
- **优先级**: 高
- **来源**: insight-extraction.md §3 短期建议3
- **执行结果**: 三个L1级可复用模式已入库：
  - metadata-layering（元数据分层模式，架构层）
  - depth-reference-table（深度参考表模式，工具自动化层）
  - spec-triple-sync（规范三同步原则，治理策略层）
- **产出物**: 
  - [metadata-layering.md](../../../../patterns/architecture-patterns/metadata-layering.md)
  - [depth-reference-table.md](../../../../patterns/methodology-patterns/tools-automation/depth-reference-table.md)
  - [spec-triple-sync.md](../../../../patterns/methodology-patterns/governance-strategy/spec-triple-sync.md)
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-004: 更新所有相关索引确保可发现
- **优先级**: 高
- **来源**: insight-extraction.md §3 短期建议4
- **执行结果**: 所有相关索引文档和导航入口同步更新，新规范在顶层总览可发现
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-005: 用深度参考表解决路径计算问题
- **优先级**: 中
- **来源**: insight-extraction.md §3 短期建议5
- **执行结果**: depth-reference-table模式已沉淀，提供不同目录深度的相对路径预计算参考表
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-006: 规范发布严格遵循三同步原则
- **优先级**: 高
- **来源**: insight-extraction.md §3 短期建议6
- **执行结果**: 本次规范发布完整执行"发现→导航→示范"三同步流程：顶层总览引用→上下文路由入口→存量迁移示范案例
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-007: 开发x-toml-ref自动生成脚本
- **优先级**: 高
- **来源**: insight-extraction.md §3 中期建议1
- **执行结果**: fix-x-toml-ref.py开发完成，支持根据当前文件路径自动计算正确相对路径，支持--dry-run预览、--write写入、--create-toml创建缺失TOML骨架
- **产出物**: [fix-x-toml-ref.py](../../../../../../scripts/fix-x-toml-ref.py)
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-008: frontmatter完整性校验工具
- **优先级**: 高
- **来源**: insight-extraction.md §3 中期建议2
- **执行结果**: check-frontmatter.py开发完成，支持检查必填字段、验证x-toml-ref路径正确性、检测禁止字段、支持--strict严格模式（CI门禁）、--fix-toml-ref自动修复
- **产出物**: [check-frontmatter.py](../../../../../../scripts/check-frontmatter.py)
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-009: 规范发布Checklist模板
- **优先级**: 中
- **来源**: insight-extraction.md §3 中期建议3
- **执行结果**: spec-release-checklist-template.md创建完成，将三同步原则转化为可逐项打勾的Checklist，包含规范编写→发现同步→导航同步→示范同步→提交前验证5个部分
- **产出物**: [spec-release-checklist-template.md](../../../../../../templates/spec-release-checklist-template.md)
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-010: 元数据分层自动校验
- **优先级**: 中
- **来源**: insight-extraction.md §3 长期建议1
- **内容**: 脚本自动检测哪些字段应该外部化到TOML，提示frontmatter重构机会
- **状态**: ⏳ 待办
- **执行结果**: -

---

### IMP-011: 规范落地度量指标
- **优先级**: 中
- **来源**: insight-extraction.md §3 长期建议2
- **内容**: 建立度量指标跟踪新规范发布后的遵循率，识别落地失败的规范
- **状态**: ⏳ 待办
- **执行结果**: -

---

### IMP-012: 模式反哺规范更新
- **优先级**: 低
- **来源**: insight-extraction.md §3 长期建议3
- **内容**: 定期从复盘中萃取模式，反向更新基础规范，形成"实践→复盘→模式→规范→实践"的闭环
- **状态**: ⏳ 待办
- **执行结果**: -

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~009 | 2026-07-02 | 11次原子提交 | 9项短期/中期行动项全部闭环完成，含规范文档、批量迁移、3个模式入库、3个自动化工具/模板 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从insight-extraction.md改进建议章节提取行动项至独立backlog文件（历史项目补建，短中期项已闭环）
