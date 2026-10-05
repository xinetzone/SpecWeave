---
type: tasks
title: 三元组探究 OKF wiki 教程 — 实施队列
spec_mode: Plan
spec: ./spec.md
method: seven-concepts-cmd（场景4，链路 F→R→I→E→V→A→C，depth=deep）
session: sc-20261003-dao-san-yuan
created: 2026-10-03
status: approved
---

# 实施队列

> AC → TR 映射见`tasks.md` 与 `spec.md` §8。优先级：high > medium > low。

## Task 1: F 阶段——第一性原理，剥离四条链的隐含假设

Status: completed

- [x] **T1.1** 剥离「三 = 某个具体实体」假设（蒋锡昌/刘笑敢/池田知久反对此假设，须正面回应）
- [x] **T1.2** 剥离「六类解释互斥」假设——检验是否可被同一结构统摄
- [x] **T1.3** 剥离「时间三元组是客观的」假设（奥古斯丁三分法的投射性质）
- [x] **T1.4** 剥离「两组三元组是行动工具而非生成结构」假设——检验其与「三」生成论的同构性
- [x] **T1.5** 提炼公理列表（自洽的最小公理集，供I/E 阶段推导）

**Test Requirements**
- TR-1.1（rule）：假设清单 ≥4 条，每条含「假设原文 / 若不成立会怎样 / 检验方式 / 检验结论」
- TR-1.2（rubric）：公理自洽性——公理之间无循环依赖，且每条公理能推出至少一条 F 阶段结论

## Task 2: R 阶段——客观事实采集

Status: completed

- [x] **T2.1** 采集帛书本第四十二章原文（甲/乙本差异，逐句标注）
- [x] **T2.2** 采集「冲/中」通假争议双向记载（《长沙马王堆汉墓简帛集成》+ 严灵/高明辨析）
- [x] **T2.3** 采集「三」六类解释的学者主张与出处（冯国超、河上公、蒋锡昌、刘笑敢、池田知久、冯友兰、庞朴等）
- [x] **T2.4** 采集郭店楚简《太一生水》全文生成链
- [x] **T2.5** 采集《穀梁传》三合生物观、《楚辞·天问》「阴阳三合」
- [x] **T2.6** 采集奥古斯丁三分法（记忆/注意/期待）+ `distentio animi` + 时间三分法的反驳立场
- [x] **T2.7** 采集两组三元组定义本体（行数锚点 + 判据 + 顺序不可颠倒论证）
- [x] **T2.8** 采集 daoapps 结伴站四站时间线与引文版本纪律
- [x] **T2.9** 采集 vendor `three-as-interface.md` 的 Ψ=Ψ(Ψ) 推导与设计三定律
- [x] **T2.10** 写入 `references/source-inventory.md`（来源键 S01~Sxx + 采集时点）

**Test Requirements**
- TR-2.1（rule）：事实 ≥25 条，编号 F-001~F-0xx，无因果推断词（因为/导致/因此/所以/使得/从而）
- TR-2.2（rule）：每条事实含可溯源信息（学者/书名/篇卷/URL/采集时点）；未证实信息不写成事实
- TR-2.3（rubric）：信源分级——学术期刊/权威出版社/机构口径/自媒体分级标注，口径差异显式并列

## Task 3: I 阶段——洞察（四元组）

Status: completed

- [x] **T3.1** I-1「三」的第五义：关系位（vendor `three-as-interface` 与冯国超新解的汇流）
- [x] **T3.2** I-2 时间三元组与生成三元组的同构：「三」= 未来时的现在
- [x] **T3.3** I-3 两组行动三元组是「三」的两种投影：诊断层与能力层
- [x] **T3.4** I-4 daoapps 四站是生成论的时间化落地（现世实证）
- [x] **T3.5** 每条洞察四元组完整：陈述 / 证据（F-xxx）/ 反常识 / 行动

**Test Requirements**
- TR-3.1（rule）：洞察 ≥3 条，四元组字段无空缺，证据引用 F 编号
- TR-3.2（rule）：洞察维度互不重叠
- TR-3.3（rubric）：反常识性——至少 2 条洞察挑战了默认假设而非正确的废话

## Task 4: E 阶段——模式萃取与生存指南

Status: completed

