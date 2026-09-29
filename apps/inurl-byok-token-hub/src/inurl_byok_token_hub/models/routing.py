"""路由模型：逻辑别名、19 种策略、Combo 回退链与路由决策。

别名口径（源文档 F-048、``examples/01`` §6）：
``inurl`` / ``inurl-text``（默认，旧别名 ``auto``、``default``）、
``inurl-code``、``inurl-image``、``inurl-video``、``inurl-audio``。
"""

import enum
import time

from pydantic import BaseModel, ConfigDict, Field

from .catalog import Capability

#: 逻辑别名 → 能力标签
ALIAS_CAPABILITIES: dict[str, Capability] = {
    "inurl": Capability.TEXT,
    "inurl-text": Capability.TEXT,
    "auto": Capability.TEXT,
    "default": Capability.TEXT,
    "inurl-code": Capability.CODE,
    "inurl-image": Capability.IMAGE,
    "inurl-video": Capability.VIDEO,
    "inurl-audio": Capability.AUDIO,
}

DEFAULT_ALIAS = "inurl"

#: 19 种路由策略（源文档 F-095：/app 设置面板列出 19 种）
STRATEGIES: tuple[str, ...] = (
    "round_robin",  # 轮询
    "latency_first",  # 延迟优先
    "priority",  # 优先级
    "cost_first",  # 成本优先
    "health_first",  # 健康优先
    "success_rate_first",  # 成功率优先
    "random",  # 随机
    "least_used",  # 最少使用
    "headroom_first",  # 余量优先
    "weighted",  # 加权
    "sticky",  # 粘性
    "diversity",  # 多样性
    "reliability",  # 可靠性
    "cost_latency",  # 成本+延迟兼顾
    "freshness",  # 新鲜度
    "auto",  # 自动
    "speed_first",  # 极速优先
    "cheapest_first",  # 极廉价优先
    "top3_round_robin",  # 均衡 Top3 轮询
)

STRATEGY_LABELS: dict[str, str] = {
    "round_robin": "轮询",
    "latency_first": "延迟优先",
    "priority": "优先级",
    "cost_first": "成本优先",
    "health_first": "健康优先",
    "success_rate_first": "成功率优先",
    "random": "随机",
    "least_used": "最少使用",
    "headroom_first": "余量优先",
    "weighted": "加权",
    "sticky": "粘性",
    "diversity": "多样性",
    "reliability": "可靠性",
    "cost_latency": "成本+延迟兼顾",
    "freshness": "新鲜度",
    "auto": "自动",
    "speed_first": "极速优先",
    "cheapest_first": "极廉价优先",
    "top3_round_robin": "均衡 Top3 轮询",
}

#: Combo 分隔符（源文档：``>`` 分隔的回退链，上层全失败流转下一层）
COMBO_SEPARATOR = ">"


class CompressionLevel(enum.StrEnum):
    """5 档提示词压缩（源文档 F-095；压缩率为页面自述估算值）。"""

    LITE = "lite"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    ULTRA = "ultra"
    RTK = "rtk"


COMPRESSION_SPECS: dict[CompressionLevel, tuple[str, str]] = {
    CompressionLevel.LITE: ("≈15%", "轻度压缩"),
    CompressionLevel.STANDARD: ("≈30%", "标准压缩"),
    CompressionLevel.AGGRESSIVE: ("≈50%", "激进压缩"),
    CompressionLevel.ULTRA: ("≈75%", "极限压缩"),
    CompressionLevel.RTK: ("60–90%", "RTK 工具链去重"),
}


class RouteRequest(BaseModel):
    """路由请求上下文。"""

    model_config = ConfigDict(frozen=True)

    model: str = DEFAULT_ALIAS
    strategy: str = "latency_first"
    combo: str = ""
    compression: CompressionLevel = CompressionLevel.STANDARD
    #: 候选池限定（对应 AUTO_MODELS / AUTO_PROVIDER_ORDER）
    auto_models: tuple[str, ...] = ()
    auto_provider_order: tuple[str, ...] = ()


class AttemptRecord(BaseModel):
    """单次尝试记录。"""

    model_config = ConfigDict(frozen=True)

    provider_id: str
    model_id: str
    status_code: int | None = None
    error: str = ""
    retryable: bool = False
    latency_ms: float = 0.0


class RouteDecision(BaseModel):
    """路由决策（可审计）：候选顺序、跳过原因、最终厂商与尝试记录。"""

    model_config = ConfigDict(frozen=True)

    alias: str = ""
    capability: Capability | None = None
    strategy: str = ""
    combo_layer: int = 0
    candidates: tuple[str, ...] = ()
    skipped: tuple[tuple[str, str], ...] = ()
    provider_id: str = ""
    model_id: str = ""
    attempts: tuple[AttemptRecord, ...] = ()
    failover_used: bool = False
    created_at: float = Field(default_factory=time.time)


class UserSettings(BaseModel):
    """用户偏好设置（路由策略 / Combo / 压缩档）。"""

    model_config = ConfigDict(frozen=True)

    user_id: str
    strategy: str = "latency_first"
    combo: str = ""
    compression: CompressionLevel = CompressionLevel.STANDARD
    auto_models: tuple[str, ...] = ()
    auto_provider_order: tuple[str, ...] = ()


def parse_combo(combo: str) -> tuple[str, ...]:
    """解析 ``延迟优先>轮询`` 形式的 Combo 链；空串返回空元组。"""
    if not combo:
        return ()
    return tuple(part.strip() for part in combo.split(COMBO_SEPARATOR) if part.strip())


def resolve_capability(model: str) -> Capability | None:
    """把逻辑别名解析为能力标签；真实模型 id 返回 ``None``。"""
    return ALIAS_CAPABILITIES.get(model.strip().lower())
