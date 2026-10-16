# 微信博文《做AI一人公司1年，营收突破110W》→ OKF 知识包 - 需求规格

## Overview

- **Summary**：按 `seven-concepts-cmd` 场景 4（知识沉淀 R→I→E→V）与 `blog-article-to-okf-wiki` 七阶段工作流，将微信公众号文章 https://mp.weixin.qq.com/s/21GT0M3k6lw_Mys1c8rjng 全面学习并转化为一个 OKF v0.2 bundle，落位于 `projects/awesome-okf-xs/doc/bundles/sheke/industry/ai-solo-company-truth/`，并完成三级索引接入与机械门禁验证。
- **Purpose**：把一篇高传播性的"AI 一人公司"个人自述复盘，转化为可溯源、观点/事实分层、带勘误与时效边界的学习教程；重点拦截"作者自述数字被误读为市场事实"和"源文内部口径冲突被静默照搬"两类风险。
- **Target Users**：OKF 文档库读者中关注 AI 变现/一人公司/自由职业的中文技术与商业学习者。

## Goals

- 完整登记文章两层内容（文字导语层 + 4 张"四个真相"图文卡片层）的全部事实、观点、建议，F 编号连续可溯源。
- 对全部 P0 声明（营收/到手/投入/亏损/粉丝/引流成本/合同金额/健康事件/时间线）完成信源距离判定与勘误四清单核验。
- 产出原创改写的概念教程（非全文镜像），沉淀可迁移模式与反模式。
- 按 OKF v0.2 规范完成 bundle 与三级索引（组索引、域索引、总索引）接入。

## Non-Goals

- 不复制/镜像原文全文与图片（版权与公开包纪律）；图片不入 bundle，仅以文字转述其承载的事实并标注 locator=图N。
- 不替作者"证实"任何收入数字，不做收益承诺式表达。
- 不新建分组；不顺手修复与本文无关的并行会话 WIP（jishu 域 3 个未跟踪束）与既存组索引漂移（industry 组 3 个已跟踪未登记束），仅在审查产物中如实注记。
- 不执行 git commit / push（遵循"未明确要求不提交"；完成后另行请示）。
- 不设 `examples/`（操作可复现性两问均为"否"，见下）。

## Background & Context

### 信源与公开性预检

- 公开文章（无登录/验证码/token，浏览器实测公开可访问），公众号"小鱼Python"，发布时间页面显示 **2026-10-13 17:52**，采集时间 2026-10-14。
- 账号主体 WebSearch 无公开权威资料可交叉（程序员客栈有一名"努力的小鱼Python"但无法确认同一主体）；文章发布仅 1 天，**全网无独立信源覆盖、无转载**。
- 文章无正文外链；底部有赞赏 DOM，无课程广告/二维码/付费入口。

### 内容形态与骨架判定（操作可复现性两问）

