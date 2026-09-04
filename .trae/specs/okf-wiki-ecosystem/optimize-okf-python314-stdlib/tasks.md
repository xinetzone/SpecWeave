# Tasks

- [x] Task 1: 采集优化前基线（可量化基准）
  - [x] SubTask 1.1: 在 `d:\AI\projects\xuanspace\tools\okf` 运行 `pytest -q`，记录测试通过数与文件名
  - [x] SubTask 1.2: 运行 `pytest --cov=okf --cov-report=term`，记录覆盖率百分比
  - [x] SubTask 1.3: 运行 `ruff check src tests`，记录告警/错误数量
  - [x] SubTask 1.4: 编写/运行一次性脚本，采集代表数据类（如 `Concept`、`Bundle`）实例的内存占用（`sys.getsizeof` 及字段递归求和）作为基线

- [x] Task 2: 形成 Python 3.14 标准库学习笔记（映射到 okf 优化机会）
  - [x] SubTask 2.1: 从 `python314-stdlib-wiki` 六个模块提炼「stdlib 能力 → okf 落点」映射表
  - [x] SubTask 2.2: 单独补足 `contextlib`/`contextvars`/`annotationlib` 三模块落点：`contextlib` → `Context`/`Harness` 上下文管理器协议；`contextvars` → 命名澄清 + 显式 DI 取舍 + 条件性未来落点；`annotationlib` → 3.14 惰性求值 + future import 遗留评估
  - [x] SubTask 2.3: 将学习笔记落盘为交付文档（Markdown，含 frontmatter），路径与格式遵循知识库现有约定

- [x] Task 3: 数据类启用 `slots=True` 并补充 `field(doc=)`（`models.py` / `service.py` / `plugin.py` / `disposable.py`）
  - [x] SubTask 3.1: 为上述文件中所有 `@dataclass(frozen=True)` 类添加 `slots=True`
  - [x] SubTask 3.2: 为关键业务字段补充 `field(doc=...)`（`Concept` / `Bundle` / `Source` / `UsageWindow` 等对外模型优先）
  - [x] SubTask 3.3: 运行相关测试（`test_models.py` / `test_service.py` / `test_plugin.py` / `test_disposable.py`），确认无回归

- [x] Task 4: 消除 `events.py` 对 `Context` 的 monkey-patch（代码结构）
  - [x] SubTask 4.1: 将六种事件分发方法移入 `context.py` 的 `Context` 类（或引入 mixin），保持签名与语义一致
  - [x] SubTask 4.2: 精简 `events.py`，移除对 `Context` 的动态赋值；更新依赖 import
  - [x] SubTask 4.3: 运行 `test_events.py` / `test_context.py`，确认事件行为不变且无 import-order 脆弱性

- [x] Task 5: 拓扑排序与依赖计算性能优化（`harness.py` / `plugin.py`）
  - [x] SubTask 5.1: `_topological_sort` 使用 `collections.deque` 替代 `list.pop(0)`
  - [x] SubTask 5.2: `Fiber` 初始化时缓存 `inject` 服务名集合，`notify` 复用缓存
  - [x] SubTask 5.3: 运行 `test_harness.py` / `test_plugin.py`，确认结果一致

- [x] Task 6: 集成 `traceback` 结构化错误诊断（`cli.py` / `harness.py`）
  - [x] SubTask 6.1: `harness.py` 插件加载失败时用 `traceback.print_exc` / `TracebackException` 输出完整回溯
  - [x] SubTask 6.2: `cli.py` 关键命令异常路径（如服务未注册）补充结构化诊断
  - [x] SubTask 6.3: 运行 `test_cli.py` / `test_harness.py`，确认诊断增强不破坏既有断言

- [x] Task 7: 修复潜在问题（`events.py` `_parallel` 与 `attested.py` `runtime` 校验）
  - [x] SubTask 7.1: `_parallel` 检测运行中事件循环，避免无条件 `asyncio.run()`；同步评估是否需为异步监听器引入 `ContextVar`（`contextvars` 条件性落点）
  - [x] SubTask 7.2: `parse_attested_computation` 对缺失/非法 `runtime` 抛 `ValueError` 并给清晰消息
  - [x] SubTask 7.3: 运行 `test_events.py` / `test_attested.py`，并新增回归用例覆盖上述两处

- [x] Task 8: `Context` 与 `Harness` 实现上下文管理器协议（`contextlib` 落地）
  - [x] SubTask 8.1: 为 `Context` 增加 `__enter__`/`__exit__`（`__exit__` 调 `dispose()`），为 `Harness` 增加 `__enter__`/`__exit__` 与公开 `dispose()`
  - [x] SubTask 8.2: 运行 `test_context.py` / `test_harness.py`，并新增 `with` 自动回收、`Harness.dispose()` 幂等的回归用例

- [x] Task 9: 评估并（如可行）移除 `from __future__ import annotations`（`annotationlib` 落地）
  - [x] SubTask 9.1: 列出 okf 各模块 future import 清单，评估 3.14 惰性求值下移除的风险（前向引用、`TYPE_CHECKING` 分支）
  - [x] SubTask 9.2: 仅在评估为「收益明确且无回归」时移除，否则在学习笔记中记录「保留原因」；若移除则全量 `pytest` 验证
  - [x] SubTask 9.3: 在学习笔记中记录 annotationlib 定位与后续注解内省的推荐入口（`get_annotations(..., format=...)`）

- [x] Task 10: 优化后复测并生成对比记录（可量化、可验证）
  - [x] SubTask 10.1: 重复 Task 1 的测试/覆盖率/ruff/内存采集，得到「优化后」数值
  - [x] SubTask 10.2: 生成「优化前后对比记录」文档，逐项列出优化前/优化后/变化量
  - [x] SubTask 10.3: 全量 `pytest` 确认 187 项全部通过、`ruff check` 无新增告警

# Task Dependencies

- [Task 2]、[Task 3]、[Task 4]、[Task 5]、[Task 6]、[Task 7]、[Task 8]、[Task 9] 均依赖 [Task 1]（基线先行）。
- [Task 10] 依赖 [Task 3~9] 全部完成。
- [Task 2]（文档）、[Task 9]（评估）与 [Task 3~8] 之间，除基线外无相互依赖；[Task 3]~[Task 8] 之间无相互依赖，可并行执行。