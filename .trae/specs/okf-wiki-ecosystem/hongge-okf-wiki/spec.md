---
title: "红歌教学知识包（OKF wiki 教程）- Product Requirement Document"
status: "draft"
---

***

title: 红歌教学知识包 OKF wiki 教程 PRD
session: sc-20260902-hongge-okf-wiki
methodology: seven-concepts-cmd（R→F→I→V→A→C）
source: 私域聊天截图（一线音乐教师需求，已脱敏）
sensitivity: public（产出物为公开教育内容，来源私域已脱敏，束内不含个人姓名）
created: 2026-09-02
-------------------

# 红歌教学知识包（OKF wiki 教程）- Product Requirement Document

## Overview

- **Summary**：在 awesome-okf-xs 文档库 `yishu/`（艺术）域下新建 **红歌教学分组（hongge）**，内含一个教学型知识包 `hongge-pedagogy`（红歌教学教程），以 OKF v0.2 bundle 三层结构（concepts/examples/references）+ facts.md 事实清单 + insights.md 架构洞察组织，覆盖图片讨论中提出的四大需求：**曲谱库、红歌赏析（适合教学）、歌谱、手势与声乐教学结合**。

- **Purpose**：一线音乐教师希望建设一个"红色歌曲"教学知识库——经典红色革命歌曲与新时代主旋律（中国梦类）歌曲的教学型赏析 + 歌谱资源 + 柯尔文手势/柯达伊教学法与声乐训练的课堂结合。本知识包把该需求落地为可照做的中文教程：教师拿到即可备课、组课、搭建合规曲谱库。

- **Target Users**：中小学/中职/老年大学音乐教师、合唱指导教师、师范生、音乐教研员；次级读者为组织红歌合唱活动的政工/工会干部与自学红歌演唱的爱好者。

## Goals

- G1：新建 `doc/bundles/yishu/hongge/` 分组与 `hongge-pedagogy/` 知识包，结构完全对齐 OKF v0.2 与同域先例束 `meitong-yanyin-pedagogy`。

- G2：**曲谱库**：讲清简谱/五线谱识读、群众歌曲曲式特征、曲谱资源信源与**版权合规边界**，给出可直接套用的曲谱库目录模板。

- G3：**教学型赏析**：提供"背景→曲式→旋律→歌词→演唱处理→教学要点"六步赏析框架，并用框架完成革命时期、建设/改革时期、新时代三个时段代表曲目的赏析示范。

- G4：**手势×声乐教学**：系统讲解柯尔文手势（Curwen hand signs）/柯达伊教学法的手势—音高映射与课堂用法，与呼吸、咬字、合唱编排等声乐基础结合，并与 `vocal/meitong-yanyin-pedagogy` 束交叉引用。

- G5：facts.md 事实清单零推测、信源 URL 逐条内嵌、单源/存疑显式标注、含 P0 双源核验表（G1 质量门）。

- G6：全束通过 awesome-okf-xs 三门质量门（utf8/toctrees/bundles）与定向 sphinx dummy 构建（0 error）。

- G7：Seedream 生成分组装饰封面（group hero）1 张 + 知识包封面 1 张，落位 `doc/_static/bundles/yishu/hongge/images/` 并在索引页正确引用。

## Non-Goals (Out of Scope)

- 不复制/转录任何仍在著作权保护期内的完整歌谱与歌词全文（只做识读教学、公版示例片段与正版信源指引）。

- 不做音频/视频资源托管，不开发任何软件应用（纯 Markdown 知识包）。

- 不做政治宣传文案；全部内容为学术性、教学法性质的客观知识整理，史实以公开权威信源为准。

- 不新建第二个知识包（如"柯达伊教学法全论"），手势教学以"服务红歌课堂"为边界。

- 不执行 git commit / push（C 阶段交付物为工作树文件 + 门控全绿；提交需用户显式指令）。

- 不修改 `projects/awesome-okf-xs/.agents/` 子项目规范文件。

## Background & Context

