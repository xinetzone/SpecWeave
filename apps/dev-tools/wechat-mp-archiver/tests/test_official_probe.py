"""官方源联调探针测试（TR-8.1，全 mock 传输层）。"""

import json

import httpx
import pytest
from pydantic import SecretStr

from mp_archiver.config import Settings
from mp_archiver.core import official_probe
from mp_archiver.db import connect, init_db, upsert_article
from mp_archiver.http_client import RateLimitedClient
from mp_archiver.models import ArticleRecord, ArticleStatus

BIZ = "MzAxMjM0NTY3OA=="
APP_ID = "wx0123456789abcdef"
APP_SECRET = "0123456789abcdef0123456789abcdef"


def make_settings(tmp_path, **overrides) -> Settings:
    base = dict(
        request_delay_min=0.0,
        request_delay_max=0.0,
        max_retries=0,
        db_path=tmp_path / "data" / "archive.db",
        archive_root=tmp_path / "archive",
        wechat_app_id=APP_ID,
        wechat_app_secret=SecretStr(APP_SECRET),
        wechat_official_biz=BIZ,
        official_daily_call_cap=90,
    )
    base.update(overrides)
    return Settings(**base)


def make_client(settings, handler) -> RateLimitedClient:
    return RateLimitedClient(
        settings, transport=httpx.MockTransport(handler),
        sleeper=lambda _: None,
    )


def _news_url(mid="2247", idx=1, sn="snaaa", biz: str = BIZ) -> str:
    from urllib.parse import quote
    return (f"https://mp.weixin.qq.com/s?__biz={quote(biz, safe='')}"
            f"&mid={mid}&idx={idx}&sn={sn}")


def _first_page(biz: str = BIZ) -> dict:
    return {
        "errcode": 0, "total_count": 3, "item_count": 3,
        "item": [
            {"article_id": "2201", "update_time": 1710000000,
             "content": {"news_item": [
                 {"title": "首篇", "url": _news_url(biz=biz),
                  "thumb_url": "https://x/t.jpg"}]}},
            {"article_id": "2202", "update_time": 1710000001,
             "content": {"news_item": [
                 {"title": "次篇", "url": _news_url(mid="2248",
                                                    biz=biz)}]}},
            {"article_id": "2203", "update_time": 1710000002,
             "content": {"news_item": [
                 {"title": "三篇", "url": _news_url(mid="2249",
                                                    biz=biz)}]}},
        ],
    }


# ---------- 第 0 段：配置 ----------

def test_probe_config_valid_with_explicit_biz(tmp_path):
    settings = make_settings(tmp_path)
    conn = connect(settings.db_path)
    init_db(conn)
    report, biz = official_probe.probe_config(settings, "自有号", conn)
    assert report.ok
    assert biz == BIZ
    assert all(s.status != "fail" for s in report.stages)


def test_probe_config_missing_credentials_and_biz(tmp_path):
    settings = make_settings(
        tmp_path,
        wechat_app_id="", wechat_app_secret=SecretStr(""),
        wechat_official_biz="",
    )
    conn = connect(settings.db_path)
    init_db(conn)
    report, biz = official_probe.probe_config(settings, "自有号", conn)
    fails = [s for s in report.stages if s.status == "fail"]
    warns = [s for s in report.stages if s.status == "warn"]
    assert len(fails) == 2 and len(warns) == 1 and biz == ""


def test_probe_config_biz_alias_fallback_from_r2(tmp_path):
    settings = make_settings(tmp_path, wechat_official_biz="")
    conn = connect(settings.db_path)
    init_db(conn)
    record = ArticleRecord(
        biz=BIZ, account_alias="自有号", mid="2247", idx=1, sn="snaaa",
        title="历史", url="https://mp.weixin.qq.com/s?x=1",
        status=ArticleStatus.PENDING,
    )
    upsert_article(conn, record)
    report, biz = official_probe.probe_config(settings, "自有号", conn)
    assert biz == BIZ
    assert any("R2" in s.message for s in report.stages if s.status == "ok")


# ---------- 第 1 段：网络 ----------

