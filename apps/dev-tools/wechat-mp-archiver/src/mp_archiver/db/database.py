"""SQLite 连接管理、schema 初始化与幂等写入。"""

import sqlite3
from pathlib import Path

from ..models import ArticleStatus, CredentialStatus, ArticleRecord, MediaStatus, MediaType

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(db_path: str | Path) -> sqlite3.Connection:
    """打开数据库连接（自动创建父目录，启用 WAL 与外键）。"""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """幂等初始化全部表与索引（可重复执行）。"""
    conn.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))
    _apply_column_migrations(conn)
    conn.commit()


# 轻量列迁移：schema.sql 只对新建库生效，已存在的库用 ALTER TABLE 补齐列。
_COLUMN_MIGRATIONS = {
    "articles": (
        ("is_original", "INTEGER NOT NULL DEFAULT 0"),
        ("album", "TEXT NOT NULL DEFAULT ''"),
        ("source", "TEXT NOT NULL DEFAULT 'exporter'"),
    ),
    "metrics": (
        ("status", "TEXT NOT NULL DEFAULT 'pending'"),
        ("fail_reason", "TEXT"),
    ),
}


def _apply_column_migrations(conn: sqlite3.Connection) -> None:
    for table, additions in _COLUMN_MIGRATIONS.items():
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        for name, ddl in additions:
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")


def merge_source(existing: str | None, incoming: str) -> str:
    """合并数据来源标记：精确成员判断 + 字典序规范化。

    形态为 ``a+b``（如 ``exporter+official_api``）；重复命中幂等，
    新源无论到达先后都产生相同的规范化结果。
    """
    members = {s for s in (existing or "").split("+") if s}
    if incoming:
        members.add(incoming)
    return "+".join(sorted(members))


def find_article_id(conn: sqlite3.Connection, record: ArticleRecord) -> int | None:
    """按 biz+mid+idx（其次 sn）定位文章行 id。"""
    if record.mid is not None and record.idx is not None:
        row = conn.execute(
            "SELECT id FROM articles WHERE biz = ? AND mid = ? AND idx = ?",
            (record.biz, record.mid, record.idx),
        ).fetchone()
        if row is not None:
            return int(row["id"])
    if record.sn:
        row = conn.execute(
            "SELECT id FROM articles WHERE sn = ?",
            (record.sn,),
        ).fetchone()
        if row is not None:
            return int(row["id"])
    return None


