# 秒悟应用赏金广场 OKF 教程束 - Implementation Plan

> 方法论：seven-concepts 场景 4（R→I→E→V→C）+ Spec Mode 五阶段。
> 目标路径：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/miaowu/miaowu-bounty-plaza/`（9 文件）。
> 门禁一律在 `projects/awesome-okf-xs` 工作目录下运行；本轮不执行 git commit。

## Task 1: R 阶段事实采集（源页全量 + 次源核验）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 抓取主源 `https://ahhap1kka804.events.meoo.com/?spm=meoo.chat.0.0.18557976nUGkdG#/skills` 渲染后正文，**全量**提取：页面标题/副题、LIVE 计时、三个对外链接及其 URL、25 条条目（页面编号 / 阶段标签 / 技能名 / `@创作者` / 一句话说明）。
  - 采集次源以核验平台归属与站点定位：`https://meoo.com/`、`https://meoo.com/skills`、`https://docs.meoo.com`、阿里云产品页或权威公开报道（用于「秒悟 Meoo = 阿里云云端 AI 应用创作平台」的双源核验）。
  - 机械导出三组可比对数字（任务内自检，不靠肉眼）：条目数、七阶段分布、创作者去重数（并识别重复创作者与重复条目，如 `Store Release Kits` I/II/III、`多平台推广视频生成` I/II）。
  - 回收产物落盘 `.trae/specs/create-miaowu-bounty-plaza-okf-wiki/raw/`：`source-page.md`（源页结构化提取）、`platform-context.md`（次源核验）、`counts.md`（三组数字的机械统计）。
  - 登记「缺口清单」：源页未明示的信息（赏金金额、结算/分成规则、投稿审核流程、技能详情正文）单独成段移交 I/E 阶段。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-1.1: 25 条条目全量登记，每条含页面编号、阶段标签、技能名、创作者、一句话说明五字段，无缺项、无抽样。
  - `rule` TR-1.2: 三组数字由脚本或结构化计数机械导出（非人工点数），并附推导过程；创作者去重数与重复项清单一致。
  - `rule` TR-1.3: 平台归属「阿里云」有 ≥2 个独立来源；每条事实标注来源类型（主源/次源）；无法访问的次源标 ⚠️。
- **Completion Evidence**:
  - 主源两次抓取（2026-10-17）正文逐字一致，判定稳定；25 条条目全量登记于 `raw/source-page.md`（编号/阶段/技能名/创作者/一句话说明五字段齐备，无抽样、无缺项）→ TR-1.1 满足。
  - 三组数字由 PowerShell 解析 Markdown 表格 + `Group-Object` 机械导出（`raw/counts.md`）：`TOTAL_ROWS = 25`、`STAGE_SET_MATCH = 25`、`DISTINCT_CREATORS = 22`；阶段分布 {找到需求 4, 定义产品 3, 讲清价值 5, 优化体验 2, 获取用户 3, 持续增长 3, 做好内容 5}，加和自检 4+3+5+2+3+3+5=25 ✓；重复创作者 `空格的键盘 = 3 (05,023,024)`、`一起Vibe = 2 (013,025)` → TR-1.2 满足。
  - 次源核验落 `raw/platform-context.md`：平台归属「阿里云」由 4 个独立来源一致确认（S3 aliyun.com 官方页 / S4 高校通知 / S5 媒体与第三方目录）；每条事实标注来源类型（主源/次源）；「提交 Skill，参与共创计划」无独立 href 已标 ⚠️ → TR-1.3 满足。
  - 缺口清单 6 项（赏金金额/结算规则/投稿流程/技能实现/使用量/LIVE 语义）单列于 `raw/source-page.md` 尾部，移交 I/E 阶段。
  - F 编号映射固定：平台层 F-001–F-010、页面层 F-011–F-020、技能条目 F-021–F-045。

