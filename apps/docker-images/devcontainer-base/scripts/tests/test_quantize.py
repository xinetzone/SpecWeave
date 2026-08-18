"""quantize.py 单元测试 — 重点验证Bug #1/#2/#3修复"""
import os
import sys
import tempfile
import pytest
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit import (
    quantize_fp16, quantize_dynamic_simple,
    quantize_static_qdq, detect_input_info,
    QuantizationConfig, QuantizationResult,
    AccuracyThresholds,
)
from onnx_quantize_kit.quantize import (
    _safe_get_input_shape, _detect_input_info, detect_input_info,
)


class TestSafeGetInputShape:
    """_safe_get_input_shape 在 quantize.py 中的版本（与benchmark统一）"""

    def test_dim_param_string_handled(self, mlp_model_path):
        """Bug #2验证：dim_param字符串不崩溃"""
        from onnx_quantize_kit.benchmark import create_session
        sess = create_session(mlp_model_path, intra_threads=1)
        inp = sess.get_inputs()[0]
        shape = _safe_get_input_shape(inp)
        assert isinstance(shape, tuple)
        assert all(isinstance(d, int) for d in shape)
        assert shape[0] == 1  # 动态batch -> 1


class TestDetectInputInfo:
    """detect_input_info 公共API测试（Bug #1修复引入的新API）"""

    def test_normal_detects_name_and_shape(self, mlp_model_path):
        """正常：检测MLP输入名称和形状"""
        name, shape = detect_input_info(mlp_model_path, intra_threads=1)
        assert name == "input"
        assert shape == (1, 10) or len(shape) == 2

    def test_normal_dynamic_batch_replaced(self, mlp_model_path):
        """Bug #2验证：动态batch维度被替换为1"""
        name, shape = detect_input_info(mlp_model_path, intra_threads=1)
        assert shape[0] == 1

    def test_normal_static_model(self, mlp_static_model_path):
        """正常：静态形状模型"""
        name, shape = detect_input_info(mlp_static_model_path, intra_threads=1)
        assert shape == (1, 10)

    def test_exception_nonexistent_file(self):
        """异常：不存在的文件"""
        with pytest.raises(Exception):
            detect_input_info("/nonexistent.onnx")

    def test_backward_compat_alias(self, mlp_model_path):
        """正常：_detect_input_info别名仍然可用"""
        name, shape = _detect_input_info(mlp_model_path, intra_threads=1)
        assert name == "input"


class TestQuantizeFp16:
    """quantize_fp16 便捷函数测试（Bug #1修复验证）"""

    def test_normal_runs_and_returns_result(self, mlp_model_path, tmp_path):
        """正常：FP16转换成功"""
        out = str(tmp_path / "mlp_fp16.onnx")
        result = quantize_fp16(mlp_model_path, out)
        assert isinstance(result, QuantizationResult)
        # 可能因onnxconverter-common未安装而失败，但不应崩溃
        if result.success:
            assert os.path.exists(out)
            assert result.strategy_used == "fp16"
            assert result.performance is not None
            assert result.performance.success
            assert result.size_ratio > 0
        else:
            assert "onnxconverter-common" in str(result.error) or "ImportError" in str(result.error)

    def test_normal_size_ratio_computed_without_extra_benchmark(self, mlp_model_path, tmp_path):
        """Bug #8验证：size_ratio直接通过文件大小计算，无需额外benchmark"""
        out = str(tmp_path / "mlp_fp16.onnx")
        result = quantize_fp16(mlp_model_path, out)
        if result.success:
            fp32_size = os.path.getsize(mlp_model_path) / 1024
            fp16_size = os.path.getsize(out) / 1024
            expected_ratio = fp16_size / fp32_size
            # size_ratio应接近文件大小比值（FP16权重几乎减半）
            assert abs(result.size_ratio - expected_ratio) < 0.1

    def test_normal_auto_detects_input_for_benchmark(self, small_mlp_path, tmp_path):
        """Bug #1验证：无需传入input_shape/input_name即可benchmark"""
        out = str(tmp_path / "small_fp16.onnx")
        result = quantize_fp16(small_mlp_path, out)
        if result.success:
            assert result.performance.success, f"benchmark应自动检测输入成功: {result.performance.error}"
            assert result.performance.avg_ms > 0

    def test_exception_invalid_model(self, tmp_path):
        """异常：无效模型"""
        bad = tmp_path / "bad.onnx"
        bad.write_bytes(b"corrupted")
        result = quantize_fp16(str(bad), str(tmp_path / "out.onnx"))
        assert not result.success
        assert result.error is not None

    def test_exception_nonexistent_input(self, tmp_path):
        """异常：输入文件不存在"""
        result = quantize_fp16("/nonexistent.onnx", str(tmp_path / "out.onnx"))
        assert not result.success


