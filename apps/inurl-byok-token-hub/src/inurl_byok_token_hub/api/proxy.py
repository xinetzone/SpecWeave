"""本地代理端点：OpenAI 兼容的 ``/v1/models`` 与 ``/v1/chat/completions``。

端口与前缀（源文档 F-020/F-047）：固定 ``http://localhost:3003/v1``。

流式（源文档 F-027「SSE 透传」）：``stream=true`` 时以 ``text/event-stream`` 下发
``chat.completion.chunk``，终止于 ``data: [DONE]``。上游响应在本实现中为非流式
（transport 抽象只返回完整 ``HttpResponse``），故 SSE 为**本地降级切分下发**，
而非上游真流式透传，详见 README「假设与差异说明」。
"""

import json
import time
from collections.abc import Iterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ..errors import ByokError, ErrorCode
from ..models import (
    ALIAS_CAPABILITIES,
    STRATEGIES,
    Capability,
    CompressionLevel,
    UserSettings,
)
from ..providers.base import ChatMessage, ChatRequest
from ..services.chat_service import ChatService
from .deps import current_user

router = APIRouter()

#: 由本层显式消费的请求键；其余键一律进 ``ChatRequest.extra``，交由厂商适配器
#: 决定「透传」（OpenAI 兼容）还是「显式 422 UNSUPPORTED_FEATURE」（Anthropic/Gemini），
#: 从而兑现「不支持的字段不静默丢弃」。
_CHAT_KNOWN_KEYS = frozenset({"model", "messages", "stream", "temperature", "max_tokens"})

#: SSE 单帧内容切分粒度（字符数）。
_SSE_CHUNK_SIZE = 24


def _chat_service(request: Request) -> ChatService:
    hub = request.app.state.hub
    return ChatService(
        hub.store,
        hub.settings,
        hub.catalog,
        hub.health,
        hub.router,
        hub.vault,
        hub.usage,
        transport=getattr(request.app.state, "transport", None),
    )


@router.get("/models")
def list_models(request: Request, user=Depends(current_user)) -> dict:
    """列出逻辑别名与当前可路由的真实模型。"""
    hub = request.app.state.hub
    data: list[dict] = []
    for alias in ALIAS_CAPABILITIES:
        data.append({"id": alias, "object": "model", "owned_by": "inurl"})
    keyed = tuple(
        k.provider_id for k in hub.store.keys.where(lambda k: k.user_id == user.id)
    )
    seen: set[str] = set()
    for provider_id in keyed:
        for entry in hub.catalog.models_of(provider_id):
            if entry.id in seen:
                continue
            seen.add(entry.id)
            data.append({"id": entry.id, "object": "model", "owned_by": provider_id})
    return {"object": "list", "data": data}


def _sse_stream(
    *,
    completion_id: str,
    created: int,
    model: str,
    content: str,
    finish_reason: str,
    route: dict,
) -> Iterator[str]:
    """把已完成的响应切分为 OpenAI 规范的 SSE 帧序列。"""

    def emit(delta: dict, finish: str | None = None, extra: dict | None = None) -> str:
        chunk: dict = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
        }
        if extra:
            chunk.update(extra)
        return f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    yield emit({"role": "assistant"})
    for start in range(0, len(content), _SSE_CHUNK_SIZE):
        yield emit({"content": content[start : start + _SSE_CHUNK_SIZE]})
    yield emit({}, finish=finish_reason, extra={"_route": route})
    yield "data: [DONE]\n\n"


