# 性学经典著作 OKF Wiki 教程 Spec

> **change-id**: `create-sexology-classics-wiki`
> **主题目录**: `standards-tools`（沿 create-graphql-wiki-tutorial / create-tvm-ffi-wiki-tutorial 先例）
> **七概念链路**: 场景4 知识沉淀 R→I→E→V→C（R/I 已完成，本 spec 对应 E 阶段实施蓝图，V 为实施后强制独立评审）
> **内容敏感度**: 公开（Public）——学术研究对象，教育性阅读教程，不含露骨描写
> **调研基础**: 104 条带 URL 信源的事实（F-ANCIENT-001~030 / F-WEST-001~036 / F-CHINA-MODERN-001~038），G1 质量门已通过

## Why

`projects/awesome-okf-xs/doc/bundles` 的 think 域（思想与理论）目前仅有 psi 与 laozi 两个分组，缺乏对性学/性文化经典著作系统的阅读教程。性相关著作横跨古典文献学、医学史、社会学与性别研究，中文读者面临书目分散、译本质量参差、争议版本无从核验三大门槛，需要一份以"方法论范式为入口、以可溯源事实为底座"的阅读教程知识包。

## What Changes

- **新增分组** `doc/bundles/think/sexology/`（与 psi/laozi 平行的子分组入口，含分组导航 index.md）
- **新增 bundle** `doc/bundles/think/sexology/classics-reading/`（阅读教程为主+著作提要定位），结构：
  - `index.md`（bundle 根，OKF v0.2 frontmatter，快速导航/定位对比/学习路径）
  - `facts.md`（104 条事实登记，含【待核验】条目显式标注）
  - `insights.md`（4 条四元组洞察 + 知识地图）
  - `log.md`（创建日志）
  - `concepts/`（约 9 篇概念文档，见 ADDED Requirements）
  - `examples/`（3 篇实践示例）
  - `references/`（5 篇信源文档）
- **更新索引**：
  - `think/index.md`：分组导航表加 sexology 行 + toctree 加 `sexology/index`
  - `bundles/index.md`：计数 286→287 束、32→33 组、think 域 "5 束 · 2 组"→"6 束 · 3 组"、导航表加行
- **范围决策**（用户已确认的三项）：
  1. 收录范围=六大板块全覆盖：①中国古代性文献 ②东方古典（《欲经》/《爱经》） ③西方性学奠基 ④现代性科学 ⑤女性主义/社会建构论 ⑥中国现代性学
  2. 内容定位=阅读教程为主+著作提要
  3. 原文引用=学术引介尺度：公版文献引篇名/核心命题/少量代表片段；现代版权著作仅介绍不录原文

## Impact

- **Affected specs**: 无既有 spec 依赖；本 spec 新增
- **Affected code**（均为文档资产，无代码）:
  - 新建：`projects/awesome-okf-xs/doc/bundles/think/sexology/**`（约 20 个文件）
  - 修改：`projects/awesome-okf-xs/doc/bundles/think/index.md`、`projects/awesome-okf-xs/doc/bundles/index.md`
  - 更新：`.trae/specs/README.md`（主题看板与 spec 登记）
- **不涉及**：git commit（除非用户明确要求）、vendor 区、任何代码构建逻辑

## ADDED Requirements

### Requirement: Bundle 结构与模板一致性

系统（awesome-okf-xs 文档工程）SHALL 在 `think/sexology/classics-reading/` 下创建完整 OKF v0.2 bundle，其文件组织、frontmatter 字段、toctree 写法 SHALL 与 boshu-reading bundle 模板一致：

- bundle 根 index.md frontmatter：`type: OKF`、`title`、`description`、`tags`、`version`、`source`、`generated: {by: "agent:...", at: ISO8601}`、`verified: {by: "process:seven-concepts-v", at: ...}`、`status`、`stale_after`、`okf_version: "0.2"`
- 概念文档 `type: Concept`，信源文档 `type: Reference`，均带 `sources` 逐声明归因（引用格式 `/references/xxx.md` bundle 相对绝对路径）
- 文件名 kebab-case 英文，正文全部中文
- 含子目录的每级 index.md 必须有 hidden toctree 引用全部内容文档

