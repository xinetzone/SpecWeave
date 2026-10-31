---
id: "convergence-period-triple-track"
title: "收口期三线闭环：版本定源、约定门禁化与文档诚实化的顺序治理"
type: "Pattern"
domain: "methodology"
layer: "governance-strategy"
maturity: "L1"
maturity_level: "L1-draft"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
version: "1.0.0"
created_date: "2026-10-29"
last_updated: "2026-10-29"
source: "../../../reports/2026-10-29-xuanspace-october-governance-retro.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/convergence-period-triple-track.toml"
tags:
  - release-governance
  - convergence
  - single-source-of-truth
  - quality-gate
  - documentation
  - ordering
trigger_conditions:
  - "项目进入发布前收口期（版本发布、里程碑交付、上线前），存量治理债需要在有限窗口内清偿"
  - "版本/许可/构建元数据存在多声明点，且一致性靠人工记忆维持"
  - "规范文档中的「应当」没有对应的可执行门禁，存量漂移未被曝光"
  - "文档中存在失效陈述（失效报告、失真示例、过时索引），且无人敢删（怕删错）"
problem_solved: "收口期常见的错误是「只加功能不治理」或「先改文档后改实现」。前者让漂移继续累积到发布后爆发；后者在没有版本背书与门禁验证时删文档，删错即制造新失真。本模式把收口期治理组织为三条有序主线——版本元数据定源 → 约定门禁化 → 文档诚实化，后一条线以前一条线落定为前提，使收口期的工作顺序可判定、可预检、可复盘。"
related_patterns:
  - "single-authority-declaration-alignment"
  - "release-eligibility-invariant-gate"
  - "version-ripple-grep-sweep"
  - "governance-three-stage-evolution"
  - "three-layer-rule-enforcement"
---

# 收口期三线闭环

## 模式类型

方法论模式 → 治理策略（发布前收口期的工作组织与顺序约束）

## 成熟度

L1（`maturity_level` = L1-draft；单案例：xuanspace 十月治理收口，2026-10-29 复盘；validation_count = 1，reuse_count = 0）。
案例覆盖完整三线（版本定源 / 门禁固化 / 文档清理）与顺序执行，但仅一个项目谱系，
跨项目第二次验证缺失，故不高于 L1。

## 一句话

发布前收口期的治理不是「把该做的都做了」，而是**按「版本可信 → 机器可验证 → 文档诚实」的顺序推进三条线**——先定唯一事实来源，再固化为可执行门禁，最后才删除失效陈述；顺序颠倒会让每一步都失去执行前提。

## 适用场景

**适用于：**

1. 项目进入发布前收口期，存量治理债需要在有限窗口内清偿；
2. 版本/许可/构建元数据存在多声明点（pyproject + `__version__` + 文档徽章等）；
3. 规范文档中的「应当」没有门禁背书，存量漂移从未被系统曝光；
4. 文档中存在失效陈述，团队「想删但不敢删」或「删了又后悔」。

**不适用于：**

- 项目不在收口期、无发布压力的持续开发——日常治理按
  [single-authority-declaration-alignment](single-authority-declaration-alignment.md) 或
  [governance-three-stage-evolution](governance-three-stage-evolution.md) 执行即可；
- 单一载体、无声明面分叉的项目——无三线可治；
- 发布路径本身有问题（版本坐标不闭合、质量关卡错位）——
  应先按 [release-eligibility-invariant-gate](release-eligibility-invariant-gate.md) 治理发布资格。

## 问题背景

收口期（release convergence）是治理债的集中清偿窗口，但常见的两种做法都有问题：

**做法一：只加功能不治理。** 版本号三处声明、构建后端两套并存、README 与目录
实态不符——这些漂移继续累积，发布后以「用户照文档踩空」「CI 时好时坏」的形式爆发，
收口期省下的时间在发布后加倍偿还。

