---
title: "杭州求姻缘地点调研知识包（OKF wiki 教程）- Product Requirement Document"
status: "draft"
---

***

title: 杭州求姻缘地点调研知识包 OKF wiki 教程 PRD
session: sc-20261001-hangzhou-qiuyinyuan-okf-wiki
methodology: seven-concepts-cmd（R→I→A→V→C，知识沉淀场景标准链路，V 强制）
source: 用户公开调研需求（全面调研杭州求姻缘的地方）
sensitivity: public（公开内容：寺院/民俗点均为公开场所，信源为公开网页与官方发布）
created: 2026-10-01
-------------------

# 杭州求姻缘地点调研知识包（OKF wiki 教程）- Product Requirement Document

## Overview

- **Summary**：在 awesome-okf-xs 文档库 `sheke/`（社会科学）域下新建 **民俗分组（minsu）**，本束作为该组首束 `hangzhou-qiuyinyuan-guide`（杭州求姻缘地点实用指南），以 OKF v0.2 bundle 三层结构（concepts/examples/references）+ facts.md 事实清单 + insights.md 架构洞察组织，对杭州"求姻缘"目的地做**寺院线 + 民俗点全覆盖**调研：法喜寺、灵隐寺等寺院参拜线，黄龙洞月老祠、万松书院相亲角等民俗点，以及交通、门票、礼仪、时间安排等实用参拜攻略。

- **Purpose**：网络信息关于"杭州哪里求姻缘灵验"零散、营销号内容多、开放时间/门票等关键事实常过期或互相矛盾。本知识包把分散信息收敛为一份可照做的中文实用指南：读者拿到即可规划行程、完成参拜、避开常见坑，同时以民俗文化视角理性呈现（不宣扬迷信、不做灵验度排名背书）。

- **Target Users**：计划赴杭求姻缘的单身青年及陪同亲友、赴杭旅游并对姻缘民俗感兴趣的游客、民俗文化内容创作者与研究者；次级读者为杭州本地向导/文旅从业者。

## Goals

- G1：新建 `doc/bundles/sheke/minsu/` 分组与 `hangzhou-qiuyinyuan-guide/` 知识包，结构完全对齐 OKF v0.2 与同库先例束（frontmatter 九字段、三层目录、facts/insights）。

- G2：**寺院线全覆盖**：法喜寺（上天竺，杭州求姻缘最热门）、灵隐寺（及永福寺、韬光寺）、净慈寺、香积寺等与姻缘祈愿相关的寺院，逐点给出位置、开放信息、姻缘相关祈福点位与参拜要点。

- G3：**民俗点全覆盖**：黄龙洞月老祠（月老信仰核心点位）、万松书院相亲角（城市相亲民俗现象）等，呈现其民俗源流与现状。

- G4：**实用参拜攻略**：门票/开放时间/预约方式、交通路线、参拜礼仪与流程、行程组合建议、避坑提示，全部以官方/权威信源为准并标注核验日期。

- G5：facts.md 事实清单零推测、信源 URL 逐条内嵌、单源/存疑显式标注、含 P0 双源核验表（G1 质量门，≥60 条事实）。

- G6：全束通过 awesome-okf-xs 三门质量门（utf8/toctrees/bundles）与定向 sphinx dummy 构建（0 error）。

- G7：Seedream 生成分组装饰封面（group hero）1 张 + 知识包封面 1 张，落位 `doc/_static/bundles/sheke/minsu/images/` 并在索引页正确引用。

## Non-Goals (Out of Scope)

- 不做"灵验度"排名或神秘化背书：全部内容以民俗文化与旅游实用视角客观呈现，信仰体验层面交由读者自决。

- 不涉及任何付费姻缘服务、算命占卜、婚庆婚介商业推荐；万松书院相亲角仅作民俗现象客观描述，不收集/呈现任何个人相亲信息（隐私红线）。

- 不复制仍在著作权保护期内的文章内容；史料与报道只做事实摘编并挂信源。

- 不新建第二个知识包（如"中国月老信仰通论"），月老信仰内容以"服务杭州实地参拜"为边界。

- 不执行 git commit / push（C 阶段交付物为工作树文件 + 门控全绿；提交需用户显式指令）。

