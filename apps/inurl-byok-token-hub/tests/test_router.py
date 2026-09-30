"""AC-3：路由别名、19 种策略、Combo 与 429/5xx 故障切换。"""

import pytest

from inurl_byok_token_hub.errors import ByokError, ErrorCode
from inurl_byok_token_hub.models import (
    STRATEGIES,
    Capability,
    ProviderProtocol,
    parse_combo,
    resolve_capability,
)
from inurl_byok_token_hub.services.strategies import Candidate, StrategyContext, apply_strategy


def _providers(hub, count: int = 3) -> list[str]:
    picks: list[str] = []
    for entry in hub.catalog.by_capability(Capability.TEXT):
        provider = hub.catalog.provider(entry.provider_id)
        if provider is None or provider.protocol is not ProviderProtocol.OPENAI_COMPAT:
            continue
        if entry.provider_id in picks:
            continue
        picks.append(entry.provider_id)
        if len(picks) == count:
            break
    return picks


def _seed_keys(hub, registered, count: int = 3) -> list[str]:
    result, master = registered
    picks = _providers(hub, count)
    for provider_id in picks:
        hub.vault.add_key(result.user.id, provider_id, f"sk-{provider_id}", master)
    return picks


def test_strategy_registry_has_nineteen():
    assert len(STRATEGIES) == 19
    assert len(set(STRATEGIES)) == 19


def test_all_nineteen_strategies_selectable():
    candidates = [
        Candidate(provider_id=f"p{i}", model_id=f"m{i}", latency_ms=100 - i, cost=i)
        for i in range(4)
    ]
    for name in STRATEGIES:
        ordered = apply_strategy(name, candidates, StrategyContext())
        assert len(ordered) == len(candidates), name
        assert {c.provider_id for c in ordered} == {c.provider_id for c in candidates}, name


def test_alias_resolution():
    assert resolve_capability("inurl") is Capability.TEXT
    assert resolve_capability("inurl-text") is Capability.TEXT
    assert resolve_capability("auto") is Capability.TEXT
    assert resolve_capability("default") is Capability.TEXT
    assert resolve_capability("inurl-code") is Capability.CODE
    assert resolve_capability("inurl-image") is Capability.IMAGE
    assert resolve_capability("inurl-video") is Capability.VIDEO
    assert resolve_capability("inurl-audio") is Capability.AUDIO
    assert resolve_capability("zhipu/glm-4-flash") is None


def test_combo_parsing():
    assert parse_combo("") == ()
    assert parse_combo("latency_first>round_robin") == ("latency_first", "round_robin")


def test_plan_returns_candidates_for_text_alias(hub, registered):
    result, _master = registered
    picks = _seed_keys(hub, registered)
    plan = hub.router.plan(result.user.id, "inurl")
    assert not plan.is_empty
    assert plan.capability is Capability.TEXT
    assert {c.provider_id for c in plan.candidates} <= set(picks)


def test_default_and_legacy_aliases_equivalent(hub, registered):
    result, _master = registered
    _seed_keys(hub, registered)
    for alias in ("inurl", "inurl-text", "auto", "default"):
        plan = hub.router.plan(result.user.id, alias)
        assert plan.capability is Capability.TEXT, alias
        assert not plan.is_empty, alias


def test_combo_layers_are_recorded(hub, registered):
    result, _master = registered
    _seed_keys(hub, registered)
    plan = hub.router.plan(result.user.id, "inurl", combo="latency_first>round_robin")
    assert plan.strategy_seq == ("latency_first", "round_robin")


def test_combo_produces_one_layer_per_strategy(hub, registered):
    """FR-6：Combo 的每一层各自产出一份有序候选，供「本层耗尽流转下一层」消费。"""
    result, _master = registered
    picks = _seed_keys(hub, registered, count=3)
    plan = hub.router.plan(result.user.id, "inurl", combo="latency_first>round_robin")
    assert plan.layer_count == 2
    assert len(plan.layers) == 2
    for layer in plan.layers:
        assert {c.provider_id for c in layer} == set(picks)
    # 各层是**独立**的回退链：第二层必须重新覆盖全部候选，而非被去重清空
    assert plan.layers[1], "第二层不得为空，否则回退链失效"


