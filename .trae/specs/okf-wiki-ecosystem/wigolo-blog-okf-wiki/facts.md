# wigolo 博文转化事实集（R 阶段产出）

> 来源博文：微信公众号「极客之家」《wigolo：零 API Key、零费用的本地优先 Agent 网络搜索工具》（标题依内容概括，确切标题/日期未从页面元数据检出）
> 博文 URL：https://mp.weixin.qq.com/s/RiMdKJGEFY8AmNQvDXWtyA?from=industrynews&color_scheme=light#rd
> 核验基准：GitHub 官方仓库 https://github.com/KnockOutEZ/wigolo （README / LICENSE / llms.txt / docs/* 于 2026-09-02 抓取）
> 事实总数：52 条（博文事实 F-001~F-033；核验补充 F-034~F-052）
> P0 核验：0 ❌ / 2 ⚠️ 口径标注 / 其余 ✅

## A. 博文事实（F-001~F-033）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-001 | 博文为公众号「极客之家」发布的开源项目推荐文，主题为本地优先 AI Agent 网页能力工具 wigolo；确切发布日期未检出，内容时点约 2026-07 下旬（文中引官方对比表口径 "as of July 2026"，同题第三方报道集中在 2026-07-16~07-21） | ⚠️ 元数据缺口 |
| F-002 | Firecrawl 这类云端抓取 API 要注册账号、拿 API Key，免费额度有限（博文口径：一个月送一千页），超了按量收费 | ⚠️ 额度数字为厂商政策，未独立核验，标博文口径 |
| F-003 | wigolo 在本地跑搜索、抓取、爬取，核心功能不要 API Key、不按次收费 | ✅ README/llms.txt |
| F-004 | wigolo 定位：给 AI Agent 提供网页能力的工具，以 MCP Server 形式接入 Claude Code / Cursor / Codex / Gemini CLI 等 | ✅ |
| F-005 | 不玩 MCP 也能用：提供 REST API + TypeScript/Python SDK，可接 n8n 等自动化工具 | ✅ |
| F-006 | 本地优先：缓存、向量模型、配置全在本地 `~/.wigolo/` 目录；查询记录不出机器，除非主动接外部模型做报告汇总 | ✅ |
| F-007 | AGPL 开源；作者个人维护（博文："一个人在维护"）；公开 beta 阶段；背后有七千多个测试用例在跑 | ✅（AGPL-3.0-only；维护者 Towhid Khan @yourtowhid；~7,600 自动化测试，官方 FAQ；另 README 显示赞助商 TestMu AI） |
| F-008 | 内置 10 个小工具：search / fetch / crawl / extract / cache / find_similar / research / agent / diff / watch | ✅ docs/tools.md 十工具清单一致 |
| F-009 | search：一次并行查 18 个公开搜索引擎，结果融合排序 + 本地模型重排；关键词支持传数组，一次调用同时查多个问题 | ✅（18 引擎适配器表；query 支持数组扇出） |
| F-010 | 搜索结果带原文摘录、源页面位置、引用 ID、置信度打分；质量差的结果评分器会标出来；没响应的引擎在返回里写明，不静默丢 | ✅（citation_id / source_span / evidence_score / engine_warnings） |
| F-011 | fetch：普通 HTTP 先行，遇到反爬/JS 渲染页面自动升级无头浏览器；输出干净 Markdown + 元数据 + 链接 | ✅（三级路由 plain HTTP → TLS-impersonation → browser engine） |
| F-012 | fetch 支持 PDF、登录态会话、页面动作（点击/输入/滚动/截图） | ✅ |
| F-013 | 验证墙过不去时标记 blocked_by_challenge，不把验证页当正文返回 | ✅ troubleshooting.md |
| F-014 | crawl：多页爬取，支持 BFS/DFS/sitemap 模式，默认遵守 robots.txt、按域名限速、过滤样板内容 | ✅ |
| F-015 | extract：抽结构化数据，表格/JSON-LD/文章/商品等常见格式可直接识别，支持自定义 JSON Schema | ✅ |
| F-016 | 本地缓存：查过的内容进缓存，关键词+语义混合检索；重复查询即时、免费、断网可用 | ✅（cache 工具；关键词+混合语义检索） |
| F-017 | find_similar：给一个网址或概念找相似页面，关键词+语义+实时网页三路合并 | ✅ |
| F-018 | research：把问题拆成多个小问题同时搜，抓完汇总成带引用的报告 | ✅ |
| F-019 | agent：自己规划步骤，搜索/抓取/提取一步步做，可设时间限制、输出 schema | ✅（plan→search→fetch→extract→synthesize；步骤日志） |
| F-020 | research/agent 写报告需接 LLM；不配 key 也不影响使用——返回结构化证据简报，把原始材料和证据交给上层 Agent 自己组装 | ✅（keyless 六工具之外三能力；无 key 返回 structured evidence brief） |
| F-021 | diff：列出页面与上次访问相比的变化；watch：隔一段时间自动复查，有变化往 webhook 推 | ✅ |
| F-022 | 安装：`npx wigolo init`，下载浏览器引擎和本地模型并做健康检查；需 Node 20+、约 1.5G 磁盘；支持 macOS/Linux/Windows | ✅（Node 20/22/24 LTS；模型 ~250MB + 浏览器 0.5–1GB） |
| F-023 | `npx wigolo init --agents=claude-code,cursor` 一键把 MCP 接进 Agent | ✅（--agents 逗号分隔，官方矩阵 9 客户端） |
| F-024 | `npx wigolo doctor` 检查各组件状态并给出修复命令 | ✅（doctor / doctor --fix / verify） |
| F-025 | 核心功能（搜索抓取）不要 key；research/agent 写报告要配 LLM，官方支持多家 provider，博文作者用本地 Ollama | ✅（gemini/anthropic/openai/groq/ollama/OpenAI 兼容） |
| F-026 | 作者实践 1：让 Agent 查最新版本文档/文档问答，答案带原文位置，不怕编 | ✅ 机制成立（source_span 字节级定位） |
| F-027 | 作者实践 2：用 watch 挂项目更新日志/定价页，有更新自动推 webhook | ✅ 机制成立 |
| F-028 | 作者实践 3：`wigolo serve` 起本地 REST 服务，n8n 里直接 curl 调用 | ✅（serve 默认 127.0.0.1:3333，POST /v1/{tool}） |
| F-029 | 作者观点：Agent 查网页次数多，按量计费 API 成本高；wigolo 零成本 + 缓存命中，省钱 | ✅ 定位一致（no metered bill） |
| F-030 | 作者"实在话"：至少 1.5G 磁盘（本地模型+浏览器引擎）；公共搜索引擎偶发抽风但 18 引擎融合单个挂影响不大；beta 完成度，个别复杂抓取场景不如付费工具 | ✅（磁盘构成官方确认；降级引擎 reported not hidden；FAQ 诚实标注 challenge ceiling） |
| F-031 | 作者引官方实测：同一场 Claude 会话里，内置 WebSearch / wigolo / Tavily / Exa 回答同一问题，结论一致、头号信源一致；wigolo 唯一返回字节级定位证据，打分和引擎状态全列出，其评分器还标出 2 条弱结果；Exa 完整渲染官方对比矩阵 | ✅（README Benchmark：Claude Fable 5 单场四工具对比；对比表口径 July 2026） |
| F-032 | 作者结论：网页爬取是强项，付费服务按次收的它免费；本地工具不要 key/账号、数据不出机器、AGPL 开源不担心突然收费 | ✅ 与官方定位一致 |
| F-033 | 开源地址：https://github.com/KnockOutEZ/wigolo | ✅ |

