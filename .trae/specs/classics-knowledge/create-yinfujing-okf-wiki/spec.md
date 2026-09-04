---
status: "draft"
name: create-yinfujing-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域经典《黄帝阴符经》原文与历代解读（道藏本、ctext.org、朱熹《阴符经考异》、王明《〈阴符经〉考》等公开学术资源），经 Web 信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（《黄帝阴符经》原文属公共领域古籍，解读为公开学术知识）
---

# 《黄帝阴符经》OKF 知识包教程 Spec

## Why

用户希望系统化获取《阴符经》**最权威、最真实**的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles`（最高可信度知识库）的恰当位置，生成可发布的 wiki 教程。《阴符经》托名黄帝、争议极大（成书年代、作者、文本版本均有分歧），"权威与真实"必须通过**双信源核对原文**与**诚实呈现托名层/文本层之分**来保证，而非沿用单一流行文本。

## What Changes

- 新增分组 `bundles/think/huangdi/`（黄帝经典分组，仿 `think/laozi/` 三层模式：域→组→束）
- 新增知识包 `bundles/think/huangdi/yinfujing/`：
  - `index.md`（bundle 根，快速导航 + 定位 + 学习路径）
  - `concepts/`（7 篇核心概念：什么是阴符经 / 版本源流 / 成书与作者之争 / 原文全录与分段 / 核心概念解读 / 历代注家立场 / 阴符经与道德经）
  - `examples/`（2 篇实操：上篇逐句精读、七日通读计划）
  - `references/`（3 篇信源登记：权威底本、注本分级表、交叉引用）
  - `facts.md` / `insights.md`（方法论文档闭环工作记录）
- 更新导航索引：`think/index.md`（新增分组行 + toctree）、`bundles/index.md`（统计数字 286→287、分组 32→33、think 域描述与分组表行）
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记，G1）→ I（洞察，G2）→ E（萃取 ≥2 个可复用阅读模式，G3）→ V（对抗审查：原文逐字双源核对）→ C（原子提交 + `invoke gates.all` 质量门）

**关键决策（落位）**：《阴符经》托名"黄帝"，故分组命名 `huangdi/`（与 `laozi/` 命名逻辑一致：人名→经典束），未来黄帝内经、黄帝四经等可归入同组。

**关键决策（底本）**：以**四百余字上中下三章本**（李筌注本系统、正统道藏通行本）为底本，同时呈现三百字本差异与传本源流，不采用网络常见未经核对的拼合文本。

## Impact

- Affected specs: `laozi-lineage-okf-bundle`、`boshu-laozi-wiki`（仅通过 references/cross-ref.md 交叉引用，不修改其产物）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增文件与两处索引更新；提交发生在子模块仓库内
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓文件

## ADDED Requirements

### Requirement: 权威原文忠实性

知识包 SHALL 提供《阴符经》原文全录（四百余字本全文 + 三百字本差异说明），且原文文字 SHALL 经至少两个独立权威信源逐字核对（如：正统道藏影印本、《中华道藏》整理本、ctext.org《陰符經》、四库全书本），每处关键异文在 facts.md 登记编号事实与信源 URL。

#### Scenario: 原文核对

- **WHEN** 读者对照任一权威底本核查 bundle 中的原文全录
- **THEN** 逐字一致（异文处显式标注"某本作某"并给出注家出处）

#### Scenario: 托名层与文本层区分

- **WHEN** 教程陈述"黄帝著"等传统托名说法
- **THEN** 显式标注其为托名传说，并列出学界主要成书年代学说（寇谦之说、李筌自著说、北朝末期说等）及依据（王明《〈阴符经〉考》等），不将托名当作史实陈述

### Requirement: 解读多元性与立场标注

知识包的解读 SHALL 覆盖多元注家传统并标注立场：六家注（太公、范蠡、鬼谷子、张良、诸葛亮、李筌）的兵机/丹道双线解读、朱熹《阴符经考异》、俞琰《阴符经发挥》、夏元鼎《阴符经讲义》等，以及现代注本分级（萧登福、任法融等）。每处引用注明注家与出处。

#### Scenario: 关键句多视角

- **WHEN** 读者阅读"观天之道，执天之行"等核心句解读
- **THEN** 至少呈现 2 种不同立场（如丹道解与兵机解）的注家观点并标注出处

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
