---
id: veadk-python-memory
title: 03 & 09 - 记忆示例（短期+长期）
source:
- d:\AI\.chaos\libs\veadk-python\examples\03_short_term_memory\main.py
- d:\AI\.chaos\libs\veadk-python\examples\09_long_term_memory\main.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# 记忆示例：短期记忆与长期记忆

## 1. 示例功能介绍

VeADK 提供两种记忆机制：
- **短期记忆（Short-term Memory）**：同一会话内的对话上下文，通过 `session_id` 维护
- **长期记忆（Long-term Memory）**：跨会话持久化存储的事实信息，Agent 可通过 `load_memory` 工具检索

本示例整合了 03_short_term_memory 和 09_long_term_memory 两个示例，演示两种记忆的使用方式与区别。

**演示的核心能力**：
- 短期记忆配置（内存/SQLite 后端）
- 通过 `session_id` 实现多轮对话
- 长期记忆初始化与自动保存
- `load_memory` 工具进行跨会话记忆检索
- 记忆如何影响 Agent 对话能力

---

## 2. 核心代码展示

### 2.1 短期记忆示例

代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/03_short_term_memory/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/03_short_term_memory/main.py)：

```python
import asyncio

from veadk import Agent, Runner
from veadk.memory.short_term_memory import ShortTermMemory

APP_NAME = "memory_demo"
SESSION_ID = "user-42-chat"


async def main() -> None:
    short_term_memory = ShortTermMemory(
        backend="sqlite",
        local_database_path="./short_term_memory.db",
    )

    agent = Agent(
        name="memory_agent",
        instruction="You are a concise assistant. Remember what the user tells you.",
        short_term_memory=short_term_memory,
    )

    runner = Runner(
        agent=agent,
        short_term_memory=short_term_memory,
        app_name=APP_NAME,
    )

    print(
        "Turn 1 ->",
        await runner.run(
            messages="我叫小明，最喜欢的颜色是蓝色。",
            session_id=SESSION_ID,
        ),
    )

    print(
        "Turn 2 ->",
        await runner.run(
            messages="我叫什么名字？我喜欢什么颜色？",
            session_id=SESSION_ID,
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
```

### 2.2 长期记忆示例

代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/09_long_term_memory/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/09_long_term_memory/main.py)：

