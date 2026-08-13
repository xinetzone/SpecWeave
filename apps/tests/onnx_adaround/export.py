"""End-to-end AdaRound export for ONNX models (torch-free).

Mirrors ``xmnn.adaround.adaround_onnx_export`` but operates purely on the ONNX
graph + numpy, using onnxruntime for reference activations.
"""

from __future__ import annotations

import argparse
import os
import random

import numpy as np
import onnx
from onnx import numpy_helper

from .data import load_calibration_data
from .onnx_utils import (
    QuantModel,
    build_weight_mapping,
    fold_bn_into_onnx,
)
from .quant import UniformAffineQuantizer
from .recon import (
    block_reconstruction,
    cache_layer_inp_out,
)


def str2bool(value):
    if isinstance(value, bool):
        return value
    value = value.lower()
    if value in ("true", "1", "yes", "y", "on"):
        return True
    if value in ("false", "0", "no", "n", "off"):
        return False
    raise argparse.ArgumentTypeError(f"Invalid bool value: {value}")


def seed_all(seed: int = 1029):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)


def _adaround_bake_weight(layer, n_bits: int):
    """Bake AdaRound-rounded weight into a dequantized float array."""
    gamma, zeta = -0.1, 1.1
    w_orig = layer.weight.astype(np.float64)
    alpha = layer.alpha

    lower_bound = -(2 ** (n_bits - 1))
    upper_bound = 2 ** (n_bits - 1) - 1

    q = UniformAffineQuantizer(
        n_bits=n_bits, symmetric=True, channel_wise=True, scale_method="max"
    )
    scale, _ = q.init_quantization_scale(w_orig, channel_wise=True)
    scale = np.clip(scale, min=1e-8)

    w_floor = np.floor(w_orig / scale)
    sigmoid_alpha = 1.0 / (1.0 + np.exp(-alpha))
    h_alpha = np.clip(sigmoid_alpha * (zeta - gamma) + gamma, 0, 1)
    correction = (h_alpha >= 0.5).astype(np.float64)
    w_int = w_floor + correction
    w_clamped = np.clip(w_int, lower_bound, upper_bound)
    return (w_clamped * scale).astype(np.float32)


def fuse_quant_to_onnx(onnx_model, qnn: QuantModel):
    """Bake quantized weights back into the ONNX initializers."""
    name_to_init = build_weight_mapping(onnx_model)
    init_map = {init.name: init for init in onnx_model.graph.initializer}
    adaround_count = 0
    fused_count = 0

    for name, layer in qnn.named_layers():
        if layer.op_type not in ("Conv", "ConvTranspose"):
            continue
        groups = int(layer.attrs.get("group", 1))
        n_bits = 4 if layer.weight.shape[0] / groups > 16 else 8
        w_orig = layer.weight.astype(np.float64)

        if getattr(layer, "alpha", None) is not None and n_bits == 4:
            w_baked = _adaround_bake_weight(layer, n_bits)
            tag = f"AdaRound {n_bits}-bit"
            adaround_count += 1
        else:
            if layer.weight_quantizer.delta is None:
                _ = layer.weight_quantizer(w_orig)
            w_baked = layer.weight_quantizer(w_orig)
            tag = f"NaiveQuant {n_bits}-bit"

        init_name = name_to_init.get(name)
        if not init_name:
            print(f"[Warn] No ONNX initializer mapping found for {name}")
            continue
        if init_name not in init_map:
            print(f"[Warn] Initializer {init_name} not found")
            continue

        arr = w_baked.astype(np.float32)
        new_tensor = numpy_helper.from_array(arr, name=init_name)
        init_map[init_name].CopyFrom(new_tensor)
        fused_count += 1
        print(f"[{tag}] {name} -> {init_name}")

    print(f"[-] AdaRound layers: {adaround_count}, Total fused weights: {fused_count}")


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Run AdaRound and directly export fused ONNX model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--onnx_path", required=True, type=str)
    parser.add_argument("--final_onnx_path", required=True, type=str)
    parser.add_argument("--save_ckpt_path", default="", type=str)
    parser.add_argument("--data_path", required=True, type=str)
    parser.add_argument("--batch_size", default=32, type=int)
    parser.add_argument("--workers", default=4, type=int)
    parser.add_argument("--input_size", default=224, type=int)
    parser.add_argument("--input_h", default=None, type=int)
    parser.add_argument("--input_w", default=None, type=int)
    parser.add_argument("--input_format", default="RGB", type=str,
                        choices=["RGB", "BGR", "GRAY"])
    parser.add_argument("--mean", nargs="+", default=[0.485, 0.456, 0.406], type=float)
    parser.add_argument("--std", nargs="+", default=[0.229, 0.224, 0.225], type=float)
    parser.add_argument("--n_bits_w", default=4, type=int)
    parser.add_argument("--n_bits_a", default=8, type=int)
    parser.add_argument("--num_samples", default=512, type=int)
    parser.add_argument("--iters_w", default=1000, type=int)
    parser.add_argument("--weight_layer", default=0.01, type=float)
    parser.add_argument("--b_start", default=20, type=int)
    parser.add_argument("--b_end", default=2, type=int)
    parser.add_argument("--warmup", default=0.2, type=float)
    parser.add_argument("--channel_wise", default=True, type=str2bool)
    parser.add_argument("--disable_8bit_head_stem", action="store_true")
    return parser


