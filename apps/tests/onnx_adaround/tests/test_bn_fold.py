from __future__ import annotations

import numpy as np
from onnx import numpy_helper

from onnx_adaround.onnx_utils import QuantModel, fold_bn_into_onnx


def test_bn_fold_removes_bn_node(make_conv_bn_model):
    model = make_conv_bn_model
    n_bn_before = sum(1 for n in model.graph.node if n.op_type == "BatchNormalization")
    assert n_bn_before == 1
    fold_bn_into_onnx(model)
    n_bn_after = sum(1 for n in model.graph.node if n.op_type == "BatchNormalization")
    assert n_bn_after == 0


def test_bn_fold_weight_value(make_conv_bn_model):
    model = make_conv_bn_model
    inits = {i.name: numpy_helper.to_array(i) for i in model.graph.initializer}
    w = inits["conv_w"]
    scale = inits["bn_scale"]
    var = inits["bn_var"]
    eps = 1e-5

    fold_bn_into_onnx(model)
    folded = {i.name: numpy_helper.to_array(i) for i in model.graph.initializer}

    w_expected = w * (scale / np.sqrt(var + eps)).reshape(-1, 1, 1, 1)
    assert np.allclose(folded["conv_w"], w_expected, atol=1e-6)


def test_bn_fold_bias_value(make_conv_bn_model):
    model = make_conv_bn_model
    inits = {i.name: numpy_helper.to_array(i) for i in model.graph.initializer}
    cbias = inits["conv_b"]
    scale = inits["bn_scale"]
    beta = inits["bn_b"]
    mean = inits["bn_mean"]
    var = inits["bn_var"]
    eps = 1e-5

    fold_bn_into_onnx(model)
    folded = {i.name: numpy_helper.to_array(i) for i in model.graph.initializer}

    safe_std = np.sqrt(var + eps)
    b_expected = scale * cbias / safe_std + (beta - scale * mean / safe_std)
    # The folded bias initializer name: conv_b (existing)
    assert np.allclose(folded["conv_b"], b_expected, atol=1e-6)


def test_bn_fold_quant_model_layers(make_conv_bn_model):
    model = make_conv_bn_model
    fold_bn_into_onnx(model)
    qnn = QuantModel(model)
    assert len(qnn.layers) == 1
    assert qnn.layers[0].op_type == "Conv"
    assert qnn.layers[0].n_bits in (4, 8)
