---
name: create-zhuangzi-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域经典《庄子》（《南华经》）原文与历代解读（郭象注本系统、ctext.org《莊子》全文、郭庆藩《庄子集释》、王先谦《庄子集解》、陈鼓应《庄子今注今译》等公开学术资源），经 Web 信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（《庄子》原文属公共领域古籍，解读为公开学术知识）
---

# 《庄子》OKF 知识包教程 Spec

## Why

用户希望系统化获取《庄子》本人相关著作的**最权威、最真实**的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles`（最高可信度知识库）的恰当位置，生成可发布的 wiki 教程。《庄子》33 篇存在明确的**作者分层**（内篇 7 篇历来被认定为庄子自著，外篇 15、杂篇 11 多为门人后学之作），且晋代郭象删定为 33 篇是现存通行定本的起点。"权威与真实"必须通过**双信源逐字核对原文**与**诚实呈现"庄子自著层/后学层/注家层"三层之分**来保证，而非沿用单一流行文本或混淆以内篇为整书。

## What Changes

- 新增分组 `bundles/think/zhuangzi/`（庄子经典分组，仿 `think/laozi/` 与 `think/huangdi/` 三层模式：域→组→束）
- 新增知识包 `bundles/think/chuang-tzu/`（bundle 根目录用纯英文 kebab-case `chuang-tzu`，正文与标题用"庄子"）：
  - `index.md`（bundle 根：快速导航 + 定位 + 学习路径 + toctree）
  - `concepts/`（8 篇核心概念，见 Task 5）
  - `examples/`（3 篇实操，见 Task 6）
  - `references/`（3 篇信源登记，见 Task 7）
  - `facts.md` / `insights.md`（方法论文档闭环工作记录）
- 更新导航索引：`think/index.md`（新增分组行 + toctree）、`bundles/index.md`（统计数字、think 域描述与分组表行）
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记，G1）→ I（洞察，G2）→ E（萃取 ≥2 个可复用阅读模式，G3）→ V（对抗审查：原文逐字双源核对）→ C（原子提交 + `invoke gates.all` 质量门）

**关键决策（落位）**：《庄子》出于庄周（人名），故分组命名 `zhuangzi/`（与 `laozi/` 命名逻辑一致：人名→经典束）；bundle 根目录名取"庄子"的威妥玛/通用英文转写 `chuang-tzu` 以满足"文件名 kebab-case 纯英文"约束。未来《庄子》相关衍生（如《外篇》专题、《天下篇》学术史）可归入同组。

**关键决策（底本与作者分层）**：以**郭象注 33 篇本**为底本（晋郭象删定，是现存《庄子》通行定本的源头），内篇 7 篇（《逍遥游》《齐物论》《养生主》《人间世》《德充符》《大宗师》《应帝王》）认定庄子自著、作**全文双源逐字核对**；外篇 15、杂篇 11 作**结构概述 + 名篇精选**（如《秋水》《天下》《至乐》等），并显式标注其"门人后学"属性。不采用网络未经核对的拼合文本。

**关键决策（篇幅）**：《庄子》全文约七万字，全 33 篇逐字双源核对属超大规模任务。本 spec 以"庄子本人自著"为核心边界：内篇 7 篇全文逐字核对 + 外/杂篇概述与精选，兼顾"最真实原文"与工程可行性；如用户后续要求补全外/杂篇全文，作为增量 bundle 扩展。

## Impact

- Affected specs: `laozi-lineage-okf-bundle`、`boshu-laozi-wiki`、`create-yinfujing-okf-wiki`（仅通过 references/cross-ref.md 交叉引用，不修改其产物）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增文件与两处索引更新；提交发生在子模块仓库内
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓文件（除 `.trae/specs/classics-knowledge/create-zhuangzi-okf-wiki/` 规格与工作记录）

## ADDED Requirements

### Requirement: 权威原文忠实性

知识包 SHALL 提供《庄子》内篇 7 篇全文（含外/杂篇精选段落），且原文文字 SHALL 经至少两个独立权威信源逐字核对（如：郭象注本系统的中华经典整理本、ctext.org《莊子》全文、四库全书本），每处关键异文在 facts.md 登记编号事实与信源 URL。

#### Scenario: 原文核对

- **WHEN** 读者对照任一权威底本核查 bundle 中的内篇全文与精选段落
- **THEN** 逐字一致（异文处显式标注"某本作某"并给出注家出处）

#### Scenario: 三层作者属性区分

- **WHEN** 教程陈述某篇为"庄子作"或某说法为传统归属
- **THEN** 显式标注作品层（庄子自著内篇 / 门人后学外杂篇 / 注家层），并列出学界主要归属学说与依据（如内篇传庄子自作、外杂篇多后学之所增益等），不将传统托名/归属当作史实陈述

### Requirement: 解读多元性与立场标注

知识包的解读 SHALL 覆盖多元注家传统并标注立场：郭象注（玄学化）、成玄英《庄子疏》（重玄学）、陆德明《庄子音义》、王先谦《庄子集解》（训诂）、郭庆藩《庄子集释》（汇集）、陈鼓应《庄子今注今译》（现代注释）。每处引用注明注家与出处。

#### Scenario: 关键句多视角

- **WHEN** 读者阅读"逍遥游""齐物论"等核心篇的核心句解读
- **THEN** 至少呈现 2 种不同立场（如玄学解与训诂解、或庄学本文解与注家引申解）的注家观点并标注出处

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type: OKF`、`source`、`generated`/`verified`、`status`、`stale_after`，规范见 `projects/awesome-okf-xs/.agents/rules/frontmatter.md`）、bundle 根 index 以 `{toctree}` 引用全部内容文档、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

#### Scenario: 质量门通过

- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **THEN** toctrees 与 utf8 检查全部通过，无孤立文档、无断链

### Requirement: 方法论闭环（G1–G3 + V）

教程 SHALL 记录 seven-concepts 场景4 方法论痕迹：facts.md ≥40 条编号事实且无因果推断词（G1）、insights.md ≥4 条带四元组洞察（G2）、≥2 个可复用阅读模式含触发场景/核心步骤/反模式/迁移示例（G3），并在提交前经对抗审查（V）完成原文与事实抽查。

#### Scenario: 事实抽查

- **WHEN** 对抗审查随机抽取 10 条 facts.md 事实核对信源
- **THEN** 全部与登记信源一致，无虚构引证

## MODIFIED Requirements

无（本任务为全新增量；`think/index.md` 与 `bundles/index.md` 仅追加统计与导航行，属索引维护而非既有需求变更）。

## REMOVED Requirements

无。

## 开放问题

- 外/杂篇是否需补全全文逐字核对：本 spec 设定为"概述 + 精选"，若读者后续需要《外篇》《杂篇》全文解读，作为增量 bundle（如 `chuang-tzu-waipian`）扩展，不阻塞当前交付。
- 底本与异文冲突：若实现阶段发现双信源核对存在无法调和的异文冲突，在 facts.md 登记并列呈现，不作裁决。