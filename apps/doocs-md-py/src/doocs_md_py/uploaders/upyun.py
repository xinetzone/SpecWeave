"""又拍云图床（upstream: providers.ts:530-563）。

签名：``UPYUN <operator>:<base64(HMAC-SHA1("PUT&<uri>&<httpDate>", md5hex(password)))>``。
关键 CryptoJS 语义：HMAC 的 key 是 MD5 输出的 **32 位小写 hex 字符串**按 UTF-8
取字节（不是 16 字节原始摘要）。date 为 RFC 7231 GMT 文本（JS toUTCString）。
"""

import base64
import hashlib
import hmac
from collections.abc import Callable
from dataclasses import dataclass
from email.utils import formatdate
from time import time

import httpx

from .base import UploadFile, get_date_filename

UPYUN_ENDPOINT = "https://v0.api.upyun.com"


def upyun_http_date(now_sec: float | None = None) -> str:
    """等价 ``new Date().toUTCString()``：``Tue, 15 Oct 2026 10:00:00 GMT``。"""
    stamp = now_sec if now_sec is not None else time()
    return formatdate(stamp, usegmt=True)


def upyun_signature(password: str, method: str, uri: str, date: str) -> str:
    password_md5 = hashlib.md5(password.encode("utf-8")).hexdigest()
    sign_str = "&".join((method, uri, date))
    digest = hmac.new(
        password_md5.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha1
    ).digest()
    return base64.b64encode(digest).decode("ascii")


@dataclass(slots=True)
class UpyunConfig:
    bucket: str
    operator: str
    password: str
    path: str
    domain: str


def upyun_upload(
    config: UpyunConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    now_sec: float | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    # 逐字：path 为空时 filename 以 "/" 开头（`${path}/${...}` 无三元）
    filename = f"{config.path}/{get_date_filename(file.name, clock_ms=clock_ms)}"
    uri = f"/{config.bucket}/{filename}"
    date = upyun_http_date(now_sec)
    signature = upyun_signature(config.password, "PUT", uri, date)

    response = http_client.put(
        f"{UPYUN_ENDPOINT}{uri}",
        content=file.content,
        headers={
            "Authorization": f"UPYUN {config.operator}:{signature}",
            "X-Date": date,
            "Content-Type": file.content_type,
        },
    )
    if response.status_code // 100 != 2:
        raise RuntimeError(
            f"upload.provider.uploadFailedWithDetail: {response.text}"
        )
    return f"{config.domain}/{filename}"
