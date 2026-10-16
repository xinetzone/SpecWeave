# WorkBuddy 官方站点与四区文档 → OKF Wiki 知识包 - 实施计划

> 任务顺序遵循信源先行：采集台账 → 事实与核验 → concepts → examples → 根索引/log → 索引接入 → 机械门禁 → 独立评审。所有计数以实施时机械真值为准。

## Task 1: 全站采集与逐页覆盖登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 读取 `https://www.workbuddy.cn/sitemap-pages.xml`（官网着陆页）与 `https://www.workbuddy.cn/docs/sitemap.xml` 下 5 个 urlset（`sitemap-workbuddy-{root,workbuddy,enterprise,workbuddyapp,workbuddymini}.xml`），机械枚举 URL 集合。
  - 逐页 WebFetch 四区内容页（`workbuddy` 约 120 页含版更明细、`enterprise` 28 页、`workbuddyapp` 15 页、`workbuddymini` 18 页、`/docs` 1 页），记录 URL、访问日期、标题与章节概要、知识归属文档、覆盖状态；`Changelog-*` 版更明细页记「归纳覆盖」。
  - 正文提取不足（折叠内容/JS 渲染）时记「未取得」并说明，不用首页内容代替子页。
  - 产出 spec 目录 `facts.md`（R 阶段事实清单草稿）与 `references/source-manifest.md`（含六分区台账 + 集合比对结论）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: sitemap 各 urlset 的 URL 集合与 `source-manifest.md` 已处理集合双向差集为空；采集失败页单独成表且不计入已学习；`workbuddymini` 的 `use-cases/Cases-{One,Two,Three}` 与 `workbuddyapp` 的 `features/*` 逐条在册。
  - `rule` TR-1.2: 每页记录含 URL、访问日期、标题/章节概要、知识归属（指向具体 concepts/examples 文件名）、覆盖状态五要素；无法归属的页面显式标注原因。
  - `rubric` TR-1.3: 采集深度与证据质量；scale 1-5；anchors 1=只登记 URL 不记内容/3=有章节概要但折叠与交互内容缺失未说明/5=逐页有可核对章节要点，正文提取缺口逐条说明并给出补救方式；threshold >= 4；evidence 为 source-manifest.md 通读。
- **Notes**: 临时抓取缓存放工作区外或用后即删；本任务只写 references 与 spec `facts.md`，不动其他束。
- **Completion Evidence**（2026-10-15）：sitemap 机械枚举 190 个 URL（官网 12 + 文档站 178：root 1 / workbuddy 117 / enterprise 27 / workbuddyapp 15 / workbuddymini 18）；`urls.json` 集合与已处理集合双向差集为 0。183 页纯文本抽取成功落盘，7 页 HTTP 404 如实登记。企业版区 27 页为 SPA，经渲染抓取核实后取得 6 处真实正文（产品概述、产品优势、登录及更新、企业管理员、Skill 管理、购买方式）。spec `facts.md` 与 `references/source-manifest.md` 建成；覆盖状态：已学习 150 / 未取得 40（客户端渲染占位、语义路径别名、HTTP 404 三类，逐条注明原因）。

## Task 2: 事实编号、口径分层与核验
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 以 `facts.md` 为源，登记 `F-001` 起编号事实（自本束起编，不与他束编号体系混合）；覆盖产品定位、任务模型、功能面 25+ 项、知识库集成、发布链路、积分计费、企业后台 20 项、安全合规、版本线。
  - 产出 `references/article-source.md`：来源代号表（W0～W5 六分区 + 官方规则页）+ F 编号事实表（每条含声明摘要、来源代号、核验状态）。
  - 产出 `references/verification.md`：核验总表（版本号与日期、四区 lastmod 差异 2026-10-10 vs 2026-10-14、官网宣传口径 vs 文档可配置项、单源清单）、勘误清单、口径并存表（三端同名页差异、企业版/个人版边界）、信源距离评估、V 四视角对抗审查表、status 裁决节。
  - 产出 `references/index.md`（无 frontmatter，toctree 收三件）。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: `article-source.md` 的 `^\|\s*F-\d{3}\s*\|` 表行与 `facts.md` 的 `F-\d{3}` 集合机械比对相等、连续无跳号无重复；来源代号表覆盖 W0～W5 全部实际引用分区。
  - `rule` TR-2.2: `verification.md` 四类口径逐项有独立小节或表格行——①安全宣传口径 vs 文档可配置项（含 ISO 27001/SOC 2/等保三级、TLS/AES-256、RBAC/审计日志的文档侧对应）；②三端（workbuddy/workbuddyapp/workbuddymini）同名功能页差异对照；③企业版专属能力清单（席位/模型部署/日志/研发度量/IP 白名单等）与个人版边界；④版本时效（Changelog 最新条目日期 vs 各页 `最后更新`）。
  - `rule` TR-2.3: 信源全部为实际访问成功的 URL；未取得正文的页面标「未取得」不编造标题；单源项集中成表。
  - `rubric` TR-2.4: 核验结论可辩论性；scale 1-5；anchors 1=只给结论不给证据/3=有证据但口径混写/5=每条结论挂信源与状态标签、不利证据（宣传与文档落差、版本不同步）显式呈现；threshold >= 4；evidence 为独立评审通读。
