---
id: "cmd-log-checklist-integration"
title: "检查清单、日志集成关系与Changelog"
source: "cmd-log-specification.md#05-checklist-integration-changelog"
x-toml-ref: "../../../.meta/toml/.agents/rules/cmd-log-specification/05-checklist-integration-changelog.toml"
---
# 检查清单、日志集成关系与Changelog

## 11. 实施检查清单

### 11.1 新增命令集Skill门面时的检查项

- [ ] 定义命令集的 `cmd` 标识和 `session` ID前缀
- [ ] 定义步骤编号（S0-Sn）及每个步骤的名称
- [ ] 定义通用事件（CMD_START/STEP_ENTER/STEP_COMPLETE/CMD_COMPLETE/CMD_ERROR）的消息模板和ctx字段
- [ ] 定义命令集特有事件的枚举（封闭集合）
- [ ] 提供至少3条真实日志示例（包含正常流程+WARN/ERROR场景）
- [ ] 在SKILL.md的"执行日志规范"章节中记录上述内容
- [ ] 在本规范文档中同步更新步骤表、特有事件定义和示例

### 11.2 每次调用命令集时的强制执行检查项

> **基于2026-07-28日志断裂违规事件补充**，每次实际执行命令集Skill门面时，必须在开始执行实质性操作前逐项自查：

- [ ] **🔴 强制**：执行任何文件操作/工具调用之前，已输出S0 CMD_START日志行（首条日志铁律）
- [ ] **🔴 强制**：CMD_START的ctx字段包含本次执行的关键参数（目标文件、操作类型、dry_run状态等）
- [ ] **🔴 强制**：每个步骤进入时输出STEP_ENTER，完成时输出STEP_COMPLETE
- [ ] **🔴 强制**：命令结束（无论成功/失败）时输出CMD_COMPLETE或CMD_ERROR，且session ID与S0一致
- [ ] **🟡 建议**：若执行中途因异常中断，在后续复盘中按§8.4规范补全日志链路
- [ ] **🟡 建议**：日志输出中无无关非CMD-LOG格式的内容混入执行链路


## 12. 与其他日志类型的关系

SpecWeave 项目日志体系：

| 日志类型 | 前缀 | 适用场景 | 文档 |
|---------|------|---------|------|
| 阶段守卫日志 | SG-LOG | 开发流程阶段边界拦截、跳转审批 | [.agents/rules/stage-guardrails.md](../stage-guardrails.md) |
| 前置文档读取日志 | PDR-LOG | 必读文档读取确认、缺失告警 | [.agents/protocols/pre-document-reading.md](../../protocols/pre-document-reading.md) |
| **命令集执行日志** | **CMD-LOG** | **6大命令集Skill门面执行追踪** | **本文件** |

三类日志共享相同的格式规范（前缀+键值对+JSON ctx），但前缀、字段集合和事件枚举各自封闭，解析脚本按前缀分发。


## 13. Changelog

- **v1.3.0** (2026-07-28): 新增§8"强制日志纪律（不可跳过）"章节，制定5条日志铁律（首条日志铁律/ctx完整性/步骤连续性/闭环铁律/事后补全义务），明确5项违规判定标准，补充正确vs错误示例及事后补全规范。同步更新§11检查清单，新增"11.2每次调用命令集时的强制执行检查项"（含4项🔴强制项+2项🟡建议项）。基于对抗审查wiki同步任务中"跳过S0 CMD_START导致执行链路断裂"的复盘违规事件萃取。
- **v1.2.0** (2026-06-30): 新增mermaid命令集注册，包含7步流程定义、8个特有事件、Session ID前缀`merm-`及典型日志示例，命令集总数从5个扩展为6个。
- **v1.1.0** (2026-06-30): 5个命令集SKILL全部完成三层架构重构，L1层CMD-LOG章节精简为概要+L2引用模式，retrospective/export-report（v1.1）+ insight/atomization/atomic-commit（v1.2）共减少重复内容约260行。
- **v1.0.0** (2026-06-30): 初始版本，从5个Skill门面提取并规范化CMD-LOG日志标准，包含通用格式、字段说明、级别约定、通用事件、各命令集特有事件定义、解析正则和分析命令。


---

## 相关模式

- - [阶段守卫规范](../stage-guardrails.md)
- - [PDR前置文档读取协议](../../protocols/pre-document-reading.md)
- - [结构化轻量日志格式](../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md)

← 上一章: [输出要求、日志解析与过滤分析](04-output-parsing.md) | **[返回索引](../cmd-log-specification.md)**
