---
id: deepseek-harness-wiki-06
title: DeepSeek Harness Wiki - Agent 循环与事件模型
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
  - external/libs/cordis/packages/core/src/context.ts
  - external/libs/cordis/packages/core/src/events.ts
date: 2026-08-17
tags:
  - deepseek
  - agent
  - harness
  - loop
  - event
  - turn
  - step
  - waterfall
  - invariant
category: learning
maturity: L2
---

# 06 Agent 循环与事件模型

Agent 循环（Agent Loop）是 Harness 的心脏——它决定了输入如何被处理、模型如何被调用、工具如何被执行、结果如何返回。dsh 将循环拆解为极其清晰的 Turn/Step 模型，并在每个关键节点暴露类型化事件，让插件可以在任意环节介入。本章详解这套机制。

## 为什么 Agent 循环是 Harness 核心

Harness 本质上是「模型外面那一层」——模型本身只输出文本，它自己打不开文件、跑不了命令、记不住历史。是 Agent 循环驱动着整个流程：
- 什么时候该调用模型
- 模型返回工具调用时该执行什么
- 工具执行完结果怎么传回给模型
- 什么时候一个回合算结束
- 多轮对话如何保持上下文

不同的循环逻辑决定了 Agent 的「性格」和能力边界：
- 简单的 ReAct 循环：思考→行动→观察→重复
- 带规划的循环：先做计划，再按步骤执行，中途调整
- 多 Agent 协作循环：可以委派子任务给其他 Agent
- 反思循环：执行后自我审查，发现错误自动修正

dsh 的强大之处在于：**这整个循环本身，也只是一个普通插件**。你可以完全替换它，实现任何你想要的调度逻辑。但在替换之前，我们需要先理解默认循环是如何工作的。

## Step 与 Turn：精确定义

dsh 将对话执行过程切分为两个精确的概念：Step 和 Turn。

### Step：最小执行单元

**一个 Step = 一次模型请求 + 这次请求触发的所有工具调用**

这是 Agent 循环的最小执行单元：
1. 组装好要发给模型的消息历史
2. 发起一次模型请求（可以是流式的）
3. 接收模型输出
4. 如果模型输出了工具调用，依次执行这些工具
5. 将工具结果追加回消息历史

一个 Step 结束后，有两种可能：
- 模型认为任务完成，输出了最终回答 → 整个 Turn 结束
- 模型说「我还需要调用更多工具」→ 进入下一个 Step

### Turn：完整对话回合

**一个 Turn = 从认领第一份用户输入开始，到没有任何「欠账」时结束，中间包含零到多个 Step**

Turn 是用户感知到的「一次对话轮次」：
- 你输入一条消息，按下回车 → 一个 Turn 开始
- Agent 思考、调用工具、再思考、再调用工具...经历若干 Step
- Agent 给出最终回答，等待下一条输入 → Turn 结束

Turn 和 Step 的关系：
- 一个 Turn 可以包含 0 个 Step（首次领取被拒绝或改写为空时，仍会关闭一个不含步骤的持久轮次）
- 一个 Turn 通常包含 1 到 N 个 Step
- 简单问答可能只有 1 个 Step（模型直接回答，不调用工具）
- 复杂编程任务可能需要几十个 Step

理解这两个概念是理解事件模型的基础。

## Turn 流程官方精确时序图

默认循环执行一个 Turn 的精确时序如下（官方文本图）：

```text
turn/start
  claim next-step input plus one queued message
  assemble prompt sections + tool schemas
  -&gt; agent/pre-step                   reject | enter(messages)
     reject, or a first enter rewritten empty -&gt; close the turn with no step
     step/start
     append entered messages as user/message
     derive model history from the log
     agent/request -&gt; llm/stream -&gt; assistant/chunk* -&gt; assistant/message
     tool/call* -&gt; tools/pre-execute -&gt; tools/execute -&gt; tools/post-execute -&gt; tool/result*
     step/end
     tools owe another request, or next-step input arrived -&gt; claim -&gt; next step
  -&gt; agent/turn-stopping
turn/end
```

