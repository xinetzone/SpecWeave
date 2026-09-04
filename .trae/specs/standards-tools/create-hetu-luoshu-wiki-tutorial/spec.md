---
title: "河图洛书与宋代图书学 OKF Wiki 教程"
status: "draft"
---

# 河图洛书与宋代图书学 OKF Wiki 教程 Spec

> **change-id**: `create-hetu-luoshu-wiki-tutorial`
> **主题目录**: `standards-tools`（沿 create-sexology-classics-wiki / create-graphql-wiki-tutorial 先例）
> **七概念链路**: 场景4 知识沉淀 **R → I → E → V → C**（R 调研采集 → I 洞察 → E 模式萃取（V 后定稿）→ V 独立对抗评审 → C 入库索引更新）
> **内容敏感度**: 公开（Public）——公版古籍与学术研究对象，标准工作流，产出物位于 `projects/awesome-okf-xs/doc/bundles/`
> **结构模板**: 仿 `think/yinyangjia/yinyangjia/`（2026-08-30 入库的最新完整束：index + facts + insights + patterns + log + concepts/ + examples/ + references/）

## Overview

- **Summary**: 在 awesome-okf-xs 文档库 think 域（思想与理论）新增 `hetu-luoshu` 分组与 1 个完整 OKF 知识包，系统整理河图洛书与宋代图书学（先天图、太极图、象数学）的**权威原文与学术解读**，以"名实分层、双源核对、辨伪谱系"为组织基调。
- **Purpose**: 河图洛书是中文世界最著名也最被误读的文化符号之一。大众读物普遍把宋代才定型的黑白点图式当作伏羲时代的"天赐原图"，混淆祥瑞名物、宋造图式、术数附会三个层面；读者需要一部以现代学术共识为框架、原典原文可核对、历代诠释有谱系的阅读教程。
- **Target Users**: ① 零基础传统文化读者（想知道河图洛书"到底是什么"）；② 读过通俗术数/国学读物、想核验真伪的读者；③ 易学/哲学史/考古方向的研究型读者（需要信源分级与争议标注）。

## 用户已确认的范围决策

1. **收录范围 = 宋代图书学全景**：以河图洛书为核心，完整展开宋代图书学三大图系——河图洛书（刘牧→朱熹/蔡元定）、先天图（陈抟→邵雍）、太极图（周敦颐），兼及汉易象数基础与清代辨伪；概念文档 12 篇。
2. **术数/风水/占卜内容 = 学术辨析为主**：客观介绍河图洛书在风水、术数、内丹等传统中的运用史，定位为文化现象分析；**不提供任何占卜、算命、风水布局的操作教程**；对民间附会说法显式标注层次。
3. **原文尺度 = 核心段落全文 + 双源核对**：先秦两汉公版原典核心段落（《尚书·顾命》《尚书·洪范》九畴、《论语·子罕》、《周易·系辞上》天地之数章、《礼记·礼运》、《大戴礼记·明堂》、《易纬·乾凿度》、《数术记遗》九宫注等）全文收录并逐句注读；宋代专著（《易数钩隐图》《易学启蒙》《皇极经世书》《太极图说》）节选关键段落；清代辨伪名著（《易图明辨》等）以提要 + 名段选录为主；全部古籍原文经 ctext.org 与维基文库/识典古籍**双源逐字核对**，异文登记。

## Goals

- 在 `doc/bundles/think/hetu-luoshu/` 下建立合规 OKF v0.2 分组与知识包，文件组织、frontmatter、toctree 与 yinyangjia 束模板一致。
- 以**名实三层框架**贯穿全部内容：① 先秦两汉文献中的"河图洛书"= 祥瑞名物记载；② 宋代才出现并定型的黑白点数图式；③ 后世术数/民俗的附会运用——三层不混用。
- 提供可核对的权威原文：公版原典双源核对、异文双录；现代学术结论（图式宋代定型、刘牧/朱熹图名互易、清儒辨伪、凌家滩玉版的推测性质）准确呈现并标注证据层级。
- 新人可入门：阅读地图、零基础路径、读图实操（点数/方位/幻方验证/卦序推演）。
- 通过 awesome-okf-xs 全部质量门（toctrees / bundles 计数对账 / utf8 / Sphinx 构建）。

## Non-Goals

