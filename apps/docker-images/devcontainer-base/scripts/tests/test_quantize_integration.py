"""
集成测试：覆盖 quantize.py 静态量化主路径 + auto_quantize 自动策略选择 + 回滚链

与单元测试的区别：
- 单元测试：测试单个函数/便捷函数，使用极快参数（warmup=0, runs=1），不做完整精度验证
- 集成测试：测试端到端静态量化流程（_prepare_model → _do_quantize_static → benchmark → validate_accuracy），
            验证量化后模型可实际推理、auto_quantize策略选择和回滚链机制正确

测试模型：cnn_model_path (Conv→Relu→GlobalAveragePool→Flatten→MatMul→Add, input (1,3,8,8))
测试参数使用快速配置（warmup=2, runs=10, calib_samples=5）保证CI速度
"""
import os
import sys
import tempfile
import shutil
import numpy as np
import pytest
import onnxruntime as ort

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit.quantize import (
    quantize_static_qdq,
    quantize_static_qoperator,
    auto_quantize,
    _build_fallback_chain,
    QuantizationConfig,
    QuantizationResult,
)
from onnx_quantize_kit.accuracy import AccuracyThresholds
from onnx_quantize_kit.calibration import NumpyCalibrationReader
from onnx_quantize_kit.benchmark import create_session


# 快速测试参数（减少集成测试执行时间）
_FAST_WARMUP = 2
_FAST_RUNS = 10
_FAST_CALIB = 5
_FAST_THREADS = 1

# 非常宽松的精度阈值——小模型+随机校准数据精度损失可能较大
# 集成测试关注"流程是否通"而非"精度是否优"，精度阈值在单元测试中已验证
_LOOSE_THRESHOLDS = AccuracyThresholds(
    excellent_max_diff=100.0,    # 极大的优秀阈值
    acceptable_max_diff=200.0,   # 极大的可接受阈值（保证流程能通过）
    min_cosine_sim=0.0,          # 不检查余弦相似度
    min_speedup=0.0,             # 不检查加速比（小模型量化可能反而变慢）
)


def _run_quantized_model(model_path: str, input_shape: tuple, input_name: str) -> np.ndarray:
    """加载量化模型并运行一次推理，返回输出"""
    sess = create_session(model_path, intra_threads=1)
    try:
        dummy = np.random.randn(*input_shape).astype(np.float32)
        out = sess.run(None, {input_name: dummy})[0]
        return out
    finally:
        del sess


