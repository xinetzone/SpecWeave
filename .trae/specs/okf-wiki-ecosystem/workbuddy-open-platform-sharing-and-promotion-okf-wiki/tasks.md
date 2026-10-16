# WorkBuddy 开放平台两篇平台公告 → OKF Wiki 知识包 - 实施计划

> 任务顺序遵循信源先行：采集台账 → 事实与核验 → concepts → examples → 根索引/log → 索引接入 → 机械门禁 → 独立评审。所有计数以实施时机械真值为准。

## Task 1: 公告正文采集与页级覆盖登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 复核 A1/A2 两篇公告正文（本次已在受控浏览器已登录会话中取得完整正文，实施时须在核验时点重新读取一次并记录），逐条登记公告标题、发布/更新时间、栏目、完整正文要点、正文中出现的链接清单。
  - 采集平台导航面：`https://open.workbuddy.cn/`、`/dashboard` 可达性；从公告页侧边栏提取平台模块地图（14 项：Buddy 应用 / 专家 / 技能 / 连接器 / 硬件接入 / 分享功能接入 / 积分兑换 / 推广管理 / 数据概览 / 推广效果 / 收入变现 / 认证信息 / 开发者信息），逐项登记路径并标注「本次未采集，仅登记入口」。
  - 正文提取不足时记「未取得」并说明；不以标题或导航推断正文内容。
  - 产出 spec 目录 `facts.md`（R 阶段事实清单草稿）与 `references/source-manifest.md`（含 A1/A2/N1/N2 + 模块地图台账 + 集合比对结论）。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: A1、A2 两页均有完整正文记录；`source-manifest.md` 声明的页面集合与已处理集合双向差集为空；两页的发布日期、栏目、版本要求（5.8.0）在台账中逐项可核。
  - `rule` TR-1.2: 每页记录含 URL、访问日期、标题、正文解析状态、知识归属（指向具体 concepts/examples 文件名）、覆盖状态六要素；模块地图逐行含路径与「本次未采集，仅登记入口」标注。
  - `rubric` TR-1.3: 采集深度与证据质量；scale 1-5；anchors 1=只登记 URL 不记内容/3=有要点但折叠与链接清单缺失未说明/5=逐页有可核对要点，正文与链接清单完整，未采集模块逐条标注并给出补救方式；threshold >= 4；evidence 为 source-manifest.md 通读。
- **Notes**: 页面为 SPA 且需登录会话——读取走受控浏览器 `document.body.innerText`；不得点击任何提交/申请/购买类按钮。本任务只写 references 与 spec `facts.md`，不动其他束。
- **Completion Evidence**（2026-10-15）：A1（分享能力接入）、A2（推广管理）两篇公告于 2026-10-15 在受控浏览器**已登录会话**中读取渲染后**完整正文**（非摘要、非截断），逐页登记标题、发布日期 2026-10-14、栏目（平台公告）、正文要点与链接清单（各 15 条平台导航链接）；平台入口 N1（`https://open.workbuddy.cn/`）与首页 N2（`/dashboard`）登记为可达；平台模块地图 13 个模块逐行登记路径并标注「本次未采集，仅登记入口」。产出 spec `facts.md` 与 `<束>/references/source-manifest.md`（页级台账六要素 + 模块地图 + 集合比对结论「已声明页面集合 = 已处理集合，双向差集为空」）。TR-1.1/1.2/1.3 自验通过。本阶段未创建 `index.md`/`log.md`/`concepts/`/`examples/`，未改动同组既有束。

