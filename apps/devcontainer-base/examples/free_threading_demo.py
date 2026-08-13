#!/usr/bin/env python3
"""
Python 3.14 Free-Threading (无GIL) 并发性能演示脚本
==================================================

本脚本演示 Python 3.14 free-threading (PEP 703) 模式下多线程并发性能的提升。

在传统CPython中，GIL（全局解释器锁）使得CPU密集型多线程代码无法真正并行执行。
Python 3.14 的 free-threading 构建移除了GIL，使得多线程可以真正利用多核CPU。

使用方式（在 devcontainer-base:conda-libmamba-v2 容器中运行）:

  # 方式1: 默认模式（GIL启用）
  docker run --rm devcontainer-base:conda-libmamba-v2 \
    python examples/free_threading_demo.py

  # 方式2: 无GIL模式（free-threading，体验真正并行）
  docker run --rm -e PYTHON_GIL=0 devcontainer-base:conda-libmamba-v2 \
    python examples/free_threading_demo.py

  # 方式3: 限制CPU核心数对比
  docker run --rm --cpuset-cpus="0-3" -e PYTHON_GIL=0 \
    devcontainer-base:conda-libmamba-v2 python examples/free_threading_demo.py
"""

import sys
import os
import time
import math
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, List, Tuple

# ============================================================
# 环境检测
# ============================================================

def detect_environment() -> dict:
    """检测当前Python环境配置"""
    info = {
        "python_version": sys.version,
        "gil_enabled": None,
        "free_threading_build": False,
        "cpu_count": os.cpu_count() or 1,
    }
    
    # 检测 free-threading 支持
    if hasattr(sys, "_is_gil_enabled"):
        info["free_threading_build"] = True
        info["gil_enabled"] = sys._is_gil_enabled()
    elif hasattr(sys.flags, "nogil"):
        info["free_threading_build"] = True
        info["gil_enabled"] = not sys.flags.nogil
    
    # 环境变量检测
    info["pygil_env"] = os.environ.get("PYTHON_GIL", "1 (default)")
    
    return info


def print_header():
    """打印环境信息头部"""
    info = detect_environment()
    
    print("=" * 70)
    print("  Python 3.14 Free-Threading 并发性能演示")
    print("=" * 70)
    print()
    print(f"  Python 版本: {info['python_version'].split(chr(10))[0]}")
    print(f"  编译器: {info['python_version'].split('[')[-1].rstrip(']') if '[' in info['python_version'] else 'N/A'}")
    print(f"  CPU 核心数: {info['cpu_count']}")
    print()
    
    if info["free_threading_build"]:
        gil_status = "🔒 启用 (GIL active)" if info["gil_enabled"] else "🔓 禁用 (No-GIL / free-threading)"
        print(f"  GIL 状态: {gil_status}")
        print(f"  PYTHON_GIL 环境变量: {info['pygil_env']}")
        if info["gil_enabled"]:
            print()
            print("  💡 提示: 当前GIL已启用，多线程CPU密集任务无法真正并行。")
            print("     如需体验无GIL并行性能，请设置环境变量 PYTHON_GIL=0:")
            print("       docker run -e PYTHON_GIL=0 ... python examples/free_threading_demo.py")
    else:
        print("  ⚠️  当前Python不是free-threading构建版本，无法体验无GIL性能。")
        print("     请使用 devcontainer-base:conda-libmamba-v2 镜像运行本脚本。")
    
    print()
    print("-" * 70)
    print()


# ============================================================
# CPU密集型计算任务
# ============================================================

def is_prime(n: int) -> bool:
    """判断素数 - 纯Python CPU密集型计算"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def count_primes_in_range(start: int, end: int) -> int:
    """统计 [start, end) 范围内素数个数"""
    count = 0
    for n in range(start, end):
        if is_prime(n):
            count += 1
    return count


def compute_primes_worker(args: Tuple[int, int]) -> int:
    """多线程/多进程 worker（接收参数元组）"""
    return count_primes_in_range(*args)


def generate_ranges(total: int, num_workers: int) -> List[Tuple[int, int]]:
    """将范围 [0, total) 均分为 num_workers 段"""
    step = total // num_workers
    ranges = []
    for i in range(num_workers):
        start = i * step
        end = (i + 1) * step if i < num_workers - 1 else total
        ranges.append((start, end))
    return ranges


# ============================================================
# 性能基准测试
# ============================================================

def benchmark(label: str, func: Callable, *args, **kwargs) -> float:
    """测量函数执行时间"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return elapsed, result


