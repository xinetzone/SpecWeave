# Python 3.14 新特性学习路径规划

> **定位**：本文档为不同角色、不同基础的开发者提供从"知道 Python 3.14 有什么"到"能在生产中应用 Python 3.14 新特性"的系统化学习路径。
>
> **前置假设**：读者具备 Python 3.10+ 基础。每条路径标注预估学习时间，可根据个人基础调整。
>
> **配套资源**：本文档是 [Python 3.14 + CPython 源码深度指南](https://github.com/xinetzone/SpecWeave/tree/main/docs/knowledge/learning/python314-cpython-wiki) 的学习路径篇，配套有速查卡片和完整 Wiki 教程。官方文档地址：<https://docs.python.org/zh-cn/3.14/>

---

## 目录

- [1. 学习路径总览](#1-学习路径总览)
- [2. 阶段一：认知入门（2-3 天）](#2-阶段一认知入门2-3-天)
- [3. 阶段二：实践上手（1-2 周）](#3-阶段二实践上手1-2-周)
- [4. 阶段三：深入理解（2-4 周，按需深入）](#4-阶段三深入理解2-4-周按需深入)
- [5. 阶段四：生产应用（持续）](#5-阶段四生产应用持续)
- [6. 分角色学习路径速查](#6-分角色学习路径速查)
- [7. 学习资源清单](#7-学习资源清单)
- [8. 自测清单](#8-自测清单)

---

## 1. 学习路径总览

### 1.1 角色矩阵

| 角色 | 目标 | 核心学习内容 | 建议时间 | 难度 |
|------|------|-------------|---------|------|
| **应用开发者** | 掌握新语法、新模块，顺利迁移项目 | 语言新特性 + 新模块 + 标准库改进 + 迁移指南 | 1-2 周 | ⭐⭐ |
| **库作者** | 确保库兼容 3.14，利用新特性优化 | 语言新特性 + 类型注解变化 + C API 变更 + 自由线程兼容 | 2-3 周 | ⭐⭐⭐ |
| **C 扩展开发者** | 适配自由线程，使用新 C API | C API 变更 + 自由线程 + 关键区段 + 构建系统 | 3-4 周 | ⭐⭐⭐⭐ |
| **源码学习者** | 理解 CPython 内部架构 | 源码架构 + 自由线程实现 + JIT 实现 | 4-8 周 | ⭐⭐⭐⭐⭐ |
| **技术决策者** | 评估升级收益与风险 | 概述 + 性能特征 + 迁移成本 + 已知限制 | 2-3 天 | ⭐⭐ |

### 1.2 四阶段递进模型

无论你是哪种角色，学习都遵循四个阶段：

```
🔵 阶段一：认知入门（知道有什么）
    ↓
🟢 阶段二：实践上手（会用新特性）
    ↓
🟡 阶段三：深入理解（理解原理）
    ↓
🔴 阶段四：生产应用（能解决问题）
```

| 阶段 | 目标 | 产出物 | 适用角色 |
|------|------|--------|---------|
| **阶段一：认知入门** | 知道 3.14 有哪些新东西，能说出核心特性名称 | 阅读笔记 | 所有角色 |
| **阶段二：实践上手** | 每个新特性写过至少一个代码示例 | 练习代码仓库 | 应用开发者/库作者 |
| **阶段三：深入理解** | 理解自由线程/JIT/延迟注解的设计原理 | 原理笔记、架构图 | 库作者/C扩展/源码学习者 |
| **阶段四：生产应用** | 在真实项目中使用新特性，解决实际问题 | 上线项目、迁移 PR | 所有角色 |

### 1.3 Wiki 教程章节对照

学习路径中引用的 Wiki 教程章节：

| 编号 | 章节标题 | 核心内容 |
|------|---------|---------|
| 第00章 | 概述 | 版本背景、目标受众、核心特性全景 |
| 第01章 | 语言新特性 | t-strings、延迟注解、无括号 except、finally 警告、内置函数变更 |
| 第02章 | 自由线程（无 GIL）深度解析 | QSBR、BRC、关键区段、mimalloc、线程安全模型、C扩展兼容 |
| 第03章 | JIT 编译器与新执行模型 | Tier 1 特化、Tier 2 uop 优化器、Copy-and-Patch JIT、尾调用解释器 |
| 第04章 | 新模块详解 | annotationlib、concurrent.interpreters、string.templatelib、compression.zstd |
| 第05章 | 标准库重大改进 | REPL、asyncio、pathlib、pdb、uuid、argparse、json 等 |
| 第06章 | CPython 源码架构总览 | 目录结构、三层头文件、解释器循环、对象系统、GC、内存分配 |
| 第07章 | C API 与扩展开发 | PEP 741/757、Limited API 变更、自由线程适配、废弃/移除 API |
| 第08章 | 构建系统与平台支持 | 构建选项、官方二进制新特性、平台支持变化 |
| 第09章 | 迁移指南 | 废弃 API 对照表、行为变更注意事项、C 扩展迁移 checklist |
| 第10章 | 实战示例 | t-strings SQL 构建、FT 基准测试、多解释器并行、zstd 压缩、pdb 远程调试 |
| 第11章 | FAQ 与排障 | 安装/兼容性/性能 FAQ、已知问题、调试技巧 |
| 第12章 | 总结与资源 | 十大变革速记、分角色学习路径、源码速查表、延伸阅读 |

---

## 2. 阶段一：认知入门（2-3 天）

### 目标
快速建立对 Python 3.14 新特性的全局认知，知道"有什么"和"我需要关注什么"。

### 学习内容

#### Day 1：全景概览
- [ ] 阅读 Python 3.14 速查卡片（见配套资源，10 分钟通读）
- [ ] 阅读 Wiki 教程第00章「概述」（30 分钟）
  - 重点关注：十大变革速记、PEP 一览表、版本信息
- [ ] 浏览官方 [What's New in Python 3.14](https://docs.python.org/zh-cn/3.14/whatsnew/3.14.html)（1 小时，挑感兴趣的章节读）

**自测**：不看资料，能否说出 Python 3.14 的五个最重要变化？

#### Day 2：按角色筛选重点
根据你的角色，标记需要深入学习的章节：

| 角色 | 必读章节 | 可了解/跳过章节 |
|------|---------|----------------|
| 应用开发者 | 第01章、第04章、第05章、第09章 | 第02章（了解概念）、第03章（了解概念）、第06/07章（跳过） |
| 库作者 | 第01章、第02章（线程安全）、第04章、第05章、第07章、第09章 | 第03章（了解）、第06章（了解目录结构） |
| C 扩展开发者 | 第02章、第03章（执行模型）、第06章、第07章、第08章、第09章 | 第04章（了解概念） |
| 源码学习者 | 第02章、第03章、第06章、第07章 全部 | 第10章、第11章 选读 |

#### Day 3：环境搭建
- [ ] 安装 Python 3.14（官方安装包或 pyenv）
  ```bash
  # pyenv
  pyenv install 3.14.0
  pyenv shell 3.14.0

  # 验证
  python3.14 --version
  python3.14 -c "import sys; print(f'Free-threading: {hasattr(sys, \"_is_gil_enabled\")}')"
  ```
- [ ] 安装自由线程版本（可选，C 扩展/源码学习者必做）
- [ ] 测试 JIT 启用
  ```bash
  PYTHON_JIT=1 python3.14 -c "print('JIT enabled via PYTHON_JIT=1')"
  ```

### 阶段一产出物
- [ ] 一份个人"3.14 关注清单"：列出你最感兴趣/最需要掌握的 3-5 个特性
- [ ] Python 3.14 环境就绪，能运行基本代码

---

## 3. 阶段二：实践上手（1-2 周）

### 目标
对每个新特性，至少写过一个可运行的代码示例，理解基本用法和适用场景。

### 学习内容

#### Week 1：语言特性与新模块（每天 1-2 小时）

**Day 1：t-strings（PEP 750）**
- [ ] 阅读 Wiki 第01章「语言新特性」→ t-strings 模板字符串节
- [ ] 阅读 Wiki 第04章「新模块详解」→ string.templatelib 节
- [ ] 练习任务：
  1. 用 t-string 写一个简单的 SQL 参数化构建器
  2. 用 t-string 写一个 HTML 转义模板
  3. 对比 t-string 和 f-string 的输出差异
- [ ] 自测：`Template` 对象迭代时，静态文本和 `Interpolation` 对象如何区分？

**Day 2：延迟注解（PEP 649/749）**
- [ ] 阅读 Wiki 第01章「语言新特性」→ 延迟注解求值节
- [ ] 阅读 Wiki 第04章「新模块详解」→ annotationlib 节
- [ ] 练习任务：
  1. 定义一个带前向引用的类（如链表节点），验证不需要 `from __future__ import annotations`
  2. 使用 `annotationlib.get_annotations()` 分别获取 VALUE、STRING、FORWARDREF 三种格式
  3. 把一个使用 `from __future__ import annotations` 的旧文件改为 3.14 风格
- [ ] 自测：`__future__ annotations` 在 3.14 中的状态是什么？迁移需要做什么？

**Day 3：语法小改进（PEP 758/765）**
- [ ] 阅读 Wiki 第01章「语言新特性」→ 无括号 except 和 finally 警告节
- [ ] 练习任务：
  1. 用无括号 except 重写一段旧代码
  2. 检查你的项目中 finally 块是否有 return/break/continue
  3. 测试 `NotImplemented` 布尔上下文的 TypeError
- [ ] 自测：`except ValueError, TypeError as e:` 的写法对吗？

**Day 4：内置函数与标准库改进**
- [ ] 阅读 Wiki 第01章「语言新特性」→ 内置函数变更节
- [ ] 阅读 Wiki 第05章「标准库重大改进」
- [ ] 练习任务：
  1. 使用 `map(strict=True)` 对比旧行为
  2. 体验新 REPL 的语法高亮和补全
  3. 使用 `uuid.uuid7()` 生成时间排序 ID
  4. 尝试 `python -m asyncio ps <PID>`（需要一个跑着的 asyncio 程序）
  5. 试用 `compression.zstd` 压缩/解压文件

**Day 5：concurrent.interpreters（PEP 734）**
- [ ] 阅读 Wiki 第04章「新模块详解」→ concurrent.interpreters 节
- [ ] 练习任务：
  1. 创建子解释器执行简单代码
  2. 使用 Channel 在主解释器和子解释器间传数据
  3. 用 `InterpreterPoolExecutor` 并行计算素数，对比 ThreadPoolExecutor
- [ ] 自测：子解释器之间能直接共享 Python 对象吗？为什么？

**Day 6-7：自由线程初体验**
- [ ] 阅读 Wiki 第02章「自由线程深度解析」→ §1-3 为什么要去掉 GIL
- [ ] 练习任务：
  1. 在 `python3.14t` 下运行自由线程多线程性能基准测试（参见 Wiki 第10章「实战示例」示例3）
  2. 对比 GIL 模式和 FT 模式下 1/2/4 线程的加速比
  3. 验证哪些内置操作是线程安全的（list.append、d[key]=v 等）
  4. 构造一个竞态条件示例（`counter += 1`），验证它在 FT 模式下确实不安全

#### Week 2：迁移与实战（每天 1-2 小时）

**Day 8：迁移指南**
- [ ] 阅读 Wiki 第09章「迁移指南」
- [ ] 练习任务：
  1. 检查你的一个项目中是否使用了废弃 API
  2. 运行 `python3.14 -W error your_script.py` 把警告变错误，发现潜在问题
  3. 评估 multiprocessing 默认 forkserver 变更的影响

**Day 9-10：JIT 实验**
- [ ] 阅读 Wiki 第03章「JIT 编译器与新执行模型」→ §1-6 Python 执行模型演进
- [ ] 练习任务：
  1. 写一个数字计算密集函数，对比 `PYTHON_JIT=0` 和 `PYTHON_JIT=1` 的性能
  2. 构造一个类型不稳定的函数，观察 JIT 是否有效
  3. 用 `sys._stats` 查看优化统计

**Day 11-12：综合项目**
- [ ] 选择一个 3.14 实战示例深入：
  - 🔹 **Web 开发者**：用 t-strings 给你的 Web 框架加 SQL 参数化
  - 🔹 **数据工程师**：用 zstd 压缩数据管道，对比 gzip 性能
  - 🔹 **并发场景**：对比 threading/multiprocessing/interpreters 三种方案
  - 🔹 **CLI 工具**：用 argparse 新特性和 pathlib 改进你的工具
- [ ] 参考 Wiki 第10章「实战示例」获取灵感

**Day 13-14：FAQ 与排障**
- [ ] 阅读 Wiki 第11章「FAQ 与排障」
- [ ] 整理你在实践中遇到的问题和解决方案
- [ ] 回顾速查卡片，确认每个特性都用过至少一次

### 阶段二产出物
- [ ] 一个 `python314-playground` 仓库，包含所有新特性的练习代码
- [ ] 每个新特性至少有 1 个可运行示例
- [ ] 能回答"什么时候用 t-strings vs f-strings"、"自由线程什么时候有用"等实践问题

---

## 4. 阶段三：深入理解（2-4 周，按需深入）

### 目标
理解核心架构变更（自由线程、JIT）的设计原理和实现机制，能够做出合理的技术选型决策。

> ⚠️ **提示**：此阶段主要面向库作者、C 扩展开发者和源码学习者。应用开发者可以选读感兴趣的部分。

### 学习内容

#### Track A：自由线程深入（C 扩展/库作者必做，1-2 周）

- [ ] 精读 Wiki 第02章「自由线程深度解析」→ §4-8（QSBR、BRC、关键区段、mimalloc、线程安全模型）
  - QSBR 原理和静默点机制
  - BRC 批量引用计数和永生对象
  - 关键区段和 Parking Lot
  - mimalloc 内存分配
  - 线程安全模型
- [ ] 阅读 CPython InternalDocs：
  - [InternalDocs/qsbr.md](https://github.com/python/cpython/blob/v3.14.0/InternalDocs/qsbr.md)
- [ ] 源码阅读（GitHub 链接，基于 v3.14.0 tag）：
  - [Python/qsbr.c](https://github.com/python/cpython/blob/v3.14.0/Python/qsbr.c) — QSBR 实现
  - [Python/critical_section.c](https://github.com/python/cpython/blob/v3.14.0/Python/critical_section.c) — 关键区段
- [ ] 练习任务：
  1. 写一个 C 扩展，先标记 `Py_MOD_GIL`，然后逐步适配为 `Py_MOD_FREE_THREADED`
  2. 使用关键区段保护对象的可变字段
  3. 用 ThreadSanitizer 检测数据竞争

#### Track B：JIT 与执行模型深入（性能优化/源码学习者，1-2 周）

- [ ] 精读 Wiki 第03章「JIT 编译器与新执行模型」→ §3-7（尾调用解释器、Tier 1/2/3、去优化）
  - 尾调用解释器原理
  - Tier 1 自适应特化
  - Tier 2 uop 优化器
  - Copy-and-Patch JIT 工作流程
  - 去优化机制
- [ ] 阅读 CPython InternalDocs：
  - [InternalDocs/jit.md](https://github.com/python/cpython/blob/v3.14.0/InternalDocs/jit.md)
  - [InternalDocs/tier2.md](https://github.com/python/cpython/blob/v3.14.0/InternalDocs/tier2.md)
- [ ] 源码阅读：
  - [Python/ceval.c](https://github.com/python/cpython/blob/v3.14.0/Python/ceval.c) — 解释器循环
  - [Python/jit.c](https://github.com/python/cpython/blob/v3.14.0/Python/jit.c) — JIT 运行时
  - [Python/optimizer.c](https://github.com/python/cpython/blob/v3.14.0/Python/optimizer.c) — Tier 2 优化器
- [ ] 练习任务：
  1. 写几个微基准测试，理解 JIT 什么时候有效、什么时候无效
  2. 阅读 Copy-and-Patch 论文，理解 stencil+patch 的原理
  3. 分析一个真实 Python 函数的字节码、uop、JIT 编译过程

#### Track C：CPython 架构深入（源码学习者，2-3 周）

- [ ] 精读 Wiki 第06章「CPython 源码架构总览」
- [ ] 源码阅读路线（按顺序，基于 v3.14.0 tag）：
  1. [Programs/python.c](https://github.com/python/cpython/blob/v3.14.0/Programs/python.c) → 启动流程
  2. [Include/object.h](https://github.com/python/cpython/blob/v3.14.0/Include/object.h) → 对象模型
  3. [Objects/longobject.c](https://github.com/python/cpython/blob/v3.14.0/Objects/longobject.c) → 最简单的内置类型
  4. [Objects/listobject.c](https://github.com/python/cpython/blob/v3.14.0/Objects/listobject.c) → 列表实现
  5. [Objects/dictobject.c](https://github.com/python/cpython/blob/v3.14.0/Objects/dictobject.c) → 字典（最复杂）
  6. [Python/ceval.c](https://github.com/python/cpython/blob/v3.14.0/Python/ceval.c) → 解释器循环
  7. [Python/compile.c](https://github.com/python/cpython/blob/v3.14.0/Python/compile.c) → 编译器
  8. [Parser/pegen.c](https://github.com/python/cpython/blob/v3.14.0/Parser/pegen.c) → PEG 解析器
- [ ] 练习任务：
  1. 画一张 CPython 架构图（不看资料自己画）
  2. 追踪一个简单 Python 语句的完整执行路径（解析→编译→执行）
  3. 为 CPython 添加一个简单的内置函数（编译自己修改过的 CPython）

#### Track D：C API 深入（C 扩展开发者，1 周）

- [ ] 精读 Wiki 第07章「C API 与扩展开发」和第08章「构建系统与平台支持」
- [ ] 练习任务：
  1. 用 PEP 741 `PyInitConfig` 重写一个嵌入 Python 的程序
  2. 使用 PEP 757 `PyLong_Export` 高效读取整数数组
  3. 适配一个现有 C 扩展到 Python 3.14 Limited API

### 阶段三产出物
- [ ] 核心原理笔记（自由线程/JIT/架构至少选一个方向）
- [ ] 一张自己画的 CPython 架构图
- [ ] 一个适配了自由线程的 C 扩展（C 扩展开发者）
- [ ] 能解释"为什么 JIT 对某些代码无效"、"为什么自由线程需要 QSBR"等原理问题

---

## 5. 阶段四：生产应用（持续）

### 目标
在真实项目中使用 Python 3.14 新特性，解决实际问题，沉淀最佳实践。

### 推荐实践

#### 迁移项目到 3.14

1. **准备阶段**
   - [ ] 在 CI 中加入 Python 3.14 测试（保留旧版本并行）
   - [ ] 运行测试套件，记录失败项
   - [ ] 使用 `python3.14 -W error` 发现弃用警告
   - [ ] 检查依赖库的 3.14 兼容性（特别是 C 扩展）

2. **代码更新**
   - [ ] 删除 `from __future__ import annotations`
   - [ ] 修复 `finally` 中的 return/break/continue
   - [ ] 替换废弃 API（对照迁移表，见下方）
   - [ ] 评估 multiprocessing 启动方法变更

3. **性能优化**（可选）
   - [ ] CPU 密集场景评估自由线程（需要依赖库支持）
   - [ ] 热循环测试 JIT 效果
   - [ ] 用 zstd 替代 gzip（压缩场景）
   - [ ] 用 uuid7 替代 uuid4（数据库主键场景）

4. **C 扩展适配**（如有）
   - [ ] 先加 `Py_MOD_GIL` 确保兼容
   - [ ] 审查全局变量和共享状态
   - [ ] 添加关键区段保护
   - [ ] 在 `python3.14t` 下测试
   - [ ] 升级到 `Py_MOD_FREE_THREADED`

#### 关键废弃/迁移对照表

| 3.13 及以前 | 3.14 状态 | 替代方案 |
|------------|----------|---------|
| `from __future__ import annotations` | 弃用警告，未来版本移除 | 删除，直接使用原生延迟注解 |
| `asynchat`/`asyncore` | 移除 | 使用 `asyncio` |
| `aifc`、`audioop`、`cgi`、`cgitb`、`chunk`、`imghdr`、`mailcap`、`msilib`、`nntplib`、`ossaudiodev`、`pipes`、`sndhdr`、`spwd`、`sunau`、`telnetlib`、`uu`、`xdrlib` | 移除 | 查找第三方替代库 |
| `typing.TypedDict` 不支持泛型 | 旧行为 | 使用 `typing.TypedDict[KT, VT]` 泛型语法 |
| `multiprocessing` 默认 `fork`（Linux） | 改为 `forkserver` | 显式 `set_start_method('fork')` 如需旧行为 |
| C API 直接访问 `ob_refcnt`/`ob_type` | Limited API 不再暴露 | 使用 `Py_REFCNT()`/`Py_TYPE()` 访问器函数 |
| `PyThreadState` 直接访问内部字段 | 不透明化 | 使用 `PyThreadState_Get*()` API |

#### 新项目技术选型建议

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| SQL 查询构建 | t-strings + 参数化 | 防注入，类型安全 |
| HTML/模板渲染 | t-strings + 自定义转义 | XSS 防护 |
| 数据压缩 | compression.zstd | 比 gzip 快 3-5x，压缩率更高 |
| CPU 并行（纯 Python） | 自由线程 + threading | 真并行，低开销 |
| CPU 并行（混合 C 扩展） | concurrent.interpreters | 隔离性好，避开 GIL 问题 |
| 数据库主键 | uuid.uuid7() | 按时间排序，索引友好 |
| 大整数数组处理 | PEP 757 PyLong_Export | 零拷贝 |
| 日志/消息 ID | uuid.uuid7() 或 time.time_ns() | 有序、唯一 |

#### 生产环境注意事项

- [ ] **JIT 仍为实验性**：生产环境使用需充分测试，建议先在非关键路径启用
- [ ] **自由线程生态成熟度**：NumPy/PyTorch 等科学计算库的 FT 支持仍在推进中，2026 年需关注各库状态
- [ ] **增量 GC 回退**：使用 3.14.5+ 版本，避免 3.14.0-3.14.4 的内存问题
- [ ] **C 扩展兼容性**：升级前在测试环境用 `python3.14t` 验证所有 C 扩展
- [ ] **多进程启动方法**：显式设置 `multiprocessing.set_start_method()` 以获得确定性行为

### 阶段四产出物
- [ ] 至少一个项目升级到 Python 3.14
- [ ] 团队内部的 3.14 迁移指南（基于本文档定制）
- [ ] 性能基准报告（迁移前后对比）
- [ ] 遇到的坑和解决方案记录

---

## 6. 分角色学习路径速查

### 🚀 应用开发者路径

```
阶段一（2天）→ 阶段二（1周）→ 阶段四（持续）
  速查卡+概述    语言特性+新模块    迁移项目
  +语言+新模块   +迁移指南+实战     +生产应用
  +标准库
```

**必学核心**：t-strings、延迟注解、zstd、uuid7、REPL、迁移检查清单
**可了解**：自由线程概念、JIT 概念（知道怎么开启即可）

### 📦 库作者路径

```
阶段一（2天）→ 阶段二（1.5周）→ 阶段三Track A（1周）→ 阶段四
  速查卡+概述    全部语言特性        自由线程线程安全     确保库兼容
  +语言+新模块   +标准库+迁移        模型+C API变更      +发布兼容版本
  +C API
```

**必学核心**：t-strings、延迟注解（`__future__` 移除影响）、C API 变更、自由线程兼容性标记
**深入方向**：关键区段 API、多解释器隔离

### 🔌 C 扩展开发者路径

```
阶段一（3天）→ 阶段二（1周）→ 阶段三 Track A+D（2-3周）→ 阶段四
  速查卡+概述    语言特性+C API    自由线程实现原理     适配自由线程
  +FT+架构       +自由线程概念     +C API 深入          +优化性能
  +C API                            +构建系统
```

**必学核心**：QSBR/BRC/关键区段原理、`Py_MOD_GIL`/`Py_MOD_FREE_THREADED`、Limited API 不透明化、PEP 741/757
**源码必看**：Python/qsbr.c、Python/critical_section.c、Include/pycore_*.h（通过 GitHub 链接）

### 🔬 源码学习者路径

```
阶段一（3天）→ 阶段二（2周）→ 阶段三 Track A+B+C（4-8周）
  速查卡+概述    全部特性写一遍      自由线程+JIT+架构
  +源码架构      +读 InternalDocs    全链路源码阅读
                                  +编译自己的 CPython
```

**阅读顺序**：启动流程 → 对象模型 → 内置类型 → 解释器循环 → 编译器 → 自由线程/JIT
**终极练习**：给 CPython 添加一个新的字节码或内置函数

### 📊 技术决策者路径

```
阶段一（2-3天）
  速查卡+概述+FT性能+迁移指南+FAQ
  → 输出：升级评估报告（收益/成本/风险/时间线）
```

**重点评估**：
- 自由线程对 CPU 密集场景的加速价值 vs 生态成熟度风险
- JIT 实验性是否适合当前项目
- 迁移成本（废弃 API 数量、C 扩展依赖、测试覆盖）
- 时间线建议（等 3.14.x 补丁版本？等主要依赖库支持？）

---

## 7. 学习资源清单

### 官方资源

| 资源 | 链接 | 适合阶段 |
|------|------|---------|
| Python 3.14 官方文档（中文） | https://docs.python.org/zh-cn/3.14/ | 一~四 |
| What's New in Python 3.14 | https://docs.python.org/zh-cn/3.14/whatsnew/3.14.html | 一 |
| CPython GitHub 仓库（v3.14.0 tag） | https://github.com/python/cpython/tree/v3.14.0 | 三 |
| PEP 索引 | https://peps.python.org/ | 二 |
| CPython Dev Guide | https://devguide.python.org/ | 三 |
| CPython InternalDocs（FT/JIT 设计文档） | https://github.com/python/cpython/tree/v3.14.0/InternalDocs | 三 |
| Python 3.14 速查卡片 | 见配套 Wiki 仓库 | 一 |

### 核心 PEP 清单

| PEP | 标题 | 阶段 |
|-----|------|------|
| [PEP 703](https://peps.python.org/pep-0703/) | Making the Global Interpreter Lock Optional | 二/三 |
| [PEP 750](https://peps.python.org/pep-0750/) | Template Strings (t-strings) | 二 |
| [PEP 649](https://peps.python.org/pep-0649/) | Deferred Evaluation of Annotations | 二 |
| [PEP 749](https://peps.python.org/pep-0749/) | The annotationlib Module and AnnotationFormat | 二 |
| [PEP 758](https://peps.python.org/pep-0758/) | Bracket-less except | 二 |
| [PEP 779](https://peps.python.org/pep-0779/) | Free Threaded Python is no longer provisional | 三 |
| [PEP 734](https://peps.python.org/pep-0734/) | Multiple Interpreters in the Stdlib | 二 |
| [PEP 784](https://peps.python.org/pep-0784/) | Zstandard Compression for the Standard Library | 二 |
| [PEP 741](https://peps.python.org/pep-0741/) | Python Configuration C API | 三 |
| [PEP 757](https://peps.python.org/pep-0757/) | C API: Importing and Exporting Python Buffer Data | 三 |
| [PEP 765](https://peps.python.org/pep-0765/) | Disallow return/break/continue that exit a finally block | 二 |

### 推荐延伸阅读

| 主题 | 资源 |
|------|------|
| 自由线程设计 | Sam Gross "nogil" 演讲（PyCon US 2023）、PEP 703 设计文档 |
| Copy-and-Patch JIT | Haoran Xu 论文 "Copy-and-Patch Compilation" (2021)，https://arxiv.org/abs/2011.13127 |
| QSBR/RCU | Linux Kernel RCU documentation、URCU 项目（Userspace RCU） |
| CPython 内部 | https://cpythoninternals.com — 《CPython Internals》书籍 |
| Faster CPython 项目 | https://github.com/faster-cpython — 官方性能优化项目 |
| Tail-Call Interpreter | PEP 703 附录关于解释器优化的部分 |

---

## 8. 自测清单

### 阶段一自测（认知入门）
- [ ] 能说出 Python 3.14 的五个最重大变化
- [ ] 知道自由线程和 JIT 的启用方式
- [ ] 知道 t-strings 和 f-strings 的核心区别
- [ ] Python 3.14 环境已安装并能运行

### 阶段二自测（实践上手）
- [ ] 每个新特性至少写过 1 个代码示例
- [ ] 能用 t-strings 构建安全 SQL 查询
- [ ] 能使用 annotationlib 获取三种格式的注解
- [ ] 体验过自由线程的多线程加速效果
- [ ] 知道自己项目中需要迁移的废弃 API
- [ ] 用过 zstd 压缩并对比过 gzip

### 阶段三自测（深入理解）
- [ ] 能解释 QSBR 为什么能实现无锁内存回收
- [ ] 能解释 Copy-and-Patch JIT 的工作流程
- [ ] 能画出 CPython 的三层头文件体系
- [ ] 能说出 Python 代码从源码到执行的完整路径
- [ ] 能判断哪些操作在自由线程模式下是线程安全的

### 阶段四自测（生产应用）
- [ ] 至少一个项目已运行在 Python 3.14 上
- [ ] 在项目中实际使用了 3 个以上的新特性
- [ ] C 扩展（如有）已标记 GIL 兼容性
- [ ] 有性能基准数据证明升级收益
- [ ] 团队成员都了解 3.14 的关键变化

---

> 💡 **学习建议**：不必一次学完所有内容。从对你最有用的特性开始，边用边学。Python 3.14 的变化很多，但每个特性都是独立的，可以按需渐进采用。自由线程和 JIT 是架构级变革，需要更长的学习周期，但 **t-strings、延迟注解、zstd、uuid7** 等特性当天学完当天就能用。

---

*文档版本：1.0 | 更新日期：2026-08-19 | 基于 Python 3.14.0 官方发布版本*
