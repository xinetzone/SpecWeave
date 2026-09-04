---
type: spec
title: 房中（中国古代性文化）典籍权威调研 OKF wiki 教程（think/fangzhong/fangzhong-reading 知识束）
spec_mode: Specify
method: seven-concepts-cmd（场景4 知识沉淀，链路 R→F→I→E→V→C）
session: sc-20260830-fangzhong-okf
content_sensitivity: Public（公版古籍 + 公开出版物信息；学术与文献学定位，不生产色情露骨内容）
created: 2026-08-30
status: awaiting-approval
---

# 房中（中国古代性文化）典籍权威调研 OKF wiki 教程 — 需求规格

## 1. 问题陈述（Problem）

用户要求「全面系统地调研和整理性相关著作的原文和解读，并在 bundles 的恰当位置生成 OKF wiki 教程」。本库既有调研均为中国古典典籍方向（道医、道家、佛家、儒法墨、鬼谷子、阴阳家、黄帝内经），本任务承接同一脉络，主题界定为**中国古代房中类典籍与性文化研究著作**——传统目录学称「房中」（《汉书·艺文志·方技略》方技四家之一），现代学术称性文化史、性医学史、道教养生术。

该领域文献分散在**五个文献世界**中，普通读者与研究者面临三重障碍：

1. **文献层累、存亡断裂**：《汉志》著录房中八家（《容成阴道》等，合计 186/191 卷，小序卷数与著录卷数之差待核验）早已全部亡佚；今见「素女经」「洞玄子」等文本并非传世原书，而是佚文，靠两大系统保存——日本丹波康赖《医心方》（984 年）卷二十八《房内》引文，与清末叶德辉《双梅景闇丛书》辑佚刻本；出土文献（马王堆汉墓《十问》《合阴阳》《天下至道谈》）则把房中体系的实物年代提前到西汉。读者普遍把辑佚本当作「汉代原典」，不辨文本层。
2. **托名成风、伪托泛滥**：房中典籍托名上古神人（素女、玄女、彭祖、容成、务成子）是通例；现代出版与网络上署名《素女经》的白话演绎本、地摊「房中术/阴阳采补」读物、无出处网文大量伪托，学术权威性低；道教内丹「阴阳双修」说（东派陆西星、西派李西月）在道教史研究中本有清修/阴阳两派诠释之争，坊间却常被单一化、神秘化渲染。
3. **缺乏可信赖的教程式入口**：现代学术研究（高罗佩《中国古代房内考》《秘戏图考》、李零《中国方术正考/续考》、江晓原、Douglas Wile《Art of the Bedchamber》、胡孚琛《道学通论》相关章节）分散在宗教史、医学史、社会史不同学科，读者无法回答「房中文献到底有哪些、哪些是真的、从哪本开始读、在线全文去哪里找、哪些说法不可信」。

目标库 `doc/bundles/think/` 已有 psi、laozi、zhuangzi、mozi、yinyangjia、buddhism、guiguzi、legalism、huangdi、huangdi-neijing、daoyi 等思想类分组，尚无覆盖房中/性文化典籍的知识束。

**内容定位与表达边界**：本束是**文化史、医学史、宗教史与文献学的学术研究教程**，不是性教育、性技巧或两性指导读物，更不收录色情内容。精选原文以目录学文献（《汉志》房中小序）、医学养生论述（《素问·上古天真论》、《千金要方·房中补益》节欲论、《三元延寿参赞书》「四不可」）、道教方法论概述（《抱朴子内篇·释滞》）、出土文献的养生原则段落（《十问》《天下至道谈》）为限；对《素女经》《洞玄子》等仅作文献学介绍与学术解读，**不收录露骨的性行为操作性段落，不收录色情文学正文与春宫图像**。

## 2. 用户与使用场景（Users）

* **零基础传统文化读者**：对房中、养生、性文化好奇但被地摊读物误导，需要一条「从哪本书开始、读哪个可信版本、信什么不信什么」的入门路径。
* **有中医/道医基础的读者**：读过 `huangdi-neijing`、`daoyi` 等束，希望理解「房中」在方技四家中的位置、房中与医家养生/内丹的关系，需要权威点校本与出土文献指南。
* **人文研究者（道教史/医学史/性文化史/文献学）**：需要房中文献谱系（汉志著录→医心方佚文→双梅景闇辑佚→马王堆出土）、现代学术地图（高罗佩、李零、江晓原、Wile、Needham、胡孚琛）与辨伪研究线索的可信索引。
* **OKF 知识包读者**：在 think 域导航时，期望获得与 `daoyi-reading`、`neijing-reading` 同构的「权威原文 + 解读 + 信源」阅读教程。

