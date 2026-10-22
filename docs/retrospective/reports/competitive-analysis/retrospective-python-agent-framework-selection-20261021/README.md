---
title: "Python 智能体框架选型调研：11 个候选框架 + 5 个排除项/参照项（LangChain/LangGraph/CrewAI/MAF/PydanticAI 等）"
date: 2026-10-21
updated: 2026-10-21
source: "15 份框架事实表 + LangGraph 种子事实表（GitHub REST API / PyPI JSON API / 官方文档实时抓取，2026-10-21）+ 官方 README/DevBlogs 原文核实争议项；kimi-webbridge 浏览器层核验未执行（扩展未连接，extension_connected=false），数值以官方 API 同源数据为准"
method: "七概念方法论编排（场景：技术选型知识沉淀）R→I→E→V，session=sc-20261021-python-agent-framework-selection；R 阶段 16 份事实表已过 G1，本报告为 I（洞察）+ E（萃取）阶段产出，V 门对抗审查已完成（13 条意见全部采纳，详见第十节）"
tags: [python, ai-agent, 框架选型, langchain, langgraph, crewai, autogen, maf, pydanticai, llama-index, haystack, dify, 七概念, 竞品分析]
---

# Python 智能体框架选型调研：11 个候选框架 + 5 个排除项/参照项

> **方法论**：七概念编排 **R（事实）→ I（洞察）→ E（萃取）→ V（对抗审查）**。R 阶段完成 16 份框架事实表（15 份框架事实表 + LangGraph 种子），全部实时抓取自 GitHub REST API / PyPI JSON API / 官方文档，抓取日期 2026-10-21；I 阶段形成 4 条四元组洞察；E 阶段沉淀「五筛法」选型模式；V 门对抗审查已完成（13 条意见全部采纳，详见第十节）。
> **评估范围**：Python 智能体框架横向选型（对话式 / 任务自动化 / 多智能体协作 / 工作流编排 / RAG 问答五类负载），覆盖头部开源框架与低代码平台参照。
> **非评估范围**：框架基准测试（token 吞吐/延迟/成本实测）、厂商商务条款、私有化部署方案对比。
> **事实/判断分离约定**：全文中 Stars、版本号、日期、许可证、Python 要求、URL 为**事实**（来自事实表，抓取日期 2026-10-21）；定位描述、上手难度评分（x/5）、成熟度评级、推荐结论为**判断**，均已标注。

---

## 一、执行摘要（结论先行）

**总体结论（判断）**：2026 年 10 月的 Python 智能体框架格局已从「百花齐放」进入「官方收敛期」——微软 AutoGen 与 Semantic Kernel 合并为 Microsoft Agent Framework（MAF）、OpenAI Swarm 被 Agents SDK 取代、transformers.agents 迁出为 smolagents；新项目不应再以 stars 排行榜选型，而应按「智能体类型 → 国产模型需求 → 维护风险」三步分流。

### 1.1 个人项目权重（易上手 / 快速迭代优先）

| 排序 | 推荐 | 理由（判断，依据事实） |
|---|---|---|
| 首选 | **PydanticAI** | 上手难度 2.5/5，`Agent('deepseek:deepseek-v4-flash')` 一行起手；DeepSeek/Qwen/GLM/Moonshot 四家均有官方 provider 文档页（原生支持）；pydantic 团队官方维护，最新 release 2026-10-21 即抓取当日（事实，2.59.0）；typed end-to-end 与 Pydantic v2 数据模型无缝衔接（注：要求 Python ≥3.11；open issues 1563，社区工单量较大） |
| 备选 | **CrewAI** | 上手难度 2/5（本组最低之一），角色扮演 Crew 心智贴近业务人员；国产模型经 LiteLLM 前缀封装（`deepseek/`、`qwen/`、`zhipuai/`，兼容前缀档、非框架原生 provider 页）；stars 59942，近 30 天 5 个 patch release |
| 备选 | **Agno** | 上手难度 2/5，纯 Python、无图/链抽象，单文件起 Agent；DeepSeek/Qwen/Moonshot/InternLM/MiniMax/MiMo 原生 provider；>=3.9 门槛最低 |

### 1.2 商业化权重（稳定 / 可扩展 / 长期维护优先）

| 排序 | 推荐 | 理由（判断，依据事实） |
|---|---|---|
| 首选 | **LangGraph** | MIT 许可；pushed_at=抓取当日（2026-10-21）；显式状态图（StateGraph）+ checkpointer 持久化 + human-in-the-loop 为生产级智能体的硬需求；多智能体拓扑（supervisor/swarm/network）官方一等支持；LangChain 生态（148185 stars）最大社区兜底 |
| 次选 | **Microsoft Agent Framework (MAF)** | 微软官方生产级 SDK，Python 1.22.0（2026-10-15）周级发版，MIT；AutoGen + Semantic Kernel 双线官方合并继任者，微软承诺长期支持；图式编排（sequential/concurrent/handoff/group collaboration）原生；**代价**：与 Azure Foundry/Azure OpenAI 生态耦合较深，非微软栈团队慎用（注：1.x 仍周级迭代、azure-ai 集成仍 rc，生产 PoC 须预留收敛期） |
| 备选 | **CrewAI / Haystack** | CrewAI：商业公司（CrewAI Inc.）主导、周级发版、MIT；Haystack：Apache-2.0（商用最友好）、发版节奏稳定（约 2-3 周一版，3.4.0 于 2026-10-15）、Pipeline DAG 控制粒度显式 |

### 1.3 明确不进入新项目候选的框架（判断，依据事实）

- **microsoft/autogen**：已归档（README 红色 Archived 徽章 + CAUTION 块，"no longer maintained"），最新 release python-v0.7.5 停留在 2025-09-30，近 12 个月无功能发布；继任者为 MAF。
- **OpenAI Swarm**：README IMPORTANT 块原文声明"Swarm is now replaced by the OpenAI Agents SDK"；最后一次功能提交在 2024-10，从未发布 GitHub Release。
- **transformers.agents**：已从 transformers v5.20.2 主包源码中移除（GitHub contents API 实测 `*agent*` 匹配为空），由独立包 **smolagents** 继任；旧 `from transformers import CodeAgent` 写法已失效。
- **Mastra**：TypeScript 框架，**无官方 Python 包**（PyPI `mastra`/`mastra-py` 等均 404，仓库语言字节中 Python=0）；社区包 `pymastra` v0.5.0 的 project_urls 指向 `YOUR_USERNAME` 占位仓库，不构成 Python 候选。
- **Dify**：低代码 Agentic 工作流平台（可视化画布 + Service-API），**非库式框架**，不以 `pip install` 后在代码中编排为主用法；代码级自研场景不进入候选，仅在业务团队零代码搭应用时作为平台参照。

---

## 二、方法论与数据来源

### 2.1 事实/判断分离约定

- **事实层（R 阶段）**：16 份事实表逐字段记录 GitHub Stars、pushed_at、archived、最新 release/tag 与日期、PyPI 包名/版本/requires_python、许可证、官方文档中的模型支持声明；每条事实保留来源 URL；争议项（AutoGen 归档状态、Swarm 取代关系、transformers.agents 移除、Mastra Python 现状、MAF 与 AutoGen/SK 关系）均以官方 README/DevBlogs 原文核实。
- **判断层（本报告 I/E 阶段）**：上手难度评分（x/5）、成熟度评级、分场景推荐、执行摘要 Top 排序均为评估者判断，不冒充实测基准；权重公开，读者可按自身约束重排。

### 2.2 数据抓取说明

- **抓取日期**：2026-10-21（北京时间）。
- **GitHub**：`https://api.github.com/repos/<owner>/<repo>`（stars / pushed_at / archived / license / description）、`releases/latest` 与 `releases?per_page=N`、`commits?per_page=5`、`contents/...`。
- **PyPI**：`https://pypi.org/pypi/<package>/json`（最新版本、upload_time、requires_python、releases 时间戳）。
- **官方文档**：docs.langchain.com、developers.llamaindex.ai、docs.haystack.deepset.ai、docs.crewai.com、learn.microsoft.com、devblogs.microsoft.com、openai.github.io、ai.pydantic.dev、huggingface.co/docs、docs.agno.com、marketplace.dify.ai 等。
- **Dify Marketplace 页面（web_fetch，2026-10-21）**：`https://marketplace.dify.ai/?category=model` 与 `https://marketplace.dify.ai/?language=zh-Hans` 页面经 web_fetch 抓取，用于 DeepSeek / GLM(ZHIPU AI) 官方插件安装量（DeepSeek 约 175.6 万、GLM 约 18.6 万）。该抓取为页面 HTTP 抓取，**非** kimi-webbridge 浏览器扩展实测；精度为页面展示量级，未做二次浏览器复核。

### 2.3 如实披露：浏览器层核验未执行

> **kimi-webbridge 浏览器核验未能执行**：全部 16 份事实表抓取时，浏览器扩展返回 `no extension connected`（`extension_connected=false`），**未执行任何浏览器页面实测**。Stars 与 release 数据一律以 GitHub REST API / PyPI JSON API 实时返回值为准（与仓库页同源），未与仓库页四舍五入显示值做交叉比对。Dify Marketplace 安装量例外：该数字来自 web_fetch 对 Marketplace 页面的 HTTP 抓取（见 2.2 节），非浏览器扩展实测。争议项改以官方 README raw 文件（`raw.githubusercontent.com`）与 DevBlogs/Learn 原文逐字核实。本限制影响：不影响数值准确性（API 与页面同源），但影响"页面渲染层/UI 层声明"的可见性；后续若扩展恢复，应对 Dify Marketplace 插件安装量、各框架文档站结构做一次浏览器复核。

### 2.4 争议项核实方式

