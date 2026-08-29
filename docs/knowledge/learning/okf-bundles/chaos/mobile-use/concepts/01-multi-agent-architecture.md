---
type: Concept
title: 多 Agent 协作架构
description: 9个Agent节点的职责划分、LangGraph图节点与边、条件门路由、子目标状态机与闭环执行流程
tags: [mobile-use, agent, langgraph, planner, orchestrator, cortex, executor, contextor]
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

# 多 Agent 协作架构

mobile-use 的智能核心是一个基于 LangGraph 构建的多 Agent 状态图。系统将"控制手机"这一复杂认知任务分解为 7 个图节点和 3 个工具型异步函数，每个节点有独立的 prompt、LLM 配置和结构化输出类型，通过共享 State 对象协作。

## Agent 节点全景

系统共包含 9 个 Agent 单元，其中 7 个注册为 LangGraph 节点，3 个为按需调用的工具函数 [F-050]：

| Agent | 类型 | 职责 | LLM |
|-------|------|------|-----|
| **PlannerNode** | 图节点 | 将用户目标分解为有序子目标列表 | 是 |
| **OrchestratorNode** | 图节点 | 推进子目标状态机，审查完成情况，决定重规划 | 是 |
| **ContextorNode** | 图节点 | 采集屏幕 UI 层级、截图、前台应用、设备日期 | 是（应用锁定验证） |
| **CortexNode** | 图节点 | 核心决策：基于视觉和 UI 信息产出结构化操作决策 | 是（最强模型） |
| **ExecutorNode** | 图节点 | 将决策绑定工具，生成 tool_calls | 是 |
| **ExecutorToolNode** | 图节点 | 顺序执行工具调用，处理成功/失败结果 | 否 |
| **SummarizerNode** | 图节点 | 消息历史裁剪，防止上下文溢出 | 否（纯规则） |
| **hopper()** | 工具函数 | 从非结构化数据中提取指定信息 | 是 |
| **outputter()** | 工具函数 | 任务结束后生成最终结构化输出 | 是 |
| **analyze_video()** | 工具函数 | 分析屏幕录制视频内容 | 是（Gemini 视觉） |

所有图节点 Agent 类均实现统一接口：构造函数接收 `MobileUseContext`，`__call__` 方法接收 `State` 并返回状态更新字典 [F-051]。节点方法使用 `@wrap_with_callbacks` 装饰器，在执行前后自动记录日志和遥测 [F-052]。

## 图结构与边

图由 `get_graph(ctx)` 异步函数构建，返回编译后的 `CompiledStateGraph` [F-190]。节点注册如下：

```text
START → planner → orchestrator → convergence
                contextor → cortex
                cortex → (条件) → orchestrator [review_subgoals]
                                → executor [execute_decisions]
                executor → (条件) → executor_tools [invoke_tools]
                                 → summarizer [skip]
                executor_tools → summarizer → convergence
                convergence → (条件) → contextor [continue]
                                    → planner [replan]
                                    → END [end]
```

### 三个条件门

**post_cortex_gate**（Cortex 之后）：检查 Cortex 输出。若 `complete_subgoals_by_ids` 非空或 `structured_decisions` 为空，路由到 Orchestrator 审查子目标；若有结构化决策，路由到 Executor 执行。两个路径可同时激活（返回字符串列表），实现并行分支 [F-195]。

**post_executor_gate**（Executor 之后）：检查 executor_messages 最后一条消息。若是 AIMessage 且包含 tool_calls，路由到 ExecutorToolNode 执行工具；否则路由到 Summarizer 跳过工具执行 [F-196]。

**convergence_gate**（汇聚点）：检查子目标计划整体状态。任一子目标失败 → 回到 Planner 重规划；全部完成 → 到达 END；有正在运行的子目标 → 回到 Contextor 继续感知-决策循环 [F-198]。

### convergence 节点

`convergence_node` 是一个返回空字典 `{}` 的空操作节点，标记为 `defer=True`。它的作用是作为并行执行路径的汇聚同步点——Orchestrator 路径和 Executor→Summarizer 路径在此汇合后，由 convergence_gate 统一判断下一步 [F-192]。

## 各节点详解

### PlannerNode（规划者）

Planner 是图执行的第一个节点，负责将高层目标分解为可执行的子目标序列。它在 prompt 中注入：executor 可用工具列表（通过 `format_tools_list`）、设备平台信息、锁定应用包名、当前前台应用 [F-056]。LLM 返回 `PlannerOutput`，包含 `subgoals: list[PlannerSubgoalOutput]`，每个子目标有 id 和 description。节点将其转换为 `Subgoal` 对象列表，初始状态设为 `SubgoalStatus.NOT_STARTED` [F-055]。

当 convergence_gate 判定需要重规划时，图边回到 Planner，此时 Planner 可基于失败原因调整计划。

### OrchestratorNode（编排者）

Orchestrator 管理子目标的生命周期。其核心逻辑在 `__call__` 方法中 [F-057]：

1. 若无正在进行的子目标，启动下一个 NOT_STARTED 子目标（标记为 PENDING）
2. 若收到 `complete_subgoals_by_ids`（来自 Cortex），调用 LLM 审查这些子目标是否真正完成
3. 根据 LLM 返回的 `OrchestratorOutput`（completed_subgoal_ids、needs_replaning、reason），将子目标标记为 SUCCESS 或 FAILURE，或触发重规划

