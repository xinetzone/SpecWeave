"""OpenAI 兼容协议适配器（``openai_compat``）。

调用契约（该契约来自文档证据）：
- 方法与路径：``POST {base_url}/chat/completions``
- 请求头：``Authorization: Bearer <key>``、``Content-Type: application/json``
- 请求体：``{"model", "messages", "temperature"?, "max_tokens"?, "stream"?}``
- 响应取值：``choices[0].message.content``、``usage.prompt_tokens`` /
  ``usage.completion_tokens``、``id``、``model``、``choices[0].finish_reason``

实现约定（本实现的合理默认）：
- ``base_url`` 的尾斜杠统一裁剪后再拼接路径，模型 id 逐字使用，不做别名替换；
- ``ChatRequest.extra`` 作为 OpenAI 兼容扩展字段原样透传；
- 非 2xx 一律抛 :class:`UpstreamError`，429 与 5xx 标 ``retryable=True``；
- 错误消息一律经 ``redact()`` 脱敏，禁止明文 Key 外泄。
"""

from ..errors import UpstreamError
from ..logging_utils import get_logger, redact
from ..models.catalog import ProviderProtocol
from .base import ChatRequest, ChatResponse, ProviderAdapter, UsageInfo
from .transport import HttpRequest, HttpResponse

logger = get_logger("providers.openai_compat")

#: 该契约来自文档证据：OpenAI 兼容端点固定路径
CHAT_COMPLETIONS_PATH = "/chat/completions"

#: 本实现的合理默认：错误摘要截断长度，避免超长上游报文进入异常消息
_DETAIL_LIMIT = 200


def _normalize_base_url(base_url: str) -> str:
    """裁剪 ``base_url`` 的尾斜杠（本实现的合理默认，目录里 base_url 可能带 ``/``）。"""
    return base_url.rstrip("/")


def _error_detail(data: dict, text: str) -> str:
    """抽取上游错误摘要：兼容 ``{"error": {"message": ...}}``、``{"error": "..."}`` 与纯文本。"""
    error = data.get("error")
    if isinstance(error, dict):
        detail = str(error.get("message") or error.get("type") or error.get("code") or "")
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


class OpenAICompatAdapter(ProviderAdapter):
    """OpenAI 兼容协议适配器。"""

    protocol: ProviderProtocol = ProviderProtocol.OPENAI_COMPAT

    def build_request(
        self,
        request: ChatRequest,
        *,
        base_url: str,
        model: str,
        api_key: str,
    ) -> HttpRequest:
        messages: list[dict] = []
        for message in request.messages:
            item: dict = {"role": message.role, "content": message.content}
            if message.name:  # 本实现的合理默认：OpenAI 协议支持消息级 name
                item["name"] = message.name
            messages.append(item)
        body: dict = {"model": model, "messages": messages}
        if request.temperature is not None:
            body["temperature"] = request.temperature
        if request.max_tokens is not None:
            body["max_tokens"] = request.max_tokens
        if request.stream:
            body["stream"] = True
        if request.extra:  # 本实现的合理默认：extra 作为兼容字段透传，避免静默丢弃
            body.update(request.extra)
        return HttpRequest(
            method="POST",
            url=f"{_normalize_base_url(base_url)}{CHAT_COMPLETIONS_PATH}",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json_body=body,
        )

    def parse_response(self, response: HttpResponse, *, provider_id: str) -> ChatResponse:
        data = _ensure_success(response, provider_id=provider_id)
        choices = data.get("choices") or []
        first = choices[0] if choices else {}
        message = first.get("message") or {}
        usage = data.get("usage") or {}
        return ChatResponse(
            id=str(data.get("id") or ""),
            model=str(data.get("model") or ""),
            provider_id=provider_id,
            content=str(message.get("content") or ""),
            role=str(message.get("role") or "assistant"),
            finish_reason=str(first.get("finish_reason") or "stop"),
            usage=UsageInfo(
                prompt_tokens=int(usage.get("prompt_tokens") or 0),
                completion_tokens=int(usage.get("completion_tokens") or 0),
            ),
            created=int(data.get("created") or 0),
        )
