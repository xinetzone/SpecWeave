# 中国古代物理典籍 OKF wiki 教程 - 产品需求文档（spec.md）

## Overview

- **Summary**：在 awesome-okf-xs 知识包库 `think/`（思想与理论）域下新建 `physics/` 分组，并交付首期综合教程知识包 `classics-reading`——对中国先秦至清代含物理学内容的核心典籍进行系统调研整理，以"原文选录 + 现代物理解读"方式组织为 OKF v0.2 bundle。
- **Purpose**：中国古代典籍中保存了大量物理学知识记载（《墨经》光学八条与力学定义、《考工记》工艺力学与声学、《梦溪笔谈》磁偏角与共振实验、赵友钦小孔成像大型实验、郑复光《镜镜詅痴》透镜光学体系等），但这些材料散见各书、缺乏面向现代读者的系统化中文教程。本知识包填补 OKF 库 think/ 域在中国科技史/物理学史方向的空白，与已有 `laozi/`（中国哲学经典）形成"思想—科技"互补。
- **Target Users**：
  - 对中国科技史、物理学史感兴趣的中文读者；
  - 寻找中国本土物理学史料教学素材的教师与学生；
  - OKF 知识库的人类读者与 AI 智能体消费者。

## Goals

- 在 `doc/bundles/think/` 下新建 `physics/` 分组（group），含分组导航 `index.md`。
- 交付 anchor bundle `physics/classics-reading/`，严格遵循 OKF v0.2 三层结构（concepts/ examples/ references/）+ 工作文档（facts.md / insights.md / log.md）。
- **精读核心典籍 9 部**：《墨经》《考工记》《淮南子》《论衡》《梦溪笔谈》《革象新书》《天工开物》《物理小识》《镜镜詅痴》，每部至少一篇 examples 原文解读文档（《墨经》拆力学/光学两篇）。
- concepts/ 按物理学科分篇：导论与阅读方法、力学、光学、声学、磁学、热学与物质观、天文仪器与度量衡、解读方法论，共 8 篇。
- references/ 登记四类信源：核心典籍原典与权威整理本、现代物理学史研究文献、扩展书目（15+ 部外围典籍）、在线公开信源。
- 全库导航联动：更新 `think/index.md` 与 `bundles/index.md`（分组数 32→33、知识包数 280→281，域说明与 toctree 同步）。
- 通过 `invoke build`（0 错误）与 `invoke gates.all`（UTF-8 + toctree 完整性）质量门。
- 按七概念方法论（R→I→E→V→C）执行，在子模块内完成 Conventional Commits 原子提交。

## Non-Goals

- 不整理现代中国物理学家著作/教材（用户已确认范围为古代典籍）。
- 不为每部典籍创建独立 bundle（后续扩展方向，本期一个综合 anchor bundle）。
- 不做典籍全文转录与全文白话翻译；仅选录与物理学相关的关键段落，辅以注释与解读。
- 不修改 SpecWeave 主仓库的 gitlink（子模块指针更新由用户另行决定）。
- 不引入本地 PDF 资料（本任务无本地资料库，信源为公开在线原典与公开出版研究文献）。
- 不做物理学史学术新论；所有现代解读以已发表的权威研究为依据，争议处显式标注。

## Background & Context

- **范本**：`doc/bundles/think/laozi/boshu-reading/`（帛书《老子》阅读教程）是同构范本——中国古典文本阅读教程，含 concepts/（7 篇）、examples/（3 篇）、references/（4 篇）、facts.md、insights.md、log.md，frontmatter 与 toctree 写法已验证。
- **规范约束**：OKF v0.2 frontmatter 规范（`type` 唯一必填；`sources` 溯源；`generated`/`verified` 信任字段；`status`/`stale_after` 生命周期；`okf_version: "0.2"` 仅出现在 bundle 根 index.md）；Sphinx + myst_parser 构建；裸日期由 `doc/conf.py` 钩子自动加引号。
- **质量门**：`invoke gates.toctrees`（无断链、无孤立文档、含子目录的 bundle 根 index 必须以 toctree 引用全部内容文档）、`invoke gates.utf8`（UTF-8 无 BOM）、`invoke build`（Sphinx 构建）。
- **内容敏感度**：先秦至清代典籍属公有领域公开内容，现代研究文献为公开出版物 → Public 级，标准工作流，spec 存放于主权区 `.trae/specs/`。
- **子模块流程**：awesome-okf-xs 为第一方自有子模块，允许子模块内开发；工作树当前干净，分支正常。
- **七概念链路**：场景判定为「知识沉淀」（场景4），链路 R（调研采集事实）→ I（洞察知识形态）→ E（萃取为 concepts/examples）→ V（对抗审查：原文核对、解读证伪、辉格史观检查）→ C（原子提交）；质量门 G1（事实无因果词）、G2（洞察四元组）、G3（模式/结构可迁移）、G4（行动项/提交原子化）。

