# 重点企业研究：AI Agent 系统五大厂商

## 核心判断

当前 AI Agent 系统竞争格局可概括为"框架生态、编码终端、平台入口、协议开放、企业流程"五条路线并行。LangChain 以图驱动框架和可观测性平台形成 agent engineering 的基础设施层；OpenAI 以 Agents SDK、Codex 和云端沙箱构建原生 Agent 执行路径；Anthropic 以 Claude Code、Claude Agent SDK 和 MCP 集成切入终端 Agent 路线；Google 以 ADK 和 Gemini Enterprise Agent Platform 强化多语言、多云与企业部署；Microsoft 则以 MAF、Copilot Studio、Microsoft 365 Agents SDK 与 A2A 沟通能力锁定企业工作流入口。编码 Agent 层面，Claude Code、OpenAI Codex 和 Cursor 并非完全同质竞争：Claude Code 偏向终端深度控制与 MCP/Skills 扩展，Codex 强调沙箱化、云端执行和 Handoff 编排，Cursor 则更接近 IDE-first 的产品体验，适合连续编码和集成工作流。

## 竞争格局矩阵

| 维度 | LangChain | OpenAI | Anthropic | Google | Microsoft |
|---|---|---|---|---|---|
| 核心产品 | LangChain、LangGraph、LangSmith | Agents SDK、Codex、Codex-as-a-Platform | Claude Agent SDK、Claude Code、Claude Desktop、Claude MCP App | ADK、Vertex AI Agent Builder / Gemini Enterprise Agent Platform | MAF、Copilot Studio、Microsoft 365 Agents SDK、Semantic Kernel |
| 架构路线 | 图驱动框架 + 可观测性 | 厂商原生 + 沙箱化执行 + Handoff | 终端 Agent + MCP 集成 | 多语言框架 + 云原生 Agent 平台 | 企业级编排 + 低代码/代理治理 |
| 主要定位 | Agent engineering 平台 | 通用 Agent 平台与编码 Agent | 终端 Agent 与 MCP 生态入口 | 企业级 Agent 平台 | 企业流程 Agent 入口 |
| 开源策略 | LangChain / LangGraph 开源 | Codex harness 开源 | 部分工具链开源 | ADK 等框架开源 | MAF 开源 |
| 编码 Agent | 不主导 | Codex 核心产品 | Claude Code 核心产品 | 通过 ADK 支撑多场景 | 通过 Copilot Studio / Microsoft 365 Agents SDK 切入 |
| 可观测性 | LangSmith Engine 为核心 | Agents SDK harness / workspace agents | Claude Agent SDK 工具链 | Vertex AI Agent Engine / Gemini Enterprise Agent Platform | Copilot Studio agent governance |
| 开放协议 | MCP 等 | MCP | MCP 核心参与方 | A2A / MCP | A2A / MCP |

## 一、LangChain（LangGraph + LangSmith）

LangChain 的核心定位是 agent engineering 平台，即围绕 Agent 构建、部署、评估和调试形成可复用工具链。其开源栈以 LangChain 和 LangGraph 为基础，LangGraph 通过图结构支持复杂工作流、状态管理、循环、条件路由和多 Agent Handoff [1]。LangSmith 则面向 Agent 的 tracing、evaluation 和调试，配套 LangGraph Engine 可在 Agent trace 中发现问题并提出修复建议 [1]。

商业化上，LangChain 公开披露其完成 1.25 亿美元 Series B 融资，并宣布扩大 Agent engineering 平台，覆盖 LangChain、LangGraph、LangSmith 等组件 [2]。2026 年，LangChain 与 NVIDIA 合作推出企业级 Agentic AI 平台，将 LangSmith 与 NVIDIA Agent Toolkit、NIM、NVIDIA Dynamo 等能力结合，面向生产环境部署 Agent [3]。

**差异化定位**：LangChain 不主要押注终端产品，而是以图驱动框架、状态管理和可观测性能力卡位 agent engineering 基础设施。其竞争优势在于把 Agent 开发、调试、评估和部署串联起来；主要风险则是通用框架层受 OpenAI、Anthropic、Google、Microsoft 等平台入口挤压。

## 二、OpenAI（Agents SDK + Codex）

OpenAI 的 Agent 战略从模型能力进一步扩展到 Agent 平台化。2025 年 Build Hour 中，OpenAI 提出 Agents SDK 的新架构，核心变化是 harness 与 compute 分离：harness 负责控制循环、快照、工具编排和上下文管理，compute 层则运行于沙箱容器或 VM [4]。此后，Agents SDK 进一步支持 configurable memory、sandbox-aware orchestration、Codex-like filesystem tools，以及 MCP、skills、AGENTS.md、shell、file edits 等通用 Agent 能力 [5]。

