"""article_archive 归档管线端到端测试（MockTransport，无真实网络）。

覆盖 TR-5.1：四件套齐全、图片本地化与失败例外登记、删除/风控页状态机、
同日同名目录后缀、重跑幂等。
"""

import json

import httpx
import pytest

from mp_archiver.config import Settings
from mp_archiver.core.article_archive import fetch_articles
from mp_archiver.db import connect, init_db
from mp_archiver.http_client import RateLimitedClient
from mp_archiver.models import ArticleRecord, ArticleStatus

PNG_BYTES = b"\x89PNG\r\n\x1a\n-fake-image-bytes-"
PIC1 = "https://mmbiz.qpic.cn/mmbiz_png/pic1?wx_fmt=png"
PIC2 = "https://mmbiz.qpic.cn/mmbiz_gif/pic2?wx_fmt=gif"
MP3_BYTES = b"ID3\x03\x00-fake-mp3-audio-"


def _media_article_page(sn: str) -> str:
    return f"""
<html><head><title>文章 {sn}</title></head><body>
<div id="img-content"><div id="js_content" class="rich_media_content">
  <p>正文段落。</p>
  <mpvoice voice_encode_fileid="audok" name="栏目语音" play_length="30000"></mpvoice>
  <mpvoice voice_encode_fileid="audbad" name="失败语音"></mpvoice>
  <iframe class="video_iframe"
          data-src="https://v.qq.com/txp/iframe/player.html?vid=vidxyz"></iframe>
  <mp-common-channels_video data-object_id="oid1" data-nickname="某视频号">
  </mp-common-channels_video>
  <iframe data-src="https://www.xiaoyuzhoufm.com/player/episode/ep1"></iframe>
</div></div>
</body></html>
"""


def _article_page(sn: str) -> str:
    return f"""
<html><head><title>文章 {sn}</title></head><body>
<div id="img-content"><div id="js_content" class="rich_media_content">
  <h2>章节标题</h2>
  <p>正文段落ABC，覆盖普通文字。</p>
  <ul><li>要点一</li></ul>
  <blockquote><p>一段引用</p></blockquote>
  <img data-src="{PIC1}" src="data:image/svg+xml;base64,PLACEHOLDER1"/>
  <img data-src="{PIC2}" src="data:image/svg+xml;base64,PLACEHOLDER2"/>
</div></div>
</body></html>
"""


DELETED_PAGE = "<html><body><div>该内容已被发布者删除</div></body></html>"
RISK_PAGE = "<html><body><div>环境异常，请完成验证后即可继续访问</div></body></html>"

PAGES = {
    "ok1": _article_page("ok1"),
    "del1": DELETED_PAGE,
    "risk1": RISK_PAGE,
    "dup1": _article_page("dup1"),
    "media1": _media_article_page("media1"),
}


def _handler(request: httpx.Request) -> httpx.Response:
    if request.url.host == "mmbiz.qpic.cn":
        if "pic1" in request.url.path:
            return httpx.Response(200, content=PNG_BYTES,
                                  headers={"content-type": "image/png"})
        return httpx.Response(404, text="not found")
    if request.url.host == "res.wx.qq.com":
        if request.url.params.get("mediaid") == "audok":
            return httpx.Response(200, content=MP3_BYTES,
                                  headers={"content-type": "audio/mpeg"})
        return httpx.Response(500, text="voice error")
    sn = request.url.params.get("sn", "")
    if sn in PAGES:
        return httpx.Response(200, html=PAGES[sn])
    return httpx.Response(404, text="unknown sn")


@pytest.fixture
def env(tmp_path):
    settings = Settings(
        request_delay_min=0.0,
        request_delay_max=0.0,
        max_retries=0,
        db_path=tmp_path / "data" / "archive.db",
        archive_root=tmp_path / "archive",
    )
    conn = connect(settings.db_path)
    init_db(conn)
    client = RateLimitedClient(settings, transport=httpx.MockTransport(_handler),
                               sleeper=lambda _: None)
    yield conn, client, settings
    client.close()
    conn.close()


