---
type: spec
title: "WorkBuddy 智能硬件接入白皮书学习 → OKF Wiki 知识包"
status: completed
methodology: seven-concepts-cmd
content-sensitivity: public
source:
  - https://www.workbuddy.link/p/JVM0gKdRyl8k9EgElw5TxA
  - https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json
  - https://open.workbuddy.cn/
---

# WorkBuddy 智能硬件接入白皮书学习 → OKF Wiki 知识包

## 概述

- **目的**：全面学习腾讯 WorkBuddy 开放平台发布的《智能硬件接入 WorkBuddy 白皮书》（发行日期 2026 年 08 月，正文 14 章 + 附录 A/B），把「战略与商务 + 产品与能力 + 技术接入 + 落地与运营」四部分转化为可溯源、有时效管理、口径分层的中文 OKF v0.2 知识包。
- **读者**：评估 AI 硬件接入方案的产品/商务负责人、需要按 OAuth 2.0 + OpenAPI 完成接入的开发者、负责上架审核与联合运营的 PMO/运营。
- **目标目录**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/workbuddy-hardware-integration-whitepaper/`（腾讯生态分组，与既有 5 个 WorkBuddy 束同组）。
- **基线**：本束为**新建**，事实编号自 `F-001` 起，与同组既有束（`workbuddy-official-docs` 的 F-001~F-520、`wecom-5-0-12-release` 等）编号体系互不干涉。
- **工作流**：七概念知识沉淀链路 `R→I→E→V`；实施前经批准门，完成后由独立上下文审查。Git 提交须另获用户明确授权。

## 目标与非目标

### 目标

- 白皮书全部章节（0~13 + 附录 A/B）均有采集记录、知识归属与覆盖状态；不以「读了目录/摘要」代替正文覆盖。
- 按「事实—机制—操作—查证」四层组织：concepts 回答「是什么/为什么/怎么合作/有哪些能力」，examples 提供可照做的接入链路，references 提供逐条查证。
- **口径分层硬要求（五类，一律不得抹平）**：
  1. **厂商自宣 vs 第三方数据**：§0.1 三项指标（「日活第一」= 腾讯 2026 Q1 财报、「2097 万/月」= 易观分析、「2.2 万+ Skills」= 平台自述）来源不同，须挂来源、不得混同为本束独立结论。
  2. **同文档自相矛盾的 Skills 数量**：§0.1 写「2.2 万+ Skills」、§1.1 与 §5.4 写「7 万余 Skills」，白皮书内部不一致，须并列表述 + 勘误登记。
  3. **匿名化伙伴场景**：§6.1 六个「已跑通的真实场景」品牌与产品名已匿名处理（如「某 AI 记忆眼镜品牌」），不得反推、补全或猜测真实品牌。
  4. **商务结构框架性参考**：§4.4/§4.5 明示「商务结构为框架性参考，具体金额与结算周期以双方协议为准」「阶梯价、分成比例、授权费一事一议」「商业化分级与数据分账以官网公示及协议为准」，须原样保留该限定。
  5. **接口以官网开发者文档为准 + 时序矛盾**：§7 明示「第 7–10 章接口清单、鉴权、示例、联调流程均以官网开发者文档最新版本为准」；且页脚「发行日期 2026 年 08 月」早于 §7 声称的「平台已于 2026 年 9 月 2 日正式发布」，时序不自洽须登记。
- 接入腾讯生态分组到 bundles 总索引的五级导航与计数（tencent → ecosystems → jishu/ai → jishu → bundles 总索引），并与同组既有束双向互链。
- 操作可复现性两问判定：白皮书第三部分与 §12 提供 OAuth 2.0 授权、Assistants/Tasks 接口调用、端到端流程、自助接入与审核等**可照做链路** → **设 `examples/`**。

### 非目标

- 不复制白皮书正文（不做全文镜像），只做原创归纳 + 事实登记 + 原创接入演练。
- 不在 WorkBuddy 开放平台注册应用、不申请真实 client_id/client_secret、不调用真实接口、不提交真实上架审核；所有操作用例明确标注「未在本机实跑」。
- 不反推 §6.1 匿名化伙伴的真实品牌，不依据场景描述做品牌归属推断。
- 不逐字转写附录 A 的 Swagger 规范（该随册文件未随本分享页提供，登记「未取得」）。
- 不修改同组既有束的事实、计数与正文（仅允许在新束 `index.md` 与既有束之间建立互链；若需在既有束回补互链，限单行最小改动）。
- 不修复与本任务无关的并行在途变更与索引漂移（只在 `log.md` 披露观测结果）。
- 不新建分组、不新建顶级类目、不执行 git commit/push。

## 背景与范围

### 信源与获取方式

白皮书分享页 `https://www.workbuddy.link/p/JVM0gKdRyl8k9EgElw5TxA` 为 **SPA（客户端渲染）**：纯 HTTP 抓取仅得 4.6 KB 壳页（含 `window.__PUBLISH_BOOTSTRAP__` 指向静态制品）；正文经页面 `janus.data.json` 数据源提取。内容敏感度判定为**公开内容（Public）**（无 `code/token` 参数、无访问控制，WebFetch 可直接读取），走标准工作流，产出物入 `doc/bundles/`。

