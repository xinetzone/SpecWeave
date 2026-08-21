---
id: custom-run-processor
title: 自定义RunProcessor开发指南
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 自定义RunProcessor开发指南

本文档介绍 RunProcessor（运行处理器）的概念、接口定义和开发方法。RunProcessor 是 VeADK 中实现横切关注点的核心机制，类似 Web 框架中的中间件模式。

---

## 一、RunProcessor 是什么

RunProcessor 采用**装饰器模式**包装 Agent 的事件生成器（event generator），用于实现认证、日志、监控、限流、审计等**横切关注点**（cross-cutting concerns）。

### 核心机制

与传统中间件类似，RunProcessor 可以在 Agent 执行流程的前后插入逻辑：

```
请求进入 → [Processor前处理] → Agent执行（事件流） → [Processor后处理] → 响应返回
                         ↓
                  [可注入自定义事件]
                  [可中断/重试/循环]
```

参考：[架构洞察8 - RunProcessor装饰器链模式](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L234-L260)

### 适用场景

| 场景 | 说明 |
|---|---|
| **认证/授权** | OAuth2 认证流程、API Key 验证（参考 AuthRequestProcessor） |
| **日志记录** | 请求/响应日志、执行时间统计 |
| **性能监控** | Token 用量统计、LLM 调用次数追踪 |
| **限流熔断** | 请求频率限制、错误率熔断 |
| **审计追踪** | 敏感操作审计、合规日志 |
| **错误重试** | 临时性错误自动重试 |
| **事件过滤/转换** | 修改、过滤或注入事件 |
| **对话中断恢复** | 暂停对话等待外部输入后恢复 |

### 与其他扩展点的区别

| 扩展点 | 作用层级 | 适用场景 |
|---|---|---|
| Tool | Agent能力层 | 扩展Agent可调用的功能 |
| RunProcessor | 执行流程层 | 拦截和控制Agent执行流程 |
| Extension | 接入层 | 外部渠道/平台集成 |
| Callback | 回调点 | 特定时机的钩子（before_agent等） |

---

## 二、BaseRunProcessor 接口定义

