---
type: spec
title: "WorkBuddy 开放平台两篇平台公告学习 → OKF Wiki 知识包"
status: completed
methodology: seven-concepts-cmd
content-sensitivity: public
source:
  - https://open.workbuddy.cn/dashboard/contents/ann_1791894782641_zyedev?source=announcement
  - https://open.workbuddy.cn/dashboard/contents/ann_1790063369912_8degpw?source=announcement
---

# WorkBuddy 开放平台两篇平台公告学习 → OKF Wiki 知识包

## 概述

- **目的**：全面学习 WorkBuddy 开放平台（`open.workbuddy.cn`）「平台公告」栏目的两篇上线公告——「分享能力接入」与「推广管理」，把「平台能力边界 + 可照做配置链路 + 版本与开放门槛」转化为一个可溯源、有时效管理、口径分层的中文 OKF v0.2 知识包。
- **读者**：想让第三方应用把内容分享进 WorkBuddy 的开发者与产品经理；想为已发布资产（专家 / 技能 / 连接器 / Buddy 应用）做站外推广与效果追踪的资产作者；需要判断平台开放边界与版本门槛的团队。
- **目标目录**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/workbuddy-open-platform-sharing-and-promotion/`（腾讯生态分组，与既有 4 个 WorkBuddy 束同组）。
- **基线**：本束为**新建**，无既有 F 编号与文档，事实编号自 `F-001` 起。同组已有 `workbuddy-official-docs`（产品与四端文档全站学习）、`workbuddy-one-sentence-mvp`、`workbuddy-sandbox-public-endpoint`、`tencent-buddy-family`、`wecom-5-0-12-release`；本束**不覆写**其事实与计数，仅做互链。
- **工作流**：七概念知识沉淀链路 `R→I→E→V`；实施前经批准门，完成后独立上下文审查。Git 提交须另获用户明确授权。

## 目标与非目标

### 目标

- 两篇公告的每条声明都有采集记录、知识归属与覆盖状态；不以「读了标题」代替正文覆盖。
- 按「事实—能力机制—操作演练—信源查证」四层组织，产出可照做的示例与可回溯 F 编号的概念文档。
- **口径分层硬要求（五类，一律不得抹平）**：
  1. **公告口径 vs 平台现状**：公告为上线通知，正文**未**给出接口字段、请求参数、错误码、审核细则与配额数字；不得据公告推断公告未写的接口细节（如需接口级内容须另立新束学习《PC 端开发手册》）。
  2. **端边界**：分享能力接入**当前仅 PC 端**（Windows 应用 / macOS 应用），移动端（Android / iPhone / 鸿蒙应用）公告原话为「将陆续开放」——属规划态，不得写成已支持。
  3. **资产类型差异**（推广管理）：专家与技能类资产支持「分享链接 + 微信小程序码」；连接器**暂时仅支持**「分享链接」；Buddy 应用分享功能「正在规划中」；免费资产支持两种，**付费资产暂时仅支持**「分享链接」。
  4. **版本时效与落差**：两篇公告均发布于 **2026-10-14**，且均要求客户端 **≥ 5.8.0**（低于该版本无法唤起）；而同组 `workbuddy-official-docs` 束于 2026-10-15 核验到官方文档更新日志止于 **5.7.7（2026-10-08）**——存在「公告先行于产品文档版本线」的口径落差，须并列登记而非择一。
  5. **开放对象与身份门槛**：分享能力接入面向**已通过企业认证的开发者**开放，应用创建与密钥生成均在开放平台完成；不得写成对任意个人开发者开放。
- 接入腾讯生态分组到 bundles 总索引的五级导航与计数（`tencent` → `ecosystems` → `jishu/ai` → `jishu` → `bundles` 总索引），并与同组既有束双向互链。
- **操作可复现性两问判定**：两篇公告均给出可照做的配置链路（分享能力接入：注册应用 → 填基础配置/应用平台信息 → 提交审核 → 生成密钥；推广管理：新建推广 → 选推广方式/填渠道标签 → 复制/下载/停用 → 查看推广效果）→ **设 `examples/`**。

### 非目标

- 不复制公告正文原文（不做全文镜像），只做原创归纳 + 事实登记 + 原创操作演练。
- 不实际注册开放平台账号、不提交真实应用审核、不生成真实密钥、不创建真实推广、不产生真实投放与安装量数据；所有操作用例明确标注「未在本机实跑」。
- 不采集或转述《PC 端开发手册》的接口细节（公告未给出，且属另一信源），本束仅登记该手册作为接入开发的入口指引。
- 不修改同组既有束的事实、计数与正文（仅允许在既有束 `index.md` 回补最小互链）。
- 不修复与本任务无关的并行在途变更与索引漂移（只在 `log.md` 披露观测结果）。
- 不新建分组、不新建顶级类目、不执行 git commit/push。

## 背景与范围

`open.workbuddy.cn` 为腾讯 WorkBuddy 开放平台，其「平台公告」栏目承载面向开发者/合作方的公开发布通知。页面为 SPA，需登录会话方可读取渲染后正文。

- **内容敏感度判定**：公开内容（Public）——信源为厂商官方开放平台的公开发布通知，不含 `share?code=`/`token=` 等私域访问控制参数，内容主题为平台能力上线通告（面向开发者公开发布）。走标准工作流，spec 位于主仓 `.trae/specs/okf-wiki-ecosystem/`，产出物入 `doc/bundles/`。
- **采集方式**：本次经受控浏览器在**已登录会话**中读取渲染后正文（`document.body.innerText`），两页均已取得**完整正文**（非摘要、非截断）；核验时点 **2026-10-15**。

### 页面集合（2 条内容页 + 平台导航面）

| 编号 | URL | 性质 | 解析状态 |
| --- | --- | --- | --- |
| A1 | `https://open.workbuddy.cn/dashboard/contents/ann_1791894782641_zyedev?source=announcement` | 平台公告：分享能力接入（2026-10-14） | 已取得完整正文 |
| A2 | `https://open.workbuddy.cn/dashboard/contents/ann_1790063369912_8degpw?source=announcement` | 平台公告：推广管理（2026-10-14） | 已取得完整正文 |
| N1 | `https://open.workbuddy.cn/` | 开放平台入口（导航面） | 可达 |
| N2 | `https://open.workbuddy.cn/dashboard` | 开放平台首页（导航面） | 可达 |

