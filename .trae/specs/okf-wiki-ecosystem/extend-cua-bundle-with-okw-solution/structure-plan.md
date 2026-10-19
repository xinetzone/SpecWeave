---
type: Plan
title: Cua 知识束扩展 × cua+okw 最优解 —— 结构设计（I 阶段）
description: 束归属与去重、骨架判定、14 文件清单、concepts/06-cua-okw-solution.md 大纲、F 编号/okw 文档→章节映射、互链计划与 V 阶段门禁清单
tags: [OKF, I阶段, 结构设计, Cua, okw, cua-okw-solution, 骨架判定]
generated: { by: "okf-wiki-ecosystem/extend-cua-bundle-with-okw-solution", at: "2026-10-16T00:00:00+08:00" }
status: draft
stale_after: 2026-12-31
sources:
  - id: spec
    resource: .trae/specs/okf-wiki-ecosystem/extend-cua-bundle-with-okw-solution/spec.md
    title: 本任务已批准 Spec
  - id: facts
    resource: .trae/specs/okf-wiki-ecosystem/extend-cua-bundle-with-okw-solution/facts.md
    title: R 阶段事实清单（F-066~F-154）
  - id: wechat-article-2-cua
    resource: https://mp.weixin.qq.com/s/vEGTwWZ8Mws2fwAQyvm0Yg
    title: 第二篇文章《别再让 Agent 用你的电脑了》（极限编程驿站，2026-10-08）
---

# Cua 知识束扩展 × cua+okw 最优解 —— 结构设计（I 阶段）

> **适用范围**：本文件为 I 阶段设计稿，只描述结构，不改动 `projects/awesome-okf-xs` 内任何文件。
> **路径约定**：全文使用**仓库根相对路径**（如 `docs/tech/guides/...`）与**束内相对路径**（如 `concepts/06-cua-okw-solution.md`），不使用本地 `file` 协议绝对 URI（三斜杠形式）。
> **事实层分离**：`concepts/06-cua-okw-solution.md` 为**合成设计（synthesis）**，与两篇源文事实层严格分离，将在正文顶部显式标注「**合成设计（synthesis）· 未在本机实测**」。

---

## 1. 归属与去重说明

