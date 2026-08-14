#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nogil 开发工具箱 —— 从 nogil_kernel_template.ipynb 提取的可复用库模块。

覆盖 free-threading（Python 3.14t）开发环境的四类高频操作：
  1. 环境自检        env_report() / format_env_report()
  2. GIL 状态诊断    diagnose()（子进程调用同目录 check_gil_state.py）
  3. kernel 注册     register_nogil_kernel()（幂等，env PYTHON_GIL=0）
  4. 性能测量        quick_thread_scaling() / pool_compare() / PoolProbe

零第三方依赖（register_nogil_kernel 内部延迟导入 jupyter_client）。

用法（任意项目里）：

    from nogil_kit import env_report, diagnose, register_nogil_kernel, PoolProbe

    print(format_env_report(env_report()))
    diagnose()                          # GIL 诊断，退出码 0=健康 1=被拉起 2=非ft构建
    register_nogil_kernel()             # 注册 "Python 3.14t (nogil)" kernel

    sp = quick_thread_scaling(range_=200_000)   # {"1": 1.0, "2": 2.3, ...}
    cmp = pool_compare(n=3_000_000, workers=8)  # ThreadPool vs ProcessPool 对照

    probe = PoolProbe(workers=8)               # 池启动开销诊断工具类
    print(probe.format_report())               # 线程/进程启动延迟 + 序列化大小