### 平台模块地图（来自公告页侧边栏，仅作导航登记）

| 模块 | 路径 | 登记价值 |
| --- | --- | --- |
| Buddy 应用 | `/buddy-app/all` | 资产类型之一（公告：分享功能规划中） |
| 专家 | `/expert/all` | 资产类型之一（支持分享链接 + 小程序码） |
| 技能 | `/skill/all` | 资产类型之一（支持分享链接 + 小程序码） |
| 连接器 | `/connector/all` | 资产类型之一（仅分享链接） |
| 硬件接入 | `/application/all/device` | 平台模块（本束不覆盖其内容） |
| 分享功能接入 | `/app-feature/all` | **A1 的功能入口** |
| 积分兑换 | `/application/all/credit` | 平台模块（本束不覆盖其内容） |
| 推广管理 | `/growth` | **A2 的功能入口** |
| 数据概览 | `/operations` | 平台模块 |
| 推广效果 | `/growth/effect` | **A2 的数据入口** |
| 收入变现 | `/monetization` | 平台模块 |
| 认证信息 | `/settings/cert-info` | 与「企业认证」开放门槛相关 |
| 开发者信息 | `/settings/developer` | 与开发者身份相关 |

> **登记纪律**：模块地图仅证明「这些入口在公告页侧边栏存在」，**不得**据模块名称推断其功能细节（各模块独立页本次未采集）。凡未采集的模块，在文档中标注「本次未采集，仅登记入口」。

### 采集边界

