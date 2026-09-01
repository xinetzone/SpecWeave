---
type: Spec
title: 声乐教学（美通唱法+咽音体系）OKF 知识束
status: draft
created: 2026-09-01
source: 微信对话需求（朋友对声乐感兴趣，关键词：美通唱法、咽音体系、侧重教学）
---

# 声乐教学（美通唱法 + 咽音体系）OKF 知识束 - 产品需求文档

## Overview

- **Summary**：在 awesome-okf-xs 子模块 `doc/bundles/think/vocal/` 下新建「🎤 声乐教学」分组与 `meitong-yanyin-pedagogy` 知识束（bundle），产出一套面向零基础自学者与声乐教师的**教学型**中文教程：以「美通唱法」（美声功底 × 通俗表达的融合唱法）为应用目标，以「咽音体系」（林俊卿咽音练声八步骤）为基本功主线，覆盖嗓音科学基础、技法步骤、纠错、保健与教学法。
- **Purpose**：回应微信对话中朋友的明确需求——"对声乐感兴趣，美通唱法、咽音体系，侧重教学"。把零散、神秘化、口传心授的声乐训练知识，整理为有信源、有步骤、有剂量、可照做的 OKF 教程。
- **Target Users**：① 零基础/业余歌唱爱好者（想自学打底、看懂教学术语）；② 流行/美声方向的声乐初学者；③ 声乐教师与播音主持等用嗓职业者（教学参考与嗓音保健）。

## Goals

- **G1 教学主线清晰**：以"美通为用、咽音为体"组织知识——咽音八步骤解决发声机能（呼吸、喉位、共鸣、换声），美通解决风格表达（混声、咬字、通道、审美）。
- **G2 事实可信可核验**：所有事实（人物生平、机构沿革、著作年表、步骤内容、科学数据）登记于 `facts.md`，F 编号连续，关键事实逐条内嵌信源 URL；P0 级事实（生卒年、成立年、出版年、八步骤内容、青歌赛年份）双源核验，存疑说法显式标注。
- **G3 门控全绿入库**：UTF-8 / toctrees / bundles-index 三门通过；Sphinx 构建无新增 frontmatter YAML 告警；总索引五面计数一致（15 域 / 70 组 / 348 束）。
- **G4 安全伦理边界**：明确"自学不能替代面授"、嗓音病变须就医、咽音不神化（对"创始人/包治"等营销说法保持学术辨析）。

## Non-Goals

- 不做音视频示范（纯文本+表格教程；需示范处指明外部权威资源）。
- 不覆盖民族唱法、戏曲唱法、音乐剧唱法的专门技法（仅在唱法谱系中定位对照）。
- 不新建顶层域（不新增 art/ 域；归入 think/ 域，与养生/性学等"身体实践"类教程同域）。
- 不修改并行会话正在编写的 think/daojia 任何文件；不推送远端。
- 不做版本提交之外的 git 操作（不 reset、不 stash、不碰他方暂存内容）。

## Background & Context

- **库现状**（2026-09-01 工作树实测）：15 域 / 69 组 / 347 束；两门控基线全绿。
- **同型范例**：`think/yangsheng/yangsheng-classics-reading/`（Web 公开信源调研 → facts.md F 编号 + insights.md + concepts/examples/references 三层，generated.by 为 `agent:seven-concepts-cmd`），本束完全对齐该结构。
- **并行会话**：think/daojia 道家束 WIP 正在写入（共享索引 `doc/bundles/index.md` 与 `think/index.md` 已被其修改但门控仍绿）。共享索引编辑只做**追加**，提交时 add 与 commit 分离并核对暂存集。
- **方法论**：七概念「知识沉淀」场景链路 R（事实采集）→ I（架构洞察）→ E（模式萃取入束）；G1 事实门（无因果断言、信源内嵌）、G3 模式门（可迁移：触发条件+步骤+反模式）适用。
- **预核验结论**（Specify 阶段 Web 调研已确认关键实体存在）：
  - 咽音（意 Voce faringea / Pharyngal Voice）：意大利美声老派练声法，林俊卿系统化为八步骤（四无声 + 四有声）。
  - 林俊卿：1940 年北京协和医学博士，1941 年后从意大利教师学声乐；上海声乐研究所主持者；著《歌唱发音的机能状态》《歌唱发音不正确的原因及纠正方法》（1960 年代）与《咽音练声的八个步骤》。
  - 潘乃宪（？–2022-12-28）：1956 年任上海声乐研究所所长助理（咽音→通俗教学的桥梁人物），著《声乐实用指导》（1994，上海音乐出版社）等。
  - 金铁霖（1940–2022）：中国音乐学院，"声情字味表养象"七字标准、"民族性/科学性/艺术性/时代性"、混声/U 通道/支点教学法；其论文集明确列举"民通、美通、民美"等融合唱法。
  - 1986 年第二届 CCTV 青歌赛首次分设美声/民族/通俗三种唱法（央视官网、光明日报双源）。

## Functional Requirements

