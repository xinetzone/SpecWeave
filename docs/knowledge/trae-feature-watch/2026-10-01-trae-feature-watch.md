---
title: TRAE 生态特性周报（2026-10-01）
date: 2026-10-01
source: "多源：TRAE 官方更新日志与文档（docs.trae.cn / docs.trae.ai / trae.cn）+ 本地清单盘点（%USERPROFILE%\\.trae-cn）；各条目来源 URL 见正文"
report_type: trae-feature-watch
check_window: "2026-09-21 ~ 2026-10-01"
---

# TRAE 生态特性周报（2026-10-01）

> 本周监测窗口：2026-09-21（上次比对）～ 2026-10-01。
> 本期共提取 **6 条**增量特性/事实：官方版本更新 1 条（统一更新日志页漏采补提）、文档新特性 2 条（TraeCode CLI 2.0）、TraeWork 设计库 0 条（无变化，已核验）、本地 skills·插件变化 3 条。
> 四个官方更新日志页顶部条目本周均无新增（最新仍为 2026-09-15 / 2026-08-19），增量主要来自官方文档族新页与本地环境。

## 一、官方版本更新

### 1. TRAE 移动端 App v0.0.17 ~ v0.0.18：我的文件入口、跨源引用与多方式会话分享（漏采补提）