## Task 2: 事实编号、口径分层与核验
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 以 `facts.md` 为源，登记 `F-001` 起编号事实（自本束起编，不与他束编号体系混合）；覆盖：平台定位与模块地图、分享能力接入（能力范围、接入四步、审核与密钥、用户使用流程、版本要求、开放对象、支持范围、品牌规范）、推广管理（入口、配置、管理、用户使用、效果查看、资产类型与付费边界）、口径落差与时效项。
  - 产出 `references/article-source.md`：来源代号表（A1/A2/N1/N2 + 官方入口指引）+ F 编号事实表（每条含声明摘要、来源代号、核验状态）。
  - 产出 `references/verification.md`：核验总表（公告日期 2026-10-14、版本门槛 5.8.0、与 `workbuddy-official-docs` 束版本线 5.7.7 的落差）、勘误清单、**五类口径分层并列登记表**、信源距离评估（厂商单源）、V 四视角对抗审查表、status 裁决节。
  - 产出 `references/index.md`（无 frontmatter，toctree 收三件）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-2.1: `article-source.md` 的 `^\|\s*F-\d{3}\s*\|` 表行与 `facts.md` 的 `F-\d{3}` 集合机械比对相等、连续无跳号无重复；来源代号表覆盖 A1/A2/N1/N2 全部实际引用来源。
  - `rule` TR-2.2: `verification.md` 五类口径逐项有独立小节或表格行——①公告口径 vs 平台现状（明确列出公告未给出的接口级信息清单）；②端边界（PC 已支持 / 移动端规划态原话）；③资产类型与付费边界（专家/技能、连接器、Buddy 应用；免费 vs 付费）；④版本时效与落差（2026-10-14 / 5.8.0 vs 5.7.7）；⑤开放对象与企业认证门槛。
  - `rule` TR-2.3: 信源全部为实际读取成功的 URL；未取得的模块标「仅登记入口」不编造能力细节；不得出现「已 GA / 已全量」类替官方宣布表述。
  - `rubric` TR-2.4: 核验结论可辩论性；scale 1-5；anchors 1=只给结论不给证据/3=有证据但口径混写/5=每条结论挂信源与状态标签、不利证据（公告先行的版本落差、公告未给接口细节）显式呈现；threshold >= 4；evidence 为独立评审通读。
- **Notes**: 若公告与产品文档口径冲突，按「并列表述、不互相替换」处理，与同组 `wecom-5-0-12-release`、`workbuddy-official-docs` 的口径分层先例一致。
- **Completion Evidence**（2026-10-15）：`references/article-source.md` 建成（来源代号表 A1/A2/N1/N2 + 官方入口指引；F 编号事实表 64 行）。**机械比对（主会话复验）**：`facts.md` 与 `article-source.md` 的唯一 `F-\d{3}` 集合均为 **64**、`Compare-Object` 差集为 0、连续无跳号（F-001 → F-064）、无重复。`references/verification.md` 建成，含核验总表、勘误清单（无）、**五类口径分层并列登记表**（①公告口径 vs 平台现状 L46、②端边界 L60、③资产与付费边界 L69、④版本时效与落差 5.8.0 vs 5.7.7 L81、⑤开放对象与企业认证门槛 L93）、信源距离评估（厂商单源）、V 四视角对抗审查表、status `stable` 裁决。`references/index.md` 无 frontmatter，`{toctree}` 收三件且三文件均存在。TR-2.1/2.2/2.3/2.4 自验通过。跨束引用按「该束事实 081/082/042 号」表述，未污染本束 `F-\d{3}` 编号集合。

