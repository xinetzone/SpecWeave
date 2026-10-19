---
type: Knowledge Map
title: "个人变现方向发现方法论 · 骨架判定与三层知识地图（knowledge-map.md）"
description: "操作可复现性两问判定结论、三层知识拆分地图（事实层/方法层/路径层）、concepts 与 examples 篇目清单（含单一职责边界），以及 bundle 归属候选对照表（industry vs personal-growth）与命名三查留痕。"
generated: { by: "reference_agent/okf-writer", at: "2026-10-17T00:00:00Z" }
status: draft
sources:
  - id: spec
    resource: "./spec.md"
    title: "本 Spec 主文件（FR3 骨架判定与三层拆分要求）"
  - id: facts
    resource: "./facts.md"
    title: "事实登记（F 编号出处）"
  - id: sources
    resource: "./sources.md"
    title: "信源候选清单（S 编号出处）"
---

# 个人变现方向发现方法论 · 骨架判定与三层知识地图（knowledge-map.md）

> 本文覆盖 Task 3 三项产出：① 操作可复现性两问判定；② 三层拆分地图与 concepts / examples 篇目清单；③ 归属候选对照表。
> 篇目命名一律 **kebab-case 英文**；正文中文；依赖 `facts.md` 的 F 编号与 `sources.md` 的 S 编号。

---

## 1. 操作可复现性两问判定（决定是否设 `examples/`）

### 1.1 两问逐项判定

| 问号 | 判定问题 | 结论 | 理由（基于本包信源与方法层设计） |
|---|---|---|---|
| ① | 本包是否含读者可**照做的自评 / 验证操作流程**（盘点表、验证实验步骤）？ | **是** | 四类信源均提供可操作的自评与验证工具：职业锚自评（F-003~F-005）、人格/兴趣自评（F-008 六类型，须标争议边界 F-041）、个人商业模式画布填表（F-049/F-051）、价值主张画布 fit 图（F-080）、Mom Test 提问脚本（F-077/F-078）、MVP 实验设计（F-071~F-073）、决策阈值——每一步都有可填的表或可执行的脚本。 |
| ② | 这些流程是否**可复现**（有输入、有步骤、有判定标准）？ | **是** | 每步均可给出「输入项 → 操作步骤 → 判定标准」三要素：如候选方向生成有输入（自评结果 + 资源约束）与步骤（画布九模块逐格填写）；需求验证有输入（访谈对象清单）、步骤（Mom Test 问过去行为）、判定标准（如「至少 N 位受访者已在为现方案付费」的信号阈值）；决策有 go/no-go 判定清单与首个 30 天行动。 |

### 1.2 判定结论

**两问皆「是」→ 本包设 `examples/`**（自评盘点表、候选方向生成工作坊、需求验证实验模板、决策清单），理由如上。

> **对照说明**：邻近同簇 bundle `zhihu-monetization` 判为「无 examples/」（其信源为平台规则宣告页，行动清单为设计产物、不可照做）。本包与之相反——四类信源本身即提供**读者可自行填写的工具**，故必须承载 `examples/`，否则方法层的「可操作性」（AC-8，阈值 ≥4）会因缺少可填表而失分。

### 1.3 若设 `examples/` 的边界纪律

- `examples/` 只放**可填写的工具与脚本**，不放理论讲解（理论归 concepts）；
- 一切自评工具页须**显著标注「非决定论、不得作为方向判定依据」**（对齐 F-041 / AC-10）；
- 收益/规模类字段一律标「非承诺」（对齐 FR 非目标与 AC-10）。

---

## 2. 三层拆分地图与篇目清单

### 2.1 三层职责定义

| 层 | 回答的问题 | 内容性质 | 承载目录 | 对应 F 编号段 |
|---|---|---|---|---|
| **事实层** | 有哪些权威框架与工具？它们是谁/何时提出的？ | What / Who / When——权威来源登记，观点标〔主张〕 | `concepts/01` ~ `concepts/04` | F-001~F-082 分四组 |
| **方法层** | 怎么从「我是谁」走到「市场愿意付费的候选方向」？ | How——自评→候选生成→需求验证→决策的操作方法与判定标准；因果解释标「洞察/推断」 | `concepts/05` ~ `concepts/08` | F-003~F-005、F-049~F-062、F-071~F-082 |
| **路径层** | 不同起点/资源约束的人各自该怎么走？边界与误区是什么？ | 面向个体的方向选择矩阵、主路径、决策清单、风险边界 | `concepts/09` ~ `concepts/10` | 综合方法层与事实层 |

> **信源先行纪律**：`references/(article-source.md + verification.md)` → `concepts/` → 各级 `index.md` 最后写（对齐 FR3）。

### 2.2 `concepts/` 篇目清单（11 篇，`00-overview.md` 起编号）

