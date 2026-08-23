---
id: "agent-runtime-protocol-wiki-05"
title: "工具协议与流式输出（Part 3）"
source: "微信公众号文章《Agent Protocol：一个生产级的 Agent Runtime 应该包含什么？》（阿里云开发者）https://mp.weixin.qq.com/s/0N-RnpGVy_PLSDHMwAIFNg"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki/05-tools-streaming.toml"
---

# 05 工具协议与流式输出（Part 3）

## 第一部分：工具协议——最可能先标准化的一层

这一部分对应任务生命周期里的"执行外部动作"：Runtime 如何调用外部能力。

工具协议定义了 Agent 如何发现、调用和处理外部能力。

### 通用概念

**子概念**：
- **工具定义 (Tool Definition)**：描述工具的名称、参数、返回值——通常用 JSON Schema
- **工具调用 (Tool Invocation)**：调用的请求/响应格式和传输方式
- **工具结果 (Tool Result)**：返回给 Agent 的数据格式
- **工具发现 (Tool Discovery)**：Agent 如何知道有哪些工具可用
- **错误处理 (Error Handling)**：工具调用失败时的行为

### 跨框架映射

| 概念 | LangGraph | OpenAI | AutoGen | Claude SDK |
|------|-----------|--------|---------|-----------|
| **定义格式** | `@tool` + JSON Schema | Function Calling JSON Schema | `FunctionTool` + JSON Schema | `Tool`（JSON Schema） |
| **调用约定** | `ToolNode` 自动执行 | `requires_action` → 客户端执行 | Agent 内部直接调用 | Agent 内部直接调用 |
| **结果格式** | `ToolMessage` | Function output（字符串） | `FunctionExecutionResult` | `ToolResult` |
| **发现机制** | 构建时 `bind_tools()` | 创建 Assistant/Response 时指定 | 创建 Agent 时注册 | 创建时 `allowed_tools` |
| **错误处理** | 可配置：`handle_tool_errors=True` | 错误作为 output 返回 LLM | 异常转为错误消息 | 错误在结果中 |

### 工具协议独立分层理念

工具协议的关键问题在于工具能力能否从执行模型里解耦出来。

**紧耦合的做法**：
- 用 LangGraph 时，工具必须适配 LangChain Tool
- 用 OpenAI 时，工具必须适配 Function Calling 格式
- 用 Claude SDK 时，工具必须适配它自己的工具定义
- 切换框架时，工具层跟着重写

**更合理的做法**：
- 工具定义统一使用结构化 schema
- 工具调用统一表达为请求和响应
- 工具结果统一转成 Agent 可理解的消息
- 执行框架只负责编排，不直接拥有工具实现

> **不再写框架特定的 Tool wrapper。** 工具定义、调用、结果处理应该独立于具体 Runtime。工具层的边界最清晰、输入输出最结构化、和底层 loop 承载方式最解耦，因此最可能先实现标准化。

### MCP：工具层标准化的典型形态

MCP（Model Context Protocol）把工具发现、工具定义、工具调用、资源读取、Prompt 模板等能力抽象成一组客户端和服务端之间的协议对象。Host/Client/Server 的分层，让 Agent Runtime 可以通过统一连接方式接入外部能力，而不必为每个工具单独写框架绑定。

| MCP 对象 | 对应工具协议能力 | Runtime 意义 |
|---------|----------------|-------------|
| **Tool** | 工具定义、参数 schema、调用结果 | 让外部能力以统一 schema 暴露给 Agent |
| **Resource** | 可读取的上下文资源 | 把文件、文档、数据库记录等变成可发现上下文 |
| **Prompt** | 可复用提示模板 | 把任务模板和工具使用方式沉淀为可调用能力 |
| **Client / Server** | 传输与能力发现边界 | 解耦 Runtime 和具体工具实现 |

**MCP 的定位边界**：MCP 标准化的是"Agent 能调用什么、如何发现和调用"；Runtime Protocol 还要继续表达 Thread/Run/Step/Event/Artifact/Checkpoint/Interrupt 这些任务生命周期对象。MCP 可以成为 Runtime 的工具层和上下文接入层，但完整 Runtime 仍然需要自己管理执行循环、状态持久化、流式事件、中断恢复和观测语义。

