# AI Agent 系统产业链分析

## 核心判断

AI Agent 产业链可按"基础模型层→框架/平台层→应用层→终端用户"划分为四层，其中 MCP 与 A2A 协议正在成为跨层互操作基础设施：MCP 负责 Agent 与工具/数据/API 的连接，A2A 负责不同 Agent 之间的任务委派、结果共享与跨平台协作。当前产业链的关键瓶颈集中在应用层的工具编排与多 Agent 调度：动态工具编排、上下文一致性、成本追踪和生命周期管理仍是生产部署中的主要短板。

---

## 产业链四层结构

### 第 1 层：基础模型层（LLM 提供商）

基础模型层提供 Agent 系统所需的推理、理解和生成能力，是产业链的上游。2026 年资料中常见的基础模型提供商包括 OpenAI、Anthropic、Google、Meta、Mistral 等；其中 OpenAI、Anthropic、Google 均参与 Agentic AI 相关协议或标准项目。

| 公司 | 代表产品 | 产业链定位 |
|---|---|---|
| OpenAI | GPT-4o、o-series | 基础模型提供商；AGENTS.md 贡献方之一 |
| Anthropic | Claude | 基础模型提供商；MCP 发起并贡献方 |
| Google | Gemini | 基础模型提供商；A2A 原始开发方 |
| Meta | Llama | 基础模型提供商 |
| Mistral | Mistral Large | 基础模型提供商 |

基础模型层的价值体现在 API 调用、模型推理和训练基础设施。对终端 Agent 应用而言，模型层通常构成算力、模型接入和基础智能能力的主要成本来源；不同模型在推理成本、延迟和可用性上会影响上层 Agent 系统的经济可行性。

### 第 2 层：框架/平台层（Agent 编排层）

框架/平台层是 Agent 产业链的核心中间层，负责将基础模型能力转化为可编排、可复用、可部署的 Agent 系统。该层产品通常具备模型接入、工具调用、状态管理、多 Agent 调度、可观测性和工作流编排等能力。

#### 2.1 开源 Agent 框架

| 框架 | 架构特点 | 代表产品/生态 |
|---|---|---|
| LangChain/LangGraph | 图驱动状态机，支持循环、持久化和复杂工作流 | LangGraph、LangSmith |
| CrewAI | 多 Agent 协作框架 | CrewAI |
| AutoGen | 多 Agent 对话式协作 | Microsoft 生态中的 AutoGen 路线 |
| Google ADK | 多语言、图基工作流 | Google ADK |
| Anthropic Claude Agent SDK | Claude 原生 Agent 开发 | Claude Agent SDK |
| OpenAI Agents SDK | OpenAI 原生 Agent 开发 | OpenAI Agents SDK |

LangGraph 的核心定位是复杂 Agent 工作流和精确流程控制。2026 年资料中，LangGraph 常被归为图驱动框架，并用于复杂、可控的多 Agent 协作流程；StackOne 将其列为 11 类 AI Agent 工具中的"AI Agent Frameworks"类别之一 [1]。

#### 2.2 商业/企业级 Agent 平台

| 平台 | 厂商 | 特点 |
|---|---|---|
| Vertex AI Agent Builder | Google | 面向企业工作流的 Agent 构建平台 |
| Bedrock AgentCore | AWS | 集成 AWS Bedrock 的企业 Agent 平台 |
| Copilot Studio/MAF | Microsoft | 企业级 Agent 平台路线 |
| Agentforce | Salesforce | 企业销售与服务场景 Agent 平台 |
| watsonx Assistant | IBM | 企业级对话 Agent 平台 |
| ServiceNow AI Agents | ServiceNow | IT 与服务运营场景 Agent |

价值集中方面，框架/平台层的产品化趋势体现在可复用 Agent 能力、工作流模板、工具集成和企业集成。开源框架与商业平台之间的竞争体现在是否提供完整工作流、多 Agent 调度、可观测性和企业集成能力。

### 第 3 层：应用层（Agent 产品）

应用层是将 Agent 能力封装到具体场景中的终端产品。StackOne 将 AI Agent 工具分为 11 个类别，其中编码 Agent、企业平台、无代码/低代码构建器、可观测性、记忆与向量数据库等均构成应用层或支撑层产品 [1]。

#### 3.1 编码 Agent

