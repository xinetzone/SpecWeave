# 01 Protocol边界与最小生命周期

## 三层概念区分

讨论 Agent Protocol 时，最容易把三层东西混在一起：

| 层级 | 例子 | 解决的问题 |
|------|------|-----------|
| **具体协议标准** | A2A、AG-UI、LangChain Agent Protocol、AITP、ACP | 不同系统如何通信，如何描述任务、消息、事件和产物 |
| **通用协议对象** | Thread、Run、Step、Event、Artifact、Checkpoint | 外部世界如何稳定理解一次 Agent 任务 |
| **Runtime 实现能力** | 状态持久化、中断恢复、可恢复流、权限控制、可观测性 | Runtime 内部如何兑现这些对象和状态机 |

本文重点讨论**第二层：通用协议对象**。具体协议标准和框架实现只作为证据，用来说明这些对象正在跨系统收敛。

## Runtime Protocol：外部世界如何理解一个Agent

Agent Runtime Protocol 是 Agent Runtime 暴露给外部世界的契约。它回答的不是"模型如何思考"，而是：

- **如何启动一次任务**：创建 Thread、Task、Run，或发送一条 Message
- **如何携带上下文**：历史消息、文件、结构化数据、参与者、能力声明
- **如何观察进展**：状态变更、流式事件、Artifact 增量、Trace
- **如何中断和恢复**：需要输入、需要授权、取消、重试、继续执行
- **如何拿到结果**：最终消息、Artifact、结构化输出、错误信息

> **Protocol 是 Runtime 的外部边界，Runtime 是 Protocol 的内部实现。**

讨论 Agent Runtime 时不应该只讨论内部编排，也要讨论它被什么协议对象驱动，以及它向外承诺什么状态机。换句话说：**Runtime 是内部能力，Protocol 是外部可依赖的边界**。

## Runtime：模型调用之外的执行系统

Agent Runtime 是 Agent 的执行环境，负责：接收输入 → 调用 LLM → 执行工具 → 管理状态 → 产出结果。

不同框架对 Runtime 的定义边界不同：
- **LangGraph**：包含了从编排到持久化的完整栈
- **OpenAI Assistants**：把整个 Runtime 藏在服务端
- **AutoGen**：更强调多 Agent 对话组织

但它们都必须回答同一组问题。更精确地说，Agent Runtime 不是"一次模型调用"，而是模型调用之外的那层执行系统。它至少要管理五类事情：

| 职责 | 说明 |
|------|------|
| **生命周期** | 一次任务如何开始、运行、暂停、恢复、结束 |
| **上下文** | 哪些消息、文件、状态、外部资源对当前执行可见 |
| **调度** | 下一步调用模型、工具、子 Agent，还是等待人类 |
| **控制面** | 权限、Guardrail、取消、超时、预算、并发限制 |
| **数据面** | 状态快照、事件流、Trace、Artifact、成本数据如何流动 |

这也是为什么 Responses API 不是 Runtime，而 OpenAI Agents SDK 是更高层 Runtime：前者主要给你模型和工具调用能力，后者开始接管循环、工具执行、Handoff、Session、Guardrail、Tracing 等运行时职责。

## 最小生命周期：一个Agent任务经历了什么

不管采用哪种框架，生产级 Agent Runtime 都绕不开同一个生命周期。这里最关键的概念是 **Run**。Thread/Session 描述长期上下文，Run 描述一次具体执行。没有 Run 这个边界，就很难定义超时、取消、Trace、成本、权限审批和最终结果。

从协议角度看，这条生命周期可以被映射成一组稳定对象：

| Protocol 对象 | Runtime 含义 | 典型来源 |
|--------------|-------------|---------|
| **Agent / Assistant** | 可被调用的能力提供者 | A2A Agent Card、OpenAI Assistant、LangGraph assistant |
| **Thread / Context** | 多轮上下文边界 | OpenAI Thread、AITP Thread、A2A Context |
| **Task / Run** | 一次执行边界 | A2A Task、OpenAI Run、LangGraph Run |
| **Message / Part** | 输入输出内容单元 | A2A Message/Part、AITP Message |
| **Artifact** | 任务产物 | A2A Artifact、文件、报告、代码 diff |
| **Event** | 进展增量 | SSE event、status update、artifact update |
| **Checkpoint / State** | 可恢复状态 | LangGraph Checkpoint、State Snapshot |

