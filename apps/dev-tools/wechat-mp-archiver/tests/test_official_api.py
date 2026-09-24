"""官方 freepublish/batchget adapter 测试（Task 8 / TR-8.1，全 mock）。"""

import json

import httpx
import pytest
from pydantic import SecretStr

from mp_archiver.adapters.official_api import (
    DailyQuotaGuard,
    DailyQuotaReached,
    OfficialApiAdapter,
    OfficialApiConfigError,
    OfficialApiPermissionError,
    parse_freepublish_page,
)
from mp_archiver.config import Settings
from mp_archiver.core.official_sync import sync_official_articles
from mp_archiver.db import connect, init_db, upsert_article
from mp_archiver.exceptions import ApiRetError, PayloadError
from mp_archiver.http_client import RateLimitedClient
from mp_archiver.models import ArticleRecord, ArticleStatus

BIZ = "MzAxMjM0NTY3OA=="


def _group(article_id: str, news: list[dict], update_time: int = 1710000000) -> dict:
    return {"article_id": article_id, "update_time": update_time,
            "content": {"news_item": news}}


def _news(title: str, *, mid: str = "2201", idx: int = 1,
          deleted: bool = False, sn: str = "snaaa") -> dict:
    return {
        "title": title,
        "author": "号主",
        "digest": f"{title}摘要",
        "content": "<p>x</p>",
        "url": f"https://mp.weixin.qq.com/s?__biz=BIZ&mid={mid}&idx={idx}&sn={sn}",
        "thumb_url": "https://mmbiz.qpic.cn/thumb",
        "content_source_url": "",
        "need_open_comment": 1,
        # 官方契约为 boolean
        "is_deleted": deleted,
    }


# 首页：1 个双图文群发 + 1 个已删群发 + 18 个普通群发 = 20 组（满页，触发翻页）
_FULL_FIRST = [
    _group("2201", [
        _news("第一篇", mid="2247", idx=1, sn="snaaa"),
        _news("第二篇", mid="2248", idx=2, sn="snbbb"),
    ]),
    _group("2202", [_news("第三篇已删", mid="2249", idx=1,
                          deleted=True, sn="snccc")]),
]
_FULL_FIRST += [
    _group(f"23{i:02d}", [_news(f"图文{i:02d}", mid=f"24{i}", idx=1,
                                sn=f"sn{i:02d}")])
    for i in range(100, 118)
]
PAGE_1 = {"errcode": 0, "total_count": 25, "item_count": 20, "item": _FULL_FIRST}
# 尾页 5 组（不足 PAGE_SIZE，翻页结束）
PAGE_2 = {
    "errcode": 0,
    "total_count": 25,
    "item_count": 5,
    "item": [
        _group(f"25{i:02d}", [_news(f"尾页{i}", mid=f"26{i}", idx=1,
                                    sn=f"snl{i}")])
        for i in range(5)
    ],
}


def test_parse_page_expands_groups_and_marks_deleted():
    page = parse_freepublish_page(PAGE_1, biz=BIZ, alias="自有号")
    assert page.total_groups == 25 and page.group_count == 20
    # 20 个群发组展开：双图文 2 + 已删 1 + 普通 18 = 21 篇
    assert len(page.groups) == 21
    first, second, deleted = page.groups[:3]
    # 身份键优先取自图文 URL（与 R2 公开页同构），群发 article_id 仅退化键
    assert (first.mid, first.idx, first.title, first.sn) == (
        "2247", 1, "第一篇", "snaaa"
    )
    assert second.mid == "2248" and second.idx == 2 and second.sn == "snbbb"
    assert first.publish_time and first.publish_time.endswith("+00:00")
    assert first.account_alias == "自有号" and first.biz == BIZ
    assert deleted.status is ArticleStatus.EXTERNAL_REF
    assert first.cover_url and "thumb" in first.cover_url


def test_parse_permission_and_other_errcode():
    with pytest.raises(OfficialApiPermissionError):
        parse_freepublish_page({"errcode": 48001, "errmsg": "unauthorized"},
                               biz=BIZ, alias="x")
    with pytest.raises(ApiRetError):
        parse_freepublish_page({"errcode": 45009, "errmsg": "limit"},
                               biz=BIZ, alias="x")


