---
title: "《汉书·艺文志》房中八家 OKF Wiki 教程"
status: "draft"
---

# 《汉书·艺文志》房中八家 OKF Wiki 教程 Spec

> **change-id**: `create-fangzhong-bajia-wiki`
> **主题目录**: `standards-tools`（沿 create-sexology-classics-wiki / create-yangsheng-classics-wiki 先例）
> **七概念链路**: 场景4 知识沉淀 R→I→E→V→C（R/I 在实施期执行，本 spec 对应 E 阶段实施蓝图，V 为实施后强制独立评审，C 默认不执行 git commit）
> **内容敏感度**: 公开（Public）——古典文献学术研究对象，教育性阅读教程，遵守学术引介尺度，不含露骨描写
> **方法论装载**: seven-concepts-cmd（compiled-methodology.md），session=sc-20260831-fangzhong-bajia-wiki

## Why

`projects/awesome-okf-xs/doc/bundles/think/sexology/classics-reading/concepts/01-ancient-china.md` 对"汉志房中八家"仅有一段概览性提及。《汉书·艺文志·方技略》房中类是现存最早的系统性房中文献目录，八家著作全部亡佚、文本散见于《医心方》等后世辑引，读者面临三重门槛：书目著录（书名/卷数/班固注）无从查核、佚文辑佚链条分散、现代研究解读（李零、马王堆医书互证等）与传世目录之间缺乏桥接。需要一份以"目录学著录为锚点、以辑佚与出土文献互证为方法、以可溯源事实为底座"的专题阅读教程知识包。

## What Changes

- **新增 bundle** `doc/bundles/think/sexology/fangzhong-bajia-reading/`（sexology 分组下第二个 bundle），结构：
  - `index.md`（bundle 根，OKF v0.2 frontmatter，快速导航/定位对比/学习路径）
  - `facts.md`（R 阶段事实登记，≥40 条带信源编号事实，【待核验】条目显式标注）
  - `insights.md`（≥3 条四元组洞察 + 知识地图）
  - `log.md`（创建日志）
  - `concepts/`（约 8 篇概念文档，见 ADDED Requirements）
  - `examples/`（3 篇实践示例）
  - `references/`（≥4 篇信源文档）
- **更新索引**：
  - `think/sexology/index.md`：分组导航表加行 + toctree 加 `fangzhong-bajia-reading/index`
  - `bundles/index.md`：计数 289→290 束、35→36 组、think 域 "8 束 · 5 组"→"9 束 · 6 组"、sexology 分组行束数与说明更新
- **交叉引用**：`sexology/classics-reading/concepts/01-ancient-china.md` 与 `sexology/classics-reading/references/further-reading.md` 各加一处指向新 bundle 的深度专题链接
- **范围决策**（依用户指令与先例默认）：
  1. 收录范围=房中八家专题：以《汉志》著录八家为锚点，覆盖著录原文、亡佚与辑佚、出土文献互证、现代解读四条线
  2. 内容定位=阅读教程为主+著作提要（与 sexology/classics-reading 定位一致，形成"通论→专题"纵深）
  3. 原文引用=学术引介尺度：公版古典文献引篇名/核心命题/少量代表性片段；全部教育性、学术性表述，不含露骨性描写

## Impact

- **Affected specs**: 无既有 spec 依赖；与已交付的 `create-sexology-classics-wiki` 为同分组纵深扩展关系（仅新增交叉引用，不改其事实与结论）
- **Affected code**（均为文档资产，无代码）:
  - 新建：`projects/awesome-okf-xs/doc/bundles/think/sexology/fangzhong-bajia-reading/**`（约 20 个文件）
  - 修改：`projects/awesome-okf-xs/doc/bundles/think/sexology/index.md`、`projects/awesome-okf-xs/doc/bundles/index.md`、`sexology/classics-reading/concepts/01-ancient-china.md`、`sexology/classics-reading/references/further-reading.md`
  - 更新：`.trae/specs/README.md` 与 `.trae/specs/standards-tools/README.md`（看板登记）
- **不涉及**：git commit（除非用户明确要求）、vendor 区、任何代码构建逻辑

## ADDED Requirements

### Requirement: R 阶段调研覆盖四条线并过 G1 门

