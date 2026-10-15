"""TR-13.1 POST /upload 契约矩阵（upstream: apps/api/src/upload.ts）。

门控顺序 404/503/400x3/429 → 三后端成功/失败 → 成功才计数；
匿名 60、free 120、pro 300 每小时；坏/幽灵 Bearer 降级 IP；
CF-Connecting-IP → XFF 首段 → unknown；Referer/Origin/md-api 兜底。
"""

import json
import re
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db, upload_rate
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.security import issue_token

JWT_SECRET = "upload-secret-0123456789-abcdef"
PNG = b"\x89PNG\r\n\x1a\n-binary-content"
MAX_BYTES = 5 * 1024 * 1024


def make_config(tmp_path, **over):
    params = {
        "jwt_secret": JWT_SECRET,
        "upload_backend": "local",
        "storage_local_dir": str(tmp_path / "uploads"),
        "storage_local_base_url": "http://local.test/img/",
    }
    params.update(over)
    return Config(**params)


@pytest.fixture
def ctx(tmp_path, conn):
    db.upsert_user(conn, {
        "id": "free1", "github_id": 1, "login": "freecat",
        "name": "Free", "avatar": None,
    })
    db.upsert_user(conn, {
        "id": "pro1", "github_id": 2, "login": "procat",
        "name": "Pro", "avatar": None,
    })
    future_ms = (int(time.time()) + 365 * 24 * 3600) * 1000
    conn.execute(
        "UPDATE users SET plan = 'pro', plan_expires_at = ? WHERE id = 'pro1'",
        (future_ms,),
    )
    conn.commit()

    config = make_config(tmp_path)

    def build(cfg=None, transport: httpx.BaseTransport | None = None):
        http_client = httpx.Client(transport=transport) if transport else None
        app = create_app(cfg or config, conn=conn, http_client=http_client)
        return TestClient(app)

    client = build()
    free_h = {"Authorization": f"Bearer {issue_token(JWT_SECRET, 'free1', 'freecat', now_s=2_000_000_000)}"}
    pro_h = {"Authorization": f"Bearer {issue_token(JWT_SECRET, 'pro1', 'procat', now_s=2_000_000_000)}"}
    return {
        "conn": conn,
        "tmp": tmp_path,
        "config": config,
        "client": client,
        "build": build,
        "free_h": free_h,
        "pro_h": pro_h,
    }


def post_file(client, *, content=PNG, filename="a.png", ct="image/png",
              field="file", headers=None):
    return client.post(
        "/upload",
        files={field: (filename, content, ct)},
        headers=headers or {},
    )


def seed_count(conn, scope, count):
    for _ in range(count):
        upload_rate.increment_upload_rate_limit(conn, scope)


# ---- 门控 404 / 503 ----------------------------------------------------------


def test_disabled_404(ctx):
    client = ctx["build"](make_config(ctx["tmp"], upload_enabled=False))
    resp = post_file(client)
    assert resp.status_code == 404
    assert resp.json() == {"error": "upload_disabled"}


def test_github_not_configured_503(ctx):
    client = ctx["build"](make_config(
        ctx["tmp"], upload_backend="github", upload_github_tokens=()
    ))
    assert post_file(client).status_code == 503


def test_s3_not_configured_503(ctx):
    client = ctx["build"](make_config(
        ctx["tmp"], upload_backend="s3", upload_s3_bucket="",
        upload_s3_access_key_id="ak", upload_s3_secret_access_key="sk",
    ))
    assert post_file(client).status_code == 503


def test_unknown_backend_falls_back_to_local(ctx):
    # 未知后端枚举兜底 local（零配置本地模式），上传成功
    client = ctx["build"](make_config(ctx["tmp"], upload_backend="mystery"))
    assert post_file(client).status_code == 200


# ---- 表单与文件校验 -----------------------------------------------------------


def test_invalid_form_data_malformed_multipart(ctx):
    # 声明 multipart 但帧体损坏：python-multipart 抛解析错误
    resp = ctx["client"].post(
        "/upload",
        content=b"\x00\x01garbage-not-a-multipart-frame",
        headers={"content-type": "multipart/form-data; boundary=----zz"},
    )
    assert resp.status_code == 400
    assert resp.json() == {"error": "invalid_form_data"}


def test_file_required_wrong_field(ctx):
    resp = ctx["client"].post("/upload", files={"other": ("a.png", PNG, "image/png")})
    assert resp.status_code == 400
    assert resp.json() == {"error": "file_required"}


def test_file_required_urlencoded(ctx):
    resp = ctx["client"].post("/upload", data={"name": "x"})
    assert resp.status_code == 400
    assert resp.json() == {"error": "file_required"}