本次**只扩展现有束，不新建束、不新建分组**。既有束 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/cua/` 已收录 `trycua/cua` 的项目身份、五大核心模块、许可分层、Stars 趋势、快速上手与场景局限（F-001~F-065），主题与该束**完全一致**；新建束会造成同一项目两束并存、事实编号分裂、父级计数漂移，并违反 OKF「同一主题单一知识包」与仓库的去重纪律。第二篇文章（F-066~F-154）带来的六组件命名（含 Cua Spaces）、权限三档、Cua Bench 榜单 v1、`cua sb`（gVisor）命令族、FSL/AGPL 许可分层、废弃包与 `cuabot` 安全警告等，全部是**既有束未覆盖的增量**，作为束的**第二主信源**并入即可（`references/second-article-facts.md`）。「cua + okw 最优解」是本仓独有的增量价值（既有束完全未涉及 okw），作为束内**新增一章概念文档**承载，同样不构成新建理由。因此束路径、束身份、既有 F-001~F-065 编号**一律不动**，父级 `ai-agent/index.md`、`ai/index.md`、`jishu/index.md`、`bundles/index.md` 的束/组/域计数**零改动**。

---

## 2. 骨架判定

**骨架**：沿用既有束的三段式 `index.md` + `concepts/` + `references/` + `log.md`，**无 `examples/` 目录**。

| 骨架目录 | 是否保留 | 本次变化 |
|---|---|---|
| `index.md`（根索引） | ✅ 保留 | 修改（导航/信源/计数/已知边界） |
| `concepts/`（核心概念） | ✅ 保留 | 追加 `06-cua-okw-solution.md` |
| `references/`（信源登记簿） | ✅ 保留 | 追加 `second-article-facts.md` |
| `examples/`（可复现示例） | ❌ 不建立 | 见下方两问判定 |
| `log.md`（生成日志） | ✅ 保留 | 修改（追加第二轮 R→I→E→V） |

**「操作可复现性两问」判定（Q2 = 否 → 无 examples）**：

- **Q1：本束是否包含"可复现操作步骤"类内容？** —— 是（第二篇含 `cua sb`/`lume`/driver 安装与沙箱命令族）。
- **Q2：这些操作是否在本机实际执行并留下实测结果？** —— **否**。第二篇命令系**转述官方 README**、本机未实测；本次新增的 `concepts/06` 为**合成设计**，同样**未在本机实测**（Cua Linux Driver 对 UKUI/xrdp 会话的支持尚无实测证据）。
- **结论**：Q2 = 否，不满足 `examples/` 的建立条件（examples 承载"已验证可复现"的实测步骤），故**不建 examples，骨架沿用现状**。与既有束在 `log.md`「已知限制」第 5 条、`index.md`「已知边界」中的既有口径一致。

---

## 3. 文件清单表（14 个文件）

| # | 文件 | 类型 | 动作 | 一句话职责 |
|---|------|------|------|-----------|
| 1 | `index.md` | 根索引 | 修改 | 目录树、分层导航、信源说明、文件计数（12→14）、已知边界（补第二信源与合成章节声明） |
| 2 | `concepts/index.md` | 概念目录索引 | 修改 | 学习路径表与 `{toctree}` 追加 `06-cua-okw-solution` |
| 3 | `concepts/00-project-overview.md` | 概念 | 不变 | 项目身份、Computer-Use 2.0 理念、三大难题 |
| 4 | `concepts/01-five-core-modules.md` | 概念 | 修改 | 五大核心模块详解；文末追加一行「延伸阅读 → 06」 |
| 5 | `concepts/02-ecosystem-and-licensing.md` | 概念 | 不变 | 许可透明度、语言构成、工程化成熟度 |
| 6 | `concepts/03-stars-and-momentum.md` | 概念 | 不变 | Stars 趋势、社区活跃度、发布节奏 |
| 7 | `concepts/04-getting-started.md` | 概念 | 不变 | 快速上手路径（安装命令、建议顺序） |
| 8 | `concepts/05-scenarios-and-limitations.md` | 概念 | 修改 | 适用场景、局限与展望；文末追加一行「延伸阅读 → 06」 |
| 9 | `concepts/06-cua-okw-solution.md` | 概念 | **新增** | cua × okw 最优解（合成设计·未实测）：分层分工/选型判据/组合路径/前置条件/风险清单 |
| 10 | `references/index.md` | 信源目录索引 | 修改 | 信源清单、事实编号索引与 `{toctree}` 追加第二信源（F-066+） |
| 11 | `references/article-source.md` | 信源事实清单 | 修改 | **仅补一行**「第二信源见 `second-article-facts.md`」，既有 F-001~F-065 事实体不改写 |
| 12 | `references/second-article-facts.md` | 信源事实清单 | **新增** | 第二篇文章事实 F-066~F-154 完整登记（含类型 O/V/S、P0 核验结论、跨信源对账四元组） |
| 13 | `references/verification.md` | 核验报告 | 修改 | 追加第二轮核验结论表 + 跨信源对账段落；`sources` 补第二篇 |
| 14 | `log.md` | 生成日志 | 修改 | 追加第二轮 R→I→E→V 记录、14 文件清单、G1–G4 结论、已知限制 |

> **计数推演**：新束内内容文档 = 7 概念（00~06）+ 3 信源（article-source / second-article-facts / verification）+ 1 日志（log）= 11；子目录索引 2（concepts/index、references/index）+ 根索引 1 = 3。合计 **14**。

---

## 4. `concepts/06-cua-okw-solution.md` 大纲（核心）

**章节定位**：本束第七篇概念文档，接在「05 适用场景、局限与展望」之后，把 Cua 的命题与本仓 okw 能力组合成一份**可迁移的组合设计**。全章标注 **「合成设计（synthesis）· 未在本机实测」**；Cua 侧陈述挂 F 编号，okw 侧陈述挂仓库根相对路径（锚点见第 5 节映射表与本节各小节标注）。

**frontmatter 规划**：`type: Concept`、`title`「cua × okw 最优解：给 Agent 一台可管理、可隔离、可复现的电脑（合成设计）」、`description`、`tags: [Cua, okw, openKylin, WSL2, Computer-Use, 隔离, 合成设计]`、`generated`/`verified`、`status: draft`、`stale_after: 2026-12-31`、`sources`（第二篇 + okw 指南/README）。

### ① 问题与定位

- **Cua 的命题**：「给 AI Agent 一台属于它自己的电脑」，让 Agent 不抢用户鼠标、不怕被弄坏（F-004 / F-136 / F-137 / F-078）。
- **缺口**：Windows 用户缺一台**可管理、可隔离、可复现**的宿主——Windows 原生桌面不适合作为「Agent 的电脑」（会抢占用户桌面）。
  - *锚点*：Cua 侧 `[F-092]`（后台操作 Windows 桌面并自测的场景描述）、`[F-128]`（只需跑命令时普通容器即可）。
- **okw 提供什么**：面向 Windows + WSL2 的 openKylin 开发工具包，提供 WSL 发行版生命周期管理、环境验收、rootless Podman、开发容器与 UKUI 桌面（xrdp）链路。
  - *锚点*：`docs/tech/guides/openkylin-wsl-devkit/index.md`、`docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md`。
- **本章目标**：给出「宿主（Windows+WSL2+okw）↔ Agent 的电脑（openKylin Desktop WSL）↔ 工作负载」的解耦分工与选型判据。

### ② 分层架构分工（三层）

```text
第 3 层  工作负载（Workload）
         ├─ Cua Sandbox（cua sb，gVisor 容器）      ← 命令任务，无需图形
         ├─ okw podman + openKylin dev container    ← 开发/测试环境
         └─ Cua Bench 评测目标                       ← 数据生成/评测/轨迹导出
                    ▲
