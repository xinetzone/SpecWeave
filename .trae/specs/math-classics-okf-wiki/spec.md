---
name: math-classics-okf-wiki-spec
version: 1.0.0
created: 2026-08-30
source: "国外数学经典著作公共领域原文与公开学术信源（Project Gutenberg / Internet Archive / Gallica / Euler Archive / Clay Mathematics Institute 等，经 Web 调研实际验证）"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（数学经典原文多属公共领域，解读为公开学术知识）
---

# 国外数学经典著作原文与解读 OKF Wiki 教程 - 产品需求文档

## Overview

- **Summary**：在 `projects/awesome-okf-xs/doc/bundles` 的 💭 思想与理论域（`think/`）下新建 `math/` 分组，并在其中创建 `classics-reading` 知识包（bundle），系统调研与整理国外数学经典著作（古希腊—阿拉伯—近代—19 世纪—20 世纪初）的**原文获取路径、权威译本/注本、核心思想解读与阅读方法论**，以 OKF v0.2 规范组织为中文 wiki 教程。
- **Purpose**：数学经典是数学思想的源头，但中文读者面对希腊语/拉丁语/法语/德语原著存在三大障碍——不知道原文从哪里获取、不知道该选哪个译本与注本、不知道按什么顺序读、怎么读。本知识包对标已有的 `think/laozi/boshu-reading`（帛书《老子》阅读教程），提供"怎么读 + 读什么"两者结合的实践指南，并系统解读 15+ 部核心经典的思想。
- **Target Users**：
  - 希望阅读数学原典（而非仅读教科书）的数学/计算机/物理专业学生与自学者；
  - 需要数学史与数学思想脉络的教育者、内容创作者；
  - 对数学可视化（viz/3b1b Manim）、数学形式化（think/psi/psi-math）有兴趣，希望追溯思想源头的读者。

## Goals

- 在 `think/math/classics-reading/` 建立符合 OKF v0.2 的完整知识包：`concepts/`（概念与解读）、`examples/`（精读示范与阅读计划）、`references/`（信源登记簿）三层结构 + `facts.md`（R 阶段事实）+ `insights.md`（I 阶段洞察）+ `log.md`。
- 全景覆盖五个时段：① 古希腊与希腊化（欧几里得、阿基米德、阿波罗尼奥斯、丢番图、帕普斯）② 伊斯兰中世纪（花剌子米、海亚姆）③ 17 世纪近代（笛卡尔、牛顿、莱布尼茨）④ 18 世纪启蒙（欧拉）⑤ 19—20 世纪初（高斯、非欧几何、黎曼、伽罗瓦、柯西/魏尔斯特拉斯、戴德金/康托尔、希尔伯特、罗素-怀特海、布尔巴基），精选 ≥15 部核心经典。
- 每部核心经典提供三要素：**原文获取路径**（公共领域数字图书馆 URL/馆藏）、**权威译本与注本推荐**（含 Heath 译注等经典译本与中译本状况）、**核心思想解读**（该书解决什么问题、关键内容、思想脉络与历史影响）。
- 提供可操作的阅读方法论：原文获取渠道辨识、版本/译本选择策略、注本使用法、跨语言阅读策略、分阶段通读计划、代表性命题精读示范。
- 遵循 seven-concepts 场景4 链路：R（事实采集，信源全部经实际访问验证）→ I（洞察，四元组）→ E（萃取 ≥2 个可迁移阅读模式）→ V（对抗审查）→ C（原子提交建议，提交前经用户确认）。

## Non-Goals

- **不大段复制原著原文**：仅收录少量公共领域代表性命题/段落选段用于精读示范，主体为指引与解读（版权与篇幅约束）。
- **不覆盖 20 世纪中叶以后的现代数学专著与论文**（如格罗滕迪克以后）；聚焦"经典原著"谱系。
- **不覆盖中国古代数学**（《九章算术》、《算经十书》等属另一潜在知识包，与"国外"范围无关）。
- **不做数学百科/定理大全**：解读服务于"阅读原著"这一主线，不替代系统教科书。
- **不自动执行 git commit**：文件与验证完成后，原子提交需用户明确确认（遵循"未明确要求不提交"规则）。
- **不修改 OKF 规范本体**（meta/okf-spec）与其他既有知识包内容（仅更新导航索引）。

## Background & Context

