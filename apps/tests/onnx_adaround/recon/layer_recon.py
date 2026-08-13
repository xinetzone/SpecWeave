"""Layer-wise AdaRound reconstruction (numpy/autodiff, torch-free).

Mirrors ``xmnn.adaround.quant.layer_recon``. Optimizes a per-layer learnable
``alpha`` (rounding policy) by reconstructing the layer's output against the
FP32 reference captured via onnxruntime.
"""

from __future__ import annotations

import numpy as np

from ..autodiff import Adam, LinearTempDecay, Tensor, mse_loss, ops, relaxation_round_loss
from ..onnx_utils import QuantLayer


def _layer_forward_tensors(layer: QuantLayer, inp, alpha, delta, zero_point, n_levels):
    """Build the quantized forward of a layer using autodiff Tensors.

    Returns output Tensor. Weight is quantized via AdaRound using ``alpha``.
    """
    # ---- AdaRound weight quantization ----
    w = Tensor(layer.weight.copy())
    dw = w / delta
    w_floor_t = ops.floor(dw)
    if getattr(layer, "soft_targets", False):
        gamma, zeta = -0.1, 1.1
        h = ops.clip(ops.sigmoid(alpha) * (zeta - gamma) + gamma, 0.0, 1.0)
    else:
        h = (alpha.data >= 0).astype(np.float64)
    w_int = w_floor_t + h
    w_int = ops.clip(w_int + zero_point, -n_levels, n_levels - 1)
    w_q = (w_int - zero_point) * delta

    if layer.op_type in ("Conv", "ConvTranspose"):
        stride = _pair(layer.attrs.get("strides", [1, 1]))
        pads = layer.attrs.get("pads", [0, 0, 0, 0])
        padding = (pads[0], pads[2])  # top,left for our 2-tuple padding
        groups = int(layer.attrs.get("group", 1))
        bias = Tensor(layer.bias) if layer.bias is not None else Tensor(np.zeros(0))
        out = ops.conv2d(inp, w_q, bias, stride=stride, padding=padding, groups=groups)
    else:  # MatMul / Gemm (assume weight is (out,in); treat as matmul)
        bias = Tensor(layer.bias) if layer.bias is not None else None
        out = ops.matmul(inp, w_q)
        if bias is not None:
            out = out + bias
    return out


def _pair(v):
    if isinstance(v, (tuple, list)):
        return int(v[0]), int(v[1])
    return int(v), int(v)


def layer_reconstruction(model, layer: QuantLayer, inp_cache, out_cache,
                         batch_size: int = 32, iters: int = 2000, weight: float = 0.01,
                         opt_mode: str = "mse", b_range=(20, 2), warmup: float = 0.2,
                         p: float = 2.0, lr: float = 4e-5, asym: bool = False,
                         soft_targets: bool = True, seed: int = 1029):
    """Reconstruct a single layer's rounding policy.

    ``inp_cache`` / ``out_cache`` are the FP32 reference input/output arrays for
    this layer (from ``cache_layer_inp_out``). Mutates ``layer.alpha``.
    """
    rng = np.random.default_rng(seed)
    if inp_cache is None or out_cache is None:
        raise RuntimeError(f"No cached activations for layer {layer.name}")

    layer.weight_quantizer.inited = False
    layer.weight_quantizer.init_quantization_scale(layer.weight, layer.weight_quantizer.channel_wise)
    delta = layer.weight_quantizer.delta
    zero_point = layer.weight_quantizer.zero_point
    n_levels = layer.weight_quantizer.n_levels
    layer.soft_targets = soft_targets

    # Initialize alpha the same way as AdaRoundQuantizer.
    w = layer.weight
    w_floor = np.floor(w / delta)
    rest = (w / delta) - w_floor
    gamma, zeta = -0.1, 1.1
    alpha = -np.log((zeta - gamma) / (rest - gamma) - 1)
    alpha = alpha.astype(np.float64)

    params = {"alpha": {"data": alpha, "grad": np.zeros_like(alpha)}}
    optimizer = Adam(params, lr=lr)
    temp_decay = LinearTempDecay(iters, rel_start_decay=warmup, start_b=b_range[0], end_b=b_range[1])

    loss_start = iters * warmup
    num_samples = inp_cache.shape[0]

    for t in range(1, iters + 1):
        idx = rng.permutation(num_samples)[:batch_size]
        cur_inp = inp_cache[idx]
        cur_out = out_cache[idx]

        alpha_t = Tensor(params["alpha"]["data"], requires_grad=True)
        inp_t = Tensor(cur_inp)
        out_q = _layer_forward_tensors(layer, inp_t, alpha_t, delta, zero_point, n_levels)

        rec = mse_loss(out_q, Tensor(cur_out), p=p)
        b = temp_decay(t)
        if t < loss_start:
            round_loss = Tensor(np.array(0.0))
        else:
            round_loss = relaxation_round_loss(alpha_t, weight, b)
        total = rec + round_loss

        optimizer.zero_grad()
        total.backward()
        params["alpha"]["grad"] = alpha_t.grad
        optimizer.step()

        if t % 500 == 0:
            print(f"Total loss:\t{float(total.data):.3f}\tb={b:.2f}\tcount={t}")

    layer.alpha = params["alpha"]["data"]
    layer.delta = delta
    layer.zero_point = zero_point
    layer.soft_targets = soft_targets
    return layer


def block_reconstruction(model, block_layers, inp_cache, out_cache, **kwargs):
    """Reconstruct a block by iterating its member layers.

    ``block_layers`` is a list of QuantLayer that form a block; activations
    are reconstructed per-layer (inp/out captured at block-level boundaries are
    used as a coarse reference). For torch parity we reconstruct each layer in
    order using its own cached activations when available.
    """
    for i, layer in enumerate(block_layers):
        layer_reconstruction(model, layer, inp_cache[i], out_cache[i], **kwargs)
    return block_layers
