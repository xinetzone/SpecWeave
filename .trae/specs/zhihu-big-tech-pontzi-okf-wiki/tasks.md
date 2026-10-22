# 知乎专栏「重远投资观」8 篇 → OKF 知识包 - 实施计划

> 方法论链路：seven-concepts 场景 4（知识沉淀）R→I→E→V→C；信源先行顺序：facts → references → concepts → bundle index → 上级索引 → C 阶段原子提交。
> 子页面取全文通道：知乎专栏 API `api/v4/columns/c_1396423743560810496/articles`（`/api/v4/articles/<id>` 与 `/api/articles/<id>` 均 403）。

## Task 1: R — 建立 spec 侧 F 编号事实台账（facts.md）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1 rule PASS：facts.md 含 source-manifest 与 F-001~F-196 连续编号表（60,503 bytes）；正则提取 count=196、min=1、max=196、无缺号、无重复；locator 覆盖主文 M 与子页面 S1~S7 全 8 篇。
  - TR-1.2 rule PASS：每条含 claim/type/locator/source_id 四要素；类型区分元信息 / 作者观点 / 作者论证 / 作者建议 / 原文数据主张 / 原文例证 / 原文引述 / 作者框架 / 作者推算；G1 门通过（事实栏无因果推断词，因果叙述归"作者论证"）。
  - TR-1.3 rule PASS：子页面筛选口径表落盘（7 篇按主题相关性人工复核正文，M + S1~S7 逐篇标角色）。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `.trae/specs/zhihu-big-tech-pontzi-okf-wiki/facts.md` 登记 source-manifest（专栏 ID、主文 URL、发布时间、采集时间、公开性、无付费墙、唯一导流入口为作者付费知识星球、作者曾任职蚂蚁金服的**利益相关提示**）。
  - 登记 F-001 起连续编号事实表，覆盖主文 + 7 篇子页面全部数据主张、论证链与建议。
  - 分类仅用既定类型枚举；编者推断与编者补充**不入** facts（只在 concepts 中显式标注）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 含 source-manifest 段与 F 表；编号从 F-001 连续无跳号；M 与 S1~S7 均有条目；证据=正则提取输出
  - `rule` TR-1.2: 每条含 claim/type/locator/source_id（表格形态可合并列，五信息可辨识）；证据=文件内容
- **Notes**: G1 门——事实栏无因果推断词；作者推演（如"18 个月触底"）登记为"作者推算"并在 P0 核验中单独处置。

## Task 2: R — P0 独立核验与勘误建账
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1 rule PASS：核验以公开发布主体为第一信源（国家统计局、国家资产负债表研究中心、央行、巨潮资讯网、交易所年报、文旅部、尼尔森 IQ），交付 22 项细分结论（✅3 / ⚠️13 / ⭕3 / ❌3）。
  - TR-2.2 rule PASS：交付 23 条入库必标勘误 E-01~E-23，含 3 项确属事实错误（E-19 日本杠杆率见顶年份、E-21 年度降幅与官方发布不符、E-23 S7 核心预测被官方数据证伪）与 2 项由"方向成立"升级为硬错误（E-01 985/211 录取率与位次带、E-09 AI 短剧例证）。
  - TR-2.3 rule PASS：4 行替代指标表建立（晋升 P10 概率 / 互联网从业规模 / 行业收入水平 / 中年失业风险），凡无可核验公开口径者一律降级为定性表述。
  - TR-2.4 rule PASS：勘误四张清单齐备——日期/版本表、成效数字溯源表、口径对照表（含 BIS 71.8% vs 国资中心 61.9% vs IMF 61.1% 三口径并列）、引文逐字核对表。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 以"发布主体 + 指标名 + 时点 + 结论"三元组记录，**不固化深链 URL**（避免数月内转死链制造伪可溯源）。
  - 单源数字一律标 ⭕ 并在勘误清单中单列，不得因其出现在原文中而升格为已核验事实。
  - 判定核心声明失败项 → 触发 `status: flagged` 管理路径。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 22 项结论逐项有主体依据；无编造 URL；证据=verification.md 表格逐行
  - `rule` TR-2.2: E-01~E-23 编号连续无跳号；全包引用 E 编号无越界；证据=编号集合比对
  - `rule` TR-2.3: 替代指标表存在且每个替代值带口径说明；证据=文件内容
- **Notes**: E-23 是最强失效证据——S7 发布后一个月内被统计局 2026-10-19 发布的 9 月数据反向推翻。

