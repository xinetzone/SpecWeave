# 中西数学对读 OKF Wiki 教程 — 实施计划

> 方法论：seven-concepts 场景4（知识沉淀）R→I→E→V→C，嵌入 Spec Mode 的 Implement 阶段。
> 产出根目录：`projects/awesome-okf-xs/doc/bundles/kexue/math/east-west-dialogue/`（下称 `<bundle>/`）。
> 所有 `invoke` 命令工作目录为 `projects/awesome-okf-xs/`。
> 交叉链接对象：`../../../../guoxue/suanxue/suanjing-reading/`（中国算经束）与本分组 `../classics-reading/`（国外经典束）——实施时以实际相对层级计算为准。

## Task 1: R 阶段——比较信源调研与事实采集

- **Status**: `done`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 用 WebSearch/WebFetch 系统调研并**实际访问验证**三类信源：① 中西原文与译本联合信源（复用既有两束已验证信源 + 增补比较研究专用：CTEXT《九章》《周髀》对照、Gutenberg/Archive 欧氏几何与阿基米德英译、MacTutor 比较数学史条目）；② 比较研究与数学史著作（Needham《中国科学技术史》卷3、Martzloff《A History of Chinese Mathematics》、Chemla & Guo Shuchun《Les neuf chapitres》、吴文俊主编《中国数学史大系》、林力娜（Karine Chemla）论文、李约瑟问题相关研究）；③ 交流史关键事件信源（1607 徐光启-利玛窦译《几何原本》前六卷、1857 李善兰-伟烈亚力续译后九卷、《崇祯历书》、清末算学教育改革）。
  - 每条外部 URL 必须实际访问确认可达且内容匹配，记录验证痕迹；不可验证的 URL 弃用。
  - 产出 `<bundle>/facts.md`：≥30 条零推测事实（G1：无"因为/导致/所以"因果推断词），覆盖六类（双方关键著作年代/作者、平行发展节点、优先权事实、交流事件、思想特征对比事实、信源 URL），每条标注信源 id；信源 id 与 Task 3 的 references 文档对应。
  - 产出 spec 工作区调研笔记（`.trae/specs/classics-knowledge/math-east-west-dialogue-okf-wiki/research-notes.md`，含 URL 验证清单）。
- **Acceptance Criteria Addressed**: AC-5, AC-6, FR-6, NFR-2, NFR-3
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 存在且事实条目 ≥30；每条事实带信源 id 归因，无无来源条目。证据：文件内容核对。
  - `rule` TR-1.2: references 将登记的外部 URL 100% 在 research-notes.md 中有访问验证记录（URL + 访问结论）。证据：research-notes.md 验证清单。
  - `rule` TR-1.3: facts.md 全文无因果推断词（因为/导致/所以/由于/因此）。证据：grep 结果。
  - `rubric` TR-1.4: 事实覆盖完整性（著作年代/作者/优先权/交流事件/思想特征/URL 六类齐全）；scale 1-5；anchors 1=大量关键事实缺失，3=主要节点齐全但交流史事实稀疏，5=六大对读主题全部有事实支撑且优先权事实有学术争议标注；threshold ≥4；证据：facts.md 覆盖矩阵。
- **Notes**: 优先级权事实（如勾股证明归属、圆周率精度、负数使用）存在学术争议处须并列诸说，禁止武断取一说。

## Task 2: 知识包骨架搭建

- **Status**: `done`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建目录 `doc/bundles/kexue/math/east-west-dialogue/{concepts,examples,references}/`。
  - 新建 bundle 根 `<bundle>/index.md`（`okf_version: "0.2"`、`type: OKF`、title/description/tags、`status: draft`、`stale_after`、generated/verified actor 字段）；含快速导航、快速开始、推荐学习路径与完整 toctree（concepts/index、examples/index、references/index、facts、insights、log）。
  - 新建 `concepts/index.md`、`examples/index.md`、`references/index.md`（分组标题+条目列表+必要 toctree）、`log.md`（2026-09-01 创建条目）。
  - **不新建分组索引**（`kexue/math/index.md` 已存在，仅更新）。
  - 更新 `kexue/math/index.md`：分组描述补充中西对读定位；知识包列表新增 east-west-dialogue 行（束数 1→2）；统计表更新；toctree 新增 `east-west-dialogue/index`。
  - 更新 `bundles/index.md`：kexue 域导航行 math 分组束数 1→2 与描述更新；总束数 378→379；域统计核对（9 域 43 组不变）。