- OKF bundles 采用「技术域 → 分组 → 知识包」三级结构，共 13 域 32 组 280 束。`think/`（💭 思想与理论）域现有 `psi/`（Ψhē 理论体系，4 束）与 `laozi/`（老子，1 束）两个分组，是非软件类思想知识的既定归宿。
- `think/laozi/boshu-reading/`（帛书《老子》阅读教程）是本任务的直接范式：7 概念 + 3 示例 + 4 信源 + facts/insights，定位为"读者视角的阅读指南"；其 `source` 字段为本地资料，而本任务信源来自公开网络，需经 Web 调研逐条验证。
- OKF v0.2 合规三要件：① 每个非保留 `.md` 含可解析 YAML frontmatter 且有非空 `type`；② 保留文件（index.md/log.md）遵循结构；③ bundle 根 index.md 可含 `okf_version: "0.2"`。
- 子项目工具链：在 `projects/awesome-okf-xs/` 下运行 `invoke build`（Sphinx 构建，须 0 警告 0 错误）与 `invoke gates.all`（UTF-8 + toctree 完整性）。
- 用户已确认四项范围决策：全景经典谱系；教程形态为"阅读教程 + 思想解读"两者结合（概念文档约 12–18 篇）；原文深度为"指引 + 选段 + 解读"；产出位置为新建 `think/math/` 分组。

## Functional Requirements

- **FR-1（分组与知识包结构）**：新建 `doc/bundles/think/math/index.md`（分组索引，`type: bundles-index`）与 `doc/bundles/think/math/classics-reading/` 知识包目录；知识包含 bundle 根 `index.md`（含 `okf_version: "0.2"`）、`log.md`、`facts.md`、`insights.md`，及 `concepts/`、`examples/`、`references/` 三个子目录（各含 `index.md`）。
- **FR-2（阅读方法论概念）**：concepts/ 包含 ≥5 篇方法论概念文档，覆盖：为什么读原典、原文获取渠道（Gutenberg/Internet Archive/Gallica/Euler Archive/Clay 等数字图书馆）、版本与译本选择、注本与现代解读使用法、跨语言（希/拉/法/德）阅读策略。
- **FR-3（经典谱系解读概念）**：concepts/ 包含按五时段组织的经典解读概念文档（约 8–10 篇），每篇覆盖该时段 2–5 部核心经典，每部经典给出：作者与成书年代、原文语言与权威版本、公共领域获取路径、权威译本/注本（英文为主，中译本状况注明）、核心思想与代表内容解读、阅读难度与建议顺序。
- **FR-4（实践示例）**：examples/ 包含 ≥3 篇：① 代表性命题精读示范（《几何原本》命题三层读法：原文/译本/注本）；② 第一次读原著的最短上手路径；③ 分阶段通读计划（路线图）。
- **FR-5（信源登记簿）**：references/ 包含 ≥3 篇信源登记：① 原文数字信源（含实际验证过的 URL）；② 权威译本与注本（按著作登记）；③ 现代解读与数学史读物；④ 与本库其他知识包的交叉引用。
- **FR-6（R 阶段事实库）**：facts.md 登记 ≥40 条零推测事实（成书年代、作者生卒、原始语言、标准版本、译本出版信息、信源 URL 等），每条可归因到 references 信源；事实陈述无因果推断词（G1）。
- **FR-7（I 阶段洞察与 E 阶段模式）**：insights.md 包含 ≥4 条四元组洞察（现象+根因+影响+建议，G2）；知识包内含 ≥2 个可迁移阅读模式（触发条件+核心步骤+反模式+迁移示例，G3），如"原著三层读法（原文/权威译本/现代注疏）""经典阅读路径选择法"。
- **FR-8（导航更新）**：更新 `think/index.md`（新增 math 分组行 + toctree 条目 + 束数）、`bundles/index.md`（think 域统计 5 束·2 组 → 6 束·3 组；总束数 280 → 281；总组数 32 → 33；生态关系图与导航表 think 描述补充 math）。
- **FR-9（frontmatter 合规）**：每个概念/示例/信源文档 frontmatter 含 `type`（必填）、`title`、`description`、`tags`、`sources`（信源归因）、`generated`/`verified`（actor 约定）、`status: draft`、`stale_after`；`generated.by` 使用 `agent:seven-concepts-cmd` 或等价生产者标识。
- **FR-10（交叉链接）**：与库内相关知识包建立合理相对链接：`viz/3b1b`（数学可视化/Manim）、`think/psi/psi-math`（数学形式化）、`document/katex`（数学排版）、`data/pydata/sympy`（符号计算）等。

## Non-Functional Requirements

