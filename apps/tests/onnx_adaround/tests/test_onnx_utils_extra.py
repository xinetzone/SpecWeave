"""Extra coverage for onnx_utils: QuantModel branches, attrs parsing, BN folding edge cases."""
from __future__ import annotations

import numpy as np
from onnx import TensorProto, helper

from onnx_adaround.onnx_utils import (
    QuantModel,
    build_weight_mapping,
    fold_bn_into_onnx,
)


def _t(name, arr):
    return helper.make_tensor(name, TensorProto.FLOAT, arr.shape, arr.flatten())


def _model(nodes, inputs, outputs, inits, name="g"):
    graph = helper.make_graph(nodes, name, inputs, outputs, inits)
    return helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])


def _input(name, shape):
    return helper.make_tensor_value_info(name, TensorProto.FLOAT, shape)


# ---------------------------------------------------------------- QuantModel


def test_quant_model_wide_conv_nbits4():
    w = np.random.default_rng(0).normal(size=(32, 3, 3, 3)).astype(np.float32)
    conv = helper.make_node("Conv", ["input", "w"], ["out"], kernel_shape=[3, 3])
    model = _model(
        [conv],
        [_input("input", [1, 3, 8, 8])],
        [_input("out", [1, 32, 8, 8])],
        [_t("w", w)],
    )
    qnn = QuantModel(model)
    layer = qnn.layers[0]
    assert layer.n_bits == 4  # wide conv -> 4-bit weight
    # no strides/pads/dilations attrs -> defaults filled in
    assert layer.attrs["strides"] == [1, 1]
    assert layer.attrs["pads"] == [0, 0, 0, 0]
    assert layer.attrs["dilations"] == [1, 1]
    assert layer.attrs["group"] == 1


def test_quant_model_matmul_8bit():
    w = np.random.default_rng(1).normal(size=(8, 4)).astype(np.float32)
    mm = helper.make_node("MatMul", ["input", "mm_w"], ["out"])
    model = _model(
        [mm],
        [_input("input", [1, 8])],
        [_input("out", [1, 4])],
        [_t("mm_w", w)],
    )
    qnn = QuantModel(model)
    layer = qnn.layers[0]
    assert layer.op_type == "MatMul"
    assert layer.weight_name == "mm_w"
    assert layer.bias_name is None
    assert layer.n_bits == 8


def test_quant_model_gemm_with_bias():
    w = np.random.default_rng(2).normal(size=(8, 4)).astype(np.float32)
    b = np.random.default_rng(3).normal(size=(4,)).astype(np.float32)
    gemm = helper.make_node("Gemm", ["input", "gemm_w", "gemm_b"], ["out"], transB=1)
    model = _model(
        [gemm],
        [_input("input", [1, 8])],
        [_input("out", [1, 4])],
        [_t("gemm_w", w), _t("gemm_b", b)],
    )
    qnn = QuantModel(model)
    layer = qnn.layers[0]
    assert layer.bias_name == "gemm_b"
    assert layer.bias is not None


def test_quant_model_matmul_both_inits():
    a = _t("a", np.ones((2, 4), dtype=np.float32))
    b = _t("b", np.ones((4, 3), dtype=np.float32))
    mm = helper.make_node("MatMul", ["a", "b"], ["out"])
    model = _model([mm], [], [_input("out", [2, 3])], [a, b])
    qnn = QuantModel(model)
    assert len(qnn.layers) == 1


def test_extract_layers_skips_non_init_weight():
    conv = helper.make_node("Conv", ["input", "intermediate_w"], ["out"], kernel_shape=[3, 3])
    model = _model([conv], [_input("input", [1, 3, 8, 8])], [_input("out", [1, 4, 8, 8])], [])
    qnn = QuantModel(model)
    assert len(qnn.layers) == 0


def test_quant_model_non_quantizable_only():
    relu = helper.make_node("Relu", ["input"], ["out"])
    model = _model([relu], [_input("input", [1, 4])], [_input("out", [1, 4])], [])
    qnn = QuantModel(model)
    assert len(qnn.layers) == 0


