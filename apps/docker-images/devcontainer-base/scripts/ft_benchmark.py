#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""free-threading（nogil）多线程基准的可复用 Python 封装。

ft-benchmark.sh 的等价 Python 实现：既提供可直接 import 的函数，
也提供命令行入口。零第三方依赖（仅标准库）。

作为库使用（其他项目里）：

    from ft_benchmark import run_ft_benchmark

    # 在 Docker 镜像里跑（容器隔离，默认）
    res = run_ft_benchmark(image="devcontainer-base:conda-llvm-latest",
                           benchmark_range=500_000, min_speedup=2.0)
    print(res.best_speedup, res.passed)      # 5.06 True

    # 在当前解释器本地跑（image=None / ""）
    res = run_ft_benchmark(image=None, benchmark_range=200_000)

    # 静默判定（不打印、不落日志）
    res = run_ft_benchmark(image="...", quiet=True, log_path=None)

作为 CLI 使用（等价于 ft-benchmark.sh）：

    python ft_benchmark.py --image devcontainer-base:conda-llvm-latest --range 500000
    python ft_benchmark.py --local --range 200000 --min-speedup 2.0 --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_IMAGE = "devcontainer-base:conda-llvm-latest"
DEFAULT_LOG = Path("benchmarks") / "ft-benchmark-history.jsonl"
MAIN_PYTHON = "/opt/conda/envs/main/bin/python"  # 镜像内 main 环境（free-threading）
# 匹配 free_threading_demo.py 的结果行："  ✔ 8 threads   0.044s   5.06x 加速"
LINE_RE = re.compile(r"^\s*\S+\s+(.+?)\s+([\d.]+)\s*s\s+([\d.]+)\s*x", re.M)
BEST_RE = re.compile(r"最佳多线程加速比[:：]\s*([\d.]+)\s*x")


@dataclass
class BenchmarkResult:
    """一次基准运行的解析结果。"""
    mode: str = "docker"                      # docker | local
    image: str = ""                           # 镜像名（local 模式为空）
    benchmark_range: int = 0
    speedups: dict = field(default_factory=dict)   # 标签 -> 加速比
    best_speedup: float = 0.0
    threshold: float = 2.0
    passed: bool = False
    raw_output: str = ""
    log_path: str = ""
    telemetry: dict = field(default_factory=dict)   # 探针埋点（线程/进程启动耗时等）

    def to_dict(self) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "mode": self.mode, "image": self.image or "-",
            "benchmark_range": self.benchmark_range,
            "result": "pass" if self.passed else "fail",
            "best_speedup": round(self.best_speedup, 2),
            "threshold": self.threshold,
            "speedups": {k: float(v) for k, v in self.speedups.items()},
            "telemetry": self.telemetry or None,
        }


def _parse(output: str) -> tuple[dict, float]:
    """解析 free_threading_demo.py 的输出，返回 (各项加速比, 最佳加速比)。"""
    speedups = {m.group(1).strip(): float(m.group(3)) for m in LINE_RE.finditer(output)}
    best = 0.0
    if (m := BEST_RE.search(output)):
        best = float(m.group(1))
    elif speedups:
        # 兜底：取线程类条目的最大值（排除进程池对照）
        best = max((v for k, v in speedups.items() if "Process" not in k), default=0.0)
    return speedups, best


# ─── 日志埋点：线程/进程池启动耗时与结果序列化大小 ────────────────────────

def _probe_task(n: int) -> tuple[float, int]:
    """探针负载：返回 (任务开始时刻, 计算结果)。模块级顶层函数，保证可 pickle。"""
    t = time.perf_counter()
    x = sum(1 for i in range(2, n) if all(i % j for j in range(2, int(i ** 0.5) + 1)))
    return t, x


