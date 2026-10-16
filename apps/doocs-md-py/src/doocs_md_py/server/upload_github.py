"""GitHub Contents API 图床（upstream: apps/api/src/upload-github.ts 1:1）。

随机选 token 与仓库 → PUT /repos/<user>/<repo>/contents/<path>（base64 内容、
``Upload by <referer>`` 提交信息）→ download_url；开启 CDN 时把
``raw.githubusercontent.com/<u>/<r>/<branch>/`` 改写为
``fastly.jsdelivr.net/gh/<u>/<r>@<branch>/``。
"""

import base64
import random
from collections.abc import Callable
from dataclasses import dataclass

import httpx

from .upload_config import GithubUploadConfig
from .upload_filename import build_dated_object_key, dated_directory


@dataclass(slots=True)
class UploadPayload:
    """路由解析后的上传文件（等价 Hono ``File`` 用到的 name/type/arrayBuffer）。"""

    name: str
    content_type: str
    content: bytes


def pick_random(items, rng: random.Random | None = None):
    """upstream: upload-github.ts:22-24。"""
    r = rng or random
    return items[r.randrange(len(items))]


def _raise_for_github_error(response: httpx.Response) -> None:
    detail = response.reason_phrase
    try:
        body = response.json()
    except ValueError:
        body = None
    if isinstance(body, dict) and isinstance(body.get("message"), str):
        detail = body["message"]
    raise RuntimeError(f"GitHub upload failed: {detail}")


def upload_to_github(
    config: GithubUploadConfig,
    file: UploadPayload,
    referer: str,
    http_client: httpx.Client,
    *,
    rng: random.Random | None = None,
    now_sec: float | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    """upstream: upload-github.ts:26-79。"""
    username = config.username
    repo = pick_random(config.repo_list, rng)
    branch = config.branch
    access_token = pick_random(config.tokens, rng)
    directory = dated_directory(now_sec)
    date_filename = build_dated_object_key(
        file.name, file.content_type, clock=clock_ms
    )
    path = f"{directory}/{date_filename}"

    content_b64 = base64.b64encode(file.content).decode("ascii")
    url = f"https://api.github.com/repos/{username}/{repo}/contents/{path}"

    response = http_client.put(
        url,
        headers={
            "Authorization": f"token {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "md-api-upload",
        },
        json={
            "content": content_b64,
            "branch": branch,
            "message": f"Upload by {referer}",
        },
    )

    if response.status_code // 100 != 2:
        _raise_for_github_error(response)

    data = response.json()
    content = data.get("content") if isinstance(data, dict) else None
    download_url = content.get("download_url") if isinstance(content, dict) else None
    if not download_url:
        raise RuntimeError("GitHub upload failed: missing download_url")

    if not config.use_cdn:
        return download_url

    github_resource = f"raw.githubusercontent.com/{username}/{repo}/{branch}/"
    cdn_resource = f"fastly.jsdelivr.net/gh/{username}/{repo}@{branch}/"
    # upstream: String.replace 仅替换第一处
    return download_url.replace(github_resource, cdn_resource, 1)
