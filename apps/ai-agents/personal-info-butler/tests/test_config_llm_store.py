"""配置 / 大模型客户端 / 云端存储 的单元测试。

这三块都直接面对外部世界（环境变量、HTTP 端点），最容易在"只测了 happy path"的
情况下带着缺陷上线。这里把失败分支逐个钉死：非 2xx、非法 JSON、空 choices、
网络异常、Supabase 只配了一半。
"""

import json

import httpx
import pytest

from info_butler import config as config_mod
from info_butler import llm as llm_mod
from info_butler import store as store_mod
from info_butler.config import LLMOverride, Settings
from info_butler.llm import LLMClient, LLMError
from info_butler.store import MemoryStore, StoreError, SupabaseStore, create_store

# -- 环境变量解析 -------------------------------------------------------------


def test_env_helpers_fall_back_on_garbage(monkeypatch):
    monkeypatch.setenv("T_FLOAT", "not-a-number")
    monkeypatch.setenv("T_INT", "not-an-int")
    assert config_mod._env_float("T_FLOAT", 3.5) == 3.5
    assert config_mod._env_int("T_INT", 7) == 7


def test_env_helpers_read_valid_values(monkeypatch):
    monkeypatch.setenv("T_FLOAT", "2.5")
    monkeypatch.setenv("T_INT", "9")
    assert config_mod._env_float("T_FLOAT", 1.0) == 2.5
    assert config_mod._env_int("T_INT", 1) == 9


def test_env_list_splits_and_trims(monkeypatch):
    monkeypatch.setenv("T_LIST", "https://a.example , https://b.example ,")
    assert config_mod._env_list("T_LIST", "*") == ["https://a.example", "https://b.example"]


def test_env_list_default(monkeypatch):
    monkeypatch.delenv("T_LIST", raising=False)
    assert config_mod._env_list("T_LIST", "*") == ["*"]


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://demo.supabase.co/")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "k")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com/v1/")
    monkeypatch.setenv("LLM_API_KEY", "sk-x")
    monkeypatch.setenv("LLM_MODEL", "m1")
    monkeypatch.setenv("APP_TOKEN", "t")
    settings = Settings.from_env()
    assert settings.supabase_url == "https://demo.supabase.co", "末尾斜杠必须被剥掉"
    assert settings.llm_base_url == "https://api.example.com/v1"
    assert settings.cloud_ready and settings.llm_ready
    assert settings.storage_mode == "cloud"
    assert settings.app_token == "t"


def test_cloud_requires_both_url_and_key():
    assert Settings(supabase_url="https://x.supabase.co").cloud_ready is False
    assert Settings(supabase_key="k").cloud_ready is False
    assert Settings(supabase_url="https://x.supabase.co", supabase_key="k").cloud_ready is True


def test_llm_ready_requires_key_and_base():
    assert Settings(llm_api_key="sk").llm_ready is True
    assert Settings(llm_base_url="").llm_ready is False
    assert Settings().llm_ready is False


def test_storage_mode_label():
    assert Settings().storage_mode == "memory"


def test_byok_only_active_with_key():
    assert LLMOverride(base_url="https://x/v1").active is False
    assert LLMOverride(api_key="sk").active is True


# -- 大模型客户端 --------------------------------------------------------------


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text if text is not None else json.dumps(payload or {})
        self.content = self.text.encode("utf-8")

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


class FakeClient:
    """替身 httpx.Client：按脚本依次返回响应。

    ``trust_env`` 必须能被接受——真实客户端由 :func:`info_butler.http_client.http_client`
    创建，它会按目标地址决定是否信任环境代理（回环必须禁用，否则真实服务器上 404）。
    """

    def __init__(self, timeout=None, trust_env=True, **_kwargs):
        self.timeout = timeout
        self.trust_env = trust_env
        self.calls: list[dict] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def request(self, method, url, headers=None, json=None):
        self.calls.append({"method": method, "url": url, "headers": headers, "json": json})
        return FakeResponse(payload=RESPONSES.pop(0) if RESPONSES else {})

    def post(self, url, json=None, headers=None):
        """LLMClient 用 post；云端存储用 request。两个入口都要接住。"""
        return self.request("POST", url, headers=headers, json=json)


