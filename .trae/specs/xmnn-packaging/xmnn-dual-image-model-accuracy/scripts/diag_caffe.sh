#!/usr/bin/env bash
# Diagnose caffe_demo accuracy float-reference build failure.
# Usage: bash diag_caffe.sh <TAG>
set -euo pipefail
cd /workspace/models/debug
export TAG="${1:?usage: diag_caffe.sh <TAG>}"
python - <<'PY'
import os, time, traceback
from xmnn.compile_api import from_frontend, split_model
from xmnn.config import set_config

tag = os.environ.get("TAG", "whl")
model = "caffe_demo"
temp_dir = f"{model}/temp/{tag}"

print("=== 1. load config + from_frontend (caffe) ===", flush=True)
config = set_config(model, src_model_group_dir="./", temp_dir=temp_dir, config_path="config.toml")
mod, params = from_frontend(config, "tvm")
print("frontend OK", flush=True)

print("=== 2. split_model ===", flush=True)
run_mod, run_params, watch_ops, ops_table, input_ids = split_model(mod, params, config)
print(f"split OK: watch_ops={len(watch_ops)} input_ids={len(input_ids)}", flush=True)

print("=== 3. try vm.compile llvm (accuracy path) ===", flush=True)
try:
    import tvm
    exe = tvm.relay.backend.vm.compile(run_mod, target=tvm.target.Target("llvm"))
    print("VM_COMPILE_OK", flush=True)
except Exception as e:
    print("VM_COMPILE_FAIL:", type(e).__name__, flush=True)
    traceback.print_exc(limit=3)

print("=== 4. try graph build llvm (alt) ===", flush=True)
try:
    import tvm
    with tvm.transform.PassContext(opt_level=3):
        lib = tvm.relay.build(run_mod, target="llvm", params=run_params)
    print("GRAPH_BUILD_OK", flush=True)
except Exception as e:
    print("GRAPH_BUILD_FAIL:", type(e).__name__, flush=True)
    traceback.print_exc(limit=3)
PY
