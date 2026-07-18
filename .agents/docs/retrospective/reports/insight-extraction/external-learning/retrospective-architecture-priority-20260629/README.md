---
id: "retrospective-architecture-priority-20260629"
title: "架构优先级评估与重构路线图：基于 Firecrawl 8 洞察"
version: "1.1"
source: "Firecrawl 8 Insights → SpecWeave Architecture Assessment"
scenario: "B-single-day-medium"
template_upgrade: "2026-07-06 v1.2"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/README.toml"
---
# 架构优先级评估与重构路线图：基于 Firecrawl 8 洞察

> **分析基础**：Firecrawl 深度学习萃取的 8 个核心洞察
> **评估对象**：SpecWeave 当前架构（规范体系/角色协议/Skill体系/脚本工具/自我演进模块）
> **评估日期**：2026-06-29
> **完成日期**：2026-07-01
> **报告状态**：✅ P0+P1 模块全部实施完成，P2 模块择机实施
> **报告类型**：架构优先级评估报告（洞察驱动）
> **关联报告**：[retrospective-firecrawl-learning-20260629](../retrospective-firecrawl-learning-20260629/README.md)

## 📂 文件索引

| 文件 | 内容 |
|------|------|
| **README.md**（本文件） | 主报告：现状诊断、差距矩阵、重构模块方案、路线图、风险应对 |
| [execution-retrospective.md](execution-retrospective.md) | 执行过程复盘索引页 |
| [execution/](execution/README.md) | 执行复盘原子化文件：事实、分析、元洞察、建议 |
| [insight-extraction.md](insight-extraction.md) | 深层架构洞察索引页：6个可复用架构模式导航 |
| [insights/](insights/README.md) | 6个原子化洞察文件（每个文件单一主题） |
| [export-suggestions.md](export-suggestions.md) | 知识沉淀与行动建议索引页 |
| [export/](export/README.md) | 建议原子化文件：6个模式详情、知识路径、行动项 |
| [insight-action-backlog.md](insight-action-backlog.md) | 洞察行动项Backlog：行动项总览、详情、执行记录 |

## 📊 核心指标

- **范式转移**：✅ Human-First（文档驱动）→ Agent-First（自主发现），已完成渐进式披露三层架构落地
- **重构模块**：✅ P0 3个 + P1 2个 全部完成；P2 3个（规范分层/模型路由/资源调度）择机实施
- **不重构项**：6项（阶段守卫/角色/工作流/协议/硬编码规则/自我演进模块）全部遵守
- **Skill化成果**：14个SKILL.md（5个指令集门面 + 5个脚本门面 + 2个集成类 + 2个新增命令）
- **可复用模式**：6个全部沉淀至模式库（渐进式披露架构→ARCHITECTURE.md，其余5个→docs/retrospective/patterns/）
- **质量保障**：282个测试全部通过（含50个CLI边界测试、20个性能基准测试），Windows编码兼容性修复

---

## 一、现状诊断：根本矛盾

### 范式错配

经过对核心模块的深入分析，当前 SpecWeave 架构存在一个根本性范式错配：

```mermaid
flowchart LR
    subgraph 当前范式["当前架构：Human-First（面向人类阅读）"]
        A1["📄 Markdown 规范文档"] --> A2["AI 阅读理解规则"]
        A3["📄 指令集文档"] --> A2
        A4["📄 协议文档"] --> A2
        A5["🔧 散落的脚本"] --> A2
        A2 --> A6["每次会话重新读取全部文档"]
    end
    subgraph 目标范式["目标架构：Agent-First（面向 Agent 自主发现）"]
        B1["🔍 统一能力注册中心"] --> B2["Agent 自主发现可用能力"]
        B3["⚡ SKILL.md 机器可读描述"] --> B2
        B4["🚀 零配置试用"] --> B2
        B2 --> B5["按需加载深度上下文"]
    end
    A6 -.->|"范式错配"| B2
```

**核心矛盾**：SpecWeave 的规范体系（阶段守卫、PDR协议、工作流等）已非常成熟，但它们都是"写给 AI 读的文档"，而非"让 Agent 自主发现和调用的服务"。这直接对照 Firecrawl 洞察1（Keyless）和洞察4（Agent-Readable Service Description）——当前架构是 Human-First，需要向 Agent-First 演进。

