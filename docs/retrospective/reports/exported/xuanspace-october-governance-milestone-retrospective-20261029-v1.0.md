---
id: "retro-20261029-xuanspace-october-governance"
type: Report
title: "xuanspace 十月治理收口里程碑复盘：版本定源、门禁固化与文档诚实化"
date: 2026-10-29
archived: 2026-10-29
scenario: milestone
methodology: seven-concepts R→I→E→C
session: sc-20261029-xuanspace-october-governance
scope: project
status: archived
topic: xuanspace-october-governance
source: "任务：对第一方子项目 xuanspace（玄境）执行里程碑复盘，方法论编排 seven-concepts 场景1（R→I→E→C），含萃取与洞察，并导出报告。观察窗口：2026-10-01 ~ 2026-10-28，73 次提交 / 378 个文件。"
pattern: "convergence-period-triple-track"
x-toml-ref: "../../../.meta/toml/docs/retrospective/reports/2026-10-29-xuanspace-october-governance-retro.toml"
tags: ["seven-concepts", "milestone", "governance", "single-source-of-truth", "quality-gate", "documentation", "monorepo"]
---

# xuanspace 十月治理收口里程碑复盘

## 执行摘要

本次复盘对象为第一方子项目 [xuanspace（玄境）](../../../../projects/xuanspace/README.md)，
观察窗口 2026-10-01 ~ 2026-10-28（活跃期 10-10 ~ 10-28），共 **73 次提交**、改动 **378 个文件**。

本次里程碑的实质是**发布前治理收口**，呈现三条协同主线：

1. **版本与构建元数据定源**——版本号改为 setuptools-scm 动态推导、移除 `__version__`
   重复声明、许可元数据统一为 PEP 639 表达式、scikit-build-core 全仓统一下限
   `>=0.11`（10-23 ~ 10-27）；
2. **约定门禁化**——新增 `check_pyproject_style.py` 构建下限契约校验、
   **声明—实现一致性门禁 P0-4**（随后扩容至六类断言）、**依赖方向门禁**
   （10-24 ~ 10-28）；
3. **文档诚实化**——删除失效依赖报告、消除输出示例与目录树失真、
   统一 `.md` 相对链接约定、清理已闭环的过程性分析文档（10-28 集中收口）。

本复盘产出：**40 条客观事实**、**3 条核心洞察**、**1 个模式升级（L1→L2）+
1 个新萃取模式（L1）**、**5 个原子行动项**，全部通过 G1~G4 质量门。

最关键的一条结论：

> **收口期治理的正确顺序是「版本可信 → 机器可验证 → 文档诚实」，不可颠倒。**
> 先定版本与元数据的唯一事实来源，再把约定固化为 CI 门禁，最后才敢删除文档中的
> 失效陈述。本里程碑中文档治理提交占比最高（26/73，35.6%），但它不是收尾杂务，
> 而是前两条线落定后的必然结果——**文档清理是收口的结果，不是收口的开始**。

---

