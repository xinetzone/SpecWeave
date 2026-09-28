"""Task 12 / TR-12.1 故障注入演练剧本（全程 MockTransport，不触网）。

六类剧本 + 续跑恢复：

1. 403：请求级指数退避（退避日志可见）→ 账号级风控熔断，后续文章零请求；
2. 验证码/环境异常页（含空 js_content 变体）：显式风控失败、无空壳归档、熔断；
3. 超时：退避后按连续传输故障阈值熔断；业务失败会重置连续计数，不误熔断；
4. 单篇 404：不重试、failed 隔离、批次继续、失败清单与成功/失败/跳过分类计数；
5. 媒体链接失效：图片 404 / 语音 500 登记 media 表与 metadata 例外表，文章仍 downloaded；
6. 凭证过期：adapter 403 → CredentialExpiredError；列表中途凭证失效 → 凭证状态落库 expired；
7. 续跑恢复（AC-8）：熔断现场保留 → 恢复后 pending 续跑 → --include-failed 补齐，无重复目录。

复现并留存演练日志（TR-12.1 证据）：

    pytest tests/test_fault_injection.py -s -o log_cli=true --log-cli-level=WARNING
"""

import json
import logging

import httpx
import pytest

from mp_archiver.adapters.base import AccountRef
from mp_archiver.adapters.wechat_download_api import WechatDownloadApiAdapter
from mp_archiver.adapters.wechat_payload import CredentialExpiredError
from mp_archiver.config import Settings
from mp_archiver.core.article_archive import fetch_articles
from mp_archiver.core.list_sync import sync_article_list
from mp_archiver.db import connect, init_db
from mp_archiver.http_client import RateLimitedClient
from mp_archiver.models import CredentialStatus
from mp_archiver.models import MediaStatus

ALIAS = "意识食谱"
BIZ = "BIZ=="
SNS = ("a1", "a2", "a3", "a4", "a5")


def _ok_page(sn: str) -> str:
    return (
        "<html><head><title>文章</title></head><body>"
        '<div id="img-content"><div id="js_content">'
        f"<p>正文段落 {sn}。</p></div></div></body></html>"
    )


# 风控页变体：命中风控文案且含空正文容器——
# G3 回归：旧实现对此页不报错，会把空壳归档并误标 downloaded。
RISK_PAGE_EMPTY = (
    "<html><body>环境异常，去验证，完成验证后即可继续访问"
    '<div id="js_content"></div></body></html>'
)
# P1-1 回归：风控词恰好出现在一篇**有实质正文**的正常文章里（结构判定不得误杀）
RISK_WORDS_IN_BODY = (
    "<html><body><div id='img-content'><div id='js_content'>"
    "<p>登录时若提示环境异常不要慌：我们去验证页面按指引操作，"
    "完成验证后即可继续访问公众号后台。这是一篇安全科普正文。</p>"
    "</div></div></body></html>"
)
# P2-1 回归：无正文容器、也不含任何已知标记的未知拦截页（疑似改版验证页）
UNKNOWN_GUARD_PAGE = (
    "<html><body><div>安全验证中，请稍候片刻，系统正在检测访问环境</div></body></html>"
)
DELETED_PAGE = "<html><body><div>该内容已被发布者删除</div></body></html>"

PNG_BYTES = b"\x89PNG\r\n\x1a\n-drill-png-"
PIC_OK = "https://mmbiz.qpic.cn/mmbiz_png/ok1?wx_fmt=png"
PIC_BAD = "https://mmbiz.qpic.cn/mmbiz_png/dead1?wx_fmt=png"


def _media_page() -> str:
    return (
        "<html><body><div id='img-content'><div id='js_content'>"
        f'<img data-src="{PIC_OK}"/>'
        f'<img data-src="{PIC_BAD}"/>'
        '<mpvoice voice_encode_fileid="vdead" name="失效语音"></mpvoice>'
        "</div></div></body></html>"
    )


def _article_url(n: int, sn: str) -> str:
    return f"http://mp.weixin.qq.com/s?__biz=BIZ&mid={n}&idx=1&sn={sn}"


