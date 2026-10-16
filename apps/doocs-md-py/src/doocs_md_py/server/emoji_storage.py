"""表情资产存储装配（upstream: Env.EMOJI_ASSETS 独立 R2 桶的 Python 等价）。

上游通过 Workers R2 binding 操作独立桶；Python 侧两种形态：
- ``local``（默认，零配置）：专用本地目录 ``emoji_local_dir``；
- ``s3``：SigV4 S3/R2。配置独立桶 ``DOOCS_MD_PY_EMOJI_S3_BUCKET`` 时键名与
  上游一致（``user/<uid>/<id>.<ext>``）；留空复用上传桶时以 ``emoji_prefix``
  为键前缀隔离，避免与图片上传对象混放。

路由只面对 :class:`PrefixedStorage` 的 put/get/delete 三方法，DB 中存的始终
是上游形态的 object_key，前缀仅作用于物理后端。
"""

import httpx

from .config import Config
from .storage import LocalBackend, S3Backend, StoredObject, StorageBackend

ASSET_URL_BASE = "/emojis/assets"


class PrefixedStorage:
    """对底层后端的键统一加固定前缀（与 R2 独立桶等价的命名空间隔离）。"""

    def __init__(self, inner: StorageBackend, prefix: str):
        self.inner = inner
        self.prefix = prefix.strip("/")

    def _with_prefix(self, key: str) -> str:
        return f"{self.prefix}/{key}" if self.prefix else key

    def put(self, key: str, data: bytes, content_type: str) -> str:
        return self.inner.put(self._with_prefix(key), data, content_type)

    def get(self, key: str) -> StoredObject | None:
        return self.inner.get(self._with_prefix(key))

    def delete(self, keys: str | list[str]) -> None:
        if isinstance(keys, str):
            self.inner.delete(self._with_prefix(keys))
        else:
            self.inner.delete([self._with_prefix(key) for key in keys])


def build_emoji_backend(
    config: Config, *, http_client: httpx.Client | None = None
) -> PrefixedStorage:
    """按配置装配表情资产后端；未知 backend 兜底 local。"""
    backend = (config.emoji_backend or "local").strip().lower()
    if backend == "s3":
        dedicated_bucket = bool(config.emoji_s3_bucket)
        bucket = config.emoji_s3_bucket or config.upload_s3_bucket
        if (
            not bucket
            or not config.upload_s3_endpoint
            or not config.upload_s3_access_key_id
            or not config.upload_s3_secret_access_key
        ):
            # 配置不全时回退本地，避免因表情存储阻断全部服务启动
            return PrefixedStorage(
                LocalBackend(config.emoji_local_dir, ASSET_URL_BASE), ""
            )
        inner: StorageBackend = S3Backend(
            endpoint=config.upload_s3_endpoint,
            bucket=bucket,
            access_key_id=config.upload_s3_access_key_id,
            secret_access_key=config.upload_s3_secret_access_key,
            region=config.upload_s3_region,
            public_url=config.emoji_s3_public_url or config.upload_s3_public_url,
            force_path_style=config.upload_s3_force_path_style,
            http_client=http_client,
        )
        # 独立桶键名与上游一致；复用上传桶时加 emoji_prefix 隔离
        prefix = "" if dedicated_bucket else config.emoji_prefix
        return PrefixedStorage(inner, prefix)

    return PrefixedStorage(LocalBackend(config.emoji_local_dir, ASSET_URL_BASE), "")
