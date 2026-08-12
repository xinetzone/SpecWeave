"""Extra coverage for AdaRoundQuantizer round modes and edge branches."""
from __future__ import annotations

import numpy as np
import pytest

from onnx_adaround.quant import AdaRoundQuantizer, UniformAffineQuantizer


def _fixture(seed=0):
    rng = np.random.default_rng(seed)
    w = rng.uniform(-0.5, 0.5, (4, 8)).astype(np.float32)
    uaq = UniformAffineQuantizer(n_bits=4, symmetric=True, channel_wise=True, scale_method="max")
    uaq.init_quantization_scale(w, channel_wise=True)
    return uaq, w


def _make(mode, seed=0):
    """Construct with a valid mode then switch round_mode to exercise other paths."""
    uaq, w = _fixture(seed)
    ar = AdaRoundQuantizer(4, uaq.delta, uaq.zero_point, w, round_mode="learned_hard_sigmoid")
    ar.round_mode = mode
    return ar, w


def test_forward_nearest():
    ar, w = _make("nearest")
    out = ar(w)
    assert out.shape == w.shape
    assert np.all(np.isfinite(out))


def test_forward_nearest_ste():
    ar, w = _make("nearest_ste")
    out = ar(w)
    assert out.shape == w.shape
    assert np.all(np.isfinite(out))


def test_forward_stochastic():
    ar, w = _make("stochastic")
    out = ar(w)
    assert out.shape == w.shape
    assert np.all(np.isfinite(out))


def test_invalid_round_mode_raises():
    ar, w = _make("bogus")
    with pytest.raises(ValueError):
        ar(w)


def test_init_alpha_not_implemented_for_non_learned_mode():
    uaq, w = _fixture()
    with pytest.raises(NotImplementedError):
        AdaRoundQuantizer(4, uaq.delta, uaq.zero_point, w, round_mode="nearest")
