#!/usr/bin/env python3
"""spec_loader 多进程并发写入压测脚本。

模拟极端并发场景（冷启动风暴），验证PID唯一命名方案在多进程同时
写入磁盘缓存时的稳定性：无数据损坏、无死锁、无tmp文件泄漏。

用法：
  python spec-loader-stress-test.py              # 默认20进程×10轮
  python spec-loader-stress-test.py -p 50 -r 20  # 50进程×20轮
  python spec-loader-stress-test.py --stale 50    # 预置50个stale tmp文件测试清理性能
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import random
import shutil
import sys
import tempfile
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.atomic_write import _DEFAULT_STALE_MAX_AGE_SEC as _STALE_TMP_MAX_AGE_SEC
from lib.spec_loader import (
    CACHE_DIRNAME,
    CACHE_FILENAME,
    CACHE_VERSION,
    SpecLoader,
)

TASK_TYPES = [
    "代码审查",
    "帮我提交代码",
    "复盘一下这个项目",
    "画个mermaid",
    "链接检查修复",
    "运行测试",
    "安全扫描",
    "性能分析",
]


def _worker(project_root: Path, worker_id: int, task: str, results: list, barrier_id: int = None):
    """子进程入口：模拟一次完整的spec加载+保存流程。

    返回dict包含：worker_id、pid、success、elapsed_ms、cache_entries、error。
    """
    pid = os.getpid()
    start = time.perf_counter()
    info = {
        "worker_id": worker_id,
        "pid": pid,
        "task": task,
        "success": False,
        "elapsed_ms": 0,
        "cache_entries": 0,
        "error": None,
        "tmp_created": False,
    }
    try:
        loader = SpecLoader(project_root, use_disk_cache=True, verbose=False)
        stage = "execution" if worker_id % 3 != 0 else "planning"
        result = loader.load_for_task(task, stage=stage)
        loader.save_cache()
        info["success"] = True
        info["cache_entries"] = len(loader._disk_cache) + len(loader._loaded)
        info["loaded_count"] = result.spec_count
        info["total_chars"] = result.total_chars
    except Exception as e:
        info["error"] = f"{type(e).__name__}: {e}"
    info["elapsed_ms"] = (time.perf_counter() - start) * 1000
    results.append(info)


def _worker_sync(project_root: Path, worker_id: int, task: str, results_dict: dict, barrier):
    """同步版本：所有进程在barrier处等待后同时开始写入。"""
    pid = os.getpid()
    try:
        barrier.wait(timeout=30)
    except Exception:
        pass
    start = time.perf_counter()
    info = {
        "worker_id": worker_id,
        "pid": pid,
        "task": task,
        "success": False,
        "elapsed_ms": 0,
        "cache_entries": 0,
        "error": None,
    }
    try:
        loader = SpecLoader(project_root, use_disk_cache=True, verbose=False)
        stage = "execution" if worker_id % 3 != 0 else "planning"
        result = loader.load_for_task(task, stage=stage)
        loader.save_cache()
        info["success"] = True
        info["cache_entries"] = len(loader._disk_cache) + len(loader._loaded)
        info["loaded_count"] = result.spec_count
        info["total_chars"] = result.total_chars
    except Exception as e:
        info["error"] = f"{type(e).__name__}: {e}"
    info["elapsed_ms"] = (time.perf_counter() - start) * 1000
    results_dict[worker_id] = info


def _create_minimal_project(root: Path):
    """创建一个最小化的项目结构用于压测。"""
    agents_dir = root / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "ONBOARDING.md").write_text("# L0 入口\n" * 5, encoding="utf-8")
    (agents_dir / "global-core-rules.md").write_text("# 全局核心规则\n" * 30, encoding="utf-8")
    (agents_dir / "capability-boundaries.md").write_text("# 能力边界\n" * 20, encoding="utf-8")
    cap_dir = agents_dir / "capabilities"
    cap_dir.mkdir(exist_ok=True)
    (cap_dir / "capability-registry.md").write_text("# 能力注册中心\n" * 40, encoding="utf-8")
    ctx_dir = agents_dir / "context-routing"
    ctx_dir.mkdir(exist_ok=True)
    (ctx_dir / "context-routing.md").write_text("# 上下文路由表\n" * 20, encoding="utf-8")
    skills_dir = agents_dir / "skills"
    skills_dir.mkdir(exist_ok=True)
    workflows_dir = agents_dir / "workflows"
    workflows_dir.mkdir(exist_ok=True)
    roles_dir = agents_dir / "roles"
    roles_dir.mkdir(exist_ok=True)
    for role_name in ["reviewer.md", "committer.md", "retrospector.md"]:
        (roles_dir / role_name).write_text(f"# {role_name}\n" * 10, encoding="utf-8")
    for wf_name in ["code-review.md", "commit.md", "retrospective.md", "mermaid.md",
                    "link-check.md", "testing.md", "security-scan.md", "perf-analysis.md"]:
        (workflows_dir / wf_name).write_text(f"# {wf_name} 工作流\n" * 15, encoding="utf-8")


def _seed_stale_tmp_files(cache_dir: Path, count: int, age_sec: float):
    """在缓存目录中制造陈旧tmp文件，用于测试清理性能。"""
    now = time.time()
    old_time = now - age_sec
    for i in range(count):
        pid = 90000 + i
        rand = f"{i:06x}"
        tmp = cache_dir / f"{CACHE_FILENAME}.pid{pid}.{rand}.tmp"
        tmp.write_text('{"stale": true, "index": %d}' % i, encoding="utf-8")
        os.utime(tmp, (old_time, old_time))


def run_stress_test(num_processes: int, num_rounds: int, num_stale: int = 0,
                    sync_start: bool = True, verbose: bool = False):
    """执行多进程压测。"""
    print("=" * 70)
    print(f"spec_loader 多进程并发压测")
    print(f"进程数={num_processes} | 轮次={num_rounds} | "
          f"stale_tmp={num_stale} | 同步启动={'是' if sync_start else '否'}")
    print("=" * 70)

    with tempfile.TemporaryDirectory(prefix="spec_loader_stress_") as tmp:
        root = Path(tmp)
        _create_minimal_project(root)
        cache_dir = root / ".agents" / CACHE_DIRNAME

        if num_stale > 0:
            cache_dir.mkdir(parents=True, exist_ok=True)
            _seed_stale_tmp_files(cache_dir, num_stale, _STALE_TMP_MAX_AGE_SEC + 60)
            initial_tmp_count = len(list(cache_dir.glob(f"{CACHE_FILENAME}.pid*.tmp")))
            print(f"[预置] {initial_tmp_count} 个stale tmp文件（age > {_STALE_TMP_MAX_AGE_SEC}s）")

        round_stats = []
        total_start = time.perf_counter()

        for rnd in range(num_rounds):
            round_start = time.perf_counter()
            tasks = [random.choice(TASK_TYPES) for _ in range(num_processes)]

            if sync_start:
                manager = multiprocessing.Manager()
                results_dict = manager.dict()
                barrier = manager.Barrier(num_processes)
                processes = []
                for i in range(num_processes):
                    p = multiprocessing.Process(
                        target=_worker_sync,
                        args=(root, i, tasks[i], results_dict, barrier),
                    )
                    processes.append(p)
                for p in processes:
                    p.start()
                for p in processes:
                    p.join(timeout=30)
                results = list(results_dict.values())
                manager.shutdown()
            else:
                with multiprocessing.Manager() as manager:
                    results = manager.list()
                    processes = []
                    for i in range(num_processes):
                        p = multiprocessing.Process(
                            target=_worker,
                            args=(root, i, tasks[i], results),
                        )
                        processes.append(p)
                    for p in processes:
                        p.start()
                    for p in processes:
                        p.join(timeout=30)
                    results = list(results)

            round_elapsed = (time.perf_counter() - round_start) * 1000
            successes = [r for r in results if r.get("success")]
            failures = [r for r in results if not r.get("success")]
            elapsed_list = [r["elapsed_ms"] for r in successes]
            cache_path = cache_dir / CACHE_FILENAME
            cache_valid = False
            cache_entry_count = 0
            try:
                data = json.loads(cache_path.read_text(encoding="utf-8"))
                cache_valid = data.get("version") == CACHE_VERSION and "entries" in data
                cache_entry_count = len(data.get("entries", {}))
            except (json.JSONDecodeError, OSError) as e:
                cache_corruption_error = str(e)

            tmp_pattern = f"{CACHE_FILENAME}.pid*.tmp"
            remaining_tmp = list(cache_dir.glob(tmp_pattern))
            recent_tmp = [t for t in remaining_tmp if time.time() - t.stat().st_mtime < 10]

            stat = {
                "round": rnd + 1,
                "total": num_processes,
                "success": len(successes),
                "failure": len(failures),
                "elapsed_ms": round_elapsed,
                "min_ms": min(elapsed_list) if elapsed_list else 0,
                "max_ms": max(elapsed_list) if elapsed_list else 0,
                "avg_ms": sum(elapsed_list) / len(elapsed_list) if elapsed_list else 0,
                "p95_ms": sorted(elapsed_list)[int(len(elapsed_list) * 0.95)] if len(elapsed_list) >= 2 else (elapsed_list[0] if elapsed_list else 0),
                "cache_valid": cache_valid,
                "cache_entries": cache_entry_count,
                "remaining_tmp": len(remaining_tmp),
                "recent_tmp": len(recent_tmp),
            }
            round_stats.append(stat)

            status = "PASS" if cache_valid and not failures and len(recent_tmp) == 0 else "FAIL"
            print(f"  [R{rnd+1:02d}] {status} | 成功={len(successes)}/{num_processes} | "
                  f"耗时={round_elapsed:.0f}ms(avg={stat['avg_ms']:.1f}ms "
                  f"p95={stat['p95_ms']:.1f}ms max={stat['max_ms']:.1f}ms) | "
                  f"缓存条目={cache_entry_count} | 残留tmp={len(recent_tmp)}", end="")
            if failures:
                print(f" | 失败样例={failures[0].get('error', 'unknown')[:80]}", end="")
            print()

            if failures:
                for f in failures[:3]:
                    print(f"         worker={f['worker_id']} pid={f['pid']} error={f.get('error')}")

        total_elapsed = (time.perf_counter() - total_start) * 1000

        cache_path = cache_dir / CACHE_FILENAME
        final_cache_valid = False
        final_cache_data = None
        try:
            final_cache_data = json.loads(cache_path.read_text(encoding="utf-8"))
            final_cache_valid = (final_cache_data.get("version") == CACHE_VERSION
                                and isinstance(final_cache_data.get("entries"), dict))
        except (json.JSONDecodeError, OSError):
            pass

        final_tmp_files = list(cache_dir.glob(f"{CACHE_FILENAME}.pid*.tmp"))
        old_tmp = [t for t in final_tmp_files if time.time() - t.stat().st_mtime > 10]

        print()
        print("=" * 70)
        print("压测结果汇总")
        print("=" * 70)
        total_success = sum(s["success"] for s in round_stats)
        total_failure = sum(s["failure"] for s in round_stats)
        all_cache_valid = all(s["cache_valid"] for s in round_stats)
        no_tmp_leak = all(s["recent_tmp"] == 0 for s in round_stats)

        print(f"  总轮次: {num_rounds}")
        print(f"  总操作: {num_processes * num_rounds}")
        print(f"  成功: {total_success} | 失败: {total_failure}")
        print(f"  总耗时: {total_elapsed:.0f}ms")
        print(f"  最终缓存: {'VALID' if final_cache_valid else 'CORRUPTED/MISSING'} | 条目={len(final_cache_data.get('entries', {})) if final_cache_data else 0}")
        print(f"  缓存JSON完整性(所有轮次): {'PASS' if all_cache_valid else 'FAIL'}")
        print(f"  tmp文件泄漏检测(写入后10s内): {'PASS' if no_tmp_leak else 'FAIL'}")
        print(f"  最终tmp文件数: {len(final_tmp_files)} (其中陈旧>10s: {len(old_tmp)})")

        all_passed = (total_failure == 0 and all_cache_valid and no_tmp_leak
                      and final_cache_valid and len(old_tmp) == 0)
        print()
        if all_passed:
            print("✅ 压测通过：PID唯一命名方案在极端并发下稳定，无死锁、无损坏、无泄漏。")
        else:
            print("❌ 压测失败：存在问题需要修复。")
        return all_passed


def main():
    parser = argparse.ArgumentParser(description="spec_loader多进程并发压测")
    parser.add_argument("-p", "--processes", type=int, default=20,
                        help="并发进程数（默认20）")
    parser.add_argument("-r", "--rounds", type=int, default=10,
                        help="压测轮次（默认10）")
    parser.add_argument("--stale", type=int, default=20,
                        help="预置stale tmp文件数（默认20，设0跳过）")
    parser.add_argument("--no-sync", action="store_true",
                        help="禁用barrier同步（进程自由启动）")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="详细输出")
    args = parser.parse_args()

    if sys.platform == "win32":
        multiprocessing.set_start_method("spawn", force=True)

    passed = run_stress_test(
        num_processes=args.processes,
        num_rounds=args.rounds,
        num_stale=args.stale,
        sync_start=not args.no_sync,
        verbose=args.verbose,
    )
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