| 争议项 | 核实方式 | 结论 |
|---|---|---|
| microsoft/autogen 是否还在维护 | README raw 文件顶部 Archived 徽章 + CAUTION 块 + releases/commits API | 官方声明归档停维，引导迁移 MAF |
| Swarm 是否被取代 | README raw 文件顶部 `> [!IMPORTANT]` 块 + commits 历史（2025-03-11 三连"point to Agents SDK"） | 已被 OpenAI Agents SDK 取代 |
| transformers.agents 现状 | tag v5.20.2 下 contents API 过滤 `*agent*` 实测为空 + HF 官方博客原文 | 模块已迁出，smolagents 继任 |
| Mastra 是否有 Python 版 | PyPI 4 个候选包名均 404 + languages API（Python 字节=0）+ release tag 为 npm scoped 包 | 无官方 Python 包 |
| MAF 与 AutoGen/SK 关系 | 微软 DevBlogs 2025-10-07 原文 + MS Learn 原文 | MAF = SK + AutoGen orchestrator 合并继任者 |
| AutoGen 许可证 | GitHub API 探测值 CC-BY-4.0（与 0.2 时代 MIT 不一致） | **待人工核对仓库根 LICENSE**（见待验证 Q-4） |

---

## 三、按智能体类型分场景推荐（判断）

> 首选/备选均为判断；括号内引用对应事实（抓取日期 2026-10-21）。

### 3.1 对话式智能体（聊天助手 / 客服 / 结构化对话输出）

- **首选：PydanticAI** —— DeepSeek 原生 `deepseek:` 前缀、GLM 原生 `zai:glm-5`、Qwen 原生 `alibaba:` 前缀（事实：docs/models 目录三份独立 provider 文档页）；typed end-to-end 天然适合结构化对话输出；上手 2.5/5。
- **备选：OpenAI Agents SDK** —— handoff/guardrail/sessions/tracing 一等公民，官方专门列出 realtime/voice agents 概念；代价：与 OpenAI 后端绑定较深，国产模型只能走兼容层（事实：README 声明 provider-agnostic 支持 100+ LLM，但国产无官方 provider 页）。
- **备选：Agno** —— 上手 2/5，Teams 委托三模式，国产 provider 原生面最广（DeepSeek/DashScope/Moonshot/InternLM/MiniMax/MiMo）。

### 3.2 任务自动化（数据处理 / 调研 / 写作流水线 / 脚本级 Agent）

- **首选：CrewAI** —— Crew（role/goal/backstory 角色扮演）+ Flows（`@start`/`@listen`/`@router` 事件驱动状态机）双层抽象恰好匹配"调研→写作→审核"类业务流程；上手 2/5；国产模型经 LiteLLM 前缀封装接入。
- **备选：PydanticAI** —— 工具参数即 Pydantic schema，后端服务集成零摩擦。
- **备选：SmolAgents** —— CodeAgent"写 Python 代码调用工具"模式对开源权重（HF Hub 上 Qwen/DeepSeek/GLM 原生托管）与代码沙箱（E2B/Modal/Docker）场景独特；注意最新 release v1.26.0 为 2026-05-29，距今约 5 个月（事实）。

### 3.3 多智能体协作（多角色分工 / 团队式 Agent 系统）

- **首选：LangGraph** —— 官方多智能体拓扑（supervisor / swarm / network）+ checkpointer 持久化，是生产级多智能体的最稳底座；与 LangChain 生态（148185 stars）打通。
- **备选：CrewAI** —— 原生 Crew 即多智能体一等公民（sequential/hierarchical 流程），上手成本远低于图式框架。
- **备选：Microsoft Agent Framework** —— sequential/concurrent/handoff/group collaboration 图式编排原生，周级双语言发版；**仅当团队在微软/Azure 技术栈内**。
- **不推荐：AG2 作为新项目首选** —— 虽然 GroupChat/Swarm/Magentic-One 经典拓扑活跃维护（v1.2.0, 2026-10-11），但 stars 仅 5008，社区规模与原 AutoGen 61504 不对等，路线已与微软 MAF 分叉。

### 3.4 工作流编排（显式 DAG / 可恢复长任务 / 人在环审批）

- **首选：LangGraph** —— StateGraph（节点/边/条件边/并行分支/子图）+ checkpointer（MemorySaver/SQLite/Postgres）+ time-travel 调试，编排原语最完整。
- **备选：Haystack** —— Pipeline 显式组件 DAG + 内置 Agent 组件（tool-calling 循环、state_schema 跨工具类型化数据、HITL 确认策略、MCPToolset）；Apache-2.0 商用最友好；代价：>=3.11 门槛、Agent 高阶特性部分仍标 experimental。
- **备选：MAF** —— 进程图编排 + durability/restartability（事实：README Key Features）；Azure 栈内首选。
- **低代码参照：Dify** —— 可视化 Workflow 画布 + Agent runtime，适合非代码团队快速搭建发布运营一体化；**它是平台不是库**，代码级自研场景应通过 Service-API REST 调用已发布应用，而非 import。

### 3.5 RAG 问答（私有文档 / 知识库 / 检索增强生成）

- **首选：LlamaIndex** —— 官方定位已转为"document processing platform for AI"（事实：GitHub 描述原文），connector/索引/检索器生态为其核心基因；内置 AgentWorkflow 可叠加检索增强 Agent；Qwen 官方独立包 `llama-index-llms-dashscope`（PyPI 0.7.0）。
- **备选：Haystack** —— Document Store / Retriever / Ranker / PromptBuilder / Generator 组件化，生产可控性强；Apache-2.0。
- **备选：Dify（平台形态）** —— DeepSeek 官方插件约 175.6 万安装、GLM 官方插件约 18.6 万安装（Dify Marketplace 页面 web_fetch，2026-10-21，量级可信未浏览器复核），适合业务团队零代码搭 RAG 应用；定制深度受平台边界约束。

---

## 四、框架总对比表（16 行，数值均为 2026-10-21 抓取事实）

> **分组说明（候选 vs 排除/参照）**：本表 16 行中，**候选框架 = #1-5（LangChain/LangGraph/LlamaIndex/Haystack/CrewAI）、#8（MAF）、#10（OpenAI Agents SDK）、#11（PydanticAI）、#12（SmolAgents）、#13（Agno）、#14（Semantic Kernel）共 11 个**；**排除/参照项 = #6（AutoGen 已归档）、#7（AG2 社区 fork）、#9（Swarm 停演进）、#15（Mastra 无 Python 包）、#16（Dify 低代码平台）共 5 个**。真正可入选的 Python 库式框架为 11 个，其中 #14 Semantic Kernel Python 多智能体仍标 experimental 且官方引导迁往 MAF。
>
> **范围说明（Google ADK 缺失）**：Google Agent Development Kit（`google/adk-python`，Google 官方 Python agent 框架，主打 A2A 协议与 Gemini 生态）**未纳入本次对比**——三巨头（OpenAI / Google / Microsoft）中 Google 官方 SDK 缺失，本次"收敛期"叙事只覆盖微软合并（AutoGen+SK→MAF）与 OpenAI 取代（Swarm→Agents SDK）。如需可按同一事实表方法补抓（见 §九 Q-9）；本报告不对 Google ADK 做任何数值陈述。
>
> 全部 Stars/版本/日期来自对应事实表（GitHub API / PyPI JSON，2026-10-21）；上手难度与成熟度为判断（x/5）。许可证以 GitHub API 探测为准，特殊项已加注。

