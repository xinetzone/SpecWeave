---
type: Facts
id: facts-loopx-long-horizon-agent-blog
title: LoopX 博文事实集（F 编号登记 · 唯一合法事实集）
source: https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ
created: 2026-09-16
---

# 事实集：《一个悄然崛起的国产开源项目，让 AI Agent 跑满 200 小时不掉线》

> 登记规则：F-001 起连续编号。来源列：【博】=博文事实；【官】=核验补充事实（官方源）。
> 观点条目显式标注「作者观点」。P0 核验结论：✅ 通过 / ⚠️ 口径或时效问题（见 verification.md）/ ❌ 失败（本任务 0 项）。

## A. 信源元信息

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-001 | 标题《一个悄然崛起的国产开源项目，让 AI Agent 跑满 200 小时不掉线》；公众号「极客之家」；作者「丛林」；发布于 2026-09-03 14:05；标注原创，文末定位山西 | 【博】 | ✅ browser 提取页面元信息 |
| F-002 | 文章 URL：https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ ；正文 2777 字符 | 【博】 | ✅ |
| F-036 | 「极客之家」公众号自述定位：长期分享实用开源项目，可后台留言互动 | 【博】 | P2 单源（自述） |

## B. 问题陈述与作者动机

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-003 | 作者描述长周期使用痛点：AI 编程工具连续工作数天时，第二天上下文中已无第一天目标，改过哪些文件、为何改对不上，无法复盘 | 【博】作者观点（体验陈述） | P2 |
| F-004 | 作者称执行节奏会乱：该停下确认时不停一路跑；无进展时一轮轮空烧 token | 【博】作者观点 | P2 |
| F-005 | 作者判断：靠聊天记忆加定时器管不住长周期任务 | 【博】作者观点 | P2 |

## C. LoopX 定位与热度

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-006 | LoopX 是开源、本地优先（local-first）的长程 Agent 控制面（control plane），作者称之为"状态内核"，运行在现有 AI 编程工具之上而非取代它们 | 【博】 | ✅ 官方 README 同口径："open, provider-neutral, stateful control plane for long-horizon agents" |
| F-007 | 分工：Codex、Claude Code、Cursor 等宿主负责逐轮执行；LoopX 管理跨轮次、跨天事项——目标、当前卡点、下一轮动作、每轮证据、剩余预算 | 【博】 | ✅ 官方 README 状态层描述一致 |
| F-008 | 博文称项目 GitHub 已有 5000 多 Star，"开源不久"，纯 Python 编写 | 【博】 | ⚠️ Star ✅（2026-09-13 API 实测 5818，见 F-037，量级一致）；"纯 Python"见 F-041 勘误 |
| F-009 | 官方一句话定位："把会干活的 Agent，接成可管理、可复盘、可持续改进的数字员工" | 【博】 | ✅ PyPI/GitHub 项目描述逐字一致（中文原句） |
| F-035 | 开源地址：https://github.com/huangruiteng/loopx | 【博】 | ✅ 仓库存在 |
| F-037 | GitHub API 实测（2026-09-13 数据）：star 5818、fork 530、watch 28、开放 issue 83；Apache-2.0 许可；仓库创建于 2026-05-31；GitHub 语言统计主语言为 Python；topics 含 agent-control-plane、agent-harness、agent-ops、long-horizon-agents、loop-engineering 等 | 【官】api.github.com/repos/huangruiteng/loopx | ✅ |

