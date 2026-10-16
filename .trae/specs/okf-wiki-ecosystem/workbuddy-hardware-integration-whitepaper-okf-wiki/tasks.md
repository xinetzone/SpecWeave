# WorkBuddy 智能硬件接入白皮书 → OKF Wiki 知识包 - 实施计划

> 任务顺序遵循信源先行：采集台账 → 事实与核验 → concepts → examples → 根索引/log → 索引接入 → 机械门禁 → 独立评审。所有计数以实施时机械真值为准。

## Task 1: 白皮书全章采集与逐章覆盖登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 采集分享页 `https://www.workbuddy.link/p/JVM0gKdRyl8k9EgElw5TxA`：先识别 SPA 壳页（4.6 KB，含 `window.__PUBLISH_BOOTSTRAP__`），再按静态制品基址 `https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/` 取得 `janus.data.json`（正文数据源，`publishVersion: 20`）与 `WorkBuddy_v4__.html`（备用）。
  - 解析 `janus.data.json` 节点树（`page-node-id`/`parentId`/`children`/`tag`/`content`），按 HTML 标签语义还原正文 Markdown（标题层级、列表、表格、代码块、Mermaid 源码外的 ASCII 决策图原样保留），提取结果落工作区外临时文件。
  - 逐章登记白皮书 0~13 章与附录 A/B 的归属文档与覆盖状态；附录 A（随册文件 `assistant-openapi.html`）记「未取得」并说明原因；`open.workbuddy.cn`（O1）记「未核验」。
  - 产出 spec 目录 `facts.md`（R 阶段事实清单草稿）与 `references/source-manifest.md`（信源台账 + 逐章覆盖表 + 集合比对结论）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 白皮书章节集合（0~13 + 附录 A/B）与 `source-manifest.md` 已登记归属集合双向差集为空；未取得项（附录 A）与未核验项（O1）单独成表且不计作已覆盖。
  - `rule` TR-1.2: 每个信源记录含 URL、访问日期、获取方式、取得体量、知识归属（指向具体 concepts/examples 文件名）、覆盖状态六要素；SPA 壳页与数据源两条获取路径显著区分。
  - `rubric` TR-1.3: 采集深度与证据质量；scale 1-5；anchors 1=只登记 URL 不记内容/3=有章节概要但表格与代码块还原缺失未说明/5=逐章有可核对要点，表格/代码块/ASCII 决策图还原完整，缺口逐条说明并给出补救方式；threshold >= 4；evidence 为 source-manifest.md 通读。
- **Notes**: 临时抓取缓存与提取脚本放工作区外或用后即删；本任务只写 references 与 spec `facts.md`，不动其他束。
- **Completion Evidence**（2026-10-15）：识别分享页为 SPA 壳页（4.6 KB，仅 `#root` 与 `publish-bootstrap-loading` 占位），依 `__PUBLISH_BOOTSTRAP__` 暴露的制品基址取得 P0 `janus.data.json`（708 KB，`publishVersion: 20`）与 P1 `WorkBuddy_v4__.html`（202 KB，备用）。解析节点树（3573 节点 / 2085 text 节点）按 HTML 标签语义还原 Markdown，提取正文 **1330 行 / 21432 字符**，含标题层级、列表、表格、代码块与 ASCII 决策图（§4.2 模式决策图原样保留）。产出 spec `facts.md`（F-001 ~ F-190，脚本验证 190 行、唯一 190、连续 1..190 = True）与 `references/source-manifest.md`（信源台账 5 行 + 逐章覆盖表 16 行 + 集合比对：章节集合 16 = 已登记 16、双向差集 0；已覆盖 15、未取得 1（附录 A）；信源已学习 2、未核验/未取得 2）。提取脚本与中间产物置于 `.temp/`，交付物零污染。

