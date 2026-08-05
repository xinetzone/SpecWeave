# 02 执行模型：Agent如何跑起来（Part 1）

执行模型定义了 Agent 计算如何被编排：什么是执行的基本单元、单元之间如何调度、控制流由谁决定。放到协议视角，它还定义了一个外部请求如何变成内部执行：一条 Message 如何创建 Task/Run，一次 Run 如何拆成多个 Step，每个 Step 如何产生状态、事件和产物。

## 通用概念

**子概念**：
- **执行单元 (Execution Unit)**：一次不可分割的计算步骤——一个 LLM 调用、一次工具执行、一个决策节点
- **调度模型 (Scheduling)**：执行单元的排列方式——顺序、并行、条件分支
- **控制流 (Control Flow)**：谁决定下一步做什么——显式的图边、LLM 的推理、代码逻辑

## 两层模型：Loop承载方式与编排协议

讨论 Agent 执行模型时，最容易混淆的是把不同层级的东西放在一起比较。更清晰的做法是拆成两层：

1. **Runtime Loop 承载方式**：谁拥有主循环，控制流被放在哪种运行时容器里
2. **编排协议模式**：主循环内部哪些语义对象被显式化，哪些 Action 副作用会进入 Runtime 状态机

Graph、Code、Managed 属于第一层，回答 loop 的承载容器；ReAct、Plan-and-Execute、Conversation-style coordination 属于第二层，回答 loop 内部的主导语义对象。

### Loop承载方式

- **图式 Runtime**（LangGraph为代表）：使用构建图的方式来构建条件和边，节点函数、条件边和工具调用仍然由代码实现，这些代码被放进图运行时里，控制流被结构化为节点、边、状态和 checkpoint。它的价值在于给复杂分支、并行、恢复和观测提供稳定运行时边界，是一种基于 Code 的 DSL。
- **代码式 Runtime**（OpenAI Agents SDK、Claude Agent SDK）：控制流由Python代码直接驱动，上手快，工具执行和事件流由SDK托管。
- **托管式 Runtime**（OpenAI Assistants）：用户将runtime托管给平台，最省心，但控制权和可观测性最少。

### 编排协议层

- **ReAct**：最小 Agent loop——Observation 进入上下文，模型完成 Reasoning，再选择 Action，最后把 Result 写回上下文继续推进。这里的 Action 可以是普通业务工具，也可以是带 Runtime 语义的工具，例如更新计划、发送消息、路由、handoff、请求人类确认。
- **Plan-and-Execute**：关键是把 Plan / Todo / Step / Progress 提升为显式状态。计划依然可以由 ReAct 的 update_plan() 或 update_todo() 触发，但 Runtime 会把这些副作用纳入进度展示、checkpoint、恢复、审计和评测。
- **Conversation-style coordination**：关键是把 Participant / Message / Route / Handoff / Speaker 提升为显式状态。transfer_to_agent() 可以表现为一次工具调用，同时触发 active agent、权限边界、上下文可见性和 trace 归属的状态迁移。它的核心语义来自持续参与者之间的消息协议，而非一次性调用对象。

这也解释了为什么 Agent 可以作为工具存在。子 Agent 被一次性调用并返回结果时，更接近 capability invocation；多个 Agent 以持续身份参与同一段消息协议，订阅、响应、修正彼此的消息时，更接近 conversation-style coordination。

## Agent Harness：Protocol/Runtime能力产品化

这里还有 Runtime 和 Framework 之间的层：**Agent Harness**。它不是主线之外的新概念，而是 Protocol/Runtime 能力产品化后的应用层。LangChain 官方把 Deep Agents SDK 归为 harness：它基于 LangGraph runtime 封装高层电池包，把 planning、todo、subagents、filesystem、context management、HITL、streaming、memory、permissions 组合成一个开箱即用的复杂任务 Agent。

Harness 的价值是**易用性**：它把原本需要开发者自己组装的 Runtime 能力，预先打包成一套默认可用的工作方式。Deep Agents 的优势就在这里——你不需要从零设计 todo list、subagent task、virtual filesystem、backend 和 permission model，就能获得一个接近 Claude Code 使用体验的长任务 Agent。