## B. 核验补充事实（F-034~F-052，来自官方仓库/文档）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-034 | 官方一句话定位："Local-first web intelligence for AI agents — no keys, no cloud, no metered bill"；一键接线支持 9 个客户端（claude-code/cursor/codex/gemini-cli/opencode/vscode/windsurf/zed/antigravity），另有 LangChain/CrewAI/LlamaIndex/Vercel AI SDK 框架集成包与 n8n | README、llms.txt |
| F-035 | LICENSE 为 GNU AGPL v3（AGPL-3.0-only），Copyright 2026 Towhid Khan；维护者 @yourtowhid；README 鸣谢赞助商 TestMu AI（formerly LambdaTest） | LICENSE 文件、README |
| F-036 | 版本状态：public beta 0.2.0；官方 FAQ："The documented surface is held to a test suite of roughly 7,600 automated tests" | docs/troubleshooting.md FAQ |
| F-037 | keyless 六工具明确清单：search / fetch / crawl / extract / cache / find_similar；research / agent / `search --format answer` 需 LLM，无 key 时返回结构化证据（structured evidence）而非成文报告 | README |
| F-038 | LLM provider 支持：gemini（免费 key，aistudio.google.com/apikey）/ anthropic / openai / groq / ollama（本地）/ 任意 OpenAI 兼容端点；配置 env：`WIGOLO_LLM_PROVIDER`、`GEMINI_API_KEY` 等 | README 配置段 |
| F-039 | 结果契约字段：`citation_id`、`source_span`（字节偏移 start/end）、`evidence_score`（final/semantic/lexical/engine_consensus 子项）、`freshness_signal`（published/confidence）；弱结果打 `junk` 标签；陈旧缓存显式标注 | README 结果示例 |
| F-040 | fetch 三级升级路由：plain HTTP → TLS-impersonation tier → full browser engine；按域名复用已通过的 challenge clearance；支持单 section 抽取、PDF、登录态、页面动作（click/type/scroll/screenshot） | README、troubleshooting.md |
| F-041 | REST 服务：`wigolo serve` 默认 127.0.0.1:3333；`POST /v1/{tool}`；`GET /openapi.json`（OpenAPI 3.1）；远程 MCP 端点 /mcp + /sse；绑定非 loopback 需 `WIGOLO_API_TOKEN`（fail-closed 设计） | README、docs/rest-api.md |
| F-042 | SDK：npm `wigolo-sdk`（零依赖，local 模式自动发现/拉起 daemon）；PyPI `wigolo`（仅标准库，sync+async）；框架包 `wigolo-vercel-ai-sdk` / `wigolo-langchain` / `wigolo-crewai` / `wigolo-llamaindex`；Docker 镜像 ghcr.io/knockoutez/wigolo | llms.txt、README |
| F-043 | 常用命令：`npx wigolo search "..." --limit=2`、`npx wigolo fetch <url> --max-content-chars=400`、任意工具命令加 `--json` 出机器可读结果；`npx wigolo verify` 端到端冒烟（真实网络）；init 变体 `--no-warmup` / `--interactive` / `--wizard` / `--json` | docs/getting-started.md |
| F-044 | doctor 报告项：数据目录、浏览器引擎、本地模型、已配置 LLM provider、搜索后端、逐引擎状态（含可选引擎所需 env，如 WIGOLO_GITHUB_TOKEN / BRAVE_API_KEY）；`warmup --all/--browser/--reranker/--embeddings` 补下载；`cache clear --url-pattern` 清缓存；`config --uninstall --yes` 卸载；`config --cleanup` 回收模型/浏览器磁盘 | docs/getting-started.md、troubleshooting.md |
| F-045 | 已知边界①：磁盘占用 = 本地 embedding+reranking 模型约 250MB + 可选浏览器引擎二进制约 0.5–1GB；`init --no-warmup` 可延迟下载，`config --cleanup` 可回收 | FAQ |
| F-046 | 已知边界②：linux-arm64 上语义功能暂不可用（embeddings tokenizer 无 ARM 预编译），find_similar/语义缓存排序回退关键词匹配；x64 主机正常 | troubleshooting.md 平台说明 |
| F-047 | 已知边界③：datacenter IP（VPS/CI/云主机）信誉评分低，部分 challenge 保护站点无法通过（住宅网络同一请求可过）；可选代理杠杆 `USE_PROXY=true` + `PROXY_URL`（凭据进 OS keychain 不落盘） | troubleshooting.md blocked_by_challenge |
| F-048 | 遥测默认关闭；仅 opt-in（`WIGOLO_TELEMETRY=1`）写 NDJSON 到 `~/.wigolo/telemetry/`；日志默认全走 stderr（结构化 JSON） | troubleshooting.md、llms.txt |
| F-049 | Windows 支持 Node 20+，数据目录 `%USERPROFILE%\.wigolo`；搜索后端三档 core / searxng / hybrid（env `WIGOLO_SEARCH`）；公司代理可用 `USE_PROXY`/`PROXY_URL`，TLS 审计代理设 `NODE_EXTRA_CA_CERTS`；离线机可在联网机 warmup 后拷贝 `~/.wigolo` 预置模型 | troubleshooting.md 平台/网络段 |
| F-050 | 官方 Benchmark 细节：单场 Claude（README 原文 "Claude Fable 5"）会话四工具同题对比，四者答案与头号信源一致；wigolo 唯一提供字节级证据定位 + 评分拆解 + 逐引擎遥测，并标出 2 条弱结果；官方对比矩阵由 Exa 完整渲染；对比表口径 "Feature standing as of July 2026" | README Benchmark 段 |
| F-051 | AGPL 通俗解释（官方 FAQ）：把 wigolo 当工具用（个人/公司/接进任意 Agent）零义务；只有"修改 wigolo 本体并把修改版作为网络服务提供给他人"时才需开源修改；仅调用 wigolo 的产品不受约束。伦理立场：默认遵守 robots.txt、按域名限速、页面预算面向研究而非批量收割，明确"not a cloaking toolkit" | FAQ |
| F-052 | 扩展机制：11 个 agent skill packs（docs/skills.md，带安装回执模型）；插件机制支持自定义搜索引擎与提取器（docs/plugins.md）；配置文件 config.json + env vars（docs/configuration.md） | llms.txt |