- **不生成任何 git commit**（除非用户明确要求；OKF 子模块存在并行会话写共享索引，提交由用户统一处理）。
- 不提供占卜、算命、风水布局、择日等术数操作教程；不做灵验性评判。
- 不做《周易》经传全文教程（只取与图书学直接相关的《系辞》等段落；经传全读属 confucian/未来 yixue 束边界）。
- 不展开内丹/丹道实践（属 daoyi 束边界）；不展开中医九宫八风临床内容（属 huangdi-neijing/tcm 边界）。
- 不"解决"学术争议（如凌家滩玉版是否即洛书源头、太极图是否源自道教《无极图》）：争议以双方依据并列、标注"学者推测，非定论"处理。
- 不修改 vendor 区与任何构建配置（doc/conf.py 等）。

## Background & Context

- **入库位置现状**：bundles 总索引当前 324 束 / 61 组 / 14 域；think 域 28 束 · 17 组，已有 yinyangjia（阴阳家）、confucian、laozi、huangdi-neijing、daoyi 等相邻束，**无易学/河图洛书专题束**。
- **最新模板先例**：`think/yinyangjia/yinyangjia/`（2026-08-30 入库）验证了"亡佚/后出文献三层归属 + 事实编号 F-xxx + 异文 Y-xx + 未核对 U-xx + patterns.md 模式萃取"的完整范式，本束直接沿用。
- **核心学术事实基线**（R 阶段须逐条联网核实并登记信源 URL）：
  - 先秦两汉记载：《尚书·顾命》"河图在东序"、《论语·子罕》"河不出图"、《周易·系辞上》"河出图，洛出书，圣人则之"及"天地之数五十有五"章、《礼记·礼运》"河出马图"、《尚书·洪范》"天乃锡禹洪范九畴"、《大戴礼记·明堂》"二九四七五三六一八"、《易纬·乾凿度》"太一取其数以行九宫"、《数术记遗》甄鸾注"戴九履一"九宫诀。
  - 宋代图式：刘牧《易数钩隐图》以**九数为河图、十数为洛书**；朱熹、蔡元定《易学启蒙》《周易本义》卷首图录定为**十数河图、九数洛书**（后世通行）；传承谱系见于朱震《汉上易传·进周易表》（陈抟→种放→穆修→李之才→邵雍；穆修→周敦颐太极图）；邵雍《皇极经世书》先天学；周敦颐《太极图说》"无极而太极"。
  - 辨伪谱系：北宋欧阳修《易童子问》已疑《系辞》；清初胡渭《易图明辨》十卷系统考证图出道教/陈抟；黄宗羲《易学象数论》、黄宗炎《图书辨惑》、毛奇龄《河图洛书原舛编》；《四库全书总目》提要持保留态度；现代朱伯崑《易学哲学史》为易学哲学权威通史。
  - 出土实物：1987 年安徽含山凌家滩 M4 出土玉龟夹玉版（距今约 5300–5600 年），陈久金、张敬国《含山出土玉片图形试考》（《文物》1989 年第 4 期）提出洛书/八卦雏形说（学界有争议，须分层标注）；1977 年阜阳双古堆西汉汝阴侯墓出土太乙九宫式盘（与《乾凿度》九宫说对应）。
  - 西传：白晋（Joachim Bouvet）1701 年寄邵雍先天六十四卦图给莱布尼茨，莱布尼茨 1703 年发表二进制论文——常见误读"莱布尼茨受易经启发发明二进制"须纠正为"二进制发明在先、见图后发现吻合"；洛书九宫是世界最早三阶幻方（西方称 Lo Shu magic square）。

## Functional Requirements

- **FR-1**：新建分组 `think/hetu-luoshu/index.md`（type: group，含知识包列表与 hidden toctree）。
- **FR-2**：新建 bundle `think/hetu-luoshu/hetu-luoshu/`，含：
  - `index.md`（type: OKF，OKF v0.2 frontmatter：generated agent、verified process、status、stale_after；⚠️ 名实警示、三层框架速览、📚 快速导航、🚀 分读者快速开始、📖 学习路径、hidden toctree）
  - `facts.md`（R 阶段事实登记，目标 ≥50 条编号事实 F-001…，异文 Y-xx、未核对 U-xx 显式登记）
  - `insights.md`（I 阶段 ≥4 条四元组洞察：陈述/证据(F 编号)/反常识/行动）
  - `patterns.md`（E 阶段模式萃取："层累符号史阅读法"/"名实分层阅读法"，含触发场景、步骤、≥3 反模式、检验标准、跨领域迁移；V 后定稿）
  - `log.md`（R→I→E→V→C 创建日志）
  - `concepts/`（12 篇概念文档 + index.md，见下）
  - `examples/`（3 篇实践示例 + index.md）
  - `references/`（4 篇信源文档 + index.md）
