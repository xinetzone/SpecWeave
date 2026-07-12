#!/usr/bin/env python3
"""L2 渐进式披露规范加载器 CLI。

根据任务描述自动路由并加载所需的 L0/L1a/L1b/L2 规范文件，
实现上下文按需加载，避免一次性加载全部规范导致上下文爆炸。

架构：
  L0（入口速查）→ L1a（核心规则，始终加载）→ L1b（索引，按需）→ L2（详细规范，按任务类型）
  支持内存缓存 + 基于mtime的磁盘持久缓存，跨会话复用

用法：
  python spec-loader.py task "代码审查"              # 加载代码审查所需规范
  python spec-loader.py task "复盘项目" -c            # 加载并输出内容
  python spec-loader.py task "提交代码" -s planning  # 规划阶段（加载L1b索引）
  python spec-loader.py layer L0                      # 仅加载L0层
  python spec-loader.py layer L1a                     # 加载L0+L1a（核心规则）
  python spec-loader.py layer L1                      # 加载L0+L1a+L1b（全部索引）
  python spec-loader.py list-types                    # 列出所有支持的任务类型
  python spec-loader.py audit                         # 审计所有路由引用的文件是否存在
  python spec-loader.py benchmark                     # 运行性能基准测试（冷/温启动对比）
  python spec-loader.py cache-stats                   # 查看缓存统计
  python spec-loader.py cache-clear                   # 清除磁盘缓存
"""

import argparse
import statistics
import sys
import time
from pathlib import Path

from lib.cli import setup_safe_output
from lib.project import resolve_project_root
from lib.spec_loader import (
    SpecLoader,
    TASK_ROUTING,
    LAYER_DESCRIPTIONS,
    setup_logging,
    CACHE_PATH,
)


def cmd_task(args) -> int:
    setup_logging(verbose=args.verbose)
    root = args.path or resolve_project_root(__file__)
    loader = SpecLoader(root, verbose=args.verbose, use_disk_cache=not args.no_cache)

    if args.lightweight:
        result = loader.load_for_task_lightweight(
            args.task_description,
            stage=args.stage,
        )
    else:
        result = loader.load_for_task(
            args.task_description,
            stage=args.stage,
            include_l1b=args.include_l1b,
            max_chars=args.max_chars,
            primary_only=args.primary_only,
        )
    loader.save_cache()

    output = loader.format_for_prompt(result, include_content=args.content)
    print(output)

    if args.verbose:
        cache_stats = loader.get_cache_stats()
        print(f"\n[缓存统计] 内存={cache_stats['memory_loaded']} | 磁盘条目={cache_stats['disk_entries']} | "
              f"命中率={cache_stats['hit_rate']:.1f}%", file=sys.stderr)
        if result.primary_type:
            print(f"[路由] 主类型={result.primary_type} | 辅助类型={[t for t in result.matched_types if t != result.primary_type]}",
                  file=sys.stderr)

    if result.missing_specs and args.warn_missing:
        print(f"\n⚠️ 以下规范文件未找到: {', '.join(result.missing_specs)}", file=sys.stderr)
        return 1
    return 0


def cmd_layer(args) -> int:
    setup_logging(verbose=args.verbose)
    root = args.path or resolve_project_root(__file__)
    loader = SpecLoader(root, verbose=args.verbose, use_disk_cache=not args.no_cache)

    if args.layer == "L0":
        result = loader.load_layer("L0")
    elif args.layer == "L1a":
        l0 = loader.load_layer("L0")
        l1a = loader.load_layer("L1a")
        result = l0
        result.loaded_specs += l1a.loaded_specs
        result.total_chars += l1a.total_chars
        result.layer_summary["L1a"] = l1a.layer_summary["L1a"]
        result.missing_specs += l1a.missing_specs
    elif args.layer in ("L1", "all"):
        l0 = loader.load_layer("L0")
        l1a = loader.load_layer("L1a")
        l1b = loader.load_layer("L1b")
        result = l0
        result.loaded_specs += l1a.loaded_specs + l1b.loaded_specs
        result.total_chars += l1a.total_chars + l1b.total_chars
        result.layer_summary["L1a"] = l1a.layer_summary["L1a"]
        result.layer_summary["L1b"] = l1b.layer_summary["L1b"]
        result.missing_specs += l1a.missing_specs + l1b.missing_specs
    else:
        print(f"错误: 未知层 {args.layer}，支持 L0/L1a/L1", file=sys.stderr)
        return 1

    loader.save_cache()
    output = loader.format_for_prompt(result, include_content=args.content)
    print(output)
    return 0