@router.post("/chat/completions")
def chat_completions(request: Request, payload: dict, user=Depends(current_user)):
    hub = request.app.state.hub
    model = str(payload.get("model") or "inurl")
    stream = bool(payload.get("stream", False))
    extra = {k: v for k, v in payload.items() if k not in _CHAT_KNOWN_KEYS}
    messages = tuple(
        ChatMessage(role=str(m.get("role", "user")), content=str(m.get("content", "")))
        for m in payload.get("messages", [])
    )
    if not messages:
        raise ByokError(ErrorCode.INVALID_REQUEST, "messages 不能为空")

    settings_row = hub.store.settings.find(lambda s: s.user_id == user.id)
    compression = (
        settings_row.compression
        if settings_row
        else CompressionLevel(hub.settings.default_compression)
    )
    if compression is not CompressionLevel.LITE:
        from ..services.compression_service import compress_prompt

        joined = "\n".join(m.content for m in messages)
        result = compress_prompt(joined, compression)
        messages = tuple(
            ChatMessage(role=m.role, content=result.text if m.role == "user" else m.content)
            for m in messages
        )

    chat_request = ChatRequest(
        model=model,
        messages=messages,
        temperature=payload.get("temperature"),
        max_tokens=payload.get("max_tokens"),
        stream=stream,
        extra=extra,
    )
    master = hub.master_key(user.id)
    result = _chat_service(request).chat(user.id, chat_request, master_key=master)
    response = result.response
    created = response.created or int(time.time())
    route = {
        "provider": response.provider_id,
        "upstream_model": response.model,
        "strategy": result.decision.strategy,
        "failover": result.failover_count,
        "skipped": [{"provider": p, "reason": r} for p, r in result.decision.skipped],
    }
    if stream:
        return StreamingResponse(
            _sse_stream(
                completion_id=response.id or f"chatcmpl-{created}",
                created=created,
                model=model,
                content=response.content,
                finish_reason=response.finish_reason,
                route=route,
            ),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    return {
        "id": response.id or f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": response.created or int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": response.role, "content": response.content},
                "finish_reason": response.finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        },
        "_route": route,
    }


@router.get("/metrics")
def metrics(request: Request, user=Depends(current_user)) -> dict:
    """控制台轮询的代理状态（源文档 F-094；schema 为本实现自定义）。"""
    hub = request.app.state.hub
    return {
        "object": "metrics",
        "user_id": user.id,
        "calls": hub.usage.total_calls(user.id),
        "summaries": [s.model_dump(mode="json") for s in hub.usage.summaries(user.id)],
        "health": {k: v.state for k, v in hub.health.snapshot().items()},
    }


@router.get("/settings")
def get_settings(request: Request, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    row = hub.store.settings.find(lambda s: s.user_id == user.id)
    if row is None:
        row = UserSettings(user_id=user.id)
        hub.store.settings.add(row)
    return row.model_dump(mode="json")


@router.put("/settings")
def put_settings(request: Request, payload: dict, user=Depends(current_user)) -> dict:
    hub = request.app.state.hub
    row = hub.store.settings.find(lambda s: s.user_id == user.id) or UserSettings(
        user_id=user.id
    )
    allowed = {"strategy", "combo", "compression", "auto_models", "auto_provider_order"}
    updates = {k: v for k, v in payload.items() if k in allowed}
    if "auto_models" in updates:
        updates["auto_models"] = tuple(updates["auto_models"])
    if "auto_provider_order" in updates:
        updates["auto_provider_order"] = tuple(updates["auto_provider_order"])
    if "compression" in updates:
        #: 必须显式归一化为枚举：``model_copy`` 不走校验，写入裸字符串会让
        #: ``compression is not CompressionLevel.LITE`` 恒成立（LITE 档被误压缩）。
        try:
            updates["compression"] = CompressionLevel(str(updates["compression"]))
        except ValueError as exc:
            raise ByokError(ErrorCode.INVALID_REQUEST, f"compression 取值非法：{exc}") from exc
    if updates.get("strategy"):
        if str(updates["strategy"]) not in STRATEGIES:
            raise ByokError(ErrorCode.INVALID_REQUEST, f"未知策略：{updates['strategy']}")
    updated = row.model_copy(update=updates)
    hub.store.settings.upsert(lambda s: s.user_id == user.id, updated)
    return updated.model_dump(mode="json")


@router.get("/capabilities")
def capabilities(request: Request, user=Depends(current_user)) -> dict:  # noqa: ARG001
    return {
        "aliases": {alias: cap.value for alias, cap in ALIAS_CAPABILITIES.items()},
        "capabilities": [c.value for c in Capability],
    }
