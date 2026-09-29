"""``providers`` 包出口：厂商协议适配器与传输层抽象的统一入口。

只导出本列表中的符号；协议实现（``openai_compat`` / ``anthropic`` / ``gemini``）
通过 :func:`get_adapter` 按 :class:`ProviderProtocol` 获取。
"""

from .base import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ProviderAdapter,
    UsageInfo,
    get_adapter,
)
from .transport import (
    HttpRequest,
    HttpResponse,
    HttpxTransport,
    MockTransport,
    Transport,
)

__all__ = [
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "HttpRequest",
    "HttpResponse",
    "HttpxTransport",
    "MockTransport",
    "ProviderAdapter",
    "Transport",
    "UsageInfo",
    "get_adapter",
]
