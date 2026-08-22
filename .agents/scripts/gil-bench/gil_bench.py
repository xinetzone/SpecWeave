"""gil-bench：GIL vs no-GIL 多线程性能对比 CLI 工具。

用于在标准 GIL 与 free-threading（no-GIL）Python 环境下对比多线程性能。

用法示例：
  # 单环境扫描（自动检测当前解释器是否 no-GIL）
  python gil_bench.py scan --units 6000000 --workers "1,2,4,8,12" --out scan.json

  # 读取两份扫描结果绘图（需 matplotlib）
  python gil_bench.py plot --nogil scan_nogil.json --gil scan_gil.json --out curve.png

  # 两环境一键对照（主进程需 typer；scan 子进程无需 typer）
  python gil_bench.py compare --no-gil-py <py314t> --gil-py <py314> --out-dir results/
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Optional

# typer 仅驱动主进程需要；目标环境无 typer 时走 --core-scan 轻量入口
try:
    import typer  # type: ignore

    _HAS_TYPER = True
except ImportError:
    typer = None  # type: ignore
    _HAS_TYPER = False


# ---------- 核心基准逻辑（仅依赖 stdlib） ----------

def _cpu_work(n: int) -> int:
    """纯 Python CPU 密集计算，触发大量 Python 字节码。"""
    total = 0
    for i in range(n):
        total += (i * i) & 0x7FFF
    return total


def _time_serial(total: int, repeat: int) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        _cpu_work(total)
        best = min(best, time.perf_counter() - start)
    return best


def _time_parallel(total: int, n_workers: int, use_pool: bool, repeat: int) -> float:
    proto: List[float] = []
    per_unit = max(1, total // n_workers)
    for _ in range(repeat):
        start = time.perf_counter()
        if use_pool:
            with ThreadPoolExecutor(max_workers=n_workers) as ex:
                list(ex.map(_cpu_work, [per_unit] * n_workers))
        else:
            threads = [threading.Thread(target=_cpu_work, args=(per_unit,)) for _ in range(n_workers)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        proto.append(time.perf_counter() - start)
    return min(proto)


def _gil_state() -> bool:
    try:
        return not bool(sys._is_gil_enabled())
    except AttributeError:
        return False


def _soabi() -> str:
    try:
        import sysconfig

        return sysconfig.get_config_var("SOABI") or "N/A"
    except Exception:
        return "N/A"


def run_scan(units: int, workers: List[int], repeat: int) -> dict:
    """执行一组基准，返回结构化结果 dict（串行 + 各线程数 thread/pool）。"""
    _cpu_work(100_000)  # 预热
    no_gil = _gil_state()
    serial = _time_serial(units, repeat)

    rows = []
    for w in workers:
        thread_s = _time_parallel(units, w, use_pool=False, repeat=repeat)
        pool_s = _time_parallel(units, w, use_pool=True, repeat=repeat)
        rows.append(
            {
                "workers": w,
                "thread_s": round(thread_s, 4),
                "pool_s": round(pool_s, 4),
                "thread_speedup": round(serial / thread_s, 3) if thread_s else 0,
                "pool_speedup": round(serial / pool_s, 3) if pool_s else 0,
            }
        )
    return {
        "gil_enabled": not no_gil,
        "python": f"{sys.version}",
        "soabi": _soabi(),
        "units": units,
        "serial_s": round(serial, 4),
        "rows": rows,
    }


def _core_scan_main(argv: List[str]) -> int:
    """轻量 scan 入口，仅依赖 stdlib，供任意 Python 环境（可能无 typer）直接执行。
    参数: --units N --workers a,b,c --repeat N --out PATH
    """
    def _get(name: str, default: str) -> str:
        try:
            i = argv.index(name)
            return argv[i + 1]
        except (ValueError, IndexError):
            return default

    units = int(_get("--units", "6000000"))
    workers = _get("--workers", "1,2,4,8,12")
    repeat = int(_get("--repeat", "3"))
    out = _get("--out", "")
    w_list = [int(x) for x in workers.split(",") if x.strip()]

    no_gil_label = "no-GIL (free-threading)" if _gil_state() else "标准 GIL"
    print(f"Python: {sys.version.split()[0]}  GIL: {no_gil_label}  SOABI: {_soabi()}")
    result = run_scan(units, w_list, repeat)
    print(f"{'线程数':<6}{'thread(s)':<10}{'thread加速':<12}{'pool(s)':<10}{'pool加速'}")
    for row in result["rows"]:
        print(
            f"{row['workers']:<6}{row['thread_s']:8.3f}s   {row['thread_speedup']:6.2f}x      "
            f"{row['pool_s']:8.3f}s   {row['pool_speedup']:6.2f}x"
        )
    print(f"串行耗时: {result['serial_s']:.4f}s")
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已写入: {out}")
    return 0


# ---------- 绘图（预留，独立于 typer，可在带 matplotlib 的环境 standalone 调用） ----------

def plot_compare(nogil_path: str, gil_path: str, out: str) -> None:
    """读取两份扫描 JSON，绘制耗时 + 加速比双联曲线（需 matplotlib）。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "Microsoft JhengHei", "SimHei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False

    def _load(p: str) -> dict:
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def _rows(d: dict):
        return [r for r in d["rows"] if "thread_s" in r]

    ng = _load(nogil_path)
    gl = _load(gil_path)
    ng_rows, g_rows = _rows(ng), _rows(gl)
    x = [r["workers"] for r in ng_rows]
    ng_thread = [r["thread_s"] for r in ng_rows]
    g_thread = [r["thread_s"] for r in g_rows]
    ng_speed = [r["thread_speedup"] for r in ng_rows]
    g_speed = [r["thread_speedup"] for r in g_rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
    ax1.plot(x, g_thread, "o--", color="#d62728", label="GIL")
    ax1.plot(x, ng_thread, "o-", color="#2ca02c", label="no-GIL")
    ax1.set_xlabel("线程数")
    ax1.set_ylabel("耗时 (s)")
    ax1.set_title("CPU 密集任务耗时（越低越好）")
    ax1.set_xticks(x)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend()

    ax2.axhline(1.0, color="gray", linestyle=":", linewidth=1)
    ax2.plot(x, g_speed, "o--", color="#d62728", label="GIL")
    ax2.plot(x, ng_speed, "o-", color="#2ca02c", label="no-GIL")
    ax2.plot(x, [i for i in x], ":", color="#7f7f7f", label="理想线性")
    ax2.set_xlabel("线程数")
    ax2.set_ylabel("加速比")
    ax2.set_title("CPU 密集任务加速比（越高越好）")
    ax2.set_xticks(x)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend()

    fig.suptitle("GIL vs no-GIL · CPU 密集多线程性能对比", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out, dpi=140)


# ---------- typer 命令（仅当 typer 可用时注册） ----------

if _HAS_TYPER and typer is not None:
    app = typer.Typer(help="GIL vs no-GIL 多线程性能对比工具")

    @app.command("scan")
    def _cmd_scan(
        units: int = typer.Option(6_000_000, "--units", "-u", help="每线程迭代基准数"),
        workers: str = typer.Option("1,2,4,8,12", "--workers", "-w", help="逗号分隔线程数序列"),
        repeat: int = typer.Option(3, "--repeat", "-r", help="每档测量次数，取最优"),
        out: str = typer.Option(None, "--out", "-o", help="JSON 输出路径"),
    ):
        w_list = [int(x) for x in workers.split(",") if x.strip()]
        no_gil_label = "no-GIL (free-threading)" if _gil_state() else "标准 GIL"
        typer.echo(f"Python: {sys.version.split()[0]}  GIL: {no_gil_label}  SOABI: {_soabi()}")
        result = run_scan(units, w_list, repeat)
        typer.echo(f"{'线程数':<6}{'thread(s)':<10}{'thread加速':<12}{'pool(s)':<10}{'pool加速'}")
        for row in result["rows"]:
            typer.echo(
                f"{row['workers']:<6}{row['thread_s']:8.3f}s   {row['thread_speedup']:6.2f}x      "
                f"{row['pool_s']:8.3f}s   {row['pool_speedup']:6.2f}x"
            )
        typer.echo(f"串行耗时: {result['serial_s']:.4f}s")
        if out:
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            typer.echo(f"结果已写入: {out}")

    @app.command("plot")
    def _cmd_plot(
        nogil: str = typer.Argument(..., help="no-GIL 扫描结果 JSON"),
        gil: str = typer.Argument(..., help="标准 GIL 扫描结果 JSON"),
        out: str = typer.Option("gil_vs_nogil_curve.png", "--out", "-o", help="输出 PNG 路径"),
    ):
        try:
            plot_compare(nogil, gil, out)
        except ImportError:
            typer.echo("错误: 需要 matplotlib，请在已安装 matplotlib 的环境下运行 plot。", err=True)
            raise typer.Exit(code=1)
        typer.echo(f"图表已保存: {out}")

    @app.command("compare")
    def _cmd_compare(
        no_gil_py: str = typer.Option(..., "--no-gil-py", help="no-GIL 解释器路径"),
        gil_py: str = typer.Option(..., "--gil-py", help="标准 GIL 解释器路径"),
        units: int = typer.Option(6_000_000, "--units", "-u"),
        workers: str = typer.Option("1,2,4,8,12", "--workers", "-w"),
        repeat: int = typer.Option(3, "--repeat", "-r"),
        out_dir: str = typer.Option("results", "--out-dir", "-d", help="输出目录"),
    ):
        os.makedirs(out_dir, exist_ok=True)
        ng_out = os.path.join(out_dir, "scan_nogil.json")
        gil_out = os.path.join(out_dir, "scan_gil.json")
        png_out = os.path.join(out_dir, "gil_vs_nogil_curve.png")
        here = os.path.abspath(__file__)

        base = [here, "--core-scan", "--units", str(units), "--workers", workers, "--repeat", str(repeat)]
        typer.echo("[1/3] 运行 no-GIL 环境扫描...")
        subprocess.run([no_gil_py, *base, "--out", ng_out], check=True)
        typer.echo("[2/3] 运行标准 GIL 环境扫描...")
        subprocess.run([gil_py, *base, "--out", gil_out], check=True)
        typer.echo("[3/3] 生成对比曲线图...")
        try:
            plot_compare(ng_out, gil_out, png_out)
            typer.echo(f"完成：\n  no-GIL: {ng_out}\n  GIL:    {gil_out}\n  图表:   {png_out}")
        except ImportError:
            typer.echo(f"扫描完成（本环境无 matplotlib，图表跳过）：\n  no-GIL: {ng_out}\n  GIL:    {gil_out}")


def main(argv: Optional[List[str]] = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "--core-scan":
        sys.exit(_core_scan_main(args[1:]))
    if not _HAS_TYPER:
        print("错误: 需要 typer 才能使用 CLI 子命令；或使用 --core-scan 轻量入口。", file=sys.stderr)
        sys.exit(2)
    app()


if __name__ == "__main__":
    main()