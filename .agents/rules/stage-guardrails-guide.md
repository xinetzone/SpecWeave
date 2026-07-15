---
id: "stage-guardrails-guide"
title: "阶段守卫运行时强制执行层使用指南"
source: "docs/knowledge/stage-guardrails-guide.md"
x-toml-ref: "../../.meta/toml/.agents/rules/stage-guardrails-guide.toml"
---
# 阶段守卫运行时强制执行层使用指南

---
id: "stage-guardrails-guide"
title: "阶段守卫运行时强制执行层使用指南"
source: "docs/knowledge/stage-guardrails-guide.md"
x-toml-ref: "../../.meta/toml/.agents/rules/stage-guardrails-guide.toml"
---
# 阶段守卫运行时强制执行层使用指南

> 本文档是 [stage-guardrails.md](stage-guardrails.md)（阶段守卫规则定义）的配套运行时指南，涵盖8阶段权限速查、必读文档清单、典型日志示例、常见拦截原因与解决方案、CLI工具手册，以及运行时+离线双层验证闭环。

## 文档导航

| 文档 | 内容 |
|------|------|
| [01 概述、架构与快速开始](stage-guardrails-guide/01-overview-quickstart.md) | 背景 + 三层架构概览 + Python/CLI快速开始示例 |
| [02 8阶段权限速查表](stage-guardrails-guide/02-permissions-reference.md) | 8阶段权限速查表（角色/核心产出/允许操作/禁止操作/必读文档） |
| [03 日志示例与格式规范](stage-guardrails-guide/03-logging-examples.md) | 10种典型SG-LOG日志示例 + 日志格式字段说明 |
| [04 常见拦截原因与解决方案](stage-guardrails-guide/04-common-interceptions.md) | 7种常见拦截原因、现象分析与解决方案 |
| [05 阶段跳转流程与CLI工具](stage-guardrails-guide/05-jump-flows-tools.md) | 阶段跳转流程（skip/rollback/advance） + CLI工具手册 + 双层验证闭环 |
| [06 Python API参考与排错指南](stage-guardrails-guide/06-api-troubleshooting.md) | GuardrailRuntime Python API参考 + 排错指南 + 参考链接 |

---

## 相关模式

- [三层检查工具模式](../docs/retrospective/patterns/code-patterns/three-tier-check-tool.md)
- [双通道分级日志](../docs/retrospective/patterns/code-patterns/dual-channel-tiered-logging.md)
