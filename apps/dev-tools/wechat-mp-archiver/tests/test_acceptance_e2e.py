"""Task 14 端到端验收测试：run_pipeline 全链路（MockTransport，无真实网络）。

以本地 fixture 同时模拟两类端点——本地采集服务（列表同步）与微信公域
（正文/图片/语音/互动），串起 ``run_pipeline`` 的两阶段编排，为
AC-4/5/6/7/8 留下可复现的命令级验收证据：

- AC-4 列表完整落库：字段齐全、``biz+mid+idx`` 无重复键、已删/不可见有状态记录；
- AC-5 抽样 10 篇（含长文/图集）四件套齐全、正文图片 100% 本地化、无远程残留；
- AC-6 微信语音落盘，腾讯视频/视频号/站外音频仅登记 external 不伪造本地文件；
- AC-7 开关关闭零写入、有开关无凭证走 ``skipped_no_credential`` 且主流程成功、有凭证时
  评论与互动指标入库，并含真实 CLI ``run --full`` 退出码 0 的端到端用例；
- AC-8 重跑幂等：文章/media 记录数与归档文件集合完全不变。
"""

import json
from datetime import datetime, timezone

import httpx
import pytest
from pydantic import SecretStr

from mp_archiver.config import Settings
from mp_archiver.core.pipeline import run_pipeline
from mp_archiver.db import connect, init_db
from mp_archiver.http_client import RateLimitedClient

ALIAS = "意识食谱"
BIZ = "MzA4MjA=="
BIZ_ENCODED = "MzA4MjA%3D%3D"
SEARCH_PATH = "/api/official-accounts/search"
HISTORY_PATH = "/api/articles/history"

SPEC = {
    "paths": {
        SEARCH_PATH: {"get": {"parameters": [
            {"name": "query", "in": "query"},
            {"name": "begin", "in": "query"},
            {"name": "count", "in": "query"},
        ]}},
        HISTORY_PATH: {"get": {"parameters": [
            {"name": "__biz", "in": "query"},
            {"name": "offset", "in": "query"},
            {"name": "count", "in": "query"},
            {"name": "f", "in": "query"},
        ]}},
    }
}

PNG_BYTES = b"\x89PNG\r\n\x1a\n-fake-image-bytes-"
MP3_BYTES = b"ID3\x03\x00-fake-mp3-audio-"
DELETED_PAGE = "<html><body><div>该内容已被发布者删除</div></body></html>"

# 文章类型：normal（单图）/ long（长文）/ gallery（图集）/ media（富媒体）
KINDS = {
    "sn-a1": "normal", "sn-a2": "normal", "sn-a3": "normal", "sn-a3b": "normal",
    "sn-a4": "long", "sn-a5": "gallery", "sn-a6": "media",
    "sn-a7": "normal", "sn-a8": "normal", "sn-a9": "normal",
}
# 已删文章（正文页返回删除标记，应落 skipped 而非下载）
DELETED_SN = "sn-del"

_LONG_TEXT = "这是一段用于验证长文解析与归档完整性的较长正文内容，覆盖中文标点与换行。"


def _ts(day: int) -> int:
    return int(datetime(2024, 3, day, 8, 0, tzinfo=timezone.utc).timestamp())


def _content_url(mid: int, idx: int, sn: str) -> str:
    return (
        f"http://mp.weixin.qq.com/s?__biz={BIZ_ENCODED}&mid={mid}&idx={idx}&sn={sn}"
    )


def _info(mid: int, idx: int, sn: str, title: str, *, is_original: bool = False) -> dict:
    return {
        "title": title,
        "digest": f"{title} 摘要",
        "content_url": _content_url(mid, idx, sn),
        "cover": f"http://img.example/cover-{sn}.jpg",
        "author": "作者甲",
        "copyright_stat": 11 if is_original else 0,
    }


def _batch(mid: int, idx: int, sn: str, title: str, *, day: int,
           is_original: bool = False, multi: tuple[dict, ...] = ()) -> dict:
    info = _info(mid, idx, sn, title, is_original=is_original)
    if multi:
        info["multi_app_msg_item_list"] = list(multi)
    return {
        "comm_msg_info": {"id": mid, "type": 49, "datetime": _ts(day)},
        "app_msg_ext_info": info,
    }


