# Spec：秒悟 Meoo 官方文档站（docs.meoo.com）OKF Wiki 教程双束沉淀

> 创建：2026-10-18 ｜ 方法论：seven-concepts-cmd 场景4「知识沉淀」链路 R→I→E（V 由 Spec Mode 独立评审门承接）
> Session：sc-20261018-meoo-docs ｜ 内容级别：**公开内容**（官方公开文档，无访问控制）

## 1. 问题陈述

秒悟（Meoo）官方文档站 `docs.meoo.com` 承载平台完整能力说明，但当前 OKF 库 miaowu 组下 3 个知识束只覆盖大使入驻、实训案例与赏金广场三个运营侧主题，**平台产品能力与开发者文档在知识库中完全空白**：库内读者无法一站式回答"秒悟能做什么、怎么构建/部署、如何开放集成"。

用户要求全面学习 18 个官方 URL 并在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/miaowu/` 恰当位置生成 OKF wiki 教程。

## 2. 用户与使用场景

- **库内检索者**：从 bundles 总索引进入，想在 30 分钟内建立 Meoo 平台全景认知并完成首次应用构建/部署。
- **外部 Agent 生态集成者**：需要团队 AK/SK→MEOO_TOKEN 的准确接入步骤与凭证边界（只能信逐字命令，不能信二手转述）。
- **后续知识维护者**：依赖 source-ledger/verification 判断哪些结论已核验、哪些会过期（模型版本、套餐额度、权益状态）。

## 3. 目标

1. 将 18 个官方页面（主页 1 + features 15 + open 1 + open/guides/cli 1，其中 `/features/cli` 与 `/open/guides/cli` 已证实**非重复页**）系统转译为符合 OKF v0.2 规范的教程型知识束（任务启动时 spec 误写 v0.3；经全库基线核验 645 个存量束均为 `okf_version: "0.2"`，Task 1 决策按库基线统一 0.2，独立评审已确认该偏差合理）。
2. 全部事实可回溯到源 URL + 章节（F 编号台账），P0 事实（命令/端点/版本/限额/权益边界）逐条回验。
3. 官方文档自相冲突或时效性强的信息显式标记（`status: conflicting/dated`），不做人为调和。
4. 完成组/分类/域/总索引四层注册与计数对账，gates.bundles 与 gates.all 通过。

## 4. 非目标（Non-Goals）

- 不抓取、不转写用户清单之外的页面（`/open/team-integration`、`/open/api`、`/pricing`、`/features/collaboration`、`/features/custom-domain` 等仅作"延伸阅读"外链登记）。
- 不做实际部署/注册/付费等实操验证；所有"可复现"内容均为文档级复现（命令逐字引用），不声称运行验证。
- 不修改 awesome-okf-xs 子模块以外任何文件；暂存稿只放 `.temp/meoo-docs-research/`（已存在）。
- 不做 git commit（用户未要求；评审通过后由用户另行决定）。
- 不更新既有 3 个 miaowu 束的内容（仅在新束需要交叉引用时加相对链接，不回改旧束）。

## 5. 束结构方案（推荐：双束，按文档站 IA 与读者工作流切分）

文档站面包屑天然分为「功能特性」与「Meoo开放能力」两区；CLI 两页虽挂在功能特性下，但与开放集成页构成完整开发者故事线，故与开放页合为一束。

### 束 A：`miaowu-product-guide`《秒悟 Meoo 产品功能全景指南：AI 构建、平台服务与扩展生态》

源页 14 个（主页 + features 13 页，不含 cli/cli-aliyun）：

| 分区 | 源页 |
|---|---|
| 平台总览与构建意图 | `/`（主页）、`/features/agent-modes`、`/features/models` |
| 应用构建主线 | `/features/web-apps`、`/features/wechat-miniprogram`、`/features/visual-editing` |
| 平台服务 | `/features/cloud-services`、`/features/ai`、`/features/asset-center` |
| 文件与站点配置 | `/features/file-storage`、`/features/project-config` |
| 扩展生态 | `/features/skills`、`/features/skill-marketplace`、`/features/connectors` |

### 束 B：`miaowu-cli-open-guide`《秒悟 CLI 部署与开放平台集成指南：本地 Agent、自有阿里云与团队 AK/SK 接入》

源页 4 个：`/features/cli`、`/features/cli-aliyun`、`/open`、`/open/guides/cli`。含 `examples/`（文档级可复现命令流）。

> 备选方案（单大束 `miaowu-platform-guide`，18 页）在审批时可替换；双束方案在学习路径与可维护性上更优，且与站点 IA 一致。

## 6. 功能需求（FR）

- **FR-1** 每束具备完整 OKF 结构：`index.md`、`concepts/index.md` + 编号概念页、`references/{index.md,source-ledger.md,verification.md}`、`log.md`；束 B 另含 `examples/index.md` + 命令流示例页。
- **FR-2** 概念页为**教程化原创改写**（定位→何时用→操作/机制→坑点/边界→延伸），不是原文复制粘贴；命令、端点、版本、限额等引用性内容逐字保留并标注 F 编号。
- **FR-3** source-ledger 覆盖 18 个 URL（F 编号连续、与概念页双向可追溯）；主页营销性表述（"0 代码""3 分钟"类）标注为厂商自述。
- **FR-4** verification.md 含 P0 核验表：状态分 verified / conflicting / dated / unverifiable；重点含——
  - 模型口径冲突：构建器模型页（Qwen3.8 系列等 13 个）vs AI 服务页 API 传参值（`qwen3.6-plus` 等 9 个）→ **conflicting 双源并存**；
  - 开放平台权益边界（集成版未上线、团队 AK/SK 暂不支持自助创建、OAuth 不可自行注册）→ dated/条件性事实；
  - Node 版本三处口径（CLI 前置 Node 20+；开放集成运行环境 Node 18+；全栈云端构建 Node 24.15.0）→ 语境标注，不判对错。
- **FR-5** 截图承载的 UI 细节只转写页面文字层，不据截图虚构按钮路径；源页已声明的图片缺失/转换残片（如 `_4d3c6c660f48.png)`）不得进入教程正文。
- **FR-6** 索引注册四层：`miaowu/index.md`（新增 2 行束条目，3→5）、`ecosystems/index.md`（95→97，目录 16 不变）、`jishu/ai/index.md`（正文 247→249、description 同步、ecosystems 行 95→97）、`bundles/index.md`（frontmatter `total_bundles: 647`、正文 645→647）；如实施前磁盘基线已变，以磁盘实际值为准并在 log 记录。
- **FR-7** 两束 frontmatter 符合 `frontmatter.md`：`okf_version: "0.2"`（库基线；原文"0.3"系笔误，理由见 §3 注）、`type: bundle`、sources/generated(2026-10-18)/verified/status/stale_after（建议 90 天，2027-01-18，因含快速演进的模型/套餐信息）。
- **FR-8** 全部交叉引用为 MyST/Markdown 相对链接；禁止 `file:///`、禁止引用 `.temp/` 路径；两束间互链用相对路径。
- **FR-9** `log.md` 记录 R→I→E→V 过程、CMD-LOG 关键事件（G1 事实门/G2 洞察门/G3 模式门）、缺口清单（未抓取但被提及页面）与采集方法声明（WebFetch HTML→MD 转换局限）。