## Task 3: concepts 四篇 + concepts/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 产出 `concepts/00-open-platform-overview.md`、`01-share-capability-integration.md`、`02-promotion-management.md`、`03-boundaries-versions-and-policy.md` 共 4 篇，每篇回答一个明确问题，所有日期、版本号、模块路径、资产类型与数量声明均挂 F 编号。
  - `01` 篇含分享能力接入链路 Mermaid（flowchart：第三方应用 → 开放平台注册/审核/密钥 → 用户分享 → 唤起 WorkBuddy 客户端 → 内容预填会话框）；或 `02` 篇含推广入口生命周期 Mermaid（flowchart：资产 → 生成入口 → 渠道投放 → 用户到达详情页 → 安装量归因）。至少 1 张 Mermaid。
  - `00` 篇含平台模块地图表（14 项，逐项标注覆盖状态）。
  - `concepts/index.md`：toctree 收 00～03，并给一句话导读表。
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 4 篇文件全部存在，每篇 frontmatter 完整（`type`=Concept、`sources` 只列该篇实际引用信源、`generated`/`verified`/`status`/`stale_after` 齐备）；Grep 抽查关键声明（5.8.0、2026-10-14、模块路径、资产类型名）均带 F 引用。
  - `rule` TR-3.2: 至少 1 张 Mermaid 图存在且节点内挂 F 依据；五类口径标签（公告口径/平台现状/端边界/资产与付费边界/版本时效/开放门槛）在各篇至少合计出现且与 facts.md 状态一致。
  - `rubric` TR-3.3: 分层清晰度（对应 AC-6）；scale 1-5；anchors 1=按公告顺序平铺翻译/3=有分层但层间重复或跨篇跳转不清/5=每篇回答一个明确问题、篇间阅读路径明确、层内无重复；threshold >= 4；evidence 独立评审逐篇评分。
- **Notes**: 跨束引用用相对路径；`concepts/` 位于子目录，引用同组平级束需 `../../` 深度（既有束曾因误用 `../` 产生断链，实施后必须机械 `Test-Path` 复核）。
- **Completion Evidence**（2026-10-15）：`concepts/` 建成 5 文件（`00-open-platform-overview.md`、`01-share-capability-integration.md`、`02-promotion-management.md`、`03-boundaries-versions-and-policy.md` + 无 frontmatter 的 `index.md`，toctree 收 00～03 且导读表齐备）。主会话机械复验：concepts 目录 `okf_version` 命中 **0**；Mermaid 代码块 **1** 个（位于 `01` 接入链路 flowchart），经 `check_mermaid.py` 的 `check_block` 实跑「共 1 个代码块、通过 1 个、有问题 0 个」；`index.md` 首行为 `{toctree}`（无 frontmatter）。子代理自验：24 条相对链接逐一 `Test-Path` 全部存活（含跨束 `../../workbuddy-official-docs/index.md`、`../../wecom-5-0-12-release/index.md`）；F 引用抽查命中且**越界引用为空**（facts 64 条中引用 62 条，未用 F-033/F-056 属公告结束语）；零 `file:///`、零 `C:\Users`、零「已 GA/已全量」；五类口径标签四篇合计覆盖。**偏差记录**：Task 描述中「模块地图表（14 项）」系笔误，实际侧边栏模块为 **13** 项（与 `facts.md` F-003/F-004～F-016 一致），按 13 项逐行登记并标注「本次未采集，仅登记入口」。TR-3.1/3.2/3.3 自验通过。

## Task 4: examples 两篇 + examples/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 产出 `examples/00-integrate-share-capability.md`（第三方应用接入分享能力：前置条件（企业认证开发者、PC 端 Windows/macOS 应用标识与签名）→ 注册应用 → 填基础配置/应用平台信息（支持保存草稿）→ 提交审核（即时生成应用 ID，7 个工作日内完成，三渠道通知）→ 生成密钥 → 参照《PC 端开发手册》接入 → 联调用户侧流程与 5.8.0 门槛）。
  - 产出 `examples/01-create-and-track-promotion.md`（创建推广：从发布管理列表资产「分享」按钮或「推广管理」页「新建推广」→ 选推广方式（分享链接 / 微信小程序码，可同时勾选）→ 填渠道标签 → 复制链接/下载小程序码 → 停用管理 → 在「运营数据 → 推广效果」按时间范围/资产类型筛选并按渠道标签下钻）。
  - 每篇含前置条件、操作步骤、结果判据、限制与边界；未在本机实跑的步骤显式标注「未在本机实跑，依据官方公告（F-xxx）」。
  - `examples/index.md`：toctree 收 00～01 + 场景导览表。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 2 篇文件全部存在，frontmatter 合规；每篇含「前置条件 / 操作步骤 / 结果判据 / 限制与边界」四段结构；所有未实跑步骤含显式标注（Grep 抽查）。
  - `rule` TR-4.2: 步骤中出现的功能名、入口路径、配置项名均可在对应 concepts 或公告页找到出处（F 编号），无凭空补全的操作路径；不得编造公告未给出的接口参数。
  - `rubric` TR-4.3: 操作可用性；scale 1-5；anchors 1=步骤缺失无法照做/3=步骤完整但结果判据含糊或前置不清/5=前置/输入/步骤/判据/限制完整，读者可据此判断能否在本机复现；threshold >= 4；evidence 独立评审抽查。
