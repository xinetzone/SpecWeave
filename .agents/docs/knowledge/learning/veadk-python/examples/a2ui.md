---
id: veadk-python-a2ui
title: A2UI - Agent驱动UI示例
source: d:\AI\.chaos\libs\veadk-python\examples\a2ui_agent\agent.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# A2UI示例 (Agent-to-UI)

## 1. 示例功能介绍

本示例展示 VeADK 的 A2UI（Agent-to-UI）能力——让 Agent 不仅返回文本，还能直接驱动前端渲染富交互 UI 组件。A2UI 通过标准化的 JSON 描述 UI 结构，前端根据 JSON 动态渲染 Card、Column、Row、Text、Icon 等组件。

与传统的"前端写死模板"不同，A2UI 模式下：
- Agent 决定何时展示 UI、展示什么内容
- 组件结构通过 `send_a2ui_json_to_client` 工具发送
- 前端只需实现标准组件库，无需为每种场景写单独模板
- 同一套 A2UI JSON 可在 Web、移动端、桌面端渲染

**演示的核心能力**：
- 启用 A2UI 功能（`enable_a2ui=True`）
- 构造 A2UI 组件树（Card、Column、Row、Text、Icon、Divider）
- 使用 `send_a2ui_json_to_client` 工具发送 UI
- A2UI 指令编写（指导 Agent 何时、如何发送 UI）
- 与 VeADK Frontend 配合运行

---

## 2. 核心代码展示

