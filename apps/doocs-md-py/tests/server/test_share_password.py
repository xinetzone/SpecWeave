"""TR-12.2 分享密码（upstream: share-password.ts）+ WebCrypto 互认 golden。"""

import base64
import json
import re
from pathlib import Path

import pytest

from doocs_md_py.server import share_password as sp

GOLDEN = (
    Path(__file__).resolve().parents[1] / "golden" / "share_pbkdf2_interop.json"
)


# ---- 常量与 cookie 名 ----


def test_constants_match_upstream():
    assert sp.PBKDF2_ITERATIONS == 100_000
    assert sp.GENERATED_PASSWORD_LENGTH == 8
    assert sp.MIN_PASSWORD_LENGTH == 4
    assert sp.MAX_PASSWORD_LENGTH == 64
    # 上游字母表 55 字符：大写去 I/O（24）、小写去 i/l/o（23）、数字 2-9（8）
    assert len(sp.GENERATED_ALPHABET) == 55
    for removed in ("I", "O", "i", "l", "o", "0", "1"):
        assert removed not in sp.GENERATED_ALPHABET


def test_cookie_name_and_path():
    assert sp.share_access_cookie_name("abc123") == "md_share_abc123"
    assert sp.share_access_cookie_path("abc123") == "/s/abc123"


# ---- 模式与自定义密码解析 ----


@pytest.mark.parametrize("value", ["none", "custom", "auto"])
def test_parse_mode_valid(value):
    assert sp.parse_share_password_mode(value) == value


@pytest.mark.parametrize("value", ["NONE", "", None, 1, "x", True])
def test_parse_mode_invalid(value):
    assert sp.parse_share_password_mode(value) is None


def test_parse_custom_password_trims_and_bounds():
    assert sp.parse_custom_password("  abcd  ") == "abcd"
    assert sp.parse_custom_password("abcd") == "abcd"
    assert sp.parse_custom_password("a" * 64) == "a" * 64
    assert sp.parse_custom_password("abc") is None          # < 4
    assert sp.parse_custom_password("a" * 65) is None       # > 64
    assert sp.parse_custom_password("    ") is None
    assert sp.parse_custom_password(None) is None
    assert sp.parse_custom_password(1234) is None


# ---- 生成 ----


def test_generate_password_shape():
    for _ in range(50):
        password = sp.generate_share_password()
        assert len(password) == 8
        assert all(ch in sp.GENERATED_ALPHABET for ch in password)


def test_generate_password_distribution_is_random():
    samples = {sp.generate_share_password() for _ in range(100)}
    assert len(samples) > 90  # 极小概率碰撞，56^8 空间内应几乎全异


# ---- hash/verify ----


def test_hash_format():
    stored = sp.hash_share_password("abcd1234")
    parts = stored.split(":")
    assert len(parts) == 4
    assert parts[0] == "pbkdf2"
    assert parts[1] == "100000"
    salt = base64.b64decode(parts[2])
    digest = base64.b64decode(parts[3])
    assert len(salt) == 16
    assert len(digest) == 32


def test_hash_uses_random_salt():
    assert sp.hash_share_password("same") != sp.hash_share_password("same")


def test_verify_roundtrip():
    stored = sp.hash_share_password("MyPass123")
    assert sp.verify_share_password("MyPass123", stored) is True
    assert sp.verify_share_password("mypass123", stored) is False
    assert sp.verify_share_password("", stored) is False


def test_verify_unicode_password():
    stored = sp.hash_share_password("分享密码四")
    assert sp.verify_share_password("分享密码四", stored) is True
    assert sp.verify_share_password("分享密码五", stored) is False


@pytest.mark.parametrize(
    "stored",
    [
        "",
        "pbkdf2:100000:aa:bb",          # 段数对但坏 base64
        "xx:100000:aa:bb",              # 前缀错
        "pbkdf2:100000:aa",             # 段数少
        "pbkdf2:abc:aa:bb",             # iterations 非数
        "pbkdf2:0:aa:bb",               # iterations=0
        "pbkdf2:-5:aa:bb",
        "pbkdf2:1.5:aa:bb",             # 非整数
        "pbkdf2:Infinity:aa:bb",
        f"pbkdf2:100000:{base64.b64encode(b'1234567890123456').decode()}:",  # 空 hash
    ],
)
def test_verify_malformed_stored(stored):
    assert sp.verify_share_password("abcd1234", stored) is False


def test_verify_wrong_length_hash_rejected():
    salt = base64.b64encode(b"1234567890123456").decode()
    short = base64.b64encode(b"0" * 16).decode()
    stored = f"pbkdf2:100000:{salt}:{short}"
    assert sp.verify_share_password("abcd1234", stored) is False


def test_fixed_rfc_vector():
    """密码+固定盐+迭代 → 已知 hash（独立锁定，防止算法漂移）。"""
    salt = base64.b64decode("Zml4ZWQtc2FsdC0xNmJ5IQ==")
    digest = sp.derive_password_hash("abcd1234", salt, 100_000)
    assert (
        base64.b64encode(digest).decode()
        == "9nLzB9dUCgu32YSVMKLs9zgc+OhzDYeoLrBl1i2vMIQ="
    )
    # 该固定向量可直接组成存储串并通过校验
    stored = (
        "pbkdf2:100000:Zml4ZWQtc2FsdC0xNmJ5IQ==:"
        "9nLzB9dUCgu32YSVMKLs9zgc+OhzDYeoLrBl1i2vMIQ="
    )
    assert sp.verify_share_password("abcd1234", stored) is True


# ---- Node WebCrypto 互认 golden（由 scripts/share_pbkdf2_regen.py 生成）----


def test_pbkdf2_interop_golden():
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert data["iterations"] == 100_000
    assert re.fullmatch(r"v\d+\.\d+\.\d+", data["node"])
    # 五项互认检查全部为真
    assert data["checks"] == {
        "fixed_vector_matches": True,
        "py_stored_verified_by_node": True,
        "py_stored_rejects_wrong_by_node": True,
        "node_stored_verified_by_python": True,
        "node_stored_rejects_wrong_by_python": True,
    }
    # Python 现算结果必须仍等于 golden 锁定的固定向量
    salt = base64.b64decode(data["fixed_salt_b64"])
    digest = sp.derive_password_hash(data["password"], salt, data["iterations"])
    assert base64.b64encode(digest).decode() == data["fixed_hash_b64"]
    # Node 生成的存储串 Python 可直接验
    assert sp.verify_share_password(data["password"], data["node_stored"]) is True
