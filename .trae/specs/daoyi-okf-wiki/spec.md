---
type: spec
title: 道医著作权威调研 OKF wiki 教程（think/daoyi/daoyi-reading 知识束）
spec_mode: Specify
method: seven-concepts-cmd（场景4 知识沉淀，链路 R→F→I→E→V→C）
session: sc-20260830-daoyi-okf
content_sensitivity: Public（公版古籍 + 公开出版物信息）
created: 2026-08-30
status: awaiting-approval
---

# 道医著作权威调研 OKF wiki 教程 — 需求规格

## 1. 问题陈述（Problem）

道医（道家/道教医学传统）相关著作卷帙浩繁且分散在三个文献世界中：中医元典（《素问》《灵枢》《难经》《神农本草经》《伤寒杂病论》）、道藏医书与养生内丹文献（《抱朴子内篇》《黄庭经》《周易参同契》《悟真篇》《云笈七签》《养性延命录》等）、出土方技文献（马王堆、张家山、天回老官山、敦煌医书）。普通读者与研究者面临三重障碍：

1. **信源分散、版本难辨**：同一部经典存在道藏本、四库本、当代整理本、网络 OCR 本等多重文本形态，在线平台质量参差（已发现 zysj.com.cn 中医世家站点遭博彩 SEO 污染；ctext《本草纲目》OCR 乱码不可用；diancang《云笈七签》为 120/121 卷系统，与道藏 122 卷本有卷次差异）。
2. **真伪层累、托名成风**：道医文献中托名上古圣贤（华佗、扁鹊、陶弘景、吕祖）的现象普遍，《中藏经》《辅行诀脏腑用药法要》《医道还元》《扁鹊心书》《华佗神医秘传》等书的成书年代与真伪在学界存在分歧；坊间亦有学术权威性低的读物（如祝守明《道医讲义》、王爱品《道医论》）被网络当作权威引用。
3. **缺乏可信赖的教程式入口**：现有资料要么是学术专著（盖建民《道教医学》等，面向研究者），要么是门户罗列的典籍清单（无阅读路径、无版本指导、无辨伪提示），读者无法回答“从哪部开始读、读哪个版本、在线全文去哪里找、哪些说法不可信”。

目标库 `awesome-okf-xs` 的 `doc/bundles/think/`（思想与理论域）已有 psi（4 束）、laozi（1 束）两个已注册分组，尚无覆盖道医/中医经典的知识束。

## 2. 用户与使用场景（Users）

* **零基础传统文化读者**：对道医、养生、中医经典有兴趣，需要一条“从哪本书开始、读哪个版本、每天读什么”的可执行路径。

* **有中医基础的读者/中医学生**：已读教材或《中医基础理论》，希望回到原典并理解医学与道家思想的源流关系，需要权威点校本指南与原典全文入口。

* **人文研究者（道教史/医学史/文献学）**：需要道医学术框架（盖建民、胡孚琛、姜生、林富士等）、出土方技文献谱系、道藏医书目录与辨伪研究线索的可信索引。

* **OKF 知识包读者**：在 awesome-okf-xs 文档站中按域导航时，期望 think 域能提供与 boshu-reading 同构的“权威原文 + 解读 + 信源”阅读教程。

## 3. 目标（Goals）

* **G1**：在 `doc/bundles/think/daoyi/` 下新建分组与单束总览教程 `daoyi-reading`，以 OKF v0.2 知识包形态（concepts/examples/references 三层 + facts/insights/log）系统呈现广义道医著作的权威原文与解读。

* **G2**：内容覆盖用户已拍板的**广义道医六层**：①中医元典的道家根源；②道门医家（葛洪、陶弘景、孙思邈）；③道藏医书与养生内丹文献；④出土方技文献；⑤医道会通流派；⑥现代学术研究。

* **G3**：每部核心经典提供“精选段落原文（标注篇卷出处）+ 已实际核验的在线全文链接 + 权威纸本点校本指南”三类信息，不系统收录全书全文。

* **G4**：真伪争议一律两说并陈（代表学者、出处、年代证据），低权威读物显式警示，污染信源禁用。

* **G5**：通过 awesome-okf-xs 全部导航与构建质量门（toctrees/utf8/build），并在子模块内以 Conventional Commits 原子提交。

## 4. 非目标（Non-Goals）

* **N1**：不系统收录/复刻任何典籍全文（只做精选段落 + 全文信源链接）。

* **N2**：不提供任何医疗、诊疗、用药、练功建议；束内显式声明文化与文献研究用途。

