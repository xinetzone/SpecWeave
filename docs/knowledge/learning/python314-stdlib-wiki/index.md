# Python 3.14 标准库教程 — 概述

> 一句话摘要：本教程系统讲解 Python 3.14 标准库中六个与日常开发密切相关的模块——`contextlib`（上下文管理器）、`contextvars`（上下文变量）、`sys.monitoring`（事件监控）、`annotationlib`（注解内省）、`dataclasses`（声明式数据类）与 `traceback`（栈回溯诊断），帮助你在一个运行中的 Python 程序里可靠地管理动态上下文状态、程序元数据，并以更少样板定义数据结构、以更可控方式诊断运行时错误。

## 一、教程介绍与共同主题

日常编写 Python 程序时，除了"把一件事算出来"，我们还经常需要回答三类问题：**在进入/退出某段代码时该做什么**、**并发的多个执行单元各自持有怎样的状态**、以及**程序里被声明（注解）、被观测（监控）、被定义（数据类）或被诊断（回溯）的信息是什么**。

本教程围绕这条主线，串联起 Python 3.14 标准库中的六个模块，并归为两大能力簇：

| 模块 | 角色定位（简） | 详细章节 |
|---|---|---|
| `contextlib` | 提供围绕 `with` 语句与上下文管理器协议的一整套工具，负责"进入与退出时做什么" | [02-contextlib](/concepts/02-contextlib.md) |
| `contextvars` | 提供"上下文局部变量"机制，让每个异步任务/上下文的取值彼此隔离 | [03-contextvars](/concepts/03-contextvars.md) |
| `sys.monitoring` | 低开销、事件驱动的运行时监控命名空间，负责"何时何地发生了什么" | [04-sys-monitoring](/concepts/04-sys-monitoring.md) |
| `annotationlib` | 可靠内省模块/类/函数上的类型注解（惰性求值），负责"程序声明了什么" | [05-annotationlib](/concepts/05-annotationlib.md) |
| `dataclasses` | 用一个 `@dataclass` 装饰器根据类型标注自动生成数据类，负责"声明式定义数据结构" | [06-dataclasses](/concepts/06-dataclasses.md) |
| `traceback` | 提取、格式化与打印异常栈回溯，负责"结构化诊断运行时错误" | [07-traceback](/concepts/07-traceback.md) |

六个模块的共同取向可以概括为四点：

1. **消除样板（boilerplate）**：`contextlib` 用一个生成器即可得到上下文管理器，`dataclasses` 用一个装饰器即可得到完整数据类，`traceback` 用标准接口替代手搓 `sys.exc_info()` 拼字符串。
2. **以数据/元数据为核心**：`dataclasses` 的核心是"字段"、`traceback` 的核心是"栈帧/回溯"、`annotationlib` 的核心是"注解元数据"、`contextvars` 的核心是"上下文取值"——能力都被沉淀为可组合的数据对象。
3. **轻量、低开销**：`copy_context()` 复杂度为 O(1)，`sys.monitoring` 在关掉绝大多数监控后开销可趋近于零，`annotationlib` 惰性求值避免导入期执行注解的开销，`TracebackException` 通过不持帧引用降低内存驻留。
4. **上下文/事件驱动，而非全局一把抓**：`contextvars` 用"当前上下文"代替进程级全局变量，`sys.monitoring` 只在显式开启的事件上触发回调；`contextlib` 的 `redirect_stdout`/`chdir` 虽是全局改动的特例，但官方明确警告其不适合库代码与并发程序。

## 二、核心术语表

下表融合六个章节的核心术语，用平实的大白话解释，避免"用术语解释术语"：