def test_network_ok_on_40001(tmp_path):
    def handler(request):
        assert request.url.path == "/cgi-bin/getcallbackip"
        return httpx.Response(200, json={"errcode": 40001,
                                         "errmsg": "invalid credential"})
    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        result = official_probe.probe_network(client)
    assert result.status == "ok"


def test_network_fail_on_transport_error(tmp_path):
    def handler(request):
        raise httpx.ConnectError("DNS failure")
    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        result = official_probe.probe_network(client)
    assert result.status == "fail" and "代理" in " ".join(result.details)


def test_network_fail_on_html_hijack(tmp_path):
    def handler(request):
        return httpx.Response(200, text="<html>proxy block</html>")
    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        result = official_probe.probe_network(client)
    assert result.status == "fail" and "非 JSON" in result.message


# ---------- 第 2 段：token ----------

def test_probe_token_success(tmp_path):
    def handler(request):
        return httpx.Response(200, json={"access_token": "tok-abc123xyz",
                                         "expires_in": 7200})
    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        result, token = official_probe.probe_token(
            client, APP_ID, APP_SECRET)
    assert result.status == "ok" and token == "tok-abc123xyz"
    assert "abc123" not in result.message  # 脱敏：只显示前 6 位


def test_probe_token_40164_extracts_ip(tmp_path):
    def handler(request):
        return httpx.Response(200, json={
            "errcode": 40164,
            "errmsg": "invalid ip 203.0.113.7, not in whitelist",
        })
    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        result, token = official_probe.probe_token(
            client, APP_ID, APP_SECRET)
    assert result.status == "fail" and token == ""
    assert "40164" in result.message
    assert any("203.0.113.7" in d for d in result.details)


def test_probe_token_40125_secret_wrong(tmp_path):
    def handler(request):
        return httpx.Response(200, json={"errcode": 40125,
                                         "errmsg": "invalid appsecret"})
    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        result, _ = official_probe.probe_token(client, APP_ID, APP_SECRET)
    assert result.status == "fail"
    assert any("AppSecret" in d for d in result.details)


def test_probe_token_48001_permission(tmp_path):
    def handler(request):
        return httpx.Response(200, json={"errcode": 48001,
                                         "errmsg": "no permission"})
    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        result, _ = official_probe.probe_token(client, APP_ID, APP_SECRET)
    assert result.status == "fail" and "权限" in result.message


# ---------- 第 3 段：batchget 实页 + biz 核对 ----------

def _api_handler(page_payload=None, *, token_payload=None,
                 stripped_first=False):
    def handler(request):
        path = request.url.path
        if path == "/cgi-bin/getcallbackip":
            return httpx.Response(200, json={"errcode": 40001,
                                             "errmsg": "invalid credential"})
        if path == "/cgi-bin/token":
            return httpx.Response(200, json=token_payload or
                                  {"access_token": "tok1", "expires_in": 7200})
        if path == "/cgi-bin/freepublish/batchget":
            body = json.loads(request.content)
            if stripped_first and body.get("no_content") == 1:
                return httpx.Response(200, json={
                    "errcode": 0, "total_count": 3,
                    "item": [{"article_id": "x", "update_time": 1}],
                })
            return httpx.Response(200, json=page_payload or _first_page())
        return httpx.Response(404)
    return handler


def test_batchget_success_and_biz_match(tmp_path):
    settings = make_settings(tmp_path)
    with make_client(settings, _api_handler()) as client:
        result = official_probe.probe_batchget(
            client, settings, BIZ, "自有号")
    assert result.status == "ok"
    assert any("biz 一致性核对通过" in d for d in result.details)
    assert any("3 篇" in d for d in result.details)


def test_batchget_stripped_then_retried(tmp_path):
    settings = make_settings(tmp_path)
    with make_client(settings,
                     _api_handler(stripped_first=True)) as client:
        result = official_probe.probe_batchget(
            client, settings, BIZ, "自有号")
    assert result.status == "ok"
    assert any("重取成功" in d for d in result.details)