## 3. 目标（Goals）

* **G1**：在 `doc/bundles/think/fangzhong/` 下新建分组与单束总览教程 `fangzhong-reading`，以 OKF v0.2 知识包形态（concepts/examples/references 三层 + facts/insights/log）系统呈现房中典籍与性文化研究著作的权威原文与解读。
* **G2**：内容覆盖房中文献**六层结构**：① 目录著录与源流（《汉志》房中八家、《隋志》、方技四家）；② 出土文献（马王堆《十问》《合阴阳》《天下至道谈》及《养生方》《杂疗方》相关条目）；③ 传世辑佚（《医心方·房内》佚文系统、《素女经》《玄女经》《玉房秘诀》《玉房指要》《洞玄子》《彭祖经》、叶德辉《双梅景闇丛书》）；④ 医家性医学（《素问》、《千金要方·房中补益》、《三元延寿参赞书》、求嗣/种子文献）；⑤ 道教房中与内丹双修论（《抱朴子》、黄书合气与寇谦之清整、《参同契》《悟真篇》清修/双修诠释史、东西派）；⑥ 文学社会史料与现代学术（《天地阴阳交欢大乐赋》敦煌写本、高罗佩、李零、江晓原、刘达临、Wile、Needham）。
* **G3**：每部核心文献提供「精选段落原文（标注篇卷出处）+ 已实际核验的在线全文链接 + 权威纸本整理本指南」三类信息，不系统收录全书全文；辑佚本一律标注「佚文辑本，非《汉志》原书」。
* **G4**：托名、辑佚、争议一律两说并陈或分层标注（代表学者、出处、年代证据），低权威现代读物显式警示，污染信源禁用，未证实信息不写成事实。
* **G5**：通过 awesome-okf-xs 全部导航与构建质量门（toctrees/utf8/build），并在子模块内以 Conventional Commits 原子提交；不干扰其他会话未提交产物。

## 4. 非目标（Non-Goals）

* **N1**：不提供任何性行为、性技巧、两性关系、求子备孕的操作指导；束根显式声明「文化史与文献学研究用途，不构成性教育、医学或生活建议」。
* **N2**：不收录色情文学正文（《金瓶梅》《肉蒲团》等仅在社会史背景提及书名）、春宫/秘戏图图像。
* **N3**：不收录、不复刻露骨的性行为操作性段落（含《素女经》《洞玄子》《房内》中具体技法条目）；此类文献只作版本源流与学术史介绍，引文以目录学、养生原则、方法论概述为限。
* **N4**：不做现代性教育/现代性医学咨询；金赛报告、海蒂报告、福柯《性史》等现代西方性学著作不在本束范围（留作后续可能增量，见开放问题 O3）。
* **N5**：不修改任何既有束内容（`daoyi`、`huangdi-neijing`、`laozi` 等仅交叉引用）；不新建 `tcm/` 域内容（房中归 think 域，理由见 §7 开放问题 O1）。
* **N6**：不处理、不提交、不删改其他会话遗留在工作区的产物：已暂存的 daoyi 束文件、mozi 束两个改动文件、未跟踪目录（`tcm/`、`think/buddhism/`、`think/confucian/`、`think/guiguzi/`、`think/huangdi-neijing/`）；验证期间如需隔离，验证后原样还原。
* **N7**：不修改 awesome-okf-xs 的 `.agents/`、`doc/conf.py`、scripts 等基建文件；不变更主仓（SpecWeave）gitlink 与主仓任何文件，提交仅发生在子模块仓库内。
* **N8**：不对「还精补脑」「采阴补阳」等历史主张作功效断言或现代医学背书；只呈现文献内容与学界研究观点。

## 5. 功能需求（Functional Requirements）

### FR-1 知识包结构与导航

