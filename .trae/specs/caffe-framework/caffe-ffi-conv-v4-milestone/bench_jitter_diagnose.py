#!/usr/bin/env python3
"""
InceptionV1 batch=16 Jitter Diagnosis Benchmark
Test OMP_SCHEDULE, OMP_WAIT_POLICY, and warmup/memory-preallocation strategies
to find the most stable configuration with minimal latency variance.
"""
import os, sys, time, subprocess, tempfile, re
import numpy as np

MODEL_PROTO = "/root/.caffe_test_data/models/inceptionv1.prototxt"
MODEL_CAFFEMODEL = "/root/.caffe_test_data/models/inceptionv1.caffemodel"
MODEL_MEAN = [104., 117., 123.]
BATCH_SIZE = 16
OMP_THREADS = 4
BLAS_THREADS = 1
TIMED_ITERS = 30

SCHEDULE_STRATEGIES = ["static", "dynamic", "dynamic,1", "guided"]
WAIT_POLICIES = ["PASSIVE", "ACTIVE"]
WARMUP_CONFIGS = [
    {"name": "standard_warmup5", "warmup_iters": 5, "prealloc": False},
    {"name": "memory_prealloc_warmup50", "warmup_iters": 50, "prealloc": True},
]


def _make_batch_prototxt(proto_path, batch):
    if batch == 1:
        return proto_path
    with open(proto_path, "r") as f:
        content = f.read()
    lines = content.split("\n")
    found_data = False
    dim_count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("input:") and "data" in stripped:
            found_data = True
            continue
        if found_data and stripped.startswith("input_dim:"):
            dim_count += 1
            if dim_count == 1:
                lines[i] = re.sub(r"input_dim:\s*\d+", f"input_dim: {batch}", line)
                break
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".prototxt", delete=False, dir="/tmp")
    tmp.write("\n".join(lines))
    tmp.close()
    return tmp.name


def run_bench_config(omp_schedule, omp_wait_policy, warmup_iters, memory_prealloc, timeout=900):
    actual_proto = _make_batch_prototxt(MODEL_PROTO, BATCH_SIZE)
    cleanup_proto = (actual_proto != MODEL_PROTO)
    model_arg = f'"{MODEL_CAFFEMODEL}"' if MODEL_CAFFEMODEL else "None"

    prealloc_code = ""
    if memory_prealloc:
        # 置于生成的子进程代码顶层（无缩进），与 f-string 中 {prealloc_code} 位置对齐
        prealloc_code = """
for _ in range(warmup):
    data = np.random.rand(batch, 3, 224, 224).astype(np.float32)
    data -= np.array(mean_vals, dtype=np.float32).reshape(1, 3, 1, 1)
    input_blob.data = data
    net.forward()
"""
    else:
        prealloc_code = """
data = np.random.rand(batch, 3, 224, 224).astype(np.float32)
data -= np.array(mean_vals, dtype=np.float32).reshape(1, 3, 1, 1)
input_blob.data = data
for _ in range(warmup):
    net.forward()
"""

    code = f'''
import os, time
os.environ["OMP_NUM_THREADS"] = "{OMP_THREADS}"
os.environ["OPENBLAS_NUM_THREADS"] = "{BLAS_THREADS}"
os.environ["OMP_WAIT_POLICY"] = "{omp_wait_policy}"
os.environ["OMP_SCHEDULE"] = "{omp_schedule}"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"
import numpy as np, caffe_ffi

proto = "{actual_proto}"
model_path = {model_arg}
mean_vals = {MODEL_MEAN}
batch = {BATCH_SIZE}
warmup = {warmup_iters}
iters = {TIMED_ITERS}

np.random.seed(42)
net = caffe_ffi.read_net(proto, model_path)
input_blob = net.blob_by_name("data")
{prealloc_code}

lats = []
for _ in range(iters):
    t0 = time.perf_counter()
    net.forward()
    lats.append((time.perf_counter() - t0) * 1000)

lats = np.array(lats)
avg = np.mean(lats)
med = np.median(lats)
mn = np.min(lats)
mx = np.max(lats)
std = np.std(lats)
p50 = np.percentile(lats, 50)
p95 = np.percentile(lats, 95)
p99 = np.percentile(lats, 99)
ps = avg / batch
fps = 1000.0 * batch / avg
cv = std / avg * 100
tail_ratio = p99 / p50

print(f"RESULT avg={{avg:.2f}} p50={{p50:.2f}} p95={{p95:.2f}} p99={{p99:.2f}} "
      f"min={{mn:.2f}} max={{mx:.2f}} std={{std:.2f}} cv={{cv:.2f}} "
      f"tail={{tail_ratio:.3f}} ps={{ps:.2f}} fps={{fps:.2f}}")
'''
    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=timeout, cwd="/root"
        )
    except subprocess.TimeoutExpired:
        if cleanup_proto and os.path.exists(actual_proto):
            os.unlink(actual_proto)
        return {"error": "timeout"}

    if cleanup_proto and os.path.exists(actual_proto):
        os.unlink(actual_proto)

    for line in r.stdout.split("\n"):
        if line.startswith("RESULT "):
            parts = {}
            for tok in line[7:].split():
                k, v = tok.split("=")
                try:
                    parts[k] = float(v)
                except:
                    parts[k] = v
            return parts

    err_lines = [l for l in r.stderr.split("\n") if "Error" in l or "Traceback" in l]
    if err_lines:
        return {"error": err_lines[-1][:300]}
    if r.returncode != 0:
        stderr_tail = "\n".join(r.stderr.split("\n")[-8:])
        return {"error": f"exit {r.returncode}: {stderr_tail[:300]}"}
    return {"error": "no RESULT line"}


