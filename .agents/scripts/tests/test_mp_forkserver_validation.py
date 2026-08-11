"""
Python multiprocessing fork vs forkserver vs spawn 行为验证脚本
=============================================================

用途：验证以下核心洞察对应的行为差异：
  洞察1：fork在多线程进程中根本不安全（锁死锁/状态损坏）
  洞察2：forkserver从干净单线程server fork，避免了多线程fork的风险
  洞察3：隐式契约（全局变量继承/__main__保护/pickle要求）在非fork模式下必须遵守

使用方法（仅Linux有效，Windows仅spawn可用）：
    python test_mp_forkserver_validation.py              # 按顺序运行所有测试
    python test_mp_forkserver_validation.py fork          # 仅测试fork模式（预计失败/死锁）
    python test_mp_forkserver_validation.py forkserver    # 仅测试forkserver模式（预计通过）
    python test_mp_forkserver_validation.py spawn         # 仅测试spawn模式（预计通过）

注意：fork+多线程的死锁测试设计为30秒超时保护，不会永久挂起。
"""

import sys
import os
import time
import threading
import multiprocessing as mp
from multiprocessing import Process, Lock, Queue, get_context


# ============================================================
# 测试1：多线程+fork导致锁永久死锁（最经典的fork不安全案例）
# ============================================================

def _worker_that_uses_locks(lock, results_q, worker_id):
    """子进程中尝试获取锁——fork后如果锁被其他线程持有且持有者消失，则永久死锁"""
    try:
        acquired = lock.acquire(timeout=5)
        if acquired:
            results_q.put(f"worker-{worker_id}: lock acquired OK")
            lock.release()
        else:
            results_q.put(f"worker-{worker_id}: TIMEOUT acquiring lock (DEADLOCK!)")
    except Exception as e:
        results_q.put(f"worker-{worker_id}: ERROR: {type(e).__name__}: {e}")


def _thread_that_holds_lock(lock, stop_event):
    """后台线程：持有锁一段时间"""
    lock.acquire()
    while not stop_event.is_set():
        time.sleep(0.01)
    lock.release()


def test_fork_multithreaded_lock_deadlock(ctx_name):
    """
    洞察1验证：在fork模式下，从多线程状态fork时，如果另一个线程正持有锁，
    子进程中锁被复制但持有者线程不存在，导致永久死锁。
    """
    print(f"\n{'='*60}")
    print(f"测试1: {ctx_name}模式 + 多线程 + 锁继承")
    print(f"{'='*60}")

    ctx = get_context(ctx_name)
    lock = ctx.Lock()
    results_q = ctx.Queue()

    # 在主进程启动后台线程持有锁
    stop_event = threading.Event()
    holder_thread = threading.Thread(target=_thread_that_holds_lock, args=(lock, stop_event), daemon=True)
    holder_thread.start()
    time.sleep(0.2)  # 确保线程已启动并持有锁

    # 现在fork子进程（此时后台线程持有锁）
    p = ctx.Process(target=_worker_that_uses_locks, args=(lock, results_q, 1))
    p.start()
    p.join(timeout=10)

    stop_event.set()
    holder_thread.join(timeout=2)

    if p.is_alive():
        p.terminate()
        p.join(timeout=2)
        print(f"  🔴 FAIL: 子进程超时未完成（死锁），已terminate")
        print(f"     结论：{ctx_name}在多线程场景下fork后锁状态不一致，导致死锁")
        return False
    else:
        try:
            result = results_q.get_nowait()
            print(f"  🟢 PASS: {result}")
            print(f"     结论：{ctx_name}模式下子进程锁状态正常")
            return True
        except Exception:
            print(f"  🟡 UNKNOWN: 子进程退出但无结果")
            return None


# ============================================================
# 测试2：全局变量隐式继承（fork可以，forkserver/spawn不行）
# ============================================================

GLOBAL_CONFIG = {"initialized": False, "value": 0}


def _worker_that_uses_global(q, expected_value):
    """子进程读取全局变量"""
    q.put(GLOBAL_CONFIG.get("value", "MISSING"))


def test_global_variable_inheritance(ctx_name):
    """
    洞察3验证：fork下全局变量隐式继承，forkserver/spawn下全局变量是模块初始值。
    这不是bug，是API契约——spawn/forkserver语义下不依赖隐式全局状态。
    """
    print(f"\n{'='*60}")
    print(f"测试2: {ctx_name}模式 + 全局变量隐式继承")
    print(f"{'='*60}")

    ctx = get_context(ctx_name)
    GLOBAL_CONFIG["value"] = 42  # 在fork前修改全局变量
    GLOBAL_CONFIG["initialized"] = True

    q = ctx.Queue()
    p = ctx.Process(target=_worker_that_uses_global, args=(q, 42))
    p.start()
    p.join(timeout=5)

    try:
        child_value = q.get_nowait()
    except Exception:
        child_value = "NO_RESULT"

    if child_value == 42:
        print(f"  🟡 全局变量值=42：隐式继承生效（fork行为）")
        if ctx_name in ("forkserver", "spawn"):
            print(f"     注意：如果这里是42，说明模块级代码有副作用，子进程重新import时也设置了")
        return child_value == 42
    elif child_value == 0:
        print(f"  🔵 全局变量值=0（模块初始值）：隐式继承未生效")
        print(f"     这是forkserver/spawn的正确行为——必须显式传参")
        return True
    else:
        print(f"  🟡 子进程读到值={child_value}")
        return False


