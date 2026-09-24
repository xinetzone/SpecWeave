"""全量文章列表同步编排：翻页采集 → 幂等入库 → 水位与对账。"""

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
    completed: bool  # False 表示因 max_pages 截断，未到历史尾页
    final_offset: int


def _today_utc() -> str:
    return datetime.now(tz=timezone.utc).date().isoformat()


def sync_article_list(
    conn,
    adapter: ArticleListAdapter,
    *,
    name: str,
    max_pages: int | None = None,
    full_reconcile: bool = True,
) -> SyncReport:
    """同步指定公众号的全量历史文章元数据。

    - 已存在的文章只刷新元数据，保留既有采集状态（含 downloaded 不回退）；
    - 完整翻到尾页（``has_more=False``）后执行删除/不可见对账；``max_pages``
      截断时不对账，避免把未扫描区间误判为下架；
    - 遇登录态失效，先把凭证状态落库再向上抛出。
    """
    account: AccountRef = adapter.resolve_account(name)
    if not account.biz:
        raise CredentialExpiredError(
            -1,
            f"账号 {account.nickname!r} 解析不到 __biz；无法判断登录态与拉取列表",
        )

    offset = 0
    pages = 0
    inserted = 0
    updated = 0
    skipped_non_article = 0
    visible_ids: set[int] = set()
    completed = False

    try:
        while True:
            page = adapter.fetch_history_page(account, offset)
            pages += 1

            for record in page.articles:
                existed = find_article_id(conn, record) is not None
                article_id = upsert_article(conn, record, preserve_status=True)
                visible_ids.add(article_id)
                if existed:
                    updated += 1
                else:
                    inserted += 1

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

    upsert_sync_state(
        conn,
        account.biz,
        account_alias=account.nickname,
        last_cursor=str(offset),
        total_seen=count_articles(conn, account.biz),
        credential_status=CredentialStatus.VALID,
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
    )