def _insert(conn, mid: int, sn: str, title: str, day: str) -> None:
    conn.execute(
        """
        INSERT INTO articles
            (biz, mid, idx, sn, account_alias, title, author, publish_time,
             url, digest, status)
        VALUES (?, ?, 1, ?, '意识食谱', ?, '作者甲', ?,
                ?, '摘要', 'pending')
        """,
        (
            "BIZ==",
            str(mid),
            sn,
            title,
            f"2024-03-{day}T08:00:00+00:00",
            f"http://mp.weixin.qq.com/s?__biz=BIZ&mid={mid}&idx=1&sn={sn}",
        ),
    )
    conn.commit()


def test_fetch_full_pipeline_four_artifacts(env):
    conn, client, settings = env
    _insert(conn, 22, "ok1", "正常图文", "01")
    _insert(conn, 23, "del1", "已删文章", "02")
    _insert(conn, 24, "risk1", "风控文章", "03")

    report = fetch_articles(conn, client, "意识食谱", settings.archive_root)
    assert (report.total, report.downloaded, report.skipped,
            report.failed, report.image_failures) == (3, 1, 1, 1, 1)

    base = settings.archive_root / "意识食谱" / "2024" / "2024-03-01_正常图文"
    # 四件套
    assert (base / "article.html").is_file()
    assert (base / "article.md").is_file()
    assert (base / "metadata.json").is_file()
    assert (base / "images" / "001.png").is_file()
    assert (base / "images" / "001.png").read_bytes() == PNG_BYTES

    md_text = (base / "article.md").read_text(encoding="utf-8")
    assert "# 正常图文" in md_text
    assert "## 章节标题" in md_text
    assert "正文段落ABC" in md_text
    assert "images/001.png" in md_text
    assert PIC2 in md_text  # 失败图片兜底保留远程引用
    assert "data:image" not in md_text

    html_text = (base / "article.html").read_text(encoding="utf-8")
    assert "images/001.png" in html_text
    assert "charset=\"utf-8\"" in html_text
    assert "data:image" not in html_text

    meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    assert meta["biz"] == "BIZ==" and meta["mid"] == "22" and meta["idx"] == 1
    images = meta["images"]
    assert images[0]["ok"] is True and images[0]["file"] == "images/001.png"
    assert images[1]["ok"] is False and images[1]["file"] is None

    # DB 状态机
    ok_row = conn.execute("SELECT * FROM articles WHERE sn='ok1'").fetchone()
    del_row = conn.execute("SELECT * FROM articles WHERE sn='del1'").fetchone()
    risk_row = conn.execute("SELECT * FROM articles WHERE sn='risk1'").fetchone()
    assert ok_row["status"] == ArticleStatus.DOWNLOADED.value
    assert ok_row["content_html_path"].endswith("article.html")
    assert ok_row["content_md_path"].endswith("article.md")
    assert del_row["status"] == ArticleStatus.SKIPPED.value
    assert "content_deleted@" in del_row["fail_reason"]
    assert risk_row["status"] == ArticleStatus.FAILED.value
    assert "PageUnavailableError" in risk_row["fail_reason"]

    # 删除/风控文章不产生归档目录
    assert not (settings.archive_root / "意识食谱" / "2024").joinpath(
        "2024-03-02_已删文章").exists()


