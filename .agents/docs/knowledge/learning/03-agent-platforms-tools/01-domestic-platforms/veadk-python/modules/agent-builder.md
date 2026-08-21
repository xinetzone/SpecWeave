---
id: agent-builder-module
title: AgentBuilder 使用指南
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# AgentBuilder 使用指南

## 概述

当前版本**提供** `AgentBuilder` 类，位于 `veadk.agent_builder` 模块。`AgentBuilder` 是一个基于 YAML 配置文件构建 Agent 的工厂类，支持通过声明式配置创建复杂的 Agent 层次结构（包括子 Agent 和工具）。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L38-L93](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L38-L93)

---

## 类签名

```python
class AgentBuilder:
```

`AgentBuilder` 是一个简单的工厂类，无继承关系，用于从 YAML 配置文件构建 Agent 实例。

---

## 支持的 Agent 类型

`AgentBuilder` 内部通过 `AGENT_TYPES` 字典映射支持以下 Agent 类型：

| 类型字符串 | 对应类 | 说明 |
|-----------|--------|------|
| `"Agent"` | `veadk.Agent` | 基础 LLM Agent |
| `"SequentialAgent"` | `veadk.agents.SequentialAgent` | 顺序执行 Agent |
| `"ParallelAgent"` | `veadk.agents.ParallelAgent` | 并行执行 Agent |
| `"LoopAgent"` | `veadk.agents.LoopAgent` | 循环执行 Agent |
| `"RemoteVeAgent"` | `veadk.a2a.RemoteVeAgent` | 远程 A2A Agent |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L29-L35](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L29-L35)

---

## 公开方法

### `__init__`

```python
def __init__(self) -> None
```

无参数构造函数，创建一个 AgentBuilder 实例。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L39-L40](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L39-L40)

---

### `build`

```python
def build(
    self,
    path: str,
    root_agent_identifier: str = "root_agent",
) -> BaseAgent
```

从 YAML 配置文件构建 Agent。

#### 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `path` | `str` | **必填** | YAML 配置文件路径（必须以 `.yaml` 结尾） |
| `root_agent_identifier` | `str` | `"root_agent"` | 配置文件中根 Agent 的键名 |

#### 返回值

`BaseAgent`：构建好的 Agent 实例（可以是 Agent、SequentialAgent、ParallelAgent、LoopAgent 或 RemoteVeAgent）。

#### 执行流程

1. 调用 `_read_config(path)` 读取并解析 YAML 文件
2. 从配置字典中获取 `root_agent_identifier` 对应的根 Agent 配置
3. 调用 `_build(agent_config)` 递归构建 Agent（包括子 Agent）
4. 返回构建好的根 Agent

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L83-L93](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L83-L93)

---

### `_build`（内部方法）

```python
def _build(self, agent_config: dict) -> BaseAgent
```

递归构建单个 Agent（包括其子 Agent 和工具）。

> **注意**：这是内部方法，通常不需要直接调用，请使用 `build()` 方法。

#### 构建逻辑

1. **子 Agent 处理**：如果配置中包含 `sub_agents` 列表，递归构建每个子 Agent
2. **工具处理**：如果配置中包含 `tools` 列表，通过动态导入加载工具函数：
   - 工具格式：`{"name": "module.path.function_name"}`
   - 使用 `importlib.import_module` 导入模块
   - 使用 `getattr` 获取函数对象
3. **Agent 实例化**：根据 `type` 字段从 `AGENT_TYPES` 获取对应的类，传入配置参数、子 Agent 和工具进行实例化

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L42-L68](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L42-L68)

---

### `_read_config`（内部方法）

```python
def _read_config(self, path: str) -> dict
```

读取 YAML 配置文件并转换为字典。

> **注意**：这是内部方法，通常不需要直接调用。

#### 校验规则

- 文件路径必须以 `.yaml` 结尾，否则抛出 `AssertionError`
- 解析后的配置必须是字典类型，否则抛出 `AssertionError`

#### 技术细节

