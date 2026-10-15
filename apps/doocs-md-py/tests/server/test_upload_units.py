"""T13 纯函数与后端单测：文件名解析、限流窗口、LocalBackend 穿越防护、
GitHub Contents API 录制对拍、S3Backend SigV4 PUT 录制（upstream:
upload-filename.ts/upload-rate.ts/upload-github.ts/upload-r2.ts）。
"""

import random
import re
from datetime import datetime, timezone

import httpx
import pytest

from doocs_md_py.server import upload_filename as uf
from doocs_md_py.server import upload_rate
from doocs_md_py.server.config import Config
from doocs_md_py.server.storage import LocalBackend, S3Backend
from doocs_md_py.server.upload_config import GithubUploadConfig
from doocs_md_py.server.upload_github import UploadPayload, upload_to_github
from doocs_md_py.server.upload_r2 import build_r2_backend

PNG = b"\x89PNG\r\n\x1a\n-binary-"


# ---- upload-filename -------------------------------------------------------


@pytest.mark.parametrize(
    "mime,ext",
    [
        ("image/jpeg", "jpg"),
        ("image/jpg", "jpg"),
        ("image/png", "png"),
        ("image/gif", "gif"),
        ("image/webp", "webp"),
        ("image/svg+xml", "svg"),
        ("image/bmp", "bmp"),
        ("image/avif", "avif"),
        ("image/x-icon", "ico"),
        ("image/vnd.microsoft.icon", "ico"),
        ("IMAGE/PNG", "png"),
        ("  image/png ", "png"),
    ],
)
def test_mime_table(mime, ext):
    assert uf.extension_from_mime(mime) == ext


@pytest.mark.parametrize(
    "mime",
    ["", "  ", "image/", "image/octet-stream", "application/octet-stream"],
)
def test_mime_fallback_none(mime):
    assert uf.extension_from_mime(mime) is None


def test_mime_leading_slash_subtype():
    # 与上游 TS mime.split("/")[1] 一致："/png" 得 subtype "png"
    assert uf.extension_from_mime("/png") == "png"


def test_mime_non_image_subtype_still_resolved():
    # MIME 解析本身不做 image/ 前缀门（门在路由），subtype 即扩展名
    assert uf.extension_from_mime("video/mp4") == "mp4"


def test_mime_subtype_plus_truncation():
    assert uf.extension_from_mime("image/x-xbitmap+xml") == "x-xbitmap"
    assert uf.extension_from_mime("image/+xml") is None


@pytest.mark.parametrize(
    "name,ext",
    [
        ("a.png", "png"),
        ("photo.JPEG", "jpeg"),
        ("x.y.z.webp", "webp"),
        ("a" * 30 + ".abcdefghij", "abcdefghij"),  # 恰好 10
    ],
)
def test_filename_ext_ok(name, ext):
    assert uf.extension_from_filename(name) == ext


@pytest.mark.parametrize(
    "name",
    [
        "png",
        ".png",
        "a.",
        "a.blob",
        "a.bin",
        "a.octet-stream",
        "a.abcdefghijk",  # 11 字符
        "  ",
        "a.BLOB",
    ],
)
def test_filename_ext_rejected(name):
    assert uf.extension_from_filename(name) is None


def test_resolve_priority():
    assert uf.resolve_image_extension("a.gif", "image/jpeg") == "gif"
    assert uf.resolve_image_extension("a.blob", "image/jpeg") == "jpg"
    assert uf.resolve_image_extension("noext", "image/png") == "png"
    assert uf.resolve_image_extension("a.bin", "application/octet-stream") == "png"


def test_dated_object_key_shape():
    key = uf.build_dated_object_key("a.png", "image/png", clock=lambda: 1_700_000_000_000)
    assert re.fullmatch(r"1700000000000-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.png", key)


def test_dated_directory_utc():
    # 1709509567 = 2024-03-03T21:06:07Z
    assert uf.dated_directory(1_709_509_567) == "2024/03/03"


# ---- upload-rate ------------------------------------------------------------


def test_rate_limit_for_plan():
    assert upload_rate.upload_rate_limit_for_plan("pro") == 300
    assert upload_rate.upload_rate_limit_for_plan("free") == 120
    assert upload_rate.upload_rate_limit_for_plan(None) == 60


