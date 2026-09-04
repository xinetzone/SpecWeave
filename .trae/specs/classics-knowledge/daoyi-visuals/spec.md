***

type: Spec
title: 道医束配图与 Mermaid 图表增强 PRD
created: 2026-09-02
source: 用户 /goal 指令——为 projects/awesome-okf-xs/doc/bundles/yixue/daoyi 生成配图（Seedream 插件）并配适度 mermaid
scenario: seven-concepts 场景4（知识沉淀）变体：R（束内容盘点）→ F（视觉载体分工设计）→ E（生成嵌入）→ V（对抗审查+门禁）→ C（原子提交）
----------------------------------------------------------------------------------------

# 道医束配图与 Mermaid 图表增强 - Product Requirement Document

## Overview

- **Summary**：为 OKF 知识包 `yixue/daoyi/daoyi-reading`（道医经典阅读教程，22 个文件、9 概念 + 3 示例 + 4 信源）增加两类视觉资产：①8 张 Seedream AI 生成的中国水墨淡彩风格意境插图（落盘 `doc/_static/bundles/yixue/daoyi/daoyi-reading/images/`）；②9 张 Mermaid 结构图/时间线/决策流程图（以 \`\`\`mermaid 栅栏嵌入既有概念与示例文档）。全部视觉资产遵循"AI 图承载氛围意境、Mermaid 承载精确结构"的分工铁律。

- **Purpose**：现束为纯文本长文（概念页单篇 60-90 行），阅读体验密不透风；三圆模型、历史分期、文献谱系、辨伪决策、阅读路径等结构性内容以表格/ASCII 表达，空间关系不直观。配图增强面向中文读者的阅读教程定位，提升可读性与审美一致性，同时不改变任何事实陈述与文献结论。

- **Target Users**：道医经典阅读教程的三档读者（零基础/中医基础/研究型）与 awesome-okf-xs 文档站（Sphinx/Read the Docs）访问者。

## Goals

- G1：8 张风格统一的水墨淡彩意境插图，覆盖束首页与 7 个核心概念页（01-07）。

- G2：9 张 Mermaid 图表，把模型、分期、谱系、卷次、决策、路径类结构信息图形化，事实与正文严格一致。

- G3：全部视觉资产通过子项目质量门（`invoke gates.all`）与 Sphinx 构建（`invoke build` 无新增警告）。

- G4：变更原子化、可审计——不新增/删除 .md 文档、不改动 toctree、不碰 `doc/bundles/index.md` 共享计数；log.md 追加变更记录。

## Non-Goals (Out of Scope)

- 不修改任何事实陈述、文献结论、ISBN/URL/年代/卷次数据（视觉只"翻译"既有内容，不新增事实）。

- 不生成历史人物真容画像、穴位/解剖图、功法动作图、符箓/经文文字图（防事实误读与医疗暗示）。

- 不新增知识包、不改动束结构与 toctree、不做束计数变更。

- 不推送远端（push）；提交仅限 daoyi 束相关文件。

- 不改动 facts.md 事实编号体系；references/ 4 篇信源文档不嵌图（表格矩阵形态保持）。

## Background & Context

- **工程环境**：awesome-okf-xs 为 Sphinx + MyST 文档工程；`doc/conf.py` 已配置 `myst_fence_as_directive = ["mermaid"]`，\`\`\`mermaid 栅栏经 sphinxcontrib-mermaid（CDN mermaid 11.4.1，运行时 JS 渲染）出图；Mermaid 语法错误不导致构建失败、只在浏览器端暴露，故须按 mermaid-cmd 技能流程做语法校验。

- **图片先例**：`yishu/vocal/meitong-yanyin-pedagogy` 束已有 3 张配图，落盘 `doc/_static/bundles/<域>/<组>/<束>/images/`，文档以 `![alt](/_static/bundles/.../images/name.png)` 绝对站点路径引用。本任务沿用同一惯例，目标路径为 `doc/_static/bundles/yixue/daoyi/daoyi-reading/images/`。

- **束内容**：道医（道家道教传统与中医交汇的文化—实践连续体）文献阅读指南，含非医疗声明；全部内容为公开文化与文献研究（Public 级）。

- **竞态背景**：该子模块为并行会话共享工作区；本任务不触碰共享索引（bundles/index.md），提交时遵循"add 与 commit 分步、暂存 blob 核验"协议（项目记忆 verified 2026-08-31/09-01）。

## Functional Requirements

- **FR-1（Mermaid 嵌入，9 张）**：

  - M1 `concepts/00-what-is-daoyi.md`：吉元昭治三圆模型（中心圆=汤液本草针灸／中间圆=导引调息内丹辟谷内视房中／外周圆=符占签咒斋禁祭祀）与"道—理—术"三层对应图（flowchart）。

  - M2 `concepts/01-history-yidao-tongyuan.md`：医道同源历史时间线——盖建民三期（汉魏六朝/隋唐至元/明清）与《道医集成》六期表述，并标注祝由科沿革节点（唐咒禁科→元明祝由科→1571 裁撤）（timeline）。

  - M3 `concepts/03-daoist-physicians.md`：葛洪（283-363）/陶弘景（456-536）/孙思邈（581-682）三人 → 各自医著与道学著述关系图（flowchart）。

  - M4 `concepts/04-daozang-medical.md`：道藏养生文献体系图——三种现代道藏（涵芬楼 1120 册/三家本 36 册/中华道藏 49 册）与《云笈七签》医学相关卷次（卷32-36 杂修摄／卷56-62 气法／卷63-73 金丹／卷74起 方药）（flowchart）。

  - M5 `concepts/05-neidan-medical.md`：外丹→内丹范式更替与丹经脉络时间线——《参同契》东汉魏伯阳→《悟真篇》北宋张伯端→《黄庭经》→《性命圭旨》明 1615→《伍柳仙宗》清 1794/1896→陈撄宁 1957《静功疗养法》（timeline）。

  - M6 `concepts/06-excavated-fangji.md`：《汉志》方技略四家（医经/经方/房中/神仙）↔ 出土文献（马王堆前168/张家山前186/天回西汉/敦煌南北朝-五代）↔ 传世文献对应图（flowchart，subgraph 分区）。

  - M7 `concepts/07-yidao-schools.md`：宋以后医道会通五家时间线——窦材《扁鹊心书》1146→张景岳《景岳全书》1624→赵献可《医贯》1617→黄元御《四圣心源》1753→郑钦安（1824-1911，1869/1874/1894 三书）（timeline）。

  - M8 `concepts/08-authenticity-and-sources.md`：辨伪决策流程图——三类非常态文本（托名/扶乩/辑佚）→ 断代三法（避讳字/著录首见/传本链）→ 两说并陈处理原则；并含在线平台四级分级（识典＞维基文库＞ctext＞diancang，zysj 禁用）（flowchart）。

  - M9 `examples/02-reading-paths.md`：三档阅读路径阶梯图——零基础 8 周／中医基础 6 周／研究型专题，体现"识典精校→点校本→道藏/出土整理本"阶梯原则（flowchart）。

- **FR-2（配图生成与嵌入，8 张）**：

  - IMG-1 `hero-daoyi`：束首页 `daoyi-reading/index.md` 顶部——云雾山间道观药庐、药葫芦/灵芝/竹简元素，水墨淡彩横卷。

  - IMG-2 `history-yidao`：concepts/01——汉唐气象长卷意境：古卷轴、山道行旅、远山观宇，时间纵深感。

  - IMG-3 `classics-roots`：concepts/02——古籍书案意境：堆叠的帛卷/竹简/线装书、青灯，不出现可辨读文字。

  - IMG-4 `daoist-physicians`：concepts/03——茅山药圃意境：背篓道者辨药（远景/背影、不刻画面容）、远山道观。

  - IMG-5 `daozang-canon`：concepts/04——道教藏经阁意境：函套经卷林立、书帙、烛火，庄肃。

  - IMG-6 `neidan-cultivation`：concepts/05——静坐者剪影与云气周天意象、山水环绕，大写意、无解剖细节。

  - IMG-7 `excavated-texts`：concepts/06——考古出土意境：帛书残卷、竹简、髹漆器物、考古刷，淡彩。

  - IMG-8 `yidao-schools`：concepts/07——明清书斋论医意境：翻开的古籍、砚台药钵、墙面淡墨卦象符号（无可辨读文字）。

- **FR-3（图片引用规范）**：每张图以 `![描述性中文 alt](/_static/bundles/yixue/daoyi/daoyi-reading/images/<file>)` 引用；图下一行斜体图注注明"AI 生成意境图，非历史图像"；插入位置为该页首个一级标题之后、第一节内容之前（首页为开篇段之后）。

- **FR-4（Mermaid 规范）**：遵循 mermaid-cmd 安全编码六规则——节点标签全部加引号、标签内不使用半角括号/冒号等特殊字符（可用全角）、不使用裸特殊字符、中文文本不依赖字体图标；timeline 与 flowchart 语法兼容 mermaid 11.4.1。

- **FR-5（log 记录）**：`daoyi-reading/log.md` 按既有格式追加本次视觉增强条目。

## Non-Functional Requirements

- **NFR-1（事实零漂移）**：Mermaid 中全部人名、年代、书名、卷次、册数、平台名必须与所在页正文/facts.md 一致；不得引入正文没有的事实。

- **NFR-2（风格一致性）**：8 张图统一为中国传统水墨淡彩、绢本设色质感、暖褐青灰色调、横向构图；无照片写实感、无现代元素、无文字水印。

- **NFR-3（安全性）**：图像不出现可识别人物面容、不表现具体医疗/练功操作、不出现符箓经文可辨读文字；所有页面非医疗声明保持原样。

- **NFR-4（构建兼容）**：`invoke gates.all` 三门全绿；`invoke build` 相对构建前无新增警告/错误；图片在构建产物中可解析（无 image not readable）。

- **NFR-5（适度原则）**：Mermaid 合计 9 张、配图 8 张；references/ 与 facts.md 不嵌图；insights.md ASCII 知识地图保留原样（文件树形态恰当）。

## Constraints

- **Technical**：图片经 Seedream 插件（GenerateImage 工具）生成，落盘子模块 `doc/_static/`；Mermaid 经 MyST 栅栏（mermaid 11.4.1 CDN 渲染）；文件名 kebab-case 英文；正文中文。

- **Business**：内容为公开文化文献研究；不构成医疗指导；不推送远端。

- **Dependencies**：sphinxcontrib-mermaid（已在 conf.py 可选扩展中）、Seedream 生成配额、子模块 invoke 门禁环境（Windows 下用 pwsh7 或 WSL 执行）。

- **边界**：projects/awesome-okf-xs 为 git submodule，变更走子模块提交；不触碰主仓库其他区域。

## Assumptions

- A1：GenerateImage 可直接写入子模块 `doc/_static/...` 路径（工作区 d:\spaces\SpecWeave 内）；生成格式以实际落盘扩展名为准，引用路径据实匹配。

- A2：sphinxcontrib-mermaid 在本地构建环境已安装（conf.py 条件加载）；若未安装，Mermaid 栅栏在构建中不报错但不出图，校验以语法审查 + mmdc（可用时）为准。

- A3：8 张图为氛围插图而非史料图像，"AI 生成意境图"图注足以防止事实误读。

- A4：提交环节若发现并行会话暂存区混入他方文件，立即停止 commit 并报告（不 reset、不代提交）。

## Acceptance Criteria

### AC-1：9 张 Mermaid 全部嵌入且语法正确

- **Given**：daoyi-reading 束 9 个目标文档

- **When**：视觉增强完成后检查各文档

- **Then**：每个目标文档含 1 张指定 Mermaid 栅栏；栅栏语法通过 mermaid-cmd 校验流程（mmdc 可用时通过渲染校验，不可用时逐图人工语法审查通过）；无半角括号等违规字符

- **Verification**: `programmatic`（文件检查 + 语法校验）

### AC-2：Mermaid 事实与正文零漂移

- **Given**：9 张 Mermaid 的全部文本节点

- **When**：对抗审查逐节点比对所在页正文与 facts.md

- **Then**：人名/年代/书名/卷次/册数/平台名 100% 一致，无新增事实、无张冠李戴

- **Verification**: `human-judgment`（对抗审查子代理逐图核验）

### AC-3：8 张配图生成落盘且引用有效

- **Given**：Seedream 生成完成

- **When**：检查 `doc/_static/bundles/yixue/daoyi/daoyi-reading/images/` 与 8 个文档

- **Then**：目录下存在 8 个图片文件；8 处 Markdown 引用路径与实际文件名（含扩展名）完全一致；Sphinx 构建无 image not readable 警告

- **Verification**: `programmatic`

### AC-4：配图风格统一且安全

- **Given**：8 张生成图

- **When**：人工审查图像内容

- **Then**：均为水墨淡彩中国风、横向构图、无现代元素/文字水印/可辨读经文/人物真容/医疗练功动作；每图带"AI 生成意境图"图注

- **Verification**: `human-judgment`

### AC-5：质量门与构建全绿

- **Given**：全部变更完成

- **When**：在 projects/awesome-okf-xs 执行 `invoke gates.all` 与 `invoke build`

- **Then**：utf8/toctrees/bundles 三门全绿；构建无新增警告（相对变更前基线）

- **Verification**: `programmatic`

### AC-6：变更范围原子化

- **Given**：git status/diff

- **When**：审查变更集

- **Then**：变更仅含——8 个新增图片文件、9 个被编辑的 .md（concepts 00/01/03/04/05/06/07/08、examples/02）、首页 index.md、log.md；不含 doc/bundles/index.md 等共享索引、无 toctree 结构改动、无新增 .md

- **Verification**: `programmatic`

### AC-7：原子提交（竞态安全）

- **Given**：门禁全绿后

- **When**：在子模块执行提交

- **Then**：先查 `.git/MERGE_HEAD` 不存在；仅 `git add` 本任务文件；add 与 commit 分两次调用；commit 前 `git diff --cached --name-only` 核验暂存集全部为本任务文件；暂存 blob 抽查含己方改动；提交信息为 Conventional Commits 中文主体；**不执行 push**

- **Verification**: `programmatic`

## Open Questions

- 无阻塞性问题。以下为执行中默认决策，用户可在审批时调整：

- [ ] 配图数量 8 张（首页 + 概念 01-07；概念 00 与 08 仅 Mermaid）是否认可？

- [ ] Mermaid 9 张的分布是否认可（references/ 与 facts.md 不嵌图）？

- [ ] 图像风格默认"水墨淡彩、暖褐青灰、写意无人物面容"是否认可？

- [ ] 完成后是否在子模块内原子提交（不推送）？默认提交；若并行会话活跃则暂停提交并报告。

