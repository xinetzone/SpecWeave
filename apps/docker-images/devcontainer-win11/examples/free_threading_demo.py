#!/usr/bin/env python
"""
Python Free-Threading (cp314t) Demo for DevContainer Win11
Demonstrates GIL-free multi-threading performance on Windows.

Run inside container:
    python examples/free_threading_demo.py

Or with explicit GIL control:
    $env:Py_GIL_DISABLED=1; python examples/free_threading_demo.py
"""

import sys
import sysconfig
import time
import threading
import os


def check_gil_state():
    """Check and report free-threading status"""
    print("=" * 60)
    print("Python Free-Threading Demo (cp314t)")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()

    ft_build = sysconfig.get_config_var('Py_GIL_DISABLED')
    soabi = sysconfig.get_config_var('SOABI') or ''
    print(f"Build config:")
    print(f"  Py_GIL_DISABLED (build flag): {ft_build}")
    print(f"  SOABI: {soabi}")
    print(f"  Free-threading build: {'YES (cp314t)' if ft_build == 1 and 't' in soabi else 'NO (standard GIL)'}")
    print()

    try:
        gil_enabled = sys._is_gil_enabled()
        print(f"Runtime GIL status:")
        print(f"  sys._is_gil_enabled(): {gil_enabled}")
        print(f"  GIL currently {'ENABLED' if gil_enabled else 'DISABLED'}")
    except AttributeError:
        print("  sys._is_gil_enabled() not available (Python < 3.13 or not free-threading build)")
        gil_enabled = True

    env_var = os.environ.get('Py_GIL_DISABLED', 'not set')
    print(f"  Py_GIL_DISABLED env var: {env_var}")
    print()

    return ft_build == 1, gil_enabled


def cpu_bound_work(n):
    """CPU-intensive prime counting (simulates computational work)"""
    count = 0
    for num in range(2, n):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count


def benchmark_single_thread(work_size=10000):
    """Single-threaded baseline"""
    start = time.time()
    result = cpu_bound_work(work_size)
    elapsed = time.time() - start
    return result, elapsed


def benchmark_multi_thread(num_threads=4, work_size=10000):
    """Multi-threaded benchmark (true parallelism if GIL disabled)"""
    results = [0] * num_threads
    threads = []

    def worker(idx):
        results[idx] = cpu_bound_work(work_size)

    start = time.time()
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=60)
        if t.is_alive():
            print(f"[WARN] Thread {t.name} did not finish within 60s timeout")

    elapsed = time.time() - start
    return sum(results), elapsed


def main():
    ft_build, gil_enabled = check_gil_state()

    print("=" * 60)
    print("Performance Benchmark: Single-thread vs Multi-thread")
    print("=" * 60)
    print()

    work_size = 8000
    num_threads = 4

    print(f"Workload: Count primes up to {work_size}")
    print(f"Threads: {num_threads}")
    print()

    # Warmup
    print("Warming up...", end=" ", flush=True)
    cpu_bound_work(1000)
    print("done")
    print()

    # Single thread
    st_result, st_time = benchmark_single_thread(work_size)
    print(f"Single-threaded: {st_time:.3f}s (found {st_result} primes)")

    # Multi thread
    mt_result, mt_time = benchmark_multi_thread(num_threads, work_size)
    print(f"Multi-threaded ({num_threads} threads): {mt_time:.3f}s (found {mt_result} primes)")
    print()

    speedup = st_time * num_threads / mt_time if mt_time > 0 else 0
    efficiency = st_time / mt_time if mt_time > 0 else 0

    print(f"Speedup analysis:")
    print(f"  Total work (seq): {st_time * num_threads:.3f}s")
    print(f"  Parallel time:    {mt_time:.3f}s")
    print(f"  Speedup:          {speedup:.2f}x (ideal: {num_threads}x)")
    print(f"  Efficiency:       {efficiency:.2f}x over single thread")
    print()

    if ft_build and not gil_enabled:
        if efficiency > 1.5:
            print("✓ Free-threading is working! Multi-threading shows real parallel speedup.")
        else:
            print("⚠ GIL disabled but speedup is modest (small workload or GIL re-enabled by C extensions)")
    else:
        print("⚠ Running with standard GIL - multi-threading is sequential (expected in non-ft builds)")
        print("  Note: Some C extensions may temporarily re-enable GIL for compatibility")

    print()
    print("=" * 60)
    print("Tips for free-threading on Windows:")
    print("  - Set Py_GIL_DISABLED=1 system-wide (already set in container)")
    print("  - C extensions compiled without GIL support will auto-re-enable GIL with warning")
    print("  - Use conda-forge packages for best free-threading compatibility")
    print("  - pip will compile from source with Py_GIL_DISABLED=1 when wheels unavailable")
    print("=" * 60)


if __name__ == "__main__":
    main()
