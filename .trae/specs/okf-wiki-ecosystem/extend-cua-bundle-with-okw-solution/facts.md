---
type: Reference
title: 第二篇信源事实与核验（Cua 知识束 R 阶段增补）
description: 微信公众号「极限编程驿站」博文《别再让 Agent 用你的电脑了「Cua：2.8 万 Star 的开源项目」》事实登记 F-066~F-139，附官方源核验补充 F-140~F-154、P0 核验结论、跨信源四元组对账与统计；补录第二篇文章事实，不改动既有的 F-001~F-065 与 bundles 内文件
tags: [事实清单, 信源, 微信公众号, 极限编程驿站, Cua, Computer-Use, trycua, 核验, 增补]
generated: { by: "okf-wiki-ecosystem/extend-cua-bundle-with-okw-solution", at: "2026-10-16T19:39:52+08:00" }
status: draft
stale_after: 2026-12-31
sources:
  - id: wechat-article-2-cua
    resource: https://mp.weixin.qq.com/s/vEGTwWZ8Mws2fwAQyvm0Yg
    title: 《别再让 Agent 用你的电脑了「Cua：2.8 万 Star 的开源项目」》（极限编程驿站，2026-10-08）
  - id: github-api-cua
    resource: https://api.github.com/repos/trycua/cua
    title: GitHub API：trycua/cua 仓库元数据（2026-10-16）
  - id: cua-readme-main
    resource: https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md
    title: 官方 README（trycua/cua main 分支，经 jsDelivr 镜像）
  - id: cuabench-leaderboard
    resource: https://cua.ai/cuabench/leaderboard
    title: Cua-Bench EDA Leaderboard（v1）
  - id: cua-home
    resource: https://cua.ai/
    title: Cua 官网首页（Cua Spaces 许可与定价）
  - id: cua-docs
    resource: https://cua.ai/docs
    title: Cua 官方文档中心
  - id: cua-docs-deprecated
    resource: https://cua.ai/docs/cua-sdk/guides/migrate-from-deprecated-packages
    title: 官方文档：从废弃包迁移
  - id: cua-docs-lifecycle
    resource: https://cua.ai/docs/concepts/sandbox-lifecycle
    title: 官方文档：Sandbox lifecycle（Fleet 池容量与费用）
---

# 第二篇信源事实与核验（Cua 知识束 R 阶段增补）

> 主信源（第二篇）：微信公众号「极限编程驿站」，2026-10-08 21:20:53 发布。
> URL：https://mp.weixin.qq.com/s/vEGTwWZ8Mws2fwAQyvm0Yg
> 标题：《别再让 Agent 用你的电脑了「Cua：2.8 万 Star 的开源项目」》
>
> 编号规划：**F-066~F-139** 为第二篇文章事实/观点/厂商自述；**F-140~F-154** 为 2026-10-16 权威源核验过程中补充的事实与未核验项。
> 与既有事实的关系：本文**不改写、不重复** `references/article-source.md` 中的 F-001~F-065；两篇文章同源命令与同项声明的交叉引用在事实文本中以「同第一篇 F-xxx」显式标注，不新增冲突编号。
> 类型：`O`=客观事实 / `V`=作者观点 / `S`=厂商自述（含榜单数值）。
> 事实表不含因果推断词，仅作客观登记。

## 一、第二篇文章元信息（F-066 ~ F-069）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-066 | 第二篇文章标题：《别再让 Agent 用你的电脑了「Cua：2.8 万 Star 的开源项目」》 | O | 第二篇 URL |
| F-067 | 第二篇文章所属公众号：「极限编程驿站」 | O | 第二篇页面 HTML |
| F-068 | 第二篇文章发布时间 2026-10-08 21:20:53（+08:00）；正文自述「本文写于 2026 年 10 月」 | O | 第二篇页面 HTML |
| F-069 | 第二篇文章标签含「跨四类系统」，正文列举 macOS、Windows、Linux、Android 四类 | O | 第二篇 URL |