**做法二：先改文档后改实现。** 团队意识到文档失真，直接动手删失效陈述——
但版本与构建元数据尚未定源，门禁尚未验证「声明 vs 实现」是否一致，
删哪条、留哪条全凭人工判断，删错即制造新失真；更常见的是「不敢删」，
因为没有任何机器证据证明某条陈述确实失效。

本模式的洞察来自 xuanspace 十月治理收口（2026-10-23 ~ 10-28）：
73 次提交、378 个文件，呈现清晰的「版本定源（10-23~27）→ 门禁固化（10-24~28）→
文档诚实化（10-28）」三线顺序。文档治理提交占比最高（26/73，35.6%），
但它不是收尾杂务——删除失效依赖报告、消除输出示例失真这些动作，
只有在前两条线落定后才具备执行条件。

## 失败案例：xuanspace 0.1.0 发布后的 CI 不稳定期

**案例事实**（来源复盘 F-007、F-009、F-025、F-038）：

- 2026-07-23 发布 v0.1.0（F-038），发布时**未执行三线收口**：版本双声明
  （pyproject 静态 version + `xs/__init__.py` 的 `__version__`）、构建后端
  setuptools/scikit-build-core 混用、许可元数据形态不一，全部持续存在；
- 发布后漂移以零散故障形式反复出现：10-12 枢纽包 editable 导入为空（F-009）、
  10-19 单日 13 条 CI 修复（pdm venv 缺 pip、Windows 中文输出崩溃、Windows
  自覆盖死锁、ruff 未清零，F-007）、10-27 发现 Python 2 式 except 语法导致
  xs CLI 无法导入（F-025）；
- 10-23 起执行三线收口后，同类故障批量消失，10-28 文档诚实化收口顺利完成
  （F-028~F-031）。

**失败模式确认**：这正是「收口期只加功能不治理」反模式的真实代价——
版本/声明漂移没有在收口期清偿，就在发布后以「CI 时好时坏 + 用户照文档踩空」
的形式加倍偿还（0.1.0 后近 3 个月的零散救火）。该案例同时验证了本模式的
正面对照：10-23~28 按「版本定源 → 门禁固化 → 文档清理」顺序收口后，
同类问题未再复发。

## 适用边界与前提条件：反目标用户与场景

1. **无发布周期的持续开发项目**：**不适用**——无收口窗口，三线闭环套用即过度工程；
   日常治理走 [single-authority-declaration-alignment](single-authority-declaration-alignment.md)
   或 [governance-three-stage-evolution](governance-three-stage-evolution.md)。
2. **声明面已单一化的成熟项目**：**不适合**套用——版本/许可/构建下限均已单一真源且门禁齐备，
   无三线可治；套用只会重复劳动。
3. **紧急上线、无治理容量的场景**：**不推荐**采用——上线窗口以小时计，收口期治理窗口不存在；
   应先做最小发布资格检查（[release-eligibility-invariant-gate](release-eligibility-invariant-gate.md)），
   三线闭环留到发布后补。
4. **超大规模多仓协作**：**不适用**——本模式以单仓收口为建模对象；多仓场景需要跨仓版本
   对齐与协调，单仓三线不直接适用。
5. **纯内容/无构建元数据项目**：**对提升治理无效**——无版本/许可/构建下限可定源，线1 失去对象；
   应改用文档治理类模式。

## 早期预警信号（危险信号与警示信号清单）

| # | 早期预警信号 | 观察方式 |
|---|---|---|
| 1 | 版本号出现 ≥2 处手工声明 | `grep -r "__version__\|^version" pyproject.toml src/` |
| 2 | 构建后端混用（setuptools 与 scikit-build-core 并存） | 扫描各 pyproject 的 build-backend 字段 |
| 3 | 同一许可出现多形态（文本/表达式/缺失） | 元数据对比 |
| 4 | 单日 CI 修复提交 ≥5 条 | `git log --since=<date> --format="%ad"` 提交聚类 |
| 5 | 文档索引条目与目录实态不符 | 索引生成脚本与目录清单对账 |
| 6 | 规范中的「应当」无对应 CI 断言 | 规范条款 ↔ CI 配置比对 |
| 7 | linkcheck 配置 `continue-on-error: true` | CI 工作流配置检查 |

