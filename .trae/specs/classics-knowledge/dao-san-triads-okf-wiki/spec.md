---
type: spec
title: 三元组探究 OKF wiki 教程（「三」的本质 + 时间三元组 + 两组行动三元组 + 极简生存指南）
spec_mode: Specify
method: seven-concepts-cmd（场景4 知识沉淀，链路 F→R→I→E→V→A→C，depth=deep）
session: sc-20261003-dao-san-yuan
content_sensitivity: Public（公版古籍 + 公开学术成果 + 自有方法论原创部分）
created: 2026-10-03
status: "implemented"
---

# 三元组探究 OKF wiki 教程 — 需求规格

## 1. 问题陈述（Problem）

四条概念链在仓库内各自存在，但从未被放在同一条论证链上被综合探究，导致三处结构性断裂：

**断裂一：「三」在bundles 侧完全空白。** `projects/awesome-okf-xs/doc/bundles/` 全仓检索显示：「道生一，一生二，二生三，三生万物」仅3 处命中，且全部是**引文嵌入而非结构阐释**——`guoxue/laoziaozi-works/concepts/core-concepts.md:28` 把整句作为「道·本体义」的定义性引文，随后立即转入「无」「有」范畴；`guoxue/daojia/xuanxue/heshanggong/concepts/04-selected-chapters.md:71-74` 是**河上公注式的史料登记**（三= 和清浊三气= 天地人），不是对「三」之数字/结构意义的本体论阐发；`zhexue/methodology/first-principles/concepts/chinese-philosophy-parallels/01-daoism-core-concepts.md:31` 用的是**王弼本「冲气以为和」**且未提及帛书本异文。第四十二章在 `laozi/laozi-works/text/boshu-jia.md`（55 行）与 `boshu-yi.md`（58 行）中**均无收录**，「中气以为和」异文在 `laozi/` 三包中**完全未登记**。

**断裂二：时间三元组无哲学根基。** 仓库内检索「过去/现在/未来」的时间三元组，未见任何与老子生成论并置的哲学论证。奥古斯丁三分法（记忆/注意/期待）作为西方时间哲学的经典表述，在仓库内无对应资产。

**断裂三：两组三元组是孤岛。** 「真问题·真需求·真目标」与「品质·技能·身份」的**定义本体唯一来源**是 `.agents/skills/role-model-methodology/SKILL.md`（v1.1.0，471 行），全仓 155 个 skill、17 个 command、11 个 role、全部 rules **均未复用**；`docs/` 下「真问题」「真需求」另有 4 处**术语重名但语义不同**的日常义项（真实故障 / 根因定位 / 产品价值 / 付费验证）。两组三元组与「三」的生成论结构、与时间三元组的关系，均未建立。

**断裂四：daoapps 结伴站未被纳入。** `projects/daoapps.github.io/doc/jieban/origin.md` 已构建一条**四站人生时间线**（修心/ 寻伴 / 成家 / 立业，对应知足/恒与/知和/愈多四频道），并明确「四个群不是四项业务，而是同一条人生时间线上的四个站」。这条时间线与本次探究的三元组在结构上高度同构，但仓库内无任何文档建立二者的关联。

**断裂五：无综合落点。** `doc/bundles/` 下检索 `wudao / daodejing / shengming / survival-guide` 全部 0 命中——**不存在任何人类生存指南类知识束**。

## 2. 用户与使用场景（Users）

* **期望极简可操作的人类生存指南者**：不读原典、不读学术，要一条能立刻执行的行动原则。指南必须能在 5 分钟内读完、今天就能用。
* **对「三」之本体意义好奇的读者**：想知道老子第四十二章的「三」到底是什么，以及为什么两千年无人定论。
* **SpecWeave 智能体与开发者**：把「三」的生成论结构用作认知工具与工程设计原则（接口优先原则）。
* **榜样学习者**：已有 `role-model-methodology` 两组三元组的使用经验，希望理解其哲学根据与统一原理，而非孤立使用两个表格。