## 二、项目身份与动量（F-070 ~ F-076）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-070 | 第二篇文章给出项目仓库地址 github.com/trycua/cua（同第一篇 F-003） | O | 第二篇 URL |
| F-071 | 截至本文编写时 Star 超过 2.8 万 | O | 第二篇 URL |
| F-072 | Fork 超过 2,000 | O | 第二篇 URL |
| F-073 | 以 Rust 为主实现，约占仓库代码量 47% | O | 第二篇 URL |
| F-074 | 项目采用 MIT 协议 | O | 第二篇 URL |
| F-075 | 项目 2025 年 1 月建仓 | O | 第二篇 URL |
| F-076 | 项目有 130+ 位贡献者 | O | 第二篇 URL |

## 三、六组件构成（F-077 ~ F-086）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-077 | 第二篇文章口径：Cua 由六个组件组成——Cua Driver、Cua Spaces、Lume、Cua SDK 与 CLI、CUA-S1、Cua Bench | O | 第二篇 URL |
| F-078 | Cua Driver：桌面操作组件，覆盖 macOS/Windows/Linux，后台投递点击和输入，不移动系统光标、不抢焦点 | O | 第二篇 URL |
| F-079 | Cua Spaces：macOS 桌面 App，要求 macOS 26 或更高版本，个人使用免费 | O | 第二篇 URL |
| F-080 | Lume：基于 Apple Virtualization.Framework 管理虚拟机，Apple Silicon 上运行完整 macOS 桌面；支持 Sequoia 与 Tahoe | O | 第二篇 URL |
| F-081 | Cua SDK 与 CLI：一个 `cua` 命令管理本地容器与虚拟机，提供 Python/TypeScript/Swift/Kotlin 四种语言接口 | O | 第二篇 URL |
| F-082 | CUA-S1：专用小模型，官方称 System 1，只做范围很小的快速判断、不负责整体规划；模型文件托管 Hugging Face；源码 MIT | S | 第二篇 URL |
| F-083 | Cua Bench：造任务、跑评测、导出操作记录；任务覆盖桌面与移动端 | O | 第二篇 URL |
| F-084 | 官方把方向命名为 Computer-Use 2.0：同一任务中 Agent 在代码、API 与图形界面之间自由切换 | S | 第二篇 URL |
| F-085 | Lume 同一仓库提供 lumier，把 Lume 包成 Docker 兼容接口 | O | 第二篇 URL |
| F-086 | Cua Spaces 提供 Teleport（把已登录应用搬进隔离环境）与 Keyvault（登录态保险箱） | S | 第二篇 URL |

## 四、Cua Driver 机制与权限三档（F-087 ~ F-096）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-087 | Cua Driver README 首句为 "drives native macOS apps without stealing focus" | S | 第二篇 URL |
| F-088 | Cua Driver 机制为「后台投递」：把点击和输入送到指定桌面窗口，而非操纵全局光标 | O | 第二篇 URL |
| F-089 | 权限档 standard：默认，不弹窗，适合常规自动化 | O | 第二篇 URL |
| F-090 | 权限档 bounded：只放行预先审查过的清单里的工具和资源 | O | 第二篇 URL |
| F-091 | 权限档 unrestricted：必须显式加 `--dangerously-bypass-approvals` | O | 第二篇 URL |
| F-092 | 验收场景：Agent 在后台操作 Windows 桌面应用并自测，用户照常做自己的事 | O | 第二篇 URL |
| F-093 | 两个 Cua Driver 会话在 Omarchy 桌面上操作 LibreOffice Calc 和 Inkscape，终端保持前台 | O | 第二篇 URL |
| F-094 | Cua Driver 可按 MCP 标准接入 Claude Code、Codex、Cursor 等 Agent，也可当普通命令行使用 | O | 第二篇 URL |
| F-095 | 文章给出第一个练习：让 Agent 在计算器里算出 6 × 7 并自行验证屏幕显示 42（同第一篇 F-029） | O | 第二篇 URL |
| F-096 | Lume 预设自动建好用户并开启 SSH、关闭睡眠与锁屏；默认账号密码都是 lume | O | 第二篇 URL |

