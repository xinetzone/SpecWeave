---
type: spec
title: "WorkBuddy 官方站点与四区文档全站学习 → OKF Wiki 知识包"
status: completed
methodology: seven-concepts-cmd
content-sensitivity: public
source:
  - https://www.workbuddy.cn/
  - https://www.workbuddy.cn/docs/workbuddy/Overview
  - https://www.workbuddy.cn/docs/sitemap.xml
---

# WorkBuddy 官方站点与四区文档全站学习 → OKF Wiki 知识包

## 概述

- **目的**：全面学习腾讯 WorkBuddy 官方站点（`www.workbuddy.cn`）与其文档站四个分区，把「产品宣传口径 + 可照做操作指引 + 企业管理后台配置」转化为一个可溯源、有时效管理、口径分层的中文 OKF v0.2 知识包。
- **读者**：评估 AI 办公工作台的个人与团队、需要让 Agent 接入腾讯办公生态的开发者、需要为企业采购与合规决策的管理者、知识库机器审核（Sphinx toctree + 计数门禁）。
- **目标目录**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/workbuddy-official-docs/`（腾讯生态分组，与既有 3 个 WorkBuddy 束同组）。
- **基线**：本束为**新建**，无既有 F 编号与文档，事实编号自 `F-001` 起。同组已有 `workbuddy-one-sentence-mvp`（一句话做 MVP 实测软文核验）、`workbuddy-sandbox-public-endpoint`（沙箱公网端点）、`tencent-buddy-family`（Buddy 品牌矩阵）、`wecom-5-0-12-release`（企微×WorkBuddy 互通版本快照）；本束**不覆写**其事实与计数，仅做互链。
- **工作流**：七概念知识沉淀链路 `R→I→E→V`；实施前经批准门，完成后独立上下文审查。Git 提交须另获用户明确授权。

## 目标与非目标

### 目标

- 四区全部内容页有采集记录、知识归属与覆盖状态；不以「读了首页」代替全站覆盖。
- 按「事实—功能机制—操作演练—信源查证」组织，产出可照做的示例与可回溯 F 编号的概念文档。
- 口径分层硬要求（四类，一律不得抹平）：
  1. **官网宣传口径 vs 文档操作口径**：官网首页的企业级安全表述（TLS/AES-256、RBAC + 操作审计日志、ISO 27001 / SOC 2 / 等保三级）与文档站实际可配置项之间需分层呈现。
  2. **四端差异**：`workbuddy`（桌面端）、`workbuddyapp`（移动端 App）、`workbuddymini`（小程序端）三区功能说明页存在同名不同文的差异，不得混为一谈。
  3. **企业版 vs 个人版边界**：`enterprise` 区的能力（席位管理、模型部署管理、Connector/Skill/专家/Playbook 管理、日志管理、研发度量、IP 白名单）属企业版管控面，不得写成个人版可用。
  4. **版本时效**：官方更新日志（Changelog）与各页 `最后更新` 日期不同步，引用时必须带核验时点。
- 接入腾讯生态分组到 bundles 总索引的五级导航与计数（tencent → ecosystems → jishu/ai → jishu → bundles 总索引），并与同组既有束双向互链。
- 操作可复现性两问判定：官方文档提供安装、创建任务、连接器/MCP、技能、知识库、定时任务、小程序发布、企业后台配置等**可照做链路** → **设 `examples/`**。

### 非目标

- 不复制官网与文档站正文原文（不做全文镜像），只做原创归纳 + 事实登记 + 原创操作演练。
- 不实际安装 WorkBuddy 客户端、不注册账号、不执行文档中的真实操作（不产生真实订单、不发布真实小程序、不开通企业版）；所有操作用例明确标注「未在本机实跑」。
- 不逐字转写版本日志正文（归纳为一条版本线，明细仅登记入口与日期）。
- 不修改同组既有束的事实、计数与正文（仅允许在 `workbuddy-one-sentence-mvp/index.md` 回补一条互链）。
- 不修复与本任务无关的并行在途变更与索引漂移（只在 `log.md` 披露观测结果）。
- 不新建分组、不新建顶级类目、不执行 git commit/push。

## 背景与范围

`www.workbuddy.cn` 为腾讯官方公开站点（无访问控制、无 `code/token` 参数），内容敏感度判定为**公开内容（Public）**，走标准工作流，产出物入 `doc/bundles/`。

文档站为 VitePress 工程，其 `/docs/sitemap.xml` 为 sitemapindex，下挂 5 个 urlset：

| 编号 | 分区路径 | 页数 | sitemap lastmod | 内容性质 |
| --- | --- | --- | --- | --- |
| W0 | `/`（官网首页） | 1 | — | 产品定位、AI 场景、腾讯生态打通、隐私与安全、下载入口 |
| W1 | `/docs/workbuddy/` | 约 120（含约 24 篇版更日志；以机械枚举为准） | 2026-10-10 | 任务模型、界面、功能说明（25+ 篇）、知识库集成、App/Web 发布、FAQ/错误码、安装指引 |
| W2 | `/docs/enterprise/` | 28 | 2026-10-14 | 概览、登录、SaaS/私有化快速开始、管理后台 20 篇、计费 3 篇 |
| W3 | `/docs/workbuddyapp/` | 15 | 2026-10-10 | 移动端 App：概览、快速开始、设置、11 篇 features |
| W4 | `/docs/workbuddymini/` | 18 | 2026-10-10 | 小程序端：快速开始 2 篇、features 12 篇、use-cases 3 篇 |
| W5 | `/docs`（文档根） | 1 | 2026-10-14 | 文档站入口 |

**W1 二级结构**（已采集，实施时以机械枚举为准）：

| 子路径 | 页面 |
| --- | --- |
| 顶层 | `Overview`、`Scenarios`、`FirstTask`、`Create-Task`、`Task-Management`、`Conversation`、`Results`、`Credits`、`Contact`、`Account-Cancellation`、`Download-History`、`Changelog` + `Changelog-5.3.14`～`Changelog-5.7.7`（约 24 篇，以机械枚举为准）、`Feishu-Guide`、`Dingtalk-Guide` |
| `From-Beginner-to-Expert-Guide/` | `FAQ`、`Error-Code`、`Efficient-Tips`、`Installation-Kylin-Guide` |
| `.../Function-Description/` | `Assistant`、`Automation-Guide`、`Buddy-App`、`CloudAgent`、`Connector`、`Data`、`Design-Idea`、`Expert-Center`、`Feedback`、`File-Browser`、`Ispiration`、`Library`（+`Collaboration`、`Content-Management`、`Lightweight-Publish`）、`Mailbox`、`MCP-Guide`、`Memory`、`Model`、`Permission-Modes`、`Plug-In`、`Project`、`Right-Sidebar`、`Setting`、`Sidebar`、`Skills-Market`、`Task-Bar`、`Worktree-Task` |
| `.../App-Publishing/` | `Mini-Program`、`Web-App`、`Cloud-Services` |
| `.../Knowledge-Base/` | `Cowriting`、`Lexiang`、`Tencent-Doc`、`IMA Knowledge Base/01`～`06` |

**W2 管理后台子结构**：`基础设置`、`账号管理/{企业管理员, 席位管理, 企业微信集成, 飞书集成}`、`模型管理`、`模型部署管理`、`提示词管理`、`自定义指令`、`专家管理`、`Skill 管理`、`Playbook`、`Connector 管理`、`知识库`、`知识库管理`、`CloudAgent`、`日志管理`、`安全管理/IP 白名单`、`研发度量`；计费 `Pricing`、`Purchase`、`Voucher`。

**采集边界**：站外链接仅按事实核验需要读取，不做无限递归；注入式介绍页（`/app` 在线使用入口、合作伙伴/博客等未入 sitemap 的着陆页）以官网首页可达范围为准，实施时用 `sitemap-pages.xml` 复核。

### 知识包分层设计（新束结构，共 29 个 Markdown）

```
workbuddy-official-docs/
├── index.md
├── log.md
├── concepts/    （index.md + 00～11 十二篇）
├── examples/    （index.md + 00～08 九篇）
└── references/  （index.md + article-source.md + source-manifest.md + verification.md）
```

| 层 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| concepts | `00-overview-and-positioning` | WorkBuddy 是什么、谁出品、与传统 AI 对话差别、界面四区 |
| concepts | `01-task-model-and-workflow` | 任务怎么创建/管理/继续/对话/验收 |
| concepts | `02-agent-execution-and-permissions` | 自主规划与工具调用怎样跑、本地文件权限、记忆、Worktree、并行 |
| concepts | `03-feature-map-and-ui` | 侧边栏/任务栏/右侧栏/设置/项目等功能面全貌 |
| concepts | `04-experts-skills-and-plugins` | 专家中心、技能市场、插件分别是什么、怎么扩展能力 |
| concepts | `05-connectors-and-mcp` | 连接器与 MCP 怎样接入外部服务/数据 |
| concepts | `06-knowledge-base-and-library` | 资料库/知识库（腾讯文档、乐享、IMA）与协同写作 |
| concepts | `07-cloud-agent-and-automation` | 云助理与自动化/定时任务机制 |
| concepts | `08-app-publishing` | 小程序、Web App、云服务发布链路与边界 |
| concepts | `09-multidevice-and-tencent-ecosystem` | 四端差异、腾讯生态打通、飞书/钉钉指南 |
| concepts | `10-credits-and-pricing` | 积分体系、套餐与计费口径 |
| concepts | `11-enterprise-admin-and-security` | 企业版管控面与隐私安全合规 |
| examples | `00`～`08` | 安装与首个任务、任务管理、对话与结果、连接器/MCP、技能与专家、知识库、自动化与云助理、小程序/Web App 发布、企业后台配置 |
| references | `article-source`/`source-manifest`/`verification` | 每条说法的出处、页面覆盖台账与核验结论 |

## 功能需求

- **FR-1**：新建 bundle `workbuddy-official-docs/`，含根 `index.md`、`log.md`、`concepts/`（索引 + 12 篇）、`examples/`（索引 + 9 篇）、`references/`（索引 + 3 篇），共 29 个 Markdown；每个含子目录的层级生成 `index.md` 并以 `{toctree}` 引用全部内容文档。
- **FR-2**：`references/source-manifest.md` 登记 W0～W5 六分区逐页台账（URL、访问日期、页标题/章节概要、知识归属文档、覆盖状态：新增覆盖/复用既有/采集失败），并以集合比对证明 sitemap 页面集合 = 已处理集合。
- **FR-3**：R 阶段产出 spec 目录 `facts.md`，登记 `F-001` 起编号事实；`references/article-source.md` 双份登记同一编号集合，两处正则提取的 `F-\d{3}` 集合相等、连续无跳号。
- **FR-4**：`references/verification.md` 给出核验总表（版本号与日期、四区 lastmod 差异、官网宣传口径 vs 文档可配置项、单源清单）、勘误清单、口径并存表、V 四视角对抗审查表、status 裁决。
- **FR-5**：concepts 12 篇中所有具体声明（数字、版本号、功能专名、日期、限额）带 F 编号引用；四类口径分层在全束一致落地；含至少 2 张 Mermaid 图（任务生命周期流程图 + 四端/生态架构图）。
- **FR-6**：examples 9 篇提供前置条件、操作步骤、结果判据与限制说明；未在本机实跑的步骤显式标注。
- **FR-7**：五级索引接入与计数同步——`tencent/index.md`（导航表 + toctree + 束数 13→14 + 概念/示例/信源/事实计数 + 「关于本分组」段 + 相关链接）、`ecosystems/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`（`total_bundles` 634→635、jishu 470→471 等）；全部数字以实施时机械真值为准，不得手工估算。
- **FR-8**：双向互链——新束 `index.md`「主题关联」链同组 4 束 + `codebuddy`；`workbuddy-one-sentence-mvp/index.md` 回补 1 条指向新束的链接（最小改动，不动其事实与计数）。
- **FR-9**：`log.md` 记录七阶段执行、口径决策、并行在途观测、门禁运行方式（直接运行底层脚本；`invoke gates.*` 若不可用不谎报）。

## 非功能需求与约束

- **NFR-1（规范一致）**：全部文件遵循 OKF v0.2 frontmatter（`okf_version` 仅出现在 bundle 根 `index.md`；子文档 `type` 取 `Concept`/`Example`/`Reference`；`generated`/`verified` 使用 `process:seven-concepts-*` actor 约定；`status`/`stale_after`/`sources` 齐备），中文正文，kebab-case 英文文件名。
- **NFR-2（机械质量）**：UTF-8 严格 roundtrip 无 BOM 无乱码；全部 Markdown 相对链接可达；零 `file:///`、零 `C:\Users` 等本机绝对路径；每个 `index.md` 含 toctree 且条目逐一存在。
- **NFR-3（时效管理）**：`stale_after` 按快速迭代的产品文档设为 `2027-04-15`；版本号、积分规则、页数、企业版功能等时效项在「已知边界」集中声明。
- **NFR-4（可审计）**：核验信源全部为实际访问成功的 URL，禁止编造；无法核验项标「仅官方单源/未取得」，不升级可信度；未实跑的操作标注「未在本机实跑」。
- **NFR-5（子模块纪律）**：产出在 git submodule `projects/awesome-okf-xs/`，**不提交**；写入前检查子模块无 merge/rebase 进行中；保护其他会话变更，不改无关共享索引。
- **NFR-6（临时文件隔离）**：采集缓存、复算脚本等临时产物放工作区外（或 `.temp/` 用后删除）；最终资料仅入目标 bundle，规划仅入本 spec 目录。

