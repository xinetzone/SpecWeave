"""Shared test fixtures: build small ONNX models and reference numpy ops."""

from __future__ import annotations

import numpy as np
import pytest
from onnx import TensorProto, helper


@pytest.fixture
def make_conv_model(seed=0):
    """A tiny Conv -> (no BN) model: input(1,3,8,8) -> Conv(3->4, k3) -> output."""
    rng = np.random.default_rng(seed)
    w = rng.standard_normal((4, 3, 3, 3)).astype(np.float32)
    b = rng.standard_normal((4,)).astype(np.float32)
    w_init = helper.make_tensor("conv_w", TensorProto.FLOAT, w.shape, w.flatten())
    b_init = helper.make_tensor("conv_b", TensorProto.FLOAT, b.shape, b.flatten())

    conv = helper.make_node(
        "Conv", ["input", "conv_w", "conv_b"], ["conv_out"],
        kernel_shape=[3, 3], strides=[1, 1], pads=[1, 1, 1, 1],
    )
    graph = helper.make_graph(
        [conv],
        "conv_graph",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, 8, 8])],
        [helper.make_tensor_value_info("conv_out", TensorProto.FLOAT, [1, 4, 8, 8])],
        [w_init, b_init],
    )
    return helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])


@pytest.fixture
def make_conv_bn_model(seed=0):
    """Conv -> BatchNormalization model to test graph-level BN folding."""
    rng = np.random.default_rng(seed)
    w = rng.standard_normal((4, 3, 3, 3)).astype(np.float32)
    b = rng.standard_normal((4,)).astype(np.float32)
    scale = rng.uniform(0.5, 1.5, (4,)).astype(np.float32)
    beta = rng.standard_normal((4,)).astype(np.float32)
    mean = rng.standard_normal((4,)).astype(np.float32)
    var = rng.uniform(0.5, 1.5, (4,)).astype(np.float32)

    inits = [
        helper.make_tensor("conv_w", TensorProto.FLOAT, w.shape, w.flatten()),
        helper.make_tensor("conv_b", TensorProto.FLOAT, b.shape, b.flatten()),
        helper.make_tensor("bn_scale", TensorProto.FLOAT, scale.shape, scale.flatten()),
        helper.make_tensor("bn_b", TensorProto.FLOAT, beta.shape, beta.flatten()),
        helper.make_tensor("bn_mean", TensorProto.FLOAT, mean.shape, mean.flatten()),
        helper.make_tensor("bn_var", TensorProto.FLOAT, var.shape, var.flatten()),
    ]
    conv = helper.make_node(
        "Conv", ["input", "conv_w", "conv_b"], ["conv_out"],
        kernel_shape=[3, 3], strides=[1, 1], pads=[1, 1, 1, 1],
    )
    bn = helper.make_node(
        "BatchNormalization",
        ["conv_out", "bn_scale", "bn_b", "bn_mean", "bn_var"],
        ["output"], epsilon=1e-5,
    )
    graph = helper.make_graph(
        [conv, bn],
        "conv_bn_graph",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, 8, 8])],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 4, 8, 8])],
        inits,
    )
    return helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])


@pytest.fixture(scope="module")
def make_conv_relu_conv_model(seed=0):
    """Conv -> ReLU -> Conv model for end-to-end AdaRound precision checks.

    Input(1,3,16,16) -> Conv(3->48, k3) -> ReLU -> Conv(48->48, k3) -> output.
    Two quantizable layers so that the second (48 > 16 channels) is AdaRound-
    baked at 4-bit, while the first is forced to 8-bit head quantization.
    (Module-scoped: the returned model is immutable and shared across checks.)
    """
    rng = np.random.default_rng(seed)
    w1 = rng.standard_normal((48, 3, 3, 3)).astype(np.float32)
    b1 = rng.standard_normal((48,)).astype(np.float32)
    w2 = rng.standard_normal((48, 48, 3, 3)).astype(np.float32)
    b2 = rng.standard_normal((48,)).astype(np.float32)
    inits = [
        helper.make_tensor("conv1_w", TensorProto.FLOAT, w1.shape, w1.flatten()),
        helper.make_tensor("conv1_b", TensorProto.FLOAT, b1.shape, b1.flatten()),
        helper.make_tensor("conv2_w", TensorProto.FLOAT, w2.shape, w2.flatten()),
        helper.make_tensor("conv2_b", TensorProto.FLOAT, b2.shape, b2.flatten()),
    ]
    conv1 = helper.make_node(
        "Conv", ["input", "conv1_w", "conv1_b"], ["c1"],
        kernel_shape=[3, 3], strides=[1, 1], pads=[1, 1, 1, 1],
    )
    relu = helper.make_node("Relu", ["c1"], ["r1"])
    conv2 = helper.make_node(
        "Conv", ["r1", "conv2_w", "conv2_b"], ["output"],
        kernel_shape=[3, 3], strides=[1, 1], pads=[1, 1, 1, 1],
    )
    graph = helper.make_graph(
        [conv1, relu, conv2],
        "conv_relu_conv_graph",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, 16, 16])],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 48, 16, 16])],
        inits,
    )
    return helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])


def ref_conv2d(x, w, b=None, stride=1, padding=0):
    """Pure numpy reference conv2d (NCHW) via scipy-free im2col-free manual loop."""
    n, c_in, h, w_in = x.shape
    c_out, _, kh, kw = w.shape
    ph, pw = (padding, padding) if isinstance(padding, int) else padding
    sh, sw = (stride, stride) if isinstance(stride, int) else stride
    xp = np.pad(x, ((0, 0), (0, 0), (ph, ph), (pw, pw)))
    oh = (h + 2 * ph - kh) // sh + 1
    ow = (w_in + 2 * pw - kw) // sw + 1
    out = np.zeros((n, c_out, oh, ow))
    for i in range(oh):
        for j in range(ow):
            patch = xp[:, :, i * sh:i * sh + kh, j * sw:j * sw + kw]
            out[:, :, i, j] = np.tensordot(patch, w, axes=([1, 2, 3], [1, 2, 3]))
    if b is not None:
        out += b.reshape(1, -1, 1, 1)
    return out