- **Acceptance Criteria Addressed**: AC-1, AC-3, FR-1, FR-8
- **Test Requirements**:
  - `rule` TR-2.1: 目录与文件全部存在（bundle 根 index.md、log.md、三个子目录及各 index.md）。证据：Glob/LS。
  - `rule` TR-2.2: kexue/math/index.md 与 bundles/index.md 的统计数字一致（math：2 束；总计：379 束·43 组·9 域），toctree 含 east-west-dialogue/index。证据：文件 diff 核对。
  - `rule` TR-2.3: bundle 根 index.md frontmatter 含 `okf_version: "0.2"` 与非空 `type`。证据：frontmatter 核对。
- **Notes**: 骨架阶段 toctree 引用的文档名须与 Task 4-6 实际文件名完全一致；内容文档齐备后在 Task 8 跑 gates 终验。

## Task 3: references/ 信源登记簿（3 篇）

- **Status**: `done`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `references/joint-sources.md`（type: Reference）：中西原文与译本联合信源——整合既有两束已验证信源（链向 classics-reading/references/original-sources.md 与 suanjing-reading/references/online-sources.md）+ 增补比较研究专用信源（如 ctext《九章算术》对照页、Gutenberg 欧几里得英译、Archive 阿基米德作品集）。
  - `references/comparative-studies.md`（type: Reference）：比较研究与数学史著作登记——Needham SCC vol.3、Martzloff、Chemla & Guo、吴文俊《中国数学史大系》、李俨/钱宝琮、Libbrecht 等，标注适用主题与比较视角价值。
  - `references/cross-references.md`（type: Reference）：与本库知识包的交叉引用——classics-reading（逐主题对应）、suanjing-reading（逐主题对应）、zhexue/psi/psi-math（数学形式化）、viz/3b1b（可视化）、document/katex（排版）、data/pydata/sympy（符号计算），及外部资源（MacTutor 比较条目等）。
  - 每篇含合规 frontmatter（type/title/description/tags/sources/generated/verified/status/stale_after）。
- **Acceptance Criteria Addressed**: AC-2, AC-5, FR-5, FR-10, NFR-2
- **Test Requirements**:
  - `rule` TR-3.1: 3 篇文档存在且 frontmatter 均含非空 `type` 与 `sources`。证据：文件核对。
  - `rule` TR-3.2: 登记的每个新增外部 URL 均能在 research-notes.md 找到验证记录；复用既有束信源处以链接指向而非重复登记。证据：交叉比对。
  - `rubric` TR-3.3: 信源质量与分级（原典底本/现代点校/学术研究三级是否清晰、比较研究信源是否权威）；scale 1-5；anchors 1=仅堆链接无分级，3=主要信源分级但比较研究专用信源稀疏，5=三级清晰、比较研究信源权威齐备；threshold ≥4；证据：文档评审。

## Task 4: concepts/ 对读方法论概念文档（3 篇）

- **Status**: `done`
- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**:
  - `concepts/00-why-compare.md`：为什么做中西数学对读——比较视角的价值（理解数学多样性、打破单线进化史观、深化对两传统的理解）、与既有两束的关系（整合层定位）、Needham 问题简介。
  - `concepts/01-comparative-reading-strategy.md`：比较阅读策略——如何同时使用两束既有内容（同题双源法、先分后合法、差异聚焦法）、比较的三个层次（结果比较/方法比较/思想比较）、避免时代错置与优越论陷阱。
  - `concepts/02-reading-path.md`：跨传统阅读路径设计——按读者背景（零基础/理工科/进阶）给出三条对读路线（几何线/代数线/极限线）、每条路线的书目搭配（西方著作 + 中国算经交替）、与两束既有阅读计划的衔接。
  - 每篇 frontmatter 合规，`sources` 归因到 references 信源；大量相对链接指向既有两束。
- **Acceptance Criteria Addressed**: AC-2, AC-7, AC-9, FR-2, FR-10, NFR-4
- **Test Requirements**:
  - `rule` TR-4.1: 3 篇文档存在，frontmatter 含非空 type、sources、generated、status；交叉链接使用相对路径，无 file:///。证据：文件核对 + grep。
  - `rule` TR-4.2: 文件名 kebab-case 纯英文（NN-slug 形式）。证据：文件名核对。
  - `rule` TR-4.3: 每篇至少 2 条相对链接指向既有两束对应文档且可达。证据：链接抽查。
  - `rubric` TR-4.4: 方法论可操作性（步骤具体、与既有束衔接清晰、读者能照做）；scale 1-5；anchors 1=泛泛而谈，3=有方法但与既有束衔接弱，5=步骤具体、三层次比较法清晰、路线可直接执行；threshold ≥4；证据：文档评审。

