"""AC-8：端到端接口冒烟（零真实密钥，全 mock 传输）。"""

import json

from inurl_byok_token_hub.crypto import b64e, new_master_key, random_salt, wrap_master_key
from inurl_byok_token_hub.models import Capability, ProviderProtocol, UserSettings
from inurl_byok_token_hub.providers.transport import HttpResponse, MockTransport
from inurl_byok_token_hub.services.hub import build_hub


def _ok_response(content: str = "mock 回答") -> HttpResponse:
    return HttpResponse(
        status_code=200,
        json_body={
            "id": "chatcmpl-x",
            "model": "m",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        },
    )


def _app_client(settings, hub, transport) -> object:
    from fastapi.testclient import TestClient

    from inurl_byok_token_hub.api.app import create_app

    return TestClient(create_app(settings, hub=hub, transport=transport))


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


def _setup(hub, registered, count: int = 3):
    result, master = registered
    picks = _providers(hub, count)
    for provider_id in picks:
        hub.vault.add_key(result.user.id, provider_id, f"sk-{provider_id}", master)
    return result, picks


def test_models_endpoint_lists_aliases_and_real_models(client, hub, registered):
    result, picks = _setup(hub, registered)
    resp = client.get("/v1/models", headers={"Authorization": f"Bearer {result.token}"})
    assert resp.status_code == 200
    ids = {item["id"] for item in resp.json()["data"]}
    for alias in ("inurl", "inurl-text", "inurl-code", "inurl-image", "inurl-video", "inurl-audio"):
        assert alias in ids