* F1.1 新建分组页 `think/fangzhong/index.md`（type: group），含分组说明（房中=方技四家之一、中国古代性文化典籍）、知识包列表表、toctree 收录 `fangzhong-reading/index`。
* F1.2 新建束 `think/fangzhong/fangzhong-reading/`：束根 `index.md`（type: OKF，含快速导航、快速开始、分档学习路径、学术用途与内容边界声明、toctree）、`facts.md`、`insights.md`、`log.md`，以及 `concepts/`、`examples/`、`references/` 三个子目录（各含 index.md）。
* F1.3 概念层 9 篇（00-08）：房中概念界定与学术框架、《汉志》著录与方技分类、马王堆出土房中文献、《医心方·房内》佚文系统、《双梅景闇丛书》与辑佚学、医家性医学文献、道教房中与内丹双修、文学社会史料、现代学术地图与信源分级。
* F1.4 示例层 3 篇：原典选读（精选段落+篇卷出处+全文链接，学术选段原则）、分档阅读路径（零基础/中医道医基础/研究型三档，含周计划）、现代学术研究入门（高罗佩→李零→Wile 的读法与纸本指南）。
* F1.5 信源层 4 篇：在线古籍平台信源矩阵（典籍×平台 URL 表）、权威纸本整理本（出土整理本/医书校注本/道藏/辑佚丛刊/学术译本）、现代学术研究文献、辨伪与争议登记。
* F1.6 更新 `think/index.md`（域说明、分组表、toctree 增 fangzhong 行）与 `bundles/index.md`（frontmatter 计数与正文计数同步、think 节束/组计数、mermaid think 标签）；**计数以 T0 实测基线为准**（当前磁盘 frontmatter 为 total_bundles 296 / groups 39 / domains 14，含其他会话未提交状态，本任务净增 1 组 1 束）。

### FR-2 内容权威性与真实性

* F2.1 facts.md 登记 R 阶段（多源调研）已取证事实：现代学术著作（书名/作者/出版社/年份/ISBN）、人物年代、古籍著录（《汉志》《隋志》卷次）、出土信息（墓葬/发掘年份/整理本/ISBN）、道藏出处、在线信源 URL（平台优先级：识典＞维基文库＞ctext 主库＞diancang/IDP）。
* F2.2 每部核心文献（《汉志·方技略》、马王堆《十问》《合阴阳》《天下至道谈》、《医心方》卷28、《双梅景闇丛书》辑本、《素问·上古天真论》、《千金要方》卷27、《三元延寿参赞书》、《抱朴子内篇》、《天地阴阳交欢大乐赋》）至少登记 1 个已核验可访问的在线全文/图像 URL，并给出权威纸本整理本信息。
* F2.3 精选原文段落须逐字依据权威本（ctext/识典/维基文库/IDP 已核验文本），标注确切篇卷出处；每段配全文链接；选段遵守 §1 内容边界。
* F2.4 托名与辑佚分层呈现：素女/玄女/彭祖/容成/务成子均标注托名传说性质；《素女经》等辑本标注「佚文辑本、非《汉志》著录原书」并说明辑出来源（《医心方》卷28/叶辑本）；内丹双修争议（清修派 vs 阴阳派、东派/西派）两说并陈代表学者。
* F2.5 低权威读物（现代白话演绎本、地摊「采补」读物、无出处网文）显式警示；zysj.com.cn 等已知污染/低质平台禁用；平台缺陷（OCR 乱码、未校页面、卷次差异）如实注明。
* F2.6 束根与示例页含学术用途与内容边界声明（文化史与文献学研究，不构成性教育/医学/行为指导；不收录露骨内容）。

### FR-3 七概念工作流产物

* F3.1 facts.md：事实按前缀分组编号（CAT 目录著录/EXC 出土/JIYI 辑佚传世/YIXUE 医家/DAOJIAO 道教/WENXUE 文学社会史/XUESHU 现代学术/FRG 辨伪/SRC 信源），纯客观陈述、无因果推断词（G1 质量门），目标 ≥100 条。
* F3.2 insights.md：每条洞察遵循四元组（陈述/证据/反常识/行动），覆盖：房中作为方技知识体系的定位、「汉志有目→原书全佚→佚文重组」的文献层累律、出土本对房中史的改写、辑佚本的文献学地位与使用纪律、道教房中与内丹双修的诠释争议、信源分级与现代读物辨伪（G2 质量门）。
* F3.3 log.md：记录创建日期、结构、事实条数与方法论过程。

## 6. 非功能需求（Non-Functional Requirements）

