---
type: Facts
id: facts-openhuman-blog-okf-wiki
title: OpenHuman 博文转化事实集（F-001~F-064）
date: 2026-09-16
source:
  - https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
---

# 事实集：开源先驱博文《又一个人AI助手炸了》→ OpenHuman

> 主信源：微信公众号「开源先驱」（作者豆芽菜小萌）2026-07-28 博文。F-001~F-042 出自博文；F-043~F-064 为 2026-09-16 核验补充（GitHub 仓库页面/API + 官方 GitBook + openhuman.dev + 第三方）。
> 级别：P0 必核验 / P1 选核验 / P2 可单源；作者观点显式标注。

## 一、博文元信息

| 编号 | 事实 | 级别 |
|------|------|------|
| F-001 | 博文标题《又一个人AI助手炸了。连续9天GitHub Trending第一，3,900次提交，7,800+ Star》（"又一个人AI助手"为原文，疑为"又一个个人AI助手"脱字） | P2 |
| F-002 | 公众号「开源先驱」，作者署名「豆芽菜小萌」，2026-07-28 06:48 发布于北京，带微信"原创"标记 | P2 |
| F-003 | 博文性质：第三方自媒体开源项目介绍/推广文；作者自陈"我翻了翻社区讨论和评测"，未声明一手实测；文末为"点赞/在看/转发"导流与标题党推荐阅读 | P2 |

## 二、热度与项目元数据（博文口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-004 | 博文称项目"发布一周内连续 9 天霸榜 GitHub Trending 第一" | P0 |
| F-005 | 博文称 3,926 次 commit，已迭代到 v0.63.3、"迭代了六十多个版本" | P0 |
| F-006 | 博文标题称 7,800+ Star | P0 |
| F-007 | 博文称 GPLv3 开源、Rust + Tauri 构建 | P0 |

## 三、产品定位

| 编号 | 事实 | 级别 |
|------|------|------|
| F-008 | 博文引用项目定位语："Every model in the world shares the same fundamental limitation: they are stateless."（世界上所有模型都有同一个根本缺陷：它们没有状态） | P1 |
| F-009 | 博文称 OpenHuman 解决的就是 stateless 问题——让 AI 真正"认识你"：知道你的项目、日程、昨天和同事聊了什么 | P1 |
| F-010 | 博文归纳：OpenHuman 不是又一个聊天机器人，而是持续运转、知道你是谁、能自己干活的个人数字分身 | 作者归纳 |

## 四、三大能力与四个痛点

| 编号 | 事实 | 级别 |
|------|------|------|
| F-011 | 能力一"有记忆的大脑"：Memory Tree 层级摘要树，博文称容量可达 10 亿 token，持续更新；存本地 SQLite 并生成 .md 文件同步到 Obsidian | P0 |
| F-012 | 能力二"编排器"：基于检查点图（checkpoint graph）的 Agent 运行时，管理 Agent 舰队；快速反射 Agent 处理入站流量，深度推理核心把复杂工作委派给 Worker | P1 |
| F-013 | 能力三"深度研究员"：研究侦察兵在用户问完问题之前已扫完记忆库和文件系统，无冷启动、无"让我想想"的等待 | P1 |
| F-014 | 痛点①AI 无长期记忆：Memory Tree 以层级摘要树替代线性对话记录，不仅记得"有什么"，还记"什么重要""它们之间什么关系" | P1 |
| F-015 | 痛点②数据孤岛：通过 118+ OAuth 集成打通 Gmail/Slack/GitHub/Notion/Google Calendar 等十几个平台，每 20 分钟自动同步 | P0 |
| F-016 | 痛点③上下文成本：TokenJuice 压缩层最高省 80% token，"日积月累一个月能省几百块" | P0 |
| F-017 | 痛点④上手门槛：桌面应用优先，图形界面、OAuth 一键授权、装好就能用 | P1 |