## Task 2: 事实编号、口径分层与核验
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 以 `facts.md` 为源，登记 `F-001` 起编号事实（自本束起编，不与他束编号体系混合）；覆盖白皮书定位、市场数据、六大能力、用户画像、硬件价值、六类触点、四种合作模式与商务口径、Agent 五层架构、云端能力包、端云协同、生态三层、硬件专区、场景能力矩阵、六个真实场景、开放平台四类能力与核心概念、OAuth 2.0 全流程、助理/任务/本机接口与 scope、常见问题、落地路径与准入审核、品牌授权、联合运营 SLA、术语表。
  - 产出 `references/article-source.md`：来源代号表（W0/P0/O1）+ F 编号事实表（每条含声明摘要、来源代号、章节定位、核验状态）。
  - 产出 `references/verification.md`：核验总表（发行日期 2026-08、`publishVersion: 20`、§7 声称的 2026-09-02 发布日、Skills 数量 2.2 万+ vs 7 万余）、**五类口径分层**表、勘误清单（含发行日期早于发布日的时序矛盾）、信源距离评估（厂商自述、O1 未核验、X1 未取得）、V 四视角对抗审查表、status 裁决节。
  - 产出 `references/index.md`（无 frontmatter，toctree 收三件）。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: `article-source.md` 的 `^\|\s*F-\d{3}\s*\|` 表行与 `facts.md` 的 `F-\d{3}` 集合机械比对相等、连续无跳号无重复；来源代号表覆盖 W0/P0/O1 全部实际引用信源。
  - `rule` TR-2.2: `verification.md` 五类口径逐项有独立小节或表格行——①厂商自宣 vs 第三方数据（三项指标来源分列）；②Skills 数量 2.2 万+/7 万余 双口径并存；③§6.1 匿名化场景不反推原则；④商务结构「以协议为准」限定；⑤接口「以官网开发者文档为准」+ 发行日期与发布日时序矛盾。
  - `rule` TR-2.3: 信源全部为实际访问成功的 URL；O1 未核验、附录 A 未取得显式标注不编造；单源项集中成表。
  - `rubric` TR-2.4: 核验结论可辩论性；scale 1-5；anchors 1=只给结论不给证据/3=有证据但口径混写/5=每条结论挂信源与状态标签、不利证据（同文档矛盾、时序不自洽、单源宣传）显式呈现；threshold >= 4；evidence 为独立评审通读。
- **Notes**: §0.1 与 §1.1/§5.4 的 Skills 数量矛盾按「并列表述、不互相替换」处理，与 wecom-5-0-12 / workbuddy-official-docs 束的口径分层先例一致。
- **Completion Evidence**（2026-10-15）：`references/article-source.md` 由 `facts.md` 机械生成（同一 190 行表行集合），脚本验证：190 行 / 唯一 190 / 连续 1..190 = True；含来源代号表（W0/P0/P1/O1/X1）与 15 行编号区间表，分区覆盖率与 facts.md 一致。`references/verification.md` 建成：核验总表 12 项、**五类口径分层**逐项成节（①厂商自宣 vs 第三方数据 4 行对照；②Skills 数量 2.2 万+/7 万余 三处并存；③匿名化场景 6 例 + 不反推纪律；④商务结构 5 处「以协议为准」限定；⑤接口以官网为准 + 发行日期与发布日时序矛盾）、勘误清单 E-1~E-6（含新发现：§10 引用不存在的「6.3 节」，实为 §8.3 交叉引用错误）、信源距离评估 8 维度、V 四视角对抗审查表 4 行、status 裁决 `stable` + 5 项复核优先级。`references/index.md`（无 frontmatter）toctree 收三件。**实施中新发现 E-3 交叉引用错误**，已按 §8.3 归位并登记。

## Task 3: concepts 十一篇 + concepts/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 按 spec「知识包分层设计」表产出 `concepts/00-whitepaper-and-workbuddy-overview.md` 至 `concepts/10-glossary-and-appendix.md` 共 11 篇，每篇回答一个明确问题，所有数量/日期/接口名/scope 名/时限/SLA 数值均挂 F 编号。
  - `05-oauth2-authorization-flow` 含 OAuth 2.0 授权时序 Mermaid（sequenceDiagram，参与者：用户 / 合作方 App / WorkBuddy / WorkBuddy API）；`02` 或 `03` 含 1 张流程/架构 Mermaid（合作模式决策 flowchart 或 Agent 五层架构图）。
  - `concepts/index.md`：toctree 收 00~10，并给一句话导读表。
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 11 篇文件全部存在，每篇 frontmatter 完整（`type`=Concept、`sources` 只列该篇实际引用信源、`generated`/`verified`/`status`/`stale_after` 齐备）；Grep 抽查关键声明（开放平台端点、scope 名、接口名、SLA 数值、触点名）均带 F 引用。
  - `rule` TR-3.2: 至少 2 张 Mermaid 图存在且节点内挂 F 依据；五类口径标签（厂商自宣 / 第三方数据 / 匿名化场景 / 商务框架性参考 / 接口以官网为准）在各篇至少合计出现 5 类且与 facts.md 状态一致。
  - `rubric` TR-3.3: 分层清晰度（对应 AC-6）；scale 1-5；anchors 1=按章节顺序平铺翻译/3=有分层但层间重复或跨篇跳转不清/5=每篇回答一个明确问题、篇间阅读路径明确、层内无重复；threshold >= 4；evidence 独立评审逐篇评分。
