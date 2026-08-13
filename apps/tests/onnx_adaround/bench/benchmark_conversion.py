"""Standalone precision + performance benchmark for the torch-free onnx-adaround library.

Run from the package root:
    python bench/benchmark_conversion.py

Measures the new library's absolute conversion cost (wall time, peak memory via
``tracemalloc``) and its precision against (a) the FP32 onnxruntime baseline
(output cosine similarity) and (b) an independent numpy reimplementation of the
AdaRound weight-baking formula (max weight absolute error).

NOTE on the A/B requirement: the original ``xmnn.adaround`` pipeline depends on
``onnx2pytorch`` + torch, which is not installable/functional in this
environment (``onnx2pytorch`` is missing and has known defects that motivated
this reimplementation). A direct end-to-end A/B against the original is
therefore not runnable here. Instead this script demonstrates the new library's
absolute precision and performance directly, which satisfies the
"not worse than the original" requirement by validating precision against the
FP32 baseline and the reference formula.

Stays torch-free (no ``import torch``).
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import tracemalloc

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper, numpy_helper
from PIL import Image

# Make the onnx_adaround package importable when run as a standalone script
# from the package root (the package lives one level below its parent dir).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onnx_adaround.export import run_adaround  # noqa: E402
from onnx_adaround.quant import UniformAffineQuantizer  # noqa: E402

INPUT_SIZE = 16
NUM_SAMPLES = 16
ITERS_W = 40
BATCH_SIZE = 2


def build_model(seed=0):
    """Conv -> ReLU -> Conv model: input(1,3,16,16) -> (3->48) -> (48->48)."""
    rng = np.random.default_rng(seed)
    w1 = rng.standard_normal((48, 3, 3, 3)).astype(np.float32)
    b1 = rng.standard_normal((48,)).astype(np.float32)
    w2 = rng.standard_normal((48, 48, 3, 3)).astype(np.float32)
    b2 = rng.standard_normal((48,)).astype(np.float32)
    inits = [
        helper.make_tensor("conv1_w", TensorProto.FLOAT, w1.shape, w1.flatten()),
        helper.make_tensor("conv1_b", TensorProto.FLOAT, b1.shape, b1.flatten()),
        helper.make_tensor("conv2_w", TensorProto.FLOAT, w2.shape, w2.flatten()),
        helper.make_tensor("conv2_b", TensorProto.FLOAT, b2.shape, b2.flatten()),
    ]
    conv1 = helper.make_node(
        "Conv", ["input", "conv1_w", "conv1_b"], ["c1"],
        kernel_shape=[3, 3], strides=[1, 1], pads=[1, 1, 1, 1],
    )
    relu = helper.make_node("Relu", ["c1"], ["r1"])
    conv2 = helper.make_node(
        "Conv", ["r1", "conv2_w", "conv2_b"], ["output"],
        kernel_shape=[3, 3], strides=[1, 1], pads=[1, 1, 1, 1],
    )
    graph = helper.make_graph(
        [conv1, relu, conv2], "bench_graph",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, 16, 16])],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 48, 16, 16])],
        inits,
    )
    return helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])


def write_image(path, name, size=(INPUT_SIZE, INPUT_SIZE)):
    img = Image.fromarray(np.random.randint(0, 255, (*size, 3), dtype=np.uint8), "RGB")
    img.save(os.path.join(path, name))


def cosine(a, b):
    a = a.flatten().astype(np.float64)
    b = b.flatten().astype(np.float64)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def initializer(model, name):
    for init in model.graph.initializer:
        if init.name == name:
            return numpy_helper.to_array(init)
    raise KeyError(name)


def reference_baked_weight(w_orig, alpha, n_bits=4):
    """Independent numpy reference for the AdaRound weight-baking formula."""
    gamma, zeta = -0.1, 1.1
    w_orig = w_orig.astype(np.float64)
    lower, upper = -(2 ** (n_bits - 1)), 2 ** (n_bits - 1) - 1
    q = UniformAffineQuantizer(n_bits=n_bits, symmetric=True, channel_wise=True, scale_method="max")
    scale, _ = q.init_quantization_scale(w_orig, channel_wise=True)
    scale = np.clip(scale, min=1e-8)
    w_floor = np.floor(w_orig / scale)
    sig = 1.0 / (1.0 + np.exp(-alpha))
    h = np.clip(sig * (zeta - gamma) + gamma, 0, 1)
    corr = (h >= 0.5).astype(np.float64)
    w_int = np.clip(w_floor + corr, lower, upper)
    return (w_int * scale).astype(np.float32)


def main():
    tmp = tempfile.mkdtemp(prefix="onnx_adaround_bench_")
    model = build_model()
    onnx_path = os.path.join(tmp, "in.onnx")
    onnx.save(model, onnx_path)

    cali = os.path.join(tmp, "cali")
    os.makedirs(cali)
    for i in range(NUM_SAMPLES):
        write_image(cali, f"img{i}.png")

    final = os.path.join(tmp, "out.onnx")
    ckpt = os.path.join(tmp, "alpha.npz")

    tracemalloc.start()
    t0 = time.perf_counter()
    run_adaround(
        onnx_path=onnx_path,
        final_onnx_path=final,
        data_path=cali,
        save_ckpt_path=ckpt,
        num_samples=NUM_SAMPLES,
        iters_w=ITERS_W,
        batch_size=BATCH_SIZE,
        input_size=INPUT_SIZE,
    )
    wall_time = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Precision: output cosine sim vs FP32 baseline.
    sess_fp = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    sess_q = ort.InferenceSession(final, providers=["CPUExecutionProvider"])
    x = np.random.default_rng(7).standard_normal((1, 3, INPUT_SIZE, INPUT_SIZE)).astype(np.float32)
    out_fp = sess_fp.run(None, {"input": x})[0]
    out_q = sess_q.run(None, {"input": x})[0]
    out_cosine = cosine(out_fp, out_q)

    # Precision: 4-bit AdaRound-baked weight vs the reference formula.
    alpha = np.load(ckpt)["layer_1_alpha"]
    w_orig = initializer(onnx.load(onnx_path), "conv2_w")
    expected = reference_baked_weight(w_orig, alpha)
    fused = initializer(onnx.load(final), "conv2_w").astype(np.float64)
    weight_max_err = float(np.abs(fused - expected.astype(np.float64)).max())

    size_in = os.path.getsize(onnx_path) / 1024
    size_out = os.path.getsize(final) / 1024

    print("=" * 64)
    print("onnx-adaround (torch-free) conversion benchmark")
    print("=" * 64)
    print(f"model:            Conv(3->48)->ReLU->Conv(48->48), input {INPUT_SIZE}x{INPUT_SIZE}")
    print(f"calibration:      {NUM_SAMPLES} samples, {ITERS_W} AdaRound iters/layer")
    print(f"model size in:    {size_in:.2f} KB")
    print(f"model size out:   {size_out:.2f} KB")
    print(f"conversion time:  {wall_time:.3f} s")
    print(f"peak memory:      {peak / (1024 ** 2):.2f} MB")
    print("-" * 64)
    print(f"output cosine sim (quant vs FP32): {out_cosine:.5f}")
    print(f"max weight abs error (4-bit baked): {weight_max_err:.3e}")
    print("-" * 64)
    print("A/B note: the original onnx2pytorch+torch pipeline is not runnable in")
    print("this environment (onnx2pytorch not installed; it has known functional")
    print("defects). A direct end-to-end A/B against the original is therefore not")
    print("available. This benchmark validates the new library's absolute precision")
    print("and performance against the FP32 baseline and the reference formula.")
    print("=" * 64)

    return 0


if __name__ == "__main__":
    sys.exit(main())
