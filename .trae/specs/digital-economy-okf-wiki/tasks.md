# 数字经济与数字资产 OKF 教程束 - Implementation Plan

> 方法论：seven-concepts 场景 4（R→I→E→V→C）+ Spec Mode 五阶段。
> 目标路径：`projects/awesome-okf-xs/doc/bundles/sheke/digital-economy/`（分组 1 + 束 2×20 = 41 文件）。
> 门禁一律在 `projects/awesome-okf-xs` 工作目录下运行；本轮不执行 git commit。

## Task 1: R 阶段事实采集（四路并行只读子代理）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 启动 4 个只读子代理按主题分区公开调研，各自回收带信源编号的原始事实草案：
    - R-A 定义与测度：G20/OECD 定义演化、国家统计局《数字经济及其核心产业统计分类（2021）》四大类、中国信通院核算框架（数字产业化/产业数字化/数字化治理/数据价值化）、国际口径（OECD/IMF/UNCTAD）。
    - R-B 产业结构与规模：数字产业化核心产业（电子信息制造·软件与信息服务·电信·互联网）、产业数字化（工业互联网·智能制造·农业与服务业数字化）、平台经济与双边市场、规模与占 GDP 比重数据（逐年）。
    - R-C 数据要素与数据资产：数据要素理论依据、"数据二十条"三权分置、《"数据要素×"三年行动计划》、财政部《企业数据资源相关会计处理暂行规定》（财会〔2023〕11 号，2024-01-01 施行）、数据交易所（上海/深圳/北京/贵阳）、公共数据授权运营、数据安全法与个人信息保护法边界。
    - R-D 加密资产与监管：比特币/以太坊与底层机制、稳定币机制与储备争议、数字人民币（e-CNY）定位与双层运营、NFT/数字藏品中国合规红线、RWA 与 DeFi、中国境内监管公告（2017-09-04 七部门公告、2021 年进一步防范通知）、香港《稳定币条例》、欧盟 MiCA、美国相关立法。
  - 回收产物：原始事实行（含出处链接与关键逐字引文）+ 待核验清单 + 口径冲突清单（移交 I 阶段）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 每条原始事实含信源编号、发布机构、文件名/文号或报告名、日期与可访问链接；无法访问者标记 ⚠️ 并注明替代信源。
  - `rule` TR-1.2: 规模/政策/法规类事实每条 ≥2 个独立出处（官方为主），单一出处者标记「单源」并说明。
  - `rule` TR-1.3: 四类口径冲突（测度三口径、加密监管四方分歧、稳定币储备、数字经济占比年际差异）在回收清单中独立成段。
- **Completion Evidence**:
  - 四路只读子代理草案已落盘 `.trae/specs/digital-economy-okf-wiki/raw/`：R-A 定义与测度（52 条事实 / 34 信源 / 6 冲突）、R-B 产业结构与规模（58 条 / 38 信源 / 6 冲突）、R-C 数据要素与入表（56 条 / 42 信源 / 7 冲突）、R-D 加密资产与监管（60 条 / 37 信源 / 7 项法域分歧），合计 **226 条原始事实、151 个信源**。
  - 关键勘误已回收入库：文号更正为「**国家统计局令第 33 号**」（原假设「国统字〔2021〕33号」有误）；三协会 NFT 倡议实为 **2022-04-13**（原假设 2021-04 已证伪）；MiCA 三时点（2023-06-29 生效 / 2024-06-30 ART·EMT / 2024-12-30 全面）；2021 年 237 号通知成文 09-15、公开 09-24；中评协〔2023〕17 号 2023-10-01 施行。
  - TR-1.1/1.2/1.3 均满足：每事实带机构、文件名/文号、日期与链接；规模与政策类双源核对；四类口径冲突独立成段（测度三口径、监管四方分歧、稳定币市值时点、核心产业占比 10.5%/10.4%/「10% 左右」）。

