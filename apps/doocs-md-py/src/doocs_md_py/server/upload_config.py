"""上传后端配置（upstream: apps/api/src/upload-config.ts 1:1 语义层）。

Python 版相对上游新增 ``local`` 后端（零配置落盘），故后端枚举为
``local | github | s3``；其余常量与判定逐字对齐。
"""

from dataclasses import dataclass

from .config import Config

# upstream: upload-config.ts:13
UPLOAD_MAX_BYTES = 5 * 1024 * 1024

# upstream: upload-config.ts:15-19（权威值在 config.UPLOAD_RATE_LIMIT，此再导出）
from .config import UPLOAD_RATE_LIMIT as UPLOAD_RATE_LIMIT  # noqa: E402,F401

GITHUB_BACKEND = "github"
R2_BACKEND = "s3"  # Python 侧 R2 走 S3 SigV4（上游为 Workers R2 binding）
LOCAL_BACKEND = "local"  # Python 版新增


@dataclass(slots=True)
class GithubUploadConfig:
    """upstream: upload-config.ts:5-11 UploadGithubConfig。"""

    username: str
    repo_list: tuple[str, ...]
    branch: str
    tokens: tuple[str, ...]
    use_cdn: bool


# upstream: upload-config.ts:21-23
def is_upload_enabled(config: Config) -> bool:
    return config.upload_enabled


# upstream: upload-config.ts:25-27（Python 侧新增 local 默认分支）
def get_upload_backend(config: Config) -> str:
    backend = config.upload_backend
    if backend in (LOCAL_BACKEND, R2_BACKEND, GITHUB_BACKEND):
        return backend
    # 上游：非 "r2" 一律 github；Python 侧未知值兜底 local（默认后端）
    return LOCAL_BACKEND


# upstream: upload-config.ts:29-53
def parse_github_upload_config(config: Config) -> GithubUploadConfig | None:
    if not config.upload_github_tokens:
        return None
    return GithubUploadConfig(
        username=config.upload_github_username,
        repo_list=config.upload_github_repo_list,
        branch=config.upload_github_branch,
        tokens=config.upload_github_tokens,
        use_cdn=config.upload_github_use_cdn,
    )


# upstream: upload-config.ts:55-57（UPLOAD_IMAGES=bucket、UPLOAD_R2_PUBLIC_URL）
def is_r2_upload_ready(config: Config) -> bool:
    return bool(config.upload_s3_bucket and config.upload_s3_public_url.strip())


# upstream: upload-config.ts:59-64（未知枚举先归一化为 local 再判就绪）
def is_upload_backend_ready(config: Config) -> bool:
    backend = get_upload_backend(config)
    if backend == LOCAL_BACKEND:
        return True
    if backend == R2_BACKEND:
        return config.s3_upload_ready()
    return config.github_upload_ready()
