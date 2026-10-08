---
title: 杭州求姻缘地点调研知识包 OKF wiki - 实施计划
session: sc-20261001-hangzhou-qiuyinyuan-okf-wiki
created: 2026-10-01
---

# 杭州求姻缘地点调研知识包 OKF wiki - The Implementation Plan (Decomposed and Prioritized Task List)

> 执行纪律：每任务由独立子代理执行（工作目录 `d:\spaces\SpecWeave\projects\awesome-okf-xs`）；一次只推进一个任务；任务完成后按 Test Requirements 验证，通过再标记 [x]；文件命名/frontmatter/结构严格对齐先例束 `doc/bundles/yishu/hongge/hongge-pedagogy/`；所有事实零推测、信源 URL 内嵌、时效信息标注采集日期；禁止 git commit/push。

## [x] Task 1: R 阶段 — 双路信源调研与 facts.md 事实清单
- **Priority**: high
- **Depends On**: None
- **Description**：
  - 用 WebSearch/WebFetch 做双路调研（通用网 + 官方/权威信源），采集并撰写 `doc/bundles/sheke/minsu/hangzhou-qiuyinyuan-guide/facts.md`（目录需创建）。
  - 事实分七轨，≥60 条：①月老信仰与杭州姻缘民俗源流（月老出处、杭州相关记载）②法喜寺（历史、位置、门票/开放、姻缘相关祈福点位、法物流通）③灵隐寺景区（灵隐寺/永福寺/韬光寺；飞来峰门票+寺院香花券双票制、开放时间、预约方式）④其他寺院（净慈寺、香积寺等与姻缘祈愿相关点）⑤黄龙洞月老祠（景区属性、月老祠位置、门票、相亲文化）⑥万松书院相亲角（开放规律、周日相亲角现象、权威媒体报道）⑦实用信息（交通、官方预约购票渠道、寺院参拜礼仪规范）。
  - 每条格式对齐先例 facts.md：F-001 起连续编号，含陈述、信源 URL、信源层级（一级=官方/政府/寺院官网公众号/权威媒体；二级=百科/自媒体仅作线索）、单源/存疑标注；禁止因果推断词；时效性事实标注采集日期（2026-10）。
  - 文末附 P0 关键事实双源核验表（≥15 条：各点位门票/开放时间/地址三类实用事实为主）。
  - frontmatter 对齐先例 facts.md（type: facts，标题、tags 等）。
  - 调研中若发现清单外公认求姻缘点位，补充进对应轨道并在本任务备注登记。
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-1.1: facts.md 存在、UTF-8 无 BOM、YAML frontmatter 可解析含 type；事实条目 ≥60 条且编号连续
  - `programmatic` TR-1.2: 每条事实含至少 1 个 http(s) URL；抽查 10 条 URL 可访问（WebFetch 返回 200 或有效内容）
  - `programmatic` TR-1.3: P0 核验表 ≥15 行，门票/开放时间/地址三类关键事实均有覆盖
  - `human-judgement` TR-1.4: 门票/开放时间等与官方信源一致；无"灵验""最灵"等主观断言作事实陈述；无个人隐私信息
- **Notes**: 禁止臆造；查不到的事实宁可不写或标注"待核"；门票/开放时间必须以官方渠道为一级信源，营销号内容仅作线索。

## [x] Task 2: Seedream 配图生成（minsu-group-hero 1 张 + bundle 封面 1 张，落位 _static）
- **Priority**: medium
- **Depends On**: None（可与 Task 1 并行，但按序执行）
- **Description**：
  - 用 GenerateImage（Seedream）生成 2 张图：①分组封面 `minsu-group-hero.jpg`：江南水乡禅意插画风格，杭州意象（西湖/古刹/香火/红线元素），温暖含蓄、无文字、无真实人物肖像；②知识包封面 `hangzhou-qiuyinyuan-guide-cover.jpg`：同风格，元素含古寺院落、月老红线、银杏/桂花等杭州季节意象。
  - 落位目录 `doc/_static/bundles/sheke/minsu/images/`（自行创建）。
  - 审美参照先例：`doc/_static/bundles/jishu/gui/images/`、`doc/_static/bundles/yishu/hongge/images/` 装饰封面定位（顶部装饰图，非内容图）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 两张图片文件存在于指定 _static 目录且可被 Read 读取
  - `human-judgement` TR-2.2: 图像无文字乱码、无真实人物肖像、风格含蓄不庸俗、不渲染迷信

