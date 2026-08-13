from __future__ import annotations

import numpy as np

from onnx_adaround.quant import AdaRoundQuantizer, UniformAffineQuantizer


def test_uniform_affine_symmetric_max():
    q = UniformAffineQuantizer(n_bits=4, symmetric=True, channel_wise=False, scale_method="max")
    x = np.random.default_rng(0).standard_normal((4, 8)).astype(np.float32)
    out = q(x)
    assert out.shape == x.shape
    # symmetric -> zero_point is 0
    assert q.zero_point == 0
    assert q.delta is not None and q.delta > 0
    assert np.all(np.isfinite(out))


def test_uniform_affine_channel_wise_shape():
    w = np.random.default_rng(1).standard_normal((8, 4, 3, 3)).astype(np.float32)
    q = UniformAffineQuantizer(n_bits=4, symmetric=True, channel_wise=True, scale_method="max")
    delta, zp = q.init_quantization_scale(w, channel_wise=True)
    assert delta.shape == (8, 1, 1, 1)
    assert zp.shape == (8, 1, 1, 1)
    out = q(w)
    assert out.shape == w.shape


def test_uniform_affine_mse():
    q = UniformAffineQuantizer(n_bits=8, symmetric=False, channel_wise=False, scale_method="mse")
    x = np.random.default_rng(2).uniform(-1, 1, (2, 16)).astype(np.float32)
    out = q(x)
    assert np.all(np.isfinite(out))
    assert q.delta is not None and q.zero_point is not None


def test_uniform_affine_bitwidth_refactor():
    q = UniformAffineQuantizer(n_bits=4, symmetric=True, channel_wise=False, scale_method="max")
    q.bitwidth_refactor(8)
    assert q.n_bits == 8
    assert q.q_max == 127


def test_adaround_init_alpha():
    rng = np.random.default_rng(3)
    w = rng.uniform(-0.5, 0.5, (4, 8)).astype(np.float32)
    uaq = UniformAffineQuantizer(n_bits=4, symmetric=True, channel_wise=True, scale_method="max")
    uaq.init_quantization_scale(w, channel_wise=True)
    ar = AdaRoundQuantizer(n_bits=4, delta=uaq.delta, zero_point=uaq.zero_point, weight_tensor=w)
    assert ar.alpha is not None
    assert ar.alpha.shape == w.shape
    assert np.all(np.isfinite(ar.alpha))


def test_adaround_forward_soft_targets():
    rng = np.random.default_rng(4)
    w = rng.uniform(-0.5, 0.5, (4, 8)).astype(np.float32)
    uaq = UniformAffineQuantizer(n_bits=4, symmetric=True, channel_wise=True, scale_method="max")
    uaq.init_quantization_scale(w, channel_wise=True)
    ar = AdaRoundQuantizer(n_bits=4, delta=uaq.delta, zero_point=uaq.zero_point, weight_tensor=w)
    ar.soft_targets = True
    out = ar(w)
    assert out.shape == w.shape
    assert np.all(np.isfinite(out))


def test_adaround_forward_hard():
    rng = np.random.default_rng(5)
    w = rng.uniform(-0.5, 0.5, (4, 8)).astype(np.float32)
    uaq = UniformAffineQuantizer(n_bits=4, symmetric=True, channel_wise=True, scale_method="max")
    uaq.init_quantization_scale(w, channel_wise=True)
    ar = AdaRoundQuantizer(n_bits=4, delta=uaq.delta, zero_point=uaq.zero_point, weight_tensor=w)
    ar.soft_targets = False
    out = ar(w)
    assert out.shape == w.shape
    assert np.all(np.isfinite(out))