## 约束

- **Technical**：Windows + PowerShell 7 + Python（py314）；门禁脚本在子模块根目录直接 `python scripts/<name>.py` 运行（`check-toctrees.py`、`check-utf8.py`、`check-bundles-index.py`）。
- **Business**：遵循 SpecWeave 启动协议与文档边界（公开内容标准工作流，spec 在主仓 `.trae/specs/okf-wiki-ecosystem/`）；用户沟通中文、动作导向。
- **Dependencies**：文档站与官网可访问性（R 阶段已抽样验证 WebFetch 成功）；外部信源时效性（2026-10-15 核验快照）；门禁脚本可用性。

## 假设

- 归属 `jishu/ai/ecosystems/tencent/` 无争议：WorkBuddy 为腾讯出品，同分组已有 3 个 WorkBuddy 束先例，不单新建分组；同时**不**在 `jishu/ai/products/` 重复建束（避免双份事实源）。
- 骨架按「产品官方文档教程化」判定：操作可复现性两问皆**是**（官方提供可照做的安装/配置/发布链路）→ 设 `examples/`。
- 核验时点 `2026-10-15` 的页面状态即本束快照基准；此后新增功能不在本束范围（`stale_after` 到期复核）。
- 27 篇 `Changelog-*` 明细页仅登记入口与日期，正文归纳为 `concepts/` 版本时效段落，不逐字转录。

