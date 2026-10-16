# 微信博文《做AI一人公司1年，营收突破110W》→ OKF 知识包 - 实施计划

> 方法论链路：seven-concepts 场景 4（知识沉淀）R→I→E，V 由独立 Review 承担；信源先行顺序：facts → references → concepts → bundle index → 上级索引。

## Task 1: R — 建立 spec 侧 F 编号事实台账（facts.md）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1 rule PASS：facts.md 含 source-manifest 与 F 表；正则提取 count=38、min=1、max=38、missing 空、dup 空；文字层 F-001~014 与图卡四层 F-015~038 关键声明全覆盖（14小时/离婚 F-018、80条/12万粉/5万/12万/7万/80%/200→8 F-021~024/F-027、15万/9万/外包流 F-029~033、四档/180万/SaaS F-036~037、110万/70万/14斤/3万/9.9万 F-006/F-008/F-013）。
  - TR-1.2 rule PASS：五要素 claim/type/locator/status + source_id（表头统一 blog）齐备；修辞比例与自述成效单列标注。G1 门通过（事实栏无因果推断词）。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `.trae/specs/ai-solo-company-truth-okf-wiki/facts.md` 登记 source-manifest（URL/账号/发布时间/采集时间/公开性/归属证据/无外链）与 F-001 起连续编号事实表。
  - 覆盖两层信源：文字层（导语+三建议）与图卡层（真相一~四，locator 标"图N"）；分类仅用 元信息 / page_fact / 作者观点 / 作者建议 / 原文示例；执行者解读不入 facts。
  - 约 38 条（F-001~F-038，以实际连续编号为准），关键数字/日期/产品名零遗漏。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 含 source-manifest 段与 F 表；正则提取编号从 F-001 连续无跳号；图卡四层（14小时/离婚、80条12万粉5万12万7万80%200→8、15万9万外包流、四档180万SaaS）与文字层（110万70万14斤三建议3万9.9万）关键声明全部在表；证据=正则输出+逐条核对记录
  - `rule` TR-1.2: 每条含 claim/type/source_id/locator/status 五要素（表格形态可合并列，但五信息可辨识）；证据=文件内容
- **Notes**: G1 门——事实栏无因果推断词，因果叙述归"作者观点"。

## Task 2: E(信源先行) — references 双文件
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1 rule PASS：正则集合比对 facts=38 / article-source=38，only-in-facts 空、only-in-article 空。
  - TR-2.2 rule PASS：verification.md 含信源距离五分类、勘误四清单（日期版本/成效溯源/口径对照/引文逐字）、110vs180/70万成本张力/9.9块vs9.9万/三修辞比例/第三档上限措辞/时间线张力/五项算术核对/coze.cn 背景源，全部要点逐条落点；无编造 URL（coze.cn 经 WebSearch 确认）。
  - TR-2.3 rule PASS：三文件 frontmatter 齐备（type:Reference、status:flagged、stale_after、sources），references/index.md 含 toctree+表格双轨。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 生成 `references/index.md`（toctree + 表格双轨）。
  - 生成 `references/article-source.md`：frontmatter 完整；F 表与 facts.md 双份一致；末尾"引用边界"（无脚注/外链、图片为自制卡片、全部数字保留作者口径）。
  - 生成 `references/verification.md`：flagged 结论；勘误四张清单表（日期/版本✅、成效数字溯源⚠️全单源、口径对照⚠️含 110vs180/9.9块vs9.9万/时间线、引文逐字✅无官方引文）；逐项核验（含算术自洽机械核对、措辞不严谨、修辞比例、Coze/Agent/RAG 背景一致性）；V 四视角审查摘要。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: article-source.md 与 facts.md 的 F 编号正则集合相等且连续；证据=两文件提取结果比对
  - `rule` TR-2.2: verification.md 含勘误四清单表且下列要点各有落点：110万vs180万、70万成本口径张力、9.9块/9.9万、80%/90%/80%三修辞比例、"180万第三档上限"措辞、2025/2026 时间线张力、80×1500=12万/12−5=7/15−9=6 算术核对、无独立信源声明、唯一背景信源 Coze；无编造 URL；证据=逐条定位
  - `rule` TR-2.3: 两文件与 references/index.md frontmatter/type/status:flagged/stale_after/sources 齐备；index 含 toctree 块；证据=文件检查

