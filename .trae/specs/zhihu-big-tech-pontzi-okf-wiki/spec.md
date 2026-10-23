# 知乎专栏「重远投资观」8 篇 → OKF 知识包 - 需求规格

## Overview

- **Summary**：按 `seven-concepts-cmd` 场景 4（知识沉淀 R→I→E→V→C）与 `blog-article-to-okf-wiki` 七阶段工作流，把知乎专栏「重远投资观」主文 https://zhuanlan.zhihu.com/p/2070094718520898598 及其 7 篇主题相关子页面全面学习，转化为一个 OKF v0.2 bundle，落位于 `projects/awesome-okf-xs/doc/bundles/sheke/industry/big-tech-pontzi-track-selection/`，并完成三级索引接入与机械门禁验证。
- **Purpose**：把这组"互联网大厂从业者职业/赛道选择"的高传播单源论述，转化为可溯源、事实/观点分层、带勘误与失效边界的学习教程；重点拦截四类风险——①"广义庞氏"被当成法律定性；②已被官方数据证伪的房价预测被照搬；③跨口径的杠杆率推演被当成结论；④"圈层=资源互换"这类通用常识被当成作者原创洞见。
- **Target Users**：OKF 文档库读者中关注大厂就业、职场圈层、行业选择与个人杠杆决策的中文学习者。

## Goals

- 完整登记主文 + 7 篇子页面的全部事实、观点、论证与建议，F 编号连续可溯源（locator 标 M / S1~S7）。
- 对全部 P0 声明（居民杠杆率、房价走势、晋升概率、裁员规模、审计意见分类、理论归属等）完成独立权威核验并建勘误清单。
- 产出原创改写的概念教程（非全文镜像），沉淀可迁移判据与失效条件。
- 按 OKF v0.2 规范完成 bundle 与三级索引（组索引、域索引、总索引）接入。

## Non-Goals

- 不复制/镜像原文全文与图片；不入库原图、私域信息、作者付费社区（知识星球）内容。
- 不替作者"证实"任何数字，不把"广义庞氏"写成法律定性，不产出投资/择业建议。
- 不新建分组；不顺手修复与本文无关的并行会话 WIP（jishu 域 vllm 等未跟踪束）内容，仅在审查产物中如实注记。
- 不设 `examples/`（操作可复现性两问均为"否"，见下）。
- 不执行 git push；提交范围与时机另行请示。

## Background & Context

### 信源与公开性预检

- 知乎专栏「重远投资观」（专栏 ID `c_1396423743560810496`，作者类型 `people`，署名「重远投资观」），主文发布 2026-08-10 10:31，采集时间 2026-10-22。
- 公开可访问，无付费墙、无正文外链；唯一导流入口为作者自有的付费知识星球。
- **取全文方式**：专栏 API `api/v4/columns/c_1396423743560810496/articles` 分页 13 次取回全部 236 篇，item 内含完整 `content` HTML 字段；`/api/v4/articles/<id>` 与 `/api/articles/<id>` 均 403，故以专栏 API 为唯一全文通道。
- 主文互动量：赞同 2257 / 评论 63（采集时点）。
- 作者早期署名「重远投资观」，文中多处自述曾任职蚂蚁金服 → 记为**利益相关提示**。

### 子页面筛选口径

从 236 篇中按主题相关性筛出 7 篇子页面，逐篇人工复核正文：

| 编号 | 主题 | 角色 |
|---|---|---|
| S1 | 利润表解析 | 方法（读表路径） |
| S2 | 职场奋斗到终点 | 职业收益上限 |
| S3 | 名校毕业中产沦为牛马 | 知识资产命中率 |
| S4 | 一夜返贫的名校毕业中产 | 优秀人设与确定性规则 |
| S5 | 裁员正在失控 | 失业机制与市场信号 |
| S6 | 拐点信号 / 房价走向 | 杠杆率触底 |
| S7 | 中产债务链条失控 | 二阶导与核心预测 |

