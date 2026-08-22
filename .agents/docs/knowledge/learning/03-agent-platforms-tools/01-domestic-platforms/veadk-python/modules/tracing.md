---
id: tracing-module
title: 可观测性与Tracing
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 可观测性与Tracing

## 概述

VeADK 提供了基于 OpenTelemetry 标准的完整可观测性解决方案，支持多种追踪后端（APMPlus、CozeLoop、TLS 日志服务、内存收集器等）。系统能够自动捕获 Agent 执行过程中的 LLM 调用、工具调用、用户输入输出等关键事件，并生成标准化的 Trace 数据用于调试、性能分析和质量评估。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/)

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        VeADK Agent                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Google ADK 事件钩子                           │  │
│  │  - trace_call_llm() → LLM 调用追踪                        │  │
│  │  - trace_tool_call() → 工具调用追踪                       │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │            OpentelemetryTracer (核心Tracer)                │  │
│  │  - 全局 TracerProvider 管理                               │  │
│  │  - Span 生命周期管理                                       │  │
│  │  - 多 Exporter 并行导出                                    │  │
│  │  - 本地 Trace 文件 dump                                    │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │                                    │
│          ┌─────────────────┼─────────────────┐                  │
│          ▼                 ▼                 ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ APMPlus      │  │ CozeLoop     │  │ TLS          │          │
│  │ Exporter     │  │ Exporter     │  │ Exporter     │          │
│  │ (gRPC OTLP)  │  │ (HTTP OTLP)  │  │ (HTTP OTLP)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│          │                 │                 │                  │
│          ▼                 ▼                 ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ InMemory     │  │ APMPlus      │  │ TLS 日志服务  │          │
│  │ Exporter     │  │ 监控平台      │  │ 存储与检索    │          │
│  │ (本地dump)   │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                            │                                    │
│                            ▼                                    │
│                   CozeLoop 评估平台                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## BaseTracer 抽象基类

`BaseTracer` 是所有 Tracer 实现的抽象基类，定义了统一的接口。