| 代号 | URL | 性质 | 状态 |
| --- | --- | --- | --- |
| W0 | `https://www.workbuddy.link/p/JVM0gKdRyl8k9EgElw5TxA` | 白皮书分享页入口（SPA 壳） | 已访问（渲染） |
| P0 | `https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/janus.data.json` | 页面正文数据源（`publishVersion: 20`，708 KB） | 已获取并解析（提取正文 1330 行 / 21432 字符） |
| P1 | `https://workbuddy-space-static.codebuddy.work/page/JVM0gKdRyl8k9EgElw5TxA/20/WorkBuddy_v4__.html` | 页面 HTML 制品（202 KB） | 已获取（备用） |
| O1 | `https://open.workbuddy.cn/` | 开放平台官网（§7/§12.6 指定入口） | **未核验**（本束不注册账号） |
| X1 | 随册文件 `assistant-openapi.html`（Swagger UI 交互版，附录 A 引用） | 接口完整规范 | **未取得**（本分享页未随附） |

### 白皮书章节结构与归属映射

| 章 | 标题 | 知识归属 |
| --- | --- | --- |
| 0 | 摘要（AI 与硬件融合三阶段、关键数据、如何使用） | concepts/00 |
| 1 | WorkBuddy 简介（六大核心能力、用户画像） | concepts/00 |
| 2 | 硬件接入的价值（三重放大、三痛点与解法） | concepts/01 |
| 3 | 六类硬件触点（听/看/戴/记/聊/协 + 硬件形态） | concepts/01 |
| 4 | 合作模式及范本（三方协同、决策图、四模式、范本、商业模式与结算、L1/L2 分层、合作边界） | concepts/02 |
| 5 | 产品能力全景（Agent 五层架构、云端能力、端云协同、生态扩展、硬件专区） | concepts/03 |
| 6 | 场景能力矩阵（六触点能力组合、六个已跑通场景、ToB 场景） | concepts/03 |
| 7 | 开放能力概述（四类能力、能力构成、核心概念、正式上线声明） | concepts/04 |
| 8 | 授权登录 OAuth 2.0（前置准备、授权流程、换票、刷新与撤销、用户标识） | concepts/05 + examples/00-01 |
| 9 | 接口调用（通用规范、助理接口、任务接口、本机能力） | concepts/06 + examples/02-04 |
| 10 | 端到端示例（六步完整流程、硬件端接入姿势） | concepts/07 + examples/05 |
| 11 | 常见问题（合作模式、票据有效期、多用户隔离、401、本机边界、系统平台、推广分佣等） | concepts/07 |
| 12 | 合作落地流程（两条路径、样板节奏、合作原则、准入审核、品牌授权、对接窗口） | concepts/08 + examples/06 |
| 13 | 联合运营（售后三级支持与 SLA、数据看板、联合宣发、版本迭代与共创） | concepts/09 |
| 附 A | OpenAPI 完整规范（随册文件引用） | concepts/10（登记未取得） |
| 附 B | 术语表（12 条术语） | concepts/10 |

