---
type: Concept
title: "视角195：NPU 错误处理策略"
description: "为 NPU 运行时设计错误处理策略：按错误类型分类、通过 TLS 状态传播、保留错误因果链，并针对异步设备错误给出可测的上报与集中同步方案。"
tags:
  - npu
  - error-handling
  - tls
  - error-kind
  - error-chain
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-028, F-029, F-030, F-031, F-032
  - code:
    - include/tvm/ffi/error.h
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
---

# 视角195：NPU 错误处理策略

## 概述

NPU 的错误来源分散：设备驱动返回错误码、内核执行异步失败、参数校验提前失败。设计良好的错误策略是把这些不同来源的错误统一到 TVM FFI 的错误模型上：用 `Error` 类表达、按 `ErrorKind` 分类（视角078）、经线程本地状态（TLS）传播（视角083、046）、用 cause chain 保留因果（视角081）。本视角给出 NPU 侧的分类、传播与同步策略。

## 错误分类

`error.h` 定义 `ErrorKind` 枚举，用于区分错误的性质。NPU 应将设备错误映射到恰当种类：

- 参数校验错误 → 对应校验类错误，立即在调用栈内抛出。
- 驱动/硬件错误 → 对应运行时类错误，携带设备返回码。
- 未找到内核/符号 → 对应查找类错误，指示调度配置问题。

分类价值在于：上层能依据种类决定"可重试、可回退到 CPU、必须终止"等处理策略。

## 传播：TLS 错误状态

C ABI 提供线程本地错误状态入口：`TVMFFIErrorCreate(:809)` 构造错误、`TVMFFIErrorSetRaised(:760)` 挂载到当前线程、`TVMFFIErrorMoveFromRaised(:754)` 取走错误、`TVMFFIErrorSetRaisedFromCStr(:768)` 从 C 字符串挂载。NPU 的错误在上抛时不应跨线程裸传递，而应遵循 safe_call 契约（视角038）——在调用线程内设错并抛异常，由 `safe_call` 统一捕获、包装、重新抛出。

## 因果链与上下文

复杂失败（如"内核启动失败 ← 显存不足"）建议保留 cause chain（视角081），通过追加 extra context（视角082）把设备错误码、内核名、设备 ID 逐层附上，使顶层诊断信息完整。`TVMFFIBacktrace(:1464)` 可用于失败时抓取调用栈，辅助定位。

## 异步援助：错误的上报时机

异步命令（视角191）的失败不在入队时发生。策略是：入队时只做参数校验的同步报错；设备异步错误通过查询同步原语或以错误挂载线程的方式在用户显式同步（如 `npu.stream_synchronize`）时一次性集中上报，避免"错误静默流失"。

## 设计分析

1. **分类治理决策、TLS 治理传播、链治理可诊断**：三者各司其职，组成完整错误闭环。
2. **异步错误必须显式汇合**：否则失败既不可测也不可定位，是 NPU 后端最易出问题的点。
3. **统一走错误模型胜于各自为政**：让 Python/C++/Rust 侧享受同一套错误语义与堆栈信息。

## NPU建议

1. 建立 NPU 错误码→`ErrorKind` 的映射表，把设备返回码归一为 FFI 错误种类，杜绝裸返回码泄漏到上层。

2. 错误产生时用 `Error::Raise`/相应抛出宏构造并携带设备上下文（设备 ID、内核名、驱动码），保持 cause chain 完整。

3. 在调用线程内通过 `TVMFFIErrorSetRaised` 挂载错误，配合 `safe_call` 的统一捕获，保证任意语言绑定都能拿到一致的异常。

4. 对异步内核失败，提供 `npu.stream_synchronize`/独立错误查询原语，在用户显式同步点集中上报设备错误，同时支持 `Event` 查询实现轻量轮询。

5. 失败诊断时用 `TVMFFIBacktrace` 抓取栈，把回溯附入错误对象，方便开发者离线复现。

6. 为常见错误提供错误码文档与 FAQ 化描述，通过元数据（或错误 extra_context）携带可读的修复建议字符串。

## 相关概念

- [197 NPU 性能分析追踪](197-npu-profiling-tracing.md)：失败栈回溯与观测
- [076 ErrorObj 对象设计](/06-error-handling/concepts/076-error-obj-design.md)
- [078 ErrorKind 错误类型分类](/06-error-handling/concepts/078-error-kind-classification.md)
- [083 TLS 错误状态](/06-error-handling/concepts/083-tls-error-state.md)
- [191 NPU 命令队列](191-npu-command-queue.md)