## C. 第三方旁证（信源距离：第三方综述，仅作热度/时点佐证）

| 编号 | 旁证 | 时点 |
|------|------|------|
| C-01 | CSDN《GitHub 热点项目》第 163 期收录 wigolo：1,218 stars / 83 forks / 仓库创建 2026-04-12 / Public Beta | 2026-07-19 |
| C-02 | aitoolly 工具目录收录页（AI 搜索工具分类） | 2026-07-20/21 |
| C-03 | vampireachao 个人博客 wigolo 介绍文 | 2026-07-21 |
| C-04 | 龙虾播客/Geek 推文等社区讨论 | 2026-07-16~19 |

## D. 勘误四张清单结论

1. **日期/版本勘误**：博文未给版本号 → 补 0.2.0 public beta（F-036）；博文确切发布日期未检出 → 标注约 2026-07 下旬（F-001）。
2. **成效数字勘误**："七千多个测试用例" ✅ 与官方 ~7,600 一致（F-007/F-036）；"18 个搜索引擎" ✅（F-009）；"1.5G 磁盘" ✅ 构成拆解（F-045）；Firecrawl "一月一千页" ⚠️ 单源博文口径（F-002）。
3. **口径对照**：博文"作者一个人维护" → 精确为"个人维护者 Towhid Khan + 社区赞助 TestMu AI"（F-035）；"不要 key" → 精确为"核心六工具 keyless，research/agent 成文需 LLM key（可本地 Ollama）"（F-037/F-038）。
4. **引文核对**：博文转述官方四工具对比结论与 README Benchmark 原文一致（F-031/F-050），未发现夸大或歪曲。