- [x] **T4.1** 萃取可迁移模式「三之位」（L1-draft）
- [x] **T4.2** 撰写 `concepts/04-survival-guide.md`：≤1200 字、≤7 条原则、每条含判据+反例
- [x] **T4.3** 给出 5 分钟内可完成的最小动作
- [x] **T4.4** 声明适用边界与不适用场景

**Test Requirements**
- TR-4.1（rule）：模式含触发场景 + 步骤 + ≥3 反模式 + 检验标准 + 跨域迁移 + 成熟度标注
- TR-4.2（rule）：生存指南正文 ≤1200 字、原则 ≤7 条（硬约束）
- TR-4.3（rule）：每条原则含可回答的判据 + ≥1 条具体反例
- TR-4.4（rubric）：极简性——删掉任一原则后指南即不可用，无冗余条款

## Task 5: 撰写四篇概念页与两篇信源页

Status: completed

- [x] **T5.1** `concepts/01-san-yi-birth.md`：六类解释 + 五义统一模型 + 映射表
- [x] **T5.2** `concepts/02-time-triads.md`：奥古斯丁三分法 + 反驳立场 + 类比性映射
- [x] **T5.3** `concepts/03-action-triads.md`：两组三元组四元关联 + 措辞分叉登记
- [x] **T5.4** `concepts/04-survival-guide.md`
- [x] **T5.5** `references/source-inventory.md` + `references/adversarial-review.md`
- [x] **T5.6** `examples/01-worked-example.md`：daoapps 四站完整走查
- [x] **T5.7** 全部 index.md 与 toctree

**Test Requirements**
- TR-5.1（rule）：frontmatter 完整（type 非空，束根含 okf_version）
- TR-5.2（rule）：toctree 完整可达；相对路径；无 file:///
- TR-5.3（rule）：《老子》引文全部标注版本（甲本/乙本/今本/楚简本）
- TR-5.4（rubric）：四页之间有实质交叉引用，非孤立页面

## Task 6: V 阶段——4 视角对抗审查

Status: completed

- [x] **T6.1** 魔鬼代言人视角：结论可能是错的？反例？
- [x] **T6.2** 新人视角：概念无解释、前置条件缺失、无入门示例？
- [x] **T6.3** 老板视角：投入产出比、可操作性、机会成本？
- [x] **T6.4** 未来视角：一年后回看是否变成笑话？环境变化后是否成立？
- [x] **T6.5** 汇总修正，回归确认

**Test Requirements**
- TR-6.1（rule）：4 视角全覆盖、意见 ≥5 条且具体、采纳 ≥2 条、被推翻假设显式记录
- TR-6.2（rule）：不采用表演式审查（禁止「写得很好」类意见）

## Task 7: Skill 萃取与双索引登记

Status: completed

- [x] **T7.1** 创建 `.agents/skills/dao-san-triads/SKILL.md`（五要素模型，≤500 行）
- [x] **T7.2** 更新 `.agents/skills/README.md`
- [x] **T7.3** 更新 `.agents/capability-registry.md`
- [x] **T7.4** 跑 `check-skill-quality.py` 验证

**Test Requirements**
- TR-7.1（rule）：SKILL.md ≤500 行，含五要素与「必须使用此技能」强制措辞
- TR-7.2（rule）：双索引均含新 skill 登记项
- TR-7.3（rule）：SKILL.md 内路径全为相对路径

## Task 8: 验证与门禁

Status: completed

- [x] **T8.1** utf8 检查通过
- [x] **T8.2** toctree 可达性检查通过
- [x] **T8.3** 链接有效性检查通过
- [x] **T8.4** 两个子模块 `git status` 无变化（只读边界验证）
- [x] **T8.5** 写 `review.md`

**Test Requirements**
- TR-8.1（rule）：门禁脚本退出码 0
- TR-8.2（rule）：子模块 git status 无变化
- TR-8.3（rule）：review.md 记录每条 AC 的独立证据

## Review History

| 轮次 | 结果 | 说明 |
|---|---|---|
| 1 | **通过** | 45 个Task 全部 completed；18/18 rule 型 AC 通过；5/5 rubric 型 AC ≥4 分；门禁退出码 0；Skill 质量 100/100。证据见 `review.md` |