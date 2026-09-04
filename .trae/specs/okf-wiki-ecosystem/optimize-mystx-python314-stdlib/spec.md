# mystx 主题基于 Python 3.14 标准库的系统性优化 Spec

## Why

`mystx`（`d:\spaces\SpecWeave\playground\books\libs\mystx\src\mystx`）是一个基于 `sphinx_book_theme` 的 Sphinx HTML 主题，已具备主题注册、`_config.toml` 配置合并、Thebe/版本切换器集成与 4 条 GitHub Readme Stats 指令等能力。但当前仅 2 项单元测试、存在「`tomllib`（需 3.11+）与 `requires-python >=3.10` 不一致」「`myst_nb` 在顶层被无条件 import 而 `dependencies=[]` 未声明」「异常重抛丢失回溯链」等问题，且尚未利用已掌握的 Python 3.14 标准库能力（`dataclasses.slots`、`traceback` 结构化诊断等）。通过系统学习 `d:\spaces\SpecWeave\docs\knowledge\learning\python314-stdlib-wiki` 的六个模块后，提炼一组**可量化、可验证**的优化机会，在不破坏既有接口与行为的前提下，实现代码结构、兼容性、诊断、内存与测试覆盖五方面提升。

## What Changes

优化工作分为两条并行链路，最终合并为「优化前后对比记录」：

- **学习笔记链路**：产出「Python 3.14 六模块 → mystx 优化机会」映射笔记（详细交付物），沿用同目录 `12-okf-optimization-mapping.md` 的既定格式；每个模块必须有明确落点或诚实记录，禁止为凑齐六模块而强行引入无收益改动。
- **代码优化链路**：落地以下变更（均以「学习事实 + 基线支撑」为准，避免拍脑袋改造）：
  - 为 `ConfigManager` / `MySTX` 两个 `@dataclass` 增加 `slots=True`（内存优化、去 `__dict__`），并修正 `ConfigManager.logger` 字段的 `None` 默认值与类型标注不一致（代码结构改进）。
  - `config.py` / `theme.py` 的异常路径改用结构化诊断：`raise ... from e` 保留异常链、用 `logger(... , exc_info=True)` 或 `traceback.TracebackException` 输出完整回溯（功能完善）。
  - 修复 `tomllib`（3.11+）与 `requires-python`（3.10）及 README「3.12+」三处版本声明不一致（兼容性/正确性修复）。
  - 将 `mystx/__init__.py` 对 `myst_nb` 的顶层无条件 import 改为**可选/惰性加载**，避免 `dependencies=[]` 下 `import mystx` 因缺 `myst_nb` 直接崩溃（潜在缺陷修复）。
  - 清理 `version_switcher.py` 未使用 import 与死注释、为空的 `ext/__init__.py` 补模块 docstring（代码结构/文档完善）。
  - 将单元测试从 2 项扩展至覆盖指令、配置合并、主题解析、版本推断与可选 import 的回归用例（测试覆盖）。

## Impact

- **Affected specs**：无既有 capability 被破坏；本优化是 `mystx` 自身的增量改进。
- **Affected code**：
  - `playground/books/libs/mystx/src/mystx/__init__.py`（可选 `myst_nb` 加载）
  - `playground/books/libs/mystx/src/mystx/config.py`（dataclass slots、traceback 诊断）
  - `playground/books/libs/mystx/src/mystx/theme.py`（dataclass slots、异常链）
  - `playground/books/libs/mystx/src/mystx/version_switcher.py`（清理）
  - `playground/books/libs/mystx/src/mystx/ext/__init__.py`（docstring）
  - `playground/books/libs/mystx/pyproject.toml`（requires-python 修正）
  - `playground/books/libs/mystx/README.md`（版本声明一致性，可选）
  - `playground/books/libs/mystx/tests/`（新增单元测试）
- **测试基线**：现有 `tests/unit/test_github_cards.py` 的 2 项测试必须全部通过；lint（`flake8`/`ruff`）与 `black`/`isort` 风格无新增告警；优化后覆盖 `src/mystx` 核心逻辑（指令、配置合并、主题解析、版本推断）且新增测试全绿。
- **接口稳定性**：`setup(app)`、`MySTX`、`ConfigManager`、四条指令的对外签名与语义保持不变；`requires-python` 的收紧为唯一标注的 **BREAKING**（见下）。

## ADDED Requirements

### Requirement: Python 3.14 标准库到 mystx 优化机会的学习笔记

系统 SHALL 基于 `python314-stdlib-wiki` 六个模块知识，形成一份「学习笔记」，明确每项 stdlib 能力在 mystx 代码中的落点、优化动作与收益预判，并对无明确收益的模块给出诚实记录。

#### Scenario: 笔记覆盖六模块映射