要点说明：
1. Turn 开始时先认领（claim）下一个步骤输入和一条排队消息
2. 组装提示词分区与工具 schema
3. 进入 `agent/pre-step` 瀑布事件，监听器可以 reject 或 enter(messages)
4. 如果被 reject 或首次 enter 被改写为空 → 关闭一个不含步骤的 Turn
5. 正常流程：step/start → 追加消息 → 从日志推导模型历史 → 模型请求流式响应 → 工具执行三阶段 → step/end
6. 如果工具需要再次请求，或有新输入到达 → 认领 → 下一个 Step
7. 最后触发 `agent/turn-stopping` 串行事件，然后 Turn 结束

## 输入到达机制

所有输入通过同一个 inbox 到达驱动器：

- 有些消息会**立即唤醒循环**（如用户主动发送的消息）
- 注入的上下文留在 inbox 中，直到另一条消息将其唤醒
- `agent.inject()` 可注入上下文到下一次获准的请求中

这种设计确保了输入处理的统一性，无论是用户输入、系统注入还是工具返回结果，都走同一条通道。

## 三类事件分发模式

dsh 的事件通过 `@mode` JSDoc 标签记录分发模式，分为三大类：

### 1. 持久会话事件（Session Events）——写入 SessionLog

这些事件是**持久化、写入会话日志**的事实，构成了可重建的历史轨迹：

- `turn/*`：Turn 生命周期事件（turn/start、turn/end）
- `step/*`：Step 生命周期事件（step/start、step/end）
- `user/message`：用户消息追加
- `assistant/*`：助手消息相关（assistant/chunk*、assistant/message）
- `tool/*`：工具相关事件（tool/call*、tool/result*）

持久会话事件的特点：
- 持久化到磁盘，重启会话后可以恢复
- append-only（只追加），不可修改已有事件
- 是 Trajectory 轨迹视图和分叉/回放功能的数据源
- 遵循「模型可见即已记录」的核心不变量

### 2. Waterfall 事件（瀑布型事件）——有 `next()`

瀑布型事件构成了插件拦截流程的主要机制，多个监听者按注册顺序依次执行，每个监听者**必须显式调用 `next()`** 才能传递控制权。

默认循环中的 Waterfall 事件：

| 事件 | 用途 |
|------|------|
| `agent/pre-step` | Step 开始前，决定模型能看到什么 |
| `agent/request` | 发送模型请求前，可修改请求参数 |
| `llm/stream` | 流式输出拦截，处理 chunk |
| `tools/pre-execute` | 工具执行前，可修改参数、权限检查 |
| `tools/execute` | 工具实际执行阶段 |
| `tools/post-execute` | 工具执行后，可修改结果、过滤输出 |

瀑布型事件的特点：
- 多个监听者按注册顺序依次执行
- 每个监听者必须显式调用 `next()` 才能继续
- 不调用 `next()` 则流程中断
- 可以修改传递给下游的数据，或直接返回结果终止流程

### 3. Serial 事件（串行事件）——无 `next()`

与瀑布型事件不同，串行事件**没有 `next()`**，用于投票/聚合逻辑而非流水线传递。

核心 Serial 事件：**`agent/turn-stopping`**

- 在每个 Step 结束后触发
- 回答一个问题：**这个 Turn 应该结束了吗？**
- 每个监听者独立判断，任何一个返回「需要继续」则 Turn 继续
- 所有监听者都认为完成时，Turn 才结束
- 不存在顺序依赖，不需要传递控制权

## `agent/pre-step` 语义详解

`agent/pre-step` 是循环中最关键的决策点，它**决定模型看到什么**：

- 监听器可以**改写已领取的消息**，增删改提示词内容
- 监听器也可以直接**拒绝（reject）**这些消息
- **首次领取被拒绝或被改写为空时，仍会关闭一个不含步骤的持久轮次**，因此日志会记录这次尝试
- 每个步骤读取插件注册的提示词片段和工具 schema

