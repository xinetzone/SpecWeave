---
status: "draft"
version: "1.0"
---

# Orca ADE 博文 → OKF Wiki 教程 Spec

## Why

微信公众号文章《GitHub 6.7万 Star，一个多 Agent 协作、手机远程指挥的开源神器！》（公众号「极客之家」，2026-09-14 14:05，约 2635 字）介绍开源工具 **Orca**——Stably AI 出品的「管理 AI 编程 Agent」的桌面工具，声称 6.7 万 Star，核心能力是并行 git worktree 多 Agent 编排、内置 Chromium Design Mode、diff 行级批注、GitHub/Linear 集成、SSH 远程 worktree、手机端远程指挥、Orca CLI。

按 `blog-article-to-okf-wiki` 七阶段工作流转化为 OKF v0.2 知识包，归入 `jishu/ai/` 分组（与同公众号的 LoopX 束并列）。

## 阶段 0：内容敏感度预检

- URL：`https://mp.weixin.qq.com/s/8JIFdIzUwyLF6j1ysOrkzg?from=industrynews&color_scheme=light#rd`
- 判定信号：无 `share?code=`/`token=`/邀请码参数，非企业内部域名（`mp.weixin.qq.com` 为公众号公开文章），内容为公开产品介绍
- **结论：公开内容（Public）** → 标准工作流，spec 位于 `.trae/specs/okf-wiki-ecosystem/orca-ade-okf-wiki/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/jishu/ai/orca-ade/`

## 归属判定

**结论：`jishu/ai/orca-ade/`**（新建 bundle，落既有分组）