- **Notes**: 不实际注册账号、不提交真实审核、不生成真实密钥、不创建真实推广；示例中的命名与门槛一律以公告为准，不虚构。
- **Completion Evidence**（2026-10-15）：`examples/` 建成 3 文件（`00-integrate-share-capability.md`、`01-create-and-track-promotion.md` + 无 frontmatter 的 `index.md`）。主会话机械复验：`examples` 目录 `okf_version` 命中 **0**；「未在本机实跑」命中 **27** 处（00 篇 12 / 01 篇 15）；四段标题齐备（00 篇行 19/28/42/52，01 篇行 19/29/45/54：「前置条件 / 操作步骤 / 结果判据 / 限制与边界」）。子代理自验：16 条相对链接逐一 `Test-Path` 全部存活（同束 `../concepts/*`、`../references/*`、同级 00/01，跨束 `../../workbuddy-official-docs/index.md`）；F 引用 00 篇 20 条、01 篇 25 条，并集落在 F-001~F-064 区间、**越界引用 0**；所有入口路径（`/app-feature/all`、`/growth`、`/growth/effect`）与配置项名均挂 F 编号；零 `file:///`、零 `C:\Users`。未注册账号、未提交审核、未生成密钥、未创建推广。TR-4.1/4.2/4.3 自验通过。

## Task 5: 根 index.md、log.md 与 references 收口
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `index.md`：OKF v0.2 frontmatter（`okf_version: "0.2"`、`status`、`stale_after: 2027-04-15`、sources 全列）、内容性质块（平台公告教程化、设 examples 的理由）、可信度状态块、「这束知识包讲什么」分层导读表、已知边界（五类口径 + 单源清单 + 未实跑声明 + 未采集模块清单）、主题关联（同组既有束 + codebuddy）、一句话结论、toctree（`concepts/index`、`examples/index`、`references/index`、`log`）。
  - `log.md`：初始版本条目，记录七阶段执行、口径决策、覆盖统计、并行在途观测、门禁运行方式与未运行 `invoke` 的声明、独立评审结论留位。
  - 收口 `references/index.md` 与各子目录 index 的 toctree 完整性。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 根 `index.md` 的 toctree 四条目（`concepts/index`、`examples/index`、`references/index`、`log`）对应文件全部存在；`okf_version` 仅出现在根 `index.md`，子文档不含。
  - `rule` TR-5.2: `log.md` 日期标题为 `YYYY-MM-DD` 倒序结构，内容含七阶段、覆盖页数、口径决策、门禁方式四类信息。
  - `rubric` TR-5.3: 已知边界可决策性；scale 1-5；anchors 1=边界缺失或与正文矛盾/3=主要边界有但分散/5=集中声明且每条挂 F 编号，读者可直接判断「谁能接入 / 支持哪些端与资产 / 哪些需复核」；threshold >= 4。
