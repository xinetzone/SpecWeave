"""云服务通道与 HTTP 客户端策略的回归测试。

这三组测试守的是**上线才会爆**的缺陷：

1. 代理泄漏：httpx 默认信任 ``HTTP_PROXY``，导致回环请求被代理转发，
   request-target 变成绝对 URI，真实 uvicorn 服务器下全部 ``/api/*`` 404；
   而进程内 TestClient 完全测不出来。
2. 云端鉴权头：publishableKey 放错头会被判为「仅 publishableKey」而拒绝。
3. 流式聚合：云端只支持 ``stream: true``，非流式输入在发出请求前就被拒绝。
"""

import json

import httpx
import pytest

from info_butler.config import LLMOverride, Settings
from info_butler.http_client import http_client, is_loopback_host, trust_env_for
from info_butler.llm import LLMClient, LLMError

# -- 代理策略 ---------------------------------------------------------------


@pytest.mark.parametrize(
    "host",
    ["localhost", "127.0.0.1", "127.0.0.53", "::1", "LOCALHOST"],
)
def test_loopback_hosts_are_detected(host):
    assert is_loopback_host(host) is True


@pytest.mark.parametrize("host", ["example.com", "api.deepseek.com", "10.0.0.1", ""])
def test_public_hosts_are_not_loopback(host):
    assert is_loopback_host(host) is False


def test_loopback_url_disables_env_proxy():
    """回环地址必须禁用环境代理，否则真实服务器上会 404。"""
    assert trust_env_for("http://127.0.0.1:8787/api/health") is False
    assert trust_env_for("http://localhost:8787/api/health") is False


def test_public_url_keeps_env_proxy():
    """公网地址必须尊重环境代理——企业网里这是访问外网的唯一通路。"""
    assert trust_env_for("https://api.deepseek.com/v1/chat/completions") is True


def test_http_client_applies_policy():
    """工厂必须真的把策略落到 httpx.Client 上，而不只是算出来。"""
    with http_client("http://127.0.0.1:8787/x", 1.0) as client:
        assert client.trust_env is False
    with http_client("https://example.com/x", 1.0) as client:
        assert client.trust_env is True


def test_loopback_request_survives_proxy_env(monkeypatch):
    """端到端守护：即使环境里有代理，回环请求也必须直达。

    这是本组测试里最重要的一条——它复刻了「CI runner 配了 HTTP_PROXY，
    部署后服务全 404」的真实事故。用真实 socket 服务器而非 MockTransport，
    因为 MockTransport 绕过传输层，根本触发不了代理路径。
    """
    import socket
    import threading

    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:9")

    received: list[str] = []

    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def serve():
        conn, _ = server.accept()
        data = conn.recv(4096)
        received.append(data.split(b"\r\n")[0].decode())
        conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
        conn.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    try:
        with http_client(f"http://127.0.0.1:{port}/api/health", 5.0) as client:
            response = client.get(f"http://127.0.0.1:{port}/api/health")
    finally:
        thread.join(timeout=5)
        server.close()

    assert response.status_code == 200
    # 代理会把 request-target 改成绝对 URI（甚至百分号编码），直达则是 origin 形式
    assert received[0] == "GET /api/health HTTP/1.1"


# -- 云端存储与通道的配置 ---------------------------------------------------


def test_wb_cloud_requires_both_endpoint_and_key():
    assert Settings(wb_cloud_endpoint="https://x.app.workbuddy.host").wb_cloud_ready is False
    assert Settings(wb_publishable_key="pk").wb_cloud_ready is False
    assert (
        Settings(
            wb_cloud_endpoint="https://x.app.workbuddy.host", wb_publishable_key="pk"
        ).wb_cloud_ready
        is True
    )


def test_wb_llm_requires_cloud_env_and_model():
    assert Settings(wb_llm_model="m").wb_llm_ready is False
    assert (
        Settings(
            wb_cloud_endpoint="https://x.app.workbuddy.host",
            wb_publishable_key="pk",
            wb_llm_model="m",
        ).wb_llm_ready
        is True
    )