* **N3**：不新建 `tcm/` 顶级域；不实现历史 spec（create-tcm-classics-okf-wiki、huangdi-neijing-okf）规划的多束结构——《黄帝内经》等元典内容在本束概念层覆盖并交叉引用，不另建束。

* **N4**：不修改 awesome-okf-xs 的 `.agents/`、`doc/conf.py`、scripts 等基建文件。

* **N5**：不处理、不提交、不删改其他会话遗留在工作区的未跟踪在建目录（`doc/bundles/tcm/`、`doc/bundles/think/confucian/`、`doc/bundles/think/guiguzi/`、`doc/bundles/think/legalism/`、`doc/bundles/think/mozi/`）；验证期间临时隔离、验证后原样还原。

* **N6**：不变更主仓（SpecWeave）的 gitlink 与主仓任何文件；提交仅发生在 awesome-okf-xs 子模块仓库内。

* **N7**：不收录佛教医方明、藏医等非道医体系（仅在边界处提及）。

## 5. 功能需求（Functional Requirements）

### FR-1 知识包结构与导航

* F1.1 新建分组页 `think/daoyi/index.md`（type: group），含分组说明、知识包列表表、toctree 收录 `daoyi-reading/index`。

* F1.2 新建束 `think/daoyi/daoyi-reading/`：束根 `index.md`（type: OKF，含快速导航、快速开始、分档学习路径、非医疗声明、toctree）、`facts.md`、`insights.md`、`log.md`，以及 `concepts/`、`examples/`、`references/` 三个子目录（各含 index.md）。

* F1.3 概念层覆盖广义道医六层：道医概念界定与学术框架、医道同源与发展史、中医元典的道家根基、道门医家（葛洪/陶弘景/孙思邈）、道藏医书与养生类书、内丹道经与医理、出土方技文献、医道会通流派、辨伪与信源分级（共 9 篇，00-08 编号）。

* F1.4 示例层 3 篇：原典选读（精选段落+篇卷出处+全文链接）、分档阅读路径（零基础/中医基础/研究型三档，含周计划）、现代研究与静功疗养入门（含权威版本指南）。

* F1.5 信源层 4 篇：在线古籍平台信源矩阵（典籍×平台 URL 表）、权威纸本点校本（人卫中医古籍整理丛书/中华书局道教典籍选刊/道藏三家本与中华道藏/出土整理本）、现代学术研究文献、辨伪与争议文献登记。

* F1.6 更新 `think/index.md`（分组表、域说明、toctree）与 `bundles/index.md`（frontmatter 计数 total\_bundles 286→287、groups 32→33、domains 13 不变；正文计数、think 节“5 束 · 2 组”→“6 束 · 3 组”、两处 mermaid think 标签、think 分组表）。

### FR-2 内容权威性与真实性

* F2.1 facts.md 登记 R 阶段（三路调研）已取证的事实：学术著作（书名/作者/出版社/年份/ISBN）、人物年代、道藏出处（涵芬楼册次/中华道藏册次）、出土文献发掘与整理信息、在线信源 URL（平台优先级：识典＞维基文库＞ctext 主库＞diancang）。

* F2.2 每部核心经典（《素问》《灵枢》《难经》《神农本草经》《伤寒论》《金匮要略》《肘后备急方》《备急千金要方》《千金翼方》《外台秘要》《本草纲目》《抱朴子内篇》《周易参同契》《黄庭经》《悟真篇》《云笈七签》及马王堆/张家山/天回/敦煌出土文献）至少登记 1 个已核验可访问的在线全文 URL，并给出权威纸本点校本信息。

* F2.3 精选原文段落须逐字依据权威本（ctext/识典/维基文库已核验文本），标注确切篇卷出处；每段配全文链接。

* F2.4 辨伪文献（《中藏经》《辅行诀脏腑用药法要》《医道还元》《扁鹊心书》《华佗神医秘传》）呈现成书年代证据（避讳字、著录、流传史）与学界两说（主真/主伪代表学者与论著）。

* F2.5 低权威读物（祝守明《道医讲义》、王爱品《道医论》等）显式标注“学术权威性低/民间自修读物”警示；zysj.com.cn 全站禁用；diancang《云笈七签》卷次差异、维基文库《伤寒论》未校完页面等平台缺陷如实注明。

* F2.6 束根与示例页含非医疗用途声明（文化与文献研究，不构成诊疗/用药/练功建议）。

### FR-3 七概念工作流产物

