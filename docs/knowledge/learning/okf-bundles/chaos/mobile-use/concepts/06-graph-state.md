---
type: Concept
title: 图结构与状态管理
description: StateGraph编译、State字段与reducer机制、条件门路由、消息通道隔离、asanitize_update状态清理与遥测
tags: [mobile-use, langgraph, state, reducer, stategraph, telemetry]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: mobile-use-source
    resource: "/references/mobile-use-source.md"
    title: mobile-use 源码
  - id: facts
    resource: "/references/facts.md"
    title: mobile-use 事实清单
---

# 图结构与状态管理

图结构层是 mobile-use 多 Agent 协作的骨架。它基于 LangGraph 的 StateGraph 构建，定义了节点、边、条件路由和共享状态。State 使用 Pydantic 模型配合 Annotated reducer 注解，实现了字段级的状态合并策略——消息累积、快照覆盖、字典合并各有不同的 reducer。

## 图构建

### get_graph 函数

`async def get_graph(ctx: MobileUseContext) -> CompiledStateGraph` 是图构建的唯一入口 [F-190]。它接收 MobileUseContext，创建 StateGraph(State)，注册节点和边，返回编译后的 CompiledStateGraph。

### 节点注册

图共注册 8 个命名节点 [F-191]：

| 节点名 | 实现 | 说明 |
|--------|------|------|
| `planner` | `PlannerNode(ctx)` | 规划节点 |
| `orchestrator` | `OrchestratorNode(ctx)` | 编排节点 |
| `contextor` | `ContextorNode(ctx)` | 上下文采集节点 |
| `cortex` | `CortexNode(ctx)` | 核心决策节点 |
| `executor` | `ExecutorNode(ctx)` | 执行节点 |
| `executor_tools` | `ExecutorToolNode(tools, ...)` | 工具执行节点 |
| `summarizer` | `SummarizerNode(ctx)` | 摘要裁剪节点 |
| `convergence` | `convergence_node` | 汇聚空节点（defer=True） |

ExecutorToolNode 在创建时根据 `ctx.video_recording_enabled` 决定是否添加视频录制工具 [F-114~F-115]。工具列表通过 `get_tools_from_wrappers(ctx, executor_wrappers)` 从包装器生成。

### 边定义

图的边分为普通边和条件边 [F-193~F-198]：

**普通边（固定路由）**：
- `START → planner`：图入口
- `planner → orchestrator`：规划完成后进入编排
- `orchestrator → convergence`：编排完成后到汇聚点
- `contextor → cortex`：感知完成后进入决策
- `executor_tools → summarizer`：工具执行完后裁剪历史
- `summarizer → convergence`：裁剪后到汇聚点

**条件边（动态路由）**：

1. **post_cortex_gate**（cortex 之后）[F-195]：
   - `review_subgoals` → orchestrator：有子目标需要审查完成
   - `execute_decisions` → executor：有结构化决策需要执行
   - 可同时返回两个路径（并行分支）

2. **post_executor_gate**（executor 之后）[F-196]：
   - `invoke_tools` → executor_tools：最后一条 AIMessage 有 tool_calls
   - `skip` → summarizer：无工具调用

3. **convergence_gate**（汇聚点之后）[F-198]：
   - `continue` → contextor：有正在运行的子目标，继续感知-决策循环
   - `replan` → planner：任一子目标失败，需要重新规划
   - `end` → END：所有子目标完成或无运行中子目标

### convergence 节点与 defer

`convergence_node` 是一个返回空字典的函数：

```python
def convergence_node(state: State):
    """Convergence point for parallel execution paths."""
    return {}
```

它标记为 `defer=True`，这是 LangGraph 的特殊配置，表示该节点不立即执行，而是作为并行路径的同步屏障。当 Orchestrator 路径和 Summarizer 路径都到达 convergence 后，才触发 convergence_gate 判断 [F-192]。

## 条件门详解

### post_cortex_gate

```python
def post_cortex_gate(state: State) -> Sequence[str]:
    node_sequence = []
    if len(state.complete_subgoals_by_ids) > 0 or not state.structured_decisions:
        node_sequence.append("review_subgoals")
    if state.structured_decisions:
        node_sequence.append("execute_decisions")
    return node_sequence
```

