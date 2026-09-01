# 马王堆房中简帛阅读教程 OKF Wiki Spec

> **change-id**: `create-mawangdui-fangzhong-wiki`
> **主题目录**: `standards-tools`（沿 create-sexology-classics-wiki / create-graphql-wiki-tutorial 先例）
> **七概念链路**: 场景4 知识沉淀 R→I→E→V→C（R/I/E 为实施主体，V 为实施后强制独立评审，C 仅在用户要求提交时执行）
> **内容敏感度**: 公开（Public）——考古出土文献与学术研究对象，教育性阅读教程，遵守学术引介尺度
> **关联既有资产**: `think/sexology/classics-reading/concepts/01-ancient-china.md` 已含马王堆概览一节，本 bundle 为其专题深化，两者交叉引用、不重复

## Why

`projects/awesome-okf-xs/doc/bundles` 的 think/sexology 分组目前仅有一个通览性教程（六大板块各一节），马王堆房中简帛作为**现存最早的房中医学文献实物**（1973 年三号墓出土，下葬于公元前 168 年），只有约 400 字的概览。这批文献（竹简《十问》《合阴阳》《天下至道谈》+ 帛书《养生方》《房内记》《胎产书》相关部分）是理解中国早期身体观、气论哲学与养生方技的枢纽，2024 年《长沙马王堆汉墓简帛集成》修订本出版又带来大量释文更新，需要一份以"出土文本为经、研究著作为纬"的专题阅读教程知识包。

## What Changes

- **新增 bundle** `doc/bundles/think/sexology/mawangdui-fangzhong-reading/`，结构（仿 boshu-reading/classics-reading 范式）：
  - `index.md`（bundle 根，OKF v0.2 frontmatter，快速导航/定位对比/学习路径）
  - `facts.md`（R 阶段事实登记，带编号与信源，【待核验】条目显式标注）
  - `insights.md`（≥4 条四元组洞察 + 知识地图）
  - `log.md`（创建日志）
  - `concepts/`（约 8 篇概念文档，见 ADDED Requirements）
  - `examples/`（3 篇实践示例）
  - `references/`（4 篇信源文档）
- **更新索引**：
  - `think/sexology/index.md`：分组导航表加行 + toctree 加 `mawangdui-fangzhong-reading/index`
  - `think/index.md`：无需改动（分组层不变）
  - `bundles/index.md`：计数 289→290 束（组数 35 不变），think 域 "8 束 · 5 组"→"9 束 · 5 组"，sexology 行说明更新
- **更新既有文档**：`classics-reading/concepts/01-ancient-china.md` 马王堆一节末尾加交叉引用链接（指向新 bundle）
- **登记**：`.trae/specs/README.md` 与 `standards-tools/README.md` 看板登记本 spec
- **范围决策**（沿用 create-sexology-classics-wiki 已确认先例）：
  1. 收录范围=马王堆房中简帛专题：竹简三种 + 帛书《养生方》《房内记》（原《杂疗方》析出）+《胎产书》房中相关内容，兼及《天下至道谈》与《素问》七损八益对照
  2. 内容定位=阅读教程为主 + 原文选读与研究著作指南
  3. 原文引用=学术引介尺度：出土公版文献引篇名/核心命题/少量代表性片段（学术介绍口吻）；现代研究著作只介绍观点与结构，不录原文；全部内容为教育性、学术性表述

## Impact

- **Affected specs**: `create-sexology-classics-wiki`（已完成，仅新增交叉引用，不改变其已交付内容）
- **Affected code**（均为文档资产，无代码）:
  - 新建：`projects/awesome-okf-xs/doc/bundles/think/sexology/mawangdui-fangzhong-reading/**`（约 22 个文件：index 1 + facts/insights/log 3 + concepts 9 + examples 4 + references 5）
  - 修改：`think/sexology/index.md`、`bundles/index.md`、`classics-reading/concepts/01-ancient-china.md`（仅加链接）
  - 更新：`.trae/specs/README.md`、`.trae/specs/standards-tools/README.md`
- **不涉及**：git commit（除非用户明确要求）、vendor 区、任何代码构建逻辑

## ADDED Requirements

### Requirement: Bundle 结构与模板一致性

系统 SHALL 在 `think/sexology/mawangdui-fangzhong-reading/` 下创建完整 OKF v0.2 bundle，文件组织、frontmatter 字段、toctree 写法 SHALL 与 sexology/classics-reading 模板一致：

- bundle 根 index.md frontmatter：`type: OKF`、`title`、`description`、`tags`、`version`、`source`、`generated: {by: "agent:...", at: ISO8601}`、`verified: {by: "process:seven-concepts-v", at: ...}`、`status`、`stale_after`、`okf_version: "0.2"`
- 概念文档 `type: Concept`，信源文档 `type: Reference`，均带 `sources` 逐声明归因
- 文件名 kebab-case 英文，正文全部中文
- 含子目录的每级 index.md 必须有 hidden toctree 引用全部内容文档

#### Scenario: 新读者从 bundle 根入口进入
- **WHEN** 读者打开 `mawangdui-fangzhong-reading/index.md`
- **THEN** 能看到📚快速导航、🚀分读者路径、🎯定位对比表（与 classics-reading 通览教程的分工）、📖推荐学习路径
- **AND** 所有链接指向真实存在的文档

### Requirement: 概念文档按"出土文本—理论—整理史—研究史"组织