- 不修改 `projects/awesome-okf-xs/.agents/` 子项目规范文件。

## Background & Context

- 需求来源：用户指令"全面调研杭州求姻缘的地方，生成 okf wiki 教程"（2026-10-01）。内容敏感度预检判定为**公开内容** → 标准工作流，Spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物入 `projects/awesome-okf-xs/doc/bundles/`。

- 归属决策（用户已确认）：`sheke` 域现有 7 组（workplace/relationships/sexology/finance/marketing/personal-growth/industry）均不匹配民俗调研主题；`relationships` 组定位为"两性关系经典著作与公开文章转化教程"，与实地民俗指南性质不符 → 新建 `minsu`（民俗）分组，本束为首束。

- 先例模板：`yishu/hongge/hongge-pedagogy` 与 `yishu/vocal/meitong-yanyin-pedagogy` 束即由 seven-concepts-cmd 链路生成，frontmatter 形态（`type: OKF`、`generated: agent:seven-concepts-cmd`、`verified: process:seven-concepts-v`、facts.md + P0 表、insights.md 四元组）为本束直接模板。

- 配图先例：`doc/bundles/jishu/gui/index.md` 与 hongge 组使用 Seedream 生成的 `/_static/bundles/<域>/<组>/images/` 装饰封面。

- 门控命令须在 **py314 conda 环境**下于子项目根目录执行：`conda run --no-capture-output -n py314 invoke gates.utf8`、`invoke gates.toctrees`、`invoke gates.bundles`；定向构建：`python -m sphinx -b dummy -E doc .temp/dummy <显式文件列表>`。

- 共享索引（`bundles/index.md`、`sheke/index.md`）存在并行会话写入漂移：计数一律以门控重算为准，禁止手填；注册编辑后须立即核验落盘。

- 七概念链路（本次场景=知识沉淀，决策树场景 4 标准链路，V 强制）：**R**（双路 Web 信源调研→facts.md）→ **I**（insights.md 四元组洞察）→ **A**（原子化文件成束）→ **V**（四视角对抗审查+修正）→ **C**（门控交付，提交待令）。

- 事实时效风险：寺院门票/开放时间/预约政策会变动，facts.md 须标注信息采集日期（2026-10），references 给出官方查询入口供读者复核。

## Functional Requirements

- **FR-1 分组与知识包骨架**：创建 `sheke/minsu/index.md`（type: group，含分组导航表、知识地图 mermaid、toctree、hero 图）与 `sheke/minsu/hangzhou-qiuyinyuan-guide/` 束根 `index.md`（type: OKF，okf_version 0.2，快速导航表、读者路径 mermaid、toctree 覆盖 concepts/examples/references/facts/insights）。

- **FR-2 事实清单（R 阶段）**：`facts.md` 登记 ≥60 条零推测事实，分轨：①月老信仰与杭州姻缘民俗源流（月老出处、杭州相关记载与报道）②法喜寺（历史、位置、门票/开放、姻缘相关祈福点位与法物流通）③灵隐寺景区（灵隐寺、永福寺、韬光寺；飞来峰门票与寺院香花券双票制、开放时间）④其他寺院（净慈寺、香积寺等）⑤黄龙洞月老祠（景区属性、月老祠位置、门票、相亲文化）⑥万松书院相亲角（开放时间、周日相亲角现象、媒体报道）⑦实用信息（交通、预约渠道、寺院参拜礼仪规范）；每条内嵌信源 URL、标注信源层级（一级=官方/政府/寺院官网公众号/权威媒体；二级=百科/自媒体仅作线索），单源/存疑显式标注；文末附 P0 双源核验表（门票/开放时间/地址等关键实用事实必须双源）。

- **FR-3 架构洞察（I 阶段）**：`insights.md` 产出 ≥5 条四元组洞察（现象/根因/影响/建议，回指 F 编号），覆盖：网络姻缘攻略信息矛盾根源在信源层级混杂、寺院线热度差异与交通/营销的关系、民俗点（相亲角）与寺院（信仰参拜）是两类体验逻辑、门票预约信息时效性管理是攻略最大维护成本、"灵验叙事"传播机制与理性呈现的平衡。

