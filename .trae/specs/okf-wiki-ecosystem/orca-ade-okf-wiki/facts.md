---
status: "draft"
version: "1.0"
---

# Orca ADE 事实登记簿（facts.md）

> **双份登记之一**：本文件与 bundle 内 `references/article-source.md` 必须编号集合一致且连续（V 阶段正则比对）。
> **信源距离层级**：`官方发布` / `作者一手实测` / `官方文档` / `第三方综述` / `厂商自宣`。
> **采集日**：2026-09-20（博文发布日 2026-09-14）。
> **F-001~F-060** = 博文事实（极客之家《GitHub 6.7万 Star，一个多 Agent 协作、手机远程指挥的开源神器！》原文口径）；**F-061~F-103** = 核验阶段补充事实（官方/第三方一手来源）。

## 一、博文事实（F-001~F-060）

| 编号 | 事实陈述（博文口径） | 层级 | P 级 | 核验结论 |
|---|---|---|---|---|
| F-001 | 项目名 Orca，是一个管理 AI 编程 Agent 的开源工具 | 第三方综述 | P1 | ✅ |
| F-002 | 文章称 Orca 在 GitHub 已有 6.7 万 Star，且仍在增长 | 厂商自宣 | **P0** | ⚠️ 核验日实测 66,453（≈6.6 万） |
| F-003 | Orca 由 Stably AI 开源 | 第三方综述 | P1 | ✅ |
| F-004 | Stably AI 是 YC 孵化出来的公司 | 第三方综述 | P1 | ✅ YC 页标注 Batch Winter 2022 |
| F-005 | 官方定位称 ADE（Agent Development Environment，智能体开发环境） | 第三方综述 | **P0** | ⚠️ "ADE" 缩写证实，全称无官方出处 |
| F-006 | 传统 IDE 里 AI 只是插件；Orca 中干活主力是 Agent，人主要管派任务和看进度 | 作者观点 | P2 | 观点，不核验 |
| F-007 | Orca 自身不含任何模型 | 官方文档 | P1 | ✅ |
| F-008 | 不需要注册 Orca 账号 | 官方文档 | **P0** | ⚠️ 口径矛盾，见 F-078/F-079 |
| F-009 | 本地已登录好的命令行 Agent 可直接接续使用 | 官方文档 | P1 | ✅ |
| F-010 | 官方列表具名 Agent 已排近三十种 | 厂商自宣 | **P0** | ⚠️ 官方三处口径不一，见 F-065/F-066 |
| F-011 | 具名 Agent 含 Claude Code、Codex、OpenCode、Grok、Cursor CLI、GitHub Copilot CLI | 官方文档 | P1 | ✅ 六个全部命中 |
| F-012 | 国产 Agent 支持 Kimi、Qwen Code、MiMo Code | 官方文档 | P1 | ⚠️ 前两个证实；MiMo Code 仅在 README 徽章行，官方 docs 表未列 |
| F-013 | 官方说法：只要 Agent 能在终端里跑，就能放进 Orca 里跑 | 官方文档 | P1 | ✅ "Works with any CLI agent" |
| F-014 | 核心功能为并行 Worktree：多个 Agent 同时干活 | 官方文档 | P1 | ✅ |
| F-015 | 同一个需求可同时派给好几个 Agent | 官方文档 | P1 | ✅ |
| F-016 | 每个 Agent 分到一个独立 git worktree（独立目录 + 独立分支） | 官方文档 | P1 | ✅ |
| F-017 | 各 Agent 改文件互不干扰 | 官方文档 | P1 | ✅ "isolated git worktree" |
| F-018 | 跑完在一个界面并排看 diff，挑一份最满意的合并，其余直接丢弃 | 官方文档 | P1 | ✅ |
| F-019 | 以前做同样的事需手动开多个终端、自建 worktree、人工记窗口与任务对应关系 | 作者观点 | P2 | 观点，不核验 |
| F-020 | 内置终端为 WebGL 渲染 | 官方文档 | P1 | ✅（同行另有 xterm.js 口径，见 F-085） |
| F-021 | 终端支持无限分屏 | 官方文档 | P1 | ✅ "infinite splits" |
| F-022 | 终端回滚记录在重启之后还在 | 官方文档 | P1 | ✅ "scrollback that survives restarts" |
| F-023 | 同时跑多个 Agent 时，所有输出平铺在一个窗口里 | 官方文档 | P1 | ✅ |
| F-024 | 某个 Agent 干完了会有通知，不用一直盯屏 | 官方文档 | P1 | ✅ |
| F-025 | 内置一个 Chromium 浏览器，提供 Design Mode | 官方文档 | P1 | ✅ |
| F-026 | Design Mode 下点击页面元素，该元素的 HTML、CSS 和截图一起发给 Agent | 官方文档 | P1 | ✅（文档另加 computed styles 与 source map） |
| F-027 | Diff 批注：可在 diff 视图某一行直接写评论，写完一起发回让 Agent 继续改 | 官方文档 | P1 | ✅ |
| F-028 | 该流程与人工 review 代码差不多 | 作者观点 | P2 | 观点，不核验 |
| F-029 | GitHub 和 Linear 集成：PR、Issue、项目看板可在 Orca 内直接看 | 官方文档 | P1 | ✅ |
| F-030 | 看到要做哪个任务，可一键从该任务开出新 worktree | 官方文档 | P1 | ✅ "open a worktree from any task" |
| F-031 | SSH 远程 Worktree：可把 Agent 放到远程服务器上跑 | 官方文档 | P1 | ✅ |
| F-032 | 远程场景下文件编辑、git、终端能力都是完整的 | 官方文档 | P1 | ✅ |
| F-033 | 断线自动重连 | 官方文档 | P1 | ✅ "auto-reconnect" |
| F-034 | 带端口转发 | 官方文档 | P1 | ✅ Ports tab 一键转发 |
| F-035 | iOS 和 Android 都有配套 App | 官方文档 | P1 | ✅ |
| F-036 | 与桌面端配对后，Agent 跑完手机会收到通知 | 官方文档 | P1 | ✅ |
| F-037 | 人不在电脑前也能发后续指令 | 官方文档 | P1 | ✅ "send follow-ups from anywhere" |
| F-038 | 状态栏直接显示 Claude 和 Codex 的用量与限流重置时间 | 官方文档 | P1 | ✅ |
| F-039 | 多个账号之间一键切换，不用重新登录 | 官方文档 | P1 | ✅ "hot-swap accounts" |
| F-040 | Orca 自己还带一条命令行（Orca CLI） | 官方文档 | P1 | ✅ |
| F-041 | CLI 可脚本化建 worktree、打快照、点界面等操作 | 官方文档 | P1 | ✅ `orca worktree create` / `orca snapshot` / `orca click` |
| F-042 | Agent 反过来也能驱动 Orca，可把整个流程接进自动化 | 官方文档 | P1 | ✅ "Agents drive Orca too" |
| F-043 | macOS 安装命令为 `brew install --cask stablyai/orca/orca` | 作者一手实测 | **P0** | ✅ 逐字证实，见 F-070 |
| F-044 | Windows 和 Linux 去官网 onorca.dev 或 GitHub Releases 下安装包 | 第三方综述 | **P0** | ⚠️ **域名拼写错误**：官网为 `onorca.dev`（非 `onnorca.dev`），见 F-069 |
| F-045 | Windows 安装包是 exe | 第三方综述 | P1 | ✅ `orca-windows-setup.exe` |
| F-046 | Linux 安装包是 AppImage | 第三方综述 | P1 | ✅ 另有 .deb/.rpm |
| F-047 | 安装后流程：打开 → 添加本地代码仓库 → 新建 worktree → 终端选 Agent → 说一句要做什么 | 作者一手实测 | P1 | ✅ 与官方 first-session 文档一致 |
| F-048 | 想对比方案时同一需求多开几个 worktree，一个 worktree 派一个 Agent | 官方文档 | P1 | ✅ |
| F-049 | Orca 自己不卖模型，也不收费 | 官方文档 | **P0** | ✅ "Free and open source"，无 pricing 页 |
| F-050 | 用的是已有 Agent 订阅，各 Agent 额度该怎么算还怎么算 | 官方文档 | P1 | ✅ "your own subscription" |
| F-051 | 同时派五个 Agent 出去，token 消耗也是五份 | 作者观点 | P2 | 观点（成本推断），与官方"自带订阅"口径自洽 |
| F-052 | 手机端 iOS 走 App Store 或 TestFlight | 官方文档 | P1 | ✅ |
| F-053 | Android 在官网下 APK | 官方文档 | P1 | ⚠️ 证实但有坑：无 Google Play 官方条目，且官方两处版本号不一致，见 F-095/F-096 |
| F-054 | 装好后跟桌面端配对就能用 | 官方文档 | P1 | ✅ "Pairing is one-time" |
| F-055 | 作者观点：Orca 能火是因为单个 Agent 已够用，真正耗人的是同时开几个之后多出来的杂事 | 作者观点 | P2 | 观点，不核验 |
| F-056 | 作者观点：平时只用一个 Agent、一次只干一件事的用户，Orca 偏重，可先观望 | 作者观点 | P2 | 观点，不核验 |
| F-057 | 作者观点：已在同时用两三个 AI 编程工具、被窗口和分支搞头疼的用户适合 | 作者观点 | P2 | 观点，不核验 |
| F-058 | 开源地址 `https://github.com/stablyai/orca` | 官方发布 | P1 | ✅ 仓库真实存在 |
| F-059 | 文章标题称 "GitHub 6.7万 Star" | 厂商自宣 | **P0** | ⚠️ 同 F-002 |
| F-060 | 文章标题称 "多 Agent 协作、手机远程指挥" | 第三方综述 | P1 | ✅ 与功能描述一致 |

