---
status: "draft"
name: create-legalism-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域法家经典（《韩非子》《商君书》《管子》《慎子》《申子》辑佚）原文与历代校注解读（王先慎《韩非子集解》、陈奇猷《韩非子新校注》、蒋礼鸿《商君书锥指》、黎翔凤《管子校注》、钱熙祚守山阁本《慎子》、严可均辑申子佚文、ctext.org 全文等公开学术资源），经 Web 信源核对后整理"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（先秦法家古籍原文属公共领域，历代校注与现代解读为公开学术知识）
---

# 法家经典 OKF 知识包教程 Spec

## Why

用户希望系统化获取法家相关著作的**最权威、最真实**的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles`（最高可信度知识库）的恰当位置，生成可发布的 wiki 教程。法家文献存在三个必须诚实处理的"真实性问题"：其一，**托名与结集**——《管子》非管仲所作而为稷下学派文集、《商君书》多为商鞅后学与秦国官文书结集、《申子》大部散佚仅存辑佚；其二，**真伪篇章**——《韩非子》中《初见秦》《存韩》等篇的作者归属存在争议；其三，**学派边界**——《管子》兼含儒道阴阳成分，《尹文子》或属名家。"权威与真实"必须通过**双信源逐字核对原文**与**显式的作者/文本分层标注**来保证，而非沿用单一流行文本或将托名当史实。

## What Changes

- 新增分组 `bundles/think/legalism/`（法家经典分组，仿 `think/laozi/` 域→组→束三层模式），含分组 `index.md`
- 新增 4 个知识包（bundle 根目录用纯英文 kebab-case，正文与标题用中文书名）：
  - `think/legalism/han-fei-tzu/`（《韩非子》——法家集大成者，旗舰知识包）：`index.md` + `concepts/`（8 篇）+ `examples/`（3 篇）+ `references/`（3 篇）
  - `think/legalism/shang-jun-shu/`（《商君书》）：`index.md` + `concepts/`（5 篇）+ `examples/`（2 篇）+ `references/`（2 篇）
  - `think/legalism/guan-tzu/`（《管子》）：`index.md` + `concepts/`（5 篇）+ `examples/`（2 篇）+ `references/`（2 篇）
  - `think/legalism/early-legalists/`（早期法家辑佚——申不害·慎到及法家源流）：`index.md` + `concepts/`（4 篇）+ `examples/`（2 篇）+ `references/`（2 篇）
- 更新导航索引：`think/index.md`（新增分组行 + toctree + 域描述）、`bundles/index.md`（total_bundles 286→290、groups 32→33、think 域行 5 束 2 组→9 束 3 组、生态关系图与推荐路径中的 think 标签）
- 遵循 seven-concepts 场景4 链路：R（信源采集与事实登记，G1）→ I（洞察，G2）→ E（萃取 ≥2 个可复用阅读模式，G3）→ V（对抗审查：原文逐字双源核对抽查）→ C（原子提交 + `invoke gates.all` 质量门）

**关键决策（落位与命名）**：法家为学派而非单人，故分组名取学派通用英文名 `legalism/`（与 `laozi/`（人名）、`psi/`（理论体系）并列）；bundle 命名规则——人名托名经典用通用英文转写（`han-fei-tzu`、`guan-tzu`），书名直接用拼音（`shang-jun-shu`），跨文献辑佚用描述性名称（`early-legalists`）。未来法家衍生专题（如《韩非子》单篇深读、法家西传研究）可归入同组。

**关键决策（底本与文本分层）**：
- 《韩非子》：以王先慎《韩非子集解》（中华书局新编诸子集成本）与陈奇猷《韩非子新校注》为主要校本，ctext.org《韓非子》全文为数字对校本；核心篇目（《五蠹》《孤愤》《说难》《定法》《难势》《显学》《二柄》《奸劫弑臣》）作**全文双源逐字核对**，其余 47 篇作结构概述与归属说明；《初见秦》《存韩》等争议篇显式标注学界归属学说。
- 《商君书》：以蒋礼鸿《商君书锥指》为校本；精选《更法》《垦令》《开塞》《壹言》《赏刑》《画策》《慎法》作全文核对，其余各篇概述；全书标注"非商鞅手著、多为后学与官文书结集"属性。
- 《管子》：以黎翔凤《管子校注》为校本；精选《牧民》《形势》《权修》《立政》《任法》《法法》作全文核对，其余概述；全书标注"托名管仲、稷下学派混合文集（法家为主兼儒道阴阳）"属性，不将《管子》全部内容等同于管仲或纯粹法家思想。
- 《申子》《慎子》：申不害文大部散佚，以严可均《全上古三代秦汉三国六朝文》及《意林》等辑佚材料为本；慎到以钱熙祚守山阁丛书辑本（残七篇）为本；均显式标注"辑佚残篇"属性，佚文逐条给出辑佚出处。

**关键决策（篇幅边界）**：法家存世文献总量逾二十万字，全篇逐字双源核对属超大规模任务。本 spec 以"法家核心经典的核心篇目"为边界：四部文献合计约 22 篇全文逐字核对 + 其余结构化概述，兼顾"最真实原文"与工程可行性；如用户后续要求补全，作为增量 bundle 扩展。

## Impact

- Affected specs: `create-zhuangzi-okf-wiki`、`boshu-laozi-wiki`、`laozi-lineage-okf-bundle`（仅通过 references 交叉引用，不修改其产物；zhuangzi 尚未实施，不产生实际依赖）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增文件与两处索引更新；提交发生在子模块仓库内，主仓仅新增本 spec 目录
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓其他文件

## ADDED Requirements

### Requirement: 权威原文忠实性

知识包 SHALL 提供核心篇目全文（其余篇目结构概述），且原文文字 SHALL 经至少两个独立权威信源逐字核对（校本：新编诸子集成本各校注本；数字对校本：ctext.org 对应文献全文），每处关键异文在 facts 文件登记编号事实与信源 URL。

#### Scenario: 原文核对

- **WHEN** 读者对照任一权威底本核查 bundle 中的核心篇目全文与精选段落
- **THEN** 逐字一致（异文处显式标注"某本作某"并给出校本出处）

#### Scenario: 辑佚文标注

- **WHEN** 教程呈现《申子》《慎子》佚文
- **THEN** 每条佚文标注辑佚来源（如《意林》《群书治要》、严可均辑本），不将后人辑佚文本伪装成传世完本

### Requirement: 文本真伪与归属的诚实分层

知识包 SHALL 显式区分作品层：托名层（《管子》托名管仲、《商君书》托名商鞅）、结集层（稷下学者/商鞅后学/秦国官文书）、亲著层（《韩非子》主体篇目归于韩非）、辑佚层（申、慎残篇）、争议层（《韩非子·初见秦》《存韩》等归属有争的篇目）。不将传统托名当作史实陈述，并列出学界主要归属学说。

#### Scenario: 争议篇处理

- **WHEN** 教程陈述《初见秦》《存韩》等争议篇的作者
- **THEN** 并列呈现主要学说（如"韩非作""非韩非作""部分为李斯文"）及其文献学依据，不作单方面裁决

#### Scenario: 托名书处理

- **WHEN** 教程介绍《管子》《商君书》
- **THEN** 明确其成书性质（稷下文集/后学结集）与学界共识，同时说明其作为法家（或法家为主）思想史料的价值不受托名影响

### Requirement: 解读多元性与立场标注

知识包的解读 SHALL 覆盖多元传统并标注立场：古注与近世校勘（王先慎、孙诒让札迻、蒋礼鸿、黎翔凤、陈奇猷等）、现代学术（冯友兰、梁启超、萧公权、郭沫若《十批判书》、侯外庐等）、西方汉学（如 Burton Watson 译本、Yuri Pines《The Book of Lord Shang》译注与法家研究）。每处引用注明注家/学者与出处；核心句解读至少呈现 2 种立场。

#### Scenario: 核心句多视角

- **WHEN** 读者阅读"法不阿贵，绳不挠曲""刑无等级""利之所在民归之"等核心命题的解读
- **THEN** 至少呈现 2 种不同立场（如古注训诂与现代批判史观、或同情式解读与"以法为教"的反思性评价）并标注出处

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type`、`title`、`sources`、`status` 等，规范见 `projects/awesome-okf-xs/.agents/rules/frontmatter.md`）、bundle 根 `index.md` 以 `{toctree}` 引用全部内容文档、分组 `index.md` 引用全部 bundle、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

