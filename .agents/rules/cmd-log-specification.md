---
id: "cmd-log-specification"
title: "CMD-LOG 命令集执行日志规范"
layer: "standards"
x-toml-ref: "../../../.meta/toml/.agents/rules/cmd-log-specification/cmd-log-specification.toml"
---
# CMD-LOG 命令执行日志规范


## 文档导航

| 章节 | 说明 |
|------|------|
| [概述与适用范围](cmd-log-specification/01-overview-scope.md) | CMD-LOG设计目标、与SG-LOG/PDR-LOG的关系、适用的7个命令集清单 |
| [日志格式与级别约定](cmd-log-specification/02-format-levels.md) | 统一单行格式、字段说明、分隔符约定、Session ID规范、DEBUG/INFO/WARN/ERROR四级使用场景 |
| [通用事件、步骤编号与命令集特有事件](cmd-log-specification/03-events-steps.md) | CMD_START/STEP_ENTER等5个通用生命周期事件、S0-S6步骤编号规范、7个命令集特有事件枚举 |
| [输出要求、日志解析与过滤分析](cmd-log-specification/04-output-parsing.md) | 零依赖输出要求、grep/awk快速过滤命令、Python正则解析示例、常见分析场景 |
| [检查清单、日志集成关系与Changelog](cmd-log-specification/05-checklist-integration-changelog.md) | 实施检查清单、与SG-LOG/PDR-LOG/应用日志的协作关系、版本更新历史 |

---

## 相关模式

- - [阶段守卫规范](stage-guardrails.md)
- - [PDR前置文档读取协议](../protocols/pre-document-reading.md)
- - [结构化轻量日志格式](../../docs/retrospective/patterns/code-patterns/structured-lightweight-logging.md)