### 当前架构成熟度评估（2026-07-01 更新）

| 架构层 | 评估时成熟度 | 当前成熟度 | 变化说明 |
|--------|-------------|-----------|---------|
| 规范层（rules/protocols） | 🟢 L4 成熟 | 🟢 L4 成熟 | 未重构，保持稳定 |
| 角色层（roles/teams） | 🟢 L4 成熟 | 🟢 L4 成熟 | 未重构，保持稳定 |
| 工作流层（workflows） | 🟢 L3 可用 | 🟢 L4 成熟 | Skill化入口封装完成 |
| Skill层（skills/） | 🟡 L2 起步 | 🟢 L4 成熟 | 从1个增至14个SKILL.md，覆盖全部指令集+高频脚本 |
| 指令集层（commands/） | 🟡 L2 文档态 | 🟢 L4 成熟 | 5个指令集全部SKILL化，具备决策树和安全清单 |
| 脚本工具层（scripts/） | 🟡 L2 半封装 | 🟢 L3 可用 | 第一批5个高频脚本Skill化，共享库提取+边界测试 |
| 能力发现层 | 🔴 L0 缺失 | 🟢 L3 可用 | ONBOARDING.md+capability-registry.md建成，三层架构落地 |
| 自我演进模块（modules/） | 🔴 L1 规划态 | 🟡 L2 起步 | 复盘/洞察/萃取流程已跑通，自我迭代能力初步验证 |

---

## 二、8 洞察 × 当前架构差距矩阵（2026-07-01 更新）

| 洞察 | 评估时状态 | 当前状态 | 差距等级 |
|------|-----------|---------|---------|
| **1. Keyless/Agent-First API** | 所有能力需先读文档才能使用 | ✅ ONBOARDING.md入口+REGISTRY注册表，Agent可零配置发现能力 | 🟢 已解决 |
| **2. Open Core + 托管差异化** | 核心规范和工具脚本混在一起 | 🟡 capabilities/分层已建立，tools/core边界待明确 | 🟡 P2-待实施 |
| **3. Tiered Credit Economy** | self-management纸面规划 | ⚪ 单Agent场景不紧迫，未实施 | ⚪ P2-延迟 |
| **4. Agent 可读服务描述** | 仅1/40+能力有SKILL封装 | ✅ 14个SKILL.md覆盖指令集+高频脚本+集成，三层披露架构 | 🟢 已解决 |
| **5. 全渠道对等接入** | 多入口不对等 | ✅ 所有指令集均有-cmd后缀Skill门面，可统一触发 | 🟢 已解决 |
| **6. 运营型护城河** | 内部工具场景不适用 | ⚪ 不适用 | ⚪ 不适用 |
| **7. 双模型成本弹性** | 无模型选择层 | 🟡 prompt层面引导已建立，model_hint字段待设计 | 🟡 P2-待实施 |
| **8. 三角验证法** | 未要求多源验证 | ✅ triangular-source-verification.md沉淀为正式模式 | 🟢 已解决 |

---

## 三、需要重构的核心模块（按优先级排序）

### 🔴 P0 级：架构级重构（必须做，影响全局交互范式）—— ✅ 全部完成

#### 重构模块 1：能力注册与发现中心（Capability Registry）—— ✅ 已完成（2026-06-30）

**对照洞察**：1（Keyless）+ 4（Agent-Readable Service Description）

**现状问题**：
- 当前 Agent 想知道系统"能做什么"，必须遍历 [.agents/README.md](../../../../../../README.md) → commands/ → protocols/ → workflows/ → scripts/ → skills/ 多个目录
- 没有统一的"系统能力清单"入口
- 新会话开始时，PDR协议要求重新读取所有前置文档，但Agent不知道"有哪些文档需要读"

**重构方案**：