"""

from __future__ import annotations

import json
import os
import pickle
import subprocess
import sys
import sysconfig
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

__all__ = [
    "env_report", "format_env_report", "locate_check_script", "diagnose",
    "register_nogil_kernel", "count_primes", "quick_thread_scaling",
    "pool_compare", "PoolProbe",
]

_SCRIPTS_DIR = Path(__file__).resolve().parent


# ─── 1. 环境自检 ────────────────────────────────────────────────────────────

def env_report() -> dict:
    """采集当前解释器的 free-threading 环境信息。"""
    return {
        "python_version": sys.version.split()[0],
        "executable": sys.executable,
        "free_threading": bool(sysconfig.get_config_var("Py_GIL_DISABLED")),
        "gil_enabled": sys._is_gil_enabled(),
        "cpu_count": os.cpu_count(),
        "PYTHON_GIL": os.environ.get("PYTHON_GIL", "(未设)"),
    }


def format_env_report(r: dict) -> str:
    """把 env_report() 结果渲染为可读文本。"""
    return (
        f"Python      : {r['python_version']}\n"
        f"解释器      : {r['executable']}\n"
        f"构建        : {'free-threading (cp314t)' if r['free_threading'] else '常规 GIL 构建'}\n"
        f"GIL 状态    : {'已启用' if r['gil_enabled'] else '禁用（nogil 生效）'}\n"
        f"CPU 核心    : {r['cpu_count']}\n"
        f"PYTHON_GIL  : {r['PYTHON_GIL']}"
    )


# ─── 2. GIL 状态诊断（复用 check_gil_state.py）─────────────────────────────

def locate_check_script(extra_paths=()) -> Path | None:
    """定位 check_gil_state.py：同目录 → 仓库 scripts/ → 镜像内 → 用户追加。"""
    candidates = [
        _SCRIPTS_DIR / "check_gil_state.py",
        Path("scripts/check_gil_state.py"),
        Path("../scripts/check_gil_state.py"),
        Path("/usr/local/bin/check_gil_state.py"),
        *(Path(p) for p in extra_paths),
    ]
    return next((p for p in candidates if p.exists()), None)


def diagnose(extra_paths=(), args: list[str] | None = None) -> int:
    """在子进程中运行 GIL 状态诊断（避免 argparse 解析到宿主的启动参数）。

    返回退出码：0=GIL 禁用(健康) 1=GIL 被迫启用 2=非 free-threading 构建。
    """
    script = locate_check_script(extra_paths)
    if script is None:
        print("[!] 未找到 check_gil_state.py —— 从仓库目录运行或传入 extra_paths")
        return 127
    print(f"[i] 诊断脚本: {script}")
    r = subprocess.run([sys.executable, str(script), *(args or [])])
    return r.returncode


# ─── 3. nogil kernel 注册 ──────────────────────────────────────────────────

def register_nogil_kernel(name: str = "nogil",
                          display: str = "Python 3.14t (nogil)",
                          gil_env: str = "0",
                          python: str | None = None) -> tuple[str, bool]:
    """幂等注册一个 PYTHON_GIL=0 的 Jupyter kernelspec。

    返回 (spec_dir, created)。注意：PYTHON_GIL 只设置初始状态，
    import 未声明 Py_mod_gil 的模块仍会在运行时拉起 GIL。
    """
    from jupyter_client.kernelspec import KernelSpecManager  # 延迟导入

    ksm = KernelSpecManager()
    specs = ksm.get_all_specs()
    if name in specs:
        return specs[name]["spec_dir"], False
    with tempfile.TemporaryDirectory() as td:
        spec = {
            "argv": [python or sys.executable, "-m", "ipykernel_launcher",
                     "-f", "{connection_file}"],
            "display_name": display,
            "language": "python",
            "env": {"PYTHON_GIL": gil_env},
        }
        with open(f"{td}/kernel.json", "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2)
        ksm.install_kernel_spec(td, name, user=True)
    return str(ksm.get_all_specs()[name]["spec_dir"]), True


# ─── 4. 性能测量 ───────────────────────────────────────────────────────────

def count_primes(n: int) -> int:
    """纯 Python CPU 密集负载：统计 [2, n) 内素数个数。"""
    return sum(1 for i in range(2, n)
               if all(i % j for j in range(2, int(i ** 0.5) + 1)))


def quick_thread_scaling(range_: int = 200_000,
                         workers: tuple[int, ...] = (2, 4, 8)) -> dict:
    """nogil 线程扩展性快测：总工作量恒定（range_ 均分给各 worker）。

    返回 {"1": 1.0, "2": 加速比, ...}。GIL 被拉起时结果退化为 ~1x。
    """
    t0 = time.perf_counter(); count_primes(range_)
    base = time.perf_counter() - t0
    out = {"1": 1.0, "_base_seconds": round(base, 4)}
    for w in workers:
        t0 = time.perf_counter()
        with ThreadPoolExecutor(w) as ex:
            list(ex.map(count_primes, [range_ // w] * w))
        out[str(w)] = round(base / (time.perf_counter() - t0), 2)
    return out


def _heavy(n: int) -> int:
    """进程池对照负载（模块级顶层函数，保证可 pickle）。"""
    x = 0
    for i in range(n):
        x += i * i
    return x


def pool_compare(n: int = 3_000_000, workers: int = 8,
                 mp_method: str = "fork") -> dict:
    """ThreadPool vs ProcessPool 对照（同负载同并发）。

    注意：3.14 起 Linux 默认 forkserver，Jupyter 单元格函数不可再导入，
    故默认显式使用 fork 上下文。
    """
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor

    ctx = mp.get_context(mp_method)
    t0 = time.perf_counter()
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(_heavy, [n] * workers))
    dt_thread = time.perf_counter() - t0
    t0 = time.perf_counter()
    with ProcessPoolExecutor(workers, mp_context=ctx) as ex:
        list(ex.map(_heavy, [n] * workers, chunksize=1))
    dt_proc = time.perf_counter() - t0
    return {
        "start_method_default": mp.get_start_method(),
        "pool_method": mp_method,
        "workers": workers,
        "thread_seconds": round(dt_thread, 4),
        "process_seconds": round(dt_proc, 4),
        "process_over_thread": round(dt_proc / dt_thread, 2),
    }


# ─── 5. 池启动开销诊断（从 ft_benchmark 探针埋点提取）──────────────────────

def _probe_lag_task(n: int) -> tuple[float, int]:
    """探针负载：返回 (任务开始时刻, 计算结果)。模块级顶层函数，保证可 pickle。"""
    t = time.perf_counter()
    x = count_primes(n)
    return t, x


class PoolProbe:
    """线程/进程池启动开销诊断工具类。

    实测维度（每种池各一份）：
      - pool_create_seconds : Executor 构造耗时（ProcessPool 为惰性 spawn，构造极快）
      - spawn_lag_seconds   : 每个 worker 从 submit 到任务真正开跑的延迟列表；
                              进程池该值含 fork/spawn 成本，即真实的"启动耗时"
      - result_bytes        : 单个 worker 结果的 pickle 序列化大小（进程池往返成本）

    用法：

        probe = PoolProbe(workers=8, payload=50_000)
        t = probe.run()                  # 全量测量，返回 dict
        print(probe.format_report(t))    # 可读报告（不传 t 则现场测量）
        probe.measure_thread_pool()      # 也可单独测量某一种池

    注意：Windows（spawn）下调用方入口需有 __main__ 保护，
    否则子进程重放模块级代码会触发 multiprocessing 引导错误。
    """

    def __init__(self, workers: int = 8, payload: int = 50_000,
                 mp_method: str | None = None):
        """
        参数：
            workers   每种池的 worker 数
            payload   每个 worker 的素数上界（探针负载规模）
            mp_method 进程池 start_method；None 表示 fork 优先、平台不支持时回退默认
        """
        import multiprocessing as mp
        self.workers = workers
        self.payload = payload
        if mp_method is None:
            mp_method = ("fork" if "fork" in mp.get_all_start_methods()
                         else mp.get_start_method())
        self.mp_method = mp_method

    def _measure(self, factory, **kw) -> dict:
        """对给定 Executor 工厂执行一轮测量（构造 → 提交 → 收集）。"""
        t_create = time.perf_counter()
        with factory(self.workers, **kw) as ex:
            create_s = time.perf_counter() - t_create
            t_submit = time.perf_counter()
            futs = [ex.submit(_probe_lag_task, self.payload)
                    for _ in range(self.workers)]
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

    def measure_thread_pool(self) -> dict:
        """测量 ThreadPoolExecutor 的启动开销。"""
        return self._measure(ThreadPoolExecutor)

    def measure_process_pool(self) -> dict:
        """测量 ProcessPoolExecutor 的启动开销（含 fork/spawn 成本）。"""
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        d = self._measure(ProcessPoolExecutor,
                          mp_context=mp.get_context(self.mp_method))
        d["start_method"] = self.mp_method
        return d

    def run(self) -> dict:
        """全量测量：线程池 + 进程池，返回完整埋点 dict。"""
        return {
            "workers": self.workers, "payload": self.payload,
            "pickle_protocol": pickle.HIGHEST_PROTOCOL,
            "thread": self.measure_thread_pool(),
            "process": self.measure_process_pool(),
        }

    def format_report(self, t: dict | None = None) -> str:
        """渲染可读报告；不传 t 则现场执行一轮 run()。"""
        t = t if t is not None else self.run()
        if not t:
            return ""
        if "error" in t:
            return f"[probe] 探针失败（不影响基准结果）: {t['error']}"
        lines = []
        for kind in ("thread", "process"):
            d = t.get(kind) or {}
            if not d:
                continue
            lags = d.get("spawn_lag_seconds") or [0.0]
            lines.append(
                f"[probe] {kind}({d.get('start_method', '-')}): x{t['workers']} "
                f"create={d['pool_create_seconds'] * 1000:7.2f}ms "
                f"lag[min={min(lags) * 1000:.1f} avg={d['spawn_lag_avg'] * 1000:.1f} "
                f"max={max(lags) * 1000:.1f}]ms "
                f"result={d['result_bytes']}B")
        return "\n".join(lines)


if __name__ == "__main__":
    print(format_env_report(env_report()))
    probe = PoolProbe(workers=4, payload=20_000)
    print(probe.format_report())
    print("\n[nogil_kit] 自检模式：python -c 'from nogil_kit import ...' 按需调用")
