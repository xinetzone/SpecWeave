"""全量文章列表同步编排：翻页采集 → 幂等入库 → 水位与对账。"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from ..adapters.base import AccountRef, ArticleListAdapter
from ..adapters.wechat_payload import CredentialExpiredError
from ..db import (
    count_articles,
    find_article_id,
    mark_articles_not_visible,
    upsert_article,
    upsert_sync_state,
)
from ..models import CredentialStatus

# sync_state.extras 中「曾完成过完整全量扫描」的标记键
FULL_COMPLETED_KEY = "full_completed_at"


@dataclass(frozen=True, slots=True)
class SyncReport:
    """一次列表同步的结果摘要。"""

    account_name: str
    biz: str
    pages: int
    inserted: int
    updated: int
    skipped_non_article: int
    hidden_marked: int
    completed: bool  # False 表示因 max_pages 截断或增量追平，未到历史尾页
    final_offset: int
    caught_up: bool = False  # True 表示增量模式在「全已知页」提前追平停止


def _today_utc() -> str:
    return datetime.now(tz=timezone.utc).date().isoformat()


def _has_completed_full_scan(conn, account_biz: str) -> bool:
    """读取水位 extras，判断该账号历史上是否完成过到尾页的全量扫描。

    增量提前停止以此为前提：若上一轮全量曾被截断（无标记），增量不得在
    全已知页停止，否则会永久漏掉截断点之后更旧的未入库文章。
    """
    row = conn.execute(
        "SELECT extras FROM sync_state WHERE account_biz = ?",
        (account_biz,),
    ).fetchone()
    if not row or not row["extras"]:
        return False
    try:
        return bool(json.loads(row["extras"]).get(FULL_COMPLETED_KEY))
    except (json.JSONDecodeError, TypeError):
        return False


def sync_article_list(
    conn,
    adapter: ArticleListAdapter,
    *,
    name: str,
    max_pages: int | None = None,
    full_reconcile: bool = True,
    catch_up: bool = False,
) -> SyncReport:
    """同步指定公众号的全量历史文章元数据。

    - 已存在的文章只刷新元数据，保留既有采集状态（含 downloaded 不回退）；
    - 完整翻到尾页（``has_more=False``）后执行删除/不可见对账；``max_pages``
      截断或增量追平时不对账，避免把未扫描区间误判为下架；
    - ``catch_up=True`` 增量模式：列表按最新在前翻页，某页全部为已知文章时
      提前停止（零新增即追平）。该提前停止仅在此前完成过全量扫描（水位
      extras 有完成标记）时允许，防止「全量被 kill 后跑增量」永久漏文；
    - 遇登录态失效，先把凭证状态落库再向上抛出。
    """
    account: AccountRef = adapter.resolve_account(name)
    if not account.biz:
        raise CredentialExpiredError(
            -1,
            f"账号 {account.nickname!r} 解析不到 __biz；无法判断登录态与拉取列表",
        )

    prior_full = _has_completed_full_scan(conn, account.biz) if catch_up else False

    offset = 0
    pages = 0
    inserted = 0
    updated = 0
    skipped_non_article = 0
    visible_ids: set[int] = set()
    completed = False
    caught_up_flag = False

    try:
        while True:
            page = adapter.fetch_history_page(account, offset)
            pages += 1
            page_inserted = 0

            for record in page.articles:
                existed = find_article_id(conn, record) is not None
                article_id = upsert_article(conn, record, preserve_status=True)
                visible_ids.add(article_id)
                if existed:
                    updated += 1
                else:
                    inserted += 1
                    page_inserted += 1

            skipped_non_article += page.skipped_non_article

            # 先推进游标（尾页也可能携带最终 offset），再判断是否结束
            if page.next_offset and page.next_offset != offset:
                offset = page.next_offset
            elif page.has_more and page.articles:
                # 游标缺失时的保底推进
                offset += 10

            if not page.has_more:
                completed = True
                break
            if not page.articles:
                # 有续页标记但本页为空：停止，避免空转死循环
                completed = True
                break
            if max_pages is not None and pages >= max_pages:
                break
            if catch_up and prior_full and page_inserted == 0:
                # 增量追平：本页全部为库中已知文章，更新的文章在更旧一侧，
                # 无需继续翻页；未扫描区间不做下架对账。
                caught_up_flag = True
                break

    except CredentialExpiredError:
        upsert_sync_state(
            conn,
            account.biz,
            account_alias=account.nickname,
            credential_status=CredentialStatus.EXPIRED,
        )
        raise

    hidden_marked = 0
    if completed and full_reconcile and visible_ids:
        hidden_marked = mark_articles_not_visible(
            conn,
            account.biz,
            visible_ids,
            reason=f"not_visible_in_full_scan@{_today_utc()}",
        )

    # 仅完整到尾页才写入/刷新全量完成标记；增量与截断保留既有 extras
    extras = (
        json.dumps({FULL_COMPLETED_KEY: _today_utc()}, ensure_ascii=False)
        if completed
        else None
    )
    upsert_sync_state(
        conn,
        account.biz,
        account_alias=account.nickname,
        last_cursor=str(offset),
        total_seen=count_articles(conn, account.biz),
        credential_status=CredentialStatus.VALID,
        extras=extras,
    )

    return SyncReport(
        account_name=account.nickname,
        biz=account.biz,
        pages=pages,
        inserted=inserted,
        updated=updated,
        skipped_non_article=skipped_non_article,
        hidden_marked=hidden_marked,
        completed=completed,
        final_offset=offset,
        caught_up=caught_up_flag,
    )
