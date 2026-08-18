"""reporting.py 单元测试"""
import os
import sys
import json
import tempfile
import pytest
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit.reporting import (
    build_report, parse_report, format_summary,
    format_strategy_chain, format_batch_summary,
)
from onnx_quantize_kit.quantize import QuantizationResult
from onnx_quantize_kit.benchmark import BenchmarkResult
from onnx_quantize_kit.accuracy import AccuracyResult, AccuracyThresholds


def _make_success_result(**kwargs):
    """创建一个成功的QuantizationResult用于测试"""
    defaults = dict(
        success=True,
        output_path="/tmp/out.onnx",
        strategy_used="dynamic",
        model_type="mlp",
        speedup=2.5,
        size_ratio=0.45,
        fallback_triggered=False,
        fallback_reason="",
        error=None,
        all_attempts=[{"strategy": "dynamic", "success": True, "speedup": 2.5, "max_diff": 0.001}],
    )
    defaults.update(kwargs)
    return QuantizationResult(**defaults)


def _make_fail_result(**kwargs):
    """创建一个失败的QuantizationResult用于测试"""
    return QuantizationResult(
        success=False,
        output_path="",
        strategy_used="",
        model_type="",
        speedup=0,
        size_ratio=0,
        fallback_triggered=True,
        fallback_reason="Primary strategy failed, fell back",
        error="All strategies failed",
        all_attempts=[
            {"strategy": "static_qdq", "success": False, "error": "max_diff too high"},
            {"strategy": "dynamic", "success": False, "error": "benchmark failed"},
        ],
        **kwargs
    )


class TestBuildReport:
    """build_report 测试"""

    def test_normal_success_result(self):
        """正常：成功结果生成PASS报告"""
        r = _make_success_result()
        report = build_report(r)
        assert report["status"] == "PASS"
        assert report["strategy_used"] == "dynamic"
        assert report["speedup"] == 2.5
        assert report["size_ratio"] == 0.45
        assert report["fallback_triggered"] is False

    def test_normal_fail_result(self):
        """正常：失败结果生成FAIL报告"""
        r = _make_fail_result()
        report = build_report(r)
        assert report["status"] == "FAIL"
        assert report["fallback_triggered"] is True
        assert "error" in report

    def test_normal_with_elapsed(self):
        """正常：包含耗时"""
        r = _make_success_result()
        report = build_report(r, elapsed=12.345)
        assert report["elapsed_seconds"] == 12.35  # rounded

    def test_normal_with_thresholds(self):
        """正常：包含阈值信息"""
        r = _make_success_result()
        t = AccuracyThresholds.strict()
        report = build_report(r, thresholds=t)
        assert "thresholds" in report
        assert report["thresholds"]["acceptable_max_diff"] == t.acceptable_max_diff

    def test_normal_with_model_path(self):
        """正常：包含模型路径"""
        r = _make_success_result()
        report = build_report(r, model_path="/models/my_model.onnx")
        assert report["model"] == "my_model.onnx"
        assert report["model_path"] == "/models/my_model.onnx"

    def test_normal_with_performance(self):
        """正常：包含性能指标"""
        r = _make_success_result()
        fp32_perf = BenchmarkResult(avg_ms=10.0, size_kb=1000.0)
        fp32_perf.error = None  # success property: error=None → True
        quant_perf = BenchmarkResult(avg_ms=4.0, p50_ms=3.9, p95_ms=4.5, p99_ms=5.0,
                                     throughput_fps=250.0, size_kb=450.0)
        quant_perf.error = None
        r.fp32_performance = fp32_perf
        r.performance = quant_perf
        report = build_report(r)
        assert "fp32" in report
        assert "quantized" in report
        assert report["quantized"]["avg_ms"] == 4.0
        assert report["fp32"]["size_kb"] == 1000.0

    def test_normal_with_accuracy(self):
        """正常：包含精度指标"""
        r = _make_success_result()
        acc = AccuracyResult(max_diff=0.005, cosine_sim_min=0.999, passed=True, level="excellent")
        r.accuracy = acc
        report = build_report(r)
        assert "accuracy" in report
        assert report["accuracy"]["passed"] is True
        assert report["accuracy"]["level"] == "excellent"

    def test_normal_with_fail_reason(self):
        """正常：失败时包含fail_reason"""
        r = _make_success_result()
        acc = AccuracyResult(max_diff=0.1, passed=False, level="unacceptable",
                             fail_reason="max_diff too high")
        r.accuracy = acc
        r.success = False
        report = build_report(r)
        assert "fail_reason" in report["accuracy"]

    def test_empty_model_path(self):
        """空值：空模型路径"""
        r = _make_success_result()
        report = build_report(r, model_path="")
        assert report["model"] == ""
        assert report["model_path"] == ""

    def test_zero_speedup(self):
        """边界：speedup=0"""
        r = _make_success_result(speedup=0.0, size_ratio=0.0)
        report = build_report(r)
        assert report["speedup"] == 0