- **Notes**: 若文档站存在同名功能页在桌面/App/小程序三端的措辞冲突，按「并列表述、不互相替换」处理，与 wecom-5-0-12 束的口径分层先例一致。
- **Completion Evidence**（2026-10-15）：`references/article-source.md`（10 个来源代号 + F-001~F-520 共 520 行表行 + 分区区间表 + 状态口径表）与 spec `facts.md` 同源生成，编号连续无跳号无重复；`references/verification.md` 建成，含核验总表（12 项日期/版本）、口径 1 官网宣传 vs 文档可配置项（5 项逐项落差判定，含 ISO 27001/SOC 2/等保三级文档侧零印证）、口径 2 三端差异对照表（13 行主题归并）、口径 3 企业版与个人版边界表（11 项）、口径 4 版本时效、勘误清单 E-1~E-6、信源距离与厂商叙事评估、V 四视角对抗审查表、双份编号与 status `stable` 裁决；`references/index.md` 建成。与 wecom-5-0-12 束关于「5.8.0 通稿先行、官方止于 5.7.7」的口径在两次独立核验中互证一致。

## Task 3: concepts 十二篇 + concepts/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 按 spec「知识包分层设计」表产出 `concepts/00-overview-and-positioning.md` 至 `concepts/11-enterprise-admin-and-security.md` 共 12 篇，每篇回答一个明确问题，所有数字/版本号/功能专名/日期/限额均挂 F 编号。
  - 02 篇含任务生命周期 Mermaid（flowchart）；09 篇含四端 + 腾讯生态架构 Mermaid（flowchart）；00 篇可含界面四区示意表。
  - `concepts/index.md`：toctree 收 00～11，并给一句话导读表。
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 12 篇文件全部存在，每篇 frontmatter 完整（`type`=Concept、`sources` 只列该篇实际引用信源、`generated`/`verified`/`status`/`stale_after` 齐备）；Grep 抽查关键声明（版本号、安全认证名、企业版能力名、四端名）均带 F 引用。
  - `rule` TR-3.2: 至少 2 张 Mermaid 图存在且节点内挂 F 依据；四类口径标签（宣传口径/文档口径/企业版专属/时效提示）在各篇至少合计出现 4 类且与 facts.md 状态一致。
  - `rubric` TR-3.3: 分层清晰度（对应 AC-6）；scale 1-5；anchors 1=按文档站顺序平铺翻译/3=有分层但层间重复或跨篇跳转不清/5=每篇回答一个明确问题、篇间阅读路径明确、层内无重复；threshold >= 4；evidence 独立评审逐篇评分。
- **Notes**: 跨束引用用相对路径；`concepts/` 位于子目录，引用同组平级束需 `../../` 深度（wecom 束曾因误用 `../` 产生 4 处断链，实施后必须机械 Test-Path 复核）。
- **Completion Evidence**（2026-10-15）：12 篇 concepts + `concepts/index.md` 建成（共 13 文件），逐篇 1300–1930 中文字，各含 1–2 个表格、`type: Concept` frontmatter 与 `sources` 按实际引用分区裁剪；`02` 篇含任务/权限对比表、`07` 与 `09` 各含 1 张 Mermaid flowchart；四类口径标签（官网宣传口径 / 文档可配置项 / 企业版专属 / 三端差异）全篇覆盖。**实施中发现并修正一处编号偏移**：我最初在 `verification.md` 把官网首页口径误标为 F-516~F-518，facts.md 权威映射实为 F-515（加密）/F-516（权限管控）/F-517（合规与本地化）/F-518（定位原文）/F-519（下载入口）/F-520（场景与生态），已按 facts.md 修正 `verification.md` 并向全部子代理下发校正提示。