## Functional Requirements

- **FR-1 目录结构**：新建 `think/physics/index.md`（type: group）与 `think/physics/classics-reading/` bundle；bundle 内含 `index.md`、`facts.md`、`insights.md`、`log.md` 及 `concepts/`、`examples/`、`references/` 三个子目录（各含 `index.md`）。
- **FR-2 concepts/（8 篇）**：
  - `00-why-read.md` 为什么读中国物理典籍（阅读价值、适用读者、常见误区）；
  - `01-mechanics.md` 力学（力的定义、杠杆与衡器、材料与结构、流体与简单机械）；
  - `02-optics.md` 光学（光影关系、小孔成像、球面镜、透镜与明清光学）；
  - `03-acoustics.md` 声学（共鸣与共振、音律学、乐器制造声学）；
  - `04-magnetism.md` 磁学（司南与指南针、地磁偏角、磁现象记载）；
  - `05-heat-and-matter.md` 热学与物质观（火候与温度判据、物态变化、气论自然观）；
  - `06-instruments-metrology.md` 天文仪器与度量衡（浑仪/水运仪象台、度量衡中的物理标准）；
  - `07-interpretation-method.md` 解读方法论（古今概念对照、实验复原、辉格史观警示、西学东渐分界）。
- **FR-3 examples/（9 篇，覆盖 9 部典籍）**：
  - `01-mojing-mechanics.md`《墨经》力学条目选读；
  - `02-mojing-optics.md`《墨经》光学八条选读；
  - `03-kaogongji.md`《考工记》选读（工艺力学、钟磬声学、冶铸火候）；
  - `04-huainanzi-lunheng.md`《淮南子》《论衡》选读（冰透镜/潜望镜、顿牟掇芥、静电静磁）；
  - `05-mengxi-bitan.md`《梦溪笔谈》选读（磁偏角/指南针、凹面镜、共振实验、虹）；
  - `06-gexiang-xinshu.md`《革象新书》"小罅光景"小孔成像实验解读；
  - `07-tiangong-kaiwu.md`《天工开物》选读（工艺中的力学/热学知识）；
  - `08-wuli-xiaoshi.md`《物理小识》选读（方以智的"物理"知识体系）；
  - `09-jingjing-lingchi.md`《镜镜詅痴》选读（郑复光透镜光学体系）。
  - 每篇统一体例：**典籍与版本背景 → 原文引录（逐段，标注出处篇卷）→ 字词注释 → 现代物理解读 → 局限与争议 → 延伸阅读**。
- **FR-4 references/（4 篇）**：
  - `core-classics.md` 9 部核心典籍：作者/成书年代、权威整理本（出版社/年份）、在线原文链接；
  - `modern-studies.md` 现代研究文献：戴念祖、关增建、陆敬严、华觉明、钱临照、王振铎、李约瑟等学者相关著作分级登记；
  - `extended-bibliography.md` 扩展书目 ≥15 部（《管子》《吕氏春秋》《淮南万毕术》《博物志》《抱朴子》《武经总要》《新仪象法要》《营造法式》《格术补》等）；
  - `online-sources.md` 在线信源（中国哲学书电子化计划 ctext.org、维基文库等）及可信度与使用注意。
- **FR-5 工作文档**：
  - `facts.md`：R 阶段事实清单（F 编号），登记典籍书目事实、版本事实、信源 URL、调研过程事实；纯客观、零因果推断词；
  - `insights.md`：I 阶段洞察，含四元组（现象+根因+影响+建议）与跨典籍知识地图；
  - `log.md`：创建与变更日志（YYYY-MM-DD 分组倒序）。