class TestStaticQdqIntegration:
    """quantize_static_qdq 端到端集成测试"""

    def test_normal_cnn_quantizes_successfully(self, cnn_model_path):
        """正常：CNN模型完整静态QDQ量化流程成功"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qdq(
                cnn_model_path, out,
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success, f"QDQ量化失败: {result.error}"
            assert result.strategy_used == "static_qdq"
            assert os.path.isfile(out)
            assert os.path.getsize(out) > 0

    def test_quantized_model_is_runnable(self, cnn_model_path):
        """正常：量化后模型可以正常加载和推理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qdq(
                cnn_model_path, out,
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success
            # 验证量化模型可推理
            output = _run_quantized_model(out, (1, 3, 8, 8), "input")
            assert output.shape == (1, 10)
            assert not np.any(np.isnan(output)), "输出包含NaN"
            assert not np.any(np.isinf(output)), "输出包含Inf"

    def test_result_contains_performance_and_accuracy(self, cnn_model_path):
        """正常：结果对象包含性能和精度指标"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qdq(
                cnn_model_path, out,
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success
            assert result.fp32_performance is not None
            assert result.fp32_performance.success
            assert result.performance is not None
            assert result.performance.success
            assert result.performance.avg_ms > 0
            assert result.performance.size_kb > 0
            assert result.accuracy is not None
            assert result.size_ratio > 0
            # speedup可能小于1（小模型开销），但字段应存在
            assert isinstance(result.speedup, float)

    def test_with_explicit_shape_and_name(self, cnn_model_path):
        """正常：显式指定input_shape和input_name"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qdq(
                cnn_model_path, out,
                input_shape=(1, 3, 8, 8),
                input_name="input",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success, f"显式shape/name量化失败: {result.error}"

    def test_with_custom_numpy_calibration_reader(self, cnn_model_path):
        """正常：使用自定义NumpyCalibrationReader而非随机数据"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            # 生成自定义校准数据（高斯分布，均值0，标准差1）
            calib_data = [np.random.randn(1, 3, 8, 8).astype(np.float32) for _ in range(_FAST_CALIB)]
            reader = NumpyCalibrationReader("input", iter(calib_data))
            result = quantize_static_qdq(
                cnn_model_path, out,
                calib_reader=reader,
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success, f"自定义校准数据量化失败: {result.error}"
            assert os.path.isfile(out)

    def test_size_ratio_is_reasonable(self, cnn_model_path):
        """正常：size_ratio在合理范围（INT8模型通常比FP32小25-75%）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qdq(
                cnn_model_path, out,
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success
            fp32_kb = os.path.getsize(cnn_model_path) / 1024
            quant_kb = os.path.getsize(out) / 1024
            # 静态量化模型可能因QDQ算子增加而变大（小模型尤其明显），但不应超过FP32的3倍
            assert quant_kb < fp32_kb * 3, f"量化后文件异常大: {quant_kb:.1f}KB vs FP32 {fp32_kb:.1f}KB"

    def test_exception_nonexistent_input(self):
        """异常：不存在的输入文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "out.onnx")
            result = quantize_static_qdq("/nonexistent/path/model.onnx", out)
            assert not result.success
            assert result.error is not None


class TestStaticQoperatorIntegration:
    """quantize_static_qoperator 端到端集成测试"""

    def test_normal_cnn_qoperator_quantizes(self, cnn_model_path):
        """正常：CNN模型静态QOperator量化成功"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qoperator(
                cnn_model_path, out,
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success, f"QOperator量化失败: {result.error}"
            assert result.strategy_used == "static_qoperator"
            assert os.path.isfile(out)
            # 验证可推理
            output = _run_quantized_model(out, (1, 3, 8, 8), "input")
            assert output.shape == (1, 10)


class TestAutoQuantizeIntegration:
    """auto_quantize 自动策略选择+回滚链集成测试"""

    def test_auto_selects_correct_strategy_for_cnn(self, cnn_model_path):
        """正常：CNN模型自动选择static_qdq作为主策略"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            cfg = QuantizationConfig(
                strategy="auto",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            result = auto_quantize(
                cnn_model_path, out,
                config=cfg,
                verbose=False,
            )
            assert result.success, f"auto_quantize失败: {result.error}"
            assert result.model_type == "cnn"
            # CNN推荐策略是static_qdq（来自model_detect配置）
            assert result.strategy_used == "static_qdq"
            assert not result.fallback_triggered, "主策略应直接成功，不应触发回滚"
            assert result.fallback_reason == ""

    def test_all_attempts_chain_recorded(self, cnn_model_path):
        """正常：all_attempts记录完整策略尝试历史"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            cfg = QuantizationConfig(
                strategy="auto",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            result = auto_quantize(
                cnn_model_path, out,
                config=cfg,
                verbose=False,
            )
            assert result.success
            assert len(result.all_attempts) >= 1
            # 第一个attempt是主策略static_qdq，应成功
            primary = result.all_attempts[0]
            assert primary["strategy"] == "static_qdq"
            assert primary["success"] is True
            assert "speedup" in primary
            assert "max_diff" in primary

    def test_result_to_dict_contains_all_fields(self, cnn_model_path):
        """正常：to_dict()输出包含性能/精度/FP32基准"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            cfg = QuantizationConfig(
                strategy="auto",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            result = auto_quantize(
                cnn_model_path, out,
                config=cfg,
                verbose=False,
            )
            assert result.success
            d = result.to_dict()
            assert d["success"] is True
            assert d["model_type"] == "cnn"
            assert d["strategy_used"] == "static_qdq"
            assert "performance" in d
            assert "fp32" in d
            assert "accuracy" in d
            assert d["performance"]["avg_ms"] > 0
            assert d["fp32"]["size_kb"] > 0

    def test_quantized_model_produces_valid_output(self, cnn_model_path):
        """正常：auto_quantize产出模型可推理，输出shape和数值有效"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            cfg = QuantizationConfig(
                strategy="auto",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            result = auto_quantize(
                cnn_model_path, out,
                config=cfg,
                verbose=False,
            )
            assert result.success
            output = _run_quantized_model(out, (1, 3, 8, 8), "input")
            assert output.shape == (1, 10)
            assert output.dtype == np.float32
            assert np.all(np.isfinite(output))

    def test_with_explicit_config(self, cnn_model_path):
        """正常：传入自定义QuantizationConfig（指定dynamic策略）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            cfg = QuantizationConfig(
                strategy="dynamic",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            result = auto_quantize(
                cnn_model_path, out,
                config=cfg,
                verbose=False,
            )
            # dynamic策略不需要校准数据，应该成功
            assert result.success, f"显式dynamic策略失败: {result.error}"
            assert result.strategy_used == "dynamic"


class TestBuildFallbackChain:
    """_build_fallback_chain 纯函数测试"""

    def test_static_qdq_chain_order(self):
        """正常：static_qdq的回滚链顺序正确"""
        chain = _build_fallback_chain("static_qdq", None)
        assert chain[0] == "static_qoperator_quint8"
        assert "dynamic" in chain
        assert "fp16" in chain
        # fp16是最后一个
        assert chain[-1] == "fp16"

    def test_static_qoperator_chain_contains_qdq(self):
        """正常：static_qoperator的回滚链包含static_qdq"""
        chain = _build_fallback_chain("static_qoperator", None)
        assert "static_qdq" in chain
        assert "dynamic" in chain
        assert "fp16" in chain

    def test_dynamic_chain_only_fp16(self):
        """正常：dynamic策略的回滚链只有fp16"""
        chain = _build_fallback_chain("dynamic", None)
        assert chain == ["fp16"]

    def test_fp16_chain_empty(self):
        """边界：fp16是最后策略，无回滚"""
        chain = _build_fallback_chain("fp16", None)
        assert chain == []

    def test_unknown_strategy_default_chain(self):
        """边界：未知策略返回默认链[dynamic, fp16]"""
        chain = _build_fallback_chain("unknown_strategy", None)
        assert "dynamic" in chain
        assert "fp16" in chain

    def test_recommended_fallback_inserted_first(self):
        """正常：推荐的fallback被插入到链首"""
        chain = _build_fallback_chain("static_qdq", "dynamic")
        # recommended_fallback已在默认链中，不应重复
        assert len([s for s in chain if s == "dynamic"]) == 1

    def test_custom_recommended_fallback_not_in_default(self):
        """正常：自定义fallback不在默认链中时插入到首位"""
        chain = _build_fallback_chain("fp16", "dynamic")
        # fp16默认链为空，插入dynamic
        assert chain[0] == "dynamic"
        assert "fp16" not in chain or chain[0] == "dynamic"


class TestQuantizationConfig:
    """QuantizationConfig 配置集成测试"""

    def test_quint8_activation_and_weight(self, cnn_model_path):
        """参数组合：QUInt8激活+QUInt8权重静态量化（ORT要求激活和权重类型匹配）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qoperator(
                cnn_model_path, out,
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success, f"QUInt8静态量化失败: {result.error}"

    def test_non_per_channel(self, cnn_model_path):
        """参数组合：非per_channel量化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qdq(
                cnn_model_path, out,
                per_channel=False,
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success, f"非per_channel量化失败: {result.error}"

    def test_entropy_calibration_method(self, cnn_model_path):
        """参数组合：Entropy校准方法"""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "quantized.onnx")
            result = quantize_static_qdq(
                cnn_model_path, out,
                calibrate_method="Entropy",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            assert result.success, f"Entropy校准量化失败: {result.error}"