| # | 框架 | 定位 | Stars(2026-10-21) | 最新版本(日期) | 许可证 | Python 要求 | 多智能体 | 国产模型支持 | 上手难度 | 成熟度 | 适合类型 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | LangChain | Agent 工程平台（LCEL + 链式生态） | 148185 | langchain 1.4.6(2026-10-14)；core 1.6.12(2026-10-16) | MIT | >=3.10,<4.0.0 | 借道 LangGraph | DeepSeek/Qwen 官方包；GLM 社区 | 3/5 | 高 | 任务自动化/对话式/RAG |
| 2 | LangGraph | 生产级状态图编排 | 43623 | langgraph 1.2.16(2026-10-21查)；cli 0.4.37(2026-10-19) | MIT | >=3.10 | 强（supervisor/swarm/network） | 兼容层（OpenAI 兼容端点 + langchain-deepseek 官方包） | 3/5 | 高 | 工作流编排/多智能体 |
| 3 | LlamaIndex | 文档处理平台 + 内置 AgentWorkflow | 52591 | 0.14.25(2026-09-21) | MIT | >=3.10,<4.0 | 中（AgentWorkflow 编排多 agent） | Qwen 官方包；DeepSeek/GLM 兼容层 | 2.5/5 | 较高 | RAG/工作流编排 |
| 4 | Haystack | 生产级 AI 编排框架（Pipeline + Agent） | 26800 | haystack-ai 3.4.0(2026-10-15) | Apache-2.0 | >=3.11 | 中（Pipeline 多 Agent 节点） | 全部兼容层（OpenAI 兼容端点） | 3/5 | 较高 | RAG/工作流编排 |
| 5 | CrewAI | 角色扮演式多智能体团队 + Flows 编排 | 59942 | 1.15.28(2026-10-14) | MIT（开源版；Enterprise/Embedded 闭源另售） | >=3.10,<3.14 | 强（原生 Crew） | LiteLLM 前缀封装（`deepseek/`、`qwen/`、`zhipuai/`）——兼容前缀档，非框架原生 provider 页 | 2/5 | 高 | 多智能体协作/任务自动化 |
| 6 | microsoft/autogen | 多智能体框架（**已归档停维，继任 MAF**） | 61504 | python-v0.7.5(2025-09-30，>12 个月未发版) | CC-BY-4.0（API 探测值，待核对仓库根 LICENSE） | >=3.10 | 强（历史资产） | 兼容层（OAI_CONFIG_LIST + base_url） | 3/5 | **已停维** | 仅历史维护/不建议新项目 |
| 7 | ag2ai/ag2 | AutoGen 社区 fork，Open-Source AgentOS | 5008 | v1.2.0 GitHub(2026-10-11)；ag2 1.1.2 PyPI | Apache-2.0 | >=3.10 | 强（经典 GroupChat/Swarm/Magentic-One） | 兼容层 | 3/5 | 活跃但规模较小 | 多智能体协作（延续 AutoGen 路线） |
| 8 | Microsoft Agent Framework | 微软官方生产级多语言 SDK，AutoGen+SK 合并继任者 | 14244 | agent-framework 1.22.0(2026-10-15)；.NET 1.25.0 并行 | MIT | >=3.10 | 强（sequential/concurrent/handoff/group 图式） | Azure Foundry 云托管（云耦合）/ 直连国产 API 走 OpenAI 兼容层 | 3.5/5 | 高（生产级，周级发版） | 多智能体协作/工作流编排/企业生产 |
| 9 | OpenAI Swarm | 实验性/教学轻量多智能体（**已停演进**） | 22065 | openai-swarm 0.1.1 PyPI(author=OpenAI Solutions；README 实际推荐 git+https 安装，PyPI 非主推路径)；**无 GitHub Release** | MIT | >=3.10 | handoff 原语 | 兼容层（覆盖 OpenAI client base_url） | 1/5 | **已停演进**（README 声明被 Agents SDK 取代） | 仅教学/不建议生产 |
| 10 | OpenAI Agents SDK | OpenAI 官方轻量多智能体框架（Swarm 继任者） | 30192 | openai-agents 0.24.0(2026-10-15) | MIT | >=3.10 | 强（Agents as Tools/Handoffs） | 兼容层（provider-agnostic，国产无官方 provider 页） | 2/5 | 高 | 多智能体/对话/语音实时 |
| 11 | PydanticAI | Pydantic 团队出品的类型安全智能体框架 | 20764 | pydantic-ai 2.59.0(2026-10-21) | MIT | >=3.11 | 中（Agent 可作工具被调用） | 原生（`deepseek:` / `zai:glm-5` / `alibaba:` / Moonshot 官方 provider 页） | 2.5/5 | 高 | 对话式/任务自动化 |
| 12 | SmolAgents | HF 官方极简"代码即动作"智能体库（transformers.agents 继任者） | 29956 | smolagents 1.26.0(2026-05-29，距今约 5 个月) | Apache-2.0 | >=3.10 | 中（ManagedAgent 分层/编排其他 agent） | 兼容层（LiteLLM/Inference Providers） | 2/5 | 中（发版放缓观察位） | 任务自动化/CodeAgent/开源权重 |
| 13 | Agno | 轻量多模态 Agent 库 / AgentOS 平台（原 Phidata） | 42850 | agno 3.1.7(2026-10-20) | Apache-2.0 | >=3.9,<4 | 强（Teams coordinate/route/broadcast 三模式） | DeepSeek/Qwen/Moonshot/InternLM/MiniMax/MiMo 原生；GLM 兼容层 | 2/5 | 高（刚经历品牌迁移） | 对话式/多智能体/任务自动化 |
| 14 | Semantic Kernel (Python) | 微软官方 LLM/Agent SDK（monorepo .NET+Python+Java） | 28681 | python-1.45.0(2026-10-06)；.NET dotnet-1.81.0 领先 | MIT | >=3.10 | 有但 **experimental**（官方标注），官方引导迁往 MAF | 全部兼容层（OpenAI connector 改 base_url） | 3.5/5 | 较高但 Python 版落后 .NET | 任务自动化/工作流编排 |
| 15 | Mastra | TS 现代 agent 框架（**无官方 Python 版**） | 28972 | @mastra/core@1.78.0(2026-10-16，npm monorepo) | Apache-2.0 开源部分 + ee/ 企业版双许可 | **无官方 Python 包**（PyPI 404；pymastra v0.5.0 为 YOUR_USERNAME 占位社区包） | TS 侧强（Python 侧不可用） | TS 侧兼容层（Python 选型不适用） | 不适用 | TS 侧高 / **Python 侧不可用** | **Python 选型排除**（仅 TS/全栈 JS 技术栈候选） |
| 16 | Dify | 低代码 Agentic 工作流平台（**非纯 Python 框架**） | 159105 | 1.17.1(2026-09-10)；官方 SDK dify-client 0.1.10 停更于 2023-11-15 | Apache-2.0 **修改版**（多租户 SaaS/前端 LOGO 需商业授权） | SDK:>=3.6（平台部署不适用） | 工作流内 Agent 节点 | DeepSeek/Qwen/GLM 均官方 Marketplace 插件（原生） | 2/5 | 高 | 工作流编排/RAG/对话式应用（低代码平台参照） |

> **表外说明**：`transformers.agents` 模块未单列行——它已从 transformers v5.20.2 主包移除（GitHub contents API 实测 `src/transformers/` 下无 `*agent*` 条目），由上表 #12 SmolAgents 独立包继任；详见第六节详情节 4.16。

---

## 五、总体建议与选型决策路径

### 5.1 决策路径（可执行，判断层）

```
① 类型分流：本项目的主智能体负载是哪一类？
   ├─ 对话式        → PydanticAI / OpenAI Agents SDK / Agno
   ├─ 任务自动化    → CrewAI / PydanticAI / SmolAgents
   ├─ 多智能体协作  → LangGraph / CrewAI（Azure 栈加 MAF）
   ├─ 工作流编排    → LangGraph（控制粒度要求高则 Haystack）
   └─ RAG 问答      → LlamaIndex（业务团队零代码则 Dify）
② 国产模型需求：是否要求 DeepSeek/Qwen/GLM 的原生体验？分两档判定——
   ├─ 原生 provider 文档页档（仓库 docs 下有独立 provider 页，参数对齐/结构化输出有保障）→ PydanticAI（`deepseek:`/`zai:glm-5`/`alibaba:`）、Agno（DeepSeek/DashScope/Moonshot 原生页）
   ├─ 前缀封装/兼容层档（无框架原生 provider，靠 LiteLLM 封装或 OpenAI 兼容端点绕道）→ CrewAI（`deepseek/` 等 LiteLLM 前缀糖）、LangGraph/Haystack/OpenAI Agents SDK/Semantic Kernel（OpenAI 兼容层）
   └─ MAF 单列：国产支持本质是 Azure Foundry **云托管**（云耦合）；直连国产官方 API 仍走 OpenAI 兼容 base_url，不按原生计
③ 维护风险剔除：查 pushed_at / 最新 release 日期 / README 迁移徽章
   ├─ 已归档/停演进：AutoGen、Swarm、transformers.agents → 剔除
   ├─ 无目标语言包：Mastra → 剔除
   └─ 发版停滞（>5 个月无 release）：smolagents → 降级为观察位
④ 生态与许可：商用场景优先 Apache-2.0（Haystack/Agno/SmolAgents）或 MIT（其余活跃项）；
   Dify 修改版 Apache-2.0 须核对多租户/LOGO 条款；AutoGen CC-BY-4.0 探测值须核对 LICENSE
⑤ 试点验证：用一个真实场景跑通 Agent → 工具调用 → 国产模型 → 会话持久化全链路，
   实测上手难度与文档质量后再全量铺开
```

### 5.1.1 30 分钟 PoC 最短路径（Top 3 各一行起手）

| 候选 | 第一行命令 | Hello world 要点 |
|---|---|---|
| PydanticAI | `pip install 'pydantic-ai-slim[openai]'` | 设置 `DEEPSEEK_API_KEY` + DeepSeek base_url 环境变量后，`Agent('deepseek:deepseek-chat')` → `agent.run_sync('你好')`，5 行内看到结构化输出（注意 Python ≥3.11） |
| CrewAI | `pip install crewai` | `crewai create crew demo` 脚手架生成 role/goal/backstory 示例 Crew，把 LLM 配置改 `LLM(model='deepseek/deepseek-chat')`，`crewai run` 跑通多角色任务流 |
| LangGraph | `pip install langgraph` | 定义一个 `StateGraph`，两个函数节点 + `MemorySaver` checkpointer，编译后 `graph.invoke(...)`，体验条件边与会话持久化（验证生产级编排的概念栈成本） |

### 5.2 E 阶段萃取模式（G3）

```yaml
id: pat-py-agent-framework-five-filter-001
name: Python 智能体框架五筛法
maturity: L1（本案例单案例萃取，待第二个选型案例验证后升 L2）
evidence: session=sc-20261021-python-agent-framework-selection 全部 16 份事实表
```

**触发场景**：为 Python 新项目（个人原型或商用产品）选择 LLM 智能体框架；或评估现有框架是否该迁移。

**不适用**：技术栈已被强制指定（如企业标准要求 Azure/Microsoft 栈、OpenAI 专属生态、或团队是 TypeScript 全栈）——此时无选型空间，直接采用对应官方 SDK。

**核心步骤（7 步）**

1. **类型筛**：先判定主智能体负载（对话/任务自动化/多智能体/工作流/RAG），锁定 1-2 个首选域，避免用"通用框架"一刀切。
2. **维护筛**：依次查 `pushed_at`（≤7 天为佳）、最新 release 日期（≤30 天）、README 顶部是否有 Archived/IMPORTANT 迁移徽章、`archived` 字段——**四者都要看**。剔除已停演进项。
3. **国产模型筛**：若需 DeepSeek/Qwen/GLM 原生体验（官方 provider 文档页、参数对齐），要求 provider 文档存在；若接受 OpenAI 兼容层，候选面放宽。
4. **语言包筛**：确认目标语言有官方包且 PyPI 版本在活跃发版（警惕无官方包的"跨语言明星框架"与占位社区包）。反例：若主语言是 Python 而框架官网主打 JS/TS，先查 PyPI 是否存在官方包，勿凭 GitHub stars 跨语言选型（Mastra 教训——28972 stars 但 Python 字节=0、PyPI 404，pymastra 为 YOUR_USERNAME 占位社区包）。
5. **许可与耦合筛**：商用场景核对许可证正文（警惕修改版 Apache、API 探测值不一致）；评估框架与特定云/特定模型厂商的耦合深度。
6. **迁移成本筛**：查当前主版本线与近 12 个月大版本跳跃/命名空间迁移史，把迁移工时计入 TCO。
7. **试点定案**：真实场景 PoC 跑通全链路后，按"个人=易上手优先 / 商用=稳定维护优先"双权重定首选 + 备选。