def test_rate_limit_window_and_isolation(conn):
    h1 = datetime(2026, 10, 15, 10, 30, 12, tzinfo=timezone.utc)
    h2 = datetime(2026, 10, 15, 11, 0, 0, tzinfo=timezone.utc)
    assert upload_rate.get_upload_rate_limit_count(conn, "upload:ip:1.1.1.1", now=h1) == 0
    upload_rate.increment_upload_rate_limit(conn, "upload:ip:1.1.1.1", now=h1)
    upload_rate.increment_upload_rate_limit(conn, "upload:ip:1.1.1.1", now=h1)
    assert upload_rate.get_upload_rate_limit_count(conn, "upload:ip:1.1.1.1", now=h1) == 2
    # 跨 UTC 小时归零
    assert upload_rate.get_upload_rate_limit_count(conn, "upload:ip:1.1.1.1", now=h2) == 0
    # scope 隔离
    assert upload_rate.get_upload_rate_limit_count(conn, "upload:ip:9.9.9.9", now=h1) == 0
    assert upload_rate.get_upload_rate_limit_count(conn, "upload:user:u1", now=h1) == 0
    assert 1 <= upload_rate.upload_rate_limit_retry_after_sec(now=h1) <= 3600


# ---- LocalBackend ------------------------------------------------------------


def test_local_backend_roundtrip(tmp_path):
    backend = LocalBackend(tmp_path / "store", "http://img.local/x/")
    url = backend.put("2026/10/15/k.png", PNG, "image/png")
    target = tmp_path / "store" / "2026" / "10" / "15" / "k.png"
    assert target.read_bytes() == PNG
    assert url == "http://img.local/x/2026/10/15/k.png"
    # 重名原子覆盖
    backend.put("2026/10/15/k.png", b"v2", "image/png")
    assert target.read_bytes() == b"v2"
    assert not target.with_name("k.png.tmp").exists()


@pytest.mark.parametrize(
    "key",
    [
        "../escape.png",
        "a/../../escape.png",
        "..\\..\\escape.png",  # Windows 分隔符
        "a/../../../x",
    ],
)
def test_local_backend_blocks_traversal(tmp_path, key):
    backend = LocalBackend(tmp_path / "store", "/uploads")
    with pytest.raises(ValueError, match="unsafe object key"):
        backend.put(key, PNG, "image/png")


# ---- GitHub 后端（请求录制）----------------------------------------------------


def _gh_config(**over):
    params = {
        "username": "bucketio",
        "repo_list": ("img0", "img1"),
        "branch": "main",
        "tokens": ("tok-a", "tok-b"),
        "use_cdn": True,
    }
    params.update(over)
    return GithubUploadConfig(**params)


