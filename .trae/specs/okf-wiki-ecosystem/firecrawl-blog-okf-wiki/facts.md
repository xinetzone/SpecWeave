---
id: facts
title: Firecrawl 博文事实集（F-001~F-063）
source: https://mp.weixin.qq.com/s/gjio8RIefYti1_p2s__A8w
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-09-16T22:10:00+08:00" }
---

# Firecrawl 博文事实集

> 本文件是 R 阶段唯一合法事实集。F-001~F-034 出自博文（公众号「开源软件社」，2026-09-01），F-035~F-048 为 2026-09-16 第一轮官方源核验补充，F-049~F-063 为同日第二轮独立深核（两路独立核验子代理：GitHub 仓库线 + 官网/公司线）补充，并修订 F-005/F-006/F-007/F-008/F-018/F-037/F-038 七行判定。
> 类型：O=客观事实（博文叙述）｜V=作者观点｜S=厂商自述口径。
> 核验：✅ 官方一致 ｜⚠️ 口径/时效/性质差异 ｜❌ 与官方源冲突（勘误）｜➖ 无需外部核验。
> 双份登记：bundle `references/article-source.md` 保有同编号集合，V 阶段正则比对一致。

## A. 博文元信息（F-001 ~ F-003）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-001 | O | 博文标题《狂揽 17 万 Star！这个开源项目，把整个互联网变成了 AI 的数据库》，栏目「AI 基础设施 2026·08」 | ➖ |
| F-002 | O | 公众号「开源软件社」原创，作者署名开源软件社，2026-09-01 07:50 发布于四川 | ➖ |
| F-003 | O | 推介项目 Firecrawl，仓库 https://github.com/firecrawl/firecrawl（标识 firecrawl/firecrawl），官方站点 firecrawl.dev（文中仓库链接出现 5 次） | ✅ F-035 |

## B. 项目身份与热度（F-004 ~ F-009）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-004 | O | 博文引用项目定位原话「The context API to search, scrape, and interact with the web at scale」——把搜索/抓取/网页交互打包成 API 的开源项目 | ✅ F-036（出处为 repo description） |
| F-005 | O | 2026 年 8 月 Star 数已达 171,711（十七万一千七百一十一颗），仍在涨；标题口径「17 万 Star」 | ⚠️ F-035/F-049（时点数字：171,711 对应约 8/28–8/31 水平，非 8 月初；2026-09-16 实测 181,040，趋势一致） |
| F-006 | S | 覆盖 96% 的网页，含重度 JS 渲染页面（文中出现 3 次） | ⚠️ F-037/F-050（官方 README/首页确有此数，但口径是自建 1,000-URL 基准数据集上的成功率，非"全网 96%"，厂商自述基准） |
| F-007 | S | P95 延迟 3.4 秒，为跨「数百万页面」的实测数字，面向实时 Agent 与动态应用 | ⚠️/❌ F-051（3.4s≈官方 3,387ms 数字属实；但样本同为 1,000-URL 基准，"数百万页面"限定语查无官方出处） |
| F-008 | O | 主仓库用 TypeScript 写成，AGPL-3.0 协议；最近一次提交在 2026-08-24，社区活跃 | TS/许可 ✅ F-035；**提交日 ❌ F-049**（commits API 实证 08-20~08-31 共 94 个提交、09-01 当天 5+ 个，"最近提交停在 08-24"失实；活跃性 ✅） |
| F-009 | O | 输出 LLM 就绪：把网页变成干净 Markdown 与结构化 JSON；Scrape 另支持 HTML、截图 | ✅ F-036 README |

## C. 七大核心端点（F-010 ~ F-017）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-010 | O | 官方 README 把能力拆为七个核心端点，覆盖「找到网页→拿到内容→操作页面」链路：Search/Scrape/Interact/Crawl/Map/BatchScrape/Agent | ✅ F-036（README 核心 3 + More 4，正好 7 个） |
| F-011 | O | Search：像搜索引擎检索全网，返回每条结果的完整页面内容（标题/正文/Markdown），省掉「搜完再爬」两段式 | ✅ F-036 |
| F-012 | O | Scrape：任意 URL 一键转 Markdown/HTML/截图/结构化 JSON，最核心能力 | ✅ F-036 |
| F-013 | O | Interact：抓完页面继续操作（点击/滚动/输入/等待/按键），提示词驱动真实网页（「帮我搜机械键盘」→「点开第一个结果」） | ✅ F-036/F-041 |
| F-014 | O | Crawl：一个请求爬完整站所有 URL，异步任务后台跑，官方 SDK 自动轮询；适合文档站、站点迁移 | ✅ F-036 |
| F-015 | O | Map：瞬间发现网站全部 URL，支持关键词定位（如搜「pricing」返回定价相关页面） | ✅ F-036 |
| F-016 | O | BatchScrape：一次任务异步抓取数千个 URL，统一拿结果 | ✅ F-036 |
| F-017 | O | Agent：无需给 URL，直接描述需求，自己搜索、导航、取回数据 | ✅ F-036 |

