"""E2EE 参考实现：PBKDF2-SHA256(100000) 派生主密钥 + AES-256-GCM 包裹。

与源文档 ``concepts/02`` §4.1（F-052）逐字对应：
``deriveKeyFromSecret`` 用 **PBKDF2（100000 次迭代、SHA-256）** 派生
**AES-GCM-256** 主密钥。本模块以 Python 复刻同一算法与参数，使服务端可在
不接触明文的前提下验证、恢复与重加密。

硬约束：
- 明文 Key 只在函数参数与返回值中出现，**绝不写入任何持久化结构**；
- 所有密文 blob 携带 alg/kdf/iterations/salt/iv，便于未来升级 KDF 参数；
- 摘要比较一律使用 :func:`hmac.compare_digest` 常量时间比较。
"""

import base64
import hashlib
import hmac
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .logging_utils import get_logger

ALG_AES_GCM = "AES-256-GCM"
KDF_PBKDF2_SHA256 = "PBKDF2-SHA256"
PBKDF2_ITERATIONS = 100_000
_KEY_BITS = 256
_KEY_BYTES = _KEY_BITS // 8
_SALT_BYTES = 16
_IV_BYTES = 12

logger = get_logger("crypto")


def random_salt(size: int = _SALT_BYTES) -> bytes:
    return secrets.token_bytes(size)


def b64e(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


def derive_master_key(secret: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """PBKDF2-SHA256 派生 256-bit 主密钥。"""
    return hashlib.pbkdf2_hmac(
        "sha256",
        secret.encode("utf-8"),
        salt,
        iterations,
        dklen=_KEY_BYTES,
    )


def aes_gcm_encrypt(key: bytes, plaintext: bytes, *, aad: bytes | None = None) -> tuple[bytes, bytes]:
    """返回 ``(iv, ciphertext)``，IV 每次随机 96-bit。"""
    iv = secrets.token_bytes(_IV_BYTES)
    ct = AESGCM(key).encrypt(iv, plaintext, aad)
    return iv, ct


def aes_gcm_decrypt(
    key: bytes, iv: bytes, ciphertext: bytes, *, aad: bytes | None = None
) -> bytes:
    return AESGCM(key).decrypt(iv, ciphertext, aad)


def digest(secret: str) -> str:
    """统一令牌/恢复密语/密码的 SHA-256 摘要（十六进制）。"""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def digests_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)


# --------------------------------------------------------------------------
# 业务级封装
# --------------------------------------------------------------------------


def encrypt_secret(master_key: bytes, plaintext: str) -> tuple[bytes, bytes]:
    """用主密钥加密一段明文，返回 ``(iv, ct)``。"""
    return aes_gcm_encrypt(master_key, plaintext.encode("utf-8"))


def decrypt_secret(master_key: bytes, iv: bytes, ct: bytes) -> str:
    return aes_gcm_decrypt(master_key, iv, ct).decode("utf-8")


def wrap_master_key(master_key: bytes, credential: str, salt: bytes) -> tuple[bytes, bytes]:
    """用口令/恢复密语派生的 KEK 包裹主密钥，返回 ``(iv, wrapped)``。"""
    kek = derive_master_key(credential, salt)
    return aes_gcm_encrypt(kek, master_key)


def unwrap_master_key(wrapped: bytes, iv: bytes, credential: str, salt: bytes) -> bytes:
    kek = derive_master_key(credential, salt)
    return aes_gcm_decrypt(kek, iv, wrapped)


def new_master_key() -> bytes:
    """生成新的 256-bit 主密钥。"""
    return secrets.token_bytes(_KEY_BYTES)


def issue_token() -> str:
    """签发统一令牌（``byok_live_`` 前缀 + 128-bit 随机熵）。"""
    from .models.identity import TOKEN_PREFIX

    return TOKEN_PREFIX + secrets.token_urlsafe(16)


def issue_recovery_secret() -> str:
    from .models.identity import RECOVERY_PREFIX

    return RECOVERY_PREFIX + secrets.token_urlsafe(16)