| 产品 | 特点 |
|---|---|
| Claude Code | Anthropic 生态下的编码 Agent |
| Cursor | 代码编辑器中的 Agent 辅助 |
| OpenAI Codex | OpenAI 生态下的编码 Agent |
| Devin | 独立软件工程师 Agent |
| GitHub Copilot | 代码生成与开发辅助 |

编码 Agent 是应用层中较清晰的垂直应用方向，其价值来自软件开发、代码生成、调试和自动修复等场景。

#### 3.2 浏览器/通用任务 Agent

| 产品 | 特点 |
|---|---|
| OpenAI Operator | 浏览器 Agent 路线 |
| Google Gemini Agent | 多模态与通用任务 Agent |
| Anthropic Computer Use | 桌面/浏览器交互 Agent |

这类 Agent 的价值在于执行更复杂的用户任务，包括浏览网页、填写表单、跨应用操作和自动化流程。

#### 3.3 企业应用层 Agent

| 场景 | 代表产品/方案 |
|---|---|
| 企业知识问答 | LangChain + LangSmith 路线 |
| 客服与支持 | Salesforce Agentforce、ServiceNow AI Agents |
| 研发与协作 | Microsoft Copilot Studio、Google Vertex AI Agent Builder |
| 财务与运营 | AWS Bedrock AgentCore、IBM watsonx Assistant |

#### 3.4 可观测性与评估层

可观测性工具包括 Langfuse、Arize、LangSmith 等，它们提供 Agent 运行轨迹、性能评估、错误追踪和合规审计能力。StackOne 将 Agent 可观测性与评估工具列为 AI Agent 工具生态的重要类别之一 [1]。

### 第 4 层：终端用户

终端用户包括企业客户和个人开发者。对企业管理者而言，Agent 的价值主要体现在流程自动化、研发效率、客服响应和运营优化；对开发者而言，Agent 的价值体现在编码辅助、工作流构建和任务自动化。

---

## MCP 与 A2A 协议在产业链中的角色

### MCP：Agent 与工具/数据/应用的连接协议

MCP（Model Context Protocol）由 Anthropic 提出，并于 2025 年 12 月捐赠给 Agentic AI Foundation（AAIF），由 Linux Foundation 托管。MCP 负责标准化 Agent 与工具、API、数据源和外部应用之间的连接方式 [2][3]。

在产业链中，MCP 的作用主要体现在：

1. **降低工具集成复杂度**：MCP 通过统一接口连接 Agent 与外部工具、API 和数据源，使工具接入具有更强的可复用性。
2. **增强模型层与应用层之间的可组合性**：不同框架可以基于 MCP 访问共同工具集，减少重复集成。
3. **提升可观测性和调试能力**：MCP 作为工具交互协议，有助于跟踪 Agent 的工具调用、输入输出和错误来源。

MCP 贡献方包括 Anthropic、OpenAI 和 Block；OpenAI 同时贡献了 AGENTS.md，作为向 Agent 提供项目特定指令和上下文的开放格式 [2][3]。

### A2A：Agent 之间的跨平台通信协议

A2A（Agent-to-Agent Protocol）由 Google 原始开发，后捐赠给 Linux Foundation，由 AAIF 管理。A2A 负责不同 Agent 之间的发现、任务委派、结果共享和跨平台协作 [4]。

在产业链中，A2A 的作用主要体现在：

1. **跨框架 Agent 协作**：A2A 支持基于 LangGraph、CrewAI、Semantic Kernel 等不同框架的 Agent 进行协作。
2. **跨平台任务委派**：独立 Agent 可以委托子任务、交换信息并共享结果。
3. **企业级多 Agent 工作流**：A2A 使企业可以将多个专用 Agent 串联为复合系统。

### MCP 与 A2A 的关系

MCP 和 A2A 不是竞争关系，而是互补关系：

- **MCP**：Agent 与工具、数据、API 的通信。
- **A2A**：Agent 与 Agent 的通信。

A2A 官方说明明确指出，MCP 用于让 Agent 连接其需要的工具、API 和资源，A2A 用于让独立 Agent 发现彼此、委派任务并共享结果 [4]。

### 协议层在产业链中的位置

MCP 和 A2A 可视为贯穿基础模型层、框架/平台层和应用层的协议层。其价值在于提升产业链的可组合性：框架层不必完全绑定特定工具，应用层也不必完全绑定特定模型，从而实现更灵活的系统组合。

---

## 工具编排：产业链关键瓶颈

工具编排是 Agent 产业链中重要的瓶颈之一，尤其体现在多 Agent 系统、复杂工作流和企业生产部署中。