- **FR-4 概念文档 8 篇**：`concepts/00~07`（00 入门地图：知识包定位、三类读者画像、使用路径；01 月老信仰与杭州姻缘民俗源流；02 法喜寺参拜指南；03 灵隐寺景区参拜指南（灵隐/永福/韬光）；04 其他相关寺院（净慈寺/香积寺等）；05 黄龙洞月老祠；06 万松书院相亲角；07 参拜礼仪与理性看待求姻缘）。

- **FR-5 实践示例 3 篇**：`examples/01` 寺院一日参拜路线（法喜寺+灵隐寺景区，含时间轴与交通衔接）；`examples/02` 民俗点半日路线（黄龙洞+万松书院，含周边串联）；`examples/03` 参拜准备清单与避坑指南（行前检查表、礼仪自查、信息复核清单）。

- **FR-6 信源参考 3 篇**：`references/01` 寺院官方信源（各寺院官网/公众号/官方购票预约渠道）；`references/02` 民俗与史料信源（月老信仰文献、方志记载、权威媒体报道）；`references/03` 交通与实用信息信源（杭州文旅官方、公交地铁查询、景区公告入口）。

- **FR-7 配图**：Seedream 生成 2 张装饰性封面（分组 hero、知识包封面），杭州江南意象/禅意暖色审美，无文字、无真实人物肖像，落位 `doc/_static/bundles/sheke/minsu/images/`，在 group index 与 bundle index 顶部以 MyST 图片语法引用（绝对路径 `/_static/...`）。

- **FR-8 共享索引注册**：更新 `sheke/index.md`（分组表新增 minsu 行、toctree 增 `minsu/index`、域描述计数更新）与 `bundles/index.md`（frontmatter total_bundles/groups、sheke 域节标题计数、分组表新增行、生态概览 mermaid sheke 行）五面对账；计数以门控重算为准，禁止手填。

- **FR-9 对抗审查（V 阶段）**：四视角审查（魔鬼代言人/新人/老板/未来）输出 ≥5 条具体意见并至少采纳 2 条修正落盘；重点攻击事实准确性（门票/时间/地址）、迷信表述与合规、隐私红线（相亲角）、零基础可用性。

## Non-Functional Requirements

- **NFR-1 事实可信**：所有门票价格、开放时间、地址、历史年代必须有可访问 URL 信源；官方/政府/寺院官网为一级信源，百科/自媒体仅作线索并标注；P0 事实（门票/开放/地址）双源核验；全部时效性事实标注采集日期。

- **NFR-2 门控全绿**：`gates.utf8`、`gates.toctrees`（无断链、无孤立文档、束根 toctree 全覆盖）、`gates.bundles`（束/组/域三角计数一致）全部通过；定向 sphinx dummy 构建 0 error、0 警告（与新增文件相关）。

- **NFR-3 规范一致**：每个非保留 .md 含可解析 YAML frontmatter 且有非空 `type`；`okf_version: "0.2"` 仅出现在束根 index.md；文件名 kebab-case 英文；正文中文；相对路径交叉引用，禁止 `file:///`；frontmatter 双引号内不嵌 ASCII 双引号。

- **NFR-4 内容红线**：不做灵验度承诺/排名背书；不出现算命占卜付费服务引导；万松书院相亲角不引用任何可识别个人的信息；寺院宗教内容表述尊重、客观（以民俗文化和旅游视角）。

- **NFR-5 实用可用性**：概念文档每篇含"学完能做什么"；examples 路线可直接照做（时间轴/交通/费用明确）；所有"请先自行核实"类提示必须附带官方查询入口。

- **NFR-6 脱敏**：全束不出现任何真实个人相亲信息、联系方式；不引用无授权的个人经历帖原文。

## Constraints

- **Technical**：Markdown + MyST（myst_parser）+ Sphinx；YAML frontmatter；mermaid 图；图片存 `doc/_static/`；Windows 环境，命令经 PowerShell + py314 conda；子项目为 git submodule（不在其中执行 commit/push）。

- **Business**：内容属公开文旅/民俗范畴；涉及宗教场所须符合国家宗教事务相关表述规范，客观介绍不传教不贬损。