MCP 的长期价值在于把工具生态从框架内部抽出来。一个 MCP Server 可以同时服务 Claude、IDE、桌面应用、后台 Agent 或自建 Runtime；Runtime 只需要实现 MCP Client/Host 侧适配，就能复用同一组工具、资源和 Prompt。

### Error-as-Data 在工具层应用

工具调用失败时，有两种根本不同的处理策略：

| 策略 | 行为 | 代表 |
|------|------|------|
| **Error-as-Data** | 错误信息作为工具结果返回给 LLM，由 LLM 决定如何处理 | OpenAI（错误在 output 中）、LangGraph (`handle_tool_errors=True`) |
| **Error-as-Exception** | 错误作为异常抛出，执行中断，由框架/开发者处理 | 传统编程模式 |

**Error-as-Data 是更好的默认策略**，原因：
- LLM 能看到错误信息，可以自主决定重试、换工具、或告知用户
- 不需要开发者为每种错误写 try/catch
- 更接近人类使用工具的方式——工具出错了，你会看看错误信息然后决定下一步

这类设计的核心是：错误仍然是一个合法的工具结果，不是直接打断 Runtime 的异常。

### Runtime 控制面：权限、Guardrail、预算

工具一旦能产生真实副作用，Runtime 就必须有控制面。控制面负责约束 Agent 能做什么、何时必须停下来、谁可以批准继续。

生产 Runtime 至少需要这些控制点：

| 控制点 | 作用 | 典型触发时机 |
|--------|------|-------------|
| **Permission** | 限制工具、文件、网络、外部系统访问 | 工具调用前 |
| **Guardrail** | 检查输入/输出是否违反安全或业务规则 | 模型调用前后 |
| **Human Review** | 让人类审批高风险动作 | 写文件、发请求、提交订单前 |
| **Budget** | 限制 token、成本、步骤数、执行时间 | Run 开始和每个 Step 后 |
| **Cancellation** | 允许用户或系统终止执行 | 长任务、误操作、超时 |

OpenAI Agents SDK 把 Guardrails、Human-in-the-loop、Tracing 做成 Runtime 能力；Claude Agent SDK 暴露 permissions 和 hooks；LangGraph 通过 interrupt/checkpoint 组合实现审批和恢复。它们指向同一个趋势：Agent Runtime 不只是执行器，还是一个安全边界。

### 工具协议本章结论

工具协议回答"Runtime 如何连接外部能力"。它与执行模型解耦：同一个 Tool API 应该能被图式、代码式、托管式 Runtime 复用，而不是绑定在某个框架的 wrapper 里。

> **工具层是最可能先标准化的部分。** JSON Schema 已经成为事实标准，MCP 进一步把工具发现、资源读取和 Prompt 模板从框架内部抽出来，让外部能力能被不同 Runtime 复用。

一旦工具能产生真实副作用，控制面就必须进入 Runtime。权限、Guardrail、人类审批、预算和取消不是外围功能，而是 Agent Runtime 面向真实系统时的安全边界。

---

## 第二部分：流式输出——不是 token 打字机，而是任务事件流

流式输出定义了 Agent 执行的增量结果如何传递给消费者。协议视角下，流式输出不是"边生成边打印 token"，而是 Runtime 把一次 Task/Run 的状态变化、消息增量、工具进展、Artifact 增量和自定义事件统一编码成事件流。

### 通用概念

**子概念**：
- **传输协议 (Transport)**：SSE、WebSocket、异步生成器、轮询
- **粒度控制 (Granularity)**：Token 级、节点/步骤级、消息级
- **可恢复性 (Resumability)**：断连后能否从断点继续接收
- **多通道 (Multi-channel)**：是否同时暴露 token、事件、状态、Artifact

### 核心理念纠正

> **生产级流式是"任务事件流"，不是"token 打字机"。**

很多人理解的流式输出只是"让用户看到 token 一个一个蹦出来"，这是对 LLM 聊天场景的窄化理解。真正的生产级 Agent 流式输出应该暴露完整的任务生命周期事件：

