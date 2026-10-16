"""SQLite 持久化基座（upstream: apps/api/src/db.ts 1:1 移植）。

差异说明：
- D1Database 替换为 sqlite3.Connection（WAL + foreign_keys + Row factory）。
- Wrangler 迁移机制替换为内置 _migrations 表的幂等应用器。
- D1 单语句 100 绑定参数限制（D1_IN_ID_CHUNK=99）在 SQLite 不存在，但分块常量与
  行为原样保留，确保跨后端契约一致。
- pushChanges 的 D1 逐语句自动提交在单连接串行服务下等价实现；整批合并包在一个
  事务内（原子性增强，LWW 判定与回拉语义不变）。
"""

import json
import sqlite3
import time
from collections.abc import Callable
from pathlib import Path
from typing import TypedDict

from .migrations import MIGRATIONS, load_migration
from .types import SyncDocument, SyncSetting, SyncHistoryEntry, UserRow

# upstream: db.ts:D1_IN_ID_CHUNK —— D1 每条查询 100 个绑定参数，留 1 个给 user_id
D1_IN_ID_CHUNK = 99


def now_ms() -> int:
    """epoch 毫秒（等价 Date.now()）。"""
    return time.time_ns() // 1_000_000


def connect(database: str | Path = ":memory:") -> sqlite3.Connection:
    """创建已配置 PRAGMA 的连接。

    - WAL：文件库并发读写；内存库设置该 PRAGMA 无害（返回 memory）。
    - foreign_keys=ON：emoji 表外键级联依赖此设置（SQLite 默认关闭）。
    """
    # check_same_thread=False：FastAPI 同步路由在线程池中执行，单一服务连接
    # 需跨线程复用；自托管单 worker 低并发场景配合 WAL 使用（上游 D1 本为远端
    # 串行存储）。多 worker 部署改用每 worker 独立文件连接。
    conn = sqlite3.connect(str(database), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _split_statements(sql: str) -> list[str]:
    """把迁移文件按分号切为独立语句（迁移 SQL 无存储过程/触发器/字符串内分号）。"""
    statements: list[str] = []
    buf: list[str] = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buf.append(line)
    text = "\n".join(buf)
    for part in text.split(";"):
        stmt = part.strip()
        if stmt:
            statements.append(stmt)
    return statements


def apply_migrations(conn: sqlite3.Connection) -> list[int]:
    """幂等应用全部迁移，返回本次新应用的迁移序号列表。"""
    conn.execute(
        """CREATE TABLE IF NOT EXISTS _migrations (
               id         INTEGER PRIMARY KEY,
               name       TEXT NOT NULL,
               applied_at INTEGER NOT NULL
           )"""
    )
    conn.commit()
    applied = {row[0] for row in conn.execute("SELECT id FROM _migrations")}
    newly: list[int] = []
    for mid, name in MIGRATIONS:
        if mid in applied:
            continue
        statements = _split_statements(load_migration(name))
        ts = now_ms()
        # DDL/DML 在同一事务；任一语句失败整体回滚（含 _migrations 登记）
        with conn:
            for stmt in statements:
                conn.execute(stmt)
            conn.execute(
                "INSERT INTO _migrations (id, name, applied_at) VALUES (?, ?, ?)",
                (mid, name, ts),
            )
        newly.append(mid)
    return newly


# ---- 行映射（upstream: db.ts rowToDocument / rowToSetting）----


def row_to_document(row: sqlite3.Row) -> SyncDocument:
    """upstream: db.ts:22-40 rowToDocument；history JSON 解析失败回退 []。"""
    try:
        parsed_history = json.loads(row["history"])
        history = (
            [SyncHistoryEntry(datetime=h["datetime"], content=h["content"]) for h in parsed_history]
            if isinstance(parsed_history, list)
            else []
        )
    except (ValueError, TypeError, KeyError):
        history = []
    return SyncDocument(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        parent_id=row["parent_id"],
        history=history,
        create_datetime=row["create_datetime"],
        update_datetime=row["update_datetime"],
        deleted=row["deleted"] == 1,
    )


def _json_compact(value) -> str:
    """等价 JS JSON.stringify：紧凑分隔符、不转义非 ASCII。"""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def decode_setting_value(raw: str) -> str | None:
    """upstream: db.ts:42-57 rowToSetting 的 value 怪癖。

    存储内容是 JSON.stringify 的产物：
    - 解析为字符串 → 原样返回；
    - 解析为 null/缺失 → None；
    - 其他标量/对象/数组 → 重新 JSON.stringify 为字符串；
    - JSON 解析失败 → None。
    """
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return None
    if isinstance(parsed, str):
        return parsed
    if parsed is None:
        return None
    return _json_compact(parsed)


def row_to_setting(row: sqlite3.Row) -> SyncSetting:
    return SyncSetting(
        key=row["key"],
        value=decode_setting_value(row["value"]),
        updated_at=row["updated_at"],
    )


# ---- 用户（upstream: db.ts:59-78）----


class GitHubUserInput(TypedDict):
    id: str
    github_id: int
    login: str
    name: str | None
    avatar: str | None


def upsert_user(conn: sqlite3.Connection, user: GitHubUserInput) -> None:
    """upstream: db.ts:59-74 upsertUser（按 github_id 冲突更新资料，不触碰 created_at）。"""
    conn.execute(
        """INSERT INTO users (id, github_id, login, name, avatar, created_at)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(github_id) DO UPDATE SET
             login = excluded.login,
             name = excluded.name,
             avatar = excluded.avatar""",
        (
            user["id"],
            user["github_id"],
            user["login"],
            user["name"],
            user["avatar"],
            now_ms(),
        ),
    )
    conn.commit()


def get_user_by_id(conn: sqlite3.Connection, user_id: str) -> UserRow | None:
    """upstream: db.ts:76-78 getUserById。"""
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return UserRow.from_row(row) if row is not None else None


def get_user_by_github_login(conn: sqlite3.Connection, login: str) -> UserRow | None:
    """upstream: plan.ts:146-156 getUserByGithubLogin（lower(login) 匹配）。"""
    from .plan import normalize_github_login

    row = conn.execute(
        "SELECT * FROM users WHERE lower(login) = ?",
        (normalize_github_login(login),),
    ).fetchone()
    return UserRow.from_row(row) if row is not None else None


def is_order_processed(conn: sqlite3.Connection, out_trade_no: str) -> bool:
    """upstream: plan.ts:158-164 isOrderProcessed（afdian_orders 幂等记录）。"""
    row = conn.execute(
        "SELECT out_trade_no FROM afdian_orders WHERE out_trade_no = ?",
        (out_trade_no,),
    ).fetchone()
    return row is not None


# ---- 文档计数（upstream: db.ts:80-94）----


def count_active_documents(conn: sqlite3.Connection, user_id: str) -> int:
    """upstream: countActiveDocuments；墓碑不计。"""
    row = conn.execute(
        "SELECT COUNT(*) AS count FROM documents WHERE user_id = ? AND deleted = 0",
        (user_id,),
    ).fetchone()
    return int(row["count"])


def count_stored_documents(conn: sqlite3.Connection, user_id: str) -> int:
    """upstream: countStoredDocuments；含墓碑。"""
    row = conn.execute(
        "SELECT COUNT(*) AS count FROM documents WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return int(row["count"])


# ---- 存量探查（upstream: db.ts:96-129）----


def chunk_document_ids(ids: list[str], size: int = D1_IN_ID_CHUNK) -> list[list[str]]:
    """upstream: db.ts:99-105 chunkDocumentIds（去重保序后分块）。"""
    unique = list(dict.fromkeys(ids))
    return [unique[i : i + size] for i in range(0, len(unique), size)]


def list_existing_documents(
    conn: sqlite3.Connection, user_id: str, ids: list[str]
) -> dict[str, bool]:
    """upstream: db.ts:108-129 listExistingDocuments；返回 id → 当前是否已删除。"""
    existing: dict[str, bool] = {}
    if not ids:
        return existing
    for chunk in chunk_document_ids(ids):
        placeholders = ", ".join("?" for _ in chunk)
        rows = conn.execute(
            f"SELECT id, deleted FROM documents WHERE user_id = ? AND id IN ({placeholders})",
            (user_id, *chunk),
        ).fetchall()
        for row in rows:
            existing[row["id"]] = int(row["deleted"]) == 1
    return existing


# ---- 增量拉取（upstream: db.ts:131-167）----


def pull_changes(
    conn: sqlite3.Connection,
    user_id: str,
    cursor: int,
) -> dict:
    """upstream: db.ts:132-167 pullChanges；严格 server_updated_at > cursor，升序。"""
    doc_rows = conn.execute(
        """SELECT id, title, content, parent_id, history, create_datetime,
                  update_datetime, deleted, server_updated_at
           FROM documents WHERE user_id = ? AND server_updated_at > ?
           ORDER BY server_updated_at ASC""",
        (user_id, cursor),
    ).fetchall()

    setting_rows = conn.execute(
        """SELECT key, value, updated_at, server_updated_at
           FROM settings WHERE user_id = ? AND server_updated_at > ?
           ORDER BY server_updated_at ASC""",
        (user_id, cursor),
    ).fetchall()

    max_cursor = cursor
    for row in doc_rows:
        max_cursor = max(max_cursor, row["server_updated_at"])
    for row in setting_rows:
        max_cursor = max(max_cursor, row["server_updated_at"])

    return {
        "documents": [row_to_document(r) for r in doc_rows],
        "settings": [row_to_setting(r) for r in setting_rows],
        "max_cursor": max_cursor,
    }


# ---- 推送合并（upstream: db.ts:169-246）----


def push_changes(
    conn: sqlite3.Connection,
    user_id: str,
    documents: list[SyncDocument],
    settings: list[SyncSetting],
    clock: Callable[[], int] = now_ms,
) -> dict:
    """upstream: db.ts:173-246 pushChanges。

    LWW：文档 existing.update_datetime >= 客户端值则跳过；
    设置 existing.updated_at >= 客户端值则跳过。
    服务端落库时间戳统一为 now；随后 pull(now-1) 回拉所有服务端新版本，
    maxCursor=now（clock 可注入仅用于测试）。
    """
    now = clock()

    with conn:
        for doc in documents:
            existing = conn.execute(
                "SELECT update_datetime FROM documents WHERE user_id = ? AND id = ?",
                (user_id, doc.id),
            ).fetchone()
            # upstream: db.ts:188 —— existing.ts >= client 即跳过
            if existing is not None and existing["update_datetime"] >= doc.update_datetime:
                continue

            conn.execute(
                """INSERT INTO documents
                     (user_id, id, title, content, parent_id, history,
                      create_datetime, update_datetime, deleted, server_updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(user_id, id) DO UPDATE SET
                     title = excluded.title,
                     content = excluded.content,
                     parent_id = excluded.parent_id,
                     history = excluded.history,
                     update_datetime = excluded.update_datetime,
                     deleted = excluded.deleted,
                     server_updated_at = excluded.server_updated_at""",
                (
                    user_id,
                    doc.id,
                    doc.title,
                    doc.content,
                    doc.parent_id,
                    _json_compact([h.to_api_dict() for h in doc.history]) if doc.history else "[]",
                    doc.create_datetime,
                    doc.update_datetime,
                    1 if doc.deleted else 0,
                    now,
                ),
            )

        for setting in settings:
            existing = conn.execute(
                "SELECT updated_at FROM settings WHERE user_id = ? AND key = ?",
                (user_id, setting.key),
            ).fetchone()
            # upstream: db.ts:226
            if existing is not None and existing["updated_at"] >= setting.updated_at:
                continue

            conn.execute(
                """INSERT INTO settings (user_id, key, value, updated_at, server_updated_at)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(user_id, key) DO UPDATE SET
                     value = excluded.value,
                     updated_at = excluded.updated_at,
                     server_updated_at = excluded.server_updated_at""",
                (
                    user_id,
                    setting.key,
                    _json_compact(setting.value),
                    setting.updated_at,
                    now,
                ),
            )

        # upstream: db.ts:244 —— 回拉 now-1，拿到服务端全部新版本（含被 LWW 拒绝的旧值）
        accepted = pull_changes(conn, user_id, now - 1)

    return {
        "documents": accepted["documents"],
        "settings": accepted["settings"],
        "max_cursor": now,
    }