**反模式**

| # | 反模式 | 证据（本案例事实） |
|---|---|---|
| 1 | 按 GitHub Stars 排行榜选型 | AutoGen 61504 stars 已归档停维（v0.7.5 停在 2025-09-30），MAF 仅 14244 stars 却周级发版 |
| 2 | 只看 `archived=false` 就认为活跃 | Swarm archived=false，但最后功能提交在 2024-10；微软归档连 GitHub 都不标 archived，靠 README CAUTION 声明 |
| 3 | 把"OpenAI 兼容端点可接"等同于"国产模型一等支持" | Haystack/Semantic Kernel/OpenAI Agents SDK 国产模型全部走兼容层，无官方 provider 页；与 PydanticAI/CrewAI/Agno 原生页体验不同 |
| 4 | 给 Python 项目选了 TS 框架 | Mastra PyPI 404、语言字节 Python=0；pymastra project_urls 指向 `YOUR_USERNAME` 占位仓库 |
| 5 | 个人原型直接上重型状态图框架 | LangGraph 对单轮对话/极简脚本属过度设计（事实表边界判断）；易上手场景应优先 PydanticAI/CrewAI/Agno |

**检验标准**：选型结论须一句话答出五问——主类型是否匹配、最近一次 release 日期、国产模型是原生还是兼容层、目标语言是否有官方包、近 12 个月有无破坏性迁移。任一答不出即未完成。

**跨领域迁移示例**：同一五筛法可迁移到 **RAG 引擎选型**（LlamaIndex vs Haystack vs 自建 ES/向量库）：类型筛=检索负载（问答/搜索/多模态），维护筛=发版节奏，国产筛=国产 embedding/rerank 支持度，许可筛=商用条款，迁移筛=数据格式与索引可否导出。亦可迁移到**低代码 Agent 平台选型**（Dify vs Coze vs FastGPT）：维护筛=发版与插件生态，语言包筛=API/SDK 可用性（对照 dify-client 停更教训）。

---

## 六、分框架详情节（核心数据 + 定位 + 能力 + 风险）

> 每框架保留来源 URL；事实为 2026-10-21 抓取值。

### 6.1 LangChain

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 148185（pushed_at=2026-10-21，archived=false） | https://api.github.com/repos/langchain-ai/langchain |
| 版本 | langchain 1.4.6（2026-10-14 上传）；langchain-core 1.6.12（2026-10-16） | https://pypi.org/pypi/langchain/json |
| 许可证 / Python | MIT / >=3.10,<4.0.0 | 同上 |

- **定位（判断）**：官方描述 "The agent engineering platform."；LCEL + Runnable 链式 LLM 应用与 RAG 生态，显式状态编排交给 LangGraph。
- **能力（事实+判断）**：官方集成目录覆盖 OpenAI/Anthropic/Google/DeepSeek（`langchain-deepseek` 独立包）/Qwen（ChatQwen 官方页）/GLM（ChatZhipuAI，位于 langchain-community）；文档加载器/文本分割/向量存储/RAG 生态齐全。来源：https://docs.langchain.com/oss/python/integrations/chat/deepseek 。
- **风险（判断）**：API 表面庞大、演进快；**版本跳跃实证**——主包 0.3.0 发布于 2024-09-13，0.4 线仅有预发布 0.4.0.dev0（2025-08-05），无任何稳定 0.4.x，直接跳 1.0.0（2025-10-17）（来源：https://pypi.org/pypi/langchain/json releases 时间戳）；深度绑定 LangSmith 观测体系，替换需重写链式代码。

### 6.2 LangGraph

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 43623（pushed_at=2026-10-21，archived=false） | https://api.github.com/repos/langchain-ai/langgraph |
| 版本 | langgraph 1.2.16（PyPI）；最新 GitHub release cli==0.4.37（2026-10-19，monorepo） | https://pypi.org/pypi/langgraph/json |
| 许可证 / Python | MIT / >=3.10 | 同上 |

- **定位（判断）**：官方描述 "Build resilient agents"；把智能体建模为显式状态图。
- **能力（事实）**：StateGraph/节点/边/条件边/并行分支/子图；checkpointer 抽象（MemorySaver/SQLite/Postgres）持久化与 time-travel 调试；官方多智能体拓扑（supervisor/swarm/network）；DeepSeek 经官方 `langchain-deepseek` 包 ChatDeepSeek（来源：https://docs.langchain.com/oss/python/integrations/chat/deepseek ）。
- **风险（判断）**：与 LangChain 生态耦合；图模式对简单场景过度设计；早期版本曾随 LangChain 演进发生迁移成本。

### 6.3 LlamaIndex

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 52591（pushed_at=2026-10-21，archived=false） | https://api.github.com/repos/run-llama/llama_index |
| 版本 | 0.14.25（2026-09-21） | https://api.github.com/repos/run-llama/llama_index/releases/latest |
| 许可证 / Python | MIT / >=3.10,<4.0 | https://pypi.org/pypi/llama-index/json |

- **定位（判断）**：GitHub 描述原文 "LlamaIndex is the document processing platform for AI"——官方叙事已转向文档处理平台；但内置完整 Agent 运行时（FunctionAgent / AgentWorkflow，官方示例页确认 "The AgentWorkflow is an orchestrator for running a system of one or more agents"，来源：https://developers.llamaindex.ai/python/examples/agent/agent_workflow_basic/ ，页面 2026-10-10 更新）。
- **能力（事实）**：事件驱动 Workflow（start_step/Context/条件流转）；Qwen 官方独立包 `llama-index-llms-dashscope`（PyPI 0.7.0）；DeepSeek/GLM 经 OpenAI 兼容端点（OpenAILike）。
- **风险（判断）**：umbrella 主包仍 0.14.x，历史上多次 API 重构（old agent → FunctionAgent）；open issues 1007；Agent 子系统叙事被"文档平台"稀释。

### 6.4 Haystack

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 26800（pushed_at=2026-10-21，archived=false） | https://api.github.com/repos/deepset-ai/haystack |
| 版本 | haystack-ai 3.4.0（2026-10-15；近 10 release 约 2-3 周一版） | https://pypi.org/pypi/haystack-ai/json |
| 许可证 / Python | Apache-2.0 / >=3.11 | 同上 |

- **定位（判断）**：官方描述 "Open-source AI orchestration framework for building context-engineered, production-ready LLM applications"。
- **能力（事实）**：内置 `haystack.components.agents.Agent` 管理完整 tool-calling 循环、state_schema 跨工具类型化数据、流式输出、HITL 确认策略、MCPToolset（来源：https://docs.haystack.deepset.ai/docs/next/agents ）；Pipeline 显式 DAG；RAG 组件化（Document Store/Retriever/Ranker/PromptBuilder/Generator）；DeepSeek/Qwen/GLM 经 OpenAI 兼容端点（官方 DeepSeek 教程：https://haystack.deepset.ai/blog/use-deepseek-with-haystack ）。
- **风险（判断）**：2.x→3.x 有 Migration Guide（https://docs.haystack.deepset.ai/docs/migration ）；Agent hooks/skills 高阶页仍标 next/experimental；国产模型无独立官方包，须自封装兼容接入。

### 6.5 CrewAI

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 59942（pushed_at=2026-10-21，archived=false） | https://api.github.com/repos/crewAIInc/crewAI |
| 版本 | 1.15.28（2026-10-14；近 30 天 ≥5 个 patch） | https://pypi.org/pypi/crewai/json |
| 许可证 / Python | MIT / >=3.10,<3.14 | 同上 |

- **定位（判断）**：官方描述 "Framework for orchestrating role-playing, autonomous AI agents"；Crew（团队抽象）+ Flows（应用骨架）分层互补（官方 first-flow 文档原话：combine crews/direct LLM calls/regular code，来源：https://docs.crewai.com/v1.14.5/en/guides/flows/first-flow ）。
- **能力（事实）**：Crew sequential/hierarchical 流程；Flows `@start`/`@listen`/`@router` 事件驱动状态机；短期/长期/实体三类记忆；内置 Knowledge 模块；国产模型经 LiteLLM 前缀封装（`deepseek/deepseek-chat`、`qwen/...`、`zhipuai/...`，CrewAI 自身不维护国产 SDK，来源：https://docs.crewai.com/en/concepts/llms.md ）。
- **风险（判断）**：API 随版本演进较快（一周多 patch）；与 LiteLLM 强耦合；闭源 Enterprise/Embedded 与开源版边界需关注。

### 6.6 microsoft/autogen（已归档）

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 61504（GitHub archived 字段=false，但 README 顶部红色 Archived 徽章 + CAUTION 声明 "Project archived and no longer maintained"） | https://raw.githubusercontent.com/microsoft/autogen/main/README.md |
| 版本 | python-v0.7.5（2025-09-30 发布，近 12 个月无新 release；最近 push 2026-10-16 为归档说明 docs 提交） | https://api.github.com/repos/microsoft/autogen/releases/latest |
| 许可证 / Python | CC-BY-4.0（GitHub API 探测值，与 0.2 时代 MIT 不一致，**须人工核对仓库根 LICENSE**）/ >=3.10 | https://api.github.com/repos/microsoft/autogen |

