#!/usr/bin/env python3
"""Build a machine-readable manifest of all Caffe models in the hub model library.

Scans ``external/chaos/xmtools/models/hub/caffe/`` for model directories that
contain at least one ``.caffemodel``, reads each ``config.toml``, and resolves a
"standard deploy" prototxt + caffemodel + input shape triple for CPU-based
forward comparison between caffe-ffi and caffex.

Prototxt variant rule: among the ``.prototxt`` files in a model directory the
standard one is preferred (a file that is NOT an NPU/compile variant such as
``*_xm530v200``, ``*_org``, ``*_sigmoid``, ``*_deploy``).  All variants are
recorded so the choice is auditable.
"""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

HUB_CAFFE = Path(r"d:\spaces\SpecWeave\external\chaos\xmtools\models\hub\caffe")

# Candidate fallbacks in case the explicit path is not found.
NPU_VARIANT_RE = re.compile(
    r"(xm\s*\d+v\d+|530v200|530v300|650v300|_org|_old|cp_|_peridot)", re.IGNORECASE
)


def _find_files(root: Path) -> dict[str, list[Path]]:
    prototxts, caffemodels = [], []
    for p in root.rglob("*"):
        if p.suffix == ".prototxt":
            prototxts.append(p)
        elif p.suffix == ".caffemodel":
            caffemodels.append(p)
    return {"prototxts": sorted(prototxts), "caffemodels": sorted(caffemodels)}


def _prefer_prototxt(candidates: list[Path], toml_ref: str | None,
                     dir_name: str) -> Path | None:
    """Pick the standard (non NPU-variant) prototxt for CPU forward."""
    if not candidates:
        return None
    # 1) explicit config reference if it exists and is not an NPU variant
    if toml_ref:
        for c in candidates:
            if c.name == toml_ref and not NPU_VARIANT_RE.search(c.name):
                return c
    # 2) file whose stem equals the model dir name (canonical deploy prototxt)
    for c in candidates:
        if c.stem == dir_name:
            return c
    # 3) first non-NPU-variant file
    for c in candidates:
        if not NPU_VARIANT_RE.search(c.name):
            return c
    # 4) explicit config reference (any variant) if present
    if toml_ref:
        for c in candidates:
            if c.name == toml_ref:
                return c
    # 5) last resort: first candidate
    return candidates[0]


def _prefer_caffemodel(candidates: list[Path], toml_ref: str | None) -> Path | None:
    if not candidates:
        return None
    if toml_ref:
        for c in candidates:
            if c.name == toml_ref:
                return c
    for c in candidates:
        if "deploy" not in c.name.lower() and "train" not in c.name.lower():
            return c
    return candidates[0]


def _read_toml(path: Path | None) -> dict:
    if path is None or not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _input_from_toml(cfg: dict) -> tuple[str | None, list[int] | None]:
    inp = cfg.get("input", {})
    name = inp.get("name") if isinstance(inp, dict) else None
    shape = inp.get("shape") if isinstance(inp, dict) else None
    if isinstance(shape, list):
        shape = [int(x) for x in shape]
    return name, shape


def _input_from_prototxt(proto: Path | None) -> tuple[str | None, list[int] | None]:
    """Best-effort parse of input name / shape from a deploy prototxt."""
    if proto is None or not proto.exists():
        return None, None
    text = proto.read_text(encoding="utf-8", errors="replace")
    name = None
    m = re.search(r'input:\s*"([^"]+)"', text)
    if m:
        name = m.group(1)
    dims = re.findall(r"dim:\s*(\d+)", text)
    shape = [int(d) for d in dims[:4]] if dims else None
    return name, shape


def main() -> None:
    root = HUB_CAFFE
    if not root.exists():
        raise SystemExit(f"hub caffe dir not found: {root}")
    manifest = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        files = _find_files(d)
        if not files["caffemodels"]:
            print(f"[skip] {d.name}: no .caffemodel")
            continue
        cfg = _read_toml(d / "config.toml")
        model_cfg = cfg.get("model", {}) if isinstance(cfg, dict) else {}
        proto_ref = model_cfg.get("prototxt_file_path")
        cm_ref = model_cfg.get("caffemodel_file_path")
        proto = _prefer_prototxt(files["prototxts"], proto_ref, d.name)
        cm = _prefer_caffemodel(files["caffemodels"], cm_ref)
        in_name, in_shape = _input_from_toml(cfg)
        if in_name is None or in_shape is None:
            in_name, in_shape = _input_from_prototxt(proto)
        entry = {
            "name": d.name,
            "dir": str(d),
            "has_config": (d / "config.toml").exists(),
            "prototxt": str(proto) if proto else None,
            "caffemodel": str(cm) if cm else None,
            "input_name": in_name,
            "input_shape": in_shape,
            "config_ref_prototxt": proto_ref,
            "config_ref_caffemodel": cm_ref,
            "all_prototxt_variants": [str(p) for p in files["prototxts"]],
            "all_caffemodel_variants": [str(p) for p in files["caffemodels"]],
        }
        manifest.append(entry)
        print(f"[ok] {d.name}: proto={proto.name if proto else None} "
              f"cm={cm.name if cm else None} input={in_name}{in_shape}")

    out = root if False else Path(__file__).resolve().parent
    out_file = out / "models_manifest.json"
    out_file.write_text(
        json.dumps({"hub_caffe_root": str(root), "models": manifest},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nWrote {len(manifest)} models -> {out_file}")


if __name__ == "__main__":
    main()