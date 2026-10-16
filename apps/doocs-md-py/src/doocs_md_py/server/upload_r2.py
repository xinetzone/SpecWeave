"""Cloudflare R2 上传（upstream: apps/api/src/upload-r2.ts 等价层）。

上游在 Workers 内使用原生 R2 binding（``env.UPLOAD_IMAGES.put``，平台隐式签名）；
Python 侧无 R2 运行时，等价实现为对 ``<account>.r2.cloudflarestorage.com`` 的
SigV4 PUT（region=auto），由 :class:`S3Backend` 承担。
"""

from collections.abc import Callable

import httpx

from .config import Config
from .storage import S3Backend
from .upload_filename import build_dated_object_key, dated_directory
from .upload_github import UploadPayload

DEFAULT_CONTENT_TYPE = "application/octet-stream"


def build_r2_backend(
    config: Config, http_client: httpx.Client | None = None
) -> S3Backend:
    return S3Backend(
        endpoint=config.upload_s3_endpoint,
        bucket=config.upload_s3_bucket,
        access_key_id=config.upload_s3_access_key_id,
        secret_access_key=config.upload_s3_secret_access_key,
        region=config.upload_s3_region or "auto",
        public_url=config.upload_s3_public_url,
        force_path_style=config.upload_s3_force_path_style,
        http_client=http_client,
    )


# upstream: upload-r2.ts:12-24
def upload_to_r2(
    config: Config,
    file: UploadPayload,
    http_client: httpx.Client,
    *,
    now_sec: float | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    if not config.upload_s3_bucket or not config.upload_s3_public_url.strip():
        raise RuntimeError("R2 upload is not configured")

    key = (
        f"{dated_directory(now_sec)}/"
        f"{build_dated_object_key(file.name, file.content_type, clock=clock_ms)}"
    )
    backend = build_r2_backend(config, http_client)
    return backend.put(key, file.content, file.content_type or DEFAULT_CONTENT_TYPE)