- **FR-3**：concepts/ 12 篇：
  1. `00-what-is-hetu-luoshu.md` 名实之辨与阅读地图（三层所指总览、读者自测）
  2. `01-pre-qin-han-records.md` 先秦两汉记载层（祥瑞名物；顾命/洪范/子罕/系辞/礼运/管子/大戴礼记/汉书）
  3. `02-han-xiangshu-foundation.md` 汉易象数与数理资源（易纬乾凿度太一行九宫、数术记遗九宫诀、明堂九室、五行生成数、京房郑玄虞翻概貌）
  4. `03-chen-tuan-lineage.md` 陈抟与图书传承谱系（龙图序辨、种放—穆修—李之才—邵雍、朱震进周易表、道教渊源）
  5. `04-liu-mu-gouyin.md` 刘牧《易数钩隐图》（九为河图十为洛书体系、图九书十与洛书五行数、刘牧学派流传）
  6. `05-zhuxi-qimeng.md` 朱熹、蔡元定《易学启蒙》与《周易本义》（十为河图九为洛书定型、卷首九图、蔡元定入蜀得图公案、本图书义理）
  7. `06-shaoyong-xiantian.md` 邵雍先天学（皇极经世书、先天八卦/六十四卦方位与次序图、加一倍法、先天后天之辨）
  8. `07-taijitu-shuo.md` 周敦颐《太极图说》与太极图源流（无极而太极、五层生成图、朱震所记传承、朱陆之辩背景、道教无极图争议）
  9. `08-numerology.md` 数理结构（天地之数五十五、五行生成数方位与一六共宗等口诀、洛书三阶幻方纵横十五验证、洪范九畴）
  10. `09-qing-skepticism.md` 辨伪学史（欧阳修易童子问、胡渭易图明辨、黄宗羲易学象数论、黄宗炎图书辨惑、毛奇龄河图洛书原舛编、四库提要、朱伯崑易学哲学史及现代共识）
  11. `10-archaeology.md` 出土与实物（凌家滩玉龟玉版、文物 1989(4) 论文、阜阳汝阴侯墓太乙九宫式盘、洛阳龙马负图寺等纪念物；推测性解读显式标注）
  12. `11-legacy-east-west.md` 影响与西传（白晋—莱布尼茨通信与二进制误读纠正、Lo Shu 幻方西传、风水/内丹/术数运用的学术辨析、当代民间附会分层）
- **FR-4**：examples/ 3 篇：
  1. `01-xici-reading.md` 《系辞上》天地之数章 + 《顾命》《洪范》九畴逐句精读（原文全录、双源核对、白话大意、概念注释）
  2. `02-diagram-reading.md` 通行本图式读图实操（河图/洛书点数与方位五行核对、洛书纵横斜十五幻方验证、先天八卦次序加一倍法推演、太极图五层读法）
  3. `03-reading-plan.md` 五阶段通读计划（先秦记载→汉易数理→宋代图书→清代辨伪→出土与西传，含检验标准与常见陷阱）
- **FR-5**：references/ 4 篇：
  1. `01-core-texts.md` 先秦两汉原典信源（ctext.org / 维基文库 / 识典古籍 URL + 版本说明 + 稳定性风险标注）
  2. `02-song-qing-works.md` 宋清专著版本分级表（易数钩隐图、易学启蒙、周易本义、皇极经世书、太极图说、易图明辨、易学象数论、图书辨惑、河图洛书原舛编——道藏/通志堂经解/四库本与现代整理本）
  3. `03-modern-scholarship.md` 现代研究信源（朱伯崑《易学哲学史》、《文物》1989(4)、凌家滩正式报告 2006、李学勤/饶宗颐等论著，含证据层级）
  4. `04-cross-ref.md` 交叉引用（yinyangjia / confucian / confucius / laozi / zhuangzi / huangdi-neijing / daoyi / fangzhong / yangsheng 等束 + 外部数字人文资源）
