"""高层量化API：自动选型+回滚策略

================================================================================
📌 量化引擎：onnxruntime.quantization（唯一引擎，不依赖 Neural Compressor）
================================================================================
- INC 3.x已弃用ONNX Runtime适配器（intel/neural-compressor#2199），
  重构为PyTorch-first框架，ONNX量化不再积极维护
- onnxruntime.quantization 原生API优势：零额外依赖、与ORT推理100%兼容、
  社区活跃、适合生产部署
- 如需PyTorch权重量化（RTN/AWQ/GPTQ），可单独 pip install neural-compressor
================================================================================
"""
import os
import tempfile
import shutil
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import onnx
import onnxruntime as ort
from onnxruntime.quantization import (
    quantize_static, quantize_dynamic, QuantType, QuantFormat,
    CalibrationMethod, quant_pre_process,
)
try:
    from onnxconverter_common import float16
    HAS_FP16 = True
except ImportError:
    HAS_FP16 = False

from .calibration import RandomCalibrationReader, CalibrationDataReader
from .benchmark import benchmark_model, create_session, BenchmarkResult
from .accuracy import validate_accuracy, AccuracyThresholds, AccuracyResult
from .model_detect import detect_model_type, ModelType, get_recommended_quant_config


@dataclass
class QuantizationConfig:
    """量化配置"""
    strategy: str = "auto"  # auto / static_qdq / static_qoperator / dynamic / fp16
    quant_format: str = "QDQ"
    activation_type: str = "QInt8"
    weight_type: str = "QInt8"
    per_channel: bool = True
    calibrate_method: str = "MinMax"
    num_calib_samples: int = 100
    intra_threads: int = 4
    warmup: int = 50
    runs: int = 300
    auto_fallback: bool = True
    exclude_nodes: Optional[list] = None
    thresholds: Optional[AccuracyThresholds] = None


@dataclass
class QuantizationResult:
    """量化结果"""
    success: bool = False
    output_path: str = ""
    strategy_used: str = ""
    model_type: str = ""
    performance: Optional[BenchmarkResult] = None
    fp32_performance: Optional[BenchmarkResult] = None
    accuracy: Optional[AccuracyResult] = None
    speedup: float = 0.0
    size_ratio: float = 0.0
    fallback_triggered: bool = False
    fallback_reason: str = ""
    error: Optional[str] = None
    all_attempts: list = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {
            "success": self.success,
            "output_path": self.output_path,
            "strategy_used": self.strategy_used,
            "model_type": self.model_type,
            "speedup": self.speedup,
            "size_ratio": self.size_ratio,
            "fallback_triggered": self.fallback_triggered,
            "fallback_reason": self.fallback_reason,
            "error": self.error,
        }
        if self.performance and self.performance.success:
            d["performance"] = {
                "avg_ms": self.performance.avg_ms,
                "p50_ms": self.performance.p50_ms,
                "p95_ms": self.performance.p95_ms,
                "p99_ms": self.performance.p99_ms,
                "throughput_fps": self.performance.throughput_fps,
                "size_kb": self.performance.size_kb,
            }
        if self.accuracy:
            d["accuracy"] = {
                "max_diff": self.accuracy.max_diff,
                "cosine_sim_min": self.accuracy.cosine_sim_min,
                "level": self.accuracy.level,
                "passed": self.accuracy.passed,
            }
        if self.fp32_performance and self.fp32_performance.success:
            d["fp32"] = {
                "avg_ms": self.fp32_performance.avg_ms,
                "size_kb": self.fp32_performance.size_kb,
            }
        return d


_QTYPE_MAP = {
    "QInt8": QuantType.QInt8,
    "QUInt8": QuantType.QUInt8,
    "QFLOAT8E4M3FN": QuantType.QFLOAT8E4M3FN,
}

_QFMT_MAP = {
    "QDQ": QuantFormat.QDQ,
    "QOperator": QuantFormat.QOperator,
}

_CALIB_MAP = {
    "MinMax": CalibrationMethod.MinMax,
    "Entropy": CalibrationMethod.Entropy,
    "Percentile": CalibrationMethod.Percentile,
    "Distribution": CalibrationMethod.Distribution,
}


