"""三协议厂商适配器契约测试。

用 ``MockTransport`` 录制请求快照，逐项断言方法 / URL 路径 / 请求头 / 查询参数，
并覆盖响应归一化、错误码可重试标记与 Key 脱敏。测试中的 Key 一律使用
``sk-test-xxx`` 这类明显占位值。
"""

import logging

import pytest

from inurl_byok_token_hub.errors import ErrorCode, UpstreamError
from inurl_byok_token_hub.logging_utils import redact
from inurl_byok_token_hub.models.catalog import ProviderProtocol
from inurl_byok_token_hub.providers import (
    ChatMessage,
    ChatRequest,
    HttpResponse,
    MockTransport,
    get_adapter,
)
from inurl_byok_token_hub.providers.anthropic import AnthropicAdapter
from inurl_byok_token_hub.providers.gemini import GeminiAdapter
from inurl_byok_token_hub.providers.openai_compat import OpenAICompatAdapter

FAKE_KEY = "sk-test-xxx"


def _chat_request(**kwargs) -> ChatRequest:
    """构造通用请求：system + user + assistant 三条消息。"""
    base = {
        "model": "unit-test-model",
        "messages": (
            ChatMessage(role="system", content="你是助手"),
            ChatMessage(role="user", content="你好"),
            ChatMessage(role="assistant", content="在的"),
            ChatMessage(role="user", content="继续"),
        ),
        "temperature": 0.7,
        "max_tokens": 256,
    }
    base.update(kwargs)
    return ChatRequest(**base)


def _roundtrip(adapter, request: ChatRequest, *, base_url: str, model: str, response):
    """经 MockTransport 发送并解析，返回 (解析结果, 录制到的请求)。"""
    transport = MockTransport([response])
    built = adapter.build_request(request, base_url=base_url, model=model, api_key=FAKE_KEY)
    http_response = transport.send(built)
    parsed = adapter.parse_response(http_response, provider_id="unit-provider")
    return parsed, transport.last_request()


# --------------------------------------------------------------------------- #
# OpenAI 兼容
# --------------------------------------------------------------------------- #


def test_openai_compat_request_contract():
    adapter = get_adapter(ProviderProtocol.OPENAI_COMPAT)
    request = adapter.build_request(
        _chat_request(),
        base_url="https://api.example.com/v1/",
        model="gpt-4o-mini",
        api_key=FAKE_KEY,
    )
    assert request.method == "POST"
    assert request.url == "https://api.example.com/v1/chat/completions"
    assert request.headers["Authorization"] == f"Bearer {FAKE_KEY}"
    assert request.headers["Content-Type"] == "application/json"
    assert request.params == {}
    assert request.json_body["model"] == "gpt-4o-mini"
    assert request.json_body["temperature"] == 0.7
    assert request.json_body["max_tokens"] == 256
    assert request.json_body["messages"][0] == {"role": "system", "content": "你是助手"}
    assert "stream" not in request.json_body


