---
type: Concept
title: 工具系统与执行节点
description: ToolWrapper注册机制、12个设备操作工具与3个scratchpad草稿工具、ExecutorToolNode顺序执行、三级回退定位策略
tags: [mobile-use, tools, executor, toolwrapper, langchain, scratchpad]
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

# 工具系统与执行节点

工具系统是 Executor 节点与设备控制器之间的桥梁。mobile-use 使用 LangChain 的 Tool 抽象，但在其上增加了 ToolWrapper 注册层、统一的成功/失败消息格式化、顺序执行保障和 scratchpad 草稿记忆。系统共注册 15 个核心工具（12 个设备操作工具 + 3 个 scratchpad 草稿工具）和 2 个可选视频工具。

## ToolWrapper 注册机制

### ToolWrapper 数据类

工具不直接注册为 LangChain BaseTool，而是通过 `ToolWrapper` Pydantic 模型包装 [F-140]：

```python
class ToolWrapper(BaseModel):
    tool_fn_getter: Callable[[MobileUseContext], BaseTool]
    on_success_fn: Callable[..., str]
    on_failure_fn: Callable[..., str]
```

- `tool_fn_getter`：接收 MobileUseContext，返回配置好的 BaseTool 实例（延迟创建，因为工具需要访问上下文）
- `on_success_fn`：工具成功后生成返回给 LLM 的消息
- `on_failure_fn`：工具失败后生成错误消息，包含失败详情供 LLM 调整策略

### CompositeToolWrapper

`CompositeToolWrapper` 继承 `ToolWrapper`，新增 `composite_tools_fn_getter` 字段，返回 `list[BaseTool]` [F-141]。它允许一个包装器注册多个相关工具（如视频录制的开始和结束）。

### 工具获取与格式化

`get_tools_from_wrappers(ctx, wrappers)` 遍历包装器列表，对普通 ToolWrapper 调用 `tool_fn_getter(ctx)`，对 CompositeToolWrapper 调用 `composite_tools_fn_getter(ctx)`，返回扁平的 `list[BaseTool]` [F-142]。

`format_tools_list(ctx, wrappers)` 返回逗号分隔的工具名称字符串，用于注入到 Planner 和 Cortex 的 prompt 中，让 LLM 知道有哪些工具可用 [F-145]。

## 工具清单

### 15 个执行工具

`EXECUTOR_WRAPPERS_TOOLS` 列表注册了以下 15 个工具包装器（12 个设备操作 + 3 个草稿工具）[F-142]：

| 工具名 | 用途 |
|--------|------|
| `back` | 按返回键 |
| `open_link` | 打开 URL |
| `tap` | 点击元素（支持三级回退定位） |
| `long_press_on` | 长按元素 |
| `swipe` | 滑动操作 |
| `focus_and_input_text` | 聚焦元素并输入文本 |
| `erase_one_char` | 删除一个字符 |
| `launch_app` | 启动应用 |
| `stop_app` | 终止应用 |
| `focus_and_clear_text` | 聚焦元素并清除文本 |
| `press_key` | 按键（回车/删除等） |
| `wait_for_delay` | 等待指定时间 |
| `save_note` | 保存笔记到 scratchpad |
| `read_note` | 读取 scratchpad 笔记 |
| `list_notes` | 列出所有 scratchpad 笔记 |

### 视频录制工具

`VIDEO_RECORDING_WRAPPERS` 注册 2 个可选工具 [F-143]：

- `start_video_recording`：开始录屏（最长 900 秒）
- `stop_video_recording`：停止录屏并获取视频文件

视频工具仅在 `ctx.video_recording_enabled` 为 True 时添加到 executor_wrappers [F-146]。该标志通过 CLI 的 `--with-video-recording-tools` 或 SDK 的 `with_video_recording_tools()` 启用。

## 工具定义模式

每个 mobile 工具遵循一致的定义模式。以 tap 工具为例 [F-148]：

```python
@tool
def tap(
    agent_thought: str,
    target: Target,
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[State, InjectedState],
) -> Command:
    ...
```

关键要素：

1. **`@tool` 装饰器**：LangChain 的工具装饰器，自动从函数签名和 docstring 生成工具 schema
2. **`agent_thought: str`**：Agent 执行工具前的思考说明，所有工具统一注入此参数 [F-155]
3. **业务参数**：如 `target: Target`，描述操作目标
4. **`InjectedToolCallId`**：注入当前工具调用 ID，用于更新消息
5. **`InjectedState`**：注入 LangGraph State，工具可读写状态
6. **返回 `Command`**：LangGraph 的 Command 对象，用于更新状态（而非简单返回字符串）

工具通过 `state.asanitize_update()` 将 agent_thought 和执行结果加入 `agents_thoughts` 列表，实现思考过程的可追溯 [F-155]。

## Target 类型与三级回退定位

`Target` 类是元素定位的核心参数类型 [F-147]：

