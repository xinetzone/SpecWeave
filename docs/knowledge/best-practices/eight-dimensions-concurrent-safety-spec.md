---
id: "eight-dimensions-concurrent-safety-spec"
title: "并发安全八维检查法技术规格"
date: 2026-07-08
source: "retrospective-concurrent-safety-checker-20260708/retrospective-report.md#1.4-八维检查法规则详解"
x-toml-ref: "../../../.meta/toml/docs/knowledge/best-practices/eight-dimensions-concurrent-safety-spec.toml"
category: "best-practices"
status: stable
tags: ["concurrent-safety", "AST", "static-analysis", "eight-dimensions", "check-rules", "pre-commit"]
related_retrospective: "retrospective-concurrent-safety-checker-20260708"
cross_refs:
  - "concurrent-code-safety-review"
  - "ast-static-analysis-disambiguation"
---
# 并发安全八维检查法技术规格

> 📋 [并发代码安全审查指南](concurrent-code-safety-review.md) | 本文档为 `check_concurrent_safety` 静态分析工具的检测规则技术规格，描述8个维度的检测反模式、信号与消歧策略。

## 概述

检查引擎基于Python AST（`ast.NodeVisitor`）遍历，8个维度按严重级别分为：
- **error级（4个）**：TIMEOUT / IDEMPOTENT / DEADLOCK / LEAK —— 阻断提交
- **warn级（3个）**：BOUNDARY / DEFENSIVE / CONFIG —— 告警但不阻断
- **info级（1个）**：I18N —— 提示性信息

共覆盖12类并发反模式检测。

---

## 八维规则详解

| # | 维度 | 代码 | 严重级别 | 检测反模式 | 检测信号与消歧策略 |
|---|------|------|---------|-----------|------------------|
| 1 | **TIMEOUT** 超时检查 | CC-TIMEOUT | error | 阻塞操作无超时 | 检测4类场景：① `lock.acquire()`无timeout且非blocking=False；② `Event.wait()`/`Condition.wait()`无timeout（通过变量名lock/event/cond/queue等启发式识别并发原语）；③ `Thread.join()`无timeout（通过变量名thread/worker/task/future等启发式识别，排除`str.join()`）；④ `asyncio.wait_for()`缺少timeout参数；⑤ `while True`无限循环无break/return/raise且无超时退出 |
| 2 | **IDEMPOTENT** 幂等检查 | CC-IDEMPOTENT | error | 并发列表append无去重 | 检测`list.append()`调用：① 目标容器名含rejected/pending/queue/waiting/blocked等并发关键词；② append前无`if x not in container`守卫（通过_if_guard_stack跟踪if条件）；③ 排除_stack后缀、issues自身、日志/测试函数 |
| 3 | **BOUNDARY** 边界检查 | CC-BOUNDARY | warn | 热路径O(n)线性查找 | 检测循环内（`_loop_depth≥1`）对列表的`in`操作符：① 变量名以_list结尾或含list/results/candidates/pending_list等列表提示词；② 排除_set/_dict/_map后缀的集合类型（集合查找是O(1)）；③ 仅在resolver类或循环上下文中触发 |
| 4 | **DEFENSIVE** 防御检查 | CC-DEFENSIVE | warn | 可变对象泄漏 | 检测4类场景：① 函数默认参数为`[]`/`{}`/`set()`等可变字面量；② `return self._cache/_list/_dict`等内部可变状态直接返回，建议copy()；③ 直接return外部传入的list/dict/set可变参数未做防御性拷贝；④ 接收float参数时未检测NaN（`x != x`）和Inf（`math.isinf()`）特殊浮点值 |
| 5 | **CONFIG** 配置检查 | CC-CONFIG | warn | 并发参数硬编码魔法数 | 检测resolver类中`sleep(N)`/`acquire(N)`等并发调用，当数值参数N≥1且未引用大写常量名（如`DEFAULT_TIMEOUT`）时告警，建议提取为可配置参数 |
| 6 | **I18N** 国际化检查 | CC-I18N | info | 业务逻辑中直接匹配中文字面量 | 检测3类场景：① `==`/`!=`比较中含≥2个中文字符的字符串常量；② 函数调用参数中含中文字符串且调用者为startswith/endswith/find/index/__contains__/__eq__；③ 排除日志/打印/异常/测试/gettext等豁免场景 |
| 7 | **DEADLOCK** 死锁顺序检查 | CC-DEADLOCK | error | 多锁获取顺序不一致 | 跨函数跟踪锁获取序列（`_lock_acquire_sequences`）：① 通过变量名含lock/mutex/semaphore/rwlock或LOCK_CLASSES构造器识别锁对象；② 记录每个函数内的锁获取顺序；③ 发现不同函数对相同两把锁采用相反获取顺序时告警（经典AB-BA死锁） |
| 8 | **LEAK** 资源泄漏检查 | CC-LEAK | error | 线程池/进程池未关闭 | 检测3类场景：① ThreadPoolExecutor/ProcessPool等POOL_CLASSES构造识别池对象（`_pool_vars`）；② 检查池变量是否调用shutdown/close/stop/terminate（`_pool_shutdown`）；③ 检查是否在`with`语句中作为上下文管理器使用（`_pool_context_managed`）；④ 局部池变量既未shutdown也非with管理时告警 |

