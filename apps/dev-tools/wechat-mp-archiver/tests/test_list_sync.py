"""列表同步编排测试（假适配器 + 内存 SQLite）。"""

import sqlite3

import pytest

from mp_archiver.adapters.base import AccountRef, HistoryPage
from mp_archiver.adapters.wechat_payload import CredentialExpiredError
from mp_archiver.core.list_sync import sync_article_list
from mp_archiver.core.validation import check_metadata_completeness
from mp_archiver.db import init_db, upsert_article
from mp_archiver.models import ArticleRecord, ArticleStatus


class FakeAdapter:
    def __init__(self, pages, account=None):
        self._pages = pages
        self._account = account or AccountRef(nickname="意识食谱", fakeid="998", biz="BIZ==")
        self.requests = []

    def resolve_account(self, name):
        return self._account

    def fetch_history_page(self, account, offset):
        self.requests.append(offset)
        return self._pages[offset]


def _record(mid, idx=1, sn=None, title=None):
    return ArticleRecord(
        biz="BIZ==",
        account_alias="意识食谱",
        mid=str(mid),
        idx=idx,
        sn=sn or f"sn-{mid}-{idx}",
        title=title or f"标题{mid}-{idx}",
        publish_time="2024-01-01T00:00:00+00:00",
        url=f"http://mp.weixin.qq.com/s?__biz=QklaPT0=&mid={mid}&idx={idx}&sn=x",
        status=ArticleStatus.PENDING,
    )


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_db(connection)
    yield connection
    connection.close()


def test_full_sync_upserts_and_sets_watermark(conn):
    page1 = HistoryPage(
        articles=(_record(100), _record(101, idx=1), _record(101, idx=2, title="多图文次条")),
        next_offset=10, has_more=True, skipped_non_article=1,
    )
    # 第二页重复回传 101/2，验证去重更新
    page2 = HistoryPage(
        articles=(_record(101, idx=2), _record(102)),
        next_offset=11, has_more=False, skipped_non_article=0,
    )
    report = sync_article_list(
        conn, FakeAdapter({0: page1, 10: page2}), name="意识食谱"
    )
    assert report.pages == 2
    assert report.inserted == 4
    assert report.updated == 1
    assert report.skipped_non_article == 1
    assert report.completed is True
    assert report.final_offset == 11

    state = conn.execute("SELECT * FROM sync_state").fetchone()
    assert state["credential_status"] == "valid"
    assert state["last_cursor"] == "11"
    assert state["total_seen"] == 4


def test_full_reconcile_marks_missing_articles(conn):
    # 预置一篇此前已下载的旧文章，本次全量历史中不再出现
    old = _record(900, title="已下架旧文")
    upsert_article(conn, old, status=ArticleStatus.DOWNLOADED)

    page = HistoryPage(articles=(_record(100),), next_offset=0,
                       has_more=False, skipped_non_article=0)
    report = sync_article_list(conn, FakeAdapter({0: page}), name="意识食谱")
    assert report.hidden_marked == 1
    row = conn.execute("SELECT status, fail_reason FROM articles WHERE mid = '900'").fetchone()
    assert row["status"] == "skipped"
    assert row["fail_reason"].startswith("not_visible_in_full_scan@")


def test_truncated_sync_does_not_reconcile(conn):
    old = _record(900, title="旧文")
    upsert_article(conn, old, status=ArticleStatus.DOWNLOADED)

    page = HistoryPage(articles=(_record(100),), next_offset=10,
                       has_more=True, skipped_non_article=0)
    report = sync_article_list(
        conn, FakeAdapter({0: page}), name="意识食谱", max_pages=1
    )
    assert report.completed is False
    assert report.hidden_marked == 0
    row = conn.execute("SELECT status FROM articles WHERE mid = '900'").fetchone()
    assert row["status"] == "downloaded"


def test_downloaded_status_not_regressed(conn):
    article = _record(100)
    upsert_article(conn, article, status=ArticleStatus.DOWNLOADED)
    page = HistoryPage(articles=(_record(100, title="标题被改写"),),
                       next_offset=0, has_more=False, skipped_non_article=0)
    sync_article_list(conn, FakeAdapter({0: page}), name="意识食谱")
    row = conn.execute("SELECT status, title FROM articles WHERE mid = '100'").fetchone()
    assert row["status"] == "downloaded"
    assert row["title"] == "标题被改写"  # 元数据仍刷新


def test_credential_expired_records_state_and_raises(conn):
    class ExpiredAdapter(FakeAdapter):
        def fetch_history_page(self, account, offset):
            raise CredentialExpiredError(200013, "invalid session")

    with pytest.raises(CredentialExpiredError):
        sync_article_list(conn, ExpiredAdapter({}), name="意识食谱")
    state = conn.execute("SELECT credential_status FROM sync_state").fetchone()
    assert state["credential_status"] == "expired"


def test_metadata_completeness_full_and_missing(conn):
    good_page = HistoryPage(
        articles=(_record(100), _record(101)),
        next_offset=0, has_more=False, skipped_non_article=0,
    )
    sync_article_list(conn, FakeAdapter({0: good_page}), name="意识食谱")
    report = check_metadata_completeness(conn, "BIZ==")
    assert report.ok is True
    assert report.rates() == {"title": 1.0, "url": 1.0, "publish_time": 1.0}

    # 手工塞入一条缺字段的记录，校验应能发现
    upsert_article(
        conn,
        ArticleRecord(biz="BIZ==", mid="888", idx=1, sn="s888",
                      title="", url=None, publish_time=None),
    )
    report = check_metadata_completeness(conn, "BIZ==")
    assert report.ok is False
    assert report.total == 3
    assert report.missing == {"title": 1, "url": 1, "publish_time": 1}