## [x] Task 3: I 阶段 — insights.md 架构洞察（≥5 条四元组洞察，全部回指 F 编号）
- **Priority**: high
- **Depends On**: Task 1
- **Description**：
  - 基于 facts.md 提炼并撰写 `doc/bundles/sheke/minsu/hangzhou-qiuyinyuan-guide/insights.md`。
  - ≥5 条四元组洞察（现象/根因/影响/建议，回指 F 编号），覆盖：①网络姻缘攻略信息矛盾根源在信源层级混杂（营销号抄过期信息）②寺院线热度差异与交通可达性/社交传播的关系 ③民俗点（相亲角=社交集市逻辑）与寺院（信仰参拜逻辑）是两类体验 ④门票/预约信息时效性是攻略最大维护成本 → 官方入口前置 ⑤"灵验叙事"传播机制与理性呈现的平衡。
  - frontmatter 对齐先例 insights.md。
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: insights.md 存在、frontmatter 可解析；洞察条目 ≥5，每条含四要素且回指至少 1 个 F 编号
  - `human-judgement` TR-3.2: 洞察非常识复述，对读者行程决策或内容维护有直接指导意义

## [x] Task 4: A 阶段（上）— concepts/ 概念文档 8 篇 + index（9 文件）
- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**：
  - 创建 `concepts/` 目录及 `index.md` 与 8 篇概念文档（文件名 kebab-case，编号 00-07）：
    - 00 入门地图：知识包定位、三类读者画像（专程求姻缘者/顺路游客/民俗兴趣者）、使用路径、信息复核原则
    - 01 月老信仰与杭州姻缘民俗源流：月老出处、杭州相关民俗记载与当代现象
    - 02 法喜寺参拜指南：历史简介、位置交通、门票开放、姻缘相关祈福点位与参拜要点
    - 03 灵隐寺景区参拜指南：灵隐寺/永福寺/韬光寺三点、双票制、预约方式、姻缘相关点位
    - 04 其他相关寺院：净慈寺、香积寺等（历史、开放信息、参拜要点）
    - 05 黄龙洞月老祠：景区属性、月老祠位置与民俗、门票开放
    - 06 万松书院相亲角：书院背景、相亲角现象（时间规律、参与方式客观描述）、隐私提示
    - 07 参拜礼仪与理性看待：寺院参拜通用礼仪、求姻缘的民俗文化定位、理性心态提示
  - 每篇含：学习目标（学完能做什么）、正文、小结、回指 facts F 编号；00 篇含概念地图 mermaid（读者路径分流）。
  - concepts/index.md 为概念篇目录页（对齐先例格式）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 9 个文件（00-07 + index）均存在、frontmatter 可解析含 type、无 UTF-8 BOM；相对路径链接全部可解析存在；无 file:/// 链接
  - `human-judgement` TR-4.2: 各点位门票/开放时间/地址与 facts.md P0 表一致；无灵验度承诺表述；相亲角篇无可识别个人信息
- **Notes**: 先读 `yishu/hongge/hongge-pedagogy/concepts/` 作为写作模板。

## [x] Task 5: A 阶段（中）— examples/ 实践示例 3 篇 + index（4 文件）
- **Priority**: high
- **Depends On**: Task 4
- **Description**：
  - 创建 `examples/` 及：
    - 01 寺院一日参拜路线：法喜寺+灵隐寺景区时间轴（含各段交通衔接、门票费用小计、用餐建议、体力分配）
    - 02 民俗点半日路线：黄龙洞+万松书院（含周日相亲角时间窗口说明、周边串联建议）
    - 03 参拜准备清单与避坑指南：行前检查表（预约/证件/着装/香火规则）、礼仪自查表、信息复核清单（官方入口汇总）
    - index.md 目录页
  - 全部可直接照做；费用/时间数据回指 facts F 编号并标注"以官方最新公告为准"；表格用 Markdown/MyST 表格。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 4 个文件存在、frontmatter 合规、无断链
  - `human-judgement` TR-5.2: 一日路线时间轴闭环可执行；费用小计与 facts.md 一致；避坑指南含官方复核入口

## [x] Task 6: A 阶段（下）— references/ 信源参考 3 篇 + index（4 文件）
- **Priority**: high
- **Depends On**: Task 1
- **Description**：
  - 创建 `references/` 及：
    - 01 寺院官方信源：各寺院官网/公众号/官方购票预约渠道（每条含名称、运营方、获取方式、用途）
    - 02 民俗与史料信源：月老信仰文献与权威研究、方志/景区志、权威媒体对相亲角的报道
    - 03 交通与实用信息信源：杭州文旅官方入口、公共交通查询、景区公告与客流提示渠道
    - index.md 信源导航页（对齐先例 references/index.md 三层结构）
  - 每条信源含 URL、层级标注、"如何验证"提示。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 4 个文件存在、frontmatter 合规；每条信源含可访问 URL（抽查 8 条）
  - `human-judgement` TR-6.2: 无营销号/付费占卜导流站点；官方渠道标注准确

