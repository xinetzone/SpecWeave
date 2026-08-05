# 06 多Agent协作：最碎片化，也最不该过早押注（Part 4）

多Agent协作是目前最碎片化、最不该过早押注的维度。不同框架对"多Agent"的定义、通信模式、状态共享方式差异极大，远未到收敛的时候。

## 通用概念

**子概念**：
- **通信模式 (Communication Pattern)**：Agent之间如何传递消息——直接调用、消息总线、共享状态
- **委派模型 (Delegation Model)**：主Agent如何把任务分给子Agent——静态拓扑、动态路由、能力发现
- **状态共享 (State Sharing)**：多个Agent如何访问上下文——共享Thread、隔离上下文、显式传递
- **拓扑结构 (Topology)**：Agent之间的组织关系——层级、扁平、环形、动态

> **核心建议**：先做好单Agent边界，再引入必要协作。很多"多Agent"需求其实是单Agent加上好的工具设计和Plan-and-Execute就能解决。

## 五种多Agent编排模式

### 模式一：子图嵌套（Subgraph Nesting）

**代表**：LangGraph
- 把一个Agent实现为父图中的一个子图节点
- 子图有自己的状态和Checkpoint
- 父图通过输入输出与子图交互
- 天然支持并行、条件分支、嵌套恢复

**优势**：状态隔离清晰、可复用、可观测性强
**劣势**：拓扑固定、动态性弱
**适用场景**：稳定的工作流、可预测的任务分解

### 模式二：Subagent Task（子Agent任务委派）

**代表**：Deep Agents、OpenAI Agents SDK（Handoff as Tool）
- 主Agent把一个子任务委派给子Agent
- 子Agent是一次性执行的"能力调用"
- 结果返回给主Agent后子Agent结束
- 本质上是一个特殊的Tool Call

**优势**：简单直观、边界清晰、上下文隔离
**劣势**：子Agent之间不能直接对话、主Agent是瓶颈
**适用场景**：任务分解型工作、专家Agent调用

### 模式三：Handoff接力（Handoff Relay）

**代表**：OpenAI Agents SDK
- 一个Agent把控制权完全移交给另一个Agent
- 移交后原Agent不再参与
- 新Agent获得完整上下文
- 本质是"路由+控制权转移"

**优势**：专家场景切换自然、各Agent职责专一
**劣势**：上下文膨胀、容易形成无限循环、调试困难
**适用场景**：客服路由、多领域专家切换

### 模式四：群聊选择（Group Chat Selection）

**代表**：AutoGen GroupChat
- 多个Agent在一个共享对话中
- Selector决定下一个谁发言
- Agent之间可以看到彼此的消息
- 支持RoundRobin、Selector、自定义策略

**优势**：灵活、支持头脑风暴、动态性强
**劣势**：消息膨胀、发言顺序难控制、Token消耗高
**适用场景**：多角色讨论、创意生成、问题诊断

### 模式五：发布-订阅（Publish-Subscribe）

**代表**：AutoGen Core
- Agent订阅Topic、发布Message
- 发送方不需要知道谁会处理
- 天然支持并行和分布式
- 本质是事件驱动架构

**优势**：完全解耦、高并发、分布式友好、弹性好
**劣势**：调试困难、消息顺序复杂、状态一致性难保证
**适用场景**：大规模多Agent系统（10+Agent）、实时协作

## 跨框架映射

| 概念 | LangGraph | OpenAI Assistants | Agents SDK | AutoGen | Claude SDK |
|------|-----------|------------------|------------|---------|-----------|
| **通信模式** | 子图嵌套+Send API | 不原生支持 | Handoff（工具） | GroupChat/Topic | 不支持 |
| **委派模型** | 子图节点 | Function Call（Handoff） | `handoff()` | `initiate_chats()` | 无 |
| **状态共享** | 父图状态传递 | 共享Thread | 共享Session | 共享GroupChat上下文 | 无 |
| **拓扑结构** | 任意图 | 单Agent+工具 | 扁平Handoff网 | 群聊/层级 | 单Agent |
| **并行执行** | Send API fan-out/fan-in | 不支持 | 不支持 | GroupChat内并行 | 不支持 |

## 五种模式设计决策对比

| 模式 | 核心语义 | 显式建模对象 | 优势 | 劣势 | 典型场景 |
|------|---------|------------|------|------|---------|
| **子图嵌套** | 工作流包含关系 | Subgraph / Parent State | 状态隔离清晰、可恢复、可观测 | 拓扑偏静态 | 复杂工作流、审批流 |
| **Subagent Task** | 一次性能力委派 | Task / Result / Sub-run | 简单直观、上下文自动隔离 | 子Agent间不直接对话 | 任务分解、专家调用 |
| **Handoff接力** | 控制权转移 | Handoff / Active Agent | 专家切换自然、职责专一 | 上下文膨胀、易循环 | 客服路由、多领域助手 |
| **群聊选择** | 多参与者对话 | Participant / Speaker / Message | 灵活、支持讨论 | Token消耗高、顺序难控 | 头脑风暴、多角色分析 |
| **发布-订阅** | 事件驱动消息 | Topic / Event / Subscription | 完全解耦、分布式、弹性 | 调试极困难、一致性弱 | 大规模系统、实时协作 |

> 这五种模式不是互斥的，可以在同一个系统中组合使用。例如LangGraph的Send API（fan-out/fan-in）可以看作子图嵌套和发布-订阅的中间形态。

## 多Agent的核心陷阱

### 陷阱一：过早引入多Agent

很多场景下，一个配置良好的单Agent + 明确的工具 + Plan-and-Execute，效果好于多个松散耦合的Agent。多Agent引入的复杂度（消息路由、状态同步、错误传播、死锁检测）往往超过其带来的收益。

### 陷阱二：为了多Agent而多Agent

"我们用了多Agent架构"听起来很高级，但如果问题可以用工具调用解决，就不要用Agent间通信。Tool Call是比Handoff更简单、更可靠的"Agent协作"方式。

### 陷阱三：共享状态变成全局变量

多Agent共享同一个Thread/Context时，如果没有清晰的写入边界和Reducer机制，状态会快速变成不可预测的"全局变量"。一个Agent的副作用可能破坏另一个Agent的假设。

### 陷阱四：忽略观测和调试成本

单Agent的Trace已经很复杂；多Agent的Trace需要区分消息来源、追踪Handoff链、记录Subagent Run ID。没有完善的可观测性，多Agent系统就是黑盒。

## 本章结论

多Agent协作回答"多个Agent如何组织起来完成复杂任务"。这是当前最碎片化、实现差异最大、最不该过早押注的维度。

五种模式（子图嵌套/Subagent task/Handoff接力/群聊选择/发布-订阅）各有适用场景，没有一种会通吃。它们可以在同一个Runtime中共存，也可以跨Runtime组合。

> **最务实的建议是：先做好单Agent边界——清晰的工具协议、健壮的状态管理、可中断恢复、完整的Trace。单Agent能力到顶了，再按需引入最必要的协作模式。大多数"多Agent需求"在单Agent能力增强后会自然消失。**

---
