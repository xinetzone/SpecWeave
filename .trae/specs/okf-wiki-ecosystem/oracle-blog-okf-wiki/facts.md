# F 编号事实登记（spec 底稿）

> 双份登记之一（bundle 内 `references/article-source.md` 为另一份，两集合须一致：F-001~F-041 连续 41 条）。
> 核验状态：✅ 官方一致 ｜ ⚠️ 单源/口径差异 ｜ 📌 作者观点（非客观事实）。

## A. 博文元信息与叙事（F-001~F-008）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-001 | 标题《太炸裂了！这是哪个大佬发现的 CodeX这个神仙用法，居然能将gpt-plus发挥到极致！》；公众号「Leon学AI」；原创标记；2026-08-30 21:45 发布；IP 属地广东；无独立作者署名；话题标签 #codex教程；正文 1684 字、无信息性图片、URL 均为纯文本 | ✅ 页面元数据 |
| F-002 | 博文开篇叙事：同时使用 Codex 与 ChatGPT Plus 的用户以前"两边各用各的"——Codex 在本地读项目/分析/改代码/跑测试，ChatGPT 只打开网页问几句 | 📌 作者观察 |
| F-003 | 博文描述串联流程四步：Codex 连接电脑读取项目 → 整理真正相关的上下文 → 交给网页版 ChatGPT 做复杂推理 → 拿到方案后 Codex 回本地继续执行 | ✅ 与官方 agents.md "agent gathers context, hands the bundle to a stronger Pro model, gets a second opinion back" 一致（F-034） |
| F-004 | 比喻"GPT 当大脑，Codex 当双手" | 📌 作者观点（比喻） |
| F-005 | 博文称 Codex 不可替代之处是进入本地环境：读项目、搜文件、改代码、执行 Shell、跑测试 | ✅ 与 Codex CLI 本地 agent 能力一致（参见本组 openai-codex 束） |
| F-006 | 博文称复杂任务最吃额度的是前置的理解上下文、反复推理与方案设计 | 📌 作者经验判断（无量化数据） |
| F-007 | 博文给出分工：Codex 负责连接电脑/读取项目/修改代码/执行与验证；ChatGPT Plus 负责复杂分析/重推理/方案规划 | 📌 作者归纳的用法（机制成立，见 F-041） |
| F-008 | 博文称把重推理分流到已付费的 ChatGPT 网页端后，"同样一份 Codex 配额有机会跑更多任务"，甚至"从总觉得不够用变成反而没那么容易跑完" | 📌 作者观点：定性体验，无实测数字，非额度互换（F-019） |

## B. 项目与安装事实（F-009~F-017）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-009 | 博文称开源项目名为 Oracle，作者 steipete，地址 https://github.com/steipete/oracle | ✅ 仓库存在；作者 Peter Steinberger；MIT 许可（npm/everydev） |
| F-010 | 博文概括 Oracle 功能：把 Prompt 与选中的本地文件整理成 Context，交给另一个模型分析，再把结果拿回来 | ✅ 官方 "bundles a prompt with the files you select, sends that context to an AI model … stores the result as a session"（npm README） |
| F-011 | 博文强调 Oracle 支持 Browser Mode，可使用已经登录的 ChatGPT 网页会话，称这是"整套玩法最关键的一环" | ✅ `--engine browser` + manual-login（browser-mode.md）；"最关键"为作者评价 📌 |
| F-012 | 博文给安装命令一：`brew install steipete/tap/oracle` | ✅ install.md 原文（标注 macOS/Linux，博文未写平台限制 → F-025） |
| F-013 | 博文给安装命令二：`npm install -g @steipete/oracle` | ✅ install.md 原文（要求 Node 24+，博文未提 → F-024） |
| F-014 | 博文给首次登录命令：`oracle --engine browser --browser-manual-login --browser-keep-browser -p "HI"` | ✅ 三参数均存在；官方等价示例 `-p "Say hi"` 并显式带 `--model "GPT-5.5 Pro"`（browser-mode.md Manual login mode 节） |
| F-015 | 博文称第一次登录 ChatGPT 后，后面可复用这套浏览器会话 | ✅ 持久化自动化 profile `~/.oracle/browser-profile`，后续运行复用（F-030） |
| F-016 | 博文给 Codex 接入命令：`git clone https://github.com/steipete/oracle.git`；`mkdir -p ~/.codex/skills`；`cp -R oracle/skills/oracle ~/.codex/skills/oracle` | ✅ agents.md「Codex」节原文一致（官方另提 `~/.codex/prompts/oracle.md` slash 包装，F-034） |
| F-017 | 博文要求在项目 AGENTS.md 里告诉 Codex：复杂任务、架构分析、疑难问题优先通过 Oracle 调用网页端 ChatGPT，拿到方案后再继续执行 | ✅ 官方 "30-second wiring" 模式：在 AGENTS.md/CLAUDE.md 写 Oracle 触发场景（卡住/难 bug/架构评审/交叉验证计划） |