这个门可以返回字符串列表，意味着 Cortex 可以同时触发子目标审查和决策执行两条并行路径。例如，Cortex 可能判断当前子目标已完成（需要 Orchestrator 标记）并同时产出了下一步操作决策（需要 Executor 执行）[F-195]。

`or not state.structured_decisions` 条件是一个防死锁保护——如果 Cortex 没有产出任何决策，至少要路由到 Orchestrator 重新评估状态。

### post_executor_gate

```python
def post_executor_gate(state: State) -> Literal["invoke_tools", "skip"]:
    messages = state.executor_messages
    if not messages:
        return "skip"
    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        tool_calls = getattr(last_message, "tool_calls", None)
        if tool_calls and len(tool_calls) > 0:
            return "invoke_tools"
    return "skip"
```

检查 executor_messages 通道（而非主 messages 通道）的最后一条消息是否为带 tool_calls 的 AIMessage [F-196]。

### convergence_gate

```python
def convergence_gate(state: State) -> Literal["continue", "replan", "end"]:
    if one_of_them_is_failure(state.subgoal_plan):
        return "replan"
    if all_completed(state.subgoal_plan):
        return "end"
    if not get_current_subgoal(state.subgoal_plan):
        return "end"
    return "continue"
```

优先级：失败重规划 > 全部完成结束 > 无运行中子目标结束 > 继续执行 [F-198]。这确保失败被最快响应，完成状态被正确检测。

## State 模型

`State` 继承 Pydantic BaseModel，使用 `Annotated` 类型注解为每个字段指定 reducer 函数 [F-199][F-200]：

```python
class State(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    remaining_steps: Annotated[int | None, ...] = None
    initial_goal: Annotated[str, ...]
    subgoal_plan: Annotated[list[Subgoal], ...]
    latest_ui_hierarchy: Annotated[list[dict] | None, take_last]
    latest_screenshot: Annotated[str | None, take_last]
    focused_app_info: Annotated[str | None, take_last]
    device_date: Annotated[str | None, take_last]
    structured_decisions: Annotated[str | None, take_last]
    complete_subgoals_by_ids: Annotated[list[str], take_last]
    executor_messages: Annotated[list[AnyMessage], add_messages]
    cortex_last_thought: Annotated[str | None, take_last]
    agents_thoughts: Annotated[list[str], take_last]
    scratchpad: Annotated[dict[str, str], merge_dicts] = {}
```

### Reducer 机制

LangGraph 使用 reducer 函数决定节点返回的更新如何与现有状态合并。

**add_messages**（LangGraph 内置）：
用于 `messages` 和 `executor_messages` 字段。它智能合并消息列表：新消息追加到列表，若消息 ID 已存在则替换，支持 RemoveMessage 删除消息 [F-200]。

**take_last**：

```python
def take_last(a, b):
    return b
```

始终返回新值 b，即新值直接覆盖旧值 [F-201]。用于快照类字段（latest_ui_hierarchy、latest_screenshot、structured_decisions 等）——这些字段只需要最新值，不需要历史累积。

**merge_dicts**：

```python
def merge_dicts(a, b):
    return {**a, **b}
```

合并两个字典，b 的键覆盖 a 的同名键 [F-202]。用于 scratchpad 字段，支持多个工具同时更新不同的笔记键。

### 字段分类

| 分类 | 字段 | Reducer | 生命周期 |
|------|------|---------|---------|
| 对话 | messages | add_messages | 全任务累积 |
| 执行 | executor_messages | add_messages | Cortex 轮次间清空 |
| 规划 | initial_goal | 无（不可变） | 任务开始时设置 |
| 规划 | subgoal_plan | 无（整体替换） | Planner/Orchestrator 更新 |
| 感知 | latest_ui_hierarchy | take_last | 每轮 Contextor 更新，Cortex 清空 |
| 感知 | latest_screenshot | take_last | 同上 |
| 感知 | focused_app_info | take_last | 同上 |
| 感知 | device_date | take_last | 同上 |
| 决策 | structured_decisions | take_last | Cortex 设置，Executor 读取 |
| 决策 | complete_subgoals_by_ids | take_last | Cortex 设置，Orchestrator 读取 |
| 决策 | cortex_last_thought | take_last | Cortex 设置，Executor 读取 |
| 思考 | agents_thoughts | take_last | 各节点更新（整体替换） |
| 记忆 | scratchpad | merge_dicts | 工具读写，跨轮次持久 |
| 控制 | remaining_steps | 无 | 剩余步数 |