- **来源**：[TRAE 官网统一更新日志 · 2026-08-18](https://www.trae.cn/changelog)
- **能力说明**：TRAE App v0.0.17 ~ v0.0.18 发布，变更合集包括：
  - 首页新增「我的文件」入口，可查看新对话中生成的图片、视频、HTML 产物，并可查看所有飞书文档；
  - 通过输入框「+」入口引用「当前项目文件」「我的文件」「飞书文档」，快速取用当前项目、TRAE 全部任务与飞书中的文件产物；
  - 发送任务时支持不选择文件夹直接发送；
  - 支持会话分享，方式包括链接、二维码、长图、系统分享；
  - 设置页新增「帮助与反馈」入口。
- **适用场景与实用价值**：移动端从"只看进度"升级为可跨源取文件、可直接发起任务的轻量工作台；多方式分享让手机端排查过程/产物的转发更顺手，与桌面端「我的文件」（2026-08-11）形成多端闭环。
- **备注**：条目日期（08-18）早于上次运行日（09-21），上期快照仅以 [TraeWork 更新日志](https://docs.trae.cn/work_changelog) 为移动端面事实源（该页移动端条目止于 08-07 v0.0.16），未收录此条，本期经官网统一更新日志交叉核验后补提。**源间不一致待核验**：同一条目仅见于 trae.cn 统一更新日志，docs.trae.cn/work_changelog 未收录。

### 官方更新日志页本周状态（无特性条目，不计入条数）

- **来源**：[企业版更新日志](https://docs.trae.cn/enterprise_release-notes) / [TraeCode 国内更新日志](https://docs.trae.cn/ide_changelog) / [TraeCode 国际版更新日志](https://docs.trae.ai/ide/changelog) / [TraeWork 更新日志](https://docs.trae.cn/work_changelog)
- 企业版顶部仍为 **2026-09-15**（新增内置模型 DeepSeek-V4.1-Flash）；TraeCode 国内页顶部仍为 **2026-09-15 v3.3.101（Hotfix）**；TraeWork 顶部仍为 **2026-08-21 桌面版 v0.1.49 ~ v0.1.52**。
- 国际版更新日志顶部仍停留在 **2026-08-19（v3.5.89 ~ v3.5.91 Hotfix）**，连续两期无新增，国内页版本节奏（v3.3.101）继续领先，维持两站并查。

## 二、文档新特性

### 1. TraeCode CLI 2.0 正式上线：运行在本地终端里的编码 Agent

- **来源**：[TraeCode CLI 2.0 概述](https://docs.trae.cn/cli_about-trae-code-cli-2)（另见 [什么是 TraeCode CLI](https://docs.trae.cn/cli_what-is-trae-cli)、[TraeCode CLI 快速开始](https://docs.trae.cn/cli_get-started-with-trae-cli)）
- **能力说明**：官方文档全站挂出「TraeCode CLI 2.0 已上线」提示。CLI 2.0 是运行在本地终端的编码 Agent，可在项目目录中直接用自然语言描述任务，由其理解代码仓库、读取和修改工作区文件、执行命令、生成和评审代码。终端交互（TUI）支持输入任务、以 `@` 提及项目文件、粘贴图片、执行 Shell 命令，并通过 Slash 命令管理模型、权限与上下文。能力覆盖：代码理解与修改（新增功能/修 Bug/重构）、执行 Lint 与单元测试并结合失败结果修复、评审当前 Git 改动/指定分支/提交。
- **适用场景与实用价值**：偏好终端工作流的开发者可在不打开 IDE 的情况下完成"理解需求 → 改代码 → 跑测试 → 评审变更"的完整闭环；`@` 文件提及与工作区/Git 状态直读减少了来回复制上下文的成本。
- **使用限制**：官方明确仅 **TRAE 企业版旗舰版套餐**客户可用；CLI 默认使用 Max 模式，需关注用量。
- **核验状态**：能力描述均照录官方文档；官方未在页面标注 2.0 的具体上线日期，**上线时间待核验**。

### 2. TraeCode CLI 2.0 自动化与多端集成：traecli exec、ACP 接入与权限安全体系

- **来源**：[TraeCode CLI 2.0 概述](https://docs.trae.cn/cli_about-trae-code-cli-2) / [TraeCode CLI 快速开始（升级方式）](https://docs.trae.cn/cli_get-started-with-trae-cli)
- **能力说明**：CLI 2.0 在交互式 TUI 之外提供面向自动化与集成的能力组：
  - **非交互式执行**：`traecli exec` 可将任务接入脚本与 CI 流程，把代码检查、修复、评审等重复性工作固化为标准流程；
  - **ACP 多端集成**：支持 Agent Client Protocol，可作为智能体服务端接入任何支持 ACP 的编辑器或客户端，在不同研发工具中获得一致的 AI 编码能力；
  - **扩展体系**：与桌面端同一套**插件、技能（Skill）、MCP** 扩展模型，支持用户级配置、项目级信任与环境变量沉淀团队工具链；
  - **权限与安全**：通过目录信任、沙箱模式与审批策略控制文件访问、命令执行和高风险操作；
  - **自诊断**：内置 `/status`、`/doctor`、状态栏与日志信息，集中排查登录、网络、权限、模型与命令执行问题；
  - **升级**：支持启动时自动升级，或 `traecli update` 手动升级。
- **适用场景与实用价值**：对本项目这类以脚本化门禁、CI 检查和原子化提交为常态的工作流，CLI 2.0 提供了把 TRAE 能力编进无人值守流水线的官方通道；ACP 则使其不绑定单一编辑器。与上期监测到的 IDE 端 Agent 合并（`/goal`、`/plan`、`/spec`）同属一条"统一入口 + 多客户端"的产品主线。
- **核验状态**：能力照录官方文档；上线日期**待核验**（同上条）。

## 三、TraeWork 设计库

本期无增量。经全页复核 [TraeWork 设计系统文档](https://docs.trae.cn/solo_design-system)：内置设计系统仍为上期核验的 **16 套**（TraeWork、TraeCode、Volcengine、TikTok、Doubao、Apple、Claude、Google、Vercel、Minimalist、21th、Motion Fit、Golden Time、Nerv、Barbie、Vibe Camp）；自定义系统的三种添加方式（解析 Figma / 导入 TraeDesign zip / 风格探索）与主题、组件、图形、设计规范四页签全生命周期编辑能力均与上期快照一致。TraeWork 更新日志顶部仍为 2026-08-21，无 Design 模式相关新条目。

## 四、本地 skills·插件变化

### 1. 新增官方插件「录制技能」record-and-replay 0.0.4

- **来源**：本地清单（`%USERPROFILE%\.trae-cn\plugins\trae-remote-official\record-and-replay\0.0.4`）
- **能力说明**：TraeWork 官方新增 **record-and-replay（录制技能）** 插件 0.0.4，可录制用户在桌面端的操作流程，并将其生成可复用的个人技能，官方定位适用于报销、报表处理、工单创建等重复性工作。插件同步向会话贡献技能 `trae-remote-official:record-and-replay:record-and-replay`；本地 MCP 缓存中随之出现 **mcp_Record___Replay** 服务（event_stream_start / event_stream_status / event_stream_stop 三个事件流工具，供录制过程的事件采集）。
- **适用场景与实用价值**：把高频、固定步骤的跨应用桌面操作沉淀为一次录制、反复调用的个人技能，是 Computer Use 从"临场操作"走向"流程资产化"的配套能力；与工作区内既有的原子化/模式沉淀方法论互补——一个沉淀 AI 协作规程，一个沉淀人工桌面操作。
- **盘点旁证**：本机插件总数由 12 增至 **13**；该 MCP 服务当前仅在部分智能体运行时缓存中可见，本会话（solo_agent_lite）的活跃 MCP 声明未包含它，属"已安装、按需挂载"状态。

### 2. Lark 插件 1.0.5 原地增量：新增 lark-meeting 技能（lark 技能 26 → 27）

- **来源**：本地清单（`%USERPROFILE%\.trae-cn\plugins\trae-remote-official\lark\1.0.5\skills\lark-meeting\SKILL.md`；当前会话 skills 列表）
- **能力说明**：lark 插件版本号维持 **1.0.5**（目录内文件有原地更新），技能目录由 26 个增至 **27 个**，新增 **lark-meeting**：面向飞书视频会议，查询会议记录与会议产物（纪要、逐字稿、妙记）、检索妙记、上传/下载/编辑会议录制片段；并与 lark-vc 明确分流——仅当显式指定 lark-vc 时相关请求才走 vc 技能，其余统一交 lark-meeting。同期 lark-drive 参考文档新增 `lark-drive-workflow-permission-governance-outputs.md`（云空间权限治理命令的产出物说明，上期仅有同系列 `-commands.md`）。
- **适用场景与实用价值**：会议后取纪要、追录制、核对发言归属等高频动作获得独立技能入口；上期报告中"lark 1.0.5 相对 1.0.4 的具体变更内容待核验"本期部分销项——技能面增量即 lark-meeting 与文档补充，插件侧是否随安装包热更新分发**待核验**。

### 3. 会话用户级 skills 批量新增 9 个

- **来源**：本地清单（当前会话可用 skills 列表，对照 2026-09-21 快照）
- **能力说明**：用户级 skills 新增 **9 个**，无移除；连同插件贡献的 lark-meeting、record-and-replay，会话 skills 总数由 **189 增至 200**。新增清单：

| 技能 | 能力摘要 |
|---|---|
| `classical-festival-video` | 以古典文本为依据生成节日问候视频（3 张 AI 关键帧 → 10 秒竖版片段 + 校准文案） |
| `client-overlay-scaffold` | 在 apps/containers/client 下脚手架化新建 podman-compose 工作负载叠加栈（声明式 StackSpec + 12 件套 + 门禁验证链） |
| `collect-api-decouple-cmd` | 硬件/设备采集与本地解析后处理解耦，支持跳过昂贵采集、复用日志重放 |
| `compose-overlay-ops` | client 三栈（quant/native/monetize）podman-compose 叠加栈的启动/重建/冒烟运维 SOP |
| `douyin-interactive-content-publish` | 抖音互动空间一键发布（zip + 图标创建/更新应用，自动生成名称描述并提审上线） |
| `inflight-deliverable-commit-verify` | 对并行会话遗留在工作区的在途知识包/模式/技能做提交前完整性核验并原子提交 |
| `scanned-book-to-okf-wiki` | 扫描版/混合型版权书籍转 OKF Wiki 的六工序工作流（文本层可信度判定、版权合规决策门） |
| `spec-task-ifavc-delivery` | 按 I→F→A→V→C 闭环推进 .trae/specs 编号 Task（事实→作用域→测试同批落地→对抗评审→中文原子提交） |
| `wording-revision-sync` | 知识包已落盘结论的用户驱动措辞修正与全量表述点机械同步、旧口径复扫 |

- **适用场景与实用价值**：本批新增呈现两条主线——其一为 SpecWeave 自身治理/容器运维能力加密（4 个 `*-cmd`/scaffold 技能 + spec-task 闭环），其二为内容生产链路扩展（节日视频、抖音互动发布、扫描书转化、知识包措辞同步）；与用户既有"七概念闭环、原子提交、容器叠加栈"工作流直接咬合。
- **盘点旁证**：browser-bridge 0.2.0 独立插件与其余官方插件版本均无变化；connectors 仍为 dingtalk、gitee、github、lark 四个；本会话活跃 MCP 服务无变化（integrated_code_mode、mcp_plugin_Gitee_gitee，后者 23 个工具）。

---

## 采集与核验记录

- **成功源**：企业版更新日志、TraeCode 国内更新日志（ide_changelog）、国际版更新日志、TraeWork 更新日志、TraeWork 设计系统文档、官网统一更新日志（trae.cn/changelog）、TraeCode CLI 2.0 文档族（cli_about-trae-code-cli-2 / cli_what-is-trae-cli / cli_get-started-with-trae-cli）、本地 plugins 目录与 skills 清单盘点。
- **上期待核验项销项：TraeCode CLI 独立更新日志页**——本期 WebSearch 恢复正常，检索结论为**不存在独立 changelog 页**：CLI 信息分布在 `cli_*` 文档族（概念页、快速开始、CLI 2.0 指南），上期猜测的 `docs.trae.cn/cli_changelog` 确无此页；CLI 版本级变更目前仅能从企业版更新日志中覆盖 TraeCode CLI 的条目与 CLI 文档挂出的版本提示获取。该项从采集失败清单移除。
- **源间不一致（待核验）**：TRAE App v0.0.17 ~ v0.0.18（2026-08-18）仅见于 trae.cn 统一更新日志，docs.trae.cn/work_changelog 的移动端条目止于 08-07 v0.0.16。
- **持续待核验**：TraeCode CLI 2.0 具体上线日期；自定义设计系统全生命周期编辑能力上线日期；lark 1.0.5 原地更新的分发方式。