_STRIPPED_PAGE = {
    "errcode": 0,
    "total_count": 25,
    "item_count": 20,
    # 平台将承载 news_item 的 content 整体裁剪（no_content 歧义场景）
    "item": [
        {"article_id": f"23{i:02d}", "update_time": 1710000000}
        for i in range(20)
    ],
}


class _CallRecorder:
    def __init__(self, *, token_invalid_once: bool = False,
                 permission: bool = False, strip_content: bool = False,
                 always_empty: bool = False, always_invalid: bool = False):
        self.token_calls = 0
        self.batch_calls = 0
        self.token_invalid_once = token_invalid_once
        self.permission = permission
        self.strip_content = strip_content
        self.always_empty = always_empty
        self.always_invalid = always_invalid

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/cgi-bin/token":
            self.token_calls += 1
            if self.permission:
                return httpx.Response(200, json={"errcode": 48001,
                                                 "errmsg": "no permission"})
            return httpx.Response(
                200, json={"access_token": f"tok-{ self.token_calls}",
                           "expires_in": 7200}
            )
        if request.url.path == "/cgi-bin/freepublish/batchget":
            self.batch_calls += 1
            if self.permission:
                return httpx.Response(200, json={"errcode": 48001,
                                                 "errmsg": "unauthorized"})
            if self.always_invalid:
                return httpx.Response(
                    200, json={"errcode": 40001, "errmsg": "invalid credential"}
                )
            if self.token_invalid_once and self.batch_calls == 1:
                return httpx.Response(
                    200, json={"errcode": 40001, "errmsg": "invalid credential"}
                )
            body = json.loads(request.content)
            offset = body.get("offset")
            no_content = body.get("no_content")
            if self.always_empty:
                return httpx.Response(200, json=_STRIPPED_PAGE)
            if self.strip_content and no_content == 1:
                return httpx.Response(200, json=_STRIPPED_PAGE)
            return httpx.Response(200, json=PAGE_1 if offset == 0 else PAGE_2)
        return httpx.Response(404)


@pytest.fixture
def settings(tmp_path):
    return Settings(
        request_delay_min=0.0,
        request_delay_max=0.0,
        max_retries=0,
        db_path=tmp_path / "data" / "archive.db",
        archive_root=tmp_path / "archive",
        wechat_app_id="wxapp",
        wechat_app_secret=SecretStr("sek"),
        wechat_official_biz=BIZ,
    )


def _client(settings, recorder):
    return RateLimitedClient(
        settings, transport=httpx.MockTransport(recorder.handler),
        sleeper=lambda _: None,
    )


def test_adapter_paginates_with_single_token_request(settings):
    recorder = _CallRecorder()
    conn = connect(settings.db_path)
    init_db(conn)
    with _client(settings, recorder) as client:
        report = sync_official_articles(
            conn, settings, client, account_alias="自有号"
        )

    assert report.enabled and report.pages == 2
    assert report.total_groups == 25
    # 25 个群发共展开 26 篇（1 组双图文），1 篇已删跳过 → 25 入库
    assert report.inserted == 25 and report.skipped_deleted == 1
    assert recorder.token_calls == 1  # 两页共用一个 token
    rows = conn.execute(
        "SELECT mid, idx, source, status FROM articles WHERE mid IN ('2247','2248')"
        " ORDER BY mid, idx"
    ).fetchall()
    assert [(r["mid"], r["idx"], r["source"], r["status"]) for r in rows] == [
        ("2247", 1, "official_api", "pending"),
        ("2248", 2, "official_api", "pending"),
    ]
    conn.close()


def test_adapter_refreshes_token_once_on_40001(settings):
    recorder = _CallRecorder(token_invalid_once=True)
    conn = connect(settings.db_path)
    init_db(conn)
    with _client(settings, recorder) as client:
        adapter = OfficialApiAdapter(client, "wxapp", "sek")
        guard = DailyQuotaGuard(settings.db_path.parent / "q.json", cap=10)
        payload = adapter.batchget_page(offset=0, guard=guard)
    assert payload["total_count"] == 25
    assert recorder.token_calls == 2  # 首次取 token + 40001 强制刷新


def test_adapter_48001_raises_permission(settings):
    recorder = _CallRecorder(permission=True)
    conn = connect(settings.db_path)
    init_db(conn)
    with _client(settings, recorder) as client:
        adapter = OfficialApiAdapter(client, "wxapp", "sek")
        guard = DailyQuotaGuard(settings.db_path.parent / "q.json", cap=10)
        with pytest.raises(OfficialApiPermissionError):
            adapter.batchget_page(offset=0, guard=guard)
    conn.close()