---

## 消歧策略核心

由于Python AST无法获取运行时类型信息，所有维度均采用"变量名启发式+上下文分析"的消歧方法：

- 通过变量名后缀（`_list`/`_set`/`_dict`/`_map`/`_lock`）区分容器类型
- 通过变量名关键词（thread/worker/lock/event/queue/pool等）识别并发对象
- 通过作用域跟踪（`in_test_function`/`in_logging_call`）排除测试代码和日志
- 遵循"宁可漏报不可误报"铁律，启发式置信度不足时跳过

### 五类误判模式及应对

| 误判类型 | 示例 | 根因 | 消歧策略 |
|---------|------|------|---------|
| **同名不同义** | `str.join()` vs `Thread.join()` | AST只看方法名，不看接收者类型 | 结合变量名模式（thread/worker前缀）+ 构造函数类型追踪 |
| **类型推断缺失** | `items = []` 是list还是deque？ | 动态类型，AST无类型信息 | 变量名后缀约定（`_list`/`_set`/`_dict`）+ 赋值语句类型追踪 |
| **上下文遗漏** | for循环内的查找 vs 顶层查找 | AST节点遍历遗漏相关节点类型 | 完整覆盖AST节点（For/While/If/With/Try等） |
| **作用域穿透** | 函数参数是list还是外部传入的set？ | 无法追踪跨函数数据流 | 仅在函数/方法内部做局部分析，不做跨过程分析 |
| **测试代码污染** | 测试函数中的故意错误被报告 | 检查器不区分测试代码和生产代码 | 按函数名前缀（`test_`）和类名（`Test*`）跳过 |

---

## 已知局限

| 局限 | 影响维度 | 改进方向 |
|------|---------|---------|
| 跨文件锁顺序无法检测 | DEADLOCK | CI全量扫描时聚合多文件锁序列 |
| 依赖变量命名约定 | BOUNDARY/IDEMPOTENT/TIMEOUT | 引入数据流分析追踪实际类型 |
| I18N未覆盖动态字符串拼接 | I18N | 扩展f-string/format拼接场景检测 |
| 无自动修复能力 | 全部 | 对可变默认参数等可修复场景提供--fix |

---

## 更新记录

- **2026-07-09**：从 `docs/retrospective/reports/task-reports/retrospective-concurrent-safety-checker-20260708/` 迁移至 `docs/knowledge/best-practices/`，提升可发现性；DEFENSIVE维度新增第④类检测场景（NaN/Inf特殊浮点值泄漏），来源于conflict_resolution.py压力测试中发现的NaN诊断遗漏Bug——`float('nan')`通过isinstance(float)检查但所有比较返回False，可绕过范围校验诊断。详见[负载异常压力测试报告](../../retrospective/reports/task-reports/report-malformed-data-handling-20260709/stress-test-report.md#4-bug发现与修复)。
- **2026-07-08**：初始版本，从并发安全检查器复盘报告原子化拆分而来。
