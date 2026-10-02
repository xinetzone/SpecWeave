---
title: tasks — real-needs-discovery-okf-wiki
status: "completed"
version: "1.0"
methodology: "seven-concepts（场景4 知识沉淀：R→I→E，叠加 F 本质剖析 + V 对抗审查）"
content-sensitivity: "public"
---

# Tasks — 真需求发现 OKF Wiki 知识包

> 关联规范：[spec.md](spec.md)。Status 取值：pending / in_progress / blocked / completed / cancelled。
> 检查点写入各任务的 Test Requirements（磁盘规范禁止独立 checklist.md）。

## Task 1 — R 阶段：西方经典谱系调研与事实登记

- **Status**: completed
- **Priority**: high
- **Depends On**: 无
- **Description**: 基于一级信源（经典著作与提出者原文）登记西方谱系事实：Customer Development（Blank）、精益创业（Ries）、JTBD（Christensen/Ulwick）、Mom Test（Fitzpatrick）、Kano（Noriaki Kano 1984）、设计思维/民族志/情境访谈（Brown/Beyer & Holtzblatt/Dave Gray）、Pretotyping（Savoia）、领先用户（von Hippel）、Working Backwards（Bryar & Carr）、RICE（Intercom）、正反案例（Dropbox/Airbnb/Zappos/Buffer vs Google Glass/Juicero/Quibi/Segway）。登记格式：编号 + 声明（无因果词）+ 信源 + 信源类型 + 可信度（P0/P1/P2）。
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**（rule 型）:
  - 每条事实含信源与 P0/P1/P2 可信度标注；P0 条目（提出者/年份/关键数字）必须给出可复核的著作或官方链接。
  - 著名误传（福特"更快的马"等）必须登记为"误传"而非事实，供 references/02 勘误。
  - 调研笔记落盘于本 spec 目录（research-notes.md），F 编号事实唯一真源为 bundle facts.md（避免双份不一致）。

## Task 2 — R 阶段：中文谱系调研与事实登记

- **Status**: completed
- **Priority**: high
- **Depends On**: 无
- **Description**: 登记中文谱系事实：梁宁《真需求》（价值-共识-模式三角，只提炼框架不逐字转录）、《产品思维30讲》（痛点/爽点/痒点）、俞军《俞军产品方法论》（用户价值公式、用户是需求的集合）、张小龙产品观、黄峥与拼多多案例、王兴/周鸿祎等公开方法论表述、小米参与感；国内伪需求大讨论（O2O 死亡潮、共享单车泡沫、脸萌等速朽产品）正反案例。
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**（rule 型）:
  - 版权书（梁宁《真需求》《俞军产品方法论》）只做框架提炼与页级转述，禁止逐字转录段落。
  - 公开语录（黄峥/张小龙/周鸿祎）须标注传播出处与可信度，无原始出处的一律标 P1 以下并在 references/02 声明。

## Task 3 — I 阶段：facts.md 成文 + insights.md 四元组提炼

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**: 将双谱系调研合并去重为 bundle 的 facts.md（S 编号信源 + F 编号事实表，分区登记）；提炼 ≥6 条四元组洞察（陈述/证据/反常识点/行动启示），每条洞察引用 F 编号溯源，通过质量门 G2（四元组完整、有反常识点）。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**（rule 型）:
  - facts.md 事实声明无因果词（"导致/因此/所以"仅允许出现在信源原文转述中）。
  - insights.md ≥6 条，每条四元组四格齐全且证据格含 F 编号。

## Task 4 — E 阶段：bundle 骨架落盘

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 创建 `doc/bundles/sheke/marketing/real-needs-discovery/` 目录结构：concepts/、examples/、references/ 三个子目录及各自 index.md，bundle 根 index.md 与 log.md 占位。frontmatter 遵循 OKF v0.2（唯一必填 type；根 index 含 okf_version: "0.2"）。
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**（rule 型）:
  - 目录名与文件名全部 kebab-case；保留文件名仅 index.md / log.md。
  - 每个 index.md 的 toctree 收录其直接子文档。

