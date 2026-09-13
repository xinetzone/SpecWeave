# 冒烟测试 3：静态 QDQ INT8 量化（Static QDQ quantization）
#
# 派生产物溯源：提取自
#   apps/docker-images/devcontainer-base/variants/onnx-quantized/Dockerfile
#   Stage 3 [SMOKE] Static QDQ quantization（STATICSMOKE heredoc）
# 语义与源逐行一致：种子 42、两层 MLP 16->32->8（Xavier 1/sqrt(fan_in)）、
# RandomCalib(15)、QDQ/per_channel/QInt8/MinMax、QDQ 节点存在断言、max_diff < 5.0。
# 运行：/opt/conda/envs/main/bin/python smoke_static_qdq.py
import os

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper
from onnxruntime.quantization import (
    CalibrationDataReader,
    CalibrationMethod,
    QuantFormat,
    QuantType,
    quantize_static,
)

rng = np.random.default_rng(42)
IN_DIM, HID_DIM, OUT_DIM = 16, 32, 8
w1 = (rng.standard_normal((IN_DIM, HID_DIM)) / np.sqrt(IN_DIM)).astype(np.float32)
b1 = np.zeros(HID_DIM, dtype=np.float32)
w2 = (rng.standard_normal((HID_DIM, OUT_DIM)) / np.sqrt(HID_DIM)).astype(np.float32)
b2 = np.zeros(OUT_DIM, dtype=np.float32)
nodes = [
    helper.make_node("Gemm", ["input", "w1", "b1"], ["g1"]),
    helper.make_node("Relu", ["g1"], ["r1"]),
    helper.make_node("Gemm", ["r1", "w2", "b2"], ["output"]),
]
graph = helper.make_graph(
    nodes,
    "mlp",
    [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, IN_DIM])],
    [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, OUT_DIM])],
    [
        helper.make_tensor("w1", TensorProto.FLOAT, w1.shape, w1.tobytes(), raw=True),
        helper.make_tensor("b1", TensorProto.FLOAT, b1.shape, b1.tobytes(), raw=True),
        helper.make_tensor("w2", TensorProto.FLOAT, w2.shape, w2.tobytes(), raw=True),
        helper.make_tensor("b2", TensorProto.FLOAT, b2.shape, b2.tobytes(), raw=True),
    ],
)
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.ir_version = min(model.ir_version, 9)
fp32_path, qdq_path = "/tmp/mlp.onnx", "/tmp/mlp_qdq.onnx"
onnx.save(model, fp32_path)


class RandomCalib(CalibrationDataReader):
    def __init__(self, n=10):
        self.data = [
            {"input": rng.standard_normal((1, IN_DIM)).astype(np.float32)} for _ in range(n)
        ]
        self.idx = 0

    def get_next(self):
        if self.idx >= len(self.data):
            return None
        d = self.data[self.idx]
        self.idx += 1
        return d

    def rewind(self):
        self.idx = 0


quantize_static(
    fp32_path,
    qdq_path,
    RandomCalib(15),
    quant_format=QuantFormat.QDQ,
    per_channel=True,
    activation_type=QuantType.QInt8,
    weight_type=QuantType.QInt8,
    calibrate_method=CalibrationMethod.MinMax,
)
onnx.checker.check_model(onnx.load(qdq_path))
m = onnx.load(qdq_path)
qdq_count = sum(1 for n in m.graph.node if n.op_type in ("QuantizeLinear", "DequantizeLinear"))
assert qdq_count > 0, "No QDQ nodes found"
sess_fp32 = ort.InferenceSession(fp32_path, providers=["CPUExecutionProvider"])
sess_qdq = ort.InferenceSession(qdq_path, providers=["CPUExecutionProvider"])
inp = rng.standard_normal((1, IN_DIM)).astype(np.float32)
out_fp32 = sess_fp32.run(None, {"input": inp})[0]
out_qdq = sess_qdq.run(None, {"input": inp})[0]
md = np.max(np.abs(out_fp32 - out_qdq))
assert md < 5.0, f"Static QDQ accuracy loss: {md}"
print(f"[OK] Static QDQ: QDQ nodes={qdq_count}, max_diff={md:.6f}")
os.remove(fp32_path)
os.remove(qdq_path)