def test_openai_compat_parse_response():
    adapter = get_adapter(ProviderProtocol.OPENAI_COMPAT)
    body = {
        "id": "chatcmpl-1",
        "model": "gpt-4o-mini",
        "created": 1730000000,
        "choices": [
            {"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "嗨"}}
        ],
        "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
    }
    parsed, recorded = _roundtrip(
        adapter,
        _chat_request(),
        base_url="https://api.example.com/v1",
        model="gpt-4o-mini",
        response=HttpResponse(status_code=200, json_body=body),
    )
    assert recorded.url.endswith("/chat/completions")
    assert parsed.provider_id == "unit-provider"
    assert parsed.id == "chatcmpl-1"
    assert parsed.model == "gpt-4o-mini"
    assert parsed.content == "嗨"
    assert parsed.role == "assistant"
    assert parsed.finish_reason == "stop"
    assert parsed.usage.prompt_tokens == 11
    assert parsed.usage.completion_tokens == 7
    assert parsed.usage.total_tokens == 18
    assert parsed.created == 1730000000


# --------------------------------------------------------------------------- #
# Anthropic
# --------------------------------------------------------------------------- #


def test_anthropic_request_contract():
    adapter = get_adapter(ProviderProtocol.ANTHROPIC)
    request = adapter.build_request(
        _chat_request(),
        base_url="https://api.anthropic.com/",
        model="claude-3-5-sonnet-latest",
        api_key=FAKE_KEY,
    )
    assert request.method == "POST"
    assert request.url == "https://api.anthropic.com/v1/messages"
    assert request.headers["x-api-key"] == FAKE_KEY
    assert request.headers["anthropic-version"] == "2023-06-01"
    assert request.headers["Content-Type"] == "application/json"
    assert request.json_body["model"] == "claude-3-5-sonnet-latest"
    assert request.json_body["max_tokens"] == 256
    assert request.json_body["system"] == "你是助手"
    roles = [m["role"] for m in request.json_body["messages"]]
    assert roles == ["user", "assistant", "user"]
    assert "system" not in roles


def test_anthropic_default_max_tokens():
    adapter = get_adapter(ProviderProtocol.ANTHROPIC)
    request = adapter.build_request(
        _chat_request(max_tokens=None),
        base_url="https://api.anthropic.com",
        model="claude-test",
        api_key=FAKE_KEY,
    )
    assert request.json_body["max_tokens"] == 1024


def test_anthropic_parse_response():
    adapter = get_adapter(ProviderProtocol.ANTHROPIC)
    body = {
        "id": "msg_01",
        "model": "claude-3-5-sonnet-latest",
        "role": "assistant",
        "stop_reason": "end_turn",
        "content": [{"type": "text", "text": "你好呀"}],
        "usage": {"input_tokens": 9, "output_tokens": 5},
    }
    parsed, _ = _roundtrip(
        adapter,
        _chat_request(),
        base_url="https://api.anthropic.com",
        model="claude-3-5-sonnet-latest",
        response=HttpResponse(status_code=200, json_body=body),
    )
    assert parsed.id == "msg_01"
    assert parsed.content == "你好呀"
    assert parsed.finish_reason == "end_turn"
    assert parsed.usage.prompt_tokens == 9
    assert parsed.usage.completion_tokens == 5


def test_anthropic_tools_rejected():
    adapter = get_adapter(ProviderProtocol.ANTHROPIC)
    with pytest.raises(UpstreamError) as excinfo:
        adapter.build_request(
            _chat_request(extra={"tools": [{"name": "search"}]}),
            base_url="https://api.anthropic.com",
            model="claude-test",
            api_key=FAKE_KEY,
        )
    assert excinfo.value.error_code is ErrorCode.UNSUPPORTED_FEATURE
    assert excinfo.value.retryable is False
    assert "sk-test-xxx" not in str(excinfo.value)


def test_anthropic_unsupported_role_rejected():
    adapter = get_adapter(ProviderProtocol.ANTHROPIC)
    request = ChatRequest(
        model="claude-test",
        messages=(ChatMessage(role="tool", content="{}"),),
    )
    with pytest.raises(UpstreamError) as excinfo:
        adapter.build_request(
            request,
            base_url="https://api.anthropic.com",
            model="claude-test",
            api_key=FAKE_KEY,
        )
    assert excinfo.value.error_code is ErrorCode.UNSUPPORTED_FEATURE


# --------------------------------------------------------------------------- #
# Gemini
# --------------------------------------------------------------------------- #


def test_gemini_request_contract():
    adapter = get_adapter(ProviderProtocol.GEMINI)
    request = adapter.build_request(
        _chat_request(),
        base_url="https://generativelanguage.googleapis.com/",
        model="gemini-2.0-flash",
        api_key=FAKE_KEY,
    )
    assert request.method == "POST"
    assert request.url == (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    )
    assert request.params == {"key": FAKE_KEY}
    assert "Authorization" not in request.headers
    assert "x-api-key" not in request.headers
    assert request.headers["Content-Type"] == "application/json"
    assert request.json_body["contents"] == [
        {"role": "user", "parts": [{"text": "你好"}]},
        {"role": "model", "parts": [{"text": "在的"}]},
        {"role": "user", "parts": [{"text": "继续"}]},
    ]
    assert request.json_body["systemInstruction"] == {"parts": [{"text": "你是助手"}]}
    assert request.json_body["generationConfig"] == {
        "temperature": 0.7,
        "maxOutputTokens": 256,
    }


def test_gemini_parse_response():
    adapter = get_adapter(ProviderProtocol.GEMINI)
    body = {
        "candidates": [
            {
                "content": {"role": "model", "parts": [{"text": "收到"}]},
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {"promptTokenCount": 13, "candidatesTokenCount": 4},
        "modelVersion": "gemini-2.0-flash",
    }
    parsed, recorded = _roundtrip(
        adapter,
        _chat_request(),
        base_url="https://generativelanguage.googleapis.com",
        model="gemini-2.0-flash",
        response=HttpResponse(status_code=200, json_body=body),
    )
    assert recorded.params == {"key": FAKE_KEY}
    assert parsed.content == "收到"
    assert parsed.model == "gemini-2.0-flash"
    assert parsed.finish_reason == "stop"
    assert parsed.usage.prompt_tokens == 13
    assert parsed.usage.completion_tokens == 4


def test_gemini_key_never_logged(caplog):
    adapter = get_adapter(ProviderProtocol.GEMINI)
    with caplog.at_level(logging.DEBUG, logger="inurl_byok_token_hub.providers.gemini"):
        adapter.build_request(
            _chat_request(),
            base_url="https://generativelanguage.googleapis.com",
            model="gemini-2.0-flash",
            api_key=FAKE_KEY,
        )
    assert FAKE_KEY not in caplog.text
    assert "[REDACTED]" in caplog.text


def test_gemini_unsupported_extra_rejected():
    adapter = get_adapter(ProviderProtocol.GEMINI)
    with pytest.raises(UpstreamError) as excinfo:
        adapter.build_request(
            _chat_request(extra={"tools": [{}]}),
            base_url="https://generativelanguage.googleapis.com",
            model="gemini-2.0-flash",
            api_key=FAKE_KEY,
        )
    assert excinfo.value.error_code is ErrorCode.UNSUPPORTED_FEATURE


# --------------------------------------------------------------------------- #
# 错误路径与脱敏
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("status_code", [429, 503])
@pytest.mark.parametrize(
    "protocol",
    [ProviderProtocol.OPENAI_COMPAT, ProviderProtocol.ANTHROPIC, ProviderProtocol.GEMINI],
)
def test_retryable_statuses(protocol, status_code):
    adapter = get_adapter(protocol)
    body = {"error": {"message": "rate limited"}}
    with pytest.raises(UpstreamError) as excinfo:
        adapter.parse_response(
            HttpResponse(status_code=status_code, json_body=body, text="rate limited"),
            provider_id="unit-provider",
        )
    assert excinfo.value.retryable is True
    assert excinfo.value.status_code == status_code
    assert excinfo.value.provider_id == "unit-provider"


@pytest.mark.parametrize("status_code", [401, 403, 404])
@pytest.mark.parametrize(
    "protocol",
    [ProviderProtocol.OPENAI_COMPAT, ProviderProtocol.ANTHROPIC, ProviderProtocol.GEMINI],
)
def test_non_retryable_statuses(protocol, status_code):
    adapter = get_adapter(protocol)
    # 上游把 Key 回显在错误报文里，适配器必须脱敏后才写入异常消息
    body = {"error": {"message": f"invalid credential ?key={FAKE_KEY}"}}
    with pytest.raises(UpstreamError) as excinfo:
        adapter.parse_response(
            HttpResponse(status_code=status_code, json_body=body),
            provider_id="unit-provider",
        )
    assert excinfo.value.retryable is False
    # Key 不得出现在任何异常消息中
    assert FAKE_KEY not in str(excinfo.value)
    assert "[REDACTED]" in str(excinfo.value)
    assert redact(str(excinfo.value)) == str(excinfo.value)


# --------------------------------------------------------------------------- #
# 工厂
# --------------------------------------------------------------------------- #


def test_get_adapter_types():
    assert isinstance(get_adapter(ProviderProtocol.OPENAI_COMPAT), OpenAICompatAdapter)
    assert isinstance(get_adapter(ProviderProtocol.ANTHROPIC), AnthropicAdapter)
    assert isinstance(get_adapter(ProviderProtocol.GEMINI), GeminiAdapter)
    assert get_adapter(ProviderProtocol.OPENAI_COMPAT).protocol is (ProviderProtocol.OPENAI_COMPAT)
