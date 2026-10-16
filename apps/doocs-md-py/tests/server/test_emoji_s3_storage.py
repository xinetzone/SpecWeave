"""TR-16.1 之四：表情资产 S3 后端 get/delete 录制与装配工厂。

LocalBackend 的 get/delete 已由 test_emoji_routes.py 端到端覆盖；本文件录制
S3Backend 的 GET、单对象 DELETE、DeleteObjects 批量 POST（XML 体 + Content-MD5
+ canonical query ``delete=``），以及 PrefixedStorage/build_emoji_backend 的
独立桶/复用桶前缀策略。
"""

import base64
import hashlib
from datetime import datetime, timezone

import httpx
import pytest

from doocs_md_py.server.config import Config
from doocs_md_py.server.emoji_storage import PrefixedStorage, build_emoji_backend
from doocs_md_py.server.storage import (
    LocalBackend,
    S3Backend,
    StoredObject,
    sha256_hex,
    sign_sigv4,
)

def fixed_clock() -> datetime:
    return datetime(2026, 10, 15, 8, 30, tzinfo=timezone.utc)


def _backend(handler, **kwargs):
    defaults = {
        "endpoint": "https://abc.r2.cloudflarestorage.com",
        "bucket": "emoji",
        "access_key_id": "AK",
        "secret_access_key": "SK",
        "region": "auto",
        "http_client": httpx.Client(transport=httpx.MockTransport(handler)),
        "clock": fixed_clock,
    }
    defaults.update(kwargs)
    return S3Backend(**defaults)


def test_s3_get_vhost_recording():
    recorded = {}
    body = b"\x89PNG-bytes"

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["method"] = request.method
        recorded["url"] = str(request.url)
        recorded["auth"] = request.headers.get("authorization", "")
        recorded["date"] = request.headers.get("x-amz-date", "")
        return httpx.Response(
            200, content=body,
            headers={"content-type": "image/png", "etag": '"abc123"'},
        )

    obj = _backend(handler).get("user/u1/i1.png")
    assert isinstance(obj, StoredObject)
    assert obj.data == body
    assert obj.content_type == "image/png"
    assert obj.etag == '"abc123"'
    assert recorded["method"] == "GET"
    assert recorded["url"] == "https://emoji.abc.r2.cloudflarestorage.com/user/u1/i1.png"
    assert recorded["auth"].startswith("AWS4-HMAC-SHA256 ")
    assert recorded["date"] == "20261015T083000Z"


def test_s3_get_404_returns_none():
    backend = _backend(lambda r: httpx.Response(404))
    assert backend.get("missing.png") is None


def test_s3_get_error_raises():
    backend = _backend(lambda r: httpx.Response(403, text="denied"))
    with pytest.raises(RuntimeError, match="S3 get failed: 403"):
        backend.get("k.png")


def test_s3_get_path_style_encoded_key():
    hit = {}

    def handler(request: httpx.Request) -> httpx.Response:
        hit["url"] = str(request.url)
        return httpx.Response(200, content=b"x", headers={"etag": '"e"'})

    backend = _backend(handler, force_path_style=True)
    obj = backend.get("user/u/a$b.png")
    assert obj.data == b"x"
    assert hit["url"] == "https://abc.r2.cloudflarestorage.com/emoji/user/u/a%24b.png"


def test_s3_delete_single_recording():
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["method"] = request.method
        recorded["url"] = str(request.url)
        recorded["auth"] = request.headers.get("authorization", "")
        recorded["body"] = request.content
        return httpx.Response(204)

    _backend(handler).delete("user/u1/i1.png")
    assert recorded["method"] == "DELETE"
    assert recorded["url"] == "https://emoji.abc.r2.cloudflarestorage.com/user/u1/i1.png"
    assert recorded["auth"].startswith("AWS4-HMAC-SHA256 ")
    assert recorded["body"] == b""


def test_s3_delete_single_404_silent():
    # R2/S3 删除不存在对象同样 204；404 也按幂等静默
    backend = _backend(lambda r: httpx.Response(404))
    backend.delete("ghost.png")  # 不抛错


def test_s3_delete_single_error_raises():
    backend = _backend(lambda r: httpx.Response(403, text="nope"))
    with pytest.raises(RuntimeError, match="S3 delete failed: 403"):
        backend.delete("k.png")


