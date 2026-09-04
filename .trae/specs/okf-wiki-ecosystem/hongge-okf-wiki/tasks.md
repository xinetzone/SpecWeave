---
title: 红歌教学知识包 OKF wiki - 实施计划
session: sc-20260902-hongge-okf-wiki
created: 2026-09-02
---

# 红歌教学知识包 OKF wiki - The Implementation Plan (Decomposed and Prioritized Task List)

> 执行纪律：每任务由独立子代理执行（工作目录 `d:\spaces\SpecWeave\projects\awesome-okf-xs`）；一次只推进一个任务；任务完成后按 Test Requirements 验证，通过再标记 [x]；文件命名/frontmatter/结构严格对齐先例束 `doc/bundles/yishu/vocal/meitong-yanyin-pedagogy/`；所有事实零推测、信源 URL 内嵌；禁止 git commit/push。

## [x] Task 1: R 阶段 — 双路信源调研与 facts.md 事实清单（68 条事实 / P0 表 33 行 / 编号已统一 F-001 三位制）
- **Priority**: high
- **Depends On**: None
- **Description**：
  - 用 WebSearch/WebFetch 做双路调研（通用网 + 权威信源），采集并撰写 `doc/bundles/yishu/hongge/hongge-pedagogy/facts.md`（目录需创建）。
  - 事实分六轨，≥60 条：①红歌概念与分期史（概念源流、革命/建设/改革/新时代四时段）②代表曲目创作档案 ≥12 首（词曲作者、年份、出处影片/剧目、首演、流传：义勇军进行曲、黄河大合唱选曲、没有共产党就没有新中国、歌唱祖国、我的祖国、唱支山歌给党听、我和我的祖国、走进新时代、不忘初心、灯火里的中国等）③课标教材（义务教育艺术课程标准 2022 年版中音乐/革命文化相关条目、人音版/人教版中小学音乐教材收录红歌情况）④柯尔文手势/柯达伊教学法（John Curwen、Zoltán Kodály、手势七音 do-re-mi-fa-sol-la-ti 空间位置、首调唱名、中文教学界用法）⑤简谱/五线谱与群众歌曲曲式（进行曲/分节歌/颂歌特征、节拍调式）⑥著作权法（保护期：作者终生+死后 50 年、公版判定、教材法定许可边界）。
  - 每条格式对齐先例 facts.md：F-001 起连续编号，含陈述、信源 URL、信源层级（一级=政府/党媒/出版社/学术；二级=百科/媒体）、单源/存疑标注；禁止因果推断词。
  - 文末附 P0 关键事实双源核验表（≥15 条：曲目档案、课标、法条、柯尔文史实）。
  - frontmatter 对齐先例 facts.md（type: facts，标题、tags 等）。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: facts.md 存在、UTF-8 无 BOM、YAML frontmatter 可解析含 type；事实条目 ≥60 条且编号连续
  - `programmatic` TR-1.2: 每条事实含至少 1 个 http(s) URL；抽查 10 条 URL 可访问（WebFetch 返回 200 或有效内容）
  - `programmatic` TR-1.3: P0 核验表 ≥15 行，四类关键事实均有覆盖
  - `human-judgement` TR-1.4: 曲目词曲作者/年份与权威信源一致；无政治史实差错；无聊天原文与个人姓名
- **Notes**: 禁止臆造；查不到的事实宁可不写或标注"待核"；课标条目引用须给出官方 PDF/出版社页面。

## [x] Task 2: Seedream 配图生成（hongge-group-hero.jpg 16:9 + hongge-pedagogy-cover.jpg 4:3，均已落位 _static）
- **Priority**: medium
- **Depends On**: None（可与 Task 1 并行，但按序执行）
- **Description**：
  - 用 GenerateImage（Seedream）生成 2 张图：①分组封面 `hongge-group-hero.jpg`：暖色纸感插画风格，校园合唱场景（学生歌唱、飘带、歌谱元素），温暖正能量、无文字、无真实人物肖像；②知识包封面 `hongge-pedagogy-cover.jpg`：与分组封面同风格，元素含打开的歌谱本、上升的音阶手势意象、红旗色点缀。
  - 落位目录 `doc/_static/bundles/yishu/hongge/images/`（自行创建）。
  - 审美参照先例：`doc/_static/bundles/jishu/gui/images/` 装饰封面定位（顶部装饰图，非内容图）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 两张图片文件存在于指定 _static 目录且可被 Read 读取
  - `human-judgement` TR-2.2: 图像无文字乱码、无真实政治人物肖像、风格温暖不庸俗

