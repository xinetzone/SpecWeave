# 企业微信 5.0.10 版本新功能发布页转 OKF Wiki - 实施计划

> 链路：E（信源先行）→ 索引接入 → V（机械门禁）→ Review（独立评审）。事实集 F-001～F-033 已在 Specify 阶段完成于 `facts.md`。

## Task 1: 信源先行——references 层三件套

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/wecom-5-0-10-release/references/` 新建 `article-source.md`（来源代号表 + F-001～F-033 双份登记表 + 勘误四张清单落实）、`verification.md`（P0 核验表、口径并存表、V 四视角审查、状态裁决）、`index.md`（无 frontmatter，toctree 收两篇）。
  - 内容以 spec `facts.md` 为唯一事实源，双份编号集合必须相等。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: 正则 `F-\d{3}` 提取 article-source.md 编号集合 = facts.md 集合 = {F-001…F-033}，连续无跳号；证据：提取输出比对。
  - `rule` TR-1.2: references/index.md 含 toctree 块且条目 article-source、verification 对应文件存在；证据：Test-Path。
  - `rule` TR-1.3: 两篇 Reference frontmatter 含 type/title/generated/verified/status/stale_after/sources，sources 含 W 与 O1/O2/O3 等核验源；证据：逐字段核对。
- **Completion Evidence**:
  - 三文件已生成；机械脚本输出「facts.md 33 连续 True / article-source.md 33 连续 True / 双份相等 True」。
  - references/index.md toctree 两条目 Test-Path 全 True（零断链脚本输出）。
  - 两篇 frontmatter 七字段脚本核对 OK；sources 含 W/O1～O8。

## Task 2: 概念层——3 篇 concepts + 子目录索引

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `concepts/00-wecom-5-0-10-release-overview.md`：版本快照总览（发布时间锚点 2026-08-18、两大重点功能、门槛取消、版本时效 5.0.12、灰度提示）。
  - `concepts/01-ai-open-capability-cli-mcp.md`：CLI/MCP 双通道、模块能力矩阵（发布页 7 模块逐项 + 当前官方页 11 模块对照）、两条安装路径与命令大小写口径、安全四机制、兼容 Agent 清单、生态旁证。
  - `concepts/02-smart-sheet-dayuan-and-smart-doc.md`：大圆与智能表格 AI 分析报告（灰度中、四维交互、实时更新单源标注）、智能文档排版与导出增强。
  - `concepts/index.md`：无 frontmatter，toctree 收 3 篇（stem 排序）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 正文出现的每个版本号/模块名/命令/日期/包名类具体声明均可在 F-001～F-033 中找到出处（行内 F 标注）；证据：V 阶段逐条比对。
  - `rule` TR-2.2: 模块 7/10/11 口径、命令大小写三处差异、5.0.12 时效、灰度状态均显式分层呈现；证据：关键词核对清单。
  - `rubric` TR-2.3: 读者可用性；1-5；1=残缺失真，3=事实全但口径混杂，5=不回源即可理解全貌与边界；阈值 >=4；证据：独立评审评分。
- **Completion Evidence**:
  - 3 概念 + 子目录 index 已生成；独立评审抽查 16 项具体声明全部命中 F 并经官方两页 WebFetch 逐字复核。
  - 7/10/11、三态大小写、5.0.12、灰度、F-016 单源/F-026 转述均在正文专节/专表呈现（CP-R3/R4 pass）。
  - 读者可用性 CP-U1 独立评分 5/5。

## Task 3: 束根 index.md 与 log.md

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - `index.md`：`okf_version: "0.2"` + bundle frontmatter（title/description/tags/generated/verified/status: stable/stale_after: 2027-01-31/sources 多源）；顶部「非操作教程」声明与可信度状态块；「这束知识包讲什么」篇导航；「已知边界」五条（灰度中、5.0.10 时点快照与官方页演进、5.0.12 已接替、命令大小写口径、单源条目 F-016/媒体转述 F-026）；「主题关联」互链 tencent-meeting-cli、lightvela-personal-agent；toctree 收 concepts/index、references/index、log。
  - `log.md`：2026-10-14 初始生成记录（链路、敏感度、事实数、核验结论、文件数、归属、门禁方式与既有计数漂移观测）。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 根 index 为目录内唯一带 okf_version 的文件；toctree 三条目对应存在；证据：frontmatter 与 Test-Path 核对。
  - `rule` TR-3.2: 已知边界覆盖 FR-5 五项；sources 至少含 W/O1/O2/O3/O6；证据：清单项核对。
- **Completion Evidence**:
  - 机械扫描确认根 index 为唯一 okf_version 文件；toctree 3 条目对应存在；已知边界五条齐备；sources 9 条（W+O1～O8）。
  - log.md 含完整生成/核验/门禁/评审记录与既有漂移披露。

## Task 4: 分组/类目/域/总索引接入与计数同步

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 先以脚本机械计数：tencent 组实际 bundle 目录数、ecosystems 各类目目录数与束数、ai 域六类合计、jishu 域合计、全库 total。
  - 更新 `tencent/index.md`（导航表加行+简介、toctree 追加、正文「当前包含 N 个」与统计句同步）；`ecosystems/index.md`（腾讯行束数、类合计与目录数按实测校正）；`jishu/ai/index.md`（description/六大类表 ecosystems 行/正文合计）；`jishu/index.md`（ai 行与域合计，按实读内容更新）；`bundles/index.md`（total_bundles、正文 630 计数、jishu 域节计数）。
  - 仅同步本次新增影响面；库内与本束无关的既有漂移在 log.md 记录，不扩大修改。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-4.1: 各修改面数字 = 机械计数值，且彼此沿链路一致；证据：计数脚本前后输出对照。
  - `rule` TR-4.2: 四个上游 index 的 toctree/导航表均可到达 `tencent/wecom-5-0-10-release/index`；证据：链接与 toctree 条目核对。
- **Completion Evidence**:
  - 机械计数（与门禁同口径递归脚本）：tencent=12、ecosystems=88、ai=240（88/85/20/32/9/6）、jishu=469、total=632。
  - 五面更新后 `check-bundles-index.py` 通过：「9 域/61 组/632 束，五面一致」；tencent 导航表/toctree/统计句（93 概念/52 信源/1555 事实）一致；本束经 tencent toctree BFS 可达。

## Task 5: V 阶段机械门禁与四视角自审

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 执行手动等效门禁（若 `invoke gates.toctrees/utf8` 依赖可用则优先运行并留存输出）：UTF-8 strict 解码全部新增/修改文件；三级 toctree 条目 Test-Path；Grep 全部相对链接逐一可达；零 `file:///`/家目录；双份 F 编号集合比对；frontmatter 完整性。
  - 四视角自审（魔鬼代言人/新人/业务方/未来视角）修复项直接落实，结论写入 references/verification.md 与 log.md。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 门禁清单 8 项全部有 pass 证据（命令输出或逐条人工记录）；若 gates 不可用须在 log.md 注明，禁止声称 gates 通过；证据：log.md 记录。
  - `rule` TR-5.2: 自审发现的每个 actionable 项均已修复并记录；证据：verification.md 四视角表。
