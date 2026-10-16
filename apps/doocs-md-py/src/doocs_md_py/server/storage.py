"""对象存储后端（Python 版新增抽象层）。

- :class:`LocalBackend`：落盘 ``STORAGE_LOCAL_DIR/<key>``，返回
  ``LOCAL_BASE_URL/<key>``；含路径穿越防护。
- :class:`S3Backend`：手写 AWS Signature V4（Authorization 头、signed payload），
  供 R2（``<account>.r2.cloudflarestorage.com``，region=auto）与任意 S3 兼容端点
  使用；上游 upload-r2.ts 的 Workers R2 binding 在 Python 侧等价为 SigV4 PUT。

签名纯函数 :func:`sign_sigv4` 全部输入可注入，配合 AWS 官方文档示例向量
（get-object/put-object）逐字节对拍（tests/server/test_sigv4_vectors.py）。
"""

import base64
import hashlib
import hmac
import os
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit
from xml.sax.saxutils import escape as xml_escape

import httpx

ALGORITHM = "AWS4-HMAC-SHA256"
UNSIGNED_PAYLOAD = "UNSIGNED-PAYLOAD"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


@dataclass(slots=True)
class StoredObject:
    """get 命中结果（upstream R2 对象的 body/httpMetadata.contentType/httpEtag）。"""

    data: bytes
    content_type: str | None
    etag: str


