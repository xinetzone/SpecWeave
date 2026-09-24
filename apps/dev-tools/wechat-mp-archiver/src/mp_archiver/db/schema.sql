-- wechat-mp-archiver 元数据库（SQLite，五表状态机）
-- 幂等：可重复执行（CREATE TABLE/INDEX IF NOT EXISTS）

-- 文章主表：唯一键 biz+mid+idx；退化键 sn（部分唯一索引）
CREATE TABLE IF NOT EXISTS articles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    biz             TEXT    NOT NULL,
    mid             TEXT,
    idx             INTEGER,
    sn              TEXT,
    account_alias   TEXT    NOT NULL DEFAULT '',
    title           TEXT    NOT NULL DEFAULT '',
    author          TEXT    NOT NULL DEFAULT '',
    publish_time    TEXT,
    url             TEXT,
    cover_url       TEXT,
    digest          TEXT    NOT NULL DEFAULT '',
    is_original     INTEGER NOT NULL DEFAULT 0,
    album           TEXT    NOT NULL DEFAULT '',
    source          TEXT    NOT NULL DEFAULT 'exporter',
    status          TEXT    NOT NULL DEFAULT 'pending',
    fail_reason     TEXT,
    content_html_path TEXT,
    content_md_path   TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_articles_biz_mid_idx
    ON articles(biz, mid, idx)
    WHERE mid IS NOT NULL AND idx IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ux_articles_sn
    ON articles(sn)
    WHERE sn IS NOT NULL AND sn <> '';

CREATE INDEX IF NOT EXISTS ix_articles_account_time
    ON articles(biz, publish_time);

CREATE INDEX IF NOT EXISTS ix_articles_status
    ON articles(status);

-- 媒体表：图片/音频/视频/附件/外链
CREATE TABLE IF NOT EXISTS media (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id      INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    media_type      TEXT    NOT NULL,
    url             TEXT    NOT NULL,
    local_path      TEXT,
    mime            TEXT,
    sha256          TEXT,
    size_bytes      INTEGER,
    status          TEXT    NOT NULL DEFAULT 'pending',
    fail_reason     TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id, url)
);

CREATE INDEX IF NOT EXISTS ix_media_status ON media(status);

-- 评论表（仅在显式开启互动数据采集时写入）
CREATE TABLE IF NOT EXISTS comments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id      INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    comment_id      TEXT    NOT NULL,
    user_name       TEXT,
    content         TEXT,
    like_count      INTEGER NOT NULL DEFAULT 0,
    create_time     TEXT,
    fetched_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id, comment_id)
);

-- 互动指标快照（阅读/点赞/在看/转发/评论数；默认不采集）
-- status: downloaded / skipped_no_credential / failed（缺凭证不记 failed）
CREATE TABLE IF NOT EXISTS metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id      INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    fetched_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    status          TEXT    NOT NULL DEFAULT 'pending',
    fail_reason     TEXT,
    read_count      INTEGER,
    like_count      INTEGER,
    old_like_count  INTEGER,
    share_count     INTEGER,
    comment_count   INTEGER,
    raw_json        TEXT
);

CREATE INDEX IF NOT EXISTS ix_metrics_article ON metrics(article_id, fetched_at);

-- 账号级同步状态与凭证状态（游标/增量水位）
CREATE TABLE IF NOT EXISTS sync_state (
    account_biz       TEXT PRIMARY KEY,
    account_alias     TEXT NOT NULL DEFAULT '',
    last_sync_at      TEXT,
    last_cursor       TEXT,
    total_seen        INTEGER NOT NULL DEFAULT 0,
    credential_status TEXT NOT NULL DEFAULT 'none',
    extras            TEXT
);