def generate_configs():
    configs = []
    for sched in SCHEDULE_STRATEGIES:
        for wait in WAIT_POLICIES:
            for wcfg in WARMUP_CONFIGS:
                configs.append({
                    "schedule": sched,
                    "wait_policy": wait,
                    "warmup_name": wcfg["name"],
                    "warmup_iters": wcfg["warmup_iters"],
                    "memory_prealloc": wcfg["prealloc"],
                })
    return configs


def print_markdown_table(results, baseline_idx):
    print("| # | OMP_SCHEDULE | OMP_WAIT_POLICY | Warmup Strategy | Avg(ms) | P50(ms) | P95(ms) | P99(ms) | Min(ms) | Max(ms) | Std(ms) | CV% | Tail(P99/P50) | FPS | vs Baseline |")
    print("|---|-------------|----------------|-----------------|---------|---------|---------|---------|---------|---------|---------|-----|---------------|-----|-------------|")
    baseline = results[baseline_idx] if baseline_idx < len(results) else None
    for i, r in enumerate(results):
        if "error" in r:
            print(f"| {i+1} | {r['schedule']} | {r['wait_policy']} | {r['warmup_name']} | - | - | - | - | - | - | - | FAIL: {r['error'][:40]} | - | - | - |")
            continue
        cv_improve = ""
        if baseline and "cv" in baseline and "cv" in r:
            cv_improve = f"{(baseline['cv'] - r['cv'])/baseline['cv']*100:+.1f}% CV"
        print(f"| {i+1} | `{r['schedule']}` | {r['wait_policy']} | {r['warmup_name']} | "
              f"{r['avg']:.1f} | {r['p50']:.1f} | {r['p95']:.1f} | {r['p99']:.1f} | "
              f"{r['min']:.1f} | {r['max']:.1f} | {r['std']:.1f} | "
              f"**{r['cv']:.1f}%** | {r['tail']:.2f}x | {r['fps']:.1f} | {cv_improve} |")


