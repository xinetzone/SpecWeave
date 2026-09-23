# Tasks — 知乎变现体系深度学习 · OKF Wiki 与个人变现路径

> 派生自 spec.md 验收标准 AC-1 ~ AC-11。状态取值：pending / in_progress / blocked / completed / cancelled。
> 任务标题不含状态标记；本地验证失败保持 `in_progress`，不设 `failed`。

## Task 1: 信源全文提取（R-a）

**Priority**: high
**Status**: completed
**映射 AC**: AC-1（事实覆盖的来源前提）
**内容**: 对 S1（project-square）、S2（打卡挑战活动页）、S3（开源主题活动页）执行信源获取链：WebFetch → browser_use 子代理（渲染后提取全文正文，核对长度低于 500 字即判定提取失败重试）→ 仍失败向用户求助。提取全文按信源存于 spec 区（raw/ 子目录），campaign 页关键规则截图一并存档。S1 静态提取已确认失败（"加载失败"），直接以 browser_use 为主通道。

- [x] Subtask 1.1: S1 项目广场 browser_use 渲染提取，存档 raw/s1-project-square.md
- [x] Subtask 1.2: S2 活动页 A browser_use 补全提取，存档 raw/s2-campaign-checkin.md（+规则截图）
- [x] Subtask 1.3: S3 活动页 B browser_use 补全提取，存档 raw/s3-campaign-opensource.md（+规则截图）
- [x] Subtask 1.4: 三信源提取结果完整性核对（正文长度、规则条款占比），失败项升级处理

**Test Requirements**:
- TR-1.1 (rule): 三个 raw 文件存在且各含 ≥800 字有效正文（或已升级为用户提供并留痕）；任一信源未提取不得进入 Task 2

**完成记录（2026-09-23）**: 三信源均提取成功。实际通道为 agent-browser CLI（browser_use 子代理因 Chrome/TRAE 扩展不可用被 BLOCKED 后切换）。
- S1：get text body 成功，18 条最热项目 + 20 条热门榜单，含页面框架（分类/标签/排序）；
- S2：页面标题确认「创作打卡挑战赛第五十三期」，四 Tab 全覆盖（打卡挑战=文本提取；回答任务/想法任务/惊喜彩蛋=点击切换后截图转录，SPA 面板不被 body 文本捕获）；
- S3：正文为图像化渲染，2x retina 分 9 段截图读图转录，三大计划奖励与六个圈子、时间表、伙伴名单齐备；
- 中间文件（s1-raw-text.txt、s2-tab-*.txt、s2-snapshot-tabs.txt）已清理，防旧 DOM 内容误用。

## Task 2: F 编号事实采集（R-b）

**Priority**: high
**Status**: completed
**依赖**: Task 1
**映射 AC**: AC-1, AC-6
**内容**: 从三信源 raw 提取全部关键声明，F-001 起连续编号登记 spec 区 `facts.md`：项目清单、奖励机制与奖池规模、参与门槛、话题领域、时间规则、盐粒/提现规则、任务类型（答题/想法/彩蛋）。平台口径声明标"平台口径"；推断性内容禁止进入 facts.md（G1：无推断词）。

- [x] Subtask 2.1: 通读三 raw，抽取事实条目并编号登记 facts.md
- [x] Subtask 2.2: 事实表结构与字段统一（编号/声明/信源定位/口径类型/备注）
- [x] Subtask 2.3: G1 自检（facts.md 无"因为/导致/所以"等推断词；观点显式标注）

**Test Requirements**:
- TR-2.1 (rule): facts.md 存在且编号连续（跳号有注记）；三信源均有 ≥5 条事实覆盖
- TR-2.2 (rule): G1 检查通过（无推断词污染）

