---
type: Concept
title: Agent 类型体系
description: LoopAgent、ParallelAgent、SequentialAgent 三种组合 Agent 与 SuperviseAgent 监督模式的实现差异与使用场景
tags: [veadk, agent-types, loop, parallel, sequential, supervisor]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: veadk-source
    resource: "/references/veadk-source.md"
    title: veadk-python 源码
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# Agent 类型体系

veadk-python 提供四种 Agent 类型来组织多 Agent 协作拓扑：基础 `Agent`、`LoopAgent`、`ParallelAgent`、`SequentialAgent`，以及通过监督者 Flow 实现的 `SuperviseAgent` 模式。前三者直接继承 Google ADK 的对应类并添加 veadk 特有字段，监督者模式则通过自定义 Flow 在 LLM 调用前后注入建议。

## 继承体系

```text
google.adk.agents.LlmAgent
    └── veadk.Agent

google.adk.agents.LoopAgent
    └── veadk.agents.LoopAgent

google.adk.agents.ParallelAgent
    └── veadk.agents.ParallelAgent

google.adk.agents.SequentialAgent
    └── veadk.agents.SequentialAgent
```

三种组合 Agent 均通过 `model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")` 允许任意类型和额外字段 [F-046~F-048]。

## LoopAgent

`LoopAgent` 定义于 `veadk/agents/loop_agent.py`，继承自 `google.adk.agents.LoopAgent` [F-046]。

**核心字段**：

| 字段 | 默认值 |
|------|--------|
| `name` | `"veLoopAgent"` |
| `description` | `DEFAULT_DESCRIPTION` |
| `instruction` | `DEFAULT_INSTRUCTION` |
| `sub_agents` | `[]`（`exclude=True`） |
| `tracers` | `[]` |

`model_post_init` 调用父类初始化并记录日志 [F-046]。模块导入时调用 `patch_asyncio()` [F-128]。

**行为特征**：LoopAgent 按照子代理列表顺序循环执行，直到满足终止条件（如最大循环次数或 LLM 判定任务完成）。适用于需要多轮迭代改进的任务，如"写作→审校→修改"循环。

## ParallelAgent

`ParallelAgent` 定义于 `veadk/agents/parallel_agent.py`，继承自 `google.adk.agents.ParallelAgent` [F-047]。

**核心字段**与 LoopAgent 相同，默认 `name` 为 `"veParallelAgent"`。

**特殊行为**：`model_post_init` 中若 `tracers` 非空，会记录 OpenTelemetry 上下文错误警告 [F-047]。这是因为并行执行时多个子 Agent 可能在不同的异步任务中运行，OpenTelemetry 的上下文传播需要特殊处理。

**行为特征**：ParallelAgent 同时向所有子代理分发相同的输入，收集各自的结果。适用于可并行的独立子任务，如多路信息检索、多视角分析。

## SequentialAgent

`SequentialAgent` 定义于 `veadk/agents/sequential_agent.py`，继承自 `google.adk.agents.SequentialAgent` [F-048]。

**核心字段**与 LoopAgent 相同，默认 `name` 为 `"veSequentialAgent"`。

`model_post_init` 调用父类初始化并记录日志 [F-048]。模块导入时同样调用 `patch_asyncio()` [F-128]。

**行为特征**：SequentialAgent 按子代理列表顺序依次执行，前一个子代理的输出作为后一个的输入。适用于流水线式任务，如"搜索→摘要→翻译→格式化"。

## 三种组合 Agent 的对比

| 特性 | LoopAgent | ParallelAgent | SequentialAgent |
|------|-----------|---------------|-----------------|
| 执行方式 | 循环迭代 | 同时并发 | 顺序传递 |
| 默认名称 | `veLoopAgent` | `veParallelAgent` | `veSequentialAgent` |
| 子代理输出关系 | 上一轮→下一轮 | 各自独立 | 前一个→后一个 |
| Tracers 警告 | 无 | 有（OTel 上下文） | 无 |
| 适用场景 | 迭代改进 | 独立并行 | 流水线处理 |

## RemoteVeAgent

`RemoteVeAgent` 在 `AgentBuilder` 的 `AGENT_TYPES` 映射表中注册 [F-042]，定义于 `veadk/a2a/remote_ve_agent.py`。它是 A2A（Agent-to-Agent）协议的客户端代理，允许将远程部署的 Agent 当作本地子代理使用。远程 Agent 通过 A2A 协议通信，其 AgentCard 通过 `get_agent_card` 函数生成 [F-113]。

## 监督者模式（SuperviseAgent）

监督者模式不是一个独立的 Agent 类，而是通过 `SuperviseAgent` 模块（`veadk/agents/supervise_agent.py`）和两个自定义 Flow 类实现的机制 [F-049]。

### Advice 数据模型

```python
class Advice(Pydantic BaseModel):
    advice: str
    reason: str
```

监督者输出 JSON 格式的建议，包含 `advice`（建议内容）和 `reason`（理由）两个字段 [F-049]。

### build_supervisor 函数

`build_supervisor(supervised_agent: Agent) -> Agent` 构建一个名为 `"supervisor"` 的 Agent [F-049]：

- 使用 `response_format=Advice` 强制 LLM 输出结构化的 Advice JSON
- `instruction` 是一个 Jinja2 `Template`，指导监督者根据当前 LLM 请求历史输出建议
- 监督者 Agent 与被监督 Agent 共享模型配置

### generate_advice 函数

`async def generate_advice(agent: Agent, llm_request: LlmRequest) -> str` [F-049]：

1. 创建临时 Runner 运行监督者 Agent
2. 将 LLM 请求历史序列化为文本
3. 运行监督者获取 Advice JSON
4. 返回建议文本

### SupervisorAutoFlow

`SupervisorAutoFlow` 定义于 `veadk/flows/supervise_auto_flow.py`，继承自 `SupervisorSingleFlow` [F-050]：

- 构造函数接收 `supervised_agent: Agent`
- 重写 `_call_llm_async` 方法：先调用 `generate_advice` 获取监督建议，将建议作为 `user` 角色的 Content 追加到 `llm_request.contents`，再委托父类方法执行实际 LLM 调用
- 这使得每次 LLM 调用前，监督者的建议都会被注入到请求上下文中

### SupervisorSingleFlow

`SupervisorSingleFlow` 定义于 `veadk/flows/supervise_single_flow.py`，是无子代理场景下的监督者 Flow 基类，与 `SingleFlow` 对应。

### 启用方式

在 Agent 构造时设置 `enable_supervisor=True` [F-019]。此时 `_llm_flow` 属性返回 `SupervisorAutoFlow` 或 `SupervisorSingleFlow`，而非普通的 `AutoFlow`/`SingleFlow` [F-038]。

## 与 AgentBuilder 的协作

在 YAML 配置中，通过 `type` 字段选择 Agent 类型 [F-042]：

```yaml
root_agent:
  type: Agent
  name: "coordinator"
  sub_agents:
    - type: ParallelAgent
      name: "researchers"
      sub_agents:
        - type: Agent
          name: "web_researcher"
        - type: Agent
          name: "doc_researcher"
    - type: SequentialAgent
      name: "writer_pipeline"
      sub_agents:
        - type: Agent
          name: "drafter"
        - type: Agent
          name: "editor"
```

AgentBuilder 的 `_build` 方法递归处理嵌套结构，根据 `type` 字段实例化对应的类 [F-043]。

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [AgentBuilder 与 YAML 配置驱动](/concepts/02-agent-builder.md)
- [Runner 运行器](/concepts/05-runner.md)
- [高级特性](/concepts/11-advanced.md)