def diagnose(results):
    valid = [r for r in results if "error" not in r]
    if not valid:
        print("\n❌ No valid results to diagnose!")
        return

    baseline = None
    for r in valid:
        if r["schedule"] == "static" and r["wait_policy"] == "PASSIVE" and r["warmup_name"] == "standard_warmup5":
            baseline = r
            break

    sorted_by_cv = sorted(valid, key=lambda x: x["cv"])
    best = sorted_by_cv[0]

    print("\n" + "="*100)
    print("  DIAGNOSIS CONCLUSION")
    print("="*100)

    print(f"\n📊 Baseline config (static, PASSIVE, warmup=5):")
    if baseline:
        print(f"   Avg={baseline['avg']:.1f}ms  P50={baseline['p50']:.1f}ms  P99={baseline['p99']:.1f}ms  "
              f"CV={baseline['cv']:.1f}%  Tail={baseline['tail']:.2f}x  FPS={baseline['fps']:.1f}")
    else:
        print("   ⚠ Baseline config not found in results!")

    print(f"\n🏆 Best config (sorted by CV% ascending):")
    print(f"   Schedule={best['schedule']}  Wait={best['wait_policy']}  Warmup={best['warmup_name']}")
    print(f"   Avg={best['avg']:.1f}ms  P50={best['p50']:.1f}ms  P99={best['p99']:.1f}ms  "
          f"CV={best['cv']:.1f}%  Tail={best['tail']:.2f}x  FPS={best['fps']:.1f}")

    if baseline:
        cv_reduction = (baseline['cv'] - best['cv']) / baseline['cv'] * 100
        tail_reduction = (baseline['tail'] - best['tail']) / baseline['tail'] * 100
        fps_change = (best['fps'] - baseline['fps']) / baseline['fps'] * 100
        print(f"\n📈 Improvement over baseline:")
        print(f"   CV reduction:        {cv_reduction:+.1f}% ({baseline['cv']:.1f}% → {best['cv']:.1f}%)")
        print(f"   Tail ratio reduction:{tail_reduction:+.1f}% ({baseline['tail']:.2f}x → {best['tail']:.2f}x)")
        print(f"   FPS change:          {fps_change:+.1f}% ({baseline['fps']:.1f} → {best['fps']:.1f})")

    print(f"\n📋 Top 5 most stable configs:")
    for i, r in enumerate(sorted_by_cv[:5]):
        print(f"   {i+1}. CV={r['cv']:5.1f}%  Tail={r['tail']:.2f}x  FPS={r['fps']:5.1f}  "
              f"| sched={r['schedule']:10s} wait={r['wait_policy']:7s} warmup={r['warmup_name']}")

    target_cv = 15.0
    if best["cv"] < target_cv:
        print(f"\n✅ TARGET ACHIEVED: CV% ({best['cv']:.1f}%) is below {target_cv}% threshold.")
        print(f"   Recommendation: Use the best config above for production deployment.")
    else:
        print(f"\n⚠️  TARGET NOT MET: Best CV% ({best['cv']:.1f}%) is still above {target_cv}% threshold.")
        print(f"\n🔍 Root Cause Analysis:")
        print(f"   Even after testing all 16 combinations of OMP_SCHEDULE, OMP_WAIT_POLICY,")
        print(f"   and aggressive memory preallocation warmup, CV% remains >15%.")
        print(f"")
        print(f"   Likely root causes:")
        print(f"   1. OS scheduling jitter: Thread migration between P-cores and E-cores")
        print(f"      (Core Ultra 9 285H has mixed P-core/E-core architecture)")
        print(f"   2. CPU frequency scaling: Turbo boost ramp-up/down between iterations")
        print(f"   3. Cache/TLB misses: Despite warmup, different memory access patterns")
        print(f"      in InceptionV1's multi-branch structure may still cause occasional misses")
        print(f"   4. OpenMP runtime overhead: Barrier synchronization across 4 threads in")
        print(f"      ~50+ small convolution layers creates inherent variability")
        print(f"")
        print(f"💡 Recommendation for 4-thread usage:")
        if best["cv"] < 25:
            print(f"   CV={best['cv']:.1f}% is in 'Fair' range. 4 threads can be used for")
            print(f"   throughput-oriented batch=16 inference if some jitter is acceptable.")
            print(f"   For latency-critical scenarios, consider using 1 or 2 threads.")
        else:
            print(f"   CV={best['cv']:.1f}% is in 'Unstable' range. 4-thread batch=16 is NOT")
            print(f"   recommended for production. Use 1 thread (batch=1) for predictable latency,")
            print(f"   or consider model compilation (TensorRT/ONNX Runtime) for better stability.")

    print(f"\n💡 Additional recommendations:")
    print(f"   - Try setting OMP_PROC_BIND=CLOSE or OMP_PLACES=cores to reduce thread migration")
    print(f"   - Lock CPU frequency (disable turbo boost) for more consistent performance")
    print(f"   - Consider using numactl or taskset for CPU affinity binding on Linux")
    print(f"   - For batch=16 throughput, also test batch=32 to see if larger batch amortizes overhead")


def main():
    print("="*100)
    print("  InceptionV1 batch=16 Jitter Diagnosis")
    print(f"  OMP_NUM_THREADS={OMP_THREADS}, OPENBLAS_NUM_THREADS={BLAS_THREADS}, iters={TIMED_ITERS}")
    print("="*100)

    configs = generate_configs()
    print(f"\n📋 Total configurations to test: {len(configs)}")
    print(f"   Schedule strategies: {len(SCHEDULE_STRATEGIES)} ({', '.join(SCHEDULE_STRATEGIES)})")
    print(f"   Wait policies:       {len(WAIT_POLICIES)} ({', '.join(WAIT_POLICIES)})")
    print(f"   Warmup strategies:   {len(WARMUP_CONFIGS)} ({', '.join(w['name'] for w in WARMUP_CONFIGS)})")
    print()

    results = []
    baseline_idx = None
    for i, cfg in enumerate(configs):
        if (cfg["schedule"] == "static" and cfg["wait_policy"] == "PASSIVE" and
            cfg["warmup_name"] == "standard_warmup5"):
            baseline_idx = i
        print(f"[{i+1:2d}/{len(configs)}] Testing: schedule={cfg['schedule']:10s} "
              f"wait={cfg['wait_policy']:7s} warmup={cfg['warmup_name']:25s} ... ", end="", flush=True)
        t0 = time.time()
        r = run_bench_config(
            cfg["schedule"], cfg["wait_policy"],
            cfg["warmup_iters"], cfg["memory_prealloc"]
        )
        elapsed = time.time() - t0
        if "error" in r:
            print(f"FAIL ({elapsed:.0f}s): {r['error'][:60]}")
        else:
            print(f"OK  CV={r['cv']:5.1f}%  Avg={r['avg']:6.1f}ms  FPS={r['fps']:5.1f}  ({elapsed:.0f}s)")
        r.update(cfg)
        results.append(r)

    print("\n" + "="*100)
    print("  RESULTS IN MARKDOWN TABLE")
    print("="*100)
    print()
    print_markdown_table(results, baseline_idx)

    diagnose(results)

    print("\n" + "="*100)
    print("  TEST COMPLETE")
    print("="*100)


if __name__ == "__main__":
    main()
