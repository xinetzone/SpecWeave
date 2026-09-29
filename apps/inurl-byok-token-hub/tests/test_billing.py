"""AC-6：套餐密钥上限与用量台账（核心勘误 E1）。

免费 ¥0 / 3 个厂商密钥；标准 ¥9.9 / 10 个；专业 ¥29.9 / 无限。
"""

import pytest

from inurl_byok_token_hub.errors import ByokError, ErrorCode
from inurl_byok_token_hub.models import Capability, ProviderProtocol


def _provider_ids(hub, count: int) -> list[str]:
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


def test_free_plan_allows_three_keys_only(hub, registered):
    result, master = registered
    providers = _provider_ids(hub, 4)
    assert len(providers) == 4
    for provider_id in providers[:3]:
        hub.vault.add_key(result.user.id, provider_id, f"sk-{provider_id}", master)
    assert hub.billing.count_keys(result.user.id) == 3
    with pytest.raises(ByokError) as exc:
        hub.vault.add_key(result.user.id, providers[3], "sk-fourth", master)
    assert exc.value.error_code is ErrorCode.KEY_LIMIT_EXCEEDED
    assert "升级套餐" in exc.value.message


def test_standard_plan_allows_ten(hub, registered):
    result, master = registered
    hub.billing.change_plan(result.user.id, "standard")
    providers = _provider_ids(hub, 11)
    for provider_id in providers[:10]:
        hub.vault.add_key(result.user.id, provider_id, f"sk-{provider_id}", master)
    with pytest.raises(ByokError) as exc:
        hub.vault.add_key(result.user.id, providers[10], "sk-eleventh", master)
    assert exc.value.error_code is ErrorCode.KEY_LIMIT_EXCEEDED


def test_pro_plan_is_unlimited(hub, registered):
    result, master = registered
    hub.billing.change_plan(result.user.id, "pro")
    assert hub.billing.key_limit(hub.store.users.find(lambda u: u.id == result.user.id)) is None
    providers = _provider_ids(hub, 12)
    for provider_id in providers:
        hub.vault.add_key(result.user.id, provider_id, f"sk-{provider_id}", master)
    assert hub.billing.count_keys(result.user.id) == len(providers)


def test_invite_bonus_raises_limit(hub, registered):
    result, _master = registered
    user = hub.store.users.find(lambda u: u.id == result.user.id)
    invited = hub.tokens.register("invited@local", "pw-invited", invited_by=user.id, vault=hub.vault)
    inviter = hub.store.users.find(lambda u: u.id == user.id)
    assert inviter.invite_bonus >= 1
    assert invited.user.invited_by == user.id


def test_plans_prices_match_source_doc(settings):
    free = settings.plan("free")
    standard = settings.plan("standard")
    pro = settings.plan("pro")
    assert (free.price_cents, free.key_limit) == (0, 3)
    assert (standard.price_cents, standard.key_limit) == (990, 10)
    assert (pro.price_cents, pro.key_limit) == (2990, None)


def test_usage_summary_computes_remaining(hub, registered):
    result, master = registered
    provider_id = _provider_ids(hub, 1)[0]
    hub.vault.add_key(result.user.id, provider_id, "sk-usage", master, quota_total=1000)
    hub.usage.record(user_id=result.user.id, provider_id=provider_id, model_id="m", prompt_tokens=40)
    summary = {s.provider_id: s for s in hub.usage.summaries(result.user.id)}
    assert summary[provider_id].calls == 1
    assert summary[provider_id].total_tokens == 40
    assert summary[provider_id].quota_remaining == 960


def test_payment_order_manual_redemption_flow(hub, registered):
    result, _master = registered
    order = hub.billing.create_order(result.user.id, "standard")
    assert order.status.value == "created"
    submitted = hub.billing.submit_proof(order.id, "支付宝单号 202609290001")
    assert submitted.status.value == "proof_submitted"
    confirmed = hub.billing.confirm_order(order.id, "admin")
    assert confirmed.status.value == "confirmed"
    user = hub.store.users.find(lambda u: u.id == result.user.id)
    assert user.plan_key == "standard"
    events = hub.store.billing.where(lambda e: e.user_id == result.user.id)
    assert any(e.kind.value == "order_confirmed" for e in events)


def test_invalid_order_transition_rejected(hub, registered):
    result, _master = registered
    order = hub.billing.create_order(result.user.id, "pro")
    hub.billing.submit_proof(order.id, "proof-002")
    hub.billing.confirm_order(order.id, "admin")
    with pytest.raises(ByokError) as exc:
        hub.billing.reject_order(order.id, "admin")
    assert exc.value.error_code is ErrorCode.ORDER_STATE_INVALID