## 五、Memory Tree 机制（博文口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-018 | 博文六步流程：①从 118+ OAuth 连接拉取邮件/文档/聊天/代码仓库/日历；②标准化为不超过 3,000 token 的 Markdown 块；③按时效性/相关性/来源权重打分；④折叠为 per-source/per-topic/per-day 层级摘要树；⑤存本地 SQLite 同时生成 .md 同步 Obsidian；⑥每 20 分钟自动增量更新 | P0 |
| F-019 | 博文对比表：记忆容量（传统上下文窗口几万 token / RAG 百万级 / Memory Tree 10 亿 token）；记忆结构（线性文本 / 向量检索 / 层级摘要树）；更新频率（每次对话 / 手动索引 / 自动 20 分钟）；可读性（不可读 / 不可读 / Obsidian 可编辑）；隐私（云端 / 可控 / 本地优先） | P1（博文整理口径） |

## 六、TokenJuice（博文测算口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-020 | 博文测算：一封 HTML 邮件 5KB + GitHub issue 页 10KB + 三份文档 15KB = 30KB 原始数据约 8,000 token，压缩后 6KB 约 1,600 token；按 GPT-4o 价格一次深度分析从 $0.04 降到 $0.008，每天 50 次则月成本 $60→$12 | P0（博文自行测算） |
| F-021 | 博文列压缩手段与省幅：HTML 转 Markdown 省 40-60%、长 URL 缩短 5-10%、非 ASCII 字符清理 5-15%、重复内容去重 10-30%，全栈最高省 80% | P0（博文口径） |

## 七、竞品对照（博文口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-022 | 博文对比表：Claude Cowork（闭源 / 桌面+CLI / 对话级记忆 / 少量集成 / 无自动同步 / 无消息渠道 / 不支持参会）；OpenClaw（MIT / 终端优先 / 依赖插件记忆 / 需自建 / 无 / 少量 / 不支持）；OpenHuman（GPLv3 / UI 优先几分钟上手 / Memory Tree+Obsidian / 118+ OAuth / 20 分钟自动 / 17 个消息渠道 / Meet·Zoom·Teams·Webex） | P0 |

## 八、特色设计

| 编号 | 事实 | 级别 |
|------|------|------|
| F-023 | 桌面吉祥物：有表情、会说话，主动提醒新邮件摘要/日历提醒/系统通知；关闭窗口后仍常驻桌面 | P1 |
| F-024 | 潜意识系统（Subconscious）：后台循环持续对比世界状态、推进长期目标、撰写晨间简报 | P1 |
| F-025 | 会议 Agent：以真人参与者身份加入 Google Meet、Zoom、Teams、Webex，自动从日历加入，提供实时转录和摘要 | P0 |
| F-026 | Split Brain 双脑架构：快速反射 Agent 处理入站流量（消息、通知），深度推理核心把复杂工作委派给 Worker 舰队 | P1 |
| F-027 | 一键隐私模式：所有推理不离开设备，Rust 核心强制执行；核心记忆数据存本地 SQLite，可接 Ollama 跑本地模型，敏感任务不上云 | P1 |
| F-028 | Agent Economy：在 tiny.place 拥有自己的 @handle，支持 Signal 加密的 Agent 间编排，x402 USDC 赏金和交易，Agent 之间可互相"雇佣" | P0 |

## 九、技术栈（博文表）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-029 | 博文技术栈表：桌面框架 Tauri（Rust 后端 + Web 前端）；前端 React/TypeScript；核心 Runtime Rust；数据库 SQLite；AI 模型 Claude/GPT/Gemini/Ollama 本地；安全 ChaCha20-Poly1305 / Signal Protocol E2E；构建工具 Cargo/CMake/Ninja/pnpm；许可证 GPLv3 | P0 |

## 十、获取与上手