def _batches() -> list[dict]:
    """10 篇可归档文章（含 1 条次条、长文、图集、富媒体）+ 1 篇已删。"""
    return [
        _batch(1001, 1, "sn-a1", "图文甲", day=1, is_original=True),
        _batch(1002, 1, "sn-a2", "图文乙", day=2),
        _batch(1003, 1, "sn-a3", "图文丙", day=3, multi=(
            _info(1003, 2, "sn-a3b", "图文丙次条"),)),
        _batch(1004, 1, "sn-a4", "长文精读", day=4),
        _batch(1005, 1, "sn-a5", "图集精选", day=5),
        _batch(1006, 1, "sn-a6", "富媒体合集", day=6),
        _batch(1007, 1, "sn-a7", "图文丁", day=7),
        _batch(1008, 1, "sn-a8", "图文戊", day=8),
        _batch(1009, 1, "sn-a9", "图文己", day=9),
        _batch(1010, 1, DELETED_SN, "已删文章", day=10),
    ]


def _history_payload(limit: int | None = None) -> dict:
    batches = _batches()
    if limit is not None:
        batches = batches[:limit]
    return {
        "ret": 0,
        "general_msg_list": json.dumps({"list": batches}),
        "next_offset": 0,
        "can_msg_continue": 0,
    }


# ---- 文章页与富媒体 ----------------------------------------------------

_MEDIA_BODY = """
  <p>正文段落。</p>
  <mpvoice voice_encode_fileid="audok" name="栏目语音" play_length="30000"></mpvoice>
  <mpvoice voice_encode_fileid="audbad" name="失败语音"></mpvoice>
  <iframe class="video_iframe"
          data-src="https://v.qq.com/txp/iframe/player.html?vid=vidxyz"></iframe>
  <mp-common-channels_video data-object_id="oid1" data-nickname="某视频号">
  </mp-common-channels_video>
  <iframe data-src="https://www.xiaoyuzhoufm.com/player/episode/ep1"></iframe>
"""


def _pic(sn: str, seq: int) -> str:
    return f"https://mmbiz.qpic.cn/mmbiz_png/{sn}-{seq}?wx_fmt=png"


def _article_page(sn: str, kind: str) -> str:
    if kind == "long":
        body = "<h2>章节标题</h2>" + "".join(
            f"<p>长文段落{i}：{_LONG_TEXT}</p>" for i in range(1, 13)
        )
    elif kind == "gallery":
        body = "<h2>图集标题</h2>" + "".join(
            f'<img data-src="{_pic(sn, i)}" src="data:image/svg+xml;base64,PH{i}"/>'
            for i in range(1, 4)
        )
    elif kind == "media":
        body = _MEDIA_BODY
    else:
        body = (
            "<h2>章节标题</h2>"
            "<p>正文段落ABC，覆盖普通文字。</p>"
            "<ul><li>要点一</li></ul>"
            "<blockquote><p>一段引用</p></blockquote>"
            f'<img data-src="{_pic(sn, 1)}" src="data:image/svg+xml;base64,PH1"/>'
        )
    return (
        f'<html><head><title>{sn}</title></head><body>'
        f'<div id="img-content"><div id="js_content" class="rich_media_content">'
        f"{body}</div></div></body></html>"
    )


SPEC_OPENAPI = "/openapi.json"

_COMMENT_PAYLOAD = {
    "base_resp": {"ret": 0},
    "elected_comment_total_cnt": 2,
    "elected_comment": [
        {
            "content_id": "c1",
            "nick_name": "读者甲",
            "content": "很有启发",
            "like_num": 7,
            "create_time": 1700000000,
            "reply": {"elected_reply": [
                {"reply_id": "r1", "nick_name": "作者甲", "content": "谢谢", "like_num": 1},
            ]},
        },
        {"content_id": "c2", "nick_name": "读者乙", "content": "已收藏", "like_num": 3},
    ],
}