## 五、Cua Bench 榜单 v1（F-097 ~ F-111）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-097 | 榜单标注 v1 | O | 第二篇 URL |
| F-098 | 任务为 25 个专家级 KiCad 任务；KiCad 是开源电路设计软件，任务要求 Agent 画原理图 | O | 第二篇 URL |
| F-099 | 每个任务给 Agent 200 次操作机会 | O | 第二篇 URL |
| F-100 | 判分方式：把 Agent 画出的电路连接关系与标准答案逐项比对（网表 netlist 比对） | O | 第二篇 URL |
| F-101 | 名次 1：Claude Fable 5（Anthropic）完整通过 6/25 | S | 第二篇 URL |
| F-102 | 名次 2：GPT-5.5（OpenAI）完整通过 6/25 | S | 第二篇 URL |
| F-103 | 名次 3：Gemini 3.5 Flash（Google）完整通过 5/25 | S | 第二篇 URL |
| F-104 | 名次 4：Claude Sonnet 4.5 完整通过 5/25 | S | 第二篇 URL |
| F-105 | 名次 5：Claude Haiku 4.5 完整通过 5/25 | S | 第二篇 URL |
| F-106 | 名次 10：Gemini 3 Flash 完整通过 1/25 | S | 第二篇 URL |
| F-107 | 榜单中带 `*` 的模型通过调用程序接口（function-calling）完成任务，而非像人一样看屏幕点按钮；Claude Fable 5 与 Gemini 3 Flash 属此列 | S | 第二篇 URL |
| F-108 | Claude 系列经 Amazon Bedrock 运行 | S | 第二篇 URL |
| F-109 | 官方榜单结论：「每一个完全通过的任务，都是对已有原理图的修改」「没有任何模型能可靠地从空白画布上建起一张图」 | S | 第二篇 URL |
| F-110 | 榜单口径：最好的前沿 Agent 只通过 6 个任务 | O | 第二篇 URL |
| F-111 | 官方提供预先开机待命的机器池（认领一台为毫秒级，空闲时缩到零）与人工复核过的标准操作记录数据集 | S | 第二篇 URL |

## 六、命令族（F-112 ~ F-120）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-112 | 安装命令：`curl -fsSL https://cua.ai/install.sh \| sh` | O | 第二篇 URL |
| F-113 | 创建沙箱：`cua sb create ubuntu --name dev`；起的是 gVisor 容器，不是虚拟机 | O | 第二篇 URL |
| F-114 | 在沙箱执行命令：`cua sb exec dev uname -a` | O | 第二篇 URL |
| F-115 | 沙箱截屏：`cua sb screenshot dev` | O | 第二篇 URL |
| F-116 | 删除沙箱：`cua sb rm dev` | O | 第二篇 URL |
| F-117 | gVisor 隔离性比普通容器强、开销比虚拟机小；需要图形界面的任务才会上虚拟化 | O | 第二篇 URL |
| F-118 | Lume 创建与启动 macOS VM：`lume create macos-tahoe --ipsw ~/Downloads/macos-tahoe.ipsw --unattended tahoe`；`lume run macos-tahoe` | O | 第二篇 URL |
| F-119 | Driver 安装（macOS/Linux）：`/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"`（同第一篇 F-027） | O | 第二篇 URL |
| F-120 | Driver 安装（Windows PowerShell）：`irm https://cua.ai/driver/install.ps1 \| iex`（同第一篇 F-028） | O | 第二篇 URL |

## 七、许可分层（F-121 ~ F-125）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-121 | MIT 档：SDK、CLI、Cua Driver、Lume、Cua Bench；MIT 部分不依赖 FSL 部分 | S | 第二篇 URL |
| F-122 | FSL-1.1-MIT 档：Spaces 应用、cua-spacesd（沙箱内常驻服务）、Keyvault、Teleport、音视频流 | S | 第二篇 URL |
| F-123 | FSL-1.1-MIT 条款：可免费自用和自建，不可做竞争性托管服务；每次发布两年后自动转为 MIT | S | 第二篇 URL |
| F-124 | cua-perception 扩展内含 OmniParser 图标识别模型（微软开源），为 AGPL-3.0-only | S | 第二篇 URL |
| F-125 | 官方 README 警告框：重新分发、或通过网络提供给用户，可能要求把相关源代码一并公开；不接受 AGPL 组件的组织不要安装 | S | 第二篇 URL |

## 八、废弃包与安全警告（F-126 ~ F-127）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-126 | 一批老包被标记为废弃：cua-computer、cua-computer-server、cua-agent、cua-som | O | 第二篇 URL |
| F-127 | npm 上的 cuabot 的 README 措辞为 "Do not run it: it has known security issues." | O | 第二篇 URL |