- 需求来源为私域聊天截图（2026-09-02）：一位音乐教师提出"做一个有关歌曲曲谱库的知识库"，范围经追问收敛为"红色歌曲：经典红色革命歌曲和新时代类似中国梦的歌曲"，并明确"这些红歌的赏析，适合教学的赏析，还要有歌谱"，以及"手势和声乐教学的结合"。产出物中不得出现聊天中的个人姓名与原文。

- 同域先例：`doc/bundles/yishu/vocal/meitong-yanyin-pedagogy/`（美通唱法与咽音体系教学教程）即由 seven-concepts-cmd 链路生成，frontmatter 形态（`type: OKF`、`generated: agent:seven-concepts-cmd`、`verified: process:seven-concepts-v`、facts.md 81 条 + P0 表、insights.md 六条四元组）为本束直接模板。

- 配图先例：`doc/bundles/jishu/gui/index.md` 使用 Seedream 生成的 `/_static/bundles/jishu/gui/images/gui-group-hero.jpg` 分组封面。

- 门控命令须在 **py314 conda 环境**下于子项目根目录执行：`conda run --no-capture-output -n py314 invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8`；定向构建：`python -m sphinx -b dummy -E doc .temp/dummy <显式文件列表>`。

- 共享索引（`bundles/index.md`、`yishu/index.md`）存在并行会话写入漂移：计数一律以门控重算为准，禁止手填；注册编辑后须立即核验落盘。

- 七概念链路（本次场景=创新突破×知识沉淀混合）：**R**（双路 Web 信源调研→facts.md）→ **F**（第一性原理推导束结构）→ **I**（insights.md 四元组洞察）→ **V**（四视角对抗审查+修正）→ **A**（原子化文件成束）→ **C**（门控交付，提交待令）。

## Functional Requirements

- **FR-1 分组与知识包骨架**：创建 `yishu/hongge/index.md`（type: group，含分组导航表、知识地图 mermaid、toctree、hero 图）与 `yishu/hongge/hongge-pedagogy/` 束根 `index.md`（type: OKF，okf\_version 0.2，快速导航表、读者路径 mermaid、toctree 覆盖 concepts/examples/references/facts/insights）。

- **FR-2 事实清单（R 阶段）**：`facts.md` 登记 ≥60 条零推测事实，分轨：①红歌概念与分期史 ②代表曲目创作档案（词曲作者、年份、出处、首演/流传）③课标与教材（义务教育艺术课程标准 2022 年版等）④柯尔文手势/柯达伊教学法史实 ⑤简谱/五线谱与群众歌曲曲式 ⑥著作权法与曲谱版权信源；每条内嵌信源 URL、标注信源层级，单源/存疑显式标注；文末附 P0 双源核验表。

- **FR-3 架构洞察（I 阶段）**：`insights.md` 产出 ≥5 条四元组洞察（现象/根因/影响/建议，回指 F 编号），覆盖：教学闭环（赏—谱—声—教）、曲谱库瓶颈在版权合规而非获取、手势是音高内化脚手架、群众歌曲曲式简单性是教学资产、红歌的时代分层与"赏析≠讲故事"。

- **FR-4 概念文档 10 篇**：`concepts/00~09`（00 入门地图/读者画像/使用法；01 红歌界定与分期；02 曲谱基础：简谱五线谱与群众歌曲曲式；03 教学型赏析六步框架；04 革命时期代表曲目赏析；05 建设与改革时期代表曲目赏析；06 新时代主旋律曲目赏析；07 柯尔文手势与柯达伊教学法；08 红歌演唱的声乐基础与合唱编排——交叉引用 vocal 束；09 曲谱库建设与版权合规 + 课堂教案设计法）。

- **FR-5 实践示例 3 篇**：`examples/01` 单曲目完整教案（以《歌唱祖国》为示范：手势练声→赏析→视唱→演唱处理→作业）；`examples/02` 曲谱库搭建指南（目录模板、资源信源清单、版权自查表）；`examples/03` 学期 16 周教学路线图（手势音阶→经典曲目→合唱汇报）。