RESPONSES: list = []


def _ok_reply(content):
    return {"choices": [{"message": {"content": content}}]}


def test_chat_returns_content(monkeypatch):
    RESPONSES[:] = [_ok_reply("你好")]
    monkeypatch.setattr(llm_mod.httpx, "Client",FakeClient)
    client = LLMClient(Settings(llm_api_key="sk", llm_base_url="https://api.example.com/v1"))
    assert client.chat("sys", "user") == "你好"


def test_chat_sends_bearer_and_model(monkeypatch):
    RESPONSES[:] = [_ok_reply("x")]
    monkeypatch.setattr(llm_mod.httpx, "Client",FakeClient)
    captured = {}

    class Spy(FakeClient):
        def request(self, method, url, headers=None, json=None):
            captured.update({"url": url, "headers": headers, "json": json})
            return FakeResponse(payload=_ok_reply("x"))

    monkeypatch.setattr(llm_mod.httpx, "Client",Spy)
    LLMClient(Settings(llm_api_key="sk", llm_base_url="https://api.example.com/v1", llm_model="m")).chat("s", "u")
    assert captured["url"].endswith("/chat/completions")
    assert captured["headers"]["Authorization"] == "Bearer sk"
    assert captured["json"]["model"] == "m"


def test_chat_json_mode_sets_response_format(monkeypatch):
    RESPONSES[:] = [_ok_reply("{}")]
    captured = {}

    class Spy(FakeClient):
        def request(self, method, url, headers=None, json=None):
            captured.update({"json": json})
            return FakeResponse(payload=_ok_reply('{"a": 1}'))

    monkeypatch.setattr(llm_mod.httpx, "Client",Spy)
    LLMClient(Settings(llm_api_key="sk")).chat_json("s", "u")
    assert captured["json"]["response_format"] == {"type": "json_object"}


def test_chat_requires_key():
    with pytest.raises(LLMError, match="未配置"):
        LLMClient(Settings()).chat("s", "u")


def test_chat_raises_on_http_error_status(monkeypatch):
    class Err(FakeClient):
        def request(self, *a, **kw):
            return FakeResponse(status_code=401, text="unauthorized")

    monkeypatch.setattr(llm_mod.httpx, "Client",Err)
    with pytest.raises(LLMError, match="401"):
        LLMClient(Settings(llm_api_key="sk")).chat("s", "u")


def test_chat_raises_on_transport_error(monkeypatch):
    class Err(FakeClient):
        def request(self, *a, **kw):
            raise httpx.ConnectError("boom")

    monkeypatch.setattr(llm_mod.httpx, "Client",Err)
    with pytest.raises(LLMError, match="请求失败"):
        LLMClient(Settings(llm_api_key="sk")).chat("s", "u")


def test_chat_raises_on_invalid_json(monkeypatch):
    class Err(FakeClient):
        def request(self, *a, **kw):
            return FakeResponse(payload=None, text="not json")

    monkeypatch.setattr(llm_mod.httpx, "Client",Err)
    with pytest.raises(LLMError, match="不是合法 JSON"):
        LLMClient(Settings(llm_api_key="sk")).chat("s", "u")


def test_chat_raises_on_empty_choices(monkeypatch):
    class Err(FakeClient):
        def request(self, *a, **kw):
            return FakeResponse(payload={"choices": []})

    monkeypatch.setattr(llm_mod.httpx, "Client",Err)
    with pytest.raises(LLMError, match="缺少 choices"):
        LLMClient(Settings(llm_api_key="sk")).chat("s", "u")


def test_chat_raises_on_empty_content(monkeypatch):
    class Err(FakeClient):
        def request(self, *a, **kw):
            return FakeResponse(payload={"choices": [{"message": {"content": ""}}]})

    monkeypatch.setattr(llm_mod.httpx, "Client",Err)
    with pytest.raises(LLMError, match="空内容"):
        LLMClient(Settings(llm_api_key="sk")).chat("s", "u")


