---
status: "draft"
name: create-guiguzi-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域古籍《鬼谷子》原文与历代解读（正统道藏·陶弘景注本、ctext.org 中国哲学书电子化计划、维基文库、四库全书本、《隋书·经籍志》《新唐书·艺文志》书志著录、许富宏《鬼谷子集校集注》等公开学术资源），经双信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（《鬼谷子》原文属公共领域古籍，解读为公开学术知识）
---

# 《鬼谷子》OKF 知识包教程 Spec

## Why

用户希望系统化调研"鬼谷子本人相关的著作"——即以《鬼谷子》为核心的先秦纵横家经典（含本经阴符七术、持枢、中经及历代注疏）——获取**最权威、最真实**的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles`（最高可信度知识库）的恰当位置，生成可发布的 wiki 教程。《鬼谷子》托名"鬼谷子"（传说为苏秦、张仪之师），成书年代、作者归属、篇目存佚均争议极大（《汉书·艺文志》未著录、首见于《隋书·经籍志》），"权威与真实"必须通过**双信源逐字核对原文** + **诚实呈现"托名层/文本层"之分** + **篇目存佚源流考证**来保证，而非沿用单一网络流行文本。

## What Changes

- 新增分组 `bundles/think/guiguzi/`（鬼谷子经典分组，仿 `think/laozi/`、`think/huangdi/` 三层模式：域→组→束）
- 新增知识包 `bundles/think/guiguzi/guiguzi/`：
  - `index.md`（bundle 根，快速导航 + 定位 + 学习路径）
  - `concepts/`（7 篇核心概念：什么是鬼谷子 / 版本源流 / 作者与成书之争 / 原文全录与篇目存佚 / 核心概念解读 / 历代注家与立场 / 影响与纵横家传统）
  - `examples/`（2 篇实操：捭阖篇逐句精读、通读计划）
  - `references/`（3 篇信源登记：权威底本、注本分级表、交叉引用）
  - `facts.md` / `insights.md` / `log.md`（方法论文档闭环工作记录 + 更新历史）
- 更新导航索引：`think/index.md`（新增分组行 + toctree）、`bundles/index.md`（`total_bundles` 286→287、`groups` 32→33、think 域描述「5 束 · 2 组」→「6 束 · 3 组」、生态关系 mermaid 图中 think 节点标注与分组表行）
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记，G1）→ I（洞察，G2）→ E（萃取 ≥2 个可复用阅读模式，G3）→ V（对抗审查：原文逐字双源核对）→ C（原子提交 + `invoke gates.all` 质量门）

**关键决策（落位）**：「鬼谷子」既是人名（传说中苏秦、张仪之师）又是书名（《鬼谷子》），故分组命名 `guiguzi/`（与 `laozi/`、`huangdi/` 的「人名→经典束」命名逻辑一致），束命名为 `guiguzi/`；未来若新增与鬼谷子思想相关的其他束（如《本经阴符七术》专题），可归入同组。

**关键决策（底本）**：以**正统道藏本（陶弘景注）**为核心底本，辅以 ctext.org《鬼谷子》、维基文库《鬼谷子》、四库全书本，并以许富宏《鬼谷子集校集注》（中华书局）作为现代校勘参照，双源逐字核对现存篇目；亡佚篇目（转丸、胠乱）与《持枢》残篇、《中经》《本经阴符七术》如实标注存佚状态，不拼合构拟文本。

## Impact

- Affected specs: `laozi-lineage-okf-bundle`、`boshu-laozi-wiki`、`create-yinfujing-okf-wiki`（仅通过 references/cross-ref.md 交叉引用，不修改其产物）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增文件与两处索引更新；提交发生在子模块仓库内，主仓 gitlink 变更需一并同步（如适用）
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓其他文件

## ADDED Requirements

### Requirement: 权威原文忠实性

知识包 SHALL 提供《鬼谷子》现存篇目原文全录（道藏本十二篇 + 本经阴符七术 + 中经 + 持枢残篇，亡佚篇目存目说明），原文文字 SHALL 经至少两个独立权威信源逐字核对（如：正统道藏陶弘景注本、ctext.org《鬼谷子》、维基文库《鬼谷子》、四库全书本），每处关键异文在 facts.md 登记编号事实与信源 URL，异文处显式标注"某本作某"并给出注家出处。

#### Scenario: 原文核对

- **WHEN** 读者对照任一权威底本核查 bundle 中的原文全录
- **THEN** 逐字一致（异文处显式标注"某本作某"并给出注家出处）

#### Scenario: 篇目存佚如实呈现

- **WHEN** 教程陈述《鬼谷子》篇目结构
- **THEN** 明确区分「现存篇目」「亡佚存目（转丸、胠乱）」「残篇（持枢）」，并说明道藏本卷次划分（上/中/下或外篇）依据，不作构拟补全

### Requirement: 托名层与文本层区分

知识包 SHALL 诚实呈现《鬼谷子》的托名传说与学术考证：当教程陈述"鬼谷子著"或"鬼谷子为苏秦、张仪之师"时，显式标注其为史传记载/传统托名说法，并列出书志著录源流（《汉书·艺文志》未著录 → 《隋书·经籍志》首录三卷皇甫谧注 → 《新唐书·艺文志》乐壹注/尹知章注）与学界主要成书年代学说（苏秦托名说、后人伪托说、旧本流传说等）及依据文献（《史记》苏秦/张仪列传、钱穆、余嘉锡等考证），不将托名当作史实陈述。

#### Scenario: 作者争议呈现

- **WHEN** 读者阅读"作者与成书"章节
- **THEN** 至少呈现 2 种不同的成书/作者学说，各自标注依据文献与出处，结论不武断

### Requirement: 解读多元性与立场标注

知识包的解读 SHALL 覆盖多元注家传统并标注立场：皇甫谧注（晋，最早著录）、陶弘景注（梁，现存主要底本）、尹知章注（唐）、乐壹/乐台注（唐），以及现代注本分级（许富宏《鬼谷子集校集注》、陈蒲清《鬼谷子详解》等）。每处引用注明注家与出处。

#### Scenario: 关键句多视角

- **WHEN** 读者阅读"捭阖者，道之大化，说之变也，必豫审其变化"等核心句解读
- **THEN** 至少呈现 1 种传统注家（如陶弘景注）与 1 种现代校注的对照，并标注出处

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type: OKF`、`source`、`generated`/`verified`、`status`、`stale_after`，规范见 `.agents/rules/frontmatter.md`）、bundle 根 index 以 `{toctree}` 引用全部内容文档、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