```python
import asyncio

from veadk import Agent, Runner
from veadk.memory.long_term_memory import LongTermMemory

APP_NAME = "ltm_demo"
USER_ID = "user-42"


def build_runner() -> Runner:
    long_term_memory = LongTermMemory(backend="local", app_name=APP_NAME)
    agent = Agent(
        name="ltm_agent",
        instruction=(
            "You are a personal assistant. When the user asks about something "
            "they told you before, use the `load_memory` tool to recall it."
        ),
        long_term_memory=long_term_memory,
        auto_save_session=True,
    )
    return Runner(agent=agent, app_name=APP_NAME, user_id=USER_ID)


async def main() -> None:
    runner = build_runner()

    print(
        "Session 1 ->",
        await runner.run(
            messages="记一下：我对花生过敏，而且我是素食者。",
            session_id="session-1",
        ),
    )

    print(
        "Session 2 ->",
        await runner.run(
            messages="帮我推荐一道适合我的菜，要考虑我的饮食限制。",
            session_id="session-2",
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. 关键代码行逐行解释

### 3.1 短期记忆关键代码

| 行号 | 代码 | 解释 |
|------|------|------|
| 26 | `from veadk.memory.short_term_memory import ShortTermMemory` | 导入短期记忆类 |
| 35-38 | `short_term_memory = ShortTermMemory(...)` | 创建短期记忆实例：<br>- `backend="sqlite"`：使用 SQLite 持久化到本地文件，进程重启后记忆不丢失<br>- `backend="local"`：纯内存模式，进程退出后记忆消失<br>- `local_database_path`：SQLite 数据库文件路径 |
| 43 | `short_term_memory=short_term_memory,` | 将短期记忆实例绑定到 Agent |
| 48 | `short_term_memory=short_term_memory,` | Runner 也需要绑定同一个短期记忆实例 |
| 29 | `SESSION_ID = "user-42-chat"` | 会话 ID 是短期记忆的 key：相同 ID 共享上下文，不同 ID 是独立对话 |
| 55-58 / 64-67 | 两轮 `runner.run()` 使用**相同** `session_id` | 第二轮对话中 Agent 能回忆起第一轮提到的姓名和颜色——因为上下文被自动维护 |

### 3.2 长期记忆关键代码

| 行号 | 代码 | 解释 |
|------|------|------|
| 36 | `from veadk.memory.long_term_memory import LongTermMemory` | 导入长期记忆类 |
| 43 | `long_term_memory = LongTermMemory(backend="local", app_name=APP_NAME)` | 创建长期记忆实例：<br>- `backend="local"`：本地向量存储，需要 embedding 模型<br>- `app_name`：用于隔离不同应用的记忆 |
| 50 | `long_term_memory=long_term_memory,` | 绑定长期记忆到 Agent，VeADK 会自动添加 `load_memory` 检索工具 |
| 51 | `auto_save_session=True` | 关键配置：每个会话结束后自动将内容保存到长期记忆 |
| 53 | `user_id=USER_ID` | Runner 需要 `user_id` 来标识用户，实现跨设备/跨会话的用户级记忆 |
| 63-66 | Session 1 告知饮食限制 | `auto_save_session=True` 会在会话结束后自动将这些信息存入长期记忆 |
| 72-75 | Session 2 使用**不同** `session_id` | 这是一个全新会话，短期记忆为空！但 Agent 会自动调用 `load_memory` 工具检索到之前的过敏信息，从而给出合适的推荐 |

### 🔑 短期记忆 vs 长期记忆对比

| 维度 | 短期记忆 | 长期记忆 |
|------|----------|----------|
| 作用范围 | 单个 `session_id` 内 | 跨会话、跨用户（通过 `user_id`） |
| 存储内容 | 完整对话历史 | 提取的关键事实/信息 |
| 后端 | 内存（local）/ SQLite | 本地向量库（local） |
| 实现机制 | 上下文窗口自动携带 | Agent 主动调用 `load_memory` 工具检索 |
| 持久化 | SQLite 可持久化，内存模式不持久 | 默认持久化到磁盘 |
| 适用场景 | 多轮对话上下文 | 用户偏好、历史事实、跨会话记忆 |

---

## 4. 运行前置条件

### 环境要求
- Python 3.10+
- 已安装 veadk-python 包
- **长期记忆需要额外安装扩展依赖**：

```bash
pip install "veadk-python[extensions]"
```

### API Key 配置
需要配置火山引擎方舟（Ark）的 API Key：

```bash
# Windows PowerShell
$env:ARK_API_KEY = "your-api-key-here"

# Linux/Mac
export ARK_API_KEY="your-api-key-here"
```

长期记忆需要 embedding 模型配置，请参考 `.env.example` 配置相关环境变量。

---

## 5. 预期运行效果/输出

### 5.1 短期记忆运行效果

```bash
cd 03_short_term_memory
python main.py
```

**预期输出**（示例）：
```
Turn 1 -> 好的，小明！我记住了，你最喜欢的颜色是蓝色。
Turn 2 -> 你叫小明，你最喜欢的颜色是蓝色。
```

第二轮对话不需要重复信息，Agent 通过短期记忆自动回忆起姓名和颜色。

### 5.2 长期记忆运行效果

```bash
cd 09_long_term_memory
python main.py
```

**预期执行流程**：
1. Session 1：用户告知花生过敏+素食者，会话结束后自动保存到长期记忆
2. Session 2：全新会话（短期记忆为空），Agent 主动调用 `load_memory` 检索到饮食限制
3. Agent 根据检索到的信息推荐合适的菜品

**预期输出**（示例）：
```
Session 1 -> 好的，我记住了：你对花生过敏，并且是素食者。我会在未来推荐菜品时考虑这些限制。
Session 2 -> 根据你的饮食限制（花生过敏、素食者），我推荐：清炒时蔬、麻婆豆腐（素食版）、蔬菜沙拉...这些菜品不含花生且适合素食者。
```

⚠️ **注意**：首次运行长期记忆时，Session 2 可能因为 embedding 模型未就绪而无法检索。重新运行一次即可看到跨会话记忆效果。

---

## 6. 延伸学习

- 上一示例：[自定义工具示例](custom-tools.md)
- 下一步学习：[知识库RAG示例](knowledgebase.md) - 学习如何基于自有文档做检索增强生成
- 相关文档：
  - [记忆模块详解](../modules/memory.md)
  - [知识库模块](../modules/knowledgebase.md)
  - [最佳实践](../faq/best-practices.md)
