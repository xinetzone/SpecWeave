---
id: python314-cpython-wiki-13-official-docs-roadmap
title: 官方文档四大支柱导览（tutorial / library / extending / howto）
type: Reference
description: "Python 3.14 官方文档路线图，涵盖 PEP 索引、What's New、标准库文档与开发计划"
sources:
  - https://docs.python.org/zh-cn/3.14/tutorial/index.html, https://docs.python.org/zh-cn/3.14/library/index.html, https://docs.python.org/zh-cn/3.14/extending/index.html, https://docs.python.org/zh-cn/3.14/howto/index.html
date: 2026-08-19
category: learning
tags: ["python314", "official-docs", "tutorial", "standard-library", "extending", "embedding", "howto", "roadmap", "foundation"]
generated:
  by: "process:docs-to-okf-conversion"
  at: "2026-08-22T00:00:00Z"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00Z"
status: "stable"
stale_after: "2027-08-22"
---
# 官方文档四大支柱导览

> **定位**：本教程的 00-12 章聚焦「Python 3.14 新特性 + CPython 源码」，默认读者已具备 Python 基础。本章补齐另一块拼图——**官方文档四大基础支柱**的完整导览，让你能系统性地从官方原始文档学习语言基础、标准库全景、C 扩展嵌入与实践指南，并与 3.14 的深度章节建立映射。
>
> **四大支柱**：`tutorial`（语言教程）、`library`（标准库参考）、`extending`（扩展与嵌入）、`howto`（实践指南）。它们与 `reference`（语言参考）、`c-api`（C API 参考）、`whatsnew`（版本日志）、`faqs` 共同构成 Python 官方文档的完整体系。

---

## 1. 四大支柱定位速览

