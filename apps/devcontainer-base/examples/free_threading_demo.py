#!/usr/bin/env python3
"""
Python 3.14 Free-Threading (无GIL) 并发性能演示脚本
==================================================

本脚本演示 Python 3.14 free-threading (PEP 703) 模式下多线程并发性能的提升。

在传统CPython中，GIL（全局解释器锁）使得CPU密集型多线程代码无法真正并行执行。
Python 3.14 的 free-threading 构建(cpython-314t)移除了GIL，使得多线程可以真正利用多核CPU。

重要说明：
- 标准Python构建(cpython-314)GIL始终启用，设置PYTHON_GIL=0会报错
- Free-threading构建(cpython-314t)GIL默认禁用，设置PYTHON_GIL=1可重新启用
- conda-forge中free-threading版本需安装 `python=*=*_cp314t` 构建

使用方式（在 devcontainer-base:conda-libmamba-v2 容器中运行）:

  # 方式1: 标准Python（GIL始终启用，作为对照基线）
  docker run --rm devcontainer-base:conda-libmamba-v2 \
    python examples/free_threading_demo.py

  # 方式2: 创建free-threading环境并运行（需先conda create -n ft python=*=*_cp314t）
  docker run --rm devcontainer-base:conda-libmamba-v2 \
    /opt/conda/envs/ft/bin/python examples/free_threading_demo.py

  # 方式3: 在free-threading构建中强制启用GIL（对照测试）
  docker run --rm -e PYTHON_GIL=1 devcontainer-base:conda-libmamba-v2 \
    /opt/conda/envs/ft/bin/python examples/free_threading_demo.py
"""

import sys
import os
import time
import math
import threading
import multiprocessing
import sysconfig
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, List, Tuple

# ============================================================
# 环境检测
# ============================================================

def detect_environment() -> dict:
    """检测当前Python环境配置
    
    正确的free-threading检测方式：
    - sysconfig.get_config_var('Py_GIL_DISABLED') == 1 表示free-threading构建(cp314t)
    - sys._is_gil_enabled() 在所有Python 3.14构建中都存在，但仅在ft构建中可返回False
    - SOABI包含't'后缀(cpython-314t)表示free-threading构建
    """
    info = {
        "python_version": sys.version,
        "gil_enabled": True,
        "free_threading_build": False,
        "cpu_count": os.cpu_count() or 1,
    }
    
    # 正确检测free-threading构建：通过sysconfig
    py_gil_disabled = sysconfig.get_config_var('Py_GIL_DISABLED')
    soabi = sysconfig.get_config_var('SOABI') or ''
    
    if py_gil_disabled == 1 or 'cpython-314t' in soabi:
        info["free_threading_build"] = True
        info["gil_enabled"] = sys._is_gil_enabled()
    elif hasattr(sys, "_is_gil_enabled"):
        # 标准CPython 3.14也有_is_gil_enabled()但始终返回True
        info["gil_enabled"] = True
    
    # 环境变量检测
    info["pygil_env"] = os.environ.get("PYTHON_GIL", "1 (default in standard build, 0 in ft build)")
    
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
        gil_status = "🔒 启用 (GIL active, PYTHON_GIL=1)" if info["gil_enabled"] else "🔓 禁用 (No-GIL / free-threading, default for cp314t)"
        print(f"  GIL 状态: {gil_status}")
        print(f"  PYTHON_GIL 环境变量: {info['pygil_env']}")
        if info["gil_enabled"]:
            print()
            print("  💡 当前GIL已启用（强制兼容模式）。不设置PYTHON_GIL即为默认无GIL模式。")
    else:
        print("  ⚠️  当前Python是标准构建(cp314)，GIL始终启用，无法禁用。")
        print("     如需体验free-threading，请安装cp314t构建：")
        print("       conda create -n ft python=*=*_cp314t -c conda-forge")
        print("       conda activate ft && python examples/free_threading_demo.py")
    
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
        print(f"  🎉 当前运行在无GIL模式 (free-threading cp314t)！")
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
        # GIL启用（ft构建但PYTHON_GIL=1）
        best_thread_speedup = max(s for _, s in thread_results.values())
        print(f"  📊 当前GIL已启用（ft构建下的兼容模式 PYTHON_GIL=1）")
        print(f"     最佳多线程加速比: {best_thread_speedup:.2f}x")
        print()
        if best_thread_speedup < 1.2:
            print("     结论: GIL阻止了多线程CPU并行（符合预期）。")
        else:
            print("     观察: 有少量加速可能来自IO等待或GIL释放间隙。")
        print()
        print("     💡 取消PYTHON_GIL环境变量（默认即为无GIL模式）。")
    else:
        best_thread_speedup = max(s for _, s in thread_results.values())
        print(f"  📊 当前Python是标准构建(cp314)，GIL始终启用。")
        print(f"     最佳多线程加速比: {best_thread_speedup:.2f}x（GIL限制下通常<1.2x）")
        print()
        if best_thread_speedup < 1.2:
            print("     结论: GIL有效阻止了CPU密集型多线程并行（符合预期）。")
        print()
        print("     💡 安装free-threading版本体验无GIL并行：")
        print("           conda create -n ft python=*=*_cp314t -c conda-forge")
    
    print()
    print("  【Free-Threading 使用建议】")
    print()
    print("  1. 安装free-threading Python:")
    print("       conda create -n ft python=*=*_cp314t -c conda-forge --solver libmamba")
    print("       conda activate ft  # 默认即为无GIL模式")
    print()
    print("  2. 环境变量:")
    print("       - cp314t构建默认无GIL；PYTHON_GIL=1 强制启用GIL（兼容模式）")
    print("       - 标准cp314构建GIL始终启用；PYTHON_GIL=0 会导致启动错误")
    print()
    print("  3. 代码兼容检查:")
    print("     - 检查C扩展是否已适配free-threading（需abi3或cp314t版本）")
    print("     - 使用 sysconfig.get_config_var('Py_GIL_DISABLED') 检测构建类型")
    print("     - 线程安全：无GIL模式下多线程共享状态需自行加锁（threading.Lock）")
    print()
    print("  4. 适用场景:")
    print("     - ✅ 纯Python CPU密集型并行计算")
    print("     - ✅ 大量独立计算任务（如蒙特卡洛模拟、素数计算）")
    print("     - ✅ 替代多进程方案（避免进程间通信开销）")
    print("     - ⚠️ IO密集型任务用asyncio即可，无GIL优势不明显")
    print("     - ⚠️ 已释放GIL的C扩展（NumPy运算）在GIL模式下已可并行")
    print()
    print("  5. 性能注意事项:")
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