```python
class Target(BaseModel):
    resource_id: str | None = None
    resource_id_index: int | None = None
    text: str | None = None
    text_index: int | None = None
    bounds: ElementBounds | None = None
```

model_validator 自动将未指定的索引设为默认值 0。

tap 工具实现**三级回退定位策略** [F-149]：

1. **bounds 坐标**：若 target 提供了 bounds，直接点击坐标中心
2. **resource_id**：若 bounds 失败，按 resource_id 查找元素
3. **text**：若 resource_id 失败，按 text/label 查找元素

每级失败后尝试下一级，所有级别均失败时返回包含所有尝试详情的错误消息。这种策略提高了在不同 UI 结构下的成功率——LLM 可以同时提供 resource_id 和 text 作为备选。

### tap_wrapper 的成功/失败消息

```python
tap_wrapper = ToolWrapper(
    tool_fn_getter=lambda ctx: tap,
    on_success_fn=lambda selector_info: f"Tap on element with {selector_info} was successful.",
    on_failure_fn=lambda attempts: f"Tap failed after trying: {attempts}",
)
```

成功消息简洁确认，失败消息包含所有定位尝试的详情，帮助 LLM 在下一轮调整策略 [F-150]。

## Scratchpad 草稿工具

scratchpad 是 State 中的一个 `dict[str, str]` 字段，使用 `merge_dicts` reducer，为 Agent 提供跨轮次持久化的键值存储 [F-200]。三个草稿工具如下 [F-151]：

### save_note

```python
@tool
def save_note(
    agent_thought: str,
    key: str,
    content: str,
    tool_call_id: ...,
    state: Annotated[State, InjectedState],
) -> Command:
    new_scratchpad = {**state.scratchpad, key: content}
    return Command(update={
        "agents_thoughts": [...],
        "executor_messages": [...],
        "scratchpad": new_scratchpad,
    })
```

更新 `state.scratchpad[key] = content`，返回包含 agents_thoughts、executor_messages、scratchpad 的 Command 更新 [F-152]。

### read_note

根据 key 读取笔记内容，返回值通过 ToolMessage 返回给 LLM。

### list_notes

列出 scratchpad 中所有已保存的 key。

草稿工具使 Agent 能够在多步任务中记录中间结果（如抓取到的数据、已检查的项目），避免依赖 LLM 上下文记忆。

## ExecutorToolNode

`ExecutorToolNode` 继承 LangGraph 的 `ToolNode`，重写了 `_afunc`（异步）和 `_func`（同步）方法 [F-153]。这是工具系统的核心执行器。

### 顺序执行（非并行）

LangGraph 默认的 ToolNode 支持并行执行多个 tool_calls。ExecutorToolNode 改为**顺序执行**：遍历 tool_calls 列表，逐个调用工具，一个工具失败后中止后续调用 [F-153]。这符合移动设备操作的物理约束——不能同时点击两个位置，且前一个操作可能改变 UI 状态导致后一个操作的目标失效。

### 错误处理

`__func` 方法在工具执行失败时 [F-154]：

1. 调用 `_get_erroneous_command` 生成包含错误信息的 ToolMessage
2. 通过 `telemetry.capture_executor_action` 记录失败遥测
3. 中止后续工具调用
4. 将错误消息返回给 Executor LLM，使其能在下一轮调整策略

成功执行时同样记录遥测，包含工具名和执行耗时。

### messages_key

ExecutorToolNode 配置了 `messages_key=EXECUTOR_MESSAGES_KEY`（即 `"executor_messages"`），工具调用消息写入独立的 executor_messages 通道而非主 messages 通道 [F-119]。这使得 Cortex 可以通过 `RemoveMessage(id=REMOVE_ALL_MESSAGES)` 清空 executor 消息而不影响主对话历史。

## 工具与 Agent 的协作流程

```text
Cortex → structured_decisions
    ↓
Executor（LLM bind_tools）→ AIMessage with tool_calls
    ↓
post_executor_gate 检测到 tool_calls
    ↓
ExecutorToolNode 顺序执行：
    for tool_call in tool_calls:
        result = execute_tool(tool_call)
        if result.error: abort
        append ToolMessage to executor_messages
    ↓
Summarizer（裁剪历史）
    ↓
convergence → Contextor（新一轮感知）
```

Planner 在生成计划时通过 `format_tools_list` 知道可用工具列表，Cortex 在决策时也知道工具能力，但实际的工具调用由 Executor LLM 生成——这是一种"知道能做什么"（Planner/Cortex）与"决定怎么做"（Executor）的职责分离。

## 相关概念

- [多 Agent 协作架构](/concepts/01-multi-agent-architecture.md)
- [设备控制抽象层](/concepts/02-device-control.md)
- [图结构与状态管理](/concepts/06-graph-state.md)
- [LLM 配置与可插拔体系](/concepts/04-llm-configuration.md)
