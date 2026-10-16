"""FastAPI 共享依赖：数据库连接与 httpx 客户端。"""

import sqlite3

import httpx
from fastapi import Request

from . import db

# 服务端对外部 API（GitHub OAuth 等）的默认超时；上游 Workers fetch 无显式超时，
# Python 侧必须给默认值（httpx 自身默认仅 5s），此处取 15s 宽松值。
DEFAULT_HTTP_TIMEOUT = 15.0

_default_http_client: httpx.Client | None = None


def get_db(request: Request) -> sqlite3.Connection:
    """返回 app.state.db；未注入时按配置路径懒连接并应用迁移（测试注入内存库）。"""
    connection = getattr(request.app.state, "db", None)
    if connection is None:
        connection = db.connect(request.app.state.config.sqlite_path)
        db.apply_migrations(connection)
        request.app.state.db = connection
    return connection


def get_http_client(request: Request) -> httpx.Client:
    """app.state.http_client 优先（测试注入 MockTransport），否则模块级单例。"""
    injected = getattr(request.app.state, "http_client", None)
    if injected is not None:
        return injected
    global _default_http_client
    if _default_http_client is None:
        _default_http_client = httpx.Client(timeout=DEFAULT_HTTP_TIMEOUT)
    return _default_http_client
