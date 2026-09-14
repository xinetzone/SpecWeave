"""配置加载：YAML 配置 → dataclass。

优先使用 PyYAML；若环境缺失则尝试 tomllib 读取 TOML 或给出明确报错。
配置项含轮数、阈值、通道开关、合规确认项。
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any

from .models import ChannelState, LoopState


def _default_native_lib_name() -> str:
    """原生 tvm-ffi 模块的平台相关文件名（与 native/build 构建产物对应）。

    Windows=MSVC 构建产物 .dll（native/build.ps1）；Linux=.so
    （容器内 clang++，见 client overlay agent-monetize-dev）；
    macOS=.dylib。仅扩展名按平台选择，目录与前缀固定。
    """
    if sys.platform.startswith("win"):
        ext = "dll"
    elif sys.platform == "darwin":
        ext = "dylib"
    else:
        ext = "so"
    return f"native/build/score_opportunity.{ext}"

try:  # pragma: no cover - 环境探测分支
    import yaml as _yaml

    _HAS_YAML = True
except ImportError:  # pragma: no cover - 环境缺少 PyYAML 时的兜底
    _HAS_YAML = False

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.yaml"
)


@dataclass(slots=True)
class WuyouConfig:
    """无为门配置：低确定性/低预期收益则不行动（动善时）。"""

    min_certainty: float = 0.55
    min_expected_return: float = 1.5


@dataclass(slots=True)
class ZhizhiConfig:
    """知止门配置：单通道收益上限 + 总亏损红线（知足不辱，知止不殆）。"""

    per_channel_revenue_cap: float = 200.0
    total_loss_redline: float = -100.0


@dataclass(slots=True)
class TaoConfig:
    wuyou: WuyouConfig = field(default_factory=WuyouConfig)
    zhizhi: ZhizhiConfig = field(default_factory=ZhizhiConfig)


@dataclass(slots=True)
class ComplianceConfig:
    enable_red_zone: bool = True
    require_confirmation: bool = True
    confirmed_behaviors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ChannelConfig:
    enabled: bool = True
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LoopConfig:
    rounds: int = 12
    interval_seconds: float = 0.0
    event_driven: bool = False
    persist_every: int = 1
    state_path: str = "state.json"


@dataclass(slots=True)
class FfiConfig:
    # 默认按平台选择扩展名（.dll/.so/.dylib）；config.yaml 显式值仍优先
    native_lib: str = field(default_factory=_default_native_lib_name)
    fallback_to_reference: bool = True


@dataclass(slots=True)
class AppConfig:
    name: str = "agent-monetize"
    version: str = "0.1.0"
    seed: int = 42
    verbose: bool = True


@dataclass(slots=True)
class Config:
    """顶层配置对象。"""

    app: AppConfig = field(default_factory=AppConfig)
    loop: LoopConfig = field(default_factory=LoopConfig)
    tao: TaoConfig = field(default_factory=TaoConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    channels: dict[str, ChannelConfig] = field(default_factory=dict)
    ffi: FfiConfig = field(default_factory=FfiConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        cfg = cls()
        app = data.get("app", {})
        if isinstance(app, dict):
            cfg.app = AppConfig(
                **{k: v for k, v in app.items() if k in AppConfig.__dataclass_fields__}
            )

        loop = data.get("loop", {})
        if isinstance(loop, dict):
            cfg.loop = LoopConfig(
                **{k: v for k, v in loop.items() if k in LoopConfig.__dataclass_fields__}
            )

        tao = data.get("tao", {})
        if isinstance(tao, dict):
            wuyou = tao.get("wuyou", {})
            zhizhi = tao.get("zhizhi", {})
            cfg.tao = TaoConfig(
                wuyou=WuyouConfig(
                    **{k: v for k, v in wuyou.items() if k in WuyouConfig.__dataclass_fields__}
                ),
                zhizhi=ZhizhiConfig(
                    **{k: v for k, v in zhizhi.items() if k in ZhizhiConfig.__dataclass_fields__}
                ),
            )

        compliance = data.get("compliance", {})
        if isinstance(compliance, dict):
            cfg.compliance = ComplianceConfig(
                enable_red_zone=compliance.get("enable_red_zone", True),
                require_confirmation=compliance.get("require_confirmation", True),
                confirmed_behaviors=list(compliance.get("confirmed_behaviors", [])),
            )

        channels = data.get("channels", {})
        if isinstance(channels, dict):
            for cid, cdata in channels.items():
                if isinstance(cdata, dict):
                    params = {k: v for k, v in cdata.items() if k != "enabled"}
                    cfg.channels[cid] = ChannelConfig(
                        enabled=cdata.get("enabled", True), params=params
                    )

        ffi = data.get("ffi", {})
        if isinstance(ffi, dict):
            ffi_fields = {
                k: v for k, v in ffi.items()
                if k in FfiConfig.__dataclass_fields__
                # 空/None 的 native_lib 不覆盖：回退平台默认（.dll/.so/.dylib）
                and not (k == "native_lib" and not v)
            }
            cfg.ffi = FfiConfig(**ffi_fields)
        return cfg


def load_config(path: str | None = None) -> Config:
    """从 YAML 文件加载配置；缺失时返回默认配置。

    YAML 不可用则回退尝试 TOML（tomllib），再失败则抛出明确异常。
    """
    path = path or DEFAULT_CONFIG_PATH
    if not os.path.exists(path):
        return Config()
    if _HAS_YAML:
        with open(path, encoding="utf-8") as f:
            data = _yaml.safe_load(f) or {}
        return Config.from_dict(data)
    # 兜底：tomllib
    import tomllib

    with open(path, "rb") as f:
        data = tomllib.load(f)
    return Config.from_dict(data)


def build_initial_loop_state(config: Config) -> LoopState:
    """根据配置构建初始循环状态（为每个启用通道建 ChannelState）。"""
    state = LoopState()
    for cid, ccfg in config.channels.items():
        if ccfg.enabled:
            state.channels[cid] = ChannelState(channel_id=cid)
    return state
