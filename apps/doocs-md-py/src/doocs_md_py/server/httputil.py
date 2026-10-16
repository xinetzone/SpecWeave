"""HTTP 通用工具：客户端 IP、JSON 错误体。"""

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


def client_ip(request: Request) -> str:
    """解析请求来源 IP。

    优先 ``X-Forwarded-For`` 链首项（反代/Cloudflare 场景），否则回退 TCP 对端。
    Cloudflare 也提供 ``CF-Connecting-IP``：自托管部署若处于可信 CF 代理之后，
    可按需改为读取该头；当前实现与上游 doocs/md 各 handler 使用的 IP 获取口径一致
    （均取转发链首项），故不单独消费 CF 头。
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        first = xff.split(",", 1)[0].strip()
        if first:
            return first
    if request.client is not None:
        return request.client.host
    return ""


def error_response(
    status_code: int,
    message: str,
    *,
    extra: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """统一 JSON 错误体（上游各 handler 普遍为 ``{"error": "<消息>"}``）。

    OAuth2 等需错误码+描述的场景传 extra，例如
    ``extra={"error_description": "..."}``；extra 可覆盖 error 键
    （``{"error": "invalid_request", ...}``）。
    """
    body: dict[str, Any] = {"error": message}
    if extra:
        body.update(extra)
    return JSONResponse(status_code=status_code, content=body, headers=headers)


class ApiError(Exception):
    """业务处理器抛出的 HTTP 错误；由 app 异常处理器转为统一 JSON 错误体。

    上游 Hono 直接 ``c.json({error}, status)``，FastAPI 用异常机制等价表达。
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        extra: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.extra = extra
        self.headers = headers