def run_single_threaded(ranges: List[Tuple[int, int]]) -> Tuple[float, int]:
    """单线程顺序执行"""
    start = time.perf_counter()
    total = 0
    for r in ranges:
        total += count_primes_in_range(*r)
    elapsed = time.perf_counter() - start
    return elapsed, total


def run_multithreaded(ranges: List[Tuple[int, int]], num_threads: int) -> Tuple[float, int]:
    """多线程并行执行"""
    results = [0] * len(ranges)
    threads = []
    
    def worker(idx, r):
        results[idx] = count_primes_in_range(*r)
    
    start = time.perf_counter()
    for i, r in enumerate(ranges):
        t = threading.Thread(target=worker, args=(i, r))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join(timeout=300)
        if t.is_alive():
            raise TimeoutError(f"Thread {t.name} did not complete within 300s timeout")
    
    elapsed = time.perf_counter() - start
    return elapsed, sum(results)


def run_threadpool(ranges: List[Tuple[int, int]], num_workers: int) -> Tuple[float, int]:
    """使用 ThreadPoolExecutor 并行执行"""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(compute_primes_worker, ranges))
    elapsed = time.perf_counter() - start
    return elapsed, sum(results)


def run_multiprocess(ranges: List[Tuple[int, int]], num_workers: int) -> Tuple[float, int]:
    """多进程执行（对照组 - 绕过GIL的传统方案）"""
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(compute_primes_worker, ranges))
    elapsed = time.perf_counter() - start
    return elapsed, sum(results)


# ============================================================
# 主测试流程
# ============================================================

def print_result_row(name: str, elapsed: float, speedup: float, correct: bool):
    """打印一行结果"""
    status = "✅" if correct else "❌"
    print(f"  {status} {name:<25} {elapsed:>8.3f}s   {speedup:>6.2f}x 加速")


