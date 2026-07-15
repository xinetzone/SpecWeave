---
id: "pattern-extraction-cmd"
title: "Pattern Extraction 模式萃取命令 Skill"
version: "1.1.0"
name: "pattern-extraction-cmd"
description: "当用户提到'模式沉淀'、'萃取模式'、'模式入库'、'沉淀为模式'、'pattern extraction'、'可复用模式'、'更新模式库'、'生成模式文档'时，必须使用此技能。提供从复盘/洞察中萃取可复用模式的标准化流程：模式识别→分类定位→标准文档生成→索引更新→质量验证，附带决策路径CMD-LOG日志支持问题回溯。不要手动编写模式文档——本Skill封装了frontmatter规范、目录分类规则、质量检查标准和成熟度管理。"
argument-hint: "<来源：insight/retrospective/experience> [模式名称]"
user-invocable: "true"
x-toml-ref: "../../../.meta/toml/.agents/skills/pattern-extraction-cmd/SKILL.toml"
---
# Pattern Extraction 模式萃取命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：本文件第5-9节（完整流程）+ [pattern-maturity.py](../../../.agents/scripts/pattern-maturity.py)（成熟度管理脚本）


## 文档导航

| 章节 | 说明 |
|------|------|
| [Skill概述、功能描述与方案选择决策树](SKILL/01-overview-decision.md) | Skill标识、三方案对比、触发词清单、决策树、CMD_START强制日志 |
| [核心步骤与全新模式创建方案](SKILL/02-core-steps-create.md) | 六步快速开始、可复用三标准、TOML frontmatter模板、标准章节结构、目录分类 |
| [现有模式更新与模式合并重构方案](SKILL/03-update-merge.md) | validate/reuse成熟度更新、L1→L2→L3→L4升级条件、三维重叠度合并判断 |
| [CMD-LOG执行日志与质量安全清单](SKILL/04-cmd-log-quality.md) | ptrn-前缀Session格式、S0-S5步骤编号、特有事件定义、日志示例、12项质量门 |
| [错误处理、Gotchas陷阱与参考速查表](SKILL/05-errors-gotchas-reference.md) | 常见问题处理、反直觉陷阱、关键参考速查表、版本历史 |

---

## 相关模式

- - [insight-cmd Skill](../insight-cmd/SKILL.md)
- - [retrospective-cmd Skill](../retrospective-cmd/SKILL.md)
- - [CMD-LOG日志规范](../../rules/cmd-log-specification.md)
- - [模式成熟度管理](../../scripts/pattern-maturity.py)
- - [模式萃取方法论](../../docs/retrospective/patterns/README.md)
- - [模式合并边界判断](../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md)
