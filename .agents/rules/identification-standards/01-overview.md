---
id: "rules-identification-01-overview"
title: "硬编码识别标准：规范说明"
source: "rules/identification-standards.md#硬编码识别标准"
x-toml-ref: "../../../.meta/toml/.agents/rules/identification-standards/01-overview.toml"
---
# 硬编码识别标准：规范说明

本规范定义硬编码（Hard-coding）的识别标准，为代码审查者和开发者提供统一的判断依据。硬编码是指将本应外部化管理的数值、字符串、路径、配置等直接写入代码逻辑中的做法。其核心危害在于：当这些值需要变更时，必须修改源代码并重新编译或部署，降低了系统的可维护性和灵活性。

本规范的适用范围包括但不限于：

- 日常开发中的自我检查
- 代码审查（Code Review）时的质量评估
- 自动化静态分析工具的规则定义
- 重构决策中的优先级排序
**[返回索引](../identification-standards.md)** | 下一章 → [02 分类定义表](02-category-table.md)
