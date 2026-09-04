---
status: "draft"
name: create-kongzi-works-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域先秦古经《春秋》《诗经》《尚书》《仪礼》《周易》《论语》原文，及历代权威注疏（阮元《十三经注疏》、杨伯峻《论语译注》《春秋左传注》、程树德《论语集释》、高亨《周易古经今注》、程俊英《诗经注析》等公开学术资源），经双信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（《春秋》等先秦古经原文属公共领域，解读为公开学术知识）
---

# 孔子相关著作 OKF 知识包教程 Spec

## Why

用户希望全面调研「孔子本人相关的著作」，获取**最权威、最真实**的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles`（最高可信度知识库）的恰当位置，生成可发布的 wiki 教程。孔子「述而不作，信而好古」（《论语·述而》），学界共识是：**亲撰仅《春秋》一部**；《诗》《书》《礼》《易》是孔子整理/传授，《乐》已亡佚；《论语》是弟子及再传弟子辑录。因此「最真实」的核心在于**诚实呈现每部著作的归属层级**（亲作/整理/辑录/存疑），而非沿用「孔子著六经」的俗说。

## What Changes

- 新增分组 `bundles/think/confucius/`（孔子分组，仿 `think/laozi/`、`think/huangdi/` 三层模式：域→组→束）
- 新增知识包 `bundles/think/confucius/works/`：
  - `index.md`（bundle 根，快速导航 + 归属矩阵 + 学习路径）
  - `concepts/`（9 篇核心概念，见下）
  - `examples/`（3 篇精读示例）
  - `references/`（3 篇信源登记）
  - `facts.md` / `insights.md` / `log.md`（方法论文档闭环工作记录）
- 更新导航索引：`think/index.md`（新增分组行 + toctree）、`bundles/index.md`（统计数字与 think 域描述/分组表行）
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记，G1）→ I（洞察，G2）→ E（萃取 ≥2 个可复用阅读模式，G3）→ V（对抗审查：原文逐字双源核对）→ C（原子提交 + `invoke gates.all` 质量门）

**关键决策（落位）**：孔子为核心人名，分组命名 `confucius/`（与 `laozi/`、`huangdi/` 命名逻辑一致：人名→经典束），未来《孝经》、孔子家语、论语出土本等可归入同组。

**关键决策（范围）**：全面覆盖孔子相关著作，逐部诚实标注归属——
- 亲作：《春秋》（传统说，现代有辨伪争议）
- 整理/传授：《诗》《书》《礼》《乐》（乐已亡佚，仅存目）、《易》（《易传》十翼归属存疑）
- 弟子辑录：《论语》（非孔子手写，但为最直接言行记录）

**关键决策（原文深度）**：采纳「精选原文 + 权威解读」——每部著作选录最具代表性原文段落（附权威校注底本与今译），不全文照录（《论语》约 1.6 万字、《春秋》约 1.6 万字、《诗经》305 篇体量过大），全文以权威底本引用指引（ctext.org 等）供查证。

## Impact

- Affected specs: `laozi-lineage-okf-bundle`、`boshu-laozi-wiki`、`create-yinfujing-okf-wiki`（仅通过 references/cross-ref 交叉引用与 think 域描述更新，不修改其产物）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增文件与 `think/index.md`、`bundles/index.md` 两处索引更新；提交发生在子模块仓库内
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓文件

## ADDED Requirements

### Requirement: 归属层级忠实性（最真实）

知识包 SHALL 对每部孔子相关著作标注明确的归属层级（亲作/整理传授/弟子辑录/存疑），并将「述而不作」作为总纲显式呈现；凡传统「孔子著六经」等俗说 SHALL 显式标注为传统说法，并列出现代辨伪/考古学依据，不将托名当作史实陈述。

#### Scenario: 归属矩阵可查

- **WHEN** 读者查看 bundle 根 index 的归属矩阵表
- **THEN** 每部著作（春秋/诗/书/礼/乐/易/论语）的归属层级、传统说、现代争议、考古依据逐列清晰，且均有 facts.md 编号事实与信源支撑

#### Scenario: 易传归属不夸大

- **WHEN** 教程陈述《易传》十翼（文言/彖/象/系辞等）的归属
- **THEN** 显式标注其为「托名孔子、归属存疑」（宋代欧阳修《易童子问》已质疑），列出战国至汉代成书的主流学说，不称「孔子作十翼」

### Requirement: 权威原文忠实性

知识包 SHALL 提供各部著作的代表性原文选录，原文文字 SHALL 经至少两个独立权威信源逐字核对（阮元《十三经注疏》、杨伯峻《论语译注》/《春秋左传注》、ctext.org 中国哲学书电子化计划、中华书局点校本），每处关键异文在 facts.md 登记编号事实与信源。全文未照录处 SHALL 给出权威底本引用指引。

#### Scenario: 选录原文核对

- **WHEN** 读者对照任一权威底本核查选录原文
- **THEN** 逐字一致（异文处显式标注「某本作某」并给出出处）

### Requirement: 解读多元性与立场标注

知识包的解读 SHALL 覆盖多元注家传统并标注立场：汉代今古文经学之争、郑玄/孔颖达注疏、朱熹《诗集传》《四书章句集注》、现代注本（杨伯峻、高亨、程俊英等），以及出土文献（定州汉简《论语》、郭店/上博/清华简）带来的文本校正。每处引用注明注家与出处。

#### Scenario: 关键句多视角

- **WHEN** 读者阅读「《春秋》笔法」或《论语》核心章句解读
- **THEN** 至少呈现 2 种不同立场（如《左传》记事解与《公羊》《穀梁》义理解）的注家观点并标注出处

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type`、`source`、`generated`/`verified`、`status`）、bundle 根 index 以 `{toctree}` 引用全部内容文档、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

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

- 无（落位、范围、原文深度、底本决策已在 spec 中给出；若实现阶段发现双信源核对存在无法调和的异文冲突，在 facts.md 登记并列呈现，不作仲裁）