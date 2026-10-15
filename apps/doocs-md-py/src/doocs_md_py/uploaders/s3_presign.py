"""S3 SigV4 presigned URL（upstream: @aws-sdk/s3-request-presigner getSignedUrl）。

Web 客户端五家 S3 兼容图床（aliOSS/txCOS/minio/s3/r2，providers.ts）统一用
``getSignedUrl(PutObjectCommand, { expiresIn: 300 })`` 生成查询串签名 URL，
再 ``fetch(url, { method: 'PUT', body: file })``。与 T13 服务端 header 签名
（x-amz-content-sha256 头 + 整包 hash）不同：presign 只签 ``host`` 头，
载荷占位为 ``UNSIGNED-PAYLOAD``，凭证放在 X-Amz-* 查询参数里。

纯函数全部时间可注入，测试以 @aws-sdk/s3-request-presigner@3.1147.0
（与上游 apps/web 锁版一致）录制 golden 对拍。
"""

import hashlib
import hmac
from datetime import datetime, timezone
from urllib.parse import quote

from ..server.storage import (
    ALGORITHM,
    UNSIGNED_PAYLOAD,
    derive_signing_key,
    encode_canonical_path,
    sha256_hex,
)

_PRESIGN_EXPIRES_SEC = 300  # upstream: providers.ts 五家均 expiresIn: 300

# @aws-sdk/client-s3@3.1147.0 presign PutObject（command 无 Body，上游逐字同构）
# 默认注入的 flexible-checksum 查询参数：空体 CRC32 base64 恒为 AAAAAA==。
_EMPTY_CRC32_B64 = "AAAAAA=="
# x-id 是 SDK operation 追踪参数，但实测 3.1147 它在签名中间件之前注入，
# **参与** canonical query 签名，同时固定出现在最终 URL 末尾。
_OPERATION_QUERY = (("x-id", "PutObject"),)

# RFC3986 unreserved（含 ~，不含 /）——canonical query 值里的 / 必须 %2F
_SAFE_CHARS = "-_.~"


def _aws_query_encode(value: str) -> str:
    """SigV4 canonical query 编码：仅 A-Za-z0-9-_.~ 不编码。"""
    return quote(value, safe=_SAFE_CHARS)


def canonical_query_string(params: dict[str, str]) -> str:
    """键按字节序排序后 ``k=v`` 串联（键值均 RFC3986 编码）。"""
    pairs = sorted(params.items(), key=lambda kv: kv[0])
    return "&".join(f"{_aws_query_encode(k)}={_aws_query_encode(v)}" for k, v in pairs)


def amz_now(now: datetime | None = None) -> tuple[str, str]:
    """返回 (amz_date, date_stamp)，UTC。"""
    moment = now if now is not None else datetime.now(timezone.utc)
    amz_date = moment.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return amz_date, amz_date[:8]


def build_presigned_put_url(
    *,
    host: str,
    raw_path: str,
    access_key_id: str,
    secret_access_key: str,
    region: str,
    amz_date: str,
    expires_in: int = _PRESIGN_EXPIRES_SEC,
    service: str = "s3",
    scheme: str = "https",
) -> dict[str, str]:
    """生成 PutObject presigned URL，返回 URL 与全部中间产物（便于逐层对拍）。

    ``raw_path`` 为未编码 key 路径（以 ``/`` 开头）；``host`` 不含 scheme。
    查询参数集合与 URL 内出现顺序逐字对齐锁版 SDK 3.1147.0（含
    UNSIGNED-PAYLOAD 与空体 CRC32 校验参数；``x-id`` 不参与签名，仅追加）。
    """
    date_stamp = amz_date[:8]
    scope = f"{date_stamp}/{region}/{service}/aws4_request"
    credential = f"{access_key_id}/{scope}"

    # 参与签名的查询参数（canonical 时另按字节序排序）
    sign_params: dict[str, str] = {
        "X-Amz-Algorithm": ALGORITHM,
        "X-Amz-Content-Sha256": UNSIGNED_PAYLOAD,
        "X-Amz-Credential": credential,
        "X-Amz-Date": amz_date,
        "X-Amz-Expires": str(expires_in),
        "X-Amz-SignedHeaders": "host",
        "x-amz-checksum-crc32": _EMPTY_CRC32_B64,
        "x-amz-sdk-checksum-algorithm": "CRC32",
        **dict(_OPERATION_QUERY),
    }

    canonical_query = canonical_query_string(sign_params)
    canonical_path = encode_canonical_path(raw_path)
    canonical_request = (
        f"PUT\n"
        f"{canonical_path}\n"
        f"{canonical_query}\n"
        f"host:{host}\n"
        f"\n"
        f"host\n"
        f"{UNSIGNED_PAYLOAD}"
    )
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

    # SDK 最终 URL 的查询段按其内部插入顺序（非 canonical 字母序）：
    # Signature 位于 Expires 与 SignedHeaders 之间，x-id 收尾。
    url_pairs: list[tuple[str, str]] = [
        ("X-Amz-Algorithm", ALGORITHM),
        ("X-Amz-Content-Sha256", UNSIGNED_PAYLOAD),
        ("X-Amz-Credential", credential),
        ("X-Amz-Date", amz_date),
        ("X-Amz-Expires", str(expires_in)),
        ("X-Amz-Signature", signature),
        ("X-Amz-SignedHeaders", "host"),
        ("x-amz-checksum-crc32", _EMPTY_CRC32_B64),
        ("x-amz-sdk-checksum-algorithm", "CRC32"),
        *_OPERATION_QUERY,
    ]
    url_query = "&".join(
        f"{_aws_query_encode(k)}={_aws_query_encode(v)}" for k, v in url_pairs
    )
    url = f"{scheme}://{host}{canonical_path}?{url_query}"
    return {
        "url": url,
        "canonical_request": canonical_request,
        "canonical_query": canonical_query,
        "string_to_sign": string_to_sign,
        "signature": signature,
    }