第 2 层  「Agent 的电脑」（Agent Host）
         └─ openKylin Desktop WSL 发行版 + UKUI 桌面（xrdp → mstsc localhost:3390）
                    ▲
第 1 层  宿主管辖（Host Governance）
         └─ Windows + WSL2 + okw 生命周期/验收（okw list/status/import/export/exec、
            okw verify、okw podman verify、okw desktop launch/verify）
```

- **第 1 层（宿主管辖）**：okw 负责发行版的导入/导出/启停与只读验收，保证「Agent 的电脑」可被创建、检查、回收。
  - *锚点*：`docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md`（`okw import/export/exec`、`okw verify`）、`docs/tech/guides/openkylin-wsl-devkit/index.md`（能力概览）。
- **第 2 层（Agent 的电脑）**：openKylin Desktop WSL 发行版内预装 UKUI 桌面，经 xrdp（默认端口 **3390**）供 Windows 侧 `mstsc` 连接；`localhost` 转发稳定（内网 IP 会漂移）。
  - *锚点*：`docs/tech/guides/openkylin-wsl-devkit/08-desktop.md`（桌面链路图、`localhost:3390`、Session 选 `xorg`）。
- **第 3 层（工作负载）**：三选一或并存——Cua Sandbox（gVisor，命令任务）、okw podman + openKylin dev container（可复现开发环境）、Cua Bench（评测与训练目标）。
  - *锚点*：Cua 侧 `[F-113]`（`cua sb create ubuntu --name dev`，gVisor 容器）、`[F-014]`/`[F-035]`（Cua Bench 闭环）；okw 侧 `docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md`、`docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md`。

### ③ 模块选型判据表（行=四类场景，列=推荐组件/理由/依据）

| 场景 | 推荐组件 | 理由 | okw / Cua 侧依据 |
|---|---|---|---|
| **A 无 GUI 命令任务**（跑命令、装依赖、跑测试） | Cua Sandbox（`cua sb`，gVisor 容器）或 okw rootless Podman / openKylin dev container | 无需图形栈时优先轻量隔离容器：隔离性强于普通容器、开销小于虚拟机；作者亦判断「只需跑命令用普通容器就够」 | Cua：`[F-113]`、`[F-117]`、`[F-128]`；okw：`docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md`、`docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md` |
| **B 需 GUI 且要求隔离**（操作无 API 的桌面软件、看界面判断状态） | Cua Driver（后台投递）接入隔离桌面（Cua Fleets/Spaces 或第 2 层 UKUI 桌面） | 无 API 的界面必须"看屏幕"；后台投递不抢焦点；隔离可防污染宿主。本地 GUI 侧用 UKUI 桌面 + xrdp 承载 | Cua：`[F-078]`、`[F-088]`、`[F-129]`、`[F-011]`、`[F-048]`（付费）；okw：`docs/tech/guides/openkylin-wsl-devkit/08-desktop.md` |
| **C 可复现开发环境**（环境要能导出/复现/验收） | okw WSL 发行版生命周期（`import/export`）+ rootless Podman + openKylin dev container | 发行版可导出为 tar、再导入复现；okw 把验收脚本化（只读 preflight/verify），复现性优于手工环境 | okw：`docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md`（`okw import/export`）、`docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md`、`docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md` |
| **D 评测与训练**（造任务、评 Agent、导轨迹） | Cua Bench（任务/评测/轨迹导出）+ Cua Fleets 认领机器池 | Bench 提供「数据生成→训练→评估」闭环与可复核评测；Fleets 池毫秒级认领、空闲缩零，适合规模化评测 | Cua：`[F-014]`、`[F-035]`、`[F-111]`、`[F-115]`（沙箱截屏）、`[F-132]`/`[F-153]`（计费）；okw：`docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md`（本地复现评测目标环境） |

> **可迁移性**：判据表的列结构（场景 / 推荐组件 / 理由 / 依据）对任意「宿主 + Agent 电脑 + 工作负载」组合成立——换用其他宿主（如 macOS + Lume）或其他 Agent 电脑（如 Windows 沙箱）时，只需替换"依据"列。此为本表作为可迁移判据的设计意图（对应 TR-3.3 / CP-10）。

### ④ 组合路径（**设计**，非实测）

**GUI 路径（设计）**：

```text
okw desktop launch <name>                     # 启动发行版 → 等 localhost:3390 → 拉起 mstsc
        │  （Windows 侧 mstsc 连 localhost:3390，Session=xorg）
        ▼