def probe_pool_overhead(workers: int = 8, n: int = 50_000) -> dict:
    """实测每个线程/进程 worker 的启动延迟与结果序列化大小（日志埋点）。

    - pool_create_seconds : Executor 构造耗时（ProcessPool 为惰性 spawn，构造极快）
    - spawn_lag_seconds   : 每个 worker 从 submit 到任务真正开跑的延迟；
                            进程池该值含 fork/spawn 成本，即真实的"启动耗时"
    - result_bytes        : 单个 worker 结果的 pickle 序列化大小（进程池往返成本）
    """
    import pickle
    import multiprocessing as mp
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

    def _run(factory, **kw) -> dict:
        t_create = time.perf_counter()
        with factory(workers, **kw) as ex:
            create_s = time.perf_counter() - t_create
            t_submit = time.perf_counter()
            futs = [ex.submit(_probe_task, n) for _ in range(workers)]
            results = [f.result() for f in futs]
        lags = [round(t - t_submit, 6) for t, _ in results]
        sample = results[0][1]
        return {
            "pool_create_seconds": round(create_s, 6),
            "spawn_lag_seconds": lags,                    # 每个 worker 一项
            "spawn_lag_avg": round(sum(lags) / len(lags), 6),
            "result_bytes": len(pickle.dumps(sample)),    # 结果序列化大小
            "result_type": type(sample).__name__,
        }

    out: dict = {"workers": workers, "payload": n,
                 "pickle_protocol": pickle.HIGHEST_PROTOCOL}
    out["thread"] = _run(ThreadPoolExecutor)
    # fork 优先（进程启动最快）；平台不支持时回退默认 start_method
    method = "fork" if "fork" in mp.get_all_start_methods() else mp.get_start_method()
    out["process"] = _run(ProcessPoolExecutor, mp_context=mp.get_context(method))
    out["process"]["start_method"] = method
    return out


def _print_telemetry(t: dict) -> None:
    """打印埋点摘要（quiet=False 时由 run_ft_benchmark 调用）。"""
    if not t:
        return
    if "error" in t:
        print(f"[probe] 探针失败（不影响基准结果）: {t['error']}")
        return
    for kind in ("thread", "process"):
        d = t.get(kind) or {}
        if not d:
            continue
        lags = d.get("spawn_lag_seconds") or [0.0]
        print(f"[probe] {kind}({d.get('start_method', '-')}): x{t['workers']} "
              f"create={d['pool_create_seconds'] * 1000:7.2f}ms "
              f"lag[min={min(lags) * 1000:.1f} avg={d['spawn_lag_avg'] * 1000:.1f} "
              f"max={max(lags) * 1000:.1f}]ms "
              f"result={d['result_bytes']}B")


def _run_probe(local: bool, image: str, docker_cmd: str, timeout: float) -> dict:
    """在目标环境（本机或容器）运行探针，返回埋点 dict；失败不抛出。"""
    try:
        if local:
            return probe_pool_overhead()
        probe_code = ("import sys, json; sys.path.insert(0, '/tmp'); "
                      "import ft_benchmark as fb; "
                      "print(json.dumps(fb.probe_pool_overhead()))")
        cmd = [docker_cmd, "run", "--rm",
               "-v", f"{Path(__file__).resolve()}:/tmp/ft_benchmark.py:ro",
               "--entrypoint", MAIN_PYTHON, str(image), "-c", probe_code]
        pr = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                            encoding="utf-8", errors="replace")
        if pr.returncode != 0:
            return {"error": (pr.stderr or pr.stdout)[-300:]}
        return json.loads(pr.stdout.strip().splitlines()[-1])
    except Exception as e:  # 探针是可观测性增强，失败不影响基准主流程
        return {"error": repr(e)}


