"""路由服务：逻辑别名解析、候选构建、策略/Combo 排序。

证据与默认的分界：
- **有文档证据**：别名 ``inurl``/``inurl-text``（旧别名 ``auto``/``default``）、
  ``inurl-code``、``inurl-image``、``inurl-video``、``inurl-audio``；
  429/5xx 切下一家；``AUTO_MODELS``/``AUTO_PROVIDER_ORDER`` 限池；
  catalog 中 video/audio 无任何可路由厂商（F-082）。
- **本实现默认**：候选打分细节、Combo 分层后的候选拼接方式、熔断阈值。
"""

import hashlib
import random
import time
from dataclasses import dataclass

from ..config import Settings
from ..errors import ByokError, ErrorCode
from ..logging_utils import get_logger
from ..models import (
    DEFAULT_ALIAS,
    Capability,
    RouteDecision,
    UserSettings,
    parse_combo,
    resolve_capability,
)
from ..storage import Store
from .health_service import HealthService
from .strategies import Candidate, StrategyContext, apply_strategy

logger = get_logger("services.router")


@dataclass(frozen=True)
class RoutePlan:
    alias: str
    capability: Capability | None
    strategy_seq: tuple[str, ...]
    candidates: tuple[Candidate, ...]
    #: 与 ``strategy_seq`` 一一对应的**分层候选**：层内按该层策略排序，
    #: 上一层全部失败后才流转下一层（源文档 F-095「Combo（`>` 分层流转）」）。
    layers: tuple[tuple[Candidate, ...], ...] = ()

    @property
    def is_empty(self) -> bool:
        return not self.candidates

    @property
    def layer_count(self) -> int:
        return len(self.layers) or 1


def baseline_latency(provider_id: str) -> float:
    """冷启动基线延迟（本实现默认）：健康服务尚无样本时的稳定伪基线。

    全部候选在无历史时若取值完全相同，``sorted`` 稳定排序会让 19 种策略
    退化成同一顺序（目录序），故按厂商 id 派生一个**确定性**抖动值
    （20~70ms），仅用于打破并列，不代表真实延迟。
    """
    digest = hashlib.blake2b(provider_id.encode("utf-8"), digest_size=4).digest()
    return 20.0 + (int.from_bytes(digest, "big") % 500) / 10.0