openKylin Desktop WSL 内的 UKUI 桌面           # 第 2 层「Agent 的电脑」
        │  在发行版内安装 Cua Driver（Linux 版）
        ▼
Cua Driver（Linux，按 MCP 接入 Agent）          # Agent 驱动 UKUI 应用、验证屏幕结果
        ▼
Agent（Claude Code / Codex / Cursor 等）        # 复刻 6×7 计算器闭环：算 6×7 并验证屏幕显示 42
```

- *锚点*：okw 侧 `docs/tech/guides/openkylin-wsl-devkit/08-desktop.md`（`launch` 三步流程、`xorg`、`localhost:3390`）；Cua 侧 `[F-119]`（Linux Driver 安装命令）、`[F-094]`（MCP 接入 Agent）、`[F-010]`（CLI/MCP/SDK 三接入）、`[F-095]`（6×7 验证任务）。
- **headless 路径（设计）**：不依赖图形，直接在沙箱内跑命令——

```text
cua sb create ubuntu --name dev      # 起 gVisor 容器（非虚拟机）
cua sb exec dev uname -a             # 在沙箱内执行命令
cua sb screenshot dev                # 沙箱截屏（用于结果核验）
cua sb rm dev                        # 用完即弃
```

- *锚点*：Cua 侧 `[F-113]`、`[F-114]`、`[F-115]`、`[F-116]`、`[F-117]`。
- **边界声明**：以上两条路径均为**设计**，未在本机执行；不得表述为"已实测可用"。

### ⑤ 前置条件

| 前置条件 | 说明 | 锚点 |
|---|---|---|
| Windows + WSL2 | 宿主环境；okw 以此为切入点 | `docs/tech/guides/openkylin-wsl-devkit/index.md` |
| openKylin Desktop 镜像**已导入** | 须为**已预装桌面**的 Desktop WSL 发行版（如 `openKylin-3.0-desktop`）；最小镜像（无 xrdp）不适用桌面路径 | `docs/tech/guides/openkylin-wsl-devkit/08-desktop.md`（先 `wsl -l -v` 确认 `<name>`） |
| okw 已安装 | Python 3.10+，运行时零第三方依赖 | `apps/dev-tools/openkylin-wsl-devkit/README.md`（快速安装） |
| Cua CLI / Driver 可用 | Driver 安装：macOS/Linux `install.sh`、Windows `install.ps1`；CLI 安装 `install.sh \| sh` | Cua 侧 `[F-112]`、`[F-119]`、`[F-120]` |
| rootless Podman 就绪（走容器路径时） | okw 三步流程 preflight → install --yes → verify | `docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md` |
| 网络与磁盘 | 发行版内 apt/一般网络可用；导入/导出镜像需足够磁盘 | `docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md`、`docs/tech/guides/openkylin-wsl-devkit/index.md` |

### ⑥ 风险与未验证项清单

| # | 类型 | 项 | 说明 | 锚点 |
|---|---|---|---|---|
| 1 | **未验证** | Cua Linux Driver 对 UKUI/xrdp 会话的支持**未验证** | 无实测证据；需在 openKylin Desktop WSL 内实测 Driver 是否能枚举/驱动 UKUI 应用 | Cua：`[F-050]`（后台投递有平台边界）；okw：`docs/tech/guides/openkylin-wsl-devkit/08-desktop.md` |
| 2 | **未验证** | xrdp 是**远程会话**而非本地物理屏 | 截屏/输入假设可能与本地物理屏不同；Cua Driver 的"后台投递/截屏"在 xrdp 会话下行为未验证 | okw：`docs/tech/guides/openkylin-wsl-devkit/08-desktop.md`；Cua：`[F-088]`、`[F-115]` |
| 3 | **未验证** | 组合路径整体**未在本机实测** | ④ 的两条路径均为设计推断，含合成成分 | 本文件第 4 节 ④ |
| 4 | **未验证** | 发行版内**嵌套 rootless Podman** 的平台限制 | 若走"dev container 内 live rootless"路径，WSL2 嵌套 userns 映射受限（需 `--privileged`，契约禁止） | okw：`docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md`（已知边界） |
| 5 | 风险 | WSL 发行版**按需停止** | 发行版停止 → xrdp 随之停止 → `localhost:3390` 无监听；连不上多半是发行版处于 `Stopped` | okw：`docs/tech/guides/openkylin-wsl-devkit/08-desktop.md`（FAQ） |
| 6 | 风险 | okw **不安装桌面套件** | 只能作用于**已预装**桌面的 Desktop WSL 镜像；不含桌面套件的镜像不能走 GUI 路径 | okw：`docs/tech/guides/openkylin-wsl-devkit/08-desktop.md`（边界）、`docs/tech/guides/openkylin-wsl-devkit/index.md` |
| 7 | 风险 | **AGPL 组件与 `cuabot` 安全警告** | 可选 `cua-perception` 含 AGPL-3.0-only OmniParser，重新分发/网络提供可能触发源码义务；`cuabot` 官方 README 警告"有已知安全问题，不要运行" | Cua：`[F-124]`、`[F-125]`、`[F-146]`、`[F-127]`、`[F-147]` |
| 8 | 风险 | **Cua Fleets 付费**且**单价未获官方核验** | 云桌面集群为按用量计费；单价仅第二篇单源，未在可达官方页检出 | Cua：`[F-048]`、`[F-132]`、`[F-153]` |

> 计数：**8 项**，其中**明确"未验证"项 4 条**（#1–#4）、**风险项 4 条**（#5–#8）。每条均标注验证路线或缓解方式（#1 需在 UKUI/xrdp 会话内实测 Cua Linux Driver；#2 需实测 xrdp 会话下的截屏/输入；#4 以发行版侧 rootless（`okw podman verify`）替代容器内 live rootless）。

---

## 5. F 编号 / okw 文档 → 章节映射表

> **两列路径形式**：
> - **仓库根相对路径**：用于正文锚点书写（如 `docs/tech/guides/...`），与 spec 一致。
> - **束内相对写法**：`06` 文件实际链接字符串。`06` 位于 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/cua/concepts/`，到仓库根为 **9 级上溯**，前缀 `../../../../../../../../../`；**实施时须以 `check-links` 校验实际深度**（若跨 Sphinx srcdir 链接不被接受，则回退为纯文本路径引用，不作超链接）。