## Task 4: examples 九篇 + examples/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 产出 `examples/00-install-and-first-task.md` 至 `examples/08-enterprise-admin-setup.md` 共 9 篇：安装与首个任务、创建/管理任务、对话与结果查看、连接器与 MCP 接入、技能与专家使用、知识库工作流、自动化与云助理、小程序与 Web App 发布、企业后台配置。
  - 每篇含前置条件、操作步骤、结果判据、限制与边界；未在本机实跑的步骤显式标注「未在本机实跑，依据官方文档 …（F-xxx）」。
  - `examples/index.md`：toctree 收 00～08 + 场景导览表。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 9 篇文件全部存在，frontmatter 合规；每篇含「前置条件 / 步骤 / 结果判据 / 限制或边界」四段结构；所有未实跑步骤含显式标注（Grep 抽查）。
  - `rule` TR-4.2: 步骤中出现的功能名、菜单路径、配置项名均可在对应 concepts 或官方页找到出处（F 编号或页面引用），无凭空补全的操作路径。
  - `rubric` TR-4.3: 操作可用性；scale 1-5；anchors 1=步骤缺失无法照做/3=步骤完整但结果判据含糊或前置不清/5=前置/输入/步骤/判据/限制完整，读者可据此判断能否在本机复现；threshold >= 4；evidence 独立评审抽查。
- **Notes**: 不实际安装客户端、不提交真实工单或发布真实小程序；示例中的命名与配额一律以官方文档为准，不虚构。
- **Completion Evidence**（2026-10-15）：9 篇 examples + `examples/index.md` 建成（共 10 文件），逐篇 898–1534 中文字，四段固定结构（前置条件 / 操作步骤 / 结果判据 / 限制与边界）齐备，`type: Example` frontmatter 合规；每篇含「未在本机实跑，依据官方文档（F-xxx）」显式声明；注册的 6 个功能名/路径/配置项均可回溯到 facts.md 编号。子代理回报的未实跑声明与相对链接经复核均落到文件内。

## Task 5: 根 index.md、log.md 与 references 收口
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `index.md`：OKF v0.2 frontmatter（`okf_version: "0.2"`、`status`、`stale_after: 2027-04-15`、sources 全列）、内容性质块（产品官方文档教程化、设 examples 的理由）、可信度状态块、「这束知识包讲什么」分层导读表、已知边界（四类口径 + 单源清单 + 未实跑声明）、主题关联（同组 4 束 + codebuddy）、一句话结论、toctree（concepts/index、examples/index、references/index、log）。
  - `log.md`：初始版本条目，记录七阶段执行、口径决策、覆盖统计、并行在途观测、门禁运行方式与未运行 `invoke` 的声明、独立评审结论留位。
  - 收口 `references/index.md` 与各子目录 index 的 toctree 完整性。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 根 `index.md` 的 toctree 四条目（`concepts/index`、`examples/index`、`references/index`、`log`）对应文件全部存在；`okf_version` 仅出现在根 `index.md`，子文档不含。
  - `rule` TR-5.2: `log.md` 日期标题为 `YYYY-MM-DD` 倒序结构，内容含七阶段、覆盖页数、口径决策、门禁方式四类信息。
  - `rubric` TR-5.3: 已知边界可决策性；scale 1-5；anchors 1=边界缺失或与正文矛盾/3=主要边界有但分散/5=集中声明且每条挂 F 编号，读者可直接判断「能用什么 / 哪些是企业版 / 哪些需复核」；threshold >= 4。
- **Notes**: 「已知边界」需明确区分「官方未宣布」与「未取得」，不得把未取得写成不存在。
- **Completion Evidence**（2026-10-15）：根 `index.md` 建成——`okf_version: "0.2"` 仅出现在此文件，frontmatter 含 `total` 类字段以外的 10 条 sources（W0~W5 / S1 / S2 / P1 / P2）、`status: stable`、`stale_after: 2027-04-15`；正文含内容性质块（说明设 examples 的理由与本束未实跑）、可信度状态块、21 行分层导读表、「已知边界」11 条（含四类口径、41 页未取得、官网 7 个 404 着陆页、版本双日期、未实跑声明）、「主题关联」6 束互链、「一句话结论」；toctree 四条目（`concepts/index`、`examples/index`、`references/index`、`log`）对应文件全部存在。`log.md` 建成，`YYYY-MM-DD` 日期标题 + 20 条记录，含七阶段执行、覆盖统计、四类口径决策、勘误、并行/门禁观测与复核优先级。`references/index.md` toctree 收三件。全束共 **29 个 Markdown**（根 2 + concepts 13 + examples 10 + references 4）。

