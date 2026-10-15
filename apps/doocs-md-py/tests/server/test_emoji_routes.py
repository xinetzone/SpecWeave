"""TR-16.1 之三：/emojis 路由端到端（upstream: emojis.test.ts + emojis.ts 全分支）。

覆盖：五端点鉴权、默认/个人 manifest、magic bytes 伪造拦截、第 101 项 409 且
对象回滚、缓存头（system immutable / user max-age=300）、ETag/nosniff、单项与
整包删除级联清理对象、存储故障 502/500 映射。
"""

import pytest
from fastapi.testclient import TestClient

from doocs_md_py.server import db
from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.security import issue_token

SECRET = "emoji-secret-0123456789-abcdef-ghijklmn"

PNG = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)) + b"\x00" * 8
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 8
GIF = b"GIF89a" + b"\x00" * 4
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 4


@pytest.fixture
def ctx(conn, tmp_path):
    db.upsert_user(conn, {
        "id": "u1", "github_id": 1, "login": "octocat",
        "name": "Octo", "avatar": None,
    })
    asset_dir = tmp_path / "emoji"
    config = Config(jwt_secret=SECRET, emoji_local_dir=str(asset_dir))
    app = create_app(config, conn=conn)
    client = TestClient(app)
    headers = {
        "Authorization": f"Bearer {issue_token(SECRET, 'u1', 'octocat', now_s=2_000_000_000)}"
    }
    return {"client": client, "app": app, "conn": conn, "h1": headers, "asset_dir": asset_dir}


def _upload(client, headers, *, data_bytes=PNG, mime="image/png", name="smile.png",
            field_name="name", form_name=None):
    files = {"file": (name, data_bytes, mime)}
    data = {field_name: form_name} if form_name is not None else None
    return client.post("/emojis/me/items", headers=headers, files=files, data=data)


# ---- 鉴权（upstream emojis.test.ts:49-59 同矩阵）----


@pytest.mark.parametrize(("method", "path"), [
    ("GET", "/emojis/me"),
    ("PATCH", "/emojis/me"),
    ("POST", "/emojis/me/items"),
    ("DELETE", "/emojis/me/items/item-id"),
    ("DELETE", "/emojis/me"),
])
def test_auth_required(ctx, method, path):
    resp = ctx["client"].request(method, path)
    assert resp.status_code == 401
    assert resp.json() == {"error": "unauthorized"}


# ---- manifest ----


def test_default_manifest_shape(ctx):
    resp = ctx["client"].get("/emojis/default")
    assert resp.status_code == 200
    body = resp.json()
    assert body["slug"] == "default"
    assert body["kind"] == "system"
    assert set(body["metadata"]) == {
        "sourceUrl", "sourceCommit", "license", "licenseUrl", "attribution", "description",
    }
    assert body["items"] == []


