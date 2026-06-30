---
name: retrospective-cmd
version: 1.2.1
description: "当用户提到'复盘'、'retrospective'、'回顾'、'总结经验'、'做个复盘'、'项目总结'、'阶段回顾'、'里程碑总结'、'事后分析'、'经验总结'时，必须使用此技能。提供标准化的项目复盘流程：收集事实→分析过程→提炼洞察→生成报告，引导完成完整的复盘闭环。不要手动组织复盘流程——本Skill已封装四步标准流程和产出物规范。"
argument-hint: "<复盘范围：project/iteration/task/incident> [重点领域]"
user-invocable: true
paths:
  - ".agents/commands/retrospective.md"
  - "docs/retrospective/reports/"
  - "docs/retrospective/patterns/"
  - "rules/cmd-log-specification.md"
---

# Retrospective 复盘命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/retrospective.md](../../commands/retrospective.md)（完整流程）+ [cmd-log-specification.md](../../rules/cmd-log-specification.md)（日志规范）

## 1. Skill ID
`retrospective-cmd`

## 2. 功能描述

提供标准化项目复盘执行能力，引导完成"事实→分析→洞察→报告"四步闭环：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **标准复盘** | ⭐ 项目/迭代里程碑完成后 | 完整四步流程，产出结构化复盘报告 |
| **轻量复盘** | ⭐ 单个任务/事件快速回顾 | 快速提炼经验，不做深入根因分析 |
| **故障复盘** | ⭐ 重大问题/故障发生后 | 重点根因分析和改进措施 |

核心功能：引导复盘流程 → 萃取可复用洞察 → 生成带优先级的改进建议 → 沉淀知识至模式库。

> **为什么用本Skill而非手动组织？** 手动复盘容易遗漏关键步骤（如跳过事实收集直接分析、或没有将洞察沉淀为可复用模式）；本Skill封装了经过多次验证的四步法模型和产出物规范，确保复盘质量可预测。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "复盘"、"retrospective"、"回顾"、"做个复盘"
- "总结经验"、"总结一下"、"经验总结"、"事后分析"
- "项目总结"、"阶段回顾"、"迭代总结"
- "里程碑总结"、"版本回顾"、"发布复盘"
- 项目里程碑完成、任务迭代结束、重大问题解决后

> **关于触发**：即使没有明确说"用retrospective命令"，只要涉及项目/任务/事件的经验总结和回顾，就应该使用本Skill。复盘是知识沉淀的核心入口，不要跳过。

## 4. 方案选择决策树

```
需要执行复盘？
├─ 项目/迭代里程碑完成？ → 标准复盘（完整四步流程）
├─ 单个任务/小事件快速总结？ → 轻量复盘（聚焦关键经验）
├─ 故障/重大问题发生后？ → 故障复盘（重点根因分析+改进措施）
└─ 需要从对话中直接萃取洞察（不做完整复盘流程）？ → 使用 insight-cmd Skill
```

**与其他Skill的关系**：
- 复盘完成后通常需要 `export-report-cmd` 导出正式报告
- 深度问题分析使用 `insight-cmd`
- 复盘报告过大时使用 `atomization-cmd` 原子化拆分

## 5. 核心步骤（快速开始）

```
步骤1：读取 [commands/retrospective.md](../../commands/retrospective.md) 了解完整四步流程
步骤2：明确复盘范围（project/iteration/task/incident）和时间范围
步骤3：按四步法执行：
   - S1 收集事实数据（时间线、关键事件、产出物）
   - S2 分析过程（成功因素、失败原因、瓶颈）
   - S3 提炼洞察（可复用模式、系统性问题、改进建议）
   - S4 生成报告（结构化复盘报告，含行动项）
   - S5 归档沉淀（模式入库、索引更新）
步骤4：需要导出时使用 export-report-cmd
步骤5：可复用模式沉淀至 docs/retrospective/patterns/
```

> 完整RACI矩阵、输入参数规范、约束条件见L2文档 [commands/retrospective.md](../../commands/retrospective.md)。

> **为什么必须区分"事实"与"判断"？** 事实阶段混入主观判断是复盘最常见的失败模式——一旦带着结论去收集事实，就会选择性忽略矛盾证据，最终得到"验证了偏见"的伪复盘。严格分离两阶段（S1只记录发生了什么，S2才分析为什么），才能确保洞察建立在客观基础上而非事后合理化。

## 6. 安全检查清单（复盘质量门）

- [ ] 复盘前已明确范围和时间边界（不是泛泛的"总结一下"）
- [ ] 事实还原基于数据和记录（执行日志、变更历史、产出物），而非主观印象
- [ ] 已区分"事实"与"判断"（事实阶段只记录发生了什么）
- [ ] 洞察提炼为可复用模式（关联到具体场景和触发条件），而非停留在具体事件描述
- [ ] 行动项有明确的优先级（高/中/低）和验收标准
- [ ] 沉淀知识时更新了相关索引（模式库/知识库README）

## 7. 执行日志（CMD-LOG）

执行复盘命令集时，必须按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
- `cmd=retrospective`，session前缀 `retr-YYYYMMDD-<topic>`
- 步骤编号 S0-S5（启动→收集事实→分析→提炼洞察→生成报告→归档沉淀）
- 6个特有事件：`KEY_FINDING`、`PATTERN_EXTRACTED`、`ACTION_ITEM`、`REPORT_GENERATED`、`DATA_INSUFFICIENT`、`PATTERN_SKIPPED`

> 完整字段说明、事件表格、日志示例见L2文档 [cmd-log-specification.md §7.1](../../rules/cmd-log-specification.md)。

## 8. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数/约束） | L2 | [commands/retrospective.md](../../commands/retrospective.md) | 每次使用必读 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../rules/cmd-log-specification.md) | 日志格式、事件定义、解析方法 |
| 四步法模型 | L2 | [retrospective-four-step-method.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/retrospective-four-step-method.md) | 理解核心方法论 |
| 洞察萃取漏斗 | L2 | [extraction-four-layer-funnel.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/extraction-four-layer-funnel.md) | 步骤3提炼洞察时 |
| 三源验证法 | L2 | [triangular-source-verification.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md) | 外部竞品/技术复盘时 |
| 复盘报告目录 | L2 | [docs/retrospective/reports/](../../../docs/retrospective/reports/) | 存放产出物 |

## 9. Changelog

- **v1.2.1** (2026-06-30): 补充Why设计意图解释（区分事实与判断），通过质量检查why.explanations≥2要求。
- **v1.2.0** (2026-06-30): 按渐进式披露三层架构重构，将CMD-LOG详细事件表迁移至L2规范文档，SKILL.md精简为L1门面（引用而非复制L2内容）。
- **v1.1.0** (2026-06-29): 添加CMD-LOG结构化日志规范，定义17个关键日志事件。
- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于retrospective命令集封装。
