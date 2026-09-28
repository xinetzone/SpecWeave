"""wechat-download-api 适配器 HTTP 行为测试（MockTransport，无真实网络）。"""

import json

import httpx
import pytest

from mp_archiver.adapters.base import AccountRef
from mp_archiver.adapters.wechat_download_api import (
    AccountNotFoundError,
    BizUnavailableError,
    EndpointDiscoveryError,
    WechatDownloadApiAdapter,
)
from mp_archiver.adapters.wechat_payload import (
    ApiRetError,
    CredentialExpiredError,
    PayloadError,
)
from mp_archiver.config import Settings
from mp_archiver.http_client import RateLimitedClient

SPEC = {
    "paths": {
        "/api/official-accounts/search": {
            "get": {"parameters": [
                {"name": "query", "in": "query"},
                {"name": "begin", "in": "query"},
                {"name": "count", "in": "query"},
            ]}
        },
        "/api/articles/history": {
            "get": {"parameters": [
                {"name": "__biz", "in": "query"},
                {"name": "offset", "in": "query"},
                {"name": "count", "in": "query"},
                {"name": "f", "in": "query"},
            ]}
        },
    }
}

SEARCH_PATH = "/api/official-accounts/search"
HISTORY_PATH = "/api/articles/history"
BIZ = "MzA4MjA=="


def _search_item(name="意识食谱", alias="mindfood", with_biz=True):
    item = {"fakeid": 998877, "nickname": name, "alias": alias}
    if with_biz:
        item["__biz"] = BIZ
    return item


def _history_payload():
    article = {
        "title": "首篇文章",
        "digest": "摘要",
        "content_url": (
            "http://mp.weixin.qq.com/s?__biz=MzA4MjA%3D%3D&mid=2447531234"
            "&idx=1&sn=sn001"
        ),
        "cover": "http://img/cover.jpg",
    }
    return {
        "ret": 0,
        "general_msg_list": json.dumps({
            "list": [{
                "comm_msg_info": {"id": 1, "type": 49, "datetime": 1609459200},
                "app_msg_ext_info": article,
            }]
        }),
        "next_offset": 10,
        "can_msg_continue": 1,
    }


@pytest.fixture
def settings():
    return Settings(
        _env_file=None,
        request_delay_min=0,
        request_delay_max=0,
        max_retries=0,
        backoff_base=0.01,
        backoff_cap=0.01,
    )


def _make_client(settings, handler):
    return RateLimitedClient(
        settings,
        transport=httpx.MockTransport(handler),
        sleeper=lambda _: None,
        rng=lambda a, b: 0,
    )


def test_build_resolve_and_fetch(settings):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/openapi.json":
            return httpx.Response(200, json=SPEC)
        params = request.url.params
        if path == SEARCH_PATH:
            seen["search"] = dict(params)
            return httpx.Response(200, json={"base_resp": {"ret": 0},
                                            "list": [_search_item()]})
        if path == HISTORY_PATH:
            seen["history"] = dict(params)
            return httpx.Response(200, json=_history_payload())
        return httpx.Response(404)

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    account = adapter.resolve_account("意识食谱")
    assert account.biz == BIZ
    assert seen["search"]["query"] == "意识食谱"

    page = adapter.fetch_history_page(account, offset=0)
    assert seen["history"]["__biz"] == BIZ
    assert seen["history"]["offset"] == "0"
    assert seen["history"]["count"] == "10"
    assert seen["history"]["f"] == "json"
    assert len(page.articles) == 1
    assert page.articles[0].title == "首篇文章"
    assert page.has_more is True


def test_search_paginates_until_found(settings):
    begins = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=SPEC)
        if request.url.path == SEARCH_PATH:
            begin = int(request.url.params["begin"])
            begins.append(begin)
            if begin == 0:
                return httpx.Response(200, json={"list": [
                    _search_item(name=f"无关号{i}", with_biz=False) for i in range(5)
                ]})
            return httpx.Response(200, json={"list": [_search_item()]})
        return httpx.Response(404)

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    account = adapter.resolve_account("意识食谱")
    assert begins == [0, 5]
    assert account.nickname == "意识食谱"


def test_search_not_found(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=SPEC)
        return httpx.Response(200, json={"list": []})

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    with pytest.raises(AccountNotFoundError):
        adapter.resolve_account("不存在的号")


def test_history_401_raises_credential_expired(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=SPEC)
        if request.url.path == SEARCH_PATH:
            return httpx.Response(200, json={"list": [_search_item()]})
        return httpx.Response(401)

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    account = adapter.resolve_account("意识食谱")
    with pytest.raises(CredentialExpiredError):
        adapter.fetch_history_page(account, 0)


def test_build_without_endpoints_raises(settings):
    bare_spec = {"paths": {"/api/login/init": {"post": {}}}}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=bare_spec)

    client = _make_client(settings, handler)
    with pytest.raises(EndpointDiscoveryError):
        WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")