完整代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/a2ui_agent/agent.py](file:///d:/AI/.chaos/libs/veadk-python/examples/a2ui_agent/agent.py)：

```python
import json

from veadk import Agent
from veadk.utils.pdf_to_images import pdf_to_images_before_model_callback

BASIC_CATALOG_ID = "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json"


def _flight_card_a2ui(flight: dict[str, str]) -> list[dict]:
    surface_id = f"flight-{flight['flight_no'].lower()}-{flight['date']}"
    components = [
        {"id": "root", "component": "Card", "child": "flight-content"},
        {
            "id": "flight-content",
            "component": "Column",
            "children": [
                "flight-top",
                "flight-hero",
                "flight-times",
                "flight-divider",
                "flight-details",
                "flight-footer",
            ],
        },
        # ... 更多组件定义（完整代码见源文件）
    ]
    return [
        {
            "version": "v0.9",
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": BASIC_CATALOG_ID,
            },
        },
        {
            "version": "v0.9",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": components,
            },
        },
    ]


def query_flight_info(
    flight_no: str = "MU5101",
    departure_city: str = "Shanghai",
    arrival_city: str = "Beijing",
    date: str = "2026-06-16",
) -> dict[str, str]:
    """Return one mock flight card for the A2UI demo.
    ...
    """
    normalized_flight_no = (flight_no or "MU5101").strip().upper()
    # ... 构造模拟航班数据
    flight["a2ui_json"] = json.dumps(_flight_card_a2ui(flight), ensure_ascii=False)
    return flight


INSTRUCTION = """You are an A2UI demo agent. Be fast and concise.

Never reveal chain-of-thought, planning, JSON drafting, or tool reasoning.

Flight demo flow:
1. If the user asks about flights, immediately call `query_flight_info`.
2. Do not infer dates such as "today"; use tool defaults unless the user gives
   an explicit YYYY-MM-DD value.
3. After `query_flight_info` returns, immediately call `send_a2ui_json_to_client`
   with the returned `a2ui_json` string verbatim.
4. Do not construct, rewrite, wrap, summarize, or explain the A2UI JSON.
5. If the A2UI tool fails once, stop and answer with a one-sentence plain-text
   fallback.

For non-flight requests, answer briefly in plain text unless a small A2UI card
is clearly useful.
"""

agent = Agent(
    name="a2ui_agent",
    description="Demo agent that replies with A2UI rich UI.",
    instruction=INSTRUCTION,
    tools=[query_flight_info],
    enable_a2ui=True,
    before_model_callback=pdf_to_images_before_model_callback,
)

root_agent = agent
```

> 注：`_flight_card_a2ui` 函数较长（约280行），定义了完整的航班卡片组件树，上面只展示了核心结构，完整定义请查看源文件。

---

## 3. 关键代码行逐行解释

| 行号 | 代码 | 解释 |
|------|------|------|
| 29 | `BASIC_CATALOG_ID = "https://a2ui.org/specification/..."` | A2UI 组件目录 ID，告诉前端使用哪个组件规范来渲染。`basic` catalog 包含 Card、Column、Row、Text、Icon、Divider 等基础组件 |
| 32-319 | `def _flight_card_a2ui(flight: dict) -> list[dict]:` | 构造航班状态卡片的 A2UI 组件树。返回一个操作列表：<br>1. `createSurface`：创建一个渲染表面（类似画布），指定 `surfaceId` 和 `catalogId`<br>2. `updateComponents`：在该表面上更新/添加组件树 |
| 34-303 | `components = [...]` | 组件树定义，核心概念：<br>- **每个组件有唯一 `id`**：用于引用和更新<br>- **`component` 字段**：指定组件类型（Card, Column, Row, Text, Icon, Divider）<br>- **`child`/`children`**：指定子组件（单个 child 或 children 列表）<br>- **布局属性**：`justify`（spaceBetween 等）、`align`（center、end 等）<br>- **组件属性**：如 Text 的 `text` 和 `variant`（h1/h2/h3/caption/body），Icon 的 `name` |
| 322-373 | `def query_flight_info(...)` | 工具函数：查询航班信息（此处是 mock 数据）。注意它返回的结果中包含 `a2ui_json` 字段——预先生成好的 A2UI JSON 字符串，供后续直接发送 |
| 372 | `flight["a2ui_json"] = json.dumps(_flight_card_a2ui(flight), ...)` | 将组件树序列化为 JSON 字符串，作为工具返回值的一部分 |
| 376-392 | `INSTRUCTION = """..."""` | **A2UI 指令至关重要**：明确告诉 Agent：<br>1. 何时调用查询工具<br>2. 查询后立即调用 `send_a2ui_json_to_client`<br>3. **必须原封不动传递** `a2ui_json`，不要自己构造或修改 JSON<br>4. 失败时的降级策略（纯文本回答） |
| 399 | `enable_a2ui=True,` | **关键开关**：启用 A2UI 功能。VeADK 会自动：<br>1. 注入 `send_a2ui_json_to_client` 工具<br>2. 在指令中补充 A2UI 相关说明<br>3. 支持前端通过 SSE/WebSocket 接收 A2UI 事件 |
| 402 | `before_model_callback=pdf_to_images_before_model_callback,` | 模型前置回调：自动将上传的 PDF 转换为图片，让视觉模型可以阅读（这是额外的多模态能力，非 A2UI 必需） |
| 406 | `root_agent = agent` | 导出 `root_agent`，供 VeADK Frontend 的 agent 加载器识别 |

### 🔑 A2UI 核心概念：组件树模型

A2UI 使用类似 React/Vue 的声明式组件树：

```
Surface (surfaceId)
  └─ Card (root)
       └─ Column (flight-content)
            ├─ Row (flight-top) - 顶部：航司 + 状态标签
            ├─ Row (flight-hero) - 主视觉：出发 → 到达 大字号
            ├─ Row (flight-times) - 时间：出发时间/到达时间
            ├─ Divider - 分隔线
            ├─ Row (flight-details) - 详情：航站楼/登机口/登机时间
            └─ Row (flight-footer) - 底部：数据来源 + 更新时间
```

**布局系统**：
- `Column`：垂直排列子组件
- `Row`：水平排列子组件
- `justify`：主轴对齐（spaceBetween=两端对齐、center=居中）
- `align`：交叉轴对齐（center、end=右对齐/底部对齐）

### 💡 为什么 A2UI JSON 在工具里预生成，而不是让 LLM 直接生成？

示例中使用 `_flight_card_a2ui()` 在 Python 代码中构造组件树，而不是让 LLM 生成，原因：
1. **可靠性**：代码生成的 JSON 100% 符合 Schema，不会有格式错误
2. **性能**：LLM 生成大段 JSON 慢且贵
3. **安全性**：避免 LLM 注入恶意组件结构
4. **最佳实践**：动态数据填充用代码，LLM 只负责决策"何时展示什么卡片"

对于简单场景，也可以让 LLM 直接生成 A2UI JSON（需在指令中提供组件 Schema），但复杂卡片推荐代码预生成。

---

## 4. 运行前置条件

### 环境要求
- Python 3.10+
- 已安装 veadk-python 包
- VeADK Frontend（用于渲染 A2UI 组件）

### API Key 配置
需要配置火山引擎方舟（Ark）的 API Key：

```bash
$env:ARK_API_KEY = "your-api-key-here"
```

### 运行方式

A2UI 示例不能直接用 `python agent.py` 运行（没有 main 函数），需要配合 VeADK Frontend：

```bash
# 在 veadk-python 根目录执行
veadk frontend --agents-dir examples
```

然后在浏览器打开：
```
http://127.0.0.1:8000
```

选择 `a2ui_agent`，然后输入提问，例如：
- "show me a flight status card"
- "查询 MU5101 航班状态"
- "帮我查一下从上海到北京的航班"

---

## 5. 预期运行效果/输出

运行 `veadk frontend` 后，在 Web UI 中提问航班相关问题：

**预期执行流程**：
1. 用户提问"查询航班状态"
2. Agent 识别意图，调用 `query_flight_info()` 获取航班数据
3. 工具返回中包含预先生成的 `a2ui_json`
4. Agent 按照指令调用 `send_a2ui_json_to_client`，将 A2UI JSON 原样发送
5. 前端接收到 A2UI 事件，渲染出一个精美的航班状态卡片
6. Agent 同时可以返回简短文字说明

**预期 UI 效果**：
- 一个带边框的卡片（Card）
- 顶部显示航司名称（China Eastern Airlines · MU5101）和绿色"On time"状态标签
- 中间大字显示出发（SHA 上海）→ 到达（PEK 北京），中间有时长和机型
- 下方显示出发/到达时间和机场
- 分隔线后显示航站楼（T2）、登机口（C18）、登机时间（08:55）
- 底部显示数据来源和更新时间

非航班问题（如"你好"）Agent 会用纯文本回答，不发送 UI 卡片。

---

## 6. 延伸学习

- 上一示例：[模型配置示例](model-config.md)
- 下一步学习：[链路追踪示例](tracing.md) - 学习如何追踪和调试 Agent 执行
- 相关文档：
  - [多模态支持](../modules/multimodal.md)
  - [最佳实践](../faq/best-practices.md)
  - [故障排查](../faq/troubleshooting.md)