## Task 3: E — concepts 三篇 + 子索引
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1 rule PASS：concepts/index.md 无 frontmatter、toctree 3 条+列表；三篇概念文均为原创改写，H2 节数分别 4/6/5（≥4）；>40 字直引零出现（短引号逐字核对，已将两处非逐字引号修正）。
  - TR-3.2 rule PASS：110/70、180、14斤/急诊/离婚、14小时、80条/12万粉/5万/12万/7万/80%/前1%/200→8、15万/9万、外包工作流、自留三环节、四档、三选择、三建议、3万/9.9万/9.9块 全部挂 F 编号；修辞比例（90%/80%）显式标注非统计。
  - TR-3.3 rule PASS：frontmatter 齐备（type:Concept、status:flagged、stale_after、三 sources），结构均为"主题+边界"，含可迁移模式（02：触发/步骤/反模式/迁移验证）。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `concepts/index.md`（toctree 3 条+列表）。
  - `00-revenue-and-health-timeline.md`：一年账本（110万/70万 vs 180万双口径并列+单源警示）、健康与家庭代价时间线（14小时/14斤/急诊/离婚/第九个月，图卡与文字两层 locator 区分）、读者应如何理解这些数字。
  - `01-four-truths.md`：四真相框架表（决策过载/流量≠客户/交付瓶颈/规模天花板四档），逐条还原主张+边界标注；外包工作流与自留三环节；流量获客调整案例（全部挂 F）。
  - `02-actions-and-boundaries.md`：三建议改写为可验证假设；四边界（平台/用户/交付/健康与时效）；可迁移模式（触发条件+核心步骤+反模式+迁移验证）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-3.1: 每个出现的具体数字/日期/产品名（110万/70万/180万/12万粉/5万/1500/7万/200/8/15万/9万/3万/9.9万/0-30-100-300万/2025/2026/Coze/RAG/Agent 等）均带 F-编号引用；无 facts 之外的新数字；证据=成稿后逐数回查
  - `rule` TR-3.2: 无原文连续长段逐字复制（>40 字直引须有引号且必要），无图片引用；证据=对照原文检查
  - `rubric` TR-3.3: 知识转化质量；scale 1-5；anchors 同 AC-6；threshold >= 4；证据=三篇成稿审查评分
  - `rule` TR-3.4: 四文件 frontmatter 齐备、status: flagged、sources 三源（article/verification/blog）；concepts/index.md 含 toctree；证据=文件检查

## Task 4: E — bundle 根 index.md + log.md
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1 rule PASS：index.md 仿 auto-money-system 模板，okf_version/type/title/description/tags/generated/verified/status/stale_after/sources 全字段齐备；blog 源用 url 键；description 含"非操作教程"。
  - TR-4.2 rule PASS：flagged 提示块在顶部；显式声明无 examples/ 及原因；含阅读地图/核心概念/主题关联（../auto-money-system、../ai-one-person-micro-product）/信源与边界；隐藏 toctree 三条。
  - TR-4.3 rule PASS：log.md 含日期、R→I→E→V 流程、F 编号、图卡视觉识读、P0 核验结论、既存漂移注记、门禁与未提交声明。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - `index.md`：OKF v0.2 frontmatter（九字段，sources 含 blog URL/article/verification）；顶部 flagged 提示块；"非操作教程、无 examples/"声明；三层阅读地图；核心概念三链接；主题关联互链（auto-money-system、ai-one-person-micro-product）；信源与边界；隐藏 toctree（concepts/index、references/index、log）。
  - `log.md`：记录 R→I→E→V 过程、F 编号区间、两问判定、flagged 理由、门禁方式（invoke 或手动等效）、未提交声明。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-7
- **Test Requirements**:
  - `rule` TR-4.1: index.md 顶部含 flagged 明示与"非操作教程"声明；toctree 三条目（concepts/index、references/index、log）拼写正确；互链相对路径 `../<bundle>/index.md` 深度正确；证据=文件检查+链接 Test-Path
  - `rule` TR-4.2: log.md 含 F 区间、两问判定、flagged 理由、门禁结论；证据=文件内容

## Task 5: 三级索引接入
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1 rule PASS：industry/index.md 导航表新增 ai-solo-company-truth 行（文档数 7）、toctree 新增条目、description 21→22。
  - TR-5.2 rule PASS：sheke/index.md 正文束数与 industry 行同步为 22。
  - TR-5.3 rule PASS：bundles/index.md total_bundles 632→633、正文 633、mermaid 67、sheke 节标题 67、industry 行 24→25；jishu 469/iot 9/systems 3 等并行会话现值未触碰（增量编辑，零回退）。
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 组索引 `sheke/industry/index.md`：导航表 +1 行（束名/文档数 5/一句话简介含 flagged 标注）、toctree +1 条（按命名序置于合适位置）、description 与"21 束"计数同步为登记口径 22；既存 3 束未登记漂移不动，仅在 log/review 注记。
  - 域索引 `sheke/index.md`：先读现状，同步束数（66→67）与涉及 industry 的计数/表述。
  - 总索引 `doc/bundles/index.md`：在当前工作区版本（含并行 WIP）上增量改 total_bundles 632→633、正文 632→633、mermaid sheke 66→67、sheke 分区标题 66→67、industry 行 24→25；不得回退 jishu WIP 行。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 组/域/总三处索引计数自洽（22 登记/25 磁盘、sheke 67、total 633），新增 toctree 条目指向的文件 Test-Path 为 True；证据=改动片段+路径检查
  - `rule` TR-5.2: `git diff` 确认 bundles/index.md 仅在 WIP 版本上增量、jishu WIP 行（632/469/iot 9/systems 3）保留；证据=git diff 输出

