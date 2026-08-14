"""模型类型自动检测与分析模块"""
import enum
import os
from typing import Any, Dict, Optional

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


def analyze_model(model_path: str, intra_threads: int = 4) -> Dict[str, Any]:
    """分析 ONNX 模型，返回模型类型、推荐策略链、输入信息等结构化结果。

    对应 CLI 的 --dry-run 功能，可独立调用用于脚本集成。

    Args:
        model_path: ONNX 模型文件路径
        intra_threads: ORT 推理线程数（用于创建 session 检测输入形状）

    Returns:
        分析结果 dict，包含以下字段：
        - model_path: 模型绝对路径
        - model_name: 文件名
        - file_size_kb: 文件大小(KB)
        - opset_version: ONNX opset 版本
        - ir_version: IR 版本
        - model_type: 检测到的模型类型字符串 (mlp/cnn/transformer/rnn/unknown)
        - recommended_strategy: 推荐的主策略
        - fallback_chain: 完整回退策略链列表 [primary, fallback1, fallback2, ...]
        - strategy_chain: 人类可读的策略链字符串 "primary → fb1 → fb2"
        - input_name: 第一个输入节点名
        - input_shape: 输入形状 tuple（动态维度替换为默认值）
        - output_name: 第一个输出节点名
        - num_inputs: 输入节点数量
        - num_outputs: 输出节点数量
        - num_nodes: 计算图节点数量

    Raises:
        FileNotFoundError: 模型文件不存在
    """
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    abs_path = os.path.abspath(model_path)
    model = onnx.load(abs_path, load_external_data=False)

    file_size = os.path.getsize(abs_path) / 1024
    opset = model.opset_import[0].version if model.opset_import else 0

    # 模型类型检测
    mtype = detect_model_type(model, verbose=False)

    # 推荐策略 + fallback chain
    rec = get_recommended_quant_config(mtype)
    primary = rec["strategy"]
    recommended_fb = rec.get("fallback")

    # 延迟导入避免循环依赖
    from .quantize import _build_fallback_chain
    fb_chain = _build_fallback_chain(primary, recommended_fb)
    full_chain = [primary] + fb_chain
    chain_str = " → ".join(full_chain)

    # 输入/输出信息（延迟导入创建 session）
    input_name = ""
    input_shape = ()
    output_name = ""
    num_inputs = len(model.graph.input)
    num_outputs = len(model.graph.output)
    num_nodes = len(model.graph.node)

    try:
        from .benchmark import create_session
        from .quantize import _safe_get_input_shape
        sess = create_session(abs_path, intra_threads)
        inp = sess.get_inputs()[0]
        out = sess.get_outputs()[0]
        input_name = inp.name
        input_shape = _safe_get_input_shape(inp)
        output_name = out.name
        del sess
    except Exception:
        # Session 创建失败时用 onnx 图信息兜底
        try:
            inp = model.graph.input[0]
            output_name = model.graph.output[0].name
            dims = []
            for d in inp.type.tensor_type.shape.dim:
                if d.dim_value > 0:
                    dims.append(d.dim_value)
                else:
                    dims.append(1)
            input_name = inp.name
            input_shape = tuple(dims) if dims else ()
        except Exception:
            pass

    return {
        "model_path": abs_path,
        "model_name": os.path.basename(abs_path),
        "file_size_kb": round(file_size, 1),
        "opset_version": opset,
        "ir_version": model.ir_version,
        "model_type": mtype.value,
        "recommended_strategy": primary,
        "fallback_chain": fb_chain,
        "strategy_chain": chain_str,
        "input_name": input_name,
        "input_shape": input_shape,
        "output_name": output_name,
        "num_inputs": num_inputs,
        "num_outputs": num_outputs,
        "num_nodes": num_nodes,
    }
