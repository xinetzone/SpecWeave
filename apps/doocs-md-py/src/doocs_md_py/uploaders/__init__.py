"""13 家 Web 图床 + md-cli dcloud 通道的 Python 复刻包。

注册表与 ID 逐字对齐 apps/web/src/services/upload/provider-registry.ts
（default/github/aliOSS/txCOS/qiniu/minio/s3/mp/r2/upyun/telegram/cloudinary/
formCustom），额外注册 md-cli 通道 ``dcloud``。未知 provider 一律回退 default。
"""

from collections.abc import Callable
from dataclasses import dataclass

import httpx

from .base import UploadFile
from .cloudinary import CloudinaryConfig, cloudinary_upload
from .dcloud import DcloudConfig, dcloud_upload_file
from .default import DefaultConfig, default_upload
from .form_custom import FormCustomConfig, form_custom_upload
from .github import GithubWebConfig, github_web_upload
from .mp import MpConfig, InMemoryMpTokenStore, mp_upload
from .qiniu import QiniuConfig, qiniu_upload
from .s3 import (
    AliOSSConfig,
    GenericS3Config,
    MinioConfig,
    R2Config,
    TxCOSConfig,
    alioss_upload,
    minio_upload,
    r2_upload,
    s3_upload,
    txcos_upload,
)
from .telegram import TelegramConfig, telegram_upload
from .upyun import UpyunConfig, upyun_upload

__all__ = [
    "UploadFile",
    "UPLOAD_PROVIDERS",
    "UploadProvider",
    "resolve_upload_provider",
    "file_upload",
    "DefaultConfig",
    "GithubWebConfig",
    "AliOSSConfig",
    "TxCOSConfig",
    "QiniuConfig",
    "MinioConfig",
    "GenericS3Config",
    "MpConfig",
    "InMemoryMpTokenStore",
    "R2Config",
    "UpyunConfig",
    "TelegramConfig",
    "CloudinaryConfig",
    "FormCustomConfig",
    "DcloudConfig",
]


@dataclass(frozen=True, slots=True)
class UploadProvider:
    id: str
    config_key: str | None


# upstream: provider-registry.ts:8-22（顺序逐字；dcloud 为 md-cli 扩展列于末尾）
UPLOAD_PROVIDERS: tuple[UploadProvider, ...] = (
    UploadProvider("default", None),
    UploadProvider("github", "githubConfig"),
    UploadProvider("aliOSS", "aliOSSConfig"),
    UploadProvider("txCOS", "txCOSConfig"),
    UploadProvider("qiniu", "qiniuConfig"),
    UploadProvider("minio", "minioConfig"),
    UploadProvider("s3", "s3Config"),
    UploadProvider("mp", "mpConfig"),
    UploadProvider("r2", "r2Config"),
    UploadProvider("upyun", "upyunConfig"),
    UploadProvider("telegram", "telegramConfig"),
    UploadProvider("cloudinary", "cloudinaryConfig"),
    UploadProvider("formCustom", "formCustomConfig"),
    UploadProvider("dcloud", None),
)

_PROVIDER_IDS = frozenset(p.id for p in UPLOAD_PROVIDERS)


def resolve_upload_provider(value: object) -> UploadProvider:
    """upstream: provider-registry.ts:37-40；未知值回退 default。"""
    if isinstance(value, str) and value in _PROVIDER_IDS:
        return next(p for p in UPLOAD_PROVIDERS if p.id == value)
    return UPLOAD_PROVIDERS[0]


def file_upload(
    provider_id: str,
    file: UploadFile,
    config: object,
    http_client: httpx.Client,
    *,
    env: dict | None = None,
) -> str:
    """按 provider id 分发到具体上传器。

    ``env`` 携带可注入的测试/运行时参数（now/clock_ms/now_sec/location_href/
    page_href/store 等），各家按需取用。
    """
    provider = resolve_upload_provider(provider_id)
    env = env or {}
    # 各上传器只取自己声明的注入参数（None 值不传，落回函数默认）
    s3_time = _pick(env, "now", "clock_ms")
    sec_time = _pick(env, "now_sec", "clock_ms")
    dispatch: dict[str, Callable[..., str]] = {
        "default": lambda: default_upload(config, file, http_client),
        "github": lambda: github_web_upload(
            config, file, http_client,
            **_pick(env, "location_href", "now_sec", "clock_ms"),
        ),
        "aliOSS": lambda: alioss_upload(config, file, http_client, **s3_time),
        "txCOS": lambda: txcos_upload(config, file, http_client, **s3_time),
        "qiniu": lambda: qiniu_upload(config, file, http_client, **sec_time),
        "minio": lambda: minio_upload(config, file, http_client, **s3_time),
        "s3": lambda: s3_upload(config, file, http_client, **s3_time),
        "mp": lambda: mp_upload(
            config,
            file,
            http_client,
            store=env.get("store") or InMemoryMpTokenStore(),
            page_href=env.get("page_href", ""),
            now_ms=env.get("now_ms"),
        ),
        "r2": lambda: r2_upload(config, file, http_client, **s3_time),
        "upyun": lambda: upyun_upload(config, file, http_client, **sec_time),
        "telegram": lambda: telegram_upload(config, file, http_client),
        "cloudinary": lambda: cloudinary_upload(
            config, file, http_client, **_pick(env, "now_sec")
        ),
        "formCustom": lambda: form_custom_upload(config, file, http_client),
        "dcloud": lambda: dcloud_upload_file(
            config, file, http_client, **_pick(env, "name", "clock_ms")
        ),
    }
    return dispatch[provider.id]()


def _pick(mapping: dict, *keys: str) -> dict:
    return {k: mapping[k] for k in keys if mapping.get(k) is not None}