def test_github_put_recording_and_cdn_rewrite():
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        recorded["method"] = request.method
        recorded["url"] = str(request.url)
        recorded["headers"] = dict(request.headers)
        recorded["body"] = json.loads(request.content)
        repo = request.url.path.split("/repos/bucketio/")[1].split("/")[0]
        return httpx.Response(
            200,
            json={"content": {"download_url":
                f"https://raw.githubusercontent.com/bucketio/{repo}/main/2026/10/x.png"}},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    config = _gh_config()
    payload = UploadPayload("a.png", "image/png", PNG)
    rng = random.Random(42)
    url = upload_to_github(
        config, payload, "https://md.example.com", client,
        rng=rng, now_sec=1_760_500_000, clock_ms=lambda: 1_760_500_000_123,
    )

    assert recorded["method"] == "PUT"
    assert re.fullmatch(
        r"https://api\.github\.com/repos/bucketio/img[01]/contents/2025/10/15/1760500000123-[0-9a-f-]{36}\.png",
        recorded["url"],
    )
    assert recorded["headers"]["authorization"] in ("token tok-a", "token tok-b")
    assert recorded["headers"]["user-agent"] == "md-api-upload"
    assert recorded["headers"]["accept"] == "application/vnd.github+json"
    assert recorded["body"]["branch"] == "main"
    assert recorded["body"]["message"] == "Upload by https://md.example.com"
    import base64

    assert base64.b64decode(recorded["body"]["content"]) == PNG
    # CDN 改写（仅第一处）
    repo = recorded["url"].split("/repos/bucketio/")[1].split("/")[0]
    assert url == f"https://fastly.jsdelivr.net/gh/bucketio/{repo}@main/2026/10/x.png"


def test_github_no_cdn_returns_download_url():
    client = httpx.Client(transport=httpx.MockTransport(
        lambda r: httpx.Response(200, json={"content": {"download_url": "https://raw.githubusercontent.com/u/r/main/a"}})
    ))
    url = upload_to_github(_gh_config(use_cdn=False), UploadPayload("a", "image/png", b"x"),
                           "ref", client, rng=random.Random(0))
    assert url == "https://raw.githubusercontent.com/u/r/main/a"


@pytest.mark.parametrize(
    "status,payload,match",
    [
        (403, {"message": "Bad credentials"}, "Bad credentials"),
        (500, {"message": "boom"}, "boom"),
        (200, {"content": {}}, "missing download_url"),
        (200, {"content": {"download_url": ""}}, "missing download_url"),
    ],
)
def test_github_failures(status, payload, match):
    client = httpx.Client(transport=httpx.MockTransport(
        lambda r: httpx.Response(status, json=payload)
    ))
    with pytest.raises(RuntimeError, match=match):
        upload_to_github(_gh_config(), UploadPayload("a", "image/png", b"x"),
                         "ref", client, rng=random.Random(0))


def test_github_non_json_error_uses_reason():
    client = httpx.Client(transport=httpx.MockTransport(
        lambda r: httpx.Response(502, text="bad gateway")
    ))
    with pytest.raises(RuntimeError, match="Bad Gateway"):
        upload_to_github(_gh_config(), UploadPayload("a", "image/png", b"x"),
                         "ref", client, rng=random.Random(0))


# ---- S3/R2 后端 ---------------------------------------------------------------


def test_s3_virtual_hosted_put_recording():
    recorded = {}

    def handler(request: httpx.Request) -> httpx.Response:
        recorded["url"] = str(request.url)
        recorded["auth"] = request.headers.get("authorization", "")
        recorded["sha"] = request.headers.get("x-amz-content-sha256", "")
        recorded["date"] = request.headers.get("x-amz-date", "")
        recorded["ct"] = request.headers.get("content-type", "")
        assert request.content == PNG
        return httpx.Response(200)

    backend = S3Backend(
        endpoint="https://abc.r2.cloudflarestorage.com",
        bucket="images",
        access_key_id="AK",
        secret_access_key="SK",
        region="auto",
        public_url="https://img.example.com/",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        clock=lambda: datetime(2026, 10, 15, 8, 30, tzinfo=timezone.utc),
    )
    url = backend.put("2026/10/15/a.png", PNG, "image/png")

    assert recorded["url"] == "https://images.abc.r2.cloudflarestorage.com/2026/10/15/a.png"
    assert url == "https://img.example.com/2026/10/15/a.png"
    assert recorded["auth"].startswith("AWS4-HMAC-SHA256 ")
    assert "/20261015/auto/s3/aws4_request" in recorded["auth"]
    assert recorded["sha"] == __import__("hashlib").sha256(PNG).hexdigest()
    assert recorded["date"] == "20261015T083000Z"
    assert recorded["ct"] == "image/png"


def test_s3_path_style_and_fallback_url():
    hit = {}

    def handler(request: httpx.Request) -> httpx.Response:
        hit["url"] = str(request.url)
        return httpx.Response(200)

    backend = S3Backend(
        endpoint="https://minio.local:9000",
        bucket="bkt",
        access_key_id="AK",
        secret_access_key="SK",
        region="us-east-1",
        force_path_style=True,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    url = backend.put("k$/图.png", b"d", "")
    assert hit["url"] == "https://minio.local:9000/bkt/k%24/%E5%9B%BE.png"
    # 无 public_url 时回退请求 URL
    assert url == hit["url"]


def test_s3_error_raises():
    backend = S3Backend(
        endpoint="https://s3.local", bucket="b", access_key_id="a",
        secret_access_key="s", http_client=httpx.Client(
            transport=httpx.MockTransport(lambda r: httpx.Response(403, text="denied"))
        ),
    )
    with pytest.raises(RuntimeError, match="S3 upload failed: 403"):
        backend.put("k", b"d", "image/png")


def test_s3_invalid_endpoint():
    with pytest.raises(ValueError):
        S3Backend(endpoint="", bucket="b", access_key_id="a", secret_access_key="s")
    with pytest.raises(ValueError):
        S3Backend(endpoint="no-scheme", bucket="b", access_key_id="a", secret_access_key="s")


def test_build_r2_backend_from_config():
    config = Config(
        upload_backend="s3",
        upload_s3_endpoint="https://acct.r2.cloudflarestorage.com",
        upload_s3_bucket="img",
        upload_s3_access_key_id="AK",
        upload_s3_secret_access_key="SK",
        upload_s3_region="auto",
        upload_s3_public_url="https://pub/",
        upload_s3_force_path_style=True,
    )
    backend = build_r2_backend(config)
    assert backend._force_path_style is True
    assert backend._region == "auto"
