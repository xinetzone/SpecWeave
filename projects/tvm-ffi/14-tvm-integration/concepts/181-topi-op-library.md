---
type: Concept
title: "视角181：TOPI 算子库"
description: "分析 TOPI 算子库的 FFI 集成：算子实现以 ffi::Object 为对象底盘，通过 refl::GlobalDef 集中登记为全局 packed 函数，支撑编译器查询与运行时绑定。"
tags:
  - topi
  - operator
  - ffi
  - global-def
  - registration
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-355, F-373
  - code:
    - src/topi/nn.cc
    - include/tvm/topi/nn.h
    - include/tvm/ffi/reflection/registry.h
---

# 视角181：TOPI 算子库

## 概述

TOPI（Tensor Operator Inventory）向编译器提供一组用 TVM 表达式（TE）实现的算子原语（dense、bias_add、softmax、卷积等）。它与 FFI 的交汇点在于算子注册方式：`src/topi/nn.cc` 用 `TVM_FFI_STATIC_INIT_BLOCK() + refl::GlobalDef()` 把算子登记为全局 packed 函数，使编译器（Python/C++）能按名查询、按签名调用。

## 核心源码引用

`src/topi/nn.cc` 集中展示注册模式（已验证）：

```cpp
// src/topi/nn.cc
namespace topi {                              // :42
TVM_FFI_STATIC_INIT_BLOCK() {                 // :48
  refl::GlobalDef()
    .def(...);                                // :50
}
TVM_FFI_STATIC_INIT_BLOCK() {                 // :90
  refl::GlobalDef().def_packed("topi.nn.dense", [](ffi::PackedArgs args, ffi::Any* rv) {
    ...
  });                                         // :92
}
TVM_FFI_STATIC_INIT_BLOCK() {                 // :99
  refl::GlobalDef().def_packed("topi.nn.bias_add", [](ffi::PackedArgs args, ffi::Any* rv) { ... });
  // flatten / dilate / layer_norm / group_norm / instance_norm / rms_norm 等同模式
}
}  // namespace topi  :276
```

`def_packed` 显式采用 `(ffi::PackedArgs args, ffi::Any* rv)` 签名（registry.h:556），与 `Function` 的调用约定完全一致（facts F-355）。

## 设计分析

### 零侵入集中注册

TOPI 算子不修改任何主干注册逻辑，只在自身 `.cc` 的静态初始化块里向 `GlobalDef` 登记。多个 `TVM_FFI_STATIC_INIT_BLOCK()`（nn.cc:48/90/99/140/207/227...）各自登记若干算子，语义清晰且加载时一次性完成。

### 编译期查询即函数查找

`refl::GlobalDef().def_packed("topi.nn.dense", ...)`（nn.cc:92）登记的名称即是编译器/上层查询的键。EVG: 只要名称一致，任意后端或替代实现都能通过相同注册点替换算子，体现了 F-141 `Function::SetGlobal`/`ListGlobalNames` 的查找语义。

### packed 签名为性能与通用性权衡

`def_packed` 用原始 `(ffi::PackedArgs, ffi::Any*)` 而非常规 `def`，因为 TOPI 要支持可变参数与标量/张量混合输入；同时该签名正处于 `ffi::Function` 调用热路径，可被同名包装直接消费。

## 扩展讨论

### 注册表与查询的对称性

算子在 `TVM_FFI_STATIC_INIT_BLOCK()` 里经 `refl::GlobalDef().def_packed(name, lambda)` 登记（nn.cc:92），对应侧则由 `Function::GetGlobal(name)` / `tvm_ffi.registry.list_global_func_names()` 按名查询（facts F-141/355）。这一登记与查询的对称性，使 `src/topi/nn.cc` 作为「算子目录」独立于任何具体编译目标，只要名称稳定，替换实现或添加后端都无需改动调用方。

### 为何分散在多个静态初始化块

nn.cc 中密集分布着多个 `TVM_FFI_STATIC_INIT_BLOCK()`（:48/90/99/140/207/227...）。静态初始化块的设计初衷是让每个注册点保持最小、可独立混入源文件；相较集中式的大初始化函数，它降低了单点编译耦合与初始化顺序依赖，也让 `refl::GlobalDef` 的链式调用各自聚焦于一个算子家族。

### 算子作为编译期查询与运行期调用的桥梁

同一个登记名同时服务两端：编译期，编译器按名取算子 lambda 以生成 TE 计算图；运行期（若算子被编译为可执行形态）仍可沿同一名称回落到 `ffi::Function` 调用。`def_packed` 的宽签名使得同一个 `Function` 既能接收编译期元数据，也能承载运行期输入的标量/张量可变参数。

### 扩展算子库的约定

新增 Topi 算子遵循固定三步约定：在 `include/tvm/topi/*.h` 声明函数；在对应 `.cc` 用 `TVM_FFI_STATIC_INIT_BLOCK()` + `refl::GlobalDef().def_packed` 登记；用 `facts F-355` 所述的调用约定编写 lambda。该约定把「实现语言（TE）—登记机制（FFI）—查询入口（GlobalDef）」三件事解耦，是算子库可独立演进的结构基础，亦是 NPU 自定义算子登记（视角 193）可复用的现成范式。

## 相关概念

- [180 目标代码生成注册](180-target-codegen-registration.md)：算子登记的注册表机制
- [182 TE 张量表达式](182-te-tensor-expression.md)：算子的实现语言
- [183 Arith 简化器](183-arith-simplifier.md)：算子推导时的简化支撑