**完成记录（2026-09-23）**: facts.md 落盘 spec 区，54 条事实连续编号（F-001~F-054 无跳号）。
- 信源覆盖：S1=27（项目广场框架+最热 18 条+榜单结构）、S2=16（四 Tab 规则全量）、S3=11（科学季三计划+六圈子+时间表）；
- 口径类型四分类（平台口径/平台展示值/页面结构/提取者转录）；P0 标记 16 条（Task 3 核验清单）；
- 已知口径缺口 4 项单列（盐粒兑换比缺席、报名资格关系、热度/榜单口径、时间窗年份细节）；
- G1 机械自查通过（grep 推断词仅命中图例元描述两处，事实表零污染）；提取者备注段未入表；F-009 字段归属已按截图裁定留痕。

## Task 3: P0 权威核验与勘误（R-c）

**Priority**: high
**Status**: completed
**依赖**: Task 2
**映射 AC**: AC-2, AC-6
**内容**: 对 P0 类声明（奖池规模/盐粒兑换比/活动时间/参与门槛/规则条款）以 WebSearch 官方源（知乎创作平台/帮助中心/官方公告）核验，逐项过勘误四张清单（日期版本/成效溯源/口径对照/引文逐字），产出 spec 区 verification 记录。无法核验项显式标"仅平台活动页单源"；核验发现源文错误时新增 F 编号记正确值并单列勘误。本阶段禁止 WebSearch 不到来源却硬编 URL（假核验红线）。

- [x] Subtask 3.1: P0 声明清单化（从 facts.md 抽取，含平台口径/独立来源两列）
- [x] Subtask 3.2: WebSearch 官方源逐项核验（独立子代理上下文，每任务给完整声明清单）
- [x] Subtask 3.3: 勘误四清单过筛并记录；源文错误按"新增 F 编号 + 勘误单列"处理

**Test Requirements**:
- TR-3.1 (rule): P0 声明 100% 有核验记录（官方 URL 或"单源"标注）；零伪造 URL
- TR-3.2 (rule): 勘误四张清单均有书面过筛记录

**完成记录（2026-09-23）**: verification.md 落盘 spec 区；三组并行核验（A=S2 打卡规则，B=S2/S3 奖池，C=时间口径+盐粒兑换比）。
- 结论分布：确认 1（F-047 万元现金，科普中国官方账号）、部分确认 5（F-026/F-033/F-034/F-044/F-048/F-052 中 6 条）、仅平台活动页单源 10；四缺口均有结论（盐粒 100:1=合作方官方公告+多三级源，无知乎域名官方页）；
- 关键限制留痕：搜索引擎对 zhihu.com 站内零收录、/help 404、S2 活动页 JS 渲染致横幅/今日任务 WebFetch 不复现（截图转录为证）；
- 防混用三对照固化：100,000 盐粒分属两活动（F-058 vs F-048）、纪念卡≠徽章（F-056 vs F-048）、100:1 vs 2019 年 10:1 场景分离；
- 补充事实 F-055~F-067 已回写 facts.md（67 条连续无跳号），双份登记基准就绪；
- flagged 判定：设 `status: flagged`，stale_after ≤ 2026-12-31；红线自查零伪造 URL（A 组证据 URL 经 resume 补交核验）。

## Task 4: 骨架判定与归属决策（I-a）

**Priority**: medium
**Status**: completed
**依赖**: Task 3
**映射 AC**: AC-3, AC-4
**内容**: ①「操作可复现性两问」判定 examples/ 取舍（预期：信源为活动规则宣告页 → 无 examples，操作步骤并入 concepts；若判相反须记录理由）；②归属决策树执行：单篇不新建顶级分组，候选对照表（sheke/industry vs 其他既有组）写入 spec 区留痕，预期落 `sheke/industry`；③确认 industry 组 index 与总 index 现值计数（读取现值，不凭记忆）。

- [x] Subtask 4.1: 两问判定 + 理由记录（log.md 或 spec 区）
- [x] Subtask 4.2: 归属候选对照表（候选位置 | 判定 | 理由）落盘
- [x] Subtask 4.3: 读取组 index/总 index 现值计数（束数、total_bundles、sheke 域束数）

**Test Requirements**:
- TR-4.1 (rule): 判定与归属理由已留痕；未新建顶级分组
- TR-4.2 (rule): 现值计数已读取并记录（后续 +1 以此为基准）