## 九、「何时不需要它」判断（F-128 ~ F-130）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-128 | 作者判断：只需跑命令、装依赖、跑测试 → 用普通容器就够 | V | 第二篇 URL |
| F-129 | 作者判断：需要操作没有 API 的桌面软件、看界面判断状态 → Cua 真正要解决的场景 | V | 第二篇 URL |
| F-130 | 作者判断：只需要三五个网站的自动化 → 写一个命令行工具直接调接口可能更划算 | V | 第二篇 URL |

## 十、采用者与成本（F-131 ~ F-133）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-131 | Cua Driver 作为底层能力出现在 Hermes、Clicky、H Company、Factory Droid 等第三方 AI 产品里 | S | 第二篇 URL |
| F-132 | Cua Fleets 按用量计费：CPU $0.044625/vCPU/小时、内存 $0.0223125/GiB/小时（截至本文编写时的官方定价） | S | 第二篇 URL |
| F-133 | 成本口径：本地这套框架开源免费，Cua Spaces 对个人免费；规模化时才用托管服务 Cua Fleets，也支持跑在自有云账号或私有环境里 | S | 第二篇 URL |

## 十一、结语观点与文章元信息（F-134 ~ F-139）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-134 | 作者观点：过去两年让 Agent 学会干活的办法，基本上是给它修一条更窄的路（把网站变成 CLI、把操作变成 API） | V | 第二篇 URL |
| F-135 | 作者观点：现实世界就是这样，一堆没有 API 的界面，一堆必须用手点的软件 | V | 第二篇 URL |
| F-136 | 作者观点：「与其把世界翻译给 Agent，不如直接给 Agent 一台电脑」 | V | 第二篇 URL |
| F-137 | 作者观点：「Agent 不缺大脑，缺一台不抢你鼠标、不怕被弄坏的电脑」 | V | 第二篇 URL |
| F-138 | 文章给出项目地址 github.com/trycua/cua、官网与文档 cua.ai、Cua Bench 榜单 cuabench.ai/leaderboard | O | 第二篇 URL |
| F-139 | 文章标注许可证：MIT（核心）· FSL-1.1-MIT（Spaces 系） | O | 第二篇 URL |

## 十二、官方源核验补充事实（F-140 ~ F-154，2026-10-16）

