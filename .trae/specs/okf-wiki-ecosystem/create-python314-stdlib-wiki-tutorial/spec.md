# Python 3.14 标准库（上下文 / 监控 / 注解）中文 Wiki 教程 Spec

## Why

用户提供了一份 Python 3.14 官方中文文档的学习清单，涉及四个标准库模块：`contextlib`（上下文管理器工具集）、`sys.monitoring`（运行时代码监控事件）、`annotationlib`（注解与元数据处理，3.14 新增）、`contextvars`（上下文变量）。这四个模块共同指向同一主题——"在运行中的 Python 程序中管理动态的上下文状态与程序元数据"，但目前项目缺乏对它们的系统化中文学习资料。需要通过方法论编排（七概念 知识沉淀场景 R→I→E）全面学习官方文档，并沉淀为一份可复用的中文 Wiki 教程。

> 注：用户输入中 `sys.monitoring` 的 URL 重复出现 3 次，按唯一模块去重后，共 4 个学习对象。

## What Changes

- 新增一套中文 Wiki 教程，系统讲解 4 个 Python 3.14 标准库模块的定位、API、使用方式与彼此关系
- 教程放置于 `docs/knowledge/learning/python314-context-monitoring-annotation-wiki/`（公开内容 → 标准工作流）
- 采用原子化章节结构（`00-overview.md` … `NN-summary-resources.md`），并附一份方法论报告 `seven-concepts-report.md`
- 更新知识库导航索引 `docs/knowledge/index.md`，纳入新教程入口

## Impact

- Affected specs：新增能力（知识库学习文档），无既有 spec 修改
- Affected code：仅文档类新增（`docs/knowledge/learning/python314-context-monitoring-annotation-wiki/`），不涉及源码
- 学习对象（只读，以 WebFetch 抓取官方文档，不修改）：
  - `https://docs.python.org/zh-cn/3.14/library/contextlib.html`
  - `https://docs.python.org/zh-cn/3.14/library/sys.monitoring.html`
  - `https://docs.python.org/zh-cn/3.14/library/annotationlib.html`
  - `https://docs.python.org/zh-cn/3.14/library/contextvars.html`

## ADDED Requirements

### Requirement: 教程整体结构
系统 SHALL 提供一套覆盖"概述→版本背景→四个模块详解→跨模块分析→使用示例→FAQ→资源"的中文 Wiki 教程。

#### Scenario: 章节完整覆盖
- **WHEN** 用户打开教程目录
- **THEN** 教程具备原子化章节、编号连续、封面概述与收尾总结齐备

### Requirement: 版本背景与模块可用性
系统 SHALL 说明四个模块在 Python 各版本中的可用性差异（`contextlib`/`contextvars` 为长期存在的模块，`sys.monitoring` 自 3.12 引入，`annotationlib` 为 3.14 新增），避免用户误用到不兼容版本。

#### Scenario: 明确版本前提
- **WHEN** 用户阅读版本背景章节
- **THEN** 能判断每个模块所需的最低 Python 版本，不会在旧版本中误用 `sys.monitoring` 或 `annotationlib`

### Requirement: contextlib 讲解
系统 SHALL 讲解 `contextlib` 核心能力：上下文管理器协议、`@contextmanager` / `@asynccontextmanager` 装饰器、`ExitStack`、`AbstractContextManager`、`nullcontext`、`suppress`、`closing`、`redirect_stdout/stderr` 等工具。

#### Scenario: 读懂上下文管理器工具集
- **WHEN** 用户阅读 contextlib 章节
- **THEN** 能区分生成器式与类式上下文管理器，并正确使用 `ExitStack` 管理动态数量的上下文

### Requirement: contextvars 讲解
系统 SHALL 讲解 `contextvars` 核心能力：`ContextVar`、`Context` 对象、`copy_context()`、`ContextVar.set/get/reset` 返回的 Token 机制，以及其在 `asyncio` 并发任务中的隔离作用。

#### Scenario: 理解异步上下文隔离
- **WHEN** 用户阅读 contextvars 章节
- **THEN** 能理解上下文变量如何在并发异步任务间保持隔离，以及何时用 `copy_context()` 快照传播上下文

### Requirement: sys.monitoring 讲解
系统 SHALL 讲解 `sys.monitoring` 的事件驱动监控模型：监控事件类型（如 `PY_START`/`PY_RETURN`、`LINE`、`INSTRUCTION`、`BRANCH`、`PY_RESUME` 等）、工具 ID 管理（`use_tool_id`/`free_tool_id`）、回调注册（`register_callback`）、事件启停（`events`/`local_events`/`set_local_events`/`restart_events`），及其相对 `sys.settrace`/`sys.setprofile` 的性能优势与限制。

#### Scenario: 理解低开销运行时监控
- **WHEN** 用户阅读 sys.monitoring 章节
- **THEN** 能理解事件驱动监控与旧式 tracing API 的差异，并知道如何注册一个最小监控回调

### Requirement: annotationlib 讲解
系统 SHALL 讲解 `annotationlib`（3.14 新增）核心能力：`get_annotations()`、`Format` 枚举（`VALUE`/`FORWARDREF`/`SOURCE`/`STRING`）、`ForwardRef`、`call_annotate_function`、`AnnotationLibError`，以及惰性注解求值（PEP 749）的动机与语义。

#### Scenario: 理解惰性注解与多格式转换
- **WHEN** 用户阅读 annotationlib 章节
- **THEN** 能理解 3.14 引入惰性注解的背景，并能用 `get_annotations(format=...)` 获取不同形式的注解

### Requirement: 跨模块综合分析
系统 SHALL 提供一章跨模块分析，说明四个模块之间的关联（contextvars 与 contextlib 的状态管理协作、sys.monitoring 与 contextvars 在异步监控场景的配合、annotationlib 与动态元数据处理的定位差异）及统一设计哲学。

#### Scenario: 建立整体认知
- **WHEN** 用户阅读跨模块分析章节
- **THEN** 能说出四个模块在一个完整运行时动态能力图谱中的各自定位与协作关系

### Requirement: 代码示例与图示
系统 SHALL 提供可运行的代码示例（上下文管理器、ContextVar 异步隔离、注册监控回调、按格式获取注解）与必要的 Mermaid 机制图。

#### Scenario: 可操作示例
- **WHEN** 用户阅读使用示例章节
- **THEN** 能参照示例独立编写覆盖各模块最小可用用法的代码

### Requirement: FAQ 与注意事项
系统 SHALL 提供常见问题与注意事项：`sys.monitoring` 的线程/事件限制与性能开销、`contextvars` 在 `asyncio` 中的正确用法、`annotationlib` 与 `typing.get_type_hints` 的差异、`ExitStack` 与嵌套 `with` 的选择。

#### Scenario: 规避误导
- **WHEN** 用户阅读 FAQ 章节
- **THEN** 明确各模块的关键限制与易错点，不将官方文档尚未稳定的细节陈述为最终契约

### Requirement: 方法论报告
系统 SHALL 附一篇 `seven-concepts-report.md`，记录知识沉淀（R→I→E）链路与 G1-G3 质量门结果。

#### Scenario: 可审计的沉淀过程
- **WHEN** 用户查看方法论报告
- **THEN** 能看到事实采集、根因洞察、模式萃取的质量门通过记录