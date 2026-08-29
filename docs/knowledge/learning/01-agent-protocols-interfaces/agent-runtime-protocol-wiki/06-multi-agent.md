---
id: "agent-runtime-protocol-wiki-06"
title: "多 Agent 协作：最碎片化，也最不该过早押注（Part 4）"
source: "微信公众号文章《Agent Protocol：一个生产级的 Agent Runtime 应该包含什么？》（阿里云开发者）https://mp.weixin.qq.com/s/0N-RnpGVy_PLSDHMwAIFNg"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-runtime-protocol-wiki/06-multi-agent.toml"
---
# 06 多 Agent 协作：最碎片化，也最不该过早押注（Part 4）

多 Agent 协作是目前最碎片化、最不该过早押注的维度。不同框架对"多 Agent"的定义、通信模式、状态共享方式差异极大，远未到收敛的时候。

## 通用概念

协议视角下，多 Agent 的本质不是"多个 prompt 互相聊天"，而是多个 Runtime 或多个 Agent 能否基于共同对象交换任务、消息、能力和产物。

**子概念**：
- **通信模式 (Communication Pattern)**：Agent 之间如何传递消息——直接调用、消息总线、共享状态
- **委派模型 (Delegation Model)**：主 Agent 如何把任务分给子 Agent——静态拓扑、动态路由、能力发现
- **状态共享 (State Sharing)**：多个 Agent 如何访问上下文——共享 Thread、隔离上下文、显式传递
- **拓扑结构 (Topology)**：Agent 之间的组织关系——层级、扁平、环形、动态

> **核心建议**：先做好单 Agent 边界，再引入必要协作。很多"多 Agent"需求其实是单 Agent 加上好的工具设计和 Plan-and-Execute 就能解决。

## 五种多 Agent 编排模式

### 模式一：子图嵌套（Subgraph Nesting）

**代表**：LangGraph
- 把一个 Agent 实现为父图中的一个子图节点
- 子图有自己的状态和 Checkpoint
- 父图通过输入输出与子图交互
- 天然支持并行、条件分支、嵌套恢复

**优势**：状态隔离清晰、可复用、可观测性强
**劣势**：拓扑固定、动态性弱
**适用场景**：稳定的工作流、可预测的任务分解

### 模式二：Subagent Task（子 Agent 任务委派）

**代表**：Deep Agents、OpenAI Agents SDK（Handoff as Tool）
- 主 Agent 把一个子任务委派给子 Agent
- 子 Agent 是一次性执行的"能力调用"
- 结果返回给主 Agent 后子 Agent 结束
- 本质上是一个特殊的 Tool Call

**优势**：简单直观、边界清晰、上下文隔离
**劣势**：子 Agent 之间不能直接对话、主 Agent 是瓶颈
**适用场景**：任务分解型工作、专家 Agent 调用

### 模式三：Handoff 接力（Handoff Relay）

**代表**：OpenAI Agents SDK
- 一个 Agent 把控制权完全移交给另一个 Agent
- 移交后原 Agent 不再参与
- 新 Agent 获得完整上下文
- 本质是"路由+控制权转移"

**优势**：专家场景切换自然、各 Agent 职责专一
**劣势**：上下文膨胀、容易形成无限循环、调试困难
**适用场景**：客服路由、多领域专家切换

### 模式四：群聊选择（Group Chat Selection）

**代表**：AutoGen GroupChat
- 多个 Agent 在一个共享对话中
- Selector 决定下一个谁发言
- Agent 之间可以看到彼此的消息
- 支持 RoundRobin、Selector、自定义策略

**优势**：灵活、支持头脑风暴、动态性强
**劣势**：消息膨胀、发言顺序难控制、Token 消耗高
**适用场景**：多角色讨论、创意生成、问题诊断

### 模式五：发布-订阅（Publish-Subscribe）

**代表**：AutoGen Core
- Agent 订阅 Topic、发布 Message
- 发送方不需要知道谁会处理
- 天然支持并行和分布式
- 本质是事件驱动架构

**优势**：完全解耦、高并发、分布式友好、弹性好
**劣势**：调试困难、消息顺序复杂、状态一致性难保证
**适用场景**：大规模多 Agent 系统（10+ Agent）、实时协作

## 跨框架映射

