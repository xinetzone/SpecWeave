---
id: perf-trace-instrumentation
title: perf_trace性能埋点集成
type: code
date: 2026-08-01
maturity: L2-validated
source:
  - retrospective-caffe-ffi-p3a (Conv/Pool/BN测试)
  - retrospective-caffe-ffi-p3b-test-milestone-20260731
related_patterns:
  - single-pass-perf-instrumentation
  - cross-language-three-layer-logging
  - ffi-memory-leak-autouse-fixture
tags: [testing, performance, observability, instrumentation, pytest]
validation_count: 2
reuse_count: 0
---

# perf_trace性能埋点集成

## 触发场景

- 当需要在测试中同时采集性能数据和内存数据时
- 当需要定位测试慢在哪个阶段（构建vs前向计算vs初始化）时
- 当需要自动检测内存/Blob泄漏时
- 适用于：pytest测试套件、性能基准测试、FFI原生扩展测试、需要细粒度性能剖析的测试
- 不适用于：纯单元测试（<1ms的简单逻辑测试）、生产代码埋点（用专门的profiler）

## 核心做法

1. **上下文管理器封装**：实现`perf_trace`上下文管理器（pytest fixture传入），用`with ptrace("标签") as t:`包裹关键阶段
2. **三类数据采集**：自动采集Δtime（毫秒）、Δmem（内存变化）、Δblobs（对象数变化）
3. **结构化键值附加**：通过`t["key"] = value`附加自定义维度（如shape、层数、batch size）
4. **[PERF]统一前缀**：所有性能日志以`[PERF]`开头，便于grep/awk过滤
5. **固定字段顺序**：日志字段按固定顺序输出：标签 → Δtime → Δmem → Δblobs → 自定义k=v
6. **autouse泄漏检测**：conftest级autouse fixture自动在测试前后做基线对比，检测跨测试的Blob/内存泄漏
7. **可选静默模式**：正常测试运行时可通过开关关闭PERF日志，需要性能数据时再开启

## 反模式（不要这么做）

- ❌ **反模式1：手动time.time()散落各处**：在测试代码中散落`start = time.time()` / `end = time.time()` / `print(end - start)`。后果：忘记end、异常时漏掉打印、输出格式不统一无法批量分析
- ❌ **反模式2：只测总时间**：只记录整个测试的总耗时，不拆分阶段。后果：知道测试慢但不知道慢在构建Net还是forward计算，无法定位优化点
- ❌ **反模式3：不采集内存/对象数**：只看时间，不看内存变化和对象泄漏。后果：性能优化了但引入内存泄漏无法发现
- ❌ **反模式4：不附加上下文维度**：只输出耗时，不记录当时的shape/batch size/层数等参数。后果："conv耗时100ms"——什么shape？什么kernel size？无法复现和对比
- ❌ **反模式5：异常时不输出**：使用try-finally但except分支忘记打印，或上下文管理器exit方法没处理异常。后果：崩溃前的性能数据丢失，无法定位崩溃前最后一个慢操作

## 检验标准

做完之后怎么知道做对了？
- 标准1：所有关键阶段（Net构建、forward、权重加载）都用`with ptrace()`包裹
- 标准2：每个trace都附加了关键维度参数（shape、层数等）
- 标准3：输出统一以`[PERF]`开头，grep能过滤出所有性能行
- 标准4：异常发生时（测试失败），已进入的trace块仍然能输出已采集的数据
- 标准5：跨测试的内存泄漏检测能自动工作，不需要每个测试手动写断言
- 标准6：日志格式一致：`[PERF] <label>  Δtime=XXms  Δmem=+XX  Δblobs=+X  k=v ...`

## 迁移示例

这个模式还能用在什么其他场景？
- 场景1（CLI工具）：为CLI命令实现`--profile`flag，用上下文管理器包裹关键步骤（加载→解析→处理→输出），自动输出各阶段耗时
- 场景2（CI流水线）：CI脚本中对每个stage（checkout→build→test→deploy）用统一格式打点，构建流水线性能趋势图
- 场景3（HTTP服务中间件）：Web框架中间件包裹请求处理，拆分阶段（路由→认证→业务逻辑→序列化），自动记录每段耗时+内存
- 场景4（数据处理管道）：ETL管道中对每个transform步骤埋点，记录Δtime+Δrows+Δmem，自动发现慢transform
- 场景5（编译器）：编译pass管理器包裹每个pass（解析→优化→代码生成），输出各pass耗时+内存使用，定位编译慢的瓶颈pass
