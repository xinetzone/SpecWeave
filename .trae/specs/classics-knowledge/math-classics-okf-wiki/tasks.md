# 国外数学经典著作 OKF Wiki 教程 - 实施计划

> 方法论：seven-concepts 场景4（知识沉淀）R→I→E→V→C，嵌入 Spec Mode 的 Implement 阶段。
> 产出根目录：`projects/awesome-okf-xs/doc/bundles/think/math/classics-reading/`（下称 `<bundle>/`）。
> 所有 `invoke` 命令工作目录为 `projects/awesome-okf-xs/`。

## Task 1: R 阶段——外部信源调研与事实采集

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 用 WebSearch/WebFetch 系统调研并**实际访问验证**五类信源：① 公共领域数字图书馆（Project Gutenberg、Internet Archive、Gallica/BnF、Euler Archive、Clay Mathematics Institute / UT Austin Fitzpatrick 希腊文对照版《几何原本》、Latin Library、DML 等）；② 权威英译本与注本（Heath 译注 Euclid/Archimedes/Diophantus/Apollonius、Rosen 花剌子米、Kasir 海亚姆、Smith-Latham 笛卡尔、Clifford 黎曼演讲、Bonola 非欧几何、Blanton 欧拉等）；③ 现代解读与数学史（Boyer、Kline、Dunham、Stillwell 等）；④ 中译本状况（徐光启/利玛窦、李善兰汉译本，现代中译本）；⑤ 15+ 部核心经典的成书年代、作者、原始语言等事实。
  - 每条外部 URL 必须实际访问确认可达且内容匹配，记录验证痕迹；不可验证的 URL 弃用。
  - 产出 `<bundle>/facts.md`：≥40 条零推测事实（G1：无"因为/导致/所以"因果推断词），每条标注信源 id；信源 id 与 Task 3 的 references 文档对应。
  - 产出 spec 工作区调研笔记（`.trae/specs/classics-knowledge/math-classics-okf-wiki/research-notes.md`，含 URL 验证清单）。
- **Acceptance Criteria Addressed**: AC-5, AC-6, FR-6, NFR-2, NFR-3
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 存在且事实条目 ≥40；每条事实带信源 id 归因，无无来源条目。证据：文件内容核对。
  - `rule` TR-1.2: references 将登记的外部 URL 100% 在 research-notes.md 中有访问验证记录（URL + 访问结论）。证据：research-notes.md 验证清单。
  - `rule` TR-1.3: facts.md 全文无因果推断词（因为/导致/所以/由于/因此）。证据：grep 结果。
  - `rubric` TR-1.4: 事实覆盖完整性（年代/作者/原语言/版本/译本/URL 六类齐全）；scale 1-5；anchors 1=大量关键事实缺失，3=五时段事实基本齐全但译本信息稀疏，5=15+ 部经典六类事实齐备；threshold ≥4；证据：facts.md 覆盖矩阵。
- **Notes**: 调研按五个时段分批进行（古希腊/希腊化→伊斯兰→17 世纪→18 世纪→19-20 世纪初）。

## Task 2: 知识包骨架与分组索引搭建

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建目录 `doc/bundles/think/math/` 与 `doc/bundles/think/math/classics-reading/{concepts,examples,references}/`。
  - 新建分组索引 `think/math/index.md`（frontmatter：`okf_version: "0.2"`、`type: bundles-index`、title/description；含知识包列表表与 toctree）。
  - 新建 bundle 根 `<bundle>/index.md`（`okf_version: "0.2"`、`type: OKF`、title/description/tags、`status: draft`、`stale_after: 2027-08-30`、generated/verified actor 字段）；含快速导航、快速开始、推荐学习路径与完整 toctree（concepts/index、examples/index、references/index、facts、insights、log）。
  - 新建 `concepts/index.md`、`examples/index.md`、`references/index.md`（分组标题+条目列表+必要 toctree）、`log.md`（2026-08-30 创建条目）。
  - 更新 `think/index.md`：域介绍补充数学经典分组、域内分组导航表新增 math 行、toctree 新增 `math/index`。
  - 更新 `bundles/index.md`：think 域"5 束 · 2 组"→"6 束 · 3 组"；总数 280 束→281 束、32 组→33 组；生态关系图与入门路径图中 think 标签补充数学经典；think 域导航表新增 math 分组行。
- **Acceptance Criteria Addressed**: AC-1, AC-3, FR-1, FR-8
- **Test Requirements**:
  - `rule` TR-2.1: 目录与文件全部存在（math/index.md、bundle 根 index.md、log.md、三个子目录及各 index.md）。证据：Glob/LS。
  - `rule` TR-2.2: think/index.md 与 bundles/index.md 的统计数字一致（think：6 束·3 组；总计：281 束·33 组·13 域），toctree 含 math/index。证据：文件 diff 核对。
  - `rule` TR-2.3: bundle 根 index.md frontmatter 含 `okf_version: "0.2"` 与非空 `type`。证据：frontmatter 核对。
