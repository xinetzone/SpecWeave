"""微信公众号平台历史消息接口（profile_ext?action=getmsg）响应解析。

该接口的响应结构为公开且长期稳定的事实，被各类导出工具广泛使用：

- 顶层 ``ret``/``errmsg`` 为平台返回码，``general_msg_list`` 是 **JSON 字符串**
  （注意二次编码），其 ``list`` 为群发批次数组；
- 每个批次 ``comm_msg_info`` 含 ``id``/``type``/``datetime``，``type == 49``
  表示图文消息；图文内容在 ``app_msg_ext_info``，首条为主图文，
  其余在 ``multi_app_msg_item_list``（一次群发最多 8 条）；
- 文章标识从 ``content_url`` 查询串解析：``__biz``/``mid``/``idx``/``sn``。

采集服务（exporter/wechat-download-api）多数情况下透传该结构；
若服务做了规范化包装，需要在端到端实测后在此模块扩展解析分支。
"""

import html
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from ..exceptions import ApiRetError, CredentialExpiredError, PayloadError
from ..models import ArticleRecord, ArticleStatus
from .base import AccountRef, HistoryPage

# 平台返回码中明确表示登录态失效的码（社区工具共识值，实测中遇到再扩充）。
CREDENTIAL_EXPIRED_RETS = frozenset({200013})

# 图文消息类型
APPMSG_TYPE = 49

# 原创声明标记；微信 copyright_stat == 11 为经验值，待实测校准
COPYRIGHT_STAT_ORIGINAL = 11

__all__ = [
    "ApiRetError",
    "CredentialExpiredError",
    "PayloadError",
    "ArticleUrlParts",
    "parse_article_url",
    "parse_history_page",
    "parse_accounts",
    "select_account",
]


@dataclass(frozen=True, slots=True)
class ArticleUrlParts:
    """文章 ``content_url`` 中解析出的标识。"""

    biz: str | None
    mid: str | None
    idx: int | None
    sn: str | None


def parse_article_url(url: str) -> ArticleUrlParts:
    """从文章永久链接解析 ``__biz``/``mid``/``idx``/``sn``。"""
    if not url:
        return ArticleUrlParts(None, None, None, None)
    query = parse_qs(urlparse(html.unescape(url)).query)

    def first(key: str) -> str | None:
        values = query.get(key)
        return values[0] if values else None

    raw_idx = first("idx")
    try:
        idx = int(raw_idx) if raw_idx is not None else None
    except ValueError:
        idx = None
    return ArticleUrlParts(biz=first("__biz"), mid=first("mid"), idx=idx, sn=first("sn"))


def _to_iso_datetime(timestamp: object) -> str | None:
    try:
        value = int(timestamp)
    except (TypeError, ValueError):
        return None
    # 微信时间戳为 Unix 秒；统一存带时区的 UTC ISO8601
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def _build_record(
    info: dict,
    *,
    account_biz: str | None,
    account_alias: str,
    default_idx: int,
    publish_time: str | None,
) -> ArticleRecord | None:
    url = html.unescape(str(info.get("content_url") or ""))
    parts = parse_article_url(url)
    biz = parts.biz or account_biz
    if not biz or not parts.mid:
        # biz+mid 是最小归档标识；缺失说明不是可归档图文
        return None

    idx = parts.idx if parts.idx is not None else default_idx
    try:
        copyright_stat = int(info.get("copyright_stat") or 0)
    except (TypeError, ValueError):
        copyright_stat = 0

    return ArticleRecord(
        biz=biz,
        account_alias=account_alias,
        mid=str(parts.mid),
        idx=idx,
        sn=parts.sn,
        title=str(info.get("title") or "").strip(),
        author=str(info.get("author") or "").strip(),
        publish_time=publish_time,
        url=url or None,
        cover_url=str(info.get("cover") or "") or None,
        digest=str(info.get("digest") or "").strip(),
        is_original=(copyright_stat == COPYRIGHT_STAT_ORIGINAL),
        album="",  # 列表接口无稳定合集字段，正文采集阶段回填
        status=ArticleStatus.PENDING,
    )


def _iter_appmsg_items(batch: dict):
    """产出 (图文信息 dict, 条位 idx 兜底) 序列：主图文 + 多图文。"""
    info = batch.get("app_msg_ext_info")
    if isinstance(info, dict):
        yield info, 1
        multi = info.get("multi_app_msg_item_list") or []
        for position, item in enumerate(multi, start=2):
            if isinstance(item, dict):
                yield item, position