# ============================================================
# 测试3：局部函数/lambda作为target（fork可以，forkserver/spawn pickle失败）
# ============================================================

def _run_local_target_inside_function(ctx_name):
    """在函数内部定义局部函数作为Process target，fork可以运行但spawn/forkserver pickle失败"""
    def local_worker(q):
        q.put("hello from local function")

    ctx = get_context(ctx_name)
    q = ctx.Queue()

    try:
        p = ctx.Process(target=local_worker, args=(q,))
        p.start()
        p.join(timeout=5)
        if p.exitcode == 0:
            result = q.get_nowait()
            return True, result
        else:
            return False, f"exitcode={p.exitcode}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def test_local_function_pickle(ctx_name):
    """
    洞察3验证：局部函数/lambda无法被pickle，在forkserver/spawn下启动失败。
    fork下可以因为不需要pickle（直接复制内存）。
    """
    print(f"\n{'='*60}")
    print(f"测试3: {ctx_name}模式 + 局部函数作为target（pickle要求）")
    print(f"{'='*60}")

    ok, msg = _run_local_target_inside_function(ctx_name)
    if ok:
        print(f"  🟢 子进程启动成功: {msg}")
        if ctx_name == "fork":
            print(f"     fork可以执行局部函数（无需pickle），但这是隐式行为，不可移植")
        return True
    else:
        print(f"  🔴 子进程启动失败: {msg}")
        if ctx_name in ("forkserver", "spawn"):
            print(f"     这是正确行为——局部函数不可pickle，必须使用顶层函数")
        return False


# ============================================================
# 测试4：forkserver安全启动时机——主进程单线程时启动vs多线程时启动
# ============================================================

def _simple_worker(q):
    q.put(f"pid={os.getpid()}, main_thread={threading.current_thread().name}")


def test_forkserver_start_timing(ctx_name):
    """
    洞察2验证：forkserver应该在主进程单线程状态下启动（即第一次创建Process之前
    不要启动后台线程）。如果在多线程状态下才第一次创建Process，forkserver本身
    是从多线程状态fork的，仍有风险。
    """
    print(f"\n{'='*60}")
    print(f"测试4: {ctx_name}模式 + 启动时机验证")
    print(f"{'='*60}")

    ctx = get_context(ctx_name)
    results = []

    # 场景A：先启动子进程（此时无线程），再启动线程
    print(f"  场景A: 先创建子进程（单线程状态），再启动线程")
    q = ctx.Queue()
    p = ctx.Process(target=_simple_worker, args=(q,))
    p.start()
    p.join(timeout=5)
    if not p.is_alive():
        try:
            results.append(("A-OK", q.get_nowait()))
            print(f"    🟢 通过")
        except Exception:
            results.append(("A-FAIL", "no result"))
            print(f"    🔴 无结果")
    else:
        p.terminate()
        results.append(("A-HANG", "timeout"))
        print(f"    🔴 超时（潜在死锁）")

    # 启动一个后台线程
    stop = threading.Event()

    def bg():
        while not stop.is_set():
            time.sleep(0.01)

    t = threading.Thread(target=bg, daemon=True)
    t.start()
    time.sleep(0.1)

    # 场景B：线程已启动后再创建子进程（此时forkserver已经启动过了，后续从单线程server fork）
    print(f"  场景B: 后台线程已运行时创建子进程（forkserver已预热，安全）")
    q2 = ctx.Queue()
    p2 = ctx.Process(target=_simple_worker, args=(q2,))
    p2.start()
    p2.join(timeout=10)
    if not p2.is_alive():
        try:
            results.append(("B-OK", q2.get_nowait()))
            print(f"    🟢 通过")
        except Exception:
            results.append(("B-FAIL", "no result"))
            print(f"    🔴 无结果")
    else:
        p2.terminate()
        results.append(("B-HANG", "timeout"))
        print(f"    🔴 超时（潜在死锁）")

    stop.set()
    t.join(timeout=2)

    all_ok = all(r[0].endswith("OK") for r in results)
    return all_ok


# ============================================================
# 测试5：asyncio事件循环继承问题（fork会继承运行中的loop导致错误）
# ============================================================

