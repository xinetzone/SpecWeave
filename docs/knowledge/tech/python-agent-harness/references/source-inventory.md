# 附录 A：信源台账（S01–S23）

> 全部信源采集日期：**2026-09-29 至 2026-09-30**，采集方式为 WebSearch 定位 + WebFetch 精读。下表 URL 为采集时实际访问的站点或页面；版本号与 star 数是时点快照，复核方法见 A.5。

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
| 一手 | S02、S07、S08、S10、S11、S12、S13、S14、S15、S16、S17、S18、S19、S22、S23（官方文档/博客/PyPI/官方 API） | 可直接支撑产品事实（API、版本、能力清单）；版本号仍须标注时点 |
| 二手分析 | S03、S05、S09、S20、S21（第三方实测/复盘/百科条目） | 只在标注来源的前提下引用；量化数字按原文口径转述，不跨文章排名 |
| 新闻 | S06 | 仅作背景登记（F-008），不进入任何结论链 |

## A.5 复核方法（V 审查 O5 采纳后新增）

本知识包中的版本号、star 数与发版日期保鲜期短，引用前按下列方法刷新（命令示例，PowerShell/bash 均可）：

1. **PyPI 最新版本与发布时间**：访问 `https://pypi.org/pypi/<包名>/json`，读 `info.version` 与 `releases` 键；或 `pip index versions <包名>`（需新版 pip）。
2. **GitHub star 数与维护状态**：`https://api.github.com/repos/<owner>/<repo>` 读 `stargazers_count`、`archived`、`pushed_at`；在仓库 README/issue 中检索 `maintenance`、`archived`、`sunset` 关键词。
3. **破坏性变更**：先读官方 changelog（如 Pydantic AI 的 https://ai.pydantic.dev/changelog/ ），再决定是否跨小版本升级；0.x 包默认假设会破坏。
4. **许可证**：以仓库根目录 LICENSE 文件全文与 PyPI `info.license` / `info.classifiers` 双核对，不以二手文章的标签为准（F-042 中六个未取证包按此法补证）。
5. **SWE-bench 成绩**：只比较同一评测文章/榜单页内、同模型、同采样次数的条目；跨页数字不排座次（见 [04 编码 agent 赛道](../concepts/04-coding-agent-track.md) §4.3）。

## A.6 采集过程中的无效路径

| 尝试 | 结果 | 处理 |
|---|---|---|
| 仅凭框架名字面推断许可证（如默认 smolagents/Strands 为 MIT/Apache） | 无一手页面佐证 | 拒绝写入，F-042 统一登记"未取证" |
| 将不同文章的 SWE-bench 数字合成一张排行榜 | 模型/采样/版本口径不一致 | 拒绝合成，改为 04 概念页 §4.3 口径警告 |
| 引用 GPT-6.1 Astra 报道作为"安全问题严重"的论据 | 单一新闻簇、无官方证实 | 降级为 F-008 背景，仅一处使用并加注 |
