---
type: Spec
title: 《浮生六记》OKF wiki 教程知识包
created: 2026-08-30
status: draft
---

# Spec：《浮生六记》OKF wiki 教程知识包

## 1. 问题背景（Problem）

用户要求：全面系统地调研和整理清代沈复《浮生六记》的著作原文与解读资料，并在 `projects/awesome-okf-xs/doc/bundles` 的恰当位置生成 OKF wiki 教程。

现状：
- awesome-okf-xs 知识库现有 286 个知识包，全部为技术/开源项目教程；`think/`（思想与理论）域下仅有 `psi/`（自指递归理论）与 `laozi/`（老子，含 `boshu-reading` 古典典籍阅读教程 bundle）两组。
- `think/laozi/boshu-reading` 已验证"古典典籍阅读教程"bundle 范式（facts.md / insights.md / concepts/ / examples/ / references/ + toctree），但知识库中尚无中国古典文学（散文/小品/自传文学）方向的知识包。
- 《浮生六记》是清代自传体散文经典，涉及作者生平、六记结构、版本流传、1935 年"足本"伪书公案、2005 年卷五佚文发现、林语堂英译传播等丰富内容，普通读者缺乏一份"怎么读、读哪个版本、伪书怎么辨"的系统中文指南。

## 2. 用户与使用场景（Users）

- **主要用户**：想读或正在读《浮生六记》的中文普通读者（零基础到进阶）。
- **次要用户**：古典文学爱好者、OKF 知识库的 AI 智能体消费者（需要可信、可溯源的事实与结构化解读）。
- **典型场景**：
  1. 零基础读者想知道这本书讲什么、值不值得读、从哪个版本入手；
  2. 读者遇到"足本/伪两记/中山记历/养生记逍"等版本问题需要辨别；
  3. 读者想深入理解芸娘形象、闲情美学、自传文学地位；
  4. 读者想按图索骥找到原典、注本、研究文献与译本。

## 3. 目标（Goals）

- G1：在 awesome-okf-xs 中新增一个结构完整、符合 OKF v0.2 规范的《浮生六记》阅读教程 bundle，范式对齐 `think/laozi/boshu-reading`。
- G2：内容覆盖"著作原文导读 + 版本源流 + 伪书考辨 + 佚文发现 + 人物与主题解读 + 注本/译本/研究信源"六大板块，事实可溯源、零臆造。
- G3：按 seven-concepts-cmd 知识沉淀链路（R 事实采集 → I 洞察 → E 萃取 → V 对抗审查）组织内容，产物映射到 OKF 三层结构（facts/insights → concepts/examples/references）。
- G4：知识库导航完整：新 bundle 被 think 域索引与 bundles 总索引正确登记，toctree 无断链、无孤立文档。

## 4. 非目标（Non-goals）

- 不做《浮生六记》全文原文收录（公有领域文本，仅做片段精读与外部全文源指引）。
- 不做学术专著级别的 exhaustive 文献综述（定位为读者向教程，研究文献作信源登记与导读）。
- 不修改 awesome-okf-xs 的 Sphinx 配置、CI 脚本或 OKF 规范本体。
- 不执行 git commit / push（用户未要求提交；子模块内变更留待用户自行提交）。
- 不为伪两记（中山记历/养生记逍）做"正面导读"，仅作辨伪教学与版本学案例。

## 5. 存放位置决策

- 路径：`doc/bundles/think/classics/fusheng-liuji-reading/`
- 理由：
  1. `think/` 域已承载"经典思想著作阅读"（laozi 组先例），《浮生六记》以生活美学与人生哲学为核，归入 think 域符合域描述"经典思想著作的知识沉淀"；
  2. 新建 `classics/`（经典阅读）分组而非直接以书名建组，为后续古典文学 bundle（如《陶庵梦忆》《闲情偶寄》等）预留扩展位；
  3. bundle 名 `fusheng-liuji-reading` 与 `boshu-reading` 命名范式一致（作品-reading 教程定位）。

## 6. 功能需求（Functional Requirements）

### FR-1 Bundle 结构（对齐 boshu-reading 范式）