## 阅读路径映射

| 生命周期阶段 | 主要协议对象 | 对应章节 |
|------------|------------|---------|
| **创建任务** | Agent / Thread / Run | 执行模型、Runtime Loop（第02章） |
| **携带上下文** | Thread / Message / Workspace | 状态管理、Workspace/Sandbox（第03章） |
| **执行步骤** | Step / Tool Call / Subagent task | 执行模型、工具协议、多Agent协作（第02、05、06章） |
| **观察事件** | Event / Trace / State Snapshot | 流式输出、可观测性（第05、07章） |
| **中断恢复** | Checkpoint / Interrupt / Resume | 状态管理、中断恢复、错误恢复（第03、04章） |
| **产生产物** | Artifact / Workspace file | 状态管理、流式输出、Harness（第03、05章） |
| **评测审计** | Step / Event / Artifact / Trace | 可观测性与可评测性（第07章） |

## 现有协议收敛对比

不同标准和框架正在围绕 Thread、Run、Step、Event、Artifact、Checkpoint 这些对象收敛：

| 协议/规范 | 核心对象 | 主要关注点 | 对 Runtime 的启发 |
|----------|---------|-----------|----------------|
| **LangChain Agent Protocol** | Thread、Run、Store、Command、OpenAPI spec | 用框架无关 API 服务化生产 Agent | Runtime 要暴露可创建、搜索、更新、流式运行和发送命令的标准资源 |
| **A2A** | Agent Card、Task、Message、Part、Artifact、Streaming Event | 独立 Agent 系统之间互操作 | Task 状态机和 Artifact 是跨 Agent 协作的核心 |
| **AITP** | Thread、Actor、Capability、Transport | 跨信任边界的 Agent 交互和交易 | Thread 是最低公共接口，Capability 承载结构化能力 |
| **ACP** | Agent metadata、REST endpoint、Message、SSE | 跨框架、跨组织 Agent 通信 | 协议要简单到能用 HTTP 直接接入，同时支持异步长任务 |
| **AG-UI** | Run event、Message event、Tool event、State delta | Agent 与前端 UI 的事件协议 | 前端需要的不只是最终答案，而是标准化事件流 |
| **OpenAI Assistants** | Assistant、Thread、Message、Run、Run Step | 托管式 Agent 执行 | Thread/Run/Step 是生产 Runtime 的基础资源模型 |
| **LangGraph Server API** | Thread、Run、Stream Mode、State Update | 可恢复流和状态观测 | Runtime 协议需要同时支持 run stream 和 thread stream |
| **Deep Agents** | Todo、Subagent task、Virtual filesystem、Backend、Skill | 复杂任务 Agent Harness | Runtime 之上还需要面向长任务的 planning、delegation、workspace 和 skill 协议对象 |
| **OpenTelemetry GenAI** | Trace、Span、Event、Attributes | 跨框架可观测性语义 | Protocol 不只面向业务调用，也面向观测系统 |

这些标准并没有完全收敛，但它们已经共同指向一个事实：Agent Protocol 的中心不再是单次 chat completion，而是**长生命周期、可观测、可评测、可恢复、可协作的任务对象**。

## 本文使用的框架证据

| 框架 | 全称 | 核心定位 | 版本基准 |
|------|------|---------|---------|
| **LangGraph** | LangGraph + LangGraph Platform | 图执行引擎 + Agent Server | 0.3.x |
| **Deep Agents** | Deep Agents SDK (built on LangGraph) | 面向复杂任务的 Agent Harness | 2026.06 |
| **OpenAI** | Assistants API + Responses API + Agents SDK | 托管式 Agent Runtime | 2025.04 |
| **AutoGen** | AutoGen 0.4 (Core + AgentChat) | 多 Agent 对话框架 | 0.4.x |
| **Claude SDK** | Claude Agent SDK (Anthropic) | 代码执行 Agent | 0.1.x |

---
