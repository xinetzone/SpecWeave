"""真实适配器协议 / 守卫 / 沙箱对照测试。"""

from __future__ import annotations

from agent_monetize.adapters.base import (
    AdapterGuard,
    HttpJsonReportAdapter,
    NoopSandboxAdapter,
    build_report_adapter,
)


class TestAdapterGuard:
    def test_blocked_when_real_disabled(self) -> None:
        guard = AdapterGuard()
        verdict = guard.allow(NoopSandboxAdapter(), enable_real=False, behavior="sandbox-report")
        assert not verdict.allowed

    def test_requires_confirmation(self) -> None:
        guard = AdapterGuard()
        verdict = guard.allow(HttpJsonReportAdapter(), enable_real=True, behavior="sandbox-report")
        assert not verdict.allowed

    def test_allowed_with_confirmation(self) -> None:
        guard = AdapterGuard(["sandbox-report"])
        verdict = guard.allow(HttpJsonReportAdapter(), enable_real=True, behavior="sandbox-report")
        assert verdict.allowed

    def test_confirmation_skipped_when_not_required(self) -> None:
        class NoConfirmAdapter:
            name = "nc"
            endpoint = "sandbox://nc"
            requires_real_confirmation = False

            def send(self, payload):  # type: ignore[no-untyped-def]
                return payload

        guard = AdapterGuard()
        verdict = guard.allow(NoConfirmAdapter(), enable_real=True, behavior="anything")
        assert verdict.allowed


class TestSandboxAdapter:
    def test_noop_sandbox_send(self) -> None:
        adapter = NoopSandboxAdapter()
        resp = adapter.send({"a": 1})
        assert resp["sandbox"] is True
        assert resp["status"] == 200


class TestBuildReportAdapter:
    def test_build_sandbox_when_real_disabled(self) -> None:
        adapter, verdict = build_report_adapter(enable_real=False, behavior="sandbox-report")
        assert isinstance(adapter, NoopSandboxAdapter)
        assert not verdict.allowed

    def test_build_real_without_confirmation(self) -> None:
        adapter, verdict = build_report_adapter(enable_real=True, behavior="sandbox-report")
        assert isinstance(adapter, HttpJsonReportAdapter)
        assert not verdict.allowed

    def test_build_real_with_confirmation(self) -> None:
        adapter, verdict = build_report_adapter(
            enable_real=True,
            behavior="sandbox-report",
            confirmed_behaviors=["sandbox-report"],
        )
        assert isinstance(adapter, HttpJsonReportAdapter)
        assert verdict.allowed
