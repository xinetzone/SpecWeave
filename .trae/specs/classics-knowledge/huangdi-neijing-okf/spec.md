---
title: "《黄帝内经》权威调研 → OKF wiki 知识包 - 产品需求文档"
status: "draft"
---

# 《黄帝内经》权威调研 → OKF wiki 知识包 - 产品需求文档

## Overview

- **Summary**：全面调研《黄帝内经》（《素问》《灵枢》各 81 篇）及相关权威著作（历代注本、现代整理本、高校教材、权威电子文本），以最权威、最真实的原文与解读为基础，在 awesome-okf-xs 文档库 `doc/bundles/think/` 域下新建 `huangdi-neijing` 分组，产出 `neijing-reading`（《黄帝内经》原典阅读教程）OKF 知识包，并更新全库索引。
- **Purpose**：用户需要一个可信的《黄帝内经》入门→进阶阅读教程：读哪个版本、怎么读、原文是什么、历代大家怎么注、现代教材怎么讲——全部溯源到权威信源，杜绝凭记忆写原文、凭印象讲版本。
- **Target Users**：想读《黄帝内经》原典的中文读者（零基础→进阶）、需要权威版本/注本导航的学习者、做中医典籍/中国哲学知识检索的 AI 智能体与研究者。

## Goals

- 在 `think/`（思想与理论）域新建 `huangdi-neijing/` 分组（与 `laozi/`、`psi/` 并列），含 `neijing-reading/` 综合阅读教程 bundle。
- 内容基于权威信源：原文以**中国哲学书电子化计划（ctext.org）/ 维基文库**电子文本逐字核对；版本事实以**人民卫生出版社、中华书局、文物出版社**等权威整理本及高校教材为准；历代注本信息经网络检索双信源核实。
- **8 篇名篇精读**（《素问》6 篇 + 《灵枢》2 篇）：核心段落原文逐字引用 + 注释 + 历代注家观点 + 现代教材解读。
- 完整覆盖《内经》理论体系概念地图：成书版本、全书结构、阴阳五行、藏象、经络、病因病机、诊法、治则治法、养生、五运六气、注本选用。
- 符合 OKF v0.2 规范；`invoke gates.all` 与 Sphinx 构建通过；索引计数同步更新。
- 方法论：seven-concepts 场景 4（知识沉淀）R→I→E 链路，V（对抗审查）映射 Spec Mode 独立 Review，C（原子提交）收尾。

## Non-Goals

- **不**全文收录 162 篇原文（约 15 万字，无必要且超出教程定位）；精读篇采用"核心段落全引 + 全篇结构导读"，其余篇目以短句引文覆盖。
- **不**为《黄帝内经太素》《难经》等相关著作建立独立 bundle；在 references/ 中登记信源并做导读。
- **不**逐字复制现代白话译文（现代译本受版权保护）；解读使用自有语言表述，观点归属到注家/教材。
- **不**提供任何医疗、诊疗、养生实践建议；全文以文献学/学术思想史立场撰写，bundle 内放置"非医疗建议"声明。
- **不**修改 awesome-okf-xs 的 `.agents/` 规范、`doc/conf.py` 构建配置；**不**更新 SpecWeave 主仓库 gitlink（由用户后续决定）。
- 不生成 PDF/DOCX 等衍生格式。

## Background & Context

- **目标库**：`projects/awesome-okf-xs/`（SpecWeave 第一方子模块，OKF v0.2 Sphinx 文档库），现有 286 束 / 32 组 / 13 域。
- **先例参照**：`doc/bundles/think/laozi/boshu-reading/`（帛书《老子》阅读教程）是同型先例——经典阅读教程 bundle，含 concepts/ 7 + examples/ 3 + references/ 4 + facts.md（45 条零推测事实）+ insights.md + log.md，R→I→E 流程生成。
- **门禁机制**：`scripts/check-toctrees.py` 强制校验 toctree 断链、内容可达性、目录清单一致性、bundle 根 index 必备；`invoke gates.all` = UTF-8 + toctrees；CI 在 GitHub Pages 构建前拦截。
- **frontmatter 规范**：`.agents/rules/frontmatter.md`——`type` 唯一必填；`sources` 溯源；`generated`/`verified` 信任字段；`status`/`stale_after` 生命周期；`okf_version: "0.2"` 仅允许出现在 bundle 根 index.md。
- **内容敏感度**：Public（公有领域典籍 + 公开出版物信息），标准工作流，存放 `doc/bundles/`。
- **用户决策（2026-08-30 澄清）**：① 单综合 bundle；② 8 篇名篇精读；③ 子模块内 Conventional Commits 原子提交；④ 文献与学术立场，分层标注原文/古注/现代解读。

## Functional Requirements

