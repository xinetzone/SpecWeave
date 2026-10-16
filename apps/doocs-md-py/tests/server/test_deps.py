"""server/deps.py 共享依赖测试（TR-4.2 / T10）。

覆盖两条依赖的真实契约：
- ``get_db``：``app.state.db`` 注入优先；未注入时按 ``Config.sqlite_path`` 懒连接并
  应用迁移，随后回填 ``app.state.db``（同一 app 内复用同一连接）；
- ``get_http_client``：注入的 client 优先于模块级单例；缺省单例按
  ``DEFAULT_HTTP_TIMEOUT`` 构造且跨调用复用。
"""

import sqlite3
from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

from doocs_md_py.server import deps
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config


def test_injected_connection_is_used_as_is(conn: sqlite3.Connection):
    # 注入已迁移的内存库 → get_db 直接返回注入对象，不再按配置路径重建连接
    app = create_app(Config(), conn=conn)
    response = TestClient(app).get("/marketplace/themes")
    assert response.status_code == 200
    assert app.state.db is conn


def test_lazy_connect_creates_db_file_and_applies_migrations(tmp_path):
    db_path = tmp_path / "lazy.db"
    app = create_app(Config(sqlite_path=str(db_path)))
    assert not db_path.exists()

    client = TestClient(app)
    first = client.get("/marketplace/themes")
    assert first.status_code == 200
    assert first.json()["items"] == []
    assert db_path.exists()

    connection = app.state.db
    try:
        # 懒连接结果回填 state：后续请求复用同一连接
        assert client.get("/marketplace/components").status_code == 200
        assert app.state.db is connection
        # 迁移已应用：审批表可查询（未应用迁移时会抛 no such table）
        count = connection.execute("SELECT COUNT(*) FROM marketplace_items").fetchone()[0]
        assert count == 0
    finally:
        connection.close()


def test_injected_http_client_wins_over_module_singleton():
    injected = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    previous = deps._default_http_client
    deps._default_http_client = None
    try:
        app = create_app(Config(), http_client=injected)
        request = SimpleNamespace(app=app)
        assert deps.get_http_client(request) is injected
        assert deps._default_http_client is None
    finally:
        injected.close()
        deps._default_http_client = previous


def test_default_http_client_is_timeout_configured_singleton():
    previous = deps._default_http_client
    deps._default_http_client = None
    try:
        request = SimpleNamespace(app=create_app(Config()))
        client = deps.get_http_client(request)
        assert client is deps.get_http_client(request)
        assert client.timeout.connect == deps.DEFAULT_HTTP_TIMEOUT
    finally:
        if deps._default_http_client is not None:
            deps._default_http_client.close()
        deps._default_http_client = previous