## 3. 目标（Goals）

* **G1**：在 `docs/knowledge/dao-san-triads/` 下建立 OKF v0.2 知识包，以**问题域**而非学科分类组织，覆盖四条概念链的完整探究过程与中间推理记录。
* **G2**：「三」的本体论探究须**穷尽主流解释谱系**并给出可裁决的判据，包含冯国超新解（`一` +天地= 三）、传统气化论（三 = 阴/阳/和气）、天地人三才说、二与一为三说（`庄子·齐物论` 路径）、模式说/虚指说（蒋锡昌、刘笑敢、池田知久）、三合生物观（`穀梁传`、`天问`）六类。
* **G3**：建立「三」的**五义统一模型**，解释为何六类看似互斥的解释可被同一结构统摄，并显式标注不可裁决处的边界。
* **G4**：时间三元组须引入奥古斯丁三分法（记忆/注意/期待）与 `distentio animi`，与老子生成论并置对照，并建立「过去=道/一，现在=二，未来=三」的映射及其有效性边界。
* **G5**：两组三元组（真问题·真需求·真目标、品质·技能·身份）须完成**四元关联建模**：与「三」的生成论同构关系、与时间三元组的映射关系、与 daoapps 四站时间线的落地对应。
* **G6**：产出**极简可复用可操作的人类生存指南**，须满足：正文 ≤ 1200 字、原则数量 ≤ 7 条、每条含判据与反例、可在 5 分钟内读完即用。
* **G7**：全流程按七概念方法论编排，中间探索过程（事实清单、四元组洞察、被V 修正的假设）随产出物一并落盘，可审计可追溯。
* **G8**：萃取为 `.agents/skills/` 下新 Skill，并完成 `README.md` + `capability-registry.md` 双索引登记。

## 4. 非目标（Non-Goals）

* **N1**：不修改 `projects/awesome-okf-xs/` 与 `projects/daoapps.github.io/` 任何文件（二者均为 git submodule，本任务只读引用与建立概念关联）。
* **N2**：不修改 `.agents/skills/role-model-methodology/SKILL.md` 的定义本体（真需求定义的分叉裁决仅在概念页记录，不回写他方资产）。
* **N3**：不收录《老子》全书全文，不做逐章校勘（只引第四十二章及必要的对照章句）。
* **N4**：不做养生、修炼、疗愈、占卜、决策建议（显式非医疗/非修炼声明）。
* **N5**：不改`.agents/` 任何既有规则、角色、命令、协议文件。
* **N6**：不新建 `.agents/docs/` 下的任何路径（该路径已于 2026-08-31 废止）。

## 5. 功能需求（Functional Requirements）

### FR-1 知识包结构与导航

* F1.1 新建 `docs/knowledge/dao-san-triads/`，含 `index.md`（束根，OKF v0.2）、`concepts/`（4 篇）、`references/`（2 篇）、`examples/`（1 篇生存指南实操），每目录含 `index.md`。
* F1.2 四篇概念页：`01-san-yi-birth.md`（三之本体论）、`02-time-triads.md`（时间三元组与奥古斯丁）、`03-action-triads.md`（两组行动三元组四元关联）、`04-survival-guide.md`（极简生存指南，承载 G6）。
* F1.3 信源 2 篇：`references/source-inventory.md`（事实与信源台账，含URL 与采集时点）、`references/adversarial-review.md`（V 门四视角攻击与修正记录）。
* F1.4 `examples/` 1 篇：`examples/01-worked-example.md`（以 daoapps 结伴站四站为真实案例的完整走查）。
* F1.5 在 `docs/knowledge/index.md` 注册：toctree 增 `dao-san-triads/index`，内容分类表增一行。
* F1.6 束根 toctree 收录全部子页；三层子目录 index 的 toctree 完整收录各自内容。

### FR-2 概念探究的严谨性