```mermaid
flowchart TB
    subgraph 新增["新增层"]
        REG["🔍 .agents/capabilities/REGISTRY.md<br/>（统一能力注册表）"]
        DISCOVER["🚀 .agents/capabilities/ONBOARDING.md<br/>（Agent Onboarding入口）"]
    end
    subgraph 现有["现有能力（SKILL.md封装）"]
        C1["commands/ → .agents/skills/<command-name>/SKILL.md"]
        C2["scripts/ → .agents/skills/<script-name>/SKILL.md"]
        C3["workflows/ → .agents/skills/<workflow-name>/SKILL.md"]
        C4["现有skills/forum-posting/"]
    end
    REG --> C1
    REG --> C2
    REG --> C3
    REG --> C4
    DISCOVER --> REG
```

**具体变更**：
1. 新建 `.agents/capabilities/` 目录（P0模块1实施时创建）
2. 创建 `ONBOARDING.md`——Agent 系统入口（类似 Firecrawl 的 `/agent-onboarding/SKILL.md`），包含：
   - 系统能力概览（我是谁、我能做什么）
   - 快速开始路径（零配置试用）
   - 注册表索引链接
3. 创建 `REGISTRY.md`——全量能力注册表，每个能力一行：ID、名称、触发词、SKILL.md路径、类型
4. 定义能力类型枚举：`command`（指令集）、`script`（脚本工具）、`workflow`（工作流）、`protocol`（协议）、`integration`（外部集成）

---

#### 重构模块 2：指令集 Skill 化改造（5 个指令集 → 标准 Skill）—— ✅ 已完成（2026-06-30）

**对照洞察**：1（Keyless）+ 4（Agent 可读描述）+ 5（全渠道对等）

**现状问题**：
- 5个指令集（[retrospective.md](../../../../README.md)、[insight.md](../../../../../../commands/insight.md)、[atomization.md](../../../../../../commands/atomization.md)、[export-report.md](../../../../../../commands/export-report.md)、[atomic-commit.md](../../../../../../commands/atomic-commit.md)）目前只是Markdown文档
- Agent需要"阅读并理解"文档才能执行指令集流程，而非通过标准SKILL接口调用
- 指令集缺少frontmatter元数据（触发词、参数、输出格式）

**重构方案**：

为每个指令集创建标准SKILL.md，遵循已有的 [SKILL-TEMPLATE.md](../../../../../../skills/SKILL-TEMPLATE.md) 五要素模型：

| 指令集 | SKILL.md路径 | 核心封装内容 |
|-------|-------------|------------|
| retrospective | `.agents/skills/retrospective/SKILL.md` | 复盘4步流程、fact模板、时间线画法、输出格式 |
| insight | `.agents/skills/insight/SKILL.md` | 数据分析流程、根因分析、三源验证法、异常识别 |
| atomization | `.agents/skills/atomization/SKILL.md` | 原子化拆分规则、单一职责原则、拆分检查清单、导航更新流程 |
| export-report | `.agents/skills/export-report/SKILL.md` | 报告格式选择、元数据规范、归档路径、索引更新 |
| atomic-commit | `.agents/skills/atomic-commit/SKILL.md` | 提交分组、Conventional Commits格式、会话边界原则 |

**关键设计决策**：
- 原 commands/ 目录中的文档保留作为深度参考（Progressive Disclosure：常用内容内联在SKILL.md，低频内容引用原文档）
- SKILL.md 控制在500行以内
- 每个SKILL.md包含：触发词、决策树、执行步骤、安全检查清单、错误处理
- 参考样板：[forum-posting/SKILL.md](../../../../../../skills/forum-posting/SKILL.md)

---

#### 重构模块 3：Agent Onboarding 协议（替代 PDR 的强制读取范式）—— ✅ 已完成（2026-06-30）

**对照洞察**：1（Keyless）+ 4（Agent可读描述）

**现状问题**：
- 当前 [pre-document-reading.md](../../../../../../protocols/pre-document-reading.md) 要求新会话"重新读取所有前置文档"
- 这是 Human-First 思维：AI记忆清零→必须重新读所有文档
- 问题：读太多不必要文档浪费上下文窗口，读太少又缺失关键信息

**重构方案**：

将PDR从"强制全量读取"升级为"渐进式按需加载"：

