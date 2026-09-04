"""Shared helpers for network-level comparison harness.

Runs inside the caffe-ffi container (/SpecWeave mount) or the caffex
origin-runtime container (workspace mounted at /SpecWeave). Windows paths in
models_manifest.json are converted to /SpecWeave/... container paths.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import numpy as np

# Windows workspace root -> container mount root
_WIN_ROOT = Path(r"d:\spaces\SpecWeave")
_CTR_ROOT = Path("/SpecWeave")

SEED = 42

# Where raw output arrays are stored (per impl), keyed by model name.
RAW_SUBDIR = "raw_outputs"


def raw_dir(impl: str, out_json: str) -> Path:
    """Return the directory where raw output arrays for `impl` are stored.

    The out_json argument is the results JSON path; raw arrays live in a sibling
    'raw_outputs/<impl>/' directory so they persist on the shared mount.
    """
    base = Path(out_json).parent
    d = base / RAW_SUBDIR / impl
    return d


def save_raw(impl: str, out_json: str, model_name: str, outputs: dict) -> None:
    """Save raw output arrays as one .npy per output blob in raw_dir."""
    d = raw_dir(impl, out_json)
    d.mkdir(parents=True, exist_ok=True)
    for oname, arr in outputs.items():
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(oname))
        np.save(d / f"{model_name}__{safe}.npy", np.asarray(arr, dtype=np.float32))


def to_container_path(p: str) -> str:
    """Convert a manifest Windows path to the in-container /SpecWeave path.

    Manifest paths are Windows-style (backslash separators). The container runs
    Linux, so normalize backslashes to forward slashes before deriving the
    relative path, then rewrite under /SpecWeave.
    """
    if not p:
        return p
    norm = p.replace("\\", "/")
    # Normalize drive prefix: d:/spaces/SpecWeave -> /SpecWeave
    lower = norm.lower()
    if lower.startswith("d:/spaces/specweave"):
        rel = norm[len("d:/spaces/SpecWeave"):].lstrip("/")
        return str(_CTR_ROOT / rel)
    # Already a container/linux path: leave as-is
    if norm.startswith("/"):
        return norm
    return norm


def load_manifest(manifest_path: str) -> list[dict]:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["models"]


def make_input(shape: list[int], seed: int = SEED) -> np.ndarray:
    """Fixed random float32 input (values in [0,1]) for a given input shape."""
    rng = np.random.default_rng(seed)
    return rng.random(tuple(shape), dtype=np.float32)


def tensor_stats(arr: np.ndarray) -> dict:
    a = arr.astype(np.float32)
    finite = np.isfinite(a)
    return {
        "shape": list(a.shape),
        "size": int(a.size),
        "mean": float(a.mean()) if a.size else None,
        "std": float(a.std()) if a.size else None,
        "min": float(a.min()) if a.size else None,
        "max": float(a.max()) if a.size else None,
        "has_nan": bool(np.isnan(a).any()),
        "has_inf": bool(np.isinf(a).any()),
        "finite_ratio": float(finite.mean()) if a.size else None,
    }


def first_conv_weight_stats(layers) -> dict:
    """Return weight stats of the first layer of type Convolution (or any layer with blobs)."""
    for layer in layers:
        blobs = getattr(layer, "blobs", None)
        if blobs is None or not blobs:
            continue
        try:
            w = blobs[0].data
        except Exception:
            continue
        if w.size == 0:
            continue
        return {
            "layer": getattr(layer, "name", ""),
            "type": getattr(layer, "type", ""),
            **tensor_stats(w),
        }
    return None