"""Loss functions for AdaRound reconstruction (numpy, torch-free)."""

from __future__ import annotations

from . import ops
from .optim import LinearTempDecay

__all__ = ["LinearTempDecay", "mse_loss", "relaxation_round_loss"]


def mse_loss(pred, tgt, p: float = 2.0):
    """Scalar MSE (Lp) reconstruction loss over all elements.

    Mirrors ``lp_loss(pred, tgt, p=p, reduction='all')``, i.e. the mean of the
    element-wise absolute Lp error over the whole tensor.
    """
    diff = ops.pow((pred - tgt), p)  # (batch, ...)
    return diff.mean()


def relaxation_round_loss(alpha, weight: float, b: float):
    """Relaxation rounding loss over a soft-target alpha tensor.

    Mirrors the torch reference:
        round_vals = get_soft_targets()
        weight * (1 - abs(round_vals - .5)*2).pow(b)).sum()
    where round_vals = clip(sigmoid(alpha)*(zeta-gamma)+gamma, 0, 1).
    """
    gamma, zeta = -0.1, 1.1
    round_vals = ops.clip(ops.sigmoid(alpha) * (zeta - gamma) + gamma, 0.0, 1.0)
    term = ops.pow((1.0 - (ops.abs(round_vals - 0.5) * 2.0)), b)
    return weight * term.sum()