## C. 博文结论与边界（F-018~F-021）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-018 | 博文总结闭环："Codex 找上下文 → Oracle 送给 GPT → GPT 思考 → Codex 执行" | ✅ 与官方数据流一致（F-003/F-010） |
| F-019 | 博文自行限定：这不是把 Plus 额度直接变成 Codex Pro 额度，两边不是额度互换；本质是把已付费的网页端推理能力接进 Coding Agent 工作流 | ✅ 自我限定与官方机制一致：browser 路径走订阅会话而非 API 计费（F-041）；账号档位门槛官方未明示（F-041） |
| F-020 | 博文建议同时持有 ChatGPT Plus + Codex、且常觉配额不够或额度耗在复杂分析上的读者安装试用；"GPT 负责想，Codex 负责干，Oracle 负责把它们连起来" | 📌 推荐主张（适用人群画像为作者归纳） |
| F-021 | 页面属性：原创声明、有赞赏入口、无广告/转载声明、无"阅读原文"外链；上下篇均为同号 Codex 题材文章 | ✅ 页面元数据 |

## D. 官方源核验补充（F-022~F-041）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-022 | 官方定位 "Bring a second brain, not a second briefing"；Oracle 同时是 CLI 与 MCP server；npm 包 `@steipete/oracle` 核验时 0.20.2（约 2026-09-15 发布，60 个版本）；官网 askoracle.sh | ✅ npm 官方包页 |
| F-023 | 作者 Peter Steinberger（GitHub: steipete）；MIT 许可证；everydev 第三方索引称项目创建于 2025-11 | ⚠️ 创建时间为第三方单源（everydev.ai），未逐 commit 核验 |
| F-024 | 硬性运行前提：Node.js 24 或更新（博文完全未提，Windows/新机器照做易踩坑） | ✅ install.md frontmatter 与正文 |
| F-025 | 平台边界：Homebrew 包标注 macOS/Linux；浏览器窗口隐藏（--browser-hide-window）目前仅 macOS 用 AppleScript 实现，Linux/Windows 忽略该参数；--copy-profile 仅 macOS/Linux 且需 rsync；Windows 上 app-bound cookie 是推荐 manual-login 的原因之一，且存在 bridge mode | ✅ install.md + browser-mode.md |
| F-026 | 三条执行路径：API（Provider 密钥直连）、Browser（驱动已登录的 ChatGPT/Gemini 浏览器会话）、Render（仅渲染/复制 bundle，不调用模型，无需账号密钥）；无 OPENAI_API_KEY 时默认选 browser | ✅ npm README + browser-mode.md |
| F-027 | API 模式支持六家：OpenAI、Azure OpenAI、Anthropic、Google Gemini、xAI、OpenRouter 及兼容端点（博文只讲 ChatGPT 网页端） | ✅ install.md 密钥表 |
| F-028 | Browser 模式除 ChatGPT 外还支持 Gemini Web（用已登录 Chrome cookie 直连 gemini.google.com，非 ChatGPT 自动化） | ✅ browser-mode.md 三路径之一 |
| F-029 | 每次运行持久化到 `~/.oracle/sessions/<id>/`：日志、bundle、transcript.md、artifacts、浏览器 pid/端口/attach 元数据；`oracle status`、`oracle session <id>` 重连、`oracle restart`、`--followup` 续聊；超时不应盲目重跑而要 reattach | ✅ npm README + browser-mode.md |
| F-030 | manual-login 使用独立持久化自动化 profile（`~/.oracle/browser-profile`，可用 ORACLE_BROWSER_PROFILE_DIR 覆盖），首次在弹出窗口手动登录 chatgpt.com，Oracle 轮询会话生效后继续，后续复用 | ✅ browser-mode.md Manual login mode |
| F-031 | `--browser-keep-browser` 语义：运行结束后保留 Chrome 窗口（省略则关窗但保留磁盘 profile）；官方建议首次登录/调试时加此参数 | ✅ browser-mode.md CLI Options |
| F-032 | 上下文控制：`--file` 接受文件/目录/glob 与 `!` 排除；browser 模式默认约 60k 字符以内内联粘贴进 composer，超出则上传（单个文本/源码文件直传，多个打包；text-only auto 为扁平文本，含二进制或显式 zip 时打 ZIP，ZIP 上限 128 MiB）；单文件默认 1 MB 上限（maxFileSizeBytes/ORACLE_MAX_FILE_SIZE_BYTES）；默认忽略 node_modules/dist/.git 等并尊重 .gitignore | ✅ npm README + browser-mode.md + agents.md |
| F-033 | 官方 Golden path：选最小且包含真相的文件集 → `--dry-run` + `--files-report` 预览解析文件与 token 估算 → browser 跑 Pro 档模型 → detach/超时时 reattach 已存会话而非重复提交 | ✅ 仓库 skills/oracle/SKILL.md（main） |
| F-034 | 官方 Codex 接入：复制 `skills/oracle` 到 `~/.codex/skills/oracle` 后在 AGENTS.md 引用即自动加载；"30-second wiring"建议 AGENTS.md/CLAUDE.md 写两条 bullet（Oracle 用途与触发场景；每个会话首次用前跑一次 `npx -y @steipete/oracle --help`）；可另在 `~/.codex/prompts/oracle.md` 放 slash 包装；Claude Code/Cursor 推荐 MCP 方式（oracle-mcp / .mcp.json / .cursor/mcp.json） | ✅ agents.md |
| F-035 | MCP：提供 `oracle-mcp` stdio server，可挂 Claude Code/Cursor/Codex 等 MCP 客户端；Claude Code 一条 `oracle bridge claude-config --local-browser > .mcp.json` 生成配置；MCP consult 工具带 preset（如 chatgpt-pro-heavy）与 dryRun | ✅ agents.md + npm README |
| F-036 | 模型档位快速演进：核验时官方文档涉及 GPT-5.5/GPT-5.5 Pro/GPT-5.6 Sol/GPT-6 Astra 等 ChatGPT 选择器目标；`--browser-thinking-time light/standard/extended/extra-high/pro/heavy`；Pro 档位"fail closed"（无法确认选中 Pro 就中止，不静默降档）；npm 0.15.2 曾把 gpt-5.6 标签错误 normalize 成 gpt-5.2，需新版本或显式回退模型——博文时代（2026-08-30）的模型口径已过时，实际模型以 `oracle --help --verbose` 与当前 ChatGPT 选择器为准 | ✅ 仓库 skills/oracle/SKILL.md + browser-mode.md |
| F-037 | 并发协作：多个 Agent（Codex/Claude Code）共享同一 manual-login profile 时，Oracle 用 tab slot 协调，默认最多 3 个并发 ChatGPT 标签页，第 4 个排队（--browser-max-concurrent-tabs）；另有 profile 锁与 --browser-reuse-wait | ✅ agents.md + browser-mode.md |
| F-038 | 安全卫生：默认不附加 secrets（.env/密钥/token 需主动排除）；API 模式真实计费，官方建议 pin --model、设 --timeout、审计会话日志，很多人把 API 模式放在显式同意之后、browser 模式放开用；Pro 跑前先 `--dry-run summary --files-report`（token 数≈费用代理） | ✅ agents.md Cost / safety hygiene |
| F-039 | 远程/无头：可 `oracle serve` 托管一台已登录 Chrome（HTTP/SSE + token），客户端用 --remote-host/--remote-token 调用；也可 --remote-chrome 挂已开 remote-debugging 的 Chrome；附件经 CDP base64 传输、单文件 20 MB 上限 | ✅ browser-mode.md Remote Service/Chrome |
| F-040 | 一手文档索引：docs/install.md、docs/browser-mode.md、docs/agents.md、docs/mcp.md、docs/sessions.md、docs/quickstart.md 与官网 askoracle.sh 为命令与行为的裁决依据；本次核验抓取于 2026-09-16（main 分支，HTTP 200） | ✅ 本次核验记录 |
| F-041 | 博文"额度"说法的官方事实校准：browser 路径驱动订阅账号的网页会话、不走按量 API 账单（"without spending API tokens"，everydev 转述 npm 文档口径），但仍估算输入/输出 token 写进会话账；官方文档未声明 Plus/Pro 订阅档位门槛，哪些 ChatGPT 档位可用 Pro/Thinking 模型以 OpenAI 官方规则为准 | ⚠️ "不花 API token"为第三方转述+官方文档隐含（browser-mode 用量记账段）；档位门槛官方三页未明示 |

## 核验总览

- 博文事实 21 条（F-001~F-021），其中 📌 作者观点/比喻/经验 7 条（F-002、F-004、F-006、F-007、F-008、F-011 评价部分、F-020）
- 官方补充 20 条（F-022~F-041），合计 41 条连续编号
- P0 操作型声明（安装 2 条、登录命令、skill 路径、AGENTS.md 接线、会话复用、项目身份）全部 ✅
- 勘误四张清单：0 ❌（无日期/版本硬错、无成效数字、无规模口径、无伪造引语）；博文缺口 5 项（Node 24+、平台、多 Provider、MCP、版本时效）已由 F-024~F-028/F-035/F-036 补齐
