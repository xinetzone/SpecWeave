"""Adam optimizer and temperature-decay utilities (numpy, torch-free)."""

from __future__ import annotations

import numpy as np


class Adam:
    """Adam optimizer over a dict of named numpy parameters.

    Mirrors torch.optim.Adam behavior with default betas=(0.9,0.999) and
    eps=1e-8. Bias correction is applied each step.
    """

    def __init__(self, params, lr: float = 1e-3, betas=(0.9, 0.999), eps: float = 1e-8):
        # params: dict name -> {"data": np.ndarray, "grad": np.ndarray}
        self.params = params
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.t = 0
        self.m = {k: np.zeros_like(p["data"]) for k, p in params.items()}
        self.v = {k: np.zeros_like(p["data"]) for k, p in params.items()}

    def zero_grad(self):
        for p in self.params.values():
            if p.get("grad") is not None:
                p["grad"][:] = 0.0

    def step(self):
        self.t += 1
        for k, p in self.params.items():
            g = p.get("grad")
            if g is None:
                continue
            self.m[k] = self.beta1 * self.m[k] + (1 - self.beta1) * g
            self.v[k] = self.beta2 * self.v[k] + (1 - self.beta2) * (g * g)
            m_hat = self.m[k] / (1 - self.beta1**self.t)
            v_hat = self.v[k] / (1 - self.beta2**self.t)
            p["data"] = p["data"] - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


class LinearTempDecay:
    """Linear temperature decay (mirrors torch reference LinearTempDecay)."""

    def __init__(self, t_max: int, rel_start_decay: float = 0.2, start_b: int = 10, end_b: int = 2):
        self.t_max = t_max
        self.start_decay = rel_start_decay * t_max
        self.start_b = start_b
        self.end_b = end_b

    def __call__(self, t: int) -> float:
        if t < self.start_decay:
            return float(self.start_b)
        rel_t = (t - self.start_decay) / (self.t_max - self.start_decay)
        return self.end_b + (self.start_b - self.end_b) * max(0.0, (1 - rel_t))