### 消息通道隔离

系统维护两个独立的消息通道：

- **messages**：主对话通道，累积完整对话历史，受 Summarizer 裁剪影响
- **executor_messages**：Executor 专用通道，累积工具调用和结果，Cortex 返回时通过 RemoveMessage 清空 [F-061]

这种隔离使得 Cortex 每轮决策时看到的是干净的 executor 状态（只含上一轮工具结果），而主 messages 通道保留完整的规划-决策历史。

## asanitize_update 状态清理

`State.asanitize_update(ctx, update, agent)` 是异步方法，在状态更新应用前进行清理和副作用处理 [F-203]：

1. 检查 update 中是否包含 `agents_thoughts`
2. 统一格式：字符串转为单元素列表，列表过滤 None
3. 若包含 agents_thoughts 但未提供 agent 参数，抛出 ValueError
4. 调用 `_add_agent_thoughts` 为每条思考添加 `[agent_name]` 前缀
5. 通过 `ctx.on_agent_thought` 回调通知外部
6. 若启用了 trace，调用 `record_interaction` 记录到 trace 文件
7. 返回清理后的 update 字典

### _add_agent_thoughts

```python
async def _add_agent_thoughts(ctx, old, new, agent):
    if ctx.on_agent_thought:
        for thought in new:
            await ctx.on_agent_thought(agent, thought)
    named_thoughts = [f"[{agent}] {thought}" for thought in new]
    if ctx.execution_setup and ctx.execution_setup.traces_path:
        await record_interaction(ctx, response=AIMessage(content=str(named_thoughts)))
    return old + named_thoughts
```

为每条思考添加 Agent 名称前缀（如 `[cortex] 点击登录按钮`），支持外部回调实时观察 Agent 思考过程，并可选持久化到 trace [F-204]。

## 常量

```python
RECURSION_LIMIT = 400
MAX_MESSAGES_IN_HISTORY = 25
EXECUTOR_MESSAGES_KEY = "executor_messages"
```

[F-045]

- `RECURSION_LIMIT`：图执行的最大递归步数（LangGraph 的 super-step 上限），TaskRequest 默认 max_steps 使用此值
- `MAX_MESSAGES_IN_HISTORY`：消息历史上限，超过后 Summarizer 裁剪旧消息
- `EXECUTOR_MESSAGES_KEY`：ExecutorToolNode 的 messages_key 参数值，指定工具消息写入 executor_messages 通道

## 图执行模式

Agent.run_task 中通过 `get_graph(context).astream()` 流式执行图 [F-219]：

```python
async for chunk in graph.astream(
    input=initial_state,
    config={"recursion_limit": task.request.max_steps},
    stream_mode=["messages", "custom", "updates", "values"],
):
    ...
```

四种 stream_mode 提供不同粒度的执行事件：

- **messages**：逐 token 的 LLM 消息流（用于实时显示）
- **custom**：自定义事件（通过 StreamWriter 发送）
- **updates**：每个节点的状态更新
- **values**：每次状态变化后的完整状态快照

`recursion_limit` 控制图的最大 super-step 数，防止无限循环。每个节点执行算一个 super-step，400 步足以支撑复杂的多步移动任务。

## 遥测集成

图执行过程中多个节点记录遥测事件：

- **CortexNode**：`telemetry.capture_cortex_decision()` 记录决策 [F-062]
- **ExecutorToolNode**：`telemetry.capture_executor_action()` 记录每个工具调用的成功/失败 [F-154]
- **Agent.init**：`telemetry.capture_agent_initialized()` 记录设备平台和 ID [F-189]
- **Agent.run_task**：任务开始/结束时记录会话事件

遥测使用 PostHog，事件前缀 `mobile_use_`，API Key 硬编码 [F-178]。用户首次运行 CLI 时会被询问是否启用遥测，配置持久化到 `~/.minitap/telemetry.json` [F-179]。环境变量 `MOBILE_USE_TELEMETRY_ENABLED` 优先级高于配置文件 [F-180]。

## 相关概念

- [多 Agent 协作架构](/concepts/01-multi-agent-architecture.md)
- [工具系统与执行节点](/concepts/03-tools-system.md)
- [SDK 双层 API 与生命周期](/concepts/05-sdk-layer.md)
- [LLM 配置与可插拔体系](/concepts/04-llm-configuration.md)