## D. 拉开差距的高级能力（F-018 ~ F-024）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-018 | O | Agent 是 /extract 的进化版，博文称官方 README 原话「更快、更可靠，而且不需要你提前知道 URL」；返回附来源链接可溯源 | ⚠️ F-036/F-053（进化版表述 ✅ 逐字一致；但 Agent 标准响应体不含 sources 字段，来源需经 trace artifacts/snapshots、tool_call 结果或 live view 获取；显式 sources 返回仅 /extract 的 showSources 参数） |
| F-019 | O | 结构化输出开箱即用：Pydantic 定义 Schema，Agent 返回符合结构的 JSON | ✅ F-036 |
| F-020 | O | README 示例「找出 Firecrawl 的创始人」结构化返回 Eric Ciarla、Nicolas Camara、Caleb Peffer 三人信息 | ✅ F-040/F-061（README 示例 + About 页双重证实） |
| F-021 | O | 两种模型按需选：博文称「默认的 spark-1-mini 便宜 60%，适合大多数任务；spark-1-pro 留给跨站对比、复杂导航、精度优先的研究场景」 | ⚠️ F-038/F-052（博文与官方 2026-01-14 发布文一致；README legacy 表与之矛盾；现行口径两者均 deprecated、统一路由 spark-2——"二选一"框架已过时） |
| F-022 | O | 媒体解析：网页内嵌 PDF、DOCX 等文件直接解析提取，无需下载后单独处理 | ✅ F-036/F-059（web-hosted 限定，支持格式与计费见 F-059） |
| F-023 | O | 页面操作（Actions）：点击/滚动/输入/等待/按键可在抓取前后编排执行，「给只读爬虫装上能干活的手」 | ✅ F-036（README：click, scroll, write, wait, press） |
| F-024 | S | 脏活累活全包：轮换代理、请求编排、限流控制、JS 拦截内容零配置内置；引 README 原话「no proxy headaches, just clean data」 | ✅ F-036（自述承诺；增强代理轮换为云端专属，见 F-055） |

## E. 适用人群与接入生态（F-025 ~ F-031）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-025 | O | Agent 就绪：一条命令接入任何 AI Agent 或 MCP 客户端；与 Claude Code、Antigravity、OpenCode 等配合 | ✅ F-057（三处官方 quickstart 均实测可达；Claude Code 为官方插件） |
| F-026 | O | 四类用户：AI 应用/Agent 开发者；数据/研究团队（BatchScrape+Map）；产品/内容团队（竞品监控/价格跟踪/内容聚合，有托管版 firecrawl.dev）；个人开发者/自托管爱好者（Self-Hosting 指南+贡献指南） | ✅ F-036 |
| F-027 | O | 九种官方 SDK：Python、Node.js、Go、Java、Elixir、Rust、Ruby、.NET、PHP；异步任务全部自动轮询 | ✅ F-036/F-060（官方 docs/llms.txt 清单正好 9 个） |
| F-028 | O | 安装命令：pip install firecrawl-py；npm install firecrawl；gem install firecrawl-sdk；dotnet add package firecrawl-sdk；composer require firecrawl/firecrawl-sdk。Python 示例：Firecrawl(api_key="fc-YOUR_API_KEY")，app.scrape("https://firecrawl.dev", formats=["markdown"])；app.agent(prompt="Find the founders of Stripe") | ✅ F-036/F-060（逐字一致；为当前 v2 SDK 形态，firecrawl-py 4.43.0；旧 v1 FirecrawlApp/scrape_url 已废弃） |
| F-029 | O | CLI 一条命令：npx -y firecrawl-cli@latest init --all --browser，装完重启 Agent；提供 firecrawl search/scrape/interact 命令 | ✅ F-060（命令逐字一致；npm 包 firecrawl-cli 1.23.3，归属独立仓库 firecrawl/cli，不在主仓库） |
| F-030 | O | MCP 接入：MCP 配置加 firecrawl-mcp 服务端，兼容 MCP 客户端几秒联网 | ✅ F-042/F-060（npm 包名 firecrawl-mcp；仓库为 firecrawl/firecrawl-mcp-server，firecrawl/firecrawl-mcp 路径 404） |
| F-031 | O | 在线体验：官方 playground；注册 firecrawl.dev 拿 API key 即可开始 | ✅ F-046/F-058（playground 可达；免费档 1,000 credits/月） |