- **FR-6**：更新两级索引：
  - `think/index.md`：frontmatter description、正文导览段、分组导航表加行、toctree 加 `hetu-luoshu/index`
  - `bundles/index.md`：frontmatter 计数（束 324→325、组 61→62，域 14 不变；**最终以 gates.bundles 实际对账为准**）、正文计数行、think 域节标题与分组表加行、两处 mermaid 中 think 节点标签补 hetu-luoshu
- **FR-7**：V 阶段委托新鲜上下文独立评审（只读），结果写入本 spec 目录 `review.md`；fail 项 materialize 为 tasks.md 修复任务，修复后复跑质量门。

## Non-Functional Requirements

- **NFR-1（学术准确性）**：全部事实性陈述可追溯至 facts.md 编号与 references 信源 URL；争议问题并列双方依据；推测性解读（凌家滩、道教图渊源等）显式标注"学者推测，非定论"。
- **NFR-2（规范一致性）**：文件名 kebab-case 英文、正文中文；每个非保留 .md 含可解析 YAML frontmatter 且 `type` 非空；含子目录的 index.md 均有 hidden toctree 引用全部内容文档；相对路径链接，禁止 file:///。
- **NFR-3（新人友好）**：零基础读者仅按 bundle 根"快速开始"即可完成首次阅读；每个概念有"是什么/为什么/怎么读"入口。
- **NFR-4（构建通过）**：`invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8`、`invoke build` 全部通过。

## Constraints

- **Technical**：Windows + WSL 环境；质量门在 `projects/awesome-okf-xs` 目录用 `invoke gates.*` 运行；OKF v0.2 frontmatter 规范；裸日期由 doc/conf.py 钩子兼容。
- **方法论**：七概念场景4 链路 R→I→E→V→C；G1（事实无因果词、≥50 条、可溯源）、G2（洞察四元组完整）、G3（模式可迁移：触发+步骤+≥3 反模式+迁移）、V 门（四视角、≥5 条具体意见、≥2 条采纳修正）为硬质量门；E 模式在 V 后定稿。
- **协作边界**：awesome-okf-xs 是 git submodule，按子项目规范执行；不 commit；子模块可能有并行会话写共享索引，更新 bundles/index.md 前先重读最新内容。
- **Dependencies**：网络可达 ctext.org、维基文库、识典古籍等公开信源（不可达项登记为 U-xx 并换源）。

## Assumptions

- 用户目标是"权威、真实的原文与解读"，故采用学术共识框架（图式宋代定型）而非通俗国学叙事；术数内容只做学术辨析。
- 新增 1 分组 + 1 知识包（非锚点组：组目录下为 bundle 子目录，bundle 内含 concepts/examples/references），束/组计数各 +1，最终以 gates.bundles 输出为准。

## Acceptance Criteria

### AC-1: Bundle 结构与 OKF v0.2 合规
- **Type**: `rule`
- **Given**: 知识包文件全部就位
- **When**: 检查 `think/hetu-luoshu/` 目录树与每个文件的 frontmatter
- **Then**: 分组 index 含 `type: group` 与 toctree；bundle 根 index 含 `type: OKF`、`okf_version: "0.2"`、generated/verified/status/stale_after；concepts 文档 `type: Concept`、references 文档 `type: Reference`；facts/insights/patterns/log 为保留/工作文档；含子目录的 index.md 均有 hidden toctree 覆盖全部内容文档
- **Pass Condition**: 目录结构与 yinyangjia 束逐项对应；无缺失文件
- **Evidence**: 目录树清单 + 各文件 frontmatter 摘录

### AC-2: 古籍原文双源核对与异文登记
- **Type**: `rule`
- **Given**: 全部公版古籍原文段落
- **When**: 逐段与 ctext.org 及维基文库/识典古籍比对
- **Then**: 引用原文与两个独立数字信源逐字一致；发现异文时在 facts.md 登记 Y-xx（异文双录 + 出处）；无法双源核对的段落登记 U-xx 并在正文标注
- **Pass Condition**: examples/01 与 concepts 中每段原文可在 references/01 找到双源 URL；无未登记的异文
- **Evidence**: facts.md 中 Y/U 登记记录 + references/01 URL 清单

