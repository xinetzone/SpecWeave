"""GitHub 图床（upstream: providers.ts:66-105，**Web 客户端版**）。

与服务端 ``server/upload_github.py`` 的差异：仓库配置来自用户填写的 repo URL
（三连前缀剥离 + ``/`` 切分），默认分支 ``master``、useCDN 默认 false，
提交信息为 ``Upload by <页面 location.href>``，请求仅带 Authorization 头
（无 User-Agent/Accept 定制；body 内文件内容为 base64）。
"""

import base64
from collections.abc import Callable
from dataclasses import dataclass

import httpx

from .base import UploadFile, get_date_filename, get_dir

GITHUB_API_BASE = "https://api.github.com"


@dataclass(slots=True)
class GithubWebConfig:
    username: str
    repo: str
    access_token: str
    branch: str = "master"
    use_cdn: bool = False


def parse_github_repo_url(repo_url: str) -> tuple[str, str]:
    """upstream: getConfig 三连 replace 后按 ``/`` 切分。"""
    cleaned = (
        repo_url.replace("https://github.com/", "")
        .replace("http://github.com/", "")
        .replace("github.com/", "")
    )
    parts = cleaned.split("/")
    return parts[0], parts[1]


def github_web_upload(
    config: GithubWebConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    location_href: str = "",
    now_sec: float | None = None,
    clock_ms: Callable[[], int] | None = None,
) -> str:
    directory = get_dir(now_sec)
    date_filename = get_date_filename(file.name, clock_ms=clock_ms)
    url = (
        f"{GITHUB_API_BASE}/repos/{config.username}/{config.repo}"
        f"/contents/{directory}/{date_filename}"
    )
    response = http_client.put(
        url,
        headers={"Authorization": f"token {config.access_token}"},
        json={
            "content": base64.b64encode(file.content).decode("ascii"),
            "branch": config.branch,
            "message": f"Upload by {location_href}",
        },
    )
    if response.status_code // 100 != 2:
        raise RuntimeError(f"GitHub upload failed: {response.reason_phrase}")

    data = response.json()
    download_url = (data.get("content") or {}).get("download_url", "")
    if not config.use_cdn:
        return download_url

    github_resource = (
        f"raw.githubusercontent.com/{config.username}/{config.repo}/{config.branch}/"
    )
    cdn_resource = (
        f"fastly.jsdelivr.net/gh/{config.username}/{config.repo}@{config.branch}/"
    )
    return download_url.replace(github_resource, cdn_resource, 1)
