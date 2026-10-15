"""环境配置（upstream: apps/api/src/types.ts Env + upload-config.ts 默认值）。

实现说明：不引入 pydantic-settings（NFR-2 依赖白名单外），用 dataclass + os.environ
做 12-factor 映射；字段名与上游环境变量一一对应。本地模式新增 local 上传后端与
SQLite/本地存储路径配置。
"""

import os
from dataclasses import dataclass, field

# upstream: upload-config.ts:13
UPLOAD_MAX_BYTES_DEFAULT = 5 * 1024 * 1024
# upstream: upload-config.ts:15-19
UPLOAD_RATE_LIMIT = {"anonymous": 60, "free": 120, "pro": 300}
DEFAULT_AFDIAN_API_BASE = "https://afdian.com/api/open"


def _csv(raw: str | None) -> tuple[str, ...]:
    return tuple(s.strip() for s in (raw or "").split(",") if s.strip())


def _env_bool(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in ("true", "1", "yes", "on")


@dataclass(slots=True)
class Config:
    """运行时配置；从环境变量加载，测试可直接构造。"""

    # ---- 服务与鉴权 ----
    app_url: str = "http://localhost:8800"
    jwt_secret: str = ""
    admin_github_logins: tuple[str, ...] = ()

    # ---- GitHub OAuth ----
    github_client_id: str = ""
    github_client_secret: str = ""

    # ---- 爱发电 ----
    afdian_user_id: str = ""
    afdian_api_token: str = ""
    afdian_api_base: str = DEFAULT_AFDIAN_API_BASE
    afdian_pro_plan_ids: tuple[str, ...] = ()
    afdian_webhook_token: str = ""

    # ---- 上传 ----
    upload_enabled: bool = True
    # Python 版后端：local（零配置）| github（upstream 默认）| s3（含 R2 兼容）
    upload_backend: str = "local"
    upload_max_bytes: int = UPLOAD_MAX_BYTES_DEFAULT
    upload_github_username: str = "bucketio"
    upload_github_repo_list: tuple[str, ...] = field(default_factory=lambda: tuple(f"img{i}" for i in range(20)))
    upload_github_branch: str = "main"
    upload_github_tokens: tuple[str, ...] = ()
    upload_github_use_cdn: bool = True
    upload_s3_endpoint: str = ""
    upload_s3_region: str = "auto"
    upload_s3_bucket: str = ""
    upload_s3_access_key_id: str = ""
    upload_s3_secret_access_key: str = ""
    upload_s3_force_path_style: bool = False
    upload_s3_public_url: str = ""

    # ---- Python 版新增：本地持久化 ----
    sqlite_path: str = str(os.path.join("data", "doocs-md-py.db"))
    storage_local_dir: str = str(os.path.join("data", "uploads"))
    storage_local_base_url: str = "/uploads"
    emoji_prefix: str = "emoji"
    # 表情资产（upstream 为独立 R2 binding EMOJI_ASSETS；Python 侧 local 默认，
    # s3 可指向独立桶，留空则复用上传桶并以 emoji_prefix 做键前缀隔离）
    emoji_backend: str = "local"
    emoji_local_dir: str = str(os.path.join("data", "emoji-assets"))
    emoji_s3_bucket: str = ""
    emoji_s3_public_url: str = ""

    # ---- 派生判定（对齐 upload-config.ts）----

    def is_oauth_configured(self) -> bool:
        return bool(self.github_client_id and self.github_client_secret)

    def is_jwt_configured(self) -> bool:
        return bool(self.jwt_secret)

    def is_afdian_configured(self) -> bool:
        return bool(self.afdian_user_id and self.afdian_api_token)

    def is_admin_login(self, login: str | None) -> bool:
        """upstream: marketplace 管理员判定（逗号分隔白名单，大小写不敏感）。"""
        if not login:
            return False
        wanted = login.strip().lower()
        return any(a.lower() == wanted for a in self.admin_github_logins)

    def github_upload_ready(self) -> bool:
        """upstream: parseGithubUploadConfig !== null（至少一个 PAT）。"""
        return bool(self.upload_github_tokens) and self.upload_backend == "github"

    def s3_upload_ready(self) -> bool:
        """upstream: isR2UploadReady（bucket + 凭证 + 对外 URL）。"""
        return (
            self.upload_backend == "s3"
            and bool(self.upload_s3_bucket)
            and bool(self.upload_s3_access_key_id)
            and bool(self.upload_s3_secret_access_key)
        )

    def upload_backend_ready(self) -> bool:
        """upstream: isUploadBackendReady；local 后端零配置恒就绪。"""
        if self.upload_backend == "local":
            return True
        if self.upload_backend == "s3":
            return self.s3_upload_ready()
        return self.github_upload_ready()

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> "Config":
        env = environ if environ is not None else os.environ

        repo_list = _csv(env.get("UPLOAD_GITHUB_REPO_LIST"))
        if not repo_list:
            repo_list = tuple(f"img{i}" for i in range(20))

        return cls(
            app_url=env.get("APP_URL", "http://localhost:8800").strip(),
            jwt_secret=env.get("JWT_SECRET", ""),
            admin_github_logins=_csv(env.get("ADMIN_GITHUB_LOGINS")),
            github_client_id=env.get("GITHUB_CLIENT_ID", ""),
            github_client_secret=env.get("GITHUB_CLIENT_SECRET", ""),
            afdian_user_id=env.get("AFDIAN_USER_ID", ""),
            afdian_api_token=env.get("AFDIAN_API_TOKEN", ""),
            afdian_api_base=env.get("AFDIAN_API_BASE", DEFAULT_AFDIAN_API_BASE).strip()
            or DEFAULT_AFDIAN_API_BASE,
            afdian_pro_plan_ids=_csv(env.get("AFDIAN_PRO_PLAN_IDS")),
            afdian_webhook_token=env.get("AFDIAN_WEBHOOK_TOKEN", ""),
            upload_enabled=_env_bool(env.get("UPLOAD_ENABLED"), default=True),
            upload_backend=env.get("UPLOAD_BACKEND", "local").strip() or "local",
            upload_max_bytes=int(env.get("UPLOAD_MAX_BYTES", str(UPLOAD_MAX_BYTES_DEFAULT))),
            upload_github_username=env.get("UPLOAD_GITHUB_USERNAME", "bucketio").strip() or "bucketio",
            upload_github_repo_list=repo_list,
            upload_github_branch=env.get("UPLOAD_GITHUB_BRANCH", "main").strip() or "main",
            upload_github_tokens=_csv(env.get("UPLOAD_GITHUB_TOKENS_BUCKETIO")),
            upload_github_use_cdn=_env_bool(env.get("UPLOAD_GITHUB_USE_CDN"), default=True),
            upload_s3_endpoint=env.get("UPLOAD_S3_ENDPOINT", ""),
            upload_s3_region=env.get("UPLOAD_S3_REGION", "auto"),
            upload_s3_bucket=env.get("UPLOAD_S3_BUCKET", ""),
            upload_s3_access_key_id=env.get("UPLOAD_S3_ACCESS_KEY_ID", ""),
            upload_s3_secret_access_key=env.get("UPLOAD_S3_SECRET_ACCESS_KEY", ""),
            upload_s3_force_path_style=_env_bool(env.get("UPLOAD_S3_FORCE_PATH_STYLE")),
            upload_s3_public_url=env.get("UPLOAD_S3_PUBLIC_URL", ""),
            sqlite_path=env.get(
                "DOOCS_MD_PY_SQLITE_PATH", str(os.path.join("data", "doocs-md-py.db"))
            ),
            storage_local_dir=env.get(
                "DOOCS_MD_PY_STORAGE_LOCAL_DIR", str(os.path.join("data", "uploads"))
            ),
            storage_local_base_url=env.get("DOOCS_MD_PY_STORAGE_LOCAL_BASE_URL", "/uploads"),
            emoji_prefix=env.get("DOOCS_MD_PY_EMOJI_PREFIX", "emoji"),
            emoji_backend=(env.get("DOOCS_MD_PY_EMOJI_BACKEND", "local").strip() or "local"),
            emoji_local_dir=env.get(
                "DOOCS_MD_PY_EMOJI_LOCAL_DIR", str(os.path.join("data", "emoji-assets"))
            ),
            emoji_s3_bucket=env.get("DOOCS_MD_PY_EMOJI_S3_BUCKET", ""),
            emoji_s3_public_url=env.get("DOOCS_MD_PY_EMOJI_S3_PUBLIC_URL", ""),
        )


def load_config() -> Config:
    """FastAPI lifespan/CLI 使用的默认加载入口。"""
    return Config.from_env()