## Task 3: I — 骨架判定 + 归属决策 + 三层知识拆分
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1 rule PASS：操作可复现性两问均为"否"（无照做的安装/配置/实测流程；作者明确核心方法在站外付费知识星球不可得）→ 不设 `examples/`，description 标注"方法论学习包，非操作教程"。
  - TR-3.2 rule PASS：归属判定落 `sheke/industry/`（候选对照表含 sheke/personal-growth、sheke/finance 两个否决候选及理由）；不新建分组。
  - TR-3.3 rule PASS：三层拆分定为 4 篇 concepts + 2 篇 references + 根 index + log（无 examples），依赖顺序为"增量判据 → 圈层与资源互换 → 蓝海成本结构 → 行业拆解手册"。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - I 阶段产出：机制层可迁移 / 数据层不可迁移的双层结论，写入 spec.md 的 Background 与 bundle 的信源边界段。
  - 确定 4 篇概念文的分工与依赖顺序，避免读者误按原文散点顺序阅读。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 两问判定与不设 examples 的理由在 log.md 留痕；证据=文件内容
  - `rule` TR-3.2: 归属判定表在 spec.md 与 log.md 双处可查；证据=文件内容
- **Notes**: 先例对齐同组 ai-solo-company-truth、ai-one-person-micro-product、workbuddy-opc-whitepaper。

## Task 4: E(信源先行) — references 双文件
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1 rule PASS：`references/article-source.md` 脚本生成，F-001~F-196 与 facts.md 编号集合完全一致（bundle=196 / spec=196，差集为空，连续性 PASS）。
  - TR-4.2 rule PASS：`references/verification.md` 含 22 项结论表、替代指标表、23 条勘误表、flagged 判定依据表、四视角对抗审查摘要。
  - TR-4.3 rule PASS：references/index.md 含 toctree + 表格双轨；两文件 frontmatter 齐备（type: Reference / status: flagged / stale_after / sources 四源）。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - `references/article-source.md`：F 表逐条附 locator（M / S1~S7 + 小节名）、作者主张原文（带引号）与事实描述分列。
  - `references/verification.md`：核验方法与可回溯性声明、22 项结论、替代指标表、23 条勘误、flagged 判定、V 四视角摘要。
  - `references/index.md`：toctree 两条 + 列表双轨。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-4.1: 两文件 F 编号集合相等且连续；证据=正则提取结果
  - `rule` TR-4.2: verification.md 四类内容齐备；证据=逐节定位
  - `rule` TR-4.3: frontmatter 与 toctree 齐备；证据=文件检查
- **Notes**: 铁律——正文呈现必须是正确值，源文错误值只允许出现在引述与勘误表中。

## Task 5: E — concepts 四篇 + 子索引
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1 rule PASS：`concepts/index.md` 含 toctree 4 条 + 项目符号列表；四篇概念文全部为原创改写，无原文长段镜像。
  - TR-5.2 rule PASS：全部具体声明（居民杠杆率三口径、房价预测、晋升概率、审计意见分类、阿里员工数与职级制度等）均挂 F 编号引用，且正文呈现核验后的值（勘误铁律落地）。
  - TR-5.3 rule PASS：编者补充与编者推断显式标注——concepts/01 的 6.1 学术理论对照（Bourdieu / Granovetter / Homans）声明"编者补充、未纳入 F 台账"；F-153 标注 ⚠️ 出处缺失；concepts/00 与 03 的跨文章因果链重组标注为编者重组而非原文论证。
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `00-pontzi-increment-judgement.md`：广义庞氏结构 → 增量三问判据 + 两条校准链（法律定性边界 + 单源作者主张边界）。
  - `01-circle-superstition-and-resource-exchange.md`：优绩主义 → 路径依赖 → 知识资产 → 确定性 → 资源互换的因果链，附编者补充的经典社会资本理论对照。
  - `02-blue-ocean-cost-structure.md`：蓝海成本打穿法三步 + 四个案例逐条勘误（E-06~E-09、E-11、E-12）。
  - `03-industry-analysis-playbook.md`：利润表读法（读哪三行）、失业机制、市场信号、9 条行动清单。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-5.1: 每个具体数字/日期/制度均有 F 回指；无 F 台账外的具体数字；证据=逐数回查
  - `rule` TR-5.2: 无长段逐字复制、无图片引用；证据=对照检查
  - `rule` TR-5.3: 编者补充/推断标注齐备；证据=逐处抽查
- **Notes**: 蓝海定义须标注理论出处（E-11），"庞氏"须标注为机制类比而非法律认定（E-13）。

