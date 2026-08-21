---
id: custom-extension
title: 自定义Extension开发指南
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 自定义Extension开发指南

本文档介绍 VeADK 中 Extension（扩展）的概念和开发方法。VeADK 提供两种 Extension 模式：渠道扩展（Channel Extension）和插件扩展（Plugin Extension）。

---

## 一、Extension 是什么

VeADK 的 Extension 是框架级扩展点，用于将 VeADK Agent 与外部系统集成。与工具（Tool）扩展 Agent 能力不同，Extension 扩展的是 Agent 的运行环境和接入方式。

### Extension vs Tool 对比

| 维度 | Tool（工具） | Extension（扩展） |
|---|---|---|
| 作用范围 | Agent 单次执行中的能力调用 | Agent 运行环境/接入方式的整体扩展 |
| 调用方 | LLM 自主决定何时调用 | 框架层/外部系统触发 |
| 典型场景 | 搜索、计算、API调用 | 消息渠道接入、插件装配、运行时增强 |
| 基类 | `BaseTool` / 函数 | 无强制基类，遵循约定模式 |
| 注册方式 | `Agent(tools=[...])` | 直接实例化使用 / `Runner(plugins=[...])` |

### 两种 Extension 模式

VeADK 现有两类 Extension 实现：

| 模式 | 参考实现 | 用途 |
|---|---|---|
| **Channel Extension** | [FeishuChannelExtension](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/feishu_channel.py#L269-L780) | 将外部消息渠道（飞书、钉钉等）桥接到 VeADK Runner |
| **Plugin Extension** | [HarnessExtension](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/harness/extension.py#L57-L120) | 通过 Google ADK Plugin 机制扩展 Runner 能力 |

---

## 二、Channel Extension（渠道扩展）开发

Channel Extension 用于将外部消息渠道（IM 平台、Webhook、消息队列等）接入 VeADK。它作为外部渠道和 Runner 之间的桥接层。

### 核心职责

1. **连接管理**：建立与外部渠道的连接（WebSocket、Webhook、长轮询等）
2. **消息接收**：监听外部渠道的消息事件
3. **上下文映射**：将外部渠道的用户ID、会话ID映射为 VeADK 的 user_id/session_id
4. **调用 Runner**：使用 Runner 执行对话
5. **响应回传**：将 Agent 响应发送回外部渠道

### FeishuChannelExtension 架构分析

[FeishuChannelExtension](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/feishu_channel.py#L269-L780) 是渠道扩展的参考实现，其核心结构如下：

```python
class FeishuChannelExtension:
    def __init__(
        self,
        runner: "Runner",                    # VeADK Runner实例
        *,
        app_id: str | None = None,           # 渠道凭证
        app_secret: str | None = None,
        session_id_factory: SessionIdFactory | None = None,  # 会话ID映射策略
        user_id_factory: UserIdFactory | None = None,        # 用户ID映射策略
        message_handler: MessageHandler | None = None,       # 自定义消息处理
        streaming: bool = False,             # 是否流式响应
        reactions: bool = False,             # 是否发送表情反馈
        ...
    ):
        ...

    async def connect(self) -> Any: ...      # 启动连接
    async def disconnect(self) -> Any: ...   # 断开连接
    async def _on_message(self, message): ... # 消息处理回调
    def build_message_context(self, message, text=None) -> FeishuMessageContext: ...
```

### Channel Extension 开发步骤

#### 步骤1：定义消息上下文数据类

```python
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class MyChannelMessageContext:
    """渠道消息上下文，包含消息ID、用户ID、会话ID等映射信息。"""
    message_id: str
    chat_id: str
    user_id: str        # VeADK user_id
    session_id: str     # VeADK session_id
    raw_message: Any    # 原始消息对象
    text: str           # 提取出的文本内容
```

参考：[FeishuMessageContext](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/feishu_channel.py#L251-L263)

#### 步骤2：实现渠道扩展类

```python
from __future__ import annotations
import asyncio
import os
from typing import Any, Awaitable, Callable

from veadk.utils.logger import get_logger

if TYPE_CHECKING:
    from veadk.runner import Runner

logger = get_logger(__name__)

MessageHandler = Callable[[MyChannelMessageContext], Awaitable[str | None] | str | None]
SessionIdFactory = Callable[[Any], str]
UserIdFactory = Callable[[Any], str]


class MyChannelExtension:
    """自定义消息渠道扩展，桥接到VeADK Runner。"""

    def __init__(
        self,
        runner: "Runner",
        *,
        api_key: str | None = None,
        channel: Any | None = None,
        session_id_factory: SessionIdFactory | None = None,
        user_id_factory: UserIdFactory | None = None,
        message_handler: MessageHandler | None = None,
        streaming: bool = False,
        ignore_empty_messages: bool = True,
    ) -> None:
        self.runner = runner
        self.session_id_factory = session_id_factory or self.default_session_id_factory
        self.user_id_factory = user_id_factory or self.default_user_id_factory
        self.message_handler = message_handler
        self.streaming = streaming
        self.ignore_empty_messages = ignore_empty_messages
        self._api_key = api_key or os.getenv("MY_CHANNEL_API_KEY")

        if channel is not None:
            self.channel = channel
        else:
            self.channel = self._build_channel(api_key=self._api_key)

        self.channel.on("message", self._on_message)

    @staticmethod
    def default_user_id_factory(message: Any) -> str:
        """默认用户ID映射策略：从消息中提取发送者ID。"""
        user_id = getattr(message, "sender_id", None) or getattr(message, "user_id", None)
        if user_id:
            return str(user_id)
        raise ValueError("Cannot resolve sender identity into user_id.")

    @staticmethod
    def default_session_id_factory(message: Any) -> str:
        """默认会话ID映射策略：使用chat_id或conversation_id。"""
        return str(
            getattr(message, "thread_id", None)
            or getattr(message, "conversation_id", None)
            or getattr(message, "chat_id", None)
            or getattr(message, "message_id", "")
        )

    async def connect(self) -> Any:
        """启动渠道连接。"""
        connect = getattr(self.channel, "start", None) or self.channel.connect
        if asyncio.iscoroutinefunction(connect):
            return await connect()
        return await asyncio.to_thread(connect)

    async def disconnect(self) -> Any:
        """断开渠道连接。"""
        disconnect = getattr(self.channel, "stop", None) or getattr(self.channel, "disconnect", None)
        if disconnect is None:
            return None
        if asyncio.iscoroutinefunction(disconnect):
            return await disconnect()
        return await asyncio.to_thread(disconnect)

    async def _on_message(self, message: Any) -> None:
        """消息回调：接收渠道消息，调用Runner，回传响应。"""
        text = self._extract_text(message).strip()

        if self.ignore_empty_messages and not text:
            return

        context = self.build_message_context(message=message, text=text)
        send_options = {}

        if self.message_handler is not None:
            response_text = await self._maybe_await(self.message_handler(context))
            if not response_text:
                return
            await self._maybe_await(
                self.channel.send(context.chat_id, {"text": str(response_text)}, send_options)
            )
        elif self.streaming and hasattr(self.channel, "stream"):
            await self._handle_streaming(context, send_options)
        else:
            response_text = await self.runner.run(
                messages=context.text,
                user_id=context.user_id,
                session_id=context.session_id,
            )
            if response_text:
                await self._maybe_await(
                    self.channel.send(context.chat_id, {"text": str(response_text)}, send_options)
                )

    async def _handle_streaming(self, context, send_options):
        """处理流式响应。"""
        from google.adk.agents import RunConfig
        from google.adk.agents.run_config import StreamingMode
        from veadk.runner import _convert_messages

        if self.runner.short_term_memory:
            await self.runner.short_term_memory.create_session(
                app_name=self.runner.app_name,
                user_id=context.user_id,
                session_id=context.session_id,
            )

        converted_messages = _convert_messages(
            context.text, self.runner.app_name, context.user_id, context.session_id
        )
        run_config = RunConfig(streaming_mode=StreamingMode.SSE)

        async def stream_to_channel(stream):
            for converted_message in converted_messages:
                async for event in self.runner.run_async(
                    user_id=context.user_id,
                    session_id=context.session_id,
                    new_message=converted_message,
                    run_config=run_config,
                ):
                    if getattr(event, "partial", False) and event.content and event.content.parts:
                        for part in event.content.parts:
                            if not getattr(part, "thought", False) and part.text:
                                await stream.append(part.text)

        await self.channel.stream(
            context.chat_id, {"markdown": stream_to_channel}, send_options
        )

    def build_message_context(self, message: Any, text: str | None = None) -> MyChannelMessageContext:
        """构建消息上下文，映射外部身份到VeADK身份。"""
        user_id = self.user_id_factory(message)
        session_id = self.session_id_factory(message)
        message_id = str(getattr(message, "message_id", None) or getattr(message, "id", ""))
        chat_id = str(getattr(message, "chat_id", None) or "")

        return MyChannelMessageContext(
            message_id=message_id,
            chat_id=chat_id,
            user_id=user_id,
            session_id=session_id,
            raw_message=message,
            text=text if text is not None else self._extract_text(message),
        )

    def _build_channel(self, *, api_key: str | None):
        """构建渠道SDK客户端实例。"""
        if not api_key:
            raise ValueError("Missing API key. Set api_key parameter or MY_CHANNEL_API_KEY env var.")
        from my_channel_sdk import MyChannelClient
        return MyChannelClient(api_key=api_key)

    def _extract_text(self, message: Any) -> str:
        """从渠道消息中提取纯文本内容。"""
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content
        text = getattr(content, "text", None)
        return str(text or "")

    @staticmethod
    async def _maybe_await(value: Any) -> Any:
        if asyncio.iscoroutine(value) or asyncio.isfuture(value):
            return await value
        return value
```

参考：[FeishuChannelExtension 完整实现](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/feishu_channel.py#L269-L780)

#### 步骤3：注册和使用

```python
import asyncio
from veadk import Agent, Runner
from my_extension import MyChannelExtension


async def main():
    agent = Agent(
        name="my_channel_agent",
        instruction="你是一个友好的助手。",
    )
    runner = Runner(agent=agent, app_name="my_channel_app")

    channel = MyChannelExtension(
        runner=runner,
        streaming=True,
    )

    await channel.connect()
    print("Channel connected, waiting for messages...")

    try:
        await asyncio.Event().wait()
    finally:
        await channel.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
```

### Channel Extension 关键设计点

1. **ID映射策略可定制**：通过 `session_id_factory` 和 `user_id_factory` 允许用户自定义ID映射逻辑，参考 [FeishuChannelExtension:342-366](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/feishu_channel.py#L342-L366)
2. **同步/异步自适应**：`_maybe_await` 工具方法自动处理同步和异步的渠道SDK方法
3. **环境变量凭证**：支持从环境变量读取凭证，方便容器化部署
4. **空消息过滤**：`ignore_empty_messages` 选项过滤无文本内容的消息
5. **线程回复支持**：`reply_in_thread` 选项支持在线程/话题中回复
6. **历史上下文收集**：参考飞书实现的 `_collect_reference_context` 可收集话题历史消息作为上下文
7. **流式响应支持**：通过 `streaming` 参数启用流式输出，参考 [FeishuChannelExtension:466-512](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/feishu_channel.py#L466-L512)

---

## 三、Plugin Extension（插件扩展）开发

Plugin Extension 基于 Google ADK 的 Plugin 机制，用于在 Runner 层面增强能力。HarnessExtension 是此类扩展的参考实现。

### HarnessExtension 架构分析

[HarnessExtension](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/harness/extension.py#L57-L120) 是一个轻量级的门面类，它不包含核心逻辑，而是将实际功能委托给内部模块：

```python
class HarnessExtension:
    def __init__(self, *, enabled=True, components=None, profile="default", store=None, ...):
        # 配置解析和存储
        ...

    @classmethod
    def from_env(cls, env=None) -> HarnessExtension:
        """从环境变量创建Extension实例。"""
        ...

    def plugins(self) -> list[BasePlugin]:
        """构建供Runner使用的插件列表。"""
        return build_harness_plugins(...)
```

### Plugin Extension 开发步骤

#### 步骤1：定义Extension配置类

```python
from __future__ import annotations
from pydantic import BaseModel, Field


class MyExtensionConfig(BaseModel):
    """Extension配置模型。"""
    enabled: bool = True
    feature_a: bool = True
    feature_b: bool = False
    custom_param: str = "default_value"
```

参考：[HarnessExtensionConfig](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/harness/extension.py#L43-L55)

#### 步骤2：实现Extension类

```python
from __future__ import annotations
import os
from collections.abc import Iterable, Mapping
from typing import Any

from google.adk.plugins import BasePlugin


class MyExtension:
    """自定义Plugin Extension，通过plugins()方法返回ADK插件列表。"""

    def __init__(
        self,
        *,
        enabled: bool = True,
        features: Iterable[str] | str | None = None,
        custom_config: dict[str, Any] | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        if features is None:
            feature_list = ["feature_a", "feature_b"]
        elif isinstance(features, str):
            feature_list = [item.strip() for item in features.split(",") if item.strip()]
        else:
            feature_list = [str(item).strip() for item in features if str(item).strip()]

        self.config = MyExtensionConfig(
            enabled=enabled,
            custom_param=str(custom_config.get("param", "default")) if custom_config else "default",
        )
        self.custom_config = custom_config or {}
        self.env = dict(env) if env is not None else None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> MyExtension:
        """从环境变量创建实例，方便云端部署。"""
        values = dict(env or os.environ)
        enabled = values.get("MY_EXTENSION_ENABLED", "true").lower() != "false"
        features = values.get("MY_EXTENSION_FEATURES", None)
        return cls(enabled=enabled, features=features, env=values)

    def plugins(self) -> list[BasePlugin]:
        """构建插件列表，传给Runner(plugins=...)。"""
        if self.env is not None:
            return self._build_plugins_from_env(self.env)
        if not self.config.enabled:
            return []
        return self._build_plugins()

    def _build_plugins(self) -> list[BasePlugin]:
        """根据配置构建具体的插件实例。"""
        plugins = []
        # 在此创建自定义BasePlugin子类实例并添加到列表
        # plugins.append(MyCustomPlugin(config=self.config))
        return plugins

    def _build_plugins_from_env(self, env: Mapping[str, str]) -> list[BasePlugin]:
        """从环境变量构建插件。"""
        # 根据环境变量创建插件
        return self._build_plugins()
```

参考：[HarnessExtension](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/harness/extension.py#L57-L120)

#### 步骤3：使用Extension

```python
from veadk import Agent, Runner
from my_extension import MyExtension

agent = Agent(
    name="my_agent",
    instruction="...",
)

my_ext = MyExtension(enabled=True, features=["feature_a"])

runner = Runner(
    agent=agent,
    app_name="my_app",
    plugins=my_ext.plugins(),  # 将插件列表传给Runner
)
```

---

## 四、Extension 生命周期

### Channel Extension 生命周期

```
1. 实例化 (__init__)
   ├─ 解析配置和凭证
   ├─ 构建渠道SDK客户端
   └─ 注册消息回调 (on_message)

2. connect()
   └─ 建立与外部渠道的连接（WebSocket启动、Webhook服务器启动等）

3. 运行中
   ├─ 接收消息 → _on_message()
   ├─ 构建上下文 → build_message_context()
   ├─ 调用Runner → runner.run() / runner.run_async()
   └─ 回传响应 → channel.send() / channel.stream()

4. disconnect()
   └─ 关闭连接，释放资源
```

### Plugin Extension 生命周期

```
1. 实例化 (__init__)
   └─ 解析配置

2. plugins()
   └─ 创建BasePlugin实例列表（Runner初始化时调用）

3. Runner运行中
   └─ Plugin通过ADK的Plugin机制介入执行流程

4. 应用关闭
   └─ Runner负责Plugin的清理
```

---

## 五、现有 Extension 参考

### FeishuChannelExtension（飞书渠道）

**文件**：[veadk/extensions/feishu_channel.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/feishu_channel.py)

**功能特性**：
- 基于 `lark_oapi` SDK 接入飞书机器人
- 支持 WebSocket 和 Webhook 两种连接方式
- 自动提取飞书消息文本（支持文本、富文本、卡片、合并转发等消息类型）
- 支持话题历史收集（thread history）
- 支持流式响应（SSE）
- 支持消息表情反馈（Reactions）
- 支持同步/异步渠道SDK方法自适应
- 灵活的ID映射策略（可自定义session_id_factory/user_id_factory）

**导出位置**：[veadk/extensions/__init__.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/__init__.py#L15-L17)

### HarnessExtension（Harness插件集）

**文件**：[veadk/extensions/harness/extension.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/harness/extension.py)

**功能特性**：
- 支持从环境变量自动配置（`from_env()` 类方法）
- 模块化组件架构（invocation_context、compactor、response_verification）
- 插件按需装配
- 支持自定义存储后端
- 环境变量驱动的启用/禁用

---

## 六、Extension 注册方式

### Channel Extension 注册

Channel Extension 无需框架级注册，直接实例化后调用 `connect()` 即可：

```python
from veadk.extensions import FeishuChannelExtension

channel = FeishuChannelExtension(runner=runner, app_id="...", app_secret="...")
await channel.connect()
```

### Plugin Extension 注册

Plugin Extension 通过 Runner 的 `plugins` 参数注册：

```python
from veadk.extensions.harness.extension import HarnessExtension

harness = HarnessExtension.from_env()
runner = Runner(agent=agent, app_name="my_app", plugins=harness.plugins())
```

### 导出自定义 Extension

如果希望你的 Extension 像 FeishuChannelExtension 一样通过 `veadk.extensions` 包导入，可以在 `veadk/extensions/__init__.py` 中添加导出：

```python
from veadk.extensions.my_channel import MyChannelExtension

__all__ = ["FeishuChannelExtension", "MyChannelExtension"]
```

---

## 七、最佳实践

1. **凭证管理**：遵循"参数 → 工具专属环境变量 → 全局环境变量 → IAM角色"的凭证链模式
2. **日志脱敏**：日志中不要打印API Key、Secret等敏感信息，参考ve_faas.py的正则脱敏模式
3. **异步友好**：所有IO操作使用async/await或asyncio.to_thread包装，避免阻塞事件循环
4. **错误隔离**：消息处理中的异常要捕获并记录日志，不要因单条消息处理失败导致整个渠道断开
5. **资源清理**：在disconnect()中正确关闭连接、释放资源
6. **配置灵活性**：支持环境变量配置，方便容器化部署和云端运行
7. **ID映射可定制**：允许用户通过factory函数自定义user_id和session_id的映射策略
