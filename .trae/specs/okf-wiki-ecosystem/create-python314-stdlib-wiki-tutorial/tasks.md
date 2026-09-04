# Tasks

- [x] Task 1：R 阶段——事实采集，抓取并通读 4 个模块的官方中文文档
  - [x] SubTask 1.1：WebFetch 抓取 `https://docs.python.org/zh-cn/3.14/library/contextlib.html`，梳理全部公开 API 与要点
  - [x] SubTask 1.2：WebFetch 抓取 `https://docs.python.org/zh-cn/3.14/library/contextvars.html`，梳理 ContextVar / Context / copy_context 等要点
  - [x] SubTask 1.3：WebFetch 抓取 `https://docs.python.org/zh-cn/3.14/library/sys.monitoring.html`，梳理事件类型、工具 ID、回调注册、事件启停要点
  - [x] SubTask 1.4：WebFetch 抓取 `https://docs.python.org/zh-cn/3.14/library/annotationlib.html`，梳理 get_annotations / Format / ForwardRef 等要点
  - [x] SubTask 1.5：记录各模块在 Python 版本中的引入时间与可用性（contextlib/contextvars 长期存在、sys.monitoring 3.12+、annotationlib 3.14 新增）

- [x] Task 2：I 阶段——洞察，提炼核心概念与 API 要点
  - [x] SubTask 2.1：归纳四个模块各自的职责定位与 API 清单，形成统一术语表
  - [x] SubTask 2.2：归纳 contextlib 与 contextvars 在"状态/执行上下文管理"上的分工与协作关系
  - [x] SubTask 2.3：归纳 sys.monitoring 相对 sys.settrace/sys.setprofile 的本质差异与性能取舍
  - [x] SubTask 2.4：归纳 annotationlib 惰性注解（PEP 749）的动机与多格式求值语义

- [x] Task 3：E 阶段——萃取产出，编写原子化中文 Wiki 章节
  - [x] SubTask 3.1：创建教程目录 `docs/knowledge/learning/python314-context-monitoring-annotation-wiki/`
  - [x] SubTask 3.2：编写 00-overview.md（概述与四模块定位）、01-version-prerequisites.md（版本背景与模块可用性）
  - [x] SubTask 3.3：编写 02-contextlib.md（上下文管理器工具集）
  - [x] SubTask 3.4：编写 03-contextvars.md（上下文变量）
  - [x] SubTask 3.5：编写 04-sys-monitoring.md（运行时代码监控）
  - [x] SubTask 3.6：编写 05-annotationlib.md（注解与元数据处理）
  - [x] SubTask 3.7：编写 06-cross-module-analysis.md（跨模块关联与统一设计哲学，含 Mermaid 图）
  - [x] SubTask 3.8：编写 07-usage-examples.md（可运行综合代码示例）
  - [x] SubTask 3.9：编写 08-faq-troubleshooting.md（常见问题与注意事项）、09-summary-resources.md（总结与资源）

- [x] Task 4：编写方法论报告 seven-concepts-report.md（R→I→E + G1-G3 质量门记录）
  - [x] SubTask 4.1：记录事实采集清单与来源（4 个官方文档 URL）
  - [x] SubTask 4.2：记录洞察四元组与术语表
  - [x] SubTask 4.3：记录萃取产出与质量门通过情况

- [x] Task 5：更新知识库导航索引 `docs/knowledge/index.md`，纳入新教程入口

# Task Dependencies

- Task 2 依赖 Task 1
- Task 3 依赖 Task 2（章节内容需基于已提炼的概念）
- Task 4 依赖 Task 1、Task 2、Task 3（方法论报告覆盖全链路）
- Task 5 依赖 Task 3（教程章节落定后更新索引）