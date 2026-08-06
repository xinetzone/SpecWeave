---
id: veadk-python-tracing
title: 11 - 链路追踪示例
source: d:\AI\.chaos\libs\veadk-python\examples\11_tracing\main.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# 链路追踪示例 (Tracing & Observability)

## 1. 示例功能介绍

本示例展示 VeADK 的链路追踪（Tracing）可观测性能力。通过挂载 Tracer，每一次 LLM 调用、工具调用都会被记录为 Span，并生成一个全局唯一的 `trace_id`（32位十六进制字符串）。你可以用这个 trace_id 在后端平台搜索查看完整的调用链，便于调试、性能分析和问题排查。

VeADK 支持多种导出器：
- **内存模式**（默认）：无需任何配置，span 收集在内存中，仍可获取 trace_id
- **APMPlus**：火山引擎应用性能监控平台
- **CozeLoop**：扣子可观测性平台
- **TLS**：火山引擎日志服务

**演示的核心能力**：
- 使用 `OpentelemetryTracer` 启用追踪
- 配置多个云导出器（通过环境变量开关）
- 获取每次运行的 `trace_id`
- 将 Tracer 挂载到 Agent
- Span 的自动生成（LLM 调用、工具调用）

---

## 2. 核心代码展示

完整代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/11_tracing/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/11_tracing/main.py)：

```python
import asyncio
import os

from veadk import Agent, Runner
from veadk.tracing.telemetry.exporters.base_exporter import BaseExporter
from veadk.tracing.telemetry.opentelemetry_tracer import OpentelemetryTracer

SESSION_ID = "demo-session"


def _enabled(env_name: str) -> bool:
    return os.getenv(env_name, "").lower() == "true"


def build_exporters() -> list[BaseExporter]:
    """Build the cloud exporters enabled via env (their config is read from .env)."""
    exporters: list[BaseExporter] = []
    if _enabled("ENABLE_APMPLUS"):
        from veadk.tracing.telemetry.exporters.apmplus_exporter import APMPlusExporter

        exporters.append(APMPlusExporter())
    if _enabled("ENABLE_COZELOOP"):
        from veadk.tracing.telemetry.exporters.cozeloop_exporter import (
            CozeloopExporter,
        )

        exporters.append(CozeloopExporter())
    if _enabled("ENABLE_TLS"):
        from veadk.tracing.telemetry.exporters.tls_exporter import TLSExporter

        exporters.append(TLSExporter())
    return exporters


def get_city_weather(city: str) -> dict[str, str]:
    """Get the current weather for a city.

    Args:
        city: The English name of the city, e.g. "Beijing".
    """
    return {"result": {"beijing": "Sunny, 25°C"}.get(city.lower(), "Unknown")}


async def main() -> None:
    exporters = build_exporters()
    tracer = OpentelemetryTracer(exporters=exporters)
    print(
        "Exporters:",
        [type(e).__name__ for e in exporters] or "in-memory only (no cloud export)",
    )

    agent = Agent(
        name="traced_agent",
        instruction="Help with weather. Use get_city_weather when asked.",
        tools=[get_city_weather],
        tracers=[tracer],
    )

    runner = Runner(agent=agent, app_name="tracing_demo")

    answer = await runner.run(messages="北京今天天气怎么样？", session_id=SESSION_ID)
    print("Answer:", answer)

    print("Trace id:", runner.get_trace_id())


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. 关键代码行逐行解释

| 行号 | 代码 | 解释 |
|------|------|------|
| 31-32 | `from veadk.tracing.telemetry.opentelemetry_tracer import OpentelemetryTracer` | 导入基于 OpenTelemetry 的 Tracer 实现。OpenTelemetry 是云原生可观测性的标准，VeADK 原生兼容 |
| 37-38 | `def _enabled(env_name: str) -> bool:` | 辅助函数：检查环境变量是否为 `"true"`，用于控制哪些导出器启用 |
| 41-58 | `def build_exporters() -> list[BaseExporter]:` | 根据环境变量动态构建导出器列表：<br>- `ENABLE_APMPLUS=true` → 添加 APMPlusExporter<br>- `ENABLE_COZELOOP=true` → 添加 CozeloopExporter<br>- `ENABLE_TLS=true` → 添加 TLSExporter<br>- 延迟导入（在 if 块内 import），避免未启用时加载不必要的依赖<br>- 如果没有启用任何导出器，返回空列表 → 纯内存模式 |
| 61-67 | `def get_city_weather(city: str) -> dict[str, str]:` | 一个简单的天气工具，用于演示工具调用也会被追踪为 Span |
| 73-74 | `exporters = build_exporters()`<br>`tracer = OpentelemetryTracer(exporters=exporters)` | 创建 Tracer 实例：<br>- 传入导出器列表<br>- 空列表表示只在内存收集（无云导出）<br>- 内存模式下依然会生成 trace_id，可用于本地调试 |
| 80-85 | `agent = Agent(..., tracers=[tracer],)` | **挂载 Tracer**：通过 `tracers` 参数传入一个或多个 Tracer。挂载后，该 Agent 的所有操作都会被追踪：<br>- 每次 LLM 调用 → 一个 Span<br>- 每次工具调用 → 一个 Span<br>- 整个 run → 一个根 Span |
| 94 | `print("Trace id:", runner.get_trace_id())` | **获取 trace_id**：每次 `runner.run()` 后，可以通过 `runner.get_trace_id()` 获取本次运行的唯一追踪 ID。这是一个 32 字符的十六进制字符串，可在对应平台的 UI 中搜索查看完整调用链 |

### 🔑 追踪数据模型：Trace 和 Span

```
Trace (trace_id: a1b2c3d4...)
  └─ Root Span: "tracing_demo run"
       ├─ Span: "LLM call - turn 1" (模型输入输出、token数、延迟)
       │    └─ Span: "Tool call - get_city_weather" (参数、返回值、耗时)
       └─ Span: "LLM call - turn 2" (根据工具结果生成最终回答)