```mermaid
flowchart LR
    A["新会话开始"] --> B["读取 ONBOARDING.md<br/>（轻量<100行）"]
    B --> C{"任务类型判断"}
    C -->|"复盘任务"| D["加载 retrospective SKILL"]
    C -->|"开发任务"| E["加载 feature-development + 相关角色SKILL"]
    C -->|"审查任务"| F["加载 code-review SKILL"]
    C -->|"未知类型"| G["查询 REGISTRY.md<br/>发现匹配能力"]
    D --> H["按需加载深度文档"]
    E --> H
    F --> H
    G --> H
    H --> I["执行任务"]
```

**具体变更**：
1. 新协议文件：`.agents/protocols/agent-onboarding.md`
2. ONBOARDING.md 作为Agent系统入口，内容精简（<100行）：
   - 系统身份（SpecWeave 多Agent协作规范框架）
   - 核心能力速查（5个指令集+3个工作流+高频脚本）
   - 任务类型→加载哪个SKILL的路由表
   - 如何查询完整注册表
3. 修改PDR协议：将"全量必读"改为"ONBOARDING必读+按需加载"
4. 保留📋确认机制，但确认内容从"已读取所有文档"变为"已加载ONBOARDING+相关SKILL"

---

### 🟡 P1 级：高价值增强（应该做，显著提升质量）—— ✅ 全部完成

#### 重构模块 4：三角验证法标准化（洞察8落地）—— ✅ 已完成（2026-06-30）

**对照洞察**：8（三源信息三角验证）

**现状问题**：
- [insight.md](../../../../../../commands/insight.md) 指令集没有要求多源信息验证
- 做外部研究/竞品分析时，容易只依赖单一信息源

**重构方案**：
1. 在 insight SKILL.md（模块2创建）中增加"信息采集规范"章节：
   - 外部产品研究必须覆盖：技术源（官方文档/GitHub）+ 商业源（定价/案例）+ 第三方源（评测/社区）
   - 交叉验证检查清单：关键数据点至少2个源确认
   - 缺口标注规则：单一来源信息必须标注可信度
2. 本次 Firecrawl 学习已实践此方法，将其模式化

**工作量**：极小（在SKILL.md中增加一个章节），价值极高（提升所有洞察报告质量）。

---

#### 重构模块 5：高频脚本 Skill 化覆盖—— ✅ 已完成（2026-07-01）

**对照洞察**：4（Agent可读描述）+ 5（全渠道对等）

**现状问题**：
- `.agents/scripts/` 下有 40+ Python 脚本，但没有SKILL封装
- Agent不知道什么时候该用哪个脚本，需要阅读脚本源码或README
- 脚本参数、输出格式、使用约束没有机器可读描述

**重构方案**：
按使用频率分批封装高频脚本为Skill：

**第一批（最高频，已完成封装）**：

| 脚本 | 实际Skill名 | 触发词 |
|------|---------|--------|
| [check-links.py](../../../../../../scripts/check-links.py) | link-check-cmd | 链接检查、检查断链、fix links |
| [docgen.py](../../../../../../scripts/docgen.py)（含generate-dashboard/generate-nav） | docgen-cmd | 生成导航、更新看板、docgen |
| [ci-check.ps1/sh](../../../../../../scripts/ci-check.ps1) | ci-check-cmd | CI检查、提交前检查、ci-check |
| [finalize-atomization.py](../../../../../../scripts/finalize-atomization.py) | atomization-finalize-cmd | 原子化收尾、断链修复、finalize |
| [check-duplication.py](../../../../../../scripts/check-duplication.py) | check-duplication-cmd | 重复代码、重复检查、check-duplication |

**第二批（中频封装）**：
- check-spec-consistency.py、generate-nav.py、build-ref-index.py、check-source-traceability.py、ci-check.ps1

**第三批（低频按需封装）**：
- 其余脚本在使用时按需封装

每个脚本Skill的SKILL.md包含：功能描述、触发词、常用命令速查、参数表、输出说明、常见错误。

---

### 🟢 P2 级：前瞻性设计（择机实施）—— ⏳ 待实施

#### 重构模块 6：规范分层治理（洞察2落地）

**对照洞察**：2（Open Core + Managed Differentiation）

**重构内容**：明确区分 `.agents/` 中两类内容：
- **Core（核心规范，必须遵守）**：roles/、protocols/、rules/、capabilities/（新）、skills/（指令集SKILL）
- **Tools（工具能力，可选使用）**：scripts/、templates/、skills/forum-posting等集成类Skill