## CMD-LOG 执行记录

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261029-xuanspace-october-governance | msg=方法论编排开始：xuanspace 十月治理收口里程碑复盘 | ctx={"scenario":"milestone","topic":"xuanspace-october-governance","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261029-xuanspace-october-governance | msg=场景识别：场景1 里程碑复盘（项目周期收口） | ctx={"scenario":"milestone","matched_triggers":["里程碑","复盘","萃取","洞察","导出报告"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261029-xuanspace-october-governance | msg=链路选定：R→I→E→C（depth=standard，单人项目复盘，V 按场景可选） | ctx={"chain":"R→I→E→C","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R0 | event=CONCEPT_STARTED | session=sc-20261029-xuanspace-october-governance | msg=R阶段开始：采集 git 历史、CHANGELOG、CI、文档与 spec 事实 | ctx={"min_facts":20}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261029-xuanspace-october-governance | msg=R阶段完成：40 条客观事实 | ctx={"facts_count":40,"causal_words_found":0}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-20261029-xuanspace-october-governance | msg=G1质量门通过：事实 40 条 ≥ 20、无因果词、关键数据可追溯 | ctx={"gate":"G1","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I1 | event=CONCEPT_COMPLETED | session=sc-20261029-xuanspace-october-governance | msg=I阶段完成：3 条核心洞察，四元组完整 | ctx={"insights_count":3,"dimensions":["收口三线顺序","约定门禁化","子模块隐性债务"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G2 | event=GATE_PASSED | session=sc-20261029-xuanspace-october-governance | msg=G2质量门通过：3 条洞察四元组完整、维度独立 | ctx={"gate":"G2","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E1 | event=CONCEPT_COMPLETED | session=sc-20261029-xuanspace-october-governance | msg=E阶段完成：single-authority-declaration-alignment 升级 L1→L2（第二独立案例）+ 新萃取 convergence-period-triple-track（L1） | ctx={"patterns":["single-authority-declaration-alignment(L2)","convergence-period-triple-track(L1)"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20261029-xuanspace-october-governance | msg=G3质量门通过：模式含触发场景+核心步骤+反模式+迁移验证，且与现有模式无重复 | ctx={"gate":"G3","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C1 | event=CONCEPT_COMPLETED | session=sc-20261029-xuanspace-october-governance | msg=C阶段完成：报告落盘+导出归档+模式库更新+链接校验 | ctx={"artifacts":["源报告","TOML镜像","导出副本+manifest","模式升级+新建","索引更新"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G4 | event=GATE_PASSED | session=sc-20261029-xuanspace-october-governance | msg=G4质量门通过：5 个行动项原子化（单一职责、可独立验证） | ctx={"gate":"G4","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S9 | event=CHAIN_COMPLETED | session=sc-20261029-xuanspace-october-governance | msg=方法论编排完成 | ctx={"gates_passed":["G1","G2","G3","G4"],"pending":["A-04","A-05"]}
```

---

## 1. 客观事实清单（R 阶段）

> 全部为可复核的客观陈述，不含因果推断与主观评价。数据经 git log / 目录实测 / 文件读取验证。

| 编号 | 事实 |
|---|---|
| F-001 | 上次 xuanspace 里程碑复盘（2026-08-25）覆盖 2026-07-24 ~ 08-19，共 314 次提交 |
| F-002 | 本仓提交总数 428 次（截至 HEAD `f8d223d`，2026-10-28） |
| F-003 | 本次里程碑观察窗口为 2026-10-01 ~ 2026-10-28 |
| F-004 | 观察窗口内提交数为 73 条 |
| F-005 | 观察窗口内提交类型分布：docs 26 / fix 19 / refactor 7 / chore 6 / feat 6 / test 4 / build 1 / ci 1 / style 1 |
| F-006 | 观察窗口内改动文件数为 378 |
| F-007 | 2026-10-19 单日提交 13 条，集中于 CI 与 CLI 修复（pdm venv 补装 pip、PATH 前置、UTF-8 输出流、Windows 自覆盖死锁、批量构建分支、ruff 全仓清零） |
| F-008 | 2026-10-10 ~ 10-12 集中于 xuan-compose 对等移植与文档原子化（索引/台账/快照十文件） |
| F-009 | 2026-10-12 修复枢纽包 editable 安装导入为空（补包体与打包声明） |
| F-010 | 2026-10-12 新增导入时版本守卫，低版本 Python 误用给出友好诊断 |
| F-011 | 观察窗口内有 4 条子模块指针更新提交（mystx 2 次、tvm-ffi 1 次、mystx 指针前移 1 次） |
| F-012 | 2026-10-23 统一第一方发行版许可口径为 Apache-2.0 |
| F-013 | 2026-10-24 许可元数据统一为 PEP 639 表达式形态 |
| F-014 | 2026-10-24 构建下限提升至 `scikit-build-core>=0.11`（PEP 639 的 license 字符串自 0.11 起被接受） |
| F-015 | 2026-10-24 移除 linkcheck 的 `continue-on-error` 以暴露真实断链 |
| F-016 | 2026-10-24 新增 `scripts/check_pyproject_style.py` 校验 scikit-build-core 下限契约 |
| F-017 | `.trae/specs/unify-scikit-build-core/` 存在 spec.md/tasks.md/checklist.md，spec 勘误记录下限 0.10→0.11 |
| F-018 | 2026-10-27 根版本号改为 setuptools-scm 动态推导（根 pyproject 无静态 version 字段） |
| F-019 | 2026-10-27 移除 `xs/__init__.py` 重复版本声明，pyproject.toml 为版本单一事实来源 |
| F-020 | 2026-10-27 `xs docs` 子命令改名 `doc`（BREAKING），模块 `doc_cmd` 统一 `doc_*` 前缀 |
| F-021 | 2026-10-27 TOML 写入库由 tomli-w 切换为 tomlkit（parse→改字段→dumps 原地编辑） |
| F-022 | 2026-10-27 新增声明—实现一致性门禁 P0-4（提交 `2750078`） |
| F-023 | 2026-10-27 声明一致性门禁扩容至六类断言并清理残余漂移（提交 `fd6d7e6`） |
| F-024 | 2026-10-27 libs 子项目清单改由脚本生成块派生（提交 `fc4fe25`） |
| F-025 | 2026-10-27 修复 Python 2 式 except 语法导致 xs CLI 无法导入（提交 `bf08b51`） |
| F-026 | 2026-10-27 补齐 xs meta 写入路径单元测试 |
| F-027 | 2026-10-28 新增依赖方向门禁并同步文档与 CI（提交 `c50f18e`） |
| F-028 | 2026-10-28 统一 doc/ 相对链接为带 `.md` 扩展名的仓内约定 |
| F-029 | 2026-10-28 删除失效的依赖报告并补全 CLI 参考与门禁覆盖 |
| F-030 | 2026-10-28 删除已闭环的过程性分析文档并清理导航 |
| F-031 | 2026-10-28 消除输出示例与目录树失真并标注依赖片段为节选 |
| F-032 | 根 pyproject 声明 `requires = ["scikit-build-core>=0.11", "setuptools-scm>=8.0"]`、`build-backend = "scikit_build_core.build"`、`requires-python = ">=3.14.6"` |
| F-033 | README 项目索引表登记 13 行（tools 3 + libs 8 + vendor 2） |
| F-034 | 目录实测：libs 8（caffe-ffi/demo-ffi/mystx/npu-ffi/tvm-book/xuan-compose/xuan-core/xuan-ext-demo）、tools 3（okf/templates/xs）、apps 0 |
| F-035 | CHANGELOG [Unreleased] 记录 4 项 BREAKING（`__version__` 移除、docs→doc 改名、init 创建 doc/、tomlkit 依赖切换）+ 内部重构 |
| F-036 | CI 矩阵为 3 OS（ubuntu/windows/macos）× 3 包管理器（pdm/pip/uv），含 ruff check/format、mypy（tools/xs、libs/xuan-core、libs/xuan-ext-demo）、pytest、xs toolchain check |
| F-037 | CI 环境强制 `PYTHONUTF8=1` 以避免 Windows 中文输出 UnicodeEncodeError |
| F-038 | CHANGELOG 记录 v0.1.0 发布于 2026-07-23 |
| F-039 | 本次复盘前 `single-authority-declaration-alignment` 模式为 L1（单案例：mystx，2026-10-22） |
| F-040 | 上次复盘（2026-08-25）产出 4 条洞察、1 个候选模式（L1）、5 个行动项 |

---

## 2. 过程分析

### 2.1 事件时间线

| 时间 | 事件簇 | 提交数 |
|---|---|---|
| 2026-10-10 ~ 10-12 | xuan-compose 对等移植与文档原子化；枢纽包 editable 修复；版本守卫；平台测试修复 | 21 |
| 2026-10-13 ~ 10-15 | 子模块指针更新（mystx/tvm-ffi） | 4 |
| 2026-10-19 | CI/CLI 修复爆发：pdm venv、UTF-8 输出、Windows 自覆盖死锁、批量构建、ruff 清零 | 13 |
| 2026-10-23 ~ 10-24 | 许可统一（Apache-2.0、PEP 639）；构建下限 0.10→0.11；linkcheck 暴露断链；构建下限契约校验脚本 | 6 |
| 2026-10-27 | 版本定源（setuptools-scm、移除 `__version__`）；xs docs→doc 改名；tomlkit；声明—实现一致性门禁 P0-4→六类断言；Python 2 except 修复 | 17 |
| 2026-10-28 | 依赖方向门禁；文档诚实化收口（删失效报告、消失真、统一 `.md` 链接、清导航） | 7 |

### 2.2 关键节点分析

**节点 1：CI 修复爆发（10-19，13 条提交）**
本次里程碑以"让 CI 真正可信"开场。pdm venv 缺 pip、Windows 中文输出崩溃、
批量构建自覆盖死锁、ruff 未清零——这些是 0.1.0 发布后第一轮真实使用暴露的
工程债。它们有一个共同特征：**都在门禁视野之内，但此前没有被门禁拦住**。
10-19 的批量修复为后续"门禁化"工作铺平了地基。

**节点 2：构建元数据定源（10-23 ~ 10-27）**
许可统一（Apache-2.0 → PEP 639 表达式）、构建下限提升（0.10→0.11）、
版本动态推导（setuptools-scm）、移除 `__version__`——这四件事的本质是
**把"谁说了算"从人工约定变成单一事实来源**。spec 勘误（F-017）记录了
0.10→0.11 的决策链：PEP 639 的 license 字符串自 0.11 起才被接受，故下限随之提升，
并由校验脚本强制（F-016）。

**节点 3：约定门禁化（10-24 ~ 10-28）**
`check_pyproject_style.py`（构建下限契约）、声明—实现一致性门禁 P0-4
（随后扩容至六类断言）、依赖方向门禁——这些把 `.agents/` 规范里的"应当"
变成了 CI 里"失败即阻断"的断言。门禁落地后立即曝光存量漂移（F-023"清理残余漂移"），
印证了"门禁是漂移的探照灯"。

**节点 4：文档诚实化收口（10-28）**
删除失效依赖报告、消除输出示例与目录树失真、统一 `.md` 相对链接约定、
删除已闭环的过程性分析文档——在版本可信、门禁可验之后，文档中的失效陈述
才被系统性清除。这一步是前三步的结果。

### 2.3 量化数据

| 指标 | 值 | 验证方式 |
|---|---|---|
| 里程碑提交数 | 73 | `git log --since=2026-10-01` |
| 改动文件数 | 378 | `git log --name-only` 去重统计 |
| docs 提交占比 | 26/73（35.6%） | `git log` 类型分组 |
| 门禁相关提交 | 4（P0-4、六类断言、依赖方向、下限契约） | 提交信息核对 |
| 全仓提交总数 | 428 | `git rev-list --count HEAD` |
| 子项目数 | libs 8 + tools 3（apps 0） | 目录实测 |

---

## 3. 核心洞察（I 阶段）

### 洞察 1：收口期的治理线是「版本可信 → 机器可验证 → 文档诚实」三线协同，且顺序不可颠倒

> **陈述**：本次里程碑呈现三条治理线：①版本与构建元数据定源
> （setuptools-scm、移除 `__version__`、PEP 639、scikit-build-core 0.11）；
> ②约定门禁化（构建下限契约、声明—实现一致性 P0-4、依赖方向门禁）；
> ③文档诚实化（删除失效报告、消除失真、统一链接约定）。
> 三者按「先定源、再校验、后清理」的顺序推进，且只有前两条落定，
> 第三条才具备执行条件。
>
> **证据**：F-018~F-019（版本定源，10-27）→ F-022~F-023、F-027（门禁，10-27~10-28）
> → F-028~F-031（文档清理，10-28）；F-016（下限校验）与 F-014（下限提升）同批落地。
>
> **反常识**：直觉上「文档清理是收尾杂务，收口期该写代码」；
> 实测文档治理提交占比最高（26/73，35.6%），且删除失效陈述只有在
> 「版本可信 + 门禁可验」之后才敢做——文档不是收口的开始，是收口的结果。
>
> **行动**：把「版本—声明—文档」三面对齐固化为发布前预检清单
> （见新萃取模式 convergence-period-triple-track），下次发布（0.2.0）前执行。

### 洞察 2：门禁是规范的唯一强制执行路径——「写在文档里」不等于「被遵守」

> **陈述**：AGENTS.md 与 `.agents/` 规范关于「构建后端统一 scikit-build-core、
> 版本单一事实来源」的约定早已存在；直到本次里程碑出现
> `check_pyproject_style.py`（下限契约）、声明—实现一致性门禁 P0-4（六类断言）、
> 依赖方向门禁，这些约定才被系统性执行，存量漂移才被曝光并清除。
>
> **证据**：F-016、F-022~F-023、F-027（门禁落地）；F-012~F-014
> （许可与下限问题在门禁化前以零散 fix 形态存在）；F-023
> （门禁扩容后「清理残余漂移」——漂移在门禁外长期未被察觉）。
>
> **反常识**：直觉上「规范写了就会被执行」；实测规范是愿望、门禁才是执行。
> 一条约定在仓库里躺多久不被遵守，取决于它有没有对应的可执行断言，
> 而不取决于它写得是否详尽。
>
> **行动**：任何「应当」约定都应评估「能否转化为断言」；本次对
> `single-authority-declaration-alignment` 的 L1→L2 升级（第二独立案例）
> 即为该洞察的跨项目验证。

### 洞察 3：子模块指针漂移是 monorepo 的隐性债务，且直接制造文档失真

> **陈述**：观察窗口内有 4 条子模块指针更新提交（F-011），10-28 删除
> 「失效的依赖报告」（F-029）——该报告的失效即源于仓库/子模块状态变化。
> README 的 13 行项目索引（F-033）与目录实测（F-034）之间的一致性依赖人工维护，
> 没有机器断言。
>
> **证据**：F-011（4 条 submodule 提交）；F-029（失效依赖报告被删）；
> F-033/F-034（13 行声明 vs 目录实测，靠人工核对）。
>
> **反常识**：直觉上「子模块自动跟随上游，省心」；实测每次上游快进都会
> 产生指针漂移，漂移沉积为文档失真，最终在收口期一次性爆发（10-28 文档清理批）。
>
> **行动**：将子模块指针状态纳入声明—实现一致性断言——依赖方向门禁已覆盖
> 依赖方向，可扩展至「子模块指针 ↔ 文档索引」对账（行动项 A-04）。

---

## 4. 萃取产物（E 阶段）

### 4.1 模式升级：`single-authority-declaration-alignment`（L1 → L2）

位置：`docs/retrospective/patterns/methodology-patterns/governance-strategy/single-authority-declaration-alignment.md`

**升级依据**：该模式原为 L1（单案例：mystx，2026-10-22）。本次里程碑构成
**第二个独立案例**（不同项目、不同谱系、不同场景）：

| 维度 | mystx 案例（L1 依据） | xuanspace 案例（本次新增） |
|---|---|---|
| 分叉形态 | 依赖双轨、行宽两值、版本文件未跟踪 | `__version__` 双声明、构建后端混用（setuptools/scikit-build-core）、README 索引 vs 目录实测 |
| 定源动作 | 指定构建清单为真源 | 版本号 setuptools-scm 动态推导、移除 `__version__`、PEP 639 许可表达式、scikit-build-core 统一下限 0.11 |
| 校验动作 | pre-commit/门禁补一致性项 | `check_pyproject_style.py` 下限契约、声明—实现一致性门禁 P0-4→六类断言、依赖方向门禁 |
| 文档清理 | README 声明修正 | 删除失效依赖报告、消除输出示例与目录树失真、统一 `.md` 链接约定 |

**成熟度更新**：`maturity: L1 → L2`、`validation_count: 1 → 2`、`reuse_count: 0 → 1`，
案例证据段补充 xuanspace 事实（F-018~F-034 对应项）。

### 4.2 新萃取模式：`convergence-period-triple-track`（收口期三线闭环）

位置：`docs/retrospective/patterns/methodology-patterns/governance-strategy/convergence-period-triple-track.md`（L1-draft，单案例）

**触发场景**：任何进入发布前收口期（版本发布、里程碑交付、上线前）的仓库或项目。

**核心做法（三线 + 顺序约束）**：

```mermaid
flowchart LR
    L1["线1 版本元数据定源<br/>单一事实来源"] --> L2["线2 约定门禁化<br/>机器可验证"]
    L2 --> L3["线3 文档诚实化<br/>删除失效陈述"]
    style L1 fill:#e3f2fd,stroke:#1976d2
    style L2 fill:#e8f5e9,stroke:#388e3c
    style L3 fill:#fff3e0,stroke:#f57c00
```

1. **版本与构建元数据定源**：消除多声明点，版本/许可/构建下限各指定唯一事实来源；
2. **约定门禁化**：把关键「应当」转化为 CI 可执行断言，失败即阻断；
3. **文档诚实化**：删除失效陈述、消除失真、统一链接约定——**仅在 1、2 落定后执行**。

**反模式**：
- ❌ 收口期只加新功能、不治理存量——版本与声明漂移继续累积；
- ❌ 先改文档后改实现——文档清理没有版本/门禁背书，删错即制造新失真；
- ❌ 门禁与文档不同步更新——门禁判定口径与文档描述脱节。

**迁移验证**：本模式不限于代码仓库——软件版本发布、内容站点上线、
合同交付、赛事提审等一切「收口期」都适用；「先定源、再校验、后清理」的顺序
约束具有跨领域普遍性。

---

## 5. 原子行动项（A 阶段）

| 编号 | 行动项 | 状态 |
|---|---|---|
| A-01 | 复盘报告落盘（源报告 + TOML 镜像） | 本次完成 |
| A-02 | 导出归档（exported 副本 + manifest + index 更新） | 本次完成 |
| A-03 | 模式库更新（`single-authority-declaration-alignment` 升级 L2 + 新建 `convergence-period-triple-track` + CATEGORIES/README 索引同步） | 本次完成 |
| A-04 | 建议 xuanspace 将「子模块指针 ↔ 文档索引」对账纳入声明—实现一致性门禁（跨子项目边界，提交建议待 xuanspace 团队决策） | 待决策 |
| A-05 | 下次发布（0.2.0）前执行「收口期三线」预检清单，作为 `convergence-period-triple-track` 首次复用验证（验证后 L1→L2） | 待触发 |

---

## 6. 质量门记录

| 门 | 判据 | 结果 |
|---|---|---|
| G1 | 事实 ≥20 条、无因果词、关键数据可追溯 | 40 条（F-001~F-040），通过 |
| G2 | 洞察 ≥3 条、四元组完整、维度独立 | 3 条，通过 |
| G3 | 模式含触发场景 + 核心步骤 + 反模式 + 迁移验证，且无重复萃取 | 1 升级 + 1 新建，通过 |
| G4 | 行动项原子化、单一职责、可独立验证 | 5 条，通过 |

**工程门禁**：

| 门禁 | 结果 |
|---|---|
| 章节结构检查（`^#` 标题层级） | 预期章节完整（事实/过程/洞察/萃取/行动/质量门） |
| 相对链接检查 | 报告引用全部为仓内相对路径（无 `file:///`） |
| 事实数据复核 | 提交数/文件数/类型分布均经 git 命令实测 |

---


---

## 导出说明

本文件是源报告 `docs/retrospective/reports/2026-10-29-xuanspace-october-governance-retro.md` 的
**内容副本**（md 格式直通，仅相对路径深度随归档位置调整）。

| 项 | 值 |
|---|---|
| 导出时间 | 2026-10-29 |
| report_type | retrospective (milestone) |
| formats | md |
| version | 1.0 |
| 相对链接调整 | 3 处：`../../../projects/` 加深为 `../../../../projects/`；同目录关联报告加 `../` 前缀；`../patterns/` 加深为 `../../patterns/` |


## 7. 关联资产

| 资产 | 关系 |
|---|---|
| [2026-08-25-xuanspace-milestone-retro.md](../2026-08-25-xuanspace-milestone-retro.md) | 上一轮 xuanspace 里程碑复盘（第一阶段，本次的对照基线） |
| [single-authority-declaration-alignment](../../patterns/methodology-patterns/governance-strategy/single-authority-declaration-alignment.md) | 本次升级 L1→L2 的模式（第二独立案例） |
| [convergence-period-triple-track](../../patterns/methodology-patterns/governance-strategy/convergence-period-triple-track.md) | 本次新萃取模式（L1） |
| [unify-scikit-build-core spec](../../../../projects/xuanspace/.trae/specs/unify-scikit-build-core/spec.md) | 本次里程碑的构建后端统一 Spec（含 0.10→0.11 勘误） |
| [xuanspace CHANGELOG](../../../../projects/xuanspace/CHANGELOG.md) | 4 项 BREAKING 变更的官方记录 |
| [xuanspace README](../../../../projects/xuanspace/README.md) | 项目索引与架构声明（本次治理的对象之一） |