def test_storage_backend_labels():
    assert Settings().storage_backend == "memory"
    assert Settings(supabase_url="https://x", supabase_key="k").storage_backend == "supabase"
    assert (
        Settings(
            wb_cloud_endpoint="https://x", wb_publishable_key="pk"
        ).storage_backend
        == "workbuddy-cloud"
    )


def test_workbuddy_cloud_wins_over_supabase():
    """平台环境优先：平台注入的变量不该被本机残留的 Supabase 变量截胡。"""
    from info_butler.store import WorkBuddyCloudStore, create_store

    settings = Settings(
        wb_cloud_endpoint="https://x.app.workbuddy.host",
        wb_publishable_key="pk",
        supabase_url="https://y.supabase.co",
        supabase_key="sk",
    )
    assert isinstance(create_store(settings), WorkBuddyCloudStore)


def test_workbuddy_cloud_uses_correct_data_plane_path():
    """数据面路径必须是 /.cloud/database/rest/<table>，不是 /rest/v1/。"""
    from info_butler.store import WorkBuddyCloudStore

    settings = Settings(
        wb_cloud_endpoint="https://x.app.workbuddy.host/", wb_publishable_key="pk"
    )
    store = WorkBuddyCloudStore(settings)
    assert store._base == "https://x.app.workbuddy.host/.cloud/database/rest"


def test_workbuddy_cloud_auth_header_is_not_bearer():
    """publishableKey 只能放 x-wb-webapp-access-key，不能当 Bearer 用。"""
    from info_butler.store import WorkBuddyCloudStore

    settings = Settings(
        wb_cloud_endpoint="https://x.app.workbuddy.host", wb_publishable_key="pk-test"
    )
    headers = WorkBuddyCloudStore(settings)._headers
    assert headers["x-wb-webapp-access-key"] == "pk-test"
    assert "Authorization" not in headers


# -- 云端通道的 LLM 行为 ----------------------------------------------------


def _sse(*frames: dict) -> bytes:
    """把若干帧编码成 SSE 响应体。"""
    lines = []
    for frame in frames:
        lines.append(f"data: {json.dumps(frame, ensure_ascii=False)}\n\n")
    lines.append("data: [DONE]\n\n")
    return "".join(lines).encode("utf-8")


def _cloud_settings() -> Settings:
    return Settings(
        wb_cloud_endpoint="https://x.app.workbuddy.host",
        wb_publishable_key="pk",
        wb_llm_model="test-model",
    )


def test_cloud_channel_is_used_when_no_byok():
    client = LLMClient(_cloud_settings())
    assert client.available() is True
    assert client._use_cloud_channel(None) is True


def test_byok_overrides_cloud_channel():
    """页面 BYOK 优先级最高：填了就该走用户自己的端点。"""
    client = LLMClient(_cloud_settings())
    override = LLMOverride(base_url="https://mine/v1", api_key="sk", model="my-model")
    assert client._use_cloud_channel(override) is False
    assert client.available(override) is True


def test_cloud_chat_aggregates_sse_chunks(monkeypatch):
    """流式通道：多帧 content 要拼成完整文本，role 帧与 [DONE] 要被跳过。"""
    client = LLMClient(_cloud_settings())
    body = _sse(
        {"choices": [{"delta": {"role": "assistant", "content": ""}}]},
        {"choices": [{"delta": {"content": "定价"}}]},
        {"choices": [{"delta": {"content": "方案"}}]},
        {"choices": [{"delta": {}, "finish_reason": "stop"}]},
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/.cloud/llm/chat/completions"
        payload = json.loads(request.content)
        assert payload["stream"] is True, "云端通道只支持流式"
        assert payload["messages"][0]["role"] == "system"
        assert request.headers["x-wb-webapp-access-key"] == "pk"
        return httpx.Response(200, content=body, headers={"Content-Type": "text/event-stream"})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr("info_butler.llm.http_client", _mock_client_factory(transport))

    assert client.chat("你是助手", "写标题") == "定价方案"


def test_cloud_chat_json_parses_aggregated_json(monkeypatch):
    """JSON 模式：云端返回的 JSON 文本要被解析成 dict。"""
    client = LLMClient(_cloud_settings())
    body = _sse(
        {"choices": [{"delta": {"content": '{"kind": "todo"}'}}]},
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body, headers={"Content-Type": "text/event-stream"})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr("info_butler.llm.http_client", _mock_client_factory(transport))

    assert client.chat_json("你是助手", "判定类型") == {"kind": "todo"}


def test_cloud_chat_raises_on_empty_stream(monkeypatch):
    """空响应必须是失败而不是空字符串——否则下游会写入空白条目。"""
    client = LLMClient(_cloud_settings())
    body = _sse({"choices": [{"delta": {"role": "assistant", "content": ""}}]})

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body, headers={"Content-Type": "text/event-stream"})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr("info_butler.llm.http_client", _mock_client_factory(transport))

    with pytest.raises(LLMError):
        client.chat("你是助手", "写标题")