Claude Agent SDK 走的是另一种路线：它直接复用 Claude Code 二进制能力，因此可以获得成熟的代码 Agent 体验、文件操作、权限模型和工具链集成；对应的限制是，它的执行环境、工具边界、可移植性和可观测性会更强地绑定到 Claude Code 的产品形态。

### Harness体验对象与协议对象对应

| Harness体验对象 | 回扣到的协议对象 | 说明 |
|----------------|----------------|------|
| **Todo / Plan** | Step / Event | 把长任务进度变成可观察、可恢复的步骤 |
| **Subagent task** | Run / Step / Artifact | 把委派任务变成可追踪的子执行和结果 |
| **Virtual filesystem / Workspace** | Artifact / Checkpoint | 把中间结果、文件和最终产物沉淀到可恢复状态 |
| **Skill** | Tool / Artifact / Metadata | 把可复用能力包变成 Runtime 可发现的能力 |
| **Permission / HITL** | Interrupt / Resume / Event | 把高风险动作放入中断恢复状态机 |

> **生产环境推荐**：使用这些成熟框架的时候，手里有源码能够覆写乃至重写很有必要，不然复杂的业务场景很难被都满足。相比强绑定二进制产品形态的路线，生产环境更推荐使用 Deep Agents 这类基于开源Runtime的Harness。

Harness 把 Runtime 能力打包成默认可用的长任务 Agent 体验，解决"能不能做"之外的"能不能低成本做好"。

## 跨框架映射

| 概念 | LangGraph | OpenAI Assistants | Agents SDK | AutoGen | Claude SDK |
|------|-----------|------------------|------------|---------|-----------|
| **执行单元** | Node（函数/Runnable） | Run Step | Agent turn | Agent message handler | Agent turn |
| **调度模型** | Graph（DAG + 循环） | 服务端托管循环 | Python 控制流 | 对话协议（轮转/选择） | 代码驱动循环 |
| **控制流** | 条件边 / Command | 服务端决定（不透明） | Handoff / 代码分支 | Selector / RoundRobin | 工具结果驱动 LLM |
| **并行执行** | Send API（fan-out/fan-in） | 不支持 | 不支持 | GroupChat 内并行 | 不支持 |
| **执行容器** | Thread + Run | Thread + Run | Runner 上下文 | Runtime + Team | Session |

## Runtime Loop：Agent的隐藏主循环

很多 Agent 框架表面 API 差异很大，但内部都存在一个主循环（伪代码）：

```python
while not done:
    messages = load_context()
    model_output = call_llm(messages, tools)
    
    if model_output.tool_calls:
        tool_results = execute_tools(model_output.tool_calls)
        append_results(tool_results)
        continue
    
    if model_output.handoff:
        transfer_to_next_agent()
        continue
    
    if model_output.needs_human:
        interrupt()
        break
    
    return final_output
```

> Runtime Loop 在内部决定下一步调用模型、执行工具、切换 Agent、等待人类还是返回结果；协议外部则需要把这些分支稳定表达成 Task / Run 状态。

### 循环拥有者四类对比

| 拥有者 | 代表 | 特点 |
|--------|------|------|
| **开发者拥有循环** | Responses API、Claude Client SDK | 灵活，但状态、重试、工具执行都要自己写 |
| **SDK 拥有循环** | OpenAI Agents SDK、Claude Agent SDK | 上手快，工具执行和事件流由 SDK 托管 |
| **图引擎拥有循环** | LangGraph | 循环被拆成节点、边、Checkpoint 和 Pregel-style SuperStep |
| **服务端拥有循环** | OpenAI Assistants | 最省心，但控制权和可观测性最少 |

判断一个框架是不是 Runtime，不要看它是否能调模型，而要看它是否拥有这个循环。

从协议角度看，这个循环就是 Task/Run 状态机的内部实现：

```
SUBMITTED ──► WORKING ──► INPUT_REQUIRED ──► WORKING ──► COMPLETED
                      │              │
                      │              └── 等待 Message / Resume / Authorization
                      ├──► FAILED
                      └──► CANCELED
```

A2A 把这类状态显式放进 Task；OpenAI 把它放进 Run；LangGraph Server 则通过 Thread/Run stream 暴露生命周期事件。对象名不同，但协议都需要向客户端回答同一个问题：**这次执行现在处于什么状态，客户端下一步能做什么？**

## 事件驱动Runtime（AutoGen Core模式）