def main():
    print_header()
    
    # 检测环境
    info = detect_environment()
    num_cpus = info["cpu_count"]
    
    # 测试参数
    PRIME_RANGE_UPPER = 200_000      # 统计 0~200000 范围素数（纯Python计算）
    MAX_WORKERS = min(num_cpus, 8)   # 最多8个workers
    
    expected_primes = count_primes_in_range(0, PRIME_RANGE_UPPER)
    print(f"  测试任务: 统计 0~{PRIME_RANGE_UPPER:,} 范围内的素数个数")
    print(f"  正确答案: {expected_primes} 个素数")
    print(f"  并行度:   1 ~ {MAX_WORKERS} workers")
    print()
    
    # ----------------------------------------------------------
    # 基准: 单线程
    # ----------------------------------------------------------
    print("  【基准测试】单线程顺序执行")
    print("  " + "-" * 55)
    
    ranges = generate_ranges(PRIME_RANGE_UPPER, 1)
    t_single, result_single = run_single_threaded(ranges)
    correct = result_single == expected_primes
    print_result_row("单线程 (1 thread)", t_single, 1.0, correct)
    print()
    
    # ----------------------------------------------------------
    # 多线程测试 (2/4/8 workers)
    # ----------------------------------------------------------
    print("  【多线程测试】threading.Thread 手动创建线程")
    print("  " + "-" * 55)
    
    thread_results = {}
    for n_workers in [2, 4, MAX_WORKERS]:
        if n_workers > MAX_WORKERS:
            continue
        ranges = generate_ranges(PRIME_RANGE_UPPER, n_workers)
        t, result = run_multithreaded(ranges, n_workers)
        speedup = t_single / t
        correct = result == expected_primes
        thread_results[n_workers] = (t, speedup)
        print_result_row(f"{n_workers} threads", t, speedup, correct)
    
    print()
    
    # ----------------------------------------------------------
    # ThreadPoolExecutor 测试
    # ----------------------------------------------------------
    print("  【ThreadPoolExecutor】高级线程池接口")
    print("  " + "-" * 55)
    
    for n_workers in [2, 4, MAX_WORKERS]:
        if n_workers > MAX_WORKERS:
            continue
        ranges = generate_ranges(PRIME_RANGE_UPPER, n_workers)
        t, result = run_threadpool(ranges, n_workers)
        speedup = t_single / t
        correct = result == expected_primes
        print_result_row(f"ThreadPool ({n_workers})", t, speedup, correct)
    
    print()
    
    # ----------------------------------------------------------
    # 多进程测试 (绕过GIL的传统方案)
    # ----------------------------------------------------------
    print("  【多进程对照】ProcessPoolExecutor (绕过GIL)")
    print("  " + "-" * 55)
    
    try:
        for n_workers in [2, 4, min(MAX_WORKERS, 4)]:
            ranges = generate_ranges(PRIME_RANGE_UPPER, n_workers)
            t, result = run_multiprocess(ranges, n_workers)
            speedup = t_single / t
            correct = result == expected_primes
            print_result_row(f"ProcessPool ({n_workers})", t, speedup, correct)
    except Exception as e:
        print(f"  ⚠️  多进程测试失败（容器环境可能不支持fork）: {e}")
    
    print()
    print("-" * 70)
    print()
    
    # ----------------------------------------------------------
    # 结论分析
    # ----------------------------------------------------------
    print("  【结果分析】")
    print()
    
    if info["free_threading_build"] and not info["gil_enabled"]:
        # 无GIL模式
        best_thread_speedup = max(s for _, s in thread_results.values())
        print(f"  🎉 当前运行在无GIL模式 (free-threading)！")
        print(f"     最佳多线程加速比: {best_thread_speedup:.2f}x（{num_cpus}核下理论上限 {num_cpus}x）")
        print()
        if best_thread_speedup > 1.5:
            print("     结论: 多线程CPU密集任务获得了显著加速，GIL移除有效！")
        else:
            print("     注意: 加速比不明显可能由于：")
            print("           - 任务规模不够大（计算量太小，线程创建开销占比高）")
            print("           - CPU核心数不足")
            print("           - 纯Python对象引用计数仍有内部同步开销")
    elif info["free_threading_build"] and info["gil_enabled"]:
        # GIL启用（但支持free-threading的构建）
        best_thread_speedup = max(s for _, s in thread_results.values())
        print(f"  📊 当前GIL已启用（但镜像支持free-threading）")
        print(f"     最佳多线程加速比: {best_thread_speedup:.2f}x")
        print()
        if best_thread_speedup < 1.2:
            print("     结论: GIL阻止了多线程CPU并行（符合预期）。")
            print("           在GIL模式下，多线程对CPU密集任务基本无效。")
        else:
            print("     观察: 有少量加速可能来自IO等待或GIL释放间隙。")
        print()
        print("     💡 设置 PYTHON_GIL=0 体验无GIL并行。")
    else:
        print("  ⚠️  当前Python不支持free-threading。")
    
    print()
    print("  【Free-Threading 使用建议】")
    print()
    print("  1. 启动无GIL模式:")
    print("       docker run -e PYTHON_GIL=0 <image> python your_script.py")
    print()
    print("  2. 代码兼容检查:")
    print("     - 检查C扩展是否已适配free-threading（NumPy等需abi3或ft版本）")
    print("     - 使用 sys._is_gil_enabled() 检测运行时GIL状态")
    print("     - 线程安全：无GIL模式下多线程共享状态需自行加锁（threading.Lock）")
    print()
    print("  3. 适用场景:")
    print("     - ✅ 纯Python CPU密集型并行计算")
    print("     - ✅ 大量独立计算任务（如蒙特卡洛模拟、素数计算）")
    print("     - ✅ 替代多进程方案（避免进程间通信开销）")
    print("     - ⚠️ IO密集型任务用asyncio或多线程即可，无GIL优势不明显")
    print("     - ⚠️ 已释放GIL的C扩展（NumPy运算、Pandas）在GIL模式下已可并行")
    print()
    print("  4. 性能注意事项:")
    print("     - Free-threading模式单线程性能可能有~5-15%开销（引用计数原子操作）")
    print("     - 真正的多线程加速需要足够的计算粒度抵消线程创建/同步开销")
    print("     - 对于超大规模并行，多进程仍然是值得考虑的选项（进程隔离更安全）")
    print()
    print("=" * 70)
    print("  演示完成")
    print("=" * 70)


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)  # 容器环境兼容性
    main()
