"""Supabase Storage 接入：上传 / 删除 / 访问 URL，含体积与类型边界。

设计要点（对应 spec FR-6、AC-6）：
- 服务端转发裸二进制到 Storage，浏览器永不接触 service_role key。
- 存储路径由服务端生成（日期分片 + 随机名），文件名净化杜绝路径穿越。
- 未配置云端时降级为 `memory://` 占位，功能可演示但不产生真实文件。
"""

import re
import secrets
import time
from typing import Dict, Optional
from urllib.parse import quote

from .config import Config
from .http_client import request

_UNSAFE = re.compile(r"[^\w\u4e00-\u9fff.-]+")
_DOTS = re.compile(r"\.{2,}")


def sanitize_filename(name: str, limit: int = 80) -> str:
    """净化文件名：去控制字符、路径分隔符与 `..`，超长截断。"""
    raw = (name or "").replace("\\", "/").split("/")[-1]
    raw = raw.strip().strip("\x00")
    raw = _UNSAFE.sub("_", raw)
    raw = _DOTS.sub(".", raw).strip(".")
    raw = raw[:limit]
    return raw or "file"


def sanitize_object_path(path: str) -> str:
    """净化对象路径：逐段净化，杜绝 `../` 穿越与空段。"""
    segments = []
    for part in (path or "").replace("\\", "/").split("/"):
        part = part.strip()
        if not part or part in (".", ".."):
            continue
        segments.append(sanitize_filename(part))
    return "/".join(segments)


class StorageError(Exception):
    """上传/删除失败的可预期错误（体积、类型、上游拒绝）。"""

    def __init__(self, code: str, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


class Storage:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._memory: Dict[str, bytes] = {}

    @property
    def enabled(self) -> bool:
        return self.cfg.cloud_ready

    def _auth_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        return {
            "apikey": self.cfg.supabase_service_role_key,
            "authorization": f"Bearer {self.cfg.supabase_service_role_key}",
            "content-type": content_type,
        }

    def object_path(self, filename: str) -> str:
        stamp = time.strftime("%Y/%m")
        safe = sanitize_filename(filename)
        return f"uploads/{stamp}/{secrets.token_hex(8)}_{safe}"

    def upload(self, filename: str, content_type: str, data: bytes) -> Dict[str, object]:
        if not data:
            raise StorageError("empty_file", "文件内容为空", 400)
        if len(data) > self.cfg.max_upload_bytes:
            limit_mb = self.cfg.max_upload_bytes / 1024 / 1024
            raise StorageError("file_too_large", f"文件超过 {limit_mb:.0f}MB 上限", 413)
        if not self.cfg.allows_upload_type(content_type):
            raise StorageError("unsupported_type", f"不支持的文件类型：{content_type or '未知'}", 415)
        path = self.object_path(filename)
        if not self.enabled:
            self._memory[path] = data
            return {
                "path": path,
                "url": f"memory://{path}",
                "size": len(data),
                "content_type": content_type,
                "degraded": True,
            }

        url = f"{self.cfg.storage_base}/object/{quote(self.cfg.supabase_bucket)}/{quote(path, safe='/')}"
        headers = self._auth_headers(content_type or "application/octet-stream")
        headers["x-upsert"] = "true"
        resp = request("POST", url, headers=headers, body=data,
                       timeout=self.cfg.http_timeout, retries=self.cfg.http_retries)
        if not resp.ok and resp.status != 0:
            raise StorageError("upstream_rejected", f"云端存储拒绝上传（{resp.status}）", 502)
        if resp.status == 0:
            self._memory[path] = data
            return {
                "path": path,
                "url": f"memory://{path}",
                "size": len(data),
                "content_type": content_type,
                "degraded": True,
            }
        return {
            "path": path,
            "url": self.public_url(path),
            "size": len(data),
            "content_type": content_type,
            "degraded": False,
        }

    def delete(self, path: str) -> bool:
        clean = sanitize_object_path(path)
        if not clean:
            return False
        self._memory.pop(clean, None)
        if not self.enabled:
            return True
        url = f"{self.cfg.storage_base}/object/{quote(self.cfg.supabase_bucket)}/{quote(clean, safe='/')}"
        resp = request("DELETE", url, headers=self._auth_headers(),
                       timeout=self.cfg.http_timeout, retries=0)
        return resp.ok or resp.status == 404

    def public_url(self, path: str) -> str:
        clean = sanitize_object_path(path)
        if not self.enabled:
            return f"memory://{clean}"
        return (
            f"{self.cfg.storage_base}/object/public/"
            f"{quote(self.cfg.supabase_bucket)}/{quote(clean, safe='/')}"
        )

    def signed_url(self, path: str) -> Optional[str]:
        """私有桶场景：返回带签名的临时访问地址。"""
        clean = sanitize_object_path(path)
        if not self.enabled:
            return f"memory://{clean}"
        url = f"{self.cfg.storage_base}/object/sign/{quote(self.cfg.supabase_bucket)}/{quote(clean, safe='/')}"
        import json as _json

        resp = request(
            "POST",
            url,
            headers=self._auth_headers(),
            body=_json.dumps({"expiresIn": self.cfg.signed_url_ttl}).encode("utf-8"),
            timeout=self.cfg.http_timeout,
            retries=0,
        )
        payload = resp.json()
        if isinstance(payload, dict) and payload.get("signedURL"):
            return f"{self.cfg.supabase_url}{payload['signedURL']}"
        return self.public_url(clean)
