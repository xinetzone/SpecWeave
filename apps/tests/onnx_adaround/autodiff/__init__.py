"""Lightweight numpy reverse-mode autodiff engine for onnx-adaround.

Covers the ops needed for AdaRound weight reconstruction: conv2d, matmul/add
(linear), relu, sigmoid, and a straight-through round op (round_ste). No torch.
"""

from . import ops
from .loss import LinearTempDecay, mse_loss, relaxation_round_loss
from .optim import Adam
from .tensor import Tensor

__all__ = ["Tensor", "ops", "Adam", "LinearTempDecay", "mse_loss", "relaxation_round_loss"]
