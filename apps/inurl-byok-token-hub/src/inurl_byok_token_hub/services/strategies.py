"""19 种路由策略实现。

证据边界：19 种策略的**名称集合**来自源文档 F-095（/app 设置面板界面证据）；
各策略的**具体排序算法属本实现的合理默认**——原产品代理为闭源程序，
无法从公开资料核实其内部打分公式，故不得宣称与原实现等价。
"""

import random
import time
from dataclasses import dataclass, field

from ..models import STRATEGIES

INF = float("inf")


@dataclass(frozen=True)
class Candidate:
    """路由候选：一个「厂商 + 模型」组合。"""

    provider_id: str
    model_id: str
    key_id: str = ""
    priority: int = 100
    weight: float = 1.0
    cost: float = 0.0  # 0 表示免费档
    latency_ms: float = 0.0
    success_rate: float = 0.0
    consecutive_failures: int = 0
    calls: int = 0
    quota_remaining: float = INF
    last_used: float = 0.0

    def score(self) -> float:
        """综合打分（auto 策略使用）：成功率越高、延迟与成本越低越优。"""
        latency_penalty = min(self.latency_ms, 10_000.0) / 10_000.0
        cost_penalty = min(self.cost, 100.0) / 100.0
        return self.success_rate - latency_penalty - cost_penalty


@dataclass
class StrategyContext:
    """策略执行上下文：注入随机源与状态，保证测试可确定性复现。"""

    rng: random.Random = field(default_factory=random.Random)
    counter: int = 0
    sticky_provider: str | None = None
    now: float = field(default_factory=time.time)


def _sorted(candidates: list[Candidate], key) -> list[Candidate]:
    return sorted(candidates, key=key)


def round_robin(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    if not candidates:
        return []
    offset = ctx.counter % len(candidates)
    return candidates[offset:] + candidates[:offset]


def latency_first(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (c.latency_ms, c.priority))


def priority(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (c.priority, c.latency_ms))


def cost_first(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (c.cost, c.latency_ms))


def health_first(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (-c.success_rate, c.consecutive_failures))


def success_rate_first(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (-c.success_rate, -c.calls, c.latency_ms))


def random_choice(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    shuffled = list(candidates)
    ctx.rng.shuffle(shuffled)
    return shuffled


def least_used(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (c.calls, c.priority))


def headroom_first(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (-c.quota_remaining, c.priority))


def weighted(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    total = sum(c.weight for c in candidates) or 1.0
    picked: list[Candidate] = []
    pool = list(candidates)
    while pool:
        draw = ctx.rng.uniform(0, total)
        acc = 0.0
        chosen = pool[-1]
        for item in pool:
            acc += item.weight
            if draw <= acc:
                chosen = item
                break
        picked.append(chosen)
        pool.remove(chosen)
        total = sum(c.weight for c in pool) or 1.0
    return picked


def sticky(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    if ctx.sticky_provider:
        pinned = [c for c in candidates if c.provider_id == ctx.sticky_provider]
        rest = [c for c in candidates if c.provider_id != ctx.sticky_provider]
        return pinned + rest
    return latency_first(candidates, ctx)


def diversity(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    """按厂商交错排列，避免连续命中同一家。"""
    buckets: dict[str, list[Candidate]] = {}
    for item in candidates:
        buckets.setdefault(item.provider_id, []).append(item)
    ordered: list[Candidate] = []
    keys = sorted(buckets)
    index = 0
    while any(buckets[k] for k in keys):
        for key in keys:
            if buckets[key]:
                ordered.append(buckets[key].pop(0))
        index += 1
        if index > len(candidates):  # pragma: no cover - 防御性
            break
    return ordered


def reliability(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(
        candidates, key=lambda c: (-c.success_rate, c.consecutive_failures, c.latency_ms)
    )


def cost_latency(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: -(c.score()))


def freshness(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    """最近未使用过的优先（LRU 反向）。"""
    return _sorted(candidates, key=lambda c: (c.last_used, c.priority))


def auto(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    """多因子实时打分（健康/额度/成本/延迟），对应原产品 auto 策略的定位。"""
    return _sorted(candidates, key=lambda c: -(c.score()))


def speed_first(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (c.latency_ms, -c.success_rate))


def cheapest_first(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    return _sorted(candidates, key=lambda c: (c.cost, c.priority, c.latency_ms))


def top3_round_robin(candidates: list[Candidate], ctx: StrategyContext) -> list[Candidate]:
    top3 = _sorted(candidates, key=lambda c: -(c.score()))[:3]
    if not top3:
        return []
    offset = ctx.counter % len(top3)
    rotated = top3[offset:] + top3[:offset]
    tail = [c for c in candidates if c not in top3]
    return rotated + tail


STRATEGY_REGISTRY: dict[str, object] = {
    "round_robin": round_robin,
    "latency_first": latency_first,
    "priority": priority,
    "cost_first": cost_first,
    "health_first": health_first,
    "success_rate_first": success_rate_first,
    "random": random_choice,
    "least_used": least_used,
    "headroom_first": headroom_first,
    "weighted": weighted,
    "sticky": sticky,
    "diversity": diversity,
    "reliability": reliability,
    "cost_latency": cost_latency,
    "freshness": freshness,
    "auto": auto,
    "speed_first": speed_first,
    "cheapest_first": cheapest_first,
    "top3_round_robin": top3_round_robin,
}


def apply_strategy(
    name: str, candidates: list[Candidate], ctx: StrategyContext | None = None
) -> list[Candidate]:
    """按策略名排序候选；未知策略回退到 ``auto``。"""
    ctx = ctx or StrategyContext()
    func = STRATEGY_REGISTRY.get(name)
    if func is None:
        func = STRATEGY_REGISTRY["auto"]
    return func(list(candidates), ctx)  # type: ignore[operator]


def strategy_names() -> tuple[str, ...]:
    return STRATEGIES


__all__ = [
    "Candidate",
    "INF",
    "STRATEGY_REGISTRY",
    "StrategyContext",
    "apply_strategy",
    "strategy_names",
]
