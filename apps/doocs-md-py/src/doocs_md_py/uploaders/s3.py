"""五家 S3 兼容图床（upstream: providers.ts aliOSS/txCOS/minio/s3/r2 五函数）。

统一流程：按各家 endpoint/forcePathStyle 规则定位 host 与 key 路径 →
SigV4 query presigned URL（expiresIn=300，只签 host，UNSIGNED-PAYLOAD）→
PUT 原始字节（Content-Type 头）。URL 拼接三返回优先级逐字对齐：
cdnHost/domain → endpoint 形态 → 各家默认公开域名。
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

from .base import UploadFile, get_date_filename, trim_trailing_slash
from .s3_presign import amz_now, build_presigned_put_url

_PROTOCOL_PREFIXES = ("https://", "http://")


@dataclass(slots=True)
class AliOSSConfig:
    region: str
    bucket: str
    access_key_id: str
    access_key_secret: str
    use_ssl: bool = True
    cdn_host: str = ""
    path: str = ""


@dataclass(slots=True)
class TxCOSConfig:
    secret_id: str
    secret_key: str
    bucket: str
    region: str
    path: str = ""
    cdn_host: str = ""


@dataclass(slots=True)
class MinioConfig:
    endpoint: str
    port: str = ""
    use_ssl: bool = True
    bucket: str = ""
    access_key: str = ""
    secret_key: str = ""


@dataclass(slots=True)
class GenericS3Config:
    endpoint: str = ""
    region: str = ""
    bucket: str = ""
    access_key_id: str = ""
    access_key_secret: str = ""
    path: str = ""
    cdn_host: str = ""
    path_style: bool = False


@dataclass(slots=True)
class R2Config:
    account_id: str
    access_key: str
    secret_key: str
    bucket: str
    path: str = ""
    domain: str = ""


def _resolve_now(now: datetime | None) -> tuple[str, str]:
    return amz_now(now)


def _presigned_put(
    *,
    host: str,
    raw_path: str,
    region: str,
    access_key_id: str,
    secret_access_key: str,
    file: UploadFile,
    http_client: httpx.Client,
    now: datetime | None,
    scheme: str = "https",
) -> httpx.Response:
    amz_date, _ = _resolve_now(now)
    presigned = build_presigned_put_url(
        host=host,
        raw_path=raw_path,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=region,
        amz_date=amz_date,
        scheme=scheme,
    )
    return http_client.put(
        presigned["url"],
        content=file.content,
        headers={"Content-Type": file.content_type},
    )


def _key_with_path(path: str, date_filename: str) -> str:
    prefix = f"{path}/" if path else ""
    return prefix + date_filename


# --------------------------------------------------------------------------
# Aliyun OSS（providers.ts:158-218）
# --------------------------------------------------------------------------


def alioss_upload(
    config: AliOSSConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    now: datetime | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    date_filename = get_date_filename(file.name, clock_ms=clock_ms)
    key = _key_with_path(config.path, date_filename)
    protocol = "https" if config.use_ssl else "http"
    host = f"{config.bucket}.{config.region}.aliyuncs.com"

    response = _presigned_put(
        host=host,
        raw_path=f"/{key}",
        region=config.region,
        access_key_id=config.access_key_id,
        secret_access_key=config.access_key_secret,
        file=file,
        http_client=http_client,
        now=now,
        scheme=protocol,
    )
    if response.status_code // 100 != 2:
        raise RuntimeError(f"Upload failed: {response.reason_phrase}")

    if config.cdn_host:
        return f"{trim_trailing_slash(config.cdn_host)}/{key}"
    return f"{protocol}://{host}/{key}"


# --------------------------------------------------------------------------
# Tencent COS（providers.ts:224-285）
# --------------------------------------------------------------------------


def txcos_upload(
    config: TxCOSConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    now: datetime | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    date_filename = get_date_filename(file.name, clock_ms=clock_ms)
    key = _key_with_path(config.path, date_filename)
    host = f"{config.bucket}.cos.{config.region}.myqcloud.com"

    response = _presigned_put(
        host=host,
        raw_path=f"/{key}",
        region=config.region,
        access_key_id=config.secret_id,
        secret_access_key=config.secret_key,
        file=file,
        http_client=http_client,
        now=now,
    )
    if response.status_code // 100 != 2:
        raise RuntimeError(f"Upload failed: {response.reason_phrase}")

    if config.cdn_host:
        # 逐字：不拼 key，按 path 是否为空重新组
        if config.path == "":
            return f"{config.cdn_host}/{date_filename}"
        return f"{config.cdn_host}/{config.path}/{date_filename}"
    return f"https://{host}/{key}"


# --------------------------------------------------------------------------
# MinIO（providers.ts:291-323，pathStyle、region=auto、无 path 前缀）
# --------------------------------------------------------------------------


def minio_upload(
    config: MinioConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    now: datetime | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    date_filename = get_date_filename(file.name, clock_ms=clock_ms)
    protocol = "https" if config.use_ssl else "http"
    port_suffix = f":{config.port}" if config.port else ""
    base = f"{protocol}://{config.endpoint}{port_suffix}"

    response = _presigned_put(
        host=f"{config.endpoint}{port_suffix}",
        raw_path=f"/{config.bucket}/{date_filename}",
        region="auto",
        access_key_id=config.access_key,
        secret_access_key=config.secret_key,
        file=file,
        http_client=http_client,
        now=now,
        scheme=protocol,
    )
    if response.status_code // 100 != 2:
        raise RuntimeError(
            f"MinIO upload failed: {response.status_code} {response.reason_phrase}"
        )
    return f"{base}/{config.bucket}/{date_filename}"


# --------------------------------------------------------------------------
# 通用 S3（providers.ts:329-402）
# --------------------------------------------------------------------------


def s3_upload(
    config: GenericS3Config,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    now: datetime | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    date_filename = get_date_filename(file.name, clock_ms=clock_ms)
    key = _key_with_path(config.path, date_filename)

    resolved_endpoint = None
    if config.endpoint:
        resolved_endpoint = (
            config.endpoint
            if config.endpoint.startswith(_PROTOCOL_PREFIXES)
            else f"https://{config.endpoint}"
        )

    if resolved_endpoint:
        scheme = "https" if resolved_endpoint.startswith("https") else "http"
        endpoint_host = resolved_endpoint.split("://", 1)[1]
        if config.path_style:
            host = endpoint_host
            raw_path = f"/{config.bucket}/{key}"
        else:
            host = f"{config.bucket}.{endpoint_host}"
            raw_path = f"/{key}"
    else:
        scheme = "https"
        host = f"{config.bucket}.s3.{config.region}.amazonaws.com"
        raw_path = f"/{key}"

    response = _presigned_put(
        host=host,
        raw_path=raw_path,
        region=config.region,
        access_key_id=config.access_key_id,
        secret_access_key=config.access_key_secret,
        file=file,
        http_client=http_client,
        now=now,
        scheme=scheme,
    )
    if response.status_code // 100 != 2:
        raise RuntimeError(f"Upload failed: {response.reason_phrase}")

    if config.cdn_host:
        return f"{trim_trailing_slash(config.cdn_host)}/{key}"

    if resolved_endpoint:
        proto = "https" if resolved_endpoint.startswith("https") else "http"
        bare = resolved_endpoint.split("://", 1)[1]
        if config.path_style:
            return f"{proto}://{bare}/{config.bucket}/{key}"
        return f"{proto}://{config.bucket}.{bare}/{key}"

    return f"https://{config.bucket}.s3.{config.region}.amazonaws.com/{key}"


# --------------------------------------------------------------------------
# Cloudflare R2（providers.ts:505-528，region=auto、virtual-host）
# --------------------------------------------------------------------------


def r2_upload(
    config: R2Config,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    now: datetime | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    prefix = f"{config.path}/" if config.path else ""
    filename = prefix + get_date_filename(file.name, clock_ms=clock_ms)
    host = f"{config.bucket}.{config.account_id}.r2.cloudflarestorage.com"

    response = _presigned_put(
        host=host,
        raw_path=f"/{filename}",
        region="auto",
        access_key_id=config.access_key,
        secret_access_key=config.secret_key,
        file=file,
        http_client=http_client,
        now=now,
    )
    if response.status_code // 100 != 2:
        raise RuntimeError(
            f"R2 upload failed: {response.status_code} {response.reason_phrase}"
        )
    return f"{config.domain}/{filename}"


def utc_now_fixed(amz_date: str) -> datetime:
    """测试辅助：由 ``YYYYMMDDTHHMMSSZ`` 构造 UTC datetime。"""
    return datetime.strptime(amz_date, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