## 二、核验补充事实（F-061~F-103）

| 编号 | 事实陈述（核验口径） | 来源 |
|---|---|---|
| F-061 | GitHub API：`stablyai/orca` 存在，`stargazers_count` = 66,453（核验日 2026-09-20） | api.github.com/repos/stablyai/orca |
| F-062 | 仓库 License 为 MIT License | 同上 |
| F-063 | 仓库主语言 TypeScript，创建于 2026-03-17 | 同上 |
| F-064 | 仓库描述："Orca is the ADE for working with a fleet of parallel agents…" | 同上 |
| F-065 | README 徽章行 "Works with any CLI agent"，具名 Agent 29 个 | github.com/stablyai/orca |
| F-066 | 官方 `docs/agents/supported` 表 35 行；官网首页口径 27 个——与 README 29 个三处不一致 | onorca.dev/docs/agents/supported |
| F-067 | 最新正式版 v1.4.205（2026-09-17） | api.github.com/repos/stablyai/orca/releases/latest |
| F-068 | Release 资产：`orca-macos-arm64.dmg`、`orca-macos-x64.dmg`、`orca-windows-setup.exe`、`orca-linux.AppImage`、`orca-linux-arm64.AppImage`、`.deb`、`.rpm`（macOS 无 zip 安装包） | 同上 |
| F-069 | **官网真实域名为 `onorca.dev`**（仓库 homepage 字段为 `https://onOrca.dev`；`onnorca.dev` 无法获取内容） | api.github.com/repos/stablyai/orca |
| F-070 | Homebrew tap `stablyai/homebrew-orca` 的 `Casks/orca.rb`：`cask "orca"`、`version "1.4.205"`、`desc "IDE for orchestrating AI coding agents across terminals and worktrees"`、`homepage "https://onorca.dev/"` | github.com/stablyai/homebrew-orca |
| F-071 | **同名混淆**：Homebrew 官方仓库 `homebrew/cask` 的 cask `orca` 是 plotly 的图表工具（v1.3.1，2026-09-01 因 fails_gatekeeper_check 被 disabled），与 Stably 版无关；Stably 版必须用全限定名 `stablyai/orca/orca` | formulae.brew.sh/api/cask/orca.json |
| F-072 | YC 公司页 "Stably AI (Orca)"：Batch **Winter 2022**，Active，旧金山，Team 25 | ycombinator.com/companies/stably-ai-orca |
| F-073 | 创始人 Jinjing Liang（CEO）、Neil Parker；公司主营 Stably（AI 测试平台 stably.ai） | 同上 |
| F-074 | 官方标语 "Ship 100x with the agent IDE"；官方 docs 首页自称 "a desktop IDE"；官网另有 "An ADE is built for you and your agents" | onorca.dev / onorca.dev/docs |
| F-075 | 官方 docs："**Not a model.** Orca runs agents you already use — bring your own Claude, Codex, or OpenCode subscription." | onorca.dev/docs |
| F-076 | 官方 docs：Orca 会以正确的工作目录启动 agent CLI，并转发你的订阅凭据 | onorca.dev/docs/first-session |
| F-077 | 首次启动提供导入 `~/.claude`、`~/.codex` | 同上 |
| F-078 | 官方 telemetry 文档称 "**Orca has no account system**" | onorca.dev/docs/telemetry |
| F-079 | 官方 mobile 文档要求 "signed into the same Orca account"，"sign-in is required for **Relay only**" | onorca.dev/docs/mobile |
| F-080 | 官网 "Free and open source."；`/pricing` 返回 404，全站无计费页 | onorca.dev |
| F-081 | 官方："Orca does **not** sell managed VPS hosting"；"your provider account, images, and billing stay yours" | onorca.dev/docs/ways-to-run |
| F-082 | 官方 worktrees 文档："Fan one prompt across five agents, each in its own isolated git worktree — compare the results and merge the winner." | onorca.dev/docs/model/worktrees |
| F-083 | 官方 first-session 文档："Three branches. Three diffs. Same prompt." | onorca.dev/docs/first-session |
| F-084 | 官方 terminal 文档："Ghostty-class terminals with **WebGL rendering**, **infinite splits**, and **scrollback that survives restarts**" | onorca.dev/docs/terminal |
| F-085 | 同一 terminal 文档另称其是 "the same **xterm.js-based** terminal VS Code uses"——与 WebGL 口径并存 | 同上 |
| F-086 | 官方 notifications 文档：agent 从 working 转为 idle 时触发系统通知 + 声音 + chip | onorca.dev/docs/notifications |
| F-087 | 官方 design-mode 文档："Click any UI element in a real **Chromium** window to send its **HTML, CSS, and a cropped screenshot** straight into your agent's prompt." | onorca.dev/docs/browser/design-mode |
| F-088 | 官方 annotate 文档："**Drop comments on any diff line and ship them back to the agent**" | onorca.dev/docs/review/annotate-ai-diff |
| F-089 | 官方："**GitHub & Linear, Native** — Browse PRs, issues, and project boards in-app — **open a worktree from any task**" | onorca.dev/docs/review/linear |
| F-090 | 官方 SSH 文档："**auto-reconnect and port forwarding included**"；"Orca reconnects and re-attaches"；侧栏 Ports tab 一键转发 | onorca.dev/docs/ssh |
| F-091 | 官方 mobile 文档："iOS and Android apps…get notified when an agent finishes and **send follow-ups from anywhere**"；"**Pairing is one-time**" | onorca.dev/docs/mobile |
| F-092 | 官方 usage-tracking 文档："See **Claude and Codex usage and rate-limit resets**, and **hot-swap accounts without re-logging in**"；状态栏呈现，5 小时/日/周重置，80% 警告 chip | onorca.dev/docs/agents/usage-tracking |
| F-093 | 官网 `/download` 同时提供 App Store 与 Android APK；README 另给 TestFlight 链接 | onorca.dev/download |
| F-094 | App Store 条目 **"Orca IDE"**，副题 "Manage Coding Agents Remotely"，免费，iPhone/iPad，6 个评分 5.0，开发者栏显示 **Lovecast LLC** | apps.apple.com/us/app/orca-ide/id6766130217 |
| F-095 | Android **仅走 GitHub Releases APK**；核验日未发现 Google Play 官方条目（Play 上的 "Orca: Boat GPS…" 为航海 App，无关） | github.com/stablyai/orca/releases |
| F-096 | 官方两处 Android 版本口径不一致：官网 `/download` 写 "APK 0.0.48"，README 链接为 `mobile-android-v0.0.50` | onorca.dev/download / github.com/stablyai/orca/releases |
| F-097 | 官方 CLI 文档：命令为 `orca`（随桌面端附带）；含 worktree/terminal/file/browser 命令族，`orca worktree create`、`orca snapshot`、`orca click`、`orca fill`；另有 `orca serve`（无头 Linux） | onorca.dev/docs/cli/overview |
| F-098 | 官方安装页另提供 Arch 的 `yay -S stably-orca-bin` | onorca.dev/docs/install |
| F-099 | 第三方星标统计：gstars.dev 于 2026-09-17 显示 70.5K；stably.ai 官网页面显示 71.4k | gstars.dev / stably.ai |
| F-100 | 第三方（Hacker News）用户评价："I've been impressed with orca"、"largely enjoying it" | news.ycombinator.com/item?id=49742023 |
| F-101 | 第三方分析：agent fleet management 能否成为独立品类是更难的战略问题；并指出 README 未含采用数据、star 数或独立基准，发布声明为公司自述 | aiinsiders.net |
| F-102 | 第三方对支持 Agent 数量的口径不一：多数写 "30+"，亦有 "25+" | andrew.ooo / dev.to / qiita.com |
| F-103 | 无官方 quickstart 页（`/docs/quickstart` 404）；官方入门页为 `/docs/first-session`，安装页为 `/docs/install` | onorca.dev |

