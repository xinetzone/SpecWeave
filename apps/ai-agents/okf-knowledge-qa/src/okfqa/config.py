"""运行时配置集中读取。

设计约束：
- 所有大模型凭据一律走环境变量，代码内零硬编码密钥；
- 未配置凭据时应用必须仍可运行（降级为抽取式检索直出），而非启动失败。
"""

import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = APP_ROOT / "static"
DEFAULT_DB_PATH = APP_ROOT / "data" / "knowledge.db"

DEFAULT_LLM_BASE_URL = "https://api.openai.com/v1"
DEFAULT_LLM_MODEL = "gpt-4o-mini"


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


def db_path() -> Path:
    custom = _env("OKF_DB_PATH")
    return Path(custom) if custom else DEFAULT_DB_PATH


def llm_base_url() -> str:
    return _env("LLM_BASE_URL") or _env("OPENAI_BASE_URL") or DEFAULT_LLM_BASE_URL


def llm_api_key() -> str:
    return _env("LLM_API_KEY") or _env("OPENAI_API_KEY")


def llm_model() -> str:
    return _env("LLM_MODEL") or _env("OPENAI_MODEL") or DEFAULT_LLM_MODEL


def llm_ready() -> bool:
    """是否具备调用大模型的能力。False 时服务降级为抽取式检索。"""
    return bool(llm_api_key())


def llm_timeout() -> float:
    return _env_float("LLM_TIMEOUT", 45.0)


def top_k() -> int:
    return _env_int("TOP_K", 6)


def max_context_chars() -> int:
    """送入大模型的上下文字符上限，防止长语料撑爆 token 预算。"""
    return _env_int("MAX_CONTEXT_CHARS", 6000)