实施 SHALL 先完成系统性调研，产出 ≥40 条带信源的事实（编号 F-001 起），覆盖四条线，中间产物存放于 `.temp/fangzhong-bajia-research/`（任务完成后清理）：

1. **著录原文线**：《汉书·艺文志·方技略》房中类完整著录——八家书名、卷数、班固自注（如有）、房中类小序原文；以 ctext.org 或权威点校本为据，逐条核对，不得凭记忆转录
2. **亡佚辑佚线**：八家各自的亡佚时代判断（仅区间性表述）、佚文见存于哪些后世文献（如《医心方》卷廿八、《素女经》系文献、《玉房秘诀》系文献等）、辑佚本状况（如双梅景闇丛书等）
3. **出土文献线**：马王堆汉墓医书房中类篇目（《十问》《合阴阳》《天下至道谈》等）与房中八家的时代关系与内容互证、其他相关简帛材料
4. **现代解读线**：李零等学者对房中书的研究结论、房中书的性质判定（医学/养生/性文化）、《汉志》分类学意义（方技略四分：医经/经方/房中/神仙）

G1 质量门：事实无因果推断词、每条可追溯信源 URL 或权威书目、关键数据（卷数/篇名/年代区间）完整。

#### Scenario: 读者核验一条著录信息
- **WHEN** 读者在概念文档中看到某家书名与卷数
- **THEN** 该信息可在 facts.md 找到对应编号、在 references/ 信源文档找到出处（ctext.org 页面或权威书目）
- **AND** 与《汉书·艺文志》原文一致，无凭记忆的转录错误

### Requirement: Bundle 结构与模板一致性

系统（awesome-okf-xs 文档工程）SHALL 在 `think/sexology/fangzhong-bajia-reading/` 下创建完整 OKF v0.2 bundle，其文件组织、frontmatter 字段、toctree 写法 SHALL 与 boshu-reading / classics-reading bundle 模板一致：

- bundle 根 index.md frontmatter：`type: OKF`、`title`、`description`、`tags`、`version`、`source`、`generated: {by: "agent:...", at: ISO8601}`、`verified: {by: "process:seven-concepts-v", at: ...}`、`status`、`stale_after`、`okf_version: "0.2"`
- 概念文档 `type: Concept`，信源文档 `type: Reference`，均带 `sources` 逐声明归因（引用格式为 bundle 相对路径）
- 文件名 kebab-case 英文，正文全部中文
- 含子目录的每级 index.md 必须有 hidden toctree 引用全部内容文档

#### Scenario: 新读者从 bundle 根入口进入
- **WHEN** 读者打开 `think/sexology/fangzhong-bajia-reading/index.md`
- **THEN** 能看到📚快速导航、🚀分读者路径的快速开始、🎯Bundle 定位对比表（与 sexology/classics-reading 通论教程的分工）、📖推荐学习路径
- **AND** 所有链接可点击且指向真实存在的文档

### Requirement: 概念文档按"著录→辑佚→互证→解读"组织

concepts/ SHALL 包含约 8 篇概念文档，组织逻辑为"目录学著录为锚点、辑佚与出土互证为方法、现代解读为落点"：

1. `00-yiwenzhi-fangji-lue.md`：《汉书·艺文志·方技略》与房中类——方技略四分结构、房中类小序、房中八家在汉代知识图谱中的位置
2. `01-eight-schools-catalog.md`：房中八家著录总表——逐家书名/卷数/班固注/存佚状态，附著录原文对照
3. `02-rongcheng-wuyin.md`：容成与务成两家——托名传统、导引之道与务成子传说谱系
4. `03-huangdi-school.md`：黄帝系诸书——黄帝托名现象、各家著录差异与主题推断（基于佚文与书名分析，明确标注推断层级）
5. `04-sanyangban-and-others.md`：三阳班及其他——逐家提要，亡佚无佚文者的"仅存书目"处理方式
6. `05-fragments-chain.md`：辑佚链条——《医心方》卷廿八等后世辑引、《素女经》《玉房秘诀》《洞玄子》系文献与八家的关系、双梅景闇丛书等辑佚本
7. `06-excavated-texts.md`：出土文献互证——马王堆医书房中类篇目与房中八家的时代/内容互证
8. `07-modern-interpretations.md`：现代解读与阅读路径——李零等研究、房中书性质诸说、推荐研读顺序与版本选择