**文件**：[veadk/processors/base_run_processor.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/processors/base_run_processor.py#L27-L120)

```python
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from google.genai import types
    from veadk.runner import Runner


class BaseRunProcessor(ABC):
    """RunProcessor抽象基类。"""

    @abstractmethod
    def process_run(
        self,
        runner: Runner,
        message: types.Content,
        **kwargs: Any,
    ) -> Callable[
        [Callable[[], AsyncGenerator]],
        Callable[[], AsyncGenerator]
    ]:
        """处理Agent运行，返回包装事件生成器的装饰器。

        Args:
            runner: 执行Agent的Runner实例。
            message: 发送给Agent的初始消息。
            **kwargs: 额外参数（如task_updater状态更新器）。

        Returns:
            装饰器函数：接收原始事件生成器，返回包装后的事件生成器。
        """
        pass
```

### 默认实现：NoOpRunProcessor

[NoOpRunProcessor](file:///d:/AI/.chaos/libs/veadk-python/veadk/processors/base_run_processor.py#L91-L120) 是空实现，直接返回原始事件生成器，无任何开销：

```python
class NoOpRunProcessor(BaseRunProcessor):
    def process_run(self, runner, message, **kwargs):
        def decorator(event_generator_func):
            return event_generator_func  # 恒等装饰器：直接返回原函数
        return decorator
```

### 核心调用点

RunProcessor 在 [runner.py:541-553](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L239-L241) 中通过Python装饰器语法应用：

```python
@processor.process_run(runner=runner, message=message, **kwargs)
async def event_generator():
    async for event in runner.run_async(...):
        yield event

async for event in event_generator():
    # 处理事件
    ...
```

### 三级优先级解析

RunProcessor 选择遵循优先级链（参考架构洞察8）：

1. **最高**：`runner.run(..., run_processor=MyProcessor())` - 单次运行级别
2. **其次**：`Runner(agent=agent, run_processor=MyProcessor())` - Runner实例级别
3. **其次**：`Agent(..., run_processor=MyProcessor())` - Agent实例级别
4. **最低**：`NoOpRunProcessor` - 默认空实现

---

## 三、内置RunProcessor分析

### AuthRequestProcessor（OAuth2认证处理器）

**文件**：[veadk/integrations/ve_identity/auth_processor.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_identity/auth_processor.py#L159-L385)

这是最复杂的内置RunProcessor实现，展示了如何实现"对话中断→等待用户认证→恢复执行"的完整流程：

**核心逻辑**：
1. 包装 `runner.run_async`，检测认证请求事件
2. 检测到认证请求时，中断主流程
3. 向用户展示授权URL
4. 轮询等待用户完成OAuth授权
5. 获取token后，构造认证响应消息
6. 重新执行Agent（循环直到无认证请求）

关键代码结构：

```python
class AuthRequestProcessor(BaseRunProcessor):
    def __init__(self, *, config: Optional[AuthRequestConfig] = None):
        self.config = config or AuthRequestConfig(...)
        self._identity_client = get_default_identity_client(...)

    def process_run(self, runner, message, **kwargs):
        task_updater = kwargs.get("task_updater")

        def decorator(event_generator_func):
            async def wrapper():
                current_message = message

                for _ in range(self.config.max_auth_cycles or DEFAULT_MAX_CYCLES):
                    auth_request_event_id = None
                    auth_config = None
                    cycle_buffer = []

                    original_run_async = runner.run_async

                    async def wrapped_run_async(**run_kwargs):
                        nonlocal auth_request_event_id, auth_config
                        run_kwargs["new_message"] = current_message

                        async for event in original_run_async(**run_kwargs):
                            if is_pending_auth_event(event):
                                auth_request_event_id = get_function_call_id(event)
                                auth_config = get_function_call_auth_config(event)
                                break
                            yield event

                    runner.run_async = wrapped_run_async

                    try:
                        async for chunk in event_generator_func():
                            cycle_buffer.append(chunk)
                    finally:
                        runner.run_async = original_run_async

                    if auth_request_event_id and auth_config:
                        current_message = await self.process_auth_request(
                            auth_request_event_id, auth_config, task_updater
                        )
                    else:
                        yield cycle_buffer[-1]
                        break

            return wrapper
        return decorator
```

这个实现展示了RunProcessor的高级能力：
- **事件拦截**：通过替换 `runner.run_async` 检测特定事件
- **流程控制**：通过循环实现"认证-重试"模式
- **事件注入**：认证完成后构造新的消息重新触发Agent
- **状态更新**：通过 `task_updater` 向前端发送状态更新
- **资源清理**：`finally`块中恢复原始的 `runner.run_async`

---

## 四、开发步骤

### 步骤1：继承BaseRunProcessor

```python
from veadk.processors.base_run_processor import BaseRunProcessor

class MyCustomProcessor(BaseRunProcessor):
    def __init__(self, config_param: str = "default"):
        """初始化处理器，可接收配置参数。"""
        self.config_param = config_param
        super().__init__()
```

### 步骤2：实现process_run方法

`process_run` 方法必须返回一个**装饰器函数**，该装饰器接收原始事件生成器函数，返回包装后的事件生成器函数。

#### 最小实现模板

```python
from typing import Any, AsyncGenerator, Callable
from veadk.processors.base_run_processor import BaseRunProcessor

class MyProcessor(BaseRunProcessor):
    def process_run(
        self,
        runner: "Runner",
        message: "types.Content",
        **kwargs: Any,
    ) -> Callable[[Callable[[], AsyncGenerator]], Callable[[], AsyncGenerator]]:

        def decorator(
            event_generator_func: Callable[[], AsyncGenerator]
        ) -> Callable[[], AsyncGenerator]:

            async def wrapper() -> AsyncGenerator:
                # === 前处理：事件流开始前 ===
                print(f"[Before] Processing message...")

                # 调用原始事件生成器，转发所有事件
                async for event in event_generator_func():
                    # === 事件级处理：每个事件可在此修改/过滤 ===
                    yield event  # 必须yield事件，否则事件会丢失

                # === 后处理：事件流结束后 ===
                print(f"[After] Processing complete.")

            return wrapper
        return decorator
```

### 步骤3：注册和使用

```python
from veadk import Agent, Runner

agent = Agent(
    name="my_agent",
    instruction="...",
)

# 方式1：Agent级别（所有运行都使用）
agent_with_processor = Agent(
    name="my_agent",
    instruction="...",
    run_processor=MyProcessor(config_param="value"),
)

# 方式2：Runner级别
runner = Runner(
    agent=agent,
    app_name="my_app",
    run_processor=MyProcessor(),
)

# 方式3：单次运行级别（最高优先级）
result = await runner.run(
    messages="你好",
    run_processor=MyProcessor(),  # 仅本次运行使用
)
```

---

## 五、代码模板

### 模板1：日志/监控Processor

```python
from __future__ import annotations
import time
from typing import Any, AsyncGenerator, Callable, TYPE_CHECKING

from veadk.processors.base_run_processor import BaseRunProcessor
from veadk.utils.logger import get_logger

if TYPE_CHECKING:
    from google.genai import types
    from veadk.runner import Runner

logger = get_logger(__name__)


class LoggingProcessor(BaseRunProcessor):
    """日志和性能监控Processor。

    记录请求开始/结束时间、事件数量、Token用量等信息。
    """

    def __init__(
        self,
        log_events: bool = False,
        slow_threshold_ms: int = 5000,
    ):
        """
        Args:
            log_events: 是否记录每个事件的详细信息。
            slow_threshold_ms: 慢请求阈值（毫秒），超过此时间会打warning日志。
        """
        super().__init__()
        self.log_events = log_events
        self.slow_threshold_ms = slow_threshold_ms

    def process_run(
        self,
        runner: Runner,
        message: types.Content,
        **kwargs: Any,
    ) -> Callable[[Callable[[], AsyncGenerator]], Callable[[], AsyncGenerator]]:

        def decorator(event_generator_func):
            async def wrapper():
                start_time = time.time()
                event_count = 0
                error = None

                # 提取用户消息文本用于日志
                user_text = ""
                if message.parts:
                    for part in message.parts:
                        if part.text:
                            user_text = part.text[:100]
                            break

                logger.info(
                    f"[RunStart] session={kwargs.get('session_id', 'unknown')} "
                    f"user={kwargs.get('user_id', 'unknown')} "
                    f"message={user_text!r}"
                )

                try:
                    async for event in event_generator_func():
                        event_count += 1

                        if self.log_events:
                            event_type = type(event).__name__
                            logger.debug(f"[Event#{event_count}] type={event_type}")

                        yield event

                except Exception as e:
                    error = e
                    logger.error(f"[RunError] {type(e).__name__}: {e}", exc_info=True)
                    raise
                finally:
                    elapsed_ms = (time.time() - start_time) * 1000
                    log_msg = (
                        f"[RunEnd] events={event_count} "
                        f"elapsed={elapsed_ms:.0f}ms"
                    )
                    if error:
                        log_msg += f" error={type(error).__name__}"
                    if elapsed_ms > self.slow_threshold_ms:
                        logger.warning(log_msg + " (SLOW)")
                    else:
                        logger.info(log_msg)

            return wrapper
        return decorator
```

### 模板2：请求限流Processor

```python
from __future__ import annotations
import asyncio
import time
from collections import defaultdict
from typing import Any, AsyncGenerator, Callable, TYPE_CHECKING

from veadk.processors.base_run_processor import BaseRunProcessor
from veadk.utils.logger import get_logger

if TYPE_CHECKING:
    from google.genai import types
    from veadk.runner import Runner

logger = get_logger(__name__)


class RateLimitProcessor(BaseRunProcessor):
    """请求限流Processor。

    基于用户ID进行请求频率限制。
    """

    def __init__(
        self,
        max_requests_per_minute: int = 30,
        max_concurrent: int = 5,
    ):
        """
        Args:
            max_requests_per_minute: 每分钟最大请求数（每用户）。
            max_concurrent: 最大并发请求数（全局）。
        """
        super().__init__()
        self.max_rpm = max_requests_per_minute
        self.max_concurrent = max_concurrent
        self._request_timestamps: dict[str, list[float]] = defaultdict(list)
        self._concurrent_semaphore = asyncio.Semaphore(max_concurrent)

    def _check_rate_limit(self, user_id: str) -> tuple[bool, str]:
        """检查用户是否超过限流阈值。"""
        now = time.time()
        window_start = now - 60.0

        self._request_timestamps[user_id] = [
            ts for ts in self._request_timestamps[user_id] if ts > window_start
        ]

        if len(self._request_timestamps[user_id]) >= self.max_rpm:
            return False, (
                f"Rate limit exceeded: {self.max_rpm} requests per minute. "
                f"Please try again later."
            )

        self._request_timestamps[user_id].append(now)
        return True, ""

    def process_run(
        self,
        runner: Runner,
        message: types.Content,
        **kwargs: Any,
    ) -> Callable[[Callable[[], AsyncGenerator]], Callable[[], AsyncGenerator]]:

        def decorator(event_generator_func):
            async def wrapper():
                user_id = kwargs.get("user_id", "anonymous")

                allowed, error_msg = self._check_rate_limit(user_id)
                if not allowed:
                    from google.genai import types as genai_types
                    yield genai_types.Content(
                        role="model",
                        parts=[genai_types.Part(text=error_msg)],
                    )
                    return

                async with self._concurrent_semaphore:
                    async for event in event_generator_func():
                        yield event

            return wrapper
        return decorator
```

### 模板3：事件过滤/转换Processor

```python
from __future__ import annotations
import re
from typing import Any, AsyncGenerator, Callable, TYPE_CHECKING

from veadk.processors.base_run_processor import BaseRunProcessor

if TYPE_CHECKING:
    from google.genai import types
    from veadk.runner import Runner


class ContentFilterProcessor(BaseRunProcessor):
    """内容过滤Processor。

    检测并过滤敏感内容，或对输出内容进行后处理。
    """

    def __init__(
        self,
        blocked_patterns: list[str] | None = None,
        replacement: str = "[内容已过滤]",
    ):
        super().__init__()
        self.patterns = [re.compile(p, re.IGNORECASE) for p in (blocked_patterns or [])]
        self.replacement = replacement

    def _filter_text(self, text: str) -> str:
        for pattern in self.patterns:
            text = pattern.sub(self.replacement, text)
        return text

    def process_run(
        self,
        runner: Runner,
        message: types.Content,
        **kwargs: Any,
    ) -> Callable[[Callable[[], AsyncGenerator]], Callable[[], AsyncGenerator]]:

        def decorator(event_generator_func):
            async def wrapper():
                async for event in event_generator_func():
                    if hasattr(event, "content") and event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                part.text = self._filter_text(part.text)
                    yield event

            return wrapper
        return decorator
```

### 模板4：可注入自定义事件的Processor

参考AuthRequestProcessor的模式，可以在事件流中注入自定义事件：

```python
from __future__ import annotations
from typing import Any, AsyncGenerator, Callable, TYPE_CHECKING

from google.genai import types
from veadk.processors.base_run_processor import BaseRunProcessor

if TYPE_CHECKING:
    from veadk.runner import Runner


class AuditEventProcessor(BaseRunProcessor):
    """审计事件注入Processor。

    在对话开始和结束时注入审计标记事件。
    """

    def __init__(self, audit_callback: Callable | None = None):
        super().__init__()
        self.audit_callback = audit_callback

    def process_run(
        self,
        runner: Runner,
        message: types.Content,
        **kwargs: Any,
    ) -> Callable[[Callable[[], AsyncGenerator]], Callable[[], AsyncGenerator]]:

        def decorator(event_generator_func):
            async def wrapper():
                session_id = kwargs.get("session_id", "unknown")
                user_id = kwargs.get("user_id", "unknown")

                # 注入开始标记（自定义事件）
                if self.audit_callback:
                    await self._call_audit("run_started", {
                        "session_id": session_id,
                        "user_id": user_id,
                    })

                try:
                    async for event in event_generator_func():
                        yield event
                finally:
                    if self.audit_callback:
                        await self._call_audit("run_completed", {
                            "session_id": session_id,
                            "user_id": user_id,
                        })

            return wrapper
        return decorator

    async def _call_audit(self, event_type: str, data: dict):
        if self.audit_callback:
            import asyncio
            if asyncio.iscoroutinefunction(self.audit_callback):
                await self.audit_callback(event_type, data)
            else:
                self.audit_callback(event_type, data)
```

---

## 六、多个RunProcessor的执行顺序

### 当前实现

当前VeADK的Runner只支持**单个**RunProcessor（通过三级优先级链选择一个），不支持多个Processor链式组合。

参考：[runner.py:406-414](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L240)

### 组合多个Processor的方法

如果需要组合多个横切关注点，可以创建一个**复合Processor**来手动组合多个处理器：

```python
from __future__ import annotations
from typing import Any, AsyncGenerator, Callable, TYPE_CHECKING

from veadk.processors.base_run_processor import BaseRunProcessor

if TYPE_CHECKING:
    from google.genai import types
    from veadk.runner import Runner


class CompositeRunProcessor(BaseRunProcessor):
    """组合多个RunProcessor，按添加顺序执行（洋葱模型）。"""

    def __init__(self, processors: list[BaseRunProcessor] | None = None):
        super().__init__()
        self.processors = processors or []

    def add(self, processor: BaseRunProcessor) -> CompositeRunProcessor:
        self.processors.append(processor)
        return self

    def process_run(
        self,
        runner: Runner,
        message: types.Content,
        **kwargs: Any,
    ) -> Callable[[Callable[[], AsyncGenerator]], Callable[[], AsyncGenerator]]:

        def decorator(event_generator_func):
            current_func = event_generator_func

            for processor in reversed(self.processors):
                current_decorator = processor.process_run(runner, message, **kwargs)
                current_func = current_decorator(current_func)

            return current_func
        return decorator


# 使用示例
composite = CompositeRunProcessor([
    LoggingProcessor(log_events=True),
    RateLimitProcessor(max_requests_per_minute=60),
    ContentFilterProcessor(blocked_patterns=[r"badword"]),
])

runner = Runner(agent=agent, app_name="my_app", run_processor=composite)
```

**执行顺序**（洋葱模型）：
```
请求 → Logging前处理 → RateLimit检查 → ContentFilter → Agent执行
       ← Logging后处理 ←                  ← ContentFilter ←
```

---

## 七、开发注意事项

### 1. 必须正确转发所有事件

在wrapper中务必使用 `async for event in event_generator_func(): yield event` 转发所有事件，遗漏 `yield` 会导致事件丢失：

```python
# ✅ 正确：转发所有事件
async for event in event_generator_func():
    yield event

# ❌ 错误：事件被吞掉
async for event in event_generator_func():
    pass  # 没有yield！
```

参考：[架构洞察8 - 使用建议](file:///d:/AI/.agents/docs/knowledge/learning/veadk-python/supporting-analysis/11-architecture-insights.md#L255-L259)

### 2. 异步非阻塞

Processor内避免同步阻塞操作，使用 `asyncio.to_thread()` 包装同步IO：

```python
import asyncio

def blocking_io():
    import time
    time.sleep(1)
    return "result"

async def wrapper():
    result = await asyncio.to_thread(blocking_io)
    async for event in event_generator_func():
        yield event
```

### 3. 异常处理与资源清理

如果在Processor中替换了runner的方法（如AuthRequestProcessor替换 `run_async`），务必在 `finally` 块中恢复：

```python
original_run_async = runner.run_async
runner.run_async = wrapped_run_async
try:
    async for chunk in event_generator_func():
        yield chunk
finally:
    runner.run_async = original_run_async  # 一定要恢复！
```

参考：[AuthRequestProcessor:359-368](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_identity/auth_processor.py#L359-L368)

### 4. 事件注入格式

注入自定义事件时，需符合ADK Event/Content格式规范。参考AuthRequestProcessor构造认证响应的方式：

```python
from google.genai import types

auth_content = types.Content(
    role="user",
    parts=[
        types.Part(
            function_response=types.FunctionResponse(
                id=auth_request_event_id,
                name="adk_request_credential",
                response=auth_config.model_dump(),
            )
        )
    ],
)
```

参考：[AuthRequestProcessor:255-266](file:///d:/AI/.chaos/libs/veadk-python/veadk/integrations/ve_identity/auth_processor.py#L255-L266)

### 5. kwargs透传

`process_run` 的 `**kwargs` 可能包含 `task_updater`、`session_id`、`user_id` 等上下文信息，注意传递给内部调用。

---

## 八、使用场景示例

### 场景1：单次运行临时启用Processor

```python
result = await runner.run(
    messages="请分析这份敏感数据",
    run_processor=AuditEventProcessor(audit_callback=log_to_db),
)
```

### 场景2：开发调试时使用LoggingProcessor

```python
if os.getenv("DEBUG"):
    processor = LoggingProcessor(log_events=True)
else:
    processor = NoOpRunProcessor()

runner = Runner(agent=agent, app_name="my_app", run_processor=processor)
```

### 场景3：多租户场景使用RateLimitProcessor

```python
processor = CompositeRunProcessor([
    AuthRequestProcessor(),
    RateLimitProcessor(
        max_requests_per_minute=int(os.getenv("RATE_LIMIT_RPM", "30")),
    ),
    LoggingProcessor(),
])
```