* **NFR-1 规范合规**：全部 .md 符合 OKF v0.2（frontmatter 必填非空 type；束根带 okf_version: "0.2"、version、source、generated/verified、status、stale_after；index.md/log.md 为保留名；外部派生内容标 sources）。
* **NFR-2 语言与命名**：正文中文；文件名 kebab-case 纯英文（概念 00-08、示例 01-03、信源 01-04 编号前缀）。
* **NFR-3 链接规范**：交叉引用一律相对路径，禁止 file:/// 绝对路径；外部 URL 仅出现在正文表格/链接中。
* **NFR-4 编码**：UTF-8 无 BOM；通过 check-utf8。
* **NFR-5 可导航性**：全部新增 .md 可由 doc/index.md 经 toctree 链可达；每个含 toctree 的 index.md 收录其目录全部内容。
* **NFR-6 可构建性**：在隔离其他会话未跟踪 WIP 后的 doc/ 树上，Sphinx 构建（invoke build）成功。
* **NFR-7 环境约束**：验证命令在 awesome-okf-xs 子模块目录执行；优先 WSL/py314 环境（Windows 侧 PowerShell 亦可运行 python scripts/check-*.py）。

## 7. 约束、依赖、假设与开放问题

### 约束（Constraints）

* C1：awesome-okf-xs 是第一方 git 子模块；只在子模块内提交，主仓 gitlink 不动。
* C2：不得修改子模块 .agents/ 与 doc/conf.py；门禁以仓库现有 `scripts/check-toctrees.py`、`scripts/check-utf8.py` 为准。
* C3：提交信息遵循 Conventional Commits、中文 subject；git 文件参数使用正斜杠。
* C4：R 阶段已验证的信源 URL 与事实清单是唯一事实来源；未证实信息（如《汉志》小序卷数与著录卷数之差、《玉房秘诀》撰者题署、高罗佩中译本版次、部分现代书 ISBN）不得写成事实，须标注「待考」或不写。
* C5：内容表达受 §1 边界约束——学术、文献学、医学史语气；不出现露骨描写；历史性主张不作功效背书。

### 依赖（Dependencies）

* D1：R 阶段多源调研结果（出土整理本、《医心方》与辑佚本、医书与道藏、现代学术、在线信源矩阵），作为 facts 素材。
* D2：范本束 `think/daoyi/daoyi-reading/` 与 `think/laozi/boshu-reading/` 的结构、frontmatter 与 toctree 模式。
* D3：验证依赖子模块现有 invoke 任务与 scripts（gates.toctrees/gates.utf8/build）。

### 假设（Assumptions）

* A1：落位 `think/fangzhong/`（理由见 O1）；束名 `fangzhong-reading`，与 daoyi-reading/neijing-reading/boshu-reading 命名一致。
* A2：当前工作区存在其他会话未提交产物（2026-08-30 实测：daoyi 束 23 文件已 `git add` 暂存未提交、`bundles/index.md` 有未暂存改动、mozi 束 2 个概念文件未暂存改动、`tcm/` 与 think 下 buddhism/confucian/guiguzi/huangdi-neijing 四个未跟踪目录）；这些均不属于本任务。T0 重新实测并记录文件数；验证期间临时移出 doc/ 的目录验证后原样还原；暂存区中非本任务文件在提交前用 `git reset HEAD <path>` 取消暂存（不删除磁盘文件）；本任务提交时用 pathspec 精确暂存，提交清单恰为 fangzhong 新文件 + think/index.md + bundles/index.md。
* A3：古籍原文为公版内容；敦煌写本图像以 IDP 公开页面为限；现代学术著作仅引用书目信息与结论出处，不复刻版权段落。

### 开放问题（Open Questions）

* O1：落位选择——`think/fangzhong/`（推荐）还是 `tcm/fangzhong/`？推荐 think 的理由：房中在《汉志》虽列方技略，但其现代研究主体在道教史/社会史/文化史（高罗佩、李零、胡孚琛），且 think 域已收 huangdi-neijing、daoyi 等医学相关典籍分组，交叉引用最密；tcm 域（另一会话在建、未跟踪）定位中医临床典籍谱系。若用户偏好 tcm 域，执行时调整。
* O2：WIP 隔离目录在验证后还原即恢复其他会话在建状态——此为既有状态，本任务只保证**已提交树 + 本束新增**通过门禁；其他会话内容的提交/清理不在本任务范围。主仓 gitlink 是否跟进由用户后续决定。
* O3：现代西方性学（金赛、海蒂、福柯《性史》等）是否作为后续增量另立知识束，本束不覆盖，待用户后续指示。

## 8. 验收标准（Acceptance Criteria）

### rule 型（客观可判定）