class ScriptedHandler:
    """按 sn 路由的假服务。

    routes 值：``("http", 状态码)`` / ``("html", 页面文本)`` /
    ``("raise", 异常实例)``；未登记 sn 一律 404（模拟单篇链接不存在）。
    """

    def __init__(self, routes: dict):
        self.routes = routes
        self.article_calls: list[str] = []
        self.media_calls: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        host = request.url.host
        if host == "mmbiz.qpic.cn":
            self.media_calls.append(str(request.url))
            if request.url.path.endswith("/ok1"):
                return httpx.Response(
                    200, content=PNG_BYTES,
                    headers={"content-type": "image/png"},
                )
            return httpx.Response(404, text="image dead")
        if host == "res.wx.qq.com":
            self.media_calls.append(str(request.url))
            return httpx.Response(500, text="voice dead")

        sn = request.url.params.get("sn", "")
        self.article_calls.append(sn)
        kind, payload = self.routes.get(sn, ("http", 404))
        if kind == "raise":
            raise payload
        if kind == "html":
            return httpx.Response(200, html=payload)
        return httpx.Response(payload, text=f"http-{payload}")


def _build_env(tmp_path, handler, *, max_retries=2, threshold=2):
    settings = Settings(
        _env_file=None,
        request_delay_min=0.0,
        request_delay_max=0.0,
        max_retries=max_retries,
        backoff_base=2.0,
        backoff_cap=60.0,
        db_path=tmp_path / "data" / "a.db",
        archive_root=tmp_path / "archive",
        transport_abort_threshold=threshold,
    )
    conn = connect(settings.db_path)
    init_db(conn)
    sleeps: list[float] = []
    client = RateLimitedClient(
        settings,
        transport=httpx.MockTransport(handler),
        sleeper=sleeps.append,
        rng=lambda a, b: 0.0,  # 去抖动：退避秒数确定
    )
    return conn, client, settings, sleeps


def _insert(conn, n: int, sn: str, *, status: str = "pending") -> None:
    conn.execute(
        """
        INSERT INTO articles
            (biz, mid, idx, sn, account_alias, title, author, publish_time,
             url, digest, status)
        VALUES (?, ?, 1, ?, ?, ?, '作者', ?, ?, '摘要', ?)
        """,
        (
            BIZ, str(n), sn, ALIAS, f"标题-{sn}",
            f"2024-03-{n:02d}T08:00:00+00:00",
            _article_url(n, sn), status,
        ),
    )
    conn.commit()


def _status_counts(conn) -> dict:
    rows = conn.execute(
        "SELECT status, COUNT(*) AS c FROM articles GROUP BY status"
    ).fetchall()
    return {r["status"]: r["c"] for r in rows}


# ---- 剧本①：文章页 403 → 退避可见 + 风控熔断 -----------------------------

def test_drill_403_backoff_logged_then_risk_abort(tmp_path, caplog):
    handler = ScriptedHandler({sn: ("http", 403) for sn in SNS})
    conn, client, settings, sleeps = _build_env(
        tmp_path, handler, max_retries=2
    )
    for i, sn in enumerate(SNS, start=1):
        _insert(conn, i, sn)

    caplog.set_level(logging.WARNING, logger="mp_archiver")
    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    # 分类计数：只尝试了第一篇；熔断后其余 4 篇零请求（无猛打）
    assert (report.total, report.downloaded, report.skipped, report.failed) == (
        5, 0, 0, 1,
    )
    assert report.aborted is True
    assert report.pending_left == 4
    assert len(handler.article_calls) == 3  # 首篇 1 次请求 + 2 次重试
    assert sleeps == [2.0, 4.0]  # 指数退避 base*2^0、base*2^1
    assert "重试退避" in caplog.text and "风控熔断" in caplog.text
    # 现场保留：1 篇 failed（原因可查），4 篇仍 pending
    assert _status_counts(conn) == {"failed": 1, "pending": 4}
    reason = conn.execute(
        "SELECT fail_reason FROM articles WHERE sn = 'a1'"
    ).fetchone()["fail_reason"]
    assert "risk_abort" in reason and "403" in reason