| 编号 | 事实 | 级别 |
|------|------|------|
| F-030 | 博文安装方式：macOS/Linux `curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh \| bash`；Windows `irm .../install.ps1 \| iex`；`brew install --cask openhuman`；亦可从 GitHub Releases 下载 | P0 |
| F-031 | 博文"三步走"：OAuth 授权连接 3-5 个核心服务（邮箱+日历+GitHub+文档）；等 5-10 分钟让 Memory Tree 完成初始同步；之后可直接问"我今天有什么会""帮我总结上周的邮件" | P1 |
| F-032 | 博文源码构建：`git clone` → `git submodule update --init --recursive` → `pnpm install` → `pnpm dev`（Web UI）/ `pnpm --filter openhuman-app dev:app`（桌面应用） | P1 |

## 十一、短板（博文评测口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-033 | Early Beta：3,900 次 commit 说明迭代飞快，也说明稳定性仍在打磨；文档不全、部分功能缺详细说明，生产环境慎重 | P1 |
| F-034 | OAuth 连接器良莠不齐：Gmail/GitHub 稳定，部分小众服务 token 偶尔过期需重新授权；同步频率固定 20 分钟，无法手动触发即时同步 | P1 |
| F-035 | 资源占用不轻：桌面吉祥物+后台同步+持续思考，建议 8GB+ 内存，4GB 机器吉祥物动画会卡 | P1 |
| F-036 | 中文体验依赖底层模型：英文体验最好，中文效果取决于接的是 GPT-4o 还是本地模型，纯中文场景建议先试再定 | P1（作者建议） |
| F-037 | 只有桌面端（Windows/macOS/Linux 全覆盖），移动端暂时没有 | P1 |

## 十二、作者结论

| 编号 | 事实 | 级别 |
|------|------|------|
| F-038 | 作者观点：连续 9 天霸榜 Trending 不是靠营销，而是踩中"所有 AI 助手都没有记忆"的真实痛点 | 作者观点 |
| F-039 | 作者观点：10 亿 token 容量、118+ OAuth、TokenJuice 省 80%、一键隐私模式不是噱头，是认真想过"个人 AI 助手该长什么样"后的产物；Rust+Tauri 比 Electron 方案轻，UI 优先不需要命令行 | 作者观点 |
| F-040 | 作者观点：OpenHuman 不是 ChatGPT/Claude 的替代品——它做"了解你这个人"而非"回答你这个问题"；最佳用法是组合（ChatGPT/Claude 做通用对话创作，OpenHuman 做个人记忆与自动化） | 作者观点 |
| F-041 | 作者建议：知识工作者、Obsidian 用户、在多个工具间切换的人值得现在就装；只想找 AI 聊天则 ChatGPT 够用 | 作者观点 |
| F-042 | 博文给出的项目地址：https://github.com/tinyhumansai/openhuman（原文为纯文本） | P2 |

