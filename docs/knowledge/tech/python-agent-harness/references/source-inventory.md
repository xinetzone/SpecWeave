# 附录 A：信源台账（S01–S38）

> 全部信源采集日期：**v1.0 为 2026-09-29 至 2026-09-30；v1.1 为 2026-11-10**。采集方式为 WebSearch 定位 + WebFetch 精读。下表 URL 为采集时实际访问的站点或页面；版本号与 star 数是时点快照，复核方法见 A.5。

## A.1 生态格局与术语

| 键 | 信源 | URL / 位置 | 支撑事实 |
|---|---|---|---|
| S01 | aiagentslist.io 框架分类目录 | https://aiagentslist.io/ | F-001（四类分法）、F-044（平台型）、F-045（RAG 型） |
| S02 | LangChain「Deep Agents」官方文档 | https://www.langchain.com/deep-agents | F-002（harness 定义与三层栈）、F-045（LangGraph 角色） |
| S03 | Growth Engineer：AI Agent Frameworks Compared（2026-05） | https://growthengineer.ai/blog/ai-agent-frameworks-compared | F-003（七框架 TTFA/LOC）、F-004（34% 与 CrewAI 45.9K/$18M）、F-025（smolagents 生产就绪 2/5）。**单一第三方实测，全文按单点口径引用** |
| S04 | Anthropic Engineering：多智能体研究系统 | https://www.anthropic.com/engineering/multi-agent-research-system | F-005（+90.2%、约 15 倍 token、故障位于编排与交接） |
| S05 | Datarekha：From AutoGPT to 2026 — What Survived | https://datarekha.com/blog/autogpt-to-2026-what-survived | F-006（AutoGPT 16 天约 5 万星、BabyAGI 约 100 行）、F-007（四失败形态、留存四原语、约 $40 案例） |
| S06 | 2026-09 下旬行业新闻（GPT-6.1 Astra 取消、沙箱逃逸报道） | 检索词「GPT-6.1 Astra canceled agent sandbox escape 2026-09」可得的多篇科技媒体报道 | F-008。**新闻信源、未交叉证实，仅作背景，禁止外推** |

## A.2 通用框架与厂商 SDK（官方一手信源）

