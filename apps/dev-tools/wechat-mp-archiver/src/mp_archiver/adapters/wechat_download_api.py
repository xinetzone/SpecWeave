"""wechat-download-api 采集服务适配器（API-first 主承载）。

端点不硬编码：构造时读取服务的 ``/openapi.json`` 并由
:class:`ApiSurface` 发现搜索/历史端点；请求参数名同样从端点声明中匹配，
匹配不到时回退微信平台公开契约的惯用名（``query``/``__biz``/``offset`` 等）。

响应默认按微信平台原生契约解析（见 :mod:`wechat_payload`）；
若实测发现服务做了规范化包装，应在 wechat_payload 中扩展解析分支，
而不是在本适配器中堆叠私有字段猜测。
"""

import httpx

from .api_surface import ApiSurface, Endpoint
from .base import AccountRef
from .wechat_payload import (
    CredentialExpiredError,
    ApiRetError,
    PayloadError,
    parse_accounts,
    parse_history_page,
    select_account,
)

_SEARCH_KEYWORD_PARAMS = (
    "query", "name", "keyword", "account_name", "nickname", "q", "word", "k",
)
_SEARCH_BEGIN_PARAMS = ("begin", "offset", "page")
_SEARCH_COUNT_PARAMS = ("count", "size", "limit", "page_size", "pagesize")
_BIZ_PARAMS = ("__biz", "biz")
_FAKEID_PARAMS = ("fakeid", "fake_id")
_OFFSET_PARAMS = ("offset", "begin", "cursor")
_COUNT_PARAMS = ("count", "size", "limit", "page_size", "pagesize")

# 微信原生 searchbiz 单页上限为 5；搜索最多翻 5 页（25 个候选）后放弃
_SEARCH_PAGE_SIZE = 5
_SEARCH_MAX_BEGIN = 25
# 微信原生 getmsg 每页固定 10 个群发批次
_HISTORY_PAGE_SIZE = 10


class EndpointDiscoveryError(RuntimeError):
    """OpenAPI 中找不到所需端点（需手工覆写端点路径配置）。"""


class AccountNotFoundError(RuntimeError):
    """按名称未搜索到目标公众号。"""


class BizUnavailableError(RuntimeError):
    """搜索结果拿不到 __biz，无法拉取历史列表（需按实测响应补全解析）。"""


def _pick(available: tuple[str, ...], candidates: tuple[str, ...], default: str) -> str:
    for candidate in candidates:
        if candidate in available:
            return candidate
    return default