## Task 5: concepts/ 六大对读主题概念文档（6 篇）

- **Status**: `done`
- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**:
  - `concepts/03-geometry-measurement.md`：几何与度量对读——《几何原本》（公理演绎、I.47 勾股证明）vs《周髀算经》勾股术与《九章·方田》（实用测量、出入相补）；西方节点链 classics-reading/concepts/05-greek-geometry.md，中国平行链 suanjing-reading/concepts/06-zhoubi-suanjing.md。
  - `concepts/04-number-theory-algebra.md`：数论与代数对读——丢番图《算术》（缩写代数、不定方程）vs《九章·方程》（正负术、线性方程组）与大衍求一术（同余）；链 classics-reading/concepts/06-hellenistic-number-theory.md 与 suanjing-reading/concepts/10-dayan-tianyuan-siyuan.md。
  - `concepts/05-limits-infinity.md`：极限与无穷小对读——阿基米德穷竭法（《圆的度量》）vs 刘徽割圆术（"割之弥细，所失弥少"）；链 classics-reading/concepts/05-greek-geometry.md 与 suanjing-reading/examples/07-geyuan-pi.md。
  - `concepts/06-symbolization-abstraction.md`：符号化与抽象对读——花剌子米代数（修辞代数）→ 韦达符号化 vs 天元术/四元术（天元一术、四元消法）；链 classics-reading/concepts/07-islamic-algebra.md 与 suanjing-reading/concepts/10-dayan-tianyuan-siyuan.md。
  - `concepts/07-axiomatic-algorithmic.md`：公理化与算法化对读——欧氏公理演绎体系（定义-公设-命题）vs 中国算法化传统（术文-算题-注疏）；比较两种范式的认识论差异与互补性；链 classics-reading/concepts/05-greek-geometry.md 与 suanjing-reading/concepts/03-jiuzhang-structure.md。
  - `concepts/08-contact-mutual-learning.md`：接触与互鉴对读——明清之际《几何原本》汉译（1607 徐光启-利玛窦前六卷、1857 李善兰-伟烈亚力后九卷）、《崇祯历书》、清代会通（梅文鼎、《数理精蕴》1723）、清末数学教育转型；链 classics-reading/concepts/08-early-modern-17c.md 与 suanjing-reading/concepts/11-ming-qing-transition.md。
  - 每篇统一四层结构：**西方节点**（概括+链 classics-reading 对应文档）→ **中国平行**（概括+链 suanjing-reading 对应文档）→ **比较分析**（路径差异、优先权争议标注、思想特征对比）→ **对读示范指引**（指向本束 examples/ 或既有两束 examples/ 的对应篇目）。
  - 每篇 frontmatter 合规；跨著作脉络用文字/表格串联；含与相关知识包的相对链接。
- **Acceptance Criteria Addressed**: AC-2, AC-6, AC-7, AC-9, FR-3, FR-10, NFR-3, NFR-4, NFR-5, NFR-7
- **Test Requirements**:
  - `rule` TR-5.1: 6 篇文档存在；覆盖矩阵显示六大主题全覆盖、每篇四层结构完整。证据：覆盖矩阵（insights.md 附）+ 文档核对。
  - `rule` TR-5.2: 关键事实（年代、作者、优先权、交流事件）与 facts.md/references 一致，无相互矛盾；优先权争议处有标注。证据：V 阶段逐条核对。
  - `rule` TR-5.3: frontmatter 合规、文件名规范、无 file:/// 链接、数学表达不触发 Sphinx 警告。证据：文件核对 + Task 8 构建输出。
  - `rule` TR-5.4: 不重复检查——每篇对既有束内容以"链接+概括"呈现，无整段复制；每篇 ≥2 条指向既有束的相对链接。证据：文档比对 + 链接统计。
  - `rubric` TR-5.5: 比较分析洞察力（路径差异、思想特征、优先权辨析）；scale 1-5；anchors 见 AC-9；threshold ≥4；证据：V 阶段评审评分。

## Task 6: examples/ 对读示范（3 篇）

