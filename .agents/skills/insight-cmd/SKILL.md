---
name: insight-cmd
version: 1.3.0
description: "当用户提到'洞察'、'insight'、'分析问题'、'萃取'、'萃取洞察'、'根因分析'、'问题诊断'、'数据分析'、'找出原因'、'为什么会这样'、'优化机会'、'异常分析'时，必须使用此技能。提供系统化的数据分析与问题诊断能力：数据采集→趋势分析→根因分析→异常检测→建议生成。不要手动进行无结构的分析——本Skill封装了5-Whys根因法和四步分析流程。"
argument-hint: "<分析目标：system/task/process/user> [关注指标]"
user-invocable: true
paths:
  - ".agents/commands/insight.md"
  - "docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/"
  - "rules/cmd-log-specification.md"
---

# Insight 洞察命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/insight.md](../../commands/insight.md)（完整流程）+ [cmd-log-specification.md](../../rules/cmd-log-specification.md)（日志规范）

## 1. Skill ID
`insight-cmd`

## 2. 功能描述

提供系统化数据分析与问题诊断能力，完成"采集→分析→诊断→建议"闭环：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **数据驱动分析** | ⭐ 指标异常、效率下降、周期性分析 | 基于量化数据，客观可验证 |
| **根因诊断** | ⭐ 问题排查、故障分析、缺陷定位 | 5-Whys追根究底，找到根本原因 |
| **萃取洞察** | ⭐ 复盘中提炼可复用经验 | 从具体事件抽象为可迁移模式 |

核心功能：采集运行数据→分析趋势变化→定位根本原因→检测异常模式→生成改进建议。

> **为什么用本Skill而非随意分析？** 手动分析容易停留在表面现象（"出了个bug"）而不去找根因（"为什么这个bug会出现"）；本Skill强制使用5-Whys方法和四步分析流程，确保分析深度足够，结论可行动。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "洞察"、"insight"、"萃取洞察"、"萃取"
- "分析问题"、"问题诊断"、"根因分析"、"找出原因"
- "为什么会这样"、"原因是什么"、"怎么回事"
- "数据分析"、"指标分析"、"趋势分析"
- "优化机会"、"异常分析"、"瓶颈分析"
- 复盘过程中需要深入分析某个问题
- 周期性数据分析触发

> **关于触发**：即使没有明确说"用insight命令"，只要涉及问题诊断、原因追查、数据分析，就应该使用本Skill。如果是外部产品/竞品研究的信息采集分析，必须结合三角验证法SOP。

## 4. 方案选择决策树

```
需要执行分析？
├─ 有明确的量化指标/数据？ → 数据驱动分析（采集→趋势→对比→结论）
├─ 有具体问题/故障需要定位原因？ → 根因诊断（5-Whys方法）
├─ 从执行过程中提炼经验模式？ → 萃取洞察（具体→抽象→可复用）
├─ 需要完整的项目/阶段复盘？ → 使用 retrospective-cmd Skill（本Skill作为其中步骤3）
└─ 需要导出分析报告？ → 分析完成后使用 export-report-cmd
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `insgt-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=insight | step=S0 | event=CMD_START | session=insgt-... | msg=开始洞察分析：<简述> | ctx={"analysis_target":"system/task/process/user","focus_metrics":"..."}
```

> **为什么决策前必须记录日志？** 洞察分析涉及多步推理（采集→趋势→根因→异常→建议），分析目标判断错误会导致分析方向偏航，CMD_START记录目标和关注指标便于回溯分析起点。

## 5. 核心步骤（快速开始）

```
步骤1：读取 [commands/insight.md](../../commands/insight.md) 了解完整四步流程
步骤2：明确分析目标（system/task/process/user）和关注指标
步骤3：按四步法执行：
   - 步骤1 数据采集（运行指标、执行日志、用户反馈、变更记录）
   - 步骤2 趋势分析（时间序列、异常拐点、基线对比、变化率）
   - 步骤3 根因分析（5-Whys追问、因果链、瓶颈识别、影响评估）
   - 步骤4 异常检测（异常分类、阈值判定、关联分析）
   - 步骤5 建议生成（可行动建议、优先级排序、预期效果）