| 序号 | 文件名 | 所属层 | 一句话职责边界（单一职责） |
|---|---|---|---|
| 00 | `00-overview.md` | 总览 | 本包定位、三类误区（跟风赛道 / 爱好即能力 / 只学技巧不问匹配）、bundle 地图、时效与「非承诺 + 非决定论」边界声明；**不展开任何框架细节** |
| 01 | `01-career-matching-facts.md` | 事实层 | C1 权威框架事实登记：Schein 职业锚、Holland RIASEC、Designing Your Life、Savickas CCT、Minnesota TWA、Super；含 RIASEC 学术局限与 ikigai 溯源勘误；**只登记事实不教方法** |
| 02 | `02-strengths-talent-facts.md` | 事实层 | C2 优势/天赋识别事实登记：CliftonStrengths、VIA、Dreyfus 五阶段、刻意练习及其元分析争议、grit 争议、心流、SDT；**含性格测评（MBTI）科学效度争议与"非决定论"强制标注**；只登记事实 |
| 03 | `03-monetization-model-facts.md` | 事实层 | C3 个人商业模式与变现模式事实登记：Business Model You、BMC 九模块、Company of One、1000 True Fans（含勘误）、So Good They Can't Ignore You、Naval 特定知识×杠杆、Long Tail、$100 Startup、Start with Why；只登记事实 |
| 04 | `04-validation-method-facts.md` | 事实层 | C4 需求验证事实登记：Lean Startup / MVP、Jobs to be Done、Mom Test、价值主张画布、客户开发四步；只登记事实 |
| 05 | `05-self-inventory-method.md` | 方法层 | **步骤 1 自我盘点**：职业锚自评排序 + 优势/心流时刻清单 + 资源约束盘点（时间/资金/技能/关系）、内在动机核对（SDT 三需要）；给出输入项、步骤与产出物；不涉及候选生成与验证 |
| 06 | `06-candidate-generation-method.md` | 方法层 | **步骤 2 候选方向生成**：以个人商业模式画布 + 「特定知识 × 杠杆 × 担责」矩阵 + 「问题优先」（PG 找自己的问题）生成 3~5 个候选；产出候选方向卡；不验证、不决策 |
| 07 | `07-needs-validation-method.md` | 方法层 | **步骤 3 需求验证**：JTBD 三问（功能/社会/情感）+ Mom Test 提问脚本（问过去行为）+ 最小验证实验（落地页/MVP/预售）设计与判定标准（信号阈值、反模式）；不生成候选、不决策 |
| 08 | `08-decision-and-launch-method.md` | 方法层 | **步骤 4 决策与启动**：信号汇总表 → go/no-go 判定阈值 → 首个 30 天行动拆解 → 退出/迭代条件；不含路径层的人群矩阵 |
| 09 | `09-path-matrix.md` | 路径层 | **方向选择矩阵**：按起点（在职副业 / 全职转型 / 技能型创作者 / 被动转型）与资源约束（时间 / 资金 / 技能 / 关系）给出四条主路径及切换条件；不重复方法层步骤细节 |
| 10 | `10-boundaries-and-risks.md` | 路径层 | **边界与风险**：伪科学自评警示（MBTI 等）、画饼式路径证伪、相关性≠因果、收益不确定性、时效与单源清单索引；不承载正向方法 |

> **拆分粒度自评（对齐 TR-3.2 阈值 ≥4）**：事实层按 C1-C4 四类分四篇（每篇单一信源类别）；方法层按「盘点→生成→验证→决策」四步分四篇（每篇单一动作、可独立执行）；路径层分矩阵/边界两篇（正向路径 vs 边界风险）。每篇均有明确「不做」边界，无一篇同时承担两层职责。

### 2.3 `examples/` 篇目清单（4 篇 + 索引）

| 序号 | 文件名 | 对应方法层步骤 | 内容（可照做的工具） |
|---|---|---|---|
| — | `examples/index.md` | — | examples 目录索引 + toctree + 「非决定论 / 非承诺」总声明 |
| 01 | `examples/01-self-inventory-worksheet.md` | 步骤 1（`05`） | 自评盘点表：职业锚排序表、优势/心流时刻清单、资源约束四栏表、内在动机自检 |
| 02 | `examples/02-candidate-direction-workshop.md` | 步骤 2（`06`） | 候选方向生成工作坊：个人商业模式画布填写指引、特定知识×杠杆矩阵表、候选方向卡模板 |
| 03 | `examples/03-validation-experiment-template.md` | 步骤 3（`07`） | 需求验证实验模板：Mom Test 提问脚本（10 问）、实验卡（假设/对象/动作/信号阈值）、验证记录表 |
| 04 | `examples/04-decision-checklist.md` | 步骤 4（`08`） | 决策清单：信号汇总表、go/no-go 判定勾选、首个 30 天行动清单、退出条件 |

### 2.4 bundle 完整目录结构（供 E 阶段执行）

```
<bundle>/
├── index.md                    # okf_version: "0.2" + toctree + 主题关联互链 + 已知边界
├── log.md                      # 两问判定理由、归属理由、更新历史
├── concepts/
│   ├── index.md                # toctree
│   ├── 00-overview.md ~ 10-boundaries-and-risks.md   # 11 篇
├── examples/
│   ├── index.md                # toctree
│   └── 01-self-inventory-worksheet.md ~ 04-decision-checklist.md   # 4 篇
└── references/
    ├── index.md                # toctree
    ├── article-source.md       # 与 facts.md 双份登记的 F 编号事实清单
    └── verification.md          # 核验结论表 + 勘误四清单 + 单源清单 + 证据 URL
```