def test_override_paths_are_used(settings):
    spec = {"paths": {
        "/custom/search": {"get": {"parameters": [
            {"name": "keyword", "in": "query"}]}},
        "/custom/list": {"get": {"parameters": [
            {"name": "biz", "in": "query"},
            {"name": "cursor", "in": "query"},
        ]}},
    }}
    requested = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=spec)
        requested.append(request.url.path)
        if request.url.path == "/custom/search":
            return httpx.Response(200, json={"list": [_search_item()]})
        if request.url.path == "/custom/list":
            return httpx.Response(200, json=_history_payload())
        return httpx.Response(404)

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(
        client,
        base_url="http://127.0.0.1:5000",
        search_override="/custom/search",
        history_override="/custom/list",
    )
    account = adapter.resolve_account("意识食谱")
    page = adapter.fetch_history_page(account, 3)
    assert requested == ["/custom/search", "/custom/list"]
    # 非标准参数名按端点声明匹配（biz + cursor），count/f 未声明则不发送
    assert page.articles[0].sn == "sn001"


# ---- 端点发现与参数分支（Task 14 覆盖率补齐） ----

def test_adapter_surface_property_exposes_endpoints(settings):
    """surface 属性返回发现到的 search/history 端点。"""
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=SPEC)
        return httpx.Response(404)

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    surface = adapter.surface
    assert surface.search.path == SEARCH_PATH
    assert surface.history.path == HISTORY_PATH


def test_build_openapi_http_error_raises_discovery_error(settings):
    """OpenAPI 返回 500（非 200/401/403）→ EndpointDiscoveryError。"""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="server error")

    client = _make_client(settings, handler)
    with pytest.raises(EndpointDiscoveryError):
        WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")


def test_build_openapi_non_json_raises_discovery_error(settings):
    """OpenAPI 响应体不是 JSON → EndpointDiscoveryError。"""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"<html>not json</html>")

    client = _make_client(settings, handler)
    with pytest.raises(EndpointDiscoveryError):
        WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")


def _spec_with_history_params(params):
    """搜索端点固定，历史端点参数按需声明，用于参数匹配分支测试。"""
    return {"paths": {
        "/api/searchbiz": {"get": {}},
        "/api/getmsg": {"get": {"parameters": params}},
    }}


def test_history_uses_declared_fakeid_when_account_has_no_biz(settings):
    """端点只声明 fakeid 且账号有 fakeid → 发送 fakeid 而非 __biz。"""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=_spec_with_history_params([
                {"name": "fakeid", "in": "query"},
                {"name": "offset", "in": "query"},
            ]))
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json=_history_payload())

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    account = AccountRef(nickname="意识食谱", alias="mindfood", fakeid="998877", biz="")
    page = adapter.fetch_history_page(account, offset=0)
    assert seen["params"]["fakeid"] == "998877"
    assert "__biz" not in seen["params"]
    assert seen["params"]["offset"] == "0"
    assert len(page.articles) == 1


def test_history_without_query_declarations_uses_native_contract(settings):
    """端点无 query 声明且账号有 biz → 按微信原生契约发 __biz 并补 count/f。"""
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json={"paths": {
                "/api/searchbiz": {"get": {}},
                "/api/getmsg": {"get": {}},
            }})
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json=_history_payload())

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    account = AccountRef(nickname="意识食谱", alias="mindfood", fakeid="998877",
                         biz=BIZ)
    adapter.fetch_history_page(account, offset=0)
    assert seen["params"]["__biz"] == BIZ
    assert seen["params"]["offset"] == "0"
    assert seen["params"]["count"] == "10"
    assert seen["params"]["f"] == "json"


def test_history_without_biz_and_unmatched_params_raises(settings):
    """端点有声明但不接受 biz/fakeid 且账号无 biz → BizUnavailableError。"""
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=_spec_with_history_params([
                {"name": "q", "in": "query"},
            ]))
        return httpx.Response(200, json=_history_payload())

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    account = AccountRef(nickname="意识食谱", alias="mindfood", fakeid="", biz="")
    with pytest.raises(BizUnavailableError):
        adapter.fetch_history_page(account, offset=0)


def test_request_json_http_error_raises_api_ret_error(settings):
    """端点返回非 200（500）→ ApiRetError 携带状态码。"""
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=SPEC)
        return httpx.Response(500, text="boom")

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    with pytest.raises(ApiRetError) as ei:
        adapter.resolve_account("意识食谱")
    assert ei.value.ret == 500


def test_request_json_non_json_body_raises_payload_error(settings):
    """端点返回 200 但响应体不是 JSON → PayloadError。"""
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=SPEC)
        return httpx.Response(200, content=b"<html>oops</html>")

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    with pytest.raises(PayloadError):
        adapter.resolve_account("意识食谱")


def test_request_json_non_object_body_raises_payload_error(settings):
    """端点返回 JSON 数组（非对象）→ PayloadError。"""
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, json=SPEC)
        return httpx.Response(200, json=[1, 2, 3])

    client = _make_client(settings, handler)
    adapter = WechatDownloadApiAdapter.build(client, base_url="http://127.0.0.1:5000")
    with pytest.raises(PayloadError):
        adapter.resolve_account("意识食谱")
