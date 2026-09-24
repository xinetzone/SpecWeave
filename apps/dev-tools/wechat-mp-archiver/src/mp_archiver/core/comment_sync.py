"""评论与互动指标的条件采集（Task 7 / AC-7）。

接口形态依据微信网页端公开文章的既有接口共识，属经验值，真实联调时以
抓包实测为准并在本模块校准：
- 评论列表：``GET /mp/appmsg_comment?action=getcomment``（精选评论+回复）；
- 互动指标：``POST /mp/getappmsgext``（阅读/点赞/在看/转发/评论数）。

凭证策略（TR-7.2）：开关关闭 → 不采集也不登记；开关开启但无凭证/凭证失效 →
metrics 写 ``skipped_no_credential``，主流程成功退出；仅真实网络/解析异常
才记 ``failed``，且不影响正文归档主流程。
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx

from ..config import Settings
from ..db import insert_metrics_snapshot, upsert_comment
from ..exceptions import ApiRetError, CredentialExpiredError, PayloadError
from .credentials import WebCredentials, load_web_credentials

logger = logging.getLogger(__name__)

COMMENT_ENDPOINT = "https://mp.weixin.qq.com/mp/appmsg_comment"
METRICS_ENDPOINT = "https://mp.weixin.qq.com/mp/getappmsgext"
COMMENT_PAGE_SIZE = 100
MAX_COMMENT_PAGES = 20  # 单篇 2000 条硬上限，防异常分页死循环

# 凭证失效类 ret（经验值，实测校准）
_CREDENTIAL_RET_CODES = {200002, 200003, 200013, 200004}

STATE_DISABLED = "disabled"
STATE_COLLECTED = "collected"
STATE_SKIPPED = "skipped_no_credential"
STATE_FAILED = "failed"


@dataclass(frozen=True, slots=True)
class CommentEntry:
    comment_id: str
    user_name: str
    content: str
    like_count: int
    create_time: str | None


@dataclass(frozen=True, slots=True)
class MetricsSnapshot:
    read_count: int | None
    like_count: int | None
    old_like_count: int | None
    share_count: int | None
    comment_count: int | None


@dataclass(frozen=True, slots=True)
class InteractionOutcome:
    state: str
    comments_written: int = 0
    error: str = ""


def _loads_json_lenient(text: str) -> dict:
    """兼容裸 JSON 与 JSONP 包裹（``cb({...})``）两种响应形态。"""
    stripped = text.strip()
    if stripped.startswith("{"):
        payload = json.loads(stripped)
    else:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise PayloadError("响应不是 JSON/JSONP 文本")
        payload = json.loads(stripped[start : end + 1])
    if not isinstance(payload, dict):
        raise PayloadError("响应根节点不是对象")
    return payload


def _check_base_resp(payload: dict) -> None:
    base = payload.get("base_resp") or {}
    ret = int(base.get("ret", 0) or 0)
    if ret == 0:
        return
    errmsg = str(base.get("errmsg") or "")
    if ret in _CREDENTIAL_RET_CODES:
        raise CredentialExpiredError(ret, errmsg or "互动接口凭证失效")
    raise ApiRetError(ret, errmsg)


def _iso_from_unix(value) -> str | None:
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).isoformat(
            timespec="seconds"
        )
    except (TypeError, ValueError):
        return None


def parse_comments(payload: dict) -> tuple[list[CommentEntry], int | None]:
    """解析 getcomment 响应：精选评论及其作者回复。

    返回 ``(条目列表, 平台宣称总条数)``；回复 id 形如 ``{父id}#r{reply_id}``。
    """
    _check_base_resp(payload)
    raw_entries = payload.get("elected_comment") or []
    if not isinstance(raw_entries, list):
        raise PayloadError("elected_comment 不是数组")

    entries: list[CommentEntry] = []
    for raw in raw_entries:
        if not isinstance(raw, dict):
            continue
        parent_id = str(raw.get("content_id") or raw.get("id") or "").strip()
        if not parent_id:
            continue
        entries.append(
            CommentEntry(
                comment_id=parent_id,
                user_name=str(raw.get("nick_name") or ""),
                content=str(raw.get("content") or ""),
                like_count=int(raw.get("like_num") or 0),
                create_time=_iso_from_unix(raw.get("create_time")),
            )
        )
        replies = ((raw.get("reply") or {}).get("elected_reply")) or []
        if isinstance(replies, list):
            for index, reply in enumerate(replies):
                if not isinstance(reply, dict):
                    continue
                reply_id = str(
                    reply.get("reply_id") or reply.get("id") or index
                ).strip()
                entries.append(
                    CommentEntry(
                        comment_id=f"{parent_id}#r{reply_id}",
                        user_name=str(reply.get("nick_name") or ""),
                        content=str(reply.get("content") or ""),
                        like_count=int(reply.get("like_num") or 0),
                        create_time=_iso_from_unix(reply.get("create_time")),
                    )
                )

    total = payload.get("elected_comment_total_cnt")
    total_count = int(total) if isinstance(total, int) else None
    return entries, total_count


def parse_metrics(payload: dict) -> MetricsSnapshot:
    """解析 getappmsgext 响应中的 appmsgstat 计数块。"""
    _check_base_resp(payload)
    stats = payload.get("appmsgstat")
    if not isinstance(stats, dict):
        raise PayloadError("响应缺少 appmsgstat 计数块（可能凭证权限不足）")

    def _int(key: str) -> int | None:
        value = stats.get(key)
        return int(value) if isinstance(value, int) else None

    return MetricsSnapshot(
        read_count=_int("read_num"),
        like_count=_int("like_num"),
        old_like_count=_int("old_like_num"),
        share_count=_int("share_num"),
        comment_count=_int("comment_num"),
    )


def _comment_page(client, credentials: WebCredentials, article, offset: int) -> dict:
    params = {
        "action": "getcomment",
        "__biz": article["biz"],
        "appmsgid": article["mid"],
        "idx": article["idx"],
        "comment_id": "",
        "offset": offset,
        "limit": COMMENT_PAGE_SIZE,
        "sendTime": "",
        "appmsg_token": credentials.appmsg_token,
        "pass_ticket": credentials.pass_ticket,
    }
    response = client.get(
        f"{COMMENT_ENDPOINT}?{urlencode(params)}",
        headers={"Referer": article["url"] or "https://mp.weixin.qq.com/"},
    )
    if response.status_code in (401, 403):
        raise CredentialExpiredError(0, f"评论接口 HTTP {response.status_code}")
    return _loads_json_lenient(response.text)


def _fetch_all_comments(client, credentials: WebCredentials, article) -> list[CommentEntry]:
    if not article["mid"] or article["idx"] is None:
        return []
    collected: list[CommentEntry] = []
    parent_count = 0  # total_cnt 只计主评论，回复不计入翻页终止判断
    for page in range(MAX_COMMENT_PAGES):
        payload = _comment_page(client, credentials, article, page * COMMENT_PAGE_SIZE)
        entries, total = parse_comments(payload)
        if not entries:
            break
        collected.extend(entries)
        parent_count += sum(1 for entry in entries if "#r" not in entry.comment_id)
        if total is not None and parent_count >= total:
            break
    return collected


def _fetch_metrics(client, credentials: WebCredentials, article) -> tuple[MetricsSnapshot, str]:
    query = {
        "__biz": article["biz"],
        "mid": article["mid"] or "",
        "idx": article["idx"] if article["idx"] is not None else "",
        "sn": article["sn"] or "",
        "appmsg_token": credentials.appmsg_token,
        "pass_ticket": credentials.pass_ticket,
    }
    form = {
        "is_only_read": "1",
        "is_temp_url": "0",
        "appmsg_type": "9",
    }
    response = client.post(
        f"{METRICS_ENDPOINT}?{urlencode(query)}",
        data=form,
        headers={"Referer": article["url"] or "https://mp.weixin.qq.com/"},
    )
    if response.status_code in (401, 403):
        raise CredentialExpiredError(0, f"指标接口 HTTP {response.status_code}")
    payload = _loads_json_lenient(response.text)
    return parse_metrics(payload), json.dumps(payload, ensure_ascii=False)


def _record_skip(conn, article, reason: str) -> None:
    insert_metrics_snapshot(
        conn,
        article_id=article["id"],
        status=STATE_SKIPPED,
        fail_reason=reason[:300],
    )


def sync_article_interactions(
    conn, settings: Settings, client, article
) -> InteractionOutcome:
    """单篇文章的互动数据采集；任何异常不外抛（主流程必须继续）。"""
    if not settings.fetch_metrics:
        return InteractionOutcome(STATE_DISABLED)

    credentials = load_web_credentials(settings)
    if credentials is None:
        _record_skip(conn, article, "missing_credentials")
        logger.info("文章 id=%s 跳过互动采集：未配置 appmsg_token/pass_ticket",
                    article["id"])
        return InteractionOutcome(STATE_SKIPPED)

    try:
        comments = _fetch_all_comments(client, credentials, article)
        for entry in comments:
            upsert_comment(
                conn,
                article_id=article["id"],
                comment_id=entry.comment_id,
                user_name=entry.user_name,
                content=entry.content,
                like_count=entry.like_count,
                create_time=entry.create_time,
            )
        conn.commit()

        snapshot, raw_json = _fetch_metrics(client, credentials, article)
        insert_metrics_snapshot(
            conn,
            article_id=article["id"],
            status=STATE_COLLECTED,
            read_count=snapshot.read_count,
            like_count=snapshot.like_count,
            old_like_count=snapshot.old_like_count,
            share_count=snapshot.share_count,
            comment_count=snapshot.comment_count
            if snapshot.comment_count is not None
            else len(comments),
            raw_json=raw_json,
        )
        return InteractionOutcome(STATE_COLLECTED, comments_written=len(comments))
    except CredentialExpiredError as exc:
        _record_skip(conn, article, f"credential_expired: {exc}")
        logger.warning("文章 id=%s 互动采集跳过：凭证失效", article["id"])
        return InteractionOutcome(STATE_SKIPPED, error=str(exc)[:200])
    except (ApiRetError, PayloadError, httpx.HTTPError, OSError) as exc:
        insert_metrics_snapshot(
            conn,
            article_id=article["id"],
            status=STATE_FAILED,
            fail_reason=f"{type(exc).__name__}: {exc}"[:300],
        )
        logger.warning("文章 id=%s 互动采集失败：%s", article["id"], exc)
        return InteractionOutcome(STATE_FAILED, error=str(exc)[:200])
    except Exception as exc:  # noqa: BLE001 - 互动采集绝不中断归档主流程
        insert_metrics_snapshot(
            conn,
            article_id=article["id"],
            status=STATE_FAILED,
            fail_reason=f"{type(exc).__name__}: {exc}"[:300],
        )
        logger.warning("文章 id=%s 互动采集意外失败：%s", article["id"], exc)
        return InteractionOutcome(STATE_FAILED, error=str(exc)[:200])