- **FR-1 目录结构**：新建
  - `think/vocal/index.md`（group 级，type: group，含束列表 + hidden toctree）
  - `think/vocal/meitong-yanyin-pedagogy/`：`index.md`（束根，okf_version 0.2）、`facts.md`、`insights.md`
  - `concepts/`：10 篇概念文档 + `index.md`
  - `examples/`：2 篇实操文档 + `index.md`
  - `references/`：3 篇信源文档 + `index.md`
- **FR-2 内容覆盖（10 概念）**：
  1. `00` 入门地图：为什么以"美通为用、咽音为体"为主线（读者画像、知识地图、束用法）
  2. `01` 歌唱生理基础：呼吸器官、声带闭合、共鸣腔、发音管与歌手共振峰（约 2800–3200 Hz）
  3. `02` 三种唱法与"美通"定位：1986 青歌赛三分法源流、融合唱法谱系（民通/美通/民美）、金铁霖"中国声乐"框架
  4. `03` 美通唱法技术原理：美声功底（通畅/共鸣/混声）× 通俗表达（语气/咬字/个性化）、混声与换声区、通道与支点概念
  5. `04` 咽音体系源流：意大利 Voce faringea 传统（阉人歌手背景、卡鲁索经验谈）→ 林俊卿生平 → 上海声乐研究所 → 六步骤到八步骤演进
  6. `05` 八步骤（上）四无声练习：张大口、震摇下巴吐舌、舌成沟、狗喘气（动作要领、达标标准、常见错误）
  7. `06` 八步骤（下）四有声练习：气泡音、哼咽音/打嘟噜、张口咽音与 oo 音管、打开喉咙泛音管（要领、声音判断标准、常见错误）
  8. `07` 常见发声毛病与纠正：挤卡捏、喉位过高、气息浅、换声断层、白声散声等——症状→机理→纠正练习映射
  9. `08` 嗓音保健与咽音治疗：用嗓卫生、声带小结等病变、气泡音按摩原理、**就医边界**与自学安全规则
  10. `09` 教学法与练声安排：潘乃宪"辨证施治/理论通俗化方法具体化"、金铁霖"启发式感觉教学/七字标准"、每日练声结构、自学与面授的关系
- **FR-3 实操文档（2 篇）**：
  - `examples/01` 每日 20–30 分钟练声清单：八步骤剂量表（次数/时长/频次）、晨起/睡前黄金时段、自检标准
  - `examples/02` 八周自学路线图：周目标、每周练习重点、配套曲目选择（美通方向）、阶段性自检与红线
- **FR-4 信源文档（3 篇）**：
  - `references/01` 核心著作与教材：林俊卿三书、潘乃宪著作年表、金铁霖教材、沈湘体系（《歌唱学》）等，含出版信息与可信度分级
  - `references/02` 现代嗓音科学与海外体系：歌手共振峰研究、SLS（Speech Level Singing）、Estill Voice Training、嗓音医学
  - `references/03` 机构/人物/赛事史料：上海声乐研究所、北京声乐研究所、师承谱系、青歌赛制度史
- **FR-5 facts.md**：F 编号事实 ≥ 70 条，分八组（意大利传统/林俊卿生平/八步骤/潘乃宪/金铁霖/三分法制度史/嗓音科学/美通术语）；P0 事实双源；纯客观陈述（G1 门：无"因为/导致"因果推断）。
- **FR-6 索引注册**：
  - `think/index.md`：域内导航表新增声乐教学行；toctree 新增 `vocal/index`；description 补入声乐
  - `doc/bundles/index.md`：frontmatter `total_bundles: 348 / groups: 70 / domains: 15`；正文计数行同步；think 节标题改「43 束 · 24 组」；think 分组表新增声乐教学行（束数 1）；两处 mermaid think 节点标签补 vocal
- **FR-7 frontmatter 合规**：每文件 `type` 非空；溯源 `sources` 内嵌；双引号标量内禁止 ASCII 引号（用全角“”）；日期裸写（conf.py 钩子兼容）。

## Non-Functional Requirements

- **NFR-1 语言与命名**：正文中文；文件名 kebab-case 纯英文；交叉引用相对路径，禁 `file:///`。
- **NFR-2 可操作性**：每个练习必须含"动作要领 + 达标/判断标准 + 常见错误 + 剂量"四要素；反例来自教学文献而非杜撰。
- **NFR-3 平衡性**：对咽音疗效、"美通创始人"等营销/门派说法做学术辨析（呈现说法来源 + 学界/制度语境），不造神不贬低。
- **NFR-4 与既有束交叉链接**：与 think/yangsheng（身体实践）、think 域阅读教程系列互链；链接全部相对路径且无断链。
- **NFR-5 幂等安全**：所有门控可重复运行；不依赖网络构建。

## Constraints

- **Technical**：OKF v0.2 frontmatter；Sphinx + myst_parser 构建；门控脚本扫描工作树（含未跟踪文件）；Windows PowerShell 环境，Python 为 py314 conda 环境。
- **Business**：内容为公开知识（Public 级），标准工作流入 `doc/bundles/`；不嵌入微信截图等私域内容。
- **并发**：并行会话占用 think/daojia 与共享索引——共享文件只追加、先读工作树最新版再改；git add 与 commit 分两次工具调用，中间核对 `git diff --cached --name-only`，混入他方文件即停止报告。
- **Dependencies**：Web 公开信源（出版社页、央视/光明日报/人民网等媒体、学术论文、百科词条需交叉验证）；门控脚本与 yangsheng 束范例。