- **FR-1（目录结构）**：新建 `doc/bundles/think/huangdi-neijing/index.md`（分组 index）与 `doc/bundles/think/huangdi-neijing/neijing-reading/` bundle，含 `index.md`、`log.md`、`facts.md`、`insights.md`、`concepts/`（12 篇 + index）、`examples/`（9 篇 + index）、`references/`（4 篇 + index）。
- **FR-2（concepts/ 12 篇）**：00 为什么读《黄帝内经》；01 成书、流传与版本系统；02 全书结构与阅读路径；03 阴阳五行理论框架；04 藏象学说（五脏六腑、精气神）；05 经络腧穴与九针；06 病因病机（六淫七情、正邪虚实、病机十九条概说）；07 诊法（四诊合参、脉诊与色诊）；08 治则治法（治未病、治病求本、正治反治、标本先后）；09 养生学说（法于阴阳、和于术数、四季养生）；10 五运六气概要；11 历代注本系统与选用方法。
- **FR-3（examples/ 9 篇）**：8 篇精读 + 1 篇通读计划：01《素问·上古天真论》；02《素问·四气调神大论》；03《素问·阴阳应象大论》；04《素问·生气通天论》；05《素问·藏气法时论》；06《素问·至真要大论》（病机十九条）；07《灵枢·九针十二原》；08《灵枢·经脉》；09 通读计划与注本搭配。每篇精读含：篇章定位 → 核心段落**原文**（逐字核对）→ 词句注释 → 历代注家观点 → 现代教材解读 → 延伸阅读。
- **FR-4（references/ 4 篇）**：`editions.md`（现代权威整理本）；`commentaries.md`（历代注本信源登记：杨上善、王冰、马莳、张介宾、张志聪、黄元御、丹波元简/元坚等）；`modern-studies.md`（高校教材与工具书：王洪图《黄帝内经》、《内经讲义》、郭霭春《黄帝内经词典》、龙伯坚《黄帝内经概论》等）；`electronic-sources.md`（电子文本可信度分级：ctext.org、维基文库、国学导航、中医世家等）。
- **FR-5（facts.md / G1）**：F 编号事实清单（成书著录、版本年代、注本书目、篇卷结构、电子信源等），纯客观、无因果推断词，每条可外部核实或标注信源。
- **FR-6（insights.md / G2）**：四元组洞察（现象+根因+影响+建议）与知识地图，说明《内经》阅读的核心认知框架。
- **FR-7（原文真实性）**：所有直接引用的原文段落，必须逐字核对自 ctext.org 或维基文库《黄帝内经》电子文本；通假字/异体字/版本异文以信源为准并加注说明；**禁止凭记忆撰写原文**。
- **FR-8（索引同步）**：更新 `think/index.md`（分组表 + toctree + 域说明）与 `bundles/index.md`（计数 286→287 束、32→33 组；think 域 5→6 束、2→3 组；生态关系概览与推荐入门路径的 think 描述）。
- **FR-9（frontmatter 合规）**：全部非保留 .md 含可解析 YAML frontmatter 且 `type` 非空；content 文档标注 `sources`、`generated`/`verified`、`status: stable`、`stale_after`；`okf_version: "0.2"` 仅出现在 bundle 根 index.md。
- **FR-10（提交）**：在 awesome-okf-xs 子模块仓库内完成 Conventional Commits 原子提交（中文主体，`docs(think): ...`），提交前质量门全绿。

## Non-Functional Requirements

- **NFR-1 真实性（最高优先级）**：原文引文与权威电子文本逐字一致；版本/注本/出版社等事实经网络检索核实（关键事实双信源）；无法核实的内容标注为"待核"或不写。
- **NFR-2 层次分离**：原文（引用块）、古注（注明注家）、现代解读（注明教材/学者）、编者按四类内容明确区分，不混层。
- **NFR-3 安全边界**：bundle 首页与精读篇均含"本文为文献与学术研究内容，不构成医疗建议"声明；不出现具体疾病治疗方案指导。
- **NFR-4 规范一致性**：正文中文、文件名 kebab-case 纯英文、Markdown 交叉引用用相对路径（禁 `file:///`）、UTF-8 无 BOM。
- **NFR-5 可导航性**：所有内容文档经 toctree 链从 `doc/index.md` 可达；bundle 内快速导航与学习路径清晰。

## Constraints

- **Technical**：OKF v0.2；Sphinx + myst_parser 构建（裸日期由 conf.py 钩子处理，无需引号）；toctree 门禁四检查（断链/可达/清单一致/bundle 根 index）。
- **Business**：在子模块 `projects/awesome-okf-xs` 内工作（第一方子项目，允许子模块内开发与提交）；遵循子项目 AGENTS.md 轻量规范自治。
- **版权**：《黄帝内经》原文及历代古注为公有领域可引用；现代白话译文、现代学者著作内容不得逐字复制，只做书目登记与观点转述（标注归属）。
- **Dependencies**：网络可达 ctext.org、zh.wikisource.org 及书目检索站点；本地 Python 环境可运行 `invoke gates.all`；`invoke build` 依赖 doc 可选依赖，若缺失则以 `sphinx-build -b dummy` 或 gates 为底线验证。

## Assumptions

- 8 篇精读为"选段精读"：核心段落（名言、纲领性条文）原文全引并逐字核对，非全篇转录；用户已确认此深度。
- 分组命名 `huangdi-neijing`、bundle 命名 `neijing-reading`（与 `laozi/boshu-reading` 同构）。
- 子模块当前工作树干净（已核实），提交不涉及主仓库 gitlink 变更。