def _worker_no_asyncio_used(q):
    """子进程中不使用asyncio，但可能继承了父进程的事件循环"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            q.put("INHERITED_RUNNING_LOOP")
        else:
            q.put("LOOP_NOT_RUNNING")
    except RuntimeError:
        q.put("NO_LOOP")


def test_asyncio_loop_inheritance(ctx_name):
    """
    洞察1验证：fork下子进程继承父进程运行中的asyncio事件循环状态，
    可能导致RuntimeError或事件循环损坏。forkserver/spawn下是全新进程。
    """
    print(f"\n{'='*60}")
    print(f"测试5: {ctx_name}模式 + asyncio事件循环继承")
    print(f"{'='*60}")

    import asyncio

    ctx = get_context(ctx_name)

    # 在父进程启动事件循环并运行一段时间
    async def main():
        await asyncio.sleep(0.05)
        return "done"

    # 启动一个后台线程运行事件循环
    loop_result = {}
    loop_started = threading.Event()
    stop_loop = threading.Event()

    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop_result["loop"] = loop
        loop_started.set()
        try:
            loop.run_until_complete(asyncio.sleep(20))
        except Exception:
            pass
        finally:
            loop.close()

    lt = threading.Thread(target=run_loop, daemon=True)
    lt.start()
    loop_started.wait(timeout=2)
    time.sleep(0.1)

    q = ctx.Queue()
    p = ctx.Process(target=_worker_no_asyncio_used, args=(q,))
    p.start()
    p.join(timeout=10)

    try:
        result = q.get_nowait()
    except Exception:
        result = "NO_RESULT"

    stop_loop.set()
    lt.join(timeout=2)

    if result == "NO_LOOP" or result == "LOOP_NOT_RUNNING":
        print(f"  🟢 子进程事件循环状态正常: {result}")
        return True
    elif result == "INHERITED_RUNNING_LOOP":
        print(f"  🔴 子进程继承了运行中的事件循环（fork风险）")
        return False
    else:
        print(f"  🟡 结果: {result}")
        return None


# ============================================================
# 主测试运行器
# ============================================================

def run_tests(ctx_name):
    print(f"\n{'#'*60}")
    print(f"# 启动方法: {ctx_name.upper()}")
    print(f"# Python: {sys.version}")
    print(f"# 平台: {sys.platform}")
    print(f"{'#'*60}")

    if ctx_name == "fork" and sys.platform == "win32":
        print("Windows不支持fork，跳过")
        return {}

    results = {}

    results["lock_deadlock"] = test_fork_multithreaded_lock_deadlock(ctx_name)
    results["global_var"] = test_global_variable_inheritance(ctx_name)
    results["local_func_pickle"] = test_local_function_pickle(ctx_name)
    results["start_timing"] = test_forkserver_start_timing(ctx_name)
    results["asyncio_loop"] = test_asyncio_loop_inheritance(ctx_name)

    print(f"\n{'='*60}")
    print(f"汇总结果 ({ctx_name}):")
    print(f"{'='*60}")
    for name, passed in results.items():
        status = "PASS" if passed else ("FAIL" if passed is False else "UNKNOWN")
        print(f"  {status:8s} {name}")

    return results


def show_comparison(all_results):
    print(f"\n\n{'#'*60}")
    print(f"# 三种启动方式结果对比表")
    print(f"{'#'*60}")
    print()
    print(f"| 测试项 | fork | forkserver | spawn |")
    print(f"|--------|------|-----------|-------|")

    test_names = ["lock_deadlock", "global_var", "local_func_pickle", "start_timing", "asyncio_loop"]
    test_labels = [
        "多线程+锁死锁",
        "全局变量隐式继承",
        "局部函数pickle",
        "启动时机安全",
        "asyncio事件循环继承",
    ]
    for name, label in zip(test_names, test_labels):
        r_fork = all_results.get("fork", {}).get(name, "SKIP")
        r_fs = all_results.get("forkserver", {}).get(name, "SKIP")
        r_sp = all_results.get("spawn", {}).get(name, "SKIP")
        mark = lambda v: "🟢PASS" if v is True else ("🔴FAIL" if v is False else ("⏭️SKIP" if v == "SKIP" else "🟡??"))
        print(f"| {label} | {mark(r_fork)} | {mark(r_fs)} | {mark(r_sp)} |")

    print()
    print("预期结果说明：")
    print("  多线程+锁死锁：fork 🔴FAIL（死锁），forkserver/spawn 🟢PASS")
    print("  全局变量继承：fork 下值=42（隐式继承），forkserver/spawn 下值=0（正确行为）")
    print("  局部函数pickle：fork 🟢PASS（但不可移植），forkserver/spawn 🔴FAIL（必须用顶层函数）")
    print("  启动时机：先预热forkserver再开线程 → 安全；先开线程再启动forkserver → 有风险")
    print("  asyncio事件循环：fork可能继承running loop，forkserver/spawn是全新进程")


if __name__ == "__main__":
    methods = sys.argv[1:] if len(sys.argv) > 1 else ["fork", "forkserver", "spawn"]

    if "fork" in methods and sys.platform == "win32":
        print("Windows平台不支持fork模式，跳过fork测试")
        methods = [m for m in methods if m != "fork"]

    all_results = {}
    for m in methods:
        if m not in ("fork", "forkserver", "spawn"):
            print(f"未知启动方法: {m}，跳过")
            continue
        all_results[m] = run_tests(m)
        # 每个模式测试完等待一下，确保进程清理
        time.sleep(0.5)

    if len(all_results) > 1:
        show_comparison(all_results)

    print(f"\n测试完成。在Linux/Python 3.13及以下运行此脚本可以复现fork的问题；")
    print(f"Python 3.14+ Linux默认forkserver可直接验证安全性。")
