# WorkBuddy 资料库协作与工作台实践 OKF Wiki - Implementation Plan

## Task 1: 核实来源并建立事实台账
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 对账 13 个原始链接与 S01–S11 唯一来源清单，确认标题、资料类型、内容边界与采集状态。
  - 将至少 20 条客观事实连续编号，逐项关联 S 编号；将作者观点、推论、产品声明和个案效果分开标注。
  - 记录 S11 主工作台正文未完整取得、四个 HTML 看板为虚构演示数据的边界。
  - 对数值、产品能力和可能影响使用决策的声明，优先与 `workbuddy-official-docs` 对应条目核对；有差异时并列来源口径，不静默择一。
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `rule` TR-1.1: S01–S11 与 Spec 来源表一一对应，重复 ID 只登记一次并注明两条重复链接；证据为 `references/article-source.md`。
  - `rule` TR-1.2: F 编号连续且不少于 20 条；任意抽查 10 条均能回溯至来源 ID；证据为事实台账抽查记录。
  - `rule` TR-1.3: S11 虚构数据声明与主工作台正文缺口均在台账及已知边界中显式登记；证据为台账与 bundle 首页。
- **Completion Evidence**: Spec `facts.md` 与 bundle `references/article-source.md` 各含 F-001–F-046；编号集合机械比对为 46/46 一致、连续、无重复。事实行 G1 因果/判断词扫描零命中。`references/verification.md` 记录产品交叉核对、P0 边界、S10 未核实案例数字及 S11 采集缺口/虚构数据。

## Task 2: 完成去重矩阵并冻结知识地图
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 S01–S11 映射到 `workbuddy-official-docs` 的 `concepts/06-knowledge-base-and-library.md`、`examples/05-knowledge-base-workflow.md` 及专家/技能相关页面。
  - 仅保留来源材料提供的实践增量、决策流程和案例；对产品机制与操作步骤使用相对链接，不复制官方包正文。
  - 按读者问题确定 4–6 篇概念页及目录导航；逐项执行 examples 可复现性两问，并记录保留或不创建 `examples/` 的理由。
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `rubric` TR-2.1: 重复控制质量，1=大量重复，3=有分工但仍有明显复述，5=各章节均体现实践增量且官方事实回链；通过阈值 >= 4；证据为来源—章节—既有包覆盖矩阵。
  - `rule` TR-2.2: 每篇计划章节均对应至少一个 S 编号，且已有官方内容不作为本包原创事实重复登记；证据为知识地图与引用。
  - `rule` TR-2.3: `examples/` 只在“可照做步骤”和“复现信息充分”两项均成立时创建；证据为两问判定表。
- **Completion Evidence**: `references/verification.md` 完成 S01–S11 对官方概念/示例页的覆盖矩阵、六篇概念页及来源映射，并逐项记录 S02/S03、S10、S11 的 examples 两问结果；均不满足双条件，因此不创建 `examples/`。逐章均有来源增量，官方产品机制与步骤明确回链、不复制；TR-2.1 评定 5/5，超过通过阈值。S03 URL 的 `?source=3` 已在 Spec 与来源台账对齐。

## Task 3: 先写信源与核验文档，再生成知识正文
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 `references/` 先创建来源事实清单和核验/边界记录，再创建 `concepts/` 正文；按 Task 2 的判定选择性创建 `examples/`。
  - 内容至少覆盖 Agent 共用工作空间、人机共编与审阅、MD/CSV/HTML 职责分工、团队协作和知识回存、专家搭建边界，以及面包店工作台案例中可溯源的独特结构。
  - 对 S10 个案避免推断普遍成效；对 S11 仅描述取得的看板与演示数据边界，不补写未取得的主工作台功能。
  - 概念页按读者问题组织，不按来源顺序或 WorkBuddy 原页面目录机械复制。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-3.1: 每项产品事实、具体数值及个案描述带 S/F 来源；作者观点与推论有显式标签；证据为逐页来源映射。
  - `rule` TR-3.2: 不存在将虚构数据写为真实业务数据、将单一个案写成普遍效果、或把未取得内容补写成事实的陈述；证据为四视角审查前的事实抽查。
  - `rubric` TR-3.3: 读者可用性，1=来源堆叠且术语无解释，3=主题可读但路径/分工不够清楚，5=按读者问题递进且能从实践页跳转到官方能力参照；通过阈值 >= 4；证据为章节导航与新人视角审读。