```
think/classics/fusheng-liuji-reading/
├── index.md              # bundle 根：frontmatter(type: OKF) + 导航 + 快速开始 + 学习路径 + toctree
├── facts.md              # R 阶段产物：零推测事实清单（F-xxx 编号，≥40 条）
├── insights.md           # I 阶段产物：四元组洞察（≥4 条）+ 知识地图 + 学习路径
├── log.md                # 创建/更新日志
├── concepts/             # E 阶段产物：概念文档 7 篇 + index.md(toctree)
│   ├── 00-why-read.md            # 为什么读《浮生六记》：阅读价值与适用读者
│   ├── 01-author-and-era.md      # 沈复其人与其时代：生平、乾嘉江南、游幕阶层
│   ├── 02-six-records-structure.md # 六记结构与读法：乐/趣/愁/快情感结构与佚两记
│   ├── 03-yun-niang.md           # 芸娘形象与女性书写：陈芸、"最可爱的女人"、女性主体
│   ├── 04-textual-history.md     # 版本流传：稿本→冷摊→独悟庵丛钞→雁来红→俞平伯定本
│   ├── 05-forgery-case.md        # "足本"伪书公案：1935 足本、考辨证据链、黄楚香、陈寅恪伪材料论
│   └── 06-life-aesthetics.md     # 闲情雅趣与生活美学：性灵传统、盆景茶食、与晚明小品文脉
├── examples/             # 实践示例 3 篇 + index.md(toctree)
│   ├── 01-close-reading.md       # 名篇精读：童趣/藏粥/七夕镌章/芸论李杜/回煞（原文+注+赏析）
│   ├── 02-reading-plan.md        # 阅读路径与版本选择：零基础计划 + 注本/译本分级推荐
│   └── 03-lost-records.md        # 佚卷追寻：钱泳《记事珠》卷五佚文发现始末与"足本"读法
└── references/           # 信源登记 4 篇 + index.md(toctree)
    ├── 01-primary-editions.md    # 原典与版本信源（独悟庵丛钞本、俞平伯校本、人文社、中华书局三全本）
    ├── 02-scholarship.md         # 研究文献（陈毓罴、吴幅员、杨仲揆、王瑜孙、蔡根祥、乐黛云等）
    ├── 03-translations.md        # 译介传播（林语堂译本、Shirley Black、白伦江素惠、多语种译本）
    └── 04-adaptations.md         # 衍生与跨媒介（昆剧/京剧、语文教材《童趣》、绘画等）
```

### FR-2 导航登记

- 新建 `think/classics/index.md`（group 索引，含 toctree 引用 fusheng-liuji-reading/index）。
- 更新 `think/index.md`：域内分组导航表新增 classics 行；toctree 新增 `classics/index`；描述文字更新。
- 更新 `doc/bundles/index.md`：think 域"5 束 · 2 组"改为"6 束 · 3 组"，分组表新增经典阅读行；生态关系概览/入门路径中的 think 标签同步（如涉及）。

### FR-3 frontmatter 规范

- 所有 .md 带 OKF v0.2 YAML frontmatter：根 index 用 `type: OKF`；概念用 `type: Concept`；示例用 `type: Example`；信源用 `type: Reference`；facts/insights/log 与各级 index 参照范式。
- 必含字段：`title`、`description`、`tags`、`generated: {by: agent:seven-concepts-sc, at: <ISO8601>}`、`status: stable`、`stale_after: 2027-08-30`、`okf_version: "0.2"`（根）；内容文档含 `sources` 字段溯源到 references。
- 正文中文，文件名 kebab-case 英文；交叉引用用相对路径，禁止 `file:///` 绝对路径。

### FR-4 事实与溯源质量

- facts.md 事实分域编号（作者生平/成书/版本流传/伪书公案/佚文发现/译介传播/内容事实），每条客观陈述，不含因果推断词（G1 质量门）。
- 关键事实（年份、人名、版本、考辨结论）均有信源支撑，references 中登记可查的公开来源（中华书局三全本前言、光明日报《真伪之间》、陈毓罴考辨论文、古诗文网全文、学术论文等）。
- 有争议事实（如沈复卒年、初刻年份 1877/1878 两说、卷五佚文真伪争议）必须并列异说，不得单取一说。

## 7. 非功能需求（Non-functional）