- **Notes**: 「已知边界」需明确区分「官方未宣布」与「未采集」，不得把未采集写成不存在。
- **Completion Evidence**（2026-10-15）：根 `index.md` 与 `log.md` 建成，全束 Markdown 共 **14 个**（根 2 + concepts 5 + examples 3 + references 4）。主会话机械复验：`okf_version` 全束命中 **1 处**（仅在根 `index.md` 第 2 行），其余 13 文件命中 0；根 `index.md` 的 `{toctree}` 四条目（`concepts/index`、`examples/index`、`references/index`、`log`）对应文件全部存在；`log.md` 无 frontmatter、含 `## 2026-10-15` 倒序日期标题，内容覆盖七阶段执行、覆盖统计（2 篇公告 + 导航面 + 13 模块地图、F-001~F-064）、五类口径决策与门禁运行方式（显式声明未运行 `invoke gates.*`），并为独立评审结论留位。三个子目录（concepts/examples/references）`index.md` 的 toctree 条目对应文件均存在，无需补齐。TR-5.1/5.2/5.3 自验通过。

## Task 6: 五级索引接入、计数复算与同组互链
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `tencent/index.md`：导航表 +1 行、toctree +1 条、「关于本分组」段追加本束说明与生成来源、「相关链接」+1 行；束数与概念/示例/信源/事实计数按机械真值复算。
  - `ecosystems/index.md`（腾讯生态行与类计数）、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`（`total_bundles`、正文计数行、mermaid 节点文字、节标题、分组表）逐层同步。
  - `workbuddy-official-docs/index.md` 回补 1 条指向新束的链接（`git diff` 核对仅新增 1 行超链接）。
  - 机械复算：自包含脚本按 marker 目录（concepts/examples/references）+ 锚点束=1 口径清点 tencent/ai/jishu 三级真值，与 `check-bundles-index.py` 输出对齐；临时脚本用后删除。
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: `python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0、五面一致；输出计数与写入索引的数字逐项相等。
  - `rule` TR-6.2: `python scripts/check-toctrees.py` 全量输出过滤本束名零命中；既有/并行污染项只在 `log.md` 列名披露，不顺手修复。
  - `rule` TR-6.3: `workbuddy-official-docs/index.md` 的 `git diff` 恰为 +1 条互链，其事实、计数、正文其他部分零改动；新束 `index.md`「主题关联」含反向链接；本束未修改同组其他束文件（`git status` 逐文件核对）。
- **Notes**: 若观察并行会话实时改写总索引，以最后一次无写入窗口的脚本输出为准并在 log 记录观测事实。
- **Completion Evidence**（2026-10-15）：机械真值来自 `check-bundles-index.py`/`check-toctrees.py` 与目录清点（束 = 目录树口径；概念/示例 = 各束 concepts/examples 下 .md 数不含 index.md，实测 113/36；信源/事实按既有累积口径 +4/+64）。五级索引全部接入：`tencent/index.md`（导航表 +1 行、toctree +1 条、相关链接 +1 行、「关于本分组」14→**15** 束 / 109→**113** 概念 / 34→**36** 示例 / 64→**68** 信源 / 2139→**2203** 事实，并追加本束生成说明）→ `ecosystems/index.md`（类总 90→**91**、腾讯行 14→**15**）→ `jishu/ai/index.md`（frontmatter description 与正文 242→**243**、ecosystems 行 90→**91**）→ `jishu/index.md`（ai 行 242→**243**）→ `doc/bundles/index.md`（`total_bundles` 636→**637**、计数行 636→**637**、mermaid `jishu` 节点 471→**472**、节标题 471→**472**、分组表 ai 行 242→**243**）。**门禁结果**：`python scripts/check-bundles-index.py` 退出码 **0**——「9 域 / 61 组 / **637 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致」；`python scripts/check-toctrees.py` 退出码 **0**——「全部 index.md 引用有效，所有内容文档均可达」（本束相关项零命中）。回链 `workbuddy-official-docs/index.md` 的主题关联段已新增 1 条指向本束的链接；本束未修改同组其他束任何文件。⚠️ 观测（披露不修复）：`tencent/index.md` 的「信源」基数 64 无法由「各束根 index.md 的 sources 条目数」或「references 文档数」等显式口径复现（实测前者 73、后者 57），疑为历史口径或并行在途演进所致；本次按既有先例的**增量**方式记 +4，未重定基数，已记入本束 `log.md`。

