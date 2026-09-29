"""聊天编排服务：路由 → 厂商适配 → 故障切换 → 用量记账。

故障切换语义（源文档 F-048 有证据）：**429 与 5xx** 切下一家。
本实现补充的合理默认：切换上限、熔断参与、流式首字节后不再跨厂商续写。
"""

import time

from ..config import Settings
from ..errors import ByokError, ErrorCode, UpstreamError
from ..logging_utils import get_logger, redact
from ..models import AttemptRecord, CallStatus, RouteDecision
from ..models.catalog import ProviderProtocol
from ..providers.base import ChatRequest, ChatResponse, get_adapter
from ..providers.transport import HttpRequest, HttpResponse, Transport
from ..storage import Store
from .health_service import HealthService
from .router_service import RoutePlan, RouterService
from .usage_service import UsageService
from .vault_service import VaultService

logger = get_logger("services.chat")


class ChatResult:
    def __init__(self, response: ChatResponse, decision: RouteDecision, failover_count: int) -> None:
        self.response = response
        self.decision = decision
        self.failover_count = failover_count


class ChatService:
    def __init__(
        self,
        store: Store,
        settings: Settings,
        catalog: object,
        health: HealthService,
        router: RouterService,
        vault: VaultService,
        usage: UsageService,
        *,
        transport: Transport | None = None,
    ) -> None:
        self.store = store
        self.settings = settings
        self.catalog = catalog
        self.health = health
        self.router = router
        self.vault = vault
        self.usage = usage
        self.transport = transport

    def chat(self, user_id: str, request: ChatRequest, *, master_key: bytes) -> ChatResult:
        plan: RoutePlan = self.router.plan(user_id, request.model)
        if plan.is_empty:
            raise ByokError(ErrorCode.NO_AVAILABLE_PROVIDER)

        attempts: list[AttemptRecord] = []
        skipped: list[tuple[str, str]] = []
        last_error: UpstreamError | None = None
        all_rate_limited = True

        #: 按 Combo 分层流转：层内依次尝试，本层耗尽后进入下一层（F-095）。
        #: ``attempted`` 为全局尝试计数，受 ``max_attempts`` 上限约束。
        attempted = 0
        stop = False
        for layer in plan.layers or (tuple(plan.candidates),):
            if stop or attempted >= self.settings.max_attempts:
                break
            for candidate in layer:
                if stop or attempted >= self.settings.max_attempts:
                    break
                provider = self.catalog.provider(candidate.provider_id)
                if provider is None:
                    skipped.append((candidate.provider_id, "厂商不在目录中"))
                    continue
                if not self.health.available(candidate.provider_id):
                    skipped.append((candidate.provider_id, "熔断中"))
                    continue
                key_id = candidate.key_id
                key_record = next(
                    (k for k in self.store.keys.all() if k.id == key_id), None
                )
                if key_record is None:
                    skipped.append((candidate.provider_id, "无可用密钥记录"))
                    continue

                api_key = self.vault.decrypt_key(key_record, master_key)
                base_url = key_record.base_url or provider.base_url
                adapter = get_adapter(ProviderProtocol(key_record.protocol))
                started = time.perf_counter()
                attempted += 1
                try:
                    http_request: HttpRequest = adapter.build_request(
                        request, base_url=base_url, model=candidate.model_id, api_key=api_key
                    )
                    if self.transport is None:
                        raise UpstreamError(ErrorCode.NO_AVAILABLE_PROVIDER.default_message)
                    response: HttpResponse = self.transport.send(
                        http_request, timeout=self.settings.timeout_seconds
                    )
                    parsed: ChatResponse = adapter.parse_response(
                        response, provider_id=candidate.provider_id
                    )
                except UpstreamError as exc:
                    latency_ms = (time.perf_counter() - started) * 1000
                    self.health.record_failure(candidate.provider_id, status_code=exc.status_code)
                    attempts.append(_attempt(candidate, exc.status_code, exc.message, latency_ms))
                    last_error = exc
                    if exc.status_code != 429:
                        all_rate_limited = False
                    retryable = exc.retryable and (
                        exc.status_code is None
                        or exc.status_code in self.settings.failover_status_codes
                    )
                    if retryable:
                        skipped.append((candidate.provider_id, f"{exc.status_code} 触发切换"))
                        continue
                    #: 不可重试的错误（400/401/403/404/422…）不再流转后续层
                    stop = True
                    break
                finally:
                    api_key = ""  # 缩短明文生命周期

                latency_ms = (time.perf_counter() - started) * 1000
                self.health.record_success(candidate.provider_id, latency_ms=latency_ms)
                attempts.append(_attempt(candidate, 200, "", latency_ms))
                index = attempted - 1
                self.usage.record(
                    user_id=user_id,
                    provider_id=candidate.provider_id,
                    model_id=candidate.model_id,
                    alias=plan.alias,
                    prompt_tokens=parsed.usage.prompt_tokens,
                    completion_tokens=parsed.usage.completion_tokens,
                    status=CallStatus.FAILOVER if index else CallStatus.SUCCESS,
                    latency_ms=latency_ms,
                    failover_count=index,
                )
                decision = self.router.decision(plan).model_copy(
                    update={
                        "provider_id": candidate.provider_id,
                        "model_id": candidate.model_id,
                        "attempts": tuple(attempts),
                        "skipped": tuple(skipped),
                        "failover_used": index > 0,
                    }
                )
                return ChatResult(parsed, decision, index)

        if all_rate_limited and attempts:
            raise UpstreamError(
                ErrorCode.ALL_PROVIDERS_RATE_LIMITED.default_message, status_code=429
            )
        if last_error is not None:
            #: 保留原始错误码（如 ``UNSUPPORTED_FEATURE`` 422 / ``UPSTREAM_AUTH_ERROR`` 401），
            #: 避免统一重包装时被改写成 502 而丢失语义。
            last_error.retryable = False
            raise last_error
        raise ByokError(ErrorCode.NO_AVAILABLE_PROVIDER)


def _attempt(candidate, status_code, message, latency_ms) -> AttemptRecord:
    return AttemptRecord(
        provider_id=candidate.provider_id,
        model_id=candidate.model_id,
        status_code=status_code,
        error=redact(message),
        latency_ms=latency_ms,
    )


__all__ = ["ChatResult", "ChatService"]