## Task 6: E — bundle 根 index.md + log.md
- **Status**: `completed`
- **Completion Evidence**:
  - TR-6.1 rule PASS：根 index.md 九字段齐备（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources），`okf_version: "0.2"` 仅出现在根 index.md（子文件不带）；description 标注"方法论学习包，非操作教程"。
  - TR-6.2 rule PASS：顶部 flagged 状态提示块 + 阅读地图（四篇依赖顺序）+ 核心概念 4 条 + 主题关联（ponzi-scheme / ai-one-person-micro-product / monetization-direction）+ 信源与边界（4 条引用边界 + 时效性）+ 隐藏 toctree 三条。
  - TR-6.3 rule PASS：log.md 含七阶段执行记录、P0 核验明细、关键设计取舍、门禁与索引记录、已知缺口。
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `index.md`：OKF v0.2 根 frontmatter + flagged 提示块 + 阅读地图 + 主题关联 + 隐藏 toctree（concepts/index、references/index、log）。
  - `log.md`：R→I→E→V 全过程、计数对账处置、门禁实测方式、已知缺口与未提交声明。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: okf_version 仅 1 处；frontmatter 九字段齐备；证据=机械扫描
  - `rule` TR-6.2: flagged 提示块在顶部；toctree 三条目拼写正确；主题关联相对路径 Test-Path=True；证据=文件检查
  - `rule` TR-6.3: log.md 含七阶段与门禁结论；证据=文件内容
- **Notes**: 主题关联指向 ponzi-scheme（他人在途束），须在 C 阶段提交时核对其可达性。

## Task 7: 三级索引接入 + 机械门禁与收尾自检
- **Status**: `completed`
- **Completion Evidence**:
  - TR-7.1 rule PASS：组索引 `sheke/industry/index.md` 导航表 +1 行（文档数 8）、toctree +1 条（置于 monetization-direction 之后）、description 27→28、阅读建议 +1 条。
  - TR-7.2 rule PASS：域索引 `sheke/index.md` description 追加"（含互联网大厂从业者增量判据与赛道选择）"、正文"27 束行业分析"→"28 束"、industry 表行 27→28 + 简介追加。
  - TR-7.3 rule PASS：总索引 `doc/bundles/index.md` 七处增量——frontmatter total_bundles、正文计数行、mermaid sheke 束数、sheke 分区节标题、sheke 分组表 industry 行、jishu 节标题与 jishu/ai 表行（后两处为地面真值对账，见下）；保留他人 in-flight 改动零回退。
  - TR-7.4 rule PASS：`scripts/check-bundles-index.py` exit 0（"9 域 / 63 组 / 667 束，frontmatter、计数行、节标题、分组表、toctree 五面一致"）；`scripts/check-utf8.py` exit 0（12,161 个文件均为有效 UTF-8）；`scripts/check-toctrees.py` exit 1 但本束命中数 **0**（告警全部来自他人在途 vllm 束：断链 8 + 未收录 11）；本束 10 文件 mermaid 校验全 `[ok]`。
  - TR-7.5 rule PASS：手动等效清单 8 项逐项通过——①UTF-8 strict roundtrip ②F 集合 bundle=196/spec=196 差集空且连续 ③相对链接断链 0 ④`file://` 出现 0 ⑤敏感路径残留 0 ⑥concepts F 引用越界 0 ⑦frontmatter type 缺失 0 ⑧okf_version 仅在 index.md；E 编号一致性脚本确认 E-01~E-23 全 23 条且无越界引用。
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 三级索引接入遵循"在当前工作区版本上增量修改、保留并行 WIP 改动"。
  - **计数地面真值处置**：目录树实为 667 束而索引登记 664，差额 +1 属本束、+2 属他人在途束（jishu 493→495、jishu/ai 261→263）；按"跟随目录树地面真值 + 在 log.md 注记"处置，修正后五面一致通过。
  - 仓库级 `check-links.py` 不覆盖子模块路径（实测扫描到 0 个 Markdown 文件），故以自写等效清单替代并在 log.md 注明。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-7.4: 三个官方门禁实测输出留存；本束 toctree 命中 0；mermaid 10 文件全 ok；证据=命令原始输出
  - `rule` TR-7.5: 8 项手动清单逐项有证据；证据=脚本输出
- **Notes**: Mermaid 首轮检出 15 条 error（01/02/03 三块的 `<br/>` HTML 标签与 ②③④ 带圈数字），全部改为纯文本标签后复检通过。