* F3.1 facts.md：事实按前缀分组编号（AX 学术/CAN 医经/DAO 道藏/EXC 出土/FLW 流派/FRG 辨伪/SRC 信源），纯客观陈述、无因果推断词（G1 质量门）。

* F3.2 insights.md：每条洞察遵循四元组（陈述/证据/反常识/行动），覆盖道-理-术三层、医道同源、吉元三圆模型、文献层累与托名规律、信源分级原则（G2 质量门）。

* F3.3 log.md：记录创建日期、结构、事实条数与方法论过程。

## 6. 非功能需求（Non-Functional Requirements）

* **NFR-1 规范合规**：全部 .md 符合 OKF v0.2（frontmatter 必填非空 type；束根带 okf\_version: “0.2”、version、source、generated/verified、status、stale\_after；index.md/log.md 为保留名；外部派生内容标 sources）。

* **NFR-2 语言与命名**：正文中文；文件名 kebab-case 纯英文（概念 00-08、示例 01-03、信源 01-04 编号前缀）。

* **NFR-3 链接规范**：交叉引用一律相对路径，禁止 file:/// 绝对路径；外部 URL 仅出现在正文表格/链接中。

* **NFR-4 编码**：UTF-8 无 BOM；通过 check-utf8。

* **NFR-5 可导航性**：全部新增 .md 可由 doc/index.md 经 toctree 链可达；每个含 toctree 的 index.md 收录其目录全部内容；束根目录含 index.md。

* **NFR-6 可构建性**：在隔离其他会话未跟踪 WIP 后的 doc/ 树上，Sphinx 构建（invoke build）成功。

* **NFR-7 环境约束**：验证命令在 awesome-okf-xs 子模块目录执行；优先 WSL/py314 环境（Windows 侧 PowerShell 亦可运行 python scripts/check-\*.py）。

## 7. 约束、依赖、假设与开放问题

### 约束（Constraints）

* C1：awesome-okf-xs 是第一方 git 子模块；只在子模块内提交，主仓 gitlink 不动。

* C2：不得修改子模块 .agents/ 与 doc/conf.py；门禁以仓库现有 `scripts/check-toctrees.py`、`scripts/check-utf8.py` 为准。

* C3：提交信息遵循 Conventional Commits、中文 subject；git 文件参数使用正斜杠。

* C4：R 阶段已验证的信源 URL 与事实清单是唯一事实来源；未证实信息（如“陈撄宁《道教与养生》华文出版社1989”、潘毅书年份、《道医集成》版次信息、《汉志》房中家卷数）不得写成事实，须标注“未获证实/待考”或不写。

### 依赖（Dependencies）

* D1：R 阶段三路调研结果（学术体系、17 部经典在线信源矩阵、出土与养生文献）已完成，作为 facts 素材。

* D2：范本束 `think/laozi/boshu-reading/` 的结构与 frontmatter 模式。

* D3：验证依赖子模块现有 invoke 任务与 scripts（gates.toctrees/gates.utf8/build）。

### 假设（Assumptions）

* A1：当前已提交基线（286 束/32 组/13 域，think 5 束 2 组）门禁为通过状态（最近提交 d67de37b 声明 gates.all 通过）；磁盘上 5 个未跟踪 WIP 目录（tcm/、think/confucian、think/guiguzi、think/legalism、think/mozi）为其他中断会话的在建骨架，不属于本任务，验证期间临时移出 doc/、验证后原样还原，且不进入本任务提交清单。

* A2：新增计数算术：total\_bundles 286→287、groups 32→33、domains 13 不变、think 5 束 2 组→6 束 3 组。

* A3：道藏/古籍原文为公版内容；现代学术著作仅引用书目信息与结论出处，不复刻版权段落。

### 开放问题（Open Questions）

* O1：WIP 隔离目录在验证后还原即恢复“门禁失败”基线状态（其他会话的在建内容所致）——此为既有状态，本任务只保证**已提交树 + 本束新增**通过门禁；是否由用户后续清理/完成那些会话，不在本任务范围。

* O2：主仓 gitlink 是否、何时跟进更新，由用户后续决定。

## 8. 验收标准（Acceptance Criteria）

### rule 型（客观可判定）