#### Scenario: 新读者从 bundle 根入口进入
- **WHEN** 读者打开 `think/sexology/classics-reading/index.md`
- **THEN** 能看到📚快速导航（concepts/examples/references + facts/insights 工作文档链接）、🚀分读者路径的快速开始、🎯Bundle 定位对比表、📖推荐学习路径
- **AND** 所有链接可点击且指向真实存在的文档

### Requirement: 概念文档覆盖六大板块并按范式组织

concepts/ SHALL 包含约 9 篇概念文档，按"范式入口"而非单纯年代罗列组织（对应洞察 I-1），覆盖用户确认的六大板块：

1. `00-reading-map.md`：总阅读地图——四大范式（古典文献学/临床医学/社会科学/建构论批判）入口与读者自测
2. `01-ancient-china.md`：中国古代性文献——马王堆房中简帛、汉志房中八家、《医心方》辑佚、《素女经》/《洞玄子》/《玉房秘诀》、双梅景闇丛书、房中医学化（《抱朴子》《千金要方》）、明清世情小说中的性书写
3. `02-eastern-western-classics.md`：东方古典与西方古代——《欲经》、奥维德《爱经》
4. `03-foundations.md`：西方性学奠基期——克拉夫特-埃宾、蔼理士、弗洛伊德、赫希菲尔德、1933 柏林焚书
5. `04-modern-science.md`：现代性科学——金赛、马斯特斯与约翰逊、《人类性功能障碍》
6. `05-feminism-construction.md`：女性主义与社会建构论——OBOS、米利特、福柯、鲁宾、巴特勒
7. `06-china-modern.md`：中国现代性学——潘光旦译注、1955《性的知识》、吴阶平《性医学》、阮芳赋、刘达临与博物馆、潘绥铭、李银河、学科建制（中国性学会/期刊/教育部纲要）
8. `07-translations.md`：中文读者的译本与版本选择指南（含待核验条目的处理方式）
9. `08-censorship-power.md`：性学与权力/审查共构的阅读视角（对应洞察 I-4）

#### Scenario: 按范式检索著作
- **WHEN** 读者想了解金赛报告
- **THEN** 在 04-modern-science.md 中能找到著作提要（作者/年代/原版/核心命题/中译本状况）及其与临床医学范式的定位关系
- **AND** 事实性陈述均可在 facts.md 找到对应编号、在信源文档找到 URL

### Requirement: 事实登记与待核验标注

facts.md SHALL 完整登记 104 条 R 阶段事实，按三大板块（F-ANCIENT / F-WEST / F-CHINA-MODERN）分组制表（编号/事实内容），SHALL 对以下调研发现的争议条目显式保留【待核验】标注或选用已核实表述：

- 浙江文艺版《性学三论》译者姓名
- 《人类性功能障碍》中译本状况
- 鲁宾《关于性的思考》正式中译文
- 台湾 OBOS 早期译本年份
- 李银河若干著作的出版社与年份
- 彭晓辉《性科学概论》版本细节
- 潘绥铭《神秘的圣火》年份（1984 vs 1988）
- 中华性文化博物馆创办年（1994 vs 1995）
- 吴阶平讲习班与刘达临 1985 上海讲习班的关系
- 克拉夫特-埃宾《性精神病态》中译本状况
- 《素女经》等成书年代（仅区间性判断：汉魏至隋唐）

**已核验的纠正项**（实施时不得沿用错误预设）：
- 阮芳赋 1985 年主编为《性知识手册》（科技文献出版社）；《性的知识》系 1955 年王文彬等著（人民卫生出版社）
- 《肉蒲团》序年为 1633 年（明崇祯六年）；李渔作者归属有争议
- 同里博物馆 2015 年关闭后藏品分散常州/武汉/海口三处；常州茅山另设道家性养生博物馆（2016 开放）