当前结构已隐含此分层，只需在 [.agents/README.md](../../../../../../README.md) 中明确化。

---

#### 重构模块 7：模型路由层（洞察7落地）

**对照洞察**：7（Dual-Model Cost-Quality Switch）

**重构内容**：
- 在SKILL.md frontmatter中增加`model_hint`字段（`fast`/`balanced`/`precise`）
- Agent根据任务类型和SKILL提示选择合适的推理策略
- 注意：受限于Trae平台，可能只能在prompt层面引导，无法实际切换模型API

---

#### 重构模块 8：资源调度框架（洞察3落地）

**对照洞察**：3（Tiered Credit Economy）

**重构内容**：
- 对应 [self-management.md](../../../../../../modules/self-management.md) 的资源分配能力
- 多Agent并发场景下的任务优先级调度
- 当前单Agent使用不紧迫，待多Agent协作场景落地时实施

---

## 四、不建议重构的项

| 当前模块 | 不重构原因 |
|---------|-----------|
| **阶段守卫（stage-guardrails）** | 设计极其成熟，SG-LOG/PDR-LOG结构化日志、8阶段边界、拦截机制都已完善，无需改动 |
| **角色体系（roles/）** | 6+1扁平角色定义清晰，职责边界明确，协作场景文档完善 |
| **工作流（workflows/）** | 三路径（新功能/扩展/重构）设计合理，只需Skill化封装入口，核心流程不变 |
| **协议层（handoff/messaging/conflict）** | 协议设计完整，不需要重构 |
| **硬编码治理规则（rules/）** | 规则体系完整，5个文档形成闭环 |
| **Self-evolution 8模块** | 是规划蓝图，当前无需重构——等Skill体系完善后，这些模块的实现可基于Skill架构 |

---

## 五、重构路线图

```mermaid
gantt
    title SpecWeave 架构重构路线图（实际执行）
    dateFormat YYYY-MM-DD
    section P0 核心重构 ✅
    模块1: 能力注册中心 (REGISTRY+ONBOARDING)    :done, a1, 2026-06-30, 1d
    模块2: 指令集Skill化(5+1个)                  :done, a2, 2026-06-30, 1d
    模块3: Agent Onboarding协议                  :done, a3, 2026-06-30, 1d
    section P1 增强 ✅
    模块4: 三角验证法标准化                      :done, b1, 2026-06-30, 4h
    模块5a: 第一批高频脚本Skill化(5个)           :done, b2, 2026-07-01, 1d
    质量保障: 单元测试+性能基准+编码兼容性修复     :done, b3, 2026-07-01, 1d
    section P2 前瞻 ⏳
    模块6: 规范分层治理                          :c1, 2026-07-02, 4h
    模块7: 模型路由层                            :c2, after c1, 1d
    模块8: 资源调度框架                          :c3, after c2, 1d
```

### 实施顺序说明（实际执行）

**第一波（P0，2026-06-30，约3天压缩为1天）：范式转移** ✅
1. ~~**先做模块1**（注册表+Onboarding入口）~~ — 与模块2/3并行实施，`.agents/capabilities/` 目录和 `.agents/ONBOARDING.md` 同步创建
2. ~~**再做模块2**（5个指令集Skill化）~~ — 实际完成6个（5个规划+1个mermaid-cmd），命名统一使用`-cmd`后缀
3. ~~**最后做模块3**（Onboarding协议）~~ — 同步完成，`.agents/protocols/onboarding-protocol.md` 创建

**第二波（P1，2026-07-01，约2天压缩为1天）：能力扩展+质量保障** ✅
4. ~~**模块4**（三角验证法）~~ — `triangular-source-verification.md` 沉淀为正式模式
5. ~~**模块5a**（第一批高频脚本Skill化）~~ — 实际完成5个（link-check-cmd/docgen-cmd/ci-check-cmd/atomization-finalize-cmd/check-duplication-cmd）
6. **质量保障（计划外增量）**：补充单元测试（282个用例）、性能基准测试（20个benchmark）、Windows编码兼容性修复（6处防御性改进）、YAML frontmatter注释规则修复、模式库沉淀