#### Scenario: 按著录检索单家信息
- **WHEN** 读者想了解某一家的著录与存佚
- **THEN** 在 01-eight-schools-catalog.md 总表中能查到书名/卷数/班固注/存佚，并可跳转到对应分篇概念文档
- **AND** 事实性陈述均可在 facts.md 找到对应编号、在信源文档找到出处

### Requirement: 事实登记与待核验标注

facts.md SHALL 完整登记 R 阶段全部事实，按四条线分组制表（编号/事实内容/信源），SHALL 对调研中发现的争议条目显式保留【待核验】标注或选用已核实表述，至少包括：

- 八家卷数与总卷数（以《汉志》原文为准，不得沿用网络讹传数字）
- 房中类小序文本（以权威点校本为准）
- 各家亡佚时代（仅区间性判断，无确证者标注）
- 佚文归属（《医心方》所引篇题与八家的对应关系，存疑者标注）
- 马王堆医书各篇定名与释读状况

#### Scenario: 读者核验一条争议信息
- **WHEN** 读者看到卷数或年代表述
- **THEN** 该处要么采用已核实的单一表述并附信源，要么明确给出争议标注并指向 facts.md 对应条目

### Requirement: 原文引用遵守学术引介尺度

所有引用 SHALL 遵守学术引介尺度：

- 公版古典文献（《汉志》著录原文、房中类小序、马王堆医书释文、《医心方》佚文等）：引篇名、核心命题、少量代表性片段，以学术介绍口吻呈现
- 涉及性内容的佚文：以学术转述为主，确需引用时取目录学/医学史角度的代表性短句，不做露骨展开
- 全部内容为教育性、学术性表述

#### Scenario: 内容得体性检查
- **WHEN** V 阶段评审者通读全部产出文档
- **THEN** 不发现超出学术引介尺度的原文摘录或露骨描写
- **AND** 涉及具体文本的引用均可对应到公版文献或仅有提要说明

### Requirement: 索引与计数一致性

sexology/index.md 与 bundles/index.md 的更新 SHALL 保持计数、表格行、toctree 三者一致：

- bundles/index.md frontmatter：`total_bundles: 290`、`groups: 36`（domains 保持 13）
- think 域表格行改为"9 束 · 6 组"，sexology 分组行束数 1→2 并更新说明
- sexology/index.md 导航表加行、toctree 加 `fangzhong-bajia-reading/index`
- 新增 bundle 计入 total_bundles

#### Scenario: toctree 质量门通过
- **WHEN** 在 `projects/awesome-okf-xs` 目录运行 `invoke gates.toctrees`
- **THEN** 零断链、零孤立文档
- **AND** `invoke gates.utf8` 通过；`invoke build` Sphinx 构建成功（允许其他既有 bundle 的孤立警告，但本 bundle 不得新增警告）

### Requirement: V 阶段独立对抗评审

实施完成后 SHALL 委托新鲜上下文的独立评审（general_purpose_task 只读），按四视角审查：

1. **事实准确性**：抽查著录信息与《汉志》原文一致性、事实条目与信源对应、待核验标注是否保留
2. **新人可入门性**：零基础读者能否通过 index.md 与 00 篇进入并按 examples 路径完成首次研读
3. **定位与边界**：是否为"阅读教程为主+著作提要"而非论文/百科；是否越界到露骨内容；与 classics-reading 通论是否重复冗余
4. **时效与规范**：frontmatter 合法性、stale_after 设置、索引计数一致

评审结果 SHALL 记录于本 spec 目录 `review.md`；fail 项 materialize 为 tasks.md 中的 pending 修复任务。

## MODIFIED Requirements

（无——本 spec 为纯新增，不修改任何既有 Requirement）

## REMOVED Requirements

（无）

## 非目标（Out of Scope）

- 不生成任何 git commit（除非用户明确要求）
- 不修改 vendor 区文件
- 不收录露骨原文、不做色情内容介绍
- 不做八家佚文的穷尽式辑佚汇编（仅做辑佚链条与代表性样本的教学性介绍）
- 不解决【待核验】清单（保留标注，留待后续有权威馆藏信源时更新）
- 不修改 sexology/classics-reading 既有事实与结论（仅加交叉引用）