def test_round_robin_rotates_across_calls(hub, registered):
    """轮询策略必须逐次轮换（轮询游标随调用递增）。"""
    result, _master = registered
    _seed_keys(hub, registered, count=3)
    first = hub.router.plan(result.user.id, "inurl", combo="round_robin").candidates
    second = hub.router.plan(result.user.id, "inurl", combo="round_robin").candidates
    third = hub.router.plan(result.user.id, "inurl", combo="round_robin").candidates
    heads = [c[0].provider_id for c in (first, second, third)]
    assert len(set(heads)) == 3, f"轮询未轮换：{heads}"


def test_strategies_are_distinguishable_at_cold_start(hub, registered):
    """冷启动（无健康/用量样本）时，不同策略不得全部退化为同一顺序。"""
    result, _master = registered
    _seed_keys(hub, registered, count=3)
    orders = {
        name: tuple(
            c.provider_id
            for c in hub.router.plan(result.user.id, "inurl", combo=name, seed=7).candidates
        )
        for name in ("latency_first", "diversity", "least_used", "random")
    }
    assert len({orders["latency_first"], orders["diversity"]}) == 2
    assert len(set(orders.values())) >= 2


def test_code_and_image_aliases_route(hub, registered):
    """AC-3：inurl-code / inurl-image 走各自能力池；真实模型 id 直连该厂商。"""
    result, master = registered
    for capability in (Capability.CODE, Capability.IMAGE):
        picks: list[str] = []
        for entry in hub.catalog.by_capability(capability):
            provider = hub.catalog.provider(entry.provider_id)
            if provider is None or provider.protocol is not ProviderProtocol.OPENAI_COMPAT:
                continue
            if entry.provider_id in picks:
                continue
            picks.append(entry.provider_id)
            hub.vault.add_key(result.user.id, entry.provider_id, "sk-x", master)
            break
        plan = hub.router.plan(result.user.id, f"inurl-{capability.value}")
        assert plan.capability is capability
        assert not plan.is_empty
        assert plan.candidates[0].provider_id in picks

    real_model = hub.catalog.by_capability(Capability.TEXT)[0]
    hub.vault.add_key(result.user.id, real_model.provider_id, "sk-y", master)
    direct = hub.router.plan(result.user.id, real_model.id)
    assert direct.capability is None
    assert {c.model_id for c in direct.candidates} == {real_model.id}


def test_video_and_audio_have_no_route(hub, registered):
    result, _master = registered
    _seed_keys(hub, registered)
    for alias in ("inurl-video", "inurl-audio"):
        with pytest.raises(ByokError) as exc:
            hub.router.plan(result.user.id, alias)
        assert exc.value.error_code is ErrorCode.UNSUPPORTED_CAPABILITY
        assert "当前没有支持该类别的厂商" in exc.value.message


def test_auto_provider_order_restricts_pool(hub, registered):
    result, _master = registered
    picks = _seed_keys(hub, registered)
    plan = hub.router.plan(result.user.id, "inurl", auto_provider_order=(picks[0],))
    assert {c.provider_id for c in plan.candidates} == {picks[0]}


def test_unknown_model_not_in_pool(hub, registered):
    result, _master = registered
    _seed_keys(hub, registered)
    with pytest.raises(ByokError) as exc:
        hub.router.plan(result.user.id, "totally/unknown-model")
    assert exc.value.error_code is ErrorCode.MODEL_NOT_FOUND


def test_circuit_breaker_removes_candidate(hub, registered):
    result, _master = registered
    picks = _seed_keys(hub, registered)
    for _ in range(3):
        hub.health.record_failure(picks[0], status_code=429)
    assert hub.health.get(picks[0]).state == "open"
    assert not hub.health.available(picks[0])