## Task 2: I 阶段洞察冻结

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 写两束 `insights.md`（`type: Insights`），每束 6 条四元组洞察（现象 / 根因 / 影响 / 建议），并给出该束的知识地图。
  - 束 1 洞察候选：口径多重→数字不可直接横比·「数字经济=新经济」语义漂移·统计分类滞后于业态·平台经济的双边外部性·产业化与数字化两条路径的非对称·数据要素市场化先于确权完备。
  - 束 2 洞察候选：术语「数字资产」三个口径混用·数据入表≠估值增值·加密资产与数字人民币的本质分野·稳定币的货币属性与监管套利·NFT 在中国的合规收缩·代币化的制度红利与风险同源。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-2.1: 每条洞察四元组字段齐全，且引用 ≥3 个 F 编号事实（F 编号在 Task 3 落盘前允许以草案编号引用，Task 3 定稿后回填）。
  - `rule` TR-2.2: 四类口径冲突在洞察或 facts 勘误段中有裁决位。
- **Completion Evidence**:
  - 束 1 `digital-economy/insights.md`：I-1 口径多重致数字不可横比、I-2 近义概念谱系无统一边界、I-3 统计分类建制化与滞后性并存、I-4 核心产业与数字经济两级常被混用、I-5 平台双边外部性超出传统工具、I-6 产业数字化占八成而官方可测口径只覆盖两成；每条四元组齐全并引用 6–9 个 F 编号，附知识地图与阅读落点。
  - 束 2 `digital-asset/insights.md`：I-1「数字资产」三口径混用、I-2 三权分置是政策创设非法律权利、I-3 会计「可入表」被误读为资产增值、I-4 数据交易场外主导与测算口径、I-5 稳定币是货币属性与监管套利复合体、I-6 代币化制度红利与风险同源且结论由法域决定；每条四元组齐全并引用 6–12 个 F 编号。
  - TR-2.2 满足：四类口径冲突在两束 facts.md 的「口径冲突与勘误」段独立成段留痕。

## Task 3: E-0 facts.md 定稿 + references 信源台账 + 两个子目录索引

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 两束各写 `facts.md`（`type: Facts`，`F-001` 起 ≥50 条，分 6–7 个主题小节，关键条目标【P0】，文末含 S1–Sn 信源登记表 ≥15 项与「放弃核验清单」，口径冲突独立成段）。
  - 两束各写 `references/01-sources-and-authorities.md`（中国官方 / 国际权威 / 学术与行业三层台账）。
  - 两束各写 `concepts/index.md` 与 `examples/index.md`（无 frontmatter，纯表格 + 阅读建议 + `{toctree}`，其 `{toctree}` 需完整覆盖后续 Task 4/5/6 落盘的篇目）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: F 编号连续无跳号，每条含 S 编号；S 台账每项含机构、文件名/文号、日期、链接。
  - `rubric` TR-3.2: 可审计性（分组清晰度 / 编号连续性 / 信源可验证性 / 口径备注完整性）；1–5；阈值 ≥4。
- **Completion Evidence**:
  - 束 1 `digital-economy/facts.md`：**82 条** F 编号事实（7 组：概念与定义谱系 15、测度框架 13、数字产业化 14、产业数字化 13、平台经济 7、规模与结构 15、治理与制度 5），P0 标记 42 条；S1–S43 信源登记表；7 项口径冲突与勘误独立成段；9 条放弃核验清单。
  - 束 2 `digital-asset/facts.md`：**90 条** F 编号事实（9 组：概念谱系 7、数据要素与确权 14、数据入表与评估 14、数据交易 11、加密资产 9、稳定币与境外监管 10、e-CNY 6、NFT/RWA/DeFi 7、境内监管红线 11），P0 标记 56 条；S1–S64 信源登记表；7 项勘误（含四方监管定性对照表与「已证伪常见误记」表）独立成段；10 条信源保真声明与放弃核验清单。
  - `references/01-sources-and-authorities.md` × 2 已落盘，按「中国官方 / 国际权威 / 学术与行业 + 技术与标准」三层组织，含引用纪律与机构测算值清单。
  - `concepts/index.md` 与 `examples/index.md` × 2 已落盘（无 frontmatter，纯表格 + 阅读建议 + `{toctree}`，toctree 覆盖全部 26 篇后续内容文件）。
  - TR-3.1 满足：F 编号连续无跳号（束 1 F-001~F-082；束 2 F-001~F-090），每条含 S 编号；S 台账每项含机构、文件名/文号、日期、链接。

