"""用量服务：调用台账与「手填额度 − 已用 = 剩余」（源文档 F-081）。"""

import secrets
import time

from ..models import CallStatus, UsageRecord, UsageSummary
from ..storage import Store


class UsageService:
    def __init__(self, store: Store) -> None:
        self.store = store

    def record(
        self,
        *,
        user_id: str,
        provider_id: str,
        model_id: str,
        alias: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        status: CallStatus = CallStatus.SUCCESS,
        latency_ms: float = 0.0,
        failover_count: int = 0,
    ) -> UsageRecord:
        row = UsageRecord(
            id=secrets.token_hex(8),
            user_id=user_id,
            provider_id=provider_id,
            model_id=model_id,
            alias=alias,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            status=status,
            latency_ms=latency_ms,
            failover_count=failover_count,
            created_at=time.time(),
        )
        self.store.usage.add(row)
        self._consume_quota(user_id, provider_id, row.total_tokens)
        return row

    def _consume_quota(self, user_id: str, provider_id: str, tokens: int) -> None:
        key = self.store.keys.find(
            lambda k: k.user_id == user_id and k.provider_id == provider_id
        )
        if key is None or key.quota_total is None:
            return
        used = key.quota_used + tokens
        update = {"quota_used": used, "updated_at": time.time()}
        if used >= key.quota_total:
            from ..models import KeyStatus

            update["status"] = KeyStatus.QUOTA_EXHAUSTED
        self.store.keys.replace(lambda k: k.id == key.id, key.model_copy(update=update))

    def summaries(self, user_id: str) -> tuple[UsageSummary, ...]:
        summaries: dict[str, UsageSummary] = {}
        for row in self.store.usage.where(lambda u: u.user_id == user_id):
            current = summaries.get(row.provider_id)
            if current is None:
                current = UsageSummary(provider_id=row.provider_id)
            summaries[row.provider_id] = current.model_copy(
                update={
                    "calls": current.calls + 1,
                    "total_tokens": current.total_tokens + row.total_tokens,
                }
            )
        for key in self.store.keys.where(lambda k: k.user_id == user_id):
            current = summaries.get(
                key.provider_id, UsageSummary(provider_id=key.provider_id)
            )
            summaries[key.provider_id] = current.model_copy(
                update={"quota_total": key.quota_total, "quota_used": key.quota_used}
            )
        return tuple(summaries.values())

    def records(self, user_id: str | None = None) -> tuple[UsageRecord, ...]:
        if user_id is None:
            return tuple(self.store.usage.all())
        return tuple(self.store.usage.where(lambda u: u.user_id == user_id))

    def total_calls(self, user_id: str | None = None) -> int:
        return len(self.records(user_id))


__all__ = ["UsageService"]