- **Status**: `done`
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - `examples/01-pythagorean-comparison.md`：勾股定理中西双源对读——《几何原本》I.47（欧几里得证明：面积拼接演绎）vs《周髀算经》勾股圆方图（赵爽弦图证明：出入相补）；双方原文公共领域选段对照 → 双方解法逐步对照 → 现代数学语言统一解读 → 差异分析（演绎构造 vs 分割重组）。
  - `examples/02-linear-systems-comparison.md`：线性方程组对读——《九章·方程》方程术与正负术（算筹布列、遍乘直除）vs 高斯消元/莱布尼茨行列式；算筹算草图示 → 现代矩阵语言统一 → 差异分析（算法机械化 vs 符号抽象）。
  - `examples/03-pi-comparison.md`：圆周率对读——阿基米德《圆的度量》（96 边形夹逼、3+10/71 < π < 3+1/7）vs 刘徽割圆术（割圆至 192 边形、徽率 157/50）与祖冲之（密率 355/113）；双方推理过程对照 → 现代极限语言统一 → 差异分析（穷竭法逻辑框架 vs 不等式逼近实用取向）。
  - 每篇含原文选段（公共领域，注明底本来源与信源 id）、双方解法逐步对照、现代数学语言统一解读、差异分析四部分；frontmatter 合规（type: Example 或 Playbook）。
- **Acceptance Criteria Addressed**: AC-8, FR-4, NFR-4, NFR-5
- **Test Requirements**:
  - `rule` TR-6.1: 3 篇文档存在且 frontmatter 合规；引用选段属公共领域且标注来源。证据：文件核对。
  - `rule` TR-6.2: 每篇含四个固定部分（原文对照/解法对照/统一解读/差异分析），结构完整。证据：结构审查。
  - `rubric` TR-6.3: 对读示范质量（逐步对照精确、统一解读准确、差异分析有洞察）；scale 1-5；anchors 见 AC-8；threshold ≥4；证据：V 阶段评审评分。

## Task 7: I/E 阶段——洞察、模式萃取与 bundle 根索引完善

- **Status**: `done`
- **Priority**: medium
- **Depends On**: Task 4, Task 5, Task 6
- **Description**:
  - 新建 `<bundle>/insights.md`：≥4 条四元组洞察（现象+根因+影响+建议，G2），主题建议：① 公理化与算法化两种范式的认识论差异及其历史后果 ② 中西数学接触的"翻译屏障"与"会通努力" ③ 优先权问题的史学方法论 ④ 比较阅读对理解数学多样性的价值；附**六主题 × 双方对应著作覆盖矩阵**。
  - 萃取 ≥2 个可迁移比较阅读模式（G3）：每个模式含触发条件、核心步骤、反模式、迁移示例（如迁移到中西医学对读、中西哲学对读），建议模式：①"同题双源对读法"（同一数学问题在两传统中的解法对照流程）②"思想路径分岔图法"（绘制两传统在同一节点的方法分岔与后世影响）。
  - 完善 bundle 根 `index.md`：快速导航（链接全部 9 概念/3 示例/3 信源）、快速开始（直接对读/先分后合两条路径）、Bundle 定位（与 classics-reading、suanjing-reading 的三层分工：单传统西方/单传统中国/比较整合）、对读主题地图；完善 concepts/index.md、examples/index.md、references/index.md 的条目列表。
  - 更新 `log.md` 记录各阶段产出。
- **Acceptance Criteria Addressed**: AC-1, AC-10, FR-7, FR-9
- **Test Requirements**:
  - `rule` TR-7.1: insights.md 含 ≥4 条洞察且每条四元组完整；覆盖矩阵六主题无缺。证据：文件核对。
  - `rule` TR-7.2: ≥2 个模式各含触发条件/核心步骤/反模式/迁移示例四要素。证据：文件核对。
  - `rule` TR-7.3: bundle 根 index.md 快速导航链接覆盖全部内容文档且无死链（与 Task 8 gates 互验）。证据：gates.toctrees 输出。
  - `rubric` TR-7.4: 模式可迁移性（脱离数学经典仍成立）；scale 1-5；anchors 1=模式仅适用本书，3=可迁移到同类阅读，5=四要素齐全且跨领域迁移示例具体；threshold ≥4；证据：V 阶段评审评分。

## Task 8: 构建验证与修复（NFR-1 硬质量门）

- **Status**: `done`（我方产出 0 警告 0 断链；剩余警告/漂移 100% 归属并行会话 WIP 的 yishu/liaoyu 组，不属本任务射程）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 在 `projects/awesome-okf-xs/` 运行 `invoke gates.toctrees`，修复全部断链/孤立文档/toctree 缺漏。
  - 运行 `invoke gates.bundles` 验证总索引计数对账（新增束后必跑）。
  - 运行 `invoke gates.utf8` 确认无 BOM/编码问题。
  - 运行 `invoke clean && invoke build`，修复所有 Sphinx 警告与错误（含数学表达兼容性、frontmatter 日期等）。
  - 运行 `invoke gates.all` 全量质量门终验。
  - 全库检查：文件名 kebab-case、无 file:/// 链接、正文中文、frontmatter 无 ASCII 双引号嵌套陷阱（中文语境引号一律全角""）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-7, NFR-1, NFR-4, NFR-5