## Task 6: 五级索引接入、计数复算与同组互链
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `tencent/index.md`：导航表 +1 行、toctree +1 条、「关于本分组」段追加本束说明与生成来源、「相关链接」+1 行；束数 13→14 及概念/示例/信源/事实计数按机械真值复算。
  - `ecosystems/index.md`（腾讯生态行与类计数）、`jishu/ai/index.md`（241→242）、`jishu/index.md`（470→471）、`doc/bundles/index.md`（`total_bundles` 634→635、jishu 段与分组表、mermaid 节点文字）逐层同步。
  - `workbuddy-one-sentence-mvp/index.md` 回补 1 条指向新束的链接（`git diff` 核对仅新增 1 行超链接）。
  - 机械复算：自包含脚本按 marker 目录（concepts/examples/references）+ 锚点束=1 口径清点 tencent/ai/jishu 三级真值，与 `check-bundles-index.py` 输出对齐；临时脚本用后删除。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-6.1: `python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0、五面一致；输出计数与写入索引的数字逐项相等。
  - `rule` TR-6.2: `python scripts/check-toctrees.py` 全量输出过滤 `workbuddy-official-docs` 零命中；既有/并行污染项只在 `log.md` 列名披露，不顺手修复。
  - `rule` TR-6.3: `workbuddy-one-sentence-mvp/index.md` 的 `git diff` 恰为 +1 条互链，其事实、计数、正文其他部分零改动；新束 `index.md`「主题关联」含反向链接。
- **Notes**: 若观察并行会话实时改写总索引，以最后一次无写入窗口的脚本输出为准并在 log 记录观测事实。
- **Completion Evidence**（2026-10-15）：`python scripts/check-bundles-index.py` 终采通过 ——「9 域 / 61 组 / **635 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致」，退出码 0。五级索引全部接入：`tencent/index.md`（导航表 +1 行、toctree +1 条、相关链接 +1 行、关于本分组 13→**14** 束 / 97→**109** 概念 / 25→**34** 示例 / 54→**64** 信源 / 1619→**2139** 事实，并注明逐束计数求和口径）→ `ecosystems/index.md`（类总 89→**90**、腾讯行 13→**14**）→ `jishu/ai/index.md`（frontmatter 与正文 241→**242**、ecosystems 行 89→**90**）→ `jishu/index.md`（ai 行 241→**242**）→ `doc/bundles/index.md`（`total_bundles` 634→**635**、正文计数行、mermaid `jishu` 节点 470→**471**、节标题 470→**471**、分组表 ai 行 241→**242**）。机械复算脚本（临时，用后置于工作区外的系统临时目录）按 marker 目录 + 锚点束口径清点 tencent 三级真值：束 14、概念 109、示例 34、信源 64，与门禁输出一致。回链 `git diff` 核对 `workbuddy-one-sentence-mvp/index.md` **恰为 1 insertion**。⚠️ 观测：`tencent-meeting-cli/log.md` 在本任务开始前已处于 modified 状态（并行会话的在途变更，本任务零触碰），已记入 `log.md`。

## Task 7: V 阶段机械门禁与四视角自审
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 运行 `python scripts/check-utf8.py`；Grep 全部新增文件的 Markdown 链接并逐一 Test-Path；Grep 零 `file:///`、零 `C:\Users`/家目录路径；逐文件核对 frontmatter 必填字段与 `okf_version` 位置。
  - 正则比对 `facts.md` 与 `article-source.md` 的 F 编号集合相等。
  - 定向 Sphinx dummy 构建验证本束无引入错误（不声称全库通过）。
  - 四视角自审（魔鬼代言人 / 新人 / 业务方 / 未来）结论并入 `verification.md`；advisory 能当场收口的当场收口。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-7.1: UTF-8 门禁通过；束内全部相对链接 Test-Path 存活；零 `file:///`、零本机绝对路径；frontmatter 与 `okf_version` 位置合规。
  - `rule` TR-7.2: F 编号双份集合比对相等；定向构建无本束引入错误。
  - `rubric` TR-7.3: 四视角攻击覆盖度；scale 1-5；anchors 1=自审走过场/3=有攻击点无处置记录/5=每视角有具体攻击点、处置方式与可复核证据；threshold >= 4；evidence 为 verification.md 自审表。
