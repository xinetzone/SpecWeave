# 《黄帝内经》OKF 知识包 - 实施计划

> 方法论：seven-concepts 场景 4（知识沉淀）R→I→E 链路 + V（独立对抗审查）+ C（原子提交）。
> 工作目录：`projects/awesome-okf-xs/`（子模块内开发与提交）。

## Task 1: R-权威信源网络调研（版本/注本/教材/电子文本）
- **Status**: pending
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 调研《黄帝内经》成书与著录（《汉书·艺文志》"《黄帝内经》十八卷"）、《素问》《灵枢》流传史（杨上善《黄帝内经太素》、王冰次注 762 年、林亿等《新校正》1057 起、史崧献《灵枢》1155）、版本系统（道藏本、赵府居敬堂本、人卫社 1956/1963 影印本、中医古籍整理丛书校注本）。
  - 调研历代核心注本：王冰《重广补注黄帝内经素问》、杨上善《黄帝内经太素》、马莳《注证发微》、张介宾《类经》（1624）、张志聪《集注》、黄元御《素灵微蕴》《长沙解》系列、丹波元简《素问识》《灵枢识》、丹波元坚《素问绍识》。
  - 调研现代权威：王洪图主编《黄帝内经》（人卫社 21 世纪课程教材）、《内经讲义》（五版教材）、郭霭春《黄帝内经词典》、龙伯坚《黄帝内经概论》、《中医大辞典》。
  - 调研电子文本信源：ctext.org《黃帝內經》条目与底本说明、zh.wikisource、国学导航、中医世家等，给出可信度分级。
  - 产出：调研事实底稿（含每条事实的信源 URL/书目），供 Task 3 与 references/ 使用。
- **Acceptance Criteria Addressed**: AC-6, NFR-1
- **Test Requirements**:
  - `rule` TR-1.1: 关键书目事实（书名、作者、朝代/年份、出版社）≥20 条，每条至少 1 个可访问信源，核心事实双信源；证据=调研底稿。
  - `rule` TR-1.2: 电子信源 URL 全部经 HTTP 实际访问验证可达（ctext/维基文库篇目页）；证据=访问记录。

## Task 2: R-8 篇名篇原文采集与逐字核对
- **Status**: pending
- **Priority**: high
- **Depends On**: None（可与 Task 1 并行）
- **Description**:
  - 从 ctext.org / 维基文库逐篇采集 8 篇精读篇目原文：素问·上古天真论、四气调神大论、阴阳应象大论、生气通天论、藏气法时论、至真要大论（病机十九条段）；灵枢·九针十二原、经脉（十二经脉循行段）。
  - 每篇确定精读将引用的核心段落（名言/纲领条文），逐字转录，标注信源 URL 与篇目定位。
  - 记录异文（如通行本与电子文本差异、异体字/通假字），形成异文注记。
  - 产出：原文底稿（引用块 + 信源标注），供 Task 8 使用；concepts/ 中拟引用的短句一并核对。
- **Acceptance Criteria Addressed**: AC-5, NFR-1
- **Test Requirements**:
  - `rule` TR-2.1: 8 篇每篇至少 3 段核心原文完成逐字转录并标注 ctext/维基文库 URL；证据=原文底稿。
  - `rule` TR-2.2: 底稿中所有引文与信源页面文本一致（转录者自检逐字比对）；异文有注记；证据=底稿比对记录。

## Task 3: facts.md 落盘（G1 事实门）
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 生成 `neijing-reading/facts.md`：F 编号事实表（成书著录、版本年代、注本书目、篇卷结构、电子信源、精读篇目），纯客观表述，无因果推断词。
  - 每条事实标注信源类别（书目/电子 URL）。
- **Acceptance Criteria Addressed**: AC-6, FR-5
- **Test Requirements**:
  - `rule` TR-3.1: G1 扫描——facts.md 无"因为/导致/所以/为了/使得/从而/因此"等因果推断词；证据=grep 输出零命中。
  - `rule` TR-3.2: 事实条目 ≥50 条，书目/年代类均可溯源至 Task 1/2 底稿；证据=条目与底稿交叉核对。

