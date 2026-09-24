"""限速 HTTP 客户端的退避/重试行为测试（无真实网络）。"""

import httpx
import pytest

from mp_archiver.config import Settings
from mp_archiver.http_client import RateLimitedClient


def _settings(**overrides) -> Settings:
    # 禁用 .env 读取，保证测试确定性
    return Settings(_env_file=None, request_delay_min=0.0, request_delay_max=0.0, **overrides)


def _client(handler, **overrides):
    """构造客户端：时钟大步前进使请求节奏不触发睡眠，仅保留退避睡眠可观测。"""
    sleeps: list[float] = []
    tick = {"t": 0.0}

    def clock() -> float:
        tick["t"] += 100.0
        return tick["t"]

    client = RateLimitedClient(
        _settings(**overrides),
        transport=httpx.MockTransport(handler),
        sleeper=sleeps.append,
        clock=clock,
        rng=lambda a, b: 0.0,  # 无随机抖动，退避值确定
    )
    return client, sleeps


def test_retries_503_with_exponential_backoff():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(503) if len(calls) < 3 else httpx.Response(200, text="ok")

    client, sleeps = _client(handler, backoff_base=2.0, backoff_cap=60.0, max_retries=5)
    response = client.get("http://test.local/a")

    assert response.status_code == 200
    assert response.text == "ok"
    assert len(calls) == 3
    assert sleeps == [2.0, 4.0]  # base*2^0, base*2^1


def test_retries_on_timeout_then_succeeds():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) <= 2:
            raise httpx.ReadTimeout("simulated slow response")
        return httpx.Response(200)

    client, sleeps = _client(handler, max_retries=3)
    response = client.get("http://test.local/b")

    assert response.status_code == 200
    assert len(calls) == 3
    assert len(sleeps) == 2


def test_403_retried_until_budget_exhausted():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(403, json={"err": "blocked"})

    client, sleeps = _client(handler, max_retries=2)
    response = client.get("http://test.local/c")

    assert response.status_code == 403
    assert len(calls) == 3  # 首次 + 2 次重试
    assert len(sleeps) == 2


def test_401_not_retried():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(401)

    client, sleeps = _client(handler, max_retries=4)
    response = client.get("http://test.local/d")

    assert response.status_code == 401
    assert len(calls) == 1
    assert sleeps == []


def test_backoff_respects_cap():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client, sleeps = _client(
        handler, max_retries=10, backoff_base=2.0, backoff_cap=8.0
    )
    response = client.get("http://test.local/e")

    assert response.status_code == 500
    assert max(sleeps) == 8.0 + 0.0


def test_timeout_persisted_raises():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    client, _ = _client(handler, max_retries=1)
    with pytest.raises(httpx.ConnectError):
        client.get("http://test.local/f")