#### Scenario: 质量门通过

- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **THEN** toctrees 与 utf8 检查全部通过，无孤立文档、无断链

### Requirement: 方法论闭环（G1–G3 + V）

教程 SHALL 记录 seven-concepts 场景4 方法论痕迹：facts.md ≥30 条编号事实且无因果推断词（G1）、insights.md ≥3 条带四元组洞察（G2）、≥2 个可复用阅读模式含触发场景/核心步骤/反模式/迁移示例（G3），并在提交前经对抗审查（V）完成原文与事实抽查。

#### Scenario: 事实抽查

- **WHEN** 对抗审查随机抽取 10 条 facts.md 事实核对信源
- **THEN** 全部与登记信源一致，无虚构引证

## MODIFIED Requirements

无（本任务为全新增量；`think/index.md` 与 `bundles/index.md` 仅追加统计与导航行，属索引维护而非既有需求变更）。

## REMOVED Requirements

无。

## 开放问题

- 无（底本与落位决策已在 spec 中给出；若实现阶段发现双信源核对存在无法调和的异文冲突，在 facts.md 登记并列呈现，不作裁决）
- 「本经阴符七术」与《阴符经》的关系、以及《鬼谷子》与《战国纵横家书》的互证，属影响/交叉引用范畴，若篇幅过大可在实现阶段拆分为独立束并归入同组 `guiguzi/`