AutoGen Core 把 Agent 执行看成事件驱动系统。Agent 不再只是"被调用的函数"，而是订阅 Topic、接收 Message、发布 Message 的 Actor。

**价值**：
- **解耦**：发送方不需要知道谁会处理消息
- **并发**：多个 Agent 可以订阅同一个 Topic 并行响应
- **分布式**：Runtime 可以演进成跨进程、跨机器的消息总线
- **弹性**：失败的 Agent 可以独立重启，不必拖垮整个工作流

**代价**：调试困难、消息顺序复杂、状态一致性变差。适用于大规模（超过10个Agent协作）多 Agent 系统。

## Workspace/Sandbox：执行环境也是状态

新一代 Agent Runtime 开始把"工作区"作为一等概念。OpenAI Agents SDK 的 Sandbox agents、Claude Agent SDK 的文件工具和权限模式，本质上都在回答同一个问题：Agent 执行时能读写哪些外部资源？

Deep Agents 把这一点推得更彻底：它默认提供 virtual filesystem，并支持 StateBackend、FilesystemBackend、StoreBackend、CompositeBackend 等可插拔 backend。也就是说，文件不只是工具调用的副作用，而是 Agent 管理上下文、沉淀中间结果、组织长任务产物的核心状态层。

### 四层状态对比

| 类型 | 例子 | 生命周期 | 风险 |
|------|------|---------|------|
| **Prompt Context** | 消息、系统提示词 | 单次模型调用 | 泄漏、污染 |
| **Runtime State** | Checkpoint、Session 变量 | 跨步骤/跨请求 | 版本不一致 |
| **Workspace State** | 文件、代码仓库、浏览器页面 | 跨工具调用 | 破坏性副作用 |
| **External State** | 数据库、工单、支付系统 | Runtime 外部 | 真实业务影响 |

因此，生产 Runtime 不能只管理"对话历史"，还要管理工作区隔离、文件变更审计、权限审批和副作用回滚。

## 设计决策分析

### Loop承载方式对比

| Loop 承载方式 | 容易做到 | 困难做到 | 典型场景 |
|--------------|---------|---------|---------|
| **图式 Runtime** | 分支、并行、可视化、断点调试 | 简单的线性对话（过度建模） | 复杂工作流、审批流、研报生成 |
| **代码式 Runtime** | 灵活、学习曲线低、调试直观 | 持久化、断线恢复、可视化 | 简单 Agent、脚本任务 |
| **托管式 Runtime** | 零运维、开箱即用 | 自定义执行逻辑、成本控制 | 快速原型、客服 Bot |

### 编排契约对比

| 编排契约 | 显式建模对象 | 典型触发形式 | Runtime 需要管理什么 |
|---------|------------|------------|-------------------|
| **ReAct Tool Loop** | Tool Call / Observation / Result | LLM 选择工具 | 工具执行、结果回写、错误作为数据 |
| **Plan-and-Execute** | Plan / Todo / Step / Progress | 工具调用或调度器触发 | 计划持久化、进度更新、计划修正、阶段恢复 |
| **Conversation-style coordination** | Participant / Message / Route / Handoff / Speaker | 工具调用或消息路由触发 | 发言顺序、路由、权限切换、上下文可见性、trace 归属 |
| **Manager-Worker** | Task / Subtask / Assignment / Result | 工具调用或调度器触发 | 子任务分派、上下文隔离、结果汇总、失败重试 |

## 本章结论

执行模型回答"一个 Run 如何被调度"。后面的状态、工具、流式、中断和观测能力，都是围绕这条 Runtime Loop 展开的。

执行模型不会统一。Loop 承载方式回答主循环放在哪里，编排协议模式回答哪些 Action 副作用会被 Runtime 提升为状态对象。复杂工作流适合图式 Runtime，简单任务适合代码式 Runtime，快速原型适合托管式 Runtime；ReAct、Plan-and-Execute、Conversation-style coordination 可以运行在不同 Runtime 之上，也可以在同一个 Runtime 内叠加。

作为开发者，关键不是押注某一种 loop，而是让状态管理、工具调用、流式输出独立于具体执行模型。这样从代码式 Runtime 切到图式 Runtime，或从 ReAct 切到 Plan-and-Execute 时，其他能力仍然可以复用。

---