## Task 7: V 阶段机械门禁与四视角自审
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 运行 `python scripts/check-utf8.py`；Grep 全部新增文件的 Markdown 链接并逐一 `Test-Path`；Grep 零 `file:///`、零 `C:\Users`/家目录路径；逐文件核对 frontmatter 必填字段与 `okf_version` 位置。
  - 正则比对 `facts.md` 与 `article-source.md` 的 F 编号集合相等。
  - 定向 Sphinx dummy 构建验证本束无引入错误（不声称全库通过）。
  - 四视角自审（魔鬼代言人 / 新人 / 业务方 / 未来）结论并入 `verification.md`；advisory 能当场收口的当场收口。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-7.1: UTF-8 门禁通过；束内全部相对链接 `Test-Path` 存活；零 `file:///`、零本机绝对路径；frontmatter 与 `okf_version` 位置合规。
  - `rule` TR-7.2: F 编号双份集合比对相等；定向构建无本束引入错误。
  - `rubric` TR-7.3: 四视角攻击覆盖度；scale 1-5；anchors 1=自审走过场/3=有攻击点无处置记录/5=每视角有具体攻击点、处置方式与可复核证据；threshold >= 4；evidence 为 verification.md 自审表。
- **Notes**: 全库既有断链/编码问题按归属隔离，如实报告，不扩大修复范围。
- **Completion Evidence**（2026-10-15）：**七项门禁**（工作目录 = 子模块根）——
  ① `python scripts/check-utf8.py` **EXIT 0**（11611 文件均为有效 UTF-8）；
  ② `python scripts/check-toctrees.py` 首跑 **EXIT 0**；Task 7 结束后复跑 **EXIT 1**，失败项**全部归属于并行会话的在途新束**（先为 `workbuddy-hardware-integration-whitepaper`、后为 `sheke/industry/workbuddy-opc-whitepaper`），**本束名零命中**；按归属隔离不修，已记入 `log.md`；
  ③ 本束 14 个 `.md` 的 Markdown 相对链接逐条 `Test-Path`：**71/71 存活、失败 0**（编辑后复跑仍 71/0）；
  ④ `file:///` 与 `C:\Users` 在束内**各 0 命中**；
  ⑤ frontmatter 逐文件核对**全部合规**：仅根 `index.md` 含 `okf_version`；`log.md` 与三个子目录 `index.md` 无 frontmatter；其余 9 个子文档含 `type`/`generated`/`verified`/`status`/`stale_after`/`sources` 且不含 `okf_version`；
  ⑥ `S\facts.md` 与 `B\references\article-source.md` 的 `F-\d{3}` 唯一集合**均 64、差集为空、F-001~F-064 连续、无重复**；
  ⑦ 定向 Sphinx dummy 构建（`python -m sphinx -b dummy -E doc _build/dummy-bundle doc/bundles/jishu/ai/ecosystems/tencent/workbuddy-open-platform-sharing-and-promotion/index.md`）**EXIT 0**，**提及本束的 WARNING = 0**（全量 258 warnings 均属其他既有束，按归属隔离不修），构建产物已清理（`_build/` 在 .gitignore 内）。
  **门禁抓出的本束缺陷：0 项**。advisory 当场收口 2 处（`concepts/01` L33 补术语说明；`references/verification.md` L75 标记统一为 ❌、L121 措辞收紧）。四视角自审落于 `references/verification.md` 第七节 L136–175（魔鬼代言人 L140 / 新人 L152 / 业务方 L161 / 未来维护者 L170），摘要表 L115–124；视角四遗留一条「SPA 公告页无独立快照，`stale_after` 到期建议重读正文比对 F 编号」。`log.md` L5–L8 追加观测：Task 6 的「信源」基数 64 不可由显式口径复现（排除本束的 14 束恰为 73/57），故只记增量 +4 不重定基数。TR-7.1/7.2/7.3 自验通过。

