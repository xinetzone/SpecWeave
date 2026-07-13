---
name: seven-concepts-cmd
version: 1.0.0
description: "当用户提到'七概念'、'seven concepts'、'用方法论'、'系统性分析'、'按七概念走'、'完整流程'时，必须使用此技能。提供七概念方法论元编排能力：自动识别5种场景（里程碑复盘/问题解决/重构优化/知识沉淀/创新突破），通过决策树选择概念组合链路，串联G1-G4质量门，完成从事实采集到原子行动项的闭环。不要手动逐个调用R/I/E/C/A/F/V命令——本Skill是元编排层，会自动选择最优概念组合并按正确顺序执行。"
argument-hint: "<场景关键词> [主题] [深度级别：standard/light/deep]"
user-invocable: true
paths:
  - ".agents/commands/seven-concepts.md"
  - ".agents/commands/retrospective.md"
  - ".agents/commands/insight.md"
  - ".agents/commands/first-principles.md"
  - ".agents/commands/adversarial-review.md"
  - ".agents/commands/extraction.md"
  - ".agents/commands/atomization.md"
  - ".agents/commands/atomic-commit.md"
  - "docs/retrospective/patterns/methodology-patterns/governance-strategy/"
title: "Seven Concepts 七概念方法论编排命令 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/seven-concepts-cmd/SKILL.toml"
---
# Seven Concepts 七概念方法论编排命令 Skill

> ⚠️ **本Skill是元指令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/seven-concepts.md](../../commands/seven-concepts.md)（完整编排逻辑）+ 7个子命令文档

## 1. Skill ID
`seven-concepts-cmd`

## 2. 功能描述

提供七概念方法论（R-I-E-C-A-F-V）的元编排统一入口，自动识别场景、选择概念组合链路、串联质量门，完成系统性分析闭环：

| 概念 | 全称 | 作用 |
|------|------|------|
| R | Retrospective（复盘） | 采集事实数据、还原过程 |
| I | Insight（洞察） | 根因分析、识别问题本质 |
| E | Extraction（萃取） | 提炼可复用模式 |
| C | Atomic Commit（原子提交） | 确保变更单一职责、原子化交付 |
| A | Atomization（原子化） | 大文档/大任务拆分 |
| F | First Principles（第一性原理） | 本质思考、创新突破 |
| V | Adversarial Review（对抗审查） | 多视角验证、证伪加固 |

> **为什么用本Skill而非手动调用子命令？** 七概念的核心价值在于**链路编排**——不同场景需要不同的概念组合（如里程碑复盘用R→I→E→C，问题解决用I→F→V→C），手动调用容易遗漏质量门、打乱执行顺序、跳过必要的对抗审查。本Skill封装了5种场景的决策树和4道质量门（G1-G4），确保产出质量可预测。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "七概念"、"seven concepts"、"用方法论"、"按七概念走"
- "系统性分析"、"完整流程"、"从头到尾分析"
- 项目里程碑复盘（隐含R→I→E→C链路）
- 复杂问题需要根因分析+对抗验证（隐含I→F→V链路）
- 需要从实践中沉淀方法论（隐含R→I→E链路）
- 重构优化（隐含I→F→A→C链路）
- 创新方案设计（隐含F→V→I链路）

> **关于触发**：当用户请求的任务涉及"分析+解决+沉淀"完整闭环时，优先使用本Skill而非单独调用retrospective-cmd或insight-cmd。本Skill会根据场景自动决定是否需要完整七概念链路还是精简链路。

## 4. 方案选择决策树

```
用户请求是什么类型？
├─ 项目/迭代里程碑完成？ → 场景1：里程碑复盘（R→I→E→C）
│   └─ 标准链路：复盘事实 → 洞察根因 → 萃取模式 → 原子提交
├─ 遇到问题/Bug/故障需要解决？ → 场景2：问题解决（I→F→V→C）
│   └─ 诊断链路：洞察根因 → 第一性原理 → 对抗审查 → 原子修复提交
├─ 需要重构/优化/拆分？ → 场景3：重构优化（I→F→A→C）
│   └─ 重构链路：洞察问题 → 第一性原理设计 → 原子化拆分 → 原子提交
├─ 需要沉淀知识/模式/最佳实践？ → 场景4：知识沉淀（R→I→E）
│   └─ 沉淀链路：复盘案例 → 洞察共性 → 萃取模式入库
└─ 需要创新方案/突破思维定式？ → 场景5：创新突破（F→V→I→C）
    └─ 创新链路：第一性原理 → 对抗审查 → 洞察落地 → 原子提交
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `sc-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-... | msg=七概念方法论开始：<简述> | ctx={"scenario":"milestone/problem/refactor/knowledge/innovation","topic":"...","depth":"standard/light/deep"}
```

**与其他Skill的关系**：
- 本Skill是元编排层，内部会调用retrospective-cmd、insight-cmd等子Skill
- 复盘/洞察/萃取等子命令可以单独使用，但复杂场景优先用本Skill编排
- 原子提交使用atomic-commit-cmd（通过子命令调用）
- 原子化拆分使用atomization-cmd（需要时调用）

## 5. 核心步骤（快速开始）

```
步骤1：读取 [commands/seven-concepts.md](../../commands/seven-concepts.md) 了解完整编排逻辑
步骤2：场景识别：根据用户请求确定5种场景之一
步骤3：链路选择：按决策树选择概念组合链路
步骤4：逐概念执行：按链路顺序执行每个概念的标准流程
   - 每个概念完成后必须通过对应质量门（G1-G4）
   - G1：事实无因果词（R阶段产出检查）
   - G2：洞察四元组完整（现象+根因+影响+建议）（I阶段产出检查）
   - G3：模式可迁移（有触发条件+核心步骤+反模式）（E阶段产出检查）
   - G4：行动项原子化（单一职责、可独立验证）（C阶段产出检查）
   - 涉及F时必须经过V对抗审查