## [x] Task 3: F+I 阶段 — insights.md 架构洞察（7 条四元组洞察，全部回指 F 编号）
- **Priority**: high
- **Depends On**: Task 1
- **Description**：
  - 基于 facts.md 用第一性原理推导教学闭环（赏—谱—声—教），撰写 `doc/bundles/yishu/hongge/hongge-pedagogy/insights.md`。
  - ≥5 条四元组洞察（现象/根因/影响/建议，回指 F 编号），覆盖：①教学闭环完整性是备课核心 ②曲谱库瓶颈在版权合规而非资源获取 ③柯尔文手势是音高内化脚手架（与 vocal 束"八步骤=音条体系脚手架"洞察互参）④群众歌曲曲式简单性是教学资产 ⑤赏析教学≠讲故事（需可操作框架）⑥红歌时代分层避免标签化（可选第六条）。
  - frontmatter 对齐先例 insights.md。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: insights.md 存在、frontmatter 可解析；洞察条目 ≥5，每条含四要素且回指至少 1 个 F 编号
  - `human-judgement` TR-3.2: 洞察非常识复述，对教学行动有直接指导意义

## [x] Task 4: A 阶段（上）— concepts/ 概念文档 10 篇 + index（11 文件，F 引用零悬空，跨束链接已修复三级路径）
- **Priority**: high
- **Depends On**: Task 1, Task 3
- **Description**：
  - 创建 `concepts/` 目录及 `index.md` 与 10 篇概念文档（文件名 kebab-case，编号 00-09）：
    - 00 入门地图：知识包是什么、三类读者画像（新手教师/有经验教师/合唱指导）、使用路径、与 vocal 束关系
    - 01 红歌的界定与四个时代分期（革命/建设/改革/新时代），概念源流
    - 02 曲谱基础：简谱与五线谱对照、调式节拍、群众歌曲三大曲式（进行曲/分节歌/颂歌）
    - 03 教学型赏析六步框架：背景→曲式→旋律→歌词→演唱处理→教学要点
    - 04 革命时期代表曲目赏析示范（义勇军进行曲、没有共产党就没有新中国、黄河大合唱选曲）
    - 05 建设与改革时期曲目赏析示范（歌唱祖国、我的祖国、唱支山歌给党听、我和我的祖国、走进新时代）
    - 06 新时代主旋律曲目赏析示范（不忘初心、共筑中国梦、灯火里的中国）
    - 07 柯尔文手势与柯达伊教学法：七音手势表（音名/唱名/手型/空间位置）、课堂操练步骤、常见错误
    - 08 红歌演唱的声乐基础：呼吸、咬字、音色（民族唱法/群众歌唱）、合唱编排，交叉引用 `../../vocal/meitong-yanyin-pedagogy/concepts/` 相关篇
    - 09 曲谱库建设与版权合规 + 课堂教案设计法（曲谱来源决策树、保护期规则、教案模板）
  - 每篇含：学习目标（学完能做什么）、正文、小结、回指 facts F 编号；00 篇含概念地图 mermaid（对齐先例 00 篇构图：读者路径分流）。
  - concepts/index.md 为概念篇目录页（对齐先例格式）。
  - 曲目赏析仅引用片段级谱例（公版）或文字描述旋律特征，不转录保护期内完整词曲。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 11 个文件（00-09 + index）均存在、frontmatter 可解析含 type、无 UTF-8 BOM
  - `programmatic` TR-4.2: 交叉引用 vocal 束的相对路径链接全部可解析存在；无 file:/// 链接
  - `human-judgement` TR-4.3: 七音手势表与柯达伊权威资料一致（教研员视角）；赏析六步在 04-06 篇被实际示范而非空转；无侵权转录
- **Notes**: 先读 `yishu/vocal/meitong-yanyin-pedagogy/concepts/` 全部文件作为写作模板与交叉引用锚点。

## [x] Task 5: A 阶段（中）— examples/ 实践示例 3 篇 + index（4 文件，教案 45 分钟闭环，零歌词转录，断链 0）
- **Priority**: high
- **Depends On**: Task 4
- **Description**：
  - 创建 `examples/` 及：
    - 01《歌唱祖国》单曲目完整教案：45 分钟流程表（手势练声 5min→背景与赏析 12min→视唱曲谱 15min→演唱处理 8min→作业 5min），含教师话术要点、学生活动、谱例仅用公版片段或正版指引
    - 02 曲谱库搭建指南：可复制目录树（按时代/年级/曲式）、资源信源清单表（平台/授权类型/用途）、版权自查清单（保护期计算、教材使用边界）
    - 03 学期 16 周教学路线图：周次表（手势音阶 1-3 周→曲目递进 4-14 周→合唱汇报 15-16 周），每周配概念篇回指
    - index.md 目录页
  - 全部可直接打印备课；表格用 Markdown/MyST 表格。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 4 个文件存在、frontmatter 合规、无断链
  - `human-judgement` TR-5.2: 教案时间合计 45 分钟且环节闭环；路线图每周可执行；版权自查清单覆盖保护期/许可/来源记录三栏

