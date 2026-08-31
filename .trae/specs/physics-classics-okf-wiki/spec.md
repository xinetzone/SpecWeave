---
id: "physics-classics-okf-wiki"
title: "国外物理学经典原著阅读 OKF Wiki 教程生成"
source: "User Request"
---

# 国外物理学经典原著阅读 OKF Wiki 教程生成 - Product Requirements Document

## Overview
- **Summary**：使用 seven-concepts-cmd 方法论编排（知识沉淀场景 R→I→E，质量门 G1-G4，V 对抗审查强制），系统调研国外物理学经典著作的原文获取渠道与权威解读资源，在 `projects/awesome-okf-xs/doc/bundles/` 下新建第 14 个技术域 `science/`（自然科学经典）与 `science/physics/` 分组，生成单个阅读指南型知识包 `physics-classics-reading`（concepts/examples/references 三层 + facts.md + insights.md），并更新全部索引。
- **Purpose**：物理学元典（伽利略、牛顿、麦克斯韦、爱因斯坦、费曼、朗道等）是现代科学的思想源头，但中文读者面对"读什么、读哪个版本/译本、从哪获取原文、怎么读、用什么解读资料"缺乏可溯源的系统指引。本知识包以 OKF v0.2 格式沉淀可信、可核验的经典阅读地图，与 think/ 域的《老子》帛书阅读教程形成"人文-科学"双经典阅读谱系。
- **Target Users**：物理系本科生与研究生、物理教师、对科学史与科学原典感兴趣的自学者、希望从教科书回溯原始文献的研究者、AI 辅助物理学习的提示词工程使用者。

## Goals
- 新建 `doc/bundles/science/` 技术域（含 domain index）与 `doc/bundles/science/physics/` 分组（含 group index），语义上与 think/（思想哲学）区分，为未来化学/数学/生物经典留扩展位
- 生成 `science/physics/physics-classics-reading/` 知识包，覆盖约 12 部核心元典的原文信源与解读资源：伽利略《两门新科学》(1638)、牛顿《自然哲学的数学原理》(1687)、麦克斯韦《电磁通论》(1873 及 1865 论文)、吉布斯《统计力学基本原理》(1902)、玻尔兹曼《气体理论讲义》(1896-98)、爱因斯坦奇迹年五篇论文 (1905) 与广义相对论论文 (1915/1916)、玻尔 1913 原子模型三部曲、海森堡 1925/1927 论文、薛定谔 1926 波动力学论文、狄拉克《量子力学原理》(1930)、费曼《费曼物理学讲义》(1964)、朗道-栗弗席兹《理论物理学教程》十卷
- references/ 层登记 30+ 部扩展经典（开普勒、惠更斯、拉格朗日、拉普拉斯、傅里叶、卡诺、克劳修斯、马赫、庞加莱、索末菲、玻恩、泡利、冯·诺依曼、温伯格、米斯纳-索恩-惠勒等）与中译本信息
- 所有外部信源 URL 通过源稳定性门（实际访问验证可达），物理事实（年份、作者、书名、版本、公式归属）经 P0 权威核验
- 分级引用策略落地：公有领域著作可双语引用关键段落；在版权著作仅短引（合理使用）+ 官方渠道指引
- 更新 `doc/bundles/index.md`（域数 13→14、组数 32→33、束数 280→281、生态图、入门路径图、导航章节、toctree）与 `doc/index.md` 计数文案

## Non-Goals (Out of Scope)
- 不复制/翻译任何在版权著作的大段原文（费曼讲义、朗道十卷、狄拉克教材、Cohen 译注本等仅合理使用短引 + 链接）
- 不做物理学知识本身的系统教学（不替代教材），只做"原著阅读"的元层指引
- 不覆盖中文物理著作（如《物理学进化》中译本原创等），"国外"指西方物理经典传统；中译本仅作为获取渠道信息登记
- 不新建第二部及以后的著作专属 bundle（如 newton-principia 深读包），本期仅交付单个阅读指南 bundle；后续著作级深读包为未来扩展
- 不修改 awesome-okf-xs 的构建配置（conf.py、tasks/、scripts/）
- 不涉及 think/ 域现有内容修改（仅在总索引生态图中建立跨域关系）