class WechatDownloadApiAdapter:
    """采集服务适配器。"""

    def __init__(
        self,
        client,
        base_url: str,
        surface: ApiSurface,
    ) -> None:
        """``client`` 为 :class:`RateLimitedClient` 或兼容 request/get 的对象。"""
        self._client = client
        self._base = base_url.rstrip("/")
        self._surface = surface

    @property
    def surface(self) -> ApiSurface:
        return self._surface

    @classmethod
    def build(
        cls,
        client,
        *,
        base_url: str,
        search_override: str = "",
        history_override: str = "",
    ) -> "WechatDownloadApiAdapter":
        """拉取 OpenAPI 规范并发现端点，构建适配器。"""
        root = base_url.rstrip("/")
        response = client.get(f"{root}/openapi.json")
        if response.status_code in (401, 403):
            raise CredentialExpiredError(-1, f"OpenAPI 返回 {response.status_code}")
        if response.status_code != 200:
            raise EndpointDiscoveryError(
                f"无法获取 OpenAPI 文档：HTTP {response.status_code}"
            )
        try:
            spec = response.json()
        except ValueError as exc:
            raise EndpointDiscoveryError(f"OpenAPI 响应不是 JSON：{exc}") from exc
        surface = ApiSurface.discover(
            spec,
            search_override=search_override,
            history_override=history_override,
        )
        if surface.search is None or surface.history is None:
            raise EndpointDiscoveryError(
                "端点自动发现失败："
                f"search={surface.search}, history={surface.history}；"
                "请用 mp-archiver doctor 查看 OpenAPI 能力路径，并通过 "
                "MP_ARCHIVER_EXPORTER_SEARCH_PATH / EXPORTER_HISTORY_PATH 覆写"
            )
        return cls(client, base_url, surface)

    # ---- 账号搜索 ---------------------------------------------------

    def resolve_account(self, name: str) -> AccountRef:
        endpoint = self._surface.search
        assert endpoint is not None
        keyword_param = _pick(
            endpoint.query_params, _SEARCH_KEYWORD_PARAMS, "query"
        )
        begin_param = _pick(endpoint.query_params, _SEARCH_BEGIN_PARAMS, "begin")
        count_param = _pick(endpoint.query_params, _SEARCH_COUNT_PARAMS, "count")

        begin = 0
        while begin < _SEARCH_MAX_BEGIN:
            params = {
                keyword_param: name,
                begin_param: str(begin),
                count_param: str(_SEARCH_PAGE_SIZE),
            }
            payload = self._request_json(endpoint, params)
            accounts = parse_accounts(payload)
            matched = select_account(accounts, name)
            if matched is not None:
                return matched
            if len(accounts) < _SEARCH_PAGE_SIZE:
                break
            begin += _SEARCH_PAGE_SIZE

        raise AccountNotFoundError(
            f"搜索 {_SEARCH_MAX_BEGIN} 个候选内未找到公众号：{name!r}"
        )

    # ---- 历史列表 ---------------------------------------------------

    def fetch_history_page(self, account: AccountRef, offset: int):
        endpoint = self._surface.history
        assert endpoint is not None
        available = endpoint.query_params

        params: dict[str, str] = {}
        biz_name = next((p for p in _BIZ_PARAMS if p in available), "")
        fakeid_name = next((p for p in _FAKEID_PARAMS if p in available), "")
        if biz_name and account.biz:
            params[biz_name] = account.biz
        elif fakeid_name and account.fakeid:
            params[fakeid_name] = account.fakeid
        else:
            # 无参数声明信息时按微信原生契约发 __biz；有声明但都不匹配且无 biz 则报错
            if not available and account.biz:
                params["__biz"] = account.biz
            elif not account.biz:
                raise BizUnavailableError(
                    f"账号 {account.nickname!r} 缺少 __biz，且端点不接受 fakeid；"
                    "请核对采集服务搜索响应并补全 biz 解析"
                )

        params[_pick(available, _OFFSET_PARAMS, "offset")] = str(offset)
        if available:
            count_name = next((p for p in _COUNT_PARAMS if p in available), "")
            if count_name:
                params[count_name] = str(_HISTORY_PAGE_SIZE)
            if "f" in available:
                params["f"] = "json"
        else:
            params["count"] = str(_HISTORY_PAGE_SIZE)
            params["f"] = "json"

        payload = self._request_json(endpoint, params)
        return parse_history_page(
            payload,
            account_alias=account.nickname,
            account_biz=account.biz or None,
        )

    # ---- 内部 -------------------------------------------------------

    def _request_json(self, endpoint: Endpoint, params: dict[str, str]) -> dict:
        response = self._client.request(
            endpoint.method, f"{self._base}{endpoint.path}", params=params
        )
        if response.status_code in (401, 403):
            raise CredentialExpiredError(
                -1, f"{endpoint.path} 返回 {response.status_code}（需重新扫码）"
            )
        if response.status_code != 200:
            raise ApiRetError(
                response.status_code,
                f"{endpoint.path} 异常响应：{response.text[:200]}",
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise PayloadError(
                f"{endpoint.path} 响应不是 JSON：{response.text[:200]}"
            ) from exc
        if not isinstance(payload, dict):
            raise PayloadError(f"{endpoint.path} 响应不是 JSON 对象")
        return payload
