"""Uniform affine quantizer and straight-through helpers (pure numpy).

Mirrors ``xmnn.adaround.quant.quant_layer`` but replaces torch tensors with
numpy arrays. All quantization math is identical to the torch reference so
that numerical cross-checks pass within the specified tolerance.
"""

from __future__ import annotations

import warnings

import numpy as np


class StraightThrough:
    """Identity pass-through (numpy equivalent of a no-op module)."""

    def forward(self, x: np.ndarray, *args) -> np.ndarray:
        return x

    def __call__(self, x: np.ndarray, *args) -> np.ndarray:
        return self.forward(x, *args)


def round_ste(x: np.ndarray) -> np.ndarray:
    """Straight-through estimator for rounding: forward rounds, gradient passes."""
    return (np.round(x) - x).astype(x.dtype) + x


def lp_loss(pred: np.ndarray, tgt: np.ndarray, p: float = 2.0, reduction: str = "none") -> np.ndarray:
    """Lp loss matching the torch reference.

    - ``none``: sum over dim 1 then mean over batch.
    - ``all``: mean over all elements (scalar-like array).
    """
    diff = np.abs(pred - tgt).astype(np.float64) ** p
    if reduction == "none":
        return diff.sum(1).mean()
    return diff.mean()


class UniformAffineQuantizer:
    """Uniform affine quantizer.

    Mirrors the torch reference: supports max/mse scale methods, channel-wise
    quantization, symmetric flag, and bitwidth refactoring.
    """

    def __init__(
        self,
        n_bits: int = 8,
        symmetric: bool = False,
        channel_wise: bool = False,
        scale_method: str = "max",
        leaf_param: bool = False,
    ):
        self.symmetric = symmetric
        if not 2 <= n_bits <= 8:
            raise AssertionError("bitwidth not supported")
        self.n_bits = n_bits
        self.n_levels = 2 ** (self.n_bits - 1)
        self.q_min = -self.n_levels
        self.q_max = self.n_levels - 1
        self.delta = None
        self.zero_point = None
        self.inited = False
        self.leaf_param = leaf_param
        self.channel_wise = channel_wise
        self.scale_method = scale_method

    def forward(self, x: np.ndarray) -> np.ndarray:
        if not self.inited:
            self.delta, self.zero_point = self.init_quantization_scale(x, self.channel_wise)
            self.inited = True

        x_int = round_ste(x / self.delta) + self.zero_point
        x_quant = np.clip(x_int, self.q_min, self.q_max)
        x_dequant = (x_quant - self.zero_point) * self.delta
        return x_dequant.astype(x.dtype)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self.forward(x)

    def init_quantization_scale(self, x: np.ndarray, channel_wise: bool = False):
        if channel_wise:
            x_clone = x.copy()
            n_channels = x_clone.shape[0]
            delta_list = []
            zp_list = []
            for c in range(n_channels):
                d, zp = self.init_quantization_scale(x_clone[c], channel_wise=False)
                delta_list.append(d)
                zp_list.append(zp)
            delta = np.array(delta_list, dtype=x.dtype)
            zero_point = np.array(zp_list, dtype=x.dtype)
            if len(x.shape) == 4:
                delta = delta.reshape(-1, 1, 1, 1)
                zero_point = zero_point.reshape(-1, 1, 1, 1)
            else:
                delta = delta.reshape(-1, 1)
                zero_point = zero_point.reshape(-1, 1)
        else:
            if "max" in self.scale_method:
                x_min = min(x.min(), 0)
                x_max = max(x.max(), 0)

                if "scale" in self.scale_method:
                    x_min = x_min * (self.n_bits + 2) / 8
                    x_max = x_max * (self.n_bits + 2) / 8

                if self.symmetric:
                    x_absmax = max(abs(x_min), abs(x_max))
                    delta = float(x_absmax) / self.q_max
                    zero_point = 0.0
                else:
                    delta = float(x_max - x_min) / (self.n_levels - 1)
                    zero_point = round(-x_min / delta)

                if delta < 1e-8:
                    warnings.warn(f"Quantization range close to zero: [{x_min}, {x_max}]")
                    delta = 1e-8

                delta = np.array(delta, dtype=x.dtype)
                zero_point = np.array(zero_point, dtype=x.dtype)
            elif self.scale_method == "mse":
                x_max = x.max()
                x_min = x.min()
                best_score = 1e10
                for i in range(80):
                    alpha = 1.0 - (i * 0.01)
                    if self.symmetric:
                        curr_absmax = max(abs(x_min), abs(x_max)) * alpha
                        new_max = curr_absmax
                        new_min = -curr_absmax
                    else:
                        new_max = x_max * alpha
                        new_min = x_min * alpha

                    x_q = self.quantize_simulate(x, new_max, new_min)
                    score = lp_loss(x, x_q, p=2.4, reduction="all")

                    if score < best_score:
                        best_score = score
                        if self.symmetric:
                            delta = new_max / self.q_max
                            zero_point = np.array(0.0, dtype=x.dtype)
                        else:
                            delta = (new_max - new_min) / (2**self.n_bits - 1)
                            zero_point = np.round(-new_min / delta)

                delta = np.array(delta, dtype=x.dtype) if not isinstance(delta, np.ndarray) else delta
                zero_point = (
                    np.array(zero_point, dtype=x.dtype)
                    if not isinstance(zero_point, np.ndarray)
                    else zero_point
                )
            else:
                raise NotImplementedError

        self.delta = delta
        self.zero_point = zero_point
        return delta, zero_point

    def quantize_simulate(self, x: np.ndarray, max_val, min_val) -> np.ndarray:
        if self.symmetric:
            delta = max_val / self.q_max
            zero_point = 0
        else:
            delta = (max_val - min_val) / (2**self.n_bits - 1)
            zero_point = np.round(-min_val / delta)

        x_int = np.round(x / delta) + zero_point
        x_quant = np.clip(x_int, self.q_min, self.q_max)
        x_float_q = (x_quant - zero_point) * delta
        return x_float_q

    def bitwidth_refactor(self, refactored_bit: int):
        if not 2 <= refactored_bit <= 8:
            raise AssertionError("bitwidth not supported")
        self.n_bits = refactored_bit
        if self.symmetric:
            self.n_levels = 2 ** (self.n_bits - 1)
            self.q_min = -self.n_levels
            self.q_max = self.n_levels - 1
        else:
            self.n_levels = 2**self.n_bits
            self.q_min = 0
            self.q_max = self.n_levels - 1