| 支柱 | 官方入口 | 一句话定位 | 面向读者 | 本 wiki 对应深度章节 |
|------|---------|-----------|---------|---------------------|
| **Tutorial**（教程） | [tutorial/index.html](https://docs.python.org/zh-cn/3.14/tutorial/index.html) | 语言基础的非正式入门 | 已会编程、刚学 Python | [01 语言新特性](/concepts/01-language-features.md)、[04 新模块](/concepts/04-new-modules.md) |
| **Library**（标准库） | [library/index.html](https://docs.python.org/zh-cn/3.14/library/index.html) | 标准库模块参考手册 | 所有开发者 | [04 新模块](/concepts/04-new-modules.md)、[05 标准库改进](/concepts/05-stdlib-improvements.md) |
| **Extending**（扩展/嵌入） | [extending/index.html](https://docs.python.org/zh-cn/3.14/extending/index.html) | 用 C/C++ 扩展与嵌入 Python | C 扩展作者、嵌入者 | [07 C API](/references/07-c-api-changes.md)、[06 架构](/concepts/06-cpython-architecture.md) |
| **HowTo**（指南） | [howto/index.html](https://docs.python.org/zh-cn/3.14/howto/index.html) | 单主题深度的实践手册 | 需要解决具体问题的开发者 | [10 实战示例](/examples/10-practical-examples.md)、[11 FAQ](/references/11-faq-troubleshooting.md) |

> **为什么读官方文档而不是只看第三方教程**：官方文档是权威、精确、随版本更新的第一手资料，尤其是 3.14 引入的 t-strings、延迟注解、自由线程、多解释器等特性，第三方资料的滞后性会带来错误信息。本 wiki 的价值是「替你定位到官方文档的正确位置 + 补充源码级原理」。

---

## 2. 支柱一：Python 教程（Tutorial）—— 语言基础

### 2.1 适用对象与前置假设

官方教程设计为面向**已「新入门 Python 语言」的程序员**（而非零编程基础的新手）。它假设你了解编程的基本概念，目标是快速感受 Python 特色、能读写 Python 模块和程序。

### 2.2 章节全览与 3.14 映射

| 章 | 主题 | 核心内容 | 3.14 相关点（映射到本 wiki） |
|---|------|---------|------------------------------|
| 1 | 课前甜点 | 激发兴趣 | — |
| 2 | 使用解释器 | 唤出/参数/交互模式/源码编码 | 新 REPL（[05 §1](/concepts/05-stdlib-improvements.md#1-repl-增强语法高亮与自动补全)） |
| 3 | Python 速览 | 计算器/文本/列表/编程第一步 | — |
| 4 | 控制流 | if/for/range/match/函数 | 无括号 except（[01 §1](/concepts/01-language-features.md)）、finally 警告（PEP 765） |
| 5 | 数据结构 | 列表/元组/集合/字典 | — |
| 6 | 模块 | 模块/包/导入 | — |
| 7 | 输入与输出 | 格式化/读写文件/json | t-strings 补充（[01 §4](/concepts/01-language-features.md)） |
| 8 | 错误和异常 | 语法错误/异常处理/异常链/异常组 | 无括号 except（PEP 758，见 01 §1） |
| 9 | 类 | 作用域/命名空间/继承/迭代器/生成器 | 延迟注解（[01 §3](/concepts/01-language-features.md)） |
| 10 | 标准库概览 | os/glob/sys/re/math 等 | — |
| 11 | 标准库概览二 | reprlib/struct/threading/logging | 自由线程（[02](/concepts/02-free-threading.md)）多线程 |
| 12 | 虚拟环境和包 | venv/pip | — |
| 13 | 接下来？ | 学习方向 | 指向本章四大支柱 |
| 14 | 交互式编辑 | Tab 补全/历史 | 新 REPL 补全（[05 §1](/concepts/05-stdlib-improvements.md#1-repl-增强语法高亮与自动补全)） |
| 15 | 浮点算术 | 表示性误差 | — |
| 16 | 附录 | 交互模式/脚本/启动文件 | — |

### 2.3 阅读建议

- **已会 3.10+ 的读者**：快速扫读第 4-9 章（控制流/数据/类/异常），重点留意 3.14 中语法变化（无括号 except、finally 控制流警告）影响到的写法；第 10-12 章（标准库/虚拟环境）按需查阅。
- **重点精读**：第 9 章「类」中关于函数注解的部分，理解 3.14 延迟注解对类定义的影响。

---

## 3. 支柱二：Python 标准库（Library）—— 模块全景

### 3.1 定位

标准库由两部分构成：**C 编写的内置模块**（承担文件 I/O 等系统级功能）+ **Python 编写的模块**（日常编程的标准解决方案）。Windows 安装包通常包含完整标准库，类 Unix 系统则拆为多个软件包。

### 3.2 模块分类全景（39 个官方分组，下表按主题合并呈现）

> 官方库参考共 39 个顶层分组。为便于速览，下表按主题合并为 32 行，仅列「代表模块」。加粗为该组内 **3.14 新增**模块，加 `*` 为该组在 3.14 有重要改进（详见 [05 章](/concepts/05-stdlib-improvements.md)）。

| 分组 | 代表模块 |
|------|---------|
| 内置函数/常量/类型/异常 | `builtins`、`constants`、`stdtypes`、`exceptions` |
| **线程安全性保证**（3.14 新增章节） | `threadsafety` —— 各内置容器在自由线程下的线程安全级别 |
| 文本处理服务 | `string`、**`string.templatelib`**、`re`、`difflib`、`textwrap`、`unicodedata` |
| 二进制数据服务 | `struct`*、`codecs` |
| 数据类型 | `datetime`、`collections`、`heapq`*、`bisect`、`array`、`weakref`、`enum`、`graphlib` |
| 数字和数学 | `math`、`cmath`、`decimal`、`fractions`、`random`、`statistics` |
| 函数式编程 | `itertools`、`functools`、`operator`* |
| 文件和目录访问 | `pathlib`*、`os.path`、`tempfile`、`glob`、`shutil` |
| 数据持久化 | `pickle`*、`shelve`、`sqlite3`、`dbm` |
| 数据压缩和存档 | **`compression`**、**`compression.zstd`**、`zlib`、`gzip`、`bz2`、`lzma`、`zipfile`、`tarfile` |
| 文件格式 | `csv`、`configparser`、`tomllib`、`plistlib` |
| 加密服务 | `hashlib`、`hmac`、`secrets` |
| 通用操作系统服务 | `os`、`io`、`time`、`logging`、`ctypes` |
| 命令行界面库 | `argparse`*、`optparse`、`getpass`、`curses`、`cmd` |
| 并发执行 | `threading`、`multiprocessing`、`concurrent.futures`*、**`concurrent.interpreters`**、`subprocess`、`queue` |
| 网络和进程间通信 | `asyncio`*、`socket`、`ssl`、`select`、`signal`、`mmap` |
| 互联网数据处理 | `email`、`json`*、`base64`、`binascii` |
| 结构化标记处理 | `html`、`xml.etree.ElementTree`、`xml.dom`、`xml.sax` |
| 互联网协议和支持 | `urllib`、`http`、`smtplib`、`imaplib`*、`uuid`*、`ipaddress` |
| 多媒体服务 | `wave`、`colorsys` |
| 国际化 | `gettext`、`locale` |
| Tk GUI | `tkinter`、`turtle`、`IDLE` |
| 开发工具 | `typing`、`doctest`、`unittest`*、`unittest.mock`、`pydoc` |
| 调试与分析 | `pdb`*、`bdb`、`faulthandler`*、`profile`、`timeit`、`tracemalloc` |
| 软件打包和分发 | `ensurepip`、`venv`、`zipapp` |
| Python 运行时服务 | `sys`、`sysconfig`、`warnings`、`dataclasses`、`contextlib`、`inspect`*、**`annotationlib`**、`gc` |
| 自定义解释器 | `code`、`codeop` |
| 导入模块 | `importlib`、`importlib.resources`、`importlib.metadata`、`runpy` |
| Python 语言服务 | `ast`、`token`、`tokenize`、`dis`、`symtable` |
| Windows 相关 | `msvcrt`、`winreg`、`winsound` |
| Unix 专属 | `posix`、`pwd`、`grp`、`termios`、`fcntl`、`resource` |
| Superseded/移除/安全 | `getopt`（被替代）、`removed`（已移除模块）、`security_warnings` |

### 3.3 与 3.14 深度章节的衔接

- **新增模块** `annotationlib`、`concurrent.interpreters`、`string.templatelib`、`compression.zstd` 的详细用法见 [04 新模块详解](/concepts/04-new-modules.md)。
- **改进模块**（asyncio/pathlib/uuid/pdb/argparse/heapq/operator/json/unittest 等）见 [05 标准库改进](/concepts/05-stdlib-improvements.md)。
- **线程安全性保证** 章节是 3.14 自由线程的配套文档，与 [02 自由线程](/concepts/02-free-threading.md) 的「线程安全模型」直接对应——官方文档从「API 契约」角度，本 wiki 从「实现原理（QSBR/BRC/关键区段）」角度互为补充。

---

## 4. 支柱三：扩展和嵌入（Extending）—— C/C++ 扩展与嵌入

官方 `extending` 文档包含两大独立主题，均假设你具备 Python 基础知识：

### 4.1 主题 A：不使用第三方工具创建扩展

面向「只想写 C/C++ 扩展」的读者（以及扩展构建工具的开发者）。结构如下：

| 节 | 主题 | 要点 |
|---|------|------|
| 1 | 使用 C/C++ 扩展 Python | 简单示例 → 错误异常 → 方法表与初始化函数 → 编译链接 → C 调 Python 函数 → 参数提取 → 引用计数 → C++ 扩展 → 暴露 C API |
| 2 | 自定义扩展类型：教程 | 基础 → 数据与方法 → 属性精细控制 → 循环 GC → 子类化 |
| 3 | 定义扩展类型：分类主题 | 终结/展示/属性/比较/抽象协议/弱引用 |
| 4 | 构建 C/C++ 扩展 | 使用 setuptools 构建 |
| 5 | Windows 上构建 | 菜谱式说明 / Unix-Windows 差异 / DLL 使用 |

### 4.2 主题 B：在更大应用中嵌入 CPython 运行时

面向「把 Python 当作嵌入脚本语言」的读者：

| 节 | 主题 |
|---|------|
| 1 | 在其它应用程序嵌入 Python（高层嵌入 → 突破限制 → 只做嵌入 → 扩展嵌入功能 → C++ 嵌入 → 编译链接） |

### 4.3 与 3.14 C API 变更的衔接

官方 `extending` 讲「**如何**写扩展/嵌入」，而本 wiki [07 C API 变更](/references/07-c-api-changes.md) 讲「3.14 **改了什么**」。二者配合阅读：

- 写新扩展时，先用 `extending` 的基础流程（方法表、`PyMethodDef`、`PyInit_*`），再叠加 07 章的 3.14 新约束：
  - 自由线程适配：模块必须声明 `Py_MOD_GIL` / `Py_MOD_FREE_THREADED`（[07 §6](/references/07-c-api-changes.md#6-自由线程-c-api-适配)）
  - 引用计数：使用 `Py_NewRef`/`Py_XNewRef` 简化（[07 §4](/references/07-c-api-changes.md#4-新增-c-api-汇总)）
  - Limited API 下不再直接访问 `ob_refcnt`/`ob_type`（[07 §5](/references/07-c-api-changes.md#5-limited-api-变更)）
- 嵌入 Python 时，用 `extending` 主题 B 的流程，叠加 PEP 741 统一配置 API（[07 §1](/references/07-c-api-changes.md#1-pep-741统一配置-c-api)）。
- 构建环节参考 [08 构建系统与平台支持](/concepts/08-build-platform.md)。

---

## 5. 支柱四：Python 指南（HowTo）—— 实践手册

HowTo 每篇文章「完全覆盖一个单独、特定的主题」，比标准库参考更深入、更面向任务。共 21 篇：

| HowTo 指南 | 主题 | 关联本 wiki 章节 |
|-----------|------|-----------------|
| 将扩展模块移植到 Python 3 | C 扩展跨版本移植 | [09 迁移指南](/concepts/09-migration-guide.md)、[07 C API](/references/07-c-api-changes.md) |
| 描述器指南 | 描述符协议 | [06 架构](/concepts/06-cpython-architecture.md)（对象模型） |
| Enum 指南 | 枚举深入 | library `enum` |
| 函数式编程指引 | map/filter/lambda/生成器 | [01 语言特性](/concepts/01-language-features.md) |
| 日志指南 / 日志专题手册 | logging 进阶 | library `logging` |
| 正则表达式指南 | re 深入 | library `re` |
| 套接字编程指南 | socket 实战 | library `socket` |
| 排序的技术 | sorted/key/λ 排序 | [05 标准库](/concepts/05-stdlib-improvements.md) |
| Unicode 指南 | 编码/规范化 | library `unicodedata` |
| urllib 获取网络资源 | HTTP 客户端实战 | library `urllib` |
| argparse 教程 | CLI 解析 | [05 §6](/concepts/05-stdlib-improvements.md#6-argparse-增强) |
| ipaddress 模块介绍 | IP 地址处理 | library `ipaddress` |
| **注解最佳实践** | 类型注解建议 | [01 §3](/concepts/01-language-features.md)（PEP 649/749）⭐ 3.14 相关 |
| **隔离扩展模块** | 自由线程下扩展模块隔离 | [02 自由线程](/concepts/02-free-threading.md)、[07 C API](/references/07-c-api-changes.md) ⭐ 3.14 相关 |
| 用 Curses 编程 | 终端 TUI | library `curses` |
| GDB 调试 C API 扩展 | gdb 扩展调试 | [11 FAQ](/references/11-faq-troubleshooting.md) |
| DTrace/SystemTap 检测 | 系统级追踪 | [06 架构](/concepts/06-cpython-architecture.md) |
| Linux perf 性能分析 | 内核 perf 追踪 | [03 JIT](/concepts/03-jit-interpreter.md) |
| timer 文件描述符指南 | timerfd | library `select` |
| Python 2.3 方法解析顺序 | MRO/C3 线性化 | [06 架构](/concepts/06-cpython-architecture.md)（类型系统） |

> ⭐ 标注的两篇（**注解最佳实践**、**隔离扩展模块**）是 3.14 最值得优先阅读的 HowTo：一篇对应延迟注解（PEP 649/749），一篇对应自由线程下的扩展隔离。

---

## 6. 四大支柱 × 3.14 深度指南 映射总表

| 你想学什么 | 先看官方支柱 | 再看本 wiki 深度章节 |
|-----------|-------------|---------------------|
| 语言基础语法 | tutorial §2-9 | 01（3.14 语法变化） |
| 标准库有什么 | library 分类索引 | 04（新模块）+ 05（改进） |
| 如何写 C 扩展/嵌入 | extending 全篇 | 07（C API 变更） |
| 某主题怎么实操 | howto 对应篇 | 10（实战示例） |
| CPython 内部怎么实现 | — | 02/03/06（源码原理） |
| 迁移/排障 | howto「移植扩展」 | 09 + 11 |

---

## 7. 分角色官方文档阅读路径

| 角色 | 官方文档阅读顺序 | 本 wiki 衔接 |
|------|-----------------|-------------|
| **应用开发者** | tutorial（§2-9）→ library（按需查模块）→ howto（正则/日志/排序/argparse） | 01 + 04 + 05 + 09 |
| **库作者** | tutorial（§9 类/注解）→ library（typing/abc）→ howto（注解最佳实践） | 01 + 07 + 09 |
| **C 扩展开发者** | extending（全篇）→ howto（移植/隔离扩展/GDB）→ c-api 参考 | 02 + 06 + 07 + 08 |
| **源码学习者** | tutorial（语言全貌）→ reference + c-api | 02 + 03 + 06 |
| **技术决策者** | library（线程安全保证）→ howto（隔离扩展）→ whatsnew | 00 + 02 + 09 |

---

## 8. 学习建议

1. **四大支柱互补，不要孤立阅读**：`tutorial` 给语言直觉，`library` 给 API 权威定义，`extending` 给扩展能力，`howto` 给任务驱动的深度实践。
2. **官方文档是「查」的，本 wiki 是「学」的**：官方文档适合按需查阅特定 API/主题；本 wiki 适合系统性学习 3.14 的「为什么 + 怎么实现」。
3. **优先读 3.14 相关的 HowTo**：`注解最佳实践` 与 `隔离扩展模块` 是理解 3.14 两大架构变革（延迟注解、自由线程）的最佳官方入门。
4. **遇到版本差异先查官方**：本 wiki 基于 3.14.0，若你使用 3.14.5+（增量 GC 已回退）或后续版本，请以 `whatsnew` 最新补丁说明为准。

---

- [上一章：总结与资源](/references/12-summary-resources.md) ←
- [返回教程首页](/index.md)