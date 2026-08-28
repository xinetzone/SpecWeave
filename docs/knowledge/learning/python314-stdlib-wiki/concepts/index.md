# Concepts

- [01-version-prerequisites](/concepts/01-version-prerequisites.md) — 版本背景与模块可用性：六个模块的 Python 版本要求与兼容性说明。
- [02-contextlib](/concepts/02-contextlib.md) — contextlib 全面详解：上下文管理器协议、`@contextmanager`、`ExitStack` 等工具。
- [03-contextvars](/concepts/03-contextvars.md) — contextvars 全面详解：上下文局部变量、`ContextVar`、`Token` 与异步隔离。
- [04-sys-monitoring](/concepts/04-sys-monitoring.md) — sys.monitoring 全面详解：事件驱动的低开销运行时监控命名空间。
- [05-annotationlib](/concepts/05-annotationlib.md) — annotationlib 全面详解：Python 3.14 新增的注解内省工具。
- [06-dataclasses](/concepts/06-dataclasses.md) — dataclasses 全面详解：声明式数据类、字段定义与 `@dataclass` 装饰器。
- [07-traceback](/concepts/07-traceback.md) — traceback 全面详解：栈回溯信息的提取、格式化与打印。
- [08-cross-module-analysis](/concepts/08-cross-module-analysis.md) — 跨模块综合分析：六模块定位总览与跨簇协作关系。
- [12-okf-optimization-mapping](/concepts/12-okf-optimization-mapping.md) — Python 3.14 标准库到 OKF 工具链优化机会映射。
- [14-mystx-optimization-mapping](/concepts/14-mystx-optimization-mapping.md) — Python 3.14 标准库到 mystx 主题优化机会映射。

```{toctree}
:maxdepth: 2

01-version-prerequisites
02-contextlib
03-contextvars
04-sys-monitoring
05-annotationlib
06-dataclasses
07-traceback
08-cross-module-analysis
12-okf-optimization-mapping
14-mystx-optimization-mapping
```