def cmd_list_types(args) -> int:
    print("支持的任务类型路由（四层架构：L0→L1a→L1b→L2）：")
    print()
    print(f"{'任务类型':<25} {'触发关键词示例':<40} {'L2规范数'}")
    print("-" * 90)
    for task_type, config in sorted(TASK_ROUTING.items()):
        kws = ", ".join(config["keywords"][:3])
        if len(config["keywords"]) > 3:
            kws += "..."
        print(f"{task_type:<25} {kws:<40} {len(config['l2_specs'])}")
    print()
    print(f"L1a 核心规则（始终加载）: {len(SpecLoader.L1A_CORE_SPECS)} 个")
    print(f"L1b 索引文档（按需加载）: {len(SpecLoader.L1B_INDEX_SPECS)} 个")
    print(f"合计: {len(TASK_ROUTING)} 种任务类型")
    return 0


def cmd_audit(args) -> int:
    setup_logging(verbose=args.verbose)
    root = args.path or resolve_project_root(__file__)
    loader = SpecLoader(root, verbose=args.verbose, use_disk_cache=False)

    missing = []
    ok = 0

    print("审计 L0 规范...")
    for rel_path in loader.L0_SPECS:
        full = loader.agents_dir / rel_path
        alt = loader.root / rel_path
        if full.exists() or alt.exists():
            ok += 1
            if args.verbose:
                print(f"  ✅ L0: {rel_path}")
        else:
            missing.append(("L0", rel_path))
            if args.verbose:
                print(f"  ❌ L0: {rel_path}")

    print("审计 L1a 核心规则...")
    for rel_path in loader.L1A_CORE_SPECS:
        full = loader.agents_dir / rel_path
        alt = loader.root / rel_path
        if full.exists() or alt.exists():
            ok += 1
            if args.verbose:
                print(f"  ✅ L1a: {rel_path}")
        else:
            missing.append(("L1a", rel_path))
            if args.verbose:
                print(f"  ❌ L1a: {rel_path}")

    print("审计 L1b 索引文档...")
    for rel_path in loader.L1B_INDEX_SPECS:
        full = loader.agents_dir / rel_path
        alt = loader.root / rel_path
        if full.exists() or alt.exists():
            ok += 1
            if args.verbose:
                print(f"  ✅ L1b: {rel_path}")
        else:
            missing.append(("L1b", rel_path))
            if args.verbose:
                print(f"  ❌ L1b: {rel_path}")

    print("审计 L2 任务路由...")
    for task_type, config in TASK_ROUTING.items():
        for rel_path in config["l2_specs"]:
            full = loader.agents_dir / rel_path
            alt = loader.root / rel_path
            if full.exists() or alt.exists():
                ok += 1
                if args.verbose:
                    print(f"  ✅ L2: {rel_path} (type={task_type})")
            else:
                missing.append(("L2", rel_path, task_type))
                if args.verbose:
                    print(f"  ❌ L2: {rel_path} (type={task_type})")

    print()
    if missing:
        print(f"❌ 发现 {len(missing)} 个缺失文件（{ok} 个正常）：")
        for item in missing:
            if len(item) == 3:
                layer, path, task_type = item
                print(f"  [{layer}] {path} (任务类型: {task_type})")
            else:
                layer, path = item
                print(f"  [{layer}] {path}")
        return 1
    else:
        print(f"✅ 所有 {ok} 个规范文件均存在（L0:{len(loader.L0_SPECS)} L1a:{len(loader.L1A_CORE_SPECS)} L1b:{len(loader.L1B_INDEX_SPECS)}）")
        return 0


