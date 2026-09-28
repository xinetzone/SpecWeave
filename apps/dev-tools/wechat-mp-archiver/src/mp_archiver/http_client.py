"""保守限速 + 指数退避的 HTTP 客户端。

- **请求节奏**：相邻请求间隔在 ``[delay_min, delay_max]`` 区间随机采样（均匀抖动）；
- **失败重试**：对超时/传输错误与可重试状态码（403/429/5xx）执行指数退避
  ``min(cap, base * 2**attempt) + 抖动``；
- **不重试**：401（凭证问题，重试无意义且增加风险）及 4xx 其他状态，交由调用方决策。

时钟、睡眠函数与随机源均可注入，便于确定性测试。
"""

import logging
import random
import time
from collections.abc import Callable
from urllib.parse import urlsplit

import httpx

from .config import Settings

logger = logging.getLogger(__name__)

RETRY_STATUSES = frozenset({403, 429, 500, 502, 503, 504})


class RateLimitedClient:
    """同步 HTTP 客户端（包装 :class:`httpx.Client`）。"""

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.BaseTransport | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
        rng: Callable[[float, float], float] = random.uniform,
    ) -> None:
        self._settings = settings
        self._sleep = sleeper
        self._clock = clock
        self._rng = rng
        self._last_request_at: float | None = None

        headers = {"User-Agent": settings.user_agent}
        token = settings.exporter_token.get_secret_value()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        kwargs: dict = {"timeout": settings.timeout, "headers": headers}
        if transport is not None:
            kwargs["transport"] = transport
        if settings.proxy_url:
            kwargs["proxy"] = settings.proxy_url
        self._client = httpx.Client(**kwargs)

    # ---- 节奏与退避 -------------------------------------------------

    def _pace(self) -> None:
        """保证相邻请求之间保持随机最小间隔。"""
        now = self._clock()
        if self._last_request_at is not None:
            desired = self._rng(
                self._settings.request_delay_min, self._settings.request_delay_max
            )
            wait = desired - (now - self._last_request_at)
            if wait > 0:
                self._sleep(wait)
        self._last_request_at = self._clock()

    def _backoff(self, attempt: int, *, method: str, url: str, reason: str) -> None:
        delay = min(
            self._settings.backoff_cap,
            self._settings.backoff_base * (2**attempt),
        ) + self._rng(0.0, 1.0)
        # 退避必须在日志中可见（TR-12.1）：只记录主机名，不记录 query，
        # 避免把完整文章链接（sn 等参数）写入演练/运行日志。
        # 畸形 URL 无 netloc 时不回退打印原文（可能含 query/userinfo）。
        host = urlsplit(url).netloc or "<unknown-host>"
        logger.warning(
            "HTTP 重试退避：%s %s 第 %d/%d 次请求失败（%s），%.2f 秒后重试",
            method.upper(),
            host,
            attempt + 1,
            self._settings.max_retries + 1,
            reason,
            delay,
        )
        self._sleep(delay)

    # ---- 请求 -------------------------------------------------------

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """执行带限速与重试的请求；重试用尽后：有响应则返回最后一个响应，无响应则抛出最后异常。"""
        last_exc: Exception | None = None
        for attempt in range(self._settings.max_retries + 1):
            self._pace()
            try:
                response = self._client.request(method, url, **kwargs)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_exc = exc
                if attempt >= self._settings.max_retries:
                    raise
                self._backoff(
                    attempt, method=method, url=url,
                    reason=exc.__class__.__name__,
                )
                continue

            if (
                response.status_code in RETRY_STATUSES
                and attempt < self._settings.max_retries
            ):
                self._backoff(
                    attempt, method=method, url=url,
                    reason=f"HTTP {response.status_code}",
                )
                continue
            return response

        # 理论不可达：循环要么 return，要么 raise
        if last_exc is not None:  # pragma: no cover
            raise last_exc
        raise RuntimeError("重试循环异常退出")  # pragma: no cover

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "RateLimitedClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
