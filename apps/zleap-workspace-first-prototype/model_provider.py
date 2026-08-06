"""ModelProvider 模块：模型适配层（P1 路线图 §3.1）。

对应 `docs/p1-latency-roadmap.md` §3.1 的模型适配层设计：
- 统一模型调用抽象，屏蔽供应商差异
- 支持延迟量测（计时包装 + 固定延迟注入，供压测脚本可控复现）
- Local / Remote 两种实现，后续可扩展更多供应商

职责：
1. 路由层只依赖 `ModelProvider` 抽象，不感知具体供应商
2. 延迟量测通过 `ModelProvider` 的计时包装实现，不侵入路由逻辑
3. 支持注入固定延迟（`latency_ms`）用于压测可控复现
"""

from __future__ import annotations

import logging
import random
import time
from collections import deque
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelProvider:
    """模型调用抽象基类。

    子类实现 `invoke` 方法，决定如何调用目标模型。
    提供 `get_latency_ms()` 报告最近一次调用的耗时（毫秒），
    供延迟量测体系读取。

    支持 P2 延迟预算（T1）：`p99_budget_ms` 设定 p99 延迟预算，
    通过 `record_latency_ms()` 记录样本、`p99_latency_ms()` 计算 p99、
    `is_within_budget()` 判定是否超预算，供路由层降级决策。
    """

    # 延迟样本窗口大小（用于 p99 计算）
    LATENCY_HISTORY_SIZE = 500

    def __init__(self) -> None:
        self._latency_history: deque = deque(maxlen=self.LATENCY_HISTORY_SIZE)
        self.p99_budget_ms: float = 0.0  # 0 表示未设预算

    # ---- 延迟预算（P2 T1） ----
    def set_p99_budget(self, budget_ms: float) -> None:
        """设置 p99 延迟预算（毫秒）。0 表示不设预算。"""
        self.p99_budget_ms = budget_ms

    def record_latency_ms(self, latency_ms: float) -> None:
        """记录一次调用延迟样本（供 p99 计算）。"""
        self._latency_history.append(latency_ms)

    def p99_latency_ms(self) -> float:
        """计算当前延迟样本的 p99（毫秒）。样本不足时返回最近一次延迟。"""
        if not self._latency_history:
            return 0.0
        s = sorted(self._latency_history)
        k = (len(s) - 1) * 0.99
        lo = int(k)
        hi = min(lo + 1, len(s) - 1)
        frac = k - lo
        return s[lo] * (1 - frac) + s[hi] * frac

    def is_within_budget(self) -> bool:
        """判断当前 p99 是否在预算内（未设预算视为通过）。"""
        if self.p99_budget_ms <= 0:
            return True
        return self.p99_latency_ms() <= self.p99_budget_ms

    def latency_samples(self) -> List[float]:
        """返回当前延迟样本列表。"""
        return list(self._latency_history)

    def invoke(self, model: str, prompt: str, **kwargs: Any) -> str:
        """调用指定模型，返回生成文本。

        Args:
            model: 目标模型名（由路由层决定）
            prompt: 输入提示词
            **kwargs: 供应商相关参数（温度、max_tokens 等）

        Returns:
            模型生成的文本。
        """
        raise NotImplementedError

    def get_latency_ms(self) -> float:
        """返回最近一次 `invoke` 调用的耗时（毫秒）。"""
        raise NotImplementedError


class _TimedProviderMixin:
    """计时包装 Mixin：记录最近一次 `invoke` 的耗时。

    用于延迟量测，不侵入调用逻辑。
    自动将每次调用耗时记入延迟历史（供 p99 预算计算）。
    """

    def __init__(self) -> None:
        self._last_latency_ms: float = 0.0

    def get_latency_ms(self) -> float:
        return self._last_latency_ms

    def _measure(self, fn: Any) -> str:
        """执行 fn 并记录耗时（毫秒）。"""
        start = time.perf_counter()
        result = fn()
        latency = (time.perf_counter() - start) * 1000.0
        self._last_latency_ms = latency
        # 记录到历史，供 p99 预算计算（若基类已初始化）
        if hasattr(self, "_latency_history"):
            self.record_latency_ms(latency)
        return result


