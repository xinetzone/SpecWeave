"""
ONNX Dev 容器推理示例脚本
演示：模型创建 → 保存 → 加载 → onnxruntime 推理 → 结果验证
注意：onnx 1.22 默认 opset 27 > onnxruntime 1.28 支持上限 26，需显式设置 opset=13
"""
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper
import onnxruntime as ort
import time

def create_simple_linear_model():
    """创建一个简单的线性模型: y = W @ x + b (2层MLP片段)"""
    # 输入输出定义
    X = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 3, 224, 224])
    Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 1000])

    # 创建权重 (实际使用时从训练框架导出)
    w1 = np.random.randn(3, 64).astype(np.float32) * 0.01
    b1 = np.zeros(64, dtype=np.float32)
    w2 = np.random.randn(64, 1000).astype(np.float32) * 0.01
    b2 = np.zeros(1000, dtype=np.float32)

    # 节点定义
    # 先做全局平均池化: [1,3,224,224] -> [1,3,1,1] -> [1,3]
    node_gap = helper.make_node(
        'GlobalAveragePool',
        inputs=['input'],
        outputs=['gap_out'],
    )
    node_flatten = helper.make_node(
        'Flatten',
        inputs=['gap_out'],
        outputs=['flatten_out'],
        axis=1,
    )
    node_matmul1 = helper.make_node(
        'MatMul',
        inputs=['flatten_out', 'W1'],
        outputs=['matmul1_out'],
    )
    node_add1 = helper.make_node(
        'Add',
        inputs=['matmul1_out', 'B1'],
        outputs=['add1_out'],
    )
    node_relu = helper.make_node(
        'Relu',
        inputs=['add1_out'],
        outputs=['relu_out'],
    )
    node_matmul2 = helper.make_node(
        'MatMul',
        inputs=['relu_out', 'W2'],
        outputs=['matmul2_out'],
    )
    node_add2 = helper.make_node(
        'Add',
        inputs=['matmul2_out', 'B2'],
        outputs=['output'],
    )

    # 初始值（权重）
    initializers = [
        numpy_helper.from_array(w1, name='W1'),
        numpy_helper.from_array(b1, name='B1'),
        numpy_helper.from_array(w2, name='W2'),
        numpy_helper.from_array(b2, name='B2'),
    ]

    # 创建图和模型
    graph = helper.make_graph(
        nodes=[node_gap, node_flatten, node_matmul1, node_add1, node_relu, node_matmul2, node_add2],
        name='simple_linear_model',
        inputs=[X],
        outputs=[Y],
        initializer=initializers,
    )

    # 关键：显式设置 opset_imports 到 13（onnxruntime 1.28 支持上限）
    model = helper.make_model(
        graph,
        opset_imports=[helper.make_opsetid('', 13)],  # onnx 1.22 默认 opset 27 需降下来
        producer_name='onnx-dev-demo',
    )
    model.ir_version = 9  # 兼容性
    return model

def create_add_model():
    """创建最简单的 Add 模型用于基础验证"""
    X = helper.make_tensor_value_info('a', TensorProto.FLOAT, [None, None])
    Y = helper.make_tensor_value_info('b', TensorProto.FLOAT, [None, None])
    Z = helper.make_tensor_value_info('c', TensorProto.FLOAT, [None, None])

    node_add = helper.make_node('Add', inputs=['a', 'b'], outputs=['c'])

    graph = helper.make_graph(
        nodes=[node_add],
        name='add_model',
        inputs=[X, Y],
        outputs=[Z],
    )
    model = helper.make_model(
        graph,
        opset_imports=[helper.make_opsetid('', 13)],
        producer_name='onnx-dev-demo',
    )
    model.ir_version = 9
    return model

def run_inference_demo():
    print("=" * 60)
    print("ONNX Runtime 推理示例")
    print("=" * 60)

    # ---------- 示例1：简单 Add 模型 ----------
    print("\n[1/3] 创建并运行 Add 模型...")
    add_model = create_add_model()
    onnx.checker.check_model(add_model)
    print("  ✅ 模型检查通过")

    # 保存并从字节加载（演示序列化/反序列化）
    model_bytes = add_model.SerializeToString()
    sess = ort.InferenceSession(model_bytes, providers=['CPUExecutionProvider'])

    a = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    b = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float32)
    t0 = time.perf_counter()
    outputs = sess.run(None, {'a': a, 'b': b})
    t1 = time.perf_counter()
    expected = a + b
    print(f"  输入 a:\n{a}")
    print(f"  输入 b:\n{b}")
    print(f"  推理结果 c:\n{outputs[0]}")
    print(f"  期望结果 a+b:\n{expected}")
    print(f"  结果匹配: {np.allclose(outputs[0], expected)}")
    print(f"  推理耗时: {(t1-t0)*1000:.3f}ms")

    # ---------- 示例2：简单 MLP 模型 ----------
    print("\n[2/3] 创建并运行 Mini-MLP 模型...")
    mlp_model = create_simple_linear_model()
    onnx.checker.check_model(mlp_model)
    print("  ✅ 模型检查通过")

    # 使用 onnxsim 简化（展示 onnx-simplifier 用法）
    try:
        import onnxsim
        mlp_model_opt, check_ok = onnxsim.simplify(mlp_model)
        print(f"  ✅ onnxsim 简化成功，check_ok={check_ok}")
        use_model = mlp_model_opt
    except Exception as e:
        print(f"  ⚠️  onnxsim 跳过: {e}")
        use_model = mlp_model

    sess2 = ort.InferenceSession(use_model.SerializeToString(), providers=['CPUExecutionProvider'])
    input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
    t0 = time.perf_counter()
    out2 = sess2.run(None, {'input': input_data})
    t1 = time.perf_counter()
    print(f"  输入形状: {input_data.shape}")
    print(f"  输出形状: {out2[0].shape}")
    print(f"  输出前5值: {out2[0].flatten()[:5]}")
    print(f"  推理耗时: {(t1-t0)*1000:.3f}ms")

    # ---------- 示例3：onnxscript 演示 ----------
    print("\n[3/3] onnxscript 函数式模型构建演示...")
    try:
        import onnxscript
        from onnxscript import ir
        print(f"  ✅ onnxscript {onnxscript.__version__} 可用")
        print(f"  ✅ onnxscript.ir 模块可用（可用于函数式模型构建）")
    except Exception as e:
        print(f"  ⚠️  onnxscript 导入问题: {e}")

    # ---------- providers 信息 ----------
    print("\n" + "-" * 60)
    print("可用的 Execution Providers:")
    for ep in ort.get_available_providers():
        print(f"  - {ep}")

    print("\n" + "=" * 60)
    print("✅ 所有推理示例运行成功！")
    print("=" * 60)

if __name__ == '__main__':
    run_inference_demo()