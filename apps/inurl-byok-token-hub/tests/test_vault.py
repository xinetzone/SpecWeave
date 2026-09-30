"""AC-2：E2EE 托管库只存密文，且双 escrow 可恢复。

加密口径（源文档 F-052）：PBKDF2-SHA256 / 100000 迭代 → AES-256-GCM；
双 escrow（``escrow_pw`` 口令密文 + ``escrow_rec`` 恢复密语密文）。
"""

import pytest

from inurl_byok_token_hub.crypto import (
    ALG_AES_GCM,
    KDF_PBKDF2_SHA256,
    PBKDF2_ITERATIONS,
    derive_master_key,
    random_salt,
)
from inurl_byok_token_hub.errors import ByokError, ErrorCode
from inurl_byok_token_hub.models import KeyStatus
from inurl_byok_token_hub.models.catalog import ProviderProtocol

PLAIN_KEY = "sk-plain-secret-abcdef0123456789"


def _text_providers(hub, count: int = 3) -> list[str]:
    from inurl_byok_token_hub.models import Capability, ProviderProtocol

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


def test_crypto_parameters_match_source_doc():
    salt = random_salt()
    key = derive_master_key("pw", salt)
    assert len(key) == 32
    assert derive_master_key("pw", salt) == key
    assert derive_master_key("pw", random_salt()) != key
    assert PBKDF2_ITERATIONS == 100_000
    assert KDF_PBKDF2_SHA256 == "PBKDF2-SHA256"
    assert ALG_AES_GCM == "AES-256-GCM"


def test_escrow_pair_created_on_register(hub, registered):
    result, master = registered
    record = hub.store.escrow.find(lambda e: e.user_id == result.user.id)
    assert record is not None
    assert record.escrow_pw.cipher.iterations == PBKDF2_ITERATIONS
    assert record.escrow_rec.cipher.iterations == PBKDF2_ITERATIONS
    assert record.escrow_pw.cipher.alg == ALG_AES_GCM
    assert record.escrow_rec.cipher.alg == ALG_AES_GCM
    assert record.escrow_pw.cipher.ct != record.escrow_rec.cipher.ct
    assert hub.vault.unlock_with_recovery(result.user.id, result.recovery_secret) == master


def test_mark_error_and_remove_key(hub, registered):
    result, master = registered
    provider_id = _text_providers(hub, 1)[0]
    record = hub.vault.add_key(result.user.id, provider_id, PLAIN_KEY, master)
    hub.vault.mark_error(record.id, "上游 401")
    marked = hub.store.keys.find(lambda k: k.id == record.id)
    assert marked.status is KeyStatus.ERROR
    assert marked.last_error == "上游 401"
    assert hub.vault.remove_key(result.user.id, record.id) == 1
    assert hub.vault.remove_key(result.user.id, record.id) == 0


def test_adopt_client_escrow_rejects_malformed_blob(hub, registered):
    result, _master = registered
    with pytest.raises(ByokError) as excinfo:
        hub.vault.adopt_client_escrow(result.user.id, "not-a-dict", {}, "user-password")
    assert excinfo.value.error_code is ErrorCode.INVALID_REQUEST
    with pytest.raises(ByokError):
        hub.vault.adopt_client_escrow(result.user.id, {"cipher": {"ct": 1}}, {}, "user-password")


def test_key_protocol_derived_from_catalog_when_unspecified(hub, registered):
    """密钥线协议默认取目录厂商协议，否则 Anthropic/Gemini 永远走不到各自适配器。"""
    result, master = registered
    anthropic = hub.vault.add_key(result.user.id, "seed-free-12", PLAIN_KEY, master)
    assert anthropic.protocol is ProviderProtocol.ANTHROPIC
    overridden = hub.vault.add_key(
        result.user.id,
        "seed-paid-26",
        PLAIN_KEY,
        master,
        protocol=ProviderProtocol.OPENAI_COMPAT,
    )
    assert overridden.protocol is ProviderProtocol.OPENAI_COMPAT


def test_provider_key_roundtrip_and_no_plaintext_on_disk(hub, registered):
    result, master = registered
    provider_id = _text_providers(hub, 1)[0]
    record = hub.vault.add_key(result.user.id, provider_id, PLAIN_KEY, master)
    assert hub.vault.decrypt_key(record, master) == PLAIN_KEY
    dumped = hub.store.raw_text()
    assert PLAIN_KEY not in dumped
    assert "sk-plain-secret" not in dumped


def test_list_keys_never_returns_plaintext(hub, registered):
    result, master = registered
    provider_id = _text_providers(hub, 1)[0]
    hub.vault.add_key(result.user.id, provider_id, PLAIN_KEY, master)
    payload = str([k.model_dump(mode="json") for k in hub.vault.list_keys(result.user.id)])
    assert PLAIN_KEY not in payload
    assert "sk-plain-secret" not in payload


def test_password_change_invalidates_old_password(hub, registered):
    result, master = registered
    provider_id = _text_providers(hub, 1)[0]
    hub.vault.add_key(result.user.id, provider_id, PLAIN_KEY, master)
    hub.tokens.change_password(result.user.id, "user-password", "new-password-2")
    hub.vault.rotate_escrow(result.user.id, "user-password", "new-password-2", kind="pw")
    with pytest.raises(Exception):
        hub.vault.unlock_with_password(result.user.id, "user-password")
    assert hub.vault.unlock_with_password(result.user.id, "new-password-2") == master


def test_recovery_flow_restores_master_key(hub, registered):
    result, master = registered
    recovered = hub.vault.unlock_with_recovery(result.user.id, result.recovery_secret)
    assert recovered == master
    hub.tokens.reset_password_with_recovery(result.recovery_secret, "reset-password-3")
    hub.vault.rotate_escrow(
        result.user.id, None, "reset-password-3", kind="pw", master_key=master
    )
    assert hub.vault.unlock_with_password(result.user.id, "reset-password-3") == master


def test_wrong_master_key_raises_vault_error(hub, registered):
    result, master = registered
    provider_id = _text_providers(hub, 1)[0]
    record = hub.vault.add_key(result.user.id, provider_id, PLAIN_KEY, master)
    wrong = derive_master_key("not-the-password", random_salt())
    with pytest.raises(ByokError):
        hub.vault.decrypt_key(record, wrong)


def test_quota_exhausted_key_leaves_candidate_pool(hub, registered):
    result, master = registered
    provider_id = _text_providers(hub, 1)[0]
    record = hub.vault.add_key(result.user.id, provider_id, PLAIN_KEY, master, quota_total=10)
    hub.usage.record(user_id=result.user.id, provider_id=provider_id, model_id="m", prompt_tokens=20)
    updated = hub.store.keys.find(lambda k: k.id == record.id)
    assert updated.quota_used == 20
    assert updated.quota_remaining == 0
    assert updated.status is KeyStatus.QUOTA_EXHAUSTED
    assert not updated.is_usable