def parse_history_page(
    payload: dict,
    *,
    account_alias: str = "",
    account_biz: str | None = None,
) -> HistoryPage:
    """解析一页历史消息响应为 :class:`HistoryPage`。

    ``account_biz`` 用于个别 ``content_url`` 缺 ``__biz`` 时的兜底。
    """
    if not isinstance(payload, dict):
        raise PayloadError(f"历史消息响应不是 JSON 对象：{type(payload).__name__}")

    ret = payload.get("ret", 0)
    if ret not in (0, None):
        try:
            ret_int = int(ret)
        except (TypeError, ValueError):
            ret_int = -1
        message = str(payload.get("errmsg") or "")
        if ret_int in CREDENTIAL_EXPIRED_RETS:
            raise CredentialExpiredError(ret_int, message)
        raise ApiRetError(ret_int, message)

    raw_list = payload.get("general_msg_list")
    if isinstance(raw_list, str):
        if not raw_list.strip():
            batches: list = []
        else:
            try:
                batches = json.loads(raw_list).get("list", [])
            except (ValueError, AttributeError) as exc:
                raise PayloadError(f"general_msg_list 不是合法 JSON：{exc}") from exc
    elif isinstance(raw_list, dict):
        batches = raw_list.get("list", [])
    else:
        # 兼容采集服务可能的轻包装：{"list": [<原生批次>...]} / {"items": [...]}
        batches = payload.get("list") or payload.get("items") or []

    if not isinstance(batches, list):
        raise PayloadError("消息批次列表字段 list 不是数组")

    articles: list[ArticleRecord] = []
    skipped_non_article = 0
    for batch in batches:
        if not isinstance(batch, dict):
            continue
        comm = batch.get("comm_msg_info")
        if not isinstance(comm, dict) or int(comm.get("type") or 0) != APPMSG_TYPE:
            skipped_non_article += 1
            continue
        publish_time = _to_iso_datetime(comm.get("datetime"))
        for info, position in _iter_appmsg_items(batch):
            record = _build_record(
                info,
                account_biz=account_biz,
                account_alias=account_alias,
                default_idx=position,
                publish_time=publish_time,
            )
            if record is not None:
                articles.append(record)

    try:
        next_offset = int(payload.get("next_offset") or 0)
    except (TypeError, ValueError):
        next_offset = 0
    has_more = str(payload.get("can_msg_continue", "0")) in ("1", "true", "True")

    return HistoryPage(
        articles=tuple(articles),
        next_offset=next_offset,
        has_more=has_more,
        skipped_non_article=skipped_non_article,
    )


# ---------------------------------------------------------------------------
# 公众号搜索（searchbiz）响应解析
# ---------------------------------------------------------------------------


def _extract_biz(item: dict) -> str:
    """从搜索结果项中尽力取得 __biz：显式字段或任意文章链接。"""
    for key in ("__biz", "biz"):
        value = item.get(key)
        if value:
            return str(value)
    for key in ("content_url", "article_url", "url", "link"):
        value = item.get(key)
        if isinstance(value, str) and "__biz=" in value:
            parsed = parse_article_url(value)
            if parsed.biz:
                return parsed.biz
    return ""


def parse_accounts(payload: dict) -> tuple[AccountRef, ...]:
    """解析公众号搜索结果（微信原生 ``searchbiz`` 或采集服务轻包装）。"""
    if not isinstance(payload, dict):
        raise PayloadError(f"搜索响应不是 JSON 对象：{type(payload).__name__}")

    base = payload.get("base_resp") if isinstance(payload.get("base_resp"), dict) else {}
    ret = payload.get("ret", base.get("ret", 0))
    if ret not in (0, None):
        try:
            ret_int = int(ret)
        except (TypeError, ValueError):
            ret_int = -1
        message = str(payload.get("errmsg") or base.get("errmsg") or "")
        if ret_int in CREDENTIAL_EXPIRED_RETS:
            raise CredentialExpiredError(ret_int, message)
        raise ApiRetError(ret_int, message)

    raw_items = payload.get("list")
    if isinstance(raw_items, str):
        try:
            raw_items = json.loads(raw_items or "[]")
        except ValueError as exc:
            raise PayloadError(f"搜索 list 不是合法 JSON：{exc}") from exc
    if raw_items is None:
        raw_items = payload.get("items") or []
    if not isinstance(raw_items, list):
        raise PayloadError("搜索结果 list 不是数组")

    accounts: list[AccountRef] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        fakeid = item.get("fakeid", item.get("fake_id", ""))
        accounts.append(
            AccountRef(
                nickname=str(item.get("nickname") or item.get("name") or "").strip(),
                alias=str(item.get("alias") or "").strip(),
                fakeid=str(fakeid or ""),
                biz=_extract_biz(item),
            )
        )
    return tuple(accounts)


def select_account(accounts: tuple[AccountRef, ...], name: str) -> AccountRef | None:
    """按名称选择账号：精确（昵称或微信号）优先，其次包含匹配。"""
    target = name.strip()
    if not target:
        return None
    for account in accounts:
        if account.nickname == target or account.alias == target:
            return account
    for account in accounts:
        if target in account.nickname or (account.alias and target in account.alias):
            return account
    return None
