"""Router 路由延迟自动化压测脚本。

针对 multi-model-routing-plan §3.2 的风险2（路由延迟），
量化路由判定（route()）的额外开销，并对比直通模式 vs 正常模式。

量测维度：
- 路由判定延迟：route() 纯决策耗时（不含模型调用）
- 端到端延迟：route() + 模拟模型推理耗时（可选 --simulate-model）
- 吞吐量：每秒可处理的路由请求数

用法：
    python tests/stress_router_latency.py                      # 默认 2000 次，单线程
    python tests/stress_router_latency.py -n 5000 --concurrency 8
    python tests/stress_router_latency.py --simulate-model 50  # 模拟 50ms 模型推理，测端到端
    python tests/stress_router_latency.py --report-only        # 仅打印报告，不重新压测

输出：统计直通/正常模式的路由判定延迟分位，对比路由开销，并生成 Docs 报告。
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from workspace import Workspace, WorkspaceRegistry
from boundary import BoundaryChecker
from router import ModelRouter, build_default_router

# 任务池：覆盖四种策略命中场景（敏感/复杂/简单查询/兜底）
TASK_POOL: List[Tuple[str, str, float]] = [
    ("处理一份客户财务票据", "", 0.9),      # 敏感 → 数据边界策略
    ("分析一段复杂代码逻辑", "", 0.95),     # 非敏感+高复杂度 → 复杂度策略
    ("查询一下当前时间", "query", 0.1),     # 简单查询 → 成本策略
    ("普通任务，无特殊属性", "", 0.3),       # 兜底策略
]


def build_fixture() -> Tuple[WorkspaceRegistry, BoundaryChecker, ModelRouter, ModelRouter]:
    """构建正常模式与直通模式的路由器夹具。"""
    registry = WorkspaceRegistry()
    ws = Workspace("finance", "财务工作区", model="local-model", private=True)
    registry.register(ws)

    boundary = BoundaryChecker()
    boundary.set_allowed_models("finance", ["local-model", "strong-model", "cheap-model"])

    normal_router = build_default_router(registry, boundary)
    direct_router = ModelRouter(registry, boundary, direct_mode=True)
    return registry, boundary, normal_router, direct_router


def _pick_task(index: int) -> Tuple[str, str, float]:
    """按 index 轮询任务池，保证各策略场景均匀覆盖。"""
    return TASK_POOL[index % len(TASK_POOL)]


def _routing_call(router: ModelRouter, index: int) -> float:
    """单次路由判定，返回耗时（秒）。"""
    task, task_type, complexity = _pick_task(index)
    start = time.perf_counter()
    router.route("finance", task, task_type=task_type, complexity=complexity)
    return time.perf_counter() - start


def _model_aware_call(router: ModelRouter, index: int, model_latency_ms: int) -> float:
    """单次路由 + 模拟模型推理，返回端到端耗时（秒）。"""
    task, task_type, complexity = _pick_task(index)
    start = time.perf_counter()
    router.route("finance", task, task_type=task_type, complexity=complexity)
    # 模拟模型推理延迟（本地/远程统一按固定值模拟）
    time.sleep(model_latency_ms / 1000.0)
    return time.perf_counter() - start


def _run_benchmark(
    router: ModelRouter,
    iterations: int,
    concurrency: int,
    model_latency_ms: int,
) -> List[float]:
    """并发执行压测，返回耗时样本列表。"""
    if model_latency_ms > 0:
        worker = lambda i: _model_aware_call(router, i, model_latency_ms)
    else:
        worker = lambda i: _routing_call(router, i)

    if concurrency <= 1:
        return [worker(i) for i in range(iterations)]

    samples: List[float] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(worker, i) for i in range(iterations)]
        for fut in concurrent.futures.as_completed(futures):
            samples.append(fut.result())
    return samples


def _percentile(sorted_samples: List[float], pct: float) -> float:
    """计算分位数（样本须已排序）。"""
    if not sorted_samples:
        return 0.0
    k = (len(sorted_samples) - 1) * pct
    lo = int(k)
    hi = min(lo + 1, len(sorted_samples) - 1)
    frac = k - lo
    return sorted_samples[lo] * (1 - frac) + sorted_samples[hi] * frac


def _summarize(samples: List[float]) -> Dict[str, float]:
    """生成延迟统计摘要。"""
    if not samples:
        return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "stdev": 0.0, "max": 0.0}
    s = sorted(samples)
    return {
        "mean": statistics.mean(samples),
        "p50": _percentile(s, 0.50),
        "p95": _percentile(s, 0.95),
        "p99": _percentile(s, 0.99),
        "stdev": statistics.stdev(samples),
        "max": max(samples),
    }


def _format_ms(sec: float) -> str:
    """秒转毫秒字符串。"""
    return f"{sec * 1000:.3f} ms"


def run_stress(
    iterations: int = 2000,
    concurrency: int = 1,
    model_latency_ms: int = 0,
) -> Dict[str, Dict[str, float]]:
    """执行压测，返回 {mode: stats} 字典。"""
    registry, boundary, normal_router, direct_router = build_fixture()

    print("=" * 64)
    print("Router 路由延迟压测")
    print(f"  迭代次数: {iterations} | 并发: {concurrency} | 模拟模型延迟: {model_latency_ms}ms")
    print("=" * 64)

    # 预热（消除首次导入/缓存开销）
    for _ in range(100):
        _routing_call(normal_router, 0)

    print("\n[1/2] 正常模式（完整策略评估）...")
    normal_samples = _run_benchmark(normal_router, iterations, concurrency, model_latency_ms)

    print("[2/2] 直通模式（跳过策略评估）...")
    direct_samples = _run_benchmark(direct_router, iterations, concurrency, model_latency_ms)

    normal_stats = _summarize(normal_samples)
    direct_stats = _summarize(direct_samples)

    return {
        "normal": normal_stats,
        "direct": direct_stats,
        "_meta": {
            "iterations": iterations,
            "concurrency": concurrency,
            "model_latency_ms": model_latency_ms,
        },
    }


def print_report(results: Dict[str, Dict[str, float]]) -> None:
    """打印压测报告。"""
    normal = results["normal"]
    direct = results["direct"]
    meta = results["_meta"]

    print("\n" + "=" * 64)
    print("压测报告（路由判定延迟）")
    print("=" * 64)
    print(f"{'指标':<12}{'正常模式':>16}{'直通模式':>16}")
    print("-" * 44)
    for key in ("mean", "p50", "p95", "p99", "max"):
        print(f"{key:<12}{_format_ms(normal[key]):>16}{_format_ms(direct[key]):>16}")

    # 路由判定开销占比
    overhead_us = (normal["mean"] - direct["mean"]) * 1_000_000
    print("-" * 44)
    print(f"路由判定平均额外开销: {overhead_us:.2f} us/次")

    if meta["model_latency_ms"] > 0:
        model_ms = meta["model_latency_ms"]
        routing_ratio = (normal["mean"] - direct["mean"]) * 1000 / model_ms * 100
        print(f"路由判定在端到端({model_ms}ms)中的占比: {routing_ratio:.3f}%")

    throughput_normal = 1.0 / normal["mean"]
    if meta["model_latency_ms"] > 0:
        print(f"正常模式吞吐: {throughput_normal:.0f} QPS（含模拟模型延迟 {meta['model_latency_ms']}ms）")
    else:
        print(f"正常模式吞吐: {throughput_normal:.0f} QPS（路由判定）")

    # 结论：基于路由判定额外开销（normal - direct），而非绝对均值
    # （mean 会受模拟模型延迟主导，绝对均值无法反映路由判定本身的开销）
    print("\n结论:")
    if overhead_us < 100:
        print(f"  ✓ 路由判定额外开销 {overhead_us:.2f}us/次，为纯内存决策，开销可忽略")
    elif overhead_us < 1000:
        print(f"  ✓ 路由判定额外开销 {overhead_us:.2f}us/次，开销微小，正常模式可接受")
    else:
        print(f"  ✗ 路由判定额外开销 {overhead_us:.2f}us/次 偏高，建议启用直通模式或优化策略评估")

    print("\n写入报告: docs/latency-baseline-report.md")


def write_report(results: Dict[str, Dict[str, float]]) -> None:
    """将压测结果写入 docs/latency-baseline-report.md。"""
    normal = results["normal"]
    direct = results["direct"]
    meta = results["_meta"]

    overhead_us = (normal["mean"] - direct["mean"]) * 1_000_000

    lines = [] if __name__ != "__main__" else []
    lines = [
        "# Router 路由延迟压测基线报告",
        "",
        "> 由 `tests/stress_router_latency.py` 自动生成。",
        f"> 日期：{time.strftime('%Y-%m-%d %H:%M:%S')} | 迭代：{meta['iterations']} | 并发：{meta['concurrency']} | 模拟模型延迟：{meta['model_latency_ms']}ms",
        "",
        "## 1. 路由判定延迟分位",
        "",
        "| 指标 | 正常模式 | 直通模式 |",
        "|------|---------|---------|",
        f"| mean | {_format_ms(normal['mean'])} | {_format_ms(direct['mean'])} |",
        f"| p50 | {_format_ms(normal['p50'])} | {_format_ms(direct['p50'])} |",
        f"| p95 | {_format_ms(normal['p95'])} | {_format_ms(direct['p95'])} |",
        f"| p99 | {_format_ms(normal['p99'])} | {_format_ms(direct['p99'])} |",
        f"| max | {_format_ms(normal['max'])} | {_format_ms(direct['max'])} |",
        "",
        f"**路由判定平均额外开销**：{overhead_us:.2f} us/次",
        "",
        "## 2. 结论",
        "",
        "对比正常模式与直通模式的路由判定延迟，判断路由是否值得。",
        "",
    ]
    if meta["model_latency_ms"] > 0:
        model_ms = meta["model_latency_ms"]
        routing_ratio = (normal["mean"] - direct["mean"]) * 1000 / model_ms * 100
        lines.append(f"- 路由判定在端到端（{model_ms}ms 模型推理）中的占比：{routing_ratio:.3f}%")
        lines.append("")
    lines.append(f"- 路由判定平均额外开销：{overhead_us:.2f} us/次")
    lines.append("")

    report_path = Path(__file__).resolve().parent.parent / "docs" / "latency-baseline-report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"已写入 {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Router 路由延迟压测")
    parser.add_argument("-n", "--iterations", type=int, default=2000, help="迭代次数（默认 2000）")
    parser.add_argument("--concurrency", type=int, default=1, help="并发线程数（默认 1）")
    parser.add_argument("--simulate-model", type=int, default=0, help="模拟模型推理延迟（ms，默认 0 仅测路由判定）")
    parser.add_argument("--report-only", action="store_true", help="仅打印报告，不重新压测")
    args = parser.parse_args()

    if args.report_only:
        print("未提供上次结果缓存，请直接运行压测生成本期报告。")
        return

    results = run_stress(
        iterations=args.iterations,
        concurrency=args.concurrency,
        model_latency_ms=args.simulate_model,
    )
    print_report(results)
    write_report(results)


if __name__ == "__main__":
    main()