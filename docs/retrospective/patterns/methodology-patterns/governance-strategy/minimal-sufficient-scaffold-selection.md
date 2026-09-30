---
type: Pattern
id: "minimal-sufficient-scaffold-selection"
title: "最小充分脚手架选型法"
source: "七概念知识沉淀(sc-20260930-python-agent-harness)——AI Harness/Agent Python 包全景调研（45 条事实）"
source_report: "../../../../knowledge/tech/python-agent-harness/index.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/minimal-sufficient-scaffold-selection.toml"
maturity: "L1-draft"
maturity_note: "3 个相互独立的外部案例同向支撑（Princeton/Stanford 的 mini-swe-agent vs SWE-agent 对照、Growth Engineer 七框架同任务实测、AutoGPT/BabyAGI 退潮复盘），非同谱系双案例故不适用 L1.5；尚未在本项目完成一次真实选型实战，按模式库标准不授 L2；本团队一次实战验证后可升 L2-validated"
date: "2026-09-30"
validation_count: 3
reuse_count: 0
documentation_level: "complete"
abstract_level: "domain-general"
tags: ["ai-agent", "agent-harness", "技术选型", "框架选型", "最小可行", "依赖治理", "swe-bench", "供应链风险", "同任务实测"]
related_patterns:
  - "agent-platform-selection-framework"
  - "harness-architecture-layered-model"
  - "tech-selection-three-checks"
  - "vendor-lifecycle-governance"
  - "bounded-iteration-budget"
  - "prove-usefulness-check"
---

# 最小充分脚手架选型法（Minimal Sufficient Scaffold）

## 模式概述

为一个 agent 任务选择 Python 框架/SDK 时，最常见的决策路径是看功能清单、比 GitHub star、读厂商文章——这三条路径在 2025-2026 年的 agent 赛道同时失效：九大 harness 能力在相互竞争的厂商栈间高度趋同（功能清单失去区分度），约 58.9K stars 的 AutoGen 进入维护模式、SWE-agent 被约 131 行的 mini-swe-agent 接替（star 是滞后且失真的指标），厂商文章天然为本家产品的满配形态辩护（软文不构成选型证据）。

该模式把选型动作从"资料比较"改为"受控实测 + 生命体征尽调"：

> **先明确任务的失败成本与最小执行环，用同一个真实任务对候选框架做小规模实测（记录首次可用时间、自写代码量、治理缺口），再按缺口反向选择生命体征健康的最薄脚手架；治理三件套（权限审批、检查点恢复、执行边界）不可省，版本必须精确锁定。**

模式名中的"充分"指对**本任务**充分，而非对框架能力清单充分——显式写下"不要哪些部件"与写下"要哪些"同等重要。

支撑该模式的三组外部证据（详见[上游知识包 F 编号事实](../../../../knowledge/tech/python-agent-harness/index.md)）：

1. **厚 scaffold 的边际收益在缩小**：mini-swe-agent 约 131 行在 SWE-bench Verified 取 65%、每任务约 0.37 美元；SWE-agent 约 4161 行取 67%、约 2.50 美元——2 个百分点之差对应约 30 倍代码与约 7 倍成本（F-032，单一来源，口径见知识包 04 概念页）。
2. **上手成本差异可达数倍且可实测**：同一任务的第三方实测中，七个框架 TTFA 分布为 7–26 分钟、自写代码 18–84 行（F-003，单一第三方来源，仅作量级假设）。
3. **全自主/无预算路线有过完整退潮**：AutoGPT 16 天约 5 万星后未落地为通用生产方案，四类失败形态（上下文溢出、自我判定完成、成本无界、递归不收敛）正是今天 harness 审批、预算闸、规划深度上限等部件的由来（F-006/F-007）。

## 触发场景

**适用于**：

- 要在 2 个以上 agent 框架/SDK/harness 之间做引入决策（Python 包形态为主，思想可外推）
- 新 agent 应用立项，团队对"用多重的框架"存在分歧
- 已有 agent 原型要走向生产，需要判断该补哪些治理部件
- 赛道处于高速迭代期：候选项目普遍 0.x 版本、近期发生过合并/更名（本模式的生命体征检查即为此设计）

**不适用于**：

- 技术栈已被公司平台/采购/合规前提强制指定（决策空间不存在）
- 一次性、无副作用的脚本任务——选型成本高于框架成本，直接用最薄工具
- 纯 RAG 检索类应用（问题域不同，应走检索质量评测路线）
- 采购周期以月计、无法做同任务实测的封闭商业软件——此时用重量型评分框架（见下节关系表），本模式退化为任务分级 + 生命体征尽调两步