**第三波（P2，待实施）：完善优化** ⏳
7. **模块6-8**——分层治理、模型路由、资源调度，择机实施

### 计划偏差分析

| 维度 | 计划 | 实际 | 偏差原因 |
|------|------|------|---------|
| P0工期 | ~4天 | ~1天 | P0模块间依赖不强，可并行实施；Skill创建有SKILL-TEMPLATE和forum-posting样板，效率远超预期 |
| P1工期 | ~2.5天 | ~1天 | 第一批脚本Skill化有P0 Skill创建经验，模式复用快速；三角验证极小工作量 |
| 质量保障 | 未单独规划 | 1天 | 执行中发现编码兼容性Bug、YAML解析Bug、需要测试覆盖，补充了质量工作 |
| Skill总数 | 5指令+5脚本=10 | 6指令+5脚本+2集成+1模板=14 | mermaid-cmd作为第六个指令集补充；home-assistant和forum-posting为已有集成Skill |

---

## 六、重构风险与应对

| 风险 | 应对策略 | 实际效果 |
|------|---------|---------|
| **向后兼容**：原commands/文档是否保留？ | 保留。SKILL.md是"入口和索引"，原文档作为深度参考（Progressive Disclosure） | ✅ 原commands/目录完整保留，SKILL.md引用L2层文档 |
| **PDR协议变更影响阶段守卫** | 保持📋确认机制格式不变，只改变"确认什么" | ✅ Onboarding协议与PDR共存，启动协议仍以AGENTS.md为最高入口 |
| **Skill数量膨胀** | 分批封装，第一批只做5个最高频脚本 | ✅ 严格遵守，5个脚本Skill完成后暂停，其余按需封装 |
| **SKILL.md质量不一致** | 严格遵循SKILL-TEMPLATE和skill-development.md五要素 | ✅ 通过check-skill-quality.py验证，5个脚本Skill全部通过质量门 |
| **ONBOARDING.md过时风险** | REGISTRY.md可考虑脚本自动生成 | 🟡 初期手动维护，后续可考虑docgen聚合 |
| **Windows编码兼容性**（计划外风险） | 未提前识别 | ✅ 通过防御性属性访问三层防护+cp65001白名单+TTY安全检测修复 |

---

## 七、可复用模式沉淀

6个从本架构评估萃取的可复用模式已全部沉淀至正式模式库：

| 模式ID | 模式名称 | 沉淀位置 | 成熟度 |
|--------|---------|---------|--------|
| P-ARCH-001 | 渐进式披露架构 | [.agents/capabilities/ARCHITECTURE.md](../../../../../../capabilities/ARCHITECTURE.md)（L2正式规范） | L3 稳定 |
| P-ARCH-002 | Markdown即接口 | [markdown-as-interface.md](../../../../patterns/methodology-patterns/ai-collaboration/markdown-as-interface.md) | L2 已验证 |
| P-ARCH-003 | 瓶颈优先重构法 | [bottleneck-first-refactoring.md](../../../../patterns/methodology-patterns/governance-strategy/bottleneck-first-refactoring.md) | L2 已验证 |
| P-ARCH-004 | 不重构清单 | [no-touch-list.md](../../../../patterns/methodology-patterns/governance-strategy/no-touch-list.md) | L2 已验证 |
| P-ARCH-005 | 架构决策三角验证 | [triangular-source-verification.md](../../../../patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md) | L2 已验证 |
| P-ARCH-006 | 元能力依赖倒置 | [meta-capability-inversion.md](../../../../patterns/architecture-patterns/meta-capability-inversion.md) | L2 已验证 |

---

## 关联报告

- [retrospective-firecrawl-learning-20260629](../retrospective-firecrawl-learning-20260629/README.md) — Firecrawl系统学习复盘（8个洞察来源）
- [retrospective-deer-flow-2-learning-20260625](../retrospective-deer-flow-2-learning-20260625/README.md) — DeerFlow 2.0学习复盘
- [retrospective-comprehensive-extraction-20260626](../../meta-methodology/retrospective-comprehensive-extraction-20260626/README.md) — 综合萃取复盘
