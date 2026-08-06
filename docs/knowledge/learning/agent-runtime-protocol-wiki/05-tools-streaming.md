# 05 工具协议与流式输出（Part 3）

## 第一部分：工具协议——最可能先标准化的一层

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
| **定义格式** | `@tool` + JSON Schema | Function Calling JSON Schema | `FunctionTool` + JSON Schema | Tool（JSON Schema） |
| **调用约定** | `ToolNode`自动执行 | `requires_action` → 客户端执行 | Agent内部直接调用 | Agent内部直接调用 |
| **结果格式** | `ToolMessage` | Function output（字符串） | `FunctionExecutionResult` | `ToolResult` |
| **发现机制** | 构建时`bind_tools()` | 创建Assistant/Response时指定 | 创建Agent时注册 | 创建时`allowed_tools` |
| **错误处理** | 可配置：`handle_tool_errors=True` | 错误作为output返回LLM | 异常转为错误消息 | 错误在结果中 |

### 工具协议独立分层理念

工具协议的关键问题在于工具能力能否从执行模型里解耦出来。

**紧耦合的做法**：
- 用LangGraph时，工具必须适配LangChain Tool
- 用OpenAI时，工具必须适配Function Calling格式
- 用Claude SDK时，工具必须适配它自己的工具定义
- 切换框架时，工具层跟着重写

**更合理的做法**：
- 工具定义统一使用结构化schema
- 工具调用统一表达为请求和响应
- 工具结果统一转成Agent可理解的消息
- 执行框架只负责编排，不直接拥有工具实现

> **工具层的边界最清晰、输入输出最结构化、和底层loop承载方式最解耦，因此最可能先实现标准化。**

### MCP：工具层标准化的典型形态

从 Runtime Protocol 的视角看，MCP（Model Context Protocol）把工具发现、工具定义、工具调用、资源读取、Prompt模板等能力抽象成一组客户端和服务端之间的协议对象。Host/Client/Server的分层，让Agent Runtime可以通过统一连接方式接入外部能力，而不必为每个工具单独写框架绑定。

| MCP对象 | 对应工具协议能力 | Runtime意义 |
|---------|----------------|------------|
| **Tool** | 工具定义、参数schema、调用结果 | 让外部能力以统一schema暴露给Agent |
| **Resource** | 可读取的上下文资源 | 把文件、文档、数据库记录等变成可发现上下文 |
| **Prompt** | 可复用提示模板 | 把任务模板和工具使用方式沉淀为可调用能力 |
| **Client/Server** | 传输与能力发现边界 | 解耦Runtime和具体工具实现 |

**MCP的定位边界**：MCP标准化的是"Agent能调用什么、如何发现和调用"；Runtime Protocol还要继续表达Thread/Run/Step/Event/Artifact/Checkpoint/Interrupt这些任务生命周期对象。MCP可以成为Runtime的工具层和上下文接入层，但完整Runtime仍然需要自己管理执行循环、状态持久化、流式事件、中断恢复和观测语义。

MCP的长期价值在于把工具生态从框架内部抽出来。一个MCP Server可以同时服务Claude、IDE、桌面应用、后台Agent或自建Runtime；Runtime只需要实现MCP Client/Host侧适配，就能复用同一组工具、资源和Prompt。

### Runtime控制面：权限、Guardrail、预算

工具一旦能产生真实副作用，Runtime就必须有控制面。控制面负责约束Agent能做什么、何时必须停下来、谁可以批准继续。

生产Runtime至少需要这些控制点：

| 控制点 | 作用 | 典型触发时机 |
|--------|------|------------|
| **Permission** | 限制工具、文件、网络、外部系统访问 | 工具调用前 |
| **Guardrail** | 检查输入/输出是否违反安全或业务规则 | 模型调用前后 |
| **Human Review** | 让人类审批高风险动作 | 写文件、发请求、提交订单前 |
| **Budget** | 限制token、成本、步骤数、执行时间 | Run开始和每个Step后 |
| **Cancellation** | 允许用户或系统终止执行 | 长任务、误操作、超时 |

OpenAI Agents SDK把Guardrails、Human-in-the-loop、Tracing做成Runtime能力；Claude Agent SDK暴露permissions和hooks；LangGraph通过interrupt/checkpoint组合实现审批和恢复。它们指向同一个趋势：Agent Runtime不只是执行器，还是一个安全边界。

### 工具协议本章结论

工具协议回答"Runtime如何连接外部能力"。它与执行模型解耦：同一个Tool API应该能被图式、代码式、托管式Runtime复用，而不是绑定在某个框架的wrapper里。

