"""onnx-adaround: Pure ONNX-ecosystem reimplementation of AdaRound PTQ.

A torch-free, onnx2pytorch-free implementation of adaptive rounding
post-training quantization that operates directly on the ONNX graph.

Public API mirrors the original ``xmnn.adaround`` package.
"""

from .export import main, run_adaround
from .onnx_utils import QuantModel, build_weight_mapping, fold_bn_into_onnx
from .quant import AdaRoundQuantizer, UniformAffineQuantizer
from .recon import block_reconstruction, layer_reconstruction

__all__ = [
    "run_adaround",
    "main",
    "QuantModel",
    "fold_bn_into_onnx",
    "build_weight_mapping",
    "UniformAffineQuantizer",
    "AdaRoundQuantizer",
    "layer_reconstruction",
    "block_reconstruction",
]

__version__ = "0.1.0"
