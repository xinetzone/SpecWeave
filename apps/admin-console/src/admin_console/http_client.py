"""标准库 HTTP 客户端：统一超时、指数退避重试、可注入（便于离线测试）。

设计要点（对应 spec FR-3/NFR-5）：所有外呼都带超时，失败重试一次后降级，
绝不把上游异常抛给终端用户。
"""

import json
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Optional

_urlopen: Callable = urllib.request.urlopen


def set_urlopen(func: Optional[Callable]) -> None:
    """注入/还原 urlopen 实现（测试用）。传 None 恢复标准库实现。"""
    global _urlopen
    _urlopen = func or urllib.request.urlopen


class HttpResponse:
    """轻量响应封装。`status == 0` 表示网络层失败（超时/DNS/连接拒绝）。"""

    __slots__ = ("status", "headers", "body")

    def __init__(self, status: int, headers: Dict[str, str], body: bytes) -> None:
        self.status = status
        self.headers = headers
        self.body = body

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def json(self) -> Any:
        if not self.body:
            return None
        try:
            return json.loads(self.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


def request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[bytes] = None,
    timeout: float = 8.0,
    retries: int = 1,
) -> HttpResponse:
    """发起 HTTP 请求；5xx 与网络异常才重试，4xx 直接返回。"""
    last = HttpResponse(0, {}, b"")
    for attempt in range(max(int(retries), 0) + 1):
        req = urllib.request.Request(url=url, data=body, method=method.upper())
        for key, value in (headers or {}).items():
            req.add_header(key, value)
        try:
            with _urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                head = {str(k).lower(): str(v) for k, v in resp.headers.items()}
                response = HttpResponse(int(resp.status), head, raw)
        except urllib.error.HTTPError as exc:
            raw = b""
            try:
                raw = exc.read()
            except Exception:  # noqa: BLE001 - 错误体不可读时忽略
                raw = b""
            head = {str(k).lower(): str(v) for k, v in (exc.headers or {}).items()}
            response = HttpResponse(int(exc.code), head, raw)
        except Exception:  # noqa: BLE001 - 超时/DNS/连接失败统一降级
            response = HttpResponse(0, {}, b"")

        last = response
        if response.status == 0 or response.status >= 500:
            if attempt < retries:
                time.sleep(0.2 * (2**attempt))
                continue
        return response
    return last
