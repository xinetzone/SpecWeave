"""评论与互动指标采集测试（Task 7 / TR-7.2，MockTransport 无真实网络）。

覆盖：响应解析（JSON/JSONP/回复嵌套/翻页）、凭证缺失与失效降级、
成功入库与重跑幂等、HTTP 错误记 failed 但不外抛。
"""

import json

import httpx
import pytest
from pydantic import SecretStr

from mp_archiver.config import Settings
from mp_archiver.core import comment_sync
from mp_archiver.core.comment_sync import (
    parse_comments,
    parse_metrics,
    sync_article_interactions,
)
from mp_archiver.core.credentials import load_web_credentials
from mp_archiver.db import connect, init_db
from mp_archiver.exceptions import CredentialExpiredError, PayloadError
from mp_archiver.http_client import RateLimitedClient

COMMENTS_PAGE1 = {
    "base_resp": {"ret": 0, "errmsg": "ok"},
    "elected_comment_total_cnt": 2,
    "elected_comment": [
        {
            "content_id": "10001",
            "nick_name": "读者甲",
            "content": "好文收藏",
            "like_num": 5,
            "create_time": 1710000000,
            "reply": {
                "elected_reply": [
                    {
                        "reply_id": "201",
                        "nick_name": "作者",
                        "content": "感谢支持",
                        "like_num": 1,
                        "create_time": 1710000300,
                    }
                ]
            },
        }
    ],
}
COMMENTS_PAGE2 = {
    "base_resp": {"ret": 0},
    "elected_comment_total_cnt": 2,
    "elected_comment": [
        {
            "content_id": "10002",
            "nick_name": "读者乙",
            "content": "催更",
            "like_num": 0,
            "create_time": 1710001000,
            "reply": {"elected_reply": []},
        }
    ],
}
METRICS_PAYLOAD = {
    "base_resp": {"ret": 0},
    "appmsgstat": {
        "read_num": 1234,
        "old_like_num": 3,
        "like_num": 12,
        "share_num": 4,
        "comment_num": 2,
    },
}
EXPIRED_PAYLOAD = {"base_resp": {"ret": 200003, "errmsg": "invalid csrf token"}}


def test_parse_comments_with_replies_and_total():
    entries, total = parse_comments(COMMENTS_PAGE1)
    assert total == 2
    assert len(entries) == 2
    parent, reply = entries
    assert parent.comment_id == "10001"
    assert parent.user_name == "读者甲"
    assert parent.like_count == 5
    assert parent.create_time and parent.create_time.endswith("+00:00")
    assert reply.comment_id == "10001#r201"
    assert reply.user_name == "作者"
    assert reply.content == "感谢支持"


def test_parse_comments_accepts_jsonp_wrapper():
    wrapped = "window.cb(" + json.dumps(COMMENTS_PAGE2, ensure_ascii=False) + ")"
    entries, total = parse_comments(comment_sync._loads_json_lenient(wrapped))
    assert total == 2
    assert entries[0].comment_id == "10002"


def test_parse_comments_credential_ret_raises():
    with pytest.raises(CredentialExpiredError):
        parse_comments(EXPIRED_PAYLOAD)


def test_parse_metrics_ok_and_missing_block():
    snapshot = parse_metrics(METRICS_PAYLOAD)
    assert (snapshot.read_count, snapshot.like_count, snapshot.old_like_count,
            snapshot.share_count, snapshot.comment_count) == (1234, 12, 3, 4, 2)
    with pytest.raises(PayloadError):
        parse_metrics({"base_resp": {"ret": 0}})


def test_load_web_credentials_required_fields(tmp_path):
    base = Settings(
        db_path=tmp_path / "a.db", archive_root=tmp_path / "arc",
        request_delay_min=0.0, request_delay_max=0.0,
    )
    assert load_web_credentials(base) is None
    enabled = base.model_copy(update={
        "wechat_appmsg_token": SecretStr("tok"),
        "wechat_pass_ticket": SecretStr("pt"),
    })
    creds = load_web_credentials(enabled)
    assert creds is not None and creds.appmsg_token == "tok"


@pytest.fixture
def env(tmp_path, monkeypatch):
    settings = Settings(
        request_delay_min=0.0,
        request_delay_max=0.0,
        max_retries=0,
        db_path=tmp_path / "data" / "archive.db",
        archive_root=tmp_path / "archive",
    )
    conn = connect(settings.db_path)
    init_db(conn)
    conn.execute(
        """
        INSERT INTO articles (biz, mid, idx, sn, account_alias, title, status, url)
        VALUES ('BIZ==', '2200', 1, 'sn2200', '意识食谱', '互动文章', 'pending',
                'https://mp.weixin.qq.com/s?__biz=BIZ&mid=2200&idx=1&sn=sn2200')
        """
    )
    conn.commit()
    article = conn.execute("SELECT * FROM articles WHERE sn='sn2200'").fetchone()
    yield conn, settings, article
    conn.close()


def _client(settings, handler):
    return RateLimitedClient(settings, transport=httpx.MockTransport(handler),
                             sleeper=lambda _: None)