## Task 4: E-1 束 1 concepts 10 篇（数字经济）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 写 `sheke/digital-economy/digital-economy/concepts/00`–`09`：
    00 定位与阅读路径 / 01 概念谱系与定义演化（含与信息经济·网络经济·知识经济·智能经济的辨析）/ 02 测度框架与统计口径（信通院四化框架·国家统计局分类·OECD-IMF 口径与不可比性）/ 03 数字产业化：核心产业构成 / 04 产业数字化：三次产业转型路径 / 05 数据要素与数据价值化（理论依据与制度框架）/ 06 平台经济与数字市场结构（双边市场·网络效应·治理与竞争）/ 07 规模与结构数据（逐年官方发布值与国际比较，口径分层标注）/ 08 数字治理与制度（数据安全法·个人信息保护法·跨境流动·数字中国规划）/ 09 争议与边界（统计口径争议·生产率悖论·AI 时代的重定义）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 每篇 frontmatter 完整（`type: Concept` 或同类 + `title`/`description`/`tags`/`sources`/`generated`/`status`/`stale_after`）、正文只用 `##`、结尾含束内 `/`-根导航段。
  - `rule` TR-4.2: 07 篇所有规模数字标注口径来源（官方发布 / 机构估算 / 第三方测算）；02 篇含三口径对照表。
  - `rubric` TR-4.3: 单篇教学质量（是什么 / 为什么重要 / 制度与数据现状 / 边界与争议）；1–5；阈值 ≥4。
- **Completion Evidence**:
  - 10 篇概念文件已落盘 `digital-economy/concepts/`（00-positioning-and-reading-path … 09-controversies-and-boundaries），文件名与 `concepts/index.md` 的 toctree 完全一致；单篇中文字数 1325–1975。
  - TR-4.1 满足：每篇 frontmatter 含 `type: Concept` + `title`/`description`/`tags`/`sources`/`generated`/`status`/`stale_after`；每篇恰 1 个 H1；每篇结尾含「相关文档」束内 `/`-根导航段。
  - TR-4.2 满足：`02-measurement-framework.md` 含三口径对照表（国家统计局核心产业口径 / 国家统计局更宽口径 33.1% / 信通院广义口径，含发布机构、口径名称、统计时点、2024 年数值与可否混用列）；`07-scale-and-structure.md` 全部规模数字标注口径来源（官方发布值 / 机构估算值 / 第三方测算值）。
  - 引用覆盖：00 F-003/016/017/019/020/022/033/035/063/065/070/080；01 F-001~F-015；02 F-006/014~028/035/065/070/072/073/082；03 F-015~019/029~042；04 F-017/019/020/022/033/035/043~055/064/065/067/075；05 F-001~003/018/020/022/055/080/081；06 F-056~F-062/075；07 规模相关组；08 F-033/035/055/063/065/070~082；09 F-011/014~020/022/028/033/035/043/044/046~048/053/064/065/067/071~073/082。
  - 事实边界处理：05 篇将「数据价值化环节」按 facts.md F-020 原文如实呈现并标注系信通院测算框架；07 篇逐年序列仅列 2023/2024 两期官方值 + 「十四五」起点 6.8%，未编造缺失年份。
  - 链接修正：子代理初稿将跨束链接写为 `../digital-asset/index.md`（层级偏浅）；已统一修正为 `../../digital-asset/index.md`（自 `concepts/` 与 `examples/` 目录正确解析）。

## Task 5: E-2 束 2 concepts 10 篇（数字资产）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 写 `sheke/digital-economy/digital-asset/concepts/00`–`09`：
    00 概念定位与谱系（「数字资产」三类口径辨析：数据资产 / 加密资产 / 广义数字化资产）/ 01 数据资产与入表（数据资源→数据资产→数据资本，财会〔2023〕11 号入表条件与计量）/ 02 数据确权与三权分置（持有权·加工使用权·产品经营权，确权难点）/ 03 数据交易与市场（场内场外·交易所·定价方法·公共数据授权运营）/ 04 加密资产总览（比特币与以太坊·底层机制·市值与周期·与法定货币的区别）/ 05 稳定币（机制·储备与脱锚事件·香港稳定币条例·美国立法·欧盟 MiCA）/ 06 数字人民币 e-CNY（M0 定位·双层运营·与支付工具及稳定币的区别·跨境试点）/ 07 NFT 与数字藏品（技术标准·中国合规红线与平台现状）/ 08 RWA 与 DeFi（代币化机制·风险结构·境外监管路径）/ 09 风险与合规红线（中国境内监管公告逐条·非法金融活动识别·税务与会计·投资者保护与免责边界）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 每篇 frontmatter 完整、正文只用 `##`、结尾含束内 `/`-根导航段。
  - `rule` TR-5.2: 09 篇逐条登记中国境内监管文件的发布机构、文号与日期；06 篇明确辨析 e-CNY 与加密货币/稳定币的三点区别；05/08 篇境外口径与中国境内口径并列不混同。
  - `rule` TR-5.3: 全束 0 处产品/平台/币种推荐性表述。
  - `rubric` TR-5.4: 单篇教学质量；1–5；阈值 ≥4。
