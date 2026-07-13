---
name: extraction-cmd
version: 1.0.0
description: "当用户提到'萃取'、'extraction'、'模式沉淀'、'萃取模式'、'模式入库'、'沉淀为模式'、'可复用模式'、'更新模式库'、'生成模式文档'时，必须使用此技能。提供标准化的模式萃取流程：案例收集→本质抽象→结构化模板→反模式提炼→迁移验证→入库。不要手动组织萃取流程——本Skill封装了六步标准萃取法、反模式对等原则和可迁移性验证。替代旧的pattern-extraction-cmd（v1.0.0）。"
argument-hint: "<萃取来源：复盘报告/洞察文档/多案例> [模式类型：方法论/代码/流程/架构]"
user-invocable: true
paths:
  - ".agents/commands/extraction.md"
  - "docs/retrospective/patterns/"
title: "Extraction 萃取命令 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/extraction-cmd/SKILL.toml"
---
# Extraction 萃取命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/extraction.md](../../commands/extraction.md)（完整流程）

## 1. Skill ID
`extraction-cmd`

> **版本说明**：本Skill替代旧的 `pattern-extraction-cmd`（v1.0.0），区别在于：
> - 从Skill封装升级为正式指令集（commands/extraction.md）
> - 新增反模式对等原则（每个模式必须配对反模式）
> - 新增多案例支撑要求（避免单案例过度泛化）
> - 新增迁移验证步骤（在新场景验证模式可复用性）
> - 抽象层次适配（根据使用范围选择L1-L4抽象层级）

## 2. 功能描述

提供标准化模式萃取执行能力，引导完成"案例→本质→模式→反模式→验证→入库"六步闭环：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **全新萃取** | ⭐ 从0到1创建新模式（首次发现可复用经验） | 完整六步流程，产出标准化模式文档 |
| **模式更新** | ⭐ 已有模式的迭代升级（新案例补充/反模式完善） | 增量更新，保留历史版本信息 |
| **合并重构** | ⭐ 多个相似模式的合并/拆分/重构 | 去重整合，提升模式库一致性 |

核心功能：从具体案例中提炼可迁移模式 → 反模式对等提炼 → 迁移性验证 → 标准化入库 → 索引更新。

> **为什么用本Skill而非手动写模式？** 手动写"模式"最容易犯三个错误：（1）把具体项目经验直接当模式（缺乏抽象，换场景就不能用）；（2）只有正面做法没有反模式（不知道什么情况下不该用）；（3）单案例过度泛化（一个项目成功就认为是通用模式）。本Skill的四原则（可迁移性优先、反模式对等、多案例支撑、抽象层次适配）从流程上防止这三个错误。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "萃取"、"extraction"、"模式沉淀"、"萃取模式"
- "模式入库"、"沉淀为模式"、"可复用模式"
- "更新模式库"、"生成模式文档"、"pattern extraction"
- 复盘报告完成后，需要将洞察沉淀为可复用模式
- 多个案例中发现共性，需要提炼为方法论
- 代码/文档中发现可复用结构，需要标准化

> **关于触发**：萃取是复盘(R)和洞察(I)的下游环节——当复盘/洞察产出可复用经验时，必须使用本Skill沉淀到模式库。经验停留在单次报告中是浪费，只有萃取为可迁移模式才能实现知识复用。

## 4. 方案选择决策树

```
需要萃取模式？
├─ 首次创建新模式（无现有模式对应）？ → 全新萃取（完整六步）
├─ 更新已有模式（补充新案例/完善反模式）？ → 模式更新（增量）
├─ 多个相似模式需要合并/拆分？ → 合并重构
└─ 只是单次复盘的快速总结（不需要沉淀到模式库）？ → 使用 retrospective-cmd 即可，不需要萃取
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `extr-YYYYMMDD-<pattern-name>`）：
```
[CMD-LOG] | level=INFO | cmd=extraction | step=S0 | event=CMD_START | session=extr-... | msg=开始模式萃取：<模式名称> | ctx={"mode":"create/update/merge","pattern_type":"methodology/code/process/architecture","source_count":"<案例数量>"}
```

**与其他Skill的关系**：
- 上游：retrospective-cmd（复盘产出洞察）、insight-cmd（洞察产出根因）
- 下游：export-report-cmd（导出模式文档）、docgen-cmd（更新索引）
- 在七概念链路中是E阶段的执行Skill（由seven-concepts-cmd调用）

## 5. 核心步骤（快速开始）

```
步骤1：读取 [commands/extraction.md](../../commands/extraction.md) 了解完整六步流程
步骤2：明确萃取模式类型和抽象层次（L1原则/L2方法/L3流程/L4模板）
步骤3：按六步法执行：
   - S1 案例收集（收集≥2个支撑案例，单案例不得萃取）
   - S2 本质抽象（剥离具体项目特征，提炼不变核心）
   - S3 结构化模板（按标准模板填充：触发场景+核心步骤+适用条件）
   - S4 反模式提炼（对等提炼反模式：什么场景下不该用、常见错误用法）
   - S5 迁移验证（在新场景中验证模式可复用性）
   - S6 入库（存入docs/retrospective/patterns/对应目录，更新索引）