def test_disabled_without_credentials_makes_no_requests(tmp_path):
    settings = Settings(
        request_delay_min=0.0, request_delay_max=0.0,
        db_path=tmp_path / "a.db", archive_root=tmp_path / "arc",
    )
    conn = connect(settings.db_path)
    init_db(conn)
    client = RateLimitedClient(
        settings,
        transport=httpx.MockTransport(lambda r: pytest.fail("不应发起请求")),
        sleeper=lambda _: None,
    )
    report = sync_official_articles(conn, settings, client, account_alias="x")
    assert report.enabled is False
    client.close()
    conn.close()


def test_missing_biz_raises_config_error(tmp_path):
    settings = Settings(
        request_delay_min=0.0, request_delay_max=0.0,
        db_path=tmp_path / "a.db", archive_root=tmp_path / "arc",
        wechat_app_id="wxapp", wechat_app_secret=SecretStr("sek"),
        # 不设 wechat_official_biz，且库中无别名记录
    )
    conn = connect(settings.db_path)
    init_db(conn)
    with _client(settings, _CallRecorder()) as client:
        with pytest.raises(OfficialApiConfigError):
            sync_official_articles(conn, settings, client, account_alias="未知号")
    conn.close()


def test_merge_with_r2_source_and_preserve_status(settings):
    conn = connect(settings.db_path)
    init_db(conn)
    # R2 先入库：同 biz+mid+idx（公开页 URL 同构身份键），已正文归档
    existing = ArticleRecord(
        biz=BIZ, mid="2247", idx=1, sn="snaaa", account_alias="自有号",
        title="旧标题",
    )
    upsert_article(conn, existing, status=ArticleStatus.DOWNLOADED)

    recorder = _CallRecorder()
    with _client(settings, recorder) as client:
        report = sync_official_articles(conn, settings, client,
                                        account_alias="自有号")

    # 首页 20 篇（含双图文）：2201/1 合并，余 19 新增；尾页 5 新增
    assert report.inserted == 24 and report.updated == 1
    row = conn.execute(
        "SELECT source, status, title FROM articles WHERE mid='2247' AND idx=1"
    ).fetchone()
    assert row["source"] == "exporter+official_api"
    assert row["status"] == "downloaded"  # 不回退采集状态
    assert row["title"] == "第一篇"  # 元数据被官方源补全
    assert conn.execute("SELECT COUNT(*) AS n FROM articles").fetchone()["n"] == 25
    conn.close()


def test_quota_guard_persists_and_stops_pagination(settings):
    # cap=2：第一页用 1 次，第二页前还有 1 次 → 实际两页都能请求；
    # cap=1 时第二页前触顶，quota_reached=True
    settings = settings.model_copy(update={"official_daily_call_cap": 1})
    conn = connect(settings.db_path)
    init_db(conn)
    recorder = _CallRecorder()
    with _client(settings, recorder) as client:
        report = sync_official_articles(
            conn, settings, client, account_alias="自有号"
        )
    assert report.quota_reached is True
    assert report.pages == 1
    assert recorder.batch_calls == 1

    state_file = settings.db_path.parent / "official_api_quota.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state == {"date": state["date"], "calls": 1}

    # 同日内同阈值再次运行：guard 已无余量，直接触顶（不再发请求）
    with _client(settings, recorder) as client:
        report2 = sync_official_articles(
            conn, settings, client, account_alias="自有号"
        )
    assert report2.quota_reached is True and report2.pages == 0
    conn.close()


def test_quota_guard_resets_on_new_day(tmp_path):
    state_file = tmp_path / "q.json"
    state_file.write_text(
        json.dumps({"date": "2000-01-01", "calls": 999}), encoding="utf-8"
    )
    guard = DailyQuotaGuard(state_file, cap=10)
    assert guard.calls == 0 and guard.remaining == 10
    guard.acquire()
    assert json.loads(state_file.read_text(encoding="utf-8"))["calls"] == 1
    with pytest.raises(DailyQuotaReached):
        for _ in range(20):
            guard.acquire()