#### Scenario: 读者核验一条争议年份
- **WHEN** 读者在 06-china-modern.md 看到《神秘的圣火》年份表述
- **THEN** 该处要么采用已核实的单一表述并附信源，要么明确给出"1984（一说 1988）"的争议标注并指向 facts.md 对应条目

### Requirement: 原文引用遵守学术引介尺度

所有引用 SHALL 遵守用户确认的学术引介尺度：

- 公版古典文献（马王堆帛书佚文、《素女经》、《欲经》、《爱经》等）：引篇名、核心命题、少量代表性片段，以学术介绍口吻呈现
- 现代版权著作（金赛、马斯特斯、福柯、李银河等）：只介绍观点与结构，不录原文段落
- 全部内容为教育性、学术性表述，不含露骨性描写

#### Scenario: 内容得体性检查
- **WHEN** V 阶段评审者通读全部产出文档
- **THEN** 不发现超出学术引介尺度的原文摘录或露骨描写
- **AND** 涉及具体文本的引用均可对应到公版文献或仅有提要说明

### Requirement: 索引与计数一致性

think/index.md 与 bundles/index.md 的更新 SHALL 保持计数、表格行、toctree 三者一致：

- bundles/index.md frontmatter：`total_bundles: 287`、`groups: 33`（domains 保持 13）
- think 域表格行改为"6 束 · 3 组"，新增 sexology 分组行与 `sexology/index` toctree 条目
- 新增 bundle 计入 total_bundles

#### Scenario: toctree 质量门通过
- **WHEN** 在 `projects/awesome-okf-xs` 目录运行 `invoke gates.toctrees`
- **THEN** 零断链、零孤立文档
- **AND** `invoke gates.utf8` 通过；`invoke build` Sphinx 构建成功

### Requirement: V 阶段独立对抗评审

实施完成后 SHALL 委托新鲜上下文的独立评审（general_purpose_task 只读），按四视角审查：

1. **事实准确性**：抽查事实条目与信源 URL 对应、待核验标注是否保留、纠正项是否正确落实
2. **新人可入门性**：零基础读者能否通过 00-reading-map 进入并按 examples 路径完成首次阅读
3. **定位与边界**：是否为"阅读教程为主+著作提要"而非论文/百科；是否越界到露骨内容
4. **时效与规范**：frontmatter 合法性、stale_after 设置、索引计数一致

评审结果 SHALL 记录于本 spec 目录 `review.md`；fail 项 materialize 为 tasks.md 中的 pending 修复任务。

## MODIFIED Requirements

（无——本 spec 为纯新增，不修改任何既有 Requirement）

## REMOVED Requirements

（无）

## 实施后记录（Post-Delivery Log）

- **2026-08-30 交付闭环**：双仓提交推送（子模块 `16d6a514` + 主仓库 `bd8e45528`），V 阶段独立评审 6 项问题全部修复（见 [review.md](review.md)），质量门 toctrees/utf8 通过。全量事实与提交记录见复盘报告 [retrospective-sexology-classics-wiki-20260830.md](../../../../.agents/docs/retrospective/reports/concepts/milestone/retrospective-sexology-classics-wiki-20260830.md)。
- **2026-08-31 知识沉淀**：复盘模式 1/2 沉淀为 `documentation-patterns/source-trace-consistency-check.md`、`documentation-patterns/version-discrepancy-arbitration.md`（L1）；洞察 I-3 沉淀为 `code-patterns/submodule-detached-head-ff-only-landing.md`（L2，validation_count=3，主仓库提交 `83c9a58e0`）。
- **2026-08-31 规划记录回写**：tasks.md（T1-T8 勾选 + Task 9 沉淀登记）、checklist.md（按复盘事实勾选，`invoke build` 附解析阶段边界注）。

## 非目标（Out of Scope）

- 不生成任何 git commit
- 不修改 vendor 区文件
- 不收录露骨原文、不做色情内容介绍
- 不解决【待核验】清单（保留标注，留待后续有权威馆藏信源时更新）
- 不为每个著作单独建 bundle（单 bundle 多概念文档模式）