_METRICS_PAYLOAD = {
    "base_resp": {"ret": 0},
    "appmsgstat": {
        "read_num": 1234, "like_num": 56, "old_like_num": 12,
        "share_num": 8, "comment_num": 2,
    },
}


def _make_handler(*, limit: int | None = None):
    """构造 MockTransport handler：按 host+path 分发四类端点。"""

    def handler(request: httpx.Request) -> httpx.Response:
        host, path = request.url.host, request.url.path
        if host in ("127.0.0.1", "localhost"):
            if path == SPEC_OPENAPI:
                return httpx.Response(200, json=SPEC)
            if path == SEARCH_PATH:
                return httpx.Response(200, json={
                    "base_resp": {"ret": 0},
                    "list": [{"fakeid": 998877, "nickname": ALIAS,
                              "alias": "mindfood", "__biz": BIZ}],
                })
            if path == HISTORY_PATH:
                return httpx.Response(200, json=_history_payload(limit))
            return httpx.Response(404)
        if host == "mmbiz.qpic.cn":
            return httpx.Response(200, content=PNG_BYTES,
                                  headers={"content-type": "image/png"})
        if host == "res.wx.qq.com":
            if request.url.params.get("mediaid") == "audok":
                return httpx.Response(200, content=MP3_BYTES,
                                      headers={"content-type": "audio/mpeg"})
            return httpx.Response(500, text="voice error")
        if host == "mp.weixin.qq.com":
            if path == "/mp/appmsg_comment":
                return httpx.Response(200, json=_COMMENT_PAYLOAD)
            if path == "/mp/getappmsgext":
                return httpx.Response(200, json=_METRICS_PAYLOAD)
            if path == "/s":
                sn = request.url.params.get("sn", "")
                if sn == DELETED_SN:
                    return httpx.Response(200, html=DELETED_PAGE)
                kind = KINDS.get(sn)
                if kind is None:
                    return httpx.Response(404, text="unknown sn")
                return httpx.Response(200, html=_article_page(sn, kind))
            return httpx.Response(404)
        return httpx.Response(404)

    return handler


def _client_factory(handler):
    """返回 run_pipeline 所需的 client_factory（注入假客户端，零真实网络）。"""

    def factory(settings: Settings) -> RateLimitedClient:
        return RateLimitedClient(
            settings,
            transport=httpx.MockTransport(handler),
            sleeper=lambda _: None,
            rng=lambda a, b: 0,
        )

    return factory


# ---- 夹具 --------------------------------------------------------------

def _settings(tmp_path, **overrides) -> Settings:
    base = dict(
        _env_file=None,
        request_delay_min=0.0,
        request_delay_max=0.0,
        max_retries=0,
        db_path=tmp_path / "data" / "archive.db",
        archive_root=tmp_path / "archive",
    )
    base.update(overrides)
    return Settings(**base)


@pytest.fixture
def env(tmp_path):
    settings = _settings(tmp_path)
    conn = connect(settings.db_path)
    init_db(conn)
    yield conn, settings
    conn.close()


def _seed_hidden(conn) -> None:
    """预置一篇此前已归档、但本轮全量历史中不再出现的文章（对账应标 skipped）。"""
    conn.execute(
        """
        INSERT INTO articles
            (biz, mid, idx, sn, account_alias, title, author, publish_time,
             url, digest, status)
        VALUES (?, '9000', 1, 'sn-old', ?, '历史旧文', '作者甲',
                '2023-01-01T00:00:00+00:00', ?, '摘要', 'downloaded')
        """,
        (BIZ, ALIAS, _content_url(9000, 1, "sn-old")),
    )
    conn.commit()


def _counts(conn) -> dict[str, int]:
    return {
        table: conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
        for table in ("articles", "media", "comments", "metrics")
    }


def _archive_files(settings) -> list[str]:
    root = settings.archive_root
    return sorted(
        p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
    )


# ---- AC-4 / AC-5 / AC-6 / AC-8 ----------------------------------------