@pytest.mark.parametrize("ct", ["text/plain", "application/octet-stream", "image", "video/mp4"])
def test_invalid_file_type(ctx, ct):
    assert post_file(ctx["client"], ct=ct).status_code == 400
    assert post_file(ctx["client"], ct=ct).json() == {"error": "invalid_file_type"}


def test_image_prefix_accepted_even_unknown_subtype(ctx):
    resp = post_file(ctx["client"], ct="image/x-made-up")
    assert resp.status_code == 200


def test_empty_file_too_large(ctx):
    resp = post_file(ctx["client"], content=b"")
    assert resp.status_code == 400
    assert resp.json() == {"error": "file_too_large", "maxBytes": MAX_BYTES}


def test_oversized_file_too_large(ctx):
    resp = post_file(ctx["client"], content=b"\x00" * (MAX_BYTES + 1))
    assert resp.status_code == 400
    assert resp.json() == {"error": "file_too_large", "maxBytes": MAX_BYTES}


def test_exactly_max_bytes_accepted(ctx):
    resp = post_file(ctx["client"], content=b"\x00" * MAX_BYTES)
    assert resp.status_code == 200


# ---- local 后端 ---------------------------------------------------------------


def test_local_success_shape_and_on_disk(ctx):
    resp = post_file(ctx["client"], filename="photo.PNG", ct="image/png")
    assert resp.status_code == 200
    url = resp.json()["url"]
    m = re.fullmatch(
        r"http://local\.test/img/\d{4}/\d{2}/\d{2}/\d+-[0-9a-f]{8}-[0-9a-f]{4}-"
        r"[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.png",
        url,
    )
    assert m is not None
    # base_url 尾斜杠不产生双斜杠
    assert "//img/" not in url
    rel = url.removeprefix("http://local.test/img/")
    target = ctx["tmp"] / "uploads" / rel.replace("/", "\\")
    assert target.read_bytes() == PNG


# ---- 限流（匿名 60 / free 120 / pro 300）--------------------------------------


def test_anonymous_limit_60(ctx):
    seed_count(ctx["conn"], "upload:ip:unknown", 59)
    assert post_file(ctx["client"]).status_code == 200  # 第 60 次成功
    resp = post_file(ctx["client"])
    assert resp.status_code == 429
    body = resp.json()
    assert body["error"] == "rate_limit_exceeded"
    assert body["limit"] == 60
    assert body["upgradeRequired"] is False
    assert 1 <= body["retryAfterSec"] <= 3600


def test_free_limit_120_and_upgrade_required(ctx):
    seed_count(ctx["conn"], "upload:user:free1", 120)
    resp = post_file(ctx["client"], headers=ctx["free_h"])
    assert resp.status_code == 429
    assert resp.json()["limit"] == 120
    assert resp.json()["upgradeRequired"] is True


def test_pro_limit_300_no_upgrade_required(ctx):
    seed_count(ctx["conn"], "upload:user:pro1", 300)
    resp = post_file(ctx["client"], headers=ctx["pro_h"])
    assert resp.status_code == 429
    assert resp.json()["limit"] == 300
    assert resp.json()["upgradeRequired"] is False


def test_bad_bearer_falls_back_to_ip_scope(ctx):
    # 用户窗口已满；坏 token 走 IP 窗口（0 计数）→ 成功
    seed_count(ctx["conn"], "upload:user:free1", 120)
    bad = {"Authorization": "Bearer not-a-jwt"}
    assert post_file(ctx["client"], headers=bad).status_code == 200


def test_ghost_user_falls_back_to_ip_scope(ctx):
    ghost = {
        "Authorization": f"Bearer {issue_token(JWT_SECRET, 'ghost', 'g', now_s=2_000_000_000)}"
    }
    assert post_file(ctx["client"], headers=ghost).status_code == 200


def test_cf_connecting_ip_scope(ctx):
    seed_count(ctx["conn"], "upload:ip:1.1.1.1", 60)
    resp = post_file(ctx["client"], headers={"CF-Connecting-IP": "1.1.1.1"})
    assert resp.status_code == 429
    # 不同 IP 不受影响
    assert post_file(ctx["client"], headers={"CF-Connecting-IP": "8.8.8.8"}).status_code == 200


def test_xff_first_hop_scope(ctx):
    seed_count(ctx["conn"], "upload:ip:2.2.2.2", 60)
    resp = post_file(ctx["client"], headers={"X-Forwarded-For": "2.2.2.2, 3.3.3.3"})
    assert resp.status_code == 429
    # CF 头优先于 XFF
    assert post_file(
        ctx["client"],
        headers={"CF-Connecting-IP": "9.9.9.9", "X-Forwarded-For": "2.2.2.2"},
    ).status_code == 200