### 5.1 Cua 侧事实 → 章节

| 事实编号 | 简述 | 落位小节 |
|---|---|---|
| F-004 / F-136 / F-137 | 命题「给 Agent 一台电脑」「不抢鼠标、不怕弄坏」 | ① 问题与定位 |
| F-092 / F-128 | 后台操作 Windows 桌面自测场景 / 只需跑命令用普通容器 | ① 问题与定位 |
| F-010 / F-094 | CLI/MCP/SDK 三接入 / 按 MCP 接入 Agent | ② 分层、④ 组合路径 |
| F-113 / F-117 / F-114 / F-115 / F-116 | `cua sb` 命令族与 gVisor 容器语义 | ② 第 3 层、③ 场景 A、④ headless |
| F-014 / F-035 / F-111 | Cua Bench 闭环 / 首个任务无需 VM / 机器池与数据集 | ② 第 3 层、③ 场景 D |
| F-078 / F-088 / F-129 | Driver 后台投递 / 不操纵全局光标 / 真场景 | ③ 场景 B、⑥ 未验证项 |
| F-011 / F-048 | Cua Fleets 隔离云桌面 / 付费 | ③ 场景 B/D |
| F-119 / F-120 / F-112 | Driver 安装（Linux/Windows）/ CLI 安装 | ⑤ 前置条件 |
| F-124 / F-125 / F-146 / F-127 / F-147 | AGPL / `cuabot` 安全警告 / 废弃包 | ⑥ 风险项 |
| F-050 / F-132 / F-153 | 后台投递平台边界 / Fleets 单价 / 单价未核验 | ⑥ 风险与未验证项 |