## 7. 非功能需求（NFR）

- **NFR-1 事实保真**：命令/端点/数字零改写；教程性表述与厂商宣传性表述可区分。
- **NFR-2 门禁**：`python gates.py bundles` 与 `python gates.py all`（cwd=`projects/awesome-okf-xs/tasks`）通过；Sphinx dummy/linkcheck 不引入新增告警。
- **NFR-3 原子性**：每束可独立阅读；概念页之间通过概念索引而非阅读顺序耦合。
- **NFR-4 语言**：正文中文；命令、代码、slug、环境变量逐字英文保留。

## 8. 约束、依赖、假设

- **约束**：目标在 git 子模块 awesome-okf-xs 内（项目路由标注"只读引用"），但用户显式指定该路径，且该组已有同来源 3 束先例（2026-10-17/18），按用户指令执行；不执行子模块 push。
- **依赖**：17 页原文已采集至 `d:\spaces\SpecWeave\.temp\meoo-docs-research\`（17 个 .md，约 115KB），全部 2026-10-18 抓取成功。
- **假设**：① WebFetch 转换文本可代表页面文字层事实（图片信息除外）；② 计数基线以 spec 创建时磁盘值为准（645/247/95/3）；③ 读者无需 Meoo 账号即可理解教程。

## 9. 验收标准（Acceptance Criteria）

### Rule 型（二元可验）

- **AC-01（rule）**：两束目录 `miaowu/miaowu-product-guide/` 与 `miaowu/miaowu-cli-open-guide/` 存在，且 FR-1 所列文件全部齐备；缺任一文件即不通过。证据：`LS`/`Glob` 文件清单。
- **AC-02（rule）**：18 个源 URL 全部出现在两束 source-ledger 中且无重复登记（每 URL 恰归一束，主页归束 A）。证据：对 ledger 做 URL 集合机械比对。
- **AC-03（rule）**：P0 清单逐字一致——抽核不少于 15 处（含：`npm install -g @aliyun-meoo/cli`、`meoo deploy --runtime image`、`POST /open/v1/team/members/{member_id}/tokens`、`scopes: ["cli.compat"]`、`MEOO_TOKEN`/`MEOO_API_URL`、两个 api.meoo.host 端点、5MB/50MB/10 个、Node 20/18/24.15.0、Free 1/Pro 4/MAX 8、`meoo aliyun {deploy,update,status,delete,rollback}`、`0.0.0.0:${PORT:-9000}`）与暂存原文逐字相符。
- **AC-04（rule）**：模型口径冲突在 verification.md 存在 `conflicting` 条目，且两处数字/传参值在 concepts 中均未被单方面"纠正"。
- **AC-05（rule）**：正文不含 `.temp/`、`file:///`、采集残片串（`_4d3c6c660f48`）、转换乱码域名（`xn--`）。
- **AC-06（rule）**：四层索引计数五面一致（总索引 frontmatter+正文、ai 分类 description+正文+导航行、ecosystems 正文、miaowu 表格行数），运行门禁机械对账通过。
- **AC-07（rule）**：`python gates.py bundles` 退出码 0；`python gates.py all` 退出码 0（在 tasks 目录执行）。
- **AC-08（rule）**：Sphinx 文档构建（按该子模块 README 的构建命令）零新增 warning/error，两束 toctree 可解析。
- **AC-09（rule）**：每束每个 .md 均含合规 frontmatter（必填字段齐全且值合法），`okf_version: "0.2"`（库基线）、`type` 与文件角色一致。
- **AC-10（rule）**：未抓取页面（team-integration/api/pricing/collaboration/custom-domain 等）只以"延伸阅读（未转写）"形式出现，不产生任何无来源事实。
- **AC-11（rule）**：独立评审以 fresh-context 子代理执行（只读），评审问题全部闭环（completed 或用户批准 cancelled）后方可结束。

### Rubric 型（评分维，阈值≥2.5/3）

- **AC-12（rubric）教程可用性（0-3）**：锚点 0=原文堆砌/无导航；1=有改写但步骤断裂；2=按学习者路径组织、含场景与坑点、可独立照做；3=在 2 基础上有决策辅助（选型表/决策树/检查清单）且概念间递进清晰。
- **AC-13（rubric）洞察与模式质量（0-3）**：锚点 0=无 I/E 内容；1=只有复述无四元组；2=含≥3 条四元组洞察与≥3 个可迁移模式（含触发条件/步骤/反模式）；3=洞察跨页综合、能解释"为什么"且反模式来自源文档明示坑点。
- **AC-14（rubric）可审计性（0-3）**：锚点 0=无台账；1=有台账但回溯断链；2=F 编号双向可追溯、P0 表完整、冲突/时效显式；3=在 2 基础上缺口与方法局限声明完整、维护者可凭台账独立复核任一结论。