- **WHEN** 完成对六个模块章节的学习
- **THEN** 笔记中出现至少六条「stdlib 能力 → mystx 具体文件/函数 → 优化动作/诚实记录」映射，且每条引用对应章节事实；其中 `dataclasses`（→ `slots=True` 省内存 / `field(doc=)` 3.14 新增落点评估）、`traceback`（→ `raise ... from e` + `TracebackException`/`exc_info=True` 结构化诊断）为代码落点；`contextlib`（→ 文件资源已用 `with` 管理，无额外落点）、`contextvars`（→ 无任务级状态隔离需求）、`annotationlib`（→ 无 `future import` 遗留，评估结论）、`sys.monitoring`（→ 未来剖析/测试插桩条件性落点）为诚实记录落点

### Requirement: 数据类启用 slots 并修正字段类型

`ConfigManager` 与 `MySTX` SHALL 启用 `slots=True`；`ConfigManager.logger` SHALL 修正为 `Optional[...]` 类型并保持「默认为 `None`、`__post_init__` 内赋值」语义不变，消除类型标注与默认值不一致。

#### Scenario: 实例无 __dict__ 且接口不变

- **WHEN** 实例化 `MySTX(app)` / `ConfigManager(app, config)`
- **THEN** `hasattr(instance, "__dict__")` 为 `False`，内存低于优化前基线；且 `ConfigManager(app, config)` 的构造调用签名不变、`instance.logger` 仍为有效的 SphinxLoggerAdapter

#### Scenario: 字段文档化采用版本无关方式

- **WHEN** 阅读类 docstring 或模块文档
- **THEN** 关键字段（`app`/`config`/`name`/`theme_dir`）的用途有平实说明；`field(doc=...)`（3.14 独占）不用于当前 `requires-python >= 3.11` 的代码中，而在学习笔记中记录为「条件性未来落点（requires-python 提升至 3.14 时启用）」

### Requirement: 异常路径的结构化诊断与异常链保留

`config.py` 的 `load_custom_config` / `config_inited_handler` 与 `theme.py` 的 `MySTX.__post_init__` SHALL 在捕获并重抛异常时使用 `raise ... from e` 保留异常链，并输出含类型/消息/定位的完整回溯。

#### Scenario: 异常链与完整定位可见

- **WHEN** `_config.toml` 解析出错或主题目录不存在时异常被捕获再抛出
- **THEN** 抛出异常的 `__cause__` 为原始异常（异常链保留），且日志包含原始异常的类型、消息与文件名/行号（非仅一行 `str(e)`）

### Requirement: 版本声明一致性修复

`tomllib`（Python 3.11 引入）的实际依赖 SHALL 与 `pyproject.toml` 的 `requires-python` 及 README 的运行环境声明保持一致。

#### Scenario: 声明与实际依赖对齐

- **WHEN** 检查 `requires-python` 与 `tomllib` 可用版本
- **THEN** `requires-python` 不再宣称对不含 `tomllib` 的版本（3.10）可用；最终取值与 README 声明一致（推荐收紧为 `>=3.11`）

### Requirement: myst_nb 的可选/惰性加载

`mystx/__init__.py` SHALL 不再在模块顶层无条件 `import myst_nb`，改在 `setup(app)` 内按可用性惰性加载，使 `dependencies=[]` 的纯主题安装下 `import mystx` 不因缺失 `myst_nb` 而崩溃。

#### Scenario: 缺 myst_nb 时主题仍可导入

- **WHEN** 环境中未安装 `myst-nb`
- **THEN** `import mystx` 成功且不抛 `ModuleNotFoundError`；`setup(app)` 仅跳过 Markdown/Notebook 支持相关初始化而主题注册正常

### Requirement: 单元测试覆盖扩展

测试套件 SHALL 从现有 2 项扩展，覆盖 `base` 的 URL 构建/图片节点、四条指令的 `run()`（合法与缺必填项错误路径）、`ConfigManager` 的配置合并（含嵌套）、`MySTX` 的主题目录解析、`version_switcher` 的版本推断，以及缺 `myst_nb` 时的导入兜底。

#### Scenario: 核心逻辑被测试覆盖

- **WHEN** 运行 `pytest`
- **THEN** 新增用例全部通过，无可查到的回归；`src/mystx` 核心逻辑（指令/配置合并/主题解析/版本推断）的语句覆盖率不低于 80%

## MODIFIED Requirements

### Requirement: 既有公开接口保持稳定

`setup(app)`、`MySTX(app, name="mystx")`、`ConfigManager(app, config)`、`gitHub-stats`/`github-top-langs`/`github-pinned-repo`/`github-wakatime` 四条指令的签名、默认值与对外语义 SHALL 保持不变。

#### Scenario: 行为不变

- **WHEN** 运行既有文档构建相关语义（主题注册、配置应用、指令 URL 生成）
- **THEN** 结果与优化前一致；仅内存占用（`__dict__` 消除）与诊断输出（异常链/回溯）发生预期提升

## REMOVED Requirements

（本次优化不删除任何既有公开能力；`version_switcher.py` 仅移除未使用 import 与死注释，`ext/__init__.py` 仅补 docstring，四条指令及主题注册语义完整保留。）