def test_quota_guard_tolerates_corrupt_state_shapes(tmp_path):
    state_file = tmp_path / "q.json"
    for raw in ("[]", "null", '{"date": "x", "calls": "abc"}', "{not json"):
        state_file.write_text(raw, encoding="utf-8")
        assert DailyQuotaGuard(state_file, cap=3).calls == 0
    # 负 calls 归零，不得产生超出 cap 的余量
    state_file.write_text(
        json.dumps({"date": DailyQuotaGuard(state_file, cap=3).day,
                    "calls": -50}), encoding="utf-8"
    )
    guard = DailyQuotaGuard(state_file, cap=3)
    assert guard.calls == 0 and guard.remaining == 3


def test_parse_malformed_item_and_garbage_values():
    with pytest.raises(PayloadError):
        parse_freepublish_page({"errcode": 0, "item": {"unexpected": 1}},
                               biz=BIZ, alias="x")
    # total_count>0 却缺失 item：结构异常，不得静默按空页收尾
    with pytest.raises(PayloadError, match="缺失 item"):
        parse_freepublish_page({"errcode": 0, "total_count": 5},
                               biz=BIZ, alias="x")
    # total_count=0 且无 item：正常空尾页
    empty = parse_freepublish_page({"errcode": 0, "total_count": 0},
                                   biz=BIZ, alias="x")
    assert empty.groups == () and empty.group_count == 0
    # 组非 dict 安全跳过；非法 errcode/时间戳容错
    page = parse_freepublish_page(
        {"errcode": "not-a-code", "total_count": "x",
         "item": ["not-a-group",
                  {"article_id": "g1", "update_time": 10 ** 18,
                   "content": {"news_item": [
                       {"title": "t", "is_deleted": "true-as-string"},
                   ]}}]},
        biz=BIZ, alias="x",
    )
    assert page.total_groups == 0 and page.group_count == 2
    (only,) = page.groups
    assert only.mid == "g1" and only.publish_time is None


def test_stripped_content_retried_with_no_content_zero(settings):
    """no_content=1 裁剪 content 时自动以 0 重取，不静默零产出。"""
    recorder = _CallRecorder(strip_content=True)
    conn = connect(settings.db_path)
    init_db(conn)
    with _client(settings, recorder) as client:
        report = sync_official_articles(conn, settings, client,
                                        account_alias="自有号")
    # 首页/尾页均经历 no_content=1 裁剪 + 0 重取：共 4 次 batchget
    assert recorder.batch_calls == 4 and report.pages == 2
    assert report.inserted == 25
    conn.close()


def test_permanently_empty_page_raises_payload_error(settings):
    recorder = _CallRecorder(always_empty=True)
    conn = connect(settings.db_path)
    init_db(conn)
    with _client(settings, recorder) as client:
        with pytest.raises(PayloadError, match="no_content=0 重取后仍无图文条目"):
            sync_official_articles(conn, settings, client, account_alias="自有号")
    assert recorder.batch_calls == 2  # 原始 + 重试，无死循环
    conn.close()


def test_token_invalid_twice_raises_apiret(settings):
    recorder = _CallRecorder(always_invalid=True)
    conn = connect(settings.db_path)
    init_db(conn)
    with _client(settings, recorder) as client:
        adapter = OfficialApiAdapter(client, "wxapp", "sek")
        guard = DailyQuotaGuard(settings.db_path.parent / "q.json", cap=10)
        raw = adapter.batchget_page(offset=0, guard=guard)
        with pytest.raises(ApiRetError):
            parse_freepublish_page(raw, biz=BIZ, alias="x")
    assert recorder.token_calls == 2 and recorder.batch_calls == 2  # 仅重试一次
    conn.close()


def test_biz_falls_back_to_r2_alias(settings):
    settings = settings.model_copy(update={"wechat_official_biz": ""})
    conn = connect(settings.db_path)
    init_db(conn)
    # R2 先同步过同别名账号（任意一篇带 biz 的文章即可解析）
    upsert_article(conn, ArticleRecord(
        biz=BIZ, mid="9999", idx=1, sn="old-sn", account_alias="自有号",
        title="R2 旧文",
    ))
    recorder = _CallRecorder()
    with _client(settings, recorder) as client:
        report = sync_official_articles(conn, settings, client,
                                        account_alias="自有号")
    assert report.enabled and report.biz == BIZ and report.inserted == 25
    conn.close()