def _safe_get_input_shape(session_or_input, default: int = 1) -> tuple:
    """从ONNX Runtime input安全提取形状，兼容DimensionProto和纯int

    动态维度（dim_value=0 或 dim_param字符串存在）会被替换为default值。
    与 benchmark._safe_get_input_shape 保持一致的逻辑。
    """
    import onnxruntime as ort
    if isinstance(session_or_input, ort.InferenceSession):
        inp = session_or_input.get_inputs()[0]
        shape = inp.shape
    else:
        shape = session_or_input.shape
    result = []
    for d in shape:
        if isinstance(d, int):
            result.append(d if d > 0 else default)
        elif hasattr(d, 'dim_value'):
            if hasattr(d, 'dim_param') and d.dim_param:
                result.append(default)
            else:
                result.append(d.dim_value if d.dim_value > 0 else default)
        else:
            result.append(default)
    return tuple(result)


def detect_input_info(model_path: str, intra_threads: int = 4) -> tuple:
    """安全检测模型的输入名称和形状

    Args:
        model_path: ONNX模型路径
        intra_threads: 推理线程数

    Returns:
        (input_name, input_shape) 元组

    Raises:
        ValueError: 模型无输入或加载失败
    """
    sess = create_session(model_path, intra_threads)
    try:
        if len(sess.get_inputs()) == 0:
            raise ValueError("Model has no inputs")
        inp = sess.get_inputs()[0]
        name = inp.name
        shape = _safe_get_input_shape(inp)
        return name, shape
    finally:
        del sess


# 保留别名以向后兼容
_detect_input_info = detect_input_info


def quantize_fp16(model_path: str, output_path: str) -> QuantizationResult:
    """FP16转换便捷函数"""
    result = QuantizationResult(strategy_used="fp16")
    tmpdir = tempfile.mkdtemp()
    try:
        prepared = _prepare_model(model_path, tmpdir)
        _do_quantize_fp16(prepared, output_path)
        result.success = True
        result.output_path = output_path

        # 自动检测输入信息（修复Bug #1）
        input_name, input_shape = detect_input_info(output_path, intra_threads=4)

        result.performance = benchmark_model(output_path, input_shape, input_name,
                                              intra_threads=4, warmup=20, runs=100)
        # 修复Bug #8：直接用os.path.getsize，无需创建Session跑推理
        fp32_size = os.path.getsize(model_path) / 1024
        result.size_ratio = result.performance.size_kb / max(fp32_size, 1)
    except Exception as e:
        result.error = str(e)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return result


def quantize_dynamic_simple(model_path: str, output_path: str,
                            weight_type: str = "QInt8") -> QuantizationResult:
    """动态量化便捷函数"""
    result = QuantizationResult(strategy_used="dynamic")
    tmpdir = tempfile.mkdtemp()
    try:
        prepared = _prepare_model(model_path, tmpdir)
        _do_quantize_dynamic(prepared, output_path, weight_type)
        result.success = True
        result.output_path = output_path

        # 自动检测输入信息（修复Bug #1）
        input_name, input_shape = detect_input_info(output_path, intra_threads=4)

        result.performance = benchmark_model(output_path, input_shape, input_name,
                                              intra_threads=4, warmup=50, runs=200)
        # 计算size_ratio
        fp32_size = os.path.getsize(model_path) / 1024
        result.size_ratio = result.performance.size_kb / max(fp32_size, 1)
    except Exception as e:
        result.error = str(e)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return result


def _prepare_model(model_path: str, tmpdir: str) -> str:
    """预处理模型：simplify + quant_pre_process"""
    prepared_path = os.path.join(tmpdir, "model_prepared.onnx")
    model = onnx.load(model_path)
    try:
        import onnxsim
        model_simp, check = onnxsim.simplify(model)
        if check:
            model = model_simp
    except Exception:
        pass  # onnxsim失败则使用原始模型

    onnx.save(model, prepared_path)

    preprocessed = os.path.join(tmpdir, "model_preprocessed.onnx")
    try:
        quant_pre_process(prepared_path, preprocessed)
        return preprocessed
    except Exception:
        return prepared_path


def _do_quantize_static(prepared_path: str, output_path: str,
                        calib_reader: CalibrationDataReader,
                        cfg: QuantizationConfig) -> None:
    """执行静态量化"""
    nodes_to_exclude = cfg.exclude_nodes or []
    quantize_static(
        model_input=prepared_path,
        model_output=output_path,
        calibration_data_reader=calib_reader,
        quant_format=_QFMT_MAP.get(cfg.quant_format, QuantFormat.QDQ),
        per_channel=cfg.per_channel,
        activation_type=_QTYPE_MAP.get(cfg.activation_type, QuantType.QInt8),
        weight_type=_QTYPE_MAP.get(cfg.weight_type, QuantType.QInt8),
        calibrate_method=_CALIB_MAP.get(cfg.calibrate_method, CalibrationMethod.MinMax),
        nodes_to_exclude=nodes_to_exclude,
    )