### 内容形态与骨架判定（操作可复现性两问）

1. 有无读者可照做的安装/配置/代码/调用/实测流程？**否**（论述与判断，无操作步骤）。
2. 是否经作者实测、有版本/输入输出/步骤顺序可复现？**否**；作者明确声明核心方法在站外付费知识星球（不可得）。
→ **不设 examples/**；description 标注"方法论学习包，非操作教程"。先例：同组 ai-solo-company-truth、ai-one-person-micro-product、workbuddy-opc-whitepaper。

### P0 核验关键结论（R 阶段正式建账）

- **系统性单源**：8 篇全部为同一作者的连续输出，机制层可迁移、数据层不可迁移。
- **3 项确属事实错误**：E-19（日本家庭部门杠杆率见顶年份，1999/2000 约 71%，1991 年是股价房价见顶年）、E-21（年度降幅与官方发布不符：2024 年末 61.4% → 2025 年末 59.4%，非 61.1%→57.7%）、E-23（S7 核心预测被官方数据证伪：统计局 2026-10-19 发布的 9 月数据，一线二手住宅环比 +0.2%、连续 7 个月环比上涨）。
- **2 项升级为硬错误**：E-01（985/211 录取率与位次带）、E-09（AI 短剧例证）。
- **口径失配 13 项**：居民杠杆率 BIS / 国资中心 / IMF 三口径（E-16、E-20）、蓝海理论归属（E-11）、作者原创判据归属（E-12）、"广义庞氏"法律定性边界（E-13）、审计意见「准则四类」vs「证监会五类」（E-22）等。
- 结论：核心声明存在失败项 → 采 `status: flagged`，`stale_after: 2026-12-31`。

### 归属判定（候选对照表）

| 候选位置 | 判定 | 理由 |
|---|---|---|
| sheke/industry（AI 行业与商业趋势） | ✅ 采纳 | 主线实体=大厂从业者的职业/赛道选择；该组已有 monetization-direction、ai-solo-company-truth、workbuddy-opc-whitepaper 等同主题束，且有"外部博文转化+flagged 单源"先例 |
| sheke/personal-growth | 否 | 非自我提升通识，是职业与行业决策框架 |
| sheke/finance | 否 | 主文虽有杠杆率与房价链，但落点是职业选择；且与既有 ponzi-scheme 束建立主题关联而非并入 |

单篇专栏不新建分组；新束与 ponzi-scheme（法律意义的庞氏骗局）、ai-one-person-micro-product、monetization-direction 建立"主题关联"互链。

### 计数基线（磁盘现值，2026-10-22 核实）

- `bundles/index.md` 工作区现值：total_bundles=664、sheke=73、jishu=493、jishu/ai=261。
- 目录树地面真值（按 `check-bundles-index.py` 递归口径）：667 束 / 63 组 / 9 域；jishu 实为 495、jishu/ai 实为 263——差额来自并行会话已落地未登记的 in-flight 束。
- 本次新增后：total 667、sheke 74、industry 28。

## Functional Requirements

- **FR-1**：在 `doc/bundles/sheke/industry/big-tech-pontzi-track-selection/` 下生成 10 个文件：`index.md`、`log.md`、`concepts/{index,00-pontzi-increment-judgement,01-circle-superstition-and-resource-exchange,02-blue-ocean-cost-structure,03-industry-analysis-playbook}.md`、`references/{index,article-source,verification}.md`；不建 `examples/`。
- **FR-2**：spec 工作区生成 `facts.md`（F-001~F-196 连续），与 bundle 内 `references/article-source.md` 双份编号集合一致；每条区分元信息/作者观点/作者论证/作者建议/原文数据主张/原文例证/原文引述/作者框架/作者推算等类型。
- **FR-3**：concepts 四篇覆盖：①增量三问判据与两条校准链；②优绩主义→路径依赖→知识资产→确定性→资源互换的因果链；③蓝海成本打穿法与四个案例的逐条勘误；④利润表读法、失业机制、市场信号与 9 条行动清单。
- **FR-4**：frontmatter 遵循 OKF v0.2（`okf_version` 仅出现在 bundle 根 `index.md`；`type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`stale_after`/`sources` 齐备）。
- **FR-5**：更新组索引 `sheke/industry/index.md`（导航表 +1 行、toctree +1 条、描述束数 27→28）、域索引 `sheke/index.md`（industry 行 27→28）、总索引 `doc/bundles/index.md`（total_bundles、正文计数行、mermaid sheke 束数、sheke 分区标题与表、industry 表行），均在当前工作区版本上增量修改，保留并行 WIP 改动。
- **FR-6**：全部具体声明（数字/日期/制度/口径）在 concepts 中挂 F 编号引用；正文呈现**核验后的值**，源文原值只出现在引述与勘误表中。
- **FR-7**：编者推断与编者补充（学术理论对照、跨文章因果链重组）必须显式标注，不得混入原文主张。

## Non-Functional Requirements

- **NFR-1（可溯源）**：读者能从任一数字回溯到 F 编号 → article-source → 原文 locator（M/S1~S7 + 小节名）。
- **NFR-2（诚实边界）**：index 顶部 flagged 明示；作者主张/核验结论/编者补充三层分离；不得出现"必赚/稳赚/赶快上车"式确定性语气。
- **NFR-3（规范一致）**：与同组先例束结构、frontmatter、语气一致；中文正文、英文 kebab-case 文件名；Mermaid 代码块遵守仓库安全编码规则（无 `<br/>`、无带圈数字）。
- **NFR-4（门禁可过）**：toctree 三级完整无断头、相对链接全可达、UTF-8 无 BOM、无 `file:///` 与家目录路径；`scripts/check-utf8.py`、`scripts/check-bundles-index.py`、`scripts/check-toctrees.py` 与 mermaid 检查均须实测，禁止谎报。

## Constraints

- **Technical**：产出在 git submodule `projects/awesome-okf-xs/` 内；Windows + PowerShell 环境；仓库级 `check-links.py` 不覆盖子模块路径（实测扫描到 0 个文件），须以自写等效清单替代并注明。
- **Business**：OKF v0.2 规范与 Sphinx/MyST 构建兼容；公开包不得含全文镜像、原图、私域信息。
- **Dependencies**：同组先例束（已读）、子模块 `scripts/check-*.py` 三个门禁、主仓 `.agents/scripts/check-mermaid.py` 及其 `lib.checks.mermaid` 校验器。

## Assumptions

- 用户所说"恰当位置"授权按归属判定落入 `sheke/industry/`；束名 `big-tech-pontzi-track-selection`（若用户更名，审批时纠正）。
- 采集时的文章元信息（字数、互动量、专栏文章总数）为时点快照，`stale_after` 覆盖。
- 时间戳生成标识沿用先例同款 `reference_agent/okf-writer` / `reference_agent/zhihu-column-api` / `reference_agent/p0-verifier`，at 取 2026-10-22。

## Acceptance Criteria

### AC-1：bundle 骨架与定位正确
- **Type**: `rule`
- **Given**：转化工作流完成
- **When**：检查 `doc/bundles/sheke/industry/big-tech-pontzi-track-selection/`
- **Then**：10 个规定文件全部存在，无 `examples/` 目录；根 index.md 含 `concepts/index`、`references/index`、`log` 的隐藏 toctree；两个子目录 index.md 各含 toctree 块；`okf_version` 仅出现在根 index.md
- **Pass Condition**：逐文件存在性检查全 True，目录树与 FR-1 清单逐一对应
- **Evidence**：文件清单 + 各 index.md toctree 文本

### AC-2：F 编号双份一致、事实观点分层
- **Type**: `rule`
- **Given**：facts.md 与 article-source.md 已生成
- **When**：用正则 `^\|\s*F-(\d{3})\s*\|` 分别提取两文件编号集合
- **Then**：两集合相等、从 F-001 连续无跳号；每条含分类列；concepts 中出现的每个 F 编号都在域内
- **Pass Condition**：集合比对相等且差集为空；concepts 引用越界数为 0
- **Evidence**：正则提取结果与差集结论

### AC-3：P0 核验与勘误完整、flagged 管理到位
- **Type**: `rule`
- **Given**：verification.md 与各文件 frontmatter 已生成
- **When**：审查核验产物
- **Then**：22 项结论、23 条勘误齐备；3 项事实错误与 2 项升级硬错误均有官方依据；替代指标表存在；bundle 与全部子文档 `status: flagged`，index.md 顶部有 flagged 提示块
- **Pass Condition**：上述每个点在 verification.md 中有对应行；frontmatter 逐文件一致
- **Evidence**：verification.md 内容、frontmatter 检查记录

### AC-4：原创改写与版权安全
- **Type**: `rule`
- **Given**：bundle 全部 .md
- **When**：与原文对照检查
- **Then**：无全文或长段逐字复制（仅保留带引号/标注的短句）；无原文图片文件入库；无私域/家目录路径；编者补充与编者推断已显式标注
- **Pass Condition**：逐篇人工对照无违规；新增文件中无 .jpg/.png；编者标注齐备
- **Evidence**：文件类型清单、编者标注抽查记录

### AC-5：三级索引与机械门禁
- **Type**: `rule`
- **Given**：bundle 与索引修改完成
- **When**：执行 toctree/链接/UTF-8/计数/mermaid 检查
- **Then**：industry 组索引表格与 toctree 各 +1 且条目可达；总索引 total=667、正文 667、sheke 74（mermaid + 分区标题 + 表）、industry 行 28；sheke 域索引计数同步；全部相对链接可达、无 file:///、UTF-8 strict roundtrip 通过；Mermaid 代码块无 `<br/>`、无带圈数字
- **Pass Condition**：逐项检查通过；仓库级 toctree 门禁中本束命中数为 0
- **Evidence**：检查命令原始输出、log.md 门禁记录

### AC-6：知识转化质量
- **Type**: `rubric`
- **Dimension**：教程的洞察深度、可迁移性与读者可用性
- **Scale**: 1-5
- **Anchors**: 1 = 摘抄改写、观点当事实、无边界；3 = 事实分层正确但洞察停留在复述；5 = 事实/作者观点/编者推断三分，判据可操作（增量→成本结构→圈层），含失效条件与不可迁移边界，读者能据此做出更优决策且不会误读为投资建议
- **Pass Threshold**: >= 4
- **Evidence**：concepts 四篇成稿 + 独立审查评分

### AC-7：OKF 规范符合度
- **Type**: `rubric`
- **Dimension**：与 OKF v0.2 规范及同组先例的一致性
- **Scale**: 1-5
- **Anchors**: 1 = 缺 frontmatter 字段/结构混乱；3 = 字段齐备但体例与先例有明显参差；5 = frontmatter 九字段齐备且取值合理、toctree/表格双轨、stale_after 与互链符合先例惯例、读感与同组成熟束一致
- **Pass Threshold**: >= 4
- **Evidence**：frontmatter 逐文件核对 + 与先例对照记录

## Open Questions

- [ ] 束名 `big-tech-pontzi-track-selection` 与四篇概念命名是否认可？（审批时可改）
- [ ] jishu 域 +2 计数差额（另一会话 in-flight 束）本次按目录树地面真值同步到总索引（493→495、261→263），是否认可此处置？
- [ ] 完成后是否执行原子提交（子模块 → 主仓库）？默认**不提交**，待明确指令。
