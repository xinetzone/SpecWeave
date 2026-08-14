#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nogil 开发工具箱 —— 从 nogil_kernel_template.ipynb 提取的可复用库模块。

覆盖 free-threading（Python 3.14t）开发环境的四类高频操作：
  1. 环境自检        env_report() / format_env_report()
  2. GIL 状态诊断    diagnose()（子进程调用同目录 check_gil_state.py）
  3. kernel 注册     register_nogil_kernel()（幂等，env PYTHON_GIL=0）
  4. 性能测量        quick_thread_scaling() / pool_compare()

零第三方依赖（register_nogil_kernel 内部延迟导入 jupyter_client）。

用法（任意项目里）：

    from nogil_kit import env_report, diagnose, register_nogil_kernel

    print(format_env_report(env_report()))
    diagnose()                          # GIL 诊断，退出码 0=健康 1=被拉起 2=非ft构建
    register_nogil_kernel()             # 注册 "Python 3.14t (nogil)" kernel

    sp = quick_thread_scaling(range_=200_000)   # {"1": 1.0, "2": 2.3, ...}
    cmp = pool_compare(n=3_000_000, workers=8)  # ThreadPool vs ProcessPool 对照
"""

from __future__ import annotations

import json
import os
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
    "pool_compare",
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


if __name__ == "__main__":
    print(format_env_report(env_report()))
    print("\n[nogil_kit] 自检模式：python -c 'from nogil_kit import ...' 按需调用")
