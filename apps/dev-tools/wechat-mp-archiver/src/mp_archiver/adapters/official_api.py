"""微信公众平台官方接口条件适配（R1，Task 8 / AC-13）。

仅在用户配置认证服务号的 ``app_id``/``app_secret`` 时启用，承载
``freepublish/batchget``（已发布图文列表）。接口边界（2026-09 时点，
以官方文档为准）：

- 只覆盖「发布成功」的图文素材（含"发表不通知"内容），**不返回群发历史**，
  历史全量仍以 R2（采集服务）为主；
- 2025-07 起个人/未认证主体相关权限被回收，调用返回 ``errcode=48001``；
- 接口有日调用配额（经验约 100 次/日），由 :class:`DailyQuotaGuard` 守护。
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from ..exceptions import ApiRetError, PayloadError
from ..models import ArticleRecord, ArticleStatus

logger = logging.getLogger(__name__)

API_BASE = "https://api.weixin.qq.com/cgi-bin"
PAGE_SIZE = 20  # batchget 单页最大群发条数

# token 失效类错误码（强制刷新一次后重试）
_TOKEN_INVALID_CODES = {40001, 40014, 42001}
# 权限被回收/未获得接口权限
_PERMISSION_DENIED_CODES = {48001}


class OfficialApiPermissionError(RuntimeError):
    """48001：主体无接口权限（2025-07 后个人/未认证主体常态）。"""


class OfficialApiConfigError(RuntimeError):
    """启用官方源但缺少必要配置（app_id/secret/biz）。"""


class DailyQuotaReached(RuntimeError):
    """当日 batchget 调用次数已达本地安全阈值。"""


@dataclass(frozen=True, slots=True)
class FreepublishPage:
    total_groups: int  # 平台记录的已发布群发总数
    groups: tuple[ArticleRecord, ...]  # 展开后的图文条目（一条群发可含多篇）
    group_count: int  # 本页群发条数（翻页 offset 据此推进）


def _safe_int(value: object, default: int = 0) -> int:
    """宽松整数转换：bool 原样取整，非法字符串/容器回退默认值。"""
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_iso(timestamp: object) -> str | None:
    try:
        value = int(timestamp)
    except (TypeError, ValueError):
        return None
    if value <= 0:
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        # 超大时间戳在部分平台抛 OverflowError/OSError
        return None


def _query_params(url: str) -> dict[str, str]:
    if not url:
        return {}
    return {k: v[0] for k, v in parse_qs(urlsplit(url).query).items() if v}


def parse_freepublish_page(payload: dict, *, biz: str, alias: str) -> FreepublishPage:
    """解析 batchget 响应并展开为 ArticleRecord 列表。

    已删除条目（``is_deleted=true``）以内存态 ``status=EXTERNAL_REF`` 标记
    （该枚举此处仅作内部传递标记，调用方一律跳过、不入库），调用方决定登记或跳过。
    """
    errcode = _safe_int(payload.get("errcode"))
    if errcode in _PERMISSION_DENIED_CODES:
        raise OfficialApiPermissionError(
            f"官方接口权限不足 errcode={errcode}: {payload.get('errmsg')}"
        )
    if errcode != 0:
        raise ApiRetError(errcode, str(payload.get("errmsg") or ""))

    total = _safe_int(payload.get("total_count"))
    if "item" not in payload:
        # 正常空尾页表现为 total_count=0；total>0 却无 item 属于结构异常，
        # 不能静默按空页收尾（会导致整轮零产出）
        if total > 0:
            raise PayloadError(
                "freepublish/batchget 响应 total_count>0 但缺失 item 数组"
            )
        items = []
    else:
        items = payload.get("item")
        if not isinstance(items, list):
            # item 契约为群发记录数组；非 list 说明响应结构已变更，不能静默翻页
            raise PayloadError("freepublish/batchget 响应 item 字段非数组")

    records: list[ArticleRecord] = []
    for group in items:
        if not isinstance(group, dict):
            continue
        article_id = str(group.get("article_id") or "").strip()
        update_time = _to_iso(group.get("update_time"))
        content = group.get("content")
        news_items = content.get("news_item") if isinstance(content, dict) else None
        if not article_id or not isinstance(news_items, list):
            # content/news_item 缺失：no_content=1 时可能被平台整体裁剪，
            # 由编排层识别"有组无条目"并以 no_content=0 重试，这里不计入展开
            continue
        for seq, news in enumerate(news_items, start=1):
            if not isinstance(news, dict):
                continue
            url = str(news.get("url") or "")
            params = _query_params(url)
            # 身份键优先取图文 URL 中的 mid/idx/sn（与 R2 公开页同构，跨源可合并）；
            # URL 缺参时退化到群发 article_id 与组内序号
            mid = params.get("mid") or article_id
            idx = _safe_int(params.get("idx"), default=seq) or seq
            record = ArticleRecord(
                biz=biz,
                account_alias=alias,
                mid=mid,
                idx=idx,
                sn=params.get("sn"),
                title=str(news.get("title") or ""),
                author=str(news.get("author") or ""),
                publish_time=update_time,
                url=url or None,
                cover_url=str(news.get("thumb_url") or "") or None,
                digest=str(news.get("digest") or ""),
            )
            if _safe_int(news.get("is_deleted")) == 1:
                # frozen dataclass：以官方删除状态覆盖默认 pending
                object.__setattr__(record, "status", ArticleStatus.EXTERNAL_REF)
            records.append(record)

    return FreepublishPage(
        total_groups=total,
        groups=tuple(records),
        group_count=len(items),
    )


class DailyQuotaGuard:
    """batchget 当日调用计数（持久化 JSON，跨进程/重跑生效）。

    状态文件损坏（非法 JSON、非对象、字段类型异常）一律按零计数安全重置。
    """

    def __init__(self, state_path: str | Path, cap: int) -> None:
        self.path = Path(state_path)
        self.cap = cap
        self.day = datetime.now(tz=timezone.utc).date().isoformat()
        self.calls = self._load()

    def _load(self) -> int:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0
        if not isinstance(data, dict) or data.get("date") != self.day:
            return 0
        return max(0, _safe_int(data.get("calls")))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"date": self.day, "calls": self.calls}, ensure_ascii=False),
            encoding="utf-8",
        )

    @property
    def remaining(self) -> int:
        return max(0, self.cap - self.calls)

    def acquire(self) -> None:
        if self.calls >= self.cap:
            raise DailyQuotaReached(
                f"batchget 当日调用已达安全阈值 {self.cap}（次日 UTC 0 点重置）"
            )
        self.calls += 1
        self._save()


class OfficialApiAdapter:
    """access_token 生命周期 + freepublish/batchget 翻页。"""

    def __init__(self, client, app_id: str, app_secret: str) -> None:
        self._client = client
        self._app_id = app_id
        self._app_secret = app_secret
        self._token = ""
        self._token_expires_at = 0.0

    def _request_token(self) -> None:
        response = self._client.get(
            f"{API_BASE}/token",
            params={
                "grant_type": "client_credential",
                "appid": self._app_id,
                "secret": self._app_secret,
            },
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise PayloadError("access_token 响应非 JSON 对象")
        errcode = _safe_int(payload.get("errcode"))
        if errcode in _PERMISSION_DENIED_CODES:
            raise OfficialApiPermissionError(
                f"获取 access_token 被拒 errcode={errcode}: {payload.get('errmsg')}"
            )
        if errcode != 0 or not payload.get("access_token"):
            raise ApiRetError(errcode, str(payload.get("errmsg") or "无 access_token"))
        self._token = str(payload["access_token"])
        expires_in = _safe_int(payload.get("expires_in"), default=7200)
        # 提前 300 秒过期，规避边界失效
        self._token_expires_at = time.time() + max(60, expires_in - 300)

    def _get_token(self, *, force: bool = False) -> str:
        if force or not self._token or time.time() >= self._token_expires_at:
            self._request_token()
        return self._token

    def _batchget_raw(self, *, offset: int, token: str, no_content: int) -> dict:
        response = self._client.post(
            f"{API_BASE}/freepublish/batchget",
            params={"access_token": token},
            json={"offset": offset, "count": PAGE_SIZE, "no_content": no_content},
        )
        payload = response.json()
        if not isinstance(payload, dict):
            raise PayloadError("freepublish/batchget 响应非 JSON 对象")
        return payload

    def batchget_page(
        self,
        *,
        offset: int,
        guard: DailyQuotaGuard,
        no_content: int = 1,
    ) -> dict:
        """取一页原始 JSON；token 失效自动刷新一次；调用前过配额守护。

        ``no_content=1`` 为默认省流形态；若平台裁剪了承载 news_item 的
        content 对象（文档存在两层同名歧义），调用方应以 ``no_content=0``
        重取同一页。
        """
        guard.acquire()
        token = self._get_token()
        payload = self._batchget_raw(offset=offset, token=token,
                                     no_content=no_content)
        errcode = _safe_int(payload.get("errcode"))
        if errcode in _TOKEN_INVALID_CODES:
            logger.info("access_token 失效（errcode=%s），刷新后重试一次", errcode)
            token = self._get_token(force=True)
            payload = self._batchget_raw(offset=offset, token=token,
                                         no_content=no_content)
        return payload
