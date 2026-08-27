---
type: Example
title: 快速开始
description: 基于 examples/01_quickstart/main.py 的最小可运行示例，演示 Agent 与 Runner 的基本用法
tags: [veadk, quickstart, example, agent, runner, getting-started]
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

# 快速开始

本文档基于 veadk-python 源码仓库中的 `examples/01_quickstart/main.py` [F-125]，演示最小可运行的 VeADK 程序。一个 `Agent` 持有模型和指令，一个 `Runner` 驱动与 Agent 的对话，`runner.run(...)` 是异步方法并返回最终文本答案。

## 前置条件

1. Python `>=3.10` [F-003]
2. 已安装 veadk-python：`pip install veadk-python`
3. 配置火山引擎方舟（Ark）API Key：

```bash
export MODEL_AGENT_API_KEY="your-ark-api-key"
```

API Key 的解析遵循四级优先级：显式参数 > `MODEL_AGENT_API_KEY` 环境变量 > Key 名称解析 > 配置默认值。详见 [配置系统](/concepts/04-configuration.md)。

## 完整代码

```python
"""The smallest possible VeADK program: one agent, one question, one answer.

An `Agent` holds the model + instruction; a `Runner` drives a conversation
with it. `runner.run(...)` is async and returns the final text answer.
"""

import asyncio

from veadk import Agent, Runner


async def main() -> None:
    agent = Agent(
        name="quickstart_agent",
        description="A friendly assistant that answers in one short paragraph.",
        instruction="You are a helpful assistant. Answer concisely in the user's language.",
    )

    runner = Runner(agent=agent, app_name="quickstart")

    answer = await runner.run(
        messages="用一句话介绍火山引擎（Volcengine）。",
        session_id="demo-session",
    )
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
```

来源：`examples/01_quickstart/main.py:21-43` [F-125]

## 代码逐行解析

### 1. 导入

```python
from veadk import Agent, Runner
```

`veadk` 包通过 `__getattr__` 实现懒加载 [F-011]：访问 `veadk.Agent` 时从 `veadk.agent` 导入，访问 `veadk.Runner` 时从 `veadk.runner` 导入。这避免了 `import veadk` 时加载所有重型依赖。

### 2. 创建 Agent

```python
agent = Agent(
    name="quickstart_agent",
    description="A friendly assistant that answers in one short paragraph.",
    instruction="You are a helpful assistant. Answer concisely in the user's language.",
)
```

- `name`：Agent 名称，默认值为 `"veAgent"`，此处自定义为 `"quickstart_agent"` [F-015]
- `description`：Agent 描述，在 A2A 场景中用于能力声明 [F-113]
- `instruction`：系统指令，指导 Agent 的行为。默认值为 `DEFAULT_INSTRUCTION` [F-111]

未指定 `model_name` 时，Agent 使用全局配置的默认模型 `doubao-seed-2-1-pro-260628` [F-054][F-061]。未指定 `enable_responses=True` 时，Agent 使用 LiteLLM 路径实例化模型 [F-025]。

Agent 构造时，`model_post_init` 自动完成模型实例化、默认请求头设置等初始化工作 [F-023]。

### 3. 创建 Runner

```python
runner = Runner(agent=agent, app_name="quickstart")
```

- `agent`：要运行的 Agent 实例 [F-067]
- `app_name`：应用名，用于会话和记忆的命名空间隔离

Runner 在初始化时 [F-068]：
- 确定 run_processor（此处无，使用 NoOpRunProcessor）
- 无显式 short_term_memory 时从 agent 获取；agent 也无则创建内存版 ShortTermMemory
- 通过 `MethodType` 将消息拦截装饰器绑定到 `run_async`

### 4. 运行对话

```python
answer = await runner.run(
    messages="用一句话介绍火山引擎（Volcengine）。",
    session_id="demo-session",
)
```

- `messages`：输入消息，此处为纯文本字符串。`RunnerMessage` 类型还支持 `list[str]`、`MediaMessage` 等多模态格式 [F-066]
- `session_id`：会话 ID，用于标识和恢复对话。未指定时自动生成 `tmp-session-<timestamp>` [F-069]

`run()` 方法的执行流程 [F-070]：
1. 创建默认 `RunConfig(max_llm_calls=100)`
2. 通过 `_convert_messages` 将文本转为 ADK Content
3. 通过短期记忆创建或获取会话
4. 遍历 Agent 事件流，提取最后一条非 thought 文本
5. 返回最终文本字符串

### 5. 启动事件循环

```python
if __name__ == "__main__":
    asyncio.run(main())
```

`runner.run()` 是异步方法，需要在 asyncio 事件循环中运行。

## 运行

```bash
python main.py
```

预期输出（具体内容取决于模型响应）：

```text
火山引擎是字节跳动旗下的云服务平台，提供大模型、云计算、数据分析等 AI 与云基础设施服务。
```

## 下一步

- 添加自定义工具：参考 [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md) 中的工具挂载机制
- 使用多 Agent 协作：参考 [Agent 类型体系](/concepts/03-agent-types.md)
- 添加知识库：参考 [知识库](/concepts/08-knowledgebase.md)
- 配置记忆：参考 [记忆系统](/concepts/06-memory-system.md)
- 使用 CLI 创建项目：运行 `veadk create` 自动生成项目脚手架 [F-077]

## 相关概念

- [veadk-python 概览](/concepts/00-overview.md)
- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [Runner 运行器](/concepts/05-runner.md)
- [配置系统](/concepts/04-configuration.md)