- **定位（事实+判断）**：官方描述 "A programming framework for agentic AI"；现状仅适合历史代码维护，README 原文警告"vulnerabilities may remain unaddressed"，引导新用户使用 MAF（迁移指南：https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/ ）。
- **能力（事实）**：0.4+ event-driven runtime（autogen-core）+ agentchat 高层层；GroupChat/Swarm/Sequential 拓扑；FunctionTool/MCP。
- **风险（判断）**：**维护风险极高——官方明确不再提供 bug fix、安全修复、新功能**；新项目选型直接排除。

### 6.7 ag2ai/ag2（AutoGen 社区 fork）

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 5008（pushed_at=2026-10-20，archived=false；仓库 created_at=2024-11-11） | https://api.github.com/repos/ag2ai/ag2 |
| 版本 | GitHub v1.2.0（2026-10-11，周级节奏）；PyPI ag2 1.1.2（落后于 GitHub） | https://pypi.org/pypi/ag2/json |
| 许可证 / Python | Apache-2.0 / >=3.10 | 同上 |

- **定位（判断）**：README 自述 "AG2 (formerly AutoGen): The Open-Source AgentOS"；继承 AutoGen 0.2 时代 ConversableAgent/GroupChat 经典 API（归入 "AG2 Classic"），v1.0 起叠加新协议层 runtime。
- **能力（事实）**：GroupChat/Swarm/Sequential/Magentic-One 经典拓扑；FunctionTool/MCP；国产模型经 OAI_CONFIG_LIST `api_type=openai` + base_url。
- **风险（判断）**：stars 仅 5k 量级，与微软官方资源不对等；路线与 MAF 分叉（社区开源 vs 企业级 LTS）；适合存量 AutoGen 0.2 用户过渡，不建议新项目押注。

### 6.8 Microsoft Agent Framework (MAF)

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 14244（pushed_at=2026-10-21，archived=false；仓库 2025-04-28 创建，18 个月达此量级） | https://api.github.com/repos/microsoft/agent-framework |
| 版本 | agent-framework 1.22.0（2026-10-15；近 30 天 Python 1.20.0→1.21.0→1.22.0 周级；.NET 1.25.0 并行） | https://pypi.org/pypi/agent-framework/json |
| 许可证 / Python | MIT / >=3.10 | 同上 |

- **定位（事实+判断）**：README 原文 "an open, multi-language framework for building production-grade AI agents and multi-agent workflows in .NET and Python"。**关系核实（事实）**：微软 DevBlogs 2025-10-07 原文 "Microsoft Agent Framework is the successor to Semantic Kernel... It builds upon the foundations laid by Semantic Kernel and AutoGen"（来源：https://devblogs.microsoft.com/semantic-kernel/semantic-kernel-and-microsoft-agent-framework/ ）；MS Learn 原文 "Agent Framework combines the Semantic Kernel and AutoGen orchestrators into one single orchestrator"。
- **能力（事实）**：图式编排 sequential/concurrent/handoff/group collaboration；中间件管道；durability/restartability 持久化重启；MCP/A2A；DeepSeek/Qwen 经 Azure Foundry Models 官方托管（来源：https://learn.microsoft.com/en-us/azure/foundry/foundry-models/tutorials/get-started-deepseek-r1 ）+ 兼容层。
- **风险（判断）**：1.x 周级迭代 API 可能变动；与 Azure Foundry/Azure OpenAI 生态耦合深，纯本地/非云场景价值打折；`agent-framework-azure-ai` 仍 1.0.0rc6。

### 6.9 OpenAI Swarm（已停演进）

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 22065（archived=false；pushed_at=2026-04-15 仅为 pre-commit hook pin 提交） | https://api.github.com/repos/openai/swarm |
| 版本 | openai-swarm 0.1.1 PyPI（author=OpenAI Solutions）；**从未发布 GitHub Release**（/releases/latest 404） | https://pypi.org/pypi/openai-swarm/json |
| 许可证 / Python | MIT / >=3.10 | https://raw.githubusercontent.com/openai/swarm/main/README.md |

- **定位（事实）**：README 标题原文 "Swarm (experimental, educational)"；仅 Agent + handoff 两原语、无状态。**取代关系（事实）**：README 顶部 `> [!IMPORTANT]` 块原文 "Swarm is now replaced by the OpenAI Agents SDK... We recommend migrating to the Agents SDK for all production use cases."（来源：https://raw.githubusercontent.com/openai/swarm/main/README.md ）；2025-03-11 三连 commit "point to Agents SDK"。
- **能力（事实）**：handoff 对话路由；完全基于 OpenAI Chat Completions API；无持久化。
- **风险（判断）**：实际活跃度≈0（open_issues 39 长期未处理）；仅作 handoff 模式教学参考，生产场景一律走 Agents SDK。

### 6.10 OpenAI Agents SDK

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 30192（pushed_at=2026-10-20，archived=false） | https://api.github.com/repos/openai/openai-agents-python |
| 版本 | openai-agents 0.24.0（2026-10-15；PyPI 累计 124 个 release） | https://pypi.org/pypi/openai-agents/json |
| 许可证 / Python | MIT / >=3.10 | 同上 |

- **定位（事实+判断）**：README 原文 "a lightweight yet powerful framework for building multi-agent workflows. It is provider-agnostic, supporting the OpenAI Responses and Chat Completions APIs, as well as 100+ other LLMs"；Swarm 的生产级演进。
- **能力（事实）**：Agents as Tools / Handoffs / Guardrails / Sessions（自动跨运行会话历史管理）/ Human-in-the-loop / Tracing；官方专门概念含 realtime agents、voice agents、sandbox agents；国产模型走兼容层。
- **风险（判断）**：Tracing/Realtime/Voice 增值能力深绑 OpenAI 后端；0.x 版本号 API 仍小步演进；第三方模型上 Responses 高级特性行为可能不一致。

### 6.11 PydanticAI

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 20764（pushed_at=2026-10-21，archived=false） | https://api.github.com/repos/pydantic/pydantic-ai |
| 版本 | pydantic-ai 2.59.0（2026-10-21 即抓取当日上传；PyPI 累计 351 个 release） | https://pypi.org/pypi/pydantic-ai/json |
| 许可证 / Python | MIT / >=3.11 | 同上 |

- **定位（判断）**：官方描述 "How Python does AI. Agents, realtime voice, image generation, embeddings. Every model, every interface, typed end to end."；强绑定 Pydantic v2（pydantic-ai-slim requires_dist 含 `pydantic>=2.12`，来源：https://pypi.org/pypi/pydantic-ai-slim/json ）。
- **能力（事实）**：国产模型原生四件套——DeepSeek `Agent('deepseek:deepseek-v4-flash')`（docs/models/deepseek.md）、GLM `Agent('zai:glm-5')`（docs/models/zai.md，需 `pydantic-ai-slim[zai]`）、Qwen `alibaba:` 前缀（DashScope）、Moonshot 原生；20+ provider 目录；配套 pydantic-graph 提供图编排。
- **风险（判断）**：强绑 Pydantic v2 且 Python 门槛 >=3.11；版本迭代极快（351 release）；open issues 1563 工单量大。

### 6.12 SmolAgents

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 29956（pushed_at=2026-10-06，archived=false） | https://api.github.com/repos/huggingface/smolagents |
| 版本 | smolagents 1.26.0（2026-05-29 上传，距今约 5 个月；PyPI 累计 41 个 release） | https://pypi.org/pypi/smolagents/json |
| 许可证 / Python | Apache-2.0 / >=3.10 | 同上 |

- **定位（事实）**：README 原文 "a barebones library for agents that think in code"；核心逻辑约 1000 行；**CodeAgent 一等设计**——智能体写 Python 代码调用工具，支持 Blaxel/E2B/Modal/Docker 沙箱。
- **能力（事实）**：CodeAgent + ToolCallingAgent 双执行体；ManagedAgent 分层多 agent；Hub 工具共享 + MCP server 工具接入；model-agnostic（本地 TransformersModel/Ollama/HF Inference Providers/OpenAI/Anthropic/LiteLLM 100+ provider）；国产模型经 LiteLLM/Inference Providers 兼容层。
- **风险（判断）**：最新 release 距今约 5 个月，发版节奏明显慢于同代（openai-agents 6 天前、pydantic-ai 当天）；薄抽象意味着生产级持久化/检查点需自行加固；open issues 982。

### 6.13 transformers.agents（迁移记录，表外框架）

| 字段 | 值 | 来源 |
|---|---|---|
| 主仓 Stars | 167937（huggingface/transformers，v5.20.2 发布于 2026-10-19，pushed_at=2026-10-21） | https://api.github.com/repos/huggingface/transformers |
| 模块现状 | v5.20.2 tag 下 `src/transformers/` 目录中**已不存在** `*agent*` 条目（contents API 实测） | https://api.github.com/repos/huggingface/transformers/contents/src/transformers?ref=v5.20.2 |
| 许可证 / Python | Apache-2.0 / >=3.10.0 | https://pypi.org/pypi/transformers/json |

- **关系核实（事实）**：HF 官方博客原文 "smolagents is the successor to transformers.agents, and will be replacing it as transformers.agents gets deprecated in the future."（来源：https://hf.co/blog/smolagents ）。
- **风险（判断）**：旧代码 `from transformers import CodeAgent, HfAgent` 在 v5 已失效，须改 `pip install smolagents`；升级 transformers 4.x→5.x 需人工适配导入路径（无完整一对一替换表）；smolagents 与 transformers 版本耦合需对齐。

### 6.14 Agno

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 42850（pushed_at=2026-10-21，archived=false） | https://api.github.com/repos/agno-agi/agno |
| 版本 | agno 3.1.7（2026-10-20 上传，与 GitHub release 同版本） | https://pypi.org/pypi/agno/json |
| 许可证 / Python | Apache-2.0 / >=3.9,<4 | 同上 |