- **Notes**: 骨架阶段 toctree 引用的文档名须与 Task 4-6 实际文件名完全一致；内容文档齐备后在 Task 8 跑 gates 终验。

## Task 3: references/ 信源登记簿（4 篇）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `references/original-sources.md`（type: Reference）：公共领域原文数字信源登记——按著作列出原文语言版本、馆藏平台、URL、访问方式（在线阅读/下载格式），含 Gutenberg、Internet Archive、Gallica、Euler Archive、UT Austin/Clay 等。
  - `references/translations-commentaries.md`（type: Reference）：权威译本与注本登记——按著作列出英译本（译注者、出版社、年份、可得性）与中译本状况；含 Heath 译注系列、Loeb/Teubner 校勘本等。
  - `references/modern-expositions.md`（type: Reference）：现代解读与数学史读物登记——Boyer《数学史》、Kline《古今数学思想》、Dunham、Stillwell 等，标注适用阶段。
  - `references/cross-references.md`（type: Reference）：与本库知识包的交叉引用——viz/3b1b（Manim 数学可视化）、think/psi/psi-math（数学形式化）、document/katex（数学排版）、data/pydata/sympy（符号计算），及外部资源（MacTutor 数学史档案等）。
  - 每篇含合规 frontmatter（type/title/description/tags/sources/generated/verified/status/stale_after）。
- **Acceptance Criteria Addressed**: AC-2, AC-5, FR-5, FR-10, NFR-2
- **Test Requirements**:
  - `rule` TR-3.1: 4 篇文档存在且 frontmatter 均含非空 `type` 与 `sources`。证据：文件核对。
  - `rule` TR-3.2: 登记的每个外部 URL 均能在 research-notes.md 找到验证记录；无未验证 URL。证据：交叉比对。
  - `rubric` TR-3.3: 信源质量与分级（入门/进阶/研究级标注是否清晰、信源是否权威）；scale 1-5；anchors 1=仅堆链接无分级，3=主要信源分级但中译本信息缺失，5=信源权威、分级清晰、中英译本齐备；threshold ≥4；证据：文档评审。

## Task 4: concepts/ 阅读方法论概念文档（5 篇）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**:
  - `concepts/00-why-read-originals.md`：为什么读数学原典——与教科书的关系、阅读价值、适用人群与不适用场景。
  - `concepts/01-accessing-originals.md`：原文获取渠道——公共领域数字图书馆使用法（Gutenberg/Archive/Gallica/Euler Archive 等）、扫描本与校勘本辨识、语言与版本辨认。
  - `concepts/02-editions-translations.md`：版本与译本选择策略——原文校勘本（Heiberg/Teubner/Loeb）、权威英译本、中译本状况；译本对照读法。
  - `concepts/03-using-commentaries.md`：注本与现代解读使用法——注家类型（古典注疏/现代译注/数学史）、三阶段选用法、如何让注本服务而非替代原文。
  - `concepts/04-reading-across-languages.md`：跨语言阅读策略——希/拉/法/德数学词汇特征、数学符号史（符号也是"语言"）、双语对照读法、语言门槛的现实预期。
  - 每篇 frontmatter 合规，`sources` 归因到 references 信源；数学表达以 Unicode/文字为主（NFR-5）。
- **Acceptance Criteria Addressed**: AC-2, AC-9, FR-2, NFR-4, NFR-5
- **Test Requirements**:
  - `rule` TR-4.1: 5 篇文档存在，frontmatter 含非空 type、sources、generated、status；交叉链接使用相对路径，无 file:///。证据：文件核对 + grep。
  - `rule` TR-4.2: 文件名 kebab-case 纯英文（NN-slug 形式）。证据：文件名核对。
  - `rubric` TR-4.3: 方法论可操作性（步骤具体、资源可定位、读者能照做）；scale 1-5；anchors 1=泛泛而谈，3=有方法但颗粒度粗，5=步骤具体到平台/版本/URL、含反模式提醒；threshold ≥4；证据：文档评审。