- **Test Requirements**:
  - `rule` TR-8.1: `invoke gates.toctrees` 退出码 0，输出 0 broken / 0 orphan。证据：命令输出。
  - `rule` TR-8.2: `invoke gates.bundles` 退出码 0，计数对账一致（379 束）。证据：命令输出。
  - `rule` TR-8.3: `invoke clean && invoke build` 退出码 0，输出 0 warning / 0 error。证据：命令输出。
  - `rule` TR-8.4: `invoke gates.all` 全部通过。证据：命令输出。
  - `rule` TR-8.5: grep 全库无 `file:///`；新增文件名全部匹配 `^[0-9a-z-]+\.md$`（index/log/facts/insights 保留名除外）。证据：grep/Glob 结果。

## Task 9: V 阶段——对抗审查与事实证伪

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 以独立新上下文（fresh reviewer）执行对抗审查，攻击面：① 事实性证伪——年代、作者、优先权、交流事件逐条抽查（用 WebSearch 独立复核 ≥12 个关键事实）；② 信源抽查——references 新增 URL 抽样复验可达；③ 比较分析准确性——有无时代错置、单线进化史观、文化优越论偏见、过度简化；④ 对读示范数学正确性——双方解法对照有无数学错误；⑤ 不重复检查——与既有两束有无内容冗余；⑥ 四个 rubric（AC-8/9/10、TR-3.3）独立评分。
  - 审查结果记录：方法论 V 阶段痕迹写入 log.md / insights.md；Spec Mode 的独立审查产物 `review.md` 由 Review 阶段生成。
  - 所有 actionable 发现修复后复验，直至 0 遗留事实错误。
- **Acceptance Criteria Addressed**: AC-8, AC-9, AC-10, NFR-3
- **Test Requirements**:
  - `rule` TR-9.1: ≥12 个关键事实经独立 Web 复核，错误数为 0（发现的错误全部修复并记录）。证据：review.md 审查记录。
  - `rule` TR-9.2: 抽样 URL 复验可达率 100%。证据：review.md。
  - `rule` TR-9.3: 不重复检查通过——与既有两束无整段冗余。证据：review.md 比对记录。
  - `rubric` TR-9.4: AC-8/AC-9/AC-10 三个维度独立评分均 ≥4，评分理由与证据记录在案。证据：review.md 评分表。

## Task 10: C 阶段——原子交付与提交建议（待用户确认）

- **Status**: `done`（变更清单与提交建议已交付用户；因共享暂存区含并行会话在途文件，本轮不执行 add/commit）
- **Priority**: low
- **Depends On**: Task 9
- **Description**:
  - 用 `git status`/`git diff` 核对变更全部落入工作树（子模块 `projects/awesome-okf-xs/` 内）。
  - 按单一职责准备原子提交建议（预计 1 个 docs 类提交：新增 east-west-dialogue 知识包 + kexue/math 分组索引更新 + bundles 总索引更新），提交信息遵循 Conventional Commits（如 `docs(bundles): 新增中西数学对读知识包（kexue/math/east-west-dialogue）`）。
  - **不自动执行 git commit**；向用户报告变更清单与建议提交信息，待明确确认后提交（子模块内提交，主权区 gitlink 变动另行报告）。
  - 共享索引竞态防护：`git add` 与 `git commit` 分两次执行，中间单独跑 `git diff --cached --name-only` 核对暂存集；发现非己方文件则**不 commit**（停下报告）。
- **Acceptance Criteria Addressed**: NFR-6
- **Test Requirements**:
  - `rule` TR-10.1: git status 显示的变更范围与任务产出一致（无无关文件混入）。证据：git status 输出。
  - `rule` TR-10.2: 建议的提交信息符合 Conventional Commits 且单一职责。证据：提交信息草案用户确认记录。

## Task Dependencies

```
Task 1 (R 调研)
  ├─→ Task 2 (骨架) ─────────────────────────┐
  ├─→ Task 3 (references) ──→ Task 4 (方法论概念) ──→ Task 6 (示例) ──→ Task 7 (洞察模式) ──→ Task 8 (构建验证) ──→ Task 9 (对抗审查) ──→ Task 10 (提交建议)
  └─────────────────────────→ Task 5 (六主题概念) ──↗
```

- Task 4 与 Task 5 可并行（均依赖 Task 1+3，互不依赖）。
- Task 6 依赖 Task 4+5（示例引用概念框架）。
- Task 8-10 串行（验证→审查→提交）。