- **Completion Evidence**:
  - `check-utf8.py` 全库 11536 文件通过；`check-toctrees.py` 过滤本束零命中（全量 91 项为开工前既有/并发 WIP，与本束无关，已 log 披露）；`check-bundles-index.py` 通过；链接/F 集合/frontmatter/禁用路径脚本逐项 pass。
  - 四视角表写入 verification.md；未跑 invoke gates 已在 log.md 注明。

## Task 6: 独立上下文对抗评审（Review R1）

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 委派一个 fresh-context 只读子代理执行独立评审（reviewer 合同：用户目标、spec/tasks/review 绝对路径、产物路径、AC 清单、核验要求），覆盖 AC-1～AC-7；结果写入 review.md。
  - `fail` 则把每条 actionable 发现物化为 Issue 回到实施；`pass` 方可收尾。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: review.md 存在且 R1 结论为 pass，每个 AC 有独立证据；证据：review.md。
  - `rubric` TR-6.2: 读者可用性维度独立评分 >=4 并附理由；证据：review.md CP 评分。
- **Completion Evidence**:
  - R1 结论 `pass`：CP-R1～R5 全过，CP-U1/CP-U2 均 5/5，无 actionable；2 项 advisory（00/02 补 O1 信源、verified actor 统一）已收口并在 review.md/log.md 记录；review.md 已落盘。