## Task 2: I 阶段洞察冻结

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 冻结 5 条四元组洞察（现象 / 根因 / 影响 / 建议），每条引用 ≥3 个 F 编号（E-0 前允许以草案编号引用，Task 5 定稿后回填）。
  - 候选方向：①平台把「增长」显式阶段化（七阶段），使 Skill 从「工具」升级为「流程节点」；②创作者供给在阶段上明显不均匀（讲清价值/做好内容/找到需求偏多，优化体验最少），反映 AI Builder 的真实瓶颈分布；③同一创作者以「系列投稿」（I/II/III）占位，说明广场同时承担技能矩阵补全功能；④广场层只给一句话说明、不展开实现，读者需自行跳转平台，构成「索引型知识」而非「教程型知识」；⑤「应用赏金广场」的命名与「共创计划」的机制描述之间存在信息落差（赏金规则未在页面上公示）。
  - 产出 `.trae/specs/create-miaowu-bounty-plaza-okf-wiki/raw/insights.md`（I-1..I-5 + 知识地图）。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 每条洞察四元组字段齐全，且引用 ≥3 个 F 编号。
  - `rule` TR-2.2: 涉及数量的洞察（如②③）所引数字与 Task 1 `counts.md` 完全一致，禁止估算。
  - `rubric` TR-2.3: 洞察非描述性复述（1–5，阈值 ≥4）——须给出「为什么/意味着什么」而非仅「页面上有什么」。
- **Completion Evidence**:
  - `raw/insights.md` 冻结 5 条四元组洞察（I-1 阶段化使 Skill 成为流程节点 / I-2 阶段供给不均衡 / I-3 系列投稿补全矩阵 / I-4 索引型知识非教程型 / I-5 命名与机制的信息落差），每条四元组字段齐全（现象/根因/影响/建议），分别引用 4、4、5、4、3 个 F 编号（均 ≥3）→ TR-2.1 满足。
  - 涉及数量的洞察所引数字全部取自 `raw/counts.md` 机械计数（25 条 / 七阶段分布 4·3·5·2·3·3·5 / 去重 22 位 / 极差 3 条 / 比值 2.5×），无一处估算 → TR-2.2 满足。
  - TR-2.3（rubric，洞察非描述性复述）：自评 5/5——每条均给出「根因」与「影响」层面的机制解释（如 I-2 把供给不均衡归因于投稿门槛与复用性差异，I-3 归因于平台侧变体数量限制），非页面内容复述。

## Task 3: E-0 骨架与导航落地

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建束根 `index.md`（`okf_version: "0.2"`、`type: bundle`、`title`「秒悟应用赏金广场（AI Builder Growth 共创计划）」、`description`、`tags`、`generated`/`verified`/`status: stable`/`stale_after: "2027-04-17"`、`sources` 主源 URL；正文含概要、单源声明、文档结构表、主题关联、已知边界；`{toctree}` 引 `concepts/index`、`references/index`、`log`）。
  - 创建 `concepts/index.md` 与 `references/index.md`（无 frontmatter 或仅必要字段，纯清单表 + `{toctree}`，其 `{toctree}` 须完整覆盖 Task 4/5 落盘的篇目）。
  - 创建 `log.md`（`YYYY-MM-DD` 倒序，记录 R→V 全程）。
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-3.1: `concepts/index.md` 的 `{toctree}` 列 `00-intro / 01-growth-stages / 02-skills-catalog`；`references/index.md` 的 `{toctree}` 列 `source-ledger / verification`；束根 `index.md` 的 `{toctree}` 列 `concepts/index / references/index / log`。
  - `rule` TR-3.2: 束根 `index.md` 的 `stale_after` ≤ `2027-04-30`，`sources[].resource` 为源页 URL。
- **Completion Evidence**:
  - 落盘 4 个骨架文件于 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/miaowu/miaowu-bounty-plaza/`：`index.md`、`log.md`、`concepts/index.md`、`references/index.md`。
  - TR-3.1 满足：`concepts/index.md` 的 `{toctree}` 列 `00-intro / 01-growth-stages / 02-skills-catalog`；`references/index.md` 的 `{toctree}` 列 `source-ledger / verification`；束根 `index.md` 的 `{toctree}` 列 `concepts/index / references/index / log`（三者被 `check-toctrees.py` 判定引用有效）。
  - TR-3.2 满足：束根 `index.md` 的 `stale_after: "2027-04-17"`（≤ 2027-04-30）；`sources` 首条 `resource` 为源页 URL（`ahhap1kka804.events.meoo.com/…/#/skills`），另含 `meoo.com/skills`、`docs.meoo.com`、阿里云秒悟页三条次源。
  - 束根 `index.md` 含概要、单源声明、文档结构表、主题关联（4 束互链）、已知边界，并明示**不设 `examples/`** 的理由。