## Background & Context
- **目标仓库**：`d:\AI\projects\awesome-okf-xs\`（SpecWeave 第一方 git submodule，规范自治；内容敏感度判定：公开内容 Public，标准工作流）
- **格式规范**：OKF v0.2——每个非保留 .md 须有 YAML frontmatter 且含非空 `type`；`okf_version: "0.2"` 仅出现在 bundle 根 index.md；index.md/log.md 为保留文件名；正文中文、文件名 kebab-case 纯英文；交叉引用用相对路径，禁止 file:/// 绝对路径；派生产物须标 sources 溯源
- **结构样板**：`think/laozi/boshu-reading/`（经典阅读教程型 bundle：7 concepts + 3 examples + 4 references + facts.md 45 条 + insights.md + index.md + log.md）为最直接同构样板；`viz/3b1b/manim/` 为含 spec/facts.md 的完整结构样板；新域建立流程参照 `3b1b-okf-wiki` spec（新建 viz 域先例）
- **信源预检结果（R 阶段预核验，2026-08-30）**：
  - 牛顿《原理》：Project Gutenberg #76404（Motte 1729 英译、1846 美国版全文，2025-06 上线）、拉丁文原版 #28233；UPenn Online Books Page 有 HathiTrust/archive.org 多版本聚合；Cohen & Whitman 1999 UC Press 新译本含 I.B. Cohen《A Guide to Newton's Principia》（权威解读，在版权）
  - 费曼讲义：官方免费在线版 feynmanlectures.caltech.edu（Caltech，Gottlieb/Pfeiffer 维护）；中译本上海科学技术出版社（潘笃武、李洪芳译）；清华大学 2008 年起开设费曼物理学课程；《大学物理》2018 年第 37 卷第 5 期费曼百年诞辰专栏（赵凯华等，中文权威解读）
  - 其余信源（Galileo Gutenberg/archive.org、Maxwell archive.org/Wikisource、Einstein Papers Project、Annalen der Physik、Nobel lectures、Stanford Encyclopedia of Philosophy、Landau 出版社页等）在 R 阶段逐一实际访问核验
- **方法链**：R（事实采集，F 编号 + G1 无因果词）→ I（洞察四元组，G2）→ E（三层知识拆分，G3 可迁移）→ V（独立对抗审查：物理事实/版权/链接/OKF 合规）→ C（原子提交，G4）
- **构建验证**：`invoke build`（Sphinx 0 warning）、`invoke gates.toctrees`（无断链/无孤立文档/bundle 根完整）、`invoke gates.utf8`（UTF-8 无 BOM）

## Functional Requirements
- **FR-1 新域与新分组脚手架**
  - 创建 `doc/bundles/science/index.md`（domain 型：frontmatter type: group 或等效域级元数据、域说明、分组导航表、hidden toctree 含 physics/index）
  - 创建 `doc/bundles/science/physics/index.md`（group 型：分组说明、bundle 列表表、toctree 含 physics-classics-reading/index）
  - 创建 `doc/bundles/science/physics/physics-classics-reading/` 目录树
- **FR-2 R 阶段事实采集（facts.md）**
  - 对 12 部核心元典逐部采集：外文原名、作者生卒年、首版年份/出版者/原始语言、篇章结构、公有领域状态判定依据、权威全文 URL（≥1 个实际验证可达）、权威英译本、权威中译本（出版社/译者/年份/ISBN 可查项）
  - 对 8+ 个在线信源门户采集：名称、网址、收录范围、使用条款（版权声明）
  - 对 30+ 扩展经典登记：作者、书名、年份、分支归属、PD/在版权状态
  - facts.md 只记客观事实（G1：无"因为/导致/说明"等因果推断词），每条 F 编号
- **FR-3 I 阶段洞察（insights.md）**
  - 提炼 4-6 条核心洞察（四元组：现象+根因+影响+建议），例如：经典语言从几何综合到分析代数的转换、原著难度的双重来源（数学工具 + 历史表达方式）、教材与原著的知识倒置关系、公有领域资源的时间断层（1929 后著作稀缺全文）
  - 含经典知识地图（编年 × 分支矩阵）
- **FR-4 E 阶段三层文档生成**
  - `concepts/` 7-8 篇：为什么读原著、物理学经典地图（编年+分支）、三条阅读路径（零基础/本科基础/研究型）、版本与译本选择、数学准备梯度、几何风格著作读法（《原理》范式）、原始论文读法（1905/量子革命序列）、教材与原著配合（费曼/朗道定位）
  - `examples/` 3-4 篇：《原理》精读示范（定义/公理/运动三定律 + 第一卷命题Ⅰ面积定律）、爱因斯坦 1905《论动体的电动力学》结构拆解、费曼讲义章节读法示范、（可选）伽利略《两门新科学》对话体裁读法
  - `references/` 4-5 篇：原著信源登记（12 部核心，含 URL/PD 状态/译本）、权威解读信源（Cohen Guide、Pais 传记、SEP、Nobel lectures、中文解读资料）、在线原文获取渠道门户、版权与分级引用政策、扩展经典书单（30+）
  - 各级 index.md（concepts/examples/references 子目录）与 log.md（YYYY-MM-DD 日期分组）
  - bundle 根 index.md 含快速导航、快速开始、bundle 定位、学习路径、完整 toctree
- **FR-5 索引与导航集成**
  - 更新 `doc/bundles/index.md`：frontmatter 计数（domains 14、groups 33、total_bundles 281）、生态关系 mermaid（新增 science 节点与关系边）、入门路径 mermaid（think 前插入或并列）、"十四域分组导航"新增 science 章节表格、toctree 新增 science/index
  - 更新 `doc/index.md` 计数文案（与 bundles/index.md 一致：281 束/14 域/33 组）
- **FR-6 溯源与信任字段**
  - 每个内容文档 frontmatter 含 type/title/description/tags/generated/status/stale_after/sources；外部信源用 sources 列表登记（id/resource/title/author），正文用脚注或显式引用逐声明归因
  - bundle 根 index.md 含 okf_version: "0.2" 与 source 溯源字段
  - 时间戳使用 ISO 8601（+08:00 时区），日期字段遵循 Sphinx 钩子兼容约定

## Non-Functional Requirements
- **NFR-1 事实零虚构（P0 权威核验）**：每部核心著作的关键事实（作者、年份、书名、版本）至少 2 个独立权威信源交叉验证；每个外部 URL 必须实际访问成功（WebFetch/HTTP 200），禁止凭记忆书写网址；无法验证的 URL 不得写入
- **NFR-2 版权合规**：公有领域（美国标准：1929 年前出版或作者逝世超 70 年）著作可引用双语关键段落（单段引用控制在合理教学长度并标注出处）；在版权著作仅短句合理使用 + 官方链接；references 中明确每部著作的 PD/版权状态与引用政策
- **NFR-3 OKF 合规**：所有非保留 .md 含可解析 YAML frontmatter 与非空 type；保留文件遵循 index/log 结构；交叉引用相对路径；文件名 kebab-case 纯英文无中文
- **NFR-4 构建质量**：`invoke build` 0 warning/0 error；`invoke gates.toctrees` 与 `invoke gates.utf8` 全部通过；无孤立文档、无断链
- **NFR-5 中文表达**：正文规范现代汉语，物理术语首次出现附英文原文（如"最小作用量原理（principle of least action）"）；外文人名采用"中文（外文）"首次标注
- **NFR-6 教学可用性**：阅读路径具体到"先读哪章/哪篇论文、大约多少小时、需要什么数学"，不停留在书单罗列

## Constraints
- **Technical**：
  - Windows + PowerShell 环境；awesome-okf-xs 使用 Invoke 任务体系（在子项目根目录执行 `invoke build`/`invoke gates.*`）
  - 子项目为 git submodule，提交在子项目仓库内进行（走子项目开发流程，不触碰主权区）
  - 调研工具：WebSearch/WebFetch（公开网络）；禁止访问需登录/付费墙内容
  - Sphinx + myst_parser 构建；frontmatter 裸日期由 doc/conf.py 钩子自动加引号，无需手动处理
- **Business**：质量优先，无硬性时间约束；信源真实性 > 覆盖面（无法核验的宁可不写）
- **Dependencies**：
  - seven-concepts-cmd Skill（R→I→E 编排 + G1-G4 质量门）
  - OKF v0.2 规范（meta/okf-spec bundle）与 awesome-okf-xs frontmatter 规范
  - 既有样板：boshu-reading（同构）、manim（完整结构）、3b1b-okf-wiki（新域流程）

## Assumptions
- 核心信源门户（Gutenberg、archive.org、feynmanlectures.caltech.edu、einsteinpapers.press.princeton.edu、nobelprize.org、plato.stanford.edu、onlinebooks.library.upenn.edu、Wikisource）在执行期可公开访问；个别不可达时以同等级权威替代源替换并在 facts.md 标注
- 12 部核心元典的关键书目事实在权威百科/出版社/图书馆信源中可交叉验证
- awesome-okf-xs 子模块工作树干净、invoke 可用（若不可用先反馈，不擅自修改子项目配置）
- 用户具备基础网络访问能力打开教程中链接；教程本身自包含阅读建议，不依赖外链可访问性
- spec 工件存放于主权区 `d:\AI\.trae\specs\physics-classics-okf-wiki\`（Spec Mode 约定），内容产物全部落在子项目内

## Acceptance Criteria

### AC-1: 新域与分组结构存在且 toctree 完整
- **Type**: `rule`
- **Given**: 知识包生成完成
- **When**: 检查 doc/bundles/science/ 目录树
- **Then**: 存在 science/index.md、science/physics/index.md、physics-classics-reading/ 完整目录（concepts/examples/references 子目录 + index.md + log.md + facts.md + insights.md）
- **Pass Condition**: 目录与文件全部存在；`invoke gates.toctrees` 通过（无孤立文档、无断链、bundle 根 index 完整）
- **Evidence**: 目录树清单 + gates.toctrees 命令输出

### AC-2: 总索引与站点首页计数一致更新
- **Type**: `rule`
- **Given**: 新域已创建
- **When**: 检查 doc/bundles/index.md 与 doc/index.md
- **Then**: bundles/index.md frontmatter 为 domains: 14、groups: 33、total_bundles: 281；正文计数文案、生态 mermaid、入门路径 mermaid、导航章节、toctree 均含 science；doc/index.md 计数文案同步
- **Pass Condition**: 六处更新（frontmatter/正文数字/两张 mermaid/导航章节/两个 toctree）逐项核对一致
- **Evidence**: grep 计数结果 + 文件 diff 摘要

### AC-3: 外部信源 URL 全部经验证可达且事实经 P0 核验
- **Type**: `rule`
- **Given**: references/ 与 facts.md 中登记的全部外部 URL
- **When**: 逐一实际访问核验
- **Then**: 每个 URL 返回可达内容且内容与声明相符；12 部核心著作的作者/年份/书名/版本事实有 ≥2 权威信源交叉记录
- **Pass Condition**: 0 个死链、0 个内容不符链接；facts.md 中每条核心著作事实可追溯到 sources 登记
- **Evidence**: facts.md 的 F 编号 + sources 字段 + R 阶段 URL 核验记录（在 tasks.md 完成证据中登记）

### AC-4: 版权分级引用政策被严格执行
- **Type**: `rule`
- **Given**: 全部内容文档
- **When**: 审查原文引用段落
- **Then**: 公有领域著作的双语引用段落均标注出处且长度合理；在版权著作（费曼讲义、朗道、狄拉克、Cohen 译注本等）无大段原文复制，仅短句合理使用 + 官方链接；references 含版权状态登记
- **Pass Condition**: 无在版权作品的大段引用（连续引用 >50 词外文原文视为超标，公有领域除外）；每部著作版权状态有明确登记
- **Evidence**: references 版权政策文档 + V 阶段逐篇审查记录

### AC-5: Sphinx 构建与质量门全部通过
- **Type**: `rule`
- **Given**: 全部文件落盘
- **When**: 在 awesome-okf-xs 根目录执行 `invoke clean && invoke build` 与 `invoke gates.all`
- **Then**: 构建 0 warning/0 error；UTF-8 与 toctree 检查通过
- **Pass Condition**: 命令退出码 0 且输出无 warning/error
- **Evidence**: 命令输出文本

### AC-6: 知识包教学实用性（阅读路径可执行）
- **Type**: `rubric`
- **Dimension**: 读者拿到 bundle 后能否真正开始读原著（路径具体性、版本可获得性、难度梯度合理性）
- **Scale**: 1-5
- **Anchors**: 1 = 仅书单罗列，无路径与版本指引；3 = 有路径与版本建议但部分环节模糊（如未说明先读哪章）；5 = 三条读者路径均具体到章节/论文顺序/预计工时/数学前置，examples 提供可照做的精读示范
- **Pass Threshold**: >= 4
- **Evidence**: concepts/02 阅读路径 + examples/ 三篇精读示范的独立审查评分

### AC-7: 物理事实准确性
- **Type**: `rubric`
- **Dimension**: 物理史实与科学内容准确性（人名、年份、公式归属、术语翻译、著作结构描述）
- **Scale**: 1-5
- **Anchors**: 1 = 存在硬伤（错误年份/错误作者/错误公式归属）；3 = 事实基本正确但有 2-3 处表述不严谨；5 = 全部关键事实经核验无误，术语规范，引用原文与通行版本一致
- **Pass Threshold**: >= 4（且 0 个硬伤）
- **Evidence**: V 阶段独立审查逐事实核验记录

### AC-8: OKF v0.2 格式合规
- **Type**: `rule`
- **Given**: 全部新增 .md 文件
- **When**: 按 OKF 合规三要件检查
- **Then**: 每个非保留 .md 含可解析 YAML frontmatter 与非空 type；okf_version 仅出现在 bundle 根 index.md；index.md/log.md 遵循保留文件结构；文件名 kebab-case 纯英文
- **Pass Condition**: 合规检查 0 违规
- **Evidence**: 逐文件 frontmatter 检查记录 + 文件名清单

## Open Questions
- [ ] 中译本 ISBN 是否逐本登记？（建议：核心 12 部的中译本登记到出版社/译者/年份层级，ISBN 仅在可稳定核验时登记，避免编目错误——R 阶段按信源可得性决定）
- [ ] 是否在 think/ 域建立到 science/ 的交叉链接？（建议：仅在总索引 mermaid 建关系边，不改 think/ 内部文件，减少改动面；V 阶段复核）