## Task 5: concepts/ 经典谱系解读文档（9 篇）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**:
  - `concepts/05-greek-geometry.md`：古希腊几何——欧几里得《几何原本》（前 300 年）、阿基米德（前 287–212）、阿波罗尼奥斯《圆锥曲线论》（前 200 年左右）。
  - `concepts/06-hellenistic-number-theory.md`：希腊化晚期——丢番图《算术》（约 250 年）、帕普斯《汇编》（约 320 年）。
  - `concepts/07-islamic-algebra.md`：伊斯兰中世纪——花剌子米《代数学》（820 年）、海亚姆《代数》（1070 年）。
  - `concepts/08-early-modern-17c.md`：17 世纪——笛卡尔《几何学》（1637）、牛顿《自然哲学的数学原理》（1687）、莱布尼茨微积分论文（1684/1686）。
  - `concepts/09-euler-18c.md`：18 世纪——欧拉《无穷分析引论》（1748）、《微分学原理》（1755）、《积分学原理》（1768–70）。
  - `concepts/10-gauss-turn.md`：世纪之交——高斯《算术研究》（1801）。
  - `concepts/11-nineteenth-revolution.md`：19 世纪革命——罗巴切夫斯基/波尔约非欧几何（1829/1832）、黎曼就职演讲（1854）、伽罗瓦理论（1832 遗稿/1846 发表）。
  - `concepts/12-rigor-and-foundations.md`：严格化与基础——柯西《分析教程》（1821）、魏尔斯特拉斯 ε-δ、戴德金分割（1872）、康托尔集合论（1874 起）、希尔伯特《几何基础》（1899）。
  - `concepts/13-twentieth-foundations.md`：20 世纪初基础——罗素-怀特海《数学原理》（1910–13）、布尔巴基《数学原本》（1939 起）。
  - 每部经典统一三段式：**原文与获取**（语言/版本/URL，链 references）→ **权威译本与注本**（链 references）→ **核心思想解读**（解决什么问题、关键内容、思想脉络与影响），并给阅读难度与建议顺序。
  - 每篇 frontmatter 合规；跨著作脉络用文字/表格串联；含与相关知识包的相对链接。
- **Acceptance Criteria Addressed**: AC-2, AC-6, AC-8, FR-3, FR-10, NFR-3, NFR-4, NFR-5
- **Test Requirements**:
  - `rule` TR-5.1: 9 篇文档存在；覆盖矩阵显示五个时段全覆盖、核心经典 ≥15 部、每部三要素（原文路径/译本注本/思想解读）齐全。证据：覆盖矩阵（insights.md 附）+ 文档核对。
  - `rule` TR-5.2: 关键事实（年代、作者、书名、译本）与 facts.md/references 一致，无相互矛盾。证据：V 阶段逐条核对。
  - `rule` TR-5.3: frontmatter 合规、文件名规范、无 file:/// 链接、数学表达不触发 Sphinx 警告。证据：文件核对 + Task 8 构建输出。
  - `rubric` TR-5.4: 思想解读质量（问题—方法—影响脉络、跨著作思想史洞见）；scale 1-5；anchors 见 AC-8；threshold ≥4；证据：V 阶段评审评分。

## Task 6: examples/ 实践示例（3 篇）

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - `examples/01-euclid-close-reading.md`：《几何原本》命题精读示范——选一个代表性命题（如第一卷命题 I.1 或 I.47），完整演示三层读法：原文（希腊语/拉丁/英译文公共领域选段）→ Heath 译注注释要点 → 现代数学语言解读，展示"读原著"的实际动作。
  - `examples/02-first-originals-starter.md`：第一次读原著的最短上手路径——按语言门槛排序的入门顺序（建议从欧拉/牛顿英译本或笛卡尔几何学入手），每步给具体资源链接与预计时间。
  - `examples/03-reading-roadmap.md`：分阶段通读计划——按读者背景（零基础/理工科本科/进阶）给出 3–4 阶段路线图与选读书目，含时间估算与检验点。
  - 每篇 frontmatter 合规（type: Example 或 Playbook）。
- **Acceptance Criteria Addressed**: AC-9, FR-4, NFR-4
- **Test Requirements**:
  - `rule` TR-6.1: 3 篇文档存在且 frontmatter 合规；引用选段属公共领域且标注来源。证据：文件核对。
  - `rubric` TR-6.2: 实操可执行性（读者可直接照做、资源具体、步骤可模仿）；scale 1-5；anchors 见 AC-9；threshold ≥4；证据：V 阶段评审评分。

## Task 7: I/E 阶段——洞察、模式萃取与 bundle 根索引完善

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 4, Task 5, Task 6
- **Description**:
  - 新建 `<bundle>/insights.md`：≥4 条四元组洞察（现象+根因+影响+建议，G2），附**五时段 × 15+ 部经典覆盖矩阵**。
  - 萃取 ≥2 个可迁移阅读模式（G3）：每个模式含触发条件、核心步骤、反模式、迁移示例（如迁移到中国古算、其他学科原典阅读），建议模式：①"原著三层读法"（原文/权威译本/现代注疏）；②"经典阅读路径选择法"（按语言门槛与思想依赖排序）。模式写入 insights.md 或 concepts/ 方法论相关文档并在 insights.md 登记。
  - 完善 bundle 根 `index.md`：快速导航（链接全部 14 概念/3 示例/4 信源）、快速开始（零基础/有基础两条路径）、Bundle 定位（与 psi-math、3b1b 的分工）、阅读路径图；完善 concepts/index.md、examples/index.md、references/index.md 的条目列表。
  - 更新 `log.md` 记录各阶段产出。