def test_failed_upload_does_not_increment(ctx):
    # github 后端必然 502：计数前不应出现 upload:ip:unknown 行
    config = make_config(
        ctx["tmp"],
        upload_backend="github",
        upload_github_tokens=("tok",),
        upload_github_repo_list=("repo",),
        upload_github_username="user",
    )
    transport = httpx.MockTransport(lambda r: httpx.Response(500, json={"message": "boom"}))
    client = ctx["build"](config, transport)
    assert post_file(client).status_code == 502
    row = ctx["conn"].execute(
        "SELECT COUNT(*) FROM share_rate_limits WHERE scope_key = ?",
        ("upload:ip:unknown",),
    ).fetchone()
    assert row[0] == 0


# ---- GitHub 后端 ---------------------------------------------------------------


def _github_config(tmp_path, use_cdn=True):
    return make_config(
        tmp_path,
        upload_backend="github",
        upload_github_tokens=("tok",),
        upload_github_repo_list=("myrepo",),
        upload_github_username="myuser",
        upload_github_use_cdn=use_cdn,
    )


@pytest.mark.parametrize(
    "referer_headers,expected_message",
    [
        ({"Referer": "https://md.doocs.org/"}, "Upload by https://md.doocs.org/"),
        ({"Origin": "https://md.doocs.org"}, "Upload by https://md.doocs.org"),
        ({}, "Upload by md-api"),
    ],
)
def test_github_success_cdn_and_referer(ctx, referer_headers, expected_message):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        seen["auth"] = request.headers.get("authorization", "")
        return httpx.Response(
            200,
            json={"content": {"download_url":
                "https://raw.githubusercontent.com/myuser/myrepo/main/dir/a.png"}},
        )

    client = ctx["build"](_github_config(ctx["tmp"]), httpx.MockTransport(handler))
    resp = post_file(client, headers=referer_headers)
    assert resp.status_code == 200
    assert seen["url"].startswith(
        "https://api.github.com/repos/myuser/myrepo/contents/"
    )
    assert seen["auth"] == "token tok"
    assert seen["body"]["message"] == expected_message
    assert resp.json()["url"] == (
        "https://fastly.jsdelivr.net/gh/myuser/myrepo@main/dir/a.png"
    )


def test_github_no_cdn_returns_download_url(ctx):
    transport = httpx.MockTransport(
        lambda r: httpx.Response(
            200,
            json={"content": {"download_url":
                "https://raw.githubusercontent.com/myuser/myrepo/main/a"}},
        )
    )
    client = ctx["build"](_github_config(ctx["tmp"], use_cdn=False), transport)
    resp = post_file(client)
    assert resp.status_code == 200
    assert resp.json()["url"] == "https://raw.githubusercontent.com/myuser/myrepo/main/a"


def test_github_failure_502(ctx):
    transport = httpx.MockTransport(
        lambda r: httpx.Response(403, json={"message": "Bad credentials"})
    )
    client = ctx["build"](_github_config(ctx["tmp"]), transport)
    resp = post_file(client)
    assert resp.status_code == 502
    body = resp.json()
    assert body["error"] == "upload_failed"
    assert "Bad credentials" in body["message"]


# ---- S3/R2 后端 ---------------------------------------------------------------


def _s3_config(tmp_path, **over):
    params = {
        "upload_backend": "s3",
        "upload_s3_endpoint": "https://acct.r2.cloudflarestorage.com",
        "upload_s3_bucket": "img",
        "upload_s3_access_key_id": "AK",
        "upload_s3_secret_access_key": "SK",
        "upload_s3_region": "auto",
        "upload_s3_public_url": "https://cdn.example.com",
    }
    params.update(over)
    return make_config(tmp_path, **params)


def test_s3_success_signed_put_and_public_url(ctx):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization", "")
        seen["date"] = request.headers.get("x-amz-date", "")
        seen["sha"] = request.headers.get("x-amz-content-sha256", "")
        return httpx.Response(200)

    client = ctx["build"](_s3_config(ctx["tmp"]), httpx.MockTransport(handler))
    resp = post_file(client)
    assert resp.status_code == 200
    assert seen["url"].startswith("https://img.acct.r2.cloudflarestorage.com/")
    assert seen["auth"].startswith("AWS4-HMAC-SHA256 ")
    assert "/auto/s3/aws4_request" in seen["auth"]
    assert re.fullmatch(r"\d{8}T\d{6}Z", seen["date"])
    assert len(seen["sha"]) == 64
    assert resp.json()["url"].startswith("https://cdn.example.com/")


def test_s3_failure_502(ctx):
    transport = httpx.MockTransport(lambda r: httpx.Response(403, text="denied"))
    client = ctx["build"](_s3_config(ctx["tmp"]), transport)
    resp = post_file(client)
    assert resp.status_code == 502
    assert resp.json()["error"] == "upload_failed"
