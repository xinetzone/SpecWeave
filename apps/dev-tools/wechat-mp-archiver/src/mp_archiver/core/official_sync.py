"""官方接口同步编排（Task 8）：翻页→展开→去重入库，配额触顶优雅停止。"""

import logging
from dataclasses import dataclass

from ..adapters.official_api import (
    DailyQuotaGuard,
    DailyQuotaReached,
    OfficialApiAdapter,
    OfficialApiConfigError,
    PAGE_SIZE,
    parse_freepublish_page,
)
from ..config import Settings
from ..db import find_article_id, get_account_biz_by_alias, upsert_article
from ..exceptions import PayloadError
from ..models import ArticleStatus

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class OfficialSyncReport:
    enabled: bool = True
    biz: str = ""
    pages: int = 0
    inserted: int = 0
    updated: int = 0
    skipped_deleted: int = 0
    total_groups: int = 0
    quota_reached: bool = False


def sync_official_articles(
    conn,
    settings: Settings,
    client,
    *,
    account_alias: str,
) -> OfficialSyncReport:
    """从 freepublish/batchget 拉取自有号已发布图文并入 articles 表。

    无 app_id/app_secret 时返回 ``enabled=False`` 的空报告（不发起任何请求）；
    biz 解析顺序：显式配置 → R2 已同步数据按别名查找。
    """
    app_secret = settings.wechat_app_secret.get_secret_value().strip()
    if not settings.wechat_app_id.strip() or not app_secret:
        logger.info("未配置自有号 app_id/app_secret，官方源跳过")
        return OfficialSyncReport(enabled=False)

    biz = settings.wechat_official_biz.strip() or (
        get_account_biz_by_alias(conn, account_alias) or ""
    )
    if not biz:
        raise OfficialApiConfigError(
            "官方接口不返回 __biz，且 R2 数据中无该账号；"
            "请先执行 list 同步，或在 .env 配置 MP_ARCHIVER_WECHAT_OFFICIAL_BIZ"
        )

    guard = DailyQuotaGuard(
        settings.db_path.parent / "official_api_quota.json",
        settings.official_daily_call_cap,
    )
    adapter = OfficialApiAdapter(
        client, settings.wechat_app_id.strip(), app_secret
    )

    pages = inserted = updated = skipped_deleted = 0
    total_groups = 0
    offset = 0
    quota_reached = False

    while True:
        try:
            raw = adapter.batchget_page(offset=offset, guard=guard)
        except DailyQuotaReached as exc:
            logger.warning("官方源停止翻页：%s", exc)
            quota_reached = True
            break

        page = parse_freepublish_page(raw, biz=biz, alias=account_alias)

        # no_content=1 存在平台整体裁剪 content 的歧义：有群发组却展开 0 篇时，
        # 以 no_content=0 重取同一页，杜绝静默零产出
        if page.group_count > 0 and len(page.groups) == 0:
            logger.info(
                "offset=%s 返回 %s 组但无图文条目，以 no_content=0 重试该页",
                offset, page.group_count,
            )
            try:
                raw = adapter.batchget_page(
                    offset=offset, guard=guard, no_content=0
                )
            except DailyQuotaReached as exc:
                logger.warning("官方源停止翻页：%s", exc)
                quota_reached = True
                break
            page = parse_freepublish_page(raw, biz=biz, alias=account_alias)
            if page.group_count > 0 and len(page.groups) == 0:
                raise PayloadError(
                    f"offset={offset} 返回 {page.group_count} 个群发组但"
                    "no_content=0 重取后仍无图文条目，响应结构疑似变更"
                )

        pages += 1
        total_groups = page.total_groups

        for record in page.groups:
            if record.status == ArticleStatus.EXTERNAL_REF:
                skipped_deleted += 1
                continue
            existed = find_article_id(conn, record) is not None
            upsert_article(
                conn,
                record,
                preserve_status=True,  # 不回退 R2/正文阶段已取得的采集状态
                source="official_api",
            )
            if existed:
                updated += 1
            else:
                inserted += 1

        offset += page.group_count
        if page.group_count < PAGE_SIZE or offset >= page.total_groups:
            break

    return OfficialSyncReport(
        enabled=True,
        biz=biz,
        pages=pages,
        inserted=inserted,
        updated=updated,
        skipped_deleted=skipped_deleted,
        total_groups=total_groups,
        quota_reached=quota_reached,
    )
