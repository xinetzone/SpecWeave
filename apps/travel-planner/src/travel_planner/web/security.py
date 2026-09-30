"""本地 Web 安全：CSRF token 比对 + Origin/Referer 同源校验。

- CSRF：首次 GET 签发 ``tp_csrf`` cookie（httponly、SameSite=Strict），
  表单携带同名隐藏域，服务端依赖比对（``secrets.compare_digest``）。
- Origin：POST 请求若携带 Origin/Referer，其 netloc 必须与 Host 一致。
- 绑定：本应用仅允许监听回环地址（CLI 层强制）。
"""

import secrets
from urllib.parse import urlsplit

from fastapi import Form, HTTPException, Request
from fastapi.responses import JSONResponse

CSRF_COOKIE = "tp_csrf"
CSRF_FIELD = "csrf_token"


def install_security(app) -> None:
    """在 FastAPI 应用上安装安全中间件（签发 token + Origin 守卫）。"""

    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        token = request.cookies.get(CSRF_COOKIE)
        issued = False
        if not token:
            token = secrets.token_urlsafe(32)
            issued = True
        request.state.csrf_token = token
        if request.method == "POST":
            origin = request.headers.get("origin") or request.headers.get("referer")
            if origin:
                netloc = urlsplit(origin).netloc
                host = request.headers.get("host", "")
                if netloc and host and netloc != host:
                    return JSONResponse({"detail": "拒绝跨源请求"}, status_code=403)
        response = await call_next(request)
        if issued:
            response.set_cookie(
                CSRF_COOKIE, token, httponly=True, samesite="strict", path="/"
            )
        return response


def csrf_protect(request: Request, csrf_token: str = Form("")) -> None:
    """POST 路由依赖：表单 token 必须与 cookie 一致。"""
    cookie = request.cookies.get(CSRF_COOKIE)
    if not cookie or not csrf_token or not secrets.compare_digest(cookie, csrf_token):
        raise HTTPException(status_code=403, detail="CSRF 校验失败：请从应用页面重新提交")