## 十三、核验补充事实（2026-09-16，GitHub 实测 + 官方文档）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-043 | 仓库真实存在：`github.com/tinyhumansai/openhuman`；About 原文 "OpenHuman is an open source agent harness with local-first memory, agent orchestration, and workflows"；官网 tinyhumans.ai/openhuman；官方文档 tinyhumans.gitbook.io/openhuman；GitHub 仓库创建于 2026-02-18 | GitHub 仓库页/API |
| F-044 | 2026-09-16 仓库实况：39.8k stars（39,814）、3.9k forks（3,922）、201 watching、190 open issues、6 open PR、183 contributors；语言构成 Rust 58.6% / TypeScript 37.9% / JavaScript 2% / Shell 1.4% | GitHub 页面+API |
| F-045 | License 侧栏与 API 均为 GPL-3.0（GNU General Public License v3.0）——博文 F-007"GPLv3"准确 | GitHub |
| F-046 | 版本实况：最新 release v0.63.12（2026-08-07）；release 共 **56 个**（最早 v0.49.32，2026-03-31）；git tag 共 **106 个**（最新 v0.63.21，main 头部已有 v0.63.29 release 提交）；博文 2026-07-28 所写 v0.63.3 处于该序列合理时点 | GitHub Releases/Tags API |
| F-047 | 提交总数 2026-09-16 为 **20,551**；博文 7-28 称 3,926——历史值无法回溯，当前值约为其 5.2 倍，7 周新增约 1.66 万提交（周均约 2,400，与 183 contributors 活跃规模相容但未能独立证实博文时点值） | GitHub |
| F-048 | "连续 9 天 Trending 第一"获官方 README 自认，原文："Within one week of launch, OpenHuman became the number one trending repository on GitHub for nine days in a row."——时间锚点是"发布后一周内"，博文标题省略该时间限定 | GitHub README |
| F-049 | OAuth 集成数口径漂移：2026-09 官方 README 为 "100+ OAuth integrations, 5,000+ MCP servers, 90,000+ Skills"；2026-05-17 快照的第三方官方指南 openhuman.dev 写 "118+ OAuth connectors"；博文 7-28 的 118+ 与 5 月快照一致，9 月官方口径已变为 100+ | GitHub README / openhuman.dev |
| F-050 | 消息渠道口径差异：2026-09 README 为 "15 messaging channels: Telegram, Discord, Slack, WhatsApp, Signal, iMessage… plus native email (IMAP IDLE + SMTP)"；博文称 17 个——当前官方口径为 15（含原生邮件） | GitHub README |
| F-051 | Memory Tree 机制经官方 GitBook 证实并比博文更完整：确定性管线（canonicalize → ≤3k token 内容寻址分块 → fast-score → 单事务持久化 → 后台深处理）；source/topic/global 三棵摘要树（L0 缓冲填满 seal 为 L1 并级联；topic 按 hotness 物化；global 每日 UTC digest）；持久作业队列 + 默认 3 个后台 worker + 信号量限流；leaf 生命周期 `pending_extraction → admitted → buffered → sealed / dropped`；磁盘位置 `~/.openhuman` 下 `memory_tree/chunks.db` + `wiki/` Obsidian vault；每 20 分钟 auto-fetch，亦可在 Intelligence 页手动 "Run ingest"，RPC `openhuman.memory_tree_ingest`；可选外部后端 agentmemory | GitBook features/memory-tree |
| F-052 | "10 亿 token 容量 / 10M tokens @4,000 tokens/s / NeoCortex"在官方 README 与官方 GitBook Memory Tree 页均**未见**；仅第三方 AI 生成知识库 agentic-ai.readthedocs.io（2026-05）给出该数字与"NeoCortex"系统名——属第三方单源，官方未背书 | agentic-.readthedocs.io；官方文档反证（未见） |
| F-053 | TokenJuice "up to 80% fewer tokens" 获 README 与 GitBook《Smart Token Compression》双重证实；官方机制为多阶段压缩路由器（≥2KB size gate → 类型检测 Json/Diff/Html/Search/Code/Log/PlainText → 专用压缩器 → CCR 缓存原文并附 ⟦tj:hash⟧ 标记 → 记录节省），代码始于对 vincentkoc/tokenjuice 的移植（vendor/tinyjuice）；博文 F-021 的细分省幅与 F-020 的金额测算为博文自行推算，官方文档无对应数字 | GitHub README / GitBook token-compression |
| F-054 | 会议能力获 README 对比行证实："🚀 Joins Meet/Zoom/Teams/Webex, speaks, live transcript"——四平台、会中发言、实时转录三项均在 | GitHub README |
| F-055 | Agent 间通信：README 明确 "Agent-to-agent messaging runs over Signal-protocol end-to-end encryption"、"instances orchestrate each other over Signal-protocol E2E sessions with x402 payments. No server ever sees plaintext"——Signal E2E 与 x402 payments 证实；"tiny.place/@handle"、"USDC"、"赏金/bounty" 字样在 README 未见 | GitHub README |
| F-056 | 安全：Signal Protocol E2E 官方明确；博文技术栈表中的 "ChaCha20-Poly1305" 在 README 未见，未获官方证据 | GitHub README |
| F-057 | 技术栈核验：Tauri（crates/openhuman-app Tauri desktop shell）、Rust workspace（贡献指南要求 Rust 1.96.1）、SQLite、Node.js 24+/pnpm/TypeScript 均有；README 正文未出现 "React"；Ollama 全本地模型明确支持（"your own provider key or a fully local Ollama model, and mix the three"），GPT/Gemini 未以模型名出现（以自有 provider key 泛指托管模型） | GitHub README/CONTRIBUTING |
| F-058 | 安装脚本真实存在：`scripts/install.sh`（HTTP 200，21,787 字节，bash）与 `scripts/install.ps1`（HTTP 200，9,013 字节，pwsh），scripts/ 目录共 109 项；`brew install --cask openhuman` 见于官方 INSTALL.md（另支持 Debian/Ubuntu .deb、AUR）；README 顶部有 4 枚 Product Hunt 徽章 | GitHub raw/INSTALL.md |
| F-059 | 硬件口径：openhuman.dev 官方指南（2026-05-17 快照）写"RAM baseline 4 GB+ cited in Getting Started；大型 Gmail/代码库 + 可选本地模型建议 16GB+；建议快速 SSD"；博文称"建议 8GB+、4GB 动画会卡"——官方基线 4GB+，博文建议更保守，两口径并存 | openhuman.dev/requirements |
| F-060 | Early Beta 状态官方证实：徽章 "Early Beta" + 正文 "Early Beta: Under active development. Expect rough edges."；仓库 2026-02-18 创建、最早 release 2026-03-31；第三方知识库称 "launched in beta on May 13, 2026"，该来源为 AI 生成知识库，仅作参考 | GitHub README；readthedocs（弱源） |
| F-061 | 第三方官方指南 openhuman.dev 的竞品表比较四款：Claude Cowork（闭源/Desktop+CLI）、OpenClaw（MIT/Terminal-first）、Hermes Agent（MIT/Terminal-first）、OpenHuman（GNU/UI-first/Memory Tree+Obsidian/118+ OAuth/~20min sync）——博文三选品与官方表一致（博文未提 Hermes Agent），"Claude Cowork 闭源、OpenClaw MIT"口径一致 | openhuman.dev |
| F-062 | 博文导语所称"内置完整 Linux 沙箱"在官方 README 渲染正文中未见，GitBook 公开功能页亦未核到对应表述——仅博文单源，存疑 | 官方文档未见 |
| F-063 | 第三方独立长评（honbul.tistory.com，2026-05-19）声明基于 main 分支 README/CONTRIBUTING/AGENTS.md、Cargo manifest、GitBook 分析，交叉证实 Tauri 桌面定位、吉祥物与 Google Meet 参与、118+ 集成 + 20 分钟 auto-fetch、Memory Tree + Obsidian vault 等博文主干 | honbul.tistory.com/266 |
| F-064 | 第三方 AI 知识库称项目上线首日 +1,694 stars/day、两周内达 27k+ stars——该站为 AI 生成内容、数字无法回溯到 GitHub 官方历史，与博文标题 7,800+（2026-07-28）存在数量级冲突；两个历史数字均不可确认，唯一权威时点值为 2026-09-16 的 39.8k（F-044） | 弱源冲突，存疑 |

## 可信度分层

| 等级 | 事实编号 | 说明 |
|------|---------|------|
| ✅ 官方核验 | F-007/F-045, F-043, F-048, F-051, F-053, F-054, F-058, F-060(Early Beta), F-061 | 许可证、仓库存在、9 天 Trending（README 自认）、Memory Tree 机制、80% 压缩、四会议平台、安装命令、Beta 状态 |
| ⚠️ 口径漂移/单源 | F-004, F-005, F-006, F-011, F-015, F-022, F-028, F-029, F-035, F-052, F-056, F-057, F-062, F-064 | 118→100+、17→15、10 亿 token 仅弱源、star/commit 历史不可回溯、tiny.place/USDC、ChaCha20、React、Linux 沙箱 |
| 📝 作者观点 | F-010, F-036, F-038, F-039, F-040, F-041 | 定位归纳、中文体验建议、爆火归因、组合使用论 |
| 📊 博文测算 | F-020, F-021 | token 省幅细分与美元成本为博文假设推算（80% 上限有官方出处） |