## Acceptance Criteria

### AC-1: bundle 结构与文件齐全
- **Type**: `rule`
- **Given**: 实施完成
- **When**: 检查 `doc/bundles/think/huangdi-neijing/` 目录树
- **Then**: 存在 group index、bundle index/log/facts/insights、concepts/ 12 篇 + index、examples/ 9 篇 + index、references/ 4 篇 + index
- **Pass Condition**: 文件清单与 FR-1/2/3/4 完全一致，无多余孤立 .md
- **Evidence**: 目录列表 + toctree 门禁输出

### AC-2: 质量门全绿
- **Type**: `rule`
- **Given**: 全部文档落盘
- **When**: 在子模块根运行 `invoke gates.all`
- **Then**: UTF-8 检查与 toctree 检查均通过，退出码 0
- **Pass Condition**: 零断链、零不可达内容、零缺失条目、零缺失 index、零编码错误
- **Evidence**: 命令输出文本

### AC-3: Sphinx 构建通过
- **Type**: `rule`
- **Given**: 质量门通过
- **When**: 运行 `invoke build`（或依赖缺失时 `sphinx-build -b dummy -E doc _build/dummy`）
- **Then**: 构建成功，无与新增文档相关的警告/错误
- **Pass Condition**: 构建退出码 0，无新增 toctree/frontmatter 警告
- **Evidence**: 构建输出

### AC-4: frontmatter 合规
- **Type**: `rule`
- **Given**: 所有新建 .md
- **When**: 检查每个非保留文件首行 YAML 块
- **Then**: 每个 content 文档 `type` 非空；bundle 根 index 含 `okf_version: "0.2"` 且其他文件不含该字段；content 文档含 sources/generated/verified/status
- **Pass Condition**: 逐文件检查全部满足
- **Evidence**: grep/人工检查记录

### AC-5: 原文引文逐字真实
- **Type**: `rule`
- **Given**: examples/ 8 篇精读与 concepts/ 中所有原文引用块
- **When**: V 阶段独立审查者从每篇精读抽取 ≥2 段原文（总计 ≥20 段），与 ctext.org/维基文库对应篇目逐字比对
- **Then**: 零字差异（异体字/通假字差异须有显式注释说明）；每段原文可追溯到具体电子信源
- **Pass Condition**: 抽查 20+ 段，差异段数 = 0（有注释说明的版本异文不计差异）
- **Evidence**: review.md 抽查记录表（篇目、段落、信源 URL、比对结果）

### AC-6: facts.md 零推测且可溯源
- **Type**: `rule`
- **Given**: facts.md 全部 F 编号条目
- **When**: G1 检查——扫描因果推断词（"因为/导致/所以/为了/使得"等）并逐条核对信源
- **Then**: 无因果推断词；书目/版本/年代类事实均有 references 或外部信源支撑
- **Pass Condition**: 因果词命中 0；关键事实（出版社、年代、注家）双信源核实率 100%
- **Evidence**: facts.md + review.md 核查记录

### AC-7: 索引计数与导航一致
- **Type**: `rule`
- **Given**: 索引更新完成
- **When**: 检查 `bundles/index.md` 与 `think/index.md`
- **Then**: total_bundles=287、groups=33、domains=13；think 域 6 束 3 组；think 分组表含 huangdi-neijing 行；两文件 toctree 含新条目
- **Pass Condition**: 计数与实际目录一致，toctree 无断链
- **Evidence**: 文件内容 + gates.toctrees 输出

### AC-8: 教程实用性
- **Type**: `rubric`
- **Dimension**: 零基础读者可据此完成"选版本→按路径读→用注本→查信源"全流程
- **Scale**: 1-5
- **Anchors**: 1 = 只有知识点罗列，无阅读路径；3 = 有路径但版本/注本建议笼统；5 = 路径清晰、注本分级具体到书名、通读计划可执行
- **Pass Threshold**: >= 4
- **Evidence**: concepts 02/11、examples 09、references 四份文档评审

### AC-9: 解读层次与学术严谨
- **Type**: `rubric`
- **Dimension**: 原文/古注/现代解读/编者按分层清晰度 + 观点归属准确性 + 无医疗建议越界
- **Scale**: 1-5
- **Anchors**: 1 = 原文与解读混写、无归属；3 = 基本分层但部分观点无归属；5 = 四层清晰、所有非通识观点均归属、声明到位
- **Pass Threshold**: >= 4
- **Evidence**: 精读篇与概念篇抽查评审

### AC-10: 原子提交完成
- **Type**: `rule`
- **Given**: 审查通过、整改完成
- **When**: 在子模块仓库执行 git 提交
- **Then**: 单次 Conventional Commits 提交（`docs(think): ...`，中文主体说明 R→I→E→V 过程与计数变更），工作树干净
- **Pass Condition**: `git log` 可见新提交、`git status` 干净
- **Evidence**: git log/status 输出

## Open Questions

- 无（范围、深度、提交方式、立场均已由用户 2026-08-30 澄清确认）。