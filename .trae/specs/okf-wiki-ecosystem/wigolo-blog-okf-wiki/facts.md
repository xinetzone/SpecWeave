---
okf_version: "0.2"
type: facts
title: "wigolo 博文事实采集清单"
source: "https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w"
blog: { account: "GHub开源甄选", author: "小涛", published: "2026-09-15T07:01:00+08:00", words: 3246 }
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-09-16T20:40:00+08:00" }
---

# 事实采集清单（F 编号）

> R 阶段唯一合法事实集。类型：`O`=客观事实，`V`=作者观点/体验，`S`=厂商自述（经博文转述）。
> 信源距离：博文一手 / 第三方综述 / 厂商自述 / 官方核验。核验级：P0 必核验 / P1 选核验 / P2 可单源。
> 核验结论：✅ 与官方一致 ｜ ⚠️ 口径/时效差异（见 verification.md 勘误）｜ ➖ 无需外部核验。
> F-001~F-033 来自博文（F-033 记录博文自身笔误）；F-034~F-055 为 2026-09-16 官方核验补充事实。

## A. 博文元信息

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-001 | O | 博文标题：《零API Key、零费用！这个GitHub开源神器让AI Agent彻底告别"搜索付费焦虑"》 | 博文一手 | P2 | ➖ |
| F-002 | O | 发布公众号「GHub开源甄选」，作者「小涛」，发布时间 2026-09-15 07:01，标记原创，发布地广东，正文 3246 字（innerText 实测） | 博文一手 | P2 | ➖ |
| F-003 | O | 博文推介项目 wigolo，给出仓库地址 https://github.com/KnockOutEZ/wigolo | 博文一手 | P0 | ✅ F-034 |

## B. 项目身份与热度（博文口径）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-004 | O | 博文将 wigolo 定位为给 AI Agent 用的「本地搜索引擎」「本地优先的 Web 情报层」；Agent 通过 MCP（Model Context Protocol）协议调用 | 第三方综述 | P1 | ✅ F-036/F-037 |
| F-005 | O | 博文称项目「从四月份开源到现在」，已获「三千多颗 Star」，并「在 GitHub Trending 上挂了好几天」 | 第三方综述 | P0 | 月份✅ F-034；Star⚠️ F-035；Trending⚠️ F-053 |
| F-006 | O | 博文称作者为开发者 KnockOutEZ，许可证 AGPL-3.0，「完全开源」 | 第三方综述 | P0 | ✅ F-034/F-037（KnockOutEZ 为个人账号） |

## C. 能力与设计（博文口径）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-007 | O | 博文称 wigolo 通过 MCP 为 Agent 提供：搜索网页、抓取内容、爬取整站、提取结构化数据、本地缓存、相似页面查找、深度研究、自动采集、页面变更监控，「一共十个工具」 | 第三方综述 | P0 | ✅ F-041（正文列举 9 个能力名，diff/watch 合为「页面变更监控」） |
| F-008 | O | 博文称搜索使用 18 个公共搜索引擎的直接适配器；抓取与提取在本地运行；重排序与嵌入模型在本机运行 | 第三方综述 | P0 | ✅ F-042 |
| F-009 | O | 博文称仅 research 与 agent 两个需要写长文总结的功能建议配免费 Gemini Key；不配则返回原始证据由调用方 Agent 自行整理 | 第三方综述 | P0 | ✅ 补正 F-040（另有 search format=answer 也走 LLM） |
| F-010 | O | 博文称所有数据存于 `~/.wigolo/`（查询记录、缓存网页、向量索引）；除非用户主动配置 LLM，否则没有数据传至第三方服务器 | 第三方综述 | P0 | ✅ F-037/F-046 |
| F-011 | S | 博文转述作者对比测试：同一问题同时跑 Claude 内置搜索、wigolo、Tavily、Exa 四个工具，四者均找到正确答案；wigolo 是唯一返回「逐字摘录 + 字节级来源定位 + 可解释评分」的工具，弱结果直接标为 junk | 厂商自述（经博文转述） | P0 | ⚠️ F-044（官方 README Benchmark 自述演示，非独立评测） |
| F-012 | O | 博文称网站被反爬机制挡住时，wigolo 标注 `blocked_by_challenge`，不返回乱码假装成功；缓存过期也会显式告知 | 第三方综述 | P1 | ✅ F-043 |
| F-013 | V | 博文将上述行为归纳为「诚实输出」特点 | 作者观点 | P2 | ➖ |
| F-014 | V | 博文开篇以 Tavily、Exa 付费搜索 API 费用与重复搜索重复计费的痛点作为引入（"比咖啡钱还贵"为修辞） | 作者观点 | P2 | ➖ |