- 使用 `OmegaConf.load()` 加载 YAML 文件
- 使用 `OmegaConf.to_container(resolve=True)` 解析并转换为普通 Python 字典

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L70-L81](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent_builder.py#L70-L81)

---

## YAML 配置格式

### 基础结构

```yaml
root_agent:
  type: Agent
  name: my_agent
  description: My custom agent
  instruction: You are a helpful assistant.
  model_name: doubao-pro-32k
  model_provider: openai
  model_api_base: https://ark.cn-beijing.volces.com/api/v3/
  tools: []
  sub_agents: []
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | `str` | 是 | Agent 类型，必须是 `AGENT_TYPES` 中的键名之一 |
| `name` | `str` | 否 | Agent 名称 |
| `description` | `str` | 否 | Agent 描述 |
| `instruction` | `str` | 否 | Agent 指令 |
| `model_name` | `str \| list[str]` | 否 | 模型名称 |
| `model_provider` | `str` | 否 | 模型提供商 |
| `model_api_base` | `str` | 否 | 模型 API 基础 URL |
| `tools` | `list[dict]` | 否 | 工具列表，每个工具包含 `name` 字段（完整模块路径） |
| `sub_agents` | `list[dict]` | 否 | 子 Agent 配置列表，递归结构 |

其他 Agent 支持的字段（如 `enable_a2ui`、`enable_tunnel`、`knowledgebase` 等）可以在配置中设置，但复杂对象类型（如 KnowledgeBase、Memory 实例等）无法通过 YAML 直接配置，需要通过代码方式构建。

---

## 使用示例

### 示例 1：简单 Agent 配置

**配置文件 `agent.yaml`**：

```yaml
root_agent:
  type: Agent
  name: greeter
  description: A friendly greeter agent
  instruction: You are a friendly assistant. Greet users warmly.
  model_name: doubao-pro-32k
  model_provider: openai
  model_api_base: https://ark.cn-beijing.volces.com/api/v3/
```

**Python 代码**：

```python
import asyncio
from veadk import Runner
from veadk.agent_builder import AgentBuilder

async def main():
    builder = AgentBuilder()
    agent = builder.build(path="./agent.yaml")

    runner = Runner(agent=agent, app_name="greeter-app")
    answer = await runner.run(
        messages="你好！",
        session_id="greeter-session",
    )
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

### 示例 2：带子 Agent 的多 Agent 配置

**配置文件 `multi_agent.yaml`**：

```yaml
root_agent:
  type: Agent
  name: router
  description: Router agent that delegates to sub-agents
  instruction: |
    You are a router agent. Delegate tasks to appropriate sub-agents:
    - For math questions, transfer to math_agent
    - For writing tasks, transfer to writing_agent
  sub_agents:
    - type: Agent
      name: math_agent
      description: Expert in mathematics
      instruction: You are a math expert. Solve math problems step by step.
    - type: Agent
      name: writing_agent
      description: Expert in writing
      instruction: You are a writing expert. Help with writing and text composition.
```

**Python 代码**：

```python
from veadk.agent_builder import AgentBuilder

builder = AgentBuilder()
agent = builder.build(path="./multi_agent.yaml")

print(f"Root agent: {agent.name}")
print(f"Sub-agents: {[sa.name for sa in agent.sub_agents]}")
```

### 示例 3：带工具的 Agent 配置

**注意**：工具必须通过完整模块路径指定。

**配置文件 `tool_agent.yaml`**：

```yaml
root_agent:
  type: Agent
  name: tool_user
  description: Agent that uses custom tools
  instruction: Use the available tools to help users.
  tools:
    - name: veadk.tools.builtin_tools.web_search
    - name: my_module.my_custom_tool
```

**工具模块示例 `my_module.py`**：

```python
from datetime import datetime

def my_custom_tool() -> str:
    """返回当前日期和时间"""
    return f"Current time: {datetime.now().isoformat()}"
```

**Python 代码**：

```python
import asyncio
from veadk import Runner
from veadk.agent_builder import AgentBuilder

async def main():
    builder = AgentBuilder()
    agent = builder.build(path="./tool_agent.yaml")

    runner = Runner(agent=agent, app_name="tool-app")
    answer = await runner.run(
        messages="现在几点了？",
        session_id="tool-session",
    )
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

### 示例 4：自定义根 Agent 标识符

如果配置文件中根 Agent 的键名不是 `root_agent`，可以通过 `root_agent_identifier` 参数指定：

**配置文件 `custom_root.yaml`**：

```yaml
my_main_agent:
  type: Agent
  name: custom_main
  instruction: You are the main agent.
```

**Python 代码**：

```python
from veadk.agent_builder import AgentBuilder

builder = AgentBuilder()
agent = builder.build(
    path="./custom_root.yaml",
    root_agent_identifier="my_main_agent",
)
```

---

## 链式构造替代方案

对于需要更灵活配置（如传入复杂对象、记忆模块、知识库实例等）的场景，推荐直接使用 `Agent` 类构造函数进行链式构造。VeADK 的 `Agent` 类基于 Pydantic，支持关键字参数初始化，可以直接在代码中灵活配置。

### 链式构造示例

```python
import asyncio
from veadk import Agent, Runner
from veadk.memory import ShortTermMemory, LongTermMemory
from veadk.knowledgebase import KnowledgeBase

async def main():
    # 直接构造带复杂配置的 Agent
    agent = (
        Agent(
            name="advanced_agent",
            description="An advanced agent with memory and knowledge",
            instruction="You are a helpful assistant with access to knowledge base and memory.",
        )
        # 注意：Pydantic 模型不支持传统链式调用，所有参数在构造时传入
    )

    # 或者使用多个步骤构造
    stm = ShortTermMemory(backend="sqlite", db_path="./sessions.db")
    ltm = LongTermMemory(backend="local", app_name="advanced-app")

    kb = KnowledgeBase(
        index="my_docs",
        backend="local",
    )

    agent = Agent(
        name="advanced_agent",
        instruction="You are a helpful assistant.",
        short_term_memory=stm,
        long_term_memory=ltm,
        knowledgebase=kb,
        enable_a2ui=True,
        enable_tunnel=False,
    )

    runner = Runner(agent=agent, app_name="advanced-app")
    answer = await runner.run(messages="你好", session_id="session-1")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## AgentBuilder 的局限性

`AgentBuilder` 适用于简单的声明式配置场景，但有以下局限性：

1. **复杂对象无法配置**：无法通过 YAML 配置复杂对象实例（如 `KnowledgeBase`、`ShortTermMemory`、`LongTermMemory`、`BaseTracer`、`RunProcessor` 等），这些需要通过代码方式构建
2. **工具动态导入限制**：工具必须是可通过 `module.path.function` 形式导入的函数，不支持 lambda 或闭包
3. **回调函数无法配置**：`before_agent_callback`、`after_agent_callback` 等回调无法通过 YAML 配置
4. **模型实例无法配置**：无法传入自定义的 `model` 实例（只能使用配置参数创建默认 LiteLlm/ArkLlm）
5. **无链式 API**：不像一些其他框架的 Builder 模式提供流畅的链式调用方法

对于复杂场景，建议直接使用 `Agent` 构造函数在代码中配置。

---

## 适用场景建议

| 场景 | 推荐方式 |
|------|----------|
| 简单 Agent（名称、指令、模型配置） | `AgentBuilder` YAML 配置 |
| 多 Agent 层次结构（子 Agent） | `AgentBuilder` YAML 配置 |
| 需要配置记忆模块/知识库/追踪器 | 直接使用 `Agent` 构造函数 |
| 需要自定义回调/RunProcessor | 直接使用 `Agent` 构造函数 |
| 需要动态创建 Agent（运行时决定配置） | 直接使用 `Agent` 构造函数 |
| 需要复杂工具（非简单导入函数） | 直接使用 `Agent` 构造函数 |