| 键 | 信源 | URL / 位置 | 支撑事实 |
|---|---|---|---|
| S07 | Deep Agents 官方页 + GitHub README（raw） | https://raw.githubusercontent.com/langchain-ai/deepagents/main/README.md | F-009（pip/MIT/API）、F-010（九件能力 + dcode） |
| S08 | Microsoft DevBlogs：Agent Framework at BUILD 2026 / GA 公告 | https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/ （及该博客 GA 1.0 公告） | F-011（2026-04-02 GA、合并、MIT、三语言）、F-012（graph/checkpoint/七 Provider/CodeAct/MCP/A2A）、F-013（版本）、F-040（合并） |
| S09 | AG2 项目资料（aiwiki 条目 + AutoGen 研究文章） | https://aiwiki.ai/wiki/ag2 ；https://rywalker.com/research/autogen | F-013（AutoGen 维护模式、最后功能版 2025-09、约 58.9K stars）、F-014（AG2 分叉、Apache-2.0、PyPI 名） |
| S10 | OpenAI Agents SDK 官方文档 + cookbook | https://openai.github.io/openai-agents-python/ | F-015（Swarm 升级、核心抽象、Responses API）、F-016（cookbook pin 0.9.3 + 频变警告）、F-040（Swarm 更名） |
| S11 | Claude Agent SDK 官方文档 + PyPI 版本页 | https://code.claude.com/docs/en/agent-sdk/overview ；https://pypi.org/project/claude-agent-sdk/ | F-017（pip/MIT/Py3.10+/二进制/query+Client）、F-018（in-process MCP/permissions/hooks/subagents/checkpointing/OTel；0.1.71/0.2.94/0.2.161） |
| S12 | Pydantic AI v1 发布文章 + 官方文档 changelog | https://pydantic.dev/articles/pydantic-ai-v1.md ；https://ai.pydantic.dev/changelog/ | F-019（v1.0 日期/1500 万下载/v2.0 日期与 breaking/MIT）、F-020（DI/Logfire/100%/durable 四后端）、F-021（harness/Graph/Evals/Gateway/Monty） |
| S13 | Google ADK 官网 + adk-python README（raw） | https://adk.dev/ ；https://raw.githubusercontent.com/google/adk-python/main/README.md | F-022（pip/Apache-2.0/Py3.10+/双周/2.0 graph+Task/五语言/部署目标） |
| S14 | Strands 官网 + AWS Prescriptive Guidance | https://strandsagents.com/ （及 AWS 官方 Strands 指南页） | F-023（pip/import/model-first/40+ 工具/MCP/Q Developer 同源/约 12.7K）、F-024（harness/harness-sdk/shell/evals） |
| S15 | smolagents 官方文档（Hugging Face） | https://huggingface.co/docs/smolagents | F-025（约 1000 行/CodeAgent/沙箱执行） |
| S16 | Agno 官方文档 + PyPI 项目页 | https://docs.agno.com/ ；https://pypi.org/project/agno/ | F-026（Apache-2.0/open-core/五抽象/AgentOS 50+ 端点/2.7.0a5 日期）、F-040（Phidata 更名） |
| S17 | AgentScope 2.0 官方文档（版本化文档站） | https://docs.agentscope.io/versions/2.0.6/ | F-027（2.0 重写日期/六抽象/五种工作区后端/PowerShell/飞书 Discord/MCP/v2.0.6 日期） |
| S18 | Qwen-Agent 官方文档 | https://qwen.readthedocs.io/ | F-028（pip extras/Assistant+function_list/OpenAI 兼容端点） |

## A.3 编码 agent 与 SWE 赛道

| 键 | 信源 | URL / 位置 | 支撑事实 |
|---|---|---|---|
| S19 | mini-swe-agent PyPI 页 + 项目仓库 README | https://pypi.org/project/mini-swe-agent/ ；https://github.com/SWE-agent/mini-swe-agent | F-029（1.4.2/各约 100 行/仅 bash/无线性历史外的状态/subprocess）、F-030（65%/74%/四容器）、F-031（替代关系表述） |
| S20 | Software Letters SL#68（ICLR 2026 相关分析） | https://softwareletters.com/ （SL#68 期）；SWE-agent 官网 https://swe-agent.com/ | F-031（maintenance-only）、F-032（4161 行/67%/$2.50 对 131 行/65%/$0.37）。**单一来源，行数与成本口径以原文为准** |
| S21 | OpenHands 项目资料（aiwiki 条目） | https://aiwiki.ai/wiki/openhands | F-033（OpenDevin 2024-03-12、2024-08-26 更名/MIT/CodeActAgent/LiteLLM/Docker/超 76K）、F-040（更名） |
| S22 | OpenHands 官方 leaderboard API | https://index.openhands.dev/api/leaderboard | F-034（Claude 3.7 60.6%/66.4%；v1.18.1+claude-fable-5 2026-06-09 = 95.8/$1.43） |
| S23 | Aider 官网 | https://aider.chat/ | F-035（pip/44K/6.8M 安装/15B tokens 每周）、F-036（RepoMap/tree-sitter/git/architect/LiteLLM/100+ 语言） |

## A.4 信源分级与使用纪律

| 级别 | 信源 | 使用纪律 |
|---|---|---|
| 一手 | S02、S07、S08、S10、S11、S12、S13、S14、S15、S16、S17、S18、S19、S22、S23、S24、S25、S26、S27、S28、S29、S30、S31、S32、S33、S34、S35、S36、S37、S38（官方文档/博客/PyPI/官方 API/官方论文） | 可直接支撑产品事实（API、版本、能力清单）；版本号仍须标注时点。**厂商对自家产品的效果陈述仍属自报**，须保留限定语 |
| 二手分析 | S03、S05、S09、S20、S21（第三方实测/复盘/百科条目） | 只在标注来源的前提下引用；量化数字按原文口径转述，不跨文章排名 |
| 新闻 | S06 | 仅作背景登记（F-008），不进入任何结论链 |

