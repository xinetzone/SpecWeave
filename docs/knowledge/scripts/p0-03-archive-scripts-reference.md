---
id: p0-03-archive-scripts-reference
title: 归档脚本工具链说明集合
source: d:\spaces\chaos\.agents\scripts\knowledge_archive.py
source_type: file
category: scripts
tags:
  - knowledge-archive
  - cli-scripts
  - automation
  - archive-commands
archive_status: archived
archive_priority: P0
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:09:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 knowledge_archive.py、正文摘要、元数据与 scripts 分类映射核对通过
summary: 归档脚本的入口路径、默认目录常量、四个命令的职责和推荐用法。以"怎么用"和"为何这样用"为核心，不搬运源码正文。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\scripts\p0-03-archive-scripts-reference.md
archived_at: 2026-08-02T03:09:49Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:09:49Z archived from d:\spaces\chaos\.agents\knowledge\temp\scripts\p0-03-archive-scripts-reference.md to D:\spaces\SpecWeave\.agents\docs\knowledge\scripts\p0-03-archive-scripts-reference.md
---

# 归档脚本工具链说明集合

## 来源

- 脚本入口：[knowledge_archive.py](file:///d:/spaces/chaos/.agents/scripts/knowledge_archive.py)
- 脚本说明：[.agents/scripts/README.md](file:///d:/spaces/chaos/.agents/scripts/README.md)（如存在）
- 执行准备文档：[p0-archive-baseline-plan.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/p0-archive-baseline-plan.md)
- 上游优先级分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`scripts`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\scripts\`

## 正文摘要

当前归档自动化实现为一个 Python CLI，入口位于 `d:\spaces\chaos\.agents\scripts\knowledge_archive.py`。

### 默认路径

- 临时知识目录：`d:\spaces\chaos\.agents\knowledge\temp`
- 正式知识目录：`d:\spaces\SpecWeave\.agents\docs\knowledge`
- 归档索引：`d:\spaces\chaos\.agents\knowledge\archive-index.json`

### 四个命令

| 命令 | 职责 |
|---|---|
| `archive` | 校验条目状态、分类、优先级和最小元数据，成功后写入正式目录并更新索引 |
| `verify` | 校验索引与正式目录的一致性，输出结构化异常结果（path_mismatch / formal_target_missing / format_unreadable / metadata_mismatch） |
| `retry` | 允许 `sync_failed` 条目在修复条件满足后重新执行归档 |
| `repair-index` | 在正式条目仍存在时重建或修复索引记录，不重复复制正文内容 |

### 输入格式

条目以 Markdown + YAML frontmatter 格式存放在 `d:\spaces\chaos\.agents\knowledge\temp\<category>\` 下，frontmatter 必须包含 id、title、source、source_type、category、tags、archive_status、archive_priority、created_at、updated_at、version 等最小字段。

## 动作边界

本轮为归档准备态（`pending_review`）。正式归档时，本条目只需沉淀脚本的入口、默认路径、命令职责和输入格式。脚本源码 (`knowledge_archive.py`) 和测试文件保留在本地，不作为正式知识正文归档。
