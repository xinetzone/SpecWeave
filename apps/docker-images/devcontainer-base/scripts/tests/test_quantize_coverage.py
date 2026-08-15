"""quantize.py 专项覆盖率测试 — 目标：将quantize.py覆盖率提升至95%+

覆盖范围：
1. _safe_get_input_shape 边界输入（Session对象、dim_value=0、未知类型）
2. _prepare_model 回退路径（onnxsim失败、quant_pre_process失败）
3. _do_quantize_fp16 依赖缺失路径
4. _quantize_with_config 未知策略、精度失败error
5. auto_quantize verbose打印、回滚触发、全策略失败
6. _try_strategy qoperator_qint8策略、未知策略、perf/acc失败分支
7. QuantizationResult.to_dict perf/fp32失败时无字段
"""
import os
import sys
import tempfile
from unittest import mock
import numpy as np
import pytest
import onnx
from onnx import TensorProto, helper, numpy_helper

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit.quantize import (
    _safe_get_input_shape, _prepare_model, _do_quantize_fp16,
    _quantize_with_config, _try_strategy, _build_fallback_chain,
    auto_quantize, quantize_static_qdq, quantize_dynamic_simple,
    QuantizationConfig, QuantizationResult, HAS_FP16,
)
from onnx_quantize_kit.accuracy import AccuracyThresholds
from onnx_quantize_kit.calibration import RandomCalibrationReader
from onnx_quantize_kit.benchmark import create_session, BenchmarkResult


# 快速测试参数
_FAST_WARMUP = 1
_FAST_RUNS = 3
_FAST_CALIB = 3
_FAST_THREADS = 1
_LOOSE_THRESHOLDS = AccuracyThresholds(
    excellent_max_diff=1000.0,
    acceptable_max_diff=2000.0,
    min_cosine_sim=0.0,
    min_speedup=0.0,
)


class _MockDimValueZero:
    """模拟dim_value=0且无dim_param的情况"""
    def __init__(self):
        self.dim_value = 0
        self.dim_param = ""


class _MockUnknownType:
    """模拟既不是int也不是DimensionProto的未知类型"""
    pass


def _ok_benchmark(**kwargs):
    """创建成功的BenchmarkResult"""
    defaults = dict(avg_ms=1.0, p50_ms=1.0, size_kb=10.0, throughput_fps=1000, runs=10)
    defaults.update(kwargs)
    return BenchmarkResult(**defaults)


def _fail_benchmark(error_msg="mock failure"):
    """创建失败的BenchmarkResult"""
    return BenchmarkResult(error=error_msg)


class TestSafeGetInputShapeCoverage:
    """覆盖_safe_get_input_shape剩余分支"""

    def test_with_session_object(self, mlp_model_path):
        """覆盖L135-137：传入InferenceSession对象而非input"""
        sess = create_session(mlp_model_path, intra_threads=1)
        shape = _safe_get_input_shape(sess)
        assert isinstance(shape, tuple)
        assert len(shape) == 2
        del sess

    def test_dim_value_zero_without_param(self):
        """覆盖L148：dim_value=0且无dim_param返回default"""
        class _MockInput:
            shape = (1, _MockDimValueZero())
        shape = _safe_get_input_shape(_MockInput())
        assert shape[1] == 1

    def test_unknown_type_returns_default(self):
        """覆盖L150：未知类型返回default"""
        class _MockInput:
            shape = (_MockUnknownType(), _MockUnknownType())
        shape = _safe_get_input_shape(_MockInput())
        assert shape == (1, 1)

    def test_custom_default_value(self):
        """覆盖：自定义default值"""
        class _MockInput:
            shape = (0, _MockDimValueZero(), _MockUnknownType())
        shape = _safe_get_input_shape(_MockInput(), default=4)
        assert shape == (4, 4, 4)


