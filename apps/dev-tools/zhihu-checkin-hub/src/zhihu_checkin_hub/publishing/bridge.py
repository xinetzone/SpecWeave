"""kimi-webbridge daemon 的 JSON HTTP 客户端。

协议（见 kimi-webbridge Skill）：
POST ``<endpoint>``，请求体 ``{"action": ..., "args": {...}, "session": ...}``。

- 所有传输异常归一为 ``BridgeError``，调用方（publisher）据此走降级；
- transport 可注入，便于离线单测；
- 三态健康：daemon 可达 → 浏览器会话可用 → 知乎已登录。
"""

import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable

import httpx

from ..errors import BridgeError

DEFAULT_ENDPOINT = "http://127.0.0.1:10086/command"
DEFAULT_SESSION = "zhihu-checkin-hub"
ZHIHU_HOME = "https://www.zhihu.com/"

# 登录态探测：只读取页面信号，绝不读取/存储 cookie 值
_LOGIN_PROBE_JS = r"""
(() => {
  const avatar = !!document.querySelector(
    '.AppHeader-profileAvatar, .AppHeader-userInfo, .GlobalWrite-top, .Topstory-container'
  );
  const loginEntry = !!document.querySelector(
    '.SignContainer, .SignFlow, .SignFlowSimpleForm, button.Button.SignFlowSimpleForm'
  );
  const onLoginPage = /login|signin/i.test(location.pathname);
  return JSON.stringify({
    url: location.href,
    avatarSignal: avatar,
    loginEntrySignal: loginEntry,
    onLoginPage: onLoginPage
  });
})()
""".strip()


class HealthState(StrEnum):
    DAEMON_DOWN = "daemon_down"
    BROWSER_DISCONNECTED = "browser_disconnected"
    LOGGED_OUT = "logged_out"
    READY = "ready"


Transport = Callable[[str, dict[str, Any], float], dict[str, Any]]