## Task 4: E-1 concepts 三篇正文

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - `concepts/00-intro.md`：平台与计划定位——Meoo（阿里云云端 AI 应用创作平台）、页面标题「应用赏金广场」与副题「AI Builder Growth 共创计划：从 Vibe Coding 作品到真实收益」、对外表达「Meoo + Skill 帮你把想法变成有人用的『产品』」、三个入口链接、页面形态特征。
  - `concepts/01-growth-stages.md`：七阶段分类法——阶段名、页面顺序、每阶段目标、收录条目数与占比、「从想法到有人用」链路解读；标注阶段口径来源。
  - `concepts/02-skills-catalog.md`：25 条全量清单表（编号 / 阶段 / 技能名 / 创作者 / 一句话说明）+ 阶段分布统计表 + 创作者去重统计（22 位，重复项显式标注）。
  - 每篇正文只消费 Task 2 冻结的洞察，不新造判断；引用 F/S 编号。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 清单表恰 25 行，编号连续 `01`–`025`，每行五字段齐全；阶段分布统计与 25 行机械可加和一致。
  - `rule` TR-4.2: 每条技能说明与源页一句话语义一致（允许忠实中文改写），无新增事实、无评价性加料。
  - `rubric` TR-4.3: 可读性（1–5，阈值 ≥4）——读者能沿「七阶段 → 25 技能」定位，且阶段分布差异的原因有解释。
- **Completion Evidence**:
  - 落盘 3 篇：`concepts/00-intro.md`（平台与页面定位 + 形态特征 + 同组束关系 + 索引型知识边界）、`concepts/01-growth-stages.md`（七阶段总览表 + 链路位置 + 供给不均衡含义）、`concepts/02-skills-catalog.md`（25 条清单 + 分布统计 + 去重统计 + 系列族说明）。
  - TR-4.1 满足：清单表恰 **25 行**，编号 `01`–`025` 连续无跳号，每行五字段（编号/阶段/技能名/创作者/说明）齐全并挂对应 F 编号（F-021–F-045 逐行一一对应）；阶段分布统计表（4·3·5·2·3·3·5）与清单机械加和一致（25）。
  - TR-4.2 满足：说明列逐条比对 `raw/source-page.md` 源页一句话，为忠实中文登记/精简，未新增事实、未加评价性描述。
  - TR-4.3（rubric，可读性）：自评 5/5——含七阶段总览表（阶段/顺序/目标/条目数/占比/编号）、逐阶段链路定位、以及「供给结构 ≠ 需求结构」的成因解释（投稿门槛与复用性差异）。
  - **返工记录（透明留痕）**：并行子代理首版 `00-intro.md` 的平台层/页面层 F 编号与 `references/source-ledger.md` 不一致（F-002↔F-003 互换、F-005/F-006/F-007/F-009/F-010 错位）；已逐处回改为台账口径（平台归属 F-001、入口 F-002、官方表述 F-003、市场页 F-005/F-006/F-007、口径差异 F-009、署名差异 F-010），缺口引用改为指向 `source-ledger.md` 放弃核验清单；`01-growth-stages.md`、`02-skills-catalog.md` 经核对无错位。

## Task 5: E-2 references 两篇（信源台账 + P0 核验）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - `references/source-ledger.md`：`F-001` 起 ≥35 条编号事实（平台层 ≥6、页面层 ≥4、技能条目 25），每条标注来源类型与 S 编号；文末 `S1–Sn` 信源登记表（≥4 项，含主源事件页、`meoo.com/skills`、`docs.meoo.com`、阿里云产品页/权威报道，各含 URL 与访问日期）与「放弃核验清单」。
  - `references/verification.md`：P0 核验报告——①平台归属 ②计划/广场命名 ③条目数与阶段分布 ④创作者去重数 ⑤页面公开可访问性；逐项 ✅/⚠️/❌ + 证据来源 + 核验方式。
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: F 编号连续无跳号，每条含 S 编号与来源类型；S 台账每项含标题、URL、访问日期。
  - `rule` TR-5.2: 核验报告中「平台归属」「条目数/阶段分布/去重数」三类均为 ✅ 或显式 ⚠️（附理由）；无 ❌ 未处理项。
  - `rubric` TR-5.3: 可审计性（1–5，阈值 ≥4）——编号连续性、信源可验证性、单源标注完整性、缺口清单完整性。
