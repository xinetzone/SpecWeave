"""表情文件与名称校验（upstream: apps/api/src/emoji-validate.ts 1:1）。

- 仅收 png/jpeg/gif/webp 四类，先比对 MIME 白名单再比对 magic bytes（防伪）；
- 名称净化取 basename、去扩展名、剔除控制字符、空白折叠、截断 100、空值兜底；
- 包名非字符串或净化后为空返回 None，截断 60。
"""

import re

from .upload_config import UPLOAD_MAX_BYTES

# upstream: emoji-validate.ts:3
EMOJI_MAX_ITEMS = 100

# upstream: emoji-validate.ts:5-10
MIME_EXTENSIONS = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}

MAX_EMOJI_NAME_LENGTH = 100
MAX_PACK_NAME_LENGTH = 60
DEFAULT_EMOJI_NAME = "emoji"


def _strip_control_characters(value: str) -> str:
    """upstream: emoji-validate.ts:18-25；按码点迭代，剔除 U+0000-001F 与 U+007F。"""
    return "".join(c for c in value if ord(c[0]) > 0x1F and ord(c[0]) != 0x7F)


def _bytes_match(data: bytes, expected: bytes, offset: int = 0) -> bool:
    return all(data[offset + i] == b for i, b in enumerate(expected))


def _magic_matches(mime: str, data: bytes) -> bool:
    """upstream: emoji-validate.ts:31-42。"""
    if mime == "image/png":
        return _bytes_match(data, bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)))
    if mime == "image/jpeg":
        return _bytes_match(data, b"\xff\xd8\xff")
    if mime == "image/gif":
        signature = data[:6].decode("ascii", errors="replace")
        return signature in ("GIF87a", "GIF89a")
    # image/webp：RIFF 头 + 偏移 8 的 WEBP
    return _bytes_match(data, b"RIFF") and _bytes_match(data, b"WEBP", offset=8)


def validate_emoji_file(mime: str, size: int, data: bytes) -> dict:
    """upstream: emoji-validate.ts:44-67。

    返回判别联合：``{"ok": True, "mime", "extension"}`` 或
    ``{"ok": False, "error": empty_file|file_too_large|invalid_file_type|mime_mismatch}``。
    """
    if size <= 0:
        return {"ok": False, "error": "empty_file"}
    if size > UPLOAD_MAX_BYTES:
        return {"ok": False, "error": "file_too_large"}

    normalized_mime = mime.strip().lower()
    if normalized_mime not in MIME_EXTENSIONS:
        return {"ok": False, "error": "invalid_file_type"}

    if not _magic_matches(normalized_mime, data):
        return {"ok": False, "error": "mime_mismatch"}

    return {"ok": True, "mime": normalized_mime, "extension": MIME_EXTENSIONS[normalized_mime]}


def sanitize_emoji_name(value: str, fallback: str = DEFAULT_EMOJI_NAME) -> str:
    """upstream: emoji-validate.ts:69-77。"""
    # split(/[\\/]/)：按反斜杠或正斜杠切分取最后一段
    basename = re.split(r"[\\/]", value)[-1]
    without_extension = re.sub(r"\.[^.]+$", "", basename)
    sanitized = re.sub(r"\s+", " ", _strip_control_characters(without_extension)).strip()
    # JS slice(100) 按 UTF-16 码元；名称为常规 BMP 文本，码点切分等价
    sanitized = sanitized[:MAX_EMOJI_NAME_LENGTH]
    return sanitized or fallback


def sanitize_pack_name(value: object) -> str | None:
    """upstream: emoji-validate.ts:79-87；非字符串或净化后为空 → None。"""
    if not isinstance(value, str):
        return None
    sanitized = re.sub(r"\s+", " ", _strip_control_characters(value)).strip()
    sanitized = sanitized[:MAX_PACK_NAME_LENGTH]
    return sanitized or None
