"""模型类型自动检测模块"""
import enum
from typing import Optional

import onnx


class ModelType(enum.Enum):
    """检测到的模型类型"""
    MLP = "mlp"           # 全连接网络（仅MatMul/Gemm/Add/Relu）
    CNN = "cnn"           # 卷积网络（含Conv）
    TRANSFORMER = "transformer"  # Transformer（含Attention/LayerNorm/Softmax链）
    RNN = "rnn"           # 循环网络（含LSTM/GRU/RNN）
    UNKNOWN = "unknown"


def detect_model_type(model_or_path, verbose: bool = False) -> ModelType:
    """通过ONNX图算子组合自动检测模型类型

    检测逻辑：
    1. 含LayerNorm+Softmax+MatMul链 → Transformer
    2. 含Conv → CNN
    3. 含LSTM/GRU/RNN → RNN
    4. 仅MatMul/Gemm → MLP
    5. 其他 → UNKNOWN

    Args:
        model_or_path: onnx.ModelProto或模型文件路径
        verbose: 是否打印检测详情

    Returns:
        ModelType枚举值
    """
    if isinstance(model_or_path, str):
        model = onnx.load(model_or_path, load_external_data=False)
    else:
        model = model_or_path

    op_types = set()
    op_counts = {}
    for node in model.graph.node:
        op = node.op_type
        op_types.add(op)
        op_counts[op] = op_counts.get(op, 0) + 1

    has_conv = "Conv" in op_types
    has_matmul = "MatMul" in op_types or "Gemm" in op_types
    has_layernorm = "LayerNormalization" in op_types or "SkipLayerNormalization" in op_types
    has_softmax = "Softmax" in op_types
    has_attention = "Attention" in op_types or "MultiHeadAttention" in op_types
    has_rnn = any(op in op_types for op in ("LSTM", "GRU", "RNN"))

    # 评分判定
    transformer_score = 0
    if has_layernorm:
        transformer_score += 2
    if has_softmax and has_matmul:
        transformer_score += 1
    if has_attention:
        transformer_score += 3

    if verbose:
        print(f"  Op distribution: {sorted(op_counts.items(), key=lambda x: -x[1])[:15]}")
        print(f"  Transformer score: {transformer_score} "
              f"(LN={has_layernorm}, Softmax+MM={has_softmax and has_matmul}, Attn={has_attention})")

    if transformer_score >= 2:
        return ModelType.TRANSFORMER
    if has_rnn:
        return ModelType.RNN
    if has_conv:
        return ModelType.CNN
    if has_matmul and not has_conv and not has_layernorm:
        return ModelType.MLP
    return ModelType.UNKNOWN


def get_recommended_quant_config(model_type: ModelType) -> dict:
    """根据模型类型返回推荐的量化配置

    基于全量基准测试实证结论：
    - MLP(大): QOperator+QUInt8/QInt8 最优 (6.39x加速)
    - MLP(小,<200KB): 不量化或FP16 (INT8反而更慢)
    - CNN: QDQ+QInt8/QInt8 最优 (1.22x加速，兼容性最好)
    - Transformer: 动态量化 (静态QDQ/QOperator精度灾难)
    - RNN: 动态量化
    """
    configs = {
        ModelType.MLP: {
            "strategy": "static_qoperator",
            "quant_format": "QOperator",
            "activation_type": "QUInt8",
            "weight_type": "QInt8",
            "per_channel": True,
            "fallback": "dynamic",
        },
        ModelType.CNN: {
            "strategy": "static_qdq",
            "quant_format": "QDQ",
            "activation_type": "QInt8",
            "weight_type": "QInt8",
            "per_channel": True,
            "fallback": "static_qoperator_quint8",
        },
        ModelType.TRANSFORMER: {
            "strategy": "dynamic",
            "weight_type": "QInt8",
            "fallback": "fp16",
        },
        ModelType.RNN: {
            "strategy": "dynamic",
            "weight_type": "QInt8",
            "fallback": "fp16",
        },
        ModelType.UNKNOWN: {
            "strategy": "static_qdq",
            "quant_format": "QDQ",
            "activation_type": "QInt8",
            "weight_type": "QInt8",
            "per_channel": True,
            "fallback": "dynamic",
        },
    }
    return configs.get(model_type, configs[ModelType.UNKNOWN])
