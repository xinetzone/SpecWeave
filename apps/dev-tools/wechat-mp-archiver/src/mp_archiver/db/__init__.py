"""SQLite 元数据库：连接、幂等初始化与 upsert。"""

from .database import (
    connect,
    count_articles,
    find_article_id,
    get_account_biz_by_alias,
    init_db,
    insert_metrics_snapshot,
    iter_articles_by_status,
    iter_downloaded_articles,
    mark_article_archived,
    mark_article_failed,
    mark_articles_not_visible,
    upsert_article,
    upsert_comment,
    upsert_media,
    upsert_sync_state,
)

__all__ = [
    "connect",
    "count_articles",
    "find_article_id",
    "get_account_biz_by_alias",
    "init_db",
    "insert_metrics_snapshot",
    "iter_articles_by_status",
    "iter_downloaded_articles",
    "mark_article_archived",
    "mark_article_failed",
    "mark_articles_not_visible",
    "upsert_article",
    "upsert_comment",
    "upsert_media",
    "upsert_sync_state",
]