concepts/ SHALL 包含约 8 篇概念文档：

1. `00-excavation-background.md`：马王堆汉墓与三号墓简帛库——发掘史（1972-1974）、墓主与下葬年代（前 168 年）、五十余种简帛总览、"四种讲养生和房中的简书"定位
2. `01-text-corpus.md`：房中简帛文本群总览——《十问》《合阴阳》《天下至道谈》三种竹简与帛书《养生方》《房内记》《胎产书》的形制、篇题由来（整理者拟题 vs 原题）、内容结构与残损状况
3. `02-seven-losses-eight-benefits.md`：《天下至道谈》核心命题——七损八益的文本结构与内涵，及与《素问·阴阳应象大论》"七损八益"悬案的对照
4. `03-he-yin-yang-techniques.md`：《合阴阳》的概念体系——戏道、十动、十节、十修、八动、十已之征等术语的学术界定（术语仅作学术介绍）
5. `04-shiwen-dialogue.md`：《十问》的问答结构与精气论——十组帝王/方士问答、保存的已佚古房中书线索、"气—精—神—神明"递进观
6. `05-theoretical-framework.md`：理论底座——气论主干、精气论、阴阳学说的初步运用、天人相参（依据朱越利等研究的学术综述口径）
7. `06-editorial-history.md`：整理出版史——1974 出土 → 帛书整理小组（1974 起，裘锡圭等）→ 早期释文 → 2014《长沙马王堆汉墓简帛集成》初版 → 2024 修订本（重写篇目、近千处修订、新缀残片）
8. `07-research-landscape.md`：研究著作地图——李零《中国方术考》第七章、周贻谋《马王堆简帛与古代房事养生》、朱越利系列论文、李建民医疗史研究、海外汉学（Harper 等）与日本《马王堆出土文献译注丛书》；入门路径建议

#### Scenario: 按概念检索文本
- **WHEN** 读者想了解"七损八益"的出土文本依据
- **THEN** 在 02 文档中能找到《天下至道谈》的篇题、结构、与《素问》关系的学术讨论
- **AND** 事实性陈述均可在 facts.md 找到编号、在 references/ 找到信源

### Requirement: 事实登记与待核验标注

facts.md SHALL 完整登记 R 阶段采集的事实（目标 ≥80 条），按板块分组制表（出土背景/文本群/核心概念/整理史/研究史/传世文献关系），SHALL 对调研中发现的争议条目保留【待核验】标注，至少包括：

- 三号墓墓主身份表述（利豨说的通行性与异议）
- 《房内记》与《杂疗方》的分合（2014 集成析分，不同文献表述不一）
- 各篇整理者拟题与原题的区分
- 周贻谋著作的出版社与版次细节
- 海外译注丛书（东方书店）各卷覆盖范围

**已确认的基准事实**（实施时不得偏离）：
- 三号墓下葬于汉文帝前元十二年（前 168 年）；马王堆汉墓 1972-1974 年发掘
- 《长沙马王堆汉墓简帛集成》裘锡圭主编，中华书局 2014 年 6 月初版、2024 年 7 月修订本（全七册）
- 2024 年修订本重写《养生方》等篇目、修订近千处、新缀/公布残片二百余片
- 有字简帛五十余种、约 13 万字；房中相关简书四种（含《十问》《合阴阳》《天下至道谈》等）

#### Scenario: 读者核验一条争议表述
- **WHEN** 读者在概念文档看到墓主或篇题表述
- **THEN** 该处要么采用已核实表述并附信源，要么明确标注争议并指向 facts.md 对应条目

### Requirement: 原文引用遵守学术引介尺度

所有引用 SHALL 遵守：

- 出土公版文献（简帛释文）：引篇名、核心命题、少量代表性片段，以学术介绍口吻呈现
- 现代研究著作（李零、周贻谋、朱越利等）：只介绍观点与结构，不录原文段落
- 全部内容为教育性、学术性表述，不含露骨描写；技术性术语以文献学/医学史口径呈现

#### Scenario: 内容得体性检查
- **WHEN** V 阶段评审者通读全部产出文档
- **THEN** 不发现超出学术引介尺度的摘录或露骨描写

### Requirement: 索引与计数一致性

- bundles/index.md frontmatter：`total_bundles: 290`（groups 35、domains 13 不变）
- think 域表格行改为"9 束 · 5 组"，sexology 行说明纳入新 bundle
- sexology/index.md 分组导航表加行 + toctree 加条目
- classics-reading 01-ancient-china.md 马王堆节末加交叉引用

#### Scenario: toctree 质量门通过
- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.toctrees`
- **THEN** 零断链、零孤立文档
- **AND** `invoke gates.utf8` 通过；`invoke build` Sphinx 构建成功（构建警告仅允许来自其他既有 bundle）

### Requirement: V 阶段独立对抗评审

实施完成后 SHALL 委托新鲜上下文的独立评审（general_purpose_task 只读），按四视角审查：

1. **事实准确性**：抽查事实条目与信源对应、待核验标注保留、基准事实正确
2. **新人可入门性**：零基础读者能否通过 index.md 与 examples 进入
3. **定位与边界**：是否为专题阅读教程（与 classics-reading 通览不重复）；是否越界到露骨内容
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
- 不覆盖马王堆非房中简帛（《老子》《周易》《五星占》等仅在背景篇简述）
- 不解决【待核验】清单（保留标注，留待权威信源更新）