"""运行时配置：环境变量驱动，**缺配置即降级，绝不在启动期崩溃**。

这条约定是整个应用的地基——个人信息管家必须能在「只装了 Python、什么密钥都没有」
的机器上跑起来给人看，否则第一次体验就是 500。因此所有配置项都有可用默认值：

- 没有 Supabase → 退回进程内存存储（重启即失，但功能完整）；
- 没有大模型 Key → 全部 AI 能力退化为启发式/统计直出；
- 没有 APP_TOKEN → 不鉴权（仅限本地回环）。
"""

import os
from dataclasses import dataclass, field

DEFAULT_LLM_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_LLM_MODEL = "deepseek-chat"


def _env(name: str, default: str = "") -> str:
    """读取环境变量；空串与未设置等价统一为默认值。"""
    return (os.environ.get(name) or "").strip() or default


def _env_float(name: str, default: float) -> float:
    raw = _env(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_list(name: str, default: str) -> list[str]:
    return [part.strip() for part in _env(name, default).split(",") if part.strip()]


@dataclass(frozen=True)
class Settings:
    """服务级配置。

    frozen 是刻意的：配置在进程启动时定形，运行期任何旁路修改都会让
    「当前到底是云端存储还是内存存储」变成不可推断的状态。
    """

    supabase_url: str = ""
    supabase_key: str = ""
    llm_base_url: str = DEFAULT_LLM_BASE_URL
    llm_api_key: str = ""
    llm_model: str = DEFAULT_LLM_MODEL
    app_token: str = ""
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    http_timeout: float = 15.0
    llm_timeout: float = 60.0

    # WorkBuddy 云服务：平台托管的 Postgres + 免密钥大模型。
    # 由平台在发布时注入，缺任一项即整体降级（不半启用）。
    wb_cloud_endpoint: str = ""
    wb_publishable_key: str = ""
    wb_llm_model: str = ""

    # 关联分析：先取候选集再本地打分，避免把全表拉进内存
    max_candidates: int = 500
    link_limit: int = 5
    link_threshold: float = 0.12

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            supabase_url=_env("SUPABASE_URL").rstrip("/"),
            supabase_key=_env("SUPABASE_SERVICE_ROLE_KEY") or _env("SUPABASE_KEY"),
            llm_base_url=_env("LLM_BASE_URL", DEFAULT_LLM_BASE_URL).rstrip("/"),
            llm_api_key=_env("LLM_API_KEY"),
            llm_model=_env("LLM_MODEL", DEFAULT_LLM_MODEL),
            app_token=_env("APP_TOKEN"),
            cors_origins=_env_list("CORS_ORIGINS", "*"),
            http_timeout=_env_float("HTTP_TIMEOUT", 15.0),
            llm_timeout=_env_float("LLM_TIMEOUT", 60.0),
            wb_cloud_endpoint=_env("WB_CLOUD_ENDPOINT").rstrip("/"),
            wb_publishable_key=_env("WB_PUBLISHABLE_KEY"),
            wb_llm_model=_env("WB_LLM_MODEL"),
            max_candidates=_env_int("MAX_CANDIDATES", 500),
            link_limit=_env_int("LINK_LIMIT", 5),
            link_threshold=_env_float("LINK_THRESHOLD", 0.12),
        )

    @property
    def cloud_ready(self) -> bool:
        """Supabase 的 URL 与 Key 必须成对出现，缺一半等于没配。"""
        return bool(self.supabase_url and self.supabase_key)

    @property
    def wb_cloud_ready(self) -> bool:
        """WorkBuddy 云服务的 endpoint 与 publishableKey 必须成对出现。"""
        return bool(self.wb_cloud_endpoint and self.wb_publishable_key)

    @property
    def llm_ready(self) -> bool:
        return bool(self.llm_api_key and self.llm_base_url)

    @property
    def wb_llm_ready(self) -> bool:
        """云端免密钥大模型可用：需要云服务环境 + 模型名。"""
        return bool(self.wb_cloud_ready and self.wb_llm_model)

    @property
    def storage_mode(self) -> str:
        if self.wb_cloud_ready or self.cloud_ready:
            return "cloud"
        return "memory"

    @property
    def storage_backend(self) -> str:
        """存储实现名，用于前端徽标与诊断。"""
        if self.wb_cloud_ready:
            return "workbuddy-cloud"
        if self.cloud_ready:
            return "supabase"
        return "memory"


@dataclass(frozen=True)
class LLMOverride:
    """请求级 BYOK 覆盖。

    用户在浏览器「设置」里填的 Base URL / API Key / 模型随请求头到达服务端，
    只在这一次请求的内存里生效：**不落盘、不写日志、不进存储层**。
    """

    base_url: str = ""
    api_key: str = ""
    model: str = ""

    @property
    def active(self) -> bool:
        """有 Key 才算 BYOK 生效；只填 Base URL 不足以切换端点。"""
        return bool(self.api_key)