def run_adaround(
    onnx_path: str,
    final_onnx_path: str,
    data_path: str,
    save_ckpt_path: str = "",
    batch_size: int = 32,
    workers: int = 4,
    input_size=224,
    input_h: int | None = None,
    input_w: int | None = None,
    input_format: str = "RGB",
    mean=None,
    std=None,
    n_bits_w: int = 4,
    n_bits_a: int = 8,
    num_samples: int = 512,
    iters_w: int = 1000,
    weight_layer: float = 0.01,
    b_start: int = 20,
    b_end: int = 2,
    warmup: float = 0.2,
    channel_wise: bool = True,
    disable_8bit_head_stem: bool = False,
):
    mean = [0.485, 0.456, 0.406] if mean is None else mean
    std = [0.229, 0.224, 0.225] if std is None else std

    seed_all(1029)

    print(f"[1/6] Loading ONNX model from {onnx_path}")
    onnx_model = onnx.load(onnx_path)

    print("[2/6] Folding BatchNorm and building QuantModel")
    fold_bn_into_onnx(onnx_model)
    wq_params = {
        "n_bits": n_bits_w,
        "symmetric": True,
        "channel_wise": channel_wise,
        "scale_method": "max",
    }
    aq_params = {
        "n_bits": n_bits_a,
        "symmetric": False,
        "channel_wise": False,
        "scale_method": "mse",
    }
    qnn = QuantModel(onnx_model, weight_quant_params=wq_params, act_quant_params=aq_params)

    if not disable_8bit_head_stem:
        print("Setting first layer to 8-bit")
        qnn.set_first_last_layer_to_8bit()

    print("[3/6] Loading calibration data")
    input_size = (input_h, input_w) if input_h is not None and input_w is not None else input_size
    cali_data = load_calibration_data(
        data_path, num_samples=num_samples, input_size=input_size,
        input_format=input_format, mean=mean, std=std,
    )
    print(f"Calibration dataset loaded with {cali_data.shape[0]} samples")
    effective_batch_size = min(batch_size, cali_data.shape[0])

    print("[4/6] Caching layer activations (onnxruntime)")
    inp_batches, out_batches = cache_layer_inp_out(onnx_model, qnn.layers, cali_data,
                                                   batch_size=effective_batch_size)

    print("[5/6] Starting layer-wise reconstruction (AdaRound)")
    kwargs = dict(
        iters=iters_w,
        weight=weight_layer,
        asym=True,
        b_range=(b_start, b_end),
        warmup=warmup,
        opt_mode="mse",
        batch_size=effective_batch_size,
    )
    for i, (name, layer) in enumerate(qnn.named_layers()):
        if layer.ignore_reconstruction:
            print(f"Ignore reconstruction of layer {name}")
            continue
        print(f"Reconstruction for layer {name}")
        block_reconstruction(
            qnn, [layer], [inp_batches[i]], [out_batches[i]], **kwargs
        )

    if save_ckpt_path:
        print("[6/6] Saving checkpoint and fusing quantized weights")
        np.savez(save_ckpt_path if save_ckpt_path.endswith(".npz") else save_ckpt_path + ".npz",
                 **{f"layer_{i}_alpha": layer.alpha for i, (_, layer) in enumerate(qnn.named_layers())
                    if layer.alpha is not None})
    else:
        print("[6/6] Fusing quantized weights into ONNX")

    fuse_quant_to_onnx(onnx_model, qnn)
    onnx.save(onnx_model, final_onnx_path)
    print(f"[Done] Final quantized ONNX saved to {final_onnx_path}")
    return final_onnx_path


def main(argv=None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    return run_adaround(**vars(args))


if __name__ == "__main__":
    main()