## Task 4: I-insights.md 架构洞察（G2 四元组门）
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 生成 `neijing-reading/insights.md`：≥4 条核心洞察，每条含四元组（现象描述+根因分析+影响评估+阅读建议），附《内经》知识地图（两部 162 篇的主题分布与阅读路径）。
- **Acceptance Criteria Addressed**: FR-6, AC-8
- **Test Requirements**:
  - `rule` TR-4.1: G2 检查——每条洞察四元组完整（现象/根因/影响/建议四要素齐备）；证据=insights.md 结构核查。

## Task 5: E-bundle 骨架与导航文件
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建目录树 `think/huangdi-neijing/neijing-reading/{concepts,examples,references}/`。
  - 写 group index（`huangdi-neijing/index.md`，参照 think/laozi/index.md 格式，含 toctree）。
  - 写 bundle 根 `index.md`（frontmatter：type/title/description/tags/version/sources/generated/verified/status/stale_after/okf_version；快速导航、快速开始、学习路径、非医疗声明；toctree 收 concepts/index、examples/index、references/index、facts、insights、log）。
  - 写 concepts/index.md、examples/index.md、references/index.md（分组表 + toctree，先列全部计划条目）。
  - 写 log.md 初始条目（YYYY-MM-DD 创建记录）。
- **Acceptance Criteria Addressed**: FR-1, FR-9, AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-5.1: 目录与 6 个 index/log 文件存在；okf_version 仅出现在 bundle 根 index；证据=目录列表。
  - `rule` TR-5.2: 每个 index.md 的 toctree 条目与计划文件清单一致（占位文件先建或随 Task 6-8 同步）；证据=gates.toctrees 最终输出（Task 10 终验）。

## Task 6: E-references/ 4 篇信源登记
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 1, Task 5
- **Description**:
  - `editions.md`（现代权威整理本）、`commentaries.md`（历代注本）、`modern-studies.md`（现代教材与工具书）、`electronic-sources.md`（电子文本可信度分级与使用建议）。
  - 每篇含 frontmatter（type: Reference、sources 外部 URL/书目）、信源登记表（书名/作者/出版社/年份/可信度说明）、相关概念链接。
- **Acceptance Criteria Addressed**: FR-4, FR-9, AC-8, NFR-1
- **Test Requirements**:
  - `rule` TR-6.1: 4 篇文件 frontmatter 合规（type 非空、含 sources）；书目信息与 Task 1 底稿一致；证据=文件检查 + 交叉核对。
  - `rubric` TR-6.2: 信源分级可用性；scale 1-5；anchors 1=仅罗列书名无分级/3=有分级但选用建议笼统/5=分级明确且给出读者场景化选用建议；threshold ≥4；证据=references 评审。

## Task 7: E-concepts/ 12 篇概念文档
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Description**:
  - 按 FR-2 写 00-11 共 12 篇概念文档（为什么读、成书版本、结构阅读路径、阴阳五行、藏象、经络、病因病机、诊法、治则治法、养生、五运六气、注本选用）。
  - 每篇 frontmatter（type: Concept、sources 指向 references/ 与电子信源）、原文短句引文须来自 Task 2 核对底稿、观点归属（古注注明注家、现代注明教材/学者）、相关概念交叉链接。
  - 02 篇含零基础阅读路径；11 篇含注本分级选用表。
- **Acceptance Criteria Addressed**: FR-2, FR-7, FR-9, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-7.1: 12 篇文件齐全且 frontmatter 合规；所有原文短句可在 Task 2 底稿中找到一致文本；证据=文件清单 + 引文比对。
  - `rubric` TR-7.2: 概念准确性与分层质量；scale 1-5；anchors 1=概念错误或混层/3=基本准确但归属不清/5=准确、分层清晰、交叉链接合理；threshold ≥4；证据=V 阶段评审。