- **Notes**: 跨束引用用相对路径；`concepts/` 位于子目录，引用同组平级束需 `../../` 深度（wecom 束曾因误用 `../` 产生 4 处断链，实施后必须机械 Test-Path 复核）。
- **Completion Evidence**（2026-10-15）：11 篇 concepts + `concepts/index.md` 建成（共 12 文件），逐篇 1.1k–2.0k 中文字，`type: Concept` frontmatter 齐备且 `sources` 只列实际引用的 P0。F 覆盖区间：00=F-001~F-026（26 条）、01=F-027~F-039（13）、02=F-040~F-081（42）、03=F-082~F-109（29）、04=F-110~F-118（11）、05=F-119~F-131（15）、06=F-132~F-147、07=F-148~F-160、08=F-161~F-176、09=F-177~F-188、10=F-189~F-190。**Mermaid 2 张**：02 篇合作模式决策 `flowchart`（由 §4.2 ASCII 决策图转换，节点文本全部引号包裹）、05 篇 OAuth `sequenceDiagram`（参与者 用户/合作方 App/WorkBuddy/WorkBuddy API，与 F-123 五步一致）。五类口径标签全篇落地：`第三方数据`（F-006/F-007）、`厂商自宣口径`（F-005/F-008/F-019/F-020~F-026/F-052/F-092）、`匿名化场景`（F-102~F-108，明确「不得反推真实品牌」）、`商务框架性参考`（F-063~F-065/F-069~F-072/F-076~F-077/F-160/F-186）、`以官网为准`（F-113）。勘误 E-1（发行日期 vs 发布日时序矛盾）在 04 篇显式提示；勘误 E-2（Skills 数量 2.2 万+ vs 7 万余）在 03 篇并列。机械验证：F 引用越界 0、frontmatter 问题 0、BOM/CRLF 0、断链 0。

## Task 4: examples 七篇 + examples/index.md
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 产出 `examples/00-register-app-and-configure-scope.md` 至 `examples/06-self-service-onboarding-and-review.md` 共 7 篇：注册应用与配置 scope、OAuth 授权换票、创建并激活云端助理、发起任务与读取结果、刷新与撤销票据、硬件后端反向代理姿势、自助接入与审核。
  - 每篇含前置条件、操作步骤（HTTP 方法 / 端点 / Header / 请求体，或平台操作路径）、结果判据、限制与边界；未在本机实跑的步骤显式标注「未在本机实跑，依据白皮书（F-xxx）」。
  - `examples/index.md`：toctree 收 00~06 + 场景导览表。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 7 篇文件全部存在，frontmatter 合规；每篇含「前置条件 / 步骤 / 结果判据 / 限制或边界」四段结构；所有未实跑步骤含显式标注（Grep 抽查）。
  - `rule` TR-4.2: 步骤中出现的端点、Header、scope 名、字段名、菜单路径均可在对应 concepts 或白皮书章节找到出处（F 编号引用），无凭空补全的接入路径；示例中的 client_id/票据/响应值一律用占位符，不虚构真实值。
  - `rubric` TR-4.3: 操作可用性；scale 1-5；anchors 1=步骤缺失无法照做/3=步骤完整但结果判据含糊或前置不清/5=前置/输入/步骤/判据/限制完整，读者可据此判断能否在本机复现；threshold >= 4；evidence 独立评审抽查。
