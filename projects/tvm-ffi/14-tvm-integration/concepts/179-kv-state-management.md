---
type: Concept
title: "视角179：KV State 管理（NPU 建议）"
description: "分析 VM 中注意力 KV 缓存与 RNN 状态如何继承 ffi::Object，以 ffi::Shape/ffi::Optional/Tensor 为参数类型暴露 Clear/AddSequence/Attention 等管理接口。"
tags:
  - kv-cache
  - attention
  - ffi
  - relax-vm
  - memory-management
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-045, F-046, F-174
  - code:
    - src/runtime/vm/kv_state.h
    - src/runtime/vm/paged_kv_cache.cc
    - include/tvm/runtime/device_api.h
---

# 视角179：KV State 管理（NPU 建议）

## 概述

KV State 是长上下文推理的缓存抽象，涵盖注意力 K/V 缓存与 RNN 隐状态两类可变状态。`src/runtime/vm/kv_state.h` 将 `KVStateObj` 定义为 `ffi::Object`（:34），用 `ffi::Shape`、`ffi::Optional`、`Tensor` 等 FFI 容器作为参数类型，使其能跨语言安全调用且可被 VM 持有。

## 核心源码引用

`src/runtime/vm/kv_state.h`（已验证）：

- `class KVStateObj : public ffi::Object`（:34）：`Clear()`（:37）、`AddSequence(int64_t)`（:47）、`RemoveSequence`（:54）、`ForkSequence`（:68）、`PopN`（:77）、`BeginForward(...)`（:97）、`EndForward()`（:106）；
- `class KVState : public ffi::ObjectRef`（:112）；`_type_mutable = true`（:108）标志可变对象；
- `class AttentionKVCacheObj : public KVStateObj`（:121）：`Empty()`、`GetNumAvailablePages()`、`AttentionWithFusedQKV(Tensor qkv, ...)`（:182）、`SelfAttention`（:195）、`AppendMLAKV`（:229）、`AttentionWithSharedKV`（:221）等细粒度注意力 API；
- `class RNNStateObj : public KVStateObj`（:325）：`Get`/`Set`/`DebugGet`（:336-353）。

`BeginForward` 的参数 `const ffi::Shape& seq_ids, const ffi::Shape& append_lengths` 与 `ffi::Optional<ffi::Shape>` 表明状态管理以 FFI 形状/可选容器作为序列元数据载体（facts F-045/046 的容器 C API 在此落地为 `ffi::Shape`/`ffi::Optional`）。

## 设计分析

### 可变状态的一等对象

`KVStateObj` 标记 `_type_mutable = true`（:108）并以 `ffi::Object` 为基，使其能通过引用计数在所有持有者间共享，同时明确「可变」语义，存取都走显式方法而非值拷贝。

### 以 FFI 容器表述序列元数据

序列 id 与增量长度以 `ffi::Shape`（不可变 `int64_t` 数组）传入 `BeginForward`（:97-99），掩码等可选参用 `ffi::Optional`，张量数据用 `Tensor`。全链路类型都落在 FFI 类型系统内，Python 驱动长上下文加载时无需额外转换。

### 前后向契约定界

`BeginForward`/`EndForward`（:97-106）界定一次模型前向执行：进入时下发辅助 KV 结构到内存（可下放到 GPU/NPU），退出时回收。这与 VM 的 `Call` 插桩（视角 177/178）呼应，构成记忆状态与执行流的时序契约。

### 分页与树编辑

`GetNumAvailablePages`（:133）与 `CommitAcceptedTokenTreeNodes`（:158）、`ForkSequence`（:68）共同支撑分页缓存、并行采样与投机解码的 KV 编辑，为高吞吐推理兜底。

## 扩展讨论

### 可变状态做成一等 FFI 对象而非普通数据类

`KVStateObj : public ffi::Object` 且标记 `_type_mutable = true`，意味着 KV 缓存被视为**可被引用计数共享的可变对象**，而非一次性值。这带来两个实际收益：其一，长上下文推理中同一份缓存可被多个执行者按需共享，释放与回收交给引用计数；其二，它以 `ffi::Object` 身份可被 VM 持有、被反射登记、被跨语言传递，Python 侧能以统一对象模型操作底层状态，而不是走一套旁路的非 FFI 数据接口。

### 全 FFI 类型描述序列元数据：零转换的跨语言边界

`BeginForward` 的 `seq_ids`/`append_lengths` 用 `ffi::Shape`、掩码用 `ffi::Optional`、数据用 `Tensor`——所有入参都落在 FFI 类型系统内。当 Python 驱动长上下文加载时，这些参数可被 `ffi::Function` 直接打包传输，无需在 Python 对象与 C++ 容器间做手写逐字段转换。它体现了 KV State 作为"运行时可调对象"的基调：接口天然可被 `ffi::PackedArgs` 承载，从而被 VM、RPC、Python 绑定统一调用。

### 分页与树编辑支撑的推理形态演进

`GetNumAvailablePages` 揭示底层采用分页式页表缓存；`CommitAcceptedTokenTreeNodes`、`ForkSequence` 则面向投机解码与并行采样——前者要在同一前缀上维护多条候选分支的树结构，后者让多个序列共享一部分 K/V。这些方法把"长上下文 / 高吞吐推理"的高级形态（分页、树、并行）作为一等 API 暴露，而非退回整段拷贝的朴素缓存，正是为满足现代 LLM 服务端吞吐需求而设计的。

## NPU 建议

1. 为 NPU 实现 `AttentionKVCache` 子类，将 `AttentionWithFusedQKV`/`SelfAttention` 映射到 NPU 分页自注意力内核，页表常驻 NPU 以消除每次前向的页管理通信。
2. 让 `BeginForward` 直接向 NPU 下发页表与序列映射（`ffi::Shape`），`EndForward` 回收，避免主机-GPU 往返；数据布局用 `AttentionWithFusedQKV(total_length,...)` 约定以贴合 NPU 内核。
3. 用 MLA 专用 `AppendMLAKV`（:229）与 `AttentionWithSharedKV`（:221）对接 NPU 的权重共享/张量化 K/V，降低显存带宽占用。
4. 借助 `KVStateObj::_type_mutable` 与反射登记，把 NPU KV 缓存暴露为可调用的 `ffi::Function`，便于在 Python 中直接操作并做整段缓存诊断。

## 相关概念

- [177 虚拟机 VM](177-virtual-machine-vm.md)：状态对象的宿主
- [178 字节码执行](178-bytecode-execution.md)：State 前向与 VM Call 的时序对齐
- [185 Instrument 性能分析](185-instrument-performance-analysis.md)：缓存命中与预取耗时侧量