### 知识包分层设计（新束结构，共 26 个 Markdown）

```
workbuddy-hardware-integration-whitepaper/
├── index.md
├── log.md
├── concepts/    （index.md + 00～10 十一篇）
├── examples/    （index.md + 00～06 七篇）
└── references/  （index.md + article-source.md + source-manifest.md + verification.md）
```

| 层 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| concepts | `00-whitepaper-and-workbuddy-overview` | 白皮书是什么、给谁看、WorkBuddy 是什么、六大能力、用户画像与市场数据来源 |
| concepts | `01-hardware-value-and-six-touchpoints` | 硬件为何接入、价值三重放大、三痛点解法、六类触点与形态 |
| concepts | `02-partnership-models-and-commercial-model` | 三方协同怎么分工、四种模式怎么选、合作范本、商业路径与结算口径、L1/L2 分层与边界 |
| concepts | `03-product-capabilities-and-scenario-matrix` | Agent 架构五层、云端能力包、端云协同、生态三层、硬件专区；六触点能力组合与六个真实场景 |
| concepts | `04-open-platform-and-core-concepts` | 开放平台暴露哪四类能力、核心概念（access_token/openid/asst_id/task_id/execution_target） |
| concepts | `05-oauth2-authorization-flow` | OAuth 2.0 授权码 + PKCE 怎么走、换票、刷新撤销、三级用户标识 |
| concepts | `06-assistant-and-task-apis` | 通用规范、助理接口、任务接口、本机能力与 scope 对应关系 |
| concepts | `07-end-to-end-walkthrough-and-faq` | 端到端六步链路、硬件端接入姿势、常见问题与边界答疑 |
| concepts | `08-landing-process-and-access-review` | 两条接入路径、样板节奏、准入条件、审核流程、上架退出、品牌使用与授权 |
| concepts | `09-joint-operations-and-service-levels` | 三级支持体系与 SLA、数据看板、联合宣发方向、版本迭代与共创机制 |
| concepts | `10-glossary-and-appendix` | 术语表 12 条、附录 A 未取得说明 |
| examples | `00`～`06` | 注册应用与配置 scope、OAuth 授权换票、创建并激活云端助理、发起任务与读结果、刷新撤销票据、硬件后端反向代理姿势、自助接入与审核 |
| references | `article-source` / `source-manifest` / `verification` | 每条说法的出处、采集台账与核验结论 |

## 功能需求

- **FR-1**：新建 bundle `workbuddy-hardware-integration-whitepaper/`，含根 `index.md`、`log.md`、`concepts/`（索引 + 11 篇）、`examples/`（索引 + 7 篇）、`references/`（索引 + 3 篇），共 26 个 Markdown；每个含子目录的层级生成 `index.md` 并以 `{toctree}` 引用全部内容文档。
- **FR-2**：`references/source-manifest.md` 登记 W0/P0/P1/O1 四个信源与 X1 未取得项的采集台账（URL、访问日期、获取方式、取得体量、知识归属、覆盖状态），并按白皮书章节表逐章登记覆盖状态（已覆盖/未取得）；对 SPA 页的「壳页 vs 数据源」两种获取路径显著区分。
- **FR-3**：R 阶段产出 spec 目录 `facts.md`，登记 `F-001` 起编号事实；`references/article-source.md` 双份登记同一编号集合，两处正则提取的 `F-\d{3}` 集合相等、连续无跳号；来源代号表覆盖 W0/P0/O1 全部实际引用信源。
- **FR-4**：`references/verification.md` 给出核验总表（发行日期、publishVersion、正式发布日、Skills 数量双口径）、**五类口径分层**表、勘误清单、V 四视角对抗审查表、status 裁决。
- **FR-5**：concepts 11 篇中所有具体声明（数量、日期、接口名、scope 名、时限、SLA 数值）带 F 编号引用；五类口径分层在全束一致落地；至少 1 张 Mermaid 图（OAuth 2.0 授权时序图）+ 1 张流程/架构图（合作模式决策或 Agent 五层架构）。
- **FR-6**：examples 7 篇提供前置条件、操作步骤、结果判据与限制说明（含 HTTP 方法、端点、Header、请求体示例）；未在本机实跑的步骤显式标注「未在本机实跑，依据白皮书（F-xxx）」；不得虚构 client_id/票据/响应值。
- **FR-7**：五级索引接入与计数同步——`tencent/index.md`（导航表 +1 行、toctree +1 条、相关链接 +1 行、「关于本分组」段追加本束说明 + 束/概念/示例/信源/事实计数复算）、`ecosystems/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`（`total_bundles` 与 jishu 段、mermaid 节点、节标题、分组表）；全部数字以实施时机械真值复算为准，不得手工估算。
- **FR-8**：互链——新束 `index.md`「主题关联」链同组既有束（至少 `workbuddy-official-docs`、`workbuddy-one-sentence-mvp`、`workbuddy-open-platform-sharing-and-promotion`、`workbuddy-sandbox-public-endpoint`、`tencent-buddy-family`）；如回补反向链接，限单行最小改动且不动既有束事实与计数。
- **FR-9**：`log.md` 记录七阶段执行、口径决策、并行在途观测、门禁运行方式（直接运行底层脚本；`invoke gates.*` 若不可用不谎报）。