### 5.2 okw 文档 → 章节

| okw 来源（仓库根相对路径） | 束内相对写法（06 内） | 落位小节 |
|---|---|---|
| `apps/dev-tools/openkylin-wsl-devkit/README.md` | `../../../../../../../../../apps/dev-tools/openkylin-wsl-devkit/README.md` | ⑤ 前置条件（安装/能力概览） |
| `docs/tech/guides/openkylin-wsl-devkit/index.md` | `../../../../../../../../../docs/tech/guides/openkylin-wsl-devkit/index.md` | ① 定位、② 第 1 层、⑤ 前置条件 |
| `docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md` | `../../../../../../../../../docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md` | ② 第 1 层、③ 场景 C、⑤ 前置条件 |
| `docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md` | `../../../../../../../../../docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md` | ③ 场景 A/C、⑤ 前置条件 |
| `docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md` | `../../../../../../../../../docs/tech/guides/openkylin-wsl-devkit/05-openkylin-dev-container.md` | ② 第 3 层、③ 场景 A/C/D、⑥ 未验证项 #4 |
| `docs/tech/guides/openkylin-wsl-devkit/08-desktop.md` | `../../../../../../../../../docs/tech/guides/openkylin-wsl-devkit/08-desktop.md` | ② 第 2 层、③ 场景 B、④ 组合路径、⑤ 前置条件、⑥ 项 #1/#2/#5/#6 |
| 知识依据 `docs/knowledge/tech/openkylin-docs-wiki/` | 同前缀 + `docs/knowledge/tech/openkylin-docs-wiki/...` | 背景佐证（只读引用，不复制正文） |

> **待核说明**：okw 侧若需引用未能在这批文档中找到依据的命令/端口/行为，一律写「**待核**」，不得编造（如 Cua Driver 在发行版内的具体安装与 MCP 注册细节，官方 README 未收录于本仓，标注为「待核 / 需实测」）。

---

## 6. 互链计划

### 6.1 概念层互链

| 源文件 | 追加内容 | 指向 |
|---|---|---|
| `concepts/01-five-core-modules.md` | 文末「参考」区新增一行：`延伸阅读 → [cua × okw 最优解](06-cua-okw-solution.md)` | `concepts/06-cua-okw-solution.md` |
| `concepts/05-scenarios-and-limitations.md` | 文末「参考」区新增一行：`延伸阅读 → [cua × okw 最优解](06-cua-okw-solution.md)` | `concepts/06-cua-okw-solution.md` |
| `concepts/06-cua-okw-solution.md` | 「参考」区回链 | `01-five-core-modules.md`、`05-scenarios-and-limitations.md`、`../index.md`、`../references/second-article-facts.md`、`../references/verification.md` |

### 6.2 信源层互链

