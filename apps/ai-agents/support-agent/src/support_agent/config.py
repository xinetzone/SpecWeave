"""运行时配置：全部来源于环境变量，支持前端 BYOK 覆盖大模型参数。"""

import os
from dataclasses import dataclass, replace

DEFAULT_LLM_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_LLM_MODEL = "deepseek-chat"
DEFAULT_BRAND = "SpecWeave 云服务"


def _env(name: str, default: str = "") -> str:
    value = os.environ.get(name, default)
    return value.strip() if isinstance(value, str) else default


@dataclass
class Config:
    """应用配置。"""

    supabase_url: str = ""
    supabase_key: str = ""
    llm_base_url: str = DEFAULT_LLM_BASE_URL
    llm_api_key: str = ""
    llm_model: str = DEFAULT_LLM_MODEL
    admin_token: str = ""
    brand: str = DEFAULT_BRAND
    request_timeout: float = 20.0
    history_turns: int = 6
    faq_top_k: int = 3
    faq_score_threshold: float = 3.0
    max_input_chars: int = 2000

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            supabase_url=_env("SUPABASE_URL"),
            supabase_key=_env("SUPABASE_SERVICE_ROLE_KEY") or _env("SUPABASE_KEY"),
            llm_base_url=_env("LLM_BASE_URL", DEFAULT_LLM_BASE_URL).rstrip("/"),
            llm_api_key=_env("LLM_API_KEY"),
            llm_model=_env("LLM_MODEL", DEFAULT_LLM_MODEL),
            admin_token=_env("ADMIN_TOKEN"),
            brand=_env("APP_BRAND", DEFAULT_BRAND),
        )

    def with_llm(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = "",
    ) -> "Config":
        """返回带 BYOK 覆盖的新配置（不修改原对象）。"""
        overrides = {}
        if base_url:
            overrides["llm_base_url"] = base_url.rstrip("/")
        if api_key:
            overrides["llm_api_key"] = api_key
        if model:
            overrides["llm_model"] = model
        return replace(self, **overrides) if overrides else self

    @property
    def cloud_ready(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    @property
    def llm_ready(self) -> bool:
        return bool(self.llm_api_key and self.llm_base_url)