* F2.1 「三」的六类解释每类须登记：代表学者/注家、原文出处（书名+篇卷）、核心主张、证据强度评级。
* F2.2 帛书本第四十二章原文须完整引用并标注甲/乙本差异，「中气以为和」须标注《长沙马王堆汉墓简帛集成》说明与「冲/中」通假争议，不得单方面采信通说。
* F2.3 郭店楚简《太一生水》生成链（「太一生水…成岁而止」）须作为**独立文本证据**登记，并标注与帛书本的关系为「并行文本，非同一版本」。
* F2.4 「三合而后生」生物观（《穀梁传·庄公三年》「独阴不生，独阳不生，独天不生，三合然后生」、《楚辞·天问》「阴阳三合，何本何化」）须登记。
* F2.5 五义统一模型须给出**映射表**：六类解释各自落位哪一义；不可裁决处须显式声明边界。
* F2.6 奥古斯丁三分法须登记其**最强反驳**（时间三分法是人的注意活动对客观世界的投射，非时间自身性质），不得只引其结论。
* F2.7 时间三元组与老子生成论的映射须标注为**类比性关联**而非史实影响论；无证据的因果影响声明禁止写入。
* F2.8 两组行动三元组须登记 `role-model-methodology` v1.1.0 的定义本体行数锚点，并记录「真需求」定义在案例包与SKILL.md 间的措辞分叉（能力/缺口 vs 能力/状态）。

### FR-3 生存指南的可操作性

* F3.1 指南正文 ≤ 1200 字，原则 ≤ 7 条（硬约束，超出即不合格）。
* F3.2 每条原则须含：**判据**（可回答是/否或可观察）+ **反例**（至少 1 条，来自真实教训或推理失败案例）。
* F3.3 指南须给出**一条可当场执行的最小动作**（今天就能做，5 分钟内完成）。
* F3.4 指南须显式声明适用边界与不适用场景。
* F3.5 生存指南须与 daoapps 结伴站四站（修心/寻伴/成家/立业）建立映射，使哲学结构落到现世可走查的四站上。

### FR-4 七概念工作流产物

* F4.1 `index.md` 内含 R 阶段事实清单（编号 F-xxx，无因果推断词）、I 阶段洞察（四元组完整）、E 阶段模式（可迁移）、V 门摘要、G1-G4+V 质量门表格、CMD-LOG。
* F4.2 事实条数 ≥ 25（深度探究场景）；每条含可溯源信息（学者/书名/出处/URL/采集时点）。
* F4.3 洞察 ≥ 3 条，维度互不重叠，每条含反常识点。
* F4.4 E 阶段产出至少 1 个可迁移模式，须含触发场景 + 步骤 + ≥3 反模式 + 检验标准 + 跨域迁移。
* F4.5 V 门须 4 视角全覆盖、意见 ≥ 5 条且具体、采纳 ≥ 2 条并回归确认；被推翻的假设须显式记录。

### FR-5 Skill 萃取

* F5.1 在 `.agents/skills/dao-san-triads/` 下创建 SKILL.md，符合五要素模型（Trigger-Ready Description / Decision Tree / Progressive Disclosure ≤500 行 / Why-Explanation / Safety Checklist）。
* F5.2 Skill description 含完整触发词与「必须使用此技能」强制措辞。
* F5.3 更新 `.agents/skills/README.md`（分类表 + 计数）与 `.agents/capability-registry.md`（L1 索引）。
* F5.4 Skill 内引用的所有路径为相对路径，不含 `file:///`。

## 6. 非功能需求（Non-Functional Requirements）