## D. 核心功能（博文六块）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-010 | 状态内核：目标建立后，范围、进展、每轮证据等持久状态全部存于本地文件，不走任何云服务 | 【博】 | ✅ "Local first" 徽章 + 本地状态目录 `.loopx/`、`.codex/goals/`、`.local/`（F-046） |
| F-011 | 宿主会话关闭、电脑重启、隔一周再打开，工作可从上次停下的轮次续跑，无需翻聊天记录推断 | 【博】 | ✅ 官方"durable across days, restarts, and harnesses"同口径 |
| F-012 | quota 机制：每次调度触发前先执行 `quota should-run` 检查——该 Agent 现在该行动吗、还有预算吗、有无实际状态变化 | 【博】 | ✅ 命令与语义逐字一致（官方核心 tick 五命令之首） |
| F-013 | 无状态变化则跳过，该轮不计费；空转、预检失败、试运行（dry-run）均不计费 | 【博】 | ✅ 官方逐字："Quiet skips, preflight failures, and dry-run previews do not spend"（F-044） |
| F-014 | 人类门禁（human gate）：需要人拍板的节点循环会暂停，并携带具体问题（如"这个改动要不要合入""这条路线还要不要继续"），答复后才继续，非模糊的"等待确认" | 【博】 | ✅ "Concrete user gates instead of a vague 'waiting for owner'" |
| F-015 | 危险权限、对外发布、生产环境写操作决定权始终在人；项目不做全自动生产控制 | 【博】 | ✅ "LoopX is not an autonomous production controller. Dangerous permissions, publishing, production writes, and final ownership stay with the human." |
| F-016 | `loopx dashboard` 在浏览器拉起本地工作台：进行中的目标、等待回复的门禁、定时挂起与已停任务均可见 | 【博】 | ✅ 官方支持的浏览器/PWA 启动路径；1.0 另有桌面预览版（F-049） |
| F-017 | 工作台可同时挂多个 Agent 会话（Codex 干一段、Claude Code 接一段），目标状态与证据不丢 | 【博】 | ✅ "continue across Codex, Claude Code, direct-model, and other registered Agent sessions without losing Goal state or evidence" |
| F-018 | 多宿主支持：Codex App、Codex CLI、Claude Code、Cursor 均有现成接入方式；国产 DeepSeek Harness 也支持；不使用这些工具可接自定义 runner；支持多 Agent 协作 | 【博】 | ✅ 官方宿主表确认且范围更大（另含 KunlunCode/OpenCode/Pi/ZCode/Antigravity/Kiro 等，F-045） |

## E. 200 小时实证

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-019 | 作者把自己作为 OpenViking 贡献者的公开 PR 序列贴出：从第一个 PR 到最近一次 review 时间跨度超 200 小时；过程中 issue 修复与可复用修复知识同步沉淀 | 【博】 | ✅ 官方 README 有专节；GitHub Search 实测 huangruiteng 在 volcengine/OpenViking 有 169 个公开 PR，最早 2026-07-17（F-042） |
| F-020 | 博文专门转述作者标注的边界：200 小时指项目从始至终的自然时间跨度（wall-clock），模型并未连续跑 200 小时，也不代表无人值守 | 【博】 | ✅ 官方边界措辞逐字对应（F-043）；博文未夸大为"连续自治" |
| F-042 | OpenViking 核验：volcengine/OpenViking，定位 "Self-evolving Context Database for AI Agents"，37,622 star（2026-09-13），仓库创建于 2026-01-05；huangruiteng 公开 PR 共 169 个（检索时点可见），最早 #3335 于 2026-07-17 | 【官】GitHub API + Search API | ✅ |
| F-043 | 官方边界原文："This measures wall-clock project time, not continuous model execution or unattended production autonomy."；另有一个脱敏的所有者运营 Auto ML 案例同为 200+ 小时（标注非独立可复现、非生产成果、非雇主背书） | 【官】README Evidence 节 | ✅ |
| F-048 | 官方"Used In Real Projects"另列三例独立用户报告：>13h C++ 精度运行；4 天无人值守（用户报告，有定期报告面）；7 个已合并 PR（zilliztech/mfs 公开 issue 可查，1B+ token 规模为用户自述口径）；官方标注这是"当前最强三例"而非全部 | 【官】README Showcase | ✅（归属口径已分层） |

