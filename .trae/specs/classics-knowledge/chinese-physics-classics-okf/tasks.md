# 中国古代物理典籍 OKF wiki 教程 - 实施计划（tasks.md）

> 方法论链路：**R（调研采集事实）→ I（洞察知识形态）→ E（萃取为 OKF 文档）→ V（对抗审查）→ C（原子提交）**
> 质量门：G1 事实无因果词 → G2 洞察四元组完整 → G3 结构可迁移/一致 → G4 提交原子化
> 工作目录：`d:\AI\projects\awesome-okf-xs`（子模块内执行 invoke 与 git）

## Task 1: R 阶段——公开信源调研与事实采集
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 针对 9 部核心典籍（《墨经》《考工记》《淮南子》《论衡》《梦溪笔谈》《革象新书》《天工开物》《物理小识》《镜镜詅痴》），通过网络检索核实：作者与成书年代、权威整理本（出版社/年份）、在线原文（ctext.org / 维基文库等可达 URL）、与物理学相关的关键段落原文。
  - 并行委派 3 个调研子任务（按典籍分组，互不重叠）：①《墨经》《考工记》《淮南子》《论衡》；②《梦溪笔谈》《革象新书》；③《天工开物》《物理小识》《镜镜詅痴》。
  - 同步登记现代研究文献（戴念祖《中国物理学史》/《中国声学史》/《中国光学史》、关增建、陆敬严、华觉明、钱临照墨经研究、王振铎司南复原、李约瑟《中国科学技术史》物理学相关卷册等）与扩展书目（≥15 部外围典籍）。
  - 产出 `facts.md`（F 编号事实清单：书目/版本/URL/调研过程事实，纯客观无因果词）与 references/ 四份信源文档的素材底稿。
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 全部条目为可验证客观事实（含书目、年代、URL），G1 检查——无"因为/导致/所以/说明"等因果推断词；证据：facts.md 全文关键词扫描
  - `rule` TR-1.2: 每部典籍至少有 1 个可达的在线原文 URL 或权威整理本著录；证据：URL 访问验证记录
  - `rule` TR-1.3: 9 部典籍的关键物理段落原文采集完成，每段标注出处（书名+篇卷）；证据：facts.md 与调研素材清单
- **Notes**: 子任务返回物必须含原文引文+出处 URL+检索日期；不得返回未经验证的二手转述。

## Task 2: I 阶段——洞察分析与知识地图
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 R 阶段事实，撰写 `insights.md`：中国古代物理知识的形态特征洞察（如：经验-工艺取向与理论建构的关系、博物学传统、个别实验精神高峰 vs 体系化不足、西学东渐的转折），每条洞察按四元组（现象+根因+影响+建议）组织。
  - 产出跨典籍×跨学科知识地图（哪些典籍承载哪些物理知识），作为 concepts/ 与 examples/ 的写作蓝图。
- **Acceptance Criteria Addressed**: AC-7, AC-9
- **Test Requirements**:
  - `rule` TR-2.1: G2 检查——每条洞察含现象/根因/影响/建议四要素；证据：insights.md 结构核查
  - `rubric` TR-2.2: 洞察深度；scale 1-5；anchors 1=现象罗列无分析，3=有分析但泛泛，5=四元组完整且能指导教程结构设计；threshold >= 4；证据：insights.md 评审记录

## Task 3: E 阶段骨架——分组、bundle 与导航
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建目录 `doc/bundles/think/physics/classics-reading/{concepts,examples,references}`。
  - 撰写 `physics/index.md`（type: group，分组导航+toctree）。
  - 撰写 `classics-reading/index.md`（bundle 根：type: OKF、okf_version 0.2、frontmatter 全字段、快速导航、按读者类型的快速开始路径、bundle 定位、隐藏 toctree）。
  - 撰写 concepts/index.md、examples/index.md、references/index.md（各含导航表与完整 toctree）。
  - 撰写 `log.md`（2026-08-30 创建条目）。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-3.1: 目录与 7 个骨架文件存在，所有 toctree 覆盖对应目录全部 .md（含后续文件的完整列表）；证据：文件列表 + gates.toctrees
  - `rule` TR-3.2: bundle 根 index.md 含 okf_version "0.2" 与完整 frontmatter；证据：frontmatter 核查

## Task 4: E 阶段——references 信源文档（4 篇）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**:
  - 撰写 `references/core-classics.md`（9 部典籍：作者/年代/权威整理本/在线原文 URL 表格）。
  - 撰写 `references/modern-studies.md`（现代物理学史研究文献分级：入门/进阶/专题）。
  - 撰写 `references/extended-bibliography.md`（≥15 部外围典籍：书名/朝代作者/相关物理内容一句话）。
  - 撰写 `references/online-sources.md`（ctext、维基文库等在线信源及可信度/使用注意）。
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 每部典籍/文献著录含可溯源信息（作者、版本或 URL）；外部 URL 全部经验证可达；证据：URL 抽查记录
  - `rule` TR-4.2: 扩展书目条目数 ≥15；证据：条目计数
  - `rule` TR-4.3: 四篇均含合规 frontmatter（type: Reference、sources、generated/verified、status、stale_after）；证据：frontmatter 核查