在编码 Agent 方面，OpenAI 推出 Codex as a Platform，将 Codex 的 harness 开源，供开发者基于 Agent 构建应用，并让应用保留对工具、模型、权限和运行环境的控制 [6]。其特色在于沙箱化执行、云端 Agent 能力、模型原生 harness 以及 handoff 式编排。

**差异化定位**：OpenAI 的优势是模型、开发者生态、云执行和 Codex-as-a-Platform 的低门槛入口；不足在于 Agent 平台的控制权仍受 OpenAI 基础设施和模型生态约束，其他框架和 MCP 生态会对其形成替代压力。

## 三、Anthropic（Claude Agent SDK + Claude Code + MCP）

Anthropic 的 Agent 战略以 Claude 系列模型、Claude Code、Claude Agent SDK 和 MCP 集成共同推进。Claude Code 是终端 Agent 代表产品，其特性包括文件编辑、终端访问、Web 搜索，以及通过 MCP 接入外部工具 [7]。MCP 被 Claude Code 作为一等扩展机制使用，Claude Desktop、Claude Code、Claude API 和 Claude Agent SDK 都围绕 MCP 形成接入能力 [8]。

Anthropic 还通过 Claude Agent SDK、Claude MCP App、连接器等机制扩展 Agent 的应用场景。例如在金融服务场景中，Anthropic 提到通过 connectors 让 Claude 获得治理化、实时数据访问，并通过 MCP apps 将 Provider 的工具嵌入 Claude [9]。

**差异化定位**：Anthropic 的差异化在于"终端 Agent + MCP 协议"路线。Claude Code 的高自主性、终端控制和 MCP 集成使其在开发者工具场景中具备较强竞争力；但 MCP 已成为跨厂商开放标准后，Anthropic 对 MCP 的独特控制力会被稀释。

## 四、Google（ADK + Vertex AI Agent Builder / Gemini Enterprise Agent Platform）

Google 的 Agent 战略集中在 ADK、Vertex AI Agent Builder 和 Gemini Enterprise Agent Platform。ADK 是一个轻量级 Agent 开发框架，强调少代码、快速构建，并支持部署到 Vertex AI Agent Engine、Cloud Run 等环境 [10]。Google 在 2026 年 Cloud Next 上将 Vertex AI Agent Builder 相关能力整合进 Gemini Enterprise Agent Platform，作为 Vertex AI 演进的一部分 [11]。

公开资料显示，Google ADK 从 2025 年 4 月发布到 2026 年初 ADK 2.0 Beta，已完成多次小版本更新，并加入新的语言运行时；同时，Google Agentspace 提供无代码设计器，让非技术人员也能参与 Agent 构建 [10]。Google 的优势在于 Google Cloud、Gemini 模型、企业安全合规和多环境部署能力。

**差异化定位**：Google 的核心定位是云原生企业 Agent 平台。其竞争重点不是单一终端产品，而是把 Agent 开发、部署、治理和 Gemini 模型能力统一在 Google Cloud 体系中；风险则来自其他厂商通过 MCP、A2A、Copilot 等入口绕开平台层。

## 五、Microsoft（MAF + Copilot Studio + Semantic Kernel）

Microsoft 的 Agent 战略以 MAF、Copilot Studio、Microsoft 365 Agents SDK 和 A2A 能力为核心。2026 年，微软将"任何人把意图变成 Agent、Agent 端到端拥有工作流、协调 Agent 产生实际结果、灵活控制 Agent 模型、跨系统执行 Agent 操作、规模化 Agent 而不牺牲控制"列为 Agent 采用的核心能力 [12]。

Copilot Studio 方面，微软在 2026 年 7 月更新中开始为新 Agent 自动创建 Microsoft Entra Agent ID，并预览支持将 workflow 或 MCP server 作为 Agent 工具 [13]。Multi-Agent 能力也在持续推进，包括 Microsoft Fabric 集成、Microsoft 365 Agents SDK orchestration 和 A2A 通信 [14]。微软的优势在于企业身份、权限、治理、M365 和现有业务流程入口。

**差异化定位**：Microsoft 的差异化在于企业级流程 Agent 入口。它不追求单个编码 Agent 模型能力最强，而是把 Agent 嵌入 Copilot Studio、Microsoft 365、企业治理和跨系统协作中；主要风险是低代码/平台化路线可能受独立 Agent 框架和编码 Agent 工具的分流。