def test_merge_source_normalizes_order_and_is_idempotent():
    from mp_archiver.db.database import merge_source

    assert merge_source("exporter", "official_api") == "exporter+official_api"
    # 到达顺序相反也产生相同规范形态
    assert merge_source("official_api", "exporter") == "exporter+official_api"
    # 精确成员判断：api 不得误命中 official_api
    assert merge_source("official_api", "api") == "api+official_api"
    # 重复幂等
    assert merge_source("exporter+official_api", "exporter") == \
        "exporter+official_api"


# ---------------- CLI 退出码（fake client，不触网） ----------------

class _FakeResp:
    def __init__(self, payload: object) -> None:
        self._payload = payload

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def _install_fake_client(monkeypatch, *, token_payload, batch_payload=None):
    from mp_archiver import cli as cli_module

    class _FakeClient:
        def __init__(self, settings) -> None:
            self.settings = settings

        def __enter__(self):
            return self

        def __exit__(self, *exc) -> bool:
            return False

        def get(self, url, params=None):
            return _FakeResp(token_payload)

        def post(self, url, params=None, json=None):
            return _FakeResp(batch_payload if batch_payload is not None
                             else {"errcode": 0, "total_count": 0, "item": []})

    monkeypatch.setattr(cli_module, "RateLimitedClient", _FakeClient)


def _cli_env(monkeypatch, tmp_path):
    from mp_archiver import cli as cli_module

    cli_module.get_settings.cache_clear()  # get_settings 为进程级 lru_cache
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_APP_ID", "wxapp")
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_APP_SECRET", "sek")
    monkeypatch.setenv("MP_ARCHIVER_DB_PATH", str(tmp_path / "cli.db"))
    monkeypatch.setenv("MP_ARCHIVER_ARCHIVE_ROOT", str(tmp_path / "arc"))
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_OFFICIAL_BIZ", BIZ)
    monkeypatch.setenv("MP_ARCHIVER_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MIN", "0")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MAX", "0")


def test_cli_48001_exits_zero(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install_fake_client(
        monkeypatch,
        token_payload={"errcode": 48001, "errmsg": "api unauthorized"},
    )
    code = cli_module.main(["sync-official", "-a", "自有号"])
    out = capsys.readouterr().out
    assert code == 0 and "48001" in out


def test_cli_apiret_40164_exits_four(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install_fake_client(
        monkeypatch,
        token_payload={"access_token": "tok", "expires_in": 7200},
        batch_payload={"errcode": 40164, "errmsg": "invalid ip"},
    )
    code = cli_module.main(["sync-official", "-a", "自有号"])
    out = capsys.readouterr().out
    assert code == 4 and "40164" in out and "白名单" in out


def test_cli_missing_biz_exits_three(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    # 注意：用 setenv("") 而非 delenv——pydantic-settings 在环境变量缺失时
    # 会回退到项目根 .env 文件加载 biz，导致测试隔离失效（实测：delenv 后 biz
    # 仍为 .env 里的 MzcwMzE5NTI5NA==，biz 检查通过，进而发起 token 请求）。
    # setenv("") 让环境变量存在且为空，pydantic 直接取空串，不回退到 .env。
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_OFFICIAL_BIZ", "")
    called = {"n": 0}

    class _ProbeClient:
        def __init__(self, settings) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc) -> bool:
            return False

        def get(self, *a, **k):
            called["n"] += 1
            raise AssertionError("biz 缺失时不应发起任何请求")

        post = get

    monkeypatch.setattr(cli_module, "RateLimitedClient", _ProbeClient)

    code = cli_module.main(["sync-official", "-a", "未知号"])
    assert code == 3 and called["n"] == 0


def test_cli_non_json_exits_four(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install_fake_client(
        monkeypatch,
        token_payload=json.JSONDecodeError("expect value", "<html>", 0),
    )
    code = cli_module.main(["sync-official", "-a", "自有号"])
    out = capsys.readouterr().out
    assert code == 4 and "非 JSON" in out


def test_cli_blank_secret_skips_without_requests(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_APP_SECRET", "   ")

    class _ProbeClient:
        def __init__(self, settings) -> None:
            raise AssertionError("空白 secret 不应构造客户端")

    monkeypatch.setattr(cli_module, "RateLimitedClient", _ProbeClient)
    code = cli_module.main(["sync-official", "-a", "自有号"])
    assert code == 0 and "[skip]" in capsys.readouterr().out
