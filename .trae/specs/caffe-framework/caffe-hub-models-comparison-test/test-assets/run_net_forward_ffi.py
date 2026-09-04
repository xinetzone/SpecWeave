"""caffe-ffi 全模型网络级前向 harness（FR-2）。

用法: python run_net_forward_ffi.py <manifest> <out_json> [--limit N] [--names a,b]
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback

from net_harness_common import (
    load_manifest,
    to_container_path,
    make_input,
    tensor_stats,
    first_conv_weight_stats,
    save_raw,
)

import caffe_ffi
from caffe_ffi import read_net


def run_model(entry: dict, out_json: str) -> dict:
    result = {"name": entry["name"], "status": "ok", "detail": {}}
    try:
        prototxt = to_container_path(entry["prototxt"])
        caffemodel = to_container_path(entry["caffemodel"])
        input_name = entry["input_name"]
        input_shape = entry["input_shape"]

        net = read_net(prototxt, caffemodel)
        result["detail"]["net_name"] = net.name
        result["detail"]["num_layers"] = len(net.layers_array())
        result["detail"]["layer_names"] = net.layer_names()
        result["detail"]["output_names"] = net.output_blob_names()

        # weight loading status (A-001 evidence)
        result["detail"]["first_conv_weight"] = first_conv_weight_stats(net.layers_array())

        # set input
        data = make_input(input_shape)
        try:
            blob = net.blob_by_name(input_name)
            blob.data = data
            input_ok = True
        except Exception as e:
            result["detail"]["input_set_error"] = f"{type(e).__name__}: {e}"
            input_ok = False

        # forward
        out = net.forward()
        if out:
            stats = {}
            for name, arr in out.items():
                stats[name] = tensor_stats(arr)
            result["detail"]["outputs"] = stats
            result["detail"]["outputs_saved"] = True
            save_raw("caffe_ffi", out_json, entry["name"], out)
        else:
            result["detail"]["outputs"] = {}
            result["detail"]["outputs_saved"] = False
        result["detail"]["input_ok"] = input_ok
    except Exception as e:
        result["status"] = "error"
        result["detail"]["error"] = f"{type(e).__name__}: {e}"
        result["detail"]["traceback"] = traceback.format_exc(limit=3)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("out")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--names", default="")
    args = ap.parse_args()

    models = load_manifest(args.manifest)
    if args.names:
        wanted = set(args.names.split(","))
        models = [m for m in models if m["name"] in wanted]
    if args.limit:
        models = models[: args.limit]

    results = []
    for i, m in enumerate(models):
        try:
            r = run_model(m, args.out)
        except Exception as e:
            r = {"name": m["name"], "status": "error", "detail": {"error": f"{type(e).__name__}: {e}"}}
        results.append(r)
        print(f"[{i+1}/{len(models)}] {m['name']}: {r['status']}", flush=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(
            {
                "impl": "caffe_ffi",
                "caffe_ffi_version": getattr(caffe_ffi, "__version__", "?"),
                "results": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"written: {args.out}")


if __name__ == "__main__":
    main()