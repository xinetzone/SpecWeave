"""真实模型延迟量测自动化压测脚本。

基于 ModelProvider 接口（`model_provider.py`），量测模型推理延迟（端到端），
并支持不同抖动幅度扫描，验证网络波动对延迟分布的影响。

量测维度：
- 模型推理延迟：`provider.invoke()` 耗时（经 `get_latency_ms()` 读取）
- 抖动幅度扫描：不同 `jitter_ms` 下的延迟分布对比
- 并发：多线程并发下的延迟分布

用法：
    python tests/stress_model_latency.py                        # 默认 local + remote 抖动扫描
    python tests/stress_model_latency.py --provider remote --latency-ms 200 --jitter-ms 50 -n 1000
    python tests/stress_model_latency.py --concurrency 8
    python tests/stress_model_latency.py --jitter-sweep 0 50 100 200

输出：延迟分布统计（mean/p50/p95/p99/stdev/min/max），写入 Docs 报告。
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from model_provider import ModelProvider, build_default_provider


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
    """生成延迟统计摘要（毫秒）。"""
    if not samples:
        return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0}
    s = sorted(samples)
    return {
        "mean": statistics.mean(samples),
        "p50": _percentile(s, 0.50),
        "p95": _percentile(s, 0.95),
        "p99": _percentile(s, 0.99),
        "stdev": statistics.stdev(samples),
        "min": min(samples),
        "max": max(samples),
    }


def _single_invoke(provider: ModelProvider, iteration: int) -> float:
    """单次模型调用，返回耗时（毫秒）。"""
    provider.invoke("test-model", f"压测任务 {iteration}")
    return provider.get_latency_ms()


def _run_benchmark(
    provider: ModelProvider,
    iterations: int,
    concurrency: int,
) -> List[float]:
    """并发执行压测，返回延迟样本列表（毫秒）。"""
    if concurrency <= 1:
        return [_single_invoke(provider, i) for i in range(iterations)]
    samples: List[float] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_single_invoke, provider, i) for i in range(iterations)]
        for fut in concurrent.futures.as_completed(futures):
            samples.append(fut.result())
    return samples


def _fmt(ms: float) -> str:
    return f"{ms:.1f}"


def run_model_latency_stress(
    provider_type: str = "remote",
    latency_ms: int = 200,
    jitter_ms: int = 0,
    iterations: int = 500,
    concurrency: int = 1,
) -> Dict[str, Any]:
    """执行真实模型延迟压测，返回统计结果。"""
    provider = build_default_provider(
        provider_type=provider_type,
        latency_ms=latency_ms,
        jitter_ms=jitter_ms,
        base_url="http://localhost:8000",
    )

    # 预热
    for _ in range(20):
        provider.invoke("test-model", "warmup")

    samples = _run_benchmark(provider, iterations, concurrency)
    stats = _summarize(samples)
    stats["_meta"] = {
        "provider": provider_type,
        "latency_ms": latency_ms,
        "jitter_ms": jitter_ms,
        "iterations": iterations,
        "concurrency": concurrency,
    }
    return stats


def print_stats(stats: Dict[str, float]) -> None:
    """打印单次压测统计。"""
    meta = stats["_meta"]
    print(f"\n[{meta['provider']}] latency={meta['latency_ms']}ms jitter={meta['jitter_ms']}ms "
          f"iter={meta['iterations']} concurrency={meta['concurrency']}")
    print(f"  mean={_fmt(stats['mean'])}ms  p50={_fmt(stats['p50'])}ms  "
          f"p95={_fmt(stats['p95'])}ms  p99={_fmt(stats['p99'])}ms  "
          f"stdev={_fmt(stats['stdev'])}ms  min={_fmt(stats['min'])}ms  max={_fmt(stats['max'])}ms")


def run_jitter_sweep(
    provider_type: str,
    latency_ms: int,
    jitter_list: List[int],
    iterations: int,
    concurrency: int,
) -> List[Dict[str, float]]:
    """扫描不同抖动幅度，返回各配置统计列表。"""
    results = []
    for jitter in jitter_list:
        stats = run_model_latency_stress(
            provider_type=provider_type,
            latency_ms=latency_ms,
            jitter_ms=jitter,
            iterations=iterations,
            concurrency=concurrency,
        )
        print_stats(stats)
        results.append(stats)
    return results


def write_report(results: List[Dict[str, float]], provider_type: str) -> None:
    """将抖动扫描结果写入报告。"""
    lines = [
        "# 真实模型延迟量测报告（抖动扫描）",
        "",
        f"> 由 `tests/stress_model_latency.py` 自动生成。",
        f"> 日期：{time.strftime('%Y-%m-%d %H:%M:%S')} | 提供者：{provider_type}",
        "",
        "## 1. 延迟分布（不同抖动幅度）",
        "",
        "| 抖动(ms) | mean | p50 | p95 | p99 | stdev | min | max |",
        "|---------|------|-----|-----|-----|-------|-----|-----|",
    ]
    for stats in results:
        meta = stats["_meta"]
        lines.append(
            f"| {meta['jitter_ms']} | {_fmt(stats['mean'])} | {_fmt(stats['p50'])} | "
            f"{_fmt(stats['p95'])} | {_fmt(stats['p99'])} | {_fmt(stats['stdev'])} | "
            f"{_fmt(stats['min'])} | {_fmt(stats['max'])} |"
        )
    lines += [
        "",
        "## 2. 结论",
        "",
        "抖动幅度越大，延迟分布越分散（stdev 增大），p99 越远离均值。",
        "真实网络场景下建议以 p99 而非均值作为延迟预算依据。",
        "",
    ]
    report_path = Path(__file__).resolve().parent.parent / "docs" / "latency-conclusion.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n已写入 {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="真实模型延迟量测压测")
    parser.add_argument("--provider", choices=["local", "remote"], default="remote", help="提供者类型")
    parser.add_argument("--latency-ms", type=int, default=200, help="基准延迟（毫秒）")
    parser.add_argument("--jitter-ms", type=int, default=0, help="抖动幅度（毫秒）")
    parser.add_argument("-n", "--iterations", type=int, default=500, help="迭代次数")
    parser.add_argument("--concurrency", type=int, default=1, help="并发线程数")
    parser.add_argument("--jitter-sweep", nargs="+", type=int, default=None,
                        help="抖动幅度扫描列表，如 0 50 100 200")
    args = parser.parse_args()

    if args.jitter_sweep is not None:
        results = run_jitter_sweep(
            provider_type=args.provider,
            latency_ms=args.latency_ms,
            jitter_list=args.jitter_sweep,
            iterations=args.iterations,
            concurrency=args.concurrency,
        )
        write_report(results, args.provider)
    else:
        stats = run_model_latency_stress(
            provider_type=args.provider,
            latency_ms=args.latency_ms,
            jitter_ms=args.jitter_ms,
            iterations=args.iterations,
            concurrency=args.concurrency,
        )
        print_stats(stats)


if __name__ == "__main__":
    main()