## Task 5: E 阶段——concepts 概念文档（8 篇）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 按 FR-2 撰写 8 篇概念文档：00-why-read、01-mechanics、02-optics、03-acoustics、04-magnetism、05-heat-and-matter、06-instruments-metrology、07-interpretation-method。
  - 每篇结构：学科知识在古代典籍中的分布 → 核心记载与原理解释（现代物理学对照）→ 代表性典籍导引（链接 examples）→ 方法论提示（07 篇集中论述辉格史观警示）。
  - 所有事实性论述通过 frontmatter `sources` 溯源到 references 文档。
- **Acceptance Criteria Addressed**: AC-5, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-5.1: 8 篇文件齐全且 frontmatter 合规（type: Concept + sources 指向 /references/）；证据：文件清单与 frontmatter 核查
  - `rubric` TR-5.2: 解读严谨性；scale 1-5；anchors 1=古今概念混同/拔高，3=对照正确但深度一般，5=分层清晰、对照准确、争议有标注；threshold >= 4；证据：逐篇评审
  - `rule` TR-5.3: 每篇含到对应 examples 与 references 的相对链接且无断链；证据：gates.toctrees + 链接抽查

## Task 6: E 阶段——examples 原文解读文档（9 篇/10 文件）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 3, Task 4
- **Description**:
  - 按 FR-3 撰写 9 篇 examples（01-mojing-mechanics、02-mojing-optics、03-kaogongji、04-huainanzi-lunheng、05-mengxi-bitan、06-gexiang-xinshu、07-tiangong-kaiwu、08-wuli-xiaoshi、09-jingjing-lingchi）。
  - 每篇严格遵循统一体例：典籍与版本背景 → 原文引录（逐段标注篇卷出处）→ 字词注释 → 现代物理解读 → 局限与争议 → 延伸阅读（链接 concepts/references）。
  - 全部古文引文取自 Task 1 核实的信源，逐字核对。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-6.1: 9 篇文件齐全，覆盖 9 部典籍（墨经占 2 篇）；每篇含"原文引录"且每条引文标注出处；证据：文件清单与逐篇结构核查
  - `rule` TR-6.2: 引文与信源逐字一致（自查阶段 100% 比对，记录核对表）；证据：引文-信源核对表
  - `rubric` TR-6.3: 解读质量；scale 1-5；anchors 1=杜撰/硬伤，3=准确但解读粗浅，5=注释精当、现代解读准确且明确区分原文与解释；threshold >= 4；证据：逐篇评审

## Task 7: 全库索引联动
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 更新 `think/index.md`：域说明段落补 physics 分组、分组导航表新增"物理典籍"行、toctree 新增 `physics/index`。
  - 更新 `bundles/index.md`：frontmatter 计数（total_bundles 281、groups 33、domains 13）、think 域行（6 束·3 组）、十三域导航新增 physics 分组表格行、toctree 不变（think/index 已在内）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-7.1: 计数与实际文件数一致（281 包/33 组/13 域，think 域 6 束）；证据：数字与目录实际计数比对
  - `rule` TR-7.2: think/index.md toctree 含 physics/index；证据：文件内容核查

## Task 8: V 阶段——对抗审查与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5, Task 6, Task 7
- **Description**:
  - 委派一个全新上下文的独立只读审查（fresh reviewer），执行四类攻击：
    1. **原文核对**：抽查 ≥20 条古文引文与 ctext/维基文库/权威整理本逐字比对；检查 URL 可达性；
    2. **解读证伪**：检查现代物理解释是否正确（如小孔成像、磁偏角、杠杆/力矩、共振、透镜光路），是否存在辉格史观过度拔高；
    3. **工程合规**：frontmatter、toctree、编码、相对路径、Sphinx 构建警告；
    4. **教程可用性**：按三类读者路径走查导航。
  - 运行 `invoke gates.all` 与 `invoke clean && invoke build`，记录基线与结果。
  - 所有 actionable 发现物化为待办修复项并逐一修复；修复后重新构建验证。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-8.1: gates.all 退出码 0；build 0 错误且新增警告 0；证据：命令输出
  - `rule` TR-8.2: 引文抽查 ≥20 条全部一致或已修正；URL 100% 可达；证据：审查核对表
  - `rubric` TR-8.3: 审查者对内容质量（AC-7）与可用性（AC-8）独立评分均 >= 4；证据：review.md 评分与理由
  - `rule` TR-8.4: 所有 actionable 发现有对应修复记录且复验通过；证据：review.md + 修复 diff

## Task 9: C 阶段——原子提交与收尾
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 在子模块内按单一职责组织 Conventional Commits（中文消息），建议序列：
    1. `feat(physics): 新增中国古代物理典籍阅读教程知识包骨架与信源文档`（physics 分组+骨架+references+facts/insights/log）；
    2. `docs(physics): 补充力学/光学等八篇概念文档与九篇典籍原文解读`（concepts+examples）；
    3. `docs(bundles): think域索引与总索引联动新增physics分组`（think/index.md + bundles/index.md）；
    实际提交边界以最终变更与验证结果为准，可合并/调整但保持单一职责。
  - 提交后重跑 `invoke gates.all` 确认通过；`git status` 确认工作树干净（不含无关变更）。
  - 不推送、不更新主仓库 gitlink（除非用户另行指示）。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-9.1: `git log --oneline` 显示规范提交消息（type(scope): 中文描述），每个提交单一职责；证据：git log
  - `rule` TR-9.2: 提交后 gates.all 通过、工作树无遗留无关变更；证据：命令输出与 git status