class LocalProvider(_TimedProviderMixin, ModelProvider):
    """本地模型（mock 实现）。

    支持注入固定延迟（`latency_ms`）模拟推理耗时，供压测脚本完全可控复现。
    不接入真实模型，仅返回 mock 文本。

    Args:
        latency_ms: 模拟推理延迟（毫秒），默认 0（无延迟）
        response_prefix: mock 响应前缀（便于区分来源）
    """

    def __init__(self, latency_ms: int = 0, response_prefix: str = "[mock/loc]") -> None:
        _TimedProviderMixin.__init__(self)
        ModelProvider.__init__(self)
        self._latency_ms = latency_ms
        self._response_prefix = response_prefix

    def invoke(self, model: str, prompt: str, **kwargs: Any) -> str:
        """模拟本地模型调用：注入延迟后返回固定 mock 文本。"""

        def _call() -> str:
            if self._latency_ms > 0:
                time.sleep(self._latency_ms / 1000.0)
            return f"{self._response_prefix} {model} 收到: {prompt[:20]}"

        return self._measure(_call)


class RemoteProvider(_TimedProviderMixin, ModelProvider):
    """远程 LLM API 提供者。

    真实接入时替换 `_call` 内的 HTTP 请求即可（当前为 mock 占位），
    保持路由层与供应商解耦。

    支持模拟真实网络延迟：`latency_ms` 为基准延迟，`jitter_ms` 为抖动幅度，
    每次调用实际延迟 = 基准 + 均匀随机抖动（[−jitter, +jitter]），
    模拟真实网络的波动特性（如 200ms 基准 ± 50ms 抖动）。

    Args:
        base_url: 远程模型服务地址
        api_key: API 密钥（默认空）
        timeout: 请求超时（秒）
        latency_ms: 基准网络延迟（毫秒），默认 0
        jitter_ms: 抖动幅度（毫秒），默认 0（无波动）
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        timeout: float = 30.0,
        latency_ms: int = 0,
        jitter_ms: int = 0,
    ) -> None:
        _TimedProviderMixin.__init__(self)
        ModelProvider.__init__(self)
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._latency_ms = latency_ms
        self._jitter_ms = jitter_ms

    def _simulate_delay(self) -> None:
        """模拟一次网络延迟（含抖动）。"""
        if self._latency_ms <= 0:
            return
        if self._jitter_ms > 0:
            # 实际延迟 = 基准 + 均匀随机抖动（[−jitter, +jitter]），下限为 0
            delay = self._latency_ms + random.uniform(-self._jitter_ms, self._jitter_ms)
            delay = max(0.0, delay)
        else:
            delay = float(self._latency_ms)
        time.sleep(delay / 1000.0)

    def invoke(self, model: str, prompt: str, **kwargs: Any) -> str:
        """调用远程模型。

        当前为 mock 占位（注入波动延迟 + 返回固定文本），
        真实接入时在此处发起 HTTP 请求即可。
        """

        def _call() -> str:
            self._simulate_delay()
            logger.info(
                "[RemoteProvider] 调用 model=%s prompt_length=%d",
                model, len(prompt),
            )
            # TODO(P2): 替换为真实 HTTP 调用，如 requests.post(f"{base_url}/v1/chat")
            return f"[mock/remote] {model} 响应（base_url={self.base_url}）"

        return self._measure(_call)


def build_default_provider(
    provider_type: str = "local",
    latency_ms: int = 0,
    **kwargs: Any,
) -> ModelProvider:
    """构建默认模型提供者。

    Args:
        provider_type: "local"（本地 mock）或 "remote"（远程）
        latency_ms: 模拟延迟（毫秒）
        **kwargs: 透传给具体实现的参数

    Returns:
        配置好的 ModelProvider。
    """
    if provider_type == "remote":
        return RemoteProvider(
            base_url=kwargs.get("base_url", "http://localhost:8000"),
            api_key=kwargs.get("api_key", ""),
            timeout=kwargs.get("timeout", 30.0),
            latency_ms=latency_ms,
            jitter_ms=kwargs.get("jitter_ms", 0),
        )
    return LocalProvider(
        latency_ms=latency_ms,
        response_prefix=kwargs.get("response_prefix", "[mock/loc]"),
    )