| 编号 | 事实 | 类型 | 来源 |
|------|------|------|------|
| F-140 | GitHub API 时点快照（2026-10-16）：stars 29,926、forks 2,142、open_issues 1,217、subscribers 99 | O | GitHub API |
| F-141 | GitHub API：language=Rust、created_at 2025-01-31T15:02:49Z、homepage=https://cua.ai、license.spdx_id=MIT、pushed_at 2026-10-16T11:32:20Z、id 925270205 | O | GitHub API |
| F-142 | GitHub languages API（2026-10-16）：Rust 字节 35,698,298 占 42.31%；TypeScript 18.09%、Python 17.16%、Swift 10.04%、Go 3.23%、Kotlin 2.60% | O | GitHub API /languages |
| F-143 | GitHub contributors 分页计数：含匿名末页 155、排除匿名末页 149，与「130+ 位贡献者」口径相容 | O | GitHub API /contributors |
| F-144 | 官方 README 许可分层逐字确认：MIT 覆盖 cua SDK 及 Python/TypeScript/Swift/Kotlin 包、`cua` 命令与 `cua daemon`、Cua Driver、Lume 及仓库其余部分；FSL-1.1-MIT 覆盖 Spaces apps、cua-spacesd、Cua Keyvault、teleport、Cua Volume（`cua-volume`）、streaming client/codecs/viewers | O | 官方 README |
| F-145 | 官方 README：Cua Driver Bench（`benchmarks/cua-driver-bench`）同为 FSL-1.1-MIT；2026-10-11 前发布版本为 MIT（第二篇未提及该项） | O | 官方 README |
| F-146 | 官方 README：`cua-som` 为 AGPL-3.0-or-later 可选包；可选 `cua-perception` 扩展由 AGPL-3.0-only OmniParser 模型 + Apache-2.0 PP-OCR 模型 + 单独打包的 ONNX Runtime 组成，并非 MIT，重新分发或通过网络提供可能触发 AGPL-3.0 源码义务 | O | 官方 README |
| F-147 | 官方 README 与官方迁移文档确认废弃清单含 cuabot（npm）、cua-computer、cua-computer-server、cua-agent、cua-som；cuabot 措辞 "Do not run it: it has known security issues." 逐字一致 | O | 官方 README / 官方迁移文档 |
| F-148 | 官方 README 确认 SDK 四语言：Python（`pip install cua`）、TypeScript（`@trycua/cua`）、Swift（`Cua`）、Kotlin（generated bindings）；`cua sb create ubuntu --name dev` 注释逐字为 "a gVisor container, set up on first use" | O | 官方 README |
| F-149 | Cua-Bench EDA 榜单页逐字确认：25 个 expert-authored KiCad schematic tasks、200-step budget、verifiable netlist grading；名次与 6/25、6/25、5/25、5/25、5/25、1/25 与第二篇一致 | O | 榜单页 |
| F-150 | 榜单页确认：`*` = "Run via function-calling; native Computer Use is not enabled for these preview models"；Claude 模型经 Amazon Bedrock 运行；结论 "Every full pass was an edit to an existing schematic. No model reliably built one from a blank canvas." | O | 榜单页 |
| F-151 | 官网 cua.ai 首页确认：Cua Spaces 为 source-available under FSL-1.1-MIT，each release becomes MIT two years after it ships；Cua Driver 与 Lume 为 MIT；Space 需 macOS 26 或更高；无需账号即可开始；对个人免费 | O | cua.ai 首页 |
| F-152 | cua.ai/docs 可达（HTTP 200）：文档导航含 Cua Driver、Cua Sandbox、Cua-Bench、Architecture（driver/sandbox/computer/agent/MCP 分层）与 Sandbox SDK reference（Python 与 TypeScript 接口） | O | cua.ai/docs |
| F-153 | **未能核验**：Cua Fleets 单价（CPU $0.044625/vCPU/小时、内存 $0.0223125/GiB/小时）未在任何可达官方页检出，仅第二篇单源；官方文档确认 Fleet 池退出 claim 后可能保留 warm capacity 并产生云用量费用 | O | 官方 Sandbox lifecycle 文档（间接） |
| F-154 | **未能核验**：第二篇文章正文无法经 WebFetch 提取（失败）；经 PowerShell 抓取 HTML 确认页面可达（HTTP 200，长度 3,567,631 字节）且标题字符串存在 | O | 第二篇 URL |

## 十三、P0 声明核验结论

> 核验日期：2026-10-16。结论口径：`✅ 通过`=与权威源一致 / `⚠️ 时点或口径差异`（含「未获官方页核验，仅第二篇单源」）/ `❌ 失败`。