def cmd_cache_stats(args) -> int:
    setup_logging(verbose=args.verbose)
    root = args.path or resolve_project_root(__file__)
    cache_path = root / ".agents" / CACHE_PATH

    if not cache_path.exists():
        print(f"磁盘缓存文件不存在: {cache_path}")
        print("（首次运行后会自动创建）")
        return 0

    import json
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"读取缓存失败: {e}")
        return 1

    entries = data.get("entries", {})
    total_size = 0
    layer_counts = {"L0": 0, "L1a": 0, "L1b": 0, "L2": 0}
    oldest = None
    newest = None
    for key, entry in entries.items():
        content_len = len(entry.get("content", ""))
        total_size += content_len
        layer = entry.get("layer", "L2")
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        cached_at = entry.get("cached_at", 0)
        if oldest is None or cached_at < oldest:
            oldest = cached_at
        if newest is None or cached_at > newest:
            newest = cached_at

    from datetime import datetime
    print("=== 磁盘缓存统计 ===")
    print(f"缓存版本: {data.get('version', '?')}")
    print(f"缓存路径: {cache_path}")
    print(f"文件大小: {cache_path.stat().st_size / 1024:.1f} KB")
    print(f"条目数量: {len(entries)}")
    print(f"缓存内容总字符数: {total_size:,}")
    print(f"层分布: L0={layer_counts['L0']} L1a={layer_counts['L1a']} L1b={layer_counts['L1b']} L2={layer_counts['L2']}")
    if oldest:
        print(f"最旧条目: {datetime.fromtimestamp(oldest).strftime('%Y-%m-%d %H:%M:%S')}")
    if newest:
        print(f"最新条目: {datetime.fromtimestamp(newest).strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


def cmd_cache_clear(args) -> int:
    root = args.path or resolve_project_root(__file__)
    cache_path = root / ".agents" / CACHE_PATH
    if cache_path.exists():
        cache_path.unlink()
        print(f"已清除磁盘缓存: {cache_path}")
    else:
        print("磁盘缓存不存在，无需清除")
    return 0


def cmd_benchmark(args) -> int:
    setup_logging(verbose=False)
    root = args.path or resolve_project_root(__file__)
    iterations = args.iterations

    print("=" * 70)
    print("L2 渐进式披露加载器 性能基准测试（P1优化后）")
    print(f"迭代次数: {iterations} | 项目根目录: {root}")
    print("=" * 70)

    test_tasks = [
        ("代码审查", "execution"),
        ("提交代码", "execution"),
        ("复盘项目", "execution"),
        ("绘制mermaid流程图", "execution"),
        ("链接检查", "execution"),
        ("开发功能并测试和审查", "execution"),
    ]

    def _time_load(task_desc: str, stage: str, use_cache: bool, lightweight: bool = False) -> tuple:
        loader = SpecLoader(root, verbose=False, use_disk_cache=use_cache)
        t0 = time.perf_counter()
        if lightweight:
            result = loader.load_for_task_lightweight(task_desc, stage=stage)
        else:
            result = loader.load_for_task(task_desc, stage=stage)
        elapsed = (time.perf_counter() - t0) * 1000
        if use_cache:
            loader.save_cache()
        return elapsed, result.total_chars, result.spec_count, len(result.pending_l2), result.primary_type

    print("\n--- 冷启动测试（清除缓存，每次新建loader，不读磁盘缓存）---")
    cold_times = {task: [] for task, _ in test_tasks}
    for task_desc, stage in test_tasks:
        cache_path = root / ".agents" / CACHE_PATH
        if cache_path.exists():
            cache_path.unlink()
        for i in range(iterations):
            elapsed, chars, count, pending, primary = _time_load(task_desc, stage, use_cache=False)
            cold_times[task_desc].append(elapsed)
            if args.verbose or i == iterations - 1:
                print(f"  冷启动 {task_desc:25s}: {elapsed:7.2f}ms | 文件={count} | 字符={chars:,} | 主类型={primary}")

    print("\n--- 温启动测试（使用磁盘缓存，跨会话复用）---")
    warm_loader = SpecLoader(root, verbose=False, use_disk_cache=True)
    for task_desc, stage in test_tasks:
        warm_loader.load_for_task(task_desc, stage=stage)
    warm_loader.save_cache()

    warm_times = {task: [] for task, _ in test_tasks}
    for task_desc, stage in test_tasks:
        for i in range(iterations):
            loader = SpecLoader(root, verbose=False, use_disk_cache=True)
            t0 = time.perf_counter()
            result = loader.load_for_task(task_desc, stage=stage)
            elapsed = (time.perf_counter() - t0) * 1000
            warm_times[task_desc].append(elapsed)
            loader.save_cache()
            if args.verbose or i == iterations - 1:
                print(f"  温启动 {task_desc:25s}: {elapsed:7.2f}ms | 文件={result.spec_count} | 字符={result.total_chars:,} | "
                      f"命中率={loader.get_cache_stats()['hit_rate']:.0f}%")

    print("\n--- 🚀 轻量模式测试（P1优化：L0+L1a+路由，不读L2内容）---")
    light_times = {task: [] for task, _ in test_tasks}
    for task_desc, stage in test_tasks:
        for i in range(iterations):
            loader = SpecLoader(root, verbose=False, use_disk_cache=True)
            t0 = time.perf_counter()
            result = loader.load_for_task_lightweight(task_desc, stage=stage)
            elapsed = (time.perf_counter() - t0) * 1000
            light_times[task_desc].append(elapsed)
            loader.save_cache()
            if args.verbose or i == iterations - 1:
                print(f"  轻量模式 {task_desc:20s}: {elapsed:7.2f}ms | 文件={result.spec_count}(仅L0+L1a) | "
                      f"待加载L2={len(result.pending_l2)} | 主类型={result.primary_type}")

    print("\n" + "=" * 70)
    print("基准测试结果汇总（单位：毫秒）")
    print("-" * 70)
    print(f"{'任务类型':25s} | {'冷启动':>8s} | {'温启动':>8s} | {'轻量模式':>8s} | {'温/冷':>6s} | {'轻/冷':>6s}")
    print("-" * 70)

    all_cold = []
    all_warm = []
    all_light = []
    for task_desc, _ in test_tasks:
        cold_avg = statistics.mean(cold_times[task_desc])
        warm_avg = statistics.mean(warm_times[task_desc])
        light_avg = statistics.mean(light_times[task_desc])
        speedup_warm = cold_avg / warm_avg if warm_avg > 0 else 0
        speedup_light = cold_avg / light_avg if light_avg > 0 else 0
        all_cold.extend(cold_times[task_desc])
        all_warm.extend(warm_times[task_desc])
        all_light.extend(light_times[task_desc])
        print(f"{task_desc:25s} | {cold_avg:8.2f} | {warm_avg:8.2f} | {light_avg:8.2f} | {speedup_warm:5.1f}x | {speedup_light:5.1f}x")

    print("-" * 70)
    cold_total = statistics.mean(all_cold)
    warm_total = statistics.mean(all_warm)
    light_total = statistics.mean(all_light)
    speedup_warm_total = cold_total / warm_total if warm_total > 0 else 0
    speedup_light_total = cold_total / light_total if light_total > 0 else 0
    improvement_warm = (1 - warm_total / cold_total) * 100
    improvement_light = (1 - light_total / cold_total) * 100
    print(f"{'综合平均':25s} | {cold_total:8.2f} | {warm_total:8.2f} | {light_total:8.2f} | {speedup_warm_total:5.1f}x | {speedup_light_total:5.1f}x")
    print("=" * 70)
    print(f"磁盘缓存加速: {improvement_warm:.1f}%（温启动 vs 冷启动）")
    print(f"🚀 轻量模式加速: {improvement_light:.1f}%（轻量 vs 冷启动，路由判定仅需 {light_total:.2f}ms）")
    print(f"多类型优化: 辅助类型自动跳过roles/角色文件，避免角色冲突")
    print(f"权重匹配: 关键词位置/长度加权，主类型识别准确率提升")

    return 0


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(description="L2 渐进式披露规范加载器")
    subparsers = parser.add_subparsers(dest="command", help="可用子命令")

    p_task = subparsers.add_parser("task", help="按任务描述加载规范")
    p_task.add_argument("task_description", help="任务描述文本")
    p_task.add_argument("--stage", "-s", default="execution",
                        choices=["startup", "planning", "execution", "verification"],
                        help="任务阶段（execution阶段仅加载L1a核心规则）")
    p_task.add_argument("--include-l1b", action="store_true", default=None,
                        help="强制包含L1b索引层（planning阶段默认包含，execution阶段默认不包含）")
    p_task.add_argument("-c", "--content", action="store_true", help="输出规范内容（默认仅输出清单）")
    p_task.add_argument("--max-chars", type=int, default=None, help="L2最大加载字符数")
    p_task.add_argument("--lightweight", "-l", action="store_true", help="轻量模式：仅加载L0+L1a，返回L2路径清单（不读内容）")
    p_task.add_argument("--primary-only", action="store_true", help="仅加载主类型全部L2，辅助类型完全跳过")
    p_task.add_argument("--warn-missing", action="store_true", help="有缺失文件时返回错误码")
    p_task.add_argument("--no-cache", action="store_true", help="不使用磁盘缓存")
    p_task.add_argument("-v", "--verbose", action="store_true", help="输出详细加载日志（到stderr）")
    p_task.add_argument("--path", type=Path, default=None, help="项目根目录路径")

    p_layer = subparsers.add_parser("layer", help="按层加载规范")
    p_layer.add_argument("layer", choices=["L0", "L1a", "L1", "all"], help="加载到指定层")
    p_layer.add_argument("-c", "--content", action="store_true", help="输出规范内容")
    p_layer.add_argument("--no-cache", action="store_true", help="不使用磁盘缓存")
    p_layer.add_argument("-v", "--verbose", action="store_true", help="输出详细加载日志")
    p_layer.add_argument("--path", type=Path, default=None)

    p_list = subparsers.add_parser("list-types", help="列出所有支持的任务类型")

    p_audit = subparsers.add_parser("audit", help="审计所有路由引用的文件是否存在")
    p_audit.add_argument("-v", "--verbose", action="store_true", help="输出每个文件的审计结果")
    p_audit.add_argument("--path", type=Path, default=None)

    p_bench = subparsers.add_parser("benchmark", help="运行性能基准测试")
    p_bench.add_argument("-n", "--iterations", type=int, default=5, help="每个任务的迭代次数")
    p_bench.add_argument("-v", "--verbose", action="store_true", help="输出每次迭代详情")
    p_bench.add_argument("--path", type=Path, default=None)

    p_cache_stats = subparsers.add_parser("cache-stats", help="查看磁盘缓存统计")
    p_cache_stats.add_argument("-v", "--verbose", action="store_true")
    p_cache_stats.add_argument("--path", type=Path, default=None)

    p_cache_clear = subparsers.add_parser("cache-clear", help="清除磁盘缓存")
    p_cache_clear.add_argument("--path", type=Path, default=None)

    args = parser.parse_args()

    cmd_map = {
        "task": cmd_task,
        "layer": cmd_layer,
        "list-types": cmd_list_types,
        "audit": cmd_audit,
        "benchmark": cmd_benchmark,
        "cache-stats": cmd_cache_stats,
        "cache-clear": cmd_cache_clear,
    }

    if not args.command:
        parser.print_help()
        return 1

    return cmd_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
