"""逐模型性能与资源占用基准（Task 7 / FR-6）。

增量保存 + caffex 子进程隔离（防原生崩溃连锁）。
为抑制 OpenBLAS 警告与线程过订阅，建议运行前设置：
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4

用法:
  python bench_net_forward.py <impl> <manifest> <out_json> [--limit N] [--names a,b] [--repeats 3]
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
import sys
import time
import traceback
from pathlib import Path

from net_harness_common import load_manifest, to_container_path, make_input

NUM_REPEATS = 3


def _bench_one_in_proc(impl: str, entry: dict, repeats: int) -> dict:
    """Run a single model bench in the current process (for caffe_ffi)."""
    result = {"name": entry["name"], "status": "ok", "detail": {}}
    try:
        prototxt = to_container_path(entry["prototxt"])
        caffemodel = to_container_path(entry["caffemodel"])
        input_name = entry["input_name"]
        input_shape = entry["input_shape"]

        if impl == "caffe_ffi":
            from caffe_ffi import read_net

            net = read_net(prototxt, caffemodel)
        else:
            import caffe

            net = caffe.Net(prototxt, caffemodel, caffe.TEST)

        data = make_input(input_shape)
        if impl == "caffe_ffi":
            net.blob_by_name(input_name).data = data
        else:
            net.blobs[input_name].data[...] = data
        net.forward()  # warmup

        t0 = resource.getrusage(resource.RUSAGE_SELF)
        lat = []
        for _ in range(max(1, repeats)):
            if impl == "caffe_ffi":
                net.blob_by_name(input_name).data = data
            else:
                net.blobs[input_name].data[...] = data
            s = time.perf_counter()
            net.forward()
            lat.append((time.perf_counter() - s) * 1000.0)
        t1 = resource.getrusage(resource.RUSAGE_SELF)
        cpu_ms = (t1.ru_utime + t1.ru_stime) * 1000.0

        m = sum(lat) / len(lat)
        result["detail"]["latency_ms"] = {
            "mean": float(m),
            "std": float((sum((x - m) ** 2 for x in lat) / len(lat)) ** 0.5),
            "min": float(min(lat)),
            "max": float(max(lat)),
            "runs": len(lat),
        }
        result["detail"]["fps"] = float(1000.0 / m) if m > 0 else 0.0
        result["detail"]["cpu_ms"] = cpu_ms
    except Exception as e:  # noqa: BLE001
        result["status"] = "error"
        result["detail"]["error"] = f"{type(e).__name__}: {e}"
        result["detail"]["traceback"] = traceback.format_exc(limit=3)
    return result


def _bench_one_subprocess(impl: str, entry: dict, repeats: int, script_path: str) -> dict:
    """caffex: run in isolated subprocess to avoid native crashes."""
    manifest_str = json.dumps(entry)
    code = (
        "import json,sys;"
        "from bench_net_forward import _bench_one_in_proc;"
        "e=json.loads(sys.argv[1]); r=int(sys.argv[2]);"
        "json.dump(_bench_one_in_proc('" + impl + "', e, r), sys.stdout)"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code, manifest_str, str(repeats)],
            cwd=str(Path(script_path).parent),
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "GLOG_minloglevel": "2"},
        )
    except subprocess.TimeoutExpired:
        return {"name": entry["name"], "status": "timeout", "detail": {"error": "timeout 600s"}}
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().split("\n")[-3:]
        return {
            "name": entry["name"],
            "status": "crash",
            "detail": {
                "error": f"exit={proc.returncode} " + " | ".join(tail),
                "stdout_tail": (proc.stdout or "")[-500:],
                "stderr_tail": (proc.stderr or "")[-500:],
            },
        }
    try:
        return json.loads(proc.stdout)
    except Exception:  # noqa: BLE001
        return {
            "name": entry["name"],
            "status": "bad_json",
            "detail": {"stdout_tail": (proc.stdout or "")[-500:]},
        }


def _write_out(out_path: str, impl: str, repeats: int, results: list) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"impl": impl, "repeats": repeats, "results": results}, f, ensure_ascii=False, indent=2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("impl", choices=["caffe_ffi", "caffex"])
    ap.add_argument("manifest")
    ap.add_argument("out")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--names", default="")
    ap.add_argument("--repeats", type=int, default=NUM_REPEATS)
    args = ap.parse_args()

    models = load_manifest(args.manifest)
    if args.names:
        wanted = set(args.names.split(","))
        models = [m for m in models if m["name"] in wanted]
    if args.limit:
        models = models[: args.limit]

    results: list[dict] = []
    # resume if partial exists
    if Path(args.out).exists():
        try:
            prev = json.loads(Path(args.out).read_text(encoding="utf-8"))
            results = prev.get("results", [])
            done = {r["name"] for r in results}
            models = [m for m in models if m["name"] not in done]
            print(f"resumed: {len(results)} existing, {len(models)} remaining", flush=True)
        except Exception:  # noqa: BLE001
            results = []

    for i, m in enumerate(models):
        if args.impl == "caffex":
            r = _bench_one_subprocess(args.impl, m, args.repeats, __file__)
        else:
            r = _bench_one_in_proc(args.impl, m, args.repeats)
        results.append(r)
        _write_out(args.out, args.impl, args.repeats, results)
        lat = r["detail"].get("latency_ms", {})
        tag = f" mean={lat.get('mean', 0):.2f}ms fps={r['detail'].get('fps', 0):.2f}" if r["status"] == "ok" else ""
        print(f"[{len(results)}/{len(results)+len(models)-i-1}] {m['name']}: {r['status']}{tag}", flush=True)

    print(f"written: {args.out}")


if __name__ == "__main__":
    main()