# inurl 三次复核 G5（四目标页面深度学习）→ OKF Wiki 更新 - Implementation Plan

> 对应 spec：同目录 `spec.md` §10（G5，F-088~F-105）
> 方法论：seven-concepts 场景4（R→I→E）× blog-article-to-okf-wiki（R→I→E→V→C）
> 证据物：`.temp/inurl-refresh-g5/`（curl 原始响应、提取文本、审计脚本；不入库）
> 目标 bundle：`projects/awesome-okf-xs/doc/bundles/jishu/ai/inurl-unified-token/`

## Task 1: R — G5 事实双份登记（F-088~F-105）+ P0 证据固化

- **Status**: completed
- **Priority**: high
- **Depends On**: None（证据已在 Specify 阶段采集完毕）
- **Description**:
  - 在 spec `facts.md` 的「### 裁决」段之前插入「### G5. 2026-09-28 三次复核（F-088 ~ F-105，四目标页面深度学习；curl 直打，未注册未下载）」段，18 条按 spec §10.4 规划表落表，列结构沿用 G4（编号/类型/事实/来源/核验）。
  - 在 bundle `references/article-source.md` G 节追加同构 G5 段（双份），措辞、编号、裁决与 facts.md 逐字一致。
  - F-088 写入哈希 `3F689C07FAE9FC67C76C10F8850D02F9F5066697498358EE69D32A13714BD0F1` 与 428,592 字节；F-090 写机器计数 46/17/29(19+10)/133 与隐藏 10 家名单；F-091 写 caps 12 键 text=12/code=5/image=7。
  - P0 固化：F-103 回链 F-069（不重新搜索，旗舰型号证据已权威）；F-104 四源落表——omniroute.online（352 providers/19 策略/:20128 自述口径）、npmjs.com/package/omniroute（v3.8.49、19 策略表、Combo、RTK 压缩 15–95%、~89% 工具链示例）、github.com/diegosouzapw/OmniRoute（MIT、本地优先）、腾讯云开发者社区媒体文（2026-09-17，19 策略/Combo 第三方佐证）；标注各口径时点差异（star/provider 计数随来源与时点变化，只引区间不固化单点）。
  - 持续型事实（F-089/091/092/093/101/105）核验列统一写「持续（F-0xx）」；facts.md 裁决段追加 G5 裁决小结（✅/⚠️/❌/🔄 计数 + flagged 第三次维持）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-1.1: 运行机械比对（Python 单行/临时脚本，正则 `^\|\s*F-(\d{3})\s*\|` 抽取两份文件 F 编号集合），facts.md 与 article-source.md 的 G5 集合均恰为 {088…105}、连续无跳号、与 {001…087} 零交集；输出集合相等证据。
  - `rule` TR-1.2: F-103 含对 F-069 的显式回链；F-104 来源列含 ≥3 个独立域名（omniroute.online、npmjs.com、github.com，媒体为第 4 源）；每条事实来源列非空。
  - `rule` TR-1.3: 持续型 6 条（F-089/091/092/093/101/105）核验列均出现「持续（F-0」回链字样，无一条被改写成全新结论表述。
- **Notes**: article-source.md 双份段落位置=G4 段（§G 末尾）之后；不改动 G1-G4 任何既有行。

## Task 2: E（信源先行）— 新建 omniroute-benchmark.md 并接入 references 索引

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建 `references/omniroute-benchmark.md`（本轮唯一新增文件）：frontmatter（title/status: verified/type: reference/source 四源/reverified: 2026-09-28/stale_after: 2026-12-31）；正文含①实体卡（MIT 开源、本地优先 AI Gateway、npm 包名、端口 20128、维护者 diegosouzapw、已并入 Cheaper Inference 生态）；②机制对照（19 路由策略、Combo 分层流转、auto 多因子、RTK+Caveman 压缩自述 15–95%/工具链示例 ~89%）；③与 inurl 的口径差异表（inurl 压缩档位 15/30/50/75/60–90% 自述估算 vs OmniRoute 15–95%；352 providers 等数字为对方站点时点自述）；④边界声明（inurl 页面主动写「OmniRoute 同款思路/Combo 一致」属自认，本文只做事实对标，不作抄袭/侵权判定）；⑤全部来源 URL 与访问日期。
  - 更新 `references/index.md`：信源表新增一行并计入条目列表（toctree 同步）。