---

## 3. 归属候选对照表（industry vs personal-growth 论证）

### 3.1 候选位置评估

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `sheke/industry/`（AI 行业与商业趋势） | **✅ 推荐** | ① 既有同主题变现簇**五束全在此组**（`ai-monetization`、`monetization-essence`、`zhihu-monetization`、`overseas-freelance-night-work`、`ai-one-person-micro-product`），本包是其「方向发现」前置/上位方法论，放入可形成完整闭环并互链；② 组收录边界为「行业趋势、商业模式与产品生态分析」（组 index 原文），本包正是**商业模式（个人）分析 + 变现方向方法论**；③ 组内已有「非操作教程/操作教程」并存的先例（`ai-one-person-micro-product` 标注「商业分析，非操作教程」），不排斥本包的方法/路径层形态；④ 计数接入成本最低（组 +1、域 +1、总 +1）。 |
| `sheke/personal-growth/`（个人成长与自我提升） | **❌ 次选（不推荐）** | 该组定位为「跨书籍的综合方法论与实操教程」（组 index 原文），内容以**魅力情商、榜样人物精读、生活方式方案库**为主，**其核心主题是"个人成长"而非"变现"**。本包虽含自评/自省成分（与 personal-growth 有弱交集），但主线是「找到可变现的方向」——若落此组，将**割裂与 industry 变现簇的互链**（spec「主题关联互链」段要求），并降低检索一致性。此外该组已 15 束、主题集中的成长类，混入更显突兀。 |
| `sheke/industry/` 之外新建顶级分组 | **❌ 否** | spec 约束明确「不新建顶级分组」，且无必要——既有 industry 组已能容纳。 |
| `sheke/marketing/`（市场营销） | **❌ 否** | 该组已含「真需求发现通识」「先卖后做需求验证」等**需求验证**内容，与本包 C4（Mom Test/MVP）有部分重叠；但本包主线是**面向个人个体的变现方向发现**，而非面向企业/运营的营销战术（STP/4P/AARRR 等），主题重心不同，放入会与营销方法论混淆。 |
| `sheke/finance/`（个人理财与投资） | **❌ 否** | 该组聚焦收益数学、资产配置、指数基金等**投资通识**，主题为「钱的管理」；本包主题为「方向的发现」，无交集。 |
| `sheke/workplace/`（职场与管理） | **❌ 否** | 该组面向行政人事岗位的**职业进修**（人力六大模块、公文写作、劳动法），是「打工岗位能力」而非「变现方向」；虽同为职场/生涯主题，但定位差异大（组织内 vs 个体经营者）。 |

### 3.2 推荐结论

> **推荐归属：`projects/awesome-okf-xs/doc/bundles/sheke/industry/<bundle>/`**——即既有变现簇所在组，与 `ai-monetization`、`monetization-essence`、`zhihu-monetization`、`overseas-freelance-night-work`、`ai-one-person-micro-product` 构成「变现簇」完整性。
>
> **理由汇总**：① 主题一致性（变现方向发现 = 变现簇的方法论入口）；② 既有五束同簇先例提供互链与形态参照；③ 收录边界覆盖「个人商业模式分析」；④ 计数接入成本最低；⑤ 不违反「不新建顶级分组」约束。

### 3.3 bundle 命名三查留痕（对齐 spec 待决问题 1）

| 查项 | 结论 |
|---|---|
| 查同类命名惯例 | 同组既有一律 kebab-case 英文、语义直白：`ai-monetization`、`monetization-essence`、`zhihu-monetization`、`overseas-freelance-night-work`、`ai-one-person-micro-product`。命名应沿用 `<主题>-<角度>` 结构。 |
| 查是否重名 | 现存同组无 `monetization-direction`；与 `monetization-essence`（变现本质公理）语义区分明确（direction = 方向发现，essence = 本质）。 |
| 查语义准确性 | 暂定 `monetization-direction` 准确表达「变现方向发现」；备选 `monetization-direction-discovery`（更全但冗长）、`find-your-monetization-direction`（动词式，与组内名词式惯例不符）。**建议定稿 `monetization-direction`**（与 spec 暂定名一致）。 |

---

## 4. 本文件结论摘要（供 log.md / 后续 Task 引用）

1. **两问判定**：皆「是」→ **设 `examples/`**（4 篇 + 索引）。
2. **三层结构**：事实层 4 篇（C1-C4）→ 方法层 4 篇（盘点/生成/验证/决策）→ 路径层 2 篇（矩阵/边界）+ 00 总览 = **concepts 11 篇**。
3. **归属结论**：**`sheke/industry/monetization-direction/`**（既有变现簇，构成完整闭环）。
4. **骨架缺口**：无——四类信源齐备（C1 18 / C2 20 / C3 20 / C4 16 条），82 条 F 事实全部有 S 出处。
