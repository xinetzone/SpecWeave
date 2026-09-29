"""配置层：三级合并优先级、loopback 守卫与构建后端约束（TR-1.1 / TR-1.2 / TR-12.3）。"""

import tomllib
from pathlib import Path

import pytest

from inurl_byok_token_hub.config import (
    DEFAULT_PLANS,
    Settings,
    load_settings,
)
from inurl_byok_token_hub.errors import ConfigError

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def test_defaults_are_loopback_and_port_3003():
    settings = load_settings()
    assert settings.host == "127.0.0.1"
    assert settings.port == 3003
    assert settings.api_prefix == "/v1"
    assert settings.base_url == "http://127.0.0.1:3003/v1"


def test_non_loopback_host_rejected_at_load_time():
    with pytest.raises(ConfigError):
        load_settings(host="0.0.0.0")
    with pytest.raises(ConfigError):
        load_settings(host="192.168.1.10")


def test_ipv6_loopback_allowed():
    assert load_settings(host="::1").host == "::1"


def test_env_overrides_yaml_and_defaults():
    settings = load_settings(env={"BYOK_PORT": "3999", "BYOK_MAX_ATTEMPTS": "5"})
    assert settings.port == 3999
    assert settings.max_attempts == 5


def test_agent_env_variables_parsed():
    settings = load_settings(
        env={
            "AGENT_TOKEN": "byok_live_envtoken",
            "AGENT_MASTERKEY": "master",
            "AUTO_MODELS": "a,b",
            "AUTO_PROVIDER_ORDER": "p1,p2",
        }
    )
    assert settings.agent_token == "byok_live_envtoken"
    assert settings.agent_masterkey == "master"
    assert settings.auto_models == ("a", "b")
    assert settings.auto_provider_order == ("p1", "p2")


def test_settings_is_frozen():
    settings = load_settings()
    with pytest.raises(Exception):
        settings.port = 4000  # type: ignore[misc]


def test_unknown_override_rejected():
    with pytest.raises(ConfigError):
        load_settings(totally_unknown_key=1)


def test_default_plans_match_source_doc():
    assert [p.key_limit for p in DEFAULT_PLANS] == [3, 10, None]
    assert Settings().plans == DEFAULT_PLANS


def test_pyproject_uses_scikit_build_core():
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    build = data["build-system"]
    assert build["build-backend"] == "scikit_build_core.build"
    assert any("scikit-build-core" in r for r in build["requires"])
    assert not any("cmake" in r.lower() or "ninja" in r.lower() for r in build["requires"])
    skb = data["tool"]["scikit-build"]
    assert skb["wheel"]["packages"] == ["src/inurl_byok_token_hub"]
    assert skb["build-dir"] == "build/{wheel_tag}"
    assert skb["minimum-version"] == "0.9"
    assert "cmake" not in skb, "纯 Python 包不得出现 cmake 配置段"
    assert data["project"]["requires-python"] == ">=3.14"
