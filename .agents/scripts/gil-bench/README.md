# gil-bench：GIL vs no-GIL 多线程性能对比工具

在标准 GIL 与 free-threading（no-GIL）Python 环境下对比 CPU 密集任务的多线程性能，支持多线程数扫描、绘图与一键双环境对照。

## 适用环境

- 需要一个 **free-threading** Python 环境（如 conda 的 `py314t`，安装 `python-freethreading` 且 `python_abi=*_cp314t`）与一个标准 GIL 环境（如 `py314`）。
- 驱动进程（运行 typer CLI）需装有 `typer`。
- `plot` / `compare` 绘图需要 `matplotlib`（无则跳过绘图）。

## 安装依赖

```bash
# 仅驱动进程需要 typer；绘图需 matplotlib
pip install typer matplotlib
```

## 用法

### 1. 单环境扫描（`scan`）

自动检测当前解释器是否 no-GIL，跑一组线程数基准并输出 JSON。

```bash
python gil_bench.py scan --units 6000000 --workers "1,2,4,8,12" --out scan.json
```

### 2. 绘图（`plot`）

读取两份扫描 JSON（no-GIL 与 GIL），生成耗时 + 加速比双联曲线。

```bash
python gil_bench.py plot --nogil scan_nogil.json --gil scan_gil.json --out curve.png
```

### 3. 一键双环境对照（`compare`）

指定两个解释器路径，自动在各环境扫描并绘图。子进程通过内置 `--core-scan` 轻量入口运行，**无需目标环境安装 typer**。

```bash
python gil_bench.py compare \
  --no-gil-py "D:\Users\xinzo\anaconda3\envs\py314t\python.exe" \
  --gil-py "D:\Users\xinzo\anaconda3\envs\py314\python.exe" \
  --out-dir results/
```

输出：`scan_nogil.json` / `scan_gil.json` / `gil_vs_nogil_curve.png`。

### 4. 轻量入口（`--core-scan`）

供无 typer 环境直接执行单环境扫描：

```bash
<任意python> gil_bench.py --core-scan --units 6000000 --workers "1,2,4,8,12" --out scan.json
```

## 输出与解读

- `workers`：线程组数扫描序列（1,2,4,8...）
- `thread_s`/`pool_s`：原生 threading / ThreadPoolExecutor 耗时
- `speedup`：相对串行的加速比
- **判读**：若 no-GIL 端口加速比随线程数近线性增长（如 5x）、GIL 端口维持 ~1x，则为 free-threading 理想甜区；若两者相近，瓶颈不在 GIL。

## 关联

对应技术分析：[Python 3.14 Free-Threading 适用场景分析](../../../docs/knowledge/tech/python-314-free-threading-scenario-analysis.md)