## 核心做法（三线 + 顺序约束）

```mermaid
flowchart LR
    L1["线1 版本元数据定源<br/>单一事实来源"] --> L2["线2 约定门禁化<br/>机器可验证"]
    L2 --> L3["线3 文档诚实化<br/>删除失效陈述"]
    style L1 fill:#e3f2fd,stroke:#1976d2
    style L2 fill:#e8f5e9,stroke:#388e3c
    style L3 fill:#fff3e0,stroke:#f57c00
```

**线1：版本与构建元数据定源（先做）**

- 消除多声明点：版本号、许可、构建下限各指定唯一事实来源；
- 首选机器可读的构建产物（pyproject / 标签 / CI 配置）为真源；
- 案例动作：setuptools-scm 动态推导版本、移除 `__version__`、PEP 639 许可表达式、
  scikit-build-core 全仓统一 `>=0.11`。

**线2：约定门禁化（次做）**

- 把关键「应当」转化为 CI 可执行断言，失败即阻断；
- 门禁落地后立即处理被曝光的存量漂移（门禁是漂移的探照灯）；
- 案例动作：`check_pyproject_style.py` 下限契约、声明—实现一致性门禁 P0-4→六类断言、
  依赖方向门禁。

**线3：文档诚实化（最后做）**

- 仅在线1、线2落定后删除失效陈述、消除失真、统一链接约定；
- 删除动作以「版本可信 + 门禁可验」为背书，删除依据可追溯；
- 案例动作：删除失效依赖报告、消除输出示例与目录树失真、统一 `.md` 相对链接约定、
  清理已闭环的过程性分析文档。

**顺序为什么不可颠倒**：没有线1，线2 的断言没有可比对的真源（比「谁」和「谁」一致？）；
没有线2，线3 的删除没有机器证据（凭什么说这条陈述失效？）。三条线互为前提，
收口期的工作顺序从「凭感觉」变为「可判定」。

## 反模式（看起来对，但会失败）

- ❌ **「收口期只加新功能，治理债留到发布后」**——漂移以「用户照文档踩空」「CI 时好时坏」的形式在发布后爆发，偿还成本高于收口期清偿成本。
- ❌ **「先改文档后改实现」**——文档清理没有版本/门禁背书，删哪条留哪条全凭人工判断，删错即制造新失真。
- ❌ **「门禁与文档不同步更新」**——门禁判定口径与文档描述脱节，文档说 A、门禁判 B，读者与 CI 各执一词。
- ❌ **「三条线并行推进」**——并行时线3 的删除动作发生在线1/线2 落定前，退化为「凭感觉删」，与不治理同效。
- ❌ **「收口期结束就停止治理」**——门禁没有后续维护（真源迁移、断言口径更新），退化为长期假绿。

## 检验标准

| # | 成功信号 | 判定方式 |
|---|---|---|
| 1 | **版本/许可/构建下限各有唯一真源** | pyproject/标签/CI 配置可指认，仓库内可查 |
| 2 | **关键约定均有 CI 断言** | 故意改一处副本 → 检查失败（拦截而非放行） |
| 3 | **文档失效陈述删除均有机器背书** | 每条删除动作可追溯到「版本定源 + 门禁验证」证据 |
| 4 | **三线顺序可判定** | 复盘时间线显示 线3 的删除动作晚于线1/线2 落定 |
| 5 | **跨项目可迁移（形式不变）** | 把「定源→门禁→清理」三段式套到不同项目/不同收口类型上，判定形式不变 |

## 迁移示例

- **软件版本发布**：版本号定源（标签/setuptools-scm）→ 版本坐标对账门禁 → 删除 CHANGELOG 失效条目与 README 过时示例。
- **内容站点上线**：内容 ID/发布时间定源 → 站点一致性校验（链接/索引）→ 删除失效文章与过时导航。
- **合同/标书交付**：条款版本定源 → 条款-附件交叉引用校验 → 删除失效附件与过期承诺。
- **赛事提审**：申报材料版本定源 → 材料完整性校验 → 删除与当前版本不符的旧材料。