```

- **Trace**：一次完整的用户请求处理过程，由唯一 `trace_id` 标识
- **Span**：Trace 中的单个操作单元，有开始时间、结束时间、属性（attributes）、事件（events）
- **父子关系**：Span 之间形成树状结构，反映调用层级

每个 Span 自动记录的信息包括：
- 操作名称和类型（LLM / tool / run）
- 开始时间和结束时间（延迟）
- 输入和输出（可配置脱敏）
- Token 使用量（LLM span）
- 模型名称、参数（LLM span）
- 工具名称、参数、返回值（tool span）
- 错误信息（如果失败）

### 💡 环境变量配置

启用云导出器需要在 `.env` 中配置对应的认证信息，参考示例目录下的 `.env.example`：

```bash
# 启用/禁用开关
ENABLE_APMPLUS=true
ENABLE_COZELOOP=false
ENABLE_TLS=false

# APMPlus 配置（火山引擎 AK/SK 认证）
APMPLUS_AK=your-access-key
APMPLUS_SK=your-secret-key
APMPLUS_REGION=cn-beijing
APMPLUS_APP_ID=your-app-id

# CozeLoop 配置
COZELOOP_API_KEY=your-cozeloop-key
# ...
```

---

## 4. 运行前置条件

### 环境要求
- Python 3.10+
- 已安装 veadk-python 包

### API Key 配置
需要配置火山引擎方舟（Ark）的 API Key：

```bash
$env:ARK_API_KEY = "your-api-key-here"
```

云导出器是**可选**的。即使不配置任何云导出器，追踪依然在内存中工作，你可以获取 trace_id。

如需启用云导出，复制 `.env.example` 为 `.env`，设置 `ENABLE_*=true` 并填入对应平台的认证信息。

### 依赖安装
```bash
pip install veadk-python
```

云导出器可能需要额外依赖，veadk-python 的 tracing 模块已包含必要的 OpenTelemetry 依赖。

---

## 5. 预期运行效果/输出

### 5.1 纯内存模式（无云导出）

不配置任何 `ENABLE_*` 环境变量，直接运行：

```bash
cd 11_tracing
python main.py
```

**预期输出**：
```
Exporters: in-memory only (no cloud export)
Answer: 北京今天天气晴朗，气温25°C。
Trace id: a1b2c3d4e5f6789012345678abcdef01
```

可以看到：
1. 没有启用云导出器，使用内存模式
2. Agent 正常回答天气问题
3. 生成了一个 32 字符的 trace_id

内存模式下，span 数据收集在进程内存中，进程退出后丢失。适合快速验证和本地调试。

### 5.2 启用云导出模式

配置 `.env` 后运行：

```bash
Exporters: ['APMPlusExporter']
Answer: 北京今天天气晴朗，气温25°C。
Trace id: f1e2d3c4b5a697880123456789abcdef
```

此时除了控制台输出，追踪数据还会异步发送到配置的云平台。你可以：
1. 复制打印的 trace_id
2. 登录对应平台（APMPlus / CozeLoop / TLS）
3. 在搜索框输入 trace_id
4. 查看完整的调用链瀑布图，包括每个 LLM 调用的耗时、token 用量、工具调用详情等

### 典型 Span 结构（在平台中可见）

```
run (session=demo-session) - 2.3s
  ├─ llm:doubao-seed-1.6 - 1.8s
  │   - prompt tokens: 423
  │   - completion tokens: 156
  │   - tool calls: [get_city_weather(city="Beijing")]
  ├─ tool:get_city_weather - 0.001s
  │   - args: {"city": "Beijing"}
  │   - result: {"result": "Sunny, 25°C"}
  └─ llm:doubao-seed-1.6 - 0.4s
      - prompt tokens: 587
      - completion tokens: 42
      - output: "北京今天天气晴朗，气温25°C。"
```

通过追踪数据，你可以：
- 发现哪个步骤慢（LLM 调用？工具调用？）
- 检查工具参数是否正确
- 统计 token 用量和成本
- 定位失败原因（如果某个 span 有 error）

---

## 6. 延伸学习

- 上一示例：[A2UI示例](a2ui.md)
- 相关文档：
  - [链路追踪模块详解](../modules/tracing.md)
  - [最佳实践](../faq/best-practices.md)
  - [故障排查](../faq/troubleshooting.md)

---

## 示例索引

| 序号 | 示例 | 文档 |
|------|------|------|
| 01 | 最小Agent示例 | [quickstart.md](quickstart.md) |
| 02 | 自定义工具示例 | [custom-tools.md](custom-tools.md) |
| 03/09 | 记忆示例（短期+长期） | [memory.md](memory.md) |
| 05 | 知识库RAG示例 | [knowledgebase.md](knowledgebase.md) |
| 06 | 多智能体协作示例 | [multi-agent.md](multi-agent.md) |
| 07 | 结构化输出示例 | [structured-output.md](structured-output.md) |
| 08 | 模型配置示例 | [model-config.md](model-config.md) |
| - | A2UI示例 | [a2ui.md](a2ui.md) |
| 11 | 链路追踪示例 | [tracing.md](tracing.md) |