- **NFR-1（构建质量）**：在 `projects/awesome-okf-xs/` 下 `invoke clean && invoke build` 必须 0 错误 0 警告；`invoke gates.all` 全部通过（UTF-8 无 BOM、toctree 无断链无孤立文档）。
- **NFR-2（信源可信）**：references 中登记的外部 URL 必须在调研中实际访问验证（HTTP 可达且内容匹配），不可凭记忆编造；不可验证的 URL 不得写入。
- **NFR-3（事实准确）**：所有年代、作者、书名、译本信息与权威信源一致；对抗审查（V）阶段对事实性陈述逐条证伪，遗留错误数为 0。
- **NFR-4（语言与命名）**：正文为规范现代汉语；文件名 kebab-case 纯英文无中文；Markdown 交叉引用一律相对路径，禁止 `file:///` 绝对路径。
- **NFR-5（数学表达兼容）**：数学符号以 Unicode 与文字表述为主，复杂公式用代码块或文字展开；不依赖未启用的 Sphinx 数学扩展，以构建 0 警告为硬约束。
- **NFR-6（原子化交付）**：文档遵循单一职责（一篇一主题），行动项/提交满足原子化（G4）：单一职责、可独立验证。

## Constraints

- **Technical**：产出物位于 git submodule `projects/awesome-okf-xs/` 内（第一方子项目，允许子模块内开发）；使用该子项目自身工具链（`invoke build`/`invoke gates.*`，工作目录需在子项目根）；遵循子项目 AGENTS.md 与 frontmatter 规范；Sphinx/myst_parser 构建约束（裸日期由 conf.py 钩子自动加引号，无需手工处理）。
- **Business**：公共领域/公开信源内容（Public），标准工作流；Spec 产物位于主权区 `.trae/specs/math-classics-okf-wiki/`，最终知识包位于子项目 `doc/bundles/`。
- **Dependencies**：网络调研能力（WebSearch/WebFetch）可用；`projects/awesome-okf-xs/` 子模块已初始化（已确认可读）；`invoke` 命令可用（历史会话已验证）。

## Assumptions

- "国外数学著作"指希腊—阿拉伯—欧洲数学传统的经典原著，不含中国古算。
- 读者以中文为母语，原文语言（希/拉/法/德/英）通过权威英译本/中译本与少量原文选段桥接，教程不教授语言本身。
- 公共领域数字信源（Gutenberg、Internet Archive、Gallica、Euler Archive、大学馆藏页等）在调研时点稳定可达；若个别 URL 失效，以同文献的替代权威馆藏登记。
- 知识包初版 `status: draft`（未经人工独立核验），与 psi-math 等既有知识包做法一致。

## Acceptance Criteria

### AC-1: 知识包目录结构与位置（rule）

- **Given**：任务完成
- **When**：检查 `projects/awesome-okf-xs/doc/bundles/think/math/`
- **Then**：存在 `index.md`（分组索引）与 `classics-reading/` 目录；后者含 `index.md`、`log.md`、`facts.md`、`insights.md`，及 `concepts/`、`examples/`、`references/` 三个子目录且各含 `index.md`；concepts 文档 12–18 篇、examples ≥3 篇、references ≥4 篇。
- **Pass Condition**：目录与文件全部存在，数量满足下限。
- **Evidence**：目录列表（LS/Glob）与文件计数。

### AC-2: OKF v0.2 frontmatter 合规（rule）

- **Given**：知识包内全部 Markdown 文件
- **When**：检查 frontmatter
- **Then**：每个非保留 `.md` 含可解析 YAML frontmatter 且 `type` 非空；bundle 根 `index.md` 含 `okf_version: "0.2"`；概念/示例/信源文档含 `title`/`description`/`tags`/`sources`/`generated`/`status`/`stale_after` 字段；`index.md`/`log.md` 遵循保留文件结构（log 按 `YYYY-MM-DD` 日期分组倒序）。
- **Pass Condition**：逐文件检查全部满足；无 `file:///` 链接。
- **Evidence**：frontmatter 抽查记录 + grep 检查结果。

### AC-3: 导航与 toctree 完整性（rule）

- **Given**：知识包创建并更新导航
- **When**：运行 `invoke gates.toctrees`（工作目录 `projects/awesome-okf-xs`）
- **Then**：无断链、无孤立文档、bundle 根 index 完整；`think/index.md` 含 math 分组导航行与 toctree 条目；`bundles/index.md` 的 think 域统计与总数更新一致（6 束·3 组；总 281 束·33 组·13 域）。
- **Pass Condition**：`invoke gates.toctrees` 退出码 0 且输出 0 broken；两处索引统计数字一致。
- **Evidence**：invoke 命令输出 + 索引文件 diff。

