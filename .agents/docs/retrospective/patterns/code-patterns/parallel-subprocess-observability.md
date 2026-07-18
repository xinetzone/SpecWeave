---
id: "parallel-subprocess-observability"
source: "external: 不存在-lib/checks/vendor.py --deep mode optimization (2026-07-08)"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/parallel-subprocess-observability.toml"
---
# 并行子进程全链路可观测模式

## 问题

CLI 工具中需要对多个独立目标（如子模块、目录、服务）执行外部命令检查时面临三重瓶颈：

1. **串行 I/O 阻塞**：每个子进程调用独立阻塞，N 个目标耗时 = Σ 各目标耗时
2. **黑盒执行**：并行执行后无法定位哪个目标慢、哪个失败、失败原因是什么
3. **日志竞争**：多线程日志输出容易交错混乱，难以阅读
4. **不可编程**：文本输出仅供人阅读，JSON 模式下缺少细粒度性能数据

在 vendor-check 的 `--deep` 模式中，对 2 个 Git 子模块串行执行 `git status` 总耗时约 455ms，其中 deep 步骤独占约 453ms（占总耗时 99%+）。

## 解决方案

三层优化叠加：**命令参数精简 → 线程池并行 → 全链路可观测日志**。

### 第一层：子进程命令参数优化

在并行化之前，先优化单个命令本身的执行时间：

| 优化手段 | 参数 | 原理 | git status 场景效果 |
|---|---|---|---|
| 跳过可选锁 | `--no-optional-locks` | 避免 git 为了优化操作而获取索引锁 | 减少锁竞争开销 |
| 跳过未跟踪文件 | `-uno` (`--untracked-files=no`) | 不遍历目录寻找未跟踪文件 | Windows 上大幅减少文件系统扫描 |

```python
result = subprocess.run(
    ["git", "--no-optional-locks", "status", "--porcelain", "-uno"],
    capture_output=True, text=True, cwd=str(sm_dir),
    timeout=10,
)
```

> **适用前提**：未跟踪文件的增减对当前检查目标无意义。vendor 子模块检查只关心已跟踪文件是否有未提交变更，构建产物等未跟踪文件不影响合规性判定。

### 第二层：ThreadPoolExecutor 并行执行

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def _check_one(target: str) -> dict:
    """单个目标的检查函数（线程安全），返回含状态和耗时的字典。"""
    t0 = time.perf_counter()
    try:
        result = subprocess.run([...], capture_output=True, text=True, cwd=target_dir, timeout=10)
        elapsed = (time.perf_counter() - t0) * 1000
        if result.returncode != 0:
            return {"target": target, "status": "warn", "msg": "...", "elapsed_ms": elapsed}
        if result.stdout.strip():
            return {"target": target, "status": "warn", "msg": "...", "elapsed_ms": elapsed}
        return {"target": target, "status": "pass", "msg": "...", "elapsed_ms": elapsed}
    except FileNotFoundError:
        return {"target": None, "status": "fatal", "msg": "命令未找到", "err": True, "elapsed_ms": 0.0}
    except subprocess.TimeoutExpired:
        return {"target": target, "status": "warn", "msg": "超时", "elapsed_ms": timeout_ms}
    except Exception as e:
        return {"target": target, "status": "error", "msg": f"异常: {e}", "err": True, "elapsed_ms": 0.0}

targets = sorted(target_list)
results: list[dict] = []
if targets:
    max_workers = min(len(targets), 8)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(_check_one, t): t for t in targets}
        for future in as_completed(future_map):
            results.append(future.result())
    results.sort(key=lambda r: r.get("target") or "")
