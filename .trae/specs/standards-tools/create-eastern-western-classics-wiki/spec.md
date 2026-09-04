---
title: "《欲经》与《爱经》双经典阅读教程 OKF Wiki"
status: "draft"
---

# 《欲经》与《爱经》双经典阅读教程 OKF Wiki Spec

> **change-id**: `create-eastern-western-classics-wiki`
> **主题目录**: `standards-tools`（沿 create-sexology-classics-wiki / create-mawangdui-fangzhong-wiki / create-fangzhong-bajia-wiki 先例）
> **七概念链路**: 场景4 知识沉淀 R→I→E→V→C（R/I/E 为实施主体，V 为实施后强制独立评审，C 仅在用户要求提交时执行）
> **内容敏感度**: 公开（Public）——古典文献学术研究对象，教育性阅读教程，遵守学术引介尺度，不含露骨描写
> **方法论装载**: seven-concepts-cmd（session=sc-20260831-eastern-western-classics-wiki）
> **关联既有资产**: `think/sexology/classics-reading/concepts/02-eastern-western-classics.md` 已含两部经典约 800 字概览（facts.md 仅 F-WEST-033/034 两条事实），本 bundle 为其专题深化，两者交叉引用、不重复
> **范围确认**: 用户已确认收录范围=《欲经》+《爱经》双经典并置（AskUserQuestion 2026-08-31）

## Why

`projects/awesome-okf-xs/doc/bundles/think/sexology/classics-reading/concepts/02-eastern-western-classics.md` 对印度《欲经》（Kāmasūtra）与罗马奥维德《爱经》（Ars Amatoria）仅有概览性介绍：《欲经》的七品结构、注疏传统、伯顿译本的"二次发现"细节、多尼格学术译本的解读框架均无从展开；《爱经》的三卷结构、哀歌体诗学、"一首诗和一个错误"放逐公案的学术讨论、中世纪禁毁与重估史也只有一句话。两部古典是"以术论欲"传统中与中国房中文献并置阅读的枢纽（该文档第三节已给出对照表），读者需要一份以"文本结构为经、译介与接受史为纬"的双经典专题阅读教程知识包。

## What Changes

- **新增 bundle** `doc/bundles/think/sexology/eastern-western-classics-reading/`（sexology 分组下新 bundle），结构（仿 classics-reading 范式）：
  - `index.md`（bundle 根，OKF v0.2 frontmatter，快速导航/定位对比/学习路径）
  - `facts.md`（R 阶段事实登记，≥60 条带信源编号事实，【待核验】条目显式标注）
  - `insights.md`（≥4 条四元组洞察 + 知识地图）
  - `log.md`（创建日志）
  - `concepts/`（8 篇概念文档 + index，见 ADDED Requirements）
  - `examples/`（3 篇实践示例 + index）
  - `references/`（4 篇信源文档 + index）
- **更新索引**：
  - `think/sexology/index.md`：分组导航表加行 + toctree 加 `eastern-western-classics-reading/index`
  - `bundles/index.md`：计数 289→290 束（groups 35 不变），think 域 "8 束 · 5 组"→"9 束 · 5 组"，sexology 行束数 1→2 与说明更新（实施时以磁盘实际状态为准核对，防止并行 spec 先行变更计数）
- **交叉引用**：`classics-reading/concepts/02-eastern-western-classics.md` 《欲经》节与《爱经》节末各加一处指向新 bundle 的深度专题链接（不改既有事实与结论）
- **登记**：`.trae/specs/README.md` 与 `standards-tools/README.md` 看板登记本 spec
- **范围决策**（沿用 create-sexology-classics-wiki 已确认先例）：
  1. 收录范围=《欲经》+《爱经》双经典：《欲经》覆盖 kama-shastra 传统、文本结构、注疏、译介史；《爱经》覆盖文本结构、诗学、放逐公案、禁毁与重估史、中译；兼及与中国房中文献的三方对照
  2. 内容定位=阅读教程为主 + 原文选读与研究著作指南
  3. 原文引用=学术引介尺度：公版古典文献（梵文/拉丁文古典）引篇名、核心命题、少量代表性片段（学术介绍口吻）；现代研究著作只介绍观点与结构，不录原文；全部内容为教育性、学术性表述，不含露骨描写

## Impact

- **Affected specs**: `create-sexology-classics-wiki`（已完成，仅新增交叉引用，不改变其已交付内容）；与未实施的 `create-mawangdui-fangzhong-wiki` / `create-fangzhong-bajia-wiki` 为同分组平行纵深关系（计数以实施时磁盘状态核对）
- **Affected code**（均为文档资产，无代码）:
  - 新建：`projects/awesome-okf-xs/doc/bundles/think/sexology/eastern-western-classics-reading/**`（约 22 个文件：index 1 + facts/insights/log 3 + concepts 9 + examples 4 + references 5）
  - 修改：`think/sexology/index.md`、`bundles/index.md`、`classics-reading/concepts/02-eastern-western-classics.md`（仅加链接）
  - 更新：`.trae/specs/README.md`、`.trae/specs/standards-tools/README.md`
