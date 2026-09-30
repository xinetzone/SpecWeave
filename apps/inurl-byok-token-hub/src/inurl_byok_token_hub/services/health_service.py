"""健康度服务：成功率、延迟、连续失败与熔断。

熔断语义为**本实现的合理默认**（源文档只记载「429/5xx 切下一家」，
未定义熔断阈值与半开探测），阈值见 :class:`HealthService` 构造参数。
"""

import time
from dataclasses import dataclass, replace

from ..logging_utils import get_logger

logger = get_logger("services.health")

#: 连续失败达到该值即熔断
DEFAULT_FAILURE_THRESHOLD = 3
#: 熔断打开后的冷却时长（秒）
DEFAULT_COOLDOWN_SECONDS = 30.0
#: 延迟指数移动平均权重
EWMA_ALPHA = 0.3


@dataclass(frozen=True)
class ProviderHealth:
    provider_id: str
    successes: int = 0
    failures: int = 0
    consecutive_failures: int = 0
    ewma_latency_ms: float = 0.0
    last_status: int | None = None
    circuit_open_until: float = 0.0
    updated_at: float = 0.0

    @property
    def state(self) -> str:
        if self.circuit_open_until > time.time():
            return "open"
        if self.consecutive_failures >= DEFAULT_FAILURE_THRESHOLD:
            return "degraded"
        if self.successes + self.failures == 0:
            return "unknown"
        return "healthy"

    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        if total == 0:
            return 0.0
        return self.successes / total

    @property
    def is_available(self) -> bool:
        return self.state != "open"


class HealthService:
    def __init__(
        self,
        *,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._states: dict[str, ProviderHealth] = {}

    def get(self, provider_id: str) -> ProviderHealth:
        return self._states.get(provider_id, ProviderHealth(provider_id=provider_id))

    def _put(self, state: ProviderHealth) -> ProviderHealth:
        self._states[state.provider_id] = state
        return state

    def record_success(self, provider_id: str, *, latency_ms: float) -> ProviderHealth:
        current = self.get(provider_id)
        ewma = (
            latency_ms
            if current.successes + current.failures == 0
            else (1 - EWMA_ALPHA) * current.ewma_latency_ms + EWMA_ALPHA * latency_ms
        )
        return self._put(
            replace(
                current,
                successes=current.successes + 1,
                consecutive_failures=0,
                ewma_latency_ms=ewma,
                last_status=200,
                circuit_open_until=0.0,
                updated_at=time.time(),
            )
        )

    def record_failure(self, provider_id: str, *, status_code: int | None = None) -> ProviderHealth:
        current = self.get(provider_id)
        consecutive = current.consecutive_failures + 1
        open_until = current.circuit_open_until
        if consecutive >= self.failure_threshold:
            open_until = time.time() + self.cooldown_seconds
            logger.warning("厂商 %s 连续失败 %d 次，熔断至 %s", provider_id, consecutive, open_until)
        return self._put(
            replace(
                current,
                failures=current.failures + 1,
                consecutive_failures=consecutive,
                last_status=status_code,
                circuit_open_until=open_until,
                updated_at=time.time(),
            )
        )

    def snapshot(self) -> dict[str, ProviderHealth]:
        return dict(self._states)

    def available(self, provider_id: str) -> bool:
        return self.get(provider_id).is_available


__all__ = [
    "DEFAULT_COOLDOWN_SECONDS",
    "DEFAULT_FAILURE_THRESHOLD",
    "HealthService",
    "ProviderHealth",
]