## A.5 复核方法（V 审查 O5 采纳后新增；v1.1 补充第 6 条）

本知识包中的版本号、star 数与发版日期保鲜期短，引用前按下列方法刷新（命令示例，PowerShell/bash 均可）：

1. **PyPI 最新版本与发布时间**：访问 `https://pypi.org/pypi/<包名>/json`，读 `info.version` 与 `releases` 键；或 `pip index versions <包名>`（需新版 pip）。
2. **GitHub star 数与维护状态**：`https://api.github.com/repos/<owner>/<repo>` 读 `stargazers_count`、`archived`、`pushed_at`；在仓库 README/issue 中检索 `maintenance`、`archived`、`sunset` 关键词。
3. **破坏性变更**：先读官方 changelog（如 Pydantic AI 的 https://ai.pydantic.dev/changelog/ ），再决定是否跨小版本升级；0.x 包默认假设会破坏。
4. **许可证**：以仓库根目录 LICENSE 文件全文与 PyPI `info.license` / `info.classifiers` 双核对，不以二手文章的标签为准（F-042 中六个未取证包按此法补证）。
5. **SWE-bench 成绩**：只比较同一评测文章/榜单页内、同模型、同采样次数的条目；跨页数字不排座次（见 [04 编码 agent 赛道](../concepts/04-coding-agent-track.md) §4.3）。
6. **版本号直读（v1.1 补充）**：PyPI 项目页顶部即当前最新版本号，`Released` 行为该版本发布时间；本包 v1.1 的 F-061~F-065 均按此方式取证。注意项目页可能因缓存显示与 `json` 接口不同的版本（如 Claude Agent SDK 页面显示 0.2.152，而 v1.0 曾记录 0.2.161），**引用时须同时记录版本号与取数页面**，不可只写"最新版"。

## A.6 采集过程中的无效路径

| 尝试 | 结果 | 处理 |
|---|---|---|
| 仅凭框架名字面推断许可证（如默认 smolagents/Strands 为 MIT/Apache） | 无一手页面佐证 | 拒绝写入，F-042 统一登记"未取证" |
| 将不同文章的 SWE-bench 数字合成一张排行榜 | 模型/采样/版本口径不一致 | 拒绝合成，改为 04 概念页 §4.3 口径警告 |
| 引用 GPT-6.1 Astra 报道作为"安全问题严重"的论据 | 单一新闻簇、无官方证实 | 降级为 F-008 背景，仅一处使用并加注 |
| 把 mini-swe-agent README 的 ">74%"、"击败 Claude Code 与 Codex" 当作独立结论 | 项目方自述；且 DeepSWE 固定 mini 为 harness，设计上不适合反推 harness 优劣（F-057） | 保留数字但全程标注"项目方自述"，并在 04 §4.3 增加"先看榜单是否固定 harness"的读法 |
| 把"缓存 token 按 10% 计费"写成行业通例 | 该折扣出自 Claude API 价目（F-050），其他厂商规则不同 | 全文加口径限定，禁止跨厂商外推 |
| 用 Copilot harness 的 vCPU 单价与自建方案做 TCO 对比 | 预览期定价、12-01 才生效、随区域与协议变化（F-059） | 仅作量级参考，并在 03 §3.6 加显式警告 |
| 用厂商博客的"效果不降"支撑"变薄无害"的普遍结论 | 三个案例全部来自 harness 卖方，存在自利偏差 | 拆分陈述：token/代码行数为可机械验证，效果类为自报；并把结论限定为"补偿型部件"，治理型不适用 |

## A.7 v1.1 增量信源（S24–S38，采集时点 2026-11-10）