1. 有无读者可照做的安装/配置/代码/调用/实测流程？**否**（仅经营建议与个人叙事）。
2. 是否经作者实测、有版本/输入输出/步骤顺序可复现？**否**（个人经历不可复现，无数据佐证）。
→ **不设 examples/**；description 标注"商业分析，非操作教程"。先例：同组 auto-money-system、ai-one-person-micro-product。

### 两层内容结构（易漏点）

- **文字层**（约 650 字）：110 万营收/70 万到手、健康时间线（瘦 14 斤/第六个月急诊/第九个月想放弃）、三条建议（外包圈/高客单续单/服务标准化，3 万 vs 9.9 万）。
- **图卡层**（4 张 960×1280 图文卡，innerText 完全漏取，已逐张视觉识读）：真相一角色过载（六角色/每天 14 小时/第四个月妻子提离婚）；真相二流量≠客户（80 条视频/12 万粉/变现 5 万/投入 12 万/净亏 7 万/80% 来自前 1% 老粉/引流成本 200→8 元）；真相三交付瓶颈（15 万 AI 客服 SaaS 合同跳票/3 人团队报价 9 万/现行四类外包工作流）；真相四规模天花板（0-30/30-100/100-300/300 万+ 四档模型，"今年做到 180 万"，破 300 万三选择）。

### P0 核验关键结论（初判，R 阶段正式建账）

- **源文内部口径冲突（勘误重点）**：文字层"2025 年 all in、整整 12 个月营收刚破 110 万、到手约 70 万"与图卡四"我今年（2026）做到 180 万"并存，文章未做口径说明；标题把 110 万作为"做 1 年"招牌数字，读者极易误读。两数可按"2025 全年 vs 2026 截至 10 月"勉强分年调和，但无法证实，须双口径并列+单源标注。
- **全部财务/成效数字为作者自述、零独立信源**（信源距离=个人自述，比厂商自宣更弱）：110 万/70 万/180 万/12 万粉/5 万/12 万投入/7 万亏损/200→8 元/15 万/9 万/3 万/9.9 万/月入 10 万。
- **修辞性比例无统计来源**："避开 80% 的坑""90% 的人想简单了""80% 来自前 1% 老粉"。
- **算术自洽性机械核对（通过）**：80×1500=12 万；12 万投入−5 万变现=7 万净亏；15−9=6 万；100×1 万=10×10 万=100 万（对仗示例）。
- **措辞不严谨**："180 万在第三档上限"——第三档区间为 100–300 万，180 万非上限。
- **时间线张力**："2025 年 all in 做 12 个月"与"2026 年前半年 All in 抖音""做 1 年"标题，实际叙事跨度约 2 年。
- **同篇双 9.9 陷阱**：9.9 块（走量商品）vs 9.9 万（标准化产品），引用必须带单位语境。
- **背景技术名词外部一致性**：Coze（扣子，字节跳动 AI 智能体平台）、Agent、RAG 为真实技术概念 ✅（唯一可外部确认点，仅作背景信源）。
- 结论：核心声明（营收数字）不可核验且内部口径冲突 → 仿同组先例 `status: flagged`。

### 归属判定（候选对照表）

| 候选位置 | 判定 | 理由 |
|---|---|---|
| sheke/industry（AI 行业与商业趋势） | ✅ 采纳 | 主线实体=AI 一人公司创业/变现；该组已有 ai-monetization、auto-money-system、ai-one-person-micro-product、overseas-freelance-night-work 等同主题束，并有 3 篇"微信博文转化+flagged 单源"先例 |
| sheke/marketing | 否 | 仅"获客渠道"一个片段属营销，全文是创业经营复盘 |
| sheke/personal-growth | 否 | 非自我提升通识，是商业经营案例 |

单篇博文不新建分组；新束与 auto-money-system、ai-one-person-micro-product 建立"主题关联"互链。

### 计数基线（磁盘现值，2026-10-14 核实）

- `bundles/index.md` 工作区现值：total_bundles=632（HEAD 629 + 并行会话 3 个 jishu WIP 束）、sheke=66、industry=24。
- industry 组索引登记 21 束，磁盘实际 24 束（telecom-token-operation、telecom-ai-pilot-base、ling-3-1-flash-first-test 已提交但未登记，属既存漂移）。
- 本次新增后：total 633、sheke 67、industry 磁盘 25；组索引登记数 21→22（仅登记本束，不回填既存 3 束）。

## Functional Requirements

- **FR-1**：在 `doc/bundles/sheke/industry/ai-solo-company-truth/` 下生成 9 个文件：`index.md`、`log.md`、`concepts/{index,00-revenue-and-health-timeline,01-four-truths,02-actions-and-boundaries}.md`、`references/{index,article-source,verification}.md`。
- **FR-2**：spec 工作区生成 `facts.md`（F-001 起连续编号，约 38 条），与 bundle 内 `references/article-source.md` 双份编号集合一致；每条区分 元信息/page_fact/作者观点/作者建议/原文示例。
- **FR-3**：concepts 三篇覆盖：①一年账本双口径与健康家庭代价时间线；②四个真相框架（决策过载/流量获客/交付瓶颈/规模四档天花板）；③三条建议的假设化改写、四类边界、可迁移模式与反模式。
- **FR-4**：frontmatter 遵循 OKF v0.2（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources），sources 含博文 URL + article-source + verification（+Coze 背景信源仅用于技术名词背景）。
- **FR-5**：更新组索引 `sheke/industry/index.md`（导航表 +1 行、toctree +1 条、描述束数同步）、域索引 `sheke/index.md`（束数/计数同步）、总索引 `doc/bundles/index.md`（total_bundles、正文计数、mermaid sheke 束数、sheke 分区计数与 industry 行 24→25），均在当前工作区版本上增量修改，保留并行 WIP 改动。
- **FR-6**：全部具体声明（数字/日期/产品名/金额）在 concepts 中挂 F 编号引用；原文措辞只做短句必要引用并标注，正文为原创改写。

## Non-Functional Requirements

- **NFR-1（可溯源）**：读者能从任一数字回溯到 F 编号→article-source→博文 locator（文字层/图N）。
- **NFR-2（诚实边界）**：index 顶部 flagged 明示；作者自述、修辞、执行者洞察三者分层；不得出现"收益承诺/躺赚"式确定性语气。
- **NFR-3（规范一致）**：与同组先例束（尤其 auto-money-system）结构、frontmatter、语气一致；中文正文、英文 kebab-case 文件名。
- **NFR-4（门禁可过）**：toctree 三级完整无断头、相对链接全可达、UTF-8 无 BOM、无 `file:///` 与家目录路径；能跑 `invoke gates.*` 则跑，不可用则执行手动等效清单并在 log.md 注明，禁止谎报。

## Constraints

- **Technical**：产出在 git submodule `projects/awesome-okf-xs/` 内；Windows + PowerShell 7 环境；微信反爬确定（已用 browser_use 取证）；`invoke gates` 依赖（invocations 包）可能缺失。
- **Business**：OKF v0.2 规范与 Sphinx/MyST 构建兼容；公开包不得含全文镜像、原图、私域信息。
- **Dependencies**：同组先例束文件（已读）、子模块 AGENTS.md 与 frontmatter 规范、浏览器取证结果（含 4 图视觉识读记录，图片仅存于系统临时目录，不入库）。

## Assumptions

- 用户所说"恰当位置"授权按归属判定落入 sheke/industry；若用户希望改归 marketing 等他组，审批时纠正。
- 临时下载的 5 张图片仅用于识读，分析后从临时目录清理，不进入任何仓库。
- 时间戳生成标识使用 `reference_agent/okf-writer` 等先例同款 by 标识，at 取 2026-10-14。

## Acceptance Criteria

### AC-1：bundle 骨架与定位正确
- **Type**: `rule`
- **Given**：转化工作流完成
- **When**：检查 `doc/bundles/sheke/industry/ai-solo-company-truth/`
- **Then**：9 个规定文件全部存在，无 `examples/` 目录；index.md 含 concepts/index、references/index、log 的隐藏 toctree；两个子目录 index.md 各含 toctree 块
- **Pass Condition**：逐文件 Test-Path 全 True，目录树与 FR-1 清单逐一对应
- **Evidence**：文件清单截图/Glob 输出 + 各 index.md toctree 文本

### AC-2：F 编号双份一致、事实观点分层
- **Type**: `rule`
- **Given**：facts.md 与 article-source.md 已生成
- **When**：用正则 `^\|\s*F-(\d{3})\s*\|` 分别提取两文件编号集合
- **Then**：两集合相等、从 F-001 连续无跳号（若跳号须有显式注记）；每条含分类列且覆盖文字层与图卡 1–4 全部关键声明；concepts 中出现的每个具体数字/日期/产品名都能回指某 F 编号
- **Pass Condition**：集合比对相等；F 覆盖检查无未登记的具体声明
- **Evidence**：正则提取结果、编号比对结论、concepts 引用抽查记录

### AC-3：P0 核验与勘误完整、flagged 管理到位
- **Type**: `rule`
- **Given**：verification.md 与各文件 frontmatter 已生成
- **When**：审查核验产物
- **Then**：含勘误四张清单（日期/版本、成效数字溯源、口径对照、引文逐字）；110 万 vs 180 万口径冲突、9.9 块/9.9 万、修辞性比例、"180 万第三档上限"措辞、时间线张力均被登记；算术自洽核对有记录；无编造的权威 URL；bundle 与全部子文档 `status: flagged`，index.md 顶部有 flagged 提示块
- **Pass Condition**：上述每个点在 verification.md 中有对应行；frontmatter 逐文件检查一致
- **Evidence**：verification.md 内容、frontmatter 检查记录

### AC-4：原创改写与版权安全
- **Type**: `rule`
- **Given**：bundle 全部 .md
- **When**：与原文对照检查
- **Then**：无全文或长段逐字复制（仅保留带引号/标注的短句）；无原文图片文件入库；无私域/家目录路径；无全文 raw HTML
- **Pass Condition**：逐篇人工对照无违规；仓库新增文件中无 .jpg/.png
- **Evidence**：文件类型清单、对照审查记录

### AC-5：三级索引与机械门禁
- **Type**: `rule`
- **Given**：bundle 与索引修改完成
- **When**：执行 toctree/链接/UTF-8/计数检查
- **Then**：industry 组索引表格与 toctree 各 +1 且条目可达；bundles 总索引 total=633、正文 633、sheke 67（mermaid+分区标题+表）、industry 行 25；sheke 域索引计数同步；全部相对链接 Test-Path 可达、无 file:///、UTF-8 strict roundtrip 无乱码；既存 3 束未登记漂移被注记而非误改
- **Pass Condition**：手动等效清单逐项通过（或 invoke gates 通过且输出留存）；计数三处一致
- **Evidence**：检查命令输出、log.md 门禁记录

### AC-6：知识转化质量
- **Type**: `rubric`
- **Dimension**：教程的洞察深度、可迁移性与读者可用性
- **Scale**: 1-5
- **Anchors**: 1 = 摘抄改写、观点当事实、无边界；3 = 事实分层正确但洞察停留在复述；5 = 事实/作者观点/执行者洞察三分，四真相框架结构清晰，建议被改写为可验证假设，含触发条件+核心步骤+反模式+迁移验证的可迁移模式，读者能据此做出更优决策且不会误读为收益承诺
- **Pass Threshold**: >= 4
- **Evidence**：concepts 三篇成稿 + 独立审查评分

### AC-7：OKF 规范符合度
- **Type**: `rubric`
- **Dimension**: 与 OKF v0.2 规范及同组先例的一致性
- **Scale**: 1-5
- **Anchors**: 1 = 缺 frontmatter 字段/结构混乱；3 = 字段齐备但体例与先例有明显参差；5 = frontmatter 九字段齐备且取值合理、toctree/表格双轨、stale_after 与互链符合先例惯例、读感与 auto-money-system 等成熟束一致
- **Pass Threshold**: >= 4
- **Evidence**：frontmatter 逐文件核对 + 与先例对照记录

## Open Questions

- [ ] 束名 `ai-solo-company-truth`、概念篇命名是否认可？（审批时可改）
- [ ] 既存漂移：industry 组 3 个已提交未登记束（telecom×2、ling）是否需要本次一并补登记？默认**不处理**（超范围且需准确撰写 3 束简介）。
- [ ] 完成后是否需要在子模块与主仓库执行原子提交？默认**不提交**。