## 非功能需求与约束

- **NFR-1（规范一致）**：全部文件遵循 OKF v0.2 frontmatter（`okf_version` 仅出现在 bundle 根 `index.md`；子文档 `type` 取 `Concept`/`Example`/`Reference`；`generated`/`verified` 使用 `process:seven-concepts-*` actor 约定；`status`/`stale_after`/`sources` 齐备），中文正文，kebab-case 英文文件名。
- **NFR-2（机械质量）**：UTF-8 严格 roundtrip 无 BOM 无乱码；全部 Markdown 相对链接可达；零 `file:///`、零 `C:\Users` 等本机绝对路径；每个 `index.md` 含 toctree 且条目逐一存在。
- **NFR-3（时效管理）**：`stale_after` 按快速迭代的开放平台文档设为 `2027-04-15`；发行日期、publishVersion、接口快照、SLA 等时效项在「已知边界」集中声明，引用必带核验时点。
- **NFR-4（可审计）**：核验信源全部为实际访问成功的 URL，禁止编造；O1 未核验、X1 未取得须显式标注，不升级可信度；未实跑的接入步骤标注「未在本机实跑」。
- **NFR-5（子模块纪律）**：产出在 git submodule `projects/awesome-okf-xs/`，**不提交**；写入前检查子模块无 merge/rebase 进行中；保护其他会话变更，不改无关共享索引。
- **NFR-6（临时文件隔离）**：采集缓存、提取脚本等临时产物放工作区外（或 `.temp/` 用后删除）；最终资料仅入目标 bundle，规划仅入本 spec 目录。

## 约束

- **Technical**：Windows + PowerShell 7 + Python（py314）；门禁脚本在子模块根目录直接 `python scripts/<name>.py` 运行（`check-toctrees.py`、`check-utf8.py`、`check-bundles-index.py`）。
- **Business**：遵循 SpecWeave 启动协议与文档边界（公开内容标准工作流，spec 在主仓 `.trae/specs/okf-wiki-ecosystem/`）；用户沟通中文、动作导向。
- **Dependencies**：分享页与静态制品可访问性（R 阶段已验证）；`janus.data.json` 的 `publishVersion: 20` 快照；门禁脚本可用性。

## 假设

- 归属 `jishu/ai/ecosystems/tencent/` 无争议：WorkBuddy 为腾讯出品，同分组已有多个 WorkBuddy 束先例，不单新建分组；同时**不**在 `jishu/ai/products/` 重复建束（避免双份事实源）。
- 骨架按「厂商白皮书 + 可照做接入指南」判定：操作可复现性两问皆**是**（提供 OAuth/接口/端到端/自助接入的可照做链路）→ 设 `examples/`。
- 分享页 `publishVersion: 20` 的正文即本束快照基准；白皮书以「发行日期 2026 年 08 月」为版本口径，此后官方文档更新不在本束范围（`stale_after` 到期复核）。
- 附录 A 的 Swagger 规范文档未随本分享页提供，按「未取得」登记，不据章节标题推断字段细节。

