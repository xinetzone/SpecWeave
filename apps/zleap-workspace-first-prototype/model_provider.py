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
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ModelProvider:
    """模型调用抽象基类。

    子类实现 `invoke` 方法，决定如何调用目标模型。
    提供 `get_latency_ms()` 报告最近一次调用的耗时（毫秒），
    供延迟量测体系读取。
    """

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
    """

    def __init__(self) -> None:
        self._last_latency_ms: float = 0.0

    def get_latency_ms(self) -> float:
        return self._last_latency_ms

    def _measure(self, fn: Any) -> str:
        """执行 fn 并记录耗时（毫秒）。"""
        start = time.perf_counter()
        result = fn()
        self._last_latency_ms = (time.perf_counter() - start) * 1000.0
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

    Args:
        base_url: 远程模型服务地址
        api_key: API 密钥（默认空）
        timeout: 请求超时（秒）
        latency_ms: 模拟网络延迟（毫秒），默认 0
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        timeout: float = 30.0,
        latency_ms: int = 0,
    ) -> None:
        _TimedProviderMixin.__init__(self)
        ModelProvider.__init__(self)
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._latency_ms = latency_ms

    def invoke(self, model: str, prompt: str, **kwargs: Any) -> str:
        """调用远程模型。

        当前为 mock 占位（注入延迟 + 返回固定文本），
        真实接入时在此处发起 HTTP 请求即可。
        """

        def _call() -> str:
            if self._latency_ms > 0:
                time.sleep(self._latency_ms / 1000.0)
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
        )
    return LocalProvider(
        latency_ms=latency_ms,
        response_prefix=kwargs.get("response_prefix", "[mock/loc]"),
    )