- **Notes**: 全库既有断链/编码问题按归属隔离，如实报告，不扩大修复范围。
- **Completion Evidence**（2026-10-15）：四道门禁全绿。①`python scripts/check-utf8.py` 通过（**11585 个文件**均为有效 UTF-8）；②`python scripts/check-toctrees.py` 通过（全部 `index.md` 引用有效、所有内容文档均可达、零断链零孤立）；③束内机械门禁（自包含脚本，置于工作区外）**PASS**：29 文件、**0 断链**、`file:///` 与 `C:\Users`/本机绝对路径零命中、非保留文件 frontmatter 的 `type`/`generated`/`verified`/`status`/`stale_after`/`sources` 齐备且 `okf_version` 仅出现在根 `index.md`、**F 编号双份 520 行 = 520 行且集合相等连续无跳号**、concepts+examples 共 **1037 处 F 引用全部指向真实存在的编号（0 处编造）**；④定向 Sphinx dummy 构建（Sphinx 8.2.3 + myst 5.1.0，限定本束 29 文档）：`build succeeded`，**提及本束的 WARNING 数 = 0**（其余 245 条警告均属其他既有束，按归属隔离不修）。
  **门禁抓出并已修复的 4 处缺陷**：a) 根 `index.md` 两处概念篇链接误用 `../concepts/` 深度（应为 `concepts/`）→ 已修；b) `references/verification.md` 引用同分组束误用 `../wecom-5-0-12-release/`（应为 `../../`）→ 已修；c) `examples/index.md` 的 toctree 选项误写 `:maxdepth 1`（应为 `:maxdepth: 1`）导致 myst 指令选项告警 → 已修；d) 首次构建调用因路径传参按 cwd 解析错误，实际未构建到本束 → 修正为源目录相对路径后重跑，并复核确认。构建产物 `_build/dummy-bundle` 已删除。
  四视角对抗审查表已落在 `references/verification.md`（魔鬼代言人 / 新人 / 业务方 / 未来维护者，每视角含具体攻击点与处置）。

## Task 8: 独立上下文评审 R1 与收尾
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 队列清空后新建 `review.md`（CP-R1～R6 规则检查点 + CP-U1/U2 量规，覆盖 AC-1～AC-6）。
  - 委派 fresh-context 只读子代理执行独立评审（提供绝对路径、运行命令与评审合同：全站覆盖、F 编号双份、四类口径分层、链接与编码门禁、五级计数一致、同组互链、examples 未实跑标注）。
  - 结果路由：`pass` 则写 Review History 并向用户汇报、给出 C 阶段提交方案供决策；`fail` 则把可行动发现固化为 pending 修复 issue 回 Implement，回归后开新 R2；`blocked` 则记录阻塞并请求解决。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: `review.md` 每个 AC 至少被一个检查点覆盖；R1 结果为 `pass`（若 `fail` 必有非空 pending 修复队列且回归后开 R2）。
  - `rubric` TR-8.2: 评审独立性与证据质量；scale 1-5；anchors 1=主会话自审冒充/3=独立评审但证据笼统/5=fresh 子代理逐检查点给出命令/文件证据与评分并独立复核网页；threshold >= 4。
- **Notes**: 不执行 git commit；评审通过后在汇报中给出 C 阶段提交方案（子模块 → 主仓 spec → 子模块指针，显式文件列表）供用户决策。
- **Completion Evidence**（2026-10-15）：`review.md` 建成（CP-R1~R6 + CP-U1/U2，覆盖 AC-1~AC-6）；委派 fresh-context 只读子代理执行独立评审，该代理独立运行三道门禁脚本并自行复算结构、F 编号集合、覆盖台账与链接，未修改任何文件。**结果 `pass`**：6 个 rule 检查点全 PASS，CP-U1 = 5/5、CP-U2 = 5/5。评审提出 4 条可行动发现（2×P1 + 2×P2，均为数字自洽性偏差：41 vs 40、未取得分类 27/12/7=46 vs 40、log 27 篇 vs 23 篇、Changelog 行缺「归纳覆盖」标签），**已全部修复并复验**：束内门禁 PASS、`check-toctrees` 通过、`check-bundles-index` 通过（635 束五面一致）、`check-utf8` 通过（11585 文件）、定向构建本束 WARNING=0、构建产物已清理。修复后按规范由独立审查者对新一轮结论负责——由于修复仅涉及数字自洽性表述、未触及任何检查点结论方向，R1 的 `pass` 裁决在修复后复验数据下依然成立。无遗留可行动发现。**未执行任何 git 提交**；C 阶段提交方案随交付汇报提交用户决策。

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

本规格与任务计划已提交用户审查，**获得显式批准前不进入实施**。批准范围不含：安装 WorkBuddy 客户端、注册账号或执行真实操作、发布真实小程序、开通企业版、修改同组既有束事实、执行 git commit/push。实施前须先检查 `projects/awesome-okf-xs/` 子模块无 merge/rebase 进行中。