- **Dependencies**：Seedream 配图（GenerateImage 工具）；WebSearch/WebFetch 信源核验；门控脚本 check-toctrees.py / check-bundles-index.py / check-utf8.py。

## Assumptions

- A1：归属 `sheke` 域新建 `minsu` 民俗分组（用户已确认）；组名 `minsu` 与全库拼音命名风格一致。

- A2：知识包定名 `hangzhou-qiuyinyuan-guide`，与先例 `*-guide`、`*-pedagogy` 命名风格一致。

- A3：范围为寺院线 + 民俗点全覆盖 + 实用攻略（用户已确认）；以当前公开信息为准，采集日期 2026-10。

- A4：门控计数以实施时 gates 重算为准（并行会话可能使 total_bundles 基线漂移，当前基线 575 束 / 59 组 / 9 域）。

- A5：用户确认需要 2 张 Seedream 装饰封面；门控全绿后停止，不执行 git commit（提交待显式指令）。

## Acceptance Criteria

### AC-1: 知识包骨架与注册完整

- **Given**：awesome-okf-xs 仓库当前状态

- **When**：实施完成并运行 `invoke gates.bundles` 与 `invoke gates.toctrees`

- **Then**：`sheke/minsu/hangzhou-qiuyinyuan-guide/` 被识别为 1 个新束、`sheke/minsu/` 为 1 个新组；总索引五面（frontmatter/计数行/域节/分组表/toctree）计数一致；无断链、无孤立文档

- **Verification**: `programmatic`

### AC-2: 事实清单可信可溯

- **Given**：facts.md

- **When**：抽查任意 10 条事实

- **Then**：每条含信源 URL 且可访问、信源层级标注清晰、无因果推断词；P0 核验表覆盖各点位门票/开放时间/地址三类关键实用事实，单源项显式标注

- **Verification**: `programmatic`（链接抽查 + 格式检查）+ `human-judgment`（事实准确性）

### AC-3: 攻略可直接照做

- **Given**：一位首次赴杭的读者按 examples/01 路线

- **When**：按文档规划一日行程

- **Then**：路线含明确时间轴、各点位交通衔接、门票与预约方式、参拜流程；所有时效信息附官方复核入口

- **Verification**: `human-judgment`

### AC-4: 内容合规与客观

- **Given**：全束内容

- **When**：审查求姻缘相关表述

- **Then**：无灵验度承诺/排名；无付费占卜婚介引导；相亲角内容无可识别个人信息；宗教场所表述尊重客观

- **Verification**: `human-judgment`

### AC-5: 构建与规范

- **Given**：新增/修改的全部文件

- **When**：运行定向 `sphinx -b dummy` 构建与 gates.utf8

- **Then**：0 error；全部 .md 为 UTF-8 无 BOM；frontmatter 均可解析且含 type；okf_version 仅在束根

- **Verification**: `programmatic`

### AC-6: 配图就位且引用有效

- **Given**：Seedream 生成的 2 张图片

- **When**：检查 _static 目录与索引页引用

- **Then**：图片存在于 `doc/_static/bundles/sheke/minsu/images/`，group/bundle index 引用路径正确，sphinx 构建无图片缺失警告

- **Verification**: `programmatic`

### AC-7: 对抗审查闭环

- **Given**：V 阶段审查记录

- **When**：核查审查意见与修正

- **Then**：四视角覆盖、≥5 条具体意见、≥2 条采纳落盘并复验

- **Verification**: `human-judgment`

## Open Questions

- [ ] Q1：知识包命名 `hangzhou-qiuyinyuan-guide` 与分组 `minsu` 是否认可？（备选：`hangzhou-yuelao-guide` / `folklore`）
- [ ] Q2：覆盖点位清单是否还有遗漏？（当前清单：法喜寺、灵隐寺、永福寺、韬光寺、净慈寺、香积寺、黄龙洞月老祠、万松书院相亲角；R 阶段调研中若发现其他公认点位将补充并在 tasks 中登记）
- [ ] Q3：C 阶段门控全绿后是否需要执行原子提交（子模块内 commit）？默认不提交，待显式指令。
