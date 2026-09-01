---
type: Wiki Tutorial

id: "python314-stdlib-wiki-13"
title: "OKF 工具链基于 Python 3.14 标准库优化 — 优化前后对比记录"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/13-okf-optimization-report.toml"
---
# OKF 工具链基于 Python 3.14 标准库优化 — 优化前后对比记录

> 一句话摘要：本记录逐项列出 `okf` 工具链（`d:\AI\projects\xuanspace\tools\okf`）在 Python 3.14 标准库优化前后的可量化指标差异——单元测试通过数、代码覆盖率、`ruff check` 告警数、数据类实例内存占用、拓扑排序队列微基准耗时，并给出「优化前 / 优化后 / 变化量」。

## 一、优化前基线来源说明

优化前的全部数据**均来自对改动前代码的实际运行采集**，而非事后估算：通过 `git stash` 将 `tools/okf` 临时恢复至 git HEAD（提交 `8aa6d8b`，即「feat(okf): 实现 OKF v0.2 零运行时依赖工具链」的最终状态，尚未做本优化），在此状态下运行 `pytest --cov`、`ruff check` 与一次性内存/微基准脚本；采集完成后 `git stash pop` 恢复优化代码，再对「优化后」运行同一套采集。

## 二、五项量化指标对比总表

| 指标 | 优化前 | 优化后 | 变化量 |
|---|---|---|---|
| 单元测试通过数 | 187 | 259 | **+72（全部通过，无回归）** |
| 代码覆盖率 | 91%（1404 语句 / 126 未覆盖） | 100%（1419 语句 / 0 未覆盖） | **+9 个百分点，未覆盖语句 126→0** |
| `ruff check` 告警数 | 0 | 0 | **0（无新增告警）** |
| `Concept` 实例内存 | 344 字节（48 + `__dict__` 296，**有** `__dict__`） | 104 字节（**无** `__dict__`） | **-240 字节（-69.8%）** |
| `Bundle` 实例内存 | 344 字节（48 + `__dict__` 296，**有** `__dict__`） | 64 字节（**无** `__dict__`） | **-280 字节（-81.4%）** |
| 拓扑排序队列微基准（N=50000） | `list.pop(0)` 约 0.24s | `deque.popleft` 约 0.004s | **约 60× 加速（O(n) → O(1) 弹出）** |

## 三、逐项详解

### 3.1 单元测试通过数：187 → 259

- 优化改动前的测试基线为 187 项（`pytest -q` 输出 `187 passed`）。
- 优化过程中为覆盖新增/重构后的代码路径，新增 72 项测试，覆盖：数据类 `slots`/`field(doc=)` 内省、`Context`/`Harness` 上下文管理器协议（`__enter__`/`__exit__`/`dispose()` 幂等）、事件分发六种模式的边界分支（`bail`/`serial` 全 `None`、`parallel` 在运行中事件循环抛错、`waterfall` 无监听器）、拓扑排序循环依赖、插件加载失败与 `KeyError` 防御分支、链接解析越界、信任推导非法日期、YAML 解析器防御分支、`attested.py` 的 `runtime` 缺失/空/非字符串校验等。
- 最终 `259 passed`，且原有 187 项**无一回归**（spec 要求「现有 187 项测试必须全部通过」已达）。

### 3.2 代码覆盖率：91% → 100%

- 优化前 `TOTAL 1404 语句，126 未覆盖，91%`。
- 优化后 `TOTAL 1419 语句，0 未覆盖，100%`，24 个源文件（含 `plugins/` 子包）均 `100%`。
- 说明：语句总数 1404→1419 净增 15，源于优化将 `events.py` 的 monkey-patch 实现（55 语句）迁移为 `Context` 类正规方法（`context.py` 63→116 语句），同时为 `Context`/`Harness` 新增 `dispose`/`__enter__`/`__exit__`、为 `harness.py` 新增 `deque` 拓扑排序等；新增语句全部被测试覆盖。
- 唯一豁免：`__main__.py` 中 `if __name__ == "__main__": main()` 的进程入口两行标 `# pragma: no cover`（委托给 `cli.main()`，其逻辑已被测试完整覆盖），属 CLI 入口的既定实践，非未覆盖逻辑。