# --------------------------------------------------------------------------
# SigV4 纯函数（upstream 对应 Workers R2 binding 内部签名；此处按 AWS 官方
# 《Signature Calculations for the Authorization Header: Transferring Payload
# in a Single Chunk》规范实现）
# --------------------------------------------------------------------------


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hmac_sha256(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def derive_signing_key(secret_key: str, date_stamp: str, region: str, service: str) -> bytes:
    """任务表 Task 3：kDate→kRegion→kService→kSigning。"""
    k_date = hmac_sha256(("AWS4" + secret_key).encode("utf-8"), date_stamp)
    k_region = hmac_sha256(k_date, region)
    k_service = hmac_sha256(k_region, service)
    return hmac_sha256(k_service, "aws4_request")


def encode_canonical_path(path: str) -> str:
    """S3 单次 URI 编码：保留分段斜杠；``~`` 等 unreserved 不编码（``$``→%24）。"""
    return quote(path, safe="/")


def build_canonical_headers(headers: Mapping[str, str]) -> tuple[str, str]:
    """返回 (CanonicalHeaders, SignedHeaders)；键小写、按名排序、值去首尾空白。"""
    lowered = {k.strip().lower(): v.strip() for k, v in headers.items()}
    names = sorted(lowered)
    canonical = "".join(f"{name}:{lowered[name]}\n" for name in names)
    signed = ";".join(names)
    return canonical, signed


def sign_sigv4(
    method: str,
    raw_path: str,
    query_string: str,
    headers: Mapping[str, str],
    payload: bytes,
    *,
    access_key_id: str,
    secret_access_key: str,
    region: str,
    service: str,
    amz_date: str,
    payload_hash: str | None = None,
) -> dict[str, str]:
    """构造 SigV4 签名。

    ``raw_path`` 为**未百分号编码**的请求路径（如 ``/test$file.text``），函数
    内部按 S3 规则做单次编码（``$``→%24、分段斜杠保留）；``amz_date`` 形如
    ``20130524T000000Z``；``query_string`` 为空串表示无查询（调用方须预先做
    canonical query 编码与排序）。返回 canonical request、string-to-sign、
    签名与 Authorization 头，便于逐层对拍。
    """
    date_stamp = amz_date[:8]
    canonical_path = encode_canonical_path(raw_path)
    canonical_headers, signed_headers = build_canonical_headers(headers)
    payload_digest = payload_hash if payload_hash is not None else sha256_hex(payload)

    canonical_request = (
        f"{method}\n"
        f"{canonical_path}\n"
        f"{query_string}\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{payload_digest}"
    )

    scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        f"{ALGORITHM}\n"
        f"{amz_date}\n"
        f"{scope}\n"
        f"{sha256_hex(canonical_request.encode('utf-8'))}"
    )

    signing_key = derive_signing_key(secret_access_key, date_stamp, region, service)
    signature = hmac.new(
        signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    authorization = (
        f"{ALGORITHM} "
        f"Credential={access_key_id}/{scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    return {
        "canonical_request": canonical_request,
        "string_to_sign": string_to_sign,
        "signature": signature,
        "authorization": authorization,
        "signed_headers": signed_headers,
    }


def amz_date_format(now: datetime) -> str:
    """UTC ``YYYYMMDDTHHMMSSZ``。"""
    return now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


# --------------------------------------------------------------------------
# 后端抽象
# --------------------------------------------------------------------------


class StorageBackend(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes, content_type: str) -> str:
        """上传对象，返回可公开访问的 URL。"""
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> StoredObject | None:
        """读取对象；不存在返回 None（upstream R2Bucket.get 语义）。"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, keys: str | Iterable[str]) -> None:
        """删除单个或批量对象；对象缺失静默（upstream R2 delete 幂等）。"""
        raise NotImplementedError


class LocalBackend(StorageBackend):
    """落盘后端（Python 版新增）：``<base_dir>/<key>`` → ``<base_url>/<key>``。"""

    def __init__(self, base_dir: str | os.PathLike[str], base_url: str):
        self._base_dir = Path(base_dir).resolve()
        self._base_url = base_url.rstrip("/")

    @property
    def base_dir(self) -> Path:
        return self._base_dir

    def _safe_target(self, key: str) -> Path:
        # key 由服务端用日期+uuid 生成，本身不可信度低，但仍强制目录包含校验，
        # 阻断绝对路径、盘符、.. 穿越等任何逃逸形态。
        target = (self._base_dir / key).resolve()
        if self._base_dir != target and self._base_dir not in target.parents:
            raise ValueError(f"unsafe object key: {key!r}")
        return target

    def put(self, key: str, data: bytes, content_type: str) -> str:
        target = self._safe_target(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        # 原子写：同目录临时文件 + replace，避免并发半成品
        tmp = target.with_name(target.name + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(target)
        return f"{self._base_url}/{key}"

    def get(self, key: str) -> StoredObject | None:
        target = self._safe_target(key)
        if not target.is_file():
            return None
        data = target.read_bytes()
        # 本地文件系统不存 Content-Type（路由以 DB 中的 mime 为准）；
        # ETag 按 R2/S3 非分段对象惯例给带双引号的 MD5 hex
        etag = f'"{hashlib.md5(data).hexdigest()}"'  # noqa: S324
        return StoredObject(data=data, content_type=None, etag=etag)

    def delete(self, keys: str | Iterable[str]) -> None:
        key_list = [keys] if isinstance(keys, str) else list(keys)
        for key in key_list:
            target = self._safe_target(key)
            try:
                target.unlink()
            except FileNotFoundError:
                continue


class S3Backend(StorageBackend):
    """S3 兼容后端（R2/MinIO/通用 S3）：SigV4 header 鉴权 PUT 整对象。"""

    def __init__(
        self,
        endpoint: str,
        bucket: str,
        access_key_id: str,
        secret_access_key: str,
        *,
        region: str = "auto",
        public_url: str = "",
        force_path_style: bool = False,
        service: str = "s3",
        http_client: httpx.Client | None = None,
        clock: Callable[[], datetime] | None = None,
    ):
        if not endpoint:
            raise ValueError("s3 endpoint is required")
        self._endpoint = endpoint.rstrip("/")
        self._bucket = bucket
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._region = region
        self._public_url = public_url.rstrip("/")
        self._force_path_style = force_path_style
        self._service = service
        self._client = http_client
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        parsed = urlsplit(self._endpoint)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"invalid s3 endpoint: {endpoint!r}")
        self._scheme = parsed.scheme
        self._host = parsed.netloc

    def _target_host_and_paths(self, key: str) -> tuple[str, str, str]:
        """返回 (host, raw_path, encoded_path)；virtual-host 与 path-style 二选一。"""
        encoded_key = quote(key, safe="/")
        if self._force_path_style:
            return (
                self._host,
                f"/{self._bucket}/{key}",
                f"/{self._bucket}/{encoded_key}",
            )
        return f"{self._bucket}.{self._host}", f"/{key}", f"/{encoded_key}"

    def put(self, key: str, data: bytes, content_type: str) -> str:
        host, raw_path, encoded_path = self._target_host_and_paths(key)
        url = f"{self._scheme}://{host}{encoded_path}"
        stamp = amz_date_format(self._clock())
        payload_digest = sha256_hex(data)

        headers = {
            "Host": host,
            "x-amz-content-sha256": payload_digest,
            "x-amz-date": stamp,
        }
        if content_type:
            headers["Content-Type"] = content_type
        signed = sign_sigv4(
            "PUT",
            # 签名函数对原始路径做单次编码，与 encoded_path 形态一致
            raw_path,
            "",
            headers,
            data,
            access_key_id=self._access_key_id,
            secret_access_key=self._secret_access_key,
            region=self._region,
            service=self._service,
            amz_date=stamp,
            payload_hash=payload_digest,
        )

        send_headers = {
            "Authorization": signed["authorization"],
            "x-amz-content-sha256": payload_digest,
            "x-amz-date": stamp,
            "Content-Length": str(len(data)),
        }
        if content_type:
            send_headers["Content-Type"] = content_type

        client = self._client or httpx.Client(timeout=15.0)
        try:
            response = client.put(url, content=data, headers=send_headers)
        finally:
            if self._client is None:
                client.close()
        if response.status_code // 100 != 2:
            raise RuntimeError(f"S3 upload failed: {response.status_code} {response.text[:300]}")

        if self._public_url:
            return f"{self._public_url}/{key}"
        return url

    # ---- 表情资产用：GET / DELETE（upstream R2 binding get/delete 等价物）----

    def _do_request(
        self, method: str, url: str, headers: Mapping[str, str], content: bytes = b""
    ) -> httpx.Response:
        client = self._client or httpx.Client(timeout=15.0)
        try:
            return client.request(method, url, content=content, headers=dict(headers))
        finally:
            if self._client is None:
                client.close()

    def get(self, key: str) -> StoredObject | None:
        """upstream R2Bucket.get：404 映射 None，其余非 2xx 抛错。"""
        host, raw_path, encoded_path = self._target_host_and_paths(key)
        url = f"{self._scheme}://{host}{encoded_path}"
        stamp = amz_date_format(self._clock())
        sign_headers = {"Host": host, "x-amz-date": stamp}
        signed = sign_sigv4(
            "GET",
            raw_path,
            "",
            sign_headers,
            b"",
            access_key_id=self._access_key_id,
            secret_access_key=self._secret_access_key,
            region=self._region,
            service=self._service,
            amz_date=stamp,
            payload_hash=EMPTY_SHA256,
        )
        response = self._do_request(
            "GET",
            url,
            {
                "Authorization": signed["authorization"],
                "x-amz-date": stamp,
            },
        )
        if response.status_code == 404:
            return None
        if response.status_code // 100 != 2:
            raise RuntimeError(f"S3 get failed: {response.status_code} {response.text[:300]}")
        return StoredObject(
            data=response.content,
            content_type=response.headers.get("content-type"),
            etag=response.headers.get("etag", f'"{hashlib.md5(response.content).hexdigest()}"'),
        )

    def _bucket_root_parts(self) -> tuple[str, str, str]:
        """DeleteObjects 的桶根 (host, raw_path, encoded_path)。"""
        if self._force_path_style:
            return self._host, f"/{self._bucket}", f"/{self._bucket}"
        return f"{self._bucket}.{self._host}", "/", "/"

    def delete(self, keys: str | Iterable[str]) -> None:
        """upstream R2 delete(key|keys[])：单对象 DELETE，多对象 POST ?delete。"""
        key_list = [keys] if isinstance(keys, str) else list(keys)
        if not key_list:
            return

        if len(key_list) == 1:
            host, raw_path, encoded_path = self._target_host_and_paths(key_list[0])
            url = f"{self._scheme}://{host}{encoded_path}"
            stamp = amz_date_format(self._clock())
            signed = sign_sigv4(
                "DELETE",
                raw_path,
                "",
                {"Host": host, "x-amz-date": stamp},
                b"",
                access_key_id=self._access_key_id,
                secret_access_key=self._secret_access_key,
                region=self._region,
                service=self._service,
                amz_date=stamp,
                payload_hash=EMPTY_SHA256,
            )
            response = self._do_request(
                "DELETE",
                url,
                {"Authorization": signed["authorization"], "x-amz-date": stamp},
            )
            if response.status_code // 100 != 2 and response.status_code != 404:
                raise RuntimeError(
                    f"S3 delete failed: {response.status_code} {response.text[:300]}"
                )
            return

        host, raw_path, encoded_path = self._bucket_root_parts()
        url = f"{self._scheme}://{host}{encoded_path}?delete"
        object_xml = "".join(
            f"<Object><Key>{xml_escape(key)}</Key></Object>" for key in key_list
        )
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            f"<Delete>{object_xml}<Quiet>true</Quiet></Delete>"
        ).encode("utf-8")
        content_md5 = base64.b64encode(hashlib.md5(body).digest()).decode("ascii")
        stamp = amz_date_format(self._clock())
        signed = sign_sigv4(
            "POST",
            raw_path,
            "delete=",
            {
                "Host": host,
                "x-amz-date": stamp,
                "Content-Type": "application/xml",
                "Content-MD5": content_md5,
            },
            body,
            access_key_id=self._access_key_id,
            secret_access_key=self._secret_access_key,
            region=self._region,
            service=self._service,
            amz_date=stamp,
            payload_hash=sha256_hex(body),
        )
        response = self._do_request(
            "POST",
            url,
            {
                "Authorization": signed["authorization"],
                "x-amz-date": stamp,
                "Content-Type": "application/xml",
                "Content-MD5": content_md5,
            },
            content=body,
        )
        if response.status_code // 100 != 2:
            raise RuntimeError(
                f"S3 batch delete failed: {response.status_code} {response.text[:300]}"
            )
