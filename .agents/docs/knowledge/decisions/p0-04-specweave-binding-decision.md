---
id: p0-04-specweave-binding-decision
title: SpecWeave 外部代理资产绑定边界
source: d:\spaces\chaos\.agents\context\specweave-binding.md
source_type: file
category: decisions
tags:
  - specweave
  - external-binding
  - agent-assets
  - cross-workspace
archive_status: archived
archive_priority: P0
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:09:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 specweave-binding.md、正文摘要、元数据与 decisions 分类映射核对通过
summary: 记录 chaos 与 SpecWeave 的跨工作区代理资产绑定决策，包括绑定路径、用途、访问顺序、适用边界和维护规则。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\decisions\p0-04-specweave-binding-decision.md
archived_at: 2026-08-02T03:09:57Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:09:57Z archived from d:\spaces\chaos\.agents\knowledge\temp\decisions\p0-04-specweave-binding-decision.md to D:\spaces\SpecWeave\.agents\docs\knowledge\decisions\p0-04-specweave-binding-decision.md
---

# SpecWeave 外部代理资产绑定边界

## 来源

- 源文件：[specweave-binding.md](file:///d:/spaces/chaos/.agents/context/specweave-binding.md)
- 治理入口引用：[AGENTS.md §3.2](../../../../external/chaos/npuusertools/AGENTS.md#L3.2)
- 执行准备文档：[p0-archive-baseline-plan.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/p0-archive-baseline-plan.md)
- 上游优先级分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`decisions`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\decisions\`

## 正文摘要

`chaos` 声明了对 `SpecWeave` 外部代理规范资产的两项绑定：

1. `../SpecWeave/AGENTS.md`：外部治理入口，说明 SpecWeave 的启动协议、上下文路由、核心规范入口与主权区边界
2. `../SpecWeave/.agents/`：外部规范资产容器，承载角色定义、规则体系、协议、工作流、模板、脚本与 Skill 门面

### 访问顺序

推荐先读取 `../SpecWeave/AGENTS.md`，确认任务是否需要进入外部规范体系；若需要继续下钻，再进入 `../SpecWeave/.agents/`，并从其中的 `README.md` 开始。

### 绑定约束

- 绑定仅表示"外部复用规范资产入口"
- 不表示 `SpecWeave` 内容属于 `chaos` 本地原生目录
- 不改变 `chaos/AGENTS.md` 作为当前工作区治理基线的定位
- `AGENTS.md` 末尾保留绑定关系维护日志模板

## 动作边界

本轮为归档准备态（`pending_review`）。正式归档时，以该绑定决策的路径、用途、访问顺序和边界约束为核心正文，不需要搬运 `specweave-binding.md` 中的完整实现模板原文。