这是插件干预模型输入的主要入口——无论是注入额外上下文、修改工具列表、过滤敏感内容，还是实现权限控制，都在这里完成。

## 运行时不变量（Invariant）

dsh 核心设计遵循一条铁律：**模型可见即已记录**——抵达模型请求的一切都必须能从日志重建。

这条不变量由 `invariants` 包的**运行时断言**强制执行。它意味着：

1. 任何新增的模型可见输入，**必须新增一个会话事件类型**
2. 需要扩展 `SessionEventMap` 类型定义
3. 需要提供从日志渲染（render）该输入的逻辑

这条不变量是会话日志可观测性、轨迹回放、分叉调试等功能的基础——如果模型看到了某样东西但日志里没有，这些功能就会失效。

## 工具执行三阶段

工具执行遵循严格的三阶段 Waterfall 链：

```text
tool/call*
  → tools/pre-execute   # 执行前：参数校验、权限检查、审计
  → tools/execute       # 实际执行：调用工具实现
  → tools/post-execute  # 执行后：结果处理、过滤、错误转换
→ tool/result*
```

> **注意**：事件名称是 `tools/pre-execute` → `tools/execute` → `tools/post-execute`，不是 `tools/before-call` 等其他命名。

### Waterfall 事件使用示例

举个例子，如果你想写一个插件，在每次调用 Shell 工具前自动添加 `set -euo pipefail` 保证脚本安全：

```typescript
ctx.on('tools/pre-execute', async (event, next) =&gt; {
  if (event.tool.name === 'bash') {
    event.tool.args.command = `set -euo pipefail\n${event.tool.args.command}`;
  }
  await next();
});
```

如果你想阻止某个危险命令执行，可以直接抛出错误：

```typescript
ctx.on('tools/pre-execute', async (event, next) =&gt; {
  if (event.tool.name === 'bash' &amp;&amp; event.tool.args.command.includes('rm -rf /')) {
    throw new Error('危险命令被安全插件拦截');
  }
  await next();
});
```

## Loop 本身也是插件

回到「一切皆插件」的核心设计：默认的 Agent 循环实现，本身也只是一个名为 `core/agent-loop` 的普通插件。

### 这意味着什么

1. **你可以完整替换它**：卸载默认循环插件，挂载你自己实现的循环插件，整个 Agent 的行为逻辑就完全变了
2. **你可以扩展它**：通过事件系统在默认循环基础上添加额外逻辑，不需要改动循环本身
3. **你可以有多个循环**：理论上你可以挂载多个循环插件，根据不同场景切换使用

### 为什么这很重要

大多数 Agent 框架把循环硬编码在内核中，你只能通过预留的 hook 在特定节点插入逻辑，但无法改变循环的整体结构。如果官方默认的 ReAct 循环不满足你的需求——比如你想实现：
- 规划-执行-反思（Plan-Execute-Reflect）三阶段循环
- 多 Agent 辩论式循环
- 蒙特卡洛树搜索（MCTS）驱动的循环
- 带人类审批介入点的循环

在传统框架中，你要么 fork 大改，要么忍受框架的限制。在 dsh 中，你只需要写一个新的循环插件。

### 默认循环的价值

默认的 `core/agent-loop` 插件提供了一个经过良好设计的通用循环实现：
- 支持标准的工具调用流程
- 内置流式输出处理
- 与所有官方插件兼容
- 处理了大部分边界情况（错误、超时、取消等）
- 严格执行「模型可见即已记录」不变量

除非你有非常特殊的调度逻辑需求，否则默认循环应该足够使用——而且你依然可以通过事件系统在不替换循环的情况下，定制几乎所有行为。

理解了 Agent 循环和事件模型，我们就掌握了 dsh「如何运行」的核心机制。下一章我们将探讨这套架构最重要的产出物——会话日志与可观测性，以及它为什么被称为 dsh 的「killer feature」。

---

← [05 核心架构](05-architecture-everything-plugin.md) | → [07 会话日志与可观测性](07-session-log-observability.md)