| 键 | 信源 | URL / 位置 | 支撑事实 |
|---|---|---|---|
| S24 | LangChain Deep Agents 官方 changelog | https://docs.langchain.com/oss/python/releases/changelog | F-046（v0.7 减配项与 breaking changes） |
| S25 | LangChain 博客：Deep Agents v0.7（2026-07-29） | https://www.langchain.com/blog/deep-agents-v0-7 | F-046（-65% base tokens、43% 工具描述、todo opt-in）、F-047（三分类 × 四模型对照、置信区间跨零）、F-051（转述 Claude Code prompt -80%）。**厂商自述** |
| S26 | LangChain 博客：Deep Agents v0.5（2026-04-07）/ v0.6（2026-05-13）/ Managed Deep Agents v0.10 | https://blog.langchain.dev/deep-agents-v0-5/ ；https://www.langchain.com/blog/deep-agents-0-6 ；https://www.langchain.com/blog/managed-deep-agents-browser-use-and-asynchronous-subagents | F-048（发版节奏与托管版） |
| S27 | Anthropic / Claude 博客：Agent Harness Design — 3 Patterns（2026-04-02） | https://claude.com/blog/harnessing-claudes-intelligence | F-049（harness 定义与假设过期）、F-050（缓存 10% 与五条前缀纪律）、F-051（-80% 转述）、F-052（context reset 变死重）、F-053（三组能力实测）、F-068（专用工具作边界、auto-mode）。**厂商自述** |
| S28 | mini-swe-agent PyPI 项目页（2.4.6） | https://pypi.org/project/mini-swe-agent/ | F-054（v2、>74%、使用方列表）、F-055（执行后端）、F-057（DeepSWE 自述）。**项目方自述** |
| S29 | mini-swe-agent 文档 + SWE-agent 文档 | https://mini-swe-agent.com/latest/ ；https://swe-agent.com/latest/ | F-055（后端清单）、F-056（superseded 表述） |
| S30 | DeepSWE 论文（arXiv 2607.07946） | https://arxiv.org/pdf/2607.07946 | F-057（固定 mini-swe-agent 作 harness 的方法论） |
| S31 | Microsoft Foundry 博客 + Microsoft 官方博客（2026-10-28） | https://devblogs.microsoft.com/foundry/microsoft-copilot-harness-in-foundry/ ；https://blogs.microsoft.com/blog/2026/10/28/introducing-the-microsoft-copilot-harness-unlocking-the-potential-of-truly-multi-model-agentic-work/ | F-058（托管 harness 形态、SKILL.md 技能、注入防御模板）、F-059（vCPU·小时计价）、F-060（long-running resilience GA、三档取舍） |
| S32 | openai-agents PyPI 项目页（0.24.0，2026-10-15） | https://pypi.org/project/openai-agents/ | F-061（版本、核心概念、provider-agnostic） |
| S33 | strands-agents PyPI 项目页（1.57.2，2026-10-02） | https://pypi.org/project/strands-agents/ | F-062（版本时点） |
| S34 | claude-agent-sdk PyPI 项目页（0.2.152，2026-09-03） | https://pypi.org/project/claude-agent-sdk/ | F-063（版本、MIT、Py3.10+、CLI 捆绑） |
| S35 | pydantic-ai PyPI 项目页（2.66.0） | https://pypi.org/project/pydantic-ai/ | F-064（版本、Harness 的 capabilities 形态） |
| S36 | deepagents PyPI 项目页（0.7.32，2026-10-24） | https://pypi.org/project/deepagents/ | F-065（版本、MIT、定位自述） |
| S37 | adk.dev ADK 2.0 页 + 第三方发布记录 | https://adk.dev/2.0/ ；https://agentupdate.ai/releases/google-adk | F-066（2.0 GA 日期、2.13.0 于 2026-10-22、部署目标） |
| S38 | Microsoft Learn：Agent Harness 概念页 | https://learn.microsoft.com/en-us/agent-framework/concepts/harness | F-067（去品牌化定义与职责） |
