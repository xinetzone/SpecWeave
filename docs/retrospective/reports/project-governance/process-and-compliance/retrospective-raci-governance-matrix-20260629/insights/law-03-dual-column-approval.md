---
id: "raci-law-03-dual-column-approval"
source: "insight-extraction.md#law-03"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/process-and-compliance/retrospective-raci-governance-matrix-20260629/insights/law-03-dual-column-approval.toml"
---
# 审批模型双列设计原则

## 规律陈述

审批层级模型表格必须使用"主要执行者(R)"+"最终审批者(A)"双列设计，而非单列"审批角色"。双列设计天然避免R/A混淆，明确区分"谁做"和"谁批"。

## 触发条件

- 设计审批层级模型
- 定义角色职责边界表
- 建立流程治理框架

## 五层模型标准格式（修正后）

| 层级 | 主要执行者 (R) | 最终审批者 (A) | 适用场景 |
|---|---|---|---|
| **日常流程** | orchestrator | orchestrator | 流程触发、进度协调、范围确认、数据采集 |
| **技术决策** | orchestrator / architect | architect | 方案设计、源文件/架构分析、根因分析 |
| **执行操作** | developer | reviewer | 代码实现、文件拆分、引用更新、提交 |
| **质量门禁** | reviewer | reviewer | 质量验收、常规审批、安全审计 |
| **关键决策** | orchestrator | co-founder | 重大审批、架构变更、核心数据操作 |

## 反例（修正前）

| 层级 | 审批角色 | 适用场景 |
|---|---|---|
| 执行操作 | developer | 代码实现...  <!-- R/A混淆，developer自审 -->
```