## [x] Task 7: 束根 index.md + 分组 minsu/index.md（含封面图）
- **Priority**: high
- **Depends On**: Task 2, Task 4, Task 5, Task 6
- **Description**：
  - 创建束根 `hangzhou-qiuyinyuan-guide/index.md`：frontmatter `type: OKF`、`okf_version: "0.2"`、generated/verified 字段对齐先例；正文含一句话定位、快速导航表（concepts/examples/references/facts/insights）、读者路径 mermaid（专程/顺路/民俗兴趣三流）、toctree 覆盖 concepts/index、examples/index、references/index、facts、insights。
  - 创建分组 `minsu/index.md`：frontmatter `type: group`；顶部 MyST 引用 hero 图 `/_static/bundles/sheke/minsu/images/minsu-group-hero.jpg`；分组说明、束导航表、知识地图 mermaid、toctree 含 `hangzhou-qiuyinyuan-guide/index`。
  - 束根正文引用封面图 `hangzhou-qiuyinyuan-guide-cover.jpg`。
  - frontmatter 双引号内禁止 ASCII 双引号；不创建 log.md（先例束无此文件）。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 两个 index.md 存在、frontmatter 可解析；okf_version 仅出现在束根；toctree 引用文件全部存在
  - `programmatic` TR-7.2: 图片引用路径 `/_static/...` 与实际文件一致

## [x] Task 8: V 阶段 — 四视角对抗审查与修正（≥5 条意见，≥2 条采纳落盘）
- **Priority**: high
- **Depends On**: Task 7
- **Description**：
  - 以四个独立视角审查全束并输出审查记录（写入束根目录下审查结论段落或直接修正后报告）：
    - 魔鬼代言人：门票/开放时间/地址是否有错漏或过期；"灵验"表述是否越界；隐私红线；法物流通/香火表述是否准确
    - 新人视角：首次赴杭、零佛教常识者能否照 examples 走完全程？术语是否都有解释？
    - 老板视角（内容编辑）：信源层级是否经得起审核？时效标注是否完整？营销号内容是否混入一级信源？
    - 未来视角：门票政策调整/点位热度变化时如何低成本维护？
  - ≥5 条具体问题，≥2 条修正落盘；修正后回归相关 TR。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-7
- **Test Requirements**:
  - `human-judgement` TR-8.1: 审查意见清单 ≥5 条且每条有文件/段落定位
  - `programmatic` TR-8.2: 采纳的修正已落盘（文件 mtime 更新、内容可见）且未引入断链（toctrees 复跑）

## [x] Task 9: 共享索引注册 + 三门门控 + 定向 sphinx 构建（C 阶段交付，不 commit）
- **Priority**: high
- **Depends On**: Task 8
- **Description**：
  - 更新 `doc/bundles/sheke/index.md`：分组导航表新增 minsu 行、toctree 增 `minsu/index`、域描述与计数以门控重算为准。
  - 更新 `doc/bundles/index.md`：frontmatter（total_bundles/groups/domains）、sheke 域节标题计数、分组表新增行、生态概览 mermaid sheke 行、计数语句；**所有计数先跑门控取真值再写**，禁止手填。
  - 在子项目根目录、py314 环境依次执行：`conda run --no-capture-output -n py314 invoke gates.utf8` → `invoke gates.toctrees` → `invoke gates.bundles`；失败按报错修复至全绿。
  - 定向构建：`python -m sphinx -b dummy -E doc .temp/dummy <新增文件列表>`，要求 0 error、无与新增文件相关警告。
  - 复跑确保无 regression；**不执行 git commit/push**，交付物为工作树文件 + 门控全绿。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: 三门门控全部 PASS（输出含 0 error / 计数一致）
  - `programmatic` TR-9.2: sphinx dummy 构建退出码 0，无与新增文件相关的 warning/error
  - `programmatic` TR-9.3: 共享索引五面对账一致（frontmatter 计数 == 域节计数 == 分组表行数 == toctree）
- **Notes**: 若并行会话导致基线漂移，以门控真值为准对账；禁止 commit。

# Task Dependencies

- Task 1 (R/facts.md) → Task 3 (I/insights.md)、Task 4 (concepts)、Task 6 (references)
- Task 3 → Task 4
- Task 4 → Task 5 (examples)
- Task 2 (配图) 与 Task 1 可并行
- Task 2, 4, 5, 6 → Task 7 (束根/分组 index)
- Task 7 → Task 8 (V 对抗审查)
- Task 8 → Task 9 (索引注册 + 门控交付)
