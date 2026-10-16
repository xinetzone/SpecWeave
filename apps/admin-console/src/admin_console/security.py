"""安全内核：口令哈希、会话签名、CSRF、Origin 校验、登录限速。

设计要点（对应 spec FR-1 / AC-1 / AC-2）：
- 口令：PBKDF2-HMAC-SHA256，20 万轮，每账号独立 16 字节随机 salt，只存哈希。
- 会话：HS256 自签 JWT（标准库 hmac+hashlib），含 exp/role，常量时间校验。
- CSRF：双提交 Cookie（非 HttpOnly）+ 请求头比对。
- Origin：浏览器发起的跨站请求一律拒绝。
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Dict, Optional, Tuple
from urllib.parse import urlsplit

PBKDF2_ROUNDS = 200_000
SALT_BYTES = 16
CSRF_HEADER = "x-csrf-token"
CSRF_COOKIE = "ac_csrf"
SESSION_COOKIE = "ac_session"


# ---- base64url -----------------------------------------------------------


def b64u_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def b64u_decode(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


# ---- 口令 ---------------------------------------------------------------


def hash_password(password: str, rounds: int = PBKDF2_ROUNDS) -> Tuple[str, str]:
    """返回 `(salt_hex, hash_hex)`；明文口令不落任何持久层。"""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return salt.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, hash_hex: str, rounds: int = PBKDF2_ROUNDS) -> bool:
    try:
        salt = bytes.fromhex(salt_hex or "")
        expected = bytes.fromhex(hash_hex or "")
    except ValueError:
        return False
    if not salt or not expected:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return hmac.compare_digest(digest, expected)


# ---- 会话令牌（HS256 JWT） ------------------------------------------------


def sign_session(secret: str, email: str, role: str, ttl: int, display_name: str = "") -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": email,
        "role": role,
        "name": display_name,
        "iat": now,
        "exp": now + int(ttl),
    }
    signing_input = b64u_encode(json.dumps(header, separators=(",", ":")).encode()) + "." + b64u_encode(
        json.dumps(payload, separators=(",", ":")).encode()
    )
    signature = hmac.new(secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return signing_input + "." + b64u_encode(signature)


def verify_session(token: str, secret: str) -> Optional[Dict[str, object]]:
    parts = (token or "").split(".")
    if len(parts) != 3:
        return None
    signing_input = parts[0] + "." + parts[1]
    expected = hmac.new(secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    try:
        provided = b64u_decode(parts[2])
    except Exception:  # noqa: BLE001 - 畸形 base64 一律视为无效令牌
        return None
    if not hmac.compare_digest(expected, provided):
        return None
    try:
        payload = json.loads(b64u_decode(parts[1]).decode("utf-8"))
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(payload, dict):
        return None
    exp = payload.get("exp")
    if not isinstance(exp, int) or exp <= int(time.time()):
        return None
    return payload


# ---- CSRF / Origin -------------------------------------------------------


def new_csrf_token() -> str:
    return secrets.token_urlsafe(24)


def csrf_ok(header_value: str, cookie_value: str) -> bool:
    if not header_value or not cookie_value:
        return False
    return hmac.compare_digest(str(header_value), str(cookie_value))


def _host_of(url: str) -> str:
    try:
        parts = urlsplit(url)
    except ValueError:
        return ""
    return (parts.netloc or "").lower()


def origin_ok(headers: Dict[str, str]) -> bool:
    """无 Origin 视为非浏览器调用（放行）；有 Origin 必须与 Host 同源。"""
    origin = headers.get("origin") or headers.get("referer") or ""
    if not origin:
        return True
    origin_host = _host_of(origin)
    if not origin_host:
        return False
    host = (headers.get("host") or "").lower()
    if host and origin_host == host:
        return True
    forwarded = (headers.get("x-forwarded-host") or "").lower()
    return bool(forwarded) and origin_host == forwarded


# ---- 登录限速 ------------------------------------------------------------

WINDOW_SECONDS = 600
MAX_ATTEMPTS = 10
LOCK_SECONDS = 600


class LoginLimiter:
    """进程内登录失败限速；Serverless 多实例下为尽力而为（配合恒定延时）。"""

    def __init__(self, window: int = WINDOW_SECONDS, max_attempts: int = MAX_ATTEMPTS,
                 lock_seconds: int = LOCK_SECONDS) -> None:
        self.window = window
        self.max_attempts = max_attempts
        self.lock_seconds = lock_seconds
        self._failures: Dict[str, list] = {}
        self._locks: Dict[str, float] = {}

    def locked_until(self, email: str) -> float:
        return self._locks.get(email.lower(), 0.0)

    def register_failure(self, email: str) -> int:
        key = (email or "").lower()
        now = time.time()
        bucket = [t for t in self._failures.get(key, []) if now - t < self.window]
        bucket.append(now)
        self._failures[key] = bucket
        if len(bucket) >= self.max_attempts:
            self._locks[key] = now + self.lock_seconds
            self._failures[key] = []
        return len(bucket)

    def register_success(self, email: str) -> None:
        key = (email or "").lower()
        self._failures.pop(key, None)
        self._locks.pop(key, None)

    def is_locked(self, email: str) -> bool:
        return self.locked_until(email) > time.time()