def test_acceptance_full_pipeline_ac4_ac5_ac6(env):
    """全量编排：列表完整落库 + 10 篇四件套与图片本地化 + 富媒体分类。"""
    conn, settings = env
    _seed_hidden(conn)

    report = run_pipeline(conn, settings, ALIAS, full=True,
                          client_factory=_client_factory(_make_handler()))

    # ---- AC-4 列表完整落库 ----
    assert report.mode == "full"
    assert report.list.completed is True
    assert report.list.inserted == 11
    assert report.list.updated == 0
    assert report.list.hidden_marked == 1

    rows = conn.execute("SELECT * FROM articles WHERE biz = ?", (BIZ,)).fetchall()
    assert len(rows) == 12  # 11 篇本轮 + 1 篇历史不可见
    keys = [(r["biz"], r["mid"], r["idx"]) for r in rows]
    assert len(set(keys)) == len(keys)  # biz+mid+idx 唯一键无重复
    for r in rows:
        assert r["title"] and r["url"] and r["publish_time"]
        assert r["idx"] is not None and r["author"]
    # 原创标记（copyright_stat == 11）
    assert conn.execute(
        "SELECT is_original FROM articles WHERE sn = 'sn-a1'").fetchone()["is_original"] == 1
    assert conn.execute(
        "SELECT is_original FROM articles WHERE sn = 'sn-a2'").fetchone()["is_original"] == 0
    # 多图文次条 idx 正确解析
    assert conn.execute(
        "SELECT idx FROM articles WHERE sn = 'sn-a3b'").fetchone()["idx"] == 2
    # 已删文章有状态记录
    deleted = conn.execute("SELECT * FROM articles WHERE sn = ?", (DELETED_SN,)).fetchone()
    assert deleted["status"] == "skipped"
    assert "content_deleted@" in deleted["fail_reason"]
    # 不可见历史文章被对账标记
    hidden = conn.execute("SELECT * FROM articles WHERE mid = '9000'").fetchone()
    assert hidden["status"] == "skipped"
    assert hidden["fail_reason"].startswith("not_visible_in_full_scan@")
    # 账号水位
    state = conn.execute("SELECT * FROM sync_state").fetchone()
    assert state["credential_status"] == "valid"
    assert state["total_seen"] == 12

    # ---- AC-5 抽样 10 篇四件套 + 图片 100% 本地化 ----
    assert (report.fetch.total, report.fetch.downloaded, report.fetch.skipped,
            report.fetch.failed, report.fetch.image_failures) == (11, 10, 1, 0, 0)
    downloaded = conn.execute(
        "SELECT * FROM articles WHERE status = 'downloaded'").fetchall()
    assert len(downloaded) == 10
    root = settings.archive_root
    for r in downloaded:
        article_dir = (root / r["content_html_path"]).parent
        html_path = article_dir / "article.html"
        md_path = article_dir / "article.md"
        meta_path = article_dir / "metadata.json"
        assert html_path.is_file() and md_path.is_file() and meta_path.is_file()

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        md = md_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")
        assert meta["source"] == "wechat-mp-archiver"
        assert meta["mid"] and meta["idx"] is not None
        # 离线可打开：本地引用的图片全部落盘，无远程残留、无 data: 占位
        assert "data:image" not in md and "data:image" not in html
        if meta["images"]:
            assert all(item["ok"] for item in meta["images"])
            assert "mmbiz.qpic.cn" not in md
            assert "mmbiz.qpic.cn" not in html
            assert "images/001.png" in html
        assert 'charset="utf-8"' in html

    # 长文与图集的形状抽查
    long_dir = (root / conn.execute(
        "SELECT content_md_path FROM articles WHERE sn = 'sn-a4'"
    ).fetchone()["content_md_path"]).parent
    long_md = (long_dir / "article.md").read_text(encoding="utf-8")
    assert "长文段落12" in long_md
    gallery = json.loads((root / conn.execute(
        "SELECT content_html_path FROM articles WHERE sn = 'sn-a5'"
    ).fetchone()["content_html_path"]).parent.joinpath("metadata.json")
        .read_text(encoding="utf-8"))
    assert len(gallery["images"]) == 3 and all(i["ok"] for i in gallery["images"])

    # ---- AC-6 富媒体：语音落盘、其余仅登记 external 不伪造文件 ----
    media_article_id = conn.execute(
        "SELECT id FROM articles WHERE sn = 'sn-a6'").fetchone()["id"]
    media_dir = (root / conn.execute(
        "SELECT content_html_path FROM articles WHERE sn = 'sn-a6'"
    ).fetchone()["content_html_path"]).parent / "media"
    assert sorted(p.name for p in media_dir.iterdir()) == ["001.mp3"]
    assert (media_dir / "001.mp3").read_bytes() == MP3_BYTES

    counts = {
        (r["media_type"], r["status"]): r["n"]
        for r in conn.execute(
            "SELECT media_type, status, COUNT(*) AS n FROM media "
            "WHERE article_id = ? GROUP BY media_type, status", (media_article_id,))
    }
    assert counts[("audio", "downloaded")] == 1
    assert counts[("audio", "failed")] == 1
    assert counts[("audio", "external")] == 1
    assert counts[("video", "external")] == 1
    assert counts[("external", "external")] == 1

    media_md = (media_dir.parent / "article.md").read_text(encoding="utf-8")
    assert "已归档：media/001.mp3" in media_md
    assert "腾讯视频" in media_md and "vidxyz" in media_md
    assert "视频号" in media_md
    assert "站外音频" in media_md and "xiaoyuzhoufm.com" in media_md


