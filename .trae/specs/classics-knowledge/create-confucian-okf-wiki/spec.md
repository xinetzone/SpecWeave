---
name: create-confucian-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域儒家经典原文与历代解读（朱熹《四书章句集注》、ctext.org《論語》《孟子》《禮記》全文、中华书局《十三经注疏》阮元校刻本、杨伯峻《论语译注》《孟子译注》、钱穆《论语新解》等公开学术资源），经 Web 信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（儒家经典原文属公共领域古籍，注疏与解读为公开学术知识）
---

# 儒家四书 OKF 知识包教程 Spec

## Why

用户希望全面调研儒家相关著作，获取**最权威、最真实**的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles`（最高可信度知识库）的恰当位置，生成可发布的 wiki 教程。儒家经典 corpus 庞大（十三经系统），"权威与真实"必须通过**精选核心文本双信源逐字核对**与**显式分层（经文层/注疏层/现代解读层）**来保证，而非沿用单一流行文本或混淆注家引申与经文本义。

## What Changes

- 新增分组 `bundles/think/confucian/`（儒家知识包分组，仿 `think/laozi/` 与 `think/psi/` 三层模式：域→组→束）
- 新增知识包 `bundles/think/confucian/four-books/`（bundle 根目录用纯英文 kebab-case `four-books`，正文与标题用"四书"）：
  - `index.md`（bundle 根：快速导航 + 定位 + 学习路径 + toctree，含 OKF v0.2 frontmatter）
  - `concepts/`（8 篇核心概念，见 Task 4）
  - `examples/`（3 篇实操，见 Task 5）
  - `references/`（4 篇信源登记，见 Task 6）
  - `facts.md` / `insights.md` / `log.md`（方法论文档闭环工作记录）
- 更新导航索引：`think/index.md`（新增分组行 + toctree + 域描述）、`bundles/index.md`（统计数字 286→287 束、32→33 组，think 域 "5 束 · 2 组"→"6 束 · 3 组"，新增分组表行）
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记 ≥40 条，G1）→ I（洞察 ≥4 条四元组，G2）→ E（沉淀可复用经典阅读模式，G3）→ V（对抗审查：原文双源抽查核对）→ C（原子提交 + `invoke gates.all` 质量门）

**关键决策（落位）**：儒家为学派（非单人），故分组命名 `confucian/`（英文 kebab-case）；首个 bundle 聚焦**四书**（朱熹结集的《大学》《中庸》《论语》《孟子》，元代以来科举法定读本、儒家阅读传统的标准单元）。儒家全 corpus（五经、十三经、《荀子》《传习录》及注疏传统）在概念文档中作总览覆盖，未来可作增量 bundle（如 `five-classics/`、`xunzi/`、`chuanxilu/`）归入同组扩展。

**关键决策（底本与核对范围）**：原文以**通行定本**（朱熹《四书章句集注》所定系统之今通行本）为底本，以 **ctext.org《論語》《孟子》《禮記》全文**与**第二独立信源**（如 Wikisource《論語》/《孟子》/《禮記》、中华书局整理本公开页）**双源逐字核对**。核对范围：
- 《大学》《中庸》**全文**（各约 1.8k/3.6k 字，合计约 5.4k 字）
- 《论语》精选约 30–40 章（学而、为政、里仁、雍也、述而、颜渊、子路、宪问、卫灵公、季氏、阳货、子张等篇核心章句）
- 《孟子》精选约 15–20 章（四端、浩然之气、义利之辨、民贵君轻、性善等核心段落）
- 每处关键异文在 facts.md 登记编号事实与信源 URL；不采用未经核对的拼合文本。

**关键决策（解读分层）**：解读覆盖**汉学（何晏《论语集解》、赵岐《孟子注》）→ 宋学（朱熹《四书章句集注》）→ 清代考据（刘宝楠《论语正义》、焦循《孟子正义》）→ 现代（杨伯峻《论语译注》《孟子译注》、钱穆《论语新解》）→ 心学旁支（王阳明《传习录》）**五条注疏脉络，每处引用注明注家与出处，关键章句至少呈现 2 种立场。

**关键决策（篇幅）**：四书全文合计约 6 万字，全逐字双源核对属超大规模任务。本 spec 以"四书体系 + 精选核对"为边界：大学中庸全文核对 + 论孟核心章句核对 + 四书体系与注疏全景，兼顾"最真实原文"与工程可行性；如用户后续要求补全论孟全文，作为增量 bundle 扩展，不阻塞当前交付。

## Impact

- Affected specs: `boshu-laozi-wiki`、`laozi-lineage-okf-bundle`、`create-zhuangzi-okf-wiki`（仅通过 references 交叉引用，不修改其产物）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增文件与两处索引更新；提交发生在子模块仓库内
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓文件（除 `.trae/specs/classics-knowledge/create-confucian-okf-wiki/` 规格与工作记录）

## ADDED Requirements

### Requirement: 权威原文忠实性

知识包 SHALL 提供《大学》《中庸》全文（含《论语》《孟子》精选核心章句），且原文文字 SHALL 经至少两个独立权威信源逐字核对（ctext.org + Wikisource 或中华书局整理本公开页），每处关键异文在 facts.md 登记编号事实与信源 URL。

#### Scenario: 原文核对

- **WHEN** 读者对照任一权威底本核查 bundle 中的《大学》《中庸》全文与论孟精选章句
- **THEN** 逐字一致（异文处显式标注"某本作某"并给出注家/底本出处）

#### Scenario: 三层文本属性区分

- **WHEN** 教程陈述某文本属性（如"《大学》《中庸》本为《礼记》两篇，朱熹抽出独立成书"、"《论语》为孔子弟子及再传弟子纂录"）
- **THEN** 显式标注文本层（经文层/注疏层/现代解读层）与成书归属的传统说法及学界共识，不将传统托名/归属当作史实陈述

### Requirement: 解读多元性与立场标注

知识包的解读 SHALL 覆盖多元注家传统并标注立场：何晏《论语集解》（汉魏古注）、赵岐《孟子注》、朱熹《四书章句集注》（理学）、刘宝楠《论语正义》与焦循《孟子正义》（清代考据）、王阳明《传习录》（心学）、杨伯峻《论语译注》与钱穆《论语新解》（现代）。每处引用注明注家与出处。

#### Scenario: 关键章句多视角

- **WHEN** 读者阅读"克己复礼为仁""浩然之气""格物致知"等核心概念的解读
- **THEN** 至少呈现 2 种不同立场（如朱熹理学解与王阳明心学解、或汉学古注与宋学新解）的注家观点并标注出处

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type: OKF`、`source`/`sources`、`generated`、`status`、`stale_after`，规范见 `projects/awesome-okf-xs/.agents/rules/frontmatter.md`；仅 bundle 根 index 可带 `okf_version`）、bundle 根 index 以 `{toctree}` 引用全部内容文档（含 facts/insights/log）、分组根 index 带 `type: group` frontmatter、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

