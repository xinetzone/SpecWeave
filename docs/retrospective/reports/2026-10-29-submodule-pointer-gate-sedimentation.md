---
id: "sediment-20261029-submodule-pointer-gate"
type: Report
title: "A-04 子模块指针对账门禁知识沉淀：生成器为何是门禁最薄弱的一环"
date: 2026-10-29
archived: 2026-10-29
scenario: knowledge
methodology: seven-concepts R→I→E→V
session: sc-20261029-submodule-pointer-gate
scope: module
status: archived
topic: submodule-pointer-gate
source: "任务：对 A-04 子模块指针对账门禁（xuanspace `submodule-alignment-gate`）执行知识沉淀，方法论编排 seven-concepts 场景4（R→I→E→V），深度 deep，V 阶段由独立审查者执行。"
pattern: "gate-baseline-write-invariants"
x-toml-ref: "../../../.meta/toml/docs/retrospective/reports/2026-10-29-submodule-pointer-gate-sedimentation.toml"
tags: ["seven-concepts", "knowledge", "quality-gate", "baseline", "drift", "submodule", "adversarial-review"]
---

# A-04 子模块指针对账门禁知识沉淀

## 执行摘要

沉淀对象是 [xuanspace 十月治理收口复盘](2026-10-29-xuanspace-october-governance-retro.md)
的行动项 A-04——把子模块指针状态纳入「声明—实现一致性」门禁
（[spec](../../../projects/xuanspace/.trae/specs/submodule-alignment-gate/spec.md) /
[tasks](../../../projects/xuanspace/.trae/specs/submodule-alignment-gate/tasks.md) /
[review](../../../projects/xuanspace/.trae/specs/submodule-alignment-gate/review.md)）。

本次产出 **32 条客观事实**、**3 条核心洞察**、**1 个新模式（L1-draft）**、
**7 条对抗审查意见（采纳 4、降级 2、部分采纳 1）**、**5 个原子行动项**。

最关键的结论：

> **门禁的强度上限由它的生成器决定，而不是由断言数量决定。**
> 任何带 `--generate` / `--fix` / `--update-snapshot` 能力的门禁，
> 只要允许从「当前状态」重新生成基线，所有断言都可以被一次性绕过——
> 基线刷新是唯一的「洗白」通道。A-04 拒绝在漂移态下刷快照是对的，
> 但它在**写盘时机、键集合收缩、状态分档**三处仍留有同类缺口，
> 本次由独立对抗审查逐条定位（F-27~F-32）。

---

