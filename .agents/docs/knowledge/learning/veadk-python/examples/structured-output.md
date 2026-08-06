---
id: veadk-python-structured-output
title: 07 - 结构化输出示例
source: d:\AI\.chaos\libs\veadk-python\examples\07_structured_output\main.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# 结构化输出示例 (Structured Output)

## 1. 示例功能介绍

本示例展示如何强制 Agent 返回符合预定义 Schema 的结构化 JSON 数据，而不是自由文本。通过传入 Pydantic 模型作为 `output_schema`，Agent 的回复保证匹配该 Schema——非常适合信息提取、分类、数据结构化等场景，让你可以直接 `json.loads()` 或用 Pydantic 验证结果，无需解析自由文本。

**演示的核心能力**：
- 使用 Pydantic BaseModel 定义输出结构
- 通过 `output_schema` 参数强制结构化输出
- 字段描述（Field description）指导模型填充
- 用 `model_validate_json()` 验证和解析结果
- 结构化输出的限制（无工具调用、无子 Agent 分发）

---

## 2. 核心代码展示

完整代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/07_structured_output/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/07_structured_output/main.py)：

```python
import asyncio
import json

from pydantic import BaseModel, Field

from veadk import Agent, Runner


class Ticket(BaseModel):
    """A structured support ticket extracted from a user's message."""

    summary: str = Field(description="One-line summary of the issue.")
    category: str = Field(description="One of: billing, bug, feature_request, other.")
    priority: str = Field(description="One of: low, medium, high.")
    sentiment: str = Field(description="One of: positive, neutral, negative.")


async def main() -> None:
    agent = Agent(
        name="ticket_extractor",
        description="Turns a free-text complaint into a structured ticket.",
        instruction="Extract a support ticket from the user's message.",
        output_schema=Ticket,
    )

    runner = Runner(agent=agent, app_name="structured_output")

    raw = await runner.run(
        messages=(
            "你们的 App 又崩溃了！我每次点开账单页面就闪退，已经第三次了，"
            "非常影响我交月费，请尽快处理！"
        ),
        session_id="demo-session",
    )

    ticket = Ticket.model_validate_json(raw)
    print(json.dumps(ticket.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. 关键代码行逐行解释

| 行号 | 代码 | 解释 |
|------|------|------|
| 28 | `from pydantic import BaseModel, Field` | 导入 Pydantic 的核心类。VeADK 原生支持 Pydantic v2 模型作为输出 Schema |
| 33-39 | `class Ticket(BaseModel): ...` | 定义工单数据结构：<br>- 继承 `BaseModel` 获得 Pydantic 的所有验证能力<br>- 每个字段使用 `Field(description="...")` 提供描述——**这些描述会传给模型，指导它如何填充每个字段**<br>- 枚举值在描述中明确说明（如 "One of: billing, bug..."），帮助模型选择正确值 |
| 34 | `"""A structured support ticket..."""` | 模型的文档字符串（docstring）也会作为整体描述传给 LLM，帮助它理解这个 Schema 的用途 |
| 43-48 | `agent = Agent(..., output_schema=Ticket,)` | **关键配置**：将 Pydantic 模型传入 `output_schema` 参数。这会：<br>1. 自动配置 LLM 以 JSON 模式输出<br>2. 将 Schema 转换为模型能理解的格式（JSON Schema）<br>3. 在系统提示中注入输出格式要求<br>4. 对输出进行验证和重试（如果不符合 Schema） |
| 52-58 | `raw = await runner.run(messages=...)` | 运行 Agent，返回值 `raw` 是一个**保证符合 Ticket Schema 的 JSON 字符串**。注意：此时不是自然语言，而是结构化 JSON |
| 61 | `ticket = Ticket.model_validate_json(raw)` | 使用 Pydantic 解析 JSON 字符串为强类型的 Ticket 对象。如果 Schema 定义正确，这一步不会失败 |
| 62 | `print(json.dumps(ticket.model_dump(), ensure_ascii=False, indent=2))` | 将 Pydantic 对象转回字典并美化输出，`ensure_ascii=False` 保证中文正常显示 |

### 🔑 结构化输出的重要约束

当设置 `output_schema` 时：

1. ❌ **不能调用工具**：Agent 无法使用 tools 功能，因为输出被强制为固定 JSON 结构
2. ❌ **不能转移到子 Agent**：不能作为分发器路由到其他 Agent
3. ✅ **只返回结构化数据**：模型输出的是纯 JSON，不会有其他自然语言解释
4. ✅ **自动验证重试**：如果模型第一次输出不符合 Schema，VeADK 会自动重试（带错误信息反馈）

### 💡 如何写好 Field description？

字段描述是给模型看的，不是给人看的，因此要：

1. **明确枚举值**：像 `"One of: billing, bug, feature_request, other."` 这样列出可选值
2. **说明格式要求**：如 `"Date in YYYY-MM-DD format"`
3. **给出示例**：如 `"e.g. 'User cannot login after password reset'"`
4. **简洁清晰**：每个描述一句话说清楚该字段填什么

**反例**（不好的描述）：
```python
summary: str = Field(description="Summary")  # 太模糊，模型不知道怎么填
priority: str = Field(description="Priority level")  # 没有说明可选值
```

**正例**（好的描述）：
```python
summary: str = Field(description="One-line summary of the issue, e.g. 'App crashes on billing page'")
priority: str = Field(description="Urgency level: low (cosmetic), medium (impaired), high (blocker/outage)")
```

---

## 4. 运行前置条件

### 环境要求
- Python 3.10+
- 已安装 veadk-python 包
- Pydantic（veadk-python 已作为依赖包含，通常无需单独安装）

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
pip install veadk-python pydantic
```

---

## 5. 预期运行效果/输出

运行命令：
```bash
cd 07_structured_output
python main.py
```

**预期执行流程**：
1. Agent 收到用户的投诉消息
2. LLM 根据 Ticket Schema 提取结构化字段
3. VeADK 验证输出符合 Schema
4. Pydantic 解析为 Ticket 对象
5. 格式化输出 JSON

**预期输出**：
```json
{
  "summary": "App闪退问题：点击账单页面即崩溃",
  "category": "bug",
  "priority": "high",
  "sentiment": "negative"
}
```

你可以直接在代码中使用 `ticket.summary`、`ticket.priority` 等属性做后续处理（如存入数据库、分配给处理人员、触发告警等），无需任何 NLP 解析。

---

## 6. 延伸学习

- 上一示例：[多智能体协作示例](multi-agent.md)
- 下一步学习：[模型配置示例](model-config.md) - 学习模型选择、fallback 和高级参数配置
- 相关文档：
  - [模型配置模块](../modules/models.md)
  - [最佳实践](../faq/best-practices.md)