## Task 5 — E 阶段：concepts 00-03 撰写

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 撰写概念层前四篇：00-what-is-real-need（需要/欲望/需求三分、痛点/爽点/痒点、真伪判别标准）；01-fake-need-taxonomy（伪需求图谱：供给方投射/补贴伪高频/技术自恋/痒点错觉 + 认知陷阱）；02-discovery-method-map（问/看/算/试四路径全景与选择决策）；03-interview-playbook（Mom Test 规则、JTBD switch 访谈、追问技术与禁用问题）。
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**（rule 型）:
  - 每篇正文引用 F 编号溯源事实；中文正文；Mermaid 图遵循安全编码规则。

## Task 6 — E 阶段：concepts 04-07 撰写

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 撰写概念层后四篇：04-jtbd-framework（雇用产品隐喻、四力模型、ODI 成果驱动）；05-validation-loop（build-measure-learn、MVP 谱系：假门/绿野仙踪/礼宾/单功能、pretotyping）；06-need-prioritization（Kano 五类与退化、RICE、ODI 机会算法）；07-cases-and-boundaries（正反案例核验版、方法论适用边界、AI 时代需求发现）。
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**（rule 型）:
  - 案例数字一律采用核验口径（如 Juicero 融资 $120M、Quibi $1.75B/约半年关停），无核验把握的标 P0 并落入 references/02 待核清单。
  - ≥4 个正反案例且每案含"教训-方法论映射"。

## Task 7 — E 阶段：examples 4 篇撰写

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Description**: 撰写实操层：01-interview-script-workshop（可直接复用的访谈脚本与禁用问题清单）；02-jtbd-switch-interview（完整 switch 访谈示范记录与四力分析）；03-one-week-validation-plan（一周验证计划模板，含判定线）；04-need-self-check-list（需求自检清单 ≥20 项）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**（rule 型）:
  - 每篇可脱离上下文直接执行（含输入、步骤、产出物、判定标准）。
  - 与 concepts 交叉引用使用相对路径，禁止 file:///。

## Task 8 — E 阶段：references 2 篇撰写

- **Status**: completed
- **Priority**: medium
- **Depends On**: Task 3
- **Description**: 撰写信源层：01-classics-and-authorities（S 编号信源登记：经典原著/官方站点/考证文章，标注信源类型与距离）；02-source-verification（P0 核验结论表、误传勘误清单、未联网核验声明与方法边界）。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**（rule 型）:
  - 每个 S 编号信源含 URL 或出版物信息；误传条目给出去伪结论与考证信源。
  - 如实声明本次调研的核验方式与局限（哪些条目未经联网核验）。

## Task 9 — 三级索引更新与五面对账

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7, Task 8
- **Description**: 更新三级索引：marketing/index.md（新增束导航 + total_bundles 2→3）、sheke/index.md（marketing 行 2→3）、bundles/index.md（total_bundles 575→576、mermaid sheke 46→47、社科域节 46→47、marketing 行 2→3，组数 59 与域数 9 不变）。
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**（rule 型）:
  - 五面计数自洽：frontmatter 总数 / 正文计数 / mermaid 图 / 域节标题 / 组行计数一致；sheke 各组束数之和 = 47。
  - marketing/index.md toctree 追加本束。

## Task 10 — 质量门验证 + V 对抗审查与修订

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 在 awesome-okf-xs 子项目内运行 `invoke gates.toctrees`、`invoke gates.bundles`、`invoke build`（或按 Skill §7 执行清单化手动等效验证并如实记录）；V 阶段四视角对抗审查（事实准确性/结构完整性/误导风险/版权合规），P0/P1 问题修订闭环。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**（rule 型）:
  - UTF-8 strict roundtrip 无异常；相对链接全可达；三级 toctree 完整；file:/// 零出现；家目录绝对路径零出现。
  - V 审查发现分级记录于 log.md，P0/P1 必须修复后方可标 completed。

## 变更记录

- 2026-10-01：初始版本（10 任务，R 双路并行 → I → E → 索引 → 门禁+V）。
- 2026-10-01：全部 10 任务完成。说明：Task 9 原口径 576 束/59 组/sheke 47 束，gate 实测目录树地面真值为 577 束/60 组/sheke 48 束——并行会话在途束 sheke/minsu/hangzhou-qiuyinyuan-guide 已在树中存在但未登记，按"以树为准"原则一并登记对齐（未改动 minsu 自身文件，提交决策留用户）。Task 10 V 审查修复根 index.md F 编号张冠李戴一处（梁宁 F-005→F-007、俞军 F-004→F-005），三门脚本实测全绿，详见 bundle log.md。