- **FR-6 信源参考 3 篇**：`references/01` 课标与教材信源（课程标准、人音版/人教版教材、教师用书）；`references/02` 曲谱与音频正版信源（人民音乐出版社、正版曲谱平台、公版判定、馆藏）；`references/03` 红歌史料与教学法信源（聂耳/冼星海等权威史料、柯达伊中文文献、柯尔文手势权威来源）。

- **FR-7 配图**：Seedream 生成 2 张装饰性封面（分组 hero、知识包封面），暖色纸感/正能量但不庸俗的审美，落位 `doc/_static/bundles/yishu/hongge/images/`，在 group index 与 bundle index 顶部以 MyST 图片语法引用（绝对路径 `/_static/...`）。

- **FR-8 共享索引注册**：更新 `yishu/index.md`（分组表新增 hongge 行、toctree 增 `hongge/index`、描述计数更新）与 `bundles/index.md`（frontmatter total\_bundles/groups、yishu 域节标题计数、分组表新增行、生态概览 mermaid yishu 行）五面对账。

- **FR-9 对抗审查（V 阶段）**：四视角审查（魔鬼代言人/新人/老板/未来）输出 ≥5 条具体意见并至少采纳 2 条修正落盘；重点攻击史实准确性、版权合规、零基础可用性、课标对齐。

## Non-Functional Requirements

- **NFR-1 事实可信**：所有人物、年份、出处、法条、课标条目必须有可访问 URL 信源；党媒/出版社/政府网/学术为一级信源，百科/自媒体仅作线索并标注；P0 事实双源核验。

- **NFR-2 门控全绿**：`gates.utf8`、`gates.toctrees`（无断链、无孤立文档、束根 toctree 全覆盖）、`gates.bundles`（束/组/域三角计数一致）全部通过；定向 sphinx dummy 构建 0 error、0 警告（与新增文件相关）。

- **NFR-3 规范一致**：每个非保留 .md 含可解析 YAML frontmatter 且有非空 `type`；`okf_version: "0.2"` 仅出现在束根 index.md；文件名 kebab-case 英文；正文中文；相对路径交叉引用，禁止 `file:///`。

- **NFR-4 安全红线**：不出现政治差错（曲目名称、词曲作者、历史事件表述以权威信源为准）；不提供侵权曲谱获取途径；frontmatter 双引号内不嵌 ASCII 双引号。

- **NFR-5 教学可用性**：概念文档每篇含"学完能做什么"；examples 可直接打印用于备课；柯尔文手势七个音的手势描述准确（do-re-mi-fa-sol-la-ti 空间位置与手型），AI 不生成手势示意图（避免错误动作误导），手势内容用文字+表格精确描述并链权威信源。

- **NFR-6 脱敏**：全束不出现需求来源中的个人姓名、聊天原文、微信群信息。

## Constraints

- **Technical**：Markdown + MyST（myst\_parser）+ Sphinx；YAML frontmatter；mermaid 图；图片存 `doc/_static/`；Windows 环境，命令经 PowerShell + py314 conda；子项目为 git submodule（不在其中执行 commit/push）。

- **Business**：内容属公开教育/教材范畴，须符合中小学音乐教学导向；著作权法合规（词、曲作者权利保护期为作者终生及死后 50 年）。

- **Dependencies**：Seedream 配图（GenerateImage 工具）；WebSearch/WebFetch 信源核验；现有束 `meitong-yanyin-pedagogy` 作交叉引用对象；门控脚本 check-toctrees.py / check-bundles-index.py / check-utf8.py。

## Assumptions

- A1：红歌教学归属 `yishu` 域、新建 `hongge` 分组（而非放入 `vocal` 声乐组）——因范围含曲谱/赏析/教学法，大于声乐技术；组名用拼音 `hongge` 与 `liaoyu`/`vocal` 命名风格一致。

- A2：知识包定名 `hongge-pedagogy`（红歌教学教程），与 `meitong-yanyin-pedagogy` 平行。