| # | 第二篇 P0 声明 | 结论 | 对应事实 | 权威来源 |
|---|----------------|------|---------|---------|
| 1 | 仓库 github.com/trycua/cua、MIT、2025 年 1 月建仓 | ✅ 通过 | F-070/F-074/F-075 → F-141 | GitHub API |
| 2 | Star 超 2.8 万 | ⚠️ 时点/口径差异（约数偏低：2026-10-16 实测 29,926） | F-071 → F-140 | GitHub API |
| 3 | Fork 超 2,000 | ✅ 通过（2,142） | F-072 → F-140 | GitHub API |
| 4 | Rust 约占仓库代码量 47% | ⚠️ 口径差异（languages API 实测 42.31%） | F-073 → F-142 | GitHub API /languages |
| 5 | 130+ 位贡献者 | ✅ 通过（149/155） | F-076 → F-143 | GitHub API /contributors |
| 6 | 六组件（Driver/Spaces/Lume/SDK-CLI/CUA-S1/Bench） | ✅ 通过 | F-077~F-086 → F-144/F-148/F-152 | 官方 README / 文档 |
| 7 | Cua Spaces：macOS 26+、个人免费 | ✅ 通过 | F-079 → F-151 | cua.ai 首页 |
| 8 | SDK 提供 Python/TypeScript/Swift/Kotlin 四语言 | ✅ 通过 | F-081 → F-148 | 官方 README |
| 9 | CUA-S1 System 1、源码 MIT、权重在 Hugging Face | ✅ 通过 | F-082 → 官方 README | 官方 README |
| 10 | 权限三档 standard/bounded/unrestricted 与 `--dangerously-bypass-approvals` | ⚠️ 未获官方页核验（仅第二篇单源） | F-089~F-091 | — |
| 11 | 安装/沙箱/Lume/Driver 命令族 | ✅ 通过 | F-112~F-120 → F-148 | 官方 README |
| 12 | `cua sb create ubuntu` 起 gVisor 容器而非虚拟机 | ✅ 通过 | F-113 → F-148 | 官方 README |
| 13 | 榜单 v1：25 个 KiCad 任务、200 次操作、netlist 比对 | ✅ 通过 | F-097~F-100 → F-149 | 榜单页 |
| 14 | 名次与通过数 6/6/5/5/5/1（前五名与第 10 名） | ✅ 通过 | F-101~F-106 → F-149 | 榜单页 |
| 15 | `*`=function-calling；Claude 经 Bedrock；「每个完全通过的任务都是对已有原理图的修改」 | ✅ 通过 | F-107~F-109 → F-150 | 榜单页 |
| 16 | 许可分层 MIT / FSL-1.1-MIT / cua-perception AGPL-3.0-only | ⚠️ 口径差异（FSL 范围文中「音视频流」对应官方 streaming client/codecs/viewers，官方 wire protocol 仍 MIT；文中漏 Cua Driver Bench 亦为 FSL） | F-121~F-125 → F-144/F-145/F-146 | 官方 README / cua.ai |
| 17 | 废弃包与 cuabot 安全警告措辞 | ✅ 通过 | F-126/F-127 → F-147 | 官方 README / 迁移文档 |
| 18 | Cua Fleets 单价 CPU $0.044625/vCPU/小时、内存 $0.0223125/GiB/小时 | ⚠️ 未获官方页核验（仅第二篇单源） | F-132 → F-153 | — |
| 19 | 采用者 Hermes、Clicky、H Company、Factory Droid | ⚠️ 未获官方页核验（仅第二篇单源） | F-131 | — |
| 20 | Cua Spaces 个人免费 | ✅ 通过 | F-133 → F-151 | cua.ai 首页 |

**计数：✅ 通过 14 项，⚠️ 时点/口径差异或未核验 6 项，❌ 失败 0 项。**

## 十四、跨信源对账（四元组）

> 对账对象：第一篇（`references/article-source.md` F-001~F-065，2026-09-26）与第二篇（本文 F-066~F-154，2026-10-08）在同一知识束内的表述差异。

### 对账 ①：模块命名 —— 第一篇「Fleets」vs 第二篇「Cua Spaces / sandbox」

- **现象**：第一篇五模块含 `Cua Fleets`（隔离云桌面集群，F-011）；第二篇六组件把对应位置写作 `Cua Spaces`，并在命令族中使用 `cua sb`（sandbox 沙箱）。
- **差异**：三个名称指向不同对象——`Cua Spaces` = macOS 桌面 App / 共享桌面产品线（source-available，FSL-1.1-MIT）；`Cua Fleets` = 托管云桌面集群付费服务（按用量计费，官方 SDK 中的 `Pool`/`@trycua/fleet`）；`sandbox`（`cua sb`）= gVisor 沙箱本地运行时。
- **影响**：若沿用单一名词，会把「本地沙箱 / 自有机器 Space / 托管 Fleet 池」三类资源混为一谈，F-011 与 F-079 有被误读为同一组件的风险；成本与许可结论随之错位（Fleets 付费、Spaces 个人免费、sandbox 开源 MIT）。
- **处置**：在正文与概念页按「三类资源」并列呈现，标注各自许可与计费；保留第一篇 F-011 原编号，不改写，仅补注第二篇对应名称为 Cua Spaces / sandbox。

### 对账 ②：接口命名 —— 第一篇「Sandbox SDK」vs 第二篇「Cua SDK 与 CLI（四语言）」

- **现象**：第一篇称云端与本地区共享 `Sandbox SDK`（F-011/F-036/F-037）；第二篇称 `Cua SDK 与 CLI`，提供 Python/TypeScript/Swift/Kotlin 四种语言接口（F-081）。
- **差异**：`Sandbox SDK` 是 `cua` SDK 中面向沙箱生命周期的高层子集（官方文档 `Sandbox SDK reference` 仍在使用该标题，见 F-152）；`Cua SDK 与 CLI` 是整体产品名，其 Rust 核心 + 四语言绑定由官方 README 的 Packages 表确认（F-148）。
- **影响**：两名称并非替代关系而是包含关系；若视作改名，会遗漏「同一 API 在本地与 Fleet 之间迁移」这一第一篇核心结论（F-037）。
- **处置**：正文采用「Cua SDK（含 Sandbox SDK 子集与四语言绑定）」的总分表述，两篇编号各自保留。