### AC-3: 名实三层框架与学术共识准确
- **Type**: `rule`
- **Given**: 全部概念文档
- **When**: 学术评审抽查关键论断
- **Then**: ① 祥瑞名物（先秦两汉）/ 宋造图式 / 术数附会三层全程不混同；② "今传黑白点图式定型于宋代（刘牧→朱熹）"表述与朱伯崑《易学哲学史》等现代学术共识一致；③ 刘牧"九为河图"与朱熹"十为河图"的图名互易表述准确；④ 凌家滩玉版等考古材料的"洛书源头"说明确标注为部分学者推测、非定论；⑤ 莱布尼茨二进制与先天图关系表述为"二进制发明在先（1703 年前已完成）、见白晋寄图后发现数理吻合"，不沿袭"易经启发二进制"误说
- **Pass Condition**: 五项关键论断逐条在 facts.md 有 F 编号与信源支撑，V 评审无事实性 fail
- **Evidence**: facts.md 对应条目 + references/02、03 信源

### AC-4: 术数内容学术辨析边界
- **Type**: `rule`
- **Given**: concepts/11 及全部正文
- **When**: 通读涉及风水/术数/占卜/内丹的内容
- **Then**: 仅作历史与文化现象的学术辨析，不含任何起卦、排盘、布局、择日、断吉凶等操作性步骤；民间附会说法有显式层次标注
- **Pass Condition**: V 评审"定位与边界"视角无越界 fail
- **Evidence**: review.md 边界检查结论

### AC-5: 新人可入门性
- **Type**: `rubric`
- **Dimension**: 零基础读者的可进入性与可完成性
- **Scale**: 1-5
- **Anchors**: 1 = 无阅读地图、术语堆砌、新人不知从何读起；3 = 有导航但读图/原文环节缺操作指引；5 = 阅读地图 + 分读者路径 + 读图实操 + 通读计划齐备，新人按"快速开始"可独立完成首次阅读并建立三层框架
- **Pass Threshold**: >= 4
- **Evidence**: bundle 根 index 导航结构 + examples/02、03 实操性评审

### AC-6: 质量门与构建全通过
- **Type**: `rule`
- **Given**: 全部文件与索引更新完成
- **When**: 在 `projects/awesome-okf-xs` 运行 `invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8`、`invoke build`
- **Then**: 零断链、零孤立文档；束/组/域计数五面对账一致（bundles/index.md frontmatter、计数行、域节标题、分组表束数列、toctree）；UTF-8 无 BOM；Sphinx 构建零错误
- **Pass Condition**: 四条命令全部退出码 0
- **Evidence**: 四条命令的完整输出

### AC-7: V 阶段独立对抗评审
- **Type**: `rule`
- **Given**: 实施队列全部完成
- **When**: 委托新鲜上下文的只读评审（四视角：魔鬼代言人=事实/信源攻击、新人=可入门性、老板=价值与边界、未来=长期时效）
- **Then**: 评审意见 ≥5 条且具体（无客套话），≥2 条被采纳修正；结果记录于 spec 目录 review.md；fail 项全部修复并复跑 AC-6 质量门
- **Pass Condition**: review.md 最新 Review 结果为 pass，无遗留 actionable finding
- **Evidence**: review.md（Review History + 检查点结论）

### AC-8: 信源质量与可追溯性
- **Type**: `rubric`
- **Dimension**: 信源权威性、URL 可达性与事实可追溯密度
- **Scale**: 1-5
- **Anchors**: 1 = 大量陈述无出处、URL 失效或来自通俗自媒体；3 = 关键事实有信源但部分 URL 不可达或分级模糊；5 = 事实性陈述原则上条条可追溯，原典用 ctext/维基文库双源、现代研究用出版社/期刊级信源并分级，URL 经抽测可达，不可达项已换源或登记 U-xx
- **Pass Threshold**: >= 4
- **Evidence**: references/ 四篇信源文档 + facts.md 溯源密度抽查

## Open Questions

- 无（三项范围决策已经用户确认；计数以质量门实际输出为准；争议学术问题按"并列双方依据 + 推测标注"处理）。
