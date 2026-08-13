"""Extra coverage for quant_layer: StraightThrough, lp_loss, scale branches."""
from __future__ import annotations

import numpy as np
import pytest

from onnx_adaround.quant.quant_layer import StraightThrough, UniformAffineQuantizer, lp_loss


def test_straight_through_forward():
    st = StraightThrough()
    x = np.array([1.0, 2.0])
    assert np.array_equal(st.forward(x), x)


def test_straight_through_call():
    st = StraightThrough()
    x = np.array([1.0, 2.0])
    assert np.array_equal(st(x), x)


def test_lp_loss_reduction_none():
    pred = np.random.default_rng(0).normal(size=(3, 4)).astype(np.float64)
    tgt = np.zeros_like(pred)
    out = lp_loss(pred, tgt, p=2.0, reduction="none")
    assert np.ndim(out) == 0


def test_invalid_n_bits_init():
    with pytest.raises(AssertionError):
        UniformAffineQuantizer(n_bits=1)


def test_max_scale_with_scale_factor():
    q = UniformAffineQuantizer(n_bits=8, symmetric=False, scale_method="max_scale")
    x = np.random.default_rng(1).normal(size=(4, 8)).astype(np.float32)
    out = q(x)
    assert np.all(np.isfinite(out))


def test_constant_input_triggers_range_warning():
    q = UniformAffineQuantizer(n_bits=8, symmetric=True, scale_method="max")
    x = np.zeros((2, 4), dtype=np.float32)
    out = q(x)
    assert np.all(np.isfinite(out))
    assert q.delta is not None and q.delta > 0


def test_mse_symmetric():
    q = UniformAffineQuantizer(n_bits=8, symmetric=True, scale_method="mse")
    x = np.random.default_rng(2).uniform(-1, 1, (2, 16)).astype(np.float32)
    out = q(x)
    assert np.all(np.isfinite(out))
    assert q.zero_point == 0


def test_invalid_scale_method_raises():
    q = UniformAffineQuantizer(n_bits=8, scale_method="bogus")
    x = np.random.default_rng(3).normal(size=(4, 8)).astype(np.float32)
    with pytest.raises(NotImplementedError):
        q.init_quantization_scale(x)


def test_quantize_simulate_symmetric():
    q = UniformAffineQuantizer(n_bits=8, symmetric=True, scale_method="max")
    x = np.random.default_rng(4).normal(size=(4, 8)).astype(np.float32)
    out = q.quantize_simulate(x, 1.0, -1.0)
    assert np.all(np.isfinite(out))


def test_bitwidth_refactor_invalid():
    q = UniformAffineQuantizer(n_bits=8)
    with pytest.raises(AssertionError):
        q.bitwidth_refactor(1)


def test_bitwidth_refactor_non_symmetric():
    q = UniformAffineQuantizer(n_bits=8, symmetric=False)
    q.bitwidth_refactor(4)
    assert q.q_min == 0
    assert q.q_max == 15
