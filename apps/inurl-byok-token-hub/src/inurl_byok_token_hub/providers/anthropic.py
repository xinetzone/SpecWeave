"""Anthropic 原生协议适配器（``anthropic``）。

调用契约（该契约来自文档证据）：
- 方法与路径：``POST {base_url}/v1/messages``
- 请求头：``x-api-key: <key>``、``anthropic-version: 2023-06-01``、
  ``Content-Type: application/json``
- 请求体：``system``（由 ``role=system`` 的消息提取）+ ``messages``（role 只允许
  ``user`` / ``assistant``）+ ``max_tokens``（缺失时默认 1024）+ ``model``
- 响应取值：``content[0].text``、``usage.input_tokens`` / ``usage.output_tokens``、
  ``id``、``model``、``stop_reason``

实现约定（本实现的合理默认）：
- **不支持的字段不得静默丢弃**：``tools`` 等无法映射到 Anthropic 协议的字段，
  以及 ``system`` / ``user`` / ``assistant`` 之外的 role，一律抛
  :class:`UpstreamError`（``ErrorCode.UNSUPPORTED_FEATURE``，``retryable=False``）；
- 多条 system 消息以空行拼接为单个 ``system`` 字段。
"""

from ..errors import ErrorCode, UpstreamError
from ..logging_utils import get_logger, redact
from ..models.catalog import ProviderProtocol
from .base import ChatRequest, ChatResponse, ProviderAdapter, UsageInfo
from .transport import HttpRequest, HttpResponse

logger = get_logger("providers.anthropic")

#: 该契约来自文档证据：Anthropic 要求固定版本头
ANTHROPIC_VERSION = "2023-06-01"

#: 该契约来自文档证据：Anthropic 强制必填 max_tokens，未指定时取 1024
DEFAULT_MAX_TOKENS = 1024

#: 该契约来自文档证据：messages 数组只允许 user/assistant
_ALLOWED_ROLES = ("user", "assistant")

_DETAIL_LIMIT = 200


def _normalize_base_url(base_url: str) -> str:
    """裁剪 ``base_url`` 的尾斜杠（本实现的合理默认）。"""
    return base_url.rstrip("/")


def _unsupported(keys: object) -> UpstreamError:
    """构造「特性不支持」错误（该契约来自文档证据：不得静默丢弃不支持字段）。

    基类会按状态码推断错误码，此处需显式改回 ``UNSUPPORTED_FEATURE``（422）。
    """
    error = UpstreamError(
        f"Anthropic 协议暂不支持该字段：{keys}",
        status_code=ErrorCode.UNSUPPORTED_FEATURE.http_status,
        retryable=False,
    )
    error.error_code = ErrorCode.UNSUPPORTED_FEATURE
    return error


def _error_detail(data: dict, text: str) -> str:
    """抽取上游错误摘要：兼容 ``{"error": {...}}`` 与纯文本响应。"""
    error = data.get("error")
    if isinstance(error, dict):
        detail = str(error.get("message") or error.get("type") or "")
    elif isinstance(error, str):
        detail = error
    else:
        detail = text
    return detail.strip()[:_DETAIL_LIMIT]


def _ensure_success(response: HttpResponse, *, provider_id: str) -> dict:
    """状态码闸门：非 2xx 抛 :class:`UpstreamError`，2xx 返回 JSON 体。"""
    status = response.status_code
    data = response.json_body or {}
    if 200 <= status < 300:
        return data
    # 该契约来自文档证据：429/5xx 可重试并触发故障切换，401/403/404 属不可重试
    retryable = status == 429 or 500 <= status < 600
    detail = _error_detail(data, response.text)
    message = redact(f"上游返回 HTTP {status}：{detail}") if detail else f"上游返回 HTTP {status}"
    logger.warning(
        "上游调用失败 provider=%s status=%s retryable=%s", provider_id, status, retryable
    )
    raise UpstreamError(
        message,
        status_code=status,
        provider_id=provider_id,
        retryable=retryable,
    )


class AnthropicAdapter(ProviderAdapter):
    """Anthropic 原生协议适配器。"""

    protocol: ProviderProtocol = ProviderProtocol.ANTHROPIC

    def build_request(
        self,
        request: ChatRequest,
        *,
        base_url: str,
        model: str,
        api_key: str,
    ) -> HttpRequest:
        if request.extra:
            raise _unsupported(sorted(request.extra))
        system_parts: list[str] = []
        messages: list[dict] = []
        for message in request.messages:
            if message.role == "system":
                system_parts.append(message.content)
                continue
            if message.role not in _ALLOWED_ROLES:
                # 该契约来自文档证据：无法映射的字段不得静默丢弃
                raise _unsupported(f"role={message.role}")
            messages.append({"role": message.role, "content": message.content})
        body: dict = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or DEFAULT_MAX_TOKENS,
        }
        if system_parts:  # 该契约来自文档证据：system 独立成顶层字段
            body["system"] = "\n\n".join(system_parts)
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.stream:
            body["stream"] = True
        return HttpRequest(
            method="POST",
            url=f"{_normalize_base_url(base_url)}/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "Content-Type": "application/json",
            },
            json_body=body,
        )

    def parse_response(self, response: HttpResponse, *, provider_id: str) -> ChatResponse:
        data = _ensure_success(response, provider_id=provider_id)
        blocks = data.get("content") or []
        first = blocks[0] if blocks else {}
        usage = data.get("usage") or {}
        return ChatResponse(
            id=str(data.get("id") or ""),
            model=str(data.get("model") or ""),
            provider_id=provider_id,
            content=str(first.get("text") or ""),
            role="assistant",
            finish_reason=str(data.get("stop_reason") or "stop"),
            usage=UsageInfo(
                prompt_tokens=int(usage.get("input_tokens") or 0),
                completion_tokens=int(usage.get("output_tokens") or 0),
            ),
        )