### 3.3 `ruff check` 告警数：0 → 0

- 优化前 `ruff check src tests` 输出 `All checks passed!`（0 告警）。
- 优化后同样 `All checks passed!`（0 告警）；过程中新写入 `events.py`（精简为纯 docstring）与新建 `test_plugins_keyerror.py` 曾产生 2 条 `W292`（文件末尾无换行符），已用 `ruff --fix` 修复归零，故「无新增告警」成立。

### 3.4 数据类实例内存：`__dict__` 消除、内存显著下降

- 优化前所有 `@dataclass(frozen=True)` 数据类无 `slots`，实例携带 `__dict__`；`Concept`/`Bundle` 实测各 48 字节顶层 + 296 字节 `__dict__` = 344 字节，`has __dict__ = True`。
- 优化后 `slots=True` 生效，`Concept` 104 字节、`Bundle` 64 字节，`has __dict__ = False`（满足 spec「`hasattr(instance, '__dict__')` 为 `False`」与内存低于基线两项场景）。
- 关键字段同时补 `field(doc=...)`，经 `dataclasses.fields(cls)` 可读到非空 `Field.doc`（满足 spec「字段文档可被内省」场景）。

### 3.5 拓扑排序队列微基准：`deque` 约 60× 加速

- 优化前 `harness.py::_topological_sort` 使用 `list.pop(0)`（每次弹出 O(n) 搬迁），优化后改用 `collections.deque` + `popleft()`（O(1) 弹出）。
- 微基准（N=50000 队列元素，`timeit` 各 3 轮）：`list.pop(0)` 约 0.20~0.24s，`deque.popleft` 约 0.003~0.004s，**约 60× 加速**。
- 行为不变性：`test_harness.py` 的拓扑排序用例（含循环依赖回退）优化前后结果一致；`harness.py` 中已无 `pop(0)` 调用（满足 spec「不再出现 `pop(0)`」场景）。
- `Fiber` 同时在初始化时缓存 `inject` 服务名集合 `frozenset`（`plugin.py::Fiber._inject_names`），`notify` 复用缓存避免重复计算（spec「Fiber 缓存 inject 名称集合」场景）。

## 四、其他已落地变更（非量化但可验证）

- **消除 `events.py` 对 `Context` 的 monkey-patch**：六种事件分发方法（`on`/`emit`/`bail`/`parallel`/`serial`/`waterfall`）已由 `Context` 类正式声明；`events.py` 精简为纯 docstring 兼容模块（0 语句）。仅 `import okf.context` 即可使用事件方法，消除 import-order 脆弱性。
- **`_parallel` 的 asyncio 兼容修复**：在已运行事件循环内不再无条件 `asyncio.run()`，避免 `RuntimeError: asyncio.run() cannot be called from a running event loop`。
- **`attested.py` 的 `runtime` 校验一致性**：对缺失/空/非字符串 `runtime` 抛出清晰 `ValueError`（消息含 `runtime` 字段名），替代原先直接下标访问抛出的 `KeyError`。

## 五、结论

本次优化在不破坏原有 187 项测试的前提下，将单元测试通过数从 187 提升至 259、代码覆盖率从 91% 提升至 100%、`ruff check` 保持 0 告警；通过 `slots=True` 消除数据类 `__dict__` 使 `Concept`/`Bundle` 内存下降 70%~81%；通过 `deque` 拓扑排序使队列弹出微基准加速约 60×；并落地上下文管理器协议、结构化错误诊断与两处潜在问题修复。对应的 stdlib 能力落点映射见 [12-okf-optimization-mapping](12-okf-optimization-mapping.md)。