- **Acceptance Criteria Addressed**: AC-3, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-2.1: 文件存在且被 references/index.md 列出、被 concepts/02 相对链接引用；两处链接 Test-Path 可达。
  - `rubric` TR-2.2: 中立性维度（事实陈述 vs 法律/贬损判断）；scale 1-5；anchors 1=出现「抄袭/剽窃/侵权」等定性或贬低任一方措辞，3=事实与观点分层但边界声明不醒目，5=纯事实对标+口径差异+显式不作法律结论+自述数字全标注；threshold >= 4；证据=审查者通读该文件的评分记录。
  - `rule` TR-2.3: 除该文件外不产生其他新增文件（git status 新增文件数=1，spec 的 tasks.md/review.md 除外）。

## Task 3: E — verification.md 新增 §8 三次复核

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - §8.1 方法与范围（四 URL、curl/GET 只读、未注册未下载、catalog 哈希审计、OmniRoute 四源核验）。
  - §8.2 持续项裁决表：F-089→F-072/F-070、F-090→F-077、F-091→F-082、F-092→F-079、F-093→F-073/F-086、F-101→F-045/F-083、F-105→F-084/F-087。
  - §8.3 新增项裁决：F-094 ✅（界面功能）、F-095 ✅ 功能存在+⚠️ 压缩率为自述估算、F-096 ✅、F-097 ⚠️（个人收款码人工核销=运营成熟度信号）、F-098 ⚠️（生产环境 mock 支付入口）、F-099 ⚠️（运营接口公开，属设计但扩大指纹面）、F-100 ❌（news 标题/摘要文不对题）、F-102 ✅、F-103 ⚠️（付费目录整体陈旧 ≥1 大版本）、F-104 ✅（对标实体真实，口径差异见专页）；给出 G5 计数小计。
  - §8.4 总裁决：核心 ❌ 产品侧依据第三次原样成立；flagged 第三次维持、stale_after: 2026-12-31 不变；下轮复核触发条件（catalog 哈希变化 / 付费卡更新当期旗舰 / news 失配修正 / mock-paid 下线）。
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-3.1: §8 含 G5 计数（✅/⚠️/❌/🔄 四个数字均可解析且与 facts.md 裁决段一致）与显式「flagged 第三次维持」句。
  - `rule` TR-3.2: /app 相关裁决（F-094~F-098）每条均含「界面/前端显示」类限定语，无「已验证后端/实测可用」越轴表述。

## Task 4: E — concepts 四篇增补（00/01/02/03）

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - `concepts/00-article-and-product.md`：追加「G5 三审补注（2026-09-28）」小节——/app 功能全景（仪表盘四组件/密钥库/模型源同步/设置/套餐/邀请/系统管理七区）、管理后台运营工具清单、个人收款码人工核销与 mock-paid 并存、公开 ads/news 接口与 news 文不对题、源同步页自述（shared/catalog.json + refresh_catalog.mjs）；全部标注「未注册账户下的界面证据」。
  - `concepts/01-free-model-landscape.md`：追加付费侧陈旧度段（F-103），与既有免费区陈旧段（F-080）并列，回链 F-069；三审零迭代一句（catalog 哈希）。
  - `concepts/02-byok-unified-architecture.md`：追加「路由策略/提示词压缩/Combo」架构小节（19 策略名单、5 档压缩、`>` 组合、偏好下发本机代理）+「开源对标：OmniRoute」小节（链接新信源页，给机制相似点与口径差异，不下定性结论）；补自定义厂商三协议在架构中的位置。
  - `concepts/03-cost-strategy-boundaries.md`：加一段三审时效指针（定价未变→核心勘误仍成立；付费目录陈旧影响"付费转用"决策；详细运营信号指针 concepts/00），不重复展开。
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-4.1: 四篇文件均只追加/补注，G4 及更早段落无删除性改写（git diff 以新增行占绝大多数；若有修改行须在 Notes 说明理由）。
  - `rubric` TR-4.2: 证据措辞维度；scale 1-5；anchors 1=把界面功能写成已实测后端行为，3=大部分有限定但有 1-2 处越轴，5=全部 /app 能力均标注证据形态（界面/JS/自述）且自述数字带「估算/约」；threshold >= 4；证据=逐篇通读评分。
  - `rule` TR-4.3: concepts/02 含对 `../references/omniroute-benchmark.md` 的相对链接且路径可达。