- **FR-6 导航与 toctree**：bundle 根 index.md 含快速导航、快速开始（按读者类型的学习路径）、bundle 定位说明、隐藏 toctree（concepts/index、examples/index、references/index、facts、insights、log）；三个子目录 index.md 各自含完整 toctree。
- **FR-7 全库索引联动**：
  - `think/index.md`：域说明新增 physics 分组、分组导航表新增行、toctree 新增 `physics/index`；
  - `bundles/index.md`：`total_bundles: 280→281`、`groups: 32→33`（domains 维持 13）、think 域计数 `5 束 · 2 组 → 6 束 · 3 组`、导航表新增物理典籍分组行、生态图与入门路径视情况补充。
- **FR-8 frontmatter 合规**：每个非保留 .md 含可解析 YAML frontmatter 与非空 `type`；concepts/examples/references 文档携带 `sources` 溯源条目（bundle 内 `/references/xxx.md` 与外部 URL）；含 `generated`/`verified`（`agent:` 与 `process:seven-concepts-v` 标记）、`status: stable`、`stale_after: 2027-08-30`；bundle 根 index.md 携带 `okf_version: "0.2"`。

## Non-Functional Requirements

- **NFR-1 引文准确性（最高优先级）**：examples 中每一条古文原文引录必须可溯源至 references 登记的权威信源（权威整理本或 ctext/维基文库在线原文）；V 阶段对全部引文逐条核对，严禁凭记忆杜撰或改写原文。
- **NFR-2 解读严谨性**：严格区分「原文记载」（引文与直译注释）与「现代解读」（现代物理学概念对照）；禁止辉格史观式过度拔高（如把经验记载直接等同于现代定律）；学术争议处显式标注"另有解释/学界有争议"。
- **NFR-3 构建合规**：`invoke clean && invoke build` 0 错误；警告数不高于任务开始前基线（目标 0 新增警告）；`invoke gates.all` 全部通过。
- **NFR-4 工程规范**：文件名 kebab-case 纯英文；正文中文；UTF-8 无 BOM；Markdown 交叉引用一律相对路径、禁止 `file:///`；Mermaid 图（如有）语法正确。
- **NFR-5 教程可用性**：读者无需外部资料即可按 bundle 内导航完成"了解价值 → 按学科学习 → 对照原文精读 → 按信源深入"的完整路径。

## Constraints

- **Technical**：OKF v0.2 规范；Sphinx myst 构建（裸日期依赖 conf.py 钩子，无需手动加引号）；Windows 环境；invoke 任务在子模块根目录执行。
- **Business**：内容为公开领域知识；不得编造不存在的文献、版本、ISBN 或 URL；外部 URL 须经实际访问验证可达。
- **Dependencies**：网络访问 ctext.org、zh.wikisource.org 等公开古籍站点；子模块 invoke 工具链可用（pyproject 已声明）。
- **Scope boundary**：所有产出物位于 `projects/awesome-okf-xs/doc/bundles/think/physics/` 及两处索引文件；spec 工件位于主权区 `.trae/specs/classics-knowledge/chinese-physics-classics-okf/`。

## Assumptions

- 用户确认的四项决策：①范围＝中国古代物理典籍；②组织＝新分组 `physics/` + 综合教程 bundle `classics-reading`；③深度＝核心 8-10 部精读（本方案落为 9 部、《墨经》拆两篇共 10 篇 examples）；④交付＝子模块内原子提交。
- 子模块内提交后不自动推送、不更新主仓库 gitlink；如需推送/更新指针由用户另行指示。
- 在线信源以 ctext.org 与维基文库为原文核对主渠道，现代解读以公开出版的物理学史权威研究为依据（通过网络可核实的书目与论点）。
- 既有 `think/laozi/` 的 frontmatter 字段风格（`source`/`generated`/`verified`/`status`/`stale_after`）作为本 bundle 的直接参照。

## Acceptance Criteria

### AC-1: 产物结构完整性
- **Type**: `rule`
- **Given**: 实现完成后的 `doc/bundles/think/physics/` 目录
- **When**: 核对文件清单
- **Then**: 29 个新文件全部存在（physics/index.md 1；classics-reading 根 4；concepts/ 9；examples/ 10；references/ 5），且 think/index.md、bundles/index.md 已更新
- **Pass Condition**: 文件清单逐项存在，无多余孤立 .md
- **Evidence**: 目录列表 + `invoke gates.toctrees` 输出（无孤立文档）

### AC-2: toctree 与链接完整性
- **Type**: `rule`
- **Given**: 全部文档写入完成
- **When**: 在子模块根目录执行 `invoke gates.toctrees`
- **Then**: 0 broken links、0 orphan docs，bundle 根 index 完整性检查通过
- **Pass Condition**: 命令退出码 0 且输出无 BROKEN/ORPHAN
- **Evidence**: 命令输出日志

