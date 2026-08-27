# 宏观与政策环境分析：AI Agent 系统行业（macro.md）

## 核心判断
2025—2026 年，全球 AI Agent 监管从政策原则阶段进入可执行法律阶段，形成三条差异化路径：中国率先建立全球首个智能体专项监管框架并引入召回权；美国以州法为基点形成事实上的联邦标准；欧盟通过 AI 法案的既有框架覆盖 Agent 行为治理。MCP 捐赠给 Linux Foundation 后，由 Anthropic、Block、OpenAI 共同创立的 AAIF 为协议提供中立治理，MCP 已成为连接 AI 模型与工具/数据的通用协议标准。A2A 协议 v1.0 发布后，拥有 150+ 组织支持、Linux Foundation 托管、AWS/Google/Microsoft 深度集成，与 MCP 形成“内部连接 + 跨 Agent 通信”的互补标准栈，在企业软件生态中已形成事实行业标准。

## 关键证据
2026 年 5 月 8 日，国家网信办等三部门联合印发《智能体规范应用与创新发展实施意见》，2026 年 7 月 15 日生效，建立了全球首个针对 AI 智能体的专项监管类别 [1]。
- **三层决策授权框架**：在医疗、交通、媒体、公共安全等敏感领域，智能体必须经过强制备案、部署前测试 [1]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [China Can Recall Your AI Agents. The US Can't Name a Regulator.](https://www.beri.net/article/china-ai-agent-recall-regulation-global-compliance-convergence-enterprise-governance-2026) - Rajesh Beri, July 17, 2026  

# AI Agent 系统行业市场规模（market.md）

## 核心判断
全球 AI Agent 系统市场处于从技术探索到产业落地的转折期。Gartner 以 "AI agent software spending" 口径给出 $864 亿（2025）→ $2,065 亿（2026）的主要规模指标，同比增长 139%；Grand View Research 以 "Agentic AI market" 口径给出 $76 亿（2025）→ $109 亿（2026）的辅助规模指标，同比增长约 43%。Brilo.ai 汇总显示 Grand View Research 的 2026 年 AI agents 市场规模为 $109.1 亿 [2]。两大口径差异来自定义边界不同：Gartner 覆盖更广泛的 AI agent 软件支出，Grand View Research 聚焦更窄的 Agent 软件市场。编码 Agent、企业 Agent 平台、浏览器 Agent 三大细分市场在 2025 年尚未形成可加总的清晰份额，但编码 Agent 已开始规模化变现，企业 Agent 平台处于快速扩张期，浏览器 Agent 仍处早期。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
2. [Agentic AI Statistics & Trends 2026](https://www.brilo.ai/resources/agentic-ai-statistics) — Brilo.ai, June 25, 2026

# AI Agent 系统产业链分析（chain.md）

## 核心判断
AI Agent 产业链可按"基础模型层→框架/平台层→应用层→终端用户"划分为四层，其中 MCP 与 A2A 协议正在成为跨层互操作基础设施：MCP 负责 Agent 与工具/数据/API 的连接，A2A 负责不同 Agent 之间的任务委派、结果共享与跨平台协作。当前产业链的关键瓶颈集中在应用层的工具编排与多 Agent 调度：动态工具编排、上下文一致性、成本追踪和生命周期管理仍是生产部署中的主要短板。

---

## 关键证据
LangGraph 的核心定位是复杂 Agent 工作流和精确流程控制。2026 年资料中，LangGraph 常被归为图驱动框架，并用于复杂、可控的多 Agent 协作流程；StackOne 将其列为 11 类 AI Agent 工具中的"AI Agent Frameworks"类别之一 [1]。
应用层是将 Agent 能力封装到具体场景中的终端产品。StackOne 将 AI Agent 工具分为 11 个类别，其中编码 Agent、企业平台、无代码/低代码构建器、可观测性、记忆与向量数据库等均构成应用层或支撑层产品 [1]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. StackOne, "The AI Agent Tools Landscape: 120+ Tools Mapped [2026]", 2026-02-08. https://www.stackone.com/blog/ai-agent-tools-landscape-2026  

# 竞争格局分析（competition.md）

## 核心判断
AI Agent 系统行业在 2026 年正处于**框架整合、协议收敛与平台分层**的 consolidation 阶段。开源框架（LangGraph/CrewAI）与商业平台（OpenAI/Anthropic/Google/Microsoft 原生 SDK）之间的竞争并非零和——框架层持续向独立框架（LangGraph）与厂商原生 SDK（Claude Agent SDK、OpenAI Agents SDK、Google ADK）两极分化，而 MCP/A2A 协议层正在成为跨平台基础设施。厂商生态呈现「双联盟 + 开源第三极」格局：Google+Anthropic 在编码 Agent 与安全合规上占优，Microsoft+OpenAI 在消费触达与企业集成上占优，开源模型（DeepSeek/Meta Llama）在成本敏感型推理中崛起。

## 关键证据
2026 年中期的整合文章显示，AI Agent 框架生态已出现超过 89 个 GitHub 星数超过 1000 的仓库，较 2024 年增长 535% [1]。这一阶段以 LangGraph、CrewAI、AutoGen、Pydantic AI、Smolagents 等独立框架为主导，强调状态管理、工作流编排和工具调用抽象。
MCP（Model Context Protocol）在 2025 年 12 月捐赠给 Linux Foundation，成为跨框架通信协议的标准。整合文章称，MCP 在 2026 年初已实现 9,400+ 公开 server 实现和 9,700 万次月 SDK 下载 [1]。A2A 协议由 Google 发起，整合文章称已有 Salesforce、ServiceNow、Atlassian、SAP 等 50+ 合作伙伴参与 [1]。这两个协议正在取代传统供应商专属 API，成为 Agent 间通信的事实标准层。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [AI Agent Ecosystem Consolidation: Platform Wars, SDK Convergence, and the Path to Infrastructure Standards](https://zylos.ai/research/2026-05-25-ai-agent-ecosystem-consolidation-platform-wars-sdk-convergence/) — Zylos AI, 2026-05-25  

# 重点企业研究：AI Agent 系统五大厂商（companies.md）

## 核心判断
当前 AI Agent 系统竞争格局可概括为"框架生态、编码终端、平台入口、协议开放、企业流程"五条路线并行。LangChain 以图驱动框架和可观测性平台形成 agent engineering 的基础设施层；OpenAI 以 Agents SDK、Codex 和云端沙箱构建原生 Agent 执行路径；Anthropic 以 Claude Code、Claude Agent SDK 和 MCP 集成切入终端 Agent 路线；Google 以 ADK 和 Gemini Enterprise Agent Platform 强化多语言、多云与企业部署；Microsoft 则以 MAF、Copilot Studio、Microsoft 365 Agents SDK 与 A2A 沟通能力锁定企业工作流入口。编码 Agent 层面，Claude Code、OpenAI Codex 和 Cursor 并非完全同质竞争：Claude Code 偏向终端深度控制与 MCP/Skills 扩展，Codex 强调沙箱化、云端执行和 Handoff 编排，Cursor 则更接近 IDE-first 的产品体验，适合连续编码和集成工作流。

## 关键证据
LangChain 的核心定位是 agent engineering 平台，即围绕 Agent 构建、部署、评估和调试形成可复用工具链。其开源栈以 LangChain 和 LangGraph 为基础，LangGraph 通过图结构支持复杂工作流、状态管理、循环、条件路由和多 Agent Handoff [1]。LangSmith 则面向 Agent 的 tracing、evaluation 和调试，配套 LangGraph Engine 可在 Agent trace 中发现问题并提出修复建议 [1]。
商业化上，LangChain 公开披露其完成 1.25 亿美元 Series B 融资，并宣布扩大 Agent engineering 平台，覆盖 LangChain、LangGraph、LangSmith 等组件 [2]。2026 年，LangChain 与 NVIDIA 合作推出企业级 Agentic AI 平台，将 LangSmith 与 NVIDIA Agent Toolkit、NIM、NVIDIA Dynamo 等能力结合，面向生产环境部署 Agent [3]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. LangGraph overview. https://docs.langchain.com/oss/python/langgraph/overview  
2. LangChain raises $125M to build the platform for agent engineering. https://blog.langchain.com/series-b/  
3. LangChain Announces Enterprise Agentic AI Platform Built with NVIDIA. https://www.langchain.com/blog/nvidia-enterprise