## 编码 Agent 竞争：Claude Code vs OpenAI Codex vs Cursor

编码 Agent 是目前 AI Agent 系统中最接近生产验证的应用场景之一。三者定位不同：Claude Code 是终端 Agent，OpenAI Codex 是 Codex-as-a-Platform 与云端沙箱 Agent，Cursor 是 IDE-first 的 AI 编码环境。

**Claude Code** 的核心优势在于终端深度控制、长周期自主运行、MCP 集成和 Skills/Hooks 扩展。它可以把外部数据源、数据库、API、GitHub、Jira、Slack 等服务接入 Claude 的工作流，适合重度终端用户、排障、重构和跨工具自动化 [15]。其劣势是产品形态相对终端化，需要用户适应 CLI 工作流。

**OpenAI Codex** 的核心优势在于沙箱化执行、云端 Agent、Workspace Agents 和 handoff 编排。Codex-as-a-Platform 降低了开发者自建 Agent 运行时成本，使应用层可以专注产品逻辑和权限管理 [6]。其劣势是默认开发环境依赖 OpenAI 生态，用户迁移成本和模型锁定风险较高。

**Cursor** 的核心优势是 IDE-first 体验。它基于 VS Code fork，具备 Composer 模式、多文件同步修改、Tab 智能补全和 Agent 模式，对开发者学习成本较低 [16]。第三方对比认为，Cursor 更适合日常主力开发环境；而 Claude Code 和 Codex 更适合终端、云端或长周期自动化场景 [17]。

**竞争判断**：编码 Agent 市场尚未形成单一主导者。Claude Code 在终端自主性和 MCP/Skills 扩展上领先，Codex 在云端沙箱、平台化和 handoff 编排上具备优势，Cursor 在 IDE 体验和连续编码场景上更顺手。三者将在开发者工具、IDE、终端、云端 Agent 和企业内部工具链之间持续分化。

## 参考资料

1. [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — LangChain Docs
2. [LangChain raises $125M to build the platform for agent engineering](https://blog.langchain.com/series-b/) — LangChain Blog
3. [LangChain Announces Enterprise Agentic AI Platform Built with NVIDIA](https://www.langchain.com/blog/nvidia-enterprise) — LangChain Blog
4. [Codex weekly: Agents SDK Gets Model-Native Harness, Workspace Agents GA, Enterprise Partnerships](https://www.bighatgroup.com/blog/codex-weekly-2026-05-29/) — BigHat Group, 2026-05-29
5. [The next evolution of the Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) — OpenAI
6. [Codex as a platform: build on the open agent harness](https://developers.openai.com/blog/codex-as-a-platform) — OpenAI Developers
7. [How Claude Code's Autonomous Commands Are Reshaping Software Development](https://www.techaimag.com/trending-ai-tools/claude-code-software-development) — TechAIMag
8. [MCP and Anthropic Claude: How Claude Desktop, Claude Code, the Claude API, and the Agent SDK Use the Model Context Protocol](https://chatforest.com/guides/mcp-anthropic-claude-integration/) — ChatForest
9. [Agents for financial services](https://www.anthropic.com/news/finance-agents) — Anthropic
10. [Google ADK Explained](https://github.com/2nth-ai/know-2nth/blob/main/google-adk-explainer.md) — 2nth AI
11. [Vertex AI Agent Builder vs Augment Cosmos: Platform Comparison](https://www.augmentcode.com/tools/vertex-ai-agent-builder-vs-augment-cosmos) — Augment Code
12. [6 core capabilities to scale agent adoption in 2026](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/6-core-capabilities-to-scale-agent-adoption-in-2026/) — Microsoft Copilot Blog
13. [What's new in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new) — Microsoft Learn
14. [New and improved: Multi-agent orchestration, connected experiences, and faster prompt iteration](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/new-and-improved-multi-agent-orchestration-connected-experiences-and-faster-prompt-iteration/) — Microsoft Copilot Blog
15. [Building an AI Software Development Team with Claude Code Agents](https://techlife.blog/posts/building-an-ai-software-development-team-with-claude-code-agents/) — TechLife Blog
16. [Cursor vs OpenAI Codex vs Claude Code: 2026 开发者选型指南](https://www.cursor-ide.com/blog/cursor-2-vs-codex-vs-claude) — Cursor IDE
17. [Claude Code vs Cursor vs Codex vs Copilot (2026): An Agent-Builder's Honest Comparison](https://orangebot.ai/blog/claude-code-vs-cursor-vs-codex-vs-copilot-2026) — OrangeBot AI