def _do_quantize_dynamic(prepared_path: str, output_path: str,
                         weight_type: str = "QInt8") -> None:
    """执行动态量化"""
    quantize_dynamic(
        model_input=prepared_path,
        model_output=output_path,
        weight_type=_QTYPE_MAP.get(weight_type, QuantType.QInt8),
    )


def _do_quantize_fp16(prepared_path: str, output_path: str) -> None:
    """执行FP16转换"""
    if not HAS_FP16:
        raise ImportError("onnxconverter-common is required for FP16 conversion")
    model = onnx.load(prepared_path)
    model_fp16 = float16.convert_float_to_float16(model)
    onnx.save(model_fp16, output_path)


def quantize_static_qdq(model_path: str, output_path: str,
                        calib_reader: Optional[CalibrationDataReader] = None,
                        input_shape: Optional[tuple] = None,
                        input_name: Optional[str] = None,
                        **kwargs) -> QuantizationResult:
    """QDQ静态量化便捷函数"""
    cfg = QuantizationConfig(strategy="static_qdq", quant_format="QDQ", **kwargs)
    return _quantize_with_config(model_path, output_path, cfg, calib_reader,
                                  input_shape, input_name)


def quantize_static_qoperator(model_path: str, output_path: str,
                               calib_reader: Optional[CalibrationDataReader] = None,
                               input_shape: Optional[tuple] = None,
                               input_name: Optional[str] = None,
                               **kwargs) -> QuantizationResult:
    """QOperator静态量化便捷函数"""
    cfg = QuantizationConfig(strategy="static_qoperator", quant_format="QOperator",
                              activation_type="QUInt8", **kwargs)
    return _quantize_with_config(model_path, output_path, cfg, calib_reader,
                                  input_shape, input_name)


def _quantize_with_config(model_path: str, output_path: str, cfg: QuantizationConfig,
                           calib_reader: Optional[CalibrationDataReader],
                           input_shape: Optional[tuple],
                           input_name: Optional[str]) -> QuantizationResult:
    """带基准测试和精度验证的单次量化尝试"""
    result = QuantizationResult(strategy_used=cfg.strategy)
    tmpdir = tempfile.mkdtemp()
    try:
        prepared = _prepare_model(model_path, tmpdir)
        # 检测输入信息
        if input_shape is None or input_name is None:
            tmp_sess = create_session(prepared, cfg.intra_threads)
            inp = tmp_sess.get_inputs()[0]
            input_name = input_name or inp.name
            if input_shape is None:
                input_shape = _safe_get_input_shape(inp)
            del tmp_sess

        if calib_reader is None:
            calib_reader = RandomCalibrationReader(input_name, input_shape,
                                                    cfg.num_calib_samples)

        # FP32基准
        fp32_perf = benchmark_model(prepared, input_shape, input_name,
                                     cfg.warmup, cfg.runs, cfg.intra_threads)
        result.fp32_performance = fp32_perf

        # 执行量化
        quant_path = os.path.join(tmpdir, f"quant_{cfg.strategy}.onnx")
        if cfg.strategy.startswith("static"):
            calib_reader.rewind()
            _do_quantize_static(prepared, quant_path, calib_reader, cfg)
        elif cfg.strategy == "dynamic":
            _do_quantize_dynamic(prepared, quant_path, cfg.weight_type)
        elif cfg.strategy == "fp16":
            _do_quantize_fp16(prepared, quant_path)
        else:
            raise ValueError(f"Unknown strategy: {cfg.strategy}")

        shutil.copy2(quant_path, output_path)

        # 性能测试
        perf = benchmark_model(output_path, input_shape, input_name,
                                cfg.warmup, cfg.runs, cfg.intra_threads)
        result.performance = perf
        result.output_path = output_path
        result.size_ratio = perf.size_kb / max(fp32_perf.size_kb, 1)

        if fp32_perf.success and perf.success:
            result.speedup = fp32_perf.avg_ms / perf.avg_ms

        # 精度验证
        thresholds = cfg.thresholds or AccuracyThresholds()
        acc = validate_accuracy(prepared, output_path, input_shape, input_name,
                                num_samples=50, thresholds=thresholds,
                                intra_threads=cfg.intra_threads,
                                speedup=result.speedup)
        result.accuracy = acc
        result.success = acc.passed and perf.success

        if not acc.passed:
            result.error = acc.fail_reason

    except Exception as e:
        result.error = str(e)
        result.success = False
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return result


