"""app factory 健康检查与缺省配置（TR-4.2）。"""

from fastapi.testclient import TestClient

from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.httputil import client_ip, error_response


def test_health_endpoint():
    client = TestClient(create_app(Config()))
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"name": "md-api", "ok": True}


def test_default_config_flags():
    cfg = Config()
    # 云端凭证缺省：OAuth/JWT/爱发电均未配置
    assert cfg.is_oauth_configured() is False
    assert cfg.is_jwt_configured() is False
    assert cfg.is_afdian_configured() is False
    # 本地模式：上传零配置可用
    assert cfg.upload_backend == "local"
    assert cfg.upload_backend_ready() is True
    assert cfg.upload_max_bytes == 5 * 1024 * 1024
    # 默认 20 个 img 仓库与 CDN 开关（upload-config.ts 默认值）
    assert cfg.upload_github_username == "bucketio"
    assert cfg.upload_github_repo_list == tuple(f"img{i}" for i in range(20))
    assert cfg.upload_github_branch == "main"
    assert cfg.upload_github_use_cdn is True


def test_admin_login_case_insensitive():
    cfg = Config(admin_github_logins=("OctoCat",))
    assert cfg.is_admin_login("octocat") is True
    assert cfg.is_admin_login("OCTOCAT") is True
    assert cfg.is_admin_login("someone") is False
    assert cfg.is_admin_login(None) is False


def test_github_and_s3_ready_gates():
    assert Config(upload_backend="github").github_upload_ready() is False
    assert (
        Config(upload_backend="github", upload_github_tokens=("ghp_x",)).github_upload_ready()
        is True
    )
    s3 = Config(
        upload_backend="s3",
        upload_s3_bucket="b",
        upload_s3_access_key_id="ak",
        upload_s3_secret_access_key="sk",
    )
    assert s3.s3_upload_ready() is True
    assert s3.upload_backend_ready() is True
    assert Config(upload_backend="s3", upload_s3_bucket="b").s3_upload_ready() is False


def test_from_env_overrides(monkeypatch):
    monkeypatch.setenv("APP_URL", "https://a.example.com, https://b.example.com")
    monkeypatch.setenv("JWT_SECRET", "topsecret")
    monkeypatch.setenv("UPLOAD_BACKEND", "s3")
    monkeypatch.setenv("UPLOAD_GITHUB_REPO_LIST", "r1,r2")
    monkeypatch.setenv("UPLOAD_GITHUB_USE_CDN", "false")
    cfg = Config.from_env()
    assert cfg.app_url == "https://a.example.com, https://b.example.com"
    assert cfg.is_jwt_configured() is True
    assert cfg.upload_backend == "s3"
    assert cfg.upload_github_repo_list == ("r1", "r2")
    assert cfg.upload_github_use_cdn is False


def test_error_response_shape():
    resp = error_response(401, "Unauthorized")
    assert resp.status_code == 401
    import json

    assert json.loads(resp.body) == {"error": "Unauthorized"}


def test_client_ip_prefers_forwarded_for():
    from types import SimpleNamespace

    request = SimpleNamespace(
        headers={"x-forwarded-for": "203.0.113.5, 10.0.0.1"},
        client=SimpleNamespace(host="10.0.0.1"),
    )
    assert client_ip(request) == "203.0.113.5"

    request_no_xff = SimpleNamespace(headers={}, client=SimpleNamespace(host="10.0.0.2"))
    assert client_ip(request_no_xff) == "10.0.0.2"