def test_refetch_is_idempotent_and_name_collision_gets_suffix(env):
    conn, client, settings = env
    _insert(conn, 22, "ok1", "正常图文", "01")
    fetch_articles(conn, client, "意识食谱", settings.archive_root)

    base = settings.archive_root / "意识食谱" / "2024" / "2024-03-01_正常图文"
    ok_row = conn.execute("SELECT * FROM articles WHERE sn='ok1'").fetchone()

    # 同一篇重跑：不产生 -2 目录，产物整体重写
    from mp_archiver.core.article_archive import archive_article

    archive_article(conn, client, ok_row, settings.archive_root)
    siblings = list((settings.archive_root / "意识食谱" / "2024").iterdir())
    assert siblings == [base]
    assert (base / "article.md").is_file()

    # 同日同名但属于另一篇：追加 -2 后缀
    _insert(conn, 25, "dup1", "正常图文", "01")
    report = fetch_articles(conn, client, "意识食谱", settings.archive_root,
                            include_failed=True)
    assert report.downloaded == 1  # 只有新文章 dup1（ok1 已 downloaded 不入选）
    assert (base.parent / "2024-03-01_正常图文-2" / "article.md").is_file()


def test_fetch_unknown_account(env):
    conn, client, settings = env
    with pytest.raises(LookupError):
        fetch_articles(conn, client, "不存在的号", settings.archive_root)


def test_rich_media_archive_voice_downloaded_placeholders_not_fabricated(env):
    """TR-6.2：语音落盘；腾讯视频/视频号/站外只登记不造文件；重跑幂等。"""
    conn, client, settings = env
    _insert(conn, 30, "media1", "富媒体文章", "10")

    fetch_articles(conn, client, "意识食谱", settings.archive_root)
    base = settings.archive_root / "意识食谱" / "2024" / "2024-03-10_富媒体文章"

    # 仅成功语音产生一个文件；失败语音与占位类型不产生任何伪造文件
    media_dir = base / "media"
    assert sorted(p.name for p in media_dir.iterdir()) == ["001.mp3"]
    assert (media_dir / "001.mp3").read_bytes() == MP3_BYTES

    md_text = (base / "article.md").read_text(encoding="utf-8")
    assert "音频·微信语音" in md_text
    assert "已归档：media/001.mp3" in md_text
    assert "下载失败" in md_text
    assert "腾讯视频" in md_text and "vidxyz" in md_text
    assert "视频号" in md_text
    assert "站外音频" in md_text and "xiaoyuzhoufm.com" in md_text

    meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    assert len(meta["rich_media"]) == 5

    article_id = conn.execute(
        "SELECT id FROM articles WHERE sn='media1'"
    ).fetchone()["id"]
    rows = conn.execute(
        "SELECT media_type, status, COUNT(*) AS n FROM media "
        "WHERE article_id=? GROUP BY media_type, status ORDER BY media_type",
        (article_id,),
    ).fetchall()
    counts = {(r["media_type"], r["status"]): r["n"] for r in rows}
    # 微信语音：1 成功 1 失败；小宇宙按媒体本体归 audio/external
    assert counts[("audio", "downloaded")] == 1
    assert counts[("audio", "failed")] == 1
    assert counts[("audio", "external")] == 1
    # 腾讯视频占位
    assert counts[("video", "external")] == 1
    # 视频号卡片归 external/external
    assert counts[("external", "external")] == 1

    downloaded = conn.execute(
        "SELECT * FROM media WHERE article_id=? AND status='downloaded' "
        "AND media_type='audio'",
        (article_id,),
    ).fetchone()
    assert downloaded["local_path"] == "media/001.mp3"
    assert downloaded["size_bytes"] == len(MP3_BYTES)
    assert downloaded["mime"] == "audio/mpeg"
    assert downloaded["sha256"]

    # 重跑：media 行不翻倍（upsert 幂等），文件仍只有一个
    from mp_archiver.core.article_archive import archive_article

    media_row = conn.execute(
        "SELECT * FROM articles WHERE sn='media1'"
    ).fetchone()
    archive_article(conn, client, media_row, settings.archive_root)
    total = conn.execute(
        "SELECT COUNT(*) AS n FROM media WHERE article_id=?", (article_id,)
    ).fetchone()["n"]
    assert total == 5
    assert sorted(p.name for p in media_dir.iterdir()) == ["001.mp3"]