## Task 8: 独立上下文评审 R1 与收尾
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 队列清空后新建 `review.md`（CP-R1～R6 规则检查点 + CP-U1/U2 量规，覆盖 AC-1～AC-6）。
  - 委派 fresh-context 只读子代理执行独立评审（提供绝对路径、运行命令与评审合同：公告正文覆盖与编号双份、五类口径分层、链接与编码门禁、五级计数一致、同组互链最小改动、examples 未实跑标注）。
  - 结果路由：`pass` 则写 Review History 并向用户汇报、给出 C 阶段提交方案供决策；`fail` 则把可行动发现固化为 pending 修复 issue 回 Implement，回归后开新 R2；`blocked` 则记录阻塞并请求解决。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: `review.md` 每个 AC 至少被一个检查点覆盖；R1 结果为 `pass`（若 `fail` 必有非空 pending 修复队列且回归后开 R2）。
  - `rubric` TR-8.2: 评审独立性与证据质量；scale 1-5；anchors 1=主会话自审冒充/3=独立评审但证据笼统/5=fresh 子代理逐检查点给出命令/文件证据与评分并独立复核网页；threshold >= 4。
- **Notes**: 不执行 git commit；评审通过后在汇报中给出 C 阶段提交方案（子模块 → 主仓 spec → 子模块指针，显式文件列表）供用户决策。
- **Completion Evidence**（2026-10-15）：`review.md` 建成（CP-R1~R6 + CP-U1/U2，覆盖 AC-1~AC-6）。委派 **fresh-context 只读子代理**执行独立评审，该代理未参与实施、未参考实施者自验结论，现场自跑四道门禁并独立复算 F 编号集合、台账覆盖、链接、frontmatter、tencent 计数与 git diff/status，全程**未修改任何文件**、无 git 写操作。**裁决 `pass`**：CP-R1~CP-R6 六项 rule 检查点全 PASS；CP-U1 = **5/5**、CP-U2 = **5/5**（阈值 ≥4）；**可行动发现 0 条**；仅 3 条 P3 advisory（`tencent/index.md:43`「信源」基数不可复现——历史遗留且已在 `log.md` 披露；`jishu/index.md:20` ai 行束数以递归链接呈现；工作树由并行会话动态漂移）。评审确认：`check-bundles-index.py` EXIT 0（评审时点为 9 域/61 组/**638** 束五面一致，较实施者记录的 637 多出的 +1 完全归属并行会话新束，本束增量自洽）；`check-toctrees.py` EXIT 1 的失败项**本束零命中**、全归属并行在途束；回链 `workbuddy-official-docs/index.md` 的 diff **恰 +1 行**。**未执行任何 git 提交**；C 阶段提交方案随交付汇报提交用户决策。

## 依赖关系

- Task 2 依赖 Task 1（无台账无法登记事实归属）。
- Task 3 依赖 Task 2（concepts 的 F 引用须先有编号事实）。
- Task 4 依赖 Task 3（examples 的功能口径与 concepts 一致）。
- Task 5 依赖 Task 4（根索引导读表需覆盖全部篇目）。
- Task 6 依赖 Task 5（计数复算需文件集合已固定）。
- Task 7 依赖 Task 6（门禁需索引已写入）。
- Task 8 依赖 Task 7（评审以队列清空为前置）。
- 无并行可并行的任务：Task 6 的机械复算与 Task 7 的门禁须串行，避免写读冲突。

## 批准门

本规格与任务计划已提交用户审查，**获得显式批准前不进入实施**。批准范围不含：注册开放平台账号、提交真实应用审核、生成真实密钥、创建真实推广、修改同组既有束事实与计数（仅 1 条互链除外）、执行 git commit/push。实施前须先检查 `projects/awesome-okf-xs/` 子模块无 merge/rebase 进行中。