## 案例证据（xuanspace）

来源复盘：[2026-10-29-xuanspace-october-governance-retro.md](../../../reports/2026-10-29-xuanspace-october-governance-retro.md)（F-012~F-031）。

| 线 | 动作 | 事实 |
|---|---|---|
| 线1 | 许可统一 Apache-2.0 + PEP 639 表达式；构建下限 `>=0.11`；版本 setuptools-scm 动态推导、移除 `__version__` | F-012~F-014、F-018~F-019 |
| 线2 | `check_pyproject_style.py` 下限契约；声明—实现一致性门禁 P0-4→六类断言；依赖方向门禁 | F-016、F-022~F-023、F-027 |
| 线3 | 删除失效依赖报告；消除输出示例与目录树失真；统一 `.md` 链接约定；清理已闭环分析文档 | F-028~F-031 |

**顺序验证**：时间线显示 线3 的集中收口（10-28）严格晚于线1（10-23~27）与线2（10-24~28）落定，
顺序约束在本案例中成立。文档治理提交占比（26/73）最高，证实「文档清理是收口的结果」。

**已闭合（2026-10-29，附保留条件）**：README 项目索引（13 行声明）与目录实态的对账
在 xuanspace 已机器化（F-033~F-034 对应的行动项 A-04）：`check_declaration_consistency.py`
新增子模块指针对账 G1-G3（状态可解析 / 指针 = 快照 / 文档版本引用对账），提交 `2714647`；
门禁首次运行即检出 `vendor/tvm-ffi` 指针漂移（快照 `e9fdc58` vs 索引 `6628c46`），
按 CONTRIBUTING §3.6 推进指针至 `e9fdc58`（提交 `991f635`）。

保留条件：该门禁的**生成模式**仍缺写盘不变量——先验证后落盘、基线不得缩表、
状态四档（含假性对齐）、变更可追溯四条尚未补齐，
见 [gate-baseline-write-invariants](gate-baseline-write-invariants.md) 与
[A-04 知识沉淀](../../../reports/2026-10-29-submodule-pointer-gate-sedimentation.md)。
即：线2 的「约定门禁化」在**判定侧**已闭合，在**基线写入侧**仍是本模式的演进输入。

## 失效条件与演进

- **无收口窗口时不必套用**：持续开发期的治理按单模式执行，三线收口是时间窗驱动的方法；
- **真源迁移即三线重演**：构建清单格式换代或版本方案变更时，三条线需要按顺序重演，
  不能只重做线1；
- **门禁长期假绿会破坏背书**：线3 依赖线2 的可信，门禁退化为假绿后，
  「删除有机器背书」的前提失效；
- **成熟度演进**：出现第二个非同谱系案例（如内容站点、合同交付）后可升 L2；
  若与 single-authority-declaration-alignment 或 release-eligibility-invariant-gate
  的边界收敛，届时重新评估。

## 参考实现与关联

- **来源复盘**：xuanspace 十月治理收口里程碑复盘（2026-10-29），
  洞察 1（三线协同顺序不可颠倒）+ 洞察 2（门禁是规范唯一强制执行路径）；
- **定源近邻**：[single-authority-declaration-alignment](single-authority-declaration-alignment.md)
  ——本模式线1 与线2 的方法论基础（定源 → 投影 → 校验 → 登记）；
- **发布资格近邻**：[release-eligibility-invariant-gate](release-eligibility-invariant-gate.md)
  ——发布资格不变量与版本坐标对账，是线2 在发布路径上的特化；
- **事后同步近邻**：[version-ripple-grep-sweep](version-ripple-grep-sweep.md)
  ——单点更新后的多点同步，是收口后日常维护的对应物；
- **阶段演进近邻**：[governance-three-stage-evolution](governance-three-stage-evolution.md)
  ——修复→预防→闭环的阶段演进；本模式是其在「收口期时间窗」上的组织化应用。
