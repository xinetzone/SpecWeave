"""厂商调用契约：统一的内部请求/响应表示与 ``ProviderAdapter`` 协议。

分层约束：``providers`` 只依赖 ``models`` / ``errors`` / ``config``，
不得依赖 ``services`` 或 ``api``。
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..models.catalog import ProviderProtocol

if TYPE_CHECKING:
    from .transport import HttpRequest, HttpResponse


@dataclass(frozen=True)
class ChatMessage:
    role: str  # system | user | assistant | tool
    content: str
    name: str | None = None


@dataclass(frozen=True)
class ChatRequest:
    """归一化聊天请求。"""

    model: str
    messages: tuple[ChatMessage, ...] = ()
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False
    extra: dict = field(default_factory=dict)


@dataclass(frozen=True)
class UsageInfo:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class ChatResponse:
    """归一化聊天响应（三种协议统一为此结构）。"""

    id: str = ""
    model: str = ""
    provider_id: str = ""
    content: str = ""
    role: str = "assistant"
    finish_reason: str = "stop"
    usage: UsageInfo = UsageInfo()
    created: int = 0


class ProviderAdapter:
    """厂商协议适配器基类。

    子类实现 :meth:`build_request` 与 :meth:`parse_response`；
    请求/响应一律走 ``transport`` 抽象，便于以 mock 完成零密钥验证。
    """

    protocol: ProviderProtocol = ProviderProtocol.OPENAI_COMPAT

    def build_request(
        self,
        request: ChatRequest,
        *,
        base_url: str,
        model: str,
        api_key: str,
    ) -> HttpRequest:
        raise NotImplementedError

    def parse_response(self, response: HttpResponse, *, provider_id: str) -> ChatResponse:
        raise NotImplementedError


def get_adapter(protocol: ProviderProtocol) -> ProviderAdapter:
    """按协议返回适配器实例。"""
    from .anthropic import AnthropicAdapter
    from .gemini import GeminiAdapter
    from .openai_compat import OpenAICompatAdapter

    registry: dict[ProviderProtocol, type[ProviderAdapter]] = {
        ProviderProtocol.OPENAI_COMPAT: OpenAICompatAdapter,
        ProviderProtocol.ANTHROPIC: AnthropicAdapter,
        ProviderProtocol.GEMINI: GeminiAdapter,
    }
    return registry[protocol]()