def test_sync_disabled_writes_nothing(env):
    conn, settings, article = env
    with _client(settings, lambda r: pytest.fail("不应发起请求")) as client:
        outcome = sync_article_interactions(conn, settings, client, article)
    assert outcome.state == "disabled"
    assert conn.execute("SELECT COUNT(*) AS n FROM metrics").fetchone()["n"] == 0
    assert conn.execute("SELECT COUNT(*) AS n FROM comments").fetchone()["n"] == 0


def test_sync_without_credentials_marks_skipped(env):
    conn, settings, article = env
    settings = settings.model_copy(update={"fetch_metrics": True})
    with _client(settings, lambda r: pytest.fail("不应发起请求")) as client:
        outcome = sync_article_interactions(conn, settings, client, article)
    assert outcome.state == "skipped_no_credential"
    row = conn.execute("SELECT * FROM metrics").fetchone()
    assert row["status"] == "skipped_no_credential"
    assert "missing_credentials" in row["fail_reason"]


def _paging_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/mp/appmsg_comment":
        offset = request.url.params.get("offset", "0")
        page = COMMENTS_PAGE1 if offset == "0" else COMMENTS_PAGE2
        return httpx.Response(200, json=page)
    if request.url.path == "/mp/getappmsgext":
        return httpx.Response(200, json=METRICS_PAYLOAD)
    return httpx.Response(404)


def test_sync_success_persists_comments_metrics_and_idempotent(env, monkeypatch):
    conn, settings, article = env
    settings = settings.model_copy(update={
        "fetch_metrics": True,
        "wechat_appmsg_token": SecretStr("tok"),
        "wechat_pass_ticket": SecretStr("pt"),
    })
    monkeypatch.setattr(comment_sync, "COMMENT_PAGE_SIZE", 1)
    with _client(settings, _paging_handler) as client:
        outcome = sync_article_interactions(conn, settings, client, article)

    assert outcome.state == "collected"
    assert outcome.comments_written == 3  # 两页：1 主评论+1 回复，第二页 1 主评论
    comments = conn.execute(
        "SELECT comment_id FROM comments ORDER BY comment_id"
    ).fetchall()
    assert [r["comment_id"] for r in comments] == [
        "10001", "10001#r201", "10002"
    ]
    metric = conn.execute("SELECT * FROM metrics").fetchone()
    assert metric["status"] == "collected"
    assert metric["read_count"] == 1234
    assert metric["comment_count"] == 2  # 以平台 appmsgstat 为准
    assert metric["raw_json"]

    # 重跑：评论 upsert 不翻倍；metrics 追加第二行快照
    with _client(settings, _paging_handler) as client:
        sync_article_interactions(conn, settings, client, article)
    assert conn.execute("SELECT COUNT(*) AS n FROM comments").fetchone()["n"] == 3
    assert conn.execute("SELECT COUNT(*) AS n FROM metrics").fetchone()["n"] == 2


def _expired_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=EXPIRED_PAYLOAD)


def test_sync_expired_credentials_marks_skipped(env):
    conn, settings, article = env
    settings = settings.model_copy(update={
        "fetch_metrics": True,
        "wechat_appmsg_token": SecretStr("stale"),
        "wechat_pass_ticket": SecretStr("stale"),
    })
    with _client(settings, _expired_handler) as client:
        outcome = sync_article_interactions(conn, settings, client, article)
    assert outcome.state == "skipped_no_credential"
    row = conn.execute("SELECT * FROM metrics").fetchone()
    assert row["status"] == "skipped_no_credential"
    assert "credential_expired" in row["fail_reason"]


def test_fetch_batch_without_credentials_downgrades_gracefully(env):
    """TR-7.2：开启开关但无凭证时，正文正常归档，互动全部 skipped 且无异常。"""
    from mp_archiver.core.article_archive import fetch_articles

    conn, settings, _ = env
    settings = settings.model_copy(update={"fetch_metrics": True})
    plain_page = (
        '<html><body><div id="img-content"><div id="js_content">'
        "<p>纯文字正文</p></div></div></body></html>"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params.get("sn") == "sn2200":
            return httpx.Response(200, html=plain_page)
        return httpx.Response(404)

    with _client(settings, handler) as client:
        report = fetch_articles(
            conn, client, "意识食谱", settings.archive_root,
            include_failed=True, settings=settings,
        )

    assert report.downloaded == 1 and report.failed == 0
    assert report.interactions_skipped == 1
    assert report.interactions_collected == 0
    row = conn.execute(
        "SELECT status FROM articles WHERE sn='sn2200'"
    ).fetchone()
    assert row["status"] == "downloaded"  # 缺凭证不影响文章状态


def _http_error_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(500, text="server error")


def test_sync_http_error_marks_failed_but_does_not_raise(env):
    conn, settings, article = env
    settings = settings.model_copy(update={
        "fetch_metrics": True,
        "wechat_appmsg_token": SecretStr("tok"),
        "wechat_pass_ticket": SecretStr("pt"),
    })
    with _client(settings, _http_error_handler) as client:
        outcome = sync_article_interactions(conn, settings, client, article)
    assert outcome.state == "failed"
    row = conn.execute("SELECT * FROM metrics").fetchone()
    assert row["status"] == "failed" and row["fail_reason"]
