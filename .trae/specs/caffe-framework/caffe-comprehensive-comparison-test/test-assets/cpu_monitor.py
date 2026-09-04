#!/usr/bin/env python3
"""CPU 占用率测量脚本（跨 caffe-ffi / caffex 容器通用，不依赖 psutil）。

通过 /proc/<pid>/stat 与 /proc/stat 计算子进程(Benchmark)的 CPU 占用率。
用法:
    python cpu_monitor.py <bench_script> <out_json> <iters>
    例: python cpu_monitor.py /SpecWeave/.../benchmark_ops.py /tmp/cpu_ffi.json 30
"""
import json
import os
import subprocess
import sys
import time


def _read(path):
    with open(path, "r") as f:
        return f.read()


def _proc_cpu(pid):
    """返回进程累计 utime+stime (jiffies)。"""
    stat = _read(f"/proc/{pid}/stat")
    idx = stat.rfind(")")
    rest = stat[idx + 2:].split()
    return int(rest[12]) + int(rest[13])  # utime(field14) + stime(field15)


def _host_cpu():
    for ln in _read("/proc/stat").splitlines():
        if ln.startswith("cpu "):
            return sum(int(t) for t in ln.split()[1:])
    return 0


def sample_subprocess(proc, duration, interval=0.1):
    """对运行中的子进程采样 duration 秒，返回 (avg, peak, min) CPU 占用率(%)。"""
    pid = proc.pid
    samples = []
    t_end = time.time() + duration
    while time.time() < t_end:
        if proc.poll() is not None:
            break
        try:
            p0 = _proc_cpu(pid)
            h0 = _host_cpu()
            time.sleep(interval)
            p1 = _proc_cpu(pid)
            h1 = _host_cpu()
            p_delta = p1 - p0
            h_delta = h1 - h0
            if h_delta > 0:
                ncpu = os.cpu_count() or 1
                samples.append((p_delta / h_delta) * 100.0 * ncpu)
        except (FileNotFoundError, ProcessLookupError):
            break
    if not samples:
        return 0.0, 0.0, 0.0
    return sum(samples) / len(samples), max(samples), min(samples)


def main():
    if len(sys.argv) < 3:
        print("usage: python cpu_monitor.py <bench_script> <out_json> [iters]")
        sys.exit(1)
    bench_script = sys.argv[1]
    out_json = sys.argv[2]
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    # 基准脚本产物写到临时文件
    tmp_out = f"/tmp/_cpu_bench_{os.getpid()}.json"
    cmd = [sys.executable, bench_script, tmp_out, str(iters)]

    # 预热（短迭代）
    subprocess.run(cmd[:-1] + [str(1)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 重复运行基准直到达到最小采样时长，保证采样可靠
    t0 = time.time()
    min_duration = min(15.0, max(5.0, 0.20 * iters))
    samples = []
    while time.time() - t0 < min_duration:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        seg_avg, seg_peak, seg_low = sample_subprocess(proc, min_duration - (time.time() - t0) + 1.0)
        proc.wait()
        if seg_avg > 0:
            samples.append((seg_avg, seg_peak, seg_low))
    elapsed = time.time() - t0
    if samples:
        avg = sum(s[0] for s in samples) / len(samples)
        peak = max(s[1] for s in samples)
        low = min(s[2] for s in samples)
    else:
        avg = peak = low = 0.0

    # 读取基准结果得到算子数
    n_ops = 0
    try:
        with open(tmp_out) as f:
            n_ops = len(json.load(f).get("ops", {}))
    except Exception:
        pass

    result = {
        "env": "caffe_ffi" if "ffi" in out_json.lower() else ("caffex" if "cx" in out_json.lower() or "caffex" in out_json.lower() else "unknown"),
        "ncpu": os.cpu_count(),
        "n_ops": n_ops,
        "iters": iters,
        "wall_s": round(elapsed, 2),
        "avg_cpu_pct": round(avg, 2),
        "peak_cpu_pct": round(peak, 2),
        "min_cpu_pct": round(low, 2),
        "sampling": "linux /proc",
    }
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()