- **Completion Evidence**: 已生成 `concepts/index.md` 与六篇概念页，覆盖 S01–S11 并逐页映射 F 编号；产品机制链接回官方包，作者框架和本页建议分层标注。S10 的“3.4 万”明确标为未核实且不作为成效证据，家庭教育高风险案例声明为案例描述、非临床或危机处置指南；S11 虚构数据及主工作台采集缺口未越界。新增概念 Markdown 均有 frontmatter，机械检查到 0 条断链，引用的本包 F 编号有效（官方参照 F-169–F-170 单独注明）；不创建 `examples/`。

## Task 4: 完成包内导航及腾讯生态索引接入
- **Status**: `blocked`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 bundle 根 `index.md`、`log.md` 和所有需要的子目录 `index.md`；toctree 覆盖每个内容文件。
  - 为包首页添加与 `workbuddy-official-docs`、`workbuddy-one-sentence-mvp`、`tencent-buddy-family` 的关联说明。
  - 在 `jishu/ai/ecosystems/tencent/index.md` 和 `doc/bundles/index.md` 追加新包导航并同步计数；执行前读取当时磁盘计数，保留现有顺序并只追加。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 根及子目录 toctree 条目与实际 Markdown 文件一一对应，无孤立内容页；证据为 `invoke gates.toctrees`。
  - `rule` TR-4.2: 两级索引均出现新包，计数与实际目录一致；证据为 `invoke gates.bundles` 及索引 diff。
  - `rule` TR-4.3: 每个 Markdown 内容页均包含符合子项目规范的 YAML frontmatter，派生内容来源可追溯；证据为 frontmatter 检查结果。
- **Blocked By**: 子模块中出现由其他会话维护的未跟踪 `doc/bundles/jishu/ai/ecosystems/deepseek-search-fetch/`，其缺失 toctree 条目和上级索引计数漂移导致全局质量门失败；用户已确认该产物保持隔离，不在本任务范围内修改。
- **Unblock Condition**: 该包负责人完成其导航与索引接入，且 `python scripts/check-toctrees.py`、`python scripts/check-bundles-index.py` 在子模块全局通过后，恢复 Task 4，复核计数并完成 TR-4.1/TR-4.2。
- **Progress Evidence**: WorkBuddy 包 8 篇内容页 frontmatter 检查通过（修正为多行正则后 `FRONTMATTER_INVALID=0`）；包内含 6 篇概念、2 篇信源文档且无 `examples/`。全局 `python scripts/check-toctrees.py` 退出码 1，报告 11 项，均指向 `deepseek-search-fetch/` 或其上级 ecosystems 索引；`python scripts/check-bundles-index.py` 退出码 1，报告全库实际 649 包而索引为 648、技术域实际 480 而索引为 479。未修改并行产物及其索引。

## Task 5: 执行事实、链接、编码与构建验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 检查所有相对链接、`file:///`、UTF-8 编码、F 编号连续性、来源覆盖和事实台账/正文一致性。
  - 在 `projects/awesome-okf-xs` 子模块运行 `invoke gates.all` 与 `invoke build`。
  - 如果自动门禁因环境依赖无法运行，执行子项目规范要求的手动等效检查，记录实际命令与结果，不把手检描述成自动门禁通过。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 内部链接全部可达，`file:///` 零出现，新增 Markdown 文件均可 strict UTF-8 解码；证据为脚本输出或手工清单。
  - `rule` TR-5.2: `invoke gates.all` 与 `invoke build` 均通过；若环境阻断，则相关手动等效检查逐项有证据并如实登记；证据为命令输出与 `log.md`。
  - `rule` TR-5.3: 事实编号、来源清单、正文引用及首页统计相互一致；证据为机械集合比对和计数回核。

## Task 6: 独立四视角 Review 与修复闭环
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 在实施队列清空后创建 Spec Mode `review.md`，对照全部 AC/TR 建立检查点。
  - 由独立上下文执行一次只读审查，覆盖魔鬼代言人、新人、业务和未来视角；记录发现、裁定与证据。
  - 对每条可行动发现先登记为 `tasks.md` 修复项，再修复、回归验证并启动新一轮独立审查，直至通过。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-6.1: 每条 AC 至少由一个 Review 检查点覆盖，且每条检查有独立证据；证据为 `review.md`。
  - `rule` TR-6.2: 所有可行动发现均有对应修复任务和回归结果，最终 Review 结果为 `pass`；证据为修复任务与 Review History。
  - `rubric` TR-6.3: Spec Mode 工作流保真度，0=跳阶段/自审冒充独立审查，1=有一项非关键边界偏差，2=批准门、任务证据和独立 Review 边界均遵守；通过阈值 >= 2；证据为完整 Spec 产物与 Review History。