## 三、勘误表（博文错误口径 → 正确口径）

| # | 博文口径 | 正确口径 | 证据 | 影响面 |
|---|---|---|---|---|
| E-1 | 官网 `onnorca.dev` | 官网 **`onorca.dev`**（博文多打一个 n） | F-069、F-070、F-072 | 硬错误：照抄会把读者带到不存在的域名 |
| E-2 | "也不需要注册什么 Orca 账号"（绝对口径） | 桌面端官方宣称"no account system"；但**移动端配对/Relay 明确要求登录同一 Orca 账号**，官方文档自相矛盾 | F-078、F-079 | 核心声明部分失真：桌面可用 ≠ 全功能免账号 |
| E-3 | "6.7 万 Star" | 核验日 66,453（≈6.6 万）；第三方统计 70.5K–71.4K（时点不同） | F-061、F-099 | 时点口径，量级成立 |
| E-4 | "官方给它的定位叫 ADE，Agent Development Environment" | 官方仅使用缩写 **ADE**、或 "agent IDE"/"desktop IDE"；**全称无官方出处**（仅第三方与 GitHub topic 佐证） | F-064、F-074 | 表述外推，需标注 |
| E-5 | 官方列表具名 Agent "已经排了将近三十种" | 官方三处口径不一：README 29 / 官网 27 / docs 表 35 行；第三方 25+~30+ | F-065、F-066、F-102 | 数字口径不稳定 |
| E-6 | Android "在官网下 APK" | 方向正确，但需补充：无 Google Play 官方条目；官网（0.0.48）与 README（0.0.50）版本号不一致 | F-095、F-096 | 补充而非纠正 |
| E-7 | 未提安装包形态 | macOS 实为 **.dmg**（无 zip 安装包）、Windows 为 `.exe`、Linux 为 `.AppImage`（另有 .deb/.rpm） | F-068 | 补充 |

## 四、核验方法与未覆盖边界

- **方法**：GitHub API（`/repos`、`/releases/latest`）+ 仓库 raw README + 官网 `onorca.dev`（首页、/download、/docs 各页）+ Homebrew tap 源码 + YC 公司页 + 第三方报道交叉印证
- **未覆盖**：① 博文发布日（2026-09-14）的星标时点快照无法还原，仅能取核验日实测值；② 官网 FAQ 折叠块为 JS 手风琴，正文未能取到；③ App Store 主体 "Lovecast LLC" 与 Stably AI 的法律实体对应关系无官方说明；④ Orca 项目 2026-03 建仓与 YC W22 批次的时序关系未获官方解释；⑤ 官方"no account system"与移动端"sign-in required"的矛盾未获官方澄清
- **未真机实测**：examples 命令经官方文档逐字比对，但本包制作中未在任何平台执行