| 编号     | 验收标准                                                                                                                                                                                                                                        |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-R1  | 束目录 `doc/bundles/think/daoyi/daoyi-reading/` 存在，含 index.md、facts.md、insights.md、log.md 及 concepts/（index.md + 00-08 共 9 篇）、examples/（index.md + 01-03 共 3 篇）、references/（index.md + 01-04 共 4 篇）；分组页 `doc/bundles/think/daoyi/index.md` 存在。 |
| AC-R2  | 每个非保留 .md 均有 YAML frontmatter 且含非空 `type`；束根 type: OKF 且含 okf\_version: “0.2”；分组页 type: group；概念/示例/信源页 type 分别为 Concept/Example/Reference。                                                                                                 |
| AC-R3  | 束根 toctree 收录 concepts/index、examples/index、references/index、facts、insights、log；三个子目录 index.md 的 toctree 完整收录各自全部内容页；think/daoyi/index.md 收录 daoyi-reading/index。                                                                           |
| AC-R4  | think/index.md 分组表含 daoyi 行且 toctree 含 daoyi/index；bundles/index.md frontmatter 为 total\_bundles: 287、groups: 33、domains: 13，正文计数同步，think 节标题为“6 束 · 3 组”且分组表含 daoyi 行，两处 mermaid 的 think 标签包含 daoyi。                                       |
| AC-R5  | 在 5 个 WIP 目录临时移出 doc/ 后，于 awesome-okf-xs 目录执行 `python scripts/check-toctrees.py` 退出码 0、`python scripts/check-utf8.py` 退出码 0、`invoke build` 构建成功（无 toctree/断链类错误）。                                                                           |
| AC-R6  | references 信源矩阵覆盖 FR-2 所列全部核心经典，每部至少 1 个 https 全文 URL；全部 URL 不含 zysj.com.cn 域；平台缺陷（diancang 卷次差异、维基伤寒论未校完、ctext 本草纲目 OCR）有注明。                                                                                                               |
| AC-R7  | 《中藏经》《辅行诀脏腑用药法要》《医道还元》《扁鹊心书》《华佗神医秘传》五书均有两说并陈的辨伪条目（含年代证据与双方代表学者/论著）；祝守明《道医讲义》、王爱品《道医论》带学术权威性低警示。                                                                                                                                             |
| AC-R8  | 束根 index.md 含显式非医疗用途声明。                                                                                                                                                                                                                     |
| AC-R9  | 全部交叉引用为相对路径、无 file:///；正文为中文；新增文件名均为 kebab-case 英文加数字前缀。                                                                                                                                                                                    |
| AC-R10 | facts.md 条目无因果推断词（“因为/导致/因此/所以/使得/从而”等），每条事实含可溯源信息（学者/书名/出版社/ISBN/URL/卷次）；未证实信息不写成事实。                                                                                                                                                       |
| AC-R11 | 子模块内原子提交的文件清单恰为：新增 daoyi 束全部文件 + think/daoyi/index.md + think/index.md + bundles/index.md；不含任何 WIP 目录文件；commit message 为 Conventional Commits 中文 subject；主仓 git 状态无变更（gitlink 不动）。                                                          |
| AC-R12 | 验证结束后 5 个 WIP 目录原样还原至 doc/bundles/ 原位置（子模块 git status 仍显示为未跟踪，文件数量与内容不变）。                                                                                                                                                                   |

### rubric 型（评分 0-5，≥4 为通过）

| 编号    | 评分维度                                                                                                                  |
| ----- | --------------------------------------------------------------------------------------------------------------------- |
| AC-Q1 | **信源权威性与可核验性**：5=每部核心经典同时给出权威纸本点校本（整理者/出版社/年份/ISBN）与已核验在线全文 URL，平台按识典＞维基文库＞ctext＞diancang 分级；3=多数有但分级不清；0=无信源或信源不可核验。 |
| AC-Q2 | **真伪与争议处理诚实度**：5=托名/辑佚/扶乩/近代伪书全部标注年代证据与学界分歧，低权威读物显式警示，未证实说法不写入；0=真伪不辨、照单全收。                                           |
| AC-Q3 | **零基础可执行性**：5=阅读路径分零基础/中医基础/研究型三档，每步给出具体书名+链接+时间计划，读者可照做；0=仅文献清单罗列。                                                   |
| AC-Q4 | **广义道医六层覆盖完整性**：5=六层均有概念文档覆盖且层间交叉引用（元典道家根源↔道门医家↔道藏养生↔出土文献↔医道流派↔现代研究）；0=缺层或层间无联系。                                      |
| AC-Q5 | **原文真实性**：5=精选段落逐字与权威在线本一致（V 阶段抽查比对），篇卷出处确切，配全文链接；0=仅有转述无原文，或原文有错漏。                                                   |

