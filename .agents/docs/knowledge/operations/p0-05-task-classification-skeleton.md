---
id: p0-05-task-classification-skeleton
title: 任务分类与追踪骨架说明
source: d:\spaces\chaos\tasks\README.md
source_type: file
category: operations
tags:
  - task-system
  - classification
  - tracking
  - task-skeleton
  - workspace-operations
archive_status: archived
archive_priority: P0
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:09:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 tasks/README.md、正文摘要、元数据与 operations 分类映射核对通过
summary: 定义 tasks/ 目录的三维正式分类骨架（task-types / business-domains / project-stages）、使用原则、临时历史目录定位和查找入口。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p0-05-task-classification-skeleton.md
archived_at: 2026-08-02T03:10:04Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:10:04Z archived from d:\spaces\chaos\.agents\knowledge\temp\operations\p0-05-task-classification-skeleton.md to D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p0-05-task-classification-skeleton.md
---

# 任务分类与追踪骨架说明

## 来源

- 源文件：[tasks/README.md](file:///d:/spaces/chaos/tasks/README.md)
- 执行准备文档：[p0-archive-baseline-plan.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/p0-archive-baseline-plan.md)
- 上游优先级分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`operations`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\operations\`

## 正文摘要

`tasks/README.md` 定义了工作区任务待办的三维正式分类骨架：

### 分类维度

1. **`task-types/`** — 按任务工作性质归档
   - `research` · `planning` · `implementation` · `review` · `maintenance`

2. **`business-domains/`** — 按业务主题归档
   - `agent-governance` · `knowledge-archive` · `task-system` · `workspace-operations`

3. **`project-stages/`** — 按推进阶段归档
   - `intake` · `planned` · `in-progress` · `completed`

### 使用原则

- 同一任务文件选一个主归档维度，不在三维度下重复存放
- `tasks/TODO.md` 作为顶层待办入口
- 跨维度追溯时可保留主文件 + 其他入口做链接或说明

### 临时历史定位

`tasks/chaos/` 只保留临时历史记录，不作为正式分类骨架。

### 查找入口

优先级：`tasks/README.md` → `tasks/TODO.md` → 对应正式分类目录 → 必要时回到 `AGENTS.md` 或 `.agents/`

## 动作边界

本轮为归档准备态（`pending_review`）。正式归档时，以三维分类骨架和使用原则为核心正文，不需要把 `tasks/README.md` 中面向本地维护者的冗余导航段落完整搬运。