def test_attrs_of_all_types():
    w = np.random.default_rng(4).normal(size=(4, 3, 3, 3)).astype(np.float32)
    node = helper.make_node(
        "Conv", ["input", "w"], ["out"], kernel_shape=[3, 3], group=1
    )
    node.attribute.append(helper.make_attribute("scale_f", 0.5))
    node.attribute.append(helper.make_attribute("auto_pad", "SAME_UPPER"))
    node.attribute.append(helper.make_attribute("floats", [1.0, 2.0]))
    tensor_attr = helper.make_tensor(
        "tensor_a", TensorProto.FLOAT, [2, 2], np.arange(4, dtype=np.float32).flatten()
    )
    node.attribute.append(helper.make_attribute("tensor_a", tensor_attr))
    model = _model(
        [node],
        [_input("input", [1, 3, 8, 8])],
        [_input("out", [1, 4, 8, 8])],
        [_t("w", w)],
    )
    qnn = QuantModel(model)
    attrs = qnn.layers[0].attrs
    assert attrs["group"] == 1
    assert attrs["scale_f"] == 0.5
    assert attrs["auto_pad"] == "SAME_UPPER"
    assert attrs["floats"] == [1.0, 2.0]
    assert attrs["tensor_a"].shape == (2, 2)


def test_conv_single_element_strides():
    w = np.random.default_rng(5).normal(size=(4, 3, 3, 3)).astype(np.float32)
    conv = helper.make_node("Conv", ["input", "w"], ["out"], strides=[2], kernel_shape=[3, 3])
    model = _model(
        [conv],
        [_input("input", [1, 3, 8, 8])],
        [_input("out", [1, 4, 8, 8])],
        [_t("w", w)],
    )
    qnn = QuantModel(model)
    assert qnn.layers[0].attrs["strides"] == [2, 2]


# ------------------------------------------------- QuantModel helper methods


def test_set_first_last_8bit_empty():
    conv = helper.make_node("Conv", ["input", "intermediate_w"], ["out"], kernel_shape=[3, 3])
    model = _model([conv], [_input("input", [1, 3, 8, 8])], [_input("out", [1, 4, 8, 8])], [])
    qnn = QuantModel(model)
    assert len(qnn.layers) == 0
    qnn.set_first_last_layer_to_8bit()  # no-op on empty


def test_set_first_last_8bit_nonempty(make_conv_model):
    qnn = QuantModel(make_conv_model)
    qnn.set_first_last_layer_to_8bit()
    layer = qnn.layers[0]
    assert layer.n_bits == 8
    assert layer.ignore_reconstruction is True


def test_disable_network_output_quantization(make_conv_model):
    qnn = QuantModel(make_conv_model)
    qnn.disable_network_output_quantization()
    assert qnn.layers[-1].use_act_quant is False


def test_forward_weight_quant(make_conv_model):
    qnn = QuantModel(make_conv_model)
    layer = qnn.layers[0]
    out = qnn.forward_weight_quant(layer, layer.weight)
    assert out.shape == layer.weight.shape
    assert np.all(np.isfinite(out))


# ----------------------------------------------------------- BN folding edges


def _bn_branch():
    rng = np.random.default_rng(9)
    scale = rng.uniform(0.5, 1.5, (4,)).astype(np.float32)
    beta = rng.standard_normal((4,)).astype(np.float32)
    mean = rng.standard_normal((4,)).astype(np.float32)
    var = rng.uniform(0.5, 1.5, (4,)).astype(np.float32)
    return scale, beta, mean, var


def test_bn_fold_short_input_not_folded():
    w = np.random.default_rng(0).normal(size=(4, 3, 3, 3)).astype(np.float32)
    conv = helper.make_node("Conv", ["input", "w"], ["conv_out"], kernel_shape=[3, 3])
    bn = helper.make_node("BatchNormalization", ["conv_out", "scale"], ["out"])
    model = _model(
        [conv, bn],
        [_input("input", [1, 3, 8, 8])],
        [_input("out", [1, 4, 8, 8])],
        [_t("w", w), _t("scale", np.ones(4, dtype=np.float32))],
    )
    fold_bn_into_onnx(model)
    assert sum(1 for n in model.graph.node if n.op_type == "BatchNormalization") == 1