- **定位（判断）**：官方描述 "Build, run, and manage agent platforms"；纯 Python、无图/链抽象，正向 AgentOS/Studio 平台演进；**更名史（事实）**：2025-01-29 官方博客《Phidata is now Agno》，PyPI 包由 `phidata` 更名 `agno`，import 根由 `phi.*` 改 `agno.*`（来源：https://www.agno.com/blog/introducing-agno ）。
- **能力（事实）**：Teams 模块 coordinate/route/broadcast 三种委托模式、支持嵌套（来源：https://docs.agno.com/teams/overview ）；provider 原生面含 DeepSeek/DashScope(Qwen)/Moonshot/InternLM/MiniMax/小米 MiMo，**无 Zhipu/GLM 原生条目**，GLM 走 OpenAI 兼容层（来源：https://docs.agno.com/models/providers/model-index ）；官方 Database/Memory/Knowledge 章节。
- **风险（判断）**：v1→v3 间有破坏性变更历史；open issues 1926 较多；无显式状态图/检查点原语，复杂长流程可恢复性弱于图式框架。

### 6.15 Semantic Kernel (Python)

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 28681（pushed_at=2026-10-21，archived=false；monorepo .NET+Python+Java） | https://api.github.com/repos/microsoft/semantic-kernel |
| 版本 | semantic-kernel 1.45.0（2026-10-06 上传，约每月一版）；.NET dotnet-1.81.0 同日发布——**Python 版本号显著落后 .NET** | https://pypi.org/pypi/semantic-kernel/json |
| 许可证 / Python | MIT / >=3.10 | 同上 |

- **定位（判断）**：PyPI 自述 "Flexible Agent Framework: build, orchestrate, and deploy AI agents and multi-agent systems"；企业 SDK 级集成（Plugin/OpenAPI/MCP 扩展）。
- **能力（事实）**：Python 提供 ChatCompletionAgent/GroupChatOrchestration/RoundRobinGroupChatManager/InProcessRuntime，但官方文档明确 "Agent Orchestration features... are in the experimental stage"（来源：https://learn.microsoft.com/en-ca/semantic-kernel/frameworks/agent/agent-orchestration/ ）；DeepSeek 经 OpenAI connector 改 base_url（官方博客：https://devblogs.microsoft.com/semantic-kernel/using-deepseek-models-in-semantic-kernel/ ）。
- **风险（判断）**：官方正引导用户迁往 MAF（2026-01 官方博客：https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/ ）；Python 多智能体"有 API、实验性、迁移中"；无可视化工作流画布。

### 6.16 Mastra（Python 选型排除）

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 28972（pushed_at=2026-10-21，archived=false） | https://api.github.com/repos/mastra-ai/mastra |
| 版本 | @mastra/core@1.78.0（2026-10-16，npm monorepo scoped 包） | https://api.github.com/repos/mastra-ai/mastra/releases/latest |
| Python 现状 | **无官方 Python 包**：`mastra`/`mastra-ai`/`mastra-py`/`mastra-python` PyPI 均 404；languages API 实测 TypeScript 132MB、**Python 字节=0** | https://pypi.org/pypi/mastra/json ；https://api.github.com/repos/mastra-ai/mastra/languages |

- **定位（事实）**：GitHub 描述原文 "Mastra is the modern TypeScript framework for AI-powered applications and agents"。
- **风险（事实+判断）**：唯一同名候选 `pymastra` v0.5.0（2026-04-11 上传）summary 自述 "Inspired by Mastra (TypeScript)"，project_urls 全部指向 `github.com/YOUR_USERNAME/pymastra` 占位符、author 为空——非官方、不具备生产可信度（来源：https://pypi.org/pypi/pymastra/json ）；许可证 Apache-2.0 开源部分 + `ee/` 目录独立 ee/LICENSE 企业版双授权。**结论：对 Python 选型不适用，仅 TS/全栈 JS 技术栈场景进入候选。**

### 6.17 Dify（低代码平台参照）

| 字段 | 值 | 来源 |
|---|---|---|
| Stars | 159105（pushed_at=2026-10-21，archived=false；本组最高量级） | https://api.github.com/repos/langgenius/dify |
| 版本 | 1.17.1（2026-09-10）；官方 Python SDK dify-client 0.1.10 停更于 2023-11-15 | https://pypi.org/pypi/dify-client/json |
| 许可证 | **Apache-2.0 修改版**（"Dify Open Source License"：未经书面授权不得用于多租户服务；前端不得移除 LOGO 与版权信息） | https://github.com/langgenius/dify/blob/main/LICENSE |

- **定位（判断）**：低代码 Agentic 工作流平台，**非纯 Python 框架**——核心能力经 Web 画布与配置完成；外部集成主路径为 Service-API REST，不存在"作为库被 import"的主用法。
- **能力（事实）**：可视化 Workflow 编辑器 + Agent runtime；国产模型原生插件——DeepSeek 官方插件约 175.6 万安装、GLM(ZHIPU AI) 官方插件约 18.6 万安装、Qwen 插件由 Dify 官方维护（来源：Dify Marketplace 页面 web_fetch，2026-10-21；https://marketplace.dify.ai/?category=model ；https://help.aliyun.com/zh/model-studio/dify ）。
- **风险（判断）**：多租户 SaaS 化与前端 LOGO 移除需商业授权，商用前逐条核对 LICENSE；dify-client 停更 3 年+，SDK 生态缺位；平台本体多容器运维对纯代码团队偏重。

---

## 七、风险与注意点

| # | 风险 | 等级 | 依据（事实，2026-10-21） | 缓解（判断） |
|---|---|---|---|---|
| R-1 | 框架生态锁定 | 高 | LangChain 深度绑定 LCEL/LangSmith；MAF 绑定 Azure Foundry/Azure OpenAI；OpenAI Agents SDK 的 Tracing/Realtime 依赖 OpenAI 后端；PydanticAI 强绑 Pydantic v2（>=3.11） | 选型时同步设计"模型 provider 可替换层"；关键业务逻辑保持纯 Python，框架层薄封装 |
| R-2 | 维护停演进（实证） | 高 | microsoft/autogen 已归档（v0.7.5 停在 2025-09-30，README CAUTION 不再修安全漏洞）；Swarm 被 Agents SDK 取代（2024-10 后无功能提交）；transformers.agents 已从 v5 主包移除 | 新项目一律避开三者；存量项目按官方迁移路径走（AutoGen→MAF、Swarm→Agents SDK、transformers.agents→smolagents） |
| R-3 | 许可证合规 | 中高 | Dify 为 Apache-2.0 修改版（多租户/LOGO 限制）；AutoGen GitHub API 探测为 CC-BY-4.0（与 0.2 时代 MIT 不一致）；Mastra Apache-2.0 + ee/ 双许可 | 商用前逐条核对仓库根 LICENSE 原文；AutoGen 若必须维护存量，先人工确认 LICENSE 归属（Q-4） |
| R-4 | 大版本迁移成本 | 中高 | LangChain 主包 0.3→1.0 跳过 0.4 稳定线（1.0.0=2025-10-17）；Haystack 2.x→3.x 需 Migration Guide；LlamaIndex umbrella 仍 0.14.x 多次重构；Agno 2025-01 刚完成 phidata→agno 命名空间迁移 | 新项目订阅 changelog、锁定当前 1.x API；TCO 中预留大版本迁移工时 |
| R-5 | 无目标语言包误用 | 中 | Mastra 无官方 Python 包（PyPI 404、Python 字节=0）；pymastra 为 YOUR_USERNAME 占位社区包 | Python 团队直接排除；TS 团队才纳入候选 |
| R-6 | 官方 SDK 停更 | 中 | Dify dify-client 0.1.10 停更于 2023-11-15 | 集成走 Service-API REST，不依赖 SDK 稳定性；关注插件/Endpoint serverless 演进 |
| R-7 | 版本节奏过快引入漂移 | 中 | CrewAI 近 30 天 5 个 patch；PydanticAI PyPI 累计 351 个 release、open issues 1563；MAF 周级双语言发版 | 固定次要版本区间（如 `~=2.59`）；升级前读 changelog breaking changes |
| R-8 | 发版放缓观察位 | 中 | smolagents 最新 release 2026-05-29（距今约 5 个月），pushed_at 2026-10-06 | 生产关键路径降级为观察位；若 6 个月内无 1.27.x 则评估替换 |

---

## 八、洞察（I 阶段·四元组）

### 洞察 1：维护活跃度与 Stars 量级脱钩——高星≠在维护

- **陈述**：2026 年选型中，GitHub Stars 排行榜前几名恰恰是停演进框架；真正活跃的新框架 Stars 量级小一个数量级。
- **证据**：microsoft/autogen 61504 stars 但 README 声明归档、v0.7.5 停在 2025-09-30（https://raw.githubusercontent.com/microsoft/autogen/main/README.md ）；Swarm 22065 stars 但 2024-10 后无功能提交（https://api.github.com/repos/openai/swarm/commits?per_page=5 ）；而 MAF 仅 14244 stars 却 Python 端周级发版（1.20.0/10-02→1.21.0/10-08→1.22.0/10-15，https://api.github.com/repos/microsoft/agent-framework/releases?per_page=6 ）。
- **反常识**：选型文章常按 Stars 排名介绍框架，但 Stars 是历史贡献的累积资产，与"未来 12 个月是否继续修安全漏洞"完全无关——61.5k Stars 的 AutoGen 官方原文警告"vulnerabilities may remain unaddressed"。
- **行动**：选型第一步查 pushed_at、最新 release 日期、README 顶部徽章，**不看 Stars 排名表**；把维护筛放在类型筛之前或同等位置。

### 洞察 2：国产模型支持分"原生 provider 页"与"兼容层"两档，且已成头部框架标配分化点