### AC-4: Sphinx 构建与质量门通过（rule）

- **Given**：全部文档完成
- **When**：运行 `invoke clean && invoke build` 与 `invoke gates.all`
- **Then**：构建 0 错误 0 警告；UTF-8 检查通过。
- **Pass Condition**：两条命令均成功退出，输出无 warning/error。
- **Evidence**：命令输出日志。

### AC-5: 信源真实可达与事实可溯（rule）

- **Given**：references/ 登记的外部信源与 facts.md 事实
- **When**：抽样实际访问外部 URL 并核对 facts 归因
- **Then**：references 中登记的外部 URL 100% 经调研访问验证（每条在 facts 或 references 留有验证痕迹）；facts.md ≥40 条事实每条可归因到信源 id，无无来源事实；无凭记忆编造的 URL 或书目信息。
- **Pass Condition**：外部 URL 验证记录完整；facts 条目 100% 有信源归因。
- **Evidence**：facts.md 信源 id 映射 + Web 调研记录（spec 工作区可留调研笔记）。

### AC-6: 全景覆盖与经典三要素（rule）

- **Given**：concepts/ 经典解读文档
- **When**：核对覆盖矩阵
- **Then**：五个时段（古希腊与希腊化/伊斯兰/17 世纪/18 世纪/19—20 世纪初）均有专文；覆盖 ≥15 部核心经典；每部经典具备三要素（原文获取路径、权威译本/注本、核心思想解读）。
- **Pass Condition**：覆盖矩阵逐时段、逐著作勾选无缺项。
- **Evidence**：insights.md 或 facts.md 附覆盖矩阵；concepts 文档内容核对。

### AC-7: 命名与语言规范（rule）

- **Given**：全部新增/修改文件
- **When**：检查文件名与正文
- **Then**：文件名 kebab-case 纯英文（数字前缀 `NN-` 允许）；正文为规范现代汉语；无 `file:///` 绝对路径链接。
- **Pass Condition**：文件名正则全部通过；grep 无 `file:///`。
- **Evidence**：文件列表 + grep 结果。

### AC-8: 思想解读质量（rubric）

- **Dimension**：核心思想解读的准确性与洞察力——是否讲清每部经典"解决什么问题、关键贡献、思想脉络与影响"，而非书单罗列。
- **Scale**: 1-5
- **Anchors**：1 = 仅罗列书名与一句简介；3 = 每部书有内容概括但思想脉络平淡、偶有套话；5 = 思想解读准确深刻，脉络连贯（问题—方法—影响），有跨著作的思想史洞见。
- **Pass Threshold**：≥ 4
- **Evidence**：concepts 经典解读文档（V 阶段评审评分）。

### AC-9: 教程实用性（rubric）

- **Dimension**：阅读方法论与实操指南的可执行性——获取渠道、译本选择、通读计划、精读示范是否能让读者直接照做。
- **Scale**: 1-5
- **Anchors**：1 = 泛泛而谈无可操作步骤；3 = 有计划与路径但颗粒度粗、部分建议无信源支撑；5 = 路径清晰、资源具体到版本与 URL、精读示范可模仿、通读计划可直接执行。
- **Pass Threshold**：≥ 4
- **Evidence**：examples/ 三篇文档 + 方法论 concepts（V 阶段评审评分）。

### AC-10: 方法论闭环质量（rubric）

- **Dimension**：seven-concepts 链路产物质量——facts 零因果词（G1）、insights 四元组完整（G2）、模式可迁移（G3：触发条件+步骤+反模式+迁移示例）。
- **Scale**: 1-5
- **Anchors**：1 = facts/insights 缺失或模式无反模式；3 = 形式齐全但模式泛化不可迁移；5 = G1/G2/G3 全过，≥2 个模式可直接迁移到其他经典阅读场景（如中国古算、其他学科原典）。
- **Pass Threshold**：≥ 4
- **Evidence**：facts.md、insights.md 与模式章节（V 阶段评审评分）。

## Open Questions

- [x] ~~覆盖范围~~：已确认——全景经典谱系（五时段，≥15 部）。
- [x] ~~教程形态~~：已确认——阅读教程 + 思想解读两者结合。
- [x] ~~原文深度~~：已确认——指引 + 少量公共领域选段 + 解读，不大段复制。
- [x] ~~产出位置~~：已确认——新建 `think/math/` 分组，知识包 `classics-reading/`。
- [ ] 知识包完成并通过验证后，是否执行原子提交（C 阶段）？默认**不自动提交**，待用户确认提交信息后执行。