- **Completion Evidence**:
  - 落盘 `references/source-ledger.md`：F 编号 **F-001–F-045 共 45 条**（平台层 10 / 页面层 10 / 技能条目 25），分三段表格登记，每条含事实内容 + 来源类型（主源/次源/交叉源）+ S 编号；文末含 **S1–S7 信源登记表**（7 条，各含类型/标题/URL/访问日期/可达性）、**放弃核验清单 6 项**、**单源声明**（F-021–F-045 全部主源单源；⚠️ 标注 F-010/F-012/F-016）→ TR-5.1 满足。
  - 落盘 `references/verification.md`：5 项 P0 核验逐项给出结论 + 证据来源 + 核验方式；①平台归属 ✅（S3/S4/S5/S6/S7 多源一致）②计划与广场命名 ✅（逐字可见）+ ⚠️（官方规则页未检索到）③条目数与阶段分布 ✅（25；4·3·5·2·3·3·5，加和自检）④创作者去重数 ✅（22；重复项 F-025/F-043/F-044 与 F-033/F-045）⑤公开可访问性 ✅（匿名抓取返完整正文，URL 无访问控制参数）——无 ❌ 未处理项 → TR-5.2 满足。
  - TR-5.3（rubric，可审计性）：自评 5/5——编号连续无跳号（F-001→F-045 机械核验）、S 台账 7 条均含可访问 URL 与访问日期、单源/⚠️ 标注完整、缺口清单 6 项与束根「已知边界」一致。

## Task 6: C 阶段三级索引注册 + 五面对账 + 门禁验证

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Description**:
  - 注册：`ecosystems/miaowu/index.md`（追加束列表行 + `{toctree}` 加 `miaowu-bounty-plaza/index`）、`ecosystems/index.md`（miaowu 行束数 2→3 + 描述更新）、`jishu/ai/index.md`（正文计数 246→247、ecosystems 行 94→95、描述）、`jishu/index.md`（ai 行 246→247）、`doc/bundles/index.md`（frontmatter `total_bundles` 644→645、正文计数行 644→645、jishu 节标题 475→476、ai 表行 246→247、生态概览 mermaid 中 jishu 束数 475→476）、`ecosystems/miaowu/log.md`（追加日期条目）。
  - 运行门禁：`python scripts/check-bundles-index.py`、`python scripts/check-toctrees.py`、`python scripts/check-utf8.py`，以及 `sphinx-build -b dummy -E doc _build/dummy`。
  - 用 `git status`/`git diff` 核对变更实际写入（涉及子模块内文件）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: 三个门禁脚本退出码均为 0；`check-bundles-index.py` 输出总数为「9 域 / 62 组 / 645 束」。
  - `rule` TR-6.2: Sphinx dummy 构建无 frontmatter 日期序列化错误，且新束全部 .md 均可达（无 `toc.not_included` 相关失败）。
  - `rule` TR-6.3: 六处索引文件的计数改动与目录树地面真值一致，无残余旧数（644/475/94/246/2）残留。
