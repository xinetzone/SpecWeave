"""大模型调用层测试：凭据缺失、超时、传输错误、HTTP 错误、响应格式异常。

用可控的假客户端替换 httpx.AsyncClient，覆盖全部失败路径——
这些路径决定了线上能否如实降级，而不是把故障伪装成「知识库里没答案」。

刻意不引入 pytest-asyncio：llm.chat 是唯一的异步入口，
用 run() 同步驱动即可，少一个测试期依赖。
"""

import asyncio
from typing import Any

import httpx
import pytest

from okfqa import config, llm


def run(coro) -> Any:
    """在同步测试中驱动协程。"""
    return asyncio.run(coro)


class _FakeResponse:
    def __init__(self, status_code: int, payload=None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


class _FakeClient:
    """替换 httpx.AsyncClient：返回预设响应或抛出预设异常。"""

    def __init__(self, response=None, exc=None) -> None:
        self._response = response
        self._exc = exc
        self.calls: list[dict] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args) -> bool:
        return False

    async def post(self, url, json=None, headers=None):
        self.calls.append({"url": url, "json": json, "headers": headers})
        if self._exc is not None:
            raise self._exc
        return self._response

    @property
    def last_call(self) -> dict:
        return self.calls[-1]


@pytest.fixture
def fake_client(monkeypatch):
    """注入假客户端的工厂；同时预置凭据，使调用走到真实请求分支。"""

    def install(response=None, exc=None):
        client = _FakeClient(response=response, exc=exc)
        monkeypatch.setattr(llm.httpx, "AsyncClient", lambda *a, **kw: client)
        return client

    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    return install


def _ok(content: str) -> _FakeResponse:
    return _FakeResponse(200, {"choices": [{"message": {"content": content}}]})


# ---------------------------------------------------------------- 凭据与端点


def test_chat_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(llm.LLMError, match="未配置 LLM_API_KEY"):
        run(llm.chat("sys", "user"))


def test_endpoint_trims_trailing_slash(monkeypatch) -> None:
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com/v1/")
    assert llm._endpoint() == "https://api.example.com/v1/chat/completions"


# ---------------------------------------------------------------- 成功路径


def test_chat_returns_content(fake_client) -> None:
    client = fake_client(_ok("  答案内容  "))
    result = run(llm.chat("系统提示", "用户问题"))

    assert result == "答案内容"
    call = client.last_call
    assert call["url"].endswith("/chat/completions")
    assert call["headers"]["Authorization"] == "Bearer sk-test"
    assert call["json"]["model"] == "test-model"
    assert call["json"]["messages"][0]["role"] == "system"
    assert call["json"]["messages"][1]["content"] == "用户问题"


# ---------------------------------------------------------------- 失败路径


def test_chat_wraps_timeout(fake_client) -> None:
    fake_client(exc=httpx.TimeoutException("boom"))
    with pytest.raises(llm.LLMError, match="超时"):
        run(llm.chat("sys", "user"))


def test_chat_wraps_transport_error(fake_client) -> None:
    fake_client(exc=httpx.ConnectError("refused"))
    with pytest.raises(llm.LLMError, match="请求失败"):
        run(llm.chat("sys", "user"))


@pytest.mark.parametrize("status", [400, 401, 429, 500, 503])
def test_chat_wraps_http_errors(fake_client, status) -> None:
    fake_client(_FakeResponse(status, text="upstream boom"))
    with pytest.raises(llm.LLMError, match=f"HTTP {status}"):
        run(llm.chat("sys", "user"))


@pytest.mark.parametrize(
    "payload",
    [
        {},                                  # 缺 choices
        {"choices": []},                     # 空 choices
        {"choices": [{"message": {}}]},      # 缺 content
        {"choices": [{"no_message": 1}]},    # 结构不符
    ],
)
def test_chat_rejects_malformed_payload(fake_client, payload) -> None:
    fake_client(_FakeResponse(200, payload))
    with pytest.raises(llm.LLMError, match="响应格式异常"):
        run(llm.chat("sys", "user"))


def test_chat_rejects_non_json_body(fake_client) -> None:
    fake_client(_FakeResponse(200, payload=None, text="<html>502</html>"))
    with pytest.raises(llm.LLMError, match="响应格式异常"):
        run(llm.chat("sys", "user"))


def test_default_timeout_is_under_vercel_limit() -> None:
    """LLM 超时必须小于 vercel.json 的 maxDuration(60s)，否则降级分支永远不触发。"""
    assert config.llm_timeout() < 60