- **状态事件**：Run 状态变更（queued → running → waiting_for_input → completed）
- **消息事件**：LLM token 增量、完整消息
- **工具事件**：工具调用开始、参数、进度、结果
- **产物事件**：Artifact 增量创建、更新、完成
- **错误事件**：工具失败、重试、降级
- **Trace 事件**：Step 开始/结束、Token 用量、耗时

前端需要的不只是最终答案，而是标准化的任务事件流。这也是 AG-UI 协议出现的原因——它专门定义 Agent 与前端 UI 之间的事件协议。

### 跨框架映射

| 概念 | LangGraph Platform | OpenAI Assistants | Agents SDK | AutoGen | Claude SDK |
|------|-------------------|------------------|------------|---------|-----------|
| **传输** | SSE（可恢复） | SSE / 轮询 | Python AsyncGen | Python AsyncGen | Python AsyncGen |
| **粒度** | 9 种 StreamMode 可组合 | 固定事件类型 | `StreamEvent` | 消息级 | 事件级 |
| **可恢复** | **支持**（Last-Event-ID + Redis Stream） | 不支持 | 不支持 | 不支持 | 不支持 |
| **自定义事件** | `get_stream_writer()` | 不支持 | 不支持 | 不支持 | 不支持 |
| **子图/子 Agent** | `stream_subgraphs=True` | N/A | 不支持 | Topic 订阅 | N/A |

### Server vs Library 流式能力分水岭

流式输出有一个容易被忽视但极其重要的分水岭：**Server 能力 vs Library 能力**。

| 形态 | 传输 | 可恢复 | 典型代表 |
|------|------|--------|---------|
| **Library（进程内）** | Python AsyncGenerator | 不需要（进程内不会断连） | Agents SDK、Claude SDK、AutoGen |
| **Server（跨网络）** | SSE/WebSocket | **必须考虑（网络会断）** | LangGraph Platform、OpenAI Assistants |

| 能力 | Library 流式（本地 SDK） | Server 流式（API 服务） |
|------|---------------------|-------------------|
| **传输** | 内存中的 async generator | HTTP SSE / WebSocket |
| **断连恢复** | 不支持（进程内） | 必须支持（Last-Event-ID） |
| **多客户端** | 单消费者 | 多订阅者 |
| **历史回放** | 不支持 | Catch-up 机制 |
| **跨进程** | 不支持 | 必须支持 |

> **只要 Agent 被部署为服务（跨网络访问），流式输出就必须从"内存 async generator"升级为"可恢复的 SSE 事件流"。**

### LangGraph Platform 可恢复流机制

LangGraph Platform 的可恢复流是目前唯一完整的实现：

1. **Redis Stream 持久化**：所有事件被写入 Redis Stream，不只是内存中临时生成
2. **Last-Event-ID 协议**：客户端断连重连时携带最后收到的 event ID，服务端从断点继续发送
3. **两种模式**：
   - **Catch-up 回放**：一次性发送断连期间错过的所有事件
   - **Live Tail**：追上后进入实时模式，继续推送新事件
4. **双 Stream 支持**：run stream（单次执行的事件）和 thread stream（整个 Thread 的所有 Run 事件）

```
客户端连接 ──► Last-Event-ID=X ──► 服务端回放 X 之后的历史事件 ──► Live Tail 实时事件
```

> **可恢复 SSE 的关键是先基于 Last-Event-ID 回放历史事件，再切换到实时 Live Tail。**

### 流式输出本章结论

流式输出回答"外部系统如何实时看见 Run 的进展"。它把状态、消息、工具调用、Artifact 增量和错误统一成事件流，是 Runtime 面向前端、控制台和审计系统的主要出口。

流式能力与部署形态高度相关。进程内 Agent 可以用 AsyncGenerator；一旦跨网络部署，SSE + 可恢复流就成为刚需，因为客户端断线、服务端继续执行、之后补收事件是生产系统的常态。

因此不要把 streaming 理解成 token 打字机。生产级流式输出应该是任务事件流，并能通过 Last-Event-ID、事件持久化和多通道事件支持恢复、追踪和审计。

---

- 上一章：[中断与错误恢复](04-interrupt-error-recovery.md)
- [下一章：多 Agent 协作](06-multi-agent.md) →