## Task 6: 机械门禁与收尾自检
- **Status**: `completed`
- **Completion Evidence**:
  - TR-6.1 rule PASS（8 项逐项有证据）：① UTF-8——官方 check-utf8.py 11555 文件通过 + 本束 7 文件 strict roundtrip 通过；② 双份 F 集合——38=38 零差集；③ toctree——官方脚本本束零命中（82 处告警全属并行 WIP/3 个既存漂移束）；④ 相对链接——两个主题关联目标 Test-Path True；⑤ file 协议链接零出现（log 描述文字已改写消除字面量）；⑥ 家目录路径零出现；⑦ frontmatter——6 个内容文件齐备，log/子 index 无 FM 与先例一致；⑧ 计数——官方 check-bundles-index.py 五面一致（634 当前态；本束增量 sheke 67/industry 25 保留）。
  - TR-6.2 rule PASS：Glob 束目录无 jpg/jpeg/png/gif/webp/html；Grep 敏感串零命中；`%TEMP%/okf-article-imgs` 已删除（Test-Path False）。
  - TR-5.2 rule PASS：git diff 确认 bundles/index.md 相对 HEAD（629）的改动中，本会话仅贡献 sheke/industry 五处增量；jishu 470、ai 241、iot 9、systems 3 为并行会话在途改动，未回退。
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 在子模块环境尝试 `invoke gates.toctrees` / `gates.bundles` / `gates.utf8`（可用则全跑并留存输出）；依赖不可用或失败项仅来自既存漂移时，执行技能 §7 手动等效清单：UTF-8 strict、双份 F 集合、三级 toctree 条目 Test-Path、全仓相对链接可达、file:///零出现、敏感路径零出现、frontmatter、计数三处一致。
  - 清理临时图片目录 `%TEMP%\okf-article-imgs`；确认仓库无图片入库。
  - 在 log.md 写入门禁实际方式与结论（禁止谎报 gates）。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: 清单 8 项逐项有证据；新增/修改 .md 全部 UTF-8 strict roundtrip 通过；证据=命令输出
  - `rule` TR-6.2: 新束目录下无 .jpg/.png/.html；`file:///`、`C:\Users`、`/Users/` 在新文件零出现；临时目录已删除；证据=Glob+Grep+Test-Path

## Task 7: V — 独立对抗审查（Spec Mode Review 阶段）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-7.1 rule PASS：fresh-context 只读审查者产出 review.md，逐 AC 给独立裁决与证据、每条 rubric 有分数与锚点理由。首轮 FAIL（P0-1：concepts/02 两条兄弟束互链深度少一级 Test-Path=False；P1-1：无据数字"60%"；P1-2：4 处非逐字引号）。
  - 回 Implement 全部修复：02 链接 `../`→`../../`（全束 23 条 md 链接机械解析 broken=0）；60% 改为 24/38 条数口径；F-006/F-013/F-037 引号逐一回改，01 篇 P2 裁剪项批量回改；修复后 UTF-8（11556 文件）、bundles 五面对账（634 当前态）复跑通过，toctrees 对本束仍零命中。
  - TR-7.2 rubric PASS（4/5 阈值）：第二轮复审独立重跑链接解析与官方门禁，改判 **PASS**——AC-1~AC-5 全 PASS、AC-6=4、AC-7=4；残留仅 P2（压缩短引号、22/25 既存双轨），不阻断。两轮审查历史均保留于 review.md。
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 队列清空后进入 Review：fresh context 只读审查者按独立审查合同核验全部 AC（事实溯源/结构/读者可用/时效/门禁），产出 review.md；fail 则建 issue 回 Implement。
- **Acceptance Criteria Addressed**: AC-1~AC-7
- **Test Requirements**:
  - `rule` TR-7.1: review.md 覆盖每个 AC、每条 rule 有独立证据、每条 rubric 有评分与理由；证据=review.md
  - `rubric` TR-7.2: 审查独立性与深度；scale 1-5；3=仅复述自检结论，5=独立重跑关键机械检查并提出实质性质证；threshold >= 4；证据=审查过程