## 验收标准

### AC-1：四区全站覆盖完整

- **Type**: `rule`
- **通过条件**：`/docs/sitemap.xml` 下 5 个 urlset + 官网首页的页面集合，与 `source-manifest.md` 登记的处理集合双向差集为空；每个内容页均有 URL、访问日期、章节概要/标题、知识归属文档与覆盖状态；采集失败页单独记录且不计作已学习；版更明细页（`Changelog-*` 全部）按「归纳覆盖」显式登记而非静默跳过。
- **证据**：`references/source-manifest.md` 逐页清单 + 集合差异机械比对输出。

### AC-2：事实编号连续且可溯源

- **Type**: `rule`
- **通过条件**：spec `facts.md` 与 `references/article-source.md` 的 `F-\d{3}` 编号集合相等、连续无跳号、无重复；每条事实指向实际读取成功的 URL/章节；数字与版本号标明来源与核验口径；无未标注的推断；不做任何 F 编号重排或覆写（本束自 F-001 起，与同组既有束编号体系互不干涉）。
- **证据**：正则集合比对输出 + article-source.md 来源代号表 + verification.md 核验表。

### AC-3：四区差异与口径分层准确

- **Type**: `rule`
- **通过条件**：四类口径（官网宣传 vs 文档可配置项、桌面/App/小程序三端差异、企业版 vs 个人版边界、版本时效）在 `verification.md` 与 concepts 正文中均有独立小节或表格行呈现；三端同名功能页的差异有对照表；企业版能力不得写成个人版可用；引用版本号/日期必带核验时点；不得出现替官方宣布的「已 GA / 已上线」类表述（官方未明示者）。
- **证据**：verification.md 口径并存表 + concepts 三端对照表 + Grep 抽查记录。