# ---- 剧本②：验证码/环境异常页（含空容器变体）→ 立即熔断、无空壳 -----------

def test_drill_captcha_page_aborts_without_empty_archive(tmp_path, caplog):
    handler = ScriptedHandler({sn: ("html", RISK_PAGE_EMPTY) for sn in SNS})
    conn, client, settings, sleeps = _build_env(tmp_path, handler)
    for i, sn in enumerate(SNS, start=1):
        _insert(conn, i, sn)

    caplog.set_level(logging.WARNING, logger="mp_archiver")
    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is True
    assert report.failed == 1 and report.pending_left == 4
    assert handler.article_calls == ["a1"]  # 200 不重试，仅 1 次请求即熔断
    assert sleeps == []
    assert "风控" in report.abort_reason
    # G3：任何文章都不得落盘归档产物（空壳 downloaded 回归）
    html_files = (
        list(settings.archive_root.rglob("article.html"))
        if settings.archive_root.exists()
        else []
    )
    assert html_files == []
    assert _status_counts(conn) == {"failed": 1, "pending": 4}


# ---- 剧本③a：超时 → 退避 + 连续传输故障熔断 -------------------------------

def test_drill_timeout_consecutive_transport_abort(tmp_path, caplog):
    handler = ScriptedHandler(
        {sn: ("raise", httpx.ReadTimeout("simulated slow")) for sn in SNS}
    )
    conn, client, settings, sleeps = _build_env(
        tmp_path, handler, max_retries=1, threshold=2
    )
    for i, sn in enumerate(SNS, start=1):
        _insert(conn, i, sn)

    caplog.set_level(logging.WARNING, logger="mp_archiver")
    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is True
    assert report.failed == 2 and report.pending_left == 3
    assert len(handler.article_calls) == 4  # 2 篇 ×（1 请求 + 1 重试）
    # 每篇的重试计数都从 attempt=0 重新起算：base*2^0=2.0（两篇各一次）
    assert sleeps == [2.0, 2.0]
    assert "传输熔断" in caplog.text
    assert _status_counts(conn) == {"failed": 2, "pending": 3}


# ---- 剧本③b：业务失败重置传输连续计数，偶发超时不熔断 ----------------------

def test_drill_business_failure_resets_transport_streak(tmp_path):
    # 处理顺序按发布时间升序：超时 → 404 → 超时 → 成功 → 成功
    routes = {
        "a1": ("raise", httpx.ConnectError("network down")),
        "a2": ("http", 404),
        "a3": ("raise", httpx.ReadTimeout("slow again")),
        "a4": ("html", _ok_page("a4")),
        "a5": ("html", _ok_page("a5")),
    }
    handler = ScriptedHandler(routes)
    conn, client, settings, _ = _build_env(
        tmp_path, handler, max_retries=1, threshold=2
    )
    for i, sn in enumerate(SNS, start=1):
        _insert(conn, i, sn)

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is False
    assert report.downloaded == 2 and report.failed == 3
    # 两次超时被 404/成功隔开，连续计数始终为 1：批次完整跑完
    assert len(report.items) == 5


# ---- 剧本④：单篇 404 隔离 + 批次分类计数 + 失败清单 ------------------------

def test_drill_single_404_isolated_batch_continues(tmp_path):
    routes = {sn: ("html", _ok_page(sn)) for sn in SNS}
    routes["a2"] = ("http", 404)
    handler = ScriptedHandler(routes)
    conn, client, settings, sleeps = _build_env(tmp_path, handler)
    for i, sn in enumerate(SNS, start=1):
        _insert(conn, i, sn)

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is False
    assert (report.total, report.downloaded, report.failed) == (5, 4, 1)
    assert len(handler.article_calls) == 5  # 每篇恰好 1 次请求
    assert sleeps == []  # 404 不重试
    failed_items = [i for i in report.items if i.state == "failed"]
    assert len(failed_items) == 1
    assert failed_items[0].article_id == 2 and "404" in failed_items[0].error
    assert _status_counts(conn) == {"downloaded": 4, "failed": 1}


