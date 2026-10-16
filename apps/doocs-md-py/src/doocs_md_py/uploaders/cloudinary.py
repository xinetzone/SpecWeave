"""Cloudinary 图床（upstream: providers.ts:609-685）。

签名上传：参与签名的参数（folder/upload_preset/timestamp）按名字典序排列为
``a=b&c=d`` 后拼接 apiSecret，SHA1 hex；multipart POST
``/v1_1/<cloudName>/image/upload``。无 apiSecret 时走 unsigned preset。
返回 ``secure_url || url``；自定义 domain 只替换源站、保留路径与查询。
"""

import hashlib
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx

from .base import UploadFile

CLOUDINARY_ENDPOINT = "https://api.cloudinary.com"


def cloudinary_signature(params: dict[str, str], api_secret: str) -> str:
    """upstream: params.sort().join('&') + apiSecret → SHA1 hex。"""
    base = "&".join(f"{k}={params[k]}" for k in sorted(params))
    return hashlib.sha1((base + api_secret).encode("utf-8")).hexdigest()


@dataclass(slots=True)
class CloudinaryConfig:
    cloud_name: str
    api_key: str
    api_secret: str = ""
    upload_preset: str = ""
    folder: str = ""
    domain: str = ""


def cloudinary_upload(
    config: CloudinaryConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    now_sec: float | None = None,
) -> str:
    if not config.cloud_name or not config.api_key:
        raise RuntimeError("upload.provider.cloudinaryMissingConfig")

    timestamp = int(now_sec if now_sec is not None else time.time())
    data: dict[str, str] = {"api_key": config.api_key, "timestamp": str(timestamp)}

    if config.api_secret:
        signed_params: dict[str, str] = {}
        if config.folder:
            signed_params["folder"] = config.folder
        if config.upload_preset:
            signed_params["upload_preset"] = config.upload_preset
        signed_params["timestamp"] = str(timestamp)
        data["signature"] = cloudinary_signature(signed_params, config.api_secret)
    elif config.upload_preset:
        data["upload_preset"] = config.upload_preset
    else:
        raise RuntimeError("upload.provider.cloudinaryMissingPreset")

    if config.folder:
        data["folder"] = config.folder

    response = http_client.post(
        f"{CLOUDINARY_ENDPOINT}/v1_1/{config.cloud_name}/image/upload",
        data=data,
        files={"file": (file.name, file.content, file.content_type)},
    )
    body = response.json() if response.content else {}
    origin_url = (
        body.get("secure_url") or body.get("url")
        if isinstance(body, dict)
        else None
    )
    if not origin_url:
        raise RuntimeError("upload.provider.cloudinaryMissingUrl")

    if config.domain:
        parts = urlsplit(origin_url)
        return f"{config.domain}{parts.path}{'?' + parts.query if parts.query else ''}"
    return origin_url
