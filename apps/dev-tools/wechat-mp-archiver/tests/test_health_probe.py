"""采集服务探测逻辑测试（MockTransport，无真实网络）。"""

import httpx
import pytest

import mp_archiver.adapters.health as health_mod
from mp_archiver.adapters.health import probe_service

_REAL_CLIENT = httpx.Client


def _install_handler(monkeypatch, handler) -> None:
    """用 MockTransport 替换健康模块使用的 httpx.Client（测试后自动还原）。"""

    def factory(**kwargs):
        return _REAL_CLIENT(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(health_mod.httpx, "Client", factory)


def test_probe_up_via_openapi_with_capabilities(monkeypatch):
    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/api/login/init": {},
            "/api/accounts/search": {},
            "/api/health": {},
            "/unrelated": {},
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/openapi.json"
        assert request.headers["user-agent"].startswith("mp-archiver-doctor/")
        return httpx.Response(200, json=spec)

    _install_handler(monkeypatch, handler)

    probe = probe_service("http://127.0.0.1:5000/")
    assert probe.status == "up"
    assert "/api/login/init" in probe.capabilities
    assert "/api/accounts/search" in probe.capabilities
    assert "/unrelated" not in probe.capabilities
    assert probe.capabilities[0] == "/api/login/init"


def test_probe_sends_bearer_token(monkeypatch):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json={"paths": {}})

    _install_handler(monkeypatch, handler)
    probe_service("http://127.0.0.1:5000", token="secret")
    assert seen["auth"] == "Bearer secret"


def test_probe_up_via_html_root(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/":
            return httpx.Response(
                200, headers={"content-type": "text/html; charset=utf-8"}, text="<html/>"
            )
        return httpx.Response(404)

    _install_handler(monkeypatch, handler)
    probe = probe_service("http://127.0.0.1:8080")
    assert probe.status == "up"
    assert "text/html" in probe.detail


def test_probe_auth_required(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    _install_handler(monkeypatch, handler)
    probe = probe_service("http://127.0.0.1:5000")
    assert probe.status == "auth_required"
    assert "401" in probe.detail


def test_probe_down_on_connection_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    _install_handler(monkeypatch, handler)
    probe = probe_service("http://127.0.0.1:5999")
    assert probe.status == "down"
    assert "ConnectError" in probe.detail


def test_probe_down_when_all_endpoints_404(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    _install_handler(monkeypatch, handler)
    probe = probe_service("http://127.0.0.1:5000")
    assert probe.status == "down"
    assert probe.capabilities == ()


def test_probe_openapi_non_json_falls_through_to_health(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openapi.json":
            return httpx.Response(200, text="<html>not json</html>")
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        return httpx.Response(404)

    _install_handler(monkeypatch, handler)
    probe = probe_service("http://127.0.0.1:5000")
    assert probe.status == "up"
    assert "/health" in probe.detail
    assert probe.capabilities == ()