```

**关键设计**：

- **max_workers 上限**：`min(N, 8)` 防止线程数过多导致上下文切换开销和系统资源争抢
- **as_completed 收集**：先完成先收集，降低内存峰值；完成后按名称排序保证输出确定性
- **每个 _check_one 自包含计时**：不依赖外部状态，天然线程安全
- **fatal 特殊处理**：返回 `target=None, status="fatal"` 表示全局性错误（如命令不存在），需中断流程

### 第三层：全链路可观测日志

每个目标的检查函数内，记录**开始 → 执行 → 完成**三阶段日志，使用缩进和图标增强可读性：

```python
def _check_one(target: str) -> dict:
    _debug("step", f"  → 开始检查: {target}")             # 进入
    if not precondition:
        _debug("step", f"  ← {target} 前置条件不满足，跳过") # 提前返回
        return {...}
    try:
        _debug("step", f"  ↻ {target} 执行命令")           # 子进程启动
        t0 = time.perf_counter()
        result = subprocess.run([...])
        elapsed = (time.perf_counter() - t0) * 1000
        if failed:
            _debug("step", f"  ✗ {target} 失败 ({elapsed:.1f}ms): {reason}")
            return {...}
        if has_issues:
            _debug("step", f"  ⚠ {target} 有问题（{n} 项，{elapsed:.1f}ms）")
            return {...}
        _debug("step", f"  ✓ {target} 通过（{elapsed:.1f}ms）")
        return {...}
    except subprocess.TimeoutExpired:
        _debug("step", f"  ✗ {target} 超时（>{timeout}ms）")
        return {...}
```

### 第四层：并行执行汇总

所有目标完成后输出汇总表，包含串行估计 vs 并行实际的加速比：

```python
_debug("step", "─── 并行执行汇总 ───")
total_serial = 0.0
for r in results:
    name = r.get("target") or "(unknown)"
    ems = r.get("elapsed_ms", 0.0)
    total_serial += ems
    icon = {"pass": "✓", "warn": "⚠", "error": "✗", "fatal": "✗"}.get(r["status"], "?")
    _debug("step", f"  {icon} {name}: {ems:.1f}ms [{r['status']}]")
if total_serial > 0 and wall_ms > 0:
    speedup = total_serial / wall_ms
    _debug("step", f"  串行估计: {total_serial:.1f}ms | 并行实际: {wall_ms:.1f}ms | 加速比: {speedup:.2f}x")
_debug("step", "────────────────────")
```

### 第五层：JSON 模式编程接口

JSON 输出中每个子检查携带独立 `duration_ms`，并新增顶层 `parallel_summary` 对象：

```python
# 各子检查条目携带独立耗时
_record("deep", "pass", f"{target}：{msg}", duration_ms=r.get("elapsed_ms"))