def test_s3_batch_delete_recording():
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["method"] = request.method
        recorded["url"] = str(request.url)
        recorded["body"] = request.content
        recorded["md5"] = request.headers.get("content-md5", "")
        recorded["ct"] = request.headers.get("content-type", "")
        recorded["auth"] = request.headers.get("authorization", "")
        return httpx.Response(200, content=b"")

    keys = ["user/u/a.png", "user/u/b.png", "user/u/c&d.png"]
    _backend(handler).delete(keys)

    assert recorded["method"] == "POST"
    assert recorded["url"] == "https://emoji.abc.r2.cloudflarestorage.com/?delete"
    assert recorded["ct"] == "application/xml"
    assert recorded["md5"] == base64.b64encode(
        hashlib.md5(recorded["body"]).digest()
    ).decode("ascii")
    body = recorded["body"].decode("utf-8")
    assert body.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<Key>user/u/a.png</Key>" in body
    assert "<Key>user/u/b.png</Key>" in body
    # XML 特殊字符转义
    assert "<Key>user/u/c&amp;d.png</Key>" in body
    assert "<Quiet>true</Quiet>" in body
    # 重算签名逐字节比对：证明 canonical query ``delete=`` 参与签名
    stamp = "20261015T083000Z"
    expected = sign_sigv4(
        "POST",
        "/",
        "delete=",
        {
            "Host": "emoji.abc.r2.cloudflarestorage.com",
            "x-amz-date": stamp,
            "Content-Type": "application/xml",
            "Content-MD5": recorded["md5"],
        },
        recorded["body"],
        access_key_id="AK",
        secret_access_key="SK",
        region="auto",
        service="s3",
        amz_date=stamp,
        payload_hash=sha256_hex(recorded["body"]),
    )
    assert recorded["auth"] == expected["authorization"]


def test_s3_batch_delete_path_style():
    hit = {}

    def handler(request: httpx.Request) -> httpx.Response:
        hit["url"] = str(request.url)
        return httpx.Response(200)

    _backend(handler, force_path_style=True).delete(["a.png", "b.png"])
    assert hit["url"] == "https://abc.r2.cloudflarestorage.com/emoji?delete"


def test_s3_batch_delete_error_raises():
    backend = _backend(lambda r: httpx.Response(500, text="boom"))
    with pytest.raises(RuntimeError, match="S3 batch delete failed: 500"):
        backend.delete(["a.png", "b.png"])


def test_delete_empty_list_no_request():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("must not call HTTP")

    _backend(handler).delete([])  # 不抛错


# ---- PrefixedStorage ----


class _RecordingBackend:
    def __init__(self):
        self.calls = []

    def put(self, key, data, content_type):
        self.calls.append(("put", key))
        return f"https://cdn/{key}"

    def get(self, key):
        self.calls.append(("get", key))
        return StoredObject(b"d", "image/png", '"e"')

    def delete(self, keys):
        self.calls.append(("delete", keys))


def test_prefixed_storage_naming():
    inner = _RecordingBackend()
    storage = PrefixedStorage(inner, "emoji")
    storage.put("user/u/a.png", b"d", "image/png")
    storage.get("user/u/a.png")
    storage.delete(["user/u/a.png", "user/u/b.png"])
    assert inner.calls == [
        ("put", "emoji/user/u/a.png"),
        ("get", "emoji/user/u/a.png"),
        ("delete", ["emoji/user/u/a.png", "emoji/user/u/b.png"]),
    ]


def test_prefixed_storage_empty_prefix_passes_through():
    inner = _RecordingBackend()
    storage = PrefixedStorage(inner, "")
    storage.delete("k")
    assert inner.calls == [("delete", "k")]


# ---- build_emoji_backend ----


def test_build_backend_default_local(tmp_path):
    config = Config(emoji_local_dir=str(tmp_path / "emoji"))
    storage = build_emoji_backend(config)
    assert isinstance(storage.inner, LocalBackend)
    assert storage.prefix == ""


def test_build_backend_s3_dedicated_bucket_no_prefix():
    config = Config(
        emoji_backend="s3",
        upload_s3_endpoint="https://acct.r2.cloudflarestorage.com",
        upload_s3_access_key_id="AK",
        upload_s3_secret_access_key="SK",
        upload_s3_bucket="uploads",
        emoji_s3_bucket="emoji-dedicated",
    )
    storage = build_emoji_backend(config, http_client=httpx.Client())
    assert isinstance(storage.inner, S3Backend)
    assert storage.inner._bucket == "emoji-dedicated"
    assert storage.prefix == ""


def test_build_backend_s3_shared_bucket_uses_prefix():
    config = Config(
        emoji_backend="s3",
        upload_s3_endpoint="https://acct.r2.cloudflarestorage.com",
        upload_s3_access_key_id="AK",
        upload_s3_secret_access_key="SK",
        upload_s3_bucket="uploads",
        emoji_prefix="emoji",
    )
    storage = build_emoji_backend(config, http_client=httpx.Client())
    assert isinstance(storage.inner, S3Backend)
    assert storage.inner._bucket == "uploads"
    assert storage.prefix == "emoji"


def test_build_backend_s3_missing_config_falls_back_local(tmp_path):
    config = Config(
        emoji_backend="s3",
        upload_s3_endpoint="",  # 凭证不全
        emoji_local_dir=str(tmp_path / "emoji"),
    )
    storage = build_emoji_backend(config)
    assert isinstance(storage.inner, LocalBackend)


def test_build_backend_unknown_value_falls_back_local(tmp_path):
    config = Config(
        emoji_backend="webdav",
        emoji_local_dir=str(tmp_path / "emoji"),
    )
    assert isinstance(build_emoji_backend(config).inner, LocalBackend)