## F. 快速开始（作者实测路径）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-021 | 环境要求：Python 3.11 以上；macOS 与 Linux 直接使用；Windows 需 PowerShell 7 | 【博】 | ✅ requires-python >=3.11；官方安装指南平台分支一致 |
| F-022 | 安装三步：`python3 -m pip install --upgrade loopx` → `loopx workflow-skills --install` → `loopx doctor` | 【博】作者实测 | ✅ 官方 Getting Started 逐字一致（1.0 README 仍为同一组命令） |
| F-023 | 安装后需重启 AI 编程工具，使其重新加载工作流技能（workflow skills） | 【博】作者实测 | ✅ 官方："Restart your agent host after first install so it reloads the workflow skills." |
| F-024 | 进入项目目录接入：`cd /path/to/your-project` → `loopx connect` → `loopx status` | 【博】作者实测 | ✅ 逐字一致 |
| F-025 | 项目未初始化时 connect 会提示状态缺失，按引导建长期目标：`loopx start-goal --guided --project . --goal-text "你的长期目标"` | 【博】作者实测 | ✅ 逐字一致（官方示例为英文 goal-text） |
| F-026 | 此时 `loopx status` 可看到当前目标、待拍板门禁与下一待办；`loopx dashboard` 打开工作台；博文称"没什么要配置的，它没有三方依赖，也没有遥测" | 【博】作者实测 | ⚠️ "无三方依赖/无遥测"对 0.4/0.5 时点成立（PyPI 包零强制运行时依赖、反馈模板声明 no telemetry，F-047）；1.0 起需外部 Node.js 22.18+（F-040/F-041），口径须更新 |
| F-046 | 本地状态文件：官方要求保持 `.loopx/`、`.codex/goals/`、`.local/` 被 gitignore；连接成功标志含 `loopx doctor` 通过、`.loopx/registry.json` 存在、status 显示目标/具体用户门禁/下一 Agent 待办 | 【官】README | ✅ |
| F-047 | 无遥测佐证：官方首跑反馈 issue 模板明确"It is optional, contains no telemetry"，且要求不提交日志/路径/凭证/项目名/目标内容；`loopx first-run-report` 仅本地打印预填链接不发送 | 【官】README | ✅（就反馈渠道而言；与 F-026 博文口径相容） |

## G. 适用场景与作者评价（作者观点层）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-027 | 作者归纳适用场景①：跨数天工程任务（大型重构、持续 issue 清理），上下文与证据不能断 | 【博】作者观点 | 与官方用例表一致（multi-day engineering objectives / issue and PR loops） |
| F-028 | 适用场景②：定时巡检（盯仓库 PR、每日日报），配额闸门防止空烧费用 | 【博】作者观点 | 与官方 recurring heartbeat/monitor work 一致 |
| F-029 | 适用场景③：ML 实验与研究探索，假设、证据、淘汰路线留痕以便复盘 | 【博】作者观点 | 官方有 Auto ML showcase 与 Explore 能力对应 |
| F-030 | 适用场景④：有审批要求的项目（发布、敏感数据改动），必须卡在人工门禁 | 【博】作者观点 | 与官方 owner/safety/publication/private-data gates 一致 |
| F-031 | 适用场景⑤：多 Agent 协作（一个干活一个 review），所有权与交接要说清 | 【博】作者观点 | 官方 peer-agent teams + cross-runtime review demo 对应 |
| F-032 | 作者总评：AI 编程工具一年来的进步大多在单次任务；真实工作常跨周且有变化/等待/拍板/换工具；LoopX 不碰模型能力、只管状态与治理，思路方向很好，"大概率后面要火起来" | 【博】作者观点（含预测） | P2 单源；预测性表述不可固化为事实 |
| F-033 | 作者指出现状不成熟：项目还在 v0.4.x 阶段，不少高级路径可选且默认关闭、有些标实验性；文档量大上手有难度；更适合已重度使用 AI 编程工具者，想当甩手掌柜不适合 | 【博】作者观点 | ⚠️ 版本口径滞后（发文时最新 0.5.4，见 F-039）；"高级路径默认关闭/实验性"与官方 Explore "optional, default-off" 一致 |
| F-034 | 作者给出两个使用前提：高强度使用、常跑长任务；轻度玩家没必要 | 【博】作者观点 | P2 |

## H. 核验补充事实（版本时间线与架构演进）