子目标状态枚举为 `NOT_STARTED → PENDING → SUCCESS/FAILURE` [F-074]。

### ContextorNode（上下文采集者）

Contextor 是"感知"节点，每轮循环开始时采集设备实时状态 [F-065]：

- 调用 `device_controller.get_screen_data()` 获取 UI 层级和截图（base64）
- 调用 `get_current_foreground_package_async()` 获取当前前台应用
- 调用 `get_device_date()` 获取设备日期

这些数据写入 State 的 `latest_ui_hierarchy`、`latest_screenshot`、`focused_app_info`、`device_date` 字段，供 Cortex 决策使用。

Contextor 还包含应用锁定验证逻辑：当配置了 `locked_app_package` 且检测到当前应用不符时，调用 LLM 决定是否重新启动应用，返回 `ContextorOutput`（should_relaunch_app、reasoning）[F-066][F-067]。

### CortexNode（大脑皮层）

Cortex 是系统的核心决策节点，也是唯一接收截图的节点。它接收 [F-059]：

- 当前 UI 层级
- 压缩后的截图（通过 `create_device_controller` 获取控制器并压缩）
- Executor 的上一轮反馈
- 当前子目标描述

Cortex 输出 `CortexOutput`，包含：
- `decisions`：给 Executor 的结构化操作指令
- `decisions_reason`：决策理由
- `goals_completion_reason`：目标完成原因
- `complete_subgoals_by_ids`：认为已完成的子目标 ID 列表

Cortex 返回时执行关键的"工作记忆清理"：清空 `latest_ui_hierarchy`、`latest_screenshot`、`focused_app_info`、`device_date`，并通过 `RemoveMessage(id=REMOVE_ALL_MESSAGES)` 清空 executor_messages [F-061]。这确保每轮决策只携带当前屏幕信息，避免上下文膨胀。

### ExecutorNode（执行者）

Executor 接收 Cortex 的 `structured_decisions`，使用 `llm.bind_tools()` 绑定所有可用工具，将决策转化为具体的 tool_calls [F-063]。它将 `cortex_last_thought`、`structured_decisions` 和 `executor_messages`（历史工具结果）作为消息发送给 LLM [F-064]。

Google 模型有特殊处理：不支持 `parallel_tool_calls` 参数，Executor 在绑定工具时会检测 provider 并跳过该参数 [F-175]。

### ExecutorToolNode（工具执行节点）

ExecutorToolNode 继承 LangGraph 的 `ToolNode`，重写了 `_afunc`（异步）和 `_func`（同步）方法 [F-153]。与默认 ToolNode 并行执行多个工具调用不同，它**顺序执行** tool_calls——一个工具失败后中止后续调用。失败时调用 `_get_erroneous_command` 生成错误消息，并通过 `telemetry.capture_executor_action` 记录成功/失败遥测 [F-154]。

### SummarizerNode（摘要者）

Summarizer 不使用 LLM，是纯规则节点。当 executor_messages 数量超过 `MAX_MESSAGES_IN_HISTORY`（25 条）时，删除旧的 ToolMessage 和 HumanMessage，保留最近的对话上下文 [F-068]。这是一种简单但有效的上下文窗口管理策略。

## 工具型 Agent

### hopper（信息漏斗）

`hopper(ctx, request, data)` 是异步函数，用于从非结构化数据中提取特定信息。例如，从网页内容或长文本中提取价格、日期等字段。它通过 `is_utils=True` 获取独立配置的 LLM，返回 `HopperOutput`（found、output、reason）[F-069][F-070]。

### outputter（输出器）

`outputter(ctx, output_config, graph_output)` 在任务结束后生成最终输出。支持两种模式 [F-072]：
- `structured_output`：Pydantic 模型类或 dict schema，LLM 返回符合 schema 的结构化数据
- `output_description`：自然语言描述期望的输出格式

当两者同时提供时，structured_output 优先并发出警告 [F-044]。

### analyze_video（视频分析）

`analyze_video(ctx, video_path, prompt)` 使用 Gemini 视频模型分析屏幕录制内容，超时 120 秒 [F-073]。这是一个可选功能，仅当 `video_analyzer` 在 LLM 配置中启用且 `--with-video-recording-tools` 标志开启时可用。

## Agent 通用机制

### Prompt 模板

所有使用 LLM 的 Agent 都使用 Jinja2 模板渲染 prompt，模板文件为同目录下的 `.md` 文件（如 `planner.md`、`cortex.md`、`human.md`）[F-053]。模板中可注入设备信息、工具列表、当前状态等变量。

### LLM 获取与 fallback

每个 Agent 通过 `get_llm(ctx=self.ctx, name="<agent_name>")` 获取 LLM 实例 [F-054]。返回的 LLM 配置了 `with_structured_output(<OutputType>)` 以强制结构化输出。主备 LLM 切换通过 `with_fallback(main_call, fallback_call)` 异步泛型函数实现：先执行主模型，失败或返回 None 时执行 fallback 模型 [F-171]。

### 回调装饰器

`@wrap_with_callbacks` 装饰器为每个节点添加统一的 before/on_success/on_failure 日志记录和遥测捕获，确保图执行过程的可观测性 [F-052]。

## 相关概念

- [图结构与状态管理](/concepts/06-graph-state.md)
- [工具系统与执行节点](/concepts/03-tools-system.md)
- [LLM 配置与可插拔体系](/concepts/04-llm-configuration.md)
- [设备控制抽象层](/concepts/02-device-control.md)
