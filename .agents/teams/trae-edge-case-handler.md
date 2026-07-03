---
id: "teams-trae-edge-case-handler"
title: "Trae 边界情况处理规范"
x-toml-ref: "../../../.meta/toml/.agents/teams/trae-edge-case-handler/trae-edge-case-handler.toml"
---
# Trae 边界情况处理规范

本规范定义 Trae 生态下边界情况处理的统一标准，覆盖 Trae IDE 集成、论坛操作、外部工具链与 Trae Work 四大边界场景的识别、判断、处理与适配。规范旨在消除"每次遇到边界情况都重新探索"的低效循环，为智能体提供预定义的判断标准、处理流程与适配策略。


## 文档导航

| 章节 | 说明 |
|------|------|
| [模块概述与四大边界场景分类体系](trae-edge-case-handler/01-overview-classification.md) | 模块定位与职责、IDE集成/论坛操作/外部工具链/Trae Work四大边界场景分类 |
| [边界条件判断标准与异常处理流程](trae-edge-case-handler/02-criteria-process.md) | 多信号组合检测、三级分级（P0/P1/P2）、异常处理流程、升级路径 |
| [特殊场景适配策略与模块接口规范](trae-edge-case-handler/03-adaptation-interface.md) | 沙箱限制、网络隔离、权限不足等特殊场景适配、模块接口与调用约定 |
| [验证清单与使用约束](trae-edge-case-handler/04-checklist-constraints.md) | 验证检查清单、使用约束与禁止事项 |

---

## 相关模式

- - [forum-posting Skill](../skills/forum-posting/SKILL.md)
- - [trae_edge_case_handler.py脚本](../scripts/trae_edge_case_handler.py)
- - [任务交接协议](../protocols/handoff.md)