- **不涉及**：git commit（除非用户明确要求）、vendor 区、任何代码构建逻辑

## ADDED Requirements

### Requirement: R 阶段调研覆盖四条线并过 G1 门

实施 SHALL 先完成系统性调研，产出 ≥60 条带信源的事实（编号 F- 起），覆盖四条线，中间产物存放于 `.temp/eastern-western-classics-research/`（任务完成后清理）：

1. **《欲经》文本线**：筏蹉衍那（Vātsyāyana）署名问题、成书年代学界区间（约 3-5 世纪，含迦腻色迦时期相关说法）、七品（adhikarana）结构总览（总论/性爱姿态/婚姻/人妻/交际/秘术等部分的学术界定）、kama-shastra 传统与人生三目的（dharma/artha/kama）思想背景、主要注疏（如 Yaśodharā 的 Jayamaṅgalā 等）
2. **《欲经》译介线**：1883 年伯顿主持英译的 Kama Shastra Society 私人订阅背景与"东方情色奇书"误读的形成、Doniger & Kakar 2002 牛津学术译本的解读框架、主要中译本状况（署名与出版信息【待核验】处理）
3. **《爱经》文本线**：奥维德生平定位（前 43-约 17/18 年）、《爱经》三卷结构（卷一/卷二面向男性、卷三面向女性）、哀歌体教谕诗的诗学特征、约前 2 年出版（一说至公元 1 年）、罗马城市生活细节与反讽语调
4. **《爱经》接受线**：公元 8 年奥维德放逐与"一首诗和一个错误"（carmen et error）公案、中世纪禁毁与抄本流传、近代重估、主要译本（含戴望舒中译的底本与出版信息【待核验】）

G1 质量门：事实无因果推断词（"因为/导致/所以"）、每条可追溯信源 URL 或权威书目、关键数据（年代区间/卷数/品名/译者）完整。

#### Scenario: 读者核验一条文本结构信息
- **WHEN** 读者在概念文档中看到《欲经》某品名或《爱经》某卷内容界定
- **THEN** 该信息可在 facts.md 找到对应编号、在 references/ 信源文档找到出处
- **AND** 年代与署名均采用区间性/存疑性表述，无凭记忆的确定性转录

### Requirement: Bundle 结构与模板一致性

系统 SHALL 在 `think/sexology/eastern-western-classics-reading/` 下创建完整 OKF v0.2 bundle，文件组织、frontmatter 字段、toctree 写法 SHALL 与 sexology/classics-reading 模板一致：

- bundle 根 index.md frontmatter：`type: OKF`、`title`、`description`、`tags`、`version`、`source`、`generated: {by: "agent:seven-concepts-r-i-e", at: ISO8601}`、`verified: {by: "process:seven-concepts-v", at: ...}`、`status`、`stale_after`、`okf_version: "0.2"`
- 概念文档 `type: Concept`，信源文档 `type: Reference`，均带 `sources` 逐声明归因
- 文件名 kebab-case 英文，正文全部中文，路径引用为相对路径（无 file:/// 绝对路径）
- 含子目录的每级 index.md 必须有 hidden toctree 引用全部内容文档

#### Scenario: 新读者从 bundle 根入口进入
- **WHEN** 读者打开 `eastern-western-classics-reading/index.md`
- **THEN** 能看到📚快速导航、🚀分读者路径、🎯定位对比表（与 classics-reading 通览教程的分工）、📖推荐学习路径
- **AND** 所有链接指向真实存在的文档

### Requirement: 概念文档按"双经典并置 + 对照"组织

concepts/ SHALL 包含 8 篇概念文档：

1. `00-kama-shastra-background.md`：印度爱欲科学传统——人生三目的（dharma/artha/kama）、kama-shastra 文献谱系、《欲经》在其中的经书体（sutra）定位
2. `01-kamasutra-text.md`：《欲经》文本总览——署名与成书年代（区间性表述）、七品结构与各品主题界定、"生活百科而非性技手册"的编纂性质
3. `02-kamasutra-commentary.md`：《欲经》注疏与印度本土接受——主要注疏传统、文本在印度的流传与地位变迁
4. `03-kamasutra-translation.md`：《欲经》译介史——1883 伯顿英译（Kama Shastra Society、私人订阅、误读形成）→ 20 世纪诸译本 → Doniger & Kakar 2002 学术译本的范式转换 → 中译状况
5. `04-ovid-context.md`：奥维德与罗马哀歌传统——生平定位、哀歌体教谕诗的诗学特征、《爱经》在奥维德作品序列中的位置
6. `05-ars-amatoria-text.md`：《爱经》文本总览——三卷结构（卷一/卷二面向男性、卷三面向女性）、反讽语调与罗马城市生活细节、约前 2 年出版的年代讨论
7. `06-ars-amatoria-reception.md`：《爱经》接受史——公元 8 年放逐与"一首诗和一个错误"公案、中世纪禁毁与抄本流传、近代重估、中译（戴望舒译本等）
8. `07-comparative-reading.md`：三方对照阅读——中国房中文献/《欲经》《爱经》的文体、归属传统、核心关怀、接受史四维对照（扩展既有对照表），及"文体取决于知识传统归属"的方法论收束

