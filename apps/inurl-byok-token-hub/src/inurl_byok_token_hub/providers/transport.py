"""传输层抽象：HTTP 调用统一入口（真实 httpx 实现 + mock 实现）。

硬约束：
- 外部调用必须经过本模块，禁止在适配器内直接使用 httpx；
- ``MockTransport`` 记录全部请求快照，供测试逐项断言
  （方法 / 路径 / 头 / 查询参数），从而零真实密钥完成验证；
- 日志与异常中的 Key / 令牌一律脱敏。
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from ..errors import UpstreamError
from ..logging_utils import get_logger, redact

logger = get_logger("providers.transport")


@dataclass(frozen=True)
class HttpRequest:
    method: str = "POST"
    url: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)
    json_body: dict | None = None


@dataclass(frozen=True)
class HttpResponse:
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    json_body: dict | None = None
    text: str = ""


class Transport:
    """传输层协议。"""

    def send(self, request: HttpRequest, *, timeout: float = 30.0) -> HttpResponse:
        raise NotImplementedError


class HttpxTransport(Transport):
    """真实 HTTP 传输（httpx）。"""

    def __init__(self, *, verify: bool = True, trust_env: bool = False) -> None:
        self.verify = verify
        self.trust_env = trust_env

    def send(self, request: HttpRequest, *, timeout: float = 30.0) -> HttpResponse:
        import httpx

        try:
            with httpx.Client(timeout=timeout, verify=self.verify, trust_env=self.trust_env) as client:
                resp = client.request(
                    request.method,
                    request.url,
                    headers=request.headers,
                    params=request.params,
                    json=request.json_body,
                )
        except Exception as exc:  # noqa: BLE001 - 统一归一化为 UpstreamError
            logger.warning("上游请求失败：%s", redact(str(exc)))
            raise UpstreamError(
                f"上游请求失败：{redact(str(exc))}", retryable=True
            ) from exc
        try:
            body = resp.json()
        except Exception:  # noqa: BLE001
            body = None
        return HttpResponse(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            json_body=body,
            text=resp.text,
        )


class MockTransport(Transport):
    """脚本化 mock 传输：按序返回预设响应，并记录全部请求快照。"""

    def __init__(
        self,
        responses: list[HttpResponse] | None = None,
        handler: Callable[[HttpRequest], HttpResponse] | None = None,
        *,
        latency_ms: float = 0.0,
    ) -> None:
        self.responses: list[HttpResponse] = list(responses or [])
        self.handler = handler
        self.latency_ms = latency_ms
        self.requests: list[HttpRequest] = []

    def send(self, request: HttpRequest, *, timeout: float = 30.0) -> HttpResponse:
        self.requests.append(request)
        if self.latency_ms:  # pragma: no cover - 仅在需要模拟延迟时使用
            time.sleep(self.latency_ms / 1000.0)
        if self.handler is not None:
            return self.handler(request)
        if not self.responses:
            raise UpstreamError("mock 传输层已无预设响应", retryable=False)
        if len(self.responses) == 1:
            return self.responses[0]
        return self.responses.pop(0)

    # 便捷断言辅助
    def last_request(self) -> HttpRequest:
        if not self.requests:
            raise AssertionError("尚未发出任何请求")
        return self.requests[-1]
