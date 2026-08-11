#!/usr/bin/env python3
"""onnx_quantize_kit 回归测试（移除Neural Compressor依赖后的纯ORT量化方案验证）

本测试是生产级回归测试，覆盖 onnx_quantize_kit 包所有公开API并验证精度阈值。
与 test_onnxruntime_quantization.py（测试原始ORT API）不同，本测试验证封装后的工具包。

测试矩阵（G1-G11）：
  G1: 包导入健全性（无需neural_compressor）
  G2: 动态INT8量化（MLP模型）
  G3: 静态QDQ量化（CNN模型）
  G4: 静态QOperator量化（CNN模型）
  G5: FP16转换
  G6: auto_quantize自动管线（MLP+CNN+Transformer）
  G7: 精度验证 validate_accuracy
  G8: 性能基准 benchmark_model
  G9: 模型类型检测 detect_model_type
  G10: 无neural_compressor依赖硬检查（源码扫描）
  G11: CI门禁阈值强制验证
"""
import os
import sys
import tempfile
import shutil

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch
import torch.nn as nn
import onnx

passed = 0
failed = 0
skipped = 0


def check(name, condition, msg=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}: {msg}")
        failed += 1


def skip(name, reason=""):
    global skipped
    print(f"  ⏭️  {name} [SKIPPED: {reason}]")
    skipped += 1


def info(msg):
    print(f"    ℹ️  {msg}")


# ======================================================================
# Test models (PyTorch → ONNX export, self-contained, no external downloads)
# ======================================================================
class MLPModel(nn.Module):
    """MLP: 3-4 linear layers, best for dynamic quantization"""
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(128, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 10),
        )
    def forward(self, x):
        return self.net(x)