- **Acceptance Criteria Addressed**: AC-1, AC-10, FR-7, FR-9
- **Test Requirements**:
  - `rule` TR-7.1: insights.md 含 ≥4 条洞察且每条四元组完整；覆盖矩阵五时段无缺。证据：文件核对。
  - `rule` TR-7.2: ≥2 个模式各含触发条件/核心步骤/反模式/迁移示例四要素。证据：文件核对。
  - `rule` TR-7.3: bundle 根 index.md 快速导航链接覆盖全部内容文档且无死链（与 Task 8 gates 互验）。证据：gates.toctrees 输出。
  - `rubric` TR-7.4: 模式可迁移性（脱离数学经典仍成立）；scale 1-5；anchors 1=模式仅适用本书，3=可迁移到同类阅读，5=四要素齐全且跨领域迁移示例具体；threshold ≥4；证据：V 阶段评审评分。

## Task 8: 构建验证与修复（NFR-1 硬质量门）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 在 `projects/awesome-okf-xs/` 运行 `invoke gates.toctrees`，修复全部断链/孤立文档/toctree 缺漏。
  - 运行 `invoke gates.utf8` 确认无 BOM/编码问题。
  - 运行 `invoke clean && invoke build`，修复所有 Sphinx 警告与错误（含数学表达兼容性、frontmatter 日期等）。
  - 运行 `invoke gates.all` 全量质量门终验。
  - 全库检查：文件名 kebab-case、无 file:/// 链接、正文中文。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-7, NFR-1, NFR-4, NFR-5
- **Test Requirements**:
  - `rule` TR-8.1: `invoke gates.toctrees` 退出码 0，输出 0 broken / 0 orphan。证据：命令输出。
  - `rule` TR-8.2: `invoke clean && invoke build` 退出码 0，输出 0 warning / 0 error。证据：命令输出。
  - `rule` TR-8.3: `invoke gates.all` 全部通过。证据：命令输出。
  - `rule` TR-8.4: grep 全库无 `file:///`；新增文件名全部匹配 `^[0-9a-z-]+\.md$`（index/log/facts/insights 保留名除外）。证据：grep/Glob 结果。

## Task 9: V 阶段——对抗审查与事实证伪

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 以独立新上下文（fresh reviewer）执行对抗审查，攻击面：① 事实性证伪——年代、作者、书名、译本信息、URL 逐条抽查（用 WebSearch 独立复核 ≥15 个关键事实）；② 信源抽查——references URL 抽样复验可达；③ 数学思想解读准确性——有无过度简化、时代错置、常识性错误；④ 方法论有效性——阅读计划与建议是否现实可行；⑤ 四个 rubric（AC-8/9/10、TR-3.3）独立评分。
  - 审查结果记录：方法论 V 阶段痕迹写入 log.md / insights.md；Spec Mode 的独立审查产物 `review.md` 由 Review 阶段生成。
  - 所有 actionable 发现修复后复验，直至 0 遗留事实错误。
- **Acceptance Criteria Addressed**: AC-8, AC-9, AC-10, NFR-3
- **Test Requirements**:
  - `rule` TR-9.1: ≥15 个关键事实经独立 Web 复核，错误数为 0（发现的错误全部修复并记录）。证据：review.md 审查记录。
  - `rule` TR-9.2: 抽样 URL 复验可达率 100%。证据：review.md。
  - `rubric` TR-9.3: AC-8/AC-9/AC-10 三个维度独立评分均 ≥4，评分理由与证据记录在案。证据：review.md 评分表。

## Task 10: C 阶段——原子交付与提交建议（待用户确认）

- **Status**: `pending`
- **Priority**: low
- **Depends On**: Task 9
- **Description**:
  - 用 `git status`/`git diff` 核对变更全部落入工作树（子模块 `projects/awesome-okf-xs/` 内）。
  - 按单一职责准备原子提交建议（预计 1 个 docs 类提交：新增 math 分组与 classics-reading 知识包 + 索引更新），提交信息遵循 Conventional Commits（如 `docs(bundles): 新增国外数学经典阅读教程知识包（think/math/classics-reading）`）。
  - **不自动执行 git commit**；向用户报告变更清单与建议提交信息，待明确确认后提交（子模块内提交，主权区 gitlink 变动另行报告）。
- **Acceptance Criteria Addressed**: NFR-6
- **Test Requirements**:
  - `rule` TR-10.1: git status 显示的变更范围与任务产出一致（无无关文件混入）。证据：git status 输出。
  - `rule` TR-10.2: 建议的提交信息符合 Conventional Commits 且单一职责。证据：提交信息草案用户确认记录。