工具层是最可能先标准化的部分。JSON Schema已经成为事实标准，MCP进一步把工具发现、资源读取和Prompt模板从框架内部抽出来，让外部能力能被不同Runtime复用。

一旦工具能产生真实副作用，控制面就必须进入Runtime。权限、Guardrail、人类审批、预算和取消不是外围功能，而是Agent Runtime面向真实系统时的安全边界。

---

## 第二部分：流式输出——不是token打字机，而是任务事件流

流式输出定义了Agent执行的增量结果如何传递给消费者。协议视角下，流式输出不是"边生成边打印token"，而是Runtime把一次Task/Run的状态变化、消息增量、工具进展、Artifact增量和自定义事件统一编码成事件流。

### 通用概念

**子概念**：
- **传输协议 (Transport)**：SSE、WebSocket、异步生成器、轮询
- **粒度控制 (Granularity)**：Token级、节点/步骤级、消息级
- **可恢复性 (Resumability)**：断连后能否从断点继续接收
- **多通道 (Multi-channel)**：是否同时暴露token、事件、状态、Artifact

### 核心理念纠正

> **生产级流式是"任务事件流"，不是"token打字机"。**

很多人理解的流式输出只是"让用户看到token一个一个蹦出来"，这是对LLM聊天场景的窄化理解。真正的生产级Agent流式输出应该暴露完整的任务生命周期事件：

- **状态事件**：Run状态变更（queued → running → waiting_for_input → completed）
- **消息事件**：LLM token增量、完整消息
- **工具事件**：工具调用开始、参数、进度、结果
- **产物事件**：Artifact增量创建、更新、完成
- **错误事件**：工具失败、重试、降级
- **Trace事件**：Step开始/结束、Token用量、耗时

前端需要的不只是最终答案，而是标准化的任务事件流。这也是AG-UI协议出现的原因——它专门定义Agent与前端UI之间的事件协议。

### 跨框架映射

| 概念 | LangGraph Platform | OpenAI Assistants | Agents SDK | AutoGen |
|------|-------------------|------------------|------------|---------|
| **传输协议** | SSE（可恢复） | SSE | Python async generator | 异步生成器 |
| **粒度控制** | Token/节点/自定义 | Run Step / Message | StreamEvent | Message级 |
| **可恢复性** | ✅ Last-Event-ID | ❌ | ❌ | ❌ |
| **多通道** | ✅ messages/events/updates/debug | ✅ 多种event类型 | ✅ 多种事件类型 | ❌ 仅消息 |

### Server vs Library流式能力分水岭

流式输出有一个容易被忽视但极其重要的分水岭：**Server能力 vs Library能力**。

| 能力 | Library流式（本地SDK） | Server流式（API服务） |
|------|---------------------|-------------------|
| **传输** | 内存中的async generator | HTTP SSE / WebSocket |
| **断连恢复** | 不支持（进程内） | 必须支持（Last-Event-ID） |
| **多客户端** | 单消费者 | 多订阅者 |
| **历史回放** | 不支持 | Catch-up机制 |
| **跨进程** | 不支持 | 必须支持 |

> **只要Agent被部署为服务（跨网络访问），流式输出就必须从"内存async generator"升级为"可恢复的SSE事件流"。** 这是LangGraph Platform、A2A、AG-UI都在解决的问题。

### LangGraph Platform可恢复流机制

LangGraph Platform的可恢复流是目前最完整的实现：

1. **Redis Stream持久化**：所有事件被写入Redis Stream，不只是内存中临时生成
2. **Last-Event-ID协议**：客户端断连重连时携带最后收到的event ID，服务端从断点继续发送
3. **两种模式**：
   - **Catch-up回放**：一次性发送断连期间错过的所有事件
   - **Live Tail**：追上后进入实时模式，继续推送新事件
4. **双Stream支持**：run stream（单次执行的事件）和thread stream（整个Thread的所有Run事件）

```
客户端 ──► SSE连接 ──► 服务端发送事件 ──► ...断连...
                                          │
客户端重连 ◄── Last-Event-ID: evt_123 ◄──┘
           │
           └──► 服务端从evt_124开始继续发送
```

### 流式输出本章结论

流式输出回答"客户端如何实时观察Run的进展"。它的核心不是token打字机，而是标准化的任务事件流——状态、消息、工具、产物、错误、Trace都应该以事件形式暴露。

流式能力有一个关键分水岭：Library流式只适合同进程内使用；一旦跨越网络边界，就必须升级为可恢复SSE，支持Last-Event-ID、Catch-up回放和多订阅者。这是生产部署和原型Demo的核心区别之一。

---
