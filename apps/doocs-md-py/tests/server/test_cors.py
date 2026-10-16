"""CORS 中间件矩阵（TR-4.1，对齐 index.ts:19-28 + origin.ts）。"""

from fastapi.testclient import TestClient

from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config


def _client(app_url: str) -> TestClient:
    return TestClient(create_app(Config(app_url=app_url)))


APP_URL = "https://md.doocs.org,https://*.doocs.org,http://localhost:*"


def test_exact_origin_get_echoes_credentials():
    client = _client(APP_URL)
    resp = client.get("/", headers={"Origin": "https://md.doocs.org"})
    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "https://md.doocs.org"
    assert resp.headers["access-control-allow-credentials"] == "true"
    assert resp.headers["vary"] == "Origin"


def test_wildcard_origin_allowed():
    client = _client(APP_URL)
    resp = client.get("/", headers={"Origin": "https://blog.doocs.org"})
    assert resp.headers["access-control-allow-origin"] == "https://blog.doocs.org"


def test_wildcard_does_not_cross_dots():
    client = _client(APP_URL)
    resp = client.get("/", headers={"Origin": "https://a.b.doocs.org"})
    assert "access-control-allow-origin" not in resp.headers


def test_suffix_attack_origin_rejected():
    client = _client(APP_URL)
    resp = client.get("/", headers={"Origin": "https://md.doocs.org.evil.com"})
    assert "access-control-allow-origin" not in resp.headers


def test_localhost_port_wildcard():
    client = _client(APP_URL)
    resp = client.get("/", headers={"Origin": "http://localhost:5173"})
    assert resp.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_browser_extension_origin_allowed():
    client = _client(APP_URL)
    resp = client.get("/", headers={"Origin": "chrome-extension://abcdef1234"})
    assert resp.headers["access-control-allow-origin"] == "chrome-extension://abcdef1234"


def test_preflight_allowed_returns_full_headers():
    client = _client(APP_URL)
    resp = client.options(
        "/",
        headers={
            "Origin": "https://md.doocs.org",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert resp.status_code == 204
    assert resp.headers["access-control-allow-origin"] == "https://md.doocs.org"
    assert resp.headers["access-control-allow-credentials"] == "true"
    methods = {m.strip() for m in resp.headers["access-control-allow-methods"].split(",")}
    assert methods == {"GET", "POST", "PATCH", "DELETE", "OPTIONS"}
    headers = {h.strip() for h in resp.headers["access-control-allow-headers"].split(",")}
    assert headers == {"Authorization", "Content-Type"}
    assert resp.headers["access-control-max-age"] == "86400"


def test_preflight_rejected_has_no_cors_headers():
    client = _client(APP_URL)
    resp = client.options(
        "/",
        headers={
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in resp.headers


def test_request_without_origin_has_no_cors_headers():
    client = _client(APP_URL)
    resp = client.get("/")
    assert "access-control-allow-origin" not in resp.headers
    assert resp.json() == {"name": "md-api", "ok": True}