## [x] Task 6: A 阶段（下）— references/ 信源参考 3 篇 + index（4 文件，64 条信源，零盗版站点，11 条 URL 实测可访问）
- **Priority**: high
- **Depends On**: Task 1
- **Description**：
  - 创建 `references/` 及：
    - 01 课标与教材信源：义务教育艺术课程标准（2022）官方来源、人音版/人教版音乐教材与教师用书、高中课标；每条含名称、出版方、获取方式、用途
    - 02 曲谱与音频正版信源：人民音乐出版社、正版曲谱平台、图书馆馆藏、公版曲谱库（IMSLP 等及其中文作品适用边界）、音频平台；标注授权类型
    - 03 红歌史料与教学法信源：聂耳/冼星海纪念馆或权威传记、中国音乐家协会资料、柯达伊教学法中文专著、柯尔文手势权威文献
    - index.md 信源导航页（对齐先例 references/index.md 三层结构）
  - 每条信源含 URL、层级标注、"如何验证"提示。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 4 个文件存在、frontmatter 合规；每条信源含可访问 URL（抽查 8 条）
  - `human-judgement` TR-6.2: 无盗版曲谱站点；公版边界表述与著作权法一致

## [x] Task 7: 束根 index.md + 分组 hongge/index.md（含封面图；分组页已补 okf_version 对齐仓库惯例）
- **Priority**: high
- **Depends On**: Task 2, Task 4, Task 5, Task 6
- **Description**：
  - 创建束根 `hongge-pedagogy/index.md`：frontmatter `type: OKF`、`okf_version: "0.2"`、generated/verified 字段对齐先例；正文含一句话定位、快速导航表（concepts/examples/references/facts/insights）、读者路径 mermaid（新手/教师/合唱指导三流）、toctree 覆盖 concepts/index、examples/index、references/index、facts、insights。
  - 创建分组 `hongge/index.md`：frontmatter `type: group`；顶部 MyST 引用 hero 图 `/_static/bundles/yishu/hongge/images/hongge-group-hero.jpg`；分组说明、束导航表、知识地图 mermaid、toctree 含 `hongge-pedagogy/index`。
  - 束根正文引用封面图 `hongge-pedagogy-cover.jpg`。
  - frontmatter 双引号内禁止 ASCII 双引号；不创建 log.md（先例束无此文件）。
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 两个 index.md 存在、frontmatter 可解析；okf_version 仅出现在束根；toctree 引用文件全部存在（"待补"规则：只链接已创建文件）
  - `programmatic` TR-7.2: 图片引用路径 `/_static/...` 与实际文件一致

## [x] Task 8: V 阶段 — 四视角对抗审查与修正（13 条意见，6 处落盘修正含 2 处 high：F-037 失配链、法条误引；结论可入门控）
- **Priority**: high
- **Depends On**: Task 7
- **Description**：
  - 以四个独立视角审查全束并输出审查记录（写入束根目录下审查结论段落或直接修正后报告）：
    - 魔鬼代言人：史实/政治差错、版权风险、手势描述错误、课标引用失实
    - 新人视角：零音乐基础能否照教案上课？术语是否都有解释？
    - 老板视角（教研组长）：拿去公开课/检查是否合规、对齐课标
    - 未来视角：教材改版/课标更新/曲目新增时如何维护
  - ≥5 条具体问题，≥2 条修正落盘；修正后回归相关 TR。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-8
- **Test Requirements**:
  - `human-judgement` TR-8.1: 审查意见清单 ≥5 条且每条有文件/段落定位
  - `programmatic` TR-8.2: 采纳的修正已落盘（文件 mtime 更新、内容可见）且未引入断链（toctrees 复跑）

## [x] Task 9: 共享索引注册 + 三门门控 + 定向 sphinx 构建（utf8/toctrees/bundles 三门全绿；sphinx dummy 退出码 0、hongge 相关警告 0；主控独立复跑门控确认）
- **Priority**: high
- **Depends On**: Task 8
- **Description**：
  - 更新 `doc/bundles/yishu/index.md`：分组导航表新增 hongge 行、toctree 增 `hongge/index`、域描述与计数以门控重算为准。
  - 更新 `doc/bundles/index.md`：frontmatter（total_bundles/groups/domains）、yishu 域节标题计数、分组表新增行、生态概览 mermaid yishu 行、计数语句；**所有计数先跑门控取真值再写**，禁止手填。
  - 在子项目根目录、py314 环境依次执行：`invoke gates.utf8` → `invoke gates.toctrees` → `invoke gates.bundles`（用 `conda run --no-capture-output -n py314 ...`）；失败按报错修复至全绿。
  - 定向构建：`python -m sphinx -b dummy -E doc .temp/dummy doc/bundles/yishu/hongge/index.md doc/bundles/yishu/hongge/hongge-pedagogy/index.md`（如平台支持显式文件列表；否则全量 dummy 构建），要求 0 error。
  - 复跑确保无 regression。
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: 三门门控全部 PASS（输出含 0 error / 计数一致）
  - `programmatic` TR-9.2: sphinx dummy 构建退出码 0，无与新增文件相关的 warning/error
  - `programmatic` TR-9.3: 共享索引五面对账一致（frontmatter 计数 == 域节计数 == 分组表行数 == toctree）
- **Notes**: 若并行会话导致基线漂移，以门控真值为准对账；禁止 commit。