def test_chat_json_extracts_object_from_prose(monkeypatch):
    """端点不支持 response_format 时，从散文里挖出 JSON 对象。"""
    # 第一轮：响应本身是合法 JSON，但 content 是散文 → 触发 chat_json 的降级重问
    # 第二轮：content 里夹着一个 JSON 对象 → 从散文中挖出来
    replies = [
        FakeResponse(payload=_ok_reply("好的，结果是：")),
        FakeResponse(payload=_ok_reply('这是说明：{"kind": "idea"}')),
    ]

    class Spy(FakeClient):
        def request(self, *a, **kw):
            return replies.pop(0)

    monkeypatch.setattr(llm_mod.httpx, "Client",Spy)
    result = LLMClient(Settings(llm_api_key="sk")).chat_json("s", "u")
    assert result == {"kind": "idea"}


def test_chat_json_returns_none_when_no_object(monkeypatch):
    class Spy(FakeClient):
        def request(self, *a, **kw):
            return FakeResponse(payload=_ok_reply("抱歉，我无法完成"))

    monkeypatch.setattr(llm_mod.httpx, "Client",Spy)
    assert LLMClient(Settings(llm_api_key="sk")).chat_json("s", "u") is None


def test_byok_overrides_endpoint(monkeypatch):
    captured = {}

    class Spy(FakeClient):
        def request(self, method, url, headers=None, json=None):
            captured.update({"url": url, "headers": headers, "json": json})
            return FakeResponse(payload=_ok_reply("x"))

    monkeypatch.setattr(llm_mod.httpx, "Client",Spy)
    client = LLMClient(Settings(llm_api_key="server", llm_base_url="https://server/v1", llm_model="sm"))
    assert client.available() is True
    client.chat("s", "u", override=LLMOverride(base_url="https://byok/v1", api_key="bk", model="bm"))
    assert captured["url"].startswith("https://byok/v1")
    assert captured["headers"]["Authorization"] == "Bearer bk"
    assert captured["json"]["model"] == "bm"


def test_byok_partial_override_keeps_server_model(monkeypatch):
    captured = {}

    class Spy(FakeClient):
        def request(self, method, url, headers=None, json=None):
            captured.update({"json": json})
            return FakeResponse(payload=_ok_reply("x"))

    monkeypatch.setattr(llm_mod.httpx, "Client",Spy)
    LLMClient(Settings(llm_api_key="server", llm_model="sm")).chat(
        "s", "u", override=LLMOverride(api_key="bk")
    )
    assert captured["json"]["model"] == "sm"


def test_available_false_without_key():
    assert LLMClient(Settings()).available() is False


# -- 云端存储 -----------------------------------------------------------------


def _cloud_store(monkeypatch, responses):
    class Spy(FakeClient):
        def request(self, method, url, headers=None, json=None):
            Spy.seen.append({"method": method, "url": url, "json": json, "headers": headers})
            return responses.pop(0)

    Spy.seen = []
    monkeypatch.setattr(store_mod.httpx, "Client", Spy)
    store = SupabaseStore(
        Settings(supabase_url="https://demo.supabase.co", supabase_key="k")
    )
    return store, Spy.seen


def test_supabase_list_items_builds_query(monkeypatch):
    store, seen = _cloud_store(monkeypatch, [FakeResponse(payload=[{"id": "1"}])])
    rows = store.list_items(kind="todo", tag="定价", status="open", limit=10)
    assert rows == [{"id": "1"}]
    query = seen[0]["url"]
    assert "kind=eq.todo" in query and "status=eq.open" in query
    assert "tags=cs.{定价}" in query and "limit=10" in query
    assert seen[0]["headers"]["apikey"] == "k"


def test_supabase_get_item_missing(monkeypatch):
    store, _ = _cloud_store(monkeypatch, [FakeResponse(payload=[])])
    assert store.get_item("nope") is None


def test_supabase_create_item(monkeypatch):
    store, seen = _cloud_store(monkeypatch, [FakeResponse(payload=[{"id": "1", "title": "t"}])])
    row = store.create_item({"title": "t"})
    assert row["id"] == "1"
    assert seen[0]["method"] == "POST"


def test_supabase_update_item_empty_patch_reads_back(monkeypatch):
    store, seen = _cloud_store(monkeypatch, [FakeResponse(payload=[{"id": "1"}])])
    assert store.update_item("1", {})["id"] == "1"
    assert seen[0]["method"] == "GET"