def test_get_me_creates_pack_and_manifest(ctx):
    resp = ctx["client"].get("/emojis/me", headers=ctx["h1"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["kind"] == "user"
    assert body["slug"] == "user-u1"
    assert body["name"] == "My Emojis"
    assert body["items"] == []


def test_pack_rename_validation(ctx):
    bad = ctx["client"].patch("/emojis/me", headers=ctx["h1"], json={"name": "  "})
    assert bad.status_code == 400 and bad.json() == {"error": "invalid_name"}
    ok = ctx["client"].patch("/emojis/me", headers=ctx["h1"], json={"name": "Funny Pack"})
    assert ok.status_code == 200 and ok.json()["name"] == "Funny Pack"


def test_pack_rename_bad_json(ctx):
    resp = ctx["client"].patch(
        "/emojis/me",
        headers={**ctx["h1"], "Content-Type": "application/json"},
        content=b"{broken",
    )
    assert resp.status_code == 400 and resp.json() == {"error": "invalid_name"}


# ---- 上传校验 ----


def test_upload_success_manifest_and_object(ctx):
    resp = _upload(ctx["client"], ctx["h1"], form_name="folder\\ happy\x00 face.png")
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["name"] == "happy face"
    assert item["mime"] == "image/png"
    assert item["size"] == len(PNG)
    assert item["sortOrder"] == 0
    assert item["width"] is None and item["height"] is None
    assert item["url"] == f"http://testserver/emojis/assets/{item['id']}"
    # 对象文件落盘
    files = list(ctx["asset_dir"].rglob("*.png"))
    assert len(files) == 1


@pytest.mark.parametrize(("mime", "data"), [
    ("image/png", JPEG),
    ("image/jpeg", PNG),
    ("image/gif", b"GIF99a\x00\x00"),
    ("image/webp", b"RIFF\x00\x00\x00\x00XXXX"),
])
def test_upload_rejects_forged_magic_bytes(ctx, mime, data):
    resp = _upload(ctx["client"], ctx["h1"], data_bytes=data, mime=mime)
    assert resp.status_code == 400
    assert resp.json() == {"error": "mime_mismatch"}
    # 校验在写对象之前，物理目录无任何文件
    assert list(ctx["asset_dir"].rglob("*")) == [] or all(
        p.is_dir() for p in ctx["asset_dir"].rglob("*")
    )


@pytest.mark.parametrize(("mime", "data"), [
    ("image/gif", GIF),
    ("image/webp", WEBP),
    ("image/jpeg", JPEG),
])
def test_upload_accepts_all_four_types(ctx, mime, data):
    resp = _upload(ctx["client"], ctx["h1"], data_bytes=data, mime=mime, name="x.bin")
    assert resp.status_code == 201
    assert resp.json()["items"][-1]["mime"] == mime


def test_upload_invalid_mime_type(ctx):
    resp = _upload(ctx["client"], ctx["h1"], data_bytes=b"<svg/>", mime="image/svg+xml")
    assert resp.status_code == 400
    assert resp.json() == {"error": "invalid_file_type"}


def test_upload_requires_file(ctx):
    resp = ctx["client"].post(
        "/emojis/me/items", headers=ctx["h1"], data={"name": "x"},
    )
    assert resp.status_code == 400 and resp.json()["error"] == "file_required"


def test_upload_empty_file(ctx):
    resp = _upload(ctx["client"], ctx["h1"], data_bytes=b"", mime="image/png")
    assert resp.status_code == 400 and resp.json()["error"] == "empty_file"


def test_upload_too_large(ctx):
    big = b"\x00" * (5 * 1024 * 1024 + 1)
    resp = _upload(ctx["client"], ctx["h1"], data_bytes=big, mime="image/png")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] == "file_too_large"
    assert body["maxBytes"] == 5 * 1024 * 1024


def test_upload_invalid_form_data(ctx):
    resp = ctx["client"].post(
        "/emojis/me/items",
        headers={**ctx["h1"], "Content-Type": "multipart/form-data; boundary=xxx"},
        content=b"this is not multipart at all",
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "invalid_form_data"


def test_upload_name_falls_back_to_filename(ctx):
    resp = _upload(ctx["client"], ctx["h1"], name="photo.jpeg", mime="image/jpeg",
                   data_bytes=JPEG)
    assert resp.status_code == 201
    assert resp.json()["items"][0]["name"] == "photo"


# ---- 第 101 项上限与对象回滚 ----


def test_item_limit_101st_conflict_and_object_rollback(ctx):
    for i in range(100):
        resp = _upload(ctx["client"], ctx["h1"], name=f"e{i}.png")
        assert resp.status_code == 201
        assert len(resp.json()["items"]) == i + 1

    # 第 101 个：先写对象，条件 INSERT 0 行后回滚
    resp = _upload(ctx["client"], ctx["h1"], name="overflow.png")
    assert resp.status_code == 409
    body = resp.json()
    assert body == {"error": "item_limit_reached", "limit": 100}

    pack_row = ctx["conn"].execute(
        "SELECT id FROM emoji_packs WHERE owner_user_id = 'u1'"
    ).fetchone()
    count = ctx["conn"].execute(
        "SELECT COUNT(*) AS c FROM emoji_items WHERE pack_id = ?", (pack_row["id"],)
    ).fetchone()["c"]
    assert count == 100
    # 物理对象恰好 100 个（第 101 个已回滚删除）
    assert len(list(ctx["asset_dir"].rglob("*.png"))) == 100


# ---- 资产下载与缓存头 ----


def test_user_asset_cache_headers(ctx):
    uploaded = _upload(ctx["client"], ctx["h1"]).json()
    item_id = uploaded["items"][0]["id"]
    resp = ctx["client"].get(f"/emojis/assets/{item_id}")
    assert resp.status_code == 200
    assert resp.content == PNG
    assert resp.headers["Content-Type"] == "image/png"
    assert resp.headers["Content-Length"] == str(len(PNG))
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["Cache-Control"] == "public, max-age=300"
    assert resp.headers["ETag"].startswith('"') and resp.headers["ETag"].endswith('"')


def test_system_asset_immutable_cache(ctx):
    # 直插系统项与对象文件（0008 仅种子 pack，不带 items）
    ctx["conn"].execute(
        "INSERT INTO emoji_items (id, pack_id, object_key, name, mime, size,"
        " sort_order, created_at, updated_at) VALUES"
        " ('sys1', 'system-default', 'system/sys1.png', 'sys', 'image/png', ?, 0, 1, 1)",
        (len(PNG),),
    )
    sys_dir = ctx["asset_dir"] / "system"
    sys_dir.mkdir(parents=True, exist_ok=True)
    (sys_dir / "sys1.png").write_bytes(PNG)

    resp = ctx["client"].get("/emojis/assets/sys1")
    assert resp.status_code == 200
    assert resp.headers["Cache-Control"] == "public, max-age=31536000, immutable"
    assert resp.headers["X-Content-Type-Options"] == "nosniff"


def test_asset_404_for_missing_item_and_missing_object(ctx):
    assert ctx["client"].get("/emojis/assets/no-such-id").status_code == 404
    # DB 有行但对象缺失同样 404（对象存储最终事实）
    uploaded = _upload(ctx["client"], ctx["h1"]).json()
    item_id = uploaded["items"][0]["id"]
    for path in ctx["asset_dir"].rglob("*.png"):
        path.unlink()
    assert ctx["client"].get(f"/emojis/assets/{item_id}").status_code == 404


# ---- 单项删除 ----


def test_delete_item_removes_object_and_row(ctx):
    uploaded = _upload(ctx["client"], ctx["h1"]).json()
    item_id = uploaded["items"][0]["id"]
    assert len(list(ctx["asset_dir"].rglob("*.png"))) == 1

    missing = ctx["client"].delete("/emojis/me/items/ghost", headers=ctx["h1"])
    assert missing.status_code == 404

    resp = ctx["client"].delete(f"/emojis/me/items/{item_id}", headers=ctx["h1"])
    assert resp.status_code == 200
    assert resp.json()["items"] == []
    assert list(ctx["asset_dir"].rglob("*.png")) == []
    # 再删一次 404
    assert ctx["client"].delete(f"/emojis/me/items/{item_id}", headers=ctx["h1"]).status_code == 404


# ---- 整包删除（级联）----


def test_delete_pack_cascades_objects_and_rows(ctx):
    _upload(ctx["client"], ctx["h1"], name="a.png")
    _upload(ctx["client"], ctx["h1"], name="b.png")
    assert len(list(ctx["asset_dir"].rglob("*.png"))) == 2

    resp = ctx["client"].delete("/emojis/me", headers=ctx["h1"])
    assert resp.status_code == 200 and resp.json() == {"ok": True}

    assert list(ctx["asset_dir"].rglob("*.png")) == []
    assert ctx["conn"].execute(
        "SELECT COUNT(*) AS c FROM emoji_items"
    ).fetchone()["c"] == 0
    assert ctx["conn"].execute(
        "SELECT COUNT(*) AS c FROM emoji_packs WHERE owner_user_id = 'u1'"
    ).fetchone()["c"] == 0
    # 再开包为空包（slug 复用）
    manifest = ctx["client"].get("/emojis/me", headers=ctx["h1"]).json()
    assert manifest["items"] == []


# ---- 存储故障 ----


class _BoomStorage:
    def __init__(self, method):
        self.method = method

    def put(self, *args, **kwargs):
        raise RuntimeError("storage down")

    def get(self, *args, **kwargs):
        if self.method == "get":
            raise RuntimeError("storage down")
        raise AssertionError("unexpected get")

    def delete(self, *args, **kwargs):
        raise RuntimeError("storage down")


def test_asset_put_failure_returns_502(ctx):
    ctx["app"].state.emoji_storage = _BoomStorage("put")
    resp = _upload(ctx["client"], ctx["h1"])
    assert resp.status_code == 502
    assert resp.json() == {"error": "asset_upload_failed"}


def test_asset_delete_failure_returns_502(ctx):
    _upload(ctx["client"], ctx["h1"])
    ctx["app"].state.emoji_storage = _BoomStorage("delete")
    manifest = ctx["client"].get("/emojis/me", headers=ctx["h1"]).json()
    item_id = manifest["items"][0]["id"]
    resp = ctx["client"].delete(f"/emojis/me/items/{item_id}", headers=ctx["h1"])
    assert resp.status_code == 502
    assert resp.json() == {"error": "asset_delete_failed"}
    # DB 行仍在（先删对象后删行）
    assert ctx["conn"].execute(
        "SELECT COUNT(*) AS c FROM emoji_items WHERE id = ?", (item_id,)
    ).fetchone()["c"] == 1


def test_pack_delete_asset_failure_returns_502(ctx):
    _upload(ctx["client"], ctx["h1"])
    ctx["app"].state.emoji_storage = _BoomStorage("delete")
    resp = ctx["client"].delete("/emojis/me", headers=ctx["h1"])
    assert resp.status_code == 502
    assert resp.json() == {"error": "asset_delete_failed"}
