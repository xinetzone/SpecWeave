"""运行时配置：全部来自环境变量，仓库内不内置任何密钥。"""

import os
import secrets
from dataclasses import dataclass, field


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _env_float(name: str, default: float) -> float:
    raw = _env(name)
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


#: 允许上传的内容类型白名单（小写比对）。
DEFAULT_UPLOAD_TYPES = (
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/zip",
    "application/json",
    "video/mp4",
    "audio/mpeg",
)


@dataclass
class Config:
    """应用配置。密钥只从环境变量读取，缺失时降级而非崩溃。"""

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_bucket: str = "ac-uploads"
    session_secret: str = ""
    session_ttl: int = 12 * 60 * 60
    max_upload_bytes: int = 5 * 1024 * 1024
    page_size: int = 20
    max_page_size: int = 100
    http_timeout: float = 8.0
    http_retries: int = 1
    signed_url_ttl: int = 3600
    upload_types: tuple = field(default=DEFAULT_UPLOAD_TYPES)
    #: 会话密钥缺失时随机生成（Serverless 冷启动后会话失效），需显式标记降级。
    ephemeral_secret: bool = False
    #: 内存降级模式下的演示账号（仅 degraded 且非 Vercel 生产环境生效）
    demo_admin_email: str = "admin@example.com"
    demo_admin_password: str = "admin12345"
    demo_admin_enabled: bool = True

    @classmethod
    def from_env(cls) -> "Config":
        cfg = cls(
            supabase_url=_env("SUPABASE_URL").rstrip("/"),
            supabase_service_role_key=_env("SUPABASE_SERVICE_ROLE_KEY"),
            supabase_bucket=_env("SUPABASE_BUCKET", "ac-uploads"),
            session_secret=_env("SESSION_SECRET"),
            session_ttl=_env_int("SESSION_TTL", 12 * 60 * 60),
            max_upload_bytes=_env_int("MAX_UPLOAD_BYTES", 5 * 1024 * 1024),
            page_size=_env_int("PAGE_SIZE", 20),
            max_page_size=_env_int("MAX_PAGE_SIZE", 100),
            http_timeout=_env_float("HTTP_TIMEOUT", 8.0),
            http_retries=_env_int("HTTP_RETRIES", 1),
            signed_url_ttl=_env_int("SIGNED_URL_TTL", 3600),
            demo_admin_email=_env("ADMIN_EMAIL", "admin@example.com"),
            demo_admin_password=_env("ADMIN_PASSWORD", "admin12345"),
            # 生产环境（Vercel）fail-closed：绝不启用口令已知的演示账号
            demo_admin_enabled=(not _env("VERCEL")) and _env("ADMIN_DEMO", "1") != "0",
        )
        if not cfg.session_secret:
            cfg.session_secret = secrets.token_hex(32)
            cfg.ephemeral_secret = True
        return cfg

    def with_overrides(self, **kwargs) -> "Config":
        """返回修改后的副本（测试与 BYOK 风格覆盖使用）。"""
        data = dict(self.__dict__)
        data.update({k: v for k, v in kwargs.items() if v is not None})
        clone = Config(**data)
        return clone

    @property
    def cloud_ready(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    @property
    def rest_base(self) -> str:
        return f"{self.supabase_url}/rest/v1"

    @property
    def storage_base(self) -> str:
        return f"{self.supabase_url}/storage/v1"

    def allows_upload_type(self, content_type: str) -> bool:
        base = (content_type or "").split(";")[0].strip().lower()
        return base in tuple(self.upload_types)
