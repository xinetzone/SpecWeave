# 冒烟测试 1：动态 INT8 量化（Dynamic INT8 quantization）
#
# 派生产物溯源：提取自
#   apps/docker-images/devcontainer-base/variants/onnx-quantized/Dockerfile
#   Stage 3 [SMOKE] Dynamic INT8 quantization（QSMOKE heredoc）
# 语义与源逐行一致：种子 42、Gemm 10x5、权重 *0.1、QInt8、max_diff < 5.0。
# 运行：/opt/conda/envs/main/bin/python smoke_dynamic_int8.py
import os

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper
from onnxruntime.quantization import QuantType, quantize_dynamic

rng = np.random.default_rng(42)
IN_DIM, OUT_DIM = 10, 5
w = (rng.standard_normal((IN_DIM, OUT_DIM)) * 0.1).astype(np.float32)
b = np.zeros(OUT_DIM, dtype=np.float32)
nodes = [helper.make_node("Gemm", ["input", "w", "b"], ["output"])]
graph = helper.make_graph(
    nodes,
    "linear",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT_DIM])],
    [
        helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
        helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True),
    ],
)
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
onnx_path, quant_path = "/tmp/test_model.onnx", "/tmp/test_model_int8.onnx"
onnx.save(model, onnx_path)
quantize_dynamic(onnx_path, quant_path, weight_type=QuantType.QInt8)
onnx.checker.check_model(onnx.load(quant_path))
sess_fp32 = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
sess_int8 = ort.InferenceSession(quant_path, providers=["CPUExecutionProvider"])
inp = rng.standard_normal((1, IN_DIM)).astype(np.float32)
out_fp32 = sess_fp32.run(None, {"input": inp})[0]
out_int8 = sess_int8.run(None, {"input": inp})[0]
md = np.max(np.abs(out_fp32 - out_int8))
assert md < 5.0, f"Quantization accuracy loss too high: {md}"
fp32_sz, int8_sz = os.path.getsize(onnx_path), os.path.getsize(quant_path)
print(f"[OK] Dynamic INT8: max_diff={md:.6f}, size FP32={fp32_sz}B INT8={int8_sz}B ({int8_sz/fp32_sz:.1%})")
os.remove(onnx_path)
os.remove(quant_path)
