"""TR-10.1 GitHub OAuth 全路由 + /me（upstream: apps/api/src/auth.ts）。

外部 HTTP 全部经 httpx.MockTransport 注入；断言重定向、cookie 属性、
换 token 请求要素、错误分支 hash 与 upsert 行为。
"""

import json
from urllib.parse import parse_qs, urlsplit

import httpx
from fastapi.testclient import TestClient

from doocs_md_py.server.app import create_app
from doocs_md_py.server.config import Config
from doocs_md_py.server.security import issue_token, verify_token

JWT_SECRET = "jwt-secret-0123456789-abcdef-ghijkl"


class GithubMock:
    """记录请求并按开关返回 token/user 响应。"""

    def __init__(self, *, token_ok=True, user_ok=True) -> None:
        self.token_ok = token_ok
        self.user_ok = user_ok
        self.token_request: httpx.Request | None = None
        self.user_request: httpx.Request | None = None

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/login/oauth/access_token":
            self.token_request = request
            if not self.token_ok:
                return httpx.Response(200, json={"error": "bad_verification_code"})
            return httpx.Response(200, json={"access_token": "gho_test_token"})
        if request.url.path == "/user":
            self.user_request = request
            if not self.user_ok:
                return httpx.Response(401, json={"message": "Requires authentication"})
            return httpx.Response(
                200,
                json={
                    "id": 999,
                    "login": "octocat",
                    "name": "The Octocat",
                    "avatar_url": "https://avatars.example.com/o.png",
                },
            )
        return httpx.Response(404, json={"message": "unexpected " + request.url.path})


def make_client(conn, *, mock=None, https=False, app_url="http://editor.test", admins=()):
    cfg = Config(
        app_url=app_url,
        jwt_secret=JWT_SECRET,
        github_client_id="cid-123",
        github_client_secret="secret-xyz",  # mock github oauth fixture
        admin_github_logins=admins,
    )
    http_client = httpx.Client(transport=httpx.MockTransport(mock.handler)) if mock else None
    app = create_app(cfg, conn=conn, http_client=http_client)
    base = "https://testserver" if https else "http://testserver"
    return TestClient(app, base_url=base)


def _set_cookie(client: TestClient, name: str, value: str) -> None:
    # 不带 domain：httpx cookiejar 对 testserver 这类无点域名的显式 domain
    # cookie 不会回发；domain="" 时按请求 host 匹配
    client.cookies.set(name, value)


def _fragment(resp) -> dict:
    return {k: v[0] for k, v in parse_qs(urlsplit(resp.headers["location"]).fragment).items()}


# ---- GET /auth/github（upstream: auth.ts:56-79）----


def test_authorize_redirect_and_cookies(conn):
    mock = GithubMock()
    client = make_client(conn, mock=mock)
    resp = client.get("/auth/github", params={"redirect": "http://editor.test/editor?x=1"},
                      follow_redirects=False)
    assert resp.status_code == 302
    target = urlsplit(resp.headers["location"])
    assert target.scheme == "https"
    assert target.netloc == "github.com"
    assert target.path == "/login/oauth/authorize"
    query = parse_qs(target.query)
    assert query["client_id"] == ["cid-123"]
    assert query["scope"] == ["read:user"]
    assert query["redirect_uri"] == ["http://testserver/auth/github/callback"]
    state = query["state"][0]

    cookies = {c.split("=", 1)[0]: c for c in resp.headers.get_list("set-cookie")}
    state_cookie = cookies["md_oauth_state"]
    assert state in state_cookie
    for attr in ("HttpOnly", "SameSite=Lax", "Path=/", "Max-Age=600"):
        assert attr in state_cookie
    assert "Secure" not in state_cookie
    # 校验通过的回跳地址原样保留（含 path/query；hono/Starlette 均不做百分号编码）
    assert 'md_oauth_redirect="http://editor.test/editor?x=1"' in cookies["md_oauth_redirect"]


def test_authorize_invalid_redirect_falls_back(conn):
    mock = GithubMock()
    client = make_client(conn, mock=mock)
    resp = client.get("/auth/github", params={"redirect": "http://evil.example/x"},
                      follow_redirects=False)
    cookies = {c.split("=", 1)[0]: c for c in resp.headers.get_list("set-cookie")}
    assert 'md_oauth_redirect="http://editor.test"' in cookies["md_oauth_redirect"]
    assert "evil" not in cookies["md_oauth_redirect"]