| 术语 | 一句话平实解释 |
|---|---|
| 上下文管理器（Context Manager） | 定义了"进入前"和"退出后"两个动作的对象，配合 `with` 语句负责资源的安全回收 |
| `with` 语句 | Python 的语法糖，自动在代码块前后调用上下文管理器的进入与退出动作 |
| 上下文管理协议 | 约定对象只要实现 `__enter__` 和 `__exit__` 两个方法，就能被 `with` 使用 |
| 生成器（Generator） | 用 `yield` 写成、可以中途暂停再恢复执行的函数，`@contextmanager` 靠它实现清理 |
| 装饰器（Decorator） | 接收一个函数并返回增强后函数的工具，可改造函数行为 |
| 回调（Callback） | 预先登记、稍后由某个机制（如监控事件）调用的一段可执行代码 |
| 上下文变量（Context Variable） | 由 `ContextVar` 声明的变量；声明本身唯一，但其取值在不同上下文里可各自不同 |
| 上下文（Context） | 记录"每个上下文变量当前取值"的映射对象，不同上下文之间取值互不干扰 |
| 当前上下文（current context） | 每个线程都有一个上下文栈，栈顶那个即"当前上下文"，`ContextVar` 的读写都作用于它 |
| Token | `ContextVar.set()` 返回的"还原凭据"，用它可把变量恢复到设置前的值 |
| 事件（event） | 程序运行到某位置、执行某动作时产生的信号，如"某函数开始执行""某行即将执行" |
| 工具 ID（tool identifier） | 0~5 之间的整数编号（带名称），让调试器、覆盖率工具等各用各的编号、互不干扰 |
| 注解（annotation） | 依附在模块/类/函数/变量上的额外标签，最常见的是类型提示 |
| 惰性求值（lazy evaluation） | 注解表达式不在一开始执行，而是等到有人真正访问注解时才去执行 |
| 前向引用（forward reference） | 注解中引用了一个"当下还没定义、稍后才出现"的名字 |
| 数据类（dataclass） | 用 `@dataclass` 装饰的普通类，会自动获得 `__init__`、`__repr__`、`__eq__` 等常用方法 |
| 字段（field） | 类里带类型标注的变量，代表每个实例各自拥有的一个数据槽位 |
| 默认工厂（default_factory） | 一个不带参数的函数，每次需要默认值时被调用一次，从而生成一个全新的默认值 |
| 哨兵值（sentinel） | 一个特殊的占位对象，专门用来表示"这个参数没有被调用方提供" |
| 类变量（ClassVar） | 属于类本身而非某个实例的变量，所有实例共享同一个值 |
| 仅初始化变量（InitVar） | 只在对象初始化阶段参与、不会作为实例属性保留下来的临时参数 |
| slots | 一种让实例不再自带 `__dict__` 字典、从而节省内存并略微提升访问速度的机制 |
| 栈回溯（traceback） | 程序出错时，从出错位置一路回溯到调用起点的函数调用链记录 |
| 回溯对象（traceback object） | 表示"异常发生时调用栈"的数据结构，类型为 `types.TracebackType`，可通过 `tb_next` 逐层追溯 |
| 栈帧（frame） | 一次函数调用所对应的执行环境，记录"正在执行哪个文件的哪一行、函数叫什么名字" |
| 栈摘要（StackSummary） | 把一整个调用栈整理成有序的帧摘要列表，是栈的"可格式化"表示 |
| 帧摘要（FrameSummary） | 栈中的单个帧的轻量描述，记录文件名、行号、函数名、源代码行等信息 |
| 链式异常（chained exception） | 一个异常在处理另一个异常的过程中被引发，两者之间的"前因后果"关联 |
| 异常组（exception group） | 一个容器型异常，内部可包裹多个子异常，用于在一次操作中同时报告多个错误 |

## 三、章节导航表