### AC-4：五级索引与计数同步

- **Type**: `rule`
- **通过条件**：`python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0（五面计数一致）；新束在 tencent 分组导航表与 toctree 均出现；五级索引写入的数字与脚本输出逐项相等；`check-toctrees.py` 全量输出过滤本束名零命中（既有/并行污染项只在 log.md 列名披露）。
- **证据**：门禁脚本输出 + 机械复算记录。

### AC-5：机械门禁与独立审查

- **Type**: `rule`
- **通过条件**：`check-utf8.py` 通过；全部新增文件的相对链接 Test-Path 存活；零 `file:///`、零本机绝对路径；frontmatter 必填字段逐文件核对通过；定向 Sphinx dummy 构建无本束引入的错误；最新独立 Review 结果为 `pass`。全库既有/并行问题按归属隔离并如实报告，不声称全库通过。
- **证据**：门禁脚本输出、构建结果、review.md。

### AC-6：教程可用性与知识分层质量

- **Type**: `rubric`
- **维度**：从「了解产品」到「照做配置」再到「企业采购决策」的可用性，以及事实—机制—操作—查证四层的分层清晰度。
- **量表**：1-5。
- **锚点**：1 = 官网宣传语与文档条目平铺堆砌，读者无法照做也无法判断可信度；3 = 主题齐全、有分层但前置条件/结果判据不清，口径分层不统一；5 = 每篇回答一个明确问题，examples 具备前置/步骤/判据/限制且未实跑处显式标注，concepts 每条数字可回溯 F 编号，四类口径标签全文一致，「已知边界」可直接支持使用与采购决策。
- **通过阈值**：>= 4。
- **证据**：concepts 12 篇 + examples 9 篇 + index「已知边界」；独立评审逐篇抽查评分。

## 待决事项

- 无阻断性范围歧义。以下为实施时按既有裁决执行、无需再确认的事项：①不执行 git commit/push；②计数以机械真值复算为准，并行漂移只披露不修复；③`stale_after: 2027-04-15`；④`status` 目标 `stable`（若 V 阶段发现核心声明证伪则转 `flagged`/`draft`）；⑤不同组既有束的事实与计数，仅 `workbuddy-one-sentence-mvp/index.md` 回补 1 条互链。