## F. 边界、合规与作者评价（F-032 ~ F-034）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-032 | O | 开源版与托管版有差异：云端 firecrawl.dev 含额外功能，自部署需自行搞定代理与基础设施（README 有自托管指南但工作量省不掉）；许可证：主仓 AGPL-3.0，SDK 与部分 UI 组件才是 MIT，闭源商用前须对照 LICENSE | ✅ F-055/F-062（云端专属能力清单与许可证文件位置均已核实） |
| F-033 | O | 合规红线：Firecrawl 默认尊重 robots.txt 指令，官方声明使用者有责任遵守目标网站隐私政策与使用条款 | ✅ F-056（README 原文；绕过开关 ignoreRobotsTxt 为 Enterprise 专属） |
| F-034 | V | 作者观点：①「Star 数可以刷，但能力不会说谎」；②走红信号=模型推理变强后「喂给模型什么数据」成新护城河；③「工具无罪，合规在人心」；④96% 覆盖/3.4 秒/九 SDK 是 17 万 Star 的理由 | ➖（观点；其中④的数字核验见 F-050/F-051） |

## G. 第一轮官方核验补充（F-035 ~ F-048，2026-09-16）

| F编号 | 类型 | 事实 | 信源 |
|-------|------|------|------|
| F-035 | O | GitHub API 快照（查询于 2026-09-16）：stargazers_count **179,337**、forks 9,753、open issues 626、subscribers 461；language=**TypeScript**；license=**AGPL-3.0**；created_at=**2024-04-15**；pushed_at=**2026-09-12**；owner 为 firecrawl Organization；default_branch=main；topics 含 ai-crawler/ai-scraping/web-scraping/llm 等（最新快照见 F-049） | GitHub REST API `/repos/firecrawl/firecrawl` |
| F-036 | O | 博文定位引语真正出处是 GitHub 仓库 About 描述（API description 字段："The context API to search, scrape, and interact with the web at scale. 🔥"）；README 正文粗体句为 "The API to search, scrape, and interact with the web at scale"，紧接 "The web context API..."。博文引语准确，出自 repo description | GitHub API + README |
| F-037 | S | 96% 与 3.4s 出处链：README 链至官方发布文《Introducing Firecrawl v2.5》（Eric Ciarla，**2025-10-30**），技术支撑=自研定制浏览器栈 + 语义索引（当时承载 40% API 调用）。第二轮深核（F-050/F-051）给出官网现行口径：两数同源于 **firecrawl/scrape-content-dataset-v1 自建基准（1,000 URL，2026-01-13 运行）**，96% 为成功率（Puppeteer 79%、cURL 75%）、延迟实测 3,387ms。**属厂商自述基准**，无第三方独立复测 | firecrawl.dev 官方博客 + 官网首页/alternatives |
| F-038 | O | spark 模型口径冲突记录：README「Model Selection (Legacy)」写 **spark-1-pro (default)**、mini "60% cheaper"；官方发布文《Introducing Spark 1 Pro and Spark 1 Mini》（2026-01-14）写 **"Spark 1 Mini (Default)"**——官方页面自相矛盾；两说均已过时（F-052）。博文口径与发布文一致，不应判博文"说反" | 官方 README + 官方发布文 |
| F-039 | O | 现版模型机制：存在 **spark-2**；effort 三档 low/medium/high（简单单站查询/多步多页/深度研究复杂导航），每个 effort 级均运行 spark-2，effort 改推理预算不改模型；model 与 effort 同时发送返回 400 错误（互斥） | 官方 README Effort Selection 段 |
| F-040 | O | 三位创始人姓名：第一轮确认为 README「Agent with Structured Output」示例 JSON 输出（role 均为 Co-founder）；第二轮经官网 About 页独立证实并补职务，见 F-061 | 官方 README + firecrawl.dev/about |
| F-041 | O | REST API v2 基址 `https://api.firecrawl.dev/v2/`：search/scrape/crawl/map/agent；交互端点 `POST /v2/scrape/{scrapeId}/interact`；Interact 返回含 liveViewUrl（https://liveview.firecrawl.dev/...）；Crawl/批量为异步任务返回 job id | 官方 README cURL 示例 |
| F-042 | O | MCP 服务端独立仓库现挂 firecrawl/firecrawl-mcp-server，README 集成段另存旧组织链接 github.com/mendableai/firecrawl-mcp-server；公司主体/融资见 F-054，包版本见 F-060 | README 链接 |
| F-043 | O | Agent Onboarding 机制：面向 AI agent 的自助注册取钥技能 `curl -s https://firecrawl.dev/agent-onboarding/SKILL.md` | 官方 README |
| F-044 | O | Firecrawl Skills Catalog：github.com/firecrawl/skills，安装 `npx skills add firecrawl/skills`；贡献分流——CLI 技能（含 research/developer index）PR 至 firecrawl/cli，build/SDK 技能 PR 至主仓 skills/，workflow 技能 PR 至 firecrawl/firecrawl-workflows；catalog 仓库只读 | 官方 README Integrations 段 |
| F-045 | O | 平台集成：Lovable、Zapier、n8n；完整集成清单 firecrawl.dev/integrations | 官方 README |
| F-046 | O | 官方资源：文档 docs.firecrawl.dev、API Reference（docs.firecrawl.dev/api-reference/introduction）、Playground（firecrawl.dev/playground）、Changelog（firecrawl.dev/changelog） | 官方 README Resources 段 |
| F-047 | O | 媒体解析能力的开源栈：官方博客列有 AnyDoc 与 pdf-inspector（Firecrawl's open-source document parsing stack）。第二轮补完整格式/计费/限定词见 F-059 | firecrawl.dev 官方博客索引 |
| F-048 | O | 竞品语境：README Agent 示例以 "Compare enterprise features across Firecrawl, Apify, and ScrapingBee" 作为 high effort 典型用例（Apify、ScrapingBee 为官方文档自举的同业对照） | 官方 README |