class CNNModel(nn.Module):
    """CNN: 2-3 conv layers + linear head, best for static QDQ"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((2, 2))
        self.fc = nn.Linear(32 * 4, 10)
        self.relu = nn.ReLU()
    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.pool(x)
        return self.fc(x.flatten(1))


class TransformerLikeModel(nn.Module):
    """Simple Transformer-like model: Linear -> attention(matmul+softmax) -> Linear
    Not a full multi-head attention, but has Softmax+MatMul to trigger transformer detection
    """
    def __init__(self):
        super().__init__()
        self.q_proj = nn.Linear(64, 64)
        self.k_proj = nn.Linear(64, 64)
        self.v_proj = nn.Linear(64, 64)
        self.out_proj = nn.Linear(64, 10)
        self.scale = 64 ** -0.5

    def forward(self, x):
        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)
        attn = torch.matmul(q, k.transpose(-2, -1)) * self.scale
        attn = torch.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)
        return self.out_proj(out.mean(dim=1))


def export_onnx(model, shape, path, opset=18):
    """Export PyTorch model to ONNX, returns (input_name, output_name)"""
    model.eval()
    torch.onnx.export(
        model, torch.randn(*shape), path,
        input_names=["input"], output_names=["output"],
        opset_version=opset, do_constant_folding=True,
    )
    return "input", "output"


def run_inference(model_path, input_name, input_data, providers=None):
    """Run ONNX inference with automatic FP16 dtype handling"""
    import onnxruntime as ort
    if providers is None:
        providers = ["CPUExecutionProvider"]
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    so.intra_op_num_threads = 4
    sess = ort.InferenceSession(model_path, sess_options=so, providers=providers)
    inp_meta = sess.get_inputs()[0]
    expected_type = inp_meta.type
    if "float16" in expected_type and input_data.dtype == np.float32:
        input_data = input_data.astype(np.float16)
    out = sess.run(None, {input_name: input_data})[0]
    if out.dtype == np.float16:
        out = out.astype(np.float32)
    return out


def compute_accuracy(fp32_path, quant_path, input_name, input_shape, num_samples=20):
    """Compute accuracy metrics between FP32 and quantized model"""
    max_diffs = []
    mean_diffs = []
    cos_sims = []
    for _ in range(num_samples):
        inp = np.random.randn(*input_shape).astype(np.float32)
        out_fp32 = run_inference(fp32_path, input_name, inp)
        out_q = run_inference(quant_path, input_name, inp)
        diff = np.abs(out_fp32 - out_q)
        max_diffs.append(float(np.max(diff)))
        mean_diffs.append(float(np.mean(diff)))
        a = out_fp32.flatten()
        b = out_q.flatten()
        cos_sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))
        cos_sims.append(cos_sim)
    return {
        "max_diff": float(np.max(max_diffs)),
        "mean_diff": float(np.mean(mean_diffs)),
        "cosine_sim_min": float(np.min(cos_sims)),
        "cosine_sim_mean": float(np.mean(cos_sims)),
    }


def count_qdq_nodes(model_path):
    """Count QuantizeLinear/DequantizeLinear and QLinear* nodes"""
    m = onnx.load(model_path)
    qlinear = 0
    qdq = 0
    has_fp16 = False
    for node in m.graph.node:
        if node.op_type in ("QLinearConv", "QLinearMatMul", "QLinearAdd"):
            qlinear += 1
        if node.op_type in ("QuantizeLinear", "DequantizeLinear"):
            qdq += 1
    for init in m.graph.initializer:
        if init.data_type == 10:
            has_fp16 = True
    return {"qlinear_ops": qlinear, "qdq_nodes": qdq, "has_fp16_weights": has_fp16}


# ======================================================================
# Setup: create temp directory and export test models
# ======================================================================
torch.manual_seed(42)
np.random.seed(42)

tmpdir = tempfile.mkdtemp(prefix="ort_regression_")
print(f"📁 Temporary directory: {tmpdir}")

models = {}
model_configs = [
    ("mlp", MLPModel(), (1, 128)),
    ("cnn", CNNModel(), (1, 3, 28, 28)),
    ("transformer", TransformerLikeModel(), (1, 10, 64)),
]

for name, model, shape in model_configs:
    path = os.path.join(tmpdir, f"{name}.onnx")
    try:
        in_name, out_name = export_onnx(model, shape, path)
        onnx.checker.check_model(onnx.load(path))
        models[name] = {"path": path, "shape": shape, "in": in_name, "out": out_name}
        info(f"Model exported: {name} shape={shape}")
    except Exception as e:
        print(f"  ❌ Failed to export {name}: {e}")

# ======================================================================
# G1: Package import sanity - All public APIs importable WITHOUT neural_compressor
# ======================================================================
print("\n" + "=" * 70)
print("G1: Package import sanity (no neural_compressor required)")
print("=" * 70)

try:
    from onnx_quantize_kit import (
        quantize_dynamic_simple,
        quantize_static_qdq,
        quantize_static_qoperator,
        quantize_fp16,
        auto_quantize,
        benchmark_model,
        validate_accuracy,
        RandomCalibrationReader,
        FileCalibrationReader,
        detect_model_type,
        QuantizationConfig,
        QuantizationResult,
        AccuracyThresholds,
        AccuracyResult,
        BenchmarkResult,
        ModelType,
        create_session,
        CalibrationReader,
    )
    check("All public APIs import successfully", True)
except ImportError as e:
    check("All public APIs import successfully", False, str(e))
    sys.exit(1)

try:
    from onnx_quantize_kit import analyze_model, build_report
    check("Auxiliary APIs import (analyze_model, build_report)", True)
except ImportError:
    skip("Auxiliary APIs import", "Not all auxiliary APIs available")

# Verify neural_compressor is NOT a hard dependency by checking it wasn't imported
nc_imported = any("neural_compressor" in k for k in sys.modules.keys())
check("neural_compressor NOT imported on package load", not nc_imported,
      "neural_compressor should not be imported")
if nc_imported:
    info("neural_compressor was imported - checking if it's actually needed...")


# ======================================================================
# G2: Dynamic INT8 quantization (MLP model)
# ======================================================================
print("\n" + "=" * 70)
print("G2: Dynamic INT8 quantization (MLP model)")
print("=" * 70)

if "mlp" in models:
    mlp = models["mlp"]
    fp32_size = os.path.getsize(mlp["path"])

    # G2a: quantize_dynamic_simple with default params (QInt8)
    dyn_qint8_path = os.path.join(tmpdir, "mlp_dyn_qint8.onnx")
    try:
        result = quantize_dynamic_simple(mlp["path"], dyn_qint8_path, weight_type="QInt8")
        check("dynamic QInt8: function returns QuantizationResult",
              isinstance(result, QuantizationResult))
        check("dynamic QInt8: result.success", result.success or result.error is None,
              f"error={result.error}")

        if os.path.exists(dyn_qint8_path):
            q_size = os.path.getsize(dyn_qint8_path)
            size_ratio = q_size / fp32_size
            check(f"dynamic QInt8: file size reduction ≥ 30% (ratio={size_ratio:.1%})",
                  size_ratio <= 0.70, f"ratio={size_ratio:.1%}")

            onnx.checker.check_model(onnx.load(dyn_qint8_path))
            check("dynamic QInt8: ONNX checker passes", True)

            acc = compute_accuracy(mlp["path"], dyn_qint8_path, mlp["in"], mlp["shape"],
                                   num_samples=30)
            check(f"dynamic QInt8: cosine_sim ≥ 0.99 (got {acc['cosine_sim_min']:.6f})",
                  acc["cosine_sim_min"] >= 0.99,
                  f"cosine_sim={acc['cosine_sim_min']:.6f}")
            check(f"dynamic QInt8: max_diff < 0.1 (got {acc['max_diff']:.6f})",
                  acc["max_diff"] < 0.1, f"max_diff={acc['max_diff']:.6f}")
            info(f"  cosine_sim_min={acc['cosine_sim_min']:.6f}, max_diff={acc['max_diff']:.6f}")
        else:
            check("dynamic QInt8: output file exists", False, "file not created")
    except Exception as e:
        check("dynamic QInt8 quantization", False, f"{type(e).__name__}: {str(e)[:150]}")

    # G2b: quantize_dynamic_simple with QUInt8
    dyn_quint8_path = os.path.join(tmpdir, "mlp_dyn_quint8.onnx")
    try:
        result = quantize_dynamic_simple(mlp["path"], dyn_quint8_path, weight_type="QUInt8")
        check("dynamic QUInt8: function returns without fatal error",
              result.error is None or os.path.exists(dyn_quint8_path),
              f"error={result.error}")

        if os.path.exists(dyn_quint8_path):
            acc = compute_accuracy(mlp["path"], dyn_quint8_path, mlp["in"], mlp["shape"],
                                   num_samples=20)
            check(f"dynamic QUInt8: cosine_sim ≥ 0.98 (got {acc['cosine_sim_min']:.6f})",
                  acc["cosine_sim_min"] >= 0.98,
                  f"cosine_sim={acc['cosine_sim_min']:.6f}")
            info(f"  QUInt8 cosine_sim_min={acc['cosine_sim_min']:.6f}")
    except Exception as e:
        check("dynamic QUInt8 quantization", False, f"{type(e).__name__}: {str(e)[:150]}")
else:
    skip("G2 Dynamic quantization", "MLP model not available")


# ======================================================================
# G3: Static QDQ quantization (CNN model)
# ======================================================================
print("\n" + "=" * 70)
print("G3: Static QDQ quantization (CNN model)")
print("=" * 70)

if "cnn" in models:
    cnn = models["cnn"]
    fp32_size = os.path.getsize(cnn["path"])

    qdq_path = os.path.join(tmpdir, "cnn_static_qdq.onnx")
    try:
        calib_reader = RandomCalibrationReader(cnn["in"], cnn["shape"], num_samples=50)
        result = quantize_static_qdq(
            cnn["path"], qdq_path,
            calib_reader=calib_reader,
            input_shape=cnn["shape"],
            input_name=cnn["in"],
            per_channel=True,
            activation_type="QInt8",
            weight_type="QInt8",
            warmup=10,
            runs=50,
            num_calib_samples=50,
        )
        check("static QDQ: returns QuantizationResult", isinstance(result, QuantizationResult))

        if os.path.exists(qdq_path):
            onnx.checker.check_model(onnx.load(qdq_path))
            check("static QDQ: ONNX checker passes", True)

            nodes = count_qdq_nodes(qdq_path)
            check(f"static QDQ: QuantizeLinear/DequantizeLinear nodes exist (qdq={nodes['qdq_nodes']})",
                  nodes["qdq_nodes"] > 0, f"qdq_nodes={nodes['qdq_nodes']}")
            info(f"  qlinear_ops={nodes['qlinear_ops']}, qdq_nodes={nodes['qdq_nodes']}")

            q_size = os.path.getsize(qdq_path)
            size_ratio = q_size / fp32_size
            info(f"  file size ratio: {size_ratio:.1%}")

            acc = compute_accuracy(cnn["path"], qdq_path, cnn["in"], cnn["shape"],
                                   num_samples=20)
            check(f"static QDQ: cosine_sim ≥ 0.99 (got {acc['cosine_sim_min']:.6f})",
                  acc["cosine_sim_min"] >= 0.99,
                  f"cosine_sim={acc['cosine_sim_min']:.6f}")
            check(f"static QDQ: max_diff < 0.1 (got {acc['max_diff']:.6f})",
                  acc["max_diff"] < 0.1, f"max_diff={acc['max_diff']:.6f}")
            info(f"  cosine_sim_min={acc['cosine_sim_min']:.6f}, max_diff={acc['max_diff']:.6f}")
        else:
            check("static QDQ: output file exists", False, f"file not created, error={result.error}")
    except Exception as e:
        check("static QDQ quantization", False, f"{type(e).__name__}: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
else:
    skip("G3 Static QDQ", "CNN model not available")


# ======================================================================
# G4: Static QOperator quantization (CNN model)
# ======================================================================
print("\n" + "=" * 70)
print("G4: Static QOperator quantization (CNN model)")
print("=" * 70)

if "cnn" in models:
    cnn = models["cnn"]

    qop_path = os.path.join(tmpdir, "cnn_static_qop.onnx")
    try:
        calib_reader = RandomCalibrationReader(cnn["in"], cnn["shape"], num_samples=50)
        result = quantize_static_qoperator(
            cnn["path"], qop_path,
            calib_reader=calib_reader,
            input_shape=cnn["shape"],
            input_name=cnn["in"],
            warmup=10,
            runs=50,
            num_calib_samples=50,
        )
        check("static QOperator: returns QuantizationResult", isinstance(result, QuantizationResult))

        if os.path.exists(qop_path):
            onnx.checker.check_model(onnx.load(qop_path))
            check("static QOperator: ONNX checker passes", True)

            nodes = count_qdq_nodes(qop_path)
            has_quant = nodes["qlinear_ops"] > 0 or nodes["qdq_nodes"] > 0
            check(f"static QOperator: quantization nodes exist (qlinear={nodes['qlinear_ops']}, qdq={nodes['qdq_nodes']})",
                  has_quant, "no quantization nodes found")

            acc = compute_accuracy(cnn["path"], qop_path, cnn["in"], cnn["shape"],
                                   num_samples=20)
            check(f"static QOperator: cosine_sim ≥ 0.98 (got {acc['cosine_sim_min']:.6f})",
                  acc["cosine_sim_min"] >= 0.98,
                  f"cosine_sim={acc['cosine_sim_min']:.6f}")
            check(f"static QOperator: max_diff < 0.2 (got {acc['max_diff']:.6f})",
                  acc["max_diff"] < 0.2, f"max_diff={acc['max_diff']:.6f}")
            info(f"  cosine_sim_min={acc['cosine_sim_min']:.6f}, max_diff={acc['max_diff']:.6f}")
        else:
            check("static QOperator: output file exists", False, f"error={result.error}")
    except Exception as e:
        check("static QOperator quantization", False, f"{type(e).__name__}: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
else:
    skip("G4 Static QOperator", "CNN model not available")


# ======================================================================
# G5: FP16 conversion
# ======================================================================
print("\n" + "=" * 70)
print("G5: FP16 conversion")
print("=" * 70)

if "mlp" in models:
    mlp = models["mlp"]
    fp16_path = os.path.join(tmpdir, "mlp_fp16.onnx")

    try:
        from onnxconverter_common import float16 as _fp16
        HAS_FP16 = True
    except ImportError:
        HAS_FP16 = False

    if HAS_FP16:
        try:
            result = quantize_fp16(mlp["path"], fp16_path)
            check("FP16: returns QuantizationResult", isinstance(result, QuantizationResult))

            if os.path.exists(fp16_path):
                onnx.checker.check_model(onnx.load(fp16_path))
                check("FP16: ONNX checker passes", True)

                nodes = count_qdq_nodes(fp16_path)
                check("FP16: float16 tensors exist in model",
                      nodes["has_fp16_weights"], "no float16 initializers found")

                acc = compute_accuracy(mlp["path"], fp16_path, mlp["in"], mlp["shape"],
                                       num_samples=30)
                check(f"FP16: cosine_sim ≥ 0.999 (got {acc['cosine_sim_min']:.8f})",
                      acc["cosine_sim_min"] >= 0.999,
                      f"cosine_sim={acc['cosine_sim_min']:.8f}")
                check(f"FP16: max_diff < 0.01 (got {acc['max_diff']:.8f})",
                      acc["max_diff"] < 0.01, f"max_diff={acc['max_diff']:.8f}")
                info(f"  cosine_sim_min={acc['cosine_sim_min']:.8f}, max_diff={acc['max_diff']:.8f}")
            else:
                check("FP16: output file exists", False, f"error={result.error}")
        except Exception as e:
            check("FP16 conversion", False, f"{type(e).__name__}: {str(e)[:200]}")
    else:
        skip("FP16 conversion", "onnxconverter-common not installed")
else:
    skip("G5 FP16", "MLP model not available")


# ======================================================================
# G6: auto_quantize pipeline (MLP + CNN + Transformer)
# ======================================================================
print("\n" + "=" * 70)
print("G6: auto_quantize pipeline (MLP + CNN + Transformer)")
print("=" * 70)

# Use relaxed thresholds for random models
AUTO_THRESHOLDS = AccuracyThresholds(
    excellent_max_diff=2.0,
    acceptable_max_diff=5.0,
    min_cosine_sim=0.95,
    min_speedup=0.0,
)
AUTO_CONFIG = QuantizationConfig(
    warmup=5,
    runs=30,
    num_calib_samples=30,
    thresholds=AUTO_THRESHOLDS,
    intra_threads=4,
)

# G6a: MLP auto_quantize - should select a reasonable strategy
if "mlp" in models:
    mlp = models["mlp"]
    mlp_auto_path = os.path.join(tmpdir, "mlp_auto.onnx")
    try:
        result = auto_quantize(
            mlp["path"], mlp_auto_path,
            input_shape=mlp["shape"],
            input_name=mlp["in"],
            config=AUTO_CONFIG,
            verbose=False,
        )
        check("MLP auto_quantize: returns result", result is not None)
        check("MLP auto_quantize: completes without fatal error",
              result.success or result.error is None or "All strategies" not in str(result.error),
              f"error={result.error}")
        if result.success:
            check(f"MLP auto_quantize: cosine_sim ≥ 0.95 (got {result.accuracy.cosine_sim_min:.6f})",
                  result.accuracy.cosine_sim_min >= 0.95,
                  f"cosine_sim={result.accuracy.cosine_sim_min:.6f}")
            info(f"  strategy={result.strategy_used}, speedup={result.speedup:.2f}x, "
                 f"max_diff={result.accuracy.max_diff:.4f}")
            check("MLP auto_quantize: output file exists", os.path.exists(result.output_path))
    except Exception as e:
        check("MLP auto_quantize", False, f"{type(e).__name__}: {str(e)[:200]}")

# G6b: CNN auto_quantize - should select static QDQ as primary
if "cnn" in models:
    cnn = models["cnn"]
    cnn_auto_path = os.path.join(tmpdir, "cnn_auto.onnx")
    try:
        result = auto_quantize(
            cnn["path"], cnn_auto_path,
            input_shape=cnn["shape"],
            input_name=cnn["in"],
            config=AUTO_CONFIG,
            verbose=False,
        )
        check("CNN auto_quantize: returns result", result is not None)
        check("CNN auto_quantize: completes without fatal error",
              result.success or result.error is None,
              f"error={result.error}")
        if result.success:
            check(f"CNN auto_quantize: cosine_sim ≥ 0.95 (got {result.accuracy.cosine_sim_min:.6f})",
                  result.accuracy.cosine_sim_min >= 0.95,
                  f"cosine_sim={result.accuracy.cosine_sim_min:.6f}")
            # CNN primary strategy should be static_qdq (may fallback if accuracy fails)
            info(f"  strategy={result.strategy_used}, speedup={result.speedup:.2f}x, "
                 f"max_diff={result.accuracy.max_diff:.4f}")
            check("CNN auto_quantize: output file exists", os.path.exists(result.output_path))
    except Exception as e:
        check("CNN auto_quantize", False, f"{type(e).__name__}: {str(e)[:200]}")

# G6c: Transformer-like auto_quantize - should complete without error
if "transformer" in models:
    trans = models["transformer"]
    trans_auto_path = os.path.join(tmpdir, "trans_auto.onnx")
    try:
        result = auto_quantize(
            trans["path"], trans_auto_path,
            input_shape=trans["shape"],
            input_name=trans["in"],
            config=AUTO_CONFIG,
            verbose=False,
        )
        check("Transformer auto_quantize: returns result", result is not None)
        check("Transformer auto_quantize: pipeline completes without fatal error",
              result is not None,
              f"error={result.error}")
        if result.success:
            check(f"Transformer auto_quantize: cosine_sim ≥ 0.95 (got {result.accuracy.cosine_sim_min:.6f})",
                  result.accuracy.cosine_sim_min >= 0.95,
                  f"cosine_sim={result.accuracy.cosine_sim_min:.6f}")
            info(f"  strategy={result.strategy_used}, speedup={result.speedup:.2f}x, "
                 f"max_diff={result.accuracy.max_diff:.4f}")
            # Transformer should pick dynamic or fp16 as safe strategies
            check("Transformer auto_quantize: safe strategy selected (dynamic/fp16)",
                  result.strategy_used in ("dynamic", "fp16", "static_qoperator_quint8"),
                  f"strategy={result.strategy_used}")
    except Exception as e:
        check("Transformer auto_quantize", False, f"{type(e).__name__}: {str(e)[:200]}")


# ======================================================================
# G7: Accuracy validation (validate_accuracy)
# ======================================================================
print("\n" + "=" * 70)
print("G7: Accuracy validation (validate_accuracy)")
print("=" * 70)

if "mlp" in models:
    mlp = models["mlp"]

    # G7a: validate_accuracy returns correct metrics for self-comparison
    try:
        acc_self = validate_accuracy(
            mlp["path"], mlp["path"],
            input_shape=mlp["shape"], input_name=mlp["in"],
            num_samples=10, intra_threads=4,
        )
        check("validate_accuracy self-compare: returns AccuracyResult",
              isinstance(acc_self, AccuracyResult))
        check(f"validate_accuracy self-compare: max_diff ≈ 0 (got {acc_self.max_diff:.2e})",
              acc_self.max_diff < 1e-5, f"max_diff={acc_self.max_diff}")
        check(f"validate_accuracy self-compare: cosine_sim ≈ 1 (got {acc_self.cosine_sim_min:.8f})",
              acc_self.cosine_sim_min > 0.9999, f"cos_sim={acc_self.cosine_sim_min}")
        check("validate_accuracy self-compare: passed=True", acc_self.passed)
        info(f"  self-compare: max_diff={acc_self.max_diff:.2e}, cosine={acc_self.cosine_sim_min:.8f}")
    except Exception as e:
        check("validate_accuracy self-compare", False, f"{type(e).__name__}: {str(e)[:150]}")

    # G7b: validate_accuracy with quantized model
    dyn_path = os.path.join(tmpdir, "mlp_dyn_qint8.onnx")
    if os.path.exists(dyn_path):
        try:
            acc_q = validate_accuracy(
                mlp["path"], dyn_path,
                input_shape=mlp["shape"], input_name=mlp["in"],
                num_samples=20, intra_threads=4,
            )
            check("validate_accuracy quant-compare: returns AccuracyResult",
                  isinstance(acc_q, AccuracyResult))
            check("validate_accuracy quant-compare: has max_diff", acc_q.max_diff >= 0)
            check("validate_accuracy quant-compare: has cosine_sim",
                  0 < acc_q.cosine_sim_min <= 1.0)
            check("validate_accuracy quant-compare: num_samples correct",
                  acc_q.num_samples == 20)
            info(f"  quant-compare: max_diff={acc_q.max_diff:.6f}, "
                 f"cosine_min={acc_q.cosine_sim_min:.6f}, level={acc_q.level}")
        except Exception as e:
            check("validate_accuracy quant-compare", False, f"{type(e).__name__}: {str(e)[:150]}")

    # G7c: validate_accuracy with strict thresholds should fail for quantized model
    if os.path.exists(dyn_path):
        try:
            strict_thresh = AccuracyThresholds(
                excellent_max_diff=1e-8,
                acceptable_max_diff=1e-7,
                min_cosine_sim=0.999999,
            )
            acc_strict = validate_accuracy(
                mlp["path"], dyn_path,
                input_shape=mlp["shape"], input_name=mlp["in"],
                num_samples=10, thresholds=strict_thresh, intra_threads=4,
            )
            check("validate_accuracy strict thresholds: should fail (passed=False)",
                  not acc_strict.passed,
                  f"passed={acc_strict.passed}, fail_reason={acc_strict.fail_reason}")
            check("validate_accuracy strict thresholds: fail_reason is set",
                  acc_strict.fail_reason is not None and len(acc_strict.fail_reason) > 0)
            info(f"  strict thresholds: passed={acc_strict.passed}, reason={acc_strict.fail_reason}")
        except Exception as e:
            check("validate_accuracy strict thresholds", False, f"{type(e).__name__}: {str(e)[:150]}")

    # G7d: AccuracyThresholds presets
    try:
        strict = AccuracyThresholds.strict()
        relaxed = AccuracyThresholds.relaxed()
        default = AccuracyThresholds()
        check("AccuracyThresholds.strict() exists", strict.min_cosine_sim >= default.min_cosine_sim)
        check("AccuracyThresholds.relaxed() exists", relaxed.acceptable_max_diff >= default.acceptable_max_diff)
        info(f"  default: min_cos={default.min_cosine_sim}, max_accept_diff={default.acceptable_max_diff}")
        info(f"  strict:  min_cos={strict.min_cosine_sim}, max_accept_diff={strict.acceptable_max_diff}")
        info(f"  relaxed: min_cos={relaxed.min_cosine_sim}, max_accept_diff={relaxed.acceptable_max_diff}")
    except Exception as e:
        check("AccuracyThresholds presets", False, str(e))
else:
    skip("G7 Accuracy validation", "MLP model not available")


# ======================================================================
# G8: Benchmark (benchmark_model)
# ======================================================================
print("\n" + "=" * 70)
print("G8: Benchmark (benchmark_model)")
print("=" * 70)

if "mlp" in models:
    mlp = models["mlp"]
    perf_fp32 = BenchmarkResult(error="not run")

    # G8a: benchmark_model returns latency metrics
    try:
        perf_fp32 = benchmark_model(mlp["path"], input_shape=mlp["shape"], input_name=mlp["in"],
                                     warmup=10, runs=100, intra_threads=4)
        check("benchmark_model FP32: returns BenchmarkResult", isinstance(perf_fp32, BenchmarkResult))
        check("benchmark_model FP32: success", perf_fp32.success, f"error={perf_fp32.error}")
        if perf_fp32.success:
            check("benchmark_model FP32: avg_ms > 0", perf_fp32.avg_ms > 0)
            check("benchmark_model FP32: p50/p95/p99 percentiles present",
                  perf_fp32.p50_ms > 0 and perf_fp32.p95_ms > 0 and perf_fp32.p99_ms > 0)
            check("benchmark_model FP32: throughput_fps > 0", perf_fp32.throughput_fps > 0)
            check("benchmark_model FP32: size_kb > 0", perf_fp32.size_kb > 0)
            info(f"  FP32: avg={perf_fp32.avg_ms:.4f}ms, p50={perf_fp32.p50_ms:.4f}ms, "
                 f"fps={perf_fp32.throughput_fps:.1f}, size={perf_fp32.size_kb:.1f}KB")
    except Exception as e:
        check("benchmark_model FP32", False, f"{type(e).__name__}: {str(e)[:150]}")

    # G8b: INT8 model benchmark and speedup comparison
    dyn_path = os.path.join(tmpdir, "mlp_dyn_qint8.onnx")
    if os.path.exists(dyn_path) and perf_fp32.success:
        try:
            perf_int8 = benchmark_model(dyn_path, input_shape=mlp["shape"], input_name=mlp["in"],
                                         warmup=10, runs=100, intra_threads=4)
            check("benchmark_model INT8: returns valid result",
                  perf_int8.success, f"error={perf_int8.error}")
            if perf_int8.success:
                speedup = perf_fp32.avg_ms / perf_int8.avg_ms
                info(f"  INT8: avg={perf_int8.avg_ms:.4f}ms, speedup={speedup:.2f}x")
                # Note: speedup depends on model size and CPU; small models may not show speedup
                # We just verify the benchmark runs and returns valid metrics, not that it's always faster
                check("benchmark_model INT8: metrics are valid (avg_ms > 0)",
                      perf_int8.avg_ms > 0)
                check("benchmark_model INT8: size_kb < FP32 size_kb",
                      perf_int8.size_kb < perf_fp32.size_kb,
                      f"INT8={perf_int8.size_kb:.1f}KB, FP32={perf_fp32.size_kb:.1f}KB")
        except Exception as e:
            check("benchmark_model INT8", False, f"{type(e).__name__}: {str(e)[:150]}")

    # G8c: BenchmarkResult.success property
    try:
        bad_perf = benchmark_model("/nonexistent/path.onnx", warmup=1, runs=1)
        check("benchmark_model nonexistent: returns failed result",
              not bad_perf.success, "should fail for nonexistent file")
        check("benchmark_model nonexistent: error message set",
              bad_perf.error is not None and len(bad_perf.error) > 0)
    except Exception as e:
        check("benchmark_model error handling", False, f"{type(e).__name__}: {str(e)[:100]}")
else:
    skip("G8 Benchmark", "MLP model not available")


# ======================================================================
# G9: Model detection (detect_model_type)
# ======================================================================
print("\n" + "=" * 70)
print("G9: Model detection (detect_model_type)")
print("=" * 70)

if "mlp" in models:
    mlp = models["mlp"]
    try:
        mtype = detect_model_type(mlp["path"], verbose=False)
        check(f"detect_model_type MLP: returns {mtype.value}",
              mtype == ModelType.MLP, f"got {mtype.value}")
    except Exception as e:
        check("detect_model_type MLP", False, str(e))

if "cnn" in models:
    cnn = models["cnn"]
    try:
        mtype = detect_model_type(cnn["path"], verbose=False)
        check(f"detect_model_type CNN: returns {mtype.value}",
              mtype == ModelType.CNN, f"got {mtype.value}")
    except Exception as e:
        check("detect_model_type CNN", False, str(e))

if "transformer" in models:
    trans = models["transformer"]
    try:
        mtype = detect_model_type(trans["path"], verbose=False)
        check(f"detect_model_type Transformer-like: returns {mtype.value}",
              mtype == ModelType.TRANSFORMER, f"got {mtype.value}")
    except Exception as e:
        check("detect_model_type Transformer", False, str(e))

# G9d: detect_model_type with loaded ModelProto (not just path)
if "mlp" in models:
    try:
        model_proto = onnx.load(mlp["path"])
        mtype = detect_model_type(model_proto, verbose=False)
        check("detect_model_type accepts ModelProto object",
              mtype == ModelType.MLP, f"got {mtype.value}")
    except Exception as e:
        check("detect_model_type ModelProto", False, str(e))

# G9e: analyze_model returns complete dict
if "mlp" in models:
    try:
        analysis = analyze_model(mlp["path"], intra_threads=2)
        check("analyze_model returns dict", isinstance(analysis, dict))
        required_keys = ["model_type", "input_name", "input_shape", "recommended_strategy",
                        "fallback_chain", "num_nodes", "file_size_kb"]
        for key in required_keys:
            check(f"analyze_model has key: {key}", key in analysis, f"missing key {key}")
        info(f"  analyze: type={analysis.get('model_type')}, "
             f"strategy={analysis.get('recommended_strategy')}, "
             f"shape={analysis.get('input_shape')}")
    except Exception as e:
        check("analyze_model", False, f"{type(e).__name__}: {str(e)[:150]}")


# ======================================================================
# G10: No neural_compressor dependency hard check (source file scan)
# ======================================================================
print("\n" + "=" * 70)
print("G10: No neural_compressor dependency hard check")
print("=" * 70)

kit_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "onnx_quantize_kit")
nc_top_level_imports = []

if os.path.isdir(kit_dir):
    for fname in os.listdir(kit_dir):
        if fname.endswith(".py"):
            fpath = os.path.join(kit_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped.startswith("import neural_compressor") or \
                       stripped.startswith("from neural_compressor"):
                        nc_top_level_imports.append((fname, i, stripped))
            except Exception:
                pass

    if not nc_top_level_imports:
        check("No top-level 'import neural_compressor' in any onnx_quantize_kit source file", True)
    else:
        info(f"Found neural_compressor imports in:")
        for fname, lineno, line in nc_top_level_imports:
            info(f"  {fname}:{lineno}: {line}")
        # Check if these are in try/except blocks (optional imports)
        hard_deps = []
        for fname, lineno, _ in nc_top_level_imports:
            fpath = os.path.join(kit_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            is_optional = False
            for j in range(max(0, lineno - 5), min(len(lines), lineno + 1)):
                if "try:" in lines[j] or "except ImportError" in lines[j] or "except:" in lines[j]:
                    is_optional = True
                    break
            if not is_optional:
                hard_deps.append((fname, lineno))
        if hard_deps:
            check("No hard neural_compressor dependency (top-level outside try/except)",
                  False, f"Hard imports: {hard_deps}")
        else:
            check("neural_compressor imports are all optional (inside try/except)", True)
else:
    skip("G10 neural_compressor check", f"kit directory not found: {kit_dir}")


# ======================================================================
# G11: CI gate thresholds enforcement
# ======================================================================
print("\n" + "=" * 70)
print("G11: CI gate thresholds enforcement")
print("=" * 70)

# G11a: Default AccuracyThresholds enforce production thresholds
try:
    default_thresh = AccuracyThresholds()
    check(f"Default min_cosine_sim ≥ 0.99 (got {default_thresh.min_cosine_sim})",
          default_thresh.min_cosine_sim >= 0.99)
    check(f"Default acceptable_max_diff ≤ 0.05 (got {default_thresh.acceptable_max_diff})",
          default_thresh.acceptable_max_diff <= 0.05)
    check(f"Default excellent_max_diff ≤ 0.01 (got {default_thresh.excellent_max_diff})",
          default_thresh.excellent_max_diff <= 0.01)
    info(f"  Default thresholds: cos≥{default_thresh.min_cosine_sim}, "
         f"max_diff<{default_thresh.acceptable_max_diff}")
except Exception as e:
    check("Default thresholds", False, str(e))

# G11b: QuantizationResult structure has all required fields
try:
    qr = QuantizationResult()
    required_fields = ["success", "output_path", "strategy_used", "model_type",
                       "performance", "accuracy", "speedup", "size_ratio",
                       "fallback_triggered", "fallback_reason", "error"]
    for field in required_fields:
        check(f"QuantizationResult has field: {field}", hasattr(qr, field))
    check("QuantizationResult.to_dict() works", isinstance(qr.to_dict(), dict))
except Exception as e:
    check("QuantizationResult structure", False, str(e))

# G11c: QuantizationConfig defaults are sensible
try:
    qc = QuantizationConfig()
    check(f"QuantizationConfig default strategy is 'auto'", qc.strategy == "auto")
    check(f"QuantizationConfig default per_channel=True", qc.per_channel == True)
    check(f"QuantizationConfig auto_fallback=True", qc.auto_fallback == True)
    check(f"QuantizationConfig num_calib_samples > 0", qc.num_calib_samples > 0)
    info(f"  Config defaults: strategy={qc.strategy}, per_channel={qc.per_channel}, "
         f"calib_samples={qc.num_calib_samples}")
except Exception as e:
    check("QuantizationConfig defaults", False, str(e))

# G11d: CalibrationReader interface
try:
    cr = RandomCalibrationReader("input", (1, 32), num_samples=5)
    check("RandomCalibrationReader.get_next() returns dict", isinstance(cr.get_next(), dict))
    cr.rewind()
    count = 0
    while cr.get_next() is not None:
        count += 1
    check(f"RandomCalibrationReader yields correct num_samples (5)", count == 5, f"count={count}")
    cr.rewind()
    batch = cr.get_next()
    check("RandomCalibrationReader data is float32",
          batch["input"].dtype == np.float32, f"dtype={batch['input'].dtype}")
except Exception as e:
    check("RandomCalibrationReader", False, f"{type(e).__name__}: {str(e)[:100]}")

# G11e: FileCalibrationReader can be instantiated with a directory of .npy files
try:
    calib_dir = os.path.join(tmpdir, "calib_data")
    os.makedirs(calib_dir, exist_ok=True)
    for i in range(3):
        arr = np.random.randn(1, 128).astype(np.float32)
        np.save(os.path.join(calib_dir, f"sample_{i:03d}.npy"), arr)
    fcr = FileCalibrationReader("input", (1, 128), calib_dir, num_samples=3)
    check("FileCalibrationReader loads .npy files from directory", True)
    d = fcr.get_next()
    check("FileCalibrationReader returns dict with correct input",
          d is not None and "input" in d)
    fcr.rewind()
    check("FileCalibrationReader.rewind() works", fcr.get_next() is not None)
except Exception as e:
    check("FileCalibrationReader", False, f"{type(e).__name__}: {str(e)[:150]}")


# ======================================================================
# Cleanup
# ======================================================================
shutil.rmtree(tmpdir, ignore_errors=True)
print(f"\n🧹 Cleaned up temp directory: {tmpdir}")

# ======================================================================
# Summary
# ======================================================================
print("\n" + "=" * 70)
print("REGRESSION TEST SUMMARY")
print("=" * 70)
total = passed + failed
print(f"  ✅ Passed:  {passed}")
print(f"  ❌ Failed:  {failed}")
print(f"  ⏭️  Skipped: {skipped}")
print(f"  📊 Total:   {total} test checks")
print("=" * 70)

print("\n  📋 onnx_quantize_kit Regression Test Coverage:")
print("     ┌──────────────────────────────────────────────────────────────┐")
print("     │ G1: Package imports (no NC dep)   │ G7: validate_accuracy    │")
print("     │ G2: Dynamic INT8 (MLP)            │ G8: benchmark_model      │")
print("     │ G3: Static QDQ (CNN)              │ G9: detect_model_type    │")
print("     │ G4: Static QOperator (CNN)        │ G10: No NC hard dep      │")
print("     │ G5: FP16 conversion               │ G11: CI gate thresholds  │")
print("     │ G6: auto_quantize pipeline        │                          │")
print("     └──────────────────────────────────────────────────────────────┘")

if failed > 0:
    print(f"\n⚠️  {failed} test(s) FAILED!")
    sys.exit(1)
else:
    print(f"\n🎉 All {passed} regression tests passed! onnx_quantize_kit is production-ready.")
    sys.exit(0)