def test_supabase_update_item_patches(monkeypatch):
    store, seen = _cloud_store(monkeypatch, [FakeResponse(payload=[{"id": "1", "status": "done"}])])
    assert store.update_item("1", {"status": "done", "title": None})["status"] == "done"
    assert seen[0]["method"] == "PATCH"
    assert "title" not in seen[0]["json"]


def test_supabase_delete_cleans_links(monkeypatch):
    store, seen = _cloud_store(
        monkeypatch,
        [FakeResponse(payload=[]), FakeResponse(payload=[]), FakeResponse(payload=[])],
    )
    assert store.delete_item("1") is True
    assert [call["method"] for call in seen] == ["DELETE", "DELETE", "DELETE"]


def test_supabase_create_links_empty_short_circuits(monkeypatch):
    store, seen = _cloud_store(monkeypatch, [])
    assert store.create_links("1", []) == []
    assert seen == []


def test_supabase_create_links_payload(monkeypatch):
    store, seen = _cloud_store(monkeypatch, [FakeResponse(payload=[{"id": "l"}])])
    store.create_links("1", [{"id": "2", "score": 0.5, "reason": "共享标签"}])
    assert seen[0]["json"][0]["src_id"] == "1"
    assert seen[0]["json"][0]["dst_id"] == "2"


def test_supabase_list_summaries_and_create(monkeypatch):
    store, _ = _cloud_store(
        monkeypatch, [FakeResponse(payload=[{"id": "s"}]), FakeResponse(payload=[{"id": "s2"}])]
    )
    assert store.list_summaries(limit=3) == [{"id": "s"}]
    assert store.create_summary({"title": "x"})["id"] == "s2"


def test_supabase_create_summary_falls_back_to_input(monkeypatch):
    store, _ = _cloud_store(monkeypatch, [FakeResponse(payload=[])])
    assert store.create_summary({"title": "x"})["title"] == "x"


def test_supabase_raises_on_transport_error(monkeypatch):
    class Err(FakeClient):
        def request(self, *a, **kw):
            raise httpx.ConnectError("down")

    monkeypatch.setattr(store_mod.httpx, "Client", Err)
    store = SupabaseStore(Settings(supabase_url="https://x.supabase.co", supabase_key="k"))
    with pytest.raises(StoreError, match="不可达"):
        store.list_items()


def test_supabase_raises_on_error_status(monkeypatch):
    class Err(FakeClient):
        def request(self, *a, **kw):
            return FakeResponse(status_code=500, text="boom")

    monkeypatch.setattr(store_mod.httpx, "Client", Err)
    store = SupabaseStore(Settings(supabase_url="https://x.supabase.co", supabase_key="k"))
    with pytest.raises(StoreError, match="500"):
        store.list_items()


def test_supabase_raises_on_invalid_json(monkeypatch):
    class Err(FakeClient):
        def request(self, *a, **kw):
            return FakeResponse(payload=None, text="nope")

    monkeypatch.setattr(store_mod.httpx, "Client", Err)
    store = SupabaseStore(Settings(supabase_url="https://x.supabase.co", supabase_key="k"))
    with pytest.raises(StoreError, match="不是合法 JSON"):
        store.list_items()


def test_create_store_picks_by_configuration():
    assert isinstance(create_store(Settings()), MemoryStore)
    assert isinstance(
        create_store(Settings(supabase_url="https://x.supabase.co", supabase_key="k")),
        SupabaseStore,
    )


# -- CLI ----------------------------------------------------------------------


def test_cli_serve_invokes_uvicorn(monkeypatch):
    import sys
    from types import ModuleType

    from info_butler import cli

    captured = {}
    fake = ModuleType("uvicorn")
    fake.run = lambda app, **kwargs: captured.update({"app": app, **kwargs})
    monkeypatch.setitem(sys.modules, "uvicorn", fake)

    assert cli.main(["serve", "--host", "0.0.0.0", "--port", "8080", "--reload"]) == 0
    assert captured["app"] == "info_butler.api:create_app"
    assert captured["factory"] is True
    assert captured["port"] == 8080
    assert captured["reload"] is True
