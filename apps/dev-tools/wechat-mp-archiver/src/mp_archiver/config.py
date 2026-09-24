"""配置模型：全部参数来自环境变量或当前目录的 ``.env`` 文件。

统一前缀 ``MP_ARCHIVER_``；凭证类字段使用 :class:`pydantic.SecretStr`，
避免在 repr/日志中意外泄露。
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class Settings(BaseSettings):
    """运行配置。"""

    model_config = SettingsConfigDict(
        env_prefix="MP_ARCHIVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # R2 采集服务
    exporter_url: str = "http://127.0.0.1:5000"
    exporter_token: SecretStr = SecretStr("")
    # 端点路径覆写（默认空：从采集服务 OpenAPI 自动发现；实测不匹配时手工指定）
    exporter_search_path: str = ""
    exporter_history_path: str = ""

    # 存储
    archive_root: Path = Path("archive")
    db_path: Path = Path("data") / "archive.db"

    # 限速与重试
    request_delay_min: float = Field(2.0, ge=0.0)
    request_delay_max: float = Field(5.0, ge=0.0)
    max_retries: int = Field(5, ge=0)
    backoff_base: float = Field(2.0, gt=0.0)
    backoff_cap: float = Field(60.0, gt=0.0)
    timeout: float = Field(30.0, gt=0.0)
    proxy_url: str = ""

    # 互动数据开关（默认关闭：无公开接口且易触发风控）
    fetch_metrics: bool = False
    # 手机端互动接口凭证（仅在 fetch_metrics=true 时需要；获取步骤见 deploy/README.md）
    # appmsg_token 与 pass_ticket 为必需项；key/wxuin 部分接口形态需要
    wechat_appmsg_token: SecretStr = SecretStr("")
    wechat_pass_ticket: SecretStr = SecretStr("")
    wechat_key: SecretStr = SecretStr("")
    wechat_wxuin: SecretStr = SecretStr("")

    # R1 自有号官方接口（可选，仅认证主体；见 deploy/README.md 第 11 节）
    wechat_app_id: str = ""
    wechat_app_secret: SecretStr = SecretStr("")
    # 官方接口不返回 __biz：优先从已同步的 R2 数据按别名解析，
    # 未做过 R2 同步时在此显式配置（形如 MzA...%3D%3D 的 Base64 串）
    wechat_official_biz: str = ""
    # freepublish/batchget 单日调用次数安全阈值（经验日限约 100 次，预留余量）
    official_daily_call_cap: int = Field(90, ge=1, le=1000)

    # 观测
    log_level: str = "INFO"
    user_agent: str = DEFAULT_USER_AGENT

    @field_validator("log_level")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        upper = value.strip().upper()
        if upper not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"非法日志级别: {value!r}")
        return upper

    @model_validator(mode="after")
    def _check_delay_interval(self) -> "Settings":
        if self.request_delay_max < self.request_delay_min:
            raise ValueError(
                "request_delay_max 不能小于 request_delay_min "
                f"({self.request_delay_max} < {self.request_delay_min})"
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """返回进程级单例配置。"""
    return Settings()