- **陈述**：接入国产模型已不稀罕，稀罕的是"官方 provider 文档页 + 原生参数对齐"；2026 年头部框架在这一项上明显分化，且需拆两档——"框架原生 provider 页"与"LiteLLM/兼容前缀封装"不是一回事。
- **证据**：原生 provider 页档——PydanticAI 有 DeepSeek/Z.AI(GLM)/Alibaba(Qwen)/Moonshot 独立 provider 文档页（https://github.com/pydantic/pydantic-ai/tree/main/docs/models ）；Agno 原生 DeepSeek/DashScope/Moonshot/InternLM/MiniMax/MiMo（https://docs.agno.com/models/providers/model-index ）。前缀封装档——CrewAI 的 `deepseek/`/`qwen/`/`zhipuai/` 前缀本质是 LiteLLM 薄封装，CrewAI 自身不维护国产模型 SDK（https://docs.crewai.com/en/concepts/llms.md ）。纯兼容层档——Haystack（OpenAIChatGenerator 改 base_url）、Semantic Kernel（OpenAI connector 改 base_url）、OpenAI Agents SDK（README provider-agnostic 但国产无 provider 页）。MAF 单列：DeepSeek/Qwen 支持本质是 Azure Foundry **云托管**，直连国产官方 API 仍走 OpenAI 兼容 base_url。
- **反常识**：2024 年"能接 DeepSeek"还是卖点；2026 年真正的分界线是"国产模型出现在官方 provider 目录第几行、有没有官方文档页"——没有官方页意味着函数名对齐、结构化输出、错误重试都要自己踩坑；而 CrewAI 这类"前缀即原生"的表述，实际只是 LiteLLM 封装的糖。
- **行动**：需求写清"原生体验 vs 可用即可"；选兼容层框架时预留国产模型联调工时，优先选有官方兼容教程的（如 Haystack DeepSeek 博客教程）；看到"原生"字样时先查证是"仓库 docs 下有独立 provider 页"还是"LiteLLM 前缀"。

### 洞察 3：停演进的官方信号不是"静音"，而是"README 被替换成迁移指引"

- **陈述**：三个停演进案例（AutoGen/Swarm/transformers.agents）的共同模式是：仓库未删、GitHub archived 字段未必为 true，但官方把 README 顶部改成了"迁移到继任者"的告示。
- **证据**：AutoGen README 红色 Archived 徽章 + CAUTION 块引导 MAF；Swarm README `> [!IMPORTANT]` 块 + 2025-03-11 三连 commit "point to Agents SDK"；transformers.agents 在 v5.20.2 源码目录中实测消失、HF 博客明示 smolagents 继任（https://hf.co/blog/smolagents ）。
- **反常识**：GitHub 的 `archived` 字段不可靠——微软归档 AutoGen 时 API 探测 archived=false，OpenAI 停 Swarm 时 archived=false；只查 archived 字段会误判"活跃"。
- **行动**：维护状态判定三查——README 顶部徽章、最近 5 个 commit 的内容性质（是功能提交还是"更新迁移指针"）、关键模块在当前 tag 下是否还存在（contents API 实测）。
- **事前预警信号清单（不等归档，先避险）**：上述都是事后信号（归档当天才有 README 徽章）；要回答"我现在选的 X 一年后会不会变成下一个 AutoGen"，须提前监测：① 近 3 个月 release 中 `docs`/`chore` 类提交占比 >50%，功能提交断流；② 核心维护者 commit 频率持续下降（对比近 6 个月 vs 之前 6 个月）；③ 官方博客/DevBlogs 提前转向新框架——**微软 2024-11 即宣布 AutoGen 与 SK 对齐，2025-10 正式合并为 MAF，2026 才归档 AutoGen README，战略转向早于归档约 1 年**；④ open issue 平均响应时长持续拉长、社区 PR 合并停滞。出现 ①+③ 组合即应启动迁移预案，不等 README 徽章出现。

### 洞察 4：版本号跳跃是隐形成本，"高版本"不等于"已稳定"

- **陈述**：主流框架在 2025-2026 经历了一轮大版本重排，版本号演进路径充满跳跃与绕路。
- **证据**：LangChain 主包 0.3（2024-09-13）直接跳 1.0.0（2025-10-17），0.4 线仅有预发布 0.4.0.dev0、从无稳定 0.4.x（https://pypi.org/pypi/langchain/json releases 时间戳）；Haystack 2.x→3.x 配 Migration Guide（https://docs.haystack.deepset.ai/docs/migration ）；LlamaIndex umbrella 仍 0.14.x；Agno 2025-01 完成 phidata→agno 命名空间迁移（https://www.agno.com/blog/introducing-agno ）；Semantic Kernel Python 1.45.0 落后 .NET 1.81.0 近 36 个 minor 版本。
- **反常识**：选型时倾向"选最高版本号/最新主版本"，但 LangChain 跳过的 0.4 稳定线说明版本号编排本身可以是跳跃的；0.14.x 的 LlamaIndex 与 1.22.0 的 MAF，稳定性未必与版本号成正比。
- **行动**：看"近 12 个月发版节奏 + breaking change 记录"而非版本号大小；新项目锁当前稳定线，存量项目把大版本迁移工时计入 TCO。

> **G2 检验（自检）**：4 条洞察（≥3 ✅）｜四元组（陈述/证据/反常识/行动）完整 ✅｜维度不重叠（维护-Stars / 国产支持档 / 停演进信号 / 版本迁移）✅｜每条证据均落在事实表数据与 URL 上 ✅｜均有可执行行动 ✅。

---

## 九、待验证清单（Open Questions）

| # | 待验证项 | 验证方式 |
|---|---|---|
| Q-1 | MAF 1.x 周级迭代何时收敛；非 Azure 场景（纯 OpenAI/本地模型）生产可靠性；`agent-framework-azure-ai` 仍 1.0.0rc6 的转正时间 | 跟踪 devblogs.microsoft.com/agent-framework；PoC 纯本地 provider 场景 |
| Q-2 | Semantic Kernel Python 多智能体（experimental）何时正式转入 MAF；SK Python 线的维护窗口与 EOL 承诺 | Microsoft Learn 迁移指南更新；官方 blog 路线图 |
| Q-3 | dify-client 停更（2023-11）后的集成路径：Service-API REST 稳定性、插件/Endpoint serverless 能力边界 | 自托管 Dify 实测 Service-API；关注 changelog |
| Q-4 | microsoft/autogen 仓库根 LICENSE 原文核对（GitHub API 探测 CC-BY-4.0 vs 0.2 时代 MIT），存量合规使用前必须人工确认 | 下载仓库根 LICENSE 原文核对 |
| Q-5 | smolagents 发版放缓（v1.26.0 距今约 5 个月）是否影响生产可靠性；pushed_at（2026-10-06）与发版节奏背离的原因 | 跟踪 GitHub releases 与 changelog；观察 2026Q4 是否补发版 |
| Q-6 | AG2 社区（5k stars）长期可持续性；与 MAF 分叉后维护资源是否会枯竭 | 跟踪 ag2ai/ag2 release 节奏与 core contributors 构成 |
| Q-7 | CrewAI Enterprise/Embedded 闭源边界对开源版路线图的影响（开源功能是否被逐步上收） | 对比 open-source changelog 与 Enterprise 功能页 |
| Q-8 | kimi-webbridge 扩展恢复后，对 Dify Marketplace 安装量、各框架文档站结构做浏览器层复核 | 浏览器实测（本报告 2.3 节已披露未执行） |
| Q-9 | **Google ADK（`google/adk-python`）纳入对比评估**——三巨头中 Google 官方 Python agent 框架（A2A 协议/Gemini 生态）本次未抓取，需按同一事实表方法（GitHub API/PyPI/官方文档，2026-10-21 抓取口径）补抓并补入对比表与分场景推荐 | 补抓事实表 + 更新本报告对比表（本报告未对 ADK 做任何数值陈述，无编造） |

---

## 十、对抗审查记录（V 门）

> 审查日期 2026-10-21；四视角（🔴魔鬼代言人 / 🟢新人 / 🟠老板 / 🔵未来）全覆盖；共 13 条意见（P0×3 / P1×4 / P2×4 / P3×2），数值层核对全部忠实于事实表。