def test_batchget_biz_mismatch_fails(tmp_path):
    # URL 里的 __biz 属于另一个主体
    settings = make_settings(tmp_path)
    other = "MzOTHEROTHER%3D%3D"
    with make_client(settings, _api_handler(_first_page(biz="MzOTHEROTHER=="))) \
            as client:
        result = official_probe.probe_batchget(client, settings, BIZ, "自有号")
    assert result.status == "fail" and "biz 不一致" in result.message


def test_batchget_empty_account_warns(tmp_path):
    settings = make_settings(tmp_path)
    empty = {"errcode": 0, "total_count": 0, "item": []}
    with make_client(settings, _api_handler(empty)) as client:
        result = official_probe.probe_batchget(client, settings, BIZ, "自有号")
    assert result.status == "warn" and "总数为 0" in result.message


def test_batchget_quota_exhausted_skips(tmp_path):
    settings = make_settings(tmp_path, official_daily_call_cap=2)
    state = settings.db_path.parent / "official_api_quota.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(
        json.dumps({"date": "", "calls": 2}), encoding="utf-8")
    # 将日期改成今天（UTC）以模拟已耗尽；复用 guard 的日期口径
    from mp_archiver.adapters.official_api import DailyQuotaGuard
    guard = DailyQuotaGuard(state, cap=2)
    state.write_text(json.dumps({"date": guard.day, "calls": 2}),
                     encoding="utf-8")
    with make_client(settings, _api_handler()) as client:
        result = official_probe.probe_batchget(client, settings, BIZ, "自有号")
    assert result.status == "warn" and "配额" in result.message


def test_batchget_48001_reports_permission(tmp_path):
    settings = make_settings(tmp_path)
    handler = _api_handler({"errcode": 48001, "errmsg": "unauthorized"})
    with make_client(settings, handler) as client:
        result = official_probe.probe_batchget(client, settings, BIZ, "自有号")
    assert result.status == "fail" and "权限" in result.message


# ---------- 全流程编排 ----------

def test_full_probe_all_pass(tmp_path):
    settings = make_settings(tmp_path)
    conn = connect(settings.db_path)
    init_db(conn)
    with make_client(settings, _api_handler()) as client:
        report = official_probe.run_full_probe(
            settings, client, account_alias="自有号", conn=conn)
    names = [s.stage for s in report.stages]
    assert names == ["config", "config", "config", "network", "token",
                     "batchget"]
    assert report.ok and all(s.status in {"ok"} for s in report.stages)


def test_full_probe_skips_after_network_fail(tmp_path):
    settings = make_settings(tmp_path)
    conn = connect(settings.db_path)
    init_db(conn)

    def handler(request):
        raise httpx.ConnectError("no route")

    with make_client(settings, handler) as client:
        report = official_probe.run_full_probe(
            settings, client, account_alias="自有号", conn=conn)
    statuses = {s.stage: s.status for s in report.stages}
    assert statuses["network"] == "fail"
    assert statuses["token"] == "skip" and statuses["batchget"] == "skip"
    assert not report.ok


def test_full_probe_no_credentials_skips_token(tmp_path):
    settings = make_settings(
        tmp_path, wechat_app_id="", wechat_app_secret=SecretStr(""))
    conn = connect(settings.db_path)
    init_db(conn)
    with make_client(settings, _api_handler()) as client:
        report = official_probe.run_full_probe(
            settings, client, account_alias="自有号", conn=conn)
    statuses = {s.stage: s.status for s in report.stages}
    assert statuses["network"] == "ok"
    assert statuses["token"] == "skip" and statuses["batchget"] == "skip"


def test_normalize_biz_decodes_url_encoding():
    assert official_probe.normalize_biz("MzA..%3D%3D") == "MzA..=="
    assert official_probe.normalize_biz("  MzA..==  ") == "MzA..=="


# ---------- 短链 biz 解析 ----------