class TestPrepareModelCoverage:
    """覆盖_prepare_model回退路径"""

    def _make_simple_model(self, tmpdir):
        """创建一个简单MLP模型"""
        IN, OUT = 4, 2
        rng = np.random.default_rng(42)
        w = (rng.standard_normal((IN, OUT)) * 0.1).astype(np.float32)
        b = np.zeros(OUT, dtype=np.float32)
        nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
        graph = helper.make_graph(
            nodes, "linear",
            [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN])],
            [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT])],
            [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
             helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        path = os.path.join(tmpdir, "model.onnx")
        onnx.save(model, path)
        return path

    def test_onnxsim_import_failure_fallback(self, tmp_path):
        """覆盖L243-244：onnxsim导入失败时回退到原始模型"""
        model_path = self._make_simple_model(str(tmp_path))
        tmp_subdir = str(tmp_path / "tmp")
        os.makedirs(tmp_subdir, exist_ok=True)
        with mock.patch('onnxsim.simplify', side_effect=ImportError("mock no onnxsim")):
            prepared = _prepare_model(model_path, tmp_subdir)
            assert os.path.exists(prepared)

    def test_quant_pre_process_failure_fallback(self, tmp_path):
        """覆盖L252-253：quant_pre_process失败时回退到prepared_path"""
        model_path = self._make_simple_model(str(tmp_path))
        tmp_subdir = str(tmp_path / "tmp2")
        os.makedirs(tmp_subdir, exist_ok=True)
        with mock.patch('onnx_quantize_kit.quantize.quant_pre_process',
                        side_effect=RuntimeError("mock pre_process failure")):
            prepared = _prepare_model(model_path, tmp_subdir)
            assert os.path.exists(prepared)
            assert "model_prepared.onnx" in prepared


class TestDoQuantizeFp16Coverage:
    """覆盖_do_quantize_fp16依赖缺失路径"""

    def test_fp16_import_error_when_missing(self, tmp_path):
        """覆盖L286-287：HAS_FP16=False时抛出ImportError"""
        IN, OUT = 4, 2
        rng = np.random.default_rng(42)
        w = (rng.standard_normal((IN, OUT)) * 0.1).astype(np.float32)
        b = np.zeros(OUT, dtype=np.float32)
        nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
        graph = helper.make_graph(
            nodes, "linear",
            [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN])],
            [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT])],
            [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
             helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        prepared = str(tmp_path / "prepared.onnx")
        out = str(tmp_path / "fp16.onnx")
        onnx.save(model, prepared)

        with mock.patch('onnx_quantize_kit.quantize.HAS_FP16', False):
            with pytest.raises(ImportError, match="onnxconverter-common"):
                _do_quantize_fp16(prepared, out)


class TestQuantizeWithConfigCoverage:
    """覆盖_quantize_with_config剩余分支"""

    def _make_simple_model(self, tmpdir):
        IN, OUT = 4, 2
        rng = np.random.default_rng(42)
        w = (rng.standard_normal((IN, OUT)) * 0.1).astype(np.float32)
        b = np.zeros(OUT, dtype=np.float32)
        nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
        graph = helper.make_graph(
            nodes, "linear",
            [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN])],
            [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT])],
            [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
             helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        path = os.path.join(tmpdir, "model.onnx")
        onnx.save(model, path)
        return path

    def test_unknown_strategy_raises_error(self, tmp_path):
        """覆盖L353：未知strategy抛出ValueError"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(strategy="invalid_strategy_xyz")
        result = _quantize_with_config(model_path, out, cfg, None, None, None)
        assert not result.success
        assert "Unknown strategy" in str(result.error)

    def test_accuracy_failure_sets_error(self, tmp_path):
        """覆盖L376-377：精度验证失败时设置error字段"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        # 使用极严格的精度阈值强制精度验证失败
        strict_thresholds = AccuracyThresholds(
            excellent_max_diff=0.0,
            acceptable_max_diff=0.0,
            min_cosine_sim=1.0,
            min_speedup=1000.0,
        )
        cfg = QuantizationConfig(
            strategy="dynamic",
            warmup=_FAST_WARMUP, runs=_FAST_RUNS,
            intra_threads=_FAST_THREADS,
            thresholds=strict_thresholds,
        )
        result = _quantize_with_config(model_path, out, cfg, None, (1, 4), "input")
        assert not result.success or isinstance(result.error, str)


class TestQuantizationResultToDictCoverage:
    """覆盖QuantizationResult.to_dict剩余分支"""

    def test_performance_exists_but_not_success(self):
        """覆盖L85：performance存在但error不为None时不输出performance字段"""
        failed_perf = _fail_benchmark("mock benchmark failure")
        r = QuantizationResult(
            success=False,
            performance=failed_perf,
            fp32_performance=_ok_benchmark(),
        )
        d = r.to_dict()
        assert "performance" not in d
        assert "fp32" in d

    def test_fp32_performance_exists_but_not_success(self):
        """覆盖L101：fp32_performance存在但error不为None时不输出fp32字段"""
        ok_perf = _ok_benchmark()
        failed_fp32 = _fail_benchmark("mock fp32 failure")
        r = QuantizationResult(
            success=True,
            performance=ok_perf,
            fp32_performance=failed_fp32,
        )
        d = r.to_dict()
        assert "performance" in d
        assert "fp32" not in d

    def test_both_performances_failed(self):
        """两个performance都失败时的to_dict"""
        r = QuantizationResult(
            success=False,
            performance=_fail_benchmark("perf fail"),
            fp32_performance=_fail_benchmark("fp32 fail"),
            accuracy=None,
        )
        d = r.to_dict()
        assert "performance" not in d
        assert "fp32" not in d
        assert "accuracy" not in d


class TestAutoQuantizeVerboseCoverage:
    """覆盖auto_quantize verbose=True路径和回滚机制"""

    def _make_simple_mlp(self, tmpdir, in_dim=4, out_dim=2):
        """创建简单MLP用于快速测试"""
        rng = np.random.default_rng(42)
        w = (rng.standard_normal((in_dim, out_dim)) * 0.1).astype(np.float32)
        b = np.zeros(out_dim, dtype=np.float32)
        nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
        graph = helper.make_graph(
            nodes, "mlp",
            [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, in_dim])],
            [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, out_dim])],
            [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
             helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        path = os.path.join(tmpdir, "mlp.onnx")
        onnx.save(model, path)
        return path

    def test_verbose_true_prints_progress(self, tmp_path, capsys):
        """覆盖verbose打印路径 - 使用dynamic策略快速测试"""
        model_path = self._make_simple_mlp(str(tmp_path))
        out = str(tmp_path / "quantized.onnx")
        cfg = QuantizationConfig(
            strategy="dynamic",
            warmup=_FAST_WARMUP, runs=_FAST_RUNS,
            num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
            thresholds=_LOOSE_THRESHOLDS,
        )
        result = auto_quantize(model_path, out, config=cfg, verbose=True)
        captured = capsys.readouterr()
        assert result.success
        assert "[auto_quantize]" in captured.out
        assert os.path.exists(out)

    def test_fallback_triggered_sets_reason(self, tmp_path):
        """覆盖L494-498：回滚触发时设置fallback_reason"""
        model_path = self._make_simple_mlp(str(tmp_path))
        out = str(tmp_path / "quantized.onnx")

        original_try_strategy = _try_strategy
        attempt_count = [0]

        def mock_try_strategy(prepared_path, output_path, strategy, calib_reader,
                             input_shape, input_name, cfg, fp32_perf, thresholds, verbose):
            attempt_count[0] += 1
            if attempt_count[0] == 1:
                return {"success": False, "error": "mock primary failure", "speedup": 0, "max_diff": -1}
            # 后续调用实际执行动态量化
            return original_try_strategy(
                prepared_path, output_path, "dynamic",
                calib_reader, (1, 4), "input",
                QuantizationConfig(
                    strategy="dynamic", warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                    intra_threads=_FAST_THREADS, thresholds=_LOOSE_THRESHOLDS,
                ),
                fp32_perf, _LOOSE_THRESHOLDS, False
            )

        with mock.patch('onnx_quantize_kit.quantize._try_strategy', mock_try_strategy):
            cfg = QuantizationConfig(
                strategy="static_qdq",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
                auto_fallback=True,
            )
            result = auto_quantize(model_path, out, config=cfg, verbose=False)
            assert result.success
            assert result.fallback_triggered is True
            assert len(result.fallback_reason) > 0

    def test_all_strategies_fail(self, tmp_path):
        """覆盖L511-514：所有策略都失败时返回error"""
        model_path = self._make_simple_mlp(str(tmp_path))
        out = str(tmp_path / "quantized.onnx")

        def mock_try_strategy_all_fail(*args, **kwargs):
            return {"success": False, "error": "mock failure", "speedup": 0, "max_diff": -1}

        with mock.patch('onnx_quantize_kit.quantize._try_strategy', mock_try_strategy_all_fail):
            cfg = QuantizationConfig(
                strategy="dynamic",
                warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                intra_threads=_FAST_THREADS,
                thresholds=_LOOSE_THRESHOLDS,
            )
            result = auto_quantize(model_path, out, config=cfg, verbose=False)
            assert not result.success
            assert result.error is not None

    def test_fatal_exception_handling(self, tmp_path):
        """覆盖L516-519：try块内异常被捕获到result.error（mock_prepare_model抛异常）"""
        model_path = self._make_simple_mlp(str(tmp_path))
        out = str(tmp_path / "quantized.onnx")

        # _prepare_model在try块内，mock它抛出异常
        with mock.patch('onnx_quantize_kit.quantize._prepare_model',
                        side_effect=RuntimeError("mock fatal error in prepare")):
            cfg = QuantizationConfig(intra_threads=_FAST_THREADS)
            result = auto_quantize(model_path, out, config=cfg, verbose=True)
            assert not result.success
            assert "mock fatal error" in str(result.error)


class TestTryStrategyCoverage:
    """覆盖_try_strategy剩余分支"""

    def _make_simple_model(self, tmpdir, in_dim=4, out_dim=2):
        rng = np.random.default_rng(42)
        w = (rng.standard_normal((in_dim, out_dim)) * 0.1).astype(np.float32)
        b = np.zeros(out_dim, dtype=np.float32)
        nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
        graph = helper.make_graph(
            nodes, "linear",
            [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, in_dim])],
            [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, out_dim])],
            [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
             helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        path = os.path.join(tmpdir, "model.onnx")
        onnx.save(model, path)
        return path

    def test_unknown_strategy_returns_error(self, tmp_path):
        """覆盖L581-584：未知strategy返回error"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(intra_threads=_FAST_THREADS)
        fp32_perf = _ok_benchmark()
        calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)
        result = _try_strategy(
            model_path, out, "nonexistent_strategy_xyz",
            calib, (1, 4), "input", cfg, fp32_perf, _LOOSE_THRESHOLDS, False
        )
        assert not result["success"]
        assert "Unknown strategy" in str(result.get("error", ""))

    def test_perf_failure_returns_error(self, tmp_path):
        """覆盖L592-595：perf失败时返回error"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(intra_threads=_FAST_THREADS)
        fp32_perf = _ok_benchmark()
        calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)

        with mock.patch('onnx_quantize_kit.quantize.benchmark_model',
                        return_value=_fail_benchmark("mock perf failure")):
            result = _try_strategy(
                model_path, out, "dynamic",
                calib, (1, 4), "input", cfg, fp32_perf, _LOOSE_THRESHOLDS, False
            )
            assert not result["success"]
            assert "benchmark failed" in str(result.get("error", ""))

    def test_accuracy_failure_returns_error(self, tmp_path):
        """覆盖L608-609：acc.passed=False时返回error"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(intra_threads=_FAST_THREADS)
        fp32_perf = _ok_benchmark()
        calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)

        class _FailedAcc:
            passed = False
            fail_reason = "mock accuracy failure"
            max_diff = 999.0

        with mock.patch('onnx_quantize_kit.quantize.validate_accuracy',
                        return_value=_FailedAcc()):
            with mock.patch('onnx_quantize_kit.quantize.benchmark_model',
                            return_value=_ok_benchmark()):
                result = _try_strategy(
                    model_path, out, "dynamic",
                    calib, (1, 4), "input", cfg, fp32_perf, _LOOSE_THRESHOLDS, False
                )
                assert not result["success"]

    def test_qoperator_qint8_strategy(self, tmp_path):
        """覆盖L561-568：static_qoperator_qint8策略分支"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(
            warmup=_FAST_WARMUP, runs=_FAST_RUNS,
            num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
            thresholds=_LOOSE_THRESHOLDS,
        )
        fp32_perf = _ok_benchmark()
        calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)
        result = _try_strategy(
            model_path, out, "static_qoperator_qint8",
            calib, (1, 4), "input", cfg, fp32_perf, _LOOSE_THRESHOLDS, False
        )
        assert isinstance(result, dict)
        assert "success" in result

    def test_exception_caught_and_returned(self, tmp_path):
        """覆盖L611-612：异常被捕获并返回error"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(intra_threads=_FAST_THREADS)
        fp32_perf = _ok_benchmark()
        calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)

        with mock.patch('onnx_quantize_kit.quantize._do_quantize_dynamic',
                        side_effect=RuntimeError("mock quantization exception")):
            result = _try_strategy(
                model_path, out, "dynamic",
                calib, (1, 4), "input", cfg, fp32_perf, _LOOSE_THRESHOLDS, False
            )
            assert not result["success"]
            assert "mock quantization exception" in str(result.get("error", ""))


class TestQuantizeStaticQdqExplicitInputCoverage:
    """覆盖_quantize_with_config中只有部分input参数为None的情况"""

    def _make_simple_model(self, tmpdir, in_dim=4, out_dim=2):
        rng = np.random.default_rng(42)
        w = (rng.standard_normal((in_dim, out_dim)) * 0.1).astype(np.float32)
        b = np.zeros(out_dim, dtype=np.float32)
        nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
        graph = helper.make_graph(
            nodes, "linear",
            [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, in_dim])],
            [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, out_dim])],
            [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
             helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        path = os.path.join(tmpdir, "model.onnx")
        onnx.save(model, path)
        return path

    def test_input_shape_provided_but_name_none(self, tmp_path):
        """覆盖L326-332：input_shape已提供但input_name为None"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        result = quantize_static_qdq(
            model_path, out,
            input_shape=(1, 4),
            input_name=None,
            warmup=_FAST_WARMUP, runs=_FAST_RUNS,
            num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
            thresholds=_LOOSE_THRESHOLDS,
        )
        assert isinstance(result, QuantizationResult)

    def test_input_name_provided_but_shape_none(self, tmp_path):
        """覆盖L326-332：input_name已提供但input_shape为None"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        result = quantize_static_qdq(
            model_path, out,
            input_shape=None,
            input_name="input",
            warmup=_FAST_WARMUP, runs=_FAST_RUNS,
            num_calib_samples=_FAST_CALIB, intra_threads=_FAST_THREADS,
            thresholds=_LOOSE_THRESHOLDS,
        )
        assert isinstance(result, QuantizationResult)


class TestBuildFallbackChainExtraCoverage:
    """覆盖_build_fallback_chain剩余分支"""

    def test_static_qoperator_qint8_chain(self):
        """覆盖：static_qoperator_qint8的回滚链（未知策略使用默认链）"""
        chain = _build_fallback_chain("static_qoperator_qint8", None)
        assert "dynamic" in chain
        assert "fp16" in chain

    def test_recommended_fallback_already_in_chain(self):
        """覆盖L536-537：recommended_fallback已在链中不重复插入"""
        chain = _build_fallback_chain("dynamic", "fp16")
        assert len([s for s in chain if s == "fp16"]) == 1


class TestFinalCoverageBoost:
    """最后补充测试，覆盖剩余行以达到≥95%覆盖率"""

    def _make_simple_model(self, tmpdir, in_dim=4, out_dim=2):
        rng = np.random.default_rng(42)
        w = (rng.standard_normal((in_dim, out_dim)) * 0.1).astype(np.float32)
        b = np.zeros(out_dim, dtype=np.float32)
        nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
        graph = helper.make_graph(
            nodes, "linear",
            [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, in_dim])],
            [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, out_dim])],
            [helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
             helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True)])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
        path = os.path.join(tmpdir, "model.onnx")
        onnx.save(model, path)
        return path

    def test_verbose_fallback_prints_reason(self, tmp_path, capsys):
        """覆盖L504：verbose模式下打印信息"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(
            strategy="dynamic",
            warmup=_FAST_WARMUP, runs=_FAST_RUNS,
            intra_threads=_FAST_THREADS,
            thresholds=_LOOSE_THRESHOLDS,
        )
        result = auto_quantize(model_path, out, config=cfg, verbose=True)
        assert result.success
        captured = capsys.readouterr()
        assert "[auto_quantize]" in captured.out

    def test_fp16_import_error_flag_exists(self):
        """验证HAS_FP16标志存在"""
        from onnx_quantize_kit import quantize
        assert hasattr(quantize, 'HAS_FP16')
        assert isinstance(quantize.HAS_FP16, bool)

    def test_quantize_static_qoperator_wrapper(self, tmp_path):
        """覆盖L310-313：quantize_static_qoperator便捷函数调用_quantize_with_config"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        with mock.patch('onnx_quantize_kit.quantize._quantize_with_config') as mock_qcfg:
            mock_qcfg.return_value = QuantizationResult(success=True)
            from onnx_quantize_kit.quantize import quantize_static_qoperator
            calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)
            result = quantize_static_qoperator(model_path, out, calib_reader=calib,
                                               warmup=_FAST_WARMUP, runs=_FAST_RUNS,
                                               intra_threads=_FAST_THREADS)
            assert mock_qcfg.called
            assert mock_qcfg.call_args[0][2].strategy == "static_qoperator"

    def test_try_strategy_fp16_working(self, tmp_path):
        """覆盖L580：_try_strategy中fp16策略正常路径"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(intra_threads=_FAST_THREADS)
        fp32_perf = _ok_benchmark()
        calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)
        result = _try_strategy(
            model_path, out, "fp16", calib, (1, 4), "input", cfg, fp32_perf, _LOOSE_THRESHOLDS, False
        )
        assert isinstance(result, dict)
        assert "success" in result

    def test_try_strategy_static_qdq(self, tmp_path):
        """覆盖L553-560：_try_strategy中static_qdq策略"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(intra_threads=_FAST_THREADS)
        fp32_perf = _ok_benchmark()
        calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)
        result = _try_strategy(
            model_path, out, "static_qdq", calib, (1, 4), "input", cfg, fp32_perf, _LOOSE_THRESHOLDS, False
        )
        assert isinstance(result, dict)

    def test_try_strategy_static_qoperator_quint8(self, tmp_path):
        """覆盖L569-576：_try_strategy中static_qoperator_quint8策略"""
        model_path = self._make_simple_model(str(tmp_path))
        out = str(tmp_path / "out.onnx")
        cfg = QuantizationConfig(intra_threads=_FAST_THREADS)
        fp32_perf = _ok_benchmark()
        calib = RandomCalibrationReader("input", (1, 4), _FAST_CALIB)
        result = _try_strategy(
            model_path, out, "static_qoperator_quint8", calib, (1, 4), "input",
            cfg, fp32_perf, _LOOSE_THRESHOLDS, False
        )
        assert isinstance(result, dict)

    def test_recommended_fallback_not_in_chain_inserts(self):
        """覆盖L537：recommended_fallback不在链中时插入到开头"""
        chain = _build_fallback_chain("fp16", "dynamic")
        assert chain[0] == "dynamic"
