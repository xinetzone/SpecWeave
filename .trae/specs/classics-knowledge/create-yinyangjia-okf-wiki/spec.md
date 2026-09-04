---
status: "draft"
name: create-yinyangjia-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域古籍阴阳家文献（《汉书·艺文志》阴阳家著录、马国翰《玉函山房辑佚书》辑《邹子》/《邹子终始》、严可均辑文、《史记·孟子荀卿列传》、司马谈《论六家要旨》、《吕氏春秋·应同》、《管子》阴阳家相关篇、《礼记·月令》、《淮南子》相关篇、ctext.org 中国哲学书电子化计划、维基文库等公开学术资源），经双信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（先秦古籍原文属公共领域，解读为公开学术知识）
---

# 阴阳家 OKF 知识包教程 Spec

## Why

用户希望系统化调研"阴阳家相关的著作"——即以邹衍为代表的先秦阴阳家学派（《汉书·艺文志》九流十家之一）的经典文献——获取**最权威、最真实**的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles`（最高可信度知识库）的恰当位置，生成可发布的 wiki 教程。阴阳家是诸子百家中**文本亡佚最严重的学派**：《汉书·艺文志》著录阴阳家二十一家三百六十九篇（《邹子》四十九篇、《邹子终始》五十六篇、《邹奭子》十二篇等），**全部亡佚**，今存者仅为：①传世文献中的引述佚文（如《吕氏春秋·应同》《文选》李善注所引邹衍语）；②后世辑佚成果（马国翰《玉函山房辑佚书》等）；③公认受阴阳家影响或归属争议的传世篇章（《管子·四时/五行/幼官》、《礼记·月令》）。"权威与真实"必须通过**书志著录源流考证 + 辑佚残篇双信源逐字核对 + 「确证佚文/争议归属/受影响文献」三层诚实呈现**来保证，而非将托名文本或后世阴阳五行材料混作阴阳家原文。

## What Changes

- 新增分组 `bundles/think/yinyangjia/`（阴阳家经典分组，仿 `think/laozi/`、`think/psi/` 域→组→束三层模式）
- 新增知识包 `bundles/think/yinyangjia/yinyangjia/`：
  - `index.md`（bundle 根：快速导航 + 学派定位 + 学习路径 + 存佚总览）
  - `concepts/`（7 篇核心概念：什么是阴阳家 / 著作源流与存佚 / 邹衍生平与学说 / 五德终始说解读 / 传世文献中的阴阳家材料 / 辑佚史与历代考据 / 影响与流变）
  - `examples/`（2 篇实操：《吕氏春秋·应同》逐句精读、阴阳家文献通读计划）
  - `references/`（3 篇信源登记：权威底本与信源、辑佚本与现代研究分级表、交叉引用）
  - `facts.md` / `insights.md` / `log.md`（方法论文档闭环工作记录 + 更新历史）
- 更新导航索引：`think/index.md`（新增分组行 + toctree）、`bundles/index.md`（`total_bundles` 286→287、`groups` 32→33、think 域描述「5 束 · 2 组」→「6 束 · 3 组」、生态关系 mermaid 图中 think 节点标注与分组表行）
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记，G1）→ I（洞察，G2）→ E（萃取 ≥2 个可复用阅读模式，G3）→ V（对抗审查：佚文逐字双源核对 + 归属断言抽查）→ C（原子提交 + `invoke gates.all` 质量门）

**关键决策（落位）**：「阴阳家」是学派名（九流十家之一）而非单一人物/书名，故分组命名 `yinyangjia/`（拼音 kebab-case，与 `laozi/`、`guiguzi/` 命名逻辑一致）；首束命名为 `yinyangjia/`（阴阳家文献总束：书志著录 + 辑佚残篇 + 传世材料 + 解读谱系）；未来若新增专题束（如《礼记·月令》专束、邹衍佚文校注专束），归入同组。**落位基准**：当前 `bundles/index.md` 实际状态为 286 束 / 32 组 / 13 域、think「5 束 · 2 组」（`create-guiguzi-okf-wiki`、`create-mozi-okf-wiki`、`create-zhuangzi-okf-wiki` 等 spec 已建但尚未实施）；若其他 spec 先落地，实现阶段以实际统计数字为准同步调整。

**关键决策（底本与文本分层）**：以**《汉书·艺文志》书志著录**（点校本/ctext.org《汉书》）为著作源流基准；邹衍佚文以**马国翰《玉函山房辑佚书》辑《邹子》《邹子终始》**为核心辑佚底本（辅以严可均等辑本），并经 ctext.org 与维基文库双源逐字核对；传世文献（《史记·孟子荀卿列传》、司马谈《论六家要旨》、《吕氏春秋·应同》、《管子》相关篇、《礼记·月令》、《淮南子》相关篇）采用 ctext.org + 维基文库双源核对。所有文本材料按三层标注：**A 确证佚文**（辑佚书所录、注明原始出处）、**B 争议归属**（学界对归属有分歧，列双方依据）、**C 受影响传世文献**（公认体现阴阳家思想但非阴阳家著作），禁止将 B/C 层材料陈述为"阴阳家原文"。

## Impact

- Affected specs: `create-guiguzi-okf-wiki`、`create-mozi-okf-wiki`、`create-zhuangzi-okf-wiki`（同批未实施 spec，仅共享 think/ 域索引数字基准，无产物冲突）、`laozi-lineage-okf-bundle`、`create-yinfujing-okf-wiki`（仅通过 references/cross-ref.md 交叉引用，不修改其产物）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增文件与两处索引更新；提交发生在子模块仓库内，主仓 gitlink 变更需一并同步（如适用）
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓其他文件

## ADDED Requirements

### Requirement: 权威原文忠实性与存佚分层

知识包 SHALL 忠实呈现阴阳家文献的存佚现实：明确说明《汉书·艺文志》著录阴阳家二十一家三百六十九篇均已亡佚；所录原文 SHALL 限定为三类——A 确证佚文（辑佚书所录，注明辑本与原始引书出处，经至少两个独立权威信源逐字核对，如 ctext.org 与维基文库）、B 争议归属材料（显式列出归属分歧与各方依据）、C 受影响传世文献（如实标注"体现阴阳家思想，非阴阳家著作"），三层 SHALL 以显式标签区分，不得混用。每处关键异文在 facts.md 登记编号事实与信源 URL，异文处显式标注"某本作某"。

#### Scenario: 佚文核对

- **WHEN** 读者对照马国翰辑本或 ctext.org 核查 bundle 中的邹衍佚文
- **THEN** 逐字一致（异文处显式标注"某本作某"并给出辑本/引书出处）

#### Scenario: 存佚如实呈现

- **WHEN** 教程陈述阴阳家篇目结构
- **THEN** 明确区分「《汉书·艺文志》著录已亡佚的篇目（存目）」「今存辑佚残篇（注明字数规模与主要引书）」「传世文献中的相关材料（归属层级标注）」，不作任何构拟补全

### Requirement: 学派定位与人物史实的证据标注

知识包 SHALL 诚实呈现阴阳家的学派定位与邹衍事迹：司马谈《论六家要旨》与《汉书·艺文志》对阴阳家的评述原文全录（"阴阳家者流，盖出于羲和之官"等）；邹衍生平以《史记·孟子荀卿列传》记载为基准（"谈天衍"之称、大九州说、游学诸侯），并标注后世记载（如刘向《别录》、桓宽《盐铁论》相关条目）的证据层级；对"邹衍著《邹子》四十九篇"等传统说法，显式标注其为书志著录而非传世实证。

#### Scenario: 人物记载分层

- **WHEN** 读者阅读"邹衍生平"章节
- **THEN** 每项事迹标注史料出处（《史记》/《别录》/后世追述），直接史料与间接追述不混淆

### Requirement: 解读多元性与立场标注

知识包的解读 SHALL 覆盖多元传统并标注立场：古代评述（司马谈"序四时之大顺"、班固"拘于禁忌"等）；核心理论（阴阳消息、五德终始、大九州）的现代研究至少涵盖 2 种视角（如顾颉刚《五德终始说下的政治和历史》的疑古考证路径与冯友兰/吕思勉等通史路径对阴阳家地位的不同评估），各自标注文献出处，结论不武断。

#### Scenario: 关键学说多视角

- **WHEN** 读者阅读"五德终始说"解读
- **THEN** 呈现《吕氏春秋·应同》原始文本 + 至少 1 种古代评述 + 至少 2 种现代研究观点对照，并标注出处

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type: OKF`、`source`、`generated`/`verified`、`status`、`stale_after`，规范见 `projects/awesome-okf-xs/.agents/rules/frontmatter.md`）、bundle 根 index 以 `{toctree}` 引用全部内容文档、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