def test_resolve_identity_follows_redirect_to_full_url(tmp_path):
    full = ("https://mp.weixin.qq.com/s?__biz=MzAxMjM0NTY3OA%3D%3D"
            "&mid=2247&idx=1&sn=abcdef")

    def handler(request):
        if request.url.path == "/s/short":
            return httpx.Response(302, headers={"location": full})
        return httpx.Response(200, text="<html></html>")

    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        identity = official_probe.resolve_article_identity(
            client, "https://mp.weixin.qq.com/s/short")
    assert identity["biz"] == BIZ and identity["mid"] == "2247"
    assert identity["source"] == "最终 URL"


def test_resolve_identity_from_og_url_meta(tmp_path):
    html = (
        '<html><head><meta property="og:url" '
        'content="https://mp.weixin.qq.com/s?__biz=MzAxMjM0NTY3OA%3D%3D'
        '&mid=2247&idx=1&sn=abcdef"></head><body></body></html>'
    )

    def handler(request):
        return httpx.Response(200, text=html)

    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        identity = official_probe.resolve_article_identity(
            client, "https://mp.weixin.qq.com/s/short")
    assert identity["biz"] == BIZ and identity["source"] == "页面 og:url"


def test_resolve_identity_from_var_biz_fallback(tmp_path):
    html = '<html><script>var biz = "MzAxMjM0NTY3OA=="; var mid = "2247";</script></html>'

    def handler(request):
        return httpx.Response(200, text=html)

    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        identity = official_probe.resolve_article_identity(
            client, "https://mp.weixin.qq.com/s/short")
    assert identity["biz"] == BIZ and identity["source"] == "页面 var biz"


def test_resolve_identity_failure_raises(tmp_path):
    from mp_archiver.exceptions import PayloadError as PE

    def handler(request):
        return httpx.Response(200, text="<html>环境异常页，无任何身份参数</html>")

    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        with pytest.raises(PE, match="无法从该链接提取"):
            official_probe.resolve_article_identity(
                client, "https://mp.weixin.qq.com/s/short")


def test_resolve_identity_rejects_js_placeholder(tmp_path):
    """验证码页的 JS 模板占位符 __biz=${window.biz} 不得被当成真实 biz。"""
    from mp_archiver.exceptions import PayloadError as PE

    html = (
        '<html><script>__biz=${window.biz};</script>'
        '<a href="/s?__biz=${window.biz}&mid=1">link</a></html>'
    )

    def handler(request):
        return httpx.Response(200, text=html)

    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        with pytest.raises(PE, match="无法从该链接提取"):
            official_probe.resolve_article_identity(
                client, "https://mp.weixin.qq.com/s/short")


def test_resolve_identity_raises_on_captcha_page(tmp_path):
    """重定向到验证码页（wappoc_appmsgcaptcha）时应直接报错。"""
    from mp_archiver.exceptions import PayloadError as PE

    captcha = ("https://mp.weixin.qq.com/mp/wappoc_appmsgcaptcha"
               "?poc_token=xxx&target_url=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2Fabc")

    def handler(request):
        if request.url.path == "/s/short":
            return httpx.Response(302, headers={"location": captcha})
        return httpx.Response(200, text="<html>captcha</html>")

    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        with pytest.raises(PE, match="人机验证码页"):
            official_probe.resolve_article_identity(
                client, "https://mp.weixin.qq.com/s/short")


def test_resolve_identity_uses_micromessenger_ua(tmp_path):
    """请求必须携带 MicroMessenger UA 以绕过验证码页拦截。"""
    full = ("https://mp.weixin.qq.com/s?__biz=MzAxMjM0NTY3OA%3D%3D"
            "&mid=2247&idx=1&sn=abcdef")
    captured_ua = {}

    def handler(request):
        captured_ua["ua"] = request.headers.get("user-agent", "")
        if request.url.path == "/s/short":
            return httpx.Response(302, headers={"location": full})
        return httpx.Response(200, text="<html></html>")

    settings = make_settings(tmp_path)
    with make_client(settings, handler) as client:
        identity = official_probe.resolve_article_identity(
            client, "https://mp.weixin.qq.com/s/short")
    assert identity["biz"] == BIZ
    assert "MicroMessenger" in captured_ua["ua"]
