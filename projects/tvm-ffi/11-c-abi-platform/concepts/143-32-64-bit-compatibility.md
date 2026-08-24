---
type: Concept
title: "视角143：32/64 位兼容性"
description: "分析 TVM FFI 如何在使用固定宽度整数类型、定长联合体与编译期断言的前提下，实现 32 位与 64 位平台上的二进制兼容。"
tags:
  - 32-bit
  - 64-bit
  - compatibility
  - bit-width
  - cross-platform
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-014, F-015
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/memory.h
    - include/tvm/ffi/container/shape.h
---

# 视角143：32/64 位兼容性

## 概述

32 位与 64 位平台在指针宽度上存在本质差异（4 字节 vs 8 字节），是 FFI 二进制兼容最大的威胁之一。TVM FFI 通过"固定宽度基础类型 + 尺寸与指针解耦的联合体 + 编译期尺寸断言"三管齐下，让绝大多数接口在两种位宽下保持相同布局，从而允许同一份头文件服务两种架构。

## 定宽基础类型

`TVMFFIObject`（`c_api.h:241-287`）与 `TVMFFIAny`（`c_api.h:297-342`）的字段几乎全部使用定宽整数：`int32_t`、`uint32_t`、`uint64_t`。组合引用计数用 `uint64_t`（`c_api.h:261`），它与指针宽度无关，因此两平台头部字节大小与对齐一致。类型索引使用 `int32_t`（`c_api.h:266`、`c_api.h:302`），即使对象数量增长到上百个也足够用更大的动态区间，但索引本身始终 4 字节。

## TVMFFIAny 联合体的稳态尺寸

`TVMFFIAny` 的 8 字节联合体（`c_api.h:319-341`）包含指针成员 `v_ptr`、`v_c_str`、`v_obj`（在 32 位为 4 字节、64 位为 8 字节），但联合体尺寸由最大成员决定——`v_int64`/`v_uint64`/`v_float64`/`v_bytes[8]` 恒为 8 字节。因此联合体在两种位宽下都稳定为 8 字节，加上 4 字节 `type_index` 与 4 字节填充，`TVMFFIAny` 总为 16 字节，与指针宽度无关。

这意味着：以 `TVMFFIAny` 构成的参数数组、返回值缓冲区在 32 位与 64 位下有相同的字节步长与偏移，绑定层可以共享同一套打包代码。

## 不透明句柄的抽象

`TVMFFIObjectHandle` 定义为 `void*`（`c_api.h:205`）。虽然指针本身在不同位宽下尺寸不同，但契约只在"句柄是合法的指针"这一层面成立，调用方从不假定其位宽，因而句柄是位宽无关的抽象边界。对象的头部布局（`TVMFFIObject`）不因指针宽度变化而改变，唯一的尺寸变化发生在堆对象内里存放指针的成员上，这属于类型内部实现，不影响稳定接口。

## 编译期尺寸断言

源码用 `static_assert` 固化与位宽相关的关键尺寸关系，例如：

- `shape.h:138-139`：`alignof(ShapeObj) % alignof(int64_t) == 0` 及 `sizeof(ShapeObj) % alignof(int64_t) == 0`；
- `map_base.h:1307`：容器对齐与元素对齐的整除关系。

这些断言在编译期即拦截"某平台元素对齐与容器不整除"的布局隐患，从而保证内联数组在 32/64 位下行为一致。

## 内存分配的位宽差异

`AlignedAlloc`（`memory.h:56-78`）中，对齐不超过 `std::max_align_t` 时走 `std::malloc`，更大时才走 `posix_memalign`。`std::max_align_t` 的对齐上限随平台（long double、SIMD 类型）而不同，但函数在逻辑上以"所需对齐 vs 平台默认对齐"为判据，因而可移植。

## 设计分析

32/64 位兼容的关键洞察是：把"指针宽度"与"布局尺寸"解耦。定宽整数保证数值字段尺寸稳定；联合体以定宽成员锚定尺寸；指针成员被吞并进联合体而不再独立放大整体；不透明句柄则把指针宽度隔离在抽象边界之后。配合编译期断言，TVM FFI 得以用一套头文件与绑定逻辑同时服务两种位宽，显著降低多架构分发的二进制复杂度。

## 相关概念

- [141 C ABI 稳定性保证](141-c-abi-stability-guarantee.md)：布局冻结的总体原则
- [142 结构体打包与对齐](142-struct-packing-alignment.md)：联合体与对齐的细节
- [147 Emscripten/WASM](147-emscripten-wasm-support.md)：WASM32/64 作为特殊位宽场景
- [108 静态断言](/08-cpp-impl/concepts/108-static-assert.md)：编译期约束机制