## 验收标准

### AC-1：白皮书全章覆盖完整

- **Type**: `rule`
- **通过条件**：白皮书 0~13 章与附录 A/B 的章节集合，与 `source-manifest.md` 中登记的知识归属集合双向差集为空；每章均有归属文档与覆盖状态；附录 A 按「未取得」显式登记而非静默跳过；SPA 壳页与数据源两种获取路径均在台账中区分记录。
- **证据**：`references/source-manifest.md` 逐章清单 + 集合差异机械比对输出。

### AC-2：事实编号连续且可溯源

- **Type**: `rule`
- **通过条件**：spec `facts.md` 与 `references/article-source.md` 的 `F-\d{3}` 编号集合相等、连续无跳号、无重复；每条事实指向白皮书实际章节/条款；数量、日期、接口名、scope 名、SLA 数值标明来源与核验口径；无未标注的推断；不做任何 F 编号重排（本束自 F-001 起，与同组既有束编号体系互不干涉）。
- **证据**：正则集合比对输出 + article-source.md 来源代号表 + verification.md 核验表。

### AC-3：口径分层与勘误准确

- **Type**: `rule`
- **通过条件**：五类口径（厂商自宣 vs 第三方数据、Skills 数量自相矛盾、匿名化伙伴场景、商务结构框架性参考、接口以官网为准 + 发行日期 vs 发布日时序矛盾）在 `verification.md` 与相关 concepts 中均有独立小节或表格行呈现；匿名化场景一律不得反推真实品牌；商务数字一律带「以协议为准」限定；接口清单标注「以官网开发者文档最新版本为准」；不得出现替官方宣布的「已 GA / 已上线」类表述（官方未明示者）。
- **证据**：verification.md 口径并存表 + 勘误清单 + Grep 抽查记录。

### AC-4：五级索引与计数同步

- **Type**: `rule`
- **通过条件**：`python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0（五面计数一致）；新束在 `tencent/index.md` 导航表与 toctree 均出现；五级索引写入的数字与脚本输出逐项相等；`check-toctrees.py` 全量输出过滤本束名零命中（既有/并行污染项只在 log.md 列名披露）。
- **证据**：门禁脚本输出 + 机械复算记录。

### AC-5：机械门禁与独立审查

- **Type**: `rule`
- **通过条件**：`check-utf8.py` 通过；全部新增文件的相对链接 Test-Path 存活；零 `file:///`、零本机绝对路径；frontmatter 必填字段逐文件核对通过；定向 Sphinx dummy 构建无本束引入的错误；最新独立 Review 结果为 `pass`。全库既有/并行问题按归属隔离并如实报告，不声称全库通过。
- **证据**：门禁脚本输出、构建结果、review.md。

### AC-6：教程可用性与知识分层质量

- **Type**: `rubric`
- **维度**：从「了解白皮书全貌」到「照做完成 OAuth 授权与接口调用」再到「判断该选哪种合作模式、能否上架」的可用性，以及事实—机制—操作—查证四层的分层清晰度。
- **量表**：1-5。
- **锚点**：1 = 白皮书章节按顺序平铺翻译，读者无法照做也无法判断可信度；3 = 主题齐全、有分层但前置条件/结果判据不清，口径分层不统一；5 = 每篇回答一个明确问题，examples 具备前置/步骤/判据/限制且未实跑处显式标注，concepts 每条数据可回溯 F 编号，五类口径标签全文一致，「已知边界」可直接支持接入决策与商务判断。
- **通过阈值**：>= 4。
- **证据**：concepts 11 篇 + examples 7 篇 + index「已知边界」；独立评审逐篇抽查评分。

## 待决事项

- 无阻断性范围歧义。以下为实施时按既有裁决执行、无需再确认的事项：①不执行 git commit/push；②计数以机械真值复算为准，并行漂移只披露不修复；③`stale_after: 2027-04-15`；④`status` 目标 `stable`（若 V 阶段发现核心声明证伪则转 `flagged`/`draft`）；⑤不同组既有束的事实与计数；⑥§6.1 匿名化场景一律保持匿名，不做品牌反推。
