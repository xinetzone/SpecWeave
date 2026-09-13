# 冒烟测试 2：FP16 半精度转换（FP16 conversion）
#
# 派生产物溯源：提取自
#   apps/docker-images/devcontainer-base/variants/onnx-quantized/Dockerfile
#   Stage 3 [SMOKE] FP16 conversion（FP16SMOKE heredoc）
# 语义与源逐行一致：种子 42、Gemm+Mul+Add 8x4、onnxconverter_common.float16、
# max_diff < 5.0。
# 运行：/opt/conda/envs/main/bin/python smoke_fp16.py
import os

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper
from onnxconverter_common import float16

rng = np.random.default_rng(42)
IN_DIM, OUT_DIM = 8, 4
w = (rng.standard_normal((IN_DIM, OUT_DIM)) * 0.1).astype(np.float32)
b = np.zeros(OUT_DIM, dtype=np.float32)
half = np.array([0.5], dtype=np.float32)
one = np.array([1.0], dtype=np.float32)
nodes = [
    helper.make_node("Gemm", ["input", "w", "b"], ["gemm_out"]),
    helper.make_node("Mul", ["gemm_out", "half"], ["mul_out"]),
    helper.make_node("Add", ["mul_out", "one"], ["output"]),
]
graph = helper.make_graph(
    nodes,
    "simple",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT_DIM])],
    [
        helper.make_tensor("w", TensorProto.FLOAT, w.shape, w.tobytes(), raw=True),
        helper.make_tensor("b", TensorProto.FLOAT, b.shape, b.tobytes(), raw=True),
        helper.make_tensor("half", TensorProto.FLOAT, half.shape, half.tobytes(), raw=True),
        helper.make_tensor("one", TensorProto.FLOAT, one.shape, one.tobytes(), raw=True),
    ],
)
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
fp32_path, fp16_path = "/tmp/test_fp32.onnx", "/tmp/test_fp16.onnx"
onnx.save(model, fp32_path)
fp16_model = float16.convert_float_to_float16(onnx.load(fp32_path))
onnx.save(fp16_model, fp16_path)
onnx.checker.check_model(onnx.load(fp16_path))
sess_fp32 = ort.InferenceSession(fp32_path, providers=["CPUExecutionProvider"])
sess_fp16 = ort.InferenceSession(fp16_path, providers=["CPUExecutionProvider"])
inp = rng.standard_normal((1, IN_DIM)).astype(np.float32)
out_fp32 = sess_fp32.run(None, {"input": inp})[0]
out_fp16 = sess_fp16.run(None, {"input": inp.astype(np.float16)})[0]
md = np.max(np.abs(out_fp16.astype(np.float32) - out_fp32))
assert md < 5.0, f"FP16 precision loss too high: {md}"
fp32_sz, fp16_sz = os.path.getsize(fp32_path), os.path.getsize(fp16_path)
print(f"[OK] FP16 conversion: max_diff={md:.6f}, size FP32={fp32_sz}B FP16={fp16_sz}B ({fp16_sz/fp32_sz:.1%})")
os.remove(fp32_path)
os.remove(fp16_path)
