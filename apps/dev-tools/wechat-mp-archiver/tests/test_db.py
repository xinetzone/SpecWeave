"""SQLite schema 幂等性与 upsert 唯一键行为测试。"""

import pytest

from mp_archiver.db import connect, init_db, upsert_article, upsert_sync_state
from mp_archiver.models import ArticleRecord, ArticleStatus, CredentialStatus


@pytest.fixture()
def conn(tmp_path):
    connection = connect(tmp_path / "test.db")
    init_db(connection)
    yield connection
    connection.close()


def test_init_db_idempotent(conn):
    # 连续再次初始化不报错，表数量稳定
    init_db(conn)
    init_db(conn)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    assert tables == {"articles", "media", "comments", "metrics", "sync_state"}


def test_upsert_article_by_biz_mid_idx_dedup(conn):
    record = ArticleRecord(
        biz="MzEx", mid="2247", idx=1, sn="SN-AAA", title="第一版",
        url="http://a/1", account_alias="测试号",
    )
    first_id = upsert_article(conn, record)
    second_id = upsert_article(conn, record)

    assert first_id == second_id
    assert conn.execute("SELECT count(*) FROM articles").fetchone()[0] == 1


def test_upsert_article_updates_fields_and_status(conn):
    upsert_article(
        conn,
        ArticleRecord(biz="MzEx", mid="2247", idx=1, sn="SN-AAA", title="旧标题"),
    )
    new_id = upsert_article(
        conn,
        ArticleRecord(biz="MzEx", mid="2247", idx=1, sn="SN-AAA", title="新标题",
                       author="张三", account_alias="号"),
        status=ArticleStatus.DOWNLOADED,
    )

    row = conn.execute(
        "SELECT title, author, status FROM articles WHERE id = ?", (new_id,)
    ).fetchone()
    assert row["title"] == "新标题"
    assert row["author"] == "张三"
    assert row["status"] == "downloaded"


def test_upsert_article_by_sn_when_mid_missing(conn):
    record = ArticleRecord(biz="MzEx", sn="ONLY-SN-1", title="短链文章")
    first_id = upsert_article(conn, record)
    second_id = upsert_article(conn, record)
    assert first_id == second_id
    assert conn.execute("SELECT count(*) FROM articles").fetchone()[0] == 1


def test_two_articles_same_biz_distinct_idx(conn):
    a1 = ArticleRecord(biz="MzEx", mid="2247", idx=1, sn="S1", title="文一")
    a2 = ArticleRecord(biz="MzEx", mid="2247", idx=2, sn="S2", title="文二")
    id1 = upsert_article(conn, a1)
    id2 = upsert_article(conn, a2)
    assert id1 != id2
    assert conn.execute("SELECT count(*) FROM articles").fetchone()[0] == 2


def test_upsert_sync_state_watermark(conn):
    upsert_sync_state(conn, "BIZ1", account_alias="号", last_cursor="c10",
                      total_seen=10, credential_status=CredentialStatus.VALID)
    # 再次同步：游标推进、别名缺省时不被空串覆盖
    upsert_sync_state(conn, "BIZ1", last_cursor="c20", total_seen=20,
                      credential_status=CredentialStatus.EXPIRED)

    row = conn.execute(
        "SELECT * FROM sync_state WHERE account_biz = 'BIZ1'"
    ).fetchone()
    assert row["last_cursor"] == "c20"
    assert row["total_seen"] == 20
    assert row["account_alias"] == "号"
    assert row["credential_status"] == "expired"