- **Completion Evidence**:
  - 10 篇概念文件已落盘 `digital-asset/concepts/`（00-positioning-and-lineage … 09-risks-and-redlines），文件名与 `concepts/index.md` 的 toctree 完全一致；单篇中文字数 1245–2423。
  - TR-5.1 满足：frontmatter 含 `type: Concept` 全套字段；每篇恰 1 个 H1；每篇结尾含「相关文档」束内 `/`-根导航段。
  - TR-5.2 满足：`09-risks-and-redlines.md` 含**中国境内监管文件逐条登记表**（文件名 + 文号 + 机构 + 日期 + 关键定性：银发〔2013〕289 号、2017-09-04 七部门公告（无文号）、银发〔2021〕237 号、发改运行〔2021〕1283 号、2021-05-18 三协会公告、2021-05-21 金融委会议）与**四方监管口径对照表**（中国境内/香港/欧盟/美国 × 法律定性/准入/稳定币/挖矿/NFT/RWA/CBDC）及免责声明；`06-ecny-digital-yuan.md` 含 e-CNY 与加密货币、稳定币、第三方支付的三组辨析；`05-stablecoins.md`/`08-rwa-and-defi.md` 境外口径与境内口径并列不混同。
  - TR-5.3 满足：全束 0 处产品/平台/币种推荐性表述（扫描命中的「推荐」均为否定式或免责句）。
  - 引用覆盖：00 F-001~082；01 F-022~035；02 F-008~047；03 F-014~047；04 F-003~061；05 F-007~090；06 F-005~072；07 F-073~088；08 F-073~084；09 F-005~090；勘误 1/2/3/5/6/7 均在相关篇目引用。
  - 事实边界处理：04 篇按 facts.md 信源保真声明，以 BIS「无许可区块链」表述为限说明机制，未采用市场白皮书式定义；「无存款保险」「价格无锚」改用 FATF 与央行口径间接论证。

## Task 6: E-3 两束 examples 各 3 篇

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 束 1 examples：01 数字经济规模数据核对演练（同一指标多口径对照与读法）；02 某行业数字化转型路径走读（教学案例，标注教学假设）；03 数字经济发展报告阅读清单（读什么、先看哪张表）。
  - 束 2 examples：01 企业数据资源入表会计处理算例（教学算例，非实务意见）；02 加密资产风险自检清单（识别红旗 + 官方核验渠道）；03 数字资产监管口径对照表（中/港/欧/美四方并列，含适用主体与合规后果）。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-6.1: 每个数字/机制可回链 `facts.md` 的 F 编号；示例不引入 F 编号之外的新主张。
  - `rule` TR-6.2: 算例数字标注「教学算例」；对照表含「本表不构成合规意见」声明。
  - `rubric` TR-6.3: 可独立走读；1–5；阈值 ≥4。
- **Completion Evidence**:
  - 6 篇示例已落盘：数字经济束 `examples/01-reading-scale-datasets.md`（1137 字）、`02-industry-digitalization-walkthrough.md`（1242 字）、`03-report-reading-checklist.md`（1117 字）；数字资产束 `01-data-capitalization-worked-example.md`（1560 字）、`02-crypto-risk-self-check.md`（1344 字）、`03-jurisdiction-comparison-table.md`（1056 字）。
  - TR-6.1 满足：所有数字与制度表述均以本束 F 编号括注（经束引用 F-017~F-081，资束引用 F-003~F-090），无跨束串号；教学假设数字显式标注「教学假设/教学算例」。
  - TR-6.2 满足：入表算例全篇标注「教学算例，不构成会计实务意见」；监管口径对照表含「本表不构成合规意见」声明。
  - 工程纪律：6 篇均 `type: Example`、frontmatter 完整、恰 1 个 H1、无 `file:///`、无 emoji、含结尾导航段；数字资产束示例 0 处推荐性表述。

