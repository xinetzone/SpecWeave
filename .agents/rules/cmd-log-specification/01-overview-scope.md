---
id: "cmd-log-overview-scope"
title: "概述与适用范围"
source: "cmd-log-specification.md#01-overview-scope"
x-toml-ref: "../../../.meta/toml/.agents/rules/cmd-log-specification/01-overview-scope.toml"
---
# 概述与适用范围

## 1. 概述

CMD-LOG 是 SpecWeave 命令集（Skill门面）的结构化执行日志规范，是项目日志体系的第三类日志（继 SG-LOG 阶段守卫日志、PDR-LOG 前置文档读取日志之后），用于追踪6大命令集执行过程中的关键节点，支持故障排查、断点续传、执行审计和事后复盘。

本规范与项目已有的 [结构化轻量日志格式](../../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md) 模式保持一致，采用统一前缀+键值对+JSON上下文的单行格式，零依赖、grep友好、机器可解析。


## 2. 适用范围

本规范适用于以下7个命令集Skill门面：

| 命令集 | cmd标识 | Session ID前缀 | 步骤数 | 特有事件数 |
|--------|---------|---------------|--------|-----------|
| 复盘（retrospective） | `retrospective` | `retr-` | 6步（S0-S5） | 17个 |
| 洞察（insight） | `insight` | `insgt-` | 7步（S0-S6） | 18个 |
| 导出报告（export-report） | `export-report` | `exprt-` | 7步（S0-S6） | 19个 |
| 原子化（atomization） | `atomization` | `atom-` | 7步（S0-S6） | 22个 |
| 原子提交（atomic-commit） | `atomic-commit` | `cmt-` | 7步（S0-S6） | 20个 |
| Mermaid图表（mermaid） | `mermaid` | `merm-` | 7步（S0-S6） | 8个 |
| 模式萃取（pattern-extraction） | `pattern-extraction` | `ptrn-` | 6步（S0-S5） | 9个 |

> **新增命令集时**：必须遵循本规范添加CMD-LOG日志章节，定义该命令集的step编号、session ID前缀和特有事件枚举。


---

## 相关模式

- - [阶段守卫规范](../stage-guardrails.md)
- - [PDR前置文档读取协议](../../protocols/pre-document-reading.md)
- - [结构化轻量日志格式](../../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md)

**[返回索引](../cmd-log-specification.md)** | 下一章 → [日志格式与级别约定](02-format-levels.md)