def test_cloud_chat_surfaces_stream_error(monkeypatch):
    """流内错误帧必须抛出，而不是被静默吞掉。"""
    client = LLMClient(_cloud_settings())
    body = _sse({"error": {"message": "quota exceeded", "code": "quota_exceeded"}})

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body, headers={"Content-Type": "text/event-stream"})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr("info_butler.llm.http_client", _mock_client_factory(transport))

    with pytest.raises(LLMError, match="quota exceeded"):
        client.chat("你是助手", "写标题")


def test_cloud_probe_reports_ok(monkeypatch):
    client = LLMClient(_cloud_settings())
    body = _sse({"choices": [{"delta": {"content": "pong"}}]})

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=body, headers={"Content-Type": "text/event-stream"})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr("info_butler.llm.http_client", _mock_client_factory(transport))

    result = client.probe()
    assert result["ok"] is True
    assert result["model"] == "test-model"


def _mock_client_factory(transport: httpx.MockTransport):
    """构造一个忽略 URL、只走 MockTransport 的 http_client 替身。"""

    def factory(url: str, timeout: float) -> httpx.Client:
        return httpx.Client(timeout=timeout, transport=transport, trust_env=False)

    return factory


# -- 诊断字段 ---------------------------------------------------------------


def test_health_reports_storage_backend_and_llm_source():
    """健康检查必须说清「数据存在哪、模型走哪条路」——发布后只有它能诊断。"""
    from fastapi.testclient import TestClient

    from info_butler.api import create_app
    from info_butler.store import MemoryStore

    settings = Settings(
        wb_cloud_endpoint="https://x.app.workbuddy.host",
        wb_publishable_key="pk",
        wb_llm_model="m",
    )
    app = create_app(settings=settings, store=MemoryStore(), llm=LLMClient(settings))
    with TestClient(app) as client:
        body = client.get("/api/health").json()

    # 存储状态以**实际生效的 store 实例**为准——这里注入的是 MemoryStore，
    # 所以即便配置里有云服务变量，也应如实显示 memory。
    assert body["storage"] == "memory"
    assert body["storage_backend"] == "memory"
    # 大模型则看配置：云端通道已就绪
    assert body["llm_ready"] is True
    assert body["llm_source"] == "cloud"


def test_health_reports_real_store_backend():
    """未注入 store 时（走 create_store 自动装配），backend 应反映真实实现。"""
    from fastapi.testclient import TestClient

    from info_butler.api import create_app

    settings = Settings(
        wb_cloud_endpoint="https://x.app.workbuddy.host", wb_publishable_key="pk"
    )
    app = create_app(settings=settings)
    with TestClient(app) as client:
        body = client.get("/api/health").json()

    assert body["storage"] == "cloud"
    assert body["storage_backend"] == "workbuddy-cloud"


def test_health_reports_byok_source_when_overridden():
    """页面填了 BYOK 就该显示 byok——状态徽标不能说谎。"""
    from fastapi.testclient import TestClient

    from info_butler.api import create_app
    from info_butler.store import MemoryStore

    settings = Settings()
    app = create_app(settings=settings, store=MemoryStore(), llm=LLMClient(settings))
    with TestClient(app) as client:
        body = client.get(
            "/api/health", headers={"X-LLM-Api-Key": "sk", "X-LLM-Base-Url": "https://x/v1"}
        ).json()

    assert body["llm_source"] == "byok"
    assert body["llm_ready"] is True
