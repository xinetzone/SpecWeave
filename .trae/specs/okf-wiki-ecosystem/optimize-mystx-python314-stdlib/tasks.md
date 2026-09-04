# Tasks

- [x] Task 1: 采集优化前基线（可量化基准）
  - [x] SubTask 1.1: 在 `playground/books/libs/mystx` 运行 `pytest -q`，记录测试通过数与文件名（2 项 `test_github_cards.py`，均 FAIL）
  - [x] SubTask 1.2: 运行 `pytest --cov=mystx --cov-report=term`，记录覆盖率（优化前 0%，测试失败）
  - [x] SubTask 1.3: 运行 lint（`flake8 src tests`），记录告警数（src 存在预置 E302/W293/W292）
  - [x] SubTask 1.4: 记录缺 `myst_nb` 时 `import mystx` 抛 `ModuleNotFoundError`；记录 `ConfigManager`/`MySTX` 无 slots 时 `hasattr(__dict__)` 为 True

- [x] Task 2: 形成 Python 3.14 标准库学习笔记（映射到 mystx 优化机会）
  - [x] SubTask 2.1: 从 `python314-stdlib-wiki` 六模块提炼「stdlib 能力 → mystx 落点 → 优化动作/诚实记录」映射表
  - [x] SubTask 2.2: 明确 `dataclasses`/`traceback` 为代码落点；`contextlib`/`contextvars`/`annotationlib`/`sys.monitoring` 为诚实记录落点
  - [x] SubTask 2.3: 落盘为 `14-mystx-optimization-mapping.md`（含 frontmatter + `source` 字段）

- [x] Task 3: 数据类启用 `slots=True` 并修正字段类型（`config.py` / `theme.py`）
  - [x] SubTask 3.1: 为 `ConfigManager`、`MySTX` 增加 `slots=True`
  - [x] SubTask 3.2: `ConfigManager.logger` 修正为 `Optional[logging.SphinxLoggerAdapter] = None`
  - [x] SubTask 3.3: 运行 `pytest` 与 `import mystx` 冒烟，确认无回归且 `hasattr(instance, "__dict__")` 为 `False`

- [x] Task 4: 异常路径结构化诊断与异常链保留（`config.py` / `theme.py`）
  - [x] SubTask 4.1: `load_custom_config`/`config_inited_handler`/`MySTX.__post_init__` 重抛保留异常链（bare `raise` 保留 `__context__`）
  - [x] SubTask 4.2: 重抛处用 `logger(..., exc_info=True)` 输出含类型/消息/定位的完整回溯
  - [x] SubTask 4.3: 由 `test_config.py::test_load_custom_config_invalid_toml` 验证 TOML 解析错误路径

- [x] Task 5: 版本声明一致性修复（`pyproject.toml` / README）
  - [x] SubTask 5.1: `requires-python` 由 `>=3.10` 收紧为 `>=3.14`；README 运行环境声明由「3.12+」同步为「3.14+」
  - [x] SubTask 5.2: pre-commit 中 black `python3.10` 语言版本不影响 3.14 语法（本优化未引入 3.14 独占语法，无影响）

- [x] Task 6: `myst_nb` 可选/惰性加载（`__init__.py`）
  - [x] SubTask 6.1: 移除顶层 `from myst_nb.sphinx_ext import ...`，改为 `setup(app)` 内 `_setup_myst_nb` 惰性 `try/except ImportError`
  - [x] SubTask 6.2: 由 `test_import_fallback.py` 验证缺 `myst-nb` 时 `import mystx` 不再抛 `ModuleNotFoundError`

- [x] Task 7: 代码清理与文档完善（`version_switcher.py` / `ext/__init__.py` 及模块 docstring）
  - [x] SubTask 7.1: 移除 `version_switcher.py` 未使用 `Path`/`ExtensionMetadata` 导入与死注释，返回值类型修正为 `None`
  - [x] SubTask 7.2: 为 `ext/__init__.py` 补模块 docstring；修正 `base.py` 布尔序列化文档（`key=true` → `key=True`）

- [x] Task 8: 单元测试覆盖扩展（`tests/`）
  - [x] SubTask 8.1: 重写 `test_github_cards.py`：`build_url`/`create_image_node`、四条指令 `run()`（合法 + 缺必填项）
  - [x] SubTask 8.2: 新增 `test_config.py`、`test_theme.py`、`test_version_switcher.py`
  - [x] SubTask 8.3: 新增 `test_import_fallback.py`；运行全量 `pytest` 确认 26 passed

- [x] Task 9: 优化后复测并生成对比记录（可量化、可验证）
  - [x] SubTask 9.1: 复测 `pytest`（26 passed）、覆盖率（74%，核心 83%~100%）、flake8（测试文件 0 告警）
  - [x] SubTask 9.2: 生成 `15-mystx-optimization-report.md`
  - [x] SubTask 9.3: 全量 `pytest` 通过、测试文件无新增告警、既有接口语义不变

# Task Dependencies

- [Task 2]、[Task 3]、[Task 4]、[Task 5]、[Task 6]、[Task 7]、[Task 8] 均依赖 [Task 1]（基线先行）。
- [Task 9] 依赖 [Task 2~8] 全部完成。
- [Task 2]（文档）、[Task 5]（版本声明）与 [Task 3]/[Task 4]/[Task 6]/[Task 7]/[Task 8] 之间无相互依赖；[Task 3]~[Task 8]（除基线外）可并行执行。