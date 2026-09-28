"""TR-7：WebBridge 客户端协议封装与三态健康（注入假 transport，零真实网络）。

transport mock 按 daemon v1.11.6 真实信封建模：
成功 ``{"ok": true, "data": <工具结果>}``；
失败 ``{"ok": false, "error": {"code": ..., "message": ...}}``。
"""

import json
from typing import Any

import httpx
import pytest

from zhihu_checkin_hub.errors import BridgeError
from zhihu_checkin_hub.publishing.bridge import (
    DEFAULT_SESSION,
    HealthState,
    ZHIHU_HOME,
    BridgeClient,
)


def ok(payload: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "data": payload}


def fail(message: str, code: str = "tool_error") -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message}}


class FakeTransport:
    def __init__(self, routes: dict[str, Any] | None = None, raise_exc: Exception | None = None):
        self.routes = routes or {}
        self.raise_exc = raise_exc
        self.calls: list[dict[str, Any]] = []

    def __call__(self, endpoint: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        self.calls.append(payload)
        if self.raise_exc:
            raise self.raise_exc
        action = payload["action"]
        route = self.routes.get(action)
        if callable(route):
            return route(payload["args"])
        return route


def make_client(routes=None, raise_exc=None) -> tuple[BridgeClient, FakeTransport]:
    transport = FakeTransport(routes, raise_exc=raise_exc)
    client = BridgeClient(transport=transport)
    return client, transport


def test_request_envelope_session_and_args() -> None:
    client, transport = make_client({"navigate": ok({"success": True, "tabId": "t1"})})
    client.navigate("https://zhihu.com/write", new_tab=True, group_title="知乎发布")
    sent = transport.calls[0]
    assert sent["session"] == DEFAULT_SESSION
    assert sent["action"] == "navigate"
    assert sent["args"] == {
        "url": "https://zhihu.com/write",
        "newTab": True,
        "group_title": "知乎发布",
    }


def test_action_methods_unwrap_real_envelope() -> None:
    client, transport = make_client(
        {
            "fill": ok({"success": True, "mode": "contenteditable"}),
            "screenshot": ok({"format": "png", "path": "x.png", "sizeBytes": 1}),
            "list_tabs": ok({"success": True, "tabs": []}),
            "evaluate": ok({"type": "string", "value": "{}"}),
        }
    )
    assert client.fill("@e12", "正文")["mode"] == "contenteditable"
    assert client.screenshot(path="x.png")["path"] == "x.png"
    assert client.evaluate("1")["value"] == "{}"
    assert client.list_tabs()["tabs"] == []
    assert [c["action"] for c in transport.calls] == [
        "fill",
        "screenshot",
        "evaluate",
        "list_tabs",
    ]
    assert transport.calls[0]["args"] == {"selector": "@e12", "value": "正文"}
    assert transport.calls[1]["args"]["path"] == "x.png"


def test_transport_and_protocol_errors_normalized() -> None:
    client, _ = make_client(raise_exc=httpx.ConnectError("refused"))
    with pytest.raises(BridgeError):
        client.list_tabs()

    # 真实信封：ok=false + error{code,message}
    client2, _ = make_client({"click": fail("element not found")})
    with pytest.raises(BridgeError, match="element not found"):
        client2.click("@e1")

    # data 内 success:false（工具执行失败）同样归一
    client3, _ = make_client({"snapshot": ok({"success": False})})
    with pytest.raises(BridgeError):
        client3.snapshot()


def _logged_in_routes(signal: dict[str, Any]) -> dict[str, Any]:
    return {
        "list_tabs": ok({"success": True, "tabs": [{"tabId": "t1", "url": ZHIHU_HOME}]}),
        "navigate": ok({"success": True, "url": ZHIHU_HOME}),
        "evaluate": ok({"type": "string", "value": json.dumps(signal)}),
    }


def test_health_ready() -> None:
    client, _ = make_client(
        _logged_in_routes(
            {"url": ZHIHU_HOME, "avatarSignal": True, "loginEntrySignal": False, "onLoginPage": False}
        )
    )
    report = client.health()
    assert report.state == HealthState.READY


def test_health_daemon_down() -> None:
    client, _ = make_client(raise_exc=httpx.ConnectError("refused"))
    report = client.health()
    assert report.state == HealthState.DAEMON_DOWN
    assert "daemon" in report.message


def test_health_browser_disconnected() -> None:
    # 真实场景：daemon 可达但扩展未连接 → ok:false 信封
    client, _ = make_client({"list_tabs": fail("no extension connected")})
    report = client.health()
    assert report.state == HealthState.BROWSER_DISCONNECTED
    assert "扩展" in report.message


def test_health_logged_out() -> None:
    client, _ = make_client(
        _logged_in_routes(
            {"url": "https://www.zhihu.com/login", "avatarSignal": False, "loginEntrySignal": True, "onLoginPage": True}
        )
    )
    report = client.health()
    assert report.state == HealthState.LOGGED_OUT
    assert "登录" in report.message