def test_drill_batch_classification_counts_success_failed_skipped(tmp_path):
    """删除页/404/正常混合：批次给出成功/失败/跳过三类准确计数。"""
    handler = ScriptedHandler({
        "a1": ("html", DELETED_PAGE),
        "a2": ("http", 404),
        "a3": ("html", _ok_page("a3")),
    })
    conn, client, settings, _ = _build_env(tmp_path, handler)
    for i, sn in enumerate(("a1", "a2", "a3"), start=1):
        _insert(conn, i, sn)

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is False
    assert (report.downloaded, report.skipped, report.failed) == (1, 1, 1)
    assert [i.state for i in report.items] == ["skipped", "failed", "downloaded"]


# ---- 剧本⑤：媒体链接失效 → 登记例外表，不阻断文章 --------------------------

def test_drill_dead_media_links_registered_article_still_downloaded(tmp_path):
    handler = ScriptedHandler({"a1": ("html", _media_page())})
    conn, client, settings, _ = _build_env(
        tmp_path, handler, max_retries=0
    )
    _insert(conn, 1, "a1")

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is False
    assert report.downloaded == 1 and report.image_failures == 1

    # media 表：1 图成功、1 图失败、1 语音失败（状态均可查）
    rows = conn.execute(
        "SELECT media_type, status, COUNT(*) AS c FROM media GROUP BY 1, 2"
    ).fetchall()
    counts = {(r["media_type"], r["status"]): r["c"] for r in rows}
    assert counts[("image", MediaStatus.DOWNLOADED.value)] == 1
    assert counts[("image", MediaStatus.FAILED.value)] == 1
    assert counts[("audio", MediaStatus.FAILED.value)] == 1

    # metadata.json 例外表保留原始 URL，四件套仍齐全
    meta_path = next(settings.archive_root.rglob("metadata.json"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    bad_images = [item for item in meta["images"] if not item["ok"]]
    assert len(bad_images) == 1 and bad_images[0]["url"] == PIC_BAD
    bad_audio = [
        item for item in meta["rich_media"]
        if item["type"] == "audio" and not item["ok"]
    ]
    assert len(bad_audio) == 1
    assert (meta_path.parent / "article.html").exists()


# ---- 剧本⑥：凭证过期 → 异常上抛 + 凭证状态落库 -----------------------------

def test_drill_credential_expired_adapter_and_watermark(tmp_path):
    # ⑥a 采集服务 OpenAPI 返回 403：不重试（max_retries=0）即判定登录态失效
    settings = Settings(
        _env_file=None, max_retries=0,
        request_delay_min=0.0, request_delay_max=0.0,
    )
    calls: list[httpx.Request] = []

    def forbidden(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(403, text="forbidden")

    with RateLimitedClient(
        settings, transport=httpx.MockTransport(forbidden)
    ) as client:
        with pytest.raises(CredentialExpiredError):
            WechatDownloadApiAdapter.build(
                client, base_url="http://collector.local"
            )
    assert len(calls) == 1

    # ⑥b 列表翻页中途凭证失效：先落库 expired 再上抛，现场保留
    conn = connect(tmp_path / "cred.db")
    init_db(conn)

    class ExpiredAdapter:
        def resolve_account(self, name):
            return AccountRef(nickname=ALIAS, fakeid="1", biz=BIZ)

        def fetch_history_page(self, account, offset):
            raise CredentialExpiredError(200013, "session expired")

    with pytest.raises(CredentialExpiredError):
        sync_article_list(conn, ExpiredAdapter(), name=ALIAS)
    row = conn.execute(
        "SELECT credential_status FROM sync_state WHERE account_biz = ?",
        (BIZ,),
    ).fetchone()
    assert row["credential_status"] == CredentialStatus.EXPIRED.value
    conn.close()


# ---- 剧本⑦：熔断后断点续跑，无重复文章/重复文件（AC-8） --------------------

def test_drill_resume_after_abort_is_idempotent(tmp_path):
    # 第一批：全站 403，首篇即熔断（重试预算设 0，加快演练）
    conn, client, settings, _ = _build_env(
        tmp_path, ScriptedHandler({sn: ("http", 403) for sn in SNS}),
        max_retries=0,
    )
    for i, sn in enumerate(SNS, start=1):
        _insert(conn, i, sn)
    report1 = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )
    client.close()
    assert report1.aborted is True and report1.failed == 1
    assert _status_counts(conn) == {"failed": 1, "pending": 4}

    # 第二批：故障解除；普通重跑只续采 pending，失败篇不被触及
    handler2 = ScriptedHandler({sn: ("html", _ok_page(sn)) for sn in SNS})
    client2 = RateLimitedClient(
        settings, transport=httpx.MockTransport(handler2),
        sleeper=lambda _: None, rng=lambda a, b: 0.0,
    )
    report2 = fetch_articles(
        conn, client2, ALIAS, settings.archive_root, settings=settings
    )
    assert report2.aborted is False
    assert report2.downloaded == 4 and report2.failed == 0
    assert set(handler2.article_calls) == {"a2", "a3", "a4", "a5"}
    client2.close()

    # 第三批：--include-failed 补齐熔断篇
    handler3 = ScriptedHandler({sn: ("html", _ok_page(sn)) for sn in SNS})
    client3 = RateLimitedClient(
        settings, transport=httpx.MockTransport(handler3),
        sleeper=lambda _: None, rng=lambda a, b: 0.0,
    )
    report3 = fetch_articles(
        conn, client3, ALIAS, settings.archive_root,
        include_failed=True, settings=settings,
    )
    assert report3.total == 1 and report3.downloaded == 1
    assert report3.failed == 0
    client3.close()

    # 最终：5 篇全部 downloaded；每篇恰好一个目录、一份 article.html（无重复）
    assert _status_counts(conn) == {"downloaded": 5}
    html_files = list(settings.archive_root.rglob("article.html"))
    assert len(html_files) == 5
    article_dirs = {p.parent for p in html_files}
    assert len(article_dirs) == 5


# ---- V 阶段回归①：风控词在正常正文中不得误熔断（P1-1） --------------------

def test_drill_risk_words_in_substantial_body_not_aborted(tmp_path):
    handler = ScriptedHandler({
        "a1": ("html", RISK_WORDS_IN_BODY),
        "a2": ("html", _ok_page("a2")),
        "a3": ("html", _ok_page("a3")),
    })
    conn, client, settings, _ = _build_env(tmp_path, handler)
    for i, sn in enumerate(("a1", "a2", "a3"), start=1):
        _insert(conn, i, sn)

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is False
    assert report.downloaded == 3 and report.failed == 0
    assert handler.article_calls == ["a1", "a2", "a3"]
    assert _status_counts(conn) == {"downloaded": 3}


# ---- V 阶段回归②：未知拦截页变体按风控熔断（P2-1） ------------------------

def test_drill_unknown_guard_page_without_marker_aborts(tmp_path):
    handler = ScriptedHandler({sn: ("html", UNKNOWN_GUARD_PAGE) for sn in SNS})
    conn, client, settings, _ = _build_env(tmp_path, handler)
    for i, sn in enumerate(SNS, start=1):
        _insert(conn, i, sn)

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is True
    assert report.failed == 1 and report.pending_left == 4
    assert handler.article_calls == ["a1"]
    html_files = (
        list(settings.archive_root.rglob("article.html"))
        if settings.archive_root.exists()
        else []
    )
    assert html_files == []
    assert _status_counts(conn) == {"failed": 1, "pending": 4}


# ---- V 阶段回归③：文章页 5xx 连续故障熔断，不再逐篇放大请求（P1-2） -------

def test_drill_5xx_consecutive_aborts_like_transport(tmp_path):
    handler = ScriptedHandler({sn: ("http", 500) for sn in SNS})
    conn, client, settings, sleeps = _build_env(
        tmp_path, handler, max_retries=1, threshold=2
    )
    for i, sn in enumerate(SNS, start=1):
        _insert(conn, i, sn)

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    assert report.aborted is True
    assert report.failed == 2 and report.pending_left == 3
    # 2 篇各吃满（1 请求 + 1 重试）后熔断；后 3 篇零请求，绝不逐篇放大
    assert len(handler.article_calls) == 4
    assert sleeps == [2.0, 2.0]
    assert "500" in report.abort_reason
    reason = conn.execute(
        "SELECT fail_reason FROM articles WHERE sn = 'a1'"
    ).fetchone()["fail_reason"]
    assert reason.startswith("transport: [transport] 文章页 HTTP 500")
    assert _status_counts(conn) == {"failed": 2, "pending": 3}


def test_drill_single_5xx_reset_by_success_no_abort(tmp_path):
    handler = ScriptedHandler({
        "a1": ("http", 500),
        "a2": ("html", _ok_page("a2")),
    })
    conn, client, settings, _ = _build_env(
        tmp_path, handler, max_retries=1, threshold=2
    )
    for i, sn in enumerate(("a1", "a2"), start=1):
        _insert(conn, i, sn)

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root, settings=settings
    )

    # 单次 5xx 后紧跟成功篇：连续计数归零，不熔断、批次跑完
    assert report.aborted is False
    assert report.failed == 1 and report.downloaded == 1
    assert handler.article_calls == ["a1", "a1", "a2"]


# ---- V 阶段回归④：--limit 熔断时横幅数据可区分本批/库内剩余（P2-2） -------

def test_drill_limit_abort_reports_full_pending_scale(tmp_path):
    handler = ScriptedHandler({f"a{i}": ("http", 403) for i in range(1, 11)})
    conn, client, settings, _ = _build_env(
        tmp_path, handler, max_retries=0
    )
    for i in range(1, 11):
        _insert(conn, i, f"a{i}")

    report = fetch_articles(
        conn, client, ALIAS, settings.archive_root,
        limit=3, settings=settings,
    )

    assert report.aborted is True
    assert report.total == 3
    assert report.pending_left == 2       # 本批已选未触
    assert report.pending_in_account == 9  # 库内真实 pending 总量


# ---- CLI 接线：熔断时退出码 4 并打印续跑提示 -------------------------------

def test_drill_fetch_cli_abort_returns_exit_4(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    cli_module.get_settings.cache_clear()
    monkeypatch.setenv("MP_ARCHIVER_EXPORTER_TOKEN", "")
    monkeypatch.setenv("MP_ARCHIVER_DB_PATH", str(tmp_path / "cli.db"))
    monkeypatch.setenv("MP_ARCHIVER_ARCHIVE_ROOT", str(tmp_path / "arc"))
    monkeypatch.setenv("MP_ARCHIVER_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MIN", "0")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MAX", "0")
    monkeypatch.setenv("MP_ARCHIVER_MAX_RETRIES", "1")

    settings = cli_module.get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    for i, sn in enumerate(("a1", "a2"), start=1):
        conn.execute(
            """
            INSERT INTO articles
                (biz, mid, idx, sn, account_alias, title, author,
                 publish_time, url, digest, status)
            VALUES (?, ?, 1, ?, ?, ?, '作者', ?, ?, '摘要', 'pending')
            """,
            (BIZ, str(i), sn, ALIAS, f"标题-{sn}",
             f"2024-03-{i:02d}T08:00:00+00:00", _article_url(i, sn)),
        )
    conn.commit()
    conn.close()

    handler = ScriptedHandler({"a1": ("http", 403), "a2": ("http", 403)})
    client = RateLimitedClient(
        settings,
        transport=httpx.MockTransport(handler),
        sleeper=lambda _: None,
        rng=lambda a, b: 0.0,
    )
    monkeypatch.setattr(cli_module, "RateLimitedClient", lambda *a, **k: client)

    code = cli_module.main(["fetch", "-a", ALIAS])
    output = capsys.readouterr().out

    assert code == 4
    assert "[abort]" in output
    assert "保持 pending" in output
