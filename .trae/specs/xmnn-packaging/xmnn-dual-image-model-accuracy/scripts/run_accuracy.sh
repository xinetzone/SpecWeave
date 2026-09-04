#!/usr/bin/env bash
# Dual-image model accuracy runner.
# Usage: bash run_accuracy.sh <TAG>   where TAG in {whl, rt}
# Runs compile_xmnn + accuracy_xmnn for caffe_demo and palmDet.
# Outputs land under <model>/temp/<TAG>/<model>/{compile,accuracy}
set -euo pipefail

TAG="${1:?usage: run_accuracy.sh <TAG>}"
cd /workspace/models/debug

export TAG
python - <<'PY'
import os, sys, time
from xmnn.compile_api import compile_xmnn
from xmnn.accuracy_api import accuracy_xmnn

tag = os.environ.get("TAG", "whl")
models_env = os.environ.get("MODELS", "caffe_demo,palmDet")
models = [m.strip() for m in models_env.split(",") if m.strip()]

for m in models:
    temp_dir = f"{m}/temp/{tag}"
    print("=" * 70, flush=True)
    print(f"[{m}] COMPILE (tag={tag}) temp_dir={temp_dir}", flush=True)
    print("=" * 70, flush=True)
    t0 = time.perf_counter()
    compile_xmnn(m, src_model_group_dir="./", temp_dir=temp_dir, config_path="config.toml")
    print(f"[{m}] COMPILE elapsed={time.perf_counter()-t0:.2f}s", flush=True)

    print("=" * 70, flush=True)
    print(f"[{m}] ACCURACY (tag={tag})", flush=True)
    print("=" * 70, flush=True)
    t0 = time.perf_counter()
    accuracy_xmnn(m, src_model_group_dir="./", temp_dir=temp_dir, config_path="config.toml", compile_name="compile")
    print(f"[{m}] ACCURACY elapsed={time.perf_counter()-t0:.2f}s", flush=True)

print("RUN_ALL_DONE", flush=True)
PY
