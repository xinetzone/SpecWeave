# onnx-adaround API Reference

A torch-free, onnx2pytorch-free reimplementation of AdaRound post-training
quantization operating directly on the ONNX graph.

## Public API (top-level)

### `run_adaround(...)`
End-to-end AdaRound export. Mirrors the original `xmnn.adaround.run_adaround`.

**Signature**
```python
run_adaround(
    onnx_path: str, final_onnx_path: str, data_path: str,
    save_ckpt_path: str = "",
    batch_size: int = 32, workers: int = 4, input_size=224,
    input_h=None, input_w=None, input_format: str = "RGB",
    mean=None, std=None,
    n_bits_w: int = 4, n_bits_a: int = 8, num_samples: int = 512,
    iters_w: int = 1000, weight_layer: float = 0.01,
    b_start: int = 20, b_end: int = 2, warmup: float = 0.2,
    channel_wise: bool = True, disable_8bit_head_stem: bool = False,
) -> str
```
Returns the `final_onnx_path`.

### `QuantModel`
Wraps an ONNX model and exposes its quantizable layers (Conv/ConvTranspose/
MatMul/Gemm) in order, each with a numpy weight and quantizer.

```python
from onnx_adaround import QuantModel
qnn = QuantModel(model, weight_quant_params={...}, act_quant_params={...})
qnn.named_layers()          # [(name, QuantLayer), ...]
qnn.set_first_last_layer_to_8bit()
```

### `fold_bn_into_onnx(model)`
Graph-level BatchNorm folding into preceding quantizable ops; removes BN nodes
and updates weight/bias initializers.

### `build_weight_mapping(model)`
Maps layer output name → weight initializer name for Conv/ConvTranspose.

## Quant package (`onnx_adaround.quant`)

### `UniformAffineQuantizer`
Uniform affine quantizer (max/mse scale methods, channel-wise, symmetric).
Mirrors `xmnn.adaround.quant.quant_layer.UniformAffineQuantizer`.

```python
from onnx_adaround import UniformAffineQuantizer
q = UniformAffineQuantizer(n_bits=4, symmetric=True, channel_wise=True, scale_method="max")
out = q(weight_numpy_array)
```

### `AdaRoundQuantizer`
Learned hard-sigmoid rounding quantizer with learnable `alpha`.

```python
from onnx_adaround import AdaRoundQuantizer
ar = AdaRoundQuantizer(n_bits=4, delta=..., zero_point=..., weight_tensor=w)
ar.soft_targets = True
out = ar(w)
```

## Recon package (`onnx_adaround.recon`)

### `layer_reconstruction(model, layer, inp_cache, out_cache, ...)`
Optimizes a single layer's rounding policy (`alpha`) against FP32 reference
activations using the built-in numpy autodiff engine + Adam.

### `block_reconstruction(model, block_layers, inp_cache, out_cache, ...)`
Reconstructs a block by iterating per-layer reconstruction.

### `cache_layer_inp_out(model, layers, cali_data, batch_size=32)`
Runs the FP32 model once via onnxruntime with intermediate outputs registered,
returning `(inp_batches, out_batches)` aligned with `layers`.

## Data package (`onnx_adaround.data`)

### `load_calibration_data(data_path, num_samples, input_size=224, ...)`
Pillow+numpy loader returning an NCHW float32 array.

## Autodiff package (`onnx_adaround.autodiff`)

- `Tensor` — numpy-backed reverse-mode autodiff tensor.
- `ops` — `conv2d`, `matmul`, `add`, `mul`, `relu`, `sigmoid`, `round_ste`,
  `floor`, `clip`, `abs`, `pow`, `sum`, `mean`.
- `Adam` — Adam optimizer (torch-compatible defaults).
- `LinearTempDecay` — temperature schedule for rounding loss annealing.
- `mse_loss`, `relaxation_round_loss` — reconstruction / rounding losses.
