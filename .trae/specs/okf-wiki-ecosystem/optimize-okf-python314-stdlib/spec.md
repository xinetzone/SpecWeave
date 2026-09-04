# OKF 工具链基于 Python 3.14 标准库的系统性优化 Spec

## Why

`okf` 工具链（`d:\AI\projects\xuanspace\tools\okf`）已是一个「零运行时依赖、可插拔」的 OKF v0.2 工具链，且已通过 187 项单元测试（覆盖率约 91%）。但它尚未充分利用 Python 3.14 标准库中已经掌握的能力——`dataclasses` 的 `slots=True` 与 `field(doc=)`、`traceback` 的结构化错误诊断、`contextlib` 的上下文管理器语义、以及性能敏感的 `collections.deque`。通过系统学习 `d:\AI\docs\knowledge\learning\python314-stdlib-wiki` 六个模块（`contextlib` / `contextvars` / `sys.monitoring` / `annotationlib` / `dataclasses` / `traceback`）后，可以提炼出一组**可量化、可验证**的优化机会，在不破坏现有 187 项测试的前提下，实现代码结构、性能、诊断、文档与潜在问题修复五方面提升。

## What Changes

优化工作分为两条并行链路，最终合并为「优化前后对比记录」：

- **学习笔记链路**：产出 Python 3.14 六模块到 okf 优化机会的映射笔记（详细笔记交付物）。其中每个模块都必须有明确落点——`contextlib`/`dataclasses`/`traceback` 映射到具体代码变更；`contextvars` 映射到「命名澄清 + 显式依赖注入为何无需隐式任务级状态 + 条件性未来落点」的诚实记录；`annotationlib` 映射到「3.14 惰性求值现状 + `from __future__ import annotations` 遗留评估 + 未来内省入口」的诚实记录。禁止为凑齐六模块而强行引入无收益的代码改动。
- **代码优化链路**：落地以下变更（均有量化基线支撑）：
  - 为所有 `@dataclass(frozen=True)` 数据类增加 `slots=True`（内存优化），为关键字段补充 `field(doc=...)`（3.14 文档化）。
  - 消除 `events.py` 中对 `Context` 的 monkey-patch（`Context.on = _on` 等），改为正规方法定义（代码结构改进）。
  - `harness.py` 拓扑排序用 `collections.deque` 替代 `list.pop(0)`（性能提升），`Fiber` 缓存 `inject` 名称集合（性能提升）。
  - `cli.py` 与 `harness.py` 集成 `traceback` 模块，输出结构化错误诊断（功能完善）。
  - `Context` / `Harness` 实现上下文管理器协议（`__enter__` / `__exit__`），`Harness` 补公开 `dispose()` 清理入口，使资源回收由 `with` 保证（`contextlib` 语义落地，功能完善）。
  - 修复 `events.py` `_parallel` 在已有事件循环中调用 `asyncio.run()` 会抛 `RuntimeError` 的问题，以及 `attested.py` `parse_attested_computation` 中 `fm["runtime"]` 缺字段抛 `KeyError` 而非清晰 `ValueError` 的问题（潜在问题修复）。

## Impact

