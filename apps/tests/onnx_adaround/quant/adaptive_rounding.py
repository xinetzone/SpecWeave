"""Adaptive Rounding quantizer (pure numpy, torch-free).

Mirrors ``xmnn.adaround.quant.adaptive_rounding``. Learned rounding (hard
sigmoid) with a learnable ``alpha`` parameter optimized during reconstruction.
"""

from __future__ import annotations

import numpy as np


class AdaRoundQuantizer:
    """Adaptive Rounding Quantizer.

    Optimizes the rounding policy by reconstructing intermediate output.
    Based on: Up or Down? Adaptive Rounding for Post-Training Quantization
    (arXiv:2004.10568).

    :param n_bits: bit width
    :param delta: quantization scale
    :param zero_point: quantization zero point
    :param weight_tensor: initializer for alpha
    """

    def __init__(
        self,
        n_bits: int,
        delta,
        zero_point,
        weight_tensor: np.ndarray,
        round_mode: str = "learned_hard_sigmoid",
    ):
        self.n_bits = n_bits
        self.delta = delta
        self.zero_point = zero_point
        self.n_levels = 2 ** (self.n_bits - 1)

        self.round_mode = round_mode
        self.alpha = None
        self.soft_targets = False

        self.gamma, self.zeta = -0.1, 1.1
        self.beta = 2 / 3
        self.init_alpha(x=weight_tensor.copy())

    def forward(self, x: np.ndarray) -> np.ndarray:
        if self.round_mode == "nearest":
            x_int = np.round(x / self.delta)
        elif self.round_mode == "nearest_ste":
            x_int = (np.round(x / self.delta) - x / self.delta) + x / self.delta
        elif self.round_mode == "stochastic":
            x_floor = np.floor(x / self.delta)
            rest = (x / self.delta) - x_floor
            x_int = x_floor + (np.random.random(rest.shape) < rest).astype(x.dtype)
            print("Draw stochastic sample")
        elif self.round_mode == "learned_hard_sigmoid":
            x_floor = np.floor(x / self.delta)
            if self.soft_targets:
                x_int = x_floor + self.get_soft_targets()
            else:
                x_int = x_floor + (self.alpha >= 0).astype(x.dtype)
        else:
            raise ValueError("Wrong rounding mode")
        x_quant = np.clip(x_int + self.zero_point, -self.n_levels, self.n_levels - 1)
        x_float_q = (x_quant - self.zero_point) * self.delta
        return x_float_q.astype(x.dtype)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self.forward(x)

    def get_soft_targets(self) -> np.ndarray:
        return np.clip(
            _sigmoid(self.alpha) * (self.zeta - self.gamma) + self.gamma, 0, 1
        )

    def init_alpha(self, x: np.ndarray):
        x_floor = np.floor(x / self.delta)
        if self.round_mode == "learned_hard_sigmoid":
            rest = (x / self.delta) - x_floor
            alpha = -np.log((self.zeta - self.gamma) / (rest - self.gamma) - 1)
            self.alpha = alpha.astype(np.float64)
        else:
            raise NotImplementedError


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))