## Task 5: E — examples/01 接入演练增补

- **Status**: completed
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 追加「进阶：自动路由环境变量」：`AUTO_MODELS`、`AUTO_PROVIDER_ORDER` 示例（照 guide 原文口径），标注别名等价关系 auto/default/inurl≡inurl-text 与「改 catalog 需重启代理」。
  - 追加「自定义厂商接入」：三类型（OpenAI 兼容/Anthropic/Gemini）、字段填写要点（baseUrl/路径/模型 ID 必须与厂商文档一字不差/鉴权头前缀/编辑留空保留原密钥）、保存后出现在模型下拉。
  - 追加「保活与停止」：shell:startup 开机自启、任务管理器或 `taskkill /f /im node.exe` 停止。
  - 顶部时效截点更新为 G5；所有步骤标注来源为站点 guide/界面（未经作者实机复验，演练篇既有 flagged 纪律不变）。
- **Acceptance Criteria Addressed**: AC-7, AC-9
- **Test Requirements**:
  - `rule` TR-5.1: 新增三个小节均存在，环境变量名与 guide.txt 逐字一致（AUTO_MODELS/AUTO_PROVIDER_ORDER）。
  - `rubric` TR-5.2: 可复现纪律维度；scale 1-5；anchors 1=把 guide 自述步骤包装成作者实测，3=步骤完整但缺未复验标注，5=步骤可照做且显式标注「站点教程口径、本轮未注册未实机复验」；threshold >= 4。

## Task 6: E — index.md 与 log.md 收尾

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Description**:
  - `index.md`：frontmatter reverified/updated 更新至 2026-09-28 G5、facts 范围改 F-001~F-105；flagged 横幅追加「2026-09-28 三审：站点零迭代（catalog 字节级同一文件），核心勘误第三次成立，新增 /app 路由/压缩/后台与 OmniRoute 对标，flagged 维持」一行；内容导航补 omniroute-benchmark 信源；toctree 加入新文件；已知边界段补 mock-paid/人工核销/news 失配/付费目录陈旧四条指针；时效截点与 stale_after 保持 2026-12-31。
  - `log.md`：追加 2026-09-28 G5 段（触发、方法、产物文件清单、裁决计数、flagged 维持、未提交待确认）。
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-9
- **Test Requirements**:
  - `rule` TR-6.1: index.md toctree 含 omniroute-benchmark.md 且与 references/index.md 计数自洽；frontmatter 无残留 G4 截止口径（不再出现 F-087 作为最大编号）。
  - `rule` TR-6.2: log.md G5 段列出的改动文件数与 git status 实际变更文件数一致。

