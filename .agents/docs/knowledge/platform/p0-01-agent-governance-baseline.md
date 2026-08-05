---
id: p0-01-agent-governance-baseline
title: 工作区代理治理基线摘要
source: d:\spaces\chaos\AGENTS.md
source_type: file
category: platform
tags:
  - agent-governance
  - collaboration-rules
  - workspace-baseline
  - temporary-knowledge-archive
  - specweave-binding
archive_status: archived
archive_priority: P0
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:09:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 AGENTS.md、正文摘要、元数据与 platform 分类映射核对通过
summary: chaos 工作区的代理治理入口，定义角色分工、协作规则、权限边界、临时知识库摘要和 SpecWeave 外部绑定入口。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\platform\p0-01-agent-governance-baseline.md
archived_at: 2026-08-02T03:09:33Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:09:33Z archived from d:\spaces\chaos\.agents\knowledge\temp\platform\p0-01-agent-governance-baseline.md to D:\spaces\SpecWeave\.agents\docs\knowledge\platform\p0-01-agent-governance-baseline.md
---

# 工作区代理治理基线摘要

## 来源

- 源文件：[AGENTS.md](../../../../external/chaos/npuusertools/AGENTS.md)
- 执行准备文档：[p0-archive-baseline-plan.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/p0-archive-baseline-plan.md)
- 上游优先级分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`platform`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\platform\`

## 正文摘要

`chaos/AGENTS.md` 是工作区级代理协作基线，核心内容包括：

- 文档边界：明确与 `README.md`、`.agents/` 和 `tasks/` 的职责分离
- 工作区定位：多模块 AI/自动化研发工作区，临时知识库缓冲区，SpecWeave 外部绑定
- 代理角色：coordinator、documentation_agent、implementation_agent、validation_agent
- 协作规则：先判范围后动手、先读上下文、优先局部修改、输出可交接
- 权限范围：默认允许 / 需谨慎 / 禁止事项
- 临时知识库治理入口：与正式库边界、归档索引、一致性校验
- SpecWeave 绑定：路径声明、访问顺序、维护日志

## 动作边界

本轮为归档准备态（`pending_review`）。正式归档前，建议从源文件提炼一份面向正式知识库的稳定摘要版本，保持原文治理结构不在正式目录中重复出现，而是以"该文件的职责、适用范围和关键约定"作为正式条目正文。
