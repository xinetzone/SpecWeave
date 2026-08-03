"""ModelProvider 测试用例：验证 LocalProvider 固定延迟注入功能。

对应 `docs/p1-latency-roadmap.md` §3.1 模型适配层设计：
- 支持注入固定延迟（latency_ms）供压测可控复现
- 延迟量测通过计时包装实现

测试目标：
1. 注入固定延迟后，get_latency_ms() 应 >= 注入值
2. 默认无延迟时，调用应快速返回
3. 返回内容正常且来源可区分
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from model_provider import LocalProvider, RemoteProvider, build_default_provider


class TestLocalProviderLatency(unittest.TestCase):
    """验证 LocalProvider 固定延迟注入功能。"""

    def test_injected_latency_is_effective(self):
        """注入 50ms 延迟后，get_latency_ms() 应 >= 50ms。"""
        provider = LocalProvider(latency_ms=50)
        provider.invoke("local-model", "处理敏感票据")
        self.assertGreaterEqual(provider.get_latency_ms(), 50.0)

    def test_zero_latency_is_fast(self):
        """默认无延迟时，调用应快速返回（<50ms）。"""
        provider = LocalProvider()
        start = time.perf_counter()
        provider.invoke("local-model", "普通任务")
        elapsed = (time.perf_counter() - start) * 1000.0
        self.assertLess(elapsed, 50.0)
        self.assertLess(provider.get_latency_ms(), 50.0)

    def test_latency_accuracy_within_tolerance(self):
        """注入值应被准确反映（允许 ±20% 计时容差）。"""
        provider = LocalProvider(latency_ms=100)
        provider.invoke("local-model", "任务")
        measured = provider.get_latency_ms()
        self.assertGreaterEqual(measured, 100.0)
        self.assertLess(measured, 100.0 * 1.2 + 20.0)  # 100~140ms 容差

    def test_response_content(self):
        """返回内容应包含模型名与来源前缀。"""
        provider = LocalProvider(response_prefix="[mock/loc]")
        result = provider.invoke("local-model", "处理敏感票据")
        self.assertIn("[mock/loc]", result)
        self.assertIn("local-model", result)

    def test_default_provider_builds_local(self):
        """build_default_provider('local') 应返回 LocalProvider。"""
        provider = build_default_provider("local")
        self.assertIsInstance(provider, LocalProvider)


class TestRemoteProviderJitter(unittest.TestCase):
    """验证 RemoteProvider 模拟真实网络延迟（含抖动）。"""

    def test_jitter_latency_within_range(self):
        """200ms 基准 + 50ms 抖动，实际延迟应落在 [150, 250]ms 容差区间。"""
        provider = RemoteProvider("http://localhost:8000", latency_ms=200, jitter_ms=50)
        lats = []
        for _ in range(8):
            provider.invoke("strong-model", "任务")
            lats.append(provider.get_latency_ms())
        # 抖动范围 [150, 250]ms，允许计时容差 ±20ms
        self.assertGreaterEqual(min(lats), 150.0 - 20.0)
        self.assertLessEqual(max(lats), 250.0 + 20.0)
        # 均值应接近基准 200ms
        self.assertLess(sum(lats) / len(lats), 260.0)

    def test_no_jitter_uses_fixed_latency(self):
        """无抖动时，延迟应稳定接近基准值。"""
        provider = RemoteProvider("http://localhost:8000", latency_ms=100)
        provider.invoke("strong-model", "任务")
        self.assertGreaterEqual(provider.get_latency_ms(), 100.0)
        self.assertLess(provider.get_latency_ms(), 120.0)

    def test_default_provider_builds_remote_with_jitter(self):
        """build_default_provider('remote', jitter_ms=...) 应透传 jitter 参数。"""
        provider = build_default_provider("remote", latency_ms=200, jitter_ms=50)
        self.assertIsInstance(provider, RemoteProvider)
        self.assertEqual(provider._jitter_ms, 50)


if __name__ == "__main__":
    unittest.main()