## D. 安装与命令（博文口径）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-015 | O | 博文称前置要求 Node.js 20 或更高版本，提及「现在 LTS 版本都到 22」 | 第三方综述 | P0 | ✅ F-038（Node ≥20） |
| F-016 | O | 博文给第一步命令 `npx wigolo init --agents=claude-code`，称自动下载浏览器引擎与本地模型，约需 1.5GB 空间 | 第三方综述 | P0 | ✅ F-038 |
| F-017 | O | 博文称支持一键接入 Claude Code、Cursor、Codex、Gemini CLI、VS Code、Windsurf、Zed 等主流 AI 编程工具 | 第三方综述 | P1 | ✅ F-039（官方为 9 目标，博文少列 OpenCode、Antigravity） |
| F-018 | O | 博文给第二步 `npx wigolo doctor`，显示全绿即就绪；随后可在 Claude Code 中直接提问触发带引用的搜索回答 | 第三方综述 | P0 | ✅ F-038/F-054 |
| F-019 | O | 博文给终端直用示例 `npx wigolo search "local-first AI agent" --limit=3`，称返回含每篇文章摘录、来源引擎、评分及失败引擎；同一问题再搜因本地缓存明显更快 | 第三方综述 | P0 | ⚠️ F-051（headless 文档签名为 `--max-results`，`--limit` 为 shell 模式参数） |
| F-020 | O | 博文称 `wigolo serve` 启动 REST API，默认监听 127.0.0.1:3333 | 第三方综述 | P0 | ✅ F-049 |
| F-021 | O | 博文给 curl 示例：`POST http://127.0.0.1:3333/v1/search`，header `Content-Type: application/json`，body `{"query":"local-first software","max_results":5}`；称十个工具均支持 REST 调用并提供 OpenAPI 3.1 文档；部署 VPS/内网时配 token 访问 | 第三方综述 | P0 | ✅ F-049 |
| F-022 | O | 博文给两条 Docker 命令：①标准 MCP 模式 `docker run -i --rm -v wigolo-data:/data ghcr.io/knockoutez/wigolo`；②HTTP 模式 `docker run -p 3333:3333 -v wigolo-data:/data -e WIGOLO_API_TOKEN=<token> ghcr.io/knockoutez/wigolo serve --host 0.0.0.0` | 第三方综述 | P0 | ✅ F-046/F-048 |
| F-023 | O | 博文称 slim 镜像懒加载模型，`:full` 标签预装浏览器引擎、启动更快 | 第三方综述 | P0 | slim✅ F-046；:full⚠️ F-047 |
| F-024 | O | 博文给 LLM 配置：`export WIGOLO_LLM_PROVIDER=gemini`、`export GEMINI_API_KEY=<key>`，申请地址 aistudio.google.com/apikey，称免费额度够用 | 第三方综述 | P0 | ✅ F-050 |
| F-025 | O | 博文称也可配置 Anthropic、OpenAI、Groq，或完全本地运行 Ollama | 第三方综述 | P0 | ✅ F-050 |
| F-026 | O | 博文称配置 LLM 后 research 可自动分解问题、并行搜索子查询、抓取来源、合成带引用的报告 | 第三方综述 | P1 | ✅ F-041 |

## E. 使用技巧与评价（博文口径）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-027 | V | 技巧一：传数组做并行搜索（`["a","b","c"]`），多引擎同时扇出查询，覆盖面更大 | 作者体验 | P1 | ✅ F-042（query array 并行扇出） |
| F-028 | V | 技巧二：重要问题用 `search_depth: deep`；默认标准深度，deep 召回率明显更高 | 作者体验 | P1 | ✅ F-051（`--search-depth` 参数存在，取值以 `--help` 为准） |
| F-029 | V | 技巧三：用 `include_domains` 锁定官方文档（示例 Next.js 限定 `["nextjs.org"]`），结果不受 SEO 垃圾页污染 | 作者体验 | P1 | ✅ F-051 |
| F-030 | V | 技巧四：缓存即知识库——常查文档首搜后进入本地缓存，离线可查、毫秒级响应；`wigolo cache` 可做语义检索，相当于私有搜索引擎 | 作者体验 | P1 | ✅ F-043/F-054 |
| F-031 | V | 博文结尾评价：wigolo 最打动人的是务实，解决「让 AI Agent 免费、私有、高效访问网页」的痛点；称其为 Claude Code/Cursor 用户与自建 Agent 工作流「目前成本最低的接入方式，字面意义上的零成本」 | 作者观点 | P2 | ➖（零成本口径见 F-040/F-045：核心工具 $0/query，LLM 合成可选） |
| F-032 | O | 博文称项目处于 Public Beta 阶段、更新频繁、作者在 X 上活跃，可通过 GitHub issue 反馈 | 第三方综述 | P1 | ✅ F-037/F-053 |
| F-033 | O | 博文自身文字记录：结尾段将 18 写作中英混杂「eighteen个搜索引擎」；仓库链接段拼写为「guthub地址」 | 博文一手 | P2 | ➖（笔误，bundle 正文不沿用） |