## 核心做法（6 步）

### 步骤 1：任务分级——先算失败账，再选技术栈

按三维度定级，任一维度为"高"即把对应治理部件标为**必需**：

| 维度 | 低端 | 高端 | 高端触发的必需部件 |
|---|---|---|---|
| 单次失败成本 | 只读分析、可丢弃 | 改生产代码/花钱/对外发消息 | 权限审批、动作拦截 |
| 任务时长 | 分钟级、一轮对话 | 小时级、跨会话 | 检查点/脱水恢复 |
| 可并行性 | 单线程 | 子任务可切分且各有验收标准 | tracing 先行，再谈编排 |

多智能体编排另设三条硬门槛（来自 Anthropic 工程数据：orchestrator-worker 效果 +90.2% 但 token 约 15 倍，且故障集中在编排与交接面，F-005）：**可并行切分 + 子任务有独立验收标准 + 价值密度覆盖约 15 倍 token 成本**，三条缺一不引入编排。

### 步骤 2：定义最小执行环

写下四件套底线：**模型客户端 + 工具面 + 文件/产物空间 + 执行隔离**。再对照 harness 九大部件（规划、文件系统、子智能体、记忆、上下文压缩、shell、skills、审批、MCP）逐项标注**必需/可选/不要**。"不要"清单是抵制满配框架诱惑的书面依据。

### 步骤 3：同任务小赛（模式的核心动作）

- ≥2 个候选框架，用**同一个真实任务**（不是 hello world）各做一遍；
- 记录三个数：**TTFA**（建虚拟环境到首次成功运行的分钟数）、**LOC**（自写胶水代码行数）、**治理缺口清单**（对照步骤 2 的必需部件，缺几个）；
- 外部实测数字（7–26 分钟/18–84 行）只作量级假设，不可作为决策依据；自己团队半天的实测比任何第三方文章都可信；
- 编码 agent 赛道可用同一真实 issue 复现"薄栈对厚栈"的成功率与成本对照。

### 步骤 4：生命体征检查（防选中"明日维护模式"）

对小赛胜出候选做四项检查：

1. 最近发版日期与发版频率（0.x 高频发版要配套读 CHANGELOG）；
2. 合并/更名/继任公告（AutoGen+SK→MAF、Swarm→Agents SDK、Phidata→Agno、OpenDevin→OpenHands 均有此类事件，F-040）；
3. 官方文档/cookbook 是否 pin 版本并警告 API 频变（OpenAI cookbook 长期 pin 0.9.3 即是信号，F-016）；
4. issue/发版说明中检索 `maintenance`、`archived`、`sunset`（AutoGen 维护模式、SWE-agent maintenance-only 为前车之鉴）。

任一红灯：选择官方继任者，或在架构中预留迁移锚点。

### 步骤 5：按缺口选最薄栈，治理三件套不可省

在覆盖必需部件的候选中选**最薄**者；无论栈多薄，三件套不可省：**权限/审批**（危险动作默认拦截）、**检查点/可恢复性**（进程终止后能续跑）、**执行边界**（进程内沙箱还是容器，按失败成本选派别——执行不可信代码优先容器派）。模型绑定按战略选择：深度用单一厂商可选运行时绑定型 SDK；要保留议价权选多 provider 抽象或 LiteLLM 兼容型。

### 步骤 6：锁版本、留预案

生产依赖精确锁定（`==` 而非 `>=`）；0.x 包的框架升级作为独立变更走完整回归；业务代码与框架 API 之间保留一层薄适配（agent 定义、工具签名、消息格式不散落在业务代码各处），作为合并/更名事件的保险费。

## 反模式

1. **按热度/star 选型**：star 是滞后指标且时点敏感，不反映项目生命状态（约 58.9K stars 进入维护模式已有实例，F-013）。
2. **demo 同质就上线**：所有框架在客服/研究助理 demo 上都能跑；分化只发生在长任务、恢复、审计与成本这些高端维度。
3. **跳过同任务小赛直接押注**：他人的"顺手"不可替代本团队实测；小赛成本约半天，选错成本约一个季度。
4. **把维护模式/0.x 频变栈当稳定基座**：不锁版本、不读 CHANGELOG、业务代码直接继承框架基类——每次发版都以生产故障还账。
5. **一上来就多智能体编排**：在子任务缺独立验收标准时上 orchestrator-worker，等于用约 15 倍 token 购买最难调试的交接面故障。永远先跑通单 agent + 工具。

## 检验标准

模式被正确执行后，应留下五份可审计产物：