def run_ft_benchmark(
    image: str | None = DEFAULT_IMAGE,
    benchmark_range: int = 500_000,
    min_speedup: float = 2.0,
    *,
    docker_cmd: str = "docker",
    log_path: str | Path | None = DEFAULT_LOG,
    quiet: bool = False,
    timeout: float = 600.0,
    probe: bool = True,
) -> BenchmarkResult:
    """运行 free-threading 多线程基准并解析结果。

    参数：
        image          目标 Docker 镜像；传 None 或 "" 则用当前解释器本地运行
        benchmark_range 素数上界（负载规模，demo 的 BENCHMARK_RANGE）
        min_speedup    通过阈值（最佳加速比 ≥ 该值判 pass）
        docker_cmd     docker 可执行文件（默认 "docker"）
        log_path       JSONL 历史日志路径；None 表示不落盘
        quiet          为 True 时不打印过程输出
        timeout        子进程超时（秒）
        probe          为 True 时运行埋点探针：记录每个线程/进程 worker 的
                       启动耗时（spawn lag）与结果序列化大小（pickle 字节），
                       结果写入 BenchmarkResult.telemetry 与 JSONL 日志

    返回 BenchmarkResult（含 speedups 字典 / best_speedup / passed / telemetry）。
    抛出 RuntimeError（镜像/脚本运行失败）、subprocess.TimeoutExpired。
    """
    demo = Path(__file__).resolve().parent.parent / "examples" / "free_threading_demo.py"
    if not demo.exists():
        raise RuntimeError(f"找不到基准脚本: {demo}")

    env = {**os.environ, "BENCHMARK_RANGE": str(benchmark_range)}
    local = not image
    if local:
        cmd = [sys.executable, str(demo)]
        mode = "local"
    else:
        cmd = [docker_cmd, "run", "--rm",
               "-e", f"BENCHMARK_RANGE={benchmark_range}",
               "-v", f"{demo}:/tmp/ft_demo.py:ro",
               "--entrypoint", MAIN_PYTHON,
               str(image), "/tmp/ft_demo.py"]
        mode = "docker"

    if not quiet:
        print(f"[ft-benchmark] mode={mode} range={benchmark_range} "
              f"target={image or sys.executable} threshold={min_speedup}x")
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, env=env, encoding="utf-8", errors="replace")
    output = proc.stdout + proc.stderr
    if proc.returncode != 0:
        tail = "\n".join(output.splitlines()[-8:])
        raise RuntimeError(f"基准运行失败 (exit={proc.returncode}):\n{tail}")

    speedups, best = _parse(output)
    res = BenchmarkResult(mode=mode, image=image or "", benchmark_range=benchmark_range,
                          speedups=speedups, best_speedup=best,
                          threshold=min_speedup, passed=best >= min_speedup,
                          raw_output=output)
    if not quiet:
        for label, sp in speedups.items():
            print(f"  {label:32s} {sp:6.2f}x")
        verdict = "PASS" if res.passed else "FAIL"
        print(f"[ft-benchmark] best={best:.2f}x threshold={min_speedup}x -> {verdict}")

    # 日志埋点：线程/进程池启动耗时 + 结果序列化大小（失败不影响基准）
    if probe:
        res.telemetry = _run_probe(local, image or "", docker_cmd, timeout)
        if not quiet:
            _print_telemetry(res.telemetry)

    if log_path is not None:
        lp = Path(log_path)
        lp.parent.mkdir(parents=True, exist_ok=True)
        with lp.open("a", encoding="utf-8") as f:
            f.write(json.dumps(res.to_dict(), ensure_ascii=False) + "\n")
        res.log_path = str(lp)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="free-threading 基准（ft-benchmark.sh 的 Python 封装）")
    ap.add_argument("--image", default=DEFAULT_IMAGE,
                    help=f"目标镜像（默认 {DEFAULT_IMAGE}；传空字符串或 --local 则本地运行）")
    ap.add_argument("--local", action="store_true", help="用当前解释器本地运行（等价 --image ''）")
    ap.add_argument("--range", type=int, default=500_000, help="素数上界（默认 500000）")
    ap.add_argument("--min-speedup", type=float, default=2.0, help="通过阈值（默认 2.0x）")
    ap.add_argument("--quick", action="store_true",
                    help="快速模式：500K 素数 / 3.0x 阈值（CI 默认，覆盖 --range/--min-speedup）")
    ap.add_argument("--full", action="store_true",
                    help="完整模式：2M 素数 / 4.0x 阈值（高加速比验证，覆盖 --range/--min-speedup）")
    ap.add_argument("--log", default=str(DEFAULT_LOG), help="JSONL 日志路径（默认 %(default)s）")
    ap.add_argument("--no-log", action="store_true", help="不写日志")
    ap.add_argument("--no-probe", action="store_true",
                    help="跳过埋点探针（默认会测量线程/进程启动耗时与结果序列化大小）")
    ap.add_argument("--json", action="store_true", help="结果以 JSON 输出")
    args = ap.parse_args()

    if args.quick and args.full:
        ap.error("--quick 与 --full 互斥")
    if args.quick:
        args.range, args.min_speedup = 500_000, 3.0
    elif args.full:
        args.range, args.min_speedup = 2_000_000, 4.0

    try:
        res = run_ft_benchmark(
            image="" if args.local else args.image,
            benchmark_range=args.range, min_speedup=args.min_speedup,
            log_path=None if args.no_log else (args.log or None),
            probe=not args.no_probe,
        )
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as e:
        print(f"[ft-benchmark] ERROR: {e}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))
    return 0 if res.passed else 1


if __name__ == "__main__":
    sys.exit(main())
