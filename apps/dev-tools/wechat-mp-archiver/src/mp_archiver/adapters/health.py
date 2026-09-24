"""采集服务存活与授权状态探测（``mp-archiver doctor`` 使用）。

设计为对后端形态保持宽容：依次探测 OpenAPI 文档（FastAPI 类服务）、
常见健康检查端点与站点根路径（Nuxt/UI 类服务），从而在不固化任何
单一工具私有端点的前提下判定服务状态；若能拿到 OpenAPI 规范，
顺带抽取与登录/账号/文章相关的能力路径，供适配器对接时核对。
"""

from dataclasses import dataclass

import httpx

# 探测顺序：信息量大的端点优先
PROBE_PATHS = ("/openapi.json", "/health", "/api/health", "/")

_CAPABILITY_HINTS = (
    "login", "account", "search", "fakeid", "article",
    "history", "biz", "subscribe", "rss", "download",
)


@dataclass(frozen=True, slots=True)
class ServiceProbe:
    """服务探测结果。

    ``status`` 取值：
    - ``up``：服务存活（可能仍未登录，需进一步看采集时的 401）；
    - ``auth_required``：所有端点均要求授权（Token 缺失或登录态失效）；
    - ``down``：无法连接或所有探测端点均不可用。
    """

    status: str
    detail: str
    capabilities: tuple[str, ...] = ()


def _extract_capabilities(openapi_spec: dict) -> tuple[str, ...]:
    paths = openapi_spec.get("paths") or {}
    found = [
        path
        for path in paths
        if any(hint in str(path).lower() for hint in _CAPABILITY_HINTS)
    ]
    return tuple(found[:20])


def probe_service(
    base_url: str,
    *,
    token: str = "",
    timeout: float = 5.0,
    proxy: str = "",
) -> ServiceProbe:
    """探测采集服务存活与授权状态。"""
    headers = {"User-Agent": "mp-archiver-doctor/0.1"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    kwargs: dict = {"timeout": timeout, "headers": headers}
    if proxy:
        kwargs["proxy"] = proxy

    root = base_url.rstrip("/")
    auth_signal: str | None = None
    last_error: Exception | None = None

    with httpx.Client(**kwargs) as client:
        for path in PROBE_PATHS:
            try:
                response = client.get(f"{root}{path}")
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                continue

            if response.status_code == 200:
                if path == "/openapi.json":
                    try:
                        spec = response.json()
                    except ValueError:
                        spec = None
                    if isinstance(spec, dict):
                        return ServiceProbe(
                            "up",
                            "OpenAPI 文档可访问（/openapi.json 200）",
                            _extract_capabilities(spec),
                        )
                    # 200 但非 OpenAPI 文档（如登录页 HTML）：继续尝试后续探针
                    continue
                content_type = response.headers.get("content-type", "").split(";")[0]
                return ServiceProbe("up", f"{path} 200（{content_type or '未知类型'}）")

            if response.status_code in (401, 403):
                auth_signal = f"{path} 返回 {response.status_code}"

    if auth_signal:
        return ServiceProbe("auth_required", f"服务在线但需要授权：{auth_signal}")

    if last_error is not None:
        return ServiceProbe(
            "down",
            f"无法连接 {root}：{last_error.__class__.__name__}: {last_error}",
        )
    return ServiceProbe("down", f"{root} 所有探测端点均不可用")