## F. 官方核验补充事实（2026-09-16，GitHub API + main 分支官方文档）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-034 | O | GitHub API 实测：仓库 KnockOutEZ/wigolo 真实存在，id 1208642537，创建时间 **2026-04-12T15:04:11Z**，默认分支 main，主语言 TypeScript，owner 类型为 User（个人账号 id 70368615） | 官方核验 | P0 | ✅ |
| F-035 | O | GitHub API 时点快照（2026-09-16T01:46Z）：stargazers_count **5268**、forks 419、open_issues 59、subscribers 21；最近 push 2026-09-15T10:02Z（活跃维护） | 官方核验 | P0 | ✅（动态数字，引用须带时点） |
| F-036 | O | 官方仓库描述："The go-to web for your AI coding agent — local-first search, fetch, crawl & research over MCP. No API keys, no cloud, $0/query. Public beta."；主页 https://knockoutez.github.io/wigolo/；npm 包名 `wigolo` | 官方核验 | P0 | ✅ |
| F-037 | O | README 徽章确认：AGPL-3.0 许可证、status=public beta、Node ≥20、MCP server、npm 已发布、CI 正常 | 官方核验 | P0 | ✅（GitHub API license 字段为 NOASSERTION，以作者徽章与 LICENSE 文件为准） |
| F-038 | O | README Quickstart：`npx wigolo init`（仅本地引擎）与 `npx wigolo init --agents=claude-code,cursor`（同时接入）；要求 Node ≥20、约 1.5GB 可用磁盘，支持 macOS/Linux/Windows；init 默认无人值守、逐组件报告，`--no-warmup` 可延迟下载 | 官方核验 | P0 | ✅ |
| F-039 | O | `--agents` 官方支持 9 个接入目标：claude-code、cursor、codex、gemini-cli、opencode、vscode、windsurf、zed、antigravity（逗号分隔）；其他 MCP 客户端用 `npx -y wigolo` 自行注册 | 官方核验 | P1 | ✅ |
| F-040 | O | 免 API Key 工具明确为 **6 个**：search、fetch、crawl、extract、cache、find-similar；research、agent 以及 `search format=answer` 需 LLM 合成，未配置时返回 raw brief 与 evidence 由宿主 Agent 组装 | 官方核验 | P0 | ✅（博文 F-009 「两个」口径补正） |
| F-041 | O | README Tools 表确认 **10 个工具**：search（多引擎搜索）、fetch（单页抓取，反爬自动升级无头浏览器）、crawl（BFS/DFS/sitemap/map 多页爬取）、extract（表格/JSON-LD/命名 schema/自定义 JSON Schema 提取）、cache（关键词与混合语义检索）、find_similar（关键词+语义+实时网三路融合）、research（分解→扇出→抓取→带引用合成）、agent（plan→search→fetch→extract→synthesize 自主采集循环）、diff、watch（页面变更检测与 webhook 推送） | 官方核验 | P0 | ✅ |
| F-042 | O | search 为 **18 个直接适配器**的多引擎搜索，含 rank fusion、ML 重排序与逐结果可解释评分；支持 query 数组并行扇出、域名限定、时间范围、精确短语匹配、图片结果 | 官方核验 | P0 | ✅ |
| F-043 | O | 证据响应结构：每条结果含 title/url/excerpt、`citation_id`、`source_span: {start,end}`（字节偏移）、`evidence_score: {final,semantic,lexical,engine_consensus}`、`freshness_signal`；弱结果由内置评分器标 junk；失败引擎、陈旧缓存、降级后端与截断均在结果中显式标注；反爬页返回 `blocked_by_challenge` 标签失败 | 官方核验 | P0 | ✅ |
| F-044 | S | README Benchmark 段（厂商自述）：在单个 **Claude Fable 5** 会话中对内置 WebSearch、wigolo、Tavily、Exa 同题实测，四者收敛到同一答案与同一顶级来源；wigolo 唯一返回字节锚定逐字摘录、评分分解与逐引擎实时遥测，其评分器将 2 条弱结果标 junk；对比表标注「Feature standing as of July 2026」。属官方自述演示，非第三方独立评测 | 厂商自述 | P0 | ⚠️ 已标注性质 |
| F-045 | O | 官方对比表（2026-07 口径）：wigolo 无 API key、$0/query；Firecrawl/Exa/Tavily 需 key 且按量计费；「字节锚定逐字摘录」「可解释评分分解」「持久本地记忆（离线即时复查）」「查询数据留在本机」四项仅 wigolo 列为 ✅ | 官方核验 | P1 | ✅ |
| F-046 | O | installation.md：发布镜像 `ghcr.io/knockoutez/wigolo` 为 slim 变体，浏览器引擎二进制与本地模型首次使用时下载至 `/data` 命名卷；stdio 命令 `docker run -i --rm -v wigolo-data:/data ghcr.io/knockoutez/wigolo` 与博文逐字一致；卷内持久化缓存、模型、引擎与加密密钥 | 官方核验 | P0 | ✅ |
| F-047 | O | `full` 在官方文档中为仓库 Dockerfile 的构建目标（`docker build --target full -t wigolo:full .`，构建时预装浏览器引擎）；文档未确认 ghcr 已发布 `:full` 预构建标签 | 官方核验 | P0 | ⚠️ 博文「:full 标签」为不严谨表述 |
| F-048 | O | HTTP 守护进程绑定非回环地址时 **fail-closed**：未设置 `WIGOLO_API_TOKEN`（或未显式 `--allow-unauthenticated`）则拒绝启动；官方提供 `packaging/compose.serve.yml` 用于 HTTP 部署 | 官方核验 | P0 | ✅ |
| F-049 | O | REST：`wigolo serve` 默认 127.0.0.1:3333；`POST /v1/{tool}` 覆盖全部 10 工具；`GET /openapi.json` 提供 OpenAPI 3.1 契约；同一端口还提供 `/mcp` 与 `/sse` 远程 MCP；`serve` 参数为 `[--port N] [--host H] [--allow-unauthenticated]` | 官方核验 | P0 | ✅ |
| F-050 | O | LLM 配置：`WIGOLO_LLM_PROVIDER=gemini` + `GEMINI_API_KEY`（aistudio.google.com/apikey 免费层）；provider 支持 anthropic/openai/groq，本地可用 ollama 或任意 OpenAI 兼容端点；cli.md 另载 LLM 密钥统一从 `WIGOLO_LLM_API_KEY` 环境变量读取（不从命令行 flag 读取） | 官方核验 | P0 | ✅ |
| F-051 | O | cli.md 参数口径：headless 一次性命令 search 签名为 `wigolo search <query> [--max-results=N] [--include-domains=a,b] [--time-range=...] [--exact-match] [--search-depth=...]`；`wigolo shell` 交互模式中 search 别名参数为 `[--limit=N] [--domains=a,b]` | 官方核验 | P0 | ⚠️ 博文 npx headless 示例的 `--limit` 与文档签名存在口径差异 |
| F-052 | O | 官方提供两套 SDK：TypeScript（`npm install wigolo-sdk`，零依赖，含 local 嵌入模式自动复用/拉起守护进程）与 Python（`pip install wigolo`，仅标准库，支持同步与异步） | 官方核验 | P1 | ✅ |
| F-053 | O | 作者/社区信息：GitHub 账号 KnockOutEZ；作者 X 账号 @yourtowhid；联系邮箱 ktowhid201@gmail.com；有 Discord 社区；README 挂载 Trendshift 徽章（trendshift.io/repositories/79424）。Trendshift 与 GitHub Trending 是两个不同产品，博文「GitHub Trending 挂了好几天」无法由官方材料直接证实 | 官方核验 | P0 | ⚠️ |
| F-054 | O | cli.md 其余命令：`doctor [--fix]`（诊断并可修复）、`verify`（真实网络端到端冒烟）、`config --uninstall`（移除集成但保留 `~/.wigolo`，完整清理需 `rm -rf ~/.wigolo`）、`shell`（带 NDJSON 管道的交互 REPL）；watch 定时检查仅在 daemon 或 MCP 会话存活期间运行 | 官方核验 | P1 | ✅ |
| F-055 | O | README 赞助段：赞助商 TestMu AI（原 LambdaTest）；项目声明「free for all and meant to stay that way」，接受赞助与捐赠；Homebrew、单文件二进制、托管安装脚本在仓库 packaging/ 有源码但尚未发布可用制品 | 官方核验 | P2 | ✅ |

## G1 自检

- 事实总数：55（博文 33 + 核验补充 22），编号 F-001~F-055 连续无跳号
- 因果/判断词：事实栏纯客观陈述；评价与因果表述均标 V/S 并归入观点/自述
- 数字/命令/版本：18、10、6、1.5GB、3333、Node 20、5268、2026-04-12 等均带 F 出处与时点
- 核验记录：✅ 47 项次、⚠️ 5 个 F 编号（F-005/F-011/F-019/F-023/F-047/F-051/F-053 中 F-005 含 2 子项）、❌ 0