## Task 7: 束根 index/log + 三级索引注册

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6
- **Description**:
  - 两束各写根 `index.md`（快速导航 / 快速开始 / 知识包立场表 / 推荐学习路径 / `{toctree}`，frontmatter 见 NFR-3；含通识教育与不构成投资建议声明）。
  - 两束各写 `log.md`（`YYYY-MM-DD` 倒序记录 R→V 全程）。
  - 写分组 `sheke/digital-economy/index.md`（frontmatter `type: group` + `total_bundles: 2` + 导航表 + `{toctree}`）。
  - 更新 `sheke/index.md`（描述、新增方向条目、分组导航表行、`{toctree}`）。
  - 更新 `doc/bundles/index.md`：frontmatter `total_bundles` 641→643、`groups` 61→62；正文计数行；sheke 域节标题「69 束 · 8 组」→「71 束 · 9 组」；sheke 分组表新增一行（束数 2）；同步 sheke 生态概览 mermaid 节点文字与域描述中的主题清单。
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: `python scripts/check-bundles-index.py` rc=0（五面对账一致）。
  - `rule` TR-7.2: `python scripts/check-toctrees.py` 与 `python scripts/check-utf8.py` rc=0，本分组 0 红名、0 孤立文档。
  - `rule` TR-7.3: `sphinx-build -b dummy -E doc _build/dummy` rc=0 且无本分组来源的警告。
- **Completion Evidence**:
  - 41 个文件全部落盘（分组 index 1 + 两束各 20）；两束根 `index.md` 含「快速导航 / 快速开始 / 知识包立场表 / 推荐学习路径」与 `{toctree}`，两束 `log.md` 以 `2026-10-17` 倒序记录 R→E→V 全程。
  - 分组 `sheke/digital-economy/index.md` 落盘（`type: group` + `total_bundles: 2` + 导航表 + toctree + 信任声明）。
  - **TR-7.1 满足**：`python scripts/check-bundles-index.py` rc=0 → 「bundles 总索引对账通过: 9 域 / 62 组 / 644 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。」
  - **TR-7.2 满足**：`python scripts/check-toctrees.py` rc=0 → 「toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。」；`python scripts/check-utf8.py` rc=0 → 「UTF-8 检查通过: 11751 个文件均为有效 UTF-8。」
  - **TR-7.3 满足**：`sphinx-build -b dummy doc _build/dummy` rc=0 → 「build succeeded, **30 warnings**」；机械统计 WARNING 行的归属目录为 `jishu` 30 / `wenxue` 1，**来自 `sheke/digital-economy` 的 WARNING 数 = 0**；构建日志中本分组 41 个文档均出现在「正在读取源文件 / 正在写入输出」进度中（82 行命中），证明本分组被完整解析与渲染。
  - 索引改动落点：`doc/bundles/index.md`（frontmatter 644/62、计数行、sheke 节标题「72 束 · 9 组」、分组表新增 1 行束数 2、mermaid 生态节点 72 束 + 主题清单）、`doc/bundles/sheke/index.md`（frontmatter description、方向条目、分组导航表行、toctree）。
  - **计数基线说明**：实施期间并行会话在 `sheke/industry` 组新增 1 束（基线 641→642），本变更在其上 +2 束 +1 组，最终以目录树地面真值为准（644/62），已同步记入 spec.md Goals。

## Task 8: V 门 fresh-context 独立验证

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 全新只读子代理执行：G1 结构核对（41 文件清单与 toctree 可达性）、G2 符号/数字抽核（覆盖率 ≥10% 且每概念页 ≥2 条，P0 虚构 = 0）、G3 计数复核（F 编号连续性、S 台账条目数、总索引计数三角）、G4 链接枚举 + 三门禁 rc 复跑、G5 Sphinx dummy。
  - 发现的问题修复后复扫；回填各内容文件 `verified` 与束内 `log.md`。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: 抽核命中率 ≥98%、P0 = 0；门禁与 dummy 输出留痕。
  - `rule` TR-8.2: G1–G5 全过后回填 `verified`；0 处遗留红名。
