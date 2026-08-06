---
id: veadk-python-quickstart
title: 01 - 最小Agent示例
source: d:\AI\.chaos\libs\veadk-python\examples\01_quickstart\main.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# 最小Agent示例 (Quickstart)

## 1. 示例功能介绍

本示例展示了 VeADK 最基础的使用方式：创建一个简单的 Agent 实例，通过 Runner 驱动对话，完成一次提问并获取回答。这是学习 VeADK 的第一个示例，仅需约 15 行核心代码即可运行一个完整的智能体。

**演示的核心能力**：
- Agent 的基本定义（名称、描述、指令）
- Runner 的初始化与运行
- 异步对话调用
- 会话 ID 的使用

---

## 2. 核心代码展示

完整代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/01_quickstart/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/01_quickstart/main.py)：

```python
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

---

## 3. 关键代码行逐行解释

| 行号 | 代码 | 解释 |
|------|------|------|
| 23 | `from veadk import Agent, Runner` | 导入 VeADK 最核心的两个类：`Agent` 负责封装模型和指令，`Runner` 负责驱动对话执行 |
| 27-31 | `agent = Agent(...)` | 创建 Agent 实例：<br>- `name`：Agent 的唯一标识符，用于日志和追踪<br>- `description`：对 Agent 能力的简短描述，帮助系统理解其用途<br>- `instruction`：系统提示词（System Prompt），定义 Agent 的行为准则 |
| 33 | `runner = Runner(agent=agent, app_name="quickstart")` | 创建 Runner 实例：<br>- `agent`：绑定要运行的 Agent<br>- `app_name`：应用名称，用于日志分组和追踪命名空间 |
| 35-38 | `answer = await runner.run(...)` | 异步执行对话：<br>- `messages`：用户输入的消息<br>- `session_id`：会话标识符，相同 ID 可在多轮对话中保持上下文记忆 |
| 39 | `print(answer)` | 打印 Agent 返回的最终文本回答 |
| 43 | `asyncio.run(main())` | 启动异步事件循环运行 main 函数 |

---

## 4. 运行前置条件

### 环境要求
- Python 3.10+
- 已安装 veadk-python 包

### API Key 配置
需要配置火山引擎方舟（Ark）的 API Key，可通过以下两种方式之一：

1. **环境变量方式**（推荐）：
   ```bash
   # Windows PowerShell
   $env:ARK_API_KEY = "your-api-key-here"
   
   # Linux/Mac
   export ARK_API_KEY="your-api-key-here"
   ```

2. **.env 文件方式**：
   复制 `.env.example` 为 `.env` 并填入 API Key：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置 ARK_API_KEY=your-api-key
   ```

### 依赖安装
```bash
pip install veadk-python
```

---

## 5. 预期运行效果/输出

运行命令：
```bash
python main.py
```

**预期输出**（示例）：
```
火山引擎（Volcengine）是字节跳动推出的企业级云服务平台，提供计算、存储、AI大模型、数据分析等一站式云服务解决方案，助力企业数字化转型。
```

Agent 会用一句简洁的中文回答关于火山引擎的问题。

---

## 6. 延伸学习

- 下一步学习：[自定义工具示例](custom-tools.md) - 学习如何为 Agent 添加自定义工具
- 相关文档：
  - [Agent 模块详解](../modules/agent.md)
  - [Runner 模块详解](../modules/runner.md)
  - [快速入门指南](../getting-started/quickstart.md)