| 编号 | 验收标准 |
|------|----------|
| AC-R1 | 束目录 `doc/bundles/think/fangzhong/fangzhong-reading/` 存在，含 index.md、facts.md、insights.md、log.md 及 concepts/（index.md + 00-08 共 9 篇）、examples/（index.md + 01-03 共 3 篇）、references/（index.md + 01-04 共 4 篇）；分组页 `doc/bundles/think/fangzhong/index.md` 存在。 |
| AC-R2 | 每个非保留 .md 均有 YAML frontmatter 且含非空 `type`；束根 type: OKF 且含 okf_version: "0.2"；分组页 type: group；概念/示例/信源页 type 分别为 Concept/Example/Reference。 |
| AC-R3 | 束根 toctree 收录 concepts/index、examples/index、references/index、facts、insights、log；三个子目录 index.md 的 toctree 完整收录各自全部内容页；think/fangzhong/index.md 收录 fangzhong-reading/index。 |
| AC-R4 | think/index.md 分组表含 fangzhong 行且 toctree 含 fangzhong/index；bundles/index.md frontmatter 计数与正文计数同步更新（在 T0 实测基线上净增 1 组 1 束），think 节束/组计数与分组表含 fangzhong，mermaid think 标签包含 fangzhong。 |
| AC-R5 | 在 WIP 临时移出/暂存区清理后，于 awesome-okf-xs 目录执行 `python scripts/check-toctrees.py` 退出码 0、`python scripts/check-utf8.py` 退出码 0、`invoke build` 构建成功（无 toctree/断链类错误）。 |
| AC-R6 | references 信源矩阵覆盖 FR-2 所列全部核心文献，每部至少 1 个 https 全文/图像 URL；全部 URL 不含 zysj.com.cn 域；平台缺陷有注明。 |
| AC-R7 | 托名层（素女/玄女/彭祖/容成）、辑佚本性质（医心方佚文/双梅景闇辑本非汉志原书）、内丹双修清修/阴阳两说均显式标注；现代低权威读物有警示条。 |
| AC-R8 | 束根 index.md 含显式学术用途与内容边界声明（非性教育/医学/行为指导，不收录露骨内容）。 |
| AC-R9 | 全部交叉引用为相对路径、无 file:///；正文为中文；新增文件名均为 kebab-case 英文加数字前缀。 |
| AC-R10 | facts.md 条目无因果推断词（「因为/导致/因此/所以/使得/从而」等），每条事实含可溯源信息（学者/书名/出版社/ISBN/URL/卷次）；未证实信息不写成事实；条数 ≥100。 |
| AC-R11 | 子模块内原子提交的文件清单恰为：新增 fangzhong 束全部文件 + think/fangzhong/index.md + think/index.md + bundles/index.md；不含任何其他会话产物（daoyi 暂存文件、mozi 改动、tcm/buddhism/confucian/guiguzi/huangdi-neijing 未跟踪目录）；commit message 为 Conventional Commits 中文 subject；主仓 git 状态无变更（gitlink 不动）。 |
| AC-R12 | 验证结束后临时移出的 WIP 目录原样还原至 doc/bundles/ 原位置（git status 仍显示为未跟踪，文件数量与内容不变）；被取消暂存的他会话文件恢复为暂存/未跟踪原状。 |
| AC-R13 | 内容边界核查：束内无露骨性行为操作性段落、无色情文学正文、无春宫图像、无功效背书表述。 |

### rubric 型（评分 0-5，≥4 为通过）

| 编号 | 评分维度 |
|------|----------|
| AC-Q1 | **信源权威性与可核验性**：5=每部核心文献同时给出权威纸本整理本（整理者/出版社/年份/ISBN）与已核验在线 URL，平台按识典＞维基文库＞ctext＞diancang/IDP 分级；3=多数有但分级不清；0=无信源或不可核验。 |
| AC-Q2 | **托名/辑佚/争议处理诚实度**：5=托名、辑佚层累、双修诠释争议全部标注年代证据与学界分歧，低权威读物显式警示，未证实说法不写入；0=真伪不辨、把辑本当原典。 |
| AC-Q3 | **零基础可执行性**：5=阅读路径分零基础/中医道医基础/研究型三档，每步给出具体书名+链接+时间计划；0=仅文献清单罗列。 |
| AC-Q4 | **六层覆盖完整性**：5=目录著录/出土/辑佚/医家/道教/文学与现代学术六层均有概念文档且层间交叉引用（马王堆↔医心方↔双梅景闇↔素问千金↔抱朴子内丹↔高罗佩学术）；0=缺层或层间无联系。 |
| AC-Q5 | **原文真实性与边界得体**：5=精选段落逐字与权威本一致（V 阶段抽查比对）、篇卷出处确切、配全文链接，且选段均为学术/养生/目录学内容、无露骨段落；0=仅有转述无原文，或原文错漏，或越界收录。 |