步骤5：输出汇总：各阶段产出物汇总+质量门通过记录
```

> 完整RACI矩阵、场景判定细节、质量门标准见L2文档 [commands/seven-concepts.md](../../commands/seven-concepts.md)。

> **为什么质量门是强制性的？** 七概念方法论与随意分析的区别就在于质量门——没有质量门，"复盘"就变成聊天，"洞察"就变成吐槽，"萃取"就变成总结。G1-G4每道门都是前一阶段产出物的质量拦截，防止垃圾进垃圾出（GIGO）。

## 6. 安全检查清单（七概念质量门）

- [ ] 场景已正确识别（5种之一），概念链路与场景匹配
- [ ] G1：事实阶段（R）无因果推断词（"因为"、"导致"、"所以"），纯客观描述
- [ ] G2：洞察（I）包含四元组：现象描述+根因分析+影响评估+改进建议
- [ ] G3：萃取（E）产出的模式包含：触发场景+核心步骤+反模式+迁移验证
- [ ] G4：行动项/提交（C）满足原子化：单一职责、可独立验证、有验收标准
- [ ] 使用第一性原理（F）时，已执行对抗审查（V）至少一个视角
- [ ] 涉及大文档拆分时已使用atomization-cmd原子化
- [ ] 涉及代码/文档变更时最终通过atomic-commit-cmd原子提交

> **为什么V（对抗审查）在使用F后是强制性的？** 第一性原理的本质是"质疑假设、从零重构"，但从零推导出的方案天然缺乏历史经验校验——这是创新方案最危险的盲区。对抗审查通过魔鬼代言人/新人/老板/未来四视角攻击，暴露第一性原理推导中可能忽略的约束条件、隐含假设和落地风险。

## 7. 执行日志（CMD-LOG）

执行七概念编排时，必须按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
- `cmd=seven-concepts`，session前缀 `sc-YYYYMMDD-<topic>`
- 步骤编号 S0-Sn（启动→场景识别→逐概念执行→质量门→汇总）
- 核心事件：`SCENARIO_DETECTED`、`CHAIN_SELECTED`、`GATE_PASSED`、`GATE_FAILED`、`CONCEPT_COMPLETED`、`CHAIN_COMPLETED`
- 每次调用子命令时输出 `SUB_CMD_INVOKED` 事件

## 8. Gotchas（陷阱与反直觉行为）

- **不要跳过场景识别直接全链路执行**：七概念不是每次都要走完R→I→E→C→A→F→V全部7个概念，轻量场景只需2-3个概念（如问题解决用I→F→V即可），强行全链路是过度工程。
- **质量门不通过时不要推进到下一阶段**：G1-G4是硬关卡——事实没厘清就分析原因，会得到基于错误事实的错误洞察；洞察不完整就萃取模式，会沉淀出不可复用的伪模式。必须回到当前阶段修复后再推进。
- **F（第一性原理）不是每个场景都需要**：里程碑复盘（场景1）和知识沉淀（场景4）的核心链路是R→I→E，不需要强行加入F；问题解决和创新突破场景才需要F进行本质思考。
- **V（对抗审查）必须在F之后，不能在F之前**：对抗审查是攻击已有的方案/推导，如果在F之前执行V，攻击的是旧方案而非新方案，无法验证第一性原理推导的正确性。
- **C（原子提交）是所有链路的终点**：无论哪种场景，只要有文件/代码变更产出，最终必须通过原子提交交付，这是"修复即闭环"原则的保证。

## 9. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整编排文档（RACI/决策树/质量门） | L2 | [commands/seven-concepts.md](../../commands/seven-concepts.md) | 每次使用必读 |
| 萃取命令 | L2 | [commands/extraction.md](../../commands/extraction.md) | E阶段执行时 |
| 复盘命令 | L2 | [commands/retrospective.md](../../commands/retrospective.md) | R阶段执行时 |
| 洞察命令 | L2 | [commands/insight.md](../../commands/insight.md) | I阶段执行时 |
| 第一性原理命令 | L2 | [commands/first-principles.md](../../commands/first-principles.md) | F阶段执行时 |
| 对抗审查命令 | L2 | [commands/adversarial-review.md](../../commands/adversarial-review.md) | V阶段执行时 |
| 七概念方法论索引 | L2 | [seven-concepts-methodology-index.md](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/seven-concepts-methodology-index.md) | 理解方法论体系 |
| 七概念质量标准 | L2 | [seven-concepts-quality-standards.md](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/seven-concepts-quality-standards.md) | 质量门判定细节 |
| 实战演练材料 | L2 | [exercises/](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/exercises/) | 团队培训参考 |

## 10. Changelog

- **v1.0.0** (2026-07-13): 初始版本，封装七概念元编排指令（commands/seven-concepts.md），支持5种场景自动识别、概念组合链路决策树、G1-G4质量门串联、子命令自动调用。配套方法论体系：萃取指令(extraction.md)、质量标准、实战演练材料。