- 仅采集上述 A1/A2 两篇公告正文与公告页侧边栏可见的平台导航面。
- 公告正文中提及但未展开的指向物（《PC 端开发手册》、WorkBuddy 品牌设计规范、WorkBuddy 客户端 5.8.0）**仅登记为指引入口**，不展开学习；不做站外递归抓取。
- 不采集开放平台后台的「注册应用」「新建推广」等**操作型页面**（需真实账号且会产生真实数据）。

### 知识包分层设计（新束结构，共 14 个 Markdown）

```text
workbuddy-open-platform-sharing-and-promotion/
├── index.md
├── log.md
├── concepts/    （index.md + 00～03 四篇）
├── examples/    （index.md + 00～01 两篇）
└── references/  （index.md + article-source.md + source-manifest.md + verification.md）
```

| 层 | 文档 | 读者要回答的问题 |
| --- | --- | --- |
| concepts | `00-open-platform-overview` | WorkBuddy 开放平台是什么？有哪些模块？这两篇公告在平台中的位置？ |
| concepts | `01-share-capability-integration` | 分享能力接入是什么？第三方应用怎么接入？审核与密钥怎么办？用户侧流程与版本要求是什么？ |
| concepts | `02-promotion-management` | 推广管理是什么？怎么创建、配置、管理？怎么查看推广效果？不同资产类型差异在哪？ |
| concepts | `03-boundaries-versions-and-policy` | 版本门槛、开放对象、端边界、资产与付费边界、品牌规范、与产品文档版本线的口径落差是什么？ |
| examples | `00-integrate-share-capability` | 照做：注册应用 → 填配置 → 提交审核 → 生成密钥 → 接入开发 |
| examples | `01-create-and-track-promotion` | 照做：新建推广 → 选推广方式/填渠道标签 → 复制/下载/停用 → 查看推广效果 |
| references | `article-source` / `source-manifest` / `verification` | 每条说法的出处、页面覆盖台账与核验结论 |

## 功能需求

- **FR-1**：新建 bundle `workbuddy-open-platform-sharing-and-promotion/`，含根 `index.md`、`log.md`、`concepts/`（索引 + 4 篇）、`examples/`（索引 + 2 篇）、`references/`（索引 + 3 篇），共 **14 个 Markdown**；每个含子目录的层级生成 `index.md` 并以 `{toctree}` 引用全部内容文档。
- **FR-2**：`references/source-manifest.md` 登记页面级台账（A1/A2/N1/N2 及平台模块地图），逐条含 URL、访问日期、标题、正文解析状态（已取得完整正文 / 仅登记入口 / 可达）、知识归属文档、覆盖状态；并以集合比对证明「已声明页面集合 = 已处理集合」。
- **FR-3**：R 阶段产出 spec 目录 `facts.md`，登记 `F-001` 起编号事实；`references/article-source.md` 双份登记同一编号集合，两处正则提取的 `F-\d{3}` 集合相等、连续无跳号。
- **FR-4**：`references/verification.md` 给出核验总表（公告日期与版本、两篇公告口径一致性、与 `workbuddy-official-docs` 束版本线（5.7.7）的落差）、勘误清单、**五类口径分层并列登记表**、V 四视角对抗审查表、status 裁决。
- **FR-5**：concepts 4 篇中所有具体声明（日期、版本号、模块路径、资产类型、数量）带 F 编号引用；五类口径分层在全束一致落地；含至少 1 张 Mermaid 图（分享能力接入的「接入方 → 开放平台 → 用户 → WorkBuddy」链路流程图或推广管理生命周期图）。
- **FR-6**：examples 2 篇提供前置条件、操作步骤、结果判据与限制说明；未在本机实跑的步骤显式标注「未在本机实跑，依据官方公告（F-xxx）」。
- **FR-7**：五级索引接入与计数同步——`tencent/index.md`（导航表 +1 行、toctree +1 条、「关于本分组」束数与概念/示例/信源/事实计数、「相关链接」+1 行）、`ecosystems/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`（`total_bundles` 与各层级计数）；全部数字以实施时**机械真值**为准，不得手工估算。
- **FR-8**：双向互链——新束 `index.md`「主题关联」链同组 `workbuddy-official-docs`（版本线口径对照）、`workbuddy-one-sentence-mvp`、`codebuddy`；并在 `workbuddy-official-docs/index.md` 回补 **1 条**指向新束的链接（最小改动，不动其事实与计数）。
- **FR-9**：`log.md` 记录七阶段执行、口径决策、并行在途观测、门禁运行方式（直接运行底层脚本；`invoke gates.*` 若不可用不谎报）。

