"""caffex 全模型网络级前向 harness（FR-3）。

用法: python run_net_forward_caffex.py <manifest> <out_json> [--limit N] [--names a,b]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
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

import caffe


def run_model(entry: dict, out_json: str) -> dict:
    result = {"name": entry["name"], "status": "ok", "detail": {}}
    try:
        prototxt = to_container_path(entry["prototxt"])
        caffemodel = to_container_path(entry["caffemodel"])
        input_name = entry["input_name"]
        input_shape = entry["input_shape"]

        net = caffe.Net(prototxt, caffemodel, caffe.TEST)
        result["detail"]["num_layers"] = len(net.layers)
        result["detail"]["layer_names"] = list(net._layer_names)
        result["detail"]["output_names"] = list(net.outputs)
        result["detail"]["input_names"] = list(net.inputs)

        # weight loading status (A-001 evidence): first conv layer with params
        result["detail"]["first_conv_weight"] = first_conv_weight_stats(net.layers)

        # set input via net.blobs
        data = make_input(input_shape)
        try:
            net.blobs[input_name].data[...] = data
            input_ok = True
        except Exception as e:
            result["detail"]["input_set_error"] = f"{type(e).__name__}: {e}"
            input_ok = False

        out = net.forward()
        stats = {}
        for name in net.outputs:
            arr = net.blobs[name].data
            stats[name] = tensor_stats(arr)
        result["detail"]["outputs"] = stats
        result["detail"]["outputs_saved"] = True
        save_raw("caffex", out_json, entry["name"], {name: net.blobs[name].data for name in net.outputs})
        result["detail"]["input_ok"] = input_ok
    except Exception as e:
        result["status"] = "error"
        result["detail"]["error"] = f"{type(e).__name__}: {e}"
        result["detail"]["traceback"] = traceback.format_exc(limit=3)
    return result


def run_model_subprocess(entry: dict, out_json: str) -> dict:
    """Run one model in a fresh subprocess so a native crash (SIGABRT) doesn't
    kill the whole run. Returns the model result dict, or a crash record."""
    manifest_str = json.dumps(entry)
    code = (
        "import json,sys;"
        "from run_net_forward_caffex import run_model;"
        "e=json.loads(sys.argv[1]); o=sys.argv[2];"
        "json.dump(run_model(e, o), sys.stdout)"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code, manifest_str, out_json],
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return {"name": entry["name"], "status": "timeout", "detail": {"error": "timeout>600s"}}
    if proc.returncode == 0 and proc.stdout.strip():
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return {"name": entry["name"], "status": "error", "detail": {"error": "bad stdout", "stdout": proc.stdout[-500:]}}
    return {
        "name": entry["name"],
        "status": "crash",
        "detail": {"error": f"exit={proc.returncode}", "stderr": proc.stderr[-800:]},
    }


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
        r = run_model_subprocess(m, args.out)
        results.append(r)
        print(f"[{i+1}/{len(models)}] {m['name']}: {r['status']}", flush=True)
        # Persist incrementally so a later crash doesn't lose prior results.
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "impl": "caffex",
                    "caffe_version": "1.0.0",
                    "results": results,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
    print(f"written: {args.out}")


if __name__ == "__main__":
    main()