### 瓶颈 1：动态工具调度不足

动态工具编排资料将静态配置系统与动态编排系统对比，显示静态配置工具资源利用率为 40–55%，动态编排为 70–85%，差距约 1.5 倍 [5]。其核心判断是：当前工具编排系统过度依赖静态配置，而运行时自适应调度能力不足。

### 瓶颈 2：共享状态管理困难

CoOMMIT 将 LangChain 的"shared-state gap"称为编排失败的重要预测因素 [6]。其业务含义是：Agent 工作流设计中，如果没有明确界定共享状态、结果存放位置和工具输出路径，应用层 Agent 在复杂任务中容易出现上下文断裂。

### 瓶颈 3：生命周期管理和成本控制不足

MindStudio 指出，Agent 编排包括调度、生命周期管理、监督层级、失败处理和成本追踪 [7]。这些能力在原型阶段可能被简化，但在企业生产部署中成为可靠性、成本控制和合规审计的关键瓶颈。

### 瓶颈 4：供应商锁定

Fifthrow 资料称，76–81% 的受访企业担心供应商锁定，尤其是在 Agent 记忆、模型集成和编排工具层 [8]。这说明工具编排层虽然具备可组合性，但实际迁移成本仍较高。

### 瓶颈 5：Token 成本和上下文管理

NVIDIA 资料显示，Claude Code 等真实 Agentic 会话的 Token 量可从数万扩展到 150,000+，需要上下文压缩、提示缓存和专门硬件支持 [9]。这说明模型层与框架/平台层之间的上下文管理成本，会直接影响应用层 Agent 的经济可行性。

---

## 产业链整合趋势

1. **框架层整合加速**：StackOne 将 AI Agent 工具分为 11 类，其中框架、平台、可观测性、记忆、工具集成和编码 Agent 等类别共同构成完整产业链 [1]。

2. **协议层成为互操作基础**：MCP 和 A2A 正在成为跨框架、跨平台协作的重要基础设施，提升产业链上下游的可组合性。

3. **应用层垂直化**：编码 Agent、浏览器 Agent、企业 Agent 等垂直应用逐步成熟，价值更多体现在具体业务场景和可量化效率提升上。

4. **框架层与协议层融合**：Google ADK 资料中的框架对比显示，不同框架对 A2A 和 MCP 的支持程度不同，框架层正在从独立开发框架向协议兼容平台演进 [10]。

5. **企业级平台成为关键部署入口**：企业级 Agent 平台连接模型层、工具层和应用层，是产业链价值从原型走向生产部署的关键节点。

---

## 参考资料

1. [The AI Agent Tools Landscape: 120+ Tools Mapped](https://www.stackone.com/blog/ai-agent-tools-landscape-2026) — StackOne, 2026-02-08
2. [Linux Foundation Announces the Formation of the Agentic AI Foundation (AAIF)](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) — Linux Foundation, 2025-12-09
3. [OpenAI co-founds the Agentic AI Foundation under the Linux Foundation](https://openai.com/index/agentic-ai-foundation/) — OpenAI, 2025-12-09
4. [Agent2Agent Protocol](https://a2a-protocol.org/latest/) — A2A Protocol, 2026
5. [AI Agent 动态工具编排：从静态配置到运行时自适应调度](https://github.com/kejun/blogpost/blob/main/2026-04-03-ai-agent-dynamic-tool-orchestration.md) — GitHub, 2026-04-03
6. [AI Agent Orchestration: Handoff Patterns for 2026](https://www.coommit.com/blog/ai-agent-orchestration-2026) — CoOMMIT, 2026
7. [What Is Agent Orchestration? Why It's the Biggest Unsolved Problem in the AI Stack](https://www.mindstudio.ai/blog/agent-orchestration-biggest-unsolved-problem-ai-stack) — MindStudio, 2026-04-07
8. [AI Agent Orchestration Goes Enterprise: The April 2026 Playbook](https://www.fifthrow.com/blog/ai-agent-orchestration-goes-enterprise-the-april-2026-playbook-for-systematic-innovation-risk-and-value-at-scale) — Fifthrow, 2026-04
9. [Building for the Rising Complexity of Agentic Systems with Extreme Co-Design](https://developer.nvidia.com/blog/?p=116408) — NVIDIA, 2026
10. [AI agent framework comparison: LangGraph, crewai, Google ADK, and when to Go custom](https://www.raftlabs.com/blog/ai-agent-framework-comparison) — RaftLabs, 2026
