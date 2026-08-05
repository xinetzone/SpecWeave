---
id: veadk-python-quickstart
title: 快速入门：Hello World
source: 'seven-concepts: veadk-python-wiki'
category: learning
tags:
- VeADK
- 火山引擎
- AI Agent
- 快速入门
- Hello World
- 教程
date: '2026-08-05'
status: stable
author: seven-concepts knowledge-scenario
summary: VeADK-Python 快速入门教程，5分钟创建你的第一个AI Agent，包含完整可运行代码和逐行解释
wiki_version: '1.0'
---


# 快速入门：Hello World

本文档将引导你在 5 分钟内创建你的第一个 VeADK Agent，并完成一次完整的对话。

---

## 前置条件

在开始之前，请确保你已经完成以下准备：

1. **Python 环境**：Python 3.10 或更高版本已安装
   - 检查版本：`python --version`
   - 如未安装，请参考 [安装指南](installation.md)

2. **VeADK 已安装**：已通过 pip 或 uv 安装 veadk-python
   - 验证安装：`pip show veadk-python`

3. **API Key 已获取**：已从火山引擎方舟平台获取 API Key
   - 如未获取，请参考 [配置指南](configuration.md#api-key-获取方式)

4. **API Key 已配置**：通过环境变量或 config.yaml 配置 API Key
   - 最简单的方式是在项目根目录创建 `.env` 文件：
     ```env
     MODEL_AGENT_API_KEY=your-ark-api-key-here
     ```

---

## Hello World 完整代码

创建一个名为 `hello_world.py` 的文件，将以下代码复制进去：

```python
"""
VeADK 快速入门：Hello World
这是一个最小化的 VeADK 程序：创建一个 Agent，发送一条消息，获取回复。
"""

import asyncio

from veadk import Agent, Runner


async def main() -> None:
    # 第一步：创建 Agent 实例
    agent = Agent(
        name="hello_world_agent",
        description="一个友好的AI助手，用简洁的中文回答问题。",
        instruction="你是一个有帮助的AI助手。请用简洁、友好的中文回答用户的问题。",
    )

    # 第二步：创建 Runner 运行器
    runner = Runner(agent=agent, app_name="hello_world")

    # 第三步：执行对话
    answer = await runner.run(
        messages="你好！请用一句话介绍一下你自己。",
        session_id="hello-world-demo",
    )

    # 第四步：输出结果
    print("=" * 50)
    print("Agent 回复：")
    print(answer)
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
```

完整示例代码来自 [file:///d:/AI/.chaos/libs/veadk-python/examples/01_quickstart/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/01_quickstart/main.py)。

---

## 运行程序

在终端中执行：

```bash
python hello_world.py
```

---

## 代码逐行解释

让我们逐行理解这段代码的含义。

### 导入模块

```python
import asyncio
```
- 导入 Python 标准库 `asyncio`，用于运行异步代码
- VeADK 的核心 API 都是异步的，需要在 asyncio 事件循环中运行

```python
from veadk import Agent, Runner
```
- 从 `veadk` 包导入两个核心类：
  - `Agent`：智能体类，定义 Agent 的身份、指令、模型、工具等（定义在 [file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L72-L751](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L72-L751)）
  - `Runner`：运行器类，负责驱动 Agent 执行对话、管理会话（定义在 [file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L329-L789](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L329-L789)）

### 定义 main 异步函数

```python
async def main() -> None:
```
- 定义一个异步主函数 `main`
- `async def` 表示这是一个异步函数，可以使用 `await` 关键字
- `-> None` 表示函数没有返回值

### 创建 Agent 实例

```python
agent = Agent(
    name="hello_world_agent",
    description="一个友好的AI助手，用简洁的中文回答问题。",
    instruction="你是一个有帮助的AI助手。请用简洁、友好的中文回答用户的问题。",
)
```

`Agent` 类的关键参数：

| 参数 | 说明 | 是否必填 | 默认值 |
|------|------|----------|--------|
| `name` | Agent 的名称，用于标识和日志 | 否 | `"veAgent"` |
| `description` | Agent 的描述，在 A2A 多智能体场景中用于能力描述 | 否 | 默认描述 |
| `instruction` | Agent 的系统指令，定义 Agent 的角色和行为规范 | 否 | 默认指令 |

> **提示**：`Agent` 类继承自 Google ADK 的 `LlmAgent`，支持更多参数如 `model_name`、`tools`、`knowledgebase` 等，我们将在后续章节介绍。

`Agent` 类完整属性列表参见 [supporting-analysis/02-agent-class-signatures.md](../supporting-analysis/02-agent-class-signatures.md)。

### 创建 Runner 运行器

```python
runner = Runner(agent=agent, app_name="hello_world")
```

`Runner` 构造函数参数：

| 参数 | 说明 | 是否必填 | 默认值 |
|------|------|----------|--------|
| `agent` | 要运行的 Agent 实例 | 是 | - |
| `app_name` | 应用名称，用于会话管理和日志标识 | 否 | `"veadk_default_app"` |
| `user_id` | 默认用户 ID | 否 | `"veadk_default_user"` |
| `short_term_memory` | 短期记忆实例 | 否 | 自动创建内存版 |

`Runner` 负责：
- 管理会话状态（session）
- 消息格式转换
- 调用 Agent 执行推理
- 处理事件流并返回最终文本结果

### 执行对话

```python
answer = await runner.run(
    messages="你好！请用一句话介绍一下你自己。",
    session_id="hello-world-demo",
)
```

- `await`：等待异步操作完成
- `runner.run()` 是执行对话的核心方法（定义在 [file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L468-L576](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L468-L576)）

`runner.run()` 方法参数：

| 参数 | 说明 | 是否必填 | 默认值 |
|------|------|----------|--------|
| `messages` | 用户消息，可以是字符串、多模态消息或消息列表 | 是 | - |
| `session_id` | 会话 ID，相同 ID 的对话会共享上下文 | 否 | 自动生成临时 ID |
| `user_id` | 用户 ID，覆盖默认值 | 否 | Runner 构造时的 user_id |
| `run_config` | 运行配置（如最大 LLM 调用次数） | 否 | 默认配置 |

返回值：`str` 类型，即 Agent 的最终文本回复。

> **注意**：README 中展示的极简写法 `agent.run("hello!")` 已在新版本中标记为废弃（[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L748-L751](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L748-L751)），请使用 `Runner.run()` 方式。

### 输出结果

```python
print("=" * 50)
print("Agent 回复：")
print(answer)
print("=" * 50)
```
- 格式化输出 Agent 的回复，便于阅读

### 程序入口

```python
if __name__ == "__main__":
    asyncio.run(main())
```
- Python 标准入口判断：当直接运行此文件时执行以下代码
- `asyncio.run(main())`：启动 asyncio 事件循环，运行异步主函数 `main()`

---

## 预期输出

运行成功后，你将看到类似如下输出（具体回复内容可能因模型版本略有差异）：

```
==================================================
Agent 回复：
你好！我是由火山引擎开发的AI助手，基于豆包大模型，能够帮助你回答问题、进行对话和完成各种任务。
==================================================
```

如果看到类似输出，说明你的第一个 VeADK Agent 已经成功运行！

---

## 常见运行问题

### 问题 1：提示 "The environment variable `MODEL_AGENT_API_KEY` not exists"

**原因**：没有配置 API Key。

**解决方案**：
1. 在项目根目录创建 `.env` 文件，添加：
   ```env
   MODEL_AGENT_API_KEY=your-ark-api-key-here
   ```
2. 或在代码中直接传入：
   ```python
   agent = Agent(
       model_api_key="your-ark-api-key-here",
       # ... 其他参数
   )
   ```

### 问题 2：网络连接超时

**原因**：无法连接到火山引擎 API 端点。

**解决方案**：
- 检查网络连接
- 如果在公司网络环境，确认代理设置
- 确认 `model_api_base` 配置正确（默认为 `https://ark.cn-beijing.volces.com/api/v3/`）

### 问题 3：模型不存在或无权限

**原因**：API Key 对应的账号没有权限访问指定模型，或模型名称错误。

**解决方案**：
1. 登录方舟控制台确认 API Key 有效
2. 确认已创建对应模型的推理接入点
3. 检查模型名称是否正确（默认为 `doubao-seed-2-1-pro-260628`）

### 问题 4：ImportError: cannot import name 'Agent' from 'veadk'

**原因**：VeADK 未正确安装，或安装在不同的 Python 环境中。

**解决方案**：
1. 确认虚拟环境已激活
2. 重新安装：`pip install --force-reinstall veadk-python`
3. 检查 Python 路径：`which python`（macOS/Linux）或 `where python`（Windows）

---

## 代码变化：README 极简写法 vs 推荐写法

README 中展示了一个极简示例（[file:///d:/AI/.chaos/libs/veadk-python/README.md#L73-L81](file:///d:/AI/.chaos/libs/veadk-python/README.md#L73-L81)）：

```python
# README 中的极简写法（已废弃 agent.run 方式）
from veadk import Agent
import asyncio

agent = Agent()
res = asyncio.run(agent.run("hello!"))
print(res)
```

但请注意：`Agent.run()` 方法在 google-adk >= 2.0.0 中已被标记为废弃（[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L743-L751](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L743-L751)），推荐使用 `Runner` 方式：

```python
# 推荐写法（使用 Runner）
from veadk import Agent, Runner
import asyncio

async def main():
    agent = Agent()
    runner = Runner(agent=agent)
    res = await runner.run(messages="hello!")
    print(res)

asyncio.run(main())
```

使用 Runner 的优势：
- 支持会话管理（通过 session_id 维护多轮对话上下文）
- 支持短期/长期记忆集成
- 支持多模态消息输入
- 支持链路追踪数据保存
- 符合未来版本 API 演进方向

---

## 下一步建议

恭喜你运行了第一个 VeADK Agent！接下来你可以：

### 1. 尝试多轮对话

修改代码，体验多轮对话的上下文记忆：

```python
async def main():
    agent = Agent(
        name="chat_agent",
        instruction="你是一个友好的助手，记住用户告诉你的信息。",
    )
    runner = Runner(agent=agent, app_name="chat_demo")

    session_id = "chat-session-001"

    # 第一轮
    answer1 = await runner.run(
        messages="我叫小明，我喜欢打篮球。",
        session_id=session_id,
    )
    print("第一轮：", answer1)

    # 第二轮 - Agent 应该记得"我叫小明"
    answer2 = await runner.run(
        messages="你还记得我叫什么名字吗？我喜欢什么运动？",
        session_id=session_id,
    )
    print("第二轮：", answer2)
```

### 2. 查看更多官方示例

浏览 [examples/](file:///d:/AI/.chaos/libs/veadk-python/examples/) 目录，了解更多功能：

| 示例目录 | 内容 |
|----------|------|
| [01_quickstart/](file:///d:/AI/.chaos/libs/veadk-python/examples/01_quickstart/) | 快速入门（当前示例） |
| [02_custom_tools/](file:///d:/AI/.chaos/libs/veadk-python/examples/02_custom_tools/) | 自定义工具 |
| [03_short_term_memory/](file:///d:/AI/.chaos/libs/veadk-python/examples/03_short_term_memory/) | 短期记忆 |
| [04_web_search/](file:///d:/AI/.chaos/libs/veadk-python/examples/04_web_search/) | 网页搜索 |
| [05_knowledgebase_rag/](file:///d:/AI/.chaos/libs/veadk-python/examples/05_knowledgebase_rag/) | 知识库 RAG |
| [06_multi_agent/](file:///d:/AI/.chaos/libs/veadk-python/examples/06_multi_agent/) | 多智能体协作 |
| [07_structured_output/](file:///d:/AI/.chaos/libs/veadk-python/examples/07_structured_output/) | 结构化输出 |
| [08_model_config/](file:///d:/AI/.chaos/libs/veadk-python/examples/08_model_config/) | 模型配置 |
| [09_long_term_memory/](file:///d:/AI/.chaos/libs/veadk-python/examples/09_long_term_memory/) | 长期记忆 |
| [11_tracing/](file:///d:/AI/.chaos/libs/veadk-python/examples/11_tracing/) | 链路追踪 |

### 3. 阅读核心概念文档

- [Agent 类详解](../modules/agent.md) - 了解 Agent 的所有参数和能力
- [Runner 运行器](../modules/runner.md) - 深入理解 Runner 的会话管理和事件流
- [配置指南](configuration.md) - 学习更多配置选项
- [AgentKit 应用工厂](agentkit-app.md) - 学习如何将 Agent 部署为 Web 服务

---

> **版本说明**：本文档基于 VeADK-Python 代码库分析生成，对应 Wiki 版本 1.0。如发现文档内容与实际代码不符，请参考源代码为准。