def test_authorize_secure_cookie_on_https(conn):
    mock = GithubMock()
    client = make_client(conn, mock=mock, https=True)
    resp = client.get("/auth/github", follow_redirects=False)
    query = parse_qs(urlsplit(resp.headers["location"]).query)
    assert query["redirect_uri"] == ["https://testserver/auth/github/callback"]
    for raw in resp.headers.get_list("set-cookie"):
        if raw.startswith("md_oauth_state"):
            assert "Secure" in raw


# ---- GET /auth/github/callback（upstream: auth.ts:82-144）----


def test_callback_oauth_error_branch_clears_cookies(conn):
    client = make_client(conn, mock=GithubMock())
    _set_cookie(client, "md_oauth_state", "s1")
    _set_cookie(client, "md_oauth_redirect", "http://editor.test")
    resp = client.get(
        "/auth/github/callback",
        params={"error": "access_denied"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert _fragment(resp) == {"oauth_error": "access_denied"}
    joined = " ".join(resp.headers.get_list("set-cookie"))
    assert "md_oauth_state" in joined and "Max-Age=0" in joined
    assert "md_oauth_redirect" in joined


def test_callback_missing_code(conn):
    client = make_client(conn, mock=GithubMock())
    _set_cookie(client, "md_oauth_state", "s1")
    resp = client.get(
        "/auth/github/callback", params={"state": "s1"}, follow_redirects=False
    )
    assert _fragment(resp) == {"oauth_error": "invalid_oauth_state"}


def test_callback_state_mismatch(conn):
    client = make_client(conn, mock=GithubMock())
    _set_cookie(client, "md_oauth_state", "s1")
    resp = client.get(
        "/auth/github/callback",
        params={"code": "c", "state": "s2"},
        follow_redirects=False,
    )
    assert _fragment(resp) == {"oauth_error": "invalid_oauth_state"}


def test_callback_exchange_failed(conn):
    mock = GithubMock(token_ok=False)
    client = make_client(conn, mock=mock)
    _set_cookie(client, "md_oauth_state", "s1")
    resp = client.get(
        "/auth/github/callback",
        params={"code": "bad-code", "state": "s1"},
        follow_redirects=False,
    )
    assert _fragment(resp) == {"oauth_error": "oauth_exchange_failed"}

    request = mock.token_request
    assert request is not None
    assert request.method == "POST"
    assert request.url.host == "github.com"
    assert request.headers["accept"] == "application/json"
    assert request.headers["content-type"] == "application/json"
    body = json.loads(request.content)
    assert body == {
        "client_id": "cid-123",
        "client_secret": "secret-xyz",
        "code": "bad-code",
        "redirect_uri": "http://testserver/auth/github/callback",
    }


def test_callback_user_fetch_failed(conn):
    mock = GithubMock(user_ok=False)
    client = make_client(conn, mock=mock)
    _set_cookie(client, "md_oauth_state", "s1")
    resp = client.get(
        "/auth/github/callback",
        params={"code": "c", "state": "s1"},
        follow_redirects=False,
    )
    assert _fragment(resp) == {"oauth_error": "github_user_fetch_failed"}
    request = mock.user_request
    assert request is not None
    assert request.headers["user-agent"] == "md-api"
    assert request.headers["accept"] == "application/vnd.github+json"
    assert request.headers["authorization"] == "Bearer gho_test_token"


def test_callback_success_issues_token_and_upserts(conn):
    mock = GithubMock()
    client = make_client(conn, mock=mock)
    _set_cookie(client, "md_oauth_state", "s1")
    _set_cookie(client, "md_oauth_redirect", "http://editor.test")
    resp = client.get(
        "/auth/github/callback",
        params={"code": "good-code", "state": "s1"},
        follow_redirects=False,
    )
    fragment = _fragment(resp)
    assert set(fragment) == {"account_token"}
    payload = verify_token(JWT_SECRET, fragment["account_token"])
    user_id = payload["sub"]
    assert payload["login"] == "octocat"

    row = conn.execute(
        "SELECT id, github_id, login, name, avatar FROM users WHERE github_id = 999"
    ).fetchone()
    assert row is not None
    assert row["id"] == user_id
    assert row["login"] == "octocat"
    assert row["name"] == "The Octocat"
    assert row["avatar"] == "https://avatars.example.com/o.png"
    # 回到前端编辑器
    assert urlsplit(resp.headers["location"]).netloc == "editor.test"


def test_callback_repeat_login_keeps_same_user_id(conn):
    client = make_client(conn, mock=GithubMock())
    _set_cookie(client, "md_oauth_state", "s1")
    first = client.get(
        "/auth/github/callback",
        params={"code": "c1", "state": "s1"},
        follow_redirects=False,
    )
    first_id = verify_token(JWT_SECRET, _fragment(first)["account_token"])["sub"]

    # GitHub 资料更新（改名/头像），仍是同一内部用户
    class ChangedMock(GithubMock):
        def handler(self, request):  # noqa: ANN001
            if request.url.path == "/user":
                self.user_request = request
                return httpx.Response(
                    200,
                    json={
                        "id": 999,
                        "login": "octocat",
                        "name": "New Name",
                        "avatar_url": None,
                    },
                )
            return super().handler(request)

    client2 = make_client(conn, mock=ChangedMock())
    _set_cookie(client2, "md_oauth_state", "s2")
    second = client2.get(
        "/auth/github/callback",
        params={"code": "c2", "state": "s2"},
        follow_redirects=False,
    )
    second_id = verify_token(JWT_SECRET, _fragment(second)["account_token"])["sub"]
    assert first_id == second_id
    count = conn.execute("SELECT COUNT(*) AS c FROM users WHERE github_id = 999").fetchone()["c"]
    assert count == 1
    row = conn.execute("SELECT name, avatar FROM users WHERE id = ?", (first_id,)).fetchone()
    assert row["name"] == "New Name"
    assert row["avatar"] is None


# ---- GET /me（upstream: auth.ts:146-160）----


def test_me_requires_bearer(conn):
    client = make_client(conn, mock=GithubMock())
    assert client.get("/me").status_code == 401
    assert client.get("/me").json() == {"error": "unauthorized"}

    resp = client.get("/me", headers={"Authorization": "Bearer nonsense"})
    assert resp.status_code == 401
    assert resp.json() == {"error": "invalid_token"}


def test_me_valid_token_but_user_missing(conn):
    client = make_client(conn, mock=GithubMock())
    token = issue_token(JWT_SECRET, "ghost", "ghost", now_s=2_000_000_000 - 100)
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404
    assert resp.json() == {"error": "not_found"}


def test_me_success_free_plan(conn, user_id):
    client = make_client(conn, mock=GithubMock())
    token = issue_token(JWT_SECRET, user_id, "octocat", now_s=2_000_000_000 - 100)
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {
        "id": "user-001",
        "login": "octocat",
        "name": "The Octocat",
        "avatar": "https://example.com/a.png",
        "plan": "free",
        "planExpiresAt": None,
        "isAdmin": False,
    }


def test_me_pro_plan_and_admin(conn, user_id):
    future_ms = 4_000_000_000_000
    conn.execute(
        "UPDATE users SET plan = 'pro', plan_expires_at = ? WHERE id = ?",
        (future_ms, user_id),
    )
    conn.commit()
    client = make_client(conn, mock=GithubMock(), admins=("OctoCat",))
    token = issue_token(JWT_SECRET, user_id, "octocat", now_s=2_000_000_000 - 100)
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    body = resp.json()
    assert body["plan"] == "pro"
    assert body["planExpiresAt"] == future_ms
    assert body["isAdmin"] is True


def test_me_expired_pro_falls_back_to_free(conn, user_id):
    conn.execute(
        "UPDATE users SET plan = 'pro', plan_expires_at = ? WHERE id = ?",
        (1_000, user_id),
    )
    conn.commit()
    client = make_client(conn, mock=GithubMock())
    token = issue_token(JWT_SECRET, user_id, "octocat", now_s=2_000_000_000 - 100)
    body = client.get("/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert body["plan"] == "free"