- **Completion Evidence**:
  - V 门由**全新上下文的只读子代理**执行（未参与撰写），结果：**G1 结构 PASS、G2 事实抽核 PASS（命中率 100%，抽样 82+90 条全量比对，P0 虚构 = 0）、G3 计数复核 PASS（独立枚举器重算 9 域/62 组/644 束、sheke 72 束/9 组，五面一致）、G4 门禁 PASS（三门禁 rc 全 0），G4 链接枚举 FAIL（1 条断链）**。
  - G2 重点核实项 18 类（国家统计局令第 33 号、140891 亿元/10.5%、127555 亿元/9.9%、126 个行业小类、5 大类 32 中类 156 小类、财会〔2023〕11 号与 2024-01-01 施行、中评协〔2023〕17 号与 2023-10-01 施行、银发〔2013〕289 号、银发〔2021〕237 号（09-15 成文 / 09-24 公开）、发改运行〔2021〕1283 号、三协会 NFT 倡议 2022-04-13、香港《稳定币条例》2025-05-21 通过 / 2025-08-01 生效、GENIUS Act 2025-07-18 与 PL 119-27、MiCA 三时点、比特币白皮书 2008-10-31、以太坊 2015-07-30、ERC-721 2018-01-24、ERC-1155 2018-06-17）**全部与 raw 草案一致**。
  - V 门发现 9 项（P0 1 项 / P1 4 项 / P2 4 项），已全部固化进 Task 10 修复队列；`verified` 字段随后回填 30 个内容文件（30/30 命中，禁用清单 0 命中）。
  - TR-8.1 满足（抽核 ≥98%、P0 = 0、门禁输出留痕）；TR-8.2 满足（G1–G5 全过后回填 `verified`，1 条断链修复后归零）。

## Task 9: C 门 fresh-context 独立评审与收口

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 另一全新只读子代理独立评审（自读 spec/tasks、自跑门禁、自写枚举器），按 AC-1–AC-7 逐条给出证据并写 `.trae/specs/digital-economy-okf-wiki/review.md`；`fail` 则把每条可行动发现固化为 pending issue → 回 Implement 修复 → 新审查者复审至 `pass`。
  - 收口：汇报产出清单、门禁证据与遗留风险；**不 commit**，等待用户显式指令。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-9.1: `review.md` 每条 AC 有独立证据，终态 Result = pass。
  - `rubric` TR-9.2: AC-4 教学质量独立评分 ≥4，并给出维度理由。
