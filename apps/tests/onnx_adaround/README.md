# onnx-adaround

Pure **ONNX-ecosystem** reimplementation of AdaRound post-training quantization.

A torch-free, onnx2pytorch-free library that performs adaptive rounding (AdaRound)
weight quantization directly on the ONNX graph, mirroring the functionality of
`xmnn.adaround` without any PyTorch dependency.

## Why this library

The original `xmnn.adaround` depends on `onnx2pytorch` (ONNX→PyTorch conversion) and
torch for quantization. `onnx2pytorch` has known functional defects and torch is a
heavy (~2 GB), non-portable dependency. This library:

- Works **directly on the ONNX graph** (graph-level BN folding, initializer fusion).
- Uses only the ONNX ecosystem: `onnx`, `onnxruntime`, `onnxscript`, `numpy`, `Pillow`.
- **Never imports torch / torchvision / onnx2pytorch** — verified by static checks.
- Uses a lightweight built-in numpy reverse-mode autodiff engine for optimizing the
  learnable rounding policy (`alpha`).

## Installation

```bash
pip install -e .          # from the package root
```

Dev/test deps (optional, only for running the test suite / reference cross-checks):

```bash
pip install -e ".[dev]"
```

## Usage

### CLI

```bash
python -m onnx_adaround \
    --onnx_path model.onnx \
    --final_onnx_path model_quant.onnx \
    --data_path ./calibration_images \
    --num_samples 512 \
    --iters_w 1000
```

### Python API

```python
from onnx_adaround import run_adaround

run_adaround(
    onnx_path="model.onnx",
    final_onnx_path="model_quant.onnx",
    data_path="./calibration_images",
    num_samples=512,
    iters_w=1000,
)
```

## Requirements / Constraints

| Allowed | Forbidden |
|---|---|
| onnx, onnxruntime, onnxscript, numpy, Pillow | torch |
| ONNX-ecosystem gradient extensions (optional) | torchvision |
| | onnx2pytorch and any derivative |

## Development

```bash
pytest --cov=onnx_adaround          # tests + coverage (>=80%, key modules >=90%)
ruff check onnx_adaround            # PEP 8 lint
```

Static zero-torch-dependency check:

```bash
grep -rE "import torch|from torch|onnx2pytorch" onnx_adaround/ && echo "VIOLATION" || echo "OK"
```

## Project layout

```
onnx_adaround/
├── autodiff/       # numpy reverse-mode autodiff engine + Adam + losses
├── data/           # Pillow-based calibration loader
├── quant/          # UniformAffineQuantizer, AdaRoundQuantizer
├── recon/          # layer/block reconstruction + activation caching
├── onnx_utils.py   # ONNX load, graph-level BN folding, QuantModel
├── export.py       # run_adaround CLI + weight fusion
└── tests/          # pytest suite
```

See [docs/api.md](docs/api.md) for the full API reference.
