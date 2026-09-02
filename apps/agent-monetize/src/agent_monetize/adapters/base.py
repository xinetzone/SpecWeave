"""真实 API 适配器协议与合规守卫。

- 默认关闭：真实适配器仅在 `enable_real=true` 且行为被用户显式加入
  `compliance.confirmed_behaviors` 时才启用（对应公理 A5：信任是通用货币，
  真实对外行为必须有人工可审计的确认）。
- 本协议仅描述「上报」等非资金流转操作；本平台不接入任何真实资金流转。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class RealAdapterProtocol(Protocol):
    """真实适配器协议：任何真实 API 通道适配器必须实现 send()。"""

    name: str
    endpoint: str
    requires_real_confirmation: bool

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        """向外部 API 发送负载并返回响应（不含真实资金流转）。"""
        ...


@dataclass(slots=True)
class AdapterGuardResult:
    """真实适配器启用守卫结果。"""

    allowed: bool
    reason: str = ""
    adapter: RealAdapterProtocol | None = None


class AdapterGuard:
    """真实适配器启用守卫：enable_real + 合规确认双条件。"""

    def __init__(self, confirmed_behaviors: list[str] | None = None) -> None:
        self.confirmed_behaviors: set[str] = set(confirmed_behaviors or [])

    def allow(
        self,
        adapter: RealAdapterProtocol,
        *,
        enable_real: bool = False,
        behavior: str | None = None,
    ) -> AdapterGuardResult:
        """判定是否允许真实发送。

        条件：enable_real=True 且（behavior 为空 或 behavior 已确认）。
        """
        if not enable_real:
            return AdapterGuardResult(
                allowed=False, adapter=adapter, reason="enable_real 未开启，真实通道关闭"
            )
        if adapter.requires_real_confirmation:
            if behavior and behavior not in self.confirmed_behaviors:
                return AdapterGuardResult(
                    allowed=False,
                    adapter=adapter,
                    reason=(
                        f"行为「{behavior}」未获得用户显式合规确认，"
                        f"需加入 compliance.confirmed_behaviors 后启用"
                    ),
                )
        return AdapterGuardResult(
            allowed=True, adapter=adapter, reason="合规确认已通过，真实通道启用"
        )


class HttpJsonReportAdapter:
    """示例真实适配器：REST JSON 上报（不含真实资金流转）。

    默认使用沙箱地址；仅当 enable_real=true 且行为已确认时才实际发送。
    使用 urllib 而非 requests，零第三方依赖。
    """

    name = "rest_report"
    endpoint: str = "https://sandbox.example.invalid/report"
    requires_real_confirmation = True

    def __init__(self, endpoint: str | None = None, timeout: float = 5.0) -> None:
        if endpoint:
            self.endpoint = endpoint
        self.timeout = timeout

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        import json
        import urllib.request

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(  # noqa: S310 - 沙箱适配器，默认 .invalid 地址不联网
            self.endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
            body = resp.read().decode("utf-8")
        return {"status": resp.status, "body": body[:500]}


class NoopSandboxAdapter:
    """沙箱空适配器：不联网，仅记录（作为真实适配器的沙箱对照）。"""

    name = "rest_report"
    endpoint: str = "sandbox://noop"
    requires_real_confirmation = True

    def __init__(self, behavior: str = "sandbox-report") -> None:
        self.behavior = behavior

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        logger.info("沙箱适配器（不联网）：%s payload=%s", self.behavior, payload)
        return {"status": 200, "body": "sandbox-noop", "sandbox": True}


def build_report_adapter(
    endpoint: str | None = None,
    *,
    enable_real: bool,
    behavior: str,
    confirmed_behaviors: list[str] | None = None,
) -> tuple[RealAdapterProtocol, AdapterGuardResult]:
    """构建上报适配器（真实 HttpJsonReportAdapter 或沙箱对照），并给出启用守卫判定。"""
    guard = AdapterGuard(confirmed_behaviors)
    adapter: RealAdapterProtocol
    if enable_real:
        adapter = HttpJsonReportAdapter(endpoint=endpoint)
    else:
        adapter = NoopSandboxAdapter(behavior=behavior)
    verdict = guard.allow(adapter, enable_real=enable_real, behavior=behavior)
    return adapter, verdict