## 非功能需求与约束

- **NFR-1（规范一致）**：全部文件遵循 OKF v0.2 frontmatter（`okf_version` 仅出现在 bundle 根 `index.md`；子文档 `type` 取 `Concept`/`Example`/`Reference`；`generated`/`verified` 使用 `process:seven-concepts-*` actor 约定；`status`/`stale_after`/`sources` 齐备），中文正文，kebab-case 英文文件名。
- **NFR-2（机械质量）**：UTF-8 严格 roundtrip 无 BOM 无乱码；全部 Markdown 相对链接可达（`Test-Path`）；零 `file:///`、零 `C:\Users` 等本机绝对路径；每个 `index.md` 含 toctree 且条目逐一存在。
- **NFR-3（时效管理）**：`stale_after` 设为 `2027-04-15`；版本号与发布日期等时效项在「已知边界」集中声明。
- **NFR-4（可审计）**：核验信源全部为实际读取成功的 URL，禁止编造；无法核验项标「仅官方单源」，不升级可信度；未实跑的操作显式标注。
- **NFR-5（子模块纪律）**：产出在 git submodule `projects/awesome-okf-xs/`，**不提交**；写入前检查子模块无 merge/rebase 进行中；保护其他会话变更，不改无关共享索引。
- **NFR-6（临时文件隔离）**：采集缓存、复算脚本等临时产物放工作区外（或 `.temp/` 用后删除）；最终资料仅入目标 bundle，规划仅入本 spec 目录。

## 约束

- **Technical**：Windows + PowerShell 7 + Python（py314）；门禁脚本在子模块根目录直接 `python scripts/<name>.py` 运行（`check-toctrees.py`、`check-utf8.py`、`check-bundles-index.py`）。
- **Business**：遵循 SpecWeave 启动协议与文档边界（公开内容标准工作流，spec 在主仓 `.trae/specs/okf-wiki-ecosystem/`）；用户沟通中文、动作导向。
- **Dependencies**：受控浏览器的已登录会话（A1/A2 正文本次已取得）；门禁脚本可用性；子模块工作树完整。

## 假设

- 归属 `jishu/ai/ecosystems/tencent/` 无争议：WorkBuddy 为腾讯出品，同分组已有 4 个 WorkBuddy 束先例，不单新建分组；同时**不**在 `jishu/ai/products/` 重复建束（避免双份事实源）。
- 骨架按「平台公告教程化」判定：两篇公告均提供可照做的配置链路 → 设 `examples/`；但公告本身信息量小于产品文档，故 concepts 收敛为 4 篇、examples 为 2 篇（不照搬 `workbuddy-official-docs` 的 12+9 规模）。
- 核验时点 `2026-10-15` 的页面状态即本束快照基准；此后新增公告不在本束范围（`stale_after` 到期复核）。
- 「企业认证」为接入分享能力的门槛，但公告未给认证流程细节——本束只登记「面向已通过企业认证的开发者开放」这一门槛事实，不展开认证流程。

## 验收标准

### AC-1：信源覆盖与事实编号可溯源

- **Type**: `rule`
- **通过条件**：A1/A2 两篇公告均取得完整正文并有页级台账记录（URL、访问日期、标题、正文解析状态、知识归属、覆盖状态）；`source-manifest.md` 声明的页面集合与处理集合双向差集为空；平台模块地图逐行登记且逐行标注「本次未采集，仅登记入口」；spec `facts.md` 与 `references/article-source.md` 的 `F-\d{3}` 编号集合相等、连续无跳号、无重复；无未标注的推断；不做任何 F 编号重排或覆写（本束自 F-001 起，不与同组既有束编号体系混合）。
- **证据**：`references/source-manifest.md` 页级台账 + 集合差异机械比对输出 + 正则编号集合比对输出。