- **Affected specs**：`okf-toolchain-implementation`（本优化是对其产出物的增量改进，不改变其已通过的验收结论）。
- **Affected code**（均在 `d:\AI\projects\xuanspace\tools\okf\src\okf\` 下）：
  - `models.py`（数据类 slots/doc/结构）
  - `service.py`、`plugin.py`、`disposable.py`（数据类 slots/doc）
  - `context.py`（Context 方法归属：吸收 events 能力）
  - `events.py`（去除 monkey-patch、修复 `_parallel`）
  - `harness.py`（deque 拓扑排序、插件加载失败诊断）
  - `cli.py`（traceback 诊断）
  - `attested.py`（`runtime` 字段校验一致性）
- **测试基线**：`d:\AI\projects\xuanspace\tools\okf\tests\` 现有 187 项测试必须全部通过；`ruff check` 无新增告警。

## ADDED Requirements

### Requirement: Python 3.14 标准库到 OKF 优化机会的学习笔记

系统 SHALL 基于 `d:\AI\docs\knowledge\learning\python314-stdlib-wiki` 的六个模块知识，形成一份「学习笔记」，明确每项 stdlib 能力在 okf 代码中的具体落点与量化收益预判。

#### Scenario: 笔记覆盖六模块映射

- **WHEN** 完成对六个模块章节的学习
- **THEN** 笔记中出现至少六条「stdlib 能力 → okf 具体文件/函数 → 优化动作」的映射，且每条引用对应章节的事实；其中 `contextlib`（→ `Context`/`Harness` 上下文管理器协议）、`dataclasses`（→ `slots=True` 省内存 / `field(doc=)` 3.14 新增）、`traceback`（→ `TracebackException.from_exception` 轻量捕获）为代码落点；`contextvars`（→ 命名澄清与显式 DI 取舍）、`annotationlib`（→ 3.14 惰性求值与 future import 评估）为诚实记录落点

### Requirement: 数据类启用 slots 与字段文档化

所有 `@dataclass(frozen=True)` 数据类 SHALL 启用 `slots=True`；关键业务字段 SHALL 通过 `field(doc=...)` 补充字段文档。

#### Scenario: 内存占用降低且无 `__dict__`

- **WHEN** 实例化任一数据类（如 `Concept`、`Bundle`、`Source`）
- **THEN** `hasattr(instance, "__dict__")` 为 `False`，且 `sys.getsizeof` 或字段级拼接后的实例内存小于优化前基线

#### Scenario: 字段文档可被内省

- **WHEN** 通过 `dataclasses.fields(cls)` 读取字段
- **THEN** 关键字段的 `Field.doc` 非空，内容为该字段的一句话平实解释

### Requirement: Context 与 Harness 实现上下文管理器协议

`Context` 与 `Harness` SHALL 实现上下文管理器协议（`__enter__` / `__exit__`），使 `with Context() as ctx:` 与 `with Harness.from_config(...) as h:` 在代码块退出时自动回收资源；`Harness` SHALL 提供公开的 `dispose()` 清理入口（当前其仅内部持有 `_ctx`，缺公开释放方法，属潜在缺陷）。

#### Scenario: with 语句自动回收资源

- **WHEN** 使用 `with Context() as ctx:` 或在 `with Harness.from_config(...) as h:` 内装配插件
- **THEN** 代码块退出后 `Context` 已执行 `dispose()`：所有 Fiber 逆序卸载、服务与效应清空（`len(ctx._fibers) == 0` 且 `len(ctx._store) == 0`）

#### Scenario: Harness 可显式释放且幂等

- **WHEN** 调用 `harness.dispose()`（或等价 `close()`）
- **THEN** 其内部 `Context` 资源被回收；对已释放的 Harness 再次调用 `dispose()` 不抛异常（幂等安全）

### Requirement: contextvars 上下文隔离的落点澄清

系统 SHALL 在学习笔记中澄清 okf 的 `Context`（服务装配容器）与 `contextvars.Context`（并发状态映射）是两种不同的「上下文」概念（存在命名冲突风险），并说明 okf 当前无需 `contextvars` 的原因——显式依赖注入（`Fiber.inject → Context.get`）已取代隐式的任务级状态隔离；同时记录一处条件性未来落点：当 `_parallel` 的异步监听器需要跨协程边界感知触发源 `Context` 时，可引入模块级 `ContextVar`（配合 3.14 的 `with var.set(...)` Token 语义）。

#### Scenario: 命名冲突与设计取舍被记录

- **WHEN** 阅读学习笔记
- **THEN** 出现「okf.Context ≠ contextvars.Context」命名澄清、显式 DI 为何无需 contextvars 的说明，以及至少一条「条件性未来落点 + 触发条件」记录（引用 03-contextvars.md 的 Token/with 语义）

### Requirement: annotationlib 惰性注解与 future import 迁移评估

系统 SHALL 在学习笔记中记录 annotationlib 在 3.14 的定位（PEP 649/749 使惰性求值成为默认），并评估移除各模块 `from __future__ import annotations`（PEP 563 遗留）的可行性与风险；仅在评估为「收益明确且无回归」时执行移除，并以 annotationlib 内省入口（`get_annotations(..., format=...)`）作为后续注解内省的推荐方式。

#### Scenario: 3.14 惰性求值现状被评估

- **WHEN** 阅读学习笔记
- **THEN** 出现「`from __future__ import annotations` 在 3.14 属遗留」的说明、okf 各模块 future import 清单、移除后的回归风险评估，以及（若执行）对应变更与验证记录

### Requirement: 消除 events 模块对 Context 的 monkey-patch

事件分发六种方法（`on`/`emit`/`bail`/`parallel`/`serial`/`waterfall`）SHALL 由 `Context` 类正式声明（直接定义方法或经 mixin），不再依赖 `events.py` 在被 import 时对 `Context` 动态赋值。

#### Scenario: Context 方法静默可用

- **WHEN** 只 `import okf.context`（不 import `okf.events`）后创建 `Context` 实例
- **THEN** `ctx.on`、`ctx.emit` 等方法依然存在且行为一致（消除 import-order 脆弱性）

### Requirement: traceback 集成的结构化错误诊断

CLI 与插件装配失败路径 SHALL 使用 `traceback` 模块输出结构化诊断信息，替代当前的裸 `print` 与吞掉异常的 `except Exception`。

#### Scenario: 插件加载失败可见完整回溯

- **WHEN** `_load_plugins_from_map` 中某插件导入/实例化抛异常
- **THEN** 输出包含该异常类型、消息与定位（文件名/行号），而非仅一行 `Warning: Failed to load plugin ...`

### Requirement: 优化前后对比记录（可量化、可验证）

优化交付物 SHALL 包含一份「优化前后对比记录」，至少覆盖以下量化指标：单元测试通过数、代码覆盖率、`ruff check` 告警数、数据类实例内存占用、拓扑排序与事件分发相关微基准耗时。

#### Scenario: 对比记录含基线与前值差异

- **WHEN** 优化完成并复测
- **THEN** 对比记录中每个指标均给出「优化前 / 优化后 / 变化量」，且优化前数值来自在改动前实际采集的基线（而非事后估算）

## MODIFIED Requirements

### Requirement: 拓扑排序与依赖计算性能

`harness.py` 的 `_topological_sort` SHALL 使用 `collections.deque` 作为队列（替代 `list.pop(0)` 的 O(n) 弹出）；`Fiber` SHALL 在初始化时缓存 `inject` 依赖服务名集合，避免每次 `notify` 重复计算。

#### Scenario: 行为不变性能提升

- **WHEN** 运行现有拓扑排序与插件通知相关测试
- **THEN** 测试结果与优化前完全一致，且 `_topological_sort` 不再出现 `pop(0)` 调用

### Requirement: 事件并行分发的 asyncio 兼容性

`events.py` 的 `_parallel` SHALL 在「调用方已存在运行中的事件循环」或「无事件循环」两种场景下均正确执行，不再无条件调用 `asyncio.run()`。

#### Scenario: 已有事件循环中不抛 RuntimeError

- **WHEN** 在 `asyncio.run(...)` 或运行中的协程内触发 `_parallel` 事件
- **THEN** 不抛 `RuntimeError: asyncio.run() cannot be called from a running event loop`，且监听器结果与同步场景等价

### Requirement: Attested Computation 运行时字段校验一致性

`attested.py` 的 `parse_attested_computation` SHALL 对缺失/非法的 `runtime` 字段抛出清晰的 `ValueError`（消息说明缺失或非法原因），而非因直接下标访问抛 `KeyError`。

#### Scenario: 缺失 runtime 报清晰错误

- **WHEN** frontmatter 缺少 `runtime` 字段时执行解析
- **THEN** 抛出 `ValueError` 且消息含 `runtime` 字段名与缺失说明

## REMOVED Requirements

（本次优化不删除任何既有公开能力；`events.py` 的 monkey-patch 实现方式被替换，但六种事件分发方法的对外语义保持不变。）