- **Notes**: 不在开放平台注册应用、不申请真实凭证、不调用真实接口；示例中的端点与 scope 以白皮书为准，不虚构。
- **Completion Evidence**（2026-10-15）：7 篇 examples + `examples/index.md` 建成（共 8 文件），逐篇 804–1300 中文字，`type: Example` frontmatter 合规。四段固定结构（前置条件 / 操作步骤 / 结果判据 / 限制与边界）全部齐备；每篇「限制与边界」显式写明「本束未在本机实跑，依据白皮书（F-xxx）」，步骤内亦逐条标注。占位符纪律落实：凭证用 `YOUR_CLIENT_ID` / `YOUR_CLIENT_SECRET` / `RECEIVED_CODE` / `<access_token>` / `asst_xxx` / `task_yyy`，未伪造真实票据或响应值。F 引用越界 0（全局去重 64 个编号，全部命中 facts.md）；端点、scope 名、字段名与 concepts/05-06 及白皮书 §8-§9 一致。`index.md` 无 frontmatter，toctree 收 00~06 + 场景导览表。机械验证：断链 0、BOM/CRLF 0、本机路径 0。

## Task 5: 根 index.md、log.md 与 references 收口
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `index.md`：OKF v0.2 frontmatter（`okf_version: "0.2"`、`status`、`stale_after: 2027-04-15`、sources 全列）、内容性质块（厂商白皮书 + 可照做接入指南，设 examples 的理由）、可信度状态块、「这束知识包讲什么」分层导读表、已知边界（五类口径 + 单源清单 + O1 未核验/附录 A 未取得 + 未实跑声明）、主题关联（同组既有束）、一句话结论、toctree（concepts/index、examples/index、references/index、log）。
  - `log.md`：初始版本条目，记录七阶段执行、口径决策、覆盖统计、并行在途观测、门禁运行方式与未运行 `invoke` 的声明、独立评审结论留位。
  - 收口 `references/index.md` 与各子目录 index 的 toctree 完整性。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 根 `index.md` 的 toctree 四条目（`concepts/index`、`examples/index`、`references/index`、`log`）对应文件全部存在；`okf_version` 仅出现在根 `index.md`，子文档不含。
  - `rule` TR-5.2: `log.md` 日期标题为 `YYYY-MM-DD` 倒序结构，内容含七阶段、覆盖章节数、口径决策、门禁方式四类信息。
  - `rubric` TR-5.3: 已知边界可决策性；scale 1-5；anchors 1=边界缺失或与正文矛盾/3=主要边界有但分散/5=集中声明且每条挂 F 编号，读者可直接判断「能接入什么 / 哪些是自宣口径 / 哪些以官网为准」；threshold >= 4。
- **Notes**: 「已知边界」需明确区分「官方未宣布」「未核验」「未取得」三种状态，不得把未取得写成不存在。
- **Completion Evidence**（2026-10-15）：根 `index.md` 建成——`okf_version: "0.2"` 仅出现在此文件；frontmatter 含 title/description/tags、`generated`/`verified`（`process:seven-concepts-*`）、`status: stable`、`stale_after: 2027-04-15` 与 4 条 `sources`（W0/P0/P1/O1）。正文含内容性质块（说明设 examples/ 的理由与本束未在本机实跑）、可信度状态块、**15 行分层导读表**（覆盖 11 篇 concepts + examples + references）、**「已知边界」11 条**（单源无第三方核验 / 市场数据转引未核验 / Skills 数量不一致 / 发行日期 vs 发布日时序矛盾 / 接口以官网为准 / 官网未核验 / 附录 A 未取得 / 匿名化场景不反推 / 商务数字框架性参考 / 未在本机实跑 / 获取路径说明）、**「主题关联」8 束互链**（workbuddy-official-docs、workbuddy-open-platform-sharing-and-promotion、workbuddy-one-sentence-mvp、workbuddy-sandbox-public-endpoint、tencent-buddy-family、wecom-5-0-12-release、codebuddy、octop）、一句话结论；toctree 四条目（`concepts/index`、`examples/index`、`references/index`、`log`）对应文件全部存在。`log.md` 建成，`YYYY-MM-DD` 日期标题倒序结构，含七阶段执行、口径决策、覆盖统计、门禁方式与并行观测。`references/index.md` toctree 收三件。全束共 **26 个 Markdown**（根 2 + concepts 12 + examples 8 + references 4），机械校验零 BOM、零 CRLF、零断链。

