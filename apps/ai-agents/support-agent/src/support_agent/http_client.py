"""极简 HTTP 客户端（仅标准库）：JSON 请求 + 超时 + 有限重试。"""

import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple


class HttpError(Exception):
    """HTTP 调用失败。"""

    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:400]}")
        self.status = status
        self.body = body


def request(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    payload: Any = None,
    timeout: float = 20.0,
    retries: int = 1,
) -> Tuple[int, str]:
    """发起 HTTP 请求，返回 (status, body_text)。5xx / 网络错误按指数退避重试。"""
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, method=method.upper())
        req.add_header("Content-Type", "application/json")
        for key, value in (headers or {}).items():
            if value:
                req.add_header(key, value)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            if exc.code < 500 or attempt == retries:
                raise HttpError(int(exc.code), body) from exc
            last_error = exc
        except Exception as exc:  # 网络层错误
            if attempt == retries:
                raise HttpError(0, str(exc)) from exc
            last_error = exc
        time.sleep(0.3 * (2 ** attempt))

    raise HttpError(0, str(last_error))


def request_json(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    payload: Any = None,
    timeout: float = 20.0,
    retries: int = 1,
) -> Any:
    """发起请求并解析 JSON 响应体。"""
    _, body = request(
        method, url, headers=headers, payload=payload, timeout=timeout, retries=retries
    )
    if not body.strip():
        return []
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise HttpError(0, f"响应不是合法 JSON: {body[:200]}") from exc