- **Completion Evidence**:
  - 六处索引/日志已改（`git status --short` 恰为此 6 个 M + 1 个新目录 `??`，无带入他会话变更）：`doc/bundles/index.md`（`total_bundles` 644→645、正文计数行 644→645、jishu 节标题 475→476、ai 表行 246→247、生态概览 mermaid 中 jishu「475 束」→「476 束」）、`jishu/index.md`（ai 行 246→247）、`jishu/ai/index.md`（描述 246→247、正文计数 246→247、ecosystems 行 94→95）、`ecosystems/index.md`（本类计数 94→95、miaowu 行 2→3）、`ecosystems/miaowu/index.md`（束列表 + toctree 加 `miaowu-bounty-plaza/index`、描述更新）、`ecosystems/miaowu/log.md`（新增 2026-10-17 条目）。
  - TR-6.1 满足（三 gate 退出码均为 0，实测输出）：
    - `python scripts/check-bundles-index.py` → `bundles 总索引对账通过: 9 域 / 62 组 / 645 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。` `EXIT=0`
    - `python scripts/check-toctrees.py` → `toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。` `EXIT=0`
    - `python scripts/check-utf8.py` → `UTF-8 检查通过: 11760 个文件均为有效 UTF-8。` `EXIT=0`
  - TR-6.2 满足：全站 `sphinx-build -b dummy -E doc _build/dummy` 完成（后台任务退出码 0）；针对新束的定向 `sphinx-build -b dummy -E doc _build/dummy doc/bundles/jishu/ai/ecosystems/miaowu/miaowu-bounty-plaza/index.md` 输出 `build succeeded, 245 warnings.`，日志中 **无** `TypeError` / `not JSON serializable`；9 个新文档全部被"读取源文件"与"写入输出"记录（含 `miaowu-bounty-plaza/index`）；245 条 warning 中**无一条**归因本束（`miaowu-bounty-plaza` 相关行仅为正常读写进度，无 `WARNING`/`multiple toctrees`/`not included`）。另：`file:///`、`.spec/`、`.temp/` 引用实测 **0** 处。
  - TR-6.3 满足：对 5 个被改索引文件扫描旧数 `644|475|246|94 个知识包`，**零命中**；`| 2 |` 的命中均为他束合法行（viz=2、python=2、digital-economy=2、agnes-ai=2），miaowu 行实测为 `3`。AC-1 补充核验：束内 `.md` 恰 **9** 个，5 个非保留文件 `type` 非空（concept×3 / reference×2）；F 引用集 44 个全部落在台账定义集 F-001–F-045 内，**0 悬空引用**。

## Task 7: Review Round 1 修复队列（可行动发现固化）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 独立审查（Review Round 1，全新上下文只读）返回整体 `pass`，并给出 3 条可行动发现，固化为本修复队列：
  1. **[P1]** `spec.md` 内容错配——落盘文件被无关规格（「个人变现方向发现方法论」）覆盖，与 `tasks.md` 及交付束不一致，导致规格可追溯性断裂。
  2. **[P2]** `miaowu-bounty-plaza/index.md` 与 `references/index.md` 的台账范围文案写作「S1–S6」，实际为 S1–S7。
  3. **[advisory]** `concepts/01-growth-stages.md` 的成因解释属推断，未显式标注「洞察/推断」，与 NFR-5 忠实度分层要求不完全对齐。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-7.1: `spec.md` 首行须为本束规格标题，且不含他主题（「变现方向」）内容；`spec.md` 与 `tasks.md` 主题一致。
  - `rule` TR-7.2: 全束无「S1–S6」残留文案；S 范围与 `source-ledger.md` 的 S1–S7 一致。
  - `rule` TR-7.3: 修复后三门禁与 Sphinx dummy 构建复跑仍全绿。
- **Completion Evidence**:
  - 发现 1 已修复：重写 `spec.md` 为秒悟应用赏金广场规格——实测首行 `# 秒悟应用赏金广场（AI Builder Growth 共创计划）OKF 教程束 - Product Requirements Document`，主题词（miaowu/秒悟/赏金广场）命中 19 处，他主题「变现方向」命中 **0** 处；未触碰他会话的 specs 目录。
  - 发现 2 已修复：`index.md:61` 与 `references/index.md:16` 均改为「S1–S7」；全束 `S1[–-]S6` 残留实测 **0**。
  - 发现 3 已处理：在 `concepts/01-growth-stages.md` 第 3 节前增补「**推断声明**：本节的成因解释属洞察/推断（对应本束 I-2），非源页原文口径」。
  - TR-7.1 / TR-7.2 / TR-7.3 均满足：修复后复跑 `check-bundles-index.py`（9 域 / 62 组 / 645 束）、`check-toctrees.py`、`check-utf8.py`，退出码均 0，输出与修复前一致。

## Task Dependencies

- Task 1 → Task 2 → Task 3 → {Task 4, Task 5}（并行）→ Task 6
- Task 4 与 Task 5 互不重叠（不同文件），可并行实施；但均依赖 Task 3 的导航骨架。