def test_acceptance_ac8_rerun_is_idempotent(env):
    """AC-8：重跑不新增记录与文件，中断后续跑自然补齐全量。"""
    conn, settings = env
    _seed_hidden(conn)
    factory = _client_factory(_make_handler())

    first = run_pipeline(conn, settings, ALIAS, full=True, client_factory=factory)
    assert first.fetch.downloaded == 10
    files_before = _archive_files(settings)
    counts_before = _counts(conn)
    assert counts_before["articles"] == 12

    second = run_pipeline(conn, settings, ALIAS, full=True, client_factory=factory)
    assert second.list.inserted == 0
    assert second.list.updated == 11
    assert second.list.hidden_marked == 0  # 已 skipped 的对账项不被重复标记
    assert second.fetch.total == 0  # 无 pending：已下载文章永不重下
    assert second.fetch.downloaded == 0

    assert _counts(conn) == counts_before
    assert _archive_files(settings) == files_before


# ---- AC-7 互动数据采集的三态 -------------------------------------------

def test_acceptance_ac7_disabled_switch_writes_nothing(env):
    """开关关闭：既不采集也不登记（metrics/comments 表零行）。"""
    conn, settings = env
    assert settings.fetch_metrics is False

    report = run_pipeline(conn, settings, ALIAS, full=True,
                          client_factory=_client_factory(_make_handler(limit=2)))

    assert report.fetch.downloaded == 2
    assert report.fetch.interactions_collected == 0
    assert _counts(conn)["metrics"] == 0
    assert _counts(conn)["comments"] == 0


def test_acceptance_ac7_missing_credentials_degrades(env):
    """开关开启但无凭证：metrics 全标 skipped_no_credential，主流程成功。"""
    conn, settings = env
    metrics_on = settings.model_copy(update={"fetch_metrics": True})

    report = run_pipeline(conn, metrics_on, ALIAS, full=True,
                          client_factory=_client_factory(_make_handler(limit=2)))

    assert report.fetch.downloaded == 2
    assert report.fetch.interactions_skipped == 2
    assert report.fetch.interactions_failed == 0
    assert (report.fetch.interactions_collected, report.fetch.comments_collected) == (0, 0)
    statuses = {r["status"] for r in conn.execute("SELECT status FROM metrics")}
    assert statuses == {"skipped_no_credential"}
    assert _counts(conn)["comments"] == 0