## Task 8: E-examples/ 9 篇（8 精读 + 通读计划）
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 5, Task 2, Task 7
- **Description**:
  - 8 篇精读：篇章定位 → 核心段落原文（引用块，逐字底稿）→ 词句注释 → 历代注家观点（注明家）→ 现代教材解读（注明来源）→ 非医疗声明 → 延伸阅读。
  - 09 通读计划：分阶段（入门/进阶/研究）阅读方案与注本搭配、时间估算。
  - 每篇 frontmatter（type: Example、sources 含 ctext/维基文库 URL）。
- **Acceptance Criteria Addressed**: FR-3, FR-7, FR-9, AC-5, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-8.1: 9 篇文件齐全；每篇精读含原文引用块且与 Task 2 底稿逐字一致、信源 URL 可访问；证据=文件检查 + URL 抽验。
  - `rule` TR-8.2: 每篇精读含"非医疗建议"声明且四层结构（原文/古注/现代解读/编者按）可辨识；证据=结构核查。
  - `rubric` TR-8.3: 精读教学质量；scale 1-5；anchors 1=原文堆砌无解读/3=有注释但泛泛/5=注释精当、注家观点有归属、可读性强；threshold ≥4；证据=V 阶段评审。

## Task 9: 索引收尾（think/index.md 与 bundles/index.md）
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 更新 `think/index.md`：域说明加黄帝内经、分组表新增行、toctree 加 huangdi-neijing/index。
  - 更新 `bundles/index.md`：total_bundles 286→287、groups 32→33；think 域"5 束 2 组"→"6 束 3 组"；think 分组表加行；生态概览/入门路径 think 描述更新（psi · laozi · huangdi-neijing）。
- **Acceptance Criteria Addressed**: FR-8, AC-7
- **Test Requirements**:
  - `rule` TR-9.1: 计数与实际目录一致（287/33/13；think 6 束 3 组），两文件 toctree 含新条目无断链；证据=gates.toctrees + 计数核对。

## Task 10: 质量门与构建验证
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 6, Task 7, Task 8, Task 9
- **Description**:
  - 在子模块根运行 `invoke gates.all`（utf8 + toctrees）；修复全部报告问题直至退出码 0。
  - 运行 `invoke build`（或 `sphinx-build -b dummy -E doc _build/dummy`）验证构建无新增警告。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-10.1: gates.all 退出码 0，输出"检查通过"；证据=命令输出。
  - `rule` TR-10.2: 构建退出码 0 且无新增警告；证据=构建输出。

## Task 11: V-独立对抗审查（fresh context）
- **Status**: pending
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 委托全新上下文的独立审查者（read-only），按 review 合同执行：AC-1~AC-10 逐项核验；重点：从 8 篇精读每篇抽 ≥2 段原文（≥20 段）与 ctext/维基文库逐字比对；facts.md 因果词扫描与信源溯源；frontmatter 合规；计数一致；安全声明。
  - 审查结果写入 `.trae/specs/classics-knowledge/huangdi-neijing-okf/review.md`。
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-9（独立证据）
- **Test Requirements**:
  - `rule` TR-11.1: review.md 含每个 AC 的独立证据与 pass/fail 结论；原文抽查 ≥20 段且结果记录在案；证据=review.md。

## Task 12: C-整改闭环与原子提交
- **Status**: pending
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 若 Review fail：将每条 actionable finding  materialize 为 pending issue，整改后重跑质量门并启动新一轮 Review。
  - Review pass 后：在子模块仓库按 Conventional Commits 提交（`docs(think): 新增黄帝内经原典阅读教程 OKF 知识束...`，中文主体说明 R→I→E→V、事实条数、束/组计数变更）；验证 git log/status。
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `rule` TR-12.1: 子模块 git log 出现新提交、git status 干净；提交信息符合规范；证据=git 输出。