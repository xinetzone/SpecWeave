"""onnx_quantize_kit - ONNX模型量化可复用工具包

提供统一的校准、基准测试、精度验证、自动量化选型和CI门禁能力。

快速开始:
    from onnx_quantize_kit import auto_quantize, benchmark_model, validate_accuracy

    # 自动量化（自动检测模型类型选择最优格式，精度不达标自动回滚）
    result = auto_quantize("model.onnx", "model_int8.onnx", calib_dir="./calib/")

    # 性能基准测试
    perf = benchmark_model("model_int8.onnx", (1,3,224,224))

    # 精度验证
    acc = validate_accuracy("model.onnx", "model_int8.onnx", (1,3,224,224))
"""
from .calibration import CalibrationReader, RandomCalibrationReader, FileCalibrationReader
from .benchmark import benchmark_model, create_session, BenchmarkResult
from .accuracy import validate_accuracy, AccuracyResult, AccuracyThresholds
from .model_detect import detect_model_type, ModelType, analyze_model
from .quantize import (
    auto_quantize, quantize_dynamic_simple, quantize_static_qdq,
    quantize_static_qoperator, quantize_fp16, QuantizationResult, QuantizationConfig,
)
from .reporting import build_report, parse_report, format_summary, format_batch_summary

__version__ = "1.0.0"
__all__ = [
    "CalibrationReader", "RandomCalibrationReader", "FileCalibrationReader",
    "benchmark_model", "create_session", "BenchmarkResult",
    "validate_accuracy", "AccuracyResult", "AccuracyThresholds",
    "detect_model_type", "ModelType", "analyze_model",
    "auto_quantize", "quantize_dynamic_simple", "quantize_static_qdq",
    "quantize_static_qoperator", "quantize_fp16",
    "QuantizationResult", "QuantizationConfig",
    "build_report", "parse_report", "format_summary", "format_batch_summary",
]
