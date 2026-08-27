---
type: Concept
title: "视角197：NPU 性能分析追踪"
description: "为 NPU 运行时设计性能分析与追踪能力，围绕模块元数据/文档、源码回看、内核级计时的挂点，以及失败诊断时的栈回溯，给出可观测的集成建议。"
tags:
  - npu
  - profiling
  - tracing
  - introspection
  - backtrace
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-063, F-295, F-296
  - code:
    - include/tvm/ffi/extra/module.h
    - include/tvm/ffi/c_api.h
    - ../../tvm/src/backend/cuda/runtime/cuda_module.cc
---

# 视角197：NPU 性能分析追踪

## 概述

NPU 性能问题（内核耗时、显存占用、队列阻塞）难以黑盒定位，必须依赖可观测的设计。TVM FFI 并非分析器本身，但提供了若干"可观测挂点"：模块元数据与文档字符串（`GetFunctionMetadata`/`GetFunctionDoc`）、源码回看（`InspectSource`）、回溯捕获（`TVMFFIBacktrace`）。本视角说明如何在 NPU 后端嵌入这些挂点并暴露计时/统计能力。

## 模块级自省作为分析入口

`module.h` 定义三个自省入口，是分析工具的天然数据源：

- `GetFunctionMetadata(name)`（`module.h:101`）：返回函数的 JSON 元数据（如签名 `type_schema`）。
- `GetFunctionDoc(name)`（`module.h:81`）：返回函数的文档字符串。
- `InspectSource(format)`（`module.h:131`）：返回模块源码（若有）。

分析工具可通过这些入口识别"这个 NPU 模块里有哪些内核、各自签名与说明"，从而枚举与标注待分析对象。

## 内核级计时的挂点

内核级耗时统计需要在调度路径上嵌入计时点。建议把计时作为全局函数暴露，例如在 `npu.kernel_enqueue` 返回的事件上附加时间戳，或提供 `npu.profile_start`/`npu.profile_stop` 包裹一段执行。计时结果可叠加在模块元数据的 `type_schema` 之外的扩展字段上，避免污染核心元数据。

## 回溯捕获与失败诊断

性能与正确性判断常需调用栈。`TVMFFIBacktrace(:1464)` 可抓取当前线程的栈回溯，配合视角195在错误对象中附加回溯，让分析器既能看"哪里慢"也能看"哪里出错"。回溯输出应遵循平台无关约定，便于跨语言绑定统一解析。

## 追踪数据的出口

分析数据需要统一出口，建议：

- 内核耗时/启动参数通过全局函数按需读取（如 `npu.profiling.snapshot`）。
- 总量与峰值内存已由 `npu.memory_info`（视角192）覆盖。
- 细粒度的硬件计数器（cycles、cache miss）由设备驱动提供，运行时透传原始值并保留来源标签。

保持"运行时收集 + 外界读取"的解耦，分析器不侵入调度核心。

## 设计分析

1. **自省与性能收集分离**：元数据是静态描述，性能数据是动态观测，二者分开实现、配合消费。
2. **计时挂点轻量、按需开启**：默认关闭可避免性能分析本身拖慢执行，需要时才打开。
3. **回溯与错误联动**：把性能和正确性诊断统一到同一出事现场，提高复现效率。

## NPU建议

1. 为 NPU 模块实现并填充 `GetFunctionMetadata`/`GetFunctionDoc`，使每个内核从装载起即可被分析器枚举与识别。

2. 若内核为源码态，实现 `InspectSource` 回看源码，与已保存的编译信息对照，方便性能归因。

3. 提供 `npu.profile_start`/`npu.profile_stop` 与事件级时间戳，按需开关计时，避免常开开销。

4. 在错误对象中附加 `TVMFFIBacktrace` 捕获的栈，与内核计时、设备计数集成一个诊断快照。

5. 透传设备硬件计数器（cycles、SM 占用、内存吞吐）并带上来源标签，供高级分析使用。

6. 通过 `npu.profiling.snapshot` 之类全局函数统一导出当前会话的分析数据，保持收集与消费解耦。

## 相关概念

- [195 NPU 错误处理策略](195-npu-error-handling-strategy.md)：回溯与诊断联动
- [188 NPU 内核库发布](188-npu-kernel-library-publishing.md)：元数据与文档
- [192 NPU 内存管理](192-npu-memory-management.md)：内存统计入口
- [079 TVMFFIBacktrace 栈回溯捕获](/06-error-handling/concepts/079-backtrace-capture.md)