### 对账 ③：主语言 —— 第一篇快照 HTML vs 第二篇 Rust（约 47%）vs GitHub API 当前值

- **现象**：第一篇 2026-09-20 快照称主语言标记 HTML（F-026）；第二篇称以 Rust 为主、约占代码量 47%（F-073）；本文 2026-10-16 GitHub API `language` 字段为 Rust，languages API 计算 Rust 字节占比 42.31%（F-141/F-142）。
- **差异**：GitHub 主语言字段按仓库字节占比动态变化，属时点口径；两篇文章的百分比口径（47%）与当前实测（42.31%）存在差距。
- **影响**：主语言与占比不能作为稳定事实引用，缺少时点会误导读者。
- **处置**：三版数值并列并标注各自时点与口径；正文以「Rust 为当前主语言」表述，占比仅作时点参考。

### 对账 ④：Stars 三（四）版 —— 24,432 / 29,189 / 「2.8 万」/ 29,926

- **现象**：第一篇 2026-09-20 快照 24,432（F-016）；2026-10-10 API 29,189（F-055）；第二篇本文称「超过 2.8 万」（F-071）；本文 2026-10-16 API 29,926（F-140）。
- **差异**：均为同一仓库不同时点的快照；第二篇「2.8 万」是作者约数，相对其发布日（2026-10-08）前后的实测水平偏低。
- **影响**：若把任一行销数当现值，会低估项目动量；跨文档引用易产生陈旧数据。
- **处置**：正文统一采用「时点 + 数值」格式，给出 2026-10-16 现值 29,926 作为当前口径，其余三版作为历史时点登记。

## 十五、事实统计

| 类别 | 数量 | 编号范围 |
|------|------|---------|
| 第二篇文章元信息 | 4 | F-066~F-069 |
| 项目身份与动量 | 7 | F-070~F-076 |
| 六组件构成 | 10 | F-077~F-086 |
| Driver 机制与权限三档 | 10 | F-087~F-096 |
| Cua Bench 榜单 v1 | 15 | F-097~F-111 |
| 命令族 | 9 | F-112~F-120 |
| 许可分层 | 5 | F-121~F-125 |
| 废弃包与安全警告 | 2 | F-126~F-127 |
| 「何时不需要它」判断 | 3 | F-128~F-130 |
| 采用者与成本 | 3 | F-131~F-133 |
| 结语观点与文章元信息 | 6 | F-134~F-139 |
| 官方源核验补充 | 15 | F-140~F-154 |
| **合计** | **89** | **F-066~F-154** |

**类型分布**：`O` 客观事实 60 项；`V` 作者观点 7 项；`S` 厂商自述（含榜单）22 项。
（计算口径：O = F-066~F-081、F-083、F-085、F-088~F-100、F-110、F-112~F-120、F-126~F-127、F-138~F-139、F-140~F-154；S = F-082、F-084、F-086~F-087、F-101~F-109、F-111、F-121~F-125、F-131~F-133；V = F-128~F-130、F-134~F-137。合计 60+7+22=89。）

## 十六、未核验项与限制

1. **Cua Fleets 单价**（F-132）：无可达官方页检出，仅第二篇单源；官方文档仅确认 Fleet 池可能保留 warm capacity 并产生云用量费用（F-153）。
2. **权限三档命名与 `--dangerously-bypass-approvals`**（F-089~F-091）：未在可达官方页逐字检出，仅第二篇单源。
3. **采用者名单**（F-131）：Hermes/Clicky/H Company/Factory Droid 未获官方页核验，仅第二篇单源。
4. **第二篇正文**（F-154）：WebFetch 提取失败；页面 HTML 可达且标题存在，正文以父任务提供的提取文本为准。
5. **既有事实未改动**：本文件不写入 bundles 目录，F-001~F-065 保持原样；两篇文章同项声明以交叉引用（「同第一篇 F-xxx」）标注。