def auto_quantize(model_path: str, output_path: str,
                  calib_reader: Optional[CalibrationDataReader] = None,
                  input_shape: Optional[tuple] = None,
                  input_name: Optional[str] = None,
                  config: Optional[QuantizationConfig] = None,
                  verbose: bool = True) -> QuantizationResult:
    """自动量化：检测模型类型 → 选择最优策略 → 精度验证 → 失败自动回滚

    核心逻辑：
    1. 自动检测模型类型(MLP/CNN/Transformer/RNN)
    2. 按实证推荐策略执行量化
    3. 精度+性能双重验证
    4. 不达标时自动按回退链尝试：
       - static QDQ → static QOperator(QUInt8) → dynamic → FP16
       - static QOperator → static QDQ → dynamic → FP16
       - dynamic → FP16
    5. 所有策略均失败时返回错误

    Args:
        model_path: FP32 ONNX模型路径
        output_path: 输出量化模型路径
        calib_reader: 校准数据Reader（None则用随机数据）
        input_shape: 输入形状（None自动检测）
        input_name: 输入名（None自动检测）
        config: 量化配置（None使用自动检测推荐配置）
        verbose: 是否打印进度信息

    Returns:
        QuantizationResult包含完整结果和回滚历史
    """
    if config is None:
        config = QuantizationConfig(strategy="auto")

    # 检测模型类型
    mtype = detect_model_type(model_path, verbose=verbose)
    if verbose:
        print(f"[auto_quantize] Detected model type: {mtype.value}")

    # 确定策略链
    if config.strategy == "auto":
        rec = get_recommended_quant_config(mtype)
        primary_strategy = rec["strategy"]
        fallback_chain = _build_fallback_chain(primary_strategy, rec.get("fallback"))
    else:
        primary_strategy = config.strategy
        fallback_chain = _build_fallback_chain(primary_strategy, None)

    if verbose:
        print(f"[auto_quantize] Primary strategy: {primary_strategy}")
        print(f"[auto_quantize] Fallback chain: {fallback_chain}")

    result = QuantizationResult(model_type=mtype.value)
    tmpdir = tempfile.mkdtemp()

    try:
        prepared = _prepare_model(model_path, tmpdir)
        # 解析输入信息
        if input_shape is None or input_name is None:
            tmp_sess = create_session(prepared, config.intra_threads)
            inp = tmp_sess.get_inputs()[0]
            input_name = input_name or inp.name
            if input_shape is None:
                input_shape = _safe_get_input_shape(inp)
            del tmp_sess

        # FP32基准
        if verbose:
            print("[auto_quantize] Benchmarking FP32 baseline...")
        fp32_perf = benchmark_model(prepared, input_shape, input_name,
                                     config.warmup, config.runs, config.intra_threads)
        result.fp32_performance = fp32_perf

        if calib_reader is None:
            calib_reader = RandomCalibrationReader(input_name, input_shape,
                                                    config.num_calib_samples)

        thresholds = config.thresholds or AccuracyThresholds()

        # 按策略链依次尝试
        all_strategies = [primary_strategy] + fallback_chain
        for idx, strategy in enumerate(all_strategies):
            if verbose:
                tag = "PRIMARY" if idx == 0 else f"FALLBACK-{idx}"
                print(f"[auto_quantize] [{tag}] Trying strategy: {strategy}...")

            attempt_result = _try_strategy(
                prepared, output_path, strategy, calib_reader,
                input_shape, input_name, config, fp32_perf, thresholds, verbose
            )
            result.all_attempts.append({
                "strategy": strategy,
                "success": attempt_result["success"],
                "speedup": attempt_result.get("speedup", 0),
                "max_diff": attempt_result.get("max_diff", -1),
                "error": attempt_result.get("error"),
            })

            if attempt_result["success"]:
                result.success = True
                result.strategy_used = strategy
                result.output_path = output_path
                result.performance = attempt_result["perf"]
                result.accuracy = attempt_result["acc"]
                result.speedup = attempt_result["speedup"]
                result.size_ratio = attempt_result["perf"].size_kb / max(fp32_perf.size_kb, 1)
                result.fallback_triggered = (idx > 0)
                if idx > 0:
                    result.fallback_reason = (
                        f"Primary strategy '{primary_strategy}' failed, "
                        f"fallback to '{strategy}'"
                    )
                if verbose:
                    print(f"[auto_quantize] ✅ Success with {strategy}: "
                          f"speedup={result.speedup:.2f}x, "
                          f"max_diff={result.accuracy.max_diff:.6f}")
                    if result.fallback_triggered:
                        print(f"[auto_quantize] ⚠️  Fallback was triggered: {result.fallback_reason}")
                break
            else:
                if verbose:
                    err = attempt_result.get("error", "validation failed")
                    print(f"[auto_quantize] ❌ {strategy} failed: {err}")

        if not result.success:
            result.error = f"All strategies failed: {[s for s in all_strategies]}"
            if verbose:
                print(f"[auto_quantize] ❌ ALL STRATEGIES FAILED")

    except Exception as e:
        result.error = str(e)
        if verbose:
            print(f"[auto_quantize] ❌ Fatal error: {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return result


def _build_fallback_chain(primary: str, recommended_fallback: Optional[str]) -> list:
    """构建回退策略链"""
    fallback_map = {
        "static_qdq": ["static_qoperator_quint8", "dynamic", "fp16"],
        "static_qoperator": ["static_qoperator_quint8", "static_qdq", "dynamic", "fp16"],
        "static_qoperator_quint8": ["static_qdq", "dynamic", "fp16"],
        "dynamic": ["fp16"],
        "fp16": [],
    }
    chain = fallback_map.get(primary, ["dynamic", "fp16"])
    if recommended_fallback and recommended_fallback not in chain:
        chain.insert(0, recommended_fallback)
    return chain


def _try_strategy(prepared_path: str, output_path: str, strategy: str,
                  calib_reader: CalibrationDataReader,
                  input_shape: tuple, input_name: str,
                  cfg: QuantizationConfig, fp32_perf: BenchmarkResult,
                  thresholds: AccuracyThresholds, verbose: bool) -> dict:
    """尝试单个量化策略"""
    import os
    tmpdir2 = tempfile.mkdtemp()
    out = {"success": False, "speedup": 0, "max_diff": -1}
    try:
        quant_path = os.path.join(tmpdir2, "quant.onnx")

        if strategy == "static_qdq":
            calib_reader.rewind()
            _do_quantize_static(prepared_path, quant_path, calib_reader,
                                QuantizationConfig(quant_format="QDQ",
                                                    activation_type="QInt8",
                                                    weight_type="QInt8",
                                                    per_channel=True,
                                                    exclude_nodes=cfg.exclude_nodes))
        elif strategy == "static_qoperator" or strategy == "static_qoperator_qint8":
            calib_reader.rewind()
            _do_quantize_static(prepared_path, quant_path, calib_reader,
                                QuantizationConfig(quant_format="QOperator",
                                                    activation_type="QInt8",
                                                    weight_type="QInt8",
                                                    per_channel=True,
                                                    exclude_nodes=cfg.exclude_nodes))
        elif strategy == "static_qoperator_quint8":
            calib_reader.rewind()
            _do_quantize_static(prepared_path, quant_path, calib_reader,
                                QuantizationConfig(quant_format="QOperator",
                                                    activation_type="QUInt8",
                                                    weight_type="QInt8",
                                                    per_channel=True,
                                                    exclude_nodes=cfg.exclude_nodes))
        elif strategy == "dynamic":
            _do_quantize_dynamic(prepared_path, quant_path, cfg.weight_type)
        elif strategy == "fp16":
            _do_quantize_fp16(prepared_path, quant_path)
        else:
            out["error"] = f"Unknown strategy: {strategy}"
            shutil.rmtree(tmpdir2, ignore_errors=True)
            return out

        shutil.copy2(quant_path, output_path)

        perf = benchmark_model(output_path, input_shape, input_name,
                                cfg.warmup, cfg.runs, cfg.intra_threads)
        out["perf"] = perf

        if not perf.success:
            out["error"] = f"benchmark failed: {perf.error}"
            shutil.rmtree(tmpdir2, ignore_errors=True)
            return out

        speedup = fp32_perf.avg_ms / perf.avg_ms if fp32_perf.success else 0
        out["speedup"] = speedup

        acc = validate_accuracy(prepared_path, output_path, input_shape, input_name,
                                num_samples=50, thresholds=thresholds,
                                intra_threads=cfg.intra_threads, speedup=speedup)
        out["acc"] = acc
        out["max_diff"] = acc.max_diff

        if acc.passed and perf.success:
            out["success"] = True
        else:
            out["error"] = acc.fail_reason or "performance/accuracy validation failed"

    except Exception as e:
        out["error"] = str(e)
    finally:
        shutil.rmtree(tmpdir2, ignore_errors=True)

    return out
