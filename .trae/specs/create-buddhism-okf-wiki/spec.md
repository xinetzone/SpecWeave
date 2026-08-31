---
name: create-buddhism-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域佛家核心经典原文与历代解读（《大正藏》T08/T09/T12 系统、玄奘译《心经》、鸠摩罗什译《金刚经》《阿弥陀经》《法华经》、《六祖坛经》敦煌本/宗宝本、ctext.org 等公开学术资源），经 Web 信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（佛家经典汉译本原文属公共领域古籍，解读为公开学术知识）
---

# 佛家核心经典 OKF 知识包教程 Spec

## Why

用户希望系统化获取佛家核心经典**最权威、最真实**的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles`（最高可信度知识库）的恰当位置。佛家经典与《阴符经》《老子》有一处本质差异：**汉传佛经的「原文」本身已是梵文/巴利文原典的汉语译本**（梵文原典大多散佚），因此「权威与真实」必须通过**标注译本系统（译者/时代）**、**以权威译本校订本（《大正藏》）为底本**、**诚实呈现翻译差异与宗派立场**来保证，而非宣称存在唯一的「原始原文」。

## What Changes

- 新增分组 `bundles/think/buddhism/`（佛家核心经典分组，仿 `think/laozi/` 三级模式：域→组→束）。
- 新增 5 个知识包（bundle），每个遵循「concepts / examples / references + facts / insights / log」三层结构：
  1. `heart-sutra/`（《般若波罗蜜多心经》，玄奘译 260 字）
  2. `diamond-sutra/`（《金刚般若波罗蜜经》，鸠摩罗什译）
  3. `platform-sutra/`（《六祖坛经》，唯一称「经」的中国祖师著作）
  4. `amitabha-sutra/`（《佛说阿弥陀经》，鸠摩罗什译，净土宗核心）
  5. `lotus-sutra/`（《妙法莲华经》选读，鸠摩罗什译，大部经导读）
- 更新导航索引：`think/index.md`（新增分组行 + toctree）、`bundles/index.md`（统计数字 286→291、分组 32→33、think 域描述与分组表行）。
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记，G1）→ I（洞察，G2）→ E（萃取 ≥2 个可复用阅读模式，G3）→ V（对抗审查：原文/译本双源逐字核对）→ C（原子提交 + `invoke gates.all` 质量门）。

**关键决策（落位）**：佛家经典落位 `think/buddhism/` 分组（与 `think/laozi/`、`think/psi/` 平级）。bundle 英文命名采用通行法名 kebab-case。

**关键决策（大部经选读）**：第 5 个 bundle 默认做《妙法莲华经》选读（鸠摩罗什译本，分 28 品约 8 万字，不全文照录，改为「结构总览 + 核心品精读 + 关键偈颂 + 选读计划」），《华严经》与《楞严经》等作为 `references/` 交叉引用条目登记，留待未来扩展。

**关键决策（底本体系）**：以《大正新修大藏经》（CBETA 电子佛典）为底本基准，每部经显式标注核心译者与译经年代（玄奘译《心经》、鸠摩罗什译《金刚经》《阿弥陀经》《法华经》），并区分「梵文/巴利文原典是否存世」。原文全录须至少经两个独立信源逐字核对（《大正藏》卷次页次 + ctext.org 等电子本）。

## Impact

- Affected specs: `create-yinfujing-okf-wiki`、`laozi-lineage-okf-bundle`、`boshu-laozi-wiki`（同属 `think/` 思想域，仅通过分组导航并列，不修改其产物）。
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增文件与两处索引更新；提交发生在子模块仓库内。
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓文件。

## ADDED Requirements

### Requirement: 译本系统与底本标注

知识包 SHALL 为每部经典标注译者、译经年代、所属藏经卷次，并显式说明「梵文/巴利文原典是否存世、通行汉语译本为何者」。原文文字 SHALL 经至少两个独立权威信源逐字核对（《大正藏》卷次 + 电子本），每处关键异文/异译在 facts.md 登记编号事实与信源。

#### Scenario: 译本区分

- **WHEN** 读者阅读「观自在菩萨行深般若波罗蜜多时」等原文
- **THEN** 教程显式标注此为玄奘译本（《大正藏》T08 No.251），并说明与鸠摩罗什译本的差异（如「照见五蕴皆空」与「照见五阴皆空」）

#### Scenario: 原文核对

- **WHEN** 读者对照《大正藏》卷次页次核查 bundle 中的原文全录
- **THEN** 逐字一致；异文处显式标注「某本作某」并给出信源

### Requirement: 解读多元性与宗派立场标注

知识包的解读 SHALL 覆盖多元注家传统并标注宗派立场：般若系（心经/金刚经）呈现中观空性、禅宗顿悟、唯识等不同立场；《坛经》区分敦煌本与宗宝本、标注禅宗史立场；《阿弥陀经》标注净土宗「称名往生」立场；每处引用注明注家与出处（如窥基《心经幽赞》、憨山《金刚决疑》、印顺《金刚经讲记》等）。

#### Scenario: 关键句多视角

- **WHEN** 读者阅读核心句解读（如「色不异空，空不异色」）
- **THEN** 至少呈现 2 种不同立场（中观空性与唯识/禅宗）的注家观点并标注出处

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type: OKF`、`sources` 溯源字段、`generated`/`verified`、`status`、`stale_after`，规范见 `.agents/rules/frontmatter.md`）、bundle 根 index 以 `{toctree}` 引用全部内容文档、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

#### Scenario: 质量门通过

- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **THEN** toctrees 与 utf8 检查全部通过，无孤立文档、无断链

### Requirement: 方法论闭环（G1–G3 + V）

每个 bundle SHALL 记录 seven-concepts 场景4 方法论痕迹：facts.md ≥25 条编号事实且无因果推断词（G1）、insights.md ≥3 条带四元组洞察（G2）、≥2 个可复用阅读模式含触发场景/核心步骤/反模式/迁移示例（G3），并在提交前经对抗审查（V）完成原文与事实抽查。

#### Scenario: 事实抽查

- **WHEN** 对抗审查随机抽取每 bundle 10 条 facts.md 事实核对信源
- **THEN** 全部与登记信源一致，无虚构引证

## MODIFIED Requirements

无（本任务为全新增量；`think/index.md` 与 `bundles/index.md` 仅追加统计与导航行，属索引维护而非既有需求变更）。

## REMOVED Requirements

无。

## 开放问题

- 大部经选读以《法华经》为默认，若实现阶段确认需以《华严经》替代或并列，在 `references/` 交叉引用中登记并顺延（不阻塞本交付）。
- 若实现阶段发现某部经典双信源核对存在无法调和的文字差异，在 facts.md 登记并列呈现，不作裁决。