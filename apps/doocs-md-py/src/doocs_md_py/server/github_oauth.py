"""GitHub OAuth 两段 HTTP 交互（upstream: apps/api/src/auth.ts:73-124）。

全部函数显式接收 httpx.Client，测试通过 MockTransport 注入，不产生真实网络。
"""

import httpx

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


def build_authorize_url(client_id: str, redirect_uri: str, state: str) -> str:
    """upstream: auth.ts:73-78；scope 固定 read:user。"""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "read:user",
        "state": state,
    }
    return _with_query(GITHUB_AUTHORIZE_URL, params)


def _with_query(url: str, params: dict[str, str]) -> str:
    request = httpx.Request("GET", url, params=params)
    return str(request.url)


def exchange_code_for_token(
    client: httpx.Client,
    *,
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
) -> str | None:
    """upstream: auth.ts:98-111；返回 access_token，缺失/失败返回 None。"""
    response = client.post(
        GITHUB_TOKEN_URL,
        # upstream: auth.ts:100 Accept + Content-Type 均 application/json
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        },
    )
    data = response.json()
    token = data.get("access_token") if isinstance(data, dict) else None
    return token if isinstance(token, str) and token else None


def fetch_github_user(client: httpx.Client, access_token: str) -> tuple[bool, dict]:
    """upstream: auth.ts:114-124。

    返回 (ok, payload)：非 2xx 时 ok=False；GitHub API 必须携带 UA，
    Accept 使用其推荐的 vendor 类型。
    """
    response = client.get(
        GITHUB_USER_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "md-api",
            "Accept": "application/vnd.github+json",
        },
    )
    if not response.is_success:
        return False, {}
    payload = response.json()
    return True, payload if isinstance(payload, dict) else {}