## H. 第二轮独立深核补充（F-049 ~ F-063，2026-09-16）

> 两路独立核验子代理（GitHub 仓库线 + 官网/公司线），以 GitHub REST API/commits API、main 分支 README（940 行）、npm/PyPI registry、firecrawl.dev 官网与文档、SEC Form D 为源。

| F编号 | 类型 | 事实 | 信源 |
|-------|------|------|------|
| F-049 | O | Star 与活跃度时点证据：2026-09-16 API 实测 stargazers_count **181,040**（另一缓存副本 179,337@09-12）；star-history 曲线反推 08-01≈158.3k、**08-24≈169.9k、09-01≈173.9k**，故博文 171,711 对应约 **8/28–8/31**。commits API 实证：08-20~08-31 共 **94 个提交**、**2026-09-01 当天至少 5 个提交**（如 "(feat/agent) Spark 2 threads (#4490)" 23:37Z）、08-31 当天仍有提交；核验当日最新为 2026-09-16 `feat(api): add Bigtable operational job stores (#4645)` | GitHub REST API + commits API + star-history |
| F-050 | S | 96% 现行官方口径（首页逐字）："96% coverage on our **1,000-URL firecrawl/scrape-content-dataset-v1** benchmark, run **Jan 13, 2026**"；alternatives 对比页：Coverage（成功率）96% vs Puppeteer 79%、cURL 75%。即厂商**自建千 URL 基准数据集上的成功率**，不是对全网的覆盖率承诺 | firecrawl.dev 首页 + /alternatives#measured-performance |
| F-051 | S | P95 现行官方口径（首页逐字）："**P95 latency of 3,387 ms** on the same 1,000-URL benchmark, run Jan 13, 2026"。3.4s 为 3,387ms 约数；博文"跨数百万页面实测"**查无任何官方出处**（"5B+ requests served" 为服务总量口径，不能当作测试样本） | firecrawl.dev 首页 + /alternatives |
| F-052 | O | 现行模型事实：docs.firecrawl.dev/features/agent 原文 "**Spark 1 models are deprecated. The Spark 1 model names remain accepted for backwards compatibility, but requests that use them route to spark-2.**"；现默认 **spark-2**（"cheaper and faster than the earlier Spark 1 models, at comparable accuracy"）。英文 /features/models 页仍残留 spark-1 旧表（官方文档自身新旧不一致，勿引该页当现状） | docs.firecrawl.dev/features/agent + /features/models |
| F-053 | O | Agent 可溯源机制精确口径：标准完成响应仅含 success/status/data/expiresAt/creditsUsed，**无顶层 sources/citations**；来源经执行 trace 的 `artifact.updated` 事件 + `GET /agent/{jobId}/snapshots/{snapshotId}`（json/markdown/html）、`tool_call.finished` result、live view 浏览器会话获取；官方原话 "Artifacts are the run's output, not a page-by-page archive"。显式 sources 字段目前仅 **/extract 的 `showSources=true`**；/extract 被标 "Use `/agent` instead" 的**软弃用建议**（successor），但 POST /v2/extract 在 API Reference 仍正常文档化、开源/云端均提供，未正式下线 | docs.firecrawl.dev/features/agent + /api-reference/endpoint/extract + 选型指南 |
| F-054 | O | 公司主体与融资：服务条款原文 "**SideGuide Technologies, Inc. d/b/a Firecrawl**, a Delaware Corporation"（总部 San Francisco；Mendable 为团队前序产品名，npm scope 仍为 @mendable）；2022 年 Y Combinator（YC S22）启动；**2025-08-19 宣布 1,450 万美元 A 轮**，Nexus Venture Partners 领投，YC 追投，Zapier、Tobi Lütke、Abhinav Asthana（Postman CEO）、Matt McClure（Mux 创始人）参投；About 页写总融资 **$16.2M**；SEC Form D（CIK 2072161，2026-09-14）显示已售优先股 **$82,063,463**（7 名投资者，未标轮次/估值），About 页尚未更新 | firecrawl.dev/terms-of-service + /about + /blog/firecrawl-v2-series-a-announcement + SEC EDGAR |
| F-055 | O | 开源 vs 云端能力边界（官方对比表）：开源版含 Scrape/Crawl/Map/Search/Batch scrape/Extract/JSON mode/LLM-ready formats/Change tracking/SDKs；**仅云端有：Agent、Browser sandbox、Actions、Enhanced proxies、Proxy rotations、Dashboard、Enterprise features**。自托管 LLM 抽取需**自备 OpenAI 兼容 API 或 Ollama**；Fire-engine（高级反爬）需另行部署且不含在内；截图/页面动作默认栈不支持 | docs.firecrawl.dev/contributing/open-source-or-cloud + self-host |
| F-056 | O | robots.txt 精确口径：README "By default, Firecrawl respects robots.txt directives. … It is the sole responsibility of end users to respect websites' policies…"；Crawl 文档参数表 "robots.txt is respected unless `ignoreRobotsTxt` is enabled (**Enterprise only**)"，默认 false；抓取时并读 FirecrawlAgent user-agent 与 `*` 规则 | GitHub README + docs /features/crawl + /advanced-scraping-guide |
| F-057 | O | 博文列举的三个客户端集成均经官方页面证实：Claude Code 有独立 quickstart（托管 MCP `https://mcp.firecrawl.dev/v2/mcp-oauth`）且为**官方 Claude 插件**（`claude plugin install firecrawl@claude-plugins-official`）；Antigravity quickstart（MCP Web Search & Scrape in Google Antigravity）；OpenCode quickstart 存在（CLI 安装注释也列 "Claude Code, Codex, OpenCode"），三页均 HTTP 200 | docs.firecrawl.dev/quickstarts/{claude-code,antigravity,opencode} + /integrations/claude-code |
| F-058 | O | 免费额度与 keyless：定价页 Free Plan **1,000 credits/月、$0、无需卡**（约 500 searches 或 1,000 pages scraped，2 并发低速率）；选型指南载 Agent **5 free runs/day**；SDK/MCP 另支持 keyless（无密钥）访问 Search/Scrape/Parse 作为兜底；Playground（firecrawl.dev/playground）可直接试、无需代码 | firecrawl.dev/pricing + /playground + docs 选型指南 |
| F-059 | O | 媒体解析完整口径：官方支持 **PDF、DOCX、DOC、ODT、RTF、XLSX、XLS、HTML** 文件 → "clean, layout-aware Markdown"；scrape/crawl 可用 `parsers: ["pdf"]`，**PDF 解析 1 credit/页**；README 表述带 **web-hosted（网页托管）** 限定词；开源解析栈为 AnyDoc + pdf-inspector（F-047） | firecrawl.dev 首页 + /use-cases/ai-mcps + docs /features/crawl |
| F-060 | O | 包与仓库实测（2026-09-16）：PyPI **firecrawl-py 4.43.0**（v2 API，`AsyncFirecrawl` 并存；旧 v1 `FirecrawlApp`/`scrape_url` 已废弃，博文示例为当前 v2 形态）；npm **firecrawl 4.40.0**；npm **firecrawl-mcp 3.24.0**（仓库 **firecrawl/firecrawl-mcp-server**，约 7.5k stars；firecrawl/firecrawl-mcp 路径 404；mendableai 旧名为重定向）；npm **firecrawl-cli 1.23.3**（bin 名 firecrawl，归属独立仓库 **firecrawl/cli**，约 631 stars，不在主仓库）；gem/dotnet **firecrawl-sdk**、composer **firecrawl/firecrawl-sdk** 一致；Go=monorepo apps/go-sdk；Java=jitpack `com.github.firecrawl:firecrawl-java-sdk:2.0`；Elixir=hex `{:firecrawl,"~>1.0"}`；Rust=crates.io `firecrawl = "2"` | GitHub API + npm/PyPI registry + 官方 docs/llms.txt |
| F-061 | O | 三创始人官网 About 页证实与职务：**Caleb Peffer — Co-Founder & CEO**；**Eric Ciarla — Co-Founder & Chief Growth Officer**；**Nicolas Silberstein Camara — Co-Founder & CTO**（常简写 Nicolas Camara，X @nickscamara_）；官网未列第四位联合创始人；2026 Form D 由 Caleb Peffer 签署 | firecrawl.dev/about + SEC Form D |
| F-062 | O | 许可证文件实测：主仓根目录许可证文件名为普通 **`LICENSE`**（AGPL-3.0 全文，约 35KB；无 LICENSE.md/LICENSE-AGPL 命名）；MIT 许可证实际位于 `apps/python-sdk/LICENSE`、`apps/js-sdk/LICENSE`、`apps/elixir-sdk/LICENSE`、`apps/ruby-sdk/LICENSE`、`apps/ui/ingestion-ui/LICENSE`（均首行 "MIT License"）；未发现自托管商用在 AGPL 之外的附加授权限制，商业边界实际通过 F-055 的云端专属能力实现 | GitHub git tree + README license 段 + docs |
| F-063 | O | 自托管运维依赖栈：PostgreSQL（默认队列）、Redis、RabbitMQ、Playwright（可选 FoundationDB）；这些为部署者自管的运维依赖（其自身许可需自行留意），非 Firecrawl 附加授权条款 | docs.firecrawl.dev/contributing/self-host |

