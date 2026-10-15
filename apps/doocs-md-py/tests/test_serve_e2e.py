"""TR-19.2 / AC-14：``mdpy serve`` 同源静态托管与 API 端到端。

覆盖：首页 index.html（no-cache）、Vite 内容哈希资产长缓存、普通静态资源短缓存、
未命中无扩展名路径回退 index.html、带扩展名缺失 404、路径穿越拦截、API 路由不被
兜底静态路由遮蔽，以及同源全链路 token→push→pull→share→GET /s/<id>。

dist 不入库（.gitignore 忽略），故全部用 ``tmp_path`` 合成并由
``create_app(web_dist=...)`` 注入。
"""

import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.security import issue_token

JWT_SECRET = "serve-secret-0123456789-abcdef-ghijkl"

INDEX_HTML = '<!DOCTYPE html><html><body><div id="app"></div></body></html>\n'
HASHED_ASSET_BODY = "console.log(1)\n"
SNAPSHOT = {
    "bodyHtml": "<p>你好</p>",
    "stylesHtml": "<style>a{color:red}</style>",
}

HASHED_CACHE = "public, max-age=31536000, immutable"
STATIC_CACHE = "public, max-age=3600"
NO_CACHE = "no-cache"


@pytest.fixture
def dist(tmp_path):
    """合成一份最小 dist（首页 + 哈希 JS + favicon）。"""
    root = tmp_path / "web-dist"
    (root / "static" / "js").mkdir(parents=True)
    # newline="\n" 关闭 Windows 平台的 CRLF 转换，保证断言跨平台一致
    (root / "index.html").write_text(INDEX_HTML, encoding="utf-8", newline="\n")
    (root / "static" / "js" / "app-a1b2c3.js").write_text(
        HASHED_ASSET_BODY, encoding="utf-8", newline="\n"
    )
    (root / "favicon.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return root


@pytest.fixture
def ctx(conn, dist):
    db.upsert_user(
        conn,
        {"id": "u1", "github_id": 1, "login": "octocat", "name": None, "avatar": None},
    )
    app = create_app(Config(jwt_secret=JWT_SECRET), conn=conn, web_dist=dist)
    client = TestClient(app)
    token = issue_token(JWT_SECRET, "u1", "octocat", now_s=2_000_000_000)
    return {
        "client": client,
        "conn": conn,
        "h": {"Authorization": f"Bearer {token}"},
    }


def _doc(doc_id: str = "p1") -> dict:
    return {
        "id": doc_id,
        "title": "T",
        "content": "# hi",
        "parentId": None,
        "history": [],
        "createDatetime": 1,
        "updateDatetime": 100,
        "deleted": False,
    }


# ---- 静态托管语义 ----


def test_index_served_with_no_cache(ctx):
    resp = ctx["client"].get("/")
    assert resp.status_code == 200
    assert resp.text == INDEX_HTML
    assert resp.headers["content-type"].startswith("text/html")
    assert resp.headers["cache-control"] == NO_CACHE


def test_hashed_asset_long_cache(ctx):
    resp = ctx["client"].get("/static/js/app-a1b2c3.js")
    assert resp.status_code == 200
    assert resp.text == HASHED_ASSET_BODY
    assert resp.headers["cache-control"] == HASHED_CACHE


def test_plain_static_asset_short_cache(ctx):
    resp = ctx["client"].get("/favicon.png")
    assert resp.status_code == 200
    assert resp.content.startswith(b"\x89PNG")
    assert resp.headers["cache-control"] == STATIC_CACHE


def test_fallback_metric_and_index_same_cache(ctx):
    """非资产路径回退 index.html：内容与首页一致、同样禁缓存。"""
    index = ctx["client"].get("/")
    resp = ctx["client"].get("/docs/getting-started")
    assert resp.status_code == 200
    assert resp.text == index.text == INDEX_HTML
    assert resp.headers["cache-control"] == NO_CACHE


def test_missing_asset_with_extension_returns_404(ctx):
    resp = ctx["client"].get("/static/js/missing.js")
    assert resp.status_code == 404
    assert resp.text != INDEX_HTML


def test_path_traversal_is_rejected(ctx, dist):
    secret = dist.parent / "secret.txt"
    secret.write_text("TOP SECRET", encoding="utf-8")
    resp = ctx["client"].get("/%2e%2e/secret.txt")
    assert resp.status_code == 404
    assert "TOP SECRET" not in resp.text


# ---- 路由顺序：API 不被兜底静态路由遮蔽 ----


def test_api_routes_not_shadowed_by_fallback(ctx):
    unchanged = ctx["client"].get("/sync/pull")
    assert unchanged.status_code == 401
    assert unchanged.headers["content-type"].startswith("application/json")

    authorized = ctx["client"].get("/sync/pull", headers=ctx["h"])
    assert authorized.status_code == 200
    assert authorized.json()["cursor"] == 0


def test_health_route_yields_to_index(ctx):
    """自托管模式下 ``/`` 由 dist 首页接管，不再返回上游健康 JSON。"""
    resp = ctx["client"].get("/")
    assert resp.headers["content-type"].startswith("text/html")
    assert resp.text == INDEX_HTML


# ---- 同源全链路 ----


def test_same_origin_full_chain(ctx):
    """token → POST /sync/push → GET /sync/pull → POST /share → GET /s/<id>。"""
    client = ctx["client"]
    headers = ctx["h"]

    pushed = client.post(
        "/sync/push", headers=headers, json={"documents": [_doc()], "settings": []}
    )
    assert pushed.status_code == 200

    pulled = client.get("/sync/pull", headers=headers)
    assert pulled.status_code == 200
    assert [d["id"] for d in pulled.json()["documents"]] == ["p1"]

    created = client.post(
        "/share", headers=headers, json={"postId": "p1", "htmlSnapshot": SNAPSHOT}
    )
    assert created.status_code == 200
    share_id = created.json()["id"]
    assert created.json()["url"] == f"http://testserver/s/{share_id}"

    page = client.get(f"/s/{share_id}")
    assert page.status_code == 200
    assert page.headers["content-type"].startswith("text/html")
    assert "你好" in page.text