- NFR-1：全文件 UTF-8 无 BOM。
- NFR-2：每个含子文档的目录（bundle 根、concepts/、examples/、references/、classics/）均有 index.md 且 `{toctree}` 覆盖全部内容文档。
- NFR-3：文档篇幅对齐范式（概念文档每篇约 4-9KB，示例约 7-9KB，信源约 3-6KB；总量 ≥ 15 个内容文件）。
- NFR-4：所有 toctree 引用的文件真实存在，无断链；新 bundle 不产生孤立文档。
- NFR-5：子模块内变更不触碰 bundle 之外的无关文件（仅允许新增 bundle 目录 + 修改 think/index.md、bundles/index.md 两个登记点）。

## 8. 约束、依赖与假设

- **约束**：projects/awesome-okf-xs 为 git submodule，按子项目规范（OKF v0.2、Sphinx toctree、invoke gates）执行；不提交 git。
- **依赖**：公开网络信源（已完成首轮核验）；子项目 Python 环境（`invoke gates.toctrees` / `invoke gates.utf8`，若环境不可用则手动等价验证并记录）。
- **假设**：
  - A1：《浮生六记》为公有领域清代文本，片段引用与原文精读无版权障碍；
  - A2：think 域容纳古典文学阅读 bundle 符合知识库演进方向（laozi 先例支持）；
  - A3：用户认可"新建 classics 分组"的位置决策（审批门确认）。

## 9. 开放问题（Open Questions）

- OQ-1：bundle 位置采用 `think/classics/fusheng-liuji-reading/`（推荐）还是 `think/fusheng-liuji/` 直挂？默认推荐前者，审批时确认。
- OQ-2：concepts 7 篇 + examples 3 篇 + references 4 篇的规模是否符合预期（"全面系统"定位），还是希望更精简？默认按全量执行。

## 10. 验收标准（Acceptance Criteria）

### AC-1（rule）结构完整
bundle 目录下存在 index.md、facts.md、insights.md、log.md 及 concepts/（7 篇 + index）、examples/（3 篇 + index）、references/（4 篇 + index），文件数 ≥ 19；classics/index.md 存在。
**证据**：目录清单 + 文件计数。

### AC-2（rule）导航与 toctree 完整
think/classics/index.md、think/index.md、bundles/index.md 三级导航均登记新 bundle；所有 `{toctree}` 块引用的文件存在且覆盖同目录全部内容文档；`invoke gates.toctrees` 通过（或手动验证无断链/无孤立文档）。
**证据**：gates 运行输出或人工逐项核对记录。

### AC-3（rule）frontmatter 合规
全部 .md 含合规 YAML frontmatter（type/title/description/tags/generated/status/stale_after，根含 okf_version）；内容文档含 sources 溯源；无 `file:///` 链接；全文件 UTF-8（`invoke gates.utf8` 通过或等价检查）。
**证据**：frontmatter 抽查表 + gates 输出。

### AC-4（rule）事实零臆造
facts.md ≥ 40 条 F 编号事实，无因果推断词；关键事实（沈复 1763 生、嘉庆十三年 1808 使琉球、1877 独悟庵丛钞初刻、1923/24 俞平伯校本、1935 世界书局足本、1978 吴幅员考辨、1989 王瑜孙揭黄楚香、2005 钱泳抄本发现等）与信源一致；争议事实并列异说。
**证据**：facts.md + references 溯源对照；V 阶段对抗审查记录。

### AC-5（rubric）内容质量（0-3，阈值 ≥ 2.5）
- 0：内容空洞/大量网络常识堆砌；
- 1：覆盖基本事实但解读浅薄、结构松散；
- 2：事实准确、结构清晰、有读者向路径设计，偶有深度不足；
- 3：事实翔实可溯源、洞察有反常识点（如伪书公案的证据链、芸娘形象的主体性、闲情美学的文脉定位）、精读片段有原文有赏析、版本推荐可操作。
**证据**：独立评审按维度打分（准确性/结构性/深度/实用性）。

### AC-6（rubric）范式一致性（0-3，阈值 ≥ 2.5）
与 boshu-reading 范式在结构、frontmatter、叙事口吻、导航样式上对齐；新读者能按"快速开始"路径无障碍进入。
**证据**：与 boshu-reading 对照检查表。