| 概念 | LangGraph | OpenAI Assistants | Agents SDK | AutoGen | Claude SDK |
|------|-----------|------------------|------------|---------|-----------|
| **通信模式** | 子图嵌套+Send API | 不原生支持 | Handoff（工具） | GroupChat/Topic | 不支持 |
| **委派模型** | 子图节点 | Function Call（Handoff） | `handoff()` | `initiate_chats()` | 无 |
| **状态共享** | 父图状态传递 | 共享 Thread | 共享 Session | 共享 GroupChat 上下文 | 无 |
| **拓扑结构** | 任意图 | 单 Agent+工具 | 扁平 Handoff 网 | 群聊/层级 | 单 Agent |
| **并行执行** | Send API fan-out/fan-in | 不支持 | 不支持 | GroupChat 内并行 | 不支持 |
| **分布式** | LangGraph Platform 管理 | 不支持 | 不支持 | `GrpcWorkerAgentRuntime` | 不支持 |

## 五种模式设计决策对比

| 模式 | 核心语义 | 显式建模对象 | 优势 | 劣势 | 典型场景 |
|------|---------|------------|------|------|---------|
| **子图嵌套** | 工作流包含关系 | Subgraph / Parent State | 状态隔离清晰、可恢复、可观测 | 拓扑偏静态 | 复杂工作流、审批流 |
| **Subagent Task** | 一次性能力委派 | Task / Result / Sub-run | 简单直观、上下文自动隔离 | 子 Agent 间不直接对话 | 任务分解、专家调用 |
| **Handoff 接力** | 控制权转移 | Handoff / Active Agent | 专家切换自然、职责专一 | 上下文膨胀、易循环 | 客服路由、多领域助手 |
| **群聊选择** | 多参与者对话 | Participant / Speaker / Message | 灵活、支持讨论 | Token 消耗高、顺序难控 | 头脑风暴、多角色分析 |
| **发布-订阅** | 事件驱动消息 | Topic / Event / Subscription | 完全解耦、分布式、弹性 | 调试极困难、一致性弱 | 大规模系统、实时协作 |

> 这五种模式不是互斥的，可以在同一个系统中组合使用。例如 LangGraph 的 Send API（fan-out/fan-in）可以看作子图嵌套和发布-订阅的中间形态。

## 多 Agent 的核心陷阱

### 陷阱一：过早引入多 Agent

很多场景下，一个配置良好的单 Agent + 明确的工具 + Plan-and-Execute，效果好于多个松散耦合的 Agent。多 Agent 引入的复杂度（消息路由、状态同步、错误传播、死锁检测）往往超过其带来的收益。

### 陷阱二：为了多 Agent 而多 Agent

"我们用了多 Agent 架构"听起来很高级，但如果问题可以用工具调用解决，就不要用 Agent 间通信。Tool Call 是比 Handoff 更简单、更可靠的"Agent 协作"方式。

### 陷阱三：共享状态变成全局变量

多 Agent 共享同一个 Thread/Context 时，如果没有清晰的写入边界和 Reducer 机制，状态会快速变成不可预测的"全局变量"。一个 Agent 的副作用可能破坏另一个 Agent 的假设。

### 陷阱四：忽略观测和调试成本

单 Agent 的 Trace 已经很复杂；多 Agent 的 Trace 需要区分消息来源、追踪 Handoff 链、记录 Subagent Run ID。没有完善的可观测性，多 Agent 系统就是黑盒。

## 本章结论

多 Agent 协作回答"多个 Agent 如何组织起来完成复杂任务"。这是当前最碎片化、实现差异最大、最不该过早押注的维度。

五种模式（子图嵌套/Subagent task/Handoff 接力/群聊选择/发布-订阅）各有适用场景，没有一种会通吃。它们可以在同一个 Runtime 中共存，也可以跨 Runtime 组合。

> **最务实的建议是：先做好单 Agent 边界——清晰的工具协议、健壮的状态管理、可中断恢复、完整的 Trace。单 Agent 能力到顶了，再按需引入最必要的协作模式。大多数"多 Agent 需求"在单 Agent 能力增强后会自然消失。**

---

- 上一章：[工具协议与流式输出](05-tools-streaming.md)
- [下一章：可观测性与可评测性](07-observability-evaluation.md) →
