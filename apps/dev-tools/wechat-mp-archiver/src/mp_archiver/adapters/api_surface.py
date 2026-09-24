"""从采集服务的 OpenAPI 规范中发现「账号搜索」与「历史列表」端点。

不同采集服务/版本的端点路径不固定，且无法离线核实，因此不硬编码：
``doctor`` 已能取得 ``/openapi.json``，适配器启动时按路径关键词评分发现端点，
并支持通过配置（``MP_ARCHIVER_EXPORTER_SEARCH_PATH`` 等）显式覆写。
端到端实测若发现规则不匹配，优先覆写配置，再把实测路径补充进规则。
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Endpoint:
    path: str
    method: str  # GET / POST
    query_params: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ApiSurface:
    search: Endpoint | None
    history: Endpoint | None

    @classmethod
    def discover(
        cls,
        spec: dict,
        *,
        search_override: str = "",
        history_override: str = "",
    ) -> "ApiSurface":
        endpoints = _collect_endpoints(spec)
        return cls(
            search=_resolve_override(search_override, endpoints)
            or _best_match(endpoints, _SEARCH_RULES),
            history=_resolve_override(history_override, endpoints)
            or _best_match(endpoints, _HISTORY_RULES),
        )


def _collect_endpoints(spec: dict) -> tuple[Endpoint, ...]:
    paths = spec.get("paths") or {}
    found: list[Endpoint] = []
    for path, operations in paths.items():
        if not isinstance(operations, dict):
            continue
        for method, operation in operations.items():
            method_upper = method.upper()
            if method_upper not in {"GET", "POST"}:
                continue
            params = tuple(
                str(p.get("name"))
                for p in (operation.get("parameters") or [])
                if isinstance(p, dict) and p.get("in") == "query" and p.get("name")
            )
            found.append(Endpoint(path=str(path), method=method_upper, query_params=params))
    return tuple(found)


def _resolve_override(override: str, endpoints: tuple[Endpoint, ...]) -> Endpoint | None:
    if not override:
        return None
    # 显式覆写：规范中存在则沿用其 method/参数，否则按 GET 信任用户指定
    for endpoint in endpoints:
        if endpoint.path == override:
            return endpoint
    return Endpoint(path=override, method="GET", query_params=())


@dataclass(frozen=True, slots=True)
class _Rule:
    keywords: tuple[str, ...]
    score: int


# 命中任一 all-of 组即得对应分值；路径统一按小写匹配
_SEARCH_RULES = (
    _Rule(("searchbiz",), 10),
    _Rule(("search", "account"), 8),
    _Rule(("search", "biz"), 8),
    _Rule(("search", "mp"), 7),
    _Rule(("search", "official"), 7),
    _Rule(("accounts", "search"), 8),
    _Rule(("search",), 4),
)

_HISTORY_RULES = (
    _Rule(("getmsg",), 10),
    _Rule(("history",), 8),
    _Rule(("article", "list"), 7),
    _Rule(("appmsg",), 7),
    _Rule(("article", "page"), 6),
    _Rule(("article", "timeline"), 6),
    _Rule(("articles",), 4),
)

_EXCLUDE = ("login", "logout", "health", "docs", "swagger", "openapi", "download", "export")


def _score(path: str, rules: tuple[_Rule, ...]) -> int:
    low = path.lower()
    if any(token in low for token in _EXCLUDE):
        return 0
    total = 0
    for rule in rules:
        if all(keyword in low for keyword in rule.keywords):
            total = max(total, rule.score)
    return total


def _best_match(
    endpoints: tuple[Endpoint, ...], rules: tuple[_Rule, ...]
) -> Endpoint | None:
    candidates = [
        (_score(endpoint.path, rules), 0 if endpoint.method == "GET" else 1, endpoint)
        for endpoint in endpoints
    ]
    candidates = [item for item in candidates if item[0] > 0]
    if not candidates:
        return None
    # 分高优先；同分 GET 优先；再同分短路径优先
    candidates.sort(key=lambda item: (-item[0], item[1], len(item[2].path)))
    return candidates[0][2]