### AC-3: Sphinx 构建通过
- **Type**: `rule`
- **Given**: 全部文档写入完成
- **When**: 执行 `invoke clean && invoke build`
- **Then**: 构建成功，0 错误；新增警告数为 0（与任务前基线对比）
- **Pass Condition**: build 退出码 0，warning 计数不高于基线
- **Evidence**: 构建输出日志（build 前后警告数对比）

### AC-4: 原文引文可溯源且核对一致
- **Type**: `rule`
- **Given**: examples/ 全部古文引录
- **When**: V 阶段逐条核对引文与权威原文（ctext/维基文库/权威整理本）
- **Then**: 每条引注标注出处（典籍+篇卷），≥20 条关键引文逐字核对一致，无杜撰；所有引用 URL 实际可达
- **Pass Condition**: 核对表 100% 通过；发现的不一致全部修正并记录
- **Evidence**: review.md 中的引文核对表（抽查条目、信源 URL、比对结果）

### AC-5: frontmatter 与编码合规
- **Type**: `rule`
- **Given**: 全部新建 .md
- **When**: 执行 `invoke gates.utf8` 并人工检查 frontmatter
- **Then**: UTF-8 无 BOM；每个非保留 .md 含非空 `type`；bundle 根含 `okf_version: "0.2"`；sources/generated/verified/status/stale_after 字段齐备
- **Pass Condition**: gates.utf8 通过；frontmatter 检查清单无缺失
- **Evidence**: gates.utf8 输出 + 逐文件 frontmatter 清单

### AC-6: 全库索引联动正确
- **Type**: `rule`
- **Given**: think/index.md 与 bundles/index.md 更新完成
- **When**: 检查计数、导航表、toctree
- **Then**: total_bundles=281、groups=33、domains=13；think 域标注 6 束·3 组；两文件 toctree 均含 physics/index；数字与实际 bundle 数一致
- **Pass Condition**: 计数与实际文件数吻合，toctree 条目存在
- **Evidence**: 两文件 diff + 实际目录计数

### AC-7: 解读学术质量
- **Type**: `rubric`
- **Dimension**: 物理解读的准确性与严谨性（原文/解读分层清晰、现代概念对照正确、无过度拔高、争议标注）
- **Scale**: 1-5
- **Anchors**: 1 = 存在杜撰原文或硬伤性错误；3 = 基本准确但部分段落古今概念混淆或解读空泛；5 = 引文准确、解读依据权威研究、分层清晰、争议处标注明确
- **Pass Threshold**: >= 4
- **Evidence**: 独立审查对 concepts/examples 的逐篇评分与依据

### AC-8: 教程可用性
- **Type**: `rubric`
- **Dimension**: 作为阅读教程的导航与学习体验（快速开始路径、跨文档引用、读者分层指引）
- **Scale**: 1-5
- **Anchors**: 1 = 文档堆砌、无学习路径；3 = 结构完整但路径指引笼统；5 = 多类读者均有明确路径、交叉引用顺畅、可独立按图索骥
- **Pass Threshold**: >= 4
- **Evidence**: 独立审查按三类读者（零基础/有物理基础/研究型）走查导航的记录

### AC-9: 七概念过程与原子提交
- **Type**: `rule`
- **Given**: 全部内容与验证完成
- **When**: 检查 facts.md（G1 无因果词）、insights.md（G2 四元组）、提交记录
- **Then**: facts.md 为纯客观事实登记；insights.md 含现象/根因/影响/建议四元组；子模块内提交为 Conventional Commits 中文消息、单一职责（建议：feat 内容与 docs/chore 索引/骨架分开），提交后构建仍通过
- **Pass Condition**: G1/G2/G4 检查通过；`git log` 显示规范提交；工作树无遗留未提交变更（除用户明确保留项）
- **Evidence**: facts/insights 检查记录 + `git log --oneline` + `git status`

## Open Questions

- [ ] 主仓库 gitlink 是否在子模块提交后一并更新？（默认假设：不更新，由用户决定；如用户要求再追加主权区提交）
- [ ] 是否需要在 bundle 中附带 Mermaid 知识图谱/时间线？（默认：insights.md 与 concepts/00 中视内容需要插入，不强制）