class RouterService:
    def __init__(
        self,
        store: Store,
        settings: Settings,
        catalog: object,
        health: HealthService,
    ) -> None:
        self.store = store
        self.settings = settings
        self.catalog = catalog
        self.health = health
        #: 每用户轮询游标（驻留内存，进程重启归零；见 README 假设说明）
        self._counters: dict[str, int] = {}

    # ------------------------------------------------------------ 候选构建
    def _keyed_providers(self, user_id: str) -> tuple[str, ...]:
        return tuple(
            k.provider_id for k in self.store.keys.where(lambda k: k.user_id == user_id and k.is_usable)
        )

    def _key_id(self, user_id: str, provider_id: str) -> str:
        key = self.store.keys.find(
            lambda k: k.user_id == user_id and k.provider_id == provider_id
        )
        return key.id if key else ""

    def _candidate(self, user_id: str, provider_id: str, model_id: str) -> Candidate:
        health = self.health.get(provider_id)
        key = self.store.keys.find(
            lambda k: k.user_id == user_id and k.provider_id == provider_id
        )
        quota = INF_QUOTA
        if key is not None and key.quota_remaining is not None:
            quota = float(key.quota_remaining)
        calls = len(
            self.store.usage.where(
                lambda u: u.user_id == user_id and u.provider_id == provider_id
            )
        )
        last_rows = self.store.usage.where(
            lambda u: u.user_id == user_id and u.provider_id == provider_id
        )
        last_used = max((r.created_at for r in last_rows), default=0.0)
        free = self.catalog.resolve_model(model_id)
        return Candidate(
            provider_id=provider_id,
            model_id=model_id,
            key_id=self._key_id(user_id, provider_id),
            cost=0.0 if (free is not None and free.free) else 10.0,
            latency_ms=health.ewma_latency_ms or baseline_latency(provider_id),
            success_rate=health.success_rate or 0.5,
            consecutive_failures=health.consecutive_failures,
            calls=calls,
            quota_remaining=quota,
            last_used=last_used,
        )

    def build_candidates(
        self,
        user_id: str,
        model: str,
        *,
        auto_models: tuple[str, ...] = (),
        auto_provider_order: tuple[str, ...] = (),
    ) -> tuple[Capability | None, list[Candidate]]:
        model_key = (model or DEFAULT_ALIAS).strip()
        capability = resolve_capability(model_key.lower())
        providers = self._keyed_providers(user_id)

        if capability is not None:
            entries = [
                m
                for m in self.catalog.by_capability(capability)
                if m.provider_id in providers
            ]
        else:
            entry = self.catalog.resolve_model(model_key)
            if entry is None or entry.provider_id not in providers:
                raise ByokError(
                    ErrorCode.MODEL_NOT_FOUND, f"模型 {model_key!r} 不在已录入密钥的可路由池中"
                )
            entries = [entry]

        if auto_models:
            entries = [m for m in entries if m.id in auto_models]
        if auto_provider_order:
            order = {pid: i for i, pid in enumerate(auto_provider_order)}
            entries = [m for m in entries if m.provider_id in order]
            entries.sort(key=lambda m: order[m.provider_id])
        if not entries:
            if capability is not None:
                raise ByokError(ErrorCode.UNSUPPORTED_CAPABILITY)
            raise ByokError(ErrorCode.MODEL_NOT_FOUND)

        return capability, [self._candidate(user_id, m.provider_id, m.id) for m in entries]

    # ------------------------------------------------------------ 计划生成
    def plan(
        self,
        user_id: str,
        model: str,
        *,
        settings_row: UserSettings | None = None,
        strategy: str | None = None,
        combo: str | None = None,
        auto_models: tuple[str, ...] | None = None,
        auto_provider_order: tuple[str, ...] | None = None,
        seed: int | None = None,
    ) -> RoutePlan:
        row = settings_row or self.store.settings.find(lambda s: s.user_id == user_id)
        use_strategy = strategy or (row.strategy if row else self.settings.default_strategy)
        use_combo = combo if combo is not None else (row.combo if row else self.settings.default_combo)
        use_models = auto_models if auto_models is not None else (
            row.auto_models if row else self.settings.auto_models
        )
        use_order = auto_provider_order if auto_provider_order is not None else (
            row.auto_provider_order if row else self.settings.auto_provider_order
        )

        model_key = (model or DEFAULT_ALIAS).strip()
        capability, candidates = self.build_candidates(
            user_id, model_key, auto_models=use_models, auto_provider_order=use_order
        )

        layers = parse_combo(use_combo) or (use_strategy,)
        #: 轮询游标按用户递增，使 ``round_robin`` / ``top3_round_robin`` 逐次轮换
        counter = self._counters.get(user_id, 0)
        self._counters[user_id] = counter + 1
        rng = random.Random(seed) if seed is not None else random.Random()  # noqa: S311
        ctx = StrategyContext(
            rng=rng,
            counter=counter,
            now=time.time(),
        )
        ordered_layers: list[tuple[Candidate, ...]] = []
        seen: set[tuple[str, str]] = set()
        ordered: list[Candidate] = []
        for layer in layers:
            layer_items: list[Candidate] = []
            in_layer: set[tuple[str, str]] = set()
            for item in apply_strategy(layer, candidates, ctx):
                marker = (item.provider_id, item.model_id)
                if marker in in_layer:
                    continue
                in_layer.add(marker)
                layer_items.append(item)
                if marker not in seen:
                    seen.add(marker)
                    ordered.append(item)
            ordered_layers.append(tuple(layer_items))
        # 未在任何策略层出现的候选（例如 combo 只覆盖部分策略）按原序兜底追加
        for item in candidates:
            marker = (item.provider_id, item.model_id)
            if marker not in seen:
                seen.add(marker)
                ordered.append(item)
                ordered_layers.append((item,))
        return RoutePlan(
            alias=model_key,
            capability=capability,
            strategy_seq=layers,
            candidates=tuple(ordered),
            layers=tuple(ordered_layers),
        )

    def decision(self, plan: RoutePlan) -> RouteDecision:
        return RouteDecision(
            alias=plan.alias,
            capability=plan.capability,
            strategy=">".join(plan.strategy_seq),
            candidates=tuple(c.provider_id for c in plan.candidates),
        )


INF_QUOTA = float("inf")

__all__ = ["INF_QUOTA", "RoutePlan", "RouterService"]