**完成记录（2026-09-23）**: decision-log.md 落盘 spec 区。
- 两问判定：信源为活动规则宣告页 + 行动清单属设计产物 → **无 examples/**，步骤并入 concepts 路径层；
- 归属：**sheke/industry/zhihu-monetization**（候选对照表 6 项，未新建顶级分组）；
- 现值实测：总 index total_bundles=564 / groups=59 / domains=9，sheke 41 束；industry 组导航表 18 行 / toctree 18 条 / description「18 束」三处一致；sheke/index.md 两处计数（16 束方向列表 + 18 束分组表）已登记待更新项 → 更新后分别 17/19。

## Task 5: 三层知识拆分设计（I-b）

**Priority**: high
**Status**: completed
**依赖**: Task 4
**映射 AC**: AC-4, AC-8（路径层的知识地基）、AC-10（G2）
**内容**: 设计 concepts 篇目规划（事实层 → 机制层 → 路径层），每篇标注拟引用 F 编号；输出洞察四元组（现象+根因+影响+建议，G2）——如"盐粒激励的时间结构""打卡机制的留存设计""活动入口与长期能力建设的关系"。因果分析与事实分层呈现。产出写入 spec 区（knowledge-map.md）。

- [x] Subtask 5.1: 篇目规划（文件名 kebab-case、每篇职责与 F 编号映射）
- [x] Subtask 5.2: 洞察四元组撰写（机制层 Why，标注为洞察非事实）
- [x] Subtask 5.3: 同主题簇 bundle 互链清单（ai-monetization / monetization-essence / overseas-freelance-night-work）

**Test Requirements**:
- TR-5.1 (rubric): 拆分合理（事实/机制/路径三层无缺层、无混层）；锚点 ≥1.5/2
- TR-5.2 (rule): 每篇 concepts 均有 F 编号映射来源

**完成记录（2026-09-23）**: knowledge-map.md 落盘 spec 区。
- 篇目 10 篇 concepts（00 总览 + 01~03 事实层 + 04~06 机制层 + 07~09 路径层）+ references/（article-source + verification）+ index + log；无 examples/（Task 4 判定一致）；
- 洞察四元组 5 条（时间结构/多层奖池/AI 排除条款信号意义/流量-资产双轨/专业内容时间窗），现象全部挂 F、根因影响建议显式标推断；
- 互链 4 个同簇 bundle；Task 6 生成顺序按 G3 信源先行排定（references → concepts 00→09 → index → log → 三处索引更新）。

## Task 6: OKF bundle 生成（E）

**Priority**: high
**Status**: completed
**依赖**: Task 5
**映射 AC**: AC-3, AC-4, AC-5（结构面）, AC-6
**内容**: 按信源先行顺序生成 `projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/`：references/（article-source.md 事实清单——与 facts.md 双份登记 + verification.md 核验报告）→ concepts/ → 各级 index.md 最后写；根 index 加"主题关联"段与同簇 bundle 互链；更新 industry 组 index（导航表 +1 行、toctree +1 条、束数 +1）与总 index（total_bundles +1、sheke 域束数 +1、三处计数同步）；frontmatter 十字段齐备；`status: flagged` 判定（P0 失败项为核心声明时）；stale_after ≤ 2026-12-31（单篇活动解析 ≤ 3 个月）。

- [x] Subtask 6.1: references/ 生成（article-source.md + verification.md，F 编号与 facts.md 一致）
- [x] Subtask 6.2: concepts/ 生成（按 Task 5 篇目，全部声明挂 F 编号）
- [x] Subtask 6.3: 根 index.md + log.md（含骨架判定/归属理由/时效声明）
- [x] Subtask 6.4: 组 index 与总 index 更新（导航表/toctree/三处计数 +1）
- [x] Subtask 6.5: flagged 状态判定与处理（若触发：顶部明示 + 到期复核安排）

**Test Requirements**:
- TR-6.1 (rule): 目录结构与 frontmatter 十字段符合 AC-4；index 与 log 齐备
- TR-6.2 (rule): toctree 三级完整、计数三面同步（基于 Task 4.3 现值 +1）
- TR-6.3 (rule): 双份 F 编号集合一致；正文无 F 之外的编造数字

**完成记录（2026-09-23）**: bundle 落盘 `projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/`，共 14 个 .md：
- 结构：index.md + log.md + concepts/00~09（10 篇）+ references/（article-source.md + verification.md），无 examples/（与 Task 4 判定一致）；
- frontmatter 十字段齐备；`status: flagged` + `stale_after: 2026-12-31`（P0 16 条中 10 条为平台活动页单源，F-059 兑换比无知乎域名官方页）；
- 互链：根 index「主题关联」段 4 个同簇 bundle（ai-monetization / monetization-essence / overseas-freelance-night-work / ai-one-person-micro-product）；
- 索引三处同步（基于 Task 4.3 现值 +1）：industry/index.md 三处 19 束（description/导航表/toctree 各 +1）；sheke/index.md L17「17 束」+ L32「（19 束）」；bundles/index.md total_bundles=565、mermaid 图 sheke 42 束、域导航「42 束 · 7 组」；
- 我方复核（Trust but verify）：14 文件 Glob 存在；article-source.md 与 facts.md 各 67 条 `| F-XXX |` 表行相等；抽查 concepts/04（奖池全景每行挂 F、100:1 与 10:1 防混用三对照显性化）与 index.md（flagged 提示/导航表/toctree 齐备）质量合格；02/03/05/07/08/09 篇亦在生成清单内逐篇生成。

## Task 7: 个人变现路径设计（F）

**Priority**: high
**Status**: completed
**依赖**: Task 5（知识地图即可启动，不必等 Task 6 完稿）
**映射 AC**: AC-8（内容要素）、AC-9、 AC-10（F 概念）
**内容**: 第一性原理推导：从"个人可变现能力 × 平台激励结构 × 时间约束（每日 ≤2h）"反推路径，而非堆砌入口。产出：① 角色化路径矩阵（≥3 类角色，每角色一条子路径）；② 针对 AI/技术内容创作者的主路径详解（起点条件 → 准入门槛 → 第 1 周/第 1 月/持续期行动清单 → 预期收益区间 → 退出/切换条件）；③ 每条行动项原子化（单一职责/可独立验证/验收标准）。收益区间仅引用 bundle F 编号口径或标"待验证"，禁止承诺性表述。设计稿落 spec 区（path-design.md）。

- [x] Subtask 7.1: 第一性原理推导记录（假设拆解 → 约束 → 路径要素）
- [x] Subtask 7.2: 角色矩阵 + 主路径设计稿（path-design.md）
- [x] Subtask 7.3: 行动项原子化拆解（每项可独立验证）

**Test Requirements**:
- TR-7.1 (rubric): 每条路径含起点/门槛/分阶段行动/收益区间/退出条件五要素；锚点 ≥1.5/2
- TR-7.2 (rule): 收益/门槛声明 100% 挂 F 编号或"待验证"；零承诺性收益表述

**完成记录（2026-09-23）**: path-design.md 落盘 spec 区。
- 第一性原理：A1-A3（能力面）/B1-B3（平台结构面）/C1-C3（约束面）推导 → P1-P6 路径要素；
- 三角色矩阵（AI/技术创作者主路径 + 通勤碎片创作者 + 专业领域答主）各含起点/门槛/分阶段行动/收益区间/退出条件五要素；
- 主路径 18 条原子化行动项（W1-1~6 第 1 周 / M1-1~6 第 1 月 / O-1-6 持续期），每项带验收标准，可独立验证；
- 收益测算全部挂 F 编号（奖池口径换算）或标「待验证」（瓜分人均无信源），承诺词机械扫描零命中；反画饼自检 7 条内置；
- 科学季报名窗按实际核定处理：今日 2026-09-23 在 9.30 截止前（仅剩数日），设计稿不预设仍开放，主力按错失设计 + 48 小时补位分支（我方 prompt 中「9.3–9.30 已过」有误，已按子代理纠正口径留痕）。

## Task 8: 路径对抗审查与文档生成（V-F → 产出）

**Priority**: high
**Status**: completed
**依赖**: Task 6, Task 7
**映射 AC**: AC-8, AC-9, AC-10（V 概念）
**内容**: 对路径设计执行对抗审查（F 后强制 V）：四视角（事实溯源/结构规范/读者可用性/时效边界）+ 魔鬼代言人证伪"画饼路径"（逐条攻击：冷启动时长、盐粒实际到手、规则变动风险）；新人视角 + 每日 ≤2h 约束逐路径可行性检验。审查通过后按落盘前三查确定 docs/ 子目录（查 docs/ 结构、查同类先例 competitive-analysis 体例、查规范原文），生成公开脱敏文档，frontmatter 带 source 溯源与规则时点标注。

- [x] Subtask 8.1: 四视角 + 魔鬼代言人审查执行，记录每视角发现
- [x] Subtask 8.2: 审查发现修复（画饼/不可达项回 Task 7 修正后复审）
- [x] Subtask 8.3: 落盘前三查 + docs/ 文档生成（脱敏 + source frontmatter + 时点标注）

**Test Requirements**:
- TR-8.1 (rubric): AC-9 路径可达性达标（≥1.5 且无未证伪路径）；审查记录留痕
- TR-8.2 (rule): 文档含 AC-8 全部要素且位于 docs/ 公开位置

**完成记录（2026-09-23）**: 审查执行 + 修复 + docs/ 产出三段完成。
- 四视角 19 条发现（事实溯源 4/结构规范 5/读者可用性 3/时效边界 4 + 重大缺陷合并 3）全处理；魔鬼代言人五点证伪：#4 AI 协作排除条款**成立（重大缺陷）**——原稿仅两行提及、无可操作自检，已修复；#1 冷启动部分成立（期中加入场景缺失），已补；#2 盐粒到手/#3 规则变动/#5 流量-资产悖论均不成立（原稿有充分回应）；
- path-design.md 修订 13 处带「【V 修订·2026-09-23】」标注（无静默改写），核心新增 §3.8「AI 协作排除条款可操作自检」（双轨合规区分表 + 发布前三问 + 诚实边界）；
- 落盘前三查结论：docs/knowledge/learning/ 已迁 bundles（磁盘实测不存在），按 spec.md FR4 引用的 competitive-analysis 体例落 `docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/`（index/README/ai-creator-main-path/risks-and-boundaries 四篇，README frontmatter 含 source/rule_snapshot/status flagged/stale_after/method 十字段，防画饼声明置顶）；父索引两处更新（index.md toctree 按字母序插入 + README.md 归档表）；
- 审查全程留痕 spec 区 path-review.md（每视角「发现→处理→残留风险」表 + 魔鬼代言人证伪记录 + 前三查结论）；
- R-1 口径差主代理裁决：**保留 bundle 08 不动**——其 L50 为机制层中性条件句（「若处于报名窗内则报名」），path-design §3.7 为执行层时点决策（主力按错失设计 + 48h 补位分支），二者非冲突；时效风险已由 bundle flagged + stale_after 2026-12-31 覆盖。R-2~R-4（活动窗复核/参与人数无信源/人类原创占比无官方细则）已在 docs 文档显性标注；
- 我方复核（Trust but verify）：docs 四文件 Glob 存在；13 处 V 修订标注实测；README frontmatter 与防画饼/时点三块提示齐备、收益表 11 行全挂 F 或待验证；README→bundle 相对链接 5 层上跳层级正确；competitive-analysis/index.md L78 toctree 字母序插入符合既有体例；bundle 零改动（R-1 按裁决未动）。

## Task 9: 机械门禁全量验证（V）

**Priority**: medium
**Status**: completed
**依赖**: Task 8
**映射 AC**: AC-5, AC-6, AC-7
**内容**: 执行 OKF 机械门禁（优先在 awesome-okf-xs 子项目内跑 `invoke gates.all`；依赖缺失时执行手动等效清单）：① UTF-8 strict roundtrip；② 双份 F 编号正则比对；③ 三级 toctree 条目逐一 Test-Path；④ 总索引三处计数核对；⑤ 全部相对链接可达 + 零 file:///；⑥ 敏感信息零残留。依赖缺失时在 bundle log.md 注明"手动等效验证"并逐项打勾，禁止谎报 gates。

- [x] Subtask 9.1: 跑 invoke gates.all（或手动等效六项清单）
- [x] Subtask 9.2: 失败项修复后复跑（迭代至全绿）

**Test Requirements**:
- TR-9.1 (rule): 六项机械门禁全过（gates 全绿或手动等效清单全勾且 log 注明）

**完成记录（2026-09-23）**: 子模块无 invoke 任务定义（`tasks.py` 不存在）→ 按 spec 约定走手动等效路线。
- 六项全绿（验证覆盖 bundle 14 + docs/ 4 + spec 区 8 共 29 个 .md）：UTF-8 strict 往返 29/29；F 集合 facts↔article-source 各 67 条相等且 F-001~F-067 连续；bundle toctree 13 条目 + docs toctree 3 条目逐一 Test-Path 存在；计数核对 total_bundles=565 / sheke「42 束 ×2」且 industry 19 束与实际目录 19 一致 / sheke 域 7 组 / sheke/index 17-19 双口径在 / industry 三处引用齐备；相对链接全可达 + `](file:///` 链接用法零命中；键值型敏感模式零命中；
- 验证中即时修复 1 处真实缺陷：spec 区 knowledge-map.md 互链清单 4 条断链（`../xxx` 在 spec 区不可达）→ 改三层上跳正确路径（`../../../projects/awesome-okf-xs/doc/bundles/sheke/industry/...`）后复跑通过；
- 三次脚本断言错位（toctree 13/14、industry 组路径、sheke 42×2 与 17 组口径）经读实际内容逐项核实为脚本判据错误而非产物缺陷，修正后全绿；
- bundle log.md 已按 TR-9.1 追加「Task 9 手动等效验证」六项打勾记录（含 invoke gates 不可用说明与知识图谱断链修复注记）。

## Task 10: 原子提交交付（C）

**Priority**: medium
**Status**: pending
**依赖**: Task 9
**映射 AC**: AC-11
**内容**: 按既定顺序提交：① awesome-okf-xs 子模块内提交（bundle 全文件 + 组 index + 总 index，显式列全文件）→ ② 主仓库提交 spec 区（.trae/specs/create-zhihu-monetization-okf-wiki/）→ ③ 主仓库提交 docs/ 变现路径 + 子模块指针更新。使用 `python .agents/scripts/git-commit-utf8.py -m "type(scope): 中文描述" <显式文件...>`；Conventional Commits；不 push；提交后 git log 验证顺序与内容。

- [ ] Subtask 10.1: 子模块内提交（bundle + 索引）
- [ ] Subtask 10.2: 主仓库 spec 区提交
- [ ] Subtask 10.3: 主仓库 docs/ 路径文档 + 子模块指针提交
- [ ] Subtask 10.4: git log 验证三笔提交顺序/内容；确认未 push

**Test Requirements**:
- TR-10.1 (rule): 三笔提交顺序正确、消息符合 Conventional Commits 中文规范；远端无新增提交

## Task Dependencies

```text
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 8 → Task 9 → Task 10
                         (Task 7 依赖 Task 5，可与 Task 6 并行) ──┘
```

- Task 6 与 Task 7 可并行（bundle 生成 ↔ 路径设计，互不写同一文件）；
- Task 8 需 Task 6（F 编号引用源）+ Task 7（设计稿）双前置；
- Task 10 依赖全部完成项；任一 blocked 则队列不算清空，不得进入 Review 阶段。

## Parallelizable Work

- Task 6（bundle 生成）与 Task 7（路径设计）在 Task 5 完成后即可并行派发；
- Task 3 的 WebSearch 核验可按 P0 声明分组并行（独立子代理，每组完整声明清单）。