* **NFR-1 规范合规**：全部 .md 含 YAML frontmatter 且 `type` 非空；束根含 `okf_version: "0.2"`。
* **NFR-2 语言与命名**：正文中文；文件名 kebab-case 纯英文加数字前缀。
* **NFR-3 链接规范**：交叉引用一律相对路径，禁止 `file:///`；跨子模块引用用 `../../projects/...` 形式。
* **NFR-4 编码**：UTF-8 无 BOM，通过 utf8 检查。
* **NFR-5 可导航性**：全部新增 .md 可由 `docs/index.md` 经 toctree 链可达。
* **NFR-6 可构建性**：Sphinx 构建无toctree/断链类错误。
* **NFR-7 只读边界**：`projects/` 下两个子模块零写入（验证方式：子模块 `git status` 无变化）。

## 7. 约束、依赖、假设与开放问题

### 约束

* C1：`projects/awesome-okf-xs/` 与 `projects/daoapps.github.io/` 是 git submodule，本任务**只读**。
* C2：产出物落`docs/knowledge/`（公开内容），非 `.agents/docs/`（已废止）。
* C3：`.agents/` 下仅新增 skill 目录与更新两个索引文件，不动既有资产。
* C4：引文须标注版本（帛书甲本/乙本/今本/郭店楚简本），不得笼统称「帛书本」——此纪律来自 `daoapps.github.io/AGENTS.md` 的实证教训。

### 依赖

* D1：`vendor/flexloop/docs/general/philosophy/engineering/three-as-interface.md`（「三」=接口/关系，全仓最系统的「三」工程阐释，已有 Ψ=Ψ(Ψ) 推导与设计三定律）。
* D2：`vendor/flexloop/docs/general/philosophy/laozi-boshu/de-jing/chapter-05.md`（帛书本第四十二章原文 + 「中气以为和」版本差异长段）。
* D3：`.agents/skills/role-model-methodology/SKILL.md` v1.1.0（两组三元组定义本体）。
* D4：`projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/taoxingzhi-youbenchang-huge/concepts/03-04`（两组三元组实战案例包，含工作表实体）。
* D5：`projects/awesome-okf-xs/doc/bundles/guoxue/laozi/boshu-reading/concepts/04-key-variants.md`（甲乙本异文对照范式）。
* D6：`docs/knowledge/mindfulness-positivity/`（同类知识包的最新落地范式，frontmatter + toctree + 双索引 + Skill 萃取全流程样板）。
* D7：`projects/daoapps.github.io/doc/jieban/origin.md`（四站人生时间线）、`covenant.md`（引文版本纪律）。

### 假设

* A1：R 阶段联网核验所得学术与信源可作为事实来源；标注为「机构/学者口径」的数字与主张不复核原始统计量。
* A2：两个子模块的现有状态即为基线，本任务不改变其门禁通过状态。

### 开放问题

* O1：「三」的最终本体裁决在学术上无定论（冯国超新解为 2024 年提出，尚需学界检验）。本任务**不给单一答案**，给的是「五义统一模型 + 判据 + 边界」——这是诚实且可复用的交付形态。若用户要求单一裁决，需另行裁定并声明立场。
* O2：`daoapps.github.io` 的关联仅限文档层概念映射（在本知识包内建立映射章节），是否需要在子模块站点内新增页面需子模块流程与用户另行决定。

## 8. 验收标准（Acceptance Criteria）

### rule 型（客观可判定）