| 编号 | 事实陈述 | 来源 | 核验 |
|---|---|---|---|
| F-038 | PyPI 版本时间线：0.4.8（08-16）、0.4.9（08-19）、0.5.0（08-19）、0.5.1（08-20）、0.5.2（08-22）、0.5.3（09-01）、0.5.4（09-02 UTC）、1.0.0（09-06）、1.0.1（09-07）、1.0.2（09-09）、1.0.3（09-11）、1.0.4（09-15）、1.0.5（09-15）；requires-python >=3.11；requires_dist 无强制运行时依赖（deepseek-harness-sdk==0.1.5rc1 为 optional extra，另有 test extras） | 【官】pypi.org/pypi/loopx/json | ✅ |
| F-039 | **勘误①（日期/版本表）**：博文 2026-09-03 发布，称"项目还在 v0.4.x 阶段"；当日 PyPI 最新为 0.5.4（0.5 线 08-19 已开始），版本口径滞后约两个小版本；核验时（09-16）最新为 1.0.5 | 【官】 | ⚠️ 非核心声明，正文呈现实测时间线 |
| F-040 | 当前官方 README（main）要求：Python 3.11+ **且 Node.js 22.18.0+**（推荐 Node.js 24 LTS）；Node 运行"托管的、空闲即退出的 TypeScript Effect 内核"，LoopX 自动启动；Windows 原生使用 PowerShell 7，无需 POSIX 兼容层 | 【官】github.com/huangruiteng/loopx README（main） | ✅ |
| F-041 | **勘误②（口径/时效）**：RFC《TypeScript Control-Plane Migration Direction v0》日期 2026-08-15、状态 Accepted（transaction-payoff 阶段进行中，09-13 修订），范围是把控制面核心从 Python 增量替换式迁移到 TypeScript、不维护两套语义实现。博文 09-03 称"纯 Python 写的"反映 0.4/0.5 发货形态（GitHub 语言统计仍以 Python 为主、PyPI 包零运行时依赖），但未捕捉 19 天前已 Accepted 的内核迁移动向；1.0（09-06 起）形态为 Python 分发货 + 托管 TS 内核，需 Node 22.18+ | 【官】RFC + PyPI 元数据 | ⚠️ 演进性事实，正文双口径呈现 |
| F-044 | 官方计费规则原文："Quiet skips, preflight failures, and dry-run previews do not spend."；自动轮次必须先查 quota、经验证 writeback 后才追加 spend；用户门禁阻塞一条车道时安全兜底车道可继续但不得绕过门禁 | 【官】README Operating and Recovery | ✅ |
| F-045 | 官方宿主接入表（比博文列举更广）：Codex App（含 SSH）、Codex CLI、Claude Code（opt-in 适配器 + /loopx、/loop）、Cursor/shell/自定义 runner、DeepSeek Harness（dsh 原生插件或 goal-mode 适配器）、KunlunCode、OpenCode、Pi、ZCode、Antigravity CLI、Kiro CLI；自定义 runner 最小示例 `examples/custom-runtime-minimal-cli-turn-smoke.py` | 【官】README | ✅ |
| F-049 | LoopX 1.0 推出 Personal Agent Workspace：目标/注意力/会话/任务/文件/调度/恢复在本地工作区持久化；`loopx dashboard` 为受支持的浏览器/PWA 路径；1.0 release 另提供原生桌面预览（macOS Apple Silicon 有签名更新、ad-hoc 签名未公证；Windows 预览需手动更新且 CLI 独立安装）；并新增飞书/Lark 异步收件箱与 Manager 群上下文/权限契约 | 【官】README + GitHub releases | ✅ |

## 统计

- 总条目：**49**（F-001 ~ F-049，连续无跳号）
- 博文事实：F-001~F-036（36 条，其中 F-003/F-004/F-005/F-027~F-034 共 11 处陈述标注"作者观点"）
- 核验补充：F-037~F-049（13 条）
- P0 核验：12 项 → 10 ✅ / 2 ⚠️（F-039 版本滞后、F-041 实现形态演进）/ 0 ❌
