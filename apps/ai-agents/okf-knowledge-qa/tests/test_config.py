"""配置层测试：环境变量别名、非法值回退、凭据就绪判定。"""

from pathlib import Path

from okfqa import config


def test_defaults_are_safe(monkeypatch) -> None:
    for key in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL", "OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL"):
        monkeypatch.delenv(key, raising=False)
    assert config.llm_base_url() == config.DEFAULT_LLM_BASE_URL
    assert config.llm_model() == config.DEFAULT_LLM_MODEL
    assert config.llm_ready() is False
    assert config.top_k() == 6


def test_base_url_prefers_primary_alias(monkeypatch) -> None:
    monkeypatch.setenv("LLM_BASE_URL", "https://primary/v1")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://fallback/v1")
    assert config.llm_base_url() == "https://primary/v1"


def test_base_url_falls_back_to_openai_alias(monkeypatch) -> None:
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_BASE_URL", "https://fallback/v1")
    assert config.llm_base_url() == "https://fallback/v1"


def test_api_key_aliases(monkeypatch) -> None:
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fallback")
    assert config.llm_api_key() == "sk-fallback"
    assert config.llm_ready() is True

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert config.llm_ready() is False


def test_model_alias(monkeypatch) -> None:
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
    assert config.llm_model() == "gpt-4o"


def test_int_parsing_rejects_invalid(monkeypatch) -> None:
    for bad in ("abc", "", "-3", "0"):
        monkeypatch.setenv("TOP_K", bad)
        assert config.top_k() == 6, f"TOP_K={bad!r} 应回退为默认值 6"


def test_int_parsing_accepts_valid(monkeypatch) -> None:
    monkeypatch.setenv("TOP_K", "12")
    assert config.top_k() == 12


def test_float_parsing_rejects_invalid(monkeypatch) -> None:
    for bad in ("soon", "-1", "0"):
        monkeypatch.setenv("LLM_TIMEOUT", bad)
        assert config.llm_timeout() == 45.0


def test_float_parsing_accepts_valid(monkeypatch) -> None:
    monkeypatch.setenv("LLM_TIMEOUT", "12.5")
    assert config.llm_timeout() == 12.5


def test_db_path_override(monkeypatch, tmp_path) -> None:
    custom = tmp_path / "custom.db"
    monkeypatch.setenv("OKF_DB_PATH", str(custom))
    assert config.db_path() == custom

    monkeypatch.delenv("OKF_DB_PATH", raising=False)
    assert config.db_path() == config.DEFAULT_DB_PATH


def test_static_and_db_paths_are_app_relative() -> None:
    assert config.STATIC_DIR.name == "static"
    assert isinstance(config.DEFAULT_DB_PATH, Path)
    assert config.DEFAULT_DB_PATH.parent.name == "data"