class TestParseReport:
    """parse_report 测试"""

    def test_normal_from_dict(self):
        """正常：从dict解析"""
        data = {"status": "PASS", "strategy_used": "dynamic"}
        result = parse_report(data)
        assert result["status"] == "PASS"

    def test_normal_from_json_file(self, tmp_path):
        """正常：从JSON文件解析"""
        data = {"status": "PASS", "strategy_used": "fp16"}
        path = tmp_path / "report.json"
        path.write_text(json.dumps(data))
        result = parse_report(str(path))
        assert result["status"] == "PASS"
        assert result["strategy_used"] == "fp16"

    def test_exception_file_not_found(self):
        """异常：文件不存在"""
        with pytest.raises(FileNotFoundError):
            parse_report("/nonexistent/report.json")

    def test_exception_missing_required_fields(self):
        """异常：缺少必要字段"""
        with pytest.raises(ValueError, match="missing required fields"):
            parse_report({"status": "PASS"})  # missing strategy_used

    def test_exception_invalid_status(self):
        """异常：status值非法"""
        with pytest.raises(ValueError, match="status must be PASS/FAIL"):
            parse_report({"status": "MAYBE", "strategy_used": "dynamic"})

    def test_exception_invalid_json(self, tmp_path):
        """异常：JSON格式错误"""
        path = tmp_path / "bad.json"
        path.write_text("not valid json{{{")
        with pytest.raises(Exception):
            parse_report(str(path))


class TestFormatSummary:
    """format_summary 测试"""

    def test_normal_pass_output(self):
        """正常：PASS结果格式化"""
        report = {
            "status": "PASS",
            "strategy_used": "dynamic",
            "model": "test.onnx",
            "speedup": 2.5,
            "size_ratio": 0.45,
            "accuracy": {
                "level": "excellent",
                "max_diff": 0.001,
                "cosine_sim_min": 0.9999,
            },
        }
        text = format_summary(report, color=False)
        assert "PASS" in text
        assert "Dynamic" in text or "dynamic" in text
        assert "2.50x" in text

    def test_normal_fail_output(self):
        """正常：FAIL结果格式化"""
        report = {
            "status": "FAIL",
            "strategy_used": "static_qdq",
            "fallback_triggered": True,
            "fallback_reason": "precision too low",
            "error": "max_diff exceeded",
        }
        text = format_summary(report, color=False)
        assert "FAIL" in text
        assert "Fallback" in text or "fallback" in text
        assert "Error" in text or "error" in text

    def test_normal_no_color(self):
        """正常：color=False无ANSI转义"""
        report = {"status": "PASS", "strategy_used": "dynamic", "speedup": 2.0}
        text = format_summary(report, color=False)
        assert "\033[" not in text

    def test_boundary_minimal_report(self):
        """边界：最小报告（只有必填字段）"""
        report = {"status": "PASS", "strategy_used": "fp16"}
        text = format_summary(report, color=False)
        assert "PASS" in text
        assert len(text) > 0


class TestFormatStrategyChain:
    """format_strategy_chain 测试"""

    def test_normal_single_success(self):
        """正常：单个成功策略"""
        attempts = [{"strategy": "dynamic", "success": True, "max_diff": 0.001, "speedup": 2.5}]
        text = format_strategy_chain(attempts, color=False)
        assert "PRIMARY" in text
        assert "Dynamic" in text
        assert "2.50x" in text

    def test_normal_with_fallback(self):
        """正常：带fallback链"""
        attempts = [
            {"strategy": "static_qdq", "success": False, "error": "max_diff too high"},
            {"strategy": "dynamic", "success": True, "max_diff": 0.01, "speedup": 2.0},
        ]
        text = format_strategy_chain(attempts, color=False)
        assert "FALLBACK-1" in text
        # 策略名被翻译为标签：static_qdq → "Static QDQ"
        assert "Static QDQ" in text
        assert "Dynamic" in text
        assert "PRIMARY" in text

    def test_empty_attempts(self):
        """边界：空attempts列表"""
        text = format_strategy_chain([], color=False)
        assert text == ""


class TestFormatBatchSummary:
    """format_batch_summary 测试"""

    def test_normal_multiple_models(self):
        """正常：多个模型汇总"""
        reports = [
            {"status": "PASS", "strategy_used": "dynamic", "model_type": "mlp",
             "model": "a.onnx", "speedup": 2.5, "accuracy": {"max_diff": 0.001}},
            {"status": "PASS", "strategy_used": "static_qdq", "model_type": "cnn",
             "model": "b.onnx", "speedup": 1.2, "accuracy": {"max_diff": 0.01}},
            {"status": "FAIL", "strategy_used": "", "model_type": "",
             "model": "c.onnx", "speedup": 0, "accuracy": {}},
        ]
        text = format_batch_summary(reports, color=False)
        assert "Batch Quantization Summary" in text
        assert "Passed: 2" in text
        assert "Failed: 1" in text
        assert "a.onnx" in text
        assert "b.onnx" in text
        assert "c.onnx" in text

    def test_boundary_empty_batch(self):
        """边界：空批次"""
        text = format_batch_summary([], color=False)
        assert "Total: 0" in text
        assert "Passed: 0" in text
        assert "Failed: 0" in text

    def test_normal_all_pass(self):
        """正常：全部通过"""
        reports = [
            {"status": "PASS", "strategy_used": "fp16", "model_type": "transformer",
             "model": "t.onnx", "speedup": 1.0, "accuracy": {"max_diff": 0}},
        ]
        text = format_batch_summary(reports, color=False)
        assert "Failed: 0" in text
