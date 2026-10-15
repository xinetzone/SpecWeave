"""图片对象键命名（upstream: apps/api/src/upload-filename.ts 1:1）。

- 扩展名优先取文件名后缀（blob/bin/octet-stream 与 >10 字符后缀拒绝），
  其次 MIME 映射表，再次 subtype 截 ``+`` 前段，最后兜底 png；
- 对象键：``<epoch_ms>-<uuid4>.<ext>``。
"""

import time
import uuid
from collections.abc import Callable

# upstream: upload-filename.ts:3-14
MIME_TO_EXT: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "image/bmp": "bmp",
    "image/avif": "avif",
    "image/x-icon": "ico",
    "image/vnd.microsoft.icon": "ico",
}

# upstream: upload-filename.ts:16
INVALID_EXTENSIONS = frozenset({"blob", "bin", "octet-stream"})

MAX_EXTENSION_LENGTH = 10


def now_ms() -> int:
    """epoch 毫秒（等价 Date.now()）。"""
    return time.time_ns() // 1_000_000


# upstream: upload-filename.ts:18-32
def extension_from_mime(mime_type: str) -> str | None:
    mime = mime_type.strip().lower()
    if not mime:
        return None

    mapped = MIME_TO_EXT.get(mime)
    if mapped is not None:
        return mapped

    parts = mime.split("/", 1)
    subtype = parts[1] if len(parts) == 2 else ""
    if not subtype or subtype == "octet-stream":
        return None

    head = subtype.split("+", 1)[0]
    return head or None


# upstream: upload-filename.ts:34-45
def extension_from_filename(filename: str) -> str | None:
    name = filename.strip()
    dot_index = name.rfind(".")
    if dot_index <= 0 or dot_index >= len(name) - 1:
        return None

    ext = name[dot_index + 1 :].lower()
    if not ext or ext in INVALID_EXTENSIONS or len(ext) > MAX_EXTENSION_LENGTH:
        return None

    return ext


# upstream: upload-filename.ts:47-51
def resolve_image_extension(filename: str, mime_type: str) -> str:
    return (
        extension_from_filename(filename)
        or extension_from_mime(mime_type)
        or "png"
    )


# upstream: upload-filename.ts:53-56（uuidv4 在 Python 侧为 uuid.uuid4）
def build_dated_object_key(
    filename: str, mime_type: str, *, clock: Callable[[], int] | None = None
) -> str:
    ext = resolve_image_extension(filename, mime_type)
    millis = clock() if clock is not None else now_ms()
    return f"{millis}-{uuid.uuid4()}.{ext}"


def dated_directory(now_epoch_sec: float | None = None) -> str:
    """upstream: upload-github.ts/upload-r2.ts 内 getDir：``YYYY/MM/DD``（UTC）。"""
    return time.strftime("%Y/%m/%d", time.gmtime(now_epoch_sec))
