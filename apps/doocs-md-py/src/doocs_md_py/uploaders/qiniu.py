"""七牛云图床（upstream: providers.ts:107-152，qiniu-js 3.4.4 网络层等价复刻）。

token = ``<AK>:<safe64(base64(HMAC-SHA1(encodedPolicy, SK)))>:<encodedPolicy>``，
policy 与 digest 均 URL-safe Base64（``+``→``-``、``/``→``_``，**保留 padding**，
逐字 tokenTools.safe64，不去除 ``=``）。上传为 multipart POST：
``file``/``key``/``token`` 三字段。
"""

import base64
import hashlib
import hmac
import json
import time
from collections.abc import Callable
from dataclasses import dataclass

import httpx

from .base import UploadFile, get_date_filename

QINIU_DEFAULT_UPLOAD_URL = "https://upload.qiniup.com"
_QINIU_TTL_SEC = 3600  # upstream: deadline = trunc(now/1000) + 3600


def _b64_urlsafe(data: bytes) -> str:
    # btoa(latin1) → 标准 base64，再 safe64 替换；padding 保留（逐字）
    return base64.b64encode(data).decode("ascii").replace("+", "-").replace("/", "_")


def qiniu_upload_token(
    access_key: str,
    secret_key: str,
    put_policy: dict,
) -> str:
    """upstream: getQiniuToken（providers.ts:111-121）。

    JSON.stringify 无空白、非 ASCII 不转义（TextEncoder UTF-8）；HMAC key 为
    SK 的 UTF-8 字节（CryptoJS 字符串键语义）。
    """
    policy = json.dumps(put_policy, separators=(",", ":"), ensure_ascii=False)
    encoded = _b64_urlsafe(policy.encode("utf-8"))
    digest = hmac.new(
        secret_key.encode("utf-8"), encoded.encode("ascii"), hashlib.sha1
    ).digest()
    encoded_signed = _b64_urlsafe(digest)
    return f"{access_key}:{encoded_signed}:{encoded}"


@dataclass(slots=True)
class QiniuConfig:
    access_key: str
    secret_key: str
    bucket: str
    path: str = ""
    domain: str = ""
    region: str = ""  # qiniu-js config.region；空→默认上传域名


def resolve_qiniu_upload_url(region: str) -> str:
    """空 region → 默认域名；http(s) 自定义 region 原样使用。"""
    trimmed = region.strip()
    if not trimmed:
        return QINIU_DEFAULT_UPLOAD_URL
    if trimmed.startswith("http://") or trimmed.startswith("https://"):
        return trimmed
    return QINIU_DEFAULT_UPLOAD_URL


def qiniu_upload(
    config: QiniuConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    now_sec: float | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    current_sec = int(now_sec if now_sec is not None else time.time())
    token = qiniu_upload_token(
        config.access_key,
        config.secret_key,
        {"scope": config.bucket, "deadline": current_sec + _QINIU_TTL_SEC},
    )
    prefix = f"{config.path}/" if config.path else ""
    key = prefix + get_date_filename(file.name, clock_ms=clock_ms)

    response = http_client.post(
        resolve_qiniu_upload_url(config.region),
        data={"token": token, "key": key},
        files={"file": (file.name, file.content, file.content_type)},
    )
    if response.status_code // 100 != 2:
        raise RuntimeError(f"Qiniu upload failed: {response.text}")
    return f"{config.domain}/{key}"
