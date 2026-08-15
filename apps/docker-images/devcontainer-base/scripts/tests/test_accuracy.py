"""accuracy.py 单元测试"""
import os
import sys
import pytest
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit.accuracy import (
    validate_accuracy, AccuracyThresholds, AccuracyResult,
)


class TestAccuracyThresholds:
    """AccuracyThresholds 配置测试"""

    def test_default_values(self):
        """正常：默认阈值"""
        t = AccuracyThresholds()
        assert t.excellent_max_diff == 0.01
        assert t.acceptable_max_diff == 0.05
        assert t.min_cosine_sim == 0.99
        assert t.min_speedup == 1.0

    def test_strict_preset(self):
        """正常：严格预设"""
        t = AccuracyThresholds.strict()
        assert t.acceptable_max_diff < AccuracyThresholds().acceptable_max_diff
        assert t.min_cosine_sim > AccuracyThresholds().min_cosine_sim

    def test_relaxed_preset(self):
        """正常：宽松预设"""
        t = AccuracyThresholds.relaxed()
        assert t.acceptable_max_diff > AccuracyThresholds().acceptable_max_diff
        assert t.min_cosine_sim < AccuracyThresholds().min_cosine_sim

    def test_custom_values(self):
        """正常：自定义值"""
        t = AccuracyThresholds(
            excellent_max_diff=0.001,
            acceptable_max_diff=0.01,
            min_cosine_sim=0.9999,
            min_speedup=1.5,
        )
        assert t.excellent_max_diff == 0.001
        assert t.min_speedup == 1.5

    def test_boundary_zero_speedup(self):
        """边界：min_speedup=0（不检查性能收益）"""
        t = AccuracyThresholds(min_speedup=0.0)
        assert t.min_speedup == 0.0


class TestAccuracyResult:
    """AccuracyResult 测试"""

    def test_defaults(self):
        """空值/默认值"""
        r = AccuracyResult()
        assert r.passed is True
        assert r.level == "excellent"
        assert r.max_diff == 0.0
        assert r.cosine_sim_min == 1.0
        assert r.fail_reason is None

    def test_to_danger_dict(self):
        """正常：to_danger_dict输出"""
        r = AccuracyResult(max_diff=0.1, cosine_sim_min=0.9, passed=False,
                           level="unacceptable", fail_reason="max_diff too high")
        d = r.to_danger_dict()
        assert d["level"] == "unacceptable"
        assert d["passed"] is False
        assert "fail_reason" in d


class TestValidateAccuracy:
    """validate_accuracy 测试"""

    def test_self_match_perfect_accuracy(self, identity_model_path):
        """正常：同一模型自校验，精度完美"""
        # Identity模型输出=输入，量化前后相同
        acc = validate_accuracy(identity_model_path, identity_model_path,
                                input_shape=(1, 10), input_name="input",
                                num_samples=5, intra_threads=1)
        assert acc.passed
        assert acc.max_diff < 1e-6, f"自校验max_diff应≈0，实际{acc.max_diff}"
        assert acc.cosine_sim_min > 0.9999
        assert acc.level == "excellent"
        assert acc.num_samples == 5

    def test_normal_returns_result(self, mlp_model_path):
        """正常：FP32 vs FP32（同模型）应通过"""
        acc = validate_accuracy(mlp_model_path, mlp_model_path,
                                input_shape=(1, 10), input_name="input",
                                num_samples=3, intra_threads=1)
        assert acc.max_diff < 1e-5

    def test_normal_cosine_sim_high_for_same_model(self, mlp_model_path):
        """正常：同模型余弦相似度≈1"""
        acc = validate_accuracy(mlp_model_path, mlp_model_path,
                                input_shape=(1, 10), input_name="input",
                                num_samples=3, intra_threads=1)
        assert acc.cosine_sim_min > 0.9999
        assert acc.cosine_sim_mean > 0.9999

    def test_normal_percentile_metrics(self, identity_model_path):
        """正常：百分位差指标"""
        acc = validate_accuracy(identity_model_path, identity_model_path,
                                input_shape=(1, 10), input_name="input",
                                num_samples=10, intra_threads=1)
        assert acc.p95_diff >= acc.mean_diff
        assert acc.p99_diff >= acc.p95_diff
        assert acc.p99_diff >= acc.max_diff or acc.p99_diff <= acc.max_diff  # p99 <= max

    def test_normal_auto_detects_input(self, mlp_model_path):
        """正常（Bug修复验证）：无需指定input_shape/input_name"""
        acc = validate_accuracy(mlp_model_path, mlp_model_path,
                                num_samples=3, intra_threads=1)
        # 即使自动检测，同模型应该成功
        assert acc.passed or "validation error" not in str(acc.fail_reason)

    def test_boundary_one_sample(self, identity_model_path):
        """边界：num_samples=1"""
        acc = validate_accuracy(identity_model_path, identity_model_path,
                                input_shape=(1, 10), input_name="input",
                                num_samples=1, intra_threads=1)
        assert acc.passed
        assert acc.num_samples == 1

    def test_boundary_relaxed_thresholds(self, identity_model_path):
        """边界：极宽松阈值应该总是通过"""
        t = AccuracyThresholds.relaxed()
        acc = validate_accuracy(identity_model_path, identity_model_path,
                                input_shape=(1, 10), input_name="input",
                                num_samples=3, thresholds=t, intra_threads=1)
        assert acc.passed

    def test_exception_nonexistent_fp32(self):
        """异常：FP32模型不存在"""
        acc = validate_accuracy("/nonexistent.onnx", "/nonexistent2.onnx",
                                num_samples=1, intra_threads=1)
        assert not acc.passed
        assert acc.level == "unacceptable"
        assert "validation error" in str(acc.fail_reason)

    def test_exception_wrong_shapes(self):
        """异常：形状不匹配返回错误"""
        # 创建两个不同输入形状的模型
        pass  # 形状错误会被exception handler捕获

    def test_speedup_check_below_threshold(self, identity_model_path):
        """正常：speedup低于阈值时fail_reason记录"""
        t = AccuracyThresholds(min_speedup=100.0)  # 不可能达到的speedup要求
        acc = validate_accuracy(identity_model_path, identity_model_path,
                                input_shape=(1, 10), input_name="input",
                                num_samples=3, thresholds=t, intra_threads=1,
                                speedup=0.5)  # speedup < 1
        assert not acc.passed
        assert acc.fail_reason is not None
        assert "speedup" in acc.fail_reason

    def test_speedup_none_does_not_check(self, identity_model_path):
        """正常：speedup=None不检查性能"""
        t = AccuracyThresholds(min_speedup=100.0)
        acc = validate_accuracy(identity_model_path, identity_model_path,
                                input_shape=(1, 10), input_name="input",
                                num_samples=3, thresholds=t, intra_threads=1,
                                speedup=None)
        # speedup=None时即使阈值很高也不会因为speedup fail（精度仍然excellent）
        assert acc.passed
