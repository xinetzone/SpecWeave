"""
pytest 共享 fixtures：使用 onnx helper 直接创建轻量测试模型（不依赖 torch）
"""
import os
import sys
import tempfile
import numpy as np
import pytest
import onnx
from onnx import helper, TensorProto

# 将scripts目录加入path
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)


def _make_mlp_model(input_dim: int = 10, hidden_dim: int = 20, output_dim: int = 5,
                    dynamic_batch: bool = True) -> onnx.ModelProto:
    """创建一个简单的MLP模型: MatMul -> Add -> Relu"""
    batch_dim = "N" if dynamic_batch else 1
    X = helper.make_tensor_value_info('input', TensorProto.FLOAT, [batch_dim, input_dim])
    W = helper.make_tensor('W', TensorProto.FLOAT, [input_dim, hidden_dim],
                           np.random.randn(input_dim, hidden_dim).flatten().tolist())
    B = helper.make_tensor('B', TensorProto.FLOAT, [hidden_dim],
                           np.random.randn(hidden_dim).flatten().tolist())
    W2 = helper.make_tensor('W2', TensorProto.FLOAT, [hidden_dim, output_dim],
                            np.random.randn(hidden_dim, output_dim).flatten().tolist())
    B2 = helper.make_tensor('B2', TensorProto.FLOAT, [output_dim],
                            np.random.randn(output_dim).flatten().tolist())
    Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [batch_dim, output_dim])

    nodes = [
        helper.make_node('MatMul', ['input', 'W'], ['mm_out']),
        helper.make_node('Add', ['mm_out', 'B'], ['add_out']),
        helper.make_node('Relu', ['add_out'], ['relu_out']),
        helper.make_node('MatMul', ['relu_out', 'W2'], ['mm2_out']),
        helper.make_node('Add', ['mm2_out', 'B2'], ['output']),
    ]
    graph = helper.make_graph(nodes, 'mlp_test', [X], [Y], [W, B, W2, B2])
    return helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])


def _make_cnn_model() -> onnx.ModelProto:
    """创建一个简单的CNN模型: Conv -> Relu -> GlobalAvgPool -> MatMul"""
    X = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 3, 8, 8])
    # Conv weight: [out_channels, in_channels, kH, kW]
    W_conv = helper.make_tensor('W_conv', TensorProto.FLOAT, [8, 3, 3, 3],
                                np.random.randn(8, 3, 3, 3).flatten().tolist())
    B_conv = helper.make_tensor('B_conv', TensorProto.FLOAT, [8],
                                np.random.randn(8).flatten().tolist())
    W_fc = helper.make_tensor('W_fc', TensorProto.FLOAT, [8, 10],
                              np.random.randn(8, 10).flatten().tolist())
    B_fc = helper.make_tensor('B_fc', TensorProto.FLOAT, [10],
                              np.random.randn(10).flatten().tolist())
    Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 10])

    nodes = [
        helper.make_node('Conv', ['input', 'W_conv', 'B_conv'], ['conv_out'], pads=[1, 1, 1, 1]),
        helper.make_node('Relu', ['conv_out'], ['relu_out']),
        helper.make_node('GlobalAveragePool', ['relu_out'], ['pool_out']),
        helper.make_node('Flatten', ['pool_out'], ['flat_out'], axis=1),
        helper.make_node('MatMul', ['flat_out', 'W_fc'], ['mm_out']),
        helper.make_node('Add', ['mm_out', 'B_fc'], ['output']),
    ]
    graph = helper.make_graph(nodes, 'cnn_test', [X], [Y], [W_conv, B_conv, W_fc, B_fc])
    return helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])


def _make_identity_model(input_shape: tuple = (1, 10)) -> onnx.ModelProto:
    """创建一个Identity模型（输出=输入，用于精度自校验）"""
    X = helper.make_tensor_value_info('input', TensorProto.FLOAT, list(input_shape))
    Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, list(input_shape))
    nodes = [helper.make_node('Identity', ['input'], ['output'])]
    graph = helper.make_graph(nodes, 'identity_test', [X], [Y])
    return helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])


@pytest.fixture(scope="module")
def tmp_model_dir():
    """模块级临时目录，用于存放测试模型文件"""
    d = tempfile.mkdtemp(prefix="onnx_quantize_test_")
    yield d
    import shutil
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(scope="module")
def mlp_model_path(tmp_model_dir):
    """MLP模型路径（动态batch维度）"""
    path = os.path.join(tmp_model_dir, "mlp.onnx")
    onnx.save(_make_mlp_model(dynamic_batch=True), path)
    return path


@pytest.fixture(scope="module")
def mlp_static_model_path(tmp_model_dir):
    """MLP模型路径（静态batch维度）"""
    path = os.path.join(tmp_model_dir, "mlp_static.onnx")
    onnx.save(_make_mlp_model(dynamic_batch=False), path)
    return path


@pytest.fixture(scope="module")
def cnn_model_path(tmp_model_dir):
    """CNN模型路径"""
    path = os.path.join(tmp_model_dir, "cnn.onnx")
    onnx.save(_make_cnn_model(), path)
    return path


@pytest.fixture(scope="module")
def identity_model_path(tmp_model_dir):
    """Identity模型路径（用于精度自校验）"""
    path = os.path.join(tmp_model_dir, "identity.onnx")
    onnx.save(_make_identity_model(), path)
    return path


@pytest.fixture(scope="module")
def small_mlp_path(tmp_model_dir):
    """极小MLP模型路径（输入维度小，用于快速测试）"""
    path = os.path.join(tmp_model_dir, "small_mlp.onnx")
    onnx.save(_make_mlp_model(input_dim=4, hidden_dim=8, output_dim=2, dynamic_batch=False), path)
    return path