#### Scenario: 质量门通过

- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **THEN** toctrees 与 utf8 检查全部通过，无孤立文档、无断链

#### Scenario: 索引统计一致

- **WHEN** 检查 `bundles/index.md` 的 `total_bundles`/`groups`/`domains` 与 think 域行、`think/index.md` 的分组表
- **THEN** 统计数字与实际新增（4 束、1 组）一致，toctree 条目齐全

### Requirement: 方法论闭环（G1–G3 + V）

教程 SHALL 记录 seven-concepts 场景4 方法论痕迹：facts 文件合计 ≥50 条编号事实且无因果推断词（G1，分布于 `.trae/specs/classics-knowledge/create-legalism-okf-wiki/facts-*.md`，其中《韩非子》≥20 条、其余每部 ≥10 条）、insights ≥4 条带四元组洞察（G2）、≥2 个可复用阅读模式含触发场景/核心步骤/反模式/迁移示例（G3），并在提交前经对抗审查（V）完成原文与事实抽查。

#### Scenario: 事实抽查

- **WHEN** 对抗审查随机抽取 10 条 facts 事实核对信源
- **THEN** 全部与登记信源一致，无虚构引证

## MODIFIED Requirements

无（本任务为全新增量；`think/index.md` 与 `bundles/index.md` 仅追加统计与导航行，属索引维护而非既有需求变更）。

## REMOVED Requirements

无。

## 开放问题

- 《尹文子》《邓析子》等法家边缘文献：学界归属存争（多列为名家或稷下杂家），本 spec 将其置于 `early-legalists` 的概念文档中作源流式介绍而非全文核对，若用户需要可作增量扩展。
- 异文冲突：若实现阶段发现双信源核对存在无法调和的异文冲突，在 facts 文件登记并列呈现，不作裁决。
- zhuangzi bundle（另一未实施 spec）若先行落地，`bundles/index.md` 统计数字需叠加调整，属索引维护，不构成本 spec 阻塞。