class TestQuantizeDynamicSimple:
    """quantize_dynamic_simple 便捷函数测试（Bug #1修复验证）"""

    def test_normal_runs_successfully(self, mlp_model_path, tmp_path):
        """正常：动态量化成功"""
        out = str(tmp_path / "mlp_dyn.onnx")
        result = quantize_dynamic_simple(mlp_model_path, out)
        assert result.success, f"动态量化失败: {result.error}"
        assert os.path.exists(out)
        assert result.strategy_used == "dynamic"
        assert result.performance is not None
        assert result.performance.success, f"benchmark失败: {result.performance.error}"
        assert result.size_ratio > 0

    def test_normal_size_ratio_reasonable(self, mlp_model_path, tmp_path):
        """正常：动态量化模型通常比FP32小"""
        out = str(tmp_path / "mlp_dyn.onnx")
        result = quantize_dynamic_simple(mlp_model_path, out)
        assert result.success
        # INT8动态量化通常文件更小，但权重较小时可能有 overhead
        assert result.size_ratio > 0

    def test_normal_performance_metrics_populated(self, mlp_model_path, tmp_path):
        """正常：性能指标完整"""
        out = str(tmp_path / "mlp_dyn.onnx")
        result = quantize_dynamic_simple(mlp_model_path, out)
        assert result.success
        assert result.performance.avg_ms > 0
        assert result.performance.p50_ms > 0
        assert result.performance.throughput_fps > 0

    def test_normal_qint8_weight_type(self, mlp_model_path, tmp_path):
        """正常：默认QInt8权重类型"""
        out = str(tmp_path / "mlp_qint8.onnx")
        result = quantize_dynamic_simple(mlp_model_path, out, weight_type="QInt8")
        assert result.success

    def test_normal_quint8_weight_type(self, mlp_model_path, tmp_path):
        """参数组合：QUInt8权重类型"""
        out = str(tmp_path / "mlp_quint8.onnx")
        result = quantize_dynamic_simple(mlp_model_path, out, weight_type="QUInt8")
        assert result.success

    def test_normal_auto_detects_input_for_benchmark(self, small_mlp_path, tmp_path):
        """Bug #1验证：自动检测输入，无需显式传参"""
        out = str(tmp_path / "small_dyn.onnx")
        result = quantize_dynamic_simple(small_mlp_path, out)
        assert result.success
        assert result.performance.success

    def test_exception_nonexistent_input(self, tmp_path):
        """异常：输入文件不存在"""
        result = quantize_dynamic_simple("/nonexistent.onnx", str(tmp_path / "out.onnx"))
        assert not result.success
        assert result.error is not None

    def test_boundary_small_model(self, small_mlp_path, tmp_path):
        """边界：极小模型"""
        out = str(tmp_path / "small_dyn.onnx")
        result = quantize_dynamic_simple(small_mlp_path, out)
        assert result.success


class TestQuantizationResult:
    """QuantizationResult 数据类测试"""

    def test_defaults(self):
        """空值/默认值"""
        r = QuantizationResult()
        assert r.success is False
        assert r.strategy_used == ""
        assert r.speedup == 0.0
        assert r.size_ratio == 0.0
        assert r.all_attempts == []
        assert r.error is None
        assert r.fallback_triggered is False

    def test_to_dict_basic(self):
        """正常：to_dict输出"""
        r = QuantizationResult(success=True, strategy_used="dynamic", speedup=1.5)
        d = r.to_dict()
        assert d["success"] is True
        assert d["strategy_used"] == "dynamic"
        assert d["speedup"] == 1.5

    def test_to_dict_with_performance(self, mlp_model_path, tmp_path):
        """正常：包含performance的to_dict"""
        out = str(tmp_path / "r.onnx")
        result = quantize_dynamic_simple(mlp_model_path, out)
        if result.success:
            d = result.to_dict()
            assert "performance" in d
            assert "avg_ms" in d["performance"]


class TestQuantizationConfig:
    """QuantizationConfig 测试"""

    def test_defaults(self):
        """正常：默认配置"""
        cfg = QuantizationConfig()
        assert cfg.strategy == "auto"
        assert cfg.quant_format == "QDQ"
        assert cfg.per_channel is True
        assert cfg.auto_fallback is True
        assert cfg.warmup == 50
        assert cfg.runs == 300

    def test_custom(self):
        """正常：自定义配置"""
        cfg = QuantizationConfig(strategy="dynamic", warmup=5, runs=20, intra_threads=2)
        assert cfg.strategy == "dynamic"
        assert cfg.warmup == 5
        assert cfg.intra_threads == 2
