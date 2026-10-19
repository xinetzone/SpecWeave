---
type: spec
title: "WorkBuddy 开放平台官方文档（dashboard + 10 篇 docs）学习 → OKF Wiki 知识包"
status: pending_approval
methodology: seven-concepts-cmd
content-sensitivity: public
source:
  - https://open.workbuddy.cn/dashboard
  - https://open.workbuddy.cn/docs/what-is-open-platform
  - https://open.workbuddy.cn/docs/onboarding
  - https://open.workbuddy.cn/docs/monetization
  - https://open.workbuddy.cn/docs/skill
  - https://open.workbuddy.cn/docs/connector
  - https://open.workbuddy.cn/docs/expert
  - https://open.workbuddy.cn/docs/expert-team
  - https://open.workbuddy.cn/docs/buddy-app
  - https://open.workbuddy.cn/docs/third-party-app
  - https://open.workbuddy.cn/docs/openapi
---

# WorkBuddy 开放平台官方文档学习 → OKF Wiki 知识包

## 概述

- **目的**：全面学习 WorkBuddy 开放平台（`open.workbuddy.cn`）的开发者文档——平台概述、入驻与资质认证、技能、连接器、专家与专家团、Buddy 应用、第三方应用、Open API 接口、收入变现——把「平台能力边界 + 开发者可照做的开发/上架/接入链路 + 接口与凭证机制 + 元信息与时效」转化为一个可溯源、有时效管理、口径分层的中文 OKF v0.2 知识包。
- **读者**：想在 WorkBuddy 开放平台开发并上架资产（技能 / 专家 / 专家团 / 连接器 / Buddy 应用）的开发者与产品经理；想把自有应用接入 WorkBuddy（分享能力、硬件接入、Open API）的第三方团队；需要判断入驻门槛、变现门槛与接口边界的决策者。
- **目标目录**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/workbuddy-open-platform-docs/`（腾讯生态分组，与既有 5 个 WorkBuddy 束同组）。
- **基线**：本束为**新建**，无既有 F 编号与文档，事实编号自 `F-001` 起。同组已有 `workbuddy-official-docs`（产品与四端文档全站学习，520 条事实）、`workbuddy-open-platform-sharing-and-promotion`（开放平台两篇平台公告，64 条事实）、`workbuddy-hardware-integration-whitepaper`（硬件接入白皮书，190 条事实）、`workbuddy-one-sentence-mvp`、`workbuddy-sandbox-public-endpoint`；本束**不覆写**其事实与计数，仅做互链。
- **工作流**：七概念知识沉淀链路 `R→I→E→V`；实施前经批准门，完成后独立上下文审查。Git 提交须另获用户明确授权。
- **产物集**：本 spec 目录按仓库权威 [TRAE-spec-mode](../../../../.agents/skills/TRAE-spec-mode/SKILL.md) 规范产出 `spec.md` + `tasks.md`（Specify / Plan 阶段**不得**创建 `review.md`，Review 阶段创建）；本仓禁止 `checklist.md` 等非规范命名，故**不创建** `checklist.md`，验收检查点记录于 Review 阶段的 `review.md`。

## 目标与非目标

### 目标

- 11 个信源 URL 的每条声明都有采集记录、知识归属与覆盖状态；不以「读了标题」代替正文覆盖。
- 按「事实—能力机制—操作演练—信源查证」四层组织，产出可照做的示例与可回溯 F 编号的概念文档。
- **口径分层硬要求（五类，一律不得抹平）**：
  1. **文档口径 vs 平台现状**：本束信源为开发者文档，**本束未在开放平台注册账号、未提交审核、未申请资质、未调用任何真实接口**；不得据文档推断文档未写明的接口字段、限额、审核时长与结算比例（未写明处一律标「官方未给」）。
  2. **声明集合 vs 站点全集**：已声明并处理 11 个 URL（`/dashboard` 导航面 + 10 篇 `/docs/` 内容页）；核验时点站点侧栏可见 **17** 篇 `/docs/` 页，其余 **7** 篇逐条登记「本次未采集，仅登记入口」，**不得**据 slug 名推断其能力细节。
  3. **端与接入形态边界**：Open API 的「本地助理 API」属 PC 端本机能力、「云端任务 / ACP 通道 / 会话产物」属云侧；第三方应用章节的「分享能力接入」当前端边界以该页所述为准并与同组 `workbuddy-open-platform-sharing-and-promotion` 束的公告口径并列互证；「硬件接入与积分兑换」为并列入口而非同类。引用时必须带端别或形态别。
  4. **免费 / 付费资产与变现门槛**：变现需「开通入驻 + 发布付费资产」两步门槛；免费与付费资产的差异、收入管理与结算规则以 `monetization` 页所述为准；文档未给出的分成与结算细节不得补全。
  5. **身份与资质门槛**：入驻需经**个人认证 / 管理员实名认证 / 企业认证（含企业信息上传与企业验证）**，通过资质审核后方可开发对应业务类型；不同业务类型（技能 / 专家 / 专家团 / 连接器 / Buddy 应用 / 第三方应用）的门槛差异按各页登记，不得写成「任意个人开发者可直接发布」。
- **时效并列**：本束核验时点为 **2026-10-16**；文档站未见统一版本号，须与同组 `workbuddy-official-docs`（更新日志止于 **5.7.7 / 2026-10-08**）与 `workbuddy-open-platform-sharing-and-promotion`（平台公告要求客户端 **≥ 5.8.0**，发布 2026-10-14）的版本线**并列登记**，不得择一。
- 接入腾讯生态分组到 bundles 总索引的五级导航与计数（`tencent` → `ecosystems` → `jishu/ai` → `jishu` → `bundles` 总索引），并与同组既有束双向互链。
- **操作可复现性两问判定**：问一「文档是否给出可照做的步骤序列」→ **是**（认证与入驻步骤、技能/专家/连接器目录与配置结构、OAuth 授权码换取凭证、变现四步等均为步骤化描述）；问二「结果是否可在本机闭环判据」→ **否**（审核与上架结果由平台判定）→ **设 `examples/`**，但逐段标注「未在本机实跑」并说明判据取自文档。

### 非目标

- 不复制文档正文原文（不做全文镜像），只做原创归纳 + 事实登记 + 原创操作演练。
- 不注册开放平台账号、不申请个人/管理员实名/企业认证、不提交任何资产审核、不创建真实应用、不生成真实密钥与 token、不调用任何 Open API 端点、不产生任何真实收入与结算数据；所有操作用例明确标注「未在本机实跑」。
- 不采集站点侧栏可见但本次未声明的 7 篇页面（`api-token` / `contact` / `developer-profile` / `legal-basis-and-examples` / `operations-data` / `service-categories-individual` / `service-categories-enterprise`）的正文，仅登记入口与 slug（经用户批准的范围收敛）。
- 不修改同组既有束的事实、计数与正文（仅允许在既有束 `index.md` 回补最小互链）。
- 不修复与本任务无关的并行在途变更与索引漂移（只在 `log.md` 披露观测结果）。
- 不新建分组、不新建顶级类目、不执行 git commit/push。

## 背景与范围

`open.workbuddy.cn` 为腾讯 WorkBuddy 开放平台，其 `/docs/` 子路径承载面向开发者的公开文档（平台概述、入驻认证、业务类型开发指南、Open API 接口参考、收入变现）。`/dashboard` 为平台工作台首页（客户端渲染的应用外壳，无可读正文）。

- **内容敏感度判定**：**公开内容（Public）**——信源为厂商官方开放平台的公开发布文档，不含 `share?code=`/`token=` 等私域访问控制参数，内容主题为面向开发者的平台能力与接入规范。走标准工作流，spec 位于主仓 `.trae/specs/okf-wiki-ecosystem/`，产出物入 `doc/bundles/`。
- **采集方式（核验时点 2026-10-16 实测）**：11 个 URL 全部 **HTTP 200**（`Invoke-WebRequest` 实测），且 `/docs/*` 十篇均为**服务端渲染**，纯 HTTP GET 即可取得完整正文（已实测：`/docs/what-is-open-platform` 与 `/docs/openapi` 经 WebFetch 取得完整正文，无需登录会话）——**与同组 `workbuddy-open-platform-sharing-and-promotion` 束所需的「已登录会话」采集条件不同**，本束无登录依赖。`/dashboard` 实测 HTML 20,367 字节（UTF-8）、含 8 个 `<script>` 与 1 个应用挂载点 → 判定为 SPA 外壳，仅作导航面登记。

### 页面集合（11 个已声明 URL）

| 编号 | URL | 性质 | 核验时点实测（UTF-8 字节） | 解析状态 |
| --- | --- | --- | --- | --- |
| D0 | `https://open.workbuddy.cn/dashboard` | 开放平台首页（导航面） | 200 / 20,367 B / SPA 外壳 | 仅登记入口（无正文） |
| D1 | `/docs/what-is-open-platform` | 开放平台概述 | 200 / 179,640 B | 服务端渲染，正文可读 |
| D2 | `/docs/onboarding` | 入驻与资质认证 | 200 / 196,648 B | 服务端渲染，正文可读 |
| D3 | `/docs/monetization` | 收入变现 | 200 / 204,634 B | 服务端渲染，正文可读 |
| D4 | `/docs/skill` | 技能 | 200 / 203,841 B | 服务端渲染，正文可读 |
| D5 | `/docs/connector` | 连接器 | 200 / 323,746 B | 服务端渲染，正文可读 |
| D6 | `/docs/expert` | 专家 | 200 / 269,332 B | 服务端渲染，正文可读 |
| D7 | `/docs/expert-team` | 专家团 | 200 / 286,687 B | 服务端渲染，正文可读 |
| D8 | `/docs/buddy-app` | Buddy 应用 | 200 / 357,854 B | 服务端渲染，正文可读 |
| D9 | `/docs/third-party-app` | 第三方应用 | 200 / 334,620 B | 服务端渲染，正文可读 |
| D10 | `/docs/openapi` | Open API 接口参考 | 200 / 422,451 B | 服务端渲染，正文可读（体量最大） |

> 上表为 **2026-10-16 实测值**（UTF-8 字节数，取自采集脚本产出的 `meta.json`），用于证明可达性；文档更新后字节数会漂移，引用时须带核验时点。采集脚本提取的正文字符数为 97,917（10 页合计），逐页值见束内 `references/source-manifest.md`。

### 站点侧栏全集与覆盖状态（17 篇 `/docs/` 页）

核验时点从 `/docs/*` 各页 HTML 内嵌侧栏提取到 17 个 `/docs/` slug（另有一个非页面布局资源 `layout-216c2d1532f8d94c`，**必须排除、不计入页面集合**）：

| slug | 本束覆盖状态 |
| --- | --- |
| `what-is-open-platform` / `onboarding` / `monetization` / `skill` / `connector` / `expert` / `expert-team` / `buddy-app` / `third-party-app` / `openapi` | **已声明并处理**（10 篇） |
| `api-token` | 本次未采集，仅登记入口 |
| `contact` | 本次未采集，仅登记入口 |
| `developer-profile` | 本次未采集，仅登记入口 |
| `legal-basis-and-examples` | 本次未采集，仅登记入口 |
| `operations-data` | 本次未采集，仅登记入口 |
| `service-categories-individual` | 本次未采集，仅登记入口 |
| `service-categories-enterprise` | 本次未采集，仅登记入口 |

> **登记纪律**：未采集页仅证明「该 slug 存在于站点侧栏」，**不得**据其名称推断功能细节；且须明确区分「官方未发布该能力」与「本束未采集该页」——前者不可断言，后者如实标注。

### 已核验的页面章节骨架（用于概念剖分，来自 2026-10-16 实测 h1/h2 提取）

| 页面 | 主要章节 |
| --- | --- |
| D1 概述 | 平台简介 / 快速开始（八步）/ 平台优势 |
| D2 入驻 | 个人认证 / 管理员实名认证 / 企业认证 / 认证结果与规则 / 入驻开放平台 / 上传企业信息 / 完成企业验证 |
| D3 变现 | 一、功能概述 / 二、开通入驻 / 三、发布付费资产 / 四、管理收入 / 五、常见问题 |
| D4 技能 | 技能 / 技能基础结构 / 子资源目录说明 / 技能市场 |
| D5 连接器 | 连接器 / 选择接入方式 / CLI + Skill 接入 / MCP + Skill 接入 / 连接器元信息 / 认证与凭证 / Skill 文件 / 图标规范 / 提交前检查 |
| D6 专家 | 专家 / 基础结构 / 模板文件 / 配置文件 / 字段说明 / Agent 定义文件 / 内置 MCP 与连接器依赖（可选）/ 头像规范 / 行业分类 / 专家市场 |
| D7 专家团 | 专家团 / 基础结构 / 模板文件 / 配置文件 / Agent 定义文件 / 内置 MCP 与连接器依赖（可选）/ 头像规范 |
| D8 Buddy 应用 | Buddy 应用 / 产品概述 / 核心定位 / 六大自定义维度 / WorkBuddy 基础能力 / 配置指引 / 发布流程 / 企业单管理 / Buddy 应用设计规范 / 最佳实践建议 |
| D9 第三方应用 | 第三方应用 / 分享能力接入 / 硬件接入与积分兑换 |
| D10 Open API | 准备工作 / 认证授权 API / 个人资料 API / 本地助理 API / 云端任务 API / ACP 通道 / 会话产物 / 兑换码核销 API / 返回码规范 |

> 该骨架仅作**概念剖分与读者导览**用途；实施时以实际正文为准，若与实读不一致须在 `tasks.md` 记录偏差（同组先例：曾出现「模块地图 14 项」实为 13 项的笔误）。

### 采集边界

- 仅采集上述 11 个 URL 的正文与 `/docs/*` 页内嵌侧栏可见的 slug 清单。
- 正文中提及但未展开的指事物（如平台内部页面路径、客户端版本、第三方规范）**仅登记为指引入口**，不展开学习；不做站外递归抓取。
- 不采集开放平台后台的操作型页面（注册应用、提交审核、发布资产等，需真实账号且会产生真实数据）。

### 知识包分层设计（新束结构，共 24 个 Markdown）

```text
workbuddy-open-platform-docs/
├── index.md
├── log.md
├── concepts/    （index.md + 00～10 十一篇）
├── examples/    （index.md + 00～04 五篇）
└── references/  （index.md + article-source.md + source-manifest.md + verification.md）
```

| 层 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| concepts | `00-overview-and-quickstart` | 开放平台是什么？能开发哪些业务类型？从入驻到上线的八步是什么？ |
| concepts | `01-onboarding-and-qualification` | 个人认证 / 管理员实名认证 / 企业认证分别怎么做？入驻与上传企业信息到企业验证怎么走？失败规则是什么？ |
| concepts | `02-skill-development-and-marketplace` | 技能的基础结构与子资源目录是什么？怎么进技能市场？ |
| concepts | `03-connector-development-and-access-modes` | 连接器的 CLI + Skill 与 MCP + Skill 两种接入方式怎么选？元信息、认证与凭证、图标规范、提交前检查是什么？ |
| concepts | `04-expert-and-expert-team` | 专家与专家团的结构差异是什么？配置文件、字段、Agent 定义文件、行业分类怎么定？ |
| concepts | `05-buddy-app-develop-and-publish` | Buddy 应用的核心定位与六大自定义维度是什么？怎么配置、发布、管理企业单？设计规范与最佳实践是什么？ |
| concepts | `06-third-party-app-access` | 第三方应用有哪些接入形态（分享能力、硬件接入与积分兑换）？与开发者自研资产的区别是什么？ |
| concepts | `07-openapi-auth-and-conventions` | 调接口前的准备工作是什么？OAuth 2.1 授权码怎么换 access_token / refresh_token？返回码规范怎么看？ |
| concepts | `08-openapi-endpoint-catalog` | 个人资料 / 本地助理 / 云端任务 / ACP 通道 / 会话产物 / 兑换码核销六类接口各能做什么？权限与形态边界在哪？ |
| concepts | `09-monetization-and-revenue` | 变现功能怎么开通？怎么发布付费资产、管理收入？常见问题有哪些？ |
| concepts | `10-boundaries-versions-and-known-gaps` | 五类口径分层是什么？哪些是未采集页、哪些是官方未给、版本与时效怎么并列？ |
| examples | `00-onboarding-and-certification` | 照做：个人认证 → 管理员实名认证 → 企业认证 → 入驻 → 上传企业信息 → 完成企业验证 |
| examples | `01-build-and-submit-a-skill` | 照做：技能目录结构 → 元信息与子资源 → 本地调试 → 提交审核 → 上架技能市场 |
| examples | `02-build-and-submit-a-connector` | 照做：选接入方式 → 写 Skill 文件与元信息 → 配认证与凭证 → 图标规范 → 提交前检查 |
| examples | `03-oauth-and-call-openapi` | 照做：`/authorize` 取授权码 → `/token` 换凭证 → 调个人资料 / 本地助理接口 → 刷新凭证 → 读返回码 |
| examples | `04-publish-and-manage-a-paid-asset` | 照做：开通入驻 → 发布付费资产 → 管理收入与常见问题排查 |
| references | `article-source` / `source-manifest` / `verification` | 每条说法的出处、页级覆盖台账与核验结论 |

## 功能需求

- **FR-1**：新建 bundle `workbuddy-open-platform-docs/`，含根 `index.md`、`log.md`、`concepts/`（索引 + 11 篇）、`examples/`（索引 + 5 篇）、`references/`（索引 + 3 篇），共 **24 个 Markdown**；每个含子目录的层级生成 `index.md` 并以 `{toctree}` 引用全部内容文档。
- **FR-2**：`references/source-manifest.md` 登记页级台账——11 个已声明 URL 逐条含 URL、访问日期、页面标题、HTTP 状态与字节数、正文解析状态、知识归属文档、覆盖状态；站点侧栏 17 个 slug 逐条含 slug 与覆盖状态（已处理 10 / 未采集 7，标注「本次未采集，仅登记入口」）；明确排除非页面资源 `layout-216c2d1532f8d94c` 并说明排除依据；以集合比对证明「已声明页面集合 = 已处理集合」（双向差集为空）。
- **FR-3**：R 阶段产出 spec 目录 `facts.md`，登记 `F-001` 起编号事实；`references/article-source.md` 双份登记同一编号集合，两处正则提取的 `F-\d{3}` 集合相等、连续无跳号、无重复。
- **FR-4**：`references/verification.md` 给出核验总表（核验时点、11 URL 可达性、侧栏 17 slug 提取结果）、勘误清单、**五类口径分层并列登记表**、信源距离评估（厂商文档单源）、V 四视角对抗审查表、status 裁决节。
- **FR-5**：concepts 11 篇中所有具体声明（步骤、字段名、章节名、接口名、业务类型名、门槛条件、状态码）带 F 编号引用；五类口径分层在全束一致落地；含至少 1 张 Mermaid 图（建议：开放平台八步上架流程图，或 OAuth 2.1 授权码换取凭证的时序图）。
- **FR-6**：examples 5 篇提供前置条件、操作步骤、结果判据与限制说明；未在本机实跑的步骤显式标注「未在本机实跑，依据官方文档（F-xxx）」；不得编造文档未给出的接口参数、字段取值与审核时长。
- **FR-7**：五级索引接入与计数同步——`tencent/index.md`（导航表 +1 行、toctree +1 条、「关于本分组」束数与概念/示例/信源/事实计数、「相关链接」+1 行）、`ecosystems/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`（`total_bundles` 与各层级计数）；全部数字以实施时**机械真值**为准，不得手工估算。
- **FR-8**：双向互链——新束 `index.md`「主题关联」链同组 `workbuddy-official-docs`（产品/四端文档与版本线口径对照）、`workbuddy-open-platform-sharing-and-promotion`（开放平台公告与端边界互证）、`workbuddy-hardware-integration-whitepaper`（硬件接入与商务口径对照）、`codebuddy`；并在 `workbuddy-official-docs/index.md` 与 `workbuddy-open-platform-sharing-and-promotion/index.md` 各回补 **1 条**指向新束的链接（最小改动，不动其事实与计数）。
- **FR-9**：`log.md` 记录七阶段执行、口径决策、并行在途观测、门禁运行方式（直接运行底层脚本；`invoke gates.*` 若不可用不谎报）。
- **FR-10**：`index.md` 含「已知边界」段，集中声明五类口径、单源清单、未实跑声明、未采集 7 页清单与时效项，并区分「官方未宣告」与「本束未采集」。

## 非功能需求与约束

- **NFR-1（规范一致）**：全部文件遵循 OKF v0.2 frontmatter（`okf_version` 仅出现在 bundle 根 `index.md`；子文档 `type` 取 `Concept`/`Example`/`Reference`；`generated`/`verified` 使用 `process:seven-concepts-*` actor 约定；`status`/`stale_after`/`sources` 齐备），中文正文，kebab-case 英文文件名。
- **NFR-2（机械质量）**：UTF-8 严格 roundtrip 无 BOM 无乱码；全部 Markdown 相对链接可达（`Test-Path`）；零 `file:///`、零 `C:\Users` 等本机绝对路径；每个 `index.md` 含 toctree 且条目逐一存在。
- **NFR-3（时效管理）**：`stale_after` 设为 `2027-04-16`；核验时点、页面字节数与版本线对照在「已知边界」集中声明。
- **NFR-4（可审计）**：核验信源全部为实际读取成功的 URL，禁止编造；无法核验项标「仅官方单源」或「本次未采集」，不升级可信度；未实跑的操作显式标注。
- **NFR-5（子模块纪律）**：产出在 git submodule `projects/awesome-okf-xs/`，**不提交**；写入前检查子模块无 merge/rebase 进行中；保护其他会话变更，不改无关共享索引的既有数字。
- **NFR-6（临时文件隔离）**：采集缓存（HTML 抓取结果）、复算脚本等临时产物放工作区外或项目 `.temp/` 用后删除；最终资料仅入目标 bundle，规划仅入本 spec 目录。

## 约束

- **Technical**：Windows + PowerShell 7 + Python（py314）；门禁脚本在子模块根目录直接运行（`python scripts/check-toctrees.py`、`python scripts/check-utf8.py`、`python scripts/check-bundles-index.py`）；采集使用纯 HTTP GET 即可，**无登录依赖**（例外见假设）。
- **Business**：遵循 SpecWeave 启动协议与文档边界（公开内容标准工作流，spec 在主仓 `.trae/specs/okf-wiki-ecosystem/`）；用户沟通中文、动作导向。
- **Dependencies**：`open.workbuddy.cn` 可达；门禁脚本可用；子模块工作树完整。

## 假设

- 归属 `jishu/ai/ecosystems/tencent/` 无争议：WorkBuddy 为腾讯出品，同分组已有 5 个 WorkBuddy 束先例，不单新建分组；同时**不**在 `jishu/ai/products/` 重复建束（避免双份事实源）。
- 骨架按「开发者文档教程化」判定：文档提供步骤化的开发/上架/接入链路 → 设 `examples/`；但审核与上架结果由平台判定、本机无法闭环 → examples 逐段标注未实跑。
- 核验时点 `2026-10-16` 的页面状态即本束快照基准；此后文档更新不在本束范围（`stale_after` 到期复核）。
- 采集主通道为纯 HTTP GET（已实测十篇 `/docs/*` 为服务端渲染）；**若实施时发现某页改为客户端渲染导致正文缺失**，改由受控浏览器渲染读取，并把该页通道变化记入 `source-manifest.md` 与 `log.md`；仍不可得则如实记「未取得」并降级为「仅登记入口」，**不虚构内容**。
- `/dashboard` 为 SPA 外壳，本束仅登记为导航面；其登录后的工作台功能不在本束范围（同组已由 `workbuddy-open-platform-sharing-and-promotion` 束登记平台模块地图）。

## 验收标准

### AC-1：信源覆盖与事实编号可溯源

- **Type**: `rule`
- **通过条件**：11 个已声明 URL 逐条有页级台账记录（URL、访问日期、标题、HTTP 状态与字节数、正文解析状态、知识归属、覆盖状态七要素）；`source-manifest.md` 声明的页面集合与已处理集合双向差集为空（10 篇 docs 取正文、`/dashboard` 记导航面）；站点侧栏 17 slug 逐条登记且 7 篇未采集逐条标注「本次未采集，仅登记入口」；非页面资源 `layout-216c2d1532f8d94c` 被显式排除且给出依据；spec `facts.md` 与 `references/article-source.md` 的 `F-\d{3}` 编号集合相等、连续无跳号、无重复；无未标注的推断；不做任何 F 编号重排或覆写（本束自 F-001 起，不与同组既有束编号体系混合）。
- **Evidence**：`references/source-manifest.md` 页级台账 + 集合差异机械比对输出 + 正则编号集合比对输出。

### AC-2：五类口径分层准确

- **Type**: `rule`
- **通过条件**：五类口径在 `references/verification.md` 与 concepts 正文中均有独立小节或表格行呈现——①文档口径 vs 平台现状（明确列出「未实跑」「官方未给」的清单）；②声明集合 vs 站点全集（11 vs 17，7 篇未采集逐条）；③端与接入形态边界（PC 本地助理 / 云侧任务与 ACP 与会话产物 / 第三方应用分享与硬件入口，并与同组公告束口径并列互证）；④免费 / 付费资产与变现开通门槛；⑤身份与资质门槛（个人认证 / 管理员实名认证 / 企业认证三档）＋版本时效并列（文档站无统一版本号 vs 产品文档 5.7.7 vs 公告 5.8.0）。不得出现替官方宣布的「已 GA / 已上线 / 已完成审核」类表述；不得把未采集写成不存在、把未实跑写成已验证。
- **Evidence**：`verification.md` 口径分层并列登记表 + concepts 正文对照 + Grep 抽查记录。

### AC-3：五级索引与计数同步

- **Type**: `rule`
- **通过条件**：`python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0（frontmatter / 计数行 / 节标题 / 分组表 / toctree 五面一致）；新束在 `tencent/index.md` 导航表与 toctree 均出现；五级索引写入的数字与脚本输出逐项相等；`python scripts/check-toctrees.py` 全量输出过滤本束名零命中（既有/并行污染项只在 `log.md` 列名披露，不顺手修复）。
- **Evidence**：门禁脚本输出 + 机械复算记录。

### AC-4：机械门禁与独立审查

- **Type**: `rule`
- **通过条件**：`python scripts/check-utf8.py` 通过；全部新增文件的相对链接 `Test-Path` 存活；零 `file:///`、零本机绝对路径；frontmatter 必填字段逐文件核对通过（`okf_version` 仅出现在根 `index.md`；`log.md` 与三个子目录 `index.md` 无 frontmatter）；定向 Sphinx dummy 构建无本束引入的错误；最新独立 Review 结果为 `pass`。全库既有/并行问题按归属隔离并如实报告，不声称全库通过。
- **Evidence**：门禁脚本输出、构建结果、`review.md`。

### AC-5：同组互链与最小改动纪律

- **Type**: `rule`
- **通过条件**：新束 `index.md`「主题关联」含指向同组既有 3 束（`workbuddy-official-docs` / `workbuddy-open-platform-sharing-and-promotion` / `workbuddy-hardware-integration-whitepaper`）与 `codebuddy` 的链接；`workbuddy-official-docs/index.md` 与 `workbuddy-open-platform-sharing-and-promotion/index.md` 的 `git diff` 各恰为 **+1** 条互链，其事实、计数、正文其他部分零改动；本束**未**修改同组其他束的任何文件（`git status` 逐文件核对）。
- **Evidence**：`git diff --stat` 与逐文件 diff 记录。

### AC-6：教程可用性与知识分层质量

- **Type**: `rubric`
- **维度**：从「了解开放平台能开发什么」到「照做入驻 / 开发并上架资产 / 接入 Open API / 开通变现」的可用性，以及事实—机制—操作—查证四层的分层清晰度。
- **量表**：1-5。
- **锚点**：1 = 文档原文平铺堆砌（含直接照搬接口表），读者无法照做也无法判断可信度；3 = 主题齐全、有分层但前置条件/结果判据不清，五类口径分层不统一，接口分类与形态边界含混；5 = 每篇回答一个明确问题，examples 具备前置/步骤/判据/限制且未实跑处显式标注，concepts 每条具体声明可回溯 F 编号，七类接口与端/形态边界清晰、五类口径标签全文一致，「已知边界」可直接支持入驻门槛与接入方案判断。
- **通过阈值**：>= 4。
- **Evidence**：concepts 11 篇 + examples 5 篇 + 根 `index.md`「已知边界」；独立评审逐篇抽查评分。

## 待决事项

- 无阻断性范围歧义。以下为实施时按既有裁决执行、无需再确认的事项：
  1. **范围已收敛**（经用户 2026-10-16 确认）：严格按 11 个 URL；侧栏其余 7 篇仅登记入口，不采集正文。
  2. **束粒度已裁定**（经用户 2026-10-16 确认）：**单束** `workbuddy-open-platform-docs`，Open API 拆为 `07`（认证与约定）+ `08`（接口目录）两篇概念，不单独建束。
  3. **bundle 目录名**采用 `workbuddy-open-platform-docs`（与同组 `workbuddy-official-docs` 命名族一致）。
  4. 不执行 git commit/push。
  5. 计数以机械真值复算为准，并行漂移只披露不修复。
  6. `stale_after: 2027-04-16`。
  7. `status` 目标 `stable`（若 V 阶段发现核心声明证伪则转 `flagged`/`draft`）。
  8. 不同组既有束的事实与计数，仅在两束 `index.md` 各回补 1 条互链。