## Task 6: 五级索引接入、计数复算与同组互链
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `tencent/index.md`：导航表 +1 行、toctree +1 条、「关于本分组」段追加本束说明与生成来源、「相关链接」+1 行；束数与概念/示例/信源/事实计数按机械真值复算。
  - `ecosystems/index.md`（腾讯生态行与类计数）、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`（`total_bundles`、正文计数行、mermaid `jishu` 节点、节标题、分组表 ai 行）逐层同步。
  - 同组互链：新束 `index.md`「主题关联」链既有束；如需反向链接，限单行最小改动（`git diff` 核对）。
  - 机械复算：自包含脚本按 marker 目录（concepts/examples/references）+ 锚点束=1 口径清点 tencent/ai/jishu 三级真值，与 `check-bundles-index.py` 输出对齐；临时脚本用后删除。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-6.1: `python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0、五面一致；输出计数与写入索引的数字逐项相等。
  - `rule` TR-6.2: `python scripts/check-toctrees.py` 全量输出过滤 `workbuddy-hardware-integration-whitepaper` 零命中；既有/并行污染项只在 `log.md` 列名披露，不顺手修复。
  - `rule` TR-6.3: 若回补既有束反向链接，其 `git diff` 恰为 +1 条互链，事实、计数、正文其他部分零改动；新束 `index.md`「主题关联」含对应链接。
- **Notes**: 若观察并行会话实时改写总索引，以最后一次无写入窗口的脚本输出为准并在 log 记录观测事实。
- **Completion Evidence**（2026-10-15）：`python scripts/check-bundles-index.py` **终采通过** ——「9 域 / 61 组 / **638 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致」，退出码 0。五级索引全部接入：`tencent/index.md`（导航表 +1 行、toctree +1 条、相关链接 +1 行、「关于本分组」15→**16** 束 / 113→**124** 概念 / 36→**43** 示例 / 68→**72** 信源 / 2203→**2393** 事实 + 本束生成说明段）→ `ecosystems/index.md`（类总 91→**92**、腾讯行 15→**16**）→ `jishu/ai/index.md`（frontmatter description 与正文 243→**244**、ecosystems 行 91→**92**）→ `jishu/index.md`（ai 行简介 243→**244**）→ `doc/bundles/index.md`（`total_bundles` 637→**638**、正文计数行 637→**638**、mermaid `jishu` 节点 472→**473**、节标题 472→**473**、分组表 ai 行 243→**244**）。本束计数按机械真值复算：束 1（锚点）、概念 11、示例 7、信源 4（frontmatter W0/P0/P1/O1）、事实 190。`check-toctrees.py` 全量输出过滤 `workbuddy-hardware-integration-whitepaper` **零命中**；并行在途束 `sheke/industry/workbuddy-opc-whitepaper` 的 5 处 toctree 问题（缺根 index.md、references 三件不可达、toctree 引用不存在的 verification）按归属隔离**只披露不修复**，已记入本束 `log.md`。同组互链：本束 `index.md`「主题关联」链 8 束；未对既有束做任何反向修改（无 git diff 变更）。

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
- **Completion Evidence**（2026-10-15）：**四道门禁全绿**。① `python scripts/check-utf8.py` 通过（**11640 个文件**均为有效 UTF-8）；② `python scripts/check-toctrees.py` 全量输出过滤 `workbuddy-hardware-integration-whitepaper` **零命中**（既有/并行污染仅属 `sheke/industry/workbuddy-opc-whitepaper`，已隔离披露）；③ `python scripts/check-bundles-index.py` 通过（**638 束**，五面一致，退出码 0）；④ **定向 Sphinx dummy 构建**（Sphinx 8.2.3 + myst_parser 5.1.0，`-b dummy -E -D exclude_patterns=<非 jishu 域>`）：`build succeeded`，本束 **26 篇全部被读入与写出**，过滤提到本束名的行**全部为进度行、WARNING 提及本束数 = 0**；构建产物 `_build/dummy-t`（及被中止的全量构建产物 `_build/dummy`）已删除。
  **束内自包含校验（脚本）**：26 个 Markdown —— `file:///` 与 `C:\Users` 本机路径 **0**；全部 Markdown 相对链接与所有 `{toctree}` 条目 **0 断链**；非保留文件 frontmatter 的 `type`/`generated`/`verified`/`status`/`stale_after`/`sources` 齐备且 `okf_version` **仅出现在根 `index.md`**；BOM **0**、CRLF **0**；**F 编号双份比对 `facts.md` 190 行 = `article-source.md` 190 行且集合相等、连续 1..190**；concepts + examples + references 中全部 `F-\d{3}` 引用**越界 0**（无编造编号）。
  **TR 抽查证据**：五类口径标签计数——`厂商自宣口径` 25 / `第三方数据` 10 / `匿名化场景` 10 / `商务框架性参考` 21 / `以官网为准` 23（`未核验` 30、`未取得` 28）；7 篇 examples 的「前置条件 / 操作步骤 / 结果判据 / 限制与边界 / 未在本机实跑」五段标记**全部为 True**。
  四视角对抗审查表（魔鬼代言人 / 新人 / 业务方 / 未来维护者，每视角含具体攻击点与处置）已落在 `references/verification.md`。