- **Completion Evidence**:
  - **评审轮次**：R1（首轮 reviewer，全新上下文）结论 `fail` → 发现 F-1~F-5 全部固化进 Task 10 并修复 → **R2（另一全新上下文 reviewer）独立复审结论 `pass`**。
  - **R1 独立重算证据**：172 条事实与 `raw/` 草案全量比对 0 处数字/文号/日期不一致；自写递归枚举器重算 9 域/62 组/644 束、sheke 72 束/9 组，五面对齐；三门禁 rc=0；409 条链接（首轮 1 条断链）；`推荐` 命中 15 行逐行核验全为否定式，0 处推荐性表述。
  - **R2 独立重算证据**：文件 **41**；F 段束 1 **F-001~F-082（82）**、束 2 **F-001~F-090（90）**，无跳号无重复；S 段束 1 **S1–S43（43）**、束 2 **S1–S63（63）**，无缺号；P0 = **42 / 56**；链接 **409 条（`/`-根 242 + 相对 167），断链 0、越界 0**，`file:///`＝`.temp/`＝`.spec/`＝0；**信源标注命中率 = 170/172 = 98.84% ≥ 98%，P0 级错引 = 0**；三门禁 rc=0；`_build/build_dummy.log` 含 `build succeeded, 30 warnings.`，30 条警告全属 `jishu`，**本分组 0 条**。
  - **AC 逐条终态**：AC-1 pass、AC-2 pass、AC-3 pass、AC-4 pass、AC-5 pass（4/4 项满足、0 推荐性表述）、AC-6 pass（0 违例）、AC-7 pass。**TR-9.1 满足（`review.md` 终态 Result = pass 且每条 AC 附独立证据）**。
  - **TR-9.2 满足**：AC-4 独立评分 **19/20（均分 4.75）**——概念定义清晰度 5 / 知识地图连贯性 5 / 跨篇导航有效性 5 / 非专业读者可跟读 4（扣分点为加密侧制度门槛与四方对照表信息密度）。
  - **advisory 发现（非阻塞；A-1 已按用户指令于收口后修复）**：
    - **A-1 已修复（2026-10-17，用户指令）**：`digital-asset/facts.md` 的 F-011、F-013 原标 S2（刘鹤 2019 署名文章）而内容出自「国家发展改革委答记者问」——现新增信源 **S64**（国家发展改革委《构建数据基础制度 更好发挥数据要素作用——国家发展改革委负责同志答记者问》2022-12-19，链接 `https://www.ndrc.gov.cn/xxgk/jd/jd/202212/t20221219_1343696_ext.html`），F-011、F-013 信源改挂 **S64**；F-013 正文补注「该表述出自官方解读口径而非《意见》条文原文」；S 台账由 S1–S63 扩为 **S1–S64**，同步 facts.md 说明段与登记表标题、references 的 description / 信源计数 / 分层标题、bundle index 两处、log.md、concepts/00、concepts/index.md、tasks.md 全部 S 范围表述；顺带修正 facts.md 说明段的三层信源区间（①中国官方 S1–S39、S63、S64 / ②国际组织 S40–S58 / ③技术与标准 S59–S62），使其与 references 分层一致（原「①S1–S38 / ②S39–S58」与台账冲突，即 A-4 的一半）。
    - **A-2～A-4（仍为 backlog）**：A-2 若干条使用「Sxx（相关：…）」披露式替代信源（已披露、可溯源，非缺陷）；A-3 S48 登记但无事实引用，可标「背景信源」；A-4 余下的表述粒度差异不影响可审计性。
    - **R3（第三轮复审）新出的两条 advisory 已按用户指令修复（2026-10-17）**：
      - **A-6**：`digital-asset/facts.md` F-010 原标 `S1、S2`，而 raw 的 C-05 信源为 `S-C01（+ S-C04）`——第二信源更正为 **S64**（发改委答记者问），现为 `S1、S64`；
      - **A-7**：`digital-economy/index.md` 正文「82 条事实、41 个信源」的信源计数与同文件 S1–S43 及 `references`（43 个）不一致——更正为「43 个信源」；同步全组扫描确认再无同类计数残留。
  - **收口状态**：不执行 git commit（`awesome-okf-xs` 为第一方 git submodule，提交待用户显式指令）；不修改子项目 `.agents/`、`tasks/`、`scripts/`、`doc/conf.py`。

## Task 10: V 门发现修复队列（P0/P1/P2）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 固化 V 门（fresh-context 只读子代理）的 9 项发现并逐项修复：P0-1 断链、P1-2 facts.md 描述计数、P1-3 F-005/F-054 信源错引、P1-4 `verified` 未回填、P1-5 AC-6 跨束链接判据、P2-6 信源折叠与同链接两用、P2-7 自链锚文本不符、P2-8 P0 计数失真、P2-9 总索引计数基线漂移。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-10.1: 每条发现均有对应修复落点（文件 + 位置），P0/P1/P2 全清。
  - `rule` TR-10.2: 修复后重跑三门禁与全量链接枚举：0 断链、0 向上越界、门禁 rc=0。
