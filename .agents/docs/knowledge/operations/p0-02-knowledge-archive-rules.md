---
id: p0-02-knowledge-archive-rules
title: 临时知识库归档规则正文
source: d:\spaces\chaos\.agents\context\temp-knowledge-archive.md
source_type: file
category: operations
tags:
  - knowledge-archive
  - archive-rules
  - metadata-schema
  - consistency-verification
  - error-recovery
archive_status: archived
archive_priority: P0
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:09:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 temp-knowledge-archive.md、正文摘要、元数据与 operations 分类映射核对通过
summary: 定义临时知识库与正式知识库的分层关系、分类规则、状态与优先级字段、最小元数据、自动归档触发条件、正式目录映射、保留与回退策略、索引结构、一致性校验项和异常修复闭环。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p0-02-knowledge-archive-rules.md
archived_at: 2026-08-02T03:09:41Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:09:41Z archived from d:\spaces\chaos\.agents\knowledge\temp\operations\p0-02-knowledge-archive-rules.md to D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p0-02-knowledge-archive-rules.md
---

# 临时知识库归档规则正文

## 来源

- 源文件：[temp-knowledge-archive.md](file:///d:/spaces/chaos/.agents/context/temp-knowledge-archive.md)
- 执行准备文档：[p0-archive-baseline-plan.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/p0-archive-baseline-plan.md)
- 上游优先级分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`operations`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\operations\`

## 正文摘要

该规则文档是 `chaos` 临时知识归档体系的最详细规则源，覆盖以下核心能力：

- 临时库 (`chaos`) 与正式库 (`SpecWeave\.agents\docs\knowledge`) 的分层关系
- 9 个标准主分类及映射表
- 8 种归档状态 (`intake` / `pending_review` / `in_sorting` / `ready_to_archive` / `archived` / `blocked` / `sync_failed` / `deprecated`)
- 4 级优先级 (`P0` / `P1` / `P2` / `P3`)
- 最小必填元数据（11 个字段）和推荐补充字段
- 自动归档触发条件（7 条前置条件）
- 正式目录映射规则与路径解析顺序
- 不满足归档条件时的保留 / 回退 / 废弃策略
- 元数据、标签和版本记录的保留要求
- 归档索引结构与追溯字段
- 8 项定期一致性校验
- 异常判定（5 类）与"记录-隔离-比对-修复-复检-关闭"修复闭环

## 动作边界

本轮为归档准备态（`pending_review`）。正式归档前，建议审查规则正文是否与当前实际执行的归档脚本和目录结构完全一致，并将规则中已稳定的章节（分类、状态、优先级、元数据）作为正式条目核心正文。