def test_acceptance_ac7_with_credentials_collects(env):
    """开关开启且有凭证：评论与互动指标入库，计数与平台返回一致。"""
    conn, settings = env
    metrics_on = settings.model_copy(update={
        "fetch_metrics": True,
        "wechat_appmsg_token": SecretStr("test-token"),
        "wechat_pass_ticket": SecretStr("test-pass-ticket"),
    })

    report = run_pipeline(conn, metrics_on, ALIAS, full=True,
                          client_factory=_client_factory(_make_handler(limit=2)))

    assert report.fetch.downloaded == 2
    assert report.fetch.interactions_collected == 2
    assert report.fetch.interactions_skipped == 0
    assert report.fetch.comments_collected == 6  # 每篇 2 主评论 + 1 回复

    assert _counts(conn)["comments"] == 6
    assert {r["status"] for r in conn.execute("SELECT status FROM metrics")} == {"collected"}
    snapshot = conn.execute(
        "SELECT read_count, like_count, old_like_count, share_count, comment_count "
        "FROM metrics LIMIT 1").fetchone()
    assert (snapshot["read_count"], snapshot["like_count"], snapshot["old_like_count"],
            snapshot["share_count"], snapshot["comment_count"]) == (1234, 56, 12, 8, 2)
    assert conn.execute(
        "SELECT COUNT(*) AS n FROM comments WHERE comment_id LIKE '%#r%'").fetchone()["n"] == 2


def test_acceptance_ac7_cli_run_without_credentials_exits_zero(
    monkeypatch, tmp_path, capsys
):
    """AC-7：真实 CLI ``run --full --fetch-metrics`` 无凭证 → 退出码 0。

    与上面三条用例的区别在于**入口层级**：此处从 ``cli.main`` 进入，经
    ``_run_pipeline_command`` 走 ``get_settings`` → ``connect`` → ``init_db``
    → 真实 ``run_pipeline`` 两阶段编排，只有 HTTP 传输被换成 MockTransport。
    这样才能真正锁定「互动缺数据不影响任务整体成功退出码」这一 AC-7 断言，
    而非由桩掉编排层的 CLI 打印用例推论。

    注入方式说明：``run_pipeline`` 的 ``client_factory`` 是关键字默认参数，
    在函数定义时即绑定为 ``RateLimitedClient`` 类对象，因此改写
    ``pipeline.RateLimitedClient`` 属性不会生效；改为给 ``cli`` 命名空间内的
    ``run_pipeline`` 套一层薄转发，仅补 ``client_factory`` 后原样委托真实实现。
    """
    from mp_archiver import cli as cli_module
    from mp_archiver.core import pipeline as pipeline_module

    cli_module.get_settings.cache_clear()
    monkeypatch.setenv("MP_ARCHIVER_EXPORTER_TOKEN", "")
    monkeypatch.setenv("MP_ARCHIVER_DB_PATH", str(tmp_path / "data" / "archive.db"))
    monkeypatch.setenv("MP_ARCHIVER_ARCHIVE_ROOT", str(tmp_path / "archive"))
    monkeypatch.setenv("MP_ARCHIVER_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MIN", "0")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MAX", "0")
    # 显式清空互动凭证，保证走「开关开启但无凭证」的降级分支
    monkeypatch.delenv("MP_ARCHIVER_WECHAT_APPMSG_TOKEN", raising=False)
    monkeypatch.delenv("MP_ARCHIVER_WECHAT_PASS_TICKET", raising=False)

    factory = _client_factory(_make_handler())
    real_run_pipeline = pipeline_module.run_pipeline

    def forwarding_run_pipeline(*args, **kwargs):
        kwargs.setdefault("client_factory", factory)
        return real_run_pipeline(*args, **kwargs)

    monkeypatch.setattr(cli_module, "run_pipeline", forwarding_run_pipeline)

    assert cli_module.main(
        ["run", "-a", ALIAS, "--full", "--fetch-metrics"]
    ) == 0

    out = capsys.readouterr().out
    assert "成功 10" in out and "失败 0" in out
    assert "缺凭证跳过 10 篇" in out  # 降级而非失败

    conn = connect(tmp_path / "data" / "archive.db")
    try:
        assert conn.execute(
            "SELECT COUNT(*) AS n FROM articles WHERE status = 'downloaded'"
        ).fetchone()["n"] == 10
        statuses = [r["status"] for r in conn.execute("SELECT status FROM metrics")]
        assert set(statuses) == {"skipped_no_credential"}
        assert len(statuses) == 10
        assert conn.execute(
            "SELECT COUNT(*) AS n FROM comments"
        ).fetchone()["n"] == 0
    finally:
        conn.close()