| 源文件 | 变更 | 指向 |
|---|---|---|
| `references/article-source.md` | **仅补一行**（不改既有事实体）：`第二信源（F-066~F-154）见 [second-article-facts.md](second-article-facts.md)` | `references/second-article-facts.md` |
| `references/index.md` | 信源清单（R1/R2/R3）、事实编号索引、`{toctree}` 追加 `second-article-facts` | 新增信源 |
| `references/verification.md` | 追加「第二轮核验」与「跨信源对账」两段落；文内指向 `second-article-facts.md` | 新增信源 |
| `references/second-article-facts.md` | 反向链接第一篇 `article-source.md`（标注「同第一篇 F-xxx」交叉引用） | `references/article-source.md` |
| `concepts/06-cua-okw-solution.md` | 事实/核验锚点 | `../references/second-article-facts.md`、`../references/verification.md` |

### 6.3 索引与导航

- `concepts/index.md`：学习路径表追加第 7 行（06），`{toctree}` 追加 `06-cua-okw-solution`；路径建议图补「06 组合最优解（怎么落地）」。
- 根 `index.md`：目录树 concepts 由「6 篇」改「7 篇」、references 由「2 篇」改「3 篇」；分层导航表追加 06 行与第二信源行；信源说明表追加第二篇信源；文件计数改「合计 14」；已知边界补「第二信源为第三方推介」「06 为合成设计·未实测」两条。
- 根 `index.md` 的 `{toctree}` **不变**（仍为 `concepts/index`、`references/index`、`log`）。
- **父级计数零改动**：不修改 `ai-agent/index.md`、`ai/index.md`、`jishu/index.md`、`bundles/index.md`。

---

## 7. V 阶段门禁清单

> 在 `projects/awesome-okf-xs/` 目录运行（子模块内）。

| # | 门禁 | 命令 / 检查项 | 通过判据 |
|---|---|---|---|
| 1 | toctree 完整 | `invoke gates.toctrees` | 束内三级 toctree 无断链、无孤立文档，根 index 完整 |
| 2 | 束清单/计数 | `invoke gates.bundles` | 通过，且 `bundles/index.md` 与父级分组索引计数**与改动前一致**（本次不新增束） |
| 3 | UTF-8 | `invoke gates.utf8` | 无 BOM、UTF-8 严格解码（14 文件全通过） |
| 4 | 相对链接可达 | `check-links --path projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/cua`（或等价工具） | 无本地 `file` 协议绝对 URI；束内链接全部可达；**跨 Sphinx srcdir 的 okw 链接**逐条确认可达（不可达则回退为纯文本路径引用） |
| 5 | 文件计数一致 | 人工/脚本比对 | 根 `index.md` 声明「14」= 实际文件数 14 |
| 6 | toctree 条目一致 | 比对 `concepts/index.md`、`references/index.md` 的 toctree 条目数与实际文件数 | 概念 7 条、信源 3 条 |
| 7 | 双份 F 编号一致 | 正则集合比对 | spec `facts.md` 的 F 编号集合 == 束 `references/second-article-facts.md` 的 F 编号集合（F-066~F-154，连续无跳号） |
| 8 | 合成边界 | 文本检查 | `06` 顶部含「合成设计（synthesis）· 未在本机实测」；全文无「已实测可用/验证通过」类无证据表述 |
| 9 | 未实测/未核验项 | 清单核对 | 06 的 ⑥ 含 8 项（未验证 4 + 风险 4），每条有验证路线或缓解 |
| 10 | 父级计数零改动 | `git diff --stat` | `ai-agent/index.md`、`ai/index.md`、`jishu/index.md`、`bundles/index.md` 均**未出现在 diff** |
| 11 | 既有事实未改写 | `git diff`（article-source.md / verification.md） | 既有 F-001~F-065 事实体逐字不变（article-source.md 仅新增一行） |
| 12 | 四视角对抗审查 | 事实/结构/可用/时效四视角各出结论 | 事实（F 编号双份一致）、结构（OKF v0.2 + toctree）、可用（导航可达 + 合成边界）、时效（时点标注 + `stale_after`） |

> 门禁失败须回修后重跑，不得仅凭过程描述宣称通过（对应 spec TR-8 与 review.md CP-21~CP-25）。