def test_chat_failover_429_then_503_then_ok(settings, hub, registered):
    result, picks = _setup(hub, registered)
    from fastapi.testclient import TestClient

    from inurl_byok_token_hub.api.app import create_app

    transport = MockTransport(
        responses=[
            HttpResponse(status_code=429, json_body={"error": {"message": "rate limited"}}),
            HttpResponse(status_code=503, json_body={"error": {"message": "unavailable"}}),
            HttpResponse(
                status_code=200,
                json_body={
                    "id": "chatcmpl-x",
                    "model": "m",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "mock 回答"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 3},
                },
            ),
        ]
    )
    app_client = TestClient(create_app(settings, hub=hub, transport=transport))
    resp = app_client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {result.token}"},
        json={"model": "inurl", "messages": [{"role": "user", "content": "你好"}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["choices"][0]["message"]["content"] == "mock 回答"
    assert body["_route"]["failover"] == 2
    assert len(body["_route"]["skipped"]) == 2
    assert hub.usage.total_calls(result.user.id) == 1


def test_chat_stream_returns_sse(settings, hub, registered):
    """AC-5 + F-027：stream=true 走 SSE 帧序列，终止于 [DONE]，内容合并后与上游一致。"""
    result, picks = _setup(hub, registered, count=1)
    transport = MockTransport(responses=[_ok_response("流式回答内容用于校验切分与合并")])
    app_client = _app_client(settings, hub, transport)
    resp = app_client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {result.token}"},
        json={
            "model": "inurl",
            "messages": [{"role": "user", "content": "你好"}],
            "stream": True,
        },
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert resp.text.rstrip().endswith("data: [DONE]")
    frames = [
        json.loads(line[len("data: ") :])
        for line in resp.text.splitlines()
        if line.startswith("data: ") and line[len("data: ") :] != "[DONE]"
    ]
    assert frames[0]["choices"][0]["delta"].get("role") == "assistant"
    joined = "".join(f["choices"][0]["delta"].get("content", "") for f in frames)
    assert joined == "流式回答内容用于校验切分与合并"
    assert frames[-1]["choices"][0]["finish_reason"] == "stop"
    assert frames[-1]["_route"]["provider"] == picks[0]
    assert hub.usage.total_calls(result.user.id) == 1


def test_unknown_payload_field_not_silently_dropped(settings, hub, registered):
    """未知字段进 extra：Anthropic 协议显式 422，而非透传后静默丢失。"""
    result, master = registered
    provider_id = "seed-free-12"  # catalog 中唯一的 anthropic 协议厂商
    hub.vault.add_key(result.user.id, provider_id, "sk-anthropic", master)
    app_client = _app_client(settings, hub, MockTransport(responses=[_ok_response()]))
    resp = app_client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {result.token}"},
        json={
            "model": "seed-free-12-a",
            "messages": [{"role": "user", "content": "你好"}],
            "tools": [{"name": "search"}],
        },
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "unsupported_feature"


def test_chat_failover_crosses_combo_layers(settings, hub, registered):
    """FR-6：第一层候选全部 429 后，必须流转到 Combo 的下一层而非直接失败。"""
    result, _picks = _setup(hub, registered, count=2)
    transport = MockTransport(
        responses=[
            HttpResponse(status_code=429, json_body={"error": {"message": "rate limited"}}),
            HttpResponse(status_code=429, json_body={"error": {"message": "rate limited"}}),
            _ok_response("第二层兜底成功"),
        ]
    )
    app_client = _app_client(settings, hub, transport)
    hub.store.settings.add(
        UserSettings(user_id=result.user.id, combo="latency_first>round_robin")
    )
    resp = app_client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {result.token}"},
        json={"model": "inurl", "messages": [{"role": "user", "content": "你好"}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["choices"][0]["message"]["content"] == "第二层兜底成功"
    assert body["_route"]["failover"] == 2


def test_chat_video_alias_unsupported(client, hub, registered):
    result, _picks = _setup(hub, registered)
    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {result.token}"},
        json={"model": "inurl-video", "messages": [{"role": "user", "content": "x"}]},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "unsupported_capability"
    assert "当前没有支持该类别的厂商" in resp.text


def test_turnstile_enabled_blocks_register_without_token(settings, hub):
    """FR-4：开启 Turnstile 后，注册未带校验 token 返回 401。"""
    from inurl_byok_token_hub.config import load_settings

    guarded = load_settings(
        data_dir=hub.store.data_dir,
        catalog_path=hub.settings.catalog_path,
        turnstile_enabled=True,
    )
    guarded_hub = build_hub(guarded)
    app_client = _app_client(guarded, guarded_hub, MockTransport(responses=[_ok_response()]))
    resp = app_client.post("/api/register", json={"email": "t@local", "password": "pw-123456"})
    assert resp.status_code == 401
    assert resp.json() == {"error": "unauthorized"}


def test_turnstile_disabled_is_passthrough(client):
    """默认关闭：注册不受影响（F-085 默认 enabled:false）。"""
    resp = client.post("/api/register", json={"email": "t2@local", "password": "pw-123456"})
    assert resp.status_code == 200


def test_client_escrow_is_actually_stored(client, hub, registered):
    """AC-2：`POST /api/escrow` 必须真正落盘并接管新主密钥，不得谎报 stored。"""
    result, master = registered
    provider_id = _providers(hub, 1)[0]
    hub.vault.add_key(result.user.id, provider_id, "sk-escrow", master)
    new_master = new_master_key()
    salt = random_salt()
    iv, wrapped = wrap_master_key(new_master, "user-password", salt)
    blob = {"kind": "pw", "cipher": {"salt": b64e(salt), "iv": b64e(iv), "ct": b64e(wrapped)}}
    before = hub.store.escrow.find(lambda e: e.user_id == result.user.id).generation
    resp = client.post(
        "/api/escrow",
        headers={"Authorization": f"Bearer {result.token}"},
        json={"escrow_pw": blob, "escrow_rec": blob, "password": "user-password"},
    )
    assert resp.status_code == 200
    assert resp.json()["stored"] is True
    assert resp.json()["generation"] == before + 1
    record = hub.store.keys.find(lambda k: k.user_id == result.user.id)
    assert hub.vault.decrypt_key(record, new_master) == "sk-escrow"


def test_escrow_upload_without_password_is_rejected(client, hub, registered):
    """服务端代理必须能解出主密钥，缺少 password 时明确拒绝而非假装成功。"""
    result, _master = registered
    resp = client.post(
        "/api/escrow",
        headers={"Authorization": f"Bearer {result.token}"},
        json={"escrow_pw": {"cipher": {}}, "escrow_rec": {"cipher": {}}},
    )
    assert resp.status_code == 400
    assert "password" in resp.json()["error"]["message"]


def test_chat_applies_compression_before_upstream(settings, hub, registered):
    """AC-4 接线：/v1/settings 的压缩档位必须作用于发给上游的 messages。"""
    from inurl_byok_token_hub.models import CompressionLevel

    result, _picks = _setup(hub, registered, count=1)
    seen: list[dict] = []

    def handler(req):
        seen.append(req.json_body or {})
        return _ok_response("ok")

    transport = MockTransport(handler=handler)
    app_client = _app_client(settings, hub, transport)
    headers = {"Authorization": f"Bearer {result.token}"}
    app_client.put("/v1/settings", headers=headers, json={"compression": "aggressive"})
    long_text = "hello   world\n\n\nthis   is    a test   " * 10
    resp = app_client.post(
        "/v1/chat/completions",
        headers=headers,
        json={"model": "inurl", "messages": [{"role": "user", "content": long_text}]},
    )
    assert resp.status_code == 200
    sent = seen[-1]["messages"][-1]["content"]
    assert len(sent) < len(long_text)
    assert hub.store.settings.find(lambda s: s.user_id == result.user.id).compression is (
        CompressionLevel.AGGRESSIVE
    )


def test_chat_requires_unlocked_vault(client, hub):
    """未解锁密钥库（进程内无主密钥）时，推理接口应明确报错而非静默失败。"""
    fresh = hub.tokens.register("locked@local", "pw-locked", vault=hub.vault)
    master = hub.unlock(fresh.user.id, "pw-locked")
    hub.vault.add_key(fresh.user.id, _providers(hub, 1)[0], "sk-locked", master)
    hub._master_keys.pop(fresh.user.id, None)
    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {fresh.token}"},
        json={"model": "inurl", "messages": [{"role": "user", "content": "x"}]},
    )
    assert resp.status_code in {409, 503}


def test_metrics_endpoint(client, hub, registered):
    result, _picks = _setup(hub, registered)
    resp = client.get("/v1/metrics", headers={"Authorization": f"Bearer {result.token}"})
    assert resp.status_code == 200
    assert resp.json()["user_id"] == result.user.id


def test_settings_roundtrip(client, hub, registered):
    result, _picks = _setup(hub, registered)
    headers = {"Authorization": f"Bearer {result.token}"}
    resp = client.put(
        "/v1/settings", headers=headers, json={"strategy": "round_robin", "combo": "auto>random"}
    )
    assert resp.status_code == 200
    assert resp.json()["strategy"] == "round_robin"
    assert client.get("/v1/settings", headers=headers).json()["combo"] == "auto>random"


def test_admin_confirm_order_writes_audit(client, hub, registered):
    result, _picks = _setup(hub, registered)
    order = hub.billing.create_order(result.user.id, "standard")
    hub.billing.submit_proof(order.id, "proof-001")
    admin = {"Authorization": f"Bearer {hub.admin_token()}"}
    resp = client.post(f"/api/admin/orders/{order.id}/confirm", headers=admin)
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"
    audit = client.get("/api/admin/audit", headers=admin).json()["data"]
    assert any(e["action"] == "order.confirm" for e in audit)


def test_admin_reload_catalog(client, hub):
    admin = {"Authorization": f"Bearer {hub.admin_token()}"}
    resp = client.post("/api/admin/catalog/reload", headers=admin)
    assert resp.status_code == 200
    assert resp.json()["reloaded"] is True