- A3：曲目赏析示范选曲为公版或教学使用最广泛的代表曲目（《义勇军进行曲》《歌唱祖国》《我的祖国》《没有共产党就没有新中国》《唱支山歌给党听》《我和我的祖国》《不忘初心》等），仅给片段级谱例与正版指引。

- A4：门控计数以实施时 gates 重算为准（并行会话可能使 total\_bundles 基线漂移）。

- A5：用户需要 2 张 Seedream 装饰封面；如需更多插图后续追加。

## Acceptance Criteria

### AC-1: 知识包骨架与注册完整

- **Given**：awesome-okf-xs 仓库当前状态

- **When**：实施完成并运行 `invoke gates.bundles` 与 `invoke gates.toctrees`

- **Then**：`yishu/hongge/hongge-pedagogy/` 被识别为 1 个新束、`yishu/hongge/` 为 1 个新组；总索引五面（frontmatter/计数行/域节/分组表/toctree）计数一致；无断链、无孤立文档

- **Verification**: `programmatic`

### AC-2: 事实清单可信可溯

- **Given**：facts.md

- **When**：抽查任意 10 条事实

- **Then**：每条含信源 URL 且可访问、信源层级标注清晰、无因果推断词；P0 核验表覆盖曲目档案/课标/版权法条/柯尔文史实四类关键事实，单源项显式标注

- **Verification**: `programmatic`（链接抽查 + 格式检查）+ `human-judgment`（事实准确性）

### AC-3: 教程可直接用于备课

- **Given**：一位音乐教师按 examples/01 教案

- **When**：按文档上完一节 45 分钟红歌课

- **Then**：教案含手势练声、赏析六步、视唱曲谱、演唱处理、作业五个环节且时间分配明确；曲谱来源为正版/公版指引

- **Verification**: `human-judgment`

### AC-4: 手势与声乐结合内容专业准确

- **Given**：concepts/07 与 08

- **When**：音乐教研员审查

- **Then**：柯尔文七音手势的空间位置/手型描述与柯达伊体系权威资料一致；声乐基础与 `vocal/meitong-yanyin-pedagogy` 交叉引用有效；无 AI 臆造手势图

- **Verification**: `human-judgment` + `programmatic`（交叉引用链接有效）

### AC-5: 版权合规

- **Given**：全束内容

- **When**：审查曲谱/歌词相关内容

- **Then**：无保护期内完整曲谱/歌词转录；examples/02 含版权自查表与保护期规则；所有曲谱获取指向正版/公版渠道

- **Verification**: `human-judgment`

### AC-6: 构建与规范

- **Given**：新增/修改的全部文件

- **When**：运行定向 `sphinx -b dummy` 构建与 gates.utf8

- **Then**：0 error；全部 .md 为 UTF-8 无 BOM；frontmatter 均可解析且含 type；okf\_version 仅在束根

- **Verification**: `programmatic`

### AC-7: 配图就位且引用有效

- **Given**：Seedream 生成的 2 张图片

- **When**：检查 \_static 目录与索引页引用

- **Then**：图片存在于 `doc/_static/bundles/yishu/hongge/images/`，group/bundle index 引用路径正确，sphinx 构建无图片缺失警告

- **Verification**: `programmatic`

### AC-8: 对抗审查闭环

- **Given**：V 阶段审查记录

- **When**：核查审查意见与修正

- **Then**：四视角覆盖、≥5 条具体意见、≥2 条采纳落盘并复验

- **Verification**: `human-judgment`

## Open Questions

- [ ] Q1：知识包命名 `hongge-pedagogy` 与分组 `hongge` 是否认可？（备选：`red-song-pedagogy`/`red-songs`）

- [ ] Q2：示例教案曲目默认选《歌唱祖国》（公版后、教学最常用、进行曲节奏适合手势），是否更换为《义勇军进行曲》或其他？

- [ ] Q3：C 阶段是否需要在门控全绿后继续执行原子提交（子模块内 commit）？默认不提交，待显式指令。

