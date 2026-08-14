"""onnx_quantize_kit - ONNX模型量化可复用工具包

基于 onnxruntime.quantization 原生API构建的生产级量化工具包，零额外重量级依赖。

提供统一的校准、基准测试、精度验证、自动量化选型和CI门禁能力。

================================================================================
📌 量化引擎说明
================================================================================
- **核心引擎（唯一）**: onnxruntime.quantization（随 onnxruntime 包内置提供）
  - 支持：动态INT8 / 静态QDQ / 静态QOperator / FP16 转换
  - 零额外运行时依赖，与ONNX Runtime推理引擎100%兼容
- **不包含**: Intel Neural Compressor (INC)
  - INC 3.x已弃用ONNX适配器（PR intel/neural-compressor#2199），聚焦PyTorch
  - 如需PyTorch权重量化（RTN/AWQ/GPTQ/AutoRound），可单独 pip install neural-compressor
  - 本工具包不依赖INC，INC的缺失不影响任何ONNX量化功能

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