# 顶层 parallel_summary 提供并行效率数据
results["parallel_summary"] = {
    "targets": [
        {"path": r["target"], "status": r["status"], "elapsed_ms": round(r["elapsed_ms"], 1)}
        for r in results
    ],
    "serial_estimate_ms": round(total_serial, 1),
    "parallel_wall_ms": round(wall_ms, 1),
    "speedup": round(total_serial / wall_ms, 2) if wall_ms > 0 else None,
    "max_workers": min(len(targets), 8),
}
```

## 性能收益

vendor-check `--deep` 模式实测数据（2 个 Git 子模块，Windows 环境）：

| 指标 | 优化前（串行+默认参数） | 优化后（并行+参数优化） | 提升 |
|---|---|---|---|
| deep 步骤耗时 | ~453ms | ~143ms | **↓ 68%** |
| 总耗时 | ~456ms | ~145ms | **↓ 68%** |
| 非 deep 步骤耗时 | ~3ms | ~2ms | 不变 |
| 加速比 | 1.0x（串行基准） | 1.77~1.81x | 接近理想 2x |

### 为什么加速比不是 2.0x？

2 个子模块理论加速比为 2x，实际稳定在 1.77~1.81x，差异来源：

1. **线程池创建/销毁开销**：约 1~3ms
2. **GIL 与进程启动**：`subprocess.run` 在等待子进程期间会释放 GIL，但进程创建本身有开销
3. **结果收集与排序**：`as_completed` 迭代 + 排序约 0.5ms
4. **两个子模块执行时间不均衡**：ark-cli ~110ms vs flexloop ~140ms，快的线程需等待慢的（墙钟时间 = max(各线程耗时) ≈ 慢的那个）

### 扩展性预测

随着子模块数量增加，线程池上限 8 个意味着：

- 1~8 个子模块：线性加速（受最慢子模块限制）
- 9+ 个子模块：加速比上限为 8x，超过部分分批执行
- 当子模块数 ≫ 8 时，I/O 等待占主导，8 线程足以饱和磁盘/网络带宽

## 关键设计决策

1. **先优化单命令、再并行**：`-uno` 参数对单个 git status 的优化效果约 30~50%，先做完再并行效果叠加
2. **elapsed_ms 字段全覆盖**：所有返回路径（pass/warn/error/timeout/fatal/skip）都携带 elapsed_ms，确保汇总数据完整
3. **线程安全日志**：`_debug()` 基于 `print(file=sys.stderr)`，CPython GIL 保证单次 print 原子性，不会出现半行交错
4. **fatal 全局短路**：全局性错误（如 git 命令不存在）通过 `target=None` 标识，主循环检测后立即 break 并记录全局错误
5. **结果排序确定性**：并行完成顺序不确定，最后按 target 名称排序，保证输出顺序稳定
6. **max_workers 硬上限 8**：防止子模块数量激增时线程数失控，8 是经验值（超过 8 个并发子进程对 Windows 文件系统无额外收益）
7. **图标语义化**：`→`（开始）`↻`（执行中）`✓`（通过）`⚠`（警告）`✗`（失败）`←`（跳过），一眼可辨
8. **加速比自证**：每次运行自动计算并输出加速比，可直观验证并行收益是否符合预期

## Debug 日志输出示例

```
[DEBUG:vendor] [deep] 并行检查 2 个子模块，max_workers=2
[DEBUG:vendor] [deep]   → 开始检查子模块: vendor/ark-cli
[DEBUG:vendor] [deep]   ↻ vendor/ark-cli 执行 git status --porcelain -uno
[DEBUG:vendor] [deep]   → 开始检查子模块: vendor/flexloop
[DEBUG:vendor] [deep]   ↻ vendor/flexloop 执行 git status --porcelain -uno
[DEBUG:vendor] [deep]   ✓ vendor/ark-cli 工作区干净（104.2ms）
[DEBUG:vendor] [deep]   ✓ vendor/flexloop 工作区干净（140.6ms）
[DEBUG:vendor] [deep] ─── 并行执行汇总 ───
[DEBUG:vendor] [deep]   ✓ vendor/ark-cli: 104.2ms [pass]
[DEBUG:vendor] [deep]   ✓ vendor/flexloop: 140.6ms [pass]
[DEBUG:vendor] [deep]   串行估计: 244.8ms | 并行实际: 142.1ms | 加速比: 1.72x
[DEBUG:vendor] [deep] ────────────────────
```

## JSON 输出示例

```json
{
  "checks": [
    {"name": "deep", "status": "pass", "message": "vendor/ark-cli：工作区干净（已跟踪文件无变更）", "duration_ms": 107.1},
    {"name": "deep", "status": "pass", "message": "vendor/flexloop：工作区干净（已跟踪文件无变更）", "duration_ms": 133.4}
  ],
  "parallel_summary": {
    "targets": [
      {"path": "vendor/ark-cli", "status": "pass", "elapsed_ms": 107.1},
      {"path": "vendor/flexloop", "status": "pass", "elapsed_ms": 133.4}
    ],
    "serial_estimate_ms": 240.5,
    "parallel_wall_ms": 135.0,
    "speedup": 1.78,
    "max_workers": 2
  },
  "step_timings_ms": [...],
  "total_duration_ms": 137.0,
  "passed": true
}
```

## 复用场景

任何需要对多个独立目标执行外部命令检查的 CLI 工具，特别是：

- 多 Git 仓库/子模块批量状态检查
- 多目录 lint/typecheck/test 并行执行
- 多服务健康检查并行探测
- 批量文件格式转换/处理
- 多主机 SSH 批量命令执行

## 来源

[vendor.py](../../../../scripts/lib/checks/vendor.py) — `run()` 函数中 `_check_one_submodule()` 和 ThreadPoolExecutor 并行块（约 L677-L806）

> **关联模式**：
> - [dual-channel-tiered-logging](dual-channel-tiered-logging.md) — 本模式的日志输出基于双轨分级日志体系
> - [script-json-output-contract](script-json-output-contract.md) — JSON 输出格式约定
> - [cli-as-api-design](cli-as-api-design.md) — CLI 同时作为可调用 API 的设计原则
