from __future__ import annotations

import numpy as np
import onnxruntime as ort

from onnx_adaround.onnx_utils import QuantModel
from onnx_adaround.recon import cache_layer_inp_out, layer_reconstruction


def _run_ort(model, x):
    sess = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"])
    out = sess.run(None, {model.graph.input[0].name: x.astype(np.float32)})
    return out[0]


def test_cache_layer_inp_out(make_conv_model):
    model = make_conv_model
    x = np.random.default_rng(0).standard_normal((4, 3, 8, 8)).astype(np.float32)
    inp_batches, out_batches = cache_layer_inp_out(model, QuantModel(model).layers, x, batch_size=2)
    assert len(inp_batches) == 1
    assert len(out_batches) == 1
    assert inp_batches[0].shape == (4, 3, 8, 8)
    assert out_batches[0].shape == (4, 4, 8, 8)


def test_layer_reconstruction_converges(make_conv_model):
    model = make_conv_model
    qnn = QuantModel(model)
    layer = qnn.layers[0]
    x = np.random.default_rng(1).standard_normal((8, 3, 8, 8)).astype(np.float32)
    inp_batches, out_batches = cache_layer_inp_out(model, qnn.layers, x, batch_size=8)

    layer_reconstruction(qnn, layer, inp_batches[0], out_batches[0], iters=60,
                         batch_size=8, weight=0.01, b_range=(20, 2), warmup=0.2)

    assert layer.alpha is not None
    assert layer.delta is not None


def test_reconstruction_reduces_mse(make_conv_model):
    model = make_conv_model
    qnn = QuantModel(model)
    layer = qnn.layers[0]
    x = np.random.default_rng(2).standard_normal((8, 3, 8, 8)).astype(np.float32)
    inp_batches, out_batches = cache_layer_inp_out(model, qnn.layers, x, batch_size=8)

    from onnx_adaround.autodiff import Tensor, mse_loss, ops

    def quantized_mse(use_alpha):
        if use_alpha and layer.alpha is not None:
            delta = layer.delta
            zp = layer.zero_point
            n_levels = 2 ** (layer.n_bits - 1)
            wq = np.clip(np.floor(layer.weight / delta) + (layer.alpha >= 0).astype(np.float64)
                         + zp, -n_levels, n_levels - 1)
            wq = (wq - zp) * delta
        else:
            wq = layer.weight_quantizer(layer.weight).astype(np.float64)
        out = ops.conv2d(Tensor(inp_batches[0]), Tensor(wq),
                         Tensor(layer.bias.astype(np.float64)), stride=1, padding=1, groups=1)
        return float(mse_loss(out, Tensor(out_batches[0])).data)

    before = quantized_mse(False)
    layer_reconstruction(qnn, layer, inp_batches[0], out_batches[0], iters=100,
                         batch_size=8, weight=0.01, b_range=(20, 2), warmup=0.2)
    after = quantized_mse(True)
    # AdaRound should not worsen the naive-quant MSE (or improve it).
    assert after <= before + 1e-6
