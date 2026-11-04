---
status: "draft"
name: laozi-culture-ecosystem-okf-wiki-spec
version: 1.0.0
created: 2026-10-31
source: "帛书《老子》（马王堆出土，公共领域） + projects/awesome-okf-xs/doc/bundles/sheke/markets/efficient-markets（现有知识包）"
methodology: "seven-concepts-cmd 场景4（知识沉淀）R→I→E→V→C"
content-sensitivity: "Public（帛书老子属公共领域；商业机制为通识理论）"
---

# 《老子文化生态圈》OKF Wiki 教程 Spec

## Why

用户希望围绕「老子文化」打造一个可自我维持的**文化生态圈**：以「流量变现／渠道变现／利他现金流」三条现金流为骨架，形成**多形态商业圈 + 现金流闭环**的「现金流有效场域」，并要求「尽可能符合**帛书**老子的思想」。

现状与缺口：

- `projects/awesome-okf-xs/doc/bundles/guoxue/laozi/` 分组现有 4 束（boshu-reading 阅读教程、laozi-works 原文与解读、laozi-lineage 传本源流、dao-san-triads 三元组探究），**均为文献学/哲学向，尚无一束把老子思想落到商业生态与现金流的经营机制上**。
- `sheke/markets/efficient-markets`（今日交付，78 条事实/30 信源）已把「价格发现与信息入价、套利与均衡、市场失灵、有效市场假说 EMH、行为金融与适应性市场 AMH」系统化，可作为「现金流有效场域」的**机制层理论支柱**，但尚无知识包把它与东方经营哲学对接。

目标：产出一套符合 SpecWeave / awesome-okf-xs 规范的原子化 OKF 知识包，用**理论与算例双轨**的方式，把「老子文化生态圈 → 多形态商业圈 → 现金流闭环」讲清，并以**帛书用字为准**锚定老子思想，逐条交叉引用 efficient-markets 的机制页，全程守住合规边界（不荐具体平台/项目、不承诺收益、不构成经营或投资建议）。

## What Changes

- **新增知识包目录**：`projects/awesome-okf-xs/doc/bundles/guoxue/laozi/laozi-culture-ecosystem/`，采用标准三层结构（`concepts/` + `examples/` + `references/`）+ 根工作文档（`index.md` / `facts.md` / `insights.md` / `log.md`）。
- **理论轨（concepts/，10 篇）**：文化生态圈定义 → 帛书老子经营哲学基线 → 流量变现 → 渠道变现 → 利他现金流 → 现金流有效场域 → 多形态商业圈与闭环条件 → 效率边界与市场失灵 → 与 EMH/AMH 的对话 → 治理与合规边界。
- **算例轨（examples/，4 篇）**：渠道分成与场地费现金流算例、流量漏斗与 LTV/CAC 算例、利他现金流的「先予后取」时间结构算例、生态圈闭环四维对照卡与自查清单。
- **信源先行（references/，2 篇）**：双体系信源索引（帛书老子文本与学术信源 + 市场机制与商业通识信源）+ P0 核验记录（含口径留痕与放弃核验清单）。
- **事实与洞察留痕**：`facts.md` 独立采集 F 编号事实（不复制 efficient-markets 编号，仅交叉引用其概念页）；`insights.md` 收录四元组洞察。
- **索引同步（3 处）**：`bundles/index.md`（total_bundles 695→696、guoxue 49→50、laozi 行 4→5、mermaid guoxue 节点数字）、`guoxue/index.md`（laozi 行简介）、`guoxue/laozi/index.md`（新增行 + toctree），并同步 `doc/index.md` / `README.md` 中的规模数字（以 `invoke gates.assetbaseline` 口径为准）。
- **不修改**基本面：不修改 efficient-markets 任何文件，不修改老子分组既有 4 束的内容（仅追加索引行）。

## Impact

- Affected specs / capabilities：OKF 知识包库（`doc/bundles/`）；「老子」分组知识面；跨域引用收敛（guoxue ↔ sheke/markets）。
- Affected code / systems：无代码变更。仅新增 23 个 Markdown 文档（7 根 + 10 concepts + 4 examples + 2 references，含 3 个 `index.md`），并同步 4~5 处索引文件的计数与简介。
- 门禁影响：新增束后必须运行 `invoke gates.toctrees`（toctree 完整性）与 `invoke gates.bundles`（束/组/域三角对账）、`invoke gates.assetbaseline`（规模数字三处一致）；本仓为 git submodule，提交走子模块流程，**默认不 push**。

## ADDED Requirements

### Requirement: 老子文化生态圈知识包本体

系统 SHALL 在 `doc/bundles/guoxue/laozi/laozi-culture-ecosystem/` 提供一套原子化 OKF 知识包，用理论与算例双轨讲清「老子文化生态圈 → 多形态商业圈 → 现金流闭环」，并以帛书老子思想为价值基线。