#### Scenario: 质量门通过

- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **THEN** toctrees 与 utf8 检查全部通过，无孤立文档、无断链

#### Scenario: 索引统计一致

- **WHEN** 检查 `bundles/index.md` frontmatter 与正文统计
- **THEN** total_bundles=287、groups=33，think 域显示 "6 束 · 3 组" 且分组表含 confucian 行，与实际目录结构一致

### Requirement: 方法论闭环（G1–G3 + V）

教程 SHALL 记录 seven-concepts 场景4 方法论痕迹：facts.md ≥40 条编号事实且无因果推断词（G1）、insights.md ≥4 条带四元组（陈述/证据/反常识/行动）洞察（G2）、≥2 个可复用经典阅读模式含触发场景/核心步骤/反模式/迁移示例（G3，沉淀于 insights.md 与通读计划示例），并在提交前经对抗审查（V）完成原文与事实抽查。

#### Scenario: 事实抽查

- **WHEN** 对抗审查随机抽取 10 条 facts.md 事实核对信源
- **THEN** 全部与登记信源一致，无虚构引证

## MODIFIED Requirements

无（本任务为全新增量；`think/index.md` 与 `bundles/index.md` 仅追加统计与导航行，属索引维护而非既有需求变更）。

## REMOVED Requirements

无。

## 开放问题

- 论孟全文是否补全：本 spec 设定为"核心章句精选 + 大学中庸全文"，若读者后续需要《论语》《孟子》全文逐字解读，作为增量 bundle（如 `analects-full/`）扩展，不阻塞当前交付。
- 底本异文冲突：若实现阶段发现双信源核对存在无法调和的异文（如论孟通行本与出土简本差异），在 facts.md 登记并列呈现，不作裁决。
- 五经/荀子/传习录深读：本 spec 仅总览覆盖，后续按需开增量 bundle 归入 `confucian/` 分组。