| 编号 | 章节 | 内容概要 | 难度 |
|---|---|---|---|
| 00 | [概述](/index.md) | 教程介绍、六模块共同主题、术语表、阅读路径 | ★☆☆☆☆ |
| 01 | [版本背景与模块可用性](/concepts/01-version-prerequisites.md) | 六模块的引入版本与 3.14 关键变更、版本检查、import 提示 | ★☆☆☆☆ |
| 02 | [contextlib 全面详解](/concepts/02-contextlib.md) | `with` 协议、`@contextmanager`、`ExitStack`、`redirect_stdout` 等全部 API | ★★☆☆☆ |
| 03 | [contextvars 全面详解](/concepts/03-contextvars.md) | `ContextVar`/`Token`/`Context`、上下文传播、asyncio 任务隔离 | ★★★☆☆ |
| 04 | [sys.monitoring 全面详解](/concepts/04-sys-monitoring.md) | 工具 ID、事件类型、回调签名、局部事件与 `DISABLE` 优化 | ★★★★☆ |
| 05 | [annotationlib 全面详解](/concepts/05-annotationlib.md) | 惰性注解求值、`Format` 四种格式、`ForwardRef`、`get_annotations` | ★★★★☆ |
| 06 | [dataclasses 全面详解](/concepts/06-dataclasses.md) | `@dataclass`/`field()`/伪字段/模块级函数/继承/示例/版本说明/反模式 | ★★☆☆☆ |
| 07 | [traceback 全面详解](/concepts/07-traceback.md) | 三组函数/三个类/异常链/示例/版本说明/反模式 | ★★★☆☆ |
| 08 | [跨模块综合分析](/concepts/08-cross-module-analysis.md) | 六模块定位对比、协作关系、统一设计哲学、Mermaid 图谱 | ★★★☆☆ |
| 09 | [综合使用示例](/examples/09-usage-examples.md) | 多模块组合的可运行示例 | ★★★☆☆ |
| 10 | [FAQ 与排错](/references/10-faq-troubleshooting.md) | 高频疑问解答与常见错误对策 | ★★☆☆☆ |
| 11 | [总结与资源](/references/11-summary-resources.md) | 知识点回顾、速查表、官方资源链接、学习路径 | ★☆☆☆☆ |

## 四、阅读路径建议

按你的目标选择路径，不必从头到尾逐字阅读：

- **路径 A：快速上手"资源管理"**（面向日常写 `with` 的开发者）
  → [00 概述](/index.md) → [01 版本背景](/concepts/01-version-prerequisites.md) → [02 contextlib](/concepts/02-contextlib.md) → [09 综合示例](/examples/09-usage-examples.md) 中的示例一

- **路径 B：深入并发与异步状态隔离**（面向 asyncio/多任务开发者）
  → [00 概述](/index.md) → [01 版本背景](/concepts/01-version-prerequisites.md) → [03 contextvars](/concepts/03-contextvars.md) → [04 sys.monitoring](/concepts/04-sys-monitoring.md) → [08 跨模块分析](/concepts/08-cross-module-analysis.md)

- **路径 C：工具与元编程作者**（面向想做调试器/分析器/类型工具的人）
  → [00 概述](/index.md) → [04 sys.monitoring](/concepts/04-sys-monitoring.md) → [05 annotationlib](/concepts/05-annotationlib.md) → [10 FAQ](/references/10-faq-troubleshooting.md) → [11 总结与资源](/references/11-summary-resources.md)

- **路径 D：声明式数据建模与异常诊断**（面向定义结构体、写日志/告警的开发者）
  → [00 概述](/index.md) → [06 dataclasses](/concepts/06-dataclasses.md) → [07 traceback](/concepts/07-traceback.md) → [09 综合示例](/examples/09-usage-examples.md) 中的示例四~七

## 五、前置知识说明

阅读本教程前，建议具备以下基础：

- 熟悉 Python 基础语法与 `with`/`import` 等语句。
- 对"同步/异步"与"并发"有基本概念即可；`asyncio` 的具体用法不是本教程的重点，涉及处会给出解释。
- 了解"类型注解"（`def f(a: int) -> str`、`name: str` 这种写法）的大致含义，有助于理解 `annotationlib` 与 `dataclasses` 两章。
- 对"异常"与 `try`/`except`、`raise` 有基本概念，有助于理解 `traceback` 一章。
- 本教程示例均面向 **Python 3.x**；部分示例强依赖较新版本（如 `Token` 上下文管理器与 `annotationlib` 需 3.14、`sys.monitoring` 需 3.12、`@dataclass(slots=)` 需 3.10、`field(doc=)` 需 3.14、`traceback` 彩色输出需 3.13），这些地方均已在对应章节显式标注，详见 [01 版本背景](/concepts/01-version-prerequisites.md)。

> 提示：六个模块的全部 API、版本号与语义均以 Python 3.14 官方文档为唯一事实来源，并已在对应章节逐条核对；本概述中的任何结论都不超出各章节的既有描述。

## 六、章节导航

- [下一章：版本背景与模块可用性](/concepts/01-version-prerequisites.md) →

```{toctree}
:maxdepth: 2

concepts/index
examples/index
references/index
log
```