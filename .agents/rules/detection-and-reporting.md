---
id: "rules-detection-and-reporting"
title: "检测与报告机制"
source: "AGENTS.md#规则体系"
x-toml-ref: "../../.meta/toml/.agents/rules/detection-and-reporting.toml"
---
# 检测与报告机制

> 本文档定义硬编码治理体系中的检测与报告机制，覆盖「自动初筛 → 人工深审 → 周期复盘」三层闭环。

## 文档导航

| 文档 | 主题 | 说明 |
|------|------|------|
| [detection-and-reporting/01-overview.md](detection-and-reporting/01-overview.md) | 规范说明 | 文档目的、覆盖范围、三层闭环概述 |
| [detection-and-reporting/02-three-layer-architecture.md](detection-and-reporting/02-three-layer-architecture.md) | 三层检测体系架构 | 自动化扫描/人工审查/定期报告三层架构图与分工原则 |
| [detection-and-reporting/03-automated-scanning.md](detection-and-reporting/03-automated-scanning.md) | 自动化扫描规范 | 触发时机、9条扫描规则表、结果分级、白名单与抑制注释 |
| [detection-and-reporting/04-manual-review.md](detection-and-reporting/04-manual-review.md) | 人工审查规范 | 审查检查清单、评分公式、审查流程与记录格式 |
| [detection-and-reporting/05-periodic-reporting.md](detection-and-reporting/05-periodic-reporting.md) | 定期报告规范 | 报告周期、7章节报告模板、数据来源与处理流程 |
| [detection-and-reporting/06-tool-integration.md](detection-and-reporting/06-tool-integration.md) | 工具集成建议 | CI脚本集成、6类外部工具推荐、自定义脚本模板、pre-commit配置 |
| [detection-and-reporting/07-roles-constraints.md](detection-and-reporting/07-roles-constraints.md) | 角色职责与使用约束 | developer/reviewer/orchestrator/architect职责划分、5条使用约束 |

**[返回上级](README.md)**
