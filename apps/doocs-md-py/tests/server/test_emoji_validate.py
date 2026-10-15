"""TR-16.1 之一：emoji_validate 纯函数（对齐上游 emoji-validate.test.ts 并扩展）。"""

import pytest

from doocs_md_py.server.emoji_validate import (
    EMOJI_MAX_ITEMS,
    sanitize_emoji_name,
    sanitize_pack_name,
    validate_emoji_file,
)
from doocs_md_py.server.upload_config import UPLOAD_MAX_BYTES

PNG_MAGIC = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))
JPEG_MAGIC = b"\xff\xd8\xff\xe0"
WEBP_MAGIC = b"RIFF\x00\x00\x00\x00WEBP"


@pytest.mark.parametrize(
    ("mime", "data", "extension"),
    [
        ("image/png", PNG_MAGIC, "png"),
        ("image/jpeg", JPEG_MAGIC, "jpg"),
        ("image/gif", b"GIF89a", "gif"),
        ("image/gif", b"GIF87a", "gif"),
        ("image/webp", WEBP_MAGIC, "webp"),
    ],
)
def test_accepts_valid_magic_bytes(mime, data, extension):
    result = validate_emoji_file(mime, len(data), data)
    assert result["ok"] is True
    assert result["extension"] == extension
    assert result["mime"] == mime


@pytest.mark.parametrize(
    ("mime", "data"),
    [
        ("image/png", JPEG_MAGIC),            # png 声明 jpeg 字节
        ("image/jpeg", PNG_MAGIC),            # jpeg 声明 png 字节
        ("image/gif", b"GIF99a"),             # 非法 GIF 版本
        ("image/webp", b"RIFF\x00\x00\x00\x00XXXX"),  # RIFF 非 WEBP
        ("image/webp", b"XXXX\x00\x00\x00\x00WEBP"),  # WEBP 非 RIFF
    ],
)
def test_rejects_magic_mismatch(mime, data):
    assert validate_emoji_file(mime, len(data), data) == {
        "ok": False,
        "error": "mime_mismatch",
    }


def test_rejects_unsupported_mime():
    assert validate_emoji_file("image/svg+xml", 4, b"\x01\x02\x03\x04") == {
        "ok": False,
        "error": "invalid_file_type",
    }
    assert validate_emoji_file("", 4, PNG_MAGIC)["error"] == "invalid_file_type"


def test_normalizes_mime_case_and_whitespace():
    result = validate_emoji_file("  Image/PNG  ", len(PNG_MAGIC), PNG_MAGIC)
    assert result["ok"] is True
    assert result["mime"] == "image/png"


def test_rejects_empty_and_oversized():
    assert validate_emoji_file("image/png", 0, b"") == {
        "ok": False,
        "error": "empty_file",
    }
    assert validate_emoji_file(
        "image/png", UPLOAD_MAX_BYTES + 1, b""
    ) == {"ok": False, "error": "file_too_large"}


def test_emoji_max_items_constant():
    assert EMOJI_MAX_ITEMS == 100


def test_sanitize_name_removes_path_extension_control_and_whitespace():
    # 上游 emoji-validate.test.ts:41 同一向量
    assert sanitize_emoji_name("folder\\ happy\x00   face.png") == "happy face"
    # 斜杠与反斜杠都取最后一段
    assert sanitize_emoji_name("a/b\\c.jpeg") == "c"
    # 其余控制字符（0x01、0x7F）剔除
    assert sanitize_emoji_name("s\x01m\x7file") == "smile"
    # 仅扩展名被剥离：点在中间不视为扩展名
    assert sanitize_emoji_name("a.b.png") == "a.b"


def test_sanitize_name_fallback_and_truncation():
    assert sanitize_emoji_name("\x00\x01   ") == "emoji"
    assert sanitize_emoji_name("\x00\x01   ", fallback="wave") == "wave"
    long_name = "x" * 150
    result = sanitize_emoji_name(long_name)
    assert len(result) == 100


def test_sanitize_pack_name():
    assert sanitize_pack_name("  My  Pack \n") == "My Pack"
    assert sanitize_pack_name(" \x00 ") is None
    assert sanitize_pack_name(None) is None
    assert sanitize_pack_name(123) is None
    long_name = "y" * 80
    assert len(sanitize_pack_name(long_name)) == 60