#### Scenario: 读者完成一次主题阅读

- **WHEN** 读者从根 `index.md` 进入知识包
- **THEN** 能通过 `concepts/index.md` / `examples/index.md` / `references/index.md` 导航到任一篇章，所有 Markdown 相对链接可达、零断链
- **AND** 根 `index.md` 的 `{toctree}` 收录全部子文档，`invoke gates.toctrees` 通过

#### Scenario: 帛书思想锚定

- **WHEN** 文档陈述老子思想（无为、自然、不争、上善若水、反者道之动、损有余而补不足、既以为人己愈有等）
- **THEN** 关键用字与章序**以帛书甲乙本为准**（如帛书「有静」而非通行本「不争」的用字差异须显式标注），凡帛书与通行本有异者并列呈现，不混称
- **AND** 引用老子原文属公共领域，frontmatter 以 `source` 标注来源

### Requirement: 双轨结构（理论 + 算例）

系统 SHALL 同时提供理论轨（concepts/）与算例轨（examples/），算例均为**可复算**的教学材料。

#### Scenario: 算例可复算

- **WHEN** 读者按算例给定的假设（分成比例、获客成本、留存率、贴现率等）逐步计算
- **THEN** 能得到与文档一致的现金流/净现值/回收期结果
- **AND** 每个算例数字均标注「教学算例」，假设显式列出，不暗示真实收益

### Requirement: 与 efficient-markets 的深度耦合

系统 SHALL 在机制层逐条交叉引用 `sheke/markets/efficient-markets` 的概念页（价格发现与信息入价、套利与均衡、市场失灵、EMH 三形态、随机游走与理性预期、行为金融与 AMH），作为「现金流有效场域」的理论支柱。

#### Scenario: 跨包引用可达

- **WHEN** 本包引用 efficient-markets 的概念页
- **THEN** 使用相对路径链接到 `../../../../sheke/markets/efficient-markets/concepts/...`，链接可达
- **AND** 不复制其 F 编号事实，本包 `facts.md` 独立编号（F-001 起）

### Requirement: 事实溯源与信源分级

系统 SHALL 在 `facts.md` 提供编号事实清单（编号连续无跳号），每条事实挂信源编号（S 编号），并在 `references/` 提供信源索引与核验记录。

#### Scenario: 事实可核验

- **WHEN** 读者核对任一具体声明
- **THEN** 能在 `facts.md` 找到对应 F 编号，并在 `references/01-sources.md` 找到 S 编号对应的信源
- **AND** 数字类/制度类事实经 P0 核验，核验结论写入 `references/02-verification.md`，并登记放弃核验清单与口径差异

### Requirement: 合规与边界声明

系统 SHALL 显式声明边界：本包为**通识教育材料**，不推荐任何平台/项目/产品，不承诺收益，不预测市场，不构成经营、投资、法律或财税建议。

#### Scenario: 边界可见

- **WHEN** 读者阅读根 `index.md` 与本包任一章
- **THEN** 能读到「不荐产品、不承诺收益、不构成建议」的立场声明
- **AND** 全文无鼓励性收益承诺、无「保证赚钱/稳赚」类表述

### Requirement: OKF 元数据与索引完整性

新增文件 SHALL 遵循 OKF v0.2 frontmatter 规范（根 `type: OKF` + `okf_version` + `version` + `sources` + `generated` + `status` + `stale_after`；子文档 `type: Concept/Example/Reference/Facts/Insights`，`source` 标注来源）。

#### Scenario: 计数对账通过

- **WHEN** 运行 `invoke gates.bundles`
- **THEN** `bundles/index.md` frontmatter（695→696）、计数行、域节标题、分组表束数列、toctree 五面与目录树一致（guoxue 49→50、laozi 4→5）
- **AND** `invoke gates.assetbaseline` 通过（规模数字三处一致、行尾归一）

## MODIFIED Requirements

### Requirement: 老子分组（guoxue/laozi）知识包索引

`guoxue/laozi/index.md` SHALL 在知识包列表新增 `laozi-culture-ecosystem/` 行，并在 `{toctree}` 追加对应条目；`guoxue/index.md` 的「老子」行简介 SHALL 增补「文化生态圈·现金流闭环」定位；`bundles/index.md` 的总束数与本分组束数 SHALL 同步 +1。

## REMOVED Requirements

无（本任务为全新增量，不删除任何既有需求）。

## 开放问题

- 无（归属路径、内容定位、耦合深度、敏感度四项已与用户确认）。
- 待实施阶段确认项：`doc/index.md` 与 `README.md` 中规模数字的确切出现位置与口径，以 `invoke gates.assetbaseline` 输出为准。