- **Completion Evidence**:
  - **P0-1 断链已修**：`digital-asset/references/01-sources-and-authorities.md:101` 的 `[04 加密资产基础](concepts/04-crypto-assets-basics.md)` 改为 `../concepts/04-crypto-assets-basics.md`（原缺 `../`，自 `references/` 目录无法解析）。
  - **P1-2 计数已修**：`digital-economy/facts.md` description「7 组 66 条」→「7 组 82 条」；`digital-asset/facts.md` description「9 组 80 条」→「9 组 90 条」。
  - **P1-3 信源错引已修**：`digital-asset/facts.md` F-005 信源 S29（挖矿通知，不含该定性）→ `S26、S30`（2013 年五部门通知 + 三协会公告）；F-054 信源 `S47、S29` → `S47、S30`。
  - **P1-4 `verified` 已回填**：两束 30 个内容文件（26 篇 concepts/examples + 2 facts.md + 2 insights.md）统一插入 `verified: [{ by: "process:okf-v-gate", at: "2026-10-17T19:50:00+08:00" }]`；机械自检 `grep` 命中 30/30，禁用清单文件（index/log/子目录 index/references）0 命中。
  - **P1-5 判据澄清已落**：spec.md AC-6 增补「跨束引用澄清（2026-10-17 V 门澄清）」——`../` 相对链接允许存在，但须解析到 `doc/bundles/` 内真实文件、禁止越界；判据依据为样板束 `sheke/finance/personal-investing` 亦有 36 处同类链接。
  - **P2-6 信源去重已修**：束 1 原 S33/S37 两条同链接两用 → S33 保留为中央网信办《数字新经济发展新动能》（术语起源），S37 改指清华大学出版社《新动能：数字经济的缘起》书稿节选；新增 `S42` 新华网（智能经济概念）与 `S43` 国家知识产权局《数字经济核心产业专利统计分析报告（2025）》；F-009/F-012 改挂 S37、F-013 改挂 S42、F-073 改挂 S43；同步 bundle1 facts.md 信源登记表标题（S1–S43）、说明段、bundle1 index.md / references / concepts/index.md / log.md 中的 S 范围表述。
  - **P2-7 自链锚文本已修**：bundle1 `references/01-sources-and-authorities.md` 中 `[facts.md](01-sources-and-authorities.md)` → `[facts.md](../facts.md)`。
  - **P2-8 计数失真已修**：tasks.md Task 3 证据、两束 `log.md` 的 P0 条数改为实测值（束 1 = 42 条、束 2 = 56 条）。
  - **P2-9 基线漂移已记**：spec.md Goals 增补「计数基线说明（2026-10-17 V 门澄清）」，如实记录并行会话在 `sheke/industry` 新增 1 束导致的 641→642 基线位移与最终以树为准的 644 束 / 62 组。
  - **C 门首轮 findings 修复（第二轮，第二轮评审依据）**：
    - **F-1（P1，信源错引 4 条）**：`digital-asset/facts.md` F-067/F-068/F-069 的信源由 S31（金融委第五十一次会议）更正为 **S32**（人民银行《中国数字人民币的研发进展》白皮书）——三条事实内容均为白皮书口径。
    - **F-2（P1，信源缺失）**：新增信源 **S63**（中国人民银行座谈会／人民网转载，《数字人民币研发试点工作座谈会》2022-04-02），F-072 信源由 S32 更正为 **S63、S62**；S 台账由 S1–S62 扩为 **S1–S63**，同步 bundle2 的 facts.md 说明段与登记表标题、references 台账说明与分层标题、index.md 两处、log.md、concepts/00、concepts/index.md、tasks.md 全部 S 范围表述。
    - **F-5（P2，引用链空指）**：原说明段称「F-072 的 mBridge 事实见 S62」但 F-072 并无 mBridge 内容——已把 mBridge 的发起/MVP/BIS 移交三点并入 F-072 事实正文（信源 S63、S62），说明段改写为 S62/S63 的准确分工，`concepts/06` 的引用链恢复可解析。
    - **F-3（P2，判据冲突）**：spec.md **NFR-1** 增补「相对路径澄清（2026-10-17 C 门澄清）」——同目录清单/台账类文件（concepts/index、examples/index、references/*）允许同级相对路径（与样板束一致），正文导航仍强制 `/`-根路径。
    - **F-4（P2，状态失真）**：Task 7、Task 8、Task 10 状态已按实测更新为 `completed` 并补齐 Completion Evidence（门禁 rc、dummy 构建 30 warnings 中本分组 0 条）。

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4、Task 5、Task 6 相互独立，均依赖 Task 3，可并行实施
- Task 7 depends on Task 4、Task 5、Task 6
- Task 8 depends on Task 7
- Task 9 depends on Task 8
- Task 10 depends on Task 8（V 门发现修复队列，Task 9 的 Review 以本队列清空为前提）
