"""微信公众号素材上传（upstream: providers.ts:404-499）。

stable_token 获取并缓存（``expires_in`` 秒，本地存 expire=now_ms+ttl*1000，
键 ``mpToken:<appID>``）；素材分流：``<1MiB`` 且 jpeg/png 走 ``media/uploadimg``
（返回可外链 url），否则走 ``material/add_material?type=image``（永久素材）。
代理（proxyOrigin）替换 ``https://api.weixin.qq.com`` 前缀；代理上传且页面
是 http(s) 来源时，图片经 ``wsrv.nl`` 反代（逐字 window.location.href 判断）。
微信可能以 ``text/plain`` 返回 JSON，httpx 按内容解析。
"""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import httpx

from .base import UploadFile

WECHAT_API_BASE = "https://api.weixin.qq.com"
_MB = 1024 * 1024


class MpTokenStore:
    """等价浏览器 localStorage 中 ``mpToken:<appID>`` 条目。"""

    def get(self, app_id: str) -> str | None:  # pragma: no cover - 接口
        raise NotImplementedError

    def set(self, app_id: str, raw_json: str) -> None:  # pragma: no cover - 接口
        raise NotImplementedError


@dataclass(slots=True)
class InMemoryMpTokenStore(MpTokenStore):
    _data: dict[str, str] = field(default_factory=dict)

    def get(self, app_id: str) -> str | None:
        return self._data.get(app_id)

    def set(self, app_id: str, raw_json: str) -> None:
        self._data[app_id] = raw_json


@dataclass(slots=True)
class MpConfig:
    app_id: str
    app_secret: str
    proxy_origin: str = ""


def get_mp_token(
    config: MpConfig,
    http_client: httpx.Client,
    store: MpTokenStore,
    *,
    now_ms: Callable[[], int] | None = None,
) -> str:
    """upstream: getMpToken（providers.ts:413-453）。"""
    clock = now_ms or (lambda: int(time.time() * 1000))
    cached = store.get(config.app_id)
    if cached:
        try:
            token_info = json.loads(cached)
            if token_info.get("expire") and token_info["expire"] > clock():
                return token_info["access_token"]
        except (ValueError, TypeError):
            pass

    url = f"{WECHAT_API_BASE}/cgi-bin/stable_token"
    if config.proxy_origin:
        url = f"{config.proxy_origin}/cgi-bin/stable_token"
    response = http_client.post(
        url,
        json={
            "grant_type": "client_credential",
            "appid": config.app_id,
            "secret": config.app_secret,
        },
    )
    res = response.json()
    if res.get("access_token"):
        token_info = dict(res)
        token_info["expire"] = clock() + int(res["expires_in"]) * 1000
        store.set(config.app_id, json.dumps(token_info, ensure_ascii=False))
        return res["access_token"]
    if res.get("errcode"):
        raise RuntimeError(
            f"upload.provider.accessTokenFailed: [{res['errcode']}] {res.get('errmsg')}"
        )
    return ""


def mp_upload(
    config: MpConfig,
    file: UploadFile,
    http_client: httpx.Client,
    store: MpTokenStore | None = None,
    *,
    page_href: str = "",
    now_ms: Callable[[], int] | None = None,
) -> str:
    """upstream: mpFileUpload（providers.ts:456-499）。

    ``page_href`` 等价注入 ``window.location.href``（wsrv 判定用）。
    """
    token_store = store or InMemoryMpTokenStore()
    access_token = get_mp_token(config, http_client, token_store, now_ms=now_ms)
    if not access_token:
        raise RuntimeError("upload.provider.accessTokenFailed")

    url = (
        f"{WECHAT_API_BASE}/cgi-bin/material/add_material"
        f"?access_token={access_token}&type=image"
    )
    size_in_mb = len(file.content) / _MB
    if size_in_mb < 1 and file.content_type.lower() in ("image/jpeg", "image/png"):
        url = f"{WECHAT_API_BASE}/cgi-bin/media/uploadimg?access_token={access_token}"
    if config.proxy_origin:
        url = url.replace(WECHAT_API_BASE, config.proxy_origin, 1)

    response = http_client.post(
        url,
        files={"media": (file.name, file.content, file.content_type)},
    )
    res = response.json()
    if not res.get("url"):
        if res.get("errcode"):
            raise RuntimeError(
                f"upload.provider.uploadNoUrl: [{res['errcode']}] {res.get('errmsg')}"
            )
        raise RuntimeError("upload.provider.uploadNoUrl")

    image_url = res["url"]
    if config.proxy_origin and page_href.startswith("http"):
        from urllib.parse import quote

        # encodeURIComponent 不转义集合：A-Za-z0-9 - _ . ~ ! * ' ( )
        image_url = f"https://wsrv.nl?url={quote(image_url, safe='-_.~!*\'()')}"
    return image_url