> 源码位置：[tracing/base_tracer.py#L22-L58](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/base_tracer.py#L22-L58)

```python
class BaseTracer(ABC):
    def __init__(self, name: str):
        self.name = name
        self._trace_id = "<unknown_trace_id>"
        self._trace_file_path = "<unknown_trace_file_path>"

    @abstractmethod
    def dump(self, user_id: str, session_id: str, path: str) -> str:
        """Dump the collected trace data to a local file."""
        ...
```

| 方法/属性 | 说明 |
|----------|------|
| `name` | Tracer 唯一标识符 |
| `_trace_id` | 当前执行上下文的 Trace ID |
| `_trace_file_path` | 当前 Trace 数据文件路径 |
| `dump(user_id, session_id, path)` | 将收集的 Trace 数据导出到本地文件 |

---

## OpentelemetryTracer - OpenTelemetry 实现

`OpentelemetryTracer` 是 VeADK 的核心 Tracer 实现，基于 OpenTelemetry 标准，支持多 Exporter 并行导出。

> 源码位置：[tracing/telemetry/opentelemetry_tracer.py#L54-L200](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/opentelemetry_tracer.py#L54-L200)

### 核心特性

1. **多 Exporter 支持**：可同时配置多个 Exporter，将 Trace 数据发送到不同后端
2. **Google ADK 集成**：自动 Patch Google ADK 的追踪函数（`trace_call_llm`、`trace_tool_call`）
3. **全局 TracerProvider 管理**：避免 VeFaaS 环境中全局 TracerProvider 冲突
4. **本地 Trace 导出**：内置 InMemoryExporter 支持本地 JSON 文件导出
5. **Span 限制配置**：默认每个 Span 最多 4096 个属性，支持详细数据捕获

### 初始化流程

```python
class OpentelemetryTracer(BaseModel, BaseTracer):
    name: str = "veadk_opentelemetry_tracer"
    exporters: list[BaseExporter] = []

    def model_post_init(self, context: Any) -> None:
        # 1. Patch Google ADK 遥测函数
        patch_google_adk_telemetry()

        # 2. 初始化全局 TracerProvider
        self._init_global_tracer_provider()

        # 3. 注册 LLM 响应 ID 回调
        _register_response_id_callback()
```

**关键设计：**
- 自动检测是否已有全局 TracerProvider（如 VeFaaS 环境预配置），避免冲突
- InMemoryExporter 由内部自动管理，禁止用户显式添加
- 每个 Exporter 可独立配置 resource_attributes

### 启用追踪

```python
from veadk import Agent
from veadk.tracing.telemetry import OpentelemetryTracer
from veadk.tracing.telemetry.exporters import (
    APMPlusExporter,
    CozeloopExporter,
    TLSExporter,
)

# 配置多个 Exporter
exporters = [
    APMPlusExporter(),      # 火山引擎 APMPlus 监控
    CozeloopExporter(),     # CozeLoop 评估平台
    TLSExporter(),          # 火山引擎 TLS 日志服务
]

tracer = OpentelemetryTracer(exporters=exporters)

agent = Agent(
    name="traced-agent",
    model_name="doubao-seed-2-1-pro-260628",
    tracers=[tracer],       # 将 tracer 添加到 Agent
)
```

### 本地 Dump Trace 文件

```python
# Agent 运行结束后，dump trace 到本地文件
trace_file = tracer.dump(
    user_id="user-123",
    session_id="session-456",
    path="./traces/"
)
print(f"Trace saved to: {trace_file}")
```

---

## 支持的追踪后端

VeADK 提供 4 种内置 Exporter，覆盖开发调试、生产监控、评估分析等不同场景。

### 1. InMemoryExporter - 内存收集器（内置）

**用途**：本地调试、单元测试、Trace 文件导出
**协议**：内存中直接存储 Span 对象
**自动管理**：由 OpentelemetryTracer 内部自动创建，无需用户配置

```python
# InMemoryExporter 始终存在，用于 dump 本地文件
# 不支持用户显式添加到 exporters 列表
```

### 2. APMPlusExporter - 火山引擎 APMPlus

**用途**：生产环境实时监控、性能指标采集、告警
**协议**：OTLP gRPC
**默认端点**：`http://apmplus-cn-beijing.volces.com:4317`
**默认服务名**：`veadk_tracing`

> 源码位置：[tracing/telemetry/exporters/apmplus_exporter.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/exporters/apmplus_exporter.py)
> 默认配置：[consts.py#L44-L45](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L44-L45)

**支持的 Metrics：**

| Metric 名称 | 说明 | Buckets |
|------------|------|---------|
| `gen_ai.client.operation.duration` | 客户端操作耗时 | 0.01s ~ 81.92s |
| `gen_ai.server.time_per_output_token` | 每输出 token 耗时 | 0.01s ~ 2.5s |
| `gen_ai.server.time_to_first_token` | 首 token 延迟（TTFT） | 0.001s ~ 10s |
| `gen_ai.client.token.usage` | Token 使用量 | 1 ~ 1M |

**特性：**
- 同时导出 Trace 和 Metrics
- 支持 Span 和 Metric 的批量处理
- 自动复用外部已配置的 TracerProvider（避免冲突）

```python
from veadk.tracing.telemetry.exporters import APMPlusExporter

exporter = APMPlusExporter()
# 配置自定义端点
# exporter = APMPlusExporter(
#     endpoint="http://apmplus-custom:4317",
#     service_name="my-agent-service",
# )
```

### 3. CozeloopExporter - CozeLoop 评估平台

**用途**：Agent 质量评估、对话分析、Prompt 优化
**协议**：OTLP HTTP
**默认端点**：`https://api.coze.cn/v1/loop/opentelemetry/v1/traces`

> 源码位置：[tracing/telemetry/exporters/cozeloop_exporter.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/exporters/cozeloop_exporter.py)
> 默认配置：[consts.py#L47-L49](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L47-L49)

**配置参数：**

| 参数 | 环境变量 | 说明 |
|------|---------|------|
| `endpoint` | - | CozeLoop OTLP 端点 |
| `space_id` | `COZELOOP_SPACE_ID` | CozeLoop 工作空间 ID |
| `token` | `COZELOOP_API_KEY` | CozeLoop API Token |

**认证方式：**
```python
headers = {
    "cozeloop-workspace-id": self.config.space_id,
    "authorization": f"Bearer {self.config.token}",
}
```

```python
from veadk.tracing.telemetry.exporters import CozeloopExporter

# 通过环境变量配置
# export COZELOOP_SPACE_ID=your-space-id
# export COZELOOP_API_KEY=your-token
exporter = CozeloopExporter()
```

### 4. TLSExporter - 火山引擎 TLS 日志服务

**用途**：Trace 长期存储、合规审计、跨服务关联分析
**协议**：OTLP HTTP
**默认端点**：`https://tls-cn-beijing.volces.com:4318/v1/traces`
**默认区域**：`cn-beijing`

> 源码位置：[tracing/telemetry/exporters/tls_exporter.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/exporters/tls_exporter.py)
> 默认配置：[consts.py#L51-L52](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L51-L52)

**配置参数：**

| 参数 | 环境变量 | 说明 |
|------|---------|------|
| `endpoint` | - | TLS OTLP HTTP 端点 |
| `region` | - | 火山引擎区域 |
| `topic_id` | `TLS_OTEL_EXPORTER_TOPIC_ID` | TLS 主题 ID |
| `access_key` | `VOLCENGINE_ACCESS_KEY` | 火山引擎 AK |
| `secret_key` | `VOLCENGINE_SECRET_KEY` | 火山引擎 SK |

```python
from veadk.tracing.telemetry.exporters import TLSExporter

# 通过环境变量配置
# export VOLCENGINE_ACCESS_KEY=AKLTxxx
# export VOLCENGINE_SECRET_KEY=xxx
# export TLS_OTEL_EXPORTER_TOPIC_ID=your-topic-id
exporter = TLSExporter()
```

---

## Trace 信息结构

### Span 类型

VeADK 追踪以下类型的 Span：

| Span 名称 | 触发时机 | 关键属性 |
|----------|---------|---------|
| `gen_ai.user.message` | 用户输入 | `gen_ai.prompt` (输入内容) |
| `gen_ai.assistant.message` | Assistant 输出 | `gen_ai.completion` (输出内容) |
| `gen_ai.llm.call` | LLM 调用 | `gen_ai.request.model`, `gen_ai.usage.*` |
| `gen_ai.tool.call` | 工具调用 | `gen_ai.tool.name`, `gen_ai.tool.call.args` |
| `gen_ai.tool.response` | 工具返回 | `gen_ai.tool.response` |

### 标准 GenAI 属性

遵循 OpenTelemetry GenAI 语义约定：

| 属性键 | 说明 |
|--------|------|
| `gen_ai.system` | AI 系统标识（如 `volcengine_ark`） |
| `gen_ai.request.model` | 请求的模型名称 |
| `gen_ai.request.temperature` | 温度参数 |
| `gen_ai.request.max_tokens` | 最大输出 token |
| `gen_ai.response.id` | 响应 ID（如 Ark 的 x-request-id） |
| `gen_ai.usage.input_tokens` | 输入 token 数 |
| `gen_ai.usage.output_tokens` | 输出 token 数 |
| `gen_ai.usage.total_tokens` | 总 token 数 |
| `gen_ai.tool.name` | 工具名称 |
| `gen_ai.tool.call.args` | 工具调用参数 |
| `gen_ai.tool.response` | 工具响应内容 |
| `veadk.app_name` | 应用名称 |
| `veadk.agent.name` | Agent 名称 |
| `veadk.user.id` | 用户 ID |
| `veadk.session.id` | 会话 ID |

> 属性提取器源码：[tracing/telemetry/attributes/extractors/](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/attributes/extractors/)

---

## 内容追踪控制

### should_trace_content()

通过 `should_trace_content()` 函数控制是否追踪消息内容（Prompt/Completion），避免敏感数据泄露。

> 源码位置：[tracing/telemetry/content_tracing.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/content_tracing.py)

```python
def should_trace_content() -> bool:
    """Check if content tracing is enabled.
    
    Content tracing includes:
    - User input messages
    - Assistant output messages
    - Tool call arguments
    - Tool responses
    
    When disabled, only metadata is traced (model name, token counts, timestamps).
    """
```

### 安全设计

- 默认行为：记录元数据，可控是否记录内容
- 敏感数据：工具参数和响应中的凭证自动脱敏
- 合规支持：TLS/APMPlus 等后端支持数据加密传输

---

## Metrics 指标上传

除了 Trace 链路追踪，VeADK 还支持 Metrics 指标采集：

### LLM 调用指标

```python
def _upload_call_llm_metrics(
    invocation_context: InvocationContext,
    event_id: str,
    llm_request: LlmRequest,
    llm_response: LlmResponse,
) -> None:
    """上传 LLM 调用指标：
    - Token 使用量（input/output/total）
    - 延迟（首 token 延迟、总耗时）
    - 模型名称、请求 ID
    """
```

> 源码位置：[tracing/telemetry/telemetry.py#L58-L87](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/telemetry.py#L58-L87)

### 工具调用指标

```python
def _upload_tool_call_metrics(
    tool: BaseTool,
    args: dict[str, Any],
    function_response_event: Event,
):
    """上传工具调用指标：
    - 工具名称
    - 执行耗时
    - 成功/失败状态
    - 参数和响应（受 content_tracing 控制）
    """
```

> 源码位置：[tracing/telemetry/telemetry.py#L89-L113](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/telemetry.py#L89-L113)

---

## 自定义 Exporter 开发

继承 `BaseExporter` 可开发自定义 Exporter：

> 源码位置：[tracing/telemetry/exporters/base_exporter.py#L20-L39](file:///d:/AI/.chaos/libs/veadk-python/veadk/tracing/telemetry/exporters/base_exporter.py#L20-L39)

```python
from opentelemetry.sdk.trace.export import SpanExporter, BatchSpanProcessor
from veadk.tracing.telemetry.exporters.base_exporter import BaseExporter

class CustomExporter(BaseExporter):
    """自定义 Exporter 示例"""

    def model_post_init(self, context: Any) -> None:
        # 1. 创建 SpanExporter
        self._exporter = MyCustomSpanExporter(
            endpoint="https://my-backend.com/traces",
            headers=self.headers,
        )
        # 2. 创建 SpanProcessor（通常用 BatchSpanProcessor）
        self.processor = BatchSpanProcessor(self._exporter)
        # 3. 设置 resource_attributes（可选）
        self.resource_attributes = {
            "service.name": "my-custom-service",
        }

    def export(self) -> None:
        """强制导出（可选实现）"""
        if self.processor:
            self.processor.force_flush()

# 使用自定义 Exporter
from veadk.tracing.telemetry import OpentelemetryTracer

custom_exporter = CustomExporter()
tracer = OpentelemetryTracer(exporters=[custom_exporter])
```

### 开发要点

1. **必须设置 `self.processor`**：这是 OpenTelemetry 处理 Span 的核心组件
2. **推荐 BatchSpanProcessor**：生产环境使用批量处理提高性能
3. **Resource Attributes**：用于标识服务、环境、版本等元数据
4. **Headers 认证**：通过 `self.headers` 设置认证头（自动合并）
5. **异常处理**：Exporter 应妥善处理网络错误，避免影响 Agent 主流程

---

## 配置参考

### 环境变量配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | APMPlus OTLP gRPC 端点 | `http://apmplus-cn-beijing.volces.com:4317` |
| `OTEL_SERVICE_NAME` | APMPlus 服务名称 | `veadk_tracing` |
| `COZELOOP_SPACE_ID` | CozeLoop 工作空间 ID | - |
| `COZELOOP_API_KEY` | CozeLoop API Token | - |
| `TLS_OTEL_EXPORTER_ENDPOINT` | TLS OTLP HTTP 端点 | `https://tls-cn-beijing.volces.com:4318/v1/traces` |
| `TLS_OTEL_EXPORTER_REGION` | TLS 区域 | `cn-beijing` |
| `TLS_OTEL_EXPORTER_TOPIC_ID` | TLS 主题 ID | - |
| `VOLCENGINE_ACCESS_KEY` | 火山引擎 AK | - |
| `VOLCENGINE_SECRET_KEY` | 火山引擎 SK | - |
| `VEADK_TRACE_CONTENT` | 是否追踪消息内容 | `true` |

---

## 使用示例

### 开发环境（仅本地文件）

```python
from veadk import Agent
from veadk.tracing.telemetry import OpentelemetryTracer

# 不配置任何远程 Exporter，仅使用 InMemoryExporter 做本地 dump
tracer = OpentelemetryTracer()

agent = Agent(
    name="dev-agent",
    model_name="doubao-seed-2-1-pro-260628",
    tracers=[tracer],
)

# ... 运行 Agent ...

# 导出 trace 文件
trace_path = tracer.dump(
    user_id="dev-user",
    session_id="test-session",
    path="./dev-traces/"
)
```

### 生产环境（APMPlus）

```python
from veadk import Agent
from veadk.tracing.telemetry import OpentelemetryTracer
from veadk.tracing.telemetry.exporters import APMPlusExporter
import os

# APMPlus 通常由 VeFaaS 环境自动配置全局 TracerProvider
# 这里只需添加 APMPlusExporter
tracer = OpentelemetryTracer(exporters=[APMPlusExporter()])

agent = Agent(
    name="production-agent",
    model_name="doubao-seed-2-1-pro-260628",
    tracers=[tracer],
)
```

### 评估环境（CozeLoop）

```bash
# .env
COZELOOP_SPACE_ID=your-workspace-id
COZELOOP_API_KEY=your-cozeloop-token
```

```python
from veadk import Agent
from veadk.tracing.telemetry import OpentelemetryTracer
from veadk.tracing.telemetry.exporters import CozeloopExporter, APMPlusExporter

# 同时发送到 CozeLoop 做评估 + APMPlus 做监控
tracer = OpentelemetryTracer(exporters=[
    CozeloopExporter(),
    APMPlusExporter(),
])

agent = Agent(
    name="eval-agent",
    model_name="doubao-seed-2-1-pro-260628",
    tracers=[tracer],
)
```

### 多后端组合

```python
from veadk.tracing.telemetry import OpentelemetryTracer
from veadk.tracing.telemetry.exporters import (
    APMPlusExporter,
    CozeloopExporter,
    TLSExporter,
)

# 三后端并行导出
tracer = OpentelemetryTracer(exporters=[
    APMPlusExporter(),      # 实时监控 + Metrics
    CozeloopExporter(),     # 质量评估
    TLSExporter(),          # 长期存储 + 审计
])
```

---

## 目录结构

```
veadk/tracing/
├── __init__.py
├── base_tracer.py                    # BaseTracer 抽象基类
└── telemetry/
    ├── __init__.py
    ├── opentelemetry_tracer.py       # OpentelemetryTracer 核心实现
    ├── telemetry.py                  # 遥测钩子（LLM/工具调用指标上传）
    ├── content_tracing.py            # 内容追踪开关控制
    ├── litellm_response_id.py        # LiteLLM 响应 ID 注册
    ├── attributes/
    │   ├── attributes.py             # 属性定义
    │   └── extractors/
    │       ├── common_attributes_extractors.py
    │       ├── llm_attributes_extractors.py
    │       ├── tool_attributes_extractors.py
    │       └── types.py
    └── exporters/
        ├── __init__.py
        ├── base_exporter.py          # BaseExporter 抽象基类
        ├── apmplus_exporter.py       # 火山引擎 APMPlus Exporter (gRPC)
        ├── cozeloop_exporter.py      # CozeLoop Exporter (HTTP)
        ├── tls_exporter.py           # TLS 日志服务 Exporter (HTTP)
        └── inmemory_exporter.py      # 内存 Exporter（内置，本地dump）
```
