"""spec_loader 缓存预热脚本（Warmup Script）。

用途：
  1. 冷启动风暴防护：在服务重启/缓存清除后主动预热缓存，避免并发冷启动
  2. 分批重启策略：滚动重启时先预热新实例，再切流量
  3. 定时预热：在低峰期预加载高频任务类型的规范到磁盘缓存
  4. 缓存健康检查：验证缓存文件完整性和各任务类型加载性能

用法：
  python .agents/scripts/spec-loader-warmup.py              # 预热全部任务类型
  python .agents/scripts/spec-loader-warmup.py --tasks code_review,commit
  python .agents/scripts/spec-loader-warmup.py --stages execution,planning
  python .agents/scripts/spec-loader-warmup.py --check       # 仅健康检查，不写入缓存
  python .agents/scripts/spec-loader-warmup.py --benchmark   # 预热后运行基准测试

分批重启集成示例：
  # 步骤1：旧实例仍在服务，新实例启动前先预热
  python .agents/scripts/spec-loader-warmup.py --quiet

  # 步骤2：验证预热效果
  python .agents/scripts/spec-loader-warmup.py --check

  # 步骤3：切流量到新实例
  # （部署系统执行流量切换）

  # 步骤4：滚动下一批
  sleep 2 && python .agents/scripts/spec-loader-warmup.py --quiet
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from lib.spec_loader import SpecLoader, TASK_ROUTING, CACHE_FILENAME, CACHE_DIRNAME

PROJECT_ROOT = SCRIPTS_DIR.parent.parent


def warmup(tasks: list[str] | None = None,
           stages: list[str] | None = None,
           check_only: bool = False,
           quiet: bool = False) -> dict:
    """执行缓存预热，返回结果统计。

    Args:
        tasks: 要预热的任务类型列表（None=全部）
        stages: 要预热的阶段列表（默认execution+planning）
        check_only: 仅健康检查，不保存缓存
        quiet: 静默模式，仅输出JSON结果

    Returns:
        预热结果字典
    """
    if stages is None:
        stages = ["execution", "planning"]

    log = (lambda *a: None) if quiet else print

    log("=" * 60)
    log("spec_loader 缓存预热" + ("（健康检查模式）" if check_only else ""))
    log("=" * 60)

    loader = SpecLoader(PROJECT_ROOT, use_disk_cache=not check_only)

    results = {
        "timestamp": time.time(),
        "check_only": check_only,
        "tasks_preheated": 0,
        "stages_preheated": 0,
        "total_specs_loaded": 0,
        "total_time_ms": 0,
        "stage_times": {},
        "task_details": [],
        "cache_stats_before": loader.get_cache_stats(),
    }

    all_tasks = tasks if tasks else list(TASK_ROUTING.keys())
    task_keywords = {tt: cfg["keywords"][0] for tt, cfg in TASK_ROUTING.items() if tt in all_tasks}

    t_total_start = time.perf_counter()

    for stage in stages:
        t_stage_start = time.perf_counter()
        stage_specs = 0
        log(f"\n[预热阶段: {stage}]")

        for task_type, keyword in task_keywords.items():
            t0 = time.perf_counter()
            include_l1b = (stage in ("planning", "startup"))
            result = loader.load_for_task(keyword, stage=stage, include_l1b=include_l1b)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            new_specs = len(result.loaded_specs)
            stage_specs += new_specs

            detail = {
                "task_type": task_type,
                "stage": stage,
                "keyword": keyword,
                "time_ms": round(elapsed_ms, 3),
                "new_specs": new_specs,
                "layer_summary": result.layer_summary,
            }
            results["task_details"].append(detail)

            hit_rate = "HIT" if new_specs == 0 else f"MISS(+{new_specs})"
            log(f"  {task_type:20s} | {elapsed_ms:7.3f}ms | {hit_rate}")

        stage_elapsed = (time.perf_counter() - t_stage_start) * 1000
        results["stage_times"][stage] = round(stage_elapsed, 3)
        results["stages_preheated"] += 1
        results["total_specs_loaded"] += stage_specs
        log(f"  阶段{stage}合计: {stage_elapsed:.2f}ms, 新载入{stage_specs}个规范")

    results["total_time_ms"] = round((time.perf_counter() - t_total_start) * 1000, 3)
    results["tasks_preheated"] = len(all_tasks)

    if not check_only:
        loader.save_cache()
        log(f"\n缓存已保存到磁盘 | {loader.get_cache_stats()['disk_entries']}个条目")
    else:
        log(f"\n健康检查完成（未写入缓存）")

    results["cache_stats_after"] = loader.get_cache_stats()

    # 验证缓存文件完整性
    cache_file = PROJECT_ROOT / ".agents" / ".cache" / CACHE_FILENAME
    results["cache_file_exists"] = cache_file.exists()
    if cache_file.exists():
        results["cache_file_size_bytes"] = cache_file.stat().st_size
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            results["cache_file_valid"] = True
            results["cache_version"] = cache_data.get("version")
            results["cache_entry_count"] = len(cache_data.get("entries", {}))
        except (json.JSONDecodeError, OSError):
            results["cache_file_valid"] = False
    else:
        results["cache_file_valid"] = False
        results["cache_file_size_bytes"] = 0

    log(f"\n预热总耗时: {results['total_time_ms']:.2f}ms")
    log(f"缓存文件: {'有效' if results.get('cache_file_valid') else '无效/不存在'}"
        f" ({results.get('cache_file_size_bytes', 0)} bytes, "
        f"{results.get('cache_entry_count', 0)} entries)")

    return results


def main():
    parser = argparse.ArgumentParser(description="spec_loader 缓存预热脚本")
    parser.add_argument("--tasks", "-t", type=str, default=None,
                        help="逗号分隔的任务类型列表（默认全部），如 code_review,commit,retrospective")
    parser.add_argument("--stages", "-s", type=str, default=None,
                        help="逗号分隔的阶段列表（默认execution,planning）")
    parser.add_argument("--check", "-c", action="store_true",
                        help="健康检查模式：仅验证缓存，不写入")
    parser.add_argument("--benchmark", "-b", action="store_true",
                        help="预热后运行CLI benchmark对比性能")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="静默模式：仅输出JSON结果到stdout")
    parser.add_argument("--json", action="store_true",
                        help="输出JSON格式结果（供监控系统采集）")
    args = parser.parse_args()

    tasks = args.tasks.split(",") if args.tasks else None
    stages = args.stages.split(",") if args.stages else None

    results = warmup(tasks=tasks, stages=stages,
                     check_only=args.check, quiet=args.quiet)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))

    if args.benchmark and not args.check:
        import subprocess
        if not args.quiet:
            print("\n" + "=" * 60)
            print("预热后基准测试")
            print("=" * 60)
        r = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "spec-loader.py"), "benchmark"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if not args.quiet:
            print(r.stdout)
            if r.stderr:
                print(r.stderr, file=sys.stderr)
        results["benchmark_exit_code"] = r.returncode

    if not args.quiet:
        print("\n" + "=" * 60)
        if results.get("cache_file_valid", False):
            print("✅ 预热完成，缓存健康")
        else:
            print("⚠️  缓存文件无效，请检查")
        print("=" * 60)

    sys.exit(0 if results.get("cache_file_valid", True) else 1)


if __name__ == "__main__":
    main()
