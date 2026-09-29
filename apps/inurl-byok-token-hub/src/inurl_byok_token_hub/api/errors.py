"""错误响应映射：把项目异常统一转成约定的 JSON 形态。"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..errors import BARE_UNAUTHORIZED, AuthError, ByokError, ErrorCode
from ..logging_utils import get_logger, redact

logger = get_logger("api.errors")

#: 使用裸 JSON 形态的错误码（鉴权类）
_BARE_CODES = frozenset(
    {
        ErrorCode.UNAUTHORIZED,
        ErrorCode.FORBIDDEN,
        ErrorCode.TURNSTILE_REQUIRED,
    }
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ByokError)
    async def _byok_handler(request: Request, exc: ByokError) -> JSONResponse:  # noqa: ARG001
        body = exc.bare_body() if exc.error_code in _BARE_CODES else exc.to_body()
        logger.info("业务错误 %s：%s", exc.error_code.code, redact(str(exc)))
        return JSONResponse(status_code=exc.http_status, content=body)

    @app.exception_handler(AuthError)
    async def _auth_handler(request: Request, exc: AuthError) -> JSONResponse:  # noqa: ARG001
        return JSONResponse(status_code=exc.http_status, content=exc.bare_body())

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # 未匹配路由（404）按源产品口径返回 401 裸 JSON（F-085）
        if exc.status_code == 404:
            return JSONResponse(status_code=401, content=dict(BARE_UNAUTHORIZED))
        return JSONResponse(
            status_code=exc.status_code, content={"error": {"message": str(exc.detail)}}
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
        logger.error("未处理异常：%s", redact(str(exc)))
        return JSONResponse(status_code=500, content=ByokError(ErrorCode.INTERNAL_ERROR).to_body())
