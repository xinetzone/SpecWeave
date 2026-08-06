---
id: veadk-python-multi-agent
title: 06 - 多智能体协作示例
source: d:\AI\.chaos\libs\veadk-python\examples\06_multi_agent\main.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# 多智能体协作示例 (Multi-Agent)

## 1. 示例功能介绍

本示例展示如何将多个 Agent 组合成工作流（Workflow），而不是让单个 Agent 完成所有任务。通过 `SequentialAgent`（顺序 Agent），我们可以将复杂任务拆分为多个专业化的子 Agent，按固定顺序执行：

```
outliner（大纲师） → writer（写作者） → editor（编辑）
```

子 Agent 之间通过会话状态（session state）共享数据：每个子 Agent 通过 `output_key` 将结果写入状态，下一个 Agent 通过在指令中引用 `{that_key}` 来读取前一个 Agent 的输出。

**演示的核心能力**：
- 定义多个专业化的子 Agent（Single Responsibility）
- 使用 `SequentialAgent` 编排顺序执行流程
- 通过 `output_key` 和 `{key}` 模板在 Agent 间传递状态
- 工作流 Agent 的记忆配置
- 多 Agent 协作的流水线模式

---

## 2. 核心代码展示

完整代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/06_multi_agent/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/06_multi_agent/main.py)：

```python
import asyncio

from veadk import Agent, Runner
from veadk.agents.sequential_agent import SequentialAgent
from veadk.memory.short_term_memory import ShortTermMemory


def build_pipeline() -> SequentialAgent:
    outliner = Agent(
        name="outliner",
        instruction=(
            "You are an outliner. Given the user's topic, produce a tight "
            "3-point outline (just the bullet points, no prose)."
        ),
        output_key="outline",
    )

    writer = Agent(
        name="writer",
        instruction=(
            "You are a writer. Expand the following outline into a short, "
            "engaging paragraph (~120 words):\n\n{outline}"
        ),
        output_key="draft",
    )

    editor = Agent(
        name="editor",
        instruction=(
            "You are an editor. Polish the draft below for clarity and flow, "
            "then return ONLY the final text:\n\n{draft}"
        ),
        output_key="final",
    )

    return SequentialAgent(
        name="content_pipeline",
        description="Turns a topic into a polished short paragraph.",
        sub_agents=[outliner, writer, editor],
    )


async def main() -> None:
    pipeline = build_pipeline()
    runner = Runner(
        agent=pipeline,
        short_term_memory=ShortTermMemory(),
        app_name="multi_agent_demo",
    )

    final_text = await runner.run(
        messages="主题：为什么团队应该写好的提交信息（commit message）。",
        session_id="demo-session",
    )
    print(final_text)


if __name__ == "__main__":
    asyncio.run(main())
```

该示例目录下还有 `parallel.py` 展示并行执行模式，本教程重点讲解顺序模式。

---

## 3. 关键代码行逐行解释

| 行号 | 代码 | 解释 |
|------|------|------|
| 30 | `from veadk.agents.sequential_agent import SequentialAgent` | 导入顺序工作流 Agent，按列表顺序依次执行子 Agent |
| 31 | `from veadk.memory.short_term_memory import ShortTermMemory` | 工作流 Agent（Sequential/Parallel/Loop）本身不携带记忆，需要 Runner 显式提供会话存储 |
| 35-42 | `outliner = Agent(..., output_key="outline",)` | 第一个子 Agent——大纲师：<br>- 职责：根据主题生成3点大纲<br>- `output_key="outline"`：将输出写入会话状态的 `outline` 字段，供后续 Agent 使用 |
| 44-51 | `writer = Agent(..., instruction="...{outline}", output_key="draft",)` | 第二个子 Agent——写作者：<br>- 职责：将大纲扩展为短文<br>- **`{outline}`**：这是模板占位符，运行时会被会话状态中 `outline` 字段的实际内容替换<br>- `output_key="draft"`：输出写入 `draft` 字段 |
| 53-60 | `editor = Agent(..., instruction="...{draft}", output_key="final",)` | 第三个子 Agent——编辑：<br>- 职责：润色草稿，只返回最终文本<br>- 引用前一个 Agent 的输出 `{draft}`<br>- `output_key="final"`：最终结果写入 `final` 字段 |
| 62-66 | `SequentialAgent(name="content_pipeline", ..., sub_agents=[outliner, writer, editor],)` | 将子 Agent 组装成顺序工作流：<br>- `sub_agents` 列表顺序就是执行顺序<br>- 列表中每个 Agent 是独立的专业化 Agent，有自己的指令<br>- SequentialAgent 本身也有 `name` 和 `description`，像普通 Agent 一样使用 |
| 73-77 | `Runner(agent=pipeline, short_term_memory=ShortTermMemory(), ...)` | **重要**：工作流 Agent 不内置记忆，必须显式给 Runner 传入 `short_term_memory`，否则状态无法在子 Agent 间传递 |
| 79-82 | `runner.run(messages="主题：为什么团队应该写好的提交信息...")` | 用户输入直接传给第一个子 Agent（outliner），最终返回最后一个子 Agent（editor）的输出 |