| 编号 | 验收标准 |
|---|---|
| AC-R1 | `docs/knowledge/dao-san-triads/` 存在，含 `index.md`、`concepts/`（index + 01-04 共 5 篇）、`references/`（index + 02 共 3 篇）、`examples/`（index + 01 共 2 篇）。 |
| AC-R2 | 每个非保留名 .md 有 YAML frontmatter 且 `type` 非空；束根含 `okf_version: "0.2"`；概念/信源/示例页 type 分别为 Concept/Reference/Example。 |
| AC-R3 | 束根 toctree 收录全部 8 篇内容页；三层子目录 index 的 toctree 完整收录各自内容；`docs/knowledge/index.md` toctree 含 `dao-san-triads/index` 且分类表增一行。 |
| AC-R4 | 「三」的六类解释全部登记，每类含代表学者/注家、原文出处、核心主张、证据强度评级（`01-san-yi-birth.md`）。 |
| AC-R5 | 帛书本第四十二章原文完整引用并标注甲/乙本差异；「中气以为和」附《长沙马王堆汉墓简帛集成》说明与「冲/中」通假争议双向记载。 |
| AC-R6 | 郭店楚简《太一生水》生成链与《穀梁传》「三合而后生」生物观均已登记，且标注与帛书本的关系为并行文本/独立文本证据。 |
| AC-R7 | 五义统一模型含六类解释的映射表，且不可裁决处有显式边界声明。 |
| AC-R8 | `02-time-triads.md` 含奥古斯丁三分法（记忆/注意/期待）、`distentio animi`，且含时间三分法为「人的注意活动对客观世界的投射」这一反驳立场。 |
| AC-R9 | 时间三元组与老子生成论的映射被显式标注为类比性关联，全篇无未加证据的史实影响论断言。 |
| AC-R10 | `03-action-triads.md` 登记两组三元组定义本体行数锚点，并记录「真需求」措辞分叉（能力/缺口 vs 能力/状态）。 |
| AC-R11 | `04-survival-guide.md` 正文 ≤ 1200 字、原则 ≤ 7 条，每条含判据与 ≥1 条反例，含一条 5 分钟内可完成的最小动作，含适用边界声明。 |
| AC-R12 | `examples/01-worked-example.md` 以 daoapps 四站（修心/寻伴/成家/立业）为案例走通全链，含四站与生存指南原则的映射表。 |
| AC-R13 | `index.md` 含 ≥25 条事实（无因果推断词、含可溯源信息）、≥3 条四元组洞察、≥1 个含触发+步骤+≥3反模式+检验标准+跨域迁移的可迁移模式、4 视角 V 门摘要、G1-G4+V 质量门表、CMD-LOG。 |
| AC-R14 | `references/adversarial-review.md` 含 4 视角全覆盖、意见 ≥5 条且具体、采纳 ≥2 条、被推翻假设的显式记录与回归确认。 |
| AC-R15 | `.agents/skills/dao-san-triads/SKILL.md` 存在，正文 ≤500 行，含五要素（强制措辞 description + 决策树 + Why 解释 + 安全清单）。 |
| AC-R16 | `.agents/skills/README.md` 与 `.agents/capability-registry.md` 均含新 skill 登记项。 |
| AC-R17 | 全部新增 .md 交叉引用为相对路径、无 `file:///`；UTF-8 无BOM。 |
| AC-R18 | `projects/awesome-okf-xs/` 与 `projects/daoapps.github.io/` 的 `git status` 无变化。 |

### rubric 型（评分 0-5，≥4 为通过）

| 编号 | 评分维度 |
|---|---|
| AC-Q1 | **「三」解释谱系的穷尽性与诚实度**：5=六类解释全部登记且给出证据强度评级与不可裁决边界，不假装有唯一答案；3=主要解释覆盖但缺来源或评级；0=只取一说冒充定论。 |
| AC-Q2 | **关联建模的说服力**：5=四元关联（生成论同构/时间映射/行动三元组/daoapps 落地）各有独立论证且边界清晰；3=关联成立但部分为断言；0=并列罗列无关联论证。 |
| AC-Q3 | **生存指南的极简与可操作性**：5=≤1200字且每条判据可当场回答、反例具体、最小动作当天可做；3=原则正确但偏冗长或落地模糊；0=正确的废话。 |
| AC-Q4 | **中间过程的可审计性**：5=F/I/E/V 每阶段产物完整且被V 修正的假设显式可见；3=有过程记录但修正痕迹模糊；0=只有结论无过程。 |
| AC-Q5 | **版本纪律**：5=所有《老子》引文标注甲/乙本/今本/楚简本且通假争议双向记载；3=多数标注；0=笼统称「帛书本」。 |