## Task 8: 独立上下文评审 R1 与收尾
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 队列清空后新建 `review.md`（CP-R1~R6 规则检查点 + CP-U1/U2 量规，覆盖 AC-1~AC-6）。
  - 委派 fresh-context 只读子代理执行独立评审（提供绝对路径、运行命令与评审合同：全章覆盖、F 编号双份、五类口径分层、链接与编码门禁、五级计数一致、同组互链、examples 未实跑标注）。
  - 结果路由：`pass` 则写 Review History 并向用户汇报、给出 C 阶段提交方案供决策；`fail` 则把可行动发现固化为 pending 修复 issue 回 Implement，回归后开新 R2；`blocked` 则记录阻塞并请求解决。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: `review.md` 每个 AC 至少被一个检查点覆盖；R1 结果为 `pass`（若 `fail` 必有非空 pending 修复队列且回归后开 R2）。
  - `rubric` TR-8.2: 评审独立性与证据质量；scale 1-5；anchors 1=主会话自审冒充/3=独立评审但证据笼统/5=fresh 子代理逐检查点给出命令/文件证据与评分并独立复核页面；threshold >= 4。
- **Notes**: 不执行 git commit；评审通过后在汇报中给出 C 阶段提交方案（子模块 → 主仓 spec → 子模块指针，显式文件列表）供用户决策。
- **Completion Evidence**（2026-10-15）：`review.md` 建成（CP-R1~R6 规则检查点 + CP-U1/U2 量规，覆盖 AC-1~AC-6）；委派 **fresh-context 只读子代理**执行独立评审——该代理独立运行三条门禁脚本并自行复算 F 编号双份集合、引用越界、链接与 toctree 可达性、frontmatter 字段与 `okf_version` 位置、BOM/CRLF，逐篇抽查 concepts 00/02/04/05/07 与 examples 00/01/06，**全程未修改任何文件**。**结果为 `pass`**：6 个 rule 检查点**全部 PASS**，CP-U1 = **5/5**、CP-U2 = **5/5**（均 ≥ 阈值 4），**无可行动发现（0 条 P0/P1）**。评审提出 1 条 P2 建议性发现（`log.md` 叙述中**字面**含 `file:///` 与 `C:\Users` 可能被机械 grep 误判）——**已当场收口**：改写为「绝对协议引用（file 协议）与用户目录本机路径 **0**」并复跑束内校验确认 `bad paths = []`。评审并复核了并行在途束 `sheke/industry/workbuddy-opc-whitepaper` 造成的全库 toctree/计数漂移，确认**与本束无关**且已在 `log.md` 归属隔离披露。队列清空、无遗留可行动项。**未执行任何 git 提交**；C 阶段提交方案随交付汇报提交用户决策。

## 依赖关系

- Task 2 依赖 Task 1（无台账无法登记事实归属）。
- Task 3 依赖 Task 2（concepts 的 F 引用须先有编号事实）。
- Task 4 依赖 Task 3（examples 的接口口径与 concepts 一致）。
- Task 5 依赖 Task 4（根索引导读表需覆盖全部篇目）。
- Task 6 依赖 Task 5（计数复算需文件集合已固定）。
- Task 7 依赖 Task 6（门禁需索引已写入）。
- Task 8 依赖 Task 7（评审以队列清空为前置）。
- 无并行可并行的任务：Task 6 的机械复算与 Task 7 的门禁须串行，避免写读冲突。

## 批准门

本规格与任务计划已提交用户审查，**获得显式批准前不进入实施**。批准范围不含：在 WorkBuddy 开放平台注册应用或申请真实凭证、调用真实接口、提交真实上架审核、修改同组既有束事实、执行 git commit/push。实施前须先检查 `projects/awesome-okf-xs/` 子模块无 merge/rebase 进行中。
