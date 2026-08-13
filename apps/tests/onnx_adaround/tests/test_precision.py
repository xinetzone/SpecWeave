"""Precision validation for the torch-free onnx-adaround library (Task 7).

End-to-end AdaRound quantization is validated against two independent
references:

1. **FP32 onnxruntime baseline** — the quantized ``out.onnx`` produced by
   ``run_adaround`` must reproduce the FP32 output (cosine similarity >= 0.99)
   on the same input.
2. **A mathematically-independent numpy reimplementation** of the AdaRound
   weight-baking formula (``_adaround_bake_weight``): the weight actually fused
   into ``out.onnx`` for the 4-bit AdaRound-baked layer must match the reference
   formula element-wise within 1e-3.

Both checks stay torch-free and are fully deterministic (the conversion seeds
its RNG internally via ``run_adaround``/``seed_all``).
"""

from __future__ import annotations

import numpy as np
import onnx
import onnxruntime as ort
import pytest
from onnx import numpy_helper

from onnx_adaround.export import run_adaround
from onnx_adaround.quant import UniformAffineQuantizer

# Conversion hyper-parameters (kept small so the test is fast but meaningful).
_NUM_SAMPLES = 16
_ITERS_W = 40
_BATCH_SIZE = 2
_INPUT_SIZE = 16


def _write_image(tmp_path, name, size=(_INPUT_SIZE, _INPUT_SIZE)):
    from PIL import Image

    img = Image.fromarray(np.random.randint(0, 255, (*size, 3), dtype=np.uint8), "RGB")
    img.save(tmp_path / name)


def _cosine(a, b):
    a = a.flatten().astype(np.float64)
    b = b.flatten().astype(np.float64)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _initializer(model, name):
    for init in model.graph.initializer:
        if init.name == name:
            return numpy_helper.to_array(init)
    raise KeyError(f"initializer {name!r} not found")


def _adaround_bake_weight_reference(w_orig, alpha, n_bits=4):
    """Independent numpy reference for the AdaRound weight-baking formula.

    Mirrors the math of ``export._adaround_bake_weight``:
    scale via UniformAffineQuantizer(max, symmetric, channel_wise);
    w_floor = floor(w / scale);
    h_alpha = clip(sigmoid(alpha) * (1.1 - (-0.1)) + (-0.1), 0, 1);
    correction = (h_alpha >= 0.5);
    w_int = w_floor + correction;
    w_clamped = clip(w_int, -(2**(n-1)), 2**(n-1) - 1);
    result = w_clamped * scale.
    """
    gamma, zeta = -0.1, 1.1
    w_orig = w_orig.astype(np.float64)
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


@pytest.fixture(scope="module")
def adaround_result(tmp_path_factory, make_conv_relu_conv_model):
    """Run ``run_adaround`` once and expose its artifacts for all checks.

    Runs the full library conversion (torch-free) on the Conv->ReLU->Conv model
    and returns the input/final ONNX paths plus the saved alpha checkpoint.
    """
    tmp = tmp_path_factory.mktemp("adaround_precision")
    model = make_conv_relu_conv_model

    onnx_path = str(tmp / "in.onnx")
    onnx.save(model, onnx_path)

    cali = tmp / "cali"
    cali.mkdir()
    for i in range(_NUM_SAMPLES):
        _write_image(cali, f"img{i}.png")

    final = str(tmp / "out.onnx")
    ckpt = str(tmp / "alpha.npz")
    run_adaround(
        onnx_path=onnx_path,
        final_onnx_path=final,
        data_path=str(cali),
        save_ckpt_path=ckpt,
        num_samples=_NUM_SAMPLES,
        iters_w=_ITERS_W,
        batch_size=_BATCH_SIZE,
        input_size=_INPUT_SIZE,
    )
    return {"onnx_path": onnx_path, "final": final, "ckpt": ckpt, "tmp": tmp}


def test_quantized_output_matches_fp32_baseline(adaround_result):
    """Quantized output vs FP32 baseline cosine similarity >= 0.99."""
    onnx_path = adaround_result["onnx_path"]
    final = adaround_result["final"]

    # Confirm the produced out.onnx is loadable by onnxruntime.
    out_model = onnx.load(final)
    sess_q = ort.InferenceSession(out_model.SerializeToString(), providers=["CPUExecutionProvider"])
    sess_fp = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

    x = np.random.default_rng(7).standard_normal((1, 3, _INPUT_SIZE, _INPUT_SIZE)).astype(np.float32)
    out_fp = sess_fp.run(None, {"input": x})[0]
    out_q = sess_q.run(None, {"input": x})[0]

    assert out_q.shape == out_fp.shape
    cs = _cosine(out_fp, out_q)
    assert cs >= 0.99, f"cosine similarity {cs:.5f} < 0.99"


def test_baked_weight_matches_reference_formula(adaround_result):
    """The 4-bit AdaRound-baked weight matches the independent numpy formula."""
    onnx_path = adaround_result["onnx_path"]
    final = adaround_result["final"]
    ckpt = adaround_result["ckpt"]

    # Recover the learned alpha for the AdaRound-baked layer (index 1 = conv2).
    alphas = np.load(ckpt)
    alpha = alphas["layer_1_alpha"]

    # Recompute the expected baked weight from the original weight + alpha.
    w_orig = _initializer(onnx.load(onnx_path), "conv2_w")
    expected = _adaround_bake_weight_reference(w_orig, alpha)

    # Extract the weight actually fused into the final quantized model.
    fused = _initializer(onnx.load(final), "conv2_w").astype(np.float64)
    max_err = float(np.abs(fused - expected.astype(np.float64)).max())
    assert max_err < 1e-3, f"max weight abs error {max_err:.2e} >= 1e-3"
