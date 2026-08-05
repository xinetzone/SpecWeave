---
id: veadk-python-custom-tools
title: 02 - 自定义工具示例
source: d:\AI\.chaos\libs\veadk-python\examples\02_custom_tools\main.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# 自定义工具示例 (Custom Tools)

## 1. 示例功能介绍

本示例展示如何为 Agent 添加自定义工具（Tools）。在 VeADK 中，"工具"就是一个带有类型提示（type hints）和文档字符串（docstring）的普通 Python 函数。模型会阅读文档字符串来决定**何时**以及**如何**调用工具，因此文档字符串是写给模型看的，而不仅仅是给人类看的。

**演示的核心能力**：
- 使用普通 Python 函数定义工具
- 通过 `tools` 参数将工具注册到 Agent
- 工具链式调用（先查天气再推荐穿衣）
- 类型提示与文档字符串的重要性
- 多步推理与工具自动调用

---

## 2. 核心代码展示

完整代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/02_custom_tools/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/02_custom_tools/main.py)：

```python
import asyncio

from veadk import Agent, Runner


def get_city_weather(city: str) -> dict[str, str]:
    """Get the current weather for a city.

    Args:
        city: The English name of the city, e.g. "Beijing".

    Returns:
        A dict with a human-readable weather "result".
    """
    fixed_weather = {
        "beijing": "Sunny, 25°C",
        "shanghai": "Cloudy, 22°C",
        "shenzhen": "Partly cloudy, 29°C",
    }
    return {"result": fixed_weather.get(city.lower().strip(), f"No data for {city}")}


def recommend_clothing(temperature_celsius: int) -> dict[str, str]:
    """Recommend what to wear for a given temperature.

    Args:
        temperature_celsius: The temperature in degrees Celsius.

    Returns:
        A dict with a clothing "result" suggestion.
    """
    if temperature_celsius < 10:
        advice = "Wear a thick coat."
    elif temperature_celsius < 23:
        advice = "A light jacket is enough."
    else:
        advice = "T-shirt weather."
    return {"result": advice}


async def main() -> None:
    agent = Agent(
        name="weather_agent",
        description="An assistant that checks weather and suggests clothing.",
        instruction=(
            "You help users with weather. Use `get_city_weather` to look up "
            "conditions, then `recommend_clothing` based on the temperature. "
            "Always state the temperature you used."
        ),
        tools=[get_city_weather, recommend_clothing],
    )

    runner = Runner(agent=agent, app_name="custom_tools")

    answer = await runner.run(
        messages="北京今天天气怎么样？我该穿什么？",
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
| 27-41 | `def get_city_weather(city: str) -> dict[str, str]:` | 定义查询天气的工具函数：<br>- **类型提示** `city: str` 告诉模型参数是字符串类型<br>- **返回类型** `dict[str, str]` 说明返回格式<br>- **文档字符串**详细描述函数功能、参数含义、返回值含义——这是模型判断是否调用该工具的关键依据 |
| 44-59 | `def recommend_clothing(temperature_celsius: int) -> dict[str, str]:` | 定义穿衣推荐工具函数，同样遵循"类型提示+文档字符串"模式 |
| 71 | `tools=[get_city_weather, recommend_clothing],` | 将工具函数列表传入 Agent 构造函数完成注册。注意：传入的是函数对象本身（不加括号），不是函数调用结果 |
| 66-70 | `instruction=(...)` | 在指令中明确指导 Agent 如何使用工具：先调用 `get_city_weather`，再根据温度调用 `recommend_clothing`，最后说明使用的温度值 |
| 77 | `messages="北京今天天气怎么样？我该穿什么？"` | 用户用中文提问，但工具参数要求英文城市名——Agent 会自动将"北京"转换为"Beijing"传给工具 |

### 🔑 为什么类型提示和文档字符串如此重要？

1. **类型提示**：模型根据类型提示生成正确格式的参数。如果类型标注错误，模型可能传入错误类型的参数导致调用失败。
2. **文档字符串**：
   - 第一行是工具的一句话功能描述——模型以此判断是否应该调用此工具
   - `Args` 部分描述每个参数的含义和示例值（如 `e.g. "Beijing"`）
   - `Returns` 部分说明返回值结构——模型以此理解如何使用返回结果
3. **指令引导**：在 `instruction` 中明确告诉 Agent 工具调用顺序和要求，能显著提升工具调用准确率。

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

或复制 `.env.example` 为 `.env` 并填入配置。

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

**预期执行流程**：
1. Agent 理解用户问题，识别需要查询天气
2. 自动调用 `get_city_weather(city="Beijing")`
3. 获取结果 `{"result": "Sunny, 25°C"}`，解析出温度 25°C
4. 自动调用 `recommend_clothing(temperature_celsius=25)`
5. 获取穿衣建议后，整合信息生成自然语言回答

**预期输出**（示例）：
```
北京今天天气晴朗，气温25°C。基于25°C的温度，建议穿T恤就可以了。
```

---

## 6. 延伸学习

- 上一示例：[最小Agent示例](quickstart.md)
- 下一步学习：[记忆示例](memory.md) - 学习短期与长期记忆的使用
- 相关文档：
  - [工具模块详解](../modules/tools.md)
  - [自定义工具开发](../extensions/custom-tool.md)
  - [最佳实践](../faq/best-practices.md)
