#!/usr/bin/env python3
"""
A-005 推进（强化版）：真实权重 vs 随机权重 延迟对比（基于中位数，降低抖动噪声）

用更多迭代次数（60次）+ 中位数(P50)作为主指标，排除 OMP=4 抖动假象。
对照模型：ResNet-50（同一网络，仅权重来源不同）。
若 P50 差异 <5% 且各线程数下的最优点一致，则证明 OpenMP 延迟结论由 GEMM 形状
决定而非权重数值，A-005 关注点收敛。
"""
import os, subprocess, numpy as np

BASE = "/root/.caffe_test_data/models/"
PY = "/opt/conda/envs/caffe-ffi/bin/python"

def run_one(proto, model_path, omp_t, blas_t=1, warmup=10, iters=60, timeout=600):
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
    t0 = time.perf_counter(); net.forward(); lats.append((time.perf_counter()-t0)*1000)
lats = np.array(lats)
cv = np.std(lats)/np.mean(lats)*100
print(f"RESULT avg={{np.mean(lats):.2f}} med={{np.median(lats):.2f}} p95={{np.percentile(lats,95):.2f}} p99={{np.percentile(lats,99):.2f}} cv={{cv:.2f}}")
'''
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=timeout, cwd="/root")
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

    print("=" * 92)
    print("A-005 强化实验: ResNet-50 REAL vs RAND (batch=1, warmup=10, iters=60, 中位数主指标)")
    print("=" * 92)
    print(f"{'Thr':>4} {'Mode':>5} {'Avg(ms)':>9} {'P50(ms)':>8} {'P95(ms)':>8} {'P99(ms)':>8} {'CV%':>6}")
    print("-" * 92)

    results = {}
    for t in threads:
        for mode, mp in [("REAL", real_w), ("RAND", random_w)]:
            r = run_one(proto, mp, t)
            if "error" in r:
                print(f"{t:4d} {mode:>5}   FAIL: {r['error'][:60]}")
                results[(t, mode)] = None
            else:
                results[(t, mode)] = r
                print(f"{t:4d} {mode:>5} {r['avg']:9.2f} {r['med']:8.2f} {r['p95']:8.2f} {r['p99']:8.2f} {r['cv']:6.2f}%")

    print("-" * 92)
    print("P50(中位数) 差异分析 |REAL-RAND|/REAL:")
    print(f"{'Thr':>4} {'AvgΔ%':>8} {'P50Δ%':>8} {'P95Δ%':>8} {'P99Δ%':>8}")
    deltas = {}
    for t in threads:
        re_ = results.get((t, "REAL")); ra = results.get((t, "RAND"))
        if re_ and ra and "error" not in re_ and "error" not in ra:
            d = {k: abs(re_[k]-ra[k])/re_[k]*100 for k in ["avg","med","p95","p99"]}
            deltas[t] = d
            print(f"{t:4d} {d['avg']:8.2f} {d['med']:8.2f} {d['p95']:8.2f} {d['p99']:8.2f}")

    print()
    # 最优线程判定一致性
    def best_thread(which):
        cand = {t: results[(t, which)]["med"] for t in threads
                if results.get((t, which)) and "error" not in results[(t, which)]}
        return min(cand, key=cand.get), cand
    b_real, d_real = best_thread("REAL")
    b_rand, d_rand = best_thread("RAND")
    print(f"REAL 最优线程: OMP={b_real} (P50={d_real[b_real]:.2f}ms)")
    print(f"RAND 最优线程: OMP={b_rand} (P50={d_rand[b_rand]:.2f}ms)")
    print(f"最优线程一致: {'是' if b_real==b_rand else '否'}")

    # 结论
    p50_deltas = [deltas[t]["med"] for t in threads if t in deltas]
    max_p50_delta = max(p50_deltas)
    verdict = ("A-005 关注点收敛：真实权重与随机权重的 P50 延迟差异 <5%，且最优线程数一致。"
               "OpenMP 延迟由 GEMM 形状决定，ResNet-101 随机权重数据对线程数标定有效，"
               "无需强制获取真实 ResNet-101 caffemodel。" if max_p50_delta < 5 and b_real == b_rand
               else "差异或最优线程不一致，需获取真实 ResNet-101 caffemodel 复核。")
    print(f"\n最大 P50 差异: {max_p50_delta:.2f}%")
    print("结论:", verdict)


if __name__ == "__main__":
    main()