| 候选分组 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/` | ✅ **选定** | 该分组已容纳同公众号（极客之家）同体裁（产品介绍+核验转化）的 `loopx` 束，以及定位高度相近的 `echobird`（AI Agent 桌面管理工具，Tauri+Rust）、`codex-agent-workflow-practices`（Agent 工作流实践）、`todesk-ai`（跨设备 AI 助手） |
| 新建分组 | ❌ 否决 | 单篇博文建新分组属过度工程（反模式 #3），违反最小变更 |
| `jishu/dev/` | ❌ 否决 | 该分组为 git/github/opensource 生态，非 AI 工具；主线实体 Orca 是 AI Agent 编排工具而非 git 专题 |

- **主线实体**：Orca（AI 编程 Agent 管理工具）
- **命名**：`orca-ade`——用 `-ade` 后缀消歧。**必须消歧**：Homebrew 官方 cask `orca` 是 plotly 的图表工具（见 facts F-071），裸名 `orca` 会在检索与引用上造成混淆

## 骨架判定（操作可复现性两问）

| 问题 | 判定 | 依据 |
|---|---|---|
| Q1 博文中是否有读者可照做的安装/配置/调用/实测流程？ | **是** | 含 macOS 安装命令（F-043）、三平台获取方式（F-044~F-046）、首个 worktree 完整步骤链（F-047）、对比方案做法（F-048）、手机端配对路径（F-052~F-054） |
| Q2 这些流程是否经作者实测、具备可复现性？ | **是（含限定）** | 作者声明 macOS 侧一手实测（F-043"我自己是 Mac，装的时候就一行命令"），步骤顺序完整；**但博文未给版本号、未展示任何命令行输出**，Windows/Linux 为转述 |

**结论：设 `examples/`（2 篇）**，并施加两条限定：

1. examples 的每条命令必须经**官方文档逐字核验**（核验日 2026-09-20，对应版本 v1.4.205），不得由 UI 描述反推命令；
2. examples 顶部显式标注"命令源自官方文档核验，非博文作者实测输出；本包制作中未在真机执行"——避免把核验补齐的内容误读为博文实证。

> **判据说明**：LoopX（同公众号、同体裁）在同类判定下设 examples/，本包与之保持一致；若严扣"必须展示输入输出"的窄口径则 Q2 不成立。因此本 spec 保留该判断的完整依据与限定条件，供后续同类任务复核。

## What Changes

- 新增 OKF bundle：`jishu/ai/orca-ade/`
  - `index.md` + `log.md`
  - `concepts/`（3 篇 + index）
  - `examples/`（2 篇 + index）
  - `references/`（2 篇 + index）
- 更新 `jishu/ai/index.md`：分组束数 +1、新增导航行、toctree 追加
- 更新 `bundles/index.md`：total_bundles、`jishu` 域束数、`ai` 分组束数与正文计数同步（**以脚本读取的现值为准，禁止凭记忆写数字**）
- 不修改 `jishu/ai/` 下任何既有 bundle 内容

## ADDED Requirements

### Requirement: Bundle 根索引
`index.md` frontmatter 含 `okf_version/type/title/description/tags/generated/verified/status/stale_after/sources`；sources 同时列出博文 URL 与核验权威 URL（GitHub 仓库/API、官网、Homebrew tap、YC 页）；顶部含类型/信源/P0 核验统计块与时效提示；设「主题关联」段与「已知边界」段。

### Requirement: 概念文档（concepts/，3 篇）
- `00-orca-overview.md`：**发布事实层**——Orca 是什么（ADE 定位与其官方口径边界）、厂商 Stably AI（YC W22）、开源许可与免费口径、星标与版本、支持平台
- `01-fleet-worktree-mechanism.md`：**机制原理层**——并行 worktree 编排范式（隔离/对比/择一合并）、终端与通知、Design Mode、Diff 批注、集成与远程能力
- `02-ecosystem-and-fit.md`：**生态与适用层**——支持 Agent 清单的三处官方口径差异、成本真相（token ×N）、适用/不适用人群、与同分组束的生态位对比（echobird / loopx / codex-agent-workflow-practices）

### Requirement: 示例文档（examples/，2 篇）
- `00-install-and-first-session.md`：三平台安装（官方逐字命令/资产）、首启导入本地 Agent 凭据、创建首个 worktree 的完整链路
- `01-parallel-worktrees-and-cli.md`：多 worktree 并行与 diff 择一、Orca CLI（`orca worktree`/`snapshot`/`click`/`fill`、`orca serve`）、SSH 远程 worktree 与移动端配对

### Requirement: 信源登记簿（references/）
- `article-source.md`：F-001~F-0NN 事实清单（博文事实 + 核验补充事实双份登记），逐条标注信源距离层级
- `verification.md`：P0 核验记录（逐项 ✅/⚠️/❌ + 来源 URL）、**勘误表**（博文错误口径 → 正确口径 + 证据）、核验方法与未覆盖边界

### Requirement: 索引与计数同步
`jishu/ai/index.md` 与 `bundles/index.md` 的导航行、toctree、束数/域数计数三处一致；新增行须在 `jishu/ai/index.md` 的"域内分组导航"表与 `{toctree}` 块内同步落地。

### Requirement: 勘误落实
`verification.md` 中 ❌/⚠️ 项必须在 bundle 正文呈现**正确值**，并标注源文口径；博文域名硬错误（F-069）不得原样照搬。

## 约束

- 全部具体声明引用 F 编号，禁止 facts.md 之外的编造；无独立出处的成效数字标注"仅博文单源"
- **厂商/产品自宣类数字默认 P0 必核验**（星标数、Agent 具名数量、免费与账号口径）
- 观点与事实分层：F-055~F-057 为作者观点（P2 单源），正文必须显式标注为"作者观点"，不得作为事实引用
- 交叉引用同分组 bundle 用相对路径 `../<bundle>/index.md`；引用本 bundle 内文档用 `/concepts/xx.md` 形式
- 提交顺序：子模块 `projects/awesome-okf-xs` 内先提交 → 主仓库提交 spec → 主仓库更新子模块指针；用户未要求时不 push