#### Scenario: 质量门通过

- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **THEN** toctrees 与 utf8 检查全部通过，无孤立文档、无断链

### Requirement: 方法论闭环（G1–G3 + V）

教程 SHALL 记录 seven-concepts 场景4 方法论痕迹：facts.md ≥30 条编号事实且无因果推断词（G1）、insights.md ≥3 条带四元组（陈述/证据/反常识/行动）洞察（G2）、≥2 个可复用阅读模式含触发场景/核心步骤/反模式/迁移示例（G3），并在提交前经对抗审查（V）完成佚文与归属断言抽查。

#### Scenario: 事实抽查

- **WHEN** 对抗审查随机抽取 10 条 facts.md 事实核对信源
- **THEN** 全部与登记信源一致，无虚构引证，B/C 层材料未被表述为 A 层

## MODIFIED Requirements

无（本任务为全新增量；`think/index.md` 与 `bundles/index.md` 仅追加统计与导航行，属索引维护而非既有需求变更；注意与同批未实施的 guiguzi/mozi/zhuangzi spec 共享索引数字基准，实现时以仓库实际状态为准）。

## REMOVED Requirements

无。

## 开放问题

- 无（底本与落位决策已在 spec 中给出；若实现阶段发现双信源核对存在无法调和的异文冲突，在 facts.md 登记并列呈现，不作裁决）
- 阴阳家与《周易》经传、与汉代阴阳五行谶纬之学的关系，属影响/交叉引用范畴，若篇幅过大可在实现阶段拆分为独立束并归入同组 `yinyangjia/`
