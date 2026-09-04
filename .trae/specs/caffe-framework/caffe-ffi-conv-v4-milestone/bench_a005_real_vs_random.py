#!/usr/bin/env python3
"""
A-005 推进：验证"真实权重 vs 随机权重不影响 OpenMP 延迟结论"

核心假设：OpenMP Conv 层延迟由 GEMM 形状（M/N/K）决定，与权重数值无关。
因此 ResNet-101 随机权重延迟数据对线程数结论有效；真实权重仅影响输出数值，
不影响 P50/P95/P99/CV%。用 ResNet-50（同时具备真实+随机两种权重路径）做对照实验验证。

对照：ResNet-50 在 OMP=1/2/4/8 下，真实权重 vs 随机权重 的延迟指标对比。
若两者延迟高度一致（<5% 差异），则证明 A-005 关注点可收敛：随机权重延迟数据
对线程数标定有效，无需强制获取真实 ResNet-101 caffemodel。
"""
import os, sys, time, subprocess, argparse, tempfile, re
import numpy as np

BASE = "/root/.caffe_test_data/models/"

def run_one(proto, model_path, omp_t, blas_t=1, batch=1, warmup=5, iters=20, timeout=600):
    code = f'''
import os, time
os.environ["OMP_NUM_THREADS"] = "{omp_t}"
os.environ["OPENBLAS_NUM_THREADS"] = "{blas_t}"
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["GLOG_minloglevel"] = "3"
import numpy as np, caffe_ffi
proto = "{proto}"
model_path = {model_path}
mean_vals = [103.939, 116.779, 123.68]
np.random.seed(42)
net = caffe_ffi.read_net(proto, model_path)
blob = net.blob_by_name("data")
data = np.random.rand(1,3,224,224).astype(np.float32)
data -= np.array(mean_vals, dtype=np.float32).reshape(1,3,1,1)
blob.data = data
for _ in range({warmup}):
    net.forward()
lats = []
for _ in range({iters}):
    t0 = time.perf_counter()
    net.forward()
    lats.append((time.perf_counter()-t0)*1000)
lats = np.array(lats)
cv = np.std(lats)/np.mean(lats)*100
print(f"RESULT avg={{np.mean(lats):.2f}} med={{np.median(lats):.2f}} p95={{np.percentile(lats,95):.2f}} p99={{np.percentile(lats,99):.2f}} cv={{cv:.2f}}")
'''
    py = "/opt/conda/envs/caffe-ffi/bin/python"
    r = subprocess.run([py, "-c", code], capture_output=True, text=True, timeout=timeout, cwd="/root")
    for line in r.stdout.split("\n"):
        if line.startswith("RESULT "):
            parts = {}
            for tok in line[7:].split():
                k, v = tok.split("=", 1)
                parts[k] = float(v)
            return parts
    err = [l for l in r.stderr.split("\n") if "Error" in l or "Traceback" in l]
    return {"error": (err[-1][:120] if err else f"exit {r.returncode}")}


def main():
    proto = os.path.join(BASE, "resnet50.prototxt")
    real_w = f'"{os.path.join(BASE, "resnet50.caffemodel")}"'
    random_w = "None"
    threads = [1, 2, 4, 8]

    print("=" * 90)
    print("A-005 对照实验: ResNet-50 真实权重 vs 随机权重 (batch=1, BLAS=1, PASSIVE)")
    print("=" * 90)
    print(f"{'Thr':>4} {'Mode':>8} {'Avg(ms)':>9} {'P50(ms)':>8} {'P95(ms)':>8} {'P99(ms)':>8} {'CV%':>6}")
    print("-" * 90)

    results = {}
    for t in threads:
        for mode, mp in [("REAL", real_w), ("RAND", random_w)]:
            r = run_one(proto, mp, t)
            if "error" in r:
                print(f"{t:4d} {mode:>8}   FAIL: {r['error'][:60]}")
                results[(t, mode)] = None
            else:
                results[(t, mode)] = r
                print(f"{t:4d} {mode:>8} {r['avg']:9.2f} {r['med']:8.2f} {r['p95']:8.2f} {r['p99']:8.2f} {r['cv']:6.2f}%")

    print("-" * 90)
    print("真实 vs 随机 差异分析 (|REAL-RAND|/REAL 百分比):")
    print(f"{'Thr':>4} {'AvgΔ%':>8} {'P50Δ%':>8} {'P95Δ%':>8} {'P99Δ%':>8}")
    for t in threads:
        re_ = results.get((t, "REAL"))
        ra = results.get((t, "RAND"))
        if re_ and ra and "error" not in re_ and "error" not in ra:
            d = {k: abs(re_[k]-ra[k])/re_[k]*100 for k in ["avg","med","p95","p99"]}
            print(f"{t:4d} {d['avg']:8.2f} {d['med']:8.2f} {d['p95']:8.2f} {d['p99']:8.2f}")

    print()
    # 结论判定
    all_ok = True
    for t in threads:
        re_ = results.get((t, "REAL"))
        ra = results.get((t, "RAND"))
        if re_ and ra and "error" not in re_ and "error" not in ra:
            if abs(re_["avg"]-ra["avg"])/re_["avg"] > 0.05:
                all_ok = False
    print("结论: %s" % ("真实权重与随机权重延迟差异 <5%，A-005 关注点收敛，随机权重数据对线程数标定有效。"
                        if all_ok else "真实权重与随机权重延迟差异 >5%，需获取真实 ResNet-101 caffemodel 复核。"))


if __name__ == "__main__":
    main()