步骤4：更新模式库索引和导航
步骤5：记录CMD-LOG完成事件
```

> 完整RACI矩阵、输入参数规范、模板字段见L2文档 [commands/extraction.md](../../commands/extraction.md)。

> **为什么反模式必须与正模式对等提炼？** 只告诉"怎么做"不告诉"什么时候不该做"是危险的——模式的价值不仅在于指引正确做法，更在于划定适用边界。没有反模式的模式就像只有油门没有刹车的车，在错误场景使用正确模式同样会导致失败。反模式回答"这个模式在什么条件下会失效"，是模式可迁移性的关键保障。

## 6. 安全检查清单（萃取质量门）

- [ ] 萃取基于≥2个独立案例（单案例只能作为"候选洞察"，不能入库为正式模式）
- [ ] 已剥离具体项目特征（模式描述中不包含具体项目名/人名/临时变量）
- [ ] 结构化模板完整：触发场景+核心步骤+适用条件+反模式+迁移验证记录
- [ ] 反模式对等存在：每个正模式至少有1个反模式（常见误用场景）
- [ ] 迁移验证已执行：在至少1个不同于来源案例的新场景中验证模式可复用
- [ ] 抽象层次适配：根据使用范围选择正确层级（L1-L4），不把L4模板当L1原则
- [ ] 模式存入正确目录（docs/retrospective/patterns/下对应分类子目录）
- [ ] 索引和导航已更新（docgen-cmd可索引到新入库模式）
- [ ] 涉及模式升级/合并/新建时已执行交叉引用系统化检查（中英文双关键词 Grep + 文件分类 + 更新说明）
- [ ] 模式成熟度评估已引用 validation_count 和 reuse_count 量化数据，非主观标签

## 7. 执行日志（CMD-LOG）

执行萃取命令集时，必须按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
- `cmd=extraction`，session前缀 `extr-YYYYMMDD-<pattern-name>`
- 步骤编号 S0-S6（启动→案例收集→本质抽象→结构化→反模式→迁移验证→入库）
- 特有事件：`CASE_COLLECTED`、`ABSTRACTION_COMPLETE`、`ANTIPATTERN_EXTRACTED`、`MIGRATION_VERIFIED`、`PATTERN_STORED`、`SINGLE_CASE_WARNING`

## 8. Gotchas（陷阱与反直觉行为）

- **单案例不得萃取为正式模式**：这是硬性红线——单个项目的成功经验可能是运气、是特定环境的产物、是过度拟合。单案例可以标记为"候选洞察"，但必须等到第二个案例出现后才能萃取为正式模式。违反这一条会污染模式库。
- **反模式不是"反面教材"**：反模式不是列出"做得差的例子"，而是定义"模式失效的边界条件"——即"在X条件下，使用本模式会导致Y负面结果"。反模式是模式的适用边界，不是道德批判。
- **抽象层次不要错位**：L1原则（如"修复即闭环"）、L2方法（如"四步复盘法"）、L3流程（如"链接检查流程"）、L4模板（如"复盘报告模板"）是不同抽象层次的模式，不要把L4模板提升为L1原则，也不要把L1原则降格为L3流程。
- **萃取不是"写总结"**：总结是写给自己看的（记录发生了什么），模式是写给别人用的（指导在类似场景怎么做）。如果一个"模式"换一个人看不懂、换一个场景用不了，那它就不是模式，只是一份项目总结。
- **模式入库后必须更新索引**：创建了模式文件但不更新索引和导航，等同于把书放进图书馆但不录入目录——其他人找不到，模式就无法复用。

## 9. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数/约束/模板） | L2 | [commands/extraction.md](../../commands/extraction.md) | 每次使用必读 |
| 萃取四原则 | L2 | [commands/extraction.md](../../commands/extraction.md) | 理解核心设计理念 |
| 模式库目录 | L2 | [docs/retrospective/patterns/](../../../docs/retrospective/patterns/) | 存放产出物 |
| 萃取四层漏斗 | L2 | [extraction-four-layer-funnel.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/extraction-four-layer-funnel.md) | 理解萃取方法论 |
| 七概念方法论（E阶段定位） | L2 | [commands/seven-concepts.md](../../commands/seven-concepts.md) | 在七概念链路中使用时 |

## 10. Changelog

- **v1.0.0** (2026-07-13): 初始版本，封装萃取指令集（commands/extraction.md），新增六步萃取流程、四核心原则（可迁移性优先/反模式对等/多案例支撑/抽象层次适配）、G3质量门（模式可迁移验证）。替代旧的pattern-extraction-cmd。
