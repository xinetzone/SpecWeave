---
id: "sg-guide-02"
title: "02 8阶段权限速查表"
source: "rules/stage-guardrails-guide.md#02"
x-toml-ref: "../../../.meta/toml/.agents/rules/stage-guardrails-guide/02-permissions-reference.toml"
---

# 02 8阶段权限速查表


### 阶段定义与负责角色

| 阶段ID | 阶段名称 | 负责角色 | 核心产出 |
|--------|----------|----------|----------|
| S1 | 需求接收 | orchestrator | 需求文档、任务分解清单、风险评估 |
| S2 | 方案设计 | architect | 技术方案、架构设计、API定义、技术选型 |
| S3 | 任务分配 | orchestrator | 任务分配表、验收标准、依赖关系 |
| S4 | 代码实现 | developer | 业务代码、单元测试、PR |
| S5 | 测试编写 | tester | 测试用例、测试报告、缺陷报告 |
| S6 | 代码审查 | reviewer | 审查意见、合并建议 |
| S7 | 合并代码 | orchestrator | 合并记录、发布说明 |
| S8 | 完成确认 | orchestrator | 完成确认、交付物清单 |

### 各阶段允许的核心操作

| 阶段 | 允许的操作 | 典型禁止操作 |
|------|-----------|-------------|
| **S1** 需求接收 | CLARIFY_REQUIREMENT、CREATE_TASK_LIST、IDENTIFY_RISK、DEFINE_SCOPE、SET_PRIORITY、SEARCH_CODE、READ_DOCS | WRITE_CODE、DESIGN_ARCHITECTURE、CHOOSE_TECH_STACK、MODIFY_ARCHITECTURE |
| **S2** 方案设计 | ARCHITECTURE_DESIGN、CHOOSE_TECH_STACK、DEFINE_API、DESIGN_DATA_MODEL、CREATE_TASK_LIST、EVALUATE_TRADEOFFS | WRITE_CODE、MODIFY_BUSINESS_CODE、DEPLOY、MERGE_CODE |
| **S3** 任务分配 | ASSIGN_TASK、SET_ACCEPTANCE_CRITERIA、DEFINE_DONE、ESTIMATE_EFFORT、PRIORITIZE_BACKLOG | WRITE_CODE、DESIGN_ARCHITECTURE、APPROVE_CODE、DEPLOY |
| **S4** 代码实现 | WRITE_CODE、WRITE_UNIT_TEST、RUN_TEST、DEBUG_CODE、REFACTOR_CODE、SUBMIT_PR、CALL_TOOL | MODIFY_ARCHITECTURE、CHANGE_TECH_SELECTION、APPROVE_CODE、DEPLOY、MERGE_CODE |
| **S5** 测试编写 | WRITE_TEST、RUN_TEST、WRITE_INTEGRATION_TEST、REPORT_BUG、VERIFY_FIX、DEBUG_CODE | WRITE_CODE（业务代码）、MODIFY_ARCHITECTURE、APPROVE_CODE、MERGE_CODE |
| **S6** 代码审查 | REVIEW_CODE、APPROVE_CODE、REQUEST_CHANGES、COMMENT_CODE、READ_DOCS | WRITE_CODE（业务代码）、MODIFY_ARCHITECTURE、DEPLOY、MERGE_CODE |
| **S7** 合并代码 | MERGE_CODE、RESOLVE_CONFLICT、TAG_RELEASE、WRITE_CHANGELOG、APPROVE_CODE | WRITE_CODE、DESIGN_ARCHITECTURE、MODIFY_ARCHITECTURE |
| **S8** 完成确认 | CONFIRM_DELIVERY、WRITE_SUMMARY、UPDATE_DOC、CLOSE_TASK、SEARCH_CODE、READ_DOCS | WRITE_CODE、DESIGN_ARCHITECTURE、CHOOSE_TECH_STACK、DEPLOY |

> **通用规则**：`SEARCH_CODE` 和 `READ_DOCS` 在所有阶段对所有角色开放（只读操作永不拦截）。

### 各阶段必读文档（PDR前置文档）

| 阶段 | 必读文档 |
|------|---------|
| S1 | `AGENTS.md`、[stage-guardrails.md](../stage-guardrails.md)、[../../docs/development-standards.md](../../docs/development-standards.md) |
| S2 | [../../docs/knowledge/](../../docs/knowledge/README.md)（架构决策相关）、[stage-guardrails.md](../stage-guardrails.md)、S1产出的需求文档 |
| S3 | [feature-development.md](../../workflows/feature-development.md)、S1+S2产出物 |
| S4 | [../../docs/development-standards.md](../../docs/development-standards.md)（编码规范）、S3任务分配表 |
| S5 | [../../docs/development-standards.md](../../docs/development-standards.md)（测试规范）、S4代码 |
| S6 | [reviewer.md](../../roles/reviewer.md)、S4代码+S5测试 |
| S7 | [dependency-management.md](../../protocols/dependency-management.md) |
| S8 | 全部阶段产出物 |

使用 `mark_doc_check(required_docs=[...])` 标记必读文档检查完成，使用 `mark_pdr_done()` 确认PDR流程完成。

---

## 相关模式

- [三层检查工具模式](../../docs/retrospective/patterns/code-patterns/three-tier-check-tool.md)
- [双通道分级日志](../../docs/retrospective/patterns/code-patterns/dual-channel-tiered-logging.md)
---

← 上一章: [01 概述、架构与快速开始](01-overview-quickstart.md) | **[返回索引](../stage-guardrails-guide.md)** | 下一章: [03 日志示例与格式规范](03-logging-examples.md) →