步骤4：建议形成行动项（高/中/低优先级+验收标准）
步骤5：可复用洞察沉淀至 docs/retrospective/patterns/
```

> 完整RACI矩阵、数据采集清单、5-Whys模板、三角验证法SOP见L2文档 [commands/insight.md](../../commands/insight.md)。分析外部产品/技术/竞品时参考[三角验证法](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md)。

> **为什么必须区分"相关性"与"因果性"？** 数据分析中最危险的陷阱是把时间上先后发生或统计上相关的两件事误判为因果关系（如"服务器重启后响应变慢"不等于重启导致变慢）。错误的因果推断会产生误导性建议，比没有结论更有害——它会引导团队在错误的方向上投入资源。必须通过对照实验、机制解释或多源交叉验证来确认因果关系。

## 6. 安全检查清单（分析质量门）

- [ ] 数据来源已标注（哪些数据来自日志/用户反馈/代码，可信度如何）
- [ ] 区分了"相关性"与"因果性"（不把相关关系误判为因果关系）
- [ ] 根因分析追问了至少3层"为什么"（不停留在表面原因）
- [ ] 分析结论有数据支撑，不是主观推测
- [ ] 改进建议是可行动的（有具体操作、责任方、验收标准），而非"加强管理"类空话
- [ ] 高优先级建议明确了预期收益和实施成本
- [ ] 外部研究使用了三角验证法（三源交叉验证）

> **为什么根因分析必须追问至少3层"为什么"？** 单层"为什么"只能得到表面原因（如"服务挂了因为进程崩溃"），双层只能得到直接原因（"进程崩溃因为内存溢出"），三层及以上才能触达根本原因（"内存溢出因为新上线的缓存策略没有设置过期时间，且代码评审时未检查资源释放逻辑"）。追问层数不足会导致"修复症状而非病因"——重启服务能暂时恢复，但同样的问题会再次发生。

## 7. 执行日志（CMD-LOG）

执行洞察命令集时，必须按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
- `cmd=insight`，session前缀 `insgt-YYYYMMDD-<topic>`
- 步骤编号 S0-S6（启动→数据采集→趋势分析→根因分析→异常检测→建议生成→沉淀）
- 6个特有事件：`DATA_QUALITY_LOW`、`ANOMALY_DETECTED`、`ROOT_CAUSE_FOUND`、`CAUSALITY_UNCERTAIN`、`ANOMALY_CLASSIFIED`、`RECOMMENDATION`

> 完整字段说明、事件表格、日志示例见L2文档 [cmd-log-specification.md §7.2](../../rules/cmd-log-specification.md)。

## 8. 常见错误处理

| 问题场景 | 处理方式 |
|---------|---------|
| 数据不足无法分析 | 明确标注"数据不足"，列出需要补充什么数据，基于现有信息给出初步判断 |
| 多个可能原因 | 列出所有可能原因，按可能性排序，说明验证方法 |
| 问题无法复现 | 记录已知条件，给出监控建议，标注为"待观察" |
| 分析范围过大 | 缩小范围，优先分析影响最大的问题，标注范围边界 |

## 9. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数/模板） | L2 | [commands/insight.md](../../commands/insight.md) | 每次使用必读 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../rules/cmd-log-specification.md) | 日志格式、事件定义、解析方法 |
| 根因诊断模式 | L2 | [root-cause-diagnosis.md](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/root-cause-diagnosis.md) | 根因分析时 |
| 洞察萃取漏斗 | L2 | [extraction-four-layer-funnel.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/extraction-four-layer-funnel.md) | 萃取洞察时 |
| 洞察冰山模型 | L2 | [insight-iceberg-model.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/insight-iceberg-model.md) | 理解洞察层次 |
| 三源验证法 | L2 | [triangular-source-verification.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md) | 外部产品研究时 |

## 10. Changelog

- **v1.3.0** (2026-07-01): 在§4决策树后添加S0 CMD_START强制日志规范，记录触发时的输入参数（analysis_target/focus_metrics）便于回溯分析起点；补充第3个Why解释（根因分析追问至少3层为什么的必要性）。
- **v1.2.1** (2026-06-30): 补充Why设计意图解释（相关性vs因果性），通过质量检查why.explanations≥2要求。
- **v1.2.0** (2026-06-30): 按渐进式披露三层架构重构，将CMD-LOG详细事件表（51行）迁移至L2规范文档，关键参考表增加层级列，外部研究提示整合入步骤说明。
- **v1.1.0** (2026-06-29): 添加CMD-LOG结构化日志规范，定义18个关键日志事件。
- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于insight命令集封装。