| # | 视角 | 意见摘要 | 处置 |
|---|---|---|---|
| A1 | 🔴魔鬼（P0） | Dify Marketplace 安装量来源自相矛盾（§2.3 未浏览器实测 vs §6.17 精确到个位） | **已采纳**：§2.2 补"Dify Marketplace 页面（web_fetch，2026-10-21）"数据源类；GLM 数字改为量级表述"约 18.6 万"；§2.3 同步补注；G1 记录同步改口径 |
| A2 | 🟠老板（P0） | 标题"16 框架横向对比"夸大，#6/#9/#15/#16 实为排除项/参照项 | **已采纳**：标题与 frontmatter title 改为"11 个候选框架 + 5 个排除项/参照项"；§四表顶加候选 vs 排除/参照分组说明行 |
| A3 | 🔴魔鬼（P0） | 国产模型"原生"口径错位：CrewAI=LiteLLM 薄封装、MAF=Azure 云托管，均非框架原生 | **已采纳**：表 #5 改"LiteLLM 前缀封装——兼容前缀档"；表 #8 改"Azure Foundry 云托管（云耦合）/ 直连国产 API 走兼容层"；§5.1 第②步拆两档重写；洞察 2 同步修正 |
| A4 | 🔴魔鬼/🔵未来（P1） | 重大遗漏 Google ADK（google/adk-python），三巨头缺 Google | **已采纳**：§四顶部加范围说明（未纳入对比、如需可补抓、不编造任何 ADK 数值）；§九加 Q-9 |
| A5 | 🟢新人（P1） | PydanticAI 首选理由未前置 Python ≥3.11 门槛与 open issues 1563 | **已采纳**：§1.1 首选理由末尾加注 |
| A6 | 🔴魔鬼/🔵未来（P1） | 4 条洞察全是事后诸葛亮，缺事前避雷信号 | **已采纳**：洞察 3 末尾补"事前预警信号清单"（docs/chore 占比、维护者提交频率、官方博客提前转向——微软 2024-11 宣布对齐早于归档约 1 年） |
| A7 | 🔴魔鬼（P1） | SmolAgents 成熟度三处口径不一致（表"中高"/6.12"节奏慢"/R-8"低风险"） | **已采纳**：表 #12 改"中（发版放缓观察位）"；R-8 风险等级低→中 |
| A8 | 🟢新人（P2） | 决策路径未落到"第一行 pip install" | **已采纳**：§5.1.1 加"30 分钟 PoC 最短路径"表（PydanticAI/CrewAI/LangGraph 各一行命令 + hello world 要点） |
| A9 | 🔴魔鬼（P2） | openai-swarm PyPI 包 vs README git+https 安装路径矛盾未点破 | **已采纳**：表 #9 版本列补"README 实际推荐 git+https 安装，PyPI 非主推路径" |
| A10 | 🟠老板（P2） | MAF 商用次选的未收敛风险藏在 Q-1，未前置到执行摘要 | **已采纳**：§1.2 MAF 行理由末尾加注（1.x 周级迭代、azure-ai 仍 rc、须预留收敛期） |
| A11 | 🔵未来（P2） | 五筛法语言包筛未覆盖本报告自身 Mastra 教训 | **已采纳**：第 4 步补反例（主语言 Python 但官网主打 JS/TS 时先查 PyPI 官方包存在性，勿凭 stars 跨语言选型） |
| A12 | 🟢新人（P3） | §1.3 排除清单漏列 Dify | **已采纳**：§1.3 补 Dify 条目（低代码平台、非库式框架、代码级自研不进入候选） |
| A13 | 🔴魔鬼（P3） | 表 #5 CrewAI 许可证未标开源/闭源双轨 | **已采纳**：表 #5 许可证改"MIT（开源版；Enterprise/Embedded 闭源另售）" |

---

## 十一、质量门记录

| 质量门 | 结果 | 说明 |
|---|---|---|
| G1 事实门 | 通过 | 16 份事实表（15 份框架事实表 + LangGraph 种子）全部实时抓取自 GitHub API/PyPI JSON/官方文档（2026-10-21），每条事实带 URL，无因果词，争议项均以官方原文核实；**Dify Marketplace 安装量经 web_fetch 页面抓取（2026-10-21），已在 §2.2 补记数据源类，GLM 数字改为量级表述**；kimi-webbridge 未执行已在 2.3 节如实披露 |
| G2 洞察门 | 通过（本阶段自检） | 4 条四元组洞察（维护-Stars 脱钩 / 国产支持两档 / 停演进信号模式 / 版本号跳跃），维度独立，证据全部落在事实表数据上，均有行动 |
| G3 模式门 | 通过（本阶段自检） | `pat-py-agent-framework-five-filter-001`「Python 智能体框架五筛法」：触发/不适用边界 + 7 步 + 5 个反模式（≥3）+ 检验标准五问 + 跨域迁移示例（RAG 引擎选型/低代码平台选型）；成熟度标 L1 待第二案例验证 |
| V 门 | 通过 | 四视角全覆盖，13 条意见（P0×3 / P1×4 / P2×4 / P3×2）全部采纳并落文；数值层核对确认全部忠实于事实表 |
| 落盘前三查 | 通过 | 目标目录在根 `docs/` 下（`docs/retrospective/reports/competitive-analysis/`）；同类产物体例参照 retrospective-atomgit-selection-evaluation-20260928；路径规则取自磁盘 AGENTS.md 原文（禁止 `.agents/docs/`）；交叉引用使用相对路径，无 `file:///` |

> **一句话结论**：个人项目从 **PydanticAI**（国产原生 + typed）或 **CrewAI**（最低上手门槛）起步；商业化生产以 **LangGraph** 为通用首选、**MAF** 为微软/Azure 栈首选；**AutoGen/Swarm/transformers.agents 停演进实证**、**Mastra 无 Python 包**，四者不进入新项目候选；选型前务必先做维护筛（pushed_at + README 徽章 + 模块存在性三查），而非看 Stars 排名。

---

## 参考来源（按框架分组，已去重）

- **公共数据源**：GitHub REST API（`api.github.com/repos/<owner>/<repo>`）、PyPI JSON API（`pypi.org/pypi/<package>/json`），抓取日期 2026-10-21。
- **LangChain**：https://api.github.com/repos/langchain-ai/langchain ；https://pypi.org/pypi/langchain/json ；https://pypi.org/pypi/langchain-core/json ；https://docs.langchain.com/oss/python/integrations/chat/deepseek ；https://docs.langchain.com/oss/python/integrations/chat/qwen ；https://docs.langchain.com/oss/python/integrations/chat/zhipuai
- **LangGraph**：https://api.github.com/repos/langchain-ai/langgraph ；https://pypi.org/pypi/langgraph/json ；https://docs.langchain.com/oss/python/integrations/chat/deepseek
- **LlamaIndex**：https://api.github.com/repos/run-llama/llama_index ；https://pypi.org/pypi/llama-index/json ；https://pypi.org/pypi/llama-index-llms-dashscope/json ；https://developers.llamaindex.ai/python/framework/understanding/agent/ ；https://developers.llamaindex.ai/python/examples/agent/agent_workflow_basic/ ；https://help.aliyun.com/zh/model-studio/dashscopellm-in-llamaindex
- **Haystack**：https://api.github.com/repos/deepset-ai/haystack ；https://pypi.org/pypi/haystack-ai/json ；https://haystack.deepset.ai/release-notes/3.0.0 ；https://docs.haystack.deepset.ai/docs/next/agents ；https://docs.haystack.deepset.ai/docs/migration ；https://haystack.deepset.ai/blog/use-deepseek-with-haystack
- **CrewAI**：https://api.github.com/repos/crewAIInc/crewAI ；https://pypi.org/pypi/crewai/json ；https://docs.crewai.com/en/concepts/llms.md ；https://docs.crewai.com/v1.14.5/en/guides/flows/first-flow
- **AutoGen / AG2**：https://api.github.com/repos/microsoft/autogen ；https://raw.githubusercontent.com/microsoft/autogen/main/README.md ；https://pypi.org/pypi/autogen-agentchat/json ；https://api.github.com/repos/ag2ai/ag2 ；https://pypi.org/pypi/ag2/json ；https://raw.githubusercontent.com/ag2ai/ag2/main/README.md ；https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/
- **Microsoft Agent Framework**：https://api.github.com/repos/microsoft/agent-framework ；https://pypi.org/pypi/agent-framework/json ；https://devblogs.microsoft.com/semantic-kernel/semantic-kernel-and-microsoft-agent-framework/ ；https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/using-semantic-kernel-agent-framework ；https://learn.microsoft.com/en-us/azure/foundry/foundry-models/tutorials/get-started-deepseek-r1
- **OpenAI Swarm / Agents SDK**：https://api.github.com/repos/openai/swarm ；https://raw.githubusercontent.com/openai/swarm/main/README.md ；https://pypi.org/pypi/openai-swarm/json ；https://api.github.com/repos/openai/openai-agents-python ；https://pypi.org/pypi/openai-agents/json ；https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md
- **PydanticAI**：https://api.github.com/repos/pydantic/pydantic-ai ；https://pypi.org/pypi/pydantic-ai/json ；https://pypi.org/pypi/pydantic-ai-slim/json ；https://github.com/pydantic/pydantic-ai/tree/main/docs/models ；https://raw.githubusercontent.com/pydantic/pydantic-ai/main/docs/models/deepseek.md ；https://raw.githubusercontent.com/pydantic/pydantic-ai/main/docs/models/zai.md
- **SmolAgents / Transformers Agents**：https://api.github.com/repos/huggingface/smolagents ；https://pypi.org/pypi/smolagents/json ；https://raw.githubusercontent.com/huggingface/smolagents/main/README.md ；https://api.github.com/repos/huggingface/transformers ；https://api.github.com/repos/huggingface/transformers/contents/src/transformers?ref=v5.20.2 ；https://pypi.org/pypi/transformers/json ；https://hf.co/blog/smolagents ；https://huggingface.co/docs/smolagents/v1.22.0/zh/guided_tour
- **Agno**：https://api.github.com/repos/agno-agi/agno ；https://pypi.org/pypi/agno/json ；https://docs.agno.com/models/providers/model-index ；https://docs.agno.com/teams/overview ；https://www.agno.com/blog/introducing-agno
- **Semantic Kernel**：https://api.github.com/repos/microsoft/semantic-kernel ；https://pypi.org/pypi/semantic-kernel/json ；https://pypi.org/project/semantic-kernel/ ；https://learn.microsoft.com/en-ca/semantic-kernel/frameworks/agent/agent-orchestration/ ；https://devblogs.microsoft.com/semantic-kernel/using-deepseek-models-in-semantic-kernel/ ；https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/
- **Mastra**：https://api.github.com/repos/mastra-ai/mastra ；https://api.github.com/repos/mastra-ai/mastra/languages ；https://pypi.org/pypi/mastra/json ；https://pypi.org/pypi/pymastra/json ；https://raw.githubusercontent.com/mastra-ai/mastra/main/LICENSE.md
- **Dify**：https://api.github.com/repos/langgenius/dify ；https://github.com/langgenius/dify/blob/main/LICENSE ；https://pypi.org/pypi/dify-client/json ；https://marketplace.dify.ai/?category=model ；https://help.aliyun.com/zh/model-studio/dify ；https://dify.ai/zh
