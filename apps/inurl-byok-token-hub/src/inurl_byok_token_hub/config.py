"""配置层：内置默认值 → YAML 配置文件 → 环境变量（``BYOK_*``）三级合并。

安全约束：监听地址必须在**加载期**通过 loopback 守卫，非法 host 直接抛
:class:`ConfigError`，绝不进入 uvicorn（避免误将密钥枢纽暴露到局域网）。
"""

import ipaddress
import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigError

ENV_PREFIX = "BYOK_"

#: 允许监听的回环字面量（与原产品「仅本机代理」口径一致）
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost", "127.0.0.0/8"})


def _is_loopback(host: str) -> bool:
    host = (host or "").strip()
    if host in {"localhost", "::1"}:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


@dataclass(frozen=True)
class PlanSpec:
    """套餐定义。``key_limit`` 为 ``None`` 表示无限。"""

    key: str
    name: str
    price_cents: int
    key_limit: int | None

    @property
    def is_unlimited(self) -> bool:
        return self.key_limit is None

    @property
    def price_yuan(self) -> float:
        return self.price_cents / 100.0


DEFAULT_PLANS: tuple[PlanSpec, ...] = (
    PlanSpec(key="free", name="免费版", price_cents=0, key_limit=3),
    PlanSpec(key="standard", name="标准版", price_cents=990, key_limit=10),
    PlanSpec(key="pro", name="专业版", price_cents=2990, key_limit=None),
)


@dataclass(frozen=True)
class Settings:
    """不可变配置对象。"""

    host: str = "127.0.0.1"
    port: int = 3003
    api_prefix: str = "/v1"

    data_dir: Path = Path("data/runtime")
    catalog_path: Path = Path("data/catalog.json")

    failover_status_codes: frozenset[int] = frozenset({429, 500, 502, 503, 504})
    max_attempts: int = 3
    timeout_seconds: float = 30.0

    default_strategy: str = "latency_first"
    default_combo: str = ""
    default_compression: str = "standard"

    hide_hidden_providers: bool = False
    turnstile_enabled: bool = False

    plans: tuple[PlanSpec, ...] = DEFAULT_PLANS
    invite_bonus_per_invite: int = 1
    invite_bonus_cap: int = 5

    admin_email: str = "admin@local"
    #: 留空表示首次启动时**随机生成**（不落配置文件，避免明文口令入版本库）；
    #: 可由环境变量 ``BYOK_ADMIN_PASSWORD`` 显式指定。
    admin_password: str = ""

    # 环境注入的代理凭证（对应原产品 AGENT_TOKEN / AGENT_MASTERKEY）
    agent_token: str | None = None
    agent_masterkey: str | None = None
    auto_models: tuple[str, ...] = ()
    auto_provider_order: tuple[str, ...] = ()

    runtime_extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not _is_loopback(self.host):
            raise ConfigError(f"监听地址必须是回环地址，收到 {self.host!r}")

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.api_prefix}"

    def plan(self, key: str) -> PlanSpec:
        for plan in self.plans:
            if plan.key == key:
                return plan
        raise ConfigError(f"未知套餐 {key!r}")

    def with_overrides(self, **overrides: Any) -> Settings:
        unknown = set(overrides) - {f for f in self.__dataclass_fields__}
        if unknown:
            raise ConfigError(f"未知配置项 {sorted(unknown)}")
        return replace(self, **overrides)


def _plans_from_yaml(raw: dict[str, Any]) -> tuple[PlanSpec, ...]:
    plans: list[PlanSpec] = []
    for key, spec in (raw or {}).items():
        if not isinstance(spec, dict):
            raise ConfigError(f"套餐 {key!r} 配置格式错误")
        plans.append(
            PlanSpec(
                key=str(key),
                name=str(spec.get("name", key)),
                price_cents=int(spec.get("price_cents", 0)),
                key_limit=(None if spec.get("key_limit") is None else int(spec["key_limit"])),
            )
        )
    return tuple(plans) if plans else DEFAULT_PLANS


_INT_FIELDS = {"port", "max_attempts", "invite_bonus_per_invite", "invite_bonus_cap"}
_FLOAT_FIELDS = {"timeout_seconds"}
_BOOL_FIELDS = {"hide_hidden_providers", "turnstile_enabled"}
_PATH_FIELDS = {"data_dir", "catalog_path"}
_LIST_FIELDS = {"failover_status_codes"}


def _coerce(name: str, value: Any) -> Any:
    if name in _INT_FIELDS:
        return int(value)
    if name in _FLOAT_FIELDS:
        return float(value)
    if name in _LIST_FIELDS:
        return frozenset(int(v) for v in value)
    if name in _PATH_FIELDS:
        return Path(str(value))
    if name in _BOOL_FIELDS:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}
    return value


def _from_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"配置文件 {path} 顶层必须是映射")
    if "plans" in data:
        data["plans"] = _plans_from_yaml(data["plans"])
    return data


def _from_env(env: dict[str, str] | None = None) -> dict[str, Any]:
    source = os.environ if env is None else env
    out: dict[str, Any] = {}
    for raw_key, raw_value in source.items():
        if raw_key == "AGENT_TOKEN":
            out["agent_token"] = raw_value
        elif raw_key == "AGENT_MASTERKEY":
            out["agent_masterkey"] = raw_value
        elif raw_key == "AUTO_MODELS":
            out["auto_models"] = tuple(v.strip() for v in raw_value.split(",") if v.strip())
        elif raw_key == "AUTO_PROVIDER_ORDER":
            out["auto_provider_order"] = tuple(
                v.strip() for v in raw_value.split(",") if v.strip()
            )
        elif raw_key.startswith(ENV_PREFIX):
            name = raw_key[len(ENV_PREFIX) :].lower()
            out[name] = raw_value
    return out


def load_settings(
    config_path: Path | None = None,
    env: dict[str, str] | None = None,
    **overrides: Any,
) -> Settings:
    """按「默认值 → YAML → 环境变量 → CLI 覆盖」合并配置。"""
    merged: dict[str, Any] = {}
    if config_path is not None:
        merged.update(_from_yaml(Path(config_path)))
    for key, value in _from_env(env).items():
        if key in {"agent_token", "agent_masterkey", "auto_models", "auto_provider_order"}:
            merged[key] = value
            continue
        if key not in Settings.__dataclass_fields__:
            continue
        merged[key] = _coerce(key, value)
    for key, value in overrides.items():
        if value is None:
            continue
        merged[key] = _coerce(key, value)
    unknown = set(merged) - set(Settings.__dataclass_fields__)
    if unknown:
        raise ConfigError(f"未知配置项 {sorted(unknown)}")
    return Settings(**merged)


def default_config_path() -> Path:
    """定位应用内置 ``config.yaml``（与包目录同级的应用根）。"""
    return Path(__file__).resolve().parents[2] / "config.yaml"