### AC-2：五类口径分层准确

- **Type**: `rule`
- **通过条件**：五类口径在 `verification.md` 与 concepts 正文中均有独立小节或表格行呈现——①公告口径 vs 平台现状（不得推断公告未写的接口细节）；②端边界（PC 端已支持 / 移动端规划态）；③资产类型与付费边界（专家/技能 vs 连接器 vs Buddy 应用；免费 vs 付费）；④版本时效与落差（公告 2026-10-14 与 5.8.0 门槛 vs 产品文档版本线止于 5.7.7）；⑤开放对象与企业认证门槛。不得出现替官方宣布的「已 GA / 已上线」类表述（官方未明示者）；不得把规划态写成已支持。
- **证据**：`verification.md` 口径分层并列登记表 + concepts 正文对照 + Grep 抽查记录。

### AC-3：五级索引与计数同步

- **Type**: `rule`
- **通过条件**：`python scripts/check-bundles-index.py` 在无并行写入窗口退出码 0（五面计数一致）；新束在 `tencent/index.md` 导航表与 toctree 均出现；五级索引写入的数字与脚本输出逐项相等；`python scripts/check-toctrees.py` 全量输出过滤本束名零命中（既有/并行污染项只在 `log.md` 列名披露，不顺手修复）。
- **证据**：门禁脚本输出 + 机械复算记录。

### AC-4：机械门禁与独立审查

- **Type**: `rule`
- **通过条件**：`python scripts/check-utf8.py` 通过；全部新增文件的相对链接 `Test-Path` 存活；零 `file:///`、零本机绝对路径；frontmatter 必填字段逐文件核对通过（`okf_version` 仅出现在根 `index.md`）；定向 Sphinx dummy 构建无本束引入的错误；最新独立 Review 结果为 `pass`。全库既有/并行问题按归属隔离并如实报告，不声称全库通过。
- **证据**：门禁脚本输出、构建结果、`review.md`。

### AC-5：同组互链与最小改动纪律

- **Type**: `rule`
- **通过条件**：新束 `index.md`「主题关联」含指向同组既有束的反向链接；`workbuddy-official-docs/index.md` 的 `git diff` 恰为 **+1** 条互链，其事实、计数、正文其他部分零改动；本束**未**修改同组其他束的任何文件。
- **证据**：`git diff --stat` 与逐文件 diff 记录。

### AC-6：教程可用性与知识分层质量

- **Type**: `rubric`
- **维度**：从「了解开放平台能力」到「照做接入/推广配置」的可用性，以及事实—机制—操作—查证四层的分层清晰度。
- **量表**：1-5。
- **锚点**：1 = 公告原文平铺堆砌，读者无法照做也无法判断可信度；3 = 主题齐全、有分层但前置条件/结果判据不清，口径分层不统一；5 = 每篇回答一个明确问题，examples 具备前置/步骤/判据/限制且未实跑处显式标注，concepts 每条具体声明可回溯 F 编号，五类口径标签全文一致，「已知边界」可直接支持接入决策与推广排期判断。
- **通过阈值**：>= 4。
- **证据**：concepts 4 篇 + examples 2 篇 + 根 `index.md`「已知边界」；独立评审逐篇抽查评分。

## 待决事项

- 无阻断性范围歧义。以下为实施时按既有裁决执行、无需再确认的事项：
  1. **bundle 目录名**采用 `workbuddy-open-platform-sharing-and-promotion`（内容描述型命名）；若用户希望改为更泛化的 `workbuddy-open-platform-*`，在批准门阶段指出即可。
  2. 不执行 git commit/push。
  3. 计数以机械真值复算为准，并行漂移只披露不修复。
  4. `stale_after: 2027-04-15`。
  5. `status` 目标 `stable`（若 V 阶段发现核心声明证伪则转 `flagged`/`draft`）。
  6. 不同组既有束的事实与计数，仅 `workbuddy-official-docs/index.md` 回补 1 条互链。