def upsert_article(
    conn: sqlite3.Connection,
    record: ArticleRecord,
    *,
    status: ArticleStatus | None = None,
    fail_reason: str | None = None,
    preserve_status: bool = False,
    source: str = "exporter",
) -> int:
    """插入或更新文章，返回行 id。

    命中策略：先按 ``biz+mid+idx`` 查重，其次按 ``sn`` 查重；
    重复时更新可变元数据（空字符串不覆盖已有值），不产生重复行。

    ``preserve_status=True`` 用于列表同步：已存在的文章保持其采集状态
    （如已 downloaded 不回退为 pending，失败原因也保留）；新行仍以
    ``status``（默认 :attr:`ArticleRecord.status`）插入。

    ``source`` 为数据来源标记（exporter/official_api）；命中既有行时
    多源以 ``a+b`` 形式合并，用于 R2 与官方接口去重对账。
    """
    effective_status = status or record.status
    existing_id = find_article_id(conn, record)

    if existing_id is None:
        cursor = conn.execute(
            """
            INSERT INTO articles (
                biz, mid, idx, sn, account_alias, title, author, publish_time,
                url, cover_url, digest, is_original, album, source, status,
                fail_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.biz,
                record.mid,
                record.idx,
                record.sn,
                record.account_alias,
                record.title,
                record.author,
                record.publish_time,
                record.url,
                record.cover_url,
                record.digest,
                int(record.is_original),
                record.album,
                source,
                effective_status.value,
                fail_reason,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)

    if preserve_status:
        conn.execute(
            """
            UPDATE articles SET
                account_alias = COALESCE(NULLIF(?, ''), account_alias),
                title         = COALESCE(NULLIF(?, ''), title),
                author        = COALESCE(NULLIF(?, ''), author),
                publish_time  = COALESCE(?, publish_time),
                url           = COALESCE(NULLIF(?, ''), url),
                cover_url     = COALESCE(NULLIF(?, ''), cover_url),
                digest        = COALESCE(NULLIF(?, ''), digest),
                is_original   = MAX(is_original, ?),
                album         = COALESCE(NULLIF(?, ''), album),
                mid           = COALESCE(mid, ?),
                idx           = COALESCE(idx, ?),
                sn            = COALESCE(NULLIF(sn, ''), ?),
                source        = ?,
                updated_at    = datetime('now')
            WHERE id = ?
            """,
            (
                record.account_alias,
                record.title,
                record.author,
                record.publish_time,
                record.url,
                record.cover_url,
                record.digest,
                int(record.is_original),
                record.album,
                record.mid,
                record.idx,
                record.sn,
                merge_source(
                    conn.execute(
                        "SELECT source FROM articles WHERE id = ?",
                        (existing_id,),
                    ).fetchone()["source"],
                    source,
                ),
                existing_id,
            ),
        )
    else:
        conn.execute(
            """
            UPDATE articles SET
                account_alias = COALESCE(NULLIF(?, ''), account_alias),
                title         = COALESCE(NULLIF(?, ''), title),
                author        = COALESCE(NULLIF(?, ''), author),
                publish_time  = COALESCE(?, publish_time),
                url           = COALESCE(NULLIF(?, ''), url),
                cover_url     = COALESCE(NULLIF(?, ''), cover_url),
                digest        = COALESCE(NULLIF(?, ''), digest),
                is_original   = MAX(is_original, ?),
                album         = COALESCE(NULLIF(?, ''), album),
                status        = ?,
                fail_reason   = ?,
                mid           = COALESCE(mid, ?),
                idx           = COALESCE(idx, ?),
                sn            = COALESCE(NULLIF(sn, ''), ?),
                source        = ?,
                updated_at    = datetime('now')
            WHERE id = ?
            """,
            (
                record.account_alias,
                record.title,
                record.author,
                record.publish_time,
                record.url,
                record.cover_url,
                record.digest,
                int(record.is_original),
                record.album,
                effective_status.value,
                fail_reason,
                record.mid,
                record.idx,
                record.sn,
                merge_source(
                    conn.execute(
                        "SELECT source FROM articles WHERE id = ?",
                        (existing_id,),
                    ).fetchone()["source"],
                    source,
                ),
                existing_id,
            ),
        )
    conn.commit()
    return existing_id


def upsert_sync_state(
    conn: sqlite3.Connection,
    account_biz: str,
    *,
    account_alias: str = "",
    last_cursor: str | None = None,
    total_seen: int | None = None,
    credential_status: CredentialStatus = CredentialStatus.NONE,
    extras: str | None = None,
) -> None:
    """写入账号同步水位（按 account_biz 主键 upsert）。

    ``extras`` 为 JSON 字符串；传 ``None`` 时保留既有值（COALESCE），
    用于增量刷新水位但不抹掉全量完成标记等历史信息。
    """
    conn.execute(
        """
        INSERT INTO sync_state (
            account_biz, account_alias, last_sync_at, last_cursor,
            total_seen, credential_status, extras
        ) VALUES (?, ?, datetime('now'), ?, COALESCE(?, 0), ?, ?)
        ON CONFLICT(account_biz) DO UPDATE SET
            account_alias     = COALESCE(NULLIF(excluded.account_alias, ''), sync_state.account_alias),
            last_sync_at      = excluded.last_sync_at,
            last_cursor       = COALESCE(excluded.last_cursor, sync_state.last_cursor),
            total_seen       = COALESCE(excluded.total_seen, sync_state.total_seen),
            credential_status = excluded.credential_status,
            extras            = COALESCE(excluded.extras, sync_state.extras)
        """,
        (
            account_biz,
            account_alias,
            last_cursor,
            total_seen,
            credential_status.value,
            extras,
        ),
    )
    conn.commit()


def get_account_biz_by_alias(conn: sqlite3.Connection, alias: str) -> str | None:
    """按账号别名（精确匹配）解析 biz；list 入库后可用。"""
    row = conn.execute(
        "SELECT biz FROM articles WHERE account_alias = ? "
        "GROUP BY biz ORDER BY COUNT(*) DESC LIMIT 1",
        (alias,),
    ).fetchone()
    return row["biz"] if row else None


def iter_articles_by_status(
    conn: sqlite3.Connection,
    account_biz: str,
    statuses: tuple[ArticleStatus, ...],
    *,
    limit: int | None = None,
):
    """按状态枚举账号文章（按发布时间升序，最旧的先归档）。"""
    placeholders = ",".join("?" for _ in statuses)
    sql = (
        f"SELECT * FROM articles WHERE biz = ? AND status IN ({placeholders}) "
        f"ORDER BY publish_time IS NULL, publish_time ASC, id ASC"
    )
    if limit is not None:
        sql += " LIMIT ?"
    params: tuple = (account_biz, *(s.value for s in statuses))
    if limit is not None:
        params = (*params, limit)
    yield from conn.execute(sql, params)


def iter_downloaded_articles(
    conn: sqlite3.Connection,
    *,
    account_biz: str | None = None,
    limit: int | None = None,
):
    """枚举已归档（status=downloaded）文章，供 RAG/报表等离线导出使用。

    按发布时间升序（NULL 置后）、id 升序稳定排序；``account_biz`` 为 None
    时导出全部账号。
    """
    where = "biz = ? AND status = ?" if account_biz is not None else "status = ?"
    sql = (
        f"SELECT * FROM articles WHERE {where} "
        "ORDER BY publish_time IS NULL, publish_time ASC, id ASC"
    )
    if account_biz is not None:
        params: tuple = (account_biz, ArticleStatus.DOWNLOADED.value)
    else:
        params = (ArticleStatus.DOWNLOADED.value,)
    if limit is not None:
        sql += " LIMIT ?"
        params = (*params, limit)
    yield from conn.execute(sql, params)


def upsert_media(
    conn: sqlite3.Connection,
    *,
    article_id: int,
    media_type: MediaType,
    url: str,
    status: MediaStatus,
    local_path: str | None = None,
    mime: str | None = None,
    sha256: str | None = None,
    size_bytes: int | None = None,
    fail_reason: str | None = None,
) -> int:
    """媒体登记（按 article_id+url 幂等 upsert），返回 media 行 id。"""
    cursor = conn.execute(
        """
        INSERT INTO media (
            article_id, media_type, url, local_path, mime, sha256,
            size_bytes, status, fail_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(article_id, url) DO UPDATE SET
            media_type = excluded.media_type,
            local_path = COALESCE(excluded.local_path, media.local_path),
            mime       = COALESCE(excluded.mime, media.mime),
            sha256     = COALESCE(excluded.sha256, media.sha256),
            size_bytes = COALESCE(excluded.size_bytes, media.size_bytes),
            status     = excluded.status,
            fail_reason= excluded.fail_reason,
            updated_at = datetime('now')
        """,
        (
            article_id,
            media_type.value,
            url,
            local_path,
            mime,
            sha256,
            size_bytes,
            status.value,
            fail_reason,
        ),
    )
    conn.commit()
    return int(cursor.lastrowid or 0) or int(
        conn.execute(
            "SELECT id FROM media WHERE article_id = ? AND url = ?",
            (article_id, url),
        ).fetchone()["id"]
    )


def upsert_comment(
    conn: sqlite3.Connection,
    *,
    article_id: int,
    comment_id: str,
    user_name: str | None,
    content: str | None,
    like_count: int,
    create_time: str | None,
) -> None:
    """评论/回复幂等写入（重跑更新点赞数，不产生重复行）。"""
    conn.execute(
        """
        INSERT INTO comments (article_id, comment_id, user_name, content,
                              like_count, create_time)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(article_id, comment_id) DO UPDATE SET
            user_name  = excluded.user_name,
            content    = excluded.content,
            like_count = excluded.like_count,
            create_time= excluded.create_time,
            fetched_at = datetime('now')
        """,
        (article_id, comment_id, user_name, content, like_count, create_time),
    )


def insert_metrics_snapshot(
    conn: sqlite3.Connection,
    *,
    article_id: int,
    status: str,
    read_count: int | None = None,
    like_count: int | None = None,
    old_like_count: int | None = None,
    share_count: int | None = None,
    comment_count: int | None = None,
    raw_json: str | None = None,
    fail_reason: str | None = None,
) -> int:
    """插入一次互动指标快照；每次采集追加历史行（不覆盖既有快照）。"""
    cursor = conn.execute(
        """
        INSERT INTO metrics (article_id, status, fail_reason, read_count,
                             like_count, old_like_count, share_count,
                             comment_count, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (article_id, status, fail_reason, read_count, like_count,
         old_like_count, share_count, comment_count, raw_json),
    )
    conn.commit()
    return int(cursor.lastrowid or 0)


def mark_article_archived(
    conn: sqlite3.Connection,
    article_id: int,
    html_path: str,
    md_path: str,
) -> None:
    """文章下载成功：回写状态与归档相对路径，清空失败原因。"""
    conn.execute(
        """
        UPDATE articles
           SET status = ?, content_html_path = ?, content_md_path = ?,
               fail_reason = NULL, updated_at = datetime('now')
         WHERE id = ?
        """,
        (ArticleStatus.DOWNLOADED.value, html_path, md_path, article_id),
    )
    conn.commit()


def mark_article_failed(
    conn: sqlite3.Connection,
    article_id: int,
    reason: str,
) -> None:
    """文章下载失败：回写 failed 与截断后的原因（不覆盖已下载产物路径）。"""
    conn.execute(
        """
        UPDATE articles
           SET status = ?, fail_reason = ?, updated_at = datetime('now')
         WHERE id = ?
        """,
        (ArticleStatus.FAILED.value, reason[:500], article_id),
    )
    conn.commit()


def count_articles(conn: sqlite3.Connection, account_biz: str) -> int:
    """统计账号下已知文章行数。"""
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM articles WHERE biz = ?", (account_biz,)
    ).fetchone()
    return int(row["n"])


def mark_articles_not_visible(
    conn: sqlite3.Connection,
    account_biz: str,
    visible_ids: set[int],
    reason: str,
) -> int:
    """全量扫描对账：本次完整历史中不可见的已知文章标记为 skipped。

    仅影响 pending/downloaded 状态（failed 记录保留原状，避免掩盖下载问题）。
    返回受影响行数。
    """
    if not visible_ids:
        # 空集对账必定是异常调用（一次全量不可能 0 篇还判定全删），交由调用方规避
        return 0
    placeholders = ",".join("?" for _ in visible_ids)
    cursor = conn.execute(
        f"""
        UPDATE articles
           SET status = ?,
               fail_reason = ?,
               updated_at = datetime('now')
         WHERE biz = ?
           AND id NOT IN ({placeholders})
           AND status IN ('pending', 'downloaded')
        """,
        (ArticleStatus.SKIPPED.value, reason, account_biz, *sorted(visible_ids)),
    )
    conn.commit()
    return int(cursor.rowcount or 0)
