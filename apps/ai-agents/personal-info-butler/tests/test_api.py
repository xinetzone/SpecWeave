"""API 契约测试。

覆盖三件事：路由与状态码、鉴权开关、**云端存储故障要变成 503 而不是 500**。
最后一条最容易被漏：StoreError 若未捕获，用户看到的是"服务器内部错误"，
而真相是"数据库连不上"——两者对应的处置完全不同。
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from info_butler import llm as llm_mod
from info_butler.api import create_app
from info_butler.config import Settings
from info_butler.llm import LLMClient
from info_butler.store import MemoryStore, StoreError


class BrokenStore(MemoryStore):
    """模拟云端存储不可达。"""

    def list_items(self, **kwargs):
        raise StoreError("云端存储不可达")


def build(app_token: str = "", store=None):
    settings = Settings(app_token=app_token)
    store = store if store is not None else MemoryStore()
    app = create_app(settings=settings, store=store, llm=LLMClient(settings))
    return TestClient(app), store


def test_root_reports_service_shape():
    client, _ = build()
    body = client.get("/").json()
    assert body["service"] == "info-butler"
    assert body["storage"] == "memory"
    assert body["llm_ready"] is False


def test_health_reports_degraded_state():
    client, _ = build()
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["auth_required"] is False
    assert body["storage"] == "memory"


# -- 大模型卡片：BYOK 探针 ----------------------------------------------------
# 探针回答的是「我填的对不对」。填错凭据是用户输入错误，不是服务端故障，
# 所以它必须走 200 + 响应体 reason，而不是 4xx/5xx——后者会让页面只能
# 显示"服务器出错"，用户也就无从下手。


class _FakeResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text


class _FakeProvider:
    """假 provider：只回应状态码，不真的发请求。"""

    def __init__(self, status_code: int = 200, exc: Exception | None = None):
        self.status_code = status_code
        self._exc = exc
        self.calls: list[dict] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def post(self, url, json=None, headers=None):
        self.calls.append({"url": url, "json": json, "headers": headers})
        if self._exc is not None:
            raise self._exc
        return _FakeResponse(self.status_code)


def _patch_provider(monkeypatch, status_code: int = 200, exc: Exception | None = None) -> _FakeProvider:
    fake = _FakeProvider(status_code, exc)
    monkeypatch.setattr(llm_mod.httpx, "Client", lambda *args, **kwargs: fake)
    return fake


BYOK = {
    "X-LLM-Base-Url": "https://api.deepseek.com/v1",
    "X-LLM-Api-Key": "sk-page",
    "X-LLM-Model": "deepseek-chat",
}


def test_llm_probe_without_credentials_reports_missing_key():
    client, _ = build()
    body = client.post("/api/llm/test").json()
    assert body["ok"] is False
    assert "API Key" in body["reason"]


def test_llm_probe_confirms_credentials_and_stays_cheap(monkeypatch):
    fake = _patch_provider(monkeypatch, 200)
    client, _ = build()
    body = client.post("/api/llm/test", headers=BYOK).json()

    assert body == {"ok": True, "model": "deepseek-chat", "reason": ""}
    # 探针必须便宜：一次调用、一个 token
    assert len(fake.calls) == 1
    assert fake.calls[0]["json"]["max_tokens"] == 1
    # 凭据只发给用户填的那个地址，不能落到别处
    assert fake.calls[0]["url"] == "https://api.deepseek.com/v1/chat/completions"
    assert fake.calls[0]["headers"]["Authorization"] == "Bearer sk-page"


def test_llm_probe_attributes_invalid_key(monkeypatch):
    _patch_provider(monkeypatch, 401)
    client, _ = build()
    body = client.post("/api/llm/test", headers=BYOK).json()
    assert body["ok"] is False
    assert "401" in body["reason"]


def test_llm_probe_attributes_wrong_model(monkeypatch):
    _patch_provider(monkeypatch, 404)
    client, _ = build()
    body = client.post("/api/llm/test", headers=BYOK).json()
    assert body["ok"] is False
    assert "404" in body["reason"]


def test_llm_probe_attributes_unreachable_endpoint(monkeypatch):
    _patch_provider(monkeypatch, exc=httpx.ConnectError("boom"))
    client, _ = build()
    body = client.post("/api/llm/test", headers=BYOK).json()
    assert body["ok"] is False
    assert "连不上" in body["reason"]


def test_llm_probe_never_signals_failure_via_status_code(monkeypatch):
    """验证结论在响应体里，HTTP 层必须是 200。"""
    _patch_provider(monkeypatch, 403)
    client, _ = build()
    assert client.post("/api/llm/test", headers=BYOK).status_code == 200


def test_llm_test_requires_token_when_configured():
    """探针会真实发起模型调用，不鉴权就等于给公网开一个免费代理。"""
    client, _ = build(app_token="t")
    assert client.post("/api/llm/test", headers=BYOK).status_code == 401


def test_health_counts_byok_as_ready():
    """页面填了 BYOK，状态徽标就不能再说「模型：未接入」。"""
    client, _ = build()
    assert client.get("/api/health").json()["llm_ready"] is False

    body = client.get("/api/health", headers=BYOK).json()
    assert body["llm_ready"] is True
    assert body["llm_source"] == "byok"


def test_health_distinguishes_server_and_byok():
    """两条运维路径不同，状态里必须说清模型来自哪。"""
    settings = Settings(llm_api_key="sk-server")
    app = create_app(settings=settings, store=MemoryStore(), llm=LLMClient(settings))
    client = TestClient(app)

    assert client.get("/api/health").json()["llm_source"] == "server"
    assert client.get("/api/health", headers=BYOK).json()["llm_source"] == "byok"


def test_create_item_returns_201_with_enrichment():
    client, _ = build()
    response = client.post("/api/items", json={"content": "记得明天把定价方案发给客户"})
    assert response.status_code == 201
    body = response.json()
    assert body["item"]["kind"] == "todo"
    assert body["todos"], "待办内容必须派生待办"


def test_create_item_rejects_empty_content():
    client, _ = build()
    assert client.post("/api/items", json={"content": ""}).status_code == 422


def test_list_and_search_items():
    client, _ = build()
    client.post("/api/items", json={"content": "定价方案需要重新评估"})
    client.post("/api/items", json={"content": "周末去爬山"})
    assert client.get("/api/items").json()["count"] == 2

    body = client.get("/api/items?q=定价").json()
    assert body["count"] >= 1
    assert body["items"][0]["title"]


def test_filter_by_kind():
    client, _ = build()
    client.post("/api/items", json={"content": "一个关于协同效率的念头"})
    client.post("/api/items", json={"content": "记得明天交方案"})
    body = client.get("/api/items?kind=todo").json()
    # 待办类内容除自身外还会派生一条待办条目，故此处是 2 条
    assert body["count"] == 2
    assert all(row["kind"] == "todo" for row in body["items"])

    idea_only = client.get("/api/items?kind=idea").json()
    assert idea_only["count"] == 1


def test_get_item_missing_returns_404():
    client, _ = build()
    assert client.get("/api/items/nope").status_code == 404


def test_patch_and_delete_item():
    client, _ = build()
    item_id = client.post("/api/items", json={"content": "一条想法"}).json()["item"]["id"]
    assert client.patch("/api/items/" + item_id, json={"status": "done"}).json()["status"] == "done"
    assert client.delete("/api/items/" + item_id).json()["deleted"] is True
    assert client.get("/api/items/" + item_id).status_code == 404


def test_patch_missing_returns_404():
    client, _ = build()
    assert client.patch("/api/items/nope", json={"status": "done"}).status_code == 404


def test_links_endpoint_returns_list():
    client, _ = build()
    item_id = client.post("/api/items", json={"content": "定价方案需要重新评估"}).json()["item"]["id"]
    body = client.get(f"/api/items/{item_id}/links").json()
    assert body["count"] == 0


def test_ask_returns_answer_and_citations():
    client, _ = build()
    client.post("/api/items", json={"content": "定价方案需要重新评估"})
    body = client.post("/api/ask", json={"question": "定价"}).json()
    assert body["answer"]
    assert isinstance(body["citations"], list)


def test_ask_rejects_empty_question():
    client, _ = build()
    assert client.post("/api/ask", json={"question": ""}).status_code == 422


def test_extract_returns_markdown():
    client, _ = build()
    client.post("/api/items", json={"content": "一条记录"})
    body = client.post("/api/extract", json={"limit": 20, "scope": "recent"}).json()
    assert body["markdown"]
    assert body["source"] in {"heuristic", "llm", "none", "error"}


def test_todos_endpoint():
    client, _ = build()
    client.post("/api/items", json={"content": "记得明天交方案"})
    body = client.get("/api/todos").json()
    assert body["count"] >= 1


def test_summary_generate_and_history():
    client, _ = build()
    client.post("/api/items", json={"content": "一条记录"})
    created = client.post("/api/summary", json={"days": 7, "limit": 50}).json()
    assert created["markdown"]
    assert client.get("/api/summary").json()["count"] == 1


def test_tags_endpoint():
    client, _ = build()
    client.post("/api/items", json={"content": "定价方案需要重新评估"})
    body = client.get("/api/tags").json()
    assert body["total"] == 1
    assert body["tags"]


def test_byok_headers_are_accepted():
    """BYOK 头只做透传；即使带了 Key，未走模型的接口也必须照常返回。"""
    client, _ = build()
    response = client.get(
        "/api/items",
        headers={"X-LLM-Base-Url": "https://example.invalid/v1", "X-LLM-Api-Key": "sk-test", "X-LLM-Model": "m"},
    )
    assert response.status_code == 200


def test_token_required_when_configured():
    client, _ = build(app_token="secret")
    assert client.get("/api/items").status_code == 401
    assert client.get("/api/items", headers={"X-App-Token": "secret"}).status_code == 200


def test_token_accepts_bearer_form():
    client, _ = build(app_token="secret")
    assert client.get("/api/items", headers={"Authorization": "Bearer secret"}).status_code == 200


def test_wrong_token_rejected():
    client, _ = build(app_token="secret")
    assert client.get("/api/items", headers={"X-App-Token": "wrong"}).status_code == 401


def test_health_requires_token_when_configured():
    """健康检查也要过鉴权——否则等于给公网留一个永久可用的探针。"""
    client, _ = build(app_token="secret")
    assert client.get("/api/health").status_code == 401


def test_storage_failure_becomes_503():
    client, _ = build(store=BrokenStore())
    response = client.get("/api/items")
    assert response.status_code == 503
    assert "云端存储" in response.json()["detail"]


def test_storage_failure_on_summary_becomes_503():
    client, _ = build(store=BrokenStore())
    assert client.post("/api/summary", json={"days": 7}).status_code == 503


@pytest.mark.parametrize("path", ["/api/items", "/api/tags", "/api/todos"])
def test_unknown_storage_error_is_never_500(path):
    client, _ = build(store=BrokenStore())
    assert client.get(path).status_code == 503