## 核验统计

- 两轮 P0/P1 核验共 **26 项声明簇**：**✅ 20 / ⚠️ 5 / ❌ 2**（❌=F-008"最近提交 2026-08-24"失实、F-007"数百万页面"样本限定查无出处；⚠️=F-005 Star 时点、F-006 覆盖率口径、F-021/F-038 spark 默认模型口径冲突且全系已弃用、F-018 Agent 来源返回机制、F-007 延迟基准口径）。
- 关键修订：第一轮 F-038 曾判博文 ❌（默认模型说反），第二轮证实博文与官方 2026-01-14 发布文一致（"Mini (Default)"），系 README legacy 表与发布文自相矛盾，且 spark-1 全系已弃用路由 spark-2，改判 ⚠️；第一轮 F-008"提交日无法回溯"经 commits API 升级为 ❌ 实证勘误。
- 两处 ❌ 均为**非核心细节声明**：文章核心声明（Firecrawl 是 17 万 Star 开源 web context API、七端点能力、九 SDK/CLI/MCP 接入、AGPL+MIT 双许可）全部 ✅，故 bundle `status: stable`，勘误在 verification.md 与正文完整落实，不置 flagged。
- 信源距离：公众号编译性推介（第三方媒体，非厂商账号）→ 事实几乎全部转译自官方 README/repo 元数据 → 已用 GitHub REST/commits API、main 分支 README、官网首页/文档/pricing/alternatives、官方博客、SEC EDGAR 两源以上交叉核验；96%/3.4s/60% 等数字均标注"厂商自述基准"及时点。