## CMD-LOG 执行记录

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261029-submodule-pointer-gate | msg=方法论编排开始：A-04 子模块指针对账门禁知识沉淀 | ctx={"scenario":"knowledge","topic":"submodule-pointer-gate","depth":"deep"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261029-submodule-pointer-gate | msg=场景识别：场景4 知识沉淀（案例→共性→模式→入库） | ctx={"scenario":"knowledge","matched_triggers":["知识沉淀","模式","deep"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261029-submodule-pointer-gate | msg=链路选定：R→I→E→V→入库 | ctx={"chain":"R→I→E→V","depth":"deep","with_validation":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261029-submodule-pointer-gate | msg=R阶段完成：32 条客观事实 | ctx={"facts_count":32,"causal_words_found":0}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-20261029-submodule-pointer-gate | msg=G1质量门通过：32 ≥ 20、无因果词、逐条可溯源 | ctx={"gate":"G1","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I1 | event=CONCEPT_COMPLETED | session=sc-20261029-submodule-pointer-gate | msg=I阶段完成：3 条洞察，四元组完整 | ctx={"insights_count":3}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G2 | event=GATE_PASSED | session=sc-20261029-submodule-pointer-gate | msg=G2质量门通过：3 条洞察四元组完整、维度独立 | ctx={"gate":"G2","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E1 | event=CONCEPT_COMPLETED | session=sc-20261029-submodule-pointer-gate | msg=E阶段完成：新萃取 gate-baseline-write-invariants（L1-draft，validation_count=1） | ctx={"patterns":["gate-baseline-write-invariants(L1-draft)"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V1 | event=CONCEPT_COMPLETED | session=sc-20261029-submodule-pointer-gate | msg=V阶段完成：独立对抗审查 7 条攻击（4 采纳 / 2 降级 / 1 部分采纳） | ctx={"attacks":7,"adopted":4,"downgraded":2}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20261029-submodule-pointer-gate | msg=G3质量门通过：模式含触发场景+核心步骤+反模式+迁移验证，已声明与近邻边界 | ctx={"gate":"G3","result":"pass"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S9 | event=CHAIN_COMPLETED | session=sc-20261029-submodule-pointer-gate | msg=知识沉淀完成，行动项 A-04-1~A-04-5 待 xuanspace 侧执行 | ctx={"pending":["A-04-1","A-04-2","A-04-3","A-04-4","A-04-5"]}
```

---

## 1. 客观事实清单（R 阶段）

> 全部为可复核的客观陈述，不含因果推断与主观评价。
> 证据来源：spec/tasks/review 三件套、门禁脚本、CI 配置、复盘报告、最近提交记录。

| 编号 | 事实 |
|---|---|
| F-01 | xuanspace 顶层子模块 4 个：`libs/mystx`、`libs/tvm-book`、`vendor/caffe`、`vendor/tvm-ffi` |
| F-02 | 2026-10-13 提交 `81c29a6` 同步 `vendor/tvm-ffi` 至 `0932956`；spec 记录该次上游 main 快进 35 提交 |
| F-03 | 2026-10-19 提交 `854d12d` 提交标题为 `modified: vendor` |
| F-04 | 2026-10-12 提交 `7415796` 更新 `libs/mystx` 指针 |
| F-05 | 既有声明—实现一致性门禁含 A–F 六类断言 |
| F-06 | A–F 中子模块相关断言（D/E/F）比对 `.gitmodules` 的路径与名称 |
| F-07 | 原 `declaration-snapshot.json` manifest 含 `cli_commands` / `lib_projects` / `submodules` 三字段 |
| F-08 | spec 新增 G1（状态可解析）/ G2（指针=快照）/ G3（文档版本引用对账）三类断言 |
| F-09 | spec 规定 `-` 前缀（未初始化）记 note 不阻断，`+` 前缀（checkout 与索引不一致）由 G2 阻断 |
| F-10 | 实施前对照 CONTRIBUTING §3.5 修正 G1 草案为「未初始化记 note 不阻断，已初始化漂移才阻断」 |
| F-11 | tasks Task 1 规定 `--generate` 遇 `+` 漂移时拒绝刷新并退出码 2 |
| F-12 | 门禁首跑捕获 `vendor/tvm-ffi` 漂移：checkout `e9fdc58` vs 索引 `6628c46` |
| F-13 | review 记录该漂移领先索引 30 提交 |
| F-14 | 漂移态执行 `--generate` 输出「拒绝刷新快照」提示且退出码 2，快照未被固化 |
| F-15 | 快照 `submodule_status` 含 4 个子模块 SHA，与 `git submodule status` 逐项一致 |
| F-16 | 校验模式退出码 0；重复 `--generate` 跳过写盘；`--json` 输出 `ok=True failures=0` |
| F-17 | `scripts/README.md` 更新为「六类 + G 类子模块指针对账」 |
| F-18 | CONTRIBUTING.md 新增 §3.6「子模块指针变更流程」三步，并写明禁止裸指针变更 |
| F-19 | review CP-U1 得分 2；锚点 2 的表述为「历史中不再出现 `modified: vendor` 类裸提交」 |
| F-20 | review CP-U2 得分 2；依据为「§3.5 当前无版本号引用（G3 无对账对象）」 |
| F-21 | 复盘 A-04 记录：确认后按 §3.6 推进指针至 `e9fdc58`（上游快进 30 提交，xuanspace `991f635`），主仓 gitlink 前移 `fce857675` |
| F-22 | 主仓同期两次前移 `projects/xuanspace` 指针：`cb9c186c2` → `2714647`、`fce857675` → `991f635` |
| F-23 | 主仓 `.gitmodules` 登记 20 个子模块 |
| F-24 | 主仓 vendor 检查 `--deep` 比对子模块 HEAD 与 `git ls-tree HEAD` 记录的 SHA（`vendor.py:861-875`） |
| F-25 | 主仓指针比对位于 `--deep` 可选分支，默认检查不含该断言（`vendor.py:812-984`） |
| F-26 | 主仓 `vendor.py` 对僵尸子模块设 index 缺失判据（`vendor.py:217-236`） |
| F-27 | `--generate` 分支仅调用 `extract_submodule_status` 判定漂移，A–F 六类断言未执行（`check_declaration_consistency.py:500-510`） |
| F-28 | `--generate` 先写快照文件，之后才校验 libs 元数据，元数据缺失时返回 2（`:511-522`） |
| F-29 | `status_map` 仅收录 `flag == " "` 的条目（`:271-272`），未初始化条目不进入快照 |
| F-30 | 校验模式对 manifest 全部键逐一比对，任一不等即 failure，未对未初始化路径做子集豁免（`:476-479`） |
| F-31 | G3 仅扫描 CONTRIBUTING §3.5 一节，并与全部子模块版本标签全集比对，未按路径绑定（`:455-467`） |
| F-32 | xuanspace CI 四个 job 均以 `submodules: recursive` 检出，并在 `ci.yml:188` 运行该门禁 |

---

## 2. 核心洞察（I 阶段）

### 洞察 1：门禁的强度上限由生成器决定，不由断言数量决定

> **陈述**：声明—实现一致性门禁已经具备六类断言，但真正决定它可信度的是
> `--generate` 这一条分支：它是唯一能把「当前状态」写成「合格基线」的通道。
> 只要生成器不设前置验证，任何断言都可以被一次刷新绕过；A-04 在这一点上
> 只做对了一半——它拒绝写漂移态，却先写盘后校验、并允许键集合收缩。
>
> **证据**：F-27（生成模式不跑 A–F）、F-28（写盘先于最后一道校验）、
> F-29（未初始化条目被排除在快照外）、F-14（漂移态拒绝写盘，正面样本）。
>
> **反常识**：直觉是「断言越多门禁越强」；实测门禁只有两种强度——
> 生成器受约束的，和生成器不受约束的。后者断言再多，也只是给守规矩的人准备的。
>
> **行动**：把「先验证后落盘」与「基线不得缩表」写成生成模式的两条硬性前置，
> 见新模式 [gate-baseline-write-invariants](../patterns/methodology-patterns/governance-strategy/gate-baseline-write-invariants.md)。

### 洞察 2：状态模型少一档，门禁会自相矛盾到被绕过

> **陈述**：spec 声明「未初始化记 note 不阻断」（F-09/F-10），
> 实现里快照等式却把「未初始化导致的事实为空」判成 failure（F-30）——
> 同一条豁免在文档里成立、在断言里被否证。状态只有「对齐/不对齐」两档时，
> 「尚未开始」只能被塞进「不对齐」，用户唯一出路是绕过门禁（跳过初始化、
> 或先 `deinit` 再生成，后者还能顺带把条目从快照里删掉）。
>
> **证据**：F-09（spec 豁免）、F-30（快照全键比对无豁免）、F-29（缩表通道存在）、
> F-26（主仓已有僵尸态判据，说明「对齐」还需存在性条件）。
>
> **反常识**：豁免通常被当作文档措辞问题；实际上豁免是**断言形状**问题——
> 只要用集合相等表达豁免，豁免就不存在。
>
> **行动**：状态改为四档（未开始 / 已对齐 / 已偏离 / 假性对齐），
> 豁免用子集断言表达，假性对齐补存在性判据（index 文件、工作区非空）。

### 洞察 3：「可审查」不等于「可判定」

> **陈述**：裸提交 `modified: vendor`（F-03）的治理手段是「门禁拦截 + 人工确认 +
> 提交说明注明范围」（F-18/F-21）。但「注明范围」落在 commit message 里，
> 没有任何断言读取它；review 给该维度的满分锚点是「历史中不再出现裸提交」（F-19），
> 而这是一个只能靠未来历史验证的命题，验收当时即给分。
> 结果上，A-04 的收口动作本身就是一次「人审确认后把漂移态正式推进为新基线」
> （F-21/F-22），人审是真实的，留痕却没有。
>
> **证据**：F-03（裸提交）、F-18（三步流程含提交说明）、F-19（未来时锚点满分）、
> F-21/F-22（人审推进 + 主仓两次人工前移）。
>
> **反常识**：以为把约定写进 CONTRIBUTING 就等于执行；实测约定要成为判据，
> 必须落在被机器读取的字段里（快照前值、变更范围、PR 模板），
> 否则它只是一句劝告。
>
> **行动**：把「范围说明」从 message 迁入结构化字段（如 `previous_sha`、
> 上游提交区间），并对「基线变更必须两文件同批」设断言。

---

## 3. 萃取产物（E 阶段）

### 3.1 新模式：`gate-baseline-write-invariants`（L1-draft）

位置：[gate-baseline-write-invariants.md](../patterns/methodology-patterns/governance-strategy/gate-baseline-write-invariants.md)

| 项 | 内容 |
|---|---|
| 一句话 | 门禁可不可信，不取决于断言多严，而取决于它能否拒绝用自己的生成器把违规态写成合格基线 |
| 四条不变量 | ① 先验证后落盘 ② 基线不得缩表 ③ 状态四档（含假性对齐） ④ 变更可追溯 |
| 成熟度 | `L1-draft`，`validation_count=1`、`reuse_count=0` |
| 验证程度 | 案例完整验证只有不变量①的一半（拒绝漂移态写盘）；②③④ 为本次 V 阶段曝光的未落地缺口 |
| 迁移验证 | lockfile 重生成、golden/snapshot 测试、覆盖率基线、SBOM、自动生成的文档索引 |

### 3.2 去重裁决（G3）

| 既有模式 | 裁定 | 依据 |
|---|---|---|
| [single-authority-declaration-alignment](../patterns/methodology-patterns/governance-strategy/single-authority-declaration-alignment.md) | 上位，不重复 | 它管「谁是权威、是否对齐」；本模式管「对齐基线自身能否被生成器改写」 |
| [snapshot-parity-migration](../patterns/methodology-patterns/governance-strategy/snapshot-parity-migration.md) | 近邻，不重复 | 它把「禁止为让测试变绿刷新快照」作为**迁移纪律**；本模式把同一原则扩展为**门禁设计不变量**（缩表禁令、写盘原子性、四态） |
| [convergence-period-triple-track](../patterns/methodology-patterns/governance-strategy/convergence-period-triple-track.md) | 近邻，不重复 | 它管收口期三线的**顺序**；本模式管线2 内部单个门禁的**设计** |
| [dual-mode-submodule-governance](../patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md) | 近邻，工作流需回改 | 其子模块更新工作流仍示范单行裸提交（`chore(vendor): update ...`），与本模式不变量④不一致，已在模式文档中登记为待对齐项 |
| [dual-env-drift-reconciliation](../patterns/methodology-patterns/governance-strategy/dual-env-drift-reconciliation.md) | 独立 | 对象是双实例资产的三态对账，不含生成器权限问题 |
| [fail-loud-over-silent-fallback](../patterns/methodology-patterns/governance-strategy/fail-loud-over-silent-fallback.md) | 互补 | 它主张显式报错；本模式补充「豁免必须是显式的、可判定的」，否则显式报错会误伤合法中间态 |

### 3.3 成熟度裁定

`L1-draft`。理由：唯一案例的四条不变量中，一条半成立、两条属未验证设计意图；
跨项目验证缺失；且该案例以「人审后推进指针」收口，使不变量①的边界（人审可作为合法旁路）
无法在本案例内被检验。**不标 L1，不宣称已验证。**

---

## 4. 对抗审查（V 阶段）

V 阶段由独立审查者执行（与实施者自验分离），对照 spec/tasks/review、门禁脚本、
CI 配置与主仓 vendor 检查逐条证伪。

| # | 攻击点 | 依据 | 严重度 | 处理 |
|---|---|---|---|---|
| V-1 | 「生成器重跑同一套断言」的口径与代码不符：生成模式只跑漂移判定 | F-27 | 高 | **采纳**：口径改为「重跑除基线相等外的断言」，并显式列豁免白名单 |
| V-2 | 可先 `deinit` 让漂移消失再生成，把条目从快照中抹掉（缩表洗白） | F-29 | 高 | **采纳**：新增不变量②「基线不得缩表」 |
| V-3 | 「未初始化不阻断」在实现中被快照等式否证 | F-09/F-30 | 高 | **采纳**：状态四档 + 子集断言 |
| V-4 | 「两文件变更 = 审计轨迹」名不副实：快照无前值与范围 | F-28/F-19 | 高 | **降级**：改为「状态可追溯」，并建议结构化字段 |
| V-5 | G3 无对账对象却给满分，且比对不绑定路径 | F-20/F-31 | 中 | **降级**：标注为未验证设计意图，不作为模式论据 |
| V-6 | CI 以 `submodules: recursive` 检出，`+` 断言在 CI 中恒真 | F-32 | 高 | **采纳**：拆「工作树漂移」与「上游已前进」为两个断言，修正 spec 场景 |
| V-7 | 缺「假性对齐」判据（HEAD==gitlink 但工作区为空） | F-26 | 中高 | **部分采纳**：并入状态第四档，判据复用主仓 index 检查思路 |

采纳后修正：模式主张由 4 条收窄为「1 主 3 辅」，成熟度由 L1 降为 L1-draft，
并把两条攻击写入模式文档的「失效条件与演进」而非成功判据。

---

## 5. 原子行动项（A 阶段）

| 编号 | 行动项 | 单一职责 | 验收标准 | 归属 |
|---|---|---|---|---|
| A-04-1 | `--generate` 在写盘前重跑除「基线相等」外的 A–F 断言，失败即整批拒绝写盘 | 写盘时机 | 构造 A–F 违例后运行 `--generate`：退出码非 0、快照 mtime 不变 | xuanspace |
| A-04-2 | 新增「快照不得缩表」断言：新键集合 ⊇ 旧键集合 | 基线单调性 | `deinit` 某子模块后运行 `--generate`：被拒且提示缺失条目 | xuanspace |
| A-04-3 | 状态四档化：未开始 / 已对齐 / 已偏离 / 假性对齐，假性对齐以 index 文件存在为判据 | 状态模型 | 构造无 index 的半检出子模块：判为假性对齐并阻断 | xuanspace |
| A-04-4 | 拆分「工作树漂移」与「上游已前进」两个断言（后者用 `fetch` + `ls-remote`） | 断言粒度 | spec 场景「上游快进未同步」可被独立复现为失败 | xuanspace |
| A-04-5 | G3 改为 `(path, version)` 元组比对；无对账对象时不给满分 | 对账精度 | 在 §3.5 写入错误子模块版本号：G3 指向具体路径报错 | xuanspace |

> 以上 5 项均在 `projects/xuanspace` 子模块内执行，须走其自身 Spec 流程，
> 不在本次沉淀范围（本次仅登记）。

---

## 6. 质量门记录

| 门 | 判据 | 结果 |
|---|---|---|
| G1 | 事实 ≥20 条、无因果词、关键数据可追溯 | 32 条（F-01~F-32），通过 |
| G2 | 洞察 ≥3 条、四元组完整、维度独立 | 3 条（生成器权限 / 状态模型 / 可判定性），通过 |
| G3 | 模式含触发场景+核心步骤+反模式+迁移验证，且已声明与近邻边界 | 1 个新模式（L1-draft），通过 |
| V 门 | 审查意见 ≥5 条且具体，至少采纳 2 条 | 7 条，采纳 4 条（另 1 条部分采纳），通过 |

**工程门禁**：章节结构完整；文中链接均为仓内相对路径；代码引用行号取自本次实读。

---

## 7. 关联资产

| 资产 | 关系 |
|---|---|
| [xuanspace 十月治理收口里程碑复盘](2026-10-29-xuanspace-october-governance-retro.md) | 本次沉淀的上游复盘（A-04 出处） |
| [submodule-alignment-gate spec](../../../projects/xuanspace/.trae/specs/submodule-alignment-gate/spec.md) | 门禁的正式提案 |
| [tasks.md](../../../projects/xuanspace/.trae/specs/submodule-alignment-gate/tasks.md) | 实施计划与完成证据 |
| [review.md](../../../projects/xuanspace/.trae/specs/submodule-alignment-gate/review.md) | 独立复核记录 |
| [check_declaration_consistency.py](../../../projects/xuanspace/scripts/check_declaration_consistency.py) | 门禁实现（F-27~F-31 的取证对象） |
| [vendor.py](../../../.agents/scripts/lib/checks/vendor.py) | 主仓对照实现（F-24~F-26） |
| [gate-baseline-write-invariants](../patterns/methodology-patterns/governance-strategy/gate-baseline-write-invariants.md) | 本次萃取的模式 |
| [single-authority-declaration-alignment](../patterns/methodology-patterns/governance-strategy/single-authority-declaration-alignment.md) | 上位模式（本模式的定源/对账基础） |
| [snapshot-parity-migration](../patterns/methodology-patterns/governance-strategy/snapshot-parity-migration.md) | 近邻模式（重生成纪律的迁移场景版） |