1. **任务分级记录**：三个维度各有定级与依据；
2. **最小执行环清单**：每件部件标注必需/可选/不要；
3. **同任务小赛记录**：≥2 候选 × TTFA/LOC/治理缺口三个数；
4. **生命体征检查表**：四项均有结论与检查日期；
5. **锁定的依赖清单**：所有 0.x/早期包精确锁版本，业务代码与框架之间存在适配层。

架构复核中追加一问：每个被启用的厚部件都要能回答"它对应哪个失败案例或高端维度"；答不上来的部件按"不要"处理。

## 迁移示例

- **工作流编排引擎选型（Temporal/Airflow/Celery 类）**：三维度分级直接通用；最小执行环换成"队列 + worker + 状态存储 + 幂等边界"；同任务小赛换成同一订单履约流程跑两个引擎；生命体征检查在 Airflow 生态分叉史中同样有效；治理三件套对应重试幂等、超时策略、死信队列。
- **前端组件库/状态管理库选型**：最小执行环换成"组件覆盖 + 主题定制 + SSR 兼容 + 打包体积"；同任务小赛用同一页面在 ≥2 个库实现；生命体征检查（发版频率、维护公告、renovate 迁移成本）不变。
- **已知边界（不可外推）**：封闭商业软件/硬件设备选型，同任务小赛受采购周期限制不可行，模式退化为步骤 1+2+4，步骤 3 以合同条款 POC 替代，重量评估让渡给 [P-AGENT-SELECT-001](P-AGENT-SELECT-001-agent-platform-selection-framework.md) 的 9 维评分卡。

## 与现有模式的关系

| 相关模式 | 关系 | 说明 |
|---|---|---|
| [P-AGENT-SELECT-001 企业级 Agent 平台 9 维选型框架](P-AGENT-SELECT-001-agent-platform-selection-framework.md) | 轻重互补 | 该模式面向企业采购（3+ 候选、9 维加权、评分卡、PoC、锁定评估），组织级重量决策；本模式面向团队/个人为具体任务选 Python 库，半天可完成的轻量实测决策。候选不可实测（封闭商业平台）时本模式让渡给该模式 |
| [harness-architecture-layered-model](harness-architecture-layered-model.md) | 选型↔构建 | 该模式回答"自己构建 harness 时需要哪五层骨架"；本模式回答"在现成 harness 之间怎么选"。本模式步骤 2 的九大部件清单是其五层骨架在 2026 年厂商产品上的实证展开 |
| [tech-selection-three-checks](tech-selection-three-checks.md) | 原则→领域落地 | 选型三查是通用原则（查权威文档、查现有实例、查本质目标）；本模式是 agent 这种高速迭代赛道上的专用流程，步骤 4 的生命体征检查是"查权威文档"在该赛道的具体化 |
| [vendor-lifecycle-governance](vendor-lifecycle-governance.md) | 生命周期衔接 | 该模式治理 vendor 依赖全生命周期；本模式步骤 4/6 是其入口端（引入前尽调与锁版本）在 agent 赛道的预填表单 |
| [bounded-iteration-budget](bounded-iteration-budget.md) | 预算原则支撑 | 多智能体三门槛与步骤 1 的成本分级，是有限迭代预算原则在 agent 编排决策上的实例 |
| [prove-usefulness-check](prove-usefulness-check.md) | 验证原则支撑 | 步骤 3 同任务小赛即"先证明有用再引入"原则的操作化 |

## 沉淀与校验记录

- **上游会话**：`sc-20260930-python-agent-harness`（R→I→E→V→C，45 事实/4 洞察），知识包位置 [docs/knowledge/tech/python-agent-harness/](../../../../knowledge/tech/python-agent-harness/index.md)；
- **沉淀会话**：`sc-20260930-pattern-mss-sediment`（2026-09-30）；
- **去重判定**：入库前比对 P-AGENT-SELECT-001（采购向）、harness-architecture-layered-model（构建向）、tech-selection-three-checks（通用原则）三者，决策对象、决策重量、核心动作均不同，不构成重复，关系见上表；
- **成熟度二次校验（沉淀 V 门）**：知识包初版按"≥2 独立案例"自标 L2；入库对照模式库等级表发现 L2-validated 另含"已在本项目验证"要件，本模式仅有外部案例，**降级为 L1-draft** 并回改知识包定级；升级条件：本团队完成一次真实 agent 选库实战并回填验证记录；
- **外部证据使用纪律**：F-003（TTFA/LOC）与 F-032（行数/成本对照）均为单一第三方来源，模式正文中只作量级假设与机制例证，检验标准不依赖其数值成立。
