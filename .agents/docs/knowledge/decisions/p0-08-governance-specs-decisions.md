---
id: p0-08-governance-specs-decisions
title: 已批准治理 Specs 稳定决策集合
source: d:\spaces\chaos\.trae\specs
source_type: directory
category: decisions
tags:
  - governance-decisions
  - spec-decisions
  - collaboration-baseline
  - knowledge-archive
  - task-system
  - archive-priority
archive_status: archived
archive_priority: P0
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:20:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 7 个已批准治理 specs、正文为稳定决策提炼、元数据与 decisions 分类映射核对通过
summary: 从 7 个已批准治理 specs 中提炼的稳定决策结论集合，覆盖协作文档三件套基线、临时知识库管道、归档自动化、SpecWeave 外部绑定、任务分类骨架、待办治理口径与归档优先级分级。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\decisions\p0-08-governance-specs-decisions.md
archived_at: 2026-08-02T03:14:21Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:14:21Z archived from d:\spaces\chaos\.agents\knowledge\temp\decisions\p0-08-governance-specs-decisions.md to D:\spaces\SpecWeave\.agents\docs\knowledge\decisions\p0-08-governance-specs-decisions.md
---

# 已批准治理 Specs 稳定决策集合

## 来源

- 决策集合来源目录：[`.trae/specs/`](file:///d:/spaces/chaos/.trae/specs)
- 上游收敛方案：[p0-archive-baseline-plan.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/p0-archive-baseline-plan.md)
- 上游优先级分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`decisions`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\decisions\`

## 稳定决策提炼

以下决策结论提炼自 7 个已批准治理 specs，各结论均为已批准并落地的稳定状态，不搬运各 spec 的实现细节正文。

### 1. 协作文档三件套基线（来自 `establish-project-collaboration-docs`）

- `README.md` 作为项目统一入口文档，面向开发者与贡献者
- `AGENTS.md` 作为代理治理基线，定义角色边界、协作规则与权限范围
- `.agents/` 作为实现层配置载体，承载代理配置、工作流、权限与上下文模板
- 三者职责分离、相互引用，不重复承载同一类详细配置

### 2. 临时知识库归档管道（来自 `establish-temporary-knowledge-archive`）

- `d:\spaces\chaos` 承担临时知识库存储工作区/缓冲区职责
- `d:\spaces\SpecWeave\.agents\docs\knowledge` 承担正式知识归档目录职责
- 归档必须保留原始元数据、关联标签与版本记录
- 临时库必须留存归档索引，支持流转轨迹追溯
- 需建立定期一致性校验与异常修复要求

### 3. 归档自动化实现（来自 `automate-temporary-knowledge-archive`）

- 治理规则从"仅文档约束"升级为"文档约束 + 最小可执行工具链"
- 实现按 `archive_status`、优先级、分类与元数据判断迁移触发
- 支持元数据继承、索引落盘与一致性校验输出结构化异常
- 支持 `sync_failed` 条目的重试与索引修复辅助流程

### 4. SpecWeave 外部代理资产绑定（来自 `bind-specweave-agents-assets`）

- `../SpecWeave/AGENTS.md` 与 `../SpecWeave/.agents/` 作为外部复用规范资产入口
- 绑定仅表示"外部复用入口"，不改变 `chaos/AGENTS.md` 本地治理基线定位
- 访问顺序：先读 `SpecWeave/AGENTS.md`，需要时再进入 `.agents/` 并从其 README 开始

### 5. 待办分类目录骨架（来自 `establish-task-category-directories`）

- `tasks/` 下按任务类型、业务领域、项目阶段三维度建立正式分类骨架
- 命名清晰规范，维度间职责不重叠
- 临时目录（如 `tasks/chaos/`）只代表历史记录，不作为长期分类规范

### 6. 待办治理口径（来自 `organize-task-tracking-docs`）

- `tasks/` 定位为待办实例与过程记录目录，`.agents/` 不承担待办实例存放
- `tasks/README.md` 约定最小分类与追踪维度：任务归属、状态、更新方式、追溯入口
- 文档口径与实际目录结构保持一致

### 7. 工作区归档优先级分级（来自 `analyze-workspace-archive-priority`）

- 按 `P0` / `P1` / `P2` / `P3` 四级口径为工作区内容分级
- 判断依据至少覆盖复用价值、治理价值、稳定性、风险或维护成本
- 优先级结论可作为后续归档任务拆解的输入，不重新定义等级语义

## 决策应用说明

- 上述决策结论已通过 `P0-01`~`P0-05` 基线条目与 `P0-06`~`P0-09` 处置登记落地
- 本条目作为决策证据集合，保留对原 spec 的引用；原 spec 正文保留在 `.trae/specs/`，不整批迁移

## 动作边界

本轮为稳定决策提炼条目。正式归档时保留来源 spec 引用与决策结论，不搬运各 spec 的实现细节、验收场景或迁移说明原文。
