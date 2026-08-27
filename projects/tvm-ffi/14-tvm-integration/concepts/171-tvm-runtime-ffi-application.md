---
type: Concept
title: "视角171：TVM 运行时 FFI 应用"
description: "分析 TVM 运行时如何全面依赖 TVM FFI C API，通过 pack_args.h 将 ffi::PackedArgs 适配为多种设备函数调用约定，实现类型擦除与跨后端参数打包统一。"
tags:
  - tvm-runtime
  - ffi
  - packed-args
  - pack-args
  - type-erasure
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-354, F-361, F-362, F-363, F-364, F-365, F-366, F-367, F-368, F-374
  - code:
    - include/tvm/runtime/base.h
    - src/runtime/pack_args.h
    - include/tvm/ffi/extra/module.h
---

# 视角171：TVM 运行时 FFI 应用

## 概述

TVM 运行时是 FFI 的首要消费者。`include/tvm/runtime/base.h` 开篇明确注释 "TVM runtime fully relies on TVM FFI C API / we will avoid defining extra C APIs here"（base.h:27-29），并直接 `#include <tvm/ffi/c_api.h>`。这意味着运行时的一切跨边界调用、模块加载、张量交互都建立在 FFI 的 C ABI 之上，而非自造一套运行时接口。本案围绕运行时最核心的 `src/runtime/pack_args.h`，剖析 FFI 类型擦除参数在设备函数调用中的适配机制。

## 核心源码引用

`pack_args.h` 提供三种把 `ffi::PackedArgs`（参数序列的只读视图）转换为设备调用约定的工具函数，均返回 `ffi::Function`：

- `PackFuncVoidAddr(F f, const ffi::Array<DLDataType>& arg_types, ...)`（pack_args.h:75）：把参数按地址打包，适配 `cuda_style(void** args, int num_args)` 约定。
- `PackFuncNonBufferArg(F f, const ffi::Array<DLDataType>& arg_types)`（pack_args.h:87）：仅打包非缓冲参数，适配 `union_64bit args[N]`。
- `PackFuncPackedArgAligned(F f, const ffi::Array<DLDataType>& arg_types)`（pack_args.h:101）：按 C 结构体字段对齐规则填充，确保内联结构体字段对齐。

三种函数内部依赖两个 `union` 与一个转换码枚举，用于在类型擦除后还原具类型数据：

```cpp
// src/runtime/pack_args.h:47-63
union ArgUnion32 {
  int32_t v_int32;
  uint32_t v_uint32;
  float v_float32;
};
union ArgUnion64 {
  int64_t v_int64;
  uint64_t v_uint64;
  double v_float64;
  int64_t v_int32[2];  // 等宽拆分为 2 个 32 位
};
```

`ArgConvertCode` 枚举（pack_args.h:131-139）列出八种转换：`INT64_TO_INT64`、`INT64_TO_INT32`、`INT64_TO_UINT32`、`FLOAT64_TO_FLOAT32`、`FLOAT64_TO_FLOAT64`、`HANDLE_TO_HANDLE`、`HANDLE_TO_TENSORMAP`。`GetArgConvertCode(DLDataType)`（pack_args.h:141）依据 `DLDataType` 的 code/bits 返回对应转换码。

## 设计分析

### 统一源：ffi::PackedArgs

`PackFuncVoidAddr_`（pack_args.h:159）把 `ffi::PackedArgs args` 当作唯一事实来源，通过 `reinterpret_cast<const TVMFFIAny*>(args.data())` 拿到底层 `TVMFFIAny` 数组，再按转换码逐槽位读取。这正是 FFI 类型擦除的价值：无论调用方传的是 int、float 还是句柄，运行时都以统一的 16 字节 `TVMFFIAny` 承载，再按目标设备的需要显式还原。

### 小数组内联优化