#### Scenario: 按概念检索文本
- **WHEN** 读者想了解"伯顿译本为何造成误读"
- **THEN** 在 03 文档中能找到 Kama Shastra Society 背景、私人订阅形式与误读机制的学术讨论
- **AND** 事实性陈述均可在 facts.md 找到编号、在 references/ 找到信源

### Requirement: 事实登记与待核验标注

facts.md SHALL 完整登记 R 阶段采集的事实（目标 ≥60 条），按板块分组制表（《欲经》文本/《欲经》译介/《爱经》文本/《爱经》接受/三方对照），SHALL 对调研中发现的争议条目保留【待核验】标注，至少包括：

- 《欲经》成书年代（3-5 世纪区间说与迦腻色迦时期说的并存）
- 筏蹉衍那生平与署名的可信度
- 《欲经》中译本的译者署名与出版信息
- 伯顿译本的实际参与者（Kama Shastra Society 成员角色）
- 《爱经》出版年（前 2 年说与稍后说）
- 奥维德放逐原因（"一首诗和一个错误"的学术讨论）
- 戴望舒译《爱经》的底本与出版信息

**已确认的基准事实**（实施时不得偏离，来自既有 facts.md 与概念文档）：
- 《欲经》托名筏蹉衍那，属印度 kama-shastra（爱欲科学）传统，成书约公元 3-5 世纪（区间性判断）
- kama 与 dharma、artha 并列为印度传统人生三目的
- 伯顿（Richard Burton）主持英译 1883 年以私人订阅形式刊行
- Doniger & Kakar 合译本 2002 年牛津大学出版社出版，为当前推荐学术译本
- 奥维德《爱经》为拉丁哀歌体教谕诗，约前 2 年出版（一说稍后至公元 1 年）
- 公元 8 年奥维德遭奥古斯都放逐，自称"一首诗和一个错误"，传统认为该诗即《爱经》

#### Scenario: 读者核验一条争议表述
- **WHEN** 读者在概念文档看到年代、译者或放逐原因表述
- **THEN** 该处要么采用已核实表述并附信源，要么明确标注争议并指向 facts.md 对应条目

### Requirement: 原文引用遵守学术引介尺度

所有引用 SHALL 遵守：

- 公版古典文献（《欲经》《爱经》）：引篇名、核心命题、少量代表性片段，以学术介绍口吻呈现；《欲经》涉及姿态清单等内容时仅作品类界定与结构性介绍，不做露骨转录
- 现代研究著作（Doniger、Kakar 及其他研究者）：只介绍观点与结构，不录原文段落
- 全部内容为教育性、学术性表述，不含露骨描写

#### Scenario: 内容得体性检查
- **WHEN** V 阶段评审者通读全部产出文档
- **THEN** 不发现超出学术引介尺度的摘录或露骨描写

### Requirement: 索引与计数一致性

- bundles/index.md：`total_bundles` 按实施时磁盘实际值 +1（当前 289→290），groups 不变（当前 35）
- think 域表格行束数 +1（当前 "8 束 · 5 组"→"9 束 · 5 组"），组数不变
- sexology 行束数 1→2、说明纳入新 bundle
- sexology/index.md 分组导航表加行 + toctree 加条目
- classics-reading 02-eastern-western-classics.md 《欲经》《爱经》两节末各加交叉引用

#### Scenario: toctree 质量门通过
- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.toctrees`
- **THEN** 零断链、零孤立文档
- **AND** `invoke gates.utf8` 通过；`invoke build` Sphinx 构建成功（构建警告仅允许来自其他既有 bundle）

### Requirement: V 阶段独立对抗评审

实施完成后 SHALL 委托新鲜上下文的独立评审（general_purpose_task 只读），按四视角审查：

1. **事实准确性**：抽查事实条目与信源对应、待核验标注保留、基准事实正确、年代均为区间性表述
2. **新人可入门性**：零基础读者能否通过 index.md 与 examples 进入
3. **定位与边界**：是否为双经典专题阅读教程（与 classics-reading 通览不重复）；是否越界到露骨内容
4. **时效与规范**：frontmatter 合法性、stale_after、索引计数一致

评审结果 SHALL 记录于本 spec 目录 `review.md`；fail 项 materialize 为 tasks.md 修复任务。

## MODIFIED Requirements

（无——对既有文档仅新增交叉引用链接，不修改既有 Requirement）

## REMOVED Requirements

（无）

## 非目标（Out of Scope）

- 不生成任何 git commit（除非用户明确要求）
- 不修改 vendor 区文件
- 不收录露骨原文、不做色情内容介绍
- 不覆盖 kama-shastra 传统中《欲经》以外的其他文献专题（仅在背景篇简述）
- 不覆盖奥维德《爱经》以外的其他作品专题（《变形记》《爱的医疗》等仅在序列定位中简述）
- 不解决【待核验】清单（保留标注，留待权威信源更新）
