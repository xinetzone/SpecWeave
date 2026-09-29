"""Gemini 原生协议适配器（``gemini``）。

调用契约（该契约来自文档证据）：
- 方法与路径：``POST {base_url}/v1beta/models/{model}:generateContent``
- **Key 走查询参数** ``?key=<key>``，不放请求头
- 请求体：``contents``（``[{"role", "parts": [{"text"}]}]``）、
  ``generationConfig``（``temperature``? / ``maxOutputTokens``?）、
  ``systemInstruction.parts[0].text``
- role 映射：``user -> user``、``assistant -> model``，``system`` 进
  ``systemInstruction``
- 响应取值：``candidates[0].content.parts[0].text``、
  ``usageMetadata.promptTokenCount`` / ``usageMetadata.candidatesTokenCount``

实现约定（本实现的合理默认）：
- 日志与异常中若出现 ``key=`` 字面量，一律经 ``redact()`` 脱敏；
- 模型 id 逐字使用，不参与 URL 编码；
- 沿用 Anthropic 的严格策略：``extra`` 中无法映射的字段抛
  ``UNSUPPORTED_FEATURE``，不静默丢弃；
- 响应无 ``id`` 字段，取 ``modelVersion`` 作为 ``model``，``id`` 留空。
"""

from ..errors import ErrorCode, UpstreamError
from ..logging_utils import get_logger, redact
from ..models.catalog import ProviderProtocol
from .base import ChatRequest, ChatResponse, ProviderAdapter, UsageInfo
from .transport import HttpRequest, HttpResponse

logger = get_logger("providers.gemini")

#: 该契约来自文档证据：Gemini 使用 ``:generateContent`` 动词式端点
_GENERATE_CONTENT_SUFFIX = ":generateContent"

#: 该契约来自文档证据：Gemini 的 role 与内部 role 不同名（assistant -> model）
_ROLE_MAP = {"user": "user", "assistant": "model"}

_DETAIL_LIMIT = 200


def _normalize_base_url(base_url: str) -> str:
    """裁剪 ``base_url`` 的尾斜杠（本实现的合理默认）。"""
    return base_url.rstrip("/")


def _redacted_url(url: str, params: dict[str, str]) -> str:
    """把查询参数拼回 URL 并脱敏（该契约来自文档证据：Key 走查询参数，日志禁止明文）。"""
    if not params:
        return redact(url)
    query = "&".join(f"{key}={value}" for key, value in params.items())
    joiner = "&" if "?" in url else "?"
    return redact(f"{url}{joiner}{query}")


def _unsupported(keys: object) -> UpstreamError:
    """构造「特性不支持」错误（该契约来自文档证据：不得静默丢弃不支持字段）。"""
    error = UpstreamError(
        f"Gemini 协议暂不支持该字段：{keys}",
        status_code=ErrorCode.UNSUPPORTED_FEATURE.http_status,
        retryable=False,
    )
    error.error_code = ErrorCode.UNSUPPORTED_FEATURE
    return error


def _error_detail(data: dict, text: str) -> str:
    """抽取上游错误摘要：兼容 ``{"error": {"message": ...}}`` 与纯文本响应。"""
    error = data.get("error")
    if isinstance(error, dict):
        detail = str(error.get("message") or error.get("status") or error.get("code") or "")
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


class GeminiAdapter(ProviderAdapter):
    """Gemini 原生协议适配器。"""

    protocol: ProviderProtocol = ProviderProtocol.GEMINI

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
        contents: list[dict] = []
        for message in request.messages:
            if message.role == "system":
                system_parts.append(message.content)
                continue
            if message.role not in _ROLE_MAP:
                # 该契约来自文档证据：无法映射的字段不得静默丢弃
                raise _unsupported(f"role={message.role}")
            contents.append({"role": _ROLE_MAP[message.role], "parts": [{"text": message.content}]})
        body: dict = {"contents": contents}
        if system_parts:  # 该契约来自文档证据：system 指令独立成 systemInstruction
            body["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}
        generation_config: dict = {}
        if request.temperature is not None:
            generation_config["temperature"] = request.temperature
        if request.max_tokens is not None:
            generation_config["maxOutputTokens"] = request.max_tokens
        if generation_config:
            body["generationConfig"] = generation_config
        url = f"{_normalize_base_url(base_url)}/v1beta/models/{model}{_GENERATE_CONTENT_SUFFIX}"
        params = {"key": api_key}
        logger.debug("Gemini 上游目标：%s", _redacted_url(url, params))
        return HttpRequest(
            method="POST",
            url=url,
            headers={"Content-Type": "application/json"},
            params=params,
            json_body=body,
        )

    def parse_response(self, response: HttpResponse, *, provider_id: str) -> ChatResponse:
        data = _ensure_success(response, provider_id=provider_id)
        candidates = data.get("candidates") or []
        first = candidates[0] if candidates else {}
        parts = ((first.get("content") or {}).get("parts")) or []
        usage = data.get("usageMetadata") or {}
        finish_reason = str(first.get("finishReason") or "stop").lower()
        return ChatResponse(
            id=str(data.get("responseId") or ""),
            model=str(data.get("modelVersion") or ""),
            provider_id=provider_id,
            content=str((parts[0] if parts else {}).get("text") or ""),
            # 本实现的合理默认：响应作者统一归一化为 assistant
            role="assistant",
            finish_reason=finish_reason,
            usage=UsageInfo(
                prompt_tokens=int(usage.get("promptTokenCount") or 0),
                completion_tokens=int(usage.get("candidatesTokenCount") or 0),
            ),
        )