def test_bn_fold_prev_not_quantizable():
    scale, beta, mean, var = _bn_branch()
    relu = helper.make_node("Relu", ["input"], ["r_out"])
    bn = helper.make_node(
        "BatchNormalization",
        ["r_out", "s", "b", "m", "v"],
        ["out"],
        epsilon=1e-5,
    )
    model = _model(
        [relu, bn],
        [_input("input", [1, 4])],
        [_input("out", [1, 4])],
        [_t("s", scale), _t("b", beta), _t("m", mean), _t("v", var)],
    )
    fold_bn_into_onnx(model)
    assert sum(1 for n in model.graph.node if n.op_type == "BatchNormalization") == 1


def test_bn_fold_missing_param_init():
    w = np.random.default_rng(1).normal(size=(4, 3, 3, 3)).astype(np.float32)
    scale, beta, mean, var = _bn_branch()
    conv = helper.make_node("Conv", ["input", "w"], ["conv_out"], kernel_shape=[3, 3])
    # "missing_scale" is referenced but not an initializer
    bn = helper.make_node(
        "BatchNormalization",
        ["conv_out", "missing_scale", "b", "m", "v"],
        ["out"],
        epsilon=1e-5,
    )
    model = _model(
        [conv, bn],
        [_input("input", [1, 3, 8, 8])],
        [_input("out", [1, 4, 8, 8])],
        [_t("w", w), _t("b", beta), _t("m", mean), _t("v", var)],
    )
    fold_bn_into_onnx(model)
    assert sum(1 for n in model.graph.node if n.op_type == "BatchNormalization") == 1


def test_bn_fold_matmul_creates_bias():
    mm_w = np.random.default_rng(2).normal(size=(4, 8)).astype(np.float32)
    scale, beta, mean, var = _bn_branch()
    mm = helper.make_node("MatMul", ["input", "mm_w"], ["mm_out"])
    bn = helper.make_node(
        "BatchNormalization",
        ["mm_out", "s", "b", "m", "v"],
        ["output"],
    )  # no epsilon -> default 1e-5
    model = _model(
        [mm, bn],
        [_input("input", [1, 4])],
        [_input("output", [1, 8])],
        [_t("mm_w", mm_w), _t("s", scale), _t("b", beta), _t("m", mean), _t("v", var)],
    )
    fold_bn_into_onnx(model)
    # MatMul node gains a folded-bias input
    mm_node = [n for n in model.graph.node if n.op_type == "MatMul"][0]
    assert any("folded_bias" in i for i in mm_node.input)
    # BN removed
    assert sum(1 for n in model.graph.node if n.op_type == "BatchNormalization") == 0


def test_bn_fold_conv_with_downstream_node():
    w = np.random.default_rng(3).normal(size=(4, 3, 3, 3)).astype(np.float32)
    scale, beta, mean, var = _bn_branch()
    conv = helper.make_node("Conv", ["input", "w"], ["conv_out"], kernel_shape=[3, 3])
    bn = helper.make_node(
        "BatchNormalization",
        ["conv_out", "s", "b", "m", "v"],
        ["bn_out"],
        epsilon=1e-5,
    )
    relu = helper.make_node("Relu", ["bn_out"], ["out"])
    model = _model(
        [conv, bn, relu],
        [_input("input", [1, 3, 8, 8])],
        [_input("out", [1, 4, 8, 8])],
        [_t("w", w), _t("s", scale), _t("b", beta), _t("m", mean), _t("v", var)],
    )
    fold_bn_into_onnx(model)
    # downstream Relu now consumes conv_out
    relu_node = [n for n in model.graph.node if n.op_type == "Relu"][0]
    assert relu_node.input[0] == "conv_out"
    assert sum(1 for n in model.graph.node if n.op_type == "BatchNormalization") == 0


# ----------------------------------------------------------- misc utilities


def test_build_weight_mapping(make_conv_model):
    mapping = build_weight_mapping(make_conv_model)
    assert mapping == {"conv_out": "conv_w"}
