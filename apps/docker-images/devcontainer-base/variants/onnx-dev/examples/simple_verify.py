#!/usr/bin/env python3
"""简单 ONNX 环境验证脚本 - 测试容器内 Python/ONNX 基本功能"""
import sys
import os

print("=" * 60)
print("  ONNX Dev Container - Simple Environment Test")
print("=" * 60)
print()

# 1. Python 版本与 GIL 状态
print(f"[1] Python 版本: {sys.version}")
print(f"    执行路径: {sys.executable}")
gil_enabled = getattr(sys, '_is_gil_enabled', lambda: True)()
print(f"    GIL 状态: {'禁用 (free-threading)' if not gil_enabled else '启用'}")
print()

# 2. 工作目录检查
workspace = "/workspace"
print(f"[2] 工作目录: {os.getcwd()}")
print(f"    /workspace 存在: {os.path.exists(workspace)}")
print(f"    挂载目录内容: {os.listdir(workspace)[:10]}")
print()

# 3. ONNX 生态导入测试
print("[3] 导入 ONNX 生态组件...")
try:
    import onnx
    print(f"    ✅ onnx {onnx.__version__}")
except Exception as e:
    print(f"    ❌ onnx 导入失败: {e}")
    sys.exit(1)

try:
    import onnxruntime as ort
    print(f"    ✅ onnxruntime {ort.__version__}")
except Exception as e:
    print(f"    ❌ onnxruntime 导入失败: {e}")
    sys.exit(1)

try:
    import numpy as np
    print(f"    ✅ numpy {np.__version__}")
except Exception as e:
    print(f"    ❌ numpy 导入失败: {e}")
    sys.exit(1)

# 可选组件
try:
    import onnxsim
    print(f"    ✅ onnxsim {onnxsim.__version__}")
except ImportError:
    print(f"    ⚠️  onnxsim 未安装（可选）")

try:
    import onnxscript
    print(f"    ✅ onnxscript {onnxscript.__version__}")
except ImportError:
    print(f"    ⚠️  onnxscript 未安装（可选）")

try:
    import torch
    print(f"    ⚠️  torch {torch.__version__} 已安装（预期不存在）")
except ImportError:
    print(f"    ✅ torch 未安装（符合预期）")

print()

# 4. 创建并运行一个简单 ONNX 模型
print("[4] 创建并运行简单 ONNX Add 模型...")
from onnx import helper, TensorProto, checker

# 创建一个简单的 Add 模型: Z = X + Y
X = helper.make_tensor_value_info('X', TensorProto.FLOAT, [None, 3])
Y = helper.make_tensor_value_info('Y', TensorProto.FLOAT, [None, 3])
Z = helper.make_tensor_value_info('Z', TensorProto.FLOAT, [None, 3])

node_def = helper.make_node(
    'Add',
    inputs=['X', 'Y'],
    outputs=['Z'],
)

graph_def = helper.make_graph(
    [node_def],
    'add_model',
    [X, Y],
    [Z],
)

model_def = helper.make_model(
    graph_def,
    producer_name='onnx-test',
    opset_imports=[helper.make_opsetid('', 13)]
)
checker.check_model(model_def)
print("    ✅ 模型创建并验证通过")

# 推理测试
sess = ort.InferenceSession(model_def.SerializeToString())
x = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
y = np.array([[4.0, 5.0, 6.0]], dtype=np.float32)
z = sess.run(None, {'X': x, 'Y': y})[0]

expected = np.array([[5.0, 7.0, 9.0]], dtype=np.float32)
if np.allclose(z, expected):
    print(f"    ✅ 推理结果正确: {x} + {y} = {z}")
else:
    print(f"    ❌ 推理结果错误: 期望 {expected}, 实际 {z}")
    sys.exit(1)

print()
print("=" * 60)
print("  ✅ 所有测试通过！容器环境正常")
print("=" * 60)