## Task 7: V — 机械门禁全量

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 在 `projects/awesome-okf-xs` 子模块根依次运行：`python scripts/check-utf8.py`、`python scripts/check-toctrees.py`、`python scripts/check-bundles-index.py`，全绿。
  - 双份 F 编号集合机械比对（TR-1.1 脚本复跑）+ 编号连续性（001…105 无缺号，允许历史既有的编号布局）。
  - 链接检查：本轮新增/改动文件内全部 Markdown 相对链接逐一 Test-Path；零 `file:///`、零家目录、零 `.temp/` 引用。
  - 计数不变核对：bundles/index.md、jishu/ai/index.md 的束计数与 G4 后现值一致（未新增束）。
  - 输出门禁证据摘要写入 tasks.md 本任务 Completion Evidence。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-7.1: 三脚本退出码均为 0（若脚本要求特定调用参数，按脚本 README 的既有调用方式；输出留存）。
  - `rule` TR-7.2: 全文扫描零 `file:///`、零 `.temp/`、零 `C:\`/`/c/Users` 路径；相对链接无死链。
  - `rule` TR-7.3: 三级索引计数与 G4 后基线 diff 为空（除日期/内容描述外计数数字零变化）。
- **Completion Evidence（2026-09-28）**：
  - check-utf8.py：`UTF-8 检查通过: 10664 个文件均为有效 UTF-8。`
  - check-toctrees.py：`toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。`
  - check-bundles-index.py：`bundles 总索引对账通过: 9 域 / 59 组 / 575 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。`（束总数未变，本轮仅在既有束内新增 reference 文件）
  - fset_check.py：双份各 105 条、F-001~F-105 连续、集合相等、G5={088..105}、6 条持续型回链全 True、F-103→F-069、F-104 三域名 True。
  - link_check.py：48 条相对/根链接全可达；零 file:/// 链接、零 .temp/、零家目录（log.md 两处「file:///」为历史门禁描述文字，非链接）。
  - git status：束内 10 M + 1 ??（omniroute-benchmark.md），子模块非本束改动 0；三级索引文件未出现在改动清单。
  - R1 独立子代理 verdict=pass（0 P0/0 P1/4 P2），P2-1/2/3 已修复（后台八模块计数、付费卡型号逐字精确化、frontmatter resource 补全 URL），P2-4 即本台账更新；修复后已复跑 fset_check/link_check。

## Task 8: Review — 独立新鲜上下文只读审查 + review.md

- **Status**: completed
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 队列清空后创建 `.trae/specs/okf-wiki-ecosystem/inurl-free-models-blog-okf-wiki/review.md`（按 artifact-templates 模板，CP 覆盖 AC-1~AC-10）。
  - 委派一个 general_purpose_task 子代理（独立、只读、新鲜上下文）：给绝对路径（spec/tasks/facts 与 bundle 目录）、用户目标、18 条 F 编号范围、门禁命令与 AC 表；要求其独立复跑三脚本与 F 集合比对、抽检证据轴（以 .temp 抓取物对照 /app 类措辞）、核对 OmniRoute 四源可达性与中立性、核对最小变更（新增文件恰 1 个+review.md）。
  - pass：回填 Review History R1=pass 与证据，输出原子提交建议（子模块 bundle 显式文件列表 → 主仓库 spec 两/三件套 → gitlink），**不 commit/push**，等用户指令。
  - fail：materialize issues（I-N 模板）回 Implement，修复后重跑对应 TR 与再审查。
- **Acceptance Criteria Addressed**: AC-1 ~ AC-10（全覆盖）
- **Test Requirements**:
  - `rule` TR-8.1: review.md 每个 AC 至少被一个 CP 覆盖；R1 结论为 pass（或 fail 时每个失败 CP 均有对应 actionable issue 与回归 TR）。
  - `rule` TR-8.2: 子代理报告含三脚本独立复跑结果、F-088~F-105 集合独立比对结果、新增文件清单（期望 bundle 内 1 个）。
  - `rubric` TR-8.3: 证据轴与中立性综合评分；scale 1-5；anchors 1=存在越轴断言或法律定性，3=个别措辞模糊但不影响结论，5=AC-7/AC-8 全部满足且审查者无修改要求；threshold >= 4；证据=子代理评分与逐条意见。