def httpx_transport(endpoint: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    """生产 transport：httpx POST，UTF-8 JSON，无第三方编码坑。"""
    try:
        resp = httpx.post(endpoint, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise BridgeError(f"WebBridge 请求失败：{exc}") from exc
    if not isinstance(data, dict):
        raise BridgeError("WebBridge 返回了非对象响应，协议异常")
    return data


@dataclass(frozen=True)
class HealthReport:
    state: HealthState
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


class BridgeClient:
    def __init__(
        self,
        *,
        endpoint: str = DEFAULT_ENDPOINT,
        session: str = DEFAULT_SESSION,
        timeout: float = 30.0,
        transport: Transport | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.session = session
        self.timeout = timeout
        self._transport = transport or httpx_transport

    # ---------------- 基础调用 ----------------

    def raw_call(self, action: str, **args: Any) -> dict[str, Any]:
        """只做传输归一，不解释 success 字段（健康检查用）。"""
        payload = {"action": action, "args": args, "session": self.session}
        try:
            data = self._transport(self.endpoint, payload, self.timeout)
        except BridgeError:
            raise
        except Exception as exc:  # 任何 transport 故障都不得向外抛裸异常
            raise BridgeError(f"WebBridge 传输失败（{action}）：{exc}") from exc
        if not isinstance(data, dict):
            raise BridgeError(f"WebBridge 返回了非对象响应（{action}）")
        return data

    def call(self, action: str, **args: Any) -> dict[str, Any]:
        envelope = self.raw_call(action, **args)
        # 真实 daemon 信封：{"ok": true, "data": {...}} /
        # {"ok": false, "error": {"code": ..., "message": ...}}
        if envelope.get("ok") is False or isinstance(envelope.get("error"), dict):
            err = envelope.get("error") or {}
            message = err.get("message") if isinstance(err, dict) else str(err)
            raise BridgeError(f"WebBridge 返回错误（{action}）：{message or err}")
        data = envelope["data"] if isinstance(envelope.get("data"), dict) else envelope
        if isinstance(data.get("error"), str):
            raise BridgeError(f"WebBridge 返回错误（{action}）：{data['error']}")
        if data.get("success") is False:
            raise BridgeError(f"WebBridge 操作未成功（{action}）：{data}")
        return data

    def navigate(
        self, url: str, *, new_tab: bool = False, group_title: str | None = None
    ) -> dict[str, Any]:
        args: dict[str, Any] = {"url": url, "newTab": new_tab}
        if group_title:
            args["group_title"] = group_title
        return self.call("navigate", **args)

    def find_tab(self, url: str, *, active: bool = False) -> dict[str, Any]:
        return self.call("find_tab", url=url, active=active)

    def snapshot(self) -> dict[str, Any]:
        return self.call("snapshot")

    def click(self, selector: str) -> dict[str, Any]:
        return self.call("click", selector=selector)

    def fill(self, selector: str, value: str) -> dict[str, Any]:
        return self.call("fill", selector=selector, value=value)

    def evaluate(self, code: str) -> dict[str, Any]:
        return self.call("evaluate", code=code)

    def screenshot(
        self,
        *,
        fmt: str = "png",
        quality: int | None = None,
        selector: str | None = None,
        path: str | None = None,
    ) -> dict[str, Any]:
        args: dict[str, Any] = {"format": fmt}
        if quality is not None:
            args["quality"] = quality
        if selector:
            args["selector"] = selector
        if path:
            args["path"] = path
        return self.call("screenshot", **args)

    def list_tabs(self) -> dict[str, Any]:
        return self.call("list_tabs")

    def cdp(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """透传 chrome.debugger CDP（受信输入通道，如 Input.insertText）。"""
        return self.call("cdp", method=method, params=params or {})

    # ---------------- 三态健康 ----------------

    def health(self) -> HealthReport:
        try:
            envelope = self.raw_call("list_tabs")
        except BridgeError as exc:
            return HealthReport(
                HealthState.DAEMON_DOWN,
                "无法连接 WebBridge daemon。请确认浏览器扩展与本地守护进程已启动。",
                {"error": str(exc)},
            )
        if envelope.get("ok") is False or isinstance(envelope.get("error"), dict):
            err = envelope.get("error") or {}
            message = err.get("message") if isinstance(err, dict) else str(err)
            return HealthReport(
                HealthState.BROWSER_DISCONNECTED,
                "daemon 可达但浏览器会话未连接，请在浏览器中启用 WebBridge 扩展。",
                {"error": message or envelope},
            )
        tabs = envelope["data"] if isinstance(envelope.get("data"), dict) else envelope
        if not tabs.get("success") or "tabs" not in tabs:
            return HealthReport(
                HealthState.BROWSER_DISCONNECTED,
                "daemon 可达但浏览器会话未连接，请在浏览器中启用 WebBridge 扩展。",
                {"raw": tabs},
            )
        try:
            self.navigate(ZHIHU_HOME)
            probe = self.evaluate(_LOGIN_PROBE_JS)
        except BridgeError as exc:
            return HealthReport(
                HealthState.BROWSER_DISCONNECTED,
                "浏览器会话探测失败，请确认扩展已接管当前浏览器。",
                {"error": str(exc)},
            )
        try:
            signal = json.loads(probe.get("value", "{}"))
        except (ValueError, TypeError):
            signal = {}
        logged_in = bool(signal.get("avatarSignal")) and not bool(
            signal.get("loginEntrySignal") or signal.get("onLoginPage")
        )
        if not logged_in:
            return HealthReport(
                HealthState.LOGGED_OUT,
                "浏览器未检测到知乎登录态，请先在该浏览器手动登录知乎（应用不会接触账号密码）。",
                {"probe": signal},
            )
        return HealthReport(
            HealthState.READY,
            "通道就绪：daemon / 浏览器 / 知乎登录态三态正常。",
            {"probe": signal},
        )