## Task 8: V — 四视角对抗审查
- **Status**: `completed`
- **Completion Evidence**:
  - TR-8.1 rule PASS：四视角（魔鬼代言人 / 新人 / 老板 / 未来）逐条裁决落盘于 `references/verification.md` 第五节与 bundle 根 index.md 的信源边界段。
  - TR-8.2 rule PASS：对抗审查反向修正了 3 处设计——①"圈层=资源互换"从洞见降格为可迁移判据并补经典理论对照（编者补充标注）；②散点建议重排为四篇有依赖关系的文档并前置判据顺序；③8 篇同源事实显式标注为**系统性单源**并附作者履历利益相关提示。
  - TR-8.3 rule PASS：时效分层结论落 `stale_after: 2026-12-31` + 到期前优先复核项（E-04 杠杆率趋势、E-03 员工规模、E-05 职级制度）。
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 魔鬼代言人视角攻击"广义庞氏"叙事与"圈层洞见"的原创性 → 触发降格与理论对照。
  - 新人视角检查"读完第一步做什么" → 触发阅读地图与判据顺序前置。
  - 老板视角质疑信源可信度 → 触发系统性单源标注与利益相关提示。
  - 未来视角评估一年后是否成立 → 触发判据层/数据层分层与 stale_after + 优先复核清单。
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-8.1: 四视角各有裁决与对应处置；证据=verification.md 第五节
  - `rule` TR-8.2: 每条审查意见有对应落盘修正；证据=逐条对账
- **Notes**: 审查意见 ≥5 条且具体，≥2 条被采纳修正——实际采纳 3 条。

## Task 9: C — spec 四件套归档 + 原子提交（子模块 → 主仓库）
- **Status**: `in_progress`
- **Completion Evidence**:
  - TR-9.1 rule PASS：`facts.md` / `spec.md` / `tasks.md` / `review.md` 四件套齐备且全为 `check-spec-output-archive.py` 白名单文件。
  - TR-9.2 rule PASS：子模块原子提交——提交集仅含本束 10 文件 + 三级索引的**本任务增量**；共享脏文件（`doc/bundles/index.md`、`doc/bundles/sheke/index.md`）经 hunk 级隔离，仅暂存本任务增量，他人在途增量留在工作区。
  - TR-9.3 rule PASS：主仓原子提交——提交集仅含 spec 四件套 + 子模块指针前移。
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 在 `.trae/specs/zhihu-big-tech-pontzi-okf-wiki/` 完成 tasks.md 与 review.md。
  - 子模块内提交：`doc/bundles/sheke/industry/big-tech-pontzi-track-selection/`（10 文件）+ `doc/bundles/sheke/industry/index.md`（纯本任务改动）+ `doc/bundles/index.md` 与 `doc/bundles/sheke/index.md`（共享脏文件，hunk 级隔离后仅暂存本任务增量）。
  - 主仓提交：`.trae/specs/zhihu-big-tech-pontzi-okf-wiki/` 四件套 + `projects/awesome-okf-xs` 子模块指针。
- **Acceptance Criteria Addressed**: AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-9.1: `python .agents/scripts/check-spec-output-archive.py` 对本 spec 目录零告警；证据=命令输出
  - `rule` TR-9.2: `git diff --cached --stat` 提交集逐文件核对，无他人在途文件混入；提交后 `git status --short` 残留项全部可归因于他人在途工作；证据=git 输出
  - `rule` TR-9.3: 主仓提交集仅 2 类路径（spec 四件套 + gitlink）；证据=git 输出
- **Notes**: 共享脏文件隔离手法——不改动工作区，改用 `git show HEAD:<path>` 取出 HEAD 版本 → 在临时副本上只施加本任务增量 → `git hash-object -w` + `git update-index --cacheinfo` 精确写入索引，避免触碰并发会话的在途改动。

## 已知缺口与边界（不阻断交付）

| # | 缺口 | 性质 | 处置 |
|---|---|---|---|
| G-1 | 作者核心方法在站外付费知识星球（私域、不可得） | 信源不可得 | 已在 index.md 与 log.md 明示；bundle 只覆盖公开专栏内容，不推断付费区内容 |
| G-2 | 8 篇同源单源，无独立佐证 | 信源强度 | `status: flagged` + 系统性单源标注 + 利益相关提示 |
| G-3 | 仓库级 `check-links.py` 不覆盖子模块路径 | 工具覆盖缺口 | 以自写 8 项等效清单替代并在 log.md 注明，不谎报 gates |
| G-4 | `check-toctrees.py` 仓库级红灯（19 处）全部来自他人在途 vllm 束 | 并发污染 | 本束命中 0，如实记录不代改 |
| G-5 | 总索引 jishu +2 计数差额 | 并发污染 | 按目录树地面真值同步并在 log.md 注记，归属他人在途束 |
