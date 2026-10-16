"""安全内核测试：口令哈希、会话签名、CSRF、Origin、登录限速（AC-1 / AC-2）。"""

import time

from admin_console.security import (
    LoginLimiter,
    csrf_ok,
    hash_password,
    new_csrf_token,
    origin_ok,
    sign_session,
    verify_password,
    verify_session,
)

SECRET = "unit-test-secret"


def test_password_roundtrip():
    salt, digest = hash_password("S3cret-pass")
    assert verify_password("S3cret-pass", salt, digest)
    assert not verify_password("wrong-pass", salt, digest)


def test_password_storage_has_no_plaintext():
    salt, digest = hash_password("plain-text-password")
    assert "plain-text-password" not in salt
    assert "plain-text-password" not in digest
    assert salt and digest and salt != digest


def test_password_salt_is_unique():
    first, _ = hash_password("same-password")
    second, _ = hash_password("same-password")
    assert first != second


def test_verify_password_rejects_malformed():
    assert not verify_password("x", "not-hex", "not-hex")
    assert not verify_password("x", "", "")


def test_session_roundtrip():
    token = sign_session(SECRET, "admin@example.com", "admin", 3600, "管理员")
    payload = verify_session(token, SECRET)
    assert payload is not None
    assert payload["sub"] == "admin@example.com"
    assert payload["role"] == "admin"


def test_session_rejects_tampered_signature():
    token = sign_session(SECRET, "admin@example.com", "admin", 3600)
    head, payload, signature = token.split(".")
    tampered = f"{head}.{payload}.{'A' * len(signature)}"
    assert verify_session(tampered, SECRET) is None


def test_session_rejects_tampered_payload():
    import base64

    token = sign_session(SECRET, "admin@example.com", "editor", 3600)
    head, payload, signature = token.split(".")
    forged_payload = base64.urlsafe_b64encode(
        b'{"sub":"admin@example.com","role":"admin","exp":9999999999}'
    ).rstrip(b"=").decode()
    assert verify_session(f"{head}.{forged_payload}.{signature}", SECRET) is None


def test_session_rejects_expired():
    token = sign_session(SECRET, "admin@example.com", "admin", -10)
    assert verify_session(token, SECRET) is None


def test_session_rejects_wrong_secret():
    token = sign_session(SECRET, "admin@example.com", "admin", 3600)
    assert verify_session(token, "another-secret") is None


def test_session_rejects_malformed():
    assert verify_session("", SECRET) is None
    assert verify_session("a.b", SECRET) is None
    assert verify_session("a.b.c", SECRET) is None


def test_csrf_double_submit():
    token = new_csrf_token()
    assert csrf_ok(token, token)
    assert not csrf_ok("", token)
    assert not csrf_ok(token, "")
    assert not csrf_ok(token, token + "x")


def test_origin_checks():
    assert origin_ok({"host": "app.example.com", "origin": "https://app.example.com"})
    assert not origin_ok({"host": "app.example.com", "origin": "https://evil.test"})
    assert origin_ok({"host": "app.example.com"})  # 无 Origin（非浏览器）放行
    assert not origin_ok({"host": "app.example.com", "origin": "not-a-url"})


def test_login_limiter_locks_after_repeated_failures():
    limiter = LoginLimiter(window=600, max_attempts=3, lock_seconds=60)
    assert not limiter.is_locked("admin@example.com")
    for _ in range(3):
        limiter.register_failure("admin@example.com")
    assert limiter.is_locked("admin@example.com")

    limiter.register_success("admin@example.com")
    assert not limiter.is_locked("admin@example.com")


def test_login_limiter_expired_lock_releases():
    limiter = LoginLimiter(window=600, max_attempts=2, lock_seconds=1)
    limiter.register_failure("a@b.c")
    limiter.register_failure("a@b.c")
    assert limiter.is_locked("a@b.c")
    limiter._locks["a@b.c"] = time.time() - 5
    assert not limiter.is_locked("a@b.c")
