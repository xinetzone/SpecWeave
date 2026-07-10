"""知识库分级加密存储模块。

提供三级安全加密策略：public（明文）、internal（敏感字段加密）、confidential（全文加密）。
使用 AES-256-GCM 认证加密，确保数据机密性和完整性。
"""

import base64
import logging
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KEY_FILE = PROJECT_ROOT / ".knowledge-key"
ENV_KEY_NAME = "KNOWLEDGE_ENCRYPTION_KEY"

ENCRYPTED_PREFIX = "enc:"
CONFIDENTIAL_HEADER = "---ENC---"
PUBLIC_HEADER = "---"

DEFAULT_SENSITIVE_FIELDS = {"author", "source", "source_url", "x-toml-ref"}
PLAINTEXT_METADATA_FIELDS = {"security_level", "knowledge_type", "integrity", "category", "tags", "id", "title"}

PBKDF2_ITERATIONS = 600000
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
TAG_SIZE = 16


def _derive_key(user_key: bytes, salt: bytes) -> bytes:
    """使用 PBKDF2-HMAC-SHA256 从用户密钥派生 32 字节 AES 密钥。

    Args:
        user_key: 用户提供的原始密钥材料。
        salt: 16 字节随机盐值。

    Returns:
        32 字节派生密钥。
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(user_key)


def generate_key() -> str:
    """生成随机加密密钥，返回 base64 编码字符串。

    Returns:
        base64 编码的 32 字节随机密钥。
    """
    key = AESGCM.generate_key(bit_length=256)
    return base64.b64encode(key).decode("ascii")


def get_encryption_key() -> bytes:
    """从环境变量或密钥文件获取加密密钥。

    优先级：
    1. 环境变量 KNOWLEDGE_ENCRYPTION_KEY（base64 编码）
    2. 项目根目录 .knowledge-key 文件（base64 编码）

    Returns:
        32 字节原始密钥。

    Raises:
        RuntimeError: 当环境变量和密钥文件都不存在时抛出。
        ValueError: 当密钥格式无效时抛出。
    """
    env_key = os.environ.get(ENV_KEY_NAME)
    if env_key:
        try:
            key = base64.b64decode(env_key.strip(), validate=True)
            if len(key) != KEY_SIZE:
                raise ValueError(f"环境变量 {ENV_KEY_NAME} 解码后长度必须为 {KEY_SIZE} 字节")
            return key
        except Exception as e:
            raise ValueError(f"环境变量 {ENV_KEY_NAME} 格式无效: {e}") from e

    if KEY_FILE.exists():
        try:
            file_content = KEY_FILE.read_text(encoding="utf-8").strip()
            key = base64.b64decode(file_content, validate=True)
            if len(key) != KEY_SIZE:
                raise ValueError(f"密钥文件 {KEY_FILE} 解码后长度必须为 {KEY_SIZE} 字节")
            return key
        except Exception as e:
            raise ValueError(f"密钥文件 {KEY_FILE} 格式无效: {e}") from e

    raise RuntimeError(
        f"未找到加密密钥。请设置环境变量 {ENV_KEY_NAME} 或在项目根目录创建 {KEY_FILE.name} 文件。"
        f"可使用 generate_key() 函数生成密钥。"
    )


def _encrypt_value(plaintext: str, key: bytes) -> str:
    """加密单个字符串值，返回带 enc: 前缀的 base64 编码密文。

    密文格式：base64(salt(16B) + nonce(12B) + tag(16B) + ciphertext)

    Args:
        plaintext: 明文字符串。
        key: 32 字节 AES 密钥。

    Returns:
        enc: 前缀开头的 base64 编码密文。
    """
    salt = os.urandom(SALT_SIZE)
    derived_key = _derive_key(key, salt)
    aesgcm = AESGCM(derived_key)
    nonce = os.urandom(NONCE_SIZE)
    plaintext_bytes = plaintext.encode("utf-8")
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, None)
    combined = salt + nonce + ciphertext_with_tag
    return ENCRYPTED_PREFIX + base64.b64encode(combined).decode("ascii")


def _decrypt_value(encrypted_value: str, key: bytes) -> str:
    """解密单个以 enc: 前缀开头的加密值。

    Args:
        encrypted_value: enc: 前缀开头的 base64 编码密文。
        key: 32 字节 AES 密钥。

    Returns:
        解密后的明文字符串。

    Raises:
        ValueError: 当密文格式无效或认证失败时抛出。
    """
    if not encrypted_value.startswith(ENCRYPTED_PREFIX):
        raise ValueError("加密值必须以 enc: 前缀开头")

    try:
        combined = base64.b64decode(encrypted_value[len(ENCRYPTED_PREFIX):], validate=True)
    except Exception as e:
        raise ValueError(f"base64 解码失败: {e}") from e

    min_len = SALT_SIZE + NONCE_SIZE + TAG_SIZE
    if len(combined) < min_len:
        raise ValueError(f"密文长度不足，至少需要 {min_len} 字节")

    salt = combined[:SALT_SIZE]
    nonce = combined[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext_with_tag = combined[SALT_SIZE + NONCE_SIZE:]

    derived_key = _derive_key(key, salt)
    aesgcm = AESGCM(derived_key)

    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    except Exception as e:
        raise ValueError(f"解密失败（密钥错误或数据已篡改）: {e}") from e

    return plaintext_bytes.decode("utf-8")


def _encrypt_full_content(metadata: dict, content: str, key: bytes) -> str:
    """加密完整条目（frontmatter + content）。

    输出格式：---ENC---\nbase64(salt(16B) + nonce(12B) + tag(16B) + ciphertext)

    Args:
        metadata: 元数据字典。
        content: 正文内容。
        key: 32 字节 AES 密钥。

    Returns:
        ---ENC--- 标记开头的加密内容字符串。
    """
    from .knowledge_security import _serialize_yaml_frontmatter

    frontmatter_str = _serialize_yaml_frontmatter(metadata)
    full_plaintext = f"{frontmatter_str}\n\n{content}"

    salt = os.urandom(SALT_SIZE)
    derived_key = _derive_key(key, salt)
    aesgcm = AESGCM(derived_key)
    nonce = os.urandom(NONCE_SIZE)
    plaintext_bytes = full_plaintext.encode("utf-8")
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext_bytes, None)
    combined = salt + nonce + ciphertext_with_tag
    encoded = base64.b64encode(combined).decode("ascii")

    return f"{CONFIDENTIAL_HEADER}\n{encoded}"


def _decrypt_full_content(encrypted_content: str, key: bytes) -> tuple[dict, str]:
    """解密 ---ENC--- 格式的全文加密内容。

    Args:
        encrypted_content: ---ENC--- 开头的加密内容。
        key: 32 字节 AES 密钥。

    Returns:
        (metadata, content) 元组。

    Raises:
        ValueError: 当格式无效或解密失败时抛出。
    """
    from .frontmatter import split_frontmatter_and_content

    lines = encrypted_content.split("\n", 1)
    if len(lines) < 2 or lines[0].strip() != CONFIDENTIAL_HEADER:
        raise ValueError("无效的全文加密格式，应以 ---ENC--- 开头")

    try:
        combined = base64.b64decode(lines[1].strip(), validate=True)
    except Exception as e:
        raise ValueError(f"base64 解码失败: {e}") from e

    min_len = SALT_SIZE + NONCE_SIZE + TAG_SIZE
    if len(combined) < min_len:
        raise ValueError(f"密文长度不足，至少需要 {min_len} 字节")

    salt = combined[:SALT_SIZE]
    nonce = combined[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext_with_tag = combined[SALT_SIZE + NONCE_SIZE:]

    derived_key = _derive_key(key, salt)
    aesgcm = AESGCM(derived_key)

    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    except Exception as e:
        raise ValueError(f"解密失败（密钥错误或数据已篡改）: {e}") from e

    full_plaintext = plaintext_bytes.decode("utf-8")
    metadata, content = split_frontmatter_and_content(full_plaintext)
    return metadata, content


def encrypt_entry(
    metadata: dict[str, str | list[str]],
    content: str,
    security_level: str,
    key: bytes | None = None
) -> tuple[dict[str, str | list[str]], str, bool]:
    """加密知识条目。

    Args:
        metadata: 元数据字典。
        content: 正文内容。
        security_level: 安全级别（public/internal/confidential）。
        key: 32 字节 AES 密钥，public 级别可省略。

    Returns:
        (encrypted_metadata, encrypted_content, is_encrypted) 元组。

    Raises:
        ValueError: 当安全级别无效或密钥缺失时抛出。
    """
    if security_level == "public":
        result_metadata = dict(metadata)
        result_metadata["security_level"] = "public"
        return result_metadata, content, False

    if key is None:
        key = get_encryption_key()

    if security_level == "internal":
        encrypted_metadata = {}
        for field, value in metadata.items():
            if field in DEFAULT_SENSITIVE_FIELDS and isinstance(value, str):
                encrypted_metadata[field] = _encrypt_value(value, key)
            else:
                encrypted_metadata[field] = value
        encrypted_metadata["security_level"] = "internal"
        return encrypted_metadata, content, True

    if security_level == "confidential":
        safe_metadata = dict(metadata)
        safe_metadata["security_level"] = "confidential"
        encrypted_full = _encrypt_full_content(safe_metadata, content, key)
        return {"security_level": "confidential", "is_encrypted": "full"}, encrypted_full, True

    raise ValueError(f"无效的安全级别: {security_level}，支持 public/internal/confidential")


def decrypt_entry(
    metadata: dict[str, str | list[str]],
    content: str,
    key: bytes | None = None
) -> tuple[dict[str, str | list[str]], str, str, bool]:
    """解密知识条目，自动检测加密格式。

    Args:
        metadata: 元数据字典（全文加密时为空）。
        content: 内容字符串（可能加密或明文）。
        key: 32 字节 AES 密钥，明文时可省略。

    Returns:
        (decrypted_metadata, decrypted_content, security_level, is_valid) 元组。
    """
    if content.startswith(CONFIDENTIAL_HEADER + "\n") or content.startswith(CONFIDENTIAL_HEADER):
        if key is None:
            try:
                key = get_encryption_key()
            except RuntimeError as e:
                return {}, "", "confidential", False

        try:
            dec_metadata, dec_content = _decrypt_full_content(content, key)
            sec_level = dec_metadata.get("security_level", "confidential")
            return dec_metadata, dec_content, sec_level, True
        except Exception as e:
            logger.warning(f"全文解密失败: {e}")
            return metadata, content, "confidential", False

    sec_level = metadata.get("security_level", "public") if metadata else "public"

    if sec_level == "public":
        return dict(metadata) if metadata else {}, content, "public", True

    if key is None:
        try:
            key = get_encryption_key()
        except RuntimeError:
            return dict(metadata) if metadata else {}, content, sec_level, False

    decrypted_metadata = {}
    has_encrypted_fields = False
    all_valid = True

    for field, value in (metadata or {}).items():
        if isinstance(value, str) and value.startswith(ENCRYPTED_PREFIX):
            has_encrypted_fields = True
            try:
                decrypted_metadata[field] = _decrypt_value(value, key)
            except Exception as e:
                logger.warning(f"字段 {field} 解密失败: {e}")
                decrypted_metadata[field] = value
                all_valid = False
        else:
            decrypted_metadata[field] = value

    if not has_encrypted_fields:
        return decrypted_metadata, content, sec_level, all_valid

    return decrypted_metadata, content, "internal", all_valid