`detail::TempArray<T, kSize>`（pack_args.h:111-128）对参数数量 `<=4` 或 `<=8` 使用栈上定长数组，避免堆分配；超过则退化为 `std::vector`。外层 `PackFuncVoidAddr`（pack_args.h:311）通过 `num_void_args` 分派到 `PackFuncVoidAddr_<4/8/0>` 三个特化，把「零分配、低延迟」作为设备函数调用的默认路径。

### 对齐修正

`PackFuncPackedArgAligned_`（pack_args.h:247）在把参数写入 `int32_t pack[]` 缓冲区前调用 `ensure_alignment_to_multiple_of_i32(factor)`，保证 `void*`（对齐至 `sizeof(void*)/sizeof(int32_t)`）与 64 位标量（factor 2）正确落到 C 结构体语义的对齐位置，规避打包后字段错位。

## 扩展讨论

### "依赖 FFI，不自造 C API"是一条架构纪律而非偶然

`base.h` 注释的 "TVM runtime fully relies on TVM FFI C API / avoid defining extra C APIs" 不只是设计取舍，而是一条**必须时刻守住的边界**：任何新加入的运行时能力若越过该行、追加自有 C ABI，都会制造「第二套接口」——与 FFI 分叉、与语言绑定分叉、增加跨库符号梳理负担。把这句话写进头文件注释，等于把"唯一 C ABI 源"变成可审阅的代码事实，任何变更 diff 都会在此显形，从而从源头预防接口漂移。

### ArgUnion 双宽联合体：一次布局服务两代传参约定

`ArgUnion32`（int32/uint32/float）与 `ArgUnion64`（int64/uint64/double/两个 int32）分别对齐 32 位与 64 位传参槽位，加上 `v_int32[2]` 提供"宽标量等宽拆分为两个窄槽"的灵活性。这允许 `GetArgConvertCode` 依据 `DLDataType` 的 code/bits 自由选取：32/64 位浮点、整型、句柄、tensor map 都落在少数几种还原路径里，避免为每种类型手写参数解包。联合体把"类型擦除后再还原"的性能成本压到一次读取，正是 FFI 类型系统在设备调用边界被高效复用的微观体现。

### TempArray 的 "N<=4/8 栈内、超出退化 vector"：零分配优先

`TempArray<T, kSize>` 把参数打包区分为"小参数走栈上定长数组、大参数退化为 `std::vector`"，再由 `PackFuncVoidAddr` 按 `num_void_args` 分派到 `<4/8/0>` 特化。这保证了设备函数调用这一热路径在常见参数规模下**零堆分配**，只有当参数真的很多时才付出 vector 的代价。它是"默认快、极端正确"的通用策略：把性能乐观假设置于最常见路径，同时用退化分支兜住正确性，避免为极少数超大调用牺牲全部小调用的延迟。

## NPU 建议

1. NPU 设备函数的入参应复用 `PackFuncPackedArgAligned` 的「按 C 结构对齐」打包路径，保证 NPU 端可直接把打包缓冲视为结构体读取，避免二次解析。
2. 为 NPU 增加专用 `ArgConvertCode`（如 `HANDLE_TO_TILE`），在 `GetArgConvertCode` 中按 NPU 特有的 tile descriptor 类型分发，使打包层能显式处理 NPU 张量描述符。
3. 建议基于 `TempArray` 特化机制为 NPU 高频算子提供 `N<=4` 栈上零分配打包，压缩驱动调用延迟。
4. NPU 应遵循 base.h 的 "rely on FFI C API only" 约束，`npu_runtime.h` 只通过 `tvm/ffi/c_api.h` 对外暴露，保持运行时与编译器两侧符号解耦。

## 相关概念

- [175 Module 系统集成](175-module-system-integration.md)：FFI Module 承载运行时可加载对象
- [177 虚拟机 VM](177-virtual-machine-vm.md)：`VirtualMachine` 继承 `ffi::ModuleObj`
- [180 目标代码生成注册](180-target-codegen-registration.md)：全局函数注册表的建立