### 🔑 状态传递机制

```
用户输入
   ↓
[outliner] → output_key="outline" → 状态: {outline: "..."}
   ↓
{outline} 被注入 writer 的指令 → [writer] → output_key="draft" → 状态: {outline: "...", draft: "..."}
   ↓
{draft} 被注入 editor 的指令 → [editor] → output_key="final" → 状态: {outline: "...", draft: "...", final: "..."}
   ↓
返回 final 内容给用户
```

**关键点**：
1. `output_key` 定义了当前 Agent 输出存储在状态中的键名
2. 指令中的 `{key_name}` 是模板变量，运行时自动替换为状态中对应键的值
3. 状态在整个工作流执行期间持续累积，后面的 Agent 可以访问前面所有 Agent 的输出
4. Runner 返回最后一个子 Agent 的输出（或者你指定的 `output_key` 对应的值）

### 💡 为什么用多 Agent 而不是单 Agent？

| 单 Agent 模式 | 多 Agent 流水线模式 |
|--------------|-------------------|
| 一个指令承担所有职责（构思+写作+编辑） | 每个 Agent 专注一个职责，指令更清晰 |
| 容易在中间步骤出错（如大纲没列好就直接写） | 流水线强制按步骤执行，前一步完成才进入下一步 |
| 难以单独优化某一步 | 可以独立调整每个子 Agent 的指令/模型/工具 |
| Token 利用率低（一次输出长文） | 每一步输出更短，质量更高，成本可控 |

---

## 4. 运行前置条件

### 环境要求
- Python 3.10+
- 已安装 veadk-python 包

### API Key 配置
需要配置火山引擎方舟（Ark）的 API Key：

```bash
# Windows PowerShell
$env:ARK_API_KEY = "your-api-key-here"

# Linux/Mac
export ARK_API_KEY="your-api-key-here"
```

### 依赖安装
```bash
pip install veadk-python
```

---

## 5. 预期运行效果/输出

运行命令：
```bash
cd 06_multi_agent
python main.py
```

**预期执行流程**：
1. outliner 接收主题，生成3点大纲（如：可读性、历史追溯、协作效率）
2. writer 接收大纲，将其扩展为约120字的段落
3. editor 接收草稿，润色优化后返回最终文本

**预期输出**（示例）：
```
写好提交信息是团队协作的基石。首先，清晰的提交信息让代码审查更高效——评审者无需阅读完整diff就能理解变更意图。其次，当需要追溯bug来源或回滚变更时，规范的提交历史就像一份详尽的变更日志，能快速定位问题引入点。最后，在多人协作的项目中，统一风格的提交信息降低了沟通成本，新成员也能通过提交历史快速理解项目演进脉络。投入几十秒写好提交信息，未来能为团队节省数小时的困惑时间。
```

你会看到输出是一段经过"大纲→写作→编辑"三阶段处理的流畅文字，质量通常优于单次直接生成。

---

## 6. 延伸学习

- 上一示例：[知识库RAG示例](knowledgebase.md)
- 下一步学习：[结构化输出示例](structured-output.md) - 学习如何让 Agent 返回可解析的结构化数据
- 相关文档：
  - [A2A 多智能体模块](../modules/a2a.md)
  - [Agent 模块](../modules/agent.md)
  - [设计模式](../architecture/design-patterns.md)
  - [最佳实践](../faq/best-practices.md)