## Assumptions

- 朋友的"美通唱法"指声乐界通行的"美声×通俗"融合唱法（金铁霖框架中的"美通"），而非某歌手自创品牌名；对后者在束中作术语辨析。
- "咽音体系"指林俊卿《咽音练声的八个步骤》体系（国内声乐教学语境下的通行所指）。
- 子模块 py314 环境可运行门控脚本（基线已实测两门绿；utf8 门同构）。

## Acceptance Criteria

### AC-1: 三门质量门全绿
- **Type**: `rule`
- **Given**: 全部束文件与索引修改落盘
- **When**: 在 `projects/awesome-okf-xs` 运行 `python scripts/check-utf8.py`、`check-toctrees.py`、`check-bundles-index.py`
- **Then**: 三脚本均退出码 0；bundles 对账输出 15 域 / 70 组 / 348 束
- **Evidence**: 三条命令输出文本记录于 tasks.md 完成证据

### AC-2: 束文件结构齐备
- **Type**: `rule`
- **Then**: 22 个新文件全部存在：group index 1 + 束根 index/facts/insights 3 + concepts（10+1）+ examples（2+1）+ references（3+1）；每个非保留 .md 含非空 type frontmatter
- **Evidence**: 目录树清单 + frontmatter type 抽查

### AC-3: 事实可信与信源内嵌
- **Type**: `rule`
- **Then**: facts.md F 编号连续无缺号、≥ 70 条；每条 P0 事实（林俊卿/潘乃宪/金铁霖生卒与关键年、上海声乐研究所成立年、三书出版年、八步骤内容、1986 青歌赛）附 ≥ 1 个可访问信源 URL，且 P0 项 ≥ 2 个独立信源；无法双源的说法标注"存疑/单源"
- **Evidence**: facts.md 信源统计 + P0 清单双源核对表

### AC-4: Sphinx 构建兼容
- **Type**: `rule`
- **When**: 运行 sphinx dummy 构建（`sphinx-build -b dummy -E doc _build/dummy` 或仓库等效命令）
- **Then**: 无 myst.topmatter YAML 解析告警、无新增断链 warning（既有 warning 以基线为准排除）
- **Evidence**: 构建输出末尾 warning 统计与基线对比

### AC-5: 索引五面一致与注册完整
- **Type**: `rule`
- **Then**: bundles/index.md 的 frontmatter 计数、正文计数行、think 节标题（43 束·24 组）、think 分组表束数列、末尾 toctree 五面一致；think/index.md 导航表与 toctree 均含 vocal；新束无孤立文档
- **Evidence**: check-bundles-index.py 输出 + toctrees 门输出

### AC-6: 教学可操作性
- **Type**: `rubric`
- **Dimension**: 练习与路线图的可照做程度
- **Scale**: 1-5
- **Anchors**: 1 = 只有抽象描述（"放松喉咙"式黑箱）；3 = 有步骤但缺剂量/判断标准；5 = 每个练习含要领+达标标准+常见错误+剂量，路线图有周目标/自检/红线
- **Pass Threshold**: >= 4
- **Evidence**: concepts/05、06、07 与 examples/01、02 评审打分

### AC-7: 内容准确与术语平衡
- **Type**: `rubric`
- **Dimension**: 事实准确性与门派/营销说法的处理
- **Scale**: 1-5
- **Anchors**: 1 = 照搬营销说法或事实硬伤；3 = 事实基本准但争议未标注；5 = P0 事实双源、六步骤/八步骤演进等异说分层呈现、"美通创始人"类说法有学术辨析、咽音疗效不夸大
- **Pass Threshold**: >= 4
- **Evidence**: 独立评审抽查 10 条事实对照信源

### AC-8: OKF 格式与导航规范度
- **Type**: `rubric`
- **Dimension**: frontmatter/交叉链接/导航表/学习路径的规范一致性
- **Scale**: 1-5
- **Anchors**: 1 = 缺 frontmatter 或断链；3 = 结构齐但导航/路径缺失；5 = 与 yangsheng 范例同构、三层 index 导航完整、学习路径清晰、交叉链接有效
- **Pass Threshold**: >= 4
- **Evidence**: 与 yangsheng 束结构对照 + 链接检查

### AC-9: Git 提交隔离
- **Type**: `rule`
- **When**: 完成后单独提交本束
- **Then**: `git diff --cached --name-only` 仅含 think/vocal/ 新文件、think/index.md、doc/bundles/index.md；无 daojia 或他方文件；commit message 遵循 Conventional Commits 中文主体
- **Evidence**: 暂存集清单与 commit 输出

## Open Questions

- 无（位置/深度/提交策略已经用户 2026-09-01 确认：think/vocal 新分组、标准版 10+2+3、完成后单独提交本束文件）。
