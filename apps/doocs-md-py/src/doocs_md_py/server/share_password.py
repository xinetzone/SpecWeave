"""分享访问密码（upstream: apps/api/src/share-password.ts 1:1）。

- PBKDF2-SHA256 100_000 轮、16 字节随机盐，串格式 ``pbkdf2:<iter>:<saltB64>:<hashB64>``
  （btoa/atob 标准 Base64，含 padding，Python base64 标准字母表等价）；
- 比较使用 hmac.compare_digest（等价上游逐字节 XOR diff 的常量时间语义）；
- 访问令牌 JWT 复用 security.issue/verify_share_access_token（T10 已按同文件
  issueShareAccessToken/verifyShareAccessToken 逐字移植）。
"""

import base64
import hashlib
import hmac
import math
import os

# upstream: share-password.ts:4-9
PBKDF2_ITERATIONS = 100_000
GENERATED_PASSWORD_LENGTH = 8
GENERATED_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789"
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 64
SALT_BYTES = 16
HASH_BYTES = 32  # deriveBits 256


def share_access_cookie_name(share_id: str) -> str:
    """upstream: share-password.ts:32-34。"""
    return f"md_share_{share_id}"


def share_access_cookie_path(share_id: str) -> str:
    """upstream: share-password.ts:36-38。"""
    return f"/s/{share_id}"


def generate_share_password() -> str:
    """upstream: share-password.ts:40-46；逐字保留 ``byte % alphabet.length`` 取模。"""
    raw = os.urandom(GENERATED_PASSWORD_LENGTH)
    return "".join(
        GENERATED_ALPHABET[byte % len(GENERATED_ALPHABET)] for byte in raw
    )


def parse_share_password_mode(value) -> str | None:
    """upstream: share-password.ts:48-52。"""
    if value in ("none", "custom", "auto"):
        return value
    return None


def parse_custom_password(value) -> str | None:
    """upstream: share-password.ts:54-61；trim 后 4–64 字符。"""
    if not isinstance(value, str):
        return None
    password = value.strip()
    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        return None
    return password


def _to_base64(raw: bytes) -> str:
    """等价 btoa(String.fromCharCode(...bytes))：标准 Base64（含 = padding）。"""
    return base64.b64encode(raw).decode("ascii")


def _from_base64(value: str) -> bytes:
    """等价 atob；非法 Base64 抛 ValueError（调用方捕获返 False）。"""
    return base64.b64decode(value.encode("ascii"), validate=True)


def derive_password_hash(
    password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS
) -> bytes:
    """PBKDF2-HMAC-SHA256；供存储串生成与校验共用。"""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, dklen=HASH_BYTES
    )


def hash_share_password(password: str) -> str:
    """upstream: share-password.ts:63-84。"""
    salt = os.urandom(SALT_BYTES)
    digest = derive_password_hash(password, salt, PBKDF2_ITERATIONS)
    return f"pbkdf2:{PBKDF2_ITERATIONS}:{_to_base64(salt)}:{_to_base64(digest)}"


def verify_share_password(password: str, stored: str) -> bool:
    """upstream: share-password.ts:86-131。

    四段格式、迭代次数为正有限整数、盐/hash Base64 可解码、长度一致后常量时间比较。
    """
    parts = stored.split(":")
    if len(parts) != 4 or parts[0] != "pbkdf2":
        return False

    # Number(parts[1]) 语义（"1e3"→1000 可解析）；WebCrypto iterations 须整数
    try:
        iterations_float = float(parts[1])
    except ValueError:
        return False

    if (
        not math.isfinite(iterations_float)
        or iterations_float <= 0
        or not iterations_float.is_integer()
    ):
        return False
    iterations = int(iterations_float)

    try:
        salt = _from_base64(parts[2])
        expected = _from_base64(parts[3])
    except (ValueError, TypeError):
        return False

    if not expected:
        return False

    actual = derive_password_hash(password, salt, iterations)
    if len(actual) != len(expected):